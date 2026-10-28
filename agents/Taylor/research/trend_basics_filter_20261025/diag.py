"""Chẩn đoán HẬU KIỂM (không thuộc PREREG) cho ô đạt LAG×up60: flat-day, ADV, PIT tertile, LOO năm.
Chạy: $DNA_PYEXE diag.py → diag.txt"""
import glob, os, sys
import numpy as np, pandas as pd
sys.argv = ["x"]
OUT = os.path.dirname(os.path.abspath(__file__))
exec(open(f"{OUT}/analyze.py").read().split("# ---------------------------------------------------------------- thống kê")[0])
exec("\n".join([l for l in open(f"{OUT}/analyze.py").read().split("# ---------------------------------------------------------------- thống kê")[1].split("P0, P1 = load")[0].splitlines()]))
FE = f"{R0}/lag_bal_discriminators_20261025/features{{}}.csv"


def extra(gp):
    gp = gp.reset_index(drop=True)
    c = gp.Close.astype(float); pc = c.shift(1)
    ok = pc.notna()
    return pd.DataFrame({"time": gp.time, "ticker": gp.ticker,
                         "flat60": (c == pc).astype(float).where(ok).rolling(60).mean(),
                         "dn60": (c < pc).astype(float).where(ok).rolling(60).mean(),
                         "ret60": c / c.shift(60) - 1})
EX = pd.concat([extra(g) for _, g in raw.groupby("ticker", sort=False)], ignore_index=True).sort_values("time")
out = []
for tag in ["", "_pin1M"]:
    P = pd.read_csv(f"{OUT}/trend{tag}.csv", parse_dates=["entry_date", "signal_date", "ind_date"])
    P = P.merge(pd.read_csv(FE.format(tag))[["holding_id", "adv"]], on="holding_id")
    P["ind_date"] = P.ind_date.astype("datetime64[ns]")
    P = pd.merge_asof(P.sort_values("ind_date"), EX.rename(columns={"time": "ind_date"}), on="ind_date", by="ticker").sort_values(["book", "entry_date", "holding_id"])
    P["upnf"] = P.up60 / (P.up60 + P.dn60)  # tỉ lệ tăng TRONG các phiên có đổi giá
    s = P[(P.book == "LAG") & P.up60.notna()].reset_index(drop=True)
    pr = s.up60.rank(pct=True); hi, lo = (pr > 2 / 3).values, (pr <= 1 / 3).values
    out.append(f"== {tag or 'pin0'} LAG N={len(s)}")
    out.append("spearman up60 vs flat60={:.3f} dn60={:.3f} adv={:.3f} ret60={:.3f} rs60={:.3f} ey={:.3f}".format(
        *[s.up60.corr(s[k], method="spearman") for k in ["flat60", "dn60", "adv", "ret60", "rs60", "ey"]]))
    out.append(f"T1/T3 median flat60={s.flat60[lo].median():.3f}/{s.flat60[hi].median():.3f} ; dn60={s.dn60[lo].median():.3f}/{s.dn60[hi].median():.3f} ; adv={s.adv[lo].median():.2f}/{s.adv[hi].median():.2f}")
    for nm in ["upnf", "dn60", "flat60", "adv"]:
        t = s[s[nm].notna()]; prr = t[nm].rank(pct=True); h, l_ = (prr > 2 / 3).values, (prr <= 1 / 3).values
        p, _ = boot_d(t, h, l_, "qtr")
        out.append(f"tertile {nm}: d(T3-T1)={dmean(t, h, l_):+.4f} p_q={p:.4f} N={len(t)}")
    # hồi quy đa biến ret ~ 1 + pr(up60) + pr(flat60) + pr(adv) + pr_ey  — hệ số up60, p cụm quý
    t = s.dropna(subset=["flat60", "adv", "ey_pr"]) if "ey_pr" in s else None
    t = s.dropna(subset=["flat60", "adv", "ey"]).copy()
    t["ey_pr"] = t.groupby("G").ey.rank(pct=True)
    X = np.column_stack([np.ones(len(t))] + [t[k].rank(pct=True).values for k in ["up60", "flat60", "adv"]] + [t.ey_pr.values]); y = t.ret.values
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    um, inv = np.unique(t.qtr.values, return_inverse=True); k = X.shape[1]
    XX = np.zeros((len(um), k, k)); XY = np.zeros((len(um), k))
    np.add.at(XX, inv, np.einsum("ni,nj->nij", X, X)); np.add.at(XY, inv, X * y[:, None])
    idx = np.random.default_rng(SEED).integers(0, len(um), (B, len(um)))
    bb = np.linalg.solve(XX[idx].sum(1), XY[idx].sum(1)[..., None])[:, :, 0]
    out.append("reg ret~up60+flat60+adv+ey (pct): " + " ".join(f"{n}={b[i]:+.4f}(p={pval(bb[:, i]):.4f})" for i, n in enumerate(["c", "up60", "flat60", "adv", "ey"], 0) if i))
    # trong nhóm flat60 thấp (mã thanh khoản ~ không có phiên đứng giá nhiều)
    for nm, m in [("flat60<=median", s.flat60 <= s.flat60.median()), ("flat60>median", s.flat60 > s.flat60.median())]:
        t = s[m.values]; prr = t.up60.rank(pct=True); h, l_ = (prr > 2 / 3).values, (prr <= 1 / 3).values
        out.append(f"up60 trong {nm}: d={dmean(t, h, l_):+.4f} p_q={boot_d(t, h, l_, 'qtr')[0]:.4f} N={len(t)}")
    # PIT tertile: cutoff từ vị thế LAG đã entry trước (≥60)
    s2 = s.sort_values(["entry_date", "holding_id"]).reset_index(drop=True)
    T = []
    for i, r in s2.iterrows():
        prev = s2.up60[s2.entry_date < r.entry_date]
        if len(prev) < 60:
            T.append(np.nan); continue
        a, b_ = prev.quantile(1 / 3), prev.quantile(2 / 3)
        T.append(3 if r.up60 > b_ else (1 if r.up60 <= a else 2))
    s2["Tp"] = T
    h, l_ = (s2.Tp == 3).values, (s2.Tp == 1).values
    out.append(f"PIT tertile: N_T3={h.sum()} N_T1={l_.sum()} ret={s2.ret[h].mean():.4f}/{s2.ret[l_].mean():.4f} d={dmean(s2, h, l_):+.4f} p_q={boot_d(s2, h, l_, 'qtr')[0]:.4f}")
    # LOO năm + từng năm
    yrs = []
    for yv in sorted(s.year.unique()):
        t = s[s.year != yv]; prr = t.up60.rank(pct=True)
        yrs.append(f"{yv}:{dmean(t, (prr > 2 / 3).values, (prr <= 1 / 3).values):+.3f}")
    out.append("LOO drop-year d: " + " ".join(yrs))
    py = []
    for yv, t in s.groupby("year"):
        h, l_ = hi[s.year.values == yv], lo[s.year.values == yv]
        py.append(f"{yv}:{dmean(t, h, l_):+.3f}(n{h.sum()}/{l_.sum()})")
    out.append("per-year d (full-sample tertile): " + " ".join(py))
    out.append(f"median ret T3/T1={s.ret[hi].median():.4f}/{s.ret[lo].median():.4f} ; winrate T3/T1={(s.ret[hi] > 0).mean():.3f}/{(s.ret[lo] > 0).mean():.3f}")
    out.append(f"up60 cutoffs (full) T1<= {s.up60.quantile(1/3):.3f}, T3> {s.up60.quantile(2/3):.3f}")
open(f"{OUT}/diag.txt", "w").write("\n".join(out) + "\n")
print("\n".join(out))
