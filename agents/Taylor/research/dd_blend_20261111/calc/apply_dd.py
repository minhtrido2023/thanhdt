# -*- coding: utf-8 -*-
"""apply_dd.py — CHỈ BÁO CÁO, KHÔNG ghi sổ: V_ngắn / V_dài / V(w) per share cho 25 mã sổ DD
(mike/agents/Mike/work/dd_vn_calib/latest_zones.json) tại as-of 2026-11-10, so với tâm DD.
Per share = V (VND) / OShares của dòng fin mới nhất (chưa đối chiếu sự kiện CP sau fin_time — ghi chú).
Run: $DNA_PYEXE apply_dd.py -> ../out/apply_dd.csv
"""
import os, sys, json
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import dcf, OUT
WC = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WC)
import duckdb
import dcf_valuation as D
D.pin_oshares_source_fin(__file__)
NPC = ["NP_P0", "NP_P1", "NP_P2", "NP_P3"]
a = pd.Timestamp("2026-11-10")
z = json.load(open(f"{WC}/mike/agents/Mike/work/dd_vn_calib/latest_zones.json"))
fin = D._load_financials()
roe = duckdb.connect().execute(f"SELECT ticker, CAST(time AS TIMESTAMP) AS time, ROE3Y, ROE_Trailing FROM read_parquet('{WC}/data/bq_cache/ticker_financial.parquet')").df()
roe["time"] = pd.to_datetime(roe["time"])
r = D.discount_rate(a, D.ERP); gT0 = D.terminal_growth_mode(a, None, D.ERP); gT = gT0 if r > gT0 else r - 0.01
rows = []
for e in z:
    tk = e["ticker"]; g = fin[(fin.ticker == tk) & (fin.time <= a)]
    o = {"ticker": tk, "dd_center": e["center"], "dd_low": e.get("low"), "dd_high": e.get("high"),
         "price_ref": e.get("price_ref"), "dd_date": e.get("dd_date")}
    if len(g) < 4 or D.is_financial(tk, a):
        o["note"] = "tai chinh/thieu BCTC"; rows.append(o); continue
    last = g.iloc[-1]; osh = float(last.OShares)
    ann = D._annual_series(g, NPC); g_raw, _ = D.recency_weighted_growth(ann)
    if np.isnan(g_raw): g_raw = gT
    gexp = gT + D.GROWTH_SHRINK * (float(np.clip(g_raw, D.G_EXPLICIT_FLOOR, D.G_EXPLICIT_CAP)) - gT)
    rr = roe[(roe.ticker == tk) & (roe.time <= a)].sort_values("time").iloc[-1]
    R = rr.ROE3Y if pd.notna(rr.ROE3Y) else rr.ROE_Trailing
    ni = float(np.median(ann[:3]))
    vs = float(dcf(np.array([ni]), gexp, gT, r, np.clip(gexp / R, 0, 1), np.clip(gT / R, 0, 1))[0]) / osh if (ni > 0 and R > 0) else np.nan
    vs = vs if vs > 0 else np.nan
    res = D.fair_value(tk, a, price=e.get("price_ref"), fin=g)
    vl = res["fair_value_ps"] if res["ok"] else np.nan
    o.update({"fin_time": str(last.time.date()), "NI_norm_bn": ni / 1e9, "ROE": float(R), "g_exp": gexp,
              "V_ngan": vs, "V_dai": vl, "eng_reason": None if res["ok"] else res["reason"],
              "D_log": float(abs(np.log(vs / vl))) if (vs > 0 and vl > 0) else np.nan})
    for w in (0.5, 0.8):
        o[f"V_w{w}"] = (w * vs + (1 - w) * vl) if (vs > 0 and vl > 0) else np.nan
    rows.append(o)
b = pd.DataFrame(rows)
b["V_hai_hoa"] = b["V_w0.5"].where(b["V_w0.5"].notna(), b.V_ngan)   # V_dài không xác định ⇒ dùng V_ngắn + cờ
b["src"] = np.where(b["V_w0.5"].notna(), "w0.5", np.where(b.V_ngan.notna(), "chi_V_ngan", "khong"))
b["hh_over_dd"] = b.V_hai_hoa / b.dd_center
b["hh_over_px"] = b.V_hai_hoa / b.price_ref
b["dd_over_px"] = b.dd_center / b.price_ref
b["lech_gt30"] = (b.hh_over_dd - 1).abs() > 0.30
b.to_csv(os.path.join(OUT, "apply_dd.csv"), index=False)
pd.set_option("display.width", 250)
print(b[["ticker", "price_ref", "dd_center", "V_ngan", "V_dai", "V_w0.5", "V_w0.8", "V_hai_hoa", "src", "D_log", "hh_over_dd", "dd_over_px", "hh_over_px", "eng_reason", "fin_time"]].round(2).to_string())
ok = b.dropna(subset=["V_hai_hoa"])
print("n", len(b), "co V_hh", len(ok), "lech>30%", int(ok.lech_gt30.sum()),
      "med hh/dd", float(np.exp(np.log(ok.hh_over_dd).median())),
      "IQR log hh/px", float(np.subtract(*np.percentile(np.log(ok.hh_over_px), [75, 25]))),
      "IQR log dd/px", float(np.subtract(*np.percentile(np.log(b.dd_over_px.dropna()), [75, 25]))))
