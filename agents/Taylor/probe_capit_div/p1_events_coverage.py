# -*- coding: utf-8 -*-
"""P1: replicate CAPIT washout events (2014-2026) + golden universe + Dividend_Min3Y coverage."""
import os, sys
import numpy as np, pandas as pd
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
from simulate_holistic_nav import bq

START_DATE, END_DATE = "2014-01-02", "2026-06-15"
WASHOUT_GATE = 0.30

br = bq(f"""SELECT p.time, AVG(CASE WHEN p.D_RSI<0.3 THEN 1.0 ELSE 0 END) oversold
FROM tav2_bq.ticker_prune p
WHERE p.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' AND p.Close_T1>0
GROUP BY p.time ORDER BY p.time""")
br["time"] = pd.to_datetime(br["time"])
ws = br[br["oversold"] >= WASHOUT_GATE].copy().sort_values("time")
ws["g"] = ws["time"].diff().dt.days.fillna(999)
ws["c"] = (ws["g"] >= 30).cumsum()
events = [g.iloc[0]["time"] for _, g in ws.groupby("c")]
print(f"N washout events (30d-clustered) 2014-2026: {len(events)}")
for d in events: print("  ", d.date())

# golden universe + dividend coverage at each event
rows = []
for d in events:
    e = bq(f"""SELECT p.ticker, SAFE_DIVIDE(p.PB-p.PB_MA5Y,p.PB_SD5Y) pbz,
  p.Dividend_Min3Y, p.DY, COALESCE(p.Price,p.Close) px
FROM tav2_bq.ticker_prune p
WHERE p.time = DATE '{d.date()}' AND p.ROE_Min5Y>=0.12 AND p.ROIC5Y>=0.10 AND p.FSCORE>=6
  AND COALESCE(p.Price,p.Close)*p.Volume/1e9 >= 2""")
    if e.empty:
        rows.append(dict(date=d, pool=0, sel=0, div_nonnull=0, div_pos=0)); continue
    g = e[e["pbz"] < -1]; c = e[e["pbz"] < 0]
    pick = g if len(g) >= 3 else (c if len(c) >= 3 else e)
    pick = pick.nsmallest(15, "pbz") if len(pick) > 15 else pick
    rows.append(dict(date=d, pool=len(e), sel=len(pick),
                     div_nonnull=int(pick["Dividend_Min3Y"].notna().sum()),
                     div_pos=int((pick["Dividend_Min3Y"].fillna(0) > 0).sum()),
                     names=",".join(pick["ticker"])))
    pick.to_csv(f"mike/agents/Taylor/probe_capit_div/basket_{d.date()}.csv", index=False)
df = pd.DataFrame(rows)
df.to_csv("mike/agents/Taylor/probe_capit_div/events_coverage.csv", index=False)
print("\n=== COVERAGE of Dividend_Min3Y in the SELECTED golden basket ===")
print(df[["date","pool","sel","div_nonnull","div_pos"]].to_string(index=False))
