#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck cho `corp_action_auto_confirm.py` — 0 side-effect thật (subprocess.run bị stub,
không ghi bus/Discord thật; mọi file I/O trỏ vào tmpdir riêng, không đụng
`data/corp_actions.json`/`data/corp_action_daily/`/`data/execution_logs/` production).

Theo skill verify-before-done: chạy dưới TZ lạ (env -u TZ) để bắt lỗi neo múi giờ tường minh (§16).

Viết mới cho arch-review vòng 9 (job Taylor_20260924_105217) — file này trước đó KHÔNG có
selfcheck nào. Phủ 4 kịch bản bắt buộc:
  (a) record MỚI vượt QTY_MULT_MAX -> không ghi + rc phù hợp + bus question đúng nội dung.
  (b) record CŨ (đã tồn tại trước lượt này) hỏng -> thông điệp/bus question trỏ ĐÚNG record cũ,
      không đổ oan cho candidate mới (B-3).
  (c) thứ tự post_bus() vs write() -- trên đường reject KHÔNG được có "✅ AUTO-CONFIRMED" đứng
      một mình không rút lại (B-4).
  (d) đường lành (mọi record hợp lệ) -> ghi đúng, post_bus đúng, không rút lại gì.

Mẫu sandbox tmpdir + stub subprocess giống `discretionary_margin_gate_selfcheck.py`.
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corp_action_auto_confirm as cac  # noqa: E402

# Bẫy cùng lớp với discretionary_margin_gate_selfcheck.py: module vừa import PHẢI nằm CÙNG thư
# mục với chính file selfcheck này, không phải bản canonical mike/bin nếu đang chạy từ worktree.
_HERE = os.path.dirname(os.path.abspath(__file__))
assert os.path.dirname(os.path.abspath(cac.__file__)) == _HERE, (
    f"corp_action_auto_confirm nạp từ {cac.__file__}, KHÔNG phải {_HERE} — sys.path đang shadow "
    f"bản worktree bằng bản canonical")

PASS = []
FAIL = []


def check(name, cond, detail=""):
    if cond:
        PASS.append(name)
    else:
        FAIL.append((name, detail))
        print(f"❌ FAIL: {name} — {detail}")


# ─────────────────────────────────────────────────────────────────────────── stub subprocess ──

class _RunCalls:
    calls = []

    @staticmethod
    def reset():
        _RunCalls.calls = []

    @staticmethod
    def fake_run(cmd, **kwargs):
        _RunCalls.calls.append(list(cmd))

        class _R:
            returncode = 0
            stdout = b""
            stderr = b""
        return _R()


def _finding_calls(ticker=None):
    """subprocess call ghi bus finding 'corp-action-auto-confirm-<ticker>' (post_bus).

    cmd = [APPEND_EVENT, "Mike", "finding", topic, payload] — index 2 = kind, index 3 = topic."""
    out = []
    for c in _RunCalls.calls:
        if len(c) >= 4 and c[2] == "finding" and str(c[3]).startswith("corp-action-auto-confirm-"):
            if ticker is None or c[3] == f"corp-action-auto-confirm-{ticker}":
                out.append(c)
    return out


def _question_calls():
    return [c for c in _RunCalls.calls
            if len(c) >= 4 and c[2] == "question"
            and c[3] == "corp-action-auto-confirm-validate-reject"]


def _notify_calls():
    return [c for c in _RunCalls.calls if cac.NOTIFY_SH in c]


# ───────────────────────────────────────────────────────────────────────────── fixture setup ──

DATE = "2026-09-24"


def _reset_dirs(tmpdir):
    cac.CA_DAILY_DIR = os.path.join(tmpdir, "corp_action_daily")
    cac.EXEC_DIR = os.path.join(tmpdir, "execution_logs")
    cac.CORP_ACTIONS_FILE = os.path.join(tmpdir, "corp_actions.json")
    os.makedirs(cac.CA_DAILY_DIR, exist_ok=True)
    os.makedirs(cac.EXEC_DIR, exist_ok=True)
    if os.path.exists(cac.CORP_ACTIONS_FILE):   # mỗi test-block bắt đầu từ registry SẠCH
        os.remove(cac.CORP_ACTIONS_FILE)
    daily = os.path.join(cac.CA_DAILY_DIR, f"corp_action_daily_{DATE}.json")
    if os.path.exists(daily):
        os.remove(daily)
    raw = os.path.join(cac.EXEC_DIR, f"dnse_raw_{DATE}.jsonl")
    if os.path.exists(raw):
        os.remove(raw)
    _RunCalls.reset()


def _write_daily_events(events):
    path = os.path.join(cac.CA_DAILY_DIR, f"corp_action_daily_{DATE}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"upcoming_events_held": events}, f, ensure_ascii=False)


def _mk_event(ticker, ratio, event_code="ISS", days_ahead=1, ex_date=DATE):
    return {"ticker": ticker, "event_code": event_code, "date": ex_date,
            "exercise_ratio": ratio, "price_adjusting": True, "days_ahead": days_ahead,
            "title": f"tỉ lệ {ratio*100:.0f}%", "record_date": ex_date}


def _write_dnse_raw(account_no, account_label, positions_by_ticker):
    """positions_by_ticker: {ticker: (qty_before, qty_after, cost_before, cost_after)}.
    Ghi 2 snapshot (đầu ngày, cuối ngày) — first_rec/last_rec đọc bởi _get_ticker_snapshots."""
    path = os.path.join(cac.EXEC_DIR, f"dnse_raw_{DATE}.jsonl")
    lines = []
    for ticker, (qb, qa, cb, ca) in positions_by_ticker.items():
        lines.append(json.dumps({
            "account_no": account_no, "account_label": account_label, "kind": "positions",
            "ts": f"{DATE}T08:00:00", "payload": {"positions": [
                {"symbol": ticker, "accountNo": account_no, "openQuantity": qb,
                 "costPrice": cb, "modifiedDate": f"{DATE}T00:30:00Z"}]},
        }, ensure_ascii=False))
        lines.append(json.dumps({
            "account_no": account_no, "account_label": account_label, "kind": "positions",
            "ts": f"{DATE}T19:00:00", "payload": {"positions": [
                {"symbol": ticker, "accountNo": account_no, "openQuantity": qa,
                 "costPrice": ca, "modifiedDate": f"{DATE}T12:00:00Z"}]},
        }, ensure_ascii=False))
    with open(path, "a", encoding="utf-8") as f:
        for ln in lines:
            f.write(ln + "\n")


def _seed_registry(records):
    with open(cac.CORP_ACTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump({"actions": records}, f, ensure_ascii=False)


def _load_registry():
    if not os.path.exists(cac.CORP_ACTIONS_FILE):
        return []
    with open(cac.CORP_ACTIONS_FILE, encoding="utf-8") as f:
        return json.load(f).get("actions") or []


_OLD_BROKEN_VHM = {
    "ticker": "VHM", "event_type": "STOCK_DIVIDEND", "qty_multiplier": 99.0,   # > QTY_MULT_MAX
    "ex_date": "2026-08-06", "broker_effective_ts": "2026-08-05T12:00:00",
    "_status": "CONFIRMED — record cũ đã hỏng từ trước (seed test)",
}


def main():
    tmpdir = tempfile.mkdtemp(prefix="cac_selfcheck_")
    orig_run = None
    import subprocess as _sp
    orig_run = _sp.run
    _sp.run = _RunCalls.fake_run
    try:
        # ── (a) record MỚI vượt QTY_MULT_MAX ────────────────────────────────────────────────
        _reset_dirs(tmpdir)
        _write_daily_events([_mk_event("ZZZ", ratio=15.0)])       # mult=16.0 > 10.0
        _write_dnse_raw("ACC1", "SpaceX", {"ZZZ": (1000, 16000, 160000.0, 10000.0)})
        rc = cac.run(DATE, dry_run=False)
        check("(a) rc=1 khi record mới vượt QTY_MULT_MAX", rc == 1, f"rc={rc}")
        check("(a) KHÔNG ghi vào registry (file rỗng/không đổi)", _load_registry() == [],
              _load_registry())
        qcalls = _question_calls()
        check("(a) có đúng 1 bus question corp-action-auto-confirm-validate-reject",
              len(qcalls) == 1, str(qcalls))
        if qcalls:
            payload = json.loads(qcalls[0][4])
            check("(a) bus question candidates=['ZZZ'] (candidate mới, đúng thủ phạm)",
                  payload.get("candidates") == ["ZZZ"], payload)
            check("(a) bus question bad_record_is_preexisting=False (record MỚI, không phải cũ)",
                  payload.get("bad_record_is_preexisting") is False, payload)
            check("(a) bus question bad_record_index=0 (record duy nhất, index 0)",
                  payload.get("bad_record_index") == 0, payload)
        check("(a) KHÔNG có bus finding AUTO-CONFIRMED nào (đường reject không post)",
              len(_finding_calls()) == 0, str(_RunCalls.calls))
        check("(a) KHÔNG có notify Discord nào (đường reject không post)",
              len(_notify_calls()) == 0, str(_RunCalls.calls))

        # ── (b) record CŨ đã hỏng từ trước, candidate mới HỢP LỆ ───────────────────────────
        _reset_dirs(tmpdir)
        _seed_registry([dict(_OLD_BROKEN_VHM)])   # index 0 = record CŨ hỏng, đã có TRƯỚC lượt này
        _write_daily_events([_mk_event("AAA", ratio=0.2)])         # mult=1.2, hợp lệ
        _write_dnse_raw("ACC1", "SpaceX", {"AAA": (1000, 1200, 12000.0, 10000.0)})
        rc = cac.run(DATE, dry_run=False)
        check("(b) rc=1 khi registry có record CŨ hỏng", rc == 1, f"rc={rc}")
        check("(b) KHÔNG ghi thêm (registry vẫn chỉ còn record CŨ hỏng, file gốc không đổi)",
              _load_registry() == [_OLD_BROKEN_VHM], _load_registry())
        qcalls = _question_calls()
        check("(b) có đúng 1 bus question", len(qcalls) == 1, str(qcalls))
        if qcalls:
            payload = json.loads(qcalls[0][4])
            check("(b) bad_record_index=0 (VHM cũ, KHÔNG phải AAA mới index 1)",
                  payload.get("bad_record_index") == 0, payload)
            check("(b) bad_record_is_preexisting=True (đúng thủ phạm là record CŨ)",
                  payload.get("bad_record_is_preexisting") is True, payload)
            check("(b) candidates=[] — KHÔNG đổ oan cho candidate MỚI (AAA)",
                  payload.get("candidates") == [], payload)
            note = payload.get("note", "")
            check("(b) note nhắc rõ record TỪ TRƯỚC và các consumer khác cũng bị chặn",
                  "TỪ TRƯỚC" in note and "park_holdings" in note, payload)
        check("(b) KHÔNG có bus finding AUTO-CONFIRMED nào cho AAA (đường reject không post)",
              len(_finding_calls("AAA")) == 0, str(_RunCalls.calls))

        # ── (c) thứ tự post_bus vs write trên đường reject (vừa chạy ở (b)) — không được có
        #        "✅ AUTO-CONFIRMED" đứng một mình mà không rút lại: kiểm KHÔNG lời gọi
        #        subprocess nào (Discord notify HAY bus finding) mang chuỗi thông báo thành công.
        auto_confirmed_notify = [c for c in _notify_calls()
                                  if any("AUTO-CONFIRMED" in str(x) for x in c)]
        check("(c) KHÔNG có Discord notify 'AUTO-CONFIRMED' nào trên đường reject vừa chạy ở (b)",
              len(auto_confirmed_notify) == 0, str(_RunCalls.calls))
        check("(c) KHÔNG có bus finding AUTO-CONFIRMED nào trên đường reject vừa chạy ở (b)",
              len(_finding_calls()) == 0, str(_RunCalls.calls))

        # ── (d) đường lành: mọi record hợp lệ -> ghi đúng, post_bus đúng ────────────────────
        _reset_dirs(tmpdir)
        _write_daily_events([_mk_event("BBB", ratio=0.2)])         # mult=1.2, hợp lệ
        _write_dnse_raw("ACC1", "SpaceX", {"BBB": (1000, 1200, 12000.0, 10000.0)})
        rc = cac.run(DATE, dry_run=False)
        check("(d) rc=0 khi mọi record hợp lệ", rc == 0, f"rc={rc}")
        reg = _load_registry()
        check("(d) registry có đúng 1 record BBB, qty_multiplier=1.2",
              len(reg) == 1 and reg[0]["ticker"] == "BBB"
              and abs(reg[0]["qty_multiplier"] - 1.2) < 1e-9, reg)
        fcalls = _finding_calls("BBB")
        check("(d) có đúng 1 bus finding AUTO-CONFIRMED cho BBB (post-write, đường lành)",
              len(fcalls) == 1, str(_RunCalls.calls))
        check("(d) validate() thật sự chạy được trên record do run() tự sinh (không có lỗi "
              "field nào bị validate() từ chối ở đường lành)", rc == 0 and len(reg) == 1)
    finally:
        _sp.run = orig_run

    print(f"\n{'='*70}\nPASS={len(PASS)} FAIL={len(FAIL)}")
    if FAIL:
        for name, detail in FAIL:
            print(f"  - {name}: {detail}")
        return 1
    print("Tat ca selfcheck PASS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
