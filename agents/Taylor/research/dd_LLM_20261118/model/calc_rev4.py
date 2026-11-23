import json, os, math, statistics as st
H=os.path.dirname(os.path.abspath(__file__))
M=json.load(open(os.path.join(H,'model_rev4_inputs.json')))
S=M['shares_m']; r0=M['r_ke']; B=M['bs_q3_bn']; W=M['warranty']; w=M['weights']; L=M['liquidity_discount']
nc=B['cash_TM3']+B['htm_st_net_TM4']+B['htm_lt_TM4']-B['borrow_st']-B['borrow_lt']
nwc=sum(B['op_assets'].values())-sum(B['op_liabs'].values()); nfp=nc+nwc
wb=W['close_st']+W['close_lt']
util=W['open_st']+W['open_lt']+W['new_9m26']-W['reversal_selling_9m26']-W['reversal_other_inc_9m26']-wb
print(f'NFP={nfp:.2f} (net cash {nc:.2f}, NWC {nwc:.2f}); warranty close={wb:.3f}; 9T26 utilised(cash)={util:.2f}; share={util/(util+W["reversal_selling_9m26"]+W["reversal_other_inc_9m26"]):.3%}')
WF=M['welfare']; wf_stock=WF['pct_npat']*WF['npat_parent_9m26_unappropriated']
def nopat(k,rev=None,gpm=None,cs=None,fa=None):
    if k=='bad': return M['nopat_bad']
    R=rev if rev is not None else (M['rev_base'] if k=='base' else M['rev_good'])
    g=gpm if gpm is not None else M['gpm'][k]; c=W['cash_share'][k] if cs is None else cs
    pre=R*g-M['opex_ga'][k]+W['flow_noncash_addback_pct_rev'][k]*R*(1 if fa is None else fa/W['flow_noncash_addback_pct_rev'][k] if W['flow_noncash_addback_pct_rev'][k] else 0)
    n=0.8*pre; return n*(1-WF['pct_npat']) if n>0 else n
def val(k,r=r0,cs=None,rev=None,gpm=None,hna=None,wf=True,hamon=None,extra=0.0,iv=None,fa=None):
    c=W['cash_share'][k] if cs is None else cs
    addw=wb*(1-c)*(1-W['tax_on_reversal'])
    hm=(M['hamon']['after_tax_if_recognised'] if k=='good' else 0) if hamon is None else hamon
    imp=M['bad_impairment'] if k=='bad' else 0
    f=M['trapped'][k]
    v=nopat(k,rev,gpm,c,fa)/r+(nfp+addw-(wf_stock if (wf and k!='bad') else 0))*f-imp+(M['lt_fin_invest_book'] if iv is None else iv)+(M['hna_after_tax'] if hna is None else hna)+hm-extra
    return v/S*1000
def ctr(LL=L,ww=None,**kw):
    ww=ww or w; return sum(ww[k]*val(k,**kw) for k in ww)*(1-LL)
sv={k:val(k) for k in w}; C=ctr()
print('NOPAT',{k:round(nopat(k),1) for k in w},' welfare pending',round(wf_stock,1))
print('scen pre-liq',{k:round(v) for k,v in sv.items()},' post-liq',{k:round(v*(1-L)) for k,v in sv.items()})
print(f'TAM pre={C/(1-L):.0f} post={C:.0f} zone_post=[{sv["bad"]*(1-L):.0f};{sv["good"]*(1-L):.0f}] 0.85xtam={0.85*C:.0f}')
print('-- warranty cash share (ca 3 kich ban dung cung muc):')
for c in (0.009,0.10,0.25,0.5,0.75,1.0): print(f'   cash {c:.1%}: tam={sum(w[k]*val(k,cs=c) for k in w)*(1-L):.0f}')
print('-- doanh thu base (chi kich ban co so):',{R:round(sum(w[k]*val(k,rev=(R if k=='base' else None)) for k in w)*(1-L)) for R in (3378,3400,4150,4500,5433)})
print('-- GPM base:',{g:round(sum(w[k]*val(k,gpm=(g if k=="base" else None)) for k in w)*(1-L)) for g in (0.03,0.04,0.045,0.05,0.06,0.07)})
print('-- r beta1:',{d:f'{ctr(r=r0+d/1e4):.0f} ({ctr(r=r0+d/1e4)/C-1:+.1%})' for d in (-100,-50,50,100)})
print('-- r beta0.5:',{d:f'{ctr(r=r0+d/1e4*0.5):.0f}' for d in (-100,-50,50,100)})
print('-- Ke band 12.3/13.4:',{rr:round(ctr(r=rr)) for rr in (0.123,0.134)})
print('-- liquidity:',{LL:round(ctr(LL=LL)) for LL in (0,0.05,0.1,0.2)})
print('-- HNA=0:',round(ctr(hna=0)),' Hamon base ghi nhan:',round(sum(w[k]*val(k,hamon=M['hamon']['after_tax_if_recognised']) for k in w)*(1-L)),' Hamon tot=0:',round(sum(w[k]*val(k,hamon=0) for k in w)*(1-L)))
G=M['sens']['guarantee_6901_overdue_debt']
for frac in (0.25,0.5,1.0): print(f'-- bao lanh 69-1 (neu co) {frac:.0%} x {G}: tam={ctr(extra=frac*G):.0f}')
print('-- welfare off:',round(ctr(wf=False)))
print('-- flow add-back bao hanh (% DT, co so+tot):',{a:round(sum(w[k]*val(k,fa=(a if k!='bad' else None)) for k in w)*(1-L)) for a in (0.0,0.01,0.0168,0.03)})
w25={'bad':0.25,'base':0.5,'good':0.25}; print('-- trong so 25/50/25 (rev3):',round(ctr(ww=w25)))
SQ=M['sens']; print('-- ngoai tru: xoa con',SQ['qualified_subs'],'=>',round(ctr(extra=SQ['qualified_subs'])),'; + lien ket ve 0 =>',round(ctr(extra=SQ['qualified_subs']+SQ['qualified_assoc'])),'; chi lien ket 50% =>',round(ctr(extra=0.5*SQ['qualified_assoc'])))
print('-- CPH (uoc luong khung):',{x:round(ctr(extra=x)) for x in SQ['cph_bracket']})
print('-- trong so:',{str(x):round(ctr(ww=x)) for x in ({'bad':0.4,'base':0.45,'good':0.15},{'bad':0.5,'base':0.4,'good':0.1},{'bad':0.1,'base':0.5,'good':0.4},{'bad':0,'base':1,'good':0})})
ns=M['sens']['capraise_new_shares_m']; px=M['sens']['capraise_price']
Vtot=C*S/1000; print(f'-- tang von {ns}tr cp @ {px}: tam/cp={(Vtot+ns*px/1000*(1-L))/(S+ns)*1000:.0f}; phat hanh dung bang tam => khong doi (NPV=0, V4)')
print(f'-- sau co tuc CP 31,7%: tam/1,317={C/1.317:.0f} vung=[{sv["bad"]*(1-L)/1.317:.0f};{sv["good"]*(1-L)/1.317:.0f}]')
# V6 hien thi (giu cong thuc rev2)
A=json.load(open(os.path.join(H,'assumptions_LLM_20261118.json')))
q=A['np_parent_quarterly_bn']; ks=sorted(q); ttm={ks[i]:sum(q[k] for k in ks[i-3:i+1]) for i in range(3,len(ks))}
npn=st.median([ttm[k] for k in ttm if '2023Q4'<=k<='2026Q3']); vs=npn/(r0)/S*1000
cq=A['cfo_q_bn']; xq=A['capex_q_bn']; cfo=sum(cq.values())/3; capex=sum(xq.values())/3; vl=(cfo-capex)/r0/S*1000
wc=A['wc_oneoff_9m26']; ex=wc['cust_adv_new']+wc['inventory_release']; vl2=((sum(cq.values())-ex)/3-capex)/r0/S*1000
print(f'V6: V_ngan={vs:.0f} V_dai={vl:.0f} D={abs(math.log(vs/vl)):.2f}; V_dai bo tam ung+ton kho={vl2:.0f} D={abs(math.log(vs/vl2)):.2f} (ln2=0.69 ln3=1.10)')
json.dump({'nfp':round(nfp,2),'warranty_util_9m26':round(util,2),'scen_post':{k:round(v*(1-L)) for k,v in sv.items()},'center_post':round(C),'center_pre':round(C/(1-L)),'zone':[round(sv['bad']*(1-L)),round(sv['good']*(1-L))]},open(os.path.join(H,'calc_rev4_out.json'),'w'))
