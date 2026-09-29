import pandas as pd, numpy as np
D="/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/first_disclosure_feasibility_20260917"
d=pd.read_csv(f"{D}/q10_master_extract.csv",low_memory=False,dtype={'sid':str})
for c in ['public_date','exright_date','record_date','payout_date','effective_date','news_pd']: d[c]=pd.to_datetime(d[c])
for c in ['fd','ingested_at']: d[c]=pd.to_datetime(d[c])
d['news_pdt']=pd.to_datetime(d.news_pdt,errors='coerce')
# TZ: two readings
d['fd_date_naive']=d.fd.dt.normalize()                       # stored value IS ICT wall clock
d['fd_date_ict']=(d.fd+pd.Timedelta(hours=7)).dt.normalize()  # stored value is true UTC
d['tz_date_differs']=d.fd_date_naive!=d.fd_date_ict
f=d[d.fd.notna()].copy()
out=[]
def P(*a):
    s=" ".join(str(x) for x in a); print(s); out.append(s)
P("## TZ: rows where naive vs UTC->ICT date differ:", int(f.tz_date_differs.sum()), "of", len(f))
for lab,col in [('naive',"fd_date_naive"),('utc2ict','fd_date_ict')]:
    f['lead_ex_'+lab]=(f.exright_date-f[col]).dt.days
    f['lead_rec_'+lab]=(f.record_date-f[col]).dt.days
f['fd_yr']=f.fd.dt.year
# 2. lead time distribution
q=lambda s: pd.Series({'n':s.notna().sum(),'p5':s.quantile(.05),'p25':s.quantile(.25),'med':s.median(),'p75':s.quantile(.75),'p95':s.quantile(.95),'mean':round(s.mean(),1)})
P("\n## Lead exright - fd (naive ICT date), by event_code")
P(f.groupby('event_code')['lead_ex_naive'].apply(q).unstack().to_string())
P("\n## Lead record - fd (naive), by event_code")
P(f.groupby('event_code')['lead_rec_naive'].apply(q).unstack().to_string())
div=f[f.event_code=='DIV']
P("\n## DIV lead exright - fd (naive) by exright year")
P(div.groupby(div.exright_date.dt.year)['lead_ex_naive'].apply(q).unstack().to_string())
# 3. PIT violations
def viol(x,lab):
    le=x['lead_ex_'+lab]; lr=x['lead_rec_'+lab]
    return pd.Series({'n_fd':len(x),'fd>ex':(le<0).sum(),'fd=ex':(le==0).sum(),'fd>rec':(lr<0).sum(),'fd=rec':(lr==0).sum(),
       'fdDate>public':(x['fd_date_'+('naive' if lab=='naive' else 'ict')]>x.public_date).sum(),
       'fd>ingested':(x.fd>x.ingested_at).sum(),'ex_null':x.exright_date.isna().sum()})
P("\n## PIT violations (naive)"); P(f.groupby('event_code').apply(viol,'naive').to_string())
P("\n## PIT violations (utc->ict)"); P(f.groupby('event_code').apply(viol,'utc2ict').to_string())
cols=['ticker','id','event_code','event_status','public_date','exright_date','record_date','fd','sid','ingested_at','title_vi','news_title']
v=f[(f.lead_ex_naive<=0)|(f.lead_rec_naive<0)|(f.fd_date_naive>f.public_date)].sort_values(['event_code','lead_ex_naive'])
v[cols+['lead_ex_naive','lead_rec_naive']].to_csv(f"{D}/pit_violations_all.csv",index=False)
P("\n## violators written:",len(v))
P(v[v.event_code=='DIV'][['ticker','id','public_date','exright_date','record_date','fd','lead_ex_naive','title_vi']].head(25).to_string())
# fd > public by how much
f['fd_minus_public']=(f.fd_date_naive-f.public_date).dt.days
P("\n## fd_date - public_date (naive) distribution by code"); P(f.groupby('event_code')['fd_minus_public'].apply(q).unstack().to_string())
P("fd_date==public_date share:"); P(f.groupby('event_code').apply(lambda x: pd.Series({'n':len(x),'eq':(x.fd_minus_public==0).sum(),'share':round((x.fd_minus_public==0).mean(),3),'fd<public':(x.fd_minus_public<0).sum(),'fd>public':(x.fd_minus_public>0).sum()})).to_string())
# DIV fd==public by status
P(div.assign(eq=(div.fd_date_naive==div.public_date)).groupby('event_status').eq.agg(['size','sum','mean']).to_string())
# 4b shared sid / timestamp among distinct events of same ticker
g=d[d.sid.notna()].groupby(['ticker','sid']).agg(n=('id','size'),codes=('event_code',lambda s:'/'.join(sorted(set(s)))),
   exs=('exright_date',lambda s: s.dropna().nunique())).reset_index()
P("\n## sid shared by >1 rows same ticker:",(g.n>1).sum(),"groups; rows:",g[g.n>1].n.sum(), "; groups with >=2 distinct exright:",(g.exs>=2).sum())
P(g[g.n>1].codes.value_counts().head(10).to_string())
gs=d[d.sid.notna()].groupby('sid').ticker.nunique(); P("sid used by >1 ticker:",(gs>1).sum())
gd=d[(d.event_code=='DIV')&d.sid.notna()].groupby(['ticker','sid']).agg(n=('id','size'),exs=('exright_date',lambda s:s.dropna().nunique()),
   vps=('value_per_share',lambda s:','.join(map(str,s))),exl=('exright_date',lambda s:','.join(s.dropna().dt.strftime('%Y-%m-%d')))).reset_index()
bad=gd[gd.exs>=2]; bad.to_csv(f"{D}/div_shared_sid_distinct_exdates.csv",index=False)
P("DIV (ticker,sid) groups spanning >=2 distinct exright dates:",len(bad)," rows:",bad.n.sum()); P(bad.head(12).to_string())
gt=f[f.event_code=='DIV'].groupby(['ticker','fd']).agg(n=('id','size'),exs=('exright_date',lambda s:s.dropna().nunique()),exl=('exright_date',lambda s:','.join(s.dropna().dt.strftime('%Y-%m-%d'))),sids=('sid',lambda s:','.join(s.dropna().unique()))).reset_index()
bt=gt[gt.exs>=2]; bt.to_csv(f"{D}/div_shared_fd_distinct_exdates.csv",index=False)
P("DIV (ticker,fd) groups spanning >=2 distinct exright:",len(bt),"rows:",bt.n.sum()); P(bt.head(12).to_string())
# 4c fd vs news
j=f[f.news_pdt.notna()].copy()
j['news_minus_fd_h']=(j.news_pdt-j.fd).dt.total_seconds()/3600
j['rel']=np.select([j.news_minus_fd_h==0, j.news_minus_fd_h==7, j.news_minus_fd_h==-7, j.news_minus_fd_h>0, j.news_minus_fd_h<0],['eq','news=fd+7h','news=fd-7h','news_after_fd','news_before_fd'],'?')
P("\n## fd vs linked news public_datetime"); P(j.groupby(['event_code','rel']).size().unstack(fill_value=0).to_string())
P("news_after_fd days quantiles (DIV):", (j[(j.event_code=='DIV')&(j.rel=='news_after_fd')].news_minus_fd_h/24).quantile([.05,.25,.5,.75,.95]).round(1).to_dict())
P("news_before_fd days quantiles (DIV):", (j[(j.event_code=='DIV')&(j.rel=='news_before_fd')].news_minus_fd_h/24).quantile([.05,.25,.5,.75,.95]).round(1).to_dict())
j.to_csv(f"{D}/fd_vs_news_join.csv",index=False,columns=cols+['news_pdt','news_mec','news_act','news_minus_fd_h','rel'])
# fd with no sid: where from?
P("\n## DIV fd without sid: count",((f.event_code=='DIV')&f.sid.isna()).sum(),"; fd_date==public share", round((f[(f.event_code=='DIV')&f.sid.isna()].fd_minus_public==0).mean(),3), "vs with sid", round((f[(f.event_code=='DIV')&f.sid.notna()].fd_minus_public==0).mean(),3))
# 4d abnormal lead
ab=f[(f.lead_ex_naive>180)|(f.lead_ex_naive<0)]
P("\n## abnormal lead (>180 or <0) by code:"); P(ab.groupby('event_code').apply(lambda x: pd.Series({'gt180':(x.lead_ex_naive>180).sum(),'neg':(x.lead_ex_naive<0).sum()})).to_string())
ab[cols+['lead_ex_naive']].to_csv(f"{D}/abnormal_lead.csv",index=False)
P(ab[ab.event_code=='DIV'].sort_values('lead_ex_naive',ascending=False)[['ticker','id','exright_date','public_date','fd','lead_ex_naive','title_vi']].head(10).to_string())
# 4e snapshot first seen
s=pd.read_csv(f"{D}/q11_snapshot_first_seen.csv",parse_dates=['first_seen','first_public_date'])
m=f.merge(s,on='id',how='left'); gmin=s.first_seen.min()
m2=m[(m.first_seen>gmin)]
m2=m2.assign(seen_minus_fd=(m2.first_seen-m2.fd_date_naive).dt.days)
P("\n## snapshot first_seen (>",gmin.date(),", not left-censored) vs fd date: n=",len(m2))
P(m2.groupby('event_code').seen_minus_fd.apply(q).unstack().to_string())
P("first_seen < fd_date (vendor saw event before its 'first disclosure' = impossible):",(m2.seen_minus_fd<0).sum())
P(m2[m2.seen_minus_fd<0][['ticker','id','event_code','first_seen','first_status','first_public_date','fd','public_date','exright_date']].to_string())
P("first_public_date (at first vintage) vs fd date, DIV: eq",((m2.event_code=='DIV')&(m2.first_public_date==m2.fd_date_naive)).sum(),"of",(m2.event_code=='DIV').sum())
m2[cols+['first_seen','first_status','first_public_date','seen_minus_fd']].to_csv(f"{D}/snapshot_firstseen_vs_fd.csv",index=False)
f.to_pickle(f"{D}/_f.pkl")
open(f"{D}/analyze_output.txt","w").write("\n".join(out))
