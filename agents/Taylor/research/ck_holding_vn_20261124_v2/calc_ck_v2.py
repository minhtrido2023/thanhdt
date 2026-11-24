"""CK holding VN v2 — buoc 2: tinh tu inputs/*.csv + raw/kbs_* (khoa md5 o LOCK_md5.txt). Tat dinh, khong mang.
Chay: python3 calc_ck_v2.py > run1.txt ; lan 2 > run2.txt ; md5 phai trung. Ghi calc_out_v2.json + panel_v2.csv.

Dinh nghia (holding p, ngay cuoi thang D; chi du lieu da cong bo <= D):
  MV_x   = Price_x(D, CHUA dieu chinh, phien co KL>0 cuoi cung) x SoCP_x(D)
           SoCP: oshares_at PIT (neo AIS, ap ISS theo ngay ex) ; tu choi -> dong quy BQ da cong bo (co FIN_FALLBACK)
  STALE  = phien cuoi > 10 phien truoc D  HOAC  ADV60 (trung binh 60 phien, ngay khong khop = 0) = 0
           -> gia STALE KHONG tinh la gia thi truong: phan do de nguyen trong nhom 'theo so'. Ban 'v1' giu gia stale.
  E_x    = VCSH thuoc co dong ME = owners_equity - minority_interests (CDKT quy VCI) cua quy moi nhat cong bo <= D
           (ngay cong bo = BQ Release_Date cua quy; khong co -> cuoi quy + 90 ngay). Thieu VCI -> fallback co gan co.
  s_i    = loi ich theo BCTC nam (KBS update_date; tang 2 = tich 2 tang, ngay = max). PIT: dung khi ngay + 90 <= D.
           Che do 'fixed' (do nhay): bo cong PIT, ty le hien tai ap lui ca cua so (LOOK-AHEAD, chi doi chieu).
  Con long nhau: con j bi bo neu mot con niem yet i khac cua cung p nam >= 20% j (gia tri j da nam trong gia i).
  SOTP_p = sum_{i khong stale} s_i MV_i + (E_p - sum_{i khong stale} s_i E_i) ; DoPhu = sum s_i MV_i / SOTP ; CK = 1 - MV_p/SOTP
  Gia me STALE -> bo quan sat (p, D).
N = so HOLDING; bootstrap khoi: holding (co hoan lai) x khoi thoi gian 3 thang (circular) ; seed 20261124.
"""
import os, json, glob, hashlib, unicodedata
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); IN = os.path.join(HERE, 'inputs'); RAW = os.path.join(HERE, 'raw')
V1 = os.path.join(os.path.dirname(HERE), 'ck_holding_vn_20261123')
DATES = json.load(open(os.path.join(IN, 'dates.json')))
ST = pd.read_csv(os.path.join(IN, 'stakes_all.csv')); QUAL = pd.read_csv(os.path.join(IN, 'qualified_parents.csv')).parent.tolist()
PX = pd.read_csv(os.path.join(IN, 'prices.csv')); SH = pd.read_csv(os.path.join(IN, 'shares_pit.csv'))
BQF = pd.read_csv(os.path.join(IN, 'bq_fin.csv')); VB = pd.read_csv(os.path.join(IN, 'vci_bs_long.csv')); DV = pd.read_csv(os.path.join(IN, 'divs.csv'))
U0 = pd.read_csv(os.path.join(IN, 'universe_U0.csv'))
QEND = {'Q1': '-03-31', 'Q2': '-06-30', 'Q3': '-09-30', 'Q4': '-12-31'}
STALE_SESS = 10


def norm(s):
    s = unicodedata.normalize('NFD', str(s).lower()); s = ''.join(c for c in s if unicodedata.category(c) != 'Mn').replace('đ', 'd')
    for w in ['cong ty co phan', 'cong ty tnhh mot thanh vien', 'cong ty tnhh mtv', 'cong ty tnhh', 'ctcp', 'tong cong ty', 'cong ty',
              'joint stock company', 'jsc', 'tap doan', 'mtv', '.', ',', '-', '(', ')']:
        s = s.replace(w, ' ')
    return ' '.join(s.split())


L = pd.read_csv(os.path.join(V1, 'raw', 'listing_vci_20261123.csv')); name2tk = {}
for n, s in zip(L.organ_name.map(norm), L.symbol): name2tk.setdefault(n, s)

# ---- ngay cong bo quy ----
BQF['rel'] = pd.to_datetime(BQF.rel)
REL = BQF.groupby(['ticker', 'quarter']).rel.min().to_dict()
VB['rel'] = [REL.get((t, q), pd.Timestamp(q[:4] + QEND[q[4:]]) + pd.Timedelta(days=90)) for t, q in zip(VB.ticker, VB.quarter)]
VB['rel_src'] = ['BQ' if (t, q) in REL else 'QEND+90' for t, q in zip(VB.ticker, VB.quarter)]
VB['eq_parent'] = VB.owners_equity - VB.minority_interests.fillna(0)
VB = VB[VB.owners_equity.notna() & (VB.owners_equity != 0)]
BQF['eq_tot'] = BQF.BVPS * BQF.OShares


def equity(t, D):
    f = VB[(VB.ticker == t) & (VB.rel <= D)].sort_values('rel')
    if len(f): r = f.iloc[-1]; return float(r.eq_parent), r.quarter, 'VCI_parent', float(r.paid_in) / 1e4 if pd.notna(r.paid_in) else np.nan
    f = BQF[(BQF.ticker == t) & (BQF.rel <= D) & BQF.eq_tot.notna()].sort_values('rel')
    if len(f): r = f.iloc[-1]; return float(r.eq_tot), r.quarter, 'BQ_total_inclNCI', np.nan
    return np.nan, None, 'NONE', np.nan


PXi = PX.set_index(['ticker', 'date']); SHi = SH.set_index(['ticker', 'date'])


def mv(t, d, stale_ok=False):
    if (t, d) not in PXi.index or (t, d) not in SHi.index: return None
    p = PXi.loc[(t, d)]; s = SHi.loc[(t, d)]
    sh, meth = (s.live_value, s.method) if pd.notna(s.live_value) else (s.fin_released, 'FIN_FALLBACK')
    if pd.isna(sh) or sh <= 0: return None
    stale = (p.sessions_since_trade > STALE_SESS) or (p.adv60_mean <= 0)
    return dict(mv=float(p.price * sh), stale=bool(stale), liq=bool(p.in_universe), meth=meth, shares=float(sh), px_date=p.px_date,
                thin=bool(p.days_traded60 < 20))


# ---- con long nhau: j bi bo neu i (con niem yet khac cua p) nam >= 20% j ----
def holds(i, j):
    f = os.path.join(RAW, 'kbs_subs', i + '.json')
    if os.path.exists(f) and any(name2tk.get(norm(r.get('name'))) == j and float(r.get('ownership_percent') or 0) >= 20 for r in json.load(open(f))): return True
    f = os.path.join(RAW, 'kbs_sh', j + '.json')
    return os.path.exists(f) and any(name2tk.get(norm(r.get('name'))) == i and float(r.get('ownership_percentage') or 0) >= 20 for r in json.load(open(f)))


ST = ST[ST.parent.isin(QUAL)].copy()
nested = []
for p, g in ST.groupby('parent'):
    subs = list(g['sub'])
    for j in subs:
        by = [i for i in subs if i != j and holds(i, j)]
        if by: nested.append((p, j, by[0]))
NEST = {(p, j): i for p, j, i in nested}
ST['nested_via'] = [NEST.get((p, j)) for p, j in zip(ST.parent, ST['sub'])]


# ---- panel (p, D, regime pit|fixed, stale rule main|v1) ----
def run(regime, stale_rule):
    rows = []
    for p in QUAL:
        for d in DATES:
            D = pd.Timestamp(d); m = mv(p, d)
            Ep, qp, srcp, _ = equity(p, D)
            if m is None or np.isnan(Ep): continue
            lmv = lbook = lmv_ctrl = lmv_liq = nci_est = stale_book = 0.0; n_used = n_stale = n_fb = 0; subs_used = []
            for _, r in ST[ST.parent == p].iterrows():
                if r.nested_via: continue
                if regime == 'pit' and pd.Timestamp(r.stake_date) + pd.Timedelta(days=90) > D: continue
                s = r.stake / 100.0; mi = mv(r['sub'], d); Ei, qi, srci, _ = equity(r['sub'], D)
                if mi is None or np.isnan(Ei): continue
                if s >= 0.5: nci_est += (1 - s) * Ei
                if mi['stale'] and stale_rule == 'main': n_stale += 1; stale_book += s * Ei; continue
                n_used += 1; n_fb += srci != 'VCI_parent'
                lmv += s * mi['mv']; lbook += s * Ei
                if s >= 0.5: lmv_ctrl += s * mi['mv']
                if mi['liq']: lmv_liq += s * mi['mv']
                subs_used.append(f"{r['sub']}:{s:.3f}")
            eq_src = srcp
            if srcp == 'BQ_total_inclNCI': Ep -= nci_est; eq_src = 'APPROX_BQtot_minus_listedNCI'
            sotp = lmv + (Ep - lbook)
            if sotp <= 0: continue
            rows.append(dict(parent=p, date=d, mv_p=m['mv'] / 1e9, parent_stale=m['stale'], parent_liq=m['liq'], parent_sh_meth=m['meth'],
                             eq_p=Ep / 1e9, eq_q=qp, eq_src=eq_src, listed_mv=lmv / 1e9, listed_book=lbook / 1e9, stale_book=stale_book / 1e9,
                             sotp=sotp / 1e9, coverage=lmv / sotp, cov_liq=lmv_liq / sotp, ctrl_share=lmv_ctrl / lmv if lmv > 0 else np.nan,
                             ck=1 - m['mv'] / sotp, n_subs=n_used, n_stale=n_stale, n_sub_eq_fallback=n_fb, subs=' '.join(subs_used)))
    R = pd.DataFrame(rows)
    return R[~R.parent_stale] if len(R) else R


PAN = {(rg, sr): run(rg, sr) for rg in ['pit', 'fixed'] for sr in ['main', 'v1']}
MAIN = PAN[('pit', 'main')]

# ---- co tuc tien con -> me (12 thang truoc D) / gia tri niem yet ; tang chong ----
DV['ex'] = pd.to_datetime(DV.exright_date)


def div_in_yield(p, d):
    D = pd.Timestamp(d); tot = 0.0
    for _, r in ST[(ST.parent == p) & ST.nested_via.isna()].iterrows():
        m = mv(r['sub'], d, True)
        if m is None: continue
        dps = DV[(DV.ticker == r['sub']) & (DV.ex > D - pd.Timedelta(days=365)) & (DV.ex <= D)].value_per_share.sum()
        tot += r.stake / 100 * m['shares'] * dps
    return tot / 1e9


def stacked(p):
    """p co co dong la cong ty NIEM YET nam >= 50% (KBS shareholders) hoac la con >=50% cua holding khac trong U0."""
    f = os.path.join(RAW, 'kbs_sh', p + '.json'); up = []
    if os.path.exists(f): up += [(name2tk.get(norm(r.get('name'))), r.get('ownership_percentage')) for r in json.load(open(f))
                                 if name2tk.get(norm(r.get('name'))) and float(r.get('ownership_percentage') or 0) >= 50]
    allst = pd.read_csv(os.path.join(IN, 'stakes_all.csv'))
    up += [(a, s) for a, s in zip(allst[(allst['sub'] == p) & (allst.stake >= 50)].parent, allst[(allst['sub'] == p) & (allst.stake >= 50)].stake)]
    return sorted(set((a, float(s)) for a, s in up))


def hold_summary(R, cov_min=0.60, min_months=3):
    K = R[R.coverage >= cov_min]
    H = K.groupby('parent').agg(ck=('ck', 'median'), ck_mean=('ck', 'mean'), ck_min=('ck', 'min'), ck_max=('ck', 'max'), months=('ck', 'count'),
                                coverage=('coverage', 'median'), cov_liq=('cov_liq', 'median'), ctrl_share=('ctrl_share', 'median'),
                                eq_src=('eq_src', 'last'), sub_fb=('n_sub_eq_fallback', 'max'), first=('date', 'min'), last=('date', 'max')).reset_index()
    return H[H.months >= min_months]


def stats(x):
    x = np.asarray(x, float); x = x[~np.isnan(x)]
    if not len(x): return dict(N=0)
    return dict(N=int(len(x)), median=float(np.median(x)), q25=float(np.percentile(x, 25)), q75=float(np.percentile(x, 75)),
                min=float(x.min()), max=float(x.max()))


def block_boot(R, H, B=5000, blk=3, seed=20261124, cov_min=0.60):
    rng = np.random.default_rng(seed); K = R[(R.coverage >= cov_min) & R.parent.isin(H.parent)]
    ser = [K[K.parent == p].sort_values('date').ck.to_numpy() for p in H.parent]
    out = np.empty(B)
    for b in range(B):
        hs = rng.integers(0, len(ser), len(ser)); vals = []
        for h in hs:
            x = ser[h]; T = len(x); nb = int(np.ceil(T / blk)); st = rng.integers(0, T, nb)
            idx = np.concatenate([(s0 + np.arange(blk)) % T for s0 in st])[:T]; vals.append(np.median(x[idx]))
        out[b] = np.median(vals)
    return dict(boot_p5=float(np.percentile(out, 5)), boot_p50=float(np.percentile(out, 50)), boot_p95=float(np.percentile(out, 95)), B=B, block_months=blk)


H = hold_summary(MAIN)
H['div_in_ann_yield'] = [np.mean([div_in_yield(p, d) for d in MAIN[MAIN.parent == p].date]) /
                         max(MAIN[MAIN.parent == p].listed_mv.mean(), 1e-9) for p in H.parent]
H['control'] = H.ctrl_share >= 0.5
H['stacked_above'] = [';'.join(f"{a}:{s:.1f}" for a, s in stacked(p)) for p in H.parent]
H['eq_exact'] = (H.eq_src == 'VCI_parent') & (H.sub_fb == 0)
H['parent_in_pit'] = H.parent.map(dict(zip(U0.ticker, U0.in_pit_any_monthend)))

res = {'N_main': int(len(H)), 'all': {**stats(H.ck), **block_boot(MAIN, H)}}
# ---- duong theo thang (cat ngang) cho tung panel ----
lines = {}
for k, R in PAN.items():
    K = R[R.coverage >= 0.60]
    g = K.groupby('date').ck.agg(['median', 'count', lambda s: s.quantile(.25), lambda s: s.quantile(.75)])
    g.columns = ['median', 'n', 'q25', 'q75']; lines['_'.join(k)] = g.round(4).reset_index().to_dict('records')
ml = pd.DataFrame(lines['pit_main']); rho = float(pd.Series(ml['median']).autocorr(1)) if len(ml) > 3 else np.nan
T = len(ml); res['time'] = dict(T_months=T, lag1_autocorr=rho, T_eff=float(T * (1 - rho) / (1 + rho)) if rho == rho and rho < 1 else np.nan,
                                monthly_median_min=float(ml['median'].min()) if T else np.nan, monthly_median_max=float(ml['median'].max()) if T else np.nan)
# ---- do nhay ----
sens = {}
for c in [0.5, 0.6, 0.7]: sens[f'cov{int(c*100)}'] = stats(hold_summary(MAIN, c).ck)
sens['v1_stale_kept_pit'] = stats(hold_summary(PAN[('pit', 'v1')]).ck)
sens['fixed_stake_main'] = stats(hold_summary(PAN[('fixed', 'main')]).ck)
sens['fixed_stake_v1'] = stats(hold_summary(PAN[('fixed', 'v1')]).ck)
sens['eq_exact_only'] = stats(H[H.eq_exact].ck)
sens['cov_liquid_ge60'] = stats(H[H.cov_liq >= 0.6].ck)
sens['parent_in_pit_only'] = stats(H[H.parent_in_pit == True].ck)
sens['ex_VIC'] = stats(H[H.parent != 'VIC'].ck)
loo = [float(np.median(H[H.parent != p].ck)) for p in H.parent]
sens['leave_one_out'] = dict(min=float(min(loo)), max=float(max(loo))) if loo else {}
grp = {'control': stats(H[H.control].ck), 'non_control': stats(H[~H.control].ck),
       'control_lowdiv(<1%/nam)': stats(H[H.control & (H.div_in_ann_yield < 0.01)].ck),
       'control_highdiv(>=1%/nam)': stats(H[H.control & (H.div_in_ann_yield >= 0.01)].ck),
       'stacked(tang chong)': stats(H[H.stacked_above != ''].ck),
       'HHS-like(control & lowdiv) U stacked': stats(H[(H.control & (H.div_in_ann_yield < 0.01)) | (H.stacked_above != '')].ck)}
# ---- phan tach troi: (dau -> cuoi) tren ho holding giu ca thang dau va cuoi cua cua so PIT ----
dec = []
for p in H.parent:
    g = MAIN[(MAIN.parent == p) & (MAIN.coverage >= 0.6)].sort_values('date')
    if len(g) < 2: continue
    a, b = g.iloc[0], g.iloc[-1]
    dec.append(dict(parent=p, d0=a.date, d1=b.date, ck0=a.ck, ck1=b.ck, dln_mv_parent=np.log(b.mv_p / a.mv_p), dln_sotp=np.log(b.sotp / a.sotp),
                    dln_listed=np.log(b.listed_mv / a.listed_mv) if a.listed_mv > 0 and b.listed_mv > 0 else np.nan,
                    listed_share0=a.listed_mv / a.sotp))
DEC = pd.DataFrame(dec)
# phan con 'dung im': ty trong gia tri niem yet cua con co |dln gia| < 2% giua d0 va d1
still = []
for _, r in DEC.iterrows():
    tot = st_ = 0.0
    for _, s in ST[(ST.parent == r.parent) & ST.nested_via.isna()].iterrows():
        m0, m1 = mv(s['sub'], r.d0), mv(s['sub'], r.d1)
        if not m0 or not m1 or m0['stale']: continue
        p0 = PXi.loc[(s['sub'], r.d0)].price; p1 = PXi.loc[(s['sub'], r.d1)].price; w = s.stake / 100 * m0['mv']
        tot += w; st_ += w * (abs(np.log(p1 / p0)) < 0.02)
    still.append(st_ / tot if tot else np.nan)
if len(DEC): DEC['share_listed_price_still'] = still


# ---- bang loai tru: MOI holding qualify (>=1 con/lien ket niem yet >=20%) khong vao N ----
PS = pd.read_csv(os.path.join(IN, 'prescreen.csv')).set_index('parent')
allq = pd.read_csv(os.path.join(IN, 'qualified_parents.csv')).parent.tolist(); EXC = []
for p in allq:
    if p in set(H.parent): continue
    if p not in QUAL: EXC.append(dict(parent=p, reason=f"prescreen do phu xap xi {PS.cov_approx.get(p, np.nan):.2f} < 0,30")); continue
    g = MAIN[MAIN.parent == p]
    if not len(g): EXC.append(dict(parent=p, reason='khong co gia me / VCSH me / so CP (hoac gia me STALE) tai moi ngay')); continue
    k = g[g.coverage >= 0.6]
    EXC.append(dict(parent=p, reason=f"do phu trung vi {g.coverage.median():.2f}; so thang >=60%: {len(k)} (<3)"
                    + (f"; co con STALE (toi da {int(g.n_stale.max())})" if g.n_stale.max() > 0 else '')))
EXC = pd.DataFrame(EXC)
# ---- doi chieu so CP: oshares_at vs VCI von gop/10.000 (cung quy CDKT da cong bo) vs BQ OShares ----
XS = []
for t in ['PAN', 'GEE', 'GEX', 'IPA', 'VHM', 'SNZ', 'MSN', 'VIC']:
    for d in DATES[-12:]:
        if (t, d) not in SHi.index: continue
        s = SHi.loc[(t, d)]; _, q, _, paid = equity(t, pd.Timestamp(d))
        XS.append(dict(ticker=t, date=d, oshares_at=s.live_value, method=s.method, bq_fin=s.fin_released, bq_q=s.fin_q, vci_paidin_sh=paid, vci_q=q))
XS = pd.DataFrame(XS)
XS['dev_vci'] = XS.oshares_at / XS.vci_paidin_sh - 1
print('\n== loai tru ==\n', EXC.to_string(index=False))
print('\n== doi chieu so CP ==\n', XS.round(4).to_string(index=False))
pd.set_option('display.width', 260); pd.set_option('display.max_columns', 40); pd.set_option('display.max_colwidth', 60)
print('== holding (PIT, loai stale, do phu>=60%, >=3 thang) ==\n', H.round(4).to_string(index=False))
print('\n== ket qua ==', json.dumps(res, default=float, indent=0))
print('\n== nhom ==\n', json.dumps(grp, default=float, indent=0))
print('\n== do nhay ==\n', json.dumps(sens, default=float, indent=0))
print('\n== duong theo thang pit_main ==\n', ml.to_string(index=False))
for k in ['pit_v1', 'fixed_main', 'fixed_v1']: print(f'\n== duong {k} ==\n', pd.DataFrame(lines[k]).to_string(index=False))
print('\n== phan tach troi ==\n', DEC.round(4).to_string(index=False))
print('\n== con long nhau bi bo ==', nested)
ALL = pd.concat([R.assign(regime=k[0], stale_rule=k[1]) for k, R in PAN.items()])
ALL.round(6).to_csv(os.path.join(HERE, 'panel_v2.csv'), index=False)
out = dict(holdings=H.round(6).to_dict('records'), result=res, groups=grp, sens=sens, lines=lines, decomposition=DEC.round(6).to_dict('records'),
           nested=nested, loo=loo, excluded=EXC.to_dict('records'), shares_xcheck=XS.round(6).to_dict('records'))
s = json.dumps(out, ensure_ascii=False, sort_keys=True, default=str)
open(os.path.join(HERE, 'calc_out_v2.json'), 'w').write(s)
print('calc_out md5', hashlib.md5(s.encode()).hexdigest())
