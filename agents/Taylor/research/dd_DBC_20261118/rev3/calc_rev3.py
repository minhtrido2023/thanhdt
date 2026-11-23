"""DBC rev3 (= rev2 + loai LN BDS lich su, them do nhay) — RI tren von chu, ROE_op (tru XDCB lich su), tru quy KTPL. Mu gia: khong doc gia thi truong."""
import json, os, hashlib, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(HERE, 'assumptions_DBC_rev3.json')
A = json.load(open(F)); print('assumptions_md5', hashlib.md5(open(F, 'rb').read()).hexdigest())
q = A['np_quarterly_bn']; EQ = A['equity_parent_q_bn']; keys = sorted(q)
q_raw = dict(q)
B = A['bds_segment']; gp = B['gross_profit_bn']; tb = B['tax_rate']
run_q = (gp['2024'] + gp['2025'] + gp['9M2026'] / 0.75) / 3 * (1 - tb) / 4
def bds_q(k):
    y = k[:4]
    return gp['9M2026'] / 3 if y == '2026' else gp[y] / 4
q = {k: q_raw[k] - bds_q(k) * (1 - tb) + run_q for k in keys}
print(f'BDS: muc chay sau thue/quy = {run_q:.2f} ty; tong LN BDS sau thue bi loai trong 20q = {sum(bds_q(k)*(1-tb) for k in keys):.1f} ty')
S = A['shares_m']; E = A['equity_parent_q3']; CIP = A['cip_q3']; Eop = E - CIP; scale = E / Eop
r0 = A['r_ke']; g = A['g']; L = A['liquidity_discount']['pct']; w = {'bad': .25, 'base': .5, 'good': .25}
SP = A['scenario_spread_pp_tot']; PIG = A['cip_pig_haircut_bad']['pig_cip_bn']; HC = A['cip_pig_haircut_bad']['haircut']
k0 = A['ktpl_appropriation']['k_base']
TL = A['good_case_tax_loss']; DTA = TL['unrecognised_tax_loss_bn'] * TL['tax_rate']

# --- XDCB theo quy: noi suy tuyen tinh giua cac moc BCTC (uoc luong) / bac thang ---
known = A['cip_known_bn']; kk = sorted(known)
def qidx(k): return int(k[:4]) * 4 + int(k[-1]) - 1
def cip_lin(k):
    x = qidx(k)
    for a, b in zip(kk, kk[1:]):
        if qidx(a) <= x <= qidx(b):
            t = (x - qidx(a)) / (qidx(b) - qidx(a)); return known[a] + t * (known[b] - known[a])
    raise KeyError(k)
def cip_step(k):
    x = qidx(k); return known[max(a for a in kk if qidx(a) <= x)]

def roe_window(lo, hi, cipf=cip_lin, op=True):
    ks = [k for k in keys if lo <= k <= hi]
    vals = [4 * q[k] / (EQ[k] - (cipf(k) if op else 0)) for k in ks]
    return sum(vals) / len(vals), len(ks)

W = A['windows_predeclared']
print('--- XDCB/von chu lich su (noi suy) ---')
sh = {k: cip_lin(k) / EQ[k] for k in keys}
print(' '.join(f'{k}:{v:.1%}' for k, v in sh.items()))
print(f'XDCB/von TB 20q={st.mean(sh.values()):.1%} | 15q={st.mean([sh[k] for k in keys if k>="2023Q1"]):.1%} | hien tai Q3/26={CIP/E:.1%}')
R = {}
for nm in ('W12', 'W15', 'W20'):
    lo, hi = W[nm]
    ro, n = roe_window(lo, hi); rt, _ = roe_window(lo, hi, op=False); rs, _ = roe_window(lo, hi, cipf=cip_step)
    R[nm] = ro
    print(f'{nm} {lo}..{hi} n={n}: ROE_tot={rt:.4f} ROE_op(noi suy)={ro:.4f} ROE_op(bac thang)={rs:.4f} | cach rev1 ROE_tot*scale={rt*scale:.4f}')
roe_op = sum(R.values()) / 3
print(f'ROE_op tam (TB 3 cua so khai truoc) = {roe_op:.4f}; k_KTPL = {k0:.4f} -> ROE_op cho co dong = {roe_op*(1-k0):.4f}')

def val(roe_op_, k=k0, r=r0, gg=g, hair=0.0, extra=0.0):
    rs = roe_op_ * (1 - k)
    return (Eop * (rs - gg) / (r - gg) + CIP - hair * PIG + extra) / S * 1000
def scen(ro, k=k0, r=r0, gg=g, hc=HC, sp=SP, wt=w):
    v = {'bad': val(ro - sp * scale, k, r, gg, hc), 'base': val(ro, k, r, gg), 'good': val(ro + sp * scale, k, r, gg, extra=DTA)}
    return sum(wt[x] * v[x] for x in wt) * (1 - L), v
c, v = scen(roe_op)
print(f'scen (truoc CK thanh khoan): bad={v["bad"]:.0f} base={v["base"]:.0f} good={v["good"]:.0f}')
print(f'TAM (sau CK {L:.0%}) = {c:.0f} | VUNG = [{v["bad"]*(1-L):.0f}; {v["good"]*(1-L):.0f}] | tam truoc CK = {c/(1-L):.0f} | base sau CK = {v["base"]*(1-L):.0f}')
NPn = roe_op * Eop  # LNST chuan hoa (truoc KTPL)
print(f'LNST chuan hoa = {NPn:.1f} ty; EPS chuan hoa = {NPn/S*1000:.0f}; sau KTPL = {NPn*(1-k0)/S*1000:.0f}; BVPS = {E/S*1000:.0f}; P/B ham y tai tam = {c/(E/S*1000):.2f}; P/E ham y = {c/(NPn/S*1000):.1f}')

print('--- DO NHAY cua so (tung cua so lam tam) ---')
for nm, ro in R.items(): print(f'{nm}: tam={scen(ro)[0]:.0f} ({scen(ro)[0]/c-1:+.1%})')
for nm in ('W12', 'W15', 'W20'):
    lo, hi = W[nm]; rs, _ = roe_window(lo, hi, cipf=cip_step); R[nm + '_step'] = rs
rstep = (R['W12_step'] + R['W15_step'] + R['W20_step']) / 3
print(f'XDCB bac thang thay noi suy: ROE_op={rstep:.4f} tam={scen(rstep)[0]:.0f} ({scen(rstep)[0]/c-1:+.1%})')
rt_all = sum(roe_window(*W[n], op=False)[0] for n in ('W12', 'W15', 'W20')) / 3
cv = sum(w[x] * (E * (rt_all * (1 - k0) + d - g) / (r0 - g) / S * 1000) for x, d in (('bad', -SP), ('base', 0), ('good', SP))) * (1 - L)
print(f'Toan-von (XDCB cung ROE lich su, khong tach): ROE_tot={rt_all:.4f} tam={cv:.0f} ({cv/c-1:+.1%})')
print('--- quy KTPL ---')
for kk_ in [0.0] + A['ktpl_appropriation']['k_sens']: print(f'k={kk_:.3f}: tam={scen(roe_op, k=kk_)[0]:.0f} ({scen(roe_op, k=kk_)[0]/c-1:+.1%})')
print('--- r (V1, beta 1 / 0,5) + dai Ke D4 ---')
for d in (-100, -50, 50, 100):
    c1 = scen(roe_op, r=r0 + d / 1e4)[0]; c5 = scen(roe_op, r=r0 + d / 1e4 * .5)[0]
    print(f'{d:+d}bp: r={r0+d/1e4:.4f} tam={c1:.0f} ({c1/c-1:+.1%}) | beta0,5 {c5:.0f} ({c5/c-1:+.1%})')
for rr in A['ke_band_D4']: print(f'Ke D4 {rr:.3f}: tam={scen(roe_op, r=rr)[0]:.0f}')
for gg in (.04, .06): print(f'g={gg}: tam={scen(roe_op, gg=gg)[0]:.0f}')
for LL in (0, .05): print(f'CK thanh khoan {LL:.0%}: tam={c/(1-L)*(1-LL):.0f}')
print('--- trong so kich ban ---')
for wt in ((.35, .5, .15), (.15, .5, .35)):
    cc = scen(roe_op, wt=dict(zip(('bad', 'base', 'good'), wt)))[0]; print(f'w={wt}: tam={cc:.0f} ({cc/c-1:+.1%})')
print('--- khong kiem chung duoc ---')
for x in A['compliance_capex_env']['sens_bn']: print(f'chi tuan thu moi truong {x} ty: -{x/S*1000:.0f} d/cp ({-x/S*1000*(1-L)/c:+.1%})')
for dl in A['esop_2026']['sens_dilution']: print(f'ESOP pha loang {dl:.0%} (o menh gia 10k): tam={(c*S + 10000*S*dl*(1-L))/(S*(1+dl)):.0f}')
print(f'phai thu nguoi lao dong 237,1 ty mat trang: -{237.1/S*1000*(1-L):.0f} d/cp')
print('--- V6 hai nen (chi hien thi) ---')
NPs = NPn * (1 - k0) + (CIP and 0)
roe_s = NPs / E; reinv = min(max(g / roe_s, 0), .8)
v_short = (NPs * (1 - reinv) / (r0 - g) + 0) / S * 1000
cf = A['cfo_capex']; cfo = sum(cf['cfo_3y_bn'].values()) / 3
cx = cf['capex_3y_bn']; capex = (cx['2023Q4'] + cx['2024'] + cx['2025'] + cx['9M2026_cash'] + cx['9M2026_finance_lease_added']) / 3
print(f'V_ngan={v_short:.0f} (tai dau tu {reinv:.3f}, ROE tren toan von sau KTPL {roe_s:.4f}) | CFO/nam={cfo:.1f} capex(gom thue TC)/nam={capex:.1f} FCFE/nam={cfo-capex:.1f} -> {"V_dai khong xac dinh (FCFE<=0)" if cfo-capex<=0 else "tinh V_dai"}')
print(f'so rev1 19.491 / rev2 17.317 -> rev3 {c:.0f} ({c/19491-1:+.1%} / {c/17317-1:+.1%})')

print('--- R3: do nhay bo sung ---')
qq = q; q = q_raw
Rk = sum(roe_window(*W[n])[0] for n in ('W12', 'W15', 'W20')) / 3
q = qq
print(f'Giu BDS lich su (=rev2): ROE_op={Rk:.4f} tam={scen(Rk)[0]:.0f} ({scen(Rk)[0]/c-1:+.1%})')
for sfrac in A['cip_equity_funded_share_sens']:
    Eop_s = E - sfrac * CIP
    ro_s = sum(roe_window(*W[n], cipf=lambda k, f=sfrac: f * cip_lin(k))[0] for n in ('W12', 'W15', 'W20')) / 3
    vb = {}
    sc_s = E / Eop_s
    for nm, ro, hair, extra in (('bad', ro_s - SP*sc_s, HC, 0), ('base', ro_s, 0, 0), ('good', ro_s + SP*sc_s, 0, DTA)):
        vb[nm] = (Eop_s * (ro*(1-k0) - g)/(r0 - g) + sfrac*CIP - hair*PIG + extra)/S*1000
    cc = sum(w[x]*vb[x] for x in w)*(1-L)
    print(f'XDCB do von chu tai tro {sfrac:.0%} (ROE lich su tinh lai cung ti le, ROE_op={ro_s:.4f}): base={vb["base"]:.0f} tam={cc:.0f} ({cc/c-1:+.1%})')
LW = A['long_window_sens']; qa = dict(LW['np_bn'], **q_raw); ea = dict(LW['eq_bn'], **EQ)
for lab, ex20 in (('2016Q1-2026Q3', False), ('2016Q1-2026Q3 bo 2020', True)):
    ks = [k for k in sorted(qa) if k >= '2016Q1' and not (ex20 and k.startswith('2020'))]
    rt = sum(4*qa[k]/ea[k] for k in ks)/len(ks)
    va = E*(rt*(1-k0) - g)/(r0 - g)/S*1000*(1-L)
    sh_avg = 0.18
    vo = (Eop*(rt/(1-sh_avg)*(1-k0) - g)/(r0 - g) + CIP)/S*1000*(1-L)
    print(f'Cua so dai {lab} n={len(ks)}: ROE_tot={rt:.4f} | toan-von base={va:.0f} | quy ROE_op (/(1-18%) uoc luong) base={vo:.0f} ({vo/c-1:+.1%} so tam)')
