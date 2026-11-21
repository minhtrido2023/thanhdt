"""Trích số cho báo cáo NĐT từ qtp_model_r3c.py (không sửa mô hình). Ghi figs/model_numbers.json."""
import json, os, sys
M = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/qtp_r3_envcapex_20261120"
sys.path.insert(0, M)
import qtp_model_r3c as q
out = {}
out["center_pre"] = q.center(wp=q.W_F); out["center_post"] = out["center_pre"] * 0.9
out["rate"] = {bp: q.center(wp=q.W_F, rr=q.R0 + bp / 1e4, i=0.09 + bp / 1e4) for bp in (-100, -50, 0, 50, 100)}
out["P_pure_pre"] = {p: sum(w * (q.val_r2(k) + q.env_delta(k, **q.SCEN[p])[0]) for k, w in q.W_R2.items()) for p in q.SCEN}
out["grid_pre"] = {k: {p: q.val_r2(k) + q.env_delta(k, **q.SCEN[p])[0] for p in q.SCEN} for k in q.W_R2}
out["W_R2"] = q.W_R2
out["wgrid_post"] = {p0: q.center(wp=q.wgrid(p0)) * 0.9 for p0 in (0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6)}
cf = {}
for p in q.SCEN:
    rows = []
    for dps in (0, 900):
        cash = q.netcash
        for r in q.env_delta('base', **q.SCEN[p])[1]:
            y = r['y']
            if y > 2047: break
            base = q.npat_base('base', y) + q.DA[y] - 15
            cash += base + r['fcfe'] - dps * q.SH / 1000
            rows.append(dict(y=y, dps=dps, fcfe_base=round(base), dfcfe=round(r['fcfe']), total=round(base + r['fcfe']), cash=round(cash)))
    cf[p] = rows
out["cf"] = cf
out["R0"] = q.R0; out["SH"] = q.SH; out["netcash"] = q.netcash
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs", "model_numbers.json"), "w"), indent=1, default=float)
print(round(out["center_pre"]), round(out["center_post"]))
print({k: (round(v), round(v * .9)) for k, v in out["rate"].items()})
print({k: (round(v), round(v * .9)) for k, v in out["P_pure_pre"].items()})
print({k: {p: round(v) for p, v in d.items()} for k, d in out["grid_pre"].items()}, out["W_R2"])
print({k: round(v) for k, v in out["wgrid_post"].items()})
for p in cf:
    print(p, [(r['y'], r['total'], r['cash']) for r in cf[p] if r['dps'] == 900 and r['y'] in (2027, 2029, 2030, 2032, 2035, 2039, 2040, 2047)])
