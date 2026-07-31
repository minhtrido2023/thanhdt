"""Viec 1 (dung nghia) — PBO episode-stratified NEO TREN 15 SU KIEN CAPIT THAT.

Ban _pbo_episode.py chia fold theo "run khac-baseline" -> 15 su kien gop lai chi con 5 run,
vi khi arm CAPIT da lech NAV thi chenh lech ton tai mai ve sau (khong tro ve 0). Script nay
neo fold vao DUNG ngay fire (record_type=EVENT_CAPIT) + cua so nam giu that cua tung su kien
(tu TX CAPIT_E<id>), roi:
  (a) CSCV chia doi 15 su kien (C(15,7)=6435 to hop day du),
  (b) bootstrap 20.000 lan chia doi ngau nhien 15 su kien.

Doc DAILY combined_nav tu 13 audit CSV da co — KHONG chay lai backtest.
"""
import glob
import itertools
import os
from collections import Counter
from math import comb

import numpy as np
import pandas as pd

D = "/home/trido/thanhdt/WorkingClaude/data"
LEGS = [
    ("capsz_ctrl", "cash"), ("capsz_idle", "idle"), ("capsz_booknav", "booknav"),
    ("capsz_nav10", "nav:0.10"), ("capsz_nav20", "nav:0.20"),
    ("capsz_idlecap30", "idlecap:0.30"), ("capsz_park25", "park:0.25"),
    ("capsz_park50", "park:0.50"), ("capsz_navsize15", "navsize:0.15"),
    ("capsz_navsize25", "navsize:0.25"), ("capsz_navsize30", "navsize:0.30"),
    ("capsz_navsize35", "navsize:0.35"), ("capsz_navsize40", "navsize:0.40"),
]


def leg_csv(tag):
    f = glob.glob(os.path.join(D, f"v23_golive_audit_2014_now_*_exp_{tag}_univpit.csv"))
    return f[0] if f else None


navs, ref_csv = {}, None
for tag, base in LEGS:
    f = leg_csv(tag)
    if not f:
        continue
    if base == "navsize:0.25":
        ref_csv = f
    df = pd.read_csv(f, low_memory=False)
    d = df[df.record_type == "DAILY"][["ymd", "combined_nav"]].copy()
    d["combined_nav"] = pd.to_numeric(d.combined_nav)
    navs[base] = d.sort_values("ymd").set_index("ymd")["combined_nav"]

idx = None
for s in navs.values():
    idx = s.index if idx is None else idx.intersection(s.index)
R = pd.DataFrame({k: navs[k].reindex(idx).pct_change() for k in navs}).dropna()
R.index = pd.to_datetime(R.index)
T, N = R.shape
print(f"legs={N}  T={T} phien  [{R.index[0].date()} -> {R.index[-1].date()}]")

# ---------------- cua so nam giu that cua tung su kien ----------------
ref = pd.read_csv(ref_csv, low_memory=False)
ev = ref[ref.record_type == "EVENT_CAPIT"][["ymd", "value"]].copy()
ev["ymd"] = pd.to_datetime(ev.ymd)
ev["size"] = pd.to_numeric(ev.value)
ev = ev.sort_values("ymd").reset_index(drop=True)

tx = ref[(ref.record_type == "TX") & ref.play_type.astype(str).str.startswith("CAPIT")].copy()
tx["ymd"] = pd.to_datetime(tx.ymd)
tx["eid"] = tx.play_type.str.extract(r"_E(\d+)$")[0].astype(int)

print(f"\nSo su kien CAPIT (EVENT_CAPIT) = {len(ev)}")
windows = []
for eid in range(len(ev)):
    d0 = ev.loc[eid, "ymd"]
    g = tx[tx.eid == eid]
    if g.empty:
        print(f"  E{eid:2d} {d0.date()} size={ev.loc[eid,'size']:.3f}  — KHONG co TX, bo qua")
        continue
    d1 = g.ymd.max()                      # phien cuoi con giao dich cua su kien nay
    m = (R.index >= d0) & (R.index <= d1)
    if m.sum() < 5:                       # cua so qua ngan -> keo toi thieu 20 phien
        pos = R.index.searchsorted(d0)
        m = np.zeros(T, bool)
        m[pos:min(pos + 20, T)] = True
    windows.append((eid, d0, d1, m))
    print(f"  E{eid:2d} {d0.date()} -> {d1.date()}  size={ev.loc[eid,'size']:.3f}  "
          f"{m.sum():4d} phien  n_tx={len(g)}")

blocks = [R.loc[m] for _, _, _, m in windows]
NE = len(blocks)
tot = sum(len(b) for b in blocks)
uniq = np.zeros(T, bool)
for _, _, _, m in windows:
    uniq |= m
print(f"\n{NE} su kien -> {tot} phien-khoi ({uniq.sum()} phien rieng biet, "
      f"{100*uniq.sum()/T:.1f}% timeline)")


def cscv(blocks, label, n_boot=None, seed=20260731):
    S = len(blocks)
    k = S // 2
    if n_boot is None:
        combos = list(itertools.combinations(range(S), k))
        tag = f"CSCV day du C({S},{k})={comb(S,k)}"
    else:
        rng = np.random.default_rng(seed)
        combos = [tuple(sorted(rng.permutation(S)[:k].tolist())) for _ in range(n_boot)]
        tag = f"bootstrap {n_boot} lan chia doi {S} su kien"
    logits, ranks, wins = [], [], Counter()
    for c in combos:
        cs = set(c)
        Ris = pd.concat([blocks[i] for i in c])
        Ros = pd.concat([blocks[i] for i in range(S) if i not in cs])
        sr_is = Ris.mean() / Ris.std(ddof=1)
        sr_os = Ros.mean() / Ros.std(ddof=1)
        best = sr_is.idxmax()
        wins[best] += 1
        rk = sr_os.rank().loc[best]
        w = rk / (N + 1.0)
        ranks.append(rk)
        logits.append(np.log(w / (1 - w)))
    logits = np.array(logits)
    pbo = float((logits <= 0).mean())
    print(f"\n=== {label} ===")
    print(f"  {tag}")
    print(f"  PBO = {pbo:.4f}   median OOS-rank(IS-best) = {np.median(ranks):.1f}/{N}"
          f"   logit mean = {logits.mean():+.4f}")
    print("  tan suat thang IS:")
    for kk, v in wins.most_common(6):
        print(f"    {kk:16s} {v:6d}/{len(combos)} ({100*v/len(combos):5.1f}%)")
    return pbo


p_a = cscv(blocks, f"VIEC 1 (a) — CSCV day du tren {NE} su kien CAPIT that")
p_b = cscv(blocks, f"VIEC 1 (b) — bootstrap tren {NE} su kien CAPIT that", n_boot=20000)

# ---- doi chieu: xep hang Sharpe CHI tren phien trong cua so su kien ----
Rev = pd.concat(blocks)
sr_ev = (Rev.mean() / Rev.std(ddof=1) * np.sqrt(252)).sort_values(ascending=False)
print("\nXep hang Sharpe CHI trong cua so su kien CAPIT (KHONG phai cong chon):")
for i, (k, v) in enumerate(sr_ev.items(), 1):
    mark = "  <== de xuat" if k == "navsize:0.25" else ("  (LIVE)" if k == "booknav" else "")
    print(f"  {i:2d}. {k:16s} SR={v:.4f}{mark}")

print("\n--- TOM TAT PBO moi dac ta ---")
print(f"  episode-anchored CSCV day du (S={NE} su kien) : {p_a:.4f}")
print(f"  episode-anchored bootstrap  (S={NE} su kien) : {p_b:.4f}")
print("  (calendar S=8/16/32 xem job_20260731_151958_pbo_episode.log)")
