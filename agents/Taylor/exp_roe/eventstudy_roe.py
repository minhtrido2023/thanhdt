"""GO/NO-GO: ROE-cycle-level co dang lam chi bao BO SUNG cho market-state khong?
Tai su dung panel forward-return da co o exp_market_prob/panel_fwd.csv.
"""
import pandas as pd, numpy as np
from scipy import stats

EXP = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_roe/'
OLD = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_market_prob/'
pd.set_option('display.width', 260)

p = pd.read_csv(OLD + 'panel_fwd.csv', parse_dates=['time'])
r = pd.read_csv(EXP + 'roe_daily_enriched.csv', parse_dates=['time'])[['time', 'roe_agg', 'roe_median', 'n']]
t100 = pd.read_csv(EXP + 'roe_t100_daily.csv', parse_dates=['time'])[['time', 'roe_t100']]
df = p.merge(r, on='time', how='left').merge(t100, on='time', how='left').reset_index(drop=True)
c = df.vni_close
df['ma200'] = c.rolling(200, min_periods=200).mean()
df['below200'] = c < df.ma200
df['dd52w'] = c / c.rolling(252, min_periods=100).max() - 1

# ---------- percentile point-in-time (khong nhin truoc) ----------
def pit_expand(s, minp=500):
    return s.expanding(minp).apply(lambda x: (x.iloc[:-1] < x.iloc[-1]).mean(), raw=False)

def pit_roll(s, w=756):
    return s.rolling(w, min_periods=w).apply(lambda x: (x[:-1] < x[-1]).mean(), raw=True)

for col in ['pe_con', 'pb_con', 'roe_agg', 'roe_t100', 'roe_median']:
    df[col + '_pex'] = pit_expand(df[col])
    df[col + '_p3y'] = pit_roll(df[col])

cur = df.dropna(subset=['roe_agg']).iloc[-1]
print('=== TRANG THAI HIEN TAI (%s) ===' % cur.time.date())
for col in ['pe_con', 'pb_con', 'roe_agg', 'roe_t100']:
    print('  %-9s = %8.4f   PIT-pctile mo rong = %5.1f   PIT-pctile 3Y = %5.1f' % (
        col, cur[col], 100 * cur[col + '_pex'], 100 * cur[col + '_p3y']))

# ---------- 1. DA CONG TUYEN: ROE co la thong tin MOI ngoai PE/PB khong ----------
print('\n=== 1. DONG NHAT THUC + DA CONG TUYEN ===')
print('max |ROE_agg - PB_agg/PE_agg| tren toan lich su = %.3e' % (df.roe_agg - df.pb_con / df.pe_con).abs().max())
sub = df.dropna(subset=['pe_con_pex', 'pb_con_pex', 'roe_agg_pex'])
print('N=%d' % len(sub))
for a, b in [('roe_agg_pex', 'pe_con_pex'), ('roe_agg_pex', 'pb_con_pex'),
             ('roe_agg_p3y', 'pe_con_p3y'), ('roe_agg_p3y', 'pb_con_p3y'),
             ('pe_con_pex', 'pb_con_pex')]:
    s2 = df[[a, b]].dropna()
    print('  corr(%s , %s): pearson=%+.3f  spearman=%+.3f  N=%d' % (
        a, b, s2[a].corr(s2[b]), s2[a].corr(s2[b], method='spearman'), len(s2)))
# R^2 cua log ROE tren log PE + log PB (phai = 1 theo dinh nghia)
s3 = df.dropna(subset=['pe_con', 'pb_con', 'roe_agg'])
X = np.column_stack([np.ones(len(s3)), np.log(s3.pe_con), np.log(s3.pb_con)])
y = np.log(s3.roe_agg)
beta, *_ = np.linalg.lstsq(X, y, rcond=None)
r2 = 1 - ((y - X @ beta) ** 2).sum() / ((y - y.mean()) ** 2).sum()
print('  hoi quy log(ROE_agg) ~ log(PE)+log(PB):  R^2 = %.6f   beta=[%.3f, %.3f, %.3f]' % (r2, *beta))

# ---------- 2. Suc du bao doc lap: IC voi forward return ----------
print('\n=== 2. IC (Spearman) voi forward return va voi min-drawdown ===')
rows = []
for col in ['pe_con_pex', 'pb_con_pex', 'roe_agg_pex', 'roe_t100_pex', 'roe_agg_p3y', 'roe_t100_p3y']:
    row = {'signal': col}
    for tgt in ['fwd_3M', 'fwd_6M', 'fwd_12M', 'minfwd_12M']:
        s2 = df[[col, tgt]].dropna()
        ic = stats.spearmanr(s2[col], s2[tgt]).statistic if len(s2) > 50 else np.nan
        row['IC_' + tgt] = round(ic, 3)
        row['N_' + tgt] = len(s2)
    rows.append(row)
IC = pd.DataFrame(rows)
print(IC.to_string(index=False))
print('(dau ky vong neu ROE cao = xau: IC am voi fwd_return, IC am voi minfwd -> dd sau hon)')
print('LUU Y: N = so NGAY chong lap; IC nay KHONG co y nghia thong ke truc tiep, chi de xem DAU va DO LON.')

# ---------- 3. Base rate co dieu kien theo ROE percentile ----------
def ep_ids(mask, gap=21):
    idx = np.array(df[mask].index)
    if len(idx) == 0: return idx, np.array([])
    br = np.concatenate([[0], np.cumsum(np.diff(idx) > gap)])
    return idx, br

def boot(mask, B=4000, seed=11):
    idx, br = ep_ids(mask)
    s = df.loc[idx, 'minfwd_12M']; ok = s.notna().values
    br = br[ok]; v = s[ok].values
    if len(v) == 0: return (np.nan, np.nan), 0
    eps = np.unique(br); rng = np.random.default_rng(seed); o = []
    for _ in range(B):
        pick = rng.choice(eps, size=len(eps), replace=True)
        o.append((np.concatenate([v[br == e] for e in pick]) <= -0.20).mean())
    return np.percentile(o, [5, 95]), len(eps)

def report(name, mask):
    s = df[mask]['minfwd_12M'].dropna()
    if len(s) < 30: return None
    ci, ne = boot(mask)
    return dict(cond=name, N_days=len(s), N_eps=ne,
                P_bear20=round(100 * (s <= -0.20).mean(), 0), CI90='[%.0f,%.0f]' % (100 * ci[0], 100 * ci[1]),
                P_benign=round(100 * (s > -0.10).mean(), 0),
                med_fwd6M=round(100 * df[mask].fwd_6M.median(), 1),
                med_fwd12M=round(100 * df[mask].fwd_12M.median(), 1),
                neg12M=round(100 * (df[mask].fwd_12M < 0).mean(), 0),
                years=','.join(sorted(set(df[mask].time.dt.year.astype(str)))))

rows = [report('UNCOND 2008+', df.time >= '2008-01-01'),
        report('UNCOND (co du PIT pctile)', df.roe_agg_pex.notna())]
for col, lab in [('roe_agg_pex', 'ROE_gop pctile mo rong'), ('roe_t100_pex', 'ROE_t100 pctile mo rong'),
                 ('roe_agg_p3y', 'ROE_gop pctile 3Y')]:
    for lo, hi, tag in [(0.0, 0.2, 'Q1 thap nhat'), (0.2, 0.8, 'giua'), (0.8, 1.01, 'Q5 CAO NHAT'),
                        (0.9, 1.01, '>=p90 RAT CAO')]:
        rows.append(report('%s %s [%.0f-%.0f]' % (lab, tag, 100 * lo, 100 * hi), df[col].between(lo, hi, inclusive='left')))
R = pd.DataFrame([x for x in rows if x])
print('\n=== 3. BASE RATE CO DIEU KIEN THEO ROE PERCENTILE (bear = co luc <= -20%% trong 252 phien) ===')
print(R.to_string(index=False))
R.to_csv(EXP + 'baserate_roe.csv', index=False)

# ---------- 4. ROE co them gi TRONG dai PE hien tai khong? ----------
PE = cur.pe_con
band = df.pe_con.between(PE - 0.75, PE + 0.75)
print('\n=== 4. TEST BIEN: TRONG dai PE %.2f+-0.75, chia doi theo ROE ===' % PE)
rows = []
rows.append(report('dai PE (tat ca)', band))
med_roe = df[band].roe_agg.median()
rows.append(report('dai PE & ROE > trung vi dai (%.2f%%)' % (100 * med_roe), band & (df.roe_agg > med_roe)))
rows.append(report('dai PE & ROE <= trung vi dai', band & (df.roe_agg <= med_roe)))
rows.append(report('dai PE & ROE pctile3Y>=0.8', band & (df.roe_agg_p3y >= 0.8)))
R4 = pd.DataFrame([x for x in rows if x]); print(R4.to_string(index=False))
R4.to_csv(EXP + 'baserate_roe_marginal.csv', index=False)

# ---------- 5. ROE cao co MEAN-REVERT khong (co so cho 'PE chuan hoa') ----------
print('\n=== 5. MEAN REVERSION cua ROE: ROE_t+H - ROE_t theo pctile hien tai ===')
for H in [126, 252, 504]:
    df['droe_%d' % H] = df.roe_agg.shift(-H) - df.roe_agg
for col in ['roe_agg_pex', 'roe_agg_p3y']:
    for H in [126, 252, 504]:
        s2 = df[[col, 'droe_%d' % H]].dropna()
        ic = stats.spearmanr(s2[col], s2['droe_%d' % H]).statistic
        hi = s2[s2[col] >= 0.8]['droe_%d' % H]
        lo = s2[s2[col] <= 0.2]['droe_%d' % H]
        print('  %-13s H=%3dphien: spearman=%+.3f | dROE khi pctile>=0.8: trungvi %+.2fpp (N=%d) | khi <=0.2: %+.2fpp (N=%d)' % (
            col, H, ic, 100 * hi.median(), len(hi), 100 * lo.median(), len(lo)))

# 5b: PE chuan hoa = PE hien tai * (ROE_hien_tai / ROE_trung_binh_dai_han)
roe_norm10 = df[df.time >= cur.time - pd.DateOffset(years=10)].roe_agg.mean()
print('\n  PE quan sat = %.2f ; ROE hien tai %.2f%% vs TB 10 nam %.2f%% => PE CHUAN HOA (E ve muc TB 10Y) = %.2f' % (
    cur.pe_con, 100 * cur.roe_agg, 100 * roe_norm10, cur.pe_con * cur.roe_agg / roe_norm10))
print('  (tuong duong: PB %.3f / ROE_TB10Y %.2f%% = %.2f)' % (cur.pb_con, 100 * roe_norm10, cur.pb_con / roe_norm10))

df.to_csv(EXP + 'panel_roe_fwd.csv', index=False)
