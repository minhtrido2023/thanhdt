#!/usr/bin/env python3
"""bq_freshness_check_selfcheck.py — extract-and-test _check()/_check_lastmod() from
bin/bq_freshness_check.sh against a stubbed `bq` + notify.sh/notify_thread.sh, in a
throwaway sandbox.

Why extract instead of duplicate: the function bodies are sliced out of the REAL file at
run time, not retyped here — if someone edits _check()/_check_lastmod() without keeping the
anchor lines in sync, this script breaks loudly instead of silently testing stale code.

Built coord-2026-09-27 (arch-review round 1 required_change #3: bq_freshness_check.sh had
ZERO selfcheck despite gating DollarBill's 19:00 plan dispatch). Round-1 fix distinguished
"bq query failed" from "bảng STALE" — but the fix itself had 2 bugs the arch-reviewer caught
by hand-running it (no test would have needed a human to catch them):
  (a) errsnip taken from tail -1 of a multi-line bq error lost the useful part
      ("southeast1]" instead of the real message) — case_query_fail_multiline_error below.
  (b) rc=0 + non-numeric result (MAX() on an empty table / all-NULL column / renamed column
      returns NULL — bq itself is healthy) got the SAME "kiểm tra auth/quota/network" message
      as a real connection failure — case_rc0_null_result_is_data_not_connection below is the
      negative control: it must NOT say "auth/quota/network".
"""
import subprocess
import sys
from pathlib import Path

REAL = Path("/home/trido/thanhdt/WorkingClaude/mike/bin/bq_freshness_check.sh")
PASS = 0
FAIL = 0


def extract_snippet():
    text = REAL.read_text()
    lines = text.splitlines()
    start = end = None
    for i, ln in enumerate(lines):
        if ln == "_check() {":
            start = i
        if start is not None and ln.startswith("_check_corp_action_scanner() {"):
            end = i
            break
    if start is None or end is None:
        print("FAIL: extraction anchors ('_check() {' / '_check_corp_action_scanner() {') "
              "not found — bq_freshness_check.sh was restructured, this selfcheck is stale",
              file=sys.stderr)
        sys.exit(1)
    return "\n".join(lines[start:end])


HARNESS = """
set -uo pipefail
ROOT="{root}"
TODAY="2026-09-27"
NOW_ICT="10:00 ICT"
DISCORD_STALE_CHANNEL="trading_daily"
PROJECT="fake-project"
FAILED=0
WARNED=0
QUIET=""
"""


def run_bash(snippet, bq_stub, call_line, root):
    (root / "bin").mkdir(parents=True, exist_ok=True)
    (root / "bin" / "notify.sh").write_text('#!/bin/bash\necho "NOTIFY_MAIN: $1"\n')
    (root / "bin" / "notify_thread.sh").write_text('#!/bin/bash\necho "NOTIFY_THREAD: $1 topic=$2"\n')
    for f in ("notify.sh", "notify_thread.sh"):
        (root / "bin" / f).chmod(0o755)
    script = (
        HARNESS.format(root=root)
        + "\nbq() {\n" + bq_stub + "\n}\nexport -f bq\n"
        + snippet + "\n" + call_line
        + '\necho "FAILED=$FAILED WARNED=$WARNED"\n'
    )
    out = subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=60)
    return out.stdout, out.stderr


def check(name, condition, extra=""):
    global PASS, FAIL
    if condition:
        print(f"PASS: {name}")
        PASS += 1
    else:
        print(f"FAIL: {name} {extra}")
        FAIL += 1


import tempfile


def case_query_fail_multiline_error():
    """rc!=0 with a bq error wrapped across multiple lines, matching real bq's mid-token wrap
    (the informative content is NOT on the last line — the last line is a meaningless leftover
    fragment, e.g. a location name split mid-word). Round-1 bug (a): old code took errsnip from
    `tail -1` of the ALREADY-tail-1'd lag_days, which for this shape keeps ONLY the fragment and
    loses the real message. errsnip must now come from the FULL captured output.

    Mutation-tested (arch-review round 2): the OLD stub here put the informative text on the
    LAST line, which `tail -1` happens to preserve — so all 4 assertions passed even on the
    buggy fcbb9d94 code (a vacuous negative control). This version's last line is a genuine
    fragment, so the first-line-content assertions below correctly FAIL on the old code and
    PASS on the fixed code — verify with:
      REAL = Path("<git show fcbb9d94:bin/bq_freshness_check.sh, checked out to a tmp file>")
    """
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        stub = ('echo "BigQuery error in query operation: Error processing job \'proj:job123\':"; '
                 'echo "Not found: Table lithe-record-440915-m9:tav2_bq.no_such_table_zzz was not found in location asia-"; '
                 'echo "southeast1"; return 1')
        out, err = run_bash(extract_snippet(), stub,
                             '_check "table-A" "t.tbl" "t.time" 2 "trading" BLOCK', root)
        check("multiline-error-first-line-kept", "BigQuery error in query operation" in out,
              extra=f"out={out!r} err={err[-300:]}")
        check("multiline-error-not-truncated-to-fragment", "Not found: Table" in out, extra=out)
        check("multiline-error-labelled-query-failed-not-stale", "BQ QUERY FAILED" in out and "STALE" not in out, extra=out)
        check("multiline-error-blocks-pipeline", "FAILED=1 WARNED=0" in out, extra=out)


def case_rc0_null_result_is_data_not_connection():
    """rc=0 but MAX(col) on an empty table / all-NULL column returns NULL -> csv output is
    empty/non-numeric even though bq answered fine. Round-1 bug (b): this got the SAME
    'kiểm tra auth/quota/network' message as an actual connection failure. Negative control:
    the new message must NOT mention auth/quota/network, and must say the data is unusual."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        stub = 'echo "gap_days"; echo ""; return 0'  # CSV header + empty NULL row
        out, err = run_bash(extract_snippet(), stub,
                             '_check "table-B" "t.tbl" "t.time" 2 "trading" BLOCK', root)
        check("rc0-null-not-mislabelled-as-connection-failure",
              "auth/quota/network" not in out.split("BQ DATA")[-1] if "BQ DATA" in out else False,
              extra=out)
        check("rc0-null-labelled-as-data-anomaly", "BQ DATA BẤT THƯỜNG" in out, extra=out)
        check("rc0-null-mentions-not-connection-error", "KHÔNG PHẢI lỗi kết nối BQ" in out, extra=out)
        check("rc0-null-still-blocks-pipeline", "FAILED=1 WARNED=0" in out, extra=out)


def case_real_staleness_still_blocks():
    """rc=0, numeric, over threshold -> must still be the ORIGINAL stale/blocking behavior,
    unaffected by the new error-branch (negative control for over-fixing)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        stub = 'echo "gap_days"; echo "5"; return 0'
        out, err = run_bash(extract_snippet(), stub,
                             '_check "table-C" "t.tbl" "t.time" 2 "trading" BLOCK', root)
        check("real-staleness-still-labelled-stale", "bảng STALE" in out, extra=out)
        check("real-staleness-not-mislabelled-query-failed", "BQ QUERY FAILED" not in out, extra=out)
        check("real-staleness-still-blocks", "FAILED=1 WARNED=0" in out, extra=out)


def case_fresh_ok_no_notify():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        stub = 'echo "gap_days"; echo "0"; return 0'
        out, err = run_bash(extract_snippet(), stub,
                             '_check "table-D" "t.tbl" "t.time" 2 "trading" BLOCK', root)
        check("fresh-ok-no-fail", "FAILED=0 WARNED=0" in out, extra=out)
        check("fresh-ok-no-notify-sent", "NOTIFY_" not in out, extra=out)


def case_warn_mode_query_fail_does_not_block():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        stub = 'echo "some transient error"; return 1'
        out, err = run_bash(extract_snippet(), stub,
                             '_check "table-E" "t.tbl" "t.time" 2 "trading" WARN', root)
        check("warn-mode-query-fail-warns-not-blocks", "FAILED=0 WARNED=1" in out, extra=out)
        check("warn-mode-query-fail-only-thread-notify", "NOTIFY_MAIN" not in out and "NOTIFY_THREAD" in out, extra=out)


def case_lastmod_show_fail_distinct_message():
    """_check_lastmod: bq show failure (rc!=0) must be labelled as a query failure, never
    as 'writer chết' (round-1 fix applied same errsnip pattern here)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        stub = 'echo "line1 of a wrapped bq show error"; echo "Permission denied on resource"; return 1'
        out, err = run_bash(extract_snippet(), stub,
                             '_check_lastmod "table-F" "t.tbl" 4', root)
        check("lastmod-show-fail-full-message-kept", "Permission denied" in out, extra=out)
        check("lastmod-show-fail-not-labelled-writer-dead", "WRITER-DEAD" not in out, extra=out)
        check("lastmod-show-fail-warn-only-never-blocks", "FAILED=0 WARNED=1" in out, extra=out)


def case_lastmod_missing_lastmodified_warns():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        stub = 'echo "{}"; return 0'  # valid JSON, but no lastModifiedTime key
        out, err = run_bash(extract_snippet(), stub,
                             '_check_lastmod "table-G" "t.tbl" 4', root)
        check("lastmod-missing-field-warns-writer-dead", "WRITER-DEAD" in out, extra=out)
        check("lastmod-missing-field-does-not-block", "FAILED=0 WARNED=1" in out, extra=out)


if __name__ == "__main__":
    case_query_fail_multiline_error()
    case_rc0_null_result_is_data_not_connection()
    case_real_staleness_still_blocks()
    case_fresh_ok_no_notify()
    case_warn_mode_query_fail_does_not_block()
    case_lastmod_show_fail_distinct_message()
    case_lastmod_missing_lastmodified_warns()
    print(f"\nbq_freshness_check_selfcheck: {PASS} PASS, {FAIL} FAIL")
    sys.exit(1 if FAIL else 0)
