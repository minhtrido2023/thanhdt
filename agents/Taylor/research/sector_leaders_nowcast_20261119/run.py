"""Mã đầu ngành × nowcast ngành — thực thi đúng PREREG.md (md5 4de8f316..., commit f485ae696).
Chạy: /home/trido/thanhdt/wc_venv/bin/python run.py   (threads=1, seed 20261119)"""
import os, sys, json
os.environ.setdefault('OMP_NUM_THREADS', '1')
import numpy as np, pandas as pd
from scipy.stats import spearmanr
O = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(O, '..', 'commodity_cycle_te_20261026'))
from common import te, cmap, px, univ, fin, bench, W   # noqa: E402
import glob

SEED = 20261119; K = 2; NB = 5000; NP = 2000; NPLAC = 200
rng = np.random.default_rng(SEED)
FAMS = ['rubber_tsr20', 'crude', 'sugar', 'steel_cn']

T = te(); P = px(); U = univ(); F = fin(); Bm = bench(P, U); Bc = (1 + Bm).cumprod()
tv = pd.concat([pd.read_parquet(f, columns=['ticker', 'time', 'Trading_Value'])
                for f in sorted(glob.glob(f'{W}/data/bq_cache/ticker/*.parquet'))])
tv['time'] = pd.to_datetime(tv.time)
TV = tv.pivot_table(index='time', columns='ticker', values='Trading_Value').sort_index().reindex(P.index)
TV60 = TV.rolling(60, min_periods=40).median().shift(1)   # kết thúc ở phiên LIỀN TRƯỚC
idx = P.index
Ur = U.reindex(idx).fillna(False)

def at(d):
    i = idx.searchsorted(d); return idx[i] if i < len(idx) else None
def off(d, n):
    i = idx.get_loc(d) + n; return idx[i] if i < len(idx) else None

qa = T.resample('QE').mean(); qn = T.resample('QE').count(); qa = qa.where(qn >= 40)
M = cmap(('A',))

# ---------------- 0. Đối chứng tái lập b2 ----------------
def npd(r):
    return float(np.clip((r.NP_P0 - r.NP_P4) / r.Revenue_P4, -.5, .5)) if r.Revenue_P4 > 0 else np.nan
ctrl = []
for _, m in M.iterrows():
    s = qa[m.te_metric_key]; yoy = np.log(s / s.shift(4))
    for _, r in F[F.ticker == m.ticker].iterrows():
        qe = r.qend
        if qe not in s.index or pd.isna(yoy.get(qe)): continue
        sig = at(qe + pd.Timedelta(days=2))
        if sig is None or r.Release_Date <= sig: continue
        if m.ticker not in U.columns or sig not in U.index or not U.at[sig, m.ticker]: continue
        ctrl.append(dict(ticker=m.ticker, family=m.family, quarter=r.quarter, c_yoy=yoy[qe] * m.sign, np_d=npd(r)))
C = pd.DataFrame(ctrl)
b2 = pd.read_csv(os.path.join(O, '..', 'commodity_cycle_te_20261026', 'b2_panel.csv'))
b2 = b2[b2.tier == 'A']
mm = b2.merge(C, on=['ticker', 'family', 'quarter'], suffixes=('_b2', '_new'))
match = float(((mm.np_d_b2 - mm.np_d_new).abs() < 1e-6).mean())
def pooled_ic(G, x, y):
    G = G.dropna(subset=[x, y]).copy()
    G['rx'] = G.groupby('family')[x].rank(pct=True) - .5; G['ry'] = G.groupby('family')[y].rank(pct=True) - .5
    return float(np.corrcoef(G.rx, G.ry)[0, 1]) if len(G) > 5 else np.nan
Cq = C[C.quarter <= '2026Q2'].groupby(['family', 'quarter']).agg(c_yoy=('c_yoy', 'first'), np_d=('np_d', 'median')).reset_index()
ctrl_ic = pooled_ic(Cq, 'c_yoy', 'np_d')
CTRL = dict(rows_b2=len(b2), rows_matched=len(mm), match_frac=round(match, 4), ic_pooled_recalc=round(ctrl_ic, 4),
            pass_=bool(match >= .98 and abs(ctrl_ic - .450) <= .02))
print('CONTROL', CTRL)
if not CTRL['pass_']:
    json.dump(dict(control=CTRL), open(os.path.join(O, 'results.json'), 'w'), indent=1)
    sys.exit('CONTROL FAIL — dừng theo PREREG §5')

# ---------------- 1. Panel đầu ngành ----------------
Ff = F.set_index(['ticker', 'quarter'])
def ret(tks, d0, d1):
    if d0 is None or d1 is None or not tks: return np.nan
    a = P.loc[d0, tks]; b = P.loc[d1, tks]; r = (b / a - 1)[(a > 0) & (b > 0)]
    return float(r.mean()) if len(r) else np.nan
def uret(d0, d1):
    return float(Bc[d1] / Bc[d0] - 1) if d0 is not None and d1 is not None else np.nan
def np_leg(tks, quarter, sig):
    v = []
    for t in tks:
        if (t, quarter) in Ff.index:
            r = Ff.loc[(t, quarter)]
            if r.Release_Date > sig: v.append(npd(r))
    v = [x for x in v if pd.notna(x)]
    return float(np.median(v)) if v else np.nan

rows, lead_rows = [], []
for fam in FAMS:
    mf = M[M.family == fam]; key = mf.te_metric_key.iloc[0]; sgn = mf.sign.iloc[0]; members = list(mf.ticker)
    s = qa[key]; yoy = np.log(s / s.shift(4))
    for qe in yoy.dropna().index:
        q = pd.Period(qe, 'Q'); d0 = at(q.start_time)
        sig = at(qe + pd.Timedelta(days=2))
        if d0 is None or sig is None: continue
        el = [t for t in members if t in Ur.columns and bool(Ur.at[d0, t]) and t in TV60.columns and pd.notna(TV60.at[d0, t])]
        if len(el) < K + 1: continue
        g = TV60.loc[d0, el].sort_values(ascending=False)
        L = list(g.index[:K]); R = list(g.index[K:])
        quarter = f'{q.year}Q{q.quarter}'; c = float(yoy[qe] * sgn)
        h1 = off(sig, 21); h3 = off(sig, 63)
        rec = dict(family=fam, quarter=quarter, qend=qe, d0=d0, sig=sig, c=c, L=','.join(L), R=','.join(R),
                   npL=np_leg(L, quarter, sig), npR=np_leg(R, quarter, sig))
        for hn, (a, b) in {'H0': (d0, sig), 'H1': (sig, h1), 'H3': (sig, h3)}.items():
            rec[f'{hn}L'] = ret(L, a, b); rec[f'{hn}R'] = ret(R, a, b); rec[f'{hn}U'] = uret(a, b)
        rows.append(rec)
        for t in L: lead_rows.append(dict(family=fam, quarter=quarter, d0=d0, ticker=t, tv60_bn=float(g[t]) / 1e9))
D = pd.DataFrame(rows).sort_values(['quarter', 'family']).reset_index(drop=True)
D['IS'] = D.quarter < '2023Q1'; D['year'] = pd.to_datetime(D.qend).dt.year
D.to_csv(os.path.join(O, 'panel_famq.csv'), index=False)
LR = pd.DataFrame(lead_rows); LR.to_csv(os.path.join(O, 'leaders_by_quarter.csv'), index=False)

# ---------------- 2. Trial ----------------
def s_(d): return np.sign(d.c)
TR = {
 'T1_dIC_np': lambda d: pooled_ic(d, 'c', 'npL') - pooled_ic(d, 'c', 'npR'),
 'T2_np_down': lambda d: float((d.npL - d.npR)[d.c < 0].mean()),
 'T3_np_up': lambda d: float((d.npL - d.npR)[d.c > 0].mean()),
 'T4_H0_vsR': lambda d: float((s_(d) * (d.H0L - d.H0R)).mean()),
 'T5_H1_vsR': lambda d: float((s_(d) * (d.H1L - d.H1R)).mean()),
 'T6_H3_vsR': lambda d: float((s_(d) * (d.H3L - d.H3R)).mean()),
 'T7_H0_vsU': lambda d: float((s_(d) * (d.H0L - d.H0U)).mean()),
 'T8_H1_vsU': lambda d: float((s_(d) * (d.H1L - d.H1U)).mean()),
 'T9_H3_vsU': lambda d: float((s_(d) * (d.H3L - d.H3U)).mean()),
}
NEED = {'T1_dIC_np': ['npL', 'npR'], 'T2_np_down': ['npL', 'npR'], 'T3_np_up': ['npL', 'npR'],
        'T4_H0_vsR': ['H0L', 'H0R'], 'T5_H1_vsR': ['H1L', 'H1R'], 'T6_H3_vsR': ['H3L', 'H3R'],
        'T7_H0_vsU': ['H0L', 'H0U'], 'T8_H1_vsU': ['H1L', 'H1U'], 'T9_H3_vsU': ['H3L', 'H3U']}
# lưới c theo quý cho dịch vòng chung
Q_all = sorted(D.quarter.unique()); nq = len(Q_all); qpos = {q: i for i, q in enumerate(Q_all)}
cgrid = {}
for fam in FAMS:
    mf = M[M.family == fam]; s = qa[mf.te_metric_key.iloc[0]]; yoy = np.log(s / s.shift(4)) * mf.sign.iloc[0]
    cgrid[fam] = np.array([yoy.get(pd.Period(q, 'Q').end_time.normalize(), np.nan) for q in Q_all])

def boot(d, f):
    qs = sorted(d.quarter.unique()); n = len(qs); byq = {q: d[d.quarter == q] for q in qs}; out = []
    for _ in range(NB):
        pick = []
        while len(pick) < n:
            st = rng.integers(0, max(n - 3, 1)); pick += qs[st:st + 4]
        out.append(f(pd.concat([byq[q] for q in pick[:n]])))
    return np.array(out)
def perm(d, f):
    out = []
    for _ in range(NP):
        k = int(rng.integers(4, nq - 3)); d2 = d.copy()
        d2['c'] = [np.roll(cgrid[fa], k)[qpos[q]] for fa, q in zip(d2.family, d2.quarter)]
        d2 = d2.dropna(subset=['c']); out.append(f(d2))
    return np.array(out)

res = []
for name, f in TR.items():
    d = D.dropna(subset=NEED[name] + ['c'])
    est = f(d); bs = boot(d, f); pm = perm(d, f)
    pm = pm[~np.isnan(pm)]; bsn = bs[~np.isnan(bs)]
    p = (np.sum(np.abs(pm) >= abs(est)) + 1) / (len(pm) + 1)
    loyo = [f(d[d.year != y]) for y in sorted(d.year.unique())]
    sub = {'IS': d[d.IS], 'OOS': d[~d.IS]}
    r = dict(trial=name, est=est, ci90=[float(np.percentile(bsn, 5)), float(np.percentile(bsn, 95))],
             se=float(bsn.std()), mde=float(2.5 * bsn.std()), p=float(p), n_units=len(d), n_quarters=d.quarter.nunique(),
             n_fam=d.family.nunique(), IS=f(sub['IS']), n_IS=len(sub['IS']), OOS=f(sub['OOS']), n_OOS=len(sub['OOS']),
             loyo_min=float(np.nanmin(loyo)), loyo_max=float(np.nanmax(loyo)))
    if name in ('T2_np_down',): r['n_cond'] = int((d.c < 0).sum())
    if name in ('T3_np_up',): r['n_cond'] = int((d.c > 0).sum())
    res.append(r); print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})
R = pd.DataFrame(res)
# BH trên 9
R = R.sort_values('p').reset_index(drop=True); m_ = len(R)
R['bh_q'] = np.minimum.accumulate((R.p * m_ / (np.arange(m_) + 1))[::-1])[::-1].clip(upper=1)
R['bonf38'] = (R.p * 38).clip(upper=1)
R = R.sort_values('trial').reset_index(drop=True)

# ---------------- 3. Placebo cho T7-T9 ----------------
tert = {}
for d0 in D.d0.unique():
    um = Ur.loc[d0].reindex(TV60.columns).fillna(False).astype(bool); v = TV60.loc[d0][um].dropna(); tert[d0] = (v, v.quantile([1 / 3, 2 / 3]).values)
def tercile(v, cuts): return 0 if v <= cuts[0] else (1 if v <= cuts[1] else 2)
fam_members = {f: set(M[M.family == f].ticker) for f in FAMS}
plac = {k: [] for k in ['T7_H0_vsU', 'T8_H1_vsU', 'T9_H3_vsU']}
prng = np.random.default_rng(SEED + 1)
for _ in range(NPLAC):
    dd = D.copy()
    for i, r in dd.iterrows():
        v, cuts = tert[r.d0]; pool = v[[t not in fam_members[r.family] for t in v.index]]
        tc = pool.apply(lambda x: tercile(x, cuts)); picks = []
        for t in r.L.split(','):
            cand = list(tc.index[tc == tercile(v.get(t, np.nan) if t in v.index else TV60.at[r.d0, t], cuts)])
            picks.append(cand[prng.integers(len(cand))])
        h1 = off(r.sig, 21); h3 = off(r.sig, 63)
        dd.at[i, 'H0L'] = ret(picks, r.d0, r.sig); dd.at[i, 'H1L'] = ret(picks, r.sig, h1); dd.at[i, 'H3L'] = ret(picks, r.sig, h3)
    for k in plac: plac[k].append(TR[k](dd.dropna(subset=NEED[k] + ['c'])))
PL = {k: dict(actual=float(R.loc[R.trial == k, 'est'].iloc[0]), plac_median=float(np.median(v)),
              plac_p5=float(np.percentile(v, 5)), plac_p95=float(np.percentile(v, 95)),
              pct_rank=float(np.mean(np.array(v) <= R.loc[R.trial == k, 'est'].iloc[0]))) for k, v in plac.items()}

# ---------------- 4. Capacity + mô tả ----------------
cap = dict(n_leader_quarters=len(LR), pct_ge_0_15bn=float((LR.tv60_bn >= .15).mean()), pct_ge_5bn=float((LR.tv60_bn >= 5).mean()),
           pct_ge_5bn_excl_banned=float((LR[~LR.ticker.isin(['HSG', 'NKG'])].tv60_bn >= 5).mean()))
lastq = LR[LR.quarter == LR.quarter.max()]
cap['latest'] = lastq[['family', 'quarter', 'ticker', 'tv60_bn']].round(2).to_dict('records')
freq = LR.groupby(['family', 'ticker']).size().rename('n_q').reset_index().to_dict('records')
desc = []
for fam, g in D.groupby('family'):
    desc.append(dict(family=fam, n_q=len(g), first=g.quarter.min(), last=g.quarter.max(),
                     ic_npL=pooled_ic(g.assign(), 'c', 'npL'), ic_npR=pooled_ic(g, 'c', 'npR'),
                     T5=float((np.sign(g.c) * (g.H1L - g.H1R)).mean()), T6=float((np.sign(g.c) * (g.H3L - g.H3R)).mean())))
phase = []
for hn in ['H0', 'H1', 'H3']:
    for cmp in ['R', 'U']:
        sp = (D[f'{hn}L'] - D[f'{hn}{cmp}'])
        phase.append(dict(h=hn, vs=cmp, mean_all=float(sp.mean()), up=float(sp[D.c > 0].mean()), down=float(sp[D.c < 0].mean()),
                          n_up=int((D.c > 0).sum()), n_down=int((D.c < 0).sum())))
npd_ph = dict(mean_all=float((D.npL - D.npR).mean()), ic_L=pooled_ic(D, 'c', 'npL'), ic_R=pooled_ic(D, 'c', 'npR'))
print(pd.DataFrame(phase).round(4).to_string()); print(npd_ph)
out = dict(phase_split=phase, npd_split=npd_ph, prereg=dict(md5='4de8f3168eac5a84f4a25766ae4a0191', commit='f485ae696'), control=CTRL,
           n_units=len(D), n_quarters=nq, quarters=[Q_all[0], Q_all[-1]], trials=R.to_dict('records'), placebo=PL,
           capacity=cap, leader_freq=freq, by_family=desc)
json.dump(out, open(os.path.join(O, 'results.json'), 'w'), indent=1, default=str)
pd.set_option('display.width', 250)
print(R[['trial', 'est', 'ci90', 'p', 'bh_q', 'bonf38', 'IS', 'OOS', 'n_units', 'n_quarters', 'mde', 'loyo_min', 'loyo_max']].round(4).to_string())
print(json.dumps(PL, indent=1)); print(json.dumps(cap, indent=1, default=str)); print(pd.DataFrame(desc).round(3).to_string())
