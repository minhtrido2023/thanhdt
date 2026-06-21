#!/usr/bin/env python3
"""
unified_screener.py — one screener, auto-routes each ticker to the right framework
==================================================================================
Each company type needs its own valuation lens (validated this research stream):
  BANK        (ICB 8355)        → NPL/coverage/CAR GATE + P/B-vs-ROE  (real vnstock data, cached)
  CYCLICAL    (commodity map)   → commodity-trough + stock dislocation (contrarian)
  COMPOUNDER  (everything else) → multi-lens cheap (PEG/pe_z/pb_z) + value-trap guard
Router assigns each ticker, runs its lens, emits a NORMALIZED verdict + action.

Inputs reused: data/bank_lens_v3.csv (banks), data/{rubber,iron_ore,urea,dap,caustic_soda}_monthly.csv
(commodity regime), BQ ticker (compounder + cyclical-stock valuation), fa_ratings_lh (quality gate).
Output: data/unified_screener.md + .csv
"""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import os, subprocess, tempfile
from io import StringIO
import numpy as np, pandas as pd
WORKDIR=os.environ.get("WORKDIR_8L", r"/home/trido/thanhdt/WorkingClaude")
PROJECT="lithe-record-440915-m9"; BQ_BIN=os.environ.get("BQ_BIN", (r"bq" if os.name=="nt" else "bq"))
# commodity cyclicals → which commodity series drives them
COMMODITY_MAP={
 "DRI":"rubber","PHR":"rubber","DPR":"rubber","GVR":"rubber","TRC":"rubber","HRC":"rubber",
 "HPG":"iron_ore","HSG":"iron_ore","NKG":"iron_ore","SMC":"iron_ore","POM":"iron_ore",
 "DCM":"urea","DPM":"urea",
 "DDV":"dap","LAS":"dap","DGC":"dap",  # DGC = phosphate-chain proxy (real P4 has no series)
 "CSV":"caustic_soda"}  # CSV = chlor-alkali (NaOH+chlorine+PVC), NOT dap fertilizer — own caustic-soda cycle

# SUGAR group (ICB 3577) — a TREND cyclical, NOT contrarian (validated sugar_cyclical.py 2026-06):
# WEAK+deep-dd = WORST bucket (1Y -4%/41%win), GOOD+deep-dd = BEST (+29%/72%win); spread negative
# all 5/5 tickers. Structural deficit + import protection (quota + anti-dumping) => high prices
# PERSIST and troughs are long value-traps (cane acreage rebuilds slowly). So BUY on a GOOD regime
# (ideally a stock pullback = dip-in-uptrend), AVOID/WAIT on WEAK. Driver = world sugar (USD/kg).
# DO NOT add to COMMODITY_MAP: eval_cyclical()'s contrarian logic would invert the signal.
SUGAR_SET={"SLS","SBT","LSS","KTS","QNS"}  # QNS hybrid (Vinasoy ~half profit → weaker pure-sugar read)
SUGAR_AD_EXPIRY="2026-06-15"  # Thai anti-dumping 47.64% end-of-term; MOIT review pending (binary catalyst)

# OIL & GAS transmission lens (2026-06-05): Brent feeds each chain-position DIFFERENTLY
# (BSR=direction/instant inventory+crack · PVD=level/long-lag, P/B leads earns 4Q · GAS=level/short-lag,
# stable margin · PLX & LPG-downstream=INVERSE margin · DPM/DCM=energy co-cyclical · tankers=freight not oil).
# Overlay only (annotates transmission); evidence in oil_8l_framework.md. Registry: data/oil_transmission_map.csv.
try:
    from oil_transmission import load_oil_map, oil_tag, OIL_TICKERS
    OILMAP=load_oil_map(WORKDIR); OIL_SET=set(OIL_TICKERS)
except Exception as _e:
    OILMAP={}; OIL_SET=set(); oil_tag=lambda *a,**k:""; print("OIL lens skipped:",_e)
# FREIGHT-RATE lens (2026-06-05): VN shipping tracks global freight per SEGMENT (bulk→BDI strong/loss-prone,
# container→SCFI HAH boom 2021-22 but fleet now decouples, tanker→BDTI charter-buffered, ports=volume not rate).
# Registry data/freight_map.csv; live BDI from real feed (fetch_bdi_daily.py). Evidence shipping_freight_sensitivity.py.
try:
    from freight_map import load_freight_map, freight_tag, current_bdi, FREIGHT_TICKERS
    FMAP=load_freight_map(WORKDIR); FREIGHT_SET=set(FREIGHT_TICKERS); _BDI=current_bdi(WORKDIR)
except Exception as _e:
    FMAP={}; FREIGHT_SET=set(); freight_tag=lambda *a,**k:""; _BDI=(None,None,None); print("FREIGHT lens skipped:",_e)

# ---- EVENT overrides: temporary event-driven disruptions (NOT structural) ----
# Mechanical VALUE_TRAP/cmdty flags can't see a one-off event + forward recovery.
# Manually-curated; each needs independent verification (WebSearch) before trusting.
EVENTS={
 "DGC":{"type":"SPECIAL_SITUATION","note":"Q1/26 −49% NP: Khai truong 25 apatite mine SUSPENDED (investigation) + chairman family (Dao Huu Huyen+son) prosecuted/arrested (illegal mining/waste). New board=founder family. Moat intact (dominant VN phosphorus, sells out). SWING VAR=mine-access restoration + sulfur cost (spiked ~2x ME war). Bull: temp event, franchise irreplaceable (Buffett bad-quarter). Bear: mine access permanently curtailed=structural raw-material loss."},
 "PAT":{"type":"SPECIAL_SITUATION","note":"DGC-group apatite arm; same event (mine/maintenance/legal). Q1/26 disrupted, ROE_tr still 46%. Same swing vars as DGC."},
}

def bq(sql):
    with tempfile.NamedTemporaryFile(mode="w",suffix=".sql",delete=False,encoding="utf-8") as f: f.write(sql); tmp=f.name
    try: r=subprocess.run(f'{"type" if os.name=="nt" else "cat"} "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=100000',capture_output=True,text=True,timeout=300,shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    return pd.read_csv(StringIO(r.stdout.strip()))

# ---- banks (cached real-data lens v3) ----
bank=pd.read_csv(os.path.join(WORKDIR,"data","bank_lens_v3.csv"))
bank_set=set(bank["ticker"])
# ---- POWER lens (ICB 7535, debt-paydown lifecycle — own sector lens like banks) ----
try:
    power=pd.read_csv(os.path.join(WORKDIR,"data","power_lens.csv"))
    POWER_set=set(power["ticker"])-bank_set
    POWERD={r["ticker"]:(r["verdict"],r["action"],r["detail"],r["liqB"]) for _,r in power.iterrows()}
except Exception: POWER_set=set(); POWERD={}
# engine classification (cash-machine + reinvestment-runway + ROIC) for compounders
try:
    eng=pd.read_csv(os.path.join(WORKDIR,"data","engine_class.csv"))
    ENGINE={r["ticker"]:(r["engine"],bool(r["machine"])) for _,r in eng.iterrows()}
except Exception: ENGINE={}
# refinement 1: structural overlay for cyclicals (percentile × supply-structure × oil)
try:
    cs=pd.read_csv(os.path.join(WORKDIR,"data","cyclical_structural.csv"))
    CYC_STRUCT={r["ticker"]:(r["verdict"],r["structure"],r["pctile"],r["commodity"]) for _,r in cs.iterrows()}
except Exception: CYC_STRUCT={}
# refinement 2: asset-play / SOTP names (value on NAV not earnings) — exclude banks
try:
    ap=pd.read_csv(os.path.join(WORKDIR,"data","asset_play.csv"))
    ASSET_PLAY=set(ap[ap["verdict"]=="ASSET_PLAY"]["ticker"]) - bank_set
except Exception: ASSET_PLAY=set()
# refinement 3 (2026-05-31): L5 margin-cycle overlay — for commodity CONSUMERS, a low PE on
# PEAK-cycle margins is a trap (earnings cyclically inflated by cheap input). Single-quarter
# PEG can mislabel a peak-margin name as cheap (or unfairly ding one on a base effect, e.g.
# BMP vs NTP). Margin-cycle position (GPM vs own history) is the structural read.
try:
    mc=pd.read_csv(os.path.join(WORKDIR,"data","margin_cycle_detector.csv"))
    MARGIN={r["ticker"]:(r["cycle"],round(r["GPM_pctile"],2)) for _,r in mc.iterrows()}
    MARGIN_INPUT={r["ticker"]:r["input"] for _,r in mc.iterrows()}
    # group same-input commodity-consumers (paired-peer overlay). A peer at MARGIN_PEAK is an
    # early-warning for followers sharing the input (BMP→NTP PVC lead-lag ~1q validated).
    INPUT_PEAKERS={}  # input -> [tickers at MARGIN_PEAK]
    for _,r in mc.iterrows():
        if r["cycle"]=="MARGIN_PEAK": INPUT_PEAKERS.setdefault(r["input"],[]).append(r["ticker"])
except Exception: MARGIN={}; MARGIN_INPUT={}; INPUT_PEAKERS={}
# refinement 4 (2026-05-31, user caught HAH): FREIGHT-RATE cyclicals (shipping) earn on freight/charter
# RATES, not a commodity input → L5 margin_cycle_detector (commodity-consumers only) misses them, yet
# low PE on PEAK-freight earnings is the same cyclical trap (HAH: 2 boom-busts in 5y; NPM pctile 0.95 now).
# Inject their OWN-history NPM percentile into MARGIN so the existing L5 overlay (downgrade+penalty) fires.
RATE_CYCLICAL=["HAH","VOS","VTO","GMD","VSC","SGP","HMH","VNA"]
try:
    _rc=bq(f"""WITH h AS (SELECT x.ticker, x.time, x.NPM_P0,
       PERCENT_RANK() OVER(PARTITION BY x.ticker ORDER BY x.NPM_P0) pct,
       ROW_NUMBER() OVER(PARTITION BY x.ticker ORDER BY x.time DESC) rn
       FROM tav2_bq.ticker_financial x WHERE x.ticker IN ('{"','".join(RATE_CYCLICAL)}') AND x.NPM_P0 IS NOT NULL AND x.time>='2017-01-01')
    SELECT h.ticker tk, MAX(CASE WHEN h.rn=1 THEN h.pct END) pct FROM h GROUP BY h.ticker""")
    for _,_r in _rc.iterrows():
        _p=round(float(_r["pct"]),2); MARGIN_INPUT[_r["tk"]]="freight rate"
        if _p>=0.85: MARGIN[_r["tk"]]=("MARGIN_PEAK",_p)
        elif _p<=0.20: MARGIN[_r["tk"]]=("MARGIN_BOTTOM",_p)
except Exception as e: print("RATE_CYCLICAL inject skipped:",e)

# ---- quality universe (compounder candidates) from fa_ratings_lh ----
fa=pd.read_csv(os.path.join(WORKDIR,"fa_ratings_lh.csv")).sort_values(["ticker","quarter"])
# FIX (2026-05-31, TV1 case): 25/687 names have NaN score in the latest lh snapshot → default to tier E
# (data-pipeline artifact, NOT a real fundamental fail). Fall back to the main 7-axis fundamental_rating
# tier where the lh score is NaN, so a broken latest-quarter doesn't wrongly exclude a good company.
try:
    _m=pd.read_csv(os.path.join(WORKDIR,"fundamental_rating_latest.csv")).sort_values(["ticker","quarter"]).groupby("ticker").tail(1).set_index("ticker")["tier"].to_dict()
    _nan=fa["score"].isna()
    fa.loc[_nan,"tier"]=fa.loc[_nan,"ticker"].map(_m).fillna(fa.loc[_nan,"tier"])
    print(f"FA NaN-score fallback applied to {int(_nan.sum())} rows (main-model tier)")
except Exception as _e: print("FA fallback skipped:",_e)
fa["is_ab"]=fa["tier"].isin(["A","B"]).astype(int); fa["qn"]=fa.groupby("ticker").cumcount()+1
fa["pct_AB"]=fa.groupby("ticker")["is_ab"].cumsum()/fa["qn"]*100
last=fa.groupby("ticker").tail(1)
quality=set(last[(last["pct_AB"]>=70)&(last["qn"]>=12)&(last["tier"].isin(["A","B"]))]["ticker"])

# universe = quality compounders ∪ commodity cyclicals ∪ banks ∪ power ∪ sugar (trend-cyclical)
universe=sorted(quality | set(COMMODITY_MAP) | bank_set | POWER_set | SUGAR_SET | OIL_SET | FREIGHT_SET)
nonbank=[t for t in universe if t not in bank_set and t not in POWER_set]
tks="','".join(nonbank)

# ---- pull valuation for non-bank tickers (+ SOLVENCY fields for survival gate) ----
val=bq(f"""WITH latest AS (SELECT t.ticker,MAX(t.time) mx FROM tav2_bq.ticker_1m t WHERE t.ticker IN ('{tks}') AND t.PB IS NOT NULL GROUP BY t.ticker),
hi AS (SELECT t.ticker,MAX(t.Close) hi52 FROM tav2_bq.ticker t WHERE t.ticker IN ('{tks}') AND t.time>=DATE_SUB(CURRENT_DATE(),INTERVAL 365 DAY) GROUP BY t.ticker),
finq AS (SELECT f.ticker, f.time, f.NP_P0, f.NP_P1, f.NP_P2, f.NP_P3, f.NP_P4, f.NP_P5, f.NP_P6, f.NP_P7,
  f.CF_OA_P0, f.CF_OA_P1, f.CF_OA_P2, f.CF_OA_P3,
  f.CF_Invest_P0, f.CF_Invest_P1, f.CF_Invest_P2, f.CF_Invest_P3, f.OShares, f.CR_P0, f.CashR_P0,
  f.UnearnRev_P0, f.UnearnRev_P4, f.STLTDebt_Eq_P0, f.IntCov_P0, f.FSCORE,
  ROW_NUMBER() OVER (PARTITION BY f.ticker ORDER BY f.time DESC) rn
  FROM tav2_bq.ticker_financial f WHERE f.ticker IN ('{tks}')),
fin AS (SELECT finq.ticker,
  SUM(CASE WHEN finq.NP_P0<0 THEN 1 ELSE 0 END) neg_q8,
  MAX(CASE WHEN finq.rn=1 THEN finq.STLTDebt_Eq_P0 END) DebtEq,
  MAX(CASE WHEN finq.rn=1 THEN finq.IntCov_P0 END) IntCov,
  MAX(CASE WHEN finq.rn=1 THEN finq.FSCORE END) FSCORE,
  -- TTM growth (P0..P3 vs P4..P7) removes single-quarter base-effect noise in PEG
  MAX(CASE WHEN finq.rn=1 THEN SAFE_DIVIDE(finq.NP_P0+finq.NP_P1+finq.NP_P2+finq.NP_P3,
       NULLIF(finq.NP_P4+finq.NP_P5+finq.NP_P6+finq.NP_P7,0))-1 END) ttm_g,
  -- LIQUIDITY: TTM operating cash flow (raw VND) + current ratio + cash ratio (working-capital health)
  MAX(CASE WHEN finq.rn=1 THEN finq.CF_OA_P0+finq.CF_OA_P1+finq.CF_OA_P2+finq.CF_OA_P3 END) ttm_cfo,
  -- CASH YIELD inputs: TTM capex (CF_Invest, negative) + shares for market cap (IC-validated cfo_yield)
  MAX(CASE WHEN finq.rn=1 THEN finq.CF_Invest_P0+finq.CF_Invest_P1+finq.CF_Invest_P2+finq.CF_Invest_P3 END) ttm_capex,
  MAX(CASE WHEN finq.rn=1 THEN finq.OShares END) OShares,
  MAX(CASE WHEN finq.rn=1 THEN finq.CR_P0 END) CR, MAX(CASE WHEN finq.rn=1 THEN finq.CashR_P0 END) CashR,
  -- ASSET-PLAY NAV: deferred-revenue backlog (pre-sold land-lease cash) — IC-validated +0.22@1Y, orthogonal to PB
  MAX(CASE WHEN finq.rn=1 THEN finq.UnearnRev_P0 END) un0, MAX(CASE WHEN finq.rn=1 THEN finq.UnearnRev_P4 END) un4
  FROM finq WHERE finq.rn<=8 GROUP BY finq.ticker)
SELECT t.ticker, ROUND(t.PE,1) PE, ROUND((t.PE-t.PE_MA5Y)/NULLIF(t.PE_SD5Y,0),2) pe_z,
 ROUND(t.PB,2) PB, ROUND((t.PB-t.PB_MA5Y)/NULLIF(t.PB_SD5Y,0),2) pb_z,
 ROUND(SAFE_DIVIDE(t.NP_P0,t.NP_P4)-1,3) np_yoy, ROUND(fin.ttm_g,3) ttm_g, ROUND(t.ROE5Y*100,1) ROE5Y,
 ROUND(t.Close/NULLIF(hi.hi52,0)-1,3) dd52,
 ROUND(GREATEST(t.Volume_3M_P50, t.Volume_1M)*t.Close/1e9,1) liqB,
 ROUND(t.Volume_3M_P50*t.Close/1e9,1) liq3m, ROUND(t.Volume_1M*t.Close/1e9,1) liq1m,
 fin.neg_q8, ROUND(fin.DebtEq,2) DebtEq, ROUND(fin.IntCov,2) IntCov, fin.FSCORE,
 ROUND(fin.ttm_cfo/1e9,0) ttm_cfo_bn, ROUND(fin.CR,2) CR, ROUND(fin.CashR,2) CashR,
 ROUND(SAFE_DIVIDE(fin.ttm_cfo, t.Close*fin.OShares),4) cfo_yield,
 ROUND(SAFE_DIVIDE(fin.ttm_cfo+fin.ttm_capex, t.Close*fin.OShares),4) fcf_yield,
 ROUND(SAFE_DIVIDE(fin.un0, t.Close*fin.OShares),3) un_lvl, ROUND(SAFE_DIVIDE(fin.un0,NULLIF(fin.un4,0))-1,2) un_yoy
FROM tav2_bq.ticker_1m t JOIN latest l ON l.ticker=t.ticker AND l.mx=t.time JOIN hi ON hi.ticker=t.ticker
LEFT JOIN fin ON fin.ticker=t.ticker""")
val=val.set_index("ticker")

# augment ASSET_PLAY set (follow-up #1): deferred revenue >> equity = IP-lease/pre-sold model BY
# DEFINITION, regardless of the np-corr/cv/turn detector (which under-tagged SIP). UnearnRev/Equity
# = un_lvl × PB (since un_lvl=UnearnRev/MktCap and MktCap=Equity×PB). Threshold 0.5 (deferred rev ≥ half equity).
for _t in val.index:
    _ul=val.loc[_t].get("un_lvl"); _pb=val.loc[_t].get("PB")
    if pd.notna(_ul) and pd.notna(_pb) and _pb>0 and _ul*_pb>=0.5 and _t not in bank_set:
        ASSET_PLAY.add(_t)

# ---- SOLVENCY / SURVIVAL gate (missing-gate fix, 2026-05-31) ----
# Contrarian "buy the cyclical trough" ASSUMES the company survives to the upturn.
# A name with negative/destroyed equity or sustained losses it can't service is a
# falling-knife (e.g. POM: 8/8 loss quarters, equity NEGATIVE -> PB=0, IntCov null).
# This gate applies to ALL non-bank routes (banks have their own NPL/CAR gate).
def distressed(t):
    if t not in val.index: return (False,"")
    r=val.loc[t]; pb=r["PB"]; deq=r.get("DebtEq"); ic=r.get("IntCov"); nq=r.get("neg_q8")
    cfo=r.get("ttm_cfo_bn"); cr=r.get("CR")
    if pd.notna(pb) and pb<=0: return (True,"PB<=0 (equity destroyed/negative)")
    if pd.notna(deq) and deq<0: return (True,f"negative equity (Debt/Eq {deq})")
    if pd.notna(nq) and nq>=6 and (pd.isna(ic) or ic<1):
        return (True,f"{int(nq)}/8 loss quarters + cannot service interest (IntCov {ic})")
    # LIQUIDITY/working-capital crunch: negative working capital (CR<1) AND burning operating cash
    # (TTM CFO<0) => can't self-fund, needs external rescue (e.g. SMC: CR 0.62, CFO −365bn, rights issue).
    if pd.notna(cr) and cr<1.0 and pd.notna(cfo) and cfo<0:
        return (True,f"liquidity crunch: Current Ratio {cr}<1 (negative working capital) + TTM CFO {cfo:.0f}bn burn -> external-rescue risk")
    return (False,"")

# ---- commodity regimes ----
comm_state={}
for com in set(COMMODITY_MAP.values()):
    c=pd.read_csv(os.path.join(WORKDIR,"data",f"{com}_monthly.csv")); c.columns=["m","p"]
    c["med36"]=c["p"].rolling(36,min_periods=18).median()
    c["pctile5y"]=c["p"].rolling(60,min_periods=24).apply(lambda x:(x.iloc[-1]>=x).mean())
    comm_state[com]={"good":bool(c["p"].iloc[-1]>c["med36"].iloc[-1]),"pctile":float(c["pctile5y"].iloc[-1])}
# sugar regime (own series — trend-cyclical, deliberately NOT in COMMODITY_MAP)
_sg=pd.read_csv(os.path.join(WORKDIR,"data","sugar_monthly.csv")); _sg.columns=["m","p"]
_sg["med36"]=_sg["p"].rolling(36,min_periods=18).median()
_sg["pctile5y"]=_sg["p"].rolling(60,min_periods=24).apply(lambda x:(x.iloc[-1]>=x).mean())
sugar_state={"good":bool(_sg["p"].iloc[-1]>_sg["med36"].iloc[-1]),"pctile":float(_sg["pctile5y"].iloc[-1]),"price":float(_sg["p"].iloc[-1])}

# ---- per-ticker evaluation ----
def eval_compounder(t):
    if t not in val.index: return ("COMPOUNDER","?","no data","")
    r=val.loc[t]; pe,pez,pbz,npy,roe,dd=r["PE"],r["pe_z"],r["pb_z"],r["np_yoy"],r["ROE5Y"],r["dd52"]
    # growth for PEG/trap = TTM (4q vs prior 4q) to remove single-quarter base-effect noise;
    # fall back to single-quarter YoY only if TTM unavailable.
    ttm=r.get("ttm_g"); g=ttm if pd.notna(ttm) else npy
    peg=(pe/(g*100)) if (pd.notna(g) and g>0 and pe>0) else np.nan
    cfy=r.get("cfo_yield")  # IC-validated cash-yield (TTM CFO / market cap); orthogonal to PB
    hist=(pez<-1) or (pbz<-1); pegc=(0<peg<=1) if pd.notna(peg) else False; absc=(pe<10) or (r["PB"]<1.2)
    cashc=(pd.notna(cfy) and cfy>=0.12)  # 4th cheap-lens: strong operating-cash yield
    trap=(pd.notna(g) and g<-0.15)
    n=sum([hist,pegc,absc,cashc])
    if trap and (hist or absc): v="VALUE_TRAP"; act="AVOID"
    elif n>=2: v="CHEAP_QUALITY"; act="BUY-zone"
    elif n==1: v="CHEAP_1lens"; act="WATCH"
    else: v="NOT_CHEAP"; act="WATCH" if roe>=12 else "PASS"
    gtag="ttm" if pd.notna(ttm) else "1q"
    pbtag=f" PB{r['PB']:.2f} pb_z{pbz:+.1f}" if (pd.notna(r['PB']) and pd.notna(pbz)) else (f" PB{r['PB']:.2f}" if pd.notna(r['PB']) else "")
    fcy=r.get("fcf_yield")
    cytag=f" CFOyld{cfy*100:+.0f}%/FCFyld{(fcy*100 if pd.notna(fcy) else 0):+.0f}%" if pd.notna(cfy) else ""
    detail=(f"PE{pe} pe_z{pez:+.1f} PEG{peg:.2f}({gtag}g{g*100:+.0f}%) ROE{roe:.0f}% dd{dd*100:+.0f}%" if pd.notna(peg) else f"PE{pe} pe_z{pez:+.1f} (g{(g*100 if pd.notna(g) else 0):+.0f}%) ROE{roe:.0f}% dd{dd*100:+.0f}%")+pbtag+cytag
    return (v,act,detail,"⚠" if trap else "")

def eval_cyclical(t):
    com=COMMODITY_MAP[t]; cs=comm_state[com]
    if t not in val.index: return (f"CYCLICAL/{com}","?","no stock data","")
    r=val.loc[t]; dd=r["dd52"]; pb=r["PB"]; deep=(pd.notna(dd) and dd<-0.25)
    pct=cs["pctile"]
    # STRUCTURAL overlay (refinement 1): percentile × supply-structure × oil-anchor
    if t in CYC_STRUCT:
        sv,struct,_,_=CYC_STRUCT[t]
        if pct<0.40 and deep: v="TROUGH_BUY"; act="BUY-zone"
        elif pct<0.40: v="cmdty_CHEAP"; act="ACCUMULATE/watch"
        elif "ELEVATED-SUPPORTED" in sv: v=f"ELEVATED-SUPPORTED({struct})"; act="HOLD/selective (not avoid)"
        elif "cyclical-PEAK" in sv: v=f"cmdty_PEAK({struct})"; act="AVOID-new (reverts)"
        else: v="cmdty_MID"; act="WAIT"
        detail=f"{com} pctile{pct:.2f} [{struct}] | stock dd{dd*100:+.0f}% PB{pb}"
        return (v,act,detail,"")
    # fallback (no structural data)
    if pct<0.40 and deep: v="TROUGH_BUY"; act="BUY-zone"
    elif pct<0.40: v="cmdty_CHEAP"; act="ACCUMULATE/watch"
    elif pct>0.80: v="cmdty_EXPENSIVE"; act="AVOID-new (late cycle)"
    else: v="cmdty_MID"; act="WAIT"
    detail=f"{com} pctile{pct:.2f}({'GOOD' if cs['good'] else 'WEAK'}) | stock dd{dd*100:+.0f}% PB{pb}"
    return (v,act,detail,"")

def eval_sugar(t):
    # TREND cyclical (inverted vs eval_cyclical): buy STRENGTH/dips, not the trough.
    cs=sugar_state
    if t not in val.index: return ("SUGAR","?","no stock data","")
    r=val.loc[t]; dd=r["dd52"]; pb=r["PB"]; roe=r["ROE5Y"]; deep=(pd.notna(dd) and dd<-0.25)
    good=cs["good"]; pct=cs["pctile"]
    if good and deep: v="TREND_DIP_BUY"; act="BUY-zone"               # pullback within a sugar uptrend
    elif good: v="TREND_UP"; act="ACCUMULATE/watch"
    elif pct<=0.15: v="DOWNCYCLE_LOW"; act="WAIT (trough=value-trap; await regime flip)"
    else: v="WEAK_FADING"; act="WAIT"
    detail=(f"sugar {cs['price']:.2f} {'GOOD' if good else 'WEAK'} pctile{pct:.2f} | stock dd{dd*100:+.0f}% "
            f"PB{pb} ROE{(roe if pd.notna(roe) else 0):.0f}% | AD-duty Thai exp {SUGAR_AD_EXPIRY} (MOIT review pending)")
    return (v,act,detail,"")

def eval_bank(t):
    r=bank[bank["ticker"]==t].iloc[0]; g=r["gate"]
    act={"CLEAN":"BUY-eligible","WATCH":"WATCH","AVOID":"AVOID"}[g]
    # CLEAN + cheap-for-ROE (roe/pb high) → BUY
    roepb=r["ROE"]/r["PB"] if r["PB"]>0 else 0
    if g=="CLEAN" and roepb>0.12: act="BUY-zone"
    detail=f"NPL{r['NPL']*100:.2f}% cov{r['coverage']*100:.0f}% CAR{(r['CAR']*100 if pd.notna(r['CAR']) else float('nan')):.0f}% ROE{r['ROE']*100:.0f}% PB{r['PB']:.2f} (4qNPL{r['NPL_chg4q']:+.1f}pp)"
    flag="⚠" if g=="AVOID" else ""
    return (g,act,detail,flag)

def eval_power(t):
    v,act,det,_=POWERD[t]
    fl="⚠" if "DEBT_STRESS" in str(v) else ("◆" if "PRE_INFLECTION" in str(v) else "")
    return (v,act,det,fl)

rows=[]
for t in universe:
    if t in bank_set: route="BANK"; v,act,det,fl=eval_bank(t)
    elif t in POWER_set: route="POWER"; v,act,det,fl=eval_power(t)   # ICB 7535 → debt-paydown lifecycle lens
    elif t in SUGAR_SET: route="SUGAR"; v,act,det,fl=eval_sugar(t)   # trend-cyclical (own lens, not contrarian)
    elif t in COMMODITY_MAP: route="CYCLICAL"; v,act,det,fl=eval_cyclical(t)
    else: route="COMPOUNDER"; v,act,det,fl=eval_compounder(t)
    # EVENT_CHECK overlay: VALUE_TRAP is never a blind AVOID — flag for manual event review
    if v=="VALUE_TRAP": act="EVENT_CHECK (verify: structural vs one-off?)"
    # SOLVENCY GATE (precedence over any cheap/trough verdict, except verified events) —
    # falling-knife protection: insolvent names are NOT contrarian buys.
    if t not in EVENTS:
        dz,why=distressed(t)
        if dz: v="DISTRESSED"; act="AVOID (insolvency/falling-knife)"; fl="☠"; det=det+f" | ☠ SOLVENCY: {why}"
        elif t in val.index and pd.notna(val.loc[t].get("ttm_cfo_bn")) and val.loc[t]["ttm_cfo_bn"]<0:
            # solvent but burning operating cash — working-capital watch (not an exclusion)
            cfo=val.loc[t]["ttm_cfo_bn"]; cr=val.loc[t].get("CR")
            det=det+f" | ⚠ CFO-watch: TTM operating CF {cfo:.0f}bn<0 (working-capital drain; CR {cr})"; fl=(fl+"⚠").strip()
    # explicit event overrides (verified special situations)
    if t in EVENTS:
        v="SPECIAL_SITUATION"; act="EVENT-driven → manual"; fl="◆"; det=det+" | EVENT: "+EVENTS[t]["note"][:90]+"..."
    # OIL transmission overlay (annotate how Brent feeds this chain-position; does not change routing/verdict)
    if t in OILMAP:
        det=det+oil_tag(OILMAP,t)
        if OILMAP[t]["signal"] in ("INVERSE_MARGIN","FREIGHT_NOT_OIL"): fl=(fl+"⛽").strip()
    # FREIGHT-RATE overlay (segment→global index; complements RATE_CYCLICAL NPM-peak gate)
    if t in FMAP:
        det=det+freight_tag(FMAP,t)
        if _BDI[0] and FMAP[t]["segment"]=="DRY_BULK": det=det+f" | BDI now {_BDI[0]}({_BDI[2]})"
    liq=POWERD[t][3] if t in POWER_set else (val.loc[t,"liqB"] if t in val.index else np.nan)   # momentum-aware = GREATEST(3M-median, 1M)
    # liquidity-RISING flag (user insight, TV1): liquidity is endogenous to performance; a 3M-median
    # lags and would exclude a good company whose liquidity is climbing on strong results. Flag the rise.
    if t in val.index:
        l1=val.loc[t].get("liq1m"); l3=val.loc[t].get("liq3m")
        if pd.notna(l1) and pd.notna(l3) and l3>0 and l1>=1.3*l3:
            det=det+f" | ⬆ liq RISING (1M {l1:.1f}B vs 3M-med {l3:.1f}B)"
    eng_lbl=""
    if route not in ("BANK","POWER") and t in ENGINE:   # engine badge (banks/power use own lens)
        e,cm=ENGINE[t]; eng_lbl=e+("◆" if cm else "")  # ◆ = also a strict cash-machine
    if t in ASSET_PLAY:                  # refinement 2: value on NAV not earnings-multiple
        eng_lbl=(eng_lbl+" ASSET_PLAY→NAV").strip(); det=det+" | ASSET_PLAY: value on NAV/SOTP (lumpy non-op NP, asset-heavy)"
        # backlog NAV (IC-validated): deferred-revenue (pre-sold land-lease) / market cap + pace (durability flag)
        if t in val.index:
            ul=val.loc[t].get("un_lvl"); uy=val.loc[t].get("un_yoy")
            if pd.notna(ul) and ul>0.02:
                det=det+f" | backlog UnRev/MV {ul*100:.0f}%"+(f" (YoY{uy*100:+.0f}%)" if pd.notna(uy) else "")
                if pd.notna(uy) and uy<-0.10: det=det+" ⚠pipeline-running-off"
    # refinement #1 (2026-05-31): HYBRID-IP — a compounder NOT tagged asset-play (manufacturing base
    # dilutes UnRev/Equity, e.g. VGC ~70% IP profit) but with meaningful deferred-lease backlog
    # (UnRev/MktCap≥10%) carries IP/land value BEYOND operating earnings → flag + bonus (not a full flip,
    # so its operating/materials value via PE/cfo is preserved).
    elif route=="COMPOUNDER" and t in val.index:
        ul=val.loc[t].get("un_lvl")
        if pd.notna(ul) and ul>=0.10:
            det=det+f" | ⬢ HYBRID-IP backlog UnRev/MV {ul*100:.0f}% (IP/leasing NAV beyond operating earnings)"
    # refinement 3: L5 margin-cycle overlay (commodity-consumers) — PEAK margin = caution, BOTTOM = opportunity
    if route=="COMPOUNDER" and t in MARGIN and v not in ("DISTRESSED","SPECIAL_SITUATION"):
        cyc,gpct=MARGIN[t]
        if cyc=="MARGIN_PEAK":
            det=det+f" | ⚠ L5 MARGIN_PEAK (GPM pctile{gpct}): low PE on peak-cycle EPS = compress risk"
            if act=="BUY-zone": act="WATCH (margin-peak: cyclically-inflated EPS)"; fl=(fl+"⚠").strip()
        elif cyc=="MARGIN_BOTTOM":
            det=det+f" | ★ L5 MARGIN_BOTTOM (GPM pctile{gpct}): margin crushed→revert↑ (buy if brand)"
        # paired-peer overlay: a same-input peer at MARGIN_PEAK warns the follower (~1q lag)
        if cyc!="MARGIN_PEAK":
            inp=MARGIN_INPUT.get(t); peakers=[p for p in INPUT_PEAKERS.get(inp,[]) if p!=t]
            if peakers:
                det=det+f" | ⚑ PEER-LEAD margin risk: {'/'.join(peakers)} (same input '{inp}') at MARGIN_PEAK → shared-input cycle may compress margin ~1q lag"
                fl=(fl+"⚑").strip()
    rows.append({"ticker":t,"route":route,"verdict":v,"action":act,"engine":eng_lbl,"liqB":liq,"detail":det,"flag":fl})
out=pd.DataFrame(rows)
act_rank={"BUY-zone":0,"BUY-eligible":1,"ACCUMULATE/watch":2,"WATCH":3,"WAIT":4,"AVOID-new (late cycle)":5,"PASS":6,"AVOID":7}
out["ar"]=out["action"].map(act_rank).fillna(9)
out=out.sort_values(["route","ar","ticker"])

# --- merge 8L Quality Rating 1-5 (from rating_8l.py; run it first for a fresh rating) ---
try:
    _rt=pd.read_csv(os.path.join(WORKDIR,"data","rating_8l.csv")).set_index("ticker")["rating"].to_dict()
    out["rating"]=out["ticker"].map(_rt)
except Exception as _e:
    print("rating_8l merge skipped (run rating_8l.py):",_e); out["rating"]=np.nan

# 8L rating -> investment-grade class. Validated (fa_rating_8l_pergroup_2026, rating_8l_credit_scale):
#   <=3 = IG (investment grade): dip-buy +9-13% / win 61-67% over 12M
#    4  = SPEC (speculative): weak, only +1.8-5% — needs a catalyst, not a buy-and-hold
#    5  = AVOID (impaired: full-year loss / extreme leverage)
def _grade(r):
    if pd.isna(r): return ""
    r=int(r); return "IG" if r<=3 else "SPEC" if r==4 else "AVOID"
out["grade"]=out["rating"].apply(_grade)

lines=[]; P=lambda s="":(print(s),lines.append(s))
P("# Unified screener — auto-routed by company type (4 sector lenses)")
P(f"universe {len(out)} | BANK {sum(out.route=='BANK')} · POWER {sum(out.route=='POWER')} · CYCLICAL {sum(out.route=='CYCLICAL')} · SUGAR {sum(out.route=='SUGAR')} · COMPOUNDER {sum(out.route=='COMPOUNDER')}")
P("commodity regimes: "+", ".join(f"{k}={v['pctile']:.2f}{'GOOD' if v['good'] else 'WEAK'}" for k,v in comm_state.items()))
P("")
for route in ["COMPOUNDER","POWER","CYCLICAL","SUGAR","BANK"]:
    g=out[out["route"]==route]
    P(f"## {route}  ({len(g)})")
    P(f"{'tkr':<6}{'R':<3}{'grade':<6}{'verdict':<15}{'engine':<14}{'action':<22}{'liqB':>6}  detail")
    for _,r in g.iterrows():
        _rr=(f"{int(r['rating'])}" if pd.notna(r['rating']) else "-")
        P(f"{r['ticker']:<6}{_rr:<3}{r['grade']:<6}{r['verdict']:<15}{r['engine']:<14}{r['action']:<22}{(r['liqB'] if pd.notna(r['liqB']) else 0):>6.0f}  {r['detail']} {r['flag']}")
    P("")
P("## TOP actionable (action=BUY-zone, by route)")
for route in ["COMPOUNDER","POWER","CYCLICAL","SUGAR","BANK"]:
    g=out[(out["route"]==route)&(out["action"]=="BUY-zone")&((out["liqB"]>=2)|out["liqB"].isna())]
    P(f"  {route}: "+(", ".join(g['ticker'].tolist()) or "none"))
# GOLDEN = cheap + multibagger-engine (COMPOUNDER) + strict cash-machine(◆), liquid
gold=out[(out["verdict"]=="CHEAP_QUALITY")&(out["engine"].str.startswith("COMPOUNDER"))&(out["liqB"]>=2)]
goldcm=out[(out["verdict"]=="CHEAP_QUALITY")&(out["engine"]=="COMPOUNDER◆")&(out["liqB"]>=2)]
P("")
P("  ★ GOLDEN (cheap_quality + COMPOUNDER engine): "+(", ".join(gold['ticker'].tolist()) or "none"))
P("  ★★ + strict cash-machine◆: "+(", ".join(goldcm['ticker'].tolist()) or "none"))
P("")
# Investment-grade gate (rating<=3): the validated dip-buy universe. SPEC(4)=catalyst-only, AVOID(5)=skip.
_ig=out[(out["grade"]=="IG")&(out["action"]=="BUY-zone")&((out["liqB"]>=2)|out["liqB"].isna())]
_spec=out[(out["grade"]=="SPEC")&(out["action"]=="BUY-zone")&((out["liqB"]>=2)|out["liqB"].isna())]
P("  ◉ INVESTMENT-GRADE buy-zone (rating≤3, liq≥2): "+(", ".join(_ig['ticker'].tolist()) or "none"))
P("  ◌ SPECULATIVE buy-zone (rating=4 — catalyst-only, not buy&hold): "+(", ".join(_spec['ticker'].tolist()) or "none"))
P("")
P("Engine: COMPOUNDER (cash + asset-growth + ROIC≥12% = multibagger candidate) | YIELD (cash-cow no runway, e.g. QTP — dividend not multibag) | LOWROIC_GROWTH (grows but ROIC<12, value-destructive) | ◆=strict cash-machine(CFO>NP TTM). Banks excluded from engine (own lens).")
P("Routing: BANK=ICB8355(vnstock NPL-gate) | CYCLICAL=commodity map(CONTRARIAN trough+dislocation) | SUGAR=ICB3577(TREND: buy GOOD-regime dips, avoid WEAK — inverts contrarian) | COMPOUNDER=else(multi-lens cheap).")
P("Grade (8L rating durability): IG=rating≤3 investment-grade (dip-buy +9-13%/win 61-67% 12M) | SPEC=4 speculative (+1.8-5%, catalyst-only) | AVOID=5 impaired (loss/extreme-leverage). Validated fa_rating_8l_pergroup_2026.")
P("Caveat: valuation/liquidity = latest live session (ticker_1m); FA/bank/structural caches ~2026-05-29; screening not advice; banks from cached vnstock v3; DGC/CSV use DAP proxy; cyclical needs commodity at trough (most now mid/high except iron-ore).")
out.drop(columns=["ar"]).to_csv(os.path.join(WORKDIR,"data","unified_screener.csv"),index=False)
with open(os.path.join(WORKDIR,"data","unified_screener.md"),"w",encoding="utf-8") as f: f.write("\n".join(lines))
P("Saved data/unified_screener.{md,csv}")
