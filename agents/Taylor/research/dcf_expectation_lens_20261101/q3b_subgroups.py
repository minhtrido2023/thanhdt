# -*- coding: utf-8 -*-
"""Q3b — HẬU NGHIỆM (+12 trial): case VCS/MWG/FPT/VNM gợi ý thị trường NỞ bội số cho doanh nghiệp lớn/chất lượng sau chuỗi
tăng trưởng (khác trung bình cắt ngang). Kiểm: (1) streak→PE tự thân & độ co giãn theo nhóm 'lớn+ROE cao' vs còn lại;
(2) sự kiện E1/E2 tách theo PE tự thân lúc sự kiện; (3) trong dòng chuỗi: lợi suất 12T VƯỢT TB cắt ngang theo dấu hiệu."""
import os
import numpy as np
import pandas as pd
from q1_extrap import nw_t, rk

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
P = print
pd.set_option("display.width", 250)


def boot_mean(x, yrs, n=2000, seed=11):
    x = np.asarray(x, float)
    ok = np.isfinite(x)
    x, yrs = x[ok], np.asarray(yrs)[ok]
    u = np.unique(yrs)
    rng = np.random.default_rng(seed)
    bs = [np.mean(np.concatenate([x[yrs == y] for y in rng.choice(u, len(u))])) for _ in range(n)]
    return x.mean(), np.percentile(bs, 2.5), np.percentile(bs, 97.5), len(x)


def main():
    m = pd.read_parquet(os.path.join(HERE, "data", "mpanel.parquet"))
    m = m[m.t >= "2014-01-01"].copy()
    m["sizeq"] = m.groupby("t").tv3.transform(lambda s: pd.qcut(s.rank(method="first"), 3, labels=False))
    m["quality_large"] = (m.sizeq == 2) & (m.ROE5Y >= 0.15)
    st = (m.g1s >= 0.2).astype(float)
    run, alive = st.copy(), st.copy()
    for k in (1, 2, 3, 4):
        alive = alive * (m[f"g1s_l{k}"] >= 0.2).astype(float)
        run = run + alive
    m["streak"] = run.where(m.g1s.notna())
    m["x12"] = m.fwd12 - m.groupby("t").fwd12.transform("mean")
    m["x6"] = m.fwd6 - m.groupby("t").fwd6.transform("mean")
    P(f"tỷ lệ quality_large (tercile thanh khoản cao & ROE5Y≥15%): {m.quality_large.mean():.3f}")
    # (1) streak → PE_own trong từng nhóm (pooled-by-month FM, đơn vị: điểm percentile mỗi quý streak)
    rows = []
    for grp, mm in (("lớn+ROE cao", m.quality_large), ("còn lại", ~m.quality_large)):
        bt = []
        for t, g in m[mm].groupby("t"):
            g = g[["PE_own", "streak", "g1", "gQ2"]].dropna()
            if len(g) < 20:
                continue
            X = np.column_stack([np.ones(len(g)), g.streak, rk(g.g1), rk(g.gQ2)])
            b, *_ = np.linalg.lstsq(X, g.PE_own.values, rcond=None)
            bt.append([t, b[1], b[2]])
        d = pd.DataFrame(bt, columns=["t", "b_streak", "b_g1"])
        for per, w in (("IS", d.t.dt.year <= 2019), ("OOS", d.t.dt.year >= 2020)):
            rows.append({"grp": grp, "per": per, "months": int(w.sum()), "b_streak": d[w].b_streak.mean(),
                         "t_streak": nw_t(d[w].b_streak), "b_g1": d[w].b_g1.mean(), "t_g1": nw_t(d[w].b_g1)})
    P("=== (1) PE tự thân lên streak (mỗi quý streak, điểm percentile) theo nhóm ===")
    P(pd.DataFrame(rows).round(3).to_string(index=False))
    tab = m[m.PE_own.notna() & m.streak.notna()].groupby(["quality_large", "streak"]).agg(
        n=("PE_own", "size"), pe_own_med=("PE_own", "median"), x12=("x12", "mean"), f1=("f1", "median"))
    P(tab.round(3).to_string())
    tab.to_csv(os.path.join(OUT, "q3b_streak_by_group.csv"))

    # (2) sự kiện theo PE tự thân lúc sự kiện
    P("\n=== (2) sự kiện E1/E2: lợi suất vượt đối chứng & ΔlogPE theo PE tự thân lúc sự kiện (CI khối năm) ===")
    rows = []
    for E in ("E1", "E2"):
        d = pd.read_csv(os.path.join(OUT, f"q3_events_{E}.csv"), parse_dates=["time"])
        d["b"] = pd.cut(d.PE_own0, [-1, 33.3, 66.7, 101], labels=["rẻ<33", "giữa", "đắt>67"])
        for b, g in d.groupby("b", observed=True):
            for c in ("x_pre63", "x_r126", "x_r252", "dlogPE12"):
                mu, lo, hi, n = boot_mean(g[c], g.time.dt.year)
                rows.append({"E": E, "PE_own": b, "metric": c, "n": n, "mean": mu, "lo": lo, "hi": hi,
                             "median": g[c].median()})
    ev = pd.DataFrame(rows)
    P(ev.round(3).to_string(index=False))
    ev.to_csv(os.path.join(OUT, "q3b_events_by_peown.csv"), index=False)

    # (3) trong dòng chuỗi (dòng tháng có streak ≥ 4): x12 theo dấu hiệu
    s = m[m.streak >= 4].copy()
    s["sig_accS"] = s.accS < 0
    s["sig_roe"] = s.ROE_Trailing < s[[f"roe_l{k}" for k in (1, 2, 3, 4)]].max(axis=1)
    s["sig_pe67"] = s.PE_own > 66.7
    s["pe67_and_accS"] = s.sig_pe67 & s.sig_accS
    P(f"\n=== (3) dòng tháng streak≥4: n={len(s)} ({s.ticker.nunique()} mã); x12 = fwd12 − TB cắt ngang ===")
    rows = []
    for c in ("sig_accS", "sig_roe", "sig_pe67", "pe67_and_accS"):
        for flag in (True, False):
            g = s[s[c] == flag]
            mu, lo, hi, n = boot_mean(g.x12, g.t.dt.year)
            rows.append({"signal": c, "on": flag, "n": n, "x12": mu, "lo": lo, "hi": hi,
                         "x12_IS": g[g.t.dt.year <= 2019].x12.mean(), "x12_OOS": g[g.t.dt.year >= 2020].x12.mean()})
    mu, lo, hi, n = boot_mean(s.x12, s.t.dt.year)
    rows.append({"signal": "ALL streak≥4", "on": True, "n": n, "x12": mu, "lo": lo, "hi": hi,
                 "x12_IS": s[s.t.dt.year <= 2019].x12.mean(), "x12_OOS": s[s.t.dt.year >= 2020].x12.mean()})
    r3 = pd.DataFrame(rows)
    P(r3.round(4).to_string(index=False))
    r3.to_csv(os.path.join(OUT, "q3b_streak_signals_x12.csv"), index=False)


if __name__ == "__main__":
    main()
