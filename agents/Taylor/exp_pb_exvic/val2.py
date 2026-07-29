import pandas as pd,numpy as np
EXP='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_pb_exvic/'
OLD='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_market_prob/'
p=pd.read_csv(EXP+'t100_panel2.csv',parse_dates=['time'])
a=pd.read_csv(EXP+'agg_all2.csv',parse_dates=['time'])
old=pd.read_csv(OLD+'agg_pepb.csv',parse_dates=['time'])
old['pb_t100_old']=old.mcap_pb_t100/old.book_t100
old['pb_all_old']=old.mcap_pb_all/old.book_all
g=p.groupby('time'); rec=pd.DataFrame({'mcap':g.mcap.sum(),'book':g.book.sum(),'n':g.size()}).reset_index()
rec['pb_t100_new']=rec.mcap/rec.book
a['pb_all_new']=a.mcap_all/a.book_all
v=rec.merge(old[['time','pb_t100_old','pb_all_old','n_pb_all']],on='time').merge(a[['time','pb_all_new','n_pb']],on='time')
d=(v.pb_t100_new-v.pb_t100_old).abs(); d2=(v.pb_all_new-v.pb_all_old).abs()
print('t100: corr=%.8f med|d|=%.2e max|d|=%.2e'%(v.pb_t100_new.corr(v.pb_t100_old),d.median(),d.max()))
print('all : corr=%.8f med|d|=%.2e max|d|=%.2e  n_match=%.3f'%(v.pb_all_new.corr(v.pb_all_old),d2.median(),d2.max(),(v.n_pb==v.n_pb_all).mean()))
print(v.loc[d.nlargest(3).index,['time','pb_t100_new','pb_t100_old']].to_string(index=False))
print(v.tail(2)[['time','pb_t100_new','pb_t100_old','pb_all_new','pb_all_old']].to_string(index=False))
