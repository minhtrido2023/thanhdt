"""DDV — VONG 3 (08/11/2026, job Taylor_20261108_153738). Ap/kiem dinh chinh TOP5B_CORRECTIONS_20261108.md muc DDV.
Gia dinh khoa: assumptions_r3.json (md5 trong LOCK_md5.txt, chot TRUOC khi so gia). Hang so BCTC/lich su import tu ../calc/model.py (khong sua).
Control: ../calc/model_r2.py tai lap r2 13.109 (gia/thanh khoan 04/11). Gia + thanh khoan r3: px_ddv_r3_20261106.csv (BQ tav2_bq.ticker).
Chay: cd calc_r3 && $DNA_PYEXE -I model_r3.py  -> model_r3_out.json (2 lan, cmp trung byte)."""
import csv, itertools, json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
CALC = os.path.join(HERE, '..', 'calc')
sys.path.insert(0, CALC); sys.path.insert(0, os.path.abspath(os.path.join(HERE, '../../_common_014127')))
import numpy as np
import model as M1          # noqa: E402
import model_r2 as MR2      # noqa: E402
import common_r2 as R2      # noqa: E402
from wpct import wpct, weight_below   # noqa: E402
sys.path.insert(0, '/home/trido/thanhdt/WorkingClaude')
from deposit_rate_vn import effective_deposit_rate   # noqa: E402

A = json.load(open(os.path.join(HERE, 'assumptions_r3.json')))
ASOF = A['asof_price']
d0 = effective_deposit_rate('2026-11-03'); d1 = effective_deposit_rate(ASOF)
R0 = 0.135 + 1.0 * (d1['rate'] - d0['rate'])


def liquidity(path=os.path.join(HERE, 'px_ddv_r3_20261106.csv')):
    rows = sorted(csv.DictReader(open(path)), key=lambda r: r['time'])
    assert rows[-1]['time'] == ASOF, rows[-1]['time']
    out = dict(last_price=float(rows[-1]['Price']), last_date=rows[-1]['time'])
    for n in (250, 60):
        d = rows[-n - 1:]
        c = np.array([float(r['Close']) for r in d]); p = np.array([float(r['Price']) for r in d]); v = np.array([float(r['Volume']) for r in d])
        val = (p * v)[1:]; sig = float(np.std(np.diff(np.log(c)), ddof=1)); adv = float(np.median(val))
        sz = {}
        for q in [A['liq_ref_q']] + A['liq_sleeve_q']:
            part = q / adv
            sz[f'{q/1e6:.0f}tr'] = dict(q_over_adv=part, disc=sig * math.sqrt(part), in_calib=bool(0.001 <= part <= 0.20), days_at_15pct=q / (0.15 * adv))
        out[f'w{n}'] = dict(window=f'{d[1]["time"]}..{d[-1]["time"]}', adv_med=adv, sigma_d=sig, sizes=sz)
    return out


LIQ = liquidity(); PX = LIQ['last_price']
D_REF = LIQ['w250']['sizes']['5000tr']['disc']; D_40 = LIQ['w250']['sizes']['40tr']['disc']

# cau hinh r2 (de lap cau noi tung buoc)
R2CFG = dict(nc=M1.NC_NORM, midcoef=True, ronic='20', liven=True, q4=dict(xau=(-60.0, .25), nhu_q3=(MR2.Q3_CORE, .5), tot=(40.0, .25)),
             rev=M1.REV_NORM, intax={'r2': (M1.INT_AT_NORM, 1.0)}, w=None)
Q4R3 = {k: (A['q4_axis_ty'][k], A['q4_weights'][k]) for k in A['q4_axis_ty']}
INTR3 = {k: (A['int_ded_axis_ty'][k], A['int_ded_weights'][k]) for k in A['int_ded_axis_ty']}
R3CFG = dict(nc=A['nc_base_ty'], midcoef=False, ronic='ke', liven=False, q4=Q4R3, rev=A['rev_norm_ty'], intax=INTR3, w=None)
RPTS = [(R0 + bp / 1e4, w) for bp, w in zip(A['r_axis_bp'], A['r_axis_w'])]
G = A['g']


def value_ps(s, m, r, q4np, int_ded, cfg, liven_loss=0.0):
    c = M1.SCN[s]; ro = r if cfg['ronic'] == 'ke' else float(cfg['ronic']) / 100
    f27 = c['np27'] * ((1 - G / ro) if c['np27'] > 0 else 1.0)
    mid = M1.NPM_CYCLE * cfg['rev'] - int_ded + cfg.get('addint', 0.0)
    e_term = mid * (c['mid'] if cfg['midcoef'] else 1.0) * m * (1 + G) * (1 - G / ro)
    v = cfg['nc'] - liven_loss + q4np / (1 + r) ** 0.125 + f27 / (1 + r) ** 0.75 + e_term / (r - G) / (1 + r) ** 1.25
    return v * 1e9 / M1.SH


def grid(cfg, rpts=None):
    rpts = RPTS if rpts is None else rpts
    sw = cfg['w'] or {s: M1.SCN[s]['w'] for s in M1.SCN}
    lv = (('thu_du', 0.0, 0.9), ('mat', 217.0, 0.1)) if cfg['liven'] else (('so_sach', 0.0, 1.0),)
    vals, wts = [], []
    for s, m, (r, rw), (q, (qnp, qw)), (ik, (ided, iw)), (_, loss, lw) in itertools.product(M1.SCN, M1.MULTS, rpts, cfg['q4'].items(), cfg['intax'].items(), lv):
        vals.append(value_ps(s, m, r, qnp, ided, cfg, loss)); wts.append(sw[s] / len(M1.MULTS) * rw * qw * iw * lw)
    return vals, wts


def central(cfg):
    q = cfg['q4']['nhu_q3'][0]; i = list(cfg['intax'].values())[len(cfg['intax']) // 2][0]
    return value_ps('coso', 1.0, R0, q, i, cfg)


def summ(vals, wts, d=None, px=None):
    d = D_REF if d is None else d; px = PX if px is None else px; f = 1 - d
    q = wpct(vals, wts, (0.10, 0.25, 0.50, 0.75, 0.90)); post = [v * f for v in vals]
    cen = sum(a * b for a, b in zip(vals, wts)) / sum(wts)
    lab = 'DƯỚI vùng' if px < q[0.10] * f else ('TRÊN vùng' if px > q[0.90] * f else 'TRONG vùng')
    return dict(n=len(vals), center_pre=round(cen), center_post=round(cen * f), p10=round(q[.1] * f), p25=round(q[.25] * f), p50=round(q[.5] * f),
                p75=round(q[.75] * f), p90=round(q[.9] * f), min=round(min(post)), max=round(max(post)), below=round(weight_below(post, wts, px), 4), label=lab)


def with_(cfg, **kw):
    c = dict(cfg); c.update(kw); return c


if __name__ == '__main__':
    # 0) control r2 (gia/thanh khoan 04/11, dung MR2.grid nguyen ban)
    lq2 = R2.liquidity_r2('DDV'); v2, w2 = MR2.grid()
    ctrl = summ(v2, w2, d=lq2['d_ref'], px=lq2['last_price'])
    # tai lap r2 bang ham r3 (kiem ham tuong duong)
    v2b, w2b = grid(R2CFG, rpts=[(r, w) for r, w, _ in R2.r_points()])
    ctrl_eq = max(abs(a - b) for a, b in zip(v2, v2b))
    # cau noi r2 -> r3 (moi buoc doi 1 thu, giu cac buoc truoc)
    steps = [('0 r2 (gia+CK 04/11)', None, None),
             ('1 gia+CK 06/11 (r 13,5% khong doi)', R2CFG, None),
             ('2 C1 tien rong = so BCTC 1.108 (bo chuan hoa VLD mot chan)', with_(R2CFG, nc=A['nc_base_ty']), None)]
    c = steps[-1][1]
    c = with_(c, midcoef=False); steps.append(('3 C2 bo he so giua chu ky 0,8/1,0/1,1 theo kich ban', c, None))
    c = with_(c, ronic='ke'); steps.append(('4 C3 RONIC = Ke (moat NONE)', c, None))
    c = with_(c, liven=False); steps.append(('5 C4 Liven ghi theo so (xac suat mat sang do nhay)', c, None))
    c = with_(c, q4=Q4R3); steps.append(('6 C7 truc Q4 doi xung +-50 quanh Q3 that', c, None))
    c = with_(c, rev=A['rev_norm_ty']); steps.append(('7 C6 DT chuan hoa 5.500 -> 5.652 (FY2025 BQ)', c, None))
    c = with_(c, intax=INTR3); steps.append(('8 C5 khoan tru lai gui: truc 70,9/35,4/0 thay 55,6 co dinh', c, None))
    assert c == R3CFG
    bridge = []; prev = None
    for name, cfg, _ in steps:
        s = ctrl if cfg is None else summ(*grid(cfg))
        bridge.append(dict(step=name, center=s['center_post'], delta=0 if prev is None else s['center_post'] - prev, p10=s['p10'], p90=s['p90'], below=s['below']))
        prev = s['center_post']
    vals, wts = grid(R3CFG); H = summ(vals, wts)
    H40 = summ(vals, wts, d=D_40)
    cp = central(R3CFG)
    # bien the song song (moi dong doi 1 gia dinh so voi headline)
    alt = {}
    def put(k, desc, cfg, extra_liven=None):
        v, w = grid(cfg); s = summ(v, w); s['desc'] = desc; s['delta_vs_headline'] = s['center_post'] - H['center_post']; alt[k] = s
    for k, ncv in A['nc_alternatives_ty'].items():
        put('nc_' + k, f'tien rong {ncv} ty ({k})', with_(R3CFG, nc=ncv))
    put('int_full_current', 'tru lai gui hien tai 70,9 ty (can tren)', with_(R3CFG, intax={'x': (70.88, 1.0)}))
    put('int_r2_55_6', 'tru 55,6 ty nhu r2', with_(R3CFG, intax={'x': (M1.INT_AT_NORM, 1.0)}))
    put('int_zero', 'khong tru lai gui (can duoi bao thu)', with_(R3CFG, intax={'x': (0.0, 1.0)}))
    put('rev_avg2125', 'DT chuan hoa = TB 2021-25 3.709,7', with_(R3CFG, rev=A['rev_sens_ty']['avg_2021_2025']))
    put('rev_ltm', 'DT chuan hoa = LTM 6.406,2', with_(R3CFG, rev=A['rev_sens_ty']['ltm_q4_25_q3_26']))
    put('rev_5500_r2', 'DT chuan hoa 5.500 nhu r2', with_(R3CFG, rev=M1.REV_NORM))
    put('scn_w_sym', 'trong so duong 2027 doi xung 1/3', with_(R3CFG, w={s: 1 / 3 for s in M1.SCN}))
    put('midcoef_bobby', 'khoi phuc he so giua chu ky 0,8/1,0/1,1 (Bobby)', with_(R3CFG, midcoef=True))
    put('ronic_20', 'RONIC 20% (thuong moat ngam, truoc quy uoc 08/11)', with_(R3CFG, ronic='20'))
    put('liven_p10', 'Liven mat 100% xac suat 0,10 [UL]', with_(R3CFG, liven=True))
    put('xcheck_cash_capitalized', 'KIEM CHEO dieu 10: tien rong KHONG tinh theo menh gia; von hoa lai gui hien tai 70,9 ty/nam vao LN o r (tien bi giu lai sinh lai < r)', with_(R3CFG, nc=0.0, addint=70.88))
    put('pess_r2_choices', 'gop lai moi lua chon bi quan cua r2 (VLD 30/06 + Bobby + RONIC20 + Liven + Q4 lech + 5.500 + 55,6)', R2CFG)
    # do nhay r
    r_sens = {}
    for bp in (-100, -50, 50, 100):
        r_sens[f'{bp:+d}bp'] = summ(*grid(R3CFG, rpts=[(r + bp / 1e4, w) for r, w in RPTS]))['center_post']
    # ngu y boi gia: he so k tren LN giua chu ky (truoc tru lai) sao cho tam sau CK = gia; va r ngu y
    def cen_with_scale(k):
        cfg = with_(R3CFG, rev=A['rev_norm_ty'] * k); return summ(*grid(cfg))['center_post']
    lo, hi = 0.5, 3.0
    for _ in range(60):
        mid_ = (lo + hi) / 2; lo, hi = (mid_, hi) if cen_with_scale(mid_) < PX else (lo, mid_)
    k_imp = (lo + hi) / 2
    def cen_with_r(rr):
        return summ(*grid(R3CFG, rpts=[(rr + bp / 1e4, w) for bp, w in zip(A['r_axis_bp'], A['r_axis_w'])]))['center_post']
    lo, hi = 0.06, 0.20
    for _ in range(60):
        mr = (lo + hi) / 2; lo, hi = (lo, mr) if cen_with_r(mr) < PX else (mr, hi)
    r_imp = (lo + hi) / 2
    mid_base = M1.NPM_CYCLE * A['rev_norm_ty'] - A['int_ded_axis_ty']['mid']
    implied = dict(scale_on_rev=k_imp, implied_npm_x_rev_ty=M1.NPM_CYCLE * A['rev_norm_ty'] * k_imp,
                   implied_mid_np_after_int_mid_ty=M1.NPM_CYCLE * A['rev_norm_ty'] * k_imp - A['int_ded_axis_ty']['mid'],
                   base_mid_np_ty=mid_base, implied_rev_at_npm_cycle=A['rev_norm_ty'] * k_imp, r_implied=r_imp,
                   r_implied_dep12=r_imp - 0.135 + d0['rate'])
    eq = A['eq_book_ty']
    gx = dict(mid_np_excl_int_mid=mid_base, mid_np_incl=M1.NPM_CYCLE * A['rev_norm_ty'], roe_excl_on_eq_minus_nc=mid_base / (eq - A['nc_base_ty']),
              roe_incl_on_eq=M1.NPM_CYCLE * A['rev_norm_ty'] / eq, eq_book=eq, nc=A['nc_base_ty'])
    out = dict(ticker='DDV', job='Taylor_20261108_153738', asof_price=ASOF, price=PX, r=R0, dep_asof=d1, dep_anchor=d0,
               control_r2=ctrl, control_fn_max_abs_diff=ctrl_eq, headline=H, headline_sleeve40=H40, center_param_pre=cp, center_param_post=cp * (1 - D_REF),
               d_ref=D_REF, d_40tr=D_40, liquidity=LIQ, bridge=bridge, alternatives=alt, r_sens_post=r_sens, implied=implied, gordon_xcheck=gx,
               npm_cycle=M1.NPM_CYCLE, outcomes_vals=vals, outcomes_wts=wts)
    s = json.dumps(out, indent=1, ensure_ascii=False, sort_keys=True, default=float)
    open(os.path.join(HERE, 'model_r3_out.json'), 'w').write(s)
    print(json.dumps(dict(ctrl=ctrl, ctrl_eq=ctrl_eq, H=H, H40={k: H40[k] for k in ('center_post', 'p10', 'p90', 'label')}, cp_post=round(cp * (1 - D_REF)), d_ref=D_REF,
                          bridge=bridge, alt={k: (v['center_post'], v['p10'], v['p90'], v['label'], v['delta_vs_headline']) for k, v in alt.items()},
                          r_sens=r_sens, implied=implied, gx=gx), ensure_ascii=False, indent=0, default=float))
