"""SAU KHOA (LOCK_md5_r4.txt) — chiet khau thanh khoan DRI theo phuong phap DANG KY TRUOC (docstring dri_model_r4.py; cung cong thuc NNC r6/MVC r9).
Nguon: bq_liq_dri_20261103.csv = tav2_bq.ticker (alias t) ticker='DRI', time >= 2025-09-01; dung 250 phien ket thuc 02/11/2026
(dong 03/11 trong BQ co the chua dong bo du — loai). Free float ~55% (Dakruco 45%, BCTN 2025).
data/execution_logs co lenh DRI cua quy nhung quy mo rat nho (~3.800 cp) => khong du hieu chinh Y; Y=1,0 (luat can bac hai,
Almgren et al. 2005; Toth et al. 2011), do nhay Y 0,5/1,5. Chay: python3 -B liquidity_r4.py (tu thu muc nay)."""
import os, csv, json, math, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
rows = [r for r in csv.DictReader(open('bq_liq_dri_20261103.csv')) if r['time'] <= '2026-11-02']
N = 250; d = rows[-N-1:]
c = np.array([float(r['Close']) for r in d]); p = np.array([float(r['Price']) for r in d]); v = np.array([float(r['Volume']) for r in d])
val = (p*v)[1:]; lr = np.diff(np.log(c)); sig = float(np.std(lr, ddof=1))
adv_med, adv_mean = float(np.median(val)), float(np.mean(val)); zero = float(np.mean(v[1:] == 0))
m = val > 0; ill = np.abs(lr[m])/(val[m]/1e9); ill_med = float(np.median(ill))
adv60 = float(np.median(val[-60:]))
o = dict(window=f'{d[1]["time"]}..{d[-1]["time"]}', n=len(val), adv_med=adv_med, adv_mean=adv_mean, adv_med_60=adv60, sigma_d=sig,
         zero_vol_share=zero, amihud_med_per_bn=ill_med, free_float=0.55, pos={})
print(f'DRI {o["window"]} N={len(val)}: ADV trung vi {adv_med/1e9:.2f} ty | TB {adv_mean/1e9:.2f} ty | trung vi 60 phien {adv60/1e9:.2f} ty'
      f' | sigma ngay {sig:.2%} | phien 0 KL {zero:.1%} | Amihud trung vi {ill_med:.4f}/ty | free float ~55%')
for q in (1e9, 5e9, 10e9):
    dq = {f'Y{y}': y*sig*math.sqrt(q/adv_med) for y in (0.5, 1.0, 1.5)}
    days = {f'p{int(pp*100)}': q/(pp*adv_med) for pp in (0.10, 0.15, 0.20)}
    ami = ill_med*0.15*adv_med/1e9
    o['pos'][f'{q/1e9:.0f}'] = dict(disc=dq, days=days, amihud_day15=ami)
    print(f'   vi the {q/1e9:>3.0f} ty: CK Y0,5/1,0/1,5 = {dq["Y0.5"]:.1%}/{dq["Y1.0"]:.1%}/{dq["Y1.5"]:.1%} | phien thoat 10/15/20% ADV = '
          f'{days["p10"]:.1f}/{days["p15"]:.1f}/{days["p20"]:.1f} | Amihud/phien @15% {ami:.1%}')
M = json.load(open('dri_model_r4_out.json'))
print('\nGIA TRI TRUOC / SAU chiet khau thanh khoan (Y=1):')
o['after'] = {}
for k, dd in o['pos'].items():
    f = 1 - dd['disc']['Y1.0']
    sc = {kk: vv*f for kk, vv in M['scale'].items()}
    o['after'][k] = dict(center=M['center']*f, expected=M['expected']*f, forced=M['forced']*f, scale=sc)
    print(f'   {k:>3} ty: tam {M["center"]:,.0f} -> {M["center"]*f:,.0f} | ky vong {M["expected"]:,.0f} -> {M["expected"]*f:,.0f} | thang '
          + ' / '.join(f'{kk} {vv:,.0f}' for kk, vv in sc.items()))
json.dump(o, open('liquidity_r4_out.json', 'w'), indent=1)
