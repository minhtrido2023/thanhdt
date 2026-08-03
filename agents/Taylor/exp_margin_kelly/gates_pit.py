"""CONG KICH HOAT + TRAN RUIN — chay tren ro universe_pit (point-in-time, ban sach hon)."""
import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
EXP = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_margin_kelly/'
RNG = np.random.default_rng(20260803)
pd.set_option('display.width', 220)
C = pd.read_csv(EXP + 'compare_pit.csv', parse_dates=['event'])
V = C[C.x_pit.notna()].copy()
V14 = V[V.event >= '2014-01-01'].copy()


def blk(v, lbl):
    v = np.asarray(v, float)
    if len(v) < 2:
        print(f'  {lbl:<46} N={len(v)}  ' + (f'x={100*v[0]:+.1f}%' if len(v) else '')); return
    b = np.array([RNG.choice(v, len(v), True).mean() for _ in range(20000)])
    print(f'  {lbl:<46} N={len(v):2d} TB {100*v.mean():+7.2f}% TV {100*np.median(v):+7.2f}% '
          f'%duong {100*(v>0).mean():5.1f} CI90 [{100*np.percentile(b,5):+6.2f};{100*np.percentile(b,95):+6.2f}] '
          f'p={2*min((b<=0).mean(),(b>=0).mean()):.3f}')


print('=' * 120); print('CONG KICH HOAT — x_pit (loi the RONG cua 1 dong VAY), ky DT5G 2014+'); print('=' * 120)
G = [('G0 moi washout', np.ones(len(V14), bool)),
     ('G1 state<=2 (CRISIS/BEAR)', (V14.state <= 2).values),
     ('G2 state>=3 (NEUTRAL+) <- o cua 2026-07-20', (V14.state >= 3).values),
     ('G3 pe_pct<=0.20 (cong V2.5 state-blind)', (V14.pe_pct <= 0.20).values),
     ('G4 pe_pct>0.20', (V14.pe_pct > 0.20).values)]
for lbl, m in G: blk(V14.x_pit.values[m], lbl)

print('\nDOSE-RESPONSE theo do SAU cua washout (dd52 VNINDEX tai ngay fire), 2014+:')
for thr in (-25, -20, -15, -10, -5, 0):
    m = (V14.dd52 <= thr).values
    blk(V14.x_pit.values[m], f'dd52 <= {thr:+d}%')
print('  (chieu nguoc lai)')
for thr in (-20, -15, -10):
    m = (V14.dd52 > thr).values
    blk(V14.x_pit.values[m], f'dd52 >  {thr:+d}%')

print('\nDOSE-RESPONSE theo breadth oversold tai ngay fire, 2014+:')
for thr in (0.30, 0.35, 0.40, 0.45):
    m = (V14.ovs >= thr).values
    blk(V14.x_pit.values[m], f'oversold >= {thr:.0%}')

print('\n' + '=' * 120); print('TRAN RUIN — margin call'); print('=' * 120)
mae = pd.read_csv(EXP + 'events_outcome.csv')
mae = mae[mae.mae.notna()]
w = float(mae.mae.min())
print(f'  MAE xau nhat (ro CAPIT, trong 60 phien): {100*w:+.1f}%  |  p10 {100*np.percentile(mae.mae,10):+.1f}%')
print('  Cong thuc: gross g (tai san = g x NAV, no = (g-1) x NAV). Cu sut |w| tren TAI SAN CO PHIEU:')
print('    equity/tai_san = (g(1-|w|) - (g-1)) / (g(1-|w|)) ; goi margin khi < maintenance m')
for m_ in (0.30, 0.35):
    for g in (1.3, 1.5, 1.8, 2.0, 2.36):
        a = g * (1 - abs(w)); e = a - (g - 1)
        print(f'    maint={m_:.0%} gross={g:.2f} : sau cu MAE {100*w:+.1f}% -> equity/ts = {e/a:6.1%} '
              f'{"=> MARGIN CALL" if e/a < m_ else ""}')
    print()
print('DONE')
