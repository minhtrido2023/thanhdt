#!/usr/bin/env python3
"""(a) left tail of the tranche a breaker would skip — is there an insurance case?
   (b) what the EXISTING `_floor_guard_buy` / `_extreme_regime` rule (floor-proximity,
       exchange-dependent) would have done to the same LAG events."""
import numpy as np, pandas as pd

WC = "/home/trido/thanhdt/WorkingClaude"
AUD = (WC + "/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_"
            "etfliqcustompitg_wtnamecap_liquncap_advprice_exp_cap50b_ideal_univpit.csv")
bars = pd.read_csv("bars_lag_audit.csv", parse_dates=["time"]).sort_values(["ticker", "time"])
g = bars.groupby("ticker", group_keys=False)
bars["prev_close"] = g["close"].shift(1)
bars["ret"] = bars.close / bars.prev_close - 1
bars["rvol_20d"] = g["ret"].apply(lambda s: s.shift(1).rolling(20, min_periods=15).std())

# --- infer each ticker's daily price band (HOSE 7% / HNX 10% / UPCOM 15%) from its own tape
p99 = bars.groupby("ticker")["ret"].quantile(0.999).abs()
mx = bars.groupby("ticker")["ret"].max()
band = pd.Series(np.select([mx > 0.125, mx > 0.085], [0.15, 0.10], default=0.07), index=mx.index)
print("inferred band mix:", band.value_counts().to_dict())

d = pd.read_csv(AUD, low_memory=False)
tx = d[d.record_type == "TX"].copy(); tx["ymd"] = pd.to_datetime(tx.ymd)
lag = tx[tx.book == "LAG"]
buys = lag[lag.action == "buy"][["ymd", "ticker", "holding_id", "buy_amount"]]
sells = (lag[lag.action == "sell"][["ymd", "holding_id", "adj_price"]]
         .sort_values("ymd").groupby("holding_id").last().reset_index()
         .rename(columns={"adj_price": "exit_price"}))
ev = buys.merge(sells[["holding_id", "exit_price"]], on="holding_id", how="left")
ev = ev.merge(bars[["ticker", "time", "low", "close", "prev_close", "rvol_20d"]],
              left_on=["ticker", "ymd"], right_on=["ticker", "time"], how="left")
ev = ev.dropna(subset=["prev_close", "rvol_20d", "low", "exit_price"])
ev = ev[ev.rvol_20d > 0]
ev["band"] = ev.ticker.map(band)

print(f"\nevents: {len(ev)}")
print("\n### (a) LEFT TAIL of the skipped tranche (return from trip price to real exit)")
print("     z   n    p5%     p10%    p25%   median%   mean%   worst%   %<-20%")
for z in (1.5, 2.0, 2.5, 3.0):
    tp = ev.prev_close * (1 - z * ev.rvol_20d)
    t = ev[ev.low <= tp].copy(); t["trip_px"] = tp[ev.low <= tp]
    r = (t.exit_price / t.trip_px - 1) * 100
    if len(r) < 5: continue
    print(f"  {z:4.1f} {len(r):4d} {r.quantile(.05):+7.2f} {r.quantile(.10):+7.2f} "
          f"{r.quantile(.25):+7.2f} {r.median():+8.2f} {r.mean():+7.2f} {r.min():+8.2f} "
          f"{(r < -20).mean()*100:6.1f}")
r_all = (ev.exit_price / ev.close - 1) * 100
print(f"  ALL  {len(r_all):4d} {r_all.quantile(.05):+7.2f} {r_all.quantile(.10):+7.2f} "
      f"{r_all.quantile(.25):+7.2f} {r_all.median():+8.2f} {r_all.mean():+7.2f} "
      f"{r_all.min():+8.2f} {(r_all < -20).mean()*100:6.1f}   <- unconditional (entry at close)")

print("\n### (b) EXISTING rule: `_floor_guard_buy` = last <= floor*(1+extreme_band)")
print("      floor = prev_close*(1-band); band 7/10/15% by exchange")
for eb in (0.03,):
    for lab, mult in (("as coded (band=3%)", 1 + eb),):
        trip = ev.prev_close * (1 - ev.band) * mult
        t = ev[ev.low <= trip].copy(); t["trip_px"] = trip[ev.low <= trip]
        r = (t.exit_price / t.trip_px - 1) * 100
        eqz = ((ev.prev_close - trip) / ev.prev_close / ev.rvol_20d)
        print(f"  {lab}: trips on {len(t)}/{len(ev)} = {len(t)/len(ev)*100:.1f}% of LAG buys | "
              f"equivalent z: median {eqz.median():.2f} (HOSE names {eqz[ev.band==0.07].median():.2f})")
        if len(r) >= 3:
            print(f"      skipped tranche return: mean {r.mean():+.2f}%  median {r.median():+.2f}%  "
                  f"n={len(r)}  worst {r.min():+.2f}%")
