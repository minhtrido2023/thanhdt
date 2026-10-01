#!/usr/bin/env python3
"""Selfcheck for the CCTG overlay wired 2026-10-01 (user directive): cctg_rate_vn.py,
deposit_rate_vn.effective_deposit_rate()/effective_deposit_events_df(), and the CCTG overlay
inside macro_killswitch_a_status(). Run under $DNA_PYEXE and under `env -u TZ` /
Pacific/Kiritimati / America/New_York (coding_guidelines §16/§19) -- every test below uses an
explicit asof, so host TZ should not matter; asserted explicitly in T_tz."""
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
import cctg_rate_vn as cctg
import deposit_rate_vn as dep

N = 0


def check(label, cond):
    global N
    N += 1
    assert cond, f"FAIL [{label}]"
    print(f"  ok: {label}")


print("=== cctg_rate_vn + effective_deposit_rate overlay selfcheck ===")

# T1: no CCTG observation before the first anchor (2026-09-30) -> None, not an error, not a guess.
r1_pct, r1_date = cctg.current_cctg_rate(asof="2026-09-29")
check("T1 pre-anchor asof -> rate is None", r1_pct is None)
check("T1 pre-anchor asof -> date is None", r1_date is None)

# T2: on/after the anchor -> the frozen 7.5% value.
r2_pct, r2_date = cctg.current_cctg_rate(asof="2026-10-01")
check("T2 post-anchor rate=7.5%", abs(r2_pct - 7.5) < 1e-9)
check("T2 post-anchor date=2026-09-30", str(r2_date.date()) == "2026-09-30")

# T3: macro_killswitch_a_status before CCTG existed -> rate_source == big4_12m (byte-identical to
# pre-CCTG behavior); uses a real frozen Big-4 anchor (2023-03-01..2023-06-01 = 7.2%).
r3 = dep.macro_killswitch_a_status(asof="2023-05-01")
check("T3 pre-CCTG call: rate_source=big4_12m", r3["rate_source"] == "big4_12m")
check("T3 pre-CCTG call: rate unchanged (7.2%)", abs(r3["rate"] - 0.072) < 1e-9)

# T4: CCTG wins when fresh and higher than Big-4 -- inject a fresh, LOW Big-4 anchor (postdating
# the last frozen 2026-06-01 anchor, same append-only mechanism as macro_killswitch_a_selfcheck.py)
# so Big-4 alone would read CLEAR, then confirm CCTG's 7.5% becomes the driver.
_tmpdir = tempfile.mkdtemp(prefix="cctg_selfcheck_")
_tmp_dep_csv = os.path.join(_tmpdir, "deposit_rate_vn_events.csv")
_orig_dep_csv = dep._EVENTS_CSV
try:
    with open(_tmp_dep_csv, "w") as f:
        f.write("effective_date,deposit_rate,collected_date,source,note\n")
        f.write("2026-09-20,6.5,2026-09-20,manual_verify,selfcheck-fixture\n")
    dep._EVENTS_CSV = _tmp_dep_csv
    r4 = dep.macro_killswitch_a_status(asof="2026-10-01", check_freshness=True)
    check("T4 CCTG wins: rate=7.5%", abs(r4["rate"] - 0.075) < 1e-9)
    check("T4 CCTG wins: rate_source starts with cctg_6m", r4["rate_source"].startswith("cctg_6m"))
    check("T4 CCTG wins: not armed (7.5% <= 7.5% strict)", r4["armed"] is False)

    r4b = dep.effective_deposit_rate(asof="2026-10-01", check_freshness=True)
    check("T4b effective_deposit_rate agrees: rate_pct=7.5", abs(r4b["rate_pct"] - 7.5) < 1e-9)
    check("T4b effective_deposit_rate agrees: source=cctg", r4b["rate_source"].startswith("cctg_6m"))
    check("T4b effective_deposit_rate: big4_rate_pct=6.5 preserved", abs(r4b["big4_rate_pct"] - 6.5) < 1e-9)
    check("T4b effective_deposit_rate: cctg_rate_pct=7.5 preserved", abs(r4b["cctg_rate_pct"] - 7.5) < 1e-9)

    # T5: CCTG present but STALE (asof far enough past the single CCTG anchor) -> Big-4's OWN
    # reading (6.5%) drives `rate`, even though CCTG's last-known value (7.5%, exactly == the 7.5%
    # threshold) is higher. Round-6 fix (hướng B, 2026-10-01): a stale CCTG reading now ALWAYS
    # forces armed=True + stale=True regardless of whether its last-known value was <=, ==, or >
    # the threshold -- this fixture is the "last==7.5" boundary case of that matrix (symmetric with
    # Big-4's own big4_stale clause, which has never had a "last value already safe" carve-out).
    r5 = dep.macro_killswitch_a_status(asof="2026-11-20", check_freshness=True)
    check("T5 stale CCTG excluded: rate_source=big4_12m", r5["rate_source"] == "big4_12m")
    check("T5 stale CCTG excluded: rate=6.5% (not 7.5%)", abs(r5["rate"] - 0.065) < 1e-9)
    check("T5 (round-6) stale CCTG, last==7.5%: stale=True", r5["stale"] is True)
    check("T5 (round-6) stale CCTG, last==7.5%: armed=True (forced, not silently dropped)",
          r5["armed"] is True)
    # (no "reason mentions CCTG" check here -- Big-4's OWN fixture is ALSO stale at this asof
    # (age 61d > 45d), so `armed`/`stale` come from the big4_stale branch, which has never
    # surfaced cctg_note in `reason` even pre-round-6; T19/T20 isolate the CCTG-only case instead.)
finally:
    dep._EVENTS_CSV = _orig_dep_csv
    shutil.rmtree(_tmpdir, ignore_errors=True)

# T6: CCTG lower than Big-4 -> Big-4 still wins (never silently replaces a higher Big-4 reading).
# Real anchor: 2012-10-01 Big-4 = 9.0%, well above CCTG's 7.5% -- but CCTG has no data that far
# back anyway (T1 covers the "no data" path); this covers the "has data but it's lower" path via
# a controlled CSV fixture co-located at a post-CCTG-anchor date.
_tmp_dep_csv2 = os.path.join(tempfile.mkdtemp(prefix="cctg_selfcheck2_"), "deposit_rate_vn_events.csv")
try:
    with open(_tmp_dep_csv2, "w") as f:
        f.write("effective_date,deposit_rate,collected_date,source,note\n")
        f.write("2026-09-25,8.0,2026-09-25,manual_verify,selfcheck-fixture-high\n")
    dep._EVENTS_CSV = _tmp_dep_csv2
    r6 = dep.macro_killswitch_a_status(asof="2026-10-01", check_freshness=True)
    check("T6 Big-4 (8.0%) > CCTG (7.5%): rate_source=big4_12m", r6["rate_source"] == "big4_12m")
    check("T6 Big-4 (8.0%) > CCTG (7.5%): rate=8.0%, armed", abs(r6["rate"] - 0.08) < 1e-9 and r6["armed"] is True)
finally:
    dep._EVENTS_CSV = _orig_dep_csv
    shutil.rmtree(os.path.dirname(_tmp_dep_csv2), ignore_errors=True)

# T7: effective_deposit_events_df() shape + pre-anchor byte-identity with deposit_events_df().
full = dep.effective_deposit_events_df()
base = dep.deposit_events_df()
check("T7 effective_deposit_events_df columns", list(full.columns) == ["time", "deposit_rate"])
pre_anchor_full = full[full["time"] < "2026-09-30"].reset_index(drop=True)
pre_anchor_base = base[base["time"] < "2026-09-30"].reset_index(drop=True)
check("T7 pre-anchor rows byte-identical to deposit_events_df()",
      pre_anchor_full.equals(pre_anchor_base))

# T8: the CCTG anchor date itself must appear as its own row (union-of-breakpoints design) --
# a naive "merge CCTG onto Big-4's existing row dates" would be a no-op here, since Big-4's last
# row (2026-06-01) predates CCTG's first anchor (2026-09-30) and a backward-only merge would never
# land on it (this exact bug was caught and fixed before shipping, 2026-10-01).
check("T8 CCTG anchor date present as its own row",
      (full["time"] == pd.Timestamp("2026-09-30")).any())
check("T8 CCTG anchor row value = 7.5 (max(6.8, 7.5))",
      abs(full.loc[full["time"] == pd.Timestamp("2026-09-30"), "deposit_rate"].iloc[0] - 7.5) < 1e-9)

# T9: downstream as-of lookup (the exact pattern value_radar.py's load_series() uses: merge a
# daily trading-day panel backward onto this step series) must surface 7.5% for ANY day on/after
# the CCTG anchor, not just the anchor day itself.
day = pd.DataFrame({"time": [pd.Timestamp("2026-10-01")]})
r9 = pd.merge_asof(day, full.sort_values("time"), on="time", direction="backward")
check("T9 downstream as-of lookup on 2026-10-01 -> 7.5%",
      abs(r9["deposit_rate"].iloc[0] - 7.5) < 1e-9)

# T10/T11: isolate the CCTG-caused signal from Big-4's own age by injecting a FRESH, low Big-4
# fixture too (postdating the last frozen 2026-06-01 anchor) -- Big-4 alone at this asof would be
# fresh and CLEAR, so any stale=True/armed-sensitive reason here is attributable purely to the
# CCTG-side problem, not to Big-4 going stale on its own.
_orig_cctg_csv = cctg._EVENTS_CSV

# T10: CCTG CSV corrupt (unparseable, same shape as macro_killswitch_a_selfcheck.py T12) must NOT
# be swallowed by the overlay's try/except -- it must surface as stale=True + armed=True (round-3
# fix 2: a CCTG value this function cannot validate is evidence it cannot rule out "effective rate
# > 7.5%" either, same fail-closed treatment as every Big-4-side error path in this function), with
# a reason noting CCTG, even while Big-4's OWN reading is fresh and CLEAR. (quant-skeptic round-2
# fix 1: the old bare `except Exception: pass` made this fail-OPEN -- CLEAR, stale=False -- first;
# round-2 fix 1's own stale=True/armed=False was STILL inconsistent with Big-4's error handling,
# closed here.)
# NOTE: both injected anchors must postdate their OWN series' frozen max (append-only design) --
# Big-4 frozen max = 2026-06-01, CCTG frozen max = 2026-09-30 -- so the CCTG fixture date must be
# after 2026-09-30 for deposit_events_df()/cctg_events_df() to actually pick it up at all.
_tmpdir10 = tempfile.mkdtemp(prefix="cctg_selfcheck10_")
_tmp_dep_csv10 = os.path.join(_tmpdir10, "deposit_rate_vn_events.csv")
_tmp_cctg_csv10 = os.path.join(_tmpdir10, "cctg_rate_vn_events.csv")
try:
    with open(_tmp_dep_csv10, "w") as f:
        f.write("effective_date,deposit_rate,collected_date,source,note\n")
        f.write("2026-10-01,6.0,2026-10-01,manual_verify,selfcheck-fixture-low\n")
    with open(_tmp_cctg_csv10, "w") as f:
        f.write('effective_date,cctg_rate,collected_date,source,note\n')
        f.write('2026-10-05,8.0,2026-10-05,manual_verify,"unterminated quote never closed\n')
    dep._EVENTS_CSV = _tmp_dep_csv10
    cctg._EVENTS_CSV = _tmp_cctg_csv10
    r10 = dep.macro_killswitch_a_status(asof="2026-10-10", check_freshness=True)
    check("T10 corrupt CCTG CSV: Big-4 rate preserved (6.0%, not overridden)",
          abs(r10["rate"] - 0.06) < 1e-9 and r10["rate_source"] == "big4_12m")
    check("T10 corrupt CCTG CSV: stale=True (surfaced, not silently CLEAR)", r10["stale"] is True)
    check("T10 corrupt CCTG CSV: reason mentions CCTG", "CCTG" in r10["reason"])
    check("T10 corrupt CCTG CSV: force-armed (unvalidated CCTG != provably CLEAR, round-3 fix 2)",
          r10["armed"] is True)
finally:
    dep._EVENTS_CSV = _orig_dep_csv
    cctg._EVENTS_CSV = _orig_cctg_csv
    shutil.rmtree(_tmpdir10, ignore_errors=True)

# T11: CCTG value outside the sanity fence (typo, e.g. written as a fraction) must NOT silently
# fall back to Big-4-only with zero trace -- must surface stale=True + armed=True (round-3 fix 2)
# + a reason mentioning CCTG.
_tmpdir11 = tempfile.mkdtemp(prefix="cctg_selfcheck11_")
_tmp_dep_csv11 = os.path.join(_tmpdir11, "deposit_rate_vn_events.csv")
_tmp_cctg_csv11 = os.path.join(_tmpdir11, "cctg_rate_vn_events.csv")
try:
    with open(_tmp_dep_csv11, "w") as f:
        f.write("effective_date,deposit_rate,collected_date,source,note\n")
        f.write("2026-10-01,6.0,2026-10-01,manual_verify,selfcheck-fixture-low\n")
    with open(_tmp_cctg_csv11, "w") as f:
        f.write("effective_date,cctg_rate,collected_date,source,note\n")
        f.write("2026-10-05,0.085,2026-10-05,manual_verify,selfcheck-typo-fixture\n")
    dep._EVENTS_CSV = _tmp_dep_csv11
    cctg._EVENTS_CSV = _tmp_cctg_csv11
    r11 = dep.macro_killswitch_a_status(asof="2026-10-10", check_freshness=True)
    check("T11 out-of-range CCTG: rate_source=big4_12m (bad value never used)",
          r11["rate_source"] == "big4_12m")
    check("T11 out-of-range CCTG: stale=True (surfaced)", r11["stale"] is True)
    check("T11 out-of-range CCTG: reason mentions CCTG", "CCTG" in r11["reason"])
    check("T11 out-of-range CCTG: force-armed (round-3 fix 2)", r11["armed"] is True)
finally:
    dep._EVENTS_CSV = _orig_dep_csv
    cctg._EVENTS_CSV = _orig_cctg_csv
    shutil.rmtree(_tmpdir11, ignore_errors=True)

# T12: the critical case named explicitly in the round-2 directive -- CCTG goes STALE and its last
# known reading was ABOVE the 7.5% threshold. Must force armed=True even though Big-4 alone (fresh,
# low) would read CLEAR -- losing track of a feed last seen above the trigger must never silently
# read as CLEAR. (Since round-6/hướng B this is no longer a SPECIAL case -- ANY cctg_stale forces
# armed=True now, see T5/T19/T20 for the other 3 cells of the last-known-value x stale matrix.)
_tmpdir12 = tempfile.mkdtemp(prefix="cctg_selfcheck12_")
_tmp_dep_csv12 = os.path.join(_tmpdir12, "deposit_rate_vn_events.csv")
_tmp_cctg_csv12 = os.path.join(_tmpdir12, "cctg_rate_vn_events.csv")
try:
    with open(_tmp_dep_csv12, "w") as f:
        f.write("effective_date,deposit_rate,collected_date,source,note\n")
        f.write("2026-11-01,6.0,2026-11-01,manual_verify,selfcheck-fixture-low\n")
    with open(_tmp_cctg_csv12, "w") as f:
        f.write("effective_date,cctg_rate,collected_date,source,note\n")
        f.write("2026-10-05,8.0,2026-10-05,manual_verify,selfcheck-fixture-high\n")
    dep._EVENTS_CSV = _tmp_dep_csv12
    cctg._EVENTS_CSV = _tmp_cctg_csv12
    r12 = dep.macro_killswitch_a_status(asof="2026-11-25", stale_days_limit=45, check_freshness=True)
    check("T12 CCTG stale-but-was-high: armed=True (forced, not silently dropped)",
          r12["armed"] is True)
    check("T12 CCTG stale-but-was-high: stale=True", r12["stale"] is True)
    check("T12 CCTG stale-but-was-high: reason mentions CCTG", "CCTG" in r12["reason"])
    check("T12 CCTG stale-but-was-high: Big-4 reading itself would have been CLEAR (6.0%)",
          abs(r12["rate"] - 0.06) < 1e-9)
finally:
    dep._EVENTS_CSV = _orig_dep_csv
    cctg._EVENTS_CSV = _orig_cctg_csv
    shutil.rmtree(_tmpdir12, ignore_errors=True)

# T13 (M16 guard): the CCTG anchor date itself, queried EXACTLY on that day, must return the
# anchor's rate -- kills a `<=` -> `<` mutant in current_cctg_rate()'s asof filter (which would
# wrongly return None/the prior anchor on the boundary day itself).
r13_pct, r13_date = cctg.current_cctg_rate(asof="2026-09-30")
check("T13 (M16) exact anchor day -> rate=7.5% (not None)", r13_pct is not None and abs(r13_pct - 7.5) < 1e-9)
check("T13 (M16) exact anchor day -> date=2026-09-30", str(r13_date.date()) == "2026-09-30")

# T14 (quant-skeptic round-3 item 3, M-range-max guard): a format-valid-but-out-of-range CCTG typo
# ("85" meaning 8.5%) fed through effective_deposit_events_df() -- the Value Radar historical
# series path, which previously had NO range validation at all and let 85 flow straight through as
# the displayed deposit_rate -- must now raise instead. Kills a mutant that widens
# cctg_rate_vn.RATE_MAX_PCT from 30 -> 300 (85 would then be "in range" and the raise would not
# fire, so this assertion catches it).
_tmpdir14 = tempfile.mkdtemp(prefix="cctg_selfcheck14_")
_tmp_cctg_csv14 = os.path.join(_tmpdir14, "cctg_rate_vn_events.csv")
try:
    with open(_tmp_cctg_csv14, "w") as f:
        f.write("effective_date,cctg_rate\n2026-10-10,85\n")
    cctg._EVENTS_CSV = _tmp_cctg_csv14
    try:
        dep.effective_deposit_events_df()
        raised = False
    except ValueError:
        raised = True
    check("T14 typo '85' in effective_deposit_events_df() raises (not silently 85%)", raised)
finally:
    cctg._EVENTS_CSV = _orig_cctg_csv
    shutil.rmtree(_tmpdir14, ignore_errors=True)

# T15: current_cctg_rate_checked()'s OWN range guard, isolated from cctg_events_df()'s load-time
# guard (T14) -- defense-in-depth: even if a value somehow reached current_cctg_rate() without
# having gone through cctg_events_df()'s validation (e.g. a future refactor bypassing it), the
# checked wrapper must still catch an out-of-range rate itself. Monkeypatches current_cctg_rate()
# directly so this test still exercises current_cctg_rate_checked()'s guard even after T14 made
# cctg_events_df() raise earlier for the same kind of bad value. Kills "bỏ guard" mutants that
# remove/widen the `RATE_MIN_PCT <= rate_pct <= RATE_MAX_PCT` check in current_cctg_rate_checked().
_orig_current_cctg_rate = cctg.current_cctg_rate
try:
    cctg.current_cctg_rate = lambda asof=None: (85.0, pd.Timestamp("2026-10-10"))
    _, _, err15 = cctg.current_cctg_rate_checked(asof="2026-10-15")
    check("T15 current_cctg_rate_checked() range guard fires on out-of-range rate=85",
          err15 is not None and "85" in err15)
finally:
    cctg.current_cctg_rate = _orig_current_cctg_rate

# T16 (boundary '>' vs '>=' at the CCTG side's stale_days_limit=45): exact day 45 must NOT be
# stale (CCTG still wins, rate=8.0%, armed via normal threshold check), day 46 MUST be stale
# (CCTG excluded, falls back to Big-4's own low fresh reading; armed stays True via
# cctg_force_armed unconditionally since round-6 -- here the last-known CCTG reading (8.0%) is
# ALSO above 7.5%, so this doubles as part of the last>7.5 cell; T12 is the dedicated case for it,
# T19/T20 cover the other two cells). Big-4 fixture anchor is kept fresh at BOTH asof dates (age
# 30/31d, well under 45) so only the CCTG-side boundary is exercised.
_tmpdir16 = tempfile.mkdtemp(prefix="cctg_selfcheck16_")
_tmp_dep_csv16 = os.path.join(_tmpdir16, "deposit_rate_vn_events.csv")
_tmp_cctg_csv16 = os.path.join(_tmpdir16, "cctg_rate_vn_events.csv")
try:
    with open(_tmp_dep_csv16, "w") as f:
        f.write("effective_date,deposit_rate\n2026-10-20,6.0\n")
    with open(_tmp_cctg_csv16, "w") as f:
        f.write("effective_date,cctg_rate\n2026-10-05,8.0\n")
    dep._EVENTS_CSV = _tmp_dep_csv16
    cctg._EVENTS_CSV = _tmp_cctg_csv16
    r16a = dep.macro_killswitch_a_status(asof="2026-11-19", stale_days_limit=45, check_freshness=True)
    check("T16 CCTG age==45d NOT stale -> CCTG still active (rate=8.0%)",
          abs(r16a["rate"] - 0.08) < 1e-9 and r16a["rate_source"].startswith("cctg_6m"))
    check("T16 CCTG age==45d NOT stale -> stale=False", r16a["stale"] is False)
    r16b = dep.macro_killswitch_a_status(asof="2026-11-20", stale_days_limit=45, check_freshness=True)
    check("T16 CCTG age==46d stale -> excluded, falls back to Big-4 (rate=6.0%)",
          abs(r16b["rate"] - 0.06) < 1e-9 and r16b["rate_source"] == "big4_12m")
    check("T16 CCTG age==46d stale -> stale=True", r16b["stale"] is True)
    check("T16 CCTG age==46d stale but last-known 8.0%>7.5% -> armed=True anyway",
          r16b["armed"] is True)
finally:
    dep._EVENTS_CSV = _orig_dep_csv
    cctg._EVENTS_CSV = _orig_cctg_csv
    shutil.rmtree(_tmpdir16, ignore_errors=True)

# T17 (round-4 fix 1, boundary '<=' vs '<' at the CCTG anchor date 2026-09-30): a CSV row whose
# effective_date is BEFORE the frozen anchor (e.g. a typo'd year "2025-10-02" meant to be
# "2026-10-02") used to be silently filtered out of cctg_events_df() with zero trace. A row dated
# EXACTLY ON the anchor date (same-day duplicate/correction) must ALSO raise, not just strictly-
# earlier rows -- this is the boundary case a `>` vs `>=` mutant on the new guard would flip.
_tmpdir17 = tempfile.mkdtemp(prefix="cctg_selfcheck17_")
_tmp_cctg_csv17a = os.path.join(_tmpdir17, "cctg_rate_vn_events_before.csv")
_tmp_cctg_csv17b = os.path.join(_tmpdir17, "cctg_rate_vn_events_oneq.csv")
try:
    with open(_tmp_cctg_csv17a, "w") as f:
        f.write("effective_date,cctg_rate\n2025-10-02,9.4\n")  # year typo, strictly BEFORE anchor
    cctg._EVENTS_CSV = _tmp_cctg_csv17a
    raised17a = False
    try:
        cctg.cctg_events_df()
    except ValueError as exc17a:
        raised17a = True
        err17a = str(exc17a)
    check("T17 effective_date strictly before anchor (year typo) raises, not silently dropped",
          raised17a and "2025-10-02" in err17a)

    with open(_tmp_cctg_csv17b, "w") as f:
        f.write("effective_date,cctg_rate\n2026-09-30,9.4\n")  # exactly ON the anchor date
    cctg._EVENTS_CSV = _tmp_cctg_csv17b
    raised17b = False
    try:
        cctg.cctg_events_df()
    except ValueError:
        raised17b = True
    check("T17 effective_date == anchor date (boundary) also raises (kills > vs >= mutant)",
          raised17b)
finally:
    cctg._EVENTS_CSV = _orig_cctg_csv
    shutil.rmtree(_tmpdir17, ignore_errors=True)

# T18 (round-4 fix 4, boundary '>' vs '>=' at effective_deposit_rate()'s own stale_days_limit=45
# -- same boundary as T16 but for the DISPLAY-ONLY function, which has its own independent
# `cctg_age > stale_days_limit` check, not shared code with macro_killswitch_a_status()). Big-4
# fixture anchor kept fresh at both asof dates so only the CCTG-side boundary is exercised.
_tmpdir18 = tempfile.mkdtemp(prefix="cctg_selfcheck18_")
_tmp_dep_csv18 = os.path.join(_tmpdir18, "deposit_rate_vn_events.csv")
_tmp_cctg_csv18 = os.path.join(_tmpdir18, "cctg_rate_vn_events.csv")
try:
    with open(_tmp_dep_csv18, "w") as f:
        f.write("effective_date,deposit_rate\n2026-10-20,6.0\n")
    with open(_tmp_cctg_csv18, "w") as f:
        f.write("effective_date,cctg_rate\n2026-10-05,8.0\n")
    dep._EVENTS_CSV = _tmp_dep_csv18
    cctg._EVENTS_CSV = _tmp_cctg_csv18
    r18a = dep.effective_deposit_rate(asof="2026-11-19", stale_days_limit=45, check_freshness=True)
    check("T18 CCTG age==45d NOT stale -> effective_deposit_rate still uses CCTG (rate_pct=8.0)",
          abs(r18a["rate_pct"] - 8.0) < 1e-9 and r18a["rate_source"].startswith("cctg_6m"))
    r18b = dep.effective_deposit_rate(asof="2026-11-20", stale_days_limit=45, check_freshness=True)
    check("T18 CCTG age==46d stale -> effective_deposit_rate falls back to Big-4 (rate_pct=6.0)",
          abs(r18b["rate_pct"] - 6.0) < 1e-9 and r18b["rate_source"] == "big4_12m")
finally:
    dep._EVENTS_CSV = _orig_dep_csv
    cctg._EVENTS_CSV = _orig_cctg_csv
    shutil.rmtree(_tmpdir18, ignore_errors=True)

# T19 (round-6/hướng B, "stale + last<7.5" cell): CCTG goes stale and its last-known reading was
# BELOW the 7.5% threshold -- before round-6 this was the ONE silently-excluded case (no note, no
# stale flag, no armed). Must now force armed=True + stale=True exactly like T5 (last==7.5) and
# T12/T16b (last>7.5) -- "stale" alone is sufficient, the last-known value no longer matters.
_tmpdir19 = tempfile.mkdtemp(prefix="cctg_selfcheck19_")
_tmp_dep_csv19 = os.path.join(_tmpdir19, "deposit_rate_vn_events.csv")
_tmp_cctg_csv19 = os.path.join(_tmpdir19, "cctg_rate_vn_events.csv")
try:
    with open(_tmp_dep_csv19, "w") as f:
        f.write("effective_date,deposit_rate\n2026-11-01,6.0\n")
    with open(_tmp_cctg_csv19, "w") as f:
        f.write("effective_date,cctg_rate\n2026-10-05,5.0\n")  # last-known CCTG < 7.5%
    dep._EVENTS_CSV = _tmp_dep_csv19
    cctg._EVENTS_CSV = _tmp_cctg_csv19
    r19 = dep.macro_killswitch_a_status(asof="2026-11-25", stale_days_limit=45, check_freshness=True)
    check("T19 CCTG stale, last<7.5%: rate_source falls back to big4_12m",
          r19["rate_source"] == "big4_12m")
    check("T19 CCTG stale, last<7.5%: rate=6.0% (Big-4's own, not CCTG's 5.0%)",
          abs(r19["rate"] - 0.06) < 1e-9)
    check("T19 CCTG stale, last<7.5%: stale=True", r19["stale"] is True)
    check("T19 CCTG stale, last<7.5%: armed=True (forced, NOT silently dropped -- the round-6 fix)",
          r19["armed"] is True)
    check("T19 CCTG stale, last<7.5%: reason mentions CCTG", "CCTG" in r19["reason"])
finally:
    dep._EVENTS_CSV = _orig_dep_csv
    cctg._EVENTS_CSV = _orig_cctg_csv
    shutil.rmtree(_tmpdir19, ignore_errors=True)

# T20 ("fresh + last==7.5" cell, completing the matrix): uses the REAL frozen CCTG anchor
# (2026-09-30, 7.5%) at an asof just 1 day later -- fresh (age=1d << 45), so none of the stale/
# force-armed machinery fires at all; must read plain CLEAR, not armed, since 7.5% is NOT strictly
# > the 7.5% threshold. Injects only a fresh, low Big-4 fixture to isolate the CCTG side.
_tmpdir20 = tempfile.mkdtemp(prefix="cctg_selfcheck20_")
_tmp_dep_csv20 = os.path.join(_tmpdir20, "deposit_rate_vn_events.csv")
try:
    with open(_tmp_dep_csv20, "w") as f:
        f.write("effective_date,deposit_rate\n2026-09-25,6.0\n")
    dep._EVENTS_CSV = _tmp_dep_csv20
    r20 = dep.macro_killswitch_a_status(asof="2026-10-01", check_freshness=True)
    check("T20 fresh CCTG==7.5%: rate_source=cctg_6m", r20["rate_source"].startswith("cctg_6m"))
    check("T20 fresh CCTG==7.5%: rate=7.5%", abs(r20["rate"] - 0.075) < 1e-9)
    check("T20 fresh CCTG==7.5%: stale=False", r20["stale"] is False)
    check("T20 fresh CCTG==7.5%: armed=False (7.5% not strictly > 7.5%, must read CLEAR)",
          r20["armed"] is False)
finally:
    dep._EVENTS_CSV = _orig_dep_csv
    shutil.rmtree(_tmpdir20, ignore_errors=True)

# T21 (quant-skeptic round-6 mutant C1a, survived): mutating `if bad.any():` -> `if False:` in
# cctg_events_df() used to go undetected because no test fed it a row with a BAD DATE + a
# perfectly VALID rate number. Without the `bad.any()` guard, that row's `time` stays NaT while
# `cctg_rate` stays a real float; NaT comparisons (`<=`, `>`) are always False in pandas, so the
# row silently fails BOTH the range guard (rate is fine, not oor) AND the not-newer guard (NaT <=
# anything is False) and gets concatenated in with a NaT time -- current_cctg_rate()'s own
# `ev.time <= asof_ts` filter then silently excludes it forever, byte-identical to "the row was
# never appended". A typo'd date with a syntactically valid rate must raise, not vanish.
_tmpdir21 = tempfile.mkdtemp(prefix="cctg_selfcheck21_")
_tmp_cctg_csv21a = os.path.join(_tmpdir21, "bad_date.csv")
try:
    with open(_tmp_cctg_csv21a, "w") as f:
        f.write("effective_date,cctg_rate\n2O26-10-05,9.0\n")  # letter O instead of digit 0
    cctg._EVENTS_CSV = _tmp_cctg_csv21a
    raised21a = False
    try:
        cctg.cctg_events_df()
    except ValueError as exc21a:
        raised21a = True
        err21a = str(exc21a)
    check("T21a (C1a) malformed date + VALID rate raises (not silently dropped)",
          raised21a and "2O26-10-05" in err21a)
finally:
    cctg._EVENTS_CSV = _orig_cctg_csv
    shutil.rmtree(_tmpdir21, ignore_errors=True)

# T21b (round-6 mutant C1b, same `bad.any()` guard, other half): VALID date + an UNPARSEABLE rate
# string must also raise, not silently drop. (NOT a stray comma -- "9,0" un-quoted would be parsed
# by pandas as an EXTRA column and silently misaligned into effective_date/cctg_rate, a different
# and separately-nasty bug, not the one this test targets -- verified by hand, 2026-10-01.)
_tmpdir21b = tempfile.mkdtemp(prefix="cctg_selfcheck21b_")
_tmp_cctg_csv21b = os.path.join(_tmpdir21b, "bad_rate.csv")
try:
    with open(_tmp_cctg_csv21b, "w") as f:
        f.write("effective_date,cctg_rate\n2026-10-05,abc\n")  # non-numeric rate string
    cctg._EVENTS_CSV = _tmp_cctg_csv21b
    raised21b = False
    try:
        cctg.cctg_events_df()
    except (ValueError, pd.errors.ParserError):
        raised21b = True
    check("T21b (C1b) valid date + unparseable rate raises (not silently dropped)", raised21b)
finally:
    cctg._EVENTS_CSV = _orig_cctg_csv
    shutil.rmtree(_tmpdir21b, ignore_errors=True)

# T22 (round-6 mutant C2, "guard thiếu header"): removing the explicit `missing = {...} -
# set(extra.columns)` check in cctg_events_df() is an EQUIVALENT mutant for the "does it raise"
# question -- `extra[["effective_date", "cctg_rate"]]` on a frame missing those columns raises a
# pandas KeyError on its own (verified by hand, 2026-10-01), so BOTH the current explicit
# ValueError and the hypothetical no-guard KeyError stop the bad row from propagating. This test
# therefore asserts the OUTCOME (some exception fires, the header-is-wrong CSV never silently
# becomes usable data) rather than narrowly pinning the exception type, so it does not flag this
# specific mutant as a real behavior change -- documented here instead of claiming a false kill.
_tmpdir22 = tempfile.mkdtemp(prefix="cctg_selfcheck22_")
_tmp_cctg_csv22 = os.path.join(_tmpdir22, "wrong_header.csv")
try:
    with open(_tmp_cctg_csv22, "w") as f:
        f.write("date,rate\n2026-10-05,9.0\n")  # neither column named as expected
    cctg._EVENTS_CSV = _tmp_cctg_csv22
    raised22 = False
    try:
        cctg.cctg_events_df()
    except Exception:
        raised22 = True
    check("T22 (C2, equivalent-mutant-documented) wrong header raises either way", raised22)
finally:
    cctg._EVENTS_CSV = _orig_cctg_csv
    shutil.rmtree(_tmpdir22, ignore_errors=True)

# T23 (round-6 mutant D6, "outer except" in current_cctg_rate_checked()): every exception
# cctg_events_df()/current_cctg_rate() can actually raise today happens to be a ValueError, so a
# mutant that narrows current_cctg_rate_checked()'s `except Exception as exc:` to
# `except ValueError as exc:` was going undetected -- no existing test ever made current_cctg_rate
# raise a non-ValueError. Monkeypatch it to raise a RuntimeError directly: the checked wrapper must
# still convert this into a (None, None, error) tuple, not let it propagate, regardless of the
# exception's concrete type (the docstring promises "Any exception ... makes CCTG-side problems
# VISIBLE", not "any ValueError").
_orig_current_cctg_rate_d6 = cctg.current_cctg_rate
try:
    def _raise_runtime(asof=None):
        raise RuntimeError("simulated non-ValueError failure")
    cctg.current_cctg_rate = _raise_runtime
    _, _, err23 = cctg.current_cctg_rate_checked(asof="2026-10-15")
    check("T23 (D6) current_cctg_rate_checked() catches non-ValueError exceptions too",
          err23 is not None and "RuntimeError" in err23)
finally:
    cctg.current_cctg_rate = _orig_current_cctg_rate_d6

# T_tz: TZ independence guard (explicit asof throughout).
r_tz_a = dep.macro_killswitch_a_status(asof="2026-10-01")
os.environ.pop("TZ", None)
r_tz_b = dep.macro_killswitch_a_status(asof="2026-10-01")
check("T_tz TZ-independent", r_tz_a == r_tz_b)

print(f"\n=== {N} assertions PASS ===")
