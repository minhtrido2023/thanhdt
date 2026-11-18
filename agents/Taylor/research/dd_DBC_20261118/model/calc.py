import json, math, statistics as st, os
A=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'assumptions_DBC_20261118.json')))
q=A['np_quarterly_bn']; keys=sorted(q)
ttm={keys[i]:sum(q[k] for k in keys[i-3:i+1]) for i in range(3,len(keys))}
win=[k for k in ttm if '2023Q4'<=k<='2026Q3']
S=A['shares_m']; E=A['equity_parent_q3']; CIP=A['cip_q3']; Eop=E-CIP; scale=E/Eop
r0=A['r_ke']; g=A['g']; L=A['liquidity_discount']; w=A['weights']
PIG=A['cip_pig_haircut_bad']['pig_cip_bn']; HC=A['cip_pig_haircut_bad']['haircut']
P=A['price_for_comparison_only']['vnd']
yr={y:sum(q[k] for k in keys if k.startswith(y)) for y in('2023','2024','2025')}
q4=A['q4_26_np_est_bn']['mid']
EQ=A['equity_parent_q_bn']
roe_q={k:4*q[k]/EQ[k] for k in keys}
roe_mean15=sum(roe_q.values())/len(keys)
roe_avg15=sum(4*q[k]/((EQ[k]+EQ[p])/2) for k,p in zip(keys,['2022Q4']+keys[:-1]))/len(keys)
roe_wtd15=4*sum(q.values())/sum(EQ[k] for k in keys)
N={'roe_mean_15q':roe_mean15*E,'median_12TTM':st.median([ttm[k] for k in win]),'mean_12TTM':st.mean([ttm[k] for k in win]),
   'ttm_after_Q4_26_est':q['2026Q1']+q['2026Q2']+q['2026Q3']+q4,
   'calendar_mean_15q':sum(q.values())/len(keys)*4,'annual_mean_2023_25':st.mean(yr.values())}
np_norm=N[A['np_norm_method']]
print(f'ROE15q quy hoa/von cuoi ky: mean {roe_mean15:.4f} | avg-equity {roe_avg15:.4f} | equity-weighted {roe_wtd15:.4f} | median {st.median(roe_q.values()):.4f} | quarters {len(keys)}')
ann=[0.117,0.41,0.186,0.032,0.005,0.135,0.203]; ex20=[a for i,a in enumerate(ann) if i!=1]
import numpy as np
print(f'ROE nam 2019-25 (BQ, uoc luong): sd(all)={np.std(ann,ddof=1):.3f} sd(bo 2020)={np.std(ex20,ddof=1):.3f} half-IQR(bo 2020)={(np.percentile(ex20,75)-np.percentile(ex20,25))/2:.3f}')
print('quarters',len(keys),'TTM window:',{k:round(ttm[k],1) for k in win})
print('annual NP',{k:round(v,1) for k,v in yr.items()})
print(f'NP_norm({A["np_norm_method"]})={np_norm:.1f} EPS_norm={np_norm/S*1000:.0f} BVPS={E/S*1000:.0f} ROE_tot={np_norm/E:.4f} ROE_op={np_norm/E*scale:.4f}')
def val(np_, r=r0, gg=g, hair=0.0, cip_book=True):
    if cip_book: v=Eop*(np_/E*scale-gg)/(r-gg)+CIP-hair*PIG
    else: v=E*(np_/E-gg)/(r-gg)
    return v/S*1000
SP=A['scenario_spread_pp']; roe_base=np_norm/E
roe_bad=roe_base-SP; roe_good=roe_base+SP
OB=A['scenario_old_fixed']['bad']; OG=A['scenario_old_fixed']['good']
def center(np_base, bad=None, good=None, hc=HC, r=r0, gg=g, sp=None):
    sp=SP if sp is None else sp
    if bad is None: bad=np_base/E-sp
    if good is None: good=np_base/E+sp
    v={'bad':val(bad*E,r,gg,hc),'base':val(np_base,r,gg),'good':val(good*E,r,gg)}
    return sum(w[k]*v[k] for k in w), v
c,v=center(np_norm); cpost=c*(1-L)
print(f'scenario ROE tong von: xau {roe_bad:.4f} / base {roe_base:.4f} / tot {roe_good:.4f} (spread ±{SP})')
print('scen(value/cp):',{k:round(x) for k,x in v.items()},'| bad ROE_op',round(roe_bad*scale,4),'good ROE_op',round(roe_good*scale,4))
print(f'center_pre_liq={c:.0f} center_post_liq={cpost:.0f} zone_post_liq=[{v["bad"]*(1-L):.0f};{v["good"]*(1-L):.0f}]  P/E={cpost/(np_norm/S*1000):.1f} P/B={cpost/(E/S*1000):.2f}')
print(f'price {P} / center = {P/cpost:.2f}; 0.85*center={0.85*cpost:.0f}')
print('--- SENSITIVITY chuan hoa LNST (kich ban xau/tot DOI XUNG quanh base rieng, +/-3,25; haircut xau 40%) ---')
for k,n in N.items():
    cc,vv=center(n); cc*=(1-L)
    vs=val(n,cip_book=False)
    print(f'{k:22s} NP={n:7.1f} ROE_tot={n/E:.4f} base_val={vv["base"]:6.0f} center={cc:6.0f} price/center={P/cc:.2f} V_ngan(all-equity)={vs:6.0f}')
print('--- haircut XDCB trai heo o kich ban xau ---')
for h in (0,0.3,0.4,0.5): print(f'haircut {h:.0%}: bad={val(roe_bad*E,hair=h):.0f} center_post_liq={center(np_norm,hc=h)[0]*(1-L):.0f}')
print('--- MA TRAN 2 TRUC (chuan hoa x kich ban) ---')
M={}
for nk in ('calendar_mean_15q','roe_mean_15q'):
    for sn,(b,gd) in (('cu 9,0/15,5',(OB,OG)),('doi xung',(None,None))):
        cc=center(N[nk],bad=b,good=gd)[0]*(1-L); M[(nk,sn)]=cc
        print(f'{nk:18s} NP={N[nk]:6.1f} scen={sn:12s} center={cc:6.0f} price/center={P/cc:.2f}')
print(f'dai gia/tam theo ma tran: {min(P/x for x in M.values()):.2f} - {max(P/x for x in M.values()):.2f}; tam {min(M.values()):.0f} - {max(M.values()):.0f}')
print('--- do rong kich ban (tam chinh) ---')
for sp in (0.0325,0.045,A['scenario_wide_spread_pp']):
    cc,vv=center(np_norm,sp=sp); print(f'spread ±{sp:.4f}: bad={vv["bad"]*(1-L):.0f} good={vv["good"]*(1-L):.0f} center={cc*(1-L):.0f} price/center={P/(cc*(1-L)):.2f}')
print('--- ROBUST: kich ban xau/tot dat lai (khong dung lam tam) ---')
for nm,b,gd in (('bad=TB ROE22-24 5,7%',A['scenario_robust_alt']['bad_roe'],roe_good),('good=TTM median 12,4% (bo 2020)',roe_bad,A['scenario_robust_alt']['good_roe_ttm_median']),('ca hai',A['scenario_robust_alt']['bad_roe'],A['scenario_robust_alt']['good_roe_ttm_median'])):
    for k in ('calendar_mean_15q','roe_mean_15q'):
        cc=center(N[k],bad=b,good=gd)[0]*(1-L); print(f'{nm:34s} base={k:18s} center={cc:6.0f} price/center={P/cc:.2f}')
print('--- r (beta=1 / 0.5) ---')
for d in (-100,-50,0,50,100):
    r=r0+d/1e4*A['beta_passthrough']; cc=center(np_norm,r=r)[0]*(1-L)
    r5=r0+d/1e4*0.5; c5=center(np_norm,r=r5)[0]*(1-L)
    print(f'dep {d:+d}bp: r={r:.4f} center={cc:.0f} ({cc/cpost-1:+.1%}) | beta0.5 {c5:.0f}')
for gg in (0.04,0.05,0.06,0.07): print(f'g={gg}: center={center(np_norm,gg=gg)[0]*(1-L):.0f}')
for LL in (0,0.02,0.05): print(f'liq {LL}: {c*(1-LL):.0f}')
roe_tot=np_norm/E
print(f'all-equity (XDCB cung ROE) base={val(np_norm,cip_book=False):.0f}')
reinv=min(max(g/roe_tot,0),0.8); v_short=np_norm*(1-reinv)/(r0-g)/S*1000
cf=A['capex_3y_bn']; cfo=sum(A['cfo_3y_bn'].values())/3
capex_cash=(cf['2023Q4']+cf['2024']+cf['2025']+cf['9M2026_cash'])/3
capex=(cf['2023Q4']+cf['2024']+cf['2025']+cf['9M2026_cash']+cf['9M2026_finance_lease_added'])/3
fcfe=cfo-capex
print(f'V_short={v_short:.0f} (reinv {reinv:.3f}) | CFO3y/yr={cfo:.1f} capex_cash/yr={capex_cash:.1f} (capex/CFO {capex_cash/cfo:.2f}) capex_incl_lease/yr={capex:.1f} capex/CFO={capex/cfo:.2f} FCFE/yr={fcfe:.1f}')
print('FCFE<=0 -> V_long khong xac dinh; BO V_dai, D, co phan ky' if fcfe<=0 else 'FCFE>0: tinh V_long')
da=A['da_3y_bn_estimate']/3; c4=cfo-min(capex,da); print(f'D&A/yr (uoc luong, gom TSSH)={da:.0f} C4/yr={c4:.0f} V_C4={c4*(1+g)/(r0-g)/S*1000:.0f}')
d2=cfo-A['industry_capex_rev_median']*A['rev_net_ttm_bn_estimate']; print(f'D2/yr={d2:.0f} V_D2={d2*(1+g)/(r0-g)/S*1000:.0f}')
print(f'depreciation Q3 incl TSSH = {A["da_incl_biological_bn"]["9M2026"]-A["da_incl_biological_bn"]["h1_2026"]:.1f}; 9T parts check {482.1+74.0+5.8:.1f} + 186.1 = {482.1+74.0+5.8+186.1:.1f}')
print(f'receivable_employees/NP9M = {A["receivable_employees_bn"]["2026Q3"]/A["receivable_employees_bn"]["np_9m26"]:.3f}')
print('--- TSSH trich lap (heo thit 1877,7 gia goc = thu hoi) ---')
for p in (0.05,0.10): print(f'lech gia tri thuan {p:.0%}: {1877.7*p:.1f} ty = {1877.7*p/S*1000:.0f} d/cp; = {1877.7*p/ (np_norm):.0%} LNST chuan hoa')
print('--- MOC §9: them Q4/26 vao ROE trung binh, cua so MO RONG (khong bo Q1/23) ---')
E_q4=E  # von chu giu nguyen Q3/26 (xap xi)
for lab,npq in (('Q4/26=-50',-50),('Q4/26=+35',35),('Q4/26=+120',120)):
    rr=(sum(roe_q.values())+4*npq/E_q4)/(len(keys)+1); cc=center(rr*E)[0]*(1-L)
    print(f'{lab}: ROE mean16q={rr:.4f} center={cc:.0f} ({cc/cpost-1:+.1%}) price/center={P/cc:.2f}')
rr_roll=(sum(roe_q.values())-roe_q['2023Q1']+4*35/E_q4)/len(keys); print(f'(tham chieu cua so TRUOT 15q, Q4/26=+35: ROE={rr_roll:.4f} center={center(rr_roll*E)[0]*(1-L):.0f} -> nhay giả do roi quy lo Q1/23)')
print('--- MOC §9: doi trong so kich ban (xau/co so/tot) ---')
for wt in ((0.15,0.5,0.35),(0.35,0.5,0.15),(0.4,0.4,0.2)):
    ww=dict(zip(('bad','base','good'),wt)); _,vv=center(np_norm); cc=sum(ww[k]*vv[k] for k in ww)*(1-L); print(f'w={wt}: center={cc:.0f} ({cc/cpost-1:+.1%}) price/center={P/cc:.2f}')
