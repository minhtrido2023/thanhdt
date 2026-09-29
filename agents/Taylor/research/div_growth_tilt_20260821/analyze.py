#!/usr/bin/env python3
"""Div-growth CAGR lam TILT LIEN TUC (industry-relative z) -> forward BHAR.
Job Taylor_20260821_113800. Spec khoa truoc o PREREG.md cung thu muc (mike@647c9424);
script CHI thuc thi spec do — moi hang so duoi day deu da khai bao trong prereg."""
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

D = os.path.dirname(os.path.abspath(__file__))
WC = "/home/trido/thanhdt/WorkingClaude"          # tuyet doi: wc_env.sh 'cd' lam relative path hong
sys.path.insert(0, WC)
from deposit_rate_vn import current_deposit_rate   # noqa: E402

SRC = f"{WC}/mike/agents/Taylor/research/div_growth_signal_20260821/panel_enriched.csv"
MIN_PAYERS = 5        # PREREG §2 — nguong payer/o nganh-thang
MIN_XS = 10           # PREREG §3 — bo thang co < 10 quan sat (y het study cha)
NW_LAG = 3
BANK_ICB = 8355       # PREREG §1 — loai khoi moi phan tich co prox

df = pd.read_csv(SRC, parse_dates=["t"])
df["icb_l2"] = (df.icb_code.astype("Int64") // 100).astype("Int64")
df["icb_l1"] = (df.icb_code.astype("Int64") // 1000).astype("Int64")


def nw_t(x, lag=NW_LAG):
    """t-stat cua mean(x) voi SE Newey-West (y het study cha)."""
    x = np.asarray(pd.to_numeric(pd.Series(x), errors="coerce").dropna(), float)
    n = len(x)
    if n < 5:
        return np.nan, n
    e = x - x.mean()
    v = (e @ e) / n
    for L in range(1, min(lag, n - 1) + 1):
        v += 2 * (1 - L / (lag + 1)) * ((e[L:] @ e[:-L]) / n)
    return float(x.mean() / np.sqrt(max(v, 1e-18) / n)), n


def add_industry_z(d, indcol):
    """PREREG §2: z-score cagr trong o (thang x nganh), o < MIN_PAYERS hoac sd==0 => BO o."""
    g = d.groupby(["ym", indcol], dropna=True)["cagr"]
    cnt, mu, sd = g.transform("count"), g.transform("mean"), g.transform(lambda s: s.std(ddof=1))
    ok = (cnt >= MIN_PAYERS) & np.isfinite(sd) & (sd > 0)
    return np.where(ok, (d.cagr - mu) / sd, np.nan), ok


def ic_series(sub, xcol, ycol):
    """Spearman theo tung cross-section thang (gop moi nganh trong thang)."""
    rows = []
    for ym, g in sub.groupby("ym"):
        g = g[[xcol, ycol]].dropna()
        if len(g) < MIN_XS or g[xcol].nunique() < 3:
            continue
        r = stats.spearmanr(g[xcol], g[ycol]).statistic
        if np.isfinite(r):
            rows.append(dict(ym=ym, ic=float(r), n=len(g)))
    return pd.DataFrame(rows)


def ic_summary(sub, xcol, ycol, scope, label):
    s = ic_series(sub, xcol, ycol)
    if s.empty:
        return s, dict(scope=scope, x=label, y=ycol, n_months=0)
    t, nm = nw_t(s.ic)
    return s, dict(scope=scope, x=label, y=ycol, n_months=nm,
                   mean_ic=float(s.ic.mean()), median_ic=float(s.ic.median()),
                   pct_ic_pos=100 * float((s.ic > 0).mean()), t_nw=t,
                   t_naive=float(s.ic.mean() / (s.ic.std(ddof=1) / np.sqrt(len(s)))),
                   mean_n_per_month=float(s.n.mean()))


def partial_spearman(g, x, y, c):
    """PREREG §3 H2(a): partial corr tren HANG (Spearman) cua x,y cho c."""
    g = g[[x, y, c]].dropna()
    if len(g) < MIN_XS or g[x].nunique() < 3 or g[c].nunique() < 3:
        return np.nan, 0
    rxy = stats.spearmanr(g[x], g[y]).statistic
    rxc = stats.spearmanr(g[x], g[c]).statistic
    ryc = stats.spearmanr(g[y], g[c]).statistic
    den = np.sqrt(max(1 - rxc ** 2, 0) * max(1 - ryc ** 2, 0))
    if not np.isfinite(den) or den < 1e-9:
        return np.nan, 0
    return float((rxy - rxc * ryc) / den), len(g)


# ============================ H1 / H1b / H1c ============================
base = df[df.has_cagr].copy()
base["z_l2"], ok_l2 = add_industry_z(base, "icb_l2")
base["z_l1"], ok_l1 = add_industry_z(base, "icb_l1")
sub_l2 = base[base.z_l2.notna()].copy()          # mau con "da loc >=5 payer" dung cho H1 & H1b

# H1c: khu nganh CA HAI VE (chi de dien giai, khong quyet GO/NO-GO)
for ycol in ["bhar60_close", "bhar20_close"]:
    m = sub_l2.groupby(["ym", "icb_l2"])[ycol].transform("mean")
    sub_l2[f"{ycol}_dm"] = sub_l2[ycol] - m

scopes = [("FULL", sub_l2),
          ("IS", sub_l2[sub_l2.period == "IS"]),
          ("OOS", sub_l2[sub_l2.period == "OOS"])]

ic_rows, ic_all = [], []
for scope, s in scopes:
    for xcol, label in [("z_l2", "z_cagr_ind_L2"), ("cagr", "cagr_raw_same_sample")]:
        for ycol in ["bhar60_close", "bhar20_close", "bhar60_price"]:
            ser, summ = ic_summary(s, xcol, ycol, scope, label)
            ic_rows.append(summ)
            if not ser.empty:
                ic_all.append(ser.assign(scope=scope, x=label, y=ycol))
    for ycol in ["bhar60_close", "bhar20_close"]:          # H1c
        ser, summ = ic_summary(s, "z_l2", f"{ycol}_dm", scope, "z_cagr_ind_L2 [H1c both-demeaned]")
        ic_rows.append(summ)
        if not ser.empty:
            ic_all.append(ser.assign(scope=scope, x="z_l2_H1c", y=f"{ycol}_dm"))

# Fallback L1 (PREREG §4) — luon tinh, luon co nhan phu
sub_l1 = base[base.z_l1.notna()].copy()
for scope, s in [("FULL", sub_l1), ("IS", sub_l1[sub_l1.period == "IS"]),
                 ("OOS", sub_l1[sub_l1.period == "OOS"])]:
    ser, summ = ic_summary(s, "z_l1", "bhar60_close", scope, "z_cagr_ind_L1 [fallback]")
    ic_rows.append(summ)
    if not ser.empty:
        ic_all.append(ser.assign(scope=scope, x="z_cagr_ind_L1", y="bhar60_close"))

ic_out = pd.DataFrame(ic_rows)
ic_out.to_csv(f"{D}/results_ic.csv", index=False)
pd.concat(ic_all).to_csv(f"{D}/results_ic_monthly.csv", index=False)

# ================================ H2 ================================
dep = {k: float(current_deposit_rate(k)) for k in sorted(sub_l2.t.dt.date.astype(str).unique())}
h2 = sub_l2.copy()
h2["dep"] = h2.t.dt.date.astype(str).map(dep)
h2["prox"] = np.where((h2.div0 > 0) & (h2.dep > 0) & (h2.price_t > 0),
                      h2.price_t / (h2.div0 / (h2.dep / 100.0)), np.nan)
h2 = h2[(h2.icb_code != BANK_ICB) & h2.prox.notna() & np.isfinite(h2.prox)].copy()

h2_rows, pc_series = [], []
for scope, s in [("FULL", h2), ("IS", h2[h2.period == "IS"]), ("OOS", h2[h2.period == "OOS"])]:
    for ycol in ["bhar60_close", "bhar20_close"]:
        pr = [dict(ym=ym, pc=p, n=n) for ym, g in s.groupby("ym")
              for p, n in [partial_spearman(g, "z_l2", ycol, "prox")] if np.isfinite(p)]
        pr = pd.DataFrame(pr)
        _, raw = ic_summary(s, "z_l2", ycol, scope, "z_cagr_ind_L2 [H2 sample]")
        if pr.empty:
            h2_rows.append(dict(scope=scope, y=ycol, n_months=0)); continue
        t, nm = nw_t(pr.pc)
        h2_rows.append(dict(scope=scope, y=ycol, n_months=nm,
                            mean_partial_ic=float(pr.pc.mean()),
                            median_partial_ic=float(pr.pc.median()),
                            pct_pos=100 * float((pr.pc > 0).mean()), t_nw=t,
                            raw_ic_same_sample=raw.get("mean_ic"),
                            raw_t_nw_same_sample=raw.get("t_nw"),
                            mean_n_per_month=float(pr.n.mean())))
        pc_series.append(pr.assign(scope=scope, y=ycol))
pd.DataFrame(h2_rows).to_csv(f"{D}/results_h2_partial.csv", index=False)
if pc_series:
    pd.concat(pc_series).to_csv(f"{D}/results_h2_partial_monthly.csv", index=False)

# H2(b) double sort: prox tercile x z_cagr tren/duoi trung vi, cat TRONG TUNG THANG
ds = h2.copy()
ds["prox_t"] = ds.groupby("ym")["prox"].transform(
    lambda s: pd.qcut(s, 3, labels=["T1_low_prox(BELOW)", "T2", "T3_high_prox(ABOVE)"],
                      duplicates="drop") if s.nunique() >= 3 else np.nan)
ds["z_half"] = ds.groupby("ym")["z_l2"].transform(
    lambda s: np.where(s > s.median(), "hi_z", "lo_z"))
rows = []
for scope, s in [("FULL", ds), ("IS", ds[ds.period == "IS"]), ("OOS", ds[ds.period == "OOS"])]:
    for pt, g in s.dropna(subset=["prox_t"]).groupby("prox_t", observed=True):
        cell = {}
        for zh in ["hi_z", "lo_z"]:
            x = pd.to_numeric(g[g.z_half == zh]["bhar60_close"], errors="coerce").dropna()
            cell[zh] = x
            rows.append(dict(scope=scope, prox_tercile=str(pt), z_half=zh, n=len(x),
                             mean_bhar60=float(x.mean()) if len(x) else np.nan,
                             median_bhar60=float(x.median()) if len(x) else np.nan))
        a, b = cell["hi_z"], cell["lo_z"]
        if len(a) > 2 and len(b) > 2:
            tt = stats.ttest_ind(a, b, equal_var=False)
            rows.append(dict(scope=scope, prox_tercile=str(pt), z_half="hi_z MINUS lo_z",
                             n=len(a) + len(b), mean_bhar60=float(a.mean() - b.mean()),
                             median_bhar60=float(a.median() - b.median()),
                             t_welch=float(tt.statistic), p_welch=float(tt.pvalue)))
ds_out = pd.DataFrame(rows)
ds_out.to_csv(f"{D}/results_h2_doublesort.csv", index=False)

# ================================ H3 ================================
h3 = []
for scope, s in [("FULL", base), ("IS", base[base.period == "IS"]),
                 ("OOS", base[base.period == "OOS"])]:
    for lvl, zc, ic in [("ICB_L2", "z_l2", "icb_l2"), ("ICB_L1", "z_l1", "icb_l1")]:
        cells = s.groupby(["ym", ic]).size()
        h3.append(dict(scope=scope, level=lvl,
                       n_cells_ge1=int((cells >= 1).sum()),
                       n_cells_ge5=int((cells >= MIN_PAYERS).sum()),
                       pct_cells=100 * float((cells >= MIN_PAYERS).mean()),
                       n_rows_has_cagr=len(s), n_rows_kept=int(s[zc].notna().sum()),
                       pct_rows=100 * float(s[zc].notna().mean()),
                       n_months=s.ym.nunique(),
                       mean_kept_per_month=float(s[s[zc].notna()].groupby("ym").size().mean())
                       if s[zc].notna().any() else np.nan))
h3 = pd.DataFrame(h3)
h3.to_csv(f"{D}/results_h3.csv", index=False)
sub_l2.to_csv(f"{D}/panel_z.csv", index=False)

pd.set_option("display.width", 250, "display.max_columns", 40)
print(f"=== PANEL === src={SRC}")
print(f"rows={len(df)} has_cagr={len(base)} kept_L2={len(sub_l2)} kept_L1={len(sub_l1)} "
      f"H2_sample={len(h2)} months={df.ym.nunique()} {df.t.min().date()}->{df.t.max().date()}")
print("\n=== H1 / H1b / H1c / fallback: IC ===")
print(ic_out.round(4).to_string(index=False))
print("\n=== H2(a) partial Spearman | control = prox ===")
print(pd.DataFrame(h2_rows).round(4).to_string(index=False))
print("\n=== H2(b) double sort prox-tercile x z_cagr (y=bhar60_close) ===")
print(ds_out.round(4).to_string(index=False))
print("\n=== H3 sparsity ===")
print(h3.round(2).to_string(index=False))
