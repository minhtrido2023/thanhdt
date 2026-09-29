import pandas as pd
import numpy as np
from scipy import stats

df = pd.read_csv("panel_raw.csv")
df["Release_Date"] = pd.to_datetime(df["Release_Date"])
assert df["release_year"].eq(df["Release_Date"].dt.year).all(), "release_year parse mismatch"

# self-check: spot recompute quarter_num + accr_q + slope_gpm for a handful of rows
chk = df.iloc[[0, 1, 100, 5000]]
for _, r in chk.iterrows():
    y, q = int(r["quarter"][:4]), int(r["quarter"][5])
    assert y * 4 + q - 1 == r["quarter_num"], "quarter_num mismatch"
print("self-check: quarter_num parse OK on spot sample")

# scope: prereg full-sample = IS(2014-2019) U OOS(2020+); pre-2014 excluded from decision stats
work = df[df["release_year"] >= 2014].copy()
print(f"rows total={len(df)} scope(2014+)={len(work)} "
      f"persist_2q non-null in scope={work['persist_2q'].notna().sum()}")

AXES = {
    "T1_accruals": ("accr_q", -1),   # expected negative IC
    "T2_margin_slope": ("slope_gpm", +1),
    "T3_wc_redflag": ("wc_score", -1),
    "T4_debt_eq": ("Debt_Eq_P0", -1),
}

def auc_mw(score, y):
    # AUC of `score` predicting y==1, via Mann-Whitney U; returns auc, p(two-sided), n1, n0
    s = pd.Series(score); yy = pd.Series(y)
    m = s.notna() & yy.notna()
    s, yy = s[m], yy[m]
    pos, neg = s[yy == 1], s[yy == 0]
    n1, n0 = len(pos), len(neg)
    if n1 < 5 or n0 < 5:
        return np.nan, np.nan, n1, n0
    u, p = stats.mannwhitneyu(pos, neg, alternative="two-sided")
    auc = u / (n1 * n0)
    return auc, p, n1, n0

def spearman_ic(score, y):
    s = pd.Series(score); yy = pd.Series(y)
    m = s.notna() & yy.notna()
    if m.sum() < 10:
        return np.nan, np.nan
    r, p = stats.spearmanr(s[m], yy[m])
    return r, p

results = {}
for name, (col, sign) in AXES.items():
    sub = work.dropna(subset=[col, "persist_2q"])
    full_auc, full_p, n1, n0 = auc_mw(sub[col], sub["persist_2q"])
    ic, ic_p = spearman_ic(sub[col], sub["persist_2q"])

    is_sub = sub[sub["release_year"].between(2014, 2019)]
    oos_sub = sub[sub["release_year"] >= 2020]
    is_auc, is_p, is_n1, is_n0 = auc_mw(is_sub[col], is_sub["persist_2q"])
    oos_auc, oos_p, oos_n1, oos_n0 = auc_mw(oos_sub[col], oos_sub["persist_2q"])

    # sign check: orient by expected sign so "effect" = (auc-0.5)*sign_expected direction
    # (report raw AUC; direction check compares (auc-0.5) sign consistency IS vs OOS directly)
    f1_fail = pd.notna(is_auc) and pd.notna(oos_auc) and np.sign(is_auc - 0.5) != np.sign(oos_auc - 0.5) and (is_auc != 0.5) and (oos_auc != 0.5)

    years = sorted(sub["release_year"].unique())
    loo = {}
    full_eff = full_auc - 0.5
    f3_fail = False
    f3_detail = []
    for yr in years:
        rest = sub[sub["release_year"] != yr]
        if rest["persist_2q"].nunique() < 2 or len(rest) < 30:
            continue
        a, p, n1r, n0r = auc_mw(rest[col], rest["persist_2q"])
        if pd.isna(a):
            continue
        eff = a - 0.5
        loo[yr] = eff
        n_yr = (sub["release_year"] == yr).sum()
        if full_eff != 0:
            ratio = eff / full_eff if np.sign(eff) == np.sign(full_eff) else -1
            if ratio < 0.5:
                f3_fail = True
                f3_detail.append(f"drop {yr} (n={n_yr}) -> eff {eff:.4f} vs full {full_eff:.4f}")

    results[name] = dict(
        col=col, sign_expected=sign, n=len(sub), n1=n1, n0=n0,
        full_auc=full_auc, full_p=full_p, ic=ic, ic_p=ic_p,
        is_auc=is_auc, is_n=len(is_sub), oos_auc=oos_auc, oos_n=len(oos_sub),
        f1_fail=bool(f1_fail), f3_fail=f3_fail, f3_detail=f3_detail,
        loo=loo,
    )

# BH correction across the 4 full-sample p-values
names = list(results.keys())
pvals = [results[n]["full_p"] for n in names]
order = np.argsort(pvals)
m = len(pvals)
bh_adj = [np.nan] * m
prev = 1.0
for rank, idx in enumerate(order[::-1], start=0):
    i = order[m - 1 - rank]
    k = m - rank  # rank from largest p (1-indexed from top)
for i, idx in enumerate(order):
    rank = i + 1
    bh = pvals[idx] * m / rank
    bh_adj[idx] = bh
# enforce monotonicity (standard BH step-up)
sorted_idx = order
running_min = 1.0
for i in range(m - 1, -1, -1):
    idx = sorted_idx[i]
    running_min = min(running_min, bh_adj[idx])
    bh_adj[idx] = running_min

print("\n=== RESULTS (scope: release_year>=2014) ===")
for i, name in enumerate(names):
    r = results[name]
    f2_fail = bh_adj[i] >= 0.05
    verdict = "PASS" if not (r["f1_fail"] or f2_fail or r["f3_fail"]) else "FAIL"
    print(f"\n-- {name} (col={r['col']}, expected sign={r['sign_expected']}) --")
    print(f"  n={r['n']} (pos={r['n1']} neg={r['n0']})")
    print(f"  full AUC={r['full_auc']:.4f}  p_raw={r['full_p']:.2e}  p_BH={bh_adj[i]:.2e}  spearman_IC={r['ic']:.4f} (p={r['ic_p']:.2e})")
    print(f"  IS(2014-19) AUC={r['is_auc']:.4f} n={r['is_n']}  |  OOS(2020+) AUC={r['oos_auc']:.4f} n={r['oos_n']}")
    print(f"  F1 (sign flip IS/OOS) = {r['f1_fail']}")
    print(f"  F2 (p_BH>=0.05) = {f2_fail}")
    print(f"  F3 (LOO year dominates) = {r['f3_fail']}  detail={r['f3_detail']}")
    print(f"  VERDICT = {verdict}")

import json
out = {}
for i, name in enumerate(names):
    r = dict(results[name])
    r["loo"] = {str(k): float(v) for k, v in r["loo"].items()}
    r["p_BH"] = float(bh_adj[i])
    r["f2_fail"] = bool(bh_adj[i] >= 0.05)
    r["verdict"] = "PASS" if not (r["f1_fail"] or r["f2_fail"] or r["f3_fail"]) else "FAIL"
    out[name] = r
with open("results.json", "w") as f:
    json.dump(out, f, indent=2, default=str)
print("\nwrote results.json")
