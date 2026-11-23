"""r3: doc tam tai 2 dau dai Ke noi dia 12,3% / 13,4% (V1/D4, chi bao kem). Chay: python3 ke_band_r3.py"""
import runpy, io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path('model_r3.py')
k = 1 - g['ck5']
for r in (0.123, 0.134, 0.135):
    G = g['grid'](r); print(f"r={r:.3f}: tam {G['center']*k:,.0f} P10 {G['p10']*k:,.0f} P90 {G['p90']*k:,.0f}")
