"""Kiem phu (sau LOCK, khong doi gia dinh): tam khi w XAU tang, CO_SO/TOT chia phan con lai theo ti le 0,45:0,275 — vi solver chinh cham bien 0,55."""
import runpy, sys, os, io, contextlib
HERE = os.path.dirname(os.path.abspath(__file__))
with contextlib.redirect_stdout(io.StringIO()):
    M = runpy.run_path(os.path.join(HERE, 'model_r3.py'))
for x in (0.55, 0.70, 0.80, 0.90, 1.0):
    rest = 1 - x; wov = {'XAU': x, 'CO_SO': rest * 0.45 / 0.725, 'TOT': rest * 0.275 / 0.725}
    print(f"w XAU {x:.2f}: tam {M['run'](M['BASE_CFG'], M['PX'], M['D'], wov=wov)[0]['center']:,.0f}")
x = M['solve'](lambda x: M['run'](M['BASE_CFG'], M['PX'], M['D'], wov={'XAU': x, 'CO_SO': (1 - x) * 0.45 / 0.725, 'TOT': (1 - x) * 0.275 / 0.725})[0]['center'], 0.0, 1.0)
print(f"w XAU ngu y (ti le CO_SO:TOT giu 0,45:0,275): {x:.3f}")
