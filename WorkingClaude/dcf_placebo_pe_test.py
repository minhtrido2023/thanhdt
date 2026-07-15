# -*- coding: utf-8 -*-
"""dcf_placebo_pe_test.py — Pha-5 VALUE-PROXY placebo for the DCF-as-gate hypothesis
(job Taylor_20260715_041608).

WHY THIS EXISTS
---------------
Pha 4 (placebo_random, 20 seeds) killed objection #1: variant A's edge is NOT what a random
same-sized swap produces (z=2.5-2.85, 0/20 seeds match). Objection #2, named in the Pha-4 finding
itself and still open: "DCF-hơn-random ≠ DCF-cụ-thể — a SIMPLER systematic rule (drop the
highest-PE names) might capture the same spread". If it does, the DCF is just 1/PE in disguise at
the gate level, and adds nothing over the yieldcombo selector that already ranks on 1/PE.

THE CONTROL
-----------
`BASKET_DCF_MODE=placebo_pe` (custom_basket.py): at each rebal date d, drop exactly n_d names
(n_d measured off the same dcf_at calls exclude_rich uses — same count, same pool, same stage,
same fail-safe), but pick the n_d names with the HIGHEST PE (lowest 1/PE from the selector's own
pe_piv at src_q). Deterministic, no seed. NaN-PE names never dropped (mirrors NOT_COMPUTED).

WHAT IT ANSWERS
---------------
(a) varA >> placebo_pe  -> DCF adds real information beyond the trivial PE rule.
(b) varA ≈ placebo_pe  -> DCF-as-gate has no incremental value over a one-line PE rule; NO-GO
    regardless of the Pha-4 result.
Interpretation guardrail: placebo_pe drops the WORST-ranked names of the selector's own score, so
it is expected to be closer to ctrl than to varA mechanically; the decisive read is whether
placebo_pe reproduces varA's delta, not whether it beats ctrl.

Metric conventions copied verbatim from dcf_placebo_test.py (Pha 4) so all numbers are
line-for-line comparable with ctrl / varA / the 20-seed random null.

Run: $DNA_PYEXE dcf_placebo_pe_test.py
"""
import os, glob, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
BASE = f"{WORKDIR}/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap"
# VINTAGE NOTE (found during the run, 2026-07-15): the shared bq_cache was resynced 23:45 ICT
# 07-14 and carries a historical price revision (ctrl AND varA reruns both diverge from their
# 07-14 twins starting exactly 2018-01-03 — a data change, not a code change, since ctrl never
# touches the placebo_pe path). The 3-way comparison below therefore uses the 07-15 vintage for
# ALL arms (same code, same pinned cache) — intra-vintage clean. The 07-14 files remain only in
# the cross-vintage guard [0] and the Pha-4 random-null section [3] (deltas-vs-own-ctrl, which
# are robust to a level shift but flagged as cross-vintage where used).
CTRL14 = f"{BASE}_exp_dcfctrl20260714.csv"
VARA14 = f"{BASE}_exp_dcfexrich.csv"
CTRL = f"{BASE}_exp_dcfctrlrerun20260715.csv"
VARA = f"{BASE}_exp_dcfexrichrerun20260715.csv"
VARA_RERUN = VARA
PEPL = f"{BASE}_exp_dcfplacebope20260715.csv"
DROPLOG = f"{WORKDIR}/data/dcf_exp_logs/placebo_pe_drops.csv"
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
    spy = len(r) / yrs
    sharpe = (r.mean() / r.std(ddof=1)) * np.sqrt(spy) if r.std(ddof=1) > 0 else np.nan
    mdd = ((s / s.cummax()) - 1).min() * 100
    calmar = cagr / abs(mdd) if mdd < 0 else np.nan
    return dict(cagr=cagr, sharpe=sharpe, mdd=mdd, calmar=calmar)


def win(s, w0, w1):
    return metrics(s[(s.index >= w0) & (s.index <= w1)])


def deltas_vs_ctrl(s, ctrl):
    out = {}
    for wname, w0, w1 in WINDOWS:
        m, b = win(s, w0, w1), win(ctrl, w0, w1)
        out[wname] = {k: m[k] - b[k] for k in ("cagr", "sharpe", "calmar")}
    return out


def main():
    ctrl, vara, pepl = nav_series(CTRL), nav_series(VARA), nav_series(PEPL)

    # --- [0] cross-vintage guard: is the 14->15 gap data or code? --------------------------------
    print("=== [0] CROSS-VINTAGE GUARD (07-14 vs 07-15 cache; ctrl isolates data-vs-code) " + "=" * 2)
    c14, a14 = nav_series(CTRL14), nav_series(VARA14)
    for nm, new, old in (("ctrl", ctrl, c14), ("varA", vara, a14)):
        d = (new / old - 1).abs()
        neq = d[d > 1e-12]
        print(f"  {nm} 07-15 vs 07-14: identical={len(neq)==0}"
              + ("" if len(neq) == 0 else
                 f"  first_diff={neq.index.min().date()}  n_diff={len(neq)}  max|rel|={d.max():.2e}"))
    print("  ctrl diverging too (same first_diff) => cache revision, NOT the placebo_pe patch;")
    print("  all 3-way reads below are intra-vintage 07-15 (same code, same pinned cache).")

    # --- [1] drop-log audit: count-match + who-gets-dropped overlap ------------------------------
    print("\n=== [1] DROP-LOG AUDIT (same-count control? PE-vs-DCF victim overlap?) " + "=" * 8)
    dl = pd.read_csv(DROPLOG)
    exact = (dl["n_dropped"] == dl["n_target"]).all()
    print(f"  dates={len(dl)}  dropped total={int(dl.n_dropped.sum())}  target total="
          f"{int(dl.n_target.sum())}  per-date exact count match: {exact}")
    ovl = []
    for _, r in dl.iterrows():
        dset = set(str(r["dcf_drops"]).split("|")) if pd.notna(r["dcf_drops"]) else set()
        pset = set(str(r["pe_drops"]).split("|")) if pd.notna(r["pe_drops"]) else set()
        if dset or pset:
            ovl.append((r["date"], len(dset & pset), len(dset), len(pset),
                        len(dset & pset) / max(len(dset | pset), 1)))
    o = pd.DataFrame(ovl, columns=["date", "inter", "n_dcf", "n_pe", "jaccard"])
    tot_i, tot_d = o.inter.sum(), o.n_dcf.sum()
    print(f"  victim overlap: {tot_i}/{tot_d} DCF-dropped names also dropped by the PE rule "
          f"({100*tot_i/tot_d:.1f}%); per-date Jaccard mean {o.jaccard.mean():.3f} / "
          f"median {o.jaccard.median():.3f} / max {o.jaccard.max():.3f}")

    # --- [2] 3-way metrics table ------------------------------------------------------------------
    print("\n=== [2] 3-WAY METRICS (baseline / DCF-exclude / PE-highest-exclude) " + "=" * 10)
    print(f"{'window':<12} {'arm':<12} {'CAGR%':>8} {'Sharpe':>8} {'MaxDD%':>8} {'Calmar':>8}")
    for wname, w0, w1 in WINDOWS:
        for name, s in (("ctrl", ctrl), ("varA(DCF)", vara), ("placeboPE", pepl)):
            m = win(s, w0, w1)
            print(f"{wname:<12} {name:<12} {m['cagr']:>8.2f} {m['sharpe']:>8.3f} "
                  f"{m['mdd']:>8.2f} {m['calmar']:>8.3f}")

    # --- [3] where does placebo_pe sit vs the Pha-4 random null AND vs varA? --------------------
    print("\n=== [3] DELTAS vs ctrl — placeboPE inside the random null; gap to varA " + "=" * 7)
    seed_files = sorted(glob.glob(f"{BASE}_exp_dcfplacebo[0-9]*.csv"),
                        key=lambda p: int(p.split("dcfplacebo")[1].split(".")[0]))
    # seeds are 07-14 vintage -> delta vs THEIR OWN ctrl (c14); varA/placeboPE are 07-15 vintage
    # -> delta vs ctrl15. Each arm is differenced within its own vintage; only the comparison of
    # deltas crosses vintages (deltas are robust to the level revision, but flagged as such).
    seeds = [deltas_vs_ctrl(nav_series(p), c14) for p in seed_files]
    a_d, p_d = deltas_vs_ctrl(vara, ctrl), deltas_vs_ctrl(pepl, ctrl)
    print(f"  ({len(seeds)} random seeds loaded as null — 07-14 vintage, delta vs own ctrl)")
    print(f"{'window':<12} {'metric':<8} {'null mean±SD':>16} {'varA':>8} {'z_A':>6} "
          f"{'placeboPE':>10} {'z_PE':>6} {'A−PE':>8}")
    for wname, _, _ in WINDOWS:
        for metric in ("cagr", "sharpe", "calmar"):
            null = np.array([d[wname][metric] for d in seeds], dtype=float)
            null = null[np.isfinite(null)]
            mu, sd = null.mean(), null.std(ddof=1)
            xa, xp = a_d[wname][metric], p_d[wname][metric]
            za = (xa - mu) / sd if sd > 0 else np.nan
            zp = (xp - mu) / sd if sd > 0 else np.nan
            print(f"{wname:<12} {metric:<8} {mu:>9.3f}±{sd:<6.3f} {xa:>8.3f} {za:>6.2f} "
                  f"{xp:>10.3f} {zp:>6.2f} {xa - xp:>8.3f}")

    # --- [4] paired daily-return test varA vs placeboPE ------------------------------------------
    print("\n=== [4] varA vs placeboPE — paired daily log-return t (same convention as Pha 3) ===")
    from scipy import stats as st
    ra = np.log(vara / vara.shift(1)).dropna()
    rp = np.log(pepl / pepl.shift(1)).dropna()
    common = ra.index.intersection(rp.index)
    diff = (ra[common] - rp[common]).dropna()
    t, p = st.ttest_1samp(diff, 0.0)
    print(f"  n={len(diff)}  mean diff {diff.mean()*1e4:+.2f} bps/day  t={t:+.2f}  p={p:.3f}")
    rb = np.log(ctrl / ctrl.shift(1)).dropna()
    for nm, rr in (("varA-ctrl", ra), ("placeboPE-ctrl", rp)):
        c2 = rr.index.intersection(rb.index)
        d2 = (rr[c2] - rb[c2]).dropna()
        t2, p2 = st.ttest_1samp(d2, 0.0)
        print(f"  {nm}: mean {d2.mean()*1e4:+.2f} bps/day  t={t2:+.2f}  p={p2:.3f}")

    # --- [5] per-year deltas (the 2017/2021 concentration question) ------------------------------
    print("\n=== [5] PER-YEAR total-return delta vs ctrl (pp) " + "=" * 26)
    def yearly(s):
        return {y: (s[s.index.year == y].iloc[-1] / s[s.index.year == y].iloc[0] - 1) * 100
                for y in sorted(set(s.index.year)) if len(s[s.index.year == y]) > 4}
    y_c, y_a, y_p = yearly(ctrl), yearly(vara), yearly(pepl)
    print(f"{'year':<6}{'varA Δ':>10}{'placeboPE Δ':>13}{'A−PE':>9}")
    for y in sorted(y_c):
        if y in y_a and y in y_p:
            da, dp = y_a[y] - y_c[y], y_p[y] - y_c[y]
            print(f"{y:<6}{da:>10.2f}{dp:>13.2f}{da - dp:>9.2f}")

    print("\n=== [6] DECISION READ " + "=" * 56)
    print("  (a) varA >> placeboPE (gap ≈ varA's own delta, placeboPE ≈ null/ctrl)")
    print("      -> the DCF gate is NOT the trivial PE rule in disguise at the gate level.")
    print("  (b) varA ≈ placeboPE -> DCF adds nothing over a one-line PE rule: NO-GO.")
    print("  Either way: 2017/2021 concentration + DSR/N-trials still gate any GO (see [5] and")
    print("  loo_dsr_dcf.py) — this test alone cannot upgrade the verdict past those.")


if __name__ == "__main__":
    main()
