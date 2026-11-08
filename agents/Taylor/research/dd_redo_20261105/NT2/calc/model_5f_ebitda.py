"""Kiem co so so sanh bien (job Taylor_20261107_172009). EBITM peer chua khau hao von dau tu ban dau (~4-12% DT);
NT2 da khau hao het may chinh tu cuoi 2025 (KH 556 -> 153/nam, REPORT dd_NT2_20261026 §2) => so EBIT dem 2 lan. So tren EBITDA.
BQ do 08/11/2026: EBITDA_P0 dong Q4 (TTM = ca nam) / tong Revenue_P0 4 quy, 2015-2025, nam du 4 quy."""
import statistics as st, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
o = json.load(open(os.path.join(HERE, 'model_5f_out.json')))
REV_N, m_ebit = o['rev_norm'], o['model_ebit_margin_implied']
DEP = 153  # KH con lai/nam = capex duy tri (gia dinh model_r2)
PEER = dict(POW=0.195, PPC=0.062, QTP=0.247, HND=0.223, PGV=0.208, BTP=0.092)  # TB bien EBITDA
NT2_OWN = 0.201
m_ebitda = m_ebit + DEP / REV_N
print(f"model: EBIT op {m_ebit:.2%} + KH {DEP/REV_N:.2%} = EBITDA {m_ebitda:.2%} (DT chuan hoa {REV_N:,.0f}); NT2 TB 2015-25 {NT2_OWN:.1%}")
for name, ks in {'all6': list(PEER), 'ex_PPC(EBITDA<EBIT, du lieu la)': [k for k in PEER if k != 'PPC'],
                 'ex_PPC_BTP': [k for k in PEER if k not in ('PPC', 'BTP')], 'POW_only': ['POW']}.items():
    v = [PEER[k] for k in ks]
    print(f"{name:34s} median {st.median(v):.1%} mean {st.mean(v):.1%} | model - median {m_ebitda - st.median(v):+.1%}")
