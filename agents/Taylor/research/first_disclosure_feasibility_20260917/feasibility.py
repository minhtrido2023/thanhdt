import pandas as pd, numpy as np
D="/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/first_disclosure_feasibility_20260917"
f=pd.read_pickle(f"{D}/_f.pkl")
a=pd.read_csv(f"{D}/q10_master_extract.csv",low_memory=False,dtype={'sid':str},parse_dates=['exright_date','public_date','record_date'])
div=a[(a.event_code=='DIV')&(a.exright_date>='2014-01-01')&(a.exright_date<='2026-09-30')&(a.value_per_share>0)&(a.event_status!='not_executed')].copy()
pr=pd.read_csv(f"{D}/q12_prune_membership.csv")
div['in_prune']=div.id.isin(pr[pr.n_prune_days>0].id)
div=div.merge(f[['id','fd_date_naive','lead_ex_naive','lead_rec_naive','tz_date_differs']],on='id',how='left')
div['fd']=pd.to_datetime(div.fd)
sh_sid=pd.read_csv(f"{D}/div_shared_sid_distinct_exdates.csv",dtype={'sid':str})
sh_fd=pd.read_csv(f"{D}/div_shared_fd_distinct_exdates.csv",parse_dates=['fd'])
bad_sid=set(zip(sh_sid.ticker,sh_sid.sid)); bad_fd=set(zip(sh_fd.ticker,sh_fd.fd))
div['has_fd']=div.fd.notna()
div['pit_viol']=div.has_fd&((div.lead_ex_naive<=0)|(div.lead_rec_naive<0)|(div.fd_date_naive>div.public_date)|div.exright_date.isna())
div['eq_public']=div.has_fd&(div.fd_date_naive==div.public_date)
div['shared']=div.has_fd&([ (t,s) in bad_sid for t,s in zip(div.ticker,div.sid)] | pd.Series([(t,x) in bad_fd for t,x in zip(div.ticker,div.fd)],index=div.index))
div['lead_gt120']=div.has_fd&(div.lead_ex_naive>120)
div['valid']=div.has_fd&~div.pit_viol&~div.eq_public&~div.shared&~div.lead_gt120
div['yr']=div.exright_date.dt.year
div['seg']=np.where(div.yr<=2019,'IS_2014_19','OOS_2020p')
rows=[]
for uni,x in [('all_tickers',div),('ticker_prune',div[div.in_prune])]:
    for yr,g in x.groupby('yr'):
        rows.append(dict(universe=uni,yr=yr,n_div=len(g),has_fd=int(g.has_fd.sum()),pit_viol=int(g.pit_viol.sum()),eq_public=int(g.eq_public.sum()),
          shared=int(g.shared.sum()),lead_gt120=int(g.lead_gt120.sum()),valid=int(g.valid.sum())))
t=pd.DataFrame(rows); t.to_csv(f"{D}/feasibility_by_year.csv",index=False)
print(t.to_string())
def indep(g):
    v=g[g.valid].copy()
    v['q']=v.exright_date.dt.to_period('Q')
    dd=v.drop_duplicates(['ticker','q'])
    # event day = fd date; if ICT hour>=15 -> reaction next day (approx: +1 calendar day); cluster by ISO week of event day
    ev=dd.fd_date_naive+pd.to_timedelta((dd.fd.dt.hour>=15).astype(int),unit='D')
    wk=ev.dt.to_period('W')
    return pd.Series(dict(valid=len(v),dedup_tk_q=len(dd),tickers=dd.ticker.nunique(),weeks=wk.nunique(),
        max_share_week=round(wk.value_counts().iloc[0]/len(dd),3) if len(dd) else np.nan,
        med_events_per_week=wk.value_counts().median() if len(dd) else np.nan))
s=[]
for uni,x in [('all_tickers',div),('ticker_prune',div[div.in_prune])]:
    for seg,g in x.groupby('seg'):
        r=indep(g); r['universe']=uni; r['seg']=seg; r['n_div']=len(g); r['has_fd']=int(g.has_fd.sum()); s.append(r)
s=pd.DataFrame(s); s.to_csv(f"{D}/feasibility_is_oos.csv",index=False); print(s.to_string())
# alt: without dropping eq_public (strict PIT only)
div['valid_loose']=div.has_fd&~div.pit_viol&~div.shared
print("loose (keep fd==public):", div[div.in_prune].groupby('seg').valid_loose.sum().to_dict(), div.groupby('seg').valid_loose.sum().to_dict())
print("TZ-ambiguous among valid prune:", int((div.valid&div.in_prune&div.tz_date_differs).sum()))
div.to_csv(f"{D}/div_events_flagged.csv",index=False,columns=['id','ticker','exright_date','record_date','public_date','fd','sid','value_per_share','event_status','in_prune','has_fd','pit_viol','eq_public','shared','lead_gt120','valid','lead_ex_naive','tz_date_differs'])
