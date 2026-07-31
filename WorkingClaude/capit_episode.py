# -*- coding: utf-8 -*-
"""
capit_episode.py — SỔ EPISODE CAPIT (quan sát thuần, KHÔNG quyết định gì).

Vì sao tồn tại (điều tra Taylor_20260731_025222, research/capit_state_visibility_gap_20260731.md):
`capit_fired`/`capit_signal_today` trong data/golive_v23_status.json là **điều kiện CỦA NGÀY CHẠY**
— tính lại từ đầu mỗi phiên, không đọc state nào. Từ 07-29 breadth rớt dưới gate ⇒ cờ về False,
`basket`/`size`/`n_capit_basket` về rỗng/0, và MỌI kênh báo cáo im lặng về CAPIT — trong khi vị thế
THẬT vẫn còn đủ 5 mã ở cả 2 account (NCT/PVT/SAB/SIP/VNM, vào lệnh 07-21). Không có file/bảng nào
ghi "episode CAPIT #1: entry 07-20, còn mở". File này là sổ đó.

RANH GIỚI (cố ý, đừng nới): module này KHÔNG chọn mã, KHÔNG tính size, KHÔNG chặn lệnh. Nó chỉ
GHI LẠI cái đã xảy ra và ĐỌC bằng chứng broker. golive_recommend_v23.py gọi nó BÊN NGOÀI nhánh
`if capit_signal_today:` nên không có đường nào để nó đổi quyết định mua.

Cơ chế exit THẬT của CAPIT (đã xác nhận, không đoán — grep toàn repo 2026-07-31):
`CAPIT_HOLD = 60` chỉ tồn tại trong đường BACKTEST/PAPER (`pt_v22_dt5g.py:123`,
`lag_dnpr_harness.py:484`, dùng qua `hold_days_by_tier`). Đường LIVE **không có dòng code nào**
bán vị thế CAPIT — exit do NGƯỜI quyết (plan DollarBill + user duyệt). `dc_book_waterfall`
reverse-unwind là của DC book, không áp cho CAPIT. Vì vậy đóng episode phải dựa vào BẰNG CHỨNG
vị thế broker, không dựa vào một quy tắc hold nào cả.

GIỚI HẠN ĐÃ BIẾT (ghi thẳng ra đây thay vì giả vờ chính xác):
  • Vị thế broker KHÔNG mang nhãn book. PVT/SIP vừa nằm trong rổ CAPIT vừa nằm trong custom30V
    parking ⇒ không thể tách "bao nhiêu cổ là CAPIT" từ dữ liệu broker. Hệ quả: auto-close CHỈ
    kích hoạt khi TẤT CẢ mã trong rổ về 0 ở MỌI account live — bằng chứng không thể nhầm. Còn dư
    một cổ vì lý do khác (custom30V) ⇒ episode **vẫn mở**. Chiều sai này là chiều an toàn: thà
    CAPIT hiện lâu hơn thực tế còn hơn im lặng trong lúc đang giữ (đúng lỗi vừa xảy ra). Đóng tay:
    `python capit_episode.py --close <episode_id> --note "..."`.
  • `qty_filled` lấy từ fill THẬT của broker (kb/coding_guidelines.md §6: fill broker mới là nguồn
    chuẩn tắc, không phải qty trong plan) nhưng quy về book CAPIT qua plan (`book=="CAPIT"`). Nếu
    trong CÙNG một ngày, CÙNG account, CÙNG mã mà book khác cũng mua thì phần đó bị tính gộp vào
    CAPIT. Đã kiểm 07-20→07-30: không có ca nào. `qty_planned` giữ song song để so lệch.

Ledger: data/capit_episode.json — ghi atomic (tmp + os.replace, guidelines §5).
"""
import os, sys, json, glob, argparse
from datetime import datetime, timedelta

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
LEDGER_PATH = os.path.join(WORKDIR, "data", "capit_episode.json")

# Snapshot vị thế cũ hơn ngần này (ngày dương lịch) thì KHÔNG được dùng để auto-close:
# thà giữ episode mở còn hơn đóng nhầm dựa trên ảnh chụp cũ.
POSITIONS_MAX_AGE_DAYS = 7

# Episode fire nhưng KHÔNG có lệnh nào khớp: sau ngần này phiên (và gate đã tắt) thì đóng sổ,
# tránh treo một episode chưa từng giải ngân. Giải ngân thật rơi vào T+1 nên 5 phiên là rộng rãi.
NO_DEPLOY_CLOSE_SESSIONS = 5


# ────────────────────────────── ledger I/O ──────────────────────────────
def _load(path):
    if not os.path.exists(path):
        return {"episodes": []}
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    d.setdefault("episodes", [])
    return d


def _save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def _open_episode(ledger):
    for ep in reversed(ledger["episodes"]):
        if ep.get("status") == "open":
            return ep
    return None


# ────────────────────────── bằng chứng từ broker ──────────────────────────
def _live_labels():
    """Nhãn account live. Fail-safe: config lỗi -> danh sách rỗng -> không auto-close."""
    try:
        from trading_bot.config import live_dnse_labels
        return sorted(live_dnse_labels())
    except Exception:
        return []


def _raw_records(workdir, date_str, kind, label):
    """Bản ghi dnse_raw của MỘT account. Lọc account_label NGAY dòng đầu (guidelines §12 —
    file này dùng chung mọi account, không lọc = lẫn số giữa các account)."""
    p = os.path.join(workdir, "data", "execution_logs", f"dnse_raw_{date_str}.jsonl")
    if not os.path.exists(p):
        return []
    out = []
    with open(p, encoding="utf-8") as f:
        for ln in f:
            try:
                r = json.loads(ln)
            except Exception:
                continue
            if r.get("account_label") != label:
                continue
            if r.get("kind") != kind:
                continue
            out.append(r)
    return out


def _plan_capit_orders(workdir, label, date_str, basket):
    """Lệnh book=CAPIT trong plan của (account, ngày) -> {(ticker, side): qty}."""
    p = os.path.join(workdir, "data", "trade_plans", f"plan_{label}_{date_str}.json")
    if not os.path.exists(p):
        return {}
    try:
        with open(p, encoding="utf-8") as f:
            plan = json.load(f)
    except Exception:
        return {}
    out = {}
    for o in plan.get("orders") or []:
        if str(o.get("book", "")).upper() != "CAPIT":
            continue
        tk = str(o.get("ticker", "")).upper()
        if tk not in basket:
            continue
        side = str(o.get("side", "")).lower()
        if side not in ("buy", "sell"):
            continue
        out[(tk, side)] = out.get((tk, side), 0) + int(o.get("qty") or 0)
    return out


def _filled_qty(workdir, label, date_str, ticker, side):
    """Qty KHỚP THẬT của broker cho (account, ngày, mã, chiều) — nguồn chuẩn tắc (§6).
    Lấy bản ghi `orders` MUỘN NHẤT trong ngày (ảnh chụp cuối = trạng thái cuối phiên)."""
    recs = _raw_records(workdir, date_str, "orders", label)
    if not recs:
        return None
    recs.sort(key=lambda r: r.get("ts") or "")
    orders = (recs[-1].get("payload") or {}).get("orders") or []
    want = "NB" if side == "buy" else "NS"
    tot = 0
    for o in orders:
        if str(o.get("symbol", "")).upper() != ticker:
            continue
        if str(o.get("side")) != want:
            continue
        # Sổ lệnh broker trả về CẢ lệnh của ngày trước, không chỉ ngày của file log —
        # thiếu bộ lọc này, replay 07-21 cộng nhầm 1 CP PVT của ZaloPay từ lệnh ngày khác
        # (fill 2071 vs plan 2070). Lọc theo transDate của CHÍNH lệnh đó.
        if str(o.get("transDate", ""))[:10] != date_str:
            continue
        tot += int(o.get("fillQuantity") or 0)
    return tot


def _positions_snapshot(workdir, label, upto_date):
    """Ảnh chụp vị thế MỚI NHẤT (<= upto_date) của MỘT account -> ({symbol: qty}, ngày).
    Trả (None, None) nếu không tìm được ảnh chụp nào -> không đủ căn cứ để auto-close."""
    files = sorted(glob.glob(os.path.join(workdir, "data", "execution_logs", "dnse_raw_*.jsonl")))
    for p in reversed(files):
        d = os.path.basename(p)[len("dnse_raw_"):-len(".jsonl")]
        if d > upto_date:
            continue
        recs = _raw_records(workdir, d, "positions", label)
        if not recs:
            continue
        recs.sort(key=lambda r: r.get("ts") or "")
        pos = (recs[-1].get("payload") or {}).get("positions") or []
        qty = {}
        for it in pos:
            sym = str(it.get("symbol", "")).upper()
            q = it.get("openQuantity")
            if q is None:
                q = int(it.get("accumulateQuantity") or 0) - int(it.get("closedQuantity") or 0)
            qty[sym] = qty.get(sym, 0) + int(q or 0)
        return qty, d
    return None, None


def _refresh_evidence(ep, workdir, session_dates, signal_date):
    """Cập nhật qty_per_account (fill thật, quy book qua plan) + remaining_qty (vị thế broker)."""
    basket = set(ep.get("basket") or [])
    labels = _live_labels()
    ep["accounts"] = labels
    if not labels or not basket:
        ep["evidence_error"] = "không xác định được live accounts hoặc basket rỗng"
        return

    entry = ep["entry_signal_date"]
    # Ngày giao dịch từ entry trở đi (deploy thật rơi vào T+1 của ngày tín hiệu).
    days = [d for d in session_dates if entry <= d <= signal_date]

    qty_filled, qty_planned = {}, {}
    for lb in labels:
        f_acc, p_acc = {}, {}
        for d in days:
            for (tk, side), q in _plan_capit_orders(workdir, lb, d, basket).items():
                sgn = 1 if side == "buy" else -1
                p_acc[tk] = p_acc.get(tk, 0) + sgn * q
                fq = _filled_qty(workdir, lb, d, tk, side)
                if fq is not None:
                    f_acc[tk] = f_acc.get(tk, 0) + sgn * fq
        if p_acc:
            qty_planned[lb] = dict(sorted(p_acc.items()))
        if f_acc:
            qty_filled[lb] = dict(sorted(f_acc.items()))
    ep["qty_per_account"] = qty_filled          # field tên theo spec — giá trị = FILL THẬT
    ep["qty_per_account_planned"] = qty_planned
    # STICKY: đã từng quan sát được lệnh CAPIT khớp thật. Bắt buộc phải True trước khi cho phép
    # auto-close — nếu không, phiên gate fire (T) tự đóng episode ngay vì vị thế chưa giải ngân
    # (giải ngân rơi vào T+1). Đây là bug replay 07-20 bắt được.
    ep["deployed"] = bool(ep.get("deployed")) or bool(qty_filled)
    ep["qty_source"] = ("fill broker dnse_raw kind=orders (lọc account_label), quy book CAPIT "
                        "qua data/trade_plans/plan_*.json")

    # Vị thế còn lại (KHÔNG mang nhãn book — xem GIỚI HẠN ĐÃ BIẾT ở đầu file).
    remaining, snap_dates, missing = {}, [], []
    for lb in labels:
        qmap, snap_d = _positions_snapshot(workdir, lb, signal_date)
        if qmap is None:
            missing.append(lb)
            continue
        snap_dates.append(snap_d)
        rem = {t: int(qmap.get(t, 0)) for t in sorted(basket) if int(qmap.get(t, 0)) > 0}
        if rem:
            remaining[lb] = rem
    ep["remaining_qty_broker"] = remaining
    ep["remaining_qty_asof"] = min(snap_dates) if snap_dates else None
    ep["remaining_qty_note"] = ("vị thế broker KHÔNG mang nhãn book — số này là TỔNG mọi book "
                                "(PVT/SIP còn nằm trong custom30V parking), không phải riêng CAPIT")
    ep["evidence_error"] = (f"thiếu ảnh chụp vị thế cho: {missing}" if missing else None)


def _try_close(ep, signal_date, signal_today):
    """Auto-close CHỈ khi bằng chứng không thể nhầm: mọi mã trong rổ = 0 ở mọi account live,
    trên ảnh chụp vị thế còn tươi. Mọi trường hợp khác -> giữ mở (chiều an toàn)."""
    if ep.get("evidence_error") or not ep.get("accounts"):
        return
    if not ep.get("deployed"):
        # Chưa từng thấy lệnh CAPIT khớp: "vị thế = 0" nghĩa là CHƯA GIẢI NGÂN, không phải
        # ĐÃ THOÁT — không được đóng. Chỉ đóng khi gate đã tắt và đã đủ lâu mà vẫn không có
        # lệnh nào (episode chết yểu: gate fire nhưng người không mua).
        if (not signal_today) and (ep.get("sessions_held") or 0) >= NO_DEPLOY_CLOSE_SESSIONS:
            ep["status"] = "closed"
            ep["close_date"] = signal_date
            ep["close_reason"] = (f"không có lệnh CAPIT nào khớp trong "
                                  f"{ep.get('sessions_held')} phiên và gate đã tắt — episode "
                                  f"không được giải ngân")
        return
    asof = ep.get("remaining_qty_asof")
    if not asof:
        return
    try:
        age = (datetime.strptime(signal_date, "%Y-%m-%d") - datetime.strptime(asof, "%Y-%m-%d")).days
    except Exception:
        return
    if age > POSITIONS_MAX_AGE_DAYS:
        return
    if ep.get("remaining_qty_broker"):
        return
    ep["status"] = "closed"
    ep["close_date"] = signal_date
    ep["close_reason"] = (f"vị thế broker = 0 cho toàn bộ rổ ở mọi account live "
                          f"({', '.join(ep['accounts'])}), ảnh chụp {asof}")


# ────────────────────────────── API chính ──────────────────────────────
def _report(ep, stale=None):
    """Các field quan sát bơm vào status JSON."""
    return {
        "capit_episode_open": ep is not None,
        "capit_episode_id": ep["episode_id"] if ep else None,
        "capit_episode_entry_date": ep["entry_signal_date"] if ep else None,
        "capit_episode_basket": ep["basket"] if ep else [],
        "capit_episode_size": ep["size"] if ep else 0.0,
        "capit_sessions_held": ep.get("sessions_held") if ep else None,
        "capit_episode_remaining_qty": ep.get("remaining_qty_broker") if ep else {},
        "capit_episode_error": stale or (ep.get("evidence_error") if ep else None),
    }


def observe(ledger_path=None):
    """ĐỌC THUẦN sổ episode — không gọi broker, không ghi gì, không bao giờ raise.

    Cho consumer BÁO CÁO đọc trực tiếp khi status JSON chưa có key episode: file status là bản
    ghi của lần golive TRƯỚC (telegram_recommend chạy 18:00, golive 19:00), nên có một cửa sổ
    thật mà status còn là bản cũ trong khi sổ đã có episode đang mở.
    """
    try:
        return _report(_open_episode(_load(ledger_path or LEDGER_PATH)))
    except Exception as e:
        return {"capit_episode_open": None, "capit_episode_id": None,
                "capit_episode_entry_date": None, "capit_episode_basket": [],
                "capit_episode_size": 0.0, "capit_sessions_held": None,
                "capit_episode_remaining_qty": {},
                "capit_episode_error": f"{type(e).__name__}: {e}"}


def update(signal_date, signal_today, basket, size, session_dates,
           workdir=WORKDIR, ledger_path=None, write=True):
    """Cập nhật sổ episode và trả về các field quan sát cho status JSON.

    signal_date  : ngày tín hiệu (str YYYY-MM-DD)
    signal_today : cờ gate CỦA NGÀY CHẠY (capit_signal_today)
    basket / size: rổ + size của ngày chạy (chỉ dùng khi MỞ episode mới)
    session_dates: list ngày giao dịch (str YYYY-MM-DD) tăng dần — để đếm sessions_held

    KHÔNG bao giờ raise: đây là lớp quan sát, lỗi ở đây không được phép làm hỏng bản
    recommend. Lỗi -> trả về capit_episode_error và không đổi quyết định gì.
    """
    try:
        # Giải ở THỜI ĐIỂM GỌI (không dùng default arg) để harness A/B trỏ được sổ sang sandbox.
        ledger_path = ledger_path or LEDGER_PATH
        basket = sorted({str(t).upper() for t in (basket or [])})
        session_dates = sorted(str(d) for d in (session_dates or []))
        ledger = _load(ledger_path)
        ep = _open_episode(ledger)

        if ep is None and signal_today and basket:
            eid = f"CAPIT-{signal_date}"
            if not any(e.get("episode_id") == eid for e in ledger["episodes"]):
                ep = {"episode_id": eid, "entry_signal_date": signal_date,
                      "basket": basket, "size": round(float(size or 0), 4),
                      "status": "open", "opened_by": "golive_recommend_v23",
                      "note": ("rổ/size chốt tại phiên gate fire lần đầu; rổ được golive tính LẠI "
                               "mỗi ngày và co dần — sổ này giữ rổ GỐC lúc vào lệnh")}
                ledger["episodes"].append(ep)

        # Gọi với ngày CŨ HƠN lần cập nhật gần nhất = replay/chạy lại lệch thứ tự. Không được xử
        # lý: bằng chứng vị thế của ngày cũ (chưa giải ngân) sẽ đóng nhầm episode đang mở. Bug
        # thật bắt được khi chạy lại backfill lần 2 (07-13 đè lên sổ đã cập nhật tới 07-30).
        if ep is not None and (ep.get("last_update") or "") > signal_date:
            return _report(ep, stale=f"bỏ qua cập nhật lệch thứ tự: signal_date {signal_date} "
                                     f"cũ hơn last_update {ep['last_update']}")

        if ep is not None:
            entry = ep["entry_signal_date"]
            ep["sessions_held"] = sum(1 for d in session_dates if entry < d <= signal_date)
            ep["sessions_held_note"] = "số phiên giao dịch đã trôi qua KỂ TỪ SAU ngày tín hiệu vào"
            _refresh_evidence(ep, workdir, session_dates, signal_date)
            _try_close(ep, signal_date, signal_today)
            ep["last_update"] = signal_date

        ledger["updated_at"] = datetime.now().isoformat(timespec="seconds")
        if write:
            _save(ledger_path, ledger)

        return _report(_open_episode(ledger))
    except Exception as e:
        return {"capit_episode_open": None, "capit_episode_id": None,
                "capit_episode_entry_date": None, "capit_episode_basket": [],
                "capit_episode_size": 0.0, "capit_sessions_held": None,
                "capit_episode_remaining_qty": {},
                "capit_episode_error": f"{type(e).__name__}: {e}"}


def close(episode_id, note, ledger_path=LEDGER_PATH):
    """Đóng tay 1 episode (khi vị thế CAPIT đã thoát nhưng mã còn dư vì book khác giữ)."""
    ledger = _load(ledger_path)
    for ep in ledger["episodes"]:
        if ep.get("episode_id") == episode_id:
            if ep.get("status") == "closed":
                return f"{episode_id} đã đóng từ {ep.get('close_date')}"
            ep["status"] = "closed"
            ep["close_date"] = datetime.now().strftime("%Y-%m-%d")
            ep["close_reason"] = f"đóng TAY: {note}"
            _save(ledger_path, ledger)
            return f"{episode_id} -> closed ({note})"
    return f"không tìm thấy episode {episode_id}"


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Sổ episode CAPIT (quan sát thuần)")
    ap.add_argument("--show", action="store_true", help="in sổ hiện tại")
    ap.add_argument("--close", metavar="EPISODE_ID", help="đóng tay 1 episode")
    ap.add_argument("--note", default="", help="lý do đóng tay (bắt buộc khi --close)")
    a = ap.parse_args()
    if a.close:
        if not a.note:
            sys.exit("--close cần --note nêu rõ căn cứ (vị thế đã thoát ở đâu, ngày nào)")
        print(close(a.close, a.note))
    else:
        print(json.dumps(_load(LEDGER_PATH), ensure_ascii=False, indent=2))
