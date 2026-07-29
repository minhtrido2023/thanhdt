"""Kiem tra chat che hon cho GO/NO-GO:
 (1) dong nhat thuc tren universe NHAT QUAN (khong phai panel cu bi lech universe)
 (2) co mau THAT: quan sat KHONG chong lap (1 diem/nam)
 (3) ROE co them gi ngoai PB khong (vi ROE = PB/PE dong nhat thuc)
 (4) mean-reversion co song sot khi khu xu the thu ky / doi sang giai doan 2014+ khong
"""
import pandas as pd, numpy as np
from scipy import stats

EXP = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_roe/'
pd.set_option('display.width', 260)
df = pd.read_csv(EXP + 'panel_roe_fwd.csv', parse_dates=['time'])
d = pd.read_csv(EXP + 'roe_daily_enriched.csv', parse_dates=['time'])[['time', 'pe_agg', 'pb_agg', 'roe_agg', 'n']]
df = df.drop(columns=['roe_agg']).merge(d, on='time', how='left')

print('=== (1) DONG NHAT THUC tren universe NHAT QUAN (cung bo ma cho ca PE, PB, ROE) ===')
s = df.dropna(subset=['pe_agg', 'pb_agg', 'roe_agg'])
print('  max |ROE_agg - PB_agg/PE_agg| = %.3e  (N=%d)' % ((s.roe_agg - s.pb_agg / s.pe_agg).abs().max(), len(s)))
X = np.column_stack([np.ones(len(s)), np.log(s.pe_agg), np.log(s.pb_agg)])
y = np.log(s.roe_agg)
b, *_ = np.linalg.lstsq(X, y, rcond=None)
r2 = 1 - ((y - X @ b) ** 2).sum() / ((y - y.mean()) ** 2).sum()
print('  hoi quy log(ROE) ~ log(PE)+log(PB): R^2 = %.8f  beta = [%.4f, %.4f, %.4f]  (ky vong 1.0 / [0,-1,+1])' % (r2, *b))
print('  => ROE thi truong KHONG phai bien moc doc lap: no LA hieu log(PB)-log(PE).')

# PIT percentile tren universe nhat quan
def pit_expand(x, minp=500):
    return x.expanding(minp).apply(lambda v: (v.iloc[:-1] < v.iloc[-1]).mean(), raw=False)
def pit_roll(x, w=756):
    return x.rolling(w, min_periods=w).apply(lambda v: (v[:-1] < v[-1]).mean(), raw=True)
for c in ['pe_agg', 'pb_agg', 'roe_agg']:
    df[c + '_pex'] = pit_expand(df[c]); df[c + '_p3y'] = pit_roll(df[c])
cur = df.dropna(subset=['roe_agg']).iloc[-1]
print('  hien tai: PE=%.2f(pex %.0f / p3y %.0f)  PB=%.3f(pex %.0f / p3y %.0f)  ROE=%.2f%%(pex %.0f / p3y %.0f)' % (
    cur.pe_agg, 100 * cur.pe_agg_pex, 100 * cur.pe_agg_p3y, cur.pb_agg, 100 * cur.pb_agg_pex, 100 * cur.pb_agg_p3y,
    100 * cur.roe_agg, 100 * cur.roe_agg_pex, 100 * cur.roe_agg_p3y))

# ---------- (2) co mau THAT: 1 quan sat / nam (khong chong lap) ----------
print('\n=== (2) QUAN SAT KHONG CHONG LAP — 1 diem cuoi thang 7 moi nam (fwd 12M khong de len nhau) ===')
df['ym'] = df.time.dt.strftime('%Y-%m')
ann = df[df.ym.str.endswith('-07')].groupby(df.time.dt.year).tail(1)
ann = ann.dropna(subset=['fwd_12M', 'roe_agg_pex', 'pb_agg_pex', 'pe_agg_pex'])
print('  N nam doc lap = %d (%s..%s)' % (len(ann), ann.time.min().date(), ann.time.max().date()))
out = []
for c in ['pe_agg_pex', 'pb_agg_pex', 'roe_agg_pex', 'roe_agg_p3y', 'pb_agg_p3y', 'pe_agg_p3y']:
    a = ann.dropna(subset=[c])
    if len(a) < 8: continue
    rho, pv = stats.spearmanr(a[c], a.fwd_12M)
    rho2, pv2 = stats.spearmanr(a[c], a.minfwd_12M)
    out.append(dict(signal=c, N=len(a), rho_fwd12M=round(rho, 3), p_fwd12M=round(pv, 3),
                    rho_minfwd12M=round(rho2, 3), p_minfwd=round(pv2, 3)))
A = pd.DataFrame(out); print(A.to_string(index=False))
print('  (voi N~14-16 nam, |rho| can >~0.50 moi dat p<0.05 — doc cot p, dung doc cot rho)')
A.to_csv(EXP + 'annual_rank_test.csv', index=False)

# ---------- (3) ROE co them gi ngoai PB? ----------
print('\n=== (3) ROE vs PB — head-to-head + hoi quy 2 bien tren mau khong chong lap ===')
a = ann.dropna(subset=['pb_agg_pex', 'pe_agg_pex', 'roe_agg_pex'])
def ols_r2(cols):
    Xm = np.column_stack([np.ones(len(a))] + [a[c].values for c in cols])
    yv = a.fwd_12M.values
    bb, *_ = np.linalg.lstsq(Xm, yv, rcond=None)
    return 1 - ((yv - Xm @ bb) ** 2).sum() / ((yv - yv.mean()) ** 2).sum()
for cols in [['pe_agg_pex'], ['pb_agg_pex'], ['roe_agg_pex'], ['pe_agg_pex', 'pb_agg_pex'],
             ['pe_agg_pex', 'pb_agg_pex', 'roe_agg_pex']]:
    print('  R^2(fwd12M ~ %-45s) = %.3f   [N=%d]' % ('+'.join(cols), ols_r2(cols), len(a)))
print('  => them ROE vao {PE,PB} khong the tang R^2: cong tuyen hoan hao (ROE la ham cua 2 bien kia).')

# ---------- (4) mean reversion co that hay chi la xu the thu ky ----------
print('\n=== (4) MEAN REVERSION cua ROE — khu xu the & kiem tra giai doan con ===')
df['roe_ma5y'] = df.roe_agg.rolling(1260, min_periods=756).mean()
df['roe_gap'] = df.roe_agg - df.roe_ma5y          # do lech CUC BO, khong bi xu the dai han chi phoi
for H in [252, 504]:
    df['droe_%d' % H] = df.roe_agg.shift(-H) - df.roe_agg
for lab, m in [('toan bo 2010+', df.time >= '2010-01-01'), ('2014+', df.time >= '2014-01-01'),
               ('2018+', df.time >= '2018-01-01')]:
    for H in [252, 504]:
        s2 = df[m][['roe_gap', 'droe_%d' % H]].dropna()
        if len(s2) < 200: continue
        rho, pv = stats.spearmanr(s2.roe_gap, s2['droe_%d' % H])
        # co mau khong chong lap: 1 diem/nam
        an = df[m].dropna(subset=['roe_gap', 'droe_%d' % H])
        an = an[an.ym.str.endswith('-07')].groupby(an.time.dt.year).tail(1)
        rho_a, pv_a = (stats.spearmanr(an.roe_gap, an['droe_%d' % H]) if len(an) >= 8 else (np.nan, np.nan))
        print('  %-14s H=%3d: rho(ngay)=%+.3f N=%4d | rho(1diem/nam)=%+.3f p=%.3f N=%d' % (
            lab, H, rho, len(s2), rho_a, pv_a, len(an)))
print('  roe_gap hien tai = %+.2fpp (ROE %.2f%% vs TB truot 5 nam %.2f%%)' % (
    100 * cur.roe_agg - 100 * df.roe_ma5y.iloc[-1], 100 * cur.roe_agg, 100 * df.roe_ma5y.iloc[-1]))

# ---------- (5) dinh gia chuan hoa chu ky ----------
print('\n=== (5) DINH GIA CHUAN HOA THEO CHU KY LOI NHUAN ===')
for lab, yrs in [('TB 5 nam', 5), ('TB 10 nam', 10), ('TB toan bo 2008+', None)]:
    base = df.roe_agg.mean() if yrs is None else df[df.time >= cur.time - pd.DateOffset(years=yrs)].roe_agg.mean()
    pe_n = cur.pe_agg * cur.roe_agg / base
    print('  ROE chuan %-16s = %.2f%%  =>  PE chuan hoa = %.2f  (PE quan sat %.2f, chenh %+.1f%%)' % (
        lab, 100 * base, pe_n, cur.pe_agg, 100 * (pe_n / cur.pe_agg - 1)))
print('  Luu y: PE chuan hoa = PB / ROE_chuan => chinh la PB doi don vi. PB pctile (pex/p3y) = %.0f / %.0f.' % (
    100 * cur.pb_agg_pex, 100 * cur.pb_agg_p3y))
df.to_csv(EXP + 'panel_roe_fwd2.csv', index=False)
