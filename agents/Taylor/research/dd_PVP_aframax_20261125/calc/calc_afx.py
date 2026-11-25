"""PVP — tac dong tai lieu DHDCD bat thuong 2026 (hop 30/11, DU THAO dang 09/11) len tam (job Taylor_20261125_080254).
KHONG doi mo hinh r3: import pvp_r3 tu ban khoi phuc (git archive 14ad1c925^), assert md5 LOCK + CONTROL 23.099 (giong calc_recheck.py dot 2).
Chi doi truc mua tau (ship_buy). MU GIA: khong doc gia.
Nguon: src/3-du-thao-to-trinh-dieu-chinh-danh-muc... (tong 116 tr USD giu nguyen, '1 den 03 tau'), src/4-du-thao-to-trinh-...-tau-cho-dau-tho (DT-08/26/TBD: TMDT <=80 tr USD, gia tau 79,55, 10 tuoi, vay <=70%, IRR 7,67%, IRRmin 10+1=11%, bang gia tau Clarksons/Allied).
Chay: /home/trido/thanhdt/wc_venv/bin/python -I calc_afx.py /tmp/ddrestore_PVP/agents/Taylor/research/dd_redo_20261105"""
import hashlib, json, os, sys
BASE = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__))
C3 = os.path.join(BASE, 'PVP', 'calc_r3')
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
LOCKED = {'PVP/calc_r3/pvp_r3.py': 'ea8c9944b846b6fa5ac1a35468ec674a', 'PVP/calc_r3/assumptions_r3.json': '1d0b7c672690f6aa729126d70851f1b9',
          'PVP/calc/model.py': '4e89831fad57543af5990bc2e8c33658', 'PVP/calc/model_r2_out.json': 'c7b2bf794ca4a8f523b962a942addbaa',
          '_common_014127/common.py': '24943cb1a1d35d91bee6ca1fab9d7202', '_shared/wpct.py': '4597bc083f0d64d8873141b12fbfb3a6',
          'PVP/calc_r3/pvp_r3_out.json': '3e9fc88cf203cd3f0d0b2bd47770358d'}
for p, m in LOCKED.items():
    assert md5(os.path.join(BASE, p)) == m, p
SRC = os.path.join(HERE, '..', 'src')
SRC_MD5 = {'3-du-thao-to-trinh-dieu-chinh-danh-muc-dau-tu-nam-20261794272973.pdf': '5632c9f145c8',
           '4-du-thao-to-trinh-phe-duyet-chu-truong-thuc-hien-du-an-dau-tu-tau-cho-dau-tho1794272973.pdf': '97a91ce533b5'}
for f, m in SRC_MD5.items():
    assert md5(os.path.join(SRC, f)).startswith(m), f
sys.path.insert(0, C3); sys.path.insert(0, os.path.join(BASE, '_shared'))
import pvp_r3 as P  # noqa: E402
from wpct import wpct  # noqa: E402
O = json.load(open(os.path.join(C3, 'pvp_r3_out.json')))
D = json.load(open(os.path.join(BASE, 'PVP', 'SUMMARY.json')))['liq_disc_5ty']; F = 1 - D
v0, w0, _ = P.grid(P.R3)
assert all(abs(a - b) < 1e-9 for a, b in zip(v0, O['outcomes_vals']))           # CONTROL tung o
BUY0 = {k: dict(v) for k, v in P.BUY.items()}


def summ(buy, cfg=None):
    P.BUY.clear(); P.BUY.update({k: dict(v) for k, v in buy.items()})
    try:
        v, w, _ = P.grid(cfg or P.R3); q = wpct(v, w, (0.10, 0.50, 0.90))
        return dict(center=round(P.mean(v, w) * F), p10=round(q[0.10] * F), p50=round(q[0.50] * F), p90=round(q[0.90] * F))
    finally:
        P.BUY.clear(); P.BUY.update({k: dict(v) for k, v in BUY0.items()})


def B(ca_hai=(0.50, 116.0), chi_2=(0.35, 56.5), khong=(0.15, 0.0)):
    return {'ca_hai': dict(w=ca_hai[0], usd=ca_hai[1]), 'chi_2': dict(w=chi_2[0], usd=chi_2[1]), 'khong': dict(w=khong[0], usd=khong[1])}


base = summ(B()); assert (base['center'], base['p10'], base['p90']) == (23099, 13799, 30338), base
npv0 = {s: 0.0 for s in P.SCNS}; m30 = {s: -0.30 for s in P.SCNS}
V = {
    'A_mot_tau_80': (B(chi_2=(0.35, 80.0)), None, 'nhanh "mot tau" = DT-08/26/TBD 80 tr USD (thay Aframax #2 56,5 da gop vao dong 116 tai to trinh 3); trong so giu'),
    'B_mot_tau_80_khong_005': (B(chi_2=(0.45, 80.0), khong=(0.05, 0.0)), None, 'do nhay: van kien da hoan thien + DHDCD da trieu tap => "khong" 0,15->0,05 [UL]'),
    'C_mot_tau_80_khong_030': (B(ca_hai=(0.40, 116.0), chi_2=(0.30, 80.0), khong=(0.30, 0.0)), None, 'do nhay: khong thong qua / khong tim duoc tau (to trinh 3: it chu tau chao ban) [UL]'),
    'D_chi_mot_tau_80_chac': (B(ca_hai=(0.0, 116.0), chi_2=(1.0, 80.0), khong=(0.0, 0.0)), None, 'do nhay: chac chan mua dung 1 tau 80'),
    'E_ca_goi_116_chac': (B(ca_hai=(1.0, 116.0), chi_2=(0.0, 80.0), khong=(0.0, 0.0)), None, 'do nhay: chac chan dung het 116'),
    'F_npv0_moi_nhanh_A': (B(chi_2=(0.35, 80.0)), dict(P.R3, npv=npv0), 'NPV tau moi = 0 moi kich ban (luat 03/11 thuan) — khong phu thuoc gia tri mua'),
    'G_m30_vo_dieu_kien_A': (B(chi_2=(0.35, 80.0)), dict(P.R3, npv=m30), 'NPV -30% vo dieu kien voi nhanh mot tau 80'),
}
out = dict(ticker='PVP', liq_disc_5ty=D, base=base, variants={})
for k, (buy, cfg, why) in V.items():
    s = summ(buy, cfg); s['d_vnd'] = s['center'] - base['center']; s['d_pct'] = round(100 * s['d_vnd'] / base['center'], 2); s['why'] = why
    out['variants'][k] = s
# kiem cheo do lon -30% nhanh xau bang bang gia tau cua chinh PVP (Clarksons/Allied, to trinh 4 tr.3): tau 10 tuoi
p10y = {'2023': 55.0, '2024': 52.0, '2025': 55.0, 'T10_2026': 80.0, 'bq_T4_T10_2026': 72.14}
mr = (p10y['2023'] + p10y['2024'] + p10y['2025']) / 3
out['xcheck_m30'] = dict(price_10y=p10y, mean_2023_2025=round(mr, 2), drop_if_revert_from_80=round(1 - mr / 79.55, 4),
                         note='gia tri tai san quay ve TB 2023-25 => -32,1% gia mua 79,55 (mark-to-market, khong phai NPV dong tien); chi KIEM CHEO dau/do lon nhanh xau, khong doi tham so')
json.dump(out, open(os.path.join(HERE, 'calc_afx_out.json'), 'w'), indent=1, ensure_ascii=False)
print(json.dumps(out, ensure_ascii=False, indent=1))
