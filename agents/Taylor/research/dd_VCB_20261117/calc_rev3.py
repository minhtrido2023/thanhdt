# rev2 VCB - mu gia thi truong; doc assumptions rev1 (bang can doi/KQKD Q3) + rev2 (lich su goc)
import json, statistics as st
A1=json.load(open('assumptions_VCB_20261117.json')); A=json.load(open('assumptions_VCB_rev3_20261123.json'))
b=A1['bs_30_09_2026']; b0=A1['bs_31_12_2025_restated']; i9=A1['is_9m']; oo=A1['one_off']
H=A['credit_cost_history']; N=A['normalization']; V=A['valuation']; S=A['sensitivities_not_base']
L={int(k):v for k,v in H['loans_end'].items()}; P={int(k):v for k,v in H['provision_expense'].items()}; PP={int(k):v for k,v in H['ppop'].items()}
o={}
bvps=(b['equity_total']-b['nci'])/b['shares_m']*1000; o['bvps']=bvps
avgL={y:(L[y]+L[y-1])/2 for y in range(2017,2026)}
cc={y:P[y]/avgL[y] for y in avgL}; o['cc_series_pct']={y:round(cc[y]*100,3) for y in cc}
o['cc_mean_17_25']=st.mean(cc.values()); o['cc_median_17_25']=st.median(cc.values())
o['cc_mean_21_25']=st.mean(cc[y] for y in range(2021,2026)); o['cc_mean_23_25']=st.mean(cc[y] for y in range(2023,2026))
dprov=sum(H[k]['2025']-H[k]['2016'] for k in ('loan_prov_balance','inv_sec_prov_balance','interbank_prov_balance'))
loss=sum(P[y] for y in range(2017,2026))-dprov; o['loss_rate_17_25']=loss/sum(avgL.values())
res_ratio=H['loan_prov_balance']['2025']/L[2025]; g=N['g_loans_for_maint']
o['maint']=res_ratio*g/(1+g); cc_base=o['loss_rate_17_25']+o['maint']; o['cc_base']=cc_base
avgL26=(b['loans_gross']+b0['loans_gross'])/2; eq=b['equity_total']-b['nci']; eq0=b0['equity_total']-b0['nci']; avgE26=(eq+eq0)/2
lev=avgL26/avgE26; o['lev']=lev
m={y:PP[y]/avgL[y] for y in PP}; o['ppop_margin_pct']={y:round(m[y]*100,3) for y in m}
m26=(i9['ppop_2026']-oo['pretax_excess'])*12/9/avgL26; o['m26_core']=m26
m_bull=st.mean([m[2022],m[2023],m[2024],m[2025],m26]); o['m_5y_mean']=m_bull
nii={int(k):v for k,v in H['nii'].items()}; o['nii_loans_pct']={y:round(nii[y]/avgL[y]*100,3) for y in nii}; o['nii_loans_2026']=i9['nii_2026']*12/9/avgL26
t=N['tax']; W=A['welfare_fund']; fw=W['fwf_2025']/W['np_2025']; o['welfare_ratio']=fw; o['welfare_ratio_2024']=W['fwf_2024']/W['np_2024']
roe=lambda mm,c:(mm-c)*lev*(1-t)*(1-fw)
cc26=i9['prov_2026']*12/9/avgL26; o['cc_9m26']=cc26
cc_5y=st.mean([cc[2022],cc[2023],cc[2024],cc[2025],cc26]); o['cc_5y_22_26']=cc_5y
o['roe_rev2_inputs_with_welfare']=roe(m26,cc_base)
sc={'bear':(m[2025],o['cc_mean_17_25']),'base':(m26,cc26),'bull':(m_bull,cc_5y)}
o['roe']={k:roe(*v) for k,v in sc.items()}
ke=V['Ke_anchor']; gg=V['g']; pb=lambda r,k=ke,g_=gg:(r-g_)/(k-g_)
val={k:pb(r)*bvps for k,r in o['roe'].items()}; o['val']=val; o['pb']={k:pb(r) for k,r in o['roe'].items()}
pr=V['probs']; o['weighted']=sum(pr[k]*val[k] for k in val)
rb=o['roe']['base']
o['ke_sens']={f'{d:+d}bp':pb(rb,ke+d/1e4)*bvps for d in (-100,-50,0,50,100)}
o['ke_sens_b05']={f'{d:+d}bp':pb(rb,ke+0.5*d/1e4)*bvps for d in (-100,-50,50,100)}
o['ke_D4']={k:pb(rb,k)*bvps for k in V['Ke_band_D4']}; o['ke_beta_real']=pb(rb,V['Ke_beta_real_read'])*bvps
o['cc_grid']={c:pb(roe(m26,c))*bvps for c in (0.005,0.006,cc_base,0.008,o['cc_mean_17_25'])}
o['cc_grid_roe']={c:roe(m26,c) for c in (0.005,0.006,cc_base,0.008,o['cc_mean_17_25'])}
o['q3_pair']={'m':17401.785*4/((1816093.286+1673525.675)/2),'cc':6184.109*4/((1816093.286+1673525.675)/2)}
o['m_grid']={round(mm,4):pb(roe(mm,cc26))*bvps for mm in (m[2025],m26,m_bull)}
o['g_sens']={x:pb(rb,ke,x)*bvps for x in (0.06,0.08)}
o['weighted_ke']={f'{d:+d}bp':sum(pr[k]*pb(o['roe'][k],ke+d/1e4)*bvps for k in val) for d in (-100,100)}
# CET1/D-SIB: ROE pha loang theo CAR/muc tieu
r_c=rb*S['car_now']/S['car_target']; o['roe_car']=r_c; o['val_car']=pb(r_c)*bvps
# CBBank: ton that minh hoa tru VCSH
o['cbbank']={h:pb(rb)*(bvps-h/b['shares_m']*1000) for h in S['cbbank_equity_hit_bn']}
# co tuc phan con lai neu bang TIEN (dieu kien)
res=S['dividend_2025_profit_bn']-S['dividend_cash_paid_bn']; dps=res/b['shares_m']*1000; o['resid_dps_if_cash']=dps
o['val_base_post_if_cash']=pb(rb)*(bvps-dps); o['holder_total_if_cash']=o['val_base_post_if_cash']+dps
o['weighted_post_if_cash']=sum(pr[k]*o['pb'][k]*(bvps-dps) for k in val)
o['stock_div_ratio_if_stock']=res/(b['shares_m']*10)
# hai giai doan (hien thi)
def two(r,k,g1,n=5):
    B=bvps;pv=0
    for y in range(1,n+1): pv+=(r-g1)*B/(1+k)**y; B*=1+g1
    return pv+B*pb(r,k)/(1+k)**n
o['two_stage']={f'ke{k}_g1{g1}':two(rb,k,g1) for k in (ke,ke-0.01) for g1 in (0.13,0.10)}
o['implied_payout_base']=1-gg/rb
# kiem cheo xac minh
o['guar_ratio_q3_vs_2024']=(9549.855+128899.826)/(286.899+58052.470); o['constr_growth_2025']=155288.015/90512.980-1
o['etr_2025']=8821.697/44019.637
o['nii_assets_2025']=58771.410/((2085873.522+2442279.166)/2); o['nii_assets_9m26']=i9['nii_2026']*4/3/((2442279.166+b['total_assets'])/2)
o['equity_roll_gap']=196112.907+35177.663-3760-2975.811-224487.205
def r(x): return round(x,4) if abs(x)<10 else round(x)
for k,x in o.items(): print(k, {a:r(c) for a,c in x.items()} if isinstance(x,dict) else r(x))

for nm,(mm,c) in [('q3_pair',(o['q3_pair']['m'],o['q3_pair']['cc']))]: print('q3_pair_val', round(pb(roe(mm,c))*bvps), round(roe(mm,c),4))
print('none_roe_eq_ke', round(bvps))
