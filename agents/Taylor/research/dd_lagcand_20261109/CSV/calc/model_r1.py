"""CSV DD 09/11/2026 - mo hinh tai lap. Chay: /home/trido/thanhdt/wc_venv/bin/python -I calc/model.py (tu thu muc CSV/).
Doc calc/assumptions.json, calc/fin_csv_bq.csv, calc/px_csv.csv; ghi calc/model_out.json. Khong goi mang."""
import csv, json, math, os, itertools
import numpy as np

H = os.path.dirname(os.path.abspath(__file__))
A = json.load(open(os.path.join(H, 'assumptions.json')))
SH = A['shares']; BS = A['bs_30_09_2026_ty']
DEP12 = 0.074; R = 0.135 + 1.0 * (DEP12 - 0.074)

# --- LN cong ty me theo nam (BQ, so quy) ---
q = {r['quarter']: float(r['NP_P0']) / 1e9 for r in csv.DictReader(open(os.path.join(H, 'fin_csv_bq.csv')))}
yr = {y: sum(q[f'{y}Q{i}'] for i in range(1, 5)) for y in range(2017, 2026) if all(f'{y}Q{i}' in q for i in range(1, 5))}
hist = [yr[y] for y in range(2019, 2026)]
ttm = q['2025Q4'] + q['2026Q1'] + q['2026Q2'] + q['2026Q3']
nine_m26 = q['2026Q1'] + q['2026Q2'] + q['2026Q3']; nine_m25 = q['2025Q1'] + q['2025Q2'] + q['2025Q3']
E = dict(XAU=min(hist), CO_SO=float(np.mean(hist)), TOT=ttm)
INT_AT = A['interest_income_9T_ty'] * 4 / 3 * (1 - A['tax_rate'])
NET_CASH = BS['cash_110'] + BS['st_deposit_121'] - BS['st_debt_321'] - BS['lt_debt']
NCI = BS['nci_429']
NT = A['nhon_trach']

def value(e_ty, de=0.0, npv=0.0, dis=0.0, r=R, ronic=None, g=0.0, comp=0.0):
    ecore = e_ty * (1 + de) - INT_AT
    mult = 1 / r if ronic is None else (1 - g / ronic) / (r - g)
    eq = ecore * mult + NET_CASH - NCI + npv * NT['capex_total_ty'] + dis * ecore + comp
    return eq * 1e9 / SH

def wpct(vals, ws, p):
    o = np.argsort(vals); v = np.asarray(vals)[o]; w = np.asarray(ws)[o]; c = np.cumsum(w) - w / 2; c /= w.sum()
    return float(np.interp(p, c, v))

def grid(r=R, **kw):
    out = []
    for (s, ws), (de, wd), (npv, wn), (dis, wdi) in itertools.product(
            zip(('XAU', 'CO_SO', 'TOT'), A['norm_np']['weights']), zip(A['norm_np']['dE_axis'], A['norm_np']['dE_w']),
            zip(NT['axis_npv_frac'], NT['axis_w']), zip(A['disruption']['axis_frac_of_1y_Ecore'], A['disruption']['w'])):
        out.append((value(E[s], de, npv, dis, r=r, **kw), ws * wd * wn * wdi, s))
    return out

def stats(g, ck=0.0):
    v = [x[0] * (1 - ck) for x in g]; w = [x[1] for x in g]
    return dict(center=round(float(np.dot(v, w) / sum(w))), p10=round(wpct(v, w, .1)), p25=round(wpct(v, w, .25)), p50=round(wpct(v, w, .5)),
                p75=round(wpct(v, w, .75)), p90=round(wpct(v, w, .9)), min=round(min(v)), max=round(max(v)), n=len(v))

# --- gia + thanh khoan ---
px = list(csv.DictReader(open(os.path.join(H, 'px_csv.csv'))))
PX = float(px[-1]['Price']); PXD = px[-1]['time']
last = px[-251:]
vals = [float(r['Price']) * float(r['Volume']) for r in last][1:]
c = np.array([float(r['Close']) for r in last]); sig = float(np.std(np.diff(np.log(c)), ddof=1)); ADV = float(np.median(vals))
last60 = px[-61:]; ADV60 = float(np.median([float(r['Price']) * float(r['Volume']) for r in last60][1:]))
CK = {k: sig * math.sqrt(qv / ADV) for k, qv in (('5ty', 5e9), ('40tr', 40e6), ('10tr', 10e6))}
EXIT = {k: dict(q_over_adv=qv / ADV, days_at10=qv / (0.1 * ADV), days_at20=qv / (0.2 * ADV)) for k, qv in (('5ty', 5e9), ('1ty', 1e9), ('40tr', 40e6))}

G = grid()
pre = stats(G)
post = {k: stats(G, ck) for k, ck in CK.items()}
def label(s):
    return 'DƯỚI vùng' if PX < s['p10'] else ('TRÊN vùng' if PX > s['p90'] else 'TRONG vùng')
scen_pre = {s: round(value(E[s])) for s in E}
sens_r = {f'{d:+d}bp': stats(grid(r=R + d / 1e4), CK['5ty'])['center'] for d in (-100, -50, 50, 100)}
sens = {
    'RONIC=ROE5Y_18.3%_g4%': stats(grid(ronic=0.1833, g=0.04), CK['5ty'])['center'],
    'den_bu_BH1_+100ty': stats(grid(comp=100.0), CK['5ty'])['center'],
    'khong_gian_doan': stats([(value(E[s], de, npv, 0.0), ws * wd * wn, s) for (s, ws), (de, wd), (npv, wn) in itertools.product(
        zip(('XAU', 'CO_SO', 'TOT'), A['norm_np']['weights']), zip(A['norm_np']['dE_axis'], A['norm_np']['dE_w']), zip(NT['axis_npv_frac'], NT['axis_w']))], CK['5ty'])['center'],
    'lai_tien_gui_tinh_trong_E_khong_cong_tien_rong': round((E['CO_SO'] / R - NCI) * 1e9 / SH),
    'P/E_bang_gia_tren_E_CO_SO': round(PX * SH / 1e9 / E['CO_SO'], 2),
    'P/E_TTM': round(PX * SH / 1e9 / ttm, 2),
    'P/B_me': round(PX * SH / 1e9 / BS['equity_parent'], 2),
}
# r ngam dinh de tam (sau CK 5 ty) = gia
lo, hi = 0.06, 0.135
for _ in range(60):
    mid = (lo + hi) / 2
    (lo, hi) = (mid, hi) if stats(grid(r=mid), CK['5ty'])['center'] > PX else (lo, mid)
r_impl = (lo + hi) / 2
# E ngam dinh (CO_SO) de gia tri tai tham so trung tam = gia
e_impl = ((PX * SH / 1e9 - NET_CASH + NCI) * R) + INT_AT
out = dict(r=R, dep12=DEP12, price=PX, price_date=PXD, hist_np_parent_ty={str(k): round(v, 2) for k, v in yr.items()}, ttm=round(ttm, 2),
           nine_m26=round(nine_m26, 3), nine_m25=round(nine_m25, 3), q3_26=q['2026Q3'], q3_25=q['2025Q3'], q2_26=q['2026Q2'], q2_25=q['2025Q2'],
           E=E, int_at=INT_AT, net_cash=NET_CASH, nci=NCI, scen_pre=scen_pre, central_param=round(value(E['CO_SO'])),
           pre=pre, post=post, label={k: label(v) for k, v in post.items()}, rule4={k: dict(threshold=round(.85 * v['center']), pass_=PX <= .85 * v['center']) for k, v in post.items()},
           pct_weight_below_price=float(sum(w for v, w, _ in G if v * (1 - CK['5ty']) < PX)),
           liq=dict(sigma_d=sig, adv250=ADV, adv60=ADV60, ck=CK, exit=EXIT, window=f"{last[1]['time']}..{last[-1]['time']}"),
           sens_r=sens_r, sens=sens, r_implied=r_impl, dep12_implied=r_impl - 0.135 + 0.074, E_parent_implied_ty=e_impl)
json.dump(out, open(os.path.join(H, 'model_out.json'), 'w'), indent=1, ensure_ascii=False, default=float)
print(json.dumps(out, indent=1, ensure_ascii=False, default=float))
