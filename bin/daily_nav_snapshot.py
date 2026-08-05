#!/usr/bin/env python3
"""daily_nav_snapshot.py --account SpaceX --date 2026-07-03 [--starting-capital 1000000000]

Tính NAV thật cuối ngày (dùng chung nguyên tắc với verify_account_snapshot.py /
reconcile_equity.py — KHÔNG đọc field ước tính, chỉ dùng fill thật + giá BQ + balance API
thật) và ghi vào lịch sử `data/execution_logs/nav_history_{account}.csv` để daily/weekly/
monthly report đều đọc từ MỘT nguồn duy nhất, nhất quán.

In ra 1 đoạn tóm tắt ngắn (dùng cho daily report — đơn giản, chỉ NAV + biến động) và ghi
JSON chi tiết ra `data/execution_logs/nav_snapshot_{account}_{date}.json`.
"""
import argparse
import csv
import datetime
import glob
import json
import os
import subprocess
import sys
import time as _time

# Chuẩn hóa TZ = ICT cho TOÀN BỘ tiến trình (server chạy UTC): mọi timestamp script này
# tạo ra (kể cả bản ghi balances do brokers._log_raw ghi hộ) phải CÙNG múi giờ với journal
# của bot (bot chạy TZ ICT qua run_bot.sh) — thiếu dòng này, invariant so sánh
# balance_ts vs fill_ts bên dưới so UTC với ICT và từ chối nhầm (bug tự cắn 2026-07-07).
os.environ["TZ"] = "Asia/Ho_Chi_Minh"
_time.tzset()

WC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXEC_DIR = os.path.join(WC_ROOT, "data", "execution_logs")
MIKE_BIN = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE_TMPL = os.path.join(EXEC_DIR, "nav_history_{account}.csv")


def trading_dates_with_fills(account, upto_date):
    dates = []
    for path in sorted(glob.glob(os.path.join(EXEC_DIR, f"exec_{account}_*_journal.csv"))):
        base = os.path.basename(path)
        date = base[len(f"exec_{account}_"):-len("_journal.csv")]
        if date <= upto_date:
            dates.append(date)
    return dates


def today_sell_value(account, date):
    """Tổng giá trị lệnh BÁN đã khớp trong ngày (dùng để cảnh báo balance có thể còn stale
    khi so với biến động cash — xem ghi chú ở latest_balance)."""
    path = os.path.join(EXEC_DIR, f"exec_{account}_{date}_journal.csv")
    if not os.path.exists(path):
        return 0.0
    latest_by_child = {}
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("event") != "FILL" or str(row.get("side") or "").lower() != "sell":
                continue
            child_oid = row.get("child_oid")
            ts = row.get("ts", "")
            prev = latest_by_child.get(child_oid)
            if prev is None or ts >= prev[0]:
                latest_by_child[child_oid] = (ts, float(row.get("qty") or 0),
                                               float(row.get("price") or 0))
    return sum(qty * price for _, qty, price in latest_by_child.values())


def broker_positions(account_label, account_no):
    """Vị thế THẬT từ API broker (source of truth) → {sym: {"qty": ..., "marketPrice": ...}}.

    Bug 2026-07-07 (kb/INCIDENTS.md): NAV từng lấy mtm_stock từ verify_account_snapshot.py
    — tái dựng vị thế TỪ LỊCH SỬ FILL journal. Đúng cho account clean-slate (SpaceX), nhưng
    account có vị thế legacy không có fill history (ZaloPay: DGC/VPB/VIB/VHC/TCM/TLG ~976tr)
    bị BỎ SÓT toàn bộ → EOD report đăng NAV 17,5tr (-98%) lên Trading report. Nguyên tắc:
    NAV đo TÀI SẢN THẬT → hỏi broker; journal chỉ dùng cho cost-basis/P&L attribution.

    marketPrice đi kèm để main() đối chiếu chéo với dnse_close_prices() (bug 2026-08-05: VHM
    chia thưởng cổ phiếu 1:1, vị thế broker cập nhật qty/marketPrice đúng ngay trong ngày
    nhưng close_price() G1 trả giá CŨ trước sự kiện — mtm_stock bị thổi phồng đúng bằng giá
    trị 1 vị thế, cả 2 tài khoản SpaceX/ZaloPay).
    """
    sys.path.insert(0, WC_ROOT)
    from trading_bot.brokers import DNSEBroker
    try:
        b = DNSEBroker(account_id=account_no, quote_only=False, label=account_label)
        b.connect()
        pos = b.get_positions()
        # Side effect CÓ CHỦ ĐÍCH: get_cash() ghi 1 bản ghi "balances" TƯƠI (kèm account
        # tag) vào dnse_raw hôm nay — ngày HOLD bot không chạy lệnh nào nên không có bản
        # ghi balance, latest_balance() sẽ không có gì để đọc nếu thiếu bước này.
        try:
            b.get_cash()
        except Exception:
            pass
        return {sym: {"qty": p["total"], "marketPrice": p.get("marketPrice")}
                for sym, p in pos.items() if p.get("total", 0) > 0}
    except Exception as e:
        print(f"⚠️ Không đọc được positions broker ({account_label}): {e}", file=sys.stderr)
        return None


def latest_balance(raw_path, account_no=None):
    """Bản ghi 'balances' MỚI NHẤT cho ĐÚNG account_no trong file dnse_raw_{date}.jsonl.

    Bug 2026-07-06 (kb/INCIDENTS.md): file này dùng CHUNG cho MỌI account cùng ngày (tên
    file chỉ theo ngày, không theo account) — trước khi ZaloPay go-live cùng ngày với
    SpaceX, chỉ 1 account nên không lộ. Khi 2 account cùng gọi balances() trong 1 ngày,
    bản ghi xen kẽ — lấy "bản ghi cuối cùng" mù quáng có thể lấy NHẦM account, gây báo NAV
    sai (SpaceX báo 688.5tr thay vì 983.0tr thật do lẫn balance của ZaloPay). Field
    account_no được _log_raw() ghi thêm từ 2026-07-06 (trading_bot/brokers.py); bản ghi cũ
    hơn không có field này — nếu account_no được truyền vào mà không lọc được gì, RAISE rõ
    ràng thay vì âm thầm dùng bản ghi có thể sai account.
    """
    if not os.path.exists(raw_path):
        return None
    latest = None
    seen_other_account = False
    with open(raw_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("kind") != "balances":
                continue
            if account_no is not None and rec.get("account_no") not in (None, account_no):
                seen_other_account = True
                continue
            latest = rec
    if latest is None and seen_other_account:
        raise RuntimeError(
            f"dnse_raw file có bản ghi balances nhưng KHÔNG bản nào khớp account_no="
            f"{account_no!r} — file này dùng chung cho nhiều account, tránh dùng nhầm.")
    return latest


def _stock_all_zero(stock):
    """Khối `stock` TOÀN SỐ 0 = lỗi API tạm thời của DNSE (xem invariant trong main())."""
    nums = [v for v in stock.values() if isinstance(v, (int, float)) and not isinstance(v, bool)]
    return bool(nums) and not any(nums)


def previous_balance(account_no, date):
    """Bản ghi 'balances' hợp lệ MỚI NHẤT của account, ở phiên TRƯỚC `date`.

    Dùng để đo mức TĂNG của `cashDividendReceiving` trong ngày (xem
    cum_dividend_double_count). Bỏ qua bản ghi toàn-số-0 vì nó tạo ra một cú sụt rồi bật
    giả trong chuỗi và làm hỏng phép so delta.
    """
    for path in sorted(glob.glob(os.path.join(EXEC_DIR, "dnse_raw_*.jsonl")), reverse=True):
        d = os.path.basename(path)[len("dnse_raw_"):-len(".jsonl")]
        if d >= date:
            continue
        latest = None
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if rec.get("kind") != "balances":
                    continue
                if account_no is not None and rec.get("account_no") not in (None, account_no):
                    continue
                if _stock_all_zero(rec.get("payload", {}).get("stock") or {}):
                    continue
                latest = rec
        if latest is not None:
            return latest
    return None


# Thị trường đóng 14:45 ICT; DNSE ghi khoản cổ tức phải thu trong đợt xử lý sau phiên. Bản ghi
# balance từ 16:00 trở đi coi là "cuối ngày" — đủ muộn để đã thấy đợt xử lý đó.
CUM_DIV_EOD_HHMM = "16:00"


def cum_dividend_double_count(account_no, date, positions, cur_bal, prev_bal,
                              events=None, bq_max_date=None):
    """Cổ tức tiền mặt ĐÃ nằm trong `totalCash` nhưng giá cổ phiếu CHƯA rơi ex-date.

    BUG GỐC (báo cáo tuần 27–31/07/2026 Mục 11.5, 5 dòng NAV lịch sử sai): DNSE ghi khoản
    `cashDividendReceiving` vào số dư ngay TỐI NGÀY CUỐI CÙNG CÒN HƯỞNG QUYỀN (last-cum-date),
    trong khi giá đóng cửa phiên đó VẪN CÒN bao gồm quyền nhận cổ tức. NAV cuối ngày =
    cổ phiếu (giá cum) + tiền (đã gồm khoản phải thu) → ĐẾM 2 LẦN cùng một khoản cổ tức, tự
    triệt tiêu ở phiên kế tiếp khi giá rơi về mức không hưởng quyền. NAV tổng cuối tháng vẫn
    đúng, nên mọi phép đối soát NAV đều PASS — đó là lý do lỗi sống sót (xem coding_guidelines §21).

    HAI ĐƯỜNG XÁC ĐỊNH, cố ý tách vai:
      * SỐ TIỀN phải trừ = mức TĂNG thật của `cashDividendReceiving` so với bản ghi balance
        hợp lệ cuối cùng của phiên trước. Chỉ số này mới biết chắc "bao nhiêu tiền đang thực
        sự nằm trong totalCash" (chia tách cổ phiếu không sinh tiền → delta = 0, tự loại).
      * TÍNH HỢP LỆ (có đúng là chưa qua ex-date không) = tỉ số Close/Price trong BQ
        (`dividend_adjusted_return.detect_adjustments_batch`) — nguồn có thẩm quyền về ex-date.
        NHƯNG cú nhảy tỉ số chỉ lộ ra ĐÚNG Ở phiên ex, nên chạy live lúc 19:10 (BQ mới sync
        tới hôm qua) sẽ KHÔNG thấy gì. Vì vậy khi BQ chưa có phiên nào sau `date`, ta lùi về
        quy tắc thời điểm: bản ghi phiên trước là bản CUỐI NGÀY (≥16:00) ⇒ khoản tăng chắc
        chắn mới được ghi tối nay ⇒ ex-date là phiên sau ⇒ trừ.

    Ca thật minh hoạ vì sao cần cả hai (SpaceX 09/07/2026, MBB): khoản 2.400.000đ lần đầu
    QUAN SÁT được lúc 09/07 15:00 nhưng ex-date đúng là 09/07 (giá đã rơi) — bản ghi phiên
    trước lại là bản GIỮA PHIÊN (08/07 15:00), không kết luận được bằng thời điểm. BQ (lịch
    sử) trả lời dứt khoát: không còn ex-date nào phía sau 09/07 ⇒ KHÔNG trừ. Đúng.

    Trả về dict (đưa nguyên vào JSON snapshot để truy vết được về sau).
    """
    res = {"amount": 0.0, "delta": 0.0, "expected_bq": None, "tickers": [],
           "bq_max_date": bq_max_date, "note": "", "warnings": []}
    cur_cd = float((cur_bal.get("payload", {}).get("stock") or {}).get("cashDividendReceiving") or 0)
    if prev_bal is None:
        if cur_cd:
            res["warnings"].append(
                f"Không có bản ghi balances hợp lệ nào ở phiên trước {date} — KHÔNG kiểm được "
                f"cổ tức phải thu ({cur_cd:,.0f}đ) có bị đếm 2 lần hay không.")
        return res
    prev_cd = float((prev_bal.get("payload", {}).get("stock") or {}).get("cashDividendReceiving") or 0)
    res["delta"] = cur_cd - prev_cd
    if res["delta"] <= 0:
        return res

    if events is None and positions:
        try:
            sys.path.insert(0, MIKE_BIN)
            from dividend_adjusted_return import detect_adjustments_batch
            d0 = datetime.date.fromisoformat(date)
            events, bq_max_date = detect_adjustments_batch(
                sorted(positions), (d0 - datetime.timedelta(days=15)).isoformat(),
                (d0 + datetime.timedelta(days=15)).isoformat())
            res["bq_max_date"] = bq_max_date
        except Exception as e:  # BQ hỏng/không với tới được → vẫn còn quy tắc thời điểm
            res["warnings"].append(f"Không tra được ex-date từ BigQuery ({e}) — chỉ dựa vào "
                                   f"thời điểm bản ghi balance.")
            events = None

    pending = [a for tk, advs in (events or {}).items() if tk in positions
               for a in advs if a.last_cum_date <= date < a.ex_date]
    # BQ chỉ KẾT LUẬN ĐƯỢC khi đã có ít nhất 1 phiên sau `date` (ex-date lộ ra ở phiên ex).
    if events is not None and bq_max_date and bq_max_date > date and not pending:
        res["note"] = (f"cashDividendReceiving tăng {res['delta']:,.0f}đ nhưng BQ (dữ liệu tới "
                       f"{bq_max_date}) xác nhận không mã nào còn ex-date sau {date} — khoản này "
                       f"ĐÃ qua ex-date, không trừ.")
        return res

    prev_ts = prev_bal.get("ts", "")
    prev_is_eod = len(prev_ts) >= 16 and prev_ts[11:16] >= CUM_DIV_EOD_HHMM
    if not pending and not prev_is_eod:
        res["warnings"].append(
            f"cashDividendReceiving tăng {res['delta']:,.0f}đ nhưng KHÔNG kết luận được đã qua "
            f"ex-date hay chưa: BQ chưa có phiên sau {date} và bản ghi balance phiên trước "
            f"({prev_ts or '?'}) là bản GIỮA PHIÊN. KHÔNG tự trừ — cần người đối chiếu.")
        return res

    res["amount"] = res["delta"]
    res["tickers"] = sorted({a.ticker for a in pending})
    if pending:
        res["expected_bq"] = sum(positions.get(a.ticker, 0) * a.per_share for a in pending)
        tol = max(10.0, res["delta"] * 0.005)
        if abs(res["expected_bq"] - res["delta"]) > tol:
            res["warnings"].append(
                f"Cổ tức chờ theo BQ ({res['expected_bq']:,.0f}đ cho {res['tickers']}) LỆCH so với "
                f"mức tăng thật của cashDividendReceiving ({res['delta']:,.0f}đ) — trừ theo số "
                f"tiền thật trong tài khoản, nhưng cần người kiểm tra nguyên nhân lệch.")
        res["note"] = (f"Trừ {res['amount']:,.0f}đ cổ tức phải thu của {', '.join(res['tickers'])} "
                       f"(ex-date {sorted({a.ex_date for a in pending})[0]}) — giá đóng cửa {date} "
                       f"vẫn CÒN quyền, cộng vào tiền nữa là đếm 2 lần.")
    else:
        res["note"] = (f"Trừ {res['amount']:,.0f}đ cổ tức phải thu vừa ghi nhận tối {date} "
                       f"(bản ghi phiên trước {prev_ts} là bản cuối ngày ⇒ ex-date là phiên sau; "
                       f"BQ chưa có dữ liệu sau {date} để xác nhận mã cụ thể).")
    return res


def load_history(account):
    path = HISTORY_FILE_TMPL.format(account=account)
    rows = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    return path, rows


def _write_nav_history(hist_path, hist_rows, fieldnames):
    """Atomic write (tmp + os.replace) — cùng pattern executor.py _save_state (review
    vòng 2 2026-07-02, kb/coding_guidelines.md §5): nav_history là nguồn duy nhất mọi
    báo cáo ngày/tuần/tháng dùng chung, kill mid-write không được để lại file truncate
    dở dang (đã xảy ra 2026-07-06: mất 2 dòng lịch sử). os.replace = rename nguyên tử
    trên POSIX — reader luôn thấy hoặc file cũ hoặc file mới, không bao giờ file dở.

    extrasaction="ignore": lịch sử cũ có thể mang field từ version trước của script
    (vd cột đã bỏ) — không để 1 dòng cũ làm hỏng cả file.
    """
    tmp = hist_path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows({k: row.get(k, "") for k in fieldnames} for row in hist_rows)
    os.replace(tmp, hist_path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--account", required=True)
    ap.add_argument("--account-no", default=None)
    ap.add_argument("--date", required=True)
    ap.add_argument("--starting-capital", type=float, default=1_000_000_000)
    args = ap.parse_args()

    # account_no: dùng --account-no nếu có, else tự tra secrets/trading_bot_accounts.json
    # theo label — tránh phải nhớ truyền tay mỗi lần gọi (và là điều kiện BẮT BUỘC để lọc
    # đúng account trong dnse_raw_{date}.jsonl dùng chung, xem latest_balance()).
    account_no = args.account_no
    sys.path.insert(0, WC_ROOT)
    from trading_bot.config import load_config, load_accounts
    _profiles = load_accounts(load_config())
    _match = next((p for p in _profiles if p["label"] == args.account), None)
    if not account_no:
        account_no = _match.get("account_id") if _match else None
    # Tài sản off-book (vd "Trứng vàng" DNSE — không lộ qua OpenAPI, xem
    # trading_bot/config.py ACCOUNT_DEFAULTS): user tự báo, Mike cập nhật config khi thay
    # đổi. Cộng vào NAV THẬT (không cộng vào 'cash' — cash vẫn phải là sức mua thực sự khả
    # dụng ở tài khoản môi giới), tránh NAV báo THẤP hơn thực tế sau khi user chuyển tiền
    # sang sản phẩm này, và tránh sanity-guard bên dưới chặn oan 1 ngày biến động lớn do
    # chuyển tiền thật (không phải lỗi dữ liệu).
    offbook = float((_match or {}).get("manual_offbook_assets_vnd") or 0)
    offbook_note = (_match or {}).get("manual_offbook_assets_note") or ""
    offbook_asof = (_match or {}).get("manual_offbook_assets_asof") or ""
    # Staleness WARN (quant-skeptic review 2026-07-17): số off-book là user tự báo, KHÔNG có
    # API xác nhận lại — nếu asof quá cũ, cảnh báo thay vì âm thầm tin mãi 1 con số có thể đã
    # đổi (user rút bớt/rút hết mà quên báo, hoặc Mike quên cập nhật config).
    offbook_stale_warning = None
    if offbook and offbook_asof:
        import datetime as _dt_stale
        try:
            age_days = (_dt_stale.date.fromisoformat(args.date)
                        - _dt_stale.date.fromisoformat(offbook_asof)).days
            if age_days > 21:
                offbook_stale_warning = (
                    f"manual_offbook_assets_asof ({offbook_asof}) đã {age_days} ngày — xác nhận "
                    f"lại số dư Trứng vàng/off-book với user trước khi tin tưởng hoàn toàn.")
        except ValueError:
            pass

    dates = trading_dates_with_fills(args.account, args.date)
    if not dates:
        print(f"ℹ️ [{args.date}] Chưa có ngày giao dịch nào cho {args.account} — bỏ qua NAV snapshot.")
        return 0

    # verify_account_snapshot: giờ chỉ là CROSS-CHECK advisory (cost-basis/đối soát journal)
    # — NAV không còn phụ thuộc nó (xem docstring broker_positions về bug 2026-07-07).
    snapshot_out = os.path.join(EXEC_DIR, f"verified_snapshot_{args.account}_{args.date}.json")
    cmd = [sys.executable, os.path.join(MIKE_BIN, "verify_account_snapshot.py"),
           "--account", args.account, "--dates", ",".join(dates), "--asof", args.date,
           "--out", snapshot_out]
    if account_no:
        cmd += ["--account-no", account_no]
    r = subprocess.run(cmd, capture_output=True, text=True)
    verify_warning = None
    if r.returncode not in (0,):
        verify_warning = (f"verify_account_snapshot (cross-check journal) rc={r.returncode} — "
                          f"NAV vẫn tính từ vị thế broker thật; cần xem cost-basis/đối soát riêng.")

    # ── mtm_stock = vị thế BROKER THẬT × giá đóng cửa verified ──
    positions = broker_positions(args.account, account_no)
    if not positions:
        print(f"❌ [{args.date}] Không lấy được vị thế broker — KHÔNG tính NAV "
              f"(tránh đăng số thiếu vị thế).", file=sys.stderr)
        return 2
    sys.path.insert(0, MIKE_BIN)
    from verify_account_snapshot import dnse_close_prices, bq_close_prices
    import datetime as _dt
    tickers = sorted(positions)
    is_today = args.date == _dt.date.today().isoformat()
    if is_today:
        prices = dnse_close_prices(tickers)
    else:
        prices, _perr = bq_close_prices(tickers, args.date)
        prices = prices or {}
    missing = [t for t in tickers if t not in prices]
    if missing:
        print(f"❌ [{args.date}] Thiếu giá đóng cửa verified cho {missing} — KHÔNG tính NAV "
              f"(không đoán giá).", file=sys.stderr)
        return 2

    # ── Đối chiếu chéo close_price(G1) vs marketPrice của CHÍNH vị thế broker (bug
    # 2026-08-05: VHM chia thưởng cổ phiếu 1:1, qty/marketPrice của vị thế cập nhật đúng
    # ngay trong ngày nhưng close_price() G1 vẫn trả giá TRƯỚC sự kiện — mtm_stock bị thổi
    # phồng đúng bằng giá trị 1 vị thế, cả SpaceX lẫn ZaloPay). Chỉ đối chiếu được khi
    # is_today (marketPrice của vị thế broker luôn là ảnh chụp HIỆN TẠI, vô nghĩa với
    # --date lịch sử). Lệch >PRICE_XCHECK_TOLERANCE_PCT gần như chắc chắn là corporate
    # action broker chưa đồng bộ hết mọi nguồn giá — fail-safe từ chối, không đoán giá nào
    # đúng hơn (đúng nguyên tắc "không tự sửa, escalate" đã dùng xuyên suốt script này).
    PRICE_XCHECK_TOLERANCE_PCT = 5.0
    if is_today:
        mismatched = []
        for t in tickers:
            mp = (positions[t] or {}).get("marketPrice")
            cp = prices.get(t)
            if not mp or not cp:
                continue
            diff_pct = abs(cp - mp) / mp * 100
            if diff_pct > PRICE_XCHECK_TOLERANCE_PCT:
                mismatched.append((t, cp, mp, diff_pct))
        if mismatched:
            detail = "; ".join(f"{t}: close_price={cp:,.0f} vs vị thế broker marketPrice={mp:,.0f} "
                               f"(lệch {d:.1f}%)" for t, cp, mp, d in mismatched)
            print(f"❌ [{args.date}] Giá close_price(G1) và marketPrice của vị thế broker LỆCH "
                  f">{PRICE_XCHECK_TOLERANCE_PCT:.0f}% cho {len(mismatched)} mã — KHÔNG tính NAV "
                  f"(nghi corporate action broker chưa đồng bộ hết nguồn giá, xem VHM 2026-08-05): "
                  f"{detail}. Kiểm tra thủ công trước khi chạy lại.", file=sys.stderr)
            return 2

    mtm_stock = sum(pos["qty"] * prices[t] for t, pos in positions.items())

    raw_path = os.path.join(EXEC_DIR, f"dnse_raw_{args.date}.jsonl")
    try:
        bal = latest_balance(raw_path, account_no=account_no)
    except RuntimeError as e:
        print(f"⚠️ [{args.date}] {e}", file=sys.stderr)
        return 2
    if bal is None:
        print(f"⚠️ [{args.date}] Không có record balances thật trong {raw_path} — "
              f"KHÔNG tính NAV (tránh dùng số ước tính/cũ).", file=sys.stderr)
        return 2

    stock = bal["payload"]["stock"]

    # INVARIANT (bug 2026-07-27, Taylor phát hiện qua báo cáo tuần 07-27→07-31): DNSE có lúc
    # trả về block `stock` TOÀN SỐ 0 (cả totalCash/availableCash/depositInterest/
    # depositFeeAmount/cashDividendReceiving = 0) — đó là API lỗi tạm thời, KHÔNG phải tiền
    # mặt thật về 0. Ngày 27/07 cả 2 lần đọc 19:04:59 và 19:10:20 đều toàn 0, script cũ nhận
    # số 0 đó và ghi NAV=804.077.200 (thiếu đúng 32.011.420đ tiền mặt = -3,83% NAV), làm
    # thổi phồng vol năm hoá 26,5%→37,7% và MaxDD -16,12%→-19,33% trong báo cáo tuần.
    # Tài khoản live có cổ phiếu thì depositInterest/depositFeeAmount gần như không bao giờ
    # đồng loạt bằng 0 → toàn-0 = dấu hiệu lỗi feed rõ ràng. FAIL-SAFE: từ chối ghi, KHÔNG
    # tự đoán số đúng (người chạy lại script/lấy bản đọc tươi hôm sau mới là nguồn thật).
    numeric = [v for v in stock.values() if isinstance(v, (int, float)) and not isinstance(v, bool)]
    if numeric and not any(numeric):
        print(f"❌ [{args.date}] Balance record ({bal.get('ts')}) trả về TOÀN SỐ 0 "
              f"(totalCash=0, totalDebt=0, và mọi field số khác =0) — đây là lỗi API tạm "
              f"thời của DNSE, KHÔNG phải NAV thật về 0. KHÔNG tính NAV để tránh ghi số sai "
              f"vào nav_history. Chạy lại script để lấy bản đọc balance tươi; nếu cuối ngày "
              f"vẫn toàn 0, lấy bản đọc đầu phiên hôm sau (TRƯỚC cú khớp đầu tiên) và điền "
              f"tay sau khi đối chiếu.", file=sys.stderr)
        return 2

    cash, debt = stock["totalCash"], stock["totalDebt"]

    # INVARIANT (bug 2026-07-07 lần 2, user chỉ ra): bản ghi balance phải MỚI HƠN cú khớp
    # CUỐI CÙNG trong ngày — ngày vừa mua vừa bán, DNSE cập nhật tiền theo TỪNG khớp
    # (mua khớp T0: totalCash → secureAmount trong vòng vài phút), snapshot chụp GIỮA
    # 2 cú khớp sẽ lệch đúng bằng giá trị lệnh sau (ZaloPay: balance 13:00:02 vs VCB khớp
    # 13:00:22 → NAV thừa 6,1tr vì cổ phiếu đã đếm VCB mà tiền chưa trừ).
    jpath = os.path.join(EXEC_DIR, f"exec_{args.account}_{args.date}_journal.csv")
    last_fill_ts = ""
    if os.path.exists(jpath):
        with open(jpath, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("event") == "FILL" and row.get("ts", "") > last_fill_ts:
                    last_fill_ts = row["ts"]
    if last_fill_ts and bal.get("ts", "") <= last_fill_ts:
        print(f"❌ [{args.date}] Balance record ({bal.get('ts')}) CŨ HƠN cú khớp cuối cùng "
              f"({last_fill_ts}) — tiền chưa phản ánh đủ lệnh đã khớp, KHÔNG tính NAV. "
              f"Chạy lại script (nó tự đọc balance tươi qua broker_positions/get_cash).",
              file=sys.stderr)
        return 2

    # ── Cổ tức phải thu ghi TRƯỚC ex-date: loại ra khỏi tiền để không đếm 2 lần ──
    # (bug 2026-08-02, coding_guidelines §21 — xem docstring cum_dividend_double_count)
    cum_div = cum_dividend_double_count(account_no, args.date, positions, bal,
                                        previous_balance(account_no, args.date))
    cash_broker = cash
    cash -= cum_div["amount"]

    # NAV = Tiền + Cổ phiếu − Nợ (đúng như app DNSE hiển thị "Tài sản ròng" — user xác nhận
    # 2026-07-06 bằng ảnh chụp thật, khớp chính xác đến từng đồng: 709.276.086 + 683.590.000
    # − 409.863.737 = 983.002.349). KHÔNG cần tự ước tính "tiền bán chờ T+2" cộng riêng —
    # `totalCash` của DNSE RỐT CUỘC cũng tự cộng khoản này vào, chỉ là CẦN THỜI GIAN để hệ
    # thống broker cập nhật (có vẻ qua 1 đợt đối soát cuối ngày, không tức thời sau khớp
    # lệnh). Bài học rút ra CÙNG NGÀY (xem kb/INCIDENTS.md): lần đọc balance sớm hơn cùng
    # ngày (giữa phiên chiều) từng cho totalDebt=0 SAI — không phải do nợ được trả ngay như
    # suy luận ban đầu, mà đơn giản là dữ liệu balance LÚC ĐÓ CHƯA CẬP NHẬT XONG (stale).
    # Lần đọc sau (cuối ngày) mới đúng, khớp ảnh chụp thật. => KHÔNG tự suy luận/mô hình hoá
    # thêm gì — chỉ cần đảm bảo balance record dùng để tính NAV là bản MỚI NHẤT trong ngày
    # (đã tự động nhờ latest_balance() lấy dòng cuối), và cảnh báo rõ nếu có dấu hiệu stale.
    # + offbook: tài sản off-book user tự báo (vd Trứng vàng, xem ACCOUNT_DEFAULTS) — cộng
    # thẳng vào NAV thật, KHÔNG lẫn vào 'cash' (cash vẫn = sức mua thật ở tài khoản môi giới).
    nav = mtm_stock + cash - debt + offbook

    sell_today = today_sell_value(args.account, args.date)
    stale_warning = None
    if sell_today > 1_000_000 and cash < sell_today * 0.5:
        stale_warning = (f"Hôm nay có bán {sell_today:,.0f}đ nhưng tiền mặt ({cash:,.0f}đ) "
                         f"không phản ánh tương xứng — balance có thể CHƯA cập nhật xong "
                         f"(đối soát cuối ngày), nên chạy lại script này muộn hơn/ngày mai "
                         f"để lấy số chính xác trước khi tin tưởng hoàn toàn.")

    hist_path, hist_rows = load_history(args.account)
    prev_nav = None
    for row in hist_rows:
        if row["date"] < args.date:
            prev_nav = float(row["nav"])
    if prev_nav is None:
        prev_nav = args.starting_capital

    day_change = nav - prev_nav
    day_change_pct = day_change / prev_nav * 100 if prev_nav else 0

    # SANITY GUARD (bài học 2026-07-07: NAV -98.25% được auto-đăng lên Trading report vì
    # không tầng nào chặn số phi lý): |biến động ngày| vượt ngưỡng → KHÔNG ghi lịch sử,
    # KHÔNG in NAV — in cảnh báo escalate để con người xem. VNINDEX biên độ ±7%/ngày; NAV
    # account biến động >15%/ngày gần như chắc chắn là bug dữ liệu (hoặc nạp/rút tiền lớn —
    # trường hợp đó con người xác nhận rồi chạy lại với NAV_SANITY_MAX_PCT cao hơn).
    sanity_max = float(os.environ.get("NAV_SANITY_MAX_PCT", "15"))
    if abs(day_change_pct) > sanity_max:
        print(f"🔴 NAV {args.date} ({args.account}) TỰ CHẶN KHÔNG ĐĂNG: {nav:,.0f} VND "
              f"(biến động {day_change_pct:+.2f}%/ngày vượt ngưỡng ±{sanity_max:.0f}%) — "
              f"gần như chắc chắn lỗi dữ liệu (vị thế thiếu/giá sai). Cần người kiểm tra; "
              f"nếu là nạp/rút tiền thật → chạy lại với NAV_SANITY_MAX_PCT lớn hơn.")
        return 3

    hist_rows = [row for row in hist_rows if row["date"] != args.date]
    hist_rows.append({"date": args.date, "nav": f"{nav:.0f}", "mtm_stock": f"{mtm_stock:.0f}",
                       "cash": f"{cash:.0f}", "margin_debt": f"{debt:.0f}",
                       "offbook_assets": f"{offbook:.0f}", "balance_ts": bal["ts"],
                       "cum_dividend_excl": f"{cum_div['amount']:.0f}"})
    hist_rows.sort(key=lambda r: r["date"])
    # `cash` = tiền THẬT của broker TRỪ cổ tức phải thu chưa qua ex-date (cum_dividend_excl),
    # để bất biến nav = mtm_stock + cash − margin_debt + offbook_assets luôn đúng trên mọi dòng.
    fieldnames = ["date", "nav", "mtm_stock", "cash", "margin_debt", "offbook_assets",
                  "balance_ts", "cum_dividend_excl"]
    _write_nav_history(hist_path, hist_rows, fieldnames)

    since_inception = nav - args.starting_capital
    since_inception_pct = since_inception / args.starting_capital * 100

    lines = [
        f"💰 **NAV {args.date}: {nav:,.0f} VND** ({day_change:+,.0f} VND, {day_change_pct:+.2f}% so với hôm trước)",
        f"   Cổ phiếu {mtm_stock:,.0f} · Tiền mặt {cash:,.0f} · Nợ margin {debt:,.0f}"
        + (f" · Off-book {offbook:,.0f}" if offbook else ""),
        f"   Từ go-live: {since_inception:+,.0f} VND ({since_inception_pct:+.2f}%)",
    ]
    if cum_div["amount"]:
        lines.append(f"   ℹ️ Đã LOẠI {cum_div['amount']:,.0f} VND cổ tức phải thu khỏi tiền mặt "
                      f"(broker báo {cash_broker:,.0f}) — {cum_div['note']}")
    for w in cum_div["warnings"]:
        lines.append(f"   ⚠️ {w}")
    if offbook:
        lines.append(f"   ℹ️ Off-book {offbook:,.0f} VND ({offbook_note or 'không có ghi chú'}, "
                      f"user tự báo asof {offbook_asof or '?'}) — KHÔNG lộ qua API broker, đã "
                      f"cộng vào NAV nhưng KHÔNG tính là tiền mặt khả dụng để đặt lệnh ngay.")
    if offbook_stale_warning:
        lines.append(f"   ⚠️ {offbook_stale_warning}")
    if debt > 1_000_000:
        lines.append(f"   ⚠️ Đang có nợ margin thật {debt:,.0f} VND — theo dõi lãi vay tích lũy.")
    if stale_warning:
        lines.append(f"   ⚠️ {stale_warning}")
    if verify_warning:
        lines.append(f"   ℹ️ {verify_warning}")
    print("\n".join(lines))

    out = {"account": args.account, "date": args.date, "nav": nav,
           "mtm_stock": mtm_stock, "cash": cash, "cash_broker": cash_broker,
           "cum_dividend_excl": cum_div, "margin_debt": debt,
           "offbook_assets": offbook, "offbook_assets_note": offbook_note,
           "offbook_assets_asof": offbook_asof, "offbook_stale_warning": offbook_stale_warning,
           "stale_warning": stale_warning, "prev_nav": prev_nav, "day_change": day_change,
           "day_change_pct": day_change_pct, "since_inception": since_inception,
           "since_inception_pct": since_inception_pct, "balance_ts": bal["ts"],
           "source": "verify_account_snapshot.py (fills) + dnse_raw balances (real broker API, "
                     "chọn bản GHI CUỐI CÙNG trong ngày — balance có thể cần thời gian đối soát "
                     "cuối phiên mới phản ánh đúng, xem cảnh báo staleness nếu có) + "
                     "manual_offbook_assets_vnd (trading_bot_accounts.json, user tự báo, KHÔNG "
                     "có API — xem note/asof)"}
    with open(os.path.join(EXEC_DIR, f"nav_snapshot_{args.account}_{args.date}.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
