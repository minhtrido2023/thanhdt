"""Follow-up robustness (job Taylor_20260731_121454) — 2 viec reviewer de xuat:

  1) PBO episode-stratified CSCV: chia fold theo TUNG SU KIEN CAPIT that (thay vi
     194-phien/khoi theo lich, lam 4/16 khoi rong khong co su kien).
  2) Do nhay PBO theo do chi tiet khoi lich: S=8 / S=16 (goc) / S=32.

Doc DAILY combined_nav tu 13 audit CSV da co (KHONG chay lai backtest) — cung nguon
va cung quy uoc voi job_20260731_111654_dsr_pbo.py.
"""
import glob
import itertools
import os
from collections import Counter

import numpy as np
import pandas as pd

D = "/home/trido/thanhdt/WorkingClaude/data"
LEGS = [
    ("capsz_ctrl", "cash"),
    ("capsz_idle", "idle"),
    ("capsz_booknav", "booknav"),
    ("capsz_nav10", "nav:0.10"),
    ("capsz_nav20", "nav:0.20"),
    ("capsz_idlecap30", "idlecap:0.30"),
    ("capsz_park25", "park:0.25"),
    ("capsz_park50", "park:0.50"),
    ("capsz_navsize15", "navsize:0.15"),
    ("capsz_navsize25", "navsize:0.25"),
    ("capsz_navsize30", "navsize:0.30"),
    ("capsz_navsize35", "navsize:0.35"),
    ("capsz_navsize40", "navsize:0.40"),
]


def load_nav(tag):
    f = glob.glob(os.path.join(D, f"v23_golive_audit_2014_now_*_exp_{tag}_univpit.csv"))
    if not f:
        return None
    df = pd.read_csv(f[0], low_memory=False)
    d = df[df.record_type == "DAILY"][["ymd", "combined_nav"]].copy()
    d["combined_nav"] = pd.to_numeric(d.combined_nav)
    return d.sort_values("ymd").set_index("ymd")["combined_nav"]


navs = {}
for tag, base in LEGS:
    s = load_nav(tag)
    if s is not None:
        navs[base] = s
idx = None
for s in navs.values():
    idx = s.index if idx is None else idx.intersection(s.index)
R = pd.DataFrame({k: navs[k].reindex(idx).pct_change() for k in navs}).dropna()
T, N = R.shape
print(f"legs={N}  T={T} phien  [{R.index[0]} -> {R.index[-1]}]")


def pbo_from_blocks(blocks, label, n_is=None):
    """CSCV chuan: moi to hop IS/OOS -> rank OOS cua config thang IS."""
    S = len(blocks)
    k = n_is if n_is is not None else S // 2
    combos = list(itertools.combinations(range(S), k))
    logits, ranks, wins = [], [], Counter()
    for c in combos:
        cs = set(c)
        Ris = pd.concat([blocks[i] for i in c])
        Ros = pd.concat([blocks[i] for i in range(S) if i not in cs])
        sr_is = Ris.mean() / Ris.std(ddof=1)
        sr_os = Ros.mean() / Ros.std(ddof=1)
        best = sr_is.idxmax()
        wins[best] += 1
        rk = sr_os.rank().loc[best]          # 1 = te nhat ... N = tot nhat
        w = rk / (N + 1.0)
        ranks.append(rk)
        logits.append(np.log(w / (1 - w)))
    logits = np.array(logits)
    pbo = float((logits <= 0).mean())
    print(f"\n=== {label} ===")
    print(f"  S={S} khoi, IS={k} khoi, so to hop={len(combos)}")
    print(f"  PBO = {pbo:.4f}   median OOS-rank(IS-best) = {np.median(ranks):.1f}/{N}"
          f"   logit mean = {logits.mean():+.4f}")
    print("  tan suat thang IS:")
    for kk, v in wins.most_common(6):
        print(f"    {kk:16s} {v:6d}/{len(combos)} ({100*v/len(combos):5.1f}%)")
    return pbo, float(np.median(ranks)), wins


# =====================================================================
# Ep: xac dinh SU KIEN CAPIT tu chinh du lieu — ngay nao cac leg khac nhau
# =====================================================================
dev = (R.sub(R["cash"], axis=0).abs().max(axis=1) > 1e-12).values
pos = np.where(dev)[0]
print(f"\nSo phien co it nhat 1 leg khac baseline `cash`: {len(pos)}/{T} ({100*len(pos)/T:.1f}%)")

GAP = 20   # >20 phien lien tiep khong-khac = tach su kien moi
runs = []
start = pos[0]
prev = pos[0]
for p in pos[1:]:
    if p - prev > GAP:
        runs.append((start, prev))
        start = p
    prev = p
runs.append((start, prev))
print(f"So RUN khac-baseline (gap>{GAP} phien tach doi) = {len(runs)}")
for i, (a, b) in enumerate(runs):
    print(f"  run{i:2d}: {R.index[a]} -> {R.index[b]}  ({b-a+1} phien)")

# ---- Variant A: phan hoach TOAN BO timeline thanh len(runs) doan, moi doan 1 su kien
bounds = [0]
for i in range(1, len(runs)):
    bounds.append((runs[i - 1][1] + runs[i][0]) // 2)
bounds.append(T)
blocksA = [R.iloc[bounds[i]:bounds[i + 1]] for i in range(len(runs))]
print(f"\nVariant A — {len(blocksA)} doan lich phu kin T, moi doan chua dung 1 su kien"
      f" (do dai: min={min(len(b) for b in blocksA)} median={int(np.median([len(b) for b in blocksA]))}"
      f" max={max(len(b) for b in blocksA)})")

# ---- Variant B: CHI cac phien khac-baseline, gom theo su kien
blocksB = [R.iloc[a:b + 1] for a, b in runs]
print(f"Variant B — chi {sum(len(b) for b in blocksB)} phien active, {len(blocksB)} khoi")

nA = len(blocksA)
resA = pbo_from_blocks(blocksA, f"VIEC 1a — episode-stratified CSCV (doan lich, 1 su kien/khoi, S={nA})",
                       n_is=nA // 2)
resB = pbo_from_blocks(blocksB, f"VIEC 1b — episode-stratified CSCV (CHI phien active, S={nA})",
                       n_is=nA // 2)

# ---- Variant C: bootstrap tren cac su kien roi rac (resample co hoan lai)
rng = np.random.default_rng(20260731)
NB = 20000
logits, ranks, wins = [], [], Counter()
ne = len(blocksB)
for _ in range(NB):
    perm = rng.permutation(ne)
    ci, co = perm[: ne // 2], perm[ne // 2:]
    Ris = pd.concat([blocksB[i] for i in ci])
    Ros = pd.concat([blocksB[i] for i in co])
    sr_is = Ris.mean() / Ris.std(ddof=1)
    sr_os = Ros.mean() / Ros.std(ddof=1)
    best = sr_is.idxmax()
    wins[best] += 1
    rk = sr_os.rank().loc[best]
    w = rk / (N + 1.0)
    ranks.append(rk)
    logits.append(np.log(w / (1 - w)))
logits = np.array(logits)
print(f"\n=== VIEC 1c — bootstrap {NB} lan chia doi {ne} su kien roi rac (chi phien active) ===")
print(f"  PBO = {(logits<=0).mean():.4f}   median OOS-rank = {np.median(ranks):.1f}/{N}")
for kk, v in wins.most_common(6):
    print(f"    {kk:16s} {v:6d}/{NB} ({100*v/NB:5.1f}%)")

# =====================================================================
# VIEC 2 — do nhay PBO theo do chi tiet khoi LICH (S=8 / 16 / 32)
# =====================================================================
print("\n" + "=" * 70)
for S in (8, 16, 32):
    n = T // S
    blocks = [R.iloc[i * n:(i + 1) * n] for i in range(S)]
    n_empty = sum(1 for b in blocks
                  if (b.sub(b["cash"], axis=0).abs().max(axis=1) <= 1e-12).all())
    print(f"\n[S={S}] block={n} phien; so khoi RONG (khong su kien CAPIT nao) = {n_empty}/{S}")
    pbo_from_blocks(blocks, f"VIEC 2 — calendar CSCV S={S}")

# =====================================================================
# Doi chieu: navsize:0.25 dung o dau trong xep hang OOS?
# =====================================================================
print("\n" + "=" * 70)
print("Xep hang Sharpe toan mau (de doi chieu, KHONG phai cong chon):")
sr = (R.mean() / R.std(ddof=1) * np.sqrt(252)).sort_values(ascending=False)
for i, (k, v) in enumerate(sr.items(), 1):
    mark = "  <== de xuat" if k == "navsize:0.25" else ("  (LIVE)" if k == "booknav" else "")
    print(f"  {i:2d}. {k:16s} SR={v:.4f}{mark}")
