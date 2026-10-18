#!/usr/bin/env python3
"""Việc (2) — giá trị TĂNG THÊM so với 8L: IC theo đợt sau trực giao hoá với rating 8L PIT.
Theo prereg.md (khoá trước khi chạy file này). threads=1, seed cố định.
Output: ic_results.csv, ic_by_wave.csv, ic_loyo.csv, composite.csv, events_features_fp.csv
"""
import os, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
OUT = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(20261016)

ev = pd.read_csv(f"{OUT}/events_features.csv.gz", parse_dates=["rd", "qend", "t_s"])
ev["monday"] = (ev.rd.dt.dayofweek == 0).astype(int)
ev["vol_ratio_log"] = np.log(ev.vol_ratio.clip(lower=1e-3))
for c in ["ins_netbuy_adv", "accr_q"]:
    lo, hi = ev[c].quantile([0.005, 0.995]); ev[c] = ev[c].clip(lo, hi)

# ---------- Empirical-Bayes fingerprint (PIT) ----------
# Mỗi mã chỉ ~4 sự kiện/năm ⇒ CẤM ước lượng riêng thuần. fp = M_g + w(m_k − M_g), w = τ²/(τ² + σ²/n_k)
# m_k, n_k: trung bình các sự kiện TRƯỚC của chính mã (shift 1). M_g, σ², τ²: từ mọi sự kiện của ngành g
# có rd < 01/01 năm sự kiện (expanding theo năm) ⇒ không nhìn tương lai.
FP_SRC = {"fp_lag_dev": "lag_dev", "fp_leak": "leak_ratio", "fp_car": "car_m1p1",
          "fp_volr": "vol_ratio_log", "fp_ins": "ins_netbuy_adv"}
ev = ev.sort_values(["ticker", "rd"]).reset_index(drop=True)
for fp, src in FP_SRC.items():
    x = ev[src]
    g = ev.assign(_x=x, _c=x.notna().astype(int)).groupby("ticker")
    csum = g["_x"].transform(lambda s: s.fillna(0).cumsum().shift(1).fillna(0))
    cnt = g["_c"].transform(lambda s: s.cumsum().shift(1).fillna(0))
    mk = csum / cnt.where(cnt > 0)
    out = pd.Series(np.nan, index=ev.index)
    for Y in range(2015, ev.year.max() + 1):
        hist = ev[(ev.rd < f"{Y}-01-01") & x.notna()]
        cur = ev.year == Y
        for sec, h in hist.groupby("sector1"):
            tm = h.groupby("ticker")[src].agg(["mean", "var", "count"])
            tm = tm[tm["count"] >= 2]
            if len(tm) < 5: continue
            M = h[src].mean(); s2 = np.nanmean(tm["var"])
            tau2 = max(tm["mean"].var() - np.mean(s2 / tm["count"]), 1e-12)
            idx = cur & (ev.sector1 == sec)
            n = cnt[idx]; w = tau2 / (tau2 + s2 / n.where(n > 0))
            out[idx] = np.where(n > 0, M + w * (mk[idx] - M), M)
    ev[fp] = out
ev.to_csv(f"{OUT}/events_features_fp.csv.gz", index=False)

FEATS = {  # name: expected sign (0 = hai phía)
    "lag_dev": -1, "monday": -1, "late30": -1, "near_deadline": -1, "car_m1p1": +1, "car_m5m1": 0,
    "leak_ratio": -1, "vol_ratio_log": +1, "amihud_log": +1, "idio_vol60": -1, "limit_freq60": -1,
    "ins_netbuy_adv": +1, "ins_breadth": +1, "accr_q": -1,
    "fp_lag_dev": 0, "fp_leak": 0, "fp_car": 0, "fp_volr": 0, "fp_ins": 0}
HOR = ["fwdx_1m", "fwdx_3m"]

U = ev[ev.in_universe & ev.rating.notna()].copy()
U["rating"] = U.rating.astype(int)

def resid_rank(df, f):
    """rank trong đợt → phần dư sau hồi quy lên dummy rating (= trừ trung bình rank theo rating trong đợt)."""
    r = df.groupby("wave")[f].rank(pct=True)
    return r - r.groupby([df.wave, df.rating]).transform("mean")

def wave_ic(df, xcol, ycol):
    d = df[["wave", "year", "ticker", xcol, ycol]].dropna()
    d = d[d.groupby("wave")[xcol].transform("count") >= 30]
    d["yr"] = d.groupby("wave")[ycol].rank(pct=True)
    d["xr"] = d[xcol]
    ic = d.groupby("wave").apply(lambda z: z.xr.corr(z.yr, method="spearman"))
    yr = d.groupby("wave").year.agg(lambda s: s.mode().iloc[0])
    return ic, yr, d

def tstat(s):
    s = s.dropna(); return s.mean() / s.std(ddof=1) * np.sqrt(len(s)) if len(s) > 2 else np.nan

def boot_ticker(d, B=1000):
    """IC gộp (corr của rank-dư và rank fwd trong đợt, đã demean) — block bootstrap theo ticker."""
    x = d.xr - d.groupby("wave").xr.transform("mean"); y = d.yr - d.groupby("wave").yr.transform("mean")
    agg = pd.DataFrame({"xy": x * y, "xx": x * x, "yy": y * y, "t": d.ticker}).groupby("t").sum()
    A = agg.values; k = len(A)
    pooled = A[:, 0].sum() / np.sqrt(A[:, 1].sum() * A[:, 2].sum())
    bs = []
    for _ in range(B):
        c = rng.multinomial(k, np.ones(k) / k)
        s = c @ A; bs.append(s[0] / np.sqrt(s[1] * s[2]))
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return pooled, lo, hi

def qspread(d, ycol_raw, df):
    dd = d.copy()   # d đã chứa cột fwd thô
    dd["q"] = dd.groupby("wave").xr.transform(lambda s: pd.qcut(s.rank(method="first"), 5, labels=False))
    sp = dd.groupby("wave").apply(lambda z: z.loc[z.q == 4, ycol_raw].mean() - z.loc[z.q == 0, ycol_raw].mean())
    return sp

res, byw, loyo = [], [], []
for f, sgn in FEATS.items():
    U[f"_r_{f}"] = resid_rank(U, f)
    U[f"_raw_{f}"] = U.groupby("wave")[f].rank(pct=True)
    for h in HOR:
        ic, yr, d = wave_ic(U, f"_r_{f}", h)
        icraw, _, _ = wave_ic(U, f"_raw_{f}", h)
        if len(ic) < 10: continue
        IS, OOS = ic[yr < 2020], ic[yr >= 2020]
        pooled, lo, hi = boot_ticker(d)
        sp = qspread(d, h, U)
        ly = {Y: ic[yr != Y].mean() for Y in sorted(yr.unique())}
        flips = sum(np.sign(v) != np.sign(ic.mean()) for v in ly.values())
        hit = (np.sign(ic) == (np.sign(ic.mean()) if sgn == 0 else sgn)).mean()
        t_all = tstat(ic); t_is = tstat(IS); t_oos = tstat(OOS)
        sign_ok = (sgn == 0) or (np.sign(ic.mean()) == sgn)
        if abs(t_all) >= 3 and np.sign(IS.mean()) == np.sign(OOS.mean()) and abs(t_oos) >= 2 and flips == 0 \
                and (lo > 0 or hi < 0) and sign_ok:
            verdict = "GO"
        elif (abs(t_all) >= 2 and np.sign(IS.mean()) == np.sign(OOS.mean())) or (abs(t_all) >= 3 and not sign_ok):
            verdict = "INCONCLUSIVE"
        else:
            verdict = "NO-GO"
        res.append(dict(feature=f, horizon=h, exp_sign=sgn, n_events=len(d), n_tickers=d.ticker.nunique(),
                        n_waves=len(ic), ic_raw=icraw.mean(), t_raw=tstat(icraw), ic_orth=ic.mean(), t_wave=t_all,
                        hit=hit, ic_IS=IS.mean(), t_IS=t_is, n_IS=len(IS), ic_OOS=OOS.mean(), t_OOS=t_oos,
                        n_OOS=len(OOS), pooled_ic=pooled, boot_lo=lo, boot_hi=hi, loyo_min=min(ly.values()),
                        loyo_max=max(ly.values()), loyo_flips=flips, q5q1_bps=sp.mean() * 1e4,
                        q5q1_t=tstat(sp), verdict=verdict))
        for w, v in ic.items(): byw.append(dict(feature=f, horizon=h, wave=w, year=yr[w], ic=v))
        for Y, v in ly.items(): loyo.append(dict(feature=f, horizon=h, left_out=Y, mean_ic=v))

R = pd.DataFrame(res)
R.to_csv(f"{OUT}/ic_results.csv", index=False)
pd.DataFrame(byw).to_csv(f"{OUT}/ic_by_wave.csv", index=False)
pd.DataFrame(loyo).to_csv(f"{OUT}/ic_loyo.csv", index=False)

# ---------- Composite: chọn trên IS, chấm OOS 1 lần ----------
comp = []
for h in HOR:
    sel = R[(R.horizon == h) & (R.t_IS.abs() >= 2)]
    if sel.empty:
        comp.append(dict(horizon=h, members="(none |t_IS|>=2)")); continue
    U["_comp"] = sum(np.sign(r.ic_IS) * U[f"_r_{r.feature}"].fillna(0) for r in sel.itertuples()) / len(sel)
    U["_comp_r"] = resid_rank(U, "_comp")
    ic, yr, d = wave_ic(U, "_comp_r", h)
    IS, OOS = ic[yr < 2020], ic[yr >= 2020]
    pooled, lo, hi = boot_ticker(d)
    comp.append(dict(horizon=h, members=";".join(f"{r.feature}({'+' if r.ic_IS > 0 else '-'})" for r in sel.itertuples()),
                     n_members=len(sel), ic_IS=IS.mean(), t_IS=tstat(IS), ic_OOS=OOS.mean(), t_OOS=tstat(OOS),
                     n_OOS=len(OOS), pooled=pooled, boot_lo=lo, boot_hi=hi, q5q1_OOS_bps=qspread(d, h, U)[yr >= 2020].mean() * 1e4))
pd.DataFrame(comp).to_csv(f"{OUT}/composite.csv", index=False)

pd.set_option("display.width", 250)
cols = ["feature", "horizon", "n_events", "n_waves", "ic_raw", "ic_orth", "t_wave", "hit", "ic_IS", "t_IS", "ic_OOS",
        "t_OOS", "boot_lo", "boot_hi", "loyo_flips", "q5q1_bps", "q5q1_t", "verdict"]
print(R[cols].round(4).to_string(index=False))
print(pd.DataFrame(comp).round(4).to_string(index=False))
