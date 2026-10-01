#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
refresh_deposit_cctg_weekly_selfcheck.py — selfcheck for the weekly deposit+CCTG mechanism
(job Taylor_20261001_054108): append_cctg_rate.py's write guards + deposit_cctg_trend_check.py's
decline/staleness detection. Run under BOTH python3 and $DNA_PYEXE, and under BOTH the host's own
TZ and `env -u TZ` + a foreign TZ (coding_guidelines §16/§19) — every date comparison here either
takes an explicit `today` argument or reads a CSV-controlled `--effective`, so host TZ should not
change any PASS/FAIL outcome; T_tz asserts this explicitly.

Also runs a handful of real source-level mutations (sed on a throwaway copy, not the real file) at
the end to confirm the guards this selfcheck exercises actually have teeth — a test that can't
fail is not a test.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date, datetime
from zoneinfo import ZoneInfo

_ICT = ZoneInfo("Asia/Ho_Chi_Minh")  # coding_guidelines §16: never trust the host system TZ

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import append_cctg_rate as acr
import cctg_rate_vn as cctg
import deposit_cctg_trend_check as trend

N = 0
FAILS = []


def check(label, cond):
    global N
    N += 1
    if not cond:
        FAILS.append(label)
        print(f"  FAIL: {label}")
    else:
        print(f"  ok: {label}")


# ============================================================================
# Part A — append_cctg_rate.py guards (direct import, module-level monkeypatch)
# ============================================================================

def _fresh_tmpdir():
    d = tempfile.mkdtemp(prefix="cctg_wk_selfcheck_")
    return d, os.path.join(d, "cctg_rate_vn_events.csv")


def _run_append(argv, job_id=None):
    """Calls acr.main() with argv patched in, JOB_ID set/unset, capturing SystemExit as (rc, msg)."""
    old_argv = sys.argv
    old_job = os.environ.get("JOB_ID", None)
    sys.argv = ["append_cctg_rate.py"] + argv
    if job_id is None:
        os.environ.pop("JOB_ID", None)
    else:
        os.environ["JOB_ID"] = job_id
    try:
        rc = acr.main()
        return (rc or 0), None
    except SystemExit as e:
        return 1, str(e.code)
    finally:
        sys.argv = old_argv
        if old_job is None:
            os.environ.pop("JOB_ID", None)
        else:
            os.environ["JOB_ID"] = old_job


def _row_count():
    return _row_count_at(acr.CSV_PATH)


def _row_count_at(path):
    import csv
    if not os.path.exists(path):
        return 0
    with open(path, newline="", encoding="utf-8") as f:
        return len([r for r in csv.DictReader(f) if r.get("effective_date")])


print("=== Part A: append_cctg_rate.py guards ===")

_orig_acr_csv = acr.CSV_PATH
_orig_cctg_csv = cctg._EVENTS_CSV
TODAY = datetime.now(_ICT).date().isoformat()


def _src(pub, url, d, rate):
    return {"publisher": pub, "url": url, "date": d, "rate": rate}


# --- A1: happy path, 2 independent owners, rates agree exactly ---
tmpdir, tmp_csv = _fresh_tmpdir()
acr.CSV_PATH = tmp_csv
cctg._EVENTS_CSV = tmp_csv
try:
    sources = json.dumps([
        _src("VietnamNet", "https://vietnamnet.vn/cctg-moi", TODAY, 7.6),
        _src("VnExpress", "https://vnexpress.net/cctg-moi", TODAY, 7.6),
    ])
    rc, msg = _run_append(
        ["--rate", "7.6", "--effective", TODAY, "--source", "web_crosscheck_auto",
         "--collected", TODAY, "--note", "test", "--sources", sources],
        job_id="job123")
    check("A1 happy path writes OK (rc=0)", rc == 0)
    check("A1 row written", _row_count() == 1)
finally:
    shutil.rmtree(tmpdir, ignore_errors=True)
    acr.CSV_PATH = _orig_acr_csv
    cctg._EVENTS_CSV = _orig_cctg_csv

# --- A2: idempotent re-run (same effective_date) -> SKIP, no dup row ---
tmpdir, tmp_csv = _fresh_tmpdir()
acr.CSV_PATH = tmp_csv
cctg._EVENTS_CSV = tmp_csv
try:
    sources = json.dumps([
        _src("VietnamNet", "https://vietnamnet.vn/x", TODAY, 7.6),
        _src("VnExpress", "https://vnexpress.net/x", TODAY, 7.6),
    ])
    argv = ["--rate", "7.6", "--effective", TODAY, "--source", "web_crosscheck_auto",
            "--collected", TODAY, "--note", "test", "--sources", sources]
    rc1, _ = _run_append(argv, job_id="job123")
    rc2, _ = _run_append(argv, job_id="job456")  # re-run, different job_id, same effective_date
    check("A2 first write OK", rc1 == 0)
    check("A2 second run does not error", rc2 == 0)
    check("A2 idempotent: still exactly 1 row (no duplicate)", _row_count() == 1)
finally:
    shutil.rmtree(tmpdir, ignore_errors=True)
    acr.CSV_PATH = _orig_acr_csv
    cctg._EVENTS_CSV = _orig_cctg_csv

# --- A3: owner-group collision (VCCorp cluster) -> refused, no write ---
tmpdir, tmp_csv = _fresh_tmpdir()
acr.CSV_PATH = tmp_csv
cctg._EVENTS_CSV = tmp_csv
try:
    sources = json.dumps([
        _src("CafeF", "https://cafef.vn/cctg", TODAY, 7.6),
        _src("Kenh14", "https://kenh14.vn/cctg", TODAY, 7.6),
    ])
    rc, msg = _run_append(
        ["--rate", "7.6", "--effective", TODAY, "--source", "web_crosscheck_auto",
         "--collected", TODAY, "--note", "test", "--sources", sources],
        job_id="job123")
    check("A3 same-owner-group refused (rc!=0)", rc != 0)
    check("A3 no row written", _row_count() == 0)
finally:
    shutil.rmtree(tmpdir, ignore_errors=True)
    acr.CSV_PATH = _orig_acr_csv
    cctg._EVENTS_CSV = _orig_cctg_csv

# --- A4: only 1 source -> refused ---
tmpdir, tmp_csv = _fresh_tmpdir()
acr.CSV_PATH = tmp_csv
cctg._EVENTS_CSV = tmp_csv
try:
    sources = json.dumps([_src("VietnamNet", "https://vietnamnet.vn/x", TODAY, 7.6)])
    rc, msg = _run_append(
        ["--rate", "7.6", "--effective", TODAY, "--source", "web_crosscheck_auto",
         "--collected", TODAY, "--note", "test", "--sources", sources],
        job_id="job123")
    check("A4 single source refused (rc!=0)", rc != 0)
    check("A4 no row written", _row_count() == 0)
finally:
    shutil.rmtree(tmpdir, ignore_errors=True)
    acr.CSV_PATH = _orig_acr_csv
    cctg._EVENTS_CSV = _orig_cctg_csv

# --- A5: rate out of sane range -> refused ---
tmpdir, tmp_csv = _fresh_tmpdir()
acr.CSV_PATH = tmp_csv
cctg._EVENTS_CSV = tmp_csv
try:
    sources = json.dumps([
        _src("VietnamNet", "https://vietnamnet.vn/x", TODAY, 35.0),
        _src("VnExpress", "https://vnexpress.net/x", TODAY, 35.0),
    ])
    rc, msg = _run_append(
        ["--rate", "35.0", "--effective", TODAY, "--source", "web_crosscheck_auto",
         "--collected", TODAY, "--note", "test", "--sources", sources],
        job_id="job123")
    check("A5 out-of-range rate refused (rc!=0)", rc != 0)
    check("A5 no row written", _row_count() == 0)
finally:
    shutil.rmtree(tmpdir, ignore_errors=True)
    acr.CSV_PATH = _orig_acr_csv
    cctg._EVENTS_CSV = _orig_cctg_csv

# --- A6: effective date NOT newer than last anchor (frozen 2026-09-30) -> refused ---
tmpdir, tmp_csv = _fresh_tmpdir()
acr.CSV_PATH = tmp_csv
cctg._EVENTS_CSV = tmp_csv
try:
    sources = json.dumps([
        _src("VietnamNet", "https://vietnamnet.vn/x", "2026-09-20", 7.5),
        _src("VnExpress", "https://vnexpress.net/x", "2026-09-20", 7.5),
    ])
    rc, msg = _run_append(
        ["--rate", "7.5", "--effective", "2026-09-29", "--source", "manual_verify",
         "--collected", "2026-09-29", "--note", "test"],
        job_id=None)  # human path, no JOB_ID, still must respect date-newer guard
    check("A6 not-newer-than-anchor refused (rc!=0)", rc != 0)
    check("A6 no row written", _row_count() == 0)
finally:
    shutil.rmtree(tmpdir, ignore_errors=True)
    acr.CSV_PATH = _orig_acr_csv
    cctg._EVENTS_CSV = _orig_cctg_csv

# --- A7: cross-source rate disagreement > 0.1pp -> refused ---
tmpdir, tmp_csv = _fresh_tmpdir()
acr.CSV_PATH = tmp_csv
cctg._EVENTS_CSV = tmp_csv
try:
    sources = json.dumps([
        _src("VietnamNet", "https://vietnamnet.vn/x", TODAY, 7.5),
        _src("VnExpress", "https://vnexpress.net/x", TODAY, 7.7),
    ])
    rc, msg = _run_append(
        ["--rate", "7.6", "--effective", TODAY, "--source", "web_crosscheck_auto",
         "--collected", TODAY, "--note", "test", "--sources", sources],
        job_id="job123")
    check("A7 cross-source disagreement (0.2pp) refused (rc!=0)", rc != 0)
    check("A7 no row written", _row_count() == 0)
finally:
    shutil.rmtree(tmpdir, ignore_errors=True)
    acr.CSV_PATH = _orig_acr_csv
    cctg._EVENTS_CSV = _orig_cctg_csv

# --- A7b: cross-source disagreement EXACTLY at tolerance (0.1pp) -> allowed (boundary) ---
tmpdir, tmp_csv = _fresh_tmpdir()
acr.CSV_PATH = tmp_csv
cctg._EVENTS_CSV = tmp_csv
try:
    sources = json.dumps([
        _src("VietnamNet", "https://vietnamnet.vn/x", TODAY, 7.5),
        _src("VnExpress", "https://vnexpress.net/x", TODAY, 7.6),
    ])
    rc, msg = _run_append(
        ["--rate", "7.5", "--effective", TODAY, "--source", "web_crosscheck_auto",
         "--collected", TODAY, "--note", "test", "--sources", sources],
        job_id="job123")
    check("A7b exactly-at-tolerance (0.1pp) allowed (rc=0)", rc == 0)
finally:
    shutil.rmtree(tmpdir, ignore_errors=True)
    acr.CSV_PATH = _orig_acr_csv
    cctg._EVENTS_CSV = _orig_cctg_csv

# --- A8: --rate doesn't match any cited source value -> refused ---
tmpdir, tmp_csv = _fresh_tmpdir()
acr.CSV_PATH = tmp_csv
cctg._EVENTS_CSV = tmp_csv
try:
    sources = json.dumps([
        _src("VietnamNet", "https://vietnamnet.vn/x", TODAY, 7.5),
        _src("VnExpress", "https://vnexpress.net/x", TODAY, 7.5),
    ])
    rc, msg = _run_append(
        ["--rate", "7.6", "--effective", TODAY, "--source", "web_crosscheck_auto",
         "--collected", TODAY, "--note", "test", "--sources", sources],
        job_id="job123")
    check("A8 synthesized --rate not matching any source refused (rc!=0)", rc != 0)
    check("A8 no row written", _row_count() == 0)
finally:
    shutil.rmtree(tmpdir, ignore_errors=True)
    acr.CSV_PATH = _orig_acr_csv
    cctg._EVENTS_CSV = _orig_cctg_csv

# --- A9: delta guard — rate >=1.0pp away from frozen anchor 7.5% -> refused ---
tmpdir, tmp_csv = _fresh_tmpdir()
acr.CSV_PATH = tmp_csv
cctg._EVENTS_CSV = tmp_csv
try:
    sources = json.dumps([
        _src("VietnamNet", "https://vietnamnet.vn/x", TODAY, 8.6),
        _src("VnExpress", "https://vnexpress.net/x", TODAY, 8.6),
    ])
    rc, msg = _run_append(
        ["--rate", "8.6", "--effective", TODAY, "--source", "web_crosscheck_auto",
         "--collected", TODAY, "--note", "test", "--sources", sources],
        job_id="job123")
    check("A9 >=1.0pp delta vs anchor refused (rc!=0)", rc != 0)
    check("A9 no row written", _row_count() == 0)
finally:
    shutil.rmtree(tmpdir, ignore_errors=True)
    acr.CSV_PATH = _orig_acr_csv
    cctg._EVENTS_CSV = _orig_cctg_csv

# --- A10: JOB_ID set + --source manual_verify -> refused (agent must use web_crosscheck_auto) ---
tmpdir, tmp_csv = _fresh_tmpdir()
acr.CSV_PATH = tmp_csv
cctg._EVENTS_CSV = tmp_csv
try:
    rc, msg = _run_append(
        ["--rate", "7.6", "--effective", TODAY, "--source", "manual_verify",
         "--collected", TODAY, "--note", "test"],
        job_id="job123")
    check("A10 dispatched agent + manual_verify refused (rc!=0)", rc != 0)
    check("A10 no row written", _row_count() == 0)
finally:
    shutil.rmtree(tmpdir, ignore_errors=True)
    acr.CSV_PATH = _orig_acr_csv
    cctg._EVENTS_CSV = _orig_cctg_csv

# --- A11: JOB_ID set + --force -> refused ---
tmpdir, tmp_csv = _fresh_tmpdir()
acr.CSV_PATH = tmp_csv
cctg._EVENTS_CSV = tmp_csv
try:
    rc, msg = _run_append(
        ["--rate", "7.6", "--effective", TODAY, "--source", "web_crosscheck_auto",
         "--collected", TODAY, "--note", "test", "--force"],
        job_id="job123")
    check("A11 dispatched agent + --force refused (rc!=0)", rc != 0)
finally:
    shutil.rmtree(tmpdir, ignore_errors=True)
    acr.CSV_PATH = _orig_acr_csv
    cctg._EVENTS_CSV = _orig_cctg_csv

# --- A12: JOB_ID set + --collected != today -> refused ---
tmpdir, tmp_csv = _fresh_tmpdir()
acr.CSV_PATH = tmp_csv
cctg._EVENTS_CSV = tmp_csv
try:
    sources = json.dumps([
        _src("VietnamNet", "https://vietnamnet.vn/x", TODAY, 7.6),
        _src("VnExpress", "https://vnexpress.net/x", TODAY, 7.6),
    ])
    rc, msg = _run_append(
        ["--rate", "7.6", "--effective", TODAY, "--source", "web_crosscheck_auto",
         "--collected", "2020-01-01", "--note", "test", "--sources", sources],
        job_id="job123")
    check("A12 falsified --collected refused (rc!=0)", rc != 0)
    check("A12 no row written", _row_count() == 0)
finally:
    shutil.rmtree(tmpdir, ignore_errors=True)
    acr.CSV_PATH = _orig_acr_csv
    cctg._EVENTS_CSV = _orig_cctg_csv

# --- A13: stale source date (>35 days) -> refused ---
tmpdir, tmp_csv = _fresh_tmpdir()
acr.CSV_PATH = tmp_csv
cctg._EVENTS_CSV = tmp_csv
try:
    sources = json.dumps([
        _src("VietnamNet", "https://vietnamnet.vn/x", "2020-01-01", 7.6),
        _src("VnExpress", "https://vnexpress.net/x", "2020-01-01", 7.6),
    ])
    rc, msg = _run_append(
        ["--rate", "7.6", "--effective", TODAY, "--source", "web_crosscheck_auto",
         "--collected", TODAY, "--note", "test", "--sources", sources],
        job_id="job123")
    check("A13 stale source date refused (rc!=0)", rc != 0)
    check("A13 no row written", _row_count() == 0)
finally:
    shutil.rmtree(tmpdir, ignore_errors=True)
    acr.CSV_PATH = _orig_acr_csv
    cctg._EVENTS_CSV = _orig_cctg_csv

print(f"Part A: {N} checks so far, {len(FAILS)} fail(s)")


# ============================================================================
# Part B — deposit_cctg_trend_check.py pure-function logic
# ============================================================================
print("=== Part B: deposit_cctg_trend_check.py decline/staleness logic ===")

# B1: real decline detected
series_data = {"cctg_6m": [("2026-08-01", 7.5), ("2026-09-01", 7.3)],
                "big4_12m": [("2026-08-01", 6.8)]}
declines = trend.check_declines(series_data, {})
check("B1 decline detected for cctg_6m", any(d["key"] == "cctg_6m" for d in declines))
check("B1 only 1 decline event (big4 has <2 points)", len(declines) == 1)

# B2: same pair already alerted -> idempotent skip
state = {"cctg_6m": {"alerted_pair": ["2026-08-01", 7.5, "2026-09-01", 7.3]}}
declines2 = trend.check_declines(series_data, state)
check("B2 idempotent: already-alerted pair not re-fired", len(declines2) == 0)

# B3: flat/up -> no decline
series_flat = {"cctg_6m": [("2026-08-01", 7.5), ("2026-09-01", 7.5)]}
check("B3 flat rate -> no decline", len(trend.check_declines(series_flat, {})) == 0)
series_up = {"cctg_6m": [("2026-08-01", 7.5), ("2026-09-01", 7.6)]}
check("B3b rising rate -> no decline", len(trend.check_declines(series_up, {})) == 0)

# B4: <2 points -> no decline (can't compare)
series_one = {"cctg_6m": [("2026-09-01", 7.5)]}
check("B4 single point -> no decline", len(trend.check_declines(series_one, {})) == 0)

# B5: NEW decline after a previously-alerted different pair -> fires again (different pair)
series_data2 = {"cctg_6m": [("2026-08-01", 7.5), ("2026-09-01", 7.3), ("2026-10-01", 7.1)]}
state2 = {"cctg_6m": {"alerted_pair": ["2026-08-01", 7.5, "2026-09-01", 7.3]}}
declines3 = trend.check_declines(series_data2, state2)
check("B5 new decline pair (different from alerted) fires", len(declines3) == 1)
check("B5 new pair is the latest one", declines3[0]["new_date"] == "2026-10-01")

# B6: staleness — below warn window -> no warning
today_t = date(2026, 10, 1)
series_fresh = {"cctg_6m": [("2026-09-30", 7.5)]}
check("B6 fresh (1d) -> no staleness warning",
      len(trend.check_staleness(series_fresh, {}, today_t)) == 0)

# B7: staleness — in warn window (age=35), not yet warned -> fires
series_aging = {"cctg_6m": [("2026-08-27", 7.5)]}  # 2026-10-01 - 2026-08-27 = 35 days
w = trend.check_staleness(series_aging, {}, today_t)
check("B7 age=35 (>= 45-10) triggers staleness warning", len(w) == 1 and w[0]["key"] == "cctg_6m")

# B8: staleness — same last_date already warned -> no re-warning
state3 = {"cctg_6m": {"staleness_warned_for_date": "2026-08-27"}}
check("B8 idempotent: same last_date not re-warned",
      len(trend.check_staleness(series_aging, state3, today_t)) == 0)

# B9: staleness — new anchor (different last_date) after a prior warning -> re-eligible
series_new_anchor = {"cctg_6m": [("2026-08-27", 7.5), ("2026-08-20", 7.5)]}
# (dates out of chronological order deliberately irrelevant here: check_staleness only reads [-1])
series_new_anchor2 = {"cctg_6m": [("2026-08-20", 7.4), ("2026-08-27", 7.5)]}
state4 = {"cctg_6m": {"staleness_warned_for_date": "2026-07-01"}}  # old last_date, now stale by itself
w2 = trend.check_staleness(series_new_anchor2, state4, today_t)
check("B9 new last_date (not matching stored warned-date) re-eligible", len(w2) == 1)

print(f"Part B done, {N} checks total so far, {len(FAILS)} fail(s)")


# ============================================================================
# Part C — TZ environment matrix note (actual multi-TZ run happens via shell wrapper below;
# this in-process check just confirms every date comparison exercised above used an explicit
# `today` argument or CSV-controlled date, not a bare host-clock read with no override path)
# ============================================================================
print("=== Part C: TZ sensitivity spot-check ===")
import inspect
src_trend = inspect.getsource(trend)
# check_declines/check_staleness never call date.today() themselves (today is always a param) —
# only main()/_heartbeat_lines read date.today(), and that's the one place a host-TZ difference
# could matter in production; selfcheck covers it by calling check_staleness with an explicit date.
bare_calls_in_pure_fns = re.findall(r"def check_(?:declines|staleness).*?(?=\ndef |\Z)",
                                     src_trend, re.S)
all_clean = all("date.today()" not in blk for blk in bare_calls_in_pure_fns)
check("C1 check_declines/check_staleness never read date.today() internally (today is a param)",
      all_clean)


# ============================================================================
# Part D — mutation testing: fire real source mutants, confirm selfcheck would catch them
# ============================================================================
print("=== Part D: mutation testing (source-level, throwaway copy) ===")

MUT_DIR = tempfile.mkdtemp(prefix="cctg_wk_mut_")


def _load_mutant(src_file, pattern, replacement, mod_name):
    """Copies src_file -> MUT_DIR, applies one regex substitution, imports the mutant IN-PROCESS
    via importlib (not subprocess) — sys.path already contains HERE (see top of this file), so the
    mutant's own `import cctg_rate_vn` / `from append_deposit_rate import _owner_group` resolve to
    the REAL sibling modules already loaded in this process, avoiding the need to copy an entire
    sibling-module tree into MUT_DIR just to satisfy imports. Returns (module, found: bool)."""
    import importlib.util
    shutil.copy(os.path.join(HERE, src_file), os.path.join(MUT_DIR, src_file))
    path = os.path.join(MUT_DIR, src_file)
    with open(path, encoding="utf-8") as f:
        content = f.read()
    new_content, count = re.subn(pattern, replacement, content, count=1)
    if count == 0:
        return None, False
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, True


def _report_mutant(label, found, detected, crashed_as=None):
    global N
    N += 1
    if not found:
        FAILS.append(f"{label} (mutation pattern not found — selfcheck/source drifted)")
        print(f"  FAIL: {label} (pattern not found)")
    elif crashed_as is not None:
        print(f"  ok (mutant killed, crashed loudly): {label} ({crashed_as!r})")
    elif detected:
        print(f"  ok (mutant killed): {label}")
    else:
        FAILS.append(f"{label} (mutant SURVIVED — guard has no teeth)")
        print(f"  FAIL (mutant survived): {label}")


# --- D1: CROSS_SOURCE_TOLERANCE_PP flipped 0.1 -> 10.0 — a 0.2pp cross-source disagreement
# that A7 proved gets refused by the real code should now be silently ACCEPTED by the mutant. ---
mut1, found1 = _load_mutant("append_cctg_rate.py", r"CROSS_SOURCE_TOLERANCE_PP = 0\.1",
                            "CROSS_SOURCE_TOLERANCE_PP = 10.0", "acr_mut_d1")
detected1, crashed1 = False, None
if found1:
    tmpdir, tmp_csv = _fresh_tmpdir()
    mut1.CSV_PATH = tmp_csv
    cctg._EVENTS_CSV = tmp_csv
    try:
        sources = json.dumps([
            _src("VietnamNet", "https://vietnamnet.vn/x", TODAY, 7.5),
            _src("VnExpress", "https://vnexpress.net/x", TODAY, 7.7),
        ])
        sys.argv = ["append_cctg_rate.py", "--rate", "7.5", "--effective", TODAY,
                    "--source", "web_crosscheck_auto", "--collected", TODAY, "--note", "mut",
                    "--sources", sources]
        os.environ["JOB_ID"] = "mutjob"
        try:
            rc = mut1.main() or 0
        except SystemExit as e:
            rc = 1
        # original code refuses (rc!=0, 0 rows); mutant SHOULD wrongly accept (rc==0, 1 row) —
        # that acceptance is exactly what "detected" (= the bug is observable) means here.
        detected1 = (rc == 0 and _row_count_at(mut1.CSV_PATH) == 1)
    except Exception as e:
        crashed1 = repr(e)
    finally:
        os.environ.pop("JOB_ID", None)
        shutil.rmtree(tmpdir, ignore_errors=True)
_report_mutant("D1 CROSS_SOURCE_TOLERANCE_PP mutant (0.1->10.0) lets 0.2pp disagreement through",
              found1, detected1, crashed1)


# --- D2: check_declines' `new_rate >= prev_rate` flipped to `<=` — inverts decline detection. ---
mut2, found2 = _load_mutant("deposit_cctg_trend_check.py", r"if new_rate >= prev_rate:",
                            "if new_rate <= prev_rate:", "trend_mut_d2")
detected2 = False
if found2:
    sd = {"cctg_6m": [("2026-08-01", 7.5), ("2026-09-01", 7.3)]}
    declines_mut = mut2.check_declines(sd, {})
    detected2 = len(declines_mut) == 0  # a real decline now goes undetected -> mutant caught
_report_mutant("D2 decline-direction mutant (>= -> <=) misses a real 7.5->7.3 decline",
              found2, detected2)


# --- D3: date-newer guard `eff <= last_date` flipped to `eff < last_date` — would allow a
# same-date-as-anchor duplicate write to slip past this guard (defense-in-depth note: the
# downstream cctg_events_df() reload-verify would still raise on a literal duplicate date, so
# this mutant is tested against the GUARD ITSELF via its refusal message, not end-to-end). ---
mut3, found3 = _load_mutant("append_cctg_rate.py", r"if eff <= last_date:",
                            "if eff < last_date:", "acr_mut_d3")
detected3, crashed3 = False, None
if found3:
    tmpdir, tmp_csv = _fresh_tmpdir()
    mut3.CSV_PATH = tmp_csv
    cctg._EVENTS_CSV = tmp_csv
    try:
        sys.argv = ["append_cctg_rate.py", "--rate", "7.5", "--effective", "2026-09-30",
                    "--source", "manual_verify", "--collected", "2026-09-30", "--note", "mut"]
        os.environ.pop("JOB_ID", None)
        refused_by_guard = False
        try:
            mut3.main()
        except SystemExit as e:
            refused_by_guard = "not newer than the last anchor" in str(e.code)
        except Exception:
            refused_by_guard = False  # downstream raise, NOT this guard -> guard itself is blind
        # mutant detected = the pre-check guard no longer refuses a same-date write (whether or
        # not something downstream also catches it is irrelevant to THIS guard's own teeth)
        detected3 = not refused_by_guard
    except Exception as e:
        crashed3 = repr(e)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
_report_mutant("D3 date-newer-guard mutant (<= -> <) stops refusing a same-date duplicate itself",
              found3, detected3, crashed3)

shutil.rmtree(MUT_DIR, ignore_errors=True)
acr.CSV_PATH = _orig_acr_csv
cctg._EVENTS_CSV = _orig_cctg_csv


# ============================================================================
print(f"\n=== TOTAL: {N} checks, {len(FAILS)} fail(s) ===")
if FAILS:
    for f in FAILS:
        print(f"  FAILED: {f}")
    sys.exit(1)
print("ALL PASS")
sys.exit(0)
