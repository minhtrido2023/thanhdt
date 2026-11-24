"""CK holding VN v3 — buoc 2 (job Taylor_20261124_041821). Tat dinh, khong mang. Chay duoc ca pandas 2.x va 3 (ket qua phai trung).
Chay: python3 calc_ck_v3.py > run1.txt ; lan 2 > run2.txt ; md5 phai trung. Ghi calc_out_v3.json + panel_v3.csv.
SUA so voi v2 (theo SKEPTIC_v2): (1) cau noi ISS: thuong/co tuc CP da ex ma so CP chua cap nhat -> S_pre x (1+r) (co ISS_FIX);
  co phieu quy: neu AIS (CP phat hanh) > BQ OShares da cong bo cung quy (sau moi su kien) 0,5-15% -> dung BQ (CP luu hanh), co TREASURY_FIX;
  (2) T_eff chi tren thang n>=11; (3) KHONG tien loc: ca 116 holding, loc do phu PIT theo thang bang VCSH me;
  (4) co con mong (ADV60 < 0,1 ty hoac <20 phien khop/60) + do nhay mong->so / mong 50%; (5) isinstance(nested_via, str).
Ung vien dai: xem PREREG_v3.md (khoa md5 truoc khi chay).

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
CE = pd.read_csv(os.path.join(IN, 'cap_events.csv'))
THIN_ADV = 1e8; THIN_DAYS = 20


def _q_end(q):
    return pd.Timestamp(q[:4] + QEND[q[4:]]) if isinstance(q, str) and len(q) == 6 else pd.NaT


# ---- so CP cuoi cung (p, D): nguon v2 -> TREASURY_FIX -> cau noi ISS (thuong / co tuc CP) ----
SHFIX = {}; SHLOG = []
for t, g in SH.groupby('ticker'):
    g = g.sort_values('date'); cur = {}
    ev_t = CE[CE.ticker == t]
    for _, s0 in g.iterrows():
        sh, meth = (s0.live_value, s0.method) if pd.notna(s0.live_value) else (s0.fin_released, 'FIN_FALLBACK')
        if pd.isna(sh) or sh <= 0: continue
        # co phieu quy: AIS dem CP PHAT HANH; BQ OShares (quy da cong bo <= D) = CP luu hanh. Chi khi khong co su kien CP nao ex sau cuoi quy BQ.
        if str(meth).startswith('AIS') and pd.notna(s0.fin_released) and s0.fin_released > 0:
            qe = _q_end(s0.fin_q); dev = sh / s0.fin_released - 1
            later = ev_t[(pd.to_datetime(ev_t.exright_date) > qe) & (pd.to_datetime(ev_t.exright_date) <= pd.Timestamp(s0.date))] if qe == qe else ev_t.iloc[:0]
            if 0.005 < dev <= 0.15 and not len(later):
                SHLOG.append(dict(ticker=t, date=s0.date, rule='TREASURY_FIX', before=float(sh), after=float(s0.fin_released), meth=meth,
                                  note=f"AIS {sh:,.0f} > BQ {s0.fin_q} {s0.fin_released:,.0f} (+{dev:.2%})"))
                sh, meth = float(s0.fin_released), meth + '+TREASURY_FIX'
        cur[s0.date] = [float(sh), meth]
    ds = sorted(cur)
    # thuong + co tuc CP CUNG ngay ex tinh tren cung so CP luu hanh truoc ex -> cong ty le (BSR 0,315+0,30 -> x1,615 da kiem)
    evb = ev_t[ev_t.issue_method_code.isin(['Bonus', 'DIV'])].groupby('exright_date').agg(
        exercise_ratio=('exercise_ratio', 'sum'), issue_method_code=('issue_method_code', lambda x: '+'.join(sorted(x)))).reset_index()
    for _, e in evb.sort_values('exright_date').iterrows():
        r = float(e.exercise_ratio); E = e.exright_date
        pre = [d for d in ds if d < E]
        if not pre or not r > 0: continue
        Spre = cur[pre[-1]][0]; exp = Spre * (1 + r)
        for d in [d for d in ds if d >= E]:
            v = cur[d][0]
            if v < exp * 0.98 and v <= Spre * (1 + r / 2):
                SHLOG.append(dict(ticker=t, date=d, rule='ISS_FIX', before=v, after=exp, meth=cur[d][1],
                                  note=f"{e.issue_method_code} {r:.4f} ex {E}; S_pre {pre[-1]} {Spre:,.0f}"))
                cur[d] = [exp, cur[d][1] + '+ISS_FIX']
    for d, v in cur.items(): SHFIX[(t, d)] = v
SHLOG = pd.DataFrame(SHLOG)


def mv(t, d, stale_ok=False):
    if (t, d) not in PXi.index or (t, d) not in SHFIX: return None
    p = PXi.loc[(t, d)]; sh, meth = SHFIX[(t, d)]
    stale = (p.sessions_since_trade > STALE_SESS) or (p.adv60_mean <= 0)
    return dict(mv=float(p.price * sh), stale=bool(stale), liq=bool(p.in_universe), meth=meth, shares=float(sh), px_date=p.px_date,
                thin=bool((p.days_traded60 < THIN_DAYS) or (p.adv60_mean < THIN_ADV)), adv60=float(p.adv60_mean))


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
ST['nested_via'] = [NEST.get((p, j), '') for p, j in zip(ST.parent, ST['sub'])]


# ---- panel (p, D, regime pit|fixed, stale rule main|v1, thin rule market|book|half) ----
EQC = {}


def equity_c(t, D):
    k = (t, D)
    if k not in EQC: EQC[k] = equity(t, D)
    return EQC[k]


def run(regime, stale_rule, thin_rule='market'):
    rows = []
    for p in QUAL:
        subs_p = ST[ST.parent == p]
        for d in DATES:
            D = pd.Timestamp(d); m = mv(p, d)
            Ep, qp, srcp, _ = equity_c(p, D)
            if m is None or np.isnan(Ep): continue
            lmv = lbook = lmv_ctrl = lmv_liq = nci_est = stale_book = thin_mv = 0.0; n_used = n_stale = n_fb = n_thin = 0; subs_used = []
            for _, r in subs_p.iterrows():
                if isinstance(r.nested_via, str) and r.nested_via: continue
                if regime == 'pit' and pd.Timestamp(r.stake_date) + pd.Timedelta(days=90) > D: continue
                s = r.stake / 100.0; mi = mv(r['sub'], d); Ei, qi, srci, _ = equity_c(r['sub'], D)
                if mi is None or np.isnan(Ei): continue
                if s >= 0.5: nci_est += (1 - s) * Ei
                if mi['stale'] and stale_rule == 'main': n_stale += 1; stale_book += s * Ei; continue
                w = 1.0
                if mi['thin']:
                    n_thin += 1; thin_mv += s * mi['mv']
                    w = {'market': 1.0, 'book': 0.0, 'half': 0.5}[thin_rule]
                n_used += 1; n_fb += srci != 'VCI_parent'
                lmv += w * s * mi['mv']; lbook += w * s * Ei
                if s >= 0.5: lmv_ctrl += w * s * mi['mv']
                if mi['liq']: lmv_liq += w * s * mi['mv']
                subs_used.append(f"{r['sub']}:{s:.3f}" + ('t' if mi['thin'] else ''))
            eq_src = srcp
            if srcp == 'BQ_total_inclNCI': Ep -= nci_est; eq_src = 'APPROX_BQtot_minus_listedNCI'
            sotp = lmv + (Ep - lbook)
            if sotp <= 0: continue
            rows.append(dict(parent=p, date=d, mv_p=m['mv'] / 1e9, parent_stale=m['stale'], parent_liq=m['liq'], parent_sh_meth=m['meth'],
                             eq_p=Ep / 1e9, eq_q=qp, eq_src=eq_src, listed_mv=lmv / 1e9, listed_book=lbook / 1e9, stale_book=stale_book / 1e9,
                             resid_book=(Ep - lbook) / 1e9, sotp=sotp / 1e9, coverage=lmv / sotp, cov_liq=lmv_liq / sotp,
                             thin_share=thin_mv / lmv if lmv > 0 else np.nan,
                             ctrl_share=lmv_ctrl / lmv if lmv > 0 else np.nan,
                             ck=1 - m['mv'] / sotp, n_subs=n_used, n_stale=n_stale, n_thin=n_thin, n_sub_eq_fallback=n_fb, subs=' '.join(subs_used)))
    R = pd.DataFrame(rows)
    return R[~R.parent_stale.astype(bool)].reset_index(drop=True) if len(R) else R


KEYS = [('pit', 'main', 'market'), ('pit', 'main', 'book'), ('pit', 'main', 'half'), ('pit', 'v1', 'market'),
        ('fixed', 'main', 'market'), ('fixed', 'v1', 'market')]
PAN = {k: run(*k) for k in KEYS}
MAIN = PAN[('pit', 'main', 'market')]

# ---- co tuc tien con -> me (12 thang truoc D) / gia tri niem yet ; tang chong ----
DV['ex'] = pd.to_datetime(DV.exright_date)
NOTNEST = ~ST.nested_via.map(lambda v: isinstance(v, str) and v != '')


def div_in_yield(p, d):
    D = pd.Timestamp(d); tot = 0.0
    for _, r in ST[(ST.parent == p) & NOTNEST].iterrows():
        m = mv(r['sub'], d, True)
        if m is None: continue
        dps = DV[(DV.ticker == r['sub']) & (DV.ex > D - pd.Timedelta(days=365)) & (DV.ex <= D)].value_per_share.sum()
        tot += r.stake / 100 * m['shares'] * dps
    return tot / 1e9


ALLST = pd.read_csv(os.path.join(IN, 'stakes_all.csv'))


def stacked(p):
    f = os.path.join(RAW, 'kbs_sh', p + '.json'); up = []
    if os.path.exists(f): up += [(name2tk.get(norm(r.get('name'))), r.get('ownership_percentage')) for r in json.load(open(f))
                                 if name2tk.get(norm(r.get('name'))) and float(r.get('ownership_percentage') or 0) >= 50]
    g = ALLST[(ALLST['sub'] == p) & (ALLST.stake >= 50)]
    up += list(zip(g.parent, g.stake))
    return sorted(set((a, float(s)) for a, s in up))


def major_holders(p):
    """Tong % co dong lon >=5% cua me (KBS shareholders); None neu khong co du lieu."""
    f = os.path.join(RAW, 'kbs_sh', p + '.json')
    if not os.path.exists(f): return None
    x = [float(r.get('ownership_percentage') or 0) for r in json.load(open(f))]
    return float(sum(v for v in x if v >= 5)) if x else None


def hold_summary(R, cov_min=0.60, min_months=3):
    K = R[R.coverage >= cov_min]
    H = K.groupby('parent').agg(ck=('ck', 'median'), ck_mean=('ck', 'mean'), ck_min=('ck', 'min'), ck_max=('ck', 'max'), months=('ck', 'count'),
                                coverage=('coverage', 'median'), cov_liq=('cov_liq', 'median'), ctrl_share=('ctrl_share', 'median'),
                                thin_share=('thin_share', 'median'), resid_book=('resid_book', 'median'),
                                eq_src=('eq_src', 'last'), sub_fb=('n_sub_eq_fallback', 'max'), first=('date', 'min'), last=('date', 'max')).reset_index()
    return H[H.months >= min_months].reset_index(drop=True)


def stats(x):
    x = np.asarray(x, float); x = x[~np.isnan(x)]
    if not len(x): return dict(N=0)
    return dict(N=int(len(x)), median=float(np.median(x)), q25=float(np.percentile(x, 25)), q75=float(np.percentile(x, 75)),
                min=float(x.min()), max=float(x.max()))


def loo(x):
    x = list(map(float, x))
    if len(x) < 3: return {}
    v = [float(np.median(x[:i] + x[i + 1:])) for i in range(len(x))]
    return dict(loo_min=min(v), loo_max=max(v))


def monthly(R, parents, cov_min=0.60, nmin=1):
    K = R[(R.coverage >= cov_min) & R.parent.isin(list(parents))]
    g = K.groupby('date').ck.agg(['median', 'count']); g.columns = ['median', 'n']
    return g[g.n >= nmin]


def block_boot(R, H, B=5000, blk=3, seed=20261124, cov_min=0.60):
    rng = np.random.default_rng(seed); K = R[(R.coverage >= cov_min) & R.parent.isin(list(H.parent))]
    ser = [K[K.parent == p].sort_values('date').ck.to_numpy() for p in H.parent]
    out = np.empty(B)
    for b in range(B):
        hs = rng.integers(0, len(ser), len(ser)); vals = []
        for h in hs:
            x = ser[h]; T = len(x); nb = int(np.ceil(T / blk)); st = rng.integers(0, T, nb)
            idx = np.concatenate([(s0 + np.arange(blk)) % T for s0 in st])[:T]; vals.append(np.median(x[idx]))
        out[b] = np.median(vals)
    return dict(boot_p5=float(np.percentile(out, 5)), boot_p50=float(np.percentile(out, 50)), boot_p95=float(np.percentile(out, 95)), B=B, block_months=blk)


def enrich(H):
    H = H.copy()
    H['div_in_ann_yield'] = [float(np.mean([div_in_yield(p, d) for d in MAIN[MAIN.parent == p].date]) /
                                   max(MAIN[MAIN.parent == p].listed_mv.mean(), 1e-9)) for p in H.parent]
    H['control'] = H.ctrl_share >= 0.5
    H['stacked_above'] = [';'.join(f"{a}:{s:.1f}" for a, s in stacked(p)) for p in H.parent]
    H['eq_exact'] = (H.eq_src == 'VCI_parent') & (H.sub_fb == 0)
    H['parent_in_pit'] = H.parent.map(dict(zip(U0.ticker, U0.in_pit_any_monthend))).fillna(False).astype(bool)
    H['major_holders_pct'] = [major_holders(p) for p in H.parent]
    H['R1_freefloat'] = [v is not None and v >= 85 for v in H.major_holders_pct]
    H['R2_neg_resid_book'] = H.resid_book < 0
    return H


H = enrich(hold_summary(MAIN))
res = {'N_main': int(len(H)), 'all': {**stats(H.ck), **block_boot(MAIN, H), **loo(H.ck)}}

# ---- (d) duong theo thang + T_eff chi tren thang n>=11 ----
lines = {}
for k, R in PAN.items():
    K = R[R.coverage >= 0.60]
    g = K.groupby('date').ck.agg(['median', 'count', lambda s: s.quantile(.25), lambda s: s.quantile(.75)])
    g.columns = ['median', 'n', 'q25', 'q75']; lines['_'.join(k)] = g.round(4).reset_index().to_dict('records')
ml_all = pd.DataFrame(lines['pit_main_market']); ml = ml_all[ml_all.n >= 11].reset_index(drop=True)
rho = float(pd.Series(ml['median'].to_numpy()).autocorr(1)) if len(ml) > 3 else np.nan
T = len(ml)
res['time'] = dict(T_months_n_ge11=T, months=list(ml.date), lag1_autocorr=rho,
                   T_eff=float(T * (1 - rho) / (1 + rho)) if rho == rho and rho < 1 else np.nan,
                   v2_style_all_months=dict(T=len(ml_all), rho=float(pd.Series(ml_all['median'].to_numpy()).autocorr(1)) if len(ml_all) > 3 else np.nan))

# ---- do nhay ----
sens = {}
for c in [0.5, 0.6, 0.7]: sens[f'cov{int(c*100)}'] = stats(hold_summary(MAIN, c).ck)
sens['v1_stale_kept_pit'] = stats(hold_summary(PAN[('pit', 'v1', 'market')]).ck)
sens['thin_to_book'] = stats(hold_summary(PAN[('pit', 'main', 'book')]).ck)
sens['thin_half'] = stats(hold_summary(PAN[('pit', 'main', 'half')]).ck)
sens['fixed_stake_main'] = stats(hold_summary(PAN[('fixed', 'main', 'market')]).ck)
sens['fixed_stake_v1'] = stats(hold_summary(PAN[('fixed', 'v1', 'market')]).ck)
sens['eq_exact_only'] = stats(H[H.eq_exact].ck)
sens['cov_liquid_ge60'] = stats(H[H.cov_liq >= 0.6].ck)
sens['parent_in_pit_only'] = stats(H[H.parent_in_pit].ck)
sens['ex_VIC'] = stats(H[H.parent != 'VIC'].ck)
sens['ex_VIC_MVN'] = stats(H[~H.parent.isin(['VIC', 'MVN'])].ck)
sens['ex_thin_dominated(thin_share>=0.5)'] = stats(H[~(H.thin_share >= 0.5)].ck)

V2N = ['APH', 'CMX', 'GEX', 'IPA', 'LHC', 'MSN', 'MVN', 'OGC', 'PAN', 'SNZ', 'VIC', 'VSC']
BANNED = ['PC1', 'VVS', 'KSF', 'NKG', 'HSG', 'HVN', 'VJC', 'NVL', 'GEG', 'SBA', 'DMC', 'IMP', 'TRA', 'TOS', 'VTP', 'BAF']   # fleet BANNED (KB)
sens['v2_sample_12_v3_rules'] = stats(H[H.parent.isin(V2N)].ck)
sens['ex_banned(KSF)'] = stats(H[~H.parent.isin(BANNED)].ck)
mv2 = monthly(MAIN, V2N, nmin=11)
sens['v2_sample_monthly_n_ge11'] = mv2.round(4).reset_index().to_dict('records')
# POST-HOC (khong dung de chon dai): chi R1, de thay R2 bat ca holding no rong o cap me
Hb1 = H[~H.R1_freefloat]
sens['POSTHOC_b_R1_only'] = {**stats(Hb1.ck), 'excluded': sorted(set(H.parent) - set(Hb1.parent))}
sens['POSTHOC_b_R1_plus_VIC'] = {**stats(Hb1[Hb1.parent != 'VIC'].ck)}

# ---- PHAN 2: ung vien dai (theo PREREG_v3.md) ----
cand = {}
# (a) luoi dac ta PIT: cov {50,60,70} x VIC {co,khong} x mong {gia,so}
grid = []
for c in [0.5, 0.6, 0.7]:
    for vic in [True, False]:
        for th in ['market', 'book']:
            Hg = hold_summary(PAN[('pit', 'main', th)], c)
            if not vic: Hg = Hg[Hg.parent != 'VIC']
            grid.append(dict(cov=c, with_VIC=vic, thin=th, N=int(len(Hg)), median=float(np.median(Hg.ck)) if len(Hg) else np.nan))
G = pd.DataFrame(grid)
cand['a_spec_grid'] = dict(low=float(G['median'].min()), mid=float(res['all']['median']), high=float(G['median'].max()),
                           N_range=[int(G.N.min()), int(G.N.max())], **loo(H.ck), what='bat dinh TRUNG TAM qua dac ta (PIT)')
# (b) loai cau truc R1/R2
Hb = H[~(H.R1_freefloat | H.R2_neg_resid_book)]
mb = monthly(MAIN, Hb.parent, nmin=5)
cand['b_struct_excl_IQR'] = dict(low=float(np.percentile(Hb.ck, 25)), mid=float(np.median(Hb.ck)), high=float(np.percentile(Hb.ck, 75)),
                                 N=int(len(Hb)), excluded=sorted(set(H.parent) - set(Hb.parent)), **loo(Hb.ck),
                                 center_monthly_min=float(mb['median'].min()) if len(mb) else np.nan,
                                 center_monthly_max=float(mb['median'].max()) if len(mb) else np.nan,
                                 what='PHAN TAN lien-holding (mot holding bat ky), sau loai cau truc')
cand['b_struct_excl_center'] = stats(Hb.ck)
# (c) co dieu kien giong HHS
t1 = float(np.percentile(H.div_in_ann_yield, 100 / 3)) if len(H) else np.nan
condsets = {'c1_control_lowdiv(<1%)': H[H.control & (H.div_in_ann_yield < 0.01)],
            'c2_lowest_div_tercile': H[H.div_in_ann_yield <= t1],
            'c3_control': H[H.control],
            'c3b_control_struct_excl': Hb[Hb.control]}
for k, Hc in condsets.items():
    mc = monthly(MAIN, Hc.parent, nmin=3)
    cand[k] = dict(N=int(len(Hc)), parents=sorted(Hc.parent), **(dict(low=float(np.percentile(Hc.ck, 25)), mid=float(np.median(Hc.ck)),
                   high=float(np.percentile(Hc.ck, 75))) if len(Hc) else {}), **loo(Hc.ck), enough=bool(len(Hc) >= 8),
                   center_monthly_min=float(mc['median'].min()) if len(mc) else np.nan, center_monthly_max=float(mc['median'].max()) if len(mc) else np.nan)
cand['c2_tercile_cut'] = t1
# (d) theo thoi gian (thang n>=11)
cand['d_monthly_n_ge11'] = dict(low=float(ml['median'].min()) if T else np.nan, mid=float(ml['median'].median()) if T else np.nan,
                                high=float(ml['median'].max()) if T else np.nan, q25=float(ml['median'].quantile(.25)) if T else np.nan,
                                q75=float(ml['median'].quantile(.75)) if T else np.nan, T=T, n_range=[int(ml.n.min()), int(ml.n.max())] if T else [],
                                what='trung tam troi theo thoi gian (1 che do)')
# loo theo thang cho (d): bo tung holding, trung vi duong thang
dl = []
for p in H.parent:
    m2 = monthly(MAIN, [q for q in H.parent if q != p], nmin=10)
    dl.append((p, float(m2['median'].min()), float(m2['median'].max())))
cand['d_loo'] = dict(min_low=min(x[1] for x in dl), max_low=max(x[1] for x in dl), min_high=min(x[2] for x in dl), max_high=max(x[2] for x in dl))
for k, v in cand.items():
    if isinstance(v, dict) and 'low' in v and 'high' in v: v['width_pp'] = float((v['high'] - v['low']) * 100)
# chon theo PREREG C
use_c = cand['c1_control_lowdiv(<1%)']['enough']
A = cand['c1_control_lowdiv(<1%)'] if use_c else cand['a_spec_grid']
ref_low = min(A['low'], cand['d_monthly_n_ge11']['low']); ref_high = max(A['high'], cand['d_monthly_n_ge11']['high'])
loo_ok = ('loo_min' in A) and ref_low <= A['loo_min'] and A['loo_max'] <= ref_high
width = (ref_high - ref_low) * 100
choice = dict(source='c1+d' if use_c else 'a+d', low=ref_low, mid=float(res['all']['median']), high=ref_high, width_pp=width,
              meaningful=bool(width <= 20 and loo_ok), loo_inside=bool(loo_ok),
              zero_position=('duoi dai' if 0 < ref_low else 'tren dai' if 0 > ref_high else f"trong dai, phan vi {(0 - ref_low) / (ref_high - ref_low):.2f}"))

# ---- phan tach troi ----
dec = []
for p in H.parent:
    g = MAIN[(MAIN.parent == p) & (MAIN.coverage >= 0.6)].sort_values('date')
    if len(g) < 2: continue
    a, b = g.iloc[0], g.iloc[-1]
    dec.append(dict(parent=p, d0=a.date, d1=b.date, ck0=a.ck, ck1=b.ck, dln_mv_parent=np.log(b.mv_p / a.mv_p), dln_sotp=np.log(b.sotp / a.sotp)))
DEC = pd.DataFrame(dec)

# ---- loai tru + vao/ra so voi v2 ----
allq = pd.read_csv(os.path.join(IN, 'qualified_parents.csv')).parent.tolist(); EXC = []
for p in allq:
    if p in set(H.parent): continue
    g = MAIN[MAIN.parent == p]
    if not len(g): EXC.append(dict(parent=p, reason='khong co gia me / VCSH me / so CP (hoac gia me STALE, SOTP<=0) tai moi ngay')); continue
    k = g[g.coverage >= 0.6]
    EXC.append(dict(parent=p, reason=f"do phu trung vi {g.coverage.median():.2f}; so thang >=60%: {len(k)} (<3)"
                    + (f"; co con STALE (toi da {int(g.n_stale.max())})" if g.n_stale.max() > 0 else '')))
EXC = pd.DataFrame(EXC)
inout = dict(new_in=sorted(set(H.parent) - set(V2N)), out=sorted(set(V2N) - set(H.parent)))
# ---- audit so CP: moi ma trong panel chinh (me + con dung) ----
used = set(MAIN.parent) | {x.split(':')[0] for s_ in MAIN.subs for x in s_.split() if x}
SHA = SHLOG[SHLOG.ticker.isin(sorted(used))] if len(SHLOG) else SHLOG
# su kien CP (moi loai) ex trong cua so cua ma dang dung: kiem lech so CP dung vs S_pre x (1+r) (chi bao, Rights/PP/EMPL khong sua)
aud = []
for _, e in CE[CE.ticker.isin(sorted(used))].iterrows():
    ds = [d for d in DATES if (e.ticker, d) in SHFIX]
    pre = [d for d in ds if d < e.exright_date]; post = [d for d in ds if d >= e.exright_date]
    if not pre or not post: continue
    a0 = SHFIX[(e.ticker, pre[-1])][0]; a1 = SHFIX[(e.ticker, post[0])][0]
    aud.append(dict(ticker=e.ticker, ex=e.exright_date, method=e.issue_method_code, ratio=e.exercise_ratio, d_pre=pre[-1], d_post=post[0],
                    sh_ratio=a1 / a0, expected=1 + (e.exercise_ratio if pd.notna(e.exercise_ratio) else 0), listing=e.listing_date))
AUD = pd.DataFrame(aud)
if len(AUD):
    AUD['expected_sameday'] = AUD.groupby(['ticker', 'ex']).ratio.transform(lambda x: 1 + x.fillna(0).sum())
    AUD['gap'] = AUD.sh_ratio - AUD.expected_sameday
# ma thuoc tap N (me + con dang dung cua holding trong N)
usedN = set(H.parent) | {x.split(':')[0] for s_ in MAIN[MAIN.parent.isin(list(H.parent))].subs for x in s_.split() if x}
AUDN = AUD[AUD.ticker.isin(sorted(usedN))] if len(AUD) else AUD
SHAN = SHA[SHA.ticker.isin(sorted(usedN))] if len(SHA) else SHA

pd.set_option('display.width', 260); pd.set_option('display.max_columns', 40); pd.set_option('display.max_colwidth', 70); pd.set_option('display.max_rows', 500)
print('== sua so CP (TREASURY_FIX / ISS_FIX) tren ma dang dung ==\n', SHA.to_string(index=False) if len(SHA) else '(rong)')
print('\n== audit su kien CP (ma dang dung) ==\n', AUD.round(4).to_string(index=False) if len(AUD) else '(rong)')
print('\n== sua so CP tren tap N ==\n', SHAN.to_string(index=False) if len(SHAN) else '(rong)')
print('\n== audit su kien CP tren tap N (|gap|>2%) ==\n', AUDN[AUDN.gap.abs() > 0.02].round(4).to_string(index=False) if len(AUDN) else '(rong)')
print('\n== loai tru ==\n', EXC.to_string(index=False))
print('\n== vao/ra so voi v2 ==', json.dumps(inout))
print('\n== holding (PIT, loai stale, do phu>=60%, >=3 thang) ==\n', H.round(4).to_string(index=False))
print('\n== ket qua ==', json.dumps(res, default=float, indent=0))
print('\n== do nhay ==\n', json.dumps(sens, default=float, indent=0))
print('\n== luoi dac ta (a) ==\n', G.round(4).to_string(index=False))
print('\n== ung vien dai ==\n', json.dumps(cand, default=float, indent=0, ensure_ascii=False))
print('\n== chon (PREREG C) ==\n', json.dumps(choice, default=float, indent=0, ensure_ascii=False))
print('\n== duong theo thang pit_main_market ==\n', ml_all.to_string(index=False))
for k in ['pit_main_book', 'pit_v1_market', 'fixed_main_market']: print(f'\n== duong {k} ==\n', pd.DataFrame(lines[k]).to_string(index=False))
print('\n== phan tach troi ==\n', DEC.round(4).to_string(index=False))
print('\n== con long nhau bi bo ==', nested)
ALL = pd.concat([R.assign(regime=k[0], stale_rule=k[1], thin_rule=k[2]) for k, R in PAN.items()])
ALL.round(6).to_csv(os.path.join(HERE, 'panel_v3.csv'), index=False)
out = dict(holdings=H.round(6).to_dict('records'), result=res, sens=sens, grid=G.round(6).to_dict('records'), candidates=cand, choice=choice,
           lines=lines, decomposition=DEC.round(6).to_dict('records'), nested=nested, excluded=EXC.to_dict('records'), inout_vs_v2=inout,
           share_fixes=SHA.to_dict('records') if len(SHA) else [], share_fixes_N=SHAN.to_dict('records') if len(SHAN) else [], share_audit_N=AUDN.round(6).to_dict('records') if len(AUDN) else [], share_audit=AUD.round(6).to_dict('records') if len(AUD) else [])


def _clean(o):
    if isinstance(o, dict): return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [_clean(v) for v in o]
    if isinstance(o, (bool, np.bool_)): return bool(o)
    if isinstance(o, (int, np.integer)): return int(o)
    if isinstance(o, (float, np.floating)): return None if o != o else round(float(o), 6)
    if o is None or (not isinstance(o, str) and pd.isna(o)): return None
    return str(o)


s = json.dumps(_clean(out), ensure_ascii=False, sort_keys=True)
open(os.path.join(HERE, 'calc_out_v3.json'), 'w').write(s)
print('calc_out md5', hashlib.md5(s.encode()).hexdigest())
