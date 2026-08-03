"""PHAN 3 — bang chi tieu + dose-response + DSR + PBO(CSCV) + LOO cho ho `park:f` / `parkdd:f`.

Doc NAV ngay tu CSV ket qua (combined_nav) bang chinh `dsr_pbo_annex.load_nav` (khong viet lai),
tinh CAGR/Sharpe/MaxDD/Calmar theo dung quy uoc registry.
job Taylor_20260803_082141 · RESEARCH-ONLY.
"""
import warnings; warnings.filterwarnings('ignore')
import sys, glob, math
import numpy as np, pandas as pd
sys.path.insert(0, '/home/trido/thanhdt/WorkingClaude')
from dsr_pbo_annex import load_nav, moments, expected_max_sr, dsr, cscv_pbo

DATA = '/home/trido/thanhdt/WorkingClaude/data/'
ANN = 252.0
LEGS = [('p3_P0_control', 'cash — control, PHAI = 28,86%'),
        ('p3_PK000', 'park:0   — identity check (PHAI trung control)'),
        ('p3_PK025', 'park:0.25  — dich 25% parking, MOI su kien'),
        ('p3_PK050', 'park:0.5   — dich 50% parking, MOI su kien'),
        ('p3_PK075', 'park:0.75  — dich 75% parking, MOI su kien'),
        ('p3_PK100', 'park:1.0   == idle, MOI su kien'),
        ('p3_PD025', 'parkdd:0.25 — CHI su kien dd52<=-20%'),
        ('p3_PD050', 'parkdd:0.5  — CHI su kien dd52<=-20%'),
        ('p3_PD075', 'parkdd:0.75 — CHI su kien dd52<=-20%'),
        ('p3_PD100', 'parkdd:1.0  — CHI su kien dd52<=-20%')]


def metr(s):
    lp = np.log(s.values)
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    cagr = (s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1
    r = np.diff(lp)
    sh = r.mean() / r.std(ddof=1) * math.sqrt(ANN)
    dd = s / s.cummax() - 1
    mdd = dd.min()
    return dict(CAGR=100 * cagr, Sharpe=sh, MaxDD=100 * mdd, Calmar=cagr / abs(mdd),
                FinalNAV=s.iloc[-1] / 1e9, MDD_date=str(dd.idxmin().date()))


def seg(s, a, b):
    x = s[(s.index >= a) & (s.index <= b)]
    if len(x) < 20: return np.nan
    y = (x.index[-1] - x.index[0]).days / 365.25
    return 100 * ((x.iloc[-1] / x.iloc[0]) ** (1 / y) - 1)


navs, rows = {}, []
for tag, lbl in LEGS:
    g = glob.glob(DATA + f'*exp_{tag}_univpit*.csv')
    if not g:
        print(f'  (thieu CSV cho {tag})'); continue
    s = load_nav(g[0]); navs[tag] = s
    m = metr(s)
    m.update(leg=tag, mota=lbl, IS=seg(s, '2014-01-01', '2019-12-31'),
             OOS=seg(s, '2020-01-01', '2026-12-31'))
    rows.append(m)
T = pd.DataFrame(rows)[['leg', 'CAGR', 'Sharpe', 'MaxDD', 'Calmar', 'FinalNAV', 'IS', 'OOS', 'MDD_date', 'mota']]
print('=' * 155)
print('PHAN 3 — TACH BIEN SIZING (lenh pin R3 nguyen van, snapshot asof20260729_postrestate, threads=1, MGE TAT => 0 dong vay)')
print('=' * 155)
print(T.round(2).to_string(index=False))

base = navs['p3_P0_control']
b = metr(base); bOOS = seg(base, '2020-01-01', '2026-12-31'); bIS = seg(base, '2014-01-01', '2019-12-31')
print('\nDelta so voi control (duong o cot MaxDD = rui ro TOT hon):')
for tag, lbl in LEGS[1:]:
    if tag not in navs: continue
    a = metr(navs[tag])
    print(f'  {tag:<14} dCAGR {a["CAGR"]-b["CAGR"]:+.2f}pp  dSharpe {a["Sharpe"]-b["Sharpe"]:+.3f}  '
          f'dMaxDD {a["MaxDD"]-b["MaxDD"]:+.2f}pp  dCalmar {a["Calmar"]-b["Calmar"]:+.3f}  '
          f'dIS {seg(navs[tag],"2014-01-01","2019-12-31")-bIS:+.2f}pp  '
          f'dOOS {seg(navs[tag],"2020-01-01","2026-12-31")-bOOS:+.2f}pp')

# ------------------------------------------------- dose-response
print('\n' + '=' * 155)
print('DOSE-RESPONSE theo f — co don dieu khong?')
print('=' * 155)
for fam, pref in (('park:f    (MOI su kien)', 'p3_PK'), ('parkdd:f  (CHI dd52<=-20%)', 'p3_PD')):
    fs = [(0.0, 'p3_PK000') if pref == 'p3_PK' else (0.0, 'p3_P0_control')]
    fs += [(v, f'{pref}{int(v*100):03d}') for v in (0.25, 0.5, 0.75, 1.0)]
    print(f'\n  {fam}')
    print('    f      CAGR    dCAGR   Sharpe   MaxDD   Calmar    IS      OOS')
    for v, tg in fs:
        if tg not in navs: continue
        a = metr(navs[tg])
        print(f'    {v:.2f}  {a["CAGR"]:6.2f}%  {a["CAGR"]-b["CAGR"]:+.2f}pp  {a["Sharpe"]:6.3f}  '
              f'{a["MaxDD"]:6.2f}%  {a["Calmar"]:5.3f}  {seg(navs[tg],"2014-01-01","2019-12-31"):6.2f}%  '
              f'{seg(navs[tg],"2020-01-01","2026-12-31"):6.2f}%')

# ------------------------------------------------- DSR
print('\n' + '=' * 155)
print('DSR (Bailey & Lopez de Prado) — N khai bao xem bao cao §ky luat thong ke')
print('=' * 155)
for tag, lbl in LEGS:
    if tag not in navs: continue
    r = np.diff(np.log(navs[tag].values))
    srh, g3, g4 = moments(r)
    line = f'  {tag:<14} SR/obs {srh:.4f}'
    for N in (9, 24, 38):
        sr0 = expected_max_sr(1.0 / (len(r) - 1), N)
        d, st = dsr(srh, sr0, g3, g4, len(r))
        line += f'   N={N:2d}: DSR {d:.4f}' + ('' if d >= 0.95 else ' <-- RED')
    print(line)

# ------------------------------------------------- PBO (CSCV)
print('\n' + '=' * 155)
print('PBO / CSCV (Bailey et al 2017) — chon cau hinh theo thu hang backtest co dang overfit khong?')
print('=' * 155)
fams = {
    'ho DAY DU 9 cau hinh (control + park*4 + parkdd*4)':
        ['p3_P0_control', 'p3_PK025', 'p3_PK050', 'p3_PK075', 'p3_PK100',
         'p3_PD025', 'p3_PD050', 'p3_PD075', 'p3_PD100'],
    'chi ho park:f (control + 4)':
        ['p3_P0_control', 'p3_PK025', 'p3_PK050', 'p3_PK075', 'p3_PK100'],
    'chi ho parkdd:f (control + 4)':
        ['p3_P0_control', 'p3_PD025', 'p3_PD050', 'p3_PD075', 'p3_PD100'],
}
for name, tags in fams.items():
    tags = [t for t in tags if t in navs]
    idx = navs[tags[0]].index
    for t in tags: idx = idx.intersection(navs[t].index)
    M = np.column_stack([np.diff(np.log(navs[t].reindex(idx).values)) for t in tags])
    for S in (8, 12, 16):
        pbo, lg, ncomb, ncfg, T2 = cscv_pbo(M, S=S)
        print(f'  {name:<52} S={S:2d}  Ncfg={ncfg}  combos={ncomb}  '
              f'PBO={pbo:.3f}  median logit={np.median(lg):+.3f}'
              + ('  <-- >=0.5 (CAM chon theo hang backtest)' if pbo >= 0.5 else ''))

# ------------------------------------------------- per-year LOO
print('\n' + '=' * 155)
print('PER-YEAR LEAVE-ONE-OUT: bo tung nam, delta CAGR con lai bao nhieu?')
print('=' * 155)


def cagr_ex(s, ex):
    r = pd.Series(np.diff(np.log(s.values)), index=s.index[1:])
    r = r[r.index.year != ex]
    n = len(r)
    return 100 * (math.exp(r.sum() * (ANN / n)) - 1) if n else np.nan


for tag, lbl in LEGS[1:]:
    if tag not in navs: continue
    a = navs[tag]
    yrs = sorted(set(a.index.year))
    d_full = metr(a)['CAGR'] - b['CAGR']
    outs = {y: cagr_ex(a, y) - cagr_ex(base, y) for y in yrs}
    worst = min(outs, key=outs.get); best = max(outs, key=outs.get)
    print(f'  {tag:<14} dCAGR day du {d_full:+.2f}pp | LOO min {outs[worst]:+.2f}pp (bo {worst}) '
          f'max {outs[best]:+.2f}pp (bo {best}) | so nam LOO am: {sum(1 for v in outs.values() if v<0)}/{len(outs)}')
    print('      ' + '  '.join(f'{y}:{outs[y]:+.2f}' for y in yrs))
print('DONE')
