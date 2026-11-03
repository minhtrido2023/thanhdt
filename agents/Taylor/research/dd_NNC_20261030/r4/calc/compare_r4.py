"""SAU KHOA (LOCK_md5_r4.txt 20:24:58). Gia dong cua NNC 03/11/2026 = 46.100 (DNSE close_price G1, verify_account_snapshot.dnse_close_prices,
nguon 'dnse_g1_today', doc ~20:26 ICT). Trung thuc: r1-r3 da biet gia => khoa chi chung minh thu tu chay."""
import sys, json, csv, numpy as np
sys.dont_write_bytecode = True
import model_r4 as N
PX = 46100
o = json.load(open('model_r4_out.json')); tam = o['tam']; gp = {(int(k) if k.isdigit() else k): v for k, v in o['grid_pct'].items()}
g = np.array([float(r['ev']) for r in csv.DictReader(open('grid_r4.csv'))])
print(f'Gia {PX:,} = {PX/tam:.2f}x tam {tam:,.0f} | {PX/gp[50]:.2f}x P50 | P/B {PX/N.N3.BVPS_NNC:.2f}x | luoi < gia {np.mean(g<PX):.1%} (min {g.min():,.0f}) | gia/P10 {PX/gp[10]-1:+.1%}')
band = 'RE (duoi P10)' if PX <= gp[10] else 'RE CO DIEU KIEN' if PX <= gp[25] else 'HOP LY' if PX <= gp[75] else 'NGHIENG DAT' if PX <= gp[90] else 'DAT'
print('Vung (nguong dang ky truoc):', band)
print(f'ROE ben ham y cua GIA (Gordon r13 g3): {0.03+PX/N.N3.BVPS_NNC*0.10:.1%} | ROE chuan hoa tron Bobby {o["gordon"]["roe_norm"]:.1%}')
for n, b in o['branches'].items(): print(f'  nhanh {n}: {b["V_NNC"]:,.0f} -> gia/gia tri {PX/b["V_NNC"]:.2f}x')
# dieu kien hoa von: 100% hoi bien tron (stress 1, moi kich ban) voi tran = X ; tim X de tam = gia
def ev_at(cap, vol):
    old = N.S.P_CYC; N.S.P_CYC = cap
    try: return N.N3.EV3({'stress': 1.0, 'nnc_vol': vol, 'tl_vol': vol})
    finally: N.S.P_CYC = old
out = {}
for lab, vol in [('SL 1,10/1,20', (1.10, 1.20)), ('SL 1,40', (1.40, 1.40)), ('SL 1,05', (1.05, 1.05))]:
    lo, hi = 120.0, 400.0
    for _ in range(50):
        m = (lo + hi) / 2
        if ev_at(m, vol) > PX: hi = m
        else: lo = m
    ev_ = N.eff_vol(vol); cu = N.unit_cost(ev_)
    out[lab] = dict(cap=m, gpm=1 - cu / m)
    print(f'Hoa von (100% hoi bien, {lab}): gia da {m:.0f}k/m3 (tien 2026) -> bien da {1-cu/m:.1%} o SL TB {ev_:.2f} '
          f'(TB chu ky {N.GPM_STONE:.1%}; tran tam {N.cap_for(ev_):.0f}k)')
s = o['sc3']; print(f'3 nhanh: tich cuc (STRUCTURAL) {s["tich_cuc"]:,.0f} | co so (ADMIN) {s["co_so"]:,.0f} | tieu cuc (CYCLICAL) {s["tieu_cuc"]:,.0f}')
json.dump(dict(px=PX, band=band, tam=tam, frac_below=float(np.mean(g < PX)), breakeven=out), open('compare_r4_out.json', 'w'), indent=1)
