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
N={'median_12TTM':st.median([ttm[k] for k in win]),'mean_12TTM':st.mean([ttm[k] for k in win]),
   'ttm_after_Q4_26_est':q['2026Q1']+q['2026Q2']+q['2026Q3']+q4,
   'calendar_mean_15q':sum(q.values())/len(keys)*4,'annual_mean_2023_25':st.mean(yr.values())}
np_norm=N[A['np_norm_method']]
print('quarters',len(keys),'TTM window:',{k:round(ttm[k],1) for k in win})
print('annual NP',{k:round(v,1) for k,v in yr.items()})
print(f'NP_norm({A["np_norm_method"]})={np_norm:.1f} EPS_norm={np_norm/S*1000:.0f} BVPS={E/S*1000:.0f} ROE_tot={np_norm/E:.4f} ROE_op={np_norm/E*scale:.4f}')
def val(np_, r=r0, gg=g, hair=0.0, cip_book=True):
    if cip_book: v=Eop*(np_/E*scale-gg)/(r-gg)+CIP-hair*PIG
    else: v=E*(np_/E-gg)/(r-gg)
    return v/S*1000
roe_bad=A['scenario_roe_total_equity']['bad']; roe_good=A['scenario_roe_total_equity']['good']
def center(np_base, bad=roe_bad, good=roe_good, hc=HC, r=r0, gg=g):
    v={'bad':val(bad*E,r,gg,hc),'base':val(np_base,r,gg),'good':val(good*E,r,gg)}
    return sum(w[k]*v[k] for k in w), v
c,v=center(np_norm); cpost=c*(1-L)
print('scen(value/cp):',{k:round(x) for k,x in v.items()},'| bad ROE_op',round(roe_bad*scale,4),'good ROE_op',round(roe_good*scale,4))
print(f'center_pre_liq={c:.0f} center_post_liq={cpost:.0f} zone_post_liq=[{v["bad"]*(1-L):.0f};{v["good"]*(1-L):.0f}]  P/E={cpost/(np_norm/S*1000):.1f} P/B={cpost/(E/S*1000):.2f}')
print(f'price {P} / center = {P/cpost:.2f}; 0.85*center={0.85*cpost:.0f}')
print('--- SENSITIVITY chuan hoa LNST (kich ban xau/tot co dinh, haircut xau 40%) ---')
for k,n in N.items():
    cc,vv=center(n); cc*=(1-L)
    vs=val(n,cip_book=False)
    print(f'{k:22s} NP={n:7.1f} ROE_tot={n/E:.4f} base_val={vv["base"]:6.0f} center={cc:6.0f} price/center={P/cc:.2f} V_ngan(all-equity)={vs:6.0f}')
print('--- haircut XDCB trai heo o kich ban xau ---')
for h in (0,0.3,0.4,0.5): print(f'haircut {h:.0%}: bad={val(roe_bad*E,hair=h):.0f} center_post_liq={center(np_norm,hc=h)[0]*(1-L):.0f}')
print('--- ROBUST: kich ban xau/tot dat lai (khong dung lam tam) ---')
for nm,b,gd in (('bad=TB ROE22-24 5,7%',A['scenario_robust_alt']['bad_roe'],roe_good),('good=TTM median 12,4% (bo 2020)',roe_bad,A['scenario_robust_alt']['good_roe_ttm_median']),('ca hai',A['scenario_robust_alt']['bad_roe'],A['scenario_robust_alt']['good_roe_ttm_median'])):
    for k in ('calendar_mean_15q','median_12TTM'):
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
