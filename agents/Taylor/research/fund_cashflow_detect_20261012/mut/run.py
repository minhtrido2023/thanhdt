#!/usr/bin/env python3
"""Chạy mutant trong SANDBOX (bản sao bin của worktree + dữ liệu giả /tmp/ar3/WC) — không chạm data/ thật.
Dùng: run.py <bộ: ar3|step2> [id ...]"""
import importlib, json, os, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
PRISTINE = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-fundcf-1012/bin"
SEED = "/tmp/ar3/WC"
BOXES = "/tmp/fundcf_mut"
CHECKS = [("ledger", ["nav_unit_ledger_selfcheck.py"]), ("flowterm", ["nav_flow_term_selfcheck.py"]),
          ("jump", ["nav_jump_flow_gate_selfcheck.py"]), ("cashid", ["cash_identity_selfcheck.py"]),
          ("npr", ["nav_period_returns.py", "--selfcheck"]), ("e2e", ["nav_corpaction_gate_e2e_selfcheck.py"])]
which = sys.argv[1]
sys.path.insert(0, os.path.join(HERE, "..", "ar3_mut") if which == "ar3" else HERE)
M = importlib.import_module("mutants" if which == "ar3" else "mutants_step2").M

def run_one(m):
    mid, fname, old, new, note = m
    box = f"{BOXES}/box_{which}_{mid}"
    shutil.rmtree(box, ignore_errors=True)
    os.makedirs(f"{box}/WC/mike")
    shutil.copytree(PRISTINE, f"{box}/WC/mike/bin", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(f"{SEED}/mike/templates", f"{box}/WC/mike/templates")
    shutil.copytree(f"{SEED}/data", f"{box}/WC/data"); shutil.copytree(f"{SEED}/secrets", f"{box}/WC/secrets")
    os.symlink("/home/trido/thanhdt/WorkingClaude/trading_bot", f"{box}/WC/trading_bot")
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
            r = subprocess.run([sys.executable] + cmd, cwd=f"{box}/WC/mike/bin", env=env, capture_output=True, text=True, timeout=300)
            out = r.stdout + "\n" + r.stderr
            fails = [l for l in out.splitlines() if "ASSERT-FAIL" in l or "✗" in l or "Traceback" in l]
            res["checks"][name] = {"rc": r.returncode, "traceback": "Traceback" in out, "fails": [f[:260] for f in fails[:3]]}
        except subprocess.TimeoutExpired:
            res["checks"][name] = {"rc": "timeout", "traceback": False, "fails": []}
    shutil.rmtree(box, ignore_errors=True)
    return res

if __name__ == "__main__":
    from concurrent.futures import ThreadPoolExecutor
    ids = set(sys.argv[2:])
    todo = [("BASE", "cash_identity.py", "", "", "không mutant — phải xanh hết")] + [m for m in M if not ids or m[0] in ids]
    with ThreadPoolExecutor(8) as ex:
        results = list(ex.map(run_one, todo))
    json.dump(results, open(os.path.join(HERE, f"results_{which}.json"), "w"), ensure_ascii=False, indent=1)
    tally = {}
    for r in results:
        if not r["applied"]:
            verdict = f"NOT_APPLIED(count={r['count']})"
        else:
            bad = {k: v for k, v in r["checks"].items() if v["rc"] != 0}
            if not bad: verdict = "SURVIVED"
            elif all(v["traceback"] and not any("ASSERT-FAIL" in f or "✗" in f for f in v["fails"]) for v in bad.values()): verdict = "KILLED_CRASH by " + ",".join(bad)
            else: verdict = "KILLED_ASSERT by " + ",".join(bad)
        tally[verdict.split(" ")[0].split("(")[0]] = tally.get(verdict.split(" ")[0].split("(")[0], 0) + 1
        print(f"{r['id']:5s} {verdict:42s} {r['file']} | {r['note']}")
    print(tally)
