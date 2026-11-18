import json, math, statistics as st, sys, os
A=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'assumptions_DBC_20261118.json')))
q=A['np_quarterly_bn']; keys=sorted(q)
ttm={keys[i]:sum(q[k] for k in keys[i-3:i+1]) for i in range(3,len(keys))}
win=[k for k in ttm if '2023Q4'<=k<='2026Q3']
np_norm=st.median([ttm[k] for k in win])
S=A['shares_m']; E=A['equity_parent_q3']; CIP=A['cip_q3']; Eop=E-CIP
r0=A['r_ke']; g=A['g']
roe_tot=np_norm/E; scale=E/Eop
print('TTM window:',{k:round(ttm[k],1) for k in win})
print(f'NP_norm={np_norm:.1f} EPS_norm={np_norm/S*1000:.0f} BVPS={E/S*1000:.0f} ROE_tot={roe_tot:.4f} ROE_op={roe_tot*scale:.4f}')
def val(roe_tot_, r=r0, gg=g, cip_book=True):
    if cip_book:
        roe_op=roe_tot_*scale; v=Eop*(roe_op-gg)/(r-gg)+CIP
    else: v=E*(roe_tot_-gg)/(r-gg)
    return v/S*1000
sc=dict(A['scenario_roe_total_equity']); sc['base']=roe_tot
vals={k:val(v) for k,v in sc.items()}; w=A['weights']
center=sum(w[k]*vals[k] for k in w)
L=A['liquidity_discount']
print('scen', {k:(round(sc[k],4),round(sc[k]*scale,4),round(vals[k])) for k in sc})
print(f'center_pre_liq={center:.0f} center_post_liq={center*(1-L):.0f}  zone_post_liq=[{vals["bad"]*(1-L):.0f};{vals["good"]*(1-L):.0f}]')
print(f'sens: all-equity ROE_tot (CIP not at book) base={val(roe_tot,cip_book=False):.0f}')
for d in (-100,-50,0,50,100):
    r=r0+d/1e4*A['beta_passthrough']; c=sum(w[k]*val(sc[k],r=r) for k in w)*(1-L)
    r5=r0+d/1e4*0.5; c5=sum(w[k]*val(sc[k],r=r5) for k in w)*(1-L)
    print(f'dep {d:+d}bp: r={r:.4f} center={c:.0f} ({c/(center*(1-L))-1:+.1%}) | beta0.5 {c5:.0f}')
for gg in (0.04,0.05,0.06,0.07):
    print(f'g={gg}: center={sum(w[k]*val(sc[k],gg=gg) for k in w)*(1-L):.0f}')
for LL in (0,0.02,0.05): print(f'liq {LL}: {center*(1-LL):.0f}')
# two bases
reinv=min(max(g/roe_tot,0),0.8)
v_short=np_norm*(1-reinv)/(r0-g)/S*1000
cfo=sum(A['cfo_3y_bn'].values())/3; capex=sum(A['capex_3y_bn'].values())/3
fcfe=cfo-capex; v_long=fcfe*(1+g)/(r0-g)/S*1000
da=A['da_3y_bn_estimate']/3; c4=cfo-min(capex,da); v_c4=c4*(1+g)/(r0-g)/S*1000
d2=cfo-A['industry_capex_rev_median']*A['rev_net_ttm_bn_estimate']; v_d2=d2*(1+g)/(r0-g)/S*1000
D=abs(math.log(v_short/v_long)) if v_long>0 else float('nan')
print(f'V_short={v_short:.0f} (reinv {reinv:.3f}) | CFO3y/yr={cfo:.0f} capex/yr={capex:.0f} capex/CFO={capex/cfo:.2f} FCFE/yr={fcfe:.0f} V_long={v_long:.0f} D={D:.2f} (ln2={math.log(2):.2f} ln3={math.log(3):.2f})')
print(f'C4/yr={c4:.0f} V_C4={v_c4:.0f} | D2/yr={d2:.0f} V_D2={v_d2:.0f}')
print(f'PE_center={center*(1-L)/(np_norm/S*1000):.1f} PB_center={center*(1-L)/(E/S*1000):.2f}')
