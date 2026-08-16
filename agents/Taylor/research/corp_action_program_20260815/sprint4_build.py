#!/usr/bin/env python3
"""Build read-only Sprint 4 rights and issuance-arrival panels."""
from __future__ import annotations
import csv,gzip,json,os,shutil,subprocess
from collections import defaultdict
from datetime import date,timedelta

HERE=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.join(HERE,"out4"); SQL=os.path.join(OUT,"sql")
PROJECT="lithe-record-440915-m9"; START="2013-01-01"; DMIN="2014-01-01"; DMAX="2026-06-30"

def bq(sql,name,timeout=1800):
    os.makedirs(SQL,exist_ok=True); pth=os.path.join(SQL,name+".sql"); open(pth,"w").write(sql)
    exe=shutil.which("bq") or "/home/trido/google-cloud-sdk/bin/bq"; env=os.environ.copy()
    env["PATH"]="/home/trido/google-cloud-sdk/bin:"+env.get("PATH",""); env.setdefault("CLOUDSDK_CONFIG","/home/trido/thanhdt/gcloud_dtienthanh")
    with open(pth) as fh: p=subprocess.run([exe,"query","--use_legacy_sql=false","--format=csv",f"--project_id={PROJECT}","--max_rows=2000000","--quiet"],stdin=fh,text=True,capture_output=True,timeout=timeout,env=env)
    if p.returncode: raise RuntimeError(p.stdout[-4000:]+p.stderr[-4000:])
    lines=[x for x in p.stdout.splitlines() if x.strip()]; return list(csv.DictReader(lines)) if lines else []

def f(x):
    try:return float(x) if x not in (None,"","NULL") else None
    except:return None
def dt(x): return date.fromisoformat(x[:10]) if x else None
def dump(name,rows):
    if not rows:return
    with open(os.path.join(OUT,name),"w",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

RAW=f"""
raw AS (
 SELECT c.*,
  CASE c.issue_method_code WHEN 'Rights' THEN 'RIGHTS' WHEN 'EMPL' THEN 'ESOP' WHEN 'PP' THEN 'PRIVATE_PLACEMENT' END subtype,
  ROW_NUMBER() OVER(PARTITION BY c.ticker,c.exright_date,c.issue_method_code,
    CAST(c.exercise_ratio AS STRING),CAST(c.issue_volumn AS STRING),CAST(c.total_value AS STRING)
    ORDER BY c.public_date DESC,c.id DESC) rn
 FROM `{PROJECT}.tav2_bq.corporate_action` c
 WHERE c.event_code='ISS' AND c.event_status='executed' AND c.issue_method_code IN ('Rights','EMPL','PP')
), dedup AS (SELECT * FROM raw WHERE rn=1)
"""

RIGHTS=f"""WITH {RAW}, ev AS (
 SELECT ticker,exright_date anchor_date,'RIGHTS' subtype,SUM(exercise_ratio) ratio_total,
  SUM(issue_volumn) issue_volume,SUM(total_value) total_value,COUNT(*) n_components,
  COUNT(DISTINCT ROUND(SAFE_DIVIDE(total_value,issue_volumn),2)) n_prices,
  MAX(listing_date) listing_date
 FROM dedup WHERE subtype='RIGHTS' AND exright_date BETWEEN DATE '{DMIN}' AND DATE '{DMAX}'
 GROUP BY ticker,anchor_date
), px AS (
 SELECT t.ticker,t.time,t.Close,t.Price,t.Volume,t.ICB_Code,
  SAFE_DIVIDE(t.Close,LAG(t.Close) OVER(PARTITION BY t.ticker ORDER BY t.time))-1 ret,
  ROW_NUMBER() OVER(PARTITION BY t.ticker ORDER BY t.time) si
 FROM `{PROJECT}.tav2_bq.ticker` t WHERE t.time>=DATE '{START}' AND t.Close>0 AND t.ticker IN(SELECT ticker FROM ev)
), a AS (SELECT e.*,p.si si0 FROM ev e JOIN px p ON p.ticker=e.ticker AND p.time=e.anchor_date),
w AS (SELECT a.*,p.si-a.si0 k,p.time dt,p.Close,p.Price,p.Volume,p.ICB_Code,p.ret FROM a JOIN px p ON p.ticker=a.ticker AND p.si BETWEEN a.si0-250 AND a.si0+62)
SELECT ticker,anchor_date,ANY_VALUE(subtype) subtype,ANY_VALUE(ratio_total) ratio_total,ANY_VALUE(issue_volume) issue_volume,
 ANY_VALUE(total_value) total_value,ANY_VALUE(n_components) n_components,ANY_VALUE(n_prices) n_prices,ANY_VALUE(listing_date) listing_date,
 MAX(IF(k=-250,Close,NULL)) c_m250,MAX(IF(k=-250,dt,NULL)) d_m250,MAX(IF(k=-230,Close,NULL)) c_m230,MAX(IF(k=-230,dt,NULL)) d_m230,
 MAX(IF(k=-40,Close,NULL)) c_m40,MAX(IF(k=-40,dt,NULL)) d_m40,MAX(IF(k=-21,Close,NULL)) c_m21,MAX(IF(k=-21,dt,NULL)) d_m21,
 MAX(IF(k=-20,Close,NULL)) c_m20,MAX(IF(k=-20,dt,NULL)) d_m20,MAX(IF(k=-1,Close,NULL)) c_m1,MAX(IF(k=-1,Price,NULL)) p_m1,MAX(IF(k=-1,dt,NULL)) d_m1,
 MAX(IF(k=0,Close,NULL)) c_0,MAX(IF(k=0,dt,NULL)) d_0,MAX(IF(k=0,Volume,NULL)) v_0,
 MAX(IF(k=1,Close,NULL)) c_1,MAX(IF(k=1,Price,NULL)) p_1,MAX(IF(k=2,Close,NULL)) c_2,MAX(IF(k=2,Price,NULL)) p_2,MAX(IF(k=3,Close,NULL)) c_3,MAX(IF(k=3,Price,NULL)) p_3,
 MAX(IF(k=5,Close,NULL)) c_5,MAX(IF(k=5,dt,NULL)) d_5,MAX(IF(k=20,Close,NULL)) c_20,MAX(IF(k=20,dt,NULL)) d_20,MAX(IF(k=60,Close,NULL)) c_60,MAX(IF(k=60,dt,NULL)) d_60,
 AVG(IF(k BETWEEN -60 AND -6,Price*Volume,NULL)) adv60,STDDEV(IF(k BETWEEN -60 AND -1,ret,NULL)) rvol60,
 EXP(SUM(IF(k BETWEEN -126 AND -21,LN(1+ret),0)))-1 mom6m,MAX(IF(k=-1,ICB_Code,NULL)) icb
FROM w GROUP BY ticker,anchor_date ORDER BY ticker,anchor_date"""

AIS=f"""WITH {RAW}, ev AS (
 SELECT ticker,listing_date anchor_date,subtype,SUM(issue_volumn) issue_volume,SUM(total_value) total_value,
  COUNT(*) n_components,COUNT(DISTINCT ROUND(SAFE_DIVIDE(total_value,issue_volumn),2)) n_prices,
  MIN(exright_date) reference_date
 FROM dedup WHERE subtype IN('RIGHTS','ESOP','PRIVATE_PLACEMENT') AND listing_date BETWEEN DATE '{DMIN}' AND DATE '{DMAX}'
 GROUP BY ticker,anchor_date,subtype
), px AS (
 SELECT t.ticker,t.time,t.Close,t.Price,t.Volume,t.ICB_Code,
  SAFE_DIVIDE(t.Close,LAG(t.Close) OVER(PARTITION BY t.ticker ORDER BY t.time))-1 ret,
  ROW_NUMBER() OVER(PARTITION BY t.ticker ORDER BY t.time) si
 FROM `{PROJECT}.tav2_bq.ticker` t WHERE t.time>=DATE '{START}' AND t.Close>0 AND t.ticker IN(SELECT ticker FROM ev)
), first AS (SELECT e.ticker,e.anchor_date,e.subtype,ANY_VALUE(e.issue_volume) issue_volume,ANY_VALUE(e.total_value) total_value,
 ANY_VALUE(e.n_components)n_components,ANY_VALUE(e.n_prices)n_prices,ANY_VALUE(e.reference_date)reference_date,MIN(p.time) trading_date
 FROM ev e JOIN px p ON p.ticker=e.ticker AND p.time>=e.anchor_date GROUP BY e.ticker,e.anchor_date,e.subtype),
a AS (SELECT f.*,p.si si0 FROM first f JOIN px p ON p.ticker=f.ticker AND p.time=f.trading_date),
w AS (SELECT a.*,p.si-a.si0 k,p.time dt,p.Close,p.Volume,p.Price,p.ICB_Code,p.ret FROM a JOIN px p ON p.ticker=a.ticker AND p.si BETWEEN a.si0-250 AND a.si0+62)
SELECT ticker,anchor_date,ANY_VALUE(trading_date)trading_date,ANY_VALUE(subtype)subtype,ANY_VALUE(issue_volume)issue_volume,ANY_VALUE(total_value)total_value,
 ANY_VALUE(n_components)n_components,ANY_VALUE(n_prices)n_prices,ANY_VALUE(reference_date)reference_date,
 MAX(IF(k=-250,Close,NULL))c_m250,MAX(IF(k=-250,dt,NULL))d_m250,MAX(IF(k=-230,Close,NULL))c_m230,MAX(IF(k=-230,dt,NULL))d_m230,
 MAX(IF(k=-40,Close,NULL))c_m40,MAX(IF(k=-40,dt,NULL))d_m40,MAX(IF(k=-21,Close,NULL))c_m21,MAX(IF(k=-21,dt,NULL))d_m21,
 MAX(IF(k=-20,Close,NULL))c_m20,MAX(IF(k=-20,dt,NULL))d_m20,MAX(IF(k=-1,Close,NULL))c_m1,MAX(IF(k=-1,Price,NULL))p_m1,MAX(IF(k=-1,dt,NULL))d_m1,
 MAX(IF(k=0,Close,NULL))c_0,MAX(IF(k=0,dt,NULL))d_0,MAX(IF(k=0,Volume,NULL))v_0,
 MAX(IF(k=5,Close,NULL))c_5,MAX(IF(k=5,dt,NULL))d_5,MAX(IF(k=20,Close,NULL))c_20,MAX(IF(k=20,dt,NULL))d_20,MAX(IF(k=60,Close,NULL))c_60,MAX(IF(k=60,dt,NULL))d_60,
 AVG(IF(k BETWEEN -60 AND -6,Volume,NULL))avol_pre,AVG(IF(k BETWEEN 0 AND 5,Volume,NULL))avol_0_5,
 AVG(IF(k BETWEEN -60 AND -6,Price*Volume,NULL))adv60,STDDEV(IF(k BETWEEN -60 AND -1,ret,NULL))rvol60,
 EXP(SUM(IF(k BETWEEN -126 AND -21,LN(1+ret),0)))-1 mom6m,MAX(IF(k=-1,ICB_Code,NULL))icb
FROM w GROUP BY ticker,anchor_date ORDER BY ticker,anchor_date"""

AIS_ROWS=f"""SELECT ticker,effective_date ais_date,shares_delta,shares_total_after FROM `{PROJECT}.tav2_bq.corporate_action`
WHERE event_code='AIS' AND event_status='executed' AND effective_date BETWEEN DATE '{DMIN}' AND DATE '2027-06-30' ORDER BY ticker,ais_date"""

def ledger():
    with gzip.open(os.path.join(HERE,"out","event_ledger.csv.gz"),"rt",newline="") as fh:return list(csv.DictReader(fh))

def match_sql(rows):
    """Return SQL for candidate ranking based only on pre-outcome characteristics."""
    ss=[]
    for x in rows:
        vals=[f(x.get(k)) for k in ('adv60','mom6m','rvol60')]
        if not all(v is not None and v==v for v in vals):continue
        kind=x['_kind']; anchor=x.get('trading_date') or x['anchor_date']
        start=x['d_0'] if kind=='RIGHTS_EX' else x['d_m1']; end=x['d_20']
        cs=x['c_0'] if kind=='RIGHTS_EX' else x['c_m1'];ce=x['c_20']
        if not all((anchor,start,end,cs,ce)):continue
        tk=x['ticker'].replace("'","''");icb=str(x.get('icb') or '').replace("'","''")
        ss.append(f"STRUCT('{kind}' AS kind,'{tk}' AS event_ticker,DATE '{anchor}' AS anchor_date,DATE '{start}' AS start_date,DATE '{end}' AS end_date,{vals[0]} AS f_adv,{vals[1]} AS f_mom,{vals[2]} AS f_vol,'{icb}' AS f_icb,{cs} AS focal_start,{ce} AS focal_end)")
    return f"""WITH anchors AS (SELECT * FROM UNNEST([{','.join(ss)}])), p0 AS (
 SELECT t.ticker,t.time,t.Close,t.Price,t.Volume,t.ICB_Code,
  SAFE_DIVIDE(t.Close,LAG(t.Close) OVER(PARTITION BY t.ticker ORDER BY t.time))-1 ret,
  LAG(t.Close,21) OVER(PARTITION BY t.ticker ORDER BY t.time)c_l21,LAG(t.Close,126) OVER(PARTITION BY t.ticker ORDER BY t.time)c_l126
 FROM `{PROJECT}.tav2_bq.ticker` t WHERE t.time>=DATE '{START}' AND t.Close>0
), p AS (SELECT *,AVG(Price*Volume) OVER(PARTITION BY ticker ORDER BY time ROWS BETWEEN 60 PRECEDING AND 6 PRECEDING)adv,
 STDDEV(ret) OVER(PARTITION BY ticker ORDER BY time ROWS BETWEEN 60 PRECEDING AND 1 PRECEDING)vol,
 SAFE_DIVIDE(c_l21,c_l126)-1 mom FROM p0), c0 AS (
 SELECT a.*,p.ticker control_ticker,ps.Close control_start,pe.Close control_end,
  SAFE_DIVIDE(LN(NULLIF(p.adv,0))-LN(NULLIF(a.f_adv,0)),NULLIF(STDDEV(LN(NULLIF(p.adv,0))) OVER(PARTITION BY a.kind,a.event_ticker,a.anchor_date),0))z_adv,
  SAFE_DIVIDE(p.mom-a.f_mom,NULLIF(STDDEV(p.mom) OVER(PARTITION BY a.kind,a.event_ticker,a.anchor_date),0))z_mom,
  SAFE_DIVIDE(p.vol-a.f_vol,NULLIF(STDDEV(p.vol) OVER(PARTITION BY a.kind,a.event_ticker,a.anchor_date),0))z_vol
 FROM anchors a JOIN `{PROJECT}.tav2_mike.universe_pit` u ON u.time=a.anchor_date AND u.in_universe
 JOIN p ON p.ticker=u.ticker AND p.time=a.anchor_date JOIN p ps ON ps.ticker=p.ticker AND ps.time=a.start_date
 JOIN p pe ON pe.ticker=p.ticker AND pe.time=a.end_date
 WHERE p.ticker!=a.event_ticker AND p.adv>0 AND p.mom IS NOT NULL AND p.vol IS NOT NULL
 AND SUBSTR(CAST(p.ICB_Code AS STRING),1,1)=SUBSTR(a.f_icb,1,1)
), ranked AS (SELECT *,SQRT(z_adv*z_adv+z_mom*z_mom+z_vol*z_vol)dist,
 ROW_NUMBER() OVER(PARTITION BY kind,event_ticker,anchor_date ORDER BY z_adv*z_adv+z_mom*z_mom+z_vol*z_vol,control_ticker)rank
 FROM c0 WHERE ABS(z_adv)<=.5 AND ABS(z_mom)<=.5 AND ABS(z_vol)<=.5)
SELECT * FROM ranked WHERE rank<=50 ORDER BY kind,event_ticker,anchor_date,rank"""

def main():
    os.makedirs(OUT,exist_ok=True); print('[1/3] rights panel'); rp=bq(RIGHTS,'q1_rights_panel')
    print('[2/3] AIS issuance panel'); ap=bq(AIS,'q2_ais_panel'); ar=bq(AIS_ROWS,'q3_ais_rows')
    led=ledger(); adjust=defaultdict(list); issuance=defaultdict(list); aisby=defaultdict(list)
    for x in led:
        if x['event_family']=='ADDITIONAL_LISTING' and x['effective_date']: aisby[x['ticker']].append(x)
        if x['actionable']!='1':continue
        if x['is_price_adjusting']=='1' and x['exright_date']:adjust[x['ticker']].append((dt(x['exright_date']),x['event_subtype']))
        if x['event_subtype'] in ('RIGHTS','ESOP','PRIVATE_PLACEMENT'):issuance[x['ticker']].append(x)
    def add_common(rows,is_rights):
        out=[]
        for r in rows:
            anchor=dt(r['anchor_date']); tk=r['ticker']; trading=dt(r.get('trading_date') or r['anchor_date'])
            rr={k:(v if k in ('ticker','anchor_date','trading_date','subtype','reference_date','listing_date','icb') or k.startswith('d_') else f(v)) for k,v in r.items()}
            rr['anchor_lag_days']=(trading-anchor).days
            if is_rights:
                rr['in_universe_pit']=None
                focal=('RIGHTS',anchor)
                rr['n_adjust_21']=sum(abs((x-anchor).days)<=21 and not(x==anchor and sub=='RIGHTS') for x,sub in adjust[tk])
                rr['n_adjust_90']=sum(-21<=(x-anchor).days<=90 and not(x==anchor and sub=='RIGHTS') for x,sub in adjust[tk])
            else:
                rr['n_adjust_21']=sum(abs((x-trading).days)<=21 for x,_ in adjust[tk])
                rr['n_issue_21']=sum(bool(y['listing_date']) and abs((dt(y['listing_date'])-trading).days)<=21 and not(dt(y['listing_date'])==anchor and y['event_subtype']==r['subtype']) for y in issuance[tk])
                cand=[x for x in aisby[tk] if x['effective_date'] and abs((dt(x['effective_date'])-anchor).days)<=5]
                cand365=[x for x in aisby[tk] if x['effective_date'] and abs((dt(x['effective_date'])-anchor).days)<=365]
                rr['ais_candidates_5d']=len(cand);rr['ais_conflict']=0
                if cand:
                    best=min(cand,key=lambda x:abs((dt(x['effective_date'])-anchor).days));iv=f(r['issue_volume']) or 0;sv=f(best['shares_delta']) or 0
                    rr['ais_shares_delta']=sv;rr['ais_shares_after']=f(best['shares_total_after'])
                    if iv and abs(iv-sv)>max(.02*iv,1000):rr['ais_conflict']=1
                else:
                    rr['ais_shares_delta']=None;rr['ais_shares_after']=None
                    if cand365: rr['ais_conflict']=1
            out.append(rr)
        return out
    rp=add_common(rp,True);ap=add_common(ap,False)
    # Universe membership in one read-only query for every anchor trading date.
    keys=[(x['ticker'],x.get('trading_date') or x['anchor_date']) for x in rp+ap]
    vals=','.join("('%s',DATE '%s')"%k for k in keys)
    uq=f"WITH k AS (SELECT * FROM UNNEST([{vals}]) AS x) SELECT 1" if False else None
    # Querying all pairs via a large literal is avoidable: pull relevant universe rows once.
    uni=bq(f"SELECT ticker,time,in_universe,backfilled FROM `{PROJECT}.tav2_mike.universe_pit` WHERE time BETWEEN DATE '{DMIN}' AND DATE '{DMAX}' AND in_universe",'q4_universe')
    uset={(x['ticker'],x['time']) for x in uni};bset={(x['ticker'],x['time']) for x in uni if x['backfilled']=='true'}
    for x in rp+ap:
        key=(x['ticker'],x.get('trading_date') or x['anchor_date']);x['in_universe_pit']=int(key in uset);x['univ_backfilled']=int(key in bset)
    print('[3/3] matched-control candidates')
    for x in rp:x['_kind']='RIGHTS_EX'
    for x in ap:x['_kind']='AIS_'+x['subtype']
    mc=bq(match_sql(rp+ap),'q5_match_candidates',timeout=2400)
    for x in rp+ap:x.pop('_kind',None)
    dump('rights_panel.csv',rp);dump('ais_panel.csv',ap);dump('ais_rows.csv',ar);dump('match_candidates.csv',mc)
    s={'rights_price_session':len(rp),'rights_core_univ':sum(x['in_universe_pit'] for x in rp),'ais_price_session':len(ap),
       'ais_by_subtype':{z:sum(x['subtype']==z for x in ap) for z in ('RIGHTS','ESOP','PRIVATE_PLACEMENT')},
       'ais_conflicts':sum(x['ais_conflict'] for x in ap),'ais_with_share_match':sum(x['ais_shares_after'] is not None for x in ap),
       'match_candidate_rows':len(mc),'events_with_match':len(set((x['kind'],x['event_ticker'],x['anchor_date']) for x in mc))}
    json.dump(s,open(os.path.join(OUT,'build_summary.json'),'w'),indent=2);print(json.dumps(s,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
