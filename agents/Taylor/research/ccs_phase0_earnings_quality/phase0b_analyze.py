"""
Phase 0b: 4 việc bắt buộc trước R3 cho trục T1 accruals (accr_q).
Nguồn: panel_raw.csv (Phase 0, job Taylor_20260905_171403) + sector_liquidity_raw.csv
(query mới, extract_sector_liquidity.sql — ICB_Code + adv_30d self-built từ `ticker`).
Scope quyết định = release_year>=2014, giống prereg/analyze.py gốc.
"""
import json
import numpy as np
import pandas as pd
from scipy import stats

df = pd.read_csv("panel_raw.csv")
df["Release_Date"] = pd.to_datetime(df["Release_Date"])
sl = pd.read_csv("sector_liquidity_raw.csv")
sl["Release_Date"] = pd.to_datetime(sl["Release_Date"])

merged = df.merge(sl[["ticker", "quarter", "ICB_Code", "adv_30d", "n_days_30d"]],
                   on=["ticker", "quarter"], how="left")
assert len(merged) == len(df), "merge changed row count"
work = merged[merged["release_year"] >= 2014].copy()
t1 = work.dropna(subset=["accr_q", "persist_2q"]).copy()
print(f"T1 usable rows (release_year>=2014, accr_q & persist_2q non-null): {len(t1)}")
print(f"T1 ICB_Code coverage: {t1['ICB_Code'].notna().mean():.4f}")
print(f"T1 adv_30d coverage: {t1['adv_30d'].notna().mean():.4f}")

def auc_mw(score, y):
    s = pd.Series(score).reset_index(drop=True)
    yy = pd.Series(y).reset_index(drop=True)
    m = s.notna() & yy.notna()
    s, yy = s[m], yy[m]
    pos, neg = s[yy == 1], s[yy == 0]
    n1, n0 = len(pos), len(neg)
    if n1 < 5 or n0 < 5:
        return np.nan, np.nan, n1, n0
    u, p = stats.mannwhitneyu(pos, neg, alternative="two-sided")
    return u / (n1 * n0), p, n1, n0

results = {}

# ============================================================
# V1 — Floor theo NGÀNH (ICB_Code) vs cutoff tuyệt đối
#   (a) cutoff tuyệt đối hiện tại (IS-P80 = 0.045, đã pin ở Phase 0)
#   (b) percentile TRONG TỪNG NGÀNH (IS per-sector P80, áp OOS)
#   (c) accr_q demean theo ngành rồi cutoff tuyệt đối trên giá trị đã demean (IS P80)
# ============================================================
print("\n" + "=" * 70)
print("V1 — Floor theo ngành vs cutoff tuyệt đối")
print("=" * 70)

t1_is = t1[t1["release_year"].between(2014, 2019)]
t1_oos = t1[t1["release_year"] >= 2020]

# recompute IS P80 exactly from data (Phase 0 report displayed it rounded to "0.0450"; using the
# rounded value instead of the full-precision quantile shifts which rows sit right at the margin)
IS_CUTOFF_ABS = float(t1_is["accr_q"].quantile(0.80))
print(f"  IS P80 cutoff (full precision) = {IS_CUTOFF_ABS:.6f} (Phase-0 report displayed 0.0450)")

v1 = {}


def persist_excl_vs_kept(mask_exclude, sub):
    """Matches the pinned Phase-0 definition: delta = persist_rate(kept) - persist_rate(excluded)."""
    p_excl = sub.loc[mask_exclude, "persist_2q"].mean()
    p_kept = sub.loc[~mask_exclude, "persist_2q"].mean()
    return p_excl, p_kept, mask_exclude.mean()


def golden_floor_overlap(mask_exclude, sub):
    """% of T1-excluded rows that golden floor (ROE_Min3Y>=0 AND CF_OA_3Y>0) already excludes."""
    excl_rows = sub.loc[mask_exclude]
    gf_fail = ~((excl_rows["ROE_Min3Y"] >= 0) & (excl_rows["CF_OA_3Y"] > 0))
    return float(gf_fail.mean())


# (a) absolute cutoff, as pinned — must reproduce 19.8% / 8.15pp exactly before trusting b/c
excl_a = t1_oos["accr_q"] >= IS_CUTOFF_ABS
p_excl_a, p_kept_a, pct_a = persist_excl_vs_kept(excl_a, t1_oos)
v1["a_absolute_cutoff"] = dict(
    is_cutoff=IS_CUTOFF_ABS, oos_excl_pct=float(pct_a),
    oos_persist_excluded=float(p_excl_a), oos_persist_kept=float(p_kept_a),
    delta_pp=float((p_kept_a - p_excl_a) * 100),
    golden_floor_overlap_pct=golden_floor_overlap(excl_a, t1_oos),
)

# (b) per-sector percentile: freeze P80 accr_q WITHIN each ICB_Code on IS, apply per-sector
#     cutoff to OOS rows of the same sector. Sectors with <30 IS obs -> fall back to global
#     IS P80 (can't estimate a stable sector-specific cutoff from too few rows).
sector_cutoff = {}
MIN_IS_N = 30
for icb, grp in t1_is.dropna(subset=["ICB_Code"]).groupby("ICB_Code"):
    if len(grp) >= MIN_IS_N:
        sector_cutoff[icb] = grp["accr_q"].quantile(0.80)
n_sectors_own_cutoff = len(sector_cutoff)
n_sectors_total = t1_is["ICB_Code"].dropna().nunique()

t1_oos_b = t1_oos.dropna(subset=["ICB_Code"]).copy()
t1_oos_b["cutoff_used"] = t1_oos_b["ICB_Code"].map(sector_cutoff).fillna(IS_CUTOFF_ABS)
t1_oos_b["fallback_global"] = ~t1_oos_b["ICB_Code"].isin(sector_cutoff)
excl_b = t1_oos_b["accr_q"] >= t1_oos_b["cutoff_used"]
p_excl_b, p_kept_b, pct_b = persist_excl_vs_kept(excl_b, t1_oos_b)
v1["b_per_sector_percentile"] = dict(
    n_sectors_with_own_cutoff=int(n_sectors_own_cutoff),
    n_sectors_total_IS=int(n_sectors_total),
    pct_oos_rows_using_fallback_global_cutoff=float(t1_oos_b["fallback_global"].mean()),
    oos_excl_pct=float(pct_b),
    oos_persist_excluded=float(p_excl_b), oos_persist_kept=float(p_kept_b),
    delta_pp=float((p_kept_b - p_excl_b) * 100),
    golden_floor_overlap_pct=golden_floor_overlap(excl_b, t1_oos_b),
)

# (c) demean accr_q by sector (IS sector means, applied to OOS same sector; unseen sector -> 0
#     demean, i.e. use raw value), then apply the SAME absolute P80 cutoff (on the demeaned
#     value's IS distribution) to the demeaned OOS values.
sector_mean_is = t1_is.dropna(subset=["ICB_Code"]).groupby("ICB_Code")["accr_q"].mean()
t1_is_c = t1_is.dropna(subset=["ICB_Code"]).copy()
t1_is_c["accr_q_demean"] = t1_is_c["accr_q"] - t1_is_c["ICB_Code"].map(sector_mean_is)
demean_cutoff = t1_is_c["accr_q_demean"].quantile(0.80)

t1_oos_c = t1_oos.dropna(subset=["ICB_Code"]).copy()
t1_oos_c["accr_q_demean"] = t1_oos_c["accr_q"] - t1_oos_c["ICB_Code"].map(sector_mean_is).fillna(0.0)
excl_c = t1_oos_c["accr_q_demean"] >= demean_cutoff
p_excl_c, p_kept_c, pct_c = persist_excl_vs_kept(excl_c, t1_oos_c)
v1["c_sector_demean_then_absolute_cutoff"] = dict(
    is_demean_cutoff=float(demean_cutoff),
    oos_excl_pct=float(pct_c),
    oos_persist_excluded=float(p_excl_c), oos_persist_kept=float(p_kept_c),
    delta_pp=float((p_kept_c - p_excl_c) * 100),
    golden_floor_overlap_pct=golden_floor_overlap(excl_c, t1_oos_c),
)

# AUC comparison too (does sector-adjustment change discriminative power on full sample?)
auc_raw, p_raw, n1_raw, n0_raw = auc_mw(t1["accr_q"], t1["persist_2q"])
sector_mean_full = t1.dropna(subset=["ICB_Code"]).groupby("ICB_Code")["accr_q"].transform("mean")
t1_demean_full = t1.dropna(subset=["ICB_Code"]).copy()
t1_demean_full["accr_q_demean"] = t1_demean_full["accr_q"] - sector_mean_full
auc_demean, p_demean, n1d, n0d = auc_mw(t1_demean_full["accr_q_demean"], t1_demean_full["persist_2q"])
v1["auc_raw_vs_sector_demeaned_full_sample"] = dict(
    auc_raw=float(auc_raw), auc_demean=float(auc_demean),
    dist_raw=float(abs(auc_raw - 0.5)), dist_demean=float(abs(auc_demean - 0.5)),
)

for k, v in v1.items():
    print(f"  {k}: {v}")

results["V1_sector_floor"] = v1

# ============================================================
# V2 — Đối chiếu mã bị floor loại (OOS, absolute cutoff pinned) với thanh khoản (adv_30d)
# ============================================================
print("\n" + "=" * 70)
print("V2 — Liquidity của nhóm bị loại (absolute P80 floor, OOS)")
print("=" * 70)

t1_oos_liq = t1_oos.dropna(subset=["adv_30d"]).copy()
excl_liq = t1_oos_liq["accr_q"] >= IS_CUTOFF_ABS
excluded_grp = t1_oos_liq.loc[excl_liq, "adv_30d"]
kept_grp = t1_oos_liq.loc[~excl_liq, "adv_30d"]

adv_percentiles = [10, 25, 50, 75, 90]
v2 = dict(
    n_excluded=int(len(excluded_grp)), n_kept=int(len(kept_grp)),
    excluded_adv_percentiles={p: float(np.percentile(excluded_grp, p)) for p in adv_percentiles},
    kept_adv_percentiles={p: float(np.percentile(kept_grp, p)) for p in adv_percentiles},
    excluded_median_adv=float(excluded_grp.median()),
    kept_median_adv=float(kept_grp.median()),
)
# MWU on liquidity itself: is excluded-group liquidity distribution lower?
u_liq, p_liq = stats.mannwhitneyu(excluded_grp, kept_grp, alternative="two-sided")
v2["mwu_p_excluded_vs_kept_liquidity"] = float(p_liq)

# what fraction of excluded names fall below common ADV thresholds used elsewhere in this repo
# (CLAUDE.md ticker_prune breadth floor references ~0.5 tỷ/day ADV60 as a liquidity floor)
for thresh_bn in [0.5, 1.0, 2.0]:
    thresh = thresh_bn * 1e9
    frac_excl_below = float((excluded_grp < thresh).mean())
    frac_kept_below = float((kept_grp < thresh).mean())
    v2[f"frac_below_{thresh_bn}bn_excluded"] = frac_excl_below
    v2[f"frac_below_{thresh_bn}bn_kept"] = frac_kept_below

for k, v in v2.items():
    print(f"  {k}: {v}")

results["V2_liquidity_crosscheck"] = v2

# ============================================================
# V3 — Cluster-by-ticker significance (thay p_BH row-level bằng cluster-robust)
# ============================================================
print("\n" + "=" * 70)
print("V3 — Cluster-by-ticker significance test cho T1")
print("=" * 70)

# Row-level (as Phase 0 reported)
auc_row, p_row, n1_row, n0_row = auc_mw(t1["accr_q"], t1["persist_2q"])

# Cluster (block) bootstrap by ticker: resample the 733 UNIQUE TICKERS with replacement (same
# count each draw), reassemble the panel by taking ALL quarterly rows for each drawn ticker
# (a ticker drawn twice contributes its rows twice), recompute AUC on the resampled panel.
# This preserves the original row-level economic question (does this quarter's accrual predict
# the NEXT two quarters' persistence) while correcting the effective-N problem: correlated
# quarters from the same firm no longer count as independent draws. Contrast with the
# collapse-to-ticker-mean below, which is a DIFFERENT (stronger, cross-sectional) question.
rng = np.random.default_rng(20260906)
tickers = t1["ticker"].unique()
n_tickers = len(tickers)
groups = {tk: g[["accr_q", "persist_2q"]].to_numpy() for tk, g in t1.groupby("ticker")}
B = 2000
boot_auc = np.empty(B)
for b in range(B):
    drawn = rng.choice(tickers, size=n_tickers, replace=True)
    rows = np.concatenate([groups[tk] for tk in drawn], axis=0)
    score, y = rows[:, 0], rows[:, 1]
    pos, neg = score[y == 1], score[y == 0]
    if len(pos) < 5 or len(neg) < 5:
        boot_auc[b] = np.nan
        continue
    u, _ = stats.mannwhitneyu(pos, neg, alternative="two-sided")
    boot_auc[b] = u / (len(pos) * len(neg))
boot_auc = boot_auc[~np.isnan(boot_auc)]
boot_se = float(boot_auc.std(ddof=1))
z_cluster = (auc_row - 0.5) / boot_se
p_cluster = float(2 * (1 - stats.norm.cdf(abs(z_cluster))))
ci_lo, ci_hi = float(np.percentile(boot_auc, 2.5)), float(np.percentile(boot_auc, 97.5))

# Secondary diagnostic (NOT the cluster-robust significance test): collapse-to-ticker-mean asks
# a different question (chronic firm-level accrual level vs firm-level average persistence rate)
by_ticker = t1.groupby("ticker").agg(
    accr_q_mean=("accr_q", "mean"), persist_2q_mean=("persist_2q", "mean"),
).reset_index()
ic_tick, ic_p_tick = stats.spearmanr(by_ticker["accr_q_mean"], by_ticker["persist_2q_mean"])

v3 = dict(
    row_level=dict(auc=float(auc_row), p=float(p_row), n1=int(n1_row), n0=int(n0_row),
                    n_total=int(n1_row + n0_row)),
    cluster_bootstrap_by_ticker=dict(
        method="block bootstrap, resample 733 tickers w/ replacement, B=2000, all quarterly "
               "rows travel with the drawn ticker",
        n_tickers=int(n_tickers), n_bootstrap_draws=int(len(boot_auc)),
        point_auc=float(auc_row), boot_se=boot_se, ci95=[ci_lo, ci_hi],
        z=float(z_cluster), p_cluster=p_cluster,
    ),
    secondary_diagnostic_collapse_to_ticker_mean=dict(
        note="DIFFERENT question (chronic firm-level accrual vs avg persistence), not the "
             "cluster-robust significance test — reported for context only",
        n_tickers=int(len(by_ticker)),
        spearman_ic=float(ic_tick), spearman_ic_p=float(ic_p_tick),
    ),
    p_inflation_factor=float(p_cluster / p_row) if p_row > 0 else None,
)
print(f"  row-level: AUC={v3['row_level']['auc']:.4f} p={v3['row_level']['p']:.2e} N={v3['row_level']['n_total']}")
cb = v3["cluster_bootstrap_by_ticker"]
print(f"  cluster-bootstrap (N_tickers={cb['n_tickers']}, B={cb['n_bootstrap_draws']}): "
      f"AUC={cb['point_auc']:.4f} boot_SE={cb['boot_se']:.4f} 95%CI={cb['ci95']} "
      f"z={cb['z']:.3f} p={cb['p_cluster']:.4f}")
sd = v3["secondary_diagnostic_collapse_to_ticker_mean"]
print(f"  [diagnostic only, different question] collapse-to-ticker-mean spearman IC="
      f"{sd['spearman_ic']:.4f} (p={sd['spearman_ic_p']:.2e}), N_tickers={sd['n_tickers']}")

# Second cluster-robust method: ONE randomly-picked quarter per ticker (literal N=733
# independent observations, no within-ticker correlation possible by construction). Repeated
# many times (Monte Carlo over which quarter gets picked) to avoid reporting a single lucky/
# unlucky draw; this is the most likely reading of "cluster-by-ticker (N=733)" in the verify log.
R = 1000
t1_sorted = t1.sort_values("ticker").reset_index(drop=True)
grp_sizes = t1_sorted.groupby("ticker").size().to_numpy()
grp_starts = np.concatenate([[0], np.cumsum(grp_sizes)[:-1]])
accr_arr = t1_sorted["accr_q"].to_numpy()
pers_arr = t1_sorted["persist_2q"].to_numpy()
mc_auc = np.empty(R)
mc_p = np.empty(R)
for r in range(R):
    offsets = rng.integers(0, grp_sizes)  # one random row index within each group
    idx = grp_starts + offsets
    a, p, _, _ = auc_mw(accr_arr[idx], pers_arr[idx])
    mc_auc[r], mc_p[r] = a, p
v3["one_quarter_per_ticker_montecarlo"] = dict(
    method=f"R={R} draws, each draw picks 1 random quarter/ticker -> N=733 literally independent rows",
    auc_median=float(np.median(mc_auc)), auc_iqr=[float(np.percentile(mc_auc, 25)), float(np.percentile(mc_auc, 75))],
    p_median=float(np.median(mc_p)), p_iqr=[float(np.percentile(mc_p, 25)), float(np.percentile(mc_p, 75))],
    frac_draws_p_below_0p05=float((mc_p < 0.05).mean()),
)
mc = v3["one_quarter_per_ticker_montecarlo"]
print(f"  one-quarter-per-ticker MC (R={R}): AUC median={mc['auc_median']:.4f} IQR={mc['auc_iqr']}, "
      f"p median={mc['p_median']:.4f} IQR={mc['p_iqr']}, frac(p<0.05)={mc['frac_draws_p_below_0p05']:.3f}")

results["V3_cluster_by_ticker"] = v3

with open("phase0b_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print("\nwrote phase0b_results.json")
