# -*- coding: utf-8 -*-
"""
cctg_deposit_wiring_selfcheck.py — selfcheck for deposit_rate_vn.consumer_deposit_rate() and its
5 LIVE wiring points (job Taylor_20261001_054110, user-approved 2026-10-01 12:40 ICT):
  rating_8l.py (NEUTRAL deposit tilt), dcf_valuation.py::discount_rate(), dcf_refresh_gate.py,
  custom30_yield_labels.py (batch yield-floor), trading_bot/due_diligence.py (_deposit_rate_pct).

Round-2 fix (job Taylor_20261001_064225, quant-skeptic+arch-review NEEDS_CHANGES on the above):
sections 7-9 below cover R1 (check_freshness was never explicit, so the 3 consumers that pass an
explicit asof never aged a stale CCTG reading out) and R2 (a CCTG error/stale read degraded to
Big-4 SILENTLY -- no log, no trace in rate_source).

Pre-registers THIS checkout's deposit_rate_vn/cctg_rate_vn AND the 3 remaining consumer modules
that touch sys.path/cwd at their own import time (dcf_valuation.py, dcf_refresh_gate.py both
hardcode WORKDIR to the absolute production path and `sys.path.insert(0, WORKDIR)`
[+ dcf_valuation also `os.chdir()`s there]) in sys.modules BEFORE any plain `import X` statement
runs. Round-4 fix (job Taylor_20261001_073836, arch-review r2 follow-up): the ORIGINAL docstring
here claimed this protection already covered "any of the 5 consumer modules", but it only ever
pre-registered deposit_rate_vn/cctg_rate_vn — dcf_refresh_gate.py and custom30_yield_labels.py
were still loaded via a bare `import X` AFTER `import dcf_valuation` (section 5) had already run
dcf_valuation's own `sys.path.insert(0, WORKDIR)`. From that point on sys.path[0] is the
CANONICAL production path, so the later `import dcf_refresh_gate as DRG` / `import
custom30_yield_labels as C30` resolved to the PRODUCTION copies of those two files, not this
worktree's — a pre-merge selfcheck run could PASS while actually validating code that was never
touched by the fix under review. `_load_here()` below sidesteps sys.path entirely (explicit file
path via `importlib.util.spec_from_file_location`), so every one of the 5 consumer modules is
guaranteed to come from THIS checkout regardless of what any of them does to sys.path/cwd
afterwards. Once `sys.modules[name]` is populated this way, any later bare `import name` anywhere
(including inside another of these 5 modules) reuses that same object.

Run: python3 cctg_deposit_wiring_selfcheck.py   (and again under $DNA_PYEXE, and under
`env -u TZ TZ=America/New_York python3 ...` per the verify-before-done skill — none of the
asserts below pass a bare asof=None, so TZ should not matter here; running under a foreign TZ
is the check that proves that, not an assumption).
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import deposit_rate_vn as dep        # noqa: E402  (pre-register THIS checkout's copy first)
import cctg_rate_vn as cctg          # noqa: E402


def _load_here(modname, filename=None):
    """Load <modname> from THIS checkout's own file at HERE, bypassing sys.path entirely — see
    the module docstring for why a bare `import X` is not safe for dcf_valuation.py/
    dcf_refresh_gate.py/custom30_yield_labels.py once any one of them has mutated sys.path."""
    fp = os.path.join(HERE, filename or f"{modname}.py")
    spec = importlib.util.spec_from_file_location(modname, fp)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[modname] = mod
    spec.loader.exec_module(mod)
    return mod


_load_here("custom30_yield_labels")
_load_here("dcf_refresh_gate")
_load_here("dcf_valuation")

fails = []


def check(name, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        fails.append(name)


# ---- 0. path-trap guard: every pre-registered module must actually be THIS checkout's file -----
print("Path-trap guard (sys.modules pre-registration actually points at HERE, not canonical):")
for _modname in ("deposit_rate_vn", "cctg_rate_vn", "custom30_yield_labels",
                  "dcf_refresh_gate", "dcf_valuation"):
    _mod_file = os.path.abspath(sys.modules[_modname].__file__)
    check(f"sys.modules[{_modname!r}].__file__ is under HERE ({_mod_file})",
          _mod_file.startswith(HERE))


def with_overlay(flag, fn):
    old = os.environ.get("DEPOSIT_RATE_CCTG_OVERLAY")
    os.environ["DEPOSIT_RATE_CCTG_OVERLAY"] = flag
    try:
        return fn()
    finally:
        if old is None:
            os.environ.pop("DEPOSIT_RATE_CCTG_OVERLAY", None)
        else:
            os.environ["DEPOSIT_RATE_CCTG_OVERLAY"] = old


# ---- 1. consumer_deposit_rate() knob behavior, pure logic --------------------------------------
print("consumer_deposit_rate() — knob semantics:")
ANCHOR = "2026-09-30"          # cctg_rate_vn's one and only frozen anchor
PRE = "2026-09-29"
POST_TODAY = "2026-10-01"

check("knob=0 (today) == current_deposit_rate(today)",
      with_overlay("0", lambda: dep.consumer_deposit_rate(POST_TODAY)) == dep.current_deposit_rate(POST_TODAY))
check("knob=1 (today) == effective_deposit_rate(today)['rate_pct']",
      with_overlay("1", lambda: dep.consumer_deposit_rate(POST_TODAY)) == dep.effective_deposit_rate(POST_TODAY)["rate_pct"])
check("knob default (unset) behaves like knob=1",
      (os.environ.pop("DEPOSIT_RATE_CCTG_OVERLAY", None), dep.consumer_deposit_rate(POST_TODAY))[1]
      == dep.effective_deposit_rate(POST_TODAY)["rate_pct"])
check("post-anchor: effective > big4-only (CCTG 7.5% beats Big-4 12M 6.8%)",
      with_overlay("1", lambda: dep.consumer_deposit_rate(POST_TODAY)) > with_overlay("0", lambda: dep.consumer_deposit_rate(POST_TODAY)))
check("post-anchor rate_source is cctg_6m(...)",
      dep.effective_deposit_rate(POST_TODAY)["rate_source"].startswith("cctg_6m"))

# ---- 2. byte-identical history: knob must be a no-op for every asof before the CCTG anchor -----
print("\nHistory unaffected (pre-anchor byte-identical, both knob values):")
import pandas as pd  # noqa: E402

dates = pd.date_range("2014-01-01", PRE, freq="11D")
pre_mismatches_knob1 = []
pre_mismatches_knob0 = []
for d in dates:
    ds = str(d.date())
    big4 = dep.current_deposit_rate(ds)
    k1 = with_overlay("1", lambda ds=ds: dep.consumer_deposit_rate(ds))
    k0 = with_overlay("0", lambda ds=ds: dep.consumer_deposit_rate(ds))
    if k1 != big4:
        pre_mismatches_knob1.append((ds, big4, k1))
    if k0 != big4:
        pre_mismatches_knob0.append((ds, big4, k0))
check(f"knob=1 byte-identical to current_deposit_rate() for {len(dates)} pre-anchor dates",
      len(pre_mismatches_knob1) == 0)
check(f"knob=0 byte-identical to current_deposit_rate() for {len(dates)} pre-anchor dates",
      len(pre_mismatches_knob0) == 0)
if pre_mismatches_knob1:
    print("    mismatches (knob=1):", pre_mismatches_knob1[:5])

# anchor-day boundary: the day BEFORE the anchor must still be Big-4-only even under knob=1
check("day before anchor (2026-09-29) unaffected by knob=1",
      with_overlay("1", lambda: dep.consumer_deposit_rate(PRE)) == dep.current_deposit_rate(PRE))
check("anchor day itself (2026-09-30) IS affected by knob=1",
      with_overlay("1", lambda: dep.consumer_deposit_rate(ANCHOR)) != dep.current_deposit_rate(ANCHOR))

# ---- 3. the 5 call sites actually call consumer_deposit_rate(), not a stale import --------------
print("\nCall-site wiring (grep-equivalent, read the actual source text):")
import re  # noqa: E402

SITES = {
    "rating_8l.py": r"from deposit_rate_vn import consumer_deposit_rate_detail",
    "dcf_valuation.py": r"_dep\.consumer_deposit_rate\(",
    "dcf_refresh_gate.py": r"_dep\.consumer_deposit_rate\(",
    "custom30_yield_labels.py": r"from deposit_rate_vn import consumer_deposit_rate\b",
    os.path.join("trading_bot", "due_diligence.py"): r"from deposit_rate_vn import consumer_deposit_rate_detail",
}
for relpath, pattern in SITES.items():
    fp = os.path.join(HERE, relpath)
    with open(fp, encoding="utf-8") as f:
        src = f.read()
    check(f"{relpath} wired ({pattern})", re.search(pattern, src) is not None)
    # none of the 5 may still call current_deposit_rate() UNCONDITIONALLY (a leftover old import
    # is OK only inside the explicit knob=0 branch) -- check the dangerous case: a bare top-level
    # `from deposit_rate_vn import current_deposit_rate` with no overlay check nearby.
    bad = re.search(r"from deposit_rate_vn import current_deposit_rate\b", src)
    if bad:
        # acceptable only if the file also branches on DEPOSIT_RATE_CCTG_OVERLAY (due_diligence.py
        # keeps a conditional current_deposit_rate import inside the knob=0 branch by design)
        check(f"{relpath}: leftover current_deposit_rate import is inside an overlay branch",
              "DEPOSIT_RATE_CCTG_OVERLAY" in src)

# ---- 4. due_diligence.py's _deposit_rate_pct: both branches + source label ----------------------
print("\ntrading_bot/due_diligence.py::_deposit_rate_pct (direct call):")
os.environ.setdefault("TRADING_BOT_RUNTIME_ROOT", HERE)
sys.path.insert(0, HERE)
import trading_bot.due_diligence as DD  # noqa: E402

DD._CACHE.clear()
r0, src0 = with_overlay("0", lambda: DD._deposit_rate_pct(POST_TODAY))
DD._CACHE.clear()
r1, src1 = with_overlay("1", lambda: DD._deposit_rate_pct(POST_TODAY))
check("knob=0 label says big4_12m(cctg_overlay_disabled)",
      src0 == "deposit_rate_vn:big4_12m(cctg_overlay_disabled)")
check("knob=1 label says cctg_6m(...) today (post-anchor)", src1.startswith("deposit_rate_vn:cctg_6m"))
check("knob=1 rate > knob=0 rate today", r1 > r0)
DD._CACHE.clear()
r0h, src0h = with_overlay("0", lambda: DD._deposit_rate_pct(PRE))
DD._CACHE.clear()
r1h, src1h = with_overlay("1", lambda: DD._deposit_rate_pct(PRE))
check("pre-anchor: knob=1 rate == knob=0 rate (byte-identical)", r1h == r0h)

# ---- 5. dcf_valuation.discount_rate(): knob changes the discount rate, pre-anchor doesn't -------
print("\ndcf_valuation.py::discount_rate (direct call):")
import dcf_valuation as DCF  # noqa: E402

DCF._RATE_CACHE.clear()
r_big4 = with_overlay("0", lambda: (DCF._RATE_CACHE.clear(), DCF.discount_rate(POST_TODAY))[1])
r_eff = with_overlay("1", lambda: (DCF._RATE_CACHE.clear(), DCF.discount_rate(POST_TODAY))[1])
check("today: effective discount_rate > big4-only discount_rate", r_eff > r_big4)
check("delta matches CCTG-vs-Big4 spread (0.70pp) exactly",
      abs((r_eff - r_big4) - 0.007) < 1e-9)
r_big4_pre = with_overlay("0", lambda: (DCF._RATE_CACHE.clear(), DCF.discount_rate(PRE))[1])
r_eff_pre = with_overlay("1", lambda: (DCF._RATE_CACHE.clear(), DCF.discount_rate(PRE))[1])
check("pre-anchor: discount_rate byte-identical regardless of knob", r_big4_pre == r_eff_pre)

# ---- 6. mutation guard: a broken knob check must get caught by test 1 --------------------------
print("\nMutation guard (manual, not an automated AST mutator):")
_orig = dep.consumer_deposit_rate


def _mutant_always_effective(asof=None):
    """Mutant: ignores the override env var entirely (the exact bug this knob exists to prevent)."""
    return dep.effective_deposit_rate(asof)["rate_pct"]


dep.consumer_deposit_rate = _mutant_always_effective
mutant_caught = with_overlay("0", lambda: dep.consumer_deposit_rate(POST_TODAY)) != dep.current_deposit_rate(POST_TODAY)
dep.consumer_deposit_rate = _orig
check("mutant (knob ignored) is caught by the knob=0 equality check", mutant_caught)

# ---- 7. R1 regression: staleness must be PIT-causal (relative to asof), not "asof is None" -----
# anchor = 2026-09-30. age>45d -> stale -> Big-4-only(6.8). age<=45d -> fresh -> CCTG(7.5) wins.
# These two fixture dates straddle the EXACT boundary (age 44 fresh, age 46 stale) the docstrings
# cite -- both are in the future relative to real "today" (2026-10-01) on purpose: a wall-clock-
# relative check (the pre-fix bug) could never reproduce this with explicit past/future asof, only
# a true PIT-causal check (relative to the asof argument itself) can.
print("\nR1 regression — all 5 consumers age out CCTG identically, PIT-causal on asof:")
STALE_DATE = "2026-11-15"   # anchor+46d -> age 46 > 45 -> stale -> Big-4-only expected
FRESH_DATE = "2026-11-13"   # anchor+44d -> age 44 <= 45 -> still fresh -> CCTG expected
BIG4_AT = dep.current_deposit_rate(STALE_DATE)
CCTG_PCT = 7.5

check("fixture sanity: Big-4-only at both fixture dates == 6.8%", abs(BIG4_AT - 6.8) < 1e-9)
check("fixture sanity: STALE_DATE is anchor+46d, FRESH_DATE is anchor+44d",
      (pd.Timestamp(STALE_DATE) - pd.Timestamp(ANCHOR)).days == 46
      and (pd.Timestamp(FRESH_DATE) - pd.Timestamp(ANCHOR)).days == 44)

check("consumer_deposit_rate(stale) == Big-4-only (CCTG aged out)",
      dep.consumer_deposit_rate(STALE_DATE) == BIG4_AT)
check("consumer_deposit_rate(fresh) == CCTG 7.5 (not yet aged out)",
      dep.consumer_deposit_rate(FRESH_DATE) == CCTG_PCT)
check("effective_deposit_rate(stale, check_freshness=True) agrees with consumer_deposit_rate",
      dep.effective_deposit_rate(STALE_DATE, check_freshness=True)["rate_pct"] == BIG4_AT)

DCF._RATE_CACHE.clear()
dr_stale = DCF.discount_rate(STALE_DATE)
DCF._RATE_CACHE.clear()
dr_fresh = DCF.discount_rate(FRESH_DATE)
check("dcf_valuation.discount_rate(stale) matches Big-4-only leg",
      abs(dr_stale - (BIG4_AT + DCF.ERP) / 100.0) < 1e-9)
check("dcf_valuation.discount_rate(fresh) matches CCTG leg",
      abs(dr_fresh - (CCTG_PCT + DCF.ERP) / 100.0) < 1e-9)

import dcf_refresh_gate as DRG  # noqa: E402
check("dcf_refresh_gate's consumer_deposit_rate(stale) == Big-4-only",
      DRG._dep.consumer_deposit_rate(STALE_DATE) == BIG4_AT)
check("dcf_refresh_gate's consumer_deposit_rate(fresh) == CCTG",
      DRG._dep.consumer_deposit_rate(FRESH_DATE) == CCTG_PCT)

# custom30_yield_labels._label_one -- exercise the REAL function (not just a direct dep call), so
# a future drift back to a decoupled copy of the rate lookup (the exact M9/M12 mutant-survival gap
# flagged in the round-2 dispatch) would be caught here, not just at the central function.
import custom30_yield_labels as C30  # noqa: E402

_d_stale, _d_fresh = pd.Timestamp(STALE_DATE), pd.Timestamp(FRESH_DATE)
_px_map = {("AAA", _d_stale): (10000.0, 1234), ("AAA", _d_fresh): (10000.0, 1234)}
_div_g = pd.DataFrame({
    "ex": [_d_stale - pd.Timedelta(days=200), _d_stale - pd.Timedelta(days=560),
           _d_stale - pd.Timedelta(days=920)],
    "value_per_share": [500.0, 500.0, 500.0]})
_div_by_tk = {"AAA": _div_g}
_thr = (0.9, 1.1, 999999)   # (near_lo, near_hi, icb_banking) -- 1234 never matches the sentinel
_cache_stale, _cache_fresh = {}, {}
C30._label_one("AAA", _d_stale, _px_map, _div_by_tk, _cache_stale, dep.consumer_deposit_rate, _thr)
C30._label_one("AAA", _d_fresh, _px_map, _div_by_tk, _cache_fresh, dep.consumer_deposit_rate, _thr)
check("custom30_yield_labels._label_one (real call path) uses Big-4-only at stale date",
      _cache_stale.get(str(_d_stale.date())) == BIG4_AT)
check("custom30_yield_labels._label_one (real call path) uses CCTG at fresh date",
      _cache_fresh.get(str(_d_fresh.date())) == CCTG_PCT)

DD._CACHE.clear()
dd_stale, dd_stale_src = with_overlay("1", lambda: DD._deposit_rate_pct(STALE_DATE))
DD._CACHE.clear()
dd_fresh, dd_fresh_src = with_overlay("1", lambda: DD._deposit_rate_pct(FRESH_DATE))
check("due_diligence._deposit_rate_pct(stale) == Big-4-only, labeled big4",
      dd_stale == BIG4_AT and "big4" in dd_stale_src)
check("due_diligence._deposit_rate_pct(fresh) == CCTG, labeled cctg",
      dd_fresh == CCTG_PCT and "cctg" in dd_fresh_src)

print("\nR1 mutant: effective_deposit_rate called with check_freshness forced False (the exact "
      "pre-fix bug) must be caught by the stale-date equality check:")
_orig_edr = dep.effective_deposit_rate


def _mutant_force_fresh(asof=None, stale_days_limit=45, check_freshness=None):
    return _orig_edr(asof, stale_days_limit, check_freshness=False)


dep.effective_deposit_rate = _mutant_force_fresh
mutant_r1_caught = dep.consumer_deposit_rate(STALE_DATE) != BIG4_AT
dep.effective_deposit_rate = _orig_edr
check("R1 mutant (check_freshness forced False) is caught", mutant_r1_caught)

# ---- 8. R2 regression: a broken/stale CCTG read must be VISIBLE, not silently swallowed --------
print("\nR2 regression — CCTG failure is logged + annotated, not silently swallowed:")
import logging as _logging


class _CaptureHandler(_logging.Handler):
    def __init__(self):
        super().__init__()
        self.messages = []

    def emit(self, record):
        self.messages.append(record.getMessage())


_handler = _CaptureHandler()
_dep_logger = _logging.getLogger("deposit_rate_vn")
_dep_logger.addHandler(_handler)
_dep_logger.setLevel(_logging.WARNING)

_orig_checked = cctg.current_cctg_rate_checked


def _mutant_cctg_broken(asof=None):
    return None, None, "simulated CSV corruption"


cctg.current_cctg_rate_checked = _mutant_cctg_broken
try:
    broken_detail = dep.effective_deposit_rate(POST_TODAY, check_freshness=True)
finally:
    cctg.current_cctg_rate_checked = _orig_checked

check("R2: CCTG error -> still returns Big-4 rate (fail-open on the display number)",
      broken_detail["rate_pct"] == dep.current_deposit_rate(POST_TODAY))
check("R2: rate_source names the real cause (cctg_unavailable), not a bare big4_12m",
      "cctg_unavailable" in broken_detail["rate_source"])
check("R2: a WARNING was actually logged for the CCTG error (not silently swallowed)",
      any("simulated CSV corruption" in m for m in _handler.messages))

_handler.messages.clear()
stale_detail = dep.effective_deposit_rate(STALE_DATE, check_freshness=True)
check("R2: rate_source names the real cause (cctg_stale) when CCTG aged out",
      "cctg_stale" in stale_detail["rate_source"])
check("R2: a WARNING was actually logged for the CCTG staleness",
      any("CCTG stale" in m for m in _handler.messages))
_dep_logger.removeHandler(_handler)

print("\nR2 mutant: silent-swallow (bare except, no annotation) must be caught by the rate_source "
      "assertions above:")
_orig_edr2 = dep.effective_deposit_rate


def _mutant_silent_swallow(asof=None, stale_days_limit=45, check_freshness=None):
    """Mutant: reproduces the ORIGINAL round-1 bug -- cctg_err degrades to bare 'big4_12m', no
    annotation, no log."""
    d = _orig_edr2(asof, stale_days_limit, check_freshness)
    if d["rate_source"].startswith("big4_12m("):
        d = dict(d, rate_source="big4_12m")
    return d


cctg.current_cctg_rate_checked = _mutant_cctg_broken
dep.effective_deposit_rate = _mutant_silent_swallow
try:
    mutant_r2_detail = dep.effective_deposit_rate(POST_TODAY, check_freshness=True)
finally:
    cctg.current_cctg_rate_checked = _orig_checked
    dep.effective_deposit_rate = _orig_edr2
check("R2 mutant (annotation stripped) is caught by the cctg_unavailable assertion",
      "cctg_unavailable" not in mutant_r2_detail["rate_source"])

# ---- 9. rating_8l.py call site: uses the detail form and prints the real driver -----------------
print("\nrating_8l.py call-site check (source inspection — full pipeline run is disproportionate "
      "for a ±0.03 display print; the shared function's correctness is covered by sections 1-8):")
with open(os.path.join(HERE, "rating_8l.py"), encoding="utf-8") as f:
    _r8l_src = f.read()
check("rating_8l.py imports consumer_deposit_rate_detail (not the bare-float wrapper)",
      "from deposit_rate_vn import consumer_deposit_rate_detail" in _r8l_src)
check("rating_8l.py print line includes the driver (rate_source)",
      "_dep_detail['rate_source']" in _r8l_src)
check("rating_8l.py calls consumer_deposit_rate_detail() with asof=None (live path)",
      "consumer_deposit_rate_detail()" in _r8l_src)
# M15 (job Taylor_20261001_073836 follow-up): a mutant that keeps the consumer_deposit_rate_detail
# IMPORT (so the 3 checks above still pass) but computes _dep from current_deposit_rate() instead
# of _dep_detail["rate_pct"] would be invisible to a plain substring check on the import/print
# lines. Target the exact assignment the mutant would have to change, and separately forbid a
# stray _dep assignment from the bare Big-4-only function anywhere outside the explicit knob=0
# fallback branch (there is none in this file today -- a future one appearing here IS the mutant).
check("rating_8l.py's _dep is assigned from _dep_detail['rate_pct'] (not a separate Big-4 call)",
      re.search(r'_dep\s*=\s*_dep_detail\["rate_pct"\]', _r8l_src) is not None)
check("rating_8l.py never assigns _dep from current_deposit_rate() directly (M15 pattern)",
      re.search(r'_dep\s*=\s*current_deposit_rate\(', _r8l_src) is None)

# ---- 10. mutation-survivor regression (job Taylor_20261001_064225 dispatch, non-blocking but
# requested): M9 (tilt applied outside NEUTRAL) and M12 (custom30_yield_labels bypasses the
# central fn) both SURVIVED the round-2 mutation sweep (/tmp/qs_logs/mut.log) because every
# existing assertion either inspects unrelated text or manually injects the correct dependency
# (section 7's _label_one call passes dep.consumer_deposit_rate explicitly, so a mutation to the
# REAL call site at custom30_yield_labels.py:133-134 would never surface there). Source-text
# checks below target the exact lines a mutant would have to change -----------------------------
print("\nMutation-survivor regression (M9 NEUTRAL-gate text, M12 custom30 call-site arg):")
check("rating_8l.py gates the deposit tilt on NEUTRAL (int(_st) == 3), not any other state",
      re.search(r"if\s+int\(_st\)\s*==\s*3\s+and\s+os\.environ\.get\(\"DEPOSIT_TILT\"", _r8l_src)
      is not None)
with open(os.path.join(HERE, "custom30_yield_labels.py"), encoding="utf-8") as f:
    _c30_src = f.read()
_label_one_call = re.search(r"_label_one\(\s*\n\s*tk, d, px_map, div_by_tk, dep_cache, ([^,]+),",
                             _c30_src)
check("custom30_yield_labels.py's REAL _label_one call site passes consumer_deposit_rate "
      "(not current_deposit_rate or any other bare-Big-4 callable)",
      _label_one_call is not None and _label_one_call.group(1).strip() == "consumer_deposit_rate")

print(f"\n{'='*70}\n{len(fails)} FAIL / selfcheck {'PASSED' if not fails else 'FAILED'}")
if fails:
    for f in fails:
        print("  -", f)
sys.exit(1 if fails else 0)
