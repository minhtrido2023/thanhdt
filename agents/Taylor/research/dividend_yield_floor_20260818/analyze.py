#!/usr/bin/env python3
"""analyze.py — Test A / Test B / robustness for the dividend yield floor (PREREG.md §5-§9).

Everything here is pre-registered. Where reality forced a choice the prereg had not pinned
down, the line carries a `# DEVIATION Dn` marker and the same id appears in DEVIATIONS.md.

The inference helpers (`Index`, `block_bootstrap_mean`, `ols_twoway`, `desc`, `_loo`, `holm`)
are copied VERBATIM from Sprint 2's `corp_action_program_20260815/sprint2_analyze.py`, per
PREREG §8 ("reuse, do not rewrite"). They are copied rather than imported because that file
lives in a git worktree that can be removed; `selfcheck.py` T1 re-derives the two-way t-stat
from first principles to prove the copy still behaves.
"""
from __future__ import annotations

import gzip
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from deposit_rate_vn import merge_deposit  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

SEED = 20260818
N_BOOT = 10_000
BAD_TICKERS = {"DNN", "BCB", "PTX"}      # PREREG §4.1 item 5 (Sprint 1 issue C3)
HORIZONS = [20, 60, 120]
PRIMARY_H = 60                            # PREREG §5
IS_END = "2019-12-31"                     # PREREG §8
FIXED_THR = [5.0, 6.0, 7.0, 8.0]          # PREREG §7.1 — the arbiters
MIN_HIST_DAYS = 1095                      # PREREG §4.1 item 3
OVERLAP_SESSIONS = 120                    # PREREG §4.3
CAUSE_LAG = 21                            # PREREG §5.1
PLACEBO_LAG = 250                         # PREREG §8
NEAR_LO, NEAR_HI = 0.97, 1.03             # PREREG §6
RVOL_LO, RVOL_HI = 0.8, 1.25              # PREREG §6
MAX_CONTROLS = 3                          # PREREG §6


# ==========================================================================================
# inference plumbing — VERBATIM from sprint2_analyze.py (PREREG §8)
# ==========================================================================================
class Index:
    """Cumulative benchmark level by date, with last-observation-carried-back lookup."""

    def __init__(self, dates, levels):
        self.dates = np.array(dates)
        self.levels = levels

    @classmethod
    def from_returns(cls, df: pd.DataFrame, col: str) -> "Index":
        r = df[col].fillna(0.0).to_numpy(dtype=float)
        return cls(df["dt"].tolist(), np.cumprod(1.0 + r))

    def level(self, dts) -> np.ndarray:
        keys = np.array([s if isinstance(s, str) and s else "" for s in dts], dtype=object)
        idx = np.searchsorted(self.dates, keys, side="right") - 1
        out = np.full(len(idx), np.nan)
        ok = idx >= 0
        out[ok] = self.levels[idx[ok]]
        return out

    def ret(self, d_from, d_to) -> np.ndarray:
        a, b = self.level(d_from), self.level(d_to)
        with np.errstate(divide="ignore", invalid="ignore"):
            return b / a - 1.0


def block_bootstrap_mean(values, blocks, n_boot: int = N_BOOT, seed: int = SEED) -> dict:
    """Mean + 95% CI + percentile p-value, resampling whole CALENDAR-MONTH blocks."""
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


def desc(values) -> dict:
    v = np.asarray(values, dtype=float)
    v = v[np.isfinite(v)]
    if len(v) == 0:
        return {}
    q = np.percentile(v, [10, 25, 50, 75, 90])
    return {"n": int(len(v)), "mean": float(v.mean()), "p10": float(q[0]), "p25": float(q[1]),
            "p50": float(q[2]), "p75": float(q[3]), "p90": float(q[4]),
            "share_pos": float((v > 0).mean())}


def ols_twoway(y, X, g1, g2) -> dict:
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


def _loo(df, col: str, ycol: str = "year") -> dict:
    """Per-year leave-one-out: is one year carrying the whole effect? (PREREG §7.3)"""
    d = df[df[col].notna()]
    if not len(d):
        return {}
    tot = d[col].mean()
    years = []
    for yr in sorted(d[ycol].unique()):
        s, rest = d[d[ycol] == yr], d[d[ycol] != yr]
        years.append({"year": int(yr), "n": int(len(s)),
                      "mean_in_year": float(s[col].mean()),
                      "mean_excluding_year": float(rest[col].mean()) if len(rest) else np.nan,
                      "share_of_total_effect": float(
                          (len(s) * s[col].mean()) / (len(d) * tot)) if tot else np.nan})
    carrier = max(years, key=lambda r: abs(r["share_of_total_effect"])) if years else None
    return {"overall_mean": float(tot), "years": years,
            "largest_carrier_year": carrier["year"] if carrier else None,
            "largest_carrier_share": carrier["share_of_total_effect"] if carrier else None,
            "sign_flips_when_any_single_year_excluded": bool(
                any(np.sign(r["mean_excluding_year"]) != np.sign(tot) for r in years)),
            "n_years": len(years)}


def stat_block(df: pd.DataFrame, col: str) -> dict:
    """The one place a headline number is produced: bootstrap CI + two-way cluster t."""
    d = df[np.isfinite(df[col])]
    if len(d) == 0:
        return {"n": 0}
    bs = block_bootstrap_mean(d[col].to_numpy(), d["ym"].to_numpy())
    ols = ols_twoway(d[col].to_numpy(dtype=float), np.ones((len(d), 1)),
                     d["ticker"].to_numpy(), d["ym"].to_numpy())
    return {"n": int(len(d)), "n_tickers": int(d["ticker"].nunique()),
            "n_months": int(d["ym"].nunique()),
            "mean": float(d[col].mean()), "median": float(d[col].median()),
            "ci_lo": bs["lo"], "ci_hi": bs["hi"], "p_boot": bs["p"],
            "t_cluster": float(ols["t"][0]), "se_cluster": float(ols["se"][0])}


def split_stats(df: pd.DataFrame, col: str) -> dict:
    out = {"all": stat_block(df, col)}
    out["IS"] = stat_block(df[df["dt"] <= IS_END], col)
    out["OOS"] = stat_block(df[df["dt"] > IS_END], col)
    return out


# ==========================================================================================
# load
# ==========================================================================================
def load() -> tuple:
    with gzip.open(os.path.join(OUT, "panel.csv.gz"), "rt") as fh:
        p = pd.read_csv(fh, dtype={"ticker": str, "dt": str, "icb": str,
                                   "d_p20": str, "d_p60": str, "d_p120": str})
    for c in ["si", "close", "price", "low", "high", "volume", "pe", "pb", "dy", "ret",
              "rvol60", "advnd60", "c_p20", "c_p60", "c_p120", "minc60", "maxc60",
              "n_fwd60", "div0", "n0", "n1", "n2", "n3", "n4", "is_exdate"]:
        p[c] = pd.to_numeric(p[c], errors="coerce")
    for c in ["d_p20", "d_p60", "d_p120"]:
        p[c] = p[c].fillna("")

    bench = pd.read_csv(os.path.join(OUT, "bench_ew.csv"), dtype={"dt": str})
    idx = Index.from_returns(bench, "ew_ret")
    state = pd.read_csv(os.path.join(OUT, "dt5g.csv"), dtype={"dt": str})
    first = pd.read_csv(os.path.join(OUT, "first_dt.csv"), dtype={"ticker": str,
                                                                 "first_dt": str})
    return p, idx, state, first


def prepare(p: pd.DataFrame, idx: Index, state: pd.DataFrame,
            first: pd.DataFrame) -> pd.DataFrame:
    p = p.sort_values(["ticker", "si"], kind="mergesort").reset_index(drop=True)

    # --- deposit rate, as-of (PIT within the limits documented in PREREG §1.1) --------------
    p["time"] = pd.to_datetime(p["dt"])
    p = merge_deposit(p, time_col="time")
    p = p.sort_values(["ticker", "si"], kind="mergesort").reset_index(drop=True)
    p["dt"] = p["time"].dt.strftime("%Y-%m-%d")
    p["ym"] = p["dt"].str.slice(0, 7)
    p["year"] = p["time"].dt.year

    # --- regime + history ------------------------------------------------------------------
    p = p.merge(state.rename(columns={"state": "dt5g"}), on="dt", how="left")
    p = p.merge(first[["ticker", "first_dt"]], on="ticker", how="left")
    p["hist_days"] = (p["time"] - pd.to_datetime(p["first_dt"])).dt.days

    # --- labels (PREREG §2) ------------------------------------------------------------------
    p["stable3"] = (p["n0"] >= 1) & (p["n1"] >= 1) & (p["n2"] >= 1)
    p["stable5"] = p["stable3"] & (p["n2"] >= 1) & (p["n3"] >= 1) & (p["n4"] >= 1)
    p["nonpayer"] = (p["n0"] == 0) & (p["n1"] == 0) & (p["n2"] == 0)

    # --- yield (PREREG §3): raw Price is the denominator, on purpose -------------------------
    p["yld"] = np.where(p["price"] > 0, 100.0 * p["div0"] / p["price"], np.nan)

    # --- lags, only valid across CONSECUTIVE sessions of the same ticker ---------------------
    g = p.groupby("ticker", sort=False)
    p["si_lag"] = g["si"].shift(1)
    contiguous = (p["si"] - p["si_lag"]) == 1
    for src, dst in [("yld", "yld_lag"), ("price", "price_lag"), ("div0", "div0_lag"),
                     ("deposit_rate", "dep_lag")]:
        p[dst] = g[src].shift(1).where(contiguous)
    p["si_lag21"] = g["si"].shift(CAUSE_LAG)
    lag21_ok = (p["si"] - p["si_lag21"]) == CAUSE_LAG
    for src, dst in [("price", "price_l21"), ("div0", "div0_l21"),
                     ("deposit_rate", "dep_l21")]:
        p[dst] = g[src].shift(CAUSE_LAG).where(lag21_ok)

    # --- eligibility (PREREG §4.1) -----------------------------------------------------------
    # DEVIATION D1: §4.1 item 4 (trailing_div > 0) is applied to the EVENT legs only. Applied
    # to "every stock-day" as literally written it would empty the NON-PAYER control pool
    # (a non-payer has div0 == 0 by construction), making §6 unrunnable.
    p["eligible"] = (
        (p["price"] > 0) & (p["close"] > 0)
        & (p["hist_days"] >= MIN_HIST_DAYS)
        & (~p["ticker"].isin(BAD_TICKERS))
    )
    # PREREG §4.2 — Price can sit in the T-1 frame on an ex-date (registry TRAP); both tests
    # are observable at t and only DISQUALIFY, never patch.
    # DEVIATION D2: §4.2 wrote the impossible-price test as `P_raw NOT IN [Low, High]`, but
    # `ticker.Low/High` are BACK-ADJUSTED (they live in the `Close` frame) while `Price` is raw.
    # Measured on this panel: median Price/Close = 1.284 (p90 = 3.03); Close in [Low, High] for
    # 99.9997% of rows vs Price in [Low, High] for only 24.7%. Read literally the test throws
    # away 96% of qualifying crossings (1,469 -> 65) for a unit mismatch, not for bad data.
    # It is therefore applied in the frame where Low/High actually live.
    p["trigger_ok"] = (
        p["eligible"] & (p["is_exdate"] == 0)
        & (p["close"] >= p["low"]) & (p["close"] <= p["high"])
    )
    # Diagnostic ONLY, deliberately NOT a third disqualifier (adding a filter after seeing the
    # data is a free parameter): raw Price frozen while adjusted Close moved is the real
    # signature of the registry TRAP. 0.48% of rows. Reported as a sensitivity leg.
    close_lag = p.groupby("ticker", sort=False)["close"].shift(1).where(contiguous)
    p["stale_px"] = (np.isclose(p["price"], p["price_lag"].fillna(-1))
                     & ~np.isclose(p["close"], close_lag.fillna(-1))
                     & p["price_lag"].notna())

    # DEVIATION D3: PREREG §7.4/§6 assumed `ticker.ICB_Code` holds the coarse CT/NH/BH/CK tag.
    # It actually holds the 4-digit numeric ICB subsector (76 distinct values here; 8355 = Banks,
    # 2357 = Heavy Construction, ...). Banks are identified as 8355; the "rough sector" used for
    # control matching is the ICB *industry* (code // 1000), which is the coarse grouping §6 asked
    # for -- matching on the raw 4-digit subsector would be far stricter than pre-registered.
    # 60-session trailing return: an episode reaches the floor BY FALLING, so this is the
    # confound the pre-registered matching (ICB + rvol only) does not close. Used by the
    # pretrend-matched falsification leg below.
    c60 = g["close"].shift(60).where((p["si"] - g["si"].shift(60)) == 60)
    p["pret60"] = 100.0 * (p["close"] / c60 - 1.0)

    p["icb_num"] = pd.to_numeric(p["icb"], errors="coerce")
    p["icb_ind"] = np.floor(p["icb_num"] / 1000.0)
    p["is_bank"] = p["icb_num"] == 8355

    # --- outcomes ---------------------------------------------------------------------------
    for h in HORIZONS:
        r_stock = p[f"c_p{h}"] / p["close"] - 1.0
        r_bench = idx.ret(p["dt"], p[f"d_p{h}"])
        p[f"bhar_{h}"] = 100.0 * (r_stock - r_bench)
    p["mdd_60"] = np.where(p["n_fwd60"] == 60, 100.0 * (p["minc60"] / p["close"] - 1.0), np.nan)
    p["mup_60"] = np.where(p["n_fwd60"] == 60, 100.0 * (p["maxc60"] / p["close"] - 1.0), np.nan)
    return p


def thr_series(p: pd.DataFrame, thr) -> tuple:
    """(thr_t, thr_{t-1}, thr_{t-21}) for a named threshold variant."""
    if thr == "deposit":
        return p["deposit_rate"], p["dep_lag"], p["dep_l21"]
    v = float(thr)
    ones = pd.Series(v, index=p.index)
    return ones, ones.where(p["yld_lag"].notna()), ones.where(p["div0_l21"].notna())


def dedupe_overlap(ev: pd.DataFrame) -> pd.DataFrame:
    """PREREG §4.3 — one episode per ticker per 120 sessions, keeping the EARLIEST."""
    if not len(ev):
        return ev
    ev = ev.sort_values(["ticker", "si"], kind="mergesort")
    keep = np.zeros(len(ev), dtype=bool)
    last = {}
    for i, (tk, si) in enumerate(zip(ev["ticker"].to_numpy(), ev["si"].to_numpy())):
        if tk not in last or si - last[tk] >= OVERLAP_SESSIONS:
            keep[i] = True
            last[tk] = si
    return ev[keep]


# ==========================================================================================
# Test A — the crossing episode (PREREG §5)
# ==========================================================================================
def label_cause(ev: pd.DataFrame) -> pd.Series:
    div_up = ev["div0"] > ev["div0_l21"]
    div_flat = np.isclose(ev["div0"], ev["div0_l21"])
    px_down = ev["price"] < ev["price_l21"]
    thr_down = ev["thr_l21"] > ev["thr"]
    out = pd.Series("OTHER", index=ev.index)
    out[div_flat & px_down] = "PRICE_DRIVEN"
    out[div_up] = "DIV_DRIVEN"
    out[thr_down & div_flat & ~px_down] = "THRESHOLD_DRIVEN"
    return out


def test_a(p: pd.DataFrame, thr, stable_col: str = "stable3") -> pd.DataFrame:
    t_now, t_lag, t_l21 = thr_series(p, thr)
    m = (
        p[stable_col] & p["trigger_ok"]
        & (p["div0"] > 0) & p["yld"].notna() & p["yld_lag"].notna()
        & (p["yld_lag"] < t_lag) & (p["yld"] >= t_now)
    )
    ev = p[m.fillna(False)].copy()
    ev["thr"], ev["thr_l21"] = t_now[m.fillna(False)], t_l21[m.fillna(False)]
    ev["cause"] = label_cause(ev)
    if thr == "deposit":
        # PREREG §5.1 — a step in the rate series is not market behaviour.
        ev = ev[ev["cause"] != "THRESHOLD_DRIVEN"]
    return dedupe_overlap(ev)


# ==========================================================================================
# Test B — price support at the floor, matched to non-payers (PREREG §6)
# ==========================================================================================
def test_b_events(p: pd.DataFrame, thr, stable_col: str = "stable3") -> pd.DataFrame:
    t_now, t_lag, _ = thr_series(p, thr)
    prox = t_now / p["yld"]
    prox_lag = t_lag / p["yld_lag"]
    m = (
        p[stable_col] & p["trigger_ok"] & (p["div0"] > 0)
        & p["yld"].notna() & (p["yld"] > 0) & p["yld_lag"].notna() & (p["yld_lag"] > 0)
        & prox.between(NEAR_LO, NEAR_HI) & (prox_lag > NEAR_HI)
        & np.isfinite(p["mdd_60"])
    )
    ev = p[m.fillna(False)].copy()
    ev["prox"] = prox[m.fillna(False)]
    return dedupe_overlap(ev)


def match_controls(ev: pd.DataFrame, p: pd.DataFrame, pret_band=None) -> pd.DataFrame:
    """Same day, same ICB, nearest rvol60 within [0.8, 1.25]x — up to 3, averaged.

    Matching on volatility is deliberate: drawdown is driven by vol before it is driven by
    valuation, so an unmatched test would only re-measure "stable payers are calmer".
    """
    pool = p[
        p["nonpayer"] & p["eligible"] & np.isfinite(p["mdd_60"])
        & p["rvol60"].notna() & (p["rvol60"] > 0)
    ][["ticker", "dt", "icb_ind", "rvol60", "mdd_60", "bhar_60", "pret60"]]   # DEVIATION D3
    ev = ev[ev["rvol60"].notna() & (ev["rvol60"] > 0)].copy()
    if not len(ev) or not len(pool):
        return ev.assign(ctrl_mdd_60=np.nan, ctrl_bhar_60=np.nan, n_ctrl=0)

    ev["_eid"] = np.arange(len(ev))
    j = ev[["_eid", "dt", "icb_ind", "rvol60", "pret60"]].merge(
        pool, on=["dt", "icb_ind"], how="inner", suffixes=("_ev", "_ct"))
    ratio = j["rvol60_ct"] / j["rvol60_ev"]
    j = j[(ratio >= RVOL_LO) & (ratio <= RVOL_HI)].copy()
    if pret_band is not None:      # falsification leg, not pre-registered
        j = j[(j["pret60_ct"] - j["pret60_ev"]).abs() <= pret_band]
    j["dist"] = (np.log(j["rvol60_ct"] / j["rvol60_ev"])).abs()
    j = j.sort_values(["_eid", "dist"], kind="mergesort")
    j = j.groupby("_eid", sort=False).head(MAX_CONTROLS)
    agg = j.groupby("_eid").agg(ctrl_mdd_60=("mdd_60", "mean"),
                                ctrl_bhar_60=("bhar_60", "mean"),
                                ctrl_pret60=("pret60_ct", "mean"),
                                n_ctrl=("mdd_60", "size"))
    ev = ev.merge(agg, left_on="_eid", right_index=True, how="left")
    ev["n_ctrl"] = ev["n_ctrl"].fillna(0).astype(int)
    ev["d_mdd_60"] = ev["mdd_60"] - ev["ctrl_mdd_60"]
    ev["d_bhar_60"] = ev["bhar_60"] - ev["ctrl_bhar_60"]
    return ev


# ==========================================================================================
# placebo (PREREG §8) — same tickers/pipeline, entry shifted back 250 sessions
# ==========================================================================================
def placebo(ev: pd.DataFrame, p: pd.DataFrame, cols: list[str]) -> dict:
    key = p.set_index(["ticker", "si"])
    want = pd.MultiIndex.from_arrays([ev["ticker"], ev["si"] - PLACEBO_LAG])
    hit = key.reindex(want)
    out = {}
    for c in cols:
        d = pd.DataFrame({c: hit[c].to_numpy(), "ticker": ev["ticker"].to_numpy(),
                          "ym": hit["ym"].to_numpy(), "dt": hit["dt"].to_numpy()})
        d = d[np.isfinite(d[c]) & d["ym"].notna()]
        out[c] = stat_block(d, c) if len(d) else {"n": 0}
    return out


def placebo_matched(ev: pd.DataFrame, p: pd.DataFrame) -> dict:
    """PREREG §8 placebo, run as literally written: the WHOLE pipeline on the fake date.

    DEVIATION D4: `placebo()` above only carries the event stock's own outcome back 250
    sessions; it never re-runs the matching, so it cannot answer the question the placebo
    exists to answer -- whether the matched gap is specific to standing at the floor or is
    just the standing difference between a stable payer and a non-payer on any random day.
    Sprint 2's lesson (`corp_action_program_20260815`) was exactly this: a pipeline's null is
    not 0 until measured. Kept alongside, not instead of, the original.
    """
    key = p.set_index(["ticker", "si"])
    want = pd.MultiIndex.from_arrays([ev["ticker"], ev["si"] - PLACEBO_LAG])
    fake = key.reindex(want).reset_index()
    fake = fake[fake["dt"].notna() & np.isfinite(fake["mdd_60"])
                & fake["eligible"].fillna(False).astype(bool)]
    if not len(fake):
        return {"n": 0}
    m = match_controls(fake, p)
    m = m[m["n_ctrl"] > 0]
    # PREREG §8 requires the primary reported NET of a PAIRED placebo, not just side by side.
    paired = ev[["ticker", "si", "d_mdd_60", "ym", "dt", "year"]].merge(
        m[["ticker", "si", "d_mdd_60"]].assign(si=lambda d: d["si"] + PLACEBO_LAG),
        on=["ticker", "si"], how="inner", suffixes=("", "_pl"))
    paired["d_net"] = paired["d_mdd_60"] - paired["d_mdd_60_pl"]
    return {"n_pseudo": int(len(fake)), "d_mdd_60": split_stats(m, "d_mdd_60") if len(m) else {},
            "paired_net": split_stats(paired, "d_net") if len(paired) else {},
            "d_bhar_60": stat_block(m, "d_bhar_60") if len(m) else {},
            "mdd_60_event": stat_block(m, "mdd_60") if len(m) else {},
            "mdd_60_ctrl": stat_block(m, "ctrl_mdd_60") if len(m) else {}}


def far_from_floor(p: pd.DataFrame, thr, lo: float = 1.30) -> dict:
    """NOT pre-registered -- a second falsification leg, added because the §8 placebo turned
    out to be the only thing separating "yield floor" from "stable payers just fall less".

    Same stable-3 population, same matching, but sampled where the price is FAR ABOVE the
    floor (prox > 1.30, i.e. yield well under the threshold). If the gap is a floor effect it
    must shrink here; if it is a payer-vs-non-payer level effect it will not move.
    """
    t_now, _, _ = thr_series(p, thr)
    prox = t_now / p["yld"]
    m = (p["stable3"] & p["trigger_ok"] & (p["div0"] > 0)
         & p["yld"].notna() & (p["yld"] > 0) & (prox > lo) & np.isfinite(p["mdd_60"]))
    ev = dedupe_overlap(p[m.fillna(False)].copy())
    mt = match_controls(ev, p)
    mt = mt[mt["n_ctrl"] > 0]
    return {"prox_gt": lo, "n_episodes": int(len(ev)), "n_matched": int(len(mt)),
            "d_mdd_60": split_stats(mt, "d_mdd_60") if len(mt) else {},
            "mdd_60_event": stat_block(mt, "mdd_60") if len(mt) else {},
            "mdd_60_ctrl": stat_block(mt, "ctrl_mdd_60") if len(mt) else {}}


# ==========================================================================================
def main() -> int:
    p, idx, state, first = load()
    p = prepare(p, idx, state, first)
    res: dict = {"seed": SEED, "n_boot": N_BOOT, "primary_h": PRIMARY_H,
                 "panel_rows": int(len(p)), "panel_tickers": int(p["ticker"].nunique())}

    # ---------------- Test A ---------------------------------------------------------------
    a_all = {}
    for thr in ["deposit"] + FIXED_THR:
        ev = test_a(p, thr)
        k = "deposit" if thr == "deposit" else f"{thr:g}%"
        blk = {"n_episodes": int(len(ev)), "n_tickers": int(ev["ticker"].nunique()),
               "n_months": int(ev["ym"].nunique()) if len(ev) else 0,
               "cause_mix": ev["cause"].value_counts().to_dict() if len(ev) else {}}
        for h in HORIZONS:
            blk[f"bhar_{h}"] = split_stats(ev, f"bhar_{h}")
        blk["mdd_60"] = split_stats(ev, "mdd_60")
        if thr == "deposit" and len(ev):
            blk["by_cause"] = {c: stat_block(g, f"bhar_{PRIMARY_H}")
                               for c, g in ev.groupby("cause")}
            blk["by_state"] = {str(int(s)): stat_block(g, f"bhar_{PRIMARY_H}")
                               for s, g in ev[ev["dt5g"].notna()].groupby("dt5g")}
            blk["ex_crisis_exbull"] = split_stats(
                ev[~ev["dt5g"].isin([1, 5])], f"bhar_{PRIMARY_H}")
            blk["loo_year"] = _loo(ev, f"bhar_{PRIMARY_H}")
            blk["by_sector"] = {   # DEVIATION D3
                "banks": stat_block(ev[ev["is_bank"]], f"bhar_{PRIMARY_H}"),
                "non_banks": stat_block(ev[~ev["is_bank"]], f"bhar_{PRIMARY_H}")}
            blk["ex_stale_px"] = split_stats(ev[~ev["stale_px"]], f"bhar_{PRIMARY_H}")
            blk["placebo"] = placebo(ev, p, [f"bhar_{PRIMARY_H}", "mdd_60"])
            ev.to_csv(os.path.join(OUT, "episodes_testA_deposit.csv"), index=False)
        a_all[k] = blk
    res["test_a"] = a_all

    # ---------------- Test B ---------------------------------------------------------------
    b_all = {}
    for thr in ["deposit"] + FIXED_THR:
        ev = match_controls(test_b_events(p, thr), p)
        k = "deposit" if thr == "deposit" else f"{thr:g}%"
        matched = ev[ev["n_ctrl"] > 0] if len(ev) else ev
        blk = {"n_episodes": int(len(ev)),
               "n_matched": int(len(matched)),
               "n_tickers": int(matched["ticker"].nunique()) if len(matched) else 0,
               "n_months": int(matched["ym"].nunique()) if len(matched) else 0,
               "mdd_60_event": split_stats(matched, "mdd_60") if len(matched) else {"n": 0},
               "mdd_60_ctrl": (stat_block(matched, "ctrl_mdd_60") if len(matched)
                               else {"n": 0}),
               "d_mdd_60": split_stats(matched, "d_mdd_60") if len(matched) else {"n": 0},
               "d_bhar_60": split_stats(matched, "d_bhar_60") if len(matched) else {"n": 0}}
        if len(matched):
            blk["p_mdd_lt_10"] = {
                "event": float((matched["mdd_60"] < -10).mean()),
                "ctrl": float((matched["ctrl_mdd_60"] < -10).mean())}
            blk["p_mdd_lt_20"] = {
                "event": float((matched["mdd_60"] < -20).mean()),
                "ctrl": float((matched["ctrl_mdd_60"] < -20).mean())}
            blk["desc_event_mdd"] = desc(matched["mdd_60"])
            blk["desc_ctrl_mdd"] = desc(matched["ctrl_mdd_60"])
        if thr == "deposit" and len(matched):
            blk["ex_crisis_exbull"] = split_stats(
                matched[~matched["dt5g"].isin([1, 5])], "d_mdd_60")
            blk["by_state"] = {str(int(s)): stat_block(g, "d_mdd_60")
                               for s, g in matched[matched["dt5g"].notna()].groupby("dt5g")}
            blk["loo_year"] = _loo(matched, "d_mdd_60")
            blk["by_sector"] = {   # DEVIATION D3
                "banks": stat_block(matched[matched["is_bank"]], "d_mdd_60"),
                "non_banks": stat_block(matched[~matched["is_bank"]], "d_mdd_60")}
            blk["ex_stale_px"] = split_stats(matched[~matched["stale_px"]], "d_mdd_60")
            blk["placebo"] = placebo(matched, p, ["mdd_60"])
            blk["placebo_matched"] = placebo_matched(matched, p)      # DEVIATION D4
            blk["far_from_floor"] = far_from_floor(p, thr)            # not pre-registered
            mp = match_controls(test_b_events(p, thr), p, pret_band=10.0)  # not pre-registered
            mp = mp[mp["n_ctrl"] > 0]
            blk["pretrend_matched"] = {
                "pret_band_pp": 10.0, "n_matched": int(len(mp)),
                "d_mdd_60": split_stats(mp, "d_mdd_60") if len(mp) else {},
                "pret60_event": stat_block(mp, "pret60") if len(mp) else {}}
            blk["pretrend_raw"] = {
                "event": stat_block(matched, "pret60"),
                "gap_note": "control pretrend is averaged inside the match, see episodes CSV"}
            matched.to_csv(os.path.join(OUT, "episodes_testB_deposit.csv"), index=False)
        b_all[k] = blk
    res["test_b"] = b_all

    # ---------------- STABLE-5 robustness (PREREG §7.5) --------------------------------------
    ev5a = test_a(p, "deposit", stable_col="stable5")
    ev5b = match_controls(test_b_events(p, "deposit", stable_col="stable5"), p)
    m5 = ev5b[ev5b["n_ctrl"] > 0] if len(ev5b) else ev5b
    res["stable5"] = {
        "test_a": {"n_episodes": int(len(ev5a)),
                   f"bhar_{PRIMARY_H}": split_stats(ev5a, f"bhar_{PRIMARY_H}")},
        "test_b": {"n_matched": int(len(m5)),
                   "d_mdd_60": split_stats(m5, "d_mdd_60") if len(m5) else {"n": 0}},
    }

    with open(os.path.join(OUT, "results.json"), "w") as fh:
        json.dump(res, fh, indent=2, default=float)
    print(json.dumps(res["test_a"]["deposit"][f"bhar_{PRIMARY_H}"]["all"], indent=2))
    print(json.dumps(res["test_b"]["deposit"]["d_mdd_60"]["all"], indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
