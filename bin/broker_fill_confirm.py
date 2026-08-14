"""broker_fill_confirm.py — LEG THỨ 3 của đối soát fill: statement DNSE tự phát hành.

Bối cảnh (coding_guidelines §27 + skill dnse-fill-reconciliation): "lệnh đã ĐẶT" ≠ "lệnh đã KHỚP".
`eod_trading_report.sh` đã có 2 leg đối soát — `state.json` (nội bộ bot) và `dnse_raw_*.jsonl`
(API client của mình). CẢ HAI đều do tiến trình bot của mình ghi ⇒ một bug hệ thống (bot chết
giữa chừng, sync sai, lệnh đặt tay ngoài app) làm SAI CẢ HAI CÙNG LÚC mà không leg nào phát hiện
được. File này thêm leg thứ 3 đi qua đường dữ liệu HOÀN TOÀN KHÁC: email "Báo cáo giao dịch khớp
lệnh" do backend DNSE tự phát hành ~16:30 ICT mỗi phiên.

Nguồn: kb/data_registry/trading-bot/dnse_khoplenh_broker_email.md (CANONICAL cho fill THẬT).
Writer CSV: fetch_dnse_khoplenh_email.py (WorkingClaude root).

KHÔNG thay thế pipeline §6 (verify_account_snapshot.py → daily_nav_snapshot.py →
reconcile_equity.py) — đây là lớp đối soát ĐỘC LẬP, chỉ đọc, chỉ cảnh báo.

Ba việc leg này làm mà 2 leg cũ KHÔNG làm được:
  1. Bắt fill trên mã NGOÀI kế hoạch. Leg `dnse_raw` lọc `sym not in plan_tickers` ⇒ lệnh đặt tay
     trong app DNSE, hoặc lệnh sót từ phiên trước, là VÔ HÌNH với cả 2 leg cũ.
  2. Xác nhận độc lập khi bot chết trước khi ghi state (case 3 của eod report: "có plan, không có
     state" hiện KHÔNG biết thực tế đã khớp gì chưa).
  3. Phí/thuế THẬT theo từng dòng khớp (phí trả sở + phí DNSE + thuế), thay vì ước lượng.

Fail-safe (bắt buộc — báo cáo client-facing không được crash vì 1 email chưa tới):
  - CSV thiếu → thử fetch 1 lần (nếu allow_fetch) → vẫn thiếu ⇒ available=False + reason,
    KHÔNG raise. Trước ~16:30 ICT email chưa tồn tại là chuyện BÌNH THƯỜNG.
  - File có dòng nhưng account_no của mình không xuất hiện ⇒ available=False (nghi ánh xạ
    tiểu khoản sai), KHÔNG kết luận "broker báo 0 fill". Báo nhầm 0 fill khi thật ra đang map sai
    tiểu khoản sẽ sinh cảnh báo giả toàn tập — fail-closed đúng tinh thần §25.
"""
import os
import subprocess
from datetime import datetime

# MUA/BÁN (broker) → buy/sell (nội bộ). Bọc cả biến thể không dấu phòng khi encoding đổi.
_SIDE_MAP = {"MUA": "buy", "BÁN": "sell", "BAN": "sell"}


def _norm_acct(x):
    """Chuẩn hoá số tiểu khoản để so sánh.

    BẪY THẬT (đo 2026-08-11): CSV giữ đúng '0002023347' trong text, nhưng `pd.read_csv` KHÔNG có
    `dtype=str` sẽ parse thành int 2023347 — mất số 0 dẫn đầu ⇒ so sánh chuỗi với `account_id`
    ('0002023347' trong secrets/trading_bot_accounts.json) LUÔN sai, và cái sai đó im lặng: mọi
    account trông như "broker báo 0 fill". Đọc bằng dtype=str VÀ so sánh qua hàm này (bỏ số 0 dẫn
    đầu cả hai phía) để không phụ thuộc vào việc ai đó nhớ truyền dtype.
    """
    s = str(x).strip()
    if s.endswith(".0"):          # phòng trường hợp đã lỡ bị parse thành float
        s = s[:-2]
    return s.lstrip("0") or "0"


def broker_csv_path(wc_root, date_iso):
    """date_iso 'YYYY-MM-DD' → path CSV (tên file dùng DD-MM-YYYY, theo writer)."""
    d = datetime.strptime(date_iso, "%Y-%m-%d").strftime("%d-%m-%Y")
    return os.path.join(wc_root, "data", "execution_logs",
                        f"dnse_khoplenh_broker_confirm_{d}.csv")


def _all_accounts(wc_root):
    """[(label, account_no)] cho mọi account khai trong secrets (bỏ entry không có số)."""
    import json
    path = os.path.join(wc_root, "secrets", "trading_bot_accounts.json")
    try:
        with open(path, encoding="utf-8") as f:
            accts = json.load(f).get("accounts", [])
    except Exception:
        return []
    items = accts.items() if isinstance(accts, dict) else [(a.get("label"), a) for a in accts]
    out = []
    for label, entry in items:
        no = (entry or {}).get("account_id") or (entry or {}).get("account_no")
        if label and no:
            out.append((label, str(no)))
    return out


def account_no_for(wc_root, account):
    """label ('SpaceX') → số tiểu khoản ('0002023347'), hoặc None."""
    return next((no for label, no in _all_accounts(wc_root) if label == account), None)


def _try_fetch(wc_root, date_iso, timeout):
    """Chạy fetch_dnse_khoplenh_email.py 1 lần. True nếu CSV tồn tại sau đó.

    Idempotent (§5): script ghi đè đúng 1 path theo ngày, chạy lại không tạo bản trùng.
    """
    d = datetime.strptime(date_iso, "%Y-%m-%d").strftime("%d/%m/%Y")
    try:
        subprocess.run(
            ["python3", "fetch_dnse_khoplenh_email.py", "--date", d],
            cwd=wc_root, timeout=timeout,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
        )
    except Exception:
        return False
    return os.path.exists(broker_csv_path(wc_root, date_iso))


class BrokerFills:
    """Kết quả đọc statement cho MỘT account. Luôn kiểm `available` trước khi dùng `by_key`."""

    def __init__(self, available, reason="", path="", by_key=None, fees=0.0, tax=0.0, value=0.0):
        self.available = available
        self.reason = reason
        self.path = path
        self.by_key = by_key or {}      # (ticker, side) -> {'qty','value','fee','tax'}
        self.fees = fees                # phí trả sở + phí DNSE, VND
        self.tax = tax
        self.value = value              # tổng giá trị khớp, VND

    def qty(self, ticker, side):
        return self.by_key.get((ticker, side), {}).get("qty", 0)

    @property
    def tickers(self):
        return {k[0] for k in self.by_key}


def load_broker_fills(date_iso, account, wc_root, allow_fetch=True, fetch_timeout=120):
    """Đọc fill THẬT của `account` trong ngày `date_iso` từ statement DNSE.

    Không bao giờ raise — mọi lỗi trả về BrokerFills(available=False, reason=...).
    """
    path = broker_csv_path(wc_root, date_iso)
    if not os.path.exists(path) and allow_fetch:
        _try_fetch(wc_root, date_iso, fetch_timeout)
    if not os.path.exists(path):
        # DNSE CHỈ gửi email vào phiên CÓ khớp (verify 2026-08-11: 04/05/06-08 không có email,
        # đúng những ngày khớp 0). Nên "không có statement" có 2 nghĩa — chưa tới giờ, HOẶC hôm
        # nay không khớp gì và email sẽ KHÔNG BAO GIỜ tới. Không phân biệt được từ Gmail ⇒ nói
        # đúng cả hai khả năng, đừng để người đọc tưởng là sự cố.
        return BrokerFills(False, "không có statement — hoặc email chưa gửi (DNSE gửi ~16:30 ICT), "
                                  "hoặc phiên nay khớp 0 (ngày không khớp gì DNSE không gửi email)", path)

    acct_no = account_no_for(wc_root, account)
    if not acct_no:
        return BrokerFills(False, f"không tra được số tiểu khoản cho account '{account}'", path)

    try:
        import pandas as pd
        # dtype=str cho tieu_khoan/ma: xem _norm_acct — mất số 0 dẫn đầu là lỗi IM LẶNG.
        df = pd.read_csv(path, dtype={"tieu_khoan": str, "ma": str})
    except Exception as e:
        return BrokerFills(False, f"không đọc được CSV ({type(e).__name__})", path)

    needed = {"tieu_khoan", "ma", "loai_lenh", "khoi_luong", "gia_tri_khop"}
    if not needed.issubset(df.columns):
        return BrokerFills(False, f"CSV thiếu cột {sorted(needed - set(df.columns))} — layout đổi?", path)

    df = df[df["ma"].notna()].copy()
    if df.empty:
        return BrokerFills(False, "CSV rỗng (không có dòng khớp nào trong ngày)", path)

    df["_acct"] = df["tieu_khoan"].map(_norm_acct)
    target = _norm_acct(acct_no)
    in_file = set(df["_acct"])
    # Tiểu khoản của mình KHÔNG có dòng nào. Hai nguyên nhân KHÁC HẲN nhau, phải tách:
    #   (a) hôm nay account này khớp 0 — sự thật hợp lệ (ca THẬT: ZaloPay 2026-08-07, plan bị
    #       gate P0 chặn sạch 0/9 lệnh nên không có gì để khớp);
    #   (b) ánh xạ tiểu khoản hỏng (đổi số, mất số 0 dẫn đầu, layout đổi) — báo "0 fill" lúc này
    #       sẽ sinh cảnh báo giả cho MỌI mã trong plan.
    # Phân biệt được bằng bằng chứng trong CHÍNH file: nếu một account KHÁC mà mình biết số lại
    # xuất hiện, thì cơ chế ánh xạ đang chạy đúng ⇒ vắng mặt là (a). Không có account nào khớp
    # ⇒ không có bằng chứng nào ⇒ fail-closed (§25), báo không đối soát được.
    if target not in in_file:
        known = {_norm_acct(no) for _, no in _all_accounts(wc_root)}
        if known & in_file:
            return BrokerFills(True, "", path, {})     # (a) khớp 0 thật, đã có bằng chứng
        return BrokerFills(                            # (b) nghi ánh xạ sai
            False,
            f"tiểu khoản {acct_no} không xuất hiện trong statement, và KHÔNG account nào mình "
            f"biết xuất hiện (file có {sorted(in_file)}) — nghi ánh xạ sai, không kết luận 0 fill",
            path,
        )

    mine = df[df["_acct"] == target]
    by_key = {}
    for _, r in mine.iterrows():
        side = _SIDE_MAP.get(str(r["loai_lenh"]).strip().upper())
        if side is None:
            continue
        key = (str(r["ma"]).strip().upper(), side)
        agg = by_key.setdefault(key, {"qty": 0, "value": 0.0, "fee": 0.0, "tax": 0.0})
        agg["qty"] += int(r["khoi_luong"] or 0)
        agg["value"] += float(r["gia_tri_khop"] or 0)
        agg["fee"] += float(r.get("phi_tra_so") or 0) + float(r.get("phi_dnse") or 0)
        agg["tax"] += float(r.get("thue") or 0)

    return BrokerFills(
        True, "", path, by_key,
        fees=sum(v["fee"] for v in by_key.values()),
        tax=sum(v["tax"] for v in by_key.values()),
        value=sum(v["value"] for v in by_key.values()),
    )


def reconcile_lines(broker, plan_by_key, state_by_key):
    """Sinh các dòng báo cáo (list[str]) cho khối đối soát leg-3. Không in, không raise.

    plan_by_key / state_by_key: {(ticker, side): qty}. `state_by_key` = fill nội bộ bot ghi nhận.
    """
    if not broker.available:
        return [f"ℹ️ Đối soát broker-statement (leg 3): bỏ qua — {broker.reason}."]

    lines = []
    conflicts = []      # broker ≠ state nội bộ → nghi bug đồng bộ / tiến trình trùng
    shortfalls = []     # broker < kế hoạch → thị trường không đủ đối ứng (thường là thanh khoản)
    off_plan = []       # broker có fill trên mã KHÔNG nằm trong plan → leg cũ mù hoàn toàn

    for key in sorted(set(plan_by_key) | set(state_by_key) | set(broker.by_key)):
        ticker, side = key
        planned = plan_by_key.get(key, 0)
        internal = state_by_key.get(key, 0)
        real = broker.qty(ticker, side)
        if key not in plan_by_key and real > 0:
            off_plan.append((ticker, side, real))
            continue
        if real != internal:
            conflicts.append((ticker, side, internal, real))
        elif planned and real < planned:
            shortfalls.append((ticker, side, real, planned))

    if off_plan:
        lines.append("🚨 **KHỚP LỆNH NGOÀI KẾ HOẠCH** (broker statement có, plan hôm nay KHÔNG có) — "
                     "nghi lệnh đặt tay ngoài app hoặc lệnh sót phiên trước:")
        for ticker, side, real in off_plan:
            lines.append(f"  ⚠️ {'MUA' if side == 'buy' else 'BÁN'} {ticker}: {real:,}cp — không có trong plan")

    if conflicts:
        lines.append("🚨 **LỆCH broker-statement ≠ state nội bộ** — hai nguồn độc lập bất đồng, "
                     "cần điều tra (state có thể bị cap ở qty kế hoạch, xem Executor._sync_fills):")
        for ticker, side, internal, real in sorted(conflicts, key=lambda x: -abs(x[3] - x[2])):
            lines.append(f"  ⚠️ {ticker} ({'mua' if side == 'buy' else 'bán'}): state {internal:,} "
                         f"vs broker {real:,} (lệch {real - internal:+,})")

    # Thứ tự có chủ đích: bất thường (nghi bug) TRƯỚC, rồi mới tới khớp thiếu (thị trường).
    # Dòng ✅ nói RÕ nó xác nhận cái gì — "không lệch" đứng ngay trên một khối "khớp thiếu"
    # sẽ đọc như tự mâu thuẫn nếu không nêu rõ hai câu hỏi là khác nhau.
    if not (conflicts or off_plan):
        lines.append("✅ Leg 3 (statement DNSE, độc lập với state/dnse_raw): số khớp trùng khớp "
                     "state nội bộ, không có fill ngoài kế hoạch.")

    if shortfalls:
        lines.append("📉 **Broker xác nhận KHỚP THIẾU so với kế hoạch** — chưa đạt mục tiêu, "
                     "KHÔNG được đọc là \"đã mua đủ\" (§27):")
        for ticker, side, real, planned in sorted(shortfalls, key=lambda x: (x[2] / x[3]) if x[3] else 0):
            pct = 100.0 * real / planned if planned else 0
            lines.append(f"  • {ticker} ({'mua' if side == 'buy' else 'bán'}): chỉ khớp "
                         f"{real:,}/{planned:,} đặt ({pct:.0f}%) — phần thiếu {planned - real:,}cp")

    if broker.value:
        rate = 100.0 * broker.fees / broker.value
        lines.append(f"💸 Phí/thuế THẬT theo statement: {broker.fees:,.0f}đ phí + {broker.tax:,.0f}đ thuế "
                     f"trên {broker.value/1e6:,.1f}M giá trị khớp (= {rate:.4f}% giá trị).")
    return lines


def main():
    import argparse
    import json
    ap = argparse.ArgumentParser(description="Đối soát fill thật theo statement DNSE (leg 3).")
    ap.add_argument("--account", required=True)
    ap.add_argument("--date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--wc-root", default=os.environ.get("WORKDIR", "/home/trido/thanhdt/WorkingClaude"))
    ap.add_argument("--no-fetch", action="store_true", help="không tự tải email nếu thiếu CSV")
    ap.add_argument("--json", action="store_true", help="in JSON thay vì dòng báo cáo")
    args = ap.parse_args()

    b = load_broker_fills(args.date, args.account, args.wc_root, allow_fetch=not args.no_fetch)
    if args.json:
        print(json.dumps({
            "available": b.available, "reason": b.reason, "path": b.path,
            "fills": [{"ticker": k[0], "side": k[1], **v} for k, v in sorted(b.by_key.items())],
            "fees": b.fees, "tax": b.tax, "value": b.value,
        }, ensure_ascii=False, indent=2))
        return
    if not b.available:
        print(f"ℹ️ không đối soát được — {b.reason}")
        return
    for (ticker, side), v in sorted(b.by_key.items()):
        print(f"{ticker:6s} {side:4s} {v['qty']:>8,}cp  {v['value']:>15,.0f}đ  phí {v['fee']:>10,.0f}đ")
    print(f"\nTổng: {b.value:,.0f}đ · phí {b.fees:,.0f}đ · thuế {b.tax:,.0f}đ")


if __name__ == "__main__":
    main()
