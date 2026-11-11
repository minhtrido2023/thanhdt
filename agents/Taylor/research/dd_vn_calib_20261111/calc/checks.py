# -*- coding: utf-8 -*-
"""checks.py — (1) PIT: FV tính với fin CẮT tại as-of == FV trong panel (engine không nhìn dữ liệu sau
as-of); (2) cầu nối: FV engine hôm nay vs tâm DD (sổ dd_price_zones, bản Mike trích 11/11).
Run: $DNA_PYEXE checks.py -> ../out/checks.json
"""
import os, sys, json
import numpy as np, pandas as pd
WC = "/home/trido/thanhdt/WorkingClaude"
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "out")
sys.path.insert(0, WC)
import dcf_valuation as D
D.pin_oshares_source_fin(__file__)
os.chdir(HERE)
p = pd.read_parquet(os.path.join(OUT, "panel.parquet"))
p = p[p["ok"] & (p["rating"] <= 3)]
fin = D._load_financials()
smp = p.sample(80, random_state=20261111)
dev = []
for r in smp.itertuples():
    g = fin[(fin.ticker == r.ticker) & (fin["time"] <= r.asof)]          # cắt cứng tại as-of
    fv = D.fair_value(r.ticker, r.asof, price=r.P0, fin=g)["fair_value_ps"]
    dev.append(abs(fv / r.FV - 1))
out = {"pit_sample": len(dev), "pit_max_rel_dev": float(max(dev))}
assert out["pit_max_rel_dev"] < 1e-12, out
# cầu nối DD
z = json.load(open(f"{WC}/mike/agents/Mike/work/dd_vn_calib/latest_zones.json"))
asof = pd.Timestamp("2026-11-10")
br = []
for e in z:
    res = D.fair_value(e["ticker"], asof, price=e.get("price_ref"))
    br.append({"ticker": e["ticker"], "dd_center": e["center"], "price_ref": e.get("price_ref"),
               "engine_fv": res.get("fair_value_ps") if res["ok"] else None, "engine_reason": res.get("reason")})
b = pd.DataFrame(br)
b["dd_over_engine"] = b.dd_center / b.engine_fv
b["engine_over_px"] = b.engine_fv / b.price_ref
b["dd_over_px"] = b.dd_center / b.price_ref
okb = b.dropna(subset=["engine_fv"])
out.update({"bridge_n": len(b), "bridge_engine_ok": len(okb),
            "bridge_med_dd_over_engine": float(np.exp(np.log(okb.dd_over_engine).median())),
            "bridge_med_engine_over_px": float(np.exp(np.log(okb.engine_over_px).median())),
            "bridge_med_dd_over_px": float(np.exp(np.log(b.dd_over_px.dropna()).median())),
            "bridge_iqr_log_engine_over_px": float(np.subtract(*np.percentile(np.log(okb.engine_over_px), [75, 25]))),
            "bridge_iqr_log_dd_over_px": float(np.subtract(*np.percentile(np.log(b.dd_over_px.dropna()), [75, 25])))})
b.to_csv(os.path.join(OUT, "bridge_dd_vs_engine.csv"), index=False)
json.dump(out, open(os.path.join(OUT, "checks.json"), "w"), indent=1)
print(json.dumps(out, indent=1)); print(b.round(2).to_string())
