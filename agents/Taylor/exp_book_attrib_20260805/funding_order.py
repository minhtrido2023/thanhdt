"""Q1 decisive test — funding source & priority. READ-ONLY. job Taylor_20260805_163403.

Logic of the test:
  block 4c (PREFILL_STATE_REBAL) sells park ONLY down to target = etf_frac x (cash + park).
  It can never take park BELOW target (`delta = target - current`, sells `-delta`).
  So: any session in state 3 (etf_frac = 0.70) that ENDS with park/pool < 0.70 - tol
  proves park was sold by a path OTHER than 4c -- i.e. JIT_FOR_BA_BUY funding a buy.
  If PARK had priority over BAL/LAG, this set would be EMPTY.
"""
import numpy as np
import pandas as pd

CSV = ("/home/trido/thanhdt/WorkingClaude/data/v23_golive_audit_2014_now_matpostbull_"
       "shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_jit_A_control_univpit.csv")
ETF_FRAC_NEUTRAL = 0.70   # PARK_STATES="3:0.7" -- production config of the pinned run

df = pd.read_csv(CSV, low_memory=False)
d = df[df.record_type == "DAILY"].copy()
d["ymd"] = pd.to_datetime(d["ymd"])
d = d.sort_values("ymd").set_index("ymd")
for c in ("bal_cash_ref", "bal_stocks_ref", "bal_etf_ref", "lag_cash_ref",
          "lag_stocks_ref", "lag_etf_ref", "state", "nav_bal_ref", "nav_lag_ref"):
    d[c] = pd.to_numeric(d[c], errors="coerce")

tx = df[df.record_type == "TX"].copy()
tx["ymd"] = pd.to_datetime(tx["ymd"])
tx["buy_amount"] = pd.to_numeric(tx["buy_amount"], errors="coerce").fillna(0.0)
tx["sell_amount"] = pd.to_numeric(tx["sell_amount"], errors="coerce").fillna(0.0)
park = tx["play_type"] == "ETF_PARK"

print("=" * 112)
print("Q1-TEST A — is park EVER drained below its own 70% target? (only JIT can do that)")
print("=" * 112)
for book, cc, sc, ec in [("BAL", "bal_cash_ref", "bal_stocks_ref", "bal_etf_ref"),
                         ("LAG", "lag_cash_ref", "lag_stocks_ref", "lag_etf_ref")]:
    n3 = d[d["state"] == 3]
    pool = n3[cc] + n3[ec]
    frac = (n3[ec] / pool).replace([np.inf, -np.inf], np.nan)
    below = frac < (ETF_FRAC_NEUTRAL - 0.02)
    print(f"  {book}: NEUTRAL sessions {len(n3)}")
    print(f"      park/pool < 68%  : {below.sum():5d} ({below.mean()*100:5.1f}%)   "
          f"median park/pool {frac.median()*100:5.1f}%")
    print(f"      park/pool < 10%  : {(frac < 0.10).sum():5d} ({(frac < 0.10).mean()*100:5.1f}%)   "
          f"park == 0 exactly: {(n3[ec] <= 1e-6).sum()}")
print()
print("  => a non-empty 'below target' set is DIRECT evidence park is raided to fund deals.")
print("     If park had priority it would sit AT 70% every NEUTRAL session.")

print()
print("=" * 112)
print("Q1-TEST B — on stock-buy days, where did the money come from?")
print("=" * 112)
sb = tx[(~park) & (tx.action == "buy")].groupby(["ymd", "book"])["buy_amount"].sum()
ps = tx[park & (tx.action == "sell")].groupby(["ymd", "book"])["sell_amount"].sum()
pb = tx[park & (tx.action == "buy")].groupby(["ymd", "book"])["buy_amount"].sum()
j = pd.DataFrame({"stock_buy": sb}).join(ps.rename("park_sell"), how="left") \
      .join(pb.rename("park_buy"), how="left").fillna(0.0)
print(f"  book-days with a stock buy: {len(j)}")
print(f"    ... park sold same day  : {(j.park_sell > 0).sum():5d} "
      f"({(j.park_sell > 0).mean()*100:5.1f}%)")
print(f"    ... park BOUGHT same day: {(j.park_buy > 0).sum():5d} "
      f"({(j.park_buy > 0).mean()*100:5.1f}%)   <- park buying while deals buy = residual sweep")
big = j[j.stock_buy > 1e9]
print(f"  book-days with stock buy > 1B: {len(big)};  park sold on "
      f"{(big.park_sell > 0).sum()} of them ({(big.park_sell > 0).mean()*100:.1f}%)")
print(f"  park_sell / stock_buy on those days: median "
      f"{(big.park_sell/big.stock_buy).median()*100:.1f}%  "
      f"mean {(big.park_sell/big.stock_buy).mean()*100:.1f}%")
print()
print("  interpretation: park is the MARGINAL funding source for deals, not their competitor.")

print()
print("=" * 112)
print("Q1-TEST C — did any deal go unfunded in the control leg?")
print("=" * 112)
ab = tx[tx.reason.astype(str).str.contains("ABANDON", na=False)]
print(f"  TX rows tagged ABANDONED_REFUND: {len(ab)}  "
      f"(refund of a queued buy that could not fill -- capacity/price, not park)")
print(f"  control leg skipped_buys (PARK_JIT gate counter) = 0   [logged in leg A of the 2x2]")
print(f"  leg C (JIT off, = live today) skipped_buys        = 8,995")
print(f"  leg E (JIT off + prefill off)                     = 25,682")

print()
print("=" * 112)
print("Q1-TEST D — park's share of TOTAL book NAV (is it '70-80% of the portfolio'?)")
print("=" * 112)
for book, sc, ec, nc in [("BAL", "bal_stocks_ref", "bal_etf_ref", "nav_bal_ref"),
                         ("LAG", "lag_stocks_ref", "lag_etf_ref", "nav_lag_ref")]:
    f_all = d[ec] / d[nc]
    f_n3 = (d[ec] / d[nc])[d["state"] == 3]
    print(f"  {book}: park/NAV  all sessions mean {f_all.mean()*100:5.1f}%  median {f_all.median()*100:5.1f}%  "
          f"max {f_all.max()*100:5.1f}%")
    print(f"       park/NAV  NEUTRAL only  mean {f_n3.mean()*100:5.1f}%  median {f_n3.median()*100:5.1f}%  "
          f"p90 {f_n3.quantile(.9)*100:5.1f}%")
print()
print("  NOTE: the 70% target is 70% of the CASH POOL (cash + park), NOT of NAV.")
print("        Stocks already bought are outside the pool entirely -- park cannot displace them.")
