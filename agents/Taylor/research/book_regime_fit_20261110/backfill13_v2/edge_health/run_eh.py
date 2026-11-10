import os, sys, pandas as pd, numpy as np, pickle
W='/home/trido/thanhdt/WorkingClaude'; R=W+'/mike/agents/Taylor/research/book_regime_fit_20261110'
sys.path.insert(0,'/tmp/audit_lag/scripts'); sys.path.insert(0,W)
src=open('/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/book_regime_fit_20261110/backfill13_v2/edge_health/audit_lag_run_py_copy.py').read().split('# control 1')[0].replace("os.chdir('/tmp/audit_lag')","os.chdir('/tmp/eh_bf13v2')").replace("/tmp/audit_lag/wd_","/tmp/eh_bf13v2/wd_")
src=src.replace("px0=pd.read_pickle('/tmp/audit_lag/px_orig.pkl'); cache=pd.read_pickle('/tmp/audit_lag/cache_all.pkl')","")
exec(src)
out=[]
for tag,p in [('ctrl_canonical',W+'/data/earnings_px.pkl'),('bf13_old_SUPERSEDED',R+'/backfill13/earnings_px_bf13.SUPERSEDED.pkl'),('bf13v2',R+'/backfill13_v2/earnings_px_bf13v2.pkl')]:
    px=pd.read_pickle(p); px['time']=pd.to_datetime(px.time)
    res=run(tag,px)
    out.append({'tag':tag,**{k:res.get(k) for k in ('asof','mean12','win12','n12','verdict','neg_streak')},'w_LAG_good_state':0.65 if (res.get('mean12') or -99)>=4.0 else 0.50})
pd.DataFrame(out).to_csv('/tmp/eh_bf13v2/edge_table.csv',index=False); print(pd.DataFrame(out).to_string(index=False))
