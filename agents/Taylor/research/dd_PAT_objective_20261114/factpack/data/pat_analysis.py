"""Phân tích PAT: chuỗi quý, kỳ định danh được (H1/Q3/Q4), biên độ, quan hệ biên gộp ~ giá hàng hoá. Chạy: wc_venv/bin/python pat_analysis.py"""
import sys, json; sys.path.insert(0,'.')
import numpy as np, pandas as pd
from scipy import stats
from pat_build_quarterly import *
T=df.set_index('quarter')
# ---------- neo từ BCTC gốc (ảnh), tỷ đồng ----------
GP_A={'Q3_2025':130.471,'Q3_2026':63.604,'H1_2025':216.612,'H1_2026':186.994}
SGA={'Q3_2025':20.554+4.132,'Q3_2026':5.049+4.711,'H1_2025':42.638+8.719,'H1_2026':27.239+8.038}
EBIT_A={k:GP_A[k]-SGA[k] for k in GP_A}
q=lambda y,n:f"{y}Q{n}"
def chain(Ts,A,y0):
    """kỳ định danh: H1,Q3,Q4 từng năm; chỉ dùng TTM sạch (>=2022Q3)"""
    out={}
    d=lambda y,n: Ts[q(y,n)]-Ts[q(y,n-1)]
    Q3={2025:A['Q3_2025'],2026:A['Q3_2026']}
    for y in range(2024,2021,-1): Q3[y]=Q3[y+1]-d(y+1,3)
    H1={2025:A['H1_2025'],2026:A['H1_2026']}
    for y in range(2024,2021,-1): H1[y]=H1[y+1]-(Ts[q(y+1,2)]-Ts[q(y,4)])
    Q4={y:Ts[q(y,4)]-H1[y]-Q3[y] for y in range(2022,2026)}
    Q4[2021]=Q4[2022]-(Ts[q(2022,4)]-Ts[q(2022,3)])
    chk={'Q3_2026_fwd':Q3[2025]+d(2026,3),'H1_2026_fwd':H1[2025]+(Ts[q(2026,2)]-Ts[q(2025,4)])}
    return Q3,H1,Q4,chk
gQ3,gH1,gQ4,gchk=chain(T['gp_ttm'],GP_A,2022)
eQ3,eH1,eQ4,echk=chain(T['ebit_ttm'],EBIT_A,2022)
# kỳ -> (nhãn, quý thành phần)
per=[]
def addp(y,tag,qs_): per.append((f"{tag}/{y}",y,tag,qs_))
addp(2021,'Q4',[q(2021,4)])
for y in range(2022,2027):
    addp(y,'H1',[q(y,1),q(y,2)]); addp(y,'Q3',[q(y,3)])
    if y<2026: addp(y,'Q4',[q(y,4)])
P=pd.DataFrame(index=[p[0] for p in per])
P['year']=[p[1] for p in per]; P['tag']=[p[2] for p in per]
P['rev']=[sum(T.loc[x,'rev'] for x in p[3]) for p in per]
P['np']=[sum(T.loc[x,'np'] for x in p[3]) for p in per]
gmap={'H1':gH1,'Q3':gQ3,'Q4':gQ4}; emap={'H1':eH1,'Q3':eQ3,'Q4':eQ4}
P['gp']=[gmap[p[2]][p[1]] for p in per]; P['ebit']=[emap[p[2]][p[1]] for p in per]
P['gpm']=P.gp/P.rev; P['ebitm']=P.ebit/P.rev; P['sga']=P.gp-P.ebit; P['npm']=P.np/P.rev
# ---------- giá hàng hoá theo kỳ ----------
c=pd.read_csv('pat_commodity_quarterly.csv')
def qmean(key,x): 
    s=c[(c.metric_key==key)&(c.quarter==x)]; return (s.mean_val.iloc[0],int(s.n_obs.iloc[0])) if len(s) else (np.nan,0)
def pmean(key,qs_):
    v=[qmean(key,x) for x in qs_]; n=sum(a[1] for a in v)
    return (sum(a[0]*a[1] for a in v)/n if n else np.nan),n
def prevq(x): i=qi(x)-1; return qs(i)
keys={'p4':'yellow_phosphorus','coke':'coke','coking_coal':'coking_coal','sulfur':'sulfur','rock_cny':'phosphate_rock_cny'}
for k,mk in keys.items():
    P[k]=[pmean(mk,p[3])[0] for p in per]
    P[k+'_n']=[pmean(mk,p[3])[1] for p in per]
    P[k+'_lag']=[qmean(mk,prevq(p[3][0]))[0] for p in per]   # trung bình quý ngay trước kỳ
P.to_csv('pat_identified_periods.csv')
# ---------- bảng quý ----------
QT=T.reset_index()[['quarter','rev','np','ttm_rev','gpm_ttm','ebitm_ttm','gp_ttm','ebit_ttm']].copy()
r2=raw.set_index('quarter')
QT=QT.set_index('quarter',drop=False)
QT['cfo']=r2['CF_OA_P0']/1e9; QT['inventory']=r2['Inventory_P0']/1e9
QT['debt_st']=r2['StDebt_P0']/1e9; QT['debt_lt']=r2['LtDebt_P0']/1e9
QT['equity']=(r2['totalAsset_P0']-r2['StLiab_P0']-r2['LtLiab_P0'])/1e9
QT['total_assets']=r2['totalAsset_P0']/1e9; QT['cash_only']=r2['Cash_P0']/1e9
QT['ebitda_ttm']=r2['EBITDA_P0']/1e9; QT['da_ttm_derived']=QT.ebitda_ttm-QT.ebit_ttm
QT['p4_mean']=[qmean('yellow_phosphorus',x)[0] for x in QT.quarter]
QT['coke_mean']=[qmean('coke',x)[0] for x in QT.quarter]
QT['sulfur_mean']=[qmean('sulfur',x)[0] for x in QT.quarter]
QT['coking_coal_mean']=[qmean('coking_coal',x)[0] for x in QT.quarter]
QT['rock_cny_mean']=[qmean('phosphate_rock_cny',x)[0] for x in QT.quarter]
QT.to_csv('pat_quarterly_series.csv',index=False)
# ---------- thống kê ----------
def corr_stats(x,y):
    m=~(np.isnan(x)|np.isnan(y)); x=x[m]; y=y[m]; n=len(x)
    r,p=stats.pearsonr(x,y); rs,ps=stats.spearmanr(x,y)
    z=np.arctanh(r); se=1/np.sqrt(n-3); lo,hi=np.tanh(z-1.96*se),np.tanh(z+1.96*se)
    lr=stats.linregress(x,y); tcrit=stats.t.ppf(.975,n-2)
    loo_r=[];loo_b=[]
    for i in range(n):
        mm=np.arange(n)!=i; loo_r.append(stats.pearsonr(x[mm],y[mm])[0]); loo_b.append(stats.linregress(x[mm],y[mm]).slope)
    return dict(n=n,pearson=r,p_pearson=p,ci_lo=lo,ci_hi=hi,spearman=rs,p_spearman=ps,slope=lr.slope,slope_lo=lr.slope-tcrit*lr.stderr,slope_hi=lr.slope+tcrit*lr.stderr,r2=lr.rvalue**2,
                loo_r_min=min(loo_r),loo_r_max=max(loo_r),loo_slope_min=min(loo_b),loo_slope_max=max(loo_b))
res=[]
def run(label,xs,ys,note=''):
    d=corr_stats(np.asarray(xs,float),np.asarray(ys,float)); d['test']=label; d['note']=note; res.append(d)
A=P.copy(); B=P[P.index!='Q4/2021']   # B bỏ Q4/2021
for nm,Dd in (('N15 gồm Q4/2021',A),('N14 bỏ Q4/2021',B)):
    for y,yl in (('gpm','GPM'),('ebitm','EBIT margin')):
        for x,xl in (('p4','P4 cùng kỳ'),('p4_lag','P4 quý trước kỳ'),('coke','than cốc sunsirs cùng kỳ'),('coking_coal','coking coal TE cùng kỳ'),('sulfur','lưu huỳnh cùng kỳ'),('rock_cny','quặng P CNY cùng kỳ')):
            if x=='rock_cny': 
                Dx=Dd[Dd.rock_cny.notna()]
            else: Dx=Dd
            run(f"{yl} ~ {xl} [{nm}]",Dx[x],Dx[y])
# log P4
for nm,Dd in (('N15',A),('N14',B)):
    run(f"GPM ~ ln(P4 cùng kỳ) [{nm}]",np.log(Dd.p4),Dd.gpm)
# sai phân (loại xu hướng): thay đổi YoY cùng loại kỳ
Y=P.copy().sort_values(['tag','year']); 
dd=[]
for tag in ['H1','Q3','Q4']:
    s=Y[Y.tag==tag].sort_values('year')
    s=s.assign(d_gpm=s.gpm.diff(),d_p4=s.p4.diff(),d_ebitm=s.ebitm.diff(),d_p4pct=s.p4.pct_change())
    dd.append(s.dropna(subset=['d_gpm']))
DD=pd.concat(dd)
run("ΔGPM(YoY cùng loại kỳ) ~ ΔP4(YoY)",DD.d_p4,DD.d_gpm,'N sai phân')
run("ΔEBITm(YoY) ~ ΔP4(YoY)",DD.d_p4,DD.d_ebitm,'N sai phân')
# biến thể TTM (chồng lấn)
TT=QT.dropna(subset=['gpm_ttm']).copy(); TT=TT[TT.quarter>='2022Q3'].copy()
def ttm_mean(key,qq):
    i=qi(qq); v=[qmean(key,qs(j)) for j in range(i-3,i+1)]; n=sum(a[1] for a in v); return sum(a[0]*a[1] for a in v)/n
TT['p4_ttm']=[ttm_mean('yellow_phosphorus',x) for x in TT.quarter]
TT['coke_ttm']=[ttm_mean('coke',x) for x in TT.quarter]
run("GPM_TTM ~ P4 TTM-mean (17 quý chồng lấn, N hiệu dụng ≈4-5)",TT.p4_ttm,TT.gpm_ttm,'chồng lấn')
run("GPM_TTM ~ than cốc TTM-mean",TT.coke_ttm,TT.gpm_ttm,'chồng lấn')
# hồi quy tuyến tính theo thời gian của GPM (xu hướng) để kiểm giả tương quan

# phân mẫu: giai đoạn giá hẹp 2024-2026 và giai đoạn giá cao 2021-2023
for nm,msk in (('H1/2024→Q3/2026 (N=8)',P.year>=2024),('Q4/2021→Q4/2023 (N=7)',(P.year<=2023))):
    Dx=P[msk]
    run(f"GPM ~ P4 cùng kỳ [{nm}]",Dx.p4,Dx.gpm); run(f"EBIT margin ~ P4 cùng kỳ [{nm}]",Dx.p4,Dx.ebitm)
run("GPM ~ chỉ số thời gian (xu hướng) [N15]",np.arange(len(P)),P.gpm)
run("P4 ~ chỉ số thời gian [N15]",np.arange(len(P)),P.p4)
R=pd.DataFrame(res)
for c_ in ['slope','slope_lo','slope_hi','loo_slope_min','loo_slope_max']: R[c_+'_per1000']=R[c_]*1000
R.to_csv('pat_corr_results.csv',index=False)
# phân vị
def pct(s): return dict(n=int(s.notna().sum()),min=s.min(),p10=s.quantile(.1),p50=s.quantile(.5),p90=s.quantile(.9),max=s.max(),mean=s.mean(),sd=s.std(),argmin=s.idxmin(),argmax=s.idxmax())
last8=P.loc[['Q4/2024','H1/2025','Q3/2025','Q4/2025','H1/2026','Q3/2026']]
S=[]
for nm,s in (('GPM kỳ định danh (toàn mẫu, 15 kỳ)',P.gpm),('GPM kỳ định danh (8 quý gần nhất = 6 kỳ)',last8.gpm),('EBIT margin kỳ định danh (toàn mẫu)',P.ebitm),('EBIT margin (8 quý gần nhất)',last8.ebitm)):
    d_=pct(s); d_['series']=nm; S.append(d_)
QN=QT.copy(); QN['npm_q']=QN.np/QN.rev
q19=QN[QN.quarter>='2022Q1']
for nm,s in (('NP margin QUÝ (19 quý 2022Q1-2026Q3)',q19.npm_q),('NP margin QUÝ (8 quý gần nhất)',q19.npm_q.iloc[-8:]),('GPM_TTM (17 quý, 2022Q3-2026Q3)',QN[QN.quarter>='2022Q3'].gpm_ttm),('GPM_TTM (8 quý gần nhất)',QN.gpm_ttm.iloc[-8:]),('EBITM_TTM (17 quý)',QN[QN.quarter>='2022Q3'].ebitm_ttm),('EBITM_TTM (8 quý gần nhất)',QN.ebitm_ttm.iloc[-8:])):
    d_=pct(s); d_['series']=nm; S.append(d_)
pd.DataFrame(S).to_csv('pat_margin_percentiles.csv',index=False)

# tự tương quan P4 vs GPM / thứ tự
out={'gp_chk':gchk,'ebit_chk':echk}
json.dump(out,open('pat_chain_checks.json','w'),indent=1)
if __name__=='__main__':
    pd.set_option('display.width',250,'display.max_columns',60,'display.max_rows',200,'display.float_format',lambda x:f'{x:,.4f}')
    print(P[['rev','np','gp','gpm','ebit','ebitm','sga','p4','p4_n','p4_lag','coke','sulfur']])
    print(out)
    print(R[['test','n','pearson','ci_lo','ci_hi','p_pearson','spearman','p_spearman','slope','slope_lo','slope_hi','loo_r_min','loo_r_max']].to_string())
    print(DD[['tag','year','d_gpm','d_p4','d_ebitm']])
