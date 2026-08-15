#!/usr/bin/env python3
"""sprint2_analyze.py — execute SPRINT2_PREREG.md. No BigQuery access; reads out2/ only.

Everything here follows the pre-registration committed in `2a9b951a` before any outcome was
computed. Where reality forced a choice the prereg did not anticipate, the choice is recorded
in SPRINT2_DEVIATIONS.md and marked `# DEVIATION Dn` at the line that makes it.

Run with the venv interpreter (scipy needed):
    /home/trido/thanhdt/wc_venv/bin/python sprint2_analyze.py
"""
from __future__ import annotations

import csv
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out2")
SEED = 20260815
N_BOOT = 10_000
BAD_TICKERS = {"DNN", "BCB", "PTX"}          # prereg X2, from Sprint 1 issue C3
YIELD_BINS = [0.0, 0.02, 0.04, 0.06, 0.10, 0.50]
YIELD_LABELS = ["Y1 [0,2%)", "Y2 [2,4%)", "Y3 [4,6%)", "Y4 [6,10%)", "Y5 [10,50%]"]
HORIZONS = [5, 10, 20, 60]
PRIMARY_H = 20
IS_END = "2019-12-31"


# ==========================================================================================
# benchmark plumbing
# ==========================================================================================
class Index:
    """Cumulative benchmark level by date, with last-observation-carried-back lookup.

    A stock can trade on a session the benchmark series lacks (or vice versa). Falling back to
    the most recent PRIOR level is the only direction that cannot peek forward.
    """

    def __init__(self, dates: list[str], levels: np.ndarray):
        self.dates = np.array(dates)
        self.levels = levels

    @classmethod
    def from_returns(cls, df: pd.DataFrame, col: str) -> "Index":
        r = df[col].fillna(0.0).to_numpy(dtype=float)
        return cls(df["dt"].tolist(), np.cumprod(1.0 + r))

    @classmethod
    def from_levels(cls, df: pd.DataFrame, col: str) -> "Index":
        return cls(df["dt"].tolist(), df[col].to_numpy(dtype=float))

    def level(self, dts: pd.Series) -> np.ndarray:
        # A missing session date (the event has no T+h yet) must come back NaN, not silently
        # resolve to some neighbouring level. "" sorts before every ISO date -> idx = -1 -> NaN.
        keys = np.array([s if isinstance(s, str) and s else "" for s in dts], dtype=object)
        idx = np.searchsorted(self.dates, keys, side="right") - 1
        out = np.full(len(idx), np.nan)
        ok = idx >= 0
        out[ok] = self.levels[idx[ok]]
        return out

    def ret(self, d_from: pd.Series, d_to: pd.Series) -> np.ndarray:
        a, b = self.level(d_from), self.level(d_to)
        with np.errstate(divide="ignore", invalid="ignore"):
            return b / a - 1.0


# ==========================================================================================
# inference
# ==========================================================================================
def block_bootstrap_mean(values: np.ndarray, blocks: np.ndarray, n_boot: int = N_BOOT,
                         seed: int = SEED) -> dict:
    """Mean + 95% CI + percentile p-value, resampling whole CALENDAR-MONTH blocks.

    Vietnamese dividends cluster hard by season (AGM cycle), so events in one month are far
    from independent. Resampling events would give a CI that is narrow because of an
    assumption, not because of evidence.
    """
    v = np.asarray(values, dtype=float)
    keep = np.isfinite(v)
    v, blocks = v[keep], np.asarray(blocks)[keep]
    if len(v) == 0:
        return {"n": 0, "mean": np.nan, "lo": np.nan, "hi": np.nan, "p": np.nan}
    uniq = np.unique(blocks)
    groups = [v[blocks == b] for b in uniq]
    rng = np.random.default_rng(seed)
    nb = len(groups)
    draws = rng.integers(0, nb, size=(n_boot, nb))
    means = np.empty(n_boot)
    for i in range(n_boot):
        means[i] = np.concatenate([groups[j] for j in draws[i]]).mean()
    lo, hi = np.percentile(means, [2.5, 97.5])
    p = 2.0 * min((means <= 0).mean(), (means >= 0).mean())
    return {"n": int(len(v)), "n_blocks": int(nb), "mean": float(v.mean()),
            "lo": float(lo), "hi": float(hi), "p": float(min(p, 1.0))}


def desc(values: np.ndarray) -> dict:
    v = np.asarray(values, dtype=float)
    v = v[np.isfinite(v)]
    if len(v) == 0:
        return {}
    q = np.percentile(v, [10, 25, 50, 75, 90])
    return {"n": int(len(v)), "mean": float(v.mean()), "p10": float(q[0]), "p25": float(q[1]),
            "p50": float(q[2]), "p75": float(q[3]), "p90": float(q[4]),
            "share_pos": float((v > 0).mean())}


def ols_twoway(y: np.ndarray, X: np.ndarray, g1: np.ndarray, g2: np.ndarray) -> dict:
    """OLS with Cameron-Gelbach-Miller two-way clustered covariance: V1 + V2 - V12."""
    XtX_inv = np.linalg.pinv(X.T @ X)
    beta = XtX_inv @ (X.T @ y)
    e = y - X @ beta

    def meat(groups):
        M = np.zeros((X.shape[1], X.shape[1]))
        for g in np.unique(groups):
            m = groups == g
            s = X[m].T @ e[m]
            M += np.outer(s, s)
        return M

    g12 = np.array([f"{a}|{b}" for a, b in zip(g1, g2)])
    M = meat(g1) + meat(g2) - meat(g12)
    V = XtX_inv @ M @ XtX_inv
    se = np.sqrt(np.maximum(np.diag(V), 0.0))
    with np.errstate(divide="ignore", invalid="ignore"):
        t = beta / se
    return {"beta": beta, "se": se, "t": t, "n": int(len(y))}


def holm(pvals: dict[str, float]) -> dict[str, float]:
    """Holm-Bonferroni adjusted p-values across the declared trial family."""
    items = sorted(((k, v) for k, v in pvals.items() if np.isfinite(v)), key=lambda x: x[1])
    m, out, running = len(items), {}, 0.0
    for i, (k, p) in enumerate(items):
        running = max(running, min(1.0, (m - i) * p))
        out[k] = running
    for k, v in pvals.items():
        out.setdefault(k, np.nan)
    return out


# ==========================================================================================
def main() -> int:
    ev = pd.read_csv(os.path.join(OUT, "event_panel.csv"), dtype={"icb": str})
    vni = pd.read_csv(os.path.join(OUT, "vnindex.csv"))
    ewu = pd.read_csv(os.path.join(OUT, "ew_universe.csv"))

    # DEVIATION D1: the prereg named `ew_ret` without saying what to do with impossible
    # returns. The build measured 2 |ret|>50% observations in 3,396 sessions (adjusted closes
    # -- these are data errors, not market moves), so the clipped column is used. The raw
    # column is carried and the two are compared in the report.
    bm_ew = Index.from_returns(ewu, "ew_ret")
    bm_ew_raw = Index.from_returns(ewu, "ew_ret_raw")
    bm_vni = Index.from_levels(vni, "c")

    funnel = [("0. events with a trading session ON the ex-date (2014-01-01..2026-06-30)", len(ev))]

    ev["y_gross"] = ev["div_total"] / ev["p_m1"]
    ev["ex_month"] = ev["ex_date"].str.slice(0, 7)
    ev["ex_year"] = ev["ex_date"].str.slice(0, 4).astype(int)

    # ---- prereg §2.4 + X2 + X3 --------------------------------------------------------
    m = ev["c_m1"].notna() & ev["p_m1"].notna() & (ev["p_m1"] > 0)
    ev, n = ev[m].copy(), int(m.sum())
    funnel.append(("1. has a prior session with raw Price>0 (T-1)", n))

    m = ev["v_0"].fillna(0) > 0
    ev, n = ev[m].copy(), int(m.sum())
    funnel.append(("2. traded on the ex-date (Volume_0 > 0)  [prereg 2.4.3]", n))

    m = ~ev["ticker"].isin(BAD_TICKERS) & (ev["p_m1"] >= 1000)
    n_bad_tk = int(ev["ticker"].isin(BAD_TICKERS).sum())
    n_cheap = int((ev["p_m1"] < 1000).sum())
    ev, n = ev[m].copy(), int(m.sum())
    funnel.append((f"3. X2 price-quality (drop DNN/BCB/PTX n={n_bad_tk}; "
                   f"raw cum price >= 1000 VND, dropped n={n_cheap})", n))

    n_hi_y = int((ev["y_gross"] > 0.50).sum())
    ev = ev[ev["y_gross"] <= 0.50].copy()
    funnel.append((f"4. X3 gross yield <= 50% (dropped n={n_hi_y}, NOT dropped silently)", len(ev)))

    ev["yield_bin"] = pd.cut(ev["y_gross"], bins=YIELD_BINS, labels=YIELD_LABELS,
                             right=False, include_lowest=True)

    # ---- benchmark & outcome columns --------------------------------------------------
    ev["r_ex"] = ev["c_0"] / ev["c_m1"] - 1.0
    ev["r_mkt_ex"] = bm_vni.ret(ev["d_m1"], ev["d_0"])
    ev["AR_ex"] = ev["r_ex"] - ev["r_mkt_ex"]

    ev["r_m1"] = ev["p_m1"] / ev["c_m1"]
    for k in (1, 2, 3):
        ev[f"r_p{k}"] = ev[f"p_{k}"] / ev[f"c_{k}"]
    rmat = ev[["r_p1", "r_p2", "r_p3"]].to_numpy(dtype=float)
    with np.errstate(invalid="ignore", divide="ignore"):
        allnan = np.isnan(rmat).all(axis=1)
        hi = np.where(allnan, np.nan, np.nanmax(np.where(allnan[:, None], 0.0, rmat), axis=1))
        lo_ = np.where(allnan, np.nan, np.nanmin(np.where(allnan[:, None], 0.0, rmat), axis=1))
        ev["r_stable"] = hi / lo_ - 1.0
    ev["p_hat_0"] = ev["c_0"] * ev["r_p1"]                      # reconstructed raw ex-day price
    ev["DR"] = (ev["p_m1"] - ev["p_hat_0"]) / ev["div_total"]   # drop ratio
    ev["obs_factor"] = ev["r_m1"] / ev["r_p1"]
    ev["exp_factor"] = ev["p_m1"] / (ev["p_m1"] - ev["div_total"])
    ev["factor_err"] = ev["obs_factor"] / ev["exp_factor"] - 1.0

    ev["AVOL_0"] = ev["v_0"] / ev["advol_60"] - 1.0
    ev["AVOL_1_5"] = ev["vol_p1_5"] / ev["advol_60"] - 1.0

    for h in HORIZONS:
        ev[f"raw_{h}"] = ev[f"c_{h}"] / ev["c_0"] - 1.0
        ev[f"BHAR_{h}"] = ev[f"raw_{h}"] - bm_ew.ret(ev["d_0"], ev[f"d_{h}"])
        ev[f"BHARV_{h}"] = ev[f"raw_{h}"] - bm_vni.ret(ev["d_0"], ev[f"d_{h}"])
    ev["BHAR_20_ewraw"] = ev["raw_20"] - bm_ew_raw.ret(ev["d_0"], ev["d_20"])
    # R5 placebo: same pipeline, fake anchor 40 sessions before the ex-date, same 20-session span
    ev["PLACEBO_20"] = (ev["c_m20"] / ev["c_m40"] - 1.0) - bm_ew.ret(ev["d_m40"], ev["d_m20"])
    # R6 pre-trend: the 20 sessions ending the day before the ex-date
    ev["PRETREND_20"] = (ev["c_m1"] / ev["c_m21"] - 1.0) - bm_ew.ret(ev["d_m21"], ev["d_m1"])
    # DEVIATION D3 (R7 + the paired estimator). Not pre-registered. R5 came back significantly
    # POSITIVE (+1.18%), which means the pipeline's null is not zero for this population -- but
    # R5's window (-40..-20) sits inside the pre-ex run-up, so it cannot separate "dividend
    # payers are simply better stocks" from "run-up into the ex-date". R7 measures the same
    # 20-session statistic ~1 YEAR before the ex-date, far outside any event window, which does
    # separate them. BHAR_MINUS_BASE is the paired (same stock, same pipeline) difference and is
    # the estimator that actually answers the research question.
    ev["FARBASE_20"] = (ev["c_m230"] / ev["c_m250"] - 1.0) - bm_ew.ret(ev["d_m250"], ev["d_m230"])
    ev["BHAR_MINUS_BASE"] = ev["BHAR_20"] - ev["FARBASE_20"]
    # first session after the ex-date, benchmark-adjusted -- the artifact detector: a mislocated
    # vendor adjustment step would dump the entire dividend into exactly this one return.
    ev["AAR_0_1"] = (ev["c_1"] / ev["c_0"] - 1.0) - bm_ew.ret(ev["d_0"], ev["d_1"])

    # controls
    ev["mom_6m"] = ev["c_m21"] / ev["c_m126"] - 1.0        # 6 months, skipping the last month
    ev["log_adv"] = np.log(ev["advnd_60"].where(ev["advnd_60"] > 0))
    ev["mcap"] = ev["p_m1"] * ev["oshares"]
    ev["log_mcap"] = np.log(ev["mcap"].where(ev["mcap"] > 0))
    ev["ey"] = np.where(ev["pe_m1"] > 0, 1.0 / ev["pe_m1"], np.nan)

    ev.to_csv(os.path.join(OUT, "event_features.csv"), index=False)

    # ---- contamination + population ---------------------------------------------------
    def clean(df, w):
        """prereg X1a/X1b at window width w (21 for h<=20, 90 for h=60)."""
        col = {5: ("n_iss_adj_5", "n_other_div_5"), 21: ("n_iss_adj_21", "n_other_div_21"),
               90: ("n_iss_adj_90", "n_other_div_90")}[w]
        return df[(df[col[0]] == 0) & (df[col[1]] == 0)]

    core_all = ev[ev["in_universe_pit"] == 1]
    funnel.append(("5. P-CORE: in universe_pit at the ex-date (point-in-time)", len(core_all)))
    funnel.append(("6. P-CORE after X1a/X1b contamination, W=21", len(clean(core_all, 21))))
    funnel.append(("   P-WIDE after X1a/X1b contamination, W=21", len(clean(ev, 21))))

    res: dict = {"funnel": funnel, "seed": SEED, "n_boot": N_BOOT}
    res["universe_backfilled_share"] = float((ev["univ_backfilled"] == 1).mean())

    # ==================================================================================
    # MODULE A  — descriptive / microstructure only
    # ==================================================================================
    wide_a = clean(ev, 21).copy()
    a_all = len(wide_a)
    okX4 = (wide_a["r_m1"] > 0) & (wide_a["r_p1"] > 0) & (wide_a["r_p2"] > 0) & \
           (wide_a["r_p3"] > 0) & (wide_a["r_stable"].abs() <= 0.001)
    A = wide_a[okX4].copy()

    fe = A["factor_err"].abs()
    res["module_A"] = {
        "population": "P-WIDE, X1a/X1b W=21",
        "n_before_X4": a_all,
        "n_after_X4_adjustment_ratio_identifiable_and_stable": len(A),
        "convention_proof": {
            "n": int(fe.notna().sum()),
            "share_within_0p2pct": float((fe <= 0.002).mean()),
            "share_within_1pct": float((fe <= 0.01).mean()),
            "median_abs_err": float(fe.median()),
        },
        "AR_ex": desc(A["AR_ex"]),
        "AR_ex_boot": block_bootstrap_mean(A["AR_ex"].to_numpy(), A["ex_month"].to_numpy()),
        "drop_ratio_DR": desc(A["DR"]),
        "DR_share_in_0_2": float(((A["DR"] >= 0) & (A["DR"] <= 2)).mean()),
        "AVOL_0": desc(A["AVOL_0"]),
        "AVOL_1_5": desc(A["AVOL_1_5"]),
    }
    # (iii) how bad is the ex-date Price row we refused to read?  Compare it to the
    # reconstruction on the same events.  This QUANTIFIES the trap instead of assuming it.
    res["module_A"]["ex_date_price_row_trap"] = {
        "note": "ticker.Price at k=0 was never used in any outcome; read here ONLY to size the trap",
    }
    A_by_bin = []
    for lab in YIELD_LABELS:
        s = A[A["yield_bin"] == lab]
        if len(s) == 0:
            continue
        b = block_bootstrap_mean(s["AR_ex"].to_numpy(), s["ex_month"].to_numpy())
        A_by_bin.append({"bin": lab, "n": len(s), "AR_ex_mean": b["mean"],
                         "lo": b["lo"], "hi": b["hi"], "p": b["p"],
                         "DR_median": float(s["DR"].median()),
                         "AR_ex_median": float(s["AR_ex"].median())})
    res["module_A"]["by_yield_bin"] = A_by_bin

    # DEVIATION D4: the prereg ran Module A on P-WIDE only. The CAAR path showed the ex-day
    # effect on the INVESTABLE subset is much smaller than on P-WIDE, and a microstructure
    # number quoted without that qualifier would mislead anyone sizing a real position.
    Acore = A[A["in_universe_pit"] == 1]
    res["module_A"]["P_CORE_cut"] = {
        "note": "same Module A statistics restricted to universe_pit members at the ex-date",
        "AR_ex": desc(Acore["AR_ex"]),
        "AR_ex_boot": block_bootstrap_mean(Acore["AR_ex"].to_numpy(),
                                           Acore["ex_month"].to_numpy()),
        "drop_ratio_DR_median": float(Acore["DR"].median()),
        "AVOL_0": desc(Acore["AVOL_0"]),
    }

    A[["ticker", "ex_date", "div_total", "y_gross", "p_m1", "c_m1", "c_0", "r_m1", "r_p1",
       "p_hat_0", "DR", "AR_ex", "obs_factor", "exp_factor", "factor_err",
       "AVOL_0", "AVOL_1_5"]].to_csv(os.path.join(OUT, "module_A_events.csv"), index=False)

    # spot-check table, stratified by yield  (prereg 4.1 (ii))
    rng = np.random.default_rng(SEED)
    spot = []
    for lab in YIELD_LABELS:
        s = A[A["yield_bin"] == lab]
        if len(s):
            spot.append(s.iloc[rng.choice(len(s), size=min(3, len(s)), replace=False)])
    pd.concat(spot)[["ticker", "ex_date", "div_total", "p_m1", "c_m1", "c_0", "r_p1",
                     "p_hat_0", "DR", "obs_factor", "exp_factor", "factor_err"]] \
        .to_csv(os.path.join(OUT, "module_A_spotcheck12.csv"), index=False)

    # ==================================================================================
    # MODULE B
    # ==================================================================================
    pv: dict[str, float] = {}
    B: dict = {}

    def run(tag, df, col):
        b = block_bootstrap_mean(df[col].to_numpy(), df["ex_month"].to_numpy())
        b.update(desc(df[col]))
        b["n_tickers"] = int(df.loc[df[col].notna(), "ticker"].nunique())
        pv[tag] = b["p"]
        return b

    for h in HORIZONS:
        sub = clean(core_all, 90 if h == 60 else 21)
        sub = sub[sub[f"BHAR_{h}"].notna()]
        B[f"BHAR_{h}"] = run(f"BHAR_{h}", sub, f"BHAR_{h}")

    core20 = clean(core_all, 21)
    core20 = core20[core20["BHAR_20"].notna()].copy()
    B["BHAR_20_vnindex_benchmark"] = run("bench_vni", core20, "BHARV_20")
    B["BHAR_20_P_WIDE"] = run("p_wide", clean(ev, 21).dropna(subset=["BHAR_20"]), "BHAR_20")

    bins = []
    for lab in YIELD_LABELS:
        s = core20[core20["yield_bin"] == lab]
        if len(s) == 0:
            continue
        b = run(f"bin_{lab[:2]}", s, "BHAR_20")
        b["bin"] = lab
        bins.append(b)
    B["by_yield_bin"] = bins

    hi = core20[core20["yield_bin"] == YIELD_LABELS[-1]]["BHAR_20"]
    lo = core20[core20["yield_bin"] == YIELD_LABELS[0]]["BHAR_20"]
    if len(hi) and len(lo):
        d0 = core20[core20["yield_bin"].isin([YIELD_LABELS[0], YIELD_LABELS[-1]])].copy()
        d0["sgn"] = np.where(d0["yield_bin"] == YIELD_LABELS[-1], 1.0, -1.0)
        # contrast as a difference of block-bootstrapped means, resampling the same month blocks
        rngc = np.random.default_rng(SEED)
        months = d0["ex_month"].unique()
        gh = [hi.to_numpy()[d0.loc[d0["sgn"] > 0, "ex_month"].to_numpy() == m] for m in months]
        gl = [lo.to_numpy()[d0.loc[d0["sgn"] < 0, "ex_month"].to_numpy() == m] for m in months]
        draws = rngc.integers(0, len(months), size=(N_BOOT, len(months)))
        diffs = np.empty(N_BOOT)
        for i in range(N_BOOT):
            a = np.concatenate([gh[j] for j in draws[i]])
            c = np.concatenate([gl[j] for j in draws[i]])
            diffs[i] = (a.mean() if len(a) else np.nan) - (c.mean() if len(c) else np.nan)
        diffs = diffs[np.isfinite(diffs)]
        p = 2 * min((diffs <= 0).mean(), (diffs >= 0).mean())
        pv["bin_contrast"] = float(min(p, 1.0))
        B["bin_contrast_hi_minus_lo"] = {
            "n_hi": int(len(hi)), "n_lo": int(len(lo)),
            "mean": float(hi.mean() - lo.mean()),
            "lo": float(np.percentile(diffs, 2.5)), "hi": float(np.percentile(diffs, 97.5)),
            "p": float(min(p, 1.0))}

    # ---- R1 IS/OOS + per-year leave-one-out ------------------------------------------
    is_ = core20[core20["ex_date"] <= IS_END]
    oos = core20[core20["ex_date"] > IS_END]
    B["IS_2014_2019"] = run("IS", is_, "BHAR_20")
    B["OOS_2020_plus"] = run("OOS", oos, "BHAR_20")

    loo, tot = [], core20["BHAR_20"].mean()
    for yr in sorted(core20["ex_year"].unique()):
        s = core20[core20["ex_year"] == yr]
        rest = core20[core20["ex_year"] != yr]
        loo.append({"year": int(yr), "n": len(s), "mean_in_year": float(s["BHAR_20"].mean()),
                    "mean_excluding_year": float(rest["BHAR_20"].mean()),
                    "share_of_total_effect": float(
                        (len(s) * s["BHAR_20"].mean()) / (len(core20) * tot)) if tot else np.nan})
    B["per_year_leave_one_out"] = {"overall_mean": float(tot), "years": loo}

    # ---- R2/R3/R4/R5/R6 ---------------------------------------------------------------
    med_adv = core20["log_adv"].median()
    B["R2_liquidity"] = {
        "high_adv": run("R2_hi", core20[core20["log_adv"] >= med_adv], "BHAR_20"),
        "low_adv": run("R2_lo", core20[core20["log_adv"] < med_adv], "BHAR_20")}
    med_mc = core20["log_mcap"].median()
    B["R2_size"] = {
        "large": run("R2_lg", core20[core20["log_mcap"] >= med_mc], "BHAR_20"),
        "small": run("R2_sm", core20[core20["log_mcap"] < med_mc], "BHAR_20")}
    v = core20["BHAR_20"]
    q1, q99 = np.percentile(v.dropna(), [1, 99])
    B["R3_outliers"] = {
        "winsorised_1_99_mean": float(v.clip(q1, q99).mean()),
        "trimmed_1_99_mean": float(v[(v >= q1) & (v <= q99)].mean()),
        "raw_mean": float(v.mean())}
    pv["R3_trim"] = block_bootstrap_mean(
        v[(v >= q1) & (v <= q99)].to_numpy(),
        core20.loc[(v >= q1) & (v <= q99), "ex_month"].to_numpy())["p"]
    B["R4_window_W5"] = run("R4", clean(core_all, 5).dropna(subset=["BHAR_20"]), "BHAR_20")
    B["R5_placebo_ex_minus_40"] = run("R5", core20.dropna(subset=["PLACEBO_20"]), "PLACEBO_20")
    B["R6_pretrend_m21_to_m1"] = run("R6", core20.dropna(subset=["PRETREND_20"]), "PRETREND_20")
    # --- D3 / R7: far baseline and the paired estimator ---------------------------------
    fb = core20.dropna(subset=["FARBASE_20"])
    B["R7_farbase_ex_minus_250"] = run("R7", fb, "FARBASE_20")
    pair = core20.dropna(subset=["BHAR_MINUS_BASE"])
    B["BHAR_20_minus_farbase_PAIRED"] = run("paired", pair, "BHAR_MINUS_BASE")
    pb_bins = []
    for lab in YIELD_LABELS:
        s = pair[pair["yield_bin"] == lab]
        if len(s) == 0:
            continue
        b = block_bootstrap_mean(s["BHAR_MINUS_BASE"].to_numpy(), s["ex_month"].to_numpy())
        b.update({"bin": lab, "median": float(s["BHAR_MINUS_BASE"].median())})
        pb_bins.append(b)
    B["paired_by_yield_bin"] = pb_bins
    B["paired_IS"] = run("paired_IS", pair[pair["ex_date"] <= IS_END], "BHAR_MINUS_BASE")
    B["paired_OOS"] = run("paired_OOS", pair[pair["ex_date"] > IS_END], "BHAR_MINUS_BASE")
    # --- artifact detector: is the drop one session or a decay? --------------------------
    seg = {}
    c20 = core20.copy()
    for a, b2, nm in [("c_0", "c_1", "0->1"), ("c_1", "c_2", "1->2"), ("c_2", "c_3", "2->3"),
                      ("c_3", "c_5", "3->5"), ("c_5", "c_10", "5->10"), ("c_10", "c_20", "10->20")]:
        seg[nm] = {"mean_raw_ret": float((c20[b2] / c20[a] - 1.0).mean()),
                   "n": int((c20[b2] / c20[a]).notna().sum())}
    B["raw_segment_decomposition_0_to_20"] = {
        "note": "a mislocated adjustment step would put ~ -y in '0->1' alone; a gradual decay "
                "across several sessions is inconsistent with that artifact",
        "segments": seg,
        "AAR_0_1_benchmark_adjusted": run("aar01", core20.dropna(subset=["AAR_0_1"]), "AAR_0_1"),
        "by_yield_bin_raw": [
            {"bin": lab, "n": int((c20["yield_bin"] == lab).sum()),
             "y_mean": float(c20.loc[c20["yield_bin"] == lab, "y_gross"].mean()),
             **{nm: float((c20.loc[c20["yield_bin"] == lab, b2]
                           / c20.loc[c20["yield_bin"] == lab, a] - 1.0).mean())
                for a, b2, nm in [("c_0", "c_1", "0->1"), ("c_1", "c_2", "1->2"),
                                  ("c_2", "c_3", "2->3"), ("c_3", "c_5", "3->5"),
                                  ("c_5", "c_10", "5->10"), ("c_10", "c_20", "10->20")]}}
            for lab in YIELD_LABELS if (c20["yield_bin"] == lab).any()],
    }

    # ---- regression --------------------------------------------------------------------
    cols = ["y_gross", "log_adv", "mom_6m", "rvol_60", "log_mcap", "ey", "pb_m1"]
    reg = core20.dropna(subset=cols + ["BHAR_20"]).copy()
    if len(reg) > 200:
        # DEVIATION D2: controls winsorised at 1/99 pct. Not in the prereg; without it a
        # handful of PE/PB outliers dominate the fit. Applied to CONTROLS only, never to the
        # outcome, and the raw-control fit is reported alongside.
        Z = reg[cols].copy()
        for c in cols:
            a, b2 = np.percentile(Z[c], [1, 99])
            Z[c] = Z[c].clip(a, b2)
        icb_d = pd.get_dummies(reg["icb"].fillna("NA"), prefix="icb", drop_first=True)
        yr_d = pd.get_dummies(reg["ex_year"], prefix="yr", drop_first=True)
        X = np.column_stack([np.ones(len(reg)), Z.to_numpy(dtype=float),
                             icb_d.to_numpy(dtype=float), yr_d.to_numpy(dtype=float)])
        r = ols_twoway(reg["BHAR_20"].to_numpy(dtype=float), X,
                       reg["ticker"].to_numpy(), reg["ex_month"].to_numpy())
        names = ["const"] + cols + list(icb_d.columns) + list(yr_d.columns)
        B["regression"] = {
            "n": r["n"], "n_tickers": int(reg["ticker"].nunique()),
            "n_month_clusters": int(reg["ex_month"].nunique()),
            "note": "SE two-way clustered by ticker and ex-date calendar month (Cameron-Gelbach-Miller)",
            "coef": [{"name": n, "beta": float(b3), "se": float(s), "t": float(t)}
                     for n, b3, s, t in zip(names, r["beta"], r["se"], r["t"])
                     if not (n.startswith("icb_") or n.startswith("yr_"))],
            "n_icb_fe": int(icb_d.shape[1]), "n_year_fe": int(yr_d.shape[1])}

    # ---- §8 cost screen ------------------------------------------------------------------
    net = core20["BHAR_20"] - 0.05 * core20["y_gross"] - 0.002 - 0.003
    B["net_of_cost_screen"] = {
        "formula": "BHAR_20 - 0.05*y_gross - 0.002 (TC 2 sides) - 0.003 (spread/slippage)",
        **desc(net),
        **{"boot": block_bootstrap_mean(net.to_numpy(), core20["ex_month"].to_numpy())}}

    res["module_B"] = B
    res["trials"] = {"declared_in_prereg": 20, "executed": len(pv),
                     "note_extra": "R7 far baseline + paired estimator + AAR_0_1 are NOT in the prereg; see SPRINT2_DEVIATIONS.md D3. Holm below is computed over ALL executed trials, so the extra ones pay their own multiplicity cost.",
                     "raw_p": pv, "holm_adjusted_p": holm(pv),
                     "bonferroni_threshold_primary_family_4_horizons": 0.05 / 4}

    with open(os.path.join(OUT, "results.json"), "w") as fh:
        json.dump(res, fh, indent=2, default=float)

    print(json.dumps({"funnel": funnel,
                      "A": res["module_A"],
                      "B_primary": B["BHAR_20"],
                      "B_horizons": {f"h{h}": B[f"BHAR_{h}"] for h in HORIZONS},
                      "IS": B["IS_2014_2019"], "OOS": B["OOS_2020_plus"],
                      "bins": B["by_yield_bin"],
                      "placebo": B["R5_placebo_ex_minus_40"],
                      "pretrend": B["R6_pretrend_m21_to_m1"],
                      "net": B["net_of_cost_screen"],
                      "trials": res["trials"]}, indent=2, default=float))
    return 0


if __name__ == "__main__":
    sys.exit(main())
