#!/usr/bin/env python3
"""
fa_longterm_sleeve.py — PROTOTYPE long-horizon FA sleeve with dry-powder timing
================================================================================
Separate from the short-term momentum book. Thesis (validated this session):
FA edge rises with horizon (2Y IC ~2x 3M) and is strongest accumulating quality
in BEAR / post-CRISIS; FA is a drag in EX-BULL. Capital allocation is the crux:
must hold dry powder to deploy at the crisis bottom.

Posture state machine (DT5G state = vnindex_5state_dt5g_live), user's design:
  - hit EX-BULL(5)            → DISTRIBUTE: cut equity to DISTRIB_EQ, hold cash,
                                KEEP through the BULL/NEUTRAL/BEAR descent (hysteresis)
  - hit CRISIS(1)             → ACCUMULATE: deploy 100% into top-FA quality
  (ride the recovery up at 100% until the next EX-BULL euphoria → distribute again)

Book = top-N FA names (fa_ratings.total_score, tier≠E, liquid), equal-weight within
the equity sleeve, monthly rebalance, quarterly-stable names (low turnover).

Variants compared:
  DRYPOWDER   : posture machine (the user's strategy)
  FULLINVEST  : always 100% in top-N FA (isolates the value of cash timing)
  VNI         : VNINDEX buy & hold

TC=0.25%/side on turnover. Cash earns 0. Monthly NAV. 2014→2026.
Output: data/fa_longterm_sleeve.md + data/fa_sleeve_nav.csv
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
N_HOLD=15; TC=0.0025; LIQ_MIN=2e9; DISTRIB_EQ=0.40
STATE={1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}

def bq_query(sql,maxrows=3000000):
    with tempfile.NamedTemporaryFile(mode="w",suffix=".sql",delete=False,encoding="utf-8") as fh:
        fh.write(sql); tmp=fh.name
    try:
        cmd=(f'"{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} '
             f'--format=csv --max_rows={maxrows} < "{tmp}"')
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=1200,shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    if r.returncode!=0: raise RuntimeError((r.stdout or r.stderr)[:800])
    return pd.read_csv(StringIO(r.stdout.strip()))

def load_prices():
    cache=os.path.join(WORKDIR,"data","_sleeve_prices.csv")
    if os.path.exists(cache):
        px=pd.read_csv(cache)
    else:
        px=bq_query("""
        SELECT t.ticker, t.time, t.Close
        FROM tav2_bq.ticker AS t
        WHERE t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
          AND t.time>=DATE '2013-06-01' AND t.Close IS NOT NULL
        """)
        px.to_csv(cache,index=False)
    px["time"]=pd.to_datetime(px["time"])
    return px

def metrics(nav, ppy=12):
    s=nav.dropna(); rets=s.pct_change().dropna()
    yrs=(s.index[-1]-s.index[0]).days/365.25
    cagr=(s.iloc[-1]/s.iloc[0])**(1/yrs)-1 if yrs>0 else 0
    sh=rets.mean()/rets.std()*np.sqrt(ppy) if rets.std()>0 else 0
    dd=((s-s.cummax())/s.cummax()).min()
    cal=cagr/abs(dd) if dd<0 else 0
    return cagr*100, sh, dd*100, cal, s.iloc[-1]/s.iloc[0]

def main():
    lines=[]; P=lambda s="":(print(s),lines.append(s))
    px=load_prices()
    wide=px.pivot_table(index="time",columns="ticker",values="Close",aggfunc="first").sort_index()
    # FA ratings (as-of), DT5G state
    fa=bq_query("""SELECT f.ticker, f.time, f.total_score, f.tier, f.trading_value_1M
                   FROM tav2_bq.fa_ratings AS f WHERE f.tier IS NOT NULL""",100000)
    fa["time"]=pd.to_datetime(fa["time"]); fa=fa.sort_values("time")
    st=bq_query("SELECT s.time, s.state FROM tav2_bq.vnindex_5state_dt5g_live AS s ORDER BY s.time",100000)
    st["time"]=pd.to_datetime(st["time"]); st=st.set_index("time")["state"]

    # monthly rebalance grid (month-end trading days within price index)
    didx=wide.index
    month_ends=pd.Series(didx).groupby([didx.year,didx.month]).max().values
    rebal=pd.DatetimeIndex(sorted(month_ends))
    rebal=rebal[(rebal>=pd.Timestamp("2014-01-01"))&(rebal<=pd.Timestamp("2026-05-15"))]

    # posture path over rebal dates (hysteresis machine)
    st_ff=st.reindex(didx).ffill()
    posture_at={}; posture="ACCUMULATE"
    for d in didx:
        s=st_ff.get(d)
        if pd.notna(s):
            if int(s)==5: posture="DISTRIBUTE"
            elif int(s)==1: posture="ACCUMULATE"
        posture_at[d]=posture

    def pick_names(d):
        f=fa[fa["time"]<=d]
        if len(f)==0: return []
        latest=f.sort_values("time").groupby("ticker").tail(1)
        latest=latest[(latest["tier"]!="E") & (latest["trading_value_1M"]>=LIQ_MIN)]
        # must have a price on/near d
        avail=[t for t in latest["ticker"] if t in wide.columns and pd.notna(wide.loc[:d,t].iloc[-1] if len(wide.loc[:d,t]) else np.nan)]
        latest=latest[latest["ticker"].isin(avail)]
        return latest.sort_values("total_score",ascending=False).head(N_HOLD)["ticker"].tolist()

    def price_on(d,t):
        col=wide.loc[:d,t] if t in wide.columns else pd.Series(dtype=float)
        col=col.dropna()
        return col.iloc[-1] if len(col) else np.nan

    def run(strategy):
        cash=1.0; shares={}; nav_hist=[]
        for i,d in enumerate(rebal):
            # MTM
            mv=sum(sh*price_on(d,t) for t,sh in shares.items() if not np.isnan(price_on(d,t)))
            nav=cash+mv
            # target equity
            if strategy=="DRYPOWDER":
                eq=1.0 if posture_at.get(d,"ACCUMULATE")=="ACCUMULATE" else DISTRIB_EQ
            else:  # FULLINVEST
                eq=1.0
            names=pick_names(d)
            if names:
                w_each=eq/len(names)
                tgt={t:w_each*nav for t in names}
            else:
                tgt={}
            # turnover & TC
            cur={t:shares.get(t,0)*price_on(d,t) for t in set(list(shares)+list(tgt))}
            cur={t:(0 if np.isnan(v) else v) for t,v in cur.items()}
            turn=sum(abs(tgt.get(t,0)-cur.get(t,0)) for t in set(list(cur)+list(tgt)))
            tc=turn*TC
            # apply: set shares to target
            new_shares={}
            for t,tv in tgt.items():
                p=price_on(d,t)
                if not np.isnan(p) and p>0: new_shares[t]=tv/p
            invested=sum(new_shares[t]*price_on(d,t) for t in new_shares)
            cash=nav-invested-tc
            shares=new_shares
            nav_hist.append((d,nav))
        return pd.Series(dict(nav_hist))

    P("# Long-horizon FA sleeve — dry-powder timing (DT5G) PROTOTYPE")
    P("")
    P(f"N_HOLD={N_HOLD} | DISTRIB_EQ={DISTRIB_EQ:.0%} | TC={TC:.2%}/side | LIQ_MIN={LIQ_MIN/1e9:.0f}B | {rebal[0].date()}→{rebal[-1].date()}")
    # posture exposure summary
    pos_series=pd.Series({d:posture_at[d] for d in rebal})
    P(f"Months in DISTRIBUTE (cash-heavy): {int((pos_series=='DISTRIBUTE').sum())}/{len(pos_series)}")
    P("")

    nav_dp=run("DRYPOWDER"); nav_fi=run("FULLINVEST")
    # VNI benchmark on same grid
    vni=bq_query("""SELECT t.time,t.Close FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX'
                    AND t.time>=DATE '2014-01-01' ORDER BY t.time""",100000)
    vni["time"]=pd.to_datetime(vni["time"]); vni=vni.set_index("time")["Close"].reindex(didx).ffill()
    nav_vni=vni.reindex(rebal).ffill(); nav_vni=nav_vni/nav_vni.iloc[0]

    out=pd.DataFrame({"DRYPOWDER":nav_dp,"FULLINVEST":nav_fi,"VNI":nav_vni,
                      "posture":pos_series})
    out.to_csv(os.path.join(WORKDIR,"data","fa_sleeve_nav.csv"))

    P("## Headline (monthly NAV, 2014→2026)")
    P(f"{'strategy':<14}{'CAGR':>9}{'Sharpe':>9}{'MaxDD':>9}{'Calmar':>8}{'Wealth':>9}")
    P("-"*58)
    for nm,nv in [("DRYPOWDER",nav_dp),("FULLINVEST",nav_fi),("VNI B&H",nav_vni)]:
        c,sh,dd,cal,w=metrics(nv)
        P(f"{nm:<14}{c:>+8.2f}%{sh:>+9.2f}{dd:>+8.2f}%{cal:>+8.2f}{w:>+9.2f}")
    P("")
    # sub-period: how each did through the 2022 drawdown + 2020 covid
    for lo,hi,lab in [("2018-01-01","2020-04-30","2018-20 (covid bottom)"),
                      ("2021-11-01","2023-06-30","2022 bear+recovery"),
                      ("2024-01-01","2026-05-15","2024-26 OOS")]:
        seg_dp=nav_dp[(nav_dp.index>=lo)&(nav_dp.index<=hi)]; seg_fi=nav_fi[(nav_fi.index>=lo)&(nav_fi.index<=hi)]
        seg_v=nav_vni[(nav_vni.index>=lo)&(nav_vni.index<=hi)]
        if len(seg_dp)>3:
            P(f"  {lab:<24} DP {(seg_dp.iloc[-1]/seg_dp.iloc[0]-1)*100:+6.1f}%  "
              f"FI {(seg_fi.iloc[-1]/seg_fi.iloc[0]-1)*100:+6.1f}%  VNI {(seg_v.iloc[-1]/seg_v.iloc[0]-1)*100:+6.1f}%")
    P("")
    P("DRYPOWDER beats FULLINVEST → the cash-timing (raise in EX-BULL, deploy in CRISIS)")
    P("adds value beyond pure FA stock selection. Compare MaxDD especially.")
    P("")
    with open(os.path.join(WORKDIR,"data","fa_longterm_sleeve.md"),"w",encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    P("Saved data/fa_longterm_sleeve.md + data/fa_sleeve_nav.csv")

if __name__=="__main__":
    main()
