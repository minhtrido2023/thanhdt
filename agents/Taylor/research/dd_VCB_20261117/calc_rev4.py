# rev4 VCB - mu gia thi truong. Doc assumptions rev1 (BS/IS Q3) + rev4 (lich su kiem toan, cua so)
import json, statistics as st
A1=json.load(open('assumptions_VCB_20261117.json')); A=json.load(open('assumptions_VCB_rev4_20261123.json'))
b=A1['bs_30_09_2026']; b0=A1['bs_31_12_2025_restated']; i9=A1['is_9m']; oo=A1['one_off']
H=A['credit_cost_history']; N=A['normalization']; V=A['valuation']; S=A['sensitivities_not_base']; W=A['welfare_fund']
L={int(k):v for k,v in H['loans_end'].items()}; P={int(k):v for k,v in H['provision_expense'].items()}; PP={int(k):v for k,v in H['ppop'].items()}
avgL={y:(L[y]+L[y-1])/2 for y in range(2017,2026)}
m={y:PP[y]/avgL[y] for y in PP}; cc={y:P[y]/avgL[y] for y in avgL}
avgL26=(b['loans_gross']+b0['loans_gross'])/2
m['9T26']=(i9['ppop_2026']-oo['pretax_excess'])*12/9/avgL26; cc['9T26']=i9['prov_2026']*12/9/avgL26
sp={k:m[k]-cc[k] for k in m}
o={}; o['spread_pct']={k:round(v*100,3) for k,v in sp.items()}
fw=W['fwf_2025']/W['np_2025']; t=N['tax']; sh=b['shares_m']
eq_end=b['equity_total']-b['nci']
acc=fw*A['welfare_accrual_2026']['np_9m26']; o['ktpl_accrual_bn']=acc; o['ktpl_accrual_ps']=acc/sh*1000
eq_adj=eq_end-acc; bvps=eq_adj/sh*1000; o['bvps_rev3']=eq_end/sh*1000; o['bvps_adj']=bvps
lev=b['loans_gross']/eq_adj; o['lev_end_adj']=lev
o['lev_end_unadj']=b['loans_gross']/eq_end
roe=lambda s:s*lev*(1-t)*(1-fw)
ke=V['Ke_anchor']; g=V['g']; pb=lambda r,k=ke,g_=g:(r-g_)/(k-g_)
val=lambda s,k=ke:pb(roe(s),k)*bvps
yrs22=[2022,2023,2024,2025,'9T26']
s_bull=st.mean(m[y] for y in yrs22)-st.mean(cc[y] for y in yrs22)
sc={'bear':sp[2017],'base':sp['9T26'],'bull':s_bull}
o['scen_spread']={k:round(v*100,3) for k,v in sc.items()}
o['roe']={k:roe(v) for k,v in sc.items()}; o['pb']={k:pb(r) for k,r in o['roe'].items()}
V_={k:val(v) for k,v in sc.items()}; o['val']=V_
pr=V['probs']; w=sum(pr[k]*V_[k] for k in V_); o['weighted']=w
o['weighted_ke']={f'{d:+d}bp':sum(pr[k]*pb(o['roe'][k],ke+d/1e4)*bvps for k in sc) for d in (-100,100)}
# cua so thay the cho base (hien thi)
cyc=st.mean(m[y] for y in range(2017,2026))-st.mean(cc[y] for y in range(2017,2026))
alt={'FY2025':sp[2025],'cycle_17_25':cyc,'median_year_17_25':st.median(sp[y] for y in range(2017,2026)),'cycle_17_21':st.mean(m[y] for y in range(2017,2022))-st.mean(cc[y] for y in range(2017,2022))}
o['alt_base_spread_pct']={k:round(v*100,3) for k,v in alt.items()}
o['alt_base_val']={k:val(v) for k,v in alt.items()}
o['alt_base_weighted']={k:pr['bear']*V_['bear']+pr['base']*val(v)+pr['bull']*V_['bull'] for k,v in alt.items()}
allw=[2017+i for i in range(9)]+['9T26']; o['equal_wt_all_10_windows']=st.mean(val(sp[k]) for k in allw)
o['bear_rev3_stress_spread_pct']=round((m[2025]-st.mean(cc[y] for y in range(2017,2026)))*100,3)
o['ke_sens_base']={f'{d:+d}bp':pb(o['roe']['base'],ke+d/1e4)*bvps for d in (-100,-50,50,100)}
o['ke_sens_base_b05']={f'{d:+d}bp':pb(o['roe']['base'],ke+0.5*d/1e4)*bvps for d in (-100,-50,50,100)}
o['ke_D4']={k:pb(o['roe']['base'],k)*bvps for k in V['Ke_band_D4']}
o['g_sens']={x:pb(o['roe']['base'],ke,x)*bvps for x in (0.06,0.08)}
rb=o['roe']['base']; o['val_car12']=pb(rb*S['car_now']/S['car_target'])*bvps
o['cbbank']={h:pb(rb)*(bvps-h/sh*1000) for h in S['cbbank_equity_hit_bn']}
res=S['dividend_2025_profit_bn']-S['dividend_cash_paid_bn']; dps=res/sh*1000; o['resid_dps_if_cash']=dps
o['weighted_post_if_cash']=sum(pr[k]*o['pb'][k]*(bvps-dps) for k in sc)
o['rebase_factor_bonus_12_8']=1/1.128; o['rebase_factor_bonus_plus_stockdiv']=1/(1+0.128+res/(sh*10))
o['zone_rebased_bonus_only']=[o['weighted_ke']['+100bp']/1.128, w/1.128, o['weighted_ke']['-100bp']/1.128]
o['casa']=b['casa_nonterm']/b['cust_deposits']
def r(x): return round(x,4) if abs(x)<10 else round(x)
for k,x in o.items(): print(k, {a:r(c) for a,c in x.items()} if isinstance(x,dict) else ([r(c) for c in x] if isinstance(x,list) else r(x)))
