#!/usr/bin/env python3
"""
dna_card.py — self-contained per-ticker "investment DNA card" (8 dims, 100% coverage)
=====================================================================================
Drop in ANY ticker → full profile across every dimension built this session.
Computes all dims ON THE FLY from BQ (ICB-fallback router → works for any ticker,
not just the quality universe). Banks pull real NPL/CAR from cached vnstock (bank_lens_v3).
Dims: ROUTE(ICB) · VALUATION(multi-lens) · ENGINE(runway×ROIC) · CASH◆ · MOAT ·
      MARGIN-CYCLE · RUNWAY/TAM · EVENT.
Usage: edit DEMO list (or pass tickers). Output: data/dna_cards.md + .csv
"""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import os, subprocess, tempfile
from io import StringIO
import numpy as np, pandas as pd
PROJECT="lithe-record-440915-m9"; BQ_BIN=os.environ.get("BQ_BIN", (r"bq" if os.name=="nt" else "bq"))
W=os.environ.get("WORKDIR_8L", r"/home/trido/thanhdt/WorkingClaude")
COMMODITY_MAP={"DRI":"rubber","PHR":"rubber","DPR":"rubber","GVR":"rubber","TRC":"rubber","HRC":"rubber",
 "HPG":"iron_ore","HSG":"iron_ore","NKG":"iron_ore","SMC":"iron_ore","POM":"iron_ore","DCM":"urea","DPM":"urea",
 "DDV":"dap","LAS":"dap","DGC":"dap","CSV":"caustic_soda"}  # CSV = chlor-alkali, NOT dap fertilizer
MOAT_TYPE={"VCS":"TECH+BRAND(global TM)","DGC":"SCALE+vert-integ","BMP":"BRAND(pipes S/Central)","VNM":"BRAND(dairy)",
 "DRC":"NONE(commodity tire)","CSM":"NONE(commodity tire)","DHC":"LOCATION(South paper)","HPG":"SCALE+cost(steel)",
 "FPT":"TECH(software export)","MWG":"SCALE+exec(retail)","FRT":"network/exec(pharma)","QTP":"none(fixed utility)",
 "PNJ":"BRAND(jewelry)","SCS":"infra-monopoly(cargo)","NCT":"infra(cargo)","SAB":"BRAND(beer)","MCH":"BRAND(consumer)",
 "DHG":"BRAND(pharma)","DPR":"land-bank(rubber)","ACB":"bank-franchise","MBB":"bank-CASA-franchise","VCB":"bank-premier"}
EXPORT={"DGC","VCS","FMC","VHC","ANV","MPC","TNG","MSH","STK","TCM","PTB","GIL","FPT","DRC","CSM"}
STRUCTURAL={"HPG","HSG","NKG"}
EVENTS={"DGC":"mine suspended + chairman prosecuted (Q1/26); moat intact, swing=mine-access+sulfur",
        "PAT":"DGC-group apatite arm, same event"}
# 5F (Porter) qualitative moat registry — slow-moving, hand-maintained (data/moat_tags.csv).
# Adds the DURABILITY verdict (WIDE/NARROW/NONE) + risk1 (kill-condition to watch) that the
# numeric ROE/GPM proxy can't see. No-op if the file is absent.
try:
    from moat_5f import load_moat_tags
    MOAT5F=load_moat_tags(W)
except Exception: MOAT5F={}
# OIL transmission lens (2026-06-05): how Brent feeds each chain-position. Registry: data/oil_transmission_map.csv
try:
    from oil_transmission import load_oil_map
    OILMAP=load_oil_map(W)
except Exception: OILMAP={}
# FREIGHT-RATE lens (2026-06-05): VN shipping per-segment vs global freight. Registry: data/freight_map.csv
try:
    from freight_map import load_freight_map, current_bdi
    FMAP=load_freight_map(W); _BDI=current_bdi(W)
except Exception: FMAP={}; _BDI=(None,None,None)
_FALLBACK=["VCS","DGC","DRC","DHC","BMP","QTP","HPG","FRT","VNM","MWG","PNJ","SCS","FMC","ACB","MBB","DPR","CSM","DHG","NKG","DCM"]
def _universe():
    # no args -> profile the WHOLE 8L universe (so dna_cards.csv covers every name the bot can query),
    # not just a curated demo. Falls back to the curated list if the screener isn't available yet.
    try:
        u=pd.read_csv(os.path.join(W,"data","unified_screener.csv"))
        tks=[str(x).upper() for x in u["ticker"].dropna().unique()]
        return tks if tks else _FALLBACK
    except Exception: return _FALLBACK
DEMO=[a.upper() for a in sys.argv[1:]] if len(sys.argv)>1 else _universe()

def bq(sql):
    with tempfile.NamedTemporaryFile(mode="w",suffix=".sql",delete=False,encoding="utf-8") as f: f.write(sql); tmp=f.name
    try: r=subprocess.run(f'{"type" if os.name=="nt" else "cat"} "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=2000000',capture_output=True,text=True,timeout=400,shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    return pd.read_csv(StringIO(r.stdout.strip()))

tks="','".join(DEMO)
# A) latest snapshot
snap=bq(f"""WITH lt AS (SELECT t.ticker,MAX(t.time) mx FROM tav2_bq.ticker_1m t WHERE t.ticker IN ('{tks}') AND t.PB IS NOT NULL GROUP BY t.ticker),
hiw AS (SELECT t.ticker,MAX(t.Close) hi FROM tav2_bq.ticker t WHERE t.ticker IN ('{tks}') AND t.time>=DATE_SUB(DATE '2026-05-29',INTERVAL 365 DAY) GROUP BY t.ticker)
SELECT t.ticker,CAST(FLOOR(t.ICB_Code/1000) AS INT64) sec,t.ICB_Code, ROUND(t.PE,1) PE,
 ROUND((t.PE-t.PE_MA5Y)/NULLIF(t.PE_SD5Y,0),2) pe_z, ROUND((t.PB-t.PB_MA5Y)/NULLIF(t.PB_SD5Y,0),2) pb_z, t.PB,
 ROUND(SAFE_DIVIDE(t.NP_P0,t.NP_P4)-1,3) np_yoy, ROUND(t.ROE5Y*100,1) roe5y, ROUND(t.ROIC5Y*100,1) roic5y,
 ROUND(t.Close/NULLIF(hiw.hi,0)-1,2) dd, ROUND(t.Volume_3M_P50*t.Close/1e9,1) liqB
FROM tav2_bq.ticker_1m t JOIN lt ON lt.ticker=t.ticker AND lt.mx=t.time JOIN hiw ON hiw.ticker=t.ticker""").set_index("ticker")
# B) quarterly series
q=bq(f"""SELECT t.ticker,t.time,t.NP_P0,t.CF_OA_P0,t.totalAsset_P0,t.Cash_P0,t.OShares,t.Revenue_P0,t.GPM_P0
FROM tav2_bq.ticker_financial t WHERE t.ticker IN ('{tks}') AND t.time>='2011-01-01' ORDER BY t.ticker,t.time""")
q["time"]=pd.to_datetime(q["time"])
try: bank=pd.read_csv(os.path.join(W,"data","bank_lens_v3.csv")).set_index("ticker")
except Exception: bank=pd.DataFrame()
# refinements: structural overlay (cyclical) + asset-play (NAV) flag
try:
    cs=pd.read_csv(os.path.join(W,"data","cyclical_structural.csv"))
    CYC_STRUCT={r["ticker"]:(r["verdict"],r["structure"]) for _,r in cs.iterrows()}
except Exception: CYC_STRUCT={}
try:
    ap=pd.read_csv(os.path.join(W,"data","asset_play.csv"))
    ASSET_PLAY=set(ap[ap["verdict"]=="ASSET_PLAY"]["ticker"])
except Exception: ASSET_PLAY=set()
comm={}
for c in set(COMMODITY_MAP.values()):
    try:
        d=pd.read_csv(os.path.join(W,"data",f"{c}_monthly.csv")); d.columns=["m","p"]
        d["pct"]=d["p"].rolling(60,min_periods=24).apply(lambda x:(x.iloc[-1]>=x).mean())
        comm[c]=float(d["pct"].iloc[-1])
    except Exception: comm[c]=np.nan

def cagr(a,b,y): return (a/b)**(1/y)-1 if (pd.notna(a) and pd.notna(b) and a>0 and b>0) else np.nan
def series(t):
    g=q[q["ticker"]==t].sort_values("time")
    out={}
    np_=g["NP_P0"]; cfo=g["CF_OA_P0"]
    ttm_np=np_.rolling(4).sum(); ttm_cfo=cfo.rolling(4).sum()
    rat=(ttm_cfo/ttm_np).where(ttm_np>0); rec=rat.dropna().tail(8)
    out["cfo_np_med"]=rec.median() if len(rec)>=4 else np.nan
    out["pct_ge1"]=(rec>=1).mean() if len(rec)>=4 else np.nan
    ta=g["totalAsset_P0"].dropna(); ta=ta[ta>0]
    out["asset_cagr"]=cagr(ta.iloc[-1],ta.iloc[max(0,len(ta)-17)],min(4,len(ta)-1)) if len(ta)>=12 else np.nan
    cash=g["Cash_P0"].dropna(); out["cash_grow"]=(cash.iloc[-1]>cash.iloc[max(0,len(cash)-9)]) if len(cash)>=4 else False
    osh=g["OShares"].dropna(); out["dilut"]=(osh.iloc[-1]/osh.iloc[max(0,len(osh)-13)]-1) if len(osh)>=8 else np.nan
    rev=g["Revenue_P0"].rolling(4).sum().dropna()
    out["rev_rec"]=cagr(rev.iloc[-1],rev.iloc[-13],3) if len(rev)>=13 else np.nan
    out["rev_pri"]=cagr(rev.iloc[-13],rev.iloc[-25],3) if len(rev)>=25 else np.nan
    gpm=g["GPM_P0"].dropna()
    out["gpm_pct"]=(gpm<=gpm.iloc[-1]).mean() if len(gpm)>=12 else np.nan
    out["gpm_now"]=gpm.iloc[-1]*100 if len(gpm) else np.nan
    return out

def fmtp(v,suf="%",mul=100,sign=True):
    if pd.isna(v): return "n/a"
    return (f"{v*mul:+.0f}{suf}" if sign else f"{v*mul:.0f}{suf}")

lines=[]; P=lambda s="":(print(s),lines.append(s))
P("# Investment DNA cards — self-contained, 100% coverage (8 dims)")
P("ROUTE(ICB)·VALUATION·ENGINE(runway×ROIC)·CASH◆·MOAT·MARGIN-CYCLE·RUNWAY/TAM·EVENT")
P("")
cards=[]
for t in DEMO:
    if t not in snap.index: P(f"━━ {t}: no data\n"); continue
    s=snap.loc[t]; ser=series(t); sec=s["sec"]
    route="BANK" if sec==8 and (bank.empty or t in bank.index or s["ICB_Code"]==8355) else ("CYCLICAL" if t in COMMODITY_MAP else "COMPOUNDER")
    if s["ICB_Code"]==8355: route="BANK"
    # MOAT
    gpm=ser["gpm_now"]; roe=s["roe5y"]
    moat="STRONG" if (pd.notna(roe) and roe>=18 and pd.notna(gpm) and gpm>=25) else ("WEAK/commodity" if (pd.notna(gpm) and gpm<15) or (pd.notna(roe) and roe<10) else "MODERATE")
    mt=MOAT_TYPE.get(t,"")
    # MARGIN-CYCLE
    gp=ser["gpm_pct"]; mcyc=("MARGIN_BOTTOM" if gp<=0.25 else "MARGIN_PEAK" if gp>=0.75 else "MID") if pd.notna(gp) else "n/a"
    # RUNWAY/TAM
    rr,rp=ser["rev_rec"],ser["rev_pri"]; accel=(rr-rp) if (pd.notna(rr) and pd.notna(rp)) else np.nan
    if pd.isna(rr): run="n/a"
    elif rr>=0.20: run="CAPTURING"
    elif rr>=0.15 and (pd.isna(accel) or accel>=-0.05): run="DURABLE"
    elif pd.notna(rp) and rp>=0.15 and pd.notna(accel) and accel<=-0.10: run="SATURATING"
    elif rr<0.08 and (pd.isna(rp) or rp<0.08): run="MATURE/FLAT"
    else: run="MODERATE"
    tam="EXPORT" if t in EXPORT else ("STRUCTURAL" if t in STRUCTURAL else "DOMESTIC")
    if route=="BANK" and not bank.empty and t in bank.index:
        b=bank.loc[t]
        P(f"━━ {t} [BANK]  gate={b['gate']}")
        P(f"   Asset-quality: NPL {b['NPL']*100:.2f}% cov {b['coverage']*100:.0f}% CAR {(b['CAR']*100 if pd.notna(b['CAR']) else float('nan')):.0f}% | ROE {b['ROE']*100:.0f}% PB {b['PB']:.2f}")
        P(f"   Moat: {moat} [{mt}]   Runway/TAM: {run} [{tam}]")
        m5=MOAT5F.get(t)
        if m5: P(f"   5F-Moat: {m5['tier']} [{m5['type']}] · risk#1: {m5['risk1']} (asof {m5['asof']})")
        cards.append({"ticker":t,"route":"BANK","gate":b["gate"],"moat":moat,"runway":run,
                      "moat5f":(m5['tier'] if m5 else ""),"risk1":(m5['risk1'] if m5 else "")}); P(""); continue
    # ENGINE
    machine=(pd.notna(ser["pct_ge1"]) and ser["pct_ge1"]>=0.6 and pd.notna(ser["cfo_np_med"]) and ser["cfo_np_med"]>=1 and ser["cash_grow"])
    runway_ok=(pd.notna(ser["asset_cagr"]) and ser["asset_cagr"]>0.03); roic_ok=(pd.notna(s["roic5y"]) and s["roic5y"]>=12)
    engine="COMPOUNDER" if (roic_ok and runway_ok) else ("YIELD" if (machine and not runway_ok) else ("LOWROIC_GROWTH" if (runway_ok and not roic_ok) else ("CASH_COW" if machine else "-")))
    # VALUATION (compounder lens)
    peg=(s["PE"]/(s["np_yoy"]*100)) if (pd.notna(s["np_yoy"]) and s["np_yoy"]>0 and s["PE"]>0) else np.nan
    hist=(s["pe_z"]<-1) or (s["pb_z"]<-1); pegc=(0<peg<=1) if pd.notna(peg) else False; absc=(s["PE"]<10) or (s["PB"]<1.2)
    trap=(pd.notna(s["np_yoy"]) and s["np_yoy"]<-0.15); nl=sum([hist,pegc,absc])
    verdict=("VALUE_TRAP→event_check" if (trap and (hist or absc)) else "CHEAP_QUALITY" if nl>=2 else "CHEAP_1lens" if nl==1 else "NOT_CHEAP")
    ap_flag=" ASSET_PLAY→NAV" if (t in ASSET_PLAY and route!="BANK") else ""
    if route=="CYCLICAL" and t in CYC_STRUCT:
        sv,st=CYC_STRUCT[t]; cyc=f"  | {COMMODITY_MAP[t]} pctile{comm.get(COMMODITY_MAP[t],float('nan')):.2f} [{st}] → {sv.split('(')[0]}"
    elif route=="CYCLICAL":
        cyc=f"  | commodity {COMMODITY_MAP[t]} pctile {comm.get(COMMODITY_MAP[t],float('nan')):.2f}"
    else: cyc=""
    P(f"━━ {t} [{route}]  {verdict}{ap_flag}  (PE{s['PE']} pe_z{s['pe_z']:+.1f} PEG{peg:.2f} dd{fmtp(s['dd'])}){cyc}")
    P(f"   Engine: {engine}{'◆' if machine else ''}  (ROIC {fmtp(s['roic5y'],'%',1,False)}, asset-growth {fmtp(ser['asset_cagr'])}, dilut3y {fmtp(ser['dilut'])})")
    P(f"   Moat:   {moat} [{mt}]  (GPM {fmtp(gpm,'%',1,False)}, ROE {fmtp(roe,'%',1,False)})")
    m5=MOAT5F.get(t)
    if m5: P(f"   5F-Moat: {m5['tier']} [{m5['type']}] · risk#1: {m5['risk1']} (asof {m5['asof']})")
    om=OILMAP.get(t)
    if om:
        _lag="" if str(om["lag_q"])=="99" else f", profit lag ~{int(om['lag_q'])}Q"
        P(f"   ⛽ OIL[{om['chain']}·{om['signal']}{_lag}]: {om['play']}")
    fm=FMAP.get(t)
    if fm:
        _bdi=f"  (BDI now {_BDI[0]},{_BDI[2]})" if (_BDI[0] and fm['segment']=='DRY_BULK') else ""
        P(f"   🚢 FREIGHT[{fm['segment']}·{fm['index']}·NP~{fm['sens']:+.2f}]{_bdi}: {fm['play']}")
    if ap_flag: P(f"   ⚑ ASSET-PLAY: value on NAV/SOTP (lumpy non-operating NP, asset-heavy) — PE/PEG misleading")
    P(f"   Margin-cycle: {mcyc} (GPM pctile {gp:.2f})" if pd.notna(gp) else f"   Margin-cycle: n/a")
    P(f"   Runway/TAM:   {run} [{tam}]  (rev CAGR {fmtp(rr)} vs prior {fmtp(rp)})")
    if t in EVENTS: P(f"   EVENT: {EVENTS[t]}")
    P("")
    cards.append({"ticker":t,"route":route,"verdict":verdict,"asset_play":bool(ap_flag),"struct":(CYC_STRUCT.get(t,('',''))[0] if route=='CYCLICAL' else ''),"engine":f"{engine}{'◆' if machine else ''}","moat":moat,"moat_type":mt,"moat5f":(m5['tier'] if m5 else ""),"risk1":(m5['risk1'] if m5 else ""),"margin_cycle":mcyc,"runway":run,"tam":tam,"roic":s["roic5y"],"event":EVENTS.get(t,"")})
pd.DataFrame(cards).to_csv(os.path.join(W,"data","dna_cards.csv"),index=False)
P(f"[{len(cards)} cards | route coverage 100% via ICB-fallback]")
with open(os.path.join(W,"data","dna_cards.md"),"w",encoding="utf-8") as f: f.write("\n".join(lines))
P("Saved data/dna_cards.{md,csv}")
