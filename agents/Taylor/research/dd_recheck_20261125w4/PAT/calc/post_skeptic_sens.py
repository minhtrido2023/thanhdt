"""PAT rev6 — độ nhạy bổ sung sau skeptic r1 (không đổi base). python3 -I post_skeptic_sens.py"""
import os, sys, runpy, io, contextlib, json
HERE = os.path.dirname(os.path.abspath(__file__))
with contextlib.redirect_stdout(io.StringIO()):
    G = runpy.run_path(os.path.join(HERE, 'model_r6.py'))
M = G['M']; value_d4 = G['value_d4']; base = G['base']; mix = G['mix']; _v = G['_v']
M.value = value_d4
out = {}
out['g0'] = mix(g=0.0)['center']; out['g1'] = mix(g=0.01)['center']
# đình chỉ lò P4 6 tháng trong 2027 (ước lượng cơ học): mất ½ EBIT 2027 sau thuế, chi phí cố định SG&A 28 tỷ/năm vẫn chịu (đã nằm trong EBIT)
M.value = _v
R = M.run(cell='D'); d = M.base_path(R, detail=True)
e27 = d['ebit27']
loss6m = 0.5 * e27 * 0.95 * 0.94 / 1.135 ** 0.63
out['ebit27_base_path'] = e27; out['loss_6m_pv'] = loss6m
M.value = value_d4
out['dinhchi_6thang'] = mix(oneoff=-loss6m)['center']
M.value = _v
for k, v in out.items():
    print(f"{k}: {v:,.1f}" + (f" ({v/base-1:+.2%}) sau CK {v*0.9:,.0f}" if k in ('g0','g1','dinhchi_6thang') else ''))
json.dump(out, open(os.path.join(HERE, 'post_skeptic_sens_out.json'), 'w'), indent=1)
