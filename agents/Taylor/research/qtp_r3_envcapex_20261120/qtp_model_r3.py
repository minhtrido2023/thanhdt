"""QTP DD r3 20/11/2026 (job Taylor_20261120_041936) - them du an nang cap, cai tao HT xu ly khi thai.
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

def env_delta(kind='base', comp=0.0, comp_cap_only=False, i=0.09, rr=R0, opex_start=None,
              shift=0, vc_scale=1.0, detail=False):
    """Delta FCFE (ty/nam) cua du an cong vao kich ban r2 `kind`. comp = ty le bu qua gia (0/0,5/1)
    tu COD (khong hoi to). shift = so nam tri hoan dau tu (quyen chon). Tra (PV d/cp, bang nam)."""
    stop = STOP[kind]; cod = COD+shift
    opex_start = cod if opex_start is None else max(opex_start, cod)
    bal = 0.0; idc_tot = 0.0; rows = []; pv = 0.0
    dep_base = None; carry = 0.0
    for y in YEARS:
        run = 1.0 if y <= stop else 0.0
        d = DISB.get(y-shift, 0.0)
        eq_out = EQ*d; draw = LOAN*d
        idc = 0.0; interest = 0.0; princ = 0.0; dep = 0.0; opex = 0.0; rev = 0.0
        if y < cod:                                   # xay dung: lai vay tra bang tien, von hoa
            idc = i*(bal+0.5*draw); idc_tot += idc; bal += draw
        else:
            if dep_base is None: dep_base = TMDT+idc_tot
            if y < cod+TENOR and bal > 0:
                princ = min(bal, LOAN/TENOR)
            if y >= stop and bal > 0 and y == stop: princ = bal   # dung nha may -> tat toan no
            if y > stop: princ = 0.0
            interest = i*(bal-0.5*princ) if y <= stop else 0.0
            bal -= princ
            dep = dep_base/DEP_YRS if (y < cod+DEP_YRS and y <= stop) else 0.0
            if y >= opex_start: opex = run*(FOM+VC*vc_scale)
            fc = FC_REV if y <= ECON_LIFE_END else 0.0
            rev = run*comp*(fc if comp_cap_only else fc+FOM+VC*vc_scale)
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
W_P = {'P0': 0.50, 'P50': 0.30, 'P100': 0.20}    # (uoc luong, co so du lieu: REPORT_r3 §3) - CHOT TRUOC khi chay

def center(rr=R0, i=0.09, wp=W_P, liq=0.0, **kw):
    tot = 0.0
    for k, wk in W_R2.items():
        v = val_r2(k, rr=rr)
        for p, w in wp.items():
            tot += wk*w*(v+env_delta(k, i=i, rr=rr, **SCEN[p], **kw)[0])
    return tot*(1-liq)

if __name__ == '__main__':
    print(f'NORM {NORM:.1f} NORM_OP {NORM_OP:.1f} netcash {netcash:.1f} | r2 xau/co so/tot',
          round(val_r2('bad')), round(val_r2('base')), round(val_r2('good')))
    r2c = sum(W_R2[k]*val_r2(k) for k in W_R2)
    print(f'r2 tam truoc CK {r2c:.0f} (pin r2 14.599) | sau CK {r2c*0.9:.0f}')
    print(f'Du an: TMDT {TMDT} vay {LOAN} ({LOAN/TMDT:.4f}) von chu {EQ:.1f} | FC {FC_REV:.1f} FOM {FOM} VC {VC} ty/nam'
          f' | tong bu 100% = {FC_REV+FOM+VC:.1f} ty/nam (=169,44 d/kWh x 6.501,57 GWh = {169.44*6501.57/1000:.1f})')

    print('\n=== (1) Dong tien delta theo nam, kich ban r2 CO SO, lai vay 9% (uoc luong) ===')
    for p in SCEN:
        v, rows = env_delta('base', **SCEN[p])
        print(f'-- {p}: PV delta {v:+.0f} d/cp')
        print('  nam | von chu | IDC | lai vay | tra goc | KH moi | opex | bu gia | dThue | dFCFE | dLNST | du no')
        for r in rows:
            if r['y'] <= 2041 or r['y'] in (2047, 2048):
                print(f"  {r['y']} | {r['eq']:6.0f} | {r['idc']:4.0f} | {r['int']:4.0f} | {r['princ']:4.0f} | {r['dep']:4.0f} |"
                      f" {r['opex']:4.0f} | {r['rev']:5.0f} | {r['dtax']:+5.0f} | {r['fcfe']:+6.0f} | {r['dnpat']:+5.0f} | {r['bal']:5.0f}")
    v50c, _ = env_delta('base', comp=0.5, comp_cap_only=True)
    print(f'-- bien the P50 chi bu 50% FC (khong bu opex): {v50c:+.0f} d/cp')

    print('\n=== Tach cau phan PV (co so, P0, 9%) ===')
    v_all = env_delta('base')[0]
    v_noopex = env_delta('base', opex_start=2100)[0]
    print(f' von+lai vay+goc (khong opex): {v_noopex:+.0f} | opex FOM+VC: {v_all-v_noopex:+.0f} | tong {v_all:+.0f}')
    print(f' opex bat dau 2032 thay vi COD (QCVN 19:2024 bat buoc 01/01/2032): {env_delta("base", opex_start=2032)[0]:+.0f}')
    print(f' VC chi 50% (huy dong thap/ amoniac re hon - uoc luong): {env_delta("base", vc_scale=0.5)[0]:+.0f}')

    print('\n=== Lai suat vay (uoc luong 7/9/11%), delta theo kich ban r2 CO SO ===')
    for i in (0.07, 0.09, 0.11):
        print(f' i={i:.0%}: ' + ' | '.join(f'{p} {env_delta("base", i=i, **SCEN[p])[0]:+.0f}' for p in SCEN))
    print(' (xau = dung 2040): ' + ' | '.join(f'{p} {env_delta("bad", **SCEN[p])[0]:+.0f}' for p in SCEN))
    print(' (tot): ' + ' | '.join(f'{p} {env_delta("good", **SCEN[p])[0]:+.0f}' for p in SCEN))

    print('\n=== (2) Tri hoan dau tu 2 nam (COD 2032) - quyen chon ===')
    for p in SCEN:
        a = env_delta('base', **SCEN[p])[0]; b = env_delta('base', shift=2, **SCEN[p])[0]
        print(f' {p}: COD2030 {a:+.0f} | COD2032 {b:+.0f} | gia tri tri hoan {b-a:+.0f} d/cp')
    pen = sum(0.5*npat_base('base', 2032)/(1+R0)**(2032-2027+0.5) for _ in [0])/SH*1000
    print(f' rui ro tre: 1 nam (2032) mat 50% LNST co so (uoc luong) = {-pen:.0f} d/cp')

    print('\n=== (3)(4) Tam moi ===')
    print(' trong so P0/P50/P100 =', W_P)
    c = center(); print(f' TAM r3 truoc CK {c:.0f} | sau CK10% {c*0.9:.0f} | delta vs r2 {c-r2c:+.0f}')
    for p in SCEN:
        x = sum(W_R2[k]*(val_r2(k)+env_delta(k, **SCEN[p])[0]) for k in W_R2)
        print(f'  thuan {p}: truoc CK {x:.0f} | sau CK {x*0.9:.0f}')
    for name, wp in {'0,6/0,3/0,1': {'P0': .6, 'P50': .3, 'P100': .1}, '0,4/0,4/0,2': {'P0': .4, 'P50': .4, 'P100': .2},
                     '1/0/0': {'P0': 1, 'P50': 0, 'P100': 0}}.items():
        x = center(wp=wp); print(f'  trong so {name}: truoc {x:.0f} sau {x*0.9:.0f}')
    for name, kw in {'opex tu 2032': dict(opex_start=2032), 'VC 50%': dict(vc_scale=0.5),
                     'lai vay 7%': dict(i=0.07), 'lai vay 11%': dict(i=0.11)}.items():
        x = center(**kw); print(f'  bien the {name}: truoc {x:.0f} sau {x*0.9:.0f}')
    for p in SCEN:
        dn_p = st.mean(r['dnpat'] for r in env_delta('base', **SCEN[p])[1] if 2030 <= r['y'] <= 2039)
        print(f'  LNST TB 2030-39 {p}: {NORM+dn_p:.0f} ty (EPS {(NORM+dn_p)/SH*1000:.0f}) -> V_ngan {(NORM+dn_p)/R0/SH*1000:.0f}')
    lo = val_r2('bad')+env_delta('bad', comp=0.0)[0]; hi = val_r2('good')+env_delta('good', comp=1.0)[0]
    print(f' vung (xau+P0 .. tot+P100) truoc CK {lo:.0f}..{hi:.0f} | sau CK {lo*0.9:.0f}..{hi*0.9:.0f}')
    for px, d in ((10300, '16/11'), (10200, '19/11 BQ')):
        print(f' gia {px} ({d}) / tam sau CK = {px/(c*0.9):.3f}')
    print(' Do nhay lai huy dong (r va lai vay cung dich 1:1):')
    for bp in (-100, -50, 50, 100):
        x = center(rr=R0+bp/1e4, i=0.09+bp/1e4)
        print(f'  {bp:+}bp: truoc {x:.0f} sau {x*0.9:.0f} ({(x/c-1)*100:+.1f}%)')
    # V_ngan vs V_dai: LNST on dinh sau du an (TB 2030-2039, co so, theo trong so P)
    dn = sum(W_P[p]*st.mean(r['dnpat'] for r in env_delta('base', **SCEN[p])[1] if 2030 <= r['y'] <= 2039) for p in SCEN)
    vs = (NORM+dn)/R0/SH*1000; vl = val_r2('base')+sum(W_P[p]*env_delta('base', **SCEN[p])[0] for p in SCEN)
    import math
    print(f' V_ngan = (LNST chuan {NORM:.0f} {dn:+.0f})/r = {vs:.0f} | V_dai (co so r3) {vl:.0f} | D = {abs(math.log(vs/vl)) if vs>0 else float("nan"):.2f} (ln2=0,69)')

    print('\n=== (6) Co tuc 2027-2032: FCFE nen (co so) vs sau du an, d/cp ===')
    print(' nam | FCFE nen | dFCFE P0 | dFCFE P50 | dFCFE P100 | dLNST P0 | dLNST P100 | LNST nen')
    rr_ = {p: {r['y']: r for r in env_delta('base', **SCEN[p])[1]} for p in SCEN}
    for y in range(2027, 2034):
        base_f = npat_base('base', y)+DA[y]-15
        print(f' {y} | {base_f/SH*1000:5.0f} | {rr_["P0"][y]["fcfe"]/SH*1000:+5.0f} | {rr_["P50"][y]["fcfe"]/SH*1000:+5.0f} |'
              f' {rr_["P100"][y]["fcfe"]/SH*1000:+5.0f} | {rr_["P0"][y]["dnpat"]/SH*1000:+5.0f} | {rr_["P100"][y]["dnpat"]/SH*1000:+5.0f} | {npat_base("base", y)/SH*1000:5.0f}')
    tot_out = sum(rr_['P0'][y]['eq']+rr_['P0'][y]['idc'] for y in (2027, 2028, 2029))
    print(f' Tong von chu + IDC 2027-29 = {tot_out:.0f} ty = {tot_out/SH*1000:.0f} d/cp (tien rong 30/9 sau tam ung {netcash:.0f} ty)')
