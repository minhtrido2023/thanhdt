# -*- coding: utf-8 -*-
"""a_engine_total.py — đối chứng A_pit (sửa lỗi skeptic #4): chạy engine production `dcf_valuation.fair_value` với oshares=1
⇒ nhận TỔNG giá trị vốn chủ (không phụ thuộc cơ sở cổ phiếu); V/P sẽ tính = FV_total / MC panel V2 (c_models2.py).
Lưu luôn g_explicit, g_terminal, r, LN 3 năm để dựng ablation A_RI. KHÔNG sửa engine. Out: ../out/engine_A2.parquet."""
import os, sys
import numpy as np, pandas as pd, duckdb
WC = "/home/trido/thanhdt/WorkingClaude"; HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WC)
import dcf_valuation as D
D.pin_oshares_source_fin(__file__)
assert D.RATE_FRAME == "domestic_v2", D.RATE_FRAME
pan = pd.read_parquet(os.path.join(HERE, "..", "out", "panel2.parquet"), columns=["ticker", "ym", "time", "in_universe", "src"])
pan = pan[pan.in_universe & (pan.src == "BQ") & (pan.ym >= "2014-01")]
pan = pan[pd.PeriodIndex(pan.ym, freq="M").month.isin([3, 6, 9, 12])]
fin = D._load_financials(); D._load_routes(); D._load_icb_map()
fin_by = {t: g for t, g in fin.groupby("ticker")}
rows = []; os.chdir(HERE)
for i, r in enumerate(pan.itertuples()):
    g = fin_by.get(r.ticker)
    if g is None:
        continue
    try:
        res = D.fair_value(r.ticker, r.time, price=None, oshares=1.0, fin=g)
    except Exception as e:
        res = {"ok": False, "reason": "EXC " + type(e).__name__}
    ok = bool(res["ok"]); an = res.get("annual_np") or []
    rows.append({"ticker": r.ticker, "ym": r.ym, "ok": ok, "reason": (res.get("reason") or "")[:40], "FV_total": res.get("fair_value_ps") if ok else np.nan,
                 "g_exp": res.get("g_explicit"), "g_T": res.get("g_terminal"), "r": res.get("discount_rate"),
                 "np3": float(np.mean(an[:3])) if ok and len(an) else np.nan, "base_fcfe": res.get("base_fcfe_vnd")})
    if i % 4000 == 0:
        print(i, len(pan), flush=True)
pd.DataFrame(rows).to_parquet(os.path.join(HERE, "..", "out", "engine_A2.parquet")); print("done", len(rows))
