#!/usr/bin/env python3
"""Ngày có kích hoạt trên mã đang giữ (stage 1, code mới ∪ cũ) + 3 phiên sau (carryover) → days/case_<i>.txt."""
import glob, json, os, sys
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
d = pd.read_parquet(os.path.join(os.path.dirname(HERE), "intraday_cutloss_replay_20261009", "cache", "daily.parquet"))
TD = sorted(d[d.ticker == "VNINDEX"].time.dt.date.astype(str).unique())
cd = set()
for f in glob.glob(os.path.join(HERE, "runs", "v2_*_BROKEN_d0.5_t3_s*", "shadow_*.jsonl")):
    for line in open(f):
        r = json.loads(line)
        if r["kind"] == "TRIGGER" and r.get("holdings"):
            cd.add(r["ts"][:10])
days = set()
for x in cd:
    i = TD.index(x) if x in TD else None
    days.add(x)
    if i is not None:
        days.update(TD[i + 1:i + 4])
days = sorted(x for x in days if x <= "2026-10-09")
n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
k = len(days) // n + 1
for i in range(n):
    open(os.path.join(HERE, "days", f"case_{i}.txt"), "w").write("\n".join(days[i * k:(i + 1) * k]))
print(len(cd), "case days;", len(days), "days incl. carryover")
