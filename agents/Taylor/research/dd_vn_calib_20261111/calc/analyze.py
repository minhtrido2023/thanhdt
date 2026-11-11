# -*- coding: utf-8 -*-
"""analyze.py — chỉ số (i)-(v) + tiêu chí PRELOCK K1-K3 + bootstrap cụm (mã / quý).
Input ../out/panel.parquet (build_panel.py). Output ../out/summary.json + bảng in ra.
Run: $DNA_PYEXE analyze.py [--panel path] [--tag name]
Seed cố định 20261111 => chạy lại ra cùng số (kiểm tra tái lập: so md5 summary.json).
"""
import os, sys, json, argparse
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "out")
SEED, B = 20261111, 2000

ap = argparse.ArgumentParser()
ap.add_argument("--panel", default=os.path.join(OUT, "panel.parquet"))
ap.add_argument("--tag", default="primary")
ap.add_argument("--sample", default="rating3", choices=["rating3", "pit_all"])
args = ap.parse_args()

p = pd.read_parquet(args.panel)
p = p[p.ok & p.FV.gt(0)].copy()
if args.sample == "rating3":
    p = p[p.rating <= 3]
p["q"] = p["asof"].dt.to_period("Q").astype(str)
p["yr"] = p["asof"].dt.year
p["lr0"] = np.log(p.FV / p.P0)                  # log(FV/P) tại as-of
for N in (12, 24, 36, 60):
    p[f"y{N}"] = np.log(p[f"PN{N}"] / p.P0)        # log return cùng khung
    p[f"gap{N}"] = np.abs(np.log(p[f"PN{N}"] / p.FV))
p["gap0"] = np.abs(p.lr0)
# FV cập nhật tại t+N (cùng mã) — "giá và FV đương thời có gặp nhau không"
key = p.set_index(["ticker", "asof"]).FV
for N in (12, 36):
    nxt = p["asof"] + pd.DateOffset(months=N)
    nxt = nxt.dt.to_period("Q").dt.end_time.dt.normalize()
    pq = p.assign(qe=p["asof"].dt.to_period("Q").dt.end_time.dt.normalize())
    m = pq.set_index(["ticker", "qe"]).FV
    p[f"FVn{N}"] = [m.get((t, d), np.nan) for t, d in zip(p.ticker, nxt)]
    p[f"gapc{N}"] = np.abs(np.log(p[f"PN{N}"] / p[f"FVn{N}"]))


def stats(d):
    o = {}
    o["n"] = len(d); o["n_tickers"] = d.ticker.nunique(); o["n_quarters"] = d.q.nunique()
    o["med_FV_over_P"] = float(np.exp(d.lr0.median()))
    o["frac_FV_lt_P"] = float((d.lr0 < 0).mean())
    o["frac_FV_lt_0.7P"] = float((d.FV < 0.7 * d.P0).mean())
    o["iqr_FV_over_P"] = [float(np.exp(d.lr0.quantile(.25))), float(np.exp(d.lr0.quantile(.75)))]
    for N in (12, 24, 36, 60):
        f = d[d[f"full{N}"] == True]
        o[f"n_full{N}"] = len(f)
        o[f"touch{N}"] = float(f[f"touch{N}"].mean()) if len(f) else np.nan
        o[f"touch85_{N}"] = float(f[f"touch85_{N}"].mean()) if len(f) else np.nan
        o[f"inzone_ever{N}"] = float(f[f"inzone_ever{N}"].mean()) if len(f) else np.nan
        o[f"inzone_frac_mean{N}"] = float(f[f"inzone_frac{N}"].mean()) if len(f) else np.nan
        need = f[f.lr0 < 0]                                    # giá phải GIẢM mới chạm tâm
        o[f"touch{N}_FVltP"] = float(need[f"touch{N}"].mean()) if len(need) else np.nan
        deep = f[f.FV < 0.7 * f.P0]
        o[f"touch{N}_FVlt0.7P"] = float(deep[f"touch{N}"].mean()) if len(deep) else np.nan
        o[f"n_FVlt0.7P_{N}"] = len(deep)
    for N in (12, 36, 60):
        f = d[d[f"full{N}"] == True].dropna(subset=[f"y{N}"])
        if len(f) < 30:
            continue
        o[f"gap0_med_{N}"] = float(f.gap0.median()); o[f"gapN_med_{N}"] = float(f[f"gap{N}"].median())
        o[f"gap_ratio_{N}"] = o[f"gapN_med_{N}"] / o[f"gap0_med_{N}"]
        o[f"frac_gap_closed_{N}"] = float((f[f"gap{N}"] < f.gap0).mean())
        x, y = f.lr0.values, f[f"y{N}"].values
        o[f"beta_{N}"] = float(np.polyfit(x, y, 1)[0])
        xw = np.clip(x, *np.quantile(x, [.01, .99]))
        o[f"beta_w_{N}"] = float(np.polyfit(xw, y, 1)[0])
        o[f"rankcorr_{N}"] = float(pd.Series(x).rank().corr(pd.Series(y).rank()))
    for N in (12, 36):
        f = d.dropna(subset=[f"gapc{N}"])
        if len(f) >= 30:
            o[f"gapc_ratio_{N}"] = float(f[f"gapc{N}"].median() / f.gap0.median())
            o[f"n_gapc_{N}"] = len(f)
    return o


def boot(d, by, fn, B=B, seed=SEED):
    rng = np.random.default_rng(seed)
    d = d.reset_index(drop=True)
    idx = list(d.groupby(by).indices.values())
    out = []
    for _ in range(B):
        s = rng.integers(0, len(idx), len(idx))
        out.append(fn(d.iloc[np.concatenate([idx[k] for k in s])]))
    out = np.array(out, float)
    return [float(np.nanpercentile(out, 2.5)), float(np.nanpercentile(out, 97.5))]


S = {"tag": args.tag, "sample": args.sample, "all": stats(p)}
f60 = p[p.full60 == True]; f36 = p[(p.full36 == True)].dropna(subset=["y36"])
fns = {
    "med_FV_over_P": (p, lambda d: np.exp(d.lr0.median())),
    "touch60": (f60, lambda d: d.touch60.mean()),
    "touch36": (p[p.full36 == True], lambda d: d.touch36.mean()),
    "beta_36": (f36, lambda d: np.polyfit(d.lr0.values, d.y36.values, 1)[0]),
    "gap_ratio_36": (f36, lambda d: d.gap36.median() / d.gap0.median()),
}
S["ci"] = {}
for k, (d, fn) in fns.items():
    S["ci"][k] = {"by_ticker": boot(d, "ticker", fn), "by_quarter": boot(d, "q", fn)}
# hiệu ứng thiết kế (N hiệu dụng) cho touch60 / lr0
v_iid = f60.touch60.var() / len(f60)
lo, hi = S["ci"]["touch60"]["by_quarter"]; v_q = ((hi - lo) / 3.92) ** 2
lo2, hi2 = S["ci"]["touch60"]["by_ticker"]; v_t = ((hi2 - lo2) / 3.92) ** 2
S["neff_touch60"] = {"rows": len(f60), "by_quarter": float(len(f60) * v_iid / v_q),
                     "by_ticker": float(len(f60) * v_iid / v_t)}
# tách theo năm / DT5G
S["by_year"] = {int(y): stats(g) for y, g in p.groupby("yr")}
S["by_dt5g"] = {str(s): stats(g) for s, g in p.groupby("dt5g")}
S["leave_year_out_touch60"] = {int(y): float(f60[f60["yr"] != y].touch60.mean()) for y in sorted(f60["yr"].unique())}
S["leave_year_out_medFVP"] = {int(y): float(np.exp(p[p.yr != y].lr0.median())) for y in sorted(p.yr.unique())}

a = S["all"]
K1 = a["touch60"] < 0.5
K2 = not (0.75 <= a["med_FV_over_P"] <= 1.25)
K3 = (a["gap_ratio_36"] >= 1.0) or (S["ci"]["beta_36"]["by_quarter"][0] <= 0)
S["verdict"] = {"K1_touch60_lt_50": bool(K1), "K2_medFVP_off_25": bool(K2), "K3_no_convergence": bool(K3),
                "result": "KHONG TUONG THICH" if (K1 or K2 or K3) else "TUONG THICH"}
json.dump(S, open(os.path.join(OUT, f"summary_{args.tag}.json"), "w"), indent=1, sort_keys=True, default=float)
p.to_parquet(os.path.join(OUT, f"scored_{args.tag}.parquet"))
pd.set_option("display.width", 220)
print(json.dumps({k: S["all"][k] for k in sorted(S["all"])}, indent=0, default=float))
print(json.dumps(S["ci"], indent=0)); print(S["neff_touch60"]); print(S["verdict"])
cols = ["n", "n_tickers", "med_FV_over_P", "frac_FV_lt_P", "touch36", "touch60", "touch36_FVltP", "gap_ratio_36", "beta_36"]
print(pd.DataFrame(S["by_year"]).T.reindex(columns=cols).round(3))
print(pd.DataFrame(S["by_dt5g"]).T.reindex(columns=cols).round(3))
print("LYO touch60", {k: round(v, 3) for k, v in S["leave_year_out_touch60"].items()})
print("LYO medFVP", {k: round(v, 3) for k, v in S["leave_year_out_medFVP"].items()})
