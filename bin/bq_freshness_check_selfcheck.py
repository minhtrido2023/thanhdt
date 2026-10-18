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


def extract_pipeline0():
    """Đoạn [pipeline-0] → hết cổng FAILED (trước '=== ALL FRESH'), lấy từ bản CÙNG THƯ MỤC với
    selfcheck này (không phải REAL cứng) để test được cả worktree."""
    lines = Path(__file__).with_name("bq_freshness_check.sh").read_text().splitlines()
    start = next((i for i, ln in enumerate(lines) if ln.startswith('echo; echo "--- [pipeline-0]')), None)
    end = next((i for i, ln in enumerate(lines) if ln.startswith('echo "=== ALL FRESH')), None)
    if start is None or end is None:
        print("FAIL: anchors [pipeline-0] / '=== ALL FRESH' not found — selfcheck stale", file=sys.stderr)
        sys.exit(1)
    return "\n".join(lines[start:end])


def case_pipeline0_exdate_forecast_runs_before_failed_gate():
    """nav_exdate_forecast (lịch corp-action + trạng thái feed, 2026-10-04) phải chạy với --alert,
    TRƯỚC cổng BQ-FAILED (BQ stale không được nuốt cảnh báo), và lỗi/crash của nó KHÔNG chặn pipeline.
    Stub ghi lại args; stub thoát rc=1 để chứng minh nhánh '|| echo [WARN]' không chặn."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "bin").mkdir(parents=True)
        (root / "bin" / "nav_exdate_forecast.py").write_text(
            'import sys\nprint("STUB_EXDATE_CALLED", " ".join(sys.argv[1:]))\nsys.exit(1)\n')
        harness_fail = 'FAILED=1\n'
        out, _err = run_bash(harness_fail + extract_pipeline0(), "return 0", ":", root)
        check("pipeline0-exdate-called-with---alert", "STUB_EXDATE_CALLED --alert" in out, extra=out)
        check("pipeline0-exdate-crash-is-nonblocking-WARN", "nav_exdate_forecast.py lỗi" in out, extra=out)
        i_call, i_gate = out.find("STUB_EXDATE_CALLED"), out.find("BQ STALE")
        check("pipeline0-exdate-runs-BEFORE-bq-failed-gate (stale BQ không nuốt cảnh báo)",
              0 <= i_call < i_gate, extra=out)
        check("pipeline0-failed-gate-still-blocks-after-exdate-crash",
              "=== FAILED" in out and "FAILED=" not in out.split("=== FAILED")[-1], extra=out)


def case_exdate_forecast_selfcheck_green():
    """Selfcheck của chính nav_exdate_forecast (gồm ca feed STALE/_FAILED/khoẻ/không-đọc-được) phải xanh."""
    r = subprocess.run([sys.executable, str(Path(__file__).with_name("nav_exdate_forecast_selfcheck.py"))],
                       capture_output=True, text=True, timeout=120)
    check("exdate-forecast-selfcheck-green-incl-feed-status-cases",
          r.returncode == 0 and "FAIL=0" in r.stdout, extra=r.stdout[-300:] + r.stderr[-300:])


# ───────────────────── GATE-SOURCE check ngay sau [pipeline-1] (retro 2026-10-11 Pattern I) ──
# Trích NGUYÊN VĂN đoạn `PIPELINE_START_EPOCH=` → trước `# [pipeline-1b]` + hàm _run_pipeline từ
# bản bq_freshness_check.sh CÙNG THƯ MỤC, chạy trong sandbox: publisher là stub, notify/bus là stub
# ghi log ⇒ KHÔNG ping Discord/Telegram/bus thật, KHÔNG publish thật.
import json
import os
import shutil

_HERE = Path(__file__).resolve().parent
GS_SCRIPT = Path(os.environ.get("BQ_FRESHNESS_SCRIPT") or _HERE / "bq_freshness_check.sh")
GS_HELPER = _HERE / "gate_source_check.py"
_PUB_CALL = '_run_pipeline "[pipeline-1] publish_gated_state"      deploy_golive_dt5g_v4/publish_gated_state.py'

# Stub publisher: in y như publisher thật (header, dòng cổng, dòng today) + 1 dòng stderr, ghi
# golive_state_today.json theo STUB_SRC. NO_WRITE = publisher chết trước khi ghi file.
_STUB_PUBLISHER = r"""
import json, os, sys
src = os.environ["STUB_SRC"]
print("=" * 20); print("  PUBLISH GATED STATE (DT5G, fail-safe)  -> 2026-10-12"); print("=" * 20)
print("stub stderr line", file=sys.stderr)
if src == "NO_WRITE":
    print("  !!! stub: chết trước khi ghi state"); sys.exit(1)
real = {"MISSING_FIELD": "DT4_only", "CORRUPT": "DT4_only", "NO_GATE_LINE": "DT4_only"}.get(src, src)
if src != "NO_GATE_LINE":
    print(f"[get_gated_state] {real}: health report 2903min old (> 1440) -> DT4_only" if real != "DT5G_macro"
          else "[get_gated_state] DT5G_macro: health=HEALTHY -> DT5G_macro")
doc = {"published_at": os.environ.get("STUB_PUBLISHED_AT", "2026-10-12T19:01:21"), "as_of": "2026-10-12",
       "state": 3, "base_state_dt4": 3, "macro_state_dt5g": 2, "source": real,
       "bq_table": "tav2_bq.vnindex_5state_dt5g_live", "bq_publish_ok": True}
if src == "MISSING_FIELD":
    del doc["source"]
path = "deploy_golive_dt5g_v4/golive_state_today.json"
with open(path, "w", encoding="utf-8") as f:
    f.write('{"published_at": "2026-10-12T19:01:21", "as_of":' if src == "CORRUPT" else json.dumps(doc, indent=2))
print(f"  today: as_of=2026-10-12 state=3 source={real} (DT4=3, DT5G=2)")
print("DONE.")
"""


def gs_extract(script=None, baseline=False):
    """(hàm _run_pipeline, đoạn publish). baseline=True ⇒ đoạn publish chỉ còn dòng gọi
    [pipeline-1] trần như TRƯỚC khi có bước kiểm — đối chứng 'ngày thường y như không có nó'."""
    lines = Path(script or GS_SCRIPT).read_text(encoding="utf-8").splitlines()
    f0 = next((i for i, ln in enumerate(lines) if ln == "_run_pipeline() {"), None)
    f1 = next((i for i in range(f0 or 0, len(lines)) if lines[i] == "}"), None)
    s = next((i for i, ln in enumerate(lines) if ln.startswith("PIPELINE_START_EPOCH=")), None)
    e = next((i for i, ln in enumerate(lines) if ln.startswith("# [pipeline-1a]")), None)
    if None in (f0, f1, s, e) or not any(_PUB_CALL in ln for ln in lines[s:e]):
        print("FAIL: anchors _run_pipeline / PIPELINE_START_EPOCH= / [pipeline-1] / [pipeline-1b] "
              "not found — selfcheck stale", file=sys.stderr)
        sys.exit(1)
    seg = [lines[s], _PUB_CALL] if baseline else lines[s:e]
    return "\n".join(lines[f0:f1 + 1]), "\n".join(seg)


def gs_sandbox(td, with_helper=True, health='{"ts": "2026-10-10T18:37:02+07:00", "status": "HEALTHY", '
                                             '"recommended_state_source": "DT5G_macro"}'):
    td = Path(td)
    mb, wc = td / "mike" / "bin", td / "wc"
    mb.mkdir(parents=True)
    (wc / "deploy_golive_dt5g_v4").mkdir(parents=True)
    (wc / "data").mkdir()
    (wc / "deploy_golive_dt5g_v4" / "publish_gated_state.py").write_text(_STUB_PUBLISHER, encoding="utf-8")
    if health is not None:
        (wc / "data" / "macro_health.json").write_text(health, encoding="utf-8")
    # stub kênh báo: mỗi lần gọi = 1 dòng JSON; rc đọc từ file <tên>.rc (mặc định 0)
    for name in ("notify.sh", "notify_thread.sh", "append_event.sh"):
        (mb / name).write_text(
            '#!/usr/bin/env bash\n'
            'python3 -c \'import json,sys; print(json.dumps(sys.argv[1:], ensure_ascii=False))\' '
            f'"{name}" "$@" >> "{td}/calls.log"\n'
            f'exit "$(cat "{td}/{name}.rc" 2>/dev/null || echo 0)"\n', encoding="utf-8")
        (mb / name).chmod(0o755)
    if with_helper:
        shutil.copy(GS_HELPER, mb / "gate_source_check.py")
    return td


def gs_run(td, src, script=None, baseline=False, published_at=None, pre="", env_extra=None):
    """Chạy đoạn publish 1 lần. Trả (stdout, stderr). `pre` = bash chèn trước đoạn publish."""
    td = Path(td)
    fn, seg = gs_extract(script, baseline)
    body = (f'set -uo pipefail\nROOT="{td}/mike"\nWORKDIR="{td}/wc"\nPY=python3\nFAILED=0\nWARNED=0\n'
            f'{fn}\ncd "$WORKDIR"\n{pre}\n{seg}\necho "__END__ FAILED=$FAILED"\n')
    env = dict(os.environ, STUB_SRC=src, TMPDIR=str(td))
    env.pop("JOB_ID", None)
    env.pop("GATE_SOURCE_SEND_TIMEOUT_S", None)
    if published_at:
        env["STUB_PUBLISHED_AT"] = published_at
    env.update(env_extra or {})
    r = subprocess.run(["bash", "-c", body], capture_output=True, text=True, timeout=120, env=env)
    return r.stdout, r.stderr


def gs_run_combined(td, src, baseline=False, timeout=120):
    """Chạy như CRON: stdout + stderr vào CÙNG MỘT FILE (`>> log 2>&1`). Trả (rc|"TIMEOUT", bytes log, giây)."""
    import time
    td = Path(td)
    fn, seg = gs_extract(None, baseline)
    body = (f'set -uo pipefail\nROOT="{td}/mike"\nWORKDIR="{td}/wc"\nPY=python3\nFAILED=0\nWARNED=0\n'
            f'{fn}\ncd "$WORKDIR"\n{seg}\necho "__END__ FAILED=$FAILED"\n')
    env = dict(os.environ, STUB_SRC=src, TMPDIR=str(td))
    env.pop("JOB_ID", None)
    log = td / "combined.log"
    t0 = time.monotonic()
    with open(log, "ab") as lf:
        try:
            rc = subprocess.run(["bash", "-c", body], stdout=lf, stderr=subprocess.STDOUT, env=env,
                                timeout=timeout).returncode
        except subprocess.TimeoutExpired:
            rc = "TIMEOUT"
    return rc, log.read_bytes(), time.monotonic() - t0


def gs_calls(td):
    p = Path(td) / "calls.log"
    return [json.loads(ln) for ln in p.read_text(encoding="utf-8").splitlines()] if p.exists() else []


def gs_count(td):
    c = gs_calls(td)
    return (sum(1 for x in c if x[0] == "notify_thread.sh"), sum(1 for x in c if x[0] == "append_event.sh"),
            sum(1 for x in c if x[0] == "notify.sh"))


def gs_marker(td):
    p = Path(td) / "wc" / "data" / "gate_source_alert.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _gs_sent(td, src):
    """Các kênh đã đánh dấu gửi cho cặp (ngày publish của marker, nguồn)."""
    m = gs_marker(td) or {}
    return (m.get("sent") or {}).get(f"{m.get('publish_date')}|{src}")


def case_gate_source_dt5g_macro_is_invisible():
    """Ngày thường: stdout và stderr y hệt từng byte đoạn publish TRẦN (không có bước kiểm), không
    tin, không bus, không file nào được ghi thêm, không sót file tạm."""
    with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
        base_out, base_err = gs_run(gs_sandbox(a), "DT5G_macro", baseline=True)
        out, err = gs_run(gs_sandbox(b), "DT5G_macro")
        check("gate-source DT5G_macro: stdout byte-identical với đoạn publish trần", out == base_out,
              extra=f"\n--- trần ---\n{base_out}\n--- mới ---\n{out}")
        check("gate-source DT5G_macro: stderr byte-identical với đoạn publish trần", err == base_err,
              extra=f"base={base_err!r} new={err!r}")
        check("gate-source DT5G_macro: stub publisher đã chạy thật (đối chứng không rỗng)",
              "[get_gated_state] DT5G_macro" in out and "__END__ FAILED=0" in out, extra=out)
        check("gate-source DT5G_macro: 0 tin, 0 bus", gs_count(b) == (0, 0, 0), extra=str(gs_calls(b)))
        check("gate-source DT5G_macro: không ghi gate_source_alert.json", gs_marker(b) is None)
        left = sorted(p.name for p in Path(b).iterdir() if p.name not in ("mike", "wc"))
        check("gate-source DT5G_macro: không sót file tạm", left == [], extra=str(left))
    # Như CRON (`>> log 2>&1`, stdout+stderr chung một file). Publisher không ghi stderr (đúng log
    # thật [pipeline-1] ngày thường) ⇒ log gộp y hệt TỪNG BYTE đoạn trần. Publisher CÓ ghi stderr ⇒
    # cùng tập dòng, chỉ dòng stderr đổi chỗ (stdout nay đi qua file rồi mới `cat` ra) — ghim đúng
    # thực tế đó, không giả vờ byte-identical.
    quiet = _STUB_PUBLISHER.replace('print("stub stderr line", file=sys.stderr)\n', "")
    for label, pub, exact in (("publisher không ghi stderr", quiet, True), ("publisher có ghi stderr", _STUB_PUBLISHER, False)):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            for d in (a, b):
                gs_sandbox(d)
                (Path(d) / "wc" / "deploy_golive_dt5g_v4" / "publish_gated_state.py").write_text(pub, encoding="utf-8")
            rc0, log0, _ = gs_run_combined(a, "DT5G_macro", baseline=True)
            rc1, log1, _ = gs_run_combined(b, "DT5G_macro")
            if exact:
                check(f"gate-source DT5G_macro log gộp như cron ({label}): rc + từng byte y hệt đoạn trần",
                      rc0 == rc1 == 0 and log0 == log1 and b"[get_gated_state] DT5G_macro" in log1,
                      extra=f"rc {rc0}/{rc1}\n--- trần ---\n{log0.decode()}\n--- mới ---\n{log1.decode()}")
            else:
                check(f"gate-source DT5G_macro log gộp như cron ({label}): rc + cùng tập dòng, cùng số byte",
                      rc0 == rc1 == 0 and sorted(log0.splitlines()) == sorted(log1.splitlines())
                      and len(log0) == len(log1) and b"stub stderr line" in log1,
                      extra=f"rc {rc0}/{rc1}\n--- trần ---\n{log0.decode()}\n--- mới ---\n{log1.decode()}")


def case_gate_source_dt4_only_alerts_once():
    """DT4_only ⇒ đúng 1 tin Trading Daily + 1 bus error (khoá theo ngày publish) + bằng chứng cho
    plan report; KHÔNG Telegram, KHÔNG chặn; chạy lại cùng ngày ⇒ không lặp."""
    with tempfile.TemporaryDirectory() as td:
        gs_sandbox(td)
        out, _ = gs_run(td, "DT4_only")
        calls = gs_calls(td)
        nt = [c for c in calls if c[0] == "notify_thread.sh"]
        bus = [c for c in calls if c[0] == "append_event.sh"]
        check("gate-source DT4_only: đúng 1 tin Discord + 1 bus, 0 Telegram", gs_count(td) == (1, 1, 0), extra=str(calls))
        msg = nt[0][1] if nt else ""
        check("gate-source DT4_only: tin vào topic trading_daily", bool(nt) and nt[0][2] == "trading_daily", extra=str(nt))
        check("gate-source DT4_only: tin nêu nguồn + KHÔNG chặn", "ra nguồn DT4_only" in msg and "KHÔNG bị chặn" in msg, extra=msg)
        check("gate-source DT4_only: tin trích NGUYÊN VĂN dòng cổng của lượt này",
              "«[get_gated_state] DT4_only: health report 2903min old (> 1440) -> DT4_only»" in msg, extra=msg)
        check("gate-source DT4_only: tin trích status + ts của macro_health.json",
              "status=HEALTHY, ts=2026-10-10T18:37:02+07:00" in msg, extra=msg)
        m = gs_marker(td) or {}
        day = m.get("publish_date", "?")
        check("gate-source DT4_only: bus = Taylor error, topic khoá theo ngày publish",
              bool(bus) and bus[0][1:4] == ["Taylor", "error", f"dt5g-gate-source-degraded-{day}"], extra=str(bus))
        payload = json.loads(bus[0][4]) if bus else {}
        check("gate-source DT4_only: bus payload mang nguồn + dòng cổng + blocking=false",
              payload.get("source") == "DT4_only" and payload.get("blocking") is False
              and "[get_gated_state] DT4_only" in str(payload.get("gate_line")), extra=str(payload))
        check("gate-source DT4_only: marker ghi bằng chứng + đã gửi 2 kênh",
              m.get("source") == "DT4_only" and m.get("sent") == {f"{day}|DT4_only": {"discord": True, "bus": True}}
              and m.get("published_at") == "2026-10-12T19:01:21", extra=str(m))
        check("gate-source DT4_only: KHÔNG chặn — chuỗi chạy tiếp, FAILED=0, output publish còn nguyên",
              "__END__ FAILED=0" in out and "  [ok] [pipeline-1] publish_gated_state" in out, extra=out)
        check("gate-source DT4_only: log có dòng WARN gate-source", "WARN gate-source:" in out, extra=out)
        check("gate-source DT4_only: helper thoát 0 (cảnh báo không phải lỗi)", "thoát rc=" not in out, extra=out)

        out2, _ = gs_run(td, "DT4_only", published_at="2026-10-12T19:40:00")
        check("gate-source chạy lại cùng ngày: KHÔNG tin/bus thứ hai", gs_count(td) == (1, 1, 0), extra=str(gs_calls(td)))
        check("gate-source chạy lại cùng ngày: nói rõ là không gửi lại", out2.count("không gửi lại") == 2, extra=out2)
        check("gate-source chạy lại cùng ngày: marker theo bản publish MỚI NHẤT (cho plan report)",
              (gs_marker(td) or {}).get("published_at") == "2026-10-12T19:40:00", extra=str(gs_marker(td)))

        # ngày publish KHÁC (marker cũ của hôm trước) ⇒ là sự kiện mới, phải báo lại
        m = gs_marker(td); m["publish_date"] = "2000-01-01"
        m["sent"] = {"2000-01-01|DT4_only": {"discord": True, "bus": True}}
        (Path(td) / "wc" / "data" / "gate_source_alert.json").write_text(json.dumps(m), encoding="utf-8")
        gs_run(td, "DT4_only")
        check("gate-source ngày publish khác: báo lại (khoá theo NGÀY, không khoá vĩnh viễn)",
              gs_count(td) == (2, 2, 0), extra=str(gs_calls(td)))


def case_gate_source_other_degraded_values():
    """DT4_STALE, giá trị lạ, thiếu trường, file hỏng ⇒ mỗi ca đúng 1 tin + 1 bus, không chặn."""
    for src, needle, no_cap in (
            ("DT4_STALE", "ra nguồn DT4_STALE", True),
            ("LA_LUNG_v9", "ra nguồn LA_LUNG_v9", False),
            ("MISSING_FIELD", "ra nguồn <thiếu trường source>", False),
            ("CORRUPT", "KHÔNG đọc được deploy_golive_dt5g_v4/golive_state_today.json vừa ghi (JSONDecodeError", False)):
        with tempfile.TemporaryDirectory() as td:
            gs_sandbox(td)
            out, _ = gs_run(td, src)
            nt = [c for c in gs_calls(td) if c[0] == "notify_thread.sh"]
            msg = nt[0][1] if nt else ""
            check(f"gate-source {src}: đúng 1 tin + 1 bus, không chặn",
                  gs_count(td) == (1, 1, 0) and "__END__ FAILED=0" in out, extra=str(gs_calls(td)) + out)
            check(f"gate-source {src}: tin nói đúng điều đọc được", needle in msg, extra=msg)
            # chỉ 2 nguồn cổng chủ động trả mới được khẳng định 'KHÔNG áp macro cap' — còn lại không đoán
            check(f"gate-source {src}: không khẳng định quá bằng chứng về macro cap",
                  ("state này KHÔNG áp macro cap" in msg) == no_cap
                  and ("KHÔNG xác nhận được state này có áp macro cap" in msg) == (not no_cap), extra=msg)
            gs_run(td, src)
            check(f"gate-source {src}: chạy lại không lặp", gs_count(td) == (1, 1, 0), extra=str(gs_calls(td)))


def case_gate_source_evidence_missing_is_said_not_guessed():
    """§29: không có dòng cổng / không đọc được health ⇒ NÓI 'không tìm thấy' / lỗi thật, không dựng nguyên nhân."""
    with tempfile.TemporaryDirectory() as td:
        gs_sandbox(td, health=None)
        gs_run(td, "NO_GATE_LINE")
        nt = [c for c in gs_calls(td) if c[0] == "notify_thread.sh"]
        msg = nt[0][1] if nt else ""
        check("gate-source không có dòng cổng: tin nói 'không tìm thấy'",
              "không tìm thấy dòng [get_gated_state] trong output lượt publish này" in msg and "«" not in msg, extra=msg)
        check("gate-source không có file health: tin nêu lỗi thật",
              "data/macro_health.json: KHÔNG đọc được (FileNotFoundError" in msg, extra=msg)
        check("gate-source không có bằng chứng: không dựng nguyên nhân", "min old" not in msg and "HEALTHY" not in msg, extra=msg)


def case_gate_source_publish_did_not_run_is_not_reported_twice():
    """Publisher chết trước khi ghi file ⇒ file state CŨ (đang DT4_only) không phải bản publish của
    lượt này ⇒ KHÔNG báo nguồn cổng (đã có _assert_fresh_artifact chặn + báo ARTIFACT STALE)."""
    with tempfile.TemporaryDirectory() as td:
        gs_sandbox(td)
        old = Path(td) / "wc" / "deploy_golive_dt5g_v4" / "golive_state_today.json"
        old.write_text('{"as_of": "2026-10-09", "source": "DT4_only", "published_at": "2026-10-09T19:01:21"}')
        os.utime(old, (1_000_000_000, 1_000_000_000))
        out, _ = gs_run(td, "NO_WRITE")
        check("gate-source publish không chạy: 0 tin, 0 bus", gs_count(td) == (0, 0, 0), extra=str(gs_calls(td)))
        check("gate-source publish không chạy: log nói rõ bỏ qua, không ghi marker",
              "SKIP gate-source" in out and gs_marker(td) is None, extra=out)
        old.unlink()
        out, _ = gs_run(td, "NO_WRITE")
        check("gate-source file state không tồn tại: 0 tin, 0 bus, có dòng SKIP",
              gs_count(td) == (0, 0, 0) and "SKIP gate-source" in out, extra=out)


def case_gate_source_failed_send_is_retried_not_marked():
    """Kênh Discord hỏng ⇒ không đánh dấu, nêu lỗi thật; lượt chạy lại gửi bù ĐÚNG kênh thiếu (bus không lặp)."""
    with tempfile.TemporaryDirectory() as td:
        gs_sandbox(td)
        (Path(td) / "notify_thread.sh.rc").write_text("1")
        out, _ = gs_run(td, "DT4_only")
        check("gate-source Discord hỏng: nêu lỗi thật, chưa đánh dấu discord, bus vẫn ghi",
              "gửi discord THẤT BẠI — Lỗi thật: rc=1" in out and _gs_sent(td, "DT4_only") == {"bus": True}
              and "__END__ FAILED=0" in out, extra=out + str(gs_marker(td)))
        # N5: câu WARN không được hứa một lượt tự chạy lại không tồn tại; phải nêu lưới còn lại thật
        check("gate-source Discord hỏng: WARN nêu lưới còn lại, không hứa 'lượt chạy lại sẽ thử lại'",
              "sẽ thử lại" not in out and "KHÔNG có lượt tự chạy lại cùng ngày" in out
              and "bus event error" in out and "báo cáo plan 21:00" in out and "check 13" in out, extra=out)
        (Path(td) / "notify_thread.sh.rc").write_text("0")
        gs_run(td, "DT4_only")
        check("gate-source chạy lại sau khi kênh sống: gửi bù Discord, bus KHÔNG lặp",
              gs_count(td) == (2, 1, 0) and _gs_sent(td, "DT4_only") == {"bus": True, "discord": True},
              extra=str(gs_calls(td)))


def case_gate_source_recovered_rerun_and_helper_crash():
    """Chạy lại ra DT5G_macro ⇒ im lặng; helper mất/crash ⇒ WARN có rc, KHÔNG chặn chuỗi."""
    with tempfile.TemporaryDirectory() as td:
        gs_sandbox(td)
        gs_run(td, "DT4_only")
        out, _ = gs_run(td, "DT5G_macro", published_at="2026-10-12T19:50:00")
        check("gate-source chạy lại đã về DT5G_macro: không tin mới, không dòng WARN",
              gs_count(td) == (1, 1, 0) and "gate-source" not in out, extra=out)
        sys.path.insert(0, str(_HERE))
        import gate_source_check as g
        check("gate-source plan_report_line: bản publish hiện tại DT5G_macro ⇒ rỗng dù còn marker cũ",
              g.plan_report_line(str(Path(td) / "wc")) == "")
    with tempfile.TemporaryDirectory() as td:
        gs_sandbox(td, with_helper=False)
        out, _ = gs_run(td, "DT4_only")
        check("gate-source helper không chạy được: WARN nêu rc, chuỗi chạy tiếp",
              "gate_source_check.py thoát rc=2" in out and "__END__ FAILED=0" in out, extra=out)


def case_gate_source_kill_cleans_tmp():
    """Cron bị kill (SIGTERM) NGAY sau khi publish xong, trước dòng `rm` ⇒ trap EXIT vẫn dọn file tạm."""
    src_lines = Path(GS_SCRIPT).read_text(encoding="utf-8")
    kill_src = src_lines.replace('  cat "$GATE_PUB_OUT"\n', '  kill -TERM $$\n', 1)
    check("gate-source kill: tiêm được SIGTERM vào bản sao script (bất biến của test)", kill_src != src_lines)
    with tempfile.TemporaryDirectory() as td:
        gs_sandbox(td)
        mut = Path(td) / "script_kill.sh"
        mut.write_text(kill_src, encoding="utf-8")
        out, err = gs_run(td, "DT4_only", script=str(mut))
        left = sorted(x.name for x in Path(td).glob("tmp.*"))
        check("gate-source kill giữa chừng (SIGTERM trước rm): KHÔNG còn file mktemp trong TMPDIR",
              left == [] and "__END__" not in out, extra=f"left={left} out={out[-120:]!r}")


def case_gate_source_mktemp_fails():
    """mktemp hỏng ⇒ rơi về /dev/null: output publish vẫn ra log nguyên vẹn, vẫn báo nguồn cổng, tin
    nói thẳng là không giữ được output (không giả vờ 'không tìm thấy dòng cổng'), stderr không có lỗi cat/rm."""
    stub = 'mktemp() { echo "mktemp: stub hỏng" >&2; return 1; }'
    with tempfile.TemporaryDirectory() as td:
        gs_sandbox(td)
        out, err = gs_run(td, "DT4_only", pre=stub)
        nt = [c for c in gs_calls(td) if c[0] == "notify_thread.sh"]
        msg = nt[0][1] if nt else ""
        check("gate-source mktemp hỏng: vẫn đúng 1 tin + 1 bus, chuỗi chạy tiếp",
              gs_count(td) == (1, 1, 0) and "__END__ FAILED=0" in out, extra=out + err)
        check("gate-source mktemp hỏng: output publish vẫn ra log", "[get_gated_state] DT4_only" in out, extra=out)
        check("gate-source mktemp hỏng: tin nói 'output lượt publish không được giữ lại'",
              "dòng cổng tự in: output lượt publish không được giữ lại" in msg, extra=msg)
        check("gate-source mktemp hỏng: stderr chỉ có lỗi mktemp thật + dòng stub, không lỗi tee/rm",
              err == "mktemp: stub hỏng\nstub stderr line\n", extra=repr(err))
    with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
        base_out, _ = gs_run(gs_sandbox(a), "DT5G_macro", baseline=True)
        out, _ = gs_run(gs_sandbox(b), "DT5G_macro", pre=stub)
        check("gate-source mktemp hỏng + DT5G_macro: stdout vẫn byte-identical, 0 tin",
              out == base_out and gs_count(b) == (0, 0, 0), extra=out)


def case_gate_source_orphan_holding_stdout_does_not_hang():
    """B1 (arch-review 2026-10-12): publisher để lại tiến trình CHÁU mồ côi còn giữ stdout (mô phỏng
    notify.sh → notify_discord.sh → curl treo) ⇒ đoạn publish vẫn xong ngay như bản trần. Quay lại
    `| tee` (hay bất kỳ pipe nào) ⇒ đầu đọc chờ EOF tới khi tiến trình cháu chết ⇒ ca này đỏ."""
    orphan = _STUB_PUBLISHER + r"""
import subprocess
subprocess.Popen(["bash", "-c", "echo $$ > orphan.pid; exec sleep 20"], stderr=subprocess.DEVNULL)
"""
    with tempfile.TemporaryDirectory() as td:
        gs_sandbox(td)
        (Path(td) / "wc" / "deploy_golive_dt5g_v4" / "publish_gated_state.py").write_text(orphan, encoding="utf-8")
        rc, log, secs = gs_run_combined(td, "DT4_only", timeout=60)
        pidf = Path(td) / "wc" / "orphan.pid"
        alive = False
        if pidf.exists():
            try:
                os.kill(int(pidf.read_text().strip()), 0)
                alive = True
            except (OSError, ValueError):
                pass
        text = log.decode("utf-8", "replace")
        check("gate-source tiến trình cháu giữ stdout: đoạn publish xong trong vài giây (không chờ nó)",
              rc == 0 and secs < 8, extra=f"rc={rc} {secs:.1f}s\n{text}")
        check("gate-source tiến trình cháu giữ stdout: đối chứng — tiến trình cháu CÒN SỐNG lúc chuỗi đã xong",
              alive, extra=f"pidfile={pidf.exists()}")
        check("gate-source tiến trình cháu giữ stdout: output publish còn đủ + vẫn báo nguồn cổng",
              "[get_gated_state] DT4_only" in text and "  [ok] [pipeline-1] publish_gated_state" in text
              and "__END__ FAILED=0" in text and gs_count(td) == (1, 1, 0), extra=text + str(gs_calls(td)))
        if alive:
            try:
                os.kill(int(pidf.read_text().strip()), 9)
            except OSError:
                pass


def case_gate_source_marker_unwritable_still_alerts():
    """N1: không ghi được data/gate_source_alert.json (data/ chỉ-đọc, đĩa đầy) ⇒ VẪN gửi Discord + bus,
    WARN nêu lỗi thật và nói đúng là ĐÃ thấy suy giảm, chuỗi chạy tiếp."""
    with tempfile.TemporaryDirectory() as td:
        gs_sandbox(td)
        # file .tmp là THƯ MỤC ⇒ open(tmp, "w") ném IsADirectoryError kể cả khi chạy bằng root
        (Path(td) / "wc" / "data" / "gate_source_alert.json.tmp").mkdir()
        out, _ = gs_run(td, "DT4_only")
        check("gate-source không ghi được dấu: VẪN đúng 1 tin Discord + 1 bus",
              gs_count(td) == (1, 1, 0), extra=str(gs_calls(td)) + out)
        check("gate-source không ghi được dấu: WARN nêu lỗi thật + nói đã phát hiện suy giảm",
              "KHÔNG ghi được data/gate_source_alert.json — Lỗi thật: IsADirectoryError" in out
              and "ĐÃ được phát hiện" in out and "KHÔNG kiểm được nguồn cổng" not in out, extra=out)
        check("gate-source không ghi được dấu: helper thoát 0, chuỗi chạy tiếp, không có file dấu",
              "thoát rc=" not in out and "__END__ FAILED=0" in out and gs_marker(td) is None, extra=out)


def case_gate_source_publish_time_is_ict_anchored():
    """N2: ngày publish + giờ trong tin neo ICT theo mtime file state, KHÔNG theo TZ của máy. mtime cố
    định quanh nửa đêm ICT; chạy helper dưới TZ lạ. fromtimestamp trần / fromtimestamp(utc) ⇒ đỏ."""
    import calendar
    for label, utc_tuple, want_date, want_hm in (
            ("23:30 ICT", (2026, 10, 12, 16, 30, 0), "2026-10-12", "23:30"),
            ("00:30 ICT", (2026, 10, 12, 17, 30, 0), "2026-10-13", "00:30")):
        mtime = calendar.timegm(utc_tuple)
        for tz in ("UTC", "America/Los_Angeles", "Pacific/Kiritimati"):
            with tempfile.TemporaryDirectory() as td:
                gs_sandbox(td)
                st = Path(td) / "wc" / "deploy_golive_dt5g_v4" / "golive_state_today.json"
                st.write_text('{"published_at": "x", "as_of": "2026-10-12", "source": "DT4_only"}', encoding="utf-8")
                os.utime(st, (mtime, mtime))
                env = dict(os.environ, TZ=tz)
                env.pop("JOB_ID", None)
                subprocess.run([sys.executable, str(Path(td) / "mike" / "bin" / "gate_source_check.py"),
                                "--workdir", str(Path(td) / "wc"), "--since-epoch", "0", "--alert"],
                               capture_output=True, text=True, timeout=60, env=env)
                calls = gs_calls(td)
                nt = [c for c in calls if c[0] == "notify_thread.sh"]
                bus = [c for c in calls if c[0] == "append_event.sh"]
                msg = nt[0][1] if nt else ""
                check(f"gate-source neo ICT ({label}, TZ={tz}): tin ghi '({want_date} {want_hm} ICT)'",
                      f"CỔNG DT5G SUY GIẢM ({want_date} {want_hm} ICT)" in msg, extra=msg[:120])
                check(f"gate-source neo ICT ({label}, TZ={tz}): publish_date của dấu + topic bus = {want_date}",
                      (gs_marker(td) or {}).get("publish_date") == want_date
                      and bool(bus) and bus[0][3] == f"dt5g-gate-source-degraded-{want_date}",
                      extra=str(gs_marker(td)) + str(bus)[:200])


def case_gate_source_hung_channel_is_capped():
    """N3: kênh báo TREO ⇒ helper về trong trần (rút ngắn qua GATE_SOURCE_SEND_TIMEOUT_S), chuỗi chạy
    tiếp, kênh treo CHƯA bị đánh dấu, kênh kia vẫn gửi. Bỏ timeout ⇒ ca này đỏ."""
    import time
    with tempfile.TemporaryDirectory() as td:
        gs_sandbox(td)
        hung = Path(td) / "mike" / "bin" / "notify_thread.sh"
        hung.write_text('#!/usr/bin/env bash\nexec sleep 20\n', encoding="utf-8")
        hung.chmod(0o755)
        t0 = time.monotonic()
        out, _ = gs_run(td, "DT4_only", env_extra={"GATE_SOURCE_SEND_TIMEOUT_S": "1"})
        secs = time.monotonic() - t0
        check("gate-source kênh treo: helper về trong trần, chuỗi chạy tiếp",
              secs < 8 and "__END__ FAILED=0" in out and "thoát rc=" not in out, extra=f"{secs:.1f}s\n{out}")
        check("gate-source kênh treo: nêu lỗi thật TimeoutExpired, CHƯA đánh dấu discord, bus vẫn ghi",
              "gửi discord THẤT BẠI — Lỗi thật: TimeoutExpired" in out and _gs_sent(td, "DT4_only") == {"bus": True}
              and gs_count(td) == (0, 1, 0), extra=out + str(gs_marker(td)))
    sys.path.insert(0, str(_HERE))
    import gate_source_check as g
    check("gate-source trần gửi mặc định production = 60s (biến môi trường chỉ để test)",
          g.SEND_TIMEOUT_S == float(os.environ.get("GATE_SOURCE_SEND_TIMEOUT_S") or 60) and
          'os.environ.get("GATE_SOURCE_SEND_TIMEOUT_S") or 60' in GS_HELPER.read_text(encoding="utf-8"))


def case_gate_source_dedupe_is_per_date_source_pair():
    """N5: khoá chống lặp theo TỪNG CẶP (ngày publish, nguồn). DT4_only → LA_LUNG_v9 → DT4_only cùng
    ngày ⇒ 2 cặp = 2 tin + 2 bus; lượt thứ ba KHÔNG gửi lại (khoá một-ô cũ sẽ gửi lần ba)."""
    with tempfile.TemporaryDirectory() as td:
        gs_sandbox(td)
        gs_run(td, "DT4_only")
        gs_run(td, "LA_LUNG_v9")
        check("gate-source đổi nguồn cùng ngày: cặp mới ⇒ báo thêm 1 tin + 1 bus", gs_count(td) == (2, 2, 0),
              extra=str(gs_calls(td)))
        out, _ = gs_run(td, "DT4_only")
        check("gate-source quay lại nguồn đã báo cùng ngày: KHÔNG gửi lần ba", gs_count(td) == (2, 2, 0)
              and out.count("không gửi lại") == 2, extra=out + str(gs_calls(td)))
        m = gs_marker(td) or {}
        day = m.get("publish_date")
        check("gate-source dấu giữ cả hai cặp của ngày, bằng chứng theo lượt MỚI NHẤT",
              m.get("source") == "DT4_only" and m.get("sent") == {
                  f"{day}|DT4_only": {"discord": True, "bus": True},
                  f"{day}|LA_LUNG_v9": {"discord": True, "bus": True}}, extra=str(m))


if __name__ == "__main__":
    case_gate_source_mktemp_fails()
    case_gate_source_kill_cleans_tmp()
    case_gate_source_orphan_holding_stdout_does_not_hang()
    case_gate_source_marker_unwritable_still_alerts()
    case_gate_source_publish_time_is_ict_anchored()
    case_gate_source_hung_channel_is_capped()
    case_gate_source_dedupe_is_per_date_source_pair()
    case_gate_source_dt5g_macro_is_invisible()
    case_gate_source_dt4_only_alerts_once()
    case_gate_source_other_degraded_values()
    case_gate_source_evidence_missing_is_said_not_guessed()
    case_gate_source_publish_did_not_run_is_not_reported_twice()
    case_gate_source_failed_send_is_retried_not_marked()
    case_gate_source_recovered_rerun_and_helper_crash()
    case_query_fail_multiline_error()
    case_rc0_null_result_is_data_not_connection()
    case_real_staleness_still_blocks()
    case_fresh_ok_no_notify()
    case_warn_mode_query_fail_does_not_block()
    case_lastmod_show_fail_distinct_message()
    case_lastmod_missing_lastmodified_warns()
    case_pipeline0_exdate_forecast_runs_before_failed_gate()
    case_exdate_forecast_selfcheck_green()
    print(f"\nbq_freshness_check_selfcheck: {PASS} PASS, {FAIL} FAIL")
    sys.exit(1 if FAIL else 0)
