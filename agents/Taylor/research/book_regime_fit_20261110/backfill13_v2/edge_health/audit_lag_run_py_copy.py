import os, sys, pandas as pd, numpy as np, pickle, shutil
W='/home/trido/thanhdt/WorkingClaude'
sys.path.insert(0,W); os.chdir('/tmp/audit_lag')
import edge_health_monitor as m
px0=pd.read_pickle('/tmp/audit_lag/px_orig.pkl'); cache=pd.read_pickle('/tmp/audit_lag/cache_all.pkl')
ev_raw=pd.read_pickle(f'{W}/data/earnings_events.pkl')   # input to step [4], read-only
ev_raw['Release_Date']=pd.to_datetime(ev_raw['Release_Date'])

def classify(npr, pre, rel, post):
    if pd.isna(npr): return "NO_NPR"
    good, bad = npr >= 15, npr <= -15
    if good:
        if pre >= 10 and rel <= -2: return "LEAK_RUNUP_POS"
        if abs(pre) < 5 and rel >= 3: return "EFFICIENT_POS"
        if abs(pre) < 5 and abs(rel) < 3 and post >= 5: return "LAGGED_POS"
        if pre >= 10 and rel >= 0 and post < 0: return "LEAK_RUNUP_POS"
    if bad:
        if pre <= -10 and rel >= 2: return "LEAK_DUMP_NEG"
        if abs(pre) < 5 and rel <= -3: return "EFFICIENT_NEG"
        if abs(pre) < 5 and abs(rel) < 3 and post <= -5: return "LAGGED_NEG"
    return "NOISE"

def events_cls(px):
    ev=ev_raw
    piv=px.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
    dates=np.array(piv.index); cols=set(piv.columns)
    def off(tk, ref, o):
        if tk not in cols: return np.nan
        pos=np.searchsorted(dates, np.datetime64(ref), side="right")-1
        if pos<0: return np.nan
        t=pos+o
        if t<0 or t>=len(dates): return np.nan
        return piv.iloc[t][tk]
    rows=[]
    for _,r in ev.iterrows():
        tk,rdt=r["ticker"],r["Release_Date"]
        if tk not in cols: continue
        a=off(tk,rdt,-30); b=off(tk,rdt,-1); c=off(tk,rdt,5); d=off(tk,rdt,30)
        if any(pd.isna(x) for x in [a,b,c,d]): continue
        if min(a,b,c,d)<=0: continue
        pre=(b/a-1)*100; rel=(c/b-1)*100; post=(d/c-1)*100
        npr=r["NP_R"]*100 if pd.notna(r["NP_R"]) else np.nan
        rows.append({"ticker":tk,"quarter":r["quarter"],"Release_Date":rdt,"NP_R":npr,
          "Rev_YoY": r["Revenue_YoY_P0"]*100 if pd.notna(r["Revenue_YoY_P0"]) else np.nan,
          "pre_ret":pre,"rel_ret":rel,"post_ret":post,"pattern":classify(npr,pre,rel,post)})
    return pd.DataFrame(rows)

def run(tag, px, ev_csv=None):
    wd=f'/tmp/audit_lag/wd_{tag}'; os.makedirs(wd+'/data',exist_ok=True)
    px.to_pickle(wd+'/data/earnings_px.pkl')
    if ev_csv is None:
        evdf=events_cls(px); evdf.to_csv(wd+'/data/earnings_events_classified.csv',index=False)
    else:
        shutil.copy(ev_csv, wd+'/data/earnings_events_classified.csv')
    m.WORKDIR=wd; os.environ['LAG_EDGE_OUT']=wd+'/lag_edge_health.csv'
    res=m.lag_edge_health()
    print(tag,res)
    return res

# control 1: orig px + CURRENT events csv (should reproduce data/lag_edge_health.csv)
r0=run('ctrl_current_events', px0, W+'/data/earnings_events_classified.csv')
# control 2: orig px + events recomputed with my replica of step [4]
r1=run('ctrl_replica_events', px0)
# A: fill missing (ticker,time) rows from cache for 2026 days only
miss=cache[cache.time>='2026-01-01'].merge(px0[['ticker','time']],on=['ticker','time'],how='left',indicator=True)
miss=miss[miss._merge=='left_only'][['ticker','time','Close']]
pxA=pd.concat([px0,miss],ignore_index=True).sort_values(['ticker','time']).reset_index(drop=True)
print('A: added rows',len(miss))
rA=run('A_fill_missing_2026', pxA)
# C: full rebuild from cache for >=2013, pkl for 2011-12
pxC=pd.concat([px0[px0.time<'2013-01-01'],cache[cache.time>='2013-01-01']],ignore_index=True).sort_values(['ticker','time']).reset_index(drop=True)
rC=run('C_full_cache_frame', pxC)
# B: drop the 13 thin days entirely from orig (what a 'skip-thin' would give)
cnt=px0.groupby('time').ticker.nunique(); thin=cnt[cnt<100].index
pxB=px0[~px0.time.isin(thin)]
rB=run('B_drop_thin_days', pxB)
