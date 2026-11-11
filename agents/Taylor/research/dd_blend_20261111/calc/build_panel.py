# -*- coding: utf-8 -*-
"""build_panel.py — panel PIT (mã, as-of quý) cho nghiên cứu dung hoà w (job Taylor_20261111_040113).

Khác dd_vn_calib_20261111:
 - SỬA share-basis: so sánh ở VND (giá trị vốn chủ) với vốn hoá MC0 = Price_asof × số CP fiinprox tại
   as-of (chuỗi theo ngày, neo ex-right). Fallback (mã ngoài fiinprox): quy giá về hệ CP của quý fin.
 - Lưu thành phần để tính V_dài (FCFE3y/5y) và V_ngắn (LNST chuẩn hoá × (1−g/ROE)) ở analyze.py.
 - Nhãn: TR_N = Close_{t+N}/Close_t (tổng lợi suất), minTR_N (chạm), MC_N giá-thuần × CP fiinprox t+N.
Giá CHỈ là nhãn chấm (MC0, đường giá sau as-of). Không profit_*. Chỉ cache local (không gọi BQ).
Run: $DNA_PYEXE build_panel.py -> ../out/panel.parquet
"""
import os, sys, json
import numpy as np, pandas as pd
WC = "/home/trido/thanhdt/WorkingClaude"
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "out")
sys.path.insert(0, WC)
import duckdb
import dcf_valuation as D
D.pin_oshares_source_fin(__file__)
assert D.RATE_FRAME == "domestic_v2", D.RATE_FRAME
os.chdir(HERE)
NPC = ["NP_P0", "NP_P1", "NP_P2", "NP_P3"]
HORIZONS = (12, 24, 36, 60)
c = duckdb.connect()
px = c.execute(f"""SELECT ticker, CAST(time AS DATE) AS time, Price, Close
    FROM read_parquet('{WC}/data/bq_cache/ticker/*.parquet')
    WHERE time >= DATE '2015-01-01' AND Price > 0 AND Close > 0""").df()
px["time"] = pd.to_datetime(px.time)
px = px.sort_values(["ticker", "time"]).reset_index(drop=True)
LAST = px.time.max()
dates = pd.Series(sorted(px.time.unique()))
q = dates.groupby(dates.dt.to_period("Q")).max()
ASOFS = [d for p_, d in q.items() if pd.Period("2016Q1") <= p_ <= pd.Period("2025Q4")]

uni = c.execute(f"""SELECT ticker, CAST(time AS DATE) AS time FROM read_parquet('{WC}/data/bq_cache/universe_pit/*.parquet')
    WHERE in_universe""").df()
uni["time"] = pd.to_datetime(uni.time)
uni_set = uni.groupby("time").ticker.apply(set).to_dict()
rat = c.execute(f"SELECT ticker, CAST(time AS DATE) AS time, route, rating FROM read_parquet('{WC}/data/bq_cache/fa_ratings_8l.parquet')").df()
rat["time"] = pd.to_datetime(rat.time); rat = rat.sort_values("time")
st = pd.read_parquet(f"{WC}/data/bq_cache/vnindex_5state_dt5g_live.parquet")[["time", "state"]]
st["time"] = pd.to_datetime(st.time); st = st.sort_values("time")
roe = c.execute(f"""SELECT ticker, CAST(time AS TIMESTAMP) AS time, ROE3Y, ROE_Trailing
    FROM read_parquet('{WC}/data/bq_cache/ticker_financial.parquet')""").df()
roe["time"] = pd.to_datetime(roe.time)
roe_by = {t: g.sort_values("time").reset_index(drop=True) for t, g in roe.groupby("ticker")}
fz = pd.read_csv(f"{WC}/mike/data/fiinprox_oshares_pit_20260926.csv", parse_dates=["date"])
fz_by = {t: g.sort_values("date")[["date", "shares"]].reset_index(drop=True) for t, g in fz.groupby("ticker")}
FZ_END = fz.date.max()


def sh_fiin(tk, d):
    g = fz_by.get(tk)
    if g is None or d > FZ_END + pd.Timedelta(days=5):
        return np.nan
    m = g.date <= d
    return float(g.shares[m].iloc[-1]) if m.any() else np.nan


fin = D._load_financials()
D._load_routes(); D._load_icb_map()
icb = D._load_icb_map()
fin_by = {t: g for t, g in fin.groupby("ticker")}
px_by = {t: g[["time", "Price", "Close"]].reset_index(drop=True) for t, g in px.groupby("ticker")}

rows = []
for a in ASOFS:
    us = uni_set.get(a, set())
    ra = rat[rat.time <= a].groupby("ticker").tail(1).set_index("ticker")
    st_a = st[st.time <= a].state.iloc[-1] if (st.time <= a).any() else None
    r_a = D.discount_rate(a, D.ERP)
    gT_a = D.terminal_growth_mode(a, None, D.ERP)
    for tk in sorted(us):
        g = fin_by.get(tk); p = px_by.get(tk)
        if g is None or p is None or D.is_financial(tk, a):
            continue
        rows_f = g[g.time <= a]
        if len(rows_f) < 4:
            continue
        pt = p[p.time == a]
        if len(pt) == 0:
            continue
        P0 = float(pt.Price.iloc[0]); C0 = float(pt.Close.iloc[0])
        last = rows_f.iloc[-1]
        assert last.time <= a, "PIT violation"
        res = D.fair_value(tk, a, price=P0, fin=g)
        annual = D._annual_series(rows_f, NPC)
        g_raw, _ = D.recency_weighted_growth(annual)
        gT = gT_a if r_a > gT_a else r_a - 0.01
        if np.isnan(g_raw):
            g_raw = gT
        g_exp = gT + D.GROWTH_SHRINK * (float(np.clip(g_raw, D.G_EXPLICIT_FLOOR, D.G_EXPLICIT_CAP)) - gT)
        if res["ok"]:   # tái dựng r/g phải khớp engine
            assert abs(res["discount_rate"] - r_a) < 1e-12 and abs(res["g_explicit"] - g_exp) < 1e-12 \
                and abs(res["g_terminal"] - gT) < 1e-12, (tk, a)
        osh_f = float(last.OShares) if pd.notna(last.OShares) else np.nan
        cfoa3 = float(last.CF_OA_3Y) if pd.notna(last.CF_OA_3Y) else np.nan
        cfinv3 = float(last.CF_Invest_3Y) if pd.notna(last.CF_Invest_3Y) else 0.0
        cfoa5 = float(last.CF_OA_5Y) if pd.notna(last.CF_OA_5Y) else np.nan
        cfinv5 = float(last.CF_Invest_5Y) if pd.notna(last.CF_Invest_5Y) else 0.0
        rr = roe_by.get(tk); roe3 = roe_t = np.nan
        if rr is not None:
            m = rr.time <= a
            if m.any():
                lr = rr[m].iloc[-1]; roe3 = lr.ROE3Y; roe_t = lr.ROE_Trailing
        ra_ = ra.loc[tk] if tk in ra.index else None
        # vốn hoá tại as-of
        shf = sh_fiin(tk, a)
        fs = p[p.time <= last.time]
        if len(fs):
            Pf, Cf = float(fs.Price.iloc[-1]), float(fs.Close.iloc[-1])
            mc_fb = Pf * osh_f * C0 / Cf
        else:
            mc_fb = np.nan
        rec = {"ticker": tk, "asof": a, "P0": P0, "icb": icb.get(tk), "dt5g": st_a,
               "rating": (float(ra_.rating) if ra_ is not None and pd.notna(ra_.rating) else np.nan),
               "eng_ok": res["ok"], "eng_reason": res.get("reason"),
               "V_l3": (res["fair_value_ps"] * res["oshares"]) if res["ok"] else np.nan,
               "r": r_a, "g_exp": g_exp, "g_T": gT, "osh_fin": osh_f, "fin_time": last.time,
               "cfoa3": cfoa3, "cfinv3": cfinv3, "cfoa5": cfoa5, "cfinv5": cfinv5,
               "annual_np": json.dumps([float(x) for x in annual]),
               "roe3y": float(roe3) if pd.notna(roe3) else np.nan,
               "roe_ttm": float(roe_t) if pd.notna(roe_t) else np.nan,
               "sh_fiin": shf, "MC0_fiin": P0 * shf if shf == shf else np.nan,
               "MC0_fb": mc_fb, "MC0_old": P0 * osh_f}
        fut = p[p.time >= a]; ft = fut.time.values; cl = fut.Close.values / C0
        for N in HORIZONS:
            end = a + pd.DateOffset(months=N)
            m = ft <= np.datetime64(end)
            full = (LAST >= end) and (ft[m][-1] >= np.datetime64(end - pd.Timedelta(days=20)))
            rec[f"full{N}"] = bool(full)
            rec[f"minTR{N}"] = float(cl[m].min())       # gồm t0 ⇒ ≤ 1
            rec[f"TR{N}"] = float(cl[m][-1]) if full else np.nan
            if full:
                d_end = pd.Timestamp(ft[m][-1])
                rec[f"MCN{N}"] = float(fut.Price.values[m][-1]) * sh_fiin(tk, d_end)
            else:
                rec[f"MCN{N}"] = np.nan
        rows.append(rec)
    print(a.date(), len(rows), flush=True)

pan = pd.DataFrame(rows)
pan.to_parquet(os.path.join(OUT, "panel.parquet"))
json.dump({"n_rows": len(pan), "n_eng_ok": int(pan.eng_ok.sum()), "last_px": str(LAST.date()),
           "fiin_end": str(FZ_END.date()), "n_fiin": int(pan.sh_fiin.notna().sum())},
          open(os.path.join(OUT, "panel_meta.json"), "w"), indent=1)
print("done", len(pan), int(pan.eng_ok.sum()), int(pan.sh_fiin.notna().sum()))
