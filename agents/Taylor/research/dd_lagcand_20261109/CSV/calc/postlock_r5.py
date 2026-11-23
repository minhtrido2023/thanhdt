"""CSV r5 - pha SAU KHOA: gia + thanh khoan + nhan. Chay tu CSV/: /home/trido/thanhdt/wc_venv/bin/python -I calc/postlock_r5.py"""
import csv, json, math, os, sys
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import model_r5 as M
px = list(csv.DictReader(open(os.path.join(H, 'px_csv_r3.csv'))))
PX = float(px[-1]['Price']); PXD = px[-1]['time']
last = px[-251:]
vals = [float(r['Price']) * float(r['Volume']) for r in last][1:]
c = np.array([float(r['Close']) for r in last]); sig = float(np.std(np.diff(np.log(c)), ddof=1)); ADV = float(np.median(vals))
ADV60 = float(np.median([float(r['Price']) * float(r['Volume']) for r in px[-61:]][1:]))
CK = {k: sig * math.sqrt(q / ADV) for k, q in (('5ty', 5e9), ('1ty', 1e9), ('40tr', 40e6))}
EXIT = {k: dict(q_over_adv=q / ADV, days_at10=q / (0.1 * ADV), days_at20=q / (0.2 * ADV)) for k, q in (('5ty', 5e9), ('1ty', 1e9))}
def post(g, ck): return M.stats([(v * (1 - ck), w) for v, w in g])
G = M.grid()
P = {k: post(G, ck) for k, ck in CK.items()}
lab = lambda s: 'DUOI vung' if PX < s['p10'] else ('TREN vung' if PX > s['p90'] else 'TRONG vung')
wb = float(sum(w for v, w in G if v * (1 - CK['5ty']) < PX) / sum(w for _, w in G))
lo, hi = 0.03, 0.135
for _ in range(60):
    mid = (lo + hi) / 2; (lo, hi) = (mid, hi) if post(M.grid(r=mid), CK['5ty'])['center'] > PX else (lo, mid)
r_impl = (lo + hi) / 2
lo, hi = 0.0, 1.0
for _ in range(60):
    mid = (lo + hi) / 2; (lo, hi) = (mid, hi) if post(M.grid(phis=[mid], phw=[1.0]), CK['5ty'])['center'] > PX else (lo, mid)
phi_impl = (lo + hi) / 2
sens_post = {k: round(v * (1 - CK['5ty'])) for k, v in M.out['sens'].items()}
out = dict(price=PX, price_date=PXD, liq=dict(sigma_d=sig, adv250=ADV, adv60=ADV60, ck=CK, exit=EXIT, window=f"{last[1]['time']}..{last[-1]['time']}"),
           post=P, label={k: lab(v) for k, v in P.items()}, rule4={k: dict(threshold=round(.85 * v['center']), pass_=PX <= .85 * v['center']) for k, v in P.items()},
           pct_weight_below_price=wb, r_implied=r_impl, dep12_implied=r_impl - 0.135 + 0.074, phi_implied=phi_impl,
           sens_r_post={k: round(v * (1 - CK['5ty'])) for k, v in M.out['sens_r'].items()}, ke_band_post={k: round(v * (1 - CK['5ty'])) for k, v in M.out['ke_band'].items()},
           sens_post=sens_post, v6_v_short_post=round(M.out['v6']['v_short'] * (1 - CK['5ty'])),
           pe_norm=PX * M.SH / 1e9 / M.E['CO_SO'], pe_ttm=PX * M.SH / 1e9 / M.ttm, pb=PX * M.SH / 1e9 / M.BS['equity_parent'])
json.dump(out, open(os.path.join(H, 'postlock_r5_out.json'), 'w'), indent=1, ensure_ascii=False, default=float)
print(json.dumps(out, indent=1, ensure_ascii=False, default=float))
