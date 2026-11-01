# -*- coding: utf-8 -*-
"""Vấn đề 2 — đánh giá OOS các biến thể beta. PREREG §4 (i)(ii)."""
import os
import numpy as np
import pandas as pd
from common import DATA, OUT, spearman

P = print
B = pd.read_parquet(os.path.join(DATA, "beta_panel.parquet"))
TR = pd.read_parquet(os.path.join(DATA, "beta_truth.parquet"))
pan = pd.read_parquet(os.path.join(DATA, "panel_monthly.parquet"))
icb2 = (pan.groupby("ticker").ICB_Code.last() // 100).rename("icb2")
TECH = ["ols", "blume", "vasicek", "dimson", "sw"]
long = B.melt(id_vars=["T", "ticker", "freq", "win", "bench", "nobs"], value_vars=TECH, var_name="tech",
              value_name="beta").dropna(subset=["beta"])
long["variant"] = long.freq + "_" + long.win.astype(str) + "y_" + long.tech + "_" + long.bench
# bottom-up ngành: TB leave-one-out của w_2y_vasicek_VNINDEX theo ICB cấp 2
base = long[long.variant == "w_2y_vasicek_VNINDEX"][["T", "ticker", "beta"]].copy()
base["icb2"] = base.ticker.map(icb2)
grp = base.groupby(["T", "icb2"]).beta
base["s"] = grp.transform("sum")
base["n"] = grp.transform("count")
base = base[base.n >= 4]
base["beta"] = (base.s - base.beta) / (base.n - 1)
bu = base[["T", "ticker", "beta"]].assign(variant="bottomup_icb2_w2y")
one = long[long.variant == "w_2y_ols_VNINDEX"][["T", "ticker"]].assign(beta=1.0, variant="const_1")
allv = pd.concat([long[["T", "ticker", "beta", "variant"]], bu, one], ignore_index=True)
N_TRIALS = allv.variant.nunique()
P("số biến thể (N trials) =", N_TRIALS)
# tập chung: mọi biến thể đánh giá trên CÙNG cặp (T,ticker) có cả 5y daily lẫn truth ⇒ so sánh công bằng
M = allv.merge(TR, on=["T", "ticker"], how="inner")
M = M[M.beta_true_w.notna()]
common_keys = M[M.variant == "d_5y_ols_VNINDEX"][["T", "ticker"]].drop_duplicates()
P("cặp chung (T,ticker) có 5Y ngày + truth:", len(common_keys), "quý:", common_keys["T"].nunique())
M = M.merge(common_keys, on=["T", "ticker"])
M["per"] = np.where(M["T"].dt.year <= 2019, "IS", "OOS")
rows = []
for (v, per), g in M.groupby(["variant", "per"]):
    sp, spd, dn, mse, bias = [], [], [], [], []
    for T, gg in g.groupby("T"):
        if len(gg) < 30:
            continue
        sp.append(spearman(gg.beta, gg.beta_true_w))
        spd.append(spearman(gg.beta, gg.beta_true_d))
        d = gg.dropna(subset=["down_sum"])
        dn.append(spearman(d.beta, d.down_sum))
        mse.append(np.mean((gg.beta - gg.beta_true_w) ** 2))
        bias.append(np.mean(gg.beta - gg.beta_true_w))
    rows.append({"variant": v, "per": per, "n_q": len(sp), "spear_w": np.mean(sp), "spear_d": np.mean(spd),
                 "spear_down": np.mean(dn), "mse_w": np.mean(mse), "bias_w": np.mean(bias),
                 "beta_med": g.beta.median(), "true_med": g.beta_true_w.median()})
ev = pd.DataFrame(rows)
ev.to_csv(os.path.join(OUT, "t2_beta_eval.csv"), index=False)
oos = ev[ev.per == "OOS"].set_index("variant")
is_ = ev[ev.per == "IS"].set_index("variant")
tab = oos.join(is_[["spear_w", "mse_w", "spear_down"]], rsuffix="_IS").sort_values("mse_w")
pd.set_option("display.width", 250)
P("=== OOS 2020+ (sắp theo MSE mức vs beta thật tuần-Dimson 12T kế tiếp); cột _IS = 2014-19")
P(tab[["n_q", "spear_w", "spear_d", "spear_down", "mse_w", "bias_w", "beta_med", "true_med", "spear_w_IS",
       "mse_w_IS", "spear_down_IS"]].round(3).head(25).to_string())
P("--- top Spearman OOS")
P(tab.sort_values("spear_w", ascending=False)[["spear_w", "mse_w", "spear_down", "spear_w_IS"]].round(3).head(12).to_string())
P("--- chiều so sánh (TB trên các biến thể còn lại):")
oo = oos.reset_index()
oo = oo[~oo.variant.isin(["const_1", "bottomup_icb2_w2y"])]
p = oo.variant.str.split("_", expand=True)
oo["freq"], oo["win"], oo["tech"], oo["bench"] = p[0], p[1], p[2], p[3]
for dim in ("freq", "win", "tech", "bench"):
    P(oo.groupby(dim)[["spear_w", "mse_w", "spear_down", "bias_w"]].mean().round(3).to_string())
P("--- phân phối beta thật (tuần Dimson 12T) OOS: p5/p25/p50/p75/p95 =",
  M[M.per == "OOS"].drop_duplicates(["T", "ticker"]).beta_true_w.quantile([.05, .25, .5, .75, .95]).round(3).tolist())
P("--- phân phối beta thật IS:", M[M.per == "IS"].drop_duplicates(["T", "ticker"]).beta_true_w.quantile([.05, .25, .5, .75, .95]).round(3).tolist())

# pha hạ cụ thể
px = pd.read_parquet(os.path.join(DATA, "px_daily.parquet"))
C = px.pivot(index="time", columns="ticker", values="Close").sort_index()
phases = [("2018-04-09", "2018-07-05", "2018-03-31"), ("2020-01-20", "2020-03-24", "2019-12-31"),
          ("2022-04-04", "2022-11-15", "2022-03-31")]
pr = []
for a, b_, T in phases:
    T = pd.Timestamp(T)
    ca = C[C.index <= a].iloc[-1]
    cb = C[C.index <= b_].iloc[-1]
    ret = (cb / ca - 1).rename("ret")
    vn = ret["VNINDEX"]
    for v in ("d_1y_ols_VNINDEX", "d_2y_ols_VNINDEX", "w_2y_ols_VNINDEX", "w_2y_vasicek_VNINDEX", "w_3y_vasicek_VNINDEX",
              "w_2y_dimson_VNINDEX", "d_2y_dimson_VNINDEX", "w_5y_vasicek_VNINDEX", "m_3y_ols_VNINDEX",
              "d_2y_sw_VNINDEX", "bottomup_icb2_w2y", "w_2y_ols_VN30"):
        g = allv[(allv.variant == v) & (allv["T"] == T)].set_index("ticker").beta
        j = pd.concat([g, ret], axis=1, join="inner").dropna()
        if len(j) < 30:
            continue
        slope = np.polyfit(j.beta, j.ret, 1)[0]
        pr.append({"phase": f"{a}→{b_}", "vnindex_ret": vn, "variant": v, "n": len(j),
                   "spear": spearman(j.beta, j.ret), "slope": slope, "beta_med": j.beta.median()})
prd = pd.DataFrame(pr)
prd.to_csv(os.path.join(OUT, "t2_beta_crash_phases.csv"), index=False)
P("=== pha hạ VNINDEX: Spearman(beta trước pha, lợi suất pha) — âm = beta báo đúng mã giảm mạnh")
P(prd.round(3).to_string(index=False))
# đối chiếu risk_rating.Beta (bin)
import duckdb
rr = duckdb.connect().execute("SELECT DISTINCT quarter,ticker,Beta FROM read_parquet('/home/trido/thanhdt/WorkingClaude/data/bq_cache/risk_rating.parquet') WHERE Beta IS NOT NULL").df()
rr["T"] = pd.PeriodIndex(rr.quarter.str[:4] + "Q" + rr.quarter.str[-1], freq="Q").end_time.normalize()
rr = rr.groupby(["T", "ticker"]).Beta.mean().reset_index()
out = []
for v in ("d_1y_ols_VNINDEX", "d_2y_ols_VNINDEX", "d_3y_ols_VNINDEX", "d_5y_ols_VNINDEX", "w_1y_ols_VNINDEX", "w_2y_ols_VNINDEX",
          "w_3y_ols_VNINDEX", "m_3y_ols_VNINDEX", "m_5y_ols_VNINDEX"):
    for lagq in (0, -1):
        rr2 = rr.copy()
        rr2["T"] = (rr2["T"] + pd.offsets.QuarterEnd(lagq)) if lagq else rr2["T"]
        j = allv[allv.variant == v].merge(rr2, on=["T", "ticker"])
        if len(j) < 100:
            continue
        sps = [spearman(g.beta, g.Beta) for _, g in j.groupby("T") if len(g) >= 30]
        out.append({"variant": v, "rr_quarter_shift": lagq, "n": len(j), "spear_mean": np.mean(sps) if sps else np.nan})
P("=== risk_rating.Beta (bin 1–5) vs beta tự tính — tìm cửa sổ khớp nhất")
P(pd.DataFrame(out).round(3).to_string(index=False))
P("risk_rating non-null theo quý:", rr.groupby("T").size().tail(6).to_dict(), "min T", rr["T"].min().date())
