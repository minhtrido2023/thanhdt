"""Buoc 0: xac nhan tien de correlation-cluster xuyen-ICB.
Khong backtest, khong forward return. Chi tinh correlation structure PIT.
"""
import numpy as np
import pandas as pd

np.random.seed(42)

panel = pd.read_csv("panel.csv", parse_dates=["time"])
icb = pd.read_csv("icb_map.csv")
mktcap = pd.read_csv("mktcap.csv")

wide = panel.pivot(index="time", columns="ticker", values="Close").sort_index()
# require enough history: drop tickers with <100 non-null obs in full sample
counts = wide.notna().sum()
wide = wide.loc[:, counts[counts >= 100].index]

ret = np.log(wide / wide.shift(1))

n_days_full = len(ret)
last252 = ret.tail(252)

print(f"[scope] full sample: {ret.index.min().date()} -> {ret.index.max().date()}, "
      f"{n_days_full} trading days, {ret.shape[1]} tickers with >=100 obs")
print(f"[scope] recent window: {last252.index.min().date()} -> {last252.index.max().date()}, "
      f"{len(last252)} trading days")

icb_map = dict(zip(icb.ticker, icb.icb_code_lv1))
cap_map = dict(zip(mktcap.ticker, mktcap.mktcap))


def pair_corr(ret_df, t1, t2, min_obs=60):
    sub = ret_df[[t1, t2]].dropna()
    if len(sub) < min_obs:
        return np.nan, len(sub)
    return sub[t1].corr(sub[t2]), len(sub)


def group_avg_corr(ret_df, tickers, min_obs=60):
    vals = []
    tickers = [t for t in tickers if t in ret_df.columns]
    for i in range(len(tickers)):
        for j in range(i + 1, len(tickers)):
            c, n = pair_corr(ret_df, tickers[i], tickers[j], min_obs)
            if not np.isnan(c):
                vals.append(c)
    return (np.mean(vals) if vals else np.nan), len(vals)


# ---------- STEP 1: known-good groups vs baselines ----------
vin = ["VIC", "VHM", "VRE"]
msn = ["MSN", "MCH", "MML", "MSR"]
viettel = ["CTR", "VGI", "VTP"]
pvn = ["BSR", "GAS", "OIL", "PLX", "PVB", "PVC", "PVD", "PVS", "PVT"]

results = {}
for label, tickers in [("Vingroup(VIC/VHM/VRE)", vin), ("Masan(MSN/MCH/MML/MSR)", msn),
                        ("Viettel(CTR/VGI/VTP, tu step2)", viettel),
                        ("PVN(BSR/GAS/OIL/PLX/PVB/PVC/PVD/PVS/PVT, tu step2)", pvn)]:
    full_c, full_n = group_avg_corr(ret, tickers)
    recent_c, recent_n = group_avg_corr(last252, tickers)
    results[label] = dict(full=full_c, full_npairs=full_n, recent=recent_c, recent_npairs=recent_n)
    print(f"[known-good] {label}: full-sample avg pairwise corr={full_c:.3f} (n_pairs={full_n}), "
          f"last252d avg corr={recent_c:.3f} (n_pairs={recent_n})")

# (a) baseline: same-ICB-lv1-sector average pairwise corr (excluding the known-good tickers themselves,
# to not contaminate baseline with the very effect being tested)
kg_all = set(vin + msn + viettel + pvn)


def same_sector_baseline(ret_df, icb_code, exclude=kg_all, min_obs=60, max_pairs=4000):
    members = [t for t, c in icb_map.items() if c == icb_code and t in ret_df.columns and t not in exclude]
    vals = []
    pairs = [(members[i], members[j]) for i in range(len(members)) for j in range(i + 1, len(members))]
    if len(pairs) > max_pairs:
        idx = np.random.choice(len(pairs), max_pairs, replace=False)
        pairs = [pairs[k] for k in idx]
    for t1, t2 in pairs:
        c, n = pair_corr(ret_df, t1, t2, min_obs)
        if not np.isnan(c):
            vals.append(c)
    return (np.mean(vals) if vals else np.nan), np.std(vals) if vals else np.nan, len(vals), len(members)


for label, icb_code in [("Real estate ICB=8600 (Vingroup's own sector)", 8600),
                         ("Consumer ICB=3000 (Masan's own sector, ex MSR)", 3000)]:
    m, s, n, nmem = same_sector_baseline(ret, icb_code)
    mr, sr, nr, _ = same_sector_baseline(last252, icb_code)
    print(f"[baseline-a same-ICB] {label}: n_members={nmem}, full-sample avg corr={m:.3f} (sd={s:.3f}, n_pairs={n}), "
          f"last252d avg corr={mr:.3f} (n_pairs={nr})")

# (b) control: random pairs, market-cap matched (log mktcap within +-0.5 of target ticker's log mktcap)
cap_series = pd.Series(cap_map).dropna()
log_cap = np.log(cap_series)


def cap_matched_random_pairs(ret_df, target_tickers, n_draw=2000, band=0.5, min_obs=60, exclude=kg_all):
    vals = []
    universe = [t for t in ret_df.columns if t in log_cap.index and t not in exclude]
    rng = np.random.default_rng(7)
    tries = 0
    while len(vals) < n_draw and tries < n_draw * 50:
        tries += 1
        a, b = rng.choice(universe, 2, replace=False)
        if abs(log_cap[a] - log_cap[b]) > band:
            continue
        c, n = pair_corr(ret_df, a, b, min_obs)
        if not np.isnan(c):
            vals.append(c)
    return np.array(vals)


ctrl_full = cap_matched_random_pairs(ret, kg_all)
ctrl_recent = cap_matched_random_pairs(last252, kg_all)
mc, sc, nc = ctrl_full.mean(), ctrl_full.std(), len(ctrl_full)
mcr, scr, ncr = ctrl_recent.mean(), ctrl_recent.std(), len(ctrl_recent)
print(f"[baseline-b cap-matched random] full-sample avg corr={mc:.3f} (sd={sc:.3f}, n_pairs={nc}), "
      f"last252d avg corr={mcr:.3f} (sd={scr:.3f}, n_pairs={ncr})")

for label, tickers in [("Vingroup", vin), ("Masan", msn), ("Viettel", viettel), ("PVN", pvn)]:
    gf, _ = group_avg_corr(ret, tickers)
    gr, _ = group_avg_corr(last252, tickers)
    pf = (ctrl_full < gf).mean() * 100
    pr = (ctrl_recent < gr).mean() * 100
    zf = (gf - mc) / sc
    zr = (gr - mcr) / scr
    print(f"[percentile-vs-cap-matched-control] {label}: full-sample corr={gf:.3f} is at "
          f"p{pf:.1f} of control dist (z={zf:+.2f}); recent252d corr={gr:.3f} is at p{pr:.1f} (z={zr:+.2f})")

with open("step1_summary.txt", "w") as f:
    f.write(f"known_good={results}\n")
    f.write(f"cap_matched_control full mean={mc:.4f} sd={sc:.4f} n={nc}; recent mean={mcr:.4f} n={ncr}\n")

print("\n[STEP1 DONE] -> step1_summary.txt")
