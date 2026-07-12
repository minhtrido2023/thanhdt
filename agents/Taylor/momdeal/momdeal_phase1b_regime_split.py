#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""momdeal Phase 1b — regime-split contrast: MOM_N vs MOM_S separately.

Job Taylor_20260712_022816 (plan_close_mom_20260712.md §6, pre-registered 2026-07-12).
Re-runs the SAME 13 pre-registered CP1 tests (momdeal_phase1_contrast.py) on two
subsets of the SAME Phase-0 dataset — no rebuild, no new features, no gate change:
  MOM_N = play_type MOMENTUM_N  (fires only in NEUTRAL, state5=3)
  MOM_S = play_type MOMENTUM_S  (fires only in BULL/EXB, state5 in {4,5})

Question: does MOM_S alone show a win/loss-separating feature that was diluted by
pooling with MOM_N in CP1?

Outputs -> data/momdeal_exp/ (guidelines §8):
  phase1b_regime_split_report.txt, phase1b_regime_split_table.csv
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
from scipy import stats

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
OUT = "data/momdeal_exp"

rep = []
def R(s=""):
    print(s); rep.append(s)

# ---- identical pre-registered feature list as CP1 (momdeal_phase1_contrast.py)
NUM_FEATS = [
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
CAT_FEAT = ("F2", "route", "8L route (categorical)")
FDR_Q = 0.10
DELTA_MIN = 0.15

def cliffs_delta(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    u = stats.mannwhitneyu(a, b, alternative="two-sided")
    return 2.0 * u.statistic / (len(a) * len(b)) - 1.0, u.pvalue

def bh_fdr(pvals, q=FDR_Q):
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
    s_mask, f_mask = df["L2_success"] == 1, df["L2_success"] == 0
    rows = []
    for fid, col, desc in NUM_FEATS:
        a = df.loc[s_mask, col].dropna()
        b = df.loc[f_mask, col].dropna()
        if len(a) < 5 or len(b) < 5 or (a.nunique() <= 1 and b.nunique() <= 1):
            rows.append(dict(fid=fid, col=col, desc=desc, n_s=len(a), n_f=len(b),
                             med_s=np.nan, med_f=np.nan, delta=np.nan, p=np.nan))
            continue
        d, p = cliffs_delta(a, b)
        rows.append(dict(fid=fid, col=col, desc=desc, n_s=len(a), n_f=len(b),
                         med_s=a.median(), med_f=b.median(), delta=d, p=p))
    fid, col, desc = CAT_FEAT
    sub = df[df["L2_success"].isin([0, 1]) & df[col].notna()]
    ct = pd.crosstab(sub[col], sub["L2_success"])
    if ct.shape[0] >= 2 and ct.shape[1] == 2 and ct.sum().min() >= 5:
        chi2, p, dof, _ = stats.chi2_contingency(ct)
        n = ct.values.sum()
        cramv = np.sqrt(chi2 / (n * (min(ct.shape) - 1)))
    else:
        p, cramv = np.nan, np.nan
    rows.append(dict(fid=fid, col=col, desc=desc,
                     n_s=int((sub["L2_success"] == 1).sum()), n_f=int((sub["L2_success"] == 0).sum()),
                     med_s=np.nan, med_f=np.nan, delta=cramv, p=p))
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
    return t

def era_delta(df, col, is_cat=False):
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

def survivor_gate(tab, era_rows, tag):
    R(f"\n  Survivor gate [{tag}]: FDR10% PASS AND |delta FULL| >= {DELTA_MIN} AND same sign IS/OOS/ex2021")
    survivors, near_miss = [], []
    for _, r in tab.iterrows():
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
        else:
            why = []
            if not big: why.append(f"|delta|={abs(d_full):.3f}<{DELTA_MIN}")
            if not signs_ok: why.append("sign flips/thin across eras")
            near_miss.append((fid, "; ".join(why)))
    for fid, why in near_miss:
        R(f"  near-miss {fid}: FDR PASS but {why}")
    R(f"  SURVIVORS [{tag}]: {survivors if survivors else 'NONE'}")
    return survivors, near_miss

# ================================================================ load
R("=" * 96)
R("PHASE 1b — REGIME-SPLIT CONTRAST: MOM_N vs MOM_S (job Taylor_20260712_022816)")
R("Same dataset, same 13 tests, same gate as CP1 — only the pooling changes.")
R("=" * 96)
ep = pd.read_csv(f"{OUT}/momdeal_episodes_phase0.csv", parse_dates=["entry_date"], low_memory=False)
fam = ep[(ep["cohort"] == "MOM_FAMILY") & ep["L2_success"].isin([0, 1])].copy()

# sanity: play_type <-> regime consistency (MOM_N should be all state5=3, MOM_S all in {4,5})
for pt, states in [("MOMENTUM_N", {3}), ("MOMENTUM_S", {4, 5})]:
    st = set(fam.loc[fam["play_type"] == pt, "state5"].dropna().astype(int))
    R(f"[sanity] {pt}: state5 observed = {sorted(st)} (expected subset of {sorted(states)}) "
      f"{'OK' if st <= states else '*** VIOLATION ***'}")

results = {}
for tag, sel in [("MOM_N (NEUTRAL-only)", fam["play_type"] == "MOMENTUM_N"),
                 ("MOM_S (BULL/EXB-only)", fam["play_type"] == "MOMENTUM_S")]:
    sub = fam[sel].copy()
    y = sub["entry_date"].dt.year
    R(f"\n{'='*96}\n[{tag}] episodes labeled = {len(sub)} | per-era: IS14-19 n={int((y<=2019).sum())} | "
      f"OOS20+ n={int((y>=2020).sum())} | 2021 alone n={int((y==2021).sum())}")
    # NOTE: C2 state5 is (near-)degenerate within a regime split — reported but expected THIN/NaN.
    tab = contrast_block(sub, tag)
    R(f"\n  Era stability [{tag}] — delta per era WITH per-cell n")
    era_rows = {}
    for fid, col, desc in NUM_FEATS + [CAT_FEAT]:
        er = era_delta(sub, col, is_cat=(fid == "F2"))
        era_rows[fid] = er
        cells = []
        for e in ["FULL", "IS14-19", "OOS20+", "ex2021"]:
            d, p, ns, nf = er[e]
            cells.append(f"{d:+.3f}(n={ns}/{nf})" if pd.notna(d) else f"THIN(n={ns}/{nf})")
        R(f"  {fid:<4}{col:<20}" + "".join(f"{c:>26}" for c in cells))
    surv, nm = survivor_gate(tab, era_rows, tag)
    tab["cohort"] = tag
    for fid in era_rows:
        for e in ["IS14-19", "OOS20+", "ex2021"]:
            d, p, ns, nf = era_rows[fid][e]
            tab.loc[tab["fid"] == fid, f"delta_{e}"] = d
            tab.loc[tab["fid"] == fid, f"n_{e}"] = f"{ns}/{nf}"
    results[tag] = (tab, surv, nm)

# ================================================================ side-by-side + verdict
R(f"\n{'='*96}\n[SUMMARY] side-by-side delta (FULL) — pooled CP1 vs MOM_N vs MOM_S")
tab_n, surv_n, _ = results["MOM_N (NEUTRAL-only)"]
tab_s, surv_s, _ = results["MOM_S (BULL/EXB-only)"]
pooled = pd.read_csv(f"{OUT}/phase1_feature_table.csv")
pooled_mom = pooled[pooled["cohort"] == "MOM_FAMILY"].set_index("fid")
R(f"  {'id':<4}{'feature':<20}{'pooled δ':>10}{'pooled FDR':>11}{'MOM_N δ':>10}{'N FDR':>7}{'MOM_S δ':>10}{'S FDR':>7}")
for fid, col, desc in NUM_FEATS + [CAT_FEAT]:
    rp = pooled_mom.loc[fid] if fid in pooled_mom.index else None
    rn = tab_n[tab_n["fid"] == fid].iloc[0]
    rs = tab_s[tab_s["fid"] == fid].iloc[0]
    f = lambda v: f"{v:+.3f}" if pd.notna(v) else "—"
    fp = lambda b: "PASS" if b else "."
    dp = f(rp["delta"]) if rp is not None else "—"
    pp = fp(bool(rp["fdr_pass"])) if rp is not None else "—"
    R(f"  {fid:<4}{col:<20}{dp:>10}{pp:>11}{f(rn['delta']):>10}{fp(rn['fdr_pass']):>7}{f(rs['delta']):>10}{fp(rs['fdr_pass']):>7}")

R(f"\n[VERDICT Phase 1b]")
R(f"  MOM_N survivors (CP1 gate, un-relaxed): {surv_n if surv_n else 'NONE'}")
R(f"  MOM_S survivors (CP1 gate, un-relaxed): {surv_s if surv_s else 'NONE'}")

full_tab = pd.concat([tab_n, tab_s])
full_tab.to_csv(f"{OUT}/phase1b_regime_split_table.csv", index=False)
open(f"{OUT}/phase1b_regime_split_report.txt", "w").write("\n".join(rep) + "\n")
print(f"\nwrote {OUT}/phase1b_regime_split_table.csv, {OUT}/phase1b_regime_split_report.txt")
