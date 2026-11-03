"""SAU KHOA (LOCK_md5_r8.txt 20:58:31). Gia dong cua MVC 03/11/2026 = 13.300 (DNSE close G1, da doc o r7 20:26 ICT; cung phien).
Trung thuc: r1-r7 da biet gia => khoa chi chung minh thu tu chay; mo hinh khong dung gia thi truong lam dau vao."""
import sys, json, csv, numpy as np
sys.dont_write_bytecode = True
import model_r8 as V
PX = 13300; PX_NNC = 46100
o = json.load(open('model_r8_out.json')); tam = o['tam']; gp = {(int(k) if k.isdigit() else k): v for k, v in o['grid_pct'].items()}
rows = list(csv.DictReader(open('grid_r8.csv'))); g = np.array([float(r['ev']) for r in rows])
band = 'RE (duoi P10)' if PX <= gp[10] else 'RE CO DIEU KIEN' if PX <= gp[25] else 'HOP LY' if PX <= gp[75] else 'NGHIENG DAT' if PX <= gp[90] else 'DAT'
print(f'Gia {PX:,} = {PX/tam:.2f}x tam {tam:,.0f} | {PX/gp[50]:.2f}x P50 | P/B {PX/V.S.BVPS:.2f}x | luoi < gia {np.mean(g<PX):.2%} (min {g.min():,.0f}) | gia/P10 {PX/gp[10]-1:+.1%} -> {band}')
for tm in ('0.25', '0.3', 'nnc'):
    s = np.array([float(r['ev']) for r in rows if r['tl_m'] == tm]); print(f'  tl_m={tm}: < gia {np.mean(s<PX):.2%}; P10 {np.percentile(s,10):,.0f}')
for n, b in o['branches'].items(): print(f'  nhanh {n}: {b["V_MVC"]:,.0f} -> gia/gia tri {PX/b["V_MVC"]:.2f}x')
for tm, d in o['tl_margin_axis'].items(): print(f'  bien Tan Lap {tm}: tam {d["V_MVC"]:,.0f} ({PX/d["V_MVC"]-1:+.0%}) | CYC {d["CYC"]:,.0f} ({d["CYC"]/PX-1:+.0%} so gia)')
gor = o['gordon']; print(f'Gordon tron {gor["tron"]["ps"]:,.0f} ; CYC {gor["CYCLICAL"]["ps"]:,.0f} ; ROE ham y gia {0.03+PX/V.S.BVPS*0.10:.1%}')
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
    ev_ = V.N4.eff_vol(vol); ctl = V.R.costA(V.R.BASE) * V.fixfac(ev_); tl = 0.91 * m
    be[lab] = dict(cap_nnc=m, tl_price=tl, tl_margin=1 - ctl / tl, nnc_margin=1 - V.N4.unit_cost(ev_) / m)
    print(f'Hoa von (100% hoi bien, {lab}): gia da NNC {m:.0f}k (tien 2026) = Tan Lap {tl:.0f}k -> bien Tan Lap {be[lab]["tl_margin"]:.1%}, bien NNC {be[lab]["nnc_margin"]:.1%} (tran {V.N4.cap_for(ev_):.0f}k)')
x = V.EV8({'VN_fix': PX_NNC}); print(f'Tham chieu (khong vao tam): V_NNC = thi gia NNC {PX_NNC:,} -> MVC {x:,.0f} ({x-tam:+,.0f})')
json.dump(dict(px=PX, band=band, tam=tam, frac_below=float(np.mean(g < PX)), breakeven=be, mvc_at_nnc_mkt=x), open('compare_r8_out.json', 'w'), indent=1)
