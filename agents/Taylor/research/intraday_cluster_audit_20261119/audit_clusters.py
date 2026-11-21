#!/usr/bin/env python
"""#1 cluster audit + #2 sensitivity + self-check. Run: $DNA_PYEXE audit_clusters.py (cwd = this dir). Output: out/*.csv, out/audit_log.txt"""
import sys, os, math, numpy as np, pandas as pd
from scipy.stats import norm, skew, kurtosis
sys.path.insert(0, '/home/trido/thanhdt/WorkingClaude')
import idle_rate_proxy as irp
HERE = os.path.dirname(os.path.abspath(__file__)); os.makedirs(f'{HERE}/out', exist_ok=True)
SETUPS = ['fz-001','fz-002','c-ceil','c-nfloor','c-nfloor3']
ADJ = 0.00134; B = 10000; rng = np.random.default_rng(7)
cal = pd.to_datetime(pd.read_csv(f'{HERE}/data/bq/capit_breadth.csv').time).reset_index(drop=True)
pos = {d: i for i, d in enumerate(cal)}
def load(per, s):
    d = pd.read_csv(f'{HERE}/data/{per}/deals_{s}.csv')
    return d
def cluster_ids(days, gap=5):
    u = sorted(pd.to_datetime(pd.Series(days).unique())); m = {}; c = 0; prev = None
    for x in u:
        if prev is not None and pos[x] - pos[prev] > gap: c += 1
        m[x] = c; prev = x
    return pd.to_datetime(pd.Series(days)).map(m).values
def prep(d):
    d = d[d.in_stats == 1].copy()
    d['sd'] = pd.to_datetime(d.signal_day)
    d['cl'] = cluster_ids(d.sd)
    d['excess_adj'] = d.excess_ret - ADJ; d['net_adj'] = d.net_ret_total - ADJ
    ed = pd.to_datetime(d.entry_ts.str[:10]); xd = pd.to_datetime(d.exit_ts.str[:10])
    d['hurdle'] = [irp.r_idle(e.date(), 'dep1m') / 100 * (x - e).days / 365 for e, x in zip(ed, xd)]
    d['abs_adj'] = d.net_adj - d.hurdle
    return d
def clv(d, col):
    g = d.groupby('cl').agg(v=(col, 'mean'), start=('sd', 'min'), n=(col, 'size')); return g
def boot_ci(v, lo=5, hi=95):
    m = np.array([rng.choice(v, len(v)).mean() for _ in range(B)]); return np.percentile(m, [lo, hi])
def dsr(v, N, T=None):
    v = np.asarray(v); T = len(v); sr = v.mean() / v.std(ddof=1)
    g = 0.5772156649; V = 1 / (T - 1)
    sr0 = math.sqrt(V) * ((1 - g) * norm.ppf(1 - 1 / N) + g * norm.ppf(1 - 1 / (N * math.e)))
    sk = skew(v); ku = kurtosis(v, fisher=False)
    den = math.sqrt(max(1e-12, 1 - sk * sr + (ku - 1) / 4 * sr ** 2))
    return sr, sr0, float(norm.cdf((sr - sr0) * math.sqrt(T - 1) / den))
def placebo(g):
    v = g.v.values; mo = g.start.dt.to_period('M').values; um = pd.unique(mo)
    idx = [np.where(mo == m)[0] for m in um]; obs = v.mean(); cnt = 0
    for _ in range(B):
        s = rng.choice([-1, 1], len(um)); w = np.empty(len(v))
        for k, ix in enumerate(idx): w[ix] = s[k] * v[ix]
        cnt += w.mean() >= obs
    return (cnt + 1) / (B + 1), len(um)
L = open(f'{HERE}/out/audit_log.txt', 'w')
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); L.write(s + '\n')
# ---------- self-check: reproduce summary.csv ----------
ok = True
for per in ['insample', 'holdout']:
    sm = pd.read_csv(f'{HERE}/data/{per}/summary.csv').set_index('setup')
    for s in SETUPS + ['c-tamix', 'c-onid']:
        d = load(per, s); d = d[d.in_stats == 1]; r = sm.loc[s.upper()]
        chk = (len(d) == r.deals_in_stats, abs(d.net_ret_total.mean() - r.mean_net_ret_total) < 1e-6,
               abs((d.net_ret_total > 0).mean() - r.win_rate) < 1e-4, abs(d.excess_ret.mean() - r.mean_excess) < 1e-6)
        ok &= all(chk)
        P(f'SELFCHECK {per} {s}: n={len(d)} mean={d.net_ret_total.mean():.5f} win={(d.net_ret_total>0).mean():.4f} -> {"OK" if all(chk) else "FAIL "+str(chk)}')
P('SELFCHECK_ALL', 'PASS' if ok else 'FAIL')
# ---------- #1 ----------
rows = []; loco_rows = []
for per in ['insample', 'holdout']:
    for s in SETUPS:
        d = prep(load(per, s)); n = len(d)
        gE = clv(d, 'excess_ret'); gA = clv(d, 'excess_adj'); gN = clv(d, 'abs_adj')
        nE = len(gE); nD = d.sd.nunique(); nW = d.sd.dt.isocalendar().week.astype(str).add(d.sd.dt.year.astype(str)).nunique()
        r = dict(period=per, setup=s.upper(), deals=n, clusters_E5=nE, signal_days=nD, iso_weeks=nW,
                 deal_mean_excess=d.excess_ret.mean(), clus_excess_raw=gE.v.mean(), clus_excess_adj=gA.v.mean(), clus_abs_adj=gN.v.mean(),
                 mean_hurdle=d.hurdle.mean())
        if nE < 15:
            r.update(verdict='KHONG DU N (<15 cum)')
        else:
            lo, hi = boot_ci(gA.v.values); r.update(ci90_lo=lo, ci90_hi=hi)
            lo2, hi2 = boot_ci(gN.v.values); r.update(abs_ci90_lo=lo2, abs_ci90_hi=hi2)
            sr, sr0, ds = dsr(gA.v.values, 1000); r.update(SR=sr, DSR_N1000=ds)
            for N in (250, 65, 30000): r[f'DSR_N{N}'] = dsr(gA.v.values, N)[2]
            p, nm = placebo(gA); r.update(placebo_p=p, n_month_blocks=nm)
            # LOCO / top5
            tot = gA.v.values; lo_m = [np.delete(tot, i).mean() for i in range(len(tot))]
            r.update(loco_min=min(lo_m), loco_max=max(lo_m), loco_sign_flip=bool(min(lo_m) <= 0 < tot.mean()))
            pos_sum = tot[tot > 0].sum(); r['top5_share_of_positive'] = np.sort(tot)[::-1][:5].sum() / pos_sum
            r['top5_share_of_total'] = np.sort(tot)[::-1][:5].sum() / tot.sum() if tot.sum() > 0 else np.nan
            r['mean_wo_top5'] = np.sort(tot)[::-1][5:].mean()
            if per == 'insample':
                ok5 = (nE >= 20, gA.v.mean() > 0, lo > 0, ds >= 0.95, p < 0.05)
                r['PASS_a_n20'], r['PASS_b_mean>0'], r['PASS_c_ci90'], r['PASS_d_dsr'], r['PASS_e_placebo'] = ok5
                r['verdict'] = 'PASS' if all(ok5) else 'FAIL'
            else: r['verdict'] = 'holdout-descriptive'
        rows.append(r)
R = pd.DataFrame(rows); R.to_csv(f'{HERE}/out/cluster_audit.csv', index=False)
pd.set_option('display.width', 250, 'display.max_columns', 60); P(R.T.to_string())
# ---------- #2 ----------
def tick(p): return np.where(p < 10000, 10, np.where(p < 50000, 50, 100))
srows = []
for per in ['insample', 'holdout']:
    for s in SETUPS + ['c-tamix', 'c-onid']:
        d = load(per, s); d = d[d.in_stats == 1].copy()
        if len(d) == 0: continue
        base = d.net_ret_total.mean()
        atc = d.entry_px >= d.close_raw_D * 1.07 - tick(d.close_raw_D * 1.07)   # near-ceiling entry
        gap5 = d.entry_px / d.close_raw_D - 1 >= 0.05
        ex = d.crosses_exdate.astype(bool)
        v = {'S1_drop_entry_at_ceiling': d[~atc].net_ret_total.mean(), 'S1b_drop_gap>=5%': d[~gap5].net_ret_total.mean(),
             'S2_drop_crosses_exdate': d[~ex].net_ret_total.mean(), 'S2c_net_ret_cash_all': d.net_ret_cash.mean(),
             'S3_fee_0.097': base - ADJ, 'S4_S1b+S2+S3': d[~gap5 & ~ex].net_ret_total.mean() - ADJ}
        r = dict(period=per, setup=s.upper(), n=len(d), base_mean=base, n_at_ceiling=int(atc.sum()), n_gap5=int(gap5.sum()), n_exdate=int(ex.sum()),
                 n_S4=int((~gap5 & ~ex).sum()))
        for k, x in v.items():
            r[k] = x; r[k + '_chg%'] = (x / base - 1) * 100 if base else np.nan
            r[k + '_PASS'] = bool(abs(x - base) < 0.25 * abs(base) and np.sign(x) == np.sign(base))
        srows.append(r)
S = pd.DataFrame(srows); S.to_csv(f'{HERE}/out/sensitivity.csv', index=False); P(S.T.to_string())
sk = []
for per in ['insample', 'holdout']:
    k = pd.read_csv(f'{HERE}/data/{per}/book3_skipped_1bn.csv'); k['period'] = per
    sk.append(k.groupby(['period', 'setup', 'reason']).size().rename('n').reset_index())
    k2 = k[k.in_stats == 1] if 'in_stats' in k else k
SK = pd.concat(sk); SK.to_csv(f'{HERE}/out/skipped_reasons.csv', index=False); P(SK.pivot_table(index=['period','setup'], columns='reason', values='n', fill_value=0).to_string())
L.close()
