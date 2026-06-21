#!/usr/bin/env python3
"""build_bank_npl_history.py — POINT-IN-TIME bank rating from REAL vnstock NPL/coverage/ROE history.

The 8L bank lens (rate_bank) needs NPL + coverage + ROE — absent from BQ ticker_financial. vnstock VCI
`finance.ratio(period='quarter')` carries them ~2018→now (32 quarters). This pulls all 18 banks, computes
the 8L bank rating PER QUARTER point-in-time, stamps each with the report-publication date (quarter-end +
45 days), and writes data/bank_rating_history.pkl [ticker, eff_time, quarter, route='BANK', rating].

Merged into the rating history (banks dropped from the BQ-derived pkl, replaced by these) for the
bank/power lens robustness test. Pre-2018 bank quarters have no vnstock data -> left as NaN (neutral).
Run with the python that has vnstock (not the CloudSDK bundled python): `python build_bank_npl_history.py`
"""
import warnings; warnings.filterwarnings("ignore")
import sys, logging, os, time
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
logging.disable(logging.CRITICAL)
import numpy as np, pandas as pd
from vnstock import Vnstock

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
BANKS = ["VCB","BID","CTG","TCB","MBB","ACB","VPB","VIB","HDB","STB","SHB","TPB","MSB","OCB","LPB","EIB","NAB","SSB"]
C_NPL="Non-performing Loan Ratio"; C_COV="Loan Loss Reserves to NPLs"; C_ROE="ROE (%)"

def rate_bank(roe, npl, cov):
    """Ported verbatim from rating_8l.py rate_bank: ROE base, asset-quality (NPL+coverage) differentiator."""
    if pd.isna(roe): return 3
    if roe < 0.08: return 5
    pristine = pd.notna(npl) and npl<=0.012 and pd.notna(cov) and cov>=1.5
    strong   = pd.notna(npl) and npl<=0.020 and pd.notna(cov) and cov>=0.9
    if roe>=0.15 and pristine: return 1
    if roe>=0.14 and strong:   return 2
    if roe>=0.12: return 3
    return 4

def qend_plus45(year, lr):
    ends = {1:f"{year}-03-31", 2:f"{year}-06-30", 3:f"{year}-09-30", 4:f"{year}-12-31"}
    return pd.Timestamp(ends[int(lr)]) + pd.Timedelta(days=45)

def pull(tk, retries=4):
    for attempt in range(retries):
        try:
            df = Vnstock().stock(symbol=tk, source="VCI").finance.ratio(period="quarter", lang="en", dropna=False)
            df = df.copy(); df.columns=[c if isinstance(c,str) else c[-1] for c in df.columns]
            df = df.loc[:, ~pd.Index(df.columns).duplicated()]
            return df
        except Exception as e:
            if attempt==retries-1: print(f"  [skip {tk}] {repr(e)[:60]}", flush=True); return None
            time.sleep(5)

rows = []
for i, tk in enumerate(BANKS):
    df = pull(tk)
    if df is None:
        if i < len(BANKS)-1: time.sleep(3)
        continue
    q = df[df["lengthReport"].isin([1,2,3,4])].sort_values(["yearReport","lengthReport"])
    n = 0
    for _, r in q.iterrows():
        roe = r.get(C_ROE, np.nan); npl = r.get(C_NPL, np.nan)
        cov = abs(r.get(C_COV, np.nan)) if pd.notna(r.get(C_COV, np.nan)) else np.nan
        if pd.isna(roe) and pd.isna(npl): continue
        rating = rate_bank(roe, npl, cov)
        yr, lr = int(r["yearReport"]), int(r["lengthReport"])
        rows.append({"ticker":tk, "eff_time":qend_plus45(yr,lr), "quarter":f"{yr}Q{lr}",
                     "route":"BANK", "rating":rating, "ROE":roe, "NPL":npl, "cov":cov})
        n += 1
    print(f"  {tk}: {n} quarters, last NPL={q[C_NPL].dropna().iloc[-1]*100:.2f}% rating={rows[-1]['rating'] if n else 'NA'}", flush=True)
    if i < len(BANKS)-1: time.sleep(3)

out = pd.DataFrame(rows)
if len(out)==0:
    print("NO DATA (network). Aborting."); sys.exit(1)
out = out.sort_values(["ticker","eff_time"]).drop_duplicates(["ticker","eff_time"], keep="last")
out[["ticker","eff_time","quarter","route","rating"]].to_pickle(os.path.join(WORKDIR,"data","bank_rating_history.pkl"))
out.to_csv(os.path.join(WORKDIR,"data","bank_rating_history.csv"), index=False)
print(f"\nsaved data/bank_rating_history.pkl  rows={len(out)}  banks={out['ticker'].nunique()}")
print("eff_time range:", out["eff_time"].min().date(), "->", out["eff_time"].max().date())
print("rating dist:\n", out["rating"].value_counts().sort_index().to_string())
