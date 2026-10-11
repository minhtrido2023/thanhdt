import sys, os, shutil, subprocess, json, concurrent.futures as cf
sys.path.insert(0, "/tmp/ar3/mut")
import importlib, os
M = importlib.import_module(os.environ.get("MUTSET", "mutants")).M
BASE = "/tmp/ar3/WC"; OUT = "/tmp/ar3/mut/work"
CORE = [["bin/nav_unit_ledger_selfcheck.py"], ["bin/nav_flow_term_selfcheck.py"], ["bin/nav_jump_flow_gate_selfcheck.py"], ["bin/nav_period_returns.py", "--selfcheck"]]
DNS = [["bin/daily_nav_snapshot_from_raw_selfcheck.py"], ["bin/nav_corpaction_gate_e2e_selfcheck.py"], ["bin/daily_nav_snapshot_corpaction_error_selfcheck.py"]]
PSS = [["bin/portfolio_status_selfcheck.py"]]
def suite(file):
    if file.endswith("daily_nav_snapshot.py"): return CORE + DNS
    if file.endswith("portfolio_status.py"): return PSS
    return CORE
def run_one(m):
    mid, file, old, new, note = m
    src = open(f"{BASE}/mike/{file}", encoding="utf-8").read()
    n = src.count(old)
    if n != 1: return {"id": mid, "file": file, "status": f"NOT_APPLIED(count={n})", "note": note}
    wd = f"{OUT}/{mid}/WC"
    shutil.rmtree(f"{OUT}/{mid}", ignore_errors=True)
    os.makedirs(f"{wd}/mike"); shutil.copytree(f"{BASE}/mike/bin", f"{wd}/mike/bin"); shutil.copytree(f"{BASE}/mike/kb", f"{wd}/mike/kb")
    shutil.copytree(f"{BASE}/data", f"{wd}/data"); open(f"{wd}/wc_env.sh", "w").close()
    os.symlink("/home/trido/thanhdt/WorkingClaude/trading_bot", f"{wd}/trading_bot")
    open(f"{wd}/mike/{file}", "w", encoding="utf-8").write(src.replace(old, new))
    line = src[:src.index(old)].count("\n") + 1
    env = {k: v for k, v in os.environ.items() if k not in ("TZ", "WC_ROOT")}
    env["NO_GCE_CHECK"] = "true"; env["PYTHONDONTWRITEBYTECODE"] = "1"
    res = {"id": mid, "file": file, "line": line, "note": note, "status": "SURVIVED", "by": None, "tail": ""}
    for cmd in suite(file):
        try:
            p = subprocess.run([sys.executable] + cmd, cwd=f"{wd}/mike", env=env, capture_output=True, text=True, timeout=240)
        except subprocess.TimeoutExpired:
            res.update(status="KILLED_TIMEOUT", by=cmd[0]); break
        if p.returncode != 0:
            txt = (p.stdout + "\n" + p.stderr).strip()
            last = [l for l in txt.splitlines() if l.strip()][-1] if txt else ""
            is_assert = ("AssertionError" in txt) or ("ASSERT-FAIL" in txt) or ("FAIL" in last) or ("[FAIL]" in txt) or ("❌" in txt and "Traceback" not in txt)
            res.update(status="KILLED_ASSERT" if is_assert else "KILLED_CRASH", by=" ".join(cmd), tail=last[:260])
            break
    shutil.rmtree(f"{OUT}/{mid}", ignore_errors=True)
    return res
if __name__ == "__main__":
    only = set(sys.argv[1:])
    todo = [m for m in M if not only or m[0] in only]
    with cf.ThreadPoolExecutor(max_workers=14) as ex:
        results = list(ex.map(run_one, todo))
    json.dump(results, open("/tmp/ar3/mut/results_" + os.environ.get("MUTSET", "mutants") + ".json", "w"), ensure_ascii=False, indent=1)
    import collections
    c = collections.Counter(r["status"].split("(")[0] for r in results)
    print(dict(c))
    for r in results:
        if not r["status"].startswith("KILLED_ASSERT"):
            print(r["id"], r["status"], f"{r['file']}:{r.get('line')}", "|", r["note"], "|", r.get("by"), "|", r.get("tail", "")[:200])
