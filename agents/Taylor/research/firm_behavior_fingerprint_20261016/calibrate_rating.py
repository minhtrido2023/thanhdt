#!/usr/bin/env python3
"""Việc (3) — hiệu chỉnh rating 8L 1-5 theo kết quả thật (CHỈ ĐO, không wire).
crash = MDD 3 tháng (từ close t0+1, 63 phiên) < −20%. Rating as-of t0+1 (PIT, fa_ratings_8l eff_date).
N độc lập = đợt công bố; CI bootstrap theo ĐỢT (crash tụ theo các cú sập thị trường).
Output: rating_calibration.csv, rating_auc.csv, rating_transition.csv, rating_outlook.csv
"""
import os, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
OUT = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(20261016)
ev = pd.read_csv(f"{OUT}/events_features_fp.csv.gz", parse_dates=["rd"])
U = ev[ev.in_universe & ev.rating.notna() & ev.mdd_3m.notna()].copy()
U = U[U.groupby("wave").wave.transform("size") >= 30]
U["rating"] = U.rating.astype(int)
U["crash"] = (U.mdd_3m < -0.20).astype(int)
U["crash_x"] = (U.fwdx_3m < -0.20).astype(int)              # sụt vượt thị trường >20pp
U["period"] = np.where(U.year < 2020, "IS", "OOS")

def auc(score, y):
    s = pd.Series(score).rank().values; y = np.asarray(y); n1 = y.sum(); n0 = len(y) - n1
    return (s[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0) if n1 and n0 else np.nan

def wave_boot(df, fn, B=1000):
    waves = df.wave.unique(); grp = {w: df[df.wave == w] for w in waves}
    bs = [fn(pd.concat([grp[w] for w in rng.choice(waves, len(waves))])) for _ in range(B)]
    return np.nanpercentile(bs, [2.5, 97.5])

# --- 3a: tỷ lệ sụt theo rating ---
cal = []
for per in ["ALL", "IS", "OOS"]:
    d = U if per == "ALL" else U[U.period == per]
    for r, z in d.groupby("rating"):
        cal.append(dict(period=per, rating=r, n=len(z), n_waves=z.wave.nunique(), crash_rate=z.crash.mean(),
                        crash_x_rate=z.crash_x.mean(), mean_fwdx_3m=z.fwdx_3m.mean(), median_fwdx_3m=z.fwdx_3m.median(),
                        mean_mdd_3m=z.mdd_3m.mean()))
CAL = pd.DataFrame(cal); CAL.to_csv(f"{OUT}/rating_calibration.csv", index=False)

# within-wave demeaned crash (loại hiệu ứng cú sập chung của cả thị trường)
U["crash_dm"] = U.crash - U.groupby("wave").crash.transform("mean")
dm = U.groupby(["period", "rating"]).crash_dm.mean().unstack(0)

# --- 3b: AUC / Gini / Brier ---
from numpy.linalg import lstsq
def logit_fit(X, y, it=50):
    b = np.zeros(X.shape[1])
    for _ in range(it):
        p = 1 / (1 + np.exp(-X @ b)); W = p * (1 - p)
        b += np.linalg.solve(X.T @ (X * W[:, None]) + 1e-6 * np.eye(X.shape[1]), X.T @ (y - p))
    return b
U["ivol_r"] = U.groupby("wave").idio_vol60.rank(pct=True)
aucs = []
for per in ["ALL", "IS", "OOS"]:
    d = U if per == "ALL" else U[U.period == per]
    for nm, col in (("rating", "rating"), ("idio_vol60_rank", "ivol_r")):
        dd = d.dropna(subset=[col])
        a = auc(dd[col], dd.crash); lo, hi = wave_boot(dd, lambda z: auc(z[col], z.crash))
        aw = dd.groupby("wave").apply(lambda z: auc(z[col], z.crash)).mean()
        aucs.append(dict(period=per, score=nm, target="crash_mdd20", n=len(dd), n_waves=dd.wave.nunique(),
                         auc=a, gini=2 * a - 1, ci_lo=lo, ci_hi=hi, auc_within_wave_mean=aw))
# Brier: xác suất = tỷ lệ crash IS theo rating, áp OOS; so climatology IS & oracle base-rate OOS
IS, OOS = U[U.period == "IS"], U[U.period == "OOS"]
p_r = IS.groupby("rating").crash.mean()
pr_oos = OOS.rating.map(p_r).fillna(IS.crash.mean())
brier = lambda p, y: np.mean((p - y) ** 2)
b_rating = brier(pr_oos, OOS.crash); b_clim = brier(IS.crash.mean(), OOS.crash); b_oracle = brier(OOS.crash.mean(), OOS.crash)
# rating + ivol logistic, fit IS, eval OOS
X = lambda d: np.column_stack([np.ones(len(d)), pd.get_dummies(d.rating).reindex(columns=[2, 3, 4, 5], fill_value=0).values, d.ivol_r.values])
ISv, OOSv = IS.dropna(subset=["ivol_r"]), OOS.dropna(subset=["ivol_r"])
bb = logit_fit(X(ISv).astype(float), ISv.crash.values.astype(float))
p2 = 1 / (1 + np.exp(-X(OOSv).astype(float) @ bb))
a2 = auc(p2, OOSv.crash)
aucs.append(dict(period="OOS", score="logit(rating+ivol) fit IS", target="crash_mdd20", n=len(OOSv), n_waves=OOSv.wave.nunique(),
                 auc=a2, gini=2 * a2 - 1))
BR = dict(brier_rating_IStable_on_OOS=b_rating, brier_climatology_IS=b_clim, brier_oracle_OOSbase=b_oracle,
          BSS_vs_climatology=1 - b_rating / b_clim, BSS_vs_oracle_base=1 - b_rating / b_oracle,
          brier_logit_rating_ivol=brier(p2, OOSv.crash.values), BSS_logit_vs_oracle=1 - brier(p2, OOSv.crash.values) / brier(OOSv.crash.mean(), OOSv.crash.values))
A = pd.DataFrame(aucs); A.to_csv(f"{OUT}/rating_auc.csv", index=False)
pd.Series(BR).to_csv(f"{OUT}/rating_brier.csv", header=["value"])

# --- 3c: ma trận chuyển hạng quý-qua-quý (từ fa_ratings_8l, mọi mã) + trên tập sự kiện universe ---
r8 = pd.read_parquet("/home/trido/thanhdt/WorkingClaude/data/bq_cache/fa_ratings_8l.parquet")
r8["time"] = pd.to_datetime(r8.time); r8 = r8.sort_values(["ticker", "time"])
r8["prev"] = r8.groupby("ticker").rating.shift(1)
tm_all = pd.crosstab(r8.prev.dropna().astype(int), r8.loc[r8.prev.notna(), "rating"], normalize="index")
tm_univ = pd.crosstab(U.rating_prev.dropna().astype(int), U.loc[U.rating_prev.notna(), "rating"], normalize="index")
pd.concat({"all_fa_ratings_8l": tm_all, "universe_events": tm_univ}).to_csv(f"{OUT}/rating_transition.csv")

# --- 3d: outlook (đo, không wire): động lực rating × thay đổi IVOL so sự kiện trước của chính mã ---
U = U.sort_values(["ticker", "rd"])
U["d_rating"] = U.rating - U.rating_prev
U["d_ivol"] = U.groupby("ticker").idio_vol60.diff()
_r = U.groupby("wave").d_ivol.rank(pct=True)   # tercile trong đợt; NaN (sự kiện đầu của mã) giữ NaN
U["d_ivol_t"] = pd.cut(_r, [0, 1/3, 2/3, 1], labels=["ivol_down", "ivol_flat", "ivol_up"], include_lowest=True)
U["rating_mom"] = np.select([U.d_rating < 0, U.d_rating > 0], ["cai_thien", "xau_di"], "on_dinh")
U.loc[U.rating_prev.isna(), "rating_mom"] = np.nan
ol = []
for (per, mom, dv), z in U.dropna(subset=["rating_mom", "d_ivol_t"]).groupby(["period", "rating_mom", "d_ivol_t"]):
    ol.append(dict(period=per, rating_mom=mom, d_ivol=dv, n=len(z), crash_rate=z.crash.mean(),
                   crash_dm=z.crash_dm.mean(), mean_fwdx_3m=z.fwdx_3m.mean(), mean_rating=z.rating.mean()))
# kiểm soát mức rating: chênh crash_dm trong cùng rating rồi lấy trung bình
strat = U.dropna(subset=["rating_mom"]).groupby(["period", "rating", "rating_mom"]).crash_dm.mean().unstack()
OL = pd.DataFrame(ol); OL.to_csv(f"{OUT}/rating_outlook.csv", index=False)
strat.to_csv(f"{OUT}/rating_outlook_stratified.csv")

pd.set_option("display.width", 220)
print(CAL.round(4).to_string(index=False)); print("\nwithin-wave demeaned crash by rating:\n", dm.round(4))
print(A.round(4).to_string(index=False)); print(pd.Series(BR).round(5))
print("\ntransition (all):\n", tm_all.round(3)); print("\ntransition (universe events):\n", tm_univ.round(3))
print(OL.round(4).to_string(index=False)); print("\nstratified crash_dm by rating x momentum:\n", strat.round(4))
print("\ncrash rate by year:", U.groupby("year").crash.mean().round(3).to_dict())
print("share of rows with d_rating!=0:", round((U.d_rating.dropna() != 0).mean(), 3))
