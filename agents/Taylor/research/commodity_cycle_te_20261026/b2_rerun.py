"""B2 rerun — xử 3 điểm quant-skeptic cho B2 (job Taylor_20261026_095928), KHÔNG đè file B2 cũ.
(i)  CI moving-block bootstrap (khối 4 quý liền, vòng) + permutation MỘT dịch chuyển chung cho mọi họ (exhaustive)
     cho IC pooled c_yoy→rev_yoy / np_d (đơn vị họ×quý, b2_famq.csv tier A).
(ii) split 2020 song song split 2023.
(iii) restatement: ticker_financial có dòng trùng không; snapshot cũ data/bq_cache_asof* so với cache hiện tại;
     độ lệch NP_P0(q) vs NP_P1(q+1) vs NP_P4(q+4) trong cùng bảng.
(iv) mô tả cho PREREG-4: SUE live (surprise_B_MA) ~ c_ma, expanding PIT theo Release_Date; phân tán ΔIC theo mùa ⇒ MDE.
Đầu ra: b2_rerun.json. Seed 20261027."""
import json, os, pickle, sys
import numpy as np, pandas as pd
from scipy.stats import spearmanr
from common import te, cmap, W

rng = np.random.default_rng(20261027)
OUT = {}
G = pd.read_csv('b2_famq.csv'); A = G[G.tier == 'A'].copy()
QS = sorted(A.quarter.unique())                      # lịch quý chung 2017Q4..2026Q3


def ranks(df, x, y):
    d = df.dropna(subset=[x, y]).copy()
    d['rx'] = d.groupby('family')[x].rank(pct=True) - .5
    d['ry'] = d.groupby('family')[y].rank(pct=True) - .5
    return d


def ic(d):
    return float(np.corrcoef(d.rx, d.ry)[0, 1])


def block_boot(d, B=5000, L=4, qs=None):
    qs = qs or sorted(d.quarter.unique()); n = len(qs); byq = {q: d[d.quarter == q] for q in qs}
    k = int(np.ceil(n / L)); bs = []
    for _ in range(B):
        st = rng.integers(0, n, k); idx = [(s + j) % n for s in st for j in range(L)][:n]
        s = pd.concat([byq[qs[i]] for i in idx]); bs.append(np.corrcoef(s.rx, s.ry)[0, 1])
    return [round(float(np.percentile(bs, 5)), 3), round(float(np.percentile(bs, 95)), 3)], float(np.std(bs))


def common_shift_p(d, min_k=1):
    """Dịch c (rx) của MỌI họ cùng k quý trên lịch chung (vòng) — giữ tương quan chéo họ cùng quý. Exhaustive k."""
    qs = sorted(d.quarter.unique()); n = len(qs)
    X = d.pivot(index='quarter', columns='family', values='rx').reindex(qs)
    Y = d.pivot(index='quarter', columns='family', values='ry').reindex(qs)
    est = ic(d); null = []
    for k in range(min_k, n - min_k + 1):
        Xs = pd.DataFrame(np.roll(X.values, k, axis=0), index=qs, columns=X.columns)
        m = Xs.notna().values & Y.notna().values
        null.append(np.corrcoef(Xs.values[m], Y.values[m])[0, 1])
    null = np.array(null)
    return round(float((np.sum(np.abs(null) >= abs(est)) + 1) / (len(null) + 1)), 4), len(null)


res = []
for y in ['rev_yoy', 'np_d', 'post60']:
    for lab, sub in [('ALL', A), ('pre2020', A[A.quarter < '2020Q1']), ('2020+', A[A.quarter >= '2020Q1']),
                     ('pre2023', A[A.quarter < '2023Q1']), ('2023+', A[A.quarter >= '2023Q1'])]:
        d = ranks(sub, 'c_yoy', y)
        ci, sd = block_boot(d)
        p1, n1 = common_shift_p(d, 1); p4, n4 = common_shift_p(d, 4)
        r = dict(y=y, split=lab, ic=round(ic(d), 3), ci90_block4=ci, n_famq=len(d), n_quarters=d.quarter.nunique(),
                 n_fam=d.family.nunique(), p_common_shift_all=p1, n_shifts_all=n1, p_common_shift_k4=p4, n_shifts_k4=n4)
        res.append(r); print(r)
OUT['i_ii_pooled_ic'] = res

# ---------- (iii) restatement ----------
TF = f'{W}/data/bq_cache/ticker_financial.parquet'
cols = ['ticker', 'quarter', 'Release_Date', 'NP_P0', 'NP_P1', 'NP_P4', 'Revenue_P0']
cur = pd.read_parquet(TF, columns=cols)
r3 = dict(cur_rows=len(cur), cur_dup_ticker_quarter=int(cur.duplicated(['ticker', 'quarter']).sum()))
tierA = set(cmap(('A',)).ticker)


def diff_rate(a, b, col, tol=0.005):
    m = a.merge(b, on=['ticker', 'quarter'], suffixes=('_o', '_n')).dropna(subset=[col + '_o', col + '_n'])
    m = m[m[col + '_o'].abs() > 0]
    ch = (m[col + '_n'] - m[col + '_o']).abs() / m[col + '_o'].abs() > tol
    return len(m), int(ch.sum()), m[ch]


snaps = {}
for p in ['bq_cache_asof20260728/ticker_financial.parquet.GOOD_pre_corruption_20260708snap',
          'bq_cache_asof20260728/ticker_financial.parquet', 'bq_cache_asof20260729_postrestate/ticker_financial.parquet']:
    o = pd.read_parquet(f'{W}/data/{p}', columns=cols)
    o = o[o.quarter <= '2026Q1']                         # chỉ quý đã chốt trước snapshot sớm nhất
    rr = {}
    for col in ['NP_P0', 'Revenue_P0', 'NP_P4']:
        n, k, ex = diff_rate(o, cur, col)
        nA, kA, _ = diff_rate(o[o.ticker.isin(tierA)], cur[cur.ticker.isin(tierA)], col)
        rr[col] = dict(n=n, changed_gt0p5pct=k, rate=round(k / max(n, 1), 4), tierA_n=nA, tierA_changed=kA,
                       tierA_rate=round(kA / max(nA, 1), 4))
        if col == 'NP_P0':
            rr['NP_P0_changed_by_year'] = ex.quarter.str[:4].value_counts().sort_index().to_dict()
    m = o.merge(cur, on=['ticker', 'quarter'], suffixes=('_o', '_n')).dropna(subset=['Release_Date_o', 'Release_Date_n'])
    rr['Release_Date_changed'] = int((pd.to_datetime(m.Release_Date_o) != pd.to_datetime(m.Release_Date_n)).sum())
    rr['n_rows_snapshot'] = len(o)
    snaps[p] = rr; print(p, rr)
r3['snapshot_vs_current_20261023'] = snaps
# trong cùng bảng: NP_P0 của quý q so NP_P1 của q+1 và NP_P4 của q+4 (số so sánh trong BCTC sau)
c = cur.copy(); c['per'] = pd.PeriodIndex(c.quarter, freq='Q')
for lag, col in [(1, 'NP_P1'), (4, 'NP_P4')]:
    nx = c[['ticker', 'per', col]].copy(); nx['per'] = nx.per - lag
    m = c[['ticker', 'per', 'NP_P0']].merge(nx, on=['ticker', 'per']).dropna()
    m = m[(m.NP_P0.abs() > 1e8)]
    ch = (m[col] - m.NP_P0).abs() / m.NP_P0.abs() > 0.005
    mA = m[m.ticker.isin(tierA)]; chA = (mA[col] - mA.NP_P0).abs() / mA.NP_P0.abs() > 0.005
    r3[f'NP_P0_q_vs_{col}_q+{lag}'] = dict(n=len(m), differ_gt0p5pct=int(ch.sum()), rate=round(ch.mean(), 4),
                                         tierA_n=len(mA), tierA_rate=round(chA.mean(), 4),
                                         rate_2020plus=round(ch[m.per >= pd.Period('2020Q1', 'Q')].mean(), 4))
pk = pickle.load(open(f'{W}/data/earnings_surprise_data.pkl', 'rb'))
r3['pkl_rows'] = len(pk); r3['pkl_dup_ticker_quarter'] = int(pk.duplicated(['ticker', 'quarter']).sum())
OUT['iii_restatement'] = r3; print(r3)

# ---------- (iv) SUE live ~ c_ma, mô tả cho PREREG-4 ----------
T = te(); qa = T.resample('QE').mean().where(T.resample('QE').count() >= 40)
M = cmap(('A',))
P = pd.read_csv('b2_panel.csv', parse_dates=['qend', 'release']); P = P[P.tier == 'A']
fin = cur.merge(pd.read_parquet(TF, columns=['ticker', 'quarter', 'NP_P2', 'NP_P3']), on=['ticker', 'quarter'])
fin['exp'] = fin[['NP_P1', 'NP_P2', 'NP_P3', 'NP_P4']].mean(axis=1)
fin['sue'] = ((fin.NP_P0 - fin.exp) / np.maximum(fin.exp.abs(), 1e9)).clip(-5, 5)   # = lag_live_schedule.surprise_B_MA
P = P.merge(fin[['ticker', 'quarter', 'sue']], on=['ticker', 'quarter'], how='left')
cma = {}
for _, m in M.drop_duplicates('family').iterrows():
    s = qa[m.te_metric_key]; cma[m.family] = np.log(s / s.shift(1).rolling(4).mean()) * m.sign
P['c_ma'] = [cma[f].get(q, np.nan) for f, q in zip(P.family, P.qend)]
P = P.dropna(subset=['sue', 'c_ma']).sort_values('release').reset_index(drop=True)
hat = np.full(len(P), np.nan)
for i, r in P.iterrows():                                   # expanding, CHỈ sự kiện cùng họ công bố TRƯỚC ngày này
    past = P[(P.family == r.family) & (P.release < r.release)]
    if len(past) >= 8 and past.quarter.nunique() >= 6:
        b = np.polyfit(past.c_ma, past.sue, 1); hat[i] = np.polyval(b, r.c_ma)
P['sue_hat'] = hat; P['sue_res'] = P.sue - P.sue_hat
E = P.dropna(subset=['sue_hat', 'post60']).copy()
iv = dict(n_events=len(E), n_quarters=int(E.quarter.nunique()),
          ic_cma_sue_famq=round(spearmanr(*E.groupby(['family', 'quarter'])[['c_ma', 'sue']].median().values.T)[0], 3),
          ic_hat_sue_event=round(spearmanr(E.sue_hat, E.sue)[0], 3))
seas = []
for q, g in E.groupby('quarter'):
    if len(g) < 6 or g.family.nunique() < 3: continue
    a, b = spearmanr(g.sue_res, g.post60)[0], spearmanr(g.sue, g.post60)[0]
    seas.append(dict(quarter=q, n=len(g), nfam=g.family.nunique(), ic_res=a, ic_raw=b, d=a - b))
S = pd.DataFrame(seas)
sd = float(S.d.std(ddof=1)); mu = float(S.d.mean())
iv.update(n_seasons=len(S), mean_dIC=round(mu, 4), sd_dIC=round(sd, 4), mean_ic_res=round(S.ic_res.mean(), 4),
          mean_ic_raw=round(S.ic_raw.mean(), 4), frac_d_pos=round((S.d > 0).mean(), 3),
          median_events_per_season=float(S.n.median()),
          mean_dIC_pre2023=round(S[S.quarter < '2023Q1'].d.mean(), 4), mean_dIC_2023plus=round(S[S.quarter >= '2023Q1'].d.mean(), 4),
          ac1_dIC=round(float(S.d.autocorr(1)), 3))
z = 1.645 + 0.8416                                          # một phía α=0,05, power 80%
iv['seasons_needed_to_detect_hist_mean'] = int(np.ceil((z * sd / mu) ** 2)) if mu > 0 else None
iv['mde_dIC_2_seasons'] = round(z * sd / np.sqrt(2), 3)
iv['mde_dIC_4_seasons'] = round(z * sd / np.sqrt(4), 3)
iv['mde_dIC_8_seasons'] = round(z * sd / np.sqrt(8), 3)
iv['mde_dIC_16_seasons'] = round(z * sd / np.sqrt(16), 3)
# LAG qualify trong tier A (lịch sử)
sys.path.insert(0, W)
from lag_live_schedule import live_lag_candidates
L = live_lag_candidates()
LA = L[L.ticker.isin(tierA)]
iv['lag_qualify_tierA_events'] = int(LA.qualify.sum()); iv['lag_qualify_all_events'] = int(L.qualify.sum())
iv['lag_qualify_tierA_per_year'] = LA[LA.qualify].Release_Date.dt.year.value_counts().sort_index().to_dict()
OUT['iv_sue_decomp_descriptive'] = iv; print(iv)
S.to_csv('b2_rerun_seasons.csv', index=False)
json.dump(OUT, open('b2_rerun.json', 'w'), indent=1, default=str)

# ---------- (v) B2 decomp (np_d, c_yoy) — SE theo moving-block bootstrap 4 quý + ΔIC theo mùa ----------
D = pd.read_csv('b2_panel.csv'); D = D[D.tier == 'A'].dropna(subset=['c_yoy', 'np_d', 'ann']).copy()
D['release'] = pd.to_datetime(D.release); D = D.sort_values('release').reset_index(drop=True)
h2 = np.full(len(D), np.nan)
for i, r in D.iterrows():                                   # expanding theo Release_Date (chặt hơn b2_decomp: quarter<q)
    past = D[(D.family == r.family) & (D.release < r.release)]
    if past.quarter.nunique() >= 6:
        h2[i] = np.polyval(np.polyfit(past.c_yoy, past.np_d, 1), r.c_yoy)
D['np_hat'] = h2; D = D.dropna(subset=['np_hat']); D['np_res'] = D.np_d - D.np_hat


def reg_block(df, y, xs, B=3000, L=4):
    Z = df.dropna(subset=[y]).copy()
    for c_ in xs + [y]: Z[c_] = Z.groupby('family')[c_].transform(lambda s: s.rank(pct=True) - .5)
    X = np.c_[np.ones(len(Z)), Z[xs].values]; beta = np.linalg.lstsq(X, Z[y].values, rcond=None)[0]
    qs = sorted(Z.quarter.unique()); n = len(qs); byq = {q: Z[Z.quarter == q] for q in qs}; k = int(np.ceil(n / L)); bs = []
    for _ in range(B):
        st = rng.integers(0, n, k); idx = [(s + j) % n for s in st for j in range(L)][:n]
        s = pd.concat([byq[qs[i]] for i in idx]); bs.append(np.linalg.lstsq(np.c_[np.ones(len(s)), s[xs].values], s[y].values, rcond=None)[0])
    bs = np.array(bs)
    return {x: dict(b=round(beta[j + 1], 3), t_block4=round(beta[j + 1] / bs[:, j + 1].std(), 2),
                    ci90=[round(np.percentile(bs[:, j + 1], 5), 3), round(np.percentile(bs[:, j + 1], 95), 3)])
            for j, x in enumerate(xs)} | dict(n=len(Z), nq=n)


v = {}
for y in ['ann', 'post60']:
    for lab, sub in [('ALL', D), ('pre2020', D[D.quarter < '2020Q1']), ('2020+', D[D.quarter >= '2020Q1']),
                     ('pre2023', D[D.quarter < '2023Q1']), ('2023+', D[D.quarter >= '2023Q1'])]:
        if sub.quarter.nunique() < 8: continue   # pre2020 chỉ 4 quý có np_hat ⇒ block-4 suy biến, bỏ
        v[f'{y}|{lab}|hat+res'] = reg_block(sub, y, ['np_hat', 'np_res']); v[f'{y}|{lab}|raw'] = reg_block(sub, y, ['np_d'])
        print(y, lab, v[f'{y}|{lab}|hat+res'], v[f'{y}|{lab}|raw'])
s2 = []
for q, g in D.dropna(subset=['post60']).groupby('quarter'):
    if len(g) < 6 or g.family.nunique() < 3: continue
    a, b = spearmanr(g.np_res, g.post60)[0], spearmanr(g.np_d, g.post60)[0]; s2.append(dict(quarter=q, n=len(g), d=a - b, ic_res=a, ic_raw=b))
S2 = pd.DataFrame(s2)
v['season_dIC_npd'] = dict(n_seasons=len(S2), mean_dIC=round(S2.d.mean(), 4), sd_dIC=round(S2.d.std(ddof=1), 4),
                           mean_ic_res=round(S2.ic_res.mean(), 4), mean_ic_raw=round(S2.ic_raw.mean(), 4), frac_pos=round((S2.d > 0).mean(), 3),
                           pre2023=round(S2[S2.quarter < '2023Q1'].d.mean(), 4), y2023plus=round(S2[S2.quarter >= '2023Q1'].d.mean(), 4))
print(v['season_dIC_npd'])
OUT['v_b2_decomp_block'] = v
json.dump(OUT, open('b2_rerun.json', 'w'), indent=1, default=str)
