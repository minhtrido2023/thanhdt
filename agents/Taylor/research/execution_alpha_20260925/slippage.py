#!/usr/bin/env python3
"""Measure REAL execution slippage of SpaceX+ZaloPay fills vs several benchmarks.

Benchmarks (all in UNADJUSTED VND, because a fill happens at the raw market
price; BQ's Open/High/Low/Close are ADJUSTED — see the factor below):
  prev_close : unadjusted close of the previous trading day = the DECISION price
               (the plan is built the evening before off that close, and
               send_plan_report goes out 21:00 ICT). Implementation shortfall.
  open       : session open = ARRIVAL price for a bot that places at ~09:05.
               Removes the overnight gap, which the execution path cannot control.
  close      : session close = "would waiting have been better?"
  limit      : our own limit price = how much of the chase cap we consumed.
  range_pos  : (fill - Low) / (High - Low) = where in the day's range we landed.
               Distribution-free; 0 = day's low, 1 = day's high.

Sign convention: slippage_bps > 0 = WORSE for us (bought higher / sold lower).
"""
import os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
WC = "/home/trido/thanhdt/WorkingClaude"

fills = pd.read_csv(os.path.join(HERE, "fills.csv"))
fills["trans_date"] = pd.to_datetime(fills["trans_date"]).dt.date

px = pd.read_parquet(
    os.path.join(WC, "data/bq_cache/ticker/2026.parquet"),
    columns=["time", "ticker", "Open", "High", "Low", "Close", "Price", "Volume"],
)
px["time"] = pd.to_datetime(px["time"]).dt.date
px = px[px["ticker"].isin(fills["ticker"].unique())].sort_values(["ticker", "time"])

# --- un-adjust. Close is adjusted, Price is the unadjusted close of the SAME day.
# The adjustment is multiplicative and applies to the whole bar, so one scalar
# factor per (ticker, day) converts the adjusted bar back to raw VND.
px["adj_f"] = px["Price"] / px["Close"]
bad = px["adj_f"].isna() | (px["adj_f"] <= 0)
px.loc[bad, "adj_f"] = 1.0
for c in ("Open", "High", "Low"):
    px[c + "_raw"] = px[c] * px["adj_f"]
px["Close_raw"] = px["Price"]
px["prev_close_raw"] = px.groupby("ticker")["Price"].shift(1)
px["prev_date"] = px.groupby("ticker")["time"].shift(1)

m = fills.merge(
    px[["time", "ticker", "Open_raw", "High_raw", "Low_raw", "Close_raw",
        "prev_close_raw", "prev_date", "Volume", "adj_f"]],
    left_on=["trans_date", "ticker"], right_on=["time", "ticker"], how="left",
)

unmatched = m[m["Close_raw"].isna()]
print(f"fills total            : {len(m)}")
print(f"unmatched vs BQ bar    : {len(unmatched)}"
      f"  dates={sorted(set(unmatched['trans_date'].astype(str)))}"
      f"  tickers={sorted(set(unmatched['ticker']))}")

m = m[m["Close_raw"].notna()].copy()

# sign: +1 for a BUY (paying more is bad), -1 for a SELL (getting less is bad)
m["sgn"] = np.where(m["side"] == "NB", 1.0, -1.0)

def bps(fill, ref, sgn):
    return sgn * (fill - ref) / ref * 1e4

m["slip_vs_prevclose_bps"] = bps(m["avg_fill_price"], m["prev_close_raw"], m["sgn"])
m["slip_vs_open_bps"]      = bps(m["avg_fill_price"], m["Open_raw"], m["sgn"])
m["slip_vs_close_bps"]     = bps(m["avg_fill_price"], m["Close_raw"], m["sgn"])
m["slip_vs_limit_bps"]     = bps(m["avg_fill_price"], m["limit_price"], m["sgn"])
rng = (m["High_raw"] - m["Low_raw"]).replace(0, np.nan)
m["range_pos"] = (m["avg_fill_price"] - m["Low_raw"]) / rng
# for a sell, "good" is high in the range -> flip so 0=best, 1=worst for us
m["range_pos_cost"] = np.where(m["side"] == "NB", m["range_pos"], 1 - m["range_pos"])
m["adv_frac"] = m["fill_qty"] / m["Volume"].replace(0, np.nan)

m["created_ict"] = (pd.to_datetime(m["created_utc"].str.slice(0, 19))
                    .dt.tz_localize("UTC").dt.tz_convert("Asia/Ho_Chi_Minh"))
m["hhmm"] = m["created_ict"].dt.strftime("%H:%M")

def bucket(t):
    hm = t.hour * 60 + t.minute
    if hm <= 9 * 60 + 15:  return "1_ATO(<=09:15)"
    if hm <  11 * 60 + 30: return "2_morning"
    if hm <  14 * 60 + 30: return "3_afternoon"
    return "4_ATC(>=14:30)"
m["tod_bucket"] = m["created_ict"].apply(bucket)

m.to_csv(os.path.join(HERE, "slippage.csv"), index=False)
print(f"rows with benchmark    : {len(m)}  -> slippage.csv")
