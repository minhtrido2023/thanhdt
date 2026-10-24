"""Bổ sung cột cho panel.csv (bản copy, không sửa bản gốc):
  - sh_chg30: max |OShares(d)/OShares(d0) - 1| với d trong [d0-30, d0+30] ngày lịch (fiinprox_oshares_pit)
  - bhar{20,60}_tr: ret{H} − lợi suất VNINDEX tổng lợi suất (data/benchmark/vnindex_tr_daily.csv, tr_gross)
    cùng cửa sổ d1→d(1+H); bhar{H}_px2: cùng cửa sổ nhưng chỉ số GIÁ của chính file đó (đối chứng nguồn)
  - LAG thật: lag_live_schedule.live_lag_candidates() (qualify, NP_R%, prior_n_good, pa_HL3, tier, surprise_B_MA)
    + post_ret của earnings_events_classified.csv (close +5 → +30 phiên, %, chưa trừ chỉ số)
  - post_ex_px / post_ex_tr: post (tự tính, close d0+5 → d0+30) trừ VNINDEX giá / TR cùng cửa sổ.
Read-only ngoài thư mục này. Chạy bằng $DNA_PYEXE (pickle pandas 3)."""
import sys, os, numpy as np, pandas as pd, duckdb
WD = "/home/trido/thanhdt/WorkingClaude"; sys.path.insert(0, WD)
import lag_live_schedule as L
OUT = os.path.dirname(os.path.abspath(__file__))
d = pd.read_csv(f"{OUT}/panel.csv", parse_dates=["rel", "d0"])

px = duckdb.connect().execute(f"""SELECT time,ticker,Close FROM read_parquet('{WD}/data/bq_cache/ticker/*.parquet')
                  WHERE time>='2013-12-01'""").df()
px["time"] = pd.to_datetime(px["time"]); px = px.sort_values(["ticker", "time"])
pg = {k: g.set_index("time")["Close"] for k, g in px.groupby("ticker")}
tr = pd.read_csv(f"{WD}/data/benchmark/vnindex_tr_daily.csv", parse_dates=["date"]).set_index("date")
TR, PX2 = tr["tr_gross"], tr["vnindex"]
vni = pg["VNINDEX"]

sh = pd.read_csv(f"{WD}/mike/data/fiinprox_oshares_pit_20260926.csv", parse_dates=["date"]).sort_values(["ticker", "date"])
sh_g = {k: g for k, g in sh.groupby("ticker")}

def br(s, a, b):
    return s[b] / s[a] - 1 if a in s.index and b in s.index else np.nan

recs = []
for r in d.itertuples():
    c = pg.get(r.ticker); out = {}
    days = c.index; j = days.searchsorted(r.d0)
    # cổ phiếu đổi số lượng ±30 ngày
    s = sh_g.get(r.ticker)
    w = s[(s.date >= r.d0 - pd.Timedelta(days=30)) & (s.date <= r.d0 + pd.Timedelta(days=30))]
    base = s[s.date <= r.d0]
    if len(base) and len(w):
        b0 = float(base.shares.iloc[-1]); out["sh_chg30"] = float((w.shares / b0 - 1).abs().max())
    else:
        out["sh_chg30"] = np.nan
    for H in (20, 60):
        if j + 1 + H < len(days):
            d1, dH = days[j + 1], days[j + 1 + H]
            ret = c.iloc[j + 1 + H] / c.iloc[j + 1] - 1
            out[f"bhar{H}_tr"] = ret - br(TR, d1, dH); out[f"bhar{H}_px2"] = ret - br(PX2, d1, dH)
    if j + 30 < len(days):
        a, b = days[j + 5], days[j + 30]
        pr = c.iloc[j + 30] / c.iloc[j + 5] - 1
        out["post_own"] = pr; out["post_ex_px"] = pr - br(vni, a, b); out["post_ex_tr"] = pr - br(TR, a, b)
    recs.append(out)
d = pd.concat([d, pd.DataFrame(recs, index=d.index)], axis=1)

lag = L.live_lag_candidates(workdir=WD)
lag = lag.drop_duplicates(["ticker", "quarter"], keep="first")
d = d.merge(lag.rename(columns={"Release_Date": "lag_rel", "NP_R": "lag_NP_R"}), on=["ticker", "quarter"], how="left")
ev = pd.read_csv(f"{WD}/data/earnings_events_classified.csv").drop_duplicates(["ticker", "quarter"])
d = d.merge(ev[["ticker", "quarter", "post_ret", "pattern"]], on=["ticker", "quarter"], how="left")
d.to_csv(f"{OUT}/panel_aug.csv", index=False)
ok = d[d.ok & d.mos.notna()]
print("rows", len(d), "ok", len(ok), "sh_chg30>2%:", int((ok.sh_chg30 > 0.02).sum()),
      "lag matched:", int(ok.qualify.notna().sum()), "qualify:", int((ok.qualify == True).sum()),
      "post_ret matched:", int(ok.post_ret.notna().sum()),
      "corr(post_own*100, post_ret):", round(ok[["post_own", "post_ret"]].assign(post_own=ok.post_own * 100).corr().iloc[0, 1], 4),
      "corr(bhar60, bhar60_px2):", round(ok[["bhar60", "bhar60_px2"]].corr().iloc[0, 1], 4))
