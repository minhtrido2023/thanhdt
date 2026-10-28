"""Phần 2 — event-study giá quanh eff_date khi rating 8L đổi hạng. Thiết kế: REPORT.md §0 (PREREG).
Đầu vào: raw/*.parquet (pull_data.py) + data/benchmark/vnindex_tr_daily.csv. Read-only.
Chạy: $DNA_PYEXE event_study.py  -> out_*.csv + stdout (lưu out_event_study_stdout.txt)."""
import numpy as np, pandas as pd, db_dtypes  # noqa: F401 (dbdate trong parquet)
from scipy import stats

W, SEED, NBOOT = 60, 20261020, 2000
EFF_MIN, EFF_MAX = pd.Timestamp("2014-07-01"), pd.Timestamp("2026-07-31")
BENCH_CSV = "/home/trido/thanhdt/WorkingClaude/data/benchmark/vnindex_tr_daily.csv"


def rd(name):
    df = pd.read_parquet(f"raw/{name}.parquet")
    for c in ("time", "Release_Date"):
        if c in df:
            df[c] = pd.to_datetime(df[c].astype(str), errors="coerce")
    return df


# ---------- lịch phiên, benchmark, panel giá ----------
bm = pd.read_csv(BENCH_CSV, parse_dates=["date"]).sort_values("date").set_index("date")
cal = bm.index
r_b1 = bm.tr_gross.pct_change()
px = rd("px")
close = px.pivot(index="time", columns="ticker", values="Close").reindex(cal)
observed = close.notna()
close = close.ffill()
ret = close.pct_change(fill_method=None)
univ = rd("univ").assign(v=True).pivot(index="time", columns="ticker", values="v").reindex(cal).reindex(columns=close.columns)
univ = univ.fillna(False).astype(bool)
r_b2 = ret.where(univ & observed).median(axis=1)
# LỆCH PREREG (thêm sau khi thấy B2 cho +10-13% ở MỌI nhóm): tổng trung vị ngày < trung bình (skew) ⇒ B2 thiên lệch.
r_b3 = ret.where(univ & observed).mean(axis=1)   # B3 = trung bình EW universe cùng phiên
print(f"lịch phiên {cal.min().date()}→{cal.max().date()} n={len(cal)} | mã có giá {close.shape[1]}")

# ---------- sự kiện đổi hạng ----------
fa = rd("fa").sort_values(["ticker", "time"])
fa["prev"] = fa.groupby("ticker").rating.shift()
ev = fa[fa.prev.notna()].copy()   # gồm cả dòng KHÔNG đổi hạng = placebo G0 (lệch PREREG, thêm làm đối chứng)
ev["grp"] = np.select([ev.rating == ev.prev, (ev.prev >= 4) & (ev.rating <= 3), (ev.prev <= 3) & (ev.rating >= 4),
                       ev.rating < ev.prev], ["G0", "G1", "G2", "G3up"], "G3down")  # rating thấp = tốt
print("dòng rating có dòng trước (G0 = không đổi):", len(ev), ev.grp.value_counts().to_dict())

# ---------- ghép (ticker, quý) + cờ loại ----------
tf = rd("tf")
tf["qend"] = pd.PeriodIndex(tf.quarter, freq="Q").end_time.normalize()
tf = tf.sort_values(["ticker", "qend"])
tf["prev_rd"] = tf.groupby("ticker").Release_Date.shift()
tf["rd_lag"] = (tf.Release_Date - tf.qend).dt.days
tf["x_null"] = tf.Release_Date.isna()
tf["x_definite"] = (tf.rd_lag < 0) | (tf.Release_Date.notna() & tf.prev_rd.notna() & (tf.Release_Date <= tf.prev_rd))
tf["x_early7"] = tf.rd_lag.between(0, 7)
tf["eff"] = tf.Release_Date.fillna(tf.time)
tf = tf.sort_values("qend").drop_duplicates(["ticker", "eff"], keep="last")  # = dedupe q_time DESC của fa_ratings_8l
ev = ev.merge(tf[["ticker", "eff", "quarter", "x_null", "x_definite", "x_early7"]],
              left_on=["ticker", "time"], right_on=["ticker", "eff"], how="left")
n0 = len(ev)
ev = ev[ev.quarter.notna()].copy()
print(f"loại dòng không khớp (ticker, quý) (override forensic …): {n0 - len(ev)}")
ev = ev[(ev.time >= EFF_MIN) & (ev.time <= EFF_MAX)].copy()
ev["excl"] = ev.x_null | ev.x_definite | ev.x_early7
print("trong cửa sổ eff", EFF_MIN.date(), "→", EFF_MAX.date(), ":", len(ev),
      "| cờ loại: null", int(ev.x_null.sum()), "definite", int(ev.x_definite.sum()), "early<=7", int(ev.x_early7.sum()))

# ---------- cửa sổ AR ----------
ev["i0"] = cal.searchsorted(ev.time.values)
tick_ix = {t: i for i, t in enumerate(close.columns)}
R, O, U = ret.values, observed.values, univ.values
B1, B2, B3 = r_b1.values, r_b2.values, r_b3.values
keep, AR1, AR2, AR3, why = [], [], [], [], {"no_px": 0, "edge": 0, "not_univ": 0, "sparse": 0, "jump": 0}
for k, (t, i0) in enumerate(zip(ev.ticker, ev.i0)):
    j = tick_ix.get(t)
    if j is None:
        why["no_px"] += 1; continue
    if i0 - W < 1 or i0 + W >= len(cal):
        why["edge"] += 1; continue
    if not U[i0, j]:
        why["not_univ"] += 1; continue
    sl = slice(i0 - W, i0 + W + 1)
    r = R[sl, j]
    if O[sl, j].mean() < 0.8 or np.isnan(r).any():
        why["sparse"] += 1; continue
    if np.abs(r).max() > 0.40:
        why["jump"] += 1; continue
    keep.append(k); AR1.append(r - B1[sl]); AR2.append(r - B2[sl]); AR3.append(r - B3[sl])
ev = ev.iloc[keep].reset_index(drop=True)
AR = {"B1": np.array(AR1), "B2": np.array(AR2), "B3": np.array(AR3)}
ev["bank"] = ev.route.eq("BANK")
ev["era"] = np.where(ev.time.dt.year <= 2019, "IS", "OOS")
ev["cl"] = ev.time.dt.to_period("Q").astype(str)
print("loại theo cửa sổ:", why, "| còn lại:", len(ev))
ev.drop(columns=["eff"]).to_csv("out_p2_events.csv", index=False)

# ---------- thống kê cluster theo quý ----------
OFF = np.arange(-W, W + 1)
def col(k):
    return k + W
WIN = {"PRE[-60,-1]": (-60, -1), "DAY0": (0, 0), "TOTAL[-60,60]": (-60, 60),
       "POST_T1[2,20]": (2, 20), "POST_T1[2,40]": (2, 40), "POST_T1[2,60]": (2, 60),
       "OPLAG3[4,60]": (4, 60), "OPLAG8[9,60]": (9, 60),
       # LỆCH PREREG (thêm sau khi thấy drift đỉnh ở +20..+40 rồi phai): trễ vận hành ở chân trời ngắn
       "OPLAG3[4,20]": (4, 20), "OPLAG3[4,40]": (4, 40), "OPLAG8[9,20]": (9, 20), "OPLAG8[9,40]": (9, 40)}
rng = np.random.default_rng(SEED)


def analyse(mask, bench):
    a = AR[bench][mask]
    cls = ev.cl[mask].values
    lab, gi = np.unique(cls, return_inverse=True)
    G, N = len(lab), len(a)
    if N == 0:
        return None
    cum = np.cumsum(a, axis=1)
    def car(lo, hi, c=cum):
        return c[:, col(hi)] - (c[:, col(lo) - 1] if col(lo) > 0 else 0)
    X = np.column_stack([car(*WIN[w]) for w in WIN])                      # N × nwin
    post = cum[:, col(2):] - cum[:, [col(1)]]                              # CAR[2,k], k=2..60
    pre_path = cum - cum[:, [col(-1)]]                                     # tham chiếu close -1
    S_X = np.zeros((G, X.shape[1])); np.add.at(S_X, gi, X)
    S_P = np.zeros((G, post.shape[1])); np.add.at(S_P, gi, post)
    S_C = np.zeros((G, cum.shape[1])); np.add.at(S_C, gi, cum)
    n_g = np.bincount(gi, minlength=G).astype(float)
    m = X.mean(0)
    resid = np.zeros((G, X.shape[1])); np.add.at(resid, gi, X - m)
    se_cl = np.sqrt(G / max(G - 1, 1) * (resid ** 2).sum(0)) / N
    se_iid = X.std(0, ddof=1) / np.sqrt(N) if N > 1 else np.full(X.shape[1], np.nan)
    t = m / se_cl
    p = 2 * stats.t.sf(np.abs(t), df=max(G - 1, 1))
    w = rng.multinomial(G, np.full(G, 1 / G), size=NBOOT).astype(float)   # bootstrap theo quý
    den = w @ n_g
    bX = (w @ S_X) / den[:, None]
    bP = (w @ S_P) / den[:, None]
    lo, hi = np.percentile(bX, [2.5, 97.5], axis=0)
    i_pre, i_tot, i_p60 = list(WIN).index("PRE[-60,-1]"), list(WIN).index("TOTAL[-60,60]"), list(WIN).index("POST_T1[2,60]")
    frac = m[i_pre] / m[i_tot]
    bfrac = bX[:, i_pre] / bX[:, i_tot]
    def halflife(path):
        tgt = 0.5 * path[-1]
        hit = np.nonzero((path >= tgt) if path[-1] > 0 else (path <= tgt))[0]
        return 2 + hit[0] if len(hit) else np.nan
    hl = halflife(post.mean(0))
    bhl = np.array([halflife(bp) for bp in bP])
    rows = []
    for k, wn in enumerate(WIN):
        rows.append(dict(window=wn, N=N, G=G, mean=m[k], ci_lo=lo[k], ci_hi=hi[k], se_cl=se_cl[k], t=t[k], p=p[k],
                         N_eff=N * (se_iid[k] / se_cl[k]) ** 2 if se_cl[k] > 0 else np.nan))
    extra = dict(N=N, G=G, frac_pre=frac, frac_pre_lo=np.nanpercentile(bfrac, 2.5), frac_pre_hi=np.nanpercentile(bfrac, 97.5),
                 tot_ci_excl0=(lo[i_tot] > 0) or (hi[i_tot] < 0), halflife=hl,
                 hl_lo=np.nanpercentile(bhl, 2.5) if np.isfinite(bhl).any() else np.nan,
                 hl_hi=np.nanpercentile(bhl, 97.5) if np.isfinite(bhl).any() else np.nan,
                 p60_ci_excl0=(lo[i_p60] > 0) or (hi[i_p60] < 0))
    path = pd.DataFrame({"offset": OFF, "car_from_m61": cum.mean(0), "car_ref_close_m1": pre_path.mean(0)})
    return pd.DataFrame(rows), extra, path


# ---------- chạy ----------
SEG = {"all": lambda e: np.ones(len(e), bool), "nonbank": lambda e: ~e.bank.values, "bank": lambda e: e.bank.values,
       "IS": lambda e: (e.era == "IS").values, "OOS": lambda e: (e.era == "OOS").values}
out, ext, paths = [], [], []
for variant in ("main", "noexcl"):
    base = ~ev.excl.values if variant == "main" else np.ones(len(ev), bool)
    for g in ("G0", "G1", "G2", "G3up", "G3down"):
        for s, f in SEG.items():
            for b in ("B1", "B2", "B3"):
                mask = base & (ev.grp.values == g) & f(ev)
                r = analyse(mask, b)
                if r is None:
                    continue
                tab, ex, pth = r
                key = dict(variant=variant, grp=g, seg=s, bench=b)
                out.append(tab.assign(**key)); ext.append({**key, **ex}); paths.append(pth.assign(**key))
def bh(p):
    """Benjamini-Hochberg q-values."""
    n = len(p); o = np.argsort(p); q = p[o] * n / np.arange(1, n + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]; r = np.empty(n); r[o] = np.minimum(q, 1); return r


T = pd.concat(out, ignore_index=True)
E = pd.DataFrame(ext)
# họ F1 (chính) vs F2 (thăm dò), BH-FDR riêng từng họ
F1W = ["PRE[-60,-1]", "POST_T1[2,20]", "POST_T1[2,40]", "POST_T1[2,60]"]
T["family"] = np.where((T.variant == "main") & T.grp.isin(["G1", "G2"]) & (T.seg == "all") & T.window.isin(F1W)
                       & T.bench.isin(["B1", "B2"]), "F1", "F2")   # F1 đúng 16 phép PREREG; B3 là hậu kiểm
T["q_bh"] = np.nan
for fam, d in T.groupby("family"):
    ok = d.p.notna()
    T.loc[d.index[ok], "q_bh"] = bh(d.p[ok].values)
print("\n===== HỌ F1 (PREREG, 16 phép, BH riêng) =====")
print(T[T.family == "F1"][["grp", "bench", "window", "N", "G", "mean", "ci_lo", "ci_hi", "p", "q_bh", "N_eff"]].round(4).to_string(index=False))
print("số phép thử: F1 =", int((T.family == "F1").sum()), "| F2 =", int((T.family == "F2").sum()))
T.to_csv("out_p2_car_tests.csv", index=False)
E.to_csv("out_p2_frac_halflife.csv", index=False)
pd.concat(paths).to_csv("out_p2_car_paths.csv", index=False)

pd.set_option("display.width", 250)
fmt = lambda x: f"{100 * x:+.2f}%"
for v in ("main", "noexcl"):
    print(f"\n===== {v} =====")
    d = T[(T.variant == v) & T.window.isin(["PRE[-60,-1]", "DAY0", "POST_T1[2,20]", "POST_T1[2,40]", "POST_T1[2,60]", "OPLAG3[4,20]", "OPLAG8[9,20]", "OPLAG8[9,40]"])]
    for (g, s, b), x in d.groupby(["grp", "seg", "bench"], sort=False):
        if v == "noexcl" and s != "all":
            continue
        cells = " | ".join(f"{w}: {fmt(r.mean)} [{fmt(r.ci_lo)},{fmt(r.ci_hi)}] q={r.q_bh:.3f}" for r in x.itertuples() for w in [r.window])
        print(f"{g:6s} {s:7s} {b} N={x.N.iloc[0]:4d} G={x.G.iloc[0]:2d} Neff(POST60)={x[x.window == 'POST_T1[2,60]'].N_eff.iloc[0]:.0f} :: {cells}")
print("\n===== tỉ lệ trước phiên 0 & nửa-đời (main, seg all) =====")
print(E[(E.variant == "main") & (E.seg == "all")][["grp", "bench", "N", "G", "frac_pre", "frac_pre_lo", "frac_pre_hi", "tot_ci_excl0",
                                                    "halflife", "hl_lo", "hl_hi", "p60_ci_excl0"]].round(3).to_string(index=False))


# ---------- LỆCH PREREG: chênh lệch nhóm − placebo G0 (bootstrap theo quý CHUNG cho 2 nhóm) ----------
def diff_vs_g0(g, bench, seg="all", variant="main"):
    base = (~ev.excl.values if variant == "main" else np.ones(len(ev), bool)) & SEG[seg](ev)
    mA, mB = base & (ev.grp.values == g), base & (ev.grp.values == "G0")
    lab = np.unique(ev.cl.values[mA | mB]); G = len(lab); idx = {c: i for i, c in enumerate(lab)}
    def sums(m):
        a = AR[bench][m]; cum = np.hstack([np.zeros((len(a), 1)), np.cumsum(a, axis=1)])   # cột 0 = trước phiên -60
        gi = np.array([idx[c] for c in ev.cl.values[m]])
        X = np.column_stack([cum[:, col(hi) + 1] - cum[:, col(lo)] for lo, hi in WIN.values()])
        S = np.zeros((G, X.shape[1])); np.add.at(S, gi, X); return S, np.bincount(gi, minlength=G).astype(float), X
    SA, nA, XA = sums(mA); SB, nB, XB = sums(mB)
    d = XA.mean(0) - XB.mean(0)
    w = np.random.default_rng(SEED + 1).multinomial(G, np.full(G, 1 / G), size=NBOOT).astype(float)
    bd = (w @ SA) / (w @ nA)[:, None] - (w @ SB) / (w @ nB)[:, None]
    lo, hi = np.percentile(bd, [2.5, 97.5], axis=0)
    p = np.minimum(1, 2 * np.minimum((bd <= 0).mean(0), (bd >= 0).mean(0)))   # bootstrap 2 phía (sàn 1/NBOOT)
    return pd.DataFrame(dict(grp=g, bench=bench, seg=seg, variant=variant, window=list(WIN), NA=mA.sum(), NG0=mB.sum(),
                             G=G, diff=d, ci_lo=lo, ci_hi=hi, p_boot=np.maximum(p, 1 / NBOOT)))
D = pd.concat([diff_vs_g0(g, b, s, v) for v in ("main", "noexcl") for g in ("G1", "G2", "G3up", "G3down")
               for b in ("B1", "B3") for s in (["all", "nonbank", "bank", "IS", "OOS"] if v == "main" else ["all"])],
              ignore_index=True)
D["q_bh"] = bh(D.p_boot.values)
D.to_csv("out_p2_diff_vs_g0.csv", index=False)
print("\n===== chênh lệch nhóm − G0 (B1 & B3 cho cùng số vì benchmark triệt tiêu; in B3) — thăm dò, BH trên", len(D), "phép =====")
x = D[(D.bench == "B3") & D.window.isin(["PRE[-60,-1]", "DAY0", "POST_T1[2,20]", "POST_T1[2,40]", "POST_T1[2,60]", "OPLAG3[4,20]", "OPLAG8[9,20]", "OPLAG8[9,40]"])]
for (v, g, s), y in x.groupby(["variant", "grp", "seg"], sort=False):
    print(f"{v:6s} {g:6s} {s:7s} N={y.NA.iloc[0]:4d} vs G0 {y.NG0.iloc[0]:5d} :: " +
          " | ".join(f"{r.window}: {fmt(r.diff)} [{fmt(r.ci_lo)},{fmt(r.ci_hi)}] q={r.q_bh:.3f}" for r in y.itertuples()))
