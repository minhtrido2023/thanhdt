#!/usr/bin/env python3
"""D2 — chạy lại D1 cho NHẤT QUÁN theo QUANT_SKEPTIC_D1 (job Taylor_20261123_174703).

KHÔNG sửa D1. Tái dùng hàm định giá của D1 (import D1/calc/proxy.py: vbv_dd, vbv_fade — không chạy main) và
panel ĐÃ KHOÁ của D1 (md5 kiểm ở đầu). Khác D1:
  (3) MỘT cơ sở lãi huy động = Big-4 12M thuần (R2 out/deposit_big4_snapshot.csv), neo r = 13,5% tại Big-4 hôm nay
      6,8% (cùng mức r hôm nay như D1; chỉ lịch sử đổi). Bản 'effective' của D1 chạy song song để parity.
      Backfill CCTG hằng chênh ≡ Big-4 thuần (R2 chứng minh: phân vị/hiệu r không đổi khi cộng hằng cho cả chuỗi).
  (1) ROE chuẩn hoá: hold (ROE_ttm, như D1) · depeak (ROE_ttm ÷ [tỷ lệ EPS_ttm/TB5Y rổ ÷ trung vị 10Y của nó],
      tỷ lệ từ R1 basket_monthly, nhân quả) · div158 (ROE_ttm ÷ tỷ lệ EPS_ttm/TB5Y rổ, =1,584 hôm nay — đúng chữ
      dispatch, CẬN DƯỚI vì chứa kéo tụt do tăng trưởng) · avg5 (cột ROE5Y = TB ROE 5 năm của chính mã).
      Mỗi cơ sở × {hold-5Y (biến thể DD của D1), fade 10Y} ⇒ dải DD/proxy [fade, hold].
  (4) G1: mẫu ngẫu nhiên LOẠI mã DD; MWU trên P/B; p REFUTED_OPEN vs CONFIRMED; phản thực tâm rev1.
  (2) G5: P/E ngụ ý ÷ P/E thị trường của CHÍNH mã (= tâm/giá) + P/E ngụ ý trên EPS chuẩn hoá.
  (6) Hiệu chuẩn nhãn 'so với lịch sử' bằng thước tương đương DD: giá/(k×proxy), k = trung vị tâm DD/proxy.
Chạy: python proxy_d2.py → out/*.csv + out/d2_results.json  (threads=1, tất định)
"""
import os
for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[k] = "1"
import hashlib
import json
import sys

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, "..", ".."))
D1C = os.path.join(BASE, "D1", "calc")
R1C = os.path.join(BASE, "R1", "calc")
R2O = os.path.join(BASE, "rerun", "R2", "out")
INP = os.path.join(BASE, "rerun", "inputs")
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)
sys.dont_write_bytecode = True   # không ghi gì vào thư mục D1
sys.path.insert(0, D1C)
import proxy as P  # noqa: E402  (D1, chỉ dùng hàm)

LOCK = {os.path.join(D1C, "panel_all.parquet"): "b64b0015dc6e9ff9f37ce981c81f9a57",
        os.path.join(D1C, "panel.parquet"): "7fad0f00d3f2f0ff0755e25a00708eff",
        os.path.join(D1C, "deposit_effective_snapshot.csv"): "e99f2038edaed5191926f8da355b4385",
        os.path.join(D1C, "proxy.py"): "28a22d9b17db04bcf5827d8e15b88c9e",
        os.path.join(D1C, "g1_provenance.csv"): "e6c05cfce0dc0522e42fc5a46d10e9e4",
        os.path.join(R1C, "out", "basket_monthly.csv"): "87654f9ef7bb49792c1de06b33822da5",
        os.path.join(INP, "dd_price_zones_da6018d95.json"): "74539e4cbe9af2dd49a083ae77af470f",
        os.path.join(INP, "dd_price_zones_e547cd7fc.json"): "9e4cab03a59edbf8af16eb5d83b9679b"}
# D1 đọc bản e547cd7fc (17:14Z: PAT/TCH/VGS → REFUTED_OPEN); R1 đọc da6018d95 (17:02Z: 3 mã đó FIXED_UNVERIFIED).
# Tâm 36 mã GIỐNG HỆT giữa 2 bản (kiểm bên dưới) — chỉ nhãn skeptic khác. D2 dùng e547cd7fc làm chính (= D1).
for f, h in LOCK.items():
    got = hashlib.md5(open(f, "rb").read()).hexdigest()
    if got != h:
        sys.exit(f"INPUT MD5 MISMATCH {f}: {got} != {h}")

ASOF = pd.Timestamp("2026-11-20")
R0 = 0.135
SEED = 20261124


def pct_rank(hist, x):
    hist = np.asarray(hist, float)
    return float(100 * (hist < x).mean())


def build():
    allp = pd.read_parquet(os.path.join(D1C, "panel_all.parquet")).sort_values(["time", "ticker"])
    uni = pd.read_parquet(os.path.join(D1C, "panel.parquet"))[["time", "ticker"]]
    eff = pd.read_csv(os.path.join(D1C, "deposit_effective_snapshot.csv"), parse_dates=["time"]).sort_values("time")
    big4 = pd.read_csv(os.path.join(R2O, "deposit_big4_snapshot.csv"), parse_dates=["time"]).sort_values("time")
    allp = pd.merge_asof(allp, eff.rename(columns={"deposit_rate": "dep_eff"}), on="time", direction="backward")
    allp = pd.merge_asof(allp, big4.rename(columns={"deposit_rate": "dep_big4"}), on="time", direction="backward")
    big4_now = float(big4["deposit_rate"].iloc[-1])
    allp["r_eff"] = R0 + (allp["dep_eff"] - 7.4) / 100.0          # = D1 (parity)
    allp["r_b4"] = R0 + (allp["dep_big4"] - big4_now) / 100.0     # MỘT cơ sở
    pe, pb = allp["PE"], allp["PB"]
    ok = pb.gt(0) & pe.notna() & pe.ne(0)
    allp["roe_ttm"] = np.where(ok, pb / pe, np.nan)
    # tỷ lệ EPS_ttm/TB5Y của rổ radar (R1, theo tháng) + trung vị 10Y NHÂN QUẢ (chỉ quá khứ, ≥24 tháng)
    b1 = pd.read_csv(os.path.join(R1C, "out", "basket_monthly.csv"), parse_dates=["time"])[["time", "eps_ttm_over_avg5"]]
    b1 = b1.sort_values("time").reset_index(drop=True)
    b1["ratio_med10"] = [b1["eps_ttm_over_avg5"].iloc[max(0, i - 119):i].median() if i >= 24 else np.nan
                         for i in range(len(b1))]
    b1["ym"] = b1["time"].dt.to_period("M")
    allp["ym"] = allp["time"].dt.to_period("M")
    allp = allp.merge(b1[["ym", "eps_ttm_over_avg5", "ratio_med10"]], on="ym", how="left")
    roe = {"hold": allp["roe_ttm"],
           "depeak": allp["roe_ttm"] / (allp["eps_ttm_over_avg5"] / allp["ratio_med10"]),
           "div158": allp["roe_ttm"] / allp["eps_ttm_over_avg5"],
           "avg5": allp["ROE5Y"]}
    for bname, rr in roe.items():
        x = pd.Series(rr, index=allp.index).clip(-0.20, 0.45)
        allp[f"roe_{bname}"] = x
        g = P.B * x.clip(lower=0)
        for rlab in ("b4", "eff"):
            if rlab == "eff" and bname != "hold":
                continue
            rv = allp[f"r_{rlab}"].values
            vh = P.vbv_dd(x.values, rv, g.values)
            vf = P.vbv_fade(x.values, rv)
            allp[f"pv_{bname}_{rlab}_hold"] = np.where(vh > 0.05, pb / vh, np.nan)
            allp[f"pv_{bname}_{rlab}_fade"] = np.where(vf > 0.05, pb / vf, np.nan)
    allp = allp.merge(uni.assign(in_uni=True), on=["time", "ticker"], how="left")
    allp["in_uni"] = allp["in_uni"].fillna(False).astype(bool)
    return allp, big4_now


def main():
    out = {}
    p, big4_now = build()
    out["big4_now"] = big4_now
    U = p[p.in_uni].copy()
    last = U.time.max()
    out["asof"] = str(last.date())
    PV = [c for c in p.columns if c.startswith("pv_")]

    # ---------------------------------------------------------------- (3)+(1) G3 mức: phân vị hôm nay
    lv = U.groupby("time")[PV + ["PB"]].median()
    lv["r_b4"] = U.groupby("time").r_b4.first()
    lv["r_eff"] = U.groupby("time").r_eff.first()
    lv.to_csv(os.path.join(OUT, "g3_level_monthly_d2.csv"), float_format="%.5g")
    w10 = lv[(lv.index > last - pd.DateOffset(years=10)) & (lv.index < last)]
    lev = {}
    for c in PV + ["PB"]:
        lev[c] = {"today": float(lv.loc[last, c]), "med10": float(w10[c].median()),
                  "p10": float(w10[c].quantile(.1)), "p90": float(w10[c].quantile(.9)),
                  "pct_today": pct_rank(w10[c], lv.loc[last, c]),
                  "months_price_below_proxy": int((w10[c] < 1).sum())}
    out["g3_level"] = lev
    out["g3_n_months_10y"] = int(len(w10))
    out["r_today_b4"], out["r_today_eff"] = float(lv.loc[last, "r_b4"]), float(lv.loc[last, "r_eff"])

    # ---------------------------------------------------------------- DD sample (bản đóng băng)
    zones = json.load(open(os.path.join(INP, "dd_price_zones_e547cd7fc.json")))["entries"]
    zalt = json.load(open(os.path.join(INP, "dd_price_zones_da6018d95.json")))["entries"]
    best_alt = {}
    for e in zalt:
        k = (e["dd_date"], e.get("rev", 1))
        if e["ticker"] not in best_alt or k > best_alt[e["ticker"]][0]:
            best_alt[e["ticker"]] = (k, e)
    best, rev1 = {}, {}
    for e in zones:
        k = (e["dd_date"], e.get("rev", 1))
        if e["ticker"] not in best or k > best[e["ticker"]][0]:
            best[e["ticker"]] = (k, e)
    for tk, (k, e) in best.items():   # rev1 = rev nhỏ nhất CÙNG dd_date của bản cuối có tâm
        chain = sorted([x for x in zones if x["ticker"] == tk and x["dd_date"] == k[0] and x.get("center")],
                       key=lambda x: x.get("rev", 1))
        rev1[tk] = chain[0] if chain else None
    prov = pd.read_csv(os.path.join(D1C, "g1_provenance.csv"))[["ticker", "group"]]
    T = p[p.time == ASOF].set_index("ticker")
    rows = []
    for tk, (_, e) in best.items():
        if tk not in T.index or not e.get("center"):
            continue
        row = T.loc[tk]
        ea = best_alt[tk][1]
        assert ea["center"] == e["center"], tk
        rec = {"ticker": tk, "skeptic_final": e["skeptic_final"], "skeptic_final_da60": ea["skeptic_final"], "center": e["center"], "price_ref": e["price_ref"],
               "price_asof": row.Price, "pc_ref": e["price_ref"] / e["center"], "pc_asof": row.Price / e["center"],
               "center_rev1": rev1[tk]["center"] if rev1[tk] else np.nan,
               "rev1_n": rev1[tk].get("rev", 1) if rev1[tk] else np.nan,
               "PB": row.PB, "PE": row.PE, "roe_ttm": row.roe_ttm, "ROE5Y": row.ROE5Y, "in_uni": bool(row.in_uni),
               "ICB_Code": row.ICB_Code}
        for c in PV:
            if not c.endswith(("_b4_hold", "_b4_fade")) and c != "pv_hold_eff_hold":
                continue
            pv = row[c]
            proxy_val = row.Price / pv if pd.notna(pv) and pv > 0 else np.nan
            rec[c] = pv
            rec[c.replace("pv_", "ddop_")] = e["center"] / proxy_val if proxy_val and proxy_val > 0 else np.nan
            rec[c.replace("pv_", "ddop1_")] = rec["center_rev1"] / proxy_val if proxy_val and proxy_val > 0 else np.nan
        eps = row.Price / row.PE if pd.notna(row.PE) and row.PE != 0 else np.nan
        rec["eps_ttm"] = eps
        rec["implied_pe"] = e["center"] / eps if eps and eps > 0 else np.nan
        rows.append(rec)
    D = pd.DataFrame(rows).merge(prov, on="ticker", how="left")
    D.to_csv(os.path.join(OUT, "g1_dd_vs_proxy_d2.csv"), index=False, float_format="%.5g")
    DD = set(D.ticker)

    # ---------------------------------------------------------------- (1)+(4) G1
    pool_all = U[U.time == ASOF]
    pool = pool_all[~pool_all.ticker.isin(DD)]
    rng = np.random.default_rng(SEED)
    samp = rng.choice(np.sort(pool.ticker.values), size=80, replace=False)
    R = pool[pool.ticker.isin(samp)]
    R[["ticker", "PB", "roe_ttm"] + [c for c in PV if "_b4_" in c]].to_csv(os.path.join(OUT, "g1_random80_exdd.csv"),
                                                                          index=False, float_format="%.5g")
    g1 = {"universe_asof": int(len(pool_all)), "n_dd_in_universe": int(pool_all.ticker.isin(DD).sum()),
          "n_pool_exdd": int(len(pool)), "n_random": int(len(R)), "n_dd_with_center": int(len(D))}
    Dk = D[D.in_uni]
    g1["n_dd_in_uni_used"] = int(len(Dk))
    g1["pb"] = {"dd_med": float(D.PB.median()), "rand_med": float(R.PB.median()),
                "mwu_p_dd_vs_rand": float(stats.mannwhitneyu(D.PB.dropna(), R.PB.dropna()).pvalue),
                "pool_exdd_med": float(pool.PB.median())}
    g1["roe_ttm"] = {"dd_med": float(D.roe_ttm.median()), "rand_med": float(R.roe_ttm.median())}
    g1["pe"] = {"dd_med_pos": float(D.PE[D.PE > 0].median()), "rand_med_pos": float(R.PE[R.PE > 0].median())
                if "PE" in R else None}
    bands = {}
    for bname in ("hold", "depeak", "div158", "avg5"):
        b = {}
        for v in ("hold", "fade"):
            c = f"pv_{bname}_b4_{v}"
            dpv, rpv = D[c].dropna(), R[c].dropna()
            b[v] = {"dd_med_pv": float(dpv.median()), "rand_med_pv": float(rpv.median()),
                    "mwu_p": float(stats.mannwhitneyu(dpv, rpv).pvalue), "n_dd": int(len(dpv)), "n_rand": int(len(rpv)),
                    "dd_over_proxy_med": float(D[c.replace("pv_", "ddop_")].median()),
                    "dd_over_proxy_rev1_med": float(D[c.replace("pv_", "ddop1_")].median())}
        b["band_dd_over_proxy_fade_hold"] = sorted([b["fade"]["dd_over_proxy_med"], b["hold"]["dd_over_proxy_med"]])
        bands[bname] = b
    g1["by_roe_basis"] = bands
    allband = [x for bb in bands.values() for x in bb["band_dd_over_proxy_fade_hold"]]
    g1["dd_over_proxy_envelope_all_bases"] = [float(min(allband)), float(max(allband))]
    # parity với D1 (r effective, hold, ROE_ttm)
    g1["parity_d1_dd_over_proxy_med_eff_hold"] = float(D["ddop_hold_eff_hold"].median())
    # REFUTED_OPEN vs CONFIRMED — trên cơ sở D1 (eff) để tái lập p=0,058, và trên Big-4 cho mọi cơ sở ROE
    grp = {}
    for c in ["ddop_hold_eff_hold"] + [f"ddop_{b}_b4_{v}" for b in ("hold", "depeak", "div158", "avg5") for v in ("hold", "fade")]:
        a = D[D.skeptic_final == "REFUTED_OPEN"]
        cf = D[D.skeptic_final == "CONFIRMED"]
        c1 = c.replace("ddop_", "ddop1_")
        grp[c] = {"n_ro": int(a[c].notna().sum()), "n_cf": int(cf[c].notna().sum()),
                  "ro_med": float(a[c].median()), "cf_med": float(cf[c].median()),
                  "mwu_p": float(stats.mannwhitneyu(a[c].dropna(), cf[c].dropna()).pvalue),
                  "ro_med_rev1": float(a[c1].median()), "cf_med_rev1": float(cf[c1].median()),
                  "mwu_p_rev1": float(stats.mannwhitneyu(a[c1].dropna(), cf[c1].dropna()).pvalue)}
        # phần khoảng cách log (RO vs CF) có sẵn ở rev1 vs do dựng lại
        gap_now = np.log(grp[c]["cf_med"] / grp[c]["ro_med"])
        gap_r1 = np.log(grp[c]["cf_med_rev1"] / grp[c]["ro_med_rev1"])
        grp[c]["share_gap_present_at_rev1"] = float(gap_r1 / gap_now) if gap_now else np.nan
    # cùng phép thử trên nhãn của bản R1 (da6018d95): PAT/TCH/VGS không thuộc REFUTED_OPEN
    for c in ("ddop_hold_eff_hold", "ddop_avg5_b4_fade", "ddop_avg5_b4_hold"):
        a = D[D.skeptic_final_da60 == "REFUTED_OPEN"][c].dropna()
        cf = D[D.skeptic_final_da60 == "CONFIRMED"][c].dropna()
        grp[f"alt_labels_da60_{c}"] = {"n_ro": int(len(a)), "ro_med": float(a.median()), "cf_med": float(cf.median()),
                                       "mwu_p": float(stats.mannwhitneyu(a, cf).pvalue)}
    D["chg_rev1_to_final"] = D.center / D.center_rev1 - 1
    for s_ in ("REFUTED_OPEN", "CONFIRMED"):
        x = D[D.skeptic_final == s_]
        grp[f"center_change_rev1_to_final_median_{s_}"] = float(x.chg_rev1_to_final.median())
        grp[f"pc_ref_median_{s_}"] = float(x.pc_ref.median())
        grp[f"pc_ref_rev1_median_{s_}"] = float((x.price_ref / x.center_rev1).median())
    g1["refuted_vs_confirmed"] = grp
    out["g1"] = g1

    # ---------------------------------------------------------------- (2) G5
    pos = U[U.PE > 0].copy()
    pos["icb"] = pos.ICB_Code.astype(int)
    secm = pos.groupby(["icb", "time"]).PE.median().rename("pe_med").reset_index()
    g5r = []
    for _, x in D.dropna(subset=["implied_pe"]).iterrows():
        s = secm[(secm.icb == int(x.ICB_Code)) & (secm.time > last - pd.DateOffset(years=10))]
        if s.empty:
            continue
        ratio_now = float(p.loc[p.time == ASOF, "eps_ttm_over_avg5"].iloc[0])
        ratio_med = float(p.loc[p.time == ASOF, "ratio_med10"].iloc[0])
        g5r.append({"ticker": x.ticker, "skeptic_final": x.skeptic_final, "implied_pe": x.implied_pe,
                    "pe_mkt_own": x.PE, "implied_over_own": x.implied_pe / x.PE if x.PE > 0 else np.nan,
                    "sector_pe_10y_med": float(s.pe_med.median()),
                    "implied_pe_on_eps_div158": x.implied_pe * ratio_now,
                    "implied_pe_on_eps_depeak": x.implied_pe * ratio_now / ratio_med,
                    "implied_pe_on_eps_avg5": x.implied_pe * (x.roe_ttm / x.ROE5Y) if x.ROE5Y and x.ROE5Y > 0 else np.nan,
                    "own_pe_on_eps_avg5": x.PE * (x.roe_ttm / x.ROE5Y) if x.ROE5Y and x.ROE5Y > 0 and x.PE > 0 else np.nan})
    G5 = pd.DataFrame(g5r)
    G5.to_csv(os.path.join(OUT, "g5_implied_pe_d2.csv"), index=False, float_format="%.4g")
    g5 = {"n": int(len(G5)), "median_implied_pe": float(G5.implied_pe.median()),
          "median_own_pe": float(G5.pe_mkt_own[G5.pe_mkt_own > 0].median()),
          "median_implied_over_own": float(G5.implied_over_own.median()),
          "share_implied_below_own": float((G5.implied_over_own < 1).mean()),
          "median_sector_pe_10y": float(G5.sector_pe_10y_med.median()),
          "median_own_over_sector10y": float((G5.pe_mkt_own / G5.sector_pe_10y_med)[G5.pe_mkt_own > 0].median()),
          "median_implied_over_sector10y": float((G5.implied_pe / G5.sector_pe_10y_med).median())}
    for k_ in ("div158", "depeak", "avg5"):
        col = f"implied_pe_on_eps_{k_}"
        g5[f"median_{col}"] = float(G5[col].median())
        g5[f"median_{col}_over_sector10y"] = float((G5[col] / G5.sector_pe_10y_med).median())
    g5["median_own_pe_on_eps_avg5"] = float(G5.own_pe_on_eps_avg5.median())
    out["g5"] = g5

    # ---------------------------------------------------------------- (6) hiệu chuẩn nhãn 'so với lịch sử' bằng thước DD
    # Thước DD-tương-đương của 1 mã = k × proxy, k = trung vị (tâm DD / proxy) đo trên 35 mã HÔM NAY (giả định k bất biến
    # theo thời gian — KHÔNG kiểm được). Phân phối lịch sử: giá/(k×proxy) = pv/k của universe ⇒ trung vị tháng / k.
    cal = {}
    pc_book_ref = float(D.pc_ref.median())
    pc_book_asof = float(D.pc_asof.median())
    for bname in ("hold", "depeak", "div158", "avg5"):
        for v in ("hold", "fade"):
            c = f"pv_{bname}_b4_{v}"
            kk = bands[bname][v]["dd_over_proxy_med"]
            h = w10[c] / kk
            cal[f"{bname}_{v}"] = {"k": kk, "hist_med10_price_over_ddeq": float(h.median()),
                                   "hist_p10": float(h.quantile(.1)), "hist_p25": float(h.quantile(.25)),
                                   "hist_p75": float(h.quantile(.75)), "hist_p90": float(h.quantile(.9)),
                                   "market_today_price_over_ddeq": float(lv.loc[last, c] / kk),
                                   "market_today_pct": pct_rank(h, lv.loc[last, c] / kk),
                                   "dd_book_pc_ref_1085_pct": pct_rank(h, pc_book_ref),
                                   "dd_book_pc_asof_pct": pct_rank(h, pc_book_asof)}
    out["calib"] = {"dd_book_pc_ref_median": pc_book_ref, "dd_book_pc_asof_median": pc_book_asof, "by_basis": cal}
    hm = [x["hist_med10_price_over_ddeq"] for x in cal.values()]
    out["calib"]["envelope_hist_med10"] = [float(min(hm)), float(max(hm))]
    pcts = [x["dd_book_pc_ref_1085_pct"] for x in cal.values()]
    out["calib"]["envelope_pct_of_1085"] = [float(min(pcts)), float(max(pcts))]

    json.dump(out, open(os.path.join(OUT, "d2_results.json"), "w"), ensure_ascii=False, indent=1, sort_keys=True,
              default=lambda o: o.item() if hasattr(o, "item") else str(o))
    print("OK", out["asof"])


if __name__ == "__main__":
    main()
