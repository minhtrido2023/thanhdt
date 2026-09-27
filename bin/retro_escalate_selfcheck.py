#!/usr/bin/env python3
"""Selfcheck cho bug ack-topic-counter (`bin/retro_escalate.py` + bước 6 `daily_retro.sh`).

Bất biến CHÍNH cần ghim (arch-review 2026-09-25, required_change #2):
  «escalation CÙNG pattern ở ngày N+1 (bộ đếm tăng) VẪN được ack hiện có phủ»

Cách chứng minh KHÔNG dùng lời hứa: mọi ca chạy CHÍNH khối CHECK5 thật của
`bin/ops_health_check.sh` (qua harness `ops_health_check_selfcheck.run_check5`) trên cùng
một bus fixture mà `retro_escalate.decide()` đọc. Hai bên phải ra CÙNG một phán quyết
"đã ack / chưa ack" — nếu ai đó sửa `_acked()` mà quên `is_acked()` (hoặc ngược lại),
ca CONSIST ở dưới ĐỎ ngay.

Ca RED control (case_red_control_old_counter_shape) dựng lại HÌNH THÁI CŨ — ack trên
`…-2days`, câu hỏi ngày sau `…-3days` — và assert code THẬT vẫn escalate nó. Đó là bằng
chứng bug có thật và test này phân biệt được cũ/mới, không phải test luôn xanh.

Chạy: python3 bin/retro_escalate_selfcheck.py     (thêm `env -u TZ` khi kiểm lớp TZ)
"""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys

BIN = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BIN)
sys.path.insert(0, BIN)

FAILS = []


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


RE = _load("retro_escalate", os.path.join(BIN, "retro_escalate.py"))
H = _load("ops_health_check_selfcheck", os.path.join(BIN, "ops_health_check_selfcheck.py"))

STABLE = RE.TOPIC_PREFIX + "foo-bar"


def check(name, cond, detail=""):
    if cond:
        print(f"  PASS  {name}")
    else:
        FAILS.append(f"{name} — {detail}")
        print(f"  FAIL  {name} — {detail}")


def _lines_for(lines, needle):
    return [ln for ln in lines if needle in ln]


def _check5_verdict(root, topic):
    """(acked_theo_check5, escalated_theo_check5) — đọc từ OUTPUT của code thật."""
    lines, _ = H.run_check5(root)
    acked = any(topic in ln for ln in _lines_for(lines, "ĐÃ TRIAGE, chờ NGƯỜI quyết"))
    esc = any(topic in ln for ln in _lines_for(lines, "CHƯA thấy answer tương ứng"))
    return acked, esc, H.joined(lines)


def _mk(events_by_agent):
    root, inbox = H.mkbus()
    for agent, evs in events_by_agent.items():
        H.write_events(os.path.join(inbox, f"{agent}.jsonl"), evs)
    return root


# ── Ca 1: hằng số ack không được trôi khỏi ops_health_check.sh ──────────────────────
def case_constants_in_sync():
    src = open(os.path.join(BIN, "ops_health_check.sh"), encoding="utf-8").read()
    m1 = re.search(r'^ACK_PREFIX\s*=\s*"([^"]+)"', src, re.M)
    m2 = re.search(r'^ACK_MAX_SUPPRESS_DAYS\s*=\s*(\d+)', src, re.M)
    check("ops_health_check.sh còn khai ACK_PREFIX/ACK_MAX_SUPPRESS_DAYS ở cột 0",
          bool(m1 and m2), "không tìm thấy — selfcheck mất khả năng so hằng số")
    if m1:
        check("ACK_PREFIX khớp giữa retro_escalate.py và ops_health_check.sh",
              RE.ACK_PREFIX == m1.group(1), f"{RE.ACK_PREFIX!r} vs {m1.group(1)!r}")
    if m2:
        check("ACK_MAX_SUPPRESS_DAYS khớp",
              RE.ACK_MAX_SUPPRESS_DAYS == int(m2.group(1)),
              f"{RE.ACK_MAX_SUPPRESS_DAYS} vs {m2.group(1)}")


# ── Ca 2: bộ đếm KHÔNG thể lọt vào topic, dù caller cố nhét ─────────────────────────
def case_counter_never_reaches_topic():
    variants = ["foo-bar", "foo-bar-2days", "foo-bar-3days", "foo-bar-1day",
                "foo-bar-3retros", "foo-bar-4", "foo-bar_5", "foo-bar-2days-3",
                RE.TOPIC_PREFIX + "foo-bar-6days"]
    got = {v: RE.stable_topic(v) for v in variants}
    check("mọi biến thể có bộ đếm đều chuẩn hoá về ĐÚNG MỘT topic ổn định",
          set(got.values()) == {STABLE}, json.dumps(got, ensure_ascii=False))
    check("số NẰM GIỮA slug không bị cắt (chỉ cắt đuôi)",
          RE.stable_topic("tdays-holiday-2days-consumer")
          == RE.TOPIC_PREFIX + "tdays-holiday-2days-consumer",
          RE.stable_topic("tdays-holiday-2days-consumer"))
    try:
        RE.stable_topic("3days")
        check("slug chỉ có bộ đếm phải FAIL LOUD, không sinh topic rỗng", False,
              "không raise")
    except SystemExit:
        check("slug chỉ có bộ đếm phải FAIL LOUD, không sinh topic rỗng", True)


# ── Ca 3 (BẤT BIẾN CHÍNH): ngày N+1 vẫn được ack ngày N phủ ─────────────────────────
def case_day_n_plus_1_still_covered():
    root = _mk({
        "Mike": [H.ev("Mike", "question", STABLE, H.ago(1))],
        "Wags": [H.ev("Wags", "status", f"{RE.ACK_PREFIX}Mike/{STABLE}", H.ago(0, 12),
                      {"suppress_days": 7})],
    })
    try:
        decision, reason = RE.decide(STABLE, root)
        check("ngày N+1: decide() = SKIP (không mở câu hỏi thứ hai cho cùng pattern)",
              decision == "SKIP", f"{decision} — {reason}")
        acked, esc, out = _check5_verdict(root, STABLE)
        check("ngày N+1: ops_health_check THẬT xếp vào 'ĐÃ TRIAGE, chờ NGƯỜI quyết'",
              acked, out)
        check("ngày N+1: ops_health_check THẬT KHÔNG escalate (không đốt job wags_autofix)",
              not esc, out)
        check("CONSIST ca 3: is_acked() của retro_escalate trùng phán quyết CHECK5",
              (decision == "SKIP") == acked, f"decide={decision} check5_acked={acked}")
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 4 (RED control): hình thái CŨ — bộ đếm trong topic — VẪN escalate ────────────
def case_red_control_old_counter_shape():
    old_d2 = RE.TOPIC_PREFIX + "foo-bar-2days"
    old_d3 = RE.TOPIC_PREFIX + "foo-bar-3days"
    root = _mk({
        "Mike": [H.ev("Mike", "question", old_d2, H.ago(1, 12)),
                 H.ev("Mike", "question", old_d3, H.ago(0, 12))],
        "Wags": [H.ev("Wags", "status", f"{RE.ACK_PREFIX}Mike/{old_d2}", H.ago(1),
                      {"suppress_days": 7})],
    })
    try:
        acked2, esc2, out = _check5_verdict(root, old_d2)
        acked3, esc3, _ = _check5_verdict(root, old_d3)
        check("RED control: ack ngày 2 phủ ĐÚNG topic ngày 2", acked2 and not esc2, out)
        check("RED control: topic ngày 3 (bộ đếm tăng) KHÔNG được phủ ⇒ VẪN escalate "
              "— đây chính là bug ack-topic-counter", esc3 and not acked3, out)
        check("bản MỚI diệt được ca này: 2 topic cũ chuẩn hoá về cùng một topic",
              RE.stable_topic(old_d2) == RE.stable_topic(old_d3) == STABLE,
              f"{RE.stable_topic(old_d2)} vs {RE.stable_topic(old_d3)}")
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 5: ack HẾT cửa sổ ⇒ escalate lại (không phải tắt vĩnh viễn) ──────────────────
def case_expired_ack_reescalates():
    root = _mk({
        "Mike": [H.ev("Mike", "question", STABLE, H.ago(1))],
        "Wags": [H.ev("Wags", "status", f"{RE.ACK_PREFIX}Mike/{STABLE}", H.ago(5),
                      {"suppress_days": 1})],
    })
    try:
        decision, reason = RE.decide(STABLE, root)
        acked, esc, out = _check5_verdict(root, STABLE)
        check("ack hết hạn: decide() = POST", decision == "POST", f"{decision} — {reason}")
        check("ack hết hạn: CHECK5 thật cũng escalate lại", esc and not acked, out)
        check("CONSIST ca 5: hai bên cùng phán quyết", (decision == "SKIP") == acked,
              f"decide={decision} check5_acked={acked}")
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 6: chưa từng escalate ⇒ POST (không im lặng nuốt pattern mới) ────────────────
def case_first_time_posts():
    root = _mk({"Mike": [H.ev("Mike", "question", "chuyen-khac", H.ago(1))]})
    try:
        decision, _ = RE.decide(STABLE, root)
        check("pattern lần đầu: decide() = POST", decision == "POST", decision)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 7: ack sd=0 (không khai suppress_days) vẫn phủ đúng instance đã có ───────────
def case_ack_sd0_covers_existing_instance():
    root = _mk({
        "Mike": [H.ev("Mike", "question", STABLE, H.ago(1))],
        "Wags": [H.ev("Wags", "status", f"{RE.ACK_PREFIX}Mike/{STABLE}", H.ago(0, 12))],
    })
    try:
        decision, _ = RE.decide(STABLE, root)
        acked, esc, out = _check5_verdict(root, STABLE)
        check("ack sd=0: decide() = SKIP", decision == "SKIP", decision)
        check("ack sd=0: CHECK5 thật cũng coi là đã triage", acked and not esc, out)
        check("CONSIST ca 7: hai bên cùng phán quyết", (decision == "SKIP") == acked,
              f"decide={decision} check5_acked={acked}")
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 7b: MIGRATION — câu hỏi LEGACY còn bộ đếm, đã được ack, không bị mở lại ──────
#    Đây là hình thái THẬT trên bus lúc bản vá land (`…-fpt-vendor-backfill-2days` +
#    ack sd=7 ngày 09-25). Không có ca này thì ngày đầu sau khi land mở thêm 1 câu hỏi
#    trùng nội dung cho MỖI pattern đang treo.
def case_legacy_counter_question_still_recognised():
    legacy = RE.TOPIC_PREFIX + "foo-bar-2days"
    root = _mk({
        "Mike": [H.ev("Mike", "question", legacy, H.ago(1))],
        "Wags": [H.ev("Wags", "status", f"{RE.ACK_PREFIX}Mike/{legacy}", H.ago(0, 12),
                      {"suppress_days": 7})],
    })
    try:
        decision, reason = RE.decide(STABLE, root)
        check("migration: câu hỏi LEGACY (bộ đếm) đã ack ⇒ decide() = SKIP, không mở trùng",
              decision == "SKIP", f"{decision} — {reason}")
        acked, esc, out = _check5_verdict(root, legacy)
        check("migration: CHECK5 thật cũng thấy câu hỏi legacy đó đang được ack phủ",
              acked and not esc, out)
        check("CONSIST ca 7b: hai bên cùng phán quyết", (decision == "SKIP") == acked,
              f"decide={decision} check5_acked={acked}")
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 7c: pattern KHÁC có tiền tố trùng một phần KHÔNG được coi là cùng pattern ────
def case_different_pattern_not_collapsed():
    other = RE.TOPIC_PREFIX + "foo-bar-baz"
    root = _mk({
        "Mike": [H.ev("Mike", "question", other, H.ago(1))],
        "Wags": [H.ev("Wags", "status", f"{RE.ACK_PREFIX}Mike/{other}", H.ago(0, 12),
                      {"suppress_days": 7})],
    })
    try:
        decision, _ = RE.decide(STABLE, root)
        check("pattern khác (chỉ trùng tiền tố) KHÔNG làm tắt escalation của pattern này",
              decision == "POST", decision)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 8: CLI --dry-run đọc đúng bus fixture và KHÔNG ghi gì ────────────────────────
def case_cli_dry_run_writes_nothing():
    root = _mk({
        "Mike": [H.ev("Mike", "question", STABLE, H.ago(1))],
        "Wags": [H.ev("Wags", "status", f"{RE.ACK_PREFIX}Mike/{STABLE}", H.ago(0, 12),
                      {"suppress_days": 7})],
    })
    inbox = os.path.join(root, "mike", "bus", "inbox")
    before = {p: os.path.getsize(os.path.join(inbox, p)) for p in os.listdir(inbox)}
    try:
        r = subprocess.run(
            [sys.executable, "-B", os.path.join(BIN, "retro_escalate.py"),
             "--pattern", "foo-bar-9days", "--days", "9", "--dry-run",
             "--bus-root", root],
            capture_output=True, text=True,
            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        check("CLI rc=0", r.returncode == 0, r.stderr)
        check(f"CLI in TOPIC ổn định ({STABLE})", f"TOPIC={STABLE}" in r.stdout, r.stdout)
        check("CLI in DECISION=SKIP", "DECISION=SKIP" in r.stdout, r.stdout)
        after = {p: os.path.getsize(os.path.join(inbox, p)) for p in os.listdir(inbox)}
        check("--dry-run KHÔNG ghi thêm byte nào vào bus", before == after,
              f"{before} → {after}")
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 9: daily_retro.sh bước 6 phải ĐI QUA helper, không gọi append_event.sh thô ───
def case_daily_retro_wired():
    src = open(os.path.join(BIN, "daily_retro.sh"), encoding="utf-8").read()
    check("daily_retro.sh bước 6 trỏ vào bin/retro_escalate.py",
          "retro_escalate.py" in src, "prompt retro chưa được wire — fix chỉ là code chết")
    bad = re.findall(r"retro-pattern-recurring-<[^>]*>-days", src)
    check("daily_retro.sh KHÔNG còn ra lệnh nhúng bộ đếm vào topic",
          not bad, f"còn: {bad}")


def main():
    print("== retro_escalate selfcheck (bug ack-topic-counter) ==")
    for fn in (case_constants_in_sync, case_counter_never_reaches_topic,
               case_day_n_plus_1_still_covered, case_red_control_old_counter_shape,
               case_expired_ack_reescalates, case_first_time_posts,
               case_ack_sd0_covers_existing_instance,
               case_legacy_counter_question_still_recognised,
               case_different_pattern_not_collapsed, case_cli_dry_run_writes_nothing,
               case_daily_retro_wired):
        print(f"\n-- {fn.__name__}")
        fn()
    print()
    if FAILS:
        print(f"❌ {len(FAILS)} assertion ĐỎ:")
        for f in FAILS:
            print(f"   - {f}")
        return 1
    print("✅ toàn bộ assertion PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
