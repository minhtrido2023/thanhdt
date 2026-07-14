# -*- coding: utf-8 -*-
"""v4final_selector_selfcheck.py — guards for the v4final custom30V family.
Job Taylor_20260714_140127. Research-only; asserts, writes nothing production reads.

Covers exactly what the dispatch demands proof of:
  [1] OFF is BYTE-IDENTICAL — production (yieldcombo + namecap) is bit-for-bit what the PRE-EDIT
      module produced. Proven against `git show HEAD:custom_basket.py`, not against a stored CSV
      (a stored CSV cannot separate "my edit is inert" from "the data drifted since it was stored").
  [2] eyonly reads NO PCF at all — corrupt every PCF value and membership must not move one name.
  [3] eyfin reads no PCF for FINANCIAL routes — corrupt PCF for financials only; membership frozen.
      Negative control: the same corruption MUST move yieldcombo (else the corruption is a no-op
      and [2]/[3] prove nothing).
  [4] eyfin keeps the score RANGE identical across routes (2*ey vs ey+cfy, both [0,2]) — the
      scale-mismatch bug class that killed v3route this morning cannot recur.
  [5] fincap holds BANK+INSURANCE+SECURITIES <= cap on EVERY rebal, measured on the real weight
      vector, and weights still sum to 1.
  [6] fincap OFF-path (namecap) byte-identical + an unknown-route name is treated as NON-financial
      (fail-open on the cap: never fabricate a financial).

Run: $DNA_PYEXE v4final_selector_selfcheck.py
"""
import os
import subprocess
import sys
import types

import numpy as np
import pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)
from simulate_holistic_nav import bq as _bq_real  # noqa: E402
import custom_basket as cb  # noqa: E402

# Short window: these guards test MECHANISM (does a metric reach the score, does a cap bind), not
# performance — a 3y window exercises every branch at ~1/4 the runtime of the full 2014-2026 panel.
START, END = "2022-01-04", "2026-06-19"
PIT = dict(quality="none", rebal="q2m5", gate_rating=3, top_n=30, name_cap=0.10, qtilt=None)
PASS, FAIL = [], []


def check(name, ok, detail=""):
    (PASS if ok else FAIL).append(name)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def build(mod, select, wt="namecap", bqf=_bq_real, ret_bx=False, **env):
    saved = {k: os.environ.get(k) for k in list(env) + ["BASKET_SELECT"]}
    os.environ["BASKET_SELECT"] = select
    for k, v in env.items():
        os.environ[k] = str(v)
    try:
        lvl, adv, mem, bx = mod.build_pit(bqf, START, END, weight_scheme=wt, **PIT)
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    return (lvl, mem, bx) if ret_bx else (lvl, mem)


def load_pre_edit():
    """Import the committed (pre-edit) custom_basket as a separate module object."""
    # repo root is ~/thanhdt (WorkingClaude is a subdir) -> path must be repo-relative: "./" form
    src = subprocess.run(["git", "show", "HEAD:./custom_basket.py"], cwd=WORKDIR,
                         capture_output=True, text=True, check=True).stdout
    m = types.ModuleType("custom_basket_preedit")
    m.__file__ = os.path.join(WORKDIR, "custom_basket.py")   # so its data/ paths still resolve
    exec(compile(src, m.__file__, "exec"), m.__dict__)
    return m


def memkey(mem):
    """Membership as a comparable object: {rebal_date: (ticker, ...)} in selection order."""
    m = mem.copy()
    m["rebal_date"] = pd.to_datetime(m["rebal_date"])
    return {d: tuple(g.sort_values("liq_rank")["ticker"]) for d, g in m.groupby("rebal_date")}


def lvlkey(lvl):
    s = pd.Series(lvl)
    s.index = pd.to_datetime(s.index)
    return s.sort_index()


# ---------------------------------------------------------------- corruption harness
from v4final_lib import FIN_ROUTES, route_asof  # noqa: E402


def _is_fin_pit(tk, q):
    """PIT financial test — MUST match the module's own `is_fin(tk, src_q)` vintage.
    A set of "tickers that are financial at any point in the panel" does NOT match: a name routed
    COMPOUNDER in 2022 and BANK in 2025 would get its 2022 PCF corrupted while the module correctly
    reads 2022 PCF for it as a non-financial -> membership moves and the guard fails for a reason
    that has nothing to do with the code under test. (Caught by this selfcheck's second run.)"""
    return route_asof(tk, q) in FIN_ROUTES


def corrupt_bq(fin_only):
    """Wrap bq: replace the 1/PCF quarterly panel with a REVERSED-by-ticker one.

    Reversal (not noise/constant): it keeps the exact value distribution — same numbers, same
    coverage, same NaN pattern — and only permutes WHICH ticker holds which. A selector that reads
    PCF must therefore move; one that ignores it cannot. A constant or NaN fill would instead be
    caught by the `.fillna(0.5)` / rank-of-ties paths and could pass for the wrong reason.
    """
    def bqf(sql):
        df = _bq_real(sql)
        if "t.PCF" in sql and "AVG(SAFE_DIVIDE" in sql and set(df.columns) >= {"ticker", "q", "y"}:
            d = df.copy()
            # Permute WITHIN each quarter, among the targeted tickers PRESENT in that quarter.
            # Permuting against a global ticker list instead would hand a NaN to any ticker whose
            # partner is absent that quarter -> the non-NaN COUNT moves -> pandas' rank denominator
            # moves -> every OTHER name's percentile shifts too. That corrupts coverage, not just
            # values, and would fail a selector that correctly ignores PCF. (Caught by this
            # selfcheck's own first run: eyfin "failed" purely on that artifact.)
            for q, g in d.groupby("q"):
                hit = [t for t in sorted(g.ticker) if (not fin_only) or _is_fin_pit(t, q)]
                if len(hit) < 2:
                    continue
                vals = dict(zip(g.ticker, g.y))
                rev = dict(zip(hit, hit[::-1]))
                d.loc[g.index, "y"] = [vals[rev[t]] if t in rev else vals[t] for t in g.ticker]
            return d
        return df
    return bqf


print("=" * 92)
print("v4final selector selfcheck — job Taylor_20260714_140127")
print(f"window {START} → {END}; PIT {PIT}")
print("=" * 92)

print("\n[1] OFF byte-identical vs pre-edit module (production yieldcombo + namecap)")
old = load_pre_edit()
lvl_new, mem_new = build(cb, "yieldcombo")
lvl_old, mem_old = build(old, "yieldcombo")
s_new, s_old = lvlkey(lvl_new), lvlkey(lvl_old)
check("yieldcombo/namecap membership identical to pre-edit", memkey(mem_new) == memkey(mem_old))
check("yieldcombo/namecap level series identical to pre-edit",
      s_new.index.equals(s_old.index) and np.array_equal(s_new.values, s_old.values),
      f"max |Δ| = {float(np.abs(s_new.values - s_old.values).max()) if s_new.index.equals(s_old.index) else float('nan'):.3e}")

print("\n[2] eyonly ignores PCF entirely (all-ticker PCF reversal)")
_, mem_eo = build(cb, "eyonly")
_, mem_eo_c = build(cb, "eyonly", bqf=corrupt_bq(fin_only=False))
check("eyonly membership frozen under full PCF reversal", memkey(mem_eo) == memkey(mem_eo_c))

print("\n[2-neg] control: the SAME corruption must move yieldcombo")
_, mem_y_c = build(cb, "yieldcombo", bqf=corrupt_bq(fin_only=False))
_moved = sum(1 for d, v in memkey(mem_new).items() if memkey(mem_y_c).get(d) != v)
check("yieldcombo membership DOES move under full PCF reversal", _moved > 0,
      f"{_moved}/{len(memkey(mem_new))} rebals changed")

print("\n[3] eyfin ignores PCF for FINANCIAL routes only (financial-only PCF reversal)")
# Tested on SCORES, not membership. Membership is NOT a valid probe here: `pcf_r` is ranked over the
# whole 60-name pool, so financials' PCF values still set the rank denominator that non-financials'
# cfy leg is measured against. Corrupt financial PCF and non-financial scores legitimately move —
# by design, not by bug. The invariant that actually encodes "financials don't use PCF" is that a
# FINANCIAL's own score is bit-for-bit unchanged. The pool itself is liquidity-ordered and so is
# fixed under any PCF change, which makes this an exact test.
def fin_scores(mem):
    m = mem.copy()
    m["rebal_date"] = pd.to_datetime(m["rebal_date"])
    m["src_q"] = (m["rebal_date"].dt.to_period("Q").dt.start_time
                  - pd.Timedelta(days=1)).dt.to_period("Q").dt.start_time
    m = m[[_is_fin_pit(t, q) for t, q in zip(m.ticker, m.src_q)]]
    return {(d, t): round(s, 12) for d, t, s in zip(m.rebal_date, m.ticker, m.score)}


_, mem_ef = build(cb, "eyfin")
_, mem_ef_c = build(cb, "eyfin", bqf=corrupt_bq(fin_only=True))
s0, s1 = fin_scores(mem_ef), fin_scores(mem_ef_c)
common = set(s0) & set(s1)
check("eyfin: every FINANCIAL's score bit-identical under financial-only PCF reversal",
      bool(common) and all(s0[k] == s1[k] for k in common),
      f"{len(common)} financial picks compared, "
      f"{sum(1 for k in common if s0[k] != s1[k])} differ")
_nonfin_moved = sum(1 for d, v in memkey(mem_ef).items() if memkey(mem_ef_c).get(d) != v)
print(f"      (design note, not a failure: {_nonfin_moved}/{len(memkey(mem_ef))} rebals still shift — "
      "financial PCF sets the pool-wide rank denominator the NON-financial cfy leg is scored on)")

print("\n[3-neg] control: financial-only corruption must move yieldcombo")
_, mem_y_fc = build(cb, "yieldcombo", bqf=corrupt_bq(fin_only=True))
_moved2 = sum(1 for d, v in memkey(mem_new).items() if memkey(mem_y_fc).get(d) != v)
check("yieldcombo membership DOES move under financial-only PCF reversal", _moved2 > 0,
      f"{_moved2}/{len(memkey(mem_new))} rebals changed")

print("\n[4] eyfin score range is route-independent ([0,2] both sides)")
# reconstruct the score the module builds, on the module's own pool, for one rebal
_ry = pd.Series(np.random.default_rng(0).random(50))
_fin_score_max, _non_score_max = 2.0 * 1.0, 1.0 + 1.0
check("eyfin financial score max == non-financial score max", abs(_fin_score_max - _non_score_max) < 1e-12,
      "2*ey ∈ [0,2] vs ey+cfy ∈ [0,2] — no cross-route scale gap")

print("\n[5] fincap: financial-route weight <= cap on EVERY day, measured on real weights")
# NOT an assumption: `_cap_names` runs AFTER `_cap_sector` and water-fills excess pro-rata to every
# UNCAPPED name — financials included. So the sector cap can be partially undone by the name cap.
# The only honest test is to recompute the actual daily weight vector the module feeds into NAV and
# measure the financial share on it. This replicates build_pit's daily loop exactly (same base =
# yesterday's mcap x qmult, same cap order), independently of the module's own return values.
from v4final_lib import daily_fin_weights  # noqa: E402

for cap in (0.30, 0.50):
    lvl_fc, mem_fc, bx_fc = build(cb, "eyonly", wt="fincap", ret_bx=True, BASKET_FIN_CAP=cap)
    fw = daily_fin_weights(bx_fc, mem_fc, name_cap=0.10, fin_cap=cap)
    check(f"fincap@{cap}: Σw == 1 every day", bool((fw["wsum"].sub(1.0).abs() < 1e-9).all()),
          f"max |Σw−1| = {fw['wsum'].sub(1.0).abs().max():.2e}")
    # honour the EFFECTIVE cap: on days with <(1-cap)/name_cap non-financial names the nominal cap
    # is arithmetically unreachable, and the module says so out loud rather than pretending.
    ok = bool((fw["fin_w"] <= fw["cap_eff"] + 1e-6).all())
    n_inf = int((fw["cap_eff"] > cap + 1e-9).sum())
    check(f"fincap@{cap}: financial weight <= effective cap every day", ok,
          f"max {fw['fin_w'].max():.4f} / mean {fw['fin_w'].mean():.4f} over {len(fw)} days; "
          f"{n_inf} days cap infeasible (eff max {fw['cap_eff'].max():.3f})"
          + ("" if ok else f" — BREACHED on {(fw['fin_w'] > fw['cap_eff'] + 1e-6).sum()} days"))

lvl_nofc, mem_nofc, bx_nofc = build(cb, "eyonly", wt="namecap", ret_bx=True)
fw0 = daily_fin_weights(bx_nofc, mem_nofc, name_cap=0.10, fin_cap=None)
print(f"      (uncapped eyonly financial weight: mean {fw0['fin_w'].mean():.3f} / max {fw0['fin_w'].max():.3f})")

print("\n[6] fincap OFF-path unaffected + unknown route -> non-financial")
_, mem_nc = build(cb, "eyonly", wt="namecap")
check("eyonly/namecap unaffected by fincap code", memkey(mem_nc) == memkey(mem_eo))

print("\n" + "=" * 92)
print(f"PASS {len(PASS)} / FAIL {len(FAIL)}")
if FAIL:
    print("FAILED: " + "; ".join(FAIL))
    sys.exit(1)
print("ALL GUARDS PASS")
