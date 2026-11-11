# -*- coding: utf-8 -*-
"""build_panel.py — PIT panel (mã, as-of quý) : FV engine production + đường giá tương lai.
Job Taylor_20261111_032615. Chỉ đọc cache local data/bq_cache (không gọi BQ, không sửa engine).

PIT: fair_value() lọc fin.time <= asof (time = ngày vendor nạp); rating merge_asof backward;
universe_pit tại đúng phiên as-of; DT5G merge_asof backward. Không dùng profit_*.
Đường giá tương lai CHỈ dùng làm nhãn chấm điểm (không vào FV).
Run: $DNA_PYEXE build_panel.py   -> ../out/panel.parquet
"""
import os, sys, json
import numpy as np, pandas as pd
WC = "/home/trido/thanhdt/WorkingClaude"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "out")
sys.path.insert(0, WC)
import duckdb
import dcf_valuation as D
import gdp_growth_vn as GDP
D.pin_oshares_source_fin(__file__)          # PIT: số CP theo quý, không đọc live
assert D.RATE_FRAME == "domestic_v2", D.RATE_FRAME
os.chdir(HERE)

HORIZONS = (12, 24, 36, 60)
c = duckdb.connect()
px = c.execute(f"""SELECT ticker, CAST(time AS DATE) AS time, Price, Close
    FROM read_parquet('{WC}/data/bq_cache/ticker/*.parquet')
    WHERE time >= DATE '2015-06-01' AND Price > 0 AND Close > 0""").df()
px["time"] = pd.to_datetime(px.time)
px = px.sort_values(["ticker", "time"]).reset_index(drop=True)
LAST = px.time.max()
dates = pd.Series(sorted(px.time.unique()))
q = dates.groupby(dates.dt.to_period("Q")).max()
ASOFS = [d for p, d in q.items() if pd.Period("2016Q1") <= p <= pd.Period("2025Q4")]

uni = c.execute(f"""SELECT ticker, CAST(time AS DATE) AS time FROM read_parquet('{WC}/data/bq_cache/universe_pit/*.parquet')
    WHERE in_universe""").df()
uni["time"] = pd.to_datetime(uni.time)
uni_set = uni.groupby("time").ticker.apply(set).to_dict()

rat = c.execute(f"SELECT ticker, CAST(time AS DATE) AS time, route, rating FROM read_parquet('{WC}/data/bq_cache/fa_ratings_8l.parquet')").df()
rat["time"] = pd.to_datetime(rat.time)
rat = rat.sort_values("time")
st = pd.read_parquet(f"{WC}/data/bq_cache/vnindex_5state_dt5g_live.parquet")[["time", "state"]]
st["time"] = pd.to_datetime(st.time); st = st.sort_values("time")

fin = D._load_financials()
D._load_routes(); D._load_icb_map()
fin_by = {t: g for t, g in fin.groupby("ticker")}
px_by = {t: g[["time", "Price", "Close"]].reset_index(drop=True) for t, g in px.groupby("ticker")}

rows = []
for a in ASOFS:
    us = uni_set.get(a, set())
    ra = rat[rat.time <= a].groupby("ticker").tail(1).set_index("ticker")
    gT_unc = D.terminal_growth(a) + GDP.longrun_real_gdp(a)
    st_a = st[st.time <= a].state.iloc[-1] if (st.time <= a).any() else None
    for tk in sorted(us):
        g = fin_by.get(tk); p = px_by.get(tk)
        if g is None or p is None:
            continue
        pt = p[p.time == a]
        if len(pt) == 0:
            continue
        P0 = float(pt.Price.iloc[0]); C0 = float(pt.Close.iloc[0])
        res = D.fair_value(tk, a, price=P0, fin=g)
        rr = ra.loc[tk] if tk in ra.index else None
        rec = {"ticker": tk, "asof": a, "P0": P0, "ok": res["ok"], "reason": res.get("reason"),
               "rating": (float(rr.rating) if rr is not None and pd.notna(rr.rating) else np.nan),
               "route": (rr.route if rr is not None else None), "dt5g": st_a, "gT_unc": gT_unc}
        if res["ok"]:
            last = g[g.time <= a].iloc[-1]
            sens = res["sensitivity"]
            vs = [res["fair_value_ps"]] + [v["fv"] for k, v in sens.items() if k != "base_fv_ps"]
            rec.update({"FV": res["fair_value_ps"], "FV_lo": min(vs), "FV_hi": max(vs),
                        "base_fcfe": res["base_fcfe_vnd"], "g_raw": res["g_explicit_raw"],
                        "g_exp": res["g_explicit"], "g_T": res["g_terminal"], "r": res["discount_rate"],
                        "osh": res["oshares"], "fin_time": res["fin_time"],
                        "cfoa5": float(last.CF_OA_5Y) if pd.notna(last.CF_OA_5Y) else np.nan,
                        "cfinv5": float(last.CF_Invest_5Y) if pd.notna(last.CF_Invest_5Y) else 0.0})
            assert pd.Timestamp(res["fin_time"]) <= a, "PIT violation"
            # đường giá tương lai, cùng khung với P0 (Price chưa đ/c tại as-of)
            fut = p[p.time >= a]
            path = P0 * fut.Close.values / C0
            ft = fut.time.values
            FV, lo, hi = rec["FV"], rec["FV_lo"], rec["FV_hi"]
            for N in HORIZONS:
                end = a + pd.DateOffset(months=N)
                m = ft <= np.datetime64(end)
                seg = path[m]
                full = (LAST >= end) and (len(ft) > 0) and (ft[m][-1] >= np.datetime64(end - pd.Timedelta(days=20)))
                tc = bool((seg <= FV).any()); t85 = bool((seg <= 0.85 * FV).any())
                rec[f"full{N}"] = full
                rec[f"touch{N}"] = tc if (full or tc) else np.nan
                rec[f"touch85_{N}"] = t85 if (full or t85) else np.nan
                rec[f"inzone_ever{N}"] = bool(((seg >= lo) & (seg <= hi)).any()) if full else np.nan
                rec[f"inzone_frac{N}"] = float(((seg >= lo) & (seg <= hi)).mean()) if full else np.nan
                rec[f"PN{N}"] = float(seg[-1]) if full else np.nan
        rows.append(rec)
    print(a.date(), len(rows), flush=True)

pan = pd.DataFrame(rows)
pan.to_parquet(os.path.join(OUT, "panel.parquet"))
json.dump({"n_rows": len(pan), "n_ok": int(pan.ok.sum()), "last_px": str(LAST.date()),
           "asofs": [str(x.date()) for x in ASOFS]}, open(os.path.join(OUT, "panel_meta.json"), "w"), indent=1)
print("done", len(pan), int(pan.ok.sum()))
