#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""End-to-end selfcheck cho corp_action_gate_v2 — chạy THẬT `daily_nav_snapshot.main()` ở chế độ
`--from-raw` trên fixture SANDBOX, không chạm file thật, không gọi BQ/broker.

Chạy:  python3 mike/bin/nav_corpaction_gate_e2e_selfcheck.py
       cd /tmp && env -u TZ python3 <repo>/mike/bin/nav_corpaction_gate_e2e_selfcheck.py

Vì sao cần E2E chứ không chỉ unit test (arch-review vòng 2, mục [1] + [3]): killer objection của
vòng 1 KHÔNG nằm trong bất kỳ hàm nào — nó nằm ở THỨ TỰ trong main(). `return 5` chạy TRƯỚC
`if args.from_raw:`, nên nhánh `early_credit` (đường DUY NHẤT quy ngược KL theo qty_multiplier
CONFIRMED) vĩnh viễn không tới được. Mọi hàm đều "đúng" khi test riêng.

Ca gốc có thật: VIB bonus-issue 9,5%, ex-date 2026-09-10, DNSE credit sớm 1 phiên (SpaceX
500→547, ZaloPay 200→219). Đường tự lành đã chạy thật ngày đó: gate → corp_action_auto_confirm.py
19:25 ghi CONFIRMED mult=1.095 → `--from-raw` quy ngược KL → NAV 09-09 tái dựng được.
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import daily_nav_snapshot as D  # noqa: E402
import corp_action_daily as CAD  # noqa: E402
import verify_account_snapshot as V  # noqa: E402

PASS, FAIL = [], []
ACCT, ACCT_NO, DATE, PREV = "SpaceX", "0002023347", "2026-09-09", "2026-09-08"
EX_DATE, MULT, PRICE = "2026-09-10", 1.095, 21_000.0


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  ✓ " if cond else "  ✗ ") + name + (f"   [{detail}]" if detail and not cond else ""))


def build_fixture(tmp, qty_now, qty_prev=500.0, fills=(), event=True, confirmed=True,
                  mkt=None):
    """dnse_raw (2 ngày) + journal + corp_actions.json + corp_action_daily snapshot."""
    def pos(ts, qty):
        return {"kind": "positions", "ts": ts, "account_no": ACCT_NO, "payload": {"positions": [
            {"symbol": "VIB", "openQuantity": qty,
             "marketPrice": PRICE / MULT if mkt is None else mkt}]}}
    with open(os.path.join(tmp, f"dnse_raw_{PREV}.jsonl"), "w") as f:
        f.write(json.dumps(pos(f"{PREV}T19:00:00", qty_prev)) + "\n")
    with open(os.path.join(tmp, f"dnse_raw_{DATE}.jsonl"), "w") as f:
        f.write(json.dumps(pos(f"{DATE}T19:00:00", qty_now)) + "\n")
        f.write(json.dumps({"kind": "balances", "ts": f"{DATE}T19:05:00", "account_no": ACCT_NO,
                            "payload": {"stock": {"totalCash": 5_000_000.0, "totalDebt": 0.0}}}) + "\n")
    hdr = ("ts,event,parent_id,ticker,side,child_oid,qty,price,filled_total,book,play_type,note\n")
    with open(os.path.join(tmp, f"exec_{ACCT}_{DATE}_journal.csv"), "w") as f:
        f.write(hdr)
        for i, (side, q) in enumerate(fills):
            f.write(f"{DATE}T09:20:0{i},FILL,P{i},VIB,{side},{9000+i},{q},{PRICE},0,BAL,X,\n")
    acts = {"actions": [{"id": "VIB-TEST", "ticker": "VIB", "ex_date": EX_DATE,
                         "qty_multiplier": MULT,
                         "_status": ("CONFIRMED — corp_action_auto_confirm.py test"
                                     if confirmed else "PROPOSED — chưa ai ký")}]}
    with open(os.path.join(tmp, "corp_actions.json"), "w") as f:
        json.dump(acts, f)
    snap = {"asof": DATE, "status": "OK", "usable": True, "feed_status": "FRESH",
            "upcoming_events_held": ([{"ticker": "VIB", "date": EX_DATE, "event_code": "ISS",
                                       "price_adjusting": True, "exercise_ratio": "0.095"}]
                                     if event else [])}
    with open(os.path.join(tmp, f"corp_action_daily_{DATE}.json"), "w") as f:
        json.dump(snap, f)


def run(tmp):
    """Chạy main() --from-raw trong sandbox; trả (rc, stderr, snapshot_json_hoặc_None)."""
    import io
    import contextlib
    old = (D.EXEC_DIR, D.CORP_ACTIONS_FILE, D.HISTORY_FILE_TMPL, CAD.snapshot_path,
           D.bq_raw_prices, D.cum_dividend_double_count, sys.argv,
           os.environ.get("NAV_SANITY_MAX_PCT"), V.EXEC_DIR)
    D.EXEC_DIR = V.EXEC_DIR = tmp
    D.CORP_ACTIONS_FILE = os.path.join(tmp, "corp_actions.json")
    D.HISTORY_FILE_TMPL = os.path.join(tmp, "nav_history_{account}.csv")
    CAD.snapshot_path = lambda d: os.path.join(tmp, f"corp_action_daily_{d}.json")
    D.bq_raw_prices = lambda tickers, date: ({t: PRICE for t in tickers},
                                             {t: PRICE for t in tickers}, None)
    D.cum_dividend_double_count = lambda *a, **k: {
        "amount": 0.0, "delta": 0.0, "expected_bq": None, "tickers": [], "bq_max_date": None,
        "note": "", "warnings": []}
    os.environ["NAV_SANITY_MAX_PCT"] = "1000000"
    sys.argv = ["daily_nav_snapshot.py", "--account", ACCT, "--account-no", ACCT_NO,
                "--date", DATE, "--from-raw", "--starting-capital", "10000000"]
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            rc = D.main()
    finally:
        (D.EXEC_DIR, D.CORP_ACTIONS_FILE, D.HISTORY_FILE_TMPL, CAD.snapshot_path,
         D.bq_raw_prices, D.cum_dividend_double_count, sys.argv, _env, V.EXEC_DIR) = old
        if _env is None:
            os.environ.pop("NAV_SANITY_MAX_PCT", None)
        else:
            os.environ["NAV_SANITY_MAX_PCT"] = _env
    snap_p = os.path.join(tmp, f"nav_snapshot_{ACCT}_{DATE}.json")
    snap = json.load(open(snap_p, encoding="utf-8")) if os.path.exists(snap_p) else None
    return rc, err.getvalue(), snap


print("1. [1] Đường PHỤC HỒI --from-raw cho corp-action ĐÃ CONFIRMED (killer objection vòng 1)")
with tempfile.TemporaryDirectory() as tmp:
    build_fixture(tmp, qty_now=547.0, confirmed=True)
    rc, err, snap = run(tmp)
    check("(1a) VIB 500→547, corp_actions.json CONFIRMED mult=1.095 ⇒ rc=0 (KHÔNG chặn)",
          rc == 0, (rc, err[-400:]))
    check("(1b) KL được quy NGƯỢC về trước sự kiện (547/1,095 ≈ 499,5)",
          snap is not None and abs(snap["corp_action_qty_adj"].get("VIB", 0) - MULT) < 1e-9
          and abs(snap["mtm_stock"] - 547.0 / MULT * PRICE) < 1.0,
          (snap or {}).get("mtm_stock"))
    check("(1c) có dòng nav_history được ghi",
          os.path.exists(os.path.join(tmp, f"nav_history_{ACCT}.csv")))
    check("(1d) gate ghi lại việc đã phục hồi (audit được)",
          bool((snap or {}).get("corp_action_gate_v2", {}).get("corp_action_recovered")), snap)
    check("(1e) KHÔNG sinh file nav_gate_block_* khi không chặn",
          not os.path.exists(os.path.join(tmp, f"nav_gate_block_{ACCT}_{DATE}.json")))

print("2. Mô hình TIN CẬY không đổi — CHƯA CONFIRMED thì vẫn CHẶN (bỏ điều kiện ⇒ case này chết)")
with tempfile.TemporaryDirectory() as tmp:
    build_fixture(tmp, qty_now=547.0, confirmed=False)
    rc, err, snap = run(tmp)
    check("(2a) corp_actions.json PROPOSED ⇒ rc=5", rc == 5, (rc, err[-400:]))
    check("(2b) thông điệp nói ĐÚNG bằng chứng (phần dư khớp tỉ lệ), không đoán",
          "KHỚP tỉ lệ 0.095" in err and "CREDIT SỚM" in err, err[-500:])
    blk = os.path.join(tmp, f"nav_gate_block_{ACCT}_{DATE}.json")
    check("(2c) [3] bằng chứng chặn ghi ra tên RIÊNG nav_gate_block_*, KHÔNG đè nav_snapshot_*",
          os.path.exists(blk) and snap is None, os.listdir(tmp))
    check("(2d) artifact chặn có đủ số liệu đối soát",
          json.load(open(blk))["corp_action_gate_v2"]["share_event_blocks"][0]["detail"]["residual"] == 47.0)

print("3. [3] §8 — chạy lại tay sau ngày ĐÃ có NAV không được ĐÈ MẤT artifact audit")
with tempfile.TemporaryDirectory() as tmp:
    build_fixture(tmp, qty_now=547.0, confirmed=False)
    keep = {"account": ACCT, "date": DATE, "nav": 987_654_321.0, "mtm_stock": 1.0}
    with open(os.path.join(tmp, f"nav_snapshot_{ACCT}_{DATE}.json"), "w") as f:
        json.dump(keep, f)
    rc, err, snap = run(tmp)
    check("(3a) rc=5 nhưng nav_snapshot_* CŨ còn nguyên (nav != null)",
          rc == 5 and snap == keep, snap)

print("4. [2] §29 — KL đổi do LỆNH KHỚP THẬT không được báo 'credit sớm' (rc=5 giả)")
with tempfile.TemporaryDirectory() as tmp:
    # Không có corp-action nào ⇒ marketPrice khớp giá BQ; cú đổi KL hoàn toàn do lệnh mua.
    build_fixture(tmp, qty_now=600.0, fills=[("buy", 100)], confirmed=False, mkt=PRICE)
    rc, err, snap = run(tmp)
    check("(4a) mua 100 đúng phiên cum, KL 500→600 ⇒ rc=0, KHÔNG chặn", rc == 0, (rc, err[-400:]))
with tempfile.TemporaryDirectory() as tmp:
    # Vừa mua 100 VỪA bị credit sớm 47 ⇒ phần dư vẫn lộ ra, phải chặn.
    build_fixture(tmp, qty_now=647.0, fills=[("buy", 100)], confirmed=False)
    rc, err, snap = run(tmp)
    check("(4b) mua 100 + credit 47 ⇒ vẫn rc=5, phần dư +47", rc == 5 and "+47" in err, err[-400:])

print("5. [2] gap D — KL đổi thật nhưng LỊCH thiếu sự kiện: trước đây KHÔNG ai chặn")
with tempfile.TemporaryDirectory() as tmp:
    build_fixture(tmp, qty_now=547.0, event=False, confirmed=False)
    rc, err, snap = run(tmp)
    check("(5a) lịch rỗng + KL +47 không lệnh khớp ⇒ rc=5", rc == 5, (rc, err[-400:]))
    check("(5b) thông điệp nói THẲNG 'CHƯA GIẢI THÍCH ĐƯỢC', KHÔNG khẳng định credit sớm",
          "CHƯA GIẢI THÍCH ĐƯỢC" in err and "KHÔNG có sự kiện nào" in err, err[-500:])

print("6. [5] §14 — mất snapshot lịch: gate phải NÓI, và trục KHỐI LƯỢNG vẫn sống")
with tempfile.TemporaryDirectory() as tmp:
    build_fixture(tmp, qty_now=547.0, confirmed=False)
    os.remove(os.path.join(tmp, f"corp_action_daily_{DATE}.json"))
    rc, err, snap = run(tmp)
    check("(6a) thiếu corp_action_daily ⇒ vẫn chặn rc=5 (trục KL không phụ thuộc lịch)", rc == 5,
          (rc, err[-400:]))
    check("(6b) in ⚠️ nói rõ gate đang thiếu lịch", "KHÔNG xác nhận được lịch corp-action" in err,
          err[-500:])
with tempfile.TemporaryDirectory() as tmp:
    # KL không đổi + giá khớp ⇒ đường THÀNH CÔNG (rc=0), để kiểm bản ghi gate ở nhánh đó.
    build_fixture(tmp, qty_now=500.0, confirmed=False, mkt=PRICE)
    os.remove(os.path.join(tmp, f"corp_action_daily_{DATE}.json"))
    rc, err, snap = run(tmp)
    check("(6c) ngày bình thường vẫn ghi corp_action_gate_v2.active=false vào nav_snapshot",
          rc == 0 and snap["corp_action_gate_v2"]["active"] is False, (rc, (snap or {}).get("corp_action_gate_v2")))

print(f"\n{len(PASS)} PASS, {len(FAIL)} FAIL")
sys.exit(1 if FAIL else 0)
