"""Hieu ung truot cua so khi co Q4/26 (co hoc): them quy Q4/26 voi LNST gia dinh; von chu = Q3 + LNST; XDCB/BDS giu Q3 (uoc luong)."""
import json, os, importlib.util, io, contextlib
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('c', os.path.join(HERE, 'calc_rev4.py')); m = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()): spec.loader.exec_module(m)
base = m.scen(*m.model()[:3])[0]
for npq in (-50, 35, 120):
    m.q_raw['2026Q4'] = npq; m.EQ['2026Q4'] = m.EQ['2026Q3'] + npq
    m.A['cip_known_bn']['2026Q4'] = m.CIP; m.A['re_wip_known_bn']['2026Q4'] = m.REW
    m.cip_lin, m.cip_step = m.interp(m.A['cip_known_bn']); m.re_lin, m.re_step = m.interp(m.A['re_wip_known_bn'])
    m.keys = sorted(m.q_raw); m.W = {'W12': ['2024Q1', '2026Q4'], 'W15': ['2023Q2', '2026Q4'], 'W20': ['2022Q1', '2026Q4']}
    old = m.gp.get('2026'); 
    c = m.scen(*m.model()[:3])[0]; print(f'LNST Q4/26 {npq:+d} ty: tam {c:.0f} ({c/base-1:+.1%})')
