"""TCH DD 31/10/2026 — moi so dau vao trich tu calc/notes_read.md (doc anh BCTC) hoac BQ; gia dinh gan (uoc luong)."""
import sys, pandas as pd, numpy as np
D=sys.argv[1]
SH=1003.312808  # tr cp, TM21d
PX=11850        # dong cua 30/10/2026 [BQ]
# --- 1. LN me theo nam tai chinh (Apr-Mar) tu BQ ticker_financial NP_P0 quy duong lich (khop KT25: FY24 854,99; FY25 211,06)
q=pd.read_csv(f"{D}/bq_tch_fin.csv").set_index("quarter").np0
fy={"FY21":["2021Q2","2021Q3","2021Q4","2022Q1"],"FY22":["2022Q2","2022Q3","2022Q4","2023Q1"],
    "FY23":["2023Q2","2023Q3","2023Q4","2024Q1"],"FY24":["2024Q2","2024Q3","2024Q4","2025Q1"],"FY25":["2025Q2","2025Q3","2025Q4","2026Q1"]}
ann={k:round(q[v].sum(),1) for k,v in fy.items()}; print("LNST me theo FY:",ann)
q2=537.73; q1=125.42  # Q2HN KQKD; Q1=663,14-537,73
ttm=q["2025Q4"]+q["2026Q1"]+q1+q2; print("TTM me (Q3FY25..Q2FY26)",round(ttm,1),"EPS",round(ttm/SH*1000), "P/E",round(PX/(ttm/SH*1000),1))
eqp=15279.65-3120.54; bv=eqp/SH*1000; print("VCSH me",round(eqp,1),"BVPS",round(bv),"P/B",round(PX/bv,2))
for lab,fy26 in [("FY26E thap 900",900),("FY26E 1.117 (SHS)",1117),("FY26E 1.300",1300)]:
    n=np.mean([ann["FY23"],ann["FY24"],ann["FY25"],fy26]); print(f"LN chuan hoa FY23-26 [{lab}] {n:.0f} EPS {n/SH*1000:.0f} P/E {PX/(n/SH*1000):.1f} ROE {n/eqp:.1%}")
n5=np.mean(list(ann.values())); print("TB FY21-25",round(n5,1),"ROE",f"{n5/eqp:.1%}","P/E",round(PX/(n5/SH*1000),1))
# --- 2. Net cash that
cash=1035.35; htm=2203.19+57.78; debt=0
print("Tien+HTM",round(cash+htm,1),"vay",debt,"; tien/cp",round((cash+htm)/SH*1000))
# --- 3. Beta tuan 2 nam vs VNINDEX
d=pd.read_csv(f"{D}/bq_tch_daily.csv",parse_dates=["time"]).set_index("time").loc["2024-10-31":]
w=d[["Close","VNINDEX"]].resample("W-FRI").last().pct_change().dropna()
b=np.cov(w.Close,w.VNINDEX)[0,1]/w.VNINDEX.var(); print("beta tuan 2y",round(b,2),"Blume",round(0.67*b+0.33,2),"n tuan",len(w))
# --- 4. NAV du an (uoc luong) -- 3 kich ban
NMTT=5599.82; vat=1.08          # (uoc luong) VAT binh quan sau phan dat
rev_bl=NMTT/vat; gm=0.50         # bien gop BDS 6T 51,9% [TM23/25]
cost_bl=rev_bl*(1-gm); htk_bds=14630.92; rest=htk_bds-cost_bl
print("DT backlog da thu ~",round(rev_bl),"GV tuong ung",round(cost_bl),"HTK con lai",round(rest))
sc={"xau":dict(m=0.28,s=0.10,disc=0.30,share=0.725),"co so":dict(m=0.36,s=0.25,disc=0.20,share=0.75),"tot":dict(m=0.40,s=0.40,disc=0.10,share=0.75)}
out={}
for k,p in sc.items():
    a=rev_bl*p["m"]*0.725*0.90          # LN sau thue backlog, phan me 72,5% (NCI 27,5% 6T), chiet khau 0,90 (~1 nam)
    bb=rest*p["s"]*0.70*p["share"]       # thang du sau thue tren HTK con lai, PV 0,70 (~4 nam), phan me
    nav=(eqp+a+bb)*(1-p["disc"]); v=nav/SH*1000; out[k]=v
    print(f"{k}: backlog {a:.0f} + HTK {bb:.0f} + VCSH {eqp:.0f} -> NAV truoc CK {eqp+a+bb:.0f}; CK holding/QT {p['disc']:.0%} -> {v:,.0f} d/cp")
wv=0.25*out["xau"]+0.5*out["co so"]+0.25*out["tot"]; print("NAV trong so 25/50/25:",round(wv),"so gia",round(PX/wv-1,3))
# --- 5. Comps P/B (BQ 30/10/2026, BV theo BQ)
pe=pd.read_csv(f"{D}/bq_peers.csv").set_index("ticker")
peers=["KDH","NLG","PDR","DIG","DXG","HDG","CEO","HDC","NVL","DXS","KHG","SCR","NTL","IJC","QCG"]
med=pe.loc[peers,"pb"].median(); print("P/B trung vi 15 peer",med,"; TCH BQ",pe.loc["TCH","pb"],"; TCH tu tinh",round(PX/bv,2),"; gia tai P/B peer x BV me",round(med*bv))
# --- 6. SOTP thi truong: CRV look-through
crv=23000*687.40/1000; lt=crv*0.6802; print("CRV von hoa",round(crv),"look-through 68,02%",round(lt),"=",round(lt/SH*1000),"d/cp TCH; von hoa TCH",round(PX*SH/1000))
# --- 7. Ke implied P/B: P/B = (ROE-g)/(Ke-g)
for roe in (0.06,0.08,0.10,0.12):
    print("ROE",roe,"P/B hop ly Ke12.3/13.4 g3%:",round((roe-0.03)/(0.123-0.03),2),round((roe-0.03)/(0.134-0.03),2))
