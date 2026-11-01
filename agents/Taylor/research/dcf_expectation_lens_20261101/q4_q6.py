# -*- coding: utf-8 -*-
"""Q4 — lưới 3×3 (gia tốc × PE tự thân) + Fama-MacBeth; Q6 — trực giao hoá với yield/SUE/NP_R/momentum. PREREG §2 Q4, Q6."""
import os
import sys
import numpy as np
import pandas as pd
from q1_extrap import nw_t, rk

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
sys.path.insert(0, os.path.join(HERE, "..", "dcf_vn_calibration_20261101"))
from common import ic_by_date, ic_summary  # noqa: E402

P = print
pd.set_option("display.width", 250)


def boot_ci(s, alpha=0.05, n=4000, seed=5):
    s = s.dropna()
    yrs = s.index.year
    u = np.unique(yrs)
    rng = np.random.default_rng(seed)
    bs = [np.mean(np.concatenate([s.values[yrs == y] for y in rng.choice(u, len(u))])) for _ in range(n)]
    return np.percentile(bs, 100 * alpha / 2), np.percentile(bs, 100 * (1 - alpha / 2))


def q4(m):
    m = m[m.t >= "2014-01-01"].copy()
    d = m[m.acc.notna() & m.PE_own.notna()].copy()
    d["G"] = d.groupby("t").acc.transform(lambda s: pd.qcut(s.rank(method="first"), 3, labels=["gt_am", "on_dinh", "gt_duong"]))
    d["V"] = pd.cut(d.PE_own, [-1, 33.3, 66.7, 101], labels=["re", "trung", "dat"])
    P(f"Q4 mẫu: {len(d)} dòng tháng, {d.ticker.nunique()} mã, {d.t.nunique()} tháng")
    rows = []
    for h in (3, 6, 12):
        d[f"x{h}"] = d[f"fwd{h}"] - d.groupby("t")[f"fwd{h}"].transform("mean")
        cm = d.groupby(["t", "G", "V"], observed=True)[f"x{h}"].mean().unstack(["G", "V"])
        for col in cm.columns:
            s = cm[col]
            lo, hi = boot_ci(s)
            blo, bhi = boot_ci(s, alpha=0.05 / 27)
            rows.append({"h": h, "G": col[0], "V": col[1], "mean": s.mean(), "lo95": lo, "hi95": hi,
                         "lo_bonf": blo, "hi_bonf": bhi, "IS": s[s.index.year <= 2019].mean(),
                         "OOS": s[s.index.year >= 2020].mean(), "n_avg": d[(d.G == col[0]) & (d.V == col[1])].groupby("t").size().mean()})
    g = pd.DataFrame(rows).sort_values(["h", "G", "V"])
    P("=== Q4 lưới 3×3: lợi suất vượt TB cắt ngang (TB các tháng), CI khối năm 95% và Bonferroni 27 ===")
    P(g.round(4).to_string(index=False))
    g.to_csv(os.path.join(OUT, "q4_grid.csv"), index=False)
    # Fama-MacBeth
    xs = ["pe_own", "ep", "mom", "sue", "npr", "acc", "pe_x_acc"]
    d["ep"] = np.where(d.PE > 0, 1 / d.PE, np.nan)
    rows = []
    for h in (3, 12):
        bt = []
        for t, gg in d.groupby("t"):
            gg = gg[["PE_own", "ep", "mom", "sue", "NP_R", "acc", f"x{h}"]].dropna()
            if len(gg) < 60:
                continue
            Z = {"pe_own": rk(gg.PE_own), "ep": rk(gg.ep), "mom": rk(gg.mom), "sue": rk(gg.sue), "npr": rk(gg.NP_R),
                 "acc": rk(gg.acc)}
            Z["pe_x_acc"] = Z["pe_own"] * Z["acc"] * 4
            X = np.column_stack([np.ones(len(gg))] + [Z[x].values for x in xs])
            y = rk(gg[f"x{h}"]).values
            b, *_ = np.linalg.lstsq(X, y, rcond=None)
            bt.append([t] + list(b[1:]))
        bd = pd.DataFrame(bt, columns=["t"] + xs)
        for per, w in (("ALL", slice(None)), ("IS", bd.t.dt.year <= 2019), ("OOS", bd.t.dt.year >= 2020)):
            dd = bd[w]
            rows.append({"h": h, "per": per, "months": len(dd), **{f"{x}": dd[x].mean() for x in xs},
                         **{f"t_{x}": nw_t(dd[x], L=max(h - 1, 1)) for x in xs}})
    f = pd.DataFrame(rows)
    P("\n=== Q4 Fama-MacBeth: hạng lợi suất vượt lên hạng biến (hệ số ~ chênh hạng top−bottom), t NW ===")
    P(f.round(3).to_string(index=False))
    f.to_csv(os.path.join(OUT, "q4_fm.csv"), index=False)


def q6():
    p = pd.read_parquet(os.path.join(HERE, "data", "q2_variants.parquet"))
    p["ep"] = np.where((p.PE > 0) & (p.PE < 200), 1 / p.PE, np.nan)
    ctrl = ["ep", "mos_S0", "sue", "NP_R", "mom"]
    tests = ["mos_CUR", "mos_L1_gQ2", "mos_L2_gQ2", "mos_L3_gQ2", "mos_L2_g1", "acc", "accS", "gQ2", "PE_own"]
    res = []
    resid = {k: np.full(len(p), np.nan) for k in tests}
    for t, idx in p.groupby("t").groups.items():
        g = p.loc[idx, ctrl + tests]
        okc = g[ctrl].notna().all(axis=1)
        for k in tests:
            ok = okc & g[k].notna()
            if ok.sum() < 60:
                continue
            X = np.column_stack([np.ones(ok.sum())] + [rk(g.loc[ok, c]).values for c in ctrl])
            y = rk(g.loc[ok, k]).values
            b, *_ = np.linalg.lstsq(X, y, rcond=None)
            pos = p.index.get_indexer(g.index[ok])
            resid[k][pos] = y - X @ b
    for k in tests:
        p[f"res_{k}"] = resid[k]
    # IC raw (cùng mẫu có đủ control) vs residual
    full = p[ctrl].notna().all(axis=1)
    for k in tests:
        for h in (3, 6, 12):
            raw = ic_summary(ic_by_date(p[full & p[k].notna()], k, f"fwd{h}"), h)
            rr = ic_summary(ic_by_date(p, f"res_{k}", f"fwd{h}"), h)
            res.append({"var": k, "h": h, "IC_raw": raw.get("ic"), "raw_OOS": raw.get("ic_oos"), "IC_resid": rr.get("ic"),
                        "resid_lo": rr.get("ci_lo"), "resid_hi": rr.get("ci_hi"), "resid_IS": rr.get("ic_is"),
                        "resid_OOS": rr.get("ic_oos")})
    r = pd.DataFrame(res)
    P("\n=== Q6 IC trước/sau trực giao hoá với {EP, FCFE yield (S0), SUE, NP_R, mom12-1} (hạng cắt ngang) ===")
    P(r.round(4).to_string(index=False))
    r.to_csv(os.path.join(OUT, "q6_orth.csv"), index=False)
    # IC của chính các control (để biết LAG/yield đã bắt bao nhiêu)
    rows = []
    for k in ctrl:
        for h in (3, 12):
            s = ic_summary(ic_by_date(p[full], k, f"fwd{h}"), h)
            rows.append({"ctrl": k, "h": h, "ic": s.get("ic"), "is": s.get("ic_is"), "oos": s.get("ic_oos"),
                         "lo": s.get("ci_lo"), "hi": s.get("ci_hi")})
    P(pd.DataFrame(rows).round(4).to_string(index=False))


if __name__ == "__main__":
    m = pd.read_parquet(os.path.join(HERE, "data", "mpanel.parquet"))
    q4(m)
    q6()
