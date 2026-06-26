"""Time-of-day fill backtest: Open vs 11:15 vs ATC vs VWAP, on data/intraday_1m (16 VN names, 1-min).
Validates the Layer-3 v4 HYBRID timing rule (BUY TOP->ATC / non-TOP->11:15; SELL->Open) vs the audited
T+1-Open assumption. Reference = PRIOR-day close (the decision/arrival price; signal at close of T,
execute T+1). For a BUY: lower fill (bps vs prior close) = cheaper = better. For a SELL: higher = better.
Also vs day-VWAP (isolates pure intraday position from the overnight gap)."""
import os, glob
import numpy as np, pandas as pd

DDIR = "data/intraday_1m"
rows = []
for f in sorted(glob.glob(f"{DDIR}/*.csv")):
    tk = os.path.basename(f)[:-4]
    df = pd.read_csv(f); df["time"] = pd.to_datetime(df["time"]); df["date"] = df["time"].dt.date
    df = df.sort_values("time")
    daily_close = df.groupby("date")["close"].last()           # last bar ≈ ATC
    dates = list(daily_close.index)
    hhmm = df["time"].dt.strftime("%H:%M")
    for i in range(1, len(dates)):
        d, prevd = dates[i], dates[i - 1]
        prior_close = daily_close[prevd]
        if prior_close <= 0: continue
        day = df[df["date"] == d]
        if len(day) < 50: continue
        op = day["open"].iloc[0]
        # 11:15 = last bar at or before 11:15 (end of morning-ish)
        m = day[hhmm.loc[day.index] <= "11:15"]
        p1115 = m["close"].iloc[-1] if len(m) else np.nan
        atc = day["close"].iloc[-1]
        vol = day["volume"].sum()
        if vol <= 0 or pd.isna(p1115): continue
        vwap = (((day["high"] + day["low"] + day["close"]) / 3) * day["volume"]).sum() / vol
        rows.append({"tk": tk,
                     "open": (op / prior_close - 1) * 1e4,
                     "t1115": (p1115 / prior_close - 1) * 1e4,
                     "atc": (atc / prior_close - 1) * 1e4,
                     "vwap": (vwap / prior_close - 1) * 1e4,
                     # vs day VWAP (pure intraday position; <0 = below avg = good to BUY)
                     "open_vw": (op / vwap - 1) * 1e4,
                     "t1115_vw": (p1115 / vwap - 1) * 1e4,
                     "atc_vw": (atc / vwap - 1) * 1e4})

R = pd.DataFrame(rows)
print(f"=== Time-of-day fill backtest: {R['tk'].nunique()} names, {len(R)} ticker-days ===\n")
print("--- Fill price vs PRIOR-day close (bps). BUY: lower=cheaper=better | SELL: higher=better ---")
m = R[["open", "t1115", "atc", "vwap"]].mean().round(1)
sd = R[["open", "t1115", "atc", "vwap"]].std().round(1)
for c in ["open", "t1115", "atc", "vwap"]:
    print(f"   {c:7s}: mean {m[c]:>7.1f} bps   std {sd[c]:>6.1f}")
print("\n--- Fill price vs DAY-VWAP (bps; <0 = below day-average = good BUY entry) ---")
mv = R[["open_vw", "t1115_vw", "atc_vw"]].mean().round(1)
for c in ["open_vw", "t1115_vw", "atc_vw"]:
    print(f"   {c:9s}: mean {mv[c]:>7.1f} bps")
print("\n--- BUY: how often is each time the CHEAPEST of {open,11:15,atc}? (% of days) ---")
cheap = R[["open", "t1115", "atc"]].idxmin(axis=1).value_counts(normalize=True).mul(100).round(1)
print(cheap.to_string())
print("\n--- SELL: how often is each the most EXPENSIVE (best to sell)? (% of days) ---")
exp = R[["open", "t1115", "atc"]].idxmax(axis=1).value_counts(normalize=True).mul(100).round(1)
print(exp.to_string())
print("\nINTERP: BUY edge of X over Open = (open_mean - time_mean) bps saved per buy.")
