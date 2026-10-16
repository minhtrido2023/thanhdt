#!/usr/bin/env python3
"""Robustness cho 2 đặc trưng GO cơ học (idio_vol60, limit_freq60 @ fwdx_3m):
kiểm soát thêm ngành ICB1 + thanh khoản (Amihud) + momentum 60 phiên trước sự kiện; quintile profile
(trung bình vs trung vị — kiểm hình dạng 'xổ số'); IS/OOS. Output: robustness_vol.csv, quintile_profile_vol.csv
"""
import glob, os, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
OUT = os.path.dirname(os.path.abspath(__file__))
C = "/home/trido/thanhdt/WorkingClaude/data/bq_cache"
ev = pd.read_csv(f"{OUT}/events_features_fp.csv.gz", parse_dates=["rd"])
U = ev[ev.in_universe & ev.rating.notna()].copy()
U = U[U.groupby("wave").wave.transform("size") >= 30]   # bỏ đợt lẻ (vd 2026Q3 mới 1 sự kiện)

px = pd.concat([pd.read_parquet(f, columns=["time", "ticker", "Close"]) for f in sorted(glob.glob(f"{C}/ticker/*.parquet"))])
px["time"] = pd.to_datetime(px.time); px = px.drop_duplicates(["ticker", "time"])
cal = pd.DatetimeIndex(sorted(px[px.ticker == "VNINDEX"].time.unique()))
cl = px.pivot(index="time", columns="ticker", values="Close").reindex(cal); cl = cl.where(cl > 0).ffill(limit=5)
ti = {t: i for i, t in enumerate(cl.columns)}; CL = cl.values
t0 = np.searchsorted(cal.values, U.rd.values)
U["mom60"] = [CL[t - 2, ti[k]] / CL[t - 62, ti[k]] - 1 if t >= 62 else np.nan for t, k in zip(t0, U.ticker)]

def resid(df, f, ctrl):
    out = pd.Series(np.nan, index=df.index)
    for w, z in df.groupby("wave"):
        z = z.dropna(subset=[f] + [c for c in ctrl if c not in ("rating", "sector1")])
        if len(z) < 30: continue
        X = [pd.get_dummies(z.rating.astype(int), prefix="r", drop_first=True)]
        if "sector1" in ctrl: X.append(pd.get_dummies(z.sector1, prefix="s", drop_first=True))
        for c in ctrl:
            if c not in ("rating", "sector1"): X.append(z[c].rank(pct=True).rename(c))
        X = pd.concat(X, axis=1).astype(float); X.insert(0, "c", 1.0)
        y = z[f].rank(pct=True).values
        b, *_ = np.linalg.lstsq(X.values, y, rcond=None)
        out[z.index] = y - X.values @ b
    return out

def ic_stats(x, h):
    d = pd.DataFrame({"x": x, "y": U[h], "wave": U.wave, "year": U.year}).dropna()
    ic = d.groupby("wave").apply(lambda z: z.x.corr(z.y, method="spearman"))
    yr = d.groupby("wave").year.agg(lambda s: s.mode().iloc[0])
    t = lambda s: s.mean() / s.std(ddof=1) * np.sqrt(len(s))
    return dict(n=len(d), ic=ic.mean(), t=t(ic), ic_IS=ic[yr < 2020].mean(), t_IS=t(ic[yr < 2020]),
                ic_OOS=ic[yr >= 2020].mean(), t_OOS=t(ic[yr >= 2020]))

rows = []
SPECS = {"rating": ["rating"], "rating+sector": ["rating", "sector1"],
         "rating+sector+amihud": ["rating", "sector1", "amihud_log"],
         "rating+sector+amihud+mom60": ["rating", "sector1", "amihud_log", "mom60"],
         "rating+sector+amihud+mom60+car_m5m1": ["rating", "sector1", "amihud_log", "mom60", "car_m5m1"]}
for f in ["idio_vol60", "limit_freq60"]:
    for h in ["fwdx_1m", "fwdx_3m"]:
        for nm, ctrl in SPECS.items():
            rows.append(dict(feature=f, horizon=h, controls=nm, **ic_stats(resid(U, f, ctrl), h)))
    # limit_freq kiểm soát luôn idio_vol (và ngược lại) — có phải cùng một thứ?
    other = "idio_vol60" if f == "limit_freq60" else "limit_freq60"
    rows.append(dict(feature=f, horizon="fwdx_3m", controls=f"rating+sector+amihud+mom60+{other}",
                     **ic_stats(resid(U, f, ["rating", "sector1", "amihud_log", "mom60", other]), "fwdx_3m")))
R = pd.DataFrame(rows); R.to_csv(f"{OUT}/robustness_vol.csv", index=False)

prof = []
for f in ["idio_vol60", "limit_freq60"]:
    U["q"] = U.groupby("wave")[f].transform(lambda s: pd.qcut(s.rank(method="first"), 5, labels=False) + 1)
    for per, m in (("IS", U.year < 2020), ("OOS", U.year >= 2020)):
        g = U[m].groupby("q")
        for q, z in g:
            prof.append(dict(feature=f, period=per, quintile=q, n=len(z), mean_fwdx_3m=z.fwdx_3m.mean(),
                             median_fwdx_3m=z.fwdx_3m.median(), mean_fwd_3m=z.fwd_3m.mean(),
                             crash_rate_mdd20=(z.mdd_3m < -0.20).mean(), mean_rating=z.rating.mean()))
P = pd.DataFrame(prof); P.to_csv(f"{OUT}/quintile_profile_vol.csv", index=False)
pd.set_option("display.width", 220)
print(R.round(4).to_string(index=False)); print(P.round(4).to_string(index=False))
print("corr(idio_vol60, limit_freq60) spearman:", round(U.idio_vol60.corr(U.limit_freq60, method="spearman"), 3))
