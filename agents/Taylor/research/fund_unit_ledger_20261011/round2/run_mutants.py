#!/usr/bin/env python3
"""Chạy bộ mutant trên bản sao SANDBOX của bin/ nhánh (không đụng worktree, không đụng data/ thật).
Dựa trên `arch_review_feaa33b5/mut/run.py` của reviewer — chỉ sửa đường dẫn sandbox + chia shard.

    python3 run_mutants.py <mutants.py> <out.json> [--shards N] [--only ID ...]

Mỗi shard = một cây `<SBX>/s<k>/WC/{wc_env.sh, data/…, mike/{MIKE.md, bin/…}}` riêng. Một mutant
= thay đúng 1 chuỗi trong 1 file của bản sao, chạy lần lượt TESTS, dừng ở test đầu tiên rc != 0.
Phân loại: KILLED_ASSERT (đầu ra có ASSERT-FAIL / AssertionError / dòng FAIL của bộ case),
KILLED_CRASH (rc != 0 mà không có dấu assertion), SURVIVED, NOAPPLY (chuỗi gốc không còn / không
duy nhất trong code hiện tại).
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

WT = "/home/trido/thanhdt/WorkingClaude/wt-fundunit-1011"
REAL = "/home/trido/thanhdt/WorkingClaude/data"
SBX = os.environ.get("FU_SBX", "/tmp/fu_r2_mut")
TESTS = [["bin/nav_unit_ledger_selfcheck.py"], ["bin/nav_flow_term_selfcheck.py"],
         ["bin/nav_jump_flow_gate_selfcheck.py"], ["bin/report_delivery_gate_selfcheck.py"],
         ["bin/nav_period_returns.py", "--selfcheck"]]
if os.environ.get("FU_TESTS"):          # ghi đè danh sách test, vd FU_TESTS=bin/portfolio_status_selfcheck.py
    TESTS = [t.split() for t in os.environ["FU_TESTS"].split(",")]
ENV = {k: v for k, v in os.environ.items()
       if k not in ("TZ", "WC_ROOT", "MIKE_ROOT", "NAV_UNIT_LEDGER_DIR", "ACCOUNT_CASH_FLOWS_PATH")}
ENV["PYTHONDONTWRITEBYTECODE"] = "1"


def build_sandbox(k):
    root = f"{SBX}/s{k}/WC"
    shutil.rmtree(f"{SBX}/s{k}", ignore_errors=True)
    os.makedirs(f"{root}/data/execution_logs")
    os.makedirs(f"{root}/mike")
    open(f"{root}/wc_env.sh", "w").close()
    open(f"{root}/mike/MIKE.md", "w").write("sandbox\n")
    shutil.copytree(f"{WT}/bin", f"{root}/mike/bin", ignore=shutil.ignore_patterns("__pycache__"))
    for f in ("account_inception.json", "account_cash_flows.json"):
        shutil.copy2(f"{REAL}/{f}", f"{root}/data/{f}")
    for a in ("SpaceX", "ZaloPay"):
        shutil.copy2(f"{REAL}/execution_logs/nav_history_{a}.csv", f"{root}/data/execution_logs")
    return f"{root}/mike"


def run_tests(sb):
    for t in TESTS:
        try:
            p = subprocess.run([sys.executable] + t, cwd=sb, capture_output=True, text=True,
                               env=ENV, timeout=300)
        except subprocess.TimeoutExpired:
            return "TIMEOUT", t[0], ""
        if p.returncode != 0:
            out = p.stdout + p.stderr
            by = os.path.basename(t[0]) + (" --selfcheck" if len(t) > 1 else "")
            asserted = ("ASSERT-FAIL" in out or "AssertionError" in out
                        or "FAIL" in out.replace("ASSERT-FAIL", ""))     # gồm "[FAIL] …" / "SELFCHECK FAILED"
            tail = [ln for ln in out.strip().splitlines() if ln.strip()]
            pick = next((ln for ln in tail if "ASSERT-FAIL" in ln or "AssertionError" in ln
                         or ln.strip().startswith(("FAIL", "[FAIL]"))), tail[-1] if tail else "")
            return ("KILLED_ASSERT" if asserted else "KILLED_CRASH"), by, pick.strip()[:260]
    return "SURVIVED", "", ""


def work(k, mutants):
    sb = build_sandbox(k)
    base = run_tests(sb)
    if base[0] != "SURVIVED":
        return [("__BASELINE__", "", "BASELINE_RED", base[1], base[2], 0)]
    res = []
    for m in mutants:
        mid, fn, old, new = m[:4]
        occ = m[4] if len(m) > 4 else None
        src = open(f"{WT}/bin/{fn}", encoding="utf-8").read()
        cnt = src.count(old)
        if cnt == 0 or (occ is None and cnt != 1):
            res.append((mid, fn, "NOAPPLY", f"count={cnt}", "", 0))
            print(mid, "NOAPPLY", cnt, flush=True)
            continue
        idx = -1
        for _ in range((occ or 0) + 1):
            idx = src.index(old, idx + 1)
        line = src[:idx].count("\n") + 1
        open(f"{sb}/bin/{fn}", "w", encoding="utf-8").write(src[:idx] + new + src[idx + len(old):])
        try:
            verdict, by, detail = run_tests(sb)
        finally:
            shutil.copy2(f"{WT}/bin/{fn}", f"{sb}/bin/{fn}")
        res.append((mid, fn, verdict, by, detail, line))
        print(mid, fn, f"L{line}", verdict, by, "|", detail, flush=True)
    return res


def main():
    args = sys.argv[1:]
    mfile, out = args[0], args[1]
    shards = int(args[args.index("--shards") + 1]) if "--shards" in args else 4
    only = set(args[args.index("--only") + 1:]) if "--only" in args else set()
    spec = importlib.util.spec_from_file_location("mutants_mod", mfile)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    todo = [m for m in mod.M if not only or m[0] in only]
    ids = [m[0] for m in todo]
    assert len(ids) == len(set(ids)), f"id mutant trùng: {[i for i in ids if ids.count(i) > 1]}"
    parts = [todo[i::shards] for i in range(shards)]
    with ThreadPoolExecutor(shards) as ex:
        chunks = list(ex.map(lambda kv: work(*kv), enumerate(parts)))
    res = [r for c in chunks for r in c]
    order = {mid: i for i, mid in enumerate(ids)}
    res.sort(key=lambda r: order.get(r[0], -1))
    json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
    from collections import Counter
    print(Counter(r[2] for r in res))


if __name__ == "__main__":
    main()
