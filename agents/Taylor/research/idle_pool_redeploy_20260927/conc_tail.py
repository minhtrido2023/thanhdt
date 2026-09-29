#!/usr/bin/env python3
"""c1 (CONCENTRATED sleeve, k=4-6 names) vs c2 (BROAD basket, k=30) — tail-DD cost of
concentration, measured WITHOUT name-picking hindsight.

Design: at each universe_pit_q quarterly date, draw k names at random from the SAME PIT-eligible
pool custom30V draws from (in_universe & pass_golden_floor & rating_8l<=3 & not banned), hold EW
until the next quarterly date, adjusted Close. R random draws per k => a DISTRIBUTION over
"which k names you happened to pick". The 5th-pct-across-draws MaxDD is the honest tail for a
sleeve whose names you cannot know in advance; using the 4 names AlphaLens actually picked would
be hindsight and is NOT what a forward sizing decision faces.

Then inject each sleeve into the pinned park=0.30 leg at w of NAV, funded from idle cash (so the
sleeve return replaces the cash carry), and re-run the SAME paired block bootstrap as
park_fraction_grid_20260927/paired_v2.py.
"""
import glob, json, numpy as np, pandas as pd

WC = "/home/trido/thanhdt/WorkingClaude"
KS = [4, 6, 30]
R = 300
SEED = 20260927
L, B, BSEED = 21, 4000, 12345
CARRY = 0.0855
W_SLEEVE = 0.10

# ---- PIT eligible pool per quarter ----
up = pd.concat([pd.read_parquet(f) for f in sorted(glob.glob(f"{WC}/data/bq_cache/universe_pit_q/*.parquet"))])
up["time"] = pd.to_datetime(up["time"])
elig = up[(up["in_universe"] == True) & (up["pass_golden_floor"] == True)
          & (up["banned"] != True) & (up["rating_8l"] <= 3)]
pool = {d: sorted(g["ticker"].unique()) for d, g in elig.groupby("time")}
qdates = sorted([d for d in pool if len(pool[d]) >= 35])
print(f"universe_pit_q: {len(pool)} quarter dates, {len(qdates)} with >=35 eligible names; "
      f"{qdates[0].date()}..{qdates[-1].date()}  pool size med={int(np.median([len(pool[d]) for d in qdates]))}")

# ---- prices ----
px = pd.concat([pd.read_parquet(f, columns=["time", "ticker", "Close"])
                for f in sorted(glob.glob(f"{WC}/data/bq_cache/ticker/*.parquet"))])
px["time"] = pd.to_datetime(px["time"])
W = px.pivot_table(index="time", columns="ticker", values="Close", aggfunc="last").sort_index()
RET = W.pct_change()
print(f"price panel: {W.shape[0]} days x {W.shape[1]} tickers  {W.index[0].date()}..{W.index[-1].date()}")

# ---- align to the pinned leg's calendar ----
leg = sorted(glob.glob(f"{WC}/data/*_parkgrid_030_univpit.csv"))
assert len(leg) == 1
df = pd.read_csv(leg[0], low_memory=False).dropna(subset=["combined_nav"])
t = pd.to_datetime(df["ymd"], errors="coerce"); df = df[t.notna()]; t = t[t.notna()]
g = df.groupby(t.dt.normalize()).last()
NAV = g["combined_nav"].astype(float)
CASH = g[["bal_cash_ref", "lag_cash_ref"]].fillna(0).sum(axis=1).astype(float)
IDX = NAV.index
RET = RET.reindex(IDX)
N = len(IDX) - 1
YRS = (IDX[-1] - IDX[0]).days / 365.25
ANN = N / YRS

seg = []   # (start_pos, end_pos, qdate) over IDX[1:]
for i, d in enumerate(qdates):
    nxt = qdates[i + 1] if i + 1 < len(qdates) else IDX[-1] + pd.Timedelta(days=1)
    m = (IDX[1:] > d) & (IDX[1:] <= nxt)
    if m.sum(): seg.append((m, d))
print(f"{len(seg)} holding segments cover {sum(int(m.sum()) for m,_ in seg)}/{N} return days")

rng = np.random.default_rng(SEED)
TIC = {t: i for i, t in enumerate(RET.columns)}
RM = RET.iloc[1:].to_numpy(dtype=float)        # (N, T) aligned to IDX[1:]
res = {}
for k in KS:
    S = np.zeros((R, N))
    for m, d in seg:
        names = [n for n in pool[d] if n in TIC]
        if len(names) < k: continue
        ci = np.array([TIC[n] for n in names])
        rows = np.where(m)[0]
        picks = np.array([rng.choice(ci, size=k, replace=False) for _ in range(R)])   # (R,k)
        X = RM[np.ix_(rows, picks.ravel())].reshape(len(rows), R, k)
        with np.errstate(invalid="ignore"):
            seg_ret = np.nanmean(X, axis=2)
        S[:, rows] = np.nan_to_num(seg_ret).T
    nav = np.cumprod(1 + S, axis=1)
    peak = np.maximum.accumulate(nav, axis=1)
    dd = (nav / peak - 1).min(axis=1)
    cagr = nav[:, -1] ** (1 / YRS) - 1
    res[k] = {"S": S, "dd": dd, "cagr": cagr}
    print(f"\nk={k:2d} standalone EW sleeve, {R} random PIT draws, quarterly reshuffle:", flush=True)
    print(f"   CAGR  median {np.median(cagr)*100:6.2f}%  5th {np.percentile(cagr,5)*100:6.2f}%  95th {np.percentile(cagr,95)*100:6.2f}%")
    print(f"   MaxDD median {np.median(dd)*100:6.1f}%  5th(worst tail) {np.percentile(dd,5)*100:6.1f}%  95th {np.percentile(dd,95)*100:6.1f}%")
    print(f"   cross-draw SD of MaxDD = {dd.std()*100:.2f}pp   SD of CAGR = {cagr.std()*100:.2f}pp")

# ---- inject into park=0.30 leg, funded from cash, paired bootstrap ----
def metrics(r):
    nav = np.exp(np.cumsum(r, axis=0)); peak = np.maximum.accumulate(nav, axis=0)
    yrs = r.shape[0] / ANN
    cagr = nav[-1] ** (1 / yrs) - 1
    dd = (nav / peak - 1).min(axis=0)
    return cagr, dd, cagr / np.abs(dd)

def boot(Rm):
    rng2 = np.random.default_rng(BSEED); nblk = int(np.ceil(N / L)); off = np.arange(L)
    C = np.empty((B, Rm.shape[1])); D = np.empty((B, Rm.shape[1])); K = np.empty((B, Rm.shape[1]))
    for b in range(B):
        st = rng2.integers(0, N, nblk)
        ix = ((st[:, None] + off[None, :]) % N).ravel()[:N]
        C[b], D[b], K[b] = metrics(Rm[ix])
    return C, D, K

dts = np.array([(IDX[i + 1] - IDX[i]).days for i in range(N)], float)
carry_ret = (np.maximum(CASH.values[:-1], 0.0) / NAV.values[:-1]) * CARRY * dts / 365.0
cash_share = np.maximum(CASH.values[:-1], 0.0) / NAV.values[:-1]
w_eff = np.minimum(W_SLEEVE, cash_share)          # cannot fund more sleeve than idle cash present
print(f"\nsleeve target w={W_SLEEVE:.0%} of NAV funded from idle cash; days where cash < target = "
      f"{(cash_share < W_SLEEVE).mean()*100:.1f}% (w_eff mean {w_eff.mean():.3f})")

base_log = np.diff(np.log(NAV.values))
cols, labels = [], []
cols.append(base_log + np.log1p(carry_ret)); labels.append("park0.30 + carry (baseline a)")
for k in KS:
    for tag, q in (("median-draw", 50), ("5th-pct-draw", 5)):
        j = int(np.argsort(res[k]["dd"])[int(round((q / 100) * (R - 1)))])
        s = res[k]["S"][j]
        r = base_log + np.log1p(carry_ret + w_eff * (s - CARRY * dts / 365.0))
        cols.append(r); labels.append(f"park0.30 + carry + {W_SLEEVE:.0%} k={k} [{tag}]")
Rm = np.column_stack(cols)
ACT = metrics(Rm); C, D, K = boot(Rm)
D5 = np.percentile(D, 5, axis=0); C5 = np.percentile(C, 5, axis=0); EK = K.mean(axis=0)
print(f"\n=== injected into park=0.30, paired block bootstrap L=21 B=4000 seed=12345 ===")
print(f"{'config':<44} {'CAGRact':>8} {'Calmar':>7} {'E[Calmar]':>9} {'DD5th':>7} {'CAGR5th':>8}")
outrows = []
for i, lab in enumerate(labels):
    print(f"{lab:<44} {ACT[0][i]*100:7.2f}% {ACT[2][i]:7.3f} {EK[i]:9.3f} {D5[i]*100:6.1f}% {C5[i]*100:7.2f}%")
    outrows.append({"config": lab, "cagr_act_pct": round(float(ACT[0][i]) * 100, 3),
                    "calmar_act": round(float(ACT[2][i]), 4), "E_calmar": round(float(EK[i]), 4),
                    "dd5_pct": round(float(D5[i]) * 100, 2), "cagr5_pct": round(float(C5[i]) * 100, 3)})
print("\nreference (same bootstrap, carry run): park0.80+carry DD5th -30.02% CAGRact 28.05%")
json.dump({"job": "Taylor_20260927_085628", "R": R, "KS": KS, "w_sleeve": W_SLEEVE,
           "carry": CARRY, "n_quarters": len(seg), "N": int(N), "yrs": round(YRS, 4),
           "standalone": {str(k): {"cagr_med_pct": round(float(np.median(res[k]['cagr'])) * 100, 3),
                                   "cagr_5th_pct": round(float(np.percentile(res[k]['cagr'], 5)) * 100, 3),
                                   "dd_med_pct": round(float(np.median(res[k]['dd'])) * 100, 2),
                                   "dd_5th_pct": round(float(np.percentile(res[k]['dd'], 5)) * 100, 2),
                                   "dd_sd_pp": round(float(res[k]['dd'].std()) * 100, 2),
                                   "cagr_sd_pp": round(float(res[k]['cagr'].std()) * 100, 2)} for k in KS},
           "injected": outrows}, open("conc_tail_results.json", "w"), indent=1)
print("wrote conc_tail_results.json")
