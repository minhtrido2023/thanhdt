#!/usr/bin/env python3
"""
fa_sleeve_v2.py — FA long-horizon sleeve v2: valuation-timed (#1) + spread (#3)
==============================================================================
v1 lessons: EX-BULL cash trigger too rare (missed COVID); long-only top-FA ≈ index
because the IC edge is a top−bottom SPREAD concentrated in cheap/bear regimes.

v2 fixes:
  #1 VALUATION TIMING — equity exposure scales inversely with VNINDEX PE expanding
     percentile (point-in-time): cheap market → deploy 100%, expensive → raise cash.
     Smoother & earlier than the rare EX-BULL state; routes capital into quality
     exactly when the market is cheap (= where 2Y FA returns are highest).
  #3 SPREAD — long top-quintile FA, short bottom-quintile FA (the edge lives in the
     spread, not long-only-top). NOTE: single-stock shorting is limited in VN →
     treat LONGSHORT/PE_LS as "what the edge looks like if shortable" (a VN30-futures
     hedge approximates the net-exposure cut but not the bottom-FA-specific short).

Variants (monthly rebalance, equal-weight, TC 0.25%/side on turnover):
  FULLINVEST : long top-15 FA, always 100%            (v1 baseline)
  PE_TIMED   : long top-15 FA, equity = 1.0−0.6·PEpct  (#1, implementable)
  LONGSHORT  : long top-Q5 − short bottom-Q1, $-neutral (#3, paper)
  PE_LS      : long top-Q5 (100%) − short bottom-Q1·PEpct (#1+#3: hedge scales w/ expensiveness)
  VNI        : VNINDEX buy & hold
Output: data/fa_sleeve_v2.md + data/fa_sleeve_v2_nav.csv
"""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import os, subprocess, tempfile
from io import StringIO
import numpy as np, pandas as pd

WORKDIR=r"/home/trido/thanhdt/WorkingClaude"
PROJECT="lithe-record-440915-m9"
BQ_BIN=r"bq"
N_LONG=15; TC=0.0025; LIQ_MIN=2e9; BORROW_M=0.10/12  # short borrow ~10%/yr

def bq_query(sql,maxrows=200000):
    with tempfile.NamedTemporaryFile(mode="w",suffix=".sql",delete=False,encoding="utf-8") as fh:
        fh.write(sql); tmp=fh.name
    try:
        cmd=(f'"{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} '
             f'--format=csv --max_rows={maxrows} < "{tmp}"')
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=600,shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    return pd.read_csv(StringIO(r.stdout.strip()))

def metrics(nav, ppy=12):
    s=nav.dropna(); rets=s.pct_change().dropna()
    yrs=(s.index[-1]-s.index[0]).days/365.25
    cagr=(s.iloc[-1]/s.iloc[0])**(1/yrs)-1 if yrs>0 else 0
    sh=rets.mean()/rets.std()*np.sqrt(ppy) if rets.std()>0 else 0
    dd=((s-s.cummax())/s.cummax()).min()
    return cagr*100, sh, dd*100, (cagr/abs(dd) if dd<0 else 0), s.iloc[-1]/s.iloc[0]

def main():
    lines=[]; P=lambda s="":(print(s),lines.append(s))
    px=pd.read_csv(os.path.join(WORKDIR,"data","_sleeve_prices.csv"))
    px["time"]=pd.to_datetime(px["time"])
    wide=px.pivot_table(index="time",columns="ticker",values="Close",aggfunc="first").sort_index()
    # month-end prices → monthly returns
    me=wide.resample("ME").last()
    mret=me.pct_change()
    months=me.index[(me.index>=pd.Timestamp("2014-01-01"))&(me.index<=pd.Timestamp("2026-05-15"))]

    # VNINDEX PE expanding percentile (point-in-time, min 252 daily obs)
    vni=pd.read_csv(os.path.join(WORKDIR,"data/VNINDEX.csv"))
    vni["time"]=pd.to_datetime(vni["time"]); vni=vni.sort_values("time")
    pe=vni.set_index("time")["VNINDEX_PE"].dropna()
    pe_pct=pe.expanding(min_periods=252).apply(lambda x: (x.iloc[-1]>=x).mean(), raw=False)
    pe_pct_m=pe_pct.resample("ME").last().reindex(months).ffill()

    # FA ratings as-of
    fa=bq_query("""SELECT f.ticker,f.time,f.total_score,f.tier,f.trading_value_1M
                   FROM tav2_bq.fa_ratings AS f WHERE f.tier IS NOT NULL""")
    fa["time"]=pd.to_datetime(fa["time"]); fa=fa.sort_values("time")

    def eligible(d):
        f=fa[fa["time"]<=d]
        if len(f)==0: return pd.DataFrame()
        g=f.groupby("ticker").tail(1)
        g=g[(g["tier"]!="E")&(g["trading_value_1M"]>=LIQ_MIN)]
        g=g[g["ticker"].isin(mret.columns)]
        return g.sort_values("total_score",ascending=False)

    # precompute baskets per month
    long15={}; longQ5={}; botQ1={}
    for d in months:
        g=eligible(d)
        if len(g)<25: long15[d]=longQ5[d]=botQ1[d]=[]; continue
        long15[d]=g.head(N_LONG)["ticker"].tolist()
        q=len(g)//5
        longQ5[d]=g.head(q)["ticker"].tolist()
        botQ1[d]=g.tail(q)["ticker"].tolist()

    def basket_ret(names, m):
        if not names: return 0.0
        r=mret.loc[m, [n for n in names if n in mret.columns]]
        r=r.dropna()
        return r.mean() if len(r) else 0.0

    def turnover(prev,cur):
        if not prev: return 1.0 if cur else 0.0
        sp,sc=set(prev),set(cur)
        return len(sp.symmetric_difference(sc))/max(len(sp|sc),1)

    # simulate each variant on monthly grid
    def sim(kind):
        nav=1.0; series={}; prevL=[]; prevS=[]
        for i,d in enumerate(months):
            series[d]=nav
            if i+1>=len(months): continue
            m=months[i+1]  # return realized over next month
            pep=pe_pct_m.get(d, 0.5);  pep=0.5 if pd.isna(pep) else pep
            if kind=="FULLINVEST":
                L=long15[d]; eq=1.0; lr=basket_ret(L,m); ret=eq*lr; tc=turnover(prevL,L)*TC*eq; prevL=L
            elif kind=="PE_TIMED":
                L=long15[d]; eq=np.clip(1.0-0.6*pep,0.4,1.0); lr=basket_ret(L,m)
                ret=eq*lr; tc=turnover(prevL,L)*TC*eq; prevL=L
            elif kind=="LONGSHORT":
                L=longQ5[d]; S=botQ1[d]; lr=basket_ret(L,m); sr=basket_ret(S,m)
                ret=lr-sr-BORROW_M; tc=(turnover(prevL,L)+turnover(prevS,S))*TC; prevL,prevS=L,S
            elif kind=="PE_LS":
                L=longQ5[d]; S=botQ1[d]; hedge=pep  # short more when expensive
                lr=basket_ret(L,m); sr=basket_ret(S,m)
                ret=lr-hedge*sr-hedge*BORROW_M; tc=(turnover(prevL,L)+hedge*turnover(prevS,S))*TC; prevL,prevS=L,S
            nav=nav*(1+ret-tc)
        return pd.Series(series)

    navs={k:sim(k) for k in ["FULLINVEST","PE_TIMED","LONGSHORT","PE_LS"]}
    vni_c=vni.set_index("time")["Close"].resample("ME").last().reindex(months).ffill()
    navs["VNI"]=vni_c/vni_c.iloc[0]

    P("# FA sleeve v2 — valuation timing (#1) + spread (#3)")
    P("")
    P(f"N_LONG={N_LONG} | TC={TC:.2%}/side | {months[0].date()}→{months[-1].date()} | "
      f"PEpct now={pe_pct_m.iloc[-1]:.2f}")
    P("NOTE: LONGSHORT/PE_LS assume shortable bottom-FA (limited in VN) — shows where edge lives.")
    P("")
    P(f"{'variant':<12}{'CAGR':>9}{'Sharpe':>9}{'MaxDD':>9}{'Calmar':>8}{'Wealth':>9}")
    P("-"*56)
    for k in ["FULLINVEST","PE_TIMED","LONGSHORT","PE_LS","VNI"]:
        c,sh,dd,cal,w=metrics(navs[k])
        P(f"{k:<12}{c:>+8.2f}%{sh:>+9.2f}{dd:>+8.2f}%{cal:>+8.2f}{w:>+9.2f}")
    P("")
    # sub-periods
    for lo,hi,lab in [("2018-01-01","2020-05-31","2018-COVID"),
                      ("2021-11-01","2023-06-30","2022 bear"),
                      ("2024-01-01","2026-05-15","2024-26 OOS")]:
        row=f"  {lab:<14}"
        for k in ["FULLINVEST","PE_TIMED","PE_LS","VNI"]:
            s=navs[k][(navs[k].index>=lo)&(navs[k].index<=hi)]
            row+=f"{k[:4]} {(s.iloc[-1]/s.iloc[0]-1)*100:+6.1f}%  " if len(s)>2 else ""
        P(row)
    P("")
    pd.DataFrame(navs).to_csv(os.path.join(WORKDIR,"data","fa_sleeve_v2_nav.csv"))
    with open(os.path.join(WORKDIR,"data","fa_sleeve_v2.md"),"w",encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    P("Saved data/fa_sleeve_v2.md + data/fa_sleeve_v2_nav.csv")

if __name__=="__main__":
    main()
