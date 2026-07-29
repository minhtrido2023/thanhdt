import pandas as pd,numpy as np
EXP='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_pb_exvic/'
pd.set_option('display.width',260)
p=pd.read_csv(EXP+'t100_panel2.csv',parse_dates=['time'])
p['pb_i']=p.mcap/p.book; p=p[np.isfinite(p.pb_i)&(p.pb_i>0)].copy()
p['w']=p.mcap/p.groupby('time').mcap.transform('sum'); p['yr']=p.time.dt.year
S=pd.read_csv(EXP+'pb_variants.csv',parse_dates=['time']); S['yr']=S.time.dt.year

print('=== 1. Ma co ty trong LON NHAT trong top-100, theo nam ===')
g=S.groupby('yr').agg(top1_w_mean=('top1_w','mean'),top1_w_max=('top1_w','max'),
                      pb_cw=('pb_cw','mean'),pb_exvic=('pb_cw_exvic','mean'),ewmed=('pb_ewmed','mean'))
mode=S.groupby('yr').top1_tk.agg(lambda x:x.value_counts().index[0])
cnt=S.groupby('yr').top1_tk.agg(lambda x:x.value_counts().iloc[0]/len(x))
g['top1_tk']=mode; g['top1_share_days']=cnt
g['vic_w']=S.groupby('yr').vic_w.mean(); g['vic_pb']=S.groupby('yr').vic_pb.mean()
print((g*[100,100,1,1,1,1,1,100,1]).round(2).to_string())

print('\n=== 2. Ngay-ma co ty trong >12%% trong top-100 (bat ky ma nao, 2008+) ===')
big=p[p.w>0.12]
if len(big):
    b=big.groupby(['ticker']).agg(n_days=('w','size'),first=('time','min'),last=('time','max'),
        w_med=('w','median'),w_max=('w','max'),pb_med=('pb_i','median'),pb_max=('pb_i','max'))
    print(b.assign(w_med=lambda x:(100*x.w_med).round(2),w_max=lambda x:(100*x.w_max).round(2),
                   pb_med=lambda x:x.pb_med.round(2),pb_max=lambda x:x.pb_max.round(2)).sort_values('n_days',ascending=False).to_string())
print('\n=== 3. Ngay-ma ty trong >15%% VA PB>5 (dieu kien "meo mo" nhu VIC hien nay) ===')
d=p[(p.w>0.15)&(p.pb_i>5)]
print('N ngay-ma = %d ; ma: %s'%(len(d), d.ticker.value_counts().to_dict()))
if len(d): print(d.groupby('ticker').agg(first=('time','min'),last=('time','max'),w_max=('w','max'),pb_med=('pb_i','median')).to_string())

print('\n=== 4. Top-5 ty trong hien tai + PB ===')
last=p[p.time==p.time.max()].nlargest(8,'w')[['ticker','w','pb_i','mcap']]
last['w']=(100*last.w).round(2); print(last.to_string(index=False))
print('\n  Ho Vingroup (VIC+VHM+VRE) ty trong top-100 = %.2f%%'%(100*p[(p.time==p.time.max())&p.ticker.isin(['VIC','VHM','VRE'])].w.sum()))

print('\n=== 5. Phan phoi top1_w lich su (top-100) ===')
q=S.top1_w.quantile([.5,.9,.99,1.0])*100
print('  median %.2f%% p90 %.2f%% p99 %.2f%% max %.2f%%  | hien tai %.2f%% (phan vi %.2f)'%(
  q.iloc[0],q.iloc[1],q.iloc[2],q.iloc[3],100*S.top1_w.iloc[-1],100*(S.top1_w<S.top1_w.iloc[-1]).mean()))
print('  So phien top1_w>15%%: %d / %d (%.2f%%), lan dau %s'%((S.top1_w>0.15).sum(),len(S),
  100*(S.top1_w>0.15).mean(), S[S.top1_w>0.15].time.min().date() if (S.top1_w>0.15).any() else '-'))

print('\n=== 6. Do nhay: contribution cua VIC vao PB cap-weighted theo thoi gian (cuoi nam) ===')
ye=S.groupby('yr').tail(1)[['time','pb_cw','pb_cw_exvic','pb_cap10','pb_ewmed','vic_w','vic_pb','top1_tk','top1_w']]
ye['delta_vic']=ye.pb_cw-ye.pb_cw_exvic
print(ye.assign(vic_w=lambda x:(100*x.vic_w).round(2),top1_w=lambda x:(100*x.top1_w).round(2)).round(3).to_string(index=False))
