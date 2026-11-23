"""MSB DD r3 23/11/2026 — RI ngan hang, MU GIA. Chi doc calc/assumptions_r3.json (khong gia/ADV).
Tai lap: python3 -I calc/model_r3.py > calc/model_r3_out.txt"""
import json, itertools, os
H = os.path.dirname(os.path.abspath(__file__))
A = json.load(open(os.path.join(H, 'assumptions_r3.json')))
KE0 = A['r']['Ke']; N = A['shares_now_m']; BV0 = A['BV_0930']
T0 = 38 / 365  # 23/11 -> 31/12/2026
SC = A['scenarios']; W = SC['weights']; AX = A['axes']

def value(sc, ke=KE0, shift=0.0, hair=0.0, acc=0.0, rights=True, term='ronic_ke', g=0.06, cover=None, roe_override=None, extra_bn=0.0):
    bv = BV0 + SC['Q4_26_NI'][sc]
    if cover is not None:
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
    tv = (roeT - ke) * b / ke if term == 'ronic_ke' else (roeT - ke) * b * (1 + g) / (ke - g)
    v_end26 = bv + pv + tv / (1 + ke) ** len(path)
    v0 = v_end26 / (1 + ke) ** T0 - cash / (1 + ke) ** T0
    v0 -= hair * AX['recv_haircut']['base_amount_bn'] * (1 - AX['recv_haircut']['tax'])
    v0 -= acc * AX['accrual_haircut']['base_amount_bn'] * (1 - AX['accrual_haircut']['tax'])
    v0 -= extra_bn
    return v0 / N * 1e3

def dist(**kw):
    s, h, a = AX['roe_shift'], AX['recv_haircut'], AX['accrual_haircut']
    return [(value(sc, shift=x, hair=y, acc=z, **kw), W[sc] * wx * wy * wz, sc)
            for sc, (x, wx), (y, wy), (z, wz) in itertools.product(W, zip(s['values'], s['w']), zip(h['values'], h['w']), zip(a['values'], a['w']))]

def stats(o):
    o = sorted(o); tw = sum(w for _, w, *_ in o); c = sum(v * w for v, w, *_ in o) / tw
    def q(p):
        acc = 0
        for v, w, *_ in o:
            acc += w / tw
            if acc >= p - 1e-12: return v
    return dict(center=c, p10=q(.1), p25=q(.25), p50=q(.5), p75=q(.75), p90=q(.9), min=o[0][0], max=o[-1][0], n=len(o))

if __name__ == '__main__':
    pre = stats(dist())
    print("== Kich ban (tham so trung tam, truoc CK) ==")
    for sc in W: print(f"  {sc} w={W[sc]}: {value(sc):,.0f} d/cp (P/B ngu y tren BVPS 30/09 {value(sc)/(BV0/N*1e3):.2f}x)")
    print(f"BVPS 30/09 {BV0/N*1e3:,.0f}; LNST TTM {A['NI_9T26']+A['NI_Q4_25']:,.0f}")
    print("PHAN PHOI truoc CK:", {k: round(v) if isinstance(v, float) else v for k, v in pre.items()})
    c0 = pre['center']
    def ctr(**kw): return stats(dist(**kw))['center']
    print("== Do nhay tam (truoc CK) ==")
    sens = {}
    for bp in (-100, -50, 50, 100):
        for beta in A['r']['beta_pass']:
            sens[f"dep{bp:+d}bp_beta{beta}"] = ctr(ke=KE0 + beta * bp / 1e4)
    for ke in A['r']['band_ends']: sens[f"Ke_{ke:.3f}"] = ctr(ke=ke)
    lc = A['sensitivities_only']['LC_forfaiting']['amount_bn']
    sens.update({
     'khong_quyen_mua': ctr(rights=False), 'bao_phu_80': ctr(cover=0.80),
     'terminal_g6_RONIC=ROE_T': ctr(term='growth', g=0.06),
     'ROE_nua_duong_ve_Ke': stats([(value(sc, roe_override=([KE0 + (r - KE0) * 0.5 for r in SC['ROE_path_27_29'][sc]], KE0)), W[sc]) for sc in W])['center'],
     'LC_ccredit_0.89pct_1nam': ctr(extra_bn=lc * 0.0089 * 0.8),
     'LC_ton_that_5pct': ctr(extra_bn=lc * 0.05 * 0.8),
     'phai_thu_khac_Q3_4620_ton_that_25pct': ctr(extra_bn=4620 * 0.25 * 0.8),
     'r2_quy_uoc_ROE_binh_quan(doi chung)': stats([(value(sc, roe_override=({'XAU':[.10,.105,.11],'CO_SO':[.125,.135,.14],'TOT':[.14,.155,.16]}[sc], {'XAU':.12,'CO_SO':.14,'TOT':.16}[sc]), shift=x, hair=y, acc=z), W[sc]*wx*wy*wz) for sc,(x,wx),(y,wy),(z,wz) in itertools.product(W, zip(AX['roe_shift']['values'],AX['roe_shift']['w']), zip(AX['recv_haircut']['values'],AX['recv_haircut']['w']), zip(AX['accrual_haircut']['values'],AX['accrual_haircut']['w'])) ])['center'],
     'khong_truc_lai_du_thu': stats([(value(sc, shift=x, hair=y), W[sc]*wx*wy) for sc,(x,wx),(y,wy) in itertools.product(W, zip(AX['roe_shift']['values'],AX['roe_shift']['w']), zip(AX['recv_haircut']['values'],AX['recv_haircut']['w']))])['center'],
    })
    for k, v in sens.items(): print(f"  {k}: {v:,.0f} ({v/c0-1:+.1%})")
    print("== Gordon P/B (kiem co tu dong) ==")
    for roe, tag in ((0.1723, 'ROE5Y BQ'), (0.151, 'CO_SO ROE_T dau ky'), (0.1409, 'ROE_Trailing BQ (binh quan)')):
        print(f"  {tag} {roe:.1%} Ke 13,5% g 6%: P/B {(roe-0.06)/(0.135-0.06):.2f}x -> {(roe-0.06)/(0.135-0.06)*BV0/N*1e3:,.0f}")
    json.dump(dict(pre=pre, central_param=value('CO_SO'), scen={sc: value(sc) for sc in W}, sens=sens,
                   dist=[(v, w, sc) for v, w, sc in sorted(dist())]),
              open(os.path.join(H, 'model_r3_out.json'), 'w'), indent=1, ensure_ascii=False)
