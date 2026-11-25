# -*- coding: utf-8 -*-
"""f_proxy_diag.py — (a) IC36 đơn biến từng proxy (PRELOCK §7); (b) delta sửa lỗi 1+2 so vòng 1 trên CÙNG dòng, CÙNG nhãn;
(c) tách ảnh hưởng mã vắng BQ lên universe EW; (d) chuỗi thị trường (mô tả); (e) chi tiết cảnh báo đắt VNM + phân vị độ trễ.
Out: proxy_ic.csv, diag2.json."""
import os, json
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "out"); SEED = 20261124
p = pd.read_parquet(os.path.join(OUT, "vp2.parquet"))
u = p[p.in_universe & (p.ym >= "2014-01") & (p.ym <= "2023-10")].copy()
u["q"] = pd.PeriodIndex(u.ym, freq="M").month.isin([3, 6, 9, 12]); u["year"] = u.ym.str[:4].astype(int)
P = {"E/P (LN TTM/vốn hoá)": u.ep, "B/P": u.bp, "S/P": u.sp, "CFO/P": u.cfo_ttm / u.mc, "EBIT/EV": u.ebit_ttm / u.ev.where(u.ev > 0), "Cổ tức tiền/P (DY)": u.div_ttm / u.mc,
     "Payout 3 năm": u.payout, "ROE TTM": u.roe, "ROE trung vị 5 năm": u.roe_tc5, "ROE thấp nhất 5 năm": u.roe_min5, "ROIC 5 năm": u.roic5.clip(-1, 1), "ROA": u.roa,
     "Biên gộp": u.gpm, "Biên ròng TTM": u.npm, "Biên ròng trung vị 5 năm": u.npm_med5, "Độ lệch chuẩn ROE 5 năm (âm = ổn định tốt)": -u.roe_sd5,
     "Tăng trưởng doanh thu TTM": u.revg, "Tăng trưởng LN TTM": u.npg, "Tăng trưởng vốn chủ 1 năm": u.E / u.E_1y.where(u.E_1y > 0) - 1,
     "Capex/CFO (âm)": -(u.capex_ttm / u.cfo_ttm.where(u.cfo_ttm > 0)).clip(-5, 5), "Vòng quay tiền (âm)": -u.cashcycle.clip(-1000, 2000),
     "Nợ vay/EBIT (âm)": -(u.debt / u.ebit_ttm.where(u.ebit_ttm > 0)).clip(0, 30), "Nợ vay/vốn chủ (âm)": -(u.debt / u.E.where(u.E > 0)).clip(0, 10),
     "Khả năng trả lãi IntCov": u.intcov.clip(-50, 200), "Tiền ròng/vốn hoá": (u.cash - u.debt) / u.mc, "Vốn hoá (log)": np.log(u.mc), "GTGD trung vị (log)": np.log(u.tv.where(u.tv > 0)),
     "Risk_Rating (âm)": -u.risk_rating, "Beta (âm)": -u.beta, "FSCORE": u.fscore, "Rating 8L (âm = tốt)": -u.rating,
     "Rẻ so lịch sử bội số của mã (REL)": u.lv_REL, "Rẻ so trung vị giá 5 năm của mã (N0)": u.lv_N0,
     "RIM-VN D0": u.lv_D0, "EPV": u.lv_EPV, "DDM": u.lv_DDM, "Bội số ngành MULT": u.lv_MULT, "Hedonic HEDf": u.lv_HEDf, "Tổ hợp ENS1w": u.lv_ENS1w}
def icset(x, era):
    d = u[u.q & (u.ym <= "2019-12" if era == "IS" else u.ym >= "2020-01")].assign(x=x)[["ym", "year", "x", "ex36"]].replace([np.inf, -np.inf], np.nan).dropna()
    r = d.groupby("ym").filter(lambda g: len(g) >= 30).groupby(["year", "ym"]).apply(lambda g: g.x.rank().corr(g.ex36.rank())).reset_index(name="ic")
    if len(r) == 0:
        return np.nan, np.nan, np.nan, 0
    ys = r.year.unique(); rng = np.random.RandomState(SEED); by = {y: r[r.year == y].ic.values for y in ys}
    bs = [np.concatenate([by[y] for y in rng.choice(ys, len(ys), replace=True)]).mean() for _ in range(2000)]
    return r.ic.mean(), np.percentile(bs, 2.5), np.percentile(bs, 97.5), int(len(d) / max(r.ym.nunique(), 1))
rows = []
for k, x in P.items():
    a = icset(x, "IS"); b = icset(x, "OOS")
    rows.append({"proxy": k, "ic36_IS": a[0], "IS_lo": a[1], "IS_hi": a[2], "ic36_OOS": b[0], "OOS_lo": b[1], "OOS_hi": b[2], "n_per_date_IS": a[3], "n_per_date_OOS": b[3],
                 "coverage": float(np.isfinite(pd.to_numeric(x, errors="coerce").replace([np.inf, -np.inf], np.nan)).mean())})
pr = pd.DataFrame(rows); pr.to_csv(os.path.join(OUT, "proxy_ic.csv"), index=False)
print(pr.round(3).to_string(index=False))
D = {}
# (b) delta sửa lỗi 1+2: D0 vòng 1 (lv_D0_fix) vs D0 mới, cùng dòng BQ, cùng nhãn ex36 mới
old = pd.read_parquet(os.path.join(HERE, "..", "..", "dcf_vn_redesign_20261124", "out", "vp.parquet") if os.path.exists(os.path.join(HERE, "..", "..", "dcf_vn_redesign_20261124", "out", "vp.parquet"))
                      else "/home/trido/thanhdt/WorkingClaude/wt-dcf-vn-redesign-20261124/agents/Taylor/research/dcf_vn_redesign_20261124/out/vp.parquet", columns=["ticker", "ym", "lv_D0_fix"])
m = u.merge(old, on=["ticker", "ym"], how="inner"); m = m[m.lv_D0.notna() & m.lv_D0_fix.notna()]
d = (m.lv_D0 - m.lv_D0_fix)
D["fix12_D0"] = {"n": int(len(m)), "corr": float(np.corrcoef(m.lv_D0, m.lv_D0_fix)[0, 1]), "share_abs_gt_0.10": float((d.abs() > 0.10).mean()), "share_abs_gt_0.25": float((d.abs() > 0.25).mean()),
                 "share_sign_flip": float((np.sign(m.lv_D0) != np.sign(m.lv_D0_fix)).mean()), "share_zone_flip_125": float(((m.lv_D0 >= np.log(1.25)) != (m.lv_D0_fix >= np.log(1.25))).mean())}
for era, mk in (("IS", m.ym <= "2019-12"), ("OOS", m.ym >= "2020-01")):
    q = m[mk & m.q & m.ex36.notna()]
    D["fix12_D0"][f"ic36_{era}_cu"] = float(q.groupby("ym").apply(lambda g: g.lv_D0_fix.rank().corr(g.ex36.rank())).mean())
    D["fix12_D0"][f"ic36_{era}_moi"] = float(q.groupby("ym").apply(lambda g: g.lv_D0.rank().corr(g.ex36.rank())).mean())
# (c) universe EW: chỉ BQ vs BQ + mã vắng (rổ lập tại as-of, giữ 36T; H = −50%)
for era, mk in (("IS", u.ym <= "2019-12"), ("OOS", u.ym >= "2020-01")):
    x = u[mk]; a = x[x.src == "BQ"]
    D[f"ew36_{era}"] = {"BQ_raw_mean_simple_ret": float(np.expm1(a.fwd36_raw).mean()), "ALL_h50": float(np.expm1(x.fwd36_h50).mean()), "ALL_h0": float(np.expm1(x.fwd36_h0).mean()),
                        "ALL_h100": float(np.expm1(x.fwd36_h100).mean()), "VND_h50": float(np.expm1(x[x.src == "VND"].fwd36_h50).mean()), "share_rows_VND": float((x.src == "VND").mean()),
                        "share_rows_ended36": float(x.ended36.mean()), "n_tickers_ended": int(x[x.ended36].ticker.nunique())}
# mã vắng BQ có bị mô hình xếp "rẻ" không?
v = u[u.src == "VND"]
D["dead_names"] = {"rows": int(len(v)), "tickers": int(v.ticker.nunique()), "median_lv_ENS1w": float(v.lv_ENS1w.median()), "share_cheap_125_ENS1w": float((v.lv_ENS1w >= np.log(1.25)).mean()),
                   "share_warn_067_ENS1w": float((v.lv_ENS1w <= np.log(0.67)).mean()), "share_cheap_125_D0": float((v.lv_D0 >= np.log(1.25)).mean()), "share_warn_067_D0": float((v.lv_D0 <= np.log(0.67)).mean()),
                   "BQ_share_cheap_125_ENS1w": float((u[u.src == "BQ"].lv_ENS1w >= np.log(1.25)).mean()), "BQ_share_warn_067_ENS1w": float((u[u.src == "BQ"].lv_ENS1w <= np.log(0.67)).mean()),
                   "ex36_mean_VND": float(v.ex36.mean()), "ex36_mean_BQ": float(u[u.src == "BQ"].ex36.mean())}
# (d) chuỗi thị trường (mô tả, N nhỏ)
import sys; sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
try:
    import deposit_rate_vn as DR
    dep = pd.DataFrame(DR.DEPOSIT_EVENTS, columns=["time", "dep"]); dep["time"] = pd.to_datetime(dep.time)
except Exception as e:
    dep = None
mk = []
for y in range(2014, 2024):
    x = u[u.ym == f"{y}-06"] if y == 2023 else u[u.ym == f"{y}-12"]
    r = {"asof": x.ym.iloc[0], "median_VP_ENS1w": float(np.exp(x.lv_ENS1w.median())), "median_VP_D0": float(np.exp(x.lv_D0.median())), "share_cheap": float((x.lv_ENS1w >= np.log(1.25)).mean()),
         "share_warn": float((x.lv_ENS1w <= np.log(0.67)).mean()), "ew36_simple": float(np.expm1(x.fwd36_h50).mean()), "median_PE": float((1 / x.ep.where(x.ep > 0)).median())}
    if dep is not None:
        r["dep12m"] = float(dep[dep.time <= pd.Timestamp(x.time.max())].dep.iloc[-1])
    mk.append(r)
D["market_by_year"] = mk; mkd = pd.DataFrame(mk)
D["market_corr_medianVP_vs_ew36"] = {"ENS1w": float(mkd.median_VP_ENS1w.corr(mkd.ew36_simple)), "D0": float(mkd.median_VP_D0.corr(mkd.ew36_simple)), "n": len(mkd),
                                     "median_PE(-)": float((-mkd.median_PE).corr(mkd.ew36_simple)), "dep12m": float(mkd.dep12m.corr(mkd.ew36_simple)) if "dep12m" in mkd else None}
# (e) VNM 2015–2018
x = p[(p.ticker == "VNM") & (p.ym >= "2014-01") & (p.ym <= "2022-12")][["ym", "Close", "lv_D0", "lv_ENS1w", "lv_ENS2", "lv_L2_ENS1w", "lv_N0"]].set_index("ym")
pk = x.Close.idxmax(); w = {}
for c in ("lv_D0", "lv_ENS1w", "lv_N0", "lv_L2_ENS1w"):
    run = (x[c] <= np.log(0.67)).astype(int).rolling(6).sum() >= 6; first = run[run].index.min() if run.any() else None
    w[c] = {"first_warning": first, "VP_at_2015-12": float(np.exp(x.loc["2015-12", c])), "VP_at_peak": float(np.exp(x.loc[pk, c])),
            "months_warning_to_peak": None if first is None else (pd.Period(pk, "M") - pd.Period(first, "M")).n,
            "ret_first_to_peak": None if first is None else float(x.loc[pk, "Close"] / x.loc[first, "Close"] - 1),
            "ret_first_plus36": None if first is None else float(x.Close.get(str(pd.Period(first, "M") + 36), np.nan) / x.loc[first, "Close"] - 1),
            "ret_peak_to_2022-12": float(x.loc["2022-12", "Close"] / x.loc[pk, "Close"] - 1)}
D["VNM"] = {"peak_ym": pk, "detail": w}
json.dump(D, open(os.path.join(OUT, "diag2.json"), "w"), indent=1, default=str, ensure_ascii=False)
print(json.dumps({k: D[k] for k in ("fix12_D0", "ew36_IS", "ew36_OOS", "dead_names", "market_corr_medianVP_vs_ew36", "VNM")}, default=str, ensure_ascii=False, indent=0))
print(mkd.round(3).to_string(index=False))
