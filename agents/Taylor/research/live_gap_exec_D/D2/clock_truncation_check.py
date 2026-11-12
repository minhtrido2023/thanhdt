#!/usr/bin/env python3
"""D2(a) self-check mạnh: với MỌI phiên t, chạy đúng logic get_dt_gate_clock() (extract_episodes trên chuỗi base CẮT tới t,
episode cuối 'censored' ⇒ active, k=length, need, cand) và so với clock per-day trong dt_clock_daily.csv. Kỳ vọng 0 lệch."""
import sys, os, numpy as np, pandas as pd
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor"); sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from dt_gate_hazard_research import extract_episodes
HERE = os.path.dirname(os.path.abspath(__file__))
C = pd.read_csv(os.path.join(HERE, "dt_clock_daily.csv"), parse_dates=["time"])
t, r = C.time.values, C.base.values.astype(int); bad = 0
for i in range(1, len(C)):
    ep = extract_episodes(t[:i + 1], r[:i + 1]); last = ep.iloc[-1].to_dict() if len(ep) else {}
    if last.get("outcome") == "censored": exp = (1, int(last["cand"]), int(last["length"]), int(last["need"]))
    else: exp = (0, 0, 0, 0)
    got = (int(C.active[i]), int(C.cand[i]), int(C.k[i]), int(C.need[i]))
    bad += exp != got
print(f"truncation check: {len(C)-1} phiên, lệch {bad}")
