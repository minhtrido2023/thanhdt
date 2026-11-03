"""SAU KHOA (LOCK_md5_r6.txt 17:37:37). Gia dong cua 03/11/2026 = 13.300 (DNSE close_price MVC board G1, 15:00:01; KL ca phien 1.430 cp).
Trung thuc: r1-r5 da biet gia 13.700 (02/11) va 13.300 (03/11) => khoa md5 chi chung minh thu tu chay, khong chung minh chua tung thay gia."""
import sys, json, csv, numpy as np
sys.dont_write_bytecode = True
import model_r6 as S
PX = 13300; BV = S.BVPS
o = json.load(open('model_r6_out.json')); tam = o['tam']; gp = {(int(k) if k.isdigit() else k): v for k, v in o['grid_pct'].items()}
g = np.array([float(r['ev']) for r in csv.DictReader(open('grid_r6.csv'))])
print(f'Gia {PX:,} = {PX/tam:.2f}x tam {tam:,.0f} | {PX/o["base_co_so"]:.2f}x base | {PX/gp[50]:.2f}x trung vi luoi | P/B {PX/BV:.2f}x | luoi < gia {np.mean(g<PX):.1%} (min {g.min():,.0f})')
band = 'RE (duoi P10)' if PX <= gp[10] else 'RE CO DIEU KIEN' if PX <= gp[25] else 'HOP LY' if PX <= gp[75] else 'NGHIENG DAT' if PX <= gp[90] else 'DAT'
print('Vung:', band)
print(f'ROE ben ham y cua GIA (Gordon r13 g3): {0.03+PX/BV*0.10:.1%} | ROE TB 2017-25 MVC {o["roe_mvc_avg_2017_25"]:.1%}')
cost = S.R.costA(S.R.BASE); peak = 0.91*380 - cost
def frac(s): p = (1-s)*320 + s*S.P_CYC; return (0.91*p - cost)/peak
def f(s): return S.EV({'stress': s}) - PX
lo, hi = 0.0, 3.0
for _ in range(60):
    m = (lo+hi)/2
    if f(m) > 0: lo = m
    else: hi = m
print(f'Tam = gia khi stress s={m:.2f}: bien don vi da cum dai han = {frac(m):.0%} bien dinh 2026 (base dai han {frac(0):.0%}; TB chu ky {frac(1):.0%})')
# kieu skeptic: dieu kien bien an toan - muc bien de P10 luoi (stress do) van >= gia
for s in (1.0, 1.5, 2.0):
    print(f'  stress {s}: tam {S.EV({"stress": s}):,.0f} ; bien dai han {frac(s):.0%} bien dinh')
print(f'V_NNC co dinh 48.000 (tham chieu SKEPTIC4 #9, gia thi truong NNC theo skeptic — Taylor KHONG truy van): MVC {S.EV({"VN_fix": 48000}):,.0f}')
