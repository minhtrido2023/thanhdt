#!/usr/bin/env python3
"""Chạy mutant vòng 2 trong SANDBOX (bản sao bin/ của worktree + dữ liệu giả của reviewer ở
/tmp/archrev_fcf/SEED) — không chạm data/ thật. Bố cục sandbox + cách phán quyết y như
arch_review_ea9d6969a/run.py (rc != 0 ở bất kỳ selfcheck nào = mutant bị giết).
Dùng: run_r2.py <rev|step2|ar3|new> [--dry] [id ...]      (--dry: chỉ kiểm chuỗi `old` còn áp được)
"""
import json
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
PRISTINE = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-fundcf-1012/bin"
SEED = "/tmp/archrev_fcf/SEED"
TB = "/home/trido/thanhdt/WorkingClaude/trading_bot"
BOXES = "/tmp/fcf_r2/boxes"
CHECKS = [("cashid", ["cash_identity_selfcheck.py"]), ("ledger", ["nav_unit_ledger_selfcheck.py"]),
          ("jump", ["nav_jump_flow_gate_selfcheck.py"]), ("e2e", ["nav_corpaction_gate_e2e_selfcheck.py"]),
          ("flowterm", ["nav_flow_term_selfcheck.py"]), ("npr", ["nav_period_returns.py", "--selfcheck"]),
          ("rdg", ["report_delivery_gate_selfcheck.py"])]
sys.path.insert(0, HERE)
from mutants_r2 import suite  # noqa: E402

which = sys.argv[1]
dry = "--dry" in sys.argv
ids = {a for a in sys.argv[2:] if not a.startswith("--")}


def run_one(m):
    mid, fname, old, new, note = m
    src = open(os.path.join(PRISTINE, fname), encoding="utf-8").read()
    n = src.count(old) if mid != "BASE" else 1
    if n != 1:
        return {"id": mid, "applied": False, "count": n, "note": note, "file": fname}
    if dry:
        return {"id": mid, "applied": True, "file": fname, "note": note, "checks": {}}
    box = f"{BOXES}/box_{which}_{mid}"
    shutil.rmtree(box, ignore_errors=True)
    os.makedirs(f"{box}/WC/mike")
    shutil.copytree(PRISTINE, f"{box}/WC/mike/bin", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(f"{SEED}/data", f"{box}/WC/data")
    os.symlink(TB, f"{box}/WC/trading_bot")
    open(f"{box}/WC/wc_env.sh", "w").close()
    open(f"{box}/WC/mike/MIKE.md", "w").close()
    if mid != "BASE":
        open(f"{box}/WC/mike/bin/{fname}", "w", encoding="utf-8").write(src.replace(old, new))
    env = dict(os.environ, MIKE_BOT_TEST_MODE="1", PYTHONDONTWRITEBYTECODE="1")
    for k in ("TZ", "WC_ROOT", "MIKE_ROOT", "ACCOUNT_CASH_FLOWS_PATH"):
        env.pop(k, None)
    res = {"id": mid, "applied": True, "file": fname, "note": note, "checks": {}}
    for name, cmd in CHECKS:
        try:
            r = subprocess.run([sys.executable] + cmd, cwd=f"{box}/WC/mike/bin", env=env, capture_output=True,
                               text=True, timeout=400)
            out = r.stdout + "\n" + r.stderr
            fails = [line for line in out.splitlines() if "ASSERT-FAIL" in line or "AssertionError" in line or "FAIL" in line]
            res["checks"][name] = {"rc": r.returncode, "fails": [f[:300] for f in fails[:2]],
                                   "tail": out.strip().splitlines()[-1][:300] if out.strip() else ""}
        except subprocess.TimeoutExpired:
            res["checks"][name] = {"rc": "timeout", "fails": [], "tail": ""}
    shutil.rmtree(box, ignore_errors=True)
    return res


if __name__ == "__main__":
    todo = [("BASE", "cash_identity.py", "", "", "không mutant — phải xanh hết")] + [
        m for m in suite(which) if not ids or m[0] in ids]
    with ThreadPoolExecutor(16) as ex:
        results = list(ex.map(run_one, todo))
    if not dry:
        json.dump(results, open(os.path.join(HERE, f"results_{which}.json"), "w"), ensure_ascii=False, indent=1)
    tally = {"KILLED": 0, "SURVIVED": 0, "NOT_APPLIED": 0}
    for r in results:
        if not r["applied"]:
            tally["NOT_APPLIED"] += 1
            print(f"{r['id']:5s} NOT_APPLIED(count={r['count']}) {r['file']} | {r['note']}")
            continue
        if dry:
            continue
        bad = {k: v for k, v in r["checks"].items() if v["rc"] != 0}
        if r["id"] == "BASE":
            print(f"BASE  {'XANH HẾT' if not bad else 'ĐỎ: ' + ','.join(bad)}")
            continue
        tally["SURVIVED" if not bad else "KILLED"] += 1
        print(f"{r['id']:5s} {'SURVIVED' if not bad else 'KILLED by ' + ','.join(bad):38s} {r['file'][:24]:24s} | {r['note']}")
    print(f"== bộ {which}: {len(results) - 1} mutant · " + " · ".join(f"{k} {v}" for k, v in tally.items()))
