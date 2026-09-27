#!/usr/bin/env python3
"""PREREG v2 analyses (1)-(4): paired block bootstrap + episode leave-out + DD-threshold
sensitivity + minimax regret, on the 12 park-fraction legs from job Taylor_20260927_064747.

PAIRED = one block-index sequence per bootstrap path, applied to ALL 12 legs, so each path is
the SAME resampled world seen at 12 different park fractions. 12 independent bootstraps
(what vong 1 did) cannot answer "is 30 better than 0" because the noise is not shared.

Calendar-year annualization + L=21 + B=4000 + seed=12345 copied from bootstrap_nav.py.
"""
import sys, glob, json, numpy as np, pandas as pd

HERE = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/park_fraction_grid_20260927"
DATA = "/home/trido/thanhdt/WorkingClaude/data"
TAGS = ["000","010","020","030","040","050","060","070","075","080","090","100"]
XS = np.array([int(t)/100 for t in TAGS])
L, B, SEED = 21, 4000, 12345

def load_nav(tag):
    hits = sorted(glob.glob(f"{DATA}/*_parkgrid_{tag}_univpit.csv"))
    assert len(hits) == 1, (tag, hits)
    df = pd.read_csv(hits[0], low_memory=False)
    d = df.dropna(subset=["combined_nav"])
    t = pd.to_datetime(d["ymd"], errors="coerce")
    d = d[t.notna()]; t = t[t.notna()]
    s = d.groupby(t.dt.normalize())["combined_nav"].last().astype(float)
    return hits[0], s

srcs, navs = {}, {}
for t in TAGS:
    p, s = load_nav(t); srcs[t] = p.split("/")[-1]; navs[t] = s

idx0 = navs["000"].index
for t in TAGS:
    assert navs[t].index.equals(idx0), f"{t}: date index differs from leg 000 — paired bootstrap invalid"
print(f"12 legs aligned on the SAME {len(idx0)} calendar days {idx0[0].date()} -> {idx0[-1].date()}")

R = np.column_stack([np.diff(np.log(navs[t].values)) for t in TAGS])   # (N, 12)
N = R.shape[0]
YRS = (idx0[-1] - idx0[0]).days / 365.25
ANN = N / YRS
print(f"N_ret={N}  calendar years={YRS:.3f}  obs/yr={ANN:.1f}\n")

def metrics(r):
    """r: (n, 12) log-returns -> CAGR, Sharpe, MaxDD, Calmar per column."""
    nav = np.exp(np.cumsum(r, axis=0))
    peak = np.maximum.accumulate(nav, axis=0)
    yrs = r.shape[0] / ANN
    cagr = nav[-1] ** (1 / yrs) - 1
    sh = r.mean(axis=0) / r.std(axis=0) * np.sqrt(ANN)
    dd = (nav / peak - 1).min(axis=0)
    return cagr, sh, dd, cagr / np.abs(dd)

ACT = metrics(R)

# ---------- (1) PAIRED block bootstrap ----------
rng = np.random.default_rng(SEED)
nblk = int(np.ceil(N / L))
C = np.empty((B, 12)); S = np.empty((B, 12)); D = np.empty((B, 12)); K = np.empty((B, 12))
off = np.arange(L)
for b in range(B):
    st = rng.integers(0, N, nblk)                      # ONE index sequence, shared by all 12 legs
    ix = ((st[:, None] + off[None, :]) % N).ravel()[:N]
    C[b], S[b], D[b], K[b] = metrics(R[ix])

argmax = K.argmax(axis=1)
p_argmax = np.bincount(argmax, minlength=12) / B
p_gt0 = (K > K[:, [0]]).mean(axis=0)
EK, ED, EC = K.mean(axis=0), D.mean(axis=0), C.mean(axis=0)
D5 = np.percentile(D, 5, axis=0); C5 = np.percentile(C, 5, axis=0)
K5 = np.percentile(K, 5, axis=0); K95 = np.percentile(K, 95, axis=0)

FLOOR = {th: D5[0] - th/100 for th in (1.5, 2.0, 3.0)}
ok20 = D5 >= FLOOR[2.0]

print("=== (1) PAIRED block bootstrap (L=21, B=4000, seed=12345, same block index all 12 legs) ===")
print(f"{'x':>5} {'Calmar_act':>10} {'E[Calmar]':>9} {'Cal5th':>7} {'Cal95th':>7} {'P(argmax)':>9} "
      f"{'P(>x=0)':>8} {'E[MaxDD]':>9} {'DD5th':>7} {'E[CAGR]':>8} {'CAGR5th':>8} {'DDgate2.0':>9}")
for i, t in enumerate(TAGS):
    print(f"{XS[i]:5.2f} {ACT[3][i]:10.3f} {EK[i]:9.3f} {K5[i]:7.3f} {K95[i]:7.3f} {p_argmax[i]:9.3f} "
          f"{p_gt0[i]:8.3f} {ED[i]*100:8.1f}% {D5[i]*100:6.1f}% {EC[i]*100:7.2f}% {C5[i]*100:7.2f}% "
          f"{'OK' if ok20[i] else 'FAIL':>9}")
print(f"\nDD constraint anchors: 5th-pct MaxDD at x=0 = {D5[0]*100:.2f}%  "
      f"=> floors: 1.5pp {FLOOR[1.5]*100:.2f}% | 2.0pp {FLOOR[2.0]*100:.2f}% | 3.0pp {FLOOR[3.0]*100:.2f}%")

# ---------- (3) DD-threshold sensitivity ----------
print("\n=== (3) DD-threshold sensitivity: which levels pass the gate ===")
passing = {}
for th in (1.5, 2.0, 3.0):
    p = [float(XS[i]) for i in range(12) if D5[i] >= FLOOR[th]]
    passing[th] = p
    print(f"  floor {th:.1f}pp (DD5th >= {FLOOR[th]*100:.2f}%): pass = {p}")

# ---------- selection per PREREG v2 ----------
cand = [i for i in range(12) if ok20[i]]
best = max(cand, key=lambda i: EK[i])
tie = [i for i in cand if abs(EK[i] - EK[best]) < 0.03]
pick = min(tie, key=lambda i: XS[i])
print(f"\n=== PREREG v2 selection ===")
print(f"  candidates passing 2.0pp DD gate: {[float(XS[i]) for i in cand]}")
print(f"  max E[Calmar]: x={XS[best]:.2f} (E[Calmar]={EK[best]:.4f})")
print(f"  within 0.03 E[Calmar] of it: {[float(XS[i]) for i in tie]}  (E[Calmar] {[round(EK[i],4) for i in tie]})")
print(f"  ==> tie-break 'lowest x' PICKS x = {XS[pick]:.2f}")
print(f"  decided by DATA (unique max) ? {'YES' if len(tie)==1 else 'NO — decided by the tie-break rule'}")

# ---------- (4) minimax regret on CAGR, 0-30% ----------
print("\n=== (4) Minimax regret on bootstrap 5th-pct CAGR, restricted to 0-30% ===")
sub = [0,1,2,3]
bestC5 = max(C5[i] for i in sub)
for i in sub:
    print(f"  x={XS[i]:.2f}: CAGR5th {C5[i]*100:6.2f}%   regret vs best {(bestC5-C5[i])*100:5.2f}pp")
mmr = min(sub, key=lambda i: bestC5 - C5[i])
print(f"  minimax-regret level (worst-case CAGR) = x {XS[mmr]:.2f}")
# per-path regret version: max over paths of (best_on_subset - x)
reg = C[:, sub].max(axis=1)[:, None] - C[:, sub]
print("  per-path regret (mean / 95th-pct shortfall vs the best 0-30% level on the SAME path):")
for j, i in enumerate(sub):
    print(f"    x={XS[i]:.2f}: mean {reg[:,j].mean()*100:5.2f}pp   95th {np.percentile(reg[:,j],95)*100:5.2f}pp")

# ---------- (2) episode-aware leave-out ----------
print("\n=== (2) Episode-aware leave-out (drop whole calendar years, recompute Calmar rank) ===")
yr = np.array([d.year for d in idx0[1:]])           # year of each return
cases = {"FULL": [], "drop 2019+2020": [2019,2020], "drop 2018": [2018],
         "drop 2018-2020": [2018,2019,2020], "drop 2022": [2022]}
loo = {}
for name, drop in cases.items():
    keep = ~np.isin(yr, drop)
    c, s, d, k = metrics(R[keep])
    order = np.argsort(-k)
    loo[name] = {TAGS[i]: round(float(k[i]), 3) for i in range(12)}
    print(f"\n  {name}  ({keep.sum()} ret days)")
    print("    rank: " + " > ".join(f"{XS[i]:.2f}({k[i]:.2f})" for i in order[:6]) + " ...")
    print(f"    Calmar 0%={k[0]:.3f}  10%={k[1]:.3f}  20%={k[2]:.3f}  30%={k[3]:.3f}  80%={k[9]:.3f}")
    print(f"    argmax overall = x {XS[k.argmax()]:.2f} | argmax within 0-30% = x {XS[np.argmax(k[:4])]:.2f}")

json.dump({"job":"Taylor_20260927_074727","srcs":srcs,"N":int(N),"yrs":round(YRS,4),
           "x":[float(v) for v in XS],
           "calmar_act":[round(float(v),4) for v in ACT[3]],
           "E_calmar":[round(float(v),4) for v in EK],
           "calmar_5th":[round(float(v),4) for v in K5],
           "p_argmax":[round(float(v),4) for v in p_argmax],
           "p_gt_x0":[round(float(v),4) for v in p_gt0],
           "E_maxdd_pct":[round(float(v)*100,2) for v in ED],
           "dd5_pct":[round(float(v)*100,2) for v in D5],
           "E_cagr_pct":[round(float(v)*100,3) for v in EC],
           "cagr5_pct":[round(float(v)*100,3) for v in C5],
           "gate_pass":{str(k):v for k,v in passing.items()},
           "pick":float(XS[pick]),"tie":[float(XS[i]) for i in tie],
           "decided_by":"data" if len(tie)==1 else "tie-break",
           "leave_one_out":loo},
          open(f"{HERE}/paired_v2_results.json","w"), indent=1)
print(f"\nwrote paired_v2_results.json")
