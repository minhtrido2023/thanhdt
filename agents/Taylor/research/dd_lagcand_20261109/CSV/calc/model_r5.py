"""CSV DD r5 (23/11/2026) - vong skeptic cuoi; khoa lai sau skeptic r3. Chay tu CSV/: /home/trido/thanhdt/wc_venv/bin/python -I calc/model_r5.py
Doc calc/assumptions_r5.json + calc/fin_csv_bq.csv; ghi calc/model_r5_out.json. KHONG doc gia.
Thay doi so voi r4: (1) trich quy KTPL 9,55% (BCTC KT FY2025 TM33); (2) chu ky tai dau tu phan thay the moi N nam trong base;
(3) APV: capex con chi chiet khau o r_commit co dinh + NPV tai tro khoan vay 10 nam (sua sai chieu kd)."""
import csv, json, os, itertools
import numpy as np
H = os.path.dirname(os.path.abspath(__file__))
A = json.load(open(os.path.join(H, 'assumptions_r5.json')))
SH = A['shares']; BS = A['bs_30_09_2026_ty']; NT = A['nhon_trach']; N = A['norm_np']; TAX = A['tax_rate']
R0 = 0.135 + 1.0 * (A['dep12'] - 0.074)
q = {r['quarter']: float(r['NP_P0']) / 1e9 for r in csv.DictReader(open(os.path.join(H, 'fin_csv_bq.csv')))}
yr = {y: sum(q[f'{y}Q{i}'] for i in range(1, 5)) for y in range(2017, 2026) if all(f'{y}Q{i}' in q for i in range(1, 5))}
hist = [yr[y] for y in range(2019, 2026)]
ttm = q['2025Q4'] + q['2026Q1'] + q['2026Q2'] + q['2026Q3']
E = dict(XAU=min(hist), CO_SO=float(np.mean(hist)), TOT=ttm)
INT_AT = A['interest_income_9T_ty'] * 4 / 3 * (1 - TAX)
WF = A['welfare_appropriation_pct_of_npat']
NET_CASH = BS['cash_110'] + BS['st_deposit_121'] - BS['st_debt_321'] - BS['lt_debt'] - BS['welfare_fund_323'] - BS['rnd_fund_344']
NCI = BS['nci_429']; C = NT['capex_total_ty']; S = NT['spent_book_ty']; REM = C - S
DEBT = NT['funding']['debt_ty']; DS = NT['depr_tax_shield']; CY = NT['reinvest_cycle']; APV = NT['apv']
RC = APV['r_commit']; KD = NT['kd_pretax']

def ann(r, L): return (1 - (1 + r) ** -L) / r

def fin_npv(kd, rc=RC, n=10):
    """NPV tai tro tai thoi diem giai ngan: DEBT - PV_rc(goc deu + lai sau thue)."""
    bal = DEBT; pv = 0.0; P = DEBT / n
    for k in range(1, n + 1):
        pv += (P + kd * bal * (1 - TAX)) / (1 + rc) ** k; bal -= P
    return DEBT - pv

def value(e, de=0.0, phi=0.65, t=1.75, npv=0.0, r=R0, adv=0.0, comp=0.0, dis=0.0, ronic=None, g=0.0,
          kd=None, life=None, shield=True, cyc=30, wf=None, elec=0.0, apv=True, rc=None):
    kd = KD if kd is None else kd; L = DS['life_years'] if life is None else life
    wf = WF if wf is None else wf; rc = RC if rc is None else rc
    ecore = (e * (1 + de) - INT_AT + elec * (1 - TAX)) * (1 - wf)
    mult = 1 / r if ronic is None else (1 - g / ronic) / (r - g)
    rem = max(REM - adv, 0.0); spent = S + adv
    if apv:
        repl_out = phi * (rem / (1 + rc) ** t - fin_npv(kd, rc) / (1 + rc) ** t)
    else:  # r4: vay o kd sau thue, VCSH o Ke
        repl_out = phi * (DEBT / (1 + kd * (1 - TAX)) ** t + max(rem - DEBT, 0.0) / (1 + r) ** t)
    sh_f = DS['tax_rate'] / L * ann(r, L) if shield else 0.0
    tax_sh = phi * C * sh_f / (1 + r) ** t
    cyc_out = 0.0
    if cyc:
        X = phi * C * (1 - sh_f)
        cyc_out = X / ((1 + r) ** cyc - 1) / (1 + r) ** t
    growth_book = (1 - phi) * spent
    eq = ecore * mult + NET_CASH - NCI + growth_book - repl_out + tax_sh - cyc_out + npv * (1 - phi) * C + comp + dis * ecore
    return eq * 1e9 / SH

def wpct(v, w, p):
    o = np.argsort(v); v = np.asarray(v)[o]; w = np.asarray(w)[o]; c = (np.cumsum(w) - w / 2) / w.sum()
    return float(np.interp(p, c, v))

SCN = ('XAU', 'CO_SO', 'TOT')
def grid(r=R0, phis=None, phw=None, dis_axis=(0.0,), dis_w=(1.0,), cycs=None, cycw=None, ts=None, tw=None, escen=None, **kw):
    phis = phis or NT['replacement_share_axis']; phw = phw or NT['replacement_share_w']
    cycs = cycs or CY['years_axis']; cycw = cycw or CY['w']
    ts = ts or NT['remaining_timing_years_axis']; tw = tw or NT['remaining_timing_w']
    escen = escen or E
    out = []
    for (s, ws), (de, wd), (ph, wp), (t, wt), (nv, wn), (di, wdi), (cy, wc) in itertools.product(
            zip(SCN, N['weights']), zip(N['dE_axis'], N['dE_w']), zip(phis, phw), zip(ts, tw),
            zip(NT['growth_npv_axis'], NT['growth_npv_w']), zip(dis_axis, dis_w), zip(cycs, cycw)):
        out.append((value(escen[s], de, ph, t, nv, r=r, dis=di, cyc=cy, **kw), ws * wd * wp * wt * wn * wdi * wc))
    return out

def stats(g):
    v = [x[0] for x in g]; w = [x[1] for x in g]
    return dict(center=round(float(np.dot(v, w) / sum(w))), p10=round(wpct(v, w, .1)), p25=round(wpct(v, w, .25)), p50=round(wpct(v, w, .5)),
                p75=round(wpct(v, w, .75)), p90=round(wpct(v, w, .9)), min=round(min(v)), max=round(max(v)), n=len(v))
c = lambda **kw: stats(grid(**kw))['center']

G = grid(); base = stats(G)
scen = {s: round(value(E[s])) for s in E}
# cau noi r4 -> r5 (trong cung khung grid r5)
bridge = {
 'r4_tai_lap(wf2.43%,khong_chu_ky,khong_APV)': c(wf=0.0243, cycs=[None], cycw=[1.0], apv=False),
 '+APV': c(wf=0.0243, cycs=[None], cycw=[1.0]),
 '+chu_ky_N20/30/40': c(wf=0.0243),
 '+quy_KTPL_9.55%(=r5)': base['center'],
}
sens_r = {f'{d:+d}bp': c(r=R0 + d / 1e4) for d in (-100, -50, 50, 100)}
ke_band = {f'Ke_{k}': c(r=k) for k in (0.123, 0.134)}
sens_beta05 = {f'beta0.5_{d:+d}bp': c(r=R0 + 0.5 * d / 1e4) for d in (-100, 100)}
dz = A['disruption']
sens = {
 'phi=1.0': c(phis=[1.0], phw=[1.0]), 'phi=0.8': c(phis=[0.8], phw=[1.0]), 'phi=0.5': c(phis=[0.5], phw=[1.0]),
 'phi=0.33': c(phis=[0.33], phw=[1.0]), 'phi=0': c(phis=[0.0], phw=[1.0]),
 'chu_ky_N=12(skeptic,=L)': c(cycs=[12], cycw=[1.0]), 'chu_ky_N=20': c(cycs=[20], cycw=[1.0]),
 'chu_ky_N=40': c(cycs=[40], cycw=[1.0]), 'khong_chu_ky(r4)': c(cycs=[None], cycw=[1.0]),
 'quy_KTPL_2.43%(r4)': c(wf=0.0243), 'quy_KTPL_11.4%(gom_cty_con)': c(wf=0.114),
 'kd_6.4%': c(kd=0.064), 'kd_9.5%': c(kd=0.095),
 'r_commit_=Ke(capex_o_Ke)': c(rc=R0), 'khong_APV(r4_kd_sau_thue)': c(apv=False),
 'khong_la_chan_thue_KH': c(shield=False), 'doi_KH_8': c(life=8), 'doi_KH_20': c(life=20),
 'TOT=CO_SO(TB2_dung)': c(escen=dict(XAU=E['XAU'], CO_SO=E['CO_SO'], TOT=E['CO_SO'])),
 'gian_doan_0/-25/-50(0.4/0.4/0.2)': c(dis_axis=dz['sens_axis'], dis_w=dz['sens_w']),
 'hoan_nguyen_-100ty': c(comp=-100.0), 'boi_thuong_+100ty': c(comp=100.0),
 'G2_ung_truoc_200ty_la_NT': c(adv=NT['advance_suspected_ty']),
 'dien_+5%(50%_DV_mua_ngoai,uoc_luong)': c(elec=A['electricity']['sens_pretax_ty']),
 'moat_RONIC18.3%_g4%': c(ronic=0.1833, g=0.04),
 't=0(khong_chiet_khau_thoi_gian)': c(ts=[0.0], tw=[1.0]),
}
med3 = float(np.median([yr[2023], yr[2024], yr[2025]]))
out = dict(r=R0, hist_np_parent_ty={str(k): round(v, 2) for k, v in yr.items()}, ttm=round(ttm, 2), E=E, int_at=INT_AT, welfare_pct=WF,
           net_cash=NET_CASH, nci=NCI, capex_total=C, spent=S, remaining=REM, fin_npv_central=fin_npv(KD), scen_central_param=scen,
           pre_ck=base, bridge=bridge, sens_r=sens_r, ke_band=ke_band, sens_beta05=sens_beta05, sens=sens,
           v6=dict(v_short=round(value(med3)), med3_np=med3), phi_step_per_0_1=round((sens['phi=0.5'] - sens['phi=0.8']) / 3))
json.dump(out, open(os.path.join(H, 'model_r5_out.json'), 'w'), indent=1, ensure_ascii=False, default=float)
print(json.dumps(out, indent=1, ensure_ascii=False, default=float))
