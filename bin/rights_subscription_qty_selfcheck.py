#!/usr/bin/env python3
"""Selfcheck N3 — quyền mua KHÔNG phải "sự kiện cổ phiếu" trong `classify_qty_residual`, và ngày
user NỘP TIỀN mua quyền được phân loại đúng (lệnh tay hợp lệ) chỉ khi đủ bằng chứng cơ khí;
KL tăng không giải thích được vẫn chặn rc=5 (daily_nav_snapshot) / blocked (exdate_frame → rc=6).

Fixture: dòng BQ SCL 2025 thật (14:5 @12.500, GDKHQ 2025-10-17) + số MBB 08-28 thật (costPrice
dnse_raw SpaceX: 1.565×21.405,7508 → 1.675×20.656,7164). Sandbox mkdtemp, KHÔNG BQ/broker/bus.
    python3 bin/rights_subscription_qty_selfcheck.py        # 3 TZ + mutant
"""
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

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
MBB = {"id": "MBB-R", "ticker": "MBB", "issue_method_code": "Rights", "issue_status_code": "D",
       "event_status": "executed", "exright_date": "2026-07-20", "exercise_ratio": "0.1",
       "value_per_share": "10000", "total_value": None, "issue_volumn": None}
RIGHTS_EV = {"ticker": "SCL", "date": "2025-10-17", "event_code": "ISS", "price_adjusting": True,
             "exercise_ratio": "0.35714286", "issue_method_vi": "Quyền mua CP cho Cổ đông hiện hữu"}


def det(resid=5000.0, qty_prev=14000.0, net_fill=0.0):
    return {"qty_prev": qty_prev, "qty_now": qty_prev + resid + net_fill, "residual": resid,
            "net_fill": net_fill, "prev_qty_date": "2025-10-24"}


def run_unit(D):
    q = D.classify_qty_residual
    v, _ = q(RIGHTS_EV, 19000.0, 14000.0, 0.0, "2025-10-16")
    ck("A1 quyền mua (issue_method_vi) KHÔNG giải thích cú tăng KL đúng tỉ lệ ⇒ qty_unexplained", v == "qty_unexplained", v)
    ev2 = dict(RIGHTS_EV, issue_method_vi=None, issue_method_code="Rights")
    ck("A2 quyền mua (issue_method_code=Rights) cũng vậy", q(ev2, 19000.0, 14000.0, 0.0, "x")[0] == "qty_unexplained")
    sd = dict(RIGHTS_EV, exercise_ratio="0.09", issue_method_vi="Trả Cổ tức bằng Cổ phiếu")
    ck("A3 regression: cổ tức CP 9% vẫn share_event_credit", q(sd, 15260.0, 14000.0, 0.0, "x")[0] == "share_event_credit")
    bo = dict(RIGHTS_EV, exercise_ratio="0.2604104", issue_method_vi="Cổ phiếu thưởng")
    ck("A4 regression: CP thưởng VPB vẫn share_event_credit", q(bo, 1386.0, 1100.0, 0.0, "x")[0] == "share_event_credit")
    reg = {"ticker": "VIB", "date": "2026-09-10", "event_code": "ISS", "price_adjusting": True, "exercise_ratio": 0.095}
    ck("A5 regression: sự kiện từ sổ corp_actions (không có issue_method) vẫn credit", q(reg, 547.0, 500.0, 0.0, "x")[0] == "share_event_credit")
    div = {"ticker": "DRI", "date": "2026-09-22", "event_code": "DIV", "price_adjusting": True, "exercise_ratio": "0.1"}
    ck("A6 regression: cổ tức tiền vẫn không giải thích KL", q(div, 2750.0, 2500.0, 0.0, "x")[0] == "qty_unexplained")

    c = D.classify_rights_subscription
    base_cost = 14000 * 30000.0
    ok, info = c([SCL25], "2025-10-27", det(), base_cost, base_cost + 5000 * 12500.0)
    ck("B1 SCL nộp 5.000 @12.500, bước giá vốn 62,5tr ⇒ nhận là nộp tiền quyền mua",
       ok and info["issue_price"] == 12500.0 and info["subscribed_qty"] == 5000, info)
    ok, info = c([MBB], "2026-08-28", det(110.0, 1565.0), 33500000.002, 34599999.97)
    ck("B2 số MBB 08-28 THẬT (costPrice dnse_raw) ⇒ nhận", ok, info)
    ok, info = c([SCL25], "2025-10-27", det(), base_cost, base_cost + 5000 * 20000.0)
    ck("B3 bước giá vốn theo GIÁ THỊ TRƯỜNG (mua thường) ⇒ KHÔNG nhận, nêu lý do",
       not ok and "bước giá vốn" in info, info)
    ok, _ = c([SCL25], "2025-10-27", det(), base_cost, base_cost + 5000 * 12500.0 + 400000)
    ck("B3b lệch 400.000đ (> 0,5% = 312.500đ) ⇒ KHÔNG nhận", not ok)
    ok, _ = c([SCL25], "2025-10-27", det(), base_cost, base_cost + 5000 * 12500.0 + 300)
    ck("B3c lệch 300đ (< sàn) ⇒ nhận", ok)
    ok, info = c([SCL25], "2025-10-27", det(5002.0), base_cost, base_cost + 5002 * 12500.0)
    ck("B4 phần dư > số quyền tối đa (+1) ⇒ KHÔNG nhận", not ok and "quyền tối đa" in info, info)
    ok, _ = c([SCL25], "2025-10-27", det(2000.0), base_cost, base_cost + 2000 * 12500.0)
    ck("B4b mua MỘT PHẦN quyền (2.000) ⇒ nhận", ok)
    ok, info = c([SCL25], "2025-10-27", det(net_fill=100.0), base_cost, base_cost + 5000 * 12500.0)
    ck("B5 có lệnh khớp cùng cửa sổ ⇒ KHÔNG nhận (không tách được giá vốn)", not ok and "lệnh khớp" in info, info)
    ok, _ = c([SCL25], "2025-10-16", det(), base_cost, base_cost + 5000 * 12500.0)
    ck("B6 trước GDKHQ ⇒ KHÔNG nhận", not ok)
    ok, _ = c([SCL25], "2026-03-01", det(), base_cost, base_cost + 5000 * 12500.0)
    ck("B7 quá cửa sổ 120 ngày sau GDKHQ ⇒ KHÔNG nhận", not ok)
    ok, info = c([dict(SCL25, total_value="0.0")], "2025-10-27", det(), base_cost, base_cost + 5000 * 12500.0)
    ck("B8 chưa có giá phát hành ⇒ KHÔNG nhận", not ok and "giá phát hành" in info, info)
    ok, _ = c([dict(SCL25, issue_status_code="N")], "2025-10-27", det(), base_cost, base_cost + 5000 * 12500.0)
    ck("B9 sự kiện huỷ ⇒ KHÔNG nhận", not ok)
    ok, _ = c([dict(SCL25, issue_method_code="Bonus")], "2025-10-27", det(), base_cost, base_cost + 5000 * 12500.0)
    ck("B10 không phải Rights ⇒ KHÔNG nhận", not ok)
    ok, info = c([SCL25], "2025-10-27", det(), None, base_cost + 5000 * 12500.0)
    ck("B11 thiếu costPrice ⇒ KHÔNG nhận, nói rõ", not ok and "costPrice" in info, info)
    ok, _ = c([SCL25], "2025-10-27", det(-100.0), base_cost, base_cost)
    ck("B12 phần dư âm ⇒ KHÔNG nhận", not ok)
    ok, info = c([], "2025-10-27", det(), base_cost, base_cost + 5000 * 12500.0)
    ck("B13 không có dòng quyền mua ⇒ KHÔNG nhận", not ok and "không có quyền mua" in info, info)
    ok, _ = c([dict(SCL25, exright_date=None)], "2025-10-27", det(), base_cost, base_cost + 5000 * 12500.0)
    ck("B14 dòng chưa có GDKHQ ⇒ KHÔNG nhận", not ok)

    def boom(_t):
        raise RuntimeError("bq failed: denied 42")
    ok, info = D.rights_subscription_check("1", "SCL", "2025-10-27", "2025-10-24", det(), fetch=boom)
    ck("B15 lỗi BQ ⇒ KHÔNG nhận + lỗi thật", not ok and "denied 42" in info, info)


ACCT, ACCT_NO, DATE, PREV = "SpaceX", "0002023347", "2025-10-27", "2025-10-24"


def build(tmp, cost_now_px, fills=()):
    def pos(ts, qty, cost, rows_extra=()):
        return {"kind": "positions", "ts": ts, "account_no": ACCT_NO, "payload": {"positions": [
            {"symbol": "SCL", "openQuantity": qty, "marketPrice": 20000.0, "costPrice": cost},
            *rows_extra]}}
    noise = {"kind": "positions", "ts": f"{DATE}T19:00:01", "account_no": "0001743768",
             "payload": {"positions": [{"symbol": "SCL", "openQuantity": 777, "marketPrice": 1, "costPrice": 1}]}}
    with open(os.path.join(tmp, f"dnse_raw_{PREV}.jsonl"), "w") as f:
        f.write(json.dumps(pos(f"{PREV}T19:00:00", 14000.0, 30000.0)) + "\n")
    with open(os.path.join(tmp, f"dnse_raw_{DATE}.jsonl"), "w") as f:
        # 2 gói vay cùng mã (14.000 + 5.000) — raw_cost_value phải CỘNG; + dòng nhiễu account khác (§12)
        f.write(json.dumps({"kind": "positions", "ts": f"{DATE}T19:00:00", "account_no": ACCT_NO,
                            "payload": {"positions": [
                                {"symbol": "SCL", "openQuantity": 14000.0, "marketPrice": 20000.0, "costPrice": 30000.0},
                                {"symbol": "SCL", "openQuantity": 5000.0, "marketPrice": 20000.0, "costPrice": cost_now_px}]}}) + "\n")
        f.write(json.dumps(noise) + "\n")
        f.write(json.dumps({"kind": "balances", "ts": f"{DATE}T19:05:00", "account_no": ACCT_NO,
                            "payload": {"stock": {"totalCash": 837_500_000.0, "totalDebt": 0.0}}}) + "\n")
    hdr = "ts,event,parent_id,ticker,side,child_oid,qty,price,filled_total,book,play_type,note\n"
    for d in (DATE,):
        with open(os.path.join(tmp, f"exec_{ACCT}_{d}_journal.csv"), "w") as f:
            f.write(hdr)
            for i, (side, q) in enumerate(fills):
                f.write(f"{d}T09:20:0{i},FILL,P{i},SCL,{side},{9000+i},{q},20000,0,LAG,X,\n")
    json.dump({"actions": []}, open(os.path.join(tmp, "corp_actions.json"), "w"))
    json.dump({"asof": DATE, "status": "OK", "usable": True, "feed_status": "FRESH",
               "upcoming_events_held": []}, open(os.path.join(tmp, f"corp_action_daily_{DATE}.json"), "w"))


def run_main(D, CAD, V, tmp):
    old = (D.EXEC_DIR, D.CORP_ACTIONS_FILE, D.HISTORY_FILE_TMPL, CAD.snapshot_path,
           D.bq_raw_prices, D.cum_dividend_double_count, sys.argv, os.environ.get("NAV_SANITY_MAX_PCT"), V.EXEC_DIR)
    D.EXEC_DIR = V.EXEC_DIR = tmp
    D.CORP_ACTIONS_FILE = os.path.join(tmp, "corp_actions.json")
    D.HISTORY_FILE_TMPL = os.path.join(tmp, "nav_history_{account}.csv")
    CAD.snapshot_path = lambda d: os.path.join(tmp, f"corp_action_daily_{d}.json")
    D.bq_raw_prices = lambda tickers, date: ({t: 20000.0 for t in tickers}, {t: 20000.0 for t in tickers}, None)
    D.cum_dividend_double_count = lambda *a, **k: {"amount": 0.0, "delta": 0.0, "expected_bq": None, "tickers": [],
                                                   "bq_max_date": None, "note": "", "warnings": []}
    os.environ["NAV_SANITY_MAX_PCT"] = "1000000"
    sys.argv = ["daily_nav_snapshot.py", "--account", ACCT, "--account-no", ACCT_NO, "--date", DATE,
                "--from-raw", "--starting-capital", "1000000000"]
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            rc = D.main()
    finally:
        (D.EXEC_DIR, D.CORP_ACTIONS_FILE, D.HISTORY_FILE_TMPL, CAD.snapshot_path, D.bq_raw_prices,
         D.cum_dividend_double_count, sys.argv, envv, V.EXEC_DIR) = old
        if envv is None:
            os.environ.pop("NAV_SANITY_MAX_PCT", None)
        else:
            os.environ["NAV_SANITY_MAX_PCT"] = envv
    return rc, err.getvalue()


def run_e2e(D):
    import corp_action_daily as CAD
    import verify_account_snapshot as V
    import rights_issue_alert as RIA
    import exdate_frame as EF
    orig_fetch = RIA.fetch_rights
    try:
        for label, cost_px, fetch, fills, want_rc in (
                ("E1 nộp tiền quyền mua đúng giá phát hành ⇒ NAV KHÔNG chặn (rc=0)", 12500.0, lambda t: [SCL25], (), 0),
                ("E2 KL tăng giá vốn thị trường (không phải quyền) ⇒ VẪN chặn rc=5", 20000.0, lambda t: [SCL25], (), 5),
                ("E3 lỗi BQ ⇒ VẪN chặn rc=5", 12500.0, None, (), 5),
                ("E4 không có quyền mua nào ⇒ VẪN chặn rc=5", 12500.0, lambda t: [], (), 5)):
            tmp = tempfile.mkdtemp(prefix="n3_e2e_")
            try:
                build(tmp, cost_px, fills)
                if fetch is None:
                    def fetch(_t):
                        raise RuntimeError("bq failed: e2e-denied")
                RIA.fetch_rights = fetch
                rc, err = run_main(D, CAD, V, tmp)
                ck(label, rc == want_rc, f"rc={rc} {err[-600:]}")
                if want_rc == 0:
                    ck(label + " — stderr nêu NỘP TIỀN MUA QUYỀN + sự kiện", "NỘP TIỀN MUA QUYỀN" in err and SCL25["id"] in err, err[-400:])
                else:
                    blk = os.path.join(tmp, f"nav_gate_block_{ACCT}_{DATE}.json")
                    ck(label + " — thông điệp nêu vì sao KHÔNG nhận quyền mua (§29)",
                       "không nhận là nộp tiền quyền mua" in err and os.path.exists(blk), err[-400:])
                # exdate_frame (đường compute_active_nav) cùng fixture
                old = (D.EXEC_DIR, CAD.snapshot_path, V.EXEC_DIR)
                D.EXEC_DIR = V.EXEC_DIR = tmp
                CAD.snapshot_path = lambda d: os.path.join(tmp, f"corp_action_daily_{d}.json")
                try:
                    with contextlib.redirect_stderr(io.StringIO()):
                        cr, bl = EF.classify_positions(ACCT, ACCT_NO, DATE, {"SCL": {"total": 19000.0}})
                finally:
                    D.EXEC_DIR, CAD.snapshot_path, V.EXEC_DIR = old
                if want_rc == 0:
                    ck(label + " — exdate_frame: không blocked, không credited", "SCL" not in bl and "SCL" not in cr, (cr, bl))
                else:
                    ck(label + " — exdate_frame: SCL blocked (⇒ compute_active_nav rc=6) kèm lý do quyền mua",
                       "không nhận là nộp tiền quyền mua" in bl.get("SCL", ""), bl)
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
    finally:
        RIA.fetch_rights = orig_fetch


def run_inner():
    sys.path.insert(0, HERE)
    import daily_nav_snapshot as D
    import exdate_frame as EF
    mut = os.environ.get("N3_MUT")
    if mut:
        fname, old, new = json.loads(mut)
        mod = D if fname == "daily_nav_snapshot.py" else EF
        src = open(os.path.join(HERE, fname), encoding="utf-8").read()
        assert src.count(old) == 1, f"mutant gốc không khớp đúng 1 lần: {old!r}"
        exec(compile(src.replace(old, new), mod.__file__, "exec"), mod.__dict__)
    run_unit(D)
    run_e2e(D)
    n, ok = len(RESULTS), sum(RESULTS)
    print(f"{ok}/{n} PASS")
    return 0 if ok == n else 1


MUTANTS = [
    ("daily_nav_snapshot.py", "                          and not _is_rights_event(ev))", ")"),
    ("daily_nav_snapshot.py", "        if abs(step - want) > tol:", "        if False:"),
    ("daily_nav_snapshot.py", "        if resid > cap:", "        if False:"),
    ("daily_nav_snapshot.py", "if abs(detail.get(\"net_fill\") or 0.0) > QTY_RESIDUAL_EPS:", "if False:"),
    ("daily_nav_snapshot.py", "if ratio <= 0 or ex > asof_d or (asof_d - ex).days > RIGHTS_PAY_WINDOW_DAYS:", "if ratio <= 0:"),
    ("daily_nav_snapshot.py", "        if px <= 0:\n            why.append", "        if False:\n            why.append"),
    ("daily_nav_snapshot.py", "                    qverdict = \"ok\"", "                    pass"),
    ("daily_nav_snapshot.py", "                why += f\" [không nhận là nộp tiền quyền mua: {d['rights_check']}]\"", "                pass"),
    ("daily_nav_snapshot.py", "        if p.get(\"symbol\") != ticker or float(p.get(\"openQuantity\") or 0) <= 0:\n            continue\n        try:\n            total +=",
     "        if p.get(\"symbol\") != ticker or float(p.get(\"openQuantity\") or 0) <= 0:\n            continue\n        try:\n            total =",),
    ("daily_nav_snapshot.py", "            if rec.get(\"kind\") == \"positions\" and rec.get(\"account_no\") == account_no:",
     "            if rec.get(\"kind\") == \"positions\":"),
    ("exdate_frame.py", "            if rs_ok:\n                print(", "            if False:\n                print("),
    ("exdate_frame.py", "            detail[\"rights_check\"] = rs_info", "            pass"),
]


def run_mutants():
    bad = 0
    for i, m in enumerate(MUTANTS, 1):
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--inner"],
                           env=dict(os.environ, N3_MUT=json.dumps(m)), capture_output=True, text=True, timeout=600)
        if "mutant gốc không khớp" in (r.stderr + r.stdout):
            print(f"  ❌ mutant {i}: chuỗi gốc không khớp đúng 1 lần — sửa MUTANTS")
            bad += 1
            continue
        killed = r.returncode != 0
        print(f"  {'KILLED' if killed else 'SURVIVED'} — mutant {i}: {m[0]} {m[1].strip()[:60]!r}")
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
