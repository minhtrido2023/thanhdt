"""SAU KHOA (LOCK_md5_r5.txt). Gia: 02/11 13.700 (tav2_bq.ticker, r3/calc/px_0211.csv); 03/11 13.300 (dispatch Mike — BQ chua sync cung ngay)."""
import sys, json, numpy as np, csv
sys.dont_write_bytecode = True
import model_r5 as R
o = json.load(open('model_r5_out.json')); tam = o['tam']; gp = o['grid_pct']
g = np.array([float(r['ev']) for r in csv.DictReader(open('grid_r5.csv'))])
for d, px in (('02/11', 13700), ('03/11', 13300)):
    print(f'{d} gia {px:,}: = {px/tam:.2f}x tam {tam:,.0f} | {px/o["base_co_so"]:.2f}x base co_so | {px/o["stress"]["flat_100"]:.2f}x stress phang | ty le luoi < gia {np.mean(g<px):.1%} | P/B {px/15460:.2f}x')
# dinh gia nguoc: r ham y; W ham y
for r in (0.15, 0.18, 0.20, 0.22, 0.25):
    print(f'  r {r:.0%}: {R.EV({"r": r}):,.0f}')
for wt in (0.0, 0.05, 0.10):
    W = {'tot': wt, 'co_so': 0.5, 'xau': 0.45 - wt, 'rat_xau': 0.05}; print(f'  W tot {wt:.0%}/co_so 50/xau {0.45-wt:.0%}/rat 5, PW phang 100%: {R.EV({"W": W, "PW": {"flat": 1.0}}):,.0f}')
W = {'tot': 0, 'co_so': 0, 'xau': 0, 'rat_xau': 1}; print(f'  100% rat_xau x phang: {R.EV({"W": W, "PW": {"flat": 1.0}}):,.0f}')
W = {'tot': 0, 'co_so': 0, 'xau': 1, 'rat_xau': 0}; print(f'  100% xau x g2031: {R.EV({"W": W, "PW": {"g2031": 1.0}}):,.0f}')
print(f'  holding 30% + r 15% + W 15/60/20/5 + PW g2031 70: {R.EV({"hold":0.3,"r":0.15,"W":{"tot":.15,"co_so":.6,"xau":.2,"rat_xau":.05},"PW":{"g2031":.7,"real":.3}}):,.0f}')
