import warnings; warnings.filterwarnings('ignore')
import pandas as pd, numpy as np
EXP='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_value_radar/'
OLD='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_market_prob/'
pd.set_option('display.width',260)
d=pd.read_csv(EXP+'radar.csv',parse_dates=['time'])
F=pd.read_csv(OLD+'panel_fwd.csv',parse_dates=['time'])

print('='*90); print('A — DOI CHIEU PE tu dung vs PE CHINH THUC (VNINDEX_PE mirror)'); print('='*90)
m=d[['time','pe_agg_pos','pe_cap10']].merge(F[['time','mkt_pe','pe_t100','pe_con']],on='time',how='inner').dropna(subset=['mkt_pe'])
print('N=%d (%s -> %s)'%(len(m),m.time.min().date(),m.time.max().date()))
print('corr(pe_agg_pos, mkt_pe chinh thuc) = %.4f | corr(pe_t100 bao cao goc, mkt_pe) = %.4f'%(
    m.pe_agg_pos.corr(m.mkt_pe),m.pe_t100.corr(m.mkt_pe)))
print('gia tri gan nhat: pe_agg_pos=%.2f | pe_t100(goc)=%.2f | mkt_pe chinh thuc=%.2f'%(
    m.pe_agg_pos.iloc[-1],m.pe_t100.iloc[-1],m.mkt_pe.iloc[-1]))
mm=F.dropna(subset=['mkt_pe']); v=mm.mkt_pe.iloc[-1]
for wn,msk in [('2008+',mm.time>='2008-01-01'),('10Y',mm.time>=mm.time.max()-pd.DateOffset(years=10)),
               ('3Y',mm.time>=mm.time.max()-pd.DateOffset(years=3))]:
    print('  phan vi PE CHINH THUC (%s): %.1f'%(wn,100*(mm[msk].mkt_pe<v).mean()))

print('\n'+'='*90); print('B — RADAR 20 phien gan nhat + do nhay nguong'); print('='*90)
t=d.dropna(subset=['radar3']).tail(20)[['time','pe_cap10','pb_cap10','sp_pe_cap10','p_pe','p_pb','p_sp','radar3','lab_radar3','radar3_roll','lab_radar3_roll']]
t.columns=['time','PE10','PB10','spread','p_pe','p_pb','p_sp','radar3','nhan','roll10Y','nhan_roll']
print(t.round(2).to_string(index=False))
cur=d.dropna(subset=['radar3']).iloc[-1]
print('\nDO NHAY cua NHAN hom nay (radar3=%.1f):'%cur.radar3)
for nm,val in [('radar3 (TB 3 tp, PIT expanding)',cur.radar3),('radar3 trung vi',cur.radar3_med),
               ('radar2 (chi PE+PB)',cur.radar2),('radar3 rolling-10Y',cur.radar3_roll)]:
    lab='CHEAP' if val<33 else ('EXPENSIVE' if val>67 else 'FAIR')
    print('  %-34s = %5.1f -> %s'%(nm,val,lab))
print('  nguong tercile that (33/67 co dinh) vs tercile THUC NGHIEM cua chinh chuoi radar3:')
s=d.radar3.dropna(); print('    p33=%.1f, p67=%.1f -> voi nguong thuc nghiem hom nay la %s'%(
    s.quantile(.33),s.quantile(.67),'CHEAP' if cur.radar3<s.quantile(.33) else ('EXPENSIVE' if cur.radar3>s.quantile(.67) else 'FAIR')))

print('\n'+'='*90); print('C — DAY FAIR-thap (radar 33-45): ket cuc lich su ra sao?'); print('='*90)
g=d.dropna(subset=['radar3','fwd_12M','minfwd_12M'])
for lo,hi in [(0,20),(20,33),(33,45),(45,55),(55,67),(67,100)]:
    s=g[(g.radar3>=lo)&(g.radar3<hi)]
    if len(s)<30: continue
    idx=np.array(s.index); ne=1+int((np.diff(idx)>21).sum())
    print('  radar %3d-%3d: N=%4d (%2d episode) fwd12M trung vi %+6.1f%% | P_bear %4.1f%% | P(fwd<0) %4.1f%%'%(
        lo,hi,len(s),ne,100*s.fwd_12M.median(),100*(s.minfwd_12M<=-0.20).mean(),100*(s.fwd_12M<0).mean()))

print('\n'+'='*90); print('D — Bối cảnh: drawdown hien tai + so voi cac moc'); print('='*90)
v2=d.dropna(subset=['vni_close']).copy()
v2['peak52']=v2.vni_close.rolling(250,min_periods=60).max(); v2['dd']=100*(v2.vni_close/v2.peak52-1)
print('phien cuoi co gia (%s): VNINDEX=%.1f, dd tu dinh 52w = %.1f%%'%(v2.time.iloc[-1].date(),v2.vni_close.iloc[-1],v2.dd.iloc[-1]))
print('so sanh: 2018-12-28 dd=%.1f%% | 2022-06-16 dd=%.1f%% | 2022-11-15 dd=%.1f%%'%(
    v2[v2.time<='2018-12-28'].dd.iloc[-1],v2[v2.time<='2022-06-16'].dd.iloc[-1],v2[v2.time<='2022-11-15'].dd.iloc[-1]))
