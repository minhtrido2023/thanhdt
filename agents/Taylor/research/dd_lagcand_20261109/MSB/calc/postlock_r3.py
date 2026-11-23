"""MSB r3 — pha SAU KHOA: thanh khoan (V3), nhan, Ke ngu y. Doc model_r3 (khoa) + calc/bq_msb_px_r3.csv (BQ, phien dong cua 20/11/2026)."""
import csv, math, os, sys, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import model_r3 as M
rows = list(csv.DictReader(open(os.path.join(H, 'bq_msb_px_r3.csv'))))[-251:]
cl = [float(r['Close']) for r in rows]; val = [float(r['val_bn']) * 1e9 for r in rows][1:]
rets = [math.log(cl[i] / cl[i-1]) for i in range(1, len(cl))]
mu = sum(rets)/len(rets); sig = math.sqrt(sum((x-mu)**2 for x in rets)/(len(rets)-1))
med = lambda x: sorted(x)[len(x)//2] if len(x) % 2 else sum(sorted(x)[len(x)//2-1:len(x)//2+1])/2
adv250, adv60, adv20 = med(val), med(val[-60:]), med(val[-20:])
PX = float(rows[-1]['Price']); PXD = rows[-1]['time']
print(f"Thanh khoan {rows[0]['time']}..{PXD} n={len(val)} sigma {sig:.4f} ADV250 {adv250/1e9:.1f} ty, 60 {adv60/1e9:.1f}, 20 {adv20/1e9:.1f}")
CK = {}
for q in M.A['liquidity']['sizes_vnd']:
    CK[q] = sig*math.sqrt(q/adv250); print(f"  Q={q/1e9:g} ty: CK {CK[q]:.4%}, Q/ADV {q/adv250:.3%}, phien thoat @10% {q/(0.1*adv250):.2f} @20% {q/(0.2*adv250):.2f}")
D = CK[5e9]; dist = M.dist(); pre = M.stats(dist)
post = {k: (v*(1-D) if isinstance(v, float) else v) for k, v in pre.items()}
below = sum(w for v, w, _ in dist if v*(1-D) < PX)/sum(w for _, w, _ in dist)
print("SAU CK 5 ty:", {k: round(v) if isinstance(v, float) else v for k, v in post.items()}, "| tham so trung tam", round(M.value('CO_SO')*(1-D)))
print("SAU CK 40 trieu: tam", round(pre['center']*(1-CK[4e7])), "P10", round(pre['p10']*(1-CK[4e7])), "P90", round(pre['p90']*(1-CK[4e7])))
lab = 'DUOI vung' if PX < post['p10'] else ('TREN vung' if PX > post['p90'] else 'TRONG vung')
print(f"Gia {PX:.0f} @{PXD}: {lab}; gia/tam {PX/post['center']-1:+.1%}; trong so gia tri < gia {below:.1%}; luat4 0,85xtam={0.85*post['center']:,.0f} -> {PX <= 0.85*post['center']}")
lo, hi = 0.06, 0.25
for _ in range(60):
    m = (lo+hi)/2
    if M.stats(M.dist(ke=m))['center']*(1-D) > PX: lo = m
    else: hi = m
print(f"Ke ngu y boi gia: {m:.2%} (lai huy dong 12T ngu y {0.074+m-0.135:.2%})")
json.dump(dict(post=post, pre=pre, ck=CK, adv250=adv250, adv60=adv60, adv20=adv20, sigma=sig, px=PX, px_date=PXD, label=lab, below=below, ke_implied=m),
          open(os.path.join(H, 'postlock_r3_out.json'), 'w'), indent=1)
