"""DD REDO VONG 3 HHS (job Taylor_20261108_180130) — ap dinh chinh fundamental-skeptic 08/11 (TOP5D_CORRECTIONS_20261108.md muc HHS).
Dau vao BCTC chep nguyen van calc/hhs_r2.py:12-20,45-46 (Q3HN 30/09/2026). Gia dinh + basis: calc_r3/assumptions_r3.json (A1..A16).
Gia 06/11 = BQ tav2_bq.ticker (px_hhs_r3.sql -> px_hhs_r3_20261106.csv). r = 13,5% + 1,0 x (dep_12T(06/11) - 7,40%).
Chay: python3 -I hhs_r3.py (2 lan, so md5 output). Script KHONG ghi LOCK (LOCK_md5.txt ghi truoc bang lenh rieng)."""
import os, sys, json, csv, math, hashlib, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..')
sys.path.insert(0, os.path.join(ROOT, '_common_014125')); sys.path.insert(0, '/home/trido/thanhdt/WorkingClaude')
import numpy as np
import r2common as R2C
from deposit_rate_vn import effective_deposit_rate

TK = 'HHS'; ASOF = '2026-11-06'; ANCHOR_DATE = '2026-11-03'; R_ANCHOR = 0.135
# ---- BCTC goc (chep nguyen van calc/hhs_r2.py) ----
SH = 431.985968; HHS = 0.5115
EQ_ME, NCI = 9152.94, 7726.98
CRV_FV = NCI / (1 - HHS)
STEP_AT = 2020.76 / 0.20 * 0.8
CRV_COST = CRV_FV - STEP_AT
OTHER = EQ_ME - HHS * CRV_FV - (694.84 - 310.74)
NMTT, VAT = 3099.20, 1.08
REST_CRV = 7338.8
NEW_I14 = 1329.0
BLK = REST_CRV - NEW_I14                      # khoi HTK cu NC-II 6.009,8
BDS_SURP = (2459.74 - 1438.45) * 0.8
KQ = 28.4
# ---- gia dinh r3 (assumptions_r3.json) ----
G_OBS = (0.519 + 0.522) / 2                   # A3
S_OBS = 0.8 * (G_OBS - 0.1) / (1 - G_OBS)
SC = {  # m bien rong backlog, s r2, lech s doi xung (A4), lech s r2, LNST o to, P/E (A12)
 'TIEU_CUC': dict(m=0.30, s_r2=0.15, off_sym=-0.15, off_r2=-0.25, np=25, pe=5),
 'CO_SO':    dict(m=0.335, s_r2=0.40, off_sym=0.0, off_r2=0.0, np=35, pe=6),
 'TICH_CUC': dict(m=0.36, s_r2=0.55, off_sym=0.15, off_r2=0.15, np=50, pe=8),
}
W = {'r2': {'TIEU_CUC': 0.30, 'CO_SO': 0.50, 'TICH_CUC': 0.20}, 'sym': {'TIEU_CUC': 0.25, 'CO_SO': 0.50, 'TICH_CUC': 0.25}}   # A6
DS = [(x, 1 / 5) for x in (-0.15, -0.075, 0.0, 0.075, 0.15)]                     # A5
Y_AX = [(2.5, 1 / 3), (3.25, 1 / 3), (4.0, 1 / 3)]                                # A2
HD_AX = [(0.0, 0.10), (0.15, 0.15), (0.25, 0.30), (0.35, 0.30), (0.45, 0.15)]     # A7 (r2) song song
GOV_AX = [(0.0, 0.55), (0.05, 0.20), (0.10, 0.15), (0.15, 0.10)]                  # A8 (r2) do nhay
BDS = {'r2': [(0.0, 1 / 3), (0.5, 1 / 3), (1.0, 1 / 3)], 'book': [(0.5, 1 / 3), (1.0, 1 / 3), (1.5, 1 / 3)]}   # A11
I14 = {'r2': [(-0.15, 0.25), (0.0, 0.50), (0.40, 0.25)], 'sym': [(-0.15, 0.25), (0.0, 0.50), (0.15, 0.25)]}   # A9
KQ_AX = [(0.0, 0.70), (1.0, 0.30)]                                                 # A10 do nhay
R_AX = list(R2C.R_AXIS)

d0 = effective_deposit_rate(ANCHOR_DATE); d1 = effective_deposit_rate(ASOF)
R = R_ANCHOR + 1.0 * (d1['rate'] - d0['rate'])                                     # A13
pv = lambda y, ke: 1 / (1 + ke) ** y

HEAD = dict(cost='y', s='obs', soff='sym', w='sym', hd=False, gov=False, bds='book', i14='sym', kq=False)
R2CFG = dict(cost='r2', s='r2', soff='sym', w='r2', hd=True, gov=True, bds='r2', i14='r2', kq=True)


def make(cfg, y_fixed=None, r_axis=False):
    ax = [('scen', [(n, W[cfg['w']][n]) for n in SC]), ('ds', DS)]
    if cfg['cost'] == 'y': ax.append(('y', Y_AX if y_fixed is None else [(y_fixed, 1.0)]))
    if cfg['hd']: ax.append(('hd', HD_AX))
    if cfg['gov']: ax.append(('gov', GOV_AX))
    ax.append(('bds', BDS[cfg['bds']])); ax.append(('i14', I14[cfg['i14']]))
    if cfg['kq']: ax.append(('kq', KQ_AX))
    if r_axis: ax.append(('r', R_AX))

    def fn(scen, ds, y=4.0, hd=0.0, gov=0.0, bds=0.0, i14=0.0, kq=0.0, r=None, hd_fix=0.0, s_shift=0.0):
        ke = R if r is None else r; s = SC[scen]
        sv = max((s['s_r2'] if cfg['s'] == 'r2' else S_OBS + s['off_' + cfg['soff']]) + ds + s_shift, 0.0)
        if cfg['cost'] == 'r2':
            c = CRV_COST + NMTT / VAT * s['m'] * pv(1, ke) + BLK * sv * pv(4, ke) + NEW_I14 * i14 * pv(4, ke)
        else:   # A1: gia goc va thang du cung pv(y)
            c = CRV_COST - BLK * (1 - pv(y, ke)) + NMTT / VAT * s['m'] * pv(1, ke) + BLK * sv * pv(y, ke) + NEW_I14 * i14 * pv(4, ke)
        h = hd + hd_fix
        core = HHS * c * (1 - h) + OTHER + s['np'] * s['pe'] + bds * BDS_SURP * HHS * (1 - h) - kq * KQ
        return core * (1 - gov) / SH * 1e3
    return ax, fn


def run(cfg, px, d, **kw):
    fkw = {k: kw.pop(k) for k in ('hd_fix', 's_shift') if k in kw}
    ax, fn = make(cfg, **kw)
    res = R2C.outcomes(ax, lambda **a: fn(**a, **fkw))
    return R2C.stats(res, px, d), res


def liq(path, pxdate):
    rows = sorted((r for r in csv.DictReader(open(path)) if r['ticker'] == TK and r['time'] <= pxdate), key=lambda r: r['time'])
    out = {}
    for n in (250, 60):
        d = rows[-n - 1:]
        c = np.array([float(r['Close']) for r in d]); p = np.array([float(r['Price']) for r in d]); v = np.array([float(r['Volume']) for r in d])
        val = (p * v)[1:]; sig = float(np.std(np.diff(np.log(c)), ddof=1)); adv = float(np.median(val))
        out[f'adv{n}'] = dict(window=f'{d[1]["time"]}..{d[-1]["time"]}', n=len(val), adv_med=adv, sigma_d=sig,
                              disc={f'{q:.0f}': sig * math.sqrt(q / adv) for q in (5e9, 10e6, 40e6)}, part={f'{q:.0f}': q / adv for q in (5e9, 10e6, 40e6)})
    out['d_ref'] = out['adv250']['disc']['5000000000']; out['d_ref_adv60'] = out['adv60']['disc']['5000000000']
    out['d_10tr'] = out['adv250']['disc']['10000000']; out['d_40tr'] = out['adv250']['disc']['40000000']
    out['px'] = float(rows[-1]['Price']); out['pxd'] = rows[-1]['time']
    return out


def r1(x): return int(round(x))
def sm(s): return {k: (r1(x) if k not in ('pct_below_px', 'n') else round(x, 4) if k == 'pct_below_px' else x) for k, x in s.items()}


# ---- CONTROL: tai lap r2 (gia 9.550 / CK r2 04/11) ----
L2 = R2C.liq2(TK)
ctrl, _ = run(R2CFG, 9550.0, L2['d_ref'])
assert r1(ctrl['center']) == 10387 and r1(ctrl['p10']) == 8252 and r1(ctrl['p90']) == 12827, ctrl
L = liq(os.path.join(HERE, 'px_hhs_r3_20261106.csv'), ASOF); PX, PXD, D = L['px'], L['pxd'], L['d_ref']
print(f"== HHS VONG 3 | gia {PX:,.0f} ({PXD}, BQ) | r {R:.2%} (dep 12T {d1['rate']:.2%} {d1['rate_source']}; neo {d0['rate']:.2%})")
print(f"s_obs = {S_OBS:.4f} (bien gop {G_OBS:.2%}) | khoi HTK cu {BLK:,.1f} ty")
print(f"CK 5 ty: r2 {L2['d_ref']:.4%} | r3 {D:.4%} (ADV250 {L['adv250']['adv_med']/1e9:,.2f} ty, ADV60 {L['adv60']['adv_med']/1e9:,.2f} ty, CK ADV60 {L['d_ref_adv60']:.4%}) | 10tr {L['d_10tr']:.4%} 40tr {L['d_40tr']:.4%}")
print(f"  Q/ADV250: 5 ty {L['adv250']['part']['5000000000']:.2%} (TREN vung hieu chinh ~0,1-20% => CK co the bi danh gia THAP) | 10tr {L['adv250']['part']['10000000']:.3%} | 40tr {L['adv250']['part']['40000000']:.3%}")
print("CONTROL r2 tai lap (04/11):", R2C.fmt(ctrl))

# ---- BRIDGE r2 -> r3 (cong don) ----
steps = [('1 gia+thanh khoan 06/11', {}),
         ('2 #1 gia goc HTK cu cung pv(y), y 2,5/3,25/4 (s r2)', dict(cost='y')),
         ('3 #2 s = bien NC-II quan sat 0,70, lech kich ban doi xung +-0,15', dict(s='obs')),
         ('4 #3 CK quan tri ra khoi tam (do nhay)', dict(gov=False)),
         ('5 #4 I.14 doi xung +-15%, ky quy ra do nhay', dict(i14='sym', kq=False)),
         ('6 #6 trong so kich ban doi xung 0,25/0,50/0,25', dict(w='sym')),
         ('7 BDSDT base theo so (truc 50/100/150%)', dict(bds='book')),
         ('8 #5 CK holding base 0% (HEADLINE)', dict(hd=False))]
cfg = dict(R2CFG); prev = ctrl['center']
bridge = [dict(step='0 r2 (gia 9.550 04/11)', center=r1(ctrl['center']), delta=0, p10=r1(ctrl['p10']), p90=r1(ctrl['p90']), pct_below=round(ctrl['pct_below_px'], 4), n=ctrl['n'])]
print(f"BRIDGE {bridge[0]['step']}: tam {ctrl['center']:,.0f}")
for name, ch in steps:
    cfg.update(ch); s, _ = run(cfg, PX, D)
    bridge.append(dict(step=name, center=r1(s['center']), delta=r1(s['center'] - prev), p10=r1(s['p10']), p90=r1(s['p90']), pct_below=round(s['pct_below_px'], 4), n=s['n']))
    print(f"BRIDGE {name}: tam {s['center']:,.0f} (buoc {s['center']-prev:+,.0f}) P10 {s['p10']:,.0f} P90 {s['p90']:,.0f} %duoi {s['pct_below_px']:.1%} n={s['n']}")
    prev = s['center']
assert cfg == HEAD

main, res = run(HEAD, PX, D); pre, _ = run(HEAD, PX, 0.0)
s10, _ = run(HEAD, PX, L['d_10tr']); s40, _ = run(HEAD, PX, L['d_40tr'])
print("HEADLINE r3 (sau CK 5 ty):", R2C.fmt(main))
print("Truoc CK:", R2C.fmt(pre))
print("Sleeve 40tr:", R2C.fmt(s40))
_, fnh = make(HEAD)
central = fnh(scen='CO_SO', ds=0.0, y=3.25, bds=1.0, i14=0.0) * (1 - D)
print(f"Gia tri tai tham so trung tam (CO_SO, ds 0, y 3,25, BDSDT 100%, I.14 0, CK holding 0) sau CK 5 ty: {central:,.0f}")

# ---- ban song song ----
ALT = {
 'co_CK_holding_r2 (0/15/25/35/45%, ky vong 27%)': dict(cfg=dict(HEAD, hd=True)),
 'co_CK_holding_va_quan_tri_r2': dict(cfg=dict(HEAD, hd=True, gov=True)),
 'co_CK_holding_y4': dict(cfg=dict(HEAD, hd=True), y_fixed=4.0),
 'co_CK_holding_y2.5': dict(cfg=dict(HEAD, hd=True), y_fixed=2.5),
 'y_co_dinh_2.5': dict(cfg=HEAD, y_fixed=2.5),
 'y_co_dinh_4.0': dict(cfg=HEAD, y_fixed=4.0),
 'co_truc_CK_quan_tri_r2': dict(cfg=dict(HEAD, gov=True)),
 'trong_so_kich_ban_r2_0.30/0.50/0.20': dict(cfg=dict(HEAD, w='r2')),
 'lech_s_kich_ban_r2_-0.25/+0.15': dict(cfg=dict(HEAD, soff='r2')),
 'BDSDT_r2_0/50/100': dict(cfg=dict(HEAD, bds='r2')),
 'co_truc_ky_quy': dict(cfg=dict(HEAD, kq=True)),
 'co_truc_r_pm1pp': dict(cfg=HEAD, r_axis=True),
}
alt_out = {}
for k, a in ALT.items():
    s, _ = run(a['cfg'], PX, D, **{x: a[x] for x in ('y_fixed', 'r_axis') if x in a}); alt_out[k] = s
    lab = R2C.label(PX, s)
    print(f"Song song {k}: {R2C.fmt(s)} | {lab}")
# do nhay o to (#6): LNST 42 (nhip EBIT 9T) x P/E 7,4 (=1/Ke) cho CO_SO
auto = (42 * 7.4 - 35 * 6) / SH * 1e3 * (1 - D)
print(f"Do nhay o to CO_SO LNST 42 x P/E 7,4 thay 35 x 6: {auto:+,.0f} d/cp")


def solve(f, lo, hi, it=60):
    flo = f(lo) - PX; fhi = f(hi) - PX
    if flo * fhi > 0: return None
    for _ in range(it):
        mid = (lo + hi) / 2; fm = f(mid) - PX
        if fm * flo > 0: lo, flo = mid, fm
        else: hi = mid
    return (lo + hi) / 2


imp_hd = solve(lambda x: run(HEAD, PX, D, hd_fix=x)[0]['center'], 0.0, 0.9)
imp_y = solve(lambda y: run(HEAD, PX, D, y_fixed=y)[0]['center'], 0.0, 40.0)
imp_y_hd = solve(lambda y: run(dict(HEAD, hd=True), PX, D, y_fixed=y)[0]['center'], 0.0, 40.0)
imp_s = solve(lambda x: run(HEAD, PX, D, s_shift=x)[0]['center'], -0.70, 0.30)
imp_s_hd = solve(lambda x: run(dict(HEAD, hd=True), PX, D, s_shift=x)[0]['center'], -0.70, 0.30)
fmt_n = lambda x, f: 'khong co nghiem trong mien' if x is None else f.format(x)
print(f"GIA NGU Y: CK holding co dinh {fmt_n(imp_hd, '{:.1%}')} | y (headline) {fmt_n(imp_y, '{:.2f}')} nam | y (ban CK holding r2) {fmt_n(imp_y_hd, '{:.2f}')} nam"
      f" | dich s (headline) {fmt_n(imp_s, '{:+.3f}')} | dich s (ban CK holding) {fmt_n(imp_s_hd, '{:+.3f}')}")

lab = R2C.label(PX, main); lab40 = R2C.label(PX, s40)
rule4 = dict(ref_5ty=dict(threshold=0.85 * main['center'], pass_=PX <= 0.85 * main['center']), sleeve_40tr=dict(threshold=0.85 * s40['center'], pass_=PX <= 0.85 * s40['center']))
print(f"NHAN: 5 ty {lab} | 40tr {lab40} | gia {PX:,.0f} vs tam {main['center']:,.0f} ({PX/main['center']-1:+.1%}) vs P10 {main['p10']:,.0f} ({PX/main['p10']-1:+.1%})")
print(f"Luat 4 (gia <= 0,85 x tam): 5 ty nguong {rule4['ref_5ty']['threshold']:,.0f} -> {'DAT' if rule4['ref_5ty']['pass_'] else 'KHONG DAT'} | 40tr nguong {rule4['sleeve_40tr']['threshold']:,.0f} -> {'DAT' if rule4['sleeve_40tr']['pass_'] else 'KHONG DAT'}")
hda = alt_out['co_CK_holding_r2 (0/15/25/35/45%, ky vong 27%)']
print(f"BAN CK HOLDING (song song): tam {hda['center']:,.0f} P10 {hda['p10']:,.0f} P90 {hda['p90']:,.0f} -> {R2C.label(PX, hda)}; luat 4 nguong {0.85*hda['center']:,.0f}")

R2C.write_grid(os.path.join(HERE, 'grid_hhs_r3.csv'), res)

# ---- SUMMARY ----
SUMP = os.path.join(ROOT, 'HHS', 'SUMMARY.json'); BK = os.path.join(ROOT, 'HHS', 'SUMMARY_r2.json')
if not os.path.exists(BK): shutil.copyfile(SUMP, BK)
old = json.load(open(BK)); S = dict(old)
A = json.load(open(os.path.join(HERE, 'assumptions_r3.json')))
S.update(round='r3', job='Taylor_20261108_180130', asof_price_date=PXD, price=PX, price_date=PXD, price_source='BQ tav2_bq.ticker Price (calc_r3/px_hhs_r3_20261106.csv)', r=R,
         r_anchor=dict(r=R_ANCHOR, rate=d0['rate'], source=d0['rate_source'], date=ANCHOR_DATE, dep_asof=d1['rate'], dep_asof_source=d1['rate_source'], rule='r = 13,5% + 1,0 x (dep_12T - 7,40%)'),
         center_post_liq=r1(main['center']), center_pre_liq=r1(pre['center']), p10_post=r1(main['p10']), p25_post=r1(main['p25']), p50_post=r1(main['p50']),
         p75_post=r1(main['p75']), p90_post=r1(main['p90']), p10_pre=r1(pre['p10']), p50_pre=r1(pre['p50']), p90_pre=r1(pre['p90']),
         p10_out=r1(main['p10']), p50_out=r1(main['p50']), p90_out=r1(main['p90']), pct_weight_below_price=round(main['pct_below_px'], 4), n_outcomes=main['n'],
         min_outcome=r1(main['min']), central_param_value_post=r1(central), liq_disc_5ty=D, label=lab, label_sleeve_40tr=lab40, sleeve_40tr=sm(s40),
         px_vs_center_post=PX / main['center'] - 1, px_vs_p10_post=PX / main['p10'] - 1, px_vs_p90_post=PX / main['p90'] - 1, rule4=rule4,
         ck_ref_size=dict(size_vnd=5e9, disc_adv250=D, disc_adv60=L['d_ref_adv60'], adv250=L['adv250']['adv_med'], adv60=L['adv60']['adv_med'], part_adv250=L['adv250']['part']['5000000000'],
                          note='5 ty = ~30% ADV250: TREN vung hieu chinh luat can bac hai => CK co the bi danh gia THAP'),
         ck_real_sleeve=dict(sizes_vnd=[10e6, 40e6], disc_adv250={'10tr': L['d_10tr'], '40tr': L['d_40tr']}, note='10tr DUOI vung hieu chinh (CK that ~ nua spread, chua do); 40tr trong vung'),
         grid_desc=('Luoi n=405: kich ban TIEU_CUC/CO_SO/TICH_CUC (0,25/0,50/0,25 [UL] doi xung; s = s_obs 0,7016 -0,15/0/+0,15) x ds -15..+15pp (5 diem deu) x y 2,5/3,25/4 nam (deu [UL]) '
                    'x BDSDT 50/100/150% so (deu [UL]) x I.14 -15/0/+15% (0,25/0,50/0,25). CK holding 0, CK quan tri 0, ky quy 0 (do nhay). '
                    'NAV: CRV gia goc - gia goc HTK cu x (1-pv(y)) + backlog NMTT x m x pv(1) + HTK cu x s x pv(y) + I.14 x pv(4) + BDSDT; x 51,15% + OTHER + o to. Sau CK 5 ty Y=1.'),
         grid_n=main['n'], center_change_vs_old=r1(main['center']) - old['center_post_liq'],
         center_vs_p50_note=f"tam = ky vong luoi {main['center']:,.0f}; P50 {main['p50']:,.0f}; gia tri tai tham so trung tam (CO_SO, ds 0, y 3,25, BDSDT 100%, I.14 0) {central:,.0f}",
         assumptions=A['assumptions'],
         headline_vs_alternatives=[dict(name='HEADLINE r3 (CK holding 0%)', center=r1(main['center']), p10=r1(main['p10']), p50=r1(main['p50']), p90=r1(main['p90']), pct_below_px=round(main['pct_below_px'], 4), label=lab)] +
                                  [dict(name=k, center=r1(x['center']), p10=r1(x['p10']), p50=r1(x['p50']), p90=r1(x['p90']), pct_below_px=round(x['pct_below_px'], 4), label=R2C.label(PX, x)) for k, x in alt_out.items()],
         parallel_versions={k: sm(x) for k, x in alt_out.items()}, bridge_r2_to_r3=bridge, control_r2_reproduced=sm(ctrl),
         implied_by_price=dict(holding_discount_fixed=imp_hd, y_headline=imp_y, y_with_holding_r2=imp_y_hd, s_shift_headline=imp_s, s_shift_with_holding_r2=imp_s_hd,
                               note='nghiem de tam (sau CK 5 ty) = gia 06/11; None = khong co nghiem trong mien tim'),
         sens_auto_dong_per_share=r1(auto),
         axes_included=['kich ban 0,25/0,50/0,25 (s_obs -0,15/0/+0,15; m 30/33,5/36%; o to 25x5/35x6/50x8)', 'ds -15..+15pp', 'y 2,5/3,25/4', 'BDSDT 50/100/150%', 'I.14 -15/0/+15%'],
         axes_excluded=[dict(axis='CK holding 0-45%', reason='[UL] khong co du lieu do lon -> luat user ra song song (co_CK_holding_r2); dinh chinh #5'),
                        dict(axis='CK quan tri 0-15%', reason='phap ly/quan tri chi WARNING -> do nhay; dinh chinh #3'),
                        dict(axis='mat ky quy 28,4 ty', reason='khong co van ban no qua han -> do nhay; dinh chinh #4'),
                        dict(axis='r', reason='NAV it nhay r; song song co_truc_r_pm1pp')],
         base_adjustments=[dict(item='Gia goc HTK cu 6.009,8 ty chiet khau pv(y)', effect_dong_per_share=None, basis='von nam y nam (A1/A2)', source='calc_r3/assumptions_r3.json A1-A2'),
                           dict(item='Thang du HTK cu s_obs 0,7016', effect_dong_per_share=None, basis='bien gop NC-II quan sat 51,9-52,2%', source='A3'),
                           dict(item='CK holding', effect_dong_per_share=0, basis='base 0 (luat user)', source='A7'),
                           dict(item='BDSDT theo so 100%', effect_dong_per_share=0, basis='so hop nhat (PPA)', source='A11')],
         gordon_crosscheck='khong ap dung (NAV holding)', lock_md5_file='calc_r3/LOCK_md5.txt',
         zone_r2=dict(center=old['center_post_liq'], p10=old['p10_post'], p90=old['p90_post'], label=old['label'], price=old['price'], date=old['asof_price_date'], pct_below=old['pct_weight_below_price']))
EXTRA = os.path.join(HERE, 'summary_r3_extra.json')
if os.path.exists(EXTRA): S.update(json.load(open(EXTRA)))
json.dump(S, open(SUMP, 'w'), ensure_ascii=False, indent=1, default=float)
json.dump(dict(main=main, pre=pre, s10=s10, s40=s40, central=central, ctrl=ctrl, bridge=bridge, alts=alt_out, liq=L, rule4=rule4, auto=auto,
               implied=dict(hd=imp_hd, y=imp_y, y_hd=imp_y_hd, s=imp_s, s_hd=imp_s_hd)),
          open(os.path.join(HERE, 'hhs_r3_out.json'), 'w'), ensure_ascii=False, indent=1, default=float)
print('SUMMARY.json (r3) written')
