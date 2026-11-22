"""PAT r2 — chạy SAU khoá lock_r2.txt. Bản sao sửa từ calc/model.py; tham số nguyên văn assumptions_objective_r2.md."""
import math, json, itertools
SH=25.0
NET_CASH0=1.246+558.069-67.218-76.690          # 415,407 (#2)
LOCKED70=70-70*0.060*0.80/0.135                 # §1-3a: 45,0
KTPL9T=0.06*215.713                             # §1-3d
NET_CASH=NET_CASH0-LOCKED70-KTPL9T
REV_BASE=1366.520*4/3
DV=0.2508; ELEC=0.98*(1+0.30*0.035+0.25*0.06-0.10*0.02); REST=0.0582
K=1.37/1.13*3857/100e6                          # tỷ trọng cốc / CNY
def nvl(base,c_from,c_to): return base+K*(c_to-c_from)
G2_27=nvl(0.5520,2040,2108); G1_27=nvl(0.4864,1541,2108)
LR={'O1':nvl(0.4660,1491,1825),'O2':nvl(0.4864,1541,1825),'O3':nvl(0.5520,2040,1825)}
STEP=1-0.85/0.90
def sga(rev,s_exp): return 0.0385*s_exp*rev+6.3+5+17
def ebit(nvl_r,f,p,s_exp,vol=1.0,elec=ELEC):
    m=1/(f*p); rev=REV_BASE*f*p*vol
    gpm=1-(nvl_r+DV*elec+REST/vol)*m
    return rev*gpm-sga(rev,s_exp), rev, gpm
def value(nvl27,nvlLR,f=1-STEP,p=1.0,s_exp=0.35,r=0.135,g=0.02,lr_mult=1.0,oneoff=0.0,cash=None,elec=ELEC,detail=False,transfer=0.0):
    ff=f*(1-0.65*transfer)
    e27,_,_=ebit(nvl27,ff,p,s_exp,elec=elec)
    elr,rv,gp=ebit(nvlLR,ff,p,s_exp,elec=elec); elr*=lr_mult
    flows=[(0.13,53.844*0.95*0.94),(0.63,e27*0.95*0.94)]
    tax={2028:.05,2029:.05,2030:.05,2031:.10,2032:.10,2033:.20}
    for i,y in enumerate(range(2028,2034)): flows.append((1.63+i,elr*(1+g)**i*(1-tax[y])*0.94))
    tv=elr*(1+g)**6*0.8*0.94/(r-g)
    pv=sum(cf/(1+r)**t for t,cf in flows); pvtv=tv/(1+r)**6.63
    nc=NET_CASH if cash is None else cash
    eq=pv+pvtv+nc+oneoff
    d=dict(per_share=eq/SH*1000,equity=eq,pv_flows=pv,pv_tv=pvtv,net_cash=nc,ebit27=e27,ebit_lr=elr,rev_lr=rv,gpm_lr=gp,tv_share=pvtv/eq)
    return d if detail else d['per_share']
# ---- tree
PO={'O1':0.1375,'O2':0.3875,'O3':0.475}
PP={0.937:0.32,1.0:0.58,1.063:0.10}
PT={'Ta':(1.0,0.35,0.65),'Tb':(0.35,0.35,0.25),'Tc':(0.135,0.135,0.10)}
PX={15:0.90,10:0.10}
def n27(o): return 0.5*G2_27+0.5*(G1_27 if o in('O1','O2') else G2_27)
leaves=[]
for o,(p,pp),(t,(s,sx,pt)),(x,px) in itertools.product(PO,PP.items(),PT.items(),PX.items()):
    f=1-s*STEP if x==15 else 1.0
    v=value(n27(o),LR[o],f,p,sx); leaves.append((PO[o]*pp*pt*px,v,o,p,t,x))
tot=sum(l[0] for l in leaves); center=sum(l[0]*l[1] for l in leaves)
def wq(q):
    acc=0
    for w,v,*_ in sorted(leaves,key=lambda z:z[1]):
        acc+=w
        if acc>=q: return v
band=(wq(.25),wq(.75)); band90=(wq(.10),wq(.90))
# base: expected inputs
EN27=sum(PO[o]*n27(o) for o in PO); ENLR=sum(PO[o]*LR[o] for o in PO)
EP=sum(k*v for k,v in PP.items())
Ef=PX[15]*sum(pt*(1-s*STEP) for s,sx,pt in PT.values())+PX[10]
Esx=sum(pt*sx for s,sx,pt in PT.values())
base=value(EN27,ENLR,Ef,EP,Esx,detail=True)
print(f"NET_CASH {NET_CASH:.2f} (locked70 {LOCKED70:.2f}, ktpl {KTPL9T:.2f}) ELEC {ELEC:.4f} K {K:.3e}")
print('NVL',{'G2_27':round(G2_27,4),'G1_27':round(G1_27,4),**{k:round(v,4) for k,v in LR.items()}},'E27',round(EN27,4),'ELR',round(ENLR,4),'EP',round(EP,4),'Ef',round(Ef,4),'Esx',round(Esx,4))
print(f"sum p {tot:.4f}  TAM {center:,.0f}  VUNG P25-P75 [{band[0]:,.0f}; {band[1]:,.0f}]  P10-P90 [{band90[0]:,.0f}; {band90[1]:,.0f}]")
print("CO SO (inputs ky vong):",{k:round(v,3) for k,v in base.items()})
# marginal by node
for name,idx,keys in (('O',2,PO),('P',3,PP),('T',4,PT),('TX',5,PX)):
    out={}
    for k in keys:
        sel=[l for l in leaves if l[idx]==k]; w=sum(l[0] for l in sel); out[k]=(round(w,4),round(sum(l[0]*l[1] for l in sel)/w))
    print('node',name,out)
# representative leaves (P=1, TX15)
for o in PO:
    for t,(s,sx,pt) in PT.items():
        d=value(n27(o),LR[o],1-s*STEP,1.0,sx,detail=True)
        print(f"leaf {o} {t} P=1 TX15: EBIT27 {d['ebit27']:.1f} EBITLR {d['ebit_lr']:.1f} GPM_LR {d['gpm_lr']:.3f} => {d['per_share']:,.0f}")
# ---- sensitivities (on base path unless noted)
B=dict(nvl27=EN27,nvlLR=ENLR,f=Ef,p=EP,s_exp=Esx)
S={}
grid={r:{g:round(value(**B,r=r,g=g)) for g in (0,.01,.02,.03)} for r in (.125,.13,.135,.14,.145)}
for m in (.8,.9,1.1,1.2): S[f'ebitLR_x{m}']=value(**B,lr_mult=m)
for s in (0.135,0.35,0.75,1.0): S[f's_eff{s}']=value(EN27,ENLR,1-s*STEP,EP,0.35)
S['tax_stays_10']=value(EN27,ENLR,1.0,EP,0.35)
for p in (0.90,0.95,1.05,1.10): S[f'price_x{p}']=value(EN27,ENLR,Ef,EP*p,Esx)
def cokeLR(c,norm=1.37):
    k=norm/1.13*3857/100e6
    lr={'O1':0.4660+k*(c-1491),'O2':0.4864+k*(c-1541),'O3':0.5520+k*(c-2040)}
    g2=0.5520+k*(2108-2040); g1=0.4864+k*(2108-1541)
    e27=sum(PO[o]*(0.5*g2+0.5*(g1 if o!='O3' else g2)) for o in PO)
    return value(e27,sum(PO[o]*lr[o] for o in PO),Ef,EP,Esx)
for c in (1704,1825,2108): S[f'cokeLR_{c}']=cokeLR(c)
for nm in (1.25,1.5): S[f'coke_norm_{nm}']=cokeLR(1825,nm)
for a in (-0.0275,0.0275): S[f'nvlLR{a:+.4f}']=value(EN27,ENLR+a,Ef,EP,Esx)
for o in PO: S[f'O_fixed_{o}']=value(n27(o),LR[o],Ef,EP,Esx)
for pa in (0.3,0.7):
    pb=0.55; both=pa*pb; one=pa*(1-pb)+(1-pa)*pb; neither=(1-pa)*(1-pb)
    po={'O1':both*0.5,'O2':both*0.5+one/2,'O3':neither+one/2}
    S[f'P(A)={pa}']=value(sum(po[o]*n27(o) for o in po),sum(po[o]*LR[o] for o in po),Ef,EP,Esx)
S['elec_x0.98_noF5']=value(**B,elec=0.98)
S['transfer_below_netback_-5pct']=value(**B,transfer=0.05)
S['oneoff_-50']=value(**B,oneoff=-50); S['pledge_loss_-42.6']=value(**B,oneoff=-42.6)
S['deposit70_at_face']=value(**B,oneoff=LOCKED70)
for k,v in S.items(): print(f"{k:32s} {v:,.0f}")
print('grid r x g (co so)'); [print(r,grid[r]) for r in grid]
roe=289.9/650; vs=289.9*0.94*(1-min(max(0.02/roe,0),0.8))/(0.135-0.02)/SH*1000
print(f"V_ngan {vs:,.0f} V_dai(co so) {base['per_share']:,.0f} D {abs(math.log(vs/base['per_share'])):.3f}")
json.dump(dict(center=center,band_p25_p75=band,band_p10_p90=band90,base=base,net_cash=NET_CASH,v_ngan=vs,sens=S,grid={str(k):v for k,v in grid.items()},
  leaves=[dict(p=l[0],v=l[1],O=l[2],P=l[3],T=l[4],TX=l[5]) for l in leaves]),open('model_out_r2_rerun.json','w'),indent=1,default=float)
