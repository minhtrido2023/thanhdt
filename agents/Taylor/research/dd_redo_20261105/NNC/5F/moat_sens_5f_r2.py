"""5F addendum NNC r2 07/11/2026 — do nhay moat tu luoi DA KHOA calc/grid_nnc_redo_r2.csv (khong chay lai engine).
Them: tach 3 muc ADMIN (perm05/ramp/full, moi 1/3), BAN CHAT-3C (bo STRUCTURAL & perm05), bo rieng perm05 giu STRUCTURAL,
va bien the KB_* (giu nguyen trong so NHANH ADMIN 0,45, chia lai ramp/full 1/2 moi muc). Chay: /home/trido/thanhdt/wc_venv/bin/python -B moat_sens_5f_r2.py"""
import csv, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '_shared'))
from wpct import wpct  # noqa: E402
rows = list(csv.DictReader(open(os.path.join(HERE, '..', 'calc', 'grid_nnc_redo_r2.csv'))))
br = np.array([r['branch'] for r in rows]); ad = np.array([r['admin'] for r in rows])
w = np.array([float(r['w']) for r in rows]); v = np.array([float(r['V']) for r in rows])
CK = 0.03632771556437639; PX = 46900.0
def st(f):  # f(branch, admin) -> relative weight multiplier
    m_ = np.array([f(b, a) for b, a in zip(br, ad)]); ww = w * m_; m = ww > 0
    vv, wq = v[m] * (1 - CK), ww[m] / ww[m].sum(); p = wpct(vv, wq)
    c = float((vv * wq).sum())
    return dict(centre=c, p10=float(p[0.10]), p50=float(p[0.50]), p90=float(p[0.90]),
                below_px=float(wq[vv < PX].sum()), rule4=bool(PX <= 0.85 * c))
def bw(b, a, adm_ok, struct=True, cyc=True, keep_branch=False):
    if keep_branch and b == 'ADMIN_GATED': return (1.0 / len(adm_ok)) * 3 if a in adm_ok else 0.0
    if b == 'STRUCTURAL': return 1.0 if struct else 0.0
    if b == 'CYCLICAL': return 1.0 if cyc else 0.0
    return 1.0 if a in adm_ok else 0.0
S = {
 'WIDE': st(lambda b, a: 1.0 if b == 'STRUCTURAL' else 0.0),
 'NARROW_current': st(lambda b, a: 1.0),
 'drop_perm05_keep_STRUCT': st(lambda b, a: bw(b, a, ('ramp', 'full'))),
 'CHAT_3C': st(lambda b, a: bw(b, a, ('ramp', 'full'), struct=False)),
 'drop_STRUCT_keep_all_ADMIN': st(lambda b, a: bw(b, a, ('perm05', 'ramp', 'full'), struct=False)),
 'KB_drop_perm05_keep_STRUCT': st(lambda b, a: bw(b, a, ('ramp', 'full'), keep_branch=True)),
 'KB_CHAT_3C': st(lambda b, a: bw(b, a, ('ramp', 'full'), struct=False, keep_branch=True)),
 'NONE': st(lambda b, a: 1.0 if b == 'CYCLICAL' else 0.0),
}
share = {'STRUCTURAL': float(w[br == 'STRUCTURAL'].sum()), 'ADMIN_perm05': float(w[(br == 'ADMIN_GATED') & (ad == 'perm05')].sum())}
for k, s in S.items(): print(f"{k:28s} tam {s['centre']:,.0f} P10 {s['p10']:,.0f} P50 {s['p50']:,.0f} P90 {s['p90']:,.0f} duoi_gia {s['below_px']:.1%} luat4 {s['rule4']}")
print('share', share)
json.dump(dict(S=S, share=share), open(os.path.join(HERE, 'moat_sens_5f_r2_out.json'), 'w'), indent=1)
