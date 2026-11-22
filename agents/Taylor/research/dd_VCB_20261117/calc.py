import json
A=json.load(open('assumptions_VCB_20261117.json'))
b=A['bs_30_09_2026']; b0=A['bs_31_12_2025_restated']; i=A['is_9m']; q=A['is_q3']; v=A['valuation']
sh=b['shares_m']; eq=b['equity_total']-b['nci']; eq0=b0['equity_total']-b0['nci']
bvps=eq/sh*1000
npl=b['npl_g3']+b['npl_g4']+b['npl_g5']; npl0=b0['npl_g3']+b0['npl_g4']+b0['npl_g5']
out={}
out['bvps']=bvps
out['npl_pct']=npl/b['loans_gross']; out['npl0_pct']=npl0/b0['loans_gross']
out['g2_pct']=b['group2']/b['loans_gross']; out['g2_0_pct']=b0['group2']/b0['loans_gross']
out['coverage']=b['loan_prov_total']/npl; out['coverage0']=b0['loan_prov_total']/npl0
out['loan_ytd']=b['loans_gross']/b0['loans_gross']-1; out['dep_ytd']=b['cust_deposits']/b0['cust_deposits']-1
out['g2_ytd']=b['group2']/b0['group2']-1; out['npl_abs_ytd']=npl/npl0-1
out['casa']=b['casa_nonterm']/b['cust_deposits']; out['casa0']=b0['casa_nonterm']/b0['cust_deposits']
out['kbnn_share']=b['kbnn_deposit']/(b['cust_deposits']+b['kbnn_deposit']); out['kbnn0_share']=b0['kbnn_deposit']/(b0['cust_deposits']+b0['kbnn_deposit'])
out['ldr_simple']=b['loans_gross']/(b['cust_deposits']+b['gtcg_issued'])
out['accr_ytd']=b['accrued_int_recv']/b0['accrued_int_recv']-1
out['npl_formation_9m']=npl-npl0  # xoa so 9T = 0 theo TM6
avg_loans=(b['loans_gross']+b0['loans_gross'])/2
out['credit_cost_9m_ann']=i['prov_2026']/avg_loans*12/9
oo=A['one_off']; oo_pat=oo['pretax_excess']*(1-oo['tax_rate_assumed'])
core9=i['pat_parent_2026']-oo_pat
out['core_pat_9m']=core9; out['core_growth']=core9/i['pat_parent_2025']-1; out['head_growth']=i['pat_parent_2026']/i['pat_parent_2025']-1
out['ppop_growth']=i['ppop_2026']/i['ppop_2025']-1; out['core_ppop_growth']=(i['ppop_2026']-oo['pretax_excess'])/i['ppop_2025']-1
out['nii_growth']=i['nii_2026']/i['nii_2025']-1; out['cir']=i['opex_2026']/(i['ppop_2026']+i['opex_2026'])
out['q3_pbt_yoy']=q['pbt_2026']/q['pbt_2025']-1; out['q3_ppop_yoy']=q['ppop_2026']/q['ppop_2025']-1
avg_eq=(eq+eq0)/2
out['roe_core_9m_ann']=core9*12/9/avg_eq; out['roe_head_9m_ann']=i['pat_parent_2026']*12/9/avg_eq
np25=sum(A['bq_np_quarter_parent'][k] for k in ['2025Q1','2025Q2','2025Q3','2025Q4'])
# normalized: core PPOP annualized - credit cost 0.6% avg loans, tax 20%
core_ppop_ann=(i['ppop_2026']-oo['pretax_excess'])*12/9
for cc in (0.004,0.006,0.008,0.010):
    out[f'roe_norm_cc{int(cc*1000)}']=(core_ppop_ann-cc*avg_loans)*0.8/avg_eq
def pb(roe,ke,g): return (roe-g)/(ke-g)
sc=v['scenarios']; ke=v['Ke_anchor']
vals={k:pb(s['roe'],ke,s['g'])*bvps for k,s in sc.items()}
out['scen']=vals; out['weighted']=sum(sc[k]['p']*vals[k] for k in sc)
base=sc['base']
out['ke_sens']={f'{d:+d}bp':pb(base['roe'],ke+d/1e4,base['g'])*bvps for d in (-100,-50,0,50,100)}
out['ke_beta_real']=pb(base['roe'],v['Ke_beta_real'],base['g'])*bvps
out['beta_sens_05']={f'{d:+d}bp':pb(base['roe'],ke+0.5*d/1e4,base['g'])*bvps for d in (-100,100)}
out['moat']={'WIDE_roe18':pb(0.18,ke,0.07)*bvps,'NARROW_roe14.6':vals['base'],'NONE_roe_eq_ke':pb(ke,ke,0.07)*bvps}
out['roe_cet1']=base['roe']*11.35/12.0; out['val_cet1']=pb(out['roe_cet1'],ke,0.07)*bvps
out['roe_anchors']={r:pb(r,ke,0.07)*bvps for r in (0.132,0.146,0.16)}
out['g_sens']={g:pb(base['roe'],ke,g)*bvps for g in (0.06,0.07,0.08)}
px=52100; out['px']=px; out['pb_px']=px/bvps; out['implied_roe_at_px']=0.07+px/bvps*(ke-0.07)
out['implied_ke_at_px']=0.07+(base['roe']-0.07)/(px/bvps)
# r4: VCSH dau ky 2025 = 196.112,9 (BCTC kiem toan 2025; dispatch Mike 22/11, chua render lai tu PDF scan)
out['np25']=np25; out['roe_2025']=np25/((eq0+196112.9)/2)
# r4: ROE 2025 chuan hoa CC 0,8% tinh tu du lieu BCTC kiem toan 2025
a=A['is_2025_audited']; avg_l25=(a['loans_end_2024']+b0['loans_gross'])/2; avg_e25=(a['equity_end_2025']+a['equity_end_2024'])/2
out['roe_2025_norm_cc8']=(a['ppop']-a['credit_cost_target']*avg_l25)*0.8/avg_e25
out['cc_loans_9m_ann']=6190/avg_loans*12/9  # TM6: du phong cho vay 9T 6.190
# r4: co tuc tien 2025
d=A['dividend_cash_2025']; out['cash_div_per_share']=d['profit_bn']/d['shares_m']*1000
# gia tri/cp (tren so cp hien hanh) sau GDKHQ co tuc tien = P/B base x (BVPS - co tuc tien/cp); tong cho co dong = + co tuc tien
pbb=pb(base['roe'],ke,base['g']); out['val_post_gdkhq']=pbb*(bvps-out['cash_div_per_share'])
out['div_haircut_vnd']=out['scen']['base']-out['val_post_gdkhq']; out['div_haircut_pct']=out['val_post_gdkhq']/out['scen']['base']-1
out['val_total_holder']=out['val_post_gdkhq']+out['cash_div_per_share']; out['total_vs_base']=out['val_total_holder']/out['scen']['base']-1
out['implied_div_payout_roe146']=1-0.07/0.146
# skeptic r1 muc 4: 2 giai doan, 5 nam tang truong BV g1, ROE 16%, chia = (ROE-g1)*BV dau ky, sau do P/B Gordon (ROE-g)/(Ke-g). HIEN THI, khong doi tam.
def two(roe,ke,g1,g,n=5):
    b=bvps;pv=0
    for t in range(1,n+1):
        pv+=(roe-g1)*b/(1+ke)**t; b*=1+g1
    return pv+b*(roe-g)/(ke-g)/(1+ke)**n
out['two_stage']={f'ke{ke}_g1{g1}':two(base['roe'],ke,g1,base['g']) for ke in (ke,ke-0.01) for g1 in (0.13,0.10)}
for k,x in out.items(): print(k, {a:round(c,4) if abs(c)<10 else round(c) for a,c in x.items()} if isinstance(x,dict) else (round(x,4) if abs(x)<10 else round(x)))
