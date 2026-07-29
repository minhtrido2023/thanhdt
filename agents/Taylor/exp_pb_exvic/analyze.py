import pandas as pd, numpy as np
EXP='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_pb_exvic/'
OLD='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_market_prob/'
pd.set_option('display.width',250)

p=pd.read_csv(EXP+'t100_panel.csv'); p['time']=pd.to_datetime(p.time)
a=pd.read_csv(EXP+'agg_all.csv'); a['time']=pd.to_datetime(a.time)
old=pd.read_csv(OLD+'agg_pepb.csv',parse_dates=['time'])
old['pb_t100_old']=old.mcap_pb_t100/old.book_t100
old['pb_all_old']=old.mcap_pb_all/old.book_all

# ---------- VALIDATION: tai lap so cu ----------
g=p.groupby('time')
rec=pd.DataFrame({'mcap':g.mcap.sum(),'book':g.book.sum(),'n':g.size()}).reset_index()
rec['pb_t100_new']=rec.mcap/rec.book
a['pb_all_new']=a.mcap_all/a.book_all
v=rec.merge(old[['time','pb_t100_old','pb_all_old']],on='time').merge(a[['time','pb_all_new']],on='time')
print('=== VALIDATION tai lap (top-100 cap-weighted) ===')
print('N=%d  corr=%.6f  median|diff|=%.2e  max|diff|=%.2e'%(len(v),v.pb_t100_new.corr(v.pb_t100_old),
      (v.pb_t100_new-v.pb_t100_old).abs().median(),(v.pb_t100_new-v.pb_t100_old).abs().max()))
print('all-universe: corr=%.6f  max|diff|=%.2e'%(v.pb_all_new.corr(v.pb_all_old),(v.pb_all_new-v.pb_all_old).abs().max()))
print(v.tail(2)[['time','pb_t100_new','pb_t100_old','pb_all_new','pb_all_old']].to_string(index=False))
