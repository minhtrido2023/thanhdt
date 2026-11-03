"""SAU KHOA (LOCK_md5_r9.txt). Gia dong cua MVC 03/11/2026 = Price BQ tav2_bq.ticker 2026-11-03 (= 13.300 da doc o r7 tu DNSE).
Thanh khoan: ../../../dd_NNC_20261030/r6/calc/liquidity_r6_out.json (phuong phap dang ky truoc). Trung thuc: r1-r8 da biet gia."""
import sys, os, json, csv, numpy as np
sys.dont_write_bytecode = True
import model_r9 as V
L = json.load(open(os.path.join(V.N6D, 'liquidity_r6_out.json')))['MVC']; PX = L['last_price']; assert L['last_date'] == '2026-11-03'
o = json.load(open('model_r9_out.json')); tam = o['tam']; gp = {(int(k) if k.isdigit() else k): v for k, v in o['grid_pct'].items()}
rows = list(csv.DictReader(open('grid_r9.csv'))); g = np.array([float(r['ev']) for r in rows])
def band(px, f=1.0):
    return 'RE (duoi P10)' if px <= gp[10]*f else 'RE CO DIEU KIEN' if px <= gp[25]*f else 'HOP LY' if px <= gp[75]*f else 'NGHIENG DAT' if px <= gp[90]*f else 'DAT'
res = dict(px=PX, tam=tam, band_pre=band(PX), frac_below=float(np.mean(g < PX)), liq={})
print(f'Gia {PX:,.0f} = {PX/tam:.2f}x tam {tam:,.0f} | P/B {PX/V.S.BVPS:.2f}x | luoi < gia {np.mean(g<PX):.2%} (min {g.min():,.0f}) | TRUOC CK: {res["band_pre"]}')
for q, pz in L['pos'].items():
    for y in ('Y0.5', 'Y1.0', 'Y1.5'):
        d = pz['disc'][y]; f = 1 - d
        res['liq'][f'{q}_{y}'] = dict(d=d, tam=tam*f, p10=gp[10]*f, p25=gp[25]*f, p50=gp[50]*f, p75=gp[75]*f, p90=gp[90]*f, band=band(PX, f))
    for y in ('Y0.5', 'Y1.0', 'Y1.5'):
        x = res['liq'][f'{q}_{y}']
        print(f'  vi the {q} ty ({y}, CK {x["d"]:.1%}): tam {x["tam"]:,.0f} | P10/25/75/90 {x["p10"]:,.0f}/{x["p25"]:,.0f}/{x["p75"]:,.0f}/{x["p90"]:,.0f} -> {x["band"]}')
res['band_post_5ty'] = res['liq']['5_Y1.0']['band']
for n, b in o['branches'].items(): print(f'  nhanh {n}: {b["V_MVC"]:,.0f} -> gia/gia tri {PX/b["V_MVC"]:.2f}x')
for tm, d in o['tl_margin_axis'].items(): print(f'  bien Tan Lap {tm}: tam {d["V_MVC"]:,.0f} | CYC {d["CYC"]:,.0f} ({d["CYC"]/PX-1:+.0%} so gia)')
gor = o['gordon']; print(f'Gordon r13,5 tron {gor["tron"]["ps"]:,.0f} ; CYC {gor["CYCLICAL"]["ps"]:,.0f} ; ROE ham y gia {0.03+PX/V.S.BVPS*0.105:.1%}')
def ev_at(cap, vol, tm):
    old = V.S.P_CYC; V.S.P_CYC = cap
    try: return V.N3.EV3({'stress': 1.0, 'nnc_vol': vol, 'tl_vol': vol, 'tl_m': tm}, detail=True)[1]
    finally: V.S.P_CYC = old
be = {}
for lab, vol in [('SL 1,10/1,20', (1.10, 1.20)), ('SL 1,40', (1.40, 1.40))]:
    lo, hi = 100.0, 400.0
    for _ in range(50):
        m = (lo + hi) / 2
        if ev_at(m, vol, 'nnc') > PX: hi = m
        else: lo = m
    ev_ = V.N4.eff_vol(vol); ctl = V.R.costA(V.R.BASE) * V.V8.fixfac(ev_); tl = 0.91 * m
    be[lab] = dict(cap_nnc=m, tl_price=tl, tl_margin=1 - ctl / tl, nnc_margin=1 - V.N4.unit_cost(ev_) / m)
    print(f'Hoa von (r13,5, {lab}): gia da NNC {m:.0f}k = Tan Lap {tl:.0f}k -> bien Tan Lap {be[lab]["tl_margin"]:.1%}, bien NNC {be[lab]["nnc_margin"]:.1%}')
x = V.EV8({'VN_fix': 46100}); print(f'Tham chieu (khong vao tam): V_NNC = thi gia NNC 46.100 -> MVC {x:,.0f} ({x-tam:+,.0f})')
res['breakeven'] = be; res['mvc_at_nnc_mkt'] = x
json.dump(res, open('compare_r9_out.json', 'w'), indent=1)
