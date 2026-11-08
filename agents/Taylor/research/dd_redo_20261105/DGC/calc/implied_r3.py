"""Gia ngu y 33.000 (sau CK 5 ty) tren mo hinh r3 khoa. Chay sau compare_r3.py. Doc model_r3.py (khoa) + summary_r3_core.json."""
import json, os, sys, itertools
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import model_r3 as M
S = json.load(open(os.path.join(HERE, 'summary_r3_core.json'))); f = 1 - S['liq_disc_5ty']; px = S['price']; r0 = M.C.r_now(); cfg = M.CFG0
ws = dict(zip(('xau', 'coso', 'tot'), cfg['w_scn']))
def ev(mult=1.0, prov=None, s_only=None):
    tot = 0
    for s, p, n in itertools.product(ws, M.MR2.PROV, M.MR2.NS):
        wp = (1.0 if p == prov else 0.0) if prov else M.MR2.PROV[p]['w']
        wsx = (1.0 if s == s_only else 0.0) if s_only else ws[s]
        tot += wsx * wp * M.MR2.NS[n]['w'] * M.value_ps(s, 'dung', p, n, mult, r0, cfg)
    return tot * f
lo, hi = 0.0, 1.0
for _ in range(60):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if ev(mid) < px else (lo, mid)
out = dict(price=px, ebit_mult_for_center_eq_price=round(lo, 4), center_if_prov_permanent_certain=round(ev(prov='vinh_vien')),
           center_if_xau_certain=round(ev(s_only='xau')), center_if_xau_and_permanent=round(ev(prov='vinh_vien', s_only='xau')),
           note='tam headline o r=13,5%, khai truong dung, NS so sach binh quan; he so EBIT ap len Q4/26, 2027, 2028 va terminal')
json.dump(out, open(os.path.join(HERE, 'implied_r3_out.json'), 'w'), ensure_ascii=False, indent=1); print(out)
