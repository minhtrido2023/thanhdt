import json, math, statistics as st, os
A=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'assumptions_POW_20261118_rev2.json')))
S=A['shares_m']; E=A['equity_parent_q3']; EN=A['e_nt34_book_estimate']; NEW=A['e_new_projects_book']; Eo=E-EN-NEW
r0=A['r_ke']; g=A['g']; w=A['weights']; L=A['liquidity_discount']; sc=A['scenario_roe_legacy']
def val(roe, r=r0, gg=g, en=EN, new=NEW):
    return ((E-en-new)*(roe-gg)/(r-gg)+en+new)/S*1000
vals={k:val(v) for k,v in sc.items()}; c=sum(w[k]*vals[k] for k in w)
print(f'BVPS_parent={E/S*1000:.0f} E_old={Eo:.0f}')
print('scen', {k:round(v) for k,v in vals.items()})
print(f'center_pre={c:.0f} center_post={c*(1-L):.0f} zone_post=[{vals["bad"]*(1-L):.0f};{vals["good"]*(1-L):.0f}] PB_center={c*(1-L)/(E/S*1000):.2f}')
for d in (-100,-50,50,100):
    for b in (1.0,0.5):
        r=r0+d/1e4*b; cc=sum(w[k]*val(sc[k],r=r) for k in w)*(1-L); print(f'dep {d:+d}bp beta{b}: r={r:.4f} center={cc:.0f} ({cc/(c*(1-L))-1:+.1%})')
for gg in (-0.02,0,0.01,0.02,0.03,0.04): print(f'g={gg}: {sum(w[k]*val(sc[k],gg=gg) for k in w)*(1-L):.0f}')
for en in (7000,8000,9000,10000): print(f'E_NT34={en}: {sum(w[k]*val(sc[k],en=en) for k in w)*(1-L):.0f}')
for rr in (0.11,0.12): print(f'r={rr} (beta utility thap, chi do nhay): {sum(w[k]*val(sc[k],r=rr) for k in w)*(1-L):.0f}')
for LL in (0,0.01,0.03): print(f'liq {LL}: {c*(1-LL):.0f}')
for nw in (0,1660,2740,5000): print(f'E_new_book={nw}: {sum(w[k]*val(sc[k],new=nw) for k in w)*(1-L):.0f}')
print(f'r=0.11 + g0 + new5000 + NT34 10000: {sum(w[k]*val(sc[k],r=0.11,new=5000,en=10000) for k in w)*(1-L):.0f}')
for dd in (-0.02,0.02): print(f'ROE all scen {dd:+.2f}: {sum(w[k]*val(sc[k]+dd) for k in w)*(1-L):.0f}')
print('VA1 FX remaining upside d/cp:', round(490*(1-0.109)/S*1000))
# moat sensitivity: WIDE would mean ROE_old held at good (11.5%) as base
print(f'kich ban tot (ROE di san 11,5%, KHONG phai gia dinh moat) center={val(0.115)*(1-L):.0f}; kich ban xau (4,5%) {val(0.045)*(1-L):.0f}')
# implied ROE_old at price
P=13250
lo,hi=0.0,0.5
for _ in range(60):
    m=(lo+hi)/2; lo,hi=(m,hi) if val(m)*(1-L)<P else (lo,m)
print(f'implied ROE_old at price {P}: {m:.4f}')
# two bases
q=A['np_parent_quarterly_bn']; ks=sorted(q); ttm={ks[i]:sum(q[k] for k in ks[i-3:i+1]) for i in range(3,len(ks))}
win=[k for k in ttm if '2023Q4'<=k<='2026Q3']; npn=st.median([ttm[k] for k in win])
print('TTM', {k:round(ttm[k]) for k in win})
roe=npn/E; reinv=min(max(g/roe,0),0.8); vs=npn*(1-reinv)/(r0-g)/S*1000
cfo=sum(A['cfo_window_bn'].values())/3; capex=sum(A['capex_window_bn'].values())/3; fcfe=cfo-capex
vl=fcfe*(1+g)/(r0-g)/S*1000
da=A['da_window_bn_estimate']/3; c4=cfo-min(capex,da); vc4=c4*(1+g)/(r0-g)/S*1000
d2=cfo-A['industry_capex_rev_median']*A['rev_ttm_bn']; vd2=d2*(1+g)/(r0-g)/S*1000
print(f'NP_norm={npn:.0f} ROE={roe:.4f} reinv={reinv:.3f} V_short={vs:.0f}')
print(f'CFO/yr={cfo:.0f} capex/yr={capex:.0f} capex/CFO={capex/cfo:.2f} FCFE/yr={fcfe:.0f} V_long={vl:.0f} (FCFE<=0 => chi V_ngan)')
print(f'C4/yr={c4:.0f} V_C4={vc4:.0f} | D2/yr={d2:.0f} V_D2={vd2:.0f}')
D=abs(math.log(vs/vd2)); print(f'D(V_short vs V_D2, chi tham khao)={D:.2f}')
# core earnings 9M2026
pbt=7743.503; one=sum(A['one_offs_9m2026_pbt'].values()); tax=(768.090+76.846)/pbt
core_np=(pbt-one)*(1-tax); par=6434.493/6898.566
lo_one=sum(A['one_offs_9m2026_pbt'].values())-A['one_offs_9m2026_pbt']['Q3_CaMau_OM_receivable_provision_reversal_est']+A['one_offs_9m2026_pbt_range_Q3']['low']
for lab,o in (('Q3 hoan nhap 280',one),('Q3 hoan nhap 187,1',lo_one)): print(f'{lab}: one-offs PBT={o:.1f} core PBT={pbt-o:.0f} taxrate={tax:.3f} core parent = 6434.5 - one*(1-t) = {6434.493-o*(1-tax):.0f} (mot lan nam o cap me => 100% thuoc me, khong nhan 93,3%)')
print(f'(r1 sai: core NPAT HN {core_np:.0f} x 93,3% = {core_np*par:.0f})')
cp=6434.493-one*(1-tax); print(f'P/E core: EPS annualised {cp*4/3/S*1000:.0f} => {13250/(cp*4/3/S*1000):.1f}x')
