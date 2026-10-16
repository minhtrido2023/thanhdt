import sys, os, shutil, subprocess, json, re
sys.path.insert(0, "/tmp/ar3/mut")
from mutants import M
PRISTINE = "/tmp/ar3/WC/mike/bin"
CHECKS = [("ledger", ["nav_unit_ledger_selfcheck.py"]), ("flowterm", ["nav_flow_term_selfcheck.py"]),
          ("jump", ["nav_jump_flow_gate_selfcheck.py"]), ("e2e", ["nav_corpaction_gate_e2e_selfcheck.py"]),
          ("npr", ["nav_period_returns.py", "--selfcheck"])]
def run_one(m):
    mid, fname, old, new, note = m
    box = f"/tmp/ar3/mut/box_{mid}"
    shutil.rmtree(box, ignore_errors=True)
    os.makedirs(f"{box}/WC/mike")
    shutil.copytree(PRISTINE, f"{box}/WC/mike/bin", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree("/tmp/ar3/WC/mike/templates", f"{box}/WC/mike/templates")
    shutil.copytree("/tmp/ar3/WC/data", f"{box}/WC/data"); shutil.copytree("/tmp/ar3/WC/secrets", f"{box}/WC/secrets")
    os.symlink("/home/trido/thanhdt/WorkingClaude/trading_bot", f"{box}/WC/trading_bot"); open(f"{box}/WC/wc_env.sh", "w").close()
    p = f"{box}/WC/mike/bin/{fname}"
    src = open(p, encoding="utf-8").read()
    n = src.count(old)
    if n != 1:
        return {"id": mid, "applied": False, "count": n, "note": note}
    open(p, "w", encoding="utf-8").write(src.replace(old, new))
    env = dict(os.environ, MIKE_BOT_TEST_MODE="1", PYTHONDONTWRITEBYTECODE="1"); env.pop("TZ", None); env.pop("WC_ROOT", None)
    res = {"id": mid, "applied": True, "file": fname, "note": note, "checks": {}}
    for name, cmd in CHECKS:
        try:
            r = subprocess.run([sys.executable] + cmd, cwd=f"{box}/WC/mike/bin", env=env, capture_output=True, text=True, timeout=240)
            out = (r.stdout + "\n" + r.stderr)
            tail = [l for l in out.strip().splitlines() if l.strip()][-1:] or [""]
            fails = [l for l in out.splitlines() if ("ASSERT-FAIL" in l or "✗" in l or "FAIL" in l or "Traceback" in l or "Error" in l)]
            res["checks"][name] = {"rc": r.returncode, "tail": tail[0][:400], "traceback": "Traceback" in out, "fails": [f[:300] for f in fails[:4]]}
        except subprocess.TimeoutExpired:
            res["checks"][name] = {"rc": "timeout", "tail": "", "traceback": False, "fails": []}
    shutil.rmtree(box, ignore_errors=True)
    return res
if __name__ == "__main__":
    from concurrent.futures import ThreadPoolExecutor
    ids = set(sys.argv[1:])
    todo = [m for m in M if not ids or m[0] in ids]
    with ThreadPoolExecutor(8) as ex:
        results = list(ex.map(run_one, todo))
    json.dump(results, open("/tmp/ar3/mut/results.json" if not ids else "/tmp/ar3/mut/results_part.json", "w"), ensure_ascii=False, indent=1)
    for r in results:
        if not r["applied"]:
            print(f"{r['id']:4s} NOT-APPLIED (count={r['count']}) {r['note']}"); continue
        killed = [k for k, v in r["checks"].items() if v["rc"] != 0]
        print(f"{r['id']:4s} {'KILLED by ' + ','.join(killed) if killed else 'SURVIVED':28s} {r['note']}")
