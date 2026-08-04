# -*- coding: utf-8 -*-
"""2021-as-F0-outlier — empirical test of the user's rebuttal (job Taylor_20260804_061252).

Question the user raised: 2021 was VN's "F0 year" (first mass retail entry since 2006) — prices rose
regardless of company quality. If true, judging a QUALITY-RANKING rule on 2021 is a methodological
bias: any quality signal loses in an indiscriminate melt-up.

This script does NOT re-run the engine. Two independent measurement tiers, both per calendar year
2014-2026, so 2021 can be compared against every other year in the sample:

  TIER 1 — signal tier, on the ACTUAL LAG candidate pool (the events the ranking rule reorders):
    rank-IC (Spearman) between each ranking key and the realised T+5->T+30 drift (`post_ret`),
    tercile spread (top-third mean minus bottom-third mean), and the dispersion of post_ret itself.
    `post_ret` is the PEAD drift window the LAG book monetises (buy at T+5) -> analyze_earnings_reaction.py:131

  TIER 2 — market tier, from the pinned BQ cache: breadth (% of names above MA200, % of names with
    a positive calendar-year return) and cross-sectional dispersion of annual returns. An
    indiscriminate melt-up = breadth extreme AND dispersion of QUALITY-SORTED buckets collapsing.

Every number printed is computed here from raw data; nothing is copied from the prior report.
Usage: python dispersion_by_year.py
"""
import os
import pickle
import numpy as np
import pandas as pd
from scipy import stats

WC = "/home/trido/thanhdt/WorkingClaude"
CACHE = os.path.join(WC, "data/bq_cache_asof20260729_postrestate")
YEARS = list(range(2014, 2027))
pd.set_option("display.width", 220)


# ---------------------------------------------------------------- TIER 1: LAG candidate pool
def build_events():
    """Replicate the engine's LAG event panel + ranking keys EXACTLY (engine_lagrank.py:1010-1052).

    Copied structurally, not re-invented, so the pool measured here is the pool the rule reorders.
    """
    with open(os.path.join(WC, "data/earnings_surprise_data.pkl"), "rb") as f:
        fin = pickle.load(f)
    fin["Release_Date"] = pd.to_datetime(fin["Release_Date"])
    FLOOR = 1e9
    fin["exp_B_MA"] = fin[["NP_P1", "NP_P2", "NP_P3", "NP_P4"]].mean(axis=1)
    fin["surprise_B_MA"] = ((fin["NP_P0"] - fin["exp_B_MA"])
                            / np.maximum(np.abs(fin["exp_B_MA"]), FLOOR)).clip(-5, 5)

    ev = pd.read_csv(os.path.join(WC, "data/earnings_events_classified.csv"),
                     parse_dates=["Release_Date"])
    ev = ev.merge(fin[["ticker", "quarter", "Release_Date", "surprise_B_MA"]],
                  on=["ticker", "quarter", "Release_Date"], how="left")
    ev = ev.sort_values(["ticker", "Release_Date"]).reset_index(drop=True)
    ev["surprise_B_MA"] = ev["surprise_B_MA"].fillna(0)
    ev["d_NPR"] = ev.groupby("ticker")["NP_R"].diff()

    LN2, HL = np.log(2), 3.0
    ev["prior_n_good"] = 0
    ev["pa_HL3"] = np.nan
    for tk, g in ev.groupby("ticker"):
        hist = []
        for ri in g.index.tolist():
            row = ev.loc[ri]
            cur = row["Release_Date"]
            ev.at[ri, "prior_n_good"] = len(hist)
            if hist:
                da = pd.to_datetime([d for d, _ in hist])
                pa = np.array([p for _, p in hist])
                w = np.exp(-LN2 * ((cur - da).days.values / 365.25) / HL)
                ev.at[ri, "pa_HL3"] = (pa * w).sum() / w.sum() if w.sum() > 0 else np.nan
            if pd.notna(row["NP_R"]) and row["NP_R"] >= 15 and pd.notna(row["post_ret"]):
                hist.append((cur, row["post_ret"]))

    # forensic gate ON (production default LAG_FORENSIC_GATE=1); non-op filter OFF
    forx = {}
    try:
        ff = pd.read_csv(os.path.join(WC, "data/forensic_flags.csv"))
        forx = {r["ticker"]: pd.Timestamp(r["date"])
                for _, r in ff.iterrows() if str(r["severity"]).strip() == "exclude"}
    except Exception:
        pass
    ev["_forbid"] = [(tk in forx) and (rd >= forx[tk])
                     for tk, rd in zip(ev["ticker"], ev["Release_Date"])]

    m = (ev["NP_R"] >= 15) & (ev["prior_n_good"] >= 4) & (ev["pa_HL3"] >= 5) & (~ev["_forbid"])
    pool = ev[m].copy()
    pool["year"] = pool["Release_Date"].dt.year
    # expanding z-score blend, exactly as engine_lagrank._z (past-only normalisation)
    pool = pool.sort_values("Release_Date").reset_index(drop=True)
    for c in ("surprise_B_MA", "pa_HL3"):
        mu = pool[c].expanding().mean().shift(1)
        sd = pool[c].expanding().std().shift(1)
        pool["z_" + c] = ((pool[c] - mu) / sd.replace(0, np.nan)).fillna(0)
    pool["blend"] = pool["z_surprise_B_MA"] + pool["z_pa_HL3"]
    return pool


def tier1(pool):
    keys = ["surprise_B_MA", "d_NPR", "pa_HL3", "blend"]
    rows = []
    for y in YEARS:
        g = pool[(pool["year"] == y) & pool["post_ret"].notna()]
        if len(g) < 20:
            continue
        r = {"year": y, "N_ev": len(g), "N_tk": g["ticker"].nunique(),
             "post_mean": g["post_ret"].mean(), "post_med": g["post_ret"].median(),
             "post_sd": g["post_ret"].std(),
             "post_iqr": g["post_ret"].quantile(.75) - g["post_ret"].quantile(.25),
             "hit%": (g["post_ret"] > 0).mean() * 100}
        for k in keys:
            gg = g[g[k].notna()]
            if len(gg) < 20:
                r["IC_" + k] = np.nan
                r["T31_" + k] = np.nan
                continue
            ic = stats.spearmanr(gg[k], gg["post_ret"]).statistic
            r["IC_" + k] = ic
            try:
                tt = pd.qcut(gg[k].rank(method="first"), 3, labels=[1, 2, 3])
                mt = gg.groupby(tt, observed=True)["post_ret"].mean()
                r["T31_" + k] = mt.get(3, np.nan) - mt.get(1, np.nan)
            except Exception:
                r["T31_" + k] = np.nan
        rows.append(r)
    return pd.DataFrame(rows).set_index("year")


# ---------------------------------------------------------------- TIER 2: market breadth
def tier2():
    """Breadth + cross-sectional dispersion per year, from the pinned cache.

    Universe filter: a real liquidity floor (Volume_3M_P50 >= 20k shares AND a price) so the
    illiquid tail cannot manufacture fake dispersion. Same spirit as the DT5G breadth guard's
    >=100-name requirement.
    """
    rows = []
    for y in YEARS:
        p = os.path.join(CACHE, "ticker", f"{y}.parquet")
        if not os.path.exists(p):
            continue
        d = pd.read_parquet(p, columns=["time", "ticker", "Close", "Price", "Volume",
                                        "Volume_3M_P50", "MA200", "PE", "ROE_Min3Y"])
        d["time"] = pd.to_datetime(d["time"])
        d = d[d["Close"].notna() & (d["Close"] > 0)]
        liq = d.groupby("ticker")["Volume_3M_P50"].median()
        keep = liq[liq >= 20000].index
        d = d[d["ticker"].isin(keep)]
        if d["ticker"].nunique() < 50:
            continue
        # breadth: % above MA200, averaged over the year's sessions
        dm = d[d["MA200"].notna()]
        br = dm.groupby("time").apply(lambda x: (x["Close"] > x["MA200"]).mean() * 100,
                                      include_groups=False)
        # calendar-year return per name (needs >=200 sessions to avoid partial-listing noise)
        g = d.sort_values("time").groupby("ticker")
        n = g["Close"].size()
        ret = (g["Close"].last() / g["Close"].first() - 1) * 100
        ret = ret[n >= 200]
        # quality sort: median PE within the year (low PE = cheap/value axis, the dominant 8L factor)
        pe = d[(d["PE"] > 0) & (d["PE"] < 200)].groupby("ticker")["PE"].median()
        roe = d.groupby("ticker")["ROE_Min3Y"].median()
        common = ret.index.intersection(pe.index)
        q31 = np.nan
        if len(common) >= 60:
            sub = pd.DataFrame({"ret": ret.loc[common], "pe": pe.loc[common]})
            t = pd.qcut(sub["pe"].rank(method="first"), 3, labels=[1, 2, 3])
            mt = sub.groupby(t, observed=True)["ret"].mean()
            q31 = mt.get(1, np.nan) - mt.get(3, np.nan)   # cheap minus expensive
        rq = np.nan
        cr = ret.index.intersection(roe[roe.notna()].index)
        if len(cr) >= 60:
            rq = stats.spearmanr(roe.loc[cr], ret.loc[cr]).statistic
        rows.append({"year": y, "N_names": int(ret.size),
                     "breadth_MA200_mean%": br.mean(), "breadth_MA200_max%": br.max(),
                     "pos_ret%": (ret > 0).mean() * 100,
                     "ret_mean%": ret.mean(), "ret_med%": ret.median(),
                     "ret_sd%": ret.std(),
                     "ret_iqr%": ret.quantile(.75) - ret.quantile(.25),
                     "cheapPE_minus_exp%": q31, "IC_ROEmin_ret": rq,
                     "turnover_Bvnd": float((d["Volume"] * d["Price"]).sum() / 1e9)})
    return pd.DataFrame(rows).set_index("year")


if __name__ == "__main__":
    pool = build_events()
    print(f"LAG candidate pool (gate NP_R>=15 & prior_n_good>=4 & pa_HL3>=5 & forensic): "
          f"{len(pool)} events, {pool['ticker'].nunique()} names, "
          f"{pool['Release_Date'].min().date()} -> {pool['Release_Date'].max().date()}\n")

    t1 = tier1(pool)
    print("=== TIER 1 — LAG candidate pool, per RELEASE year "
          "(post_ret = realised T+5->T+30 drift, %) ===")
    print(t1[["N_ev", "N_tk", "post_mean", "post_med", "post_sd", "post_iqr", "hit%"]].round(2))
    print("\n  rank-IC (Spearman) of each ranking key vs realised drift:")
    print(t1[[c for c in t1.columns if c.startswith("IC_")]].round(3))
    print("\n  tercile spread top-minus-bottom of realised drift (pp):")
    print(t1[[c for c in t1.columns if c.startswith("T31_")]].round(2))

    t2 = tier2()
    print("\n=== TIER 2 — market-wide breadth & dispersion "
          "(liquid universe, Volume_3M_P50>=20k) ===")
    print(t2.round(2))

    t1.to_csv("tier1_lagpool_by_year.csv")
    t2.to_csv("tier2_market_by_year.csv")
    print("\nwrote tier1_lagpool_by_year.csv / tier2_market_by_year.csv")
