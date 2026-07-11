#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""momdeal Phase 1 — pure statistical contrast (no tuning, no harness runs).

Job Taylor_20260711_225135 (plan_momentum_deals_20260711.md §5 Phase 1, CP1 gate §6).
Pre-registered test ledger: 13 univariate tests (FDR-BH 10%) + 1 multivariate check
(logistic L2, fixed defaults, walk-forward by year). Nothing else is tested.

Inputs (read-only, built at CP0):
  data/momdeal_exp/momdeal_episodes_phase0.csv   L2 unit (episodes)
  data/momdeal_exp/momdeal_deals_phase0.csv      L1 unit (book round-trips)
  data/ba_v11_unified_12y_sig.pkl.bak_predt5g_20260711  (independent N recount only)

Outputs -> data/momdeal_exp/ (guidelines §8):
  phase1_report.txt, phase1_feature_table.csv

quant-skeptic Phase-0 verify addenda applied here:
  (1) IS-era (2014-19) per-cell n reported for EVERY feature — no "stable IS/OOS" claim
      may lean on the post-2020 mass alone.
  (2) independent recount of episode N on the untouched backup pkl, code path separate
      from momdeal_phase0_build.episodes_from (plain python loop, no groupby machinery).
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, pickle
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
from scipy import stats

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
OUT = "data/momdeal_exp"
PKL_BAK = "data/ba_v11_unified_12y_sig.pkl.bak_predt5g_20260711"

rep = []
def R(s=""):
    print(s); rep.append(s)

# ---- pre-registered feature list (§4) — mapping to phase0 CSV columns
NUM_FEATS = [  # (id, column, theory-direction-free label)
    ("F1", "rating",             "8L rating 1-5 (as-of PIT)"),
    ("F3", "ROIC_Trailing",      "ROIC trailing 4Q"),
    ("F4", "F4_cfoa_pos",        "CF_OA_P0 > 0 (binary)"),
    ("F5", "Revenue_YoY_P0",     "Revenue YoY P0"),
    ("T1", "ta",                 "ta score at entry"),
    ("T2", "D_RSI",              "D_RSI at entry"),
    ("T3", "T3_vol_ratio",       "Volume / Volume_3M_P50"),
    ("T4", "C_L1M",              "Close vs 1M low"),
    ("T5", "T5_close_res",       "Close / Res_1Y"),
    ("C1", "C1_log_tv",          "log10 Trading_Value_1M_P50"),
    ("C2", "state5",             "DT5G state at entry"),
    ("C3", "days_since_release", "days since BCTC release"),
]
CAT_FEAT = ("F2", "route", "8L route (categorical)")  # chi-square + Cramér's V
FDR_Q = 0.10
DELTA_MIN = 0.15

# ---------------------------------------------------------------- helpers
def cliffs_delta(a, b):
    """delta = P(a>b) - P(a<b), via Mann-Whitney U. a=SUCCESS, b=FAIL."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    u = stats.mannwhitneyu(a, b, alternative="two-sided")
    return 2.0 * u.statistic / (len(a) * len(b)) - 1.0, u.pvalue

def bh_fdr(pvals, q=FDR_Q):
    """Benjamini-Hochberg: returns boolean pass array (same order as input)."""
    p = np.asarray(pvals, float)
    n = len(p)
    order = np.argsort(p)
    passed = np.zeros(n, bool)
    thresh = 0
    for rank, idx in enumerate(order, start=1):
        if p[idx] <= q * rank / n:
            thresh = rank
    for rank, idx in enumerate(order, start=1):
        passed[idx] = rank <= thresh
    return passed

def contrast_block(df, tag):
    """Run the 13 univariate tests on one labeled cohort. Returns table df."""
    s_mask, f_mask = df["L2_success"] == 1, df["L2_success"] == 0
    rows = []
    for fid, col, desc in NUM_FEATS:
        a = df.loc[s_mask, col].dropna()
        b = df.loc[f_mask, col].dropna()
        if len(a) < 5 or len(b) < 5:
            rows.append(dict(fid=fid, col=col, desc=desc, n_s=len(a), n_f=len(b),
                             med_s=np.nan, med_f=np.nan, delta=np.nan, p=np.nan))
            continue
        d, p = cliffs_delta(a, b)
        rows.append(dict(fid=fid, col=col, desc=desc, n_s=len(a), n_f=len(b),
                         med_s=a.median(), med_f=b.median(), delta=d, p=p))
    # F2 route: chi-square + Cramér's V
    fid, col, desc = CAT_FEAT
    sub = df[df["L2_success"].isin([0, 1]) & df[col].notna()]
    ct = pd.crosstab(sub[col], sub["L2_success"])
    if ct.shape[0] >= 2 and ct.values.min() >= 0 and ct.sum().min() >= 5:
        chi2, p, dof, _ = stats.chi2_contingency(ct)
        n = ct.values.sum()
        cramv = np.sqrt(chi2 / (n * (min(ct.shape) - 1)))
    else:
        p, cramv = np.nan, np.nan
    rows.append(dict(fid=fid, col=col, desc=desc,
                     n_s=int((sub["L2_success"] == 1).sum()), n_f=int((sub["L2_success"] == 0).sum()),
                     med_s=np.nan, med_f=np.nan, delta=cramv, p=p))  # delta col holds Cramér's V for F2
    t = pd.DataFrame(rows)
    t["fdr_pass"] = bh_fdr(t["p"].fillna(1.0))
    R(f"\n  [{tag}] n labeled = {int(s_mask.sum())} SUCCESS / {int(f_mask.sum())} FAIL")
    R(f"  {'id':<4}{'feature':<20}{'n_s':>6}{'n_f':>6}{'med_S':>10}{'med_F':>10}{'delta':>8}{'p':>11}{'FDR10%':>8}")
    for _, r in t.iterrows():
        ds = f"{r['delta']:+.3f}" if pd.notna(r["delta"]) else "   —"
        ms = f"{r['med_s']:.3f}" if pd.notna(r["med_s"]) else "—"
        mf = f"{r['med_f']:.3f}" if pd.notna(r["med_f"]) else "—"
        ps = f"{r['p']:.2e}" if pd.notna(r["p"]) else "—"
        R(f"  {r['fid']:<4}{r['col']:<20}{r['n_s']:>6}{r['n_f']:>6}{ms:>10}{mf:>10}{ds:>8}{ps:>11}{'PASS' if r['fdr_pass'] else '.':>8}")
    R(f"  (F2 route: delta column = Cramér's V, not Cliff's delta)")
    return t

def era_delta(df, col, is_cat=False):
    """Cliff's delta + n per era for one feature. Eras: IS 2014-19, OOS 2020+, ex-2021."""
    y = pd.to_datetime(df["entry_date"]).dt.year
    out = {}
    for era, mask in [("FULL", y >= 0), ("IS14-19", y <= 2019), ("OOS20+", y >= 2020), ("ex2021", y != 2021)]:
        sub = df[mask]
        a = sub.loc[sub["L2_success"] == 1, col].dropna()
        b = sub.loc[sub["L2_success"] == 0, col].dropna()
        if len(a) < 5 or len(b) < 5:
            out[era] = (np.nan, np.nan, len(a), len(b))
            continue
        if is_cat:
            ct = pd.crosstab(sub.loc[sub[col].notna(), col], sub.loc[sub[col].notna(), "L2_success"])
            if ct.shape[0] < 2:
                out[era] = (np.nan, np.nan, len(a), len(b)); continue
            chi2, p, _, _ = stats.chi2_contingency(ct)
            v = np.sqrt(chi2 / (ct.values.sum() * (min(ct.shape) - 1)))
            out[era] = (v, p, len(a), len(b))
        else:
            d, p = cliffs_delta(a, b)
            out[era] = (d, p, len(a), len(b))
    return out

# ================================================================ [0] independent N recount
R("=" * 96)
R("PHASE 1 — PURE STATISTICAL CONTRAST (job Taylor_20260711_225135)")
R("=" * 96)
R("\n[0] Independent episode-N recount on backup base pkl (skeptic addendum 2)")
R("    code path: plain per-(ticker,play_type) python loop — independent of phase0 groupby builder")
sig = pickle.load(open(PKL_BAK, "rb"))
sig["time"] = pd.to_datetime(sig["time"])
survey = {"MOMENTUM_N": 87, "MOMENTUM_S": 513, "MOMENTUM": 129, "MEGA": 10, "DEEP_VALUE_RECOVERY": 1077}
recount_fail = []
for pt, sv in survey.items():
    n_ep = 0
    sub = sig[sig["play_type"] == pt]
    for tk, g in sub.groupby("ticker"):
        ds = sorted(g["time"].tolist())
        n_ep += 1 + sum(1 for i in range(1, len(ds)) if (ds[i] - ds[i - 1]).days > 7)
    ok = n_ep == sv
    if not ok: recount_fail.append(pt)
    R(f"    {pt:<22} survey={sv:>5}  independent recount={n_ep:>5}  {'EXACT' if ok else 'MISMATCH'}")
R(f"    verdict: {'N reconciliation CLOSED (exact, independent code path)' if not recount_fail else 'MISMATCH: ' + ','.join(recount_fail)}")

# ================================================================ load phase0
ep = pd.read_csv(f"{OUT}/momdeal_episodes_phase0.csv", parse_dates=["entry_date"], low_memory=False)
mom = ep[(ep["cohort"] == "MOM_FAMILY") & ep["L2_success"].isin([0, 1])].copy()
dvr = ep[(ep["cohort"] == "DVR_CONTROL") & ep["L2_success"].isin([0, 1])].copy()
y_mom = mom["entry_date"].dt.year
R(f"\n[load] MOM_FAMILY labeled episodes: {len(mom)} ({int((mom['L2_success']==1).sum())} S / {int((mom['L2_success']==0).sum())} F)")
R(f"       DVR_CONTROL labeled episodes: {len(dvr)} ({int((dvr['L2_success']==1).sum())} S / {int((dvr['L2_success']==0).sum())} F)")
R(f"       MOM per-era: IS14-19 n={int((y_mom<=2019).sum())} | OOS20+ n={int((y_mom>=2020).sum())} | 2021 alone n={int((y_mom==2021).sum())}")

# ================================================================ [A] univariate MOM
R("\n[A] Univariate contrast — MOM_FAMILY (L2: profit_2M >= +10% vs <= 0%) — FDR-BH 10% over 13 tests")
tab_mom = contrast_block(mom, "MOM_FAMILY")

# ================================================================ [B] era stability (ALL features; skeptic addendum 1)
R("\n[B] Era stability — Cliff's delta (or Cramér's V for F2) per era, WITH per-cell n (skeptic addendum 1)")
R(f"  {'id':<4}{'feature':<20}" + "".join(f"{e:>26}" for e in ["FULL", "IS14-19", "OOS20+", "ex2021"]))
era_rows = {}
for fid, col, desc in NUM_FEATS + [CAT_FEAT]:
    is_cat = fid == "F2"
    er = era_delta(mom, col, is_cat=is_cat)
    era_rows[fid] = er
    cells = []
    for e in ["FULL", "IS14-19", "OOS20+", "ex2021"]:
        d, p, ns, nf = er[e]
        cells.append(f"{d:+.3f}(n={ns}/{nf})" if pd.notna(d) else f"THIN(n={ns}/{nf})")
    R(f"  {fid:<4}{col:<20}" + "".join(f"{c:>26}" for c in cells))

# survivor rule (pre-registered CP1 gate): FDR pass AND |delta_FULL|>=0.15 AND same sign IS/OOS/ex2021
R(f"\n  Survivor gate: FDR10% PASS  AND  |delta FULL| >= {DELTA_MIN}  AND  sign(delta) identical in IS14-19, OOS20+, ex2021")
R(f"  (F2 categorical: Cramér's V has no sign — sign-stability gate not applicable; treated as NOT survivor-eligible")
R(f"   for a directional rule, reported for information only.)")
survivors, near_miss = [], []
for _, r in tab_mom.iterrows():
    fid = r["fid"]
    if fid == "F2":
        continue
    er = era_rows[fid]
    d_full, d_is, d_oos, d_ex = er["FULL"][0], er["IS14-19"][0], er["OOS20+"][0], er["ex2021"][0]
    if not r["fdr_pass"] or pd.isna(d_full):
        continue
    signs_ok = pd.notna(d_is) and pd.notna(d_oos) and pd.notna(d_ex) and \
               (np.sign(d_is) == np.sign(d_full)) and (np.sign(d_oos) == np.sign(d_full)) and (np.sign(d_ex) == np.sign(d_full))
    big = abs(d_full) >= DELTA_MIN
    if signs_ok and big:
        survivors.append(fid)
    elif r["fdr_pass"]:
        why = []
        if not big: why.append(f"|delta|={abs(d_full):.3f}<{DELTA_MIN}")
        if not signs_ok: why.append("sign flips/thin across eras")
        near_miss.append((fid, "; ".join(why)))
for fid, why in near_miss:
    R(f"  near-miss {fid}: FDR PASS but {why}")
R(f"  SURVIVORS (full CP1 gate): {survivors if survivors else 'NONE'}")

# ================================================================ [C] multivariate check — logistic walk-forward
R("\n[C] Multivariate check — logistic L2 (fixed: C=1.0, lbfgs, max_iter=1000, median-impute, z-score),")
R("    walk-forward by entry year (train = all years < y). NO hyperparameter tuning.")
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

num_cols = [c for _, c, _ in NUM_FEATS]
mom_ml = mom.copy()
mom_ml["route_f"] = mom_ml["route"].fillna("NA")
route_dummies = pd.get_dummies(mom_ml["route_f"], prefix="rt")
X_all = pd.concat([mom_ml[num_cols].astype(float), route_dummies], axis=1)
y_all = mom_ml["L2_success"].astype(int).values
yr_all = mom_ml["entry_date"].dt.year.values

aucs = []
R(f"  {'year':>6}{'n_train':>9}{'n_test':>8}{'S/F test':>10}{'AUC':>8}")
for yr in sorted(np.unique(yr_all)):
    tr, te = yr_all < yr, yr_all == yr
    if tr.sum() < 100 or te.sum() < 10:
        continue
    yte = y_all[te]
    if len(np.unique(yte)) < 2 or min((yte == 1).sum(), (yte == 0).sum()) < 5:
        continue
    Xtr, Xte = X_all[tr].copy(), X_all[te].copy()
    med = Xtr.median(numeric_only=True)
    Xtr, Xte = Xtr.fillna(med), Xte.fillna(med)
    mu, sd = Xtr.mean(), Xtr.std().replace(0, 1.0)
    Xtr, Xte = (Xtr - mu) / sd, (Xte - mu) / sd
    clf = LogisticRegression(penalty="l2", C=1.0, solver="lbfgs", max_iter=1000)
    clf.fit(Xtr.values, y_all[tr])
    auc = roc_auc_score(yte, clf.predict_proba(Xte.values)[:, 1])
    aucs.append((yr, auc, int(tr.sum()), int(te.sum())))
    R(f"  {yr:>6}{tr.sum():>9}{te.sum():>8}{f'{(yte==1).sum()}/{(yte==0).sum()}':>10}{auc:>8.3f}")
if aucs:
    av = np.array([a for _, a, _, _ in aucs])
    R(f"  mean AUC = {av.mean():.3f} | std = {av.std():.3f} | years>0.5: {(av>0.5).sum()}/{len(av)} | min {av.min():.3f} max {av.max():.3f}")
else:
    R("  no year met minimum-n requirements — walk-forward not computable")

# ================================================================ [D] control cohort — DVR (L2)
R("\n[D] Control cohort — DVR_CONTROL, same 13 tests + own FDR-BH 10%")
tab_dvr = contrast_block(dvr, "DVR_CONTROL")
R("\n  MOM vs DVR separation pattern (structural info = separates in MOM only; common filter = both):")
R(f"  {'id':<4}{'MOM delta':>11}{'MOM FDR':>9}{'DVR delta':>11}{'DVR FDR':>9}{'  reading'}")
for fid in [f for f, _, _ in NUM_FEATS] + ["F2"]:
    rm = tab_mom[tab_mom["fid"] == fid].iloc[0]
    rd = tab_dvr[tab_dvr["fid"] == fid].iloc[0]
    both = rm["fdr_pass"] and rd["fdr_pass"]
    momonly = rm["fdr_pass"] and not rd["fdr_pass"]
    dvronly = rd["fdr_pass"] and not rm["fdr_pass"]
    same_sign = pd.notna(rm["delta"]) and pd.notna(rd["delta"]) and np.sign(rm["delta"]) == np.sign(rd["delta"])
    if both:
        reading = "COMMON filter (golden-floor candidate)" if same_sign or fid == "F2" else "both sig, OPPOSITE sign"
    elif momonly: reading = "MOM-only (structural)"
    elif dvronly: reading = "DVR-only"
    else: reading = "neither"
    dm = f"{rm['delta']:+.3f}" if pd.notna(rm["delta"]) else "—"
    dd = f"{rd['delta']:+.3f}" if pd.notna(rd["delta"]) else "—"
    R(f"  {fid:<4}{dm:>11}{'PASS' if rm['fdr_pass'] else '.':>9}{dd:>11}{'PASS' if rd['fdr_pass'] else '.':>9}  {reading}")

# ================================================================ [E] L1 consistency + RE_BACKLOG control
R("\n[E] L1 consistency check (book deals, net_ret >= +10% vs <= 0%) — sign check only, small N")
dl = pd.read_csv(f"{OUT}/momdeal_deals_phase0.csv", parse_dates=["entry_date"], low_memory=False)
dl["L1s"] = np.where(pd.to_numeric(dl["net_ret"]) >= 0.10, 1, np.where(pd.to_numeric(dl["net_ret"]) <= 0.0, 0, np.nan))
MOM_PT = ["MOMENTUM_N", "MOMENTUM_S", "MOMENTUM", "MEGA"]
for tag, sel in [("MOM deals", dl["pt_base"].isin(MOM_PT)), ("RE_BACKLOG deals (2nd control)", dl["pt_base"] == "RE_BACKLOG_BUY")]:
    sub = dl[sel & dl["L1s"].isin([0, 1])]
    ns, nf = int((sub["L1s"] == 1).sum()), int((sub["L1s"] == 0).sum())
    R(f"  {tag}: n = {ns} S / {nf} F")
    for fid, col, _ in NUM_FEATS:
        a = sub.loc[sub["L1s"] == 1, col].dropna(); b = sub.loc[sub["L1s"] == 0, col].dropna()
        if len(a) < 5 or len(b) < 5:
            R(f"    {fid:<4}{col:<20} THIN (n={len(a)}/{len(b)})"); continue
        d, p = cliffs_delta(a, b)
        R(f"    {fid:<4}{col:<20} delta={d:+.3f}  p={p:.3f}  (n={len(a)}/{len(b)})")

# ================================================================ [F] label sensitivity (survivors + near-miss only)
R("\n[F] Label sensitivity — sign of delta under alternative labels (profit_3M; thresholds +7/+15)")
check_ids = survivors + [f for f, _ in near_miss]
cols_by_id = {f: c for f, c, _ in NUM_FEATS}
p2 = pd.to_numeric(ep["profit_2M"]); p3 = pd.to_numeric(ep["profit_3M"])
fam_all = ep["cohort"] == "MOM_FAMILY"
alt_labels = {
    "2M +7/0":  np.where(p2 >= 7.0, 1, np.where(p2 <= 0.0, 0, np.nan)),
    "2M +15/0": np.where(p2 >= 15.0, 1, np.where(p2 <= 0.0, 0, np.nan)),
    "3M +10/0": np.where(p3 >= 10.0, 1, np.where(p3 <= 0.0, 0, np.nan)),
}
for fid in check_ids:
    col = cols_by_id[fid]
    parts = []
    for lab, arr in alt_labels.items():
        sub = ep[fam_all & pd.Series(arr, index=ep.index).isin([0, 1])]
        lab_arr = pd.Series(arr, index=ep.index)[sub.index]
        a = sub.loc[lab_arr == 1, col].dropna(); b = sub.loc[lab_arr == 0, col].dropna()
        if len(a) < 5 or len(b) < 5: parts.append(f"{lab}: THIN"); continue
        d, p = cliffs_delta(a, b)
        parts.append(f"{lab}: {d:+.3f} (p={p:.1e})")
    R(f"  {fid:<4}{col:<20} " + " | ".join(parts))

# ================================================================ [G] verdict
R("\n[G] CP1 verdict (gate pre-registered §6 — not relaxed)")
R(f"    condition: >=1 feature FDR10% PASS AND same sign IS/OOS/ex2021 AND |delta|>={DELTA_MIN}")
R(f"    survivors: {survivors if survivors else 'NONE'}")
verdict = "GO" if survivors else "NO-GO"
R(f"    CP1 = {verdict}")

# feature table CSV
tab_mom["cohort"] = "MOM_FAMILY"; tab_dvr["cohort"] = "DVR_CONTROL"
full_tab = pd.concat([tab_mom, tab_dvr])
for fid in era_rows:
    for e in ["IS14-19", "OOS20+", "ex2021"]:
        d, p, ns, nf = era_rows[fid][e]
        full_tab.loc[(full_tab["fid"] == fid) & (full_tab["cohort"] == "MOM_FAMILY"), f"delta_{e}"] = d
        full_tab.loc[(full_tab["fid"] == fid) & (full_tab["cohort"] == "MOM_FAMILY"), f"n_{e}"] = f"{ns}/{nf}"
full_tab.to_csv(f"{OUT}/phase1_feature_table.csv", index=False)
open(f"{OUT}/phase1_report.txt", "w").write("\n".join(rep) + "\n")
print(f"\nwrote {OUT}/phase1_feature_table.csv, {OUT}/phase1_report.txt")
