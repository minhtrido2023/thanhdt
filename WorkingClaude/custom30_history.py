# -*- coding: utf-8 -*-
"""custom30_history.py — PUBLISHER for the "8L custom30" parking basket -> BQ table
`tav2_bq.custom30_8l` (single source of truth; consumers query instead of re-running build_pit).
Construction = custompitg + namecap (cap-weight, each name <=10%; data-chosen 2026-06-15).
Per quarterly rebalance (q2m5): the 30 members with as-of 8L rating, liquidity rank, and the
namecap REFERENCE weight at the rebal date. Run in the daily pipeline (cheap; basket only moves
quarterly + on fa_ratings_8l republish). Lookup today's basket:
  SELECT ticker,weight FROM tav2_bq.custom30_8l
  WHERE rebal_date=(SELECT MAX(rebal_date) FROM tav2_bq.custom30_8l WHERE rebal_date<=CURRENT_DATE())
"""
import os, sys, subprocess
import numpy as np, pandas as pd
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
from simulate_holistic_nav import bq
from pt_dates import detect_end_date
import custom_basket as cb

NAME_CAP = 0.10
START = "2014-01-02"; END = detect_end_date()
# TABLE/CSV env-overridable (2026-06-17): publish custom30V (BASKET_SELECT=yieldcombo) to a shadow table
# custom30v_8l for paper-diff vs the live custom30_8l, until the 2026-06-30 go-live cutover.
TABLE = os.environ.get("CUSTOM30_TABLE", "lithe-record-440915-m9:tav2_bq.custom30_8l")
CSV = os.path.join(WORKDIR, "data", os.environ.get("CUSTOM30_CSV", "custom30_8l_publish.csv"))
BQ = r"bq"

print(f"building 8L custom30 (namecap {NAME_CAP:.0%}) {START} -> {END} ...")
lvl, adv, memdf, bx = cb.build_pit(bq, START, END, quality="none", rebal="q2m5",
                                   gate_rating=3, weight_scheme="namecap")
bx["time"] = pd.to_datetime(bx["time"])
memdf["rebal_date"] = pd.to_datetime(memdf["rebal_date"])
rebals = sorted(memdf["rebal_date"].unique())
adv_s = pd.Series(adv)  # date -> basket ADV (parkable capacity ref)

rows = []
for i, rd in enumerate(rebals):
    rd = pd.Timestamp(rd)
    mem = memdf[memdf["rebal_date"] == rd].sort_values("liq_rank")
    tks = list(mem["ticker"])
    sub = bx[(bx["ticker"].isin(tks)) & (bx["time"] <= rd)]
    mc = sub.sort_values("time").groupby("ticker")["mcap"].last().reindex(tks)
    mc = mc.fillna(0.0)
    base = (mc / mc.sum()).values if mc.sum() > 0 else np.ones(len(tks)) / len(tks)
    w = cb._cap_names(base, NAME_CAP)
    eff_to = (pd.Timestamp(rebals[i + 1]) - pd.Timedelta(days=1)).date() if i + 1 < len(rebals) else ""
    for j, (_, r) in enumerate(mem.iterrows()):
        rows.append(dict(
            rebal_date=rd.date(), effective_from=rd.date(), effective_to=eff_to,
            ticker=r["ticker"], liq_rank=int(r["liq_rank"]),
            rating_8l=(int(r["rating"]) if pd.notna(r["rating"]) else ""),
            weight=round(float(w[j]), 6), quarter=str(r["quarter"])))
df = pd.DataFrame(rows)
df.to_csv(CSV, index=False, encoding="utf-8")
print(f"  {len(df)} rows, {len(rebals)} rebals -> {CSV}")

schema = ("rebal_date:DATE,effective_from:DATE,effective_to:DATE,ticker:STRING,"
          "liq_rank:INTEGER,rating_8l:INTEGER,weight:FLOAT,quarter:STRING")
cmd = f'"{BQ}" load --replace --source_format=CSV --skip_leading_rows=1 {TABLE} "{CSV}" {schema}'
print("  bq load ...")
r = subprocess.run(cmd, capture_output=True, text=True, shell=True)
print(r.stdout.strip()); print(r.stderr.strip())
if r.returncode != 0:
    print("LOAD FAILED"); sys.exit(1)
print(f"OK -> tav2_bq.custom30_8l  (current rebal {pd.Timestamp(rebals[-1]).date()}, {df[df['rebal_date']==pd.Timestamp(rebals[-1]).date()].shape[0]} mã)")
