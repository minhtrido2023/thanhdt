"""Phần 2 vòng 2 — G − G0* (khớp quý × mom × SUE × bank), B3 loại chính mã. Thiết kế: PREREG.md (commit a467963b9).
Đầu vào: ../rating_8l_lag_p2_20261020/raw/{fa,tf,univ,px}.parquet + raw/vol.parquet + data/earnings_surprise_data.pkl
+ data/benchmark/vnindex_tr_daily.csv (lịch). Read-only.
Chạy: OMP_NUM_THREADS=1 $DNA_PYEXE event_study_v2.py > out_v2_stdout.txt"""
import numpy as np, pandas as pd, db_dtypes  # noqa: F401 (dbdate trong parquet)
from scipy import stats

WPRE, WPOST, SEED, NBOOT = 60, 40, 20261020, 2000
EFF_MIN, EFF_MAX = pd.Timestamp("2014-07-01"), pd.Timestamp("2026-07-31")
WC = "/home/trido/thanhdt/WorkingClaude"
RAW1 = "../rating_8l_lag_p2_20261020/raw"
WIN = {"[2,20]": (2, 20), "[2,40]": (2, 40)}
COST, ADV_MIN = 0.002, 5e9


def rd(path):
    df = pd.read_parquet(path)
    for c in ("time", "Release_Date"):
        if c in df:
            df[c] = pd.to_datetime(df[c].astype(str), errors="coerce")
    return df


# ---------- lịch, giá, B3 loại chính mã ----------
cal = pd.read_csv(f"{WC}/data/benchmark/vnindex_tr_daily.csv", parse_dates=["date"]).sort_values("date").date
cal = pd.DatetimeIndex(cal)
px = rd(f"{RAW1}/px.parquet")
close = px.pivot(index="time", columns="ticker", values="Close").reindex(cal)
observed = close.notna()
close = close.ffill()
ret = close.pct_change(fill_method=None)
univ = rd(f"{RAW1}/univ.parquet").assign(v=True).pivot(index="time", columns="ticker", values="v")
univ = univ.reindex(cal).reindex(columns=close.columns).fillna(False).astype(bool)
inb = (univ & observed & ret.notna()).values
R = ret.values
S_b = np.where(inb, R, 0.0).sum(1)
C_b = inb.sum(1)
vol = rd("raw/vol.parquet")
tv = (vol.assign(tv=vol.Price * vol.Volume).pivot(index="time", columns="ticker", values="tv")
      .reindex(cal).reindex(columns=close.columns)).values
print(f"lịch {cal.min().date()}→{cal.max().date()} n={len(cal)} | mã có giá {close.shape[1]}")

# kiểm giá điều chỉnh 1 mã chia tách (như vòng 1)
v = px[px.ticker == "VHM"].sort_values("time").set_index("time")
d0 = pd.Timestamp("2026-08-07")
if d0 in v.index:
    i = v.index.get_loc(d0)
    print(f"kiểm điều chỉnh VHM {d0.date()}: r(Price) {v.Price.iloc[i] / v.Price.iloc[i - 1] - 1:+.3f} "
          f"r(Close) {v.Close.iloc[i] / v.Close.iloc[i - 1] - 1:+.3f}")

# ---------- sự kiện + cờ loại (giữ nguyên vòng 1) ----------
fa = rd(f"{RAW1}/fa.parquet").sort_values(["ticker", "time"])
fa["prev"] = fa.groupby("ticker").rating.shift()
ev = fa[fa.prev.notna()].copy()
ev["grp"] = np.select([ev.rating == ev.prev, (ev.prev >= 4) & (ev.rating <= 3), (ev.prev <= 3) & (ev.rating >= 4)],
                      ["G0", "G1", "G2"], "G3")
tf = rd(f"{RAW1}/tf.parquet")
tf["qend"] = pd.PeriodIndex(tf.quarter, freq="Q").end_time.normalize()
tf = tf.sort_values(["ticker", "qend"])
tf["prev_rd"] = tf.groupby("ticker").Release_Date.shift()
tf["rd_lag"] = (tf.Release_Date - tf.qend).dt.days
tf["x_null"] = tf.Release_Date.isna()
tf["x_definite"] = (tf.rd_lag < 0) | (tf.Release_Date.notna() & tf.prev_rd.notna() & (tf.Release_Date <= tf.prev_rd))
tf["x_early7"] = tf.rd_lag.between(0, 7)
tf["eff"] = tf.Release_Date.fillna(tf.time)
tf = tf.sort_values("qend").drop_duplicates(["ticker", "eff"], keep="last")
ev = ev.merge(tf[["ticker", "eff", "quarter", "x_null", "x_definite", "x_early7"]],
              left_on=["ticker", "time"], right_on=["ticker", "eff"], how="left")
ev = ev[ev.quarter.notna() & (ev.time >= EFF_MIN) & (ev.time <= EFF_MAX) & ev.grp.isin(["G0", "G1", "G2"])].copy()
peek7 = pd.read_csv(f"{WC}/mike/agents/Taylor/research/rating_8l_lag_20261020/out_phase3_definite_peek_cases.csv")
ev["x_peek7"] = pd.MultiIndex.from_frame(ev[["ticker", "quarter"]]).isin(pd.MultiIndex.from_frame(peek7[["ticker", "quarter"]]))
ev["excl"] = ev.x_null | ev.x_definite | ev.x_early7 | ev.x_peek7
print("G0/G1/G2 trong cửa sổ eff:", ev.grp.value_counts().to_dict(), "| loại a-c:", int(ev.excl.sum()),
      "(trong đó 7-ca list khớp:", int(ev.x_peek7.sum()), ")")
ev = ev[~ev.excl].copy()

# ---------- cửa sổ AR, momentum, ADV ----------
ev["i0"] = cal.searchsorted(ev.time.values)
tix = {t: i for i, t in enumerate(close.columns)}
O, U, CL = observed.values, univ.values, close.values
keep, ARs, MOM, ADV, why = [], [], [], [], dict(no_px=0, edge=0, not_univ=0, sparse=0, jump=0)
for k, (t, i0) in enumerate(zip(ev.ticker, ev.i0)):
    j = tix.get(t)
    if j is None:
        why["no_px"] += 1; continue
    if i0 - WPRE - 1 < 0 or i0 + WPOST >= len(cal):
        why["edge"] += 1; continue
    if not U[i0, j]:
        why["not_univ"] += 1; continue
    sl = slice(i0 - WPRE, i0 + WPOST + 1)
    r = R[sl, j]
    if O[sl, j].mean() < 0.8 or np.isnan(r).any():
        why["sparse"] += 1; continue
    if np.abs(r).max() > 0.40:
        why["jump"] += 1; continue
    own = inb[sl, j]
    b3 = np.where(own, (S_b[sl] - np.where(own, R[sl, j], 0)) / np.maximum(C_b[sl] - 1, 1), S_b[sl] / C_b[sl])
    keep.append(k); ARs.append(r - b3)
    MOM.append(CL[i0 - 1, j] / CL[i0 - 1 - WPRE, j] - 1)
    ADV.append(np.nanmedian(tv[i0 - 20:i0, j]) if np.isfinite(tv[i0 - 20:i0, j]).any() else np.nan)
ev = ev.iloc[keep].reset_index(drop=True)
AR = np.array(ARs)
ev["mom"], ev["adv"] = MOM, ADV
ev["bank"] = ev.route.eq("BANK")
ev["cl"] = ev.time.dt.to_period("Q").astype(str)
ev["era"] = np.where(ev.time.dt.year <= 2019, "IS", "OOS")
cum = np.cumsum(AR, axis=1)
for w, (lo, hi) in WIN.items():
    ev[f"car{w}"] = cum[:, hi + WPRE] - cum[:, lo - 1 + WPRE]
print("loại theo cửa sổ:", why, "| còn:", len(ev), ev.grp.value_counts().to_dict())

# ---------- SUE tự dựng (PIT theo Release_Date ≤ eff) ----------
es = pd.read_pickle(f"{WC}/data/earnings_surprise_data.pkl")
es["qp"] = pd.PeriodIndex(es.quarter, freq="Q")
es = es.sort_values(["ticker", "qp", "Release_Date"]).drop_duplicates(["ticker", "qp"], keep="first")
es["d"] = es.NP_P0 - es.NP_P4
by_t = {t: g for t, g in es.groupby("ticker")}
sue, n_hist, viol = [], [], 0
for t, q, eff in zip(ev.ticker, ev.quarter, ev.time):
    g = by_t.get(t)
    qp = pd.Period(q, freq="Q")
    if g is None or (g.qp == qp).sum() == 0:
        sue.append(np.nan); n_hist.append(0); continue
    dq = g.loc[g.qp == qp, "d"].iloc[0]
    h = g[(g.qp < qp) & (g.qp >= qp - 8) & (g.Release_Date <= eff) & g.d.notna()]
    viol += int((h.Release_Date > eff).sum())
    n_hist.append(len(h))
    sd = h.d.std(ddof=1) if len(h) >= 6 else np.nan
    sue.append(dq / sd if np.isfinite(dq) and sd and np.isfinite(sd) and sd > 0 else np.nan)
ev["sue"], ev["sue_nhist"] = sue, n_hist
assert viol == 0
print("SUE: có", int(ev.sue.notna().sum()), "/", len(ev), "| thiếu theo nhóm:",
      ev[ev.sue.isna()].grp.value_counts().to_dict(), "| kiểm PIT: 0 dòng lịch sử có Release_Date > eff")
print("SUE trung vị theo nhóm:", ev.groupby("grp").sue.median().round(3).to_dict())


def qbin(s, by):
    return s.groupby(by).transform(lambda x: np.ceil(x.rank(pct=True) * 5).clip(1, 5))


ev["momq"] = qbin(ev.mom, ev.cl)
ev["sueq"] = np.nan
m = ev.sue.notna()
ev.loc[m, "sueq"] = qbin(ev.sue[m], ev.cl[m])
# mom quintile cho tập có SUE (dùng cho cả bản chính và bản đối chứng không-SUE, cùng tập sự kiện)
ev.loc[m, "momq_s"] = qbin(ev.mom[m], ev.cl[m])
ev.to_csv("out_v2_events.csv", index=False)


# ---------- δ = CAR_G − mean CAR_G0 cùng ô ----------
def matched(df, cell):
    g0 = df[df.grp == "G0"].groupby(cell)[[f"car{w}" for w in WIN]].mean()
    out = {}
    for g in ("G1", "G2"):
        x = df[df.grp == g].join(g0, on=cell, rsuffix="_g0")
        n_all = len(x)
        x = x[x[f"car{list(WIN)[0]}_g0"].notna()].copy()
        for w in WIN:
            x[f"d{w}"] = x[f"car{w}"] - x[f"car{w}_g0"]
        out[g] = (x, n_all - len(x))
    return out


rng_seed = SEED


def stat(x, w):
    d = x[f"d{w}"].values
    N = len(d)
    if N < 2:
        return dict(N=N)
    lab, gi = np.unique(x.cl.values, return_inverse=True)
    G = len(lab)
    S = np.bincount(gi, d, G); n = np.bincount(gi, minlength=G).astype(float)
    wts = np.random.default_rng(rng_seed).multinomial(G, np.full(G, 1 / G), size=NBOOT).astype(float)
    b = (wts @ S) / (wts @ n)
    mu = d.mean()
    p = max(min(1.0, 2 * min((b <= 0).mean(), (b >= 0).mean())), 1 / NBOOT)
    def cse(ids):
        _, k = np.unique(ids, return_inverse=True); K = k.max() + 1
        rs = np.bincount(k, d - mu, K)
        return np.sqrt(K / (K - 1) * (rs ** 2).sum()) / N, K
    se_q, _ = cse(x.cl.values)
    se_t, K_t = cse(x.ticker.values)
    se_iid = d.std(ddof=1) / np.sqrt(N)
    return dict(N=N, G=G, mean=mu, ci_lo=np.percentile(b, 2.5), ci_hi=np.percentile(b, 97.5), p_boot=p,
                se_q=se_q, N_eff=N * (se_iid / se_q) ** 2, K_tick=K_t, se_tick=se_t,
                p_tick=2 * stats.t.sf(abs(mu / se_t), df=K_t - 1))


def bh(p):
    p = np.asarray(p, float); n = len(p); o = np.argsort(p); q = p[o] * n / np.arange(1, n + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]; r = np.empty(n); r[o] = np.minimum(q, 1); return r


def family(df, cell, tag):
    M = matched(df, cell)
    rows = []
    for g in ("G1", "G2"):
        x, n_drop = M[g]
        for w in WIN:
            s = stat(x, w)
            rows.append(dict(spec=tag, grp=g, window=w, n_nocell=n_drop, **s))
    T = pd.DataFrame(rows)
    T["q_bh"] = bh(T.p_boot.values)
    return T, M


base = ev[ev.sue.notna()].copy()
CELL = ["cl", "momq_s", "sueq", "bank"]
CELL_NOSUE = ["cl", "momq_s", "bank"]
F1, M1 = family(base, CELL, "F1 khớp SUE (CHÍNH)")
FC, MC = family(base, CELL_NOSUE, "đối chứng không khớp SUE")
pd.set_option("display.width", 250)
cols = ["spec", "grp", "window", "N", "n_nocell", "G", "mean", "ci_lo", "ci_hi", "p_boot", "q_bh", "N_eff", "K_tick", "p_tick"]
print("\n===== HỌ CHÍNH F1 (4 phép, BH riêng) =====")
print(F1[cols].round(4).to_string(index=False))
print("\n===== THĂM DÒ: cùng tập sự kiện, ô KHÔNG có SUE (BH riêng 4 phép) =====")
print(FC[cols].round(4).to_string(index=False))


# ---------- tiêu chí tái lập ----------
def criteria(M, F):
    res = []
    for g in ("G1", "G2"):
        x = M[g][0]
        for w in WIN:
            r = F[(F.grp == g) & (F.window == w)].iloc[0]
            sg = np.sign(r["mean"])
            halves = {e: stat(x[x.era == e], w) for e in ("IS", "OOS")}
            b_ok = all(np.sign(h["mean"]) == sg and h["p_boot"] < 0.10 for h in halves.values())
            qs = x.groupby("cl")[f"d{w}"].sum().sort_values(ascending=(sg < 0))
            top3 = list(qs.index[:3])
            m3 = x[~x.cl.isin(top3)][f"d{w}"].mean()
            c_ok = np.sign(m3) == sg and abs(m3) >= 0.5 * abs(r["mean"])
            xa = x[x.adv >= ADV_MIN]
            ma = xa[f"d{w}"].mean() if len(xa) else np.nan
            d_ok = (abs(r["mean"]) - COST > 0) and np.sign(ma) == sg and (abs(ma) - COST > 0)
            res.append(dict(grp=g, window=w, mean=r["mean"], q_bh=r.q_bh, a=r.q_bh < 0.05,
                            IS_mean=halves["IS"]["mean"], IS_p=halves["IS"]["p_boot"], IS_N=halves["IS"]["N"],
                            OOS_mean=halves["OOS"]["mean"], OOS_p=halves["OOS"]["p_boot"], OOS_N=halves["OOS"]["N"], b=b_ok,
                            top3=",".join(top3), mean_drop3=m3, ratio_drop3=m3 / r["mean"], c=c_ok,
                            net_cost=abs(r["mean"]) - COST, N_adv5=len(xa), mean_adv5=ma,
                            net_cost_adv5=abs(ma) - COST if np.isfinite(ma) else np.nan, d=d_ok,
                            N=r.N, N_eff=r.N_eff))
    return pd.DataFrame(res)


C1 = criteria(M1, F1)
print("\n===== TIÊU CHÍ TÁI LẬP (a)-(d) — bản CHÍNH =====")
print(C1.round(4).to_string(index=False))
CC = criteria(MC, FC)
print("\n===== tiêu chí trên bản đối chứng không-SUE (thăm dò) =====")
print(CC[["grp", "window", "mean", "q_bh", "a", "b", "c", "d", "ratio_drop3", "mean_adv5"]].round(4).to_string(index=False))

# ---------- thăm dò: loại sự kiện thứ 2 của cùng mã trong 40 phiên ----------
b2 = base.sort_values(["ticker", "i0"]).copy()
b2["gap"] = b2.groupby("ticker").i0.diff()
dd = b2[~(b2.gap <= WPOST)].copy()
print(f"\n===== THĂM DÒ: loại sự kiện thứ 2 cùng mã trong {WPOST} phiên: bỏ {len(b2) - len(dd)} / {len(b2)} =====")
FD, _ = family(dd, CELL, "dedupe40 khớp SUE")
print(FD[cols].round(4).to_string(index=False))

# ---------- thăm dò: toàn bộ sự kiện (kể cả thiếu SUE), ô quý×mom×bank ----------
FA, _ = family(ev, ["cl", "momq", "bank"], "mọi sự kiện, không SUE")
print("\n===== THĂM DÒ: mọi sự kiện (kể cả thiếu SUE), ô quý×mom×bank =====")
print(FA[cols].round(4).to_string(index=False))
# ngân hàng / phi NH (khớp SUE)
for nm, msk in (("nonbank", ~base.bank), ("bank", base.bank)):
    Fb, _ = family(base[msk], CELL, f"{nm} khớp SUE")
    print(f"\n----- THĂM DÒ {nm} -----"); print(Fb[cols].round(4).to_string(index=False))

pd.concat([F1, FC, FD, FA]).to_csv("out_v2_tests.csv", index=False)
pd.concat([C1.assign(spec="F1"), CC.assign(spec="nosue")]).to_csv("out_v2_criteria.csv", index=False)
print("\nSố phép thử: chính F1 = 4; thăm dò: đối chứng 4 + dedupe 4 + mọi-sự-kiện 4 + bank/nonbank 8 + nửa mẫu/ADV/bỏ-3-quý (mô tả)")
