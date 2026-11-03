"""DD DRI r4 (job Taylor_20261103_152938, 03/11/2026). MU GIA: khong dung gia/von hoa/P-E cua DRI lam dau vao.
Engine: exec NGUYEN VAN ../../../dri_val_supply_adj_r4_20261027/model.py (ham fv4/fvph, khong sua file cu). Chay:
  python3 -B dri_model_r4.py   (tu thu muc nay)

THAY DOI so voi ban hien hanh (tam 10.500; co so 'tai canh dung ke hoach' 9.078-11.116 @ r thuc 8,74%):
 (1) TAI CANH = DU AN MOI => base NPV 0. Kiem nghia vu to nhuong: BCTN 2024/2025 chi ghi tai canh "phu hop voi hop dong
     to nhuong dat va chat luong vuon cay" / "vuon cay kem hieu qua, phu hop voi thoi han hop dong to nhuong" (BCTN25 tr ~8,
     ~60; BCTN24 ~tr 60); legal-vn 03/11: luat Lao (Luat KK Dau tu 14/NA 2016 tran 50 nam; Luat Dat dai 70/NA 2019) chi co
     nghia vu chung "su dung dat dung muc dich, khong bo hoang", KHONG thay dieu khoan buoc tai canh; hop dong 01616/KD/DDT4
     (30/03/2016) khong cong khai => CHUA XAC MINH. => khong co co so ban lanh dao bi BUOC chiu NPV am.
     Base = tai san HIEN HUU (vuon dang cao, het doi theo lop tuoi L_tap, go thanh ly cuoi doi) + du an tai canh/ giai doan 2
     / sau rieng / lien doanh go = NPV 0 (phan con phai chi doi ung bang gia tri tuong duong) + phan DA CHI = XDCB do dang
     72,71 ty [BCTC3 CDKT ma 252, 30/09/2026] theo gia von.
     Kich ban co xac suat (KHONG vao base): 'tai canh bi buoc theo dieu kien su dung dat + kinh te du an nhu gia dinh cu'
     (capex 172,6 tr/ha, nang suat cay moi 1,69) = cau hinh T1 cu; xac suat chu quan 20%.
 (2) GIA CAO SU CHUAN HOA CHU KY (tai san hien huu): RSS3 World Bank thang (data/rubber_monthly_snapshot_20261103.csv,
     2006-04..2026-09) quy ve USD 2025 bang CPI-U My (FRED CPIAUCSL, data/fred_cpiaucsl_20261103.csv).
     Muc giua chu ky DANG KY TRUOC: tam = TB thuc 2013-01..2026-09 (sau sieu chu ky 2010-11, gom >=2 chu ky day 2015-16/2020
     va dinh 2017/2021/2024/2026); thap = trung vi thuc cung cua so; cao = TB thuc 2006-04..2026-09. Duong 2027-28 giu doc
     nganh doc lap cua Bobby (PEAK 60 / MID 40, vn_sector_read_rubber_20261027.md).
 (3) r = 13,5% danh nghia tai diem neo lai huy dong 12T hieu dung 7,40% (CCTG 12M 02/11/2026; deposit_rate_vn.
     macro_killswitch_a_status() 03/11/2026). r(dep) = 13,5% + beta*(dep - 7,40%), beta 1 (do nhay 0,5). Dong tien gia
     thuc 2025 (khung engine) => r thuc = (1+r)/(1+3%) - 1. Truc r cua luoi: {11,5; 13,5; 15,5}%.
 (4) Cac cau phan khac giu nguyen engine (co nguon BCTC3): tien rong, Dakruco 50%, cat 15% tien gui Lao, quy du phong Lao,
     khau tru tai nguon, KTPL, Q4/2026 Base, ton kho 1.717 t. Dat: to nhuong, khong so huu => 0 (doi xung: khong cong gia tri
     dat, khong tru). Gia han to nhuong sau 2054: 0 o base (doi xung).
LUOI (dang ky truoc): mid {thap .25, tam .5, cao .25} x L_tap {22 .25, 27 .5, 32 .25} x r {11,5 .25; 13,5 .5; 15,5 .25} = 27 o,
  trong so tich; thang P10/P25/P50/P75/P90 co trong so. Tam = o (mid tam, L27, r 13,5).
NGUONG (dang ky truoc, ap tren thang SAU chiet khau thanh khoan 5 ty, Y=1): RE <= P10; RE CO DIEU KIEN P10-P25; HOP LY P25-P75;
  NGHIENG DAT P75-P90; DAT >= P90.
THANH KHOAN (dang ky truoc, tinh SAU khoa o liquidity_r4.py): d(Q) = Y*sigma_ngay*sqrt(Q/ADV_trung_vi) (luat can bac hai, Y 0,5/1/1,5),
  sigma = do lech chuan log-return Close 250 phien, ADV = trung vi Price*Volume 250 phien (tav2_bq.ticker); kiem cheo Amihud,
  so phien thoat o 10/15/20% ADV; free float ~55% (Dakruco 45%, BCTN 2025).
"""
import os, io, csv, json, contextlib, itertools, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.path.abspath(os.path.join(HERE, '../../../dri_val_supply_adj_r4_20261027/model.py'))
ns = {'__file__': ENG, '__name__': 'eng'}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(open(ENG, encoding='utf-8').read(), ENG, 'exec'), ns)
fvph, CEN, SH, build3, D_V = ns['fvph'], ns['CEN'], ns['SH'], ns['build3'], ns['D_V']
R_ANCHOR, DEP_ANCHOR, PI = 0.135, 0.0740, ns['PI']
def r_of(dep, beta=1.0): return R_ANCHOR + beta*(dep - DEP_ANCHOR)
CIP = 72.712702447                                    # XDCB do dang 30/09/2026, ty [BCTC3 CDKT 252]
out = {}

# ---------- 0. SELFCHECK: tai lap so cu o r 12% ----------
CEN['r'] = 0.12
old_T1 = [fvph(m, 2029, 27) for m in (1.97, 2.18)]
old_D = [fvph(m, 2029, 27, R_on=False, new_on=False) for m in (1.97, 2.18)]
print("0) SELFCHECK engine cu @ r 12%: T1 (tai canh day du) " + " / ".join(f"{v:,.0f}" for v in old_T1)
      + " | D (khong thanh ly/tai canh) " + " / ".join(f"{v:,.0f}" for v in old_D))
assert [round(v) for v in old_T1] == [9078, 11116] and [round(v) for v in old_D] == [13096, 15172], "KHONG tai lap engine cu"
print("   PASS (9.078/11.116 va 13.096/15.172 khop bao cao cu)")

# ---------- 1. Chuan hoa chu ky RSS3 thuc ----------
cpi = {r['observation_date'][:7]: float(r['CPIAUCSL']) for r in csv.DictReader(open(os.path.join(HERE, 'data/fred_cpiaucsl_20261103.csv'))) if r['CPIAUCSL']}
cpi['2025-10'] = (cpi['2025-09'] + cpi['2025-11'])/2                # FRED trong 2025-10 (khong cong bo) => noi suy tuyen tinh
rss = [(m, float(p)) for m, p in csv.reader(open(os.path.join(HERE, 'data/rubber_monthly_snapshot_20261103.csv'))) if m != 'month']
c25 = st.mean([cpi[f'2025-{i:02d}'] for i in range(1, 13)])
real = {m: p*c25/cpi[m] for m, p in rss if m in cpi}
w13 = [v for m, v in real.items() if '2013-01' <= m <= '2026-09']; w06 = [v for m, v in real.items() if '2006-04' <= m <= '2026-09']
MID = {'thap': st.median(w13), 'tam': st.mean(w13), 'cao': st.mean(w06)}
nom13 = [p for m, p in rss if '2013-01' <= m <= '2026-09']
yr = {y: st.mean([v for m, v in real.items() if m.startswith(str(y))]) for y in range(2007, 2026)}
print(f"\n1) RSS3 THUC (USD 2025/kg; CPI-U TB2025 {c25:.2f}): TB 2013-26 {MID['tam']:.3f} | trung vi 2013-26 {MID['thap']:.3f} | TB 2006-26 {MID['cao']:.3f}"
      f" | (danh nghia TB 2013-26 {st.mean(nom13):.3f}; TB2025 {ns['rss25']:.3f}; Q3/26 {ns['rssq3']:.3f})")
print("   TB nam thuc: " + " ".join(f"{y}:{v:.2f}" for y, v in yr.items()))
print(f"   phan vi gia Q3/26 trong chuoi thuc 2013-26: {sum(v <= ns['rssq3'] for v in w13)/len(w13):.0%}")
out['rss3_real'] = {k: round(v, 4) for k, v in MID.items()}
out['rss3_real_yearly'] = {y: round(v, 3) for y, v in yr.items()}

# ---------- 2. Gia tri ----------
def base(mid, L=27, r=R_ANCHOR):
    CEN['r'] = r
    return fvph(mid, 2029, L, R_on=False, new_on=False) + CIP*1e9/SH
def forced(mid, L=27, r=R_ANCHOR):
    CEN['r'] = r
    return fvph(mid, 2029, L)                          # T1 cu: thanh ly 4.081 ha + trong lai, capex 172,6 tr/ha (khong cong XDCB)
C = base(MID['tam'])
print(f"\n2) TAM (mid {MID['tam']:.3f}, L27, r 13,5%): {C:,.0f} d/cp  (trong do XDCB gia von {CIP*1e9/SH:,.0f})")
CEN['r'] = R_ANCHOR
parts = ns['fv4']("PEAK", MID['tam'], CEN, V=build3(2029, 27, R_on=False, new_on=False)[0], farea=True, addD=D_V,
                  wood=ns['wood3'](build3(2029, 27, R_on=False, new_on=False)[1]))
F = forced(MID['tam'])
print(f"   kich ban 'tai canh bi buoc, kinh te nhu gia dinh cu' (T1): {F:,.0f} | chenh {F-C:+,.0f}")
# cau noi tu ban cu
CEN['r'] = 0.12
b0 = fvph(1.97, 2029, 27); b1 = fvph(1.97, 2029, 27, R_on=False, new_on=False); b2 = b1 + CIP*1e9/SH
CEN['r'] = R_ANCHOR
b3 = fvph(1.97, 2029, 27, R_on=False, new_on=False) + CIP*1e9/SH
b4 = C
print(f"   CAU NOI (mid 1,97 -> chuan hoa): T1 cu r12% {b0:,.0f} | tai canh NPV0 {b1-b0:+,.0f} | XDCB gia von {b2-b1:+,.0f} | r 12->13,5% {b3-b2:+,.0f}"
      f" | mid 1,97->{MID['tam']:.3f} {b4-b3:+,.0f} => {b4:,.0f}")
out['bridge'] = dict(old_T1_mid197_r12=round(b0), npv0_replant=round(b1-b0), cip_book=round(b2-b1), r_to_135=round(b3-b2), mid_to_norm=round(b4-b3), center=round(b4))

# ---------- 3. Luoi 27 o ----------
WM = {'thap': .25, 'tam': .5, 'cao': .25}; WL = {22: .25, 27: .5, 32: .25}; WR = {0.115: .25, 0.135: .5, 0.155: .25}
cells = []
for (mk, wm), (L, wl), (r, wr) in itertools.product(WM.items(), WL.items(), WR.items()):
    v = base(MID[mk], L, r); cells.append(dict(mid=mk, L=L, r=r, w=wm*wl*wr, v=v))
def wq(xs, q):
    xs = sorted(xs, key=lambda c: c['v']); acc = 0
    for c in xs:
        acc += c['w']
        if acc >= q - 1e-12: return c['v']
SCALE = {f'P{int(q*100)}': wq(cells, q) for q in (.10, .25, .50, .75, .90)}
print("\n3) THANG (luoi 27 o, trong so): " + " / ".join(f"{k} {v:,.0f}" for k, v in SCALE.items())
      + f" | min {min(c['v'] for c in cells):,.0f} max {max(c['v'] for c in cells):,.0f} | TB co trong so {sum(c['v']*c['w'] for c in cells):,.0f}")
for ax, key, vals in [('mid', 'mid', list(WM)), ('L_tap', 'L', list(WL)), ('r', 'r', list(WR))]:
    print(f"   mot truc quanh tam [{ax}]: " + " | ".join(
        f"{k}: {base(MID[k] if key=='mid' else MID['tam'], k if key=='L' else 27, k if key=='r' else R_ANCHOR):,.0f}" for k in vals))
with open(os.path.join(HERE, 'grid_r4.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['mid', 'L', 'r', 'w', 'v']); w.writeheader(); [w.writerow({**c, 'v': round(c['v'])}) for c in cells]

# ---------- 4. Kich ban co xac suat ----------
P_FORCED = 0.20
EXP = (1-P_FORCED)*C + P_FORCED*F
print(f"\n4) KY VONG co xac suat (chu quan): 80% base {C:,.0f} + 20% tai canh bi buoc {F:,.0f} = {EXP:,.0f}")
forced_grid = {k: forced(MID[k]) for k in MID}
print("   T1 theo mid thap/tam/cao (L27, r13,5): " + " / ".join(f"{v:,.0f}" for v in forced_grid.values()))
TROUGH = None
CEN['r'] = R_ANCHOR
tr = ns['fv4']('TROUGH', MID['tam'], CEN, V=build3(2029, 27, R_on=False, new_on=False)[0], farea=True, addD=D_V,
               wood=ns['wood3'](build3(2029, 27, R_on=False, new_on=False)[1])) + CIP*1e9/SH
print(f"   stress duong day RSS3 2027=2028=1,60 (tam con lai): {tr:,.0f}")
print(f"   (doi chieu) giu vuon qua L27 (L99 - khong het doi, khong tai canh): {base(MID['tam'], 99):,.0f}")

# ---------- 5. Do nhay lai huy dong ----------
print("\n5) DO NHAY LAI HUY DONG 12T (diem neo 7,40% -> r 13,5%)")
sens = {}
for beta in (1.0, 0.5):
    row = {}
    for bp in (-100, -50, 0, 50, 100):
        dep = DEP_ANCHOR + bp/1e4; v = base(MID['tam'], 27, r_of(dep, beta)); row[bp] = v
    sens[beta] = row
    print(f"   beta {beta}: " + " | ".join(f"{bp:+d}bp (r {r_of(DEP_ANCHOR+bp/1e4, beta):.2%}): {v:,.0f} ({v/C-1:+.1%})" for bp, v in row.items()))
out.update(center=C, forced=F, expected=EXP, p_forced=P_FORCED, scale=SCALE, mids=MID, trough_stress=tr,
           dep_sens={str(b): {str(k): v for k, v in r.items()} for b, r in sens.items()}, cip_bn=CIP,
           r_anchor=R_ANCHOR, dep_anchor=DEP_ANCHOR, real_r=(1+R_ANCHOR)/(1+PI)-1)
json.dump(out, open(os.path.join(HERE, 'dri_model_r4_out.json'), 'w'), indent=1, default=float)
print("\nOUT -> dri_model_r4_out.json, grid_r4.csv")
