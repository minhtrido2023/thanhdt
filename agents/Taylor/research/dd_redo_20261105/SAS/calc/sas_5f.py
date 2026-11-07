"""SAS 5F addendum r2 (job Taylor_20261107_125216; r1 = sas_5f_r1.py). Chay: $DNA_PYEXE -I -B sas_5f.py > sas_5f_out.txt
Tai lap model_r2.py (WIDE = hien hanh, phai khop tam 31,066) + ban CHAT-3C: RONIC=Ke (doi xung moi o g) va GPM ve TB chu ky nganh.
GPM: BQ tav2_bq.ticker_financial 07/11/2026; GPM_P0 la TTM => dong Q4 = GPM nam (dung thang, khong tinh lai); 9T/2026 = BCTC 1.556,1/2.333,1.
r2: muc tieu NPM VAN HANH = NPM chu ky (gom thu nhap TC) - f, f = thu nhap TC sau thue / DT (pp)."""
import sys, os, json, itertools
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', '..', '_common_020021'))
import r2lib as R2
L = R2.L
SH = 133.481310
dep, dep_src = L.current_dep(); R = L.r_of(dep)
Q = R2.liq2('SAS'); PX = Q['price']; LD = Q['disc_ref']; LDS = Q['disc_sleeve_max']
CASH, HTM = 280.717512019, 664.486706849
EMP_PAY, BONUS_FUND, TAX_PAY = 141.169135385, 99.711533217, 50.247155609
LT_INV, LT_RECV = 253.830133419, 242.036924823
NP_9M, FIN_REV_9M, FIN_EXP_9M = 539.458668050, 194.955804947, 6.671156612
EPS_RATIO = 0.883
XCASH = CASH + HTM - EMP_PAY - BONUS_FUND - TAX_PAY
N0 = (NP_9M - (FIN_REV_9M - FIN_EXP_9M) * 0.80) * 4 / 3
# BQ GPM_P0 dong Q4 (= GPM nam, TTM) %, va DT nam (ty dong; SAS = tong Revenue_P0 4 quy; AST = tong Revenue_P0..P3 tai Q4 nhu r1)
SAS_GPM = {2016: (45.13, 2089), 2017: (47.11, 2369), 2018: (45.58, 2659), 2019: (47.73, 2895), 2020: (48.52, 919), 2021: (56.18, 321), 2022: (52.44, 1401), 2023: (54.10, 2581), 2024: (59.15, 2907), 2025: (62.97, 3316)}
AST_GPM = {2017: (50.46, 659), 2018: (53.89, 865), 2019: (54.17, 1141), 2020: (41.75, 359), 2021: (24.89, 155), 2022: (52.92, 604), 2023: (58.14, 1100), 2024: (61.14, 1330), 2025: (63.47, 1727)}
GPM_9M, REV_9M = 100 * 1556.1 / 2333.1, 2333.168945119   # BCTC 9T/2026
REV_ANN = REV_9M * 4 / 3
def wavg(ds, yrs): return sum(ds[y][0] * ds[y][1] for y in yrs) / sum(ds[y][1] for y in yrs)
YRS = range(2017, 2026)
pool = {y: (wavg({1: SAS_GPM[y], 2: AST_GPM[y]}, (1, 2)), SAS_GPM[y][1] + AST_GPM[y][1]) for y in YRS}
TGT = {"nganh_SAS+AST_2017-25": wavg(pool, YRS), "SAS_rieng_2016-25": wavg(SAS_GPM, SAS_GPM), "AST_rieng_2017-25": wavg(AST_GPM, AST_GPM),
       "AST_GPM_P0_26Q3": 64.16, "peer_rong_trung_vi_26Q3": 47.34, "peer_rong_TB_26Q3": (64.16 + 47.34 + 77.25 + 30.62 + 18.32) / 5}  # BQ GPM_P0 26Q3 AST/NCT/SCS/SGN/MAS
def adj_of(t): return REV_ANN * (t - GPM_9M) / 100 * 0.80   # (a) LN sau thue thay doi khi GPM ve t, SG&A giu nguyen (CAN TREN muc cat)
def adj_prop(t): return N0 * (t / GPM_9M - 1)                 # (c) SG&A co gian theo LN gop (CAN DUOI muc cat)
# (b) NPM TTM (BQ NP_P0..3/Revenue_P0..3, gom thu nhap TC) gop SAS+AST, bo 2020-21 (COVID dong cua), co trong so DT
SAS_NP = {2017: 290, 2018: 341, 2019: 373, 2022: 210, 2023: 294, 2024: 430, 2025: 695}
AST_NP = {2017: 147, 2018: 161, 2019: 191, 2022: 23, 2023: 116, 2024: 149, 2025: 250}
NPY = SAS_NP.keys()
NPM_POOL = 100 * (sum(SAS_NP.values()) + sum(AST_NP.values())) / (sum(SAS_GPM[y][1] for y in NPY) + sum(AST_GPM[y][1] for y in NPY))
NPM_SAS = 100 * sum(SAS_NP.values()) / sum(SAS_GPM[y][1] for y in NPY); NPM_AST = 100 * sum(AST_NP.values()) / sum(AST_GPM[y][1] for y in NPY)
NPM_9M = 100 * NP_9M / REV_9M                # gom thu nhap TC (chi de doi chieu)
NPM_OP = 100 * N0 / REV_ANN                   # bien van hanh cua N0 (da LOAI thu nhap TC sau thue)
FIN_9M25, REV_9M25 = 58.2, 764.2 + 770.2 + 804.9   # DT TC 9T/25 (cot so sanh BCTC Q3/26); DT 9T/25 BQ
F_PROXY_9M25 = 0.80 * FIN_9M25 / REV_9M25 * 100   # can tren: chua tru CP TC 9T/25
F_2025_FY = 0.80 * (FIN_9M25 + 139.80) / 3315.5 * 100   # DT TC Q4/25 139,8 [web, thitruongtaichinhtiente]; co the gom khoan mot lan
def adj_npm(t, f=0.0): return REV_ANN * ((t - f) - NPM_OP) / 100   # N0 la van hanh => muc tieu cung phai la van hanh
print(f"N0 {N0:.1f}; DT nam hoa 9T {REV_ANN:,.0f}; GPM 9T {GPM_9M:.2f}%; r {R:.2%}; gia {PX:,.0f}; CK 5ty {LD:.2%} sleeve40 {LDS:.2%}")
for k, t in TGT.items(): print(f"  muc tieu GPM {k}: {t:.2f}% -> dieu chinh LN sau thue {adj_of(t):+.1f} ty/nam ({adj_of(t)/N0:+.1%} N0)")

def val(delta, n0, r, g, adj=0.0, ronic_ke=False, adj27=0.5):
    e27 = (n0 + adj * adj27) * (1 + delta / 2); e28 = (n0 + adj) * (1 + delta)
    tv = e28 / r if ronic_ke else e28 / (r - g)       # RONIC=Ke: V=E(1-g/RONIC)/(r-g)=E/r, nam 1 giu quy uoc r2
    return (XCASH + LT_INV + LT_RECV + (e27 / (1 + r) + tv / (1 + r)) * EPS_RATIO) / SH * 1000
DS = (-0.55, -0.40, -0.25, -0.10, 0.05); WD = (0.1, 0.2, 0.4, 0.2, 0.1)
NS = (N0 * 0.9, N0, N0 * 1.1); RS = (R - 0.01, R, R + 0.01); GS = (0.02, 0.03, 0.04); W3 = (0.25, 0.5, 0.25)
def run(**kw):
    v, w = [], []
    for (d, wd), (n, wn), (rr, wr), (g, wg) in itertools.product(zip(DS, WD), zip(NS, W3), zip(RS, W3), zip(GS, W3)):
        v.append(val(d, n, rr, g, **kw)); w.append(wd * wn * wr * wg)
    s = R2.stats(v, w, PX, LD); s['label'] = R2.label(PX, s)
    s['label_sleeve40'] = 'DUOI vung (<P10)' if PX < s['p10_pre'] * (1 - LDS) else ('TREN vung (>P90)' if PX > s['p90_pre'] * (1 - LDS) else 'TRONG vung')
    s['center_sleeve40'] = s['center_pre'] * (1 - LDS); s['central_post'] = val(-0.25, N0, R, 0.03, **kw) * (1 - LD)
    return s
print(f"NPM 9T/2026 gom TC {NPM_9M:.2f}% | NPM van hanh N0 {NPM_OP:.2f}% | NPM chu ky (bo 2020-21, gom TC) gop {NPM_POOL:.2f}% | SAS {NPM_SAS:.2f}% | AST {NPM_AST:.2f}%")
print(f"f proxy 9T/25 {F_PROXY_9M25:.2f}pp | f nam 2025 (gom Q4/25) {F_2025_FY:.2f}pp | f 9T/26 {100*(FIN_REV_9M-FIN_EXP_9M)*0.8/REV_9M:.2f}pp")
F_HEAD = 2.0
FS = (0.0, 1.0, 2.0, 3.0, round(F_2025_FY, 2))
A = adj_npm(NPM_POOL, F_HEAD)
for nm, a in {"(a) GPM nganh, SG&A co dinh": adj_of(TGT["nganh_SAS+AST_2017-25"]), "(b) NPM nganh gop - f 2pp [HEADLINE]": A, "(c) GPM nganh, SG&A ty le": adj_prop(TGT["nganh_SAS+AST_2017-25"]),
              "(b') NPM SAS rieng - f 2pp": adj_npm(NPM_SAS, F_HEAD), "(b'') NPM AST rieng - f 2pp": adj_npm(NPM_AST, F_HEAD)}.items():
    print(f"  kenh bien {nm}: {a:+.1f} ty/nam ({a/N0:+.1%} N0)")
CASES = {"WIDE_hien_hanh(=r2)": {}, "chi_RONIC=Ke": dict(ronic_ke=True), "chi_bien_NPM_ve_nganh": dict(adj=A),
         "HEADLINE_CHAT3C(RONIC=Ke+NPM nganh-f2)": dict(adj=A, ronic_ke=True),
         "NONE(chat3c f2, NPM ve nganh ngay 2027)": dict(adj=A, ronic_ke=True, adj27=1.0)}
CASES["kenh(a)GPM_SGA_codinh+RONIC=Ke"] = dict(adj=adj_of(TGT["nganh_SAS+AST_2017-25"]), ronic_ke=True)
CASES["kenh(c)GPM_SGA_tyle+RONIC=Ke"] = dict(adj=adj_prop(TGT["nganh_SAS+AST_2017-25"]), ronic_ke=True)
CASES["kenh(b')NPM_SAS+RONIC=Ke"] = dict(adj=adj_npm(NPM_SAS, F_HEAD), ronic_ke=True)
CASES["kenh(b'')NPM_AST+RONIC=Ke"] = dict(adj=adj_npm(NPM_AST, F_HEAD), ronic_ke=True)
for f in FS:
    CASES[f"f={f}:chi_bien"] = dict(adj=adj_npm(NPM_POOL, f))
    CASES[f"f={f}:RONIC=Ke+bien"] = dict(adj=adj_npm(NPM_POOL, f), ronic_ke=True)
for k in ("SAS_rieng_2016-25", "AST_rieng_2017-25", "AST_GPM_P0_26Q3", "peer_rong_trung_vi_26Q3", "peer_rong_TB_26Q3"):
    CASES[f"kenh(a)_muc_tieu_GPM:{k}"] = dict(adj=adj_of(TGT[k]), ronic_ke=True)
OUT = {}
for k, kw in CASES.items():
    s = run(**kw); OUT[k] = s
    print(f"{k}: " + R2.fmt(s, PX) + f" | tam trung tam {s['central_post']:,.0f} | sleeve40 tam {s['center_sleeve40']:,.0f} {s['label_sleeve40']}")
# chong dem hai lan voi Long Thanh: headline nhung Delta=0 moi o
v, w = [], []
for (n, wn), (rr, wr), (g, wg) in itertools.product(zip(NS, W3), zip(RS, W3), zip(GS, W3)):
    v.append(val(0.0, n, rr, g, adj=A, ronic_ke=True)); w.append(wn * wr * wg)
s0 = R2.stats(v, w, PX, LD); OUT["HEADLINE_nhung_Delta=0"] = s0; print("HEADLINE_nhung_Delta=0 (can tren neu bien cao = ton that LT trung lap): " + R2.fmt(s0, PX))
json.dump(dict(npm_pool=NPM_POOL, npm_9m=NPM_9M, npm_op=NPM_OP, f_head=F_HEAD, f_grid=FS, f_proxy_9m25=F_PROXY_9M25, f_2025_fy=F_2025_FY, targets=TGT, adj_headline=A, n0=N0, rev_ann=REV_ANN, gpm_9m=GPM_9M, r=R, price=PX, disc_ref=LD, disc_sleeve=LDS, cases=OUT),
          open(os.path.join(HERE, 'sas_5f_out.json'), 'w'), indent=1, default=float, sort_keys=True)
