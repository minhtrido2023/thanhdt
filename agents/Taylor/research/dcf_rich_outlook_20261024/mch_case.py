"""Case MCH: phân rã DCF 2026-10-23 + quỹ đạo 8 quý (NP, biên, vốn lưu động, CFO/NP)."""
import sys, numpy as np, pandas as pd, duckdb
WD = "/home/trido/thanhdt/WorkingClaude"; sys.path.insert(0, WD)
import dcf_valuation as dv
P = 141900; A = "2026-10-23"
r = dv.fair_value("MCH", A, price=P)
print({k: r[k] for k in ("fair_value_ps", "margin_of_safety", "base_fcfe_vnd", "g_explicit_raw", "g_explicit", "g_terminal", "discount_rate", "oshares", "growth_points", "annual_np")})
osh, rr, gT = r["oshares"], r["discount_rate"], r["g_terminal"]
fv = lambda base, g, gt=gT, rate=rr: dv._fv_per_share(base, g, gt, rate, osh)
c = duckdb.connect()
f = c.execute(f"""SELECT time,quarter,NP_P0,NP_P4,Revenue_P0,GPM_P0,NPM_P0,CF_OA_P0,CF_Invest_P0,DSO_P0,DIO_P0,CashCycle_P0,ROE5Y,ROE_Trailing,Cash_P0,totalAsset_P0
  FROM read_parquet('{WD}/data/bq_cache/ticker_financial.parquet') WHERE ticker='MCH' ORDER BY time""").df().drop_duplicates("quarter", keep="last")
f = f.tail(9).copy(); f["NP_yoy"] = f.NP_P0 / f.NP_P4 - 1; f["CFO_NP"] = f.CF_OA_P0 / f.NP_P0
f["NP_ttm"] = f.NP_P0.rolling(4).sum()
pd.set_option("display.width", 250)
cols = ["quarter", "NP_P0", "NP_yoy", "Revenue_P0", "GPM_P0", "NPM_P0", "CFO_NP", "DSO_P0", "DIO_P0", "CashCycle_P0", "ROE_Trailing", "Cash_P0", "totalAsset_P0"]
t = f[cols].copy()
for k in ("NP_P0", "Revenue_P0", "Cash_P0", "totalAsset_P0"): t[k] = (t[k] / 1e9).round(0)
print(t.round(3).to_string(index=False))
np_ttm = f.NP_P0.tail(4).sum(); print("NP TTM bn", round(np_ttm / 1e9), "P/E", round(P * osh / np_ttm, 1), "base_fcfe/NP_ttm", round(r["base_fcfe_vnd"] / np_ttm, 2))
# độ nhạy giả định
print("FV nếu base FCFE = NP TTM (không trừ tái đầu tư):", round(fv(np_ttm, r["g_explicit"])))
print("FV nếu g_exp = 15%:", round(fv(r["base_fcfe_vnd"], 0.15)), " | base=NP TTM & g 15%:", round(fv(np_ttm, 0.15)))
print("FV nếu r = 12%:", round(fv(r["base_fcfe_vnd"], r["g_explicit"], rate=0.12)))
# g_exp (5 năm) ngầm định để FV = giá
lo, hi = -0.5, 1.5
for _ in range(80):
    m = (lo + hi) / 2; lo, hi = (m, hi) if fv(r["base_fcfe_vnd"], m) < P else (lo, m)
print("g_exp 5 năm ngầm định giá 141.900 (base FCFE hiện tại):", round(m, 4))
lo, hi = -0.5, 1.5
for _ in range(80):
    m = (lo + hi) / 2; lo, hi = (m, hi) if fv(np_ttm, m) < P else (lo, m)
print("g_exp 5 năm ngầm định nếu base = NP TTM:", round(m, 4))
