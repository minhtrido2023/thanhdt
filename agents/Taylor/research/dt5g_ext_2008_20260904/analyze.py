# -*- coding: utf-8 -*-
import os, sys
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)
import pandas as pd, numpy as np

LABEL = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EXBULL"}

ext = pd.read_csv("mike/agents/Taylor/research/dt5g_ext_2008_20260904/dt5g_ext_2008_full.csv", parse_dates=["time"])
ext = ext.sort_values("time").reset_index(drop=True)

def episodes(df):
    """Contiguous runs of `state` -> list of (label, start, end, n_days)."""
    s = df["state"].values
    t = df["time"].values
    out = []
    i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and s[j+1] == s[i]:
            j += 1
        out.append((LABEL[int(s[i])], pd.Timestamp(t[i]).date(), pd.Timestamp(t[j]).date(), j - i + 1))
        i = j + 1
    return out

pre2014 = ext[ext["time"] < "2014-01-01"]
post2014 = ext[ext["time"] >= "2014-01-01"]

print("=" * 70)
print("EPISODES 2008-01-02 .. 2013-12-31 (extension segment)")
print("=" * 70)
ep_pre = episodes(pre2014)
for lab, a, b, n in ep_pre:
    print(f"  {lab:8s} {a} -> {b}  ({n} sessions)")

print()
print("=" * 70)
print("EPISODES 2014-01-01 .. now (existing production-warmup segment)")
print("=" * 70)
ep_post = episodes(post2014)
for lab, a, b, n in ep_post:
    print(f"  {lab:8s} {a} -> {b}  ({n} sessions)")

def summarize(eps, tag):
    from collections import Counter
    cnt = Counter(l for l, *_ in eps)
    print(f"\n--- {tag}: episode counts ---")
    for lab in ["CRISIS", "BEAR", "NEUTRAL", "BULL", "EXBULL"]:
        print(f"  {lab:8s} {cnt.get(lab,0)}")
    print(f"  TOTAL transitions (episode boundaries): {len(eps)-1}")

summarize(ep_pre, "2008-2013 (36 mo * ~12 = 72mo)" )
summarize(ep_post, "2014-2026 (~152mo)")

n_days_pre = len(pre2014); n_days_post = len(post2014)
print(f"\ntransition density: pre2014 = {(len(ep_pre)-1)}/{n_days_pre} sessions = {(len(ep_pre)-1)/n_days_pre*252:.2f} transitions/year-equiv")
print(f"transition density: post2014 = {(len(ep_post)-1)}/{n_days_post} sessions = {(len(ep_post)-1)/n_days_post*252:.2f} transitions/year-equiv")

# cap-fire summary pre-2014 (did the macro cap ever bind vs pure DT4 base?)
diff = (pre2014["state"] != pre2014["state_dt4"])
print(f"\npre-2014: macro cap changed state on {diff.sum()} / {len(pre2014)} days "
      f"({diff.sum()/len(pre2014)*100:.1f}%)")
if diff.sum():
    capdays = pre2014[diff]
    print(capdays[["time","state","state_dt4","cap"]].head(20).to_string())

ext.to_csv("mike/agents/Taylor/research/dt5g_ext_2008_20260904/dt5g_ext_2008_full.csv", index=False)
with open("mike/agents/Taylor/research/dt5g_ext_2008_20260904/episodes_pre2014.csv", "w") as f:
    f.write("label,start,end,n_sessions\n")
    for lab, a, b, n in ep_pre:
        f.write(f"{lab},{a},{b},{n}\n")
