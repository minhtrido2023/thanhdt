"""
Core-architecture backtest: momentum-core vs balanced vs adaptive
=================================================================
Question (user): V5/V11 core is a momentum MONOCULTURE (BA + VN30 both momentum).
Should we elevate VALUE from satellite to a CO-EQUAL core pillar, and/or tilt the
momentum/value balance by edge-health? Compare 3 cores (no capit/grind, no leverage
— isolate the core composition question):
  A. MOMENTUM-CORE  = V5 alone (current production core)
  B. BALANCED 50/50 = 0.5 momentum + 0.5 value (static co-equal pillars)
  C. ADAPTIVE       = momentum/value tilt by CAUSAL momentum rolling-IC (#1) with
                      hysteresis: MOM-healthy -> 70/30, flipped -> 30/70, else 50/50.
Both legs gated DT5G (comparable). Edge-health signal uses fwd_1m IC LAGGED (the
real ~1-month lag of #1 — adaptive is reactive, not anticipatory; honest).

Reports full + IS/OOS + the 2025-26 momentum-drought + bull years.
Run: python backtest_core_arch.py
"""
import sys, os
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
NAVF = WORKDIR + r"/data/5sys_prodspec_201401_202605_dt5g_realetf.csv"
VALF = WORKDIR + r"/data/value_book_realistic.csv"
PANEL = WORKDIR + r"/data/edge_panel.csv"
GRIND = ("2025-09", "2026-03")


def spearman(a, b):
    return pd.Series(a).rank().corr(pd.Series(b).rank())


def mom_health():
    """Causal rolling-12M momentum cross-sectional IC (fwd_1m), lagged 1mo (no look-ahead)."""
    d = pd.read_csv(PANEL, parse_dates=["time"])
    d = d[d["fwd_1m"].notna()].copy()
    d["ym"] = d["time"].dt.to_period("M")
    ic = {}
    for ym, g in d.groupby("ym"):
        s = g[["mom_200", "fwd_1m"]].dropna()
        if len(s) >= 25 and s["mom_200"].nunique() >= 5:
            ic[ym] = spearman(s["mom_200"].values, s["fwd_1m"].values)
    ic = pd.Series(ic).sort_index()
    # rolling 12m mean, then shift(1): at month t use only ICs realized by t-1
    return ic.rolling(12, min_periods=6).mean().shift(1)


def monthly(col):
    nav = pd.read_csv(NAVF, parse_dates=["time"]).set_index("time")[col]
    r = nav.resample("ME").last().pct_change(); r.index = r.index.to_period("M")
    return r.dropna()


def ann(ret):
    ret = ret.dropna(); n = len(ret)
    if n < 3: return dict(CAGR=np.nan, Sharpe=np.nan, MaxDD=np.nan, Calmar=np.nan)
    mu = ret.mean()*12; sd = ret.std(ddof=1)*np.sqrt(12); cagr = (1+ret).prod()**(12/n)-1
    nav = (1+ret).cumprod(); dd = (nav/nav.cummax()-1).min()
    return dict(CAGR=cagr*100, Sharpe=mu/sd if sd > 0 else 0, MaxDD=dd*100,
                Calmar=cagr/abs(dd) if dd < 0 else np.nan)


def fmt(m):
    return f"CAGR {m['CAGR']:5.1f}%  Sharpe {m['Sharpe']:.2f}  MaxDD {m['MaxDD']:6.1f}%  Calmar {m['Calmar']:.2f}"


def main():
    mom = monthly("V5_V4_KellyQ2")
    val = pd.read_csv(VALF); val.columns = ["ym", "v"]; val["ym"] = pd.PeriodIndex(val["ym"], freq="M"); val = val.set_index("ym")["v"]
    mh = mom_health()
    idx = mom.index.intersection(val.index)
    m, v, mh = mom.loc[idx], val.loc[idx], mh.reindex(idx)

    # adaptive weight with hysteresis (min-stay 2 months)
    HI, LO = 0.01, -0.01
    reg, regimes, cur, cnt = [], [], "BAL", 0
    pend = "BAL"
    for t in idx:
        h = mh.get(t, np.nan)
        want = "MOM" if (pd.notna(h) and h > HI) else ("VAL" if (pd.notna(h) and h < LO) else "BAL")
        if want == cur:
            cnt = 0; pend = want
        else:
            if want == pend: cnt += 1
            else: pend, cnt = want, 1
            if cnt >= 2: cur = want; cnt = 0
        regimes.append(cur)
    wmom = pd.Series([{"MOM": 0.70, "BAL": 0.50, "VAL": 0.30}[r] for r in regimes], index=idx)

    A = m                                   # momentum-core (V5)
    B = 0.5*m + 0.5*v                        # balanced static
    C = wmom*m + (1-wmom)*v                  # adaptive
    arch = {"A momentum-core (V5)": A, "B balanced 50/50": B, "C adaptive (IC-tilt)": C, "  value-only ref": v}

    def sub(r, lo, hi): return r[(r.index >= pd.Period(lo)) & (r.index <= pd.Period(hi))]
    print(f"Period {idx.min()} → {idx.max()} ({len(idx)} months)")
    print(f"Adaptive regime months: {pd.Series(regimes).value_counts().to_dict()}  "
          f"(current: {regimes[-1]}, wmom={wmom.iloc[-1]:.0%})\n")

    print(f"{'arch':>24}  {'FULL':^46}")
    for name, r in arch.items():
        print(f"{name:>24}  {fmt(ann(r))}")
    print(f"\n  --- IS (≤2019) / OOS (2020+) ---")
    for name, r in arch.items():
        print(f"{name:>24}  IS  {fmt(ann(sub(r,'2014-01','2019-12')))}")
        print(f"{name:>24}  OOS {fmt(ann(sub(r,'2020-01','2026-12')))}")
    print(f"\n  --- GRIND {GRIND[0]}..{GRIND[1]} (momentum drought) ---")
    for name, r in arch.items():
        g = sub(r, *GRIND); cum = ((1+g).prod()-1)*100
        print(f"{name:>24}  cum {cum:+6.1f}%  (worst mo {g.min()*100:+.1f}%)")
    print(f"\n  --- BULL years (cum return) ---")
    for yr in ["2017", "2021", "2023"]:
        line = f"  {yr}: "
        for name, r in arch.items():
            g = sub(r, f"{yr}-01", f"{yr}-12"); line += f"{name.split()[0]}={((1+g).prod()-1)*100:+5.1f}%  "
        print(line)
    pd.DataFrame({"wmom": wmom, "mom_health": mh, "A": A, "B": B, "C": C, "value": v}).to_csv(
        WORKDIR + r"/data/core_arch_backtest.csv")
    print("\nSaved: data/core_arch_backtest.csv")


if __name__ == "__main__":
    main()
