"""ERP nội địa cho DCF fleet (job Taylor_20261030_034654). READ-ONLY research — theo PREREG.md (commit f4a6cce0c).
Chỉ đọc data/*.csv (đã chụp bởi fetch_data.py + cache_local.py) ⇒ tất định. DGC: import model_ke.py của nghiên cứu 29/10
(không sửa r7). Tái lập: $DNA_PYEXE erp_domestic.py  ⇒ out_*.csv + run_stdout.txt.
Nhãn: [BQ] đo từ BigQuery (cache data/) · [SRC] có nguồn · [UL] ước lượng."""
import os, sys, importlib.util
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); DD = os.path.join(HERE, "data")
csv = lambda n: os.path.join(HERE, n)
ASOF = "2026-10-29"
RF_C = 6.75                       # [thừa kế 29/10] π mục tiêu 4,25 + lãi thực 2,5
PI_C, PI_BAND = 4.25, (4.0, 4.5)  # [UL]
G_C, G_BAND = 5.5, (4.25, 6.75)   # PREREG §1 M-b
DAMO_MATURE, DAMO_TOTAL = 4.23, 8.13   # [SRC] Damodaran 01/2026
BANK, RE = {8355}, {8633, 8637}
TPCP_PRE = {2008: (12.0, "UL"), 2009: (9.7, "SRC VietnamPlus 26/09/2019"), 2010: (10.5, "UL")}
L = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s); L.append(s)


# =================================================================== 1. E/P robust
def load_snap():
    s = pd.read_csv(os.path.join(DD, "snap_universe_pit_qe.csv"))
    s["mcap"] = s.Price * s.OShares
    s["np"] = s.mcap / s.PE
    s["icb"] = s.ICB_Code.fillna(-1).astype(int)
    return s


def ep_estimators(d, vni_pe):
    """d: một ngày, đã loại PE/OShares NULL. Trả dict E1..E10 (E/P, %), ROE trung vị từng rổ."""
    d = d[np.isfinite(d.np) & (d.PE != 0)]
    agg = lambda x: 100 * x.np.sum() / x.mcap.sum()
    ep = 100 / d.PE
    lo, hi = ep.quantile(0.01), ep.quantile(0.99)
    top = d.sort_values("mcap", ascending=False)
    exbr = d[~d.icb.isin(BANK | RE)]
    out = {
        "E1_vnindex_pe": (100 / vni_pe if vni_pe and np.isfinite(vni_pe) else np.nan, d),
        "E2_aggregate": (agg(d), d),
        "E3_eqw_mean_w1": (float(ep.clip(lo, hi).mean()), d),
        "E4_median": (float(ep.median()), d),
        "E5_agg_ex_top5": (agg(top.iloc[5:]), top.iloc[5:]),
        "E6_agg_ex_top10": (agg(top.iloc[10:]), top.iloc[10:]),
        "E7_agg_ex_bank": (agg(d[~d.icb.isin(BANK)]), d[~d.icb.isin(BANK)]),
        "E8_agg_ex_re": (agg(d[~d.icb.isin(RE)]), d[~d.icb.isin(RE)]),
        "E9_agg_ex_bank_re": (agg(exbr), exbr),
        "E10_median_ex_bank_re": (float((100 / exbr.PE).median()), exbr),
    }
    return {k: (v, float(sub.ROE5Y.median()), len(sub)) for k, (v, sub) in out.items()}


def ke_ma(ep, pi=PI_C):
    return ep + pi


def ke_mb(ep, roe, g=G_C):
    gg, r = g / 100, min(max(roe, g / 100 + 0.01), 0.40)
    return 100 * (gg + (1 - gg / r) * (1 + gg) * ep / 100)


def part1(s, vni):
    pe_by_date = vni.set_index("time").VNINDEX_PE
    d0 = s[s.time == ASOF]
    n_all = len(d0); d0v = d0.dropna(subset=["PE", "OShares", "Price"])
    P(f"[1] rổ universe_pit {ASOF}: {n_all} mã, {len(d0v)} có PE/OShares [BQ]; lỗ (PE<0): {(d0v.PE < 0).sum()}")
    est = ep_estimators(d0v, pe_by_date.get(ASOF, np.nan))
    rows = []
    for k, (ep, roe_med, n) in est.items():
        r = dict(est=k, n=n, ep=round(ep, 3), pe_equiv=round(100 / ep, 2), roe5y_med=round(roe_med, 4),
                 ke_ma=round(ke_ma(ep), 3), ke_ma_lo=round(ke_ma(ep, PI_BAND[0]), 3), ke_ma_hi=round(ke_ma(ep, PI_BAND[1]), 3),
                 ke_mb=round(ke_mb(ep, roe_med), 3), ke_mb_g425=round(ke_mb(ep, roe_med, G_BAND[0]), 3),
                 ke_mb_g675=round(ke_mb(ep, roe_med, G_BAND[1]), 3))
        r["erp_ma"] = round(r["ke_ma"] - RF_C, 3); r["erp_mb"] = round(r["ke_mb"] - RF_C, 3)
        rows.append(r)
    T = pd.DataFrame(rows); T.to_csv(csv("out_ep_estimators.csv"), index=False)
    P(T[["est", "n", "ep", "pe_equiv", "roe5y_med", "ke_ma", "ke_mb", "ke_mb_g425", "ke_mb_g675", "erp_ma", "erp_mb"]].to_string(index=False))
    top10 = d0v.sort_values("mcap", ascending=False).head(10)
    P(f"  top-10 vốn hoá = {100 * top10.mcap.sum() / d0v.mcap.sum():.1f}% vốn hoá rổ, {100 * top10.np.sum() / d0v.np.sum():.1f}% lợi nhuận rổ;",
      "mã:", ",".join(top10.ticker))
    # lịch sử quý
    H = []
    for t, d in s.groupby("time"):
        d = d.dropna(subset=["PE", "OShares", "Price"])
        e = ep_estimators(d, pe_by_date.get(t, np.nan))
        H.append(dict(time=t, n=len(d), **{k: round(e[k][0], 3) for k in ("E1_vnindex_pe", "E2_aggregate", "E4_median", "E6_agg_ex_top10", "E9_agg_ex_bank_re")}))
    H = pd.DataFrame(H); H.to_csv(csv("out_ep_history_quarterly.csv"), index=False)
    h = H.dropna(subset=["E1_vnindex_pe"])
    for c in ("E2_aggregate", "E4_median", "E6_agg_ex_top10", "E9_agg_ex_bank_re"):
        dif = h[c] - h.E1_vnindex_pe
        P(f"  lịch sử {h.time.min()}→{h.time.max()} (N={len(h)} quý có VNINDEX_PE): {c} − E1 trung vị {dif.median():+.2f}pp, min {dif.min():+.2f}, max {dif.max():+.2f}")
    sub = T.set_index("est").loc[["E2_aggregate", "E4_median", "E6_agg_ex_top10", "E9_agg_ex_bank_re", "E10_median_ex_bank_re"]]
    D1, D2 = float(sub.erp_mb.median()), float(sub.erp_ma.median())
    P(f"  D1 (M-b, trung vị 5 ước lượng robust) = {D1:.3f} ; D2 (M-a) = {D2:.3f}")
    return T, D1, D2, d0v


# =================================================================== 2. ERP lịch sử
def monthly_series(vni):
    tr = pd.read_csv(os.path.join(DD, "vnindex_tr_daily.csv"), usecols=["date", "vnindex", "y_gross", "tr_gross"])
    tr["date"] = pd.to_datetime(tr.date); tr["y_gross"] = tr.y_gross.fillna(0)
    yg = tr.groupby(tr.date.dt.year).y_gross.sum()
    div_pre = float(yg.loc[2014:2016].mean()) * 100          # %/năm, [UL-ngoại suy]
    v = vni.copy(); v["time"] = pd.to_datetime(v.time)
    v = v[v.time < "2013-12-31"].set_index("time").vnindex
    # trước 2014: chỉ số giá × cổ tức tích luỹ đều theo ngày giao dịch
    def build(div_pct):
        px = pd.concat([v, pd.Series([tr.vnindex.iloc[0]], index=[tr.date.iloc[0]])])   # giá tới 2013-12-31
        dd = (1 + div_pct / 100) ** (1 / 250) - 1
        pre = px * (1 + dd) ** np.arange(len(px))
        pre = pre / pre.iloc[-1] * tr.tr_gross.iloc[0]                                    # khớp mức tr_gross 2013-12-31
        s = pd.concat([pre.iloc[:-1], tr.set_index("date").tr_gross])
        return s
    return build, div_pre, yg


def rf_daily_index(dates):
    dep = pd.read_csv(os.path.join(DD, "deposit_big4_12m_daily.csv")); dep["date"] = pd.to_datetime(dep.date)
    dep = dep.set_index("date").big4_12m
    full = dep.reindex(pd.date_range(dep.index.min(), dep.index.max())).ffill()
    acc = (1 + full / 100 / 365).cumprod()
    return acc, full


def tpcp_annual():
    t = pd.read_csv(os.path.join(DD, "tpcp10y_annual.csv")).set_index("year")
    y = {int(k): float(r.yield_pct) for k, r in t.iterrows()}
    for k, (val, _) in TPCP_PRE.items(): y[k] = val
    return y


def tpcp_index():
    y = tpcp_annual(); days = pd.date_range("2008-01-01", ASOF)
    r = np.array([y[d.year] for d in days]) / 100 / 365
    return pd.Series(np.cumprod(1 + r), index=days)


def window_stats(eq, rfi, a, b, pe_s, label, leg):
    e = eq[(eq.index >= a) & (eq.index <= b)]; a0, b0 = e.index[0], e.index[-1]
    yrs = (b0 - a0).days / 365.25
    rf_idx = rfi.reindex(pd.date_range(min(a0, rfi.index.min()), max(b0, rfi.index.max()))).ffill()
    eq_c = (e.iloc[-1] / e.iloc[0]) ** (1 / yrs) - 1
    rf_c = (rf_idx[b0] / rf_idx[a0]) ** (1 / yrs) - 1
    geo = (1 + eq_c) / (1 + rf_c) - 1
    me = e.resample("ME").last(); mr = rf_idx.reindex(me.index, method="ffill")
    ex = (me.pct_change() - mr.pct_change()).dropna()
    arith = ex.mean() * 12
    pa, pb = pe_s.get(a0, np.nan), pe_s.get(b0, np.nan)
    rer = np.log(pb / pa) / yrs if np.isfinite(pa) and np.isfinite(pb) else np.nan
    return dict(window=label, leg=leg, start=str(a0.date()), end=str(b0.date()), years=round(yrs, 2),
                eq_cagr=round(100 * eq_c, 3), rf_avg=round(100 * rf_c, 3), erp_geo=round(100 * geo, 3),
                erp_arith=round(100 * arith, 3), pe_start=None if not np.isfinite(pa) else round(pa, 2),
                pe_end=None if not np.isfinite(pb) else round(pb, 2),
                rerating_pa=None if not np.isfinite(rer) else round(100 * rer, 3),
                erp_geo_ex_rerating=None if not np.isfinite(rer) else round(100 * (geo - rer), 3)), ex


def stationary_bootstrap(x, n=10000, mean_block=12, seed=20261030):
    rng = np.random.default_rng(seed); x = np.asarray(x); T = len(x); p = 1 / mean_block
    out = np.empty(n)
    for i in range(n):
        idx = np.empty(T, dtype=int); idx[0] = rng.integers(T)
        newb = rng.random(T) < p; starts = rng.integers(T, size=T)
        for t in range(1, T):
            idx[t] = starts[t] if newb[t] else (idx[t - 1] + 1) % T
        out[i] = x[idx].mean() * 12
    return np.percentile(out, [5, 50, 95]) * 100


def part2(vni):
    build, div_pre, yg = monthly_series(vni)
    P(f"[2] cổ tức trước 2014 = TB y_gross 2014–2016 = {div_pre:.3f}%/năm [UL-ngoại suy]; y_gross theo năm [BQ]:",
      ", ".join(f"{y}:{100 * v:.2f}" for y, v in yg.items()))
    pe = vni.copy(); pe["time"] = pd.to_datetime(pe.time); pe_s = pe.set_index("time").VNINDEX_PE.dropna()
    pe_first = pe_s.index.min()
    P(f"  VNINDEX_PE có từ {pe_first.date()} [BQ]")
    dep_i, dep_lvl = rf_daily_index(None); tp_i = tpcp_index()
    W = [("2008→", "2008-01-01"), ("2011→", "2011-01-01"), ("2014→", "2013-12-31"), ("2016-07→", "2016-07-01"),
         ("2008-2013", "2008-01-01", "2013-12-31"), ("2014-2019", "2013-12-31", "2019-12-31"), ("2020-2026", "2019-12-31", ASOF)]
    rows, boots = [], []
    for div_lab, dv in (("central", div_pre), ("div-1", div_pre - 1), ("div+1", div_pre + 1)):
        eq = build(dv)
        for w in W:
            lab, a = w[0], w[1]; b = w[2] if len(w) > 2 else ASOF
            for leg, rfi in (("big4_12m", dep_i), ("tpcp10y", tp_i)):
                if leg == "big4_12m" and pd.Timestamp(a) < pd.Timestamp("2011-01-01"): continue
                if div_lab != "central" and pd.Timestamp(a) >= pd.Timestamp("2013-12-31"): continue
                r, ex = window_stats(eq, rfi, pd.Timestamp(a), pd.Timestamp(b), pe_s, lab, leg); r["div_case"] = div_lab
                if div_lab == "central" and len(w) == 2:
                    lo, md, hi = stationary_bootstrap(ex.values)
                    r.update(boot_p5=round(lo, 2), boot_p50=round(md, 2), boot_p95=round(hi, 2), n_months=len(ex))
                rows.append(r)
    T = pd.DataFrame(rows); T.to_csv(csv("out_erp_history.csv"), index=False)
    P(T[T.div_case == "central"][["window", "leg", "years", "eq_cagr", "rf_avg", "erp_geo", "erp_arith", "rerating_pa", "erp_geo_ex_rerating", "boot_p5", "boot_p95"]].to_string(index=False))
    P(T[T.div_case != "central"][["window", "leg", "div_case", "erp_geo"]].to_string(index=False))
    c = T[(T.div_case == "central") & (T.leg == "big4_12m")].set_index("window")
    wpe = "2011→"   # cửa sổ dài nhất có cả chân Big-4 và VNINDEX_PE (PE có từ 2007-12, không phải 2016-07 như PREREG dự kiến)
    D3 = float(c.loc[wpe, "erp_geo_ex_rerating"] + c.loc[wpe, "rf_avg"] - RF_C)
    D3b = float(c.loc["2016-07→", "erp_geo_ex_rerating"] + c.loc["2016-07→", "rf_avg"] - RF_C)
    P(f"  D3-thay thế (2016-07→, cửa sổ PREREG dự kiến) = {D3b:.3f} — độ nhạy, KHÔNG vào luật")
    D4 = float(c.loc["2014→", "erp_geo"] + c.loc["2014→", "rf_avg"] - RF_C)
    P(f"  D3 (2011→, bỏ tái định giá, quy về rf_c) = {c.loc[wpe, 'erp_geo_ex_rerating']:.3f} + ({c.loc[wpe, 'rf_avg']:.3f} − {RF_C}) = {D3:.3f}")
    P(f"  D4 (2014→, quy về rf_c) = {c.loc['2014→', 'erp_geo']:.3f} + ({c.loc['2014→', 'rf_avg']:.3f} − {RF_C}) = {D4:.3f}")
    return T, D3, D4, dep_lvl


# =================================================================== 3. rf proxies
def part3(dep_lvl):
    sbv = pd.read_csv(os.path.join(DD, "fiinprox_sbv_avg_deposit_rate_monthly_2011_2026.csv"))
    last = sbv.period.max(); sl = sbv[sbv.period == last].set_index("series").rate_pct
    y = tpcp_annual()
    rows = [("building-block thấp/giữa/cao", "6.00/6.75/7.50", "π mục tiêu 4,0–4,5 + thực 2–3 [UL] (29/10)"),
            ("TPCP 10Y hiện tại", "4.47", "[SRC] ADB AsianBondsOnline 28/10/2026"),
            ("TPCP 10Y TB 2016-2025", f"{np.mean([y[k] for k in range(2016, 2026)]):.2f}", "9/16 điểm chuỗi chưa kiểm chứng"),
            ("Big-4 12M hôm nay", f"{dep_lvl.iloc[-1]:.2f}", "[CANONICAL-PROXY] deposit_rate_vn"),
            ("Big-4 12M TB 10 năm", f"{dep_lvl[dep_lvl.index > '2016-10-29'].mean():.2f}", "deposit_rate_vn, mốc neo có hindsight"),
            ("Big-4 12M TB 2011→", f"{dep_lvl.mean():.2f}", "gồm giai đoạn 14% 2011"),
            ("CCTG 12M", "7.40", "[CANONICAL-PROXY] cctg_rate_vn 2026-10-12"),
            (f"NHNN TB huy động >12T {last} thấp/cao", f"{sl.iloc[1]:.2f}/{sl.iloc[0]:.2f}" if len(sl) == 2 else str(sl.to_dict()), "[SRC-PIT] FiinPro snapshot"),
            ("Lãi cho vay TB", "8.3-10.7", "[SRC thứ cấp] VNF 21/09/2026 (TB 08/2026 10,7%; nhóm NHTM 8,3–10,5% 07/2026)")]
    T = pd.DataFrame(rows, columns=["proxy", "rate_pct", "source"]); T.to_csv(csv("out_rf_proxies.csv"), index=False)
    P("[3] rf proxy:"); P(T.to_string(index=False))
    P(f"  kiểm: rf_c {RF_C} nằm giữa TPCP 10Y 4,47 và lãi cho vay 8,3–10,7 ⇒ {'ĐẠT' if 4.47 < RF_C < 8.3 else 'KHÔNG'}")


# =================================================================== 5. justify
def part5(d0v):
    d = d0v[(d0v.PE > 0) & d0v.ROE5Y.notna()].copy(); nb = d[~d.icb.isin(BANK)]; bk = d[d.icb.isin(BANK)]
    P(f"[5] justify: {len(d0v)} mã có PE; lỗ {int((d0v.PE <= 0).sum())}; ROE5Y NULL {int(((d0v.PE > 0) & d0v.ROE5Y.isna()).sum())}; xếp {len(nb)} phi-NH + {len(bk)} NH")
    rows = []
    for g in (G_C,) + G_BAND:
        for kk in range(90, 171, 5):
            ke = kk / 10
            for lab, x in (("non_bank", nb), ("bank", bk)):
                gg, k = g / 100, ke / 100
                roe = x.ROE5Y.clip(lower=gg + 0.01, upper=0.40)
                pe_imp = (1 - gg / roe) * (1 + gg) / (k - gg)
                rich = x.PE > pe_imp; vrich = x.PE > 1.5 * pe_imp
                rows.append(dict(g=g, ke=ke, group=lab, n=len(x), pct_rich=round(100 * rich.mean(), 1),
                                 pct_mcap_rich=round(100 * x.mcap[rich].sum() / x.mcap.sum(), 1),
                                 pct_very_rich=round(100 * vrich.mean(), 1), pe_imp_median=round(float(pe_imp.median()), 2)))
    T = pd.DataFrame(rows); T.to_csv(csv("out_justify_grid.csv"), index=False)
    # Ke* = trung vị ICC từng mã phi-NH
    icc = {}
    for g in (G_C,) + G_BAND:
        gg = g / 100; roe = nb.ROE5Y.clip(lower=gg + 0.01, upper=0.40)
        ki = 100 * (gg + (1 - gg / roe) * (1 + gg) / nb.PE)
        icc[g] = (float(ki.median()), float(ki.quantile(0.25)), float(ki.quantile(0.75)),
                  float(np.average(ki, weights=nb.mcap)))
    P(T[(T.g == G_C) & (T.group == "non_bank")][["ke", "pct_rich", "pct_mcap_rich", "pct_very_rich", "pe_imp_median"]].to_string(index=False))
    P(T[(T.g == G_C) & (T.group == "bank") & (T.ke.isin([11.0, 12.0, 13.0, 14.0, 15.0, 16.0]))][["ke", "n", "pct_rich", "pct_mcap_rich"]].to_string(index=False))
    P(f"  PE thực trung vị phi-NH = {nb.PE.median():.2f}; ROE5Y trung vị = {nb.ROE5Y.median():.4f}")
    for g, (m, q1, q3, w) in icc.items():
        P(f"  ICC mã-lẻ phi-NH g={g}: trung vị {m:.2f} (IQR {q1:.2f}–{q3:.2f}); TB trọng số vốn hoá {w:.2f} ⇒ ERP trung vị {m - RF_C:.2f}")
    pd.DataFrame([dict(g=g, icc_median=round(m, 3), icc_q1=round(q1, 3), icc_q3=round(q3, 3), icc_mcapw=round(w, 3)) for g, (m, q1, q3, w) in icc.items()]).to_csv(csv("out_icc.csv"), index=False)
    return T, icc


# =================================================================== 6. DGC
def part6(erp_lo, erp_c, erp_hi):
    spec = importlib.util.spec_from_file_location("mke", os.path.join(HERE, "..", "dgc_discount_rate_20261029", "model_ke.py"))
    K = importlib.util.module_from_spec(spec); spec.loader.exec_module(K); M = K.M
    A = K.run_cfg(M.CFG_A, K.KE_R7)
    for lab, got, exp in (("A dcf nghich", A["dcf_nghich"], 21407), ("A dcf coso", A["dcf_coso"], 32925), ("A dcf thuan", A["dcf_thuan"], 41779), ("A ev", A["ev"], 29817)):
        P(f"SELFCHECK {lab}: {got} vs {exp} lệch {got - exp}"); assert got == exp
    rows = [dict(cand="r7 hiện hành", rf=7.4, beta=1.0, erp=7.5, ke=14.9, **{k: A[k] for k in ("dcf_nghich", "dcf_coso", "dcf_thuan", "ev")})]
    for el, e in (("ERP thấp", erp_lo), ("ERP trung tâm", erp_c), ("ERP cao", erp_hi), ("Damodaran mature (sàn)", DAMO_MATURE), ("Damodaran tổng (nước ngoài)", DAMO_TOTAL)):
        for b in (1.0, 1.1, 1.11, 1.2):
            ke = round(RF_C + b * e, 2)
            r = K.run_cfg(M.CFG_A, ke / 100)
            rows.append(dict(cand=el, rf=RF_C, beta=b, erp=round(e, 2), ke=ke, **{k: r[k] for k in ("dcf_nghich", "dcf_coso", "dcf_thuan", "ev")}))
    T = pd.DataFrame(rows); T.to_csv(csv("out_dgc_ke.csv"), index=False)
    P("[6] DGC tầng A:"); P(T.to_string(index=False))
    M.CFG.clear(); M.CFG.update(M.CFG_A)


def main():
    s = load_snap(); vni = pd.read_csv(os.path.join(DD, "vnindex_daily.csv"))
    T1, D1, D2, d0v = part1(s, vni)
    T2, D3, D4, dep_lvl = part2(vni)
    part3(dep_lvl)
    D = {"D1": D1, "D2": D2, "D3": D3, "D4": D4}
    c = float(np.median(list(D.values()))); lo, hi = min(D.values()), max(D.values())
    floor = c < DAMO_MATURE; c_used = max(c, DAMO_MATURE)
    P(f"[4] ERP nội địa: {', '.join(f'{k}={v:.3f}' for k, v in D.items())} ⇒ trung tâm (trung vị) {c:.3f}{' → SÀN 4,23' if floor else ''}; dải {lo:.3f}–{hi:.3f}")
    for b in (1.0, 1.1, 1.2):
        P(f"  Ke β={b}: {RF_C + b * lo:.2f} / {RF_C + b * c_used:.2f} / {RF_C + b * hi:.2f}")
    pd.DataFrame([dict(k=k, erp=round(v, 3)) for k, v in D.items()] + [dict(k="central", erp=round(c_used, 3)), dict(k="lo", erp=round(lo, 3)), dict(k="hi", erp=round(hi, 3))]).to_csv(csv("out_erp_choice.csv"), index=False)
    part5(d0v)
    part6(lo, c_used, hi)
    with open(csv("run_stdout.txt"), "w") as f: f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
