import json, os, sys
A=json.load(open(os.path.join(os.path.dirname(__file__),'assumptions_r2.json'))); R=A['r2']
r=A['r_ke']; g0=A['g_terminal']; n0=A['n0_shares_m']
def F(N,roe,g=g0,rr=r,yrs=3):
    b=min(max(g/roe,0.0),0.8); return N*(1+g)*(1-b)/(rr-g)/(1+rr)**yrs
ps=lambda f,n=550.0: round(f/(n0+n)*1000)
o={}
# (2) bien gop truoc du phong Q3
gp,rev=R['gross_profit_q3_2026'],R['rev_net_q3_2026']
lo=R['lctt03_prov_9m_2026']-R['lctt03_prov_h1_2026']; hi=R['inv_prov_3009']-R['inv_prov_3006']
o['q3_prov_lctt03']=round(lo,1); o['q3_inv_prov_delta']=round(hi,1)
o['gpm_q3_reported']=round(gp/rev,4); o['gpm_q3_preprov_lo']=round((gp+lo)/rev,4); o['gpm_q3_preprov_hi']=round((gp+hi)/rev,4)
o['npm_2029_plan']=round(A['plan_npat']['2029']/A['plan_rev']['2029'],4)
o['npm_2028_plan']=round(A['plan_npat']['2028']/A['plan_rev']['2028'],4)
o['npm_9m_2025']=round(1610.4/25353.1,4)
# (3) ngan hang
bm=R['bank_moves']; o['bank_delta']=round(R['bank_loans_3009']-R['bank_loans_3112'],1)
o['bank_delta_pct']=round(R['bank_loans_3009']/R['bank_loans_3112']-1,4)
o['bank_by_name_delta']={k:round(v[1]-v[0],1) for k,v in bm.items()}
# (5) san gia phat hanh
eqp=R['equity_total_3006']-R['nci_3006']; o['bvps_h1_sx']=round(eqp/n0*1000)
bv26=(A['equity_parent_930']-(-A['npat_2026_plan']+A['npat_9m_2026_parent']))/n0*1000; o['bvps_2026_est']=round(bv26)
o['raise_at_bvps2026_550m_bn']=round(bv26*550/1000,1)
o['price_needed_8000bn_550m']=round(8000/550*1000)
o['raise_at_bvps_h1_550m_bn']=round(o['bvps_h1_sx']*550/1000,1)
# (8) kich ban
sc=dict(A['scenarios']); sc['bear_alt']=R['bear_alt']
for k,s in sc.items():
    for g in (g0,0.0):
        o[f'{k}_g{int(g*100)}_ps550']=ps(F(s['N2029'],s['roe'],g=g)); o[f'{k}_g{int(g*100)}_ps400']=ps(F(s['N2029'],s['roe'],g=g),400.0)
o['level_grid']={}
for N in R['level_grid']:
    roe=N/R['equity_post_recap_est']
    o['level_grid'][str(N)]={'roe':round(roe,4),'g5_n550':ps(F(N,roe)),'g0_n550':ps(F(N,roe,g=0.0)),'g5_n400':ps(F(N,roe),400.0)}
# kiem nguoc: tam r1 de doi chieu
W=A['weights']; o['r1_weighted_ps550_reproduced']=round(sum(W[k]*ps(F(A['scenarios'][k]['N2029'],A['scenarios'][k]['roe'])) for k in ('bull','base','bear')))
json.dump(o,sys.stdout,indent=1,ensure_ascii=False); print()
