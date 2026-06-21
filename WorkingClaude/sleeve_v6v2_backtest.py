"""
V6-v2 backtest — BALANCED 50/50 core (momentum+value) + capit/grind + leverage
==============================================================================
Per the core-architecture decision, the strategic core is now 50/50 momentum+value
(co-equal pillars) instead of momentum-only. capit/grind tactical sleeves + DT5G
state-conditional gross (<=150%, borrow 10%/yr on >100%) as before. Compares:
  V5 alone | old V6 (momentum-core levered) | V6-v2 (balanced-core levered).
core_ret = 0.5*V5_momentum + 0.5*value_book (both gated DT5G).
Run: python sleeve_v6v2_backtest.py
"""
import sys, os
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
NAVF = WORKDIR + r"\data\5sys_prodspec_201401_202605_dt5g_realetf.csv"
VALF = WORKDIR + r"\data\value_book_realistic.csv"
STATEF = WORKDIR + r"\data\dt5g_vnindex.csv"
STRONGF = WORKDIR + r"\data\bt_capitulation_STRONG.csv"
WATCHF = WORKDIR + r"\data\bt_capitulation_WATCH.csv"
BORROW, MAX_GROSS = 0.10, 1.50
GRIND = ("2025-09", "2026-03")

# V6-v2 policy: w_core applies to the BALANCED 50/50 core.
V6V2 = {1: dict(core=0.10, capit=0.70, grind=0.00),   # CRISIS (both pillars ~cash; capit carries)
        2: dict(core=0.85, capit=0.25, grind=0.00),   # BEAR
        3: dict(core=1.00, capit=0.10, grind=0.25),   # NEUTRAL
        4: dict(core=1.35, capit=0.00, grind=0.00),   # BULL (lever balanced core)
        5: dict(core=0.90, capit=0.00, grind=0.00)}   # EXBULL (trim, fragility)
# old V6 (momentum-core) policy for comparison
V6OLD = {1: dict(core=0.10, value=0.00, capit=0.70, grind=0.00),
         2: dict(core=0.45, value=0.40, capit=0.25, grind=0.00),
         3: dict(core=0.60, value=0.40, capit=0.10, grind=0.25),
         4: dict(core=0.85, value=0.50, capit=0.00, grind=0.00),
         5: dict(core=0.55, value=0.35, capit=0.00, grind=0.00)}


def ann(ret):
    ret = ret.dropna(); n = len(ret); mu = ret.mean()*12; sd = ret.std(ddof=1)*np.sqrt(12)
    cagr = (1+ret).prod()**(12/n)-1; nav = (1+ret).cumprod(); dd = (nav/nav.cummax()-1).min()
    return dict(CAGR=cagr*100, Sharpe=mu/sd if sd > 0 else 0,
                Sortino=mu/(ret[ret < 0].std(ddof=1)*np.sqrt(12)) if (ret < 0).any() else 0,
                MaxDD=dd*100, Calmar=cagr/abs(dd) if dd < 0 else np.nan)


def fmt(m):
    return (f"CAGR {m['CAGR']:5.1f}%  Sharpe {m['Sharpe']:.2f}  Sortino {m['Sortino']:.2f}  "
            f"MaxDD {m['MaxDD']:6.1f}%  Calmar {m['Calmar']:.2f}")


def monthly(col):
    nav = pd.read_csv(NAVF, parse_dates=["time"]).set_index("time")[col]
    r = nav.resample("ME").last().pct_change(); r.index = r.index.to_period("M"); return r.dropna()


def event_stream(path, idx):
    e = pd.read_csv(path, parse_dates=["date"]); r = pd.Series(0.0, index=idx); a = pd.Series(False, index=idx)
    for _, x in e.iterrows():
        mr = (1 + x["FIX60_ret"]/100.0)**(1/3)-1
        for h in range(3):
            m = x["date"].to_period("M")+h
            if m in idx: r[m] = mr; a[m] = True
    return r, a


def gross_of(p, keys): return sum(p.get(k, 0) for k in keys)


def main():
    mom = monthly("V5_V4_KellyQ2")
    val = pd.read_csv(VALF); val.columns = ["ym", "v"]; val["ym"] = pd.PeriodIndex(val["ym"], freq="M"); val = val.set_index("ym")["v"]
    st = pd.read_csv(STATEF, parse_dates=["time"]); st["ym"] = st["time"].dt.to_period("M")
    state = st.groupby("ym")["state"].agg(lambda s: int(s.mode().iloc[0]))
    idx = mom.index.intersection(val.index).intersection(state.index)
    m, v = mom.loc[idx], val.loc[idx]
    cap, con = event_stream(STRONGF, idx); grd, gon = event_stream(WATCHF, idx)
    core_bal = 0.5*m + 0.5*v

    def build(policy, balanced):
        rets, grosses = [], []
        for t in idx:
            p = dict(policy[int(state[t])])
            if not con[t]: p["capit"] = 0.0
            if not gon[t]: p["grind"] = 0.0
            if balanced:
                g = p["core"] + p["capit"] + p["grind"]
                if g > MAX_GROSS:
                    s = MAX_GROSS/g; p = {k: x*s for k, x in p.items()}; g = MAX_GROSS
                r = p["core"]*core_bal[t] + p["capit"]*cap[t] + p["grind"]*grd[t]
            else:
                if int(state[t]) == 1: p["value"] = 0.0
                g = p["core"]+p["value"]+p["capit"]+p["grind"]
                if g > MAX_GROSS:
                    s = MAX_GROSS/g; p = {k: x*s for k, x in p.items()}; g = MAX_GROSS
                r = p["core"]*m[t] + p["value"]*v[t] + p["capit"]*cap[t] + p["grind"]*grd[t]
            r -= BORROW/12*max(0, g-1); rets.append(r); grosses.append(g)
        return pd.Series(rets, index=idx), pd.Series(grosses, index=idx)

    v6v2, g2 = build(V6V2, True)
    v6old, g1 = build(V6OLD, False)
    arms = {"V5 alone": m, "old V6 (mom-core levered)": v6old, "V6-v2 (balanced-core levered)": v6v2}

    def sub(r, lo, hi): return r[(r.index >= pd.Period(lo)) & (r.index <= pd.Period(hi))]
    print(f"Period {idx.min()} → {idx.max()} ({len(idx)} months)")
    print(f"V6-v2 avg gross {g2.mean():.2f} (max {g2.max():.2f})\n")
    print(f"{'arm':>30}  FULL")
    for n, r in arms.items(): print(f"{n:>30}  {fmt(ann(r))}")
    print("\n  --- OOS (2020+) ---")
    for n, r in arms.items(): print(f"{n:>30}  {fmt(ann(sub(r,'2020-01','2026-12')))}")
    print(f"\n  --- GRIND {GRIND[0]}..{GRIND[1]} ---")
    for n, r in arms.items():
        g = sub(r, *GRIND); print(f"{n:>30}  cum {((1+g).prod()-1)*100:+.1f}%  worst {g.min()*100:+.1f}%")
    print(f"\n  --- BULL years ---")
    for yr in ["2017", "2021", "2023"]:
        line = f"  {yr}: "
        for n, r in arms.items():
            g = sub(r, f"{yr}-01", f"{yr}-12"); line += f"{n.split()[0]}={((1+g).prod()-1)*100:+5.1f}%  "
        print(line)
    pd.DataFrame({"V5": m, "v6old": v6old, "v6v2": v6v2, "gross_v6v2": g2}).to_csv(WORKDIR + r"\data\v6v2_backtest.csv")
    print("\nSaved: data/v6v2_backtest.csv")


if __name__ == "__main__":
    main()
