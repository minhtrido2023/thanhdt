"""
Levered sleeve orchestration (tune: harder capit carve, less cash, gross<=150%)
================================================================================
User has 1:1 margin (gross up to ~200%) but caps at 150% and uses it sparingly.
Relax the <=100% constraint to MAX_GROSS=1.5, deploy capit HARD when it fires,
cut idle cash. Honest leverage cost: borrow 10%/yr on the portion of gross >100%.
Discipline kept: NO leverage INTO crisis (crisis = hard capit carve only, rest
cash); TRIM in EXBULL (fragility, AMH #4); leverage mainly in BULL + when a
tactical sleeve (capit/grind) adds a live edge.

Compares: V5 baseline | ORCH <=100% (full) | ORCH <=150% levered | vs image COMMITTED.
Run: python sleeve_pnl_levered.py
"""
import sys, os
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
NAVF = os.environ.get("CORE_NAV", WORKDIR + r"\data\5sys_prodspec_201401_202605_dt5g_realetf.csv")
VALF = WORKDIR + r"\data\value_book_realistic.csv"
STATEF = WORKDIR + r"\data\dt5g_vnindex.csv"
STRONGF = WORKDIR + r"\data\bt_capitulation_STRONG.csv"
WATCHF = WORKDIR + r"\data\bt_capitulation_WATCH.csv"
BORROW = 0.10          # annual borrow cost on gross>1
MAX_GROSS = 1.50

# Levered policy: target fractions (may sum >1). Inactive tactical sleeves are
# simply DROPPED (gross falls) -> leverage only when a live edge justifies it.
POLICY_LEV = {
    1: dict(core=0.10, value=0.00, capit=0.70, grind=0.00),  # CRISIS: hard capit carve, NO leverage (gross .80)
    2: dict(core=0.45, value=0.40, capit=0.25, grind=0.00),  # BEAR  : defensive value+capit (gross up to 1.10)
    3: dict(core=0.60, value=0.40, capit=0.10, grind=0.25),  # NEUTRAL: base 1.00, +grind/capit -> up to 1.35
    4: dict(core=0.85, value=0.50, capit=0.00, grind=0.00),  # BULL  : lever the trend (gross 1.35)
    5: dict(core=0.55, value=0.35, capit=0.00, grind=0.00),  # EXBULL: TRIM, no leverage (gross .90)
}


def allocate_lev(state, capit_on, grind_on):
    p = dict(POLICY_LEV[state])
    if state == 1:
        p["value"] = 0.0
    if not capit_on:
        p["capit"] = 0.0
    if not grind_on:
        p["grind"] = 0.0
    gross = p["core"] + p["value"] + p["capit"] + p["grind"]
    if gross > MAX_GROSS:                       # scale down to the 150% cap
        s = MAX_GROSS / gross
        for k in ("core", "value", "capit", "grind"):
            p[k] *= s
        gross = MAX_GROSS
    p["gross"] = gross
    p["cash"] = max(0.0, 1.0 - gross)
    return p


def ann(ret):
    ret = ret.dropna(); mu = ret.mean()*12; sd = ret.std(ddof=1)*np.sqrt(12)
    n = len(ret); cagr = (1+ret).prod()**(12/n)-1
    nav = (1+ret).cumprod(); dd = (nav/nav.cummax()-1).min()
    return dict(CAGR=cagr*100, Sharpe=mu/sd if sd > 0 else 0,
                Sortino=mu/(ret[ret < 0].std(ddof=1)*np.sqrt(12)) if (ret < 0).any() else 0,
                MaxDD=dd*100, Calmar=cagr/abs(dd) if dd < 0 else np.nan)


def fmt(m):
    return (f"CAGR(geo) {m['CAGR']:5.2f}%  Sharpe {m['Sharpe']:.2f}  Sortino {m['Sortino']:.2f}  "
            f"MaxDD {m['MaxDD']:6.1f}%  Calmar {m['Calmar']:.2f}")


def event_stream(path, idx):
    e = pd.read_csv(path, parse_dates=["date"]); r = pd.Series(0.0, index=idx); a = pd.Series(False, index=idx)
    for _, x in e.iterrows():
        mr = (1 + x["FIX60_ret"]/100.0) ** (1/3) - 1
        for h in range(3):
            m = x["date"].to_period("M") + h
            if m in idx: r[m] = mr; a[m] = True
    return r, a


def main():
    core = pd.read_csv(NAVF, parse_dates=["time"]).set_index("time")["V5_V4_KellyQ2"]
    cm = core.resample("ME").last().pct_change(); cm.index = cm.index.to_period("M"); cm = cm.dropna()
    val = pd.read_csv(VALF); val.columns = ["ym", "v"]; val["ym"] = pd.PeriodIndex(val["ym"], freq="M"); val = val.set_index("ym")["v"]
    st = pd.read_csv(STATEF, parse_dates=["time"]); st["ym"] = st["time"].dt.to_period("M")
    state = st.groupby("ym")["state"].agg(lambda s: int(s.mode().iloc[0]))
    idx = cm.index.intersection(val.index).intersection(state.index)
    cap, con = event_stream(STRONGF, idx); grd, gon = event_stream(WATCHF, idx)

    A = pd.DataFrame([allocate_lev(int(state[m]), bool(con[m]), bool(gon[m])) for m in idx], index=idx)
    lev = (A["core"]*cm.loc[idx] + A["value"]*val.loc[idx] + A["capit"]*cap.loc[idx] + A["grind"]*grd.loc[idx]
           - BORROW/12 * (A["gross"] - 1).clip(lower=0))
    # reference arms
    base = cm.loc[idx]
    print(f"Levered orchestration (V5 core real-ETF+DT5G, gross<=150%, borrow {BORROW*100:.0f}%/yr)")
    print(f"  avg gross {A['gross'].mean():.2f}  max gross {A['gross'].max():.2f}  "
          f"avg cash {A['cash'].mean()*100:.0f}%  avg capit wt {A['capit'].mean()*100:.0f}% "
          f"(when on {A['capit'][con].mean()*100:.0f}%)  months levered>1: {int((A['gross']>1.001).sum())}")
    print(f"  mean gross by state: " + ", ".join(f"{s}:{A['gross'][state.loc[idx]==s].mean():.2f}" for s in [1,2,3,4,5] if (state.loc[idx]==s).any()))
    oos = idx >= pd.Period("2020-01")
    print()
    print(f"  V5 baseline          : {fmt(ann(base))}")
    print(f"  V5 ORCH LEVERED <=150: {fmt(ann(lev))}")
    print(f"     OOS (2020+)       : {fmt(ann(lev[oos]))}")
    print(f"\n  [image COMMITTED ref : CAGR 31.45%(daily)  Sharpe 1.63  MaxDD -23.5  | baseline 24.88%(daily)]")
    print(f"  NOTE: my CAGR is MONTHLY-geo; daily basis (like image) is ~+1.6pp higher "
          f"(my baseline {ann(base)['CAGR']:.1f}% monthly == ~24.9% daily).")
    A.to_csv(WORKDIR + r"\data\sleeve_levered_path.csv")
    print("\nSaved: data/sleeve_levered_path.csv")


if __name__ == "__main__":
    main()
