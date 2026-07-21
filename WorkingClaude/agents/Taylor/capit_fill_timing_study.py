#!/usr/bin/env python3
"""capit_fill_timing_study.py — WHEN in the day to fill the CAPIT (bear-washout) basket?

Question (Mike dispatch job=Taylor_20260721_022952): CAPIT currently fills at 11:15 ICT.
Is that optimal, or should down-gap/washout logic push fills to the OPEN (or ATC)?

Production CAPIT trigger = breadth_oversold >= 0.30 where
    breadth_oversold(t) = mean over ticker_prune of 1[D_RSI < 0.30]   (crisis_capitulation_signal.py)
De-cluster with a 30-calendar-day gap = one washout episode = one "fire date".

Two evidence tracks (we lack minute bars for the CAPIT basket names themselves):
  TRACK A (daily OHLC, ALL fire dates, actual liquid quality universe = CAPIT selection pool):
     per name on the fire date:
        o2c = Close/Open - 1      >0 => OPEN cheaper than ATC (buy at open wins vs close)
        o2l = Low/Open  - 1       best-case: how far below open it traded
        c2l = Close/Low - 1       recovery off the low into the close
     This answers OPEN-vs-ATC directly. It CANNOT time the 11:15 window (needs intraday).
  TRACK B (1-minute bars, 16 liquid names, washout dates >= 2023-09-11 only) = intraday SHAPE proxy:
     where in the day does the low sit, and where does 11:15 fall vs open/close/day-low?
     This is a MARKET-WIDE shape proxy (none of the 16 are current CAPIT names) — used only to
     locate the 11:15 window on the average washout-day path, not to price the basket.

No look-ahead: breadth uses same-day cross-section (a market state, not a forward target);
D_RSI is a same-day indicator. profit_* never used. Self-check: this is an execution-price
study, no NAV simulation, so "0 VND" self-check N/A; instead every number is a direct
price ratio auditable from the printed per-episode table.
"""
import warnings; warnings.filterwarnings("ignore")
import os, glob
import duckdb, numpy as np, pandas as pd
pd.set_option("display.width", 220); pd.set_option("display.max_columns", 40); pd.set_option("display.max_rows", 200)

W = "/home/trido/thanhdt/WorkingClaude"
PARQ = f"{W}/data/bq_cache/ticker_prune/*.parquet"
GATE = 0.30
LIQ_FLOOR = 3e9   # CAPIT liquidity floor ~3B/day

con = duckdb.connect()

# ── 1. Reconstruct the production breadth_oversold series + fire dates ─────────────
breadth = con.execute(f"""
  SELECT time,
         AVG(CASE WHEN D_RSI < 0.30 THEN 1.0 ELSE 0 END) AS oversold,
         COUNT(*) AS n
  FROM read_parquet('{PARQ}')
  WHERE Close_T1 > 0 AND D_RSI IS NOT NULL AND time >= DATE '2014-01-01'
  GROUP BY time ORDER BY time
""").df()
breadth["time"] = pd.to_datetime(breadth["time"])
fire = breadth[breadth["oversold"] >= GATE].copy().sort_values("time")
# de-cluster: 30 calendar-day gap = new episode; fire date = first day breadth crossed gate
fire["gap"] = fire["time"].diff().dt.days.fillna(999)
fire["ep"] = (fire["gap"] >= 30).cumsum()
episodes = fire.groupby("ep").agg(fire_date=("time", "first"),
                                  peak_oversold=("oversold", "max"),
                                  ws_days=("time", "size")).reset_index(drop=True)
print("="*100)
print(f"CAPIT FIRE EPISODES (breadth_oversold >= {GATE}, D_RSI<0.30 metric, 30d de-cluster), 2014+")
print("="*100)
print(episodes.assign(peak_oversold=(episodes.peak_oversold*100).round(1)).to_string(index=False))
print(f"\nN episodes = {len(episodes)}")

fire_dates = list(episodes["fire_date"])

# ── 2. TRACK A: daily OHLC of the liquid quality universe on the FILL day (D+1) ────
# CAPIT trigger fires on the washout CLOSE (day D); the plan is generated ~17:30 and the basket
# FILLS on the next session D+1. So the execution-timing question is about D+1's intraday path.
# The deepest-pbz basket is chosen from D's cross-section (pbz uses D's data), then filled on D+1.
qs = ",".join([f"DATE '{d.date()}'" for d in fire_dates])
# pull D (for pbz basket selection) and a window after D to locate D+1 per ticker
allrows = con.execute(f"""
  SELECT ticker, time, Open, High, Low, Close, Close_T1,
         Trading_Value_1M_P50 AS liq, PB, PB_MA5Y, PB_SD5Y
  FROM read_parquet('{PARQ}')
  WHERE Open > 0 AND Close > 0 AND Low > 0 AND Close_T1 > 0
    AND ( time IN ({qs})
          OR time IN ({",".join([f"DATE '{(d+pd.Timedelta(days=k)).date()}'" for d in fire_dates for k in range(1,8)])}) )
""").df()
allrows["time"] = pd.to_datetime(allrows["time"])
# map each fire date D -> its D+1 (first trading day strictly after D present in data)
alldates = np.sort(allrows["time"].unique())
d_to_dp1 = {}
for d in fire_dates:
    later = alldates[alldates > np.datetime64(d)]
    if len(later): d_to_dp1[d] = pd.Timestamp(later[0])
# basket selection uses D's pbz; execution metrics use D+1's OHLC
dayD = allrows[allrows["time"].isin([pd.Timestamp(d) for d in fire_dates])].copy()
dayD["pbz"] = (dayD["PB"] - dayD["PB_MA5Y"]) / dayD["PB_SD5Y"]
dayD = dayD[dayD["liq"] >= LIQ_FLOOR]
dp1_dates = list(d_to_dp1.values())
day = allrows[allrows["time"].isin(dp1_dates)].copy()
day = day[day["liq"] >= LIQ_FLOOR]
day["time"] = pd.to_datetime(day["time"])
day["o2c"] = day["Close"]/day["Open"] - 1        # ATC vs OPEN ; >0 => open cheaper
day["o2l"] = day["Low"]/day["Open"] - 1          # best-case intraday low vs open
day["c2l"] = day["Close"]/day["Low"] - 1         # recovery off low into close
day["day_ret"] = day["Close"]/day["Close_T1"] - 1
day["pbz"] = (day["PB"] - day["PB_MA5Y"]) / day["PB_SD5Y"]

def summ(d, lbl):
    print(f"\n  {lbl:<34} n={len(d):4d} | "
          f"o2c(ATCvsOPEN) {d.o2c.mean()*1e4:+6.1f}bps (t={d.o2c.mean()/(d.o2c.std()/np.sqrt(len(d))):+4.1f}) | "
          f"o2l {d.o2l.mean()*1e4:+6.1f}bps | c2l {d.c2l.mean()*1e4:+6.1f}bps | "
          f"day_ret {d.day_ret.mean()*100:+5.2f}% | %open<close {100*(d.o2c>0).mean():4.0f}%")

print("\n" + "-"*100)
print("TRACK A — daily OHLC on the FILL day D+1. o2c>0 => OPEN cheaper than ATC (favor buy-at-OPEN).")
print("  Basket = deepest-pbz quintile picked from washout-close D, filled on D+1.")
print("  o2l = how far below D+1 open the D+1 day-low traded (best achievable if you nail the low).")
print("-"*100)
summ(day, "ALL liquid (>=3B/day), D+1")
# deepest-pbz quintile picked on D, then look up their D+1 OHLC
basket_rows = []
for d in fire_dates:
    if d not in d_to_dp1: continue
    gD = dayD[(dayD["time"] == pd.Timestamp(d))].dropna(subset=["pbz"])
    if not len(gD): continue
    picks = gD.nsmallest(max(1, int(len(gD)*0.2)), "pbz")["ticker"].tolist()
    gp1 = day[(day["time"] == d_to_dp1[d]) & (day["ticker"].isin(picks))].copy()
    gp1["fire_date"] = d.date()
    basket_rows.append(gp1)
basket = pd.concat(basket_rows) if basket_rows else day.iloc[:0].assign(fire_date=None)
summ(basket, "deepest-pbz quintile (basket proxy), D+1")
print("\n  Per-episode (deepest-pbz quintile) OPEN-vs-ATC on fill day D+1:")
pe = basket.groupby("fire_date").agg(n=("o2c","size"), o2c_bps=("o2c", lambda x: x.mean()*1e4),
                                o2l_bps=("o2l", lambda x: x.mean()*1e4),
                                day_ret=("day_ret", lambda x: x.mean()*100)).round(1)
print(pe.to_string())

# ── 3. TRACK B: minute-bar intraday shape on washout dates (16-name proxy) ─────────
print("\n" + "-"*100)
print("TRACK B — 1-minute intraday SHAPE on washout dates (16 liquid names, market-wide proxy).")
print("  Locates the 11:15 fill window vs open / day-low / close on the average washout path.")
print("-"*100)
mfiles = glob.glob(f"{W}/data/intraday_1m/*.csv")
fdset = set(dp1.date() for dp1 in d_to_dp1.values())   # FILL days D+1
recs = []
shape_rows = []   # normalized path for averaging
for f in mfiles:
    tk = os.path.basename(f)[:-4]
    m = pd.read_csv(f, parse_dates=["time"])
    m["d"] = m["time"].dt.date
    m["hm"] = m["time"].dt.strftime("%H:%M")
    for d, g in m.groupby("d"):
        if d not in fdset: continue
        g = g.sort_values("time")
        op = g["open"].iloc[0]; cl = g["close"].iloc[-1]
        lo = g["low"].min(); hi = g["high"].max()
        lo_time = g.loc[g["low"].idxmin(), "time"].strftime("%H:%M")
        # price at ~11:15 (the current CAPIT fill): last bar at/just before 11:15
        pre = g[g["time"].dt.strftime("%H:%M") <= "11:15"]
        p1115 = pre["close"].iloc[-1] if len(pre) else np.nan
        # price at open-window (09:30) and mid windows for context
        recs.append(dict(ticker=tk, date=d, open=op, close=cl, low=lo,
                         p1115=p1115, lo_time=lo_time,
                         o2c=cl/op-1, o2_1115=p1115/op-1 if p1115==p1115 else np.nan,
                         _1115_vs_low=p1115/lo-1 if p1115==p1115 else np.nan,
                         lo_am=1 if lo_time < "11:30" else 0))
mB = pd.DataFrame(recs)
if len(mB):
    print(f"  Coverage: {mB['date'].nunique()} washout dates x {mB['ticker'].nunique()} names = {len(mB)} name-days")
    print(f"  (washout dates with minute data: {sorted(set(str(d) for d in mB['date']))})")
    print(f"\n  OPEN -> CLOSE (o2c):        {mB.o2c.mean()*1e4:+6.1f} bps   (>0 = recovered into close, OPEN cheaper)")
    print(f"  OPEN -> 11:15 (current):    {mB.o2_1115.mean()*1e4:+6.1f} bps   (>0 = 11:15 higher than open = worse entry)")
    print(f"  11:15 vs day-LOW:           {mB._1115_vs_low.mean()*1e4:+6.1f} bps   (how far above the day's low 11:15 sits)")
    print(f"  day-LOW occurs in MORNING (<11:30): {100*mB.lo_am.mean():.0f}% of name-days")
    print(f"  mean low-time (mode bucket): {mB.lo_time.mode().iloc[0]}")
    print("\n  Per-date (avg across the 16 names):")
    pb = mB.groupby("date").agg(n=("ticker","size"),
            o2c_bps=("o2c", lambda x: x.mean()*1e4),
            o2_1115_bps=("o2_1115", lambda x: x.mean()*1e4),
            _1115_vs_low_bps=("_1115_vs_low", lambda x: x.mean()*1e4),
            lo_am_pct=("lo_am", lambda x: 100*x.mean())).round(1)
    print(pb.to_string())
else:
    print("  No overlap between washout dates and minute-data coverage window.")

print("\nDONE.")
