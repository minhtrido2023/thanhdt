"""DCM r7 — pha SAU KHOÁ (LOCK_r7_md5.txt ghi 06:53:17 ICT 23/11 trước khi chạy file này). Đọc giá/KL từ DNSE OHLC 1D (không BQ),
tính chiết khấu thanh khoản (V3, luật căn bậc hai d = σ_ngày×sqrt(Q/ADV trung vị)), áp vào lưới đã khoá, so giá, giá hàm ý.
Chạy từ dd_DCM_20261104/: python3 calc/compare_px_r7.py [--refresh]  (--refresh = gọi DNSE, ghi calc/dnse_ohlc_r7.csv; mặc định đọc CSV đã lưu)."""
import sys, os, csv, json, math, time
sys.path.insert(0, 'calc'); sys.path.insert(0, '../dd_redo_20261105/_shared')
import numpy as np
import model_r7 as r7
import model as m
from wpct import wpct, weight_below

CSV = 'calc/dnse_ohlc_r7.csv'
if '--refresh' in sys.argv or not os.path.exists(CSV):
    sys.path.insert(0, '/home/trido/thanhdt/WorkingClaude')
    from dnse_api import DNSEClient
    now = int(time.time()); d = DNSEClient.from_credentials_file().ohlc('DCM', '1D', 'stock', **{'from': now-400*86400, 'to': now})
    with open(CSV, 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['t_utc', 'date_ict', 'o', 'h', 'l', 'c', 'v'])
        for i, t in enumerate(d['t']):
            w.writerow([t, time.strftime('%Y-%m-%d', time.gmtime(t+7*3600)), d['o'][i], d['h'][i], d['l'][i], d['c'][i], d['v'][i]])
rows = list(csv.DictReader(open(CSV)))[-251:]
c = np.array([float(r['c']) for r in rows])*1000; v = np.array([float(r['v']) for r in rows])
val = (c*v)[1:]; sig = float(np.std(np.diff(np.log(c)), ddof=1)); adv = float(np.median(val)); adv60 = float(np.median(val[-60:]))
PRICE, PDATE = float(c[-1]), rows[-1]['date_ict']
dl = lambda q, a=adv: sig*math.sqrt(q/a)
liq = dict(window=f"{rows[1]['date_ict']}..{PDATE}", n=len(val), sigma_d=round(sig, 5), adv250_ty=round(adv/1e9, 1), adv60_ty=round(adv60/1e9, 1),
           d_5ty_adv250=round(dl(5e9), 5), d_5ty_adv60=round(dl(5e9, adv60), 5),
           sizes={f'{q/1e9:g}ty': dict(d_adv250=round(dl(q), 5), pct_adv=round(q/adv, 4), sessions_at_15pct=round(q/(0.15*adv), 2)) for q in (0.5e9, 1e9, 2e9, 5e9)})
D = dl(5e9)
v, w = r7.grid7(); post = v*(1-D)
q = wpct(post, w, (.1, .25, .5, .75, .9))
H = dict(n=int(len(v)), center_pre=round(float(np.average(v, weights=w))), center_post=round(float(np.average(post, weights=w))),
         p10_post=round(q[.1]), p25_post=round(q[.25]), p50_post=round(q[.5]), p75_post=round(q[.75]), p90_post=round(q[.9]),
         pct_weight_below_price=round(weight_below(post, w, PRICE), 4))
lab = 'DƯỚI vùng (<P10)' if PRICE < H['p10_post'] else ('TRÊN vùng (>P90)' if PRICE > H['p90_post'] else 'TRONG vùng P10–P90')
cmp_ = dict(price=PRICE, price_date=PDATE, source='DNSE /price/ohlc 1D (close 14:45 ATC)', px_vs_center_post=round(PRICE/H['center_post']-1, 4),
            px_vs_p10=round(PRICE/H['p10_post']-1, 4), px_vs_p90=round(PRICE/H['p90_post']-1, 4), label=lab,
            rule_015=('ĐẠT (giá ≤ 0,85×tâm)' if PRICE <= 0.85*H['center_post'] else 'KHÔNG đạt (giá > 0,85×tâm)'), center_x085=round(0.85*H['center_post']))
# giá hàm ý: biên dài hạn s để điểm trung tâm (TB 2 cửa sổ, TB M, A/B, I_C 22) sau CK = giá
def pt_s(s): return sum(r7.pt7(M=M_, s_lr=s) for M_ in r7.M_GRID)/3*(1-D)
lo, hi = 0.0, 600.0
for _ in range(60):
    mid = (lo+hi)/2
    if pt_s(mid) < PRICE: lo = mid
    else: hi = mid
imp = round((lo+hi)/2, 1)
# biến thể chính, sau CK
VAR = {}
for k, kw in dict(V_4windows=dict(regs=tuple(r7.r6.CODE_REG)), V_M342=dict(Ms=(r7.M_GRID[0],)), V_M540=dict(Ms=(540.0,)), V_M738=dict(Ms=(738.0,)),
                  V_khcn0=dict(khcn=0.0), V_policy055=dict(p_policy=0.55), V_da_cal=dict(cal=True)).items():
    vv, ww = r7.grid7(**kw); pp = vv*(1-D); qq = wpct(pp, ww)
    VAR[k] = dict(center_post=round(float(np.average(pp, weights=ww))), p10=round(qq[.1]), p90=round(qq[.9]), below_px=round(weight_below(pp, ww, PRICE), 4))
O = dict(liquidity=liq, headline=H, compare=cmp_, implied_lr_margin_usd_t=imp, variants_post=VAR, d_liq_used=round(D, 5))
print(json.dumps(O, ensure_ascii=False, indent=1))
json.dump(O, open('calc/compare_px_r7_out.json', 'w'), ensure_ascii=False, indent=1, sort_keys=True)
