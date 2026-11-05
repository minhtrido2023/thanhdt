#!/usr/bin/env python3
"""Áp `plan["book_transfers"]` (GĐ3 clearing PARK→LAG) — chạy TRƯỚC bot_execute, KHÔNG sửa executor.

Thiết kế: `kb/projects/book-clearing-plan-20261029.md`; lõi dùng chung: `book_clearing.py`.
Mỗi transfer PLANNED, lần lượt:
  1. Đã có dòng journal BOOK_TRANSFER cùng id (mọi journal của account) ⇒ cùng nội dung: đánh dấu
     APPLIED (idempotent, chạy lại 13:00/autoheal không ghi lần 2); khác nội dung ⇒ PAUSE.
  2. Kiểm (fail ⇒ PAUSE, không đoán): schema + id đúng account/ngày · lệnh liên kết trong plan đúng
     `qty_after` (writer nào sửa plan sau clearing ⇒ lệch) · không excluded/BANNED/UNVERIFIED/lệch đối
     soát · PREFIX lô PARK (thứ tự trừ của LotBook.transfer) đủ T+2 phiên và không chạm lô CP quyền ·
     broker (DNSE sống — §6) sellable ≥ lượng chuyển · lệnh MUA đích qua đủ cổng book đích.
  3. Ghi 1 dòng BOOK_TRANSFER vào `exec_<acct>_<date>_journal.csv` (O_APPEND một lần write + fsync;
     KHÔNG tmp+replace: executor cũng append file này, thay cả file có thể nuốt dòng FILL của nó),
     đọc lại bằng chính parser của sổ lô, rồi mới đánh dấu APPLIED trong plan (atomic).
PAUSE = KHÔI PHỤC lệnh gốc của transfer đó (lệnh bị giảm trả qty gốc, lệnh bị gỡ trả lại vào orders[]
= đúng hành vi production khi không có clearing, fail-safe), transfer → PAUSED, báo bus. Lệnh khác
của account chạy bình thường.

§5 kill giữa chừng: journal là nguồn sự thật — ghi journal TRƯỚC, plan SAU; chạy lại thấy id trong
journal ⇒ chỉ đánh dấu APPLIED. Plan chưa duyệt / BOT_STOP ⇒ không làm gì (bot cũng không chạy).

rc: 0 = xong/không có gì · 3 = có transfer bị PAUSE (bot vẫn chạy phần còn lại) · 2 = lỗi nặng, KHÔNG
pause được ⇒ `book_transfers_gate.sh` (run_bot.sh + autoheal của bot_heartbeat.sh) KHÔNG chạy bot cho
account NẾU plan còn transfer chưa APPLIED/PAUSED (lệnh đã giảm mà không chuyển được nhãn = đoán);
plan không có transfer ⇒ rc≠0 chỉ cảnh báo, bot vẫn chạy.

Chỉ stdlib ở tầng 0: `book_clearing`/`wc_paths` import MUỘN (sau khi biết plan CÓ transfer) ⇒ lỗi import
không chặn account khi cờ clearing TẮT. Khoá `fcntl.flock` per-account (chạy tay + cron song song).

    python3 mike/bin/apply_book_transfers.py --account SpaceX [--date 2026-11-06] [--check]
"""
import argparse
import csv
import datetime as dt
import fcntl
import io
import json
import math
import os
import subprocess
import sys
import time
import traceback
from zoneinfo import ZoneInfo

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
ICT = ZoneInfo("Asia/Ho_Chi_Minh")   # §16
HEADER = ["ts", "event", "parent_id", "ticker", "side", "child_oid", "qty", "price",
          "filled_total", "book", "play_type", "note"]
RC_OK, RC_FATAL, RC_PAUSED = 0, 2, 3
LOCK_TIMEOUT_S = float(os.environ.get("APPLY_BT_LOCK_TIMEOUT", "120"))
BC = None   # book_clearing — import MUỘN (_late_imports), sau tầng 0 stdlib


def _wc_root():
    import wc_paths   # stdlib-only
    return wc_paths.find_wc_root(__file__)


def _late_imports():
    global BC
    if BC is None:
        import book_clearing as _bc
        BC = _bc


def now_ict():
    return dt.datetime.now(ICT)


def _atomic_write_json(path, obj):
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def append_journal_row(path, row):
    """Một lần os.write với O_APPEND (+ header nếu file chưa có). Từ chối (ValueError) nếu file có
    header CŨ 10 cột (thiếu `book`) hoặc dòng cuối dở dang — ghi tiếp sẽ làm lệch cột/dính dòng."""
    buf = io.StringIO()
    w = csv.writer(buf)          # cùng dialect executor (lineterminator \r\n)
    if os.path.exists(path) and os.path.getsize(path) > 0:
        with open(path, newline="", encoding="utf-8") as f:
            head = next(csv.reader(f), [])
        if head != HEADER:
            raise ValueError(f"journal {os.path.basename(path)} header {head} ≠ 12 cột chuẩn")
        with open(path, "rb") as f:
            f.seek(-1, os.SEEK_END)
            if f.read(1) != b"\n":
                raise ValueError(f"journal {os.path.basename(path)} dòng cuối chưa kết thúc")
    else:
        w.writerow(HEADER)
    w.writerow(row)
    data = buf.getvalue().encode("utf-8")
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        n = os.write(fd, data)
        if n != len(data):
            raise OSError(f"ghi journal thiếu byte ({n}/{len(data)})")
        os.fsync(fd)
    finally:
        os.close(fd)


def journal_index(ph, account, upto, exec_dir):
    """{id: [sig,...]} mọi dòng BOOK_TRANSFER của account (journal mọi ngày ≤ upto)."""
    idx = {}
    for path in ph.journal_files(account, "0000-00-00", upto, exec_dir):
        for ev in ph._book_transfers(path):
            idx.setdefault(ev["id"], []).append(
                None if ev["invalid"] else (ev["ticker"], ev["from_book"], ev["to_book"],
                                            ev["qty"], ev["price"]))
    return idx


def sig_of(x):
    return (x["ticker"], x["from_book"], x["to_book"], int(x["qty"]), float(x["ref_price"]))


def schema_problems(x, account, date):
    p = []
    try:
        q, px = x.get("qty"), float(x.get("ref_price"))
        if isinstance(q, bool) or not isinstance(q, int) or q <= 0:
            p.append(f"qty={q!r} không phải số nguyên dương")
        if not math.isfinite(px) or px <= 0:
            p.append(f"ref_price={px!r} không hợp lệ")
    except (TypeError, ValueError):
        p.append(f"ref_price={x.get('ref_price')!r} không phải số")
    if x.get("account") != account:
        p.append(f"account={x.get('account')!r} ≠ {account} (cấm chuyển chéo account)")
    if x.get("plan_date") != date:
        p.append(f"plan_date={x.get('plan_date')!r} ≠ ngày chạy {date}")
    if x.get("from_book") != BC.FROM_BOOK or x.get("to_book") not in BC.TO_BOOKS:
        p.append(f"sổ {x.get('from_book')}→{x.get('to_book')} ngoài phạm vi GĐ3 (chỉ PARK→LAG)")
    want = f"XFER-{account}-{date}-{x.get('ticker')}-{x.get('from_book')}-{x.get('to_book')}"
    if x.get("id") != want:
        p.append(f"id={x.get('id')!r} ≠ {want}")
    return p


def holdings_problems(x, h, used, banned, count_fn, date):
    """Kiểm sổ lô + broker cho transfer `x`; `used[tk]` = lượng PARK đã chuyển trước đó trong lượt
    này (2 sổ đích cùng mã) — prefix phải tính cộng dồn."""
    tk, m = x["ticker"], int(x["qty"])
    if tk in set(h.get("excluded_tickers") or []):
        return [f"{tk} thuộc excluded_tickers"]
    if tk in banned:
        return [f"{tk} BANNED"]
    if tk in set(h.get("unverified_tickers") or []):
        return [f"{tk} UNVERIFIED trong sổ lô"]
    bad = [mm for mm in (h.get("reconcile") or {}).get("mismatches") or [] if mm.get("ticker") == tk]
    if bad:
        return [f"{tk} lệch đối soát broker: {bad[0]}"]
    need = used.get(tk, 0) + m
    park = [l for l in h.get("lots") or [] if l["ticker"] == tk and l["book"] == BC.FROM_BOOK]
    if sum(l["qty"] for l in park) < need:
        return [f"sổ PARK {tk} có {sum(l['qty'] for l in park)}cp < cần {need}cp"]
    rem = need
    for l in park:
        if rem <= 0:
            break
        if l.get("rights_subscription"):
            return [f"prefix PARK {tk} chạm lô CP quyền mua"]
        n = count_fn(dt.date.fromisoformat(l["entry_date"]), dt.date.fromisoformat(date))
        if n is None:
            return ["không đếm được phiên (trading_bot.vn_market)"]
        if n < 2:
            return [f"lô PARK {tk} {l['entry_date']} mới {n} phiên (<T+2)"]
        rem -= l["qty"]
    pos = (h.get("broker_positions") or {}).get(tk) or {}
    sell = pos.get("sellable")
    if sell is None:
        return [f"broker không trả `sellable` cho {tk}"]
    if int(sell) < need:
        return [f"broker sellable {tk} {sell} < {need}"]
    return []


def notify_bus(kind, topic, payload):
    if os.environ.get("MIKE_BOT_TEST_MODE") == "1":     # §5b
        return
    try:
        subprocess.run([os.path.join(_HERE, "append_event.sh"), "Mafee", kind, topic,
                        json.dumps(payload, ensure_ascii=False)], timeout=30, check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"[apply_book_transfers] bus lỗi ({type(e).__name__}: {e})", file=sys.stderr)


def run(account, date, plan_path, plan, exec_dir, deps, check_only=False, bot_stop=None):
    """Trả (rc, plan_mới, log_lines). `deps` = dict callable: ph, holdings_fn(acct, date),
    banned_fn(), count_fn, gates_fn(plan, x, excluded), approval_fn(plan_dict) [, now_fn()]."""
    log = []
    now_fn = deps.get("now_fn") or now_ict
    if bot_stop is None:
        bot_stop = os.path.join(_wc_root(), "data", "BOT_STOP")
    if os.path.exists(bot_stop):
        return RC_OK, plan, ["BOT_STOP tồn tại ⇒ không áp transfer (bot cũng dừng)"]
    why = deps["approval_fn"](plan)
    xs = [x for x in plan.get("book_transfers") or [] if isinstance(x, dict)]
    pending = [x for x in xs if x.get("status") not in (BC.ST_APPLIED, BC.ST_PAUSED)]
    if pending and not why:
        # cổng bot (approval_block_reason) im lặng khi orders=[] — clearing có thể làm rỗng orders mà
        # transfer vẫn đòi ghi journal ⇒ chữ ký duyệt bắt buộc BẤT KỂ số lệnh
        why = BC.approval_problem(plan)
    if why:
        return RC_OK, plan, [f"plan chưa qua cổng duyệt ⇒ không áp transfer (để HOLD): {why}"]
    if not pending:
        return RC_OK, plan, [f"{len(xs)} transfer, không còn PLANNED"]
    ph = deps["ph"]
    jidx = journal_index(ph, account, date, exec_dir)
    h, h_err = None, None
    used, rc = {}, RC_OK
    jpath = os.path.join(exec_dir, f"exec_{account}_{date}_journal.csv")
    for x in pending:
        xid = x.get("id")
        probs = schema_problems(x, account, date)
        if not probs and now_fn().date().isoformat() != date:
            # ts dòng journal = ngày hiệu lực (entry_date lô đích) ⇒ chỉ áp ĐÚNG ngày plan_date
            probs = [f"hôm nay {now_fn().date()} ≠ plan_date {date} — chỉ áp đúng ngày thực thi"]
        if not probs and xid in jidx:
            if all(s == sig_of(x) for s in jidx[xid]):
                plan = BC.mark(plan, xid, BC.ST_APPLIED, applied_note="đã có trong journal (chạy lại)")
                used[x["ticker"]] = used.get(x["ticker"], 0) + int(x["qty"])
                log.append(f"{xid}: đã có trong journal ⇒ APPLIED (idempotent)")
                continue
            probs = [f"journal có id {xid} nhưng KHÁC nội dung {jidx[xid]} ≠ {sig_of(x)}"]
        if not probs:
            probs = BC.binding_problems(plan, x)
        if not probs:
            cwhy = BC.corp_action_problem(x["ticker"], BC.plan_asof(plan), date, deps.get("events_fn"))
            probs = [f"corp-action: {cwhy}"] if cwhy else []
        if not probs:
            if h is None and h_err is None:
                try:
                    h = deps["holdings_fn"](account, date)
                except BaseException as e:   # park_holdings dùng SystemExit cho lỗi dữ liệu
                    if isinstance(e, KeyboardInterrupt):
                        raise
                    h_err = f"sổ lô/broker không dựng được: {type(e).__name__}: {e}"
            probs = [h_err] if h_err else holdings_problems(
                x, h, used, deps["banned_fn"](), deps["count_fn"], date)
        if not probs:
            ok, gwhy = deps["gates_fn"](plan, x, set((h or {}).get("excluded_tickers") or []))
            if not ok:
                probs = [f"cổng book đích: {gwhy}"]
        if check_only:
            log.append(f"{xid}: {'OK' if not probs else 'SẼ PAUSE — ' + '; '.join(probs)}")
            if not probs:
                used[x["ticker"]] = used.get(x["ticker"], 0) + int(x["qty"])
            continue
        if probs:
            reason = "; ".join(probs)
            plan = BC.pause_transfer(plan, xid, reason, now_fn().isoformat(timespec="seconds"))
            _atomic_write_json(plan_path, plan)
            rc = RC_PAUSED
            log.append(f"⛔ {xid}: PAUSE (khôi phục lệnh gốc) — {reason}")
            notify_bus("error", "book-transfer-paused",
                       {"account": account, "plan_date": date, "transfer_id": xid,
                        "ticker": x.get("ticker"), "qty": x.get("qty"), "reason": reason,
                        "restored_order_ids": [r.get("id") for s in ("buy_orders", "sell_orders")
                                               for r in x.get(s) or []],
                        "measured_by": f"apply_book_transfers.py --account {account} --date {date}"})
            continue
        ts = now_fn().isoformat(timespec="seconds")
        row = [ts, "BOOK_TRANSFER", xid, x["ticker"], "transfer", xid, int(x["qty"]),
               float(x["ref_price"]), int(x["qty"]), x["to_book"], x.get("play_type") or "",
               f"from={x['from_book']};to={x['to_book']};src=apply_book_transfers"]
        append_journal_row(jpath, row)              # journal TRƯỚC (nguồn sự thật, §5)
        back = [ev for ev in ph._book_transfers(jpath) if ev["id"] == xid]
        if not back or back[-1]["invalid"] or (back[-1]["ticker"], back[-1]["from_book"],
                                                back[-1]["to_book"], back[-1]["qty"],
                                                back[-1]["price"]) != sig_of(x):
            raise RuntimeError(f"đọc lại journal không thấy {xid} hợp lệ: {back[-1:]}")
        plan = BC.mark(plan, xid, BC.ST_APPLIED, applied_at=ts)
        _atomic_write_json(plan_path, plan)
        used[x["ticker"]] = used.get(x["ticker"], 0) + int(x["qty"])
        log.append(f"✅ {xid}: chuyển nhãn {x['qty']}cp {x['ticker']} {x['from_book']}→{x['to_book']} "
                   f"@{float(x['ref_price']):,.0f} (journal {os.path.basename(jpath)})")
        notify_bus("status", "book-transfer-applied",
                   {"account": account, "plan_date": date, "transfer_id": xid, "ticker": x["ticker"],
                    "qty": x["qty"], "to_book": x["to_book"], "journal": jpath,
                    "measured_by": f"apply_book_transfers.py --account {account} --date {date}"})
    if not check_only:
        _atomic_write_json(plan_path, plan)        # lưu các đánh dấu APPLIED do idempotent
    return rc, plan, log


def emergency_pause_all(plan_path, reason, account, date, exec_dir):
    """Lỗi bất ngờ giữa chừng: transfer chưa APPLIED/PAUSED ⇒ nếu journal ĐÃ có dòng cùng id + cùng
    nội dung (chết sau khi ghi journal, trước khi lưu plan) ⇒ đánh dấu APPLIED (journal là sự thật,
    lệnh liên kết giữ nguyên); còn lại ⇒ PAUSE. PAUSE = KHÔI PHỤC lệnh GỐC (mua/bán qty gốc) rồi bot
    đặt lệnh như bình thường — KHÔNG phải "không đặt lệnh". Không đọc được journal (jidx=None) ⇒ PAUSE
    tất cả; nếu lúc đó dòng BOOK_TRANSFER ĐÃ ghi hợp lệ (chết sau journal, trước khi lưu plan + journal
    không đọc nổi) thì sổ ĐÃ chuyển mà lệnh gốc được khôi phục ⇒ có thể lệch nhãn PARK/LAG của m cp (tổng
    vị thế mã KHÔNG đổi, vì chuyển nhãn không chạm broker). Đây là khe hẹp CÒN LẠI, chưa loại bỏ; được
    giảm nhẹ vì (1) lỗi đọc journal ở đây hiếm, (2) log + bus ghi nguyên văn lý do, (3) sổ lô replay lại
    từ journal ở lần chạy sau nên lệch chỉ ở nhãn, tự lộ ở reconcile. Báo to cho người."""
    _late_imports()
    with open(plan_path, encoding="utf-8") as f:
        plan = json.load(f)
    try:
        import park_holdings as ph
        jidx = journal_index(ph, account, date, exec_dir)
    except Exception as e:
        jidx, reason = None, f"{reason} | journal không đọc được ({type(e).__name__}: {e})"
    t = now_ict().isoformat(timespec="seconds")
    for x in plan.get("book_transfers") or []:
        if not isinstance(x, dict) or x.get("status") in (BC.ST_APPLIED, BC.ST_PAUSED):
            continue
        try:
            done = jidx is not None and x.get("id") in jidx and all(s == sig_of(x) for s in jidx[x["id"]])
        except (KeyError, TypeError, ValueError):
            done = False
        plan = (BC.mark(plan, x["id"], BC.ST_APPLIED, applied_note="journal đã có (khôi phục sau lỗi)")
                if done else BC.pause_transfer(plan, x.get("id"), f"LỖI BẤT NGỜ: {reason}", t))
    _atomic_write_json(plan_path, plan)


def live_deps(account, date):
    import park_holdings as ph
    import clear_books as CB
    from portfolio_status import count_trading_days
    sys.path.insert(0, _wc_root())
    from trading_bot.plan import load_plan, approval_block_reason

    def approval_fn(plan):
        tp = load_plan(date, account=account)
        if tp is None:
            return "load_plan không đọc được plan"
        return approval_block_reason(tp)

    return {"ph": ph,
            "holdings_fn": lambda a, d: ph.park_holdings(a, asof=d, need_price=False),
            "banned_fn": CB.load_banned, "count_fn": count_trading_days,
            "gates_fn": BC.target_book_gates, "approval_fn": approval_fn, "events_fn": None}


def _read_plan(plan_path):
    with open(plan_path, encoding="utf-8") as f:
        return json.load(f)


class _Lock:
    """flock per-account trên file khoá riêng (chạy tay + cron/autoheal song song). Chờ tới
    LOCK_TIMEOUT_S giây; quá hạn ⇒ TimeoutError (caller trả RC_FATAL, KHÔNG chạy không khoá)."""

    def __init__(self, path, timeout=None):
        self.path, self.timeout = path, LOCK_TIMEOUT_S if timeout is None else timeout
        self.fd = None

    def __enter__(self):
        self.fd = os.open(self.path, os.O_WRONLY | os.O_CREAT, 0o644)
        end = time.monotonic() + self.timeout
        while True:
            try:
                fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return self
            except BlockingIOError:
                if time.monotonic() >= end:
                    os.close(self.fd)
                    self.fd = None
                    raise TimeoutError(f"không lấy được khoá {self.path} sau {self.timeout}s "
                                       "(tiến trình apply khác đang chạy)")
                time.sleep(0.2)

    def __exit__(self, *a):
        if self.fd is not None:
            os.close(self.fd)     # đóng fd = nhả flock


def main(argv=None):
    ap = argparse.ArgumentParser(description="Áp book_transfers của plan trước bot_execute")
    ap.add_argument("--account", required=True)
    ap.add_argument("--date", default=None, help="ngày thực thi (mặc định hôm nay ICT)")
    ap.add_argument("--plan-dir", default=None)
    ap.add_argument("--exec-dir", default=None)
    ap.add_argument("--check", action="store_true", help="chỉ kiểm, không ghi journal/plan")
    a = ap.parse_args(argv)
    date = a.date or now_ict().date().isoformat()
    try:
        wc = _wc_root() if not (a.plan_dir and a.exec_dir) else None
    except Exception as e:
        print(f"[apply_book_transfers] {a.account} {date}: không xác định được gốc WorkingClaude "
              f"({type(e).__name__}: {e})", file=sys.stderr)
        return RC_FATAL
    plan_dir = a.plan_dir or os.path.join(wc, "data", "trade_plans")
    exec_dir = a.exec_dir or os.path.join(wc, "data", "execution_logs")
    plan_path = os.path.join(plan_dir, f"plan_{a.account}_{date}.json")
    # Tầng 0 — chỉ stdlib: ngày thường không có transfer thì thoát trước mọi import nặng.
    if not os.path.exists(plan_path):
        print(f"[apply_book_transfers] {a.account} {date}: không có plan — không làm gì")
        return RC_OK
    try:
        plan = _read_plan(plan_path)
        xs = plan.get("book_transfers")
    except Exception as e:
        # plan hỏng thì bot_execute cũng không đọc được — không phải việc của bước này
        print(f"[apply_book_transfers] {a.account} {date}: plan không đọc được ({e}) — bỏ qua",
              file=sys.stderr)
        return RC_OK
    if not xs:
        print(f"[apply_book_transfers] {a.account} {date}: plan không có book_transfers — không làm gì")
        return RC_OK
    # Từ đây plan CÓ transfer ⇒ cần lõi + khoá. Lỗi import ⇒ RC_FATAL (gate quyết định theo transfer chờ).
    try:
        _late_imports()
    except Exception as e:
        print(f"[apply_book_transfers] {a.account} {date}: không import được book_clearing "
              f"({type(e).__name__}: {e}) — plan CÓ transfer ⇒ lỗi nặng", file=sys.stderr)
        return RC_FATAL
    try:
        lock = _Lock(os.path.join(plan_dir, f".apply_book_transfers_{a.account}.lock"))
        with lock:
            plan = _read_plan(plan_path)       # đọc lại TRONG khoá (tiến trình trước có thể đã áp)
            return _main_locked(a, date, plan_dir, exec_dir, plan_path, plan)
    except TimeoutError as e:
        print(f"[apply_book_transfers] {a.account} {date}: {e}", file=sys.stderr)
        return RC_FATAL


def _main_locked(a, date, plan_dir, exec_dir, plan_path, plan):
    try:
        rc, _, log = run(a.account, date, plan_path, plan, exec_dir, live_deps(a.account, date),
                         check_only=a.check)
        for line in log:
            print(f"[apply_book_transfers] {a.account} {date}: {line}")
        return rc
    except Exception as e:
        tb = traceback.format_exc()
        print(f"[apply_book_transfers] {a.account} {date}: LỖI BẤT NGỜ {type(e).__name__}: {e}\n{tb}",
              file=sys.stderr)
        if a.check:
            return RC_FATAL
        try:
            emergency_pause_all(plan_path, f"{type(e).__name__}: {e}", a.account, date, exec_dir)
        except Exception as e2:
            print(f"[apply_book_transfers] KHÔNG pause được: {type(e2).__name__}: {e2}", file=sys.stderr)
            notify_bus("error", "book-transfer-fatal",
                       {"account": a.account, "plan_date": date, "error": f"{type(e).__name__}: {e}",
                        "pause_error": f"{type(e2).__name__}: {e2}"})
            return RC_FATAL
        notify_bus("error", "book-transfer-paused",
                   {"account": a.account, "plan_date": date, "transfer_id": "ALL_PENDING",
                    "reason": f"lỗi bất ngờ {type(e).__name__}: {e}"})
        return RC_PAUSED


if __name__ == "__main__":
    sys.exit(main())
