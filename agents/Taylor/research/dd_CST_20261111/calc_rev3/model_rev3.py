import json, math, csv, statistics as st, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
A=json.load(open('assumptions_rev3.json')); SH=A['shares']
vps=lambda bn: bn*1e9/SH
T=A['life_years']; rho=A['book_recovery_at_end']; R=A['r']
B=A['B0_bn']+A['B0_adj_leak_on_accrued_2026']
ann=lambda r,T:(1-(1+r)**-T)/r
def leak(N,kind='rule',alpha=A['leak_rule']['alpha'],cap=A['leak_rule']['cap_bn']):
    if kind=='rule': return min(alpha*N,cap) if N>0 else 0
    if kind=='prop': return alpha*N
    if kind=='fixed': return cap
    return 0.0
def val(N,r=R,T=T,rho=rho,kind='rule',alpha=A['leak_rule']['alpha'],cap=A['leak_rule']['cap_bn'],C=A['compliance_outflow_bn_yr'],B=B,extra=0.0):
    Nsh=N-leak(N,kind,alpha,cap)-C-extra
    return vps(rho*B*(1+r)**-T + Nsh*ann(r,T))
PD=A['payout_retained']['D_bn']
def pay_delta(r=R,T=T,i_at=0.064,D=PD): return vps(D - i_at*D*ann(r,T) - D*(1+r)**-T)
_val=val
def val(N,pay=True,i_at=0.064,**kw):
    return _val(N,**kw) + (pay_delta(r=kw.get('r',R),T=kw.get('T',T),i_at=i_at) if pay else 0.0)
def center(**kw):
    return sum(s['w']*val(s['N'],**kw) for s in A['scenarios'].values())
o={k:val(s['N']) for k,s in A['scenarios'].items()}; o['center']=center()
o['pay_delta_base']=pay_delta()
o['Nsh']={k:round(s['N']-leak(s['N'])-A['compliance_outflow_bn_yr'],2) for k,s in A['scenarios'].items()}
S={}
S['rev1_equiv_noleak_noC_B961']=center(kind='none',C=0,B=A['B0_bn'],pay=False)
S['rev2_equiv_nopay']=center(pay=False)
S['pay_cash_funded_4pct']=center(i_at=0.04)
S['alpha_0.50']=center(alpha=0.50)
S['alpha_0.50_cap82']=center(alpha=0.4995)
S['leak_prop_37pct']=center(kind='prop',alpha=0.37)
S['leak_fixed_70']=center(kind='fixed',cap=70)
S['leak_fixed_50']=center(kind='fixed',cap=50)
S['no_compliance_C']=center(C=0)
S['deposit_interest_locked_5.9']=center(extra=5.9)
for dr in (-0.01,-0.005,0.005,0.01):
    S[f'r{dr*1e4:+.0f}bp']=center(r=R+dr)
for rr in (0.11,0.12,0.123,0.134): S[f'r_{rr}']=center(r=rr)
S['life_2030_T4']=center(T=4)
S['rho_1']=center(rho=1.0); S['rho_0']=center(rho=0.0)
# payout of 130.66 retained, debt funded @8% pre-tax (after-tax 6.4%), debt repaid at end
# expansion: equity part 30% of remaining ~1.020 (uoc luong) earning ROE 7.9%, 19y, rho 0.5
I=0.3*1020; S['expansion_negNPV_delta_dps']=vps(I*(0.079*ann(R,T)+0.5*(1+R)**-T-1))
S['center_display_expansion_p0.3']=center()+0.3*S['expansion_negNPV_delta_dps']
o['sens']=S
# V6
Nsh_base=o['Nsh']['base']
o['V_ngan']=vps(Nsh_base/R)
fcfe={'2024':289.572-276.057+13.901+(155.0-97.66),'2025':169.881-359.238+3.29+(310.414-80.718)}
o['fcfe']=fcfe; fc=st.mean(fcfe.values()); o['V_dai']=vps(fc/R) if fc>0 else None
o['D']=abs(math.log(o['V_ngan']/o['V_dai'])) if o['V_dai'] else None
# liquidity
px=list(csv.DictReader(open('px_cst.csv')))
P=[float(x['Close']) for x in px]; V=[float(x['Price'])*float(x['Volume'])/1e9 for x in px]
rets=[math.log(P[i]/P[i-1]) for i in range(1,len(P))][-250:]
sig=st.pstdev(rets); adv60=st.median(V[-60:]); adv250=st.median(V[-250:])
liq={}
for q in A['liquidity']['sizes_bn']:
    ck=sig*math.sqrt(q/adv60)
    liq[q]=dict(ck60=ck,center_post=o['center']*(1-ck),bear_post=o['bear']*(1-ck),bull_post=o['bull']*(1-ck),base_post=o['base']*(1-ck),sess10=q/(0.1*adv60),sess20=q/(0.2*adv60))
o['liq']=dict(sigma_d=sig,adv60_bn=adv60,adv250_bn=adv250,by_size=liq)
print(json.dumps(o,indent=1,default=lambda x:round(x,4)))
json.dump(o,open('model_out_rev3.json','w'),indent=1)
