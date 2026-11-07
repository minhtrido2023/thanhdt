"""PVP — bo sung 3c (5F), job Taylor_20261107_131638. KHONG sua model_r2.py; import va bien the tham so.
Bien the: CUR (tai lap r2) | A: EBITDA doi tau ve TB chu ky (proxy) | B: NPV tau moi = 0 moi kich ban (RONIC=Ke thuan) | AB | WIDE gia dinh (khong co bang chung)."""
import copy, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); CALC = os.path.dirname(HERE)
sys.path.insert(0, CALC); sys.path.insert(0, os.path.abspath(os.path.join(CALC, '../../_common_014127')))
os.chdir(CALC)
import model_r2 as R, model as M1, common_r2 as R2
PX, D_REF = 18400.0, json.load(open('../SUMMARY.json'))['liq_disc_5ty']
D40 = json.load(open('../SUMMARY.json'))['ck_real_sleeve']['40tr']['disc_adv250']
# proxy TB chu ky: BQ ticker_financial PVP EBITDA_P0 (TTM) Q4 2016-2025 TB 431 / 2026Q3 TTM 700 = 0,616; ap len EBITDA doi tau 9T/26 nam hoa 561
EB_HIST_MEAN, EB_NOW = 431.0, 700.0
FLEET_CYC = EB_HIST_MEAN / EB_NOW * (M1.VT_EBITDA_9T * 4 / 3)
W_MEAN = sum(c['w'] * c['ebitda'] for c in M1.SCN.values())
K = FLEET_CYC / W_MEAN
ORIG = copy.deepcopy(M1.SCN)
def run(k_eb=1.0, npv=R.SHIP_NPV, d=D_REF):
    for s in M1.SCN: M1.SCN[s]['ebitda'] = ORIG[s]['ebitda'] * k_eb
    v, w = R.grid(npv)
    out = R2.summarize_r2(v, w, R.mean(v, w), R.value_ps('coso', 6, R2.C.r_now(), 'ca_hai', 'thanh_tien'), PX, d)
    for s in M1.SCN: M1.SCN[s]['ebitda'] = ORIG[s]['ebitda']
    return {x: out[x] for x in ('center_post', 'p10_out', 'p50_out', 'p90_out', 'pct_weight_below_price', 'label')}
Z = {'xau': 0.0, 'coso': 0.0, 'tot': 0.0}
WIDE = {s: v + 0.20 for s, v in R.SHIP_NPV.items()}
res = dict(fleet_cyc_proxy=FLEET_CYC, w_mean_ebitda=W_MEAN, k=K,
           CUR=run(), A_ebitda_cycle=run(K), B_npv0=run(1.0, Z), AB=run(K, Z), WIDE_hyp=run(1.0, WIDE),
           A_sleeve40=run(K, d=D40), CUR_sleeve40=run(d=D40))
json.dump(res, open(os.path.join(HERE, 'addendum_5f_out.json'), 'w'), indent=1, ensure_ascii=False)
print(json.dumps(res, ensure_ascii=False, indent=0))
