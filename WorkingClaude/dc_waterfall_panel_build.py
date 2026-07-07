# -*- coding: utf-8 -*-
"""dc_waterfall_panel_build.py (job Taylor_20260706_173317) — build & CACHE the daily
point-in-time double-confirm panel + stock returns + custom30V parking return, reusing the
EXACT functions of converge_portfolio_backtest.py (no re-implementation). RESEARCH ONLY.
Outputs (data/):
  dc_dbl_panel.csv      date x WL ticker booleans (double-confirm: lens BUY AND 8L<=2)
  dc_strong_panel.csv   date x WL ticker booleans (STRONG buy_mode)
  dc_stock_ret.csv      date x WL ticker daily Close returns
  dc_park_ret.csv       date, park_ret  (custom30V vehicle daily return)
"""
import os, sys
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)
import pandas as pd
import converge_portfolio_backtest as cpb

def main():
    basket = cpb.load_parking_basket()
    price = cpb.load_prices(set(cpb.WL_TK) | set(basket["ticker"]))
    fin = cpb.load_financials()
    dt5g = cpb.load_dt5g()
    rat = cpb.load_ratings()
    calendar = pd.DatetimeIndex(sorted(price["time"].unique()))
    calendar = calendar[calendar >= pd.Timestamp(cpb.START)]
    price_wide = price.pivot_table(index="time", columns="ticker", values="Close").reindex(calendar)
    stock_ret = price_wide[cpb.WL_TK].pct_change()
    buy, strong, dbl = cpb.build_signal_panel(price, fin, dt5g, rat, calendar)
    park_ret = cpb.parking_returns(basket, price_wide, calendar)
    dbl.to_csv("data/dc_dbl_panel.csv")
    strong.to_csv("data/dc_strong_panel.csv")
    stock_ret.to_csv("data/dc_stock_ret.csv")
    park_ret.rename("park_ret").to_frame().to_csv("data/dc_park_ret.csv")
    print(f"panel cached: {len(calendar)} sessions, dbl name-days={int(dbl.values.sum())}")

if __name__ == "__main__":
    main()
