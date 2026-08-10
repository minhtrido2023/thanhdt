#!/usr/bin/env python3
"""Is the NO-GO robust to WHICH reference the breaker measures the drop from?
Three candidate anchors, same event set, same conservative counterfactual."""
import numpy as np, pandas as pd
WC = "/home/trido/thanhdt/WorkingClaude"
AUD = (WC + "/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_"
            "etfliqcustompitg_wtnamecap_liquncap_advprice_exp_cap50b_ideal_univpit.csv")
bars = pd.read_csv("bars_lag_audit.csv", parse_dates=["time"]).sort_values(["ticker", "time"])
g = bars.groupby("ticker", group_keys=False)
bars["prev_close"] = g["close"].shift(1)
bars["ret"] = bars.close / bars.prev_close - 1
bars["rvol_20d"] = g["ret"].apply(lambda s: s.shift(1).rolling(20, min_periods=15).std())
# trailing anchor = highest close of the 3 sessions before t (proxy for an entry-window anchor
# set on the standard session and carried into sessions 2/3 — the SCL shape)
bars["anchor3"] = g["close"].apply(lambda s: s.shift(1).rolling(3, min_periods=1).max())
d = pd.read_csv(AUD, low_memory=False)
tx = d[d.record_type == "TX"].copy(); tx["ymd"] = pd.to_datetime(tx.ymd)
lag = tx[tx.book == "LAG"]
buys = lag[lag.action == "buy"][["ymd", "ticker", "holding_id"]]
sells = (lag[lag.action == "sell"][["ymd", "holding_id", "adj_price"]]
         .sort_values("ymd").groupby("holding_id").last().reset_index()
         .rename(columns={"adj_price": "exit_price"}))
ev = (buys.merge(sells[["holding_id", "exit_price"]], on="holding_id", how="left")
      .merge(bars[["ticker", "time", "open", "low", "close", "prev_close", "anchor3", "rvol_20d"]],
             left_on=["ticker", "ymd"], right_on=["ticker", "time"], how="left"))
ev = ev.dropna(subset=["prev_close", "anchor3", "rvol_20d", "low", "exit_price", "open"])
ev = ev[ev.rvol_20d > 0]
refs = {"prev close (q.ref)": ev.prev_close,
        "today's OPEN (≈first fill)": ev.open,
        "3-session trailing anchor": ev.anchor3}
print(f"n = {len(ev)} LAG buy events\n")
print("  reference                     z    trip%   n    mean%   median%   worst%   verdict")
for name, R in refs.items():
    for z in (1.5, 2.0, 2.5):
        tp = R * (1 - z * ev.rvol_20d)
        m = ev.low <= tp
        r = (ev.exit_price[m] / tp[m] - 1) * 100
        if len(r) < 5: continue
        v = "skip is +EV" if r.mean() < 0 else "skipping COSTS"
        print(f"  {name:28s} {z:3.1f}  {m.mean()*100:5.1f}% {len(r):4d}  {r.mean():+6.2f}  "
              f"{r.median():+7.2f}  {r.min():+7.2f}   {v}")
    print()
