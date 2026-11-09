"""GAS DD (v2: hoi quy NAM) 09/11/2026 — mo hinh gia tri noi tai (mu gia thi truong). Tai lap: python3 model.py > model_out.txt
Doc: assumptions.json, bq_fin_gas.csv, brent_q.csv, px_gas_daily_20261106.csv. Khong goi mang."""
import csv, json, math, itertools, os
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); A = json.load(open(os.path.join(H, 'assumptions.json')))
SH = A['shares']; R = A['r']['value']

# 1) LN NAM (ty) tu BQ ticker_financial (cong 4 quy) vs Brent TB nam
import collections
npy = collections.defaultdict(float); cnt = collections.Counter()
for r in csv.DictReader(open(os.path.join(H, 'np_hist_gas.csv'))):
    y = int(r['quarter'][:4]); npy[y] += float(r['np_bn']); cnt[y] += 1
bry = {int(r['y']): float(r['brent']) for r in csv.DictReader(open(os.path.join(H, 'brent_y.csv')))}
M = A['op_np_model']; Y = list(range(M['years'][0], M['years'][1] + 1))
yv = {y: npy[y] + (M['adj_2025_bn'] if y == 2025 else 0) for y in Y}
x = np.array([bry[y] for y in Y]); yy = np.array([yv[y] for y in Y])
b, a = np.polyfit(x, yy, 1); r2 = 1 - ((yy - (a + b * x)) ** 2).sum() / ((yy - yy.mean()) ** 2).sum(); n = len(Y)
xbar = float(x.mean())
INT_AT = A['interest_income_9T_bn'] / 3 * 4 * (1 - A['tax_rate_interest'])
BR_TTM = float(np.mean([float(r['brent']) for r in csv.DictReader(open(os.path.join(H, 'brent_q.csv'))) if r['q'] in ('2025-Q4', '2026-Q1', '2026-Q2', '2026-Q3')]))
NP_TTM = npy[2026] + float([r for r in csv.DictReader(open(os.path.join(H, 'np_hist_gas.csv'))) if r['quarter'] == '2025Q4'][0]['np_bn'])
RES = NP_TTM - 492.2 * 0.8 - (a + b * BR_TTM)
U = [0.5]
def op_np_year(br, bm): return a + b * xbar + b * bm * (br - xbar) - INT_AT + U[0] * RES
qs = Y; np_q = yv; brent = bry
# hoi quy quy cu (chi de doi chieu)
rows = {r['quarter']: r for r in csv.DictReader(open(os.path.join(H, 'bq_fin_gas.csv')))}
bq_ = {r['q']: float(r['brent']) for r in csv.DictReader(open(os.path.join(H, 'brent_q.csv')))}
def back(q, k):
    yy_, nn = int(q[:4]), int(q[-1]); nn -= k
    while nn <= 0: nn += 4; yy_ -= 1
    return f'{yy_}-Q{nn}'
npq = {}
for anchor in ('2026Q3', '2025Q2'):
    for k in range(8): npq.setdefault(back(anchor, k), float(rows[anchor][f'NP_P{k}']) / 1e9)
qq = [q for q in sorted(npq) if q in bq_ and q != '2025-Q2']
bq_fit = np.polyfit([bq_[q] for q in qq], [npq[q] for q in qq], 1)
a2, b2, r22, n2 = float(bq_fit[1]), float(bq_fit[0]), None, len(qq)
resid_2026_9T = npy[2026] - (a + b * bry[2026]) * 0.75
NB = A['net_cash_bridge_bn']; NC = sum(v for k, v in NB.items() if k != 'basis')
ARO = A['aro_provision_343_bn']
T27, T28 = 1.14, 2.14   # 09/11/2026 -> 31/12/2027, 31/12/2028

def value(sc, bm, aro_f, dlr, r=R, with_aro=True):
    S = A['scenarios'][sc]; lr = S['brent_lr'] + dlr; d = S['decline']
    q4 = op_np_year(S['brent_q4_26'], bm) / 4
    n27 = op_np_year(S['brent_2027'], bm); n28 = op_np_year(S['brent_2028'], bm) * (1 - d)
    n29 = op_np_year(lr, bm) * (1 - d) ** 2
    tv = n29 / (r + d)
    ev = q4 + n27 / (1 + r) ** T27 + n28 / (1 + r) ** T28 + tv / (1 + r) ** T28
    eq = ev + NC - (aro_f * ARO if with_aro else 0)
    return eq * 1e9 / SH

def wq(vals, w, p):
    o = np.argsort(vals); v = np.array(vals)[o]; c = np.cumsum(np.array(w)[o]); c = (c - 0.5 * np.array(w)[o]) / c[-1]
    return float(np.interp(p, c, v))

def grid(r=R, scen_w=None):
    V, W = [], []
    for sc in ('XAU', 'CO_SO', 'TOT'):
        ws = (scen_w or {}).get(sc, A['scenarios'][sc]['w'])
        for (bm, wb), (af, wa), (dl, wl), (u, wu) in itertools.product(zip(A['op_np_model']['b_axis']['values'], A['op_np_model']['b_axis']['w']),
                                                              zip(A['aro_axis']['values'], A['aro_axis']['w']), zip(A['lr_axis']['values'], A['lr_axis']['w']),
                                                              zip(A['residual_axis']['values'], A['residual_axis']['w'])):
            U[0] = u; V.append(value(sc, bm, af, dl, r)); W.append(ws * wb * wa * wl * wu)
    U[0] = 0.5
    V, W = np.array(V), np.array(W); c = float((V * W).sum() / W.sum())
    return dict(n=len(V), center=c, p10=wq(V, W, .1), p25=wq(V, W, .25), p50=wq(V, W, .5), p75=wq(V, W, .75), p90=wq(V, W, .9), min=float(V.min()), max=float(V.max()), V=V, W=W)

# 2) thanh khoan (tien le FPT r3)
px = list(csv.DictReader(open(os.path.join(H, 'px_gas_daily_20261106.csv'))))
def liq(n):
    d = px[-n - 1:]; c = np.array([float(r['Close']) for r in d]); p = np.array([float(r['Price']) for r in d]); v = np.array([float(r['Volume']) for r in d])
    val = (p * v)[1:]; sig = float(np.std(np.diff(np.log(c)), ddof=1)); adv = float(np.median(val))
    return dict(window=f"{d[1]['time']}..{d[-1]['time']}", adv_med=adv, sigma_d=sig, ck={f'{q:.0f}': sig * math.sqrt(q / adv) for q in A['liquidity']['sizes']}, part={f'{q:.0f}': q / adv for q in A['liquidity']['sizes']})
L250, L60 = liq(250), liq(60); PX = float(px[-1]['Price'])

G = grid()
out = dict(price=PX, price_date=px[-1]['time'], r=R,
           regression=dict(a=a, b=b, r2=r2, n=n, xbar=xbar, years=Y, BR_TTM=BR_TTM, NP_TTM=NP_TTM, RES=RES, quarterly_fit_rejected=dict(a_q=a2, b_q=b2, n=n2), resid_2026_9T=resid_2026_9T),
           np_year_adj={y: round(yv[y]) for y in Y}, brent_y={y: bry[y] for y in Y},
           int_after_tax_yr=INT_AT, net_cash_bn=NC, net_cash_per_sh=NC * 1e9 / SH,
           op_np_year_at={br: round(op_np_year(br, 1.0)) for br in (60, 62, 70, 72, 75, 80, 85, 90, 100)},
           scen_central={sc: value(sc, 1.0, 0.5, 0) for sc in ('XAU', 'CO_SO', 'TOT')},
           pre={k: v for k, v in G.items() if k not in ('V', 'W')}, liq250=L250, liq60=L60)
ck5 = L250['ck']['5000000000']; ck40 = L250['ck']['40000000']
out['post_5ty'] = {k: (v * (1 - ck5) if isinstance(v, float) else v) for k, v in out['pre'].items()}
out['post_40tr'] = {k: (v * (1 - ck40) if isinstance(v, float) else v) for k, v in out['pre'].items()}
out['pct_weight_below_price'] = float(G['W'][G['V'] * (1 - ck5) < PX].sum() / G['W'].sum())
# do nhay r theo lai huy dong
out['sens_r'] = {f'{bp:+d}bp': grid(R + bp / 1e4)['center'] * (1 - ck5) for bp in (-100, -50, 50, 100)}
# implied: r lam tam = gia
lo, hi = 0.02, 0.30
for _ in range(60):
    m = (lo + hi) / 2
    if grid(m)['center'] * (1 - ck5) > PX: lo = m
    else: hi = m
out['implied_r'] = m
# implied Brent LR (CO_SO, b=1, aro 50%) lam gia tri = gia
lo, hi = 20.0, 600.0
for _ in range(60):
    m2 = (lo + hi) / 2
    v = value('CO_SO', 1.0, 0.5, m2 - A['scenarios']['CO_SO']['brent_lr']) * (1 - ck5)
    if v > PX: hi = m2
    else: lo = m2
out['implied_brent_lr_coso'] = m2
# do nhay ngoai luoi (moi mot thay doi tren tam)
c0 = out['post_5ty']['center']
out['sens_offgrid_dong_per_share'] = {
    'truy_thu_cuoc_ong_-1500ty': -1500e9 / SH * (1 - ck5),
    'lo_ton_kho_LPG_-250ty_truoc_thue': -250e9 * 0.8 / SH * (1 - ck5),
    'khong_tru_co_tuc_phai_tra': 5491.7e9 / SH * (1 - ck5)}
# moat WIDE gia dinh (chi thong tin): khong suy giam o moi kich ban
sv = {sc: dict(A['scenarios'][sc]) for sc in A['scenarios'] if sc != 'basis'}
for sc in sv: A['scenarios'][sc]['decline'] = 0.0
out['sens_moat_wide_no_decline'] = grid()['center'] * (1 - ck5) - c0
for sc in sv: A['scenarios'][sc]['decline'] = sv[sc]['decline']
for sc in sv: A['scenarios'][sc]['decline'] = sv[sc]['decline'] + 0.03
out['sens_moat_none_decline_plus3pp'] = grid()['center'] * (1 - ck5) - c0
for sc in sv: A['scenarios'][sc]['decline'] = sv[sc]['decline']
print(json.dumps(out, indent=1, default=float, ensure_ascii=False))
