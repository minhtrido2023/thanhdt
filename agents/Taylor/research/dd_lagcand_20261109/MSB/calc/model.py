"""MSB DD 09/11/2026 — RI ngan hang, mu gia thi truong (gia chi dung de gan nhan sau cung).
Tai lap: python3 -I calc/model.py > calc/model_out.txt  (doc calc/assumptions.json + calc/bq_msb_px.csv)"""
import json, csv, math, itertools, os
H = os.path.dirname(os.path.abspath(__file__))
A = json.load(open(os.path.join(H, 'assumptions.json')))
KE0 = A['r']['Ke']; N = A['shares_now_m']; BV0 = A['BV_0930']
T0 = (52) / 365  # 09/11 -> 31/12/2026
SC = A['scenarios']; W = SC['weights']

def value(sc, ke=KE0, shift=0.0, hair=0.0, rights=True, term='ronic_ke', g=0.06, cover=None, roe_override=None):
    bv = BV0 + SC['Q4_26_NI'][sc]
    if cover is not None:  # do nhay: dua bao phu len `cover` (thieu DP sau thue tru BV)
        bv -= max(0.0, cover * 6284.819 - 2964.303) * 0.8
    cash = A['rights']['cash_bn'] if rights else 0.0
    bv += cash
    path = roe_override[0] if roe_override else SC['ROE_path_27_29'][sc]
    roeT = roe_override[1] if roe_override else SC['ROE_T'][sc]
    path = [r + shift for r in path]; roeT += shift
    pv = 0.0; b = bv
    for i, r in enumerate(path, 1):
        pv += (r - ke) * b / (1 + ke) ** i
        b = b * (1 + r * (1 - A['payout']))
    if term == 'ronic_ke':
        tv = (roeT - ke) * b / ke
    else:  # tang truong: RI tang g vinh vien (RONIC = ROE_T)
        tv = (roeT - ke) * b * (1 + g) / (ke - g)
    v_end26 = bv + pv + tv / (1 + ke) ** len(path)
    v0 = v_end26 / (1 + ke) ** T0 - cash / (1 + ke) ** T0
    v0 -= hair * A['axes']['recv_haircut']['base_amount_bn'] * (1 - A['axes']['recv_haircut']['tax'])
    return v0 / N * 1e3  # dong/cp

def dist(**kw):
    ax_s = A['axes']['roe_shift']; ax_h = A['axes']['recv_haircut']
    out = []
    for sc, (s, ws), (h, wh) in itertools.product(W, zip(ax_s['values'], ax_s['w']), zip(ax_h['values'], ax_h['w'])):
        out.append((value(sc, shift=s, hair=h, **kw), W[sc] * ws * wh, sc))
    return out

def stats(o, px=None):
    o = sorted(o); tw = sum(w for _, w, *_ in o); c = sum(v * w for v, w, *_ in o) / tw
    def q(p):
        acc = 0
        for v, w, *_ in o:
            acc += w / tw
            if acc >= p - 1e-12: return v
    r = dict(center=c, p10=q(.1), p25=q(.25), p50=q(.5), p75=q(.75), p90=q(.9), min=o[0][0], max=o[-1][0], n=len(o))
    if px: r['pct_below_px'] = sum(w for v, w, *_ in o if v < px) / tw
    return r

# ---- thanh khoan (BQ) ----
rows = list(csv.DictReader(open(os.path.join(H, 'bq_msb_px.csv'))))
rows = rows[-251:]
cl = [float(r['Close']) for r in rows]; val = [float(r['val_bn']) * 1e9 for r in rows][1:]
rets = [math.log(cl[i] / cl[i - 1]) for i in range(1, len(cl))]
mu = sum(rets) / len(rets); sig = math.sqrt(sum((x - mu) ** 2 for x in rets) / (len(rets) - 1))
def med(x): x = sorted(x); n = len(x); return (x[n // 2] if n % 2 else (x[n // 2 - 1] + x[n // 2]) / 2)
adv250 = med(val); adv60 = med(val[-60:]); adv20 = med(val[-20:])
CK = {q: sig * math.sqrt(q / adv250) for q in A['liquidity']['sizes_vnd']}
PX = A['price_for_label_only']['price']
print(f"Thanh khoan: {rows[0]['time']}..{rows[-1]['time']} n={len(val)} | sigma ngay {sig:.4f} | ADV trung vi 250 {adv250/1e9:,.1f} ty, 60 {adv60/1e9:,.1f}, 20 {adv20/1e9:,.1f}")
for q, d in CK.items(): print(f"  CK Q={q/1e9:g} ty: {d:.4%} | Q/ADV250 {q/adv250:.4%} | so phien thoat @15% ADV: {q/(0.15*adv250):.3f}")

# ---- headline ----
pre = stats(dist())
D = CK[5e9]
post = {k: (v * (1 - D) if k in ('center', 'p10', 'p25', 'p50', 'p75', 'p90', 'min', 'max') else v) for k, v in pre.items()}
post['pct_below_px'] = stats([(v * (1 - D), w) for v, w, _ in dist()], PX)['pct_below_px']
central = value('CO_SO') * (1 - D)
print("\n== Tung kich ban (tham so trung tam, truoc CK) ==")
for sc in W: print(f"  {sc} w={W[sc]}: {value(sc):,.0f} d/cp (P/B ngu y tren BVPS 30/09 {value(sc)/(BV0/N*1e3):.2f}x)")
print(f"BVPS 30/09 = {BV0/N*1e3:,.0f} (sau CP thuong); LNST TTM {A['NI_9T26']+A['NI_Q4_25']:,.0f} ty, EPS TTM {(A['NI_9T26']+A['NI_Q4_25'])/N*1e3:,.0f}")
print("\nHEADLINE truoc CK:", {k: round(v) if isinstance(v, float) and v > 10 else v for k, v in pre.items()})
print("HEADLINE sau CK 5 ty:", {k: round(v) if isinstance(v, float) and v > 10 else round(v, 4) for k, v in post.items()}, "| trung tam tham so", round(central))
def label(p10, p90): return 'DƯỚI vùng' if PX < p10 else ('TRÊN vùng' if PX > p90 else 'TRONG vùng')
lab = label(post['p10'], post['p90'])
print(f"Gia (chi gan nhan) {PX} @{A['price_for_label_only']['date']}: {lab}; px/tam {PX/post['center']-1:+.1%}; luat4 (px <= 0,85 x tam = {0.85*post['center']:,.0f}): {PX <= 0.85*post['center']}")

# ---- do nhay ----
print("\n== Do nhay (tam co trong so, sau CK 5 ty) ==")
def ctr(**kw): return stats(dist(**kw))['center'] * (1 - D)
sens = {}
for bp in (-100, -50, 50, 100):
    for beta in A['r']['beta_pass']:
        sens[f"dep{bp:+d}bp_beta{beta}"] = ctr(ke=KE0 + beta * bp / 1e4)
for k, v in sens.items(): print(f"  {k}: {v:,.0f} ({v/post['center']-1:+.1%})")
alts = {
 'A_khong_quyen_mua': ctr(rights=False),
 'B_bao_phu_80pct': ctr(cover=0.80),
 'C_terminal_tang_truong_g6_RONIC=ROE_T': ctr(term='growth', g=0.06),
 'D_moat_NONE_ROE_ve_Ke_5nam(thong tin rui ro)': stats([(value(sc, roe_override=([KE0+(r-KE0)*0.5 for r in SC['ROE_path_27_29'][sc]], KE0)), W[sc]) for sc in W])['center'] * (1 - D),
}
for k, v in alts.items(): print(f"  {k}: {v:,.0f} ({v/post['center']-1:+.1%})")
# Ke ngu y boi gia (chi doc, khong doi headline)
lo, hi = 0.06, 0.25
for _ in range(60):
    m = (lo + hi) / 2
    if stats(dist(ke=m))['center'] * (1 - D) > PX: lo = m
    else: hi = m
print(f"  Ke ngu y de tam = gia {PX}: {m:.2%} (dep12T ngu y {0.074 + m - KE0:.2%})")
# Gordon kiem co tu dong
print("\n== Kiem co Gordon P/B tu dong (P/B=(ROE-g)/(Ke-g)) ==")
for roe, tag in ((0.1723, 'ROE5Y'), (0.1420, 'ROE_Min5Y'), (0.1409, 'ROE trailing Q3/26'), (0.1142, 'ROE10Y')):
    for ke in (0.123, 0.133, 0.135):
        print(f"  {tag} {roe:.1%} Ke {ke:.1%} g 6%: P/B {(roe-0.06)/(ke-0.06):.2f}x -> {(roe-0.06)/(ke-0.06)*BV0/N*1e3:,.0f} d")
# phan phoi
print("\nPhan phoi (sau CK):")
for v, w, sc in sorted(dist()): print(f"  {sc:6s} {v*(1-D):9,.0f}  w={w:.4f}")
json.dump(dict(pre=pre, post=post, central=central, label=lab, ck=CK, adv250=adv250, adv60=adv60, adv20=adv20, sigma=sig,
               sens=sens, alts=alts, ke_implied=m, scen={sc: value(sc) for sc in W},
               ck40=[stats([(v * (1 - CK[4e7]), w) for v, w, _ in dist()], PX)]),
          open(os.path.join(H, 'model_out.json'), 'w'), indent=1, ensure_ascii=False)
