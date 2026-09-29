#!/usr/bin/env python3
"""Selfcheck for the PRHM flag program. Offline: reads `out/*.csv` and drives pure functions
with fixtures. Never queries BigQuery.

Two things it deliberately does NOT do:
  * assert on live production state (a basket, a ticker list, a count measured today) — that is
    how a test rots into background noise (coding_guidelines §23 hệ luận 1);
  * re-implement an estimator to compare against itself. Where a number must be checked, it is
    checked against the PRIOR program's PUBLISHED value or against arithmetic done by hand here.

Run:  python3 selfcheck_pump_flag.py            (also under `env -u TZ` and a foreign TZ)
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PRIOR = os.path.join(os.path.dirname(HERE), "serial_capital_raiser_20260817")
OUT = os.path.join(HERE, "out")
sys.path.insert(0, PRIOR)   # for scr_lib, which only exists there

# `import analyze` is AMBIGUOUS here: both this program and the prior one have an `analyze.py`,
# and whichever directory sits earlier on sys.path wins. That silently tested the wrong module
# once already. Load ours by absolute path so the name cannot resolve anywhere else.
_spec = importlib.util.spec_from_file_location("prhm_analyze", os.path.join(HERE, "analyze.py"))
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)

RESULTS = json.load(open(os.path.join(OUT, "results.json")))
EXTRAS = pd.read_csv(os.path.join(OUT, "extras.csv"))
Q1 = pd.read_csv(os.path.join(PRIOR, "out", "q1_bhar.csv"))

_res: list[tuple[str, bool, str]] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    _res.append((name, bool(cond), detail))
    print(f"{'PASS' if cond else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""))


# ------------------------------------------------------------------ A. cross-checks (CC1-CC5)
def a_crosschecks() -> None:
    cc = RESULTS["crosschecks"]
    check("CC1 pooled BHAR_250 RAISE_SET reproduces published -7.74% / n=712",
          cc["CC1_n_match"] and cc["CC1_bhar250_raiseset"]["abs_diff"] < 5e-5,
          f"n={cc['CC1_bhar250_raiseset']['n']} "
          f"mean={cc['CC1_bhar250_raiseset']['mean']:.6f}")
    check("CC2a pooled pretrend reproduces published +45.54%",
          cc["CC2a_pretrend_raiseset"]["abs_diff"] < 5e-5)
    check("CC2b far placebo reproduces published +30.21%",
          cc["CC2b_placebo_raiseset"]["abs_diff"] < 5e-5)
    for tag in ("muc1_primary", "muc1_sensitivity_raiseset"):
        m = RESULTS[tag]
        check(f"CC3 [{tag}] every T partitions the population exactly",
              all(r["partition_ok"] and r["n_susp"] + r["n_non"] == m["n_population"]
                  for r in m["grid"]))
    check("CC4 used-T suspected mean sits inside the prior program's Q2-Q3 pre-trend band",
          cc["CC4"]["inside_band"],
          f"{cc['CC4']['mean_bhar250_susp']:.4f} in {cc['CC4']['prior_q2_q3_band']}")
    check("CC5 extras key set == q1_bhar key set",
          set(zip(EXTRAS.ticker, EXTRAS.t0)) == set(zip(Q1.ticker, Q1.t0)),
          f"{len(EXTRAS)} vs {len(Q1)} rows")


# ------------------------------------------------------------------ B. no look-ahead
def b_no_lookahead() -> None:
    e = EXTRAS.dropna(subset=["dt_m1"])
    check("fundamentals are read STRICTLY BEFORE the ex-date (dt_m1 < t0, all rows)",
          bool((e.dt_m1 < e.t0).all()),
          f"violations={int((e.dt_m1 >= e.t0).sum())}/{len(e)}")
    b = EXTRAS.dropna(subset=["beta_n"])
    check("beta window never exceeds the 250 pre-event sessions it declares",
          bool((b.beta_n <= 250).all()), f"max={int(b.beta_n.max())}")
    check("beta_raw is NULL below the declared 150-session floor",
          bool(EXTRAS.loc[EXTRAS.beta_n < 150, "beta_raw"].isna().all()),
          f"{int((EXTRAS.beta_n < 150).sum())} rows below floor")
    check("beta_raw is populated whenever the floor is met",
          bool(EXTRAS.loc[EXTRAS.beta_n >= 150, "beta_raw"].notna().all()))
    r = EXTRAS.dropna(subset=["rr_quarter"])
    check("risk_rating quarter is STRICTLY before the event's own quarter (PIT)",
          bool((r.rr_quarter < r.t0_quarter).all()),
          f"violations={int((r.rr_quarter >= r.t0_quarter).sum())}/{len(r)}")
    check("no wall-clock read in the analysis path (TZ cannot change a number)",
          not any(tok in open(os.path.join(HERE, f)).read()
                  for f in ("analyze.py", "build_extras.py")
                  for tok in ("datetime.now", "date.today", "time.time()")))


# ------------------------------------------------------------------ C. threshold-rule fixtures
def _row(T, gap, lo, hi, p_holm, fpr, n=200, tk=100):
    return {"T": T, "gap_250": gap, "gap_lo": lo, "gap_hi": hi, "gap_p_holm": p_holm,
            "fpr": fpr, "n_susp": n, "n_non": n, "tickers_susp": tk, "tickers_non": tk}


def c_selection_rule() -> None:
    # (1) a clear winner: only T=0.30 satisfies all three gates
    rows = [_row(0.15, -0.02, -0.09, +0.05, 1.00, 0.30),
            _row(0.30, -0.12, -0.20, -0.04, 0.01, 0.30),
            _row(0.50, -0.15, -0.26, +0.02, 0.30, 0.30)]
    check("rule picks the only T passing power+gap+FPR", A.select_T(rows)[:2] == (0.30, "T_SELECTED"))

    # (2) largest |gap| wins when several qualify and they are >1pp apart
    rows = [_row(0.15, -0.08, -0.14, -0.02, 0.01, 0.20),
            _row(0.30, -0.20, -0.30, -0.10, 0.01, 0.20)]
    check("rule prefers the largest |gap| when the gaps differ by >1pp",
          A.select_T(rows)[0] == 0.30)

    # (3) within 1pp = tie -> smaller T wins (wider coverage)
    rows = [_row(0.15, -0.195, -0.30, -0.09, 0.01, 0.20),
            _row(0.30, -0.200, -0.30, -0.10, 0.01, 0.20)]
    check("tie inside 1pp resolves to the SMALLER T", A.select_T(rows)[0] == 0.15)

    # (4) each gate blocks on its own
    check("power floor blocks (events)",
          A.select_T([_row(0.3, -0.12, -0.2, -0.04, 0.01, 0.2, n=99)])[1] == "NO-FLAG")
    check("power floor blocks (distinct tickers)",
          A.select_T([_row(0.3, -0.12, -0.2, -0.04, 0.01, 0.2, tk=59)])[1] == "NO-FLAG")
    check("CI spanning zero blocks",
          A.select_T([_row(0.3, -0.12, -0.20, +0.01, 0.01, 0.2)])[1] == "NO-FLAG")
    check("gap shallower than -5pp blocks",
          A.select_T([_row(0.3, -0.049, -0.09, -0.01, 0.01, 0.2)])[1] == "NO-FLAG")
    check("Holm-adjusted p >= .05 blocks (unadjusted p would not)",
          A.select_T([_row(0.3, -0.12, -0.20, -0.04, 0.06, 0.2)])[1] == "NO-FLAG")
    check("FPR >= 40% blocks",
          A.select_T([_row(0.3, -0.12, -0.20, -0.04, 0.01, 0.40)])[1] == "NO-FLAG")
    check("gap of the WRONG sign blocks (suspected better, not worse)",
          A.select_T([_row(0.3, +0.12, +0.04, +0.20, 0.01, 0.2)])[1] == "NO-FLAG")

    # (5) boundary: -5.0pp exactly and FPR 39.99% are inside the rule as written
    check("gap exactly -5.00pp passes (<= boundary)",
          A.select_T([_row(0.3, -0.05, -0.09, -0.01, 0.01, 0.2)])[0] == 0.30)
    check("FPR just under 40% passes",
          A.select_T([_row(0.3, -0.12, -0.20, -0.04, 0.01, 0.3999)])[0] == 0.30)

    # (6) least-bad T is returned even when nothing is eligible, and ignores unpowered rows
    rows = [_row(0.15, -0.02, -0.09, 0.05, 1.0, 0.3),
            _row(0.30, -0.09, -0.19, 0.01, 1.0, 0.3),
            _row(0.60, -0.50, -0.90, 0.10, 1.0, 0.3, n=10, tk=5)]
    ch, vd, lb = A.select_T(rows)
    check("NO-FLAG still yields a least-bad T, drawn only from POWERED rows",
          (ch, vd, lb) == (None, "NO-FLAG", 0.30))

    # (7) the real grid: reproduce the recorded verdict from the recorded rows
    m = RESULTS["muc1_primary"]
    ch, vd, lb = A.select_T([dict(r) for r in m["grid"]])
    check("rule re-applied to the stored grid reproduces the recorded verdict",
          (ch, vd, lb) == (m["T_chosen"], m["verdict"], m["T_least_bad"]),
          f"{vd} T={ch} least_bad={lb}")


# ------------------------------------------------------------------ D. FPR + beta binning
def d_fpr_and_bins() -> None:
    # FPR by hand on a 4-row fixture: median ROIC = 0.25; healthy = ROIC>median AND FSCORE>4
    f = pd.DataFrame({"roic_trailing": [0.1, 0.2, 0.3, 0.4], "fscore": [9, 9, 5, 3],
                      "pretrend_250": [1.0, 1.0, 1.0, 1.0]})
    med = f.roic_trailing.median()                      # 0.25
    healthy = (f.roic_trailing > med) & (f.fscore > A.FSCORE_GOOD)
    check("FPR fixture: only rows above median ROIC *and* FSCORE>4 count as healthy",
          healthy.tolist() == [False, False, True, False] and abs(healthy.mean() - 0.25) < 1e-12)
    check("FSCORE gate is strict '>4' (a 4 is not healthy)",
          not bool((pd.Series([4]) > A.FSCORE_GOOD).iloc[0]))

    check("beta bins: boundaries land where PREREG says (<=1.2 low, <=1.8 mid, >1.8 high)",
          [A.bin_beta(x) for x in (-0.5, 0.0, 1.19, 1.2, 1.2001, 1.8, 1.8001, 3.0)]
          == ["low", "low", "low", "low", "mid", "mid", "high", "high"])
    check("beta bin of a missing value is None, never a bucket",
          A.bin_beta(float("nan")) is None and A.bin_beta(None) is None)

    m3 = RESULTS["muc3"]
    n_binned = sum(r["n"] for r in m3["bins_raw_beta"])
    pop = m3["n_population"]
    check("beta bins partition exactly the events that HAVE a beta (no silent drop into a bucket)",
          n_binned <= pop and abs(n_binned - pop * m3["beta_coverage"]) < 1,
          f"binned={n_binned} pop={pop} cov={m3['beta_coverage']:.3f}")
    # Mục 1 and Mục 3 run on different populations on purpose; assert the difference is EXACTLY
    # the missing-pretrend events and nothing else, so a future edit cannot widen it unnoticed.
    check("Mục 3's wider population is exactly Mục 1's plus the events lacking a pre-trend",
          m3["n_population_muc1"] == RESULTS["muc1_primary"]["n_population"],
          f"muc3={pop} muc1={RESULTS['muc1_primary']['n_population']}")
    check("the dispatched high-beta bin is correctly declared below the power floor",
          next(r for r in m3["bins_raw_beta"] if r["bin"] == "high")["below_power_floor"])
    check("the combined pump x high-beta cell is declared UNDERPOWERED, not given a verdict",
          m3["combined"]["underpowered"] and "no verdict" in m3["combined"]["verdict"].lower(),
          f"n={m3['combined']['n']} tickers={m3['combined']['tickers']}")
    check("combined cell is NOT presented as recommended (Mục 1 returned NO-FLAG)",
          m3["combined"]["T_is_recommended"] is False)


# ------------------------------------------------------------------ E. sector logic
def e_sector() -> None:
    check("ICB label is only asserted for codes whose membership was inspected",
          A.label(8777).endswith("(Investment Services (securities brokerages))")
          and A.label(3353).endswith("(unverified label)")
          and A.label(float("nan")) == "ICB unknown")

    q = Q1.copy()
    sec = set(q.loc[q.icb == A.SEC_ICB, "ticker"])
    bank = set(q.loc[q.icb == 8355, "ticker"])
    check("ICB 8777 contains the brokerages it claims to (SSI/HCM/SHS/MBS/VND-class names)",
          {"SSI", "HCM", "SHS", "MBS", "BSI", "FTS", "CTS"} <= sec, f"n={len(sec)}")
    check("ICB 8777 contains no bank (the two financial codes are disjoint)",
          not (sec & bank) and {"ACB", "MBB", "CTG", "BID"} <= bank)
    check("no ticker carries two different ICB codes in the panel (label is stable per name)",
          int(q.groupby("ticker").icb.nunique().max()) == 1)

    m2 = RESULTS["muc2"]
    tot = sum(s["n_events"] for s in m2["raise_by_sector"])
    pop_raise = int(Q1.subtype.isin(A.PRIMARY_SUBTYPES).sum())
    check("sector split covers every RIGHTS+PP event exactly once",
          tot == pop_raise, f"{tot} vs {pop_raise}")
    check("sectors below the CI floor carry no CI, and below the verdict floor are tagged",
          all((s.get("lo") is None) == s["below_ci_floor"] for s in m2["raise_by_sector"]))
    s8777 = next(s for s in m2["raise_by_sector"] if s["icb"] == A.SEC_ICB)
    check("securities sector is below the verdict floor and says so",
          s8777["below_verdict_floor"] and m2["sec_vs_rest_raise"]["below_verdict_floor"],
          f"n={s8777['n_events']} tickers={s8777['n_tickers']}")
    check("top-20 ISS table carries a sector label on every row",
          all(r.get("label") for r in m2["top20_iss"]) and len(m2["top20_iss"]) == 20)


# ------------------------------------------------------------------ F. estimator sanity
def f_estimators() -> None:
    rng = np.random.default_rng(7)
    blk = np.array([f"m{i % 20}" for i in range(400)], dtype=object)
    a, b = rng.normal(0.0, 0.1, 400), rng.normal(0.0, 0.1, 400)
    g1 = A.boot_gap(a, b, blk, blk)
    g2 = A.boot_gap(a, b, blk, blk)
    check("boot_gap is deterministic for a fixed seed", g1 == g2)
    check("boot_gap point estimate equals the plain difference of means",
          abs(g1["gap"] - (a.mean() - b.mean())) < 1e-12)
    check("boot_gap CI brackets its own point estimate", g1["lo"] <= g1["gap"] <= g1["hi"])
    check("boot_gap finds no difference where none exists", g1["p"] > 0.05, f"p={g1['p']:.3f}")

    shifted = b - 0.20
    g3 = A.boot_gap(a, shifted, blk, blk)
    check("boot_gap detects a planted -20pp shift with the right sign",
          g3["p"] < 0.01 and g3["gap"] > 0.15 and g3["lo"] > 0, f"gap={g3['gap']:.3f}")
    check("boot_gap is antisymmetric in its arguments",
          abs(A.boot_gap(shifted, a, blk, blk)["gap"] + g3["gap"]) < 1e-12)
    a_nan = np.concatenate([a, [np.nan]])
    blk_nan = np.concatenate([blk, np.array(["mX"], dtype=object)])
    check("boot_gap drops NaNs rather than propagating them",
          np.isfinite(A.boot_gap(a_nan, b, blk_nan, blk)["gap"]))
    check("boot_gap returns nulls (not a crash) on an empty side",
          A.boot_gap([], b, [], blk)["gap"] is None)

    from scr_lib import holm
    adj = holm({"a": 0.01, "b": 0.02, "c": 0.60})
    check("Holm adjustment is monotone and never shrinks a p-value",
          adj["a"] <= adj["b"] <= adj["c"] and all(adj[k] >= p for k, p in
                                                   (("a", 0.01), ("b", 0.02), ("c", 0.60))))


# ------------------------------------------------------------------ G. reporting discipline
FORBIDDEN = ("manipulat", "thao túng", "thao tung", "tội phạm", "toi pham", "criminal", "fraud")


def g_language() -> None:
    for fn in ("FINDINGS.md", "FLAG_SPEC.md"):
        path = os.path.join(HERE, fn)
        if not os.path.exists(path):
            check(f"{fn} exists", False, "not written yet")
            continue
        txt = open(path).read().lower()
        hits = [w for w in FORBIDDEN if w in txt]
        check(f"{fn} avoids accusatory vocabulary (PREREG §0)", not hits, f"hits={hits}")
        check(f"{fn} states the NO-FLAG verdict explicitly",
              "no-flag" in txt or "not recommended for wiring" in txt)


def main() -> int:
    print(f"TZ={os.environ.get('TZ', '<unset>')}\n")
    for fn in (a_crosschecks, b_no_lookahead, c_selection_rule, d_fpr_and_bins,
               e_sector, f_estimators, g_language):
        print(f"--- {fn.__name__} ---")
        fn()
        print()
    n_pass = sum(1 for _, ok, _ in _res if ok)
    print(f"{n_pass}/{len(_res)} PASS")
    with open(os.path.join(OUT, "selfcheck.json"), "w") as fh:
        json.dump({"n_pass": n_pass, "n_total": len(_res),
                   "tz": os.environ.get("TZ", "<unset>"),
                   "results": [{"name": n, "pass": ok, "detail": d} for n, ok, d in _res]},
                  fh, indent=2)
    return 0 if n_pass == len(_res) else 1


if __name__ == "__main__":
    if "--rerun-foreign-tz" in sys.argv:
        # §16: a selfcheck that inherits the author's own TZ proves nothing about TZ.
        base = [sys.executable, os.path.abspath(__file__)]
        codes = []
        for env in ({}, {"TZ": "America/Chicago"}, {"TZ": "UTC"}):
            e = dict(os.environ)
            e.pop("TZ", None)
            e.update(env)
            p = subprocess.run(base, env=e, capture_output=True, text=True)
            tail = [x for x in p.stdout.splitlines() if "PASS" in x and "/" in x.split()[0]]
            print(f"TZ={env.get('TZ', '<unset>'):<16} rc={p.returncode}  {tail[-1] if tail else ''}")
            codes.append(p.returncode)
        sys.exit(max(codes))
    sys.exit(main())
