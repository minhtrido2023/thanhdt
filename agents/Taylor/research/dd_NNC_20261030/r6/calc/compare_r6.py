"""SAU KHOA (LOCK_md5_r6.txt). Gia dong cua NNC 03/11/2026 = Price BQ tav2_bq.ticker 2026-11-03 (= 46.100 da doc o r4 tu DNSE).
Trung thuc: r1-r5 da biet gia => khoa chi chung minh thu tu chay; mo hinh khong dung gia thi truong lam dau vao."""
import sys, json, csv, numpy as np
sys.dont_write_bytecode = True
import nnc_model_r6 as N
N4 = N.N4
L = json.load(open('liquidity_r6_out.json'))['NNC']; PX = L['last_price']; assert L['last_date'] == '2026-11-03'
o = json.load(open('nnc_model_r6_out.json')); tam = o['tam']; gp = {(int(k) if k.isdigit() else k): v for k, v in o['grid_pct'].items()}
g = np.array([float(r['ev']) for r in csv.DictReader(open('grid_r6.csv'))])
def band(px, f=1.0):
    return 'RE (duoi P10)' if px <= gp[10]*f else 'RE CO DIEU KIEN' if px <= gp[25]*f else 'HOP LY' if px <= gp[75]*f else 'NGHIENG DAT' if px <= gp[90]*f else 'DAT'
res = dict(px=PX, tam=tam, band_pre=band(PX), frac_below=float(np.mean(g < PX)), pb=PX / N.N3.BVPS_NNC, liq={})
print(f'Gia {PX:,.0f} = {PX/tam:.2f}x tam {tam:,.0f} | luoi < gia {np.mean(g<PX):.1%} (min {g.min():,.0f}) | TRUOC CK thanh khoan: {res["band_pre"]}')
for q, pz in L['pos'].items():
    for y in ('Y0.5', 'Y1.0', 'Y1.5'):
        d = pz['disc'][y]; f = 1 - d
        res['liq'][f'{q}_{y}'] = dict(d=d, tam=tam*f, p10=gp[10]*f, p25=gp[25]*f, p50=gp[50]*f, p75=gp[75]*f, p90=gp[90]*f, band=band(PX, f))
    x = res['liq'][f'{q}_Y1.0']
    print(f'  vi the {q} ty (Y1,0, CK {x["d"]:.1%}): tam {x["tam"]:,.0f} | P10/25/75/90 {x["p10"]:,.0f}/{x["p25"]:,.0f}/{x["p75"]:,.0f}/{x["p90"]:,.0f} -> {x["band"]}')
res['band_post_5ty'] = res['liq']['5_Y1.0']['band']
for n, b in o['branches'].items(): print(f'  nhanh {n}: {b["V_NNC"]:,.0f} -> gia/gia tri {PX/b["V_NNC"]:.2f}x')
gor = o['gordon']; print(f'Gordon r13,5 khoa {gor["tron_roe_lock"]["ps"]:,.0f} ({PX/gor["tron_roe_lock"]["ps"]-1:+.0%}) | bo sung {gor["tron_roe_fin"]["ps"]:,.0f} ({PX/gor["tron_roe_fin"]["ps"]-1:+.0%})')
def ev_at(cap, vol):
    old = N.S.P_CYC; N.S.P_CYC = cap
    try: return N.N3.EV3({'stress': 1.0, 'nnc_vol': vol, 'tl_vol': vol})
    finally: N.S.P_CYC = old
be = {}
for lab, vol in [('SL 1,10/1,20', (1.10, 1.20)), ('SL 1,40', (1.40, 1.40))]:
    lo, hi = 120.0, 400.0
    for _ in range(50):
        m = (lo + hi) / 2
        if ev_at(m, vol) > PX: hi = m
        else: lo = m
    cu = N4.unit_cost(N4.eff_vol(vol)); be[lab] = dict(cap=m, gpm=1 - cu / m)
    print(f'Hoa von (100% hoi bien, {lab}, r13,5): gia da {m:.0f}k/m3 -> bien {1-cu/m:.1%}')
res['breakeven'] = be
json.dump(res, open('compare_r6_out.json', 'w'), indent=1)
