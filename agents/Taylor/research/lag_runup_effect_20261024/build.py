"""lag_runup_effect_20261024 — panel sự kiện LAG qualify (gate pin R3, verbatim pt_v23_audit_2014.py §4)
+ biến "giá đã chạy xa" PIT (chỉ giá ĐẾN phiên trước ngày công bố) + excess vs VNINDEX.
Kết quả = post_ret của classified CSV (Close[R+30]/Close[R+5]-1, lịch toàn cục) = định nghĩa LAG pin.
Read-only; chỉ ghi vào thư mục này. Chạy bằng $DNA_PYEXE.
"""
import os, pickle, numpy as np, pandas as pd, duckdb
WD = "/home/trido/thanhdt/WorkingClaude"; OUT = os.path.dirname(os.path.abspath(__file__))
c = duckdb.connect()

# ---- 1. event set: verbatim gate pin ----
ev = pd.read_csv(f"{WD}/data/earnings_events_classified.csv", parse_dates=["Release_Date"])
fin = pickle.load(open(f"{WD}/data/earnings_surprise_data.pkl", "rb"))
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"])
FLOOR = 1e9
fin["exp_B_MA"] = fin[["NP_P1", "NP_P2", "NP_P3", "NP_P4"]].mean(axis=1)
fin["surprise_B_MA"] = ((fin.NP_P0 - fin.exp_B_MA) / np.maximum(fin.exp_B_MA.abs(), FLOOR)).clip(-5, 5)
# biến thay thế: surprise so với quý liền trước, và so với xu hướng tuyến tính 4 quý
fin["surprise_prevQ"] = ((fin.NP_P0 - fin.NP_P1) / np.maximum(fin.NP_P1.abs(), FLOOR)).clip(-5, 5)
fin["exp_trend"] = fin.NP_P1 + (fin.NP_P1 - fin.NP_P4) / 3.0
fin["surprise_trend"] = ((fin.NP_P0 - fin.exp_trend) / np.maximum(fin.exp_trend.abs(), FLOOR)).clip(-5, 5)
keep = ["ticker", "quarter", "Release_Date", "surprise_B_MA", "surprise_prevQ", "surprise_trend", "NP_P0", "NP_P1", "NP_P4"]
ev = ev.merge(fin[keep], on=["ticker", "quarter", "Release_Date"], how="left")
ev = ev.sort_values(["ticker", "Release_Date"]).reset_index(drop=True)
ev["surprise_B_MA"] = ev["surprise_B_MA"].fillna(0)
ev["NP_R_prev"] = ev.groupby("ticker")["NP_R"].shift(1)
LN2, HL = np.log(2), 3.0
ev["prior_n_good"] = 0; ev["pa_HL3"] = np.nan
for tk, g in ev.groupby("ticker"):
    hist = []
    for ri in g.index:
        cur = ev.at[ri, "Release_Date"]
        ev.at[ri, "prior_n_good"] = len(hist)
        if hist:
            da = pd.to_datetime([d for d, _ in hist]); pa = np.array([p for _, p in hist])
            w = np.exp(-LN2 * ((cur - da).days.values / 365.25) / HL)
            ev.at[ri, "pa_HL3"] = (pa * w).sum() / w.sum()
        npr, pr = ev.at[ri, "NP_R"], ev.at[ri, "post_ret"]
        if pd.notna(npr) and npr >= 15 and pd.notna(pr):
            hist.append((cur, pr))
ff = pd.read_csv(f"{WD}/data/forensic_flags.csv")
forx = {r.ticker: pd.Timestamp(r.date) for r in ff.itertuples() if str(r.severity).strip() == "exclude"}
ev["_forbid"] = [(t in forx) and (d >= forx[t]) for t, d in zip(ev.ticker, ev.Release_Date)]
m = (ev.NP_R >= 15) & (ev.prior_n_good >= 4) & (ev.pa_HL3 >= 5)
print(f"gate (no forensic) n={int(m.sum())}; forensic dropped {int((m & ev._forbid).sum())}")
q = ev[m & ~ev._forbid].copy()
qq = q[(q.Release_Date >= "2014-01-01") & (q.Release_Date < "2026-05-15")]
print(f"CONTROL gate 2014-01..2026-05-15: n={len(qq)} post_ret={qq.post_ret.mean():.3f}; 2026 n={int((qq.Release_Date>='2026-01-01').sum())} post={qq[qq.Release_Date>='2026-01-01'].post_ret.mean():.3f}")
q.to_csv(f"{OUT}/gate_events.csv", index=False)
q["tier"] = np.where(q.surprise_B_MA > 0.5, "LAG_HI", "LAG_LO")

# ---- 2. prices (bq_cache ticker, Close adj) — global calendar like refresh_lagged_caches ----
px = c.execute(f"SELECT time,ticker,Close,ICB_Code FROM read_parquet('{WD}/data/bq_cache/ticker/*.parquet') WHERE time>='2012-01-01'").df()
px["time"] = pd.to_datetime(px.time)
icb = px.dropna(subset=["ICB_Code"]).sort_values("time").groupby("ticker").ICB_Code.last()
piv = px.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
dates = piv.index.values
vni = piv["VNINDEX"]
uni = c.execute(f"SELECT time,ticker FROM read_parquet('{WD}/data/bq_cache/universe_pit/*.parquet') WHERE in_universe").df()
uni["time"] = pd.to_datetime(uni.time); uni_set = set(zip(uni.ticker, uni.time))

def at(col, pos):
    return col.iat[pos] if 0 <= pos < len(col) else np.nan

rows = []
for r in q.itertuples():
    if r.ticker not in piv.columns: continue
    s = piv[r.ticker]
    pos = np.searchsorted(dates, np.datetime64(r.Release_Date), side="right") - 1
    if pos < 260: continue
    b = pos - 1                               # phiên TRƯỚC ngày công bố (PIT)
    cb, vb = at(s, b), at(vni, b)
    w250 = s.iloc[b - 249:b + 1]
    yr_end = piv.index[piv.index < pd.Timestamp(r.Release_Date.year, 1, 1)]
    ye = yr_end[-1] if len(yr_end) else None
    e5, e30 = at(s, pos + 5), at(s, pos + 30)
    v5, v30 = at(vni, pos + 5), at(vni, pos + 30)
    d = dict(ticker=r.ticker, quarter=r.quarter, rel=r.Release_Date, tier=r.tier, NP_R=r.NP_R, NP_R_prev=r.NP_R_prev,
             surprise_B_MA=r.surprise_B_MA, surprise_prevQ=r.surprise_prevQ, surprise_trend=r.surprise_trend,
             prior_n_good=r.prior_n_good, pa_HL3=r.pa_HL3, pre_ret=r.pre_ret, rel_ret=r.rel_ret, post_ret=r.post_ret,
             icb=icb.get(r.ticker, np.nan), in_uni=(r.ticker, pd.Timestamp(dates[pos])) in uni_set)
    d["r60"] = (cb / at(s, b - 60) - 1) * 100; d["r120"] = (cb / at(s, b - 120) - 1) * 100
    d["v60"] = (vb / at(vni, b - 60) - 1) * 100; d["v120"] = (vb / at(vni, b - 120) - 1) * 100
    if ye is not None and ye in s.index and pd.Timestamp(dates[b]) > ye:
        d["ytd"] = (cb / s.loc[ye] - 1) * 100; d["vytd"] = (vb / vni.loc[ye] - 1) * 100
    else:  # công bố trong vài phiên đầu năm → YTD≈0
        d["ytd"] = 0.0; d["vytd"] = 0.0
    hi, lo = w250.max(), w250.min()
    d["dist_hi250"] = (cb / hi - 1) * 100
    d["pos250"] = (cb - lo) / (hi - lo) if hi > lo else np.nan
    d["vni_post"] = (v30 / v5 - 1) * 100
    d["post_chk"] = (e30 / e5 - 1) * 100       # tự tính lại post_ret từ bq_cache (đối chiếu)
    rows.append(d)
P = pd.DataFrame(rows)
for a, b_ in [("r60", "v60"), ("r120", "v120"), ("ytd", "vytd")]:
    P[a + "_x"] = P[a] - P[b_]
P["excess"] = P.post_ret - P.vni_post
P["pre_minus_rel"] = P.pre_ret - P.rel_ret
P["sur_gap"] = P.surprise_B_MA - P.surprise_prevQ
P["commodity"] = P.icb < 2000
P["consec100"] = (P.NP_R > 100) & (P.NP_R_prev > 100)
P["oos"] = P.rel >= "2020-01-01"
P = P[P.rel >= "2014-01-01"]
P.to_csv(f"{OUT}/panel.csv", index=False)
print(f"panel n={len(P)} quarters={P.quarter.nunique()} in_uni={int(P.in_uni.sum())}")
print(f"post_ret mean {P.post_ret.mean():.3f} | recompute mean {P.post_chk.mean():.3f} | |diff|>0.5pp: {int(((P.post_ret-P.post_chk).abs()>0.5).sum())}")
print(P.groupby("tier").agg(n=("post_ret", "size"), post=("post_ret", "mean"), exc=("excess", "mean")))
