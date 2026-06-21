# -*- coding: utf-8 -*-
"""
f_v5_drawdown_stop_test.py
==========================
Drawdown-stop NGAY TREN SACH V5 (fix goc cho style-grind ma DT5G + VN30F hedge khong cham toi).
Co che (shadow-based, causal):
  - shadow = duong cong von V5 full-weight (NAV that, quan sat duoc real-time qua gia book).
  - INVESTED: neu shadow_dd tu peak <= -X% -> STOP (p=0, ve cash) tu phien sau.
  - STOPPED : track day; re-enter khi shadow bat >= +Y% tu day -> p=1, reset peak.
  combined_ret[t] = p[t-1] * V5_ret[t]   (cash ~0%).
So baseline V5 + grid (X stop, Y reentry); do full CAGR/Sharpe/MaxDD + DD tung episode.
"""
import sys, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding="utf-8")
import numpy as np, pandas as pd
WD=r"/home/trido/thanhdt/WorkingClaude"

v=pd.read_csv(WD+"/data/5sys_prodspec_201401_202605_dt5g.csv"); v["time"]=pd.to_datetime(v["time"])
v=v[["time","V5_V4_KellyQ2","V4_V121_ENS_TQ34b","VNI"]].rename(
    columns={"V5_V4_KellyQ2":"V5","V4_V121_ENS_TQ34b":"V4"})
v["V5r"]=v["V5"].pct_change().fillna(0.0)
v["V4r"]=v["V4"].pct_change().fillna(0.0)
SPY=len(v)/((v.time.iloc[-1]-v.time.iloc[0]).days/365.25)

def apply_stop(rets, X, Y):
    """shadow = cumulative rets (full weight). Returns participation array p (0/1) and combined rets."""
    nfull=len(rets); p=np.ones(nfull); shadow=1.0; peak=1.0; invested=True; trough=1.0
    comb=np.zeros(nfull)
    for t in range(nfull):
        # decide participation for today using info up to t-1 (p already set)
        comb[t]=p[t]*rets[t] if t>0 else 0.0
        # update shadow with today's full-weight return (observable)
        shadow*= (1+rets[t])
        if invested:
            peak=max(peak,shadow)
            if shadow/peak-1 <= -X:
                invested=False; trough=shadow
                if t+1<nfull: p[t+1:]=0.0
        else:
            trough=min(trough,shadow)
            if shadow/trough-1 >= Y:
                invested=True; peak=shadow
                if t+1<nfull: p[t+1:]=1.0
    return p,comb

def met(r):
    r=np.asarray(r); nav=np.cumprod(1+r); yrs=len(r)/SPY
    cg=nav[-1]**(1/yrs)-1; sh=np.mean(r)*SPY/(np.std(r)*np.sqrt(SPY)) if np.std(r)>0 else 0
    mdd=np.min(nav/np.maximum.accumulate(nav)-1); return cg,sh,mdd,cg/abs(mdd) if mdd else 0
def ddw(r,a,b):
    idx=v[(v.time>=a)&(v.time<=b)].index; nav=np.cumprod(1+np.asarray(r)[idx])
    return np.min(nav/np.maximum.accumulate(nav)-1)

EP=[("COVID20","2020-01-15","2020-05-01"),("Bear22","2022-04-01","2022-12-01"),
    ("Grind25","2025-09-04","2026-03-23")]

for VV in ["V5","V4"]:
    rets=v[VV+"r"].values
    bc,bs,bd,bcal=met(rets)
    print("="*94); print(f"  {VV} drawdown-stop (shadow-based) | full {v.time.min().date()}->{v.time.max().date()}"); print("="*94)
    print(f"  BASELINE {VV}: CAGR {bc*100:+.1f}%  Sharpe {bs:.2f}  MaxDD {bd*100:+.1f}%  Calmar {bcal:.2f}")
    be={l:ddw(rets,a,b) for l,a,b in EP}
    print(f"  {'episode DD baseline':<22}: COVID {be['COVID20']*100:+.1f}%  Bear22 {be['Bear22']*100:+.1f}%  Grind {be['Grind25']*100:+.1f}%")
    print(f"\n  {'X_stop / Y_reentry':<20}{'CAGR':>8}{'Sharpe':>8}{'MaxDD':>9}{'Calmar':>8}{'%cash':>7}  {'COVID':>7}{'Bear22':>8}{'Grind':>8}")
    print("  "+"-"*92)
    for X in [0.08,0.10,0.12,0.15]:
        for Y in [0.04,0.06]:
            p,comb=apply_stop(rets,X,Y)
            cg,sh,md,cal=met(comb); cashpct=(1-p).mean()*100
            e={l:ddw(comb,a,b) for l,a,b in EP}
            print(f"  X{int(X*100)}% / Y{int(Y*100)}%       {'':<2}{cg*100:>+7.1f}%{sh:>8.2f}{md*100:>+8.1f}%{cal:>8.2f}{cashpct:>6.0f}%  "
                  f"{e['COVID20']*100:>+6.1f}%{e['Bear22']*100:>+7.1f}%{e['Grind25']*100:>+7.1f}%")
    print()
print("Done.")
