# -*- coding: utf-8 -*-
"""Regression self-check for the DT5G chain freshness fixes (audit Winston_20260710_173031,
fix job Winston_20260711_023903 — user-approved production change).

Incident recap: a 2026-06-21 reorg left vnindex_5state_ew_v1.py writing its outputs to
WORKDIR root while the daily chain (vnindex_5state_dual_v3.py) read data/ — the EW leg of
the blended base state silently froze at 2026-06-19 for 3 weeks, manufacturing a fake BULL
candidate that only a human caught on 2026-07-10. Every chain step still exited 0: nothing
verified that the files a step is EXPECTED to produce were actually (re)written this run.
A second, independent hole: bq_freshness_check.sh was "tightened" to MAX_STATE_LAG=1 on
07-10, but its gate compares with -le, so lag=1 (the exact case the tightening targeted —
DT5G one trading day behind, DollarBill planning on yesterday's state) still PASSED: the
tightening was a NO-OP. This selfcheck pins down all fixes:

  A. bq_freshness_check.sh — MAX_STATE_LAG now 0; the REAL _check() function (extracted
     from the script, run against a mocked `bq`) fails lag=1 and passes lag=0; regression
     proof that the old value 1 was a NO-OP under -le.
  B. writer/reader path consistency — ew_v1 writes BOTH outputs to data/; every active
     reader reads data/; no active reader still points at the quarantined root copies;
     daily_refresh mirrors root v3_4b -> data/ so build_dt_4gate.py's data/ input is
     refreshed nightly (the root write at build_v3_4_bull_aware.py:165 is INTENTIONAL —
     bq load reads root — and is deliberately left alone).
  C. assert_chain_outputs.sh mechanism — stale file => exit 1 (must DIE, not warn);
     missing file => exit 1; ALL files fresh => exit 0 (no false positive — this exact
     chain must self-run Mon 2026-07-13 18:30 ICT to publish the approved EW-leg fix,
     a false positive here would block that publish); boundary mtime == chain start
     counts as fresh; the file list is parsed from daily_refresh itself so the test
     exercises the real production list, not a copy.
  D. daily_refresh_v34b_linux.sh wiring — CHAIN_START_EPOCH captured after step [0];
     assertion step [8b] runs BEFORE backup/bq-load/publish (stale data can never reach
     BQ); failure path dies AND alerts; dt_4gate is advisory-only (research consumer,
     step [8] non-fatal by design — must not block the production publish path).

  E. macro_healthcheck runs BEFORE publish (2026-10-12, job Taylor_20261012_040247) — the
     healthcheck command sits immediately before the publish command, exactly ONCE (a second
     run would double the Telegram/MACRO_HEALTH_ALERT.md on every non-HEALTHY evening), is
     non-fatal and time-bounded; and the REAL block (extracted from the script, run in a
     sandbox with a stub interpreter) still reaches publish when the healthcheck exits
     1/2/127, is SIGKILLed, or hangs.

Run: python3 dt5g_chain_freshness_selfcheck.py   (exit 0 = all pass)
NOTE: never runs the real chain and never touches BQ — everything is sandboxed in tmp.
"""
import os
import re
import stat
import subprocess
import sys
import tempfile
import time

WC = "/home/trido/thanhdt/WorkingClaude"
FRESHNESS_SH = os.path.join(WC, "mike/bin/bq_freshness_check.sh")
ASSERT_SH = os.path.join(WC, "assert_chain_outputs.sh")
# Script nằm cạnh selfcheck này (ở canonical HERE == WC): chạy từ một worktree thì phải kiểm
# đúng bản của worktree đó, không phải bản đang chạy cron.
HERE = os.path.dirname(os.path.abspath(__file__))
REFRESH_SH = os.path.join(HERE, "daily_refresh_v34b_linux.sh")

fails = []


def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


# ═══════════════════════════════════════════════════════════════════════════
# A. bq_freshness_check.sh — threshold + REAL gate behavior under mocked bq
# ═══════════════════════════════════════════════════════════════════════════
print("\nA. bq_freshness_check.sh boundary (real _check(), mocked bq)")
fresh_src = read(FRESHNESS_SH)

m = re.search(r"^MAX_STATE_LAG=(\d+)", fresh_src, re.M)
check("A1 MAX_STATE_LAG tightened to 0", m is not None and m.group(1) == "0",
      f"found {m.group(1) if m else 'nothing'}")

# Extract the real _check() body so we test production code, not a re-implementation.
fm = re.search(r"^_check\(\) \{\n.*?^\}", fresh_src, re.M | re.S)
check("A2 _check() extractable from script", fm is not None)


def run_check_gate(fake_gap, max_lag):
    """Run the REAL _check() with a fake `bq` that reports gap_days=fake_gap."""
    with tempfile.TemporaryDirectory() as tmp:
        bindir = os.path.join(tmp, "bin"); os.makedirs(bindir)
        rootbin = os.path.join(tmp, "root", "bin"); os.makedirs(rootbin)
        with open(os.path.join(bindir, "bq"), "w") as f:
            f.write(f"#!/bin/bash\necho gap_days\necho {fake_gap}\n")
        for stub in ("notify.sh", "notify_thread.sh"):
            with open(os.path.join(rootbin, stub), "w") as f:
                f.write("#!/bin/bash\nexit 0\n")
        for p in (os.path.join(bindir, "bq"), os.path.join(rootbin, "notify.sh"),
                  os.path.join(rootbin, "notify_thread.sh")):
            os.chmod(p, os.stat(p).st_mode | stat.S_IEXEC)
        driver = os.path.join(tmp, "driver.sh")
        with open(driver, "w") as f:
            f.write("#!/bin/bash\n"
                    f'export PATH="{bindir}:$PATH"\n'
                    f'PROJECT=x; TODAY=t; NOW_ICT=n; DISCORD_STALE_CHANNEL=c; '
                    f'FAILED=0; QUIET=""; ROOT="{os.path.join(tmp, "root")}"\n'
                    f"source {os.path.join(tmp, 'check_fn.sh')}\n"
                    f'_check "test-table" "tav2_bq.fake" "time" {max_lag} "trading"\n'
                    "exit $?\n")
        with open(os.path.join(tmp, "check_fn.sh"), "w") as f:
            f.write(fm.group(0) + "\n")
        r = subprocess.run(["bash", driver], capture_output=True, text=True)
        return r.returncode


if fm:
    check("A3 lag=0 vs MAX=0 -> PASS (normal day must not be blocked)",
          run_check_gate(0, 0) == 0)
    check("A4 lag=1 vs MAX=0 -> FAIL (state 1 day behind now blocks DollarBill)",
          run_check_gate(1, 0) == 1)
    check("A5 regression proof: lag=1 vs old MAX=1 passed under -le (07-10 tighten was a NO-OP)",
          run_check_gate(1, 1) == 0)
    check("A6 lag=2 vs old MAX=1 would have failed (old setting only caught >=2)",
          run_check_gate(2, 1) == 1)

# ═══════════════════════════════════════════════════════════════════════════
# B. writer/reader path consistency (data/ is the single canonical location)
# ═══════════════════════════════════════════════════════════════════════════
print("\nB. writer/reader path consistency")
ew_src = read(os.path.join(WC, "vnindex_5state_ew_v1.py"))
check("B1 ew_v1 staging writer -> data/",
      'f"data/vnindex_5state_ew_staging{_OTAG}.csv"' in ew_src)
check("B2 ew_v1 diagnostics writer -> data/",
      'f"data/vnindex_5state_ew_full{_OTAG}.csv"' in ew_src)
check("B3 ew_v1 has NO remaining root write of either output",
      re.search(r'os\.path\.join\(WORKDIR, f?"vnindex_5state_ew_(full|staging)', ew_src) is None)

READERS = {  # active consumers verified in the 07-10 audit; each must read data/
    "vnindex_5state_dual_v3.py": "data/vnindex_5state_ew_full.csv",          # chain step [5] (bug gốc)
    "compare_ew_vs_live.py": "data/vnindex_5state_ew_staging.csv",
    "run_phase2_states.py": "data/vnindex_5state_ew_staging.csv",
    "ngu_hanh_shadow_tracker.py": "data/vnindex_5state_ew_full.csv",
    "vnindex_5state_dual_v1.py": "data/vnindex_5state_ew_full.csv",
    "sweep_ew_liq_threshold.py": 'f"data/vnindex_5state_ew_full{tag}.csv"',
    "mike/agents/Taylor/bull_commit_breadth_check.py": "data/vnindex_5state_ew_full.csv",
}
for rel, needle in READERS.items():
    src = read(os.path.join(WC, rel))
    has_data_path = needle in src
    # a root-path read = same filename reference NOT preceded by data/ inside a
    # read_csv/open/join call line (comments/docstrings excluded)
    root_read = False
    for line in src.splitlines():
        code = line.split("#", 1)[0]
        if "read_csv" not in code and "open(" not in code:
            continue
        if re.search(r'(?<!data/)(?<!_)vnindex_5state_ew_(full|staging)', code):
            root_read = True
    check(f"B4 {rel} reads data/ and has no root read", has_data_path and not root_read)

dt4_src = read(os.path.join(WC, "build_dt_4gate.py"))
refresh_src = read(REFRESH_SH)
check("B5 build_dt_4gate reads data/ v3_4b AND daily_refresh mirrors root -> data/ nightly",
      'data/vnindex_5state_tam_quan_v3_4b_full_history.csv' in dt4_src
      and re.search(r"^cp vnindex_5state_tam_quan_v3_4b_full_history\.csv "
                    r"data/vnindex_5state_tam_quan_v3_4b_full_history\.csv", refresh_src, re.M))
check("B6 daily_refresh bq load still reads ROOT v3_4b (intentional, untouched)",
      re.search(r'^CSV="vnindex_5state_tam_quan_v3_4b_full_history\.csv"', refresh_src, re.M) is not None)
check("B7 quarantined stale copies exist and live ONLY under data/_quarantine/",
      os.path.exists(os.path.join(WC, "data/_quarantine/vnindex_5state_ew_staging_FROZEN_20260619.csv"))
      and os.path.exists(os.path.join(WC, "data/_quarantine/vnindex_5state_ew_full_ROOT_ORPHAN_20260709.csv"))
      and not os.path.exists(os.path.join(WC, "vnindex_5state_ew_full.csv"))
      and not os.path.exists(os.path.join(WC, "vnindex_5state_ew_staging.csv")))

# ═══════════════════════════════════════════════════════════════════════════
# C. assert_chain_outputs.sh — mechanism (sandboxed, uses the REAL prod file list)
# ═══════════════════════════════════════════════════════════════════════════
print("\nC. assert_chain_outputs.sh mechanism")

lm = re.search(r"REQUIRED_OUTPUTS=\((.*?)^\)", refresh_src, re.S | re.M)
prod_files = re.findall(r"^\s*([\w./-]+\.csv)", lm.group(1), re.M) if lm else []
check("C1 REQUIRED_OUTPUTS parseable from daily_refresh, 10 files",
      len(prod_files) == 10, f"got {len(prod_files)}: {prod_files}")


def run_assert(tmp, start, files):
    return subprocess.run(["bash", ASSERT_SH, str(start)] + files,
                          cwd=tmp, capture_output=True, text=True)


with tempfile.TemporaryDirectory() as tmp:
    for rel in prod_files:
        os.makedirs(os.path.join(tmp, os.path.dirname(rel)) or tmp, exist_ok=True)
        with open(os.path.join(tmp, rel), "w") as f:
            f.write("time,state\n2026-07-10,3\n")
    now = int(os.stat(os.path.join(tmp, prod_files[0])).st_mtime)

    r = run_assert(tmp, now - 5, prod_files)
    check("C2 ALL fresh -> exit 0 (no false positive — Monday publish must not be blocked)",
          r.returncode == 0, r.stdout.strip().splitlines()[-1] if r.stdout else r.stderr)

    r = run_assert(tmp, now, prod_files)
    check("C3 boundary mtime == chain start -> still fresh (>= semantics)", r.returncode == 0)

    stale_one = prod_files[1]
    os.utime(os.path.join(tmp, stale_one), (now - 86400 * 21, now - 86400 * 21))  # frozen 3 tuần
    r = run_assert(tmp, now - 5, prod_files)
    check("C4 ONE stale file -> exit 1 and named as STALE (the 3-week EW freeze signature)",
          r.returncode == 1 and f"STALE:   {stale_one}" in r.stdout, r.stdout.strip())

    os.remove(os.path.join(tmp, stale_one))
    r = run_assert(tmp, now - 5, prod_files)
    check("C5 MISSING file -> exit 1 and named as MISSING",
          r.returncode == 1 and f"MISSING: {stale_one}" in r.stdout)

    r = run_assert(tmp, "not-a-number", prod_files)
    check("C6 garbage start_epoch -> exit 1 (never silently passes)", r.returncode == 1)

    r = subprocess.run(["bash", ASSERT_SH, str(now)], capture_output=True, text=True)
    check("C7 no files given -> usage error exit 1", r.returncode == 1)

# ═══════════════════════════════════════════════════════════════════════════
# D. daily_refresh wiring — assertion placed before any BQ publish, dies + alerts
# ═══════════════════════════════════════════════════════════════════════════
print("\nD. daily_refresh_v34b_linux.sh wiring")
lines = refresh_src.splitlines()


def line_of(pattern):
    for i, ln in enumerate(lines):
        if re.search(pattern, ln):
            return i
    return -1


l_step0 = line_of(r'step "\[0\]')
l_epoch = line_of(r'^CHAIN_START_EPOCH="\$\(date \+%s\)"')
l_step1 = line_of(r'step "\[1\]')
l_assert = line_of(r'step "\[8b\]')
l_backup = line_of(r'step "\[9\]')
l_bqload = line_of(r'step "\[10\]')
l_invoke = line_of(r'\./assert_chain_outputs\.sh "\$CHAIN_START_EPOCH" "\$\{REQUIRED_OUTPUTS\[@\]\}"')

check("D1 CHAIN_START_EPOCH captured after step [0], before step [1]",
      0 <= l_step0 < l_epoch < l_step1, f"lines {l_step0}/{l_epoch}/{l_step1}")
check("D2 assertion invoked with CHAIN_START_EPOCH + REQUIRED_OUTPUTS", l_invoke > 0)
check("D3 assertion step [8b] runs BEFORE backup [9] and bq load [10] — stale never publishes",
      0 < l_assert < l_backup < l_bqload, f"lines {l_assert}/{l_backup}/{l_bqload}")
blk = "\n".join(lines[l_assert:l_backup]) if 0 < l_assert < l_backup else ""
check("D4 REQUIRED failure path dies (not warn) AND alerts via notify.sh + notify_thread.sh",
      'die "post-chain freshness assertion FAILED' in blk
      and "notify.sh" in blk and "notify_thread.sh" in blk)
check("D5 dt_4gate checked as ADVISORY (alert, no die) — research-only, must not block publish",
      "data/vnindex_5state_dt_4gate.csv" in blk
      and "data/vnindex_5state_dt_4gate.csv" not in (lm.group(1) if lm else ""))
check("D6 bash syntax of both scripts still valid",
      subprocess.run(["bash", "-n", REFRESH_SH]).returncode == 0
      and subprocess.run(["bash", "-n", ASSERT_SH]).returncode == 0)

# ═══════════════════════════════════════════════════════════════════════════
# E. macro_healthcheck BEFORE publish — order (static) + non-blocking (sandboxed real block)
# ═══════════════════════════════════════════════════════════════════════════
print("\nE. macro_healthcheck runs before publish_gated_state, and never blocks it")
HC_CMD = r'\$PY\s+(\S*/)?macro_healthcheck\.py\b'
PUB_CMD = r'\$PY\s+(\S*/)?publish_gated_state\.py\b'


def cmd_lines(pattern):
    """Chỉ dòng LỆNH: bỏ comment và nhãn `step "..."` (nhãn có nhắc tên file .py)."""
    return [i for i, ln in enumerate(lines)
            if re.search(pattern, ln) and not re.match(r'\s*(#|step\s)', ln)]


hc_ls, pub_ls = cmd_lines(HC_CMD), cmd_lines(PUB_CMD)
step_ls = [i for i, ln in enumerate(lines) if re.match(r'step\s+"', ln)]
check("E1 exactly ONE macro_healthcheck invocation (2 lượt = nhân đôi Telegram tối không HEALTHY)",
      len(hc_ls) == 1, f"lines {[i + 1 for i in hc_ls]}")
check("E2 exactly ONE publish_gated_state invocation", len(pub_ls) == 1,
      f"lines {[i + 1 for i in pub_ls]}")
e_ok = len(hc_ls) == 1 and len(pub_ls) == 1
l_hc, l_pub = (hc_ls[0], pub_ls[0]) if e_ok else (-1, -1)
check("E3 healthcheck command stands BEFORE publish command", e_ok and l_hc < l_pub,
      f"healthcheck line {l_hc + 1}, publish line {l_pub + 1}")
hc_step = max([i for i in step_ls if i < l_hc], default=-1) if e_ok else -1
pub_step = max([i for i in step_ls if i < l_pub], default=-1) if e_ok else -1
after_pub = min([i for i in step_ls if i > l_pub], default=-1) if e_ok else -1
e4_ok = (e_ok and 0 <= hc_step < pub_step
         and [i for i in step_ls if hc_step < i <= pub_step] == [pub_step]
         and 0 <= line_of(r'step "\[11b\]') < hc_step)
check("E4 healthcheck step is the step IMMEDIATELY before the publish step (after sync [11]/[11b])",
      e4_ok, f"step lines {hc_step + 1}/{pub_step + 1}")
hc_blk = "\n".join(lines[hc_step:pub_step]) if 0 <= hc_step < pub_step else ""
hc_code = "\n".join(ln for ln in hc_blk.splitlines() if not ln.lstrip().startswith("#"))
_tm = re.search(r'\btimeout\s+-k\s+(\d+)\s+(\d+)\s+[^|\n]*' + HC_CMD + r'\s*\|\|', lines[l_hc]) if e_ok else None
_k, _n = (int(_tm.group(1)), int(_tm.group(2))) if _tm else (-1, -1)
check("E5 healthcheck is NON-FATAL (`||` guard, no die/exit in its step) and TIME-BOUNDED "
      "(`timeout -k K N`, K>=1 so KILL always follows, 60<=N<=600: không tắt/không đụng chuỗi 19:00/không giết healthcheck sống)",
      e_ok and _tm is not None and _k >= 1 and 60 <= _n <= 600
      and not re.search(r'\b(die|exit)\b', hc_code), f"-k {_k} {_n}")
set_ls = [ln for ln in lines if re.match(r'set\s+[-+]', ln)]
check("E6 script does not enable errexit (`set -e` would turn healthcheck rc!=0 into an abort)",
      len(set_ls) == 1 and not re.search(r'\s-[a-zA-Z]*e', set_ls[0]), f"{set_ls}")

# E7: chạy KHỐI THẬT [healthcheck step → hết publish step] trong sandbox. $PY là stub ghi lại
# thứ tự gọi; notify*.sh (đường dẫn tuyệt đối trong khối) bị trỏ sang stub — còn sót đường dẫn
# thật thì KHÔNG chạy (không bao giờ bắn notify thật từ selfcheck). Ba lớp chặn lệnh THẬT lọt
# vào sandbox nếu sau này khối bị sửa: (1) chỉ chạy khi E4 đạt — khối đúng 2 step healthcheck +
# publish, không kẹp step nào khác (bq load / restate guard…); (2) PATH kín = stub + /usr/bin:/bin
# (bq/gcloud nằm ngoài đó); (3) stub `bq`/`gcloud` đứng đầu PATH.
STUB_PY = """#!/usr/bin/env bash
echo "$1" >> "$CALLS"
case "$1" in
  *macro_healthcheck.py)
    case "$HC_MODE" in
      rc0|rc1|rc2) mkdir -p data; : > data/macro_health.json; sleep 1.2; exit "${HC_MODE#rc}" ;;
      crash1|crash2) exit "${HC_MODE#crash}" ;;
      rc*)  exit "${HC_MODE#rc}" ;;
      kill) kill -9 $$ ;;
      hang) exec sleep 20 ;;
    esac ;;
esac
exit 0
"""
# Shim CHỈ rút ngắn thời lượng (để ca treo không chờ đủ trần thật); dạng gọi khác
# `timeout -k N N cmd…` ⇒ shim exit 99 ⇒ stub healthcheck không được gọi ⇒ E7 đỏ.
STUB_TIMEOUT = """#!/usr/bin/env bash
[ "$1" = "-k" ] || exit 99
shift 3
exec "$REAL_TIMEOUT" -k 1 2 "$@"
"""
blk_e = "\n".join(lines[hc_step:after_pub]) if e4_ok and l_pub < after_pub else ""
with tempfile.TemporaryDirectory() as sbx:
    sbin = os.path.join(sbx, "bin")
    os.makedirs(sbin)
    blk_run = blk_e.replace(WC + "/mike/bin/", sbin + "/")
    safe = bool(blk_e) and "/home/" not in blk_run.replace(sbx, "")
    check("E7a real healthcheck→publish block extracted (needs E4); no real absolute path left after stubbing",
          safe, f"{len(blk_e.splitlines())} lines")

    def put(path, body):
        with open(path, "w", encoding="utf-8") as f:
            f.write(body)
        os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR)

    real_timeout = subprocess.run(["bash", "-c", "command -v timeout"],
                                  capture_output=True, text=True).stdout.strip()
    put(os.path.join(sbin, "stubpy"), STUB_PY)
    put(os.path.join(sbin, "timeout"), STUB_TIMEOUT)
    for nm in ("notify.sh", "notify_thread.sh", "bq", "gcloud"):
        put(os.path.join(sbin, nm), '#!/usr/bin/env bash\necho "$0" >> "$CALLS"\n[ -n "${NOTIFY_HANG:-}" ] && exec sleep 15\n[ -n "${NOTIFY_FAIL:-}" ] && exit 1\nexit 0\n')
    harness = os.path.join(sbx, "harness.sh")
    put(harness, "\n".join([
        "#!/usr/bin/env bash",
        set_ls[0] if set_ls else "set -uo pipefail",     # đúng dòng `set` của script thật
        f'PY="{sbin}/stubpy"; LOG="{sbx}/refresh.log"; WORKDIR_8L="{sbx}"',
        'step() { echo "--- $* ---"; }',
        'die() { echo "!!! ABORT: $*"; exit 1; }',
        'mkdir -p "$PWD/data"; touch -d "1 day ago" "$PWD/data/macro_health.json"',   # production LUÔN có JSON cũ
        blk_run,
        "echo CHAIN_CONTINUED",
        "",
    ]))

    def run_block(mode, notify_fail=False, notify_hang=False):
        calls = os.path.join(sbx, f"calls_{mode}{'_nf' if notify_fail else ''}{'_nh' if notify_hang else ''}.log")
        env = dict(os.environ, PATH=sbin + os.pathsep + "/usr/bin:/bin",
                   CALLS=calls, HC_MODE=mode, REAL_TIMEOUT=real_timeout)
        if notify_fail:
            env["NOTIFY_FAIL"] = "1"
        if notify_hang:
            env["NOTIFY_HANG"] = "1"
        t0 = time.monotonic()
        r = subprocess.run(["bash", harness], cwd=sbx, env=env, capture_output=True,
                           text=True, timeout=120)
        got = [os.path.basename(c) for c in read(calls).split()] if os.path.exists(calls) else []
        return r, got, time.monotonic() - t0

    HC, PUB = "macro_healthcheck.py", "publish_gated_state.py"
    NTF = ["notify.sh", "notify_thread.sh"]
    # (mode, nhãn, notify?, nhãn bắt buộc, nhãn cấm)
    modes = (("rc0", "HEALTHY rc=0", False, None, None),
             ("rc1", "DEGRADED rc=1", False, "DEGRADED", "FAILED"),
             ("rc2", "FAILED rc=2", False, "FAILED", "DEGRADED"),
             ("crash1", "rc=1 nhưng JSON KHÔNG làm mới (Python crash)", True, "LỖI CHẠY", "DEGRADED"),
             ("crash2", "rc=2 nhưng JSON KHÔNG làm mới (thiếu script)", True, "LỖI CHẠY", "FAILED"),
             ("rc124", "rc=124", True, "TIMEOUT", "DEGRADED"),
             ("rc137", "rc=137", True, "TIMEOUT", "DEGRADED"),
             ("rc127", "interpreter/script hỏng rc=127", True, "LỖI CHẠY", "TIMEOUT"),
             ("kill", "bị SIGKILL", True, "TIMEOUT", "DEGRADED"),
             ("hang", "TREO, timeout cắt", True, "TIMEOUT", "DEGRADED"))
    for mode, label, notif, must, banned in modes:
        if not (safe and real_timeout):
            check(f"E7 [{label}] publish still runs", False, "block not runnable / no timeout binary")
            continue
        want = [HC] + (NTF if notif else []) + [PUB]
        for nf in ((False, True) if notif else (False,)):
            r, got, dt = run_block(mode, nf)
            tag = f"{label}{' + notify TỰ LỖI' if nf else ''}"
            check(f"E7 [{tag}] healthcheck first, publish STILL runs, chain continues; "
                  f"notify {'đúng 1 lần (notify.sh+notify_thread.sh)' if notif else '0 lần'}",
                  got == want and "CHAIN_CONTINUED" in r.stdout and r.returncode == 0 and dt < 10,
                  f"calls={got} rc={r.returncode} {dt:.1f}s")
        if notif and mode in ("rc124", "crash1"):
            r, got, dt = run_block(mode, notify_hang=True)
            check(f"E7 [{label} + notify TREO] publish VẪN chạy trong trần thời gian (notify bọc timeout), chain continues",
                  got == [HC] + NTF + [PUB] and "CHAIN_CONTINUED" in r.stdout and r.returncode == 0 and dt < 10,
                  f"calls={got} rc={r.returncode} {dt:.1f}s")
        if mode != "rc0":
            r, got, dt = run_block(mode)
            warn = re.findall(r"WARN: macro_healthcheck[^\n]*rc=[1-9][0-9]*", r.stdout)
            check(f"E7 [{label}] failure is LOGGED with its rc, label '{must}' (not '{banned}')",
                  bool(warn) and must in warn[0] and banned not in warn[0],
                  (warn or ["<no WARN line>"])[0][:90])

print()
if fails:
    print(f"FAILED {len(fails)} check(s): {fails}")
    sys.exit(1)
print("ALL CHECKS PASSED — freshness gate now blocks 1-day-stale DT5G, all chain outputs "
      "write/read a single canonical data/ path, and the post-chain mtime assertion dies "
      "loudly BEFORE publishing if any expected output is missing or stale.")
sys.exit(0)
