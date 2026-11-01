# -*- coding: utf-8 -*-
"""Việc 1+2: lưới g_T (3,0–8,0% bước 0,25) cho s=0 và s=0,5; đường fin vs live; nhóm ổn định/nhảy/post-step-excluded.
Metric & định nghĩa: PREREG.md. FV: đúng variants.fv (min(g_T thô, cap lưới))."""
import os, sys
import numpy as np, pandas as pd
WC = "/home/trido/thanhdt/WorkingClaude"
HERE = os.path.dirname(os.path.abspath(__file__))
OLD = os.path.join(HERE, "..", "dcf_vn_calibration_20261101")
sys.path.insert(0, OLD); sys.path.insert(0, WC)
os.environ["DCF_RATE_FRAME"] = "domestic_v2"
import engine as E            # noqa: E402  (ghim fin + chdir OLD)
import gdp_growth_vn as _gdp  # noqa: E402
OUT = os.path.join(HERE, "out"); DATA = os.path.join(HERE, "data")
P = print
RF, ERP = 6.75, 5.5
G_FLOOR, G_CAP = -0.02, 0.20
GRID = np.round(np.arange(0.03, 0.0801, 0.0025), 4)


def load():
    p = pd.read_parquet(os.path.join(OLD, "data", "panel_monthly.parquet"))
    m, base = E.base_valid(p)
    p = p[m & p.Price.notna() & (p.Price > 0)].copy()
    p["base"] = base[p.index].values
    L = pd.read_parquet(os.path.join(DATA, "os_live.parquet"))[["t", "ticker", "os_live", "source", "method"]]
    p = p.merge(L, on=["t", "ticker"], how="left")
    assert p.os_live.notna().all()
    gt_raw = {t: E.D.terminal_growth(t) + _gdp.longrun_real_gdp(t) for t in p.t.unique()}
    p["g_T_raw"] = p.t.map(gt_raw)
    # cờ nhóm (PREREG §Việc 2)
    ri = pd.read_parquet(os.path.join(OLD, "data", "row_inputs.parquet")).sort_values(["ticker", "time"])
    ri["osh_max"] = ri.groupby("ticker").OShares.transform(lambda s: s.rolling(9, center=True, min_periods=1).max())
    ri["osh_min"] = ri.groupby("ticker").OShares.transform(lambda s: s.rolling(9, center=True, min_periods=1).min())
    ri["unstable"] = ri.osh_max / ri.osh_min > 1.10
    ri["step"] = (ri.OShares / ri.groupby("ticker").OShares.shift(1) - 1).abs() > 0.10   # PIT: so dòng liền trước
    p = pd.merge_asof(p.sort_values("t"), ri[["ticker", "time", "unstable", "step"]].sort_values("time"),
                      left_on="t", right_on="time", by="ticker", direction="backward", suffixes=("", "_ri"))
    p["unstable"] = p.unstable.fillna(False).astype(bool)
    p["poststep"] = p.step.fillna(False).astype(bool) & (p.age_days <= 100)
    return p.sort_values(["t", "ticker"]).reset_index(drop=True)


def fv(p, osh, s, cap):
    gT = np.minimum(p.g_T_raw.values, cap)
    r = (RF + ERP) / 100
    gT = np.where(r <= gT, r - 0.01, gT)
    graw = np.where(np.isnan(p.g_raw.values), gT, p.g_raw.values)
    gc = np.clip(graw, G_FLOOR, G_CAP)
    ge = gT + s * (gc - gT)
    return E.fv_path(p.base.values, np.repeat(ge[:, None], 5, axis=1), gT, r, osh)


def level(p, f, mask):
    q = pd.DataFrame({"t": p.t.values, "l": np.log(p.Price.values / f)})[mask]
    q = q[np.isfinite(q.l)]
    return q.groupby("t").l.median()


def calib(Ly):
    """Ly: DataFrame năm × ô lưới (TB log median P/FV theo năm)."""
    full = Ly.mean().abs().idxmin()
    is_ = Ly[Ly.index <= 2019].mean().abs().idxmin()
    oos = Ly[Ly.index >= 2020].mean().abs().idxmin()
    loyo = [Ly.drop(y).mean().abs().idxmin() for y in Ly.index]
    return full, is_, oos, min(loyo), max(loyo)


def main():
    p = load()
    P("panel rows", len(p), "months", p.t.nunique(), "| g_T thô min/med/max", p.g_T_raw.min().round(4), p.g_T_raw.median().round(4), p.g_T_raw.max().round(4))
    groups = {"all": np.ones(len(p), bool), "stable": ~p.unstable.values, "unstable": p.unstable.values,
              "ex_poststep": ~p.poststep.values}
    for k, m in groups.items():
        P(f"  nhóm {k}: {int(m.sum())} dòng-tháng ({m.mean():.1%}), {p.t[m].nunique()} tháng, {p.ticker[m].nunique()} mã")
    P("  % dòng live != fin (>1e-9):", f"{(np.abs(p.os_live / p.OShares - 1) > 1e-9).mean():.2%}", "| nguồn:", p.source.value_counts().to_dict())
    res, mp = [], []
    LY = {}
    for path, col in (("fin", "OShares"), ("live", "os_live")):
        osh = p[col].values
        for s in (0.0, 0.5):
            L = {g: {} for g in groups}
            for cap in GRID:
                f = fv(p, osh, s, cap)
                for g, m in groups.items():
                    L[g][cap] = level(p, f, m)
            for g in groups:
                D = pd.DataFrame(L[g])
                Ly = D.groupby(D.index.year).mean()
                LY[(path, s, g)] = Ly
                full, is_, oos, lo, hi = calib(Ly)
                at = lambda c: float(np.exp(Ly[c].mean()))
                res.append({"path": path, "s": s, "group": g, "gT_full": full, "gT_IS": is_, "gT_OOS": oos,
                            "loyo_min": lo, "loyo_max": hi, "medPFV_at_4.5": at(0.045), "medPFV_at_5.5": at(0.055),
                            "n_rows": int(groups[g].sum())})
    R = pd.DataFrame(res)
    R.to_csv(os.path.join(OUT, "level_gT_star.csv"), index=False)
    with pd.option_context("display.width", 250, "display.max_columns", 30):
        P(R.round(4).to_string(index=False))
    # hố giữa nhóm: (b) − (a)
    P("=== phân cách g_T* giữa nhóm nhảy (b) và ổn định (a), full-sample (pp)")
    for path in ("fin", "live"):
        for s in (0.0, 0.5):
            a = R[(R.path == path) & (R.s == s) & (R.group == "stable")].iloc[0]
            b = R[(R.path == path) & (R.s == s) & (R.group == "unstable")].iloc[0]
            c = R[(R.path == path) & (R.s == s) & (R.group == "ex_poststep")].iloc[0]
            P(f"  {path} s={s}: stable {a.gT_full:.4f}  unstable {b.gT_full:.4f}  Δ={100*(b.gT_full-a.gT_full):+.2f}pp | ex_poststep {c.gT_full:.4f}")
    pd.to_pickle(LY, os.path.join(DATA, "level_LY.pkl"))
    # tác động live 30/10/2026
    last = (p.t == p.t.max()).values
    pl = p[last]
    v0 = fv(p, p.os_live.values, 0.5, 0.055)[last]            # production mặc định: live, s=.5, cap 5,5%
    rows = []
    def imp(name, f):
        ok = np.isfinite(f) & np.isfinite(v0) & (f > 0)
        mos = (f - pl.Price.values) / f
        rows.append({"variant": name, "n": int(ok.sum()), "FV_med_vs_V0live": float(np.median(f[ok] / v0[ok]) - 1),
                     "pct_RE": float((mos[ok] > 0).mean()), "RICH_sau": int((mos[ok] < -1).sum())})
    imp("V0 live s=.5 gT5.5 (production)", v0)
    imp("V0 fin s=.5 gT5.5", fv(p, p.OShares.values, 0.5, 0.055)[last])
    for path, col in (("fin", "OShares"), ("live", "os_live")):
        for s in (0.0, 0.5):
            for g in ("all", "stable", "unstable"):
                c = R[(R.path == path) & (R.s == s) & (R.group == g)].iloc[0].gT_full
                imp(f"{path} s={s} gT*={c:.4f} (calib nhóm {g})", fv(p, p[col].values, s, c)[last])
    I = pd.DataFrame(rows)
    I.to_csv(os.path.join(OUT, "level_live_impact_20261030.csv"), index=False)
    P("=== tác động live 30/10/2026"); P(I.round(4).to_string(index=False))
    p.drop(columns=[c for c in p.columns if c in ("rt",)]).to_parquet(os.path.join(DATA, "panel_live.parquet"))


if __name__ == "__main__":
    main()
