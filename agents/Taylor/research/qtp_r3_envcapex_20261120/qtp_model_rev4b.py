"""QTP DD r3 20/11/2026 (job Taylor_20261120_041936) - them du an nang cap, cai tao HT xu ly khi thai.
r3b: them tham so bien the (stop_ov, comp_start, comp_k, dep_yrs, tmdt, vc_abs), tach VC, trong so W_F.
Nen = r2 (agents/Taylor/research/dd_QTP_20261117/model/qtp_model.py) - giu nguyen, chi CONG delta du an.
So nguon du an = FS goc (src_fs/, CBTT VNDirect 11/06/2026, BC tham tra PECC1 so 2985/TVD1-NDNLM 22/5/2026):
  TMDT truoc VAT 3.484,88 ty (sau VAT 3.799,19); O&M co dinh 102,01 ty/nam; dien-nuoc-hoa chat 470,29 ty/nam
  (amoniac 12.045.120 kg x 26.350 d = 317,4 ty); dien thuong pham 6.501,57 GWh/nam;
  gia tang them de nghi 169,44 d/kWh = FC 81,42 + O&M co dinh 15,69 + bien doi 72,33; FIRR 11%; tuoi tho kinh te 18 nam.
Vay 2.787,9 ty = 80% (QD 917 15/6/2026; QD 1490 21/9/2026: BIDV 1.787,9 + VCB 1.000). EPC 89.756.813 USD + 901,8 ty
  (QD 1710 6/10/2026, 38 thang). LAI SUAT / KY HAN: KHONG co trong van ban nao doc duoc -> (uoc luong).
Chay: python3 qtp_model_rev4.py   (in so; khong ghi file).
rev4 (23/11/2026, job Taylor_20261123_063644) - xu ly skeptic r1 (INCONCLUSIVE):
  (a) quy khen thuong-phuc loi (KTPL) tru khoi FCFE: ty le do tu BCTC KT 2025 TM 19.1 (trich 2025 = 71,36 ty tren
      LNST 2024 619,26; trich 2024 = 69,04 tren LNST 2023 614,4) -> 11,4%, tra nam sau tren LNST toan cong ty >0;
  (b) trong so P0/P50/P100 ve 0,5/0,3/0,2 (r3) - skeptic: doi 0,4 o r3b khong co du kien moi; legal-vn 23/11 bat loi them;
  (c) Cvlp (amoniac qua gia bien doi) = kich ban co dieu kien (can sua PPA, TT12 D18: Cvlp chi truot 2,5%/nam) - KHONG vao tam;
  (d) bien the: san luong (vol), ty gia EPC USD (extra_eq), thay xuc tac SCR (extra_opex, uoc luong), FC chi 10 nam (fc_end)."""
import statistics as st

# ---------------- r2 nen (chep nguyen, khong sua) ----------------
SH = 450.0
q = {'23Q1':143.9,'23Q2':248.3,'23Q3':11.6,'23Q4':210.6,'24Q1':226.5,'24Q2':161.8,'24Q3':76.1,'24Q4':154.8,
     '25Q1':172.6,'25Q2':190.6,'25Q3':33.0,'25Q4':639.7,'26Q1':197.2,'26Q2':326.6,'26Q3':75.7}
FX_AT = (663.0-(69.04+2.23))*0.8
adj = dict(q); adj['25Q4'] -= FX_AT
for k in adj:
    if k[:2] in ('23','24'): adj[k] *= 0.8/0.9
keys = list(q); ttm = [sum(adj[k] for k in keys[i-3:i+1]) for i in range(3, len(keys))]
NORM = st.median(ttm[-12:])
netcash = 82.18+1774.11-0.07*10000*SH/1000
nwc = 3091.52+729.32+16.66-1578.55
R0 = 0.135
INT_AT = 1541.3*0.05*0.8
NORM_OP = NORM-INT_AT
DA_Q = 104.53; DA_now = 4*DA_Q; REM = 1803.4
Q4_FLOW = 145.0+DA_Q-4.0
YEARS = list(range(2027, 2055))
def da_sched():
    out = {}; left = REM-DA_Q
    for y in YEARS:
        d = max(0, min(left, DA_now*(0.85 if y > 2028 else 1.0))); out[y] = d; left -= d
    return out
DA = da_sched()
def capfn(stop):
    if stop == '40y': return lambda y: 1.0 if y <= 2051 else (0.5 if y <= 2054 else 0.0)
    return lambda y: 1.0 if y <= stop else 0.0
def npat_base(kind, y, gnom=0.0):
    n = NORM_OP*(1+gnom)**(y-2026)
    if kind == 'base': return n
    if kind == 'good': return n+(DA_now-DA[y])*0.8
    return n*0.85 if y <= 2027 else n*0.5
def val_r2(kind, stop=2047, rr=R0):
    cap = capfn(stop)
    if kind == 'bad': cap = capfn(min(2040, stop))
    pv = Q4_FLOW/(1+rr)**0.125
    for y in YEARS:
        c = cap(y); cp = cap(y-1) if y > 2027 else 1.0
        pv += c*(npat_base(kind, y)+DA[y]-15)/(1+rr)**(y-2027+0.5)
        pv += nwc*(cp-c)/(1+rr)**(y-2027)
    return (pv+netcash)/SH*1000
STOP = {'bad': 2040, 'base': 2047, 'good': 2047}
W_R2 = {'bad': 0.25, 'base': 0.65, 'good': 0.10}          # r2 trong so (giu nguyen)

# ---------------- du an khi thai (r3) ----------------
TMDT = 3484.88                     # ty, truoc VAT (FS bang TMDT)
LOAN = 2787.9                      # ty (QD 917/1490) = 80,0% TMDT
EQ = TMDT-LOAN                     # 697,0 ty
FOM = 102.01                       # ty/nam O&M co dinh (FS; = 15,69 d/kWh x 6.501,57 GWh)
VC = 470.29                        # ty/nam dien-nuoc-hoa chat (FS; = 72,33 d/kWh x 6.501,57 GWh)
FC_REV = 81.42*6501.57/1000        # 529,4 ty/nam phan von (FS gia FC)
ECON_LIFE_END = 2047               # FS: tuoi tho kinh te 18 nam tu COD 2030 -> 2047
DISB = {2027: 0.30, 2028: 0.45, 2029: 0.25}   # (uoc luong) tien do giai ngan theo 38 thang tu 10/2026
COD = 2030                         # (uoc luong) 6/10/2026 + 38 thang = 12/2029 -> van hanh du nam tu 2030
TENOR = 10                         # (uoc luong) tra goc deu 10 nam 2030-2039 (= thoi gian khau hao FS 10 nam)
DEP_YRS = 10                       # FS: thoi gian khau hao 10 nam
TAX = 0.20
LIQ = 0.10

VC_AMMONIA = 12045120*26350/1e9    # ty: amoniac 317,4 (FS)
VC_POWER = 18470400*2036/1e9       # ty: dien tu dung 18,47 GWh x 2.036 d/kWh (gia mua dien chay thu, FS) = 37,6
VC_REST = VC-VC_AMMONIA-VC_POWER   # ty: phan du ~115,3 CHUA thuyet minh trong FS doc duoc (nuoc/hoa chat khac?) - nhan

def env_delta(kind='base', comp=0.0, comp_cap_only=False, i=0.09, rr=R0, opex_start=None,
              shift=0, vc_scale=1.0, detail=False, stop_ov=None, comp_start=None, comp_k=1.0,
              dep_yrs=None, tmdt=None, vc_abs=None, vol=1.0, vc_pass=False, fc_end=None,
              extra_opex=0.0, extra_from=2033, extra_eq=0.0):
    """Delta FCFE (ty/nam) cua du an cong vao kich ban r2 `kind`. comp = ty le bu qua gia tu comp_start
    (mac dinh COD; khong hoi to). shift = tri hoan dau tu. stop_ov = nam dung nha may (quyen tu bo).
    comp_k = he so gia bu (164,25/169,44). dep_yrs = so nam khau hao. tmdt = TMDT thay the (vay 80%).
    vc_abs = chi phi dien-nuoc-hoa chat tuyet doi (ty/nam) thay VC*vc_scale. Tra (PV d/cp, bang nam)."""
    stop = STOP[kind] if stop_ov is None else stop_ov; cod = COD+shift
    T = TMDT if tmdt is None else tmdt; L = 0.8*T if tmdt is not None else LOAN; E = T-L
    dy = DEP_YRS if dep_yrs is None else dep_yrs
    vc_use = (VC*vc_scale if vc_abs is None else vc_abs)*vol          # rev4: VC (amoniac...) ty le san luong
    fc_rev_k = FC_REV*comp_k*vol; fom_k = FOM*comp_k*vol; vc_k = vc_use*comp_k   # rev4: bu d/kWh x san luong
    fc_last = ECON_LIFE_END if fc_end is None else fc_end
    opex_start = cod if opex_start is None else max(opex_start, cod)
    cstart = cod if comp_start is None else max(comp_start, cod)
    bal = 0.0; idc_tot = 0.0; rows = []; pv = 0.0
    dep_base = None; carry = 0.0
    for y in YEARS:
        run = 1.0 if y <= stop else 0.0
        d = DISB.get(y-shift, 0.0)
        eq_out = (E+extra_eq)*d; draw = L*d   # rev4: extra_eq = von chu bu chenh ty gia EPC USD
        idc = 0.0; interest = 0.0; princ = 0.0; dep = 0.0; opex = 0.0; rev = 0.0
        if y < cod:                                   # xay dung: lai vay tra bang tien, von hoa
            idc = i*(bal+0.5*draw); idc_tot += idc; bal += draw
        else:
            if dep_base is None: dep_base = T+extra_eq+idc_tot
            if y < cod+TENOR and bal > 0:
                princ = min(bal, L/TENOR)
            if y >= stop and bal > 0 and y == stop: princ = bal   # dung nha may -> tat toan no
            if y > stop: princ = 0.0
            interest = i*(bal-0.5*princ) if y <= stop else 0.0
            bal -= princ
            dep = dep_base/dy if (y < cod+dy and y <= stop) else 0.0
            if y >= opex_start: opex = run*(FOM+vc_use+(extra_opex if y >= extra_from else 0.0))
            fc = fc_rev_k if y <= fc_last else 0.0
            if y >= cstart: rev = run*comp*(fc + (0.0 if (comp_cap_only or y < opex_start) else fom_k+vc_k))   # r3c: bu FOM+VC chi phat sinh cung opex
            if vc_pass and y >= opex_start: rev += run*(1-comp)*vc_use   # rev4: Cvlp amoniac qua gia bien doi phan chua bu
        # thue: tinh lai thue toan cong ty voi chuyen lo 5 nam (gian luoc: carry khong het han)
        pbt_b = run*npat_base(kind, y)/(1-TAX)
        pbt_n = pbt_b+rev-opex-dep-interest
        tax_b = TAX*max(0.0, pbt_b)
        use = min(carry, max(0.0, pbt_n)); taxable = max(0.0, pbt_n)-use
        carry = carry-use+max(0.0, -pbt_n)
        tax_n = TAX*taxable; dtax = tax_n-tax_b
        f = -eq_out-idc-interest-princ-opex+rev-dtax
        dnpat = (pbt_n-tax_n)-(pbt_b-tax_b)
        pv += f/(1+rr)**(y-2027+0.5)
        rows.append(dict(y=y, eq=eq_out, draw=draw, idc=idc, int=interest, princ=princ, dep=dep, opex=opex,
                         rev=rev, dtax=dtax, fcfe=f, dnpat=dnpat, bal=bal))
    return pv/SH*1000, rows

SCEN = {'P0': dict(comp=0.0), 'P50': dict(comp=0.5), 'P100': dict(comp=1.0)}
W_P = {'P0': 0.50, 'P50': 0.30, 'P100': 0.20}    # r3 (giu de doi chieu)
W_F = {'P0': 0.40, 'P50': 0.36, 'P100': 0.24}    # r3b - CHOT bang lap luan REPORT_r3b §4 TRUOC khi chay luoi (P50:P100 = 60:40)

def center(rr=R0, i=0.09, wp=W_P, liq=0.0, **kw):
    tot = 0.0
    for k, wk in W_R2.items():
        v = val_r2(k, rr=rr)
        for p, w in wp.items():
            tot += wk*w*(v+env_delta(k, i=i, rr=rr, **SCEN[p], **kw)[0])
    return tot*(1-liq)


def wgrid(p0):
    r = 1-p0; return {'P0': p0, 'P50': r*0.6, 'P100': r*0.4}


# ---------------- rev4 ----------------
KTPL_RATE = (69.04+71.36+94.58)/(614.4+619.26+1035.9)   # rev4b: trich 2024 69,04 & 2025 71,36 (KT25 TM19.1; TM30 xac nhan 71,36), 2026 ~94,58 = 544,58 giam khac LNST chua PP 9T26 (Q3/26 V.27) - 450 co tuc 1.000d (uoc luong tach) ; mau so LNST 2023/24/25
NPAT_2026 = 599.5 + 145.0                       # 9T26 thuc te (r2) + Q4 uoc (r2 Q4_FLOW 145, uoc luong)
KTPL_BAL = 148.64                               # ty, BCDKT Q3/26 ma 323 tai 30/9/2026 (cung moc netcash); KT25 31/12/2025 = 120,66
W_R4 = {'P0': 0.50, 'P50': 0.30, 'P100': 0.20}  # rev4: CHOT truoc khi chay (REPORT_rev4 §3)

KFIX = None   # rev4b bien the: quy KTPL tran co dinh (ty/nam) thay %LNST (gia thuyet tran theo luong)
def ktpl_pv(kind, rows, rr=R0, rate=None):
    """PV (d/cp) quy KTPL: tra nam y = rate x max(0, LNST toan cong ty nam y-1) (hoac min(KFIX, LNST) neu KFIX)."""
    rate = KTPL_RATE if rate is None else rate
    cap = capfn(STOP[kind]); prev = NPAT_2026; pv = 0.0
    for r in rows:
        y = r['y']
        amt = min(KFIX, max(0.0, prev)) if KFIX is not None else rate*max(0.0, prev)
        pv -= amt/(1+rr)**(y-2027+0.5)
        prev = cap(y)*npat_base(kind, y) + r['dnpat']
    return pv/SH*1000

def val4(kind, p, rr=R0, i=0.09, ktpl=True, krate=None, **kw):
    v, rows = env_delta(kind, i=i, rr=rr, **SCEN[p], **kw)
    return val_r2(kind, rr=rr) + v + ((ktpl_pv(kind, rows, rr, krate) - KTPL_BAL/SH*1000 + nwc_addback(kind, rr)) if ktpl else 0.0)

def nwc_addback(kind, rr=R0):
    """rev4b: nwc r2 (tru tong no ngan han, gom quy KTPL) thu hoi khi dung nha may => so du KTPL da tru o thoi diem 0
    khong duoc tru lan nua khi thu hoi nwc. Cong lai PV cua KTPL_BAL trong dong thu hoi nwc."""
    global nwc
    n0 = nwc; base = val_r2(kind, rr=rr); nwc = n0 + KTPL_BAL; up = val_r2(kind, rr=rr); nwc = n0
    return up - base

def center4(wp=W_R4, rr=R0, i=0.09, ktpl=True, krate=None, q_vc=0.0, **kw):
    """q_vc = xac suat P0 duoc Cvlp (amoniac) qua gia bien doi (kich ban co dieu kien; tam dung q_vc=0)."""
    tot = 0.0
    for k, wk in W_R2.items():
        for p, w in wp.items():
            x = val4(k, p, rr, i, ktpl, krate, **kw)
            if p == 'P0' and q_vc:
                x = (1-q_vc)*x + q_vc*val4(k, p, rr, i, ktpl, krate, vc_pass=True, **kw)
            tot += wk*w*x
    return tot

if __name__ == '__main__':
    LIQ_ = 0.10
    r2c = sum(W_R2[k]*val_r2(k) for k in W_R2)
    print(f'r2 tam truoc CK {r2c:.0f} (pin 14.599) | KTPL_RATE {KTPL_RATE:.4f}')
    r2k = sum(W_R2[k]*(val_r2(k)+ktpl_pv(k, env_delta(k, comp=1.0, opex_start=2100, shift=100)[1])) for k in W_R2)
    c3c = center(wp=W_F); c3 = center(wp=W_P)
    print(f'tai lap r3c {c3c:.0f}/{c3c*.9:.0f} (pin 8.557/7.701) | r3 W_P {c3:.0f}/{c3*.9:.0f} (pin 7.836/7.053)')
    steps = [('r3c (W 0,4/0,36/0,24, khong KTPL)', center4(wp=W_F, ktpl=False)),
             ('+ KTPL 10,35% + so du 148,64 (30/9/26) + cong lai nwc', center4(wp=W_F)),
             ('+ trong so ve 0,5/0,3/0,2 = TAM rev4', center4())]
    for n, x in steps: print(f' buoc {n:40s}: truoc {x:.0f} sau {x*.9:.0f}')
    C = center4()
    print(f'\nTAM rev4: truoc CK {C:.0f} | sau CK {C*.9:.0f} | vs r3c sau CK {C*.9/(c3c*.9)-1:+.1%}')
    for p in SCEN:
        x = sum(W_R2[k]*val4(k, p) for k in W_R2); print(f'  thuan {p}: truoc {x:.0f} sau {x*.9:.0f}')
    print(f'  KTPL dong trich tren nen r2 khong du an (co so): {ktpl_pv("base", env_delta("base", comp=1.0, opex_start=2100, shift=100)[1]):+.0f} d/cp | so du -{KTPL_BAL/SH*1000:.0f} | cong lai nwc (co so) +{nwc_addback("base"):.0f}')
    print('\n Do nhay trong so P0 (P50:P100 = 60:40), co KTPL:')
    for p0 in (0, .2, .3, .4, .5, .6):
        x = center4(wp=wgrid(p0)); print(f'  P0={p0:.1f}: truoc {x:.0f} sau {x*.9:.0f}')
    print('\n Kich ban Cvlp (amoniac qua gia bien doi, can sua PPA) - xac suat q trong nhanh P0:')
    for q in (0, .25, .5, 1.0):
        x = center4(q_vc=q); print(f'  q={q:.2f}: truoc {x:.0f} sau {x*.9:.0f} ({x/C-1:+.1%})')
    x = center4(vc_abs=0.0); print(f'  [doi chieu skeptic] VC=0 moi kich ban: truoc {x:.0f} sau {x*.9:.0f} ({x/C-1:+.1%})')
    VN = VC_AMMONIA+VC_POWER
    FX10 = 0.10*89.756813*26388/1000   # ty: VND mat gia 10% tren phan EPC USD (QD 1710; ty gia FS 26.388)
    VARS = {'bo phan du 115 cua VC': dict(vc_abs=VN),
            'opex SCR tu 2032 (QCVN19)': dict(opex_start=2032),
            'san luong 5.000h (vol 0,833)': dict(vol=5000/6000),
            'san luong 6.500h (vol 1,083)': dict(vol=6500/6000),
            f'ty gia EPC USD VND -10% (+{FX10:.0f} ty von chu)': dict(extra_eq=FX10),
            'thay xuc tac SCR 27 ty/nam tu 2033 (uoc luong)': dict(extra_opex=27.0),
            'thay xuc tac SCR 54 ty/nam tu 2033 (uoc luong)': dict(extra_opex=54.0),
            'FC chi bu 10 nam (den 2039)': dict(fc_end=2039),
            'bu cham tu 2033': dict(comp_start=2033),
            'khau hao 18 nam': dict(dep_yrs=18),
            'lai vay 7%': dict(i=0.07), 'lai vay 11%': dict(i=0.11),
            'KTPL 8% / 15%': None, 'KTPL tran co dinh 80 ty/nam': 'kfix'}
    print('\n Bien the (W_R4, co KTPL; truoc / sau CK):')
    xs = []
    for n, kw in VARS.items():
        if kw == 'kfix':
            globals()['KFIX'] = 80.0; x = center4(); globals()['KFIX'] = None
            xs.append(x); print(f'  {n:46s}: {x:6.0f} / {x*.9:6.0f} ({x/C-1:+.1%})'); continue
        if kw is None:
            a = center4(krate=0.08); b = center4(krate=0.15)
            print(f'  KTPL 8%  : {a:6.0f} / {a*.9:6.0f} ({a/C-1:+.1%})'); print(f'  KTPL 15% : {b:6.0f} / {b*.9:6.0f} ({b/C-1:+.1%})'); xs += [a, b]; continue
        x = center4(**kw); xs.append(x); print(f'  {n:46s}: {x:6.0f} / {x*.9:6.0f} ({x/C-1:+.1%})')
    for bp in (-100, -50, 50, 100):
        x = center4(rr=R0+bp/1e4, i=0.09+bp/1e4); print(f'  lai huy dong {bp:+}bp (r va lai vay, beta=1): {x:6.0f} / {x*.9:6.0f} ({x/C-1:+.1%})')
    for b, bp in ((0.5, 100), (0.5, -100)):
        x = center4(rr=R0+b*bp/1e4, i=0.09+bp/1e4); print(f'  beta 0,5, lai huy dong {bp:+}bp: {x:6.0f} / {x*.9:6.0f} ({x/C-1:+.1%})')
    for ke in (0.123, 0.134):
        x = center4(rr=ke); print(f'  Ke dai V2 {ke:.3f}: {x:6.0f} / {x*.9:6.0f} ({x/C-1:+.1%})')
    good = center4(vc_abs=VN, opex_start=2032, i=0.07); bad = center4(comp_start=2033, extra_opex=27.0, vol=5000/6000, i=0.11)
    print(f'  ket hop thuan loi (bo du 115 + opex 2032 + lai 7%): {good:.0f} / {good*.9:.0f} ({good/C-1:+.1%})')
    print(f'  ket hop bat loi (bu cham 2033 + xuc tac 27 + 5.000h + lai 11%): {bad:.0f} / {bad*.9:.0f} ({bad/C-1:+.1%})')
    print(f'\n vung bien the don le sau CK: {min(xs)*.9:.0f}..{max(xs)*.9:.0f}')
    lo, hi = center4(wp=wgrid(.6))*.9, center4(wp=wgrid(0))*.9
    print(f' vung theo trong so P0 0,6..0: {lo:.0f}..{hi:.0f}')
    # V6 hai nen (co so, W_R4)
    dn = sum(W_R4[p]*st.mean(r['dnpat'] for r in env_delta('base', **SCEN[p])[1] if 2030 <= r['y'] <= 2039) for p in SCEN)
    vs = (NORM+dn)*(1-KTPL_RATE)/R0/SH*1000; vl = sum(W_R4[p]*val4('base', p) for p in SCEN)
    import math
    dtxt = f'D = {abs(math.log(vs/vl)):.2f}' if vs > 0 else 'D khong xac dinh (V_ngan <= 0: LNST nen + delta TB 2030-39 am)'
    print(f' V6: V_ngan {vs:.0f} | V_dai co so {vl:.0f} | {dtxt} (ln2 0,69 / ln3 1,10) | NORM {NORM:.0f} dnpat TB 2030-39 {dn:+.0f} ty')
    # dong tien toan cong ty P0 co KTPL
    rows = env_delta('base')[1]; cash = netcash; prev = NPAT_2026; mn = (None, 1e9); c3039 = 0
    for r in rows:
        y = r['y']
        if y > 2047: break
        kt = KTPL_RATE*max(0, prev); prev = npat_base('base', y)+r['dnpat']
        tot = npat_base('base', y)+DA[y]-15+r['fcfe']-kt; cash += tot
        if 2030 <= y <= 2039: c3039 += tot
        if cash < mn[1]: mn = (y, cash)
    print(f' P0 co so co KTPL: cong don 2030-39 {c3039:+.0f} ty; tien thap nhat {mn[1]:.0f} ty nam {mn[0]} (chua co tuc)')
