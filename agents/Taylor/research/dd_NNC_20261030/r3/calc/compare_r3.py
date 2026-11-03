"""SAU KHOA (LOCK_md5_r3.txt 20:04:30). Gia dong cua NNC 03/11/2026 = 46.100 (DNSE dnse_close_prices G1 ~20:10 ICT; BQ ticker Price 03/11 doi chieu).
ADV trung vi (BQ Price*Volume): 20 phien 1,43 / 60 phien 1,38 / 120 phien 1,39 ty/phien."""
import sys, json, csv, numpy as np
sys.dont_write_bytecode = True
import model_r3 as N
PX = 46100
o = json.load(open('model_r3_out.json')); tam = o['tam']; gp = {(int(k) if k.isdigit() else k): v for k, v in o['grid_pct'].items()}
g = np.array([float(r['ev']) for r in csv.DictReader(open('grid_r3.csv'))])
print(f'Gia {PX:,} = {PX/tam:.2f}x tam {tam:,.0f} | {PX/o["base_co_so"]:.2f}x base | {PX/gp[50]:.2f}x P50 | P/B {PX/N.BVPS_NNC:.2f}x | luoi < gia {np.mean(g<PX):.1%} (min {g.min():,.0f})')
band = 'RE (duoi P10)' if PX <= gp[10] else 'RE CO DIEU KIEN' if PX <= gp[25] else 'HOP LY' if PX <= gp[75] else 'NGHIENG DAT' if PX <= gp[90] else 'DAT'
print('Vung:', band)
print(f'ROE ben ham y cua GIA (Gordon r13 g3): {0.03+PX/N.BVPS_NNC*0.10:.1%}')
# dieu kien bien an toan: tran gia cum tu 2028 (moi kich ban) de tam = gia
def f(cap):
    pc = N.S.P_CYC; N.S.P_CYC = cap
    try: return N.EV3({'stress': 1.0}) - PX
    finally: N.S.P_CYC = pc
lo, hi = 120.0, 400.0
for _ in range(50):
    m = (lo + hi) / 2
    if f(m) > 0: hi = m
    else: lo = m
cu = N.M.VAR * 0.97 + N.M.FIX * 0.97 / 1.40
print(f'Tam = gia khi tran gia da cum tu 2028 = {m:.0f}k/m3 (tien 2026, sau do theo duong gia) -> GPM da mo hinh {1-cu/m:.0%} (dinh 2026 ~{1-cu/380:.0%}; GPM NNC TB 2012-25 34%)')
pc = N.S.P_CYC
for cap in (270, 242, 220):
    N.S.P_CYC = cap; print(f'  tran {cap}: tam {N.EV3({"stress": 1.0}):,.0f}')
N.S.P_CYC = pc
# dinh gia nguoc: P(tieu cuc) ham y, giu ti le tich cuc:co so 1:2
s = o['sc3']; up = (s['tich_cuc'] + 2 * s['co_so']) / 3
print(f'P(tieu cuc) ham y o gia {PX:,}: {(up-PX)/(up-s["tieu_cuc"]):.0%} (mo hinh 25%)')
