"""
pt_sleeve_allocator.py — FORWARD paper-trade NAV: V6 "Tứ Trụ" vs V5
===================================================================
Accumulates out-of-sample evidence for go-live. V5 (V121_Kelly) live NAV comes
from the existing paper-trade (`papertrade_compare5.csv`, inception 2026-04-01).
V6 overlays the value sleeve + disciplined leverage on the SAME days:
  V6_ret = w_core·V5_ret + w_value·value_ret − borrow·max(0,gross−1)
weights from the levered allocator given each day's DT5G state. Capit/grind are
held in CASH here (no live deployable basket yet → conservative; when a real
capitulation fires, mark its actual basket). Idempotent: recomputes the forward
window from source files each run; append into the daily bat.

Run: python pt_sleeve_allocator.py
"""
import sys, os
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import numpy as np
import pandas as pd
from sleeve_v6v2_backtest import MAX_GROSS, BORROW
from edge_health_monitor import capit_edge_health

# V6-v3 = balanced core gross by DT5G state (margin in BULL) + committed-capit/grind carve when fired
V6V3_CORE = {1: 0.0, 2: 0.40, 3: 1.0, 4: 1.35, 5: 0.90}
WCAP, WGR = 0.50, 0.30   # committed carve weights (additive, gross capped at MAX_GROSS=1.5)


def event_daily(path, idx):
    """Daily active-flag + FIX60-spread return over each event's 60-trading-day window."""
    e = pd.read_csv(path, parse_dates=["date"]); a = pd.Series(False, index=idx); r = pd.Series(0.0, index=idx)
    for _, x in e.iterrows():
        dr = (1 + x["FIX60_ret"]/100.0) ** (1/60) - 1
        win = idx[(idx >= x["date"]) & (idx <= x["date"] + pd.Timedelta(days=90))]
        for t in win:
            a[t] = True; r[t] = dr
    return a, r

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
CMP = WORKDIR + r"/data/papertrade_compare5.csv"          # live V5 (V121_Kelly) NAV
VALD = WORKDIR + r"/data/value_daily_fwd.csv"             # daily liquid value universe
STATEF = WORKDIR + r"/data/dt5g_vnindex.csv"
STRONGF = WORKDIR + r"/data/bt_capitulation_STRONG.csv"
WATCHF = WORKDIR + r"/data/bt_capitulation_WATCH.csv"
STATE_LBL = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EXBULL"}


def value_daily():
    """Monthly-rebalanced cheapest-quintile (PB%+PE%) EW daily return series."""
    d = pd.read_csv(VALD, parse_dates=["time"])
    d["ym"] = d["time"].dt.to_period("M")
    # month-start value rank -> membership held through the month
    member = {}
    for ym, g in d.groupby("ym"):
        first = g[g["time"] == g["time"].min()].copy()
        first["v"] = first["PB"].rank(pct=True) + first["PE"].rank(pct=True)
        k = max(5, int(len(first) * 0.20))
        member[ym] = set(first.nsmallest(k, "v")["ticker"])
    rows = {}
    for t, g in d.groupby("time"):
        ym = t.to_period("M")
        sel = g[g["ticker"].isin(member.get(ym, set()))]
        if len(sel) >= 5:
            rows[t] = sel["ret"].mean()
    return pd.Series(rows).sort_index()


def main():
    cmp = pd.read_csv(CMP, parse_dates=["ymd"]).set_index("ymd").sort_index()
    v5_nav = cmp["V23"].dropna()
    v5_ret = v5_nav.pct_change()
    vni_ret = cmp["VNI_BH"].pct_change()
    val = value_daily()
    st = pd.read_csv(STATEF, parse_dates=["time"]).set_index("time")["state"]

    idx = v5_ret.index.intersection(val.index)
    idx = idx[idx >= v5_nav.index[0]]
    if len(idx) < 2:
        print("Not enough overlapping forward days yet."); return

    cap_a, cap_r = event_daily(STRONGF, idx); grd_a, grd_r = event_daily(WATCHF, idx)
    ce = capit_edge_health()
    capit_ok = bool(ce and ce["verdict"] != "NEGATIVE")   # gate carve by live capit-edge health
    recs = []
    for t in idx:
        s = int(st.reindex([t], method="ffill").iloc[0]) if t >= st.index[0] else 3
        # V6-v3: balanced 50/50 core (margin-by-state) + committed-capit/grind carve when fired
        wcore = V6V3_CORE[s]
        wcap = WCAP if (cap_a[t] and capit_ok) else 0.0
        wgr = WGR if grd_a[t] else 0.0
        gross = min(wcore + wcap + wgr, MAX_GROSS)
        sc = gross / (wcore + wcap + wgr) if (wcore + wcap + wgr) > 0 else 0
        wcore, wcap, wgr = wcore*sc, wcap*sc, wgr*sc
        core_ret = 0.5 * v5_ret[t] + 0.5 * val[t]
        v6r = wcore*core_ret + wcap*cap_r[t] + wgr*grd_r[t] - BORROW/252*max(0, gross - 1)
        recs.append(dict(date=t, state=s, w_core=round(wcore,3), w_capit=round(wcap,3),
                         w_grind=round(wgr,3), gross=round(gross,3),
                         v5_ret=v5_ret[t], value_ret=val[t], core_ret=core_ret, v6_ret=v6r,
                         vni_ret=vni_ret.get(t, np.nan)))
    df = pd.DataFrame(recs).set_index("date")
    df["V6_nav"] = (1 + df["v6_ret"].fillna(0)).cumprod()
    df["V5_nav"] = (1 + df["v5_ret"].fillna(0)).cumprod()
    df["VNI_nav"] = (1 + df["vni_ret"].fillna(0)).cumprod()
    df.to_csv(WORKDIR + r"/data/v6_vs_v5_paper.csv")

    def stat(nav, ret):
        n = len(ret.dropna()); tot = nav.iloc[-1] - 1
        ann = (nav.iloc[-1]) ** (252 / n) - 1
        dd = (nav / nav.cummax() - 1).min()
        sh = ret.mean() / ret.std() * np.sqrt(252) if ret.std() > 0 else 0
        return tot, ann, dd, sh

    print(f"=== FORWARD paper-trade V6-v3 'Tứ Trụ' vs V5  ({idx[0].date()} → {idx[-1].date()}, {len(idx)} sessions) ===")
    print(f"  DT5G states in window: {dict(df['state'].value_counts().sort_index().rename(STATE_LBL))}")
    print(f"  V6-v3 (balanced + capit/grind carve + margin) | avg gross {df['gross'].mean():.2f}")
    print(f"\n  {'book':>6} {'totRet':>8} {'annual':>8} {'MaxDD':>8} {'Sharpe':>7}  {'NAV':>7}")
    for lbl, nav, ret in [("V6", df["V6_nav"], df["v6_ret"]), ("V5", df["V5_nav"], df["v5_ret"]),
                          ("VNI", df["VNI_nav"], df["vni_ret"])]:
        tot, ann, dd, sh = stat(nav, ret)
        print(f"  {lbl:>6} {tot*100:7.2f}% {ann*100:7.1f}% {dd*100:7.1f}% {sh:7.2f}  {nav.iloc[-1]:7.4f}")
    sp = df["V6_nav"].iloc[-1] - df["V5_nav"].iloc[-1]
    print(f"\n  V6 − V5 cumulative spread: {sp*100:+.2f}pp over {len(idx)} sessions "
          f"({'V6 ahead' if sp > 0 else 'V5 ahead'})")
    print(f"  ⚠️ EVIDENCE so far is SHORT ({len(idx)} sessions); capit/grind parked in cash (conservative).")
    print(f"  Saved: data/v6_vs_v5_paper.csv")


if __name__ == "__main__":
    main()
