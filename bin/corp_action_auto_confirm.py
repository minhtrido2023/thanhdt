#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tự động xác nhận sự kiện doanh nghiệp (BONUS_ISSUE / SPLIT) khi DNSE credit cổ phiếu.

VÒNG LẶP 5 LẦN (VHM, MBB, BID, VIX, MSB) đều cùng mẫu:
  corp_action_daily biết sự kiện từ sáng (07:30) qua upcoming_events_held (days_ahead=1),
  nhưng DNSE credit trước ex_date 1 phiên (~18:30–19:00 ICT), trong khi DollarBill xây plan
  tại 19:00–19:10. Kết quả: sổ lô ≠ broker → BLOCKED_RECONCILE cho mã đó.

Script này chạy lúc 19:30 ICT (sau khi DNSE credit, trước DollarBill) và tự CONFIRMED khi
đủ bằng chứng 2 nguồn ĐỘC LẬP:
  (1) upcoming_events_held có event ex ∈ [hôm nay, phiên giao dịch kế tiếp] (lịch VN thật — m6 r2)
  (2) Broker: openQuantity và costPrice đổi đúng hệ số trong ngày

⚠️ CHỈ xác nhận sự kiện LÀM TĂNG số lượng (BONUS_ISSUE / SPLIT). Cổ tức tiền mặt không đi qua
đây. Gộp cổ phiếu (reverse split) chưa thiết kế (qty_multiplier > 1 là điều kiện cứng trong corp_actions.py).

NHÁNH BROKER (user duyệt 2026-10-03, phương án B — feed vendor chết từ 2026-09-26, ca TPB):
sau nhánh vendor, `run_broker()` quét MỌI mã đang giữ bằng `corp_action_broker_detect` — KL +
tổng giá vốn + giá tham chiếu cùng kể một sự kiện, credit sau 15:00 ⇒ ex-date = phiên kế tiếp.
Công tắc `MIKE_CA_BROKER_SOURCE`:
  off    — không chạy nhánh broker (hành vi trước 2026-10-03; r3 thêm DUY NHẤT chốt I1 ở write_corp_actions).
  shadow — MẶC ĐỊNH: phát hiện + ghi sổ `data/corp_action_broker_ledger.jsonl` + 1 bus finding
           tóm tắt; KHÔNG ghi `data/corp_actions.json`, KHÔNG hỏi user.
  live   — BROKER LÀ NGUỒN CHÍNH (user nâng cấp 2026-10-03 23:08): nhánh broker chạy TRƯỚC và là
           nơi DUY NHẤT ghi — CONFIRMABLE ⇒ record CONFIRMED provenance=broker (validate() + atomic)
           BẤT KỂ vendor có sự kiện hay không; vendor chỉ đối chiếu (`vendor_check`): LỆCH (>1% hệ
           số / >1đ/cp / ex khác) ⇒ UNVERIFIED, KHÔNG ghi, bus question gọi tên Winston kèm CẢ HAI
           số; MƠ HỒ / CHƯA ĐỦ ⇒ question (1 lần / mã / phiên / verdict). Cổ tức tiền đã khớp
           cashDividendReceiving ⇒ finding (sổ không chứa cổ tức tiền). Nhánh vendor chạy SAU ở
           chế độ CHỈ-XÁC-NHẬN (`confirm_only`): không bao giờ ghi; lệch record broker ⇒ hỏi; vendor có
           sự kiện mà broker không thấy gì ⇒ hỏi (không im lặng, không tự ghi).
           r2 (2026-10-04): registry ĐÃ có (mã, ex) ⇒ đối chiếu record MỌI provenance với broker
           (trạng thái, hệ số, chân tiền nếu record khai) — lệch ⇒ UNVERIFIED + question Winston,
           KHÔNG ghi đè; ghi sự kiện KL TRƯỚC, sàng lọc chỉ-giá SAU trong ngân sách thời gian; record
           broker chưa được vendor xác nhận ⇒ đối chiếu lại SAU ex (`_reverify_broker_records`).
           r3 (2026-10-04, bảng bất biến ở agents/Taylor/research/broker-primary-20261004.md §r3):
           I1 ≤1 record HIỆU LỰC/(mã, ex) chốt ở ĐIỂM GHI (`_validate_for_write`, cả 2 writer) + trùng
           có sẵn ⇒ LỆCH + hỏi; I2 câu hỏi khi registry đã có record KHÔNG BAO GIỜ đề xuất record thứ
           hai (chỉ sửa/thu hồi); I3 chân tiền vắng = 0 như consumer đọc; I4 positions rỗng/cũ ⇒
           "không xác định", không "không giữ"; `_registry_sweep` (trùng + chờ/quá hạn credit).
  shadow/off giữ NGUYÊN nhánh vendor là bên ghi như trước (chưa được duyệt bật live); shadow chỉ
           ghi sổ quyết định broker-primary SẼ làm để người so sánh.
Sổ 2 pha (intent → tác dụng ngoài → done khi bus rc=0): kill/bus lỗi ⇒ lượt sau GỬI BÙ.
⚠️ Phụ thuộc NGẦM: nhánh broker chỉ đọc dnse_raw do tiến trình khác ghi (EOD/park/verify chạy
19:0x–19:1x); không có bản ghi positions nào sau credit ⇒ INSUFFICIENT/không thấy.
Bật `live` cần user duyệt sau khi xem cửa sổ shadow.

Chạy: python3 mike/bin/corp_action_auto_confirm.py [--dry-run] [--date YYYY-MM-DD]
"""
import argparse
import datetime as dt
import json
import math
import os
import sys

# ── Paths ──────────────────────────────────────────────────────────────────
MIKE_BIN = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, MIKE_BIN)
import wc_paths  # noqa: E402

WC_ROOT = wc_paths.find_wc_root(__file__)
MIKE_ROOT = os.path.join(WC_ROOT, "mike")

CORP_ACTIONS_FILE  = os.path.join(WC_ROOT, "data", "corp_actions.json")
CA_DAILY_DIR       = os.path.join(WC_ROOT, "data", "corp_action_daily")
EXEC_DIR           = os.path.join(WC_ROOT, "data", "execution_logs")

sys.path.insert(0, MIKE_ROOT)
import corp_actions as CA  # noqa: E402 — validate() tại điểm ghi, BLOCKER 1b arch-review vòng 8
import corp_action_broker_detect as BD  # noqa: E402 — nhánh broker (2026-10-03)
LEDGER_FILE = BD.LEDGER_FILE

# ── Constants ──────────────────────────────────────────────────────────────
RATIO_TOL       = 0.02   # ±2% chấp nhận giữa hệ số khai báo và hệ số suy từ broker
CONFIRMED_CODES = {"ISS", "SPLIT"}

APPEND_EVENT = os.path.join(MIKE_BIN, "append_event.sh")
NOTIFY_SH    = os.path.join(MIKE_BIN, "notify_thread.sh")


# ── Helpers ────────────────────────────────────────────────────────────────

def today_ict():
    from zoneinfo import ZoneInfo
    return dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date().isoformat()


def load_corp_actions_raw():
    """Đọc toàn bộ corp_actions.json, trả list thô. [] nếu file không tồn tại."""
    if not os.path.exists(CORP_ACTIONS_FILE):
        return []
    with open(CORP_ACTIONS_FILE, encoding="utf-8") as f:
        return json.load(f).get("actions") or []


def already_confirmed_set():
    """Tập (ticker.upper(), ex_date) đã có _status bắt đầu CONFIRMED."""
    out = set()
    for r in load_corp_actions_raw():
        if str(r.get("_status", "")).upper().startswith("CONFIRMED"):
            out.add((str(r.get("ticker", "")).upper(), str(r.get("ex_date", ""))[:10]))
    return out


def get_candidate_events(date_str):
    """Từ corp_action_daily_{date}.json → upcoming_events_held khớp điều kiện: sự kiện CP có ex
    trong [date_str, phiên giao dịch KẾ TIẾP] theo LỊCH GIAO DỊCH VN (`trading_bot.vn_market`) —
    broker có thể credit trong hôm nay. Bản cũ dùng `days_ahead ≤ 1` NGÀY LỊCH ⇒ credit thứ Sáu,
    ex thứ Hai (days_ahead=3) / qua kỳ nghỉ lễ bị bỏ sót (m6)."""
    from trading_bot.vn_market import next_trading_day
    path = os.path.join(CA_DAILY_DIR, f"corp_action_daily_{date_str}.json")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    held = d.get("upcoming_events_held") or []
    last = next_trading_day(dt.date.fromisoformat(date_str)).isoformat()
    out = []
    for ev in held:
        if not (ev.get("price_adjusting") and ev.get("event_code") in CONFIRMED_CODES):
            continue
        ex = str(ev.get("date") or "")[:10]
        try:
            dt.date.fromisoformat(ex)
        except ValueError:      # §29: nói ra, không lặng lẽ bỏ
            print(f"  [{ev.get('ticker')}] sự kiện vendor {ev.get('event_code')} có ngày không đọc được "
                  f"{ev.get('date')!r} ⇒ không xét")
            continue
        if date_str <= ex <= last:
            out.append(ev)
    return out


def _get_ticker_snapshots(account_no, ticker, date_str):
    """Đọc tất cả bản ghi positions cho (account_no, ticker) từ dnse_raw_{date}.jsonl.

    Trả (first_rec, last_rec) — rec là dict position của DNSE, có openQuantity / costPrice.
    Trả (None, None) nếu không có bản ghi nào.
    """
    path = os.path.join(EXEC_DIR, f"dnse_raw_{date_str}.jsonl")
    if not os.path.exists(path):
        return None, None

    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if str(d.get("account_no")) != str(account_no):  # §12
                continue
            if d.get("kind") != "positions":
                continue
            ts = d.get("ts") or ""
            positions = d.get("payload", {}).get("positions") or []
            for p in positions:
                if p.get("symbol") == ticker and str(p.get("accountNo")) == str(account_no):
                    records.append((ts, p))
                    break  # chỉ 1 bản ghi / snapshot / ticker

    if not records:
        return None, None
    records.sort(key=lambda x: x[0])
    return records[0][1], records[-1][1]


def _get_account_nos(date_str):
    """Đọc danh sách account_no từ dnse_raw_{date}.jsonl."""
    path = os.path.join(EXEC_DIR, f"dnse_raw_{date_str}.jsonl")
    if not os.path.exists(path):
        return []
    seen = {}  # account_no → account_label
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            ano = d.get("account_no")
            lbl = d.get("account_label") or ano
            if ano and ano not in seen:
                seen[ano] = lbl
    return list(seen.items())  # [(account_no, label), ...]


def check_ratio(first_rec, last_rec, expected_mult, tol=RATIO_TOL):
    """So hệ số thực tế với hệ số khai báo. Trả (ok, actual_qty_ratio, actual_cost_ratio).

    expected_mult = 1.2 với tỉ lệ thưởng 20%.
    """
    qty_before = int(first_rec.get("openQuantity") or 0)
    qty_after  = int(last_rec.get("openQuantity") or 0)
    cost_before = float(first_rec.get("costPrice") or 0)
    cost_after  = float(last_rec.get("costPrice") or 0)

    if qty_before <= 0 or qty_after <= qty_before or cost_after <= 0:
        return False, None, None

    actual_qty  = qty_after / qty_before
    actual_cost = cost_before / cost_after if cost_after > 0 else 0

    qty_ok  = abs(actual_qty  - expected_mult) <= tol * expected_mult
    cost_ok = abs(actual_cost - expected_mult) <= tol * expected_mult
    return (qty_ok and cost_ok), round(actual_qty, 4), round(actual_cost, 4)


def broker_modified_today(last_rec, today_str):
    """True nếu modifiedDate của record là hôm nay ICT (broker credit hôm nay)."""
    md = str(last_rec.get("modifiedDate") or "")
    # modifiedDate là UTC (Z suffix), quy về ICT (+7)
    if not md:
        return False
    try:
        from zoneinfo import ZoneInfo
        ts_utc = dt.datetime.fromisoformat(md.replace("Z", "+00:00"))
        ts_ict = ts_utc.astimezone(ZoneInfo("Asia/Ho_Chi_Minh"))
        return ts_ict.date().isoformat() == today_str
    except Exception:
        # fallback: so chuỗi thô (UTC date)
        return md[:10] == today_str


def write_corp_actions(actions_list, dry_run=False):
    """Ghi lại corp_actions.json với list actions mới. Atomic tmp+rename.

    BLOCKER 1b (arch-review vòng 8): validate() TỪNG record trước khi ghi — writer này là điểm
    duy nhất tạo record CONFIRMED tự động, không đi qua ai review tay. Một record vượt biên
    QTY_MULT_MAX (lỗi gõ tay ở `exercise_ratio` nguồn, hoặc bug tính `mult`) mà lọt vào registry
    sẽ làm MỌI consumer khác (park_holdings, verify_account_snapshot, reconcile_equity) ném
    CorpActionError cho TOÀN BỘ ticker trong file, không riêng ticker hỏng — validate ở đây chặn
    trước khi file bị đầu độc, thay vì để 3 consumer khác nhau tự phát hiện sau.
    r3 (I1): cùng chốt kiểm bất biến ≤1 record HIỆU LỰC/(mã, ex) — lượt này tạo nhóm trùng (vd lịch
    vendor ghi lặp 1 sự kiện ⇒ 2 ứng viên cùng (mã, ex) trong 1 lượt) ⇒ CorpActionError, 0 ghi.
    """
    _validate_for_write(actions_list, load_corp_actions_raw())
    if dry_run:
        print(f"[DRY-RUN] would write {len(actions_list)} records to {CORP_ACTIONS_FILE}")
        return
    data = {"actions": actions_list}
    tmp = CORP_ACTIONS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, CORP_ACTIONS_FILE)


def post_bus(ticker, event_id, ex_date, multiplier, acct_evidence, dry_run=False):
    """Ghi bus finding và notify Discord."""
    import subprocess
    summary = (f"AUTO-CONFIRMED {ticker} {event_id}: ×{multiplier} (ex {ex_date}), "
               f"broker evidence: {acct_evidence}")
    payload = json.dumps({
        "status": "AUTO_CONFIRMED",
        "event_id": event_id,
        "ticker": ticker,
        "qty_multiplier": multiplier,
        "ex_date": ex_date,
        "broker_evidence": acct_evidence,
        "decided_by": "agent",
        "note": "auto-confirmed by corp_action_auto_confirm.py (2-source rule)"
    }, ensure_ascii=False)
    if dry_run:
        print(f"[DRY-RUN] bus finding: {summary}")
        return

    # Append bus event
    subprocess.run(
        [APPEND_EVENT, "Mike", "finding", f"corp-action-auto-confirm-{ticker}", payload],
        check=False
    )

    # Discord notify
    thread_id = os.environ.get("DISCORD_THREAD_ID", "")
    if thread_id and os.path.exists(NOTIFY_SH):
        msg = (f"✅ **Corp Action AUTO-CONFIRMED** — **{ticker}** ×{multiplier} "
               f"(ex {ex_date}): broker credit xác nhận, sổ lô tự đồng bộ, "
               f"DollarBill sẽ build plan sạch.")
        subprocess.run([NOTIFY_SH, msg, thread_id], check=False)


# ── Main ───────────────────────────────────────────────────────────────────

def run(date_str, dry_run=False):
    mode = broker_mode()
    if mode == "off":
        return run_vendor(date_str, dry_run=dry_run)
    if not dry_run:
        _sandbox_guard()
    # Khoá bao CẢ nhánh vendor: hai nhánh cùng đọc-sửa-ghi data/corp_actions.json; cron + chạy tay
    # song song không được đè record của nhau (arch-review v2 N3). off ⇒ không khoá (như cũ).
    lk = None if dry_run else _lock(LEDGER_FILE)
    if not dry_run and lk is None:
        print(f"❌ không lấy được khoá {LEDGER_FILE}.lock sau {LOCK_WAIT_S}s — tiến trình khác đang "
              f"chạy; KHÔNG chạy nhánh nào.")
        _ask_lock_unavailable(date_str, mode)
        return 1
    global _LOCK_HELD
    _LOCK_HELD = lk is not None   # cả đời run(): 2 nhánh dùng chung khoá này, run_broker không xin lại
    try:
        return _run_both(date_str, dry_run, mode)
    finally:
        _LOCK_HELD = False
        if lk:
            lk.close()


def _run_branch(name, fn, date_str, dry_run, mode):
    """Chạy MỘT nhánh (vendor / broker) độc lập với nhánh kia: nhánh nổ ⇒ in traceback + bus
    `question` urgency high 1 lần/ngày (r5 M-B: `error` không được ops_health_check leo thang,
    rc bị bỏ qua — cùng lớp #3 vòng 4) + rc=1, nhánh còn lại VẪN chạy (r5 M-C: hai nhánh đọc
    nguồn khác nhau, chỉ chung khoá + registry; vendor nổ không có lý do làm mất lượt broker).
    SandboxMismatch KHÔNG bị nuốt (đang trỏ lệch production ⇒ dừng hẳn)."""
    try:
        return fn()
    except SandboxMismatch:
        raise
    except Exception as e:   # crash nhánh KHÔNG được chỉ nằm trong log cron (§29: lỗi thật)
        import traceback
        tb = traceback.format_exc()
        print(tb)
        if not dry_run:
            _ask_day_once(f"{name}crash", date_str, f"corp-action-{name}-crash-{date_str}",
                          {"question": (f"Nhánh {name} của corp_action_auto_confirm NỔ lượt {date_str} "
                                        f"({type(e).__name__}: {e}) — nhánh còn lại vẫn chạy độc lập. "
                                        f"Cần người đọc log cron và chạy lại tay --date {date_str}."),
                           "error": f"{type(e).__name__}: {e}", "traceback_tail": tb[-1500:],
                           "mode": mode, "urgency": "high"})
        return 1


def _run_both(date_str, dry_run, mode):
    if mode == "live":
        # Broker là nguồn chính ⇒ ghi TRƯỚC; vendor sau, chỉ xác nhận (không bao giờ ghi).
        rc_b = _run_branch("broker", lambda: run_broker(date_str, dry_run=dry_run, mode=mode),
                           date_str, dry_run, mode)
        rc = _run_branch("vendor", lambda: run_vendor(date_str, dry_run=dry_run, confirm_only=True),
                         date_str, dry_run, mode)
        return rc_b or rc
    rc = _run_branch("vendor", lambda: run_vendor(date_str, dry_run=dry_run),
                     date_str, dry_run, mode)
    rc_b = _run_branch("broker", lambda: run_broker(date_str, dry_run=dry_run, mode=mode),
                       date_str, dry_run, mode)
    return rc or rc_b


def run_vendor(date_str, dry_run=False, confirm_only=False):
    """Nhánh vendor. `confirm_only` (live, broker-primary) ⇒ KHÔNG ghi registry, chỉ đối chiếu/hỏi. Lỗi ở đường hỏi người (N9 / tỉ lệ lệch broker) KHÔNG được làm mất lô vendor
    (arch-review v4 #6: bản cũ để ngoại lệ ledger_append/_bus thoát ⇒ mất cả lô, 0 bus event):
    gom lỗi, chạy hết lô, rồi báo 1 bus question (urgency high) + rc=1."""
    ask_failed = []
    rc = _run_vendor(date_str, dry_run, ask_failed, confirm_only)
    if ask_failed:
        print(f"  ❌ {len(ask_failed)} lần hỏi người lỗi trong nhánh vendor: {ask_failed}")
        try:
            _bus("question", f"corp-action-vendor-ask-failed-{date_str}",
                 {"question": (f"Nhánh vendor KHÔNG gửi được câu hỏi đối chiếu record broker "
                               f"({len(ask_failed)} mục) — lô vendor vẫn chạy hết. Cần người kiểm "
                               f"tay các mã dưới đây trong data/corp_actions.json."),
                  "failed": ask_failed, "urgency": "high"})
        except Exception as e:  # §29: kênh báo lỗi cũng hỏng ⇒ chỉ còn log cron, nói thật
            print(f"  ❌ không gửi được cả bus question báo lỗi: {type(e).__name__}: {e}")
        rc = 1
    return rc


def _ask_guarded(failed, fn, *args):
    """Gọi 1 hàm hỏi người; lỗi (trừ SandboxMismatch) ⇒ in traceback + ghi vào `failed`, không ném."""
    try:
        fn(*args)
    except SandboxMismatch:
        raise
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        failed.append({"call": fn.__name__, "ticker": args[0], "ex_date": args[1],
                       "error": f"{type(e).__name__}: {e}"})


def _run_vendor(date_str, dry_run, ask_failed, confirm_only=False):
    print(f"[corp_action_auto_confirm] date={date_str} dry_run={dry_run} confirm_only={confirm_only}")

    candidates = get_candidate_events(date_str)
    if not candidates:
        print("  → không có sự kiện nào trong upcoming_events_held cần kiểm.")
        return 0
    if confirm_only:
        return _vendor_confirm_only(date_str, dry_run, ask_failed, candidates)

    confirmed_set = already_confirmed_set()
    accounts = _get_account_nos(date_str)
    if not accounts:
        print(f"  → không đọc được account_no từ dnse_raw_{date_str}.jsonl.")
        return 1

    print(f"  {len(candidates)} candidate event(s), {len(accounts)} account(s): "
          f"{[a for _, a in accounts]}")

    new_confirms = []
    pending_bus_posts = []   # B-4 arch-review vòng 9: post_bus() BỊ DỜI ra sau write thành công —
                              # bản cũ post_bus() TRƯỚC write_corp_actions() nên trên đường bị
                              # reject (validate() ném CorpActionError) Discord/bus vẫn hiện
                              # "✅ AUTO-CONFIRMED" dù registry KHÔNG hề được ghi (tự mâu thuẫn
                              # artifact-vs-thực-tế, MIKE.md quy chuẩn #2).
    actions_raw = load_corp_actions_raw()
    old_count = len(actions_raw)   # B-3: mốc phân biệt record CŨ (đã có trước lượt này) vs MỚI

    for ev in candidates:
        ticker   = ev.get("ticker", "").upper()
        ex_date  = str(ev.get("date") or "")[:10]
        ratio    = float(ev.get("exercise_ratio") or 0)
        if ratio <= 0:
            print(f"  [{ticker}] skip: exercise_ratio={ratio} không hợp lệ")
            continue
        mult = 1.0 + ratio

        if (ticker, ex_date) in confirmed_set:
            _bratio = _broker_record_ratio_diff(actions_raw, ticker, ex_date, mult)
            if _bratio:
                # arch-review v4 #12: CÙNG ex nhưng vendor khai tỉ lệ khác record broker — bản cũ
                # im lặng "đã CONFIRMED rồi". Không ghi gì (record đã có), hỏi người đối chiếu.
                print(f"  [{ticker}] ⚠ WARNING {_bratio[0]} — cần người đối chiếu tỉ lệ.")
                if not dry_run:
                    _ask_guarded(ask_failed, _ask_ratio_vs_broker, ticker, ex_date, *_bratio)
            else:
                print(f"  [{ticker}] đã CONFIRMED rồi — bỏ qua.")
            continue
        _bdup = _broker_record_near(actions_raw, ticker, ex_date)
        if _bdup:
            # Chỉ chạm tới được khi registry có record provenance=broker (từ 2026-10-03) — mọi
            # registry cũ đi đúng đường cũ. Vendor sống lại với ex ≠ ex broker suy ra ⇒ ghi thêm
            # là áp hệ số 2 lần (arch-review v2 N9) ⇒ không ghi, hỏi người.
            print(f"  [{ticker}] ❌ {_bdup[0]} — không tự xác nhận, cần người kiểm.")
            if not dry_run:
                _ask_guarded(ask_failed, _ask_vendor_vs_broker, ticker, ex_date, *_bdup)
            continue

        print(f"  [{ticker}] ex_date={ex_date}, ratio={ratio} (×{mult}) — kiểm broker ...")

        acct_results = {}
        for acct_no, acct_lbl in accounts:
            first, last = _get_ticker_snapshots(acct_no, ticker, date_str)
            if first is None:
                # account không giữ ticker này
                continue
            if not broker_modified_today(last, date_str):
                # broker chưa credit hôm nay cho ticker này
                acct_results[acct_lbl] = {
                    "verdict": "NOT_MODIFIED_TODAY",
                    "qty_before": first.get("openQuantity"),
                    "qty_after": last.get("openQuantity"),
                }
                continue
            ok, qty_r, cost_r = check_ratio(first, last, mult)
            acct_results[acct_lbl] = {
                "verdict": "MATCH" if ok else "MISMATCH",
                "qty_before": int(first.get("openQuantity") or 0),
                "qty_after":  int(last.get("openQuantity") or 0),
                "qty_ratio":  qty_r,
                "cost_ratio": cost_r,
                "modified_today": True,
            }

        print(f"  [{ticker}] broker results: {acct_results}")

        if not acct_results:
            print(f"  [{ticker}] không account nào giữ mã này → CANNOT_VERIFY, bỏ qua.")
            continue

        any_mismatch = any(v["verdict"] == "MISMATCH" for v in acct_results.values())
        has_match    = any(v["verdict"] == "MATCH"    for v in acct_results.values())

        if any_mismatch:
            print(f"  [{ticker}] ❌ MISMATCH — không tự xác nhận, cần người kiểm.")
            continue
        if not has_match:
            print(f"  [{ticker}] broker chưa credit hôm nay → bỏ qua.")
            continue

        # ── ĐỦ ĐIỀU KIỆN: tự CONFIRMED ─────────────────────────────────
        event_id = f"{ticker}-{ex_date}-BONUS-ISSUE"
        from zoneinfo import ZoneInfo
        now_ict = dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%dT%H:%M:%S+07:00")

        ev_code = ev.get("event_code", "ISS")
        ev_type = "BONUS_ISSUE" if ev_code == "ISS" else "SPLIT"

        new_rec = {
            "id": event_id,
            "ticker": ticker,
            "event_type": ev_type,
            "ratio_text": ev.get("title", f"tỉ lệ {ratio*100:.0f}%"),
            "qty_multiplier": mult,
            "ex_date": ex_date,
            "record_date": ev.get("record_date"),
            "broker_effective_ts": f"{date_str}T00:00:00",  # placeholder; refined below
            "_status": (f"CONFIRMED — corp_action_auto_confirm.py {now_ict} "
                        f"(2-source: upcoming_events_held + broker qty/cost ratio match). "
                        f"Thu hồi: đổi _status thành 'REVOKED ...'"),
            "confirmed_by": "corp_action_auto_confirm.py (agent)",
            "decided_by": "agent",
            "confirmed_at": now_ict,
            "evidence": [
                (f"NGUỒN 1 — corp_action_daily {date_str} upcoming_events_held: "
                 f"ticker={ticker}, event_code={ev_code}, date={ex_date}, "
                 f"exercise_ratio={ratio}, price_adjusting=True, days_ahead={ev.get('days_ahead')}"),
            ] + [
                (f"NGUỒN 2 — broker {lbl}: qty {r['qty_before']}→{r['qty_after']} "
                 f"(×{r.get('qty_ratio')}), costPrice ratio ×{r.get('cost_ratio')}, "
                 f"modified_today=True")
                for lbl, r in acct_results.items() if r["verdict"] == "MATCH"
            ],
            "verify_against_bq": f"PENDING — chạy sau {ex_date}: "
                                  f"python3 mike/bin/corp_actions.py --verify {event_id}",
            "note": "Cùng mẫu broker credit 1 phiên trước ex_date như VHM/MBB/BID/VIX/MSB.",
        }

        # Refine broker_effective_ts từ modifiedDate account khớp đầu tiên
        for lbl, r in acct_results.items():
            if r["verdict"] == "MATCH":
                for acct_no, albl in accounts:
                    if albl == lbl:
                        _, last = _get_ticker_snapshots(acct_no, ticker, date_str)
                        if last and last.get("modifiedDate"):
                            # modifiedDate là UTC → bỏ .Z suffix
                            new_rec["broker_effective_ts"] = last["modifiedDate"].replace("Z", "")
                        break
                break

        print(f"  [{ticker}] ✅ AUTO-CONFIRMED ×{mult} (ex {ex_date})")
        if dry_run:
            print(f"  [DRY-RUN] new record: {json.dumps(new_rec, ensure_ascii=False)[:300]}")

        actions_raw.append(new_rec)
        new_confirms.append((ticker, event_id))
        pending_bus_posts.append((ticker, event_id, ex_date, mult, acct_results))

    if new_confirms:
        try:
            write_corp_actions(actions_raw, dry_run=dry_run)
        except CA.CorpActionError as e:
            # B-3 arch-review vòng 9: write_corp_actions() validate() TOÀN BỘ registry (record
            # CŨ + MỚI), nhưng bản cũ luôn quy kết "record vừa tạo" và trỏ candidates=CANDIDATE
            # MỚI — SAI khi record hỏng là record CŨ đã tồn tại từ TRƯỚC lượt này (vd VHM index 0
            # hỏng sẵn), khiến người xử lý đi kiểm nhầm candidate mới trong khi thủ phạm thật là
            # record cũ (và nếu vậy thì park_holdings/verify_account_snapshot/reconcile_equity
            # CŨNG đang bị chặn đồng thời — thông tin quan trọng bị mất nếu quy kết sai).
            import re
            m = re.search(r"corp_actions\[(\d+)\]", str(e))
            bad_idx = int(m.group(1)) if m else None
            new_tickers = [t for t, _ in new_confirms]
            # R9-4 arch-review vòng 10: write_corp_actions() → validate() DỪNG ở record hỏng
            # ĐẦU TIÊN gặp phải (không kiểm hết toàn bộ list) — khi record hỏng là record CŨ
            # (index < old_count), các candidate MỚI của lượt này CHƯA HỀ được validate() đọc
            # tới, nên không có bằng chứng để khẳng định chúng "không phải" thủ phạm hay
            # "chắc chắn lành". Chỉ nói điều ĐÃ ĐỌC được.
            bad_is_preexisting = bad_idx is not None and bad_idx < old_count
            bad_ticker = (actions_raw[bad_idx].get("ticker") if bad_idx is not None
                          and 0 <= bad_idx < len(actions_raw) else None)
            bad_label = f"{bad_ticker} (index {bad_idx})" if bad_ticker else f"index {bad_idx}"
            if bad_is_preexisting:
                print(f"\n❌ KHÔNG GHI — record cũ {bad_label}, đã tồn tại TỪ TRƯỚC lượt này, "
                      f"không qua validate(): {e}\n"
                      f"   ⚠ Registry đã hỏng TỪ TRƯỚC — mọi consumer khác "
                      f"(park_holdings/verify_account_snapshot/reconcile_equity) CŨNG đang bị "
                      f"chặn bởi CHÍNH record này.")
                note = (f"registry đã có record HỎNG TỪ TRƯỚC lượt chạy này ({bad_label}). "
                        f"validate() dừng ở record hỏng ĐẦU TIÊN nên các candidate mới của lượt "
                        f"này ({new_tickers}) CHƯA được kiểm tra — không khẳng định chúng có hỏng "
                        f"hay không. Mọi consumer khác "
                        f"(park_holdings/verify_account_snapshot/reconcile_equity) cũng đang bị "
                        f"chặn bởi cùng record cũ này — cần sửa/REVOKE record cũ trước, rồi chạy "
                        f"lại để biết candidate mới có qua được validate() hay không.")
                candidates_payload = []
            elif bad_idx is not None:
                print(f"\n❌ KHÔNG GHI — record vừa tạo {bad_label} không qua validate(): {e}")
                note = ("auto_confirm tạo record hỏng, KHÔNG ghi vào registry — cần người kiểm tay")
                candidates_payload = new_tickers
            else:
                # Không parse được index từ message lỗi — không đủ bằng chứng để nói "cũ" hay
                # "mới", tránh suy diễn.
                print(f"\n❌ KHÔNG GHI — không xác định được record nào hỏng từ message lỗi "
                      f"validate(): {e}")
                note = (f"validate() báo lỗi nhưng không parse được index record hỏng từ message "
                        f"({e!r}) — không xác định được record cũ hay candidate mới ({new_tickers}) "
                        f"là thủ phạm, cần kiểm tay toàn bộ registry.")
                candidates_payload = new_tickers
            import subprocess
            subprocess.run(
                [APPEND_EVENT, "Mike", "question",
                 "corp-action-auto-confirm-validate-reject",
                 json.dumps({"error": str(e), "bad_record_index": bad_idx,
                             "bad_record_is_preexisting": bad_is_preexisting,
                             "candidates": candidates_payload,
                             "urgency": "high", "note": note}, ensure_ascii=False)],
                check=False)
            # B-4: KHÔNG post_bus() ở đây — pending_bus_posts chưa hề được gửi (bị dời ra sau
            # write thành công) nên không có gì cần rút lại; "✅ AUTO-CONFIRMED" sẽ KHÔNG BAO GIỜ
            # xuất hiện trên đường reject.
            return 1
        for ticker, event_id, ex_date, mult, acct_results in pending_bus_posts:
            post_bus(ticker, event_id, ex_date, mult, acct_results, dry_run=dry_run)
        print(f"\nXong: {len(new_confirms)} event(s) AUTO-CONFIRMED: "
              f"{[t for t, _ in new_confirms]}")
    else:
        print("Xong: không có event mới nào đủ điều kiện tự xác nhận.")

    return 0


def _vendor_confirm_only(date_str, dry_run, ask_failed, candidates):
    """LIVE broker-primary: nhánh vendor KHÔNG BAO GIỜ ghi registry. Mỗi sự kiện CP vendor sắp ex:
      · registry đã có (mã, ex) — record MỌI provenance (người ký / broker / vendor cũ) — đối chiếu
        `_record_vs_vendor`: record chưa CONFIRMED, hệ số lệch >1%, chân tiền record khai lệch DIV
        vendor cùng ex ⇒ hỏi (không đè); khớp ⇒ in CẢ HAI số đã so (RC1);
      · record broker ĐANG CONFIRMED cùng mã ở ex KHÁC gần đó ⇒ hỏi (N9);
      · nhánh broker đã có mục sổ cho mã ở phiên này (đã ghi/hỏi theo verdict của nó) ⇒ thôi;
      · còn lại, mã đang giữ theo `BD.held_tickers` (bản ghi positions khác rỗng cuối mỗi tài khoản,
        RC2/M3/m5) ⇒ vendor có sự kiện mà sổ broker không có mục ⇒ hỏi. Có tài khoản KHÔNG xác định
        được (không file nào / positions rỗng / file cũ) mà mã không nằm ở tài khoản đã biết ⇒ hỏi
        INSUFFICIENT (I4: vắng mặt ≠ không giữ). Chỉ "không giữ" khi MỌI tài khoản đã biết xác định.
    Registry khớp vendor ⇒ in trạng thái credit broker (`_credit_state`, m1); hỏi QUÁ HẠN do
    `_registry_sweep` của nhánh broker lo (1 nơi hỏi). Sổ broker đọc hỏng ⇒ coi như broker chưa thấy
    (hỏi thừa an toàn hơn im)."""
    actions_raw = load_corp_actions_raw()
    reg = _registry_view(actions_raw)
    ledger_note = "sổ broker đọc được"
    try:
        intents, _done = BD.ledger_state(LEDGER_FILE)
    except BD.CorpActionLedgerError as e:       # §29: nói lỗi thật
        print(f"  ⚠ sổ broker đọc hỏng ({e}) ⇒ coi như nhánh broker chưa thấy mã nào")
        intents = {}
        ledger_note = f"sổ broker ĐỌC HỎNG ({e}) — không biết nhánh broker đã thấy gì"
    broker_seen = {e.get("ticker") for e in intents.values()
                   if e.get("mode") == "live" and e.get("credit_day") == date_str}
    hi = BD.held_tickers(date_str, EXEC_DIR)
    held, unknown = hi if hi is not None else (None, None)
    vfn = _vendor_events_fn(date_str)
    for ev in candidates:
        ticker = ev.get("ticker", "").upper()
        ex_date = str(ev.get("date") or "")[:10]
        try:
            ratio = float(ev.get("exercise_ratio") or 0)
        except (TypeError, ValueError):
            ratio = 0.0
        mult = 1.0 + ratio
        if (ticker, ex_date) in reg:
            vev = vfn(ticker)
            vcash = (None if vev == BD.VENDOR_UNREADABLE else
                     [e.get("value_per_share") for e in BD.dedup_vendor(vev)
                      if str(e.get("event_code") or "").upper() == "DIV"
                      and str(e.get("date") or "")[:10] == ex_date])
            ok, why, rid = _record_vs_vendor(reg[(ticker, ex_date)], mult, vcash)
            if not ok:
                print(f"  [{ticker}] ⚠ {why} — registry giữ nguyên, hỏi người.")
                if not dry_run:
                    _ask_guarded(ask_failed, _ask_registry_vs_vendor, ticker, ex_date, why, rid)
            else:
                print(f"  [{ticker}] registry ({ticker}, {ex_date}) {why}; credit broker: "
                      f"{_credit_state(ticker, ex_date, date_str, intents)}")
            continue
        _bdup = _broker_record_near(actions_raw, ticker, ex_date)
        if _bdup:
            print(f"  [{ticker}] ❌ {_bdup[0]} — hỏi người.")
            if not dry_run:
                _ask_guarded(ask_failed, _ask_vendor_vs_broker, ticker, ex_date, *_bdup)
            continue
        if ticker in broker_seen:
            print(f"  [{ticker}] nhánh broker đã có mục sổ phiên {date_str} (đã ghi/hỏi theo verdict) — vendor không hỏi lặp.")
            continue
        if held is None or (ticker not in held and unknown):
            why_u = (f"không có file positions dnse_raw nào trong {BD.HELD_LOOKBACK_DAYS} ngày tới {date_str}"
                     if held is None else f"tài khoản KHÔNG xác định được: {'; '.join(unknown)}")
            print(f"  [{ticker}] ❌ {why_u} ⇒ không xác định được mã có đang giữ — hỏi người (không bỏ qua).")
            if not dry_run:
                _ask_guarded(ask_failed, _ask_vendor_held_unknown, ticker, ex_date, mult,
                             ev.get("event_code"), date_str, why_u)
            continue
        if ticker not in held:
            print(f"  [{ticker}] bản ghi positions khác rỗng cuối của MỌI tài khoản đã biết ({date_str}/phiên "
                  f"trước) không có mã ⇒ không giữ — bỏ qua.")
            continue
        print(f"  [{ticker}] vendor {ev.get('event_code')} ×{mult} ex {ex_date}, đang giữ ở {held[ticker]}, "
              f"nhưng {ledger_note} và KHÔNG có mục nào cho mã phiên {date_str} ⇒ KHÔNG ghi (broker là "
              f"nguồn chính), hỏi người.")
        if not dry_run:
            _ask_guarded(ask_failed, _ask_vendor_only, ticker, ex_date, mult, ev.get("event_code"),
                         date_str, held[ticker], ledger_note)
    return 0


def _record_vs_vendor(rec, mult, vcash):
    """PURE. Record registry CÙNG (mã, ex) — MỌI provenance — vs sự kiện CP vendor ×`mult` và
    `vcash` (giá trị DIV vendor cùng ex: list, [] = vendor không có DIV, None = lịch hỏng).
    Trả (khớp?, lý do nêu CẢ HAI số đã so, id record). Chân tiền record so ĐÚNG NHƯ CONSUMER ĐỌC
    (vắng = 0, M1 r3) với Σ DIV vendor cùng ex; chỉ bỏ so khi lịch vendor đọc hỏng (nói rõ)."""
    rid = str(rec.get("id"))
    st = str(rec.get("_status", ""))
    prov = rec.get("provenance") or "người ký/vendor cũ"
    if rec.get("_dup_ids"):
        return False, _dup_why(rec), rid
    if not st.upper().startswith("CONFIRMED"):
        return False, (f"record {rid!r} ({prov}) trạng thái {st[:40]!r} — CHƯA áp dụng, trong khi "
                       f"vendor khai ×{mult:.7g}"), rid
    try:
        rm = float(rec.get("qty_multiplier"))
        if not math.isfinite(rm):
            raise ValueError(rm)
    except (TypeError, ValueError):
        return False, f"record {rid!r} có qty_multiplier không đọc được {rec.get('qty_multiplier')!r}", rid
    if abs(rm - mult) > BROKER_VENDOR_MULT_TOL * mult:
        return False, f"vendor khai ×{mult:.7g} nhưng record {rid!r} ({prov}) là ×{rm:.7g}", rid
    rcv = _cash_leg_as_read(rec)
    shown = ("KHÔNG khai (consumer đọc 0)" if rec.get("cash_leg_vnd_per_share") is None
             else f"{rcv:,.0f}đ/cp")
    if not math.isfinite(rcv):
        return False, f"record {rid!r} có cash_leg_vnd_per_share không đọc được {rec.get('cash_leg_vnd_per_share')!r}", rid
    if vcash is None:
        cash_note = f"chân tiền record {shown}, lịch vendor đọc hỏng (không so được)"
    else:
        vals = [BD._vnum(x) for x in vcash]
        if None in vals:
            return False, f"record {rid!r} chân tiền {shown} vs DIV vendor không đọc được {vcash}", rid
        if abs(sum(vals) - rcv) > BD.VENDOR_CASH_TOL_VND:
            return False, (f"record {rid!r} ({prov}) chân tiền {shown} vs DIV vendor cùng ex "
                           f"{sum(vals):,.0f}đ/cp"), rid
        cash_note = f"chân tiền record {rcv:,.0f} = vendor {sum(vals):,.0f}đ/cp"
    return True, f"khớp: record {rid!r} ({prov}) ×{rm:.7g} vs vendor ×{mult:.7g}; {cash_note}", rid


def _ask_registry_vs_vendor(ticker, ex_date, why, rid):
    """CÙNG (mã, ex) với record registry (mọi provenance) nhưng vendor lệch / record chưa áp dụng —
    hỏi 1 lần / record. Gọi tên Winston (quy ước 09-24: lệch nguồn vendor ⇒ Winston kiểm)."""
    _ask_once(["vendor-vs-registry", ticker, ex_date, rid, "ASKED"],
              f"corp-action-vendor-vs-registry-{ticker}-{ex_date}",
              {"question": f"[Winston] {ticker} ex {ex_date}: {why}. Registry KHÔNG bị ghi đè. Cần "
                           f"người đối chiếu nguồn thật; record {rid} sai ⇒ {ONE_RECORD_RULE}.",
               "assignee": "Winston", "ticker": ticker, "ex_date": ex_date, "record_id": rid,
               "urgency": "high"})


def _ask_vendor_only(ticker, ex_date, mult, code, date_str, holders, ledger_note):
    """Vendor có sự kiện CP sắp ex cho mã đang giữ, sổ broker không có mục — 1 lần / (mã, ex).
    Chỉ nói điều ĐÃ đọc (§29): sổ broker không có mục cho mã phiên này — KHÔNG khẳng định 'DNSE
    không credit' (nhánh broker có thể chưa chạy/nổ, hoặc credit sau 19:25)."""
    _ask_once(["vendor-only", ticker, ex_date, "ASKED"], f"corp-action-vendor-only-{ticker}-{ex_date}",
              {"question": (f"{ticker}: lịch vendor có {code} ×{mult} ex {ex_date} cho mã đang giữ "
                            f"({', '.join(holders)}) nhưng {ledger_note} và không có mục nào cho mã ở "
                            f"phiên {date_str} (nhánh broker chưa thấy ứng viên credit lúc chạy). Broker "
                            f"là nguồn chính ⇒ KHÔNG tự ghi. Kiểm DNSE sau 21:00 / xác nhận tay; nếu "
                            f"vendor sai ⇒ Winston."),
               "ticker": ticker, "vendor_ex_date": ex_date, "vendor_qty_multiplier": mult,
               "vendor_event_code": code, "credit_day": date_str, "holders": holders,
               "urgency": "normal"})


def _ask_vendor_held_unknown(ticker, ex_date, mult, code, date_str, why_u):
    """Không xác định được mã có đang giữ (không file / tài khoản positions rỗng / file cũ) — hỏi 1 lần
    / (mã, ex) (RC2, M3 r3). `why_u` = điều ĐÃ đọc (§29)."""
    _ask_once(["vendor-held-unknown", ticker, ex_date, "ASKED"],
              f"corp-action-vendor-held-unknown-{ticker}-{ex_date}",
              {"question": (f"{ticker}: lịch vendor có {code} ×{mult} ex {ex_date} nhưng {why_u} ⇒ không "
                            f"xác định được có đang giữ mã — INSUFFICIENT, KHÔNG tự ghi. Kiểm pipeline "
                            f"positions (phiên {date_str}) rồi xác nhận tay."),
               "ticker": ticker, "vendor_ex_date": ex_date, "verdict": BD.INSUFFICIENT,
               "credit_day": date_str, "urgency": "normal"})


# ── Nhánh BROKER ───────────────────────────────────────────────────────────

BROKER_MODES = ("off", "shadow", "live")
BUS_TIMEOUT_S = 60
_LOCK_HELD = False        # run() đã giữ khoá ⇒ run_broker không xin lại (flock 2 fd cùng tiến trình = tự khoá)
# Gốc PRODUCTION tính ĐỘC LẬP với các biến module selfcheck hay đổi (LEDGER_FILE/EXEC_DIR/
# BD.LEDGER_FILE) — guard sandbox so với cái này (arch-review v2 N4).
_PROD_DATA = os.path.realpath(os.path.join(WC_ROOT, "data"))
BROKER_VENDOR_MULT_TOL = BD.VENDOR_MULT_TOL_PCT   # vendor vs record broker CÙNG ex: lệch >1% ⇒ hỏi (quy ước 09-24)
NEAR_DUP_DAYS = 10        # record CÙNG MÃ có ex_date cách credit_day ≤ N ngày lịch ⇒ không ghi, hỏi
LOCK_WAIT_S = 120
FEED_DEAD_TAG = "VENDOR_FEED_DEAD: vendor feed chết, broker là nguồn xác định"
DAYMARK_STALE_S = 300     # marker rỗng (claim) cũ hơn N giây = tiến trình đã bị kill trước khi gửi bus
DAYMARK_KEEP_DAYS = 30    # dọn marker `.{tag}-<ngày>` cũ hơn N ngày (chỉ marker, KHÔNG đụng sổ)
DAYMARK_TAGS = ("lockfail", "vendorcrash", "brokercrash")


def broker_mode():
    """`MIKE_CA_BROKER_SOURCE` — giá trị lạ ⇒ shadow (không bao giờ tự lên `live` do gõ nhầm)."""
    raw = os.environ.get("MIKE_CA_BROKER_SOURCE", "shadow").strip().lower()
    if raw not in BROKER_MODES:
        print(f"  ⚠ MIKE_CA_BROKER_SOURCE={raw!r} không hợp lệ {BROKER_MODES} ⇒ dùng 'shadow'")
        return "shadow"
    return raw


def _vendor_events_fn(date_str):
    """ticker → MỌI sự kiện của mã trong `upcoming_events_held` lịch vendor ngày `date_str`.
    Feed đứng vẫn ra file (feed_status STALE, ca TPB 10-01) ⇒ đọc bình thường.
    Không có file thường:
      · `_FAILED.json` đọc được với failed_gate=feed_dead (feed vendor CHẾT >5 ngày) ⇒ lịch vendor
        coi là RỖNG + hàm trả có thuộc tính `feed_dead=True` (caller gắn cờ VENDOR_FEED_DEAD vào
        sổ/log): đúng ý user 10-01 "vendor feed đứng thì broker là nguồn xác định" (r5 M-A, user
        chốt phương án A; vòng 4 #5 đã gộp ca này vào UNREADABLE ⇒ shadow chỉ ra AMBIGUOUS).
      · THIẾU file hoàn toàn / `_FAILED` gate KHÁC feed_dead (vd selfcheck) / file hỏng ⇒
        VENDOR_UNREADABLE + in lý do thật (§29) — KHÔNG coi là "vendor không có sự kiện" (status
        UNREADABLE ≠ NO_EVENT), nhưng từ broker-primary (2026-10-03) cũng KHÔNG chặn broker."""
    path = os.path.join(CA_DAILY_DIR, f"corp_action_daily_{date_str}.json")
    if not os.path.exists(path):
        failed = os.path.join(CA_DAILY_DIR, f"corp_action_daily_{date_str}_FAILED.json")
        if os.path.exists(failed):
            try:
                with open(failed, encoding="utf-8") as f:
                    gate = json.load(f).get("failed_gate")
            except (OSError, json.JSONDecodeError, AttributeError) as e:
                print(f"  ❌ lịch vendor {os.path.basename(failed)} đọc hỏng: {type(e).__name__}: {e}"
                      f" ⇒ VENDOR_UNREADABLE: không đối chiếu được — broker vẫn là nguồn chính, ghi 'chưa được vendor xác nhận'")
                return lambda tk: BD.VENDOR_UNREADABLE
            if gate == "feed_dead":
                print(f"  ⚠ VENDOR_FEED_DEAD: {os.path.basename(failed)} failed_gate=feed_dead ⇒ "
                      f"vendor feed chết, broker là nguồn xác định (lịch vendor coi là rỗng)")

                def dead(tk):
                    return []
                dead.feed_dead = True
                return dead
            why = f"chỉ có {os.path.basename(failed)} với failed_gate={gate!r} (không phải feed_dead)"
        else:
            why = "không có file"
        print(f"  ❌ lịch vendor {path}: {why} ⇒ VENDOR_UNREADABLE: không đối chiếu được — broker vẫn là "
          f"nguồn chính, ghi 'chưa được vendor xác nhận'")
        return lambda tk: BD.VENDOR_UNREADABLE
    try:
        with open(path, encoding="utf-8") as f:
            held = json.load(f).get("upcoming_events_held") or []
    except (OSError, json.JSONDecodeError, AttributeError) as e:
        print(f"  ❌ lịch vendor {path} đọc hỏng: {type(e).__name__}: {e} ⇒ VENDOR_UNREADABLE: không đối "
              f"chiếu được — broker vẫn là nguồn chính")
        return lambda tk: BD.VENDOR_UNREADABLE
    return lambda tk: [e for e in held if str(e.get("ticker", "")).upper() == tk]


def _exchange_fn():
    """ticker → sàn THẬT qua DNSE `marketId` (STO/STX/UPX). Không xác định được ⇒ None ⇒ detector
    MƠ HỒ (fail-closed; không mặc định HOSE như `Quote.exchange`).

    PHẢI `connect()` (arch-review v4 #1): `get_quote_source()` trả nguồn client=None; `get_quote`
    khi chưa connect nuốt AttributeError của từng lời gọi API ⇒ Quote rỗng ⇒ exchange_known=False
    ⇒ MỌI ứng viên MƠ HỒ (TPB 10-01 thật). Connect 1 lần/lượt như `bot_execute.py --probe` /
    `opening_window_l2_poll.py`; lỗi ⇒ None cho mọi mã. `_raw_log=None`: script này chỉ ĐỌC
    dnse_raw — không ghi quote_unmapped/quote_l2 vào file kế toán production (kể cả --dry-run)."""
    cache, src = {}, []

    def _source():
        if not src:
            try:
                from trading_bot.brokers import get_quote_source
                s = get_quote_source("dnse")
                s._raw_log = None
                s.connect()
                src.append(s)
            except Exception as e:  # §29: nói lỗi thật
                print(f"  không kết nối được nguồn quote DNSE: {type(e).__name__}: {e} ⇒ sàn None")
                src.append(None)
        return src[0]

    def fn(tk):
        if tk not in cache:
            s = _source()
            if s is None:
                cache[tk] = None
                return None
            try:
                q = s.get_quote(tk)
                cache[tk] = q.exchange if getattr(q, "exchange_known", False) else None
            except Exception as e:  # §29: nói lỗi thật
                print(f"  [{tk}] không xác định được sàn qua DNSE: {type(e).__name__}: {e}")
                cache[tk] = None
        return cache[tk]
    return fn


def _px_cum_fn(date_str):
    """Giá đóng cửa CÒN QUYỀN của phiên credit. Hôm nay ⇒ DNSE G1 (§6, BẮT BUỘC nguồn
    'dnse_g1_today' — giá phiên khác là sai hệ); ngày quá khứ ⇒ BQ `Price` chưa điều chỉnh.
    Lỗi/thiếu ⇒ None ⇒ detector trả INSUFFICIENT, KHÔNG đoán. `fn.prefetch(tickers, day, over)` —
    ngày quá khứ: MỘT truy vấn BQ cho cả lô; hôm nay: `dnse_close_prices` vốn gọi DNSE TUẦN TỰ từng
    mã (mỗi mã ≤3 endpoint, có timeout riêng) ⇒ gọi TỪNG mã và hỏi `over()` TRƯỚC mỗi lời gọi
    (m2 r3: ngân sách kiểm 1 lần trước lô không chặn được N×timeout). Hết ngân sách ⇒ dừng, mã chưa
    gọi không vào cache (caller xếp vào dòng 'hết ngân sách')."""
    cache = {}

    def prefetch(tickers, day, over=None):
        try:
            if day == today_ict():
                from verify_account_snapshot import dnse_close_prices
                for t in tickers:
                    if over is not None and over():
                        print(f"  hết ngân sách sàng lọc chỉ-giá trước khi gọi giá DNSE cho {t} ⇒ dừng prefetch")
                        break
                    px, src = dnse_close_prices([t], with_source=True)
                    ok = src.get(t) == "dnse_g1_today"
                    if not ok:
                        print(f"  [{t}] giá DNSE nguồn {src.get(t)!r} ≠ dnse_g1_today ⇒ không dùng")
                    cache[(t, day)] = px.get(t) if ok else None
            else:
                got = BD.bq_unadjusted_close({(t, day) for t in tickers})
                for t in tickers:
                    cache[(t, day)] = got.get((t, day))
        except Exception as e:  # §29: lỗi thật; mã chưa có trong cache sẽ thử lẻ ở fn()
            print(f"  không lấy được giá cum lô {len(tickers)} mã {day}: {type(e).__name__}: {e}")

    def fn(ticker, day):
        if (ticker, day) in cache:
            return cache[(ticker, day)]
        try:
            if day == today_ict():
                from verify_account_snapshot import dnse_close_prices
                px, src = dnse_close_prices([ticker], with_source=True)
                if src.get(ticker) != "dnse_g1_today":
                    print(f"  [{ticker}] giá DNSE nguồn {src.get(ticker)!r} ≠ dnse_g1_today ⇒ không dùng")
                    return None
                return px.get(ticker)
            return BD.bq_unadjusted_close({(ticker, day)}).get((ticker, day))
        except Exception as e:  # mạng/bq lỗi ⇒ INSUFFICIENT, nói rõ lỗi thật (§29)
            print(f"  [{ticker}] không lấy được giá cum {day}: {type(e).__name__}: {e}")
            return None
    fn.prefetch = prefetch
    return fn


def _bus(kind, topic, payload):
    """rc của append_event.sh (0 = bus đã nhận). rc≠0 ⇒ in lỗi THẬT, caller KHÔNG đánh dấu done."""
    import subprocess
    try:
        r = subprocess.run([APPEND_EVENT, "Mike", kind, topic,
                            json.dumps(payload, ensure_ascii=False, default=str)],
                           capture_output=True, text=True, timeout=BUS_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        print(f"  ❌ append_event {kind} {topic} treo > {BUS_TIMEOUT_S}s — coi như CHƯA gửi")
        return 124
    if r.returncode != 0:
        print(f"  ❌ append_event {kind} {topic} rc={r.returncode}: "
              f"{(r.stderr or r.stdout or '').strip()[:300]}")
    return r.returncode


def _lock(path):
    """Khoá loại trừ (fcntl) quanh đọc-sửa-ghi sổ + registry của nhánh broker — cron và chạy tay
    đồng thời không đè nhau. Không lấy được trong LOCK_WAIT_S ⇒ None (caller rc=1, không ghi)."""
    import fcntl
    import time
    fh = open(path + ".lock", "a")
    t0 = time.monotonic()
    while True:
        try:
            fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return fh
        except BlockingIOError:
            if time.monotonic() - t0 > LOCK_WAIT_S:
                fh.close()
                return None
            time.sleep(1)


def _near_duplicate(raw_actions, tk, credit_day, ex):
    """Record (MỌI trạng thái) cùng mã, ex_date ≠ ex nhưng cách credit_day ≤ NEAR_DUP_DAYS ⇒ rất có
    thể CÙNG sự kiện được người ký với ex khác (lịch thiếu ngày nghỉ…) — ghi thêm = áp hệ số 2 lần.
    Trả (lý do, id record) — id để câu hỏi chỉ đúng record cần SỬA/THU HỒI (I2 r3), hoặc None."""
    d0 = dt.date.fromisoformat(credit_day)
    for r in raw_actions:
        if str(r.get("ticker", "")).upper() != tk:
            continue
        try:
            rex = dt.date.fromisoformat(str(r.get("ex_date", ""))[:10])
        except ValueError:
            return (f"record {r.get('id')!r} cùng mã có ex_date không đọc được {r.get('ex_date')!r}",
                    str(r.get("id")))
        if rex.isoformat() != ex and abs((rex - d0).days) <= NEAR_DUP_DAYS:
            return (f"registry đã có {r.get('id')!r} ({str(r.get('_status', ''))[:30]!r}) ex "
                    f"{rex} cách phiên credit {credit_day} ≤ {NEAR_DUP_DAYS} ngày — có thể CÙNG sự "
                    f"kiện với ex khác ⇒ không ghi thêm (×hệ số 2 lần)"), str(r.get("id"))
    return None


class SandboxMismatch(RuntimeError):
    """Sổ PRODUCTION + dữ liệu sandbox — KHÔNG bao giờ bị nuốt (kể cả bởi _ask_guarded)."""


def _sandbox_guard():
    """Sổ là PRODUCTION mà dữ liệu vào/registry KHÔNG ⇒ đúng lớp lỗi B2 (selfcheck quên đổi
    LEDGER_FILE ghi rác vào sổ thật). Gọi TRƯỚC khi tạo bất kỳ file nào (kể cả .lock)."""
    def _in_prod(p):
        return os.path.realpath(p).startswith(_PROD_DATA + os.sep)
    if _in_prod(LEDGER_FILE) and not (_in_prod(EXEC_DIR) and _in_prod(CORP_ACTIONS_FILE)):
        # Sandbox LỆCH: dữ liệu vào/registry là sandbox mà sổ là PRODUCTION ⇒ đúng lớp lỗi B2
        # (selfcheck quên đổi LEDGER_FILE ghi rác vào sổ thật). Từ chối thay vì ghi.
        raise SandboxMismatch(f"LEDGER_FILE={LEDGER_FILE} là sổ PRODUCTION nhưng EXEC_DIR={EXEC_DIR} / "
                           f"CORP_ACTIONS_FILE={CORP_ACTIONS_FILE} đã bị đổi (sandbox?) — từ chối ghi")


def _broker_record_near(raw_actions, tk, ex):
    """Record provenance=broker ĐANG CONFIRMED (không tính REVOKED/PROPOSED) CÙNG mã, ex ≠ `ex`,
    cách ≤ NEAR_DUP_DAYS ngày, trước HOẶC sau (cho nhánh vendor)."""
    try:
        d0 = dt.date.fromisoformat(ex)
    except ValueError:
        return None
    for r in raw_actions:
        if (str(r.get("ticker", "")).upper() != tk
                or str(r.get("provenance", "")).lower() != "broker"):
            continue
        if not str(r.get("_status", "")).upper().startswith("CONFIRMED"):
            continue      # REVOKED/PROPOSED đã bị người thu hồi/chưa duyệt ⇒ không khoá vendor mãi
        try:
            rex = dt.date.fromisoformat(str(r.get("ex_date", ""))[:10])
        except ValueError:
            return f"record broker {r.get('id')!r} có ex_date không đọc được", str(r.get("id"))
        if rex != d0 and abs((rex - d0).days) <= NEAR_DUP_DAYS:
            return (f"registry đã có record BROKER {r.get('id')!r} ex {rex} (cách {abs((rex - d0).days)}"
                    f" ngày) — có thể CÙNG sự kiện với ex khác"), str(r.get("id"))
    return None


def _broker_record_ratio_diff(raw_actions, tk, ex, mult):
    """Record provenance=broker ĐANG CONFIRMED CÙNG (mã, ex) mà hệ số lệch hệ số vendor `mult` quá
    BROKER_VENDOR_MULT_TOL (tương đối) ⇒ (lý do, id). Record người ký ⇒ None (đường cũ)."""
    for r in raw_actions:
        if (str(r.get("ticker", "")).upper() != tk or str(r.get("ex_date", ""))[:10] != ex
                or str(r.get("provenance", "")).lower() != "broker"
                or not str(r.get("_status", "")).upper().startswith("CONFIRMED")):
            continue
        try:
            bm = float(r.get("qty_multiplier"))
        except (TypeError, ValueError):
            bm = None
        if bm is None or abs(bm - mult) > BROKER_VENDOR_MULT_TOL * mult:
            return (f"vendor khai ×{mult} nhưng record BROKER {r.get('id')!r} cùng ex {ex} là "
                    f"×{r.get('qty_multiplier')}"), str(r.get("id"))
    return None


REG_MATCH, REG_MISMATCH = "MATCH", "MISMATCH"
ONE_RECORD_RULE = ("KHÔNG thêm record thứ hai cho cùng (mã, ex) — chỉ SỬA hoặc THU HỒI (REVOKED) record "
                   "hiện có, hoặc đóng câu hỏi (bất biến ≤1 record hiệu lực/(mã, ex))")


def _effective(rec):
    """Record HIỆU LỰC = _status CONFIRMED* (đúng bộ lọc `corp_actions.load_corp_actions`)."""
    return str(rec.get("_status", "")).upper().startswith("CONFIRMED")


def _effective_groups(actions):
    """{(mã, ex): [index]} của record HIỆU LỰC."""
    g = {}
    for i, r in enumerate(actions):
        if _effective(r):
            g.setdefault((str(r.get("ticker", "")).upper(), str(r.get("ex_date", ""))[:10]), []).append(i)
    return g


def _validate_for_write(actions, base):
    """Chốt ĐIỂM GHI (I1 r3): validate() từng record + bất biến ≤1 record HIỆU LỰC/(mã, ex). Nhóm ≥2
    mà `base` (registry trên đĩa trước lượt ghi) KHÔNG có y hệt ⇒ do lượt này tạo ⇒ CorpActionError
    (thông điệp `corp_actions[i]` = index record vi phạm cuối, cùng dạng validate()) ⇒ 0 ghi. Nhóm ≥2
    CÓ SẴN (người gõ) không chặn ghi mã khác — đối chiếu coi nó là LỆCH và hỏi riêng (m6)."""
    for i, rec in enumerate(actions):
        CA.validate(rec, i)  # ném CorpActionError nếu hỏng — KHÔNG bắt ở đây, để caller quyết định
    old = {k: sorted(str(base[i].get("id")) for i in v) for k, v in _effective_groups(base).items()}
    for k, idx in sorted(_effective_groups(actions).items()):
        ids = sorted(str(actions[i].get("id")) for i in idx)
        if len(idx) > 1 and ids != old.get(k):
            raise CA.CorpActionError(
                f"corp_actions[{idx[-1]}] vi phạm bất biến ≤1 record HIỆU LỰC/(mã, ex): {k[0]} ex {k[1]} sẽ "
                f"có {len(idx)} record CONFIRMED {ids} ⇒ park_holdings áp hệ số {len(idx)} lần — từ chối ghi")


def _registry_view(actions):
    """{(mã, ex): record đại diện} cho ĐỐI CHIẾU. Đúng 1 record hiệu lực ⇒ nó; ≥2 ⇒ record giả mang
    `_dup_ids` (đối chiếu coi là LỆCH — m6: bản cũ dict comprehension lấy record CUỐI, im lặng);
    0 hiệu lực ⇒ record cuối (chưa áp dụng: PROPOSED/REVOKED…)."""
    by = {}
    for r in actions:
        by.setdefault((str(r.get("ticker", "")).upper(), str(r.get("ex_date", ""))[:10]), []).append(r)
    out = {}
    for k, rs in by.items():
        eff = [r for r in rs if _effective(r)]
        if len(eff) > 1:
            ids = [str(r.get("id")) for r in eff]
            out[k] = {"id": "+".join(ids), "ticker": k[0], "ex_date": k[1], "_dup_ids": ids,
                      "_status": f"CONFIRMED ×{len(eff)} (TRÙNG — vi phạm ≤1 record hiệu lực)"}
        else:
            out[k] = eff[0] if eff else rs[-1]
    return out


def _dup_why(rec):
    ids = rec["_dup_ids"]
    return (f"registry có {len(ids)} record HIỆU LỰC cho ({rec['ticker']}, {rec['ex_date']}) {ids} ⇒ "
            f"park_holdings áp hệ số {len(ids)} lần")


def _cash_leg_as_read(rec):
    """Chân tiền ĐÚNG như consumer đọc (I3 r3): vắng/None ⇒ 0.0 (validate/park_holdings/exdate_frame);
    không phải số / không hữu hạn ⇒ nan (caller coi là LỆCH)."""
    raw = rec.get("cash_leg_vnd_per_share")
    try:
        v = float(raw if raw is not None else 0.0)
    except (TypeError, ValueError):
        return float("nan")
    return v if math.isfinite(v) else float("nan")


def _registry_reconcile(rec, r):
    """PURE (RC1). Record registry CÙNG (mã, ex) — MỌI provenance, MỌI trạng thái — vs kết luận
    broker `r`. Trả {status MATCH|MISMATCH, why (nêu CẢ HAI số), record_id, record_status}.
      MISMATCH: ≥2 record hiệu lực (m6); record chưa CONFIRMED (PROPOSED/UNVERIFIED/REVOKED… — chưa
                áp dụng mà broker thấy sự kiện); broker CHỈ-GIÁ (KL không đổi) trong khi registry khai
                sự kiện KL; hệ số lệch >1%; chân tiền registry ĐÚNG NHƯ CONSUMER ĐỌC (vắng = 0, M1 r3 —
                bản r2 coi vắng là "không so" ⇒ MATCH im, mà cổng giá đêm park_holdings dùng 0 ⇒ FAIL)
                lệch chân tiền broker >1đ/cp; hệ số/chân tiền record hỏng.
      MATCH:    còn lại.
    Broker chưa quyết (INSUFFICIENT/AMBIGUOUS) ⇒ không gọi hàm này (caller giữ verdict + hỏi)."""
    rid, st = str(rec.get("id")), str(rec.get("_status", ""))
    prov = rec.get("provenance") or "người ký/vendor cũ"
    base = {"record_id": rid, "record_status": st[:60], "record_provenance": prov}
    bm, bc = r.get("qty_multiplier"), float(r.get("cash_leg") or 0.0)
    if rec.get("_dup_ids"):
        return dict(base, status=REG_MISMATCH, why=_dup_why(rec))
    if not st.upper().startswith("CONFIRMED"):
        return dict(base, status=REG_MISMATCH,
                    why=(f"registry có {rid!r} ({prov}) trạng thái {st[:40]!r} — CHƯA áp dụng, trong khi "
                         f"broker thấy {r.get('kind') or 'SHARE_EVENT'} ×{bm or 1} chân tiền {bc:,.0f}đ/cp"))
    try:
        rm = float(rec.get("qty_multiplier"))
        if not math.isfinite(rm):
            raise ValueError(rm)
    except (TypeError, ValueError):
        return dict(base, status=REG_MISMATCH,
                    why=f"registry {rid!r} có qty_multiplier không đọc được {rec.get('qty_multiplier')!r}")
    if not bm:
        return dict(base, status=REG_MISMATCH,
                    why=(f"registry {rid!r} ({prov}) khai sự kiện KL ×{rm:.7g} ex {rec.get('ex_date')} nhưng "
                         f"broker KL KHÔNG đổi ({r.get('kind')}, chân tiền {bc:,.0f}đ/cp)"))
    if abs(rm - bm) > BROKER_VENDOR_MULT_TOL * bm:
        return dict(base, status=REG_MISMATCH,
                    why=f"broker ×{bm} vs registry {rid!r} ({prov}) ×{rm:.7g} (lệch {abs(rm - bm) / bm:.2%} > 1%)")
    rc = rec.get("cash_leg_vnd_per_share")
    rcv = _cash_leg_as_read(rec)
    shown = (f"KHÔNG khai (consumer đọc {rcv:,.0f})" if rc is None else f"{rc!r}")
    if not math.isfinite(rcv) or abs(rcv - bc) > BD.VENDOR_CASH_TOL_VND:
        return dict(base, status=REG_MISMATCH,
                    why=(f"chân tiền: broker {bc:,.0f}đ/cp vs registry {rid!r} ({prov}) {shown}đ/cp"
                         + (" — park_holdings/exdate_frame sẽ dựng giá tham chiếu với chân tiền SAI ⇒ cổng "
                            "giá đêm FAIL" if math.isfinite(rcv) else "")))
    note = f"chân tiền broker {bc:,.0f} = registry {rcv:,.0f}đ/cp" + (" (không khai = 0)" if rc is None else "")
    return dict(base, status=REG_MATCH, why=f"broker ×{bm} = registry {rid!r} ({prov}) ×{rm:.7g}; {note}")


def _ask_vendor_vs_broker(ticker, ex_date, why, rid):
    """Vendor ex ≠ ex record broker gần đó (N9). Khoá hỏi có id record broker (arch-review v4 #9):
    người REVOKE record cũ rồi broker ghi record MỚI cho cùng (mã, ex vendor) ⇒ hỏi lại."""
    _ask_once(["vendor-vs-broker", ticker, ex_date, rid, "ASKED"],
              f"corp-action-vendor-vs-broker-{ticker}-{ex_date}",
              {"question": f"{ticker}: lịch vendor ex {ex_date} nhưng {why}. Cần người xác "
                           f"nhận ex thật; record {rid} sai ex ⇒ {ONE_RECORD_RULE}.",
               "ticker": ticker, "vendor_ex_date": ex_date, "broker_record_id": rid,
               "urgency": "high"})


def _ask_ratio_vs_broker(ticker, ex_date, why, rid):
    """CÙNG (mã, ex) với record broker nhưng tỉ lệ khác (arch-review v4 #12) — hỏi 1 lần/record."""
    _ask_once(["vendor-ratio-vs-broker", ticker, ex_date, rid, "ASKED"],
              f"corp-action-vendor-ratio-vs-broker-{ticker}-{ex_date}",
              {"question": f"{ticker} ex {ex_date}: {why}. Registry giữ hệ số BROKER (không ghi đè). "
                           f"Cần người đối chiếu tỉ lệ thật; record {rid} sai ⇒ {ONE_RECORD_RULE}.",
               "ticker": ticker, "ex_date": ex_date, "broker_record_id": rid, "urgency": "high"})


def _prune_daymarks():
    """Marker ngày cũ hơn DAYMARK_KEEP_DAYS ngày thì xoá — chỉ marker `.{tag}-<ngày>` cạnh sổ."""
    import glob
    import time
    for tag in DAYMARK_TAGS:
        for p in glob.glob(f"{LEDGER_FILE}.{tag}-*"):
            try:
                if time.time() - os.stat(p).st_mtime > DAYMARK_KEEP_DAYS * 86400:
                    os.remove(p)
            except OSError:
                pass


def _ask_day_once(tag, date_str, topic, payload):
    """Bus `question` 1 lần/ngày/`tag` (ops_health_check leo thang question, KHÔNG leo thang `error`
    — arch-review v4 #3). Marker `{LEDGER_FILE}.{tag}-{date_str}` tạo nguyên tử O_EXCL (không cần
    khoá — có thể chính khoá đang bị giữ) như CLAIM RỖNG; chỉ khi bus rc=0 mới ghi nội dung
    "sent" (r5 M-D: bản cũ coi marker là đã báo ngay lúc tạo ⇒ kill giữa tạo marker và gửi bus làm
    ngày đó im vĩnh viễn). Bus lỗi/ném ⇒ xoá marker, lượt sau hỏi lại. Claim rỗng cũ hơn
    DAYMARK_STALE_S giây ⇒ tiến trình chủ đã chết, chiếm lại."""
    import time
    _prune_daymarks()
    marker = f"{LEDGER_FILE}.{tag}-{date_str}"
    fd = None
    for _ in range(3):
        try:
            fd = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            try:
                st = os.stat(marker)
            except FileNotFoundError:
                continue
            if st.st_size > 0 or time.time() - st.st_mtime <= DAYMARK_STALE_S:
                print(f"  đã hỏi người ({tag}) ngày {date_str} (hoặc tiến trình khác đang gửi) ⇒ không hỏi lại")
                return
            print(f"  claim {os.path.basename(marker)} rỗng quá {DAYMARK_STALE_S}s ⇒ tiến trình trước "
                  f"chết giữa claim và bus, chiếm lại")
            try:
                os.remove(marker)
            except FileNotFoundError:
                pass
    if fd is None:
        print(f"  ❌ không chiếm được marker {marker} sau 3 lần — bỏ qua lượt hỏi này")
        return
    try:
        rc = _bus("question", topic, payload)
    except Exception as e:  # §29
        print(f"  ❌ không gửi được bus question {topic}: {type(e).__name__}: {e}")
        rc = 1
    try:
        if rc == 0:
            os.write(fd, b"sent\n")
    finally:
        os.close(fd)
    if rc != 0:
        os.remove(marker)


def _ask_lock_unavailable(date_str, mode):
    """Không lấy được khoá ⇒ CẢ nhánh vendor lẫn broker không chạy (urgency high, 1 lần/ngày)."""
    _ask_day_once("lockfail", date_str, f"corp-action-lock-unavailable-{date_str}",
                  {"question": (f"Không lấy được khoá {LEDGER_FILE}.lock sau {LOCK_WAIT_S}s — nhánh "
                                f"vendor VÀ broker đều KHÔNG chạy lượt {date_str}. Kiểm tiến trình "
                                f"corp_action_auto_confirm đang treo rồi chạy lại tay --date {date_str}."),
                   "mode": mode, "urgency": "high"})


def _ask_once(key, topic, payload):
    """Hỏi người MỘT lần cho mỗi `key` (xem `_notify_once`)."""
    _notify_once("question", key, topic, payload)


def _notify_once(kind, key, topic, payload):
    """Gửi bus `kind` MỘT lần cho mỗi `key`: bus rc=0 ⇒ ghi dòng `done` vào sổ ⇒ lượt sau im. Bus
    lỗi ⇒ không đánh dấu (lượt sau gửi lại). Sổ đọc hỏng ⇒ vẫn gửi (an toàn), nói lỗi thật.
    Trả True khi đã gửi được hoặc đã gửi từ trước."""
    from zoneinfo import ZoneInfo
    ticker = key[1]
    _sandbox_guard()
    try:
        _intents, done = BD.ledger_state(LEDGER_FILE)
    except BD.CorpActionLedgerError as e:       # sổ hỏng ⇒ vẫn hỏi (an toàn), nói lỗi thật (§29)
        print(f"  ⚠ sổ broker đọc hỏng ({e}) ⇒ không kiểm được đã hỏi chưa, hỏi lại")
        done = set()
    if tuple(key) in done:
        print(f"  [{ticker}] đã gửi {kind} {key} ⇒ không gửi lại")
        return True
    rc = _bus(kind, topic, payload)
    if rc == 0:
        now_ict = dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%dT%H:%M:%S+07:00")
        BD.ledger_append([{"kind": "done", "key": key, "at": now_ict}], LEDGER_FILE)
    return rc == 0


def _close_stale_questions(e, intents):
    """§26: lượt trước (cùng mã, cùng phiên, live) đã HỎI vì INSUFFICIENT/AMBIGUOUS/DEFER, nay
    record đã CONFIRMED ⇒ đóng các câu hỏi đó bằng `answer` đúng topic, kèm bằng chứng record id.
    Lỗi gửi chỉ in ra (question vẫn mở = an toàn, người đọc thấy record ở finding confirm)."""
    for k, old in intents.items():
        if (old.get("mode") == "live" and old.get("ticker") == e["ticker"]
                and old.get("credit_day") == e["credit_day"]
                and old.get("verdict") in (BD.INSUFFICIENT, BD.AMBIGUOUS, BD.DEFER_VENDOR, BD.UNVERIFIED)):
            _bus("answer", f"corp-action-broker-{old['verdict'].lower()}-{e['ticker']}-{e['credit_day']}",
                 {"resolution": (f"lượt sau đã CONFIRMED {e['record']['id']} ×{e['qty_multiplier']} "
                                 f"ex {e['ex_date']} (provenance=broker)"),
                  "evidence": f"data/corp_actions.json id={e['record']['id']}",
                  "decided_by": "agent"})


_OPEN_VERDICTS = (BD.INSUFFICIENT, BD.AMBIGUOUS, BD.DEFER_VENDOR, BD.UNVERIFIED)


def _close_resolved(tk, day, intents, done, regc):
    """m7 r3 (§26, I8): registry KHỚP broker cho mã ở phiên `day` (live) ⇒ câu hỏi cũ cùng mã/phiên
    (INSUFFICIENT/AMBIGUOUS/DEFER/UNVERIFIED) đã hết lý do mở:
      · đã gửi (có `done`) ⇒ `answer` đúng topic, 1 lần/khoá (sổ done), kèm bằng chứng record id;
      · chưa gửi (việc dở lượt trước) ⇒ trả khoá để caller BỎ gửi bù + ghi done 'superseded'.
    Lỗi gửi chỉ in (câu hỏi vẫn mở = an toàn). Trả set khoá superseded."""
    sup = set()
    for k, old in intents.items():
        if (old.get("mode") != "live" or old.get("ticker") != tk or old.get("credit_day") != day
                or old.get("verdict") not in _OPEN_VERDICTS):
            continue
        if k not in done:
            sup.add(k)
            continue
        _notify_once("answer", ["closed", tk, day, old["verdict"], str(regc.get("record_id")), "|".join(map(str, k))],
                     f"corp-action-broker-{old['verdict'].lower()}-{tk}-{day}",
                     {"resolution": (f"lượt sau: registry {regc.get('record_id')} KHỚP broker ({regc.get('why')}) "
                                     f"⇒ câu hỏi {old['verdict']} đã giải quyết"),
                      "evidence": f"data/corp_actions.json id={regc.get('record_id')}", "decided_by": "agent"})
    return sup


CREDIT_WATCH_SESSIONS = 1   # cảnh báo QUÁ HẠN khi ex ≤ hôm nay ≤ ex + N phiên mà sổ broker chưa thấy credit


def _credit_state(tk, ex, date_str, intents, seen_now=None):
    """Trạng thái credit broker cho record registry (mã, ex) — đọc sổ broker (mọi mode, kể cả dòng
    `observation_only` của nhánh registry-khớp) + `seen_now` {(mã, ex): verdict} của CHÍNH lượt này
    (dry-run không ghi sổ): 'ĐÃ THẤY …' / 'CHỜ CREDIT …' (ex sau hôm nay) / 'QUÁ HẠN …'. m1 r3."""
    seen = sorted({str(e.get("verdict")) for e in intents.values()
                   if e.get("ticker") == tk and e.get("ex_date") == ex}
                  | ({str((seen_now or {})[(tk, ex)])} if (tk, ex) in (seen_now or {}) else set()))
    if seen:
        return f"ĐÃ THẤY ở sổ broker / kết quả lượt này ({', '.join(seen)})"
    if ex > date_str:
        return (f"CHỜ CREDIT — sổ broker chưa có mục ({tk}, {ex}); DNSE thường credit tối phiên liền "
                f"trước ex (18:30–20:15)")
    return (f"QUÁ HẠN — ex {ex} ≤ {date_str} mà sổ broker KHÔNG có mục ({tk}, {ex}) ở mode nào (DNSE chưa "
            f"credit, HOẶC credit SAU lượt 19:25 phiên trước — lượt này không quét lại phiên trước)")


def _registry_sweep(date_str, mode, dry_run=False, seen_now=None):
    """Phủ các ô registry KHÔNG đi qua detector (I5 r3):
      (a) m6/I1 — (mã, ex) có ≥2 record HIỆU LỰC ⇒ log; live ⇒ question high 1 lần/(mã, ex, ids);
      (b) m1 — record HIỆU LỰC (mọi provenance) có ex = phiên KẾ TIẾP (chờ credit tối nay) hoặc ex ≤ hôm
          nay ≤ ex + CREDIT_WATCH_SESSIONS phiên, mã đang giữ / KHÔNG xác định được: sổ broker không có
          mục nào ⇒ log 'CHỜ CREDIT'; quá hạn ⇒ live question 1 lần/(mã, ex, id). Mã chắc chắn không
          giữ ⇒ log. shadow/dry-run ⇒ chỉ in. Không bao giờ ghi data/corp_actions.json. Trả rc."""
    from trading_bot.vn_market import next_trading_day
    quiet = dry_run or mode != "live"
    view = _registry_view(load_corp_actions_raw())
    rc = 0
    for (tk, ex), rec in sorted(view.items()):
        if not rec.get("_dup_ids"):
            continue
        print(f"  [registry] ❌ {_dup_why(rec)}")
        if not quiet:
            ok = _notify_once("question", ["registry-dup", tk, ex, "+".join(rec["_dup_ids"]), "ASKED"],
                              f"corp-action-registry-dup-{tk}-{ex}",
                              {"question": (f"{_dup_why(rec)} — vi phạm bất biến ≤1 record hiệu lực/(mã, ex). "
                                            f"Giữ ĐÚNG MỘT record (sửa nó theo số thật), THU HỒI (REVOKED) các "
                                            f"record còn lại. Không lượt tự động nào sửa registry."),
                               "ticker": tk, "ex_date": ex, "record_ids": rec["_dup_ids"], "urgency": "high"})
            rc = rc or (0 if ok else 1)
    nxt = next_trading_day(dt.date.fromisoformat(date_str)).isoformat()

    def _in_window(ex):
        try:
            return ex == nxt or (ex <= date_str and _sessions_since(ex, date_str) <= CREDIT_WATCH_SESSIONS)
        except ValueError:      # ex hỏng ⇒ validate() của consumer đã chặn cả registry; không đoán ở đây
            print(f"  [credit-watch] ex_date không đọc được {ex!r} ⇒ bỏ qua (validate() báo ở consumer)")
            return False
    watch = [(k, r) for k, r in sorted(view.items())
             if _effective(r) and not r.get("_dup_ids") and _in_window(k[1])]
    if not watch:
        return rc
    try:
        intents, _done = BD.ledger_state(LEDGER_FILE)
    except BD.CorpActionLedgerError as e:      # §29: sổ hỏng ⇒ không biết broker đã thấy gì ⇒ coi chưa thấy
        print(f"  ⚠ sổ broker đọc hỏng ({e}) ⇒ credit-watch coi như sổ broker chưa thấy mục nào")
        intents = {}
    hi = BD.held_tickers(date_str, EXEC_DIR)
    held, unknown = hi if hi is not None else ({}, [f"không có file dnse_raw nào trong {BD.HELD_LOOKBACK_DAYS} ngày"])
    for (tk, ex), rec in watch:
        rid = str(rec.get("id"))
        st = _credit_state(tk, ex, date_str, intents, seen_now)
        if not st.startswith("QUÁ HẠN") and not st.startswith("CHỜ"):
            print(f"  [credit-watch {rid}] {st}")
            continue
        if tk not in held and not unknown:
            print(f"  [credit-watch {rid}] {st} — nhưng MỌI tài khoản đã biết không giữ {tk} ⇒ không chờ credit")
            continue
        holders = held.get(tk) or [f"không xác định: {'; '.join(unknown)}"]
        print(f"  [credit-watch {rid}] ex {ex}: {st}; giữ: {holders}")
        if not st.startswith("QUÁ HẠN") or quiet:
            continue
        ok = _notify_once("question", ["credit-overdue", tk, ex, rid, "ASKED"],
                          f"corp-action-credit-overdue-{tk}-{ex}",
                          {"question": (f"{tk}: registry có record HIỆU LỰC {rid} ×{rec.get('qty_multiplier')} ex "
                                        f"{ex} (park_holdings đang áp) nhưng {st}. Tài khoản: {holders}. Kiểm KL "
                                        f"DNSE thật so với record; sai ⇒ {ONE_RECORD_RULE}."),
                           "ticker": tk, "ex_date": ex, "record_id": rid, "holders": holders,
                           "urgency": "high"})
        rc = rc or (0 if ok else 1)
    return rc


def _finish_live(e, registry_ids):
    """Gửi thông báo cho MỘT mục sổ ở live. Trả rc bus. Không khẳng định điều chưa kiểm (§29)."""
    tk, day, v = e["ticker"], e["credit_day"], e["verdict"]
    vc = e.get("vendor_check") or {}
    if v == BD.CONFIRMABLE:
        rid = e["record"]["id"]
        if rid in registry_ids:
            return _bus("finding", f"corp-action-broker-confirm-{tk}",
                        {"status": "AUTO_CONFIRMED_BROKER", "event_id": rid, "ticker": tk,
                         "ex_date": e["ex_date"], "qty_multiplier": e["qty_multiplier"],
                         "cash_leg_vnd_per_share": e["cash_leg"],
                         "vendor_check": vc.get("status"), "vendor_why": vc.get("why"),
                         "verified_by_vendor": vc.get("status") == BD.V_VERIFIED,
                         "evidence": e["record"]["evidence"], "decided_by": "agent",
                         "note": "provenance=broker (nguồn chính); vendor chỉ xác nhận chéo; thu hồi: _status REVOKED"})
        return _bus("question", f"corp-action-broker-write-incomplete-{tk}-{day}",
                    {"question": (f"{tk}: nhánh broker đã quyết CONFIRMABLE ×{e['qty_multiplier']} "
                                  f"ex {e['ex_date']} nhưng load_corp_actions() KHÔNG thấy record "
                                  f"{rid} trong registry (ghi dở/bị kill/đọc lại hỏng). Cần người "
                                  f"kiểm data/corp_actions.json."),
                     "ticker": tk, "credit_day": day, "record": e["record"], "urgency": "high"})
    if v == BD.CASH_DIVIDEND:
        return _bus("finding", f"corp-action-broker-cashdiv-{tk}-{day}",
                    {"status": "CASH_DIVIDEND_BROKER", "ticker": tk, "credit_day": day,
                     "ex_date": e["ex_date"], "cash_vnd_per_share": e["cash_leg"],
                     "vendor_check": vc.get("status"), "vendor_why": vc.get("why"),
                     "accounts": e["accounts"], "decided_by": "agent",
                     "note": ("giá vốn DNSE giảm đúng KL×tiền + cashDividendReceiving tăng khớp; KHÔNG ghi "
                              "data/corp_actions.json (sổ chỉ chứa sự kiện đổi KL)")})
    if v == BD.UNVERIFIED:
        rg = e.get("registry_check") or {}
        causes = []
        if rg.get("status") == REG_MISMATCH:
            causes.append(f"LỆCH REGISTRY: {rg.get('why')} (registry KHÔNG bị ghi đè)")
        if vc.get("status") == BD.V_MISMATCH or vc.get("qty_unconfirmed"):
            causes.append(f"{'LỆCH' if vc.get('status') == BD.V_MISMATCH else 'THIẾU trục KL ở'} lịch "
                          f"vendor: {vc.get('why')}")
        if not causes:      # §29: không khẳng định nguyên nhân chưa đọc — lý do nằm ở 'Chi tiết'
            causes.append("bị hạ UNVERIFIED (lý do ở 'Chi tiết')")
        upd = e.get("registry_update_proposed")
        # I2 r3 (M2): registry/near-dup ĐÃ có record ⇒ KHÔNG BAO GIỜ dặn ghi record thứ hai (record_proposed
        # id khác + record cũ CONFIRMED = áp hệ số 2 lần) — chỉ sửa/thu hồi record hiện có hoặc đóng.
        act = (f"registry ĐÃ có record {upd['record_id']} cho mã quanh ex này ⇒ {ONE_RECORD_RULE}; số "
               f"broker để sửa record đó: {upd['broker']}" if upd else
               "người chốt: ghi record_proposed (đổi _status thành CONFIRMED, giữ số broker), hoặc bỏ")
        return _bus("question", f"corp-action-broker-unverified-{tk}-{day}",
                    {"question": (f"[Winston] {tk} phiên {day}: broker DNSE (nguồn chính) kết luận "
                                  f"{e.get('event_kind')} ×{e.get('qty_multiplier') or 1} chân tiền "
                                  f"{e.get('cash_leg') or 0:,.0f}đ/cp ex {e['ex_date']} nhưng "
                                  f"{'; '.join(causes)}. Đã hạ UNVERIFIED — KHÔNG ghi registry, KHÔNG "
                                  f"lấy số nguồn khác đè. Winston kiểm nguồn; {act}. Chi tiết: {e['why']}"),
                     "assignee": "Winston", "ticker": tk, "credit_day": day, "ex_date": e["ex_date"],
                     "registry_check": rg or None,
                     "broker": {"qty_multiplier": e.get("qty_multiplier"), "cash_leg": e.get("cash_leg")},
                     "vendor_check": vc, "record_proposed": e.get("record_proposed"),
                     "registry_update_proposed": upd,
                     "accounts": e["accounts"], "urgency": "high"})
    urgency = "normal" if v == BD.INSUFFICIENT else "high"
    hint = {BD.INSUFFICIENT: "chưa đủ bản ghi/giá để quyết (cron 19:25 có thể chạy trước khi DNSE "
                             "credit xong mọi gói vay) — chạy lại tay sau 21:00 hoặc xác nhận tay",
            BD.DEFER_VENDOR: "lịch vendor có sự kiện cổ phiếu cho mã nhưng nhánh vendor KHÔNG xác "
                             "nhận (MISMATCH/không khớp ngày) — nhánh vendor không tự hỏi",
            BD.AMBIGUOUS: "không đủ điều kiện tự xác nhận (lý do cụ thể ở 'Chi tiết')"}.get(v, v)
    upd = e.get("registry_update_proposed")
    act = (f"registry ĐÃ có record {upd['record_id']} cho mã quanh ex này ⇒ {ONE_RECORD_RULE}" if upd else
           "Cần người xác nhận sự kiện + ex-date trước khi ghi data/corp_actions.json")
    return _bus("question", f"corp-action-broker-{v.lower()}-{tk}-{day}",
                {"question": (f"{tk} phiên {day}: nhánh broker ({e.get('event_kind') or 'SHARE_EVENT'}) "
                              f"trả {v} — {hint}. Chi tiết: {e['why']}. Lịch vendor (chỉ tham khảo, "
                              f"KHÔNG tự ghi): {vc.get('status', '-')} {vc.get('vendor') or ''}. {act}."),
                 "ticker": tk, "credit_day": day, "ex_date_if_event": e["ex_date"],
                 "event_kind": e.get("event_kind"), "vendor_check": vc,
                 "registry_update_proposed": upd,
                 "verdict": v, "accounts": e["accounts"], "urgency": urgency})


def _flag_feed_dead(results, vfn):
    """r5 M-A: cờ feed chết đi vào log + sổ + record + bus."""
    if not getattr(vfn, "feed_dead", False):
        return results
    return [dict(r, vendor_feed_dead=True, why=f"{FEED_DEAD_TAG}; {r['why']}",
                 vendor_check=(dict(r["vendor_check"], status=BD.V_FEED_DEAD,
                                    why=f"{FEED_DEAD_TAG} — chưa được vendor xác nhận")
                               if (r.get("vendor_check") or {}).get("status") == BD.V_NO_EVENT
                               else r.get("vendor_check")))
            for r in results]


def run_broker(date_str, dry_run=False, mode="shadow"):
    """Hai pha (RC4): (1) sự kiện ĐỔI KL — quét, ghi registry/sổ, thông báo; (2) SAU ĐÓ mới sàng
    lọc CHỈ-GIÁ (gọi DNSE cho cả danh mục) trong ngân sách thời gian TỔNG
    `BD.PRICE_SCREEN_BUDGET_S` — DNSE chậm không thể đẩy lần ghi registry qua park_trim 19:30;
    hết ngân sách ⇒ dòng báo thiếu dữ liệu, KHÔNG chặn ghi. (3) Re-verify record broker sau ex (RC3)."""
    import time
    print(f"[corp_action_auto_confirm] NHÁNH BROKER mode={mode} date={date_str} dry_run={dry_run}")
    vfn = _vendor_events_fn(date_str)
    qty, ctx = BD.scan_qty(date_str, _px_cum_fn(date_str), vfn, exec_dir=EXEC_DIR,
                           exchange_fn=_exchange_fn())
    qty = _flag_feed_dead([r for r in qty if r["verdict"] != BD.NOT_CANDIDATE], vfn)

    def _price_phase():
        t0 = time.monotonic()
        po = BD.scan_price_only(ctx, deadline=t0 + BD.PRICE_SCREEN_BUDGET_S)
        print(f"  sàng lọc chỉ-giá: {time.monotonic() - t0:.1f}s / ngân sách {BD.PRICE_SCREEN_BUDGET_S}s")
        return _flag_feed_dead([r for r in po if r["verdict"] != BD.NOT_CANDIDATE], vfn)
    if dry_run:
        reg = _registry_view(load_corp_actions_raw())
        po = _price_phase()
        for r in qty + po:
            print(f"  [DRY-RUN] {r['ticker']} ex {r['ex_date']} {r['verdict']} ×"
                  f"{r.get('qty_multiplier', '-')} vendor={(r.get('vendor_check') or {}).get('status', '-')}"
                  f": {r['why'][:300]}")
            rrec = reg.get((r["ticker"], r["ex_date"]))
            if rrec is not None and r["verdict"] in (BD.CONFIRMABLE, BD.UNVERIFIED, BD.CASH_DIVIDEND):
                rg = _registry_reconcile(rrec, r)
                print(f"  [DRY-RUN] {r['ticker']} đối chiếu registry: {rg['status']} — {rg['why']}")
        _reverify_broker_records(date_str, mode, dry_run=True)
        _registry_sweep(date_str, mode, dry_run=True,
                        seen_now={(r["ticker"], r["ex_date"]): r["verdict"] for r in qty + po})
        return 0
    _sandbox_guard()

    def _all():
        rc = _run_broker_locked(date_str, mode, qty, resend=True, phase="qty")
        rc = _run_broker_locked(date_str, mode, _price_phase(), resend=False, phase="price_only") or rc
        rc = _reverify_broker_records(date_str, mode) or rc
        return _registry_sweep(date_str, mode) or rc
    if _LOCK_HELD:
        return _all()
    lk = _lock(LEDGER_FILE)
    if lk is None:
        print(f"❌ không lấy được khoá {LEDGER_FILE}.lock sau {LOCK_WAIT_S}s — tiến trình khác đang "
              f"chạy nhánh broker; KHÔNG ghi gì.")
        return 1
    try:
        return _all()
    finally:
        lk.close()


# ── RC3: đối chiếu lại record broker SAU ex-date ────────────────────────────
REVERIFY_GIVEUP_SESSIONS = 5   # sau N phiên kể từ ex mà vendor vẫn không xác nhận ⇒ hỏi người 1 lần
REVERIFY_LOOKBACK_DAYS = 45    # m4 r3: đọc cả lịch asof TRƯỚC ex (sự kiện vendor nằm ở events_today ngày công bố)


def _vendor_events_post_ex(ticker, ex, upto):
    """Sự kiện vendor của `ticker` có GDKHQ trong ±VENDOR_EX_WINDOW_DAYS quanh `ex`, đọc từ
    `events_today` (+ `backfilled_events` nếu là list sự kiện) của MỌI lịch daily asof ∈
    [ex − REVERIFY_LOOKBACK_DAYS ngày lịch, upto] (m4 r3: bản r2 chỉ đọc asof ≥ ex ⇒ sự kiện vendor
    công bố trước ex — dòng events_today của ngày công bố — không bao giờ được thấy) mà feed TƯƠI
    (`feed_fresh_today` True — ngày STALE lặp lại sự kiện cũ, không phải bằng chứng).
    Chuẩn hoá về dạng vendor_crosscheck (`date` = exright_date, `price_adjusting` theo taxonomy
    CHUNG `corp_action_lib.is_price_adjusting`). Trả (events, n_file_tươi, đã_đọc_ngày_ex?)."""
    from corp_action_lib import is_price_adjusting
    ex_d, end = dt.date.fromisoformat(ex), dt.date.fromisoformat(upto)
    d = ex_d - dt.timedelta(days=REVERIFY_LOOKBACK_DAYS)
    evs, seen, n_fresh, ex_read = [], set(), 0, False
    while d <= end:
        path = os.path.join(CA_DAILY_DIR, f"corp_action_daily_{d.isoformat()}.json")
        try:
            with open(path, encoding="utf-8") as f:
                snap = json.load(f)
        except (OSError, json.JSONDecodeError):
            snap = None
        if isinstance(snap, dict) and snap.get("feed_fresh_today") is True:
            n_fresh += 1
            ex_read = ex_read or d == ex_d
            rows = list(snap.get("events_today") or [])
            if isinstance(snap.get("backfilled_events"), list):
                rows += [x for x in snap["backfilled_events"] if isinstance(x, dict)]
            for e in rows:
                if str(e.get("ticker", "")).upper() != ticker or not e.get("exright_date"):
                    continue
                k = e.get("id") or json.dumps(e, sort_keys=True, default=str)
                if k in seen:
                    continue
                seen.add(k)
                evs.append({"ticker": ticker, "event_code": e.get("event_code"),
                            "date": str(e.get("exright_date"))[:10],
                            "exercise_ratio": e.get("exercise_ratio"),
                            "value_per_share": e.get("value_per_share"),
                            "price_adjusting": is_price_adjusting(e),
                            "title": e.get("event_title_vi")})
        d += dt.timedelta(days=1)                   # ngày lịch: file chỉ có ở ngày có lịch
    return evs, n_fresh, ex_read


def _sessions_since(ex, day):
    from trading_bot.vn_market import next_trading_day
    d, n, end = dt.date.fromisoformat(ex), 0, dt.date.fromisoformat(day)
    while d < end:
        d = next_trading_day(d)
        n += 1
    return n


def _reverify_broker_records(date_str, mode, dry_run=False):
    """RC3: record provenance=broker ĐANG CONFIRMED mà lúc ghi vendor CHƯA xác nhận (NO_EVENT /
    UNREADABLE / FEED_DEAD / PARTIAL) và ex ≤ date_str ⇒ đối chiếu LẠI với lịch vendor sau ex
    (vendor sống lại / lịch ngày ex). Kết quả, MỖI record MỘT lần (sổ `done`, bus rc=0):
      VERIFIED ⇒ finding; MISMATCH (hoặc thiếu trục KL) ⇒ question [Winston] (KHÔNG sửa record —
      người quyết REVOKED); sau REVERIFY_GIVEUP_SESSIONS phiên vẫn chưa xác nhận ⇒ question để
      user CHẤP NHẬN 'không đối chiếu lại' hoặc Winston kiểm. Chưa tới hạn ⇒ in trạng thái, chờ.
    shadow / dry-run ⇒ CHỈ IN (không bus, không sổ). Không bao giờ ghi data/corp_actions.json."""
    rc = 0
    recs = [r for r in load_corp_actions_raw()
            if str(r.get("provenance", "")).lower() == "broker"
            and str(r.get("_status", "")).upper().startswith("CONFIRMED")
            and (r.get("vendor_check") or {}).get("status") != BD.V_VERIFIED
            and str(r.get("ex_date", ""))[:10] <= date_str]
    if not recs:
        return 0
    quiet = dry_run or mode != "live"
    try:
        _intents, done = BD.ledger_state(LEDGER_FILE)
    except BD.CorpActionLedgerError as e:       # sổ hỏng ⇒ vẫn đối chiếu (hỏi thừa an toàn hơn im)
        print(f"  ⚠ sổ broker đọc hỏng ({e}) ⇒ không biết record nào đã đối chiếu lại, đối chiếu hết")
        done = set()
    for r in recs:
        rid, tk, ex = str(r.get("id")), str(r.get("ticker", "")).upper(), str(r.get("ex_date"))[:10]
        if any(tuple(["reverify", rid, x]) in done for x in ("VERIFIED", "MISMATCH", "GIVEUP")):
            continue
        try:
            m = float(r.get("qty_multiplier"))
        except (TypeError, ValueError):
            m = float("nan")
        cash = _cash_leg_as_read(r)
        evs, n_fresh, ex_read = _vendor_events_post_ex(tk, ex, date_str)
        n_sess = _sessions_since(ex, date_str)
        bad = not (math.isfinite(m) and math.isfinite(cash))
        vc = (BD.vendor_crosscheck(ex, m, cash, evs) if n_fresh and not bad else
              {"status": BD.V_MISMATCH, "vendor": [],
               "why": (f"record có qty_multiplier/cash_leg không đọc được {r.get('qty_multiplier')!r}/"
                       f"{r.get('cash_leg_vnd_per_share')!r}")} if bad else
              {"status": BD.V_UNREADABLE, "vendor": [],
               "why": (f"chưa có lịch vendor TƯƠI nào từ {REVERIFY_LOOKBACK_DAYS} ngày trước ex {ex} tới "
                       f"{date_str} (feed chết/STALE/thiếu file)")})
        if vc["status"] == BD.V_MISMATCH or vc.get("qty_unconfirmed"):
            res = "MISMATCH"
        elif vc["status"] == BD.V_VERIFIED:
            res = "VERIFIED"
        elif n_sess >= REVERIFY_GIVEUP_SESSIONS:
            res = "GIVEUP"
        else:
            res = None
        print(f"  [re-verify {rid}] ex {ex} (+{n_sess} phiên, {n_fresh} lịch tươi, đọc được ngày ex: "
              f"{ex_read}): vendor {vc['status']} — {vc['why']} ⇒ {res or 'CHỜ'}")
        if res is None or quiet:
            continue
        base = {"record_id": rid, "ticker": tk, "ex_date": ex, "qty_multiplier": r.get("qty_multiplier"),
                "cash_leg_vnd_per_share": r.get("cash_leg_vnd_per_share"),
                "vendor_check_at_write": (r.get("vendor_check") or {}).get("status"),
                "vendor_check_now": vc, "sessions_since_ex": n_sess, "fresh_calendars": n_fresh}
        if res == "VERIFIED":
            ok = _notify_once("finding", ["reverify", rid, res], f"corp-action-broker-reverify-{tk}-{ex}",
                              dict(base, status="VERIFIED_POST_EX", decided_by="agent",
                                   note="vendor xác nhận record broker SAU ex — record giữ nguyên"))
        elif res == "MISMATCH":
            ok = _notify_once("question", ["reverify", rid, res], f"corp-action-broker-reverify-{tk}-{ex}",
                              dict(base, assignee="Winston", urgency="high",
                                   question=(f"[Winston] {tk} ex {ex}: record broker {rid} ×{r.get('qty_multiplier')} "
                                             f"chân tiền {cash:,.0f}đ/cp ĐÃ ÁP DỤNG, nay lịch vendor sau ex LỆCH: "
                                             f"{vc['why']}. KHÔNG tự sửa registry. Winston kiểm nguồn; người "
                                             f"quyết giữ hay REVOKED record.")))
        else:
            ok = _notify_once("question", ["reverify", rid, res], f"corp-action-broker-reverify-{tk}-{ex}",
                              dict(base, urgency="normal",
                                   question=(f"{tk} ex {ex}: record broker {rid} ×{r.get('qty_multiplier')} đã "
                                             f"áp dụng {n_sess} phiên mà vendor VẪN chưa xác nhận ({vc['status']}: "
                                             f"{vc['why']}). User chấp nhận 'không đối chiếu lại' (giữ record) "
                                             f"hay Winston kiểm nguồn vendor? Hỏi 1 lần, sẽ không nhắc lại.")))
        rc = rc or (0 if ok else 1)
    return rc


def _run_broker_locked(date_str, mode, results, resend=True, phase="qty"):
    """`resend` — gửi bù mục sổ dở của lượt trước (chỉ pha đầu, tránh gửi 2 lần trong 1 lượt)."""
    intents, done = BD.ledger_state(LEDGER_FILE)
    pending = ([e for k, e in intents.items() if k not in done and e.get("mode") == mode]
               if resend else [])
    actions_raw = load_corp_actions_raw()
    reg_recs = _registry_view(actions_raw)          # ≥2 record hiệu lực ⇒ record giả _dup_ids (m6)
    from zoneinfo import ZoneInfo
    now_ict = dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%dT%H:%M:%S+07:00")
    new, superseded, observed = [], set(), []
    for r in results:
        tk, ex, v = r["ticker"], r["ex_date"], r["verdict"]
        vc = r.get("vendor_check") or {}
        print(f"  [{tk}] ex {ex} {v} (vendor {vc.get('status', '-')}): {r['why']}")
        rrec = reg_recs.get((tk, ex))
        reg_has = str(rrec.get("_status", ""))[:40] if rrec is not None else None
        regc = None
        # chỉ sự kiện KL mới có thể thành record ⇒ chỉ nó cần chặn ×2 lần; tính TRƯỚC nhánh "registry
        # khớp": registry khớp mà CÒN record cùng mã ở ex khác gần đó ⇒ có thể đã áp 2 lần ⇒ hỏi.
        dup = _near_duplicate(actions_raw, tk, date_str, ex) if r.get("kind") is None else None
        if rrec is not None and v in (BD.CONFIRMABLE, BD.UNVERIFIED, BD.CASH_DIVIDEND):
            # RC1: đối chiếu record registry (MỌI provenance) với số broker — KHÔNG im lặng bỏ qua.
            regc = _registry_reconcile(rrec, r)
            print(f"  [{tk}] registry ĐÃ có ({tk}, {ex}) — đối chiếu: {regc['status']} — {regc['why']}")
            if regc["status"] == REG_MISMATCH:
                r = dict(r, verdict=BD.UNVERIFIED,
                         why=f"LỆCH REGISTRY: {regc['why']} ⇒ KHÔNG ghi đè, Winston kiểm; detector: {v} — {r['why']}")
                v = BD.UNVERIFIED
            elif v != BD.UNVERIFIED and not dup:
                print(f"  [{tk}] registry khớp broker ⇒ không ghi/hỏi lại")
                if mode == "live":
                    # m7 r3 (§26): câu hỏi cũ cùng mã/phiên nay đã được registry khớp broker giải quyết
                    superseded |= _close_resolved(tk, date_str, intents, done, regc)
                    # Bằng chứng "broker ĐÃ thấy credit" cho credit-watch (m1) — dòng sổ CHỈ quan sát
                    # (intent + done cùng lúc, 0 bus): thiếu nó, phiên ex sau sẽ báo QUÁ HẠN giả.
                    obs = {"kind": "intent", "at": now_ict, "mode": mode, "ticker": tk, "credit_day": date_str,
                           "ex_date": ex, "verdict": v, "why": r["why"], "registry_has": reg_has,
                           "registry_check": regc, "phase": phase, "observation_only": True,
                           "qty_multiplier": r.get("qty_multiplier"), "cash_leg": r.get("cash_leg"),
                           "accounts": {}}
                    obs["key"] = BD.ledger_key(obs)
                    if not any(e.get("ticker") == tk and e.get("ex_date") == ex for e in intents.values()):
                        observed.append(obs)
                    continue
            # MATCH nhưng vendor LỆCH (UNVERIFIED) ⇒ vẫn đi tiếp để hỏi Winston về vendor.
        elif rrec is not None:
            print(f"  [{tk}] registry ĐÃ có ({tk}, {ex}) — {reg_has!r}; broker {v} chưa đối chiếu được ⇒ vẫn hỏi người")
        if reg_has is not None and mode != "live":
            print(f"  [{tk}] (shadow) registry đã có ({tk}, {ex}) — {reg_has!r}; vẫn ghi sổ để so sánh")
        if dup:
            # m7: UNVERIFIED (lệch vendor/registry) GIỮ verdict ⇒ câu hỏi vẫn gọi tên Winston.
            nv = BD.UNVERIFIED if v == BD.UNVERIFIED else BD.AMBIGUOUS
            r = dict(r, verdict=nv, why=f"{dup[0]}; detector: {v} — {r['why']}")
            v = nv
        # I2 r3 (M2): record hiện có cho mã quanh ex (cùng ex hoặc near-dup) ⇒ đường trả lời chỉ được
        # SỬA/THU HỒI nó — KHÔNG mang record_proposed (id khác ⇒ người ghi thêm = áp hệ số 2 lần).
        existing = rrec.get("id") if rrec is not None else (dup[1] if dup else None)
        entry = {"kind": "intent", "at": now_ict, "mode": mode, "ticker": tk,
                 "credit_day": date_str, "ex_date": ex, "verdict": v, "why": r["why"],
                 "event_kind": r.get("kind") or "SHARE_EVENT",
                 "qty_multiplier": r.get("qty_multiplier"), "cash_leg": r.get("cash_leg"),
                 "px_cum": r.get("px_cum"), "vendor_feed_dead": bool(r.get("vendor_feed_dead")),
                 "vendor_check": r.get("vendor_check"), "registry_has": reg_has,
                 "registry_check": regc, "phase": phase,
                 "accounts": {k: {kk: vv for kk, vv in a.items() if kk != "lots"}
                              for k, a in r["accounts"].items()}}
        entry["key"] = BD.ledger_key(entry)
        if tuple(entry["key"]) in intents:
            print(f"  [{tk}] sổ broker đã có {entry['key']} ⇒ không lặp (idempotent)")
            continue
        if existing is not None and v != BD.CONFIRMABLE:
            entry["registry_update_proposed"] = {
                "record_id": str(existing), "rule": ONE_RECORD_RULE,
                "broker": {"ex_date": ex, "qty_multiplier": r.get("qty_multiplier"),
                           "cash_leg_vnd_per_share": r.get("cash_leg")}}
        elif v == BD.CONFIRMABLE or (v == BD.UNVERIFIED and r.get("qty_multiplier")):
            rec = BD.build_record(r, now_ict)
            if r.get("vendor_feed_dead"):
                rec["evidence"].append(FEED_DEAD_TAG)
            # UNVERIFIED: record chỉ là ĐỀ XUẤT trong câu hỏi cho người — KHÔNG BAO GIỜ ghi registry
            entry["record" if v == BD.CONFIRMABLE else "record_proposed"] = rec
        new.append(entry)
    # registry đã có (mã, ex) ⇒ KHÔNG BAO GIỜ ghi thêm (RC1: không ghi đè, không trùng).
    new_recs = [e["record"] for e in new if mode == "live" and e["verdict"] == BD.CONFIRMABLE
                and e.get("registry_has") is None]
    rc = 0
    if new_recs:
        try:   # validate + bất biến I1 TRƯỚC mọi ghi — hỏng ⇒ 0 ghi registry, 0 intent cho mục CONFIRMABLE
            _validate_for_write(actions_raw + new_recs, actions_raw)
        except CA.CorpActionError as e:
            # Cron lượt sau quét PHIÊN KHÁC ⇒ sẽ KHÔNG tự thử lại ca này; chỉ chạy tay
            # `--date <D>` sau khi sửa registry mới thử lại (arch-review v2 N2). Các mục KHÔNG
            # phải CONFIRMABLE của lượt vẫn đi tiếp (không nuốt câu hỏi của mã khác).
            print(f"\n❌ NHÁNH BROKER KHÔNG GHI registry — validate() từ chối: {e}")
            _bus("question", f"corp-action-broker-validate-reject-{date_str}",
                 {"question": (f"validate() từ chối khi ghi record broker: {e}. Sửa "
                               f"data/corp_actions.json rồi chạy lại TAY: python3 "
                               f"mike/bin/corp_action_auto_confirm.py --date {date_str} "
                               f"(cron lượt sau quét phiên khác, không tự thử lại)."),
                  "error": str(e), "candidates": [x["ticker"] for x in new_recs],
                  "urgency": "high"})
            new = [x for x in new if x["verdict"] != BD.CONFIRMABLE]
            new_recs = []
            rc = 1
    if observed:
        BD.ledger_append(observed + [{"kind": "done", "key": o["key"], "at": now_ict, "observation_only": True}
                                     for o in observed], LEDGER_FILE)
    if superseded:      # việc dở lượt trước đã được giải quyết ⇒ KHÔNG gửi bù câu hỏi đã hết thời
        pending = [e for e in pending if tuple(e.get("key") or BD.ledger_key(e)) not in superseded]
        BD.ledger_append([{"kind": "done", "key": list(k), "at": now_ict, "superseded": True}
                          for k in sorted(superseded, key=str)], LEDGER_FILE)
    if new:
        BD.ledger_append(new, LEDGER_FILE)              # pha 1: intent TRƯỚC mọi tác dụng ngoài
    if new_recs:
        write_corp_actions(actions_raw + new_recs)
    todo = pending + new
    for e in todo:
        e.setdefault("key", BD.ledger_key(e))          # dòng sổ định dạng cũ (không có key)
    if not todo:
        print("  → không mục mới / không việc dở.")
        return rc
    try:
        registry_ids = {a["id"] for a in CA.load_corp_actions(CORP_ACTIONS_FILE)}
    except CA.CorpActionError as e:
        # Registry hỏng (đã hỏi ở validate-reject) ⇒ KHÔNG đọc lại được: mục CONFIRMABLE dở (nếu
        # có) bị báo write-incomplete — đúng sự thật "không xác minh được", không giả là đã ghi.
        print(f"  ❌ load_corp_actions() lỗi khi đọc lại: {e}")
        registry_ids = set()
        rc = 1
    if pending:
        print(f"  ↻ gửi bù {len(pending)} mục sổ chưa có 'done' (lượt trước bị kill/bus lỗi)")
    finished = []
    if mode == "live":
        for e in todo:
            if e["verdict"] == BD.CONFIRMABLE and e["record"]["id"] not in registry_ids:
                rc = 1                                       # §6 verify artifact: không thấy ⇒ lỗi
            if _finish_live(e, registry_ids) == 0:
                finished.append(e)
                if e["verdict"] == BD.CONFIRMABLE and e["record"]["id"] in registry_ids:
                    _close_stale_questions(e, intents)
            else:
                rc = 1
    else:
        if _bus("finding", f"corp-action-broker-shadow-{date_str}",
                {"mode": "shadow", "note": "KHÔNG ghi registry — cửa sổ quan sát chờ user duyệt bật live",
                 "phase": phase,
                 "results": [dict({k: e.get(k) for k in ("ticker", "credit_day", "ex_date", "verdict",
                                                          "event_kind", "qty_multiplier", "cash_leg",
                                                          "registry_has", "why")},
                                  vendor_check=(e.get("vendor_check") or {}).get("status"),
                                  registry_check=(e.get("registry_check") or {}).get("status"))
                             for e in todo]}) == 0:
            finished = todo
        else:
            rc = 1
    if finished:
        BD.ledger_append([{"kind": "done", "key": e["key"], "at": now_ict} for e in finished],
                         LEDGER_FILE)                    # pha 2: chỉ sau khi bus nhận
    print(f"Xong nhánh broker: {len(new)} mục sổ mới, {len(pending)} gửi bù, {len(new_recs)} "
          f"record ghi registry, {len(finished)}/{len(todo)} đã thông báo.")
    return rc


def main():
    ap = argparse.ArgumentParser(description="Tự động xác nhận corp action khi broker credit")
    ap.add_argument("--dry-run", action="store_true",
                    help="In kết quả nhưng KHÔNG ghi file / gửi bus")
    ap.add_argument("--date", default=None,
                    help="Ngày cần kiểm (mặc định: hôm nay ICT)")
    a = ap.parse_args()
    date_str = a.date or today_ict()
    sys.exit(run(date_str, dry_run=a.dry_run))


if __name__ == "__main__":
    main()
