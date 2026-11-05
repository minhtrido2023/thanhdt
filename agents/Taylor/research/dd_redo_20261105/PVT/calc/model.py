"""PVT — DD redo 05/11/2026 (job Taylor_20261105_014127). Mo hinh DUNG LAI theo khung skill hien hanh (FCFE cua co dong me, r = Ke noi dia).
Chay: $DNA_PYEXE -I model.py -> model_out.json/.txt ; md5 -> LOCK_md5.txt ; ../../_common_014127/compare.py PVT.
Nguon BCTC: BCTC hop nhat Q3/2026 + CV 983 (text ../../../dd_PVT_20261029/src/q3_pvt_hopnhat_text.txt; so chep + rap hang dang thuc o dd_PVT_20261029/REPORT.md, out.txt).
Lich su: BQ tav2_bq.ticker_financial (bq_hist_out.csv): NP_P0 = LNST me theo QUY (2026Q3 375,1 = 9T me 1.272,3 - 6T 897,2), ROE_Trailing."""
import csv, json, os, sys, itertools, statistics
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../_common_014127')))
import common as C
HERE = os.path.dirname(os.path.abspath(__file__))
SH = 516_918_938                   # [TM22b]
EQ_PARENT = 9855.6                 # VCSH me 30/09/2026 [BCDKT]
NET_DEBT = 619.3                   # da nam trong VCSH (dinh gia theo LN sau lai vay) — chi ghi nhan
rows = list(csv.DictReader(open(os.path.join(HERE, 'bq_hist_out.csv'))))
Q3_NP = float([r for r in rows if r['quarter'] == '2026Q3'][0]['NP_P0']) / 1e9
ROE_HIST = {r['quarter'][:4]: float(r['ROE_Trailing']) for r in rows if r['quarter'].endswith('Q4') and 2015 <= int(r['quarter'][:4]) <= 2025}
assert len(ROE_HIST) == 11
ROE_MID = statistics.median(ROE_HIST.values())          # ROE trung vi ca chu ky 2015-2025 (BQ)
G = 0.03                                                 # (uoc luong)
# NP me 2027 theo kich ban (uoc luong, DD 29/10 §7; trong so 0,35/0,45/0,20 uoc luong theo doc mu Bobby: CYCLICAL 0,55, BIMCO keo cuoc 2027 xuong)
# mid = he so ROE giua chu ky theo kich ban (uoc luong): xau 0,85 (doi tau gia + KH tau mua 2025-26 de len), tot 1,1.
SCN = {'xau': dict(w=0.35, np27=1000.0, mid=0.85), 'coso': dict(w=0.45, np27=1250.0, mid=1.0), 'tot': dict(w=0.20, np27=1500.0, mid=1.1)}
MULTS = (0.8, 0.9, 1.0, 1.1, 1.2)   # he so ROE giua chu ky (uoc luong)


def value_ps(s, m=1.0, r=None):
    r = C.r_now() if r is None else r; c = SCN[s]; roe = ROE_MID * c['mid'] * m
    reinv = 1 - G / max(roe, 1e-9)
    q4 = Q3_NP / (1 + r) ** 0.125                         # Q4/2026 ~ Q3 me (khong phan phoi giu lai -> van thuoc co dong)
    f27 = c['np27'] * reinv / (1 + r) ** 0.75
    np_mid = roe * EQ_PARENT
    tv = np_mid * (1 + G) * reinv / (r - G) / (1 + r) ** 1.25
    return (q4 + f27 + tv) * 1e9 / SH


def expected(r=None):
    return sum(SCN[s]['w'] * value_ps(s, 1.0, r) for s in SCN)


if __name__ == '__main__':
    r0 = C.r_now(); vals, wts = [], []
    for s, m in itertools.product(SCN, MULTS):
        vals.append(value_ps(s, m)); wts.append(SCN[s]['w'] / len(MULTS))
    sens = {f'beta{b}_{bp:+d}bp': round(expected(C.r_now(beta=b, shift=bp / 1e4))) for b in (0.5, 1.0) for bp in (-100, -50, 50, 100)}
    sens['base'] = round(expected())
    sc = {s: round(value_ps(s)) for s in SCN}
    bvps = EQ_PARENT * 1e9 / SH
    out = dict(ticker='PVT', r=r0, center_pre=expected(), grid_vals=vals, grid_wts=wts,
               grid_desc='3 kich ban LN me 2027 (xau/co so/tot 1.000/1.250/1.500, w 0,35/0,45/0,20) x he so ROE giua chu ky 5 diem 0,8-1,2 (deu); n=15; trong so o = w_kb/5',
               r_sens_pre=sens, scenarios_pre=sc,
               parts=dict(q3_np_parent=Q3_NP, roe_mid=ROE_MID, roe_hist=ROE_HIST, np_mid_coso=ROE_MID * EQ_PARENT, bvps_parent=bvps,
                          implied_pb_center=expected() / bvps, net_debt_info=NET_DEBT),
               free_float=1 - 0.51, free_float_src='1 - PVN 51% (263,6 tr cp) [TM22b]',
               change_reason='DCF FCFE r 13,5% (ROE giua chu ky BQ 2015-25, g 3%) thay PE 6,5/8,0/8,5 x LN 2027; Q4/2026 cong rieng; co chiet khau thanh khoan (~0)',
               warnings=['Thay TGD 2 lan trong 4 thang (07-08/2026); ly do khong cong bo', 'Phai thu don vi PVN 1.144,7 ty (+130%) — von luu dong',
                         'Doi chuan muc TT99: ngung trich truoc sua chua lon -> bien 2026 thien lech tang, do lon chua xac dinh',
                         'Mua tau o dinh gia tau cu truoc 31/12/2026 (Bobby muc 7) — chua thay trong 9T; co so NPV=0'],
               open_issues=['BCTC ban nien soat xet / nam 2025 kiem toan (y kien) chua co trong tay', 'Tac dong TT99 dinh luong', 'Ty trong TC/spot va dao han HD tau', 'Room ngoai chua kiem', 'NP 2027 kich ban la uoc luong'])
    json.dump(out, open('model_out.json', 'w'), indent=1, ensure_ascii=False)
    with open('model_out.txt', 'w') as f:
        print(f"r={r0:.4f} center_pre={out['center_pre']:.0f}", file=f)
        for k in ('scenarios_pre', 'r_sens_pre', 'parts'):
            print(k, json.dumps(out[k]), file=f)
        print('grid wq pre:', json.dumps({k: round(v) for k, v in C.wq(vals, wts).items()}), file=f)
    print(open('model_out.txt').read())
