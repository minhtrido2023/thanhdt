#!/usr/bin/env python3
"""Việc (1) — bảng đặc trưng hành vi theo TỪNG sự kiện BCTC (ticker × quý, release ≥ 2014, PIT).

Paper-only R&D, job Taylor_20261015_173117. KHÔNG đọc/ghi gì production.
Nguồn (tra mike/kb/data_registry/ 2026-10-16):
  data/bq_cache/ticker/*.parquet          DERIVED mirror tav2_bq.ticker (vintage sync 2026-10-15 23:45)
  data/bq_cache/ticker_financial.parquet  CANONICAL ticker_financial (Release_Date)
  data/bq_cache/universe_pit/*.parquet    CANONICAL universe_pit (KHÔNG ticker_prune)
  data/bq_cache/fa_ratings_8l.parquet     CANONICAL 8L PIT (time = eff_date)
  insider_raw.csv                         tav2_bq.insider_transaction (Done, DDIND+DDRP; public_date = ngày báo cáo KẾT QUẢ = an toàn)
Quy ước thời gian: t0 = phiên đầu tiên >= Release_Date. Cửa sổ đặc trưng dùng tới close t0+1.
Forward bắt đầu từ close s = t0+1 (sau khi mọi đặc trưng đã biết) ⇒ không look-ahead.
profit_* KHÔNG dùng. Forward return tự tính từ Close (adjusted) chỉ để ĐO.
"""
import glob, os
import warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore", category=RuntimeWarning)

WC = "/home/trido/thanhdt/WorkingClaude"
OUT = os.path.dirname(os.path.abspath(__file__))
C = f"{WC}/data/bq_cache"

# ---------- prices (wide, VNINDEX calendar) ----------
px = pd.concat([pd.read_parquet(f, columns=["time", "ticker", "Close", "Price", "Volume", "ICB_Code"])
                for f in sorted(glob.glob(f"{C}/ticker/*.parquet"))], ignore_index=True)
px["time"] = pd.to_datetime(px["time"])
px = px.drop_duplicates(["ticker", "time"], keep="last")
cal = pd.DatetimeIndex(sorted(px.loc[px.ticker == "VNINDEX", "time"].unique()))
W = lambda c: px.pivot(index="time", columns="ticker", values=c).reindex(cal)
close, price, vol = W("Close"), W("Price"), W("Volume")
close = close.where(close > 0); price = price.where(price > 0)   # Close=0 rác ⇒ NaN
icb = px.dropna(subset=["ICB_Code"]).sort_values("time").groupby("ticker")["ICB_Code"].last()
mk = close["VNINDEX"]
ret = close.pct_change(fill_method=None)            # NaN on suspended days (no stale fill)
mret = mk.pct_change()
ar = ret.sub(mret, axis=0)                          # market-adjusted
tick_idx = {t: i for i, t in enumerate(close.columns)}
R, AR, MR = ret.values, ar.values, mret.values
CL = close.ffill(limit=5).values                    # path for MDD (fill short suspensions only)
CLraw = close.values
VOL, PRC = vol.values, price.values
NT = len(cal)

# ---------- events ----------
tf = pd.read_parquet(f"{C}/ticker_financial.parquet",
                     columns=["ticker", "time", "quarter", "Release_Date", "NP_P0", "CF_OA_P0", "totalAsset_P0"])
tf["rd"] = pd.to_datetime(tf["Release_Date"], errors="coerce")
y, q = tf.quarter.str[:4].astype(int), tf.quarter.str[-1].astype(int)
tf["qend"] = pd.to_datetime(dict(year=y, month=q * 3, day=1)) + pd.offsets.MonthEnd(0)
n_all = len(tf[tf.qend >= "2013-01-01"]); n_null = tf[(tf.qend >= "2013-01-01")].rd.isna().sum()
tf = tf.dropna(subset=["rd"]).drop_duplicates(["ticker", "quarter"], keep="last")
tf = tf[tf.qend >= "2012-01-01"].sort_values(["ticker", "qend"]).reset_index(drop=True)
tf["lag_days"] = (tf.rd - tf.qend).dt.days
# baseline = median of SAME ticker's previous 8 events (strictly prior) — min 4
tf["lag_med8"] = tf.groupby("ticker")["lag_days"].transform(lambda s: s.shift(1).rolling(8, min_periods=4).median())
tf["lag_dev"] = tf.lag_days - tf.lag_med8
tf = tf[(tf.rd >= "2014-01-01") & tf.ticker.isin(tick_idx)].reset_index(drop=True)
tf["weekend"] = (tf.rd.dt.dayofweek >= 5).astype(int)
tf["late30"] = (tf.lag_days > 30).astype(int)          # quá hạn 30 ngày (BCTC quý riêng lẻ, TT96)
tf["near_deadline"] = tf.lag_days.between(27, 30).astype(int)
tf["accr_q"] = tf.NP_P0.sub(tf.CF_OA_P0) / tf.totalAsset_P0.where(tf.totalAsset_P0 > 0)

t0 = np.searchsorted(cal.values, tf.rd.values, side="left")
tf["t0"] = t0
tf = tf[(tf.t0 >= 70) & (tf.t0 < NT - 2)].reset_index(drop=True)

def wsum(a, j, lo, hi, need):
    x = a[lo:hi + 1, j]; ok = ~np.isnan(x)
    return np.nansum(x) if ok.sum() >= need else np.nan

rows = []
for r in tf.itertuples(index=False):
    j = tick_idx[r.ticker]; t = r.t0
    d = {}
    d["car_m1p1"] = wsum(AR, j, t - 1, t + 1, 2)
    d["car_m5m1"] = wsum(AR, j, t - 5, t - 1, 3)
    d["car_m5p1"] = wsum(AR, j, t - 5, t + 1, 5)
    v0 = VOL[t, j]; vb = VOL[t - 21:t - 1, j]
    d["vol_ratio"] = v0 / np.nanmean(vb) if np.nanmean(vb) > 0 and not np.isnan(v0) else np.nan
    den = d["car_m5p1"]
    d["leak_ratio"] = np.clip(d["car_m5m1"] / den, -2, 3) if (den == den and abs(den) >= 0.02) else np.nan
    lo, hi = t - 61, t - 2
    rr, mm = R[lo:hi + 1, j], MR[lo:hi + 1]
    pv = (PRC[lo:hi + 1, j] * VOL[lo:hi + 1, j])
    ok = ~np.isnan(rr) & (pv > 0)
    d["n_days60"] = int(ok.sum())
    if ok.sum() >= 40:
        d["amihud_log"] = np.log(np.mean(np.abs(rr[ok]) / pv[ok]) * 1e9 + 1e-12)
        b = np.polyfit(mm[ok], rr[ok], 1)
        d["idio_vol60"] = np.std(rr[ok] - np.polyval(b, mm[ok]), ddof=2) * np.sqrt(252)
        d["limit_freq60"] = np.mean(np.abs(rr[ok]) >= 0.065)
        d["adv_sh60"] = np.nanmean(VOL[lo:hi + 1, j])
    # forward (measurement only): from close s=t0+1
    s = t + 1
    for name, h in (("1m", 21), ("3m", 63)):
        e = s + h
        if e < NT and not np.isnan(CLraw[s, j]) and not np.isnan(CLraw[e, j]):
            rs = CLraw[e, j] / CLraw[s, j] - 1; ms = mk.values[e] / mk.values[s] - 1
            d[f"fwd_{name}"] = rs; d[f"fwdx_{name}"] = rs - ms
    e = s + 63
    if e < NT and not np.isnan(CL[s, j]):
        p = CL[s:e + 1, j]
        if np.isnan(p).mean() < 0.2:
            p = pd.Series(p).ffill().values
            d["mdd_3m"] = np.min(p / np.maximum.accumulate(p) - 1)
            m = mk.values[s:e + 1]; d["mdd_3m_mkt"] = np.min(m / np.maximum.accumulate(m) - 1)
    d["t_s"] = cal[s]
    rows.append(d)
ev = pd.concat([tf, pd.DataFrame(rows)], axis=1)
ev["sector1"] = (ev.ticker.map(icb) // 1000).fillna(-1).astype(int)

# ---------- universe_pit as of t0-1 ----------
up = pd.concat([pd.read_parquet(f, columns=["time", "ticker", "in_universe"])
                for f in sorted(glob.glob(f"{C}/universe_pit/*.parquet"))], ignore_index=True)
up["time"] = pd.to_datetime(up["time"])
ev["t_prev"] = cal[ev.t0 - 1]
ev = ev.merge(up.rename(columns={"time": "t_prev"}), on=["ticker", "t_prev"], how="left")
ev["in_universe"] = ev.in_universe.fillna(False).astype(bool)

# ---------- insider net buy 90d before release ----------
ins = pd.read_csv(f"{OUT}/insider_raw.csv", parse_dates=["public_date"])
ins["sh"] = np.where(ins.action_code == "S", -ins.share_acquire.abs(), ins.share_acquire.abs())
# Bẫy (4) registry: cụm ≥5 người MUA cùng ticker+ngày = ESOP ⇒ loại
cl = ins[ins.action_code == "B"].groupby(["ticker", "public_date"]).trader_person_id.nunique()
esop = set(cl[cl >= 5].index)
ins = ins[~((ins.action_code == "B") & pd.Series(list(zip(ins.ticker, ins.public_date))).isin(esop).values)]
INS_START = ins.public_date.min() + pd.Timedelta(days=90)
g = {k: v.sort_values("public_date") for k, v in ins.groupby("ticker")}
nb, nbuyers, nsellers = [], [], []
for r in ev.itertuples(index=False):
    if r.rd < INS_START:
        nb.append(np.nan); nbuyers.append(np.nan); nsellers.append(np.nan); continue
    x = g.get(r.ticker)
    if x is None:
        nb.append(0.0); nbuyers.append(0); nsellers.append(0); continue
    w = x[(x.public_date >= r.rd - pd.Timedelta(days=90)) & (x.public_date <= r.rd - pd.Timedelta(days=1))]
    nb.append(w.sh.sum()); nbuyers.append(w.loc[w.sh > 0, "trader_person_id"].nunique())
    nsellers.append(w.loc[w.sh < 0, "trader_person_id"].nunique())
ev["ins_net_sh"] = nb
ev["ins_netbuy_adv"] = ev.ins_net_sh / ev.adv_sh60.where(ev.adv_sh60 > 0)   # đơn vị: số phiên ADV
ev["ins_breadth"] = pd.Series(nbuyers, dtype=float) - pd.Series(nsellers, dtype=float)

# ---------- 8L rating PIT (as-of forward start s) + previous row ----------
r8 = pd.read_parquet(f"{C}/fa_ratings_8l.parquet")
r8["time"] = pd.to_datetime(r8["time"])
r8 = r8.sort_values(["ticker", "time"])
r8["rating_prev"] = r8.groupby("ticker").rating.shift(1)
ev = ev.sort_values("t_s")
ev = pd.merge_asof(ev, r8.rename(columns={"time": "r8_time"})[["ticker", "r8_time", "route", "rating", "rating_prev"]].sort_values("r8_time"),
                   left_on="t_s", right_on="r8_time", by="ticker", direction="backward")
assert (ev.r8_time.dropna() <= ev.loc[ev.r8_time.notna(), "t_s"]).all()

ev["wave"] = ev.quarter          # 1 đợt công bố = 1 quý tài chính (≈51 đợt)
ev["year"] = ev.rd.dt.year
keep = ["ticker", "quarter", "wave", "year", "qend", "rd", "t_s", "sector1", "in_universe", "route", "rating",
        "rating_prev", "lag_days", "lag_med8", "lag_dev", "weekend", "late30", "near_deadline",
        "car_m1p1", "car_m5m1", "car_m5p1", "leak_ratio", "vol_ratio", "amihud_log", "idio_vol60",
        "limit_freq60", "ins_netbuy_adv", "ins_breadth", "accr_q", "n_days60",
        "fwd_1m", "fwdx_1m", "fwd_3m", "fwdx_3m", "mdd_3m", "mdd_3m_mkt"]
ev = ev.sort_values(["ticker", "rd"])[keep]
ev.to_csv(f"{OUT}/events_features.csv.gz", index=False)
print(f"ticker_financial rows qend>=2013: {n_all}, Release_Date NULL: {n_null} ({n_null/n_all:.1%}) — loại khỏi mẫu")
print(f"events written: {len(ev)}, in_universe: {ev.in_universe.sum()}, tickers(univ): {ev[ev.in_universe].ticker.nunique()}, waves: {ev.wave.nunique()}")
print(f"insider window start: {INS_START.date()}, ESOP clusters removed: {len(esop)}")
print(ev[ev.in_universe].describe().T[["count", "mean", "50%", "std"]].round(4).to_string())
