"""SAU KHOA (LOCK_md5_r7.txt 20:33:44). Gia dong cua MVC 03/11/2026 = 13.300 (DNSE close_price G1 'dnse_g1_today', doc 20:26 ICT cung lenh voi NNC)."""
import sys, json, csv, numpy as np
sys.dont_write_bytecode = True
import model_r7 as V
PX = 13300; PX_NNC = 46100
o = json.load(open('model_r7_out.json')); tam = o['tam']; gp = {(int(k) if k.isdigit() else k): v for k, v in o['grid_pct'].items()}
g = np.array([float(r['ev']) for r in csv.DictReader(open('grid_r7.csv'))])
print(f'Gia {PX:,} = {PX/tam:.2f}x tam {tam:,.0f} | {PX/gp[50]:.2f}x P50 | P/B {PX/V.S.BVPS:.2f}x | luoi < gia {np.mean(g<PX):.1%} (min {g.min():,.0f}) | gia/P10 {PX/gp[10]-1:+.1%}')
band = 'RE (duoi P10)' if PX <= gp[10] else 'RE CO DIEU KIEN' if PX <= gp[25] else 'HOP LY' if PX <= gp[75] else 'NGHIENG DAT' if PX <= gp[90] else 'DAT'
print('Vung (nguong dang ky truoc):', band)
print(f'ROE ben ham y cua GIA (Gordon r13 g3): {0.03+PX/V.S.BVPS*0.10:.1%} | ROE chuan hoa tron {o["gordon"]["tron"]["roe"]:.1%} -> {o["gordon"]["tron"]["ps"]:,.0f}')
for n, b in o['branches'].items(): print(f'  nhanh {n}: {b["V_MVC"]:,.0f} -> gia/gia tri {PX/b["V_MVC"]:.2f}x')
def ev_at(cap, vol):
    old = V.S.P_CYC; V.S.P_CYC = cap
    try: return V.N3.EV3({'stress': 1.0, 'nnc_vol': vol, 'tl_vol': vol}, detail=True)[1]
    finally: V.S.P_CYC = old
be = {}
for lab, vol in [('SL 1,10/1,20', (1.10, 1.20)), ('SL tran 1,40 ca hai mo', (1.40, 1.40))]:
    lo, hi = 100.0, 400.0
    for _ in range(50):
        m = (lo + hi) / 2
        if ev_at(m, vol) > PX: hi = m
        else: lo = m
    tl = 0.91 * m; be[lab] = dict(cap_nnc=m, tl_price=tl, tl_margin=1 - V.R.costA(V.R.BASE) / tl, nnc_margin=1 - V.N4.unit_cost(V.N4.eff_vol(vol)) / m)
    print(f'Hoa von (100% hoi bien, {lab}): gia da NNC {m:.0f}k/m3 (tien 2026) = Tan Lap {tl:.0f}k -> bien Tan Lap {be[lab]["tl_margin"]:.1%}, bien NNC {be[lab]["nnc_margin"]:.1%} (TB chu ky {V.N4.GPM_STONE:.1%})')
# V_NNC theo thi gia (chi tham chieu, trai D1)
x = V.EV7({'VN_fix': PX_NNC}); print(f'Tham chieu (trai D1, khong vao tam): V_NNC = thi gia NNC {PX_NNC:,} -> MVC {x:,.0f} ({x-tam:+,.0f})')
json.dump(dict(px=PX, band=band, tam=tam, frac_below=float(np.mean(g < PX)), breakeven=be, mvc_at_nnc_mkt=x), open('compare_r7_out.json', 'w'), indent=1)
