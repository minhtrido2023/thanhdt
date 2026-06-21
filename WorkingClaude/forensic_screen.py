# -*- coding: utf-8 -*-
"""
forensic_screen.py — Layer 2 of the forensic system: surface CANDIDATES for human review
(it does NOT judge — confirmed cases go into data/forensic_flags.csv by hand).
Targets the KSF signature: 'too-good profitability NOT backed by cash collection' = high ROE/margin
+ receivables exceeding revenue (related-party paper sales) + long cash-cycle + weak multi-yr cash conv.
Output: data/forensic_candidates.csv (ranked), printed for review.
"""
import os, sys, subprocess, tempfile
from io import StringIO
import numpy as np, pandas as pd
WORKDIR = os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude"); sys.path.insert(0, WORKDIR)
def bq(sql):
    f=tempfile.NamedTemporaryFile(mode="w",suffix=".sql",delete=False); f.write(sql); f.close()
    r=subprocess.run(f'cat {f.name} | bq query --quiet --use_legacy_sql=false --project_id=lithe-record-440915-m9 --format=csv --max_rows=5000',capture_output=True,text=True,shell=True); os.unlink(f.name)
    return pd.read_csv(StringIO(r.stdout.strip()))

m = bq("""SELECT f.ticker,
  ROUND(f.ROE_Trailing,3) roe, ROUND(f.NPM_P0,3) npm,
  ROUND(SAFE_DIVIDE(f.AR_P0, NULLIF(f.Revenue_P0+f.Revenue_P1+f.Revenue_P2+f.Revenue_P3,0)),2) ar_rev,
  ROUND(f.CashCycle_P0,0) ccyc,
  ROUND(SAFE_DIVIDE(f.CF_OA_3Y, NULLIF(f.NP_P0+f.NP_P1+f.NP_P2+f.NP_P3,0)),2) cfo3y_np1y,
  ROUND(SAFE_DIVIDE((f.NP_P0+f.NP_P1+f.NP_P2+f.NP_P3)-(f.CF_OA_P0+f.CF_OA_P1+f.CF_OA_P2+f.CF_OA_P3), NULLIF(f.totalAsset_P0,0)),3) accruals_ta
FROM (SELECT t.*,ROW_NUMBER() OVER(PARTITION BY t.ticker ORDER BY t.time DESC) rn FROM tav2_bq.ticker_financial t) f WHERE f.rn=1""")
rt = pd.read_csv(f"{WORKDIR}/data/rating_8l.csv")[["ticker","route","rating","liq_bn"]]
d = rt.merge(m, on="ticker", how="left"); d = d[d.liq_bn >= 3].copy()
try:
    fexist = set(pd.read_csv(f"{WORKDIR}/data/forensic_flags.csv")["ticker"])
except Exception: fexist = set()

# KSF signature: HIGH profitability claim + receivables EXCEED revenue + (long cash-cycle or weak cash conv).
# The high-ROE filter discriminates related-party (genuine high-AR RE has LOW ROE; a 50%-ROE name with
# AR>1x revenue is the anomaly — big profits booked, no cash collected).
d["susp"] = ((d.roe >= 0.15).astype(int)               # claims high profitability
           + (d.ar_rev >= 1.0).astype(int)             # receivables exceed annual revenue
           + (d.ar_rev >= 1.5).astype(int)             # extra weight for extreme
           + (d.ccyc >= 365).astype(int)               # cash tied up > 1yr
           + (d.cfo3y_np1y < 1.0).fillna(False).astype(int))  # 3y cash << 1y profit (low conversion)
cand = d[(d.roe >= 0.15) & (d.ar_rev >= 1.0)].sort_values(["susp","ar_rev"], ascending=False)
cand["already_flagged"] = cand.ticker.isin(fexist)
print(f"### FORENSIC CANDIDATES (high ROE>=15% + AR>=1x revenue = profit-not-collected) — {len(cand)} names ###")
print("  (review footnotes for related-party sales; confirmed -> add to data/forensic_flags.csv)\n")
print(cand[["ticker","route","rating","roe","npm","ar_rev","ccyc","cfo3y_np1y","accruals_ta","susp","already_flagged"]].to_string(index=False))
out = f"{WORKDIR}/data/forensic_candidates.csv"; cand.to_csv(out, index=False)
print(f"\n-> {out}  (susp score 0-5; higher = stronger 'earnings not cash' signature)")
