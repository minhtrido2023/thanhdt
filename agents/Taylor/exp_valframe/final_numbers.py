# -*- coding: utf-8 -*-
import numpy as np, pandas as pd
from scipy import stats
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
EXP='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_valframe/'
pd.set_option('display.width',250)
M=pd.read_csv(EXP+'metrics_full.csv',parse_dates=['time']).sort_values('time').reset_index(drop=True)
M['t']=(M.time-M.time.min()).dt.days/365.25
def dt_(d,c):
    sl,ic,*_=stats.linregress(d.t,d[c]); return d[c].values-(ic+sl*d.t.values)

comp=['pe_cap10','pb_cap10','cape7','erp']
d=M[['time','t']+comp].dropna().reset_index(drop=True)
Z=pd.DataFrame(index=d.index)
for c in comp:
    x=dt_(d,c); z=(x-x.mean())/x.std(); Z[c]=-z if c=='erp' else z
d['comp']=Z.mean(axis=1)
cur=d.iloc[-1]
print(f"COMPOSITE (khu xu huong) den {cur.time.date()}: z={cur.comp:+.2f} phan vi={100*(d.comp<cur.comp).mean():.1f} N={len(d)}")
for c in comp:
    print(f"   thanh phan {c:10s} z={Z[c].iloc[-1]:+.2f}")

print('\n=== BANG TOM TAT VIEC 1 (gia tri hien tai + phan vi THO va KHU XU HUONG) ===')
rows=[]
for c in ['pe_cap10','pe_cw','pb_cap10','pb_cw','pb_ewmed','eveb_cap10','eveb_cw','eveb_ewmed',
          'cape5','cape7','cape10','ey','erp']:
    dd=M[['time','t',c]].dropna().copy()
    xd=dt_(dd,c); slope=stats.linregress(dd.t,dd[c]).slope
    rows.append(dict(chi_so=c, hien_tai=round(dd[c].iloc[-1],3), bat_dau=str(dd.time.min().date()),
                     nam=round((dd.time.max()-dd.time.min()).days/365.25,1),
                     doc_moi_nam=round(slope,3),
                     pctile_tho=round(100*(dd[c]<dd[c].iloc[-1]).mean(),1),
                     pctile_khu_xu_huong=round(100*(xd<xd[-1]).mean(),1)))
T=pd.DataFrame(rows); print(T.to_string(index=False)); T.to_csv(EXP+'viec1_summary.csv',index=False)

# ---- chart ----
fig,ax=plt.subplots(3,1,figsize=(13,11),sharex=True)
ax[0].plot(M.time,M.pe_cap10,lw=1,label='P/E capped-10% (ben voi outlier)')
ax[0].plot(M.time,M.cape5,lw=1,label='CAPE-5Y (E thuc binh quan 5 nam)')
ax[0].plot(M.time,M.cape7,lw=1,label='CAPE-7Y')
ax[0].plot(M.time,M.cape10,lw=1,label='CAPE-10Y')
ax[0].set_ylabel('lan'); ax[0].legend(fontsize=8,ncol=2); ax[0].grid(alpha=.25)
ax[0].set_title('Bo chi so dinh gia cap-index VN (ro top-100 von hoa) — den %s'%M.time.max().date())
ax[1].plot(M.time,M.pb_cap10,lw=1,label='P/B capped-10%')
ax[1].plot(M.time,M.eveb_cap10,lw=1,label='EV/EBITDA capped-10%')
ax[1].set_ylabel('lan'); ax[1].legend(fontsize=8); ax[1].grid(alpha=.25)
ax[2].plot(M.time,M.ey,lw=1,label='Earnings yield (1/PE capped-10%), %')
ax[2].plot(M.time,M.dep,lw=1,label='Lai suat huy dong Big4-12M, %')
ax[2].plot(M.time,M.erp,lw=1.4,color='k',label='ERP = ey - lai suat huy dong, pp')
ax[2].axhline(0,ls='--',c='grey',lw=.8); ax[2].set_ylabel('%'); ax[2].legend(fontsize=8); ax[2].grid(alpha=.25)
plt.tight_layout(); plt.savefig('/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/valuation_framework_20260729.png',dpi=110)

# ---- chart 2: CAPIT events scatter ----
E=pd.read_csv(EXP+'capit_events_gate0.3.csv',parse_dates=['event'])
fig,ax=plt.subplots(1,2,figsize=(13,5.5))
for i,o in enumerate(['r6M','r12M']):
    dd=E[['event','pb_cap10_pctE',o]].dropna()
    prod=dd.event>='2014-01-01'
    ax[i].scatter(dd.pb_cap10_pctE[~prod],dd[o][~prod],c='grey',s=60,label='2009-2013')
    ax[i].scatter(dd.pb_cap10_pctE[prod],dd[o][prod],c='C3',s=60,label='2014+ (cua so production)')
    for _,r in dd.iterrows(): ax[i].annotate(str(r.event.date())[:7],(r.pb_cap10_pctE,r[o]),fontsize=6.5,alpha=.8)
    sl,ic,*_=stats.linregress(dd.pb_cap10_pctE,dd[o])
    xs=np.linspace(0,90,10); ax[i].plot(xs,ic+sl*xs,'k--',lw=1)
    rho=stats.spearmanr(dd.pb_cap10_pctE,dd[o])[0]
    ax[i].axhline(0,c='grey',lw=.8); ax[i].grid(alpha=.25); ax[i].legend(fontsize=8)
    ax[i].set_xlabel('phan vi P/B (capped-10%) luc CAPIT fire — NHAN QUA')
    ax[i].set_ylabel(f'VNINDEX {o} sau su kien (%)')
    ax[i].set_title(f'{o}: Spearman rho={rho:+.3f} (N={len(dd)})')
plt.suptitle('Dinh gia luc CAPIT fire vs ket qua forward — 26 su kien 2009-2026',y=1.0)
plt.tight_layout(); plt.savefig('/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/capit_valuation_20260729.png',dpi=110)
print('\ncharts saved')
