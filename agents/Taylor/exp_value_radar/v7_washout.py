"""VIEC (job Taylor_20260730_171814) — Value Radar ROLLING-10Y doc tai 26 su kien CAPIT-washout.

KHONG dinh nghia lai washout: dung nguyen exp_valframe/capit_events_gate0.3.csv (Viec 2 cua
fundamental_valuation_framework_20260729.md). KHONG doi cong thuc radar: dung cot radar3_roll
cua exp_value_radar/radar.csv (== value_radar.py `score`, parity 0/4134 nhan lech).
Output: washout_radar.csv + in bang thong ke.
"""
import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd

EXP = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_value_radar/'
VAL = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_valframe/'
pd.set_option('display.width', 250)
RNG = np.random.default_rng(20260730)

# ---------------------------------------------------------------- 0. self-check tai lap
ev = pd.read_csv(VAL + 'capit_events_gate0.3.csv', parse_dates=['event'])
rd = pd.read_csv(EXP + 'radar.csv', parse_dates=['time'])
print('=' * 110)
print('SELF-CHECK 0 — parity nguon')
print('=' * 110)
print('  su kien CAPIT gate0.30 : N=%d  (%s -> %s)' % (len(ev), ev.event.min().date(), ev.event.max().date()))
assert len(ev) == 26, 'phai dung 26 su kien goc'
# doi chieu 3 dong voi bang §2.2 cua bao cao goc (chep tay tu markdown)
ref = {'2011-11-14': (1.33, 1.72, 7.92), '2018-05-28': (2.83, 85.96, 18.51), '2026-07-20': (1.91, 43.60, 12.20)}
for d, (pb, pct, pe) in ref.items():
    r = ev[ev.event == d].iloc[0]
    ok = abs(r.pb_cap10 - pb) < .01 and abs(r.pb_cap10_pctE - pct) < .01 and abs(r.pe_cap10 - pe) < .01
    print('  §2.2 %s  pb=%.2f pctE=%.2f pe=%.2f  -> %s' % (d, r.pb_cap10, r.pb_cap10_pctE, r.pe_cap10, 'MATCH' if ok else 'MISMATCH'))
    assert ok
# radar rolling: doi chieu voi so da cong bo (C.4.5 update + module value_radar.py)
chk = {'2026-07-30': 25.9}
for d, v in chk.items():
    got = rd.loc[rd.time == d, 'radar3_roll'].iloc[0]
    print('  radar3_roll %s = %.1f (cong bo %.1f) -> %s' % (d, got, v, 'MATCH' if abs(got - v) < .1 else 'MISMATCH'))
    assert abs(got - v) < .1
print('  radar3_roll co tu %s, N=%d phien' % (rd.dropna(subset=['radar3_roll']).time.iloc[0].date(), rd.radar3_roll.notna().sum()))

# ---------------------------------------------------------------- 1. merge radar tai ngay fire
m = ev.merge(rd[['time', 'radar3', 'radar3_roll', 'lab_radar3_roll', 'p_pe_r', 'p_pb_r', 'p_sp_r', 'state']],
             left_on='event', right_on='time', how='left')
miss = m[m.time.isna()]
print('  su kien khong khop dung phien radar: %d %s' % (len(miss), list(miss.event.dt.date)))
assert len(miss) == 0, 'moi ngay fire phai la 1 phien giao dich co trong radar.csv'

VN = {'CHEAP': 'RE', 'FAIR': 'TRUNG TINH', 'EXPENSIVE': 'DAT'}
m['nhan'] = m.lab_radar3_roll.map(VN).fillna('(burn-in)')
m['year'] = m.event.dt.year

print('\n' + '=' * 110)
print('B1 — 26 SU KIEN CAPIT + RADAR ROLLING-10Y TAI NGAY FIRE')
print('=' * 110)
cols = ['event', 'ovs', 'dd52', 'radar3_roll', 'nhan', 'p_pe_r', 'p_pb_r', 'p_sp_r', 'radar3', 'r3M', 'r6M', 'r12M', 'mdd12M']
print(m[cols].round(1).to_string(index=False))
print('\nPhan bo nhan tren 26 su kien:')
print(m.nhan.value_counts().to_string())

m.to_csv(EXP + 'washout_radar.csv', index=False)

# ---------------------------------------------------------------- 2. so sanh nhom
# cua so ket cuc = dung y bang §2.2: r3M / r6M / r12M / mdd12M
# su kien CHUA du cua so -> loai khoi chinh metric do (khong dung so cut ngan)
LAST = rd.time.max()


def eligible(col):
    need = {'r3M': 63, 'r6M': 126, 'r12M': 252, 'mdd12M': 252, 'mdd3M': 63}[col]
    # so phien thuc te co sau ngay fire
    idx = rd.time.values
    out = []
    for _, r in m.iterrows():
        n_after = (idx > np.datetime64(r.event)).sum()
        out.append(n_after >= need and np.isfinite(r[col]))
    return np.array(out)


def desc(sub, col):
    v = sub[col].dropna().values
    if len(v) == 0:
        return dict(n=0)
    return dict(n=len(v), med=np.median(v), mean=v.mean(), pos=100 * (v > 0).mean())


def boot_med(v, B=8000):
    if len(v) < 2:
        return (np.nan, np.nan)
    s = np.array([np.median(RNG.choice(v, len(v), replace=True)) for _ in range(B)])
    return np.percentile(s, 5), np.percentile(s, 95)


def boot_diff(a, b, B=8000):
    """CI90 + p 2 phia cho hieu trung vi (a - b), bootstrap doc lap 2 nhom."""
    if len(a) < 2 or len(b) < 2:
        return (np.nan, np.nan, np.nan)
    d = np.array([np.median(RNG.choice(a, len(a), True)) - np.median(RNG.choice(b, len(b), True)) for _ in range(B)])
    p = 2 * min((d <= 0).mean(), (d >= 0).mean())
    return np.percentile(d, 5), np.percentile(d, 95), p


def perm_p(a, b, B=20000):
    """permutation 2 phia tren hieu trung vi — khong gia dinh phan phoi."""
    if len(a) < 2 or len(b) < 2:
        return np.nan
    obs = np.median(a) - np.median(b)
    pool = np.concatenate([a, b]); n = len(a)
    cnt = 0
    for _ in range(B):
        p = RNG.permutation(pool)
        if abs(np.median(p[:n]) - np.median(p[n:])) >= abs(obs) - 1e-12:
            cnt += 1
    return (cnt + 1) / (B + 1)


print('\n' + '=' * 110)
print('B2 — KET CUC FORWARD THEO NHAN RADAR (chi su kien du cua so)')
print('=' * 110)
rows = []
tests = []
for col in ['r3M', 'r6M', 'r12M', 'mdd12M']:
    el = eligible(col)
    sub = m[el]
    print('\n--- %s --- (N du cua so = %d / 26)' % (col, len(sub)))
    for lab in ['RE', 'TRUNG TINH', 'DAT', '(burn-in)']:
        s = sub[sub.nhan == lab]
        d = desc(s, col)
        if d['n'] == 0:
            continue
        lo, hi = boot_med(s[col].dropna().values)
        rows.append(dict(metric=col, nhan=lab, **d, ci_lo=lo, ci_hi=hi))
        print('  %-12s N=%2d  trung vi %+7.2f  CI90 [%+6.1f;%+6.1f]  TB %+7.2f  %%duong %5.1f' %
              (lab, d['n'], d['med'], lo, hi, d['mean'], d['pos']))
    base = sub[col].dropna().values
    lo, hi = boot_med(base)
    rows.append(dict(metric=col, nhan='VO DIEU KIEN', n=len(base), med=np.median(base), mean=base.mean(),
                     pos=100 * (base > 0).mean(), ci_lo=lo, ci_hi=hi))
    print('  %-12s N=%2d  trung vi %+7.2f  CI90 [%+6.1f;%+6.1f]  TB %+7.2f  %%duong %5.1f' %
          ('BASELINE', len(base), np.median(base), lo, hi, base.mean(), 100 * (base > 0).mean()))
    # 2 phep thu / metric: RE vs (TRUNG TINH+DAT)  va  RE vs BASELINE-khong-RE == cung nhom => 1 test
    a = sub[sub.nhan == 'RE'][col].dropna().values
    b = sub[sub.nhan.isin(['TRUNG TINH', 'DAT'])][col].dropna().values
    dlo, dhi, pb = boot_diff(a, b)
    pp = perm_p(a, b)
    tests.append(dict(test='RE vs KHONG-RE | ' + col, n_a=len(a), n_b=len(b),
                      diff=np.median(a) - np.median(b) if len(a) and len(b) else np.nan,
                      ci_lo=dlo, ci_hi=dhi, p_boot=pb, p_perm=pp))
    print('    HIEU RE - (TRUNG TINH+DAT) = %+.2fpp  CI90 [%+.1f;%+.1f]  p_boot=%.3f  p_perm=%.3f' %
          (np.median(a) - np.median(b), dlo, dhi, pb, pp))

pd.DataFrame(rows).to_csv(EXP + 'washout_radar_groups.csv', index=False)

# ---------------------------------------------------------------- 3. rui ro: P(roi sau them)
print('\n' + '=' * 110)
print('B3 — XAC SUAT "ROI SAU THEM" SAU NGAY FIRE')
print('=' * 110)
for col, thr, ten in [('mdd3M', -10, 'P(mdd 3M <= -10%)'), ('mdd12M', -20, 'P(mdd 12M <= -20%)')]:
    el = eligible(col)
    sub = m[el]
    print('\n--- %s --- (N=%d)' % (ten, len(sub)))
    for lab in ['RE', 'TRUNG TINH', 'DAT', '(burn-in)']:
        s = sub[sub.nhan == lab][col].dropna().values
        if len(s) == 0:
            continue
        hit = (s <= thr)
        bs = np.array([RNG.choice(hit, len(hit), True).mean() for _ in range(8000)]) * 100
        print('  %-12s N=%2d  %s = %5.1f%%  CI90 [%4.1f;%5.1f]' %
              (lab, len(s), ten, 100 * hit.mean(), np.percentile(bs, 5), np.percentile(bs, 95)))
    base = sub[col].dropna().values
    print('  %-12s N=%2d  %s = %5.1f%%' % ('BASELINE', len(base), ten, 100 * (base <= thr).mean()))
    a = (sub[sub.nhan == 'RE'][col].dropna().values <= thr).astype(float)
    b = (sub[sub.nhan.isin(['TRUNG TINH', 'DAT'])][col].dropna().values <= thr).astype(float)
    if len(a) > 1 and len(b) > 1:
        d = np.array([RNG.choice(a, len(a), True).mean() - RNG.choice(b, len(b), True).mean() for _ in range(8000)]) * 100
        p = 2 * min((d <= 0).mean(), (d >= 0).mean())
        tests.append(dict(test='RE vs KHONG-RE | ' + ten, n_a=len(a), n_b=len(b),
                          diff=100 * (a.mean() - b.mean()), ci_lo=np.percentile(d, 5), ci_hi=np.percentile(d, 95),
                          p_boot=p, p_perm=np.nan))
        print('    HIEU RE - KHONG-RE = %+.1fpp  CI90 [%+.1f;%+.1f]  p_boot=%.3f' %
              (100 * (a.mean() - b.mean()), np.percentile(d, 5), np.percentile(d, 95), p))

# ---------------------------------------------------------------- 4. radar co them gi so voi pb pctE?
print('\n' + '=' * 110)
print('B4 — RADAR ROLLING-10Y CO PHAI CHIEU MOI? (vs %ile P/B expanding da test o Viec 2)')
print('=' * 110)
cc = m[['radar3_roll', 'pb_cap10_pctE', 'pe_cap10_pctE', 'radar3', 'ovs', 'dd52']].dropna()
print(cc.corr(method='spearman').round(3).to_string())
print('\n(Spearman tren 25 su kien co radar; radar3 = ban expanding da bao cao truoc)')

# ---------------------------------------------------------------- 5. su kien dang song
print('\n' + '=' * 110)
print('B5 — SU KIEN LIVE 2026-07-20 DAT VAO PHAN PHOI LICH SU')
print('=' * 110)
live = m[m.event == '2026-07-20'].iloc[0]
hist = m[m.event < '2026-07-20'].dropna(subset=['radar3_roll'])
print('  radar rolling-10Y tai 2026-07-20 = %.1f -> %s   (expanding-2008: %.1f)' %
      (live.radar3_roll, live.nhan, live.radar3))
print('  xep hang trong 25 su kien lich su: %d/%d tu re nhat (phan vi %.0f)' %
      ((hist.radar3_roll < live.radar3_roll).sum() + 1, len(hist) + 1,
       100 * (hist.radar3_roll < live.radar3_roll).mean()))
print('  radar hom nay 2026-07-30 = %.1f (%s)' % (rd.radar3_roll.iloc[-1], rd.lab_radar3_roll.iloc[-1]))
print('\n  phan phoi radar3_roll tai 26 su kien:')
print('   ', np.round(np.sort(hist.radar3_roll.values), 1))

print('\n' + '=' * 110)
print('B6 — BANG PHEP THU (de cong don vao N_trials trong ngay)')
print('=' * 110)
T = pd.DataFrame(tests)
T.to_csv(EXP + 'washout_radar_tests.csv', index=False)
print(T.round(4).to_string(index=False))
print('\nSo phep thu MOI trong bao cao nay = %d' % len(T))
