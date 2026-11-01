# -*- coding: utf-8 -*-
"""Vấn đề 1 — thời điểm chạy DCF. PREREG §3."""
import os
import numpy as np
import pandas as pd
import duckdb
from common import load_panel, month_close, add_fwd, spearman, OUT, DATA
import engine as E

WC = E.WC
P = print

# ---------------------------------------------------------------- (a) trễ công bố
c = duckdb.connect()
fin = c.execute(f"SELECT ticker,time,quarter,Release_Date FROM read_parquet('{WC}/data/bq_cache/ticker_financial.parquet')").df()
fin["time"] = pd.to_datetime(fin.time)
fin["Release_Date"] = pd.to_datetime(fin.Release_Date)
fin["qy"] = fin.quarter.str[:4].astype(int)
fin["qn"] = fin.quarter.str[-1].astype(int)
fin["qend"] = pd.PeriodIndex.from_fields(year=fin.qy, quarter=fin.qn, freq="Q").end_time.normalize()
fin["lag"] = (fin.Release_Date - fin.qend).dt.days
u = E.load_universe()
# universe tại cuối quý (phiên cuối của tháng cuối quý)
u["qend"] = u.time.dt.to_period("Q").dt.end_time.dt.normalize()
uset = u.groupby("qend").ticker.agg(set)
pan = load_panel()
finflag = pan.groupby("ticker").is_fin.last()
fin["in_u"] = [tk in uset.get(q, set()) for tk, q in zip(fin.ticker, fin.qend)]
fin["nonfin"] = ~fin.ticker.map(finflag).fillna(False).astype(bool)
f = fin[(fin.qy >= 2014) & fin.in_u & fin.Release_Date.notna() & (fin.lag >= 0) & (fin.lag <= 400)].copy()
f["period"] = np.where(f.qy <= 2019, "2014-19", "2020+")
rows = []
for (per, qn), g in f.groupby(["period", "qn"]):
    l = g.lag
    rows.append({"period": per, "Q": qn, "n": len(g), "p25": l.quantile(.25), "p50": l.median(), "p80": l.quantile(.8),
                 "p90": l.quantile(.9), "p95": l.quantile(.95), "le30": (l <= 30).mean(), "le45": (l <= 45).mean(),
                 "le60": (l <= 60).mean(), "le90": (l <= 90).mean()})
lagtab = pd.DataFrame(rows)
lagtab.to_csv(os.path.join(OUT, "t1a_release_lag.csv"), index=False)
P("=== (a) trễ công bố (ngày sau cuối quý), universe_pit, dòng có Release_Date")
P(lagtab.round(3).to_string(index=False))
P("dòng NULL Release_Date (2014+, in_u):", int((fin.qy.ge(2014) & fin.in_u & fin.Release_Date.isna()).sum()),
  "/", int((fin.qy.ge(2014) & fin.in_u).sum()))
# % mã có BCTC quý gần nhất theo ngày lịch (2020+, mỗi mùa): CDF theo ngày trong năm
cal = f[f.period == "2020+"].copy()
cal["rel_month_day"] = cal.Release_Date.dt.strftime("%m-%d")
for qn in (1, 2, 3, 4):
    g = cal[cal.qn == qn]
    P(f"Q{qn} 2020+: ngày lịch đạt 50/80/90/95% =",
      [(g.qend.iloc[0] + pd.Timedelta(days=int(g.lag.quantile(x)))).strftime("%m-%d") for x in (.5, .8, .9, .95)])

# trễ nạp vendor: vintage V
vint = {"2026-07-08": f"{WC}/data/bq_cache/ticker_financial.parquet.GOOD_pre_corruption_20260708snap",
        "2026-07-28": f"{WC}/data/bq_cache_asof20260728/ticker_financial.parquet",
        "2026-07-29": f"{WC}/data/bq_cache_asof20260729_postrestate/ticker_financial.parquet"}
cur = fin[["ticker", "quarter", "Release_Date"]].dropna()
vrows = []
for V, fp in vint.items():
    old = c.execute(f"SELECT ticker,quarter FROM read_parquet('{fp}')").df()
    have = set(zip(old.ticker, old.quarter))
    Vd = pd.Timestamp(V)
    for lo, hi in ((0, 7), (8, 14), (15, 30), (31, 60)):
        w = cur[(cur.Release_Date <= Vd - pd.Timedelta(days=lo)) & (cur.Release_Date > Vd - pd.Timedelta(days=hi + 1))]
        if len(w):
            vrows.append({"vintage": V, "days_since_release": f"{lo}-{hi}", "n": len(w),
                          "present_in_vintage": np.mean([(a, b) in have for a, b in zip(w.ticker, w.quarter)])})
vt = pd.DataFrame(vrows)
vt.to_csv(os.path.join(OUT, "t1a_vendor_ingest.csv"), index=False)
P("=== trễ nạp vendor (dòng 10-30 có Release_Date trong khoảng, có mặt ở vintage cũ?)")
P(vt.round(3).to_string(index=False))
# độ phủ Q3/2026 trong vintage 10-30 (live): bao nhiêu mã universe non-fin có quý 2026Q3
u_last = set(u.ticker[u.time == u.time.max()])
q3 = fin[(fin.quarter == "2026Q3")]
q2 = fin[(fin.quarter == "2026Q2")]
P(f"vintage 10-30: mã universe_pit có 2026Q3 = {len(set(q3.ticker) & u_last)}/{len(u_last)}; 2026Q2 = {len(set(q2.ticker) & u_last)}/{len(u_last)}")

# ---------------------------------------------------------------- (b) suy giảm theo tuổi
pan = pan.copy()
fv, gexp = E.current_fv(pan)
pan["fv"] = fv
pan["gexp"] = gexp
pan["mos"] = (pan.fv - pan.Price) / pan.fv
ri = pd.read_parquet(os.path.join(DATA, "row_inputs.parquet")).sort_values("time")
fut = pan[["t", "ticker"]].copy()
fut["t1"] = fut.t + pd.Timedelta(days=365)
fut = pd.merge_asof(fut.sort_values("t1"), ri[["ticker", "time", "ttm_np", "ttm_fcfe"]].rename(columns={"time": "tf"}),
                    left_on="t1", right_on="tf", by="ticker", direction="backward")
fut = fut.rename(columns={"ttm_np": "np_real", "ttm_fcfe": "fcfe_real"})
pan = pan.merge(fut[["t", "ticker", "tf", "np_real", "fcfe_real"]], on=["t", "ticker"], how="left")
pan["bucket"] = pd.cut(pan.age_days, [-1, 30, 60, 90, 10000], labels=["0-30", "31-60", "61-90", ">90"])
ok = pan.fv.notna() & (pan.t <= "2025-10-31") & (pan.tf > pan.time)
b = pan[ok].copy()
b["np_fc"] = b.ttm_np * (1 + b.gexp)
b["fcfe_fc"] = ((b.CF_OA_3Y + b.CF_Invest_3Y.fillna(0)) / 3) * (1 + b.gexp)
m1 = (b.np_fc > 0) & (b.np_real > 0)
b.loc[m1, "err_np"] = np.abs(np.log(b.np_real[m1] / b.np_fc[m1]))
m2 = (b.fcfe_fc > 0) & (b.fcfe_real > 0)
b.loc[m2, "err_fcfe"] = np.abs(np.log(b.fcfe_real[m2] / b.fcfe_fc[m2]))
b["fcfe_signwrong"] = (b.fcfe_real <= 0).astype(float)
b["yr"] = b.t.dt.year
# trong cùng mã × năm (loại hiệu ứng 'mã nộp muộn')
for col in ("err_np", "err_fcfe"):
    b[col + "_dm"] = b[col] - b.groupby(["ticker", "yr"])[col].transform("mean")
agg = b.groupby("bucket", observed=True).agg(n=("ticker", "size"), err_np_med=("err_np", "median"),
                                             err_np_dm=("err_np_dm", "mean"), err_fcfe_med=("err_fcfe", "median"),
                                             err_fcfe_dm=("err_fcfe_dm", "mean"), fcfe_signwrong=("fcfe_signwrong", "mean"))
P("=== (b) sai số dự báo 1 năm theo tuổi BCTC (|log thực/dự|; _dm = lệch so TB cùng mã×năm)")
P(agg.round(4).to_string())
agg.to_csv(os.path.join(OUT, "t1b_error_by_age.csv"))

# IC MoS theo nhóm tuổi: rank trong ngày rồi gộp
mc, me = month_close()
pan = add_fwd(pan, mc, me)
q = pan[pan.fv.notna() & pan.fwd3.notna() & pan.mos.notna()].copy()
q["rm"] = q.groupby("t").mos.rank(pct=True)
q["rr"] = q.groupby("t").fwd3.rank(pct=True)
q["rr12"] = q.groupby("t").fwd12.rank(pct=True)
rows = []
rng = np.random.default_rng(7)
for bk, g in q.groupby("bucket", observed=True):
    for per, gg in (("all", g), ("IS", g[g.t.dt.year <= 2019]), ("OOS", g[g.t.dt.year >= 2020])):
        if len(gg) < 200:
            continue
        ic = np.corrcoef(gg.rm, gg.rr)[0, 1]
        g12 = gg.dropna(subset=["rr12"])
        ic12 = np.corrcoef(g12.rm, g12.rr12)[0, 1] if len(g12) > 200 else np.nan
        yrs = gg.t.dt.year.unique()
        bs = []
        for _ in range(500):
            pick = rng.choice(yrs, len(yrs))
            s = pd.concat([gg[gg.t.dt.year == y] for y in pick])
            bs.append(np.corrcoef(s.rm, s.rr)[0, 1])
        rows.append({"bucket": bk, "period": per, "n_obs": len(gg), "n_dates": gg.t.nunique(), "ic3": ic,
                     "ic3_lo": np.percentile(bs, 2.5), "ic3_hi": np.percentile(bs, 97.5), "ic12": ic12})
ict = pd.DataFrame(rows)
ict.to_csv(os.path.join(OUT, "t1b_ic_by_age.csv"), index=False)
P("=== IC MoS (rank trong ngày, gộp) theo nhóm tuổi BCTC")
P(ict.round(4).to_string(index=False))
# phân bố tuổi theo tháng lịch
q["mon"] = q.t.dt.month
P("tuổi trung vị theo tháng lịch:", q.groupby("mon").age_days.median().to_dict())

# ---------------------------------------------------------------- (c) giá vs BCTC: ai đổi MoS
pp = pan[pan.fv.notna()].sort_values(["ticker", "t"]).copy()
pp["lp"] = np.log(pp.Price)
pp["lfv"] = np.log(pp.fv)
for k in (1, 3):
    d = pp.groupby("ticker")[["lp", "lfv"]].diff(k)
    v_p, v_f = d.lp.var(), d.lfv.var()
    cov = np.cov(d.dropna().lp, d.dropna().lfv)[0, 1]
    P(f"Δ{k} tháng log(P/FV): var(ΔlogP)={v_p:.4f} var(ΔlogFV)={v_f:.4f} cov={cov:.4f} "
      f"⇒ phần giá ≈ {v_p/(v_p+v_f):.2f}; FV đổi ở {(d.lfv.abs()>1e-9).mean():.2f} số tháng")
    dd = d.dropna()
    ch = dd.lfv.abs() > 1e-9
    P(f"   robust: median|ΔlogP|={dd.lp.abs().median():.4f}  median|ΔlogFV| (khi đổi)={dd.lfv[ch].abs().median():.4f} "
      f"p75={dd.lfv[ch].abs().quantile(.75):.4f}  median|ΔlogFV| mọi tháng={dd.lfv.abs().median():.4f}")
# trôi MoS khi để nguyên FV: |ΔMoS| trung vị trong 30/60/90 ngày do giá
pan.to_parquet(os.path.join(DATA, "panel_with_fv.parquet"))
