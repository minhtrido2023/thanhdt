"""DD MVC 03/11/2026 — SOTP MU GIA (khong doc gia/von hoa MVC; gia tham chieu chi so sanh o REPORT §cuoi, sau khi khoa md5 output).
Don vi: ty dong. Gia dinh tu dat = (uoc luong). Nguon so lieu: BCTC HN/rieng Q3/2026, soat xet 6T/2026, KT 2025, tai lieu DHCD 2026 (src/).
Cau phan:
 A. Mo da Tan Lap (CN Binh Phuoc, Dong Phu) — 90 ha, cong suat 1,4 tr m3 thanh pham/nam (website cong ty). Han GP: CHUA XAC MINH -> kich ban.
 B. 2 mo moi trung dau gia 19/03/2026 (QD 2080, 2083/QD-UBND 07/04/2026): Tam Lap 1 khu 1 (14,81 tr m3 nguyen khoi, 1,0 tr/nam)
    + Minh Hoa (3,95 tr m3, 0,5 tr/nam); tong dau tu 1.500, van hanh 2028 (NQ DHDCD 03/DHDCD26). Da chi ~438 (CIP 431,86 dat + 6,56 tien cap quyen).
 C. BOT DT743 (tram Binh Thung/Lai Thieu con thu; Binh Thang dung 22/10/2024). Han thu: CHUA XAC MINH -> kich ban.
 D. Gach (Ben Cat/Long Nguyen; My Phuoc dung 08/2025) + xang dau + dich vu: gop.
 E. Lien ket: NNC 44,07% (9.659.170 cp) — mo hinh NNC tai dung khung dd_NNC_20261030/calc/valuation_v2.py (path/chi phi K=0,97/cho thue),
    BO phan co phan MVC ma NNC nam (xu ly so huu cheo bang he phuong trinh), NHC theo so sach (khong dung gia).
    MCC 30,08%, NHC 30,04%, ICD Hoa Lu (100%, gop 44,80) theo so sach x he so.
 F. Dat du an nha o (Lai Hung 6,1 ha, My Phuoc 3,1+2,4 ha NOXH, Long Nguyen 11,9 ha) = option, chua co chu truong.
 G. Tai chinh rong 30/09/2026 (HN): tien 117,40 + HTM NH 274,42 + HTM DH 20,00 - vay NH 461,85 - co tuc phai tra 60,00 - quy KTPL 6,52.
So huu cheo: V_M = D + s*V_N ; V_N = N_ex + c*V_M  (s=0,4407 MVC->NNC ; c=0,103 NNC->MVC).
"""
import csv, numpy as np
INFL=0.03; TAX=0.20; T0=2026.83
SH_M=100e6; SH_N=21.92e6
s_NNC=9.659170/21.92; c_MVC=0.103
# ---------- G. tai chinh rong (BCTC HN Q3/26 tr.1-3, V.1, V.2, V.19, V.20)
NETFIN=117.395+274.416+20.000-461.848-60.000-6.524
# ---------- Q4/2026: LNST truc tiep (khong lien ket) Q3/26 = 81,33 - 19,84 (lien ket) - 10,57 (co tuc LK) = 50,9 -> Q4 ~50 (uoc luong)
Q4_DIRECT=50.0
def pv(cf,r): return sum(c/(1+r)**(y-T0+0.5) for y,c in cf)
def g(y,mode):  # he so gia danh nghia
    return 1.0 if mode=='flat' else (1+INFL)**(y-2026)
# ---------- gia NNC theo kich ban (k/m3, tien 2026) — giong dd_NNC v2; MVC ban thap hon (kenh phan phoi, khac quy cach): x0,87 (uoc luong)
REL=0.87
NNC_SCN={'tot':(1.40,1.40,420,400,1.40,420),'co_so':(1.40,1.10,380,300,1.20,320),
         'xau':(1.30,0.80,330,250,0.80,250),'rat_xau':(0.80,0.80,230,210,0.80,210)}
def nprice(k,y):
    a=NNC_SCN[k]; return a[2] if y==2027 else (a[3] if y<2031 else a[5])
# ---------- A. mo Tan Lap
# Hieu chinh: LN gop 9T/26 hang hoa+thanh pham = 251,19 - BOT 25,67 - dich vu 6,93 = 218,6; tru xang dau ~8 + gach ~10 (uoc luong) -> da ~200/9T
# => ~265/nam o ~1,3 tr m3 -> bien gop ~200k/m3; gia ban 2026 ~330k (=0,87 x 380) -> chi phi tien mat ~130k/m3 (uoc luong)
COST_A=130; SGA_A=40
VOL_A={'tot':(1.40,1.40),'co_so':(1.30,1.20),'xau':(1.30,1.05),'rat_xau':(0.90,0.90)}   # (2027, 2028+)
END_A={'tot':2045,'co_so':2040,'xau':2035,'rat_xau':2035}   # han GP CHUA XAC MINH (uoc luong)
def cf_A(k,mode,endA=None):
    out=[]; end=endA or END_A[k]
    for y in range(2027,end+1):
        v=VOL_A[k][0] if y==2027 else VOL_A[k][1]
        f=(1+INFL)**(y-2026)
        ebit=v*(REL*nprice(k,y)*g(y,mode)-COST_A*f)-SGA_A*f
        out.append((y,max(ebit,0)*(1-TAX)))
    return out
# ---------- B. 2 mo moi: thanh pham = nguyen khoi x 1,42 (ty le NNC BCTN25)
CAP_B=1.5*1.42; CAPEX_LEFT=1500-438.4      # ~1.062 con lai (uoc luong: tong 1.500 theo NQ)
COST_B=135; SGA_B=15                        # chi phi tien mat ~ mo cu +5k (boc tang phu moi); tien trung dau gia nam trong capex 1.500 -> khong tinh lai (uoc luong)
SALV=0.30*431.857                           # san 'dung du an': ban lai dat da mua 30% gia goc (uoc luong); khong tinh bat buoc tiep tuc dau tu
UTIL={'tot':(0.6,1.0,1.0),'co_so':(0.5,0.8,0.8),'xau':(0.4,0.5,0.5),'rat_xau':(0.3,0.4,0.4)}  # 2028, 2029, 2030+
DELAY={'tot':0,'co_so':0,'xau':1,'rat_xau':2}   # tre GP/van hanh (nam)
def cf_B(k,mode):
    out=[]; d=DELAY[k]
    out.append((2027,-0.6*CAPEX_LEFT)); out.append((2028,-0.4*CAPEX_LEFT))
    tl_left=14.806; mh_left=3.945                # tr m3 nguyen khoi
    for y in range(2028+d,2050):
        u=UTIL[k][min(y-2028-d,2)]
        q_tl=min(1.0*u,tl_left); q_mh=min(0.5*u,mh_left); tl_left-=q_tl; mh_left-=q_mh
        v=(q_tl+q_mh)*1.42
        if v<=1e-6: break
        f=(1+INFL)**(y-2026)
        ebit=v*(REL*nprice(k,y)*g(y,mode)-COST_B*f)-SGA_B*f
        sust=0.03*v*REL*nprice(k,y)*g(y,mode)
        out.append((y,max(ebit,0)*(1-TAX)-sust))
    return out
# ---------- C. BOT DT743: LN gop 2025 = 54,71 - 22,83 = 31,88 (KT25 7.1/7.2); 6T/26 17,09; han CHUA XAC MINH
BOT_GP=32.0; BOT_YRS={'tot':8,'co_so':5,'xau':3,'rat_xau':2}
def cf_C(k): return [(2027+i,BOT_GP*(1-TAX)) for i in range(BOT_YRS[k])]
# ---------- D. gach + xang dau + dich vu - phi chung con lai: LN gop ~33/nam (gach ~13, xang ~11, dich vu ~9) - SG&A 24 (uoc luong)
D_EBIT={'tot':20,'co_so':9,'xau':0,'rat_xau':-5}
def cf_D(k): return [(y,D_EBIT[k]*(1-TAX) if D_EBIT[k]>0 else D_EBIT[k]) for y in range(2027,2037)]
# ---------- E. NNC: tai dung khung NNC v2 (tu kiem: NNC Q3/26 tien+HTM-vay, du phong truy thu...)
N_SH=21.92e6
n_cash=25.474+322.440+0.130-5.000-69.890-22.373-16.776-5.888-4.497
n_nhc_book=710242*19893/1e9          # NHC so sach (BQ BVPS Q2/26) — thay cho gia thi truong
n_cip=83.506; n_q4=60.0; VAR=110; FIX=70; SGA=20; K=0.97; RENT=18.920-7.790
def nnc_ex(k,mode,r):
    a=NNC_SCN[k]; out=[]
    for y in range(2027,2044):
        v=a[0] if y==2027 else (a[1] if y<2031 else a[4]); p=nprice(k,y)
        f=(1+INFL)**(y-2026)
        ebit=v*(p*g(y,mode)-VAR*K*f)-FIX*K*f-SGA*f+RENT*f
        out.append((y,max(ebit,0)*(1-TAX)))
    return pv(out,r)+n_q4+n_cash+n_nhc_book+(n_cip if k in('tot','co_so') else 0)
# MCC/NHC/ICD so sach x he so (uoc luong)
MCC_BOOK=0.3008*4986124*14788/1e9; NHC_BOOK=0.3004*3041542*19893/1e9; ICD_BOOK=44.797
ASSOC_K={'tot':1.0,'co_so':0.8,'xau':0.5,'rat_xau':0.3}; ICD_K={'tot':1.0,'co_so':0.6,'xau':0.0,'rat_xau':0.0}
# ---------- F. dat du an nha o — option (uoc luong rat tho; chua co chu truong dau tu)
LAND={'tot':400,'co_so':100,'xau':0,'rat_xau':0}
FLOOR=True
SCN=list(NNC_SCN); W={'tot':.25,'co_so':.50,'xau':.20,'rat_xau':.05}
def value(k,mode='flat',r=0.13,hold=0.15,detail=False,endA=None):
    A=pv(cf_A(k,mode,endA),r); B=pv(cf_B(k,mode),r); B=max(B,SALV) if (FLOOR and k in ('xau','rat_xau')) else B; C=pv(cf_C(k),r); D=pv(cf_D(k),r)
    N_ex=nnc_ex(k,mode,r)
    oth=ASSOC_K[k]*(MCC_BOOK+NHC_BOOK)+ICD_K[k]*ICD_BOOK+LAND[k]
    Dm=A+B+C+D+Q4_DIRECT+NETFIN+oth
    # so huu cheo; chiet khau holding ap len phan NNC
    VM=(Dm+(1-hold)*s_NNC*N_ex)/(1-(1-hold)*s_NNC*c_MVC)
    ps=VM*1e9/SH_M
    if detail: return dict(A_TanLap=A,B_moMoi=B,C_BOT=C,D_gach_xang=D,Q4=Q4_DIRECT,NETFIN=NETFIN,MCC_NHC_ICD=oth-LAND[k],LAND=LAND[k],
                           NNC_stake=(1-hold)*s_NNC*(N_ex+c_MVC*VM),VM=VM,per_share=ps,N_ex=N_ex)
    return ps
def ev(**kw):
    v={k:value(k,**kw) for k in SCN}; return sum(W[k]*v[k] for k in SCN),v
if __name__=='__main__':
    print(f'Mo moi: capex/tru luong = {1500/(14.806+3.945):.0f}k/m3 nguyen khoi (Gia Canh ~16k, nguoi doc nganh)'); print(f'NETFIN {NETFIN:.1f} | MCC so sach x30,08% {MCC_BOOK:.1f} | NHC {NHC_BOOK:.1f} | s={s_NNC:.4f} c={c_MVC}')
    print('\n=== SOTP chi tiet (r=13%, holding 15%) ty dong ===')
    rows=[]
    for mode in ('flat','real'):
        for k in SCN:
            d=value(k,mode=mode,detail=True)
            print(mode,k,' '.join(f'{a}={b:,.0f}' for a,b in d.items()))
            rows.append([mode,k]+[round(b,1) for b in d.values()])
    with open('sotp_detail.csv','w',newline='') as fh:
        w=csv.writer(fh); w.writerow(['mode','kb']+list(value('co_so',detail=True).keys())); w.writerows(rows)
    print('\n=== Gia tri/cp theo kich ban (tot/co_so/xau/rat_xau | KV 25/50/20/5) ===')
    res={}
    for mode in ('flat','real'):
        for r in (0.11,0.13,0.15):
            for hold in (0.0,0.15,0.30):
                e,v=ev(mode=mode,r=r,hold=hold); res[(mode,r,hold)]=(e,v)
                print(f'{mode:4s} r={r:.0%} hold={hold:.0%}: '+' '.join(f'{v[k]:>7,.0f}' for k in SCN)+f' | KV {e:>7,.0f}')
    lo=res[('flat',0.13,0.15)][0]; hi=res[('real',0.13,0.15)][0]; mid=(lo+hi)/2
    grid=np.array([x[0] for x in res.values()])
    print(f'\nTAM r13 hold15: phang {lo:,.0f} .. thuc {hi:,.0f} ; diem giua {mid:,.0f}')
    print(f'LUOI 2 duong gia x 3 r x 3 holding = {len(grid)}: min {grid.min():,.0f} P10 {np.percentile(grid,10):,.0f} trung vi {np.median(grid):,.0f} P90 {np.percentile(grid,90):,.0f} max {grid.max():,.0f}')
    print('\n3 kich ban NDT (tich cuc / co so / tieu cuc=xau:rat_xau 20:5), r13 hold15:')
    for mode in ('flat','real'):
        v=res[(mode,0.13,0.15)][1]
        print(mode, round(v['tot']), round(v['co_so']), round((0.20*v['xau']+0.05*v['rat_xau'])/0.25))
    print('\n=== Do nhay (diem giua phang..thuc, r13 hold15) ===')
    def midv(**kw): return (ev(mode='flat',**kw)[0]+ev(mode='real',**kw)[0])/2
    base=midv()
    for lab,fn in [('han GP Tan Lap 2035 moi kich ban',lambda: (sum(W[k]*value(k,'flat',endA=2035) for k in SCN)+sum(W[k]*value(k,'real',endA=2035) for k in SCN))/2),
                   ('han GP Tan Lap 2045 moi kich ban',lambda: (sum(W[k]*value(k,'flat',endA=2045) for k in SCN)+sum(W[k]*value(k,'real',endA=2045) for k in SCN))/2)]:
        x=fn(); print(f'{lab:40s} {x:,.0f} ({x-base:+,.0f})')
    import valuation as M
    for lab,attr,val in [('chi phi da cu +15% (150k)','COST_A',150),('chi phi da cu -15% (110k)','COST_A',110),
                         ('mo moi chi phi 165k','COST_B',165),('mo moi capex con lai +30%','CAPEX_LEFT',CAPEX_LEFT*1.3),
                         ('he so gia MVC/NNC 0,80','REL',0.80),('he so gia MVC/NNC 0,95','REL',0.95),('dat du an = 0 moi kb','LAND',{k:0 for k in SCN}),('KHONG san dung du an (mo moi chay bang moi gia)','FLOOR',False)]:
        old=getattr(M,attr); setattr(M,attr,val)
        x=(sum(M.W[k]*M.value(k,'flat') for k in SCN)+sum(M.W[k]*M.value(k,'real') for k in SCN))/2
        setattr(M,attr,old); print(f'{lab:40s} {x:,.0f} ({x-base:+,.0f})')
    # dong gop cua tung manh vao tam (co_so, diem giua)
    print('\nNNC ex-MVC (ty) co_so: phang %.0f / thuc %.0f; = %.0f / %.0f d/cp NNC'%(nnc_ex('co_so','flat',0.13),nnc_ex('co_so','real',0.13),
          nnc_ex('co_so','flat',0.13)*1e9/N_SH,nnc_ex('co_so','real',0.13)*1e9/N_SH))
    # chi tieu tham chieu (khong phai gia thi truong): LN, EPS, BVPS
    np_ttm=75.1+65.8+84.6+81.325   # Q4/25-Q2/26 BQ ticker_financial; Q3/26 BCTC HN
    print(f'\nLNST HN TTM {np_ttm:.1f} ty, EPS TTM {np_ttm*10:.0f} d; BVPS 30/09 {1545.995*10:.0f} d; tam/BVPS = {mid/15460:.2f}x; tam/EPS = {mid/(np_ttm*10):.1f}x')
    with open('valuation_grid.csv','w',newline='') as fh:
        w=csv.writer(fh); w.writerow(['mode','r','hold']+SCN+['KV'])
        for (m,r,h),(e,v) in res.items(): w.writerow([m,r,h]+[round(v[k]) for k in SCN]+[round(e)])
