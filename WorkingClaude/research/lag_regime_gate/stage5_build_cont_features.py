#!/usr/bin/env python3
"""
stage5_build_cont_features.py — Q2 (job Taylor_20260723_135623)
Build a CONTINUOUS market-feature panel (daily) and attribute PIT to each LAG
event at entry_dt. Adds to the prior events pkl:
  drawdown at 3 lookbacks: dd3m(63d), dd6m(126d), dd12m(252d)
  roc5/roc10/roc20 (VNINDEX % change over N sessions, recent decline speed)
  liq_ratio (market liquidity: VNINDEX Volume / trailing 252d mean — >1 = above LT avg)
  breadth (% ticker_prune above MA200, CAPIT-style, PIT merge_asof)
  (already present: vni_6m, vni_vs_ma200, vni_rsi, dt5g_state)
Writes lag_events_cont.pkl. Run with $DNA_PYEXE.
"""
import warnings; warnings.filterwarnings("ignore")
import pandas as pd, numpy as np, pickle

E = pd.read_pickle("research/lag_regime_gate/lag_events_attributed.pkl")

vni = pickle.load(open("data/_cache_vnindex_2000_now.pkl","rb"))
vni["time"] = pd.to_datetime(vni["time"]); vni = vni.set_index("time").sort_index()
c = vni["Close"]; v = vni["Volume"].astype(float)
F = pd.DataFrame(index=vni.index)
F["dd3m"]  = (c / c.rolling(63,  min_periods=30).max() - 1)*100
F["dd6m"]  = (c / c.rolling(126, min_periods=40).max() - 1)*100
F["dd12m"] = (c / c.rolling(252, min_periods=60).max() - 1)*100
F["roc5"]  = c.pct_change(5)*100
F["roc10"] = c.pct_change(10)*100
F["roc20"] = c.pct_change(20)*100
F["liq_ratio"] = v / v.rolling(252, min_periods=60).mean()      # market liquidity vs LT avg
F["vni_rsi2"]  = vni["D_RSI"]

# breadth (% ticker_prune > MA200) PIT
bp = pd.read_csv("data/breadth_prune_daily.csv", parse_dates=["time"]).sort_values("time")
F = F.reset_index().rename(columns={"time":"time"})
F = pd.merge_asof(F, bp[["time","breadth"]], on="time", direction="backward").set_index("time")
F = F.ffill()

# attribute PIT to events at entry_dt via merge_asof
E = E.sort_values("entry_dt")
E["entry_dt"] = E["entry_dt"].astype("datetime64[ns]")
Fr = F.reset_index().sort_values("time")
Fr["time"] = Fr["time"].astype("datetime64[ns]")
cols = ["dd3m","dd6m","dd12m","roc5","roc10","roc20","liq_ratio","breadth"]
E = pd.merge_asof(E, Fr[["time"]+cols], left_on="entry_dt", right_on="time",
                  direction="backward").drop(columns=["time"])
for col in cols:
    print(f"{col:10s} coverage {E[col].notna().mean():.3f}  "
          f"range [{E[col].min():.2f}, {E[col].max():.2f}]")
E.to_pickle("research/lag_regime_gate/lag_events_cont.pkl")
print("saved lag_events_cont.pkl", E.shape)

# also persist the daily panel for the "current state" Q3 read
F.to_pickle("research/lag_regime_gate/cont_feature_panel.pkl")
print("saved daily panel", F.shape, "->", F.index.max())
