#!/usr/bin/env python3
"""probe_cheapness_payoff.py — does CHEAPNESS (pb_z vs own history) monotonically raise reward AND
win-probability, with RECOVERABLE downside? The data case for betting BIGGER the cheaper it gets
(Kelly: size to edge), with hold-to-recovery as the risk container. (User challenge 2026-06-22.)

THREE views:
  (1) CROSS-SECTIONAL (value_panel ~thousands obs): per-name pb_z bucket -> fwd 3M return + win%.
      Large-sample proof the cheapness->payoff relation is real, not 2 lucky episodes.
  (2) MARKET-LEVEL (monthly median pb_z 2014-2026): bucket -> fwd 12M/24M VNINDEX return + win% +
      worst forward drawdown + recovery (does/when VNINDEX reclaim the entry level within 24M).
  (3) The CHEAPEST historical months + what actually happened next (the bet you'd have made).
Usage: source ./wc_env.sh && $DNA_PYEXE probe_cheapness_payoff.py
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from ic_panel_8l import bq, load

def main():
    # ---------- (1) cross-sectional: per-name pb_z -> fwd-3M payoff ----------
    d = load()
    cs = d[d["pb_z"].notna() & d["profit_3M"].notna()].copy()
    cs["profit_3M"] = pd.to_numeric(cs["profit_3M"], errors="coerce").replace([np.inf,-np.inf], np.nan)
    cs = cs[cs["profit_3M"].notna()]
    bins = [-99,-1.5,-1.0,-0.5,0.0,0.5,1.0,99]
    lbl = ["≤-1.5","-1.5..-1","-1..-.5","-.5..0","0..0.5","0.5..1",">1"]
    cs["bk"] = pd.cut(cs["pb_z"], bins=bins, labels=lbl)
    print("=== (1) CROSS-SECTIONAL: per-name pb_z bucket -> forward 3M return (value_panel, large-n) ===")
    print(f"{'pb_z bucket':10} {'n':>6} {'fwd3M%':>7} {'win%':>5} {'p25%':>6} {'p75%':>6}")
    for b in lbl:
        g = cs[cs["bk"] == b]["profit_3M"]
        if len(g) < 20: continue
        print(f"{b:10} {len(g):>6} {g.mean():>7.1f} {(g>0).mean()*100:>4.0f}% {g.quantile(.25):>6.1f} {g.quantile(.75):>6.1f}")

    # ---------- (2) market-level: monthly median pb_z -> fwd 12M/24M VNINDEX + downside/recovery ----------
    vni = bq("SELECT t.time, ANY_VALUE(t.VNINDEX) v FROM tav2_bq.ticker AS t WHERE t.VNINDEX IS NOT NULL AND t.time>=DATE '2014-01-01' GROUP BY t.time ORDER BY t.time")
    vni["time"] = pd.to_datetime(vni["time"]); vm = vni.set_index("time")["v"].resample("ME").last()
    mc = bq("""SELECT FORMAT_DATE('%Y-%m', t.time) ym,
      APPROX_QUANTILES(SAFE_DIVIDE(t.PB - t.PB_MA5Y, NULLIF(t.PB_SD5Y,0)), 2)[OFFSET(1)] AS med_pbz
    FROM tav2_bq.ticker_prune AS t WHERE t.PB_SD5Y>0 AND t.Trading_Value_1M_P50>3e9 AND t.time>=DATE '2014-01-01'
    GROUP BY ym ORDER BY ym""")
    mc.index = pd.PeriodIndex(mc["ym"], freq="M").to_timestamp(how="end").normalize()
    pbz = mc["med_pbz"].reindex(vm.index).ffill()
    f12 = vm.shift(-12)/vm - 1; f24 = vm.shift(-24)/vm - 1
    # forward worst drawdown + recovery within 24M
    arr = vm.values; ddw = np.full(len(arr), np.nan); rec = np.full(len(arr), np.nan)
    for i in range(len(arr)):
        win = arr[i:i+25]
        if len(win) < 6: continue
        ddw[i] = win.min()/arr[i] - 1
        above = np.where(win >= arr[i])[0]
        rec[i] = (above[above>0][0] if len(above[above>0]) else np.nan)   # months to reclaim entry
    M = pd.DataFrame({"pbz": pbz.values, "f12": f12.values, "f24": f24.values,
                      "ddw": ddw, "rec": rec}, index=vm.index).dropna(subset=["pbz"])
    mb = [-99,-1.0,-0.5,0.0,0.5,99]; ml = ["≤-1.0","-1..-.5","-.5..0","0..0.5",">0.5"]
    M["bk"] = pd.cut(M["pbz"], bins=mb, labels=ml)
    print("\n=== (2) MARKET-LEVEL: median pb_z bucket -> fwd VNINDEX return + worst-DD + recovery (monthly 2014-2026) ===")
    print(f"{'med pb_z':9} {'n':>4} {'fwd12M%':>8} {'win%':>5} {'fwd24M%':>8} {'worstDD%':>9} {'recov-mo':>8}")
    for b in ml:
        g = M[M["bk"] == b]
        if len(g) < 3: continue
        f12g = g["f12"].dropna(); f24g = g["f24"].dropna()
        print(f"{b:9} {len(g):>4} {f12g.mean()*100:>7.1f} {(f12g>0).mean()*100:>4.0f}% "
              f"{f24g.mean()*100:>7.1f} {g['ddw'].mean()*100:>8.1f} {g['rec'].mean():>8.1f}")

    # ---------- (3) the cheapest months + what happened next ----------
    print("\n=== (3) the 8 CHEAPEST months (lowest median pb_z) — the bet & the payoff ===")
    print(f"{'month':8} {'med_pbz':>8} {'fwd12M%':>8} {'fwd24M%':>8} {'worstDD%':>9} {'recov-mo':>8}")
    chp = M.sort_values("pbz").head(8).sort_index()
    for ts, r in chp.iterrows():
        f12s = f"{r.f12*100:+.0f}" if pd.notna(r.f12) else "  -"
        f24s = f"{r.f24*100:+.0f}" if pd.notna(r.f24) else "  -"
        recs = f"{r.rec:.0f}" if pd.notna(r.rec) else "—"
        print(f"{ts.strftime('%Y-%m'):8} {r.pbz:>8.2f} {f12s:>8} {f24s:>8} {r.ddw*100:>8.1f} {recs:>8}")

if __name__ == "__main__":
    main()
