"""SAU KHOA (LOCK_md5_r5.txt). Gia dong cua NNC 03/11/2026 = 46.100 (DNSE close G1, da doc o r4 ~20:26 ICT; cung phien).
Trung thuc: r1-r4 da biet gia => khoa chi chung minh thu tu chay; mo hinh khong dung gia thi truong lam dau vao."""
import sys, json, csv, numpy as np
sys.dont_write_bytecode = True
import nnc_model_r5 as N
N4 = N.N4; PX = 46100
o = json.load(open('nnc_model_r5_out.json')); tam = o['tam']; gp = {(int(k) if k.isdigit() else k): v for k, v in o['grid_pct'].items()}
g = np.array([float(r['ev']) for r in csv.DictReader(open('grid_r5.csv'))])
band = 'RE (duoi P10)' if PX <= gp[10] else 'RE CO DIEU KIEN' if PX <= gp[25] else 'HOP LY' if PX <= gp[75] else 'NGHIENG DAT' if PX <= gp[90] else 'DAT'
print(f'Gia {PX:,} = {PX/tam:.2f}x tam {tam:,.0f} | {PX/gp[50]:.2f}x P50 | P/B {PX/N.N3.BVPS_NNC:.2f}x | luoi < gia {np.mean(g<PX):.1%} (min {g.min():,.0f}) | gia/P10 {PX/gp[10]-1:+.1%} -> {band}')
for n, b in o['branches'].items(): print(f'  nhanh {n}: {b["V_NNC"]:,.0f} -> gia/gia tri {PX/b["V_NNC"]:.2f}x')
gor = o['gordon']; print(f'Gordon ban khoa {gor["tron_roe_lock"]["ps"]:,.0f} ({PX/gor["tron_roe_lock"]["ps"]-1:+.0%} gia so Gordon) | bo sung {gor["tron_roe_fin"]["ps"]:,.0f} ({PX/gor["tron_roe_fin"]["ps"]-1:+.0%})')
def ev_at(cap, vol):
    old = N.S.P_CYC; N.S.P_CYC = cap
    try: return N.N3.EV3({'stress': 1.0, 'nnc_vol': vol, 'tl_vol': vol})
    finally: N.S.P_CYC = old
be = {}
for lab, vol in [('SL 1,10/1,20', (1.10, 1.20)), ('SL 1,40', (1.40, 1.40)), ('SL 1,05', (1.05, 1.05)), ('SL 1,20/1,30', (1.20, 1.30))]:
    lo, hi = 120.0, 400.0
    for _ in range(50):
        m = (lo + hi) / 2
        if ev_at(m, vol) > PX: hi = m
        else: lo = m
    cu = N4.unit_cost(N4.eff_vol(vol)); be[lab] = dict(cap=m, gpm=1 - cu / m)
    print(f'Hoa von (100% hoi bien, {lab}): gia da {m:.0f}k/m3 (tien 2026) -> bien {1-cu/m:.1%}')
json.dump(dict(px=PX, band=band, tam=tam, frac_below=float(np.mean(g < PX)), pb=PX / N.N3.BVPS_NNC, breakeven=be), open('compare_r5_out.json', 'w'), indent=1)
