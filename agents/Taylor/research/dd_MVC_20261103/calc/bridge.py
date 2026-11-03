"""fundamental-skeptic vong 2 — cau noi MVC 'gia phang' + phan phan (KHONG sua file goc).
Chay: python3 -B /tmp/fs_mvc_bridge/bridge.py"""
import sys, importlib, copy
sys.dont_write_bytecode=True
CALC='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/dd_MVC_20261103/calc'
sys.path.insert(0,CALC)
import valuation as M
SCN=M.SCN; W=M.W
def mid():
    f=sum(W[k]*M.value(k,'flat') for k in SCN); r=sum(W[k]*M.value(k,'real') for k in SCN); return f,r,(f+r)/2
base=mid(); print('BASELINE flat %.0f real %.0f mid %.0f'%base)
# ---------------- A. cau noi flat co_so
for mode in ('flat','real'):
    d=M.value('co_so',mode,detail=True)
    VM=d['VM']; s=M.s_NNC; c=M.c_MVC; h=0.15
    pre=s*(d['N_ex']+c*VM)
    Dm=VM-d['NNC_stake']
    capex_pv=M.pv([(2027,-0.6*M.CAPEX_LEFT),(2028,-0.4*M.CAPEX_LEFT)],0.13)
    print(f'\n[{mode} co_so] ty dong (d/cp = x10)')
    for k in ('A_TanLap','B_moMoi','C_BOT','D_gach_xang','Q4','NETFIN','MCC_NHC_ICD','LAND'):
        print(f'  {k:12s} {d[k]:8.1f}  ({d[k]*10:7.0f} d/cp)')
    print(f'    B = PV van hanh {d["B_moMoi"]-capex_pv:7.1f} + PV capex con lai {capex_pv:7.1f}')
    print(f'  = Dm truc tiep {Dm:8.1f} ({Dm*10:.0f} d/cp)')
    print(f'  NNC truoc holding s*(N_ex+c*VM) = {s:.4f}*({d["N_ex"]:.1f}+{c}*{VM:.1f}) = {pre:.1f}; holding 15% -> {d["NNC_stake"]:.1f} (cat {pre-d["NNC_stake"]:.1f})')
    print(f'  VM {VM:.1f} = {d["per_share"]:.0f} d/cp')
    print(f'  Chuong trinh mo moi vs khong dau gia: B {d["B_moMoi"]:.1f} + dat da chi nam trong no rong -431.9 = {d["B_moMoi"]-431.857:.1f} ty')
# so sanh 'gia tri gop von NNC'
print('\nMoc so sanh phan NNC: so sach VCSH HN Q3 470,0 ty (4.700 d/cp MVC); thi truong 9,659tr x 47.100 = %.0f ty; NNC-DD v2 tam 69.402 -> %.0f ty'%(9.65917*47.1, 9.65917*69.402))
# ---------------- NNC van hanh vs Tan Lap (iv)
def nnc_ops(k,mode):
    return M.nnc_ex(k,mode,0.13)-(M.n_q4+M.n_cash+M.n_nhc_book+(M.n_cip if k in('tot','co_so') else 0))
for mode in ('flat','real'):
    print(f'(iv) {mode} co_so: NNC ops PV {nnc_ops("co_so",mode):.0f} (44,07% = {M.s_NNC*nnc_ops("co_so",mode):.0f}) | Tan Lap PV {M.pv(M.cf_A("co_so",mode),0.13):.0f}')
for y in (2027,2028,2031,2035,2040):
    f=1.03**(y-2026); p=M.nprice('co_so',y)
    nn=p-110*.97*f-(70*.97*f+20*f-M.RENT*f)/(1.4 if y==2027 else (1.1 if y<2031 else 1.2))
    tl=M.REL*p-130*f-40*f/(1.3 if y==2027 else 1.2)
    print(f'   {y} flat bien/m3: NNC {nn:6.1f}k  TanLap {tl:6.1f}k (gia {p}, MVC {M.REL*p:.0f})')
def setv(**kw):
    old={a:copy.deepcopy(getattr(M,a)) for a in kw}
    for a,v in kw.items(): setattr(M,a,v)
    return old
def show(lab,**kw):
    old=setv(**kw); f,r,m=mid(); cf=M.value('co_so','flat'); setv(**old)
    print(f'{lab:62s} flat {f:7,.0f} real {r:7,.0f} mid {m:7,.0f} ({m-base[2]:+6,.0f}) | co_so flat {cf:7,.0f}')
print('\n=== Doi tung gia dinh ===')
show('baseline')
# REL hieu chinh nhat quan: giu bien 2026 = 0,87*380-130 = 200,6k
gp=0.87*380-130
for rel in (0.80,0.95,1.00):
    show(f'REL {rel} + COST_A hieu chinh lai ({rel*380-gp:.0f}k)',REL=rel,COST_A=rel*380-gp)
    show(f'REL {rel} KHONG hieu chinh (nhu bao cao)',REL=rel)
show('holding 0%')  # placeholder
def show_h(lab,h):
    f=sum(W[k]*M.value(k,'flat',hold=h) for k in SCN); r=sum(W[k]*M.value(k,'real',hold=h) for k in SCN); m=(f+r)/2
    print(f'{lab:62s} flat {f:7,.0f} real {r:7,.0f} mid {m:7,.0f} ({m-base[2]:+6,.0f}) | co_so flat {M.value("co_so","flat",hold=h):7,.0f}')
show_h('holding 0% (thay 15%)',0.0)
for rel in (0.80,0.95,1.00):
    show(f'REL {rel} + COST_A & COST_B hieu chinh lai',REL=rel,COST_A=rel*380-gp,COST_B=rel*380-gp+5)
show('capex mo moi con lai -30% (doi xung voi +30% bao cao)',CAPEX_LEFT=M.CAPEX_LEFT*0.7)
show('capex mo moi con lai +30% (bao cao)',CAPEX_LEFT=M.CAPEX_LEFT*1.3)
show('mo moi chi phi 105k (doi xung voi 165k)',COST_B=105)
show('han GP Tan Lap 2043 = han NNC (moi kb tru tot 2045)',END_A={'tot':2045,'co_so':2043,'xau':2038,'rat_xau':2038})
# lua chon dung du an o co_so (san ban dat 30%) — chi de do gia tri gia dinh 'chay bat ke NPV'
orig_value=M.value
def value_floor_all(k,mode='flat',r=0.13,hold=0.15,detail=False,endA=None):
    A=M.pv(M.cf_A(k,mode,endA),r); B=max(M.pv(M.cf_B(k,mode),r),M.SALV); C=M.pv(M.cf_C(k),r); D=M.pv(M.cf_D(k),r)
    N_ex=M.nnc_ex(k,mode,r); oth=M.ASSOC_K[k]*(M.MCC_BOOK+M.NHC_BOOK)+M.ICD_K[k]*M.ICD_BOOK+M.LAND[k]
    Dm=A+B+C+D+M.Q4_DIRECT+M.NETFIN+oth
    VM=(Dm+(1-hold)*M.s_NNC*N_ex)/(1-(1-hold)*M.s_NNC*M.c_MVC); return VM*1e9/M.SH_M
M.value=value_floor_all; show('san dung du an ap ca co_so/tot (B=max(B,130))'); M.value=orig_value
# duong gia g2031 / g2028 (NNC-DD v2 co 4 bien the; MVC chi dung 2)
orig_g=M.g
for gm,lab in (('g2031','+3%/nam tu 2031 (sau vach)'),('g2028','+3%/nam tu 2028')):
    def g2(y,mode,_gm=gm):
        if mode=='flat': return 1.0
        if mode=='real': return (1.03)**(y-2026)
        return (1.03)**max(0,y-(2030 if _gm=='g2031' else 2027))
    M.g=g2
    for k in SCN: pass
    v={k:M.value(k,gm) for k in SCN}; e=sum(W[k]*v[k] for k in SCN)
    print(f'{"duong gia "+lab:62s} KV {e:7,.0f} ({e-base[2]:+6,.0f} vs tam) | co_so {v["co_so"]:7,.0f}')
M.g=orig_g
# tre 1 nam NHAT QUAN: mo moi tre 1 nam VA vach gia/san luong NNC cung lui 1 nam (vach do chinh cung moi gay ra)
orig_np=M.nprice
def nprice_shift(k,y):
    a=M.NNC_SCN[k]; return a[2] if y<=2028 else (a[3] if y<2032 else a[5])
def nnc_ex_shift(k,mode,r):
    a=M.NNC_SCN[k]; out=[]
    for y in range(2027,2044):
        v=a[0] if y<=2028 else (a[1] if y<2032 else a[4]); p=nprice_shift(k,y); f=1.03**(y-2026)
        ebit=v*(p*M.g(y,mode)-M.VAR*M.K*f)-M.FIX*M.K*f-M.SGA*f+M.RENT*f; out.append((y,max(ebit,0)*(1-M.TAX)))
    return M.pv(out,r)+M.n_q4+M.n_cash+M.n_nhc_book+(M.n_cip if k in('tot','co_so') else 0)
old=dict(M.DELAY); M.DELAY['co_so']=1
show('v2 (1): co_so tre 1 nam, vach gia GIU 2028 (nhu bao cao)')
orig_nx=M.nnc_ex
M.nprice=nprice_shift; M.nnc_ex=nnc_ex_shift
show('co_so tre 1 nam + vach gia/san luong lui 1 nam (moi kb)')
M.DELAY.update(old)
M.nprice=orig_np; M.nnc_ex=orig_nx
show('check reset')
print('\n=== D. NNC nhat quan he phuong trinh (V_N = N_ex + c*VM, MVC theo mo hinh MVC thay vi gia 14.100) ===')
for mode in ('flat','real'):
    vs={}
    for k in SCN:
        d=M.value(k,mode,detail=True); vs[k]=(d['N_ex']+M.c_MVC*d['VM'])*1e9/M.N_SH
    e=sum(W[k]*vs[k] for k in SCN)
    print(mode,' '.join(f'{k} {vs[k]:,.0f}' for k in SCN),f'| KV {e:,.0f}')
    # chiet khau 15% tren co phan MVC cua NNC (nhu NNC v2)
    vs2={k:(M.value(k,mode,detail=True)['N_ex']+0.85*M.c_MVC*M.value(k,mode,detail=True)['VM'])*1e9/M.N_SH for k in SCN}
    print('   (MVC disc 15%)', f'KV {sum(W[k]*vs2[k] for k in SCN):,.0f}')
# luoi 'co the bao ve': duong g2031, r x hold x capex
import numpy as np, itertools
def g2(y,mode):
    if mode=='flat': return 1.0
    if mode=='real': return 1.03**(y-2026)
    return 1.03**max(0,y-2030)
M.g=g2
out=[]
for r,h,cx,cb in itertools.product((0.11,0.13,0.15),(0.0,0.15,0.30),(0.7,1.0,1.3),(0.85,1.0,1.15)):
    M.CAPEX_LEFT=(1500-438.4)*cx; M.COST_A=130*cb
    out.append(sum(W[k]*M.value(k,'g2031',r=r,hold=h) for k in SCN))
M.CAPEX_LEFT=1500-438.4; M.COST_A=130
o=np.array(out)
print(f'\nLuoi g2031 x r(3) x hold(3) x capex(+-30%) x chi phi Tan Lap(+-15%) = {len(o)}: P10 {np.percentile(o,10):,.0f} P25 {np.percentile(o,25):,.0f} P50 {np.median(o):,.0f} P75 {np.percentile(o,75):,.0f} P90 {np.percentile(o,90):,.0f}')
v={k:M.value(k,'g2031') for k in SCN}; print('g2031 r13 h15 kb:',{k:round(x) for k,x in v.items()})
M.g=orig_g
