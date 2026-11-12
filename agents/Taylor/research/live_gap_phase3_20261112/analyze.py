#!/usr/bin/env python3
"""GĐ3 — thời điểm an toàn V2.4 vs gửi tiết kiệm (job Taylor_20261112_132954).
Thực thi đúng PREREG.md (md5 trong PREREG.md5). Usage: analyze.py <ledger_P0.csv> <ledger_P30.csv>
Ghi mọi output vào thư mục của script. Seed cố định 20261112."""
import sys, os, json
import numpy as np, pandas as pd

W = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, W)
from deposit_rate_vn import deposit_events_df  # noqa: E402

OUT = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(20261112)
STATE_NAME = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EXBULL"}
TC = 0.001


# ---------------------------------------------------------------- data
def load_ledger(p):
    d = pd.read_csv(p, low_memory=False)
    d = d[d.record_type == "DAILY"].copy()
    d["time"] = pd.to_datetime(d.ymd)
    d = d.set_index("time").sort_index()
    return d[["combined_nav", "state", "vni_close"]].astype(float)


def savings_index(rates: pd.DataFrame, start, end, col):
    """cum factor theo ngày lịch, actual/365, lãi %/năm as-of backward."""
    cal = pd.DataFrame({"time": pd.date_range(start, end, freq="D")})
    m = pd.merge_asof(cal, rates.sort_values("time")[["time", col]], on="time", direction="backward")
    r = m[col].ffill().bfill().values / 100.0
    f = np.cumprod(1 + r / 365.0)
    return pd.Series(f, index=m.time)


def dep1m_known():
    p = W + "/mike/agents/Taylor/research/idle_cash_proxy_20260927/fiinprox_deposit_1m_big4_monthly_2019_2026.csv"
    d = pd.read_csv(p)
    d["time"] = pd.to_datetime(d.period + "-01") + pd.offsets.MonthBegin(1)  # tháng T dùng từ 1/T+1
    return d[["time", "rate_pct"]].rename(columns={"rate_pct": "dep1m"})


def vni_close_full(led):
    v = pd.read_csv(W + "/data/VNINDEX.csv", usecols=["time", "Close"], low_memory=False)
    v["time"] = pd.to_datetime(v.time)
    v = v.set_index("time").Close
    v = v[v.index < led.index[0]]
    return pd.concat([v, led.vni_close]).sort_index()


# ---------------------------------------------------------------- outcomes
def excess_at(nav, sav, starts, H):
    """starts = ngày s (đã là phiên kế tiếp). trả DataFrame ret, sav, exc, dd, end."""
    idx = nav.index
    last = idx[-1]
    out = []
    for s in starts:
        e = s + pd.DateOffset(months=H)
        if e > last or s < sav.index[0]:
            out.append((s, np.nan, np.nan, np.nan, np.nan, pd.NaT)); continue
        j1 = idx.searchsorted(e, side="right") - 1
        i0 = idx.get_loc(s)
        path = nav.values[i0:j1 + 1]
        ret = path[-1] / path[0] - 1
        sv = sav.loc[idx[j1]] / sav.loc[s] - 1
        dd = (path / np.maximum.accumulate(path) - 1).min()
        out.append((s, ret, sv, ret - sv, dd, idx[j1]))
    return pd.DataFrame(out, columns=["s", "ret", "sav", "exc", "dd", "end"]).set_index("s")


def next_session(idx, t):
    i = idx.searchsorted(t, side="right")
    return idx[i] if i < len(idx) else pd.NaT


def era_of(t):
    if t.year <= 2018: return "IS"
    if t.year == 2019: return "BUF"
    return "OOS"


# ---------------------------------------------------------------- step 1
def baseline(nav, sav, tag):
    idx = nav.index
    rows, yrows = [], []
    for H in (3, 6, 12):
        starts = idx[1:]
        ex = excess_at(nav, sav, starts, H).dropna()
        ex["era"] = [era_of(t) for t in ex.index]
        ex["year"] = ex.index.year
        for grp, g in [("ALL", ex)] + [(e, ex[ex.era == e]) for e in ("IS", "BUF", "OOS")]:
            if not len(g): continue
            lose = g[g.exc <= 0]
            # CI P(thắng): block bootstrap theo tháng (khối 12 tháng)
            mo = g.exc.groupby(g.index.to_period("M")).apply(lambda x: (x > 0).mean())
            lo, hi = block_ci(mo.values, 12, 1000)
            rows.append(dict(leg=tag, H=H, era=grp, n_days=len(g), n_months=len(mo),
                             n_indep=round(len(mo) / H, 1),
                             p_win=(g.exc > 0).mean(), p_win_ci90_lo=lo, p_win_ci90_hi=hi,
                             exc_p10=g.exc.quantile(.1), exc_p25=g.exc.quantile(.25), exc_med=g.exc.median(),
                             exc_p75=g.exc.quantile(.75), exc_p90=g.exc.quantile(.9),
                             med_loss_when_lose=lose.exc.median() if len(lose) else np.nan,
                             med_dd_when_lose=lose.dd.median() if len(lose) else np.nan,
                             p10_dd_when_lose=lose.dd.quantile(.1) if len(lose) else np.nan))
        for y, g in ex.groupby("year"):
            yrows.append(dict(leg=tag, H=H, year=y, n_days=len(g), p_win=(g.exc > 0).mean(),
                              exc_med=g.exc.median(), med_dd=g.dd.median()))
    return pd.DataFrame(rows), pd.DataFrame(yrows)


def block_ci(x, b, n, q=(0.05, 0.95)):
    x = np.asarray(x, float); m = len(x)
    if m == 0: return np.nan, np.nan
    b = min(b, m)
    nb = int(np.ceil(m / b)); st = []
    for _ in range(n):
        s = RNG.integers(0, m, nb)
        ii = np.concatenate([(np.arange(k, k + b) % m) for k in s])[:m]
        st.append(np.nanmean(x[ii]))
    return tuple(np.quantile(st, q))


# ---------------------------------------------------------------- conditions
def build_conditions(led, vfull, dates):
    """giá trị thô các biến tại mỗi t trong dates (đóng cửa t)."""
    df = pd.DataFrame(index=dates)
    df["V1"] = led.state.reindex(dates).values
    dd52 = vfull / vfull.rolling(252, min_periods=200).max() - 1
    df["V2"] = dd52.reindex(dates).values
    br = pd.read_csv(os.path.join(OUT, "breadth_pit_b200.csv"), parse_dates=["time"]).set_index("time").b200
    df["V3"] = [br[br.index < t].iloc[-1] if (br.index < t).any() else np.nan for t in dates]
    us = pd.read_csv(W + "/data/us_market_history.csv", parse_dates=["time"]).set_index("time").spx_dd_1y.dropna()
    df["V4"] = [us[us.index < t].iloc[-1] for t in dates]
    le = pd.read_csv(W + "/data/lag_edge_health.csv", parse_dates=["entry", "known_date"]).sort_values(["known_date", "entry"])
    df["V5"] = [le[le.known_date <= t].mean12.iloc[-1] if (le.known_date <= t).any() else np.nan for t in dates]
    lr = np.log(vfull).diff()
    vol = lr.rolling(60, min_periods=55).std() * np.sqrt(252)
    df["V6"] = vol.reindex(dates).values
    return df


NAT_CUTS = {"V2": [-0.20, -0.10], "V4": [-0.15, -0.05]}


def classify(df, cuts):
    c = pd.DataFrame(index=df.index)
    c["V1"] = df.V1.map(lambda s: np.nan if np.isnan(s) else (0 if s <= 2 else (1 if s == 3 else 2)))
    for v in ("V2", "V3", "V4", "V5", "V6"):
        lo, hi = cuts[v]
        x = df[v]
        c[v] = np.where(x.isna(), np.nan, np.where(x <= lo, 0, np.where(x <= hi, 1, 2)))
    return c


def episodes(cls):
    """số episode (cụm tháng liên tiếp cùng lớp) theo lớp."""
    s = cls.dropna()
    runs = (s != s.shift()).cumsum()
    return s.groupby(runs).first().value_counts().to_dict()


def delta(cls, y):
    a = y[cls == 2]; b = y[cls == 0]
    if len(a) < 3 or len(b) < 3: return np.nan
    return a.mean() - b.mean()


def test_var(cls, y, years, nnull=2000, nplac=500):
    cls = np.asarray(cls, float); y = np.asarray(y, float); n = len(y)
    d0 = delta(cls, y)
    if np.isnan(d0): return dict(delta=np.nan, p=np.nan, mde=np.nan, plac_ok=False, loyo_ok=False, loyo_min=np.nan, loyo_max=np.nan)
    nulls = []
    for _ in range(nnull):
        k = RNG.integers(12, n - 11)
        nulls.append(delta(np.roll(cls, k), y))
    nulls = np.array(nulls); nulls = nulls[~np.isnan(nulls)]
    p = (1 + np.sum(np.abs(nulls) >= abs(d0))) / (1 + len(nulls))
    mde = 2.8 * nulls.std()
    # placebo hoán vị-trong-năm
    pl = []
    yrs = np.asarray(years)
    for _ in range(nplac):
        c2 = cls.copy()
        for yy in np.unique(yrs):
            ii = np.where(yrs == yy)[0]; c2[ii] = c2[RNG.permutation(ii)]
        pl.append(delta(c2, y))
    pl = np.array(pl); pl = pl[~np.isnan(pl)]
    plac_ok = (d0 > np.quantile(pl, .9)) if d0 > 0 else (d0 < np.quantile(pl, .1))
    # bỏ từng năm
    lo = []
    for yy in np.unique(yrs):
        m = yrs != yy
        lo.append(delta(cls[m], y[m]))
    lo = np.array(lo)
    loyo_ok = bool(np.all(~np.isnan(lo)) and np.all(np.sign(lo) == np.sign(d0)))
    return dict(delta=d0, p=p, mde=mde, plac_q10=np.quantile(pl, .1), plac_q90=np.quantile(pl, .9),
                plac_ok=bool(plac_ok), loyo_ok=loyo_ok, loyo_min=np.nanmin(lo), loyo_max=np.nanmax(lo))


def bh(p):
    p = np.asarray(p, float); q = np.full_like(p, np.nan)
    ok = ~np.isnan(p); pv = p[ok]; m = len(pv)
    if m == 0: return q
    o = np.argsort(pv); r = pv[o] * m / (np.arange(m) + 1)
    r = np.minimum.accumulate(r[::-1])[::-1]
    qq = np.empty(m); qq[o] = np.minimum(r, 1); q[ok] = qq
    return q


def class_table(cls, ex, era, var):
    rows = []
    ep = episodes(cls)
    for k in (0, 1, 2):
        g = ex[cls == k]
        if not len(g): continue
        lo, hi = block_ci((g.values > 0).astype(float), 12, 1000)
        rows.append(dict(var=var, era=era, cls=int(k), n_months=len(g), n_episodes=ep.get(k, 0),
                         p_win=(g > 0).mean(), p_win_ci90_lo=lo, p_win_ci90_hi=hi, exc_med=g.median(), exc_mean=g.mean()))
    return rows


# ---------------------------------------------------------------- step 3 policy
def policy_nav(nav, sav, off_daily):
    """off_daily[t]=True => từ phiên t+1 ở tiết kiệm. Trả nav chính sách + số lần đổi."""
    idx = nav.index
    r_eng = nav.pct_change().fillna(0).values
    sv = sav.reindex(idx).values
    r_sav = np.r_[0, sv[1:] / sv[:-1] - 1]
    off = np.asarray(off_daily, bool)
    pos = np.r_[False, off[:-1]]  # áp từ t+1
    r = np.where(pos, r_sav, r_eng)
    sw = np.r_[False, pos[1:] != pos[:-1]]
    r = r - sw * TC
    return pd.Series(np.cumprod(1 + r), index=idx), int(sw.sum())


def perf(n):
    yrs = (n.index[-1] - n.index[0]).days / 365.25
    cagr = (n.iloc[-1] / n.iloc[0]) ** (1 / yrs) - 1
    r = n.pct_change().dropna()
    sh = r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else np.nan
    dd = (n / n.cummax() - 1).min()
    return cagr, sh, dd


def segments(mask):
    m = np.asarray(mask, bool); segs = []; i = 0
    while i < len(m):
        j = i
        while j < len(m) and m[j] == m[i]: j += 1
        segs.append((bool(m[i]), j - i)); i = j
    return segs


def random_like(mask):
    segs = segments(mask)
    offs = [l for v, l in segs if v]; ons = [l for v, l in segs if not v]
    offs = list(RNG.permutation(offs)) if offs else []; ons = list(RNG.permutation(ons)) if ons else []
    first_off = segs[0][0]
    out = []
    a, b = (offs, ons) if first_off else (ons, offs)
    va, vb = (True, False) if first_off else (False, True)
    while a or b:
        if a: out += [va] * a.pop()
        if b: out += [vb] * b.pop()
    return np.array(out[:len(mask)], bool)


def eval_policy(name, nav, sav, off, nplac=500):
    pn, nsw = policy_nav(nav, sav, off)
    c, s, d = perf(pn)
    pls = []
    for _ in range(nplac):
        pm = random_like(off)
        pls.append(perf(policy_nav(nav, sav, pm)[0]))
    pls = np.array(pls)
    return dict(policy=name, off_frac=float(np.mean(off)), n_switch=nsw, cagr=c, sharpe=s, maxdd=d,
                plac_cagr_p50=np.quantile(pls[:, 0], .5), plac_cagr_p90=np.quantile(pls[:, 0], .9),
                pct_rank_cagr=float(np.mean(pls[:, 0] < c)),
                plac_dd_p50=np.quantile(pls[:, 2], .5), pct_rank_dd=float(np.mean(pls[:, 2] < d)),
                plac_sharpe_p50=np.quantile(pls[:, 1], .5))


# ---------------------------------------------------------------- main
def main(p0, p30):
    legs = {"P0": load_ledger(p0), "P30": load_ledger(p30)}
    start, end = legs["P0"].index[0], legs["P0"].index[-1]
    dep = deposit_events_df()
    sav12 = savings_index(dep, start - pd.Timedelta(days=5), end + pd.Timedelta(days=5), "deposit_rate")
    d1 = dep1m_known()
    sav1m = savings_index(d1, "2019-03-01", end + pd.Timedelta(days=5), "dep1m")
    res = {}

    # ---- step 1
    B, Y = [], []
    for tag, led in legs.items():
        nav = led.combined_nav
        b, y = baseline(nav, sav12, tag); B.append(b); Y.append(y)
    B = pd.concat(B); Y = pd.concat(Y)
    B.to_csv(os.path.join(OUT, "step1_baseline.csv"), index=False)
    Y.to_csv(os.path.join(OUT, "step1_baseline_by_year.csv"), index=False)
    for tag, led in legs.items():
        res[f"perf_{tag}"] = dict(zip(("cagr", "sharpe", "maxdd"), perf(led.combined_nav)))

    # ---- step 2
    led = legs["P0"]; nav = led.combined_nav; idx = nav.index
    vfull = vni_close_full(led)
    months = pd.Series(idx, index=idx).groupby(idx.to_period("M")).first().values
    months = pd.DatetimeIndex(months)
    raw = build_conditions(led, vfull, months)
    starts = [next_session(idx, t) for t in months]
    ok = [not pd.isna(s) for s in starts]
    raw = raw[ok]; starts = [s for s in starts if not pd.isna(s)]
    outc = {}
    for H in (12, 6):
        e = excess_at(nav, sav12, starts, H); e.index = raw.index; outc[H] = e
    # P30 outcome (độ nhạy)
    e30 = excess_at(legs["P30"].combined_nav, sav12, starts, 12); e30.index = raw.index
    era = pd.Series([era_of(t) for t in raw.index], index=raw.index)
    ism = era == "IS"
    cuts = {v: NAT_CUTS[v] for v in NAT_CUTS}
    for v in ("V3", "V5", "V6"):
        x = raw.loc[ism, v].dropna()
        cuts[v] = [x.quantile(1 / 3), x.quantile(2 / 3)]
    cls = classify(raw, cuts)
    raw.join(cls, rsuffix="_cls").join(outc[12][["exc", "ret", "sav"]]).assign(era=era).to_csv(os.path.join(OUT, "step2_monthly_panel.csv"))
    res["cuts"] = {k: [float(a) for a in v] for k, v in cuts.items()}

    T, CT = [], []
    for spec, ycol in (("main_P0_H12", outc[12].exc), ("sens_P0_H6", outc[6].exc), ("sens_P30_H12", e30.exc)):
        for er in ("IS", "OOS"):
            m = (era == er) & ycol.notna()
            for v in ("V1", "V2", "V3", "V4", "V5", "V6"):
                mm = m & cls[v].notna()
                r = test_var(cls.loc[mm, v].values, ycol[mm].values, raw.index[mm].year)
                r.update(spec=spec, era=er, var=v, n_months=int(mm.sum()))
                T.append(r)
                if spec == "main_P0_H12":
                    CT += class_table(cls.loc[mm, v], ycol[mm], er, v)
    T = pd.DataFrame(T)
    T["q_bh"] = np.nan
    for (sp, er), g in T.groupby(["spec", "era"]):
        T.loc[g.index, "q_bh"] = bh(g.p.values)
    piv = T[T.spec == "main_P0_H12"].pivot(index="var", columns="era")
    passes = {}
    for v in piv.index:
        dI, dO = piv.loc[v, ("delta", "IS")], piv.loc[v, ("delta", "OOS")]
        c1 = bool(piv.loc[v, ("q_bh", "IS")] < .10 and piv.loc[v, ("q_bh", "OOS")] < .10 and np.sign(dI) == np.sign(dO))
        c2 = bool(piv.loc[v, ("plac_ok", "IS")] and piv.loc[v, ("plac_ok", "OOS")])
        c3 = bool(piv.loc[v, ("loyo_ok", "IS")] and piv.loc[v, ("loyo_ok", "OOS")])
        passes[v] = dict(c1_fdr_samesign=c1, c2_placebo=c2, c3_loyo=c3, pass_123=c1 and c2 and c3)
    T.to_csv(os.path.join(OUT, "step2_tests.csv"), index=False)
    pd.DataFrame(CT).to_csv(os.path.join(OUT, "step2_class_table.csv"), index=False)
    res["passes"] = passes

    # Value Radar mô tả (ngoài họ)
    try:
        import value_radar as vr
        rs = vr.load_series(update=False).set_index("time").score
        z = [rs[rs.index <= t].iloc[-1] if (rs.index <= t).any() else np.nan for t in raw.index]
        z = pd.Series(z, index=raw.index)
        zc = pd.Series(np.where(z.isna(), np.nan, np.where(z < 33, 0, np.where(z <= 67, 1, 2))), index=raw.index)
        R = []
        for er in ("IS", "OOS"):
            m = (era == er) & outc[12].exc.notna() & zc.notna()
            R += class_table(zc[m], outc[12].exc[m], er, "RADAR")
        pd.DataFrame(R).to_csv(os.path.join(OUT, "step2_radar_descriptive.csv"), index=False)
    except Exception as ex:  # noqa
        res["radar_error"] = repr(ex)

    # ---- step 3
    daily_raw = build_conditions(led, vfull, idx)
    dcls = classify(daily_raw, cuts)
    P = []
    for v, pz in passes.items():
        if not pz["pass_123"]: continue
        dI = piv.loc[v, ("delta", "IS")]
        worse = 0 if dI > 0 else 2
        P.append(eval_policy(f"{v}_off_cls{worse}", nav, sav12, (dcls[v] == worse).values))
    P.append(eval_policy("REF_DT5G_CRISIS_BEAR_off", nav, sav12, (led.state <= 2).values))
    c, s, d = perf(nav)
    P.append(dict(policy="ENGINE_P0", off_frac=0.0, n_switch=0, cagr=c, sharpe=s, maxdd=d))
    pd.DataFrame(P).to_csv(os.path.join(OUT, "step3_policy.csv"), index=False)

    # ---- step 4 (2019+)
    dk = pd.merge_asof(pd.DataFrame({"time": raw.index}), d1.sort_values("time"), on="time", direction="backward").set_index("time").dep1m
    dk91 = pd.merge_asof(pd.DataFrame({"time": raw.index - pd.Timedelta(days=91)}), d1.sort_values("time"), on="time",
                         direction="backward").dep1m.values
    pe = pd.read_csv(W + "/data/VNINDEX_pe_only.csv", parse_dates=["time"]).set_index("time").Pe.dropna()
    pek = pd.Series([pe[pe.index <= t].iloc[-1] if (pe.index <= t).any() else np.nan for t in raw.index], index=raw.index)
    s4 = pd.DataFrame({"dep1m": dk, "trend3m": dk.values - dk91, "spread": 100 / pek - dk}, index=raw.index)
    m19 = (s4.index >= "2019-03-01")
    ref = (s4.index >= "2019-03-01") & (s4.index <= "2020-12-31")
    c_lvl = s4.dep1m[ref].median(); c_sp = s4.spread[ref].median()
    e1m = excess_at(nav, sav1m, [s for s, t in zip(starts, raw.index)], 12); e1m.index = raw.index
    lab = pd.DataFrame({"exc12_hurdle12": outc[12].exc, "exc12_dep1m": e1m.exc})
    S4 = []
    for name, cser in (("dep1m_level_high", (s4.dep1m > c_lvl).astype(float)),
                       ("dep1m_trend3m_up", (s4.trend3m > 0).astype(float)),
                       ("spread_ey_dep1m_high", (s4.spread > c_sp).astype(float))):
        for lc in lab.columns:
            mm = m19 & lab[lc].notna() & s4.notna().all(axis=1)
            cc = cser[mm]; yy = lab.loc[mm, lc]
            ep = episodes(cc)
            for k in (0.0, 1.0):
                g = yy[cc == k]
                S4.append(dict(cond=name, label=lc, cls=int(k), n_months=len(g), n_episodes=ep.get(k, 0),
                               p_win=(g > 0).mean() if len(g) else np.nan, exc_med=g.median() if len(g) else np.nan))
    pd.DataFrame(S4).to_csv(os.path.join(OUT, "step4_rate.csv"), index=False)
    res["step4_cuts"] = dict(dep1m_median_2019_2020=float(c_lvl), spread_median_2019_2020=float(c_sp))

    # ---- step 5
    S5 = []
    for tag, l in legs.items():
        n = l.combined_nav; ix = n.index
        r_eng = n.pct_change().fillna(0).values
        sv = sav12.reindex(ix).values; r_sav = np.r_[0, sv[1:] / sv[:-1] - 1]
        N = len(ix); b = 252; nb = int(np.ceil(N / b))
        boots = [np.concatenate([(np.arange(k, k + b) % N) for k in RNG.integers(0, N, nb)])[:N] for _ in range(1000)]
        yrs = (ix[-1] - ix[0]).days / 365.25
        for w in np.round(np.arange(0, 1.01, .1), 1):
            r = w * r_eng + (1 - w) * r_sav
            nv = pd.Series(np.cumprod(1 + r), index=ix)
            c, s, d = perf(nv)
            cg, dd = [], []
            for bi in boots:
                v = np.cumprod(1 + r[bi]); cg.append(v[-1] ** (1 / yrs) - 1); dd.append((v / np.maximum.accumulate(v) - 1).min())
            ex = excess_at(nv, sav12, ix[1:], 12).dropna()
            S5.append(dict(leg=tag, w=w, cagr=c, sharpe=s, maxdd=d, boot_cagr_p5=np.quantile(cg, .05),
                           boot_cagr_p50=np.quantile(cg, .5), boot_maxdd_p5=np.quantile(dd, .05),
                           p_win12=(ex.exc > 0).mean(), med_loss12=ex.exc[ex.exc <= 0].median()))
    S5 = pd.DataFrame(S5); S5.to_csv(os.path.join(OUT, "step5_sizing.csv"), index=False)

    json.dump(res, open(os.path.join(OUT, "summary.json"), "w"), indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
