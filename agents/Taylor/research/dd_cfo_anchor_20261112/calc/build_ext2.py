# -*- coding: utf-8 -*-
"""build_ext2.py — thành phần bổ sung cho panel dd_blend (job Taylor_20261111_095819, dd_cfo_anchor).

Mỗi dòng panel (mã, as-of, fin_time): lịch sử quý của cùng mã, mỗi quý lấy bản phát hành mới nhất có
time <= fin_time (PIT; build_panel đã assert fin_time <= as-of). Chuỗi năm TTM j=0..4 kết thúc ở quý
q0-4j: CFO, capex (=-CF_Invest), LNST, doanh thu. NWC (không gồm nợ vay NH) tại q0 và q0-12.
Nhãn ngắn TR3/TR6 = Close_{t+N}/Close_t (Close điều chỉnh, như build_panel). ADV60 = TB Price*Volume
60 phiên <= as-of (chỉ để kiểm độ bền thanh khoản). Không BQ (cache local). Không profit_*.
Run: $DNA_PYEXE build_ext2.py -> ../out/ext2.parquet
"""
import os, json
import numpy as np, pandas as pd, duckdb
WC = "/home/trido/thanhdt/WorkingClaude"
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "out")
PANEL = os.path.join(HERE, "..", "..", "dd_blend_20261111", "out", "panel.parquet")
p = pd.read_parquet(PANEL).reset_index(drop=True)
c = duckdb.connect()
cols = ["CF_OA_P0", "CF_Invest_P0", "NP_P0", "Revenue_P0", "Inventory_P0", "AR_P0", "StLiab_P0",
        "StDebt_P0", "ROIC3Y", "EBITDA_P0", "EBITM_P0", "totalAsset_P0", "ROE3Y"]
f = c.execute(f"SELECT ticker, CAST(time AS TIMESTAMP) AS time, quarter, {','.join(cols)} "
              f"FROM read_parquet('{WC}/data/bq_cache/ticker_financial.parquet')").df()
f["time"] = pd.to_datetime(f.time)
f = f.sort_values(["ticker", "time"]).drop_duplicates(["ticker", "time"], keep="last").reset_index(drop=True)
f["qp"] = pd.PeriodIndex(f.quarter, freq="Q")
fby = {t: g.reset_index(drop=True) for t, g in f.groupby("ticker")}
px = c.execute(f"""SELECT ticker, CAST(time AS DATE) AS time, Price, Close, Volume
    FROM read_parquet('{WC}/data/bq_cache/ticker/*.parquet')
    WHERE time >= DATE '2015-06-01' AND Price > 0 AND Close > 0""").df()
px["time"] = pd.to_datetime(px.time)
px = px.sort_values(["ticker", "time"]).reset_index(drop=True)
LAST = px.time.max()
pby = {t: g.reset_index(drop=True) for t, g in px.groupby("ticker")}

out = []
for i, (tk, ft, a) in enumerate(zip(p.ticker, pd.to_datetime(p.fin_time), pd.to_datetime(p["asof"]))):
    rec = {"i": i}
    g = fby.get(tk)
    if g is not None:
        h = g[g.time <= ft]
        if len(h) and h.time.iloc[-1] == ft:
            hq = h.drop_duplicates("qp", keep="last").set_index("qp")
            q0 = h.qp.iloc[-1]
            L = hq.loc[q0]
            for k in ("ROIC3Y", "ROE3Y", "EBITDA_P0", "EBITM_P0", "totalAsset_P0"):
                rec[k] = float(L[k]) if pd.notna(L[k]) else np.nan
            def ysum(col, j):
                qs = [q0 - 4 * j - k for k in range(4)]
                if not all(q in hq.index for q in qs):
                    return np.nan
                v = hq.loc[qs, col].values.astype(float)
                return float(v.sum()) if np.isfinite(v).all() else np.nan
            for j in range(5):
                rec[f"cfo_y{j}"] = ysum("CF_OA_P0", j)
                cfi = ysum("CF_Invest_P0", j)
                rec[f"cpx_y{j}"] = -cfi if cfi == cfi else np.nan
                rec[f"ni_y{j}"] = ysum("NP_P0", j)
                rec[f"rev_y{j}"] = ysum("Revenue_P0", j)
            def nwc(q):
                if q not in hq.index:
                    return np.nan
                r = hq.loc[q]
                sd = r.StDebt_P0 if pd.notna(r.StDebt_P0) else 0.0
                v = r.Inventory_P0 + r.AR_P0 - (r.StLiab_P0 - sd)
                return float(v) if pd.notna(v) else np.nan
            rec["nwc0"] = nwc(q0); rec["nwc12"] = nwc(q0 - 12)
    pp = pby.get(tk)
    if pp is not None:
        t0 = pp[pp.time == a]
        if len(t0):
            C0 = float(t0.Close.iloc[0]); j0 = t0.index[0]
            past = pp.iloc[max(0, j0 - 59): j0 + 1]
            rec["adv60"] = float((past.Price * past.Volume).mean())
            fut = pp[pp.time >= a]; ftm = fut.time.values; cl = fut.Close.values / C0
            for N in (3, 6):
                end = a + pd.DateOffset(months=N)
                m = ftm <= np.datetime64(end)
                full = (LAST >= end) and (ftm[m][-1] >= np.datetime64(end - pd.Timedelta(days=20)))
                rec[f"full{N}"] = bool(full)
                rec[f"TR{N}"] = float(cl[m][-1]) if full else np.nan
    out.append(rec)
E = pd.DataFrame(out).set_index("i").reindex(range(len(p)))
for N in (3, 6):
    E[f"full{N}"] = E[f"full{N}"].fillna(False).astype(bool)
E.to_parquet(os.path.join(OUT, "ext2.parquet"))
meta = {"n": len(E), "n_cfo_y0": int(E.cfo_y0.notna().sum()), "n_cfo_y2": int(E.cfo_y2.notna().sum()),
        "n_cfo_y4": int(E.cfo_y4.notna().sum()), "n_full3": int(E.full3.sum()), "n_full6": int(E.full6.sum()),
        "last_px": str(LAST.date())}
json.dump(meta, open(os.path.join(OUT, "ext2_meta.json"), "w"), indent=1)
print(meta)
