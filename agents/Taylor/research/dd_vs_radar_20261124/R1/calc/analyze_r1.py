#!/usr/bin/env python3
"""R1 — "Value Radar ở đáy 10 năm" có thật là rẻ?  (job Taylor_20261123_170313)

Đầu vào (khoá md5 ở INPUTS.md5):
  panel_monthly.parquet  — tav2_bq.ticker phiên cuối mỗi tháng 2007-01..2026-11-23, MỌI mã
                           (Price thô, OShares, PE, PB, BVPS, ICB_Code, NP_P0..P4) + universe_pit.in_universe
  data/value_radar_series.csv (chuỗi radar daily, chỉ để đối chiếu parity + H5)
  cpi_vn.cpi_monthly_df(), deposit_rate_vn.effective_deposit_events_df()
  kb/dd_price_zones.json (danh sách 36 mã DD)

Tất cả phân vị: NHÂN QUẢ (chỉ so với quá khứ trong cửa sổ), giống value_radar._roll_pct.
Tần suất THÁNG ⇒ cửa sổ 10Y = 120 tháng (min 24). N khai báo = số THÁNG; N độc lập hiệu dụng
nhỏ hơn nhiều (chuỗi định giá tự tương quan cao) — xem REPORT.
Chạy: python analyze_r1.py  → out/*.csv + out/summary.json   (threads=1, tất định)
"""
import os
for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[k] = "1"
import json
import sys

import numpy as np
import pandas as pd

W = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, W)
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

BANK = 8355.0
VINGROUP = {"VIC", "VHM", "VRE", "VPL"}
FLOOR = pd.Timestamp("2008-01-01")
WIN, MINP = 120, 24


# ---------------------------------------------------------------- công thức radar (chép nguyên)
def cap_weights(w, cap=0.10):
    w = np.asarray(w, float).copy()
    for _ in range(60):
        w = w / w.sum()
        over = w > cap + 1e-12
        if not over.any():
            break
        ex = (w[over] - cap).sum()
        w[over] = cap
        fr = ~over
        if w[fr].sum() <= 0:
            break
        w[fr] += ex * w[fr] / w[fr].sum()
    return w / w.sum()


def harm(w, x):
    return w.sum() / (w / x).sum()


def roll_pct(s, win=WIN, minp=MINP):
    v = np.asarray(s, float)
    out = np.full(len(v), np.nan)
    for i in range(len(v)):
        if not np.isfinite(v[i]):
            continue
        h = v[max(0, i - win + 1):i + 1]
        h = h[np.isfinite(h)]
        if len(h) < minp:
            continue
        out[i] = 100 * (h[:-1] < v[i]).mean()
    return out


def exp_pct(s, minp=MINP):
    return roll_pct(s, win=len(s), minp=minp)


# ---------------------------------------------------------------- nạp panel
p = pd.read_parquet(os.path.join(HERE, "panel_monthly.parquet"))
p["time"] = pd.to_datetime(p["time"])
p = p.sort_values(["ticker", "time"]).reset_index(drop=True)
p["mcap"] = p["Price"] * p["OShares"]            # Price THÔ × OShares PIT (đúng cơ sở, registry Bẫy 7)
p["book"] = p["BVPS"] * p["OShares"]
p["np_ttm"] = p[["NP_P0", "NP_P1", "NP_P2", "NP_P3"]].sum(axis=1, min_count=4)
p["is_bank"] = p["ICB_Code"] == BANK
# universe_pit: 2026-11-23 chưa build (max 2026-11-20) ⇒ dùng cờ phiên gần nhất của chính mã đó
# trong panel tháng (tháng trước) — chỉ ảnh hưởng tháng cuối.
p["in_univ"] = p.groupby("ticker")["in_universe"].transform(lambda s: s.astype("float").ffill())
p["in_univ"] = p["in_univ"].fillna(0).astype(bool)

# CPI level (chain YoY → tháng), ngoại suy YoY cuối cho tháng thiếu (ghi chú trong REPORT)
import cpi_vn  # noqa: E402
c = cpi_vn.cpi_monthly_df()[["time", "cpi_yoy"]].copy()
c["time"] = pd.to_datetime(c["time"]).dt.to_period("M")
months = pd.period_range("2007-01", "2026-11", freq="M")
c = c.set_index("time").reindex(months)
cpi_last_real = str(c["cpi_yoy"].last_valid_index())
c["cpi_yoy"] = c["cpi_yoy"].ffill()
c["lvl"] = np.cumprod((1 + c["cpi_yoy"] / 100) ** (1 / 12))
CPI = c["lvl"]
p["per"] = p["time"].dt.to_period("M")
p["cpi"] = p["per"].map(CPI)

# EPS chuẩn hoá theo từng mã: trung bình NP_ttm tại t, t-12, ..., (5 hoặc 10 mốc năm không chồng lấn)
# — đơn vị là LỢI NHUẬN CẤP DOANH NGHIỆP (không per-share) ⇒ khử pha loãng tự nhiên vì so với mcap.
p = p.set_index(["ticker", "per"]).sort_index()
idx_np = p["np_ttm"]
idx_np_real = p["np_ttm"] / p["cpi"]


def lagged_mean(series, nyears, minyrs):
    vals = []
    for k in range(nyears):
        s = series.copy()
        s.index = pd.MultiIndex.from_arrays([s.index.get_level_values(0),
                                             s.index.get_level_values(1) + 12 * k])
        vals.append(s.rename(f"l{k}"))
    m = pd.concat(vals, axis=1).reindex(series.index)
    cnt = m.notna().sum(axis=1)
    return m.mean(axis=1).where(cnt >= minyrs), cnt


p["np5"], p["n5"] = lagged_mean(idx_np, 5, 5)
p["np10"], p["n10"] = lagged_mean(idx_np, 10, 7)
np5r, _ = lagged_mean(idx_np_real, 5, 5)
np10r, _ = lagged_mean(idx_np_real, 10, 7)
p["np5_real"] = np5r * p["cpi"]     # quy về VND của ngày t
p["np10_real"] = np10r * p["cpi"]
p = p.reset_index()


# ---------------------------------------------------------------- rổ radar theo tháng + biến thể
def basket_stats(d):
    """d = panel 1 tháng. Trả dict số liệu các rổ."""
    r = {}
    d = d.copy()
    d["pb_i"] = d["mcap"] / d["book"]
    t300 = d.nlargest(300, "mcap")
    t = t300[np.isfinite(t300["pb_i"]) & (t300["pb_i"] > 0)].nlargest(100, "mcap").copy()
    if len(t) < 50:
        return None
    w = (t["mcap"] / t["mcap"].sum()).values
    pe = t["PE"].values.astype(float)
    ok = np.isfinite(pe) & (pe > 0)
    r["n_top100"] = len(t)
    r["n_pe_le0_or_nan"] = int((~ok).sum())
    r["w_pe_le0_or_nan"] = float(w[~ok].sum())
    r["pe_cap10"] = harm(cap_weights(w[ok]), pe[ok])
    r["pb_cap10"] = harm(cap_weights(w), t["pb_i"].values)
    # PE gồm cả mã lỗ (EY âm) — ratio-of-sums thuần cap-weight không trần
    r["pe_agg_incl_loss"] = t["mcap"].sum() / t["np_ttm"].sum()
    # H1: chuẩn hoá (cùng trọng số capped như radar, chỉ mã có np chuẩn hoá > 0)
    for col in ("np5", "np10", "np5_real", "np10_real"):
        x = (t["mcap"] / t[col]).values
        okn = np.isfinite(x) & (x > 0)
        r[f"pe_norm_{col}"] = harm(cap_weights(w[okn]), x[okn]) if okn.sum() > 30 else np.nan
        r[f"cov_{col}"] = float(w[okn].sum())
    both = t[np.isfinite(t["np5"]) & np.isfinite(t["np_ttm"])]
    r["eps_ttm_over_avg5"] = both["np_ttm"].sum() / both["np5"].sum()
    both10 = t[np.isfinite(t["np10"]) & np.isfinite(t["np_ttm"])]
    r["eps_ttm_over_avg10"] = both10["np_ttm"].sum() / both10["np10"].sum()
    bothr = t[np.isfinite(t["np5_real"]) & np.isfinite(t["np_ttm"])]
    r["eps_ttm_over_avg5_real"] = bothr["np_ttm"].sum() / bothr["np5_real"].sum()
    r["roe_agg"] = t["np_ttm"].sum() / t["book"].sum()
    nb = t[~t["is_bank"]]
    r["roe_agg_nonbank"] = nb["np_ttm"].sum() / nb["book"].sum()
    bk = t[t["is_bank"]]
    r["roe_agg_bank"] = bk["np_ttm"].sum() / bk["book"].sum() if len(bk) else np.nan
    r["w_bank"] = float((t["mcap"] * t["is_bank"]).sum() / t["mcap"].sum())
    r["w_vingroup"] = float((t["mcap"] * t["ticker"].isin(VINGROUP)).sum() / t["mcap"].sum())
    wc = cap_weights(w)
    r["wcap_bank"] = float((wc * t["is_bank"].values).sum())
    r["wcap_vingroup"] = float((wc * t["ticker"].isin(VINGROUP).values).sum())

    # H2: tách nhóm trong top-100
    def pe_capw(sub):
        ww = (sub["mcap"] / sub["mcap"].sum()).values
        x = sub["PE"].values.astype(float)
        k = np.isfinite(x) & (x > 0)
        return harm(cap_weights(ww[k]), x[k]) if k.sum() > 5 else np.nan

    def pb_capw(sub):
        ww = (sub["mcap"] / sub["mcap"].sum()).values
        return harm(cap_weights(ww), sub["pb_i"].values)

    def ew(sub):  # equal-weight: PE điều hoà (=1/EY trung bình, mã lỗ loại) + trung vị
        x = sub["PE"].values.astype(float)
        k = np.isfinite(x) & (x > 0)
        return (1 / np.mean(1 / x[k]) if k.sum() > 5 else np.nan,
                float(np.median(x[k])) if k.sum() > 5 else np.nan,
                float(np.median(sub["pb_i"])))

    r["pe_bank_cap"] = pe_capw(bk) if len(bk) > 5 else np.nan
    r["pb_bank_cap"] = pb_capw(bk) if len(bk) > 5 else np.nan
    r["pe_nonbank_cap"] = pe_capw(nb)
    r["pb_nonbank_cap"] = pb_capw(nb)
    nbv = nb[~nb["ticker"].isin(VINGROUP)]
    r["pe_nonbank_exvin_cap"] = pe_capw(nbv)
    r["pb_nonbank_exvin_cap"] = pb_capw(nbv)
    r["pe_top100_ewh"], r["pe_top100_med"], r["pb_top100_med"] = ew(t)
    r["pe_nonbank_ewh"], r["pe_nonbank_med"], r["pb_nonbank_med"] = ew(nb)
    # DD-like: universe_pit, phi ngân hàng, hạng vốn hoá 31-250 (vốn hoá vừa), PB>0
    u = d[d["in_univ"] & np.isfinite(d["pb_i"]) & (d["pb_i"] > 0)].copy()
    u["rk"] = u["mcap"].rank(ascending=False, method="first")
    mid = u[(u["rk"] > 30) & (u["rk"] <= 250) & (~u["is_bank"])]
    r["n_ddlike"] = len(mid)
    r["pe_ddlike_ewh"], r["pe_ddlike_med"], r["pb_ddlike_med"] = ew(mid) if len(mid) > 20 else (np.nan,) * 3
    r["pe_ddlike_cap"] = pe_capw(mid) if len(mid) > 20 else np.nan
    return r


rows = []
for tm, d in p[p["time"] >= FLOOR].groupby("time"):
    s = basket_stats(d)
    if s:
        s["time"] = tm
        rows.append(s)
B = pd.DataFrame(rows).sort_values("time").reset_index(drop=True)

# DD set: 36 mã (danh sách HÔM NAY ⇒ chọn mẫu hồi tố, chỉ dùng mô tả)
dd = json.load(open(os.path.join(W, "mike/kb/dd_price_zones.json")))
DD = sorted({e["ticker"] for e in dd["entries"]})
ddp = p[p["ticker"].isin(DD) & (p["time"] >= FLOOR)].copy()
ddp["ey"] = ddp["np_ttm"] / ddp["mcap"]
g = ddp.groupby("time")
DDS = pd.DataFrame({
    "n_dd": g.size(),
    "pe_dd_med": g.apply(lambda x: np.nanmedian(np.where(x.PE > 0, x.PE, np.nan)), include_groups=False),
    "pe_dd_ewh_incl_loss": g.apply(lambda x: 1 / np.nanmean(x.ey), include_groups=False),
    "pb_dd_med": g.apply(lambda x: np.nanmedian(np.where(x.PB > 0, x.PB, np.nan)), include_groups=False),
}).reset_index()
B = B.merge(DDS, on="time", how="left")

# deposit rate (effective, như radar) + spread
from deposit_rate_vn import effective_deposit_events_df  # noqa: E402
ev = effective_deposit_events_df().sort_values("time")
ev["time"] = pd.to_datetime(ev["time"])
B = pd.merge_asof(B, ev, on="time", direction="backward")
B["spread"] = 100 / B["pe_cap10"] - B["deposit_rate"]
B["spread_norm5"] = 100 / B["pe_norm_np5"] - B["deposit_rate"]

# phân vị
pct_cols = ["pe_cap10", "pb_cap10", "pe_agg_incl_loss", "pe_norm_np5", "pe_norm_np10",
            "pe_norm_np5_real", "pe_norm_np10_real", "eps_ttm_over_avg5", "eps_ttm_over_avg10",
            "eps_ttm_over_avg5_real", "roe_agg", "roe_agg_nonbank", "roe_agg_bank",
            "pe_bank_cap", "pb_bank_cap", "pe_nonbank_cap", "pb_nonbank_cap", "pe_nonbank_exvin_cap",
            "pb_nonbank_exvin_cap", "pe_top100_ewh", "pe_top100_med", "pb_top100_med",
            "pe_nonbank_ewh", "pe_nonbank_med", "pb_nonbank_med", "pe_ddlike_ewh", "pe_ddlike_med",
            "pb_ddlike_med", "pe_ddlike_cap", "pe_dd_med", "pe_dd_ewh_incl_loss", "pb_dd_med",
            "spread", "spread_norm5"]
for col in pct_cols:
    B[f"p10_{col}"] = roll_pct(B[col])
    B[f"pexp_{col}"] = exp_pct(B[col])
    B[f"p5_{col}"] = roll_pct(B[col], win=60, minp=24)
B.to_csv(os.path.join(OUT, "basket_monthly.csv"), index=False, float_format="%.6g")

last = B.iloc[-1]
summ = {"asof": str(last["time"].date()), "n_months": int(len(B)),
        "first_month": str(B["time"].iloc[0].date()), "cpi_last_real_month": cpi_last_real,
        "dd_tickers": DD}
summ["now"] = {k: (None if pd.isna(v) else (float(v) if not isinstance(v, (str, pd.Timestamp)) else str(v)))
               for k, v in last.items() if k != "time"}

# H1 — phân phối lịch sử của tỷ lệ chu kỳ
for col in ("eps_ttm_over_avg5", "eps_ttm_over_avg10", "roe_agg"):
    s = B.set_index("time")[col]
    summ[f"hist_{col}"] = {"min": float(s.min()), "p50": float(s.median()), "max": float(s.max()),
                           "last10y_median": float(s[s.index >= s.index[-1] - pd.DateOffset(years=10)].median())}

# H3 — P/E 'công bằng' kiểu DD: justified P/E = (1 - g/ROE)(1+g)/(r-g)
roe = float(last["roe_agg"])
roe_nb = float(last["roe_agg_nonbank"])
fair = []
for r_ in (0.123, 0.134, 0.135, 0.145):
    for g_ in (0.04, 0.06, 0.08):
        for lab, R in (("top100", roe), ("nonbank", roe_nb)):
            fair.append(dict(r=r_, g=g_, roe_basis=lab, roe=R,
                             pe_fair=(1 - g_ / R) * (1 + g_) / (r_ - g_)))
F = pd.DataFrame(fair)
F.to_csv(os.path.join(OUT, "h3_fair_pe_grid.csv"), index=False, float_format="%.4f")
summ["h3_fair_pe_grid"] = fair
# implied g tại P/E hiện tại, r=13,5%, ROE rổ: PE = (1-g/ROE)(1+g)/(r-g) — giải số
from scipy.optimize import brentq  # noqa: E402
pe_now = float(last["pe_cap10"])
for lab, R in (("top100", roe), ("nonbank", roe_nb)):
    try:
        summ[f"h3_implied_g_r135_{lab}"] = brentq(
            lambda g_: (1 - g_ / R) * (1 + g_) / (0.135 - g_) - pe_now, -0.2, 0.13)
    except ValueError:
        summ[f"h3_implied_g_r135_{lab}"] = None
# P/E lịch sử khi lãi huy động hiệu dụng ở cùng mặt bằng (±0,75pp)
dep_now = float(last["deposit_rate"])
same = B[(B["deposit_rate"] - dep_now).abs() <= 0.75]
same10 = same[same["time"] >= last["time"] - pd.DateOffset(years=10)]
summ["h3_same_rate"] = {"dep_now": dep_now, "n_months_all": int(len(same)),
                        "pe_med_all": float(same["pe_cap10"].median()) if len(same) else None,
                        "n_months_10y": int(len(same10)),
                        "pe_med_10y": float(same10["pe_cap10"].median()) if len(same10) else None,
                        "pe_min_10y": float(same10["pe_cap10"].min()) if len(same10) else None,
                        "months_10y": [str(x.date()) for x in same10["time"]]}

# H4 — tái lập P/E radar: (a) PE cột vs Σ NP_P0..P3 ; (b) parity với cache radar
d = p[p["time"] == p["time"].max()].copy()
d["pb_i"] = d["mcap"] / d["book"]
t = d.nlargest(300, "mcap")
t = t[np.isfinite(t["pb_i"]) & (t["pb_i"] > 0)].nlargest(100, "mcap")
recon = t["mcap"] / t["np_ttm"]
okk = np.isfinite(t["PE"]) & np.isfinite(recon)
summ["h4"] = {
    "pe_col_vs_recon_maxrelerr": float(((t.loc[okk, "PE"] - recon[okk]).abs() / t.loc[okk, "PE"].abs()).max()),
    "n_pe_le0": int((t["PE"] <= 0).sum()), "n_pe_nan": int(t["PE"].isna().sum()),
    "tickers_pe_le0_or_nan": t.loc[~(t["PE"] > 0), "ticker"].tolist(),
    "n_pb_le0_dropped_from_top300": int(((d.nlargest(300, "mcap")["pb_i"] <= 0) |
                                         ~np.isfinite(d.nlargest(300, "mcap")["pb_i"])).sum()),
    "pe_cap10_recon": float(last["pe_cap10"]),
    "pe_agg_incl_loss": float(last["pe_agg_incl_loss"]),
    "price_close_ratio_top100_median": float((t["Price"] / t["Close"]).median()),
    "top10_by_cap10_weight": None,
}
w = cap_weights((t["mcap"] / t["mcap"].sum()).values[t["PE"].values > 0])
tt = t[t["PE"] > 0].assign(wcap=w, wraw=lambda x: x.mcap / x.mcap.sum(),
                           contrib_ey=lambda x: x.wcap / x.PE)
tt["share_ey"] = tt["contrib_ey"] / tt["contrib_ey"].sum()
top = tt.sort_values("wcap", ascending=False).head(12)[["ticker", "Price", "PE", "PB", "wraw", "wcap", "share_ey", "is_bank"]]
top.to_csv(os.path.join(OUT, "h4_top_weights_now.csv"), index=False, float_format="%.4f")
summ["h4"]["top10_by_cap10_weight"] = top.head(10).to_dict("records")
rc = pd.read_csv(os.path.join(W, "data/value_radar_series.csv"), parse_dates=["time"])
m = B[["time", "pe_cap10", "pb_cap10"]].merge(rc, on="time", suffixes=("", "_radar"))
summ["h4"]["parity_months"] = int(len(m))
summ["h4"]["parity_pe_maxabs"] = float((m["pe_cap10"] - m["pe_cap10_radar"]).abs().max())
summ["h4"]["parity_pe_n_gt_1e6"] = int(((m["pe_cap10"] - m["pe_cap10_radar"]).abs() > 1e-6).sum())
summ["h4"]["parity_pb_maxabs"] = float((m["pb_cap10"] - m["pb_cap10_radar"]).abs().max())

# H5 — radar daily: rolling-10Y vs expanding-2008 vs cửa sổ khác cho P/E
rcs = rc.sort_values("time").reset_index(drop=True)
h5 = {}
for lab, win in (("roll10y_2500", 2500), ("roll5y_1250", 1250), ("roll3y_750", 750)):
    h5[f"p_pe_{lab}"] = float(roll_pct(rcs["pe_cap10"], win=win, minp=500 if win >= 1250 else 250)[-1])
    h5[f"p_pb_{lab}"] = float(roll_pct(rcs["pb_cap10"], win=win, minp=500 if win >= 1250 else 250)[-1])
h5["p_pe_expanding2008"] = float(exp_pct(rcs["pe_cap10"], minp=500)[-1])
h5["p_pb_expanding2008"] = float(exp_pct(rcs["pb_cap10"], minp=500)[-1])
post = rcs[rcs["time"] >= "2021-01-01"]
h5["p_pe_since2021"] = float(100 * (post["pe_cap10"].iloc[:-1] < post["pe_cap10"].iloc[-1]).mean())
h5["pe_min_since2021"] = float(post["pe_cap10"].min())
h5["pe_date_min_since2021"] = str(post.loc[post["pe_cap10"].idxmin(), "time"].date())
for yr0, yr1 in (("2008-01-01", "2013-12-31"), ("2014-01-01", "2019-12-31"),
                 ("2020-01-01", "2024-12-31"), ("2025-01-01", "2026-12-31")):
    s = rcs[(rcs["time"] >= yr0) & (rcs["time"] <= yr1)]
    h5[f"pe_{yr0[:4]}_{yr1[:4]}"] = {"min": float(s.pe_cap10.min()), "median": float(s.pe_cap10.median()),
                                    "max": float(s.pe_cap10.max()), "pb_median": float(s.pb_cap10.median())}
pre = rcs[rcs["time"] < "2026-09-21"]
h5["n_sessions_post_ftse"] = int((rcs["time"] >= "2026-09-21").sum())
h5["pe_median_post_ftse"] = float(rcs[rcs["time"] >= "2026-09-21"]["pe_cap10"].median())
h5["pe_last_pre_ftse"] = float(pre["pe_cap10"].iloc[-1])
summ["h5"] = h5


# ---------------------------------------------------------------- bổ sung: DD set + phân rã + phản thực tế
def top100(dt):
    d = p[p["time"] == dt].copy()
    d["pb_i"] = d["mcap"] / d["book"]
    t = d.nlargest(300, "mcap")
    return t[np.isfinite(t["pb_i"]) & (t["pb_i"] > 0)].nlargest(100, "mcap")


ext = {}
tnow = p["time"].max()
# (a) phân rã đổi P/E (aggregate gồm mã lỗ, cùng rổ top-100 mỗi mốc): dlnPE = dln(Σmcap) - dln(ΣNP)
for lab, t0 in (("since_2026-06-30", pd.Timestamp("2026-06-30")), ("since_2025-11-28", pd.Timestamp("2025-11-28")),
                ("since_2024-11-29", pd.Timestamp("2024-11-29"))):
    a, b = top100(t0), top100(tnow)
    common = sorted(set(a.ticker) & set(b.ticker))
    ac, bc = a.set_index("ticker").loc[common], b.set_index("ticker").loc[common]
    ext[f"decomp_{lab}"] = {
        "n_common": len(common),
        "dln_pe_agg_all": float(np.log((b.mcap.sum() / b.np_ttm.sum()) / (a.mcap.sum() / a.np_ttm.sum()))),
        "dln_mcap_common": float(np.log(bc.mcap.sum() / ac.mcap.sum())),
        "dln_np_common": float(np.log(bc.np_ttm.sum() / ac.np_ttm.sum())),
        "pe_cap10_t0": float(B.loc[B.time == t0, "pe_cap10"].iloc[0]),
        "top_np_increase": (bc.np_ttm - ac.np_ttm).sort_values(ascending=False).head(6).div(1e12).round(2).to_dict(),
        "top_np_increase_share": float((bc.np_ttm - ac.np_ttm).sort_values(ascending=False).head(5).sum()
                                       / (bc.np_ttm.sum() - ac.np_ttm.sum())),
    }
# (b) DD set: EPS TTM / TB5Y, P/E chuẩn hoá, P/E tại tâm DD
dnow = p[(p["time"] == tnow) & p["ticker"].isin(DD)].copy()
okd = dnow[np.isfinite(dnow.np5) & (dnow.np5 > 0) & np.isfinite(dnow.np_ttm)]
ext["dd_eps_ttm_over_avg5_agg"] = float(okd.np_ttm.sum() / okd.np5.sum())
ext["dd_eps_ttm_over_avg5_median"] = float((okd.np_ttm / okd.np5).median())
ext["dd_n_with_np5"] = int(len(okd))
ext["dd_pe_norm5_median"] = float((okd.mcap / okd.np5).median())
ent = {}
for e in dd["entries"]:  # rev cao nhất / dd_date mới nhất thắng (append-only)
    k = e["ticker"]
    if k not in ent or (e.get("dd_date") or "") >= (ent[k].get("dd_date") or ""):
        ent[k] = e
z = pd.DataFrame([{"ticker": k, "center": v.get("center"), "price_ref": v.get("price_ref")} for k, v in ent.items()])
z = z.merge(dnow[["ticker", "Price", "PE", "PB", "np_ttm", "np5", "mcap"]], on="ticker", how="left")
z["pe_at_center"] = z["PE"] * z["center"] / z["Price"]
z["price_over_center_now"] = z["Price"] / z["center"]
z["eps_ratio5"] = z["np_ttm"] / z["np5"]
z.to_csv(os.path.join(OUT, "dd_set_now.csv"), index=False, float_format="%.4f")
zz = z[z["PE"] > 0]
ext["dd_pe_at_center_median"] = float(zz["pe_at_center"].median())
ext["dd_pe_now_median_pos"] = float(zz["PE"].median())
ext["dd_price_over_center_now_median"] = float(z["price_over_center_now"].median())
ext["dd_n_pe_pos"] = int(len(zz))
# (c) phản thực tế: nếu EPS ratio hồi về trung vị 10Y ⇒ P/E TTM tương đương & phân vị 10Y của nó
hist10 = B[B.time >= tnow - pd.DateOffset(years=10)]
med_ratio = float(hist10["eps_ttm_over_avg5"].median())
pe_cf = float(last["pe_norm_np5"]) / med_ratio
ext["cf_pe_if_eps_ratio_at_10y_median"] = pe_cf
ext["cf_pe_if_eps_ratio_at_10y_median_pct10y"] = float(100 * (hist10["pe_cap10"].iloc[:-1] < pe_cf).mean())
ext["eps_ratio5_10y_median"] = med_ratio
# composite phản thực tế (rolling 10Y tháng): thay P/E bằng P/E chuẩn hoá 5Y, spread bằng EY chuẩn hoá
ext["cf_composite_norm5"] = float(np.mean([last["p10_pe_norm_np5"], last["p10_pb_cap10"],
                                           100 - last["p10_spread_norm5"]]))
ext["composite_monthly_replica"] = float(np.mean([last["p10_pe_cap10"], last["p10_pb_cap10"],
                                                  100 - last["p10_spread"]]))
ext["cf_composite_ddlike"] = float(np.mean([last["p10_pe_ddlike_cap"], last["p10_pb_ddlike_med"],
                                            100 - roll_pct(100 / B["pe_ddlike_cap"] - B["deposit_rate"])[-1]]))
# (d) P/E công bằng với ROE chuẩn hoá (trung vị 10Y) — H3
roe_med = float(hist10["roe_agg"].median())
ext["roe_10y_median"] = roe_med
ext["fair_pe_r135_g6_roe_now"] = (1 - .06 / roe) * 1.06 / (.135 - .06)
ext["fair_pe_r135_g6_roe_med"] = (1 - .06 / roe_med) * 1.06 / (.135 - .06)
# implied r tại P/E trung vị 2014-19 (15,55, radar daily), g=6%, ROE trung vị 10Y — cho thấy "lịch sử" ngầm định r thấp hơn
pe_hist = summ["h5"]["pe_2014_2019"]["median"]
ext["implied_r_at_pe_2014_19_median_g6_roemed"] = brentq(
    lambda r_: (1 - .06 / roe_med) * 1.06 / (r_ - .06) - pe_hist, 0.0601, 0.5)
summ["ext"] = ext

import value_radar  # noqa: E402  (chỉ đọc cache, update=False ⇒ không chạm BQ)
vr = value_radar.load_series(update=False).dropna(subset=["score"]).iloc[-1]
ext["radar_now"] = {k: (float(vr[k]) if not isinstance(vr[k], (str, pd.Timestamp)) else str(vr[k]))
                    for k in ("time", "score", "score_expanding", "p_pe", "p_pb", "p_sp", "p_pe_e", "p_pb_e",
                              "p_sp_e", "pe_cap10", "pb_cap10", "spread", "deposit_rate")}
ext["pe_cap10_10y_median_monthly"] = float(hist10["pe_cap10"].median())
ext["pb_cap10_10y_median_monthly"] = float(hist10["pb_cap10"].median())
summ["ext"] = ext

json.dump(summ, open(os.path.join(OUT, "summary.json"), "w"), indent=1, ensure_ascii=False, sort_keys=True,
          default=lambda o: o.item() if hasattr(o, "item") else str(o))
print("OK", summ["asof"], "months", summ["n_months"])
