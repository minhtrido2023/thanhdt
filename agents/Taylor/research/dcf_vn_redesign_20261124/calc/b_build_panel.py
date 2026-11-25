# -*- coding: utf-8 -*-
"""b_build_panel.py — panel THÁNG (mã, phiên cuối tháng) 2008→2026 trong KHÔNG GIAN TỈ SỐ, PIT.
Không dùng OShares / PB / PE vendor (TRAP). Không dùng profit_*. Chỉ cache local + px_pre2013_m.csv (BQ, tháng).
Out: ../out/panel_m.parquet. Env LAGQ=1 ⇒ trễ thêm 1 quý (known_date + 92 ngày) -> panel_m_lag1.parquet."""
import os, sys
import numpy as np, pandas as pd, duckdb
WC = "/home/trido/thanhdt/WorkingClaude"; HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "out")
sys.path.insert(0, WC)
LAGQ = int(os.environ.get("LAGQ", "0"))
c = duckdb.connect()

# ---------- 1. BCTC theo kỳ công bố ----------
fin = c.execute(f"""SELECT ticker, CAST(time AS DATE) AS time, quarter, Price, Close, BVPS, ROE_Trailing, Dividend_1Y,
      NP_P0, NP_P1, NP_P2, NP_P3 FROM read_parquet('{WC}/data/bq_cache/ticker_financial.parquet')
      WHERE BVPS > 0 AND Price > 0 AND Close > 0 AND ROE_Trailing IS NOT NULL""").df()
fin["time"] = pd.to_datetime(fin.time).astype("datetime64[ns]")
fin = fin.sort_values(["ticker", "time"]).drop_duplicates(["ticker", "time"], keep="last").reset_index(drop=True)
fin["known"] = fin.time + pd.Timedelta(days=92 * LAGQ)
fin["B_adj_raw"] = fin.BVPS * fin.Close / fin.Price          # sổ sách/cp theo đơn vị Close điều chỉnh
fin["roe"] = fin.ROE_Trailing.clip(-0.5, 0.6)
fin["payout_raw"] = np.where(fin.roe > 0.01, (fin.Dividend_1Y.fillna(0) / (fin.roe * fin.BVPS)).clip(0, 1), np.nan)

def per_ticker(g):
    g = g.copy()
    # debounce PIT: bước nhảy |dlog B_adj| > 0.3 chỉ được nhận khi dòng kế xác nhận (trễ 1 quý), tránh lệch split 1 dòng
    b = np.log(g.B_adj_raw.values); acc = np.empty(len(b)); acc[0] = b[0]; pend = None; deb = np.zeros(len(b), bool)
    for i in range(1, len(b)):
        if abs(b[i] - acc[i - 1]) <= 0.3:
            acc[i] = b[i]; pend = None
        elif pend is not None and abs(b[i] - pend) <= 0.3:
            acc[i] = b[i]; pend = None
        else:
            acc[i] = acc[i - 1]; pend = b[i]; deb[i] = True
    g["B_adj"] = np.exp(acc); g["debounced"] = deb
    t = g.time.values; roe = g.roe.values; po = g.payout_raw.values; pb = (g.Close / g.B_adj).values
    for W in (3, 5, 7):
        med = np.empty(len(g)); n = np.empty(len(g))
        for i in range(len(g)):
            m = (t <= t[i]) & (t > t[i] - np.timedelta64(int(W * 365.25), "D"))
            med[i] = np.median(roe[m]); n[i] = m.sum()
        g[f"roe_tc{W}"] = med; g[f"n_tc{W}"] = n
        if W == 5:
            g["roe_min5"] = [np.min(roe[(t <= t[i]) & (t > t[i] - np.timedelta64(1826, "D"))]) for i in range(len(g))]
    pm = np.empty(len(g)); pbm = np.empty(len(g)); npb = np.empty(len(g))
    for i in range(len(g)):
        m3 = (t <= t[i]) & (t > t[i] - np.timedelta64(1096, "D"))
        x = po[m3]; x = x[~np.isnan(x)]
        pm[i] = np.median(x) if len(x) else np.nan
        m5 = (t < t[i]) & (t > t[i] - np.timedelta64(1826, "D"))     # P/B quá khứ, KHÔNG gồm dòng hiện tại
        pbm[i] = np.median(pb[m5]) if m5.sum() >= 8 else np.nan; npb[i] = m5.sum()
    g["payout"] = pm; g["pb_med5"] = pbm
    return g
fin = pd.concat([per_ticker(g) for _, g in fin.groupby("ticker")], ignore_index=True)
print("fin rows", len(fin), "debounced", int(fin.debounced.sum()), flush=True)

# ---------- 2. lưới tháng ----------
px = c.execute(f"""SELECT ticker, CAST(time AS DATE) AS time, Close, Price, Volume, Trading_Value_1M_P50 AS tv
      FROM read_parquet('{WC}/data/bq_cache/ticker/*.parquet') WHERE Close > 0""").df()
px["time"] = pd.to_datetime(px.time).astype("datetime64[ns]")
px = px.sort_values(["ticker", "time"])
px["ym"] = px.time.dt.to_period("M")
gdates = pd.Series(sorted(px.time.unique())); gme = gdates.groupby(gdates.dt.to_period("M")).max()   # phiên cuối tháng toàn TT
me = px.groupby(["ticker", "ym"]).tail(1).copy()
# T+1: Close phiên giao dịch đầu tiên của mã SAU phiên cuối tháng toàn thị trường (trong 10 ngày)
nxt = px.merge(gme.rename("gme").rename_axis("ym").reset_index(), on="ym")
first_next = px.copy(); first_next["ym_prev"] = first_next.ym - 1
fn = first_next.groupby(["ticker", "ym"]).head(1)[["ticker", "ym_prev", "time", "Close"]].rename(
    columns={"ym_prev": "ym", "time": "t1_time", "Close": "t1_close"})
me = me.merge(fn, on=["ticker", "ym"], how="left")
pre = pd.read_csv(os.path.join(OUT, "px_pre2013_m.csv"), parse_dates=["time"])
pre["ym"] = pre.time.dt.to_period("M"); pre["tv"] = pre.Price * pre.Volume
pre = pre[pre.ym < me.ym.min()]
mm = pd.concat([pre[["ticker", "time", "ym", "Close", "Price", "tv"]], me[["ticker", "time", "ym", "Close", "Price", "tv", "t1_time", "t1_close"]]],
               ignore_index=True).sort_values(["time", "ticker"]).reset_index(drop=True)
mm = mm[mm.ym >= pd.Period("2008-01")]
mm["time"] = mm.time.astype("datetime64[ns]")
fcols = ["ticker", "known", "time", "quarter", "B_adj", "roe", "payout", "pb_med5", "debounced",
         "roe_tc3", "roe_tc5", "roe_tc7", "roe_min5", "n_tc3", "n_tc5", "n_tc7"]
f2 = fin[fcols].rename(columns={"time": "fin_time"}).sort_values("known")
f2["known"] = f2.known.astype("datetime64[ns]")
pan = pd.merge_asof(mm, f2, left_on="time", right_on="known", by="ticker", direction="backward")
pan = pan[pan.fin_time.notna() & ((pan.time - pan.known).dt.days <= 200 + 0)].copy()
assert (pan.fin_time <= pan.time).all() and (pan.known <= pan.time).all(), "PIT violation"
pan["bp"] = pan.B_adj / pan.Close

# ---------- 3. route, universe, rating, DT5G, lãi suất ----------
rat = c.execute(f"SELECT ticker, CAST(time AS DATE) AS time, route, rating FROM read_parquet('{WC}/data/bq_cache/fa_ratings_8l.parquet')").df()
rat["time"] = pd.to_datetime(rat.time).astype("datetime64[ns]"); rat = rat.sort_values("time")
route = rat.groupby("ticker").route.last()
pan["route"] = pan.ticker.map(route).fillna("COMPOUNDER")
pan = pd.merge_asof(pan.sort_values("time"), rat[["ticker", "time", "rating"]].rename(columns={"time": "rat_time"}),
                    left_on="time", right_on="rat_time", by="ticker", direction="backward")
uni = c.execute(f"SELECT ticker, CAST(time AS DATE) AS time, in_universe FROM read_parquet('{WC}/data/bq_cache/universe_pit/*.parquet') WHERE in_universe").df()
uni["time"] = pd.to_datetime(uni.time).astype("datetime64[ns]")
pan = pan.merge(uni, on=["ticker", "time"], how="left"); pan["in_universe"] = pan.in_universe.fillna(False).astype(bool)
st = pd.read_parquet(f"{WC}/data/bq_cache/vnindex_5state_dt5g_live.parquet")[["time", "state"]]
st["time"] = pd.to_datetime(st.time).astype("datetime64[ns]"); st = st.sort_values("time")
pan = pd.merge_asof(pan.sort_values("time"), st.rename(columns={"state": "dt5g"}), on="time", direction="backward")
import deposit_rate_vn as DR, sbv_macro_overlay as SBV
dep = pd.DataFrame(DR.DEPOSIT_EVENTS, columns=["time", "dep"]); dep["time"] = pd.to_datetime(dep.time).astype("datetime64[ns]")
refi = pd.DataFrame(SBV.SBV_REFI_EVENTS, columns=["time", "dep"]); refi["time"] = pd.to_datetime(refi.time).astype("datetime64[ns]"); refi["dep"] += 1.0
dep = pd.concat([refi[refi.time < dep.time.min()], dep]).sort_values("time")
months = pd.DataFrame({"ym": pd.period_range("2006-01", pan.ym.max(), freq="M")}); months["time"] = months.ym.dt.to_timestamp("M").astype("datetime64[ns]")
months = pd.merge_asof(months, dep, on="time", direction="backward")
months["dep_slow"] = months.dep.rolling(60, min_periods=24).mean()
pan = pan.merge(months[["ym", "dep", "dep_slow"]], on="ym", how="left")
# trung vị ROE_tc theo ngành (PIT: chỉ dòng BCTC đã biết tại tháng đó)
for W in (3, 5, 7):
    pan[f"sec_roe{W}"] = pan.groupby(["ym", "route"])[f"roe_tc{W}"].transform("median")
pan["tv_med_uni"] = pan[pan.in_universe].groupby("ym").tv.transform("median")
pan["tv_med_uni"] = pan.groupby("ym").tv_med_uni.transform("max")

# ---------- 4. lợi suất tương lai (NHÃN) ----------
pan = pan.sort_values(["ticker", "ym"]).reset_index(drop=True)
cl = pan.set_index(["ticker", "ym"]).Close
for N in (12, 24, 36):
    idx = pd.MultiIndex.from_arrays([pan.ticker, pan.ym + N])
    pan[f"fwd{N}"] = np.log(cl.reindex(idx).values / pan.Close.values)
pan["ym"] = pan.ym.astype(str)
pan.to_parquet(os.path.join(OUT, "panel_m.parquet" if LAGQ == 0 else f"panel_m_lag{LAGQ}.parquet"))
print("panel", len(pan), pan.ticker.nunique(), pan.ym.min(), pan.ym.max(), "in_uni rows", int(pan.in_universe.sum()))
