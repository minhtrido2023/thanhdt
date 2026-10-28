#!/usr/bin/env python3
"""Execute locked Sprint 4 outcomes; local artifacts only."""
import json,os,csv,gzip
from collections import defaultdict
from datetime import date
import numpy as np
import pandas as pd
from sprint3_analyze import Index,boot,holm,loo

HERE=os.path.dirname(os.path.abspath(__file__));OUT=os.path.join(HERE,'out4');SEED=20260815

def reg(d,ycol):
    cols=[ycol,'ticker','anchor_date','dilution','discount','subtype','adv60','mom6m','rvol60']
    z=d[cols].dropna().copy();z=z[(z.adv60>0)]
    if len(z)<30:return {'n':len(z)}
    years=pd.get_dummies(z.anchor_date.str[:4],drop_first=True,dtype=float)
    X=np.column_stack([np.ones(len(z)),z.dilution,z.discount,(z.subtype=='PRIVATE_PLACEMENT').astype(float),np.log(z.adv60),z.mom6m,z.rvol60,years]);y=z[ycol].to_numpy()
    inv=np.linalg.pinv(X.T@X);b=inv@X.T@y;e=y-X@b
    def meat(g):
        M=np.zeros((X.shape[1],X.shape[1]))
        for q in np.unique(g):s=X[g==q].T@e[g==q];M+=np.outer(s,s)
        return M
    g1=z.ticker.to_numpy();g2=z.anchor_date.str[:7].to_numpy();g12=np.char.add(np.char.add(g1,'|'),g2)
    V=inv@(meat(g1)+meat(g2)-meat(g12))@inv;se=np.sqrt(np.maximum(np.diag(V),0))
    return {'n':len(z),'dilution_beta':float(b[1]),'dilution_t':float(b[1]/se[1]) if se[1] else None,
      'discount_beta':float(b[2]),'discount_t':float(b[2]/se[2]) if se[2] else None,
      'placement_beta':float(b[3]),'placement_t':float(b[3]/se[3]) if se[3] else None,'mcap_omitted':True}

def main():
    ew=pd.read_csv(os.path.join(HERE,'out2','ew_universe.csv'));bm=Index(ew.dt.tolist(),ew.ew_ret.to_numpy(float))
    r=pd.read_csv(os.path.join(OUT,'rights_panel.csv'),dtype={'icb':str});a=pd.read_csv(os.path.join(OUT,'ais_panel.csv'),dtype={'icb':str})
    for d in (r,a):
        d['month']=d.anchor_date.str[:7];d['issue_price']=d.total_value/d.issue_volume
    for h in (5,20,60):
        r[f'BHAR_{h}']=r[f'c_{h}']/r.c_0-1-bm.ret(r.d_0,r[f'd_{h}'])
        a[f'BHAR_{h}']=a[f'c_{h}']/a.c_m1-1-bm.ret(a.d_m1,a[f'd_{h}'])
    for d in (r,a):
        d['PLACEBO_20']=d.c_m20/d.c_m40-1-bm.ret(d.d_m40,d.d_m20)
        d['PRETREND_20']=d.c_m1/d.c_m21-1-bm.ret(d.d_m21,d.d_m1)
        d['FARBASE_20']=d.c_m230/d.c_m250-1-bm.ret(d.d_m250,d.d_m230)
    r['TERP']=(r.p_m1+r.ratio_total*r.issue_price)/(1+r.ratio_total)
    r['r_m1']=r.p_m1/r.c_m1;r['r_p1']=r.p_1/r.c_1
    mat=r[['p_1','p_2','p_3']].to_numpy()/r[['c_1','c_2','c_3']].to_numpy()
    r['r_stable']=np.nanmax(mat,axis=1)/np.nanmin(mat,axis=1)-1
    r['factor_err']=(r.r_m1/r.r_p1)/(r.p_m1/r.TERP)-1
    r['p_hat_0']=r.c_0*r.r_p1;r['terp_gap']=r.p_hat_0/r.TERP-1;r['discount']=1-r.issue_price/r.p_m1
    a['dilution']=a.ais_shares_delta/a.ais_shares_after;a['discount']=1-a.issue_price/a.p_m1
    a['AVOL0']=a.v_0/a.avol_pre-1;a['AVOL0_5']=a.avol_0_5/a.avol_pre-1

    rc=(r.in_universe_pit==1)&(r.v_0>0)&(r.n_adjust_21==0)&(r.ratio_total>0)&(r.ratio_total<=5)&(r.issue_volume>0)&(r.issue_price>0)&(r.issue_price<=5*r.p_m1)&(r.n_prices==1)
    rc=r[rc].copy()
    ac=(a.in_universe_pit==1)&(a.v_0>0)&(a.anchor_lag_days.between(0,5))&(a.ais_conflict==0)&(a.n_adjust_21==0)&(a.n_issue_21==0)
    ac=a[ac].copy();pooled=ac[ac.subtype.isin(['ESOP','PRIVATE_PLACEMENT'])].copy();rightsais=ac[ac.subtype=='RIGHTS'].copy()
    # Locked matched controls: remove contaminated candidates, then greedy no-replacement
    # assignment within month separately for rights-ex and pooled AIS families.
    mc=pd.read_csv(os.path.join(OUT,'match_candidates.csv'));adj=defaultdict(list)
    with gzip.open(os.path.join(HERE,'out','event_ledger.csv.gz'),'rt',newline='') as fh:
        for x in csv.DictReader(fh):
            if x['actionable']=='1' and x['is_price_adjusting']=='1' and x['exright_date']:
                adj[x['ticker']].append(date.fromisoformat(x['exright_date'][:10]))
    mc['event_day']=pd.to_datetime(mc.anchor_date).dt.date
    mc=mc[[not any(abs((z-ed).days)<=21 for z in adj[tk]) for tk,ed in zip(mc.control_ticker,mc.event_day)]].copy()
    rk=set(zip(rc.ticker,rc.d_0));ak=set(zip('AIS_'+pooled.subtype,pooled.ticker,pooled.d_0))
    def assign(cand,valid,ais=False):
        if ais:cand=cand[[k in valid for k in zip(cand.kind,cand.event_ticker,cand.anchor_date)]].copy()
        else:cand=cand[[k in valid for k in zip(cand.event_ticker,cand.anchor_date)]].copy()
        chosen=[]
        for month,gm in cand.groupby(cand.anchor_date.str[:7]):
            used=set();groups=list(gm.groupby(['kind','event_ticker','anchor_date']));groups.sort(key=lambda q:len(q[1]))
            for _,g in groups:
                av=g[~g.control_ticker.isin(used)].sort_values(['dist','control_ticker'])
                if len(av):x=av.iloc[0];used.add(x.control_ticker);chosen.append(x)
        z=pd.DataFrame(chosen)
        if len(z):z['MATCHED_DIFF_20']=(z.focal_end/z.focal_start-1)-(z.control_end/z.control_start-1);z['month']=z.anchor_date.str[:7]
        return z
    mr=assign(mc[mc.kind=='RIGHTS_EX'],rk);ma=assign(mc[mc.kind.isin(['AIS_ESOP','AIS_PRIVATE_PLACEMENT'])],ak,True)
    rh={f'R_{h}':boot(rc[f'BHAR_{h}'],rc.month,SEED+h) for h in (5,20,60)}
    ah={f'A_{h}':boot(pooled[f'BHAR_{h}'],pooled.month,SEED+100+h) for h in (5,20,60)}
    mech=rc[(rc.r_stable<=.001)&rc.factor_err.notna()]
    res={'funnel':{'rights_raw':len(r),'rights_core':len(rc),'rights_tickers':rc.ticker.nunique(),
      'ais_raw':len(a),'ais_core_pooled':len(pooled),'ais_core_pooled_tickers':pooled.ticker.nunique(),
      'ais_rights':len(rightsais),'ais_conflicts':int(a.ais_conflict.sum()),
      'dilution_valid_pooled':int(pooled.dilution.between(0,1).sum()),'mixed_terms_rights':int((r.n_prices>1).sum())},
      'rights_horizons':rh,'rights_holm':holm({k:v['p'] for k,v in rh.items()}),
      'ais_horizons':ah,'ais_holm':holm({k:v['p'] for k,v in ah.items()}),
      'rights_mechanical':{'n':len(mech),'stable_share':float((rc.r_stable<=.001).mean()),
        'factor_match_1pct':float((mech.factor_err.abs()<=.01).mean()),'terp_gap':boot(mech.terp_gap,mech.month,SEED+201)},
      'rights_splits':{},'ais_splits':{},'robustness':{},'dose_response':{}}
    for name,g in [('IS',rc[rc.anchor_date<='2019-12-31']),('OOS',rc[rc.anchor_date>'2019-12-31'])]:res['rights_splits'][name]=boot(g.BHAR_20,g.month,SEED+len(name))
    for name,g in [('IS',pooled[pooled.anchor_date<='2019-12-31']),('OOS',pooled[pooled.anchor_date>'2019-12-31']),('ESOP',pooled[pooled.subtype=='ESOP']),('PRIVATE_PLACEMENT',pooled[pooled.subtype=='PRIVATE_PLACEMENT']),('RIGHTS_AIS',rightsais)]:res['ais_splits'][name]=boot(g.BHAR_20,g.month,SEED+20+len(name))
    res['robustness']={'rights_placebo':boot(rc.PLACEBO_20,rc.month,SEED+301),'rights_pretrend':boot(rc.PRETREND_20,rc.month,SEED+302),'rights_farbase':boot(rc.FARBASE_20,rc.month,SEED+303),
      'ais_placebo':boot(pooled.PLACEBO_20,pooled.month,SEED+304),'ais_pretrend':boot(pooled.PRETREND_20,pooled.month,SEED+305),'ais_farbase':boot(pooled.FARBASE_20,pooled.month,SEED+306),
      'rights_loo':loo(rc,'BHAR_20','anchor_date'),'ais_loo':loo(pooled,'BHAR_20','anchor_date'),
      'rights_matched':boot(mr.MATCHED_DIFF_20,mr.month,SEED+308) if len(mr) else {'n':0},
      'ais_matched':boot(ma.MATCHED_DIFF_20,ma.month,SEED+309) if len(ma) else {'n':0},
      'rights_match_balance':{'n':len(mr),'max_abs_z':float(mr[['z_adv','z_mom','z_vol']].abs().max().max()) if len(mr) else None},
      'ais_match_balance':{'n':len(ma),'max_abs_z':float(ma[['z_adv','z_mom','z_vol']].abs().max().max()) if len(ma) else None},
      'rights_wide':boot(r[(r.v_0>0)&(r.n_adjust_21==0)&(r.ratio_total>0)&(r.ratio_total<=5)&(r.issue_price>0)&(r.issue_price<=5*r.p_m1)&(r.n_prices==1)].BHAR_20,r[(r.v_0>0)&(r.n_adjust_21==0)&(r.ratio_total>0)&(r.ratio_total<=5)&(r.issue_price>0)&(r.issue_price<=5*r.p_m1)&(r.n_prices==1)].month,SEED+307)}
    dose=pooled[pooled.dilution.between(0,1)&(pooled.issue_price>0)&(pooled.issue_price<=5*pooled.p_m1)].copy()
    res['dose_response']={'coverage_n':len(dose),'coverage_pct':len(dose)/max(len(pooled),1),'regression':reg(dose,'BHAR_20')}
    r.to_csv(os.path.join(OUT,'rights_analysis.csv'),index=False);a.to_csv(os.path.join(OUT,'ais_analysis.csv'),index=False)
    if len(mr):mr.to_csv(os.path.join(OUT,'rights_matched.csv'),index=False)
    if len(ma):ma.to_csv(os.path.join(OUT,'ais_matched.csv'),index=False)
    json.dump(res,open(os.path.join(OUT,'results.json'),'w'),indent=2,allow_nan=False);print(json.dumps(res,indent=2)[:14000]);return 0
if __name__=='__main__':raise SystemExit(main())
