"""Cross-check tuong doi (KHONG vao headline): P/B ~ ROE_Min3Y cac NH, BQ 06/11/2026. python3 -I calc/peers_xcheck.py"""
import csv, os
H = os.path.dirname(os.path.abspath(__file__))
R = [r for r in csv.DictReader(open(os.path.join(H, 'bq_peers_20261106.csv'))) if r['ticker'] not in ('NVB', 'STB', 'SGB', 'BVB', 'EIB', 'PGB')]  # loai NH ROE am/tai co cau/LN dot bien
for key in ('ROE_Min3Y', 'ROE5Y'):
    xs = [float(r[key]) for r in R if r['ticker'] != 'MSB']; ys = [float(r['PB']) for r in R if r['ticker'] != 'MSB']
    n = len(xs); mx = sum(xs)/n; my = sum(ys)/n
    sxy = sum((x-mx)*(y-my) for x, y in zip(xs, ys)); sxx = sum((x-mx)**2 for x in xs); syy = sum((y-my)**2 for y in ys)
    b = sxy/sxx; a = my-b*mx; m = [r for r in R if r['ticker'] == 'MSB'][0]
    print(f"{key}: n={n} P/B = {a:.2f} + {b:.2f}*ROE, R2={sxy**2/(sxx*syy):.2f}; MSB {key} {float(m[key]):.1%} -> P/B {a+b*float(m[key]):.2f}x = {(a+b*float(m[key]))*float(m['BVPS']):,.0f} d (thuc te {float(m['PB']):.2f}x)")
ys = sorted(float(r['PB']) for r in R if r['ticker'] != 'MSB'); n = len(ys)
md = ys[n//2] if n % 2 else (ys[n//2-1]+ys[n//2])/2
print(f"Trung vi P/B {n} NH (khong MSB): {md:.2f}x -> {md*12515.24:,.0f} d")
for r in sorted(R, key=lambda r: -float(r['PB'])): print(f"  {r['ticker']}: P/B {float(r['PB']):.2f} ROE_Min3Y {float(r['ROE_Min3Y']):.1%} ROE5Y {float(r['ROE5Y']):.1%}")
