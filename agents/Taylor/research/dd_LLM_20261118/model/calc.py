import json, math, statistics as st, os
A=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'assumptions_LLM_20261118.json')))
S=A['shares_m']; E=A['equity_parent_q3']; r0=A['r_ke']; g=A['g']; w=A['weights']; L=A['liquidity_discount']; sc=A['scenario_roe']; H=A['hna_hidden_gain_after_tax_bn']; P=A['price_today']
def val(roe, r=r0, gg=g, h=H): return (E*(roe-gg)/(r-gg)+h)/S*1000
def ctr(r=r0,gg=g,h=H,d=0): return sum(w[k]*val(sc[k]+d,r,gg,h) for k in w)
vals={k:val(v) for k,v in sc.items()}; c=ctr()
print(f'BVPS_parent={E/S*1000:.0f}  P/B_parent={P/(E/S*1000):.2f}')
print('scen pre-liq', {k:round(v) for k,v in vals.items()}, ' HNA d/cp', round(H/S*1000))
print(f'center_pre={c:.0f} center_post={c*(1-L):.0f} zone_post=[{vals["bad"]*(1-L):.0f};{vals["good"]*(1-L):.0f}] 0.85xtam={0.85*c*(1-L):.0f} gia/tam={P/(c*(1-L)):.2f}')
for d in (-100,-50,50,100):
    for b in (1.0,0.5):
        r=r0+d/1e4*b; cc=ctr(r)*(1-L); print(f'dep {d:+d}bp beta{b}: r={r:.4f} center={cc:.0f} ({cc/(c*(1-L))-1:+.1%})')
for LL in (0,0.05,0.10,0.20): print(f'liq {LL}: {c*(1-LL):.0f}')
for gg in (0,0.02,0.04): print(f'g={gg}: {ctr(gg=gg)*(1-L):.0f}')
for dd in (-0.02,0.02,0.05): print(f'ROE all {dd:+.2f}: {ctr(d=dd)*(1-L):.0f}')
print(f'HNA=0: {ctr(h=0)*(1-L):.0f}')
for rr in (0.12,0.15): print(f'r={rr}: {ctr(rr)*(1-L):.0f}')
lo,hi=-0.1,1.0
for _ in range(60):
    m=(lo+hi)/2; lo,hi=(m,hi) if val(m)*(1-L)<P else (lo,m)
print(f'implied ROE at price {P} (post-liq): {m:.4f}; pre-liq:', end=' ')
lo,hi=-0.1,1.0
for _ in range(60):
    m=(lo+hi)/2; lo,hi=(m,hi) if val(m)<P else (lo,m)
print(f'{m:.4f}')
print(f'post stock-div 31.7% equiv: center_post/1.317={c*(1-L)/1.317:.0f}, price/1.317={P/1.317:.0f}')
q=A['np_parent_quarterly_bn']; ks=sorted(q); ttm={ks[i]:sum(q[k] for k in ks[i-3:i+1]) for i in range(3,len(ks))}
win=[k for k in ttm if '2023Q4'<=k<='2026Q3']; npn=st.median([ttm[k] for k in win])
print('TTM', {k:round(ttm[k],1) for k in win})
roe=npn/E; reinv=min(max(g/roe,0),0.8) if roe>0 else 0; vs=npn*(1-reinv)/(r0-g)/S*1000
cq=A['cfo_q_bn']; xq=A['capex_q_bn']; cfo=sum(cq.values())/3; capex=sum(xq.values())/3; fcfe=cfo-capex
vl=fcfe*(1+g)/(r0-g)/S*1000; c4=cfo-min(capex,A['da_annual_bn']); vc4=c4*(1+g)/(r0-g)/S*1000
d2=cfo-A['industry_capex_rev_median']*A['rev_ttm_bn']; vd2=d2*(1+g)/(r0-g)/S*1000
print(f'NP_norm(median TTM 12q)={npn:.1f} ROE={roe:.4f} V_short={vs:.0f}')
print(f'CFO/yr={cfo:.1f} capex/yr={capex:.1f} capex/CFO={capex/cfo:.3f} FCFE/yr={fcfe:.1f} V_long={vl:.0f}')
print(f'C4/yr={c4:.1f} V_C4={vc4:.0f} | D2/yr={d2:.1f} V_D2={vd2:.0f}')
D=abs(math.log(vs/vl)); print(f'D=|ln(Vs/Vl)|={D:.2f} (ln2={math.log(2):.2f}, ln3={math.log(3):.2f})')
one=sum(A['one_offs_9m2026_pbt'].values()); core=A['pbt_9m2026']-one
print(f'9M one-offs PBT={one:.1f}; core PBT={core:.1f}; core NPAT~{core*0.8:.0f} (thue 20%); nam hoa {core*0.8*4/3:.0f} => ROE {core*0.8*4/3/E:.3f} (van gom bien gop quyet toan 31%)')
# ---- [v1] SOTP tron RI (giu de doi chieu; nopat tu assumptions rev2) ----
B=A['bs_q3_bn']; nc=B['cash_TM3']+B['htm_st_net_TM4']+B['htm_lt_TM4']-B['borrow_st']-B['borrow_lt']
nwc=sum(B['op_assets'].values())-sum(B['op_liabs'].values()); nfp=nc+nwc
print(f'\nSOTP: tien+tien gui={B["cash_TM3"]+B["htm_st_net_TM4"]+B["htm_lt_TM4"]:.1f} net cash={nc:.1f} NWC van hanh={nwc:.1f} => vi the TC rong sau no van hanh={nfp:.1f} ({nfp/S*1000:.0f} d/cp); tam ung khach={B["op_liabs"]["cust_adv"]:.1f}')
T=A['sotp']; inv=B['lt_fin_invest_book']
def sotp(k,r=r0,h=H,nf=nfp):
    imp=T['bad_impairment'] if k=='bad' else 0
    return (T['nopat'][k]/r+nf-imp+inv+h)/S*1000
sv={k:sotp(k) for k in ('bad','base','good')}
print('SOTP per scen pre-liq',{k:round(v) for k,v in sv.items()})
mix={'bad':vals['bad'],'base':sv['base'],'good':sv['good']}
cm=sum(w[k]*mix[k] for k in w)
print('[v1-cau truc tron RI/SOTP, nopat rev2] (xau=RI tien mac ket; co so/tot=SOTP) pre-liq',{k:round(v) for k,v in mix.items()})
print(f'TAM pre={cm:.0f} post={cm*(1-L):.0f} vung_post=[{mix["bad"]*(1-L):.0f};{mix["good"]*(1-L):.0f}] 0.85xtam={0.85*cm*(1-L):.0f} gia/tam={P/(cm*(1-L)):.2f}')
def cm_f(r=r0,LL=L,nf=nfp,h=H,wb=None):
    ww=wb or w; m={'bad':val(sc['bad'],r,g,h),'base':sotp('base',r,h,nf),'good':sotp('good',r,h,nf)}
    return sum(ww[k]*m[k] for k in ww)*(1-LL)
base_c=cm_f()
for d in (-100,-50,50,100):
    for b in (1.0,0.5):
        rr=r0+d/1e4*b; x=cm_f(rr); print(f'[chinh] dep {d:+d}bp beta{b}: {x:.0f} ({x/base_c-1:+.1%})')
for LL in (0,0.05,0.10,0.20): print(f'[chinh] liq {LL}: {cm_f(LL=LL):.0f}')
for hc in (0,0.25,0.5): print(f'[chinh] cat {hc:.0%} vi the TC rong (tien mac ket mot phan): {cm_f(nf=nfp*(1-hc)):.0f}')
print(f'[chinh] HNA=0: {cm_f(h=0):.0f}')
for wb in ({'bad':0.5,'base':0.4,'good':0.1},{'bad':0.1,'base':0.5,'good':0.4}): print(f'[chinh] trong so {wb}: {cm_f(wb=wb):.0f}')
print(f'[chinh] sau co tuc CP 31,7%: tam/1,317={base_c/1.317:.0f} gia/1,317={P/1.317:.0f}')
print(f'[v1-doi chieu] RI ca 3 kich ban (tien mac ket moi kich ban) post-liq={c*(1-L):.0f}')

# ================= REV2 (skeptic r1): SOTP xuyen suot 3 kich ban, bien goc neo trung vi =================
print('\n===== REV2 =====')
def nop(m,k='base'):
    R=T['rev']['base' if k=='base' else 'good']; o=sum(T['opex']['base' if k=='base' else 'good']); return 0.8*(R*m-o)
TF=T['trapped_cash_factor']
def s2(k,r=r0,h=H,nf=nfp,iv=inv,mb=None,mg=None,f=None):
    n={'bad':T['nopat']['bad'],'base':nop(mb if mb is not None else T['margin']['base'],'base'),'good':nop(mg if mg is not None else T['margin']['good'],'good')}[k]
    ff=TF[k] if f is None else f
    imp=T['bad_impairment'] if k=='bad' else 0
    return (n/r+nf*ff-imp+iv+h)/S*1000
def c2(LL=L,ww=None,**kw):
    ww=ww or w; return sum(ww[k]*s2(k,**kw) for k in ww)*(1-LL)
sv2={k:s2(k) for k in ('bad','base','good')}
print('NOPAT', {k:round(T['nopat'][k],1) for k in T['nopat']}, ' margin base/good', T['margin']['base'], T['margin']['good'], ' trapped f', TF)
print('SOTP2 per scen pre-liq',{k:round(v) for k,v in sv2.items()},' post-liq',{k:round(v*(1-L)) for k,v in sv2.items()})
C2=c2(); print(f'TAM2 pre={C2/(1-L):.0f} post={C2:.0f} vung_post=[{sv2["bad"]*(1-L):.0f};{sv2["good"]*(1-L):.0f}] 0.85xtam={0.85*C2:.0f} gia/tam={P/C2:.2f}')
print('-- do nhay bien gop co so (tot giu 7%):')
for m in (0.04,0.045,0.05,0.06,0.07): x=c2(mb=m); print(f'  base GPM {m:.1%}: tam={x:.0f} gia/tam={P/x:.2f}')
print('-- do nhay bien gop co so khi tot = co so + 3pp:')
for m in (0.04,0.045,0.05,0.06,0.07): x=c2(mb=m,mg=m+0.03); print(f'  base {m:.1%}/good {m+0.03:.1%}: tam={x:.0f} gia/tam={P/x:.2f}')
print(f'  breakeven: GPM co so de tam=gia (tot 7%):', end=' ')
lo,hi=0.0,0.3
for _ in range(60):
    mm=(lo+hi)/2; lo,hi=(mm,hi) if c2(mb=mm)<P else (lo,mm)
print(f'{mm:.4f}')
print('-- trong so:')
for wb in ({'bad':0.25,'base':0.5,'good':0.25},{'bad':0.4,'base':0.45,'good':0.15},{'bad':0.5,'base':0.4,'good':0.1},{'bad':0.1,'base':0.5,'good':0.4},{'bad':0.0,'base':1.0,'good':0.0}):
    x=c2(ww=wb); print(f'  {wb}: {x:.0f} gia/tam={P/x:.2f}')
print('-- lai huy dong (beta 1):')
for d in (-100,-50,50,100): x=c2(r=r0+d/1e4); print(f'  {d:+d}bp: {x:.0f} ({x/C2-1:+.1%})')
print('-- thanh khoan:', {LL:round(c2(LL=LL)) for LL in (0,0.05,0.1,0.2)})
print(f'-- HNA=0: {c2(h=0):.0f}')
print('-- tien mac ket o kich ban co so (f co so):', {f:round(sum(w[k]*s2(k,f=(f if k!="bad" else None)) for k in w)*(1-L)) for f in (1.0,0.75,0.5)})
# ngoai tru soat xet AASC (WARNING/do nhay, khong vao base)
Q=A['qualified_items_bn']; qx=Q['sub_overdue_recv']+Q['sub_wip']+Q['cokhi_capitalised_interest']+Q['bhxh_late_interest']
print(f'-- ngoai tru: xoa 100% khoan muc cong ty con bi ngoai tru {qx:.1f} ty: {c2(nf=nfp-qx):.0f}; + lien ket 328,2 ve 0: {c2(nf=nfp-qx,iv=inv-Q["assoc_book_total"]):.0f}; chi lien ket ve 50%: {c2(iv=inv-0.5*Q["assoc_book_total"]):.0f}')
# BCTC rieng
SP=A['separate_q3']; ncs=SP['cash']+SP['htm_st_net']-SP['borrow_st']-SP['borrow_lt']; nws=sum(SP['op_assets'].values())-sum(SP['op_liabs'].values()); nfs=ncs+nws
print(f'-- BCTC RIENG: net cash={ncs:.1f} NWC={nws:.1f} NFP={nfs:.1f} (HN {nfp:.1f}, chenh {nfs-nfp:+.1f}); DT TC dai han rieng {SP["lt_fin_invest_book"]:.1f} (HN {inv:.1f}); tam theo rieng={c2(nf=nfs,iv=SP["lt_fin_invest_book"]):.0f} (HN {C2:.0f})')
print(f'-- sau co tuc CP 31,7%: tam/1,317={C2/1.317:.0f} gia/1,317={P/1.317:.0f}')
print(f'-- [doi chieu phuong phap] RI ca 3 kich ban (tien mac ket moi kich ban) post-liq={c*(1-L):.0f}; v1 tron RI/SOTP=31589')
# D luong hoa (dinh chinh 9)
cf3=sum(cq.values()); print(f'\nD: CFO 12q (BQ) tong={cf3:.1f}, TB/nam={cf3/3:.1f}')
wc=A['wc_oneoff_9m26']; ex=wc['cust_adv_new']+wc['inventory_release']
def vl_f(tot): return (tot/3-capex)*(1+g)/(r0-g)/S*1000
for lab,tot in [('goc',cf3),('bo tam ung 657,8 + ton kho 440,9',cf3-ex),('them bo Q3/24 + Q2/25',cf3-ex-sum(A['cfo_unexplained_q'].values()))]:
    v=vl_f(tot); print(f'  V_dai {lab}: CFO/nam={tot/3:.1f} V={v:.0f} D='+(f'{abs(math.log(vs/v)):.2f}' if v>0 else 'n/a (V<=0)'))
cfb=cf3-sum(cq[k] for k in ('2026Q1','2026Q2','2026Q3'))+A['cfo_9m26_bctc']; v=vl_f(cfb-ex); print(f'  (CFO 9T/26 theo BCTC 1.231,3 thay BQ) bo tam ung+ton kho: V={v:.0f} D={abs(math.log(vs/v)):.2f}')
