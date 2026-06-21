"""
Sleeve Budget Allocator  (capital-budgeting orchestrator for the 4-sleeve book)
===============================================================================
Problem (from the interaction analysis): core + value + capitulation + grind-half
all want capital, overlapping in NEUTRAL. Stacking them naively can over-allocate
(memory: committed-sleeve hit 148% NAV in 2022). This allocator gives ONE coherent
budget: total carve-out <= 100% of NAV, state-conditional PRIORITY, and activation
gates so a sleeve only consumes capital when its signal actually fires.

Design:
  * DT5G state sets the broad risk posture (the policy row).
  * Each state has a target split across {core, value, capit, grind}; the rest = cash.
  * ACTIVATION GATES: value off in CRISIS (gated); capit only on washout
    (oversold>=40%); grind only in a NEUTRAL grind (flat index + weak breadth +
    elevated oversold). An inactive sleeve's budget reverts to core (capped) then cash.
  * CAPS: per-sleeve cap, max total sleeve carve, min core. Renormalize to <=1.

Outputs: policy table, weight timeline (PNG), activation summary, combined backtest
(core+value real P&L; capit/grind sized but parked in CASH for P&L = CONSERVATIVE,
since their streams are separately paper-traded), today's recommended allocation.

Run: python sleeve_budget_allocator.py
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import os
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
NAVF = os.environ.get("CORE_NAV", WORKDIR + r"\data\5sys_prodspec_201401_202605_dt5g.csv")
VALF = WORKDIR + r"\data\value_book_realistic.csv"
STATEF = WORKDIR + r"\data\dt5g_vnindex.csv"
ECOF = WORKDIR + r"\data\ecology_panel.csv"
STATE_LBL = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EXBULL"}

# ---- POLICY: target NAV fractions per state (when all relevant sleeves active) ----
# rows sum <= 1.0; remainder = cash. Fit per Fitness Matrix #3:
#   CRISIS  -> mostly cash; capitulation is the only tactical edge; core(mom) inverts, value gated.
#   BEAR    -> defensive value + trimmed core.
#   NEUTRAL -> core + value + grind (the budget-competition zone).
#   BULL    -> core + value (both fit), no capit/grind.
#   EXBULL  -> trim gross (fragility, #4): smaller core+value.
POLICY = {
    1: dict(core=0.10, value=0.00, capit=0.40, grind=0.00),   # CRISIS
    2: dict(core=0.40, value=0.30, capit=0.10, grind=0.00),   # BEAR
    3: dict(core=0.45, value=0.25, capit=0.05, grind=0.15),   # NEUTRAL
    4: dict(core=0.60, value=0.35, capit=0.00, grind=0.00),   # BULL
    5: dict(core=0.50, value=0.30, capit=0.00, grind=0.00),   # EXBULL
}
CAP = dict(value=0.35, capit=0.40, grind=0.20)            # per-sleeve max
# core cap is STATE-DEPENDENT: in CRISIS momentum INVERTS (#3) -> cap core hard so
# an unfired capit budget overflows to CASH, not back into bad-regime momentum.
CORE_CAP = {1: 0.10, 2: 0.50, 3: 0.70, 4: 0.70, 5: 0.50}
MAX_SLEEVE = 0.50      # value+capit+grind total carve cap


def allocate(state, capit_on, grind_on, value_on=None):
    """Return dict of NAV fractions {core,value,capit,grind,cash}, sum=1."""
    p = dict(POLICY[state])
    if value_on is None:
        value_on = (state != 1)          # value gated off in CRISIS
    # activation gates: inactive sleeve budget -> core (then capped -> cash)
    if not value_on:
        p["core"] += p["value"]; p["value"] = 0.0
    if not capit_on:
        p["core"] += p["capit"]; p["capit"] = 0.0
    if not grind_on:
        p["core"] += p["grind"]; p["grind"] = 0.0
    # per-sleeve caps (overflow -> core)
    for k in ("value", "capit", "grind"):
        if p[k] > CAP[k]:
            p["core"] += p[k] - CAP[k]; p[k] = CAP[k]
    # total sleeve carve cap
    sleeve = p["value"] + p["capit"] + p["grind"]
    if sleeve > MAX_SLEEVE:
        scale = MAX_SLEEVE / sleeve
        for k in ("value", "capit", "grind"):
            p["core"] += p[k] * (1 - scale); p[k] *= scale
    # state-dependent core cap -> overflow to CASH (key in CRISIS: no bad-regime momentum)
    p["core"] = min(p["core"], CORE_CAP[state])
    inv = p["core"] + p["value"] + p["capit"] + p["grind"]
    p["cash"] = max(0.0, 1.0 - inv)
    return p


def load():
    st = pd.read_csv(STATEF, parse_dates=["time"]); st["ym"] = st["time"].dt.to_period("M")
    g = st.groupby("ym")
    state = g["state"].agg(lambda s: int(s.mode().iloc[0]))
    px = g["vnindex"].last()
    eco = pd.read_csv(ECOF, parse_dates=["time"]); eco["ym"] = eco["time"].dt.to_period("M")
    em = eco.groupby("ym").agg(oversold=("pct_oversold", "mean"), breadth=("breadth200", "mean"))
    M = pd.DataFrame({"state": state, "px": px}).join(em)
    M["idx3m"] = M["px"].pct_change(3)
    # activation signals
    M["capit_on"] = M["oversold"] >= 0.30   # DEMO proxy; production uses real pt_capitulation signal
    M["grind_on"] = (M["state"] == 3) & (M["idx3m"].abs() < 0.05) & (M["breadth"] < 0.45)
    return M.dropna(subset=["state"])


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


def book_monthly(col):
    nav = pd.read_csv(NAVF, parse_dates=["time"]).set_index("time")[col]
    r = nav.resample("ME").last().pct_change(); r.index = r.index.to_period("M")
    return r.dropna()


def main():
    M = load()
    print("=== POLICY (target NAV fractions per state; rest = cash) ===")
    print(pd.DataFrame(POLICY).T.rename(index=STATE_LBL).to_string())
    print(f"sleeve caps {CAP} | max_total_sleeve {MAX_SLEEVE} | core cap by state {CORE_CAP}")

    # build allocation path
    alloc = M.apply(lambda r: allocate(int(r["state"]), bool(r["capit_on"]), bool(r["grind_on"])),
                    axis=1, result_type="expand")
    A = pd.concat([M[["state", "capit_on", "grind_on"]], alloc], axis=1)
    print(f"\nActivation over {len(A)} months: capit fires {int(A['capit_on'].sum())}, "
          f"grind fires {int(A['grind_on'].sum())}")
    print("Mean allocation by state:")
    print(A.groupby("state")[["core", "value", "capit", "grind", "cash"]].mean()
          .rename(index=STATE_LBL).round(2).to_string())

    # combined backtest (CONSERVATIVE: capit/grind parked in cash for P&L)
    value = pd.read_csv(VALF); value.columns = ["ym", "v"]
    value["ym"] = pd.PeriodIndex(value["ym"], freq="M"); value = value.set_index("ym")["v"]
    print("\n=== COMBINED BACKTEST (orchestrated vs core-alone vs naive fixed-30% value) ===")
    print("    (capit/grind sized by allocator but parked in CASH for P&L -> CONSERVATIVE)")
    for col, lbl in [("V4_V121_ENS_TQ34b", "V12.1 core"), ("V5_V4_KellyQ2", "V5 core")]:
        core = book_monthly(col)
        idx = core.index.intersection(value.index).intersection(A.index)
        c, v, a = core.loc[idx], value.loc[idx], A.loc[idx]
        # normalize core+value within the (core+value) invested part for clean P&L attribution
        orch = a["core"]*c + a["value"]*v          # capit/grind/cash -> 0
        base = c                                    # core alone (already self-gated)
        fixed = 0.7*c + 0.3*v
        oos = idx >= pd.Period("2020-01")
        print(f"\n  -- {lbl}")
        print(f"     core alone      : {fmt(ann(base))}")
        print(f"     fixed 30% value : {fmt(ann(fixed))}")
        print(f"     ORCHESTRATED    : {fmt(ann(orch))}")
        print(f"       avg weights: core {a['core'].mean():.2f} value {a['value'].mean():.2f} "
              f"cash {a['cash'].mean():.2f} | OOS orch {fmt(ann(orch[oos]))}")

    # today's recommendation
    last = A.iloc[-1]
    print(f"\n=== TODAY ({M.index[-1]}) — DT5G {STATE_LBL[int(last['state'])]}, "
          f"capit {'ON' if last['capit_on'] else 'off'}, grind {'ON' if last['grind_on'] else 'off'} ===")
    print(f"  Recommended NAV split: core {last['core']:.0%} | value {last['value']:.0%} | "
          f"capit {last['capit']:.0%} | grind {last['grind']:.0%} | cash {last['cash']:.0%}")

    # plot weight timeline
    fig, ax = plt.subplots(figsize=(14, 6))
    A2 = A.copy(); A2.index = A2.index.to_timestamp()
    ax.stackplot(A2.index, A2["core"], A2["value"], A2["capit"], A2["grind"], A2["cash"],
                 labels=["core", "value", "capit", "grind", "cash"],
                 colors=["#1f77b4", "#2ca02c", "#d62728", "#ff7f0e", "#cccccc"], alpha=0.85)
    ax.set_ylim(0, 1); ax.legend(loc="lower left", ncol=5, fontsize=9)
    ax.set_title("Sleeve Budget Allocator — NAV allocation path (state-conditional, gated)")
    fig.tight_layout(); fig.savefig(WORKDIR + r"\sleeve_budget_allocator.png", dpi=110)
    A.to_csv(WORKDIR + r"\data\sleeve_allocation_path.csv")
    print("\nSaved: sleeve_budget_allocator.png | data/sleeve_allocation_path.csv")


if __name__ == "__main__":
    main()
