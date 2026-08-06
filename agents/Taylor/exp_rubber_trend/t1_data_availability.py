#!/usr/bin/env python3
"""T1 — how much REAL history do we actually have? (the bug-of-the-day lesson:
never infer coverage from row count)."""
import pandas as pd
W = "/home/trido/thanhdt/WorkingClaude"

d = pd.read_csv(f"{W}/data/rubber_weekly.csv")
d["date"] = pd.to_datetime(d["date"])
real = d[(d["src"] != "wb_seed") & d["rss3_usdkg"].notna()].sort_values("date")
print("=== DAILY feed (data/rubber_weekly.csv) ===")
print(f"rows total in file      : {len(d)}")
print(f"rows RSS3 non-null      : {d['rss3_usdkg'].notna().sum()}")
print(f"rows REAL (src!=wb_seed): {len(real)}")
print(f"first REAL / last REAL  : {real['date'].iloc[0].date()} -> {real['date'].iloc[-1].date()}")
span = (real['date'].iloc[-1] - real['date'].iloc[0]).days
print(f"calendar span REAL      : {span} days  ({span/7:.1f} weeks)")
gaps = real["date"].diff().dt.days.dropna()
print(f"max gap between prints  : {int(gaps.max())} days")
# obs-per-calendar-day rate -> when do we reach 100 / 200 observations?
rate = len(real)/max(span,1)
for need in (100, 200):
    more = (need - len(real))/rate
    eta = real['date'].iloc[-1] + pd.Timedelta(days=more)
    print(f"  MA{need} on DAILY: need {need} obs, have {len(real)}, "
          f"rate {rate:.2f} obs/cal-day -> ETA ~{eta.date()}")

m = pd.read_csv(f"{W}/data/rubber_monthly.csv")
m["dt"] = pd.to_datetime(m["month"].astype(str)+"-15")
m = m[m["price"].notna()].sort_values("dt")
print("\n=== MONTHLY WB Pink Sheet (data/rubber_monthly.csv) ===")
print(f"rows                    : {len(m)}")
print(f"range                   : {m['month'].iloc[0]} -> {m['month'].iloc[-1]}")
mg = m["dt"].diff().dt.days.dropna()
print(f"max gap                 : {int(mg.max())} days (monthly step ~30)  | missing months: "
      f"{int(round(((m['dt'].iloc[-1]-m['dt'].iloc[0]).days/30.44)+1)) - len(m)}")
print(f"price range             : {m['price'].min():.2f} - {m['price'].max():.2f} USD/kg")
print("\nMonthly-equivalent windows (21 trading days/month):")
for dd in (100, 200):
    print(f"  MA{dd} daily  ~= MA{dd/21:.1f} monthly  -> use MA{round(dd/21)} on the monthly series")
