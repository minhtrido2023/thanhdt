#!/usr/bin/env python3
"""
dividend_upgrade_test.py — Research-only test of whether the NEW event-based
Dividend_Min3Y (from VCI ex-date DIV events) improves the 8L rating model.

Dispatch: Taylor_20260714_033021 (Mike). Does NOT modify rating_8l.py defaults;
research/backtest first, opt-in flag only if positive & clear.

Methodology (matches fleet discipline):
 - Point-in-time: Dividend_Min3Y as-of time t vs forward profit_1M/2M/3M (T+20/40/60).
   profit_* are TRAINING/eval-only forward columns (never a live filter) — used here
   strictly for IC evaluation, the sanctioned use.
 - Cross-sectional Spearman IC per date, averaged; walk-forward IS(2014-19)/OOS(2020-26).
 - self-check style: report N, coverage, t-stats; no fitted params.

Panel: exp_dividend/panel_monthly.csv (one row per ticker-month, ticker_prune 2014-2026).
"""
import numpy as np, pandas as pd
from scipy.stats import spearmanr

EXPDIR = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_dividend"
PANEL = EXPDIR + "/panel_monthly.csv"
IS_END = "2019-12-31"          # IS 2014-2019, OOS 2020-2026
FWD = ["profit_1M", "profit_2M", "profit_3M"]


def load():
    df = pd.read_csv(PANEL, parse_dates=["time"])
    for c in ["Price","Dividend_Min3Y","DY","ROE_Min3Y","CF_OA_5Y","PE","PB","Volume_1M"]+FWD:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    # signals
    df["real_dy"]   = df["Dividend_Min3Y"] / df["Price"].replace(0, np.nan)   # true cash div yield
    df["div_payer"] = np.where(df["Dividend_Min3Y"].notna(), (df["Dividend_Min3Y"] > 0).astype(float), np.nan)
    df["earn_yield"]= 1.0 / df["PE"].replace(0, np.nan)                        # existing dominant value factor
    df["DY_old"]    = df["DY"]
    df["seg"] = np.where(df["time"] <= IS_END, "IS", "OOS")
    return df


def xsec_ic(df, sig, fwd):
    """Mean cross-sectional Spearman IC + Newey-ish t (t = mean/se over dates)."""
    ics = []
    for _, g in df.groupby("time"):
        s = g[[sig, fwd]].dropna()
        if len(s) < 15 or s[sig].nunique() < 2:   # binary signals allowed (div_payer)
            continue
        r, _ = spearmanr(s[sig], s[fwd])
        if np.isfinite(r):
            ics.append(r)
    ics = np.array(ics)
    if len(ics) == 0:
        return dict(ic=np.nan, t=np.nan, n_dates=0, hit=np.nan)
    t = ics.mean() / (ics.std(ddof=1) / np.sqrt(len(ics))) if len(ics) > 1 else np.nan
    return dict(ic=ics.mean(), t=t, n_dates=len(ics), hit=(ics > 0).mean())


def ic_table(df, sigs):
    rows = []
    for sig in sigs:
        for fwd in FWD:
            for seg, sub in [("ALL", df), ("IS", df[df.seg=="IS"]), ("OOS", df[df.seg=="OOS"])]:
                r = xsec_ic(sub, sig, fwd)
                rows.append(dict(signal=sig, fwd=fwd, seg=seg, **r))
    return pd.DataFrame(rows)


def coverage(df):
    print("\n=== COVERAGE (monthly panel, ticker_prune 2014-2026) ===")
    n = len(df)
    liq = df[df.Volume_1M >= 50000]   # liquid subset proxy (~50k sh/day avg)
    for name, d in [("full", df), ("liquid(Vol1M>=50k)", liq)]:
        print(f"  [{name}] N={len(d)}")
        print(f"    DY_old  >0     : {100*(d.DY_old>0).mean():.1f}%   non-null {100*d.DY_old.notna().mean():.1f}%")
        print(f"    Div_Min3Y >0   : {100*(d.Dividend_Min3Y>0).mean():.1f}%   =0 {100*(d.Dividend_Min3Y==0).mean():.1f}%   null {100*d.Dividend_Min3Y.isna().mean():.1f}%")
        print(f"    usable(pos+zero): {100*d.Dividend_Min3Y.notna().mean():.1f}%   real_dy computable {100*d.real_dy.notna().mean():.1f}%")


def gate_test(df):
    """Does requiring a dividend track-record ADD to the golden floor?
    golden = ROE_Min3Y>=0 & CF_OA_5Y>0.  test: + div_payer (Dividend_Min3Y>0)."""
    print("\n=== GOLDEN-FLOOR GATE TEST (fwd profit_3M, %) ===")
    d = df.dropna(subset=["ROE_Min3Y","CF_OA_5Y","profit_3M"]).copy()
    d["golden"] = (d.ROE_Min3Y >= 0) & (d.CF_OA_5Y > 0)
    d["golden_div"] = d.golden & (d.Dividend_Min3Y > 0)
    for seg, sub in [("ALL", d), ("IS", d[d.seg=="IS"]), ("OOS", d[d.seg=="OOS"])]:
        g   = sub[sub.golden];      gd = sub[sub.golden_div]
        gnd = sub[sub.golden & ~(sub.Dividend_Min3Y>0)]  # golden but NON-payer
        def stat(x):
            return f"n={len(x):6d} mean={x.profit_3M.mean():6.2f} med={x.profit_3M.median():6.2f} win={100*(x.profit_3M>0).mean():4.1f}% p10={x.profit_3M.quantile(.1):6.1f}"
        print(f"  [{seg}]")
        print(f"    golden        : {stat(g)}")
        print(f"    golden & payer: {stat(gd)}")
        print(f"    golden & NONpay:{stat(gnd)}")


def stability_vs_timing(df):
    """Is div_payer a QUALITY proxy (persistent, orthogonal) rather than a timing signal?
    Compare IC of level(real_dy) vs binary(div_payer), and persistence of div_payer."""
    print("\n=== STABILITY vs TIMING ===")
    # persistence: same-ticker autocorr of div_payer month-over-month
    dd = df.dropna(subset=["div_payer"]).sort_values(["ticker","time"])
    dd["prev"] = dd.groupby("ticker")["div_payer"].shift(1)
    per = dd.dropna(subset=["prev"])
    print(f"  div_payer month-over-month persistence P(same)= {100*(per.div_payer==per.prev).mean():.1f}% (n={len(per)})")
    # real_dy autocorr
    dd2 = df.dropna(subset=["real_dy"]).sort_values(["ticker","time"])
    dd2["prev"] = dd2.groupby("ticker")["real_dy"].shift(1)
    p2 = dd2.dropna(subset=["prev"])
    print(f"  real_dy month-over-month corr= {p2.real_dy.corr(p2.prev):.3f}")


def _zscore(s):
    return (s - s.mean()) / s.std(ddof=0) if s.std(ddof=0) > 0 else s * 0.0


def orthogonality(df):
    """Is real_dy ADDING info beyond the existing dominant value factor earn_yield(1/PE)?
    (a) cross-sectional corr; (b) residual IC of real_dy after neutralizing earn_yield;
    (c) combined equal-weight z-lens IC vs earn_yield alone."""
    print("\n=== ORTHOGONALITY vs earn_yield (1/PE) ===")
    corrs, res_ic, ey_ic, comb_ic = [], {"IS":[], "OOS":[]}, {"IS":[], "OOS":[]}, {"IS":[], "OOS":[]}
    for _, g in df.groupby("time"):
        s = g[["real_dy","earn_yield","profit_3M","time"]].dropna()
        if len(s) < 20 or s.real_dy.nunique() < 5:
            continue
        seg = "IS" if s.time.iloc[0].strftime("%Y-%m-%d") <= IS_END else "OOS"
        rdz, eyz = _zscore(s.real_dy.rank()), _zscore(s.earn_yield.rank())
        corrs.append(np.corrcoef(rdz, eyz)[0,1])
        # residual real_dy after removing earn_yield (rank space)
        beta = np.polyfit(eyz, rdz, 1)[0]
        resid = rdz - beta*eyz
        rr,_ = spearmanr(resid, s.profit_3M);           res_ic[seg].append(rr)
        re,_ = spearmanr(s.earn_yield, s.profit_3M);     ey_ic[seg].append(re)
        rc,_ = spearmanr(rdz+eyz, s.profit_3M);          comb_ic[seg].append(rc)   # equal-wt combo
    def mt(a): a=np.array(a); return (np.nan,np.nan) if len(a)==0 else (a.mean(), a.mean()/(a.std(ddof=1)/np.sqrt(len(a))))
    print(f"  mean xsec rank-corr(real_dy, earn_yield) = {np.nanmean(corrs):.3f}  (0=orthogonal, 1=redundant)")
    for seg in ["IS","OOS"]:
        r_i,r_t = mt(res_ic[seg]); e_i,e_t = mt(ey_ic[seg]); c_i,c_t = mt(comb_ic[seg])
        print(f"  [{seg}] earn_yield IC={e_i:+.4f}(t{e_t:.1f}) | real_dy RESIDUAL IC={r_i:+.4f}(t{r_t:.1f}) | ey+real_dy combo IC={c_i:+.4f}(t{c_t:.1f})")


def weight_sweep(df):
    """Blend value composite = (1-w)*z(ey) + w*z(div). Find w that helps IS without diluting OOS.
    Uses rank-z of earn_yield and real_dy; IC vs profit_3M, IS/OOS."""
    print("\n=== EY+DIV WEIGHT SWEEP (composite IC vs profit_3M) ===")
    weights = [0.0, 0.10, 0.15, 0.20, 0.25, 0.35, 0.50]
    acc = {w: {"IS": [], "OOS": []} for w in weights}
    for _, g in df.groupby("time"):
        s = g[["earn_yield","real_dy","profit_3M","time"]].dropna()
        if len(s) < 20 or s.real_dy.nunique() < 5:
            continue
        seg = "IS" if s.time.iloc[0].strftime("%Y-%m-%d") <= IS_END else "OOS"
        eyz, rdz = _zscore(s.earn_yield.rank()), _zscore(s.real_dy.rank())
        for w in weights:
            blend = (1-w)*eyz + w*rdz
            r,_ = spearmanr(blend, s.profit_3M)
            if np.isfinite(r): acc[w][seg].append(r)
    print(f"  {'w_div':>6} | {'IS_IC':>8} {'IS_t':>6} | {'OOS_IC':>8} {'OOS_t':>6}")
    for w in weights:
        def mt(a): a=np.array(a); return (a.mean(), a.mean()/(a.std(ddof=1)/np.sqrt(len(a))))
        i_ic,i_t = mt(acc[w]["IS"]); o_ic,o_t = mt(acc[w]["OOS"])
        print(f"  {w:6.2f} | {i_ic:+8.4f} {i_t:6.1f} | {o_ic:+8.4f} {o_t:6.1f}")


def case_studies(df):
    print("\n=== CASE STUDIES: names where DY_old missing but Div_Min3Y present ===")
    latest = df.sort_values("time").groupby("ticker").tail(1)
    cand = latest[(latest.DY_old.isna() | (latest.DY_old==0)) & (latest.Dividend_Min3Y>0)]
    cand = cand.sort_values("real_dy", ascending=False)
    cols = ["ticker","time","Price","Dividend_Min3Y","real_dy","DY_old","ROE_Min3Y","PE"]
    print(f"  {len(cand)} liquid names gain a usable dividend signal. Top real_dy:")
    print(cand[cols].head(12).to_string(index=False))


if __name__ == "__main__":
    df = load()
    print(f"panel rows={len(df)}  tickers={df.ticker.nunique()}  dates={df.time.nunique()}  {df.time.min().date()}..{df.time.max().date()}")
    coverage(df)
    sigs = ["real_dy","div_payer","DY_old","earn_yield"]
    tab = ic_table(df, sigs)
    print("\n=== CROSS-SECTIONAL IC (Spearman, per-date avg) ===")
    with pd.option_context("display.width",200,"display.max_rows",200):
        print(tab.round(4).to_string(index=False))
    tab.to_csv(EXPDIR+"/ic_table.csv", index=False)
    orthogonality(df)
    gate_test(df)
    weight_sweep(df)
    stability_vs_timing(df)
    case_studies(df)
    print("\n[done] ic_table -> " + EXPDIR)
