"""Mô hình định giá PAT — chạy SAU khoá (lock.txt). Tham số lấy nguyên văn assumptions_objective.md."""
import math, json
SH=25.0            # triệu cp
NET_CASH=1.246+558.069-67.218-76.690   # #2
REV9M=1366.520; REV_BASE=REV9M*4/3      # 1.822
DV_Q3=0.2413*0.98; REST_Q3=0.0620       # Q3/26 tỷ lệ, điện -2%
NVL_NEAR=0.5520+0.0025                  # Q3/26 + cốc Q3->T11
NVL_LR=0.4864+0.0283                    # H1/26 + cốc H1->hiện tại
NVL_FAV=0.4660+0.0310                   # FY25 + cốc 2025->hiện tại
EXP_TAX_STEP=1-0.85/0.90
def sga(rev,s): return 0.0385*s*rev+6.3+5+17
def ebit(rev_base,s,nvl,price=1.0,vol=1.0,tax_step=True,transfer=0.0,dlc_share=None):
    f=1-s*EXP_TAX_STEP if tax_step else 1.0
    if dlc_share is not None: f*= (1-dlc_share*transfer)
    m=1/f/price
    rev=rev_base*f*price*vol
    gpm=1-(nvl*m+DV_Q3*m+REST_Q3*m/vol)
    return rev*gpm-sga(rev,s), rev, gpm
def value(r=0.135,g=0.02,s=0.35,nvl_near=NVL_NEAR,nvl_lr=NVL_LR,price27=1.0,price_lr=1.0,vol27=1.0,
          tax_step=True,ebit_lr_mult=1.0,nvl_lr_add=0.0,transfer=0.0,oneoff=0.0,detail=False):
    q4=53.844*0.95*0.94
    e27,_,_=ebit(REV_BASE,s,nvl_near,price27,vol27,tax_step,transfer,0.65 if transfer else None)
    elr,_,_=ebit(REV_BASE,s,nvl_lr+nvl_lr_add,price_lr,1.0,tax_step,transfer,0.65 if transfer else None)
    elr*=ebit_lr_mult
    flows=[(0.13,q4),(0.63,e27*0.95*0.94)]
    tax={2028:.05,2029:.05,2030:.05,2031:.10,2032:.10,2033:.20}
    for i,y in enumerate(range(2028,2034)):
        e=elr*(1+g)**i; flows.append((1.63+i,e*(1-tax[y])*0.94))
    e34=elr*(1+g)**6*(1-0.20)*0.94
    tv=e34/(r-g); t_tv=6.63
    pv=sum(cf/(1+r)**t for t,cf in flows); pv_tv=tv/(1+r)**t_tv
    eq=pv+pv_tv+NET_CASH+oneoff
    out=dict(per_share=eq/SH*1000, equity=eq, pv_flows=pv, pv_tv=pv_tv, net_cash=NET_CASH, ebit27=e27, ebit_lr=elr,
             tv_share=pv_tv/eq)
    return out if detail else out['per_share']
res={}
base=value(detail=True); res['base']=base
adv=value(nvl_lr=NVL_NEAR,vol27=0.90,price_lr=0.95,detail=True)
fav=value(s=0.135,nvl_lr=NVL_FAV,detail=True)
P={'adv':0.25,'base':0.50,'fav':0.25}
center=P['adv']*adv['per_share']+P['base']*base['per_share']+P['fav']*fav['per_share']
lo=value(nvl_lr_add=+0.0275); hi=value(nvl_lr_add=-0.0275)
res.update(adv=adv,fav=fav,center=center,band=[lo,hi])
for k in ('base','adv','fav'):
    d=res[k]; print(f"{k:5s} EBIT27 {d['ebit27']:6.1f} EBIT_LR {d['ebit_lr']:6.1f} PVflows {d['pv_flows']:6.1f} PV_TV {d['pv_tv']:6.1f} cash {d['net_cash']:5.1f} equity {d['equity']:7.1f} => {d['per_share']:8.0f} d/cp (TV {d['tv_share']:.0%})")
print(f"TAM (xac suat) {center:,.0f}  VUNG [{lo:,.0f} ; {hi:,.0f}]")
for k in ('base','adv','fav'):
    e,rv,gp=ebit(REV_BASE,0.35 if k!='fav' else 0.135,{'base':NVL_LR,'adv':NVL_NEAR,'fav':NVL_FAV}[k],0.95 if k=='adv' else 1.0)
    print(k,'LR rev %.0f gpm %.3f ebit %.1f'%(rv,gp,e))
print('base 2027 rev/gpm',[round(x,3) for x in ebit(REV_BASE,0.35,NVL_NEAR)])
# --- V_ngan / V_dai
roe=289.9/650; vs=289.9*0.94*(1-min(max(0.02/roe,0),0.8))/(0.135-0.02)/SH*1000
D=abs(math.log(vs/base['per_share'])); print(f"V_ngan {vs:,.0f}  V_dai {base['per_share']:,.0f}  D {D:.3f} (ln2=0.693)")
res['v_ngan']=vs; res['D']=D
# --- sensitivities (on base, and on center-weights where noted)
S={}
def wc(**kw):  # weighted center under a change applied to all 3 scenarios
    a=value(nvl_lr=NVL_NEAR,vol27=0.90,price_lr=0.95,**kw); b=value(**kw); f=value(s=kw.pop('s',0.135) if 's' in kw else 0.135,nvl_lr=NVL_FAV,**kw)
    return .25*a+.5*b+.25*f
for dep in (-1.0,-0.5,0.5,1.0):
    for beta in (0.5,1.0):
        r=0.135+beta*dep/100; S[f'dep{dep:+.1f}_b{beta}']=(r,value(r=r),wc(r=r))
for g in (0,0.01,0.02,0.03): S[f'g{g}']=(g,value(g=g),wc(g=g))
for m in (0.8,0.9,1.1,1.2): S[f'ebitLR_x{m}']=(m,value(ebit_lr_mult=m))
for a in (-0.0275,0.0275): S[f'nvlLR{a:+.4f}']=(a,value(nvl_lr_add=a))
for s in (0.135,0.35,0.85,1.0): S[f'export_share{s}']=(s,value(s=s))
S['exp_tax_stays_10']=(0,value(tax_step=False))
for p in (0.95,0.90): S[f'price_all_{p}']=(p,value(price27=p,price_lr=p))
S['vol27_-20']=(0.8,value(vol27=0.8))
S['transfer_DLC_-5pct']=(0.05,value(transfer=0.05))
S['oneoff_-50']=(-50,value(oneoff=-50)); S['pledge_-42.6']=(-42.6,value(oneoff=-42.6))
for k,v in S.items(): print(k, *[f'{x:,.4f}' if isinstance(x,float) and abs(x)<1 else f'{x:,.0f}' for x in v])
grid={}
for r in (0.125,0.13,0.135,0.14,0.145):
    grid[r]={g:round(value(r=r,g=g)) for g in (0,0.01,0.02,0.03)}
print('grid r x g (base)'); [print(r,grid[r]) for r in grid]
# liquidity
adv_sh=9300
for part in (0.05,0.10,0.20):
    per=adv_sh*part; print(f'part {part:.0%}: {per:,.0f} cp/phien', {n:(round(n/per,1), f"{0.135*(n/per/250)/2:.1%}") for n in (10000,50000,100000,250000)})
json.dump({k:(v if not isinstance(v,dict) else {kk:vv for kk,vv in v.items()}) for k,v in res.items()},open('model_out.json','w'),indent=1,default=float)
json.dump({k:list(v) for k,v in S.items()},open('sens_out.json','w'),indent=1)
