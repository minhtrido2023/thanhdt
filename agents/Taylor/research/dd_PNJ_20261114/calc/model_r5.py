"""DD PNJ rev5 — cay ket cuc phat hanh (sua skeptic r3). Gia tri/cp hien huu:
O1 phat hanh 550tr cp o san BVPS: (F0 + PV LNST 2027-28 - shortfall) / (n0+550)
O2 khong phat hanh, tai tro no/ton kho, kinh te giu nguyen: (F0 + PV LNST 2027-28 - 8.000) / n0, san 0.
Khong co bien gia thi truong. Chay: python3 model_r5.py > model_r5_out.json"""
import json, os, sys
A=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'assumptions_r5.json')))
M=A['model_r3']; P=M['scenario_params']; T=M['outcome_tree']; r0=A['discount_rate']['r']; n0=A['share_base']['shares_m']
W={it['name']:it['p'] for it in A['scenarios']['items']}; PR=M['pre_reach_npat']
bvps=(M['equity_parent_930']+M['npat_2026_plan']-M['npat_9m_2026'])/n0*1000
short=M['recap_bn']-T['O1_placement_at_floor']['shares_new_m']*bvps/1000
def F0(s,r):
    p=P[s]; k=p['reach_year']-2026; v=p['N_steady']/r/(1+r)**(k-1)
    if 'extra_loss_bn' in p: v-=p['extra_loss_bn']/(1+r)**(p['extra_loss_year']-2026)
    return v
def pre(s,r,on=True): return sum(v/(1+r)**(int(y)-2026) for y,v in PR[s].items()) if on else 0.0
def o1(s,r=r0,re=True): return max(0,F0(s,r)+pre(s,r,re)-short)/(n0+T['O1_placement_at_floor']['shares_new_m'])*1000
def o2(s,r=r0,re=True): e=T['O2_no_placement']['economics_shift'][s]; return max(0,F0(e,r)+pre(e,r,re)-T['O2_no_placement']['deduct_bn'])/n0*1000
def center(p,r=r0,re=True): return sum(W[s]*(p*o1(s,r,re)+(1-p)*o2(s,r,re)) for s in W)
pc=T['p_success_center']; o={'r':r0,'bvps_floor':round(bvps,1),'shortfall_bn':round(short,1),'scen':{}}
for s in W: o['scen'][s]={'w':W[s],'F0':round(F0(s,r0),1),'PV_2027_28':round(pre(s,r0),1),'O1_ps':round(o1(s)),'O2_ps':round(o2(s)),'mix_ps':round(pc*o1(s)+(1-pc)*o2(s))}
o['O1_weighted']=round(sum(W[s]*o1(s) for s in W)); o['O2_weighted']=round(sum(W[s]*o2(s) for s in W))
o['center']=round(center(pc)); o['center_base_scenario']=o['scen']['base']['mix_ps']
o['p_band']={str(p):round(center(p)) for p in T['p_success_band']}
o['p_step_0.1']=round(center(pc+0.1)-center(pc))
o['sens_r']={f'{bp:+d}bp':round(center(pc,r0+bp/1e4)) for bp in (-100,-50,50,100)}
o['ke_band']={str(k):round(center(pc,k)) for k in M['ke_band']}
o['sens_no_2027_28']=round(center(pc,re=False))
o['O1_premium_floor_vs_value_pct']=round((bvps/o['O1_weighted']-1)*100,1)
eq=(M['equity_parent_930']+M['npat_2026_plan']-M['npat_9m_2026'])
L={'L0':0.0}; L.update({f'L_h{h}':max(0,(eq-h*A['working_capital']['nwc_bn'])/n0*1000) for h in (0.2,0.4)})
o['O3_L_ps']={k:round(v) for k,v in L.items()}
o['O3_shift']={f'q{q}_{k}':round(center(pc)+(1-pc)*q*(v-o['O2_weighted'])) for q in (0.1,0.2) for k,v in L.items()}
o['zone_low']=min(o['p_band'].values()); o['zone_high']=max(o['p_band'].values())
json.dump(o,sys.stdout,indent=1,ensure_ascii=False); print()
