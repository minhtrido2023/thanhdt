#!/usr/bin/env python3
"""Dose-response: would an intraday buy circuit-breaker have helped the LAG book?

EVENT SET (point-in-time, no selection bias): every LAG-book BUY in the PINNED R3 audit
`v23_golive_audit_..._cap50b_ideal_univpit.csv` (2014-01 → 2026-06). Exits taken from the
matching SELL of the same holding_id, so the horizon is the STRATEGY's real horizon, not a
guess.

COUNTERFACTUAL, deliberately biased IN FAVOUR of the breaker:
  A breaker at threshold z trips on day t when  low(t) <= prev_close*(1 - z*rvol_20d(t-1)).
  Baseline = the un-bought tranche fills at exactly `trip_price` (the HIGHEST price still
  reachable after the trip — every later fill would be at or below it, i.e. cheaper). So the
  baseline's measured return is a LOWER bound. Breaker = that capital earns 0 (cash).
  => breaker is +EV only if the measured baseline return is NEGATIVE.
All inputs causal: rvol_20d uses only sessions strictly before t.
"""
import numpy as np, pandas as pd

WC = "/home/trido/thanhdt/WorkingClaude"
AUD = (WC + "/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_"
            "etfliqcustompitg_wtnamecap_liquncap_advprice_exp_cap50b_ideal_univpit.csv")

bars = pd.read_csv("bars_lag_audit.csv", parse_dates=["time"]).sort_values(["ticker", "time"])
g = bars.groupby("ticker", group_keys=False)
bars["prev_close"] = g["close"].shift(1)
bars["ret"] = bars.close / bars.prev_close - 1
bars["rvol_20d"] = g["ret"].apply(lambda s: s.shift(1).rolling(20, min_periods=15).std())
bars["sess"] = g.cumcount()

d = pd.read_csv(AUD, low_memory=False)
tx = d[d.record_type == "TX"].copy()
tx["ymd"] = pd.to_datetime(tx.ymd)
lag = tx[tx.book == "LAG"]
buys = lag[lag.action == "buy"][["ymd", "ticker", "play_type", "holding_id", "shares",
                                 "adj_price", "buy_amount"]].copy()
sells = lag[lag.action == "sell"][["ymd", "ticker", "holding_id", "adj_price"]].copy()
sells = sells.rename(columns={"ymd": "exit_ymd", "adj_price": "exit_price"})
# one holding_id can be sold in tranches -> use the LAST exit (position fully closed)
sells = sells.sort_values("exit_ymd").groupby("holding_id").last().reset_index()
ev = buys.merge(sells[["holding_id", "exit_ymd", "exit_price"]], on="holding_id", how="left")

ev = ev.merge(bars[["ticker", "time", "open", "low", "close", "prev_close", "rvol_20d", "sess"]],
              left_on=["ticker", "ymd"], right_on=["ticker", "time"], how="left")
n0 = len(ev)
ev = ev.dropna(subset=["prev_close", "rvol_20d", "low"])
ev = ev[(ev.rvol_20d > 0) & (ev.prev_close > 0)]
print(f"LAG buy events: {n0} raw -> {len(ev)} with causal rvol_20d + bars "
      f"({ev.ticker.nunique()} tickers, {ev.ymd.min().date()} -> {ev.ymd.max().date()})")
print(f"  exits matched: {ev.exit_price.notna().mean()*100:.1f}%  "
      f"(median hold {(ev.exit_ymd-ev.ymd).dt.days.median():.0f} calendar days)")

# forward prices at fixed horizons, for events whose exit is unmatched / as a cross-check
idx = bars.set_index(["ticker", "sess"])["close"]
for h in (5, 10, 20, 60):
    key = pd.MultiIndex.from_arrays([ev.ticker, ev.sess + h])
    ev[f"px{h}"] = idx.reindex(key).values

ev["is_oos"] = ev.ymd >= "2020-01-01"

def run(z, ret_col):
    trip_px = ev.prev_close * (1 - z * ev.rvol_20d)
    tripped = ev.low <= trip_px
    sub = ev[tripped].copy()
    sub["trip_px"] = trip_px[tripped]
    exitp = sub[ret_col]
    ok = exitp.notna() & (sub.trip_px > 0)
    sub = sub[ok]
    r = (exitp[ok] / sub.trip_px - 1)
    # capital weight = the buy_amount of tripped events (upper bound on capital withheld)
    w = sub.buy_amount.clip(lower=0)
    wr = np.average(r, weights=w) if w.sum() > 0 else np.nan
    return dict(z=z, n_trip=int(tripped.sum()), pct_events=tripped.mean() * 100,
                n_used=len(sub), mean=r.mean() * 100, median=r.median() * 100,
                wmean=wr * 100, hit=(r > 0).mean() * 100,
                pct_capital=w.sum() / ev.buy_amount.clip(lower=0).sum() * 100)

for label, col in (("REAL EXIT (strategy horizon)", "exit_price"),
                   ("fixed T+20", "px20"), ("fixed T+60", "px60")):
    print(f"\n### Baseline return of the tranche the breaker would SKIP — {label}")
    print("     z  trip%  n     capital%   mean%   med%   wmean%   hit%   -> breaker helps?")
    for z in (1.0, 1.5, 2.0, 2.5, 3.0):
        s = run(z, col)
        verdict = "YES (skip is +EV)" if s["mean"] < 0 else "NO — skipping destroys value"
        print(f"  {s['z']:4.1f}  {s['pct_events']:5.1f}% {s['n_used']:4d}  {s['pct_capital']:6.1f}%  "
              f"{s['mean']:+7.2f} {s['median']:+7.2f} {s['wmean']:+7.2f}  {s['hit']:5.1f}   {verdict}")

# unconditional reference
for col, lab in (("exit_price", "REAL EXIT"), ("px20", "T+20"), ("px60", "T+60")):
    r = (ev[col] / ev.close - 1).dropna()
    print(f"\nUnconditional LAG buy, entry at that day's CLOSE, {lab}: "
          f"mean {r.mean()*100:+.2f}%  median {r.median()*100:+.2f}%  n={len(r)}")

print("\n### IS (2014-2019) / OOS (2020+) split, REAL EXIT, mean return of the skipped tranche")
print("     z    IS n   IS mean%    OOS n  OOS mean%")
for z in (1.0, 1.5, 2.0, 2.5, 3.0):
    row = []
    for flag in (False, True):
        e = ev[ev.is_oos == flag]
        tp = e.prev_close * (1 - z * e.rvol_20d)
        t = e[e.low <= tp].copy(); t["trip_px"] = tp[e.low <= tp]
        r = (t.exit_price / t.trip_px - 1).dropna()
        row.append((len(r), r.mean() * 100 if len(r) else np.nan))
    print(f"  {z:4.1f}  {row[0][0]:5d}  {row[0][1]:+8.2f}   {row[1][0]:5d}  {row[1][1]:+8.2f}")
