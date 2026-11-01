# -*- coding: utf-8 -*-
"""Q2 — "DCF nhẹ": tường minh 1/2/3 năm theo tăng trưởng gần rồi rơi về g_T 4,5%; so S0 (đề xuất bài trước) và CUR (engine).
Tiêu chí: (i) giải thích giá (var cắt ngang log P/FV), (ii) sai số dự báo NP 1-2 năm, (iii) IC MoS 3/6/12T. PREREG §2 Q2."""
import os
import sys
import numpy as np
import pandas as pd
from scipy.stats import norm, skew, kurtosis

HERE = os.path.dirname(os.path.abspath(__file__))
PRIOR = os.path.join(HERE, "..", "dcf_vn_calibration_20261101")
OUT = os.path.join(HERE, "out")
sys.path.insert(0, PRIOR)
_cwd = os.getcwd()
import engine as E  # noqa: E402  (engine chdir về PRIOR)
os.chdir(_cwd)
from common import ic_by_date, ic_summary  # noqa: E402

P = print
pd.set_option("display.width", 250)
R = E.R_CONST
GT = 0.045
CLIP = (-0.30, 0.50)


def h(g, N):
    """Bội số FV/base cho đường: g trong N năm, sau đó g_T. N=0 ⇒ Gordon thuần ở g_T."""
    g = np.asarray(g, float)
    pv = np.zeros_like(g)
    f = np.ones_like(g)
    for y in range(N):
        f = f * (1 + g)
        pv += f / (1 + R) ** (y + 1)
    return pv + f * (1 + GT) / (R - GT) / (1 + R) ** N


def wvar(x):
    x = pd.Series(x).dropna()
    if len(x) < 30:
        return np.nan
    lo, hi = x.quantile(0.01), x.quantile(0.99)
    return x.clip(lo, hi).var()


def main():
    p = pd.read_parquet(os.path.join(HERE, "data", "mpanel.parquet"))
    p = p[p.t >= "2014-01-01"].copy()
    m, base = E.base_valid(p)
    p = p[m & p.Price.notna() & (p.Price > 0)].copy()
    p["base"] = base[p.index].values
    fv_cur, gexp = E.current_fv(p)
    p["gexp_cur"] = gexp
    bps = p.base.values / p.OShares.values
    V = {"S0": bps * h(np.zeros(len(p)), 0), "CUR": fv_cur}
    gsrc = {"g1": p.g1s.clip(*CLIP).fillna(GT).values, "gQ2": p.gQ2s.clip(*CLIP).fillna(GT).values}
    for N in (1, 2, 3):
        for k, g in gsrc.items():
            V[f"L{N}_{k}"] = bps * h(g, N)
    for k, v in V.items():
        p[f"mos_{k}"] = np.log(v / p.Price.values)
    # cơ sở E (chỉ hạng/độ phân tán): log(FV_E/P) = −log PE + log h(g,N) + hằng
    pe_ok = (p.PE > 0) & (p.PE < 200)
    p["mos_EP"] = np.where(pe_ok, -np.log(p.PE), np.nan)
    p["mos_L2E_g1"] = np.where(pe_ok, -np.log(p.PE) + np.log(h(gsrc["g1"], 2)), np.nan)
    p["mos_PEGY"] = np.where(pe_ok & p.g1s.notna(), p.g1s.clip(*CLIP) / p.PE, np.nan)
    names = list(V) + ["EP", "L2E_g1", "PEGY"]
    p.to_parquet(os.path.join(HERE, "data", "q2_variants.parquet"))

    # (i) giải thích giá
    P("=== (i) R²_rel = 1 − var(log P/FV_v)/var(log P/FV_S0) cắt ngang, cùng mẫu, winsor 1% (TB theo tháng) ===")
    rows = []
    for t, g in p.groupby("t"):
        vS = wvar(g.mos_S0)
        vE = wvar(g.mos_EP)
        rec = {"t": t}
        for k in V:
            rec[k] = 1 - wvar(g[f"mos_{k}"]) / vS
        rec["L2E_g1|vsEP"] = 1 - wvar(g.mos_L2E_g1) / vE
        rows.append(rec)
    d = pd.DataFrame(rows)
    s = pd.DataFrame({"IS": d[d.t.dt.year <= 2019].drop(columns="t").mean(),
                      "OOS": d[d.t.dt.year >= 2020].drop(columns="t").mean()})
    P(s.round(3).to_string())
    s.to_csv(os.path.join(OUT, "q2_i_r2rel.csv"))

    # (ii) sai số dự báo NP 1-2 năm (dòng quý duy nhất)
    q = p.sort_values("t").drop_duplicates(["ticker", "qtime"], keep="first").copy()
    q = q[q.TTM0 > 0]
    P("\n=== (ii) dự báo TTM NP sau 1 năm / 2 năm: trung vị |log(thật/dự)| (bias = trung vị log(thật/dự)); cặp dương ===")
    preds = {"g=0": (np.zeros(len(q)), 0), "S0 (g_T 4,5%)": (np.full(len(q), GT), 9),
             "CUR (gexp engine 5 năm)": (q.gexp_cur.values, 5)}
    for N in (1, 2, 3):
        for k in ("g1", "gQ2"):
            col = "g1s" if k == "g1" else "gQ2s"
            preds[f"L{N}_{k}"] = (q[col].clip(*CLIP).fillna(GT).values, N)
    rows = []
    for name, (g, N) in preds.items():
        rec = {"model": name}
        for yrs, col in ((1, "TTMf1"), (2, "TTMf2")):
            path = np.ones(len(q))
            for y in range(yrs):
                gy = g if y < N else np.full(len(q), GT)
                if name == "g=0":
                    gy = np.zeros(len(q))
                path = path * (1 + gy)
            pred = q.TTM0.values * path
            real = q[col].values
            ok = (real > 0) & np.isfinite(pred) & (pred > 0)
            e = np.log(real[ok] / pred[ok])
            yr = q.t.dt.year.values[ok]
            rec[f"MAE{yrs}"] = np.median(np.abs(e))
            rec[f"MAE{yrs}_IS"] = np.median(np.abs(e[yr <= 2019]))
            rec[f"MAE{yrs}_OOS"] = np.median(np.abs(e[yr >= 2020]))
            rec[f"bias{yrs}"] = np.median(e)
            rec[f"n{yrs}"] = int(ok.sum())
            rec[f"neg{yrs}"] = float(np.mean(q[col].values[np.isfinite(q[col].values)] <= 0))
        rows.append(rec)
    e2 = pd.DataFrame(rows)
    P(e2.round(3).to_string(index=False))
    e2.to_csv(os.path.join(OUT, "q2_ii_forecast.csv"), index=False)

    # (iii) IC
    P("\n=== (iii) IC hạng MoS vs lợi suất kỳ hạn (CI bootstrap khối năm) ===")
    ics = {}
    rows = []
    for k in names:
        for hh in (3, 6, 12):
            ic = ic_by_date(p, f"mos_{k}", f"fwd{hh}")
            sm = ic_summary(ic, hh)
            ics[(k, hh)] = ic
            rows.append({"var": k, "h": hh, **{a: sm.get(a) for a in ("ic", "ci_lo", "ci_hi", "ic_is", "ic_oos", "t_nw", "n_dates")}})
    icd = pd.DataFrame(rows)
    P(icd.round(4).to_string(index=False))
    icd.to_csv(os.path.join(OUT, "q2_iii_ic.csv"), index=False)
    # chênh IC12 vs S0 cùng ngày, CI khối năm
    P("\n=== ΔIC vs S0 (cùng tháng), CI khối năm ===")
    rng = np.random.default_rng(7)
    rows = []
    for k in names:
        for hh in (3, 12):
            a = ics[(k, hh)].set_index("t").ic
            b = ics[("S0", hh)].set_index("t").ic
            dlt = (a - b).dropna()
            yrs = sorted(set(dlt.index.year))
            bs = [np.mean(np.concatenate([dlt[dlt.index.year == y].values for y in rng.choice(yrs, len(yrs))]))
                  for _ in range(2000)]
            rows.append({"var": k, "h": hh, "dIC": dlt.mean(), "lo": np.percentile(bs, 2.5), "hi": np.percentile(bs, 97.5),
                         "dIC_IS": dlt[dlt.index.year <= 2019].mean(), "dIC_OOS": dlt[dlt.index.year >= 2020].mean()})
            if k != "S0":
                do = dlt[dlt.index.year >= 2020]
                yo = sorted(set(do.index.year))
                bso = [np.mean(np.concatenate([do[do.index.year == y].values for y in rng.choice(yo, len(yo))]))
                       for _ in range(2000)]
                rows[-1]["lo_OOS"], rows[-1]["hi_OOS"] = np.percentile(bso, 2.5), np.percentile(bso, 97.5)
    dd = pd.DataFrame(rows)
    P(dd.round(4).to_string(index=False))
    dd.to_csv(os.path.join(OUT, "q2_iii_dic.csv"), index=False)
    # ngũ phân vị (phân phối)
    P("\n=== ngũ phân vị MoS → lợi suất 12T trung bình (TB theo tháng) & tỷ lệ thắng VNINDEX-agnostic (>TB cắt ngang) ===")
    rows = []
    for k in ("S0", "CUR", "L2_g1", "L1_gQ2", "EP", "L2E_g1"):
        acc = []
        for t, g in p.groupby("t"):
            g = g[[f"mos_{k}", "fwd12"]].dropna()
            if len(g) < 50:
                continue
            qn = pd.qcut(g[f"mos_{k}"].rank(method="first"), 5, labels=False)
            mu = g.fwd12.mean()
            acc.append([t] + [g.fwd12[qn == i].mean() - mu for i in range(5)] +
                       [(g.fwd12[qn == 4] > g.fwd12.median()).mean()])
        a = pd.DataFrame(acc, columns=["t", "Q1", "Q2", "Q3", "Q4", "Q5", "hitQ5"])
        for per, mm in (("IS", a.t.dt.year <= 2019), ("OOS", a.t.dt.year >= 2020)):
            rows.append({"var": k, "per": per, **a[mm].drop(columns="t").mean().to_dict()})
    qq = pd.DataFrame(rows)
    P(qq.round(4).to_string(index=False))
    qq.to_csv(os.path.join(OUT, "q2_iii_quintiles.csv"), index=False)
    # DSR IC12 (tháng 12 mỗi năm), N trials = 30 khai PREREG (+3 biến thể E-base hậu nghiệm)
    srs = {}
    for k in names:
        x = ics[(k, 12)].set_index("t").ic
        x = x[x.index.month == 12].dropna()
        srs[k] = x
    allsr = [x.mean() / x.std(ddof=1) for x in srs.values()]
    Nn = 30
    emc = 0.5772156649
    sr0 = np.sqrt(np.var(allsr, ddof=1)) * ((1 - emc) * norm.ppf(1 - 1 / Nn) + emc * norm.ppf(1 - 1 / (Nn * np.e)))
    P(f"\n=== DSR IC12 (tháng 12/năm), N=30, SR0={sr0:.3f} ===")
    for k, x in srs.items():
        sr = x.mean() / x.std(ddof=1)
        sk, ku = skew(x), kurtosis(x, fisher=False)
        z = (sr - sr0) * np.sqrt(len(x) - 1) / np.sqrt(max(1 - sk * sr + (ku - 1) / 4 * sr ** 2, 1e-9))
        P(f"  {k:8s} T={len(x)} SR={sr:.3f} DSR={norm.cdf(z):.3f}")


if __name__ == "__main__":
    main()
