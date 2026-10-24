"""5 kiểm tra bổ sung cho dcf_rich_outlook_20261024 (quant-skeptic yêu cầu). Tái dùng boot_diff + cách ghép
của analyze.py/robust.py (bản copy). Cụm độc lập = quý báo cáo; bootstrap 2000, seed 7.
  T1 ngưỡng ROE5Y 15/20/25/30% · T2 MDE (power 80%, alpha 5%, mô phỏng bootstrap cụm quý)
  T3 tập sự kiện LAG thật (qualify) · T4 bỏ sự kiện đổi OShares >2% ±30 ngày · T5 benchmark VNINDEX TR."""
import numpy as np, pandas as pd, os, runpy, json
OUT = os.path.dirname(os.path.abspath(__file__))
ns = runpy.run_path(f"{OUT}/analyze.py", run_name="lib")
boot_diff = ns["boot_diff"]
d0 = ns["d"]
aug = pd.read_csv(f"{OUT}/panel_aug.csv")
mm = pd.read_csv(f"{OUT}/sh_chg_minmax.csv")
keep = ["bhar20_tr", "bhar60_tr", "post_own", "post_ex_px", "post_ex_tr", "qualify", "lag_NP_R",
        "prior_n_good", "pa_HL3", "tier", "surprise_B_MA", "post_ret"]
d = d0.merge(aug[["ticker", "quarter"] + keep], on=["ticker", "quarter"], how="left").merge(mm, on=["ticker", "quarter"], how="left")
assert len(d) == len(d0)
d["ind1"] = (d.icb.fillna(0) // 1000).astype(int)
d["mq"] = d.groupby("clu").mos.transform(lambda x: pd.qcut(x.rank(method="first"), 5, labels=False))
rng = np.random.default_rng(11)

def prep(frame):
    p = frame.drop(columns=["cm"], errors="ignore").copy()
    p["size_t"] = p.groupby("clu").mcap.transform(lambda x: pd.qcut(x.rank(method="first"), 3, labels=False))
    return p

def matched(p, treat, ctl, col, keys=("clu", "ind1", "size_t")):
    keys = list(keys)
    cm = p[ctl(p)].groupby(keys)[col].mean().rename("cm")
    q = p.join(cm, on=keys); q["ex"] = q[col] - q.cm
    return q[treat(q) & q.ex.notna()]

def est(a):
    r = boot_diff(a, a.assign(ex=0.0), "ex"); return r

deep = lambda s: s.bucket == "RICH_DEEP"; ctlf = lambda s: s.bucket.isin(["FAIR", "CHEAP"])
rq1 = lambda s: s.mq == 0; rq35 = lambda s: s.mq >= 2
POS = (d.sue > 0) & (d.yoy0 > 0)
rows = []

def table(tag, base, col="bhar60", thresholds=(0.15, 0.20, 0.25, 0.30)):
    p = prep(base)
    variants = {"loose": (p, deep, ctlf), "rankQ1": (p, rq1, rq35),
                "loose IS2014-19": (prep(base[base.rel.dt.year <= 2019]), deep, ctlf),
                "loose OOS2020+": (prep(base[base.rel.dt.year >= 2020]), deep, ctlf)}
    for vn, (pp, tf, cf) in variants.items():
        a = matched(pp, tf, cf, col)
        r = est(a); rows.append(dict(test=tag, col=col, variant=vn, thr=None, subset="ALL", **r))
        com = a[a.grp == "COMMODITY"]; rows.append(dict(test=tag, col=col, variant=vn, thr=None, subset="COMMODITY", **est(com)))
        for t in thresholds:
            hi = a.roe5y >= t
            for nm, s in (("ROE_HI", a[hi]), ("ROE_LO", a[~hi]), ("ROE_LO|COMMODITY", a[(~hi) | (a.grp == "COMMODITY")]),
                          ("ROE_HI&~COMMODITY", a[hi & (a.grp != "COMMODITY")])):
                rows.append(dict(test=tag, col=col, variant=vn, thr=t, subset=nm, **est(s)))
            # hiệu HI − LO (bootstrap cụm quý)
            rows.append(dict(test=tag, col=col, variant=vn, thr=t, subset="HI-LO",
                             **boot_diff(a[hi], a[~hi], "ex")))

# ---------- T1 + control (bhar60 BQ VNINDEX giá) ----------
table("T1_base", d[POS])
table("T1_base", d[POS], col="bhar20", thresholds=(0.25,))
# ---------- T4 bỏ đổi OShares >2% (max/min trong [d0-30,d0+30], tái lập 465/7510) ----------
table("T4_drop_shchg", d[POS & ~(d.mm > 0.02)])
# ---------- T5 benchmark VNINDEX TR (tr_gross) ----------
table("T5_TR", d[POS], col="bhar60_tr")
table("T5_TR_drop_shchg", d[POS & ~(d.mm > 0.02)], col="bhar60_tr")

# ---------- T3 tập LAG thật ----------
Q = d[d.qualify == True]
lag_rows = []
for col in ("bhar60", "bhar60_tr", "post_ex_px", "post_ex_tr", "bhar20"):
    for vn, base in (("ALL", Q), ("IS2014-19", Q[Q.rel.dt.year <= 2019]), ("OOS2020+", Q[Q.rel.dt.year >= 2020])):
        # (a) thô: RICH_DEEP vs FAIR+CHEAP trong tập qualify; (b) khử trung bình quý của qualify-control
        lag_rows.append(dict(col=col, period=vn, method="raw diff", subset="ALL",
                             **boot_diff(base[deep(base)], base[ctlf(base)], col)))
        cm = base[ctlf(base)].groupby("clu")[col].mean().rename("cm")
        q = base.drop(columns=["cm"], errors="ignore").join(cm, on="clu"); q["ex"] = q[col] - q.cm
        a = q[deep(q) & q.ex.notna()]
        lag_rows.append(dict(col=col, period=vn, method="quarter-demeaned", subset="ALL", **est(a)))
        for t in (0.15, 0.20, 0.25, 0.30):
            lag_rows.append(dict(col=col, period=vn, method="quarter-demeaned", subset=f"ROE_HI>={t:.2f}", **est(a[a.roe5y >= t])))
            lag_rows.append(dict(col=col, period=vn, method="quarter-demeaned", subset=f"ROE_LO<{t:.2f}", **est(a[~(a.roe5y >= t)])))
        lag_rows.append(dict(col=col, period=vn, method="quarter-demeaned", subset="COMMODITY", **est(a[a.grp == "COMMODITY"])))
LAGT = pd.DataFrame(lag_rows); LAGT.to_csv(f"{OUT}/t3_lag_qualify.csv", index=False)
lag_counts = Q.bucket.value_counts().to_dict()

R = pd.DataFrame(rows); R.to_csv(f"{OUT}/t1_t4_t5_drift.csv", index=False)

# ---------- n sự kiện / n quý theo ngưỡng (loose, bhar60) ----------
p = prep(d[POS]); a = matched(p, deep, ctlf, "bhar60")
cnt = [dict(thr=t, n_hi=int((a.roe5y >= t).sum()), k_hi=int(a[a.roe5y >= t].clu.nunique()),
            n_lo=int((~(a.roe5y >= t)).sum()), k_lo=int(a[~(a.roe5y >= t)].clu.nunique()),
            n_hi_tk=int(a[a.roe5y >= t].ticker.nunique()), roe_nan=int(a.roe5y.isna().sum())) for t in (0.15, 0.20, 0.25, 0.30)]
pd.DataFrame(cnt).to_csv(f"{OUT}/t1_counts.csv", index=False)

# ---------- T2 MDE: mô phỏng bootstrap cụm quý ----------
def cl_stats(x, c):
    g = pd.DataFrame({"x": x, "c": c}).groupby("c").x.agg(["sum", "count"]).values
    return g

def power(g, delta, nsim=1000):
    """g: (K,2) [sum, count] của dữ liệu ĐÃ ĐỊNH TÂM về 0; thêm delta mỗi sự kiện; t cụm-robust |t|>1.96."""
    K = len(g); rej = 0
    for _ in range(nsim):
        ix = rng.integers(0, K, K); s = g[ix, 0] + delta * g[ix, 1]; n = g[ix, 1]
        N = n.sum(); m = s.sum() / N
        se = np.sqrt(K / (K - 1) * ((s - m * n) ** 2).sum()) / N
        rej += abs(m / se) > 1.96 if se > 0 else 0
    return rej / nsim

def mde(a, col="ex"):
    x = a[col].to_numpy(float); c = a.clu.to_numpy()
    g = cl_stats(x - x.mean(), c)
    grid = np.arange(0.0, 0.40, 0.005); pw = None
    for dl in grid:
        pw = power(g, dl)
        if pw >= 0.80: break
    # SE bootstrap cụm (đối chiếu xấp xỉ 2,8×SE)
    K = len(g); bs = []
    for _ in range(2000):
        ix = rng.integers(0, K, K); bs.append(g[ix, 0].sum() / g[ix, 1].sum())
    se = float(np.std(bs, ddof=1))
    return dict(n=len(x), k=K, point=float(x.mean()), mde80=float(dl), power_at_mde=pw, se_boot=se, mde_2p8se=2.8 * se,
                power_vs_m045=power(g, -0.045), power_vs_m034=power(g, -0.034), power_vs_m030=power(g, -0.03))

M = []
for tag, base, col in (("loose bhar60", d[POS], "bhar60"), ("loose bhar60_tr", d[POS], "bhar60_tr"),
                       ("loose bhar60 drop_shchg", d[POS & ~(d.mm > 0.02)], "bhar60")):
    a = matched(prep(base), deep, ctlf, col)
    for t in (0.15, 0.20, 0.25, 0.30):
        M.append(dict(test=tag, thr=t, subset="ROE_HI", **mde(a[a.roe5y >= t])))
        M.append(dict(test=tag, thr=t, subset="ROE_LO", **mde(a[~(a.roe5y >= t)])))
for t in (0.15, 0.20, 0.25, 0.30):   # LAG qualify, post_ex_px quarter-demeaned
    for col in ("bhar60", "post_ex_px"):
        cm = Q[ctlf(Q)].groupby("clu")[col].mean().rename("cm")
        q = Q.drop(columns=["cm"], errors="ignore").join(cm, on="clu"); q["ex"] = q[col] - q.cm
        a = q[deep(q) & q.ex.notna()]
        if (a.roe5y >= t).sum() >= 10:
            M.append(dict(test=f"LAG qualify {col}", thr=t, subset="ROE_HI", **mde(a[a.roe5y >= t])))
MD = pd.DataFrame(M); MD.to_csv(f"{OUT}/t2_mde.csv", index=False)

summ = {"n_ok": int(len(d)), "n_pos": int(POS.sum()), "n_shchg_gt2pct": int((d.mm > 0.02).sum()),
        "n_shchg_richdeep": int(((d.mm > 0.02) & deep(d)).sum()), "lag_qualify_by_bucket": lag_counts,
        "lag_qualify_n": int(len(Q)), "lag_qualify_quarters": int(Q.clu.nunique())}
json.dump(summ, open(f"{OUT}/summary_rerun.json", "w"), indent=1)
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 500)
print(json.dumps(summ, indent=1)); print(pd.DataFrame(cnt).to_string())
cols = ["test", "col", "variant", "thr", "subset", "n_a", "k", "diff", "lo", "hi"]
print(R[cols].round(3).to_string()); print(LAGT.round(3).to_string()); print(MD.round(3).to_string())
