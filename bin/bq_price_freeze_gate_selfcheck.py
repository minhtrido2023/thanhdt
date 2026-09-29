#!/usr/bin/env python3
"""Selfcheck cho _check_price_freeze() trong bin/bq_freshness_check.sh (job Taylor_20260927_103434).

Test CHÍNH file thật: hàm được TRÍCH ra bằng sed từ bin/bq_freshness_check.sh mỗi lần chạy,
không phải bản copy — nên mutation test có nghĩa (sửa file thật ⇒ test phải chết).

`bq`, `notify.sh`, `notify_thread.sh` đều bị chặn bằng stub trong sandbox /tmp: selfcheck này
KHÔNG tra BQ và KHÔNG gửi Discord/Telegram. Query SQL thật đã được smoke riêng (xem REPORT.md).

Chạy:
  $DNA_PYEXE bin/bq_price_freeze_gate_selfcheck.py            # 10 case × 4 môi trường TZ
  $DNA_PYEXE bin/bq_price_freeze_gate_selfcheck.py --mutations # + 10 mutation
  $DNA_PYEXE bin/bq_price_freeze_gate_selfcheck.py --all
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, "bq_freshness_check.sh")

# 4 môi trường: ICT (đúng), UTC, một múi giờ ÂM (qua ngày ngược chiều), và TZ bị GỠ HẲN.
# §16: selfcheck thừa hưởng TZ đúng của tác giả thì pass bất kể code sai — phải chạy cả biến thể.
TZ_ENVS = [
    ("ICT", {"TZ": "Asia/Ho_Chi_Minh"}),
    ("UTC", {"TZ": "UTC"}),
    ("NY", {"TZ": "America/New_York"}),
    ("no-TZ", {"__unset_TZ__": "1"}),
]

HARNESS = r"""
set -uo pipefail
PROJECT="proj-test"
ROOT="__SANDBOX__"
WC_ROOT="__SANDBOX__"
TODAY="2026-09-27"
NOW_ICT="19:00 ICT"
QUIET="__QUIET__"
FAILED=0
WARNED=0
DISCORD_STALE_CHANNEL="trading_daily"
export PATH="__SANDBOX__/stub:$PATH"
source __FUNCFILE__
_check_price_freeze
rc=$?
echo "___RC=${rc}___FAILED=${FAILED}___WARNED=${WARNED}___"
"""

BQ_STUB = r"""#!/usr/bin/env bash
# stub `bq` — trả canned CSV từ __SANDBOX__/bq_out, exit code từ __SANDBOX__/bq_rc
cat "__SANDBOX__/bq_out"
exit "$(cat "__SANDBOX__/bq_rc")"
"""

NOTIFY_STUB = r"""#!/usr/bin/env bash
printf '%s\n' "__KIND__|$1" >> "__SANDBOX__/notify_log"
"""


def extract_func(src_text):
    """Trích khối MAX_PRICE_FLAT_PCT=... đến hết hàm _check_price_freeze."""
    m = re.search(
        r"^MAX_PRICE_FLAT_PCT=.*?^_check_price_freeze\(\) \{.*?^\}$",
        src_text,
        re.S | re.M,
    )
    if not m:
        raise SystemExit(
            "FATAL: không trích được _check_price_freeze() từ bq_freshness_check.sh — "
            "hàm đã bị đổi tên/đổi cấu trúc? Selfcheck KHÔNG kết luận 'pass'."
        )
    return m.group(0)


def run_case(func_text, bq_out, bq_rc, tz_env, quiet=""):
    sb = tempfile.mkdtemp(prefix="pfgate_")
    try:
        os.makedirs(os.path.join(sb, "stub"), exist_ok=True)
        os.makedirs(os.path.join(sb, "bin"), exist_ok=True)
        funcfile = os.path.join(sb, "func.sh")
        with open(funcfile, "w", encoding="utf-8") as fh:
            fh.write(func_text + "\n")
        with open(os.path.join(sb, "bq_out"), "w", encoding="utf-8") as fh:
            fh.write(bq_out)
        with open(os.path.join(sb, "bq_rc"), "w", encoding="utf-8") as fh:
            fh.write(str(bq_rc))
        bqp = os.path.join(sb, "stub", "bq")
        with open(bqp, "w", encoding="utf-8") as fh:
            fh.write(BQ_STUB.replace("__SANDBOX__", sb))
        os.chmod(bqp, 0o755)
        for kind in ("notify.sh", "notify_thread.sh"):
            p = os.path.join(sb, "bin", kind)
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(NOTIFY_STUB.replace("__SANDBOX__", sb).replace("__KIND__", kind))
            os.chmod(p, 0o755)
        script = (
            HARNESS.replace("__SANDBOX__", sb)
            .replace("__FUNCFILE__", funcfile)
            .replace("__QUIET__", quiet)
        )
        env = dict(os.environ)
        env.pop("TZ", None)
        for k, v in tz_env.items():
            if k != "__unset_TZ__":
                env[k] = v
        out = subprocess.run(
            ["bash", "-c", script], capture_output=True, text=True, env=env, timeout=60
        )
        nlog = ""
        nlp = os.path.join(sb, "notify_log")
        if os.path.exists(nlp):
            nlog = open(nlp, encoding="utf-8").read()
        mm = re.search(r"___RC=(\d+)___FAILED=(\d+)___WARNED=(\d+)___", out.stdout)
        if not mm:
            return dict(rc=None, failed=None, warned=None, stdout=out.stdout,
                        stderr=out.stderr, notify=nlog)
        return dict(rc=int(mm.group(1)), failed=int(mm.group(2)),
                    warned=int(mm.group(3)), stdout=out.stdout, stderr=out.stderr,
                    notify=nlog)
    finally:
        shutil.rmtree(sb, ignore_errors=True)


def csv(n_tot, n_flat, n_cm, n_both, d="2026-09-25", dprev="2026-09-24"):
    return f"n_tot,n_flat,n_cm,n_both,d,dprev\n{n_tot},{n_flat},{n_cm},{n_both},{d},{dprev}\n"


# (tên, bq_out, bq_rc, danh sách assertion (mô tả, hàm(res)->bool))
def build_cases():
    C = []

    # 1. Phiên bình thường — số THẬT đo từ ticker_prune 2026-09-25 (31/209, both-flat 31).
    C.append(("normal-2026-09-25", csv(209, 31, 0, 31), 0, [
        ("không chặn", lambda r: r["failed"] == 0),
        ("không WARN", lambda r: r["warned"] == 0),
        ("không gửi notify nào", lambda r: r["notify"].strip() == ""),
        ("in OK kèm số thật 31/209", lambda r: "OK" in r["stdout"] and "31/209" in r["stdout"]),
    ]))

    # 2. Replay 2026-01-30 THẬT (256 mã, 254 Price phẳng, 222 trong đó Close vẫn đổi).
    C.append(("replay-2026-01-30-price-only-freeze", csv(256, 254, 222, 32), 0, [
        ("KHÔNG chặn (Close còn đúng)", lambda r: r["failed"] == 0),
        ("đếm 1 WARN", lambda r: r["warned"] == 1),
        ("chỉ gửi Discord, KHÔNG Telegram", lambda r:
            "notify_thread.sh|" in r["notify"] and "notify.sh|" not in r["notify"]),
        ("§29 trích bằng chứng 254/256", lambda r: "254/256" in r["notify"]),
        ("§29 trích bit phân biệt 222/254", lambda r: "222/254" in r["notify"]),
        ("nói rõ không phải phiên nghỉ", lambda r: "KHÔNG phải phiên nghỉ" in r["notify"]),
    ]))

    # 3. Replay 2025-02-03 THẬT (258/258 phẳng, 234 Close đổi) — phiên đầu sau Tết.
    C.append(("replay-2025-02-03-total-price-freeze", csv(258, 258, 234, 24), 0, [
        ("KHÔNG chặn", lambda r: r["failed"] == 0),
        ("đếm 1 WARN", lambda r: r["warned"] == 1),
        ("trích 258/258", lambda r: "258/258" in r["notify"]),
    ]))

    # 4. Replay 2018-01-24 THẬT (221 mã, 175 Price phẳng, chỉ 1 mã Close đổi ⇒ 174 both-flat).
    C.append(("replay-2018-01-24-whole-row-frozen", csv(221, 175, 1, 174), 0, [
        ("CHẶN pipeline", lambda r: r["failed"] == 1),
        ("rc=1", lambda r: r["rc"] == 1),
        ("gửi CẢ Telegram và Discord", lambda r:
            "notify.sh|" in r["notify"] and "notify_thread.sh|" in r["notify"]),
        ("trích 174/221", lambda r: "174/221" in r["notify"]),
    ]))

    # 5-6. Biên ngưỡng 50%: đúng 50% ⇒ OK (dùng -gt), 51% ⇒ kêu.
    C.append(("boundary-exactly-50pct", csv(200, 100, 95, 5), 0, [
        ("50% KHÔNG kêu", lambda r: r["failed"] == 0 and r["warned"] == 0),
    ]))
    C.append(("boundary-51pct-price-only", csv(200, 102, 100, 2), 0, [
        ("51% kêu WARN", lambda r: r["warned"] == 1 and r["failed"] == 0),
    ]))
    # both-flat ĐÚNG 50% (không phải 2% như case trên) — case duy nhất giết được -gt→-ge
    # trên nhánh both-flat; thiếu nó, mutation bothflat-gt->ge SỐNG SÓT (đã đo thật).
    C.append(("boundary-bothflat-exactly-50pct", csv(200, 100, 0, 100), 0, [
        ("50% both-flat KHÔNG chặn", lambda r: r["failed"] == 0),
        ("50% both-flat KHÔNG WARN", lambda r: r["warned"] == 0),
    ]))
    C.append(("boundary-51pct-both-flat", csv(200, 110, 8, 102), 0, [
        ("51% both-flat ⇒ CHẶN", lambda r: r["failed"] == 1),
    ]))

    # 7. Mẫu quá nhỏ ⇒ nói thẳng không kết luận, KHÔNG báo động (fail-safe theo yêu cầu).
    C.append(("sample-too-small", csv(40, 40, 38, 2), 0, [
        ("không chặn", lambda r: r["failed"] == 0),
        ("không WARN", lambda r: r["warned"] == 0),
        ("không notify", lambda r: r["notify"].strip() == ""),
        ("nói rõ KHÔNG đủ dữ liệu", lambda r: "KHÔNG đủ dữ liệu" in r["stdout"]),
        ("không nói 'OK'/sạch", lambda r: "OK " not in r["stdout"]),
    ]))

    # 8. bq chết (rc!=0) — §29: phải in LỖI THẬT bq trả, và KHÔNG được coi là dữ liệu sạch.
    C.append(("bq-connection-error", "BigQuery error in query operation: Access Denied: "
              "Project proj-test: User does not have bigquery.jobs.create permission.\n", 1, [
        ("không chặn pipeline", lambda r: r["failed"] == 0),
        ("đếm 1 WARN", lambda r: r["warned"] == 1),
        ("trích lỗi thật của bq", lambda r: "Access Denied" in r["notify"]),
        ("quy đúng nguyên nhân auth/quota/network", lambda r: "auth/quota/network" in r["notify"]),
        ("nói rõ KHÔNG PHẢI kết luận sạch", lambda r: "KHÔNG PHẢI kết luận" in r["notify"]),
    ]))

    # 9. bq rc=0 nhưng output rác (bảng rỗng / đổi schema) — nguyên nhân KHÁC case 8, §28.
    C.append(("bq-ok-but-garbage-row", "n_tot,n_flat,n_cm,n_both,d,dprev\n,,,,,\n", 0, [
        ("đếm 1 WARN", lambda r: r["warned"] == 1),
        ("không chặn", lambda r: r["failed"] == 0),
        ("KHÔNG quy cho auth", lambda r: "auth/quota/network" not in r["notify"]),
        ("quy đúng rỗng/đổi schema", lambda r: "đổi schema" in r["notify"]),
    ]))

    # 10. n_flat=0 — guard chia cho 0 khi tính % Close-đổi trên tổng mã phẳng.
    C.append(("zero-flat-no-divide-by-zero", csv(200, 0, 0, 0), 0, [
        ("không chặn/WARN", lambda r: r["failed"] == 0 and r["warned"] == 0),
        ("không có lỗi division by 0", lambda r: "division by 0" not in r["stderr"]),
        ("stderr sạch", lambda r: r["stderr"].strip() == ""),
    ]))
    return C


MUTATIONS = [
    ("thr-50->95", lambda t: t.replace("MAX_PRICE_FLAT_PCT=50", "MAX_PRICE_FLAT_PCT=95", 1)),
    ("min-sample-50->5", lambda t: t.replace("MIN_FLAT_SAMPLE=50", "MIN_FLAT_SAMPLE=5", 1)),
    ("bothflat-gt->ge", lambda t: t.replace(
        '[ "$pct_both" -gt "$MAX_PRICE_FLAT_PCT" ]', '[ "$pct_both" -ge "$MAX_PRICE_FLAT_PCT" ]', 1)),
    ("priceflat-gt->ge", lambda t: t.replace(
        '[ "$pct_flat" -gt "$MAX_PRICE_FLAT_PCT" ]', '[ "$pct_flat" -ge "$MAX_PRICE_FLAT_PCT" ]', 1)),
    ("drop-FAILED=1", lambda t: t.replace("    FAILED=1\n    return 1", "    return 1", 1)),
    ("bothflat-uses-nflat", lambda t: t.replace(
        "pct_both=$(( n_both * 100 / n_tot ))", "pct_both=$(( n_flat * 100 / n_tot ))", 1)),
    ("priceflat-uses-nboth", lambda t: t.replace(
        "pct_flat=$(( n_flat * 100 / n_tot ))", "pct_flat=$(( n_both * 100 / n_tot ))", 1)),
    ("small-sample-lt->gt", lambda t: t.replace(
        '[ "$n_tot" -lt "$MIN_FLAT_SAMPLE" ]', '[ "$n_tot" -gt "$MIN_FLAT_SAMPLE" ]', 1)),
    ("rc-ne->eq", lambda t: t.replace("if [ $rc -ne 0 ] || !", "if [ $rc -eq 0 ] || !", 1)),
    ("drop-div-guard", lambda t: t.replace(
        '[ "$n_flat" -gt 0 ] && pct_cm_of_flat=$(( n_cm * 100 / n_flat ))',
        'pct_cm_of_flat=$(( n_cm * 100 / n_flat ))', 1)),
    ("drop-bq-fail-WARN", lambda t: t.replace(
        "    WARNED=$((WARNED + 1))\n    return 0\n  fi\n\n  IFS=,",
        "    return 0\n  fi\n\n  IFS=,", 1)),
    ("regex-accept-anything", lambda t: t.replace(
        "grep -qE '^[0-9]+,[0-9]+,[0-9]+,[0-9]+,[0-9-]+,[0-9-]+$'", "grep -qE '.*'", 1)),
]


def run_suite(func_text, tz_envs, verbose=True):
    cases = build_cases()
    n_assert = 0
    fails = []
    for tzname, tzenv in tz_envs:
        for name, bq_out, bq_rc, asserts in cases:
            res = run_case(func_text, bq_out, bq_rc, tzenv)
            if res["rc"] is None:
                fails.append(f"[{tzname}] {name}: harness không chạy được — "
                             f"stdout={res['stdout'][:200]!r} stderr={res['stderr'][:300]!r}")
                n_assert += len(asserts)
                continue
            for desc, fn in asserts:
                n_assert += 1
                try:
                    ok = fn(res)
                except Exception as exc:  # assertion tự lỗi = fail, không im lặng
                    ok = False
                    desc = f"{desc} (assertion lỗi: {exc})"
                if not ok:
                    fails.append(
                        f"[{tzname}] {name}: {desc} — "
                        f"rc={res['rc']} FAILED={res['failed']} WARNED={res['warned']} "
                        f"stdout={res['stdout'].strip()[:180]!r} notify={res['notify'].strip()[:180]!r}"
                    )
    if verbose:
        for f in fails:
            print("  FAIL " + f)
    return n_assert, fails


def main():
    args = sys.argv[1:]
    do_mut = "--mutations" in args or "--all" in args
    src = open(TARGET, encoding="utf-8").read()
    func_text = extract_func(src)
    print(f"target : {TARGET}")
    print(f"trích  : {len(func_text.splitlines())} dòng (_check_price_freeze + 2 ngưỡng)")
    print(f"môi trường TZ: {[t[0] for t in TZ_ENVS]}")

    n_assert, fails = run_suite(func_text, TZ_ENVS)
    print(f"\nBASE: {n_assert} assertion, {len(fails)} fail")
    rc = 1 if fails else 0

    if do_mut:
        print(f"\nMUTATION ({len(MUTATIONS)} đột biến trên CHÍNH hàm thật):")
        killed = 0
        survived = []
        for mname, mfn in MUTATIONS:
            mutated = mfn(func_text)
            if mutated == func_text:
                survived.append(f"{mname} (KHÔNG áp được — pattern không khớp code hiện tại)")
                continue
            _, mfails = run_suite(mutated, TZ_ENVS[:1], verbose=False)
            if mfails:
                killed += 1
                print(f"  killed   {mname}  ({len(mfails)} assertion chết)")
            else:
                survived.append(mname)
                print(f"  SURVIVED {mname}")
        print(f"\nMUTATION: {killed}/{len(MUTATIONS)} bị giết")
        if survived:
            print("  sống sót: " + "; ".join(survived))
            rc = 1

    print("\n" + ("PASS" if rc == 0 else "FAIL"))
    return rc


if __name__ == "__main__":
    sys.exit(main())
