"""
Full-P&L sleeve orchestration (engineering step 1)
==================================================
Upgrades the sleeve allocator's combined backtest from CONSERVATIVE (capit/grind
parked in cash) to a FULL P&L by building real return streams for the two tactical
sleeves from their backtested event returns:
  capit stream  <- bt_capitulation_STRONG (tier1, deep washout) FIX60 basket return
  grind stream  <- bt_capitulation_WATCH  (tier2, milder/NEUTRAL washout) FIX60 return
Each event = enter at event month, hold ~60 trading days (=3 months), earn the
realized FIX60 return spread geometrically over those 3 months; cash otherwise.
The allocator's capit_on / grind_on gates are driven by these REAL event windows
(a sleeve gets budget exactly when it holds a live position) — self-consistent.

Run: python sleeve_pnl_full.py
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import os
import numpy as np
import pandas as pd
from sleeve_budget_allocator import allocate, STATE_LBL

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
NAVF = os.environ.get("CORE_NAV", WORKDIR + r"\data\5sys_prodspec_201401_202605_dt5g.csv")
VALF = WORKDIR + r"\data\value_book_realistic.csv"
STATEF = WORKDIR + r"\data\dt5g_vnindex.csv"
STRONGF = WORKDIR + r"\data\bt_capitulation_STRONG.csv"
WATCHF = WORKDIR + r"\data\bt_capitulation_WATCH.csv"
HOLD_M = 3             # 60 trading days ≈ 3 months


def ann(ret):
    ret = ret.dropna()
    mu = ret.mean()*12; sd = ret.std(ddof=1)*np.sqrt(12)
    nav = (1+ret).cumprod(); dd = (nav/nav.cummax()-1).min()
    return dict(CAGR=mu*100, Sharpe=mu/sd if sd > 0 else 0,
                Sortino=mu/(ret[ret < 0].std(ddof=1)*np.sqrt(12)) if (ret < 0).any() else 0,
                MaxDD=dd*100, Calmar=mu/abs(dd) if dd < 0 else np.nan)


def fmt(m):
    return (f"CAGR {m['CAGR']:5.1f}%  Sharpe {m['Sharpe']:.2f}  Sortino {m['Sortino']:.2f}  "
            f"MaxDD {m['MaxDD']:6.1f}%  Calmar {m['Calmar']:.2f}")


def event_stream(path, all_months):
    """Build monthly return stream + active flag from a capitulation event file.
    Each event's FIX60 total return is spread geometrically over HOLD_M months."""
    ev = pd.read_csv(path, parse_dates=["date"])
    ret = pd.Series(0.0, index=all_months); active = pd.Series(False, index=all_months)
    for _, r in ev.iterrows():
        m0 = r["date"].to_period("M")
        tot = r["FIX60_ret"] / 100.0
        mret = (1 + tot) ** (1.0 / HOLD_M) - 1
        for h in range(HOLD_M):
            m = m0 + h
            if m in ret.index:
                ret[m] = mret          # later events overwrite earlier in overlap (single position)
                active[m] = True
    return ret, active


def book_monthly(col):
    nav = pd.read_csv(NAVF, parse_dates=["time"]).set_index("time")[col]
    r = nav.resample("ME").last().pct_change(); r.index = r.index.to_period("M")
    return r.dropna()


def main():
    st = pd.read_csv(STATEF, parse_dates=["time"]); st["ym"] = st["time"].dt.to_period("M")
    state = st.groupby("ym")["state"].agg(lambda s: int(s.mode().iloc[0]))
    months = state.index

    capit, capit_on = event_stream(STRONGF, months)
    grind, grind_on = event_stream(WATCHF, months)
    print(f"Event windows: capit active {int(capit_on.sum())} months "
          f"(mean ret in-window {capit[capit_on].mean()*100:+.2f}%/mo), "
          f"grind active {int(grind_on.sum())} months "
          f"({grind[grind_on].mean()*100:+.2f}%/mo)")

    value = pd.read_csv(VALF); value.columns = ["ym", "v"]
    value["ym"] = pd.PeriodIndex(value["ym"], freq="M"); value = value.set_index("ym")["v"]

    # allocation path driven by REAL event windows
    A = pd.DataFrame([allocate(int(state[m]), bool(capit_on[m]), bool(grind_on[m]))
                      for m in months], index=months)
    print("\nMean allocation by state (real event-driven gates):")
    AA = A.join(state.rename("state"))
    print(AA.groupby("state")[["core", "value", "capit", "grind", "cash"]].mean()
          .rename(index=STATE_LBL).round(2).to_string())

    print("\n=== FULL-P&L combined orchestration (capit/grind now earn real returns) ===")
    for col, lbl in [("V4_V121_ENS_TQ34b", "V12.1"), ("V5_V4_KellyQ2", "V5")]:
        core = book_monthly(col)
        idx = core.index.intersection(value.index).intersection(months)
        c, v, a = core.loc[idx], value.loc[idx], A.loc[idx]
        cap, grd = capit.loc[idx], grind.loc[idx]
        base = c
        fixed = 0.7*c + 0.3*v
        orch_cash = a["core"]*c + a["value"]*v                         # capit/grind -> cash (old)
        orch_full = a["core"]*c + a["value"]*v + a["capit"]*cap + a["grind"]*grd  # FULL
        oos = idx >= pd.Period("2020-01")
        print(f"\n  -- {lbl}")
        print(f"     core alone        : {fmt(ann(base))}")
        print(f"     fixed 30% value   : {fmt(ann(fixed))}")
        print(f"     orch (capit/grind=cash): {fmt(ann(orch_cash))}")
        print(f"     ORCH FULL-P&L     : {fmt(ann(orch_full))}")
        print(f"       OOS full: {fmt(ann(orch_full[oos]))}  | capit/grind add "
              f"{(ann(orch_full)['CAGR']-ann(orch_cash)['CAGR']):+.1f}pp CAGR vs cash-parked")

    out = pd.DataFrame({"capit": capit, "capit_on": capit_on, "grind": grind, "grind_on": grind_on})
    out.to_csv(WORKDIR + r"\data\sleeve_tactical_streams.csv")
    print("\nSaved: data/sleeve_tactical_streams.csv")


if __name__ == "__main__":
    main()
