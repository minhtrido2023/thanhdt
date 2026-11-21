#!/usr/bin/env python
"""Basket vs FZ vs CAPIT. Run: $DNA_PYEXE basket_vs_fz.py (cwd=this dir). PREREG.md md5 in PREREG.md5."""
import os, math, numpy as np, pandas as pd
from scipy.stats import norm, skew, kurtosis
HERE = os.path.dirname(os.path.abspath(__file__)); SRC = f'{HERE}/../intraday_cluster_audit_20261119/data'
B = 10000; rng = np.random.default_rng(7); ADJ = 0.00134; ENG = 0.0016; HOLD = 10; TP = 0.06
L = open(f'{HERE}/out/log.txt', 'w')
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); L.write(s + '\n')
cap = pd.read_csv(f'{SRC}/bq/capit_breadth.csv', parse_dates=['time']).set_index('time'); cal = list(cap.index); pos = {d: i for i, d in enumerate(cal)}
fire = cap.oversold >= 0.31
def cl_ids(days, gap=5):
    u = sorted(set(days)); m = {}; c = 0; prev = None
    for x in u:
        if prev is not None and pos[x] - pos[prev] > gap: c += 1
        m[x] = c; prev = x
    return m
def ci(v, f=np.mean):
    v = np.asarray(v); b = np.array([f(rng.choice(v, len(v))) for _ in range(B)]); return np.percentile(b, [5, 95])
def dsr(v, N):
    v = np.asarray(v); T = len(v); sr = v.mean() / v.std(ddof=1); g = 0.5772156649; V = 1 / (T - 1)
    sr0 = math.sqrt(V) * ((1 - g) * norm.ppf(1 - 1 / N) + g * norm.ppf(1 - 1 / (N * math.e)))
    den = math.sqrt(max(1e-12, 1 - skew(v) * sr + (kurtosis(v, fisher=False) - 1) / 4 * sr ** 2))
    return float(norm.cdf((sr - sr0) * math.sqrt(T - 1) / den))
def placebo(v, starts):
    mo = pd.PeriodIndex(starts, freq='M'); um = pd.unique(mo); idx = [np.where(mo == m)[0] for m in um]; obs = v.mean(); cnt = 0
    for _ in range(B):
        s = rng.choice([-1, 1], len(um)); w = np.empty(len(v))
        for k, ix in enumerate(idx): w[ix] = s[k] * v[ix]
        cnt += w.mean() >= obs
    return (cnt + 1) / (B + 1)
# ---- proxy basket (c): per (sym, D) return, same rule as audit #4
D = pd.read_csv(f'{SRC}/bq/daily_ohlc.csv', parse_dates=['time']).sort_values(['ticker', 'time']); recs = []
for sym, g in D.groupby('ticker'):
    g = g.reset_index(drop=True); pc = g.Close.shift(1)
    tr = np.maximum.reduce([g.High - g.Low, (g.High - pc).abs(), (g.Low - pc).abs()])
    atrp = (pd.Series(tr).ewm(alpha=1 / 14, adjust=False, min_periods=14).mean() / g.Close).values
    for i in range(len(g) - 1):
        e = i + 1; di = g.time[i]
        if di not in pos or pos[di] + 1 >= len(cal) or g.time[e] != cal[pos[di] + 1]: continue
        ent = g.Open[e]
        if not (ent > 0) or np.isnan(atrp[i]): continue
        tp = ent * (1 + TP); sl = ent * (1 - 2 * atrp[i]); last = e + HOLD - 1
        if last >= len(g): continue
        ex = g.Close[last]
        for j in range(e + 2, last + 1):
            if g.Low[j] <= sl: ex = min(sl, g.Open[j]) if g.Open[j] < sl else sl; break
            if g.High[j] >= tp: ex = max(tp, g.Open[j]) if g.Open[j] > tp else tp; break
        recs.append((sym, di, g.time[last], ex / ent - 1 - ENG, bool(g.in_universe[i]) if pd.notna(g.in_universe[i]) else False))
A = pd.DataFrame(recs, columns=['symbol', 'D', 'exit_d', 'ret', 'inuni']); A = A[A.inuni]
bday = A.groupby('D').ret.mean(); bexit = A.groupby('D').exit_d.max()   # proxy basket per signal day D (raw, engine-fee)
P(f'proxy basket days={len(bday)}, universe syms={A.symbol.nunique()}')
W = {'insample': (pd.Timestamp('2023-09-11'), pd.Timestamp('2026-04-30')), 'holdout': (pd.Timestamp('2026-05-01'), pd.Timestamp('2026-11-06'))}
rows = []; fzdays = {}
for per in ['insample', 'holdout']:
    for s in ['fz-001', 'fz-002']:
        d = pd.read_csv(f'{SRC}/{per}/deals_{s}.csv', parse_dates=['signal_day']); d = d[d.in_stats == 1].copy()
        d['a'] = d.net_ret_total - ADJ; d['b'] = d.market_drift_same_day - ADJ; d['x'] = d.a - d.b
        assert np.allclose(d.x, d.excess_ret, atol=1e-6), 'excess mismatch'
        cm = cl_ids(d.signal_day); d['cl'] = d.signal_day.map(cm)
        g = d.groupby('cl').agg(a=('a', 'mean'), b=('b', 'mean'), x=('x', 'mean'), start=('signal_day', 'min'), end=('signal_day', 'max'), n=('a', 'size'))
        # CAPIT window flag: fire within [start-5 sessions, end]
        def hasfire(r):
            i0 = max(0, pos[r.start] - 5); i1 = pos[r.end]; return bool(fire.iloc[i0:i1 + 1].any())
        g['capit'] = g.apply(hasfire, axis=1)
        def cbasket(r):
            i0 = max(0, pos[r.start] - 5); i1 = pos[r.end]; ds = [x for x in cal[i0:i1 + 1] if fire[x] and x in bday.index]
            return np.mean([bday[x] for x in ds]) - ADJ if ds else np.nan
        g['c'] = g.apply(cbasket, axis=1)
        # calibration proxy vs engine drift (per signal day)
        dd = d.groupby('signal_day').agg(eng=('market_drift_same_day', 'mean')); dd['prox'] = bday.reindex(dd.index); dd = dd.dropna()
        cal_corr = np.corrcoef(dd.eng, dd.prox)[0, 1] if len(dd) > 3 else np.nan
        T = len(g); r = dict(period=per, setup=s.upper(), clusters=T, deals=len(d), days=d.signal_day.nunique(),
                             a_mean=g.a.mean(), b_mean=g.b.mean(), x_mean=g.x.mean(), ratio_b_over_a=g.b.mean() / g.a.mean() if g.a.mean() else np.nan,
                             clusters_with_capit=int(g.capit.sum()), calib_corr_proxy_vs_engine=cal_corr, calib_days=len(dd),
                             calib_mean_engine=dd.eng.mean() if len(dd) else np.nan, calib_mean_proxy=dd.prox.mean() if len(dd) else np.nan)
        if T >= 3:
            r['x_ci90_lo'], r['x_ci90_hi'] = ci(g.x.values)
            rr = np.array([ (lambda ix: g.b.values[ix].mean() / g.a.values[ix].mean())(rng.integers(0, T, T)) for _ in range(B)]); r['ratio_ci90_lo'], r['ratio_ci90_hi'] = np.percentile(rr, [5, 95])
            r['b_ci90_lo'], r['b_ci90_hi'] = ci(g.b.values); r['a_ci90_lo'], r['a_ci90_hi'] = ci(g.a.values)
        if T >= 15:
            for N in (1000, 65, 250, 30000): r[f'dsr_N{N}'] = dsr(g.x.values, N)
            r['placebo_p'] = placebo(g.x.values, g.start.values); r['sharpe_cluster'] = g.x.mean() / g.x.std(ddof=1)
            loco = [np.delete(g.x.values, k).mean() for k in range(T)]; r['loco_min'], r['loco_max'] = min(loco), max(loco)
            top5 = np.sort(g.x.values)[-5:]; pos_sum = g.x.values[g.x.values > 0].sum(); r['top5_share_pos'] = top5[top5 > 0].sum() / pos_sum if pos_sum > 0 else np.nan
            r['x_ex_top5'] = np.sort(g.x.values)[:-5].mean()
        passed = (per == 'insample') and T >= 20 and r.get('x_mean', 0) > 0 and r.get('x_ci90_lo', -1) > 0
        r['PASS_adds_value_vs_basket'] = bool(passed)
        # FZ with CAPIT vs without
        for flag, nm in [(True, 'with_capit'), (False, 'no_capit')]:
            sub = g[g.capit == flag]; r[f'N_{nm}'] = len(sub)
            r[f'a_{nm}'] = sub.a.mean() if len(sub) else np.nan; r[f'b_{nm}'] = sub.b.mean() if len(sub) else np.nan; r[f'x_{nm}'] = sub.x.mean() if len(sub) else np.nan
            r[f'c_{nm}'] = sub.c.mean() if flag and len(sub) else np.nan
            if len(sub) >= 15: r[f'x_{nm}_ci90_lo'], r[f'x_{nm}_ci90_hi'] = ci(sub.x.values)
        rows.append(r); g.to_csv(f'{HERE}/out/clusters_{per}_{s}.csv'); fzdays[(per, s)] = set(d.signal_day.unique())
        P(f"[{per} {s.upper()}] clusters={T} a={g.a.mean():+.4f} b={g.b.mean():+.4f} excess={g.x.mean():+.4f} CI90=[{r.get('x_ci90_lo',np.nan):+.4f},{r.get('x_ci90_hi',np.nan):+.4f}] ratio b/a={r['ratio_b_over_a']:.2f} capit-clusters={int(g.capit.sum())}/{T} calib corr={cal_corr:.2f}")
pd.DataFrame(rows).to_csv(f'{HERE}/out/basket_vs_fz.csv', index=False)
# ---- CAPIT clusters (c) own, in-sample vs holdout, entry D+1 exit <= window end
crow = []
for per, (w0, w1) in W.items():
    fd = [x for x in cal if fire[x] and w0 <= x <= w1 and x in bday.index and bexit[x] <= w1]
    if not fd: continue
    m = cl_ids(fd); g = pd.DataFrame({'D': fd, 'cl': [m[x] for x in fd], 'c': [bday[x] - ADJ for x in fd]}).groupby('cl').agg(c=('c', 'mean'), start=('D', 'min'), n=('c', 'size'))
    r = dict(period=per, fire_days=len(fd), clusters=len(g), c_mean=g.c.mean())
    if len(g) >= 3: r['c_ci90_lo'], r['c_ci90_hi'] = ci(g.c.values)
    crow.append(r); P(f'[CAPIT basket {per}] fire_days={len(fd)} clusters={len(g)} mean={g.c.mean():+.4f} CI90={r.get("c_ci90_lo",np.nan):+.4f}..{r.get("c_ci90_hi",np.nan):+.4f}')
pd.DataFrame(crow).to_csv(f'{HERE}/out/capit_basket.csv', index=False)
# ---- correlation of FZ signal days with CAPIT fire days over the calendar (full window)
w0, w1 = pd.Timestamp('2023-09-11'), pd.Timestamp('2026-10-20'); days = [x for x in cal if w0 <= x <= w1]
crows = []
for s in ['fz-001', 'fz-002']:
    allfz = set().union(*[fzdays[(p, s)] for p in ['insample', 'holdout']])
    x = np.array([d in allfz for d in days], float); y = np.array([bool(fire[d]) for d in days], float)
    phi = np.corrcoef(x, y)[0, 1]; both = int((x * y).sum())
    # also any-FZ-candidate days (in_stats=0 included), already in audit; here in_stats days only
    crows.append(dict(setup=s.upper(), sessions=len(days), fz_days=int(x.sum()), capit_days=int(y.sum()), both=both, phi=phi, p_fire_given_fz=both / x.sum(), p_fz_given_fire=both / y.sum()))
    P(f'[corr {s.upper()}] sessions={len(days)} fz_days={int(x.sum())} capit_days={int(y.sum())} both={both} phi={phi:.3f} P(fire|fz)={both/x.sum():.2f} P(fz|fire)={both/y.sum():.2f}')
pd.DataFrame(crows).to_csv(f'{HERE}/out/day_correlation.csv', index=False); L.close()
