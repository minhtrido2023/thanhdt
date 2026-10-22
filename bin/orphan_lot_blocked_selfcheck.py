#!/usr/bin/env python3
"""Selfcheck X2 — mã MỒ CÔI (broker qty>0, sổ lô = 0 ở mọi book) phải hiện vào `blocked` của
`book_lot_snapshot` và của auto-exit (+ alert), không im lặng (audit lag_rights_audit_20261022 F2).

park_holdings / book_lot_snapshot / process_account THẬT trên sandbox mkdtemp (bootstrap + journal +
dnse_raw giả, account giả + 1 dòng nhiễu account khác — §12). Không bus/Discord, không data/ thật.
    python3 bin/orphan_lot_blocked_selfcheck.py        # 3 TZ + mutant
"""
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile

os.environ["AUTO_EXIT_TEST_MODE"] = "1"
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")
HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = []


def ck(name, cond, detail=""):
    RESULTS.append(bool(cond))
    print(f"  {'PASS' if cond else 'FAIL'} — {name}" + ("" if cond else f"  [{detail}]"))


DAY0, SIG, PLAN = "2026-10-01", "2026-11-20", "2026-11-23"
JCOLS = ["ts", "event", "parent_id", "child_oid", "ticker", "side", "qty", "price", "book", "play_type"]


def build(td, S, scl_broker, scl_sold):
    """SCL LAG mua 14.000 ngày 10-26 (+ bán 14.000 ngày 11-18 nếu scl_sold); HPG BAL từ bootstrap
    (entry 2026-08-01 ⇒ quá T+45); FPT PARK. Broker SIG: SCL = scl_broker (open, trade=open)."""
    ex, pl = os.path.join(td, "execution_logs"), os.path.join(td, "trade_plans")
    os.makedirs(ex)
    os.makedirs(pl)
    S.write_bootstrap(pl, S.ACCOUNT, S.ACCOUNT_NO, DAY0, [
        {"ticker": "FPT", "qty": 6000, "book": "custom30V_parking", "entry_date": DAY0, "cost_price_vnd": 100000},
        {"ticker": "HPG", "qty": 1000, "book": "BAL", "entry_date": "2026-08-01", "cost_price_vnd": 25000}])
    fills = [("2026-10-26", "buy")] + ([("2026-11-18", "sell")] if scl_sold else [])
    for d, side in fills:
        with open(os.path.join(ex, f"exec_{S.ACCOUNT}_{d}_journal.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=JCOLS)
            w.writeheader()
            w.writerow({"ts": f"{d}T09:30:00", "event": "FILL", "parent_id": f"P-{d}", "child_oid": f"C-{d}",
                        "ticker": "SCL", "side": side, "qty": 14000, "price": 30000, "book": "LAG",
                        "play_type": "LAG_LO"})
    rows = [{"accountNo": S.ACCOUNT_NO, "symbol": "FPT", "openQuantity": 6000, "tradeQuantity": 6000,
             "marketPrice": 100000, "costPrice": 100000},
            {"accountNo": S.ACCOUNT_NO, "symbol": "HPG", "openQuantity": 1000, "tradeQuantity": 1000,
             "marketPrice": 25000, "costPrice": 25000}]
    if scl_broker:
        rows.append({"accountNo": S.ACCOUNT_NO, "symbol": "SCL", "openQuantity": scl_broker,
                     "tradeQuantity": scl_broker, "marketPrice": 21000, "costPrice": 25395})
    with open(os.path.join(ex, f"dnse_raw_{SIG}.jsonl"), "w") as f:
        f.write(json.dumps({"ts": f"{SIG}T20:30:00", "kind": "positions", "account_no": "7777777777",
                            "payload": {"positions": [dict(rows[0], accountNo="7777777777", symbol="SCL",
                                                           openQuantity=999)]}}) + "\n")
        f.write(json.dumps({"ts": f"{SIG}T20:30:01", "kind": "positions", "account_no": S.ACCOUNT_NO,
                            "payload": {"positions": rows}}) + "\n")
    return ex, pl


def scenario(S, aei, ps, scl_broker, scl_sold):
    td = tempfile.mkdtemp(prefix="x2_selfcheck_")
    ledger = os.path.join(td, "capit.json")
    S.write_capit_ledger(ledger)
    ex, pl = build(td, S, scl_broker, scl_sold)
    orig = S.patch_all_e2e(ex, pl, ledger, S.ACCOUNT_NO)
    sp, calls = S.install_subprocess_recorder()
    try:
        lag = ps.book_lot_snapshot(S.ACCOUNT, "LAG", asof=SIG)
        bal = ps.book_lot_snapshot(S.ACCOUNT, "BAL", asof=SIG)
        S.write_plan(pl, S.ACCOUNT, PLAN)
        rc = aei.process_account(S.ACCOUNT, PLAN, SIG, dry_run=False)
        plan = S.load_plan_raw(pl, S.ACCOUNT, PLAN)
    finally:
        S.restore_subprocess_recorder(sp)
        S.restore_all_e2e(orig)
        shutil.rmtree(td, ignore_errors=True)
    blocked = [b for n in plan.get("auto_exit_inject_notes", []) for b in n.get("blocked", [])]
    sells = {(o["ticker"], o["book"]): o["qty"] for o in plan["orders"] if o["side"] == "sell"}
    return lag, bal, rc, blocked, sells, calls


def run_inner():
    sys.path.insert(0, HERE)
    import auto_exit_inject_selfcheck as S   # helper sandbox + stub cổng quyền mua (mã giả)
    import auto_exit_inject as aei
    import portfolio_status as ps
    mut = os.environ.get("X2_MUT")
    if mut:
        fname, old, new = json.loads(mut)
        mod = ps if fname == "portfolio_status.py" else aei
        src = open(os.path.join(HERE, fname), encoding="utf-8").read()
        assert src.count(old) == 1, f"mutant gốc không khớp đúng 1 lần: {old!r}"
        exec(compile(src.replace(old, new), mod.__file__, "exec"), mod.__dict__)
        aei.book_lot_snapshot = ps.book_lot_snapshot
        aei.ORPHAN_PREFIX = ps.ORPHAN_PREFIX
        aei.rights_hold.holds_for = lambda *a, **kw: {}

    lag, bal, rc, blocked, sells, calls = scenario(S, aei, ps, scl_broker=5000, scl_sold=True)
    ck("O1 book_lot_snapshot LAG: SCL mồ côi vào blocked", lag[1] and lag[3].get("SCL", "").startswith(ps.ORPHAN_PREFIX)
       and "5000cp" in lag[3]["SCL"], lag)
    ck("O1b book_lot_snapshot BAL cũng nêu SCL mồ côi (không book nào sở hữu)",
       bal[3].get("SCL", "").startswith(ps.ORPHAN_PREFIX), bal)
    orph = [b for b in blocked if b["ticker"] == "SCL"]
    ck("O2 auto-exit: SCL mồ côi ghi ĐÚNG MỘT lần vào blocked (book '*')",
       len(orph) == 1 and orph[0]["book"] == "*" and orph[0]["reason"].startswith(ps.ORPHAN_PREFIX), blocked)
    ck("O3 auto-exit KHÔNG bán SCL; HPG BAL T+45 vẫn bán (mã khác không bị ảnh hưởng)",
       ("SCL", "LAG") not in sells and sells.get(("HPG", "BAL")) == 1000, sells)
    ck("O4 test-mode ⇒ 0 subprocess thật (alert đi qua guard §5b)", calls == [], calls)
    ck("O4b không còn dòng 'không có candidate' im lặng (rc=0, có notes)", rc == 0 and bool(blocked))

    lag, bal, rc, blocked, sells, _ = scenario(S, aei, ps, scl_broker=19000, scl_sold=False)
    ck("O5 regression: lệch một phần (sổ 14.000 / broker 19.000) ⇒ blocked LAG lý do reconcile cũ, không phải mồ côi",
       any(b["ticker"] == "SCL" and b["book"] == "LAG" and "reconcile lệch broker" in b["reason"] for b in blocked)
       and not any(b["reason"].startswith(ps.ORPHAN_PREFIX) for b in blocked), blocked)
    lag, bal, rc, blocked, sells, _ = scenario(S, aei, ps, scl_broker=0, scl_sold=True)
    ck("O6 regression: đã bán hết, broker 0 ⇒ không blocked, chỉ HPG BAL bán",
       blocked == [] and sells == {("HPG", "BAL"): 1000}, (blocked, sells))
    lag, bal, rc, blocked, sells, _ = scenario(S, aei, ps, scl_broker=14000, scl_sold=False)
    ck("O7 regression: khớp sổ, chưa tới T+25 ⇒ không blocked, SCL không bán",
       blocked == [] and ("SCL", "LAG") not in sells and lag[0].get("SCL", {}).get("qty") == 14000, (blocked, sells, lag))
    n, ok = len(RESULTS), sum(RESULTS)
    print(f"{ok}/{n} PASS")
    return 0 if ok == n else 1


MUTANTS = [
    ("portfolio_status.py", 'if m["ledger_qty"] == 0 and m["broker_qty"] > 0:', "if False:"),
    ("portfolio_status.py", 'if m["ledger_qty"] == 0 and m["broker_qty"] > 0:', 'if m["broker_qty"] > 0:'),
    ("auto_exit_inject.py", '            book = "*"   # mã mồ côi', '            pass  # mã mồ côi'),
]


def run_mutants():
    bad = 0
    for i, m in enumerate(MUTANTS, 1):
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--inner"],
                           env=dict(os.environ, X2_MUT=json.dumps(m)), capture_output=True, text=True, timeout=900)
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
