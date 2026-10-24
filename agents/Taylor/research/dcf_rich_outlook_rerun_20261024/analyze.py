"""Phân tích panel.csv: (a) triển vọng NP Q+1/Q+2, (b) BHAR sau surprise dương, ghép ô.
N độc lập = cụm QUÝ BÁO CÁO (mùa công bố); CI = bootstrap cụm 2000 lần, seed 7."""
import numpy as np, pandas as pd, json, os
OUT = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(7); B = 2000
d = pd.read_csv(f"{OUT}/panel.csv", parse_dates=["rel", "d0"])
d = d[d.ok & d.mos.notna()].copy()
roe_scale = 1.0 if d.roe5y.median() > 1.5 else 0.01     # ROE5Y % hay phân số
d["roe_hi"] = d.roe5y >= 25 * roe_scale
d["bucket"] = pd.cut(d.mos, [-np.inf, -1.0, -0.2, 0.2, np.inf], labels=["RICH_DEEP", "RICH_MILD", "FAIR", "CHEAP"])
icb = d.icb.fillna(0)
d["grp"] = np.where(icb < 2000, "COMMODITY", np.where(((icb >= 3000) & (icb < 4000)) | ((icb >= 5000) & (icb < 6000)), "CONSUMER", "OTHER"))
d["sector"] = (icb // 100).astype(int)
d["mcap"] = d.price * d.oshares_pit
d["decel1"] = (d.yoy1 < d.yoy0).where(d.yoy1.notna() & d.yoy0.notna())
d["neg1"] = (d.yoy1 < 0).where(d.yoy1.notna())
d["dg1"] = d.yoy1 - d.yoy0
d["neg2"] = (d.yoy2 < 0).where(d.yoy2.notna())
d["clu"] = d.quarter

def boot_diff(a, b, col):
    """mean(col|a) - mean(col|b), bootstrap theo cụm quý."""
    a = a[a[col].notna()]; b = b[b[col].notna()]
    if len(a) < 10 or len(b) < 10: return dict(n_a=len(a), n_b=len(b), diff=np.nan, lo=np.nan, hi=np.nan, k=0)
    ga = a.groupby("clu")[col].agg(["sum", "count"]); gb = b.groupby("clu")[col].agg(["sum", "count"])
    cl = sorted(set(ga.index) | set(gb.index)); ga = ga.reindex(cl, fill_value=0); gb = gb.reindex(cl, fill_value=0)
    A = ga.values; Bv = gb.values; est = A[:, 0].sum() / A[:, 1].sum() - Bv[:, 0].sum() / Bv[:, 1].sum()
    bs = []
    for _ in range(B):
        ix = rng.integers(0, len(cl), len(cl)); sa = A[ix].sum(0); sb = Bv[ix].sum(0)
        if sa[1] > 0 and sb[1] > 0: bs.append(sa[0] / sa[1] - sb[0] / sb[1])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return dict(n_a=len(a), n_b=len(b), k=int((ga["count"] > 0).sum()), diff=est, lo=lo, hi=hi)

res = {"n_rows_ok": int(len(d)), "n_quarters": int(d.clu.nunique()), "n_tickers": int(d.ticker.nunique()),
       "roe_scale": roe_scale, "bucket_counts": d.bucket.value_counts().to_dict()}
# đặc tả: RICH ~ P/E cao?
v = d[(d.pe > 0)]
res["spearman_mos_vs_ey"] = float(v.groupby("clu").apply(lambda g: g.mos.rank().corr((1 / g.pe).rank())).mean())
res["median_pe_by_bucket"] = v.groupby("bucket", observed=True).pe.median().round(1).to_dict()

# (a) triển vọng lợi nhuận
outA = []
desc = d.groupby("bucket", observed=True).agg(n=("mos", "size"), yoy0_med=("yoy0", "median"), yoy1_med=("yoy1", "median"),
        yoy2_med=("yoy2", "median"), p_neg1=("neg1", "mean"), p_decel1=("decel1", "mean"), p_neg2=("neg2", "mean")).round(3)
desc.to_csv(f"{OUT}/outlook_by_bucket.csv")
subsets = {"ALL": d, "ROE_HI": d[d.roe_hi], "ROE_LO": d[~d.roe_hi], "CONSUMER": d[d.grp == "CONSUMER"],
           "COMMODITY": d[d.grp == "COMMODITY"], "OTHER": d[d.grp == "OTHER"]}
for nm, s in subsets.items():
    ctl = s[s.bucket.isin(["FAIR", "CHEAP"])]
    for grp in ("RICH_DEEP", "RICH_MILD"):
        for col in ("yoy1", "yoy2", "neg1", "decel1", "dg1"):
            outA.append(dict(subset=nm, group=grp, vs="FAIR+CHEAP", metric=col, **boot_diff(s[s.bucket == grp], ctl, col)))
# (a') kiểm soát mức tăng trưởng hiện tại: so trong ô (quý × tercile yoy0)
d["yoy0_t"] = d.groupby("clu").yoy0.transform(lambda x: pd.qcut(x.rank(method="first"), 3, labels=False) if x.notna().sum() >= 3 else np.nan)
for col in ("yoy1", "neg1"):
    m = d[d.bucket.isin(["FAIR", "CHEAP"])].groupby(["clu", "yoy0_t"])[col].mean().rename("cm")
    d = d.drop(columns=["cm"], errors="ignore").join(m, on=["clu", "yoy0_t"])
    d[col + "_adj"] = d[col] - d.cm
    for nm, s in {"ALL": d, "ROE_HI": d[d.roe_hi], "ROE_LO": d[~d.roe_hi], "CONSUMER": d[d.grp == "CONSUMER"], "COMMODITY": d[d.grp == "COMMODITY"]}.items():
        z = s.copy(); z["zero"] = 0.0
        a = z[z.bucket == "RICH_DEEP"]
        r = boot_diff(a, a.assign(**{col + "_adj": 0.0}), col + "_adj")
        outA.append(dict(subset=nm, group="RICH_DEEP", vs="cell(q×yoy0_t) FAIR+CHEAP", metric=col + "_adj", **r))
A = pd.DataFrame(outA); A.to_csv(f"{OUT}/outlook_diffs.csv", index=False)

# (b) drift sau surprise dương — ghép ô (quý × ngành 2 số × tercile cỡ × tercile SUE)
p = d[(d.sue > 0) & (d.yoy0 > 0)].drop(columns=["cm"], errors="ignore").copy()
p["size_t"] = p.groupby("clu").mcap.transform(lambda x: pd.qcut(x.rank(method="first"), 3, labels=False))
p["sue_t"] = p.groupby("clu").sue.transform(lambda x: pd.qcut(x.rank(method="first"), 3, labels=False))
outB = []
for H in (20, 40, 60):
    col = f"bhar{H}"
    ctl = p[p.bucket.isin(["FAIR", "CHEAP"])]
    cm = ctl.groupby(["clu", "sector", "size_t", "sue_t"])[col].mean().rename("cm")
    q = p.join(cm, on=["clu", "sector", "size_t", "sue_t"])
    q["ex"] = q[col] - q.cm                   # chỉ sự kiện có đối chứng cùng ô
    for nm, s in {"ALL": q, "ROE_HI": q[q.roe_hi], "ROE_LO": q[~q.roe_hi], "CONSUMER": q[q.grp == "CONSUMER"],
                  "COMMODITY": q[q.grp == "COMMODITY"], "OTHER": q[q.grp == "OTHER"]}.items():
        for grp in ("RICH_DEEP", "RICH_MILD"):
            a = s[(s.bucket == grp) & s.ex.notna()]
            r = boot_diff(a, a.assign(ex=0.0), "ex")
            r["raw_bhar_mean"] = float(s[s.bucket == grp][col].mean()); r["ctl_raw_bhar_mean"] = float(s[s.bucket.isin(["FAIR", "CHEAP"])][col].mean())
            outB.append(dict(H=H, subset=nm, group=grp, **r))
Bdf = pd.DataFrame(outB); Bdf.to_csv(f"{OUT}/drift_matched.csv", index=False)
res["n_pos_surprise"] = int(len(p)); res["n_pos_quarters"] = int(p.clu.nunique())
json.dump(res, open(f"{OUT}/summary.json", "w"), indent=1, default=str)
pd.set_option("display.width", 220)
print(json.dumps(res, indent=1, default=str)); print(desc)
print(A.round(3).to_string()); print(Bdf.round(3).to_string())
