"""Do nhay r ngoai luat (chi thong tin, khong doi headline): import model.py roi chay grid o r khac."""
import contextlib, io, runpy
with contextlib.redirect_stdout(io.StringIO()): g = runpy.run_path('model.py')
ck = g['L250']['ck']['5000000000']
for r in (0.08, 0.10, 0.115, 0.135):
    G = g['grid'](r); print(f"r={r:.3f} center_post={G['center']*(1-ck):,.0f} p10={G['p10']*(1-ck):,.0f} p90={G['p90']*(1-ck):,.0f}")
