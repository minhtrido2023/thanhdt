"""NT2 bo sung 3c (job Taylor_20261107_131635). Chay: $DNA_PYEXE -B model_5f.py > model_5f_out.txt
Tai dung NGUYEN ham val/grid cua model_r2.py (exec, khong sua file cu). Quy uoc chiet khau giu nguyen: nam 1 = t=1 cuoi nam.
Bien the:
 - CHAT3C_EBIT_{median,mean}: LNST chuan hoa doi ve bien EBIT TB chu ky NGANH (peer nhiet dien noi dia, BQ ticker_financial
   EBITM_P0 dong Q4 = ca nam, 2015-2025) x DT chuan hoa NT2 (TB 2016-2025) x (1-20%) + thu nhap TC rong; TINH TIEN CA LUOI
   (doi xung 2 phia, giu do rong). RONIC: mo hinh khong tai dau tu, TV=0 => kenh RONIC = 0 (khong ap dung).
 - WIDE (neu 'hao' sai = ben): sau thoi han PPA dong tien van hanh tiep VO HAN o RONIC=Ke (g=0, op/r chiet khau ve).
"""
import io, contextlib, json, os, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__))
g = {'__file__': os.path.join(HERE, 'model_r2.py'), '__name__': 'nt2_r2'}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open(os.path.join(HERE, 'model_r2.py')).read(), g)
R2, val, NPS0, WNP, YRS, WY, RS, WR = g['R2'], g['val'], g['NPS'], g['WNP'], g['YRS'], g['WY'], g['RS'], g['WR']
PX, LD, SH, FIN, Q = g['PX'], g['LD'], g['SH'], g['FIN_NET_AT'], g['Q']
import itertools
# BQ do 07/11/2026 (xem ADDENDUM_5F.md): EBITM TB 2015-2025 (dong Q4, so nam du 4 quy)
PEER_EBITM = dict(POW=0.093, PPC=0.079, QTP=0.126, HND=0.101, PGV=0.100, BTP=0.054)
NT2_EBITM = 0.120
REV = [7983, 6761, 7670, 7654, 6082, 6150, 8788, 6383, 5944, 7958]  # NT2 DT 2016-2025, ty (tong Revenue_P0 4 quy)
REV_N = sum(REV) / len(REV)

def run(shift=0.0, wide=False):
    v, w = [], []
    for (a, wa), (y, wy), (rr, wr) in itertools.product(zip(NPS0, WNP), zip(YRS, WY), zip(RS, WR)):
        x = val(a + shift, y, rr)
        if wide:
            x += (a + shift - FIN) / rr / (1 + rr) ** y / SH * 1000
        v.append(x); w.append(wa * wy * wr)
    s = R2.stats(v, w, PX, LD)
    s['label'] = R2.label(PX, s)
    s['sleeve_center_post'] = {k: s['center_pre'] * (1 - Q['adv250']['sizes'][k]['disc']) for k in Q['adv250']['sizes']}
    return s

out = {'rev_norm': REV_N, 'model_ebit_margin_implied': (800 - FIN) / 0.8 / REV_N, 'peer_ebitm': PEER_EBITM,
       'peer_median': st.median(PEER_EBITM.values()), 'peer_mean': st.mean(PEER_EBITM.values())}
res = {'BASE_r2': run()}
for k in ('median', 'mean'):
    lnst = out[f'peer_{k}'] * REV_N * 0.8 + FIN
    out[f'lnst_center_chat3c_{k}'] = lnst
    res[f'CHAT3C_EBIT_{k}'] = run(shift=lnst - 800)
res['WIDE_TV_RONIC_eq_Ke'] = run(wide=True)
out['variants'] = res
print(f"DT chuan hoa {REV_N:,.0f}; bien EBIT ngam dinh mo hinh {out['model_ebit_margin_implied']:.2%}; peer median {out['peer_median']:.2%} mean {out['peer_mean']:.2%}; NT2 TB {NT2_EBITM:.1%}")
for k in ('median', 'mean'):
    print(f"LNST tam chat-3c ({k}) = {out[f'lnst_center_chat3c_{k}']:,.0f}")
for k, s in res.items():
    print(f"{k}: " + R2.fmt(s, PX) + " | sleeve " + ", ".join(f"{a}:{b:,.0f}" for a, b in s['sleeve_center_post'].items()))
json.dump(out, open(os.path.join(HERE, 'model_5f_out.json'), 'w'), ensure_ascii=False, indent=1, sort_keys=True, default=float)
