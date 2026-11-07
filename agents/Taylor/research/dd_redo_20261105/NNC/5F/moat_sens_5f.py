"""5F addendum NNC 07/11/2026 — do nhay moat tu luoi DA KHOA grid_nnc_redo_r2.csv (khong chay lai engine).
WIDE = 100% STRUCTURAL (bien dinh ben toi 2043); NARROW_hien_hanh = trong so Bobby 0,20/0,45/0,35 (= REPORT_r2);
NARROW_strict = bo STRUCTURAL, chuan hoa lai 0,45/0,35 (bien ve TB chu ky / hoi mot nua co tre); NONE = 100% CYCLICAL.
Sau CK = x(1 - 0,036328) nhu REPORT_r2. Chay: /home/trido/thanhdt/wc_venv/bin/python -B moat_sens_5f.py"""
import csv, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '_shared'))
from wpct import wpct, weight_below  # noqa: E402
rows = list(csv.DictReader(open(os.path.join(HERE, '..', 'calc', 'grid_nnc_redo_r2.csv'))))
br = np.array([r['branch'] for r in rows]); w = np.array([float(r['w']) for r in rows]); v = np.array([float(r['V']) for r in rows])
CK = 0.03632771556437639; PX = 46900.0
base_w = {b: w[br == b].sum() for b in set(br)}
def st(cw):
    ww = w * np.array([cw.get(b, 0) / base_w[b] for b in br]); m = ww > 0
    vv, wq = v[m] * (1 - CK), ww[m] / ww[m].sum(); p = wpct(vv, wq)
    return dict(centre=float((vv * wq).sum()), p10=p[0.10], p50=p[0.50], p90=p[0.90],
                below_px=float(wq[vv < PX].sum()))
S = {'WIDE': st({'STRUCTURAL': 1}), 'NARROW_current': st({'STRUCTURAL': .2, 'ADMIN_GATED': .45, 'CYCLICAL': .35}),
     'NARROW_strict': st({'ADMIN_GATED': .45 / .8, 'CYCLICAL': .35 / .8}), 'NONE': st({'CYCLICAL': 1})}
print('base_w', {k: round(x, 4) for k, x in base_w.items()})
for k, s in S.items(): print(f"{k:15s} tam {s['centre']:,.0f} P10 {s['p10']:,.0f} P50 {s['p50']:,.0f} P90 {s['p90']:,.0f} duoi_gia {s['below_px']:.1%}")
json.dump(S, open(os.path.join(HERE, 'moat_sens_5f_out.json'), 'w'), indent=1)
