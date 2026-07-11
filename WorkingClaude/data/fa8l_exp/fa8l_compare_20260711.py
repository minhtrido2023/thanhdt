# -*- coding: utf-8 -*-
"""fa_ratings_8l migration validation — comparison + robustness (job Taylor_20260711_094714).

Reads the 3 probe audit CSVs (control=legacy fa_ratings / tier8l / rating8l), computes:
  1. FULL + walk-forward IS(2014-19)/OOS(2020+) CAGR, Sharpe, MaxDD, Calmar (registry conventions:
     daily combined_nav, logret, ANN=252 — same as dsr_pbo_annex.py).
  2. Per-year returns + per-year leave-one-out on the DELTA vs control (Wave1/H8a lesson:
     if 1-2 years carry the whole edge -> reshuffle-luck, not signal).
  3. DSR for each variant (BLdP, trial-family variance from the registry config family
     + these 2 new trials; N declared at N_csv+2 / 120 / 200 like the pinned annex).
  4. PBO (CSCV S=16) over the family INCLUDING the 2 new variants.
  5. Bootstrap circular-block L=21 5th-pct CAGR / MaxDD for each variant.
Deterministic (fixed seeds, inherited from dsr_pbo_annex). Read-only: writes nothing.
"""
import os, sys, math
import numpy as np, pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)

from dsr_pbo_annex import (load_nav, daily_logret, moments, expected_max_sr, dsr,
                           cscv_pbo, circular_block_boot, family_paths, ANN)

EXP = "data/fa8l_exp"
CSVS = {
    "legacy_control": f"{EXP}/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_falegacy_control.csv",
    "tier8l":         f"{EXP}/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_fatier8l_exp.csv",
    "rating8l":       f"{EXP}/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_farating8l_exp.csv",
}
PIN = {"CAGR": 28.82, "Sharpe": 1.90, "MaxDD": -15.7, "Calmar": 1.83}

def metrics(nav):
    """nav: daily Series (datetime index). Registry conventions."""
    r = daily_logret(nav)
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1 / yrs) - 1
    sh = r.mean() / r.std(ddof=1) * math.sqrt(ANN)
    peak = nav.cummax()
    mdd = (nav / peak - 1).min()
    calmar = cagr / abs(mdd) if mdd != 0 else float("nan")
    return cagr * 100, sh, mdd * 100, calmar

def window(nav, lo=None, hi=None):
    s = nav
    if lo: s = s[s.index >= lo]
    if hi: s = s[s.index <= hi]
    return s

def annual_returns(nav):
    out = {}
    for y in range(nav.index[0].year, nav.index[-1].year + 1):
        ny = nav[nav.index.year == y]
        if len(ny) < 5: continue
        out[y] = ny.iloc[-1] / ny.iloc[0] - 1
    return out

def loo_cagr(ann_ret, drop_year=None):
    """Geometric CAGR from annual returns, optionally excluding one year."""
    items = [(y, r) for y, r in ann_ret.items() if y != drop_year]
    if not items: return float("nan")
    g = np.prod([1 + r for _, r in items])
    return (g ** (1 / len(items)) - 1) * 100

def main():
    navs = {}
    for k, p in CSVS.items():
        if not os.path.exists(p):
            print(f"MISSING: {p}"); sys.exit(1)
        navs[k] = load_nav(p)
        print(f"loaded {k}: {len(navs[k])} daily obs  ({navs[k].index[0].date()} -> {navs[k].index[-1].date()})")

    print("\n" + "=" * 100)
    print("[1] HEADLINE + WALK-FORWARD (registry conventions)")
    print("=" * 100)
    rows = []
    for k, nav in navs.items():
        full = metrics(nav)
        is_  = metrics(window(nav, hi="2019-12-31"))
        oos  = metrics(window(nav, lo="2020-01-01"))
        rows.append((k, full, is_, oos))
        print(f"{k:16s} FULL: CAGR {full[0]:6.2f}%  Sh {full[1]:.2f}  MaxDD {full[2]:6.1f}%  Calmar {full[3]:.2f}"
              f"   | IS: {is_[0]:6.2f}%/{is_[1]:.2f}/{is_[2]:6.1f}%/{is_[3]:.2f}"
              f"   | OOS: {oos[0]:6.2f}%/{oos[1]:.2f}/{oos[2]:6.1f}%/{oos[3]:.2f}")
    ctrl_full = rows[0][1]
    print(f"\ncontrol vs PIN (28.82/1.90/-15.7/1.83): "
          f"dCAGR {ctrl_full[0]-PIN['CAGR']:+.2f}pp  dSh {ctrl_full[1]-PIN['Sharpe']:+.2f}  "
          f"dDD {ctrl_full[2]-PIN['MaxDD']:+.1f}pp  dCalmar {ctrl_full[3]-PIN['Calmar']:+.2f}")

    print("\n" + "=" * 100)
    print("[2] PER-YEAR + LOO on delta vs control")
    print("=" * 100)
    ann = {k: annual_returns(nav) for k, nav in navs.items()}
    years = sorted(ann["legacy_control"].keys())
    hdr = "year  " + "".join(f"{k:>16s}" for k in navs) + "   d(tier8l)   d(rating8l)"
    print(hdr)
    for y in years:
        line = f"{y}  "
        for k in navs:
            line += f"{ann[k].get(y, float('nan'))*100:15.2f}%"
        d1 = (ann['tier8l'].get(y, np.nan) - ann['legacy_control'].get(y, np.nan)) * 100
        d2 = (ann['rating8l'].get(y, np.nan) - ann['legacy_control'].get(y, np.nan)) * 100
        print(line + f"  {d1:+9.2f}pp  {d2:+9.2f}pp")

    for variant in ("tier8l", "rating8l"):
        base_edge = loo_cagr(ann[variant]) - loo_cagr(ann["legacy_control"])
        print(f"\nLOO {variant}: full-geo edge (annual-ret basis) = {base_edge:+.2f}pp; drop-1-year edges:")
        drops = []
        for y in years:
            e = loo_cagr(ann[variant], drop_year=y) - loo_cagr(ann["legacy_control"], drop_year=y)
            drops.append((y, e))
        print("   " + "  ".join(f"{y}:{e:+.2f}" for y, e in drops))
        neg = [y for y, e in drops if e < 0]
        print(f"   years whose removal flips edge NEGATIVE: {neg if neg else 'NONE'}"
              f"   (min edge after any single-year drop: {min(e for _, e in drops):+.2f}pp)")

    print("\n" + "=" * 100)
    print("[3] DSR (BLdP) — family variance incl. 2 new trials")
    print("=" * 100)
    fam = family_paths()
    series = {}
    for p in fam:
        s = load_nav(p)
        if s is None or len(s) < 2500: continue
        series[p] = s
    for k in ("tier8l", "rating8l"):
        series[CSVS[k]] = navs[k]
    srs = np.array([daily_logret(s).mean() / daily_logret(s).std(ddof=1) for s in series.values()])
    var_sr = srs.var(ddof=1)
    print(f"family: {len(series)} configs (registry family + 2 fa8l trials); Var(per-day SR)={var_sr:.3e}")
    for k in ("legacy_control", "tier8l", "rating8l"):
        r = daily_logret(navs[k]); T = len(r)
        sr_hat, g3, g4 = moments(r)
        out = []
        for label, N in [(f"N={len(series)}", len(series)), ("N=120", 120), ("N=200", 200)]:
            sr0 = expected_max_sr(var_sr, N)
            p_dsr, _ = dsr(sr_hat, sr0, g3, g4, T)
            out.append(f"{label}: {p_dsr:.4f}{' <<<RED' if p_dsr < 0.95 else ''}")
        print(f"{k:16s} ann-SR {sr_hat*math.sqrt(ANN):.3f}  DSR  " + "   ".join(out))

    print("\n" + "=" * 100)
    print("[4] PBO (CSCV S=16) — family incl. 2 new trials")
    print("=" * 100)
    common = None
    for s in series.values():
        common = s.index if common is None else common.intersection(s.index)
    common = common.sort_values()
    lvl = np.column_stack([s.reindex(common).values for s in series.values()])
    Mret = np.diff(np.log(lvl), axis=0)
    pbo, logits, ncomb, ncfg, T2 = cscv_pbo(Mret, S=16)
    print(f"matrix {Mret.shape[0]} x {ncfg}; PBO = {pbo:.4f}  "
          f"(median logit {np.median(logits):.2f}, P(lambda<0)={(logits<0).mean():.4f})")

    print("\n" + "=" * 100)
    print("[5] BOOTSTRAP circular-block L=21 (B=4000, seed=12345)")
    print("=" * 100)
    for k, nav in navs.items():
        C, D = circular_block_boot(daily_logret(nav), L=21, B=4000, seed=12345)
        print(f"{k:16s} CAGR 5th={np.percentile(C,5)*100:5.1f}%  med={np.percentile(C,50)*100:5.1f}%  | "
              f"MaxDD 5th={np.percentile(D,5)*100:6.1f}%  P(DD<-30%)={(D<-0.30).mean()*100:4.1f}%")

    print("\nDONE.")

if __name__ == "__main__":
    main()
