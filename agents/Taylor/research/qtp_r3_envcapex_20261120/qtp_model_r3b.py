"""QTP DD r3 20/11/2026 (job Taylor_20261120_041936) - them du an nang cap, cai tao HT xu ly khi thai.
r3b: them tham so bien the (stop_ov, comp_start, comp_k, dep_yrs, tmdt, vc_abs), tach VC, trong so W_F.
Nen = r2 (agents/Taylor/research/dd_QTP_20261117/model/qtp_model.py) - giu nguyen, chi CONG delta du an.
So nguon du an = FS goc (src_fs/, CBTT VNDirect 11/06/2026, BC tham tra PECC1 so 2985/TVD1-NDNLM 22/5/2026):
  TMDT truoc VAT 3.484,88 ty (sau VAT 3.799,19); O&M co dinh 102,01 ty/nam; dien-nuoc-hoa chat 470,29 ty/nam
  (amoniac 12.045.120 kg x 26.350 d = 317,4 ty); dien thuong pham 6.501,57 GWh/nam;
  gia tang them de nghi 169,44 d/kWh = FC 81,42 + O&M co dinh 15,69 + bien doi 72,33; FIRR 11%; tuoi tho kinh te 18 nam.
Vay 2.787,9 ty = 80% (QD 917 15/6/2026; QD 1490 21/9/2026: BIDV 1.787,9 + VCB 1.000). EPC 89.756.813 USD + 901,8 ty
  (QD 1710 6/10/2026, 38 thang). LAI SUAT / KY HAN: KHONG co trong van ban nao doc duoc -> (uoc luong).
Chay: python3 qtp_model_r3.py   (in so; khong ghi file)."""
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
              dep_yrs=None, tmdt=None, vc_abs=None):
    """Delta FCFE (ty/nam) cua du an cong vao kich ban r2 `kind`. comp = ty le bu qua gia tu comp_start
    (mac dinh COD; khong hoi to). shift = tri hoan dau tu. stop_ov = nam dung nha may (quyen tu bo).
    comp_k = he so gia bu (164,25/169,44). dep_yrs = so nam khau hao. tmdt = TMDT thay the (vay 80%).
    vc_abs = chi phi dien-nuoc-hoa chat tuyet doi (ty/nam) thay VC*vc_scale. Tra (PV d/cp, bang nam)."""
    stop = STOP[kind] if stop_ov is None else stop_ov; cod = COD+shift
    T = TMDT if tmdt is None else tmdt; L = 0.8*T if tmdt is not None else LOAN; E = T-L
    dy = DEP_YRS if dep_yrs is None else dep_yrs
    vc_use = VC*vc_scale if vc_abs is None else vc_abs
    fc_rev_k = FC_REV*comp_k; fom_k = FOM*comp_k; vc_k = vc_use*comp_k
    opex_start = cod if opex_start is None else max(opex_start, cod)
    cstart = cod if comp_start is None else max(comp_start, cod)
    bal = 0.0; idc_tot = 0.0; rows = []; pv = 0.0
    dep_base = None; carry = 0.0
    for y in YEARS:
        run = 1.0 if y <= stop else 0.0
        d = DISB.get(y-shift, 0.0)
        eq_out = E*d; draw = L*d
        idc = 0.0; interest = 0.0; princ = 0.0; dep = 0.0; opex = 0.0; rev = 0.0
        if y < cod:                                   # xay dung: lai vay tra bang tien, von hoa
            idc = i*(bal+0.5*draw); idc_tot += idc; bal += draw
        else:
            if dep_base is None: dep_base = T+idc_tot
            if y < cod+TENOR and bal > 0:
                princ = min(bal, L/TENOR)
            if y >= stop and bal > 0 and y == stop: princ = bal   # dung nha may -> tat toan no
            if y > stop: princ = 0.0
            interest = i*(bal-0.5*princ) if y <= stop else 0.0
            bal -= princ
            dep = dep_base/dy if (y < cod+dy and y <= stop) else 0.0
            if y >= opex_start: opex = run*(FOM+vc_use)
            fc = fc_rev_k if y <= ECON_LIFE_END else 0.0
            if y >= cstart: rev = run*comp*(fc if comp_cap_only else fc+fom_k+vc_k)
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

if __name__ == '__main__':
    r2c = sum(W_R2[k]*val_r2(k) for k in W_R2)
    print(f'r2 tam truoc CK {r2c:.0f} (pin 14.599)')
    print(f'VC tach: amoniac {VC_AMMONIA:.1f} + dien tu dung {VC_POWER:.1f} + du CHUA thuyet minh {VC_REST:.1f} = {VC_AMMONIA+VC_POWER+VC_REST:.2f}')
    VC_NOREST = VC_AMMONIA+VC_POWER
    base0 = env_delta('base')[0]
    print(f'P0/co so (r3 tai lap) {base0:+.0f}; bo phan du 115 (vc_abs={VC_NOREST:.1f}): {env_delta("base", vc_abs=VC_NOREST)[0]:+.0f}')
    c_r3 = center(wp=W_P); c_nr = center(wp=W_P, vc_abs=VC_NOREST)
    print(f'TAM r3 (0,5/0,3/0,2) truoc {c_r3:.0f} sau {c_r3*.9:.0f} | bo du 115: truoc {c_nr:.0f} sau {c_nr*.9:.0f}')

    print('\n=== (2) Quyen tu bo: dung cuoi 2031 (hop dong EPC da ky -> CHI nhan nhan, khong vao tam) ===')
    for kind in ('base',):
        for p in SCEN:
            a = val_r2(kind)+env_delta(kind, **SCEN[p])[0]
            b = val_r2(kind, stop=2031)+env_delta(kind, stop_ov=2031, **SCEN[p])[0]
            print(f' {kind}/{p}: chay den STOP {a:.0f} | dung 2031 {b:.0f} | chenh {b-a:+.0f} d/cp truoc CK')
    a = val_r2('base')+env_delta('base')[0]
    b = val_r2('base', stop=2031)+env_delta('base', stop_ov=2031)[0]
    print(f' (so voi quyen tu bo 2031, P0 CO SO: {b:.0f} d/cp truoc CK -> sau CK {b*.9:.0f}; cap tren cho P0)')
    print(f' r2 thuan dung 2031 (khong du an) {val_r2("base", stop=2031):.0f} vs r2 co so {val_r2("base"):.0f}')

    print('\n=== (2b) Dong tien TOAN CONG TY o P0, co so (ty) ===')
    rows = env_delta('base')[1]; cash = netcash; mn = (None, 1e9); cum = 0; cum3039 = 0
    print(' nam | FCFE nen | dFCFE P0 | FCFE toan cty | tien rong luy ke (chua tra co tuc)')
    for r in rows:
        y = r['y']
        if y > 2041: break
        bf = npat_base('base', y)+DA[y]-15; tot = bf+r['fcfe']; cash += tot
        if 2030 <= y <= 2039: cum3039 += tot
        if cash < mn[1]: mn = (y, cash)
        print(f' {y} | {bf:6.0f} | {r["fcfe"]:+6.0f} | {tot:+6.0f} | {cash:7.0f}')
    print(f' tien rong dau ky (30/9/26) {netcash:.0f}; cong don FCFE toan cty 2030-39 {cum3039:+.0f} ty; tien thap nhat {mn[1]:.0f} ty nam {mn[0]}')
    neg = [r['y'] for r in rows if r['y']>=2027 and netcash+sum((npat_base('base', x['y'])+DA[x['y']]-15+x['fcfe']) for x in rows if x['y']<=r['y'])<0]
    print(f' nam dau tien tien rong < 0 (CHUA tra co tuc): {neg[0] if neg else "khong"}')
    print(' P50: ', end='')
    rows50 = env_delta('base', comp=0.5)[1]; cash = netcash; mn5 = (None, 1e9)
    for r in rows50:
        cash += npat_base('base', r['y'])+DA[r['y']]-15+r['fcfe']
        if r['y'] <= 2047 and cash < mn5[1]: mn5 = (r['y'], cash)
    print(f'tien thap nhat {mn5[1]:.0f} ty nam {mn5[0]}')

    print('\n=== (3) Do nhay trong so (truoc/sau CK; P50:P100 = 60:40) ===')
    for p0 in (0, .2, .3, .4, .5):
        x = center(wp=wgrid(p0)); print(f' P0={p0:.1f}: truoc {x:.0f} sau {x*.9:.0f}   w={ {k: round(v,2) for k,v in wgrid(p0).items()} }')
    cf = center(wp=W_F)
    print(f'\n TAM r3b (W_F {W_F}): truoc CK {cf:.0f} | sau CK {cf*.9:.0f} | delta vs r2 {cf-r2c:+.0f} | vs r3 {cf-c_r3:+.0f}')
    for p in SCEN:
        x = sum(W_R2[k]*(val_r2(k)+env_delta(k, **SCEN[p])[0]) for k in W_R2)
        print(f'  thuan {p}: truoc {x:.0f} sau {x*.9:.0f}')
    print('\n Bien the tren W_F (truoc CK / sau CK):')
    VARS = {'bo phan du 115 cua VC': dict(vc_abs=VC_NOREST),
            'opex tu 2032 (QCVN19)': dict(opex_start=2032),
            'bu cham tu 2033': dict(comp_start=2033),
            'P50 chi bu FC': None,
            'khau hao 18 nam': dict(dep_yrs=18),
            'TMDT 3.300 (vay 80%)': dict(tmdt=3300.0),
            'gia bu 164,25 d/kWh': dict(comp_k=164.25/169.44),
            'lai vay 7%': dict(i=0.07), 'lai vay 11%': dict(i=0.11),
            'VC 50%': dict(vc_scale=0.5)}
    for name, kw in VARS.items():
        if kw is None:
            tot = 0.0
            for k, wk in W_R2.items():
                v = val_r2(k)
                for p, w in W_F.items():
                    d = env_delta(k, comp=SCEN[p]['comp'], comp_cap_only=(p == 'P50'))[0]
                    tot += wk*w*(v+d)
            x = tot
        else:
            x = center(wp=W_F, **kw)
        print(f'  {name:26s}: {x:6.0f} / {x*.9:6.0f}  ({x/cf-1:+.1%})')
    # P0 chi so (cho bang bien the tren tung kich ban)
    print('\n Bien the tren tung kich ban (co so r2, truoc CK, delta PV):')
    for name, kw in VARS.items():
        if kw is None: continue
        print(f'  {name:26s}: ' + ' | '.join(f'{p} {env_delta("base", **SCEN[p], **kw)[0]:+.0f}' for p in SCEN))
    print(f'  P50 chi bu FC: {env_delta("base", comp=.5, comp_cap_only=True)[0]:+.0f}')
    # vung
    lo = min(center(wp=wgrid(p0)) for p0 in (0, .5))*.9; hi = max(center(wp=wgrid(p0)) for p0 in (0, .5))*.9
    print(f'\n vung theo trong so P0 0..0,5: sau CK {lo:.0f}..{hi:.0f}; theo bien the: ', end='')
    xs = []
    for name, kw in VARS.items():
        xs.append(center(wp=W_F, **kw)*.9 if kw else None)
    xs = [v for v in xs if v is not None]+[cf*.9]
    print(f'{min(xs):.0f}..{max(xs):.0f}')
    for px in (10200, 10300):
        print(f' gia {px} / tam sau CK = {px/(cf*.9):.3f}; / nguong tren vung bien the {px/max(xs):.3f}')
    for name, wp in {'P0 .4': W_F, 'P0 .5': W_P}.items():
        pass
    # V_ngan
    dn = sum(W_F[p]*st.mean(r['dnpat'] for r in env_delta('base', **SCEN[p])[1] if 2030 <= r['y'] <= 2039) for p in SCEN)
    vs = (NORM+dn)/R0/SH*1000; vl = val_r2('base')+sum(W_F[p]*env_delta('base', **SCEN[p])[0] for p in SCEN)
    print(f' V_ngan (W_F) {vs:.0f} | V_dai co so {vl:.0f}')
    print('\n Do nhay lai huy dong (W_F):')
    for bp in (-100, 100):
        x = center(wp=W_F, rr=R0+bp/1e4, i=0.09+bp/1e4); print(f'  {bp:+}bp: truoc {x:.0f} sau {x*.9:.0f} ({x/cf-1:+.1%})')

    print('\n=== (4) Bo sung: quyen tu bo co dieu kien, tien rong co co tuc, bien the ket hop ===')
    opt = 0.0; plain = 0.0
    for p, w in W_F.items():
        a = val_r2('base')+env_delta('base', **SCEN[p])[0]
        b = val_r2('base', stop=2031)+env_delta('base', stop_ov=2031, **SCEN[p])[0]
        opt += w*max(a, b); plain += w*a
    print(f' (chi cho co so) plain {plain:.0f} | co quyen tu bo 2031 (chon sau khi biet P) {opt:.0f} | +{opt-plain:.0f} truoc CK = +{(opt-plain)*.9:.0f} sau CK [KHONG vao tam]')
    for dps in (0, 500, 900):
        cash = netcash; first = None
        for r in env_delta('base')[1]:
            y = r['y']
            if y > 2047: break
            cash += npat_base('base', y)+DA[y]-15+r['fcfe']-dps*SH/1000
            if cash < 0 and first is None: first = y
        print(f' P0, co tuc {dps} d/cp/nam (tu 2027): tien rong am dau tien nam {first}')
    for name, kw in {'bo du 115 + opex tu 2032': dict(vc_abs=VC_NOREST, opex_start=2032),
                     'bo du 115 + opex 2032 + lai 7%': dict(vc_abs=VC_NOREST, opex_start=2032, i=0.07),
                     'bu cham 2033 + khau hao 18 + lai 11%': dict(comp_start=2033, dep_yrs=18, i=0.11)}.items():
        x = center(wp=W_F, **kw); print(f' ket hop [{name}]: truoc {x:.0f} sau {x*.9:.0f}')
