"""VIEC 1 — bang chi tieu + DSR cho cac chan engine S4.

Doc NAV ngay tu CSV ket qua (combined_nav), tinh CAGR/Sharpe/MaxDD/Calmar theo dung quy uoc
registry, roi DSR (Bailey & Lopez de Prado) bang chinh ham cua `dsr_pbo_annex.py` (khong viet lai).
Kem per-year leave-one-out: nam nao ganh edge.
"""
import warnings; warnings.filterwarnings('ignore')
import sys, glob, math
import numpy as np, pandas as pd
sys.path.insert(0, '/home/trido/thanhdt/WorkingClaude')
from dsr_pbo_annex import load_nav, moments, expected_max_sr, dsr

DATA = '/home/trido/thanhdt/WorkingClaude/data/'
ANN = 252.0
LEGS = [('L0_control', 'control (khong bat gi) — PHAI = 28,86%'),
        ('L1b_mge130dd52', 'MGE 1.3 + cong dd52<=-20% (S4 dung nghia)'),
        ('L2b_mge150dd52', 'MGE 1.5 + cong dd52<=-20% (S4 dung nghia)'),
        ('L1_mge130', 'MGE 1.3 KHONG cong (bay: MGE_GATE vo hieu)'),
        ('L2_mge150', 'MGE 1.5 KHONG cong (bay: MGE_GATE vo hieu)')]


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
    g = glob.glob(DATA + f'*exp_s4p2_{tag}_univpit*.csv')
    if not g:
        print(f'  (thieu CSV cho {tag})'); continue
    s = load_nav(g[0])
    navs[tag] = s
    m = metr(s)
    m.update(leg=tag, mota=lbl, IS=seg(s, '2014-01-01', '2019-12-31'), OOS=seg(s, '2020-01-01', '2026-12-31'))
    rows.append(m)
T = pd.DataFrame(rows)[['leg', 'CAGR', 'Sharpe', 'MaxDD', 'Calmar', 'FinalNAV', 'IS', 'OOS', 'MDD_date', 'mota']]
print('=' * 150)
print('VIEC 1 — TANG PORTFOLIO-ENGINE (lenh pin R3 nguyen van, snapshot asof20260729_postrestate, threads=1)')
print('=' * 150)
print(T.round(2).to_string(index=False))

base = navs.get('L0_control')
if base is not None:
    print('\nDelta so voi control:')
    for tag, lbl in LEGS[1:]:
        if tag not in navs: continue
        a, b = metr(navs[tag]), metr(base)
        print(f'  {tag:<16} dCAGR {a["CAGR"]-b["CAGR"]:+.2f}pp  dSharpe {a["Sharpe"]-b["Sharpe"]:+.3f}  '
              f'dMaxDD {a["MaxDD"]-b["MaxDD"]:+.2f}pp (duong=tot hon)  dCalmar {a["Calmar"]-b["Calmar"]:+.3f}  '
              f'dOOS {seg(navs[tag],"2020-01-01","2026-12-31")-seg(base,"2020-01-01","2026-12-31"):+.2f}pp')

# ---------------------------------------------------------------- DSR
print('\n' + '=' * 150)
print('DSR (Bailey & Lopez de Prado) — P(SR that > SR ky vong lon nhat duoi gia thuyet KHONG KY NANG, N phep thu)')
print('=' * 150)
print('  N khai bao (ho phep thu don bay CAPIT tich luy tren cung chu de):')
print('    2026-06-23..25 MGE_CAPIT_ONLY + FORCE_REAL_LEVER (4) · 2026-06-26 Kelly-lever sweep MGE 1.3/1.5/1.8/2.0 (4)')
print('    2026-06-24 MGE_GATE none/deposit/fedborrow/deposit_eyield/conviction (5) · V2.5 family (4)')
print('    job nay: 1.3/1.5 x {khong cong, cong dd52} (4)  => N ~ 21')
for tag, lbl in LEGS:
    if tag not in navs: continue
    s = navs[tag]
    r = np.diff(np.log(s.values))
    srh, g3, g4 = moments(r)
    for N in (4, 21):
        sr0 = expected_max_sr(1.0 / (len(r) - 1), N)
        d, st = dsr(srh, sr0, g3, g4, len(r))
        print(f'  {tag:<16} N={N:2d}  SR/obs {srh:.4f}  SR0 {sr0:.4f}  DSR {d:.4f} '
              f'{"" if d >= 0.95 else "<-- DUOI 0.95 (RED FLAG)"}')

# ---------------------------------------------------------------- per-year LOO
print('\n' + '=' * 150)
print('PER-YEAR LEAVE-ONE-OUT: bo tung nam, delta CAGR con lai bao nhieu? (1-2 nam ganh het = reshuffle-luck)')
print('=' * 150)
if base is not None:
    for tag, lbl in LEGS[1:]:
        if tag not in navs: continue
        a, b = navs[tag], base
        yrs = sorted(set(a.index.year))
        # chuoi log-return theo nam -> tong hop CAGR bo 1 nam
        def cagr_ex(s, ex):
            r = pd.Series(np.diff(np.log(s.values)), index=s.index[1:])
            r = r[r.index.year != ex]
            n = len(r)
            return 100 * (math.exp(r.sum() * (ANN / n)) - 1) if n else np.nan
        d_full = metr(a)['CAGR'] - metr(b)['CAGR']
        outs = {y: cagr_ex(a, y) - cagr_ex(b, y) for y in yrs}
        worst = min(outs, key=outs.get); best = max(outs, key=outs.get)
        print(f'  {tag:<16} dCAGR day du {d_full:+.2f}pp | LOO min {outs[worst]:+.2f}pp (bo {worst}) '
              f'max {outs[best]:+.2f}pp (bo {best}) | so nam LOO am: {sum(1 for v in outs.values() if v<0)}/{len(outs)}')
        print('        ' + '  '.join(f'{y}:{outs[y]:+.2f}' for y in yrs))
print('DONE')
