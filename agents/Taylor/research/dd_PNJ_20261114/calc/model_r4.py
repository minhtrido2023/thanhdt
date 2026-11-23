"""DD PNJ rev4 — cay ket cuc phat hanh (sua skeptic r2). F0 = VCSH van hanh post-money tai 31/12/2026 (RONIC=Ke => N/r).
O1 phat hanh 550tr cp o san: (F0 - shortfall*(1+bridge)) / (n0+550)  [co dong hien huu huong chuyen giao]
O2 khong phat hanh: kinh te ha 1 bac; (F0' - 8.000*(1+bridge)) / n0, san 0. Khong co bien gia thi truong."""
import json, os, sys
A=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'assumptions_r4.json')))
M=A['model_r3']; P=M['scenario_params']; T=M['outcome_tree']; r0=A['discount_rate']['r']; n0=A['share_base']['shares_m']; C=M['recap_bn']
W={it['name']:it['p'] for it in A['scenarios']['items']}
def F0(s,r):
    p=P[s]; k=p['reach_year']-2026; v=p['N_steady']/r/(1+r)**(k-1)
    if 'extra_loss_bn' in p: v-=p['extra_loss_bn']/(1+r)**(p['extra_loss_year']-2026)
    return v
br=T['bridge_rate_after_tax']*T['bridge_years']
def o1(s,r=r0): return max(0,F0(s,r)-T['O1_placement_at_floor']['shortfall_bn']*(1+br))/(n0+T['O1_placement_at_floor']['shares_new_m'])*1000
def o2(s,r=r0): return max(0,F0(T['O2_no_placement']['economics_shift'][s],r)-C*(1+br))/n0*1000
def center(p,r=r0): return sum(W[s]*(p*o1(s,r)+(1-p)*o2(s,r)) for s in W)
pc=T['p_success_center']; o={'r':r0,'scen':{}}
for s in W: o['scen'][s]={'p':W[s],'F0':round(F0(s,r0),1),'O1_ps':round(o1(s)),'O2_ps':round(o2(s)),'mix_ps':round(pc*o1(s)+(1-pc)*o2(s))}
o['O1_weighted']=round(sum(W[s]*o1(s) for s in W)); o['O2_weighted']=round(sum(W[s]*o2(s) for s in W))
o['center']=round(center(pc)); o['center_base_scenario']=o['scen']['base']['mix_ps']
o['p_band']={str(p):round(center(p)) for p in T['p_success_band']}
o['sens_r']={f'{bp:+d}bp':round(center(pc,r0+bp/1e4)) for bp in (-100,-50,50,100)}
o['ke_band']={str(k):round(center(pc,k)) for k in M['ke_band']}
o['zone_low']=min(o['p_band'].values()); o['zone_high']=max(o['p_band'].values())
json.dump(o,sys.stdout,indent=1,ensure_ascii=False); print()
