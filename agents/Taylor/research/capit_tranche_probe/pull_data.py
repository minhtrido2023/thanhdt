#!/usr/bin/env python3
"""CAPIT tranche event-study — DATA PULL (job Taylor_20260726_125456).
Replicates the washout-event detection of pt_v23_audit_2014.py and caches the
raw series + per-event golden baskets + forward prices to CSV so the analysis
step re-runs cheaply. RESEARCH-ONLY — reads BQ, writes only to this probe dir.
"""
import subprocess, io, os, sys
import pandas as pd, numpy as np

PROJ = "lithe-record-440915-m9"
OUT  = os.path.dirname(os.path.abspath(__file__))
START, END = "2014-01-02", "2026-07-25"
WASHOUT_GATE = 0.30

def bq(sql):
    r = subprocess.run(["bq","query","--use_legacy_sql=false","--project_id="+PROJ,
                        "--format=csv","--max_rows=2000000", sql],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr); raise SystemExit("bq failed")
    return pd.read_csv(io.StringIO(r.stdout))

# ---- 1. breadth_oversold (identical formula to audit [5]) ----
print("[1] breadth_oversold ...")
br = bq(f"""SELECT p.time, AVG(CASE WHEN p.D_RSI<0.3 THEN 1.0 ELSE 0 END) oversold
FROM tav2_bq.ticker_prune p
WHERE p.time BETWEEN DATE '{START}' AND DATE '{END}' AND p.Close_T1>0
GROUP BY p.time ORDER BY p.time""")
br["time"] = pd.to_datetime(br["time"])
br.to_csv(f"{OUT}/breadth.csv", index=False)
print(f"    {len(br)} days")

# ---- 2. VNINDEX Close (for dd52) + state (DT5G live) ----
print("[2] VNINDEX + state ...")
vni = bq(f"""SELECT t.time, t.Close FROM tav2_bq.ticker t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE_SUB(DATE '{START}', INTERVAL 1100 DAY)
  AND DATE '{END}' ORDER BY t.time""")
vni["time"] = pd.to_datetime(vni["time"])
vni["dd52"] = (vni["Close"]/vni["Close"].rolling(252, min_periods=60).max()-1)*100
vni.to_csv(f"{OUT}/vni.csv", index=False)

st = bq(f"""SELECT s.time, s.state FROM tav2_bq.vnindex_5state_dt5g_live s
WHERE s.time BETWEEN DATE '{START}' AND DATE '{END}' ORDER BY s.time""")
st["time"] = pd.to_datetime(st["time"])
st.to_csv(f"{OUT}/state.csv", index=False)

# ---- 3. detect washout events (cluster >=30d gap, first day = d0) ----
print("[3] detect events ...")
state_ff = st.set_index("time")["state"].reindex(vni["time"], method="ffill")
state_ff = dict(zip(vni["time"], state_ff.values))
vni_i = vni.set_index("time")
ws = br[br["oversold"] >= WASHOUT_GATE].copy().sort_values("time")
ws["g"] = ws["time"].diff().dt.days.fillna(999)
ws["c"] = (ws["g"] >= 30).cumsum()
wdays = set(ws["time"])
vni_dates = list(vni["time"])
di = {d:i for i,d in enumerate(vni_dates)}
events = []
for _, grp in ws.groupby("c"):
    d0 = grp.iloc[0]["time"]
    s = state_ff.get(d0)
    stv = int(s) if pd.notna(s) else 3
    dd_now = float(vni_i["dd52"].reindex([d0], method="ffill").iloc[0])
    # grind: any washout day 20..90 sessions before d0
    grind = False
    i0 = di.get(d0)
    if i0 is not None:
        for back in range(20,91):
            j = i0-back
            if j>=0 and vni_dates[j] in wdays: grind=True; break
    events.append({"date":d0.date(),"state":stv,"dd52":round(dd_now,1),"grind":grind,
                   "peak_oversold":round(grp["oversold"].max(),3),
                   "n_washdays_cluster":len(grp)})
ev = pd.DataFrame(events)
ev.to_csv(f"{OUT}/events.csv", index=False)
print(ev.to_string())

# ---- 4. golden basket per event + forward prices (180 sessions) ----
print("[4] baskets + forward prices ...")
all_names = {}
for _, e in ev.iterrows():
    d = pd.Timestamp(e["date"])
    g = bq(f"""SELECT p.ticker, SAFE_DIVIDE(p.PB-p.PB_MA5Y,p.PB_SD5Y) pbz
FROM tav2_bq.ticker_prune p
WHERE p.time = DATE '{d.date()}' AND p.ROE_Min5Y>=0.12 AND p.ROIC5Y>=0.10 AND p.FSCORE>=6
  AND COALESCE(p.Price,p.Close)*p.Volume/1e9 >= 2""")
    if g.empty:
        print(f"    {d.date()} EMPTY golden universe"); all_names[str(e['date'])]=[]; continue
    gg = g[g["pbz"]<-1]; cc = g[g["pbz"]<0]
    pick = gg if len(gg)>=3 else (cc if len(cc)>=3 else g)
    pick = pick.nsmallest(15,"pbz") if len(pick)>15 else pick
    names = list(pick["ticker"])
    all_names[str(e["date"])] = names
    print(f"    {d.date()} state{e['state']} -> {len(names)} names: {','.join(names)}")

import json
json.dump(all_names, open(f"{OUT}/baskets.json","w"))

# forward prices for every name that appears, from each event date + 200 sessions
uniq = sorted({t for v in all_names.values() for t in v})
if uniq:
    in_list = ",".join(f"'{t}'" for t in uniq)
    px = bq(f"""SELECT t.ticker, t.time, t.Close, t.Open
FROM tav2_bq.ticker t
WHERE t.ticker IN ({in_list}) AND t.time BETWEEN DATE '{START}' AND DATE '{END}'
ORDER BY t.ticker, t.time""")
    px["time"] = pd.to_datetime(px["time"])
    px.to_csv(f"{OUT}/prices.csv", index=False)
    print(f"    prices: {len(px)} rows / {px['ticker'].nunique()} names")
print("DONE pull")
