import json, math, csv, statistics as st
A=json.load(open('assumptions.json')); S=A['shares']/1e9  # bn shares -> VND/share = bn VND / S /1e? 
def vps(bn): return bn*1e9/A['shares']
r=A['r']; T=A['life_years']; B=A['B0_bn']; rho=A['book_recovery_at_end']
ann=lambda r,T:(1-(1+r)**-T)/r
def ri_value(N,r=r,T=T,rho=rho):
    return B + (N-r*B)*ann(r,T) - (1-rho)*B*(1+r)**-T
out={}
for k,s in A['scenarios'].items(): out[k]=vps(ri_value(s['N']))
center=sum(A['scenarios'][k]['w']*out[k] for k in out)
out['center']=center
# sensitivities
sens={}
for dr in (-0.01,-0.005,0.005,0.01):
    rr=r+dr; sens[f'dep{dr*1e4:+.0f}bp_b1']=sum(A['scenarios'][k]['w']*vps(ri_value(A['scenarios'][k]['N'],r=rr)) for k in A['scenarios'])
    rr=r+0.5*dr; sens[f'dep{dr*1e4:+.0f}bp_b05']=sum(A['scenarios'][k]['w']*vps(ri_value(A['scenarios'][k]['N'],r=rr)) for k in A['scenarios'])
sens['life_to_2030_T4']=sum(A['scenarios'][k]['w']*vps(ri_value(A['scenarios'][k]['N'],T=4,rho=0.5)) for k in A['scenarios'])
sens['rho_1.0']=sum(A['scenarios'][k]['w']*vps(ri_value(A['scenarios'][k]['N'],rho=1.0)) for k in A['scenarios'])
sens['rho_0']=sum(A['scenarios'][k]['w']*vps(ri_value(A['scenarios'][k]['N'],rho=0.0)) for k in A['scenarios'])
sens['r_12pct']=sum(A['scenarios'][k]['w']*vps(ri_value(A['scenarios'][k]['N'],r=0.12)) for k in A['scenarios'])
out['sens']=sens
# two bases
N_short=75.2  # trung vi TTM 3 nam: TTM Q3/24 312,9; Q3/25 30,1; Q3/26 75,2
roe=N_short/B; reinv=0.0  # g=0
out['V_ngan']=vps(N_short*(1-reinv)/r)
fcfe={'2024':289.572-276.057+13.901+(155.0-97.66),'2025':169.881-359.238+3.29+(310.414-80.718)}
out['fcfe']=fcfe; fc=st.mean(fcfe.values())
out['V_dai']=vps(fc/r)
out['D']=abs(math.log(out['V_ngan']/out['V_dai']))
cfo3=(252.9+289.572+169.881)/3; capex3=(160.9+276.057+359.238)/3; dep2=(336.234+177.148)/2
rev3=(7868+9448.094+8498.624)/3
out['C4_flow']=cfo3-min(capex3,dep2); out['D2_flow']=cfo3-0.0483*rev3
# liquidity
px=[row for row in csv.DictReader(open('px_cst.csv'))]
P=[float(x['Close']) for x in px]; V=[float(x['Price'])*float(x['Volume'])/1e9 for x in px]
rets=[math.log(P[i]/P[i-1]) for i in range(1,len(P))][-250:]
sig=st.pstdev(rets); adv250=st.median(V[-250:]); adv60=st.median(V[-60:])
vol60=st.median([float(x['Volume']) for x in px[-60:]])
liq={}
for q in A['liquidity']['sizes_bn']:
    ck=sig*math.sqrt(q/adv250); ck60=sig*math.sqrt(q/adv60)
    liq[q]=dict(ck250=ck,ck60=ck60,center_post=center*(1-ck60),bear_post=out['bear']*(1-ck60),bull_post=out['bull']*(1-ck60),
      sess10_250=q/(0.10*adv250),sess20_250=q/(0.20*adv250),sess10_60=q/(0.10*adv60),sess20_60=q/(0.20*adv60))
out['liq']=dict(sigma_d=sig,adv250_bn=adv250,adv60_bn=adv60,med_vol60=vol60,by_size=liq)
out['pb_price']=A['price']/vps(B); out['pe_ttm_price']=A['price']*A['shares']/1e9/75.23
out['pb_center']=center/vps(B)
print(json.dumps(out,indent=1,default=lambda x:round(x,4)))
json.dump(out,open('model_out.json','w'),indent=1)
