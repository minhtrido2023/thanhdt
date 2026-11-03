"""SAU KHOA (LOCK_md5_r5.txt). Chiet khau thanh khoan DRI: cong thuc r4 GIU NGUYEN (luat can bac hai, Y 0,5/1/1,5; ADV trung vi
250 phien toi 02/11/2026 tu bq_liq_dri_20261103.csv = snapshot r4). Bang 1/5/10 ty; THAM CHIEU NHAN = 5 ty (quy uoc fleet).
So gia: dong cua 03/11/2026 = 13.400 d (DNSE ohlc 1D; ../../../dd_audit_newproject_20261103/close_20261103.md). Chay: python3 -B liquidity_r5.py"""
import os, csv, json, math, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
rows = [r for r in csv.DictReader(open('bq_liq_dri_20261103.csv')) if r['time'] <= '2026-11-02']
d = rows[-251:]
c = np.array([float(r['Close']) for r in d]); p = np.array([float(r['Price']) for r in d]); v = np.array([float(r['Volume']) for r in d])
val = (p*v)[1:]; sig = float(np.std(np.diff(np.log(c)), ddof=1)); adv = float(np.median(val))
print(f'DRI {d[1]["time"]}..{d[-1]["time"]} N={len(val)}: ADV trung vi {adv/1e9:.2f} ty | sigma ngay {sig:.2%}')
M = json.load(open('dri_model_r5_out.json')); PX = 13400
o = dict(adv_med=adv, sigma_d=sig, pos={}, after={}, price=PX, price_date='2026-11-03')
def lab(px, s):
    return ('RE' if px <= s['P10'] else 'RE CO DIEU KIEN' if px <= s['P25'] else 'HOP LY' if px <= s['P75'] else 'NGHIENG DAT' if px <= s['P90'] else 'DAT')
for q in (1, 5, 10):
    dq = {f'Y{y}': y*sig*math.sqrt(q*1e9/adv) for y in (0.5, 1.0, 1.5)}; f = 1 - dq['Y1.0']
    days15 = q*1e9/(0.15*adv)
    a = dict(center=M['center']*f, center_liqread=M['center_liqread']*f, forced=M['forced']*f, expected=M['expected']['0.2']*f,
             scale={k: x*f for k, x in M['scale'].items()}, scale_forced={k: x*f for k, x in M['scale_forced'].items()},
             scale_liqread={k: x*f for k, x in M['scale_liqread'].items()})
    a['label'] = lab(PX, a['scale']); a['label_liqread'] = lab(PX, a['scale_liqread'])
    a['rule4_pct_vs_center'] = PX/a['center'] - 1; a['rule4_hit'] = PX < a['center']*0.85
    o['pos'][str(q)] = dict(disc=dq, days15=days15); o['after'][str(q)] = a
    print(f'{q:>3} ty: CK {dq["Y0.5"]:.1%}/{dq["Y1.0"]:.1%}/{dq["Y1.5"]:.1%} | {days15:.1f} phien @15% | tam {M["center"]:,.0f}->{a["center"]:,.0f} | ky vong p20 {a["expected"]:,.0f}'
          f' | thang ' + ' / '.join(f'{k} {x:,.0f}' for k, x in a['scale'].items()))
    print(f'        nhan @13.400: {a["label"]} | luat so muc gia (gia < tam-15% = {a["center"]*0.85:,.0f}): {a["rule4_pct_vs_center"]:+.1%} => {"DAT" if a["rule4_hit"] else "KHONG DAT"}'
          f' | (dien giai C-thanh ly: tam {a["center_liqread"]:,.0f}, nhan {a["label_liqread"]}) | bi buoc {a["forced"]:,.0f} (P25-P75 {a["scale_forced"]["P25"]:,.0f}-{a["scale_forced"]["P75"]:,.0f})')
json.dump(o, open('liquidity_r5_out.json', 'w'), indent=1)
