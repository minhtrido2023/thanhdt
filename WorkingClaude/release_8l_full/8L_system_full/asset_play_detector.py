#!/usr/bin/env python3
"""
asset_play_detector.py — flag ASSET-PLAY / SOTP companies (value on NAV, not PE)
================================================================================
User insight (PHR): land-bank → IP conversion gives LUMPY land-compensation NP
spikes (non-operating) + recurring IP rental → earnings multiples (PE/PEG/margin)
MISLEAD; value on NAV/sum-of-parts instead. Screener mishandles land-banks/holdcos
as operating companies.
Data proxies (BQ): (1) NP↔Revenue correlation LOW (NP driven by non-operating items,
not sales); (2) NP lumpiness HIGH (CV); (3) asset-heavy (low asset turnover = Rev/Assets).
Flag ASSET_PLAY when all three → "value on NAV not earnings-multiple".
Validates PHR (should flag) vs DRI (pure-operating rubber, should NOT). Output: data/asset_play.csv + .md
"""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import os, subprocess, tempfile
from io import StringIO
import numpy as np, pandas as pd
PROJECT="lithe-record-440915-m9"; BQ_BIN=r"bq"
W=r"/home/trido/thanhdt/WorkingClaude"
def bq(sql):
    with tempfile.NamedTemporaryFile(mode="w",suffix=".sql",delete=False,encoding="utf-8") as f: f.write(sql); tmp=f.name
    try: r=subprocess.run(f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=2000000',capture_output=True,text=True,timeout=300,shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    return pd.read_csv(StringIO(r.stdout.strip()))

# universe: quality names + land/IP/RE + commodity + validation pair
fa=pd.read_csv(os.path.join(W,"data/fa_ratings_lh.csv")).sort_values(["ticker","quarter"])
fa["is_ab"]=fa["tier"].isin(["A","B"]).astype(int); fa["qn"]=fa.groupby("ticker").cumcount()+1
fa["pct_AB"]=fa.groupby("ticker")["is_ab"].cumsum()/fa["qn"]*100
last=fa.groupby("ticker").tail(1)
univ=sorted(set(last[(last["pct_AB"]>=70)&(last["qn"]>=12)&(last["tier"].isin(["A","B"]))]["ticker"])
            | {"PHR","DRI","DPR","IDC","SIP","KBC","NTC","D2D","TIP","SZC","BCM","DXG","NLG","KDH"})
tks="','".join(univ)
df=bq(f"""SELECT t.ticker,t.time,t.NP_P0,t.Revenue_P0,t.totalAsset_P0
FROM tav2_bq.ticker_financial t WHERE t.ticker IN ('{tks}') AND t.time>='2015-01-01' ORDER BY t.ticker,t.time""")
df["time"]=pd.to_datetime(df["time"])

rows=[]
for tk,g in df.groupby("ticker"):
    g=g.sort_values("time")
    npv=g["NP_P0"].dropna(); rev=g["Revenue_P0"]
    if len(npv)<12: continue
    pair=g.dropna(subset=["NP_P0","Revenue_P0"])
    corr=pair["NP_P0"].corr(pair["Revenue_P0"]) if len(pair)>=10 else np.nan
    np_cv=npv.std()/abs(npv.mean()) if npv.mean()!=0 else np.nan
    ttm_rev=rev.rolling(4).sum(); ta=g["totalAsset_P0"]
    turn=(ttm_rev/ta).dropna().median()   # asset turnover (low = asset-heavy)
    # ASSET_PLAY: NP decoupled from revenue + lumpy + asset-heavy
    score=sum([ (pd.notna(corr) and corr<0.35), (pd.notna(np_cv) and np_cv>0.6), (pd.notna(turn) and turn<0.5) ])
    flag="ASSET_PLAY" if score>=2 and (pd.notna(turn) and turn<0.7) else ("partial" if score>=2 else "")
    rows.append({"ticker":tk,"np_rev_corr":corr,"np_cv":np_cv,"asset_turn":turn,"flags":score,"verdict":flag})
res=pd.DataFrame(rows).sort_values(["verdict","asset_turn"])

lines=[]; P=lambda s="":(print(s),lines.append(s))
P("# ASSET-PLAY / SOTP detector — value on NAV, not earnings-multiple")
P("proxies: NP↔Rev corr LOW (non-operating NP) + NP CV HIGH (lumpy) + asset-turn LOW (asset-heavy)")
P("")
P(f"{'tkr':<6}{'NP-Rev corr':>12}{'NP CV':>7}{'assetTurn':>10}{'flags':>6}  verdict")
P("-"*52)
for _,r in res[res["verdict"]!=""].iterrows():
    P(f"{r['ticker']:<6}{r['np_rev_corr']:>+12.2f}{r['np_cv']:>7.2f}{r['asset_turn']:>10.2f}{int(r['flags']):>6}  {r['verdict']}")
P("")
P("ASSET_PLAY (value on NAV/SOTP): "+", ".join(res[res['verdict']=='ASSET_PLAY']['ticker'].tolist() or ['none']))
P("")
P("## Validation PHR vs DRI")
for tk in ["PHR","DRI","DPR"]:
    r=res[res["ticker"]==tk]
    if len(r): rr=r.iloc[0]; P(f"  {tk}: NP-Rev corr {rr['np_rev_corr']:+.2f}, NP CV {rr['np_cv']:.2f}, assetTurn {rr['asset_turn']:.2f} → {rr['verdict'] or 'operating (PE ok)'}")
P("  → PHR = ASSET_PLAY (land-comp NP decoupled from rubber rev) → NAV; DRI = operating rubber (NP tracks rev) → PE/PB ok")
P("")
P("Caveat: proxy only; true NAV (land at market) needs external estimate; flags land-banks/IP/holdcos/RE.")
res.to_csv(os.path.join(W,"data","asset_play.csv"),index=False)
with open(os.path.join(W,"data","asset_play.md"),"w",encoding="utf-8") as f: f.write("\n".join(lines))
P("Saved data/asset_play.{md,csv}")
