"""DDV — DD redo 05/11/2026 (job Taylor_20261105_014127). Mo hinh DUNG LAI theo khung skill hien hanh.
Chay: $DNA_PYEXE -I model.py -> model_out.json/.txt ; md5 -> LOCK_md5.txt ; roi ../../_common_014127/compare.py DDV.
Don vi ty dong; moc 30/09/2026. Nguon BCTC: BCTC rieng Q3/2026 (ban EN, ../../../dd_DDV_20261026/src/en_p1.txt; so chep o dd_DDV_20261026/REPORT.md muc 3).
Gia tri = tien rong chuan hoa VLD + PV(FCF 2027 theo duong S) + PV(Gordon tren LN loi giua chu ky tu 2028)."""
import csv, json, os, sys, itertools
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../_common_014127')))
import common as C
HERE = os.path.dirname(os.path.abspath(__file__))
# --- BCTC Q3/2026 (do) ---
NC_BCTC = 1108.0            # tien 114,4 + HTM 1.207,8 - vay NH 210,9 - thue TC 3,3
AP_UP, AR_UP = 449.0, 210.1  # phai tra NB 120 -> 569 (+449), phai thu KH 9,3 -> 219,4 (+210,1) trong Q3
NC_NORM = NC_BCTC - (AP_UP - AR_UP)   # tien rong khi VLD ve muc 30/06 (co so du lieu: BCTC) — DCF loi gia dinh VLD binh thuong
INT_Q3 = 22.15              # lai tien gui Q3 (BCTC) -> chi de tach khoi LN loi lich su
SH = 146_109_900
# --- Lich su (BQ tav2_bq.ticker_financial, NP_P0/Revenue_P0 theo QUY; bq_hist_out.csv) ---
rows = list(csv.DictReader(open(os.path.join(HERE, 'bq_hist_out.csv'))))
yr = {}
for r in rows:
    y = int(r['quarter'][:4])
    if 2015 <= y <= 2025:
        a = yr.setdefault(y, [0.0, 0.0, 0]); a[0] += float(r['NP_P0']) / 1e9; a[1] += float(r['Revenue_P0']) / 1e9; a[2] += 1
assert all(v[2] == 4 for v in yr.values()), 'thieu quy'
NPM_CYCLE = sum(v[0] for v in yr.values()) / sum(v[1] for v in yr.values())   # bien LN rong ca chu ky 2015-2025 (gom 2016 lo -470)
# --- Gia dinh (uoc luong) ---
REV_NORM = 5500.0      # (uoc luong) DT chuan hoa = DT 2027 cua DD 28/10 (Q3 chay 5.160, 9T chay 6.555)
G, RONIC = 0.03, 0.20  # (uoc luong)
INT_AT_NORM = INT_Q3 * 4 * 0.8 * NC_NORM / NC_BCTC   # lai tien gui sau thue tren tien rong chuan hoa — tru khoi LN giua chu ky (vi lich su co gom lai tien gui; tranh tinh doi voi tien rong)
SCN = {'xau': dict(w=0.45, np27=-185.0, mid=0.8), 'coso': dict(w=0.40, np27=107.0, mid=1.0), 'tot': dict(w=0.15, np27=373.0, mid=1.1)}
# np27 = LN hoat dong sau thue 2027 theo duong S/DAP (DD 28/10 bang muc 3, do doc bien 2,44; uoc luong) ; trong so 0,45/0,40/0,15 tu doc mu Bobby (DD 28/10 muc 2, uoc luong)
# mid = he so LN giua chu ky theo kich ban (uoc luong): xau 0,8 = Bobby loai B (chi phi S cao keo dai), tot 1,1.
MULTS = (0.8, 0.9, 1.0, 1.1, 1.2)   # he so LN giua chu ky (uoc luong)


def mid_np():
    return NPM_CYCLE * REV_NORM - INT_AT_NORM


def value_ps(s, m=1.0, r=None, nc=None):
    r = C.r_now() if r is None else r; c = SCN[s]; nc = NC_NORM if nc is None else nc
    f27 = c['np27'] * ((1 - G / RONIC) if c['np27'] > 0 else 1.0)
    e_term = mid_np() * c['mid'] * m * (1 + G) * (1 - G / RONIC)
    v = nc + f27 / (1 + r) ** 0.75 + e_term / (r - G) / (1 + r) ** 1.25
    return v * 1e9 / SH


def expected(r=None, nc=None):
    return sum(SCN[s]['w'] * value_ps(s, 1.0, r, nc) for s in SCN)


if __name__ == '__main__':
    r0 = C.r_now(); vals, wts = [], []
    for s, m in itertools.product(SCN, MULTS):
        vals.append(value_ps(s, m)); wts.append(SCN[s]['w'] / len(MULTS))
    sens = {f'beta{b}_{bp:+d}bp': round(expected(C.r_now(beta=b, shift=bp / 1e4))) for b in (0.5, 1.0) for bp in (-100, -50, 50, 100)}
    sens['base'] = round(expected())
    sc = {s: round(value_ps(s)) for s in SCN}
    hist = {y: dict(np=round(v[0], 1), rev=round(v[1], 1)) for y, v in sorted(yr.items())}
    nc_sens = {'nc_bctc_1108': round(expected(nc=NC_BCTC)), 'nc_norm': round(expected()), 'nc_norm_minus_liven217': round(expected(nc=NC_NORM - 217.0))}
    tvsh = (mid_np() * 1.03 * 0.85 / (r0 - G) / (1 + r0) ** 1.25 * 1e9 / SH) / value_ps('coso')
    out = dict(ticker='DDV', r=r0, center_pre=expected(), grid_vals=vals, grid_wts=wts,
               grid_desc='3 kich ban duong S/DAP 2027 (xau/co so/tot, w 0,45/0,40/0,15) x he so LN giua chu ky 5 diem 0,8-1,2 (deu); n=15; trong so o = w_kb/5',
               r_sens_pre=sens, scenarios_pre=sc, nc_sens_pre=nc_sens,
               parts=dict(nc_norm=NC_NORM, nc_norm_ps=NC_NORM * 1e9 / SH, npm_cycle=NPM_CYCLE, mid_np=mid_np(), int_at_norm=INT_AT_NORM, tv_share_coso=tvsh, hist=hist),
               free_float=1 - 0.640, free_float_src='1 - Vinachem 64,0% (935,1/1.461,1 ty VDL, BCTC Q3/2026)',
               change_reason='DCF Gordon r 13,5% thay boi so 9,5x/7x tren LN 2027; LN dai han = bien LN ca chu ky 2015-2025 (BQ) thay vi 1 nam; tien rong co so = chuan hoa VLD (5.950) thay vi 7.583; them chiet khau thanh khoan',
               warnings=['Vinachem 64% — gia chuyen giao apatit (ben lien quan), thoai von chua thuc hien',
                         'Phai thu Liven Nutrients 217 ty (9,8% VCSH) tap trung 1 khach — chua thu ve tai 30/09',
                         'Bai thach cao/moi truong Dinh Vu — nut that cong suat (WARNING, khong dinh luong)', 'UPCOM, free float 36%'],
               open_issues=['Duong S 2027 va do doc bien 2,44 la hieu chuan 2 diem (uoc luong)', 'NH3 khong co chuoi BQ', 'Tham so bien LN chu ky gom lai tien gui lich su (da tru lai tien gui hien tai)', 'Room ngoai chua kiem', 'Chua co BCTC Q4/2026'])
    json.dump(out, open('model_out.json', 'w'), indent=1, ensure_ascii=False)
    with open('model_out.txt', 'w') as f:
        print(f"r={r0:.4f} center_pre={out['center_pre']:.0f}", file=f)
        for k in ('scenarios_pre', 'r_sens_pre', 'nc_sens_pre', 'parts'):
            print(k, json.dumps(out[k]), file=f)
        print('grid wq pre:', json.dumps({k: round(v) for k, v in C.wq(vals, wts).items()}), file=f)
    print(open('model_out.txt').read())
