"""CSV DD r3 (23/11/2026) - MU GIA. Chay tu thu muc CSV/: /home/trido/thanhdt/wc_venv/bin/python -I calc/model_r3.py
Doc calc/assumptions_r3.json + calc/fin_csv_bq.csv; ghi calc/model_r3_out.json. KHONG doc gia."""
import csv, json, os, itertools
import numpy as np
H = os.path.dirname(os.path.abspath(__file__))
A = json.load(open(os.path.join(H, 'assumptions_r3.json')))
SH = A['shares']; BS = A['bs_30_09_2026_ty']; NT = A['nhon_trach']; N = A['norm_np']
R0 = 0.135 + 1.0 * (A['dep12'] - 0.074)
q = {r['quarter']: float(r['NP_P0']) / 1e9 for r in csv.DictReader(open(os.path.join(H, 'fin_csv_bq.csv')))}
yr = {y: sum(q[f'{y}Q{i}'] for i in range(1, 5)) for y in range(2017, 2026) if all(f'{y}Q{i}' in q for i in range(1, 5))}
hist = [yr[y] for y in range(2019, 2026)]
ttm = q['2025Q4'] + q['2026Q1'] + q['2026Q2'] + q['2026Q3']
E = dict(XAU=min(hist), CO_SO=float(np.mean(hist)), TOT=ttm)
INT_AT = A['interest_income_9T_ty'] * 4 / 3 * (1 - A['tax_rate'])
WF = A['welfare_appropriation_pct_of_npat']
NET_CASH = BS['cash_110'] + BS['st_deposit_121'] - BS['st_debt_321'] - BS['lt_debt'] - BS['welfare_fund_323'] - BS['rnd_fund_344']
NCI = BS['nci_429']; C = NT['capex_total_ty']; S = NT['spent_book_ty']; REM = C - S

def value(e, de=0.0, phi=0.65, t=1.75, npv=0.0, r=R0, adv=0.0, comp=0.0, dis=0.0, cycle=False, ronic=None, g=0.0):
    ecore = (e * (1 + de) - INT_AT) * (1 - WF)
    mult = 1 / r if ronic is None else (1 - g / ronic) / (r - g)
    rem = REM - adv                                   # neu ung truoc la Nhon Trach thi phan con chi giam
    spent = S + adv
    repl_out = phi * rem / (1 + r) ** t               # D3: capex thay the con chi = dong tien ra (PV)
    if cycle:                                         # do nhay: thay the lap lai moi 30 nam
        L = A['perpetual_replacement_sens_life_years']; repl_out += phi * C / (1 + r) ** (t + L) / (1 - (1 + r) ** -L)
    growth_book = (1 - phi) * spent                   # phan tang truong da chi = tai san gia von (NPV=0)
    eq = ecore * mult + NET_CASH - NCI + growth_book - repl_out + npv * (1 - phi) * C + comp + dis * ecore
    return eq * 1e9 / SH

def wpct(v, w, p):
    o = np.argsort(v); v = np.asarray(v)[o]; w = np.asarray(w)[o]; c = (np.cumsum(w) - w / 2) / w.sum()
    return float(np.interp(p, c, v))

def grid(r=R0, phis=None, phw=None, dis_axis=(0.0,), dis_w=(1.0,), **kw):
    phis = phis or NT['replacement_share_axis']; phw = phw or NT['replacement_share_w']
    out = []
    for (s, ws), (de, wd), (ph, wp), (t, wt), (nv, wn), (di, wdi) in itertools.product(
            zip(('XAU', 'CO_SO', 'TOT'), N['weights']), zip(N['dE_axis'], N['dE_w']), zip(phis, phw),
            zip(NT['remaining_timing_years_axis'], NT['remaining_timing_w']), zip(NT['growth_npv_axis'], NT['growth_npv_w']), zip(dis_axis, dis_w)):
        out.append((value(E[s], de, ph, t, nv, r=r, dis=di, **kw), ws * wd * wp * wt * wn * wdi))
    return out

def stats(g):
    v = [x[0] for x in g]; w = [x[1] for x in g]
    return dict(center=round(float(np.dot(v, w) / sum(w))), p10=round(wpct(v, w, .1)), p25=round(wpct(v, w, .25)), p50=round(wpct(v, w, .5)),
                p75=round(wpct(v, w, .75)), p90=round(wpct(v, w, .9)), min=round(min(v)), max=round(max(v)), n=len(v))

G = grid()
base = stats(G)
scen = {s: round(value(E[s])) for s in E}
sens_r = {f'{d:+d}bp': stats(grid(r=R0 + d / 1e4))['center'] for d in (-100, -50, 50, 100)}
ke_band = {f'Ke_{k}': stats(grid(r=k))['center'] for k in (0.123, 0.134)}
sens_beta05 = {f'beta0.5_{d:+d}bp': stats(grid(r=R0 + 0.5 * d / 1e4))['center'] for d in (-100, 100)}
sens = {
    'phi=1.0_(skeptic_100%_thay_the)': stats(grid(phis=[1.0], phw=[1.0]))['center'],
    'phi=0.33': stats(grid(phis=[0.33], phw=[1.0]))['center'],
    'phi=0.5': stats(grid(phis=[0.5], phw=[1.0]))['center'],
    'phi=0.8': stats(grid(phis=[0.8], phw=[1.0]))['center'],
    'phi=0_(r2_cach_a)': stats(grid(phis=[0.0], phw=[1.0]))['center'],
    'khong_chiet_khau_thoi_gian_capex_con_lai(t=0)': stats([(value(E[s], de, ph, 0.0, nv), ws * wd * wp * wn) for (s, ws), (de, wd), (ph, wp), (nv, wn) in itertools.product(
        zip(('XAU', 'CO_SO', 'TOT'), N['weights']), zip(N['dE_axis'], N['dE_w']), zip(NT['replacement_share_axis'], NT['replacement_share_w']), zip(NT['growth_npv_axis'], NT['growth_npv_w']))])['center'],
    'thay_the_lap_lai_moi_30_nam': stats(grid(cycle=True))['center'],
    'ung_truoc_200ty_la_NhonTrach(G2)': stats(grid(adv=NT['advance_suspected_ty']))['center'],
    'boi_thuong_BH1_+100ty': stats(grid(comp=100.0))['center'],
    'gian_doan_0/-25/-50_(0.4/0.4/0.2)': stats(grid(dis_axis=A['disruption']['sens_axis'], dis_w=A['disruption']['sens_w']))['center'],
    'gian_doan_nhu_tren_+boi_thuong_100': stats(grid(dis_axis=A['disruption']['sens_axis'], dis_w=A['disruption']['sens_w'], comp=100.0))['center'],
    'moat_thuong_RONIC=ROE5Y_18.3%_g4%': stats(grid(ronic=0.1833, g=0.04))['center'],
    'khong_tru_quy_KTPL/KHCN_(r2)': round(stats(grid())['center'] + (BS['welfare_fund_323'] + BS['rnd_fund_344']) * 1e9 / SH),
}
# V6: V_ngan = trung vi LN 3 nam gan nhat (2023-25) /r + cau noi von; V_dai: FCFE<=0 trong giai doan capex
med3 = float(np.median([yr[2023], yr[2024], yr[2025]]))
v_short = round(value(med3))
out = dict(r=R0, dep12=A['dep12'], hist_np_parent_ty={str(k): round(v, 2) for k, v in yr.items()}, ttm=round(ttm, 2), E=E, int_at=INT_AT,
           welfare_pct=WF, net_cash=NET_CASH, nci=NCI, capex_total=C, spent=S, remaining=REM, scen_central_param=scen,
           pre_ck=base, sens_r=sens_r, ke_band=ke_band, sens_beta05=sens_beta05, sens=sens,
           v6=dict(v_short=v_short, med3_np=med3, v_long='FCFE<=0 (CFO 9T 197,8 - capex 265,7; con ~1.498 ty capex) => chi V_ngan'),
           phi_step_per_0_1=round((sens['phi=0.5'] - sens['phi=0.8']) / 3))
json.dump(out, open(os.path.join(H, 'model_r3_out.json'), 'w'), indent=1, ensure_ascii=False, default=float)
print(json.dumps(out, indent=1, ensure_ascii=False, default=float))
