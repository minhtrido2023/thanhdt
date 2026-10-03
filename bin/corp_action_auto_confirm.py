#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tự động xác nhận sự kiện doanh nghiệp (BONUS_ISSUE / SPLIT) khi DNSE credit cổ phiếu.

VÒNG LẶP 5 LẦN (VHM, MBB, BID, VIX, MSB) đều cùng mẫu:
  corp_action_daily biết sự kiện từ sáng (07:30) qua upcoming_events_held (days_ahead=1),
  nhưng DNSE credit trước ex_date 1 phiên (~18:30–19:00 ICT), trong khi DollarBill xây plan
  tại 19:00–19:10. Kết quả: sổ lô ≠ broker → BLOCKED_RECONCILE cho mã đó.

Script này chạy lúc 19:30 ICT (sau khi DNSE credit, trước DollarBill) và tự CONFIRMED khi
đủ bằng chứng 2 nguồn ĐỘC LẬP:
  (1) upcoming_events_held có event trong cửa sổ days_ahead ≤ 1
  (2) Broker: openQuantity và costPrice đổi đúng hệ số trong ngày

⚠️ CHỈ xác nhận sự kiện LÀM TĂNG số lượng (BONUS_ISSUE / SPLIT). Cổ tức tiền mặt không đi qua
đây. Gộp cổ phiếu (reverse split) chưa thiết kế (qty_multiplier > 1 là điều kiện cứng trong corp_actions.py).

NHÁNH BROKER (user duyệt 2026-10-03, phương án B — feed vendor chết từ 2026-09-26, ca TPB):
sau nhánh vendor, `run_broker()` quét MỌI mã đang giữ bằng `corp_action_broker_detect` — KL +
tổng giá vốn + giá tham chiếu cùng kể một sự kiện, credit sau 15:00 ⇒ ex-date = phiên kế tiếp.
Công tắc `MIKE_CA_BROKER_SOURCE`:
  off    — không chạy nhánh broker (hành vi trước 2026-10-03, byte-identical).
  shadow — MẶC ĐỊNH: phát hiện + ghi sổ `data/corp_action_broker_ledger.jsonl` + 1 bus finding
           tóm tắt; KHÔNG ghi `data/corp_actions.json`, KHÔNG hỏi user.
  live   — ghi record CONFIRMED provenance=broker vào registry (validate() + atomic); MƠ HỒ /
           CHƯA ĐỦ / vendor có sự kiện mà không xác nhận ⇒ bus question (1 lần / mã / phiên /
           verdict), KHÔNG ghi.
Sổ 2 pha (intent → tác dụng ngoài → done khi bus rc=0): kill/bus lỗi ⇒ lượt sau GỬI BÙ.
⚠️ Phụ thuộc NGẦM: nhánh broker chỉ đọc dnse_raw do tiến trình khác ghi (EOD/park/verify chạy
19:0x–19:1x); không có bản ghi positions nào sau credit ⇒ INSUFFICIENT/không thấy.
Bật `live` cần user duyệt sau khi xem cửa sổ shadow.

Chạy: python3 mike/bin/corp_action_auto_confirm.py [--dry-run] [--date YYYY-MM-DD]
"""
import argparse
import datetime as dt
import json
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
DAYS_AHEAD_MAX  = 1      # chỉ xét sự kiện broker có thể credit trong hôm nay
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
    """Từ corp_action_daily_{date}.json → upcoming_events_held khớp điều kiện."""
    path = os.path.join(CA_DAILY_DIR, f"corp_action_daily_{date_str}.json")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    held = d.get("upcoming_events_held") or []
    out = []
    for ev in held:
        if (ev.get("price_adjusting") and
                ev.get("event_code") in CONFIRMED_CODES and
                int(ev.get("days_ahead") or 999) <= DAYS_AHEAD_MAX):
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
    """
    for i, rec in enumerate(actions_list):
        CA.validate(rec, i)  # ném CorpActionError nếu hỏng — KHÔNG bắt ở đây, để caller quyết định
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
    try:
        return _run_both(date_str, dry_run, mode)
    finally:
        if lk:
            lk.close()


def _run_both(date_str, dry_run, mode):
    global _LOCK_HELD
    _LOCK_HELD = True
    try:
        rc = run_vendor(date_str, dry_run=dry_run)
    finally:
        _LOCK_HELD = False
    try:
        _LOCK_HELD = True
        rc_b = run_broker(date_str, dry_run=dry_run, mode=mode)
    except Exception as e:   # crash nhánh broker KHÔNG được chỉ nằm trong log cron (§29: lỗi thật)
        import traceback
        tb = traceback.format_exc()
        print(tb)
        if not dry_run:
            _bus("error", f"corp-action-broker-crash-{date_str}",
                 {"error": f"{type(e).__name__}: {e}", "traceback_tail": tb[-1500:], "mode": mode})
        rc_b = 1
    finally:
        _LOCK_HELD = False
    return rc or rc_b


def run_vendor(date_str, dry_run=False):
    """Nhánh vendor. Lỗi ở đường hỏi người (N9 / tỉ lệ lệch broker) KHÔNG được làm mất lô vendor
    (arch-review v4 #6: bản cũ để ngoại lệ ledger_append/_bus thoát ⇒ mất cả lô, 0 bus event):
    gom lỗi, chạy hết lô, rồi báo 1 bus question (urgency high) + rc=1."""
    ask_failed = []
    rc = _run_vendor(date_str, dry_run, ask_failed)
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


def _run_vendor(date_str, dry_run, ask_failed):
    print(f"[corp_action_auto_confirm] date={date_str} dry_run={dry_run}")

    candidates = get_candidate_events(date_str)
    if not candidates:
        print("  → không có sự kiện nào trong upcoming_events_held cần kiểm.")
        return 0

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


# ── Nhánh BROKER ───────────────────────────────────────────────────────────

BROKER_MODES = ("off", "shadow", "live")
BUS_TIMEOUT_S = 60
_LOCK_HELD = False        # run() đã giữ khoá ⇒ run_broker không xin lại (flock 2 fd cùng tiến trình = tự khoá)
# Gốc PRODUCTION tính ĐỘC LẬP với các biến module selfcheck hay đổi (LEDGER_FILE/EXEC_DIR/
# BD.LEDGER_FILE) — guard sandbox so với cái này (arch-review v2 N4).
_PROD_DATA = os.path.realpath(os.path.join(WC_ROOT, "data"))
BROKER_VENDOR_MULT_TOL = 1e-3   # hệ số vendor vs record broker CÙNG ex: lệch >0,1% ⇒ hỏi (D3 replay ≤0,1%)
NEAR_DUP_DAYS = 10        # record CÙNG MÃ có ex_date cách credit_day ≤ N ngày lịch ⇒ không ghi, hỏi
LOCK_WAIT_S = 120


def broker_mode():
    """`MIKE_CA_BROKER_SOURCE` — giá trị lạ ⇒ shadow (không bao giờ tự lên `live` do gõ nhầm)."""
    raw = os.environ.get("MIKE_CA_BROKER_SOURCE", "shadow").strip().lower()
    if raw not in BROKER_MODES:
        print(f"  ⚠ MIKE_CA_BROKER_SOURCE={raw!r} không hợp lệ {BROKER_MODES} ⇒ dùng 'shadow'")
        return "shadow"
    return raw


def _vendor_events_fn(date_str):
    """ticker → MỌI sự kiện của mã trong `upcoming_events_held` lịch vendor ngày `date_str`.
    Feed đứng vẫn ra file (feed_status STALE, ca TPB 10-01) ⇒ đọc bình thường. KHÔNG có file /
    chỉ có `_FAILED.json` (pipeline vendor không chạy hoặc trượt cổng) hay file đọc hỏng ⇒
    VENDOR_UNREADABLE cho mọi mã + in lý do thật (§29) — fail-closed, KHÔNG coi là "vendor không
    có sự kiện" (arch-review v4 #5: bản cũ coi file thiếu là [] ⇒ live có thể CONFIRM)."""
    path = os.path.join(CA_DAILY_DIR, f"corp_action_daily_{date_str}.json")
    if not os.path.exists(path):
        failed = os.path.join(CA_DAILY_DIR, f"corp_action_daily_{date_str}_FAILED.json")
        why = ("chỉ có " + os.path.basename(failed) if os.path.exists(failed)
               else "không có file")
        print(f"  ❌ lịch vendor {path}: {why} ⇒ mọi ứng viên broker MƠ HỒ (VENDOR_UNREADABLE)")
        return lambda tk: BD.VENDOR_UNREADABLE
    try:
        with open(path, encoding="utf-8") as f:
            held = json.load(f).get("upcoming_events_held") or []
    except (OSError, json.JSONDecodeError, AttributeError) as e:
        print(f"  ❌ lịch vendor {path} đọc hỏng: {type(e).__name__}: {e} ⇒ mọi ứng viên broker MƠ HỒ")
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
    Lỗi/thiếu ⇒ None ⇒ detector trả INSUFFICIENT, KHÔNG đoán."""
    def fn(ticker, day):
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
    thể CÙNG sự kiện được người ký với ex khác (lịch thiếu ngày nghỉ…) — ghi thêm = áp hệ số 2 lần."""
    d0 = dt.date.fromisoformat(credit_day)
    for r in raw_actions:
        if str(r.get("ticker", "")).upper() != tk:
            continue
        try:
            rex = dt.date.fromisoformat(str(r.get("ex_date", ""))[:10])
        except ValueError:
            return f"record {r.get('id')!r} cùng mã có ex_date không đọc được {r.get('ex_date')!r}"
        if rex.isoformat() != ex and abs((rex - d0).days) <= NEAR_DUP_DAYS:
            return (f"registry đã có {r.get('id')!r} ({str(r.get('_status', ''))[:30]!r}) ex "
                    f"{rex} cách phiên credit {credit_day} ≤ {NEAR_DUP_DAYS} ngày — có thể CÙNG sự "
                    f"kiện với ex khác ⇒ không ghi thêm (×hệ số 2 lần)")
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


def _ask_vendor_vs_broker(ticker, ex_date, why, rid):
    """Vendor ex ≠ ex record broker gần đó (N9). Khoá hỏi có id record broker (arch-review v4 #9):
    người REVOKE record cũ rồi broker ghi record MỚI cho cùng (mã, ex vendor) ⇒ hỏi lại."""
    _ask_once(["vendor-vs-broker", ticker, ex_date, rid, "ASKED"],
              f"corp-action-vendor-vs-broker-{ticker}-{ex_date}",
              {"question": f"{ticker}: lịch vendor ex {ex_date} nhưng {why}. Cần người xác "
                           f"nhận ex thật và thu hồi (REVOKED) record sai.",
               "ticker": ticker, "vendor_ex_date": ex_date, "broker_record_id": rid,
               "urgency": "high"})


def _ask_ratio_vs_broker(ticker, ex_date, why, rid):
    """CÙNG (mã, ex) với record broker nhưng tỉ lệ khác (arch-review v4 #12) — hỏi 1 lần/record."""
    _ask_once(["vendor-ratio-vs-broker", ticker, ex_date, rid, "ASKED"],
              f"corp-action-vendor-ratio-vs-broker-{ticker}-{ex_date}",
              {"question": f"{ticker} ex {ex_date}: {why}. Registry giữ hệ số BROKER (không ghi đè). "
                           f"Cần người đối chiếu tỉ lệ thật; sai ⇒ REVOKED record rồi ghi tay.",
               "ticker": ticker, "ex_date": ex_date, "broker_record_id": rid, "urgency": "high"})


def _ask_lock_unavailable(date_str, mode):
    """Không lấy được khoá ⇒ CẢ nhánh vendor lẫn broker không chạy. Bus `question` urgency high
    (ops_health_check leo thang question, KHÔNG leo thang `error` — arch-review v4 #3), 1 lần/ngày:
    marker tạo nguyên tử O_EXCL cạnh sổ (không cần khoá — chính khoá đang bị giữ); bus lỗi ⇒ xoá
    marker để lượt sau hỏi lại."""
    marker = f"{LEDGER_FILE}.lockfail-{date_str}"
    try:
        os.close(os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
    except FileExistsError:
        print(f"  đã hỏi người về khoá ngày {date_str} ⇒ không hỏi lại")
        return
    try:
        rc = _bus("question", f"corp-action-lock-unavailable-{date_str}",
                  {"question": (f"Không lấy được khoá {LEDGER_FILE}.lock sau {LOCK_WAIT_S}s — nhánh "
                                f"vendor VÀ broker đều KHÔNG chạy lượt {date_str}. Kiểm tiến trình "
                                f"corp_action_auto_confirm đang treo rồi chạy lại tay --date {date_str}."),
                   "mode": mode, "urgency": "high"})
    except Exception as e:  # §29
        print(f"  ❌ không gửi được bus question khoá: {type(e).__name__}: {e}")
        rc = 1
    if rc != 0:
        os.remove(marker)


def _ask_once(key, topic, payload):
    """Hỏi người MỘT lần cho mỗi `key`: bus rc=0 ⇒ ghi dòng `done` vào sổ ⇒ lượt sau im. Bus lỗi ⇒
    không đánh dấu (lượt sau hỏi lại). Sổ đọc hỏng ⇒ vẫn hỏi (an toàn), nói lỗi thật."""
    from zoneinfo import ZoneInfo
    ticker = key[1]
    _sandbox_guard()
    try:
        _intents, done = BD.ledger_state(LEDGER_FILE)
    except BD.CorpActionLedgerError as e:       # sổ hỏng ⇒ vẫn hỏi (an toàn), nói lỗi thật (§29)
        print(f"  ⚠ sổ broker đọc hỏng ({e}) ⇒ không kiểm được đã hỏi chưa, hỏi lại")
        done = set()
    if tuple(key) in done:
        print(f"  [{ticker}] đã hỏi người {key} ⇒ không hỏi lại")
        return
    rc = _bus("question", topic, payload)
    if rc == 0:
        now_ict = dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%dT%H:%M:%S+07:00")
        BD.ledger_append([{"kind": "done", "key": key, "at": now_ict}], LEDGER_FILE)


def _close_stale_questions(e, intents):
    """§26: lượt trước (cùng mã, cùng phiên, live) đã HỎI vì INSUFFICIENT/AMBIGUOUS/DEFER, nay
    record đã CONFIRMED ⇒ đóng các câu hỏi đó bằng `answer` đúng topic, kèm bằng chứng record id.
    Lỗi gửi chỉ in ra (question vẫn mở = an toàn, người đọc thấy record ở finding confirm)."""
    for k, old in intents.items():
        if (old.get("mode") == "live" and old.get("ticker") == e["ticker"]
                and old.get("credit_day") == e["credit_day"]
                and old.get("verdict") in (BD.INSUFFICIENT, BD.AMBIGUOUS, BD.DEFER_VENDOR)):
            _bus("answer", f"corp-action-broker-{old['verdict'].lower()}-{e['ticker']}-{e['credit_day']}",
                 {"resolution": (f"lượt sau đã CONFIRMED {e['record']['id']} ×{e['qty_multiplier']} "
                                 f"ex {e['ex_date']} (provenance=broker)"),
                  "evidence": f"data/corp_actions.json id={e['record']['id']}",
                  "decided_by": "agent"})


def _finish_live(e, registry_ids):
    """Gửi thông báo cho MỘT mục sổ ở live. Trả rc bus. Không khẳng định điều chưa kiểm (§29)."""
    tk, day, v = e["ticker"], e["credit_day"], e["verdict"]
    if v == BD.CONFIRMABLE:
        rid = e["record"]["id"]
        if rid in registry_ids:
            return _bus("finding", f"corp-action-broker-confirm-{tk}",
                        {"status": "AUTO_CONFIRMED_BROKER", "event_id": rid, "ticker": tk,
                         "ex_date": e["ex_date"], "qty_multiplier": e["qty_multiplier"],
                         "cash_leg_vnd_per_share": e["cash_leg"],
                         "evidence": e["record"]["evidence"], "decided_by": "agent",
                         "note": "provenance=broker (vendor feed không có sự kiện); thu hồi: _status REVOKED"})
        return _bus("question", f"corp-action-broker-write-incomplete-{tk}-{day}",
                    {"question": (f"{tk}: nhánh broker đã quyết CONFIRMABLE ×{e['qty_multiplier']} "
                                  f"ex {e['ex_date']} nhưng load_corp_actions() KHÔNG thấy record "
                                  f"{rid} trong registry (ghi dở/bị kill/đọc lại hỏng). Cần người "
                                  f"kiểm data/corp_actions.json."),
                     "ticker": tk, "credit_day": day, "record": e["record"], "urgency": "high"})
    urgency = "normal" if v == BD.INSUFFICIENT else "high"
    hint = {BD.INSUFFICIENT: "chưa đủ bản ghi/giá để quyết (cron 19:25 có thể chạy trước khi DNSE "
                             "credit xong mọi gói vay) — chạy lại tay sau 21:00 hoặc xác nhận tay",
            BD.DEFER_VENDOR: "lịch vendor có sự kiện cổ phiếu cho mã nhưng nhánh vendor KHÔNG xác "
                             "nhận (MISMATCH/không khớp ngày) — nhánh vendor không tự hỏi",
            BD.AMBIGUOUS: "không đủ điều kiện tự xác nhận (lý do cụ thể ở 'Chi tiết')"}.get(v, v)
    return _bus("question", f"corp-action-broker-{v.lower()}-{tk}-{day}",
                {"question": (f"{tk} phiên {day}: broker cho thấy KL tăng với tổng giá vốn không "
                              f"tăng, nhánh broker trả {v} — {hint}. Chi tiết: {e['why']}. Cần người "
                              f"xác nhận sự kiện + ex-date trước khi ghi data/corp_actions.json."),
                 "ticker": tk, "credit_day": day, "ex_date_if_event": e["ex_date"],
                 "verdict": v, "accounts": e["accounts"], "urgency": urgency})


def run_broker(date_str, dry_run=False, mode="shadow"):
    print(f"[corp_action_auto_confirm] NHÁNH BROKER mode={mode} date={date_str} dry_run={dry_run}")
    results = [r for r in BD.scan_day(date_str, _px_cum_fn(date_str), _vendor_events_fn(date_str),
                                      exec_dir=EXEC_DIR, exchange_fn=_exchange_fn())
               if r["verdict"] != BD.NOT_CANDIDATE]
    if dry_run:
        for r in results:
            print(f"  [DRY-RUN] {r['ticker']} ex {r['ex_date']} {r['verdict']} ×"
                  f"{r.get('qty_multiplier', '-')}: {r['why'][:300]}")
        return 0
    _sandbox_guard()
    if _LOCK_HELD:
        return _run_broker_locked(date_str, mode, results)
    lk = _lock(LEDGER_FILE)
    if lk is None:
        print(f"❌ không lấy được khoá {LEDGER_FILE}.lock sau {LOCK_WAIT_S}s — tiến trình khác đang "
              f"chạy nhánh broker; KHÔNG ghi gì.")
        return 1
    try:
        return _run_broker_locked(date_str, mode, results)
    finally:
        lk.close()


def _run_broker_locked(date_str, mode, results):
    intents, done = BD.ledger_state(LEDGER_FILE)
    pending = [e for k, e in intents.items() if k not in done and e.get("mode") == mode]
    actions_raw = load_corp_actions_raw()
    in_registry = {(str(r.get("ticker", "")).upper(), str(r.get("ex_date", ""))[:10]):
                   str(r.get("_status", ""))[:40] for r in actions_raw}
    from zoneinfo import ZoneInfo
    now_ict = dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%dT%H:%M:%S+07:00")
    new = []
    for r in results:
        tk, ex, v = r["ticker"], r["ex_date"], r["verdict"]
        print(f"  [{tk}] ex {ex} {v}: {r['why']}")
        if (tk, ex) in in_registry:
            print(f"  [{tk}] registry ĐÃ có ({tk}, {ex}) — {in_registry[(tk, ex)]!r} ⇒ không ghi/hỏi lại")
            continue
        dup = _near_duplicate(actions_raw, tk, date_str, ex)
        if dup:
            r = dict(r, verdict=BD.AMBIGUOUS, why=f"{dup}; detector: {v} — {r['why']}")
            v = BD.AMBIGUOUS
        entry = {"kind": "intent", "at": now_ict, "mode": mode, "ticker": tk,
                 "credit_day": date_str, "ex_date": ex, "verdict": v, "why": r["why"],
                 "qty_multiplier": r.get("qty_multiplier"), "cash_leg": r.get("cash_leg"),
                 "px_cum": r.get("px_cum"),
                 "accounts": {k: {kk: vv for kk, vv in a.items() if kk != "lots"}
                              for k, a in r["accounts"].items()}}
        entry["key"] = BD.ledger_key(entry)
        if tuple(entry["key"]) in intents:
            print(f"  [{tk}] sổ broker đã có {entry['key']} ⇒ không lặp (idempotent)")
            continue
        if v == BD.CONFIRMABLE:
            entry["record"] = BD.build_record(r, now_ict)
        new.append(entry)
    new_recs = [e["record"] for e in new if mode == "live" and e["verdict"] == BD.CONFIRMABLE]
    rc = 0
    if new_recs:
        try:   # validate TRƯỚC mọi ghi — hỏng ⇒ 0 ghi registry, 0 intent cho mục CONFIRMABLE
            for i, rec in enumerate(actions_raw + new_recs):
                CA.validate(rec, i)
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
                 "results": [{k: e.get(k) for k in ("ticker", "credit_day", "ex_date", "verdict",
                                                     "qty_multiplier", "cash_leg", "why")}
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
