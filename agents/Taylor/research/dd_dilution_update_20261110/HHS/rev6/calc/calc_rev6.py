"""HHS rev6 (23/11/2026, job Taylor_20261123_100926) — MU GIA. Khong doc gia thi truong.
(1) Tai lap luoi r3 tu hhs_r3.py (phan loi dong 1..'# ---- CONTROL', md5 pin) => tam truoc CK 14.169 / sau CK 13.969.
(2) Tach khoi HTK NC-II: phan HH1-HH4 (ty trong w tren gia goc BLK 6.009,8) nhan thang du s_hh rieng, phan con lai giu s r3.
(3) Doi chieu PPA kiem toan (AASC 2025): gia tri so CRV theo GTHL vs gia tri mo hinh.
(4) Tai lap kiem tra cua skeptic r3 (dich s toan khoi -0,30 / -0,54)."""
import os, sys, json, hashlib, math
H = os.path.dirname(os.path.abspath(__file__))
R3 = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/dd_redo_20261105/HHS/calc_r3/hhs_r3.py'
DIL = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/dd_dilution_update_20261110/calc/dilution_out.json'
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
assert md5(R3) == 'cf5420d86989f25b4070697b38347c52'
assert md5(DIL) == '0450ba0aee972c6c4ec97847fe2de68c'
A = json.load(open(os.path.join(H, 'assumptions.json')))
src = open(R3).read(); core = src.split('# ---- CONTROL')[0]
ns = {'__file__': R3, '__name__': 'r3core'}
exec(compile(core, R3, 'exec'), ns)
R2C, make, HEAD = ns['R2C'], ns['make'], ns['HEAD']
SC, BLK, HHS, SH, R, S_OBS, pv = ns['SC'], ns['BLK'], ns['HHS'], ns['SH'], ns['R'], ns['S_OBS'], ns['pv']
d5 = json.load(open(DIL))['HHS']['inputs']['d5']
PX_BLIND = 0.0   # mu gia: khong dung gia; pct_below bo qua


def grid(fn_extra=None, **fkw):
    ax, fn = make(HEAD)
    def f(**a):
        v = fn(**a, **fkw)
        return v + (fn_extra(**a) if fn_extra else 0.0)
    res = R2C.outcomes(ax, f)
    pre = R2C.stats(res, PX_BLIND, 0.0); post = R2C.stats(res, PX_BLIND, d5)
    k = ('center', 'p10', 'p50', 'p90')
    return {**{q + '_pre': round(pre[q]) for q in k}, **{q: round(post[q]) for q in k}, 'n': pre['n']}


out = {'r': R, 's_obs': S_OBS, 'BLK': BLK, 'd5': d5}
base = grid(); out['base_r3_reproduced'] = base
assert (base['center_pre'], base['center'], base['p10'], base['p50'], base['p90']) == (14169, 13969, 12422, 13917, 15564), base

# (4) kiem tra skeptic: dich s TOAN khoi
out['skeptic_whole_block_shift'] = {str(x): grid(s_shift=x) for x in (-0.30, -0.54)}

# (2) tach HH1-HH4: tru phan thang du chenh lech tren w*BLK
def split_extra(w, s_hh):
    def e(scen, ds, y=4.0, bds=0.0, i14=0.0, **_):
        s = SC[scen]; sv = max(S_OBS + s['off_sym'] + ds, 0.0)
        return -HHS * BLK * w * (sv - s_hh) * pv(y, R) / SH * 1e3
    return e

hs = A['hh_split']
tab = {}
for w in hs['w_ladder']:
    for s_hh in hs['s_hh_ladder']:
        g = grid(fn_extra=split_extra(w, s_hh)); g['d_center_pct'] = round(g['center'] / base['center'] - 1, 4)
        tab[f'w={w}|s_hh={s_hh}'] = g
out['hh_split'] = tab
# phep thu: w=1, s_hh=s_obs-0,54 phai ~ skeptic -0,54 (chi khac o kich ban lech doi xung)
# ty le dien tich dat (chi bao, uoc luong)
out['land_share_hh'] = dict(hh_m2=hs['hh_land_m2'], nc2_m2=hs['nc2_site_m2'], share=round(hs['hh_land_m2'] / hs['nc2_site_m2'], 4))

# xac suat kich ban (b) — uoc luong, KHONG vao base
pw = hs['scenario_probs']
ev = sum(p * tab[k]['center'] for k, p in pw.items()) + (1 - sum(pw.values())) * base['center']
out['hh_prob_weighted_center_estimate'] = round(ev); out['hh_prob_weighted_pct'] = round(ev / base['center'] - 1, 4)

# (3) doi chieu PPA kiem toan
EQ_ME, NCI, CRV_FV, CRV_COST, STEP_AT = ns['EQ_ME'], ns['NCI'], ns['CRV_FV'], ns['CRV_COST'], ns['STEP_AT']
NMTT, VAT, BDS_SURP = ns['NMTT'], ns['VAT'], ns['BDS_SURP']
surplus_model_undisc = BLK * S_OBS + NMTT / VAT * SC['CO_SO']['m'] + BDS_SURP
out['ppa_anchor'] = dict(bvps_parent=round(EQ_ME / SH * 1e3), crv_fv_book_bn=round(CRV_FV, 1), step_up_after_tax_bn=round(STEP_AT, 1),
                         model_surplus_undiscounted_central_bn=round(surplus_model_undisc, 1),
                         model_over_ppa=round(surplus_model_undisc / STEP_AT, 3),
                         center_vs_bvps=round(base['center'] / (EQ_ME / SH * 1e3) - 1, 4))

# r V1 tai 23/11
from deposit_rate_vn import effective_deposit_rate
dn = effective_deposit_rate('2026-11-23'); out['deposit_now'] = dict(rate=dn['rate'], src=dn.get('rate_source'))
out['r_now'] = 0.135 + 1.0 * (dn['rate'] - 0.074)

# bien doi pha loang cho kich ban (dung cong thuc rev5): EX du 100%, k=1
N0, NR, CASH, DIV = 431_985_968, 259_191_580, 259_191_580 * 10_000, 0.07
ex = lambda V: (V * N0 + (1 - d5) * CASH) / (N0 + NR) / (1 + DIV)
out['ex_full_k1'] = {'base': round(ex(base['center']))} | {k: round(ex(v['center'])) for k, v in tab.items()}
json.dump(out, open(os.path.join(H, 'calc_rev6_out.json'), 'w'), ensure_ascii=False, indent=1, default=float)
print(json.dumps(out, ensure_ascii=False, indent=1, default=float))
