#!/usr/bin/env python3
"""Execute locked Sprint 3 outcomes from out3/; no network or BigQuery access."""
from __future__ import annotations

import json
import os
import gzip
import csv
from collections import defaultdict
from datetime import date

import numpy as np
import pandas as pd

HERE=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.join(HERE,"out3")
EW=os.path.join(HERE,"out2","ew_universe.csv")
SEED=20260815
NBOOT=10_000
H=[5,10,20,60]


class Index:
    def __init__(self,dts,ret):
        self.d=np.asarray(dts,dtype=object); self.l=np.cumprod(1+np.nan_to_num(ret,nan=0.0))
    def level(self,s):
        keys=np.asarray([x if isinstance(x,str) else "" for x in s],dtype=object)
        ix=np.searchsorted(self.d,keys,side="right")-1
        z=np.full(len(ix),np.nan); ok=ix>=0; z[ok]=self.l[ix[ok]]; return z
    def ret(self,a,b):
        x,y=self.level(a),self.level(b)
        with np.errstate(divide="ignore",invalid="ignore"): return y/x-1


def boot(x,blocks,seed=SEED):
    x=np.asarray(x,float); blocks=np.asarray(blocks,dtype=object)
    m=np.isfinite(x); x=x[m]; blocks=blocks[m]
    if not len(x): return {"n":0,"mean":None,"lo":None,"hi":None,"p":None}
    u=np.unique(blocks); sums=np.array([x[blocks==b].sum() for b in u]); ns=np.array([(blocks==b).sum() for b in u])
    rng=np.random.default_rng(seed); draws=rng.integers(0,len(u),(NBOOT,len(u)))
    means=sums[draws].sum(1)/ns[draws].sum(1)
    lo,hi=np.percentile(means,[2.5,97.5]); p=2*min((means<=0).mean(),(means>=0).mean())
    q=np.percentile(x,[10,25,50,75,90])
    return {"n":int(len(x)),"n_blocks":int(len(u)),"mean":float(x.mean()),
      "lo":float(lo),"hi":float(hi),"p":float(min(1,p)),"p10":float(q[0]),
      "p25":float(q[1]),"median":float(q[2]),"p75":float(q[3]),"p90":float(q[4]),
      "share_positive":float((x>0).mean())}


def holm(d):
    items=sorted(((k,v) for k,v in d.items() if v is not None and np.isfinite(v)),key=lambda z:z[1]); n=len(items); out={}; run=0
    for i,(k,p) in enumerate(items): run=max(run,min(1,(n-i)*p)); out[k]=run
    return out


def loo(d,col,datecol):
    x=d[d[col].notna()].copy(); x["yr"]=x[datecol].str[:4].astype(int); total=x[col].sum()
    rows=[]
    for y,g in x.groupby("yr"):
        rest=x[x.yr!=y]
        rows.append({"year":int(y),"n":len(g),"mean":float(g[col].mean()),
          "mean_without":float(rest[col].mean()),"effect_share":float(g[col].sum()/total) if total else None})
    carrier=max(rows,key=lambda z:abs(z["effect_share"] or 0)) if rows else None
    return {"rows":rows,"carrier_year":carrier["year"] if carrier else None,
      "carrier_share":carrier["effect_share"] if carrier else None,
      "sign_flip":any(np.sign(z["mean_without"])!=np.sign(x[col].mean()) for z in rows)}


def twoway_ols(d,ycol):
    z=d[[ycol,"ticker","ex_date","ratio_total","subtype_list","adtv_pre","mom6m","rvol60"]].dropna().copy()
    z=z[(z.adtv_pre>0)&(z.ratio_total>0)]
    years=pd.get_dummies(z.ex_date.str[:4],drop_first=True,dtype=float)
    X=np.column_stack([np.ones(len(z)),np.log1p(z.ratio_total),
      (z.subtype_list=="BONUS").astype(float),np.log(z.adtv_pre),z.mom6m,z.rvol60,years])
    y=z[ycol].to_numpy(); inv=np.linalg.pinv(X.T@X); beta=inv@X.T@y; e=y-X@beta
    def meat(g):
        M=np.zeros((X.shape[1],X.shape[1]))
        for q in np.unique(g):
            s=X[g==q].T@e[g==q]; M+=np.outer(s,s)
        return M
    g1=z.ticker.to_numpy(); g2=z.ex_date.str[:7].to_numpy(); g12=np.char.add(np.char.add(g1,"|"),g2)
    V=inv@(meat(g1)+meat(g2)-meat(g12))@inv; se=np.sqrt(np.maximum(np.diag(V),0))
    return {"n":len(z),"ratio_log_beta":float(beta[1]),"ratio_log_se":float(se[1]),
      "ratio_log_t":float(beta[1]/se[1]) if se[1] else None,
      "bonus_beta":float(beta[2]),"bonus_t":float(beta[2]/se[2]) if se[2] else None,
      "mcap_omitted":True}


def main():
    d=pd.read_csv(os.path.join(OUT,"linked_panel.csv"),dtype={"icb":str})
    ew=pd.read_csv(EW); bm=Index(ew.dt.tolist(),ew.ew_ret.to_numpy(float))
    for h in H:
        d[f"BHAR_EX_{h}"]=d[f"c_{h}"]/d.c_0-1-bm.ret(d.d_0,d[f"d_{h}"])
    d["AR_EX"]=d.c_0/d.c_m1-1-bm.ret(d.d_m1,d.d_0)
    d["PLACEBO_20"]=d.c_m20/d.c_m40-1-bm.ret(d.d_m40,d.d_m20)
    d["PRETREND_20"]=d.c_m1/d.c_m21-1-bm.ret(d.d_m21,d.d_m1)
    d["FARBASE_20"]=d.c_m230/d.c_m250-1-bm.ret(d.d_m250,d.d_m230)
    d["r_m1"]=d.p_m1/d.c_m1; d["r_p1"]=d.p_1/d.c_1
    d["r_stable"]=(d[["p_1","p_2","p_3"]].to_numpy()/d[["c_1","c_2","c_3"]].to_numpy()).max(1)/(d[["p_1","p_2","p_3"]].to_numpy()/d[["c_1","c_2","c_3"]].to_numpy()).min(1)-1
    d["factor_err"]=(d.r_m1/d.r_p1)/(1+d.ratio_total)-1
    d["p_hat_0"]=d.c_0*d.r_p1; d["p_ref"]=d.p_m1/(1+d.ratio_total)
    d["raw_ref_gap"]=d.p_hat_0/d.p_ref-1
    d["DLOG_ADTV_EX"]=np.log(d.adtv_post.where(d.adtv_post>0))-np.log(d.adtv_pre.where(d.adtv_pre>0))
    for h in (5,20,60):
        d[f"BHAR_AIS_{h}"]=d[f"ais_c_{h}"]/d.ais_c_m1-1-bm.ret(d.ais_d_m1,d[f"ais_d_{h}"])
    d["AIS_AVOL0"]=d.ais_v_0/d.ais_avol_pre-1
    d["AIS_AVOL0_5"]=d.ais_avol_0_5/d.ais_avol_pre-1
    d["supply_intensity"]=d.ais_shares_delta/d.ais_shares_total_after

    base=(d.in_universe_pit==1)&(d.ratio_total>0)&(d.ratio_total<=2)&(d.v_0>0)&(d.n_other_adjust_21==0)
    core=d[base].copy(); core["month"]=core.ex_date.str[:7]
    ais=core[core.ais_link_tier.isin(["A","B"])&(core.ais_conflict==0)&
      (core.n_other_ais_21==0)&(core.n_adjust_at_ais_21==0)&core.ais_c_m1.notna()].copy()
    ais["ais_month"]=ais.ais_date.str[:7]

    # Greedy no-replacement-within-month match. Events with fewer candidates go first. Controls
    # with another price-adjusting action in ±21 calendar days are removed before assignment.
    mc=pd.read_csv(os.path.join(OUT,"match_candidates.csv"))
    adj=defaultdict(list)
    with gzip.open(os.path.join(HERE,"out","event_ledger.csv.gz"),"rt",newline="") as fh:
        for r in csv.DictReader(fh):
            if r["actionable"]=="1" and r["is_price_adjusting"]=="1" and r["exright_date"]:
                adj[r["ticker"]].append(date.fromisoformat(r["exright_date"][:10]))
    valid_keys=set(zip(core.ticker,core.ex_date)); mc=mc[[k in valid_keys for k in zip(mc.event_ticker,mc.ex_date)]].copy()
    mc["event_day"]=pd.to_datetime(mc.ex_date).dt.date
    mc=mc[[not any(abs((x-ed).days)<=21 for x in adj[tk])
           for tk,ed in zip(mc.control_ticker,mc.event_day)]].copy()
    chosen=[]
    for month,gmonth in mc.groupby(mc.ex_date.str[:7]):
        used=set(); groups=list(gmonth.groupby(["event_ticker","ex_date"]))
        groups.sort(key=lambda z:len(z[1]))
        for key,g in groups:
            avail=g[~g.control_ticker.isin(used)].sort_values(["dist","control_ticker"])
            if len(avail):
                x=avail.iloc[0]; used.add(x.control_ticker); chosen.append(x)
    matched=pd.DataFrame(chosen)
    if len(matched):
        matched["MATCHED_DIFF_20"]=(matched.focal_c20/matched.focal_c0-1)-(
            matched.control_c20/matched.control_c0-1)
        matched["month"]=matched.ex_date.str[:7]
        matched.to_csv(os.path.join(OUT,"matched_control.csv"),index=False)

    ex_h={f"EX_{h}":boot(core[f"BHAR_EX_{h}"],core.month,SEED+h) for h in H}
    ais_h={f"AIS_{h}":boot(ais[f"BHAR_AIS_{h}"],ais.ais_month,SEED+100+h) for h in (5,20,60)}
    result={"funnel":{"raw_panel":len(d),"core":len(core),"core_tickers":core.ticker.nunique(),
      "ais_confirmatory":len(ais),"ais_tickers":ais.ticker.nunique(),
      "ratio_gt_200pct":int((d.ratio_total>2).sum()),"ais_conflicts":int(d.ais_conflict.sum())},
      "ex_horizons":ex_h,"ex_holm":holm({k:v["p"] for k,v in ex_h.items()}),
      "ais_horizons":ais_h,"ais_holm":holm({k:v["p"] for k,v in ais_h.items()}),
      "primary_splits":{},"liquidity":{},"mechanical":{},"robustness":{},
      "regression":{"bhar_ex20":twoway_ols(core,"BHAR_EX_20"),
                    "dlog_adtv":twoway_ols(core,"DLOG_ADTV_EX")}}
    for name,g in [("IS",core[core.ex_date<="2019-12-31"]),("OOS",core[core.ex_date>"2019-12-31"]),
      ("STOCK_DIVIDEND",core[core.subtype_list=="STOCK_DIVIDEND"]),("BONUS",core[core.subtype_list=="BONUS"]),
      ("MIXED",core[core.n_subtypes>1])]:
        result["primary_splits"][name]=boot(g.BHAR_EX_20,g.month,SEED+len(name))
    result["liquidity"]={"dlog_adtv":boot(core.DLOG_ADTV_EX,core.month,SEED+201),
      "by_subtype":{s:boot(g.DLOG_ADTV_EX,g.month,SEED+202+i) for i,(s,g) in enumerate(core.groupby("subtype_list"))}}
    result["ais_splits"]={
      "IS":boot(ais[ais.ais_date<="2019-12-31"].BHAR_AIS_20,
                ais[ais.ais_date<="2019-12-31"].ais_month,SEED+211),
      "OOS":boot(ais[ais.ais_date>"2019-12-31"].BHAR_AIS_20,
                 ais[ais.ais_date>"2019-12-31"].ais_month,SEED+212),
      "TIER_A_ONLY":boot(ais[ais.ais_link_tier=="A"].BHAR_AIS_20,
                         ais[ais.ais_link_tier=="A"].ais_month,SEED+213)}
    mech=core[(core.r_stable<=.001)&core.factor_err.notna()]
    result["mechanical"]={"n":len(mech),"stable_ratio_share":float((core.r_stable<=.001).mean()),
      "factor_match_0p2pct":float((mech.factor_err.abs()<=.002).mean()),
      "factor_match_1pct":float((mech.factor_err.abs()<=.01).mean()),
      "raw_ref_gap":boot(mech.raw_ref_gap,mech.month,SEED+203)}
    result["robustness"]={"placebo":boot(core.PLACEBO_20,core.month,SEED+204),
      "pretrend":boot(core.PRETREND_20,core.month,SEED+205),
      "farbase":boot(core.FARBASE_20,core.month,SEED+206),
      "loo":loo(core,"BHAR_EX_20","ex_date"),
      "wide":boot(d[(d.ratio_total>0)&(d.ratio_total<=2)&(d.v_0>0)&(d.n_other_adjust_21==0)].BHAR_EX_20,
                  d[(d.ratio_total>0)&(d.ratio_total<=2)&(d.v_0>0)&(d.n_other_adjust_21==0)].ex_date.str[:7],SEED+207),
      "matched_control":boot(matched.MATCHED_DIFF_20,matched.month,SEED+208) if len(matched) else {"n":0},
      "matched_balance":{"n":len(matched),"median_distance":float(matched.dist.median()) if len(matched) else None,
                         "max_abs_z":float(matched[["z_adv","z_mom","z_vol"]].abs().max().max()) if len(matched) else None}}
    d.to_csv(os.path.join(OUT,"analysis_panel.csv"),index=False)
    with open(os.path.join(OUT,"results.json"),"w") as fh: json.dump(result,fh,indent=2,allow_nan=False)
    print(json.dumps(result,indent=2)[:12000]); return 0


if __name__=="__main__": raise SystemExit(main())
