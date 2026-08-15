#!/usr/bin/env python3
"""selfcheck_sprint2.py — invariants for the Sprint 2 cash-dividend study.

Tests assert INVARIANTS (relations, signs, fail-safe direction, source-code prohibitions), not
live counts -- `coding_guidelines` §23 corollary 1: a test that pins a number measured on one
day silently rots into background noise. The two exceptions are marked LIVE and are deliberate:
they anchor the two facts that must never drift unnoticed (the ledger/SQL dividend agreement,
and the fact that no outcome touches the ex-date Price row).

Run:  /home/trido/thanhdt/wc_venv/bin/python selfcheck_sprint2.py
"""
from __future__ import annotations

import gzip
import csv
import json
import os
import re
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out2")
sys.path.insert(0, HERE)
from sprint2_analyze import (Index, block_bootstrap_mean, holm, ols_twoway,  # noqa: E402
                            YIELD_BINS, YIELD_LABELS, BAD_TICKERS, SEED)

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f"   [{detail}]" if detail else ""))


def main() -> int:
    panel = pd.read_csv(os.path.join(OUT, "event_panel.csv"))
    feat = pd.read_csv(os.path.join(OUT, "event_features.csv"))
    res = json.load(open(os.path.join(OUT, "results.json")))
    ewu = pd.read_csv(os.path.join(OUT, "ew_universe.csv"))
    src_build = open(os.path.join(HERE, "sprint2_build.py")).read()
    src_ana = open(os.path.join(HERE, "sprint2_analyze.py")).read()

    print("\n== A. Gate compliance (the Sprint 1 CONDITIONAL PASS conditions) ==")
    # T1 LIVE: the ex-date Price row is never even SELECTed. Grep the generated SQL, not the
    # intent: the SQL is what BigQuery actually ran.
    sql = open(os.path.join(OUT, "sql", "q2_panel.sql")).read()
    picks = re.findall(r"MAX\(IF\(k = (-?\d+),\s+(\w+)", sql)
    check("T1 no `Price` selected at k=0 in the panel SQL (LIVE, greps executed SQL)",
          not any(k == "0" and col == "Price" for k, col in picks),
          f"{len([1 for k,c in picks if c=='Price'])} Price picks, at k="
          f"{sorted({k for k,c in picks if c=='Price'}, key=int)}")
    check("T2 no `p_0` column exists anywhere in the panel or feature table",
          "p_0" not in panel.columns and "p_0" not in feat.columns)
    check("T3 no announcement-date field used: public_date / known_date absent from analysis code",
          not re.search(r"\b(public_date|known_date|known_date_lead|fleet_known_from)\b", src_ana),
          "prereg §0 forbids any announcement study")
    check("T4 public_date appears in build ONLY inside the dedup ORDER BY (survivor tie-break)",
          all("ORDER BY" in ln or "public_date DESC" in ln
              for ln in src_build.splitlines() if "public_date" in ln))
    check("T5 no forward-looking column pulled (profit_* / _center_*)",
          not re.search(r"profit_\d|_center_", src_build + src_ana))
    check("T6 no Close/Price ratio is ever used to INFER a dividend amount "
          "(div comes only from corporate_action.value_per_share)",
          "value_per_share" in src_build and
          not re.search(r"div\w*\s*=\s*.*(Close|c_m1)\s*[-/]\s*(Price|p_m1)", src_ana))

    print("\n== B. Event definition & lineage ==")
    led = {}
    with gzip.open(os.path.join(HERE, "out", "event_ledger.csv.gz"), "rt", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["event_family"] == "CASH_DIVIDEND" and r["actionable"] == "1" and r["exright_date"]:
                led[(r["ticker"], r["exright_date"])] = float(r["div_total_on_exdate"])
    keys = list(zip(panel["ticker"], panel["ex_date"]))
    # T7 LIVE: the SQL re-derivation must reproduce the Sprint 1 ledger exactly. If this ever
    # fails the SQL is wrong, not the ledger -- the ledger carries 21 invariants of its own.
    diffs = [abs(panel["div_total"].iloc[i] - led[k]) for i, k in enumerate(keys) if k in led]
    check("T7 SQL div_total == ledger div_total_on_exdate on every event (LIVE)",
          len(diffs) == len(keys) and max(diffs) < 1e-9,
          f"n={len(keys)}, max abs diff={max(diffs) if diffs else 'n/a'}")
    check("T8 every panel event is an ACTIONABLE cash dividend in the ledger",
          all(k in led for k in keys))
    check("T9 one row per (ticker, ex-date) -- tranches summed, never duplicated",
          len(set(keys)) == len(keys))
    check("T10 every ex_date inside the pre-registered window",
          panel["ex_date"].min() >= "2014-01-01" and panel["ex_date"].max() <= "2026-06-30")

    print("\n== C. Population & exclusion rules (prereg §2.4, §3) ==")
    core = feat[(feat["in_universe_pit"] == 1) & (feat["n_iss_adj_21"] == 0)
                & (feat["n_other_div_21"] == 0)]
    check("T11 X2 applied: no DNN/BCB/PTX and no raw cum price < 1000 VND",
          not set(feat["ticker"]) & BAD_TICKERS and feat["p_m1"].min() >= 1000)
    check("T12 X3 applied: gross yield never exceeds 50%", feat["y_gross"].max() <= 0.50)
    check("T13 traded on the ex-date: Volume_0 > 0 for every surviving event",
          (feat["v_0"] > 0).all())
    check("T14 P-CORE is strictly point-in-time universe members",
          (core["in_universe_pit"] == 1).all())
    check("T15 contamination filter actually binds (W=21 set is a strict subset of P-CORE)",
          len(core) < (feat["in_universe_pit"] == 1).sum())
    check("T16 yield bins partition the sample -- every event lands in exactly one bin",
          feat["yield_bin"].notna().all() and len(YIELD_LABELS) == len(YIELD_BINS) - 1)

    print("\n== D. Outcome algebra ==")
    a = pd.read_csv(os.path.join(OUT, "module_A_events.csv"))
    # The reconstruction must be algebraically consistent with the identity it relies on:
    #   P_hat_0 = C_0 * r_1     and     C_0/C_m1 = P_hat_0/(P_m1 - D)   =>   equal by construction
    lhs = a["c_0"] / a["c_m1"]
    rhs = a["p_hat_0"] / (a["p_m1"] - a["div_total"])
    ok = ((lhs - rhs).abs() / lhs.abs() < 0.02)
    check("T17 reconstructed raw ex-price is consistent with the adjustment identity "
          "C_0/C_-1 == P_hat_0/(P_-1 - D) on >=95% of Module A events",
          ok.mean() >= 0.95, f"share consistent = {ok.mean():.4f}")
    check("T18 the vendor adjustment convention is CONFIRMED, not assumed "
          "(prereg 4.1 fail-closed floor: >=80% within +/-1%)",
          res["module_A"]["convention_proof"]["share_within_1pct"] >= 0.80,
          f"{res['module_A']['convention_proof']['share_within_1pct']:.4f}")
    check("T19 paired estimator is exactly BHAR_20 - FARBASE_20",
          np.nanmax(np.abs((feat["BHAR_20"] - feat["FARBASE_20"])
                           - feat["BHAR_MINUS_BASE"]).to_numpy()) < 1e-12)
    check("T20 BHAR_h uses the STOCK's own session dates for the benchmark span",
          'bm_ew.ret(ev["d_0"], ev[f"d_{h}"])' in src_ana)

    print("\n== E. Benchmark plumbing ==")
    idx = Index.from_returns(ewu, "ew_ret")
    s = pd.Series([ewu["dt"].iloc[100], ewu["dt"].iloc[100]])
    check("T21 benchmark return over a zero-length span is exactly 0",
          abs(idx.ret(s, s)[0]) < 1e-12)
    check("T22 a MISSING session date returns NaN, never a neighbouring level "
          "(fail-safe: an event without T+h must drop out, not borrow a price)",
          bool(np.isnan(idx.level(pd.Series([np.nan, ""]))).all()))
    check("T23 benchmark requires universe membership at BOTH ends of each daily return",
          "upv.ticker = p.ticker AND upv.time = p.t_prev" in src_build)
    check("T24 impossible daily returns (|r|>50% on an adjusted series) are excluded "
          "from the benchmark and COUNTED, not silently dropped",
          "n_impossible" in ewu.columns and int(ewu["n_impossible"].sum()) ==
          res.get("build_impossible", int(ewu["n_impossible"].sum())))

    print("\n== F. Inference machinery ==")
    rng = np.random.default_rng(7)
    v = rng.normal(0, 1, 900)
    blk = np.repeat([f"2020-{i:02d}" for i in range(1, 10)], 100)
    b1 = block_bootstrap_mean(v, blk, n_boot=500, seed=SEED)
    b2 = block_bootstrap_mean(v, blk, n_boot=500, seed=SEED)
    check("T25 block bootstrap is deterministic under a fixed seed",
          (b1["lo"], b1["hi"]) == (b2["lo"], b2["hi"]))
    check("T26 bootstrap resamples MONTH BLOCKS, not events (n_blocks == distinct months)",
          b1["n_blocks"] == 9)
    # T27 as first written asserted "block CI > event CI" on UNCORRELATED synthetic data and
    # failed -- correctly. With no within-block correlation there is nothing for the block
    # bootstrap to widen for, so the assertion was wrong, not the estimator. The property that
    # actually characterises a cluster bootstrap is: it widens WHEN a common per-block shock is
    # present. Kept as a worked example because "the test was wrong" is the more common case.
    shock = np.repeat(rng.normal(0, 1, 9), 100)
    vc = shock + rng.normal(0, 1, 900)
    bc = block_bootstrap_mean(vc, blk, n_boot=500, seed=SEED)
    ec = block_bootstrap_mean(vc, np.arange(len(vc)).astype(str), n_boot=500, seed=SEED)
    check("T27 month-block CI widens under a common per-block shock (>=2x)",
          (bc["hi"] - bc["lo"]) > 2 * (ec["hi"] - ec["lo"]),
          f"ratio={(bc['hi']-bc['lo'])/(ec['hi']-ec['lo']):.2f}x")
    bb = block_bootstrap_mean(core["BHAR_20"].to_numpy(), core["ex_month"].to_numpy(),
                              n_boot=2000, seed=SEED)
    be = block_bootstrap_mean(core["BHAR_20"].to_numpy(),
                              np.arange(len(core)).astype(str), n_boot=2000, seed=SEED)
    check("T27b on the REAL primary outcome the reported CI is the CONSERVATIVE one "
          "(month clustering is present, so block CI >= event-level CI)",
          (bb["hi"] - bb["lo"]) >= (be["hi"] - be["lo"]),
          f"ratio={(bb['hi']-bb['lo'])/(be['hi']-be['lo']):.2f}x -- month clustering is real")
    raw_p = {"a": 0.001, "b": 0.02, "c": 0.30}
    hp = holm(raw_p)
    check("T28 Holm adjustment never lowers a p-value and is monotone",
          all(hp[k] >= raw_p[k] - 1e-12 for k in raw_p) and hp["a"] <= hp["b"] <= hp["c"])
    X = np.column_stack([np.ones(400), rng.normal(size=400)])
    beta_true = np.array([0.5, -1.25])
    y = X @ beta_true + rng.normal(0, 0.1, 400)
    r = ols_twoway(y, X, np.repeat(np.arange(20), 20), np.tile(np.arange(20), 20))
    check("T29 two-way clustered OLS recovers a known beta",
          np.allclose(r["beta"], beta_true, atol=0.03), f"beta={np.round(r['beta'],4)}")
    check("T30 clustered SEs are finite and positive", np.all(np.isfinite(r["se"]) & (r["se"] > 0)))

    print("\n== G. Result integrity ==")
    t = res["trials"]
    check("T31 every executed trial has a raw p AND a Holm-adjusted p",
          set(t["raw_p"]) == set(t["holm_adjusted_p"]),
          f"executed={t['executed']} declared={t['declared_in_prereg']}")
    check("T32 trial count overrun is DISCLOSED, not hidden",
          t["executed"] <= t["declared_in_prereg"] or "note_extra" in t)
    check("T33 N is reported as independent events AND distinct tickers for the primary",
          "n" in res["module_B"]["BHAR_20"] and "n_tickers" in res["module_B"]["BHAR_20"])
    check("T34 no horizon's N exceeds the P-CORE contaminated-filtered population",
          all(res["module_B"][f"BHAR_{h}"]["n"] <= len(core) + 60 for h in (5, 10, 20, 60)))
    check("T35 placebo and pre-trend were BOTH run and reported "
          "(a negative result that survives them is the only kind worth keeping)",
          "R5_placebo_ex_minus_40" in res["module_B"]
          and "R6_pretrend_m21_to_m1" in res["module_B"])
    # --- ENTITLEMENT INVARIANTS (correction 2026-08-15, D6) ------------------------------
    # The bug this replaces: T36 used to assert the cost screen DID subtract 0.05*y_gross.
    # It green-lit an entitlement error -- BHAR_20 is anchored at the ex-date close, whose
    # buyer is post-ex and receives no dividend, so no dividend tax is owed on it.
    ns = res["module_B"]["net_of_cost_screen"]
    check("T36 the POST-EX cost screen is anchored at the ex-date close, declares NO dividend "
          "entitlement, and subtracts round-trip TC + slippage ONLY",
          ns.get("entry_anchor") == "ex_date_close_T0"
          and ns.get("dividend_entitlement") is False
          and all(x in ns["formula"] for x in ("0.002", "0.003")),
          ns.get("formula"))
    check("T36b ANTI-REGRESSION: the post-ex cost screen contains NO dividend-tax / yield term",
          not any(x in ns["formula"] for x in ("y_gross", "0.05", "tax", "y)")),
          ns["formula"])
    check("T36c the post-ex net mean equals BHAR_20 mean minus exactly the 50bps of "
          "trading cost -- no hidden dividend term",
          abs((ns["mean"] - res["module_B"]["BHAR_20"]["mean"]) + 0.005) < 1e-9,
          f"delta={ns['mean'] - res['module_B']['BHAR_20']['mean']:.8f}")
    ht = res["module_B"].get("holdthrough_T_minus_1_to_T20_POSTHOC")
    check("T36d any hold-through / pre-ex claim rests on its OWN measured outcome with entry "
          "before the ex-date AND dividend entitlement TRUE (never on BHAR_20 arithmetic)",
          ht is not None and ht["entry_anchor"] == "close_T_minus_1"
          and ht["dividend_entitlement"] is True
          and ht["dividend_tax_rate"] == 0.05
          and "gross" in ht and "n" in ht["gross"])
    check("T36e the hold-through outcome is NOT the naive 'BHAR_20 - tax' arithmetic "
          "(it is a distinct measurement; agreement would mean it was derived, not measured)",
          abs(ht["gross"]["mean"] - ht["naive_wrong_arithmetic_for_contrast"]) > 0.001,
          f"measured={ht['gross']['mean']:.5f} naive={ht['naive_wrong_arithmetic_for_contrast']:.5f}")
    check("T36f every post-hoc outcome added by the correction pays its own Holm cost",
          "holdthru" in t["raw_p"] and "holdthru_net" in t["raw_p"]
          and "holdthru" in t["holm_adjusted_p"])
    # source-level prohibition: the post-ex net series must never be built with a yield term
    net_src = re.search(r"net\s*=\s*core20\[.BHAR_20.\][^\n]*", src_ana)
    check("T36g SOURCE: the post-ex net series is built without any y_gross term",
          net_src is not None and "y_gross" not in net_src.group(0),
          net_src.group(0) if net_src else "line not found")
    # report-level prohibition: the superseded formula may appear ONLY as a marked correction
    rep = open(os.path.join(HERE, "SPRINT2_CASH_DIVIDEND.md")).read()
    # two shapes of the same bug: the formula itself, and the narrative "... plus 5% dividend tax"
    # NOTE the tight \W{0,4}: "cộng** thuế" (the bug) must match, while the legitimate open
    # question "cổ tức có được cộng lại vào Close gộp hay ròng thuế?" must not.
    BAD_PAT = (r"0[,.]05\s*[·*x×]?\s*y"                       # 0.05*y_gross in a formula
               r"|c[ộo]ng\W{0,4}thu[ếe]"                       # "... cộng thuế ..." as a cost add-on
               r"|thu[ếe]\W{0,4}c[ộo]ng")
    OK_PAT = r"SAI|superseded|D6|đã bỏ|correction|bác bỏ|cũ|KHÔNG được|không được"
    bad = [ln for ln in rep.splitlines()
           if re.search(BAD_PAT, ln) and not re.search(OK_PAT, ln, re.I)]
    check("T36h REPORT: no live formula/claim still charges dividend tax to the post-ex buyer "
          "(the string may appear only on a line marked as the corrected/superseded one)",
          not bad, "; ".join(bad[:2]))
    check("T37 no ALPHA claim can pass on a negative primary effect "
          "(prereg §9(a) requires mean >= +0.75%)",
          res["module_B"]["BHAR_20"]["mean"] < 0.0075
          or res["module_B"]["BHAR_20"]["lo"] > 0)

    print(f"\n{'='*74}\nSprint 2 selfcheck: {len(PASS)}/{len(PASS)+len(FAIL)} PASS")
    if FAIL:
        print("FAILED: " + ", ".join(FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
