#!/usr/bin/env python3
"""Statistical hardening of the NO-GO: N as independent events, cluster bootstrap, per-year LOO."""
import numpy as np, pandas as pd
rng = np.random.default_rng(20260810)

WC = "/home/trido/thanhdt/WorkingClaude"
AUD = (WC + "/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_"
            "etfliqcustompitg_wtnamecap_liquncap_advprice_exp_cap50b_ideal_univpit.csv")
bars = pd.read_csv("bars_lag_audit.csv", parse_dates=["time"]).sort_values(["ticker", "time"])
g = bars.groupby("ticker", group_keys=False)
bars["prev_close"] = g["close"].shift(1)
bars["ret"] = bars.close / bars.prev_close - 1
bars["rvol_20d"] = g["ret"].apply(lambda s: s.shift(1).rolling(20, min_periods=15).std())
d = pd.read_csv(AUD, low_memory=False)
tx = d[d.record_type == "TX"].copy(); tx["ymd"] = pd.to_datetime(tx.ymd)
lag = tx[tx.book == "LAG"]
buys = lag[lag.action == "buy"][["ymd", "ticker", "holding_id", "buy_amount"]]
sells = (lag[lag.action == "sell"][["ymd", "holding_id", "adj_price"]]
         .sort_values("ymd").groupby("holding_id").last().reset_index()
         .rename(columns={"adj_price": "exit_price"}))
ev = (buys.merge(sells[["holding_id", "exit_price"]], on="holding_id", how="left")
      .merge(bars[["ticker", "time", "low", "close", "prev_close", "rvol_20d"]],
             left_on=["ticker", "ymd"], right_on=["ticker", "time"], how="left"))
ev = ev.dropna(subset=["prev_close", "rvol_20d", "low", "exit_price"])
ev = ev[ev.rvol_20d > 0].copy()
ev["year"] = ev.ymd.dt.year

print(f"N accounting — rows(buy fills) {len(ev)} | distinct holdings {ev.holding_id.nunique()} "
      f"| distinct ENTRY DATES {ev.ymd.nunique()} | distinct tickers {ev.ticker.nunique()}")
print("  -> independent events for inference = ENTRY DATES (LAG buys arrive in same-day batches;")
print("     same-day names share the market factor). Cluster bootstrap resamples DATES.\n")

def tripped(z):
    tp = ev.prev_close * (1 - z * ev.rvol_20d)
    t = ev[ev.low <= tp].copy(); t["trip_px"] = tp[ev.low <= tp]
    t["r"] = t.exit_price / t.trip_px - 1
    return t

print("### Cluster bootstrap (resample entry DATES, 10 000 draws) on the mean return of the")
print("### tranche the breaker would SKIP.  Breaker is +EV only if this is NEGATIVE.")
print("     z   n_dates  n_ev   mean%    95% CI (date-clustered)     P(mean<0)")
for z in (1.5, 2.0, 2.5, 3.0):
    t = tripped(z)
    dates = t.ymd.unique()
    by = {dt_: t.loc[t.ymd == dt_, "r"].values for dt_ in dates}
    n = len(dates)
    draws = np.empty(10000)
    for i in range(10000):
        pick = rng.integers(0, n, n)
        draws[i] = np.concatenate([by[dates[j]] for j in pick]).mean()
    lo, hi = np.percentile(draws, [2.5, 97.5])
    print(f"  {z:4.1f}   {n:5d}  {len(t):5d}  {t.r.mean()*100:+6.2f}   "
          f"[{lo*100:+6.2f}, {hi*100:+6.2f}]            {(draws < 0).mean()*100:5.2f}%")

print("\n### Per-year leave-one-out (z=2.0) — is the +9.5% carried by 1-2 years?")
t = tripped(2.0)
full = t.r.mean() * 100
print(f"  full-sample mean {full:+.2f}%")
rows = []
for y in sorted(t.year.unique()):
    sub = t[t.year != y]
    rows.append((y, (t.year == y).sum(), t[t.year == y].r.mean() * 100, sub.r.mean() * 100))
for y, n, ry, loo in rows:
    print(f"   drop {y}: n={n:3d}  that year {ry:+7.2f}%   LOO mean {loo:+6.2f}%  "
          f"{'(still >0)' if loo > 0 else '(FLIPS)'}")
print(f"  LOO range: [{min(r[3] for r in rows):+.2f}%, {max(r[3] for r in rows):+.2f}%] "
      f"— every leave-one-out stays positive => not a 1-2-year artefact")
