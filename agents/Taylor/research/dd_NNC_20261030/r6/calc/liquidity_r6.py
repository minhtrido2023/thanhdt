"""SAU KHOA (LOCK_md5_r6.txt) — chiet khau thanh khoan theo phuong phap DANG KY TRUOC trong docstring nnc_model_r6.py. Dung chung cho NNC r6 va MVC r9.
Nguon: bq_liq_nnc_mvc_20261103.csv = tav2_bq.ticker (alias t) ticker IN (NNC,MVC), time >= 2025-09-01, cot Close (dieu chinh), Price (chua dieu chinh), Volume.
Free float (uoc tu co dong lon): NNC 36,3% (FPTS 07/01/2026: co dong lon nam 63,7%); MVC 30,2% (BCTN 2025: 4 co dong lon 69,8%).
Khong co so lieu thuc thi cua quy cho NNC/MVC trong data/execution_logs (grep 0 dong) => Y khong hieu chinh noi bo; Y=1,0 la he so luat can bac hai
pho bien trong nghien cuu thuc nghiem (Almgren et al. 2005; Toth et al. 2011 bao Y bac 1) — do nhay Y 0,5/1,5."""
import csv, json, math, numpy as np
rows = list(csv.DictReader(open('bq_liq_nnc_mvc_20261103.csv')))
FF = {'NNC': 0.363, 'MVC': 0.302}; QS = (1e9, 5e9, 10e9); YS = (0.5, 1.0, 1.5); N = 250
out = {}
for tk in ('NNC', 'MVC'):
    d = [r for r in rows if r['ticker'] == tk][-N - 1:]
    c = np.array([float(r['Close']) for r in d]); p = np.array([float(r['Price']) for r in d]); v = np.array([float(r['Volume']) for r in d])
    val = (p * v)[1:]; lr = np.diff(np.log(c)); sig = float(np.std(lr, ddof=1))
    adv_med, adv_mean = float(np.median(val)), float(np.mean(val)); zero = float(np.mean(v[1:] == 0))
    m = val > 0; ill = np.abs(lr[m]) / (val[m] / 1e9)            # |r| tren 1 ty d gia tri giao dich
    ill_med = float(np.median(ill))
    o = dict(window=f'{d[1]["time"]}..{d[-1]["time"]}', n=len(val), adv_med=adv_med, adv_mean=adv_mean, sigma_d=sig, zero_vol_share=zero,
             amihud_med_per_bn=ill_med, amihud_mean_per_bn=float(np.mean(ill)), free_float=FF[tk], last_price=float(p[-1]), last_date=d[-1]['time'], pos={})
    print(f'{tk} {o["window"]} N={len(val)}: ADV trung vi {adv_med/1e9:.2f} ty | TB {adv_mean/1e9:.2f} ty | sigma ngay {sig:.2%} | phien 0 KL {zero:.1%} | Amihud trung vi {ill_med:.4f}/ty | free float {FF[tk]:.1%}')
    for q in QS:
        dq = {f'Y{y}': y * sig * math.sqrt(q / adv_med) for y in YS}
        days = {f'p{int(pp*100)}': q / (pp * adv_med) for pp in (0.10, 0.15, 0.20)}
        ami = ill_med * 0.15 * adv_med / 1e9                        # tac dong moi phien khi ban 15% ADV (Amihud trung vi)
        o['pos'][f'{q/1e9:.0f}'] = dict(disc=dq, days=days, amihud_day15=ami)
        print(f'   vi the {q/1e9:>4.0f} ty: CK Y0,5/1,0/1,5 = {dq["Y0.5"]:.1%}/{dq["Y1.0"]:.1%}/{dq["Y1.5"]:.1%} | phien thoat 10%/15%/20% ADV = {days["p10"]:.0f}/{days["p15"]:.0f}/{days["p20"]:.0f} | Amihud/phien @15% {ami:.1%}')
    out[tk] = o
json.dump(out, open('liquidity_r6_out.json', 'w'), indent=1)
