"""DD PNJ rev3 — dinh gia co dong HIEN HUU voi gia phat hanh NHAT QUAN (sua skeptic r1).
F0 = gia tri VCSH post-money tai 31/12/2026: dong LNST on dinh N tu nam dat KH, RONIC=Ke (D4) => TV = N/r.
Gia tri co dong hien huu = (F0 - PV(8.000)) / n0 = gia phat hanh cong bang P*. Khong co bien gia thi truong."""
import json, os, sys
A=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'assumptions_r3.json')))
M=A['model_r3']; P=M['scenario_params']; r0=A['discount_rate']['r']; n0=A['share_base']['shares_m']
C=M['recap_bn']; tC=M['recap_t_years']
def F0(name,r=r0):
    p=P[name]; k=p['reach_year']-2026          # nam dat N; TV tai cuoi nam k-1 = N/r
    v=p['N_steady']/r/(1+r)**(k-1)
    if 'extra_loss_bn' in p: v-=p['extra_loss_bn']/(1+r)**(p['extra_loss_year']-2026)
    return v
def ex(name,r=r0,t=tC,c=C): return max(0.0,(F0(name,r)-c/(1+r)**t))/n0*1000
W={it['name']:it['p'] for it in A['scenarios']['items']}
def wavg(r=r0,t=tC): return sum(W[k]*ex(k,r,t) for k in W)
o={'r':r0,'scen':{}}
bv26=(M['equity_parent_930']-(-M['npat_2026_plan']+M['npat_9m_2026']))/n0*1000; o['bvps_fy2026_est']=round(bv26)
for k in W:
    f=F0(k); p=ex(k)
    o['scen'][k]={'p':W[k],'F0_bn':round(f,1),'existing_ps':round(p),'issue_feasible_at_floor':p>=bv26,
                  'if_550m_issued_ps_transfer_case':round(f/(n0+M['recap_max_shares_m'])*1000)}
o['center_weighted']=round(wavg()); o['center_base']=o['scen']['base']['existing_ps']
o['zone_low']=o['scen']['bear_delay']['existing_ps']; o['zone_high']=o['scen']['bull']['existing_ps']
o['sens_r']={f'{bp:+d}bp':{'base':round(ex('base',r0+bp/1e4)),'weighted':round(wavg(r0+bp/1e4))} for bp in (-100,-50,50,100)}
o['ke_band']={str(k):{'base':round(ex('base',k)),'weighted':round(wavg(k))} for k in M['ke_band']}
o['sens_t_raise']={str(t):{'base':round(ex('base',t=t)),'weighted':round(wavg(t=t))} for t in M['sens']['t_raise_alt']}
S=M['sens']
for m in S['npm_recovery']:
    N=S['rev_2029_plan']*m; f=N/r0/(1+r0)**2; o[f'npm_{m}_N']=round(N); o[f'npm_{m}_existing_ps']=round(max(0,f-C/(1+r0)**tC)/n0*1000)
lr={k:v[1]/(v[0]*v[2]) for k,v in S['observed_loss_rates'].items()}; o['observed_loss_per_exercised']={k:round(v,4) for k,v in lr.items()}
loss80=sum(S['observed_loss_rates'][k][0]*0.8*lr[k] for k in lr); o['loss_at80_observed_rates_bn']=round(loss80,1)
o['observed_rate_reversal_bn']=round(A['one_offs']['items'][0]['amount_bn']*-1-loss80,1)
o['observed_rate_upside_ps_on_base']=round(o['observed_rate_reversal_bn']/(1+r0)**0.5/n0*1000)
o['excess_inventory_per_1000bn_ps']=round(S['excess_inventory_step_bn']/n0*1000)
o['raise_at_floor_550m_bn']=round(bv26*550/1000,1)
o['F_needed_for_floor_issue_bn']=round(bv26*n0/1000+C/(1+r0)**tC,1)
# V6 V_ngan (chi hien thi): trung vi LNST 2023-25 BQ, RONIC=Ke => N/r
vn=2112.9/r0; o['v_short_bn']=round(vn); o['v_short_ps_n0']=round(vn/n0*1000); o['v_short_ps_n1061']=round(vn/(n0+550)*1000)
json.dump(o,sys.stdout,indent=1,ensure_ascii=False); print()
