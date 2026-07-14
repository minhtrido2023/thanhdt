# -*- coding: utf-8 -*-
"""dcf_placebo_test.py — Pha-4 PLACEBO test for the DCF-as-gate hypothesis
(job Taylor_20260714_080414).

WHY THIS EXISTS
---------------
quant-skeptic's REFUTED verdict on Pha 3 (mike/logs/verify_20260714_073843.log) named ONE decisive,
blocking objection: variant A (BASKET_DCF_MODE=exclude_rich) mechanically swaps only ~3 names in a
30-name PARKING basket, and nobody had shown that a RANDOM 3-name swap wouldn't produce the same
spread. If random does the same thing, the DCF is not doing any work — variant A's +0.99pp CAGR is
just the dispersion you get from perturbing a concentrated basket at all.

THE CONTROL
-----------
`BASKET_DCF_MODE=placebo_random` (custom_basket.py) drops, at each rebal date d, exactly as many
names as exclude_rich actually dropped at that same date d (n_d measured off the same dcf_at calls,
not estimated) — but picks the victims at RANDOM. Same count, same pool, same stage of the pipeline,
same fail-safe. The ONLY difference vs variant A is *which* names go. 20 independent seeds give the
null distribution of "what a same-sized random swap is worth".

WHAT IT ANSWERS
---------------
Where does variant A's real delta (+0.99pp CAGR / +0.059 Sharpe vs control) sit inside that null?
Middle of the pack -> the DCF adds nothing over random, REFUTED confirmed. Clear outlier -> report
the fact, do NOT conclude GO (that needs quant-skeptic re-verification).

Metric conventions (CAGR/Sharpe on actual sessions/yr, not 252) are copied verbatim from Pha 3's
data/dcf_exp_logs/compare_dcf.py so placebo numbers are comparable to ctrl/varA line-for-line.

Run: $DNA_PYEXE dcf_placebo_test.py
"""
import os, glob, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
BASE = f"{WORKDIR}/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap"
CTRL = f"{BASE}_exp_dcfctrl20260714.csv"
VARA = f"{BASE}_exp_dcfexrich.csv"
WINDOWS = [("IS 2014-19", "2014-01-01", "2019-12-31"),
           ("OOS 2020+",  "2020-01-01", "2099-12-31"),
           ("FULL",       "2014-01-01", "2099-12-31")]


def nav_series(path):
    df = pd.read_csv(path, low_memory=False)
    d = df[df["combined_nav"].notna() & df["ymd"].notna()].copy()
    d["ymd"] = pd.to_datetime(d["ymd"], errors="coerce")
    d = d.dropna(subset=["ymd"]).sort_values("ymd")
    return d.groupby("ymd")["combined_nav"].last().astype(float)


def metrics(s):
    s = s.dropna()
    if len(s) < 20:
        return dict(cagr=np.nan, sharpe=np.nan, mdd=np.nan, calmar=np.nan)
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    cagr = ((s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1) * 100
    r = np.log(s / s.shift(1)).dropna()
    spy = len(r) / yrs                       # actual sessions/yr (registry convention, not 252)
    sharpe = (r.mean() / r.std(ddof=1)) * np.sqrt(spy) if r.std(ddof=1) > 0 else np.nan
    mdd = ((s / s.cummax()) - 1).min() * 100
    calmar = cagr / abs(mdd) if mdd < 0 else np.nan
    return dict(cagr=cagr, sharpe=sharpe, mdd=mdd, calmar=calmar)


def win(s, w0, w1):
    return metrics(s[(s.index >= w0) & (s.index <= w1)])


def deltas_vs_ctrl(s, ctrl):
    """-> {window: {cagr/sharpe/calmar delta}} for one run."""
    out = {}
    for wname, w0, w1 in WINDOWS:
        m, b = win(s, w0, w1), win(ctrl, w0, w1)
        out[wname] = {k: m[k] - b[k] for k in ("cagr", "sharpe", "calmar")}
    return out


def pct_rank(null, x):
    """% of null draws strictly BELOW x (the observed value's percentile in the null)."""
    null = np.asarray([v for v in null if np.isfinite(v)])
    return float((null < x).mean() * 100) if len(null) else np.nan


def main():
    ctrl = nav_series(CTRL)
    vara = nav_series(VARA)

    # --- regression guard: the control re-run under the patched code must be byte-identical -------
    rerun = f"{BASE}_exp_dcfctrlrerun20260714.csv"
    print("=== [0] REGRESSION GUARD (patched code must not move the control) " + "=" * 12)
    if os.path.exists(rerun):
        a, b = pd.read_csv(CTRL, low_memory=False), pd.read_csv(rerun, low_memory=False)
        same_nav = nav_series(rerun).equals(ctrl)
        print(f"  ctrl re-run under placebo patch: NAV series identical = {same_nav}  "
              f"(shape {a.shape} vs {b.shape})")
        if not same_nav:
            print("  !! WARNING: the patch moved the OFF path — every delta below is suspect.")
    else:
        print(f"  MISSING {os.path.basename(rerun)} — cannot prove the patch left OFF untouched.")

    # --- collect placebo seeds ---------------------------------------------------------------
    seed_files = sorted(glob.glob(f"{BASE}_exp_dcfplacebo*.csv"),
                        key=lambda p: int(p.split("dcfplacebo")[1].split(".")[0]))
    seeds = []
    for p in seed_files:
        sd = int(p.split("dcfplacebo")[1].split(".")[0])
        try:
            seeds.append((sd, deltas_vs_ctrl(nav_series(p), ctrl)))
        except Exception as e:
            print(f"  seed {sd}: unreadable ({e})")
    print(f"\n=== [1] PLACEBO SEEDS LOADED: {len(seeds)} " + "=" * 40)
    if not seeds:
        raise SystemExit("no placebo runs found")

    a_d = deltas_vs_ctrl(vara, ctrl)

    # --- per-seed table ----------------------------------------------------------------------
    print(f"\n{'seed':<6}" + "".join(f"{w+' ΔCAGR':>16}{w+' ΔShrp':>16}" for w, _, _ in WINDOWS))
    for sd, d in seeds:
        row = f"{sd:<6}"
        for w, _, _ in WINDOWS:
            row += f"{d[w]['cagr']:>16.2f}{d[w]['sharpe']:>16.3f}"
        print(row)
    row = f"{'varA':<6}"
    for w, _, _ in WINDOWS:
        row += f"{a_d[w]['cagr']:>16.2f}{a_d[w]['sharpe']:>16.3f}"
    print(row + "   <-- the REAL DCF gate")

    # --- null distribution vs variant A ------------------------------------------------------
    print("\n=== [2] NULL DISTRIBUTION — where does the REAL DCF delta sit? " + "=" * 14)
    print(f"{'window':<12} {'metric':<8} {'null mean':>10} {'null SD':>9} {'null min':>9} "
          f"{'null max':>9} {'varA':>9} {'pctile':>8} {'z':>7} {'#>=varA':>9}")
    verdict_rows = []
    for wname, _, _ in WINDOWS:
        for metric in ("cagr", "sharpe", "calmar"):
            null = np.array([d[wname][metric] for _, d in seeds], dtype=float)
            null = null[np.isfinite(null)]
            x = a_d[wname][metric]
            mu, sd_ = null.mean(), null.std(ddof=1)
            z = (x - mu) / sd_ if sd_ > 0 else np.nan
            n_ge = int((null >= x).sum())
            print(f"{wname:<12} {metric:<8} {mu:>10.3f} {sd_:>9.3f} {null.min():>9.3f} "
                  f"{null.max():>9.3f} {x:>9.3f} {pct_rank(null, x):>7.1f}% {z:>7.2f} "
                  f"{n_ge:>4}/{len(null)}")
            verdict_rows.append((wname, metric, x, mu, sd_, z, n_ge, len(null)))

    # --- one-sample t-test: varA point vs the 20-draw null (skeptic's mandatory field) ---------
    # NOTE: this is NOT the daily-return t-test already run in Pha 3. Here the null is the spread of
    # 20 random same-sized swaps, and we ask whether one observed point is extreme within it. With
    # n=20 draws the SD is itself noisy, so treat this as descriptive, not a p-value to defend.
    print("\n=== [3] varA vs PLACEBO NULL — t-statistic (n=20 draws, descriptive) " + "=" * 8)
    from scipy import stats as st
    for wname in ("FULL", "IS 2014-19", "OOS 2020+"):
        for metric in ("cagr", "sharpe"):
            null = np.array([d[wname][metric] for _, d in seeds], dtype=float)
            null = null[np.isfinite(null)]
            x = a_d[wname][metric]
            t = (x - null.mean()) / (null.std(ddof=1) / np.sqrt(len(null))) if null.std(ddof=1) > 0 else np.nan
            # two-sided p for "is varA's point drawn from the same distribution as the placebos"
            t_single = (x - null.mean()) / null.std(ddof=1) if null.std(ddof=1) > 0 else np.nan
            p_single = 2 * (1 - st.t.cdf(abs(t_single), df=len(null) - 1)) if np.isfinite(t_single) else np.nan
            print(f"  {wname:<12} {metric:<7} varA={x:+.3f}  null={null.mean():+.3f}±{null.std(ddof=1):.3f}  "
                  f"t_vs_mean={t:+.2f}  t_as_draw={t_single:+.2f}  p_as_draw={p_single:.3f}")

    # --- per-year deltas (the 2017/2021 concentration the skeptic flagged) --------------------
    print("\n=== [4] PER-YEAR ΔCAGR-equivalent (total-return delta vs ctrl, pp) " + "=" * 10)
    def yearly(s):
        out = {}
        for y in sorted(set(s.index.year)):
            ny = s[s.index.year == y]
            out[y] = (ny.iloc[-1] / ny.iloc[0] - 1) * 100 if len(ny) > 4 else np.nan
        return out
    y_ctrl, y_a = yearly(ctrl), yearly(vara)
    y_seeds = [yearly(nav_series(p)) for p in seed_files]
    years = sorted(y_ctrl)
    print(f"{'year':<6}{'varA Δ':>10}{'null mean':>11}{'null SD':>9}{'pctile':>8}{'#>=varA':>9}")
    for y in years:
        xa = y_a.get(y, np.nan) - y_ctrl.get(y, np.nan)
        null = np.array([ys.get(y, np.nan) - y_ctrl.get(y, np.nan) for ys in y_seeds], dtype=float)
        null = null[np.isfinite(null)]
        if not len(null) or not np.isfinite(xa):
            continue
        print(f"{y:<6}{xa:>10.2f}{null.mean():>11.2f}{null.std(ddof=1):>9.2f}"
              f"{pct_rank(null, xa):>7.1f}%{int((null >= xa).sum()):>5}/{len(null)}")

    # --- headline read -----------------------------------------------------------------------
    print("\n=== [5] DECISION READ " + "=" * 56)
    for wname in ("FULL",):
        for metric in ("cagr", "sharpe"):
            null = np.array([d[wname][metric] for _, d in seeds], dtype=float)
            null = null[np.isfinite(null)]
            x = a_d[wname][metric]
            n_ge = int((null >= x).sum())
            print(f"  {wname} {metric}: {n_ge}/{len(null)} random same-sized swaps did as well or "
                  f"better than the real DCF gate (pctile {pct_rank(null, x):.0f}%).")
    print("  Read: varA inside the null's normal range -> DCF adds nothing over a random swap")
    print("        (REFUTED confirmed). Clear outlier (top 1-2/20, >mean+2SD) -> report, do NOT")
    print("        self-declare GO; route to quant-skeptic.")


if __name__ == "__main__":
    main()
