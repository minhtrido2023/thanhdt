"""Biên gộp ±1/±2pp quanh A7/B7 theo Ke (bản sao logic out_r7_margin_band trong model.py r12, dòng ~638-642).
Chạy: /home/trido/thanhdt/wc_venv/bin/python margin_ke.py"""
import os, sys, io, contextlib, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "dgc_valuation_20261029_r12"))
with contextlib.redirect_stdout(io.StringIO()):
    import model as M
gmo = {k: list(v["gm"]) for k, v in M.SCN.items()}
def at(ke, dpp, cfg):
    try:
        for k in M.SCN: M.SCN[k]["gm"] = [g + dpp for g in gmo[k]]
        return M.per_scn(dict(cfg, rf=ke - 0.075))[0]
    finally:
        for k in M.SCN: M.SCN[k]["gm"] = list(gmo[k])
rows = [dict(ke=round(ke * 100, 1), dpp=d, ev_A7=at(ke, d / 100, M.CFG_A7), ev_B7=at(ke, d / 100, M.CFG_B7)) for ke in (0.125, 0.13, 0.135, 0.149) for d in (-2, -1, 0, 1, 2)]
df = pd.DataFrame(rows); df.to_csv(os.path.join(HERE, "out_margin_ke.csv"), index=False); print(df.to_string(index=False))
c = df[df.ke == 14.9].set_index("dpp"); assert (c.ev_A7[-2], c.ev_A7[2]) == (29345, 35017), c   # đối chứng out_r7_margin_band.csv
