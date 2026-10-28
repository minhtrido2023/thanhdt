#!/usr/bin/env python3
"""Dựng 300 case ẩn danh theo PREREG.md (md5 018bd323…). Chạy từ WC root cache:
BQ_LOCAL_CACHE=data/bq_cache OMP_NUM_THREADS=1 /home/trido/thanhdt/wc_venv/bin/python build_cases.py
Cột giá: tav2_bq.ticker Open/High/Low/Close (Close đã điều chỉnh; cùng nguồn lag_events.py / nav_overlay.py).
"""
import os, sys, json
import numpy as np, pandas as pd
WC = "/home/trido/thanhdt/WorkingClaude"; OUT = os.path.dirname(os.path.abspath(__file__))
ER = f"{WC}/mike/agents/Taylor/research/entry_risk_tech_20261022"
sys.path.insert(0, WC); os.chdir(WC)
from simulate_holistic_nav import bq  # noqa: E402

SEED = 20261022; W = 250; NJ = 0.30
lag = pd.read_csv(f"{ER}/lag_events_features.csv", parse_dates=["entry"])
lag = lag.assign(book="LAG", ent=lag["entry"], ret=lag["Y"])[["ticker","ent","book","G_VOL","HIT15","ret","VOL60","RUN20","DIST52","season"]]
pos = pd.read_csv(f"{ER}/positions_features.csv", parse_dates=["e"])
pos = pos[(pos.tag == "pin0") & (pos.book == "BAL")]
pos = pos.assign(ent=pos["e"], season=pos["q"])[["ticker","ent","book","G_VOL","HIT15","ret","VOL60","RUN20","DIST52","season"]]
ev = pd.concat([lag, pos], ignore_index=True)
ev = ev[ev.ent >= "2015-03-01"].dropna(subset=["HIT15","G_VOL"]).reset_index(drop=True)
tks = ",".join(f"'{t}'" for t in sorted(ev.ticker.unique()))
px = bq(f"SELECT t.ticker, t.time, t.Open, t.High, t.Low, t.Close, t.Volume FROM tav2_bq.ticker AS t WHERE t.ticker IN ({tks}) AND t.time >= DATE '2012-10-01' AND t.Close > 0")
px["time"] = pd.to_datetime(px["time"]); px = px.sort_values(["ticker","time"])
by = {tk: g.reset_index(drop=True) for tk, g in px.groupby("ticker")}

def kidx(r):
    g = by.get(r.ticker)
    if g is None: return -1
    return int(np.searchsorted(g["time"].values, np.datetime64(r.ent)))
ev["k"] = [kidx(r) for r in ev.itertuples()]
ev["ok_hist"] = ev.k >= W   # >=250 phiên TRƯỚC ngày vào
n0 = len(ev); ev = ev[ev.ok_hist].reset_index(drop=True)
print(f"sự kiện >=2015-03-01: {n0}; đủ >=250 phiên trước vào: {len(ev)}")

def window(r):
    g = by[r.ticker]; return g.iloc[r.k - W:r.k]
def jump(w):
    C = w.Close.values; O = w.Open.values
    cc = np.abs(C[1:] / C[:-1] - 1).max(); oc = np.abs(O[1:] / C[:-1] - 1).max()
    return max(cc, oc) > NJ

rng = np.random.default_rng(SEED)
tick_n = {}; tick_ks = {}
chosen = []; dropped_jump = 0; dropped_rule = 0; short = {}
for gv in (True, False):
    for book, need in (("LAG", 100), ("BAL", 50)):
        pool = ev[(ev.G_VOL == gv) & (ev.book == book)]
        order = rng.permutation(len(pool)); got = 0
        for i in order:
            if got >= need: break
            r = pool.iloc[i]
            if tick_n.get(r.ticker, 0) >= 3: dropped_rule += 1; continue
            if any(abs(r.k - k2) < 40 for k2 in tick_ks.get(r.ticker, [])): dropped_rule += 1; continue
            w = window(r)
            if jump(w) or w.isna().any().any() or w.Volume.median() <= 0:
                dropped_jump += 1; continue
            chosen.append(r); got += 1
            tick_n[r.ticker] = tick_n.get(r.ticker, 0) + 1; tick_ks.setdefault(r.ticker, []).append(r.k)
        short[(gv, book)] = (got, need, len(pool))
print("n thực tế theo (G_VOL,book): ", short)
print(f"loại vì nhảy giá >30% (corp-action chưa chỉnh) hoặc NaN/vol0: {dropped_jump}; loại vì luật mã/giãn cách: {dropped_rule}")
ch = pd.DataFrame(chosen).reset_index(drop=True)
perm = rng.permutation(len(ch)); ch = ch.iloc[perm].reset_index(drop=True)
ch["id"] = [f"E{i+1:03d}" for i in range(len(ch))]
cases = []
for r in ch.itertuples():
    w = window(r); c0 = w.Close.values[0]; m = np.median(w.Volume.values)
    rows = ["i,O,H,L,C,V"]
    for i, (o, h, l, c, v) in enumerate(zip(w.Open, w.High, w.Low, w.Close, w.Volume)):
        rows.append(f"{i},{o/c0*100:.2f},{h/c0*100:.2f},{l/c0*100:.2f},{c/c0*100:.2f},{v/m:.2f}")
    cases.append({"id": r.id, "data": "\n".join(rows)})
with open(f"{OUT}/cases.jsonl", "w") as f:
    for c in cases: f.write(json.dumps(c) + "\n")
ch[["id","ticker","ent","book","G_VOL","HIT15","ret","VOL60","RUN20","DIST52","season","k"]].to_csv(f"{OUT}/case_key_HIDDEN.csv", index=False)
# kiểm rò rỉ
import re
leak = 0
for c, r in zip(cases, ch.itertuples()):
    s = c["data"]
    if re.search(r"[A-Za-z]{3}", s.replace("i,O,H,L,C,V","")) or str(r.ent.year) in s.split("\n")[0]: leak += 1
print(f"N={len(cases)} | book: {ch.book.value_counts().to_dict()} | G_VOL: {ch.G_VOL.value_counts().to_dict()} | mã: {ch.ticker.nunique()} | rò rỉ chữ cái trong data: {leak}")
print("HIT15 (chỉ để log kích thước, KHÔNG dùng chấm ở bước này) — số dương tính:", int(ch.HIT15.sum()))
for c in cases[:2]: print("\n=== MẪU", c["id"], "===\n" + "\n".join(c["data"].split("\n")[:6]) + "\n...\n" + "\n".join(c["data"].split("\n")[-3:]))
