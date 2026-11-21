#!/usr/bin/env python
"""#4: FZ-001 intraday vs daily proxy + CAPIT overlap. Run with $DNA_PYEXE, cwd = this dir. See PREREG.md section 5."""
import os, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(7); B = 10000
ENG_COST = 0.0016; HOLD = 10; TP = 0.06
D = pd.read_csv(f'{HERE}/data/bq/daily_ohlc.csv', parse_dates=['time']).sort_values(['ticker', 'time'])
cap = pd.read_csv(f'{HERE}/data/bq/capit_breadth.csv', parse_dates=['time']).set_index('time')
cal = list(cap.index); pos = {d: i for i, d in enumerate(cal)}
L = open(f'{HERE}/out/daily_vs_intraday_log.txt', 'w')
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); L.write(s + '\n')
# per-symbol proxy engine
recs = []
for sym, g in D.groupby('ticker'):
    g = g.reset_index(drop=True); pc = g.Close.shift(1)
    tr = np.maximum.reduce([g.High - g.Low, (g.High - pc).abs(), (g.Low - pc).abs()])
    atr = pd.Series(tr).ewm(alpha=1 / 14, adjust=False, min_periods=14).mean(); atrp = (atr / g.Close).values
    for i in range(len(g) - 1):
        e = i + 1
        if g.time[e] != cal[pos[g.time[i]] + 1] if g.time[i] in pos and pos[g.time[i]] + 1 < len(cal) else True: continue
        ent = g.Open[e]
        if not (ent > 0) or np.isnan(atrp[i]): continue
        tp = ent * (1 + TP); sl = ent * (1 - 2 * atrp[i]); last = e + HOLD - 1
        if last >= len(g): continue
        ex = g.Close[last]; kind = 'time'; xi = last
        for j in range(e + 2, last + 1):   # sellable from T+2 (session E+2)
            if g.Low[j] <= sl: ex, kind, xi = min(sl, g.Open[j]) if g.Open[j] < sl else sl, 'sl', j; break
            if g.High[j] >= tp: ex, kind, xi = max(tp, g.Open[j]) if g.Open[j] > tp else tp, 'tp', j; break
        recs.append((sym, g.time[i], g.time[e], g.time[xi], ent, ex, kind, ex / ent - 1 - ENG_COST, g.D_RSI[i], bool(g.in_universe[i]) if pd.notna(g.in_universe[i]) else False))
A = pd.DataFrame(recs, columns=['symbol', 'D', 'entry_d', 'exit_d', 'entry', 'exit', 'kind', 'ret', 'rsi', 'inuni'])
A = A[A.inuni]
A['drift'] = A.groupby('D').ret.transform('mean')        # same-day all-universe, same exit rule
A['excess'] = A.ret - A.drift
A['brd'] = A.groupby('D').rsi.transform(lambda s: (s < 0.32).sum())
daily = A[(A.rsi < 0.32) & (A.brd >= 3)].copy()
# FZ-001 intraday candidates (engine) and in-sample window
cand = pd.read_csv(f'{HERE}/data/insample/deals_fz-001.csv', parse_dates=['signal_day'])
W0, W1 = pd.Timestamp('2023-09-11'), pd.Timestamp('2026-04-30')
daily = daily[(daily.D >= W0) & (daily.exit_d <= W1)]
key = set(zip(cand.symbol, cand.signal_day)); daily['intra'] = [(s, d) in key for s, d in zip(daily.symbol, daily.D)]
# coverage / reproducibility
c1 = cand[cand.in_stats == 1]; k1 = set(zip(c1.symbol, c1.signal_day)); inD = set(zip(daily.symbol, daily.D))
P(f'REPRO: FZ-001 candidates={len(cand)}, in daily-set: {sum((s,d) in inD for s,d in key)}; in_stats deals={len(c1)}, in daily-set: {sum((s,d) in inD for s,d in k1)}')
cov = sum((s, d) in inD for s, d in k1) / len(k1); P(f'REPRO coverage of in_stats deals = {cov:.3f} (need >= 0.80)')
m = c1.merge(daily, left_on=['symbol', 'signal_day'], right_on=['symbol', 'D'])
P(f'PROXY vs engine on {len(m)} matched deals: mean engine net_ret_total={m.net_ret_total.mean():.4f} mean proxy ret={m.ret.mean():.4f} corr={np.corrcoef(m.net_ret_total, m.ret)[0,1]:.3f}; exit-kind agreement={(m.exit_reason==m.kind).mean():.3f}')
P(f'PROXY excess vs engine excess: proxy={m.excess.mean():.4f} engine={m.excess_ret.mean():.4f} corr={np.corrcoef(m.excess_ret, m.excess)[0,1]:.3f}')
# non-overlap per symbol within each set (one open deal per symbol)
def nonover(x):
    x = x.sort_values('D'); keep = []; last = {}
    for r in x.itertuples():
        if r.symbol in last and r.D <= last[r.symbol]: continue
        keep.append(r.Index); last[r.symbol] = r.exit_d
    return x.loc[keep]
S_all = nonover(daily); S_int = nonover(daily[daily.intra]); S_oth = nonover(daily[~daily.intra])
for n, s in [('daily-all', S_all), ('intraday-subset(proxy)', S_int), ('daily-only(complement)', S_oth)]:
    P(f'{n}: deals={len(s)} signal_days={s.D.nunique()} mean_ret={s.ret.mean():.4f} mean_excess={s.excess.mean():.4f}')
# clusters E5 over the daily-all signal days
ud = sorted(S_all.D.unique()); cm = {}; c = 0; prev = None
for x in ud:
    if prev is not None and pos[x] - pos[prev] > 5: c += 1
    cm[x] = c; prev = x
for s in (S_all, S_int, S_oth): s['cl'] = s.D.map(cm)
ci = S_int.groupby('cl').excess.mean(); co = S_oth.groupby('cl').excess.mean(); ca = S_all.groupby('cl').excess.mean()
def cmp(a, b, name):
    j = pd.concat([a.rename('a'), b.rename('b')], axis=1).dropna(); dlt = (j.a - j.b).values
    bs = np.array([rng.choice(dlt, len(dlt)).mean() for _ in range(B)]); lo, hi = np.percentile(bs, [5, 95])
    P(f'{name}: clusters_paired={len(j)}  mean_a={j.a.mean():.4f} mean_b={j.b.mean():.4f}  diff={dlt.mean():.4f}  CI90=[{lo:.4f},{hi:.4f}]  PASS={bool(lo>0)}')
    return dict(name=name, clusters=len(j), mean_a=j.a.mean(), mean_b=j.b.mean(), diff=dlt.mean(), ci90_lo=lo, ci90_hi=hi, PASS=bool(lo > 0))
res = [cmp(ci, co, 'PRIMARY intraday-subset minus daily-only (cluster E5)'), cmp(ci, ca, 'secondary intraday-subset minus daily-all')]
# also on engine-actual excess for the intraday set vs proxy daily-only
act = c1.assign(cl=c1.signal_day.map(cm)).dropna(subset=['cl']).groupby('cl').excess_ret.mean()
res.append(cmp(act, co, 'secondary ENGINE-actual intraday excess minus proxy daily-only'))
pd.DataFrame(res).to_csv(f'{HERE}/out/daily_vs_intraday.csv', index=False)
# CAPIT overlap on FZ-001 signal days (insample + holdout, in_stats and all candidate days)
allc = pd.concat([pd.read_csv(f'{HERE}/data/{p}/deals_fz-001.csv', parse_dates=['signal_day']).assign(per=p) for p in ['insample', 'holdout']])
rows = []
for nm, sub in [('all candidates', allc), ('in_stats', allc[allc.in_stats == 1])]:
    days = sorted(sub.signal_day.unique()); fire = cap.oversold.reindex(days) >= 0.31
    fire5 = [(cap.oversold.iloc[max(0, pos[d] - 5):pos[d] + 1] >= 0.31).any() for d in days]
    ud = sorted(days); cl = {}; c = 0; prev = None
    for x in ud:
        if prev is not None and pos[x] - pos[prev] > 5: c += 1
        cl[x] = c; prev = x
    t = pd.DataFrame({'d': days, 'fire': fire.values, 'fire5': fire5}); t['cl'] = t.d.map(cl); cc = t.groupby('cl').agg(f=('fire', 'any'), f5=('fire5', 'any'))
    r = dict(set=nm, days=len(days), days_fire_same_D=int(t.fire.sum()), frac_days=t.fire.mean(), frac_days_5sess=t.fire5.mean(),
             clusters=len(cc), frac_clusters_same=cc.f.mean(), frac_clusters_5sess=cc.f5.mean())
    rows.append(r)
    P(r)
# base rate: share of all sessions with fire in window, for context
w = cap.loc[W0:'2026-11-06']; P(f'CAPIT fire base rate sessions {W0.date()}..2026-11-06: {(w.oversold>=0.31).mean():.3f} ({int((w.oversold>=0.31).sum())}/{len(w)}); fire dates: {[d.strftime("%Y-%m-%d") for d in w.index[w.oversold>=0.31]][:40]}')
pd.DataFrame(rows).to_csv(f'{HERE}/out/capit_overlap.csv', index=False)
L.close()
