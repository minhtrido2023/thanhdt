#!/usr/bin/env python3
"""Selfcheck X3 — `corp_actions.load_all` bỏ qua CÓ CẢNH BÁO record loại chưa hỗ trợ / chưa
CONFIRMED hỏng, vẫn raise với record CONFIRMED hỏng (audit lag_rights_audit_20261022 F5).

Sổ corp_actions + bootstrap/journal/dnse_raw giả trong mkdtemp; KHÔNG đụng data/corp_actions.json.
    python3 bin/corp_actions_skip_unsupported_selfcheck.py        # 3 TZ + mutant
"""
import contextlib
import csv
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")
os.environ["AUTO_EXIT_TEST_MODE"] = "1"
HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = []


def ck(name, cond, detail=""):
    RESULTS.append(bool(cond))
    print(f"  {'PASS' if cond else 'FAIL'} — {name}" + ("" if cond else f"  [{detail}]"))


GOOD = {"id": "SCL-BONUS", "ticker": "SCL", "event_type": "STOCK_DIVIDEND", "qty_multiplier": 1.09,
        "ex_date": "2025-11-06", "broker_effective_ts": "2025-11-06T19:00:00", "_status": "CONFIRMED by user"}
RIGHTS = {"id": "SCL-R", "ticker": "SCL", "event_type": "RIGHTS", "qty_multiplier": 19 / 14,
          "ex_date": "2026-11-09", "broker_effective_ts": "2026-12-03T19:00:00", "_status": "PROPOSED"}


def write_reg(td, actions):
    p = os.path.join(td, "corp_actions.json")
    json.dump({"actions": actions}, open(p, "w"))
    return p


def load(CA, path):
    sk, err = [], io.StringIO()
    with contextlib.redirect_stderr(err):
        out = CA.load_all(path, skipped=sk)
    return out, sk, err.getvalue()


def raises(fn):
    try:
        fn()
    except Exception as e:  # noqa: BLE001
        return type(e).__name__
    return None


def run_unit(CA, td):
    out, sk, err = load(CA, write_reg(td, [GOOD, RIGHTS]))
    ck("U1 PROPOSED RIGHTS ⇒ bỏ qua, record tốt vẫn nạp", [a["id"] for a in out] == ["SCL-BONUS"], out)
    ck("U1b skipped nêu id + lý do 'chưa hỗ trợ'", len(sk) == 1 and sk[0]["id"] == "SCL-R"
       and "chưa hỗ trợ" in sk[0]["reason"], sk)
    ck("U1c cảnh báo stderr nêu tên record", "SCL-R" in err and "BỎ QUA" in err, err)
    p2 = write_reg(td, [GOOD, dict(RIGHTS, _status="CONFIRMED by user")])
    ck("U2 RIGHTS ĐÃ CONFIRMED (loại chưa hỗ trợ) ⇒ VẪN raise CorpActionError (arch-review 22/10: record CONFIRMED "
       "hỏng không được bỏ qua)", raises(lambda: CA.load_all(p2)) == "CorpActionError")
    p3 = write_reg(td, [GOOD, dict(GOOD, id="TYPO-C", event_type="Stock dividend")])
    ck("U2b CONFIRMED gõ sai loại ('Stock dividend') ⇒ raise, không im lặng", raises(lambda: CA.load_all(p3)) == "CorpActionError")
    out, sk, _ = load(CA, write_reg(td, [GOOD, dict(GOOD, id="BAD-P", qty_multiplier="1,30", _status="PROPOSED")]))
    ck("U3 PROPOSED loại hỗ trợ nhưng hỏng ⇒ bỏ qua + cảnh báo", len(out) == 1 and sk and sk[0]["id"] == "BAD-P"
       and "chưa CONFIRMED" in sk[0]["reason"], sk)
    p = write_reg(td, [GOOD, dict(GOOD, id="BAD-C", qty_multiplier="1,30")])
    ck("U4 CONFIRMED loại hỗ trợ mà hỏng ⇒ VẪN raise CorpActionError (như cũ)",
       raises(lambda: CA.load_all(p)) == "CorpActionError")
    ck("U4b load_corp_actions cũng raise (đường live park_holdings)",
       raises(lambda: CA.load_corp_actions(p)) == "CorpActionError")
    p = write_reg(td, [dict(GOOD, event_type=None)])
    ck("U5 CONFIRMED thiếu event_type ⇒ raise", raises(lambda: CA.load_all(p)) == "CorpActionError")
    out, sk, _ = load(CA, write_reg(td, [dict(GOOD, event_type=None, _status="PROPOSED")]))
    ck("U5b PROPOSED thiếu event_type ⇒ bỏ qua", out == [] and len(sk) == 1, sk)
    out, sk, err = load(CA, write_reg(td, [GOOD, dict(GOOD, id="P2", _status="PROPOSED", ex_date="2026-01-05")]))
    ck("U6 regression: record hợp lệ PROPOSED vẫn nạp đủ, không cảnh báo", len(out) == 2 and sk == [] and err == "")
    p = write_reg(td, [GOOD, RIGHTS, dict(GOOD, id="P2", _status="PROPOSED", ex_date="2026-01-05")])
    with contextlib.redirect_stderr(io.StringIO()):
        live = CA.load_corp_actions(p)
    ck("U7 load_corp_actions chỉ trả CONFIRMED hợp lệ", [a["id"] for a in live] == ["SCL-BONUS"], live)
    ck("U8 không truyền skipped vẫn chạy", raises(lambda: CA.load_all(write_reg(td, [RIGHTS]))) is None)
    ck("U9 sổ vắng mặt = []", CA.load_all(os.path.join(td, "khong-co.json")) == [])


ACCOUNT, ACCOUNT_NO, DAY0 = "X3Acct", "8888888888", "2026-10-01"


def run_e2e(td):
    """park_holdings / book_lot_snapshot THẬT với sổ có RIGHTS PROPOSED (ca F5 của audit)."""
    import corp_actions as CA
    import park_holdings as ph
    import portfolio_status as ps
    ex, pl = os.path.join(td, "execution_logs"), os.path.join(td, "trade_plans")
    os.makedirs(ex)
    os.makedirs(pl)
    json.dump({"_status": "APPROVED by selfcheck", "account_label": ACCOUNT, "account_no": ACCOUNT_NO,
               "day0_date": DAY0, "broker_source": {"file": "x", "ts": f"{DAY0}T00:00:00"},
               "reconcile_ok": True, "positions": [{"ticker": "FPT", "qty": 6000, "book": "custom30V_parking",
                                                    "entry_date": DAY0, "cost_price_vnd": 100000}]},
              open(os.path.join(pl, f"bootstrap_book_snapshot_{ACCOUNT}_{DAY0.replace('-', '')}.json"), "w"))
    with open(os.path.join(ex, f"exec_{ACCOUNT}_2026-10-26_journal.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["ts", "event", "parent_id", "child_oid", "ticker", "side", "qty",
                                          "price", "book", "play_type"])
        w.writeheader()
        w.writerow({"ts": "2026-10-26T09:30:00", "event": "FILL", "parent_id": "P", "child_oid": "C",
                    "ticker": "SCL", "side": "buy", "qty": 14000, "price": 30000, "book": "LAG",
                    "play_type": "LAG_LO"})
    pos = [{"accountNo": ACCOUNT_NO, "symbol": "FPT", "openQuantity": 6000, "tradeQuantity": 6000,
            "marketPrice": 100000, "costPrice": 100000},
           {"accountNo": ACCOUNT_NO, "symbol": "SCL", "openQuantity": 14000, "tradeQuantity": 14000,
            "marketPrice": 25400, "costPrice": 30000}]
    with open(os.path.join(ex, "dnse_raw_2026-11-20.jsonl"), "w") as f:
        f.write(json.dumps({"ts": "2026-11-20T20:30:00", "kind": "positions", "account_no": "7777777777",
                            "payload": {"positions": [dict(pos[1], accountNo="7777777777", openQuantity=999)]}}) + "\n")
        f.write(json.dumps({"ts": "2026-11-20T20:30:01", "kind": "positions", "account_no": ACCOUNT_NO,
                            "payload": {"positions": pos}}) + "\n")
    reg = write_reg(td, [RIGHTS])
    orig = (ph.load_corp_actions, ph.account_profile)
    ph.load_corp_actions = lambda *a, **k: CA.load_corp_actions(reg)
    ph.account_profile = lambda label: {"account_id": ACCOUNT_NO, "excluded_tickers": []}
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            lag = ps.book_lot_snapshot(ACCOUNT, "LAG", asof="2026-11-20", plan_dir=pl, exec_dir=ex)
            bal = ps.book_lot_snapshot(ACCOUNT, "BAL", asof="2026-11-20", plan_dir=pl, exec_dir=ex)
            err = raises(lambda: ph.park_holdings(ACCOUNT, asof="2026-11-20", plan_dir=pl, exec_dir=ex,
                                                  price_fn=lambda t, d: {k: 1.0 for k in t}))
    finally:
        ph.load_corp_actions, ph.account_profile = orig
    ck("E1 sổ có RIGHTS PROPOSED ⇒ park_holdings KHÔNG raise (audit F5: CorpActionError)", err is None, err)
    ck("E2 book_lot_snapshot LAG ok=True, SCL 14.000", lag[1] and lag[0].get("SCL", {}).get("qty") == 14000, lag)
    ck("E3 book_lot_snapshot BAL ok=True (không còn chặn cả book)", bal[1], bal)


def run_inner():
    sys.path.insert(0, HERE)
    import corp_actions as CA
    mut = os.environ.get("X3_MUT")
    if mut:
        old, new = json.loads(mut)
        src = open(os.path.join(HERE, "corp_actions.py"), encoding="utf-8").read()
        assert src.count(old) == 1, f"mutant gốc không khớp đúng 1 lần: {old!r}"
        exec(compile(src.replace(old, new), CA.__file__, "exec"), CA.__dict__)
    td = tempfile.mkdtemp(prefix="x3_selfcheck_")
    try:
        run_unit(CA, td)
        run_e2e(td)
    finally:
        shutil.rmtree(td, ignore_errors=True)
    n, ok = len(RESULTS), sum(RESULTS)
    print(f"{ok}/{n} PASS")
    return 0 if ok == n else 1


MUTANTS = [
    ("if status.upper().startswith(CONFIRMED_PREFIX):", "if False:"),
    ("if status.upper().startswith(CONFIRMED_PREFIX):", "if True:"),
    ('print(f"⚠️ corp_actions: BỎ QUA', 'None and print(f"⚠️ corp_actions: BỎ QUA'),
    ("                skipped.append(info)", "                pass"),
    ("unsupported = bool(etype) and etype not in QTY_EVENT_TYPES", "unsupported = False"),
]


def run_mutants():
    bad = 0
    for i, m in enumerate(MUTANTS, 1):
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--inner"],
                           env=dict(os.environ, X3_MUT=json.dumps(m)), capture_output=True, text=True, timeout=600)
        if "mutant gốc không khớp" in (r.stderr + r.stdout):
            print(f"  ❌ mutant {i}: chuỗi gốc không khớp đúng 1 lần — sửa MUTANTS")
            bad += 1
            continue
        killed = r.returncode != 0
        print(f"  {'KILLED' if killed else 'SURVIVED'} — mutant {i}: {m[0].strip()[:60]!r} → {m[1].strip()[:30]!r}")
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
