"""dcf_rich_outlook_20261024 — panel PIT: mỗi (mã, quý công bố) 2014→2026 trong universe_pit.
DCF = dcf_valuation.fair_value(asof=ngày công bố) (chỉ dùng dòng ticker_financial time<=asof),
OShares PIT = fiinprox_oshares_pit (TRAP: ticker_financial.OShares bị restate), giá = Price (chưa
điều chỉnh) phiên đầu tiên >= ngày công bố. Kết quả: NP yoy Q+1/Q+2 (số công bố SAU), BHAR 20/40/60
từ close phiên kế tiếp (vs VNINDEX, Close đã điều chỉnh). Read-only, không ghi gì ngoài thư mục này.
"""
import sys, os, numpy as np, pandas as pd, duckdb
WD = "/home/trido/thanhdt/WorkingClaude"; sys.path.insert(0, WD)
import dcf_valuation as dv
OUT = os.path.dirname(os.path.abspath(__file__))
LIMIT = int(os.environ.get("LIMIT_TICKERS", "0"))
c = duckdb.connect()

fin = dv._load_financials()
extra = c.execute(f"SELECT ticker,time,quarter FROM read_parquet('{WD}/data/bq_cache/ticker_financial.parquet')").df()
px = c.execute(f"""SELECT time,ticker,Close,Price,ICB_Code,ROE5Y,PE FROM read_parquet('{WD}/data/bq_cache/ticker/*.parquet')
                  WHERE time>='2013-06-01'""").df()
px["time"] = pd.to_datetime(px["time"]); px = px.sort_values(["ticker", "time"])
vni = px[px.ticker == "VNINDEX"].set_index("time")["Close"]
uni = c.execute(f"SELECT time,ticker FROM read_parquet('{WD}/data/bq_cache/universe_pit/*.parquet') WHERE in_universe").df()
uni["time"] = pd.to_datetime(uni["time"]); uni_set = set(zip(uni.ticker, uni.time))
sh = pd.read_csv(f"{WD}/mike/data/fiinprox_oshares_pit_20260926.csv", parse_dates=["date"]).sort_values(["ticker", "date"])
sh_g = {k: g for k, g in sh.groupby("ticker")}

# sự kiện = lần XUẤT HIỆN ĐẦU của mỗi (mã, quý)
ev = fin.sort_values(["ticker", "time"]).drop_duplicates(["ticker", "quarter"], keep="first")
ev = ev[(ev.time >= "2014-01-01") & (ev.quarter.notna())]
tick = sorted(set(ev.ticker) & set(sh_g))
if LIMIT: tick = tick[:LIMIT]

def qnext(q, k):
    y, n = int(q[:4]), int(q[-1]); n += k
    y += (n - 1) // 4; n = (n - 1) % 4 + 1
    return f"{y}Q{n}"

def yoy(r):
    p0, p4 = r.NP_P0, r.NP_P4
    if pd.notna(p0) and pd.notna(p4) and p4 > 0: return float(np.clip(p0 / p4 - 1, -1, 2))
    return np.nan

rows = []
for i, tk in enumerate(tick):
    f_t = fin[fin.ticker == tk]; e_t = ev[ev.ticker == tk].set_index("quarter")
    p_t = px[px.ticker == tk].set_index("time"); s_t = sh_g[tk]
    if p_t.empty: continue
    days = p_t.index
    for q, r in e_t.iterrows():
        t = r.time
        j = days.searchsorted(t)                # phiên đầu tiên >= ngày công bố
        if j >= len(days) - 1: continue
        d0, d1 = days[j], days[j + 1]
        if (d0 - t).days > 7: continue
        if (tk, d0) not in uni_set: continue
        s = s_t[s_t.date <= d0]
        if s.empty: continue
        osh = float(s.shares.iloc[-1]); price = float(p_t.Price.iloc[j])
        res = dv.fair_value(tk, t, price=price, oshares=osh, fin=f_t)
        rec = {"ticker": tk, "quarter": q, "rel": t, "d0": d0, "price": price, "oshares_pit": osh,
               "icb": p_t.ICB_Code.iloc[j], "roe5y": p_t.ROE5Y.iloc[j], "pe": p_t.PE.iloc[j],
               "ok": res["ok"], "reason": res.get("reason"), "fv": res.get("fair_value_ps"),
               "mos": res.get("margin_of_safety"), "g_exp": res.get("g_explicit"), "r": res.get("discount_rate"),
               "g_T": res.get("g_terminal"), "base_fcfe": res.get("base_fcfe_vnd"),
               "np_p0": r.NP_P0, "np_p4": r.NP_P4, "yoy0": yoy(r),
               "np_ttm": r[["NP_P0", "NP_P1", "NP_P2", "NP_P3"]].sum(min_count=4)}
        # SUE mùa vụ: (P0-P4)/std 4 hiệu mùa vụ trước (P1-P5..P3-P7 + P0-P4)
        dif = np.array([r.NP_P0 - r.NP_P4, r.NP_P1 - r.NP_P5, r.NP_P2 - r.NP_P6, r.NP_P3 - r.NP_P7], float)
        sd = np.nanstd(dif[1:], ddof=1) if np.isfinite(dif[1:]).sum() == 3 else np.nan
        rec["sue"] = dif[0] / sd if sd and sd > 0 else np.nan
        for k in (1, 2):
            qk = qnext(q, k)
            if qk in e_t.index and 0 < (e_t.loc[qk].time - t).days <= 75 * k + 60:
                rec[f"yoy{k}"] = yoy(e_t.loc[qk]); rec[f"rel{k}"] = e_t.loc[qk].time
            else:
                rec[f"yoy{k}"] = np.nan
        cl = p_t.Close
        for H in (20, 40, 60):
            if j + 1 + H < len(days):
                dH = days[j + 1 + H]
                if dH in vni.index and d1 in vni.index:
                    rec[f"ret{H}"] = cl.iloc[j + 1 + H] / cl.iloc[j + 1] - 1
                    rec[f"bhar{H}"] = rec[f"ret{H}"] - (vni[dH] / vni[d1] - 1)
        rows.append(rec)
    if i % 100 == 0: print(i, len(tick), len(rows), flush=True)

df = pd.DataFrame(rows)
df.to_csv(f"{OUT}/panel.csv", index=False)
print("rows", len(df), "ok", int(df.ok.sum()))
