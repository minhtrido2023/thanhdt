#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck cho nhánh `except corp_actions.CorpActionError` trong `daily_nav_snapshot.main()`
(đường LIVE, KHÔNG `--from-raw`) — B3, arch-review vòng 6/7 Việc 2.

Trước bản này KHÔNG selfcheck nào chạm tới nhánh này (grep "\\.main(" trên mọi *selfcheck*.py chỉ
ra `nav_corpaction_gate_e2e_selfcheck.py`, nhưng file đó CHỈ chạy `--from-raw` — nhánh quy đổi
NGƯỢC vị thế qua `confirmed_qty_multiplier_after()` ở main() bị SKIP hẳn khi `--from-raw` vì điều
kiện `if not is_today and not args.from_raw:` (dòng ~885). Registry hỏng ở đường LIVE (ngày lịch
sử, không phải hôm nay, không phải backfill) chưa từng được test end-to-end.

Chạy THẬT `main()` với record `qty_multiplier` sai định dạng trong `corp_actions.json` — mock
DUY NHẤT 2 điểm I/O không xác định được từ sandbox (`broker_positions`: cần kết nối DNSE thật;
`subprocess.run`: verify_account_snapshot.py cross-check, advisory only, không ảnh hưởng rc). Mọi
thứ còn lại (load_config/load_accounts, trading_dates_with_fills, corp_actions.load_all) chạy
CODE THẬT trên fixture sandbox — đây là lý do B3 chọn e2e thay vì unit test thẳng
`confirmed_qty_multiplier_after` (đã có ở round 6, chỉ cô lập được hàm, không cô lập được main()
có THỰC SỰ đi tới nhánh except hay không, giống bài học "killer objection" của
`nav_corpaction_gate_e2e_selfcheck.py`).
"""
import io
import json
import os
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import daily_nav_snapshot as D  # noqa: E402
import verify_account_snapshot as V  # noqa: E402

PASS, FAIL = [], []
ACCOUNT = "SelfchkCorpErr"
ACCOUNT_NO = "9999999999"
DATE = "2026-08-10"           # ngày LỊCH SỬ (không phải hôm nay) — bắt buộc để vào nhánh corp_action_adj
PREV_JOURNAL_DATE = "2026-08-05"


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  ✓ " if cond else "  ✗ ") + name + (f"   [{detail}]" if detail and not cond else ""))


def _fake_completed(rc=0):
    return types.SimpleNamespace(returncode=rc, stdout="", stderr="")


def run_main(tmp, registry_actions):
    """Chạy D.main() thật trong sandbox; trả (rc, stderr, nav_history_tồn_tại)."""
    corp_actions_path = os.path.join(tmp, "corp_actions.json")
    with open(corp_actions_path, "w", encoding="utf-8") as f:
        json.dump({"actions": registry_actions}, f)

    hist_path = os.path.join(tmp, f"nav_history_{ACCOUNT}.csv")
    old = (D.EXEC_DIR, D.CORP_ACTIONS_FILE, D.HISTORY_FILE_TMPL, D.broker_positions,
           D.subprocess.run, V.bq_close_prices, sys.argv)
    D.EXEC_DIR = tmp
    D.CORP_ACTIONS_FILE = corp_actions_path
    D.HISTORY_FILE_TMPL = os.path.join(tmp, "nav_history_{account}.csv")
    # journal cần cho trading_dates_with_fills() thấy có ≥1 ngày giao dịch <= --date.
    with open(os.path.join(tmp, f"exec_{ACCOUNT}_{PREV_JOURNAL_DATE}_journal.csv"), "w") as f:
        f.write("ts,event,parent_id,ticker,side,child_oid,qty,price,filled_total,book,play_type,note\n")
    D.broker_positions = lambda account_label, account_no: {
        "VPB": {"qty": 500.0, "marketPrice": 20_000.0}}
    D.subprocess.run = lambda *a, **k: _fake_completed(0)
    # Đường KHÔNG bị chặn bởi CorpActionError (test 3) đi tiếp tới bq_close_prices() — ngoài
    # phạm vi B3 (đó là gọi BQ thật qua subprocess riêng của verify_account_snapshot, không
    # phải D.subprocess). Mock trả rỗng để main() dừng ở guard "thiếu giá" (rc=2) ngay sau,
    # KHÔNG chạm mạng — vẫn đủ để phân biệt "chặn vì CorpActionError" khỏi "chặn vì lý do khác".
    V.bq_close_prices = lambda tickers, date: ({}, None)
    sys.argv = ["daily_nav_snapshot.py", "--account", ACCOUNT, "--account-no", ACCOUNT_NO,
                "--date", DATE, "--starting-capital", "10000000"]
    err = io.StringIO()
    out = io.StringIO()
    import contextlib
    try:
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
            rc = D.main()
    finally:
        (D.EXEC_DIR, D.CORP_ACTIONS_FILE, D.HISTORY_FILE_TMPL, D.broker_positions,
         D.subprocess.run, V.bq_close_prices, sys.argv) = old
    return rc, err.getvalue(), os.path.exists(hist_path)


print("1. Registry hỏng (qty_multiplier kiểu số Việt) trên đường LIVE (không --from-raw)")
with tempfile.TemporaryDirectory() as tmp:
    bad = {"ticker": "VPB", "event_type": "BONUS_ISSUE", "qty_multiplier": "1,30",
           "ex_date": "2026-09-15", "broker_effective_ts": "2026-09-14T19:00:00+07:00",
           "_status": "CONFIRMED — test"}
    rc, err, hist_exists = run_main(tmp, [bad])
    check("(1a) rc=2 — main() PHẢI chặn khi corp_actions.json có record hỏng", rc == 2,
          (rc, err[-500:]))
    check("(1b) thông điệp lỗi nêu rõ corp_actions.json + ticker liên quan",
          "corp_actions.json" in err and "VPB" in err, err[-500:])
    check("(1c) KHÔNG ghi nav_history — record hỏng không được lọt qua thành NAV",
          not hist_exists, hist_exists)

print("2. Registry hỏng (ex_date thiếu) — cùng nhánh except, dạng lỗi khác")
with tempfile.TemporaryDirectory() as tmp:
    bad = {"ticker": "VPB", "event_type": "BONUS_ISSUE", "qty_multiplier": 1.30,
           "ex_date": None, "broker_effective_ts": "2026-09-14T19:00:00+07:00",
           "_status": "CONFIRMED — test"}
    rc, err, hist_exists = run_main(tmp, [bad])
    check("(2a) rc=2", rc == 2, (rc, err[-500:]))
    check("(2b) KHÔNG ghi nav_history", not hist_exists, hist_exists)

print("3. Đối chứng KHÔNG-ĐƯỢC-CHẾT: registry LÀNH hoàn toàn không kích nhánh except "
      "(rc khác 2 vì lý do KHÁC — chứng minh guard không chặn oan đường lành)")
with tempfile.TemporaryDirectory() as tmp:
    good = {"ticker": "VPB", "event_type": "BONUS_ISSUE", "qty_multiplier": 1.30,
            "ex_date": "2026-12-01", "broker_effective_ts": "2026-11-30T19:00:00+07:00",
            "_status": "CONFIRMED — test"}
    rc, err, hist_exists = run_main(tmp, [good])
    check("(3a) registry lành -> KHÔNG bị chặn bởi CorpActionError "
          "(rc=2 chấp nhận được ở bước SAU đó — vd thiếu giá BQ — nhưng KHÔNG được có "
          "'corp_actions.json có record hỏng' trong stderr)",
          "corp_actions.json có record hỏng" not in err, err[-500:])

print(f"\n{'='*70}\nPASS={len(PASS)} FAIL={len(FAIL)}")
if FAIL:
    for name in FAIL:
        print(f"  - {name}")
    sys.exit(1)
print("Tat ca selfcheck PASS.")
sys.exit(0)
