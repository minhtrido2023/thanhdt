#!/usr/bin/env python3
"""Div growth trajectory -> forward return IC test. Job Taylor_20260821_111228.
Spec khoa truoc o PREREG.md cung thu muc; script chi thuc thi spec do."""
import os
import numpy as np
import pandas as pd
from scipy import stats

D = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(20260821)
N_BOOT = 5000
HI, LO = 0.05, -0.05          # nguong production YIELD_FLOOR_DIV_GROWTH_HI/LO
MIN_XS = 10                   # PREREG §5: bo thang co < 10 ma
BANK_ICB = 8355

df = pd.read_csv(f"{D}/panel.csv", parse_dates=["t"])
df["stable3"] = (df.n0 >= 1) & (df.n1 >= 1) & (df.n2 >= 1)
df["has_cagr"] = df.stable3 & (df.div3 > 0)
df["cagr"] = np.where(df.has_cagr, (df.div0 / df.div3.replace(0, np.nan)) ** (1 / 3) - 1, np.nan)
df["grp"] = np.where(~df.stable3, "NOT_STABLE3",
             np.where(~df.has_cagr, "NO_HISTORY",
              np.where(df.cagr > HI, "GROWING",
               np.where(df.cagr < LO, "DECLINING", "STABLE"))))
df["period"] = np.where(df.t <= pd.Timestamp("2019-12-31"), "IS", "OOS")
df["ym"] = df.t.dt.to_period("M").astype(str)
df.to_csv(f"{D}/panel_enriched.csv", index=False)


def nw_t(x, lag=3):
    """t-stat cua mean(x) voi SE Newey-West (PREREG §5 H1)."""
    x = np.asarray(pd.to_numeric(x, errors="coerce").dropna(), float)
    n = len(x)
    if n < 5:
        return np.nan, np.nan, n
    e = x - x.mean()
    g0 = (e @ e) / n
    v = g0
    for L in range(1, min(lag, n - 1) + 1):
        gL = (e[L:] @ e[:-L]) / n
        v += 2 * (1 - L / (lag + 1)) * gL
    v = max(v, 1e-18)
    se = np.sqrt(v / n)
    return float(x.mean() / se), float(se), n


def ic_table(sub, ycol, label):
    """IC Spearman theo tung cross-section thang, roi gop."""
    rows = []
    for ym, g in sub.groupby("ym"):
        g = g[["cagr", ycol]].dropna()
        if len(g) < MIN_XS or g.cagr.nunique() < 3:
            continue
        r = stats.spearmanr(g.cagr, g[ycol]).statistic
        if np.isfinite(r):
            rows.append(dict(ym=ym, ic=r, n=len(g)))
    icdf = pd.DataFrame(rows)
    if icdf.empty:
        return icdf, dict(scope=label, y=ycol, n_months=0)
    t_nw, se, nm = nw_t(icdf.ic)
    t_naive = float(icdf.ic.mean() / (icdf.ic.std(ddof=1) / np.sqrt(len(icdf))))
    return icdf, dict(scope=label, y=ycol, n_months=nm,
                      mean_ic=float(icdf.ic.mean()), median_ic=float(icdf.ic.median()),
                      pct_ic_pos=100 * float((icdf.ic > 0).mean()),
                      t_nw=t_nw, t_naive=t_naive, se_nw=se,
                      mean_n_per_month=float(icdf.n.mean()))


# ---------------- H1: IC ----------------
base = df[df.has_cagr].copy()
scopes = [
    ("FULL", base),
    ("IS", base[base.period == "IS"]),
    ("OOS", base[base.period == "OOS"]),
    ("EX_REGIME", base[~base.dt5g_state.isin([0, 4])]),
    ("EX_BANK", base[base.icb_code != BANK_ICB]),
]
ic_rows, ic_series = [], []
for name, sub in scopes:
    for ycol in ["bhar60_close", "bhar20_close", "bhar60_price"]:
        icdf, summ = ic_table(sub, ycol, name)
        ic_rows.append(summ)
        if not icdf.empty:
            icdf = icdf.assign(scope=name, y=ycol)
            ic_series.append(icdf)
ic_out = pd.DataFrame(ic_rows)
ic_out.to_csv(f"{D}/results_ic.csv", index=False)
pd.concat(ic_series).to_csv(f"{D}/results_ic_monthly.csv", index=False)

# ---------------- H2: categorical ----------------
def boot_mean_diff(sub, ycol, a, b):
    """Block bootstrap theo thang lich tren HIEU trung binh 2 nhom."""
    d = sub[sub.grp.isin([a, b])][["ym", "grp", ycol]].dropna()
    if d.empty:
        return (np.nan, np.nan)
    g = d.groupby(["ym", "grp"])[ycol].agg(["sum", "count"]).unstack("grp")
    sa = g[("sum", a)].fillna(0).to_numpy(float); ca = g[("count", a)].fillna(0).to_numpy(float)
    sb = g[("sum", b)].fillna(0).to_numpy(float); cb = g[("count", b)].fillna(0).to_numpy(float)
    idx = RNG.integers(0, len(sa), size=(N_BOOT, len(sa)))
    ma = np.where(ca[idx].sum(1) > 0, sa[idx].sum(1) / np.where(ca[idx].sum(1) == 0, np.nan, ca[idx].sum(1)), np.nan)
    mb = np.where(cb[idx].sum(1) > 0, sb[idx].sum(1) / np.where(cb[idx].sum(1) == 0, np.nan, cb[idx].sum(1)), np.nan)
    dd = (ma - mb); dd = dd[np.isfinite(dd)]
    return (float(np.percentile(dd, 2.5)), float(np.percentile(dd, 97.5)))


grp_rows = []
for name, sub in scopes:
    for ycol in ["bhar60_close", "bhar20_close"]:
        for g in ["GROWING", "STABLE", "DECLINING"]:
            x = pd.to_numeric(sub[sub.grp == g][ycol], errors="coerce").dropna()
            grp_rows.append(dict(scope=name, y=ycol, grp=g, n=len(x),
                                 mean=float(x.mean()) if len(x) else np.nan,
                                 median=float(x.median()) if len(x) else np.nan,
                                 pct_neg=100 * float((x < 0).mean()) if len(x) else np.nan))
        a = pd.to_numeric(sub[sub.grp == "GROWING"][ycol], errors="coerce").dropna()
        b = pd.to_numeric(sub[sub.grp == "DECLINING"][ycol], errors="coerce").dropna()
        if len(a) > 2 and len(b) > 2:
            tt = stats.ttest_ind(a, b, equal_var=False)
            lo, hi = boot_mean_diff(sub, ycol, "GROWING", "DECLINING")
            grp_rows.append(dict(scope=name, y=ycol, grp="GROWING-DECLINING",
                                 n=len(a) + len(b), mean=float(a.mean() - b.mean()),
                                 t_welch=float(tt.statistic), p_welch=float(tt.pvalue),
                                 boot_lo=lo, boot_hi=hi))
pd.DataFrame(grp_rows).to_csv(f"{D}/results_groups.csv", index=False)

# ---------------- H3: portfolio relevance ----------------
h3 = []
for name, sub in [("FULL", df), ("IS", df[df.period == "IS"]), ("OOS", df[df.period == "OOS"])]:
    s3 = sub[sub.stable3]
    tot = len(s3)
    for g in ["GROWING", "STABLE", "DECLINING", "NO_HISTORY"]:
        n = int((s3.grp == g).sum())
        h3.append(dict(scope=name, grp=g, n=n, pct_of_stable3=100 * n / tot if tot else np.nan,
                       n_stable3=tot, n_panel=len(sub),
                       pct_stable3_of_panel=100 * tot / len(sub) if len(sub) else np.nan))
h3 = pd.DataFrame(h3)
h3.to_csv(f"{D}/results_h3.csv", index=False)

pd.set_option("display.width", 200, "display.max_columns", 40)
print("=== PANEL ===")
print(f"rows={len(df)}  tickers={df.ticker.nunique()}  months={df.ym.nunique()}  "
      f"{df.t.min().date()} -> {df.t.max().date()}")
print(df.grp.value_counts().to_string())
print("\n=== H1: IC ===")
print(ic_out.round(4).to_string(index=False))
print("\n=== H2: groups ===")
print(pd.DataFrame(grp_rows).round(4).to_string(index=False))
print("\n=== H3 ===")
print(h3.round(2).to_string(index=False))
