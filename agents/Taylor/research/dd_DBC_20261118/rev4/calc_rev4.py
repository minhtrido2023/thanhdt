"""DBC rev4 (= rev3 + tach BDS do dang khoi von hoat dong NPV=0 so sach; do nhay thue uu dai/TSSH/EPR). Mu gia."""
import json, os, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(HERE, 'assumptions_DBC_rev4.json')
A = json.load(open(F)); print('assumptions_md5', hashlib.md5(open(F, 'rb').read()).hexdigest())
q_raw = A['np_quarterly_bn']; EQ = A['equity_parent_q_bn']; keys = sorted(q_raw)
B = A['bds_segment']; gp = B['gross_profit_bn']; tb = B['tax_rate']
run_q = (gp['2024'] + gp['2025'] + gp['9M2026'] / 0.75) / 3 * (1 - tb) / 4
def bds_q(k): return gp['9M2026'] / 3 if k[:4] == '2026' else gp[k[:4]] / 4
def np_series(keep_run): return {k: q_raw[k] - bds_q(k) * (1 - tb) + (run_q if keep_run else 0) for k in keys}
S = A['shares_m']; E = A['equity_parent_q3']; CIP = A['cip_q3']
r0 = A['r_ke']; g = A['g']; L = A['liquidity_discount']['pct']; w0 = {'bad': .25, 'base': .5, 'good': .25}
SP = A['scenario_spread_pp_tot']; PIG = A['cip_pig_haircut_bad']['pig_cip_bn']; HC = A['cip_pig_haircut_bad']['haircut']
k0 = A['ktpl_appropriation']['k_base']; TL = A['good_case_tax_loss']; DTA = TL['unrecognised_tax_loss_bn'] * TL['tax_rate']
def qidx(k): return int(k[:4]) * 4 + int(k[-1]) - 1
def interp(known):
    kk = sorted(known)
    def f(k):
        x = qidx(k)
        for a, b in zip(kk, kk[1:]):
            if qidx(a) <= x <= qidx(b):
                t = (x - qidx(a)) / (qidx(b) - qidx(a)); return known[a] + t * (known[b] - known[a])
        raise KeyError(k)
    def fs(k): x = qidx(k); return known[max(a for a in kk if qidx(a) <= x)]
    return f, fs
cip_lin, cip_step = interp(A['cip_known_bn']); re_lin, re_step = interp(A['re_wip_known_bn'])
REW = A['re_wip_known_bn']['2026Q3']
W = A['windows_predeclared']

def model(keep_run=False, re_out=True, step=False, fund=1.0, tax_mult=1.0):
    """tra ve (ROE_op tam, Eop, them_so_sach). fund = ti le XDCB+BDS do von chu tai tro; tax_mult nhan LNST lich su."""
    q = np_series(keep_run)
    cf = cip_step if step else cip_lin; rf = re_step if step else re_lin
    R = {}
    for nm in ('W12', 'W15', 'W20'):
        lo, hi = W[nm]; ks = [k for k in keys if lo <= k <= hi]
        R[nm] = sum(4 * q[k] * tax_mult / (EQ[k] - fund * (cf(k) + (rf(k) if re_out else 0))) for k in ks) / len(ks)
    book = fund * (CIP + (REW if re_out else 0))
    return sum(R.values()) / 3, E - book, book, R

def val(ro, Eop, book, k=k0, r=r0, gg=g, hair=0.0, extra=0.0):
    return (Eop * (ro * (1 - k) - gg) / (r - gg) + book - hair * PIG + extra) / S * 1000
def scen(ro, Eop, book, k=k0, r=r0, gg=g, wt=w0, extra_all=0.0):
    sc = E / Eop
    v = {'bad': val(ro - SP * sc, Eop, book, k, r, gg, HC, extra_all), 'base': val(ro, Eop, book, k, r, gg, extra=extra_all),
         'good': val(ro + SP * sc, Eop, book, k, r, gg, extra=DTA + extra_all)}
    return sum(wt[x] * v[x] for x in wt) * (1 - L), v

ro, Eop, book, R = model()
c, v = scen(ro, Eop, book)
print(f'BDS do dang 30/9 (=30/6) = {REW:.1f}; XDCB = {CIP:.1f}; Eop = {Eop:.1f} (rev3: {E-CIP:.1f})')
for nm, x in R.items(): print(f'{nm}: ROE_op={x:.4f} -> tam {scen(x,Eop,book)[0]:.0f} ({scen(x,Eop,book)[0]/c-1:+.1%})')
print(f'ROE_op tam = {ro:.4f}; sau KTPL = {ro*(1-k0):.4f}')
print(f'scen truoc CK: bad={v["bad"]:.0f} base={v["base"]:.0f} good={v["good"]:.0f}')
print(f'TAM (sau CK {L:.0%}) = {c:.0f} | VUNG = [{v["bad"]*(1-L):.0f}; {v["good"]*(1-L):.0f}] | tam truoc CK = {c/(1-L):.0f} | base sau CK = {v["base"]*(1-L):.0f}')
NPn = ro * Eop
print(f'LNST chuan hoa (loai BDS) = {NPn:.1f}; EPS = {NPn/S*1000:.0f}; sau KTPL = {NPn*(1-k0)/S*1000:.0f}; BVPS = {E/S*1000:.0f}; P/B ham y = {c/(E/S*1000):.2f}; P/E ham y = {c/(NPn/S*1000):.1f}')
print(f'so rev3 14.696: {c/14696-1:+.1%} | rev2 17.317: {c/17317-1:+.1%} | rev1 19.491: {c/19491-1:+.1%}')
print('--- doi chieu cach xu ly BDS ---')
for lab, kw in (('rev3 (BDS trong von hd + muc chay)', dict(keep_run=True, re_out=False)),
                ('tach BDS + giu muc chay (dem 2 lan nhe)', dict(keep_run=True)),
                ('XDCB/BDS bac thang', dict(step=True))):
    a = model(**kw); cc = scen(a[0], a[1], a[2])[0]; print(f'{lab}: ROE_op={a[0]:.4f} tam={cc:.0f} ({cc/c-1:+.1%})')
for hcut in (0.2, 0.4):
    cc = scen(ro, Eop, book, extra_all=-hcut * REW)[0]; print(f'haircut BDS do dang {hcut:.0%} ({hcut*REW:.0f} ty): tam={cc:.0f} ({cc/c-1:+.1%})')
for s in A['cip_equity_funded_share_sens']:
    a = model(fund=s); cc = scen(a[0], a[1], a[2])[0]; print(f'XDCB+BDS do von chu tai tro {s:.0%}: ROE_op={a[0]:.4f} tam={cc:.0f} ({cc/c-1:+.1%})')
print('--- thue uu dai TNDN (KT25 TM31) ---')
T = A['cit_incentive']; pbt = T['pbt_bn']['2025']; ex = T['tax_exempt_reduced_bn']['2025']; lc = T['loss_cf_used_bn']['2025']; npat25 = pbt - T['tax_expense_bn']['2025']
for lab, cut in (('het 100% mien giam', ex), ('het 50% mien giam', ex / 2), ('het mien giam + lo chuyen sang', ex + lc)):
    m = 1 - cut / npat25; cc = scen(ro * m, Eop, book)[0]
    print(f'{lab}: {cut:.1f} ty = {cut/pbt:.2%} LNTT 2025 -> LNST x{m:.4f} -> tam={cc:.0f} ({cc/c-1:+.1%})')
print(f'thue hieu dung 2025 = {T["tax_expense_bn"]["2025"]/pbt:.2%}; 2024 = {T["tax_expense_bn"]["2024"]/T["pbt_bn"]["2024"]:.2%}; mien giam/LNTT 2024 = {T["tax_exempt_reduced_bn"]["2024"]/T["pbt_bn"]["2024"]:.2%}')
print('--- KTPL / r / g / CK / trong so ---')
for kk_ in [0.0] + A['ktpl_appropriation']['k_sens']: print(f'k={kk_:.3f}: tam={scen(ro,Eop,book,k=kk_)[0]:.0f} ({scen(ro,Eop,book,k=kk_)[0]/c-1:+.1%})')
for d in (-100, -50, 50, 100):
    c1 = scen(ro, Eop, book, r=r0 + d / 1e4)[0]; c5 = scen(ro, Eop, book, r=r0 + d / 2e4)[0]
    print(f'{d:+d}bp: tam={c1:.0f} ({c1/c-1:+.1%}) | beta0,5 {c5:.0f} ({c5/c-1:+.1%})')
for rr in A['ke_band_D4']: print(f'Ke D4 {rr:.3f}: tam={scen(ro,Eop,book,r=rr)[0]:.0f}')
for gg in (.04, .06): print(f'g={gg}: tam={scen(ro,Eop,book,gg=gg)[0]:.0f}')
for LL in (0, .05): print(f'CK thanh khoan {LL:.0%}: tam={c/(1-L)*(1-LL):.0f}')
for wt in ((.35, .5, .15), (.15, .5, .35)):
    cc = scen(ro, Eop, book, wt=dict(zip(('bad', 'base', 'good'), wt)))[0]; print(f'w={wt}: tam={cc:.0f} ({cc/c-1:+.1%})')
print('--- mot lan / khong kiem chung ---')
for x in A['bio_asset_writedown_sens']['bn']: print(f'trich lap TSSH {x} ty: -{x/S*1000*(1-L):.0f} d/cp ({-x/S*1000*(1-L)/c:+.1%})')
for x in A['compliance_capex_env']['sens_bn']: print(f'chi tuan thu moi truong mot lan {x} ty: -{x/S*1000*(1-L):.0f} d/cp ({-x/S*1000*(1-L)/c:+.1%})')
for x in A['compliance_capex_env']['epr_sens_bn_per_year']:
    pv = x * (1 - 0) / (r0 - g); print(f'EPR dinh ky {x} ty/nam (PV tang g): -{pv/S*1000*(1-L):.0f} d/cp ({-pv/S*1000*(1-L)/c:+.1%})')
for dl in A['esop_2026']['sens_dilution']: print(f'ESOP pha loang {dl:.0%}: tam={(c*S + 10000*S*dl*(1-L))/(S*(1+dl)):.0f}')
print(f'phai thu NLD 237,1 ty mat trang: -{237.1/S*1000*(1-L):.0f} d/cp')
print('--- V6 (chi hien thi) ---')
NPs = NPn * (1 - k0); roe_s = NPs / E; reinv = min(max(g / roe_s, 0), .8)
v_short = NPs * (1 - reinv) / (r0 - g) / S * 1000
cf = A['cfo_capex']; cfo = sum(cf['cfo_3y_bn'].values()) / 3; cx = cf['capex_3y_bn']
capex = (cx['2023Q4'] + cx['2024'] + cx['2025'] + cx['9M2026_cash'] + cx['9M2026_finance_lease_added']) / 3
print(f'V_ngan={v_short:.0f} (tai dau tu {reinv:.3f}, ROE toan von sau KTPL {roe_s:.4f}) | FCFE/nam={cfo-capex:.1f} -> V_dai khong xac dinh')
