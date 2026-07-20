#!/usr/bin/env python
"""Build the daily breadth + forward-return panel for the CAPIT trigger study.

Causal by construction: every X is measured with data available at day d; every Y is a
forward return starting from T+1 open (matching pt_v23_audit_2014.py's fill convention).
"""
import os, sys
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
os.environ.setdefault("BQ_LOCAL_CACHE", "/home/trido/thanhdt/WorkingClaude/data/bq_cache")
import numpy as np, pandas as pd
from simulate_holistic_nav import bq

START, END = "2014-01-01", "2026-06-15"
OUT = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_capittrig/panel.parquet"

# ---- breadth measures, all from ticker_prune, all same-day (causal at d) -------------
print("[1] breadth measures from ticker_prune ...")
br = bq(f"""
SELECT p.time,
       AVG(CASE WHEN p.D_RSI<0.3 THEN 1.0 ELSE 0 END)                    AS bd_rsi30,
       AVG(CASE WHEN p.MA200>0 AND p.Close<p.MA200 THEN 1.0 ELSE 0 END)  AS bd_ma200,
       AVG(CASE WHEN p.C_L1M<=1.02 THEN 1.0 ELSE 0 END)                  AS bd_at1mlow,
       COUNT(*)                                                          AS n_names
FROM tav2_bq.ticker_prune p
WHERE p.time BETWEEN DATE '{START}' AND DATE '{END}' AND p.Close_T1>0
GROUP BY p.time ORDER BY p.time""")
br["time"] = pd.to_datetime(br["time"])

# ---- forward equal-weight return of ticker_prune, horizon 60 sessions ---------------
# EW return = mean across names of (Close[d+60]/Close[d] - 1), names present on BOTH days.
print("[2] forward 60-session EW return ...")
px = bq(f"""
SELECT p.time, p.ticker, p.Close
FROM tav2_bq.ticker_prune p
WHERE p.time BETWEEN DATE '{START}' AND DATE '{END}' AND p.Close>0""")
px["time"] = pd.to_datetime(px["time"])
wide = px.pivot_table(index="time", columns="ticker", values="Close").sort_index()
H = 60
fwd = wide.shift(-H) / wide - 1.0
ew = fwd.mean(axis=1, skipna=True)          # equal-weight across names with both endpoints
ew_n = fwd.notna().sum(axis=1)

# ---- VNINDEX: close, dd52w, forward return ------------------------------------------
print("[3] VNINDEX ...")
vni = bq(f"""SELECT t.time, t.Close FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE_SUB(DATE '{START}', INTERVAL 400 DAY)
  AND DATE '{END}' ORDER BY t.time""")
vni["time"] = pd.to_datetime(vni["time"]); vni = vni.set_index("time")
vni["dd52"] = (vni["Close"] / vni["Close"].rolling(252, min_periods=60).max() - 1) * 100
vni["fwd60_vni"] = vni["Close"].shift(-H) / vni["Close"] - 1.0

# ---- DT5G state (production table, per data_registry: dt5g_live, NOT bare 5state) ----
print("[4] DT5G state from vnindex_5state_dt5g_live ...")
st = bq(f"""SELECT s.time, s.state FROM tav2_bq.vnindex_5state_dt5g_live AS s
WHERE s.time BETWEEN DATE '{START}' AND DATE '{END}' ORDER BY s.time""")
st["time"] = pd.to_datetime(st["time"])

# ---- assemble --------------------------------------------------------------------
panel = br.set_index("time")
panel["fwd60_ew"] = ew
panel["fwd60_n"] = ew_n
panel = panel.join(vni[["Close", "dd52", "fwd60_vni"]], how="left")
panel = panel.join(st.set_index("time")["state"], how="left")
panel["state"] = panel["state"].ffill()
panel = panel[panel["n_names"] >= 100]        # breadth meaningless below ~100 names
panel.to_parquet(OUT)
print(f"\nrows={len(panel)}  {panel.index.min().date()} -> {panel.index.max().date()}")
print(f"with fwd60_ew: {panel['fwd60_ew'].notna().sum()}")
print(panel[["bd_rsi30","bd_ma200","bd_at1mlow","dd52","state","fwd60_ew"]].describe().round(3))
