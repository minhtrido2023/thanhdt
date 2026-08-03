"""BUOC D — bang chi tieu + dose-response + DSR + PBO(CSCV) + LOO nam cho ho `CAPIT_LEVER_FORCE=f`.

Doc NAV ngay tu CSV ket qua bang chinh `dsr_pbo_annex.load_nav` (khong viet lai quy uoc registry).
job Taylor_20260803_101341 · RESEARCH-ONLY.

Gate dang ky truoc (plan §5 G-D + bo sung tu 2 lan quant-skeptic):
  OOS(2020+) duong · DSR >= 0,95 · MaxDD khong xau qua +1,0pp so control · PBO ho {f} < 0,5
"""
import warnings; warnings.filterwarnings('ignore')
import sys, glob, math
import numpy as np, pandas as pd
sys.path.insert(0, '/home/trido/thanhdt/WorkingClaude')
from dsr_pbo_annex import load_nav, moments, expected_max_sr, dsr, cscv_pbo

DATA = '/home/trido/thanhdt/WorkingClaude/data/'
ANN = 252.0
# Chan E125_* = lai vay 12,5%/nam (BASE dang ky trong plan §5); E140_* = 14%/nam (adversarial).
# Chan D_* (10%/nam) GIU LAI lam truc nhay lai suat — KHONG phai lai suat dang ky, khong dung lam gate.
LEGS = [('D0_control', 'control f=1 — PHAI tai lap 28,86% / -17,79% / 1,62 / 1.178,01B'),
        ('E125_f11', 'f=1,1 @ lai vay BASE 12,5%/nam'),
        ('E125_f12', 'f=1,2 @ 12,5%'),
        ('E125_f13', 'f=1,3 @ 12,5%'),
        ('E125_f15', 'f=1,5 @ 12,5%'),
        ('E140_f13', 'f=1,3 @ ADVERSARIAL 14%/nam'),
        ('E140_f15', 'f=1,5 @ ADVERSARIAL 14%/nam'),
        ('D_f11', '[nhay lai suat] f=1,1 @ 10%'),
        ('D_f12', '[nhay lai suat] f=1,2 @ 10%'),
        ('D_f13', '[nhay lai suat] f=1,3 @ 10%'),
        ('D_f15', '[nhay lai suat] f=1,5 @ 10%'),
        ('D_f13nc', '[tach bien] f=1,3 KHONG tinh lai vay (carry=0)')]
FVAL = {'D0_control': 1.0,
        'E125_f11': 1.1, 'E125_f12': 1.2, 'E125_f13': 1.3, 'E125_f15': 1.5,
        'E140_f13': 1.3, 'E140_f15': 1.5,
        'D_f11': 1.1, 'D_f12': 1.2, 'D_f13': 1.3, 'D_f15': 1.5, 'D_f13nc': 1.3}
# Gate chi doc chan lai suat DANG KY (BASE + adversarial); chan 10% chi de bao cao do nhay.
GATE_LEGS = ['E125_f11', 'E125_f12', 'E125_f13', 'E125_f15', 'E140_f13', 'E140_f15']


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
    g = [p for p in sorted(glob.glob(DATA + f'*exp_{tag}_univpit*.csv'))
         if not p.endswith(('_borrowledger.csv', '_leveraudit.csv'))]
    if not g:
        print(f'  (thieu CSV cho {tag})'); continue
    s = load_nav(g[0]); navs[tag] = s
    m = metr(s)
    m.update(leg=tag, f=FVAL[tag], mota=lbl, IS=seg(s, '2014-01-01', '2019-12-31'),
             OOS=seg(s, '2020-01-01', '2026-12-31'))
    rows.append(m)
T = pd.DataFrame(rows)[['leg', 'f', 'CAGR', 'Sharpe', 'MaxDD', 'Calmar', 'FinalNAV', 'IS', 'OOS', 'MDD_date', 'mota']]
print('=' * 160)
print('BUOC D — ENGINE TIER, forced-borrow. Lenh pin R3 nguyen van, snapshot asof20260729_postrestate, threads=1.')
print('=' * 160)
print(T.round(3).to_string(index=False))
T.to_csv('metrics_p5.csv', index=False)

if 'D0_control' not in navs:
    sys.exit('\nCHUA co chan control — dung lai, khong doc delta.')
base = navs['D0_control']
b = metr(base); bIS = seg(base, '2014-01-01', '2019-12-31'); bOOS = seg(base, '2020-01-01', '2026-12-31')
print(f'\nCONTROL SELF-CHECK vs pin R3 2026-08-03 (28,86 / -17,79 / 1,62 / 1.178,01B / IS 27,09 / OOS 30,48):')
print(f'  CAGR {b["CAGR"]:.4f}%  MaxDD {b["MaxDD"]:.4f}%  Calmar {b["Calmar"]:.4f}  '
      f'FinalNAV {b["FinalNAV"]:.4f}B  IS {bIS:.4f}%  OOS {bOOS:.4f}%')
_ok = (abs(b['CAGR'] - 28.86) < 0.02 and abs(b['MaxDD'] + 17.79) < 0.02 and abs(b['FinalNAV'] - 1178.01) < 0.5)
print(f'  -> {"TAI LAP DUNG PIN" if _ok else "*** LECH PIN — DUNG LAI, KHONG DOC KET QUA ***"}')

print('\nDelta so voi control  (dMaxDD DUONG = rui ro TOT hon; gate: khong duoc xau qua -1,0pp):')
for tag, lbl in LEGS[1:]:
    if tag not in navs: continue
    a = metr(navs[tag])
    dIS = seg(navs[tag], '2014-01-01', '2019-12-31') - bIS
    dOOS = seg(navs[tag], '2020-01-01', '2026-12-31') - bOOS
    print(f'  {tag:<12} f={FVAL[tag]:.2f}  dCAGR {a["CAGR"]-b["CAGR"]:+.3f}pp  dSharpe {a["Sharpe"]-b["Sharpe"]:+.4f}  '
          f'dMaxDD {a["MaxDD"]-b["MaxDD"]:+.3f}pp  dCalmar {a["Calmar"]-b["Calmar"]:+.4f}  '
          f'dIS {dIS:+.3f}pp  dOOS {dOOS:+.3f}pp   '
          f'[OOS {"PASS" if dOOS > 0 else "FAIL"} | DD {"PASS" if (a["MaxDD"]-b["MaxDD"]) > -1.0 else "FAIL"}]')

print('\n' + '=' * 160)
print('DOSE-RESPONSE theo f — don bay THAT thi phai don dieu theo boi so (p2 §1.3(2): phang = khong cham don bay)')
print('=' * 160)
# Dose-response phai doc trong CUNG MOT lai suat — tron 10%/12,5%/14% vao 1 bang la so sanh sai truc.
for _fam, _lbl in (('E125', 'lai vay BASE 12,5%/nam (truc gate)'),
                   ('E140', 'lai vay ADVERSARIAL 14%/nam'),
                   ('D',    'lai vay 10%/nam (chi de do DO NHAY, khong phai truc gate)')):
    _t = ['D0_control'] + [t for t, _ in LEGS
                           if t in navs and t.startswith(_fam + '_f') and not t.endswith('nc')]
    if len(_t) < 2: continue
    print(f'\n  --- ho {_fam}: {_lbl} ---')
    print('    f      CAGR    dCAGR   Sharpe   MaxDD   Calmar     IS      OOS')
    for tag in _t:
        a = metr(navs[tag])
        print(f'  {FVAL[tag]:.2f}  {a["CAGR"]:7.3f}%  {a["CAGR"]-b["CAGR"]:+.3f}pp  {a["Sharpe"]:6.3f}  '
              f'{a["MaxDD"]:7.3f}%  {a["Calmar"]:5.3f}  {seg(navs[tag],"2014-01-01","2019-12-31"):6.2f}%  '
              f'{seg(navs[tag],"2020-01-01","2026-12-31"):6.2f}%')

print('\n' + '=' * 160)
print('DSR (Bailey & Lopez de Prado). N = so cau hinh da so sanh de toi day.')
print('  N=5  : chi ho {f} cua job nay | N=25 : cong don margin+Kelly p1..p4 | N=180: cong don toan chu de (bao cao p4 §5)')
print('=' * 160)
for tag, lbl in LEGS:
    if tag not in navs: continue
    r = np.diff(np.log(navs[tag].values))
    srh, g3, g4 = moments(r)
    line = f'  {tag:<12} SR/obs {srh:.4f}'
    for N in (5, 25, 180):
        sr0 = expected_max_sr(1.0 / (len(r) - 1), N)
        d, st = dsr(srh, sr0, g3, g4, len(r))
        line += f'   N={N:<3d}: DSR {d:.4f}' + ('' if d >= 0.95 else ' <-RED')
    print(line)

print('\n' + '=' * 160)
print('PBO / CSCV — gate lan nay CUNG hon p3: PBO PHAI < 0,5 (bai hoc p3 §4.2)')
print('=' * 160)
# Ho cau hinh cho PBO = dung ho THUC SU da chon giua (control + luoi f o lai suat BASE dang ky).
# Khong nhet chan 10%/14%/no-carry vao: chung la truc do nhay/tach bien, khong phai ung vien canh tranh.
tags = ['D0_control'] + [t for t in GATE_LEGS if t in navs and t.startswith('E125')]
if len(tags) >= 3:
    idx = navs[tags[0]].index
    for t in tags: idx = idx.intersection(navs[t].index)
    M = np.column_stack([np.diff(np.log(navs[t].reindex(idx).values)) for t in tags])
    for S in (8, 12, 16):
        pbo, lg, ncomb, ncfg, T2 = cscv_pbo(M, S=S)
        print(f'  ho {{f}} = {len(tags)} cau hinh  S={S:2d}  combos={ncomb}  PBO={pbo:.3f}  '
              f'median logit={np.median(lg):+.3f}' + ('  <-- >=0,5 FAIL' if pbo >= 0.5 else '  PASS'))

print('\n' + '=' * 160)
print('PER-YEAR LEAVE-ONE-OUT')
print('=' * 160)


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
    _share = (d_full - outs[best]) / d_full * 100 if d_full else float('nan')
    print(f'  {tag:<12} dCAGR {d_full:+.3f}pp | LOO min {outs[worst]:+.3f}pp (bo {worst}) '
          f'max {outs[best]:+.3f}pp (bo {best}) | nam LOO am: {sum(1 for v in outs.values() if v<0)}/{len(outs)} '
          f'| nam ganh nhieu nhat {best} = {_share:.1f}% edge')
    print('      ' + '  '.join(f'{y}:{outs[y]:+.2f}' for y in yrs))
print('DONE')
