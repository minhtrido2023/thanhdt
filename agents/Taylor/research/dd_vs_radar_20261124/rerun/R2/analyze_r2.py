#!/usr/bin/env python3
"""R2 — chạy lại R1 cho NHẤT QUÁN theo QUANT_SKEPTIC_R1 (job Taylor_20261123_174703).

KHÔNG sửa R1. Tái dùng đầu vào ĐÃ KHOÁ của R1 (md5 kiểm ở đầu script, lệch ⇒ dừng):
  R1/calc/panel_monthly.parquet, R1/calc/out/basket_monthly.csv (chỉ đọc cột pe_cap10/pb_cap10 để parity),
  rerun/inputs/dd_price_zones_da6018d95.json  (BẢN SAO ĐÓNG BĂNG = đúng bản R1 đã băm 74539e4…),
  rerun/inputs/value_radar_series_frozen.csv  (= data/value_radar_series.csv R1 đã băm 11aa152…).
Lãi huy động: deposit_rate_vn.deposit_events_df() (Big-4 12M thuần) và effective_deposit_events_df()
(Big-4 ∨ CCTG, cơ sở radar hiện dùng) — snapshot ghi ra out/deposit_*_snapshot.csv để khoá.

Mục (đánh số theo dispatch):
 (1) phản thực 'lợi nhuận đỉnh' NHẤT QUÁN ⇒ dải
 (2) H3 nhất quán (lợi nhuận chuẩn hoá ↔ ROE chuẩn hoá; dạng P/B) + phân rã r-vs-ROE trong script
 (3) spread + composite trên MỘT cơ sở lãi huy động (Big-4 thuần; backfill CCTG hằng chênh lệch)
 (4) H1 robustness: bỏ Vingroup/BSR, trung vị theo mã, độ phủ np5 theo thời gian, đỉnh toàn chuỗi vs 10Y
Chạy: python analyze_r2.py → out/*.csv + out/summary_r2.json   (threads=1, tất định)
"""
import os
for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[k] = "1"
import hashlib
import json
import sys

import numpy as np
import pandas as pd
from scipy.optimize import brentq

W = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, W)
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, "..", ".."))
R1C = os.path.join(BASE, "R1", "calc")
INP = os.path.join(BASE, "rerun", "inputs")
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

LOCK = {os.path.join(R1C, "panel_monthly.parquet"): "9dfdf1e6b52263162115ec4ee8f3e87d",
        os.path.join(INP, "dd_price_zones_da6018d95.json"): "74539e4cbe9af2dd49a083ae77af470f",
        os.path.join(INP, "value_radar_series_frozen.csv"): "11aa15262bc6dd6481f6faa10a69b054",
        os.path.join(R1C, "out", "basket_monthly.csv"): "87654f9ef7bb49792c1de06b33822da5"}
for f, h in LOCK.items():
    got = hashlib.md5(open(f, "rb").read()).hexdigest()
    if got != h:
        sys.exit(f"INPUT MD5 MISMATCH {f}: {got} != {h}")

BANK = 8355.0
VINGROUP = {"VIC", "VHM", "VRE", "VPL"}
EXCL_CONC = VINGROUP | {"BSR"}
FLOOR = pd.Timestamp("2008-01-01")
WIN, MINP = 120, 24
R_DD = (0.123, 0.135)
G_GRID = (0.04, 0.05, 0.06, 0.07, 0.08)


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


def fair_pe(roe, r, g):
    return (1 - g / roe) * (1 + g) / (r - g)


def fair_pb(roe, r, g):
    return fair_pe(roe, r, g) * roe


# ---------------------------------------------------------------- panel (y hệt R1)
p = pd.read_parquet(os.path.join(R1C, "panel_monthly.parquet"))
p["time"] = pd.to_datetime(p["time"])
p = p.sort_values(["ticker", "time"]).reset_index(drop=True)
p["mcap"] = p["Price"] * p["OShares"]
p["book"] = p["BVPS"] * p["OShares"]
p["np_ttm"] = p[["NP_P0", "NP_P1", "NP_P2", "NP_P3"]].sum(axis=1, min_count=4)
p["is_bank"] = p["ICB_Code"] == BANK
p["per"] = p["time"].dt.to_period("M")
p = p.set_index(["ticker", "per"]).sort_index()


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


p["np5"], p["n5"] = lagged_mean(p["np_ttm"], 5, 5)
p["np10"], _ = lagged_mean(p["np_ttm"], 10, 7)
p = p.reset_index()
# xuất tỷ lệ np_ttm/np5 theo mã-tháng cho D2 dùng (ROE chuẩn hoá theo mã, PIT)
p.loc[p["time"] >= pd.Timestamp("2010-01-01"),
      ["ticker", "per", "time", "np_ttm", "np5", "book"]].assign(per=lambda x: x["per"].astype(str)) \
    .to_parquet(os.path.join(OUT, "ticker_np5_ratio.parquet"), index=False)


def top100(d):
    d = d.copy()
    d["pb_i"] = d["mcap"] / d["book"]
    t = d.nlargest(300, "mcap")
    return t[np.isfinite(t["pb_i"]) & (t["pb_i"] > 0)].nlargest(100, "mcap").copy()


def set_stats(t, excl=None):
    """Mọi số trên MỘT tập S = top-100 có np5>0 & np_ttm>0 (cùng trọng số cap10 tái chuẩn trên S)."""
    if excl:
        t = t[~t["ticker"].isin(excl)]
    w_all = (t["mcap"] / t["mcap"].sum()).values
    pe = t["PE"].values.astype(float)
    okpe = np.isfinite(pe) & (pe > 0)
    r = {"pe_cap10": harm(cap_weights(w_all[okpe]), pe[okpe]) if okpe.sum() > 30 else np.nan}
    # độ phủ np5 trên toàn top-100 (mọi mã, kể cả lỗ): theo số mã và theo vốn hoá
    has = np.isfinite(t["np5"])
    r["cov_np5_count"] = float(has.mean())
    r["cov_np5_w"] = float(t.loc[has, "mcap"].sum() / t["mcap"].sum())
    S = t[np.isfinite(t["np5"]) & (t["np5"] > 0) & (t["np_ttm"] > 0)]
    if len(S) < 30:
        return r
    ws = cap_weights((S["mcap"] / S["mcap"].sum()).values)
    r["S_n"] = len(S)
    r["S_cov_w"] = float(S["mcap"].sum() / t["mcap"].sum())
    r["S_pe_ttm"] = harm(ws, (S["mcap"] / S["np_ttm"]).values)
    r["S_pe_n5"] = harm(ws, (S["mcap"] / S["np5"]).values)
    r["S_ratio_w"] = r["S_pe_n5"] / r["S_pe_ttm"]            # = Σw·EY_ttm / Σw·EY_n5
    r["S_ratio_agg"] = S["np_ttm"].sum() / S["np5"].sum()   # định nghĩa R1 (tổng/tổng)
    r["S_ratio_med"] = float((S["np_ttm"] / S["np5"]).median())
    r["S_roe_ttm"] = S["np_ttm"].sum() / S["book"].sum()
    r["S_roe_n5"] = S["np5"].sum() / S["book"].sum()
    r["S_pb"] = harm(ws, (S["mcap"] / S["book"]).values)
    return r


rows = []
for tm, d in p[p["time"] >= FLOOR].groupby("time"):
    t = top100(d)
    if len(t) < 50:
        continue
    a = set_stats(t)
    b = {f"xc_{k}": v for k, v in set_stats(t, EXCL_CONC).items()}
    rows.append({"time": tm, **a, **b})
B = pd.DataFrame(rows).sort_values("time").reset_index(drop=True)

# parity với R1 (pe_cap10 tháng)
b1 = pd.read_csv(os.path.join(R1C, "out", "basket_monthly.csv"), parse_dates=["time"])
par = B[["time", "pe_cap10"]].merge(b1[["time", "pe_cap10", "eps_ttm_over_avg5", "pe_norm_np5", "pb_cap10",
                                        "spread", "spread_norm5", "deposit_rate"]],
                                    on="time", suffixes=("", "_r1"))
S = {"parity_pe_cap10_maxabs_vs_r1": float((par["pe_cap10"] - par["pe_cap10_r1"]).abs().max()),
     "n_months": int(len(B)), "asof": str(B["time"].iloc[-1].date())}
B = B.merge(b1[["time", "eps_ttm_over_avg5", "pe_norm_np5", "pb_cap10", "roe_agg"]], on="time", how="left")

last = B.iloc[-1]
tnow = B["time"].iloc[-1]
h10 = B[B["time"] > tnow - pd.DateOffset(years=10)]          # 120 tháng kể cả hiện tại
h10x = h10.iloc[:-1]                                           # quá khứ (cho phân vị)
pe_now = float(last["pe_cap10"])
pe_med10 = float(h10x["pe_cap10"].median())
S["pe_now"] = pe_now
S["pe_cap10_10y_median"] = pe_med10
gap = np.log(pe_med10 / pe_now)
S["ln_gap_pe_vs_10y_median"] = gap

# ================================================================ (1) phản thực lợi nhuận đỉnh — dải
cf = {}
# A. công thức skeptic: PE_ttm × ratio_now / ratio_med (định nghĩa R1 tổng/tổng, rổ R1)
rn, rm = float(last["eps_ttm_over_avg5"]), float(h10x["eps_ttm_over_avg5"].median())
cf["A_r1ratio_pe_x_ratio"] = {"ratio_now": rn, "ratio_med10": rm, "pe_cf": pe_now * rn / rm}
# B. R1 gốc (pe_norm5 ÷ ratio_med; tập/trọng số KHÔNG khớp) — chỉ để đối chiếu
cf["B_r1_original_inconsistent"] = {"pe_cf": float(last["pe_norm_np5"]) / rm}
# C. CÙNG TẬP S, ratio trọng số (S_ratio_w): pe_cf = S_pe_ttm × ratio_now/ratio_med, quy về rổ radar
#    bằng hệ số pe_cap10/S_pe_ttm hôm nay (để so được với trung vị 10Y của chính pe_cap10)
for lab, col in (("C_sameset_wratio", "S_ratio_w"), ("D_sameset_aggratio", "S_ratio_agg"),
                 ("E_sameset_medratio", "S_ratio_med")):
    rnow, rmed = float(last[col]), float(h10x[col].median())
    cf[lab] = {"ratio_now": rnow, "ratio_med10": rmed, "pe_cf": pe_now * rnow / rmed}
# F. so trên chính tập S: S_pe_ttm hiện tại vs trung vị 10Y của S_pe_ttm (không cần quy đổi)
spt_med = float(h10x["S_pe_ttm"].median())
cf["F_sameset_own_anchor"] = {"S_pe_ttm_now": float(last["S_pe_ttm"]), "S_pe_ttm_med10": spt_med,
                              "ratio_now": float(last["S_ratio_w"]), "ratio_med10": float(h10x["S_ratio_w"].median()),
                              "pe_cf": float(last["S_pe_ttm"]) * float(last["S_ratio_w"]) / float(h10x["S_ratio_w"].median())}
xr_now, xr_med = float(last["xc_S_ratio_w"]), float(h10x["xc_S_ratio_w"].median())
xpt_now, xpt_med = float(last["xc_S_pe_ttm"]), float(h10x["xc_S_pe_ttm"].median())
cf["G_excl_vingroup_bsr_own_anchor"] = {"S_pe_ttm_now": xpt_now, "S_pe_ttm_med10": xpt_med, "ratio_now": xr_now,
                                        "ratio_med10": xr_med, "pe_cf": xpt_now * xr_now / xr_med}
for k, v in cf.items():
    own = "S_pe_ttm_now" in v
    anchor_now, anchor_med = (v["S_pe_ttm_now"], v["S_pe_ttm_med10"]) if own else (pe_now, pe_med10)
    hcol = ("xc_S_pe_ttm" if k.startswith("G_") else "S_pe_ttm") if own else "pe_cap10"
    v["share_of_log_gap_explained"] = float(np.log(v["pe_cf"] / anchor_now) / np.log(anchor_med / anchor_now))
    v["pe_cf_pct10y_own_series"] = float(100 * (h10x[hcol] < v["pe_cf"]).mean())
S["cf_peak_earnings"] = cf
cons = [cf[k]["share_of_log_gap_explained"] for k in ("A_r1ratio_pe_x_ratio", "C_sameset_wratio",
                                                       "D_sameset_aggratio", "F_sameset_own_anchor")]
S["cf_peak_band_consistent"] = [float(min(cons)), float(max(cons))]

# ================================================================ (4) H1 robustness
h1 = {}
s_all = B.set_index("time")["eps_ttm_over_avg5"]
h1["ratio_now"] = float(s_all.iloc[-1])
h1["ratio_full_max"] = float(s_all.max())
h1["ratio_full_argmax"] = str(s_all.idxmax().date())
h1["ratio_full_pct_now"] = float(100 * (s_all.iloc[:-1] < s_all.iloc[-1]).mean())
h1["ratio_10y_max_excl_now"] = float(h10x["eps_ttm_over_avg5"].max())
h1["ratio_10y_is_window_peak"] = bool(s_all.iloc[-1] >= h10["eps_ttm_over_avg5"].max())
h1["months_full_ge_now"] = [str(t.date()) for t, v in s_all.iloc[:-1].items() if v >= s_all.iloc[-1]]
for col in ("S_ratio_w", "S_ratio_med", "xc_S_ratio_agg", "xc_S_ratio_w", "xc_S_ratio_med"):
    s = B[col]
    h1[col] = {"now": float(s.iloc[-1]), "med10": float(h10x[col].median()),
               "p10_now": float(roll_pct(s)[-1]), "full_max": float(s.max()),
               "full_argmax": str(B.loc[s.idxmax(), "time"].date())}
cov = B[["time", "cov_np5_count", "cov_np5_w", "S_cov_w"]].copy()
cov["year"] = cov["time"].dt.year
covy = cov.groupby("year")[["cov_np5_count", "cov_np5_w", "S_cov_w"]].median()
covy.to_csv(os.path.join(OUT, "h1_np5_coverage_by_year.csv"), float_format="%.3f")
h1["coverage_np5_w_by_year"] = {int(k): round(float(v), 3) for k, v in covy["cov_np5_w"].items()}
h1["coverage_np5_w_now"] = float(last["cov_np5_w"])
# đỉnh 2011-03 đo trên độ phủ bao nhiêu?
pk = B.loc[B["eps_ttm_over_avg5"].idxmax()]
h1["coverage_at_full_peak"] = {"time": str(pk["time"].date()), "cov_np5_w": float(pk["cov_np5_w"]),
                               "cov_np5_count": float(pk["cov_np5_count"])}
S["h1"] = h1

# ================================================================ (2) H3 nhất quán + phân rã r-vs-ROE
roe_ttm = float(last["S_roe_ttm"])
roe_n5 = float(last["S_roe_n5"])
roe_med10 = float(h10x["S_roe_ttm"].median())
ratio_now_w, ratio_med_w = float(last["S_ratio_w"]), float(h10x["S_ratio_w"].median())
roe_dp = roe_ttm * ratio_med_w / ratio_now_w      # 'khử đỉnh': đưa tỷ lệ EPS_ttm/TB5Y về trung vị 10Y
pb_S = float(last["S_pb"])
pb_hist = float(h10x["S_pb"].median())
pe_S_ttm, pe_S_n5 = float(last["S_pe_ttm"]), float(last["S_pe_n5"])
ROES = (("ttm_hold", roe_ttm), ("depeaked", roe_dp), ("med10", roe_med10), ("n5_over_book_now", roe_n5))
h3 = {"S_roe_ttm": roe_ttm, "S_roe_depeaked": roe_dp, "S_roe_ttm_med10": roe_med10, "S_roe_n5_over_book_now": roe_n5,
      "S_pb_now": pb_S, "S_pb_med10": pb_hist, "S_pe_ttm": pe_S_ttm, "S_pe_n5": pe_S_n5,
      "note": "Cùng tập S. So ở dạng P/B: giá = P/B_công_bằng(ROE) × sổ sách ⇒ không cần chọn 'lợi nhuận nào' cho mẫu số "
              "P/E; ROE giả định là biến duy nhất. P/E công bằng trên lợi nhuận X = P/B_công_bằng/ROE_X (cặp nhất quán). "
              "n5_over_book_now = TB lợi nhuận 5Y / sổ sách HÔM NAY ⇒ chứa kéo tụt do tăng trưởng sổ sách (cận dưới, không phải ước lượng trung tâm)."}
grid = []
for r_ in R_DD:
    for g_ in G_GRID:
        row = {"r": r_, "g": g_}
        for lab, roe_ in ROES:
            fpb = fair_pb(roe_, r_, g_)
            row[f"fair_pb_{lab}"] = fpb
            row[f"fair_pe_ttm_equiv_{lab}"] = fpb / roe_ttm       # P/E TTM tương đương của giá công bằng
            row[f"mkt_vs_fair_{lab}"] = pb_S / fpb - 1             # >0 ⇒ thị trường TRÊN công bằng kiểu DD
        grid.append(row)
G = pd.DataFrame(grid)
G.to_csv(os.path.join(OUT, "h3_consistent_grid.csv"), index=False, float_format="%.4f")
h3["grid"] = grid
for lab, _ in ROES:
    for r_ in R_DD:
        v = G[G.r == r_][f"mkt_vs_fair_{lab}"]
        h3[f"band_mkt_vs_fair_{lab}_r{int(round(r_*1000))}"] = [float(v.min()), float(v.max())]

# phân rã ở dạng P/B (tách được CHÍNH XÁC, không có phần dư/không phụ thuộc thứ tự):
# ln P/B_công_bằng = ln(ROE−g) + ln(1+g) − ln(r−g).  Mốc lịch sử: P/B trung vị 10Y của S với ROE trung vị 10Y của S
# ⇒ r_hist giải từ fair_pb(ROE_med10, r_hist, g) = P/B_hist.  Mốc DD: (r_DD, g, ROE_x).
# gap = ln(P/B_hist / P/B_DD) = [ln(r_DD−g) − ln(r_hist−g)]  (phần r)  +  [ln(ROE_med10−g) − ln(ROE_x−g)]  (phần ROE)
dec = []
for r_ in R_DD:
    for g_ in G_GRID:
        try:
            r_hist = brentq(lambda x: fair_pb(roe_med10, x, g_) - pb_hist, g_ + 1e-4, 0.6)
        except ValueError:
            r_hist = np.nan
        for lab, roe_x in ROES:
            part_r = np.log(r_ - g_) - np.log(r_hist - g_)
            part_roe = np.log(roe_med10 - g_) - np.log(roe_x - g_)
            tot = np.log(pb_hist / fair_pb(roe_x, r_, g_))
            dec.append({"r_dd": r_, "g": g_, "roe_dd_basis": lab, "roe_dd": roe_x, "roe_hist": roe_med10,
                        "pb_hist_anchor": pb_hist, "r_hist_implied": r_hist, "fair_pb_dd": fair_pb(roe_x, r_, g_),
                        "ln_gap_total": tot, "part_r": part_r, "part_roe": part_roe,
                        "check_sum": tot - part_r - part_roe,
                        "share_r": part_r / tot, "share_roe": part_roe / tot})
DEC = pd.DataFrame(dec)
DEC.to_csv(os.path.join(OUT, "h3_r_vs_roe_decomp.csv"), index=False, float_format="%.4f")
h3["decomp_check_maxabs"] = float(DEC["check_sum"].abs().max())
h3["decomp"] = dec
S["h3"] = h3

# ================================================================ (3) spread + composite — MỘT cơ sở lãi huy động
from deposit_rate_vn import deposit_events_df, effective_deposit_events_df  # noqa: E402
big4 = deposit_events_df()[["time", "deposit_rate"]].sort_values("time")
eff = effective_deposit_events_df()[["time", "deposit_rate"]].sort_values("time")
big4.to_csv(os.path.join(OUT, "deposit_big4_snapshot.csv"), index=False)
eff.to_csv(os.path.join(OUT, "deposit_effective_snapshot.csv"), index=False)
cctg_now = float(eff["deposit_rate"].iloc[-1])
big4_now = float(big4["deposit_rate"].iloc[-1])
PREM = cctg_now - big4_now          # chênh CCTG−Big-4 đo ở phần chồng lấn (duy nhất có dữ liệu)
sp = {"big4_now": big4_now, "effective_now": cctg_now, "cctg_premium_overlap_pp": PREM,
      "cctg_backfill_note": "Không có lịch sử CCTG trước 2026-09-30 ⇒ 'backfill' duy nhất dựng được = Big-4 + chênh hằng "
                            "(đo ở đoạn chồng lấn). Phân vị là hàm hạng ⇒ cộng hằng số cho CẢ chuỗi không đổi phân vị: "
                            "bản backfill TRÙNG Big-4 thuần theo cấu trúc (kiểm số bên dưới)."}


def dep_on(times, ev, add=0.0):
    x = pd.merge_asof(pd.DataFrame({"time": pd.to_datetime(times)}).sort_values("time"), ev, on="time",
                      direction="backward")
    return x["deposit_rate"].values + add


# --- (3a) THÁNG, cùng chuỗi R1 (pe_cap10, pe_norm_np5, pb_cap10)
M = B[["time", "pe_cap10", "pe_norm_np5", "pb_cap10"]].copy()
for lab, ev, add in (("eff", eff, 0.0), ("big4", big4, 0.0), ("cctgbf", big4, PREM)):
    dep = dep_on(M["time"], ev, add)
    M[f"sp_{lab}"] = 100 / M["pe_cap10"] - dep
    M[f"spn5_{lab}"] = 100 / M["pe_norm_np5"] - dep
p_pe, p_pb, p_pen5 = roll_pct(M["pe_cap10"]), roll_pct(M["pb_cap10"]), roll_pct(M["pe_norm_np5"])
mon = {}
for lab in ("eff", "big4", "cctgbf"):
    ps, psn = roll_pct(M[f"sp_{lab}"]), roll_pct(M[f"spn5_{lab}"])
    mon[lab] = {"spread_now": float(M[f"sp_{lab}"].iloc[-1]), "p10_spread": float(ps[-1]),
                "spread_norm5_now": float(M[f"spn5_{lab}"].iloc[-1]), "p10_spread_norm5": float(psn[-1]),
                "composite_ttm": float(np.mean([p_pe[-1], p_pb[-1], 100 - ps[-1]])),
                "composite_norm5": float(np.mean([p_pen5[-1], p_pb[-1], 100 - psn[-1]]))}
mon["p10_pe_cap10"], mon["p10_pb_cap10"], mon["p10_pe_norm5"] = float(p_pe[-1]), float(p_pb[-1]), float(p_pen5[-1])
sp["monthly"] = mon
# --- (3b) NGÀY, đúng radar (rolling 2500 phiên, min 500) trên 3 cơ sở
rc = pd.read_csv(os.path.join(INP, "value_radar_series_frozen.csv"), parse_dates=["time"]).sort_values("time")
rc = rc.reset_index(drop=True)
day = {}
dpe, dpb = roll_pct(rc["pe_cap10"], 2500, 500), roll_pct(rc["pb_cap10"], 2500, 500)
for lab, ev, add in (("eff", eff, 0.0), ("big4", big4, 0.0), ("cctgbf", big4, PREM)):
    s_ = 100 / rc["pe_cap10"].values - dep_on(rc["time"], ev, add)
    ps = roll_pct(s_, 2500, 500)
    day[lab] = {"spread_now": float(s_[-1]), "p_sp_inverted": float(100 - ps[-1]),
                "p10_spread": float(ps[-1]), "score": float(np.mean([dpe[-1], dpb[-1], 100 - ps[-1]]))}
day["p_pe"], day["p_pb"] = float(dpe[-1]), float(dpb[-1])
sp["daily_radar"] = day
sp["check_cctgbf_equals_big4_monthly"] = float(abs(mon["cctgbf"]["p10_spread"] - mon["big4"]["p10_spread"])
                                              + abs(mon["cctgbf"]["p10_spread_norm5"] - mon["big4"]["p10_spread_norm5"]))
sp["check_cctgbf_equals_big4_daily"] = float(abs(day["cctgbf"]["score"] - day["big4"]["score"]))
S["spread_one_basis"] = sp

# ================================================================ (5) DD set (bản đóng băng) — mô tả, như R1
dd = json.load(open(os.path.join(INP, "dd_price_zones_da6018d95.json")))
S["dd_n_tickers_frozen"] = len({e["ticker"] for e in dd["entries"]})

B.to_csv(os.path.join(OUT, "basket_monthly_r2.csv"), index=False, float_format="%.6g")
json.dump(S, open(os.path.join(OUT, "summary_r2.json"), "w"), indent=1, ensure_ascii=False, sort_keys=True,
          default=lambda o: o.item() if hasattr(o, "item") else str(o))
print("OK", S["asof"], "months", S["n_months"], "parity", S["parity_pe_cap10_maxabs_vs_r1"])
