import json, math, csv, statistics as st
A = json.load(open('assumptions.json'))
SH = A['shares']; B = A['B0_bn']; r0 = A['r']; g0 = A['g']; cap = A['reinv_cap']
vps = lambda bn: bn * 1e9 / SH

def gordon(N, r=r0, g=g0, Bk=B):
    roe = N / Bk
    reinv = min(max(g / roe, 0.0), cap) if roe > 0 else cap
    return N * (1 - reinv) / (r - g)

def scen_val(k, r=r0, g=g0, Nmul=1.0):
    s = A['scenarios'][k]
    return vps(gordon(s['N'] * Nmul, r, g) - s['loss_bn'])

W = {k: A['scenarios'][k]['w'] for k in A['scenarios']}
def center(**kw): return sum(W[k] * scen_val(k, **kw) for k in W)

out = {k: scen_val(k) for k in W}
out['center'] = center()
out['B0_vps'] = vps(B)
sens = {}
for dbp in (-100, -50, 50, 100):
    for beta in (1.0, 0.5):
        sens[f'dep{dbp:+d}bp_b{beta}'] = center(r=r0 + beta * dbp / 1e4)
for g in (0.0, 0.01, 0.03, 0.04):
    sens[f'g_{g}'] = center(g=g)
# moat sai: ROE ve Ke o moi kich ban => V = B (tru loss)
sens['moat_none_ROE_eq_Ke'] = sum(W[k] * vps(B - A['scenarios'][k]['loss_bn']) for k in W)
sens['no_loan_loss_bear'] = sum(W[k] * vps(gordon(A['scenarios'][k]['N'])) for k in W)
sens['loss_100pct_bear'] = out['center'] - W['bear'] * vps(A['scenarios']['bear']['loss_bn'])
out['sens'] = sens

# hai nen
Nshort = st.median(A['N_short_median_TTM3y'].values())
out['N_short'] = Nshort
out['V_ngan'] = vps(gordon(Nshort))
f = A['fcfe_conso']; ps = A['parent_share']
fc = st.mean([v['cfo'] - v['capex'] for v in f.values()]) * ps
out['fcfe_parent_avg'] = fc
out['V_dai'] = vps(fc / (r0 - g0))
out['D'] = abs(math.log(out['V_ngan'] / out['V_dai']))
cfo3 = st.mean([v['cfo'] for v in f.values()]); capex3 = st.mean([v['capex'] for v in f.values()])
da3 = st.mean([283.995, 279.512, 279.512])  # TTM D&A chua do rieng -> lay muc 2025 (uoc luong)
c4 = (cfo3 - min(capex3, da3)) * ps
d2 = (cfo3 - A['peer_capex_rev_median'] * st.mean(A['rev3'])) * ps
out['V_C4'] = vps(c4 / (r0 - g0)); out['V_D2'] = vps(d2 / (r0 - g0))
out['flows'] = dict(cfo3=cfo3, capex3=capex3, da3=da3, c4=c4, d2=d2)

# thanh khoan
px = list(csv.DictReader(open('px_vcp.csv')))
P = [float(x['Close']) for x in px]
V = [float(x['Price']) * float(x['Volume']) / 1e9 for x in px]
rets = [math.log(P[i] / P[i - 1]) for i in range(1, len(P))][-250:]
sig = st.pstdev(rets); adv250 = st.median(V[-250:]); adv60 = st.median(V[-60:]); adv20 = st.median(V[-20:])
zero = sum(1 for x in px[-250:] if float(x['Volume']) == 0)
liq = {}
for q in A['liquidity']['sizes_bn']:
    ck = sig * math.sqrt(q / adv60)
    liq[q] = dict(ck60=ck, ck250=sig * math.sqrt(q / adv250), center_post=out['center'] * (1 - ck),
                  bear_post=out['bear'] * (1 - ck), bull_post=out['bull'] * (1 - ck),
                  sess10_60=q / (0.10 * adv60), sess20_60=q / (0.20 * adv60))
out['liq'] = dict(sigma_d=sig, adv250_bn=adv250, adv60_bn=adv60, adv20_bn=adv20, zero_vol_days_250=zero, by_size=liq)
for p in (37900, 31700):
    out[f'px{p}'] = dict(pe_ttm=p * SH / 1e9 / 700.8, pe_base=p * SH / 1e9 / 441.5, pb=p / vps(B),
                         vs_center_post=p / liq[1.0]['center_post'] - 1)
# ---- VONG 2 ----
vb = A['variantB']
def val_B(k, w=None):
    s_ = A['scenarios'][k]
    return vps(gordon(s_['N'], Bk=vb['B_end2025_bn']) + vb['dB_bn'] - s_['loss_bn'])
out['varB'] = {k: val_B(k) for k in W}
out['varB']['center'] = sum(W[k] * val_B(k) for k in W)
out['varB']['base_check_bn'] = gordon(441.5, Bk=vb['B_end2025_bn']) + vb['dB_bn']
# bull sens
bs = A['bull_sens']
hh_rev = bs['q3_nonpower_rev'] - bs['services_rev_q3_est'] - bs['other_rev_q3_est']
hh_gp = bs['q3_nonpower_gp'] - bs['services_rev_q3_est'] * bs['services_gm']
excess_gp = hh_gp - bs['hh_normal_gm'] * hh_rev
dN_a = excess_gp * (1 - bs['cit_trading']) * bs['parent_share']
unc = bs['fin_rev_9T'] - bs['lcttt_interest_received_9T']
dN_b = unc * bs['parent_share'] * (1 - bs['tax_9T'])
def center_with(bullN, wts=None, loss=None):
    sc = A['scenarios']; w = wts or W
    v = {'bear': scen_val('bear'), 'base': scen_val('base'),
         'bull': vps(gordon(bullN) - sc['bull']['loss_bn'])}
    return sum(w[k] * v[k] for k in v), v['bull']
bN = A['scenarios']['bull']['N']
ca, bva = center_with(bN - dN_a); cb, bvb = center_with(bN - dN_a - dN_b)
ck60 = out['liq'] and liq[1.0]['ck60']
out['bull_sens'] = dict(hh_rev=hh_rev, hh_gp=hh_gp, hh_gm=hh_gp / hh_rev, excess_gp=excess_gp, dN_a=dN_a,
    unc_interest_9T=unc, unc_share=unc / bs['fin_rev_9T'], dN_b=dN_b,
    a=dict(N=bN - dN_a, bull=bva, center=ca, center_post=ca * (1 - ck60), vs37900=37900 / (ca * (1 - ck60)) - 1),
    b=dict(N=bN - dN_a - dN_b, bull=bvb, center=cb, center_post=cb * (1 - ck60), vs37900=37900 / (cb * (1 - ck60)) - 1))
out['px_cross'] = dict(price_37900_vs_center_post=37900 / out['liq'][1.0]['center_post'] - 1 if False else 37900 / liq[1.0]['center_post'] - 1,
    thresh_085=0.85 * liq[1.0]['center_post'])
# trong so
walt = {}
for nm, w in A['weights_alt'].items():
    c, _ = center_with(bN, w); walt[nm] = dict(center=c, center_post=c * (1 - ck60))
out['weights_alt'] = walt
# bien an toan: bull = 0 tai tam (chi base/bear)
out['bear_base_only_w'] = dict(center=(W['bear'] * out['bear'] + (W['base'] + W['bull']) * out['base']), note='bull weight chuyen sang base')
# EBITDA
ebitda = 849.8 + 266.0 + A['da_ttm_est']
out['ebitda_ttm'] = ebitda; out['debt_ebitda'] = 4282.0 / ebitda
out['debt_ebitda_old_da279'] = 4282.0 / (849.8 + 266.0 + 279.5)
print(json.dumps(out, indent=1, default=lambda x: round(x, 4)))
json.dump(out, open('model_out.json', 'w'), indent=1)
