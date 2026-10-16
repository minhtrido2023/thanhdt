import importlib, json, os, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
PRISTINE = "/tmp/archrev_fcf/S1/mike/bin"
SEED = "/tmp/archrev_fcf/SEED"
TB = "/tmp/archrev_fcf/S1/trading_bot"
BOXES = "/tmp/archrev_fcf/boxes"
CHECKS = [("cashid", ["cash_identity_selfcheck.py"]), ("ledger", ["nav_unit_ledger_selfcheck.py"]),
          ("jump", ["nav_jump_flow_gate_selfcheck.py"]), ("e2e", ["nav_corpaction_gate_e2e_selfcheck.py"]),
          ("flowterm", ["nav_flow_term_selfcheck.py"]), ("npr", ["nav_period_returns.py", "--selfcheck"]), ("rdg", ["report_delivery_gate_selfcheck.py"])]
sys.path.insert(0, HERE)
M = importlib.import_module("mutants").M
def run_one(m):
    mid, fname, old, new, note = m
    box = f"{BOXES}/box_{mid}"
    shutil.rmtree(box, ignore_errors=True)
    os.makedirs(f"{box}/WC/mike")
    shutil.copytree(PRISTINE, f"{box}/WC/mike/bin", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(f"{SEED}/data", f"{box}/WC/data")
    shutil.copytree(TB, f"{box}/WC/trading_bot", ignore=shutil.ignore_patterns("__pycache__"))
    open(f"{box}/WC/wc_env.sh", "w").close(); open(f"{box}/WC/mike/MIKE.md", "w").close()
    p = f"{box}/WC/mike/bin/{fname}"
    src = open(p, encoding="utf-8").read()
    n = src.count(old) if mid != "BASE" else 1
    if n != 1:
        shutil.rmtree(box, ignore_errors=True)
        return {"id": mid, "applied": False, "count": n, "note": note, "file": fname}
    if mid != "BASE":
        open(p, "w", encoding="utf-8").write(src.replace(old, new))
    env = dict(os.environ, MIKE_BOT_TEST_MODE="1", PYTHONDONTWRITEBYTECODE="1")
    for k in ("TZ", "WC_ROOT", "MIKE_ROOT", "ACCOUNT_CASH_FLOWS_PATH"):
        env.pop(k, None)
    res = {"id": mid, "applied": True, "file": fname, "note": note, "checks": {}}
    for name, cmd in CHECKS:
        try:
            r = subprocess.run([sys.executable] + cmd, cwd=f"{box}/WC/mike/bin", env=env, capture_output=True, text=True, timeout=400)
            out = r.stdout + "\n" + r.stderr
            fails = [l for l in out.splitlines() if "AssertionError" in l or "FAIL" in l or "✗" in l]
            res["checks"][name] = {"rc": r.returncode, "fails": [f[:300] for f in fails[:2]], "tail": out.strip().splitlines()[-1][:300] if out.strip() else ""}
        except subprocess.TimeoutExpired:
            res["checks"][name] = {"rc": "timeout", "fails": [], "tail": ""}
    shutil.rmtree(box, ignore_errors=True)
    return res
if __name__ == "__main__":
    from concurrent.futures import ThreadPoolExecutor
    ids = set(sys.argv[1:])
    todo = [("BASE", "cash_identity.py", "", "", "không mutant")] + [m for m in M if not ids or m[0] in ids]
    with ThreadPoolExecutor(8) as ex:
        results = list(ex.map(run_one, todo))
    json.dump(results, open(os.path.join(HERE, "results.json"), "w"), ensure_ascii=False, indent=1)
    for r in results:
        if not r["applied"]:
            print(f"{r['id']:5s} NOT_APPLIED(count={r['count']}) {r['file']} | {r['note']}"); continue
        bad = {k: v for k, v in r["checks"].items() if v["rc"] != 0}
        verdict = "SURVIVED" if not bad else "KILLED by " + ",".join(bad)
        print(f"{r['id']:5s} {verdict:34s} {r['file'][:22]:22s} | {r['note']}")
