# -*- coding: utf-8 -*-
"""a_engine_baseline.py — đối chứng A: FV engine production (dcf_valuation.fair_value, domestic_v2) tại cuối quý.
Chỉ đọc cache local; KHÔNG sửa engine. PIT: fair_value lọc fin.time<=asof; OShares=fin (như calib 11/11 — cột này
là TRAP restate, giữ nguyên để tái lập đúng đối chứng). Out: ../out/engine_A.parquet (ticker, asof, P0, FV, ok)."""
import os, sys
import numpy as np, pandas as pd, duckdb
WC = "/home/trido/thanhdt/WorkingClaude"; HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WC)
import dcf_valuation as D
D.pin_oshares_source_fin(__file__)
assert D.RATE_FRAME == "domestic_v2", D.RATE_FRAME
c = duckdb.connect()
px = c.execute(f"""SELECT ticker, CAST(time AS DATE) AS time, Price, Close FROM read_parquet('{WC}/data/bq_cache/ticker/*.parquet')
    WHERE Price > 0 AND Close > 0""").df()
px["time"] = pd.to_datetime(px.time)
dates = pd.Series(sorted(px.time.unique()))
q = dates.groupby(dates.dt.to_period("Q")).max()
ASOFS = [d for p, d in q.items() if pd.Period("2014Q1") <= p <= pd.Period("2026Q3")]
uni = c.execute(f"""SELECT ticker, CAST(time AS DATE) AS time FROM read_parquet('{WC}/data/bq_cache/universe_pit/*.parquet') WHERE in_universe""").df()
uni["time"] = pd.to_datetime(uni.time)
uni_set = uni.groupby("time").ticker.apply(set).to_dict()
fin = D._load_financials(); D._load_routes(); D._load_icb_map()
fin_by = {t: g for t, g in fin.groupby("ticker")}
pxa = px[px.time.isin(ASOFS)].set_index(["time", "ticker"]).Price
rows = []
os.chdir(HERE)
for a in ASOFS:
    for tk in sorted(uni_set.get(a, set())):
        g = fin_by.get(tk)
        if g is None or (a, tk) not in pxa.index:
            continue
        P0 = float(pxa.loc[(a, tk)])
        try:
            res = D.fair_value(tk, a, price=P0, fin=g)
        except Exception as e:
            res = {"ok": False, "reason": "EXC " + type(e).__name__}
        rows.append({"ticker": tk, "asof": a, "P0": P0, "ok": bool(res["ok"]), "reason": res.get("reason"),
                     "FV": res.get("fair_value_ps") if res["ok"] else np.nan})
    print(a.date(), len(rows), flush=True)
pd.DataFrame(rows).to_parquet(os.path.join(HERE, "..", "out", "engine_A.parquet"))
print("done")
