# -*- coding: utf-8 -*-
"""probe_impact_today.py — do TAC DONG THAT cua san ADV3T 2 ty/phien len ro ung vien HOM NAY.

Chi DOC, khong sua gi. Hai cau hoi:
  (1) LAG: bao nhieu ung vien qualify hom nay co ADV < 2 ty (tren nen gate ADV>0 dang chay)?
  (2) BAL: SIGNAL_V11 da co san 1e9 cung; bao nhieu dong "today eligible" nam trong bang
      [1e9, 2e9) = phan gate 2 ty THEM vao?
"""
import os, sys
from datetime import datetime, timedelta
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
os.environ.pop("BQ_LOCAL_CACHE", None)

from simulate_holistic_nav import bq
from signal_v11_sql import SIGNAL_V11
from lag_live_schedule import live_lag_candidates

FLOOR = 2e9
TIER_BAL = ["MEGA", "MOMENTUM", "DEEP_VALUE_RECOVERY", "RE_BACKLOG_BUY"]

END = datetime.now().strftime("%Y-%m-%d")
START = (datetime.now() - timedelta(days=120)).strftime("%Y-%m-%d")

# ── (1) LAG ─────────────────────────────────────────────────────────────────
q = live_lag_candidates(start=START)
q = q[q["qualify"]]
tks = sorted(set(q["ticker"]))
asof = pd.Timestamp(bq("SELECT MAX(t.time) AS m FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX'")["m"].iloc[0])
tl = ",".join(f"'{t}'" for t in tks)
a = bq(f"""SELECT t.ticker, t.time, t.Volume_3M_P50,
       t.Volume_3M_P50 * COALESCE(t.Price, t.Close) AS adv_vnd
FROM tav2_bq.ticker AS t
WHERE t.ticker IN ({tl}) AND t.time <= DATE '{asof.date()}'
  AND t.time >= DATE_SUB(DATE '{asof.date()}', INTERVAL 45 DAY)
QUALIFY ROW_NUMBER() OVER (PARTITION BY t.ticker ORDER BY t.time DESC) = 1""")
a["adv_ty"] = a["adv_vnd"] / 1e9
print(f"\n=== (1) LAG — asof {asof.date()} — {len(tks)} ung vien qualify ===")
cur_bad = a[~(a["adv_vnd"] > 0)]
new_bad = a[(a["adv_vnd"] > 0) & (a["adv_vnd"] < FLOOR)]
print(f"  gate HIEN TAI (ADV>0) loai : {len(cur_bad):2d} — {sorted(cur_bad['ticker'])}")
print(f"  gate 2 ty loai THEM        : {len(new_bad):2d} — "
      + ", ".join(f"{r.ticker} {r.adv_ty:.2f}ty" for r in new_bad.sort_values('adv_ty').itertuples()))
print(f"  con lai sau gate 2 ty      : {len(a) - len(cur_bad) - len(new_bad):2d}/{len(tks)}")

# ── (2) BAL ─────────────────────────────────────────────────────────────────
sig = bq(SIGNAL_V11.format(start=START, end=END))
sig["time"] = pd.to_datetime(sig["time"])
LATEST = sig["time"].max()
today = sig[(sig["time"] == LATEST) & sig["play_type"].isin(TIER_BAL)].copy()
today["liq_ty"] = today["liq"] / 1e9
band = today[today["liq"] < FLOOR]
print(f"\n=== (2) BAL — latest signal {LATEST.date()} — {len(today)} dong eligible (TIER_BAL) ===")
print(f"  SIGNAL_V11 da chan san     : liq >= 1e9 (signal_v11_sql.py:143)")
print(f"  bang [1e9, 2e9) = gate THEM: {len(band):2d} — "
      + ", ".join(f"{r.ticker} {r.liq_ty:.2f}ty" for r in band.sort_values('liq_ty').itertuples()))
print(f"  con lai sau gate 2 ty      : {len(today) - len(band):2d}/{len(today)}")
print(f"  min/median liq hom nay     : {today['liq_ty'].min():.2f} / {today['liq_ty'].median():.2f} ty")
# co bao nhieu dong lot vao top-12 select_book that su bi anh huong?
print(f"  (MAX_POS=12; so dong eligible hom nay = {len(today)} "
      f"=> {'HANG DOI DAI hon 12, co the bu slot' if len(today) > 12 else 'NGAN hon 12, KHONG co ai bu slot'})")
