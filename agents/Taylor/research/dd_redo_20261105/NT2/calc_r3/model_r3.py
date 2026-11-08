"""NT2 VONG 3 (job Taylor_20261108_153742) — ap TOP5B_CORRECTIONS_20261108.md muc NT2 + STANDARD_r2.md.
Chay (tu thu muc nay): $DNA_PYEXE -B model_r3.py > model_r3_out.txt
Gia dinh khoa: assumptions_r3.json (LOCK_md5.txt chot TRUOC khi chay/so gia).
So BCTC giu nguyen r2 (calc/model_r2.py; src/Q3_2026_hopnhat_va_giaitrinh.pdf)."""
import sys, os, json, itertools, csv
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '_common_020021'))
import r2lib as R2  # noqa: E402
L = R2.L
A = json.load(open(os.path.join(HERE, 'assumptions_r3.json')))
ASOF = A['asof_price_date']
PXCSV = os.path.join(HERE, os.path.basename(A['price_csv']))


def _px_series(tk, asof=ASOF):
    return [r for r in csv.DictReader(open(PXCSV)) if r['ticker'] == tk and r['time'] <= asof]


# --- so BCTC (giu nguyen r2) ---
SH = 287.876029
CASH, HTM_ST = 11.835947084, 5362.324001394
LOAN = 1795.772639513
DIV_PAY = 297.125837477
AR, AP, ACCR = 4252.014358468, 2637.441833617, 777.396880480
EQ = 5421.366757659
FIN_REV_9M, FIN_EXP_9M = 226.366187841, 68.448729333
NET_CASH = CASH + HTM_ST - LOAN - DIV_PAY
FIN_NET_AT = (FIN_REV_9M - FIN_EXP_9M) * 4 / 3 * 0.80
NWC = AR - AP - ACCR
NWC_NORM = NWC * A['rev_norm'] / A['rev_9m26_annualized']
NWC_REL = NWC - NWC_NORM

dep, dep_src = L.current_dep(ASOF); R = L.r_of(dep)


def val(np_norm, yrs, r=R, fcf=0.0, nwc_mode='norm'):
    op = np_norm - FIN_NET_AT + fcf
    pv = sum(op / (1 + r) ** t for t in range(1, yrs + 1))
    if nwc_mode == 'norm':
        wc = NWC_REL / (1 + r) ** A['nwc_release_t'] + NWC_NORM / (1 + r) ** yrs
    elif nwc_mode == 'full':
        wc = NWC / (1 + r) ** yrs
    else:
        wc = 0.0
    return (NET_CASH + pv + wc) / SH * 1000


AX = dict(np=(A['np_levels'], A['np_weights']), yrs=(A['yrs'], A['yrs_weights']),
          r=([R + d for d in A['r_offsets']], A['r_weights']), fcf=(A['fcf_adj'], A['fcf_weights']))


def grid(np_shift=0.0, fcf_shift=0.0, nwc_mode='norm', **over):
    ax = dict(AX); ax.update(over)
    v, w = [], []
    for (a, wa), (y, wy), (rr, wr), (f, wf) in itertools.product(zip(*ax['np']), zip(*ax['yrs']), zip(*ax['r']), zip(*ax['fcf'])):
        v.append(val(a + np_shift, y, rr, f + fcf_shift, nwc_mode)); w.append(wa * wy * wr * wf)
    return v, w


def run(Q, **kw):
    v, w = grid(**kw); return R2.stats(v, w, Q['price'], Q['disc_ref']), v, w


# --- thanh khoan: r2 (04/11, control) va r3 (06/11) ---
Q_r2 = R2.liq2('NT2')
L.px_series = _px_series
_liq0 = L.liq
L.liq = lambda tk, Q_bn=(1, 5, 10), asof=ASOF, n=250, free_float_shares=None: _liq0(tk, Q_bn, asof, n, free_float_shares)
Q = R2.liq2('NT2'); PX = Q['price']; LD = Q['disc_ref']
print(f"Gia {PX:,.0f} ({Q['price_date']}); r = {R:.2%} (dep {dep:.2%} [{dep_src}]); net cash {NET_CASH:,.1f} ({NET_CASH/SH*1000:,.0f} d/cp = {NET_CASH/SH*1000/PX:.0%} gia)")
print(f"NWC {NWC:,.1f} -> chuan hoa {NWC_NORM:,.1f} (x {A['rev_norm']:,.0f}/{A['rev_9m26_annualized']:,.0f}), giai phong {NWC_REL:,.1f} t={A['nwc_release_t']}; thu nhap TC rong sau thue {FIN_NET_AT:.1f}")

# --- control: tai lap r2 (truc r2, gia/CK 04/11) ---
r2ax = dict(yrs=((8, 10, 12), (0.25, 0.5, 0.25)), fcf=((0,), (1.0,)))
S_ctrl, _, _ = run(Q_r2, nwc_mode='full', **r2ax)
print("CONTROL r2 (gia 04/11): " + R2.fmt(S_ctrl, Q_r2['price']))

# --- bridge r2 -> r3 ---
steps = [("0 r2 (gia+CK 04/11)", Q_r2, dict(nwc_mode='full', **r2ax)),
         ("1 gia+CK 06/11 (22.200)", Q, dict(nwc_mode='full', **r2ax)),
         ("2 dinh chinh #1 truc thoi han 5/8/10/12/15 (.1/.2/.4/.2/.1)", Q, dict(nwc_mode='full', fcf=((0,), (1.0,)))),
         ("3 dinh chinh #2 NWC chuan hoa theo DT 7.137 (giai phong t=1)", Q, dict(nwc_mode='norm', fcf=((0,), (1.0,)))),
         ("4 dinh chinh #4 truc FCF-LNST +-150 (.25/.5/.25) = HEADLINE r3", Q, dict(nwc_mode='norm'))]
bridge, prev = [], None
for name, q, kw in steps:
    s, _, _ = run(q, **kw)
    bridge.append(dict(step=name, center=round(s['center_post']), delta=0 if prev is None else round(s['center_post'] - prev),
                       p10=round(s['p10_post']), p50=round(s['p50_post']), p90=round(s['p90_post']), n=s['n'], pct_below_px=s['pct_w_below_px']))
    prev = s['center_post']
    print(f"BRIDGE {name}: tam {s['center_post']:,.0f} (d {bridge[-1]['delta']:+,}) P10/P50/P90 {s['p10_post']:,.0f}/{s['p50_post']:,.0f}/{s['p90_post']:,.0f} n={s['n']}")

S, vals, ws = run(Q)
lab = R2.label(PX, S)
print("HEADLINE r3: " + R2.fmt(S, PX))
cp = val(800, 10)
print(f"Gia tri tai tham so trung tam (LNST 800, 10 nam, r {R:.1%}, FCF=LNST): {cp:,.0f} truoc CK / {cp*(1-LD):,.0f} sau CK")

# --- bien the song song (do nhay, KHONG phai headline) ---
alts = {
    "A_nut_4_nam_tr0.2 (skeptic)": dict(yrs=(A['alt_4y']['yrs'], A['alt_4y']['yrs_weights'])),
    "B_khong_chuan_hoa_NWC (837 thu hoi cuoi han)": dict(nwc_mode='full'),
    "C_khong_truc_FCF": dict(fcf=((0,), (1.0,))),
    "D_FCF_base_+110 (khau hao-capex, dai tu on dinh)": dict(fcf_shift=A['alt_da_up']['fcf_shift']),
    "E_LNST_neo_lich_su_735 (bien TB/trung vi x 7.137)": dict(np_shift=-65),
    "F_LNST_neo_9T26_829": dict(np_shift=29),
    "G_thoi_han_r2_8/10/12": dict(yrs=((8, 10, 12), (0.25, 0.5, 0.25))),
}
par = {}
for k, kw in alts.items():
    s, _, _ = run(Q, **kw); par[k] = s
    print(f"SONG SONG {k}: " + R2.fmt(s, PX))
hva = [dict(name="HEADLINE r3", center=round(S['center_post']), p10=round(S['p10_post']), p50=round(S['p50_post']), p90=round(S['p90_post']),
            pct_below_px=S['pct_w_below_px'], label=lab)]
hva += [dict(name=k, center=round(s['center_post']), p10=round(s['p10_post']), p50=round(s['p50_post']), p90=round(s['p90_post']),
             pct_below_px=s['pct_w_below_px'], label=R2.label(PX, s)) for k, s in par.items()]

# --- gia ngu y (gia sau CK = gia tri) ---
def solve(f, lo, hi):
    for _ in range(200):
        m = (lo + hi) / 2
        (lo, hi) = (m, hi) if f(m) < 0 else (lo, m)
    return (lo + hi) / 2

tgt = PX / (1 - LD)
imp = dict(np_const_10y_nwcnorm=solve(lambda x: val(x, 10) - tgt, 0, 3000),
           np_const_10y_nwcfull=solve(lambda x: val(x, 10, nwc_mode='full') - tgt, 0, 3000),
           yrs_at_800_nwcnorm=None, r_at_center_params=solve(lambda rr: -(val(800, 10, rr) - tgt), 0.01, 0.6),
           net_cash_per_share=NET_CASH / SH * 1000, net_cash_pct_px=NET_CASH / SH * 1000 / PX)
for y in range(1, 30):
    if val(800, y) >= tgt:
        imp['yrs_at_800_nwcnorm'] = y; break
op8 = 800 - FIN_NET_AT
pv_need = (tgt * SH / 1000 - NET_CASH)
print(f"GIA NGU Y: LNST co dinh 10 nam {imp['np_const_10y_nwcnorm']:,.0f} (NWC chuan hoa) / {imp['np_const_10y_nwcfull']:,.0f} (NWC 837 cuoi han); "
      f"LNST 800 can ~{imp['yrs_at_800_nwcnorm']} nam; r ngu y o tham so trung tam {imp['r_at_center_params']:.1%}; net cash {imp['net_cash_per_share']:,.0f} d/cp = {imp['net_cash_pct_px']:.0%} gia")

cc = {"A_co_lai_tien_gui": 800 / R / SH * 1000, "B_khong_lai_tien_gui_cong_net_cash": ((800 - FIN_NET_AT) / R + NET_CASH) / SH * 1000,
      "ROE_co_lai": 800 / (EQ - DIV_PAY), "ROE_khong_lai": (800 - FIN_NET_AT) / (EQ - DIV_PAY - NET_CASH)}
print(f"Cross-check Gordon g=0 vo han (can tren): A {cc['A_co_lai_tien_gui']:,.0f}; B {cc['B_khong_lai_tien_gui_cong_net_cash']:,.0f}; ROE co lai {cc['ROE_co_lai']:.1%}, van hanh {cc['ROE_khong_lai']:.1%}")
sens = {}
for b in (0.5, 1.0):
    for d in (-0.01, -0.005, 0.005, 0.01):
        rr0 = L.r_of(dep + d, b)
        s, _, _ = run(Q, r=([rr0 + o for o in A['r_offsets']], A['r_weights']))
        sens[f"b{b}_d{int(d*1e4)}bp"] = dict(r=rr0, center_post=s['center_post'], d_pct=s['center_post'] / S['center_post'] - 1)
print("Do nhay lai huy dong (tam sau CK): " + "; ".join(f"{k} {v['center_post']:,.0f} ({v['d_pct']:+.1%})" for k, v in sens.items()))
for ln in R2.liq_lines(Q):
    print(ln)
by_size = {k: S['center_pre'] * (1 - Q['adv250']['sizes'][k]['disc']) for k in Q['adv250']['sizes']}
print("Tam sau CK theo co (ADV250): " + ", ".join(f"{float(k)*1000:,.0f}tr {v:,.0f}" for k, v in by_size.items()))
M = dict(ticker='NT2', price=PX, price_date=Q['price_date'], r=R, dep=dep, dep_src=dep_src, liq=Q, grid=S, label=lab, center_param_pre=cp,
         net_cash=NET_CASH, nwc=NWC, nwc_norm=NWC_NORM, nwc_release=NWC_REL, fin_net_at=FIN_NET_AT, control_r2=S_ctrl, bridge=bridge,
         parallel=par, headline_vs_alternatives=hva, implied_by_price=imp, crosscheck=cc, sens_dep=sens, center_by_size=by_size)
json.dump(M, open(os.path.join(HERE, 'model_r3_out.json'), 'w'), indent=1, default=float, ensure_ascii=False, sort_keys=True)
