"""Robustness cho drift (b) + outlook (a): (1) ô ghép lỏng q×ngành1số×cỡ, (2) RICH theo rank MoS trong quý
(quintile giàu nhất, tránh phụ thuộc mức r lịch sử), (3) IS 2014-19 / OOS 2020+."""
import numpy as np, pandas as pd, os, runpy
OUT = os.path.dirname(os.path.abspath(__file__))
ns = runpy.run_path(f"{OUT}/analyze.py", run_name="lib")   # tái dùng d, boot_diff (chạy lại analyze, seed cố định)
d, boot_diff = ns["d"], ns["boot_diff"]
d["ind1"] = (d.icb.fillna(0) // 1000).astype(int)
d["mq"] = d.groupby("clu").mos.transform(lambda x: pd.qcut(x.rank(method="first"), 5, labels=False))  # 0 = giàu nhất
p = d[(d.sue > 0) & (d.yoy0 > 0)].drop(columns=["cm"], errors="ignore").copy()
p["size_t"] = p.groupby("clu").mcap.transform(lambda x: pd.qcut(x.rank(method="first"), 3, labels=False))
p["sue_t"] = p.groupby("clu").sue.transform(lambda x: pd.qcut(x.rank(method="first"), 3, labels=False))
out = []
def run(tag, frame, is_treat, is_ctl, keys, H=60):
    col = f"bhar{H}"
    cm = frame[is_ctl(frame)].groupby(keys)[col].mean().rename("cm")
    q = frame.join(cm, on=keys); q["ex"] = q[col] - q.cm
    for nm, s in {"ALL": q, "ROE_HI": q[q.roe_hi], "ROE_LO": q[~q.roe_hi], "CONSUMER": q[q.grp == "CONSUMER"],
                  "COMMODITY": q[q.grp == "COMMODITY"]}.items():
        a = s[is_treat(s) & s.ex.notna()]
        r = boot_diff(a, a.assign(ex=0.0), "ex"); r["n_treat_total"] = int(is_treat(s).sum())
        out.append(dict(test=tag, H=H, subset=nm, **r))
deep = lambda s: s.bucket == "RICH_DEEP"; ctl = lambda s: s.bucket.isin(["FAIR", "CHEAP"])
for H in (20, 60):
    run("strict q×sector2×size×sue", p, deep, ctl, ["clu", "sector", "size_t", "sue_t"], H)
    run("loose q×ind1×size", p, deep, ctl, ["clu", "ind1", "size_t"], H)
    run("rankQ1(MoS trong quý) vs Q3-5, q×ind1×size", p, lambda s: s.mq == 0, lambda s: s.mq >= 2, ["clu", "ind1", "size_t"], H)
    for lab, msk in (("IS2014-19", p.rel.dt.year <= 2019), ("OOS2020+", p.rel.dt.year >= 2020)):
        run(f"loose {lab}", p[msk], deep, ctl, ["clu", "ind1", "size_t"], H)
R = pd.DataFrame(out); R.to_csv(f"{OUT}/drift_robust.csv", index=False)
# outlook IS/OOS + rank-RICH
o = []
for lab, s in (("IS2014-19", d[d.rel.dt.year <= 2019]), ("OOS2020+", d[d.rel.dt.year >= 2020]), ("ALL", d)):
    for sub, ss in (("ALL", s), ("ROE_HI", s[s.roe_hi])):
        o.append(dict(test=f"abs DEEP vs FAIR+CHEAP {lab}", subset=sub, metric="yoy1", **boot_diff(ss[ss.bucket == "RICH_DEEP"], ss[ss.bucket.isin(["FAIR", "CHEAP"])], "yoy1")))
        o.append(dict(test=f"abs DEEP vs FAIR+CHEAP {lab}", subset=sub, metric="neg1", **boot_diff(ss[ss.bucket == "RICH_DEEP"], ss[ss.bucket.isin(["FAIR", "CHEAP"])], "neg1")))
        o.append(dict(test=f"rankQ1 vs Q3-5 {lab}", subset=sub, metric="yoy1", **boot_diff(ss[ss.mq == 0], ss[ss.mq >= 2], "yoy1")))
O = pd.DataFrame(o); O.to_csv(f"{OUT}/outlook_robust.csv", index=False)
pd.set_option("display.width", 220); print(R.round(3).to_string()); print(O.round(3).to_string())
print("RICH_DEEP pos-surprise total:", int((p.bucket == "RICH_DEEP").sum()))
