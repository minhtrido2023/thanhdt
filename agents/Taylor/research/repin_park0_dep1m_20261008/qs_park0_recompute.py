import sys, numpy as np, pandas as pd
sys.path.insert(0,"/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-repin-dep1m-2809/WorkingClaude")
sys.path.insert(0,"/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/c30v_w2_q2_20260927")
import idle_rate_proxy as irp
import w2b_overlay as w
print("same irp module:", w.irp is irp, irp.__file__, "dep1m" in irp.TIERS)
P="v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_park3-%s_wtnamecap_advprice_etfcreatpit_exp_%s_univpit%s.csv"
L={"c_p30_off":P%("30","c_p30_off",""),"c_p30_1m":P%("30","c_p30_1m","_idledep1m"),"p0_off":P%("0","p0_off",""),"p0_1m":P%("0","p0_1m","_idledep1m")}
nav={};idle={}
for k,p in L.items():
    df=pd.read_csv(p,low_memory=False); d=df[df.record_type=="DAILY"].copy()
    d["t"]=pd.to_datetime(d.ymd); g=d.groupby(d.t.dt.normalize()).last()
    n=g.combined_nav.astype(float); nav[k]=n; idle[k]=(g.bal_cash_ref+g.lag_cash_ref).astype(float)
    yrs=(n.index[-1]-n.index[0]).days/365.25
    cagr=(n.iloc[-1]/n.iloc[0])**(1/yrs)-1
    dd=(n/n.cummax()-1); i=dd.idxmin(); pk=n.loc[:i].idxmax()
    print(k, len(n), n.index[0].date(), n.index[-1].date(), "final %.2fB"%(n.iloc[-1]/1e9), "CAGR %.3f"%(cagr*100), "MaxDD %.2f"%(dd.min()*100), pk.date(), i.date(), "calmar %.3f"%(cagr/-dd.min()), "idlefrac %.4f"%(idle[k]/n).mean(), "neg idle days", int((idle[k]<0).sum()))
# overlay & rate check
o,ns,rate=w.overlay(nav["p0_off"],idle["p0_off"],"dep1m")
yrs=(o.index[-1]-o.index[0]).days/365.25
print("rate mean",rate.mean()*100,"ov p0 CAGR",((o.iloc[-1]/o.iloc[0])**(1/yrs)-1)*100, "ovDD",(o/o.cummax()-1).min()*100,(o/o.cummax()-1).idxmin().date())
# yearly
for k in nav:
    y=nav[k].groupby(nav[k].index.year).last(); 
print("2019 idle frac p0_off", (idle["p0_off"]/nav["p0_off"])["2019"].mean(), "rate2019", rate[nav["p0_off"].index.year==2019].mean())
# DD path diag: p0_off vs p0_1m in 2019-2020
for k in ["p0_off","p0_1m"]:
    n=nav[k]; print(k, "2019-05-29", n["2019-05-29"]/1e9, "2020-02-13", n["2020-02-13"]/1e9, "2020-03-24", n["2020-03-24"]/1e9)
print("ov", o["2019-05-29"]/1e9, o["2020-02-13"]/1e9, o["2020-03-24"]/1e9)
# seed sensitivity of DD5 (circular block bootstrap L=21)
def boot_dd5(n, seed, B=4000, Lb=21):
    r=np.diff(np.log(n.values)); N=len(r); rng=np.random.default_rng(seed)
    nb=int(np.ceil(N/Lb)); out=np.empty(B)
    for b in range(B):
        st=rng.integers(0,N,nb); idx=((st[:,None]+np.arange(Lb))%N).ravel()[:N]
        c=np.cumsum(r[idx]); out[b]=(np.exp(c-np.maximum.accumulate(np.maximum(c,0)))-1).min()
    return np.percentile(out,5)*100
for k in ["c_p30_off","p0_off"]:
    print(k,"DD5 by seed",[round(boot_dd5(nav[k],s),2) for s in (1,2,3,12345)])
