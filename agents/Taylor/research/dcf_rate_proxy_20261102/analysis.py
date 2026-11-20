# -*- coding: utf-8 -*-
"""dcf_rate_proxy — job Taylor_20261102_012810. Theo PREREG.md (commit 43f941991). R&D thuần.
Chạy: $DNA_PYEXE analysis.py  (đọc data/*.csv + panel_live của dcf_level_rerun_20261102)."""
import os, sys
import numpy as np, pandas as pd
WC = "/home/trido/thanhdt/WorkingClaude"
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..")
OUT = os.path.join(HERE, "out"); DATA = os.path.join(HERE, "data")
sys.path.insert(0, os.path.join(RES, "dcf_vn_calibration_20261101")); sys.path.insert(0, WC)
os.environ["DCF_RATE_FRAME"] = "domestic_v2"
import engine as E                 # noqa: E402  (chdir sang thư mục engine — mọi path dưới đây tuyệt đối)
import deposit_rate_vn as DR       # noqa: E402
import sbv_macro_overlay as SBV    # noqa: E402
P = print
SEED, NBOOT, BLOCK = 20261102, 2000, 12
R_CONST, G_CAP, S = 0.1225, 0.055, 0.5
EP = {"E1_2022_tang": ("2021-12", "2022-12"), "E2_2023_giam": ("2022-12", "2023-12"), "E3_2026_tang": ("2025-12", "2026-10")}
IDX = pd.period_range("2012-01", "2026-10", freq="M")


# ---------------- proxies (theo tháng, nhãn Period) ----------------
def step_to_month(ev_t, ev_v):
    s = pd.Series(np.asarray(ev_v, float), index=pd.to_datetime(np.asarray(ev_t))).sort_index()
    me = IDX.to_timestamp(how="end").normalize()
    return pd.Series(s.reindex(s.index.union(me)).ffill().loc[me].values, index=IDX)


def proxies():
    px = {}
    ev = DR.deposit_events_df(); px["dep12"] = step_to_month(ev.time, ev.deposit_rate)
    r = pd.DataFrame(SBV.SBV_REFI_EVENTS, columns=["t", "v"]); px["refi"] = step_to_month(r.t, r.v)
    ic = os.path.join(RES, "idle_cash_proxy_20260927")
    d1 = pd.read_csv(os.path.join(ic, "fiinprox_deposit_1m_big4_monthly_2019_2026.csv"))
    d1 = d1[d1.series == "big4_1m_individual"]
    px["dep1m"] = pd.Series(d1.rate_pct.values, index=pd.PeriodIndex(d1.period, freq="M")).reindex(IDX)
    sb = pd.read_csv(os.path.join(ic, "fiinprox_sbv_avg_deposit_rate_monthly_2011_2026.csv"))
    for k, lab in (("sbv_hi", "(cao nhất)"), ("sbv_lo", "(thấp nhất)")):
        q = sb[sb.series.str.contains(lab, regex=False)]
        px[k] = pd.Series(q.rate_pct.values, index=pd.PeriodIndex(q.period, freq="M")).reindex(IDX).ffill(limit=2)
    ib = pd.read_csv(os.path.join(ic, "fiinprox_interbank_avg_rate_monthly_2014_2026.csv"))
    for k, lab in (("ib_on", "qua đêm"), ("ib_1w", "1 tuần"), ("ib_1m", "1 tháng"), ("ib_3m", "3 tháng")):
        q = ib[ib.series == f"Lãi suất BQ liên NH kỳ hạn {lab}"]
        px[k] = pd.Series(q.rate_pct.values, index=pd.PeriodIndex(pd.to_datetime(q.period), freq="M")).reindex(IDX)
    te = pd.read_csv(os.path.join(DATA, "te_macro.csv"), parse_dates=["d"])
    for k, sk in (("te_ib3m", "vn_interbank_3m"), ("gb10", "vn_bond_10y")):
        q = te[te.series_key == sk].set_index("d").value
        m = q.groupby(q.index.to_period("M")).mean()
        px[k] = m.reindex(IDX)
    df = pd.DataFrame(px)
    # mẫu chung 2014-01→: dep1m chỉ 2019-02+
    return df


def market():
    v = pd.read_csv(os.path.join(DATA, "vnindex_pe.csv"), parse_dates=["time"])
    v["m"] = v.time.dt.to_period("M")
    g = v.groupby("m")
    m = pd.DataFrame({"vni": g.Close.last(), "pe": g.VNINDEX_PE.mean()}).reindex(IDX)
    m["ey"] = 100.0 / m.pe
    return m


# ---------------- DCF ----------------
def load_panel():
    p = pd.read_parquet(os.path.join(RES, "dcf_level_rerun_20261102", "data", "panel_live.parquet"))
    p["m"] = p.t.dt.to_period("M")
    return p.reset_index(drop=True)


def fv(p, r, gcap):
    r = np.broadcast_to(np.asarray(r, float), (len(p),))
    gT = np.minimum(p.g_T_raw.values, np.broadcast_to(np.asarray(gcap, float), (len(p),)))
    gT = np.where(r - gT < 0.01, r - 0.01, gT)
    graw = np.where(np.isnan(p.g_raw.values), gT, p.g_raw.values)
    ge = gT + S * (np.clip(graw, -0.02, 0.20) - gT)
    return E.fv_path(p.base.values, np.repeat(ge[:, None], 5, axis=1), gT, r, p.os_live.values)


def rstar(p, gcap):
    codes, months = pd.factorize(p.m, sort=True)
    lo = np.full(len(months), 0.05); hi = np.full(len(months), 0.40)
    lp = np.log(p.Price.values)
    for _ in range(45):
        mid = (lo + hi) / 2
        l = lp - np.log(fv(p, mid[codes], gcap))
        med = pd.Series(np.where(np.isfinite(l), l, np.nan)).groupby(codes).median().values
        # median log(P/FV) tăng theo r (FV giảm) ⇒ med>0 nghĩa r quá cao
        hi = np.where(med > 0, mid, hi); lo = np.where(med > 0, lo, mid)
    return pd.Series((lo + hi) / 2 * 100, index=pd.PeriodIndex(months, freq="M"))


# ---------------- thống kê ----------------
def block_boot_idx(n, rng):
    k = int(np.ceil(n / BLOCK)); st = rng.integers(0, n - BLOCK + 1, k)
    return np.concatenate([np.arange(s, s + BLOCK) for s in st])[:n]


def corr_ci(x, y, rng, spearman=False):
    d = pd.concat([x, y], axis=1).dropna()
    if len(d) < 24:
        return np.nan, np.nan, np.nan, len(d)
    a, b = d.iloc[:, 0].values, d.iloc[:, 1].values
    if spearman:
        a, b = pd.Series(a).rank().values, pd.Series(b).rank().values
    c = np.corrcoef(a, b)[0, 1]
    bs = []
    for _ in range(NBOOT):
        i = block_boot_idx(len(a), rng)
        if a[i].std() > 0 and b[i].std() > 0:
            bs.append(np.corrcoef(a[i], b[i])[0, 1])
    return c, np.percentile(bs, 2.5), np.percentile(bs, 97.5), len(d)


def main():
    rng = np.random.default_rng(SEED)
    X = proxies(); M = market(); p = load_panel()
    M["rstar"] = rstar(p, G_CAP).reindex(IDX)
    M["rstar_g45"] = rstar(p, 0.045).reindex(IDX)
    A = pd.concat([X, M], axis=1)
    A.index.name = "month"
    A.round(4).to_csv(os.path.join(OUT, "monthly_series.csv"))
    PX = list(X.columns)
    W = A.loc["2014-01":]
    # (i)+(iii) giai đoạn
    d12 = W.diff(12)

    def ep_rows(Wv):
        rows = []
        for k in PX + ["rstar", "rstar_g45", "ey"]:
            sd = d12[k].std()
            row = {"proxy": k, "sd_d12": sd}
            lastv = Wv[k].last_valid_index()
            for e, (a, b) in EP.items():
                b_eff = min(pd.Period(b), lastv)   # PREREG: E3 tới 2026-10 "hoặc tháng cuối có dữ liệu"
                row[f"{e}_end"] = str(b_eff)
                dv = Wv.at[b_eff, k] - Wv.at[pd.Period(a), k]
                row[f"{e}_d"] = dv; row[f"{e}_dz"] = dv / sd if sd else np.nan
                dr = Wv.at[b_eff, "rstar"] - Wv.at[pd.Period(a), "rstar"]   # r*/EY đo CÙNG cửa sổ
                de = Wv.at[b_eff, "ey"] - Wv.at[pd.Period(a), "ey"]
                row[f"{e}_sign_ok_rstar"] = bool(np.sign(dv) == np.sign(dr)) if np.isfinite(dv) and dv != 0 else None
                row[f"{e}_sign_ok_ey"] = bool(np.sign(dv) == np.sign(de)) if np.isfinite(dv) and dv != 0 else None
                row[f"{e}_drstar_per_dproxy"] = dr / dv if np.isfinite(dv) and dv != 0 else np.nan
            rows.append(row)
        return pd.DataFrame(rows)
    # NGOÀI PREREG (độ bền): mốc = TB 3 tháng kết thúc tại mốc, tránh một bản in cuối năm
    ep_rows(W.rolling(3, min_periods=3).mean()).to_csv(os.path.join(OUT, "episodes_avg3_ngoai_prereg.csv"), index=False)
    EPT = ep_rows(W)
    EPT.to_csv(os.path.join(OUT, "episodes.csv"), index=False)
    # mốc đầu/cuối cho bảng
    pts = sorted({pd.Period(x) for ab in EP.values() for x in ab})
    W.loc[pts, PX + ["rstar", "rstar_g45", "ey", "pe", "vni"]].round(3).to_csv(os.path.join(OUT, "episode_levels.csv"))
    # (ii) lead-lag Δ1M
    D1 = W.diff()
    D1["dlogpe"] = np.log(W.pe).diff(); D1["dlogvni"] = np.log(W.vni).diff()
    ll = []
    for k in PX:
        for tgt in ("rstar", "dlogpe", "dlogvni", "ey"):
            for lag in range(-6, 7):
                x = D1[k].shift(lag)          # lag>0: proxy tháng t−lag so với mục tiêu tháng t ⇒ proxy DẪN
                c = pd.concat([x, D1[tgt]], axis=1).dropna()
                ll.append({"proxy": k, "target": tgt, "lag": lag, "corr": c.corr().iloc[0, 1] if len(c) > 24 else np.nan, "n": len(c)})
    LL = pd.DataFrame(ll); LL.to_csv(os.path.join(OUT, "leadlag.csv"), index=False)
    ci = []
    for k in PX:
        for tgt in ("rstar", "dlogpe", "ey"):
            sub = LL[(LL.proxy == k) & (LL.target == tgt)].dropna()
            if sub.empty:
                continue
            best = int(sub.loc[sub["corr"].abs().idxmax(), "lag"])
            for lag in sorted({0, best}):
                c, lo, hi, n = corr_ci(D1[k].shift(lag), D1[tgt], rng)
                ci.append({"proxy": k, "target": tgt, "lag": lag, "is_best": lag == best, "corr": c, "ci_lo": lo, "ci_hi": hi, "n": n})
    # liên NH dẫn huy động?
    for src in ("ib_1m", "ib_3m", "te_ib3m", "refi", "gb10"):
        for dst in ("sbv_lo", "sbv_hi", "dep1m"):
            sub = [(lag, pd.concat([D1[src].shift(lag), D1[dst]], axis=1).dropna().corr().iloc[0, 1]) for lag in range(0, 7)]
            best = max(sub, key=lambda z: abs(z[1]) if np.isfinite(z[1]) else -1)[0]
            for lag in sorted({0, best}):
                c, lo, hi, n = corr_ci(D1[src].shift(lag), D1[dst], rng)
                ci.append({"proxy": src, "target": dst, "lag": lag, "is_best": lag == best, "corr": c, "ci_lo": lo, "ci_hi": hi, "n": n})
    CI = pd.DataFrame(ci); CI.to_csv(os.path.join(OUT, "leadlag_ci.csv"), index=False)
    # Δ3M không chồng (cuối quý) proxy vs r*
    Q = W[W.index.month.isin([3, 6, 9, 12])].diff()
    q3 = []
    for k in PX:
        c, lo, hi, n = corr_ci(Q[k], Q["rstar"], rng)
        c2, lo2, hi2, _ = corr_ci(Q[k], Q["ey"], rng)
        q3.append({"proxy": k, "corr_d3m_rstar": c, "lo": lo, "hi": hi, "n": n, "corr_d3m_ey": c2, "lo_ey": lo2, "hi_ey": hi2})
    Q3 = pd.DataFrame(q3); Q3.to_csv(os.path.join(OUT, "d3m_corr.csv"), index=False)
    # luật chọn
    first = W.apply(lambda s: s.first_valid_index())
    sel = []
    for _, r in EPT[EPT.proxy.isin(PX)].iterrows():
        a = all(r[f"{e}_sign_ok_rstar"] is True and r[f"{e}_sign_ok_ey"] is True for e in EP)
        b = sum(abs(r[f"{e}_dz"]) >= 0.5 for e in EP if np.isfinite(r[f"{e}_dz"])) >= 2
        c = (r.proxy != "dep12") and first[r.proxy] <= pd.Period("2014-01")
        sel.append({"proxy": r.proxy, "a_dir3of3": a, "b_sens2of3": b, "c_pit2014": c, "pass": a and b and c,
                    "corr_d3m_rstar": float(Q3.set_index("proxy").at[r.proxy, "corr_d3m_rstar"]), "first": str(first[r.proxy])})
    SEL = pd.DataFrame(sel).sort_values(["pass", "corr_d3m_rstar"], ascending=False)
    SEL.to_csv(os.path.join(OUT, "selection.csv"), index=False)
    winners = SEL[SEL["pass"]].proxy.tolist()
    P("=== luật chọn"); P(SEL.round(3).to_string(index=False))
    best = winners[0] if winners else None
    P("proxy tốt nhất:", best)
    # ---- kịch bản DCF ----
    pub_lag = {"sbv_hi": 1, "sbv_lo": 1}   # NHNN công bố khoảng huy động tháng M vào ~đầu M+1
    cands = ([best] if best else []) + [k for k in ("gb10", "sbv_lo") if k != best]
    fwd = np.log(A.vni.shift(-12) / A.vni)
    pm = p.m.values
    scen = {"a_const": (np.full(len(p), R_CONST), np.full(len(p), G_CAP))}
    erp_tab = []
    for k in cands:
        s = A[k].shift(pub_lag.get(k, 0))
        base = s.loc["2014-01":"2026-10"]
        if base.isna().any():
            base_f = base.ffill().bfill()
        else:
            base_f = base
        erp = R_CONST * 100 - base_f.mean()
        rr = (base_f + erp) / 100
        gg = G_CAP + (base_f - base_f.mean()) / 100
        erp_tab.append({"proxy": k, "erp_b": erp, "r_min": rr.min(), "r_max": rr.max(), "r_last": rr.iloc[-1], "nan_filled": int(base.isna().sum())})
        rmap = rr.reindex(pm).values; gmap = gg.reindex(pm).values
        scen[f"b_{k}"] = (rmap, np.full(len(p), G_CAP))
        scen[f"c_{k}"] = (rmap, gmap)
    pd.DataFrame(erp_tab).to_csv(os.path.join(OUT, "scen_erp.csv"), index=False)
    MOS = {}; ts = {}
    for nm, (rr, gg) in scen.items():
        f = fv(p, rr, gg)
        mos = (f - p.Price.values) / f
        ok = np.isfinite(mos) & (f > 0)
        MOS[nm] = np.where(ok, mos, np.nan)
        q = pd.DataFrame({"m": pm, "re": (mos > 0).astype(float), "ok": ok, "lpf": np.log(p.Price.values / np.where(f > 0, f, np.nan))})
        q = q[q.ok]
        ts[nm] = q.groupby("m").re.mean()
        ts[nm + "_medPFV"] = np.exp(q.groupby("m").lpf.median())
    TS = pd.DataFrame(ts); TS.index = pd.PeriodIndex(TS.index, freq="M")
    TS.round(4).to_csv(os.path.join(OUT, "scen_pctRE_monthly.csv"))
    last = (p.m == p.m.max()).values
    f0 = None; imp = []
    for nm, (rr, gg) in scen.items():
        f = fv(p, rr, gg)[last]
        if f0 is None:
            f0 = f
        mos = (f - p.Price.values[last]) / f; m0 = (f0 - p.Price.values[last]) / f0
        ok = np.isfinite(mos) & np.isfinite(m0) & (f > 0) & (f0 > 0)
        imp.append({"scen": nm, "r_last": float(np.nanmedian(np.asarray(rr)[last])), "gT_last": float(np.nanmedian(np.asarray(gg)[last])),
                    "n": int(ok.sum()), "FV_med_vs_a": float(np.median(f[ok] / f0[ok]) - 1), "pct_RE": float((mos[ok] > 0).mean()),
                    "flip_RE_to_RICH": int(((m0 > 0) & (mos <= 0) & ok).sum()), "flip_RICH_to_RE": int(((m0 <= 0) & (mos > 0) & ok).sum())})
    IMP = pd.DataFrame(imp); IMP.to_csv(os.path.join(OUT, "scen_today.csv"), index=False)
    # tương quan hạng MoS cắt ngang vs (a)
    rk = []
    for nm in scen:
        if nm == "a_const":
            continue
        q = pd.DataFrame({"m": pm, "a": MOS["a_const"], "x": MOS[nm]}).dropna()
        rc = q.groupby("m").apply(lambda g: g.a.rank().corr(g.x.rank()), include_groups=False)
        rk.append({"scen": nm, "rank_corr_min": rc.min(), "rank_corr_med": rc.median()})
    # dự báo: Spearman(%RẺ_t, fwd 12M) 2014-01→2025-10 + hiệu với (a)
    fc = []
    win = slice(pd.Period("2014-01"), pd.Period("2025-10"))
    y = fwd.loc[win]
    for nm in scen:
        x = TS[nm].loc[win]
        c, lo, hi, n = corr_ci(x, y, rng, spearman=True)
        # hiệu vs (a) bằng cùng khối bootstrap
        d = pd.concat([TS["a_const"].loc[win], x, y], axis=1).dropna().rank().values
        diffs = []
        for _ in range(NBOOT):
            i = block_boot_idx(len(d), rng)
            diffs.append(np.corrcoef(d[i, 1], d[i, 2])[0, 1] - np.corrcoef(d[i, 0], d[i, 2])[0, 1])
        base_c = np.corrcoef(d[:, 0], d[:, 2])[0, 1]
        fc.append({"scen": nm, "spearman_pctRE_fwd12": c, "lo": lo, "hi": hi, "n": n,
                   "diff_vs_a": c - base_c, "diff_lo": np.percentile(diffs, 2.5), "diff_hi": np.percentile(diffs, 97.5)})
    FC = pd.DataFrame(fc).merge(pd.DataFrame(rk), on="scen", how="left"); FC.to_csv(os.path.join(OUT, "scen_forecast.csv"), index=False)
    keyp = [pd.Period(x) for x in ("2022-03", "2022-11", "2023-12", "2025-12", "2026-10")]
    KP = TS.reindex(keyp)[[c for c in TS.columns if not c.endswith("_medPFV")]]
    KP.round(3).to_csv(os.path.join(OUT, "scen_keypoints.csv"))
    with pd.option_context("display.width", 250, "display.max_columns", 40):
        P("=== episodes"); P(EPT[["proxy", "sd_d12"] + [f"{e}_d" for e in EP] + [f"{e}_dz" for e in EP]].round(2).to_string(index=False))
        P(EPT[["proxy"] + [f"{e}_sign_ok_rstar" for e in EP] + [f"{e}_sign_ok_ey" for e in EP]].to_string(index=False))
        P("=== d3m corr"); P(Q3.round(3).to_string(index=False))
        P("=== leadlag CI"); P(CI.round(3).to_string(index=False))
        P("=== ERP scen"); P(pd.DataFrame(erp_tab).round(3).to_string(index=False))
        P("=== today"); P(IMP.round(4).to_string(index=False))
        P("=== forecast"); P(FC.round(3).to_string(index=False))
        P("=== keypoints %RE"); P(KP.round(3).to_string())


if __name__ == "__main__":
    main()
