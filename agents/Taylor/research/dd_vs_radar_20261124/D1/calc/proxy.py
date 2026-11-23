"""D1/G3 + G1(định lượng) + G5 — bộ ước lượng CƠ HỌC kiểu DD (proxy), PIT, tất định.

Proxy = Residual Income trên mỗi đồng sổ sách, công khai các quy ước DD:
  - r_t = 13,5% + β·(lãi huy động 12T hiệu dụng_t − 7,4%)  [V1, neo 03/11/2026 eff=7,4%, β=1]
    (chuỗi lãi huy động = deposit_rate_vn.effective_deposit_events_df, snapshot deposit_effective_snapshot.csv;
     CAVEAT registry: 26 mốc lịch sử neo hồi tố 2026-06-19, không PIT thật cho quá khứ).
  - ROE_ttm = PB/PE (cùng Price thô ⇒ = EPS_ttm/BVPS, PIT theo registry valuation_pe_pb_pcf_ps.md).
  - Biến thể chính "DD": giữ ROE 5 năm (V5: không ép fade ở giai đoạn dự báo), tái đầu tư b=0,5 [UL],
    terminal RONIC=Ke (RI cuối kỳ giữ phẳng vĩnh viễn, không tăng — tức không NPV>0 cho vốn mới).
  - Biến thể "fade": ROE tuyến tính về r trong 10 năm, sau đó RI=0.
  - Biến thể "r_const": như DD nhưng r=13,5% cố định (tách phần do r).
Giá/proxy-tâm = PB / (V/BV). Không cột profit_*; lợi suất kỳ sau từ Close (adj) cuối tháng t+6/t+12.
Không có kịch bản xấu, CK thanh khoản, KTPL… ⇒ proxy ≈ "giá trị THÔ" kiểu DD trước haircut.
"""
import os, json, sys
import numpy as np, pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
B = 0.5; H = 5; FADE = 10
R_ANCHOR = 0.135; DEP_ANCHOR = 7.4
ASOF = pd.Timestamp("2026-11-20")


def vbv_dd(roe, r, g):
    """V/BV — giữ ROE H năm, BV tăng g, sau đó RI phẳng vĩnh viễn (RONIC=Ke cho vốn mới)."""
    v = np.ones_like(roe)
    for t in range(1, H + 1):
        v += (roe - r) * (1 + g) ** (t - 1) / (1 + r) ** t
    v += (roe - r) * (1 + g) ** H / r / (1 + r) ** H
    return v


def vbv_fade(roe, r):
    v = np.ones_like(roe); bv = np.ones_like(roe)
    for t in range(1, FADE + 1):
        roe_t = roe + (r - roe) * t / FADE
        v += (roe_t - r) * bv / (1 + r) ** t
        bv = bv * (1 + B * np.clip(roe_t, 0, None))
    return v


def build():
    dep = pd.read_csv(os.path.join(HERE, "deposit_effective_snapshot.csv"), parse_dates=["time"]).sort_values("time")
    allp = pd.read_parquet(os.path.join(HERE, "panel_all.parquet"))
    uni = pd.read_parquet(os.path.join(HERE, "panel.parquet"))[["time", "ticker", "adv20"]]
    allp = allp.sort_values(["time", "ticker"])
    allp = pd.merge_asof(allp, dep, on="time", direction="backward")
    allp["r"] = R_ANCHOR + (allp["deposit_rate"] - DEP_ANCHOR) / 100.0
    pe, pb = allp["PE"], allp["PB"]
    ok = pb.gt(0) & pe.notna() & pe.ne(0)
    allp["roe_ttm"] = np.where(ok, pb / pe, np.nan)
    allp["roe"] = allp["roe_ttm"].clip(-0.20, 0.45)
    g = B * allp["roe"].clip(lower=0)
    allp["vbv_dd"] = vbv_dd(allp["roe"].values, allp["r"].values, g.values)
    allp["vbv_fade"] = vbv_fade(allp["roe"].values, allp["r"].values)
    allp["vbv_rc"] = vbv_dd(allp["roe"].values, np.full(len(allp), R_ANCHOR), g.values)
    for k in ["dd", "fade", "rc"]:
        v = allp[f"vbv_{k}"]
        allp[f"pv_{k}"] = np.where(v > 0.05, pb / v, np.nan)  # V/BV ≤0,05 ⇒ không định nghĩa (lỗ sâu)
    # lợi suất kỳ sau (Close adj, cuối tháng t+6/t+12) — trên MỌI mã, không chỉ universe
    allp = allp.sort_values(["ticker", "time"])
    allp["ym"] = allp["time"].dt.year * 12 + allp["time"].dt.month
    for h in (6, 12):
        nxt = allp[["ticker", "ym", "Close"]].copy(); nxt["ym"] -= h
        allp = allp.merge(nxt.rename(columns={"Close": f"C{h}"}), on=["ticker", "ym"], how="left")
        allp[f"fwd{h}"] = allp[f"C{h}"] / allp["Close"] - 1
    allp = allp.merge(uni.assign(in_uni=True), on=["time", "ticker"], how="left")
    allp["in_uni"] = allp["in_uni"].fillna(False).astype(bool)
    return allp


def nw_t(x, lag):
    x = np.asarray(x, float); x = x[~np.isnan(x)]; n = len(x); m = x.mean(); e = x - m
    s = (e @ e) / n
    for L in range(1, lag + 1):
        s += 2 * (1 - L / (lag + 1)) * (e[L:] @ e[:-L]) / n
    return m, m / np.sqrt(s / n), n


def main():
    out = {}
    p = build()
    U = p[p.in_uni & p.pv_dd.notna()].copy()
    # (a) mức theo thời gian: trung vị cắt ngang giá/proxy, mỗi tháng
    lv = U.groupby("time").agg(med_dd=("pv_dd", "median"), med_fade=("pv_fade", "median"),
                               med_rc=("pv_rc", "median"), med_pb=("PB", "median"),
                               r=("r", "first"), n=("ticker", "size"))
    lv.to_csv(os.path.join(HERE, "g3_level_monthly.csv"))
    last = lv.index.max()
    w10 = lv[(lv.index > last - pd.DateOffset(years=10)) & (lv.index < last)]
    w14 = lv[(lv.index >= "2014-01-01") & (lv.index < last)]
    for c in ["med_dd", "med_fade", "med_rc", "med_pb"]:
        out[f"level_{c}"] = {
            "today": round(float(lv.loc[last, c]), 3),
            "hist_median_10y": round(float(w10[c].median()), 3),
            "hist_median_2014plus": round(float(w14[c].median()), 3),
            "pctile_today_10y": round(float((w10[c] < lv.loc[last, c]).mean() * 100), 1),
            "hist_p10_p90_10y": [round(float(w10[c].quantile(.1)), 3), round(float(w10[c].quantile(.9)), 3)],
        }
    out["level_asof"] = str(last.date()); out["n_today"] = int(lv.loc[last, "n"]); out["r_today"] = float(lv.loc[last, "r"])
    out["n_months_10y"] = int(len(w10))
    # tỷ lệ mã "đạt luật 4" (giá ≤0,85×tâm) theo proxy, hôm nay vs lịch sử
    U["le085"] = U.pv_dd <= 0.85
    sh = U.groupby("time").le085.mean()
    out["share_le085"] = {"today": round(float(sh.loc[last]), 3), "hist_median_10y": round(float(sh[w10.index].median()), 3)}
    # (c) dự báo: rank-IC tháng của −giá/proxy với fwd12 / fwd6; Q1−Q5
    res = {}
    for h in (6, 12):
        rows = []
        for t, df in U[U.time >= "2014-01-01"].groupby("time"):
            d = df.dropna(subset=[f"fwd{h}"])
            if len(d) < 50: continue
            ic = stats.spearmanr(-d.pv_dd, d[f"fwd{h}"]).correlation
            icpb = stats.spearmanr(-d.PB, d[f"fwd{h}"]).correlation
            q = pd.qcut(d.pv_dd.rank(method="first"), 5, labels=False)
            sp = d[f"fwd{h}"][q == 0].mean() - d[f"fwd{h}"][q == 4].mean()
            rows.append((t, ic, icpb, sp, len(d), df[f"fwd{h}"].isna().mean()))
        r = pd.DataFrame(rows, columns=["time", "ic", "ic_pb", "q1_q5", "n", "miss_fwd"]).set_index("time")
        r.to_csv(os.path.join(HERE, f"g3_ic_fwd{h}.csv"))
        lag = h - 1
        d = {}
        for name, sub in [("all", r), ("IS_2014_2019", r[r.index < "2020-01-01"]), ("OOS_2020plus", r[r.index >= "2020-01-01"])]:
            m, t_, n = nw_t(sub.ic, lag); mp, tp, _ = nw_t(sub.q1_q5, lag); mb, tb, _ = nw_t(sub.ic_pb, lag)
            nonov = sub.iloc[::h]  # mẫu không chồng lấn
            t_no = stats.ttest_1samp(nonov.q1_q5.dropna(), 0)
            d[name] = {"n_months": n, "n_indep_nonoverlap": int(len(nonov)), "ic_mean": round(m, 4), "ic_nw_t": round(t_, 2),
                       "q1_q5_mean": round(mp, 4), "q1_q5_nw_t": round(tp, 2),
                       "q1_q5_nonoverlap_t": round(float(t_no.statistic), 2), "q1_q5_nonoverlap_p": round(float(t_no.pvalue), 3),
                       "ic_pb_mean": round(mb, 4), "ic_pb_nw_t": round(tb, 2), "miss_fwd_mean": round(float(sub.miss_fwd.mean()), 3)}
        res[f"fwd{h}"] = d
    out["predictive"] = res
    # (c2) mức thị trường: trung vị giá/proxy tháng vs lợi suất trung vị 12T tới (N độc lập ≈ số năm)
    mk = U.groupby("time").agg(lvl=("pv_dd", "median"), f12=("fwd12", "median")).dropna()
    mk = mk[mk.index >= "2014-01-01"]
    mk_no = mk.iloc[::12]
    out["market_level_vs_fwd12"] = {"spearman_all_months": round(float(stats.spearmanr(mk.lvl, mk.f12).correlation), 3),
                                    "n_months": int(len(mk)),
                                    "spearman_nonoverlap": round(float(stats.spearmanr(mk_no.lvl, mk_no.f12).correlation), 3),
                                    "n_nonoverlap": int(len(mk_no)),
                                    "p_nonoverlap": round(float(stats.spearmanr(mk_no.lvl, mk_no.f12).pvalue), 3)}
    # G1 định lượng: mẫu DD vs mẫu ngẫu nhiên PIT — CÙNG thước proxy, tại ASOF
    zones = json.load(open("/home/trido/thanhdt/WorkingClaude/mike/kb/dd_price_zones.json"))["entries"]
    best = {}
    for e in zones:
        k = (e["dd_date"], e.get("rev", 1))
        if e["ticker"] not in best or k > best[e["ticker"]][0]: best[e["ticker"]] = (k, e)
    prov = pd.read_csv(os.path.join(HERE, "g1_provenance.csv"))[["ticker", "group"]]
    T = p[p.time == ASOF].set_index("ticker")
    dd = []
    for tk, (_, e) in best.items():
        if tk not in T.index: dd.append({"ticker": tk, "missing": True}); continue
        row = T.loc[tk]
        proxy_val = row.Price / row.pv_dd if pd.notna(row.pv_dd) else np.nan
        eps = row.Price / row.PE if pd.notna(row.PE) and row.PE != 0 else np.nan
        dd.append({"ticker": tk, "skeptic_final": e["skeptic_final"], "center": e["center"], "price_ref": e["price_ref"],
                   "pc_ref": e["price_ref"] / e["center"], "price_asof": row.Price, "pc_asof": row.Price / e["center"],
                   "pv_proxy": row.pv_dd, "pv_proxy_fade": row.pv_fade, "proxy_value": proxy_val,
                   "dd_over_proxy": e["center"] / proxy_val if proxy_val and proxy_val > 0 else np.nan,
                   "roe_ttm": row.roe_ttm, "PB": row.PB, "PE": row.PE, "in_uni": bool(row.in_uni),
                   "implied_pe_dd": e["center"] / eps if eps and eps > 0 else np.nan,
                   "ICB_Code": row.ICB_Code})
    D = pd.DataFrame(dd).merge(prov, on="ticker", how="left")
    D.to_csv(os.path.join(HERE, "g1_dd_vs_proxy.csv"), index=False)
    rng = np.random.default_rng(20261124)
    pool = U[(U.time == ASOF)].ticker.values
    samp = rng.choice(pool, size=80, replace=False)
    R = U[(U.time == ASOF) & U.ticker.isin(samp)]
    R[["ticker", "pv_dd", "pv_fade", "PB", "roe_ttm"]].to_csv(os.path.join(HERE, "g1_random80.csv"), index=False)
    Dk = D.dropna(subset=["pv_proxy"])
    out["g1"] = {
        "asof": str(ASOF.date()), "n_dd_with_proxy": int(len(Dk)), "n_random": int(len(R)), "universe_size_asof": int(len(pool)),
        "median_pv_proxy_dd36": round(float(Dk.pv_proxy.median()), 3),
        "median_pv_proxy_random80": round(float(R.pv_dd.median()), 3),
        "median_pv_proxy_universe": round(float(U[U.time == ASOF].pv_dd.median()), 3),
        "mannwhitney_p_dd_vs_random": round(float(stats.mannwhitneyu(Dk.pv_proxy, R.pv_dd).pvalue), 3),
        "median_dd_over_proxy": round(float(Dk.dd_over_proxy.median()), 3),
        "median_pc_ref_dd": round(float(D.pc_ref.median()), 3),
        "median_pc_asof_dd": round(float(Dk.pc_asof.median()), 3),
        "by_group": {g: {"n": int(len(x)), "med_pc_ref": round(float(x.pc_ref.median()), 3),
                         "med_pv_proxy": round(float(x.pv_proxy.median()), 3),
                         "med_dd_over_proxy": round(float(x.dd_over_proxy.median()), 3)}
                     for g, x in Dk.groupby("group")},
        "by_skeptic": {g: {"n": int(len(x)), "med_pc_ref": round(float(x.pc_ref.median()), 3),
                           "med_pv_proxy": round(float(x.pv_proxy.median()), 3),
                           "med_dd_over_proxy": round(float(x.dd_over_proxy.median()), 3)}
                       for g, x in Dk.groupby("skeptic_final")},
    }
    # G5: P/E ngụ ý của tâm DD vs P/E ngành (ICB 4 số; trung vị cắt ngang universe) hôm nay / 10Y / tháng cùng mặt bằng lãi (±1pp)
    U["icb"] = U.ICB_Code.astype(int)
    pos = U[U.PE > 0]
    secm = pos.groupby(["icb", "time"]).PE.median().rename("pe_med").reset_index()
    rate = lv["r"].rename("r").reset_index()
    secm = secm.merge(rate, on="time")
    g5 = []
    for _, x in D.dropna(subset=["implied_pe_dd"]).iterrows():
        s = secm[secm.icb == int(x.ICB_Code)]
        if s.empty: continue
        s10 = s[s.time > last - pd.DateOffset(years=10)]
        same = s10[(s10.r - out["r_today"]).abs() <= 0.01]
        cur = s[s.time == last].pe_med
        g5.append({"ticker": x.ticker, "icb": int(x.ICB_Code), "implied_pe_dd": round(x.implied_pe_dd, 2),
                   "pe_mkt_asof": round(x.PE, 2), "sector_pe_today": round(float(cur.iloc[0]), 2) if len(cur) else np.nan,
                   "sector_pe_10y_median": round(float(s10.pe_med.median()), 2),
                   "sector_pe_same_rate_median": round(float(same.pe_med.median()), 2) if len(same) else np.nan,
                   "n_months_same_rate": int(len(same))})
    G5 = pd.DataFrame(g5); G5.to_csv(os.path.join(HERE, "g5_implied_pe.csv"), index=False)
    G5["ratio_10y"] = G5.implied_pe_dd / G5.sector_pe_10y_median
    G5["ratio_same_rate"] = G5.implied_pe_dd / G5.sector_pe_same_rate_median
    out["g5"] = {"n": int(len(G5)), "median_implied_pe_dd": round(float(G5.implied_pe_dd.median()), 2),
                 "median_sector_pe_10y": round(float(G5.sector_pe_10y_median.median()), 2),
                 "median_ratio_implied_over_sector10y": round(float(G5.ratio_10y.median()), 3),
                 "median_ratio_implied_over_sector_same_rate": round(float(G5.ratio_same_rate.median()), 3),
                 "share_implied_below_sector10y": round(float((G5.ratio_10y < 1).mean()), 3)}
    json.dump(out, open(os.path.join(HERE, "g3_results.json"), "w"), ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
