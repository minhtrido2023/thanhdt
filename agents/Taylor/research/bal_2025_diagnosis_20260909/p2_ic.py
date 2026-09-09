import pandas as pd, numpy as np
from scipy import stats
d = pd.read_csv('p2_panel_exp.csv', parse_dates=['time'])
d = d[d.adv_vnd >= 1e9].copy()          # mirror SIGNAL_V11's liq>=1e9 gate
FEAT = ['prox52','mom12_1','mom3m','relmom12_1','residmom_scaled','trend_atr',
        'bb_pctb_centered','eff_ratio60','fip','idiovol_ann','volratio','cmf',
        'rsi','macddiff','px_ma50','pe_z','ey']
NEW  = set(FEAT[:12])
def nw_t(x, lags):
    x = np.asarray(x, float); n = len(x); m = x.mean(); e = x - m
    g0 = (e*e).sum()/n; s = g0
    for L in range(1, lags+1):
        g = (e[L:]*e[:-L]).sum()/n
        s += 2*(1 - L/(lags+1))*g
    return m/np.sqrt(s/n) if s > 0 else np.nan

def ic_series(df, f, fw):
    out = {}
    for t, g in df.groupby('time'):
        g = g[[f, fw]].dropna()
        if len(g) >= 20:
            out[t] = stats.spearmanr(g[f], g[fw]).statistic
    return pd.Series(out).sort_index()

def block(df, label, fw, lags):
    rows = []
    for f in FEAT:
        s = ic_series(df, f, fw)
        if len(s) < 6: continue
        rows.append(dict(feature=f, new=f in NEW, window=label, fwd=fw, n_months=len(s),
                         ic_mean=s.mean(), ic_med=s.median(), ic_std=s.std(),
                         t_nw=nw_t(s.values, lags), hit=(s > 0).mean()))
    return pd.DataFrame(rows), {f: ic_series(df, f, fw) for f in FEAT}

periods = {'FULL 2014-2026': (None, None), 'IS 2014-2019': ('2014-01-01','2019-12-31'),
           'OOS 2020-2026': ('2020-01-01','2026-06-19'), '2025': ('2025-01-01','2025-12-31'),
           '2026H1': ('2026-01-01','2026-06-19')}
allres = []
for fw, lags in [('profit_1M',1), ('profit_3M',3)]:
    for lab,(a,b) in periods.items():
        sub = d if a is None else d[(d.time >= a) & (d.time <= b)]
        r,_ = block(sub, lab, fw, lags)
        allres.append(r)
R = pd.concat(allres, ignore_index=True)
R.to_csv('p2_ic_results.csv', index=False)
pd.set_option('display.width', 220)
for fw in ['profit_1M','profit_3M']:
    print('\n########## forward =', fw, '##########')
    piv = R[R.fwd==fw].pivot(index='feature', columns='window', values='ic_mean')
    tpv = R[R.fwd==fw].pivot(index='feature', columns='window', values='t_nw')
    order = [c for c in ['FULL 2014-2026','IS 2014-2019','OOS 2020-2026','2025','2026H1'] if c in piv.columns]
    out = pd.concat([piv[order].round(4), tpv[order].round(2).add_suffix(' (t)')], axis=1)
    out.insert(0,'new', [f in NEW for f in out.index])
    print(out.sort_values('FULL 2014-2026').to_string())
print('\nN months FULL:', R[(R.fwd=="profit_1M")&(R.window=="FULL 2014-2026")].n_months.max())
