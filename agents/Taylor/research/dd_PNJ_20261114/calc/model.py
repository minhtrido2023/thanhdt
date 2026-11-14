import json, math, sys, os
A=json.load(open(os.path.join(os.path.dirname(__file__),'assumptions.json')))
r=A['r_ke']; g=A['g_terminal']; n0=A['n0_shares_m']
def F(N,roe,r=r,g=g,yrs=3):
    b=min(max(g/roe,0.0),0.8); return N*(1+g)*(1-b)/(r-g)/(1+r)**yrs
out={}
E26=A['equity_parent_930']-(A['npat_2026_plan']*-1+A['npat_9m_2026_parent'])  # 13182 - 6741.7
out['Q4_implied_npat']=A['npat_2026_plan']-A['npat_9m_2026_parent']
out['equity_2026_est']=E26; out['bvps_2026_est']=E26/n0*1000
out['bvps_930']=A['equity_parent_930']/n0*1000
for nn in (550.0,400.0):
    for k,s in A['scenarios'].items():
        f=F(s['N2029'],s['roe']); out[f'{k}_F_bn']=round(f,1); out[f'{k}_ps_n{int(nn)}']=round(f/(n0+nn)*1000)
# r sensitivity (base, n550): r = 13.5 + beta*d
for beta in (1.0,0.5):
    for d in (-0.01,-0.005,0.005,0.01):
        rr=r+beta*d; s=A['scenarios']['base']; out[f'base_r_b{beta}_d{int(d*1e4)}bp']=round(F(s['N2029'],s['roe'],r=rr)/(n0+550)*1000)
# ROE grid base N
for roe in (0.10,0.135,0.20):
    out[f'base_roe{roe}']=round(F(1600,roe)/(n0+550)*1000)
# V_ngan (nen loi nhuan TIEN khung hoang), median TTM 2023/24/25 BQ
N=sorted([1971.5,2112.9,2828.5])[1]; roe=0.215
out['V_ngan_raw_bn']=round(N*(1-min(g/roe,0.8))/(r-g),1); out['V_ngan_raw_ps']=round(out['V_ngan_raw_bn']/n0*1000)
json.dump(out,sys.stdout,indent=1,ensure_ascii=False); print()
W=A['weights']; out2={}
for nn in (550,400):
    out2[f'weighted_ps_n{nn}']=round(sum(W[k]*out[f'{k}_ps_n{nn}'] for k in ('bull','base','bear')))
out2['V_ngan_post_dilution_550']=round(out['V_ngan_raw_bn']/(n0+550)*1000)
out2['cfo3_avg']=round(sum(v for k,v in A['cfo_ttm'].items() if k!='src')/3,1)
out2['zone_cheap_085x']=round(0.85*out2['weighted_ps_n550'])
json.dump(out2,sys.stdout,indent=1); print()
