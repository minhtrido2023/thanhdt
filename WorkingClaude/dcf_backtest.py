# -*- coding: utf-8 -*-
"""
dcf_backtest.py — empirical calibration + walk-forward validation for dcf_valuation.py.

Two studies (both point-in-time / no look-ahead for the *inputs*; forward-looking columns are
used only as evaluation labels, never as model inputs):

  A) RECENCY-WEIGHT CALIBRATION — does a recency-weighted average of the last 3 annual
     earnings-growth rates predict NEXT year's actual growth better than an equal-weighted
     average? Compares schemes {equal, 50/30/20, 60/25/15, exp-decay} by rank-IC and MAE of
     predicted-vs-realized next-year growth, walk-forward IS(<=2019)/OOS(>=2020).

  B) MARGIN-OF-SAFETY IC — does the DCF margin-of-safety predict forward returns
     (profit_1M/2M/3M) on the non-financial rating<=3 universe? Computes FV once per financial
     release (point-in-time), merges as-of onto a monthly price panel, and reports Spearman IC
     IS(2014-19)/OOS(2020-26). Honest read: if IC is not positive & stable, the tool is an
     interpretive aid, not a measured edge (unlike the other 8L lenses).

Run: python dcf_backtest.py            (both studies)
     python dcf_backtest.py --calib    (only A)
     python dcf_backtest.py --ic       (only B)
Author: Taylor. Job Taylor_20260714_042622.
"""
import os, sys, argparse, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
import duckdb
import dcf_valuation as D

WEIGHT_SCHEMES = {
    "equal_1/3":   (1/3, 1/3, 1/3),
    "50/30/20":    (0.50, 0.30, 0.20),
    "60/25/15":    (0.60, 0.25, 0.15),
    "expdecay_.6": (0.6, 0.24, 0.096),   # w_k ∝ 0.6^(k-1), renormalized below
}
def _norm(w):
    w = np.array(w, float); return tuple(w / w.sum())
WEIGHT_SCHEMES = {k: _norm(v) for k, v in WEIGHT_SCHEMES.items()}


def spearman_ic(a, b):
    m = (~pd.isna(a)) & (~pd.isna(b))
    if m.sum() < 8: return np.nan
    return pd.Series(a[m]).rank().corr(pd.Series(b[m]).rank())


# ============================================================ A) recency-weight calibration
def build_growth_panel():
    """One obs per (ticker, calendar-year last release): trailing 3 annual growths + realized
    next-year TTM-earnings growth. Non-financial universe only."""
    fin = D._load_financials()
    routes = D._load_routes()
    fin_fin = set(routes[routes.route.isin(D.FIN_ROUTES)].ticker.unique())
    fin = fin[~fin.ticker.isin(fin_fin)]
    rows = []
    for tk, g in fin.groupby("ticker"):
        g = g.sort_values("time").reset_index(drop=True)
        g["yr"] = g.time.dt.year
        g["ttm_np"] = g[["NP_P0","NP_P1","NP_P2","NP_P3"]].sum(axis=1, min_count=1)
        # one row per calendar year: the last release of each year
        last_per_yr = g.groupby("yr").tail(1)
        for _, r in last_per_yr.iterrows():
            hist = g[g.time <= r.time]
            ann = D._annual_series(hist, ["NP_P0","NP_P1","NP_P2","NP_P3"])
            if len(ann) < 4:                       # need g1,g2,g3
                continue
            def gr(a, b):
                return (a/b - 1) if (b and b > 0) else np.nan
            g1, g2, g3 = gr(ann[0], ann[1]), gr(ann[1], ann[2]), gr(ann[2], ann[3])
            if any(pd.isna(x) for x in (g1, g2, g3)):
                continue
            # realized next-year growth: TTM_NP at a release ~365d later vs now
            fut = g[(g.time > r.time + pd.Timedelta(days=300)) & (g.time <= r.time + pd.Timedelta(days=430))]
            if len(fut) == 0 or not (r.ttm_np and r.ttm_np > 0):
                continue
            g_next = fut.ttm_np.iloc[0] / r.ttm_np - 1
            rows.append({"ticker": tk, "year": int(r.yr), "g1": g1, "g2": g2, "g3": g3, "g_next": g_next})
    return pd.DataFrame(rows)


def run_calibration():
    print("\n" + "="*78)
    print("STUDY A — recency-weight calibration (predict next-year earnings growth)")
    print("="*78)
    pan = build_growth_panel()
    # clamp extreme growths (robust: winsorize at +/-100% so a single 10x doesn't dominate)
    for c in ["g1","g2","g3","g_next"]:
        pan[c] = pan[c].clip(-0.9, 2.0)
    print(f"panel n={len(pan)}  years {pan.year.min()}-{pan.year.max()}  tickers={pan.ticker.nunique()}")
    for label, split in [("IS (<=2019)", pan[pan.year <= 2019]), ("OOS (>=2020)", pan[pan.year >= 2020]),
                         ("ALL", pan)]:
        print(f"\n  {label}  n={len(split)}")
        print(f"    {'scheme':14s} {'rankIC':>8s} {'MAE':>8s} {'corr':>8s}")
        for name, w in WEIGHT_SCHEMES.items():
            ghat = w[0]*split.g1 + w[1]*split.g2 + w[2]*split.g3
            ic = spearman_ic(ghat.values, split.g_next.values)
            mae = float((ghat - split.g_next).abs().mean())
            corr = float(ghat.corr(split.g_next))
            print(f"    {name:14s} {ic:8.3f} {mae:8.3f} {corr:8.3f}")
    # also: does last-year-only (g1) beat blends? and simple mean?
    print("\n  reference predictors (ALL):")
    for name, ghat in [("g1_only", pan.g1), ("mean(g1,g2,g3)", pan[["g1","g2","g3"]].mean(axis=1))]:
        ic = spearman_ic(ghat.values, pan.g_next.values); mae=float((ghat-pan.g_next).abs().mean())
        print(f"    {name:14s} rankIC={ic:.3f} MAE={mae:.3f}")
    return pan


# ============================================================ B) margin-of-safety IC
def run_ic():
    print("\n" + "="*78)
    print("STUDY B — margin-of-safety forward-return IC (non-financial, rating<=3)")
    print("="*78)
    c = duckdb.connect(":memory:")
    # candidate non-financial tickers ever rated <=3
    cand = c.execute("""SELECT DISTINCT ticker FROM read_parquet('data/bq_cache/fa_ratings_8l.parquet')
        WHERE rating<=3 AND route NOT IN ('BANK','INSURANCE','SECURITIES')""").df().ticker.tolist()
    cand_sql = "(" + ",".join(f"'{t}'" for t in cand) + ")"

    # 1) FV once per financial release (point-in-time) — cached to an experiment file (§8)
    cache_fp = f"{WORKDIR}/mike/agents/Taylor/dcf_exp/fv_releases.parquet"
    os.makedirs(os.path.dirname(cache_fp), exist_ok=True)
    if os.path.exists(cache_fp) and not os.environ.get("DCF_REFRESH"):
        fv = pd.read_parquet(cache_fp)
        print(f"FV loaded from cache: {fv.ticker.nunique()} tickers, {len(fv)} release-points")
    else:
        fin = D._load_financials()
        D._load_routes(); D._load_icb_map()      # warm caches once
        fin_by_tk = {tk: g for tk, g in fin.groupby("ticker")}
        fv_rows = []
        for tk in cand:
            g = fin_by_tk.get(tk)
            if g is None or len(g) < 5: continue
            for t in g.time.unique():
                if pd.Timestamp(t) < pd.Timestamp("2012-06-01"):
                    continue                      # deposit/cpi proxies + IC window start later
                res = D.fair_value(tk, t, price=None, fin=g)
                if res["ok"]:
                    fv_rows.append({"ticker": tk, "rel_time": pd.Timestamp(t), "fv_ps": res["fair_value_ps"]})
        fv = pd.DataFrame(fv_rows).sort_values(["ticker","rel_time"]).reset_index(drop=True)
        fv.to_parquet(cache_fp)
        print(f"FV computed for {fv.ticker.nunique()} tickers, {len(fv)} release-points (cached)")

    # 2) monthly price panel + forward returns (first trading row each month)
    px = c.execute(f"""
        SELECT ticker, tdate, Price, profit_1M, profit_2M, profit_3M FROM (
          SELECT ticker, CAST(time AS DATE) AS tdate, Price, profit_1M, profit_2M, profit_3M,
                 row_number() OVER (PARTITION BY ticker, date_trunc('month',CAST(time AS DATE)) ORDER BY CAST(time AS DATE)) rn
          FROM read_parquet('data/bq_cache/ticker/2*.parquet')
          WHERE ticker IN {cand_sql} AND CAST(time AS DATE) >= DATE '2014-01-01'
        ) WHERE rn=1 AND Price IS NOT NULL
    """).df().rename(columns={"tdate": "time"})
    px["time"] = pd.to_datetime(px["time"])
    px = px.sort_values(["ticker","time"]).reset_index(drop=True)

    # 3) as-of merge FV (latest release <= eval date), per ticker
    merged = []
    for tk, gp in px.groupby("ticker"):
        gf = fv[fv.ticker == tk].drop(columns=["ticker"])
        if len(gf) == 0: continue
        m = pd.merge_asof(gp.sort_values("time"), gf.sort_values("rel_time"),
                          left_on="time", right_on="rel_time", direction="backward")
        merged.append(m)
    m = pd.concat(merged, ignore_index=True)
    m = m[m.fv_ps.notna() & (m.fv_ps > 0)]
    # rating<=3 as-of filter
    rat = c.execute("""SELECT ticker, time, rating FROM read_parquet('data/bq_cache/fa_ratings_8l.parquet')""").df()
    rat["time"] = pd.to_datetime(rat["time"]); rat = rat.sort_values(["ticker","time"])
    mm = []
    for tk, gp in m.groupby("ticker"):
        rr = rat[rat.ticker == tk]
        if len(rr) == 0: continue
        j = pd.merge_asof(gp.sort_values("time"), rr.sort_values("time"),
                          on="time", by="ticker", direction="backward")
        mm.append(j)
    m = pd.concat(mm, ignore_index=True)
    m = m[m.rating <= 3]
    m["mos"] = (m.fv_ps - m.Price) / m.fv_ps
    # freshness: only use FV releases within 15 months of eval date (drop stale)
    m = m[(m.time - m.rel_time).dt.days <= 460]
    m["year"] = m.time.dt.year
    print(f"panel rows={len(m)}  months={m.time.dt.to_period('M').nunique()}  tickers={m.ticker.nunique()}")
    print(f"  MoS distribution: mean={m.mos.mean():+.2f} median={m.mos.median():+.2f} "
          f"%cheap(MoS>0)={100*(m.mos>0).mean():.0f}%")

    # 4) cross-sectional Spearman IC per eval month, averaged by window
    def ic_table(df, label):
        print(f"\n  {label}: (cross-sectional Spearman IC of MoS vs forward return, monthly, then averaged)")
        for tgt in ["profit_1M","profit_2M","profit_3M"]:
            ics = df.groupby("time").apply(lambda x: spearman_ic(x.mos.values, x[tgt].values)).dropna()
            if len(ics) == 0:
                print(f"    {tgt}: no data"); continue
            mean_ic = ics.mean(); t = mean_ic / (ics.std()/np.sqrt(len(ics))) if ics.std()>0 else np.nan
            hit = (ics > 0).mean()
            print(f"    {tgt}: meanIC={mean_ic:+.4f}  t={t:+.2f}  hit%={100*hit:.0f}  (n_months={len(ics)})")
    ic_table(m, "ALL 2014-2026")
    ic_table(m[m.year <= 2019], "IS 2014-2019")
    ic_table(m[m.year >= 2020], "OOS 2020-2026")
    # decile monotonicity (ALL): forward return by MoS quintile
    m["q"] = m.groupby("time").mos.transform(lambda x: pd.qcut(x, min(5, x.nunique()), labels=False, duplicates="drop"))
    dec = m.assign(p2=m.profit_2M.clip(-100, 200)).groupby("q").p2.mean()
    print("\n  profit_2M by MoS quintile (0=most rich .. 4=cheapest):")
    print("   ", {int(k): round(float(v),2) for k,v in dec.items()})
    return m


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--calib", action="store_true")
    ap.add_argument("--ic", action="store_true")
    a = ap.parse_args()
    do_all = not (a.calib or a.ic)
    if a.calib or do_all: run_calibration()
    if a.ic or do_all: run_ic()
