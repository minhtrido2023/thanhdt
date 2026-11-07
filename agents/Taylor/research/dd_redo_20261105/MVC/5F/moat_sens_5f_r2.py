"""5F addendum MVC 07/11/2026 (job Taylor_20261107_123139) — do nhay moat tu luoi DA KHOA calc/grid_mvc_redo_r2.csv (khong chay lai engine).
Cung quy uoc NNC r2 (NNC/5F/moat_sens_5f_r2.py): BAN CHAT-3C = bo STRUCTURAL & ADMIN-perm05, giu trong so NHANH ADMIN 0,45 (ramp/full moi 1/2).
Them truc bien Tan Lap theo TB chu ky NGANH (GPM nam trong so DT 2016-25, 5F/bq_gpm_annual_rw.csv): trung vi peer 29,9% ~ tl_m 0,30;
TB peer 32,6% ~ {0,30; ~NNC 34,0%}. CK 4 co: 5 ty / 1 ty / 40 tr / 10 tr (so tu SUMMARY.json r2). Chay: $DNA_PYEXE -B moat_sens_5f.py"""
import csv, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '_shared'))
from wpct import wpct  # noqa: E402
rows = list(csv.DictReader(open(os.path.join(HERE, '..', 'calc', 'grid_mvc_redo_r2.csv'))))
br = np.array([r['branch'] for r in rows]); ad = np.array([r['admin'] for r in rows]); tl = np.array([r['tl_m'] for r in rows])
w = np.array([float(r['w']) for r in rows]); v = np.array([float(r['V']) for r in rows])
S0 = json.load(open(os.path.join(HERE, '..', 'SUMMARY.json')))
PX = S0['price']
CK = {'5ty': S0['ck_ref_size']['disc_adv250'], '1ty': S0['ck_ref_size']['disc_1bn'],
      '40tr': S0['ck_real_sleeve']['40tr']['adv250'], '10tr': S0['ck_real_sleeve']['10tr']['adv250']}


def lab(p10, p90): return 'DUOI' if PX < p10 else ('TREN' if PX > p90 else 'TRONG')


def st(f):
    mm = np.array([f(b, a, t) for b, a, t in zip(br, ad, tl)]); ww = w * mm; m = ww > 0; wq = ww[m] / ww[m].sum()
    out = {}
    for k, ck in CK.items():
        vv = v[m] * (1 - ck); p = wpct(vv, wq); c = float((vv * wq).sum())
        out[k] = dict(centre=c, p10=float(p[0.10]), p50=float(p[0.50]), p90=float(p[0.90]), below_px=float(wq[vv < PX].sum()),
                      rule4=bool(PX <= 0.85 * c), label=lab(float(p[0.10]), float(p[0.90])))
    return out


def kb(b, a, t, struct=False, adm=('ramp', 'full'), tls=None):
    if tls is not None and b != 'STRUCTURAL' and t not in tls: return 0.0
    if b == 'STRUCTURAL': return 1.0 if struct else 0.0
    if b == 'ADMIN_GATED': return 1.5 if (a in adm and len(adm) == 2) else (1.0 if a in adm else 0.0)
    return 1.0


S = {
 'WIDE': st(lambda b, a, t: 1.0 if b == 'STRUCTURAL' else 0.0),
 'NARROW_current': st(lambda b, a, t: 1.0),
 'KB_drop_perm05_keep_STRUCT': st(lambda b, a, t: kb(b, a, t, struct=True)),
 'KB_CHAT_3C': st(lambda b, a, t: kb(b, a, t)),
 'CHAT_3C_global_renorm': st(lambda b, a, t: 0.0 if (b == 'STRUCTURAL' or a == 'perm05' and b == 'ADMIN_GATED') else 1.0),
 'KB_CHAT_3C_tl_peer_median_0.30': st(lambda b, a, t: kb(b, a, t, tls=('0.3',))),
 'KB_CHAT_3C_tl_peer_mean_0.30_nnc': st(lambda b, a, t: kb(b, a, t, tls=('0.3', 'nnc'))),
 'KB_CHAT_3C_tl_0.25_floor': st(lambda b, a, t: kb(b, a, t, tls=('0.25',))),
 'NONE': st(lambda b, a, t: 1.0 if b == 'CYCLICAL' else 0.0),
}
share = {'STRUCTURAL': float(w[br == 'STRUCTURAL'].sum()), 'ADMIN_perm05': float(w[(br == 'ADMIN_GATED') & (ad == 'perm05')].sum())}
assert abs(S['NARROW_current']['5ty']['centre'] - S0['center_post_liq']) < 1, 'chan doi chung khong tai lap REPORT_r2'
for k, s in S.items():
    a = s['5ty']; b1 = s['1ty']
    print(f"{k:34s} 5ty tam {a['centre']:,.0f} P10 {a['p10']:,.0f} P50 {a['p50']:,.0f} P90 {a['p90']:,.0f} duoi {a['below_px']:.1%} L4 {a['rule4']} {a['label']}"
          f" | 1ty tam {b1['centre']:,.0f} P10 {b1['p10']:,.0f} P90 {b1['p90']:,.0f} {b1['label']} | 40tr P10 {s['40tr']['p10']:,.0f} {s['40tr']['label']} | 10tr {s['10tr']['label']}")
print('share', share, 'px', PX)
json.dump(dict(S=S, share=share, px=PX, ck=CK), open(os.path.join(HERE, 'moat_sens_5f_out.json'), 'w'), indent=1)
