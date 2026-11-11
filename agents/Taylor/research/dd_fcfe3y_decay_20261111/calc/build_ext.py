# -*- coding: utf-8 -*-
"""build_ext.py — thành phần dòng tiền bổ sung cho panel dd_blend (job Taylor_20261111_051016).

Ghép mỗi dòng panel (mã, fin_time) với dòng ticker_financial CÙNG time (PIT: fin_time ≤ as-of đã
được build_panel assert). Lịch sử quý dựng từ các dòng fin có time ≤ fin_time của cùng mã.
Không đọc giá. Không BQ (chỉ cache local). Run: $DNA_PYEXE build_ext.py -> ../out/ext.parquet
"""
import os, json
import numpy as np, pandas as pd, duckdb
WC = "/home/trido/thanhdt/WorkingClaude"
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "out")
PANEL = os.path.join(HERE, "..", "..", "dd_blend_20261111", "out", "panel.parquet")
p = pd.read_parquet(PANEL).reset_index(drop=True)
cols = ["CF_OA_P0", "CF_OA_P1", "CF_OA_P2", "CF_OA_P3", "CF_Invest_P0", "CF_Invest_P1", "CF_Invest_P2",
        "CF_Invest_P3", "CF_OA_3Y", "CF_Invest_3Y", "CF_OA_5Y", "CF_Invest_5Y", "EBITDA_P0", "EBITM_P0",
        "Revenue_P0", "Revenue_P1", "Revenue_P2", "Revenue_P3", "FAssetTurn_P0", "totalAsset_P0",
        "Inventory_P0", "AR_P0", "StLiab_P0", "NP_P0", "NP_P1", "NP_P2", "NP_P3", "Cash_P0"]
f = duckdb.connect().execute(f"SELECT ticker, CAST(time AS TIMESTAMP) AS time, quarter, {','.join(cols)} "
                             f"FROM read_parquet('{WC}/data/bq_cache/ticker_financial.parquet')").df()
f["time"] = pd.to_datetime(f.time)
f = f.sort_values(["ticker", "time"]).drop_duplicates(["ticker", "time"], keep="last").reset_index(drop=True)
f["qp"] = pd.PeriodIndex(f.quarter, freq="Q")
by = {t: g.reset_index(drop=True) for t, g in f.groupby("ticker")}
out = []
for i, (tk, ft) in enumerate(zip(p.ticker, pd.to_datetime(p.fin_time))):
    g = by.get(tk); rec = {"i": i}
    if g is None:
        out.append(rec); continue
    h = g[g.time <= ft]
    if not len(h) or h.time.iloc[-1] != ft:
        out.append(rec); continue
    L = h.iloc[-1]
    for c in cols:
        rec[c] = float(L[c]) if pd.notna(L[c]) else np.nan
    rec["fin_quarter"] = str(L.quarter)
    # chuỗi quý liên tục kết thúc ở quý của dòng cuối (mỗi quý lấy bản phát hành mới nhất ≤ fin_time)
    hq = h.drop_duplicates("qp", keep="last").set_index("qp")
    q0 = L.qp
    def qsum(col, k):
        qs = [q0 - j for j in range(k)]
        if not all(q in hq.index for q in qs):
            return np.nan
        v = hq.loc[qs, col].values.astype(float)
        return float(v.sum()) if np.isfinite(v).all() else np.nan
    rec["cfo12q"] = qsum("CF_OA_P0", 12); rec["cfi12q"] = qsum("CF_Invest_P0", 12)
    q4 = q0 - 4
    if q4 in hq.index:
        r4 = hq.loc[q4]
        rec["inv_l4"] = float(r4.Inventory_P0) if pd.notna(r4.Inventory_P0) else np.nan
        rec["ar_l4"] = float(r4.AR_P0) if pd.notna(r4.AR_P0) else np.nan
        rec["stl_l4"] = float(r4.StLiab_P0) if pd.notna(r4.StLiab_P0) else np.nan
        rec["cash_l4"] = float(r4.Cash_P0) if pd.notna(r4.Cash_P0) else np.nan
    # tháng từ cuối năm tài chính gần nhất chứa trong trường 3Y (trường 3Y chỉ đổi ở dòng Q4)
    yq = [q for q in hq.index if q <= q0 and q.quarter == 4]
    rec["m_since_fy"] = (q0.year - yq[-1].year) * 12 + (q0.quarter - 4) * 3 if yq else np.nan
    out.append(rec)
E = pd.DataFrame(out).set_index("i").reindex(range(len(p)))
# kiểm vintage: CF_OA_3Y/CF_Invest_3Y của cache hiện tại == panel
m = E.CF_OA_3Y.notna() & p.cfoa3.notna()
dev3 = float(np.nanmax(np.abs(E.CF_OA_3Y[m] / p.cfoa3[m] - 1)))
nmis = int((E.CF_OA_3Y.isna() & p.cfoa3.notna()).sum())
E.to_parquet(os.path.join(OUT, "ext.parquet"))
meta = {"panel_md5_prefix": None, "n": len(E), "n_matched": int(E.CF_OA_3Y.notna().sum()),
        "vintage_maxdev_CF_OA_3Y": dev3, "n_unmatched_with_cfoa3": nmis,
        "n_cfo12q": int(E.cfo12q.notna().sum())}
json.dump(meta, open(os.path.join(OUT, "ext_meta.json"), "w"), indent=1)
print(meta)
