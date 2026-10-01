# -*- coding: utf-8 -*-
"""
cctg_deposit_wiring_selfcheck.py — selfcheck for deposit_rate_vn.consumer_deposit_rate() and its
5 LIVE wiring points (job Taylor_20261001_054110, user-approved 2026-10-01 12:40 ICT):
  rating_8l.py (NEUTRAL deposit tilt), dcf_valuation.py::discount_rate(), dcf_refresh_gate.py,
  custom30_yield_labels.py (batch yield-floor), trading_bot/due_diligence.py (_deposit_rate_pct).

Pre-registers THIS checkout's deposit_rate_vn/cctg_rate_vn in sys.modules before importing any
of the 5 consumer modules — several of them (dcf_valuation.py, dcf_refresh_gate.py) hardcode
WORKDIR to the absolute production path and `os.chdir()`/`sys.path.insert(0, WORKDIR)` to it,
which would otherwise silently import the PRODUCTION deposit_rate_vn.py instead of this
worktree's copy when the selfcheck is run pre-merge. Once `import X` has populated
sys.modules['deposit_rate_vn'], any later `import deposit_rate_vn as _dep` anywhere reuses that
same object regardless of sys.path order — this is what makes the pre-registration work.

Run: python3 cctg_deposit_wiring_selfcheck.py   (and again under $DNA_PYEXE, and under
`env -u TZ TZ=America/New_York python3 ...` per the verify-before-done skill — none of the
asserts below pass a bare asof=None, so TZ should not matter here; running under a foreign TZ
is the check that proves that, not an assumption).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import deposit_rate_vn as dep        # noqa: E402  (pre-register THIS checkout's copy first)
import cctg_rate_vn as cctg          # noqa: E402

fails = []


def check(name, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        fails.append(name)


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
    "rating_8l.py": r"from deposit_rate_vn import consumer_deposit_rate",
    "dcf_valuation.py": r"_dep\.consumer_deposit_rate\(",
    "dcf_refresh_gate.py": r"_dep\.consumer_deposit_rate\(",
    "custom30_yield_labels.py": r"from deposit_rate_vn import consumer_deposit_rate",
    os.path.join("trading_bot", "due_diligence.py"): r"effective_deposit_rate",
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
check("knob=0 label says big4_12m", src0 == "deposit_rate_vn:big4_12m")
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

print(f"\n{'='*70}\n{len(fails)} FAIL / selfcheck {'PASSED' if not fails else 'FAILED'}")
if fails:
    for f in fails:
        print("  -", f)
sys.exit(1 if fails else 0)
