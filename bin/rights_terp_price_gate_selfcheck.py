#!/usr/bin/env python3
"""Selfcheck N2 — cổng giá tối cum (daily_nav_snapshot) chấp nhận marketPrice ≈ TERP quyền mua.

Tối cum, broker có thể hạ marketPrice về giá tham chiếu điều chỉnh (TERP) cho phiên GDKHQ, trong
khi giá đóng cửa hôm nay vẫn là giá CUM ⇒ lệch >5% ⇒ rc=4 chặn oan (audit B2.2). N2 chỉ nới khi
ĐỦ bằng chứng: Rights chưa huỷ, GDKHQ = phiên kế tiếp, biết giá phát hành, marketPrice khớp TERP.
Thiếu bit nào ⇒ VẪN rc=4 và thông điệp nói vì sao (§29). NAV mark giá CUM.

Fixture: dòng BQ SCL 2025 thật (14:5 @12.500, GDKHQ 2025-10-17), giá cum 22.200, TERP 19.647
(Close/Price đo 10-17: 0,88674 vs lý thuyết 0,88501). Sandbox mkdtemp, KHÔNG BQ/broker/bus.
    python3 bin/rights_terp_price_gate_selfcheck.py        # 3 TZ + mutant
"""
import contextlib
import datetime
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from zoneinfo import ZoneInfo

os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")
HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = []


def ck(name, cond, detail=""):
    RESULTS.append(bool(cond))
    print(f"  {'PASS' if cond else 'FAIL'} — {name}" + ("" if cond else f"  [{detail}]"))


SCL25 = {"id": "682291730e8a716db6edd5a4", "ticker": "SCL", "issue_method_code": "Rights",
         "issue_status_code": "D", "event_status": "executed", "exright_date": "2025-10-17",
         "record_date": "2025-10-20", "public_date": "2025-10-10", "exercise_ratio": "0.35714286",
         "value_per_share": None, "total_value": "1.0E11", "issue_volumn": "8000000"}
P_CUM, MP_TERP = 22200.0, 19650.0


def run_unit(D):
    c = D.classify_rights_ref_gap
    v, info = c([SCL25], "2025-10-17", P_CUM, MP_TERP)
    ck("U1 SCL marketPrice 19.650 ≈ TERP ⇒ rights_ref_confirmed", v == "rights_ref_confirmed", (v, info))
    ck("U1b TERP tính đúng ≈ 19.647", v and abs(info["terp"] - 19647.4) < 1.0, info)
    ck("U1c giá phát hành = total_value/issue_volumn = 12.500", v and info["issue_price"] == 12500.0, info)
    v, info = c([SCL25], "2025-10-17", P_CUM, 17000.0)
    ck("U2 marketPrice lệch TERP ⇒ unconfirmed + nêu TERP/marketPrice", v == "rights_ref_unconfirmed" and "17,000" in info, info)
    v, info = c([dict(SCL25, total_value=None)], "2025-10-17", P_CUM, MP_TERP)
    ck("U3 chưa có giá phát hành ⇒ KHÔNG nới (unconfirmed, nói rõ)", v == "rights_ref_unconfirmed" and "CHƯA có giá phát hành" in info, info)
    v, _ = c([dict(SCL25, issue_status_code="N")], "2025-10-17", P_CUM, MP_TERP)
    ck("U4 quyền mua đã huỷ (N) ⇒ không áp (None)", v is None, v)
    v, _ = c([dict(SCL25, event_status="not_executed")], "2025-10-17", P_CUM, MP_TERP)
    ck("U5 event_status not_executed ⇒ không áp", v is None, v)
    v, _ = c([SCL25], "2025-10-24", P_CUM, MP_TERP)
    ck("U6 GDKHQ KHÔNG phải phiên kế tiếp ⇒ không áp", v is None, v)
    v, _ = c([dict(SCL25, exright_date=None)], "2025-10-17", P_CUM, MP_TERP)
    ck("U7 chưa có ngày GDKHQ ⇒ không áp", v is None, v)
    v, info = c([dict(SCL25, exercise_ratio="0")], "2025-10-17", P_CUM, MP_TERP)
    ck("U8 tỉ lệ 0 ⇒ unconfirmed", v == "rights_ref_unconfirmed", (v, info))
    stock_div = dict(SCL25, issue_method_code="StockDividend", issue_method_vi="Trả Cổ tức bằng Cổ phiếu")
    v, _ = c([stock_div], "2025-10-17", P_CUM, MP_TERP)
    ck("U9 regression: dòng KHÔNG phải Rights ⇒ không áp", v is None, v)
    v, _ = c([], "2025-10-17", P_CUM, MP_TERP)
    ck("U10 không có dòng nào ⇒ None", v is None, v)
    v, _ = c([dict(SCL25, value_per_share="12500", total_value=None)], "2025-10-17", P_CUM, MP_TERP)
    ck("U11 value_per_share có sẵn ⇒ dùng được", v == "rights_ref_confirmed", v)

    def boom(_t):
        raise RuntimeError("bq failed: denied 42")
    v, info = D.rights_ref_check("SCL", "2025-10-17", P_CUM, MP_TERP, fetch=boom)
    ck("U12 lỗi BQ ⇒ unconfirmed + lỗi thật (fail-closed)", v == "rights_ref_unconfirmed" and "denied 42" in info, info)


ACCT, ACCT_NO = "SpaceX", "0002023347"


def build(tmp, date, prev, mp):
    def pos(ts):
        return {"kind": "positions", "ts": ts, "account_no": ACCT_NO, "payload": {"positions": [
            {"symbol": "SCL", "openQuantity": 14000.0, "marketPrice": mp, "costPrice": 30000.0}]}}
    noise = {"kind": "positions", "ts": f"{date}T19:00:01", "account_no": "0001743768",
             "payload": {"positions": [{"symbol": "SCL", "openQuantity": 777, "marketPrice": 1, "costPrice": 1}]}}
    with open(os.path.join(tmp, f"dnse_raw_{prev}.jsonl"), "w") as f:
        f.write(json.dumps(dict(pos(f"{prev}T19:00:00"), payload={"positions": [
            {"symbol": "SCL", "openQuantity": 14000.0, "marketPrice": P_CUM, "costPrice": 30000.0}]})) + "\n")
    with open(os.path.join(tmp, f"dnse_raw_{date}.jsonl"), "w") as f:
        f.write(json.dumps(pos(f"{date}T19:00:00")) + "\n")
        f.write(json.dumps(noise) + "\n")
        f.write(json.dumps({"kind": "balances", "ts": f"{date}T19:05:00", "account_no": ACCT_NO,
                            "payload": {"stock": {"totalCash": 689_200_000.0, "totalDebt": 0.0}}}) + "\n")
    hdr = "ts,event,parent_id,ticker,side,child_oid,qty,price,filled_total,book,play_type,note\n"
    with open(os.path.join(tmp, f"exec_{ACCT}_{date}_journal.csv"), "w") as f:
        f.write(hdr)
    json.dump({"actions": []}, open(os.path.join(tmp, "corp_actions.json"), "w"))
    json.dump({"asof": date, "status": "OK", "usable": True, "feed_status": "FRESH",
               "upcoming_events_held": []}, open(os.path.join(tmp, f"corp_action_daily_{date}.json"), "w"))


class _RC0:
    returncode, stdout, stderr = 0, "", ""


def run_main(D, CAD, V, tmp, date, live, mp):
    old = (D.EXEC_DIR, D.CORP_ACTIONS_FILE, D.HISTORY_FILE_TMPL, CAD.snapshot_path, D.bq_raw_prices,
           D.cum_dividend_double_count, sys.argv, os.environ.get("NAV_SANITY_MAX_PCT"), V.EXEC_DIR,
           D.broker_positions, V.dnse_close_prices, D.subprocess.run)
    D.EXEC_DIR = V.EXEC_DIR = tmp
    D.CORP_ACTIONS_FILE = os.path.join(tmp, "corp_actions.json")
    D.HISTORY_FILE_TMPL = os.path.join(tmp, "nav_history_{account}.csv")
    CAD.snapshot_path = lambda d: os.path.join(tmp, f"corp_action_daily_{d}.json")
    D.bq_raw_prices = lambda tickers, d: ({t: P_CUM for t in tickers}, {t: P_CUM for t in tickers}, None)
    D.cum_dividend_double_count = lambda *a, **k: {"amount": 0.0, "delta": 0.0, "expected_bq": None, "tickers": [],
                                                   "bq_max_date": None, "note": "", "warnings": []}
    # đường LIVE: vị thế + giá DNSE giả; verify_account_snapshot (advisory) không chạy thật
    D.broker_positions = lambda label, no: {"SCL": {"qty": 14000.0, "marketPrice": mp}}
    V.dnse_close_prices = lambda tickers: {t: P_CUM for t in tickers}
    _real_run = old[-1]
    D.subprocess.run = lambda cmd, *a, **k: (_RC0() if any("verify_account_snapshot" in str(x) for x in cmd)
                                             else _real_run(cmd, *a, **k))
    os.environ["NAV_SANITY_MAX_PCT"] = "1000000"
    sys.argv = ["daily_nav_snapshot.py", "--account", ACCT, "--account-no", ACCT_NO, "--date", date,
                "--starting-capital", "1000000000"] + ([] if live else ["--from-raw"])
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            rc = D.main()
    finally:
        (D.EXEC_DIR, D.CORP_ACTIONS_FILE, D.HISTORY_FILE_TMPL, CAD.snapshot_path, D.bq_raw_prices,
         D.cum_dividend_double_count, sys.argv, envv, V.EXEC_DIR, D.broker_positions,
         V.dnse_close_prices, D.subprocess.run) = old
        if envv is None:
            os.environ.pop("NAV_SANITY_MAX_PCT", None)
        else:
            os.environ["NAV_SANITY_MAX_PCT"] = envv
    return rc, err.getvalue()


def run_e2e(D):
    import corp_action_daily as CAD
    import verify_account_snapshot as V
    import rights_issue_alert as RIA
    from trading_bot.vn_market import next_trading_day, is_holiday
    orig_fetch = RIA.fetch_rights
    today = datetime.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date()
    live_nxt = next_trading_day(today).isoformat()
    live_prev = today - datetime.timedelta(days=1)
    while live_prev.weekday() >= 5 or is_holiday(live_prev):
        live_prev -= datetime.timedelta(days=1)
    live_prev = live_prev.isoformat()

    def rows(**kw):
        return lambda t, kw=kw: [dict(SCL25, **kw)]

    def boom(_t):
        raise RuntimeError("bq failed: e2e-denied")

    cases = [
        # label, live?, mp, fetch, want_rc, must_in_err
        ("E1 from-raw: marketPrice = TERP ⇒ rc=0", False, MP_TERP, rows(), 0, None),
        ("E2 from-raw: chưa có giá phát hành ⇒ VẪN rc=4 + lý do", False, MP_TERP, rows(total_value=None), 4, "CHƯA có giá phát hành"),
        ("E3 from-raw: lỗi BQ ⇒ VẪN rc=4 + lỗi thật", False, MP_TERP, boom, 4, "e2e-denied"),
        ("E4 from-raw: marketPrice không khớp TERP ⇒ rc=4", False, 17000.0, rows(), 4, "≠ marketPrice"),
        ("E5 from-raw regression: không có quyền mua ⇒ rc=4 như cũ, không câu quyền mua", False, MP_TERP, lambda t: [], 4, None),
        ("E6 from-raw: quyền mua đã huỷ ⇒ rc=4", False, MP_TERP, rows(issue_status_code="N"), 4, None),
        ("E7 from-raw regression: không lệch giá ⇒ rc=0 KHÔNG cần đọc BQ", False, P_CUM, boom, 0, None),
        ("L1 live: marketPrice = TERP ⇒ rc=0", True, MP_TERP, rows(exright_date=live_nxt), 0, None),
        ("L2 live: chưa có giá phát hành ⇒ rc=4 + lý do", True, MP_TERP, rows(exright_date=live_nxt, total_value=None), 4,
         "CHƯA có giá phát hành"),
        ("L3 live: lỗi BQ ⇒ rc=4 + lỗi thật", True, MP_TERP, boom, 4, "e2e-denied"),
        ("L4 live: GDKHQ không phải phiên kế tiếp ⇒ rc=4", True, MP_TERP, rows(exright_date="2099-01-02"), 4, None),
    ]
    try:
        for label, live, mp, fetch, want_rc, must in cases:
            tmp = tempfile.mkdtemp(prefix="n2_e2e_")
            date, prev = ((today.isoformat(), live_prev) if live else ("2025-10-16", "2025-10-15"))
            try:
                build(tmp, date, prev, mp)
                RIA.fetch_rights = fetch
                rc, err = run_main(D, CAD, V, tmp, date, live, mp)
                ck(label, rc == want_rc, f"rc={rc} {err[-700:]}")
                if must:
                    ck(label + f" — stderr nêu '{must}' (§29)", must in err, err[-500:])
                if want_rc == 0 and mp == MP_TERP:
                    snap = json.load(open(os.path.join(tmp, f"nav_snapshot_{ACCT}_{date}.json")))
                    rr = snap["corp_action_gate_v2"].get("rights_ref_confirmed") or {}
                    ck(label + " — artifact ghi rights_ref_confirmed SCL", "SCL" in rr, snap.get("corp_action_gate_v2"))
                    ck(label + " — NAV mark giá CUM (mtm = 14.000 × 22.200)",
                       abs(float(snap.get("mtm_stock") or 0) - 14000 * P_CUM) < 1, snap.get("mtm_stock"))
                if "regression: không có quyền mua" in label:
                    ck(label + " — không chèn câu [quyền mua]", "[quyền mua:" not in err, err[-400:])
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
    finally:
        RIA.fetch_rights = orig_fetch


def run_inner():
    sys.path.insert(0, HERE)
    sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))   # WorkingClaude/ ⇒ trading_bot
    import daily_nav_snapshot as D
    mut = os.environ.get("N2_MUT")
    if mut:
        old, new = json.loads(mut)
        src = open(D.__file__, encoding="utf-8").read()
        assert src.count(old) == 1, f"mutant gốc không khớp đúng 1 lần: {old!r}"
        exec(compile(src.replace(old, new), D.__file__, "exec"), D.__dict__)
    run_unit(D)
    run_e2e(D)
    n, ok = len(RESULTS), sum(RESULTS)
    print(f"{ok}/{n} PASS")
    return 0 if ok == n else 1


MUTANTS = [
    ("        if abs(mkt_price - terp) > tol:", "        if False:"),
    ("        if not px:\n            why.append(f\"id={r.get('id')} GDKHQ", "        if False:\n            why.append(f\"id={r.get('id')} GDKHQ"),
    ("        if str(r.get(\"exright_date\") or \"\")[:10] != ex_date:\n            continue\n",
     "        if False:\n            continue\n"),
    ("        terp = (price_ref + ratio * px) / (1 + ratio)", "        terp = price_ref / (1 + ratio)"),
    ("    if why:\n        return \"rights_ref_unconfirmed\", \"; \".join(why)\n    return None, None",
     "    return \"rights_ref_confirmed\", {\"event_id\": None, \"exright_date\": ex_date, \"exercise_ratio\": 0, "
     "\"issue_price\": 0, \"terp\": 0, \"price_ref\": price_ref, \"mkt_price\": mkt_price}"),
    ("        return (\"rights_ref_unconfirmed\",\n                f\"không đọc được",
     "        return (None,\n                f\"không đọc được"),
    ("        if not _is_rights_event(r) or r.get(\"issue_status_code\") == \"N\" \\\n                or r.get(\"event_status\") == \"not_executed\":\n            continue\n        if str(",
     "        if not _is_rights_event(r):\n            continue\n        if str("),
    ("                           + (f\" [quyền mua: {rights_ref_why[t]}]\" if t in rights_ref_why else \"\")", ""),
    ("                rv, rinfo = rights_ref_check(t, nxt_session, cp, mp)\n                if rv == \"rights_ref_confirmed\":\n                    rights_ref_confirmed[t] = rinfo\n                    print(",
     "                rv, rinfo = None, None\n                if rv == \"rights_ref_confirmed\":\n                    rights_ref_confirmed[t] = rinfo\n                    print("),
    ("               \"rights_ref_confirmed\": rights_ref_confirmed,\n", ""),
]


def run_mutants():
    bad = 0
    for i, m in enumerate(MUTANTS, 1):
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--inner"],
                           env=dict(os.environ, N2_MUT=json.dumps(m)), capture_output=True, text=True, timeout=600)
        if "mutant gốc không khớp" in (r.stderr + r.stdout):
            print(f"  ❌ mutant {i}: chuỗi gốc không khớp đúng 1 lần — sửa MUTANTS")
            bad += 1
            continue
        killed = r.returncode != 0
        print(f"  {'KILLED' if killed else 'SURVIVED'} — mutant {i}: {m[0].strip()[:70]!r}")
        bad += 0 if killed else 1
    print(f"MUTANTS: {len(MUTANTS) - bad}/{len(MUTANTS)} killed")
    return bad


def main():
    if "--inner" in sys.argv:
        return run_inner()
    rc = 0
    for label, env in (("env -u TZ", {k: v for k, v in os.environ.items() if k != "TZ"}),
                       ("TZ=Pacific/Kiritimati", dict(os.environ, TZ="Pacific/Kiritimati")),
                       ("TZ=America/New_York", dict(os.environ, TZ="America/New_York"))):
        print(f"=== {label} ===")
        rc |= subprocess.run([sys.executable, os.path.abspath(__file__), "--inner"], env=env).returncode
    print("=== mutants ===")
    if run_mutants():
        rc |= 1
    print("TỔNG:", "PASS" if rc == 0 else "FAIL")
    return rc


if __name__ == "__main__":
    sys.exit(main())
