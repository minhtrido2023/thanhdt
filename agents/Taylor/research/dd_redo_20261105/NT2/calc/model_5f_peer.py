"""Do nhay chon peer cho CHAT3C (job Taylor_20261107_172009). Tai dung run() cua model_5f.py. Chay: $DNA_PYEXE -B model_5f_peer.py"""
import io, contextlib, os, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__))
g = {'__file__': os.path.join(HERE, 'model_5f.py'), '__name__': 'nt2_5f'}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open(os.path.join(HERE, 'model_5f.py')).read(), g)
P, run, REV_N, FIN, R2, PX = g['PEER_EBITM'], g['run'], g['REV_N'], g['FIN'], g['R2'], g['PX']
sets = {'all6': list(P), 'ex_BTP': [k for k in P if k != 'BTP'], 'ex_BTP_PPC(than)': [k for k in P if k not in ('BTP', 'PPC')],
        'gas_POW_only': ['POW'], 'NT2_own_avg': None}
for name, ks in sets.items():
    for agg in (('median', st.median), ('mean', st.mean)) if ks and len(ks) > 1 else (('-', None),):
        m = g['NT2_EBITM'] if ks is None else (agg[1](P[k] for k in ks) if agg[1] else P[ks[0]])
        lnst = m * REV_N * 0.8 + FIN
        s = run(shift=lnst - 800)
        print(f"{name:18s} {agg[0]:6s} ebitm {m:.2%} lnst {lnst:,.0f}: " + R2.fmt(s, PX))
