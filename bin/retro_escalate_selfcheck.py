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

VÒNG 2 (arch-review NEEDS_CHANGES vòng 1): bổ sung các ca GIẾT 5 mutation từng sống sót
— ack topic KHÁC hẳn / ack dạng topic TRẦN / clamp ACK_MAX_SUPPRESS_DAYS / ts hỏng /
event nằm trong `bus/inbox/archive/*.jsonl.gz` — cộng ca chống FALSE-COLLAPSE (2 slug mô
tả khác nhau KHÔNG được gộp thành 1 topic), ca resolver, ca fail-loud khi thiếu bus, và
2 ca chạy CODE THẬT của `daily_retro.sh` + `append_event.sh`.

Chạy: python3 bin/retro_escalate_selfcheck.py     (thêm `env -u TZ` khi kiểm lớp TZ)
"""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

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


def _check5_verdict(root, topic):
    """(acked_theo_check5, escalated_theo_check5, output) — đọc từ OUTPUT của code thật."""
    lines, _ = H.run_check5(root)
    acked = any(topic in ln for ln in lines if "ĐÃ TRIAGE, chờ NGƯỜI quyết" in ln)
    esc = any(topic in ln for ln in lines if "CHƯA thấy answer tương ứng" in ln)
    return acked, esc, H.joined(lines)


def _mk(events_by_agent, archive=None):
    root, inbox = H.mkbus()
    for agent, evs in events_by_agent.items():
        H.write_events(os.path.join(inbox, f"{agent}.jsonl"), evs)
    for name, evs in (archive or {}).items():
        H.write_events(os.path.join(inbox, "archive", f"{name}.jsonl.gz"), evs, gz=True)
    return root


def _consist(label, decision, acked):
    check(f"CONSIST {label}: is_acked() của retro_escalate trùng phán quyết CHECK5",
          (decision == "SKIP") == acked, f"decide={decision} check5_acked={acked}")


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


# ── Ca 2: slug mang bộ đếm bị TỪ CHỐI (không tự cắt) ────────────────────────────────
#    Vòng 1 CẮT đuôi đếm ⇒ 2 slug mô tả khác nhau gộp thành 1 topic (false-collapse).
#    Vòng 2: từ chối, fail-loud. Danh sách phủ CẢ dạng dính lẫn dạng có gạch.
def case_counter_slug_is_rejected():
    rejected = ["foo-bar-2days", "foo-bar-3days", "foo-bar-1day", "foo-bar-3retros",
                "foo-bar-4", "foo-bar_5", "foo-bar-2-days", "foo-bar-5-days",
                "2-days", "3days", "foo-bar-0001743768",
                RE.TOPIC_PREFIX + "foo-bar-6days", RE.TOPIC_PREFIX + "2-days"]
    bad = []
    for v in rejected:
        try:
            bad.append(f"{v} → {RE.stable_topic(v)}")
        except SystemExit:
            pass
    check("mọi slug kết thúc bằng số đều bị TỪ CHỐI (không tự cắt ⇒ không false-collapse)",
          not bad, f"lọt: {bad}")
    check("slug sạch vẫn dùng được",
          RE.stable_topic("foo-bar") == STABLE
          and RE.stable_topic(RE.TOPIC_PREFIX + "foo-bar") == STABLE,
          RE.stable_topic("foo-bar"))
    check("số NẰM GIỮA slug không sao (chỉ đuôi mới bị chặn)",
          RE.stable_topic("tdays-holiday-2days-consumer")
          == RE.TOPIC_PREFIX + "tdays-holiday-2days-consumer", "")


# ── Ca 2b (KILLER vòng 1): 2 pattern KHÁC nhau không bao giờ gộp làm một ────────────
#    Ca thật arch-reviewer dựng: 2 account tiền thật 0001743767 / 0001743768.
def case_no_false_collapse_between_patterns():
    a = RE.TOPIC_PREFIX + "plan-t1-not-ready-acct0001743767"
    b = RE.TOPIC_PREFIX + "plan-t1-not-ready-acct0001743768"
    check("2 slug mô tả khác nhau ⇒ 2 topic khác nhau", a != b, "")
    check("_same_pattern KHÔNG coi pattern account 767 là cùng pattern với 768",
          not RE._same_pattern(a, b) and not RE._same_pattern(b, a), "")
    root = _mk({
        "Mike": [H.ev("Mike", "question", a, H.ago(1))],
        "Wags": [H.ev("Wags", "status", f"{RE.ACK_PREFIX}Mike/{a}", H.ago(0, 12),
                      {"suppress_days": 14})],
    })
    try:
        decision, reason = RE.decide(b, root)
        check("ack của pattern 767 KHÔNG nuốt im lặng escalation của pattern 768",
              decision == "POST", f"{decision} — {reason}")
    finally:
        shutil.rmtree(root, ignore_errors=True)


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
        _consist("ca 3", decision, acked)
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
        check("bản MỚI diệt ca này: cả 2 topic cũ đều thuộc CÙNG pattern ổn định",
              RE._same_pattern(old_d2, STABLE) and RE._same_pattern(old_d3, STABLE), "")
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
        _consist("ca 5", decision, acked)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 5b: suppress_days vượt trần phải bị CLAMP về ACK_MAX_SUPPRESS_DAYS ───────────
def case_suppress_days_clamped():
    root = _mk({
        "Mike": [H.ev("Mike", "question", STABLE, H.ago(1))],
        "Wags": [H.ev("Wags", "status", f"{RE.ACK_PREFIX}Mike/{STABLE}", H.ago(20),
                      {"suppress_days": 99})],
    })
    try:
        decision, reason = RE.decide(STABLE, root)
        acked, esc, out = _check5_verdict(root, STABLE)
        check(f"ack sd=99 đăng 20 ngày trước: bị clamp về {RE.ACK_MAX_SUPPRESS_DAYS}d "
              "⇒ hết hạn ⇒ POST", decision == "POST", f"{decision} — {reason}")
        check("CHECK5 thật cũng coi là hết hạn", esc and not acked, out)
        _consist("ca 5b", decision, acked)
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
        _consist("ca 7", decision, acked)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 7a: ack sd=0 KHÔNG được khoá pattern VĨNH VIỄN ───────────────────────────────
#    `_acked` coi ack sd=0 là vĩnh viễn cho ĐÚNG instance — đúng cho "không dispatch lại
#    câu hỏi CŨ", nhưng dùng nó để chặn escalate LẦN TÁI DIỄN MỚI thì 1 ack khoá cả
#    pattern mãi mãi (arch-review vòng 1 tái lập được với ack 39 ngày tuổi).
def case_ack_sd0_has_escape_hatch():
    root = _mk({
        "Mike": [H.ev("Mike", "question", STABLE, H.ago(39))],
        "Wags": [H.ev("Wags", "status", f"{RE.ACK_PREFIX}Mike/{STABLE}", H.ago(38))],
    })
    try:
        decision, reason = RE.decide(STABLE, root)
        check(f"câu hỏi acked 39 ngày tuổi (> trần {RE.ACK_MAX_SUPPRESS_DAYS}d): POST",
              decision == "POST", f"{decision} — {reason}")
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 7b: MIGRATION — câu hỏi LEGACY còn bộ đếm, đã ack, không bị mở lại ───────────
#    Dùng ĐÚNG các dạng topic CÓ THẬT trên bus, gồm cả dạng có gạch `-2-days`.
def case_legacy_counter_question_still_recognised():
    for legacy_suffix in ("-2days", "-2-days", "-3retros"):
        legacy = STABLE + legacy_suffix
        root = _mk({
            "Mike": [H.ev("Mike", "question", legacy, H.ago(1))],
            "Wags": [H.ev("Wags", "status", f"{RE.ACK_PREFIX}Mike/{legacy}", H.ago(0, 12),
                          {"suppress_days": 7})],
        })
        try:
            decision, reason = RE.decide(STABLE, root)
            check(f"migration '{legacy_suffix}': đã ack ⇒ SKIP, không mở trùng",
                  decision == "SKIP", f"{decision} — {reason}")
            acked, esc, out = _check5_verdict(root, legacy)
            check(f"migration '{legacy_suffix}': CHECK5 thật cũng thấy đang được ack phủ",
                  acked and not esc, out)
            _consist(f"ca 7b{legacy_suffix}", decision, acked)
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


# ── Ca 7d: ack của topic HOÀN TOÀN KHÁC không được phủ ──────────────────────────────
#    Mutation "bỏ hẳn khớp topic trong is_acked" từng SỐNG vì không fixture nào có ack
#    lạ. Bus thật LUÔN có ack dạng `triaged-needs-human: selfcheck-red: …` sd=14 tươi.
def case_unrelated_ack_does_not_cover():
    root = _mk({
        "Mike": [H.ev("Mike", "question", STABLE, H.ago(1))],
        "Wags": [H.ev("Wags", "status",
                      f"{RE.ACK_PREFIX} selfcheck-red: bq_freshness_check_selfcheck.py",
                      H.ago(0, 6), {"suppress_days": 14})],
    })
    try:
        decision, reason = RE.decide(STABLE, root)
        acked, esc, out = _check5_verdict(root, STABLE)
        check("ack của topic KHÁC HẲN (selfcheck-red) KHÔNG phủ escalation retro ⇒ POST",
              decision == "POST", f"{decision} — {reason}")
        check("CHECK5 thật cũng escalate", esc and not acked, out)
        _consist("ca 7d", decision, acked)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 7e: ack dạng topic TRẦN (không 'Agent/') vẫn phải phủ ────────────────────────
def case_ack_bare_topic_form_covers():
    root = _mk({
        "Mike": [H.ev("Mike", "question", STABLE, H.ago(1))],
        "Wags": [H.ev("Wags", "status", f"{RE.ACK_PREFIX}{STABLE}", H.ago(0, 12),
                      {"suppress_days": 7})],
    })
    try:
        decision, _ = RE.decide(STABLE, root)
        acked, esc, out = _check5_verdict(root, STABLE)
        check("ack dạng topic trần (không 'Agent/') vẫn phủ ⇒ SKIP", decision == "SKIP", "")
        check("CHECK5 thật cũng coi là đã triage", acked and not esc, out)
        _consist("ca 7e", decision, acked)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 7f: ts hỏng ⇒ fail-closed (ack không đọc được ts thì KHÔNG tắt escalate) ─────
def case_corrupt_ts_is_fail_closed():
    root = _mk({
        "Mike": [H.ev("Mike", "question", STABLE, H.ago(1))],
        "Wags": [H.ev("Wags", "status", f"{RE.ACK_PREFIX}Mike/{STABLE}", "khong-phai-ngay",
                      {"suppress_days": 7})],
    })
    try:
        decision, reason = RE.decide(STABLE, root)
        acked, esc, out = _check5_verdict(root, STABLE)
        check("ack có ts HỎNG không được tắt escalate (fail-closed) ⇒ POST",
              decision == "POST", f"{decision} — {reason}")
        check("CHECK5 thật cũng fail-closed", esc and not acked, out)
        _consist("ca 7f", decision, acked)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 7g: event nằm trong bus/inbox/archive/*.jsonl.gz vẫn phải được đọc ───────────
def case_archive_gz_is_read():
    root = _mk(
        {"Taylor": [H.ev("Taylor", "question", "chuyen-khac", H.ago(1))]},
        archive={"Mike_2026-09": [
            H.ev("Mike", "question", STABLE, H.ago(1)),
            H.ev("Mike", "status", f"{RE.ACK_PREFIX}Mike/{STABLE}", H.ago(0, 12),
                 {"suppress_days": 7})]})
    try:
        decision, reason = RE.decide(STABLE, root)
        acked, esc, out = _check5_verdict(root, STABLE)
        check("câu hỏi + ack nằm trong archive .jsonl.gz vẫn được đọc ⇒ SKIP",
              decision == "SKIP", f"{decision} — {reason}")
        check("CHECK5 thật cũng đọc được archive", acked and not esc, out)
        _consist("ca 7g", decision, acked)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 7h: câu hỏi ĐÃ CÓ answer/decision không được dùng làm căn cứ SKIP ────────────
def case_resolved_question_is_not_basis_for_skip():
    root = _mk({
        "Mike": [H.ev("Mike", "question", STABLE, H.ago(2)),
                 H.ev("Mike", "answer", STABLE, H.ago(1, 12))],
        "Wags": [H.ev("Wags", "status", f"{RE.ACK_PREFIX}Mike/{STABLE}", H.ago(1),
                      {"suppress_days": 7})],
    })
    try:
        decision, reason = RE.decide(STABLE, root)
        check("câu hỏi cũ ĐÃ có answer ⇒ lần tái diễn mới phải POST, không SKIP",
              decision == "POST", f"{decision} — {reason}")
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 7i: tra cứu bus THẤT BẠI phải FAIL LOUD, không kết luận 'chưa có câu hỏi' ────
def case_missing_bus_fails_loud():
    d = tempfile.mkdtemp(prefix="retro_esc_nobus_")
    try:
        try:
            RE.decide(STABLE, d)
            check("thiếu bus/inbox ⇒ FAIL LOUD (không lặng lẽ POST)", False, "không raise")
        except SystemExit as e:
            check("thiếu bus/inbox ⇒ FAIL LOUD (không lặng lẽ POST)",
                  "KHÔNG tìm thấy thư mục bus" in str(e), str(e))
        r = subprocess.run(
            [sys.executable, "-B", os.path.join(BIN, "retro_escalate.py"),
             "--pattern", "foo-bar", "--days", "2", "--dry-run", "--bus-root", d],
            capture_output=True, text=True,
            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        check("CLI rc != 0 khi bus-root sai", r.returncode != 0, r.stdout + r.stderr)
    finally:
        shutil.rmtree(d, ignore_errors=True)


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
             "--pattern", "foo-bar", "--days", "9", "--dry-run", "--bus-root", root],
            capture_output=True, text=True,
            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        check("CLI rc=0", r.returncode == 0, r.stderr)
        check(f"CLI in TOPIC ổn định ({STABLE})", f"TOPIC={STABLE}" in r.stdout, r.stdout)
        check("CLI in DECISION=SKIP", "DECISION=SKIP" in r.stdout, r.stdout)
        after = {p: os.path.getsize(os.path.join(inbox, p)) for p in os.listdir(inbox)}
        check("--dry-run KHÔNG ghi thêm byte nào vào bus", before == after,
              f"{before} → {after}")
        r2 = subprocess.run(
            [sys.executable, "-B", os.path.join(BIN, "retro_escalate.py"),
             "--pattern", "foo-bar-9days", "--days", "9", "--dry-run", "--bus-root", root],
            capture_output=True, text=True,
            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        check("CLI TỪ CHỐI --pattern mang bộ đếm (rc!=0, nói rõ lý do)",
              r2.returncode != 0 and "kết thúc bằng một CON SỐ" in (r2.stdout + r2.stderr),
              r2.stdout + r2.stderr)
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


# ── Ca 9b: guard chống-trùng của daily_retro phải THẤY nhánh SKIP (event status) ────
#    Chạy CHÍNH khối python trong daily_retro.sh (extract-and-test), không đọc chuỗi.
def case_daily_retro_guard_sees_skip_status():
    src = open(os.path.join(BIN, "daily_retro.sh"), encoding="utf-8").read()
    m = re.search(r"\npath, since = sys\.argv\[1\], sys\.argv\[2\]\n(.*?)\nPY\n", src, re.S)
    if not m:
        check("trích được khối guard chống-trùng trong daily_retro.sh", False,
              "không tìm thấy khối `path, since = sys.argv…` — selfcheck mất hiệu lực")
        return
    check("trích được khối guard chống-trùng trong daily_retro.sh", True)
    code = "import json, sys\npath, since = sys.argv[1], sys.argv[2]\n" + m.group(1)
    d = tempfile.mkdtemp(prefix="retro_guard_")
    try:
        f = os.path.join(d, "Mike.jsonl")
        H.write_events(f, [
            H.ev("Mike", "status", f"{RE.SKIP_STATUS_PREFIX}{STABLE}", H.ago(0, 1)),
            H.ev("Mike", "status", "chuyen-khac-khong-lien-quan", H.ago(0, 1)),
        ])
        r = subprocess.run([sys.executable, "-c", code, f, H.ago(1)],
                           capture_output=True, text=True)
        check("guard THẤY nhánh SKIP (status retro-pattern-recurring-update:…)",
              STABLE in r.stdout, r.stdout + r.stderr)
        check("guard KHÔNG nhặt status không liên quan",
              "chuyen-khac-khong-lien-quan" not in r.stdout, r.stdout)
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── Ca 10: chốt CƠ KHÍ ở append_event.sh — chạy SCRIPT THẬT trong sandbox ───────────
def case_append_event_guard_is_mechanical():
    d = tempfile.mkdtemp(prefix="retro_ae_")
    try:
        os.symlink(BIN, os.path.join(d, "bin"))
        ae = os.path.join(d, "bin", "append_event.sh")
        env = dict(os.environ, JOB_ID="")
        bad = subprocess.run(
            [ae, "Mike", "question", RE.TOPIC_PREFIX + "foo-bar-3days", '{"a":1}'],
            capture_output=True, text=True, env=env)
        check("append_event.sh CHẶN question mang bộ đếm (rc!=0)",
              bad.returncode != 0, bad.stdout + bad.stderr)
        check("thông điệp chặn trỏ đúng sang retro_escalate.py",
              "retro_escalate.py" in (bad.stdout + bad.stderr), bad.stdout + bad.stderr)
        for suf in ("-2-days", "-3retros", "-4", "-3x", "-3d", "-2ngay"):
            v = subprocess.run([ae, "Mike", "question", RE.TOPIC_PREFIX + "foo-bar" + suf,
                                '{"a":1}'], capture_output=True, text=True, env=env)
            check(f"append_event.sh chặn biến thể '{suf}'", v.returncode != 0,
                  v.stdout + v.stderr)
        ok = subprocess.run([ae, "Mike", "question", STABLE, '{"a":1}'],
                            capture_output=True, text=True, env=env)
        check("append_event.sh CHO QUA topic ổn định (đối chứng — guard không chặn bừa)",
              ok.returncode == 0, ok.stdout + ok.stderr)
        other = subprocess.run([ae, "Mike", "question", "nav-xcheck-spacex-2days",
                                '{"a":1}'], capture_output=True, text=True, env=env)
        check("guard KHÔNG đụng topic ngoài tiền tố retro (đối chứng phạm vi)",
              other.returncode == 0, other.stdout + other.stderr)
        fnd = subprocess.run([ae, "Mike", "finding",
                              RE.TOPIC_PREFIX + "foo-bar-3days", '{"a":1}'],
                             capture_output=True, text=True, env=env)
        check("guard chỉ áp cho event_type=question (finding vẫn qua)",
              fnd.returncode == 0, fnd.stdout + fnd.stderr)
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── Ca 2c: ví dụ trong THÔNG ĐIỆP TỪ CHỐI phải tự nó qua được stable_topic ──────────
#    arch-review vòng 2 (killer): thông điệp gợi ý đúng cái tên vừa bị từ chối ⇒ phiên
#    retro làm theo hướng dẫn lặp vô hạn và tưởng pattern này không escalate được.
def case_reject_message_example_is_actually_valid():
    try:
        got = RE.stable_topic(RE._REJECT_EXAMPLE)
        check("ví dụ trong thông điệp từ chối TỰ NÓ qua được stable_topic()", True, got)
    except SystemExit as e:
        check("ví dụ trong thông điệp từ chối TỰ NÓ qua được stable_topic()", False, str(e))
    try:
        RE.stable_topic("plan-t1-not-ready-0001743768")
        msg = ""
    except SystemExit as e:
        msg = str(e)
    check("thông điệp từ chối có in ví dụ hợp lệ ra cho người đọc",
          RE._REJECT_EXAMPLE in msg, msg)
    # Mọi tên được GỢI Ý (sau chữ "vd ") phải tự nó qua được — chống việc sửa ví dụ sau
    # này thành một tên lại bị từ chối. Chuỗi bị TỪ CHỐI cũng nằm trong thông điệp (echo
    # lại input), nên chỉ soi phần gợi ý, không soi mọi chuỗi trong nháy.
    sugg = re.findall(r"vd '([^']+)'", msg)
    check("thông điệp từ chối có ít nhất 1 tên GỢI Ý", bool(sugg), msg)
    for cand in sugg:
        try:
            RE.stable_topic(cand)
            ok = True
        except SystemExit:
            ok = False
        check(f"chuỗi ví dụ {cand!r} trong thông điệp lỗi phải hợp lệ", ok, msg)


# ── Ca 2d: đơn vị đếm còn sót ở vòng 2 (`-3d`, `-3lần`) nay cũng bị từ chối ─────────
def case_extra_counter_units_rejected():
    lot = []
    for v in ["foo-bar-3d", "foo-bar-3lần", "foo-bar-2ngay", "foo-bar-3x", "foo-bar-2times"]:
        try:
            lot.append(f"{v} → {RE.stable_topic(v)}")
        except SystemExit:
            pass
    check("các đơn vị đếm bổ sung (d / lần / ngay / x / times) đều bị TỪ CHỐI",
          not lot, f"lọt: {lot}")


# ── Ca 5c: ack `window` (sd>0) còn hiệu lực KHÔNG bị đường thoát đè ─────────────────
#    arch-review vòng 2: đo đường thoát bằng tuổi CÂU HỎI thì ack sd=14 mới 1 ngày cũng
#    bị đè. Đúng ngưỡng là tuổi của ACK, và chỉ áp cho ack `permanent`.
def case_fresh_window_ack_not_overridden_by_escape():
    root = _mk({
        "Mike": [H.ev("Mike", "question", STABLE, H.ago(20))],
        "Wags": [H.ev("Wags", "status", f"{RE.ACK_PREFIX}Mike/{STABLE}", H.ago(1),
                      {"suppress_days": 14})],
    })
    try:
        decision, reason = RE.decide(STABLE, root)
        check("câu hỏi 20 ngày tuổi nhưng ack sd=14 MỚI 1 ngày ⇒ vẫn SKIP",
              decision == "SKIP", f"{decision} — {reason}")
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 5d: đường thoát đo bằng tuổi ACK (permanent), không phải tuổi câu hỏi ────────
def case_escape_hatch_measures_ack_age():
    root = _mk({
        "Mike": [H.ev("Mike", "question", STABLE, H.ago(40))],
        "Wags": [H.ev("Wags", "status", f"{RE.ACK_PREFIX}Mike/{STABLE}", H.ago(1))],
    })
    try:
        decision, reason = RE.decide(STABLE, root)
        check("ack permanent MỚI 1 ngày (câu hỏi 40 ngày) ⇒ SKIP, đo theo tuổi ACK",
              decision == "SKIP", f"{decision} — {reason}")
        check("lý do KHÔNG viện dẫn tuổi câu hỏi", "40 ngày tuổi" not in reason, reason)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 7j: legacy ĐÃ ack (cũ) + câu hỏi ổn định CHƯA ack (mới) ⇒ phải POST ──────────
#    Hình thái CÓ THẬT trong giai đoạn migrate. Chọn nhầm câu hỏi CŨ ⇒ SKIP im lặng.
def case_newest_question_wins():
    legacy = STABLE + "-2days"
    root = _mk({
        "Mike": [H.ev("Mike", "question", legacy, H.ago(5)),
                 H.ev("Mike", "question", STABLE, H.ago(1))],
        "Wags": [H.ev("Wags", "status", f"{RE.ACK_PREFIX}Mike/{legacy}", H.ago(4),
                      {"suppress_days": 14})],
    })
    try:
        decision, reason = RE.decide(STABLE, root)
        check("câu hỏi MỚI NHẤT (chưa ack) quyết định, không phải legacy đã ack ⇒ POST",
              decision == "POST", f"{decision} — {reason}")
        acked, esc, out = _check5_verdict(root, STABLE)
        check("CHECK5 thật cũng escalate câu hỏi mới đó", esc and not acked, out)
        _consist("ca 7j", decision, acked)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 8b: ĐƯỜNG GHI THẬT (không --dry-run) cho CẢ 2 nhánh POST và SKIP ─────────────
#    arch-review vòng 2: mọi ca CLI trước đây đều --dry-run nên 2 mutation (bỏ
#    recurring_days khỏi payload; đổi prefix topic nhánh SKIP) sống sót.
def _run_real(sandbox_bin_root, bus_root, pattern, days, payload):
    return subprocess.run(
        [sys.executable, "-B", os.path.join(sandbox_bin_root, "bin", "retro_escalate.py"),
         "--pattern", pattern, "--days", str(days), "--payload", payload,
         "--bus-root", bus_root],
        capture_output=True, text=True,
        env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", JOB_ID=""))


def _events_of(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def case_real_write_post_and_skip():
    sb = tempfile.mkdtemp(prefix="retro_write_")
    try:
        os.symlink(BIN, os.path.join(sb, "bin"))          # ROOT của append_event.sh = sb
        bus_root = _mk({"Taylor": [H.ev("Taylor", "question", "chuyen-khac", H.ago(1))]})
        try:
            # (1) POST — pattern chưa có câu hỏi nào
            r = _run_real(sb, bus_root, "foo-bar", 3, '{"summary":"x"}')
            check("ghi THẬT nhánh POST: rc=0", r.returncode == 0, r.stdout + r.stderr)
            check("ghi THẬT nhánh POST: in WROTE=question", "WROTE=question" in r.stdout,
                  r.stdout)
            evs = _events_of(os.path.join(sb, "bus", "inbox", "Mike.jsonl"))
            q = [e for e in evs if e.get("event_type") == "question"]
            check("POST ghi đúng 1 event question", len(q) == 1, str(evs))
            if q:
                check("POST: topic = topic ỔN ĐỊNH", q[0].get("topic") == STABLE,
                      str(q[0].get("topic")))
                check("POST: payload.recurring_days == --days",
                      q[0].get("payload", {}).get("recurring_days") == 3,
                      str(q[0].get("payload")))
            # (2) SKIP — dựng bus có câu hỏi + ack phủ
            H.write_events(os.path.join(bus_root, "mike", "bus", "inbox", "Mike.jsonl"),
                           [H.ev("Mike", "question", STABLE, H.ago(1))])
            H.write_events(os.path.join(bus_root, "mike", "bus", "inbox", "Wags.jsonl"),
                           [H.ev("Wags", "status", f"{RE.ACK_PREFIX}Mike/{STABLE}",
                                 H.ago(0, 12), {"suppress_days": 7})])
            r2 = _run_real(sb, bus_root, "foo-bar", 4, '{"summary":"x"}')
            check("ghi THẬT nhánh SKIP: rc=0", r2.returncode == 0, r2.stdout + r2.stderr)
            evs2 = _events_of(os.path.join(sb, "bus", "inbox", "Mike.jsonl"))
            st = [e for e in evs2 if e.get("event_type") == "status"]
            check("SKIP ghi đúng 1 event status (không mở question thứ hai)",
                  len(st) == 1 and len([e for e in evs2
                                        if e.get("event_type") == "question"]) == 1,
                  str([e.get("event_type") for e in evs2]))
            if st:
                check(f"SKIP: topic mang đúng hằng SKIP_STATUS_PREFIX "
                      f"({RE.SKIP_STATUS_PREFIX!r})",
                      st[0].get("topic") == f"{RE.SKIP_STATUS_PREFIX}{STABLE}",
                      str(st[0].get("topic")))
                check("SKIP: payload vẫn giữ recurring_days (số ngày KHÔNG mất)",
                      st[0].get("payload", {}).get("recurring_days") == 4,
                      str(st[0].get("payload")))
        finally:
            shutil.rmtree(bus_root, ignore_errors=True)
    finally:
        shutil.rmtree(sb, ignore_errors=True)


# ── Ca 9c: hằng SKIP_STATUS_PREFIX phải khớp chuỗi grep trong daily_retro.sh ────────
def case_skip_prefix_constant_in_sync():
    src = open(os.path.join(BIN, "daily_retro.sh"), encoding="utf-8").read()
    check("daily_retro.sh dùng ĐÚNG chuỗi SKIP_STATUS_PREFIX của retro_escalate.py",
          f'"{RE.SKIP_STATUS_PREFIX}"' in src,
          f"không thấy {RE.SKIP_STATUS_PREFIX!r} trong daily_retro.sh")


# ── Ca 7k: answer CŨ HƠN câu hỏi KHÔNG được coi là đã giải quyết (pre-resolve) ─────
def case_older_answer_does_not_preresolve():
    root = _mk({
        "Mike": [H.ev("Mike", "answer", STABLE, H.ago(10)),
                 H.ev("Mike", "question", STABLE, H.ago(1))],
    })
    try:
        decision, reason = RE.decide(STABLE, root)
        check("answer đăng TRƯỚC câu hỏi không được pre-resolve nó ⇒ vẫn xét ack, POST vì "
              "chưa ai ack", decision == "POST", f"{decision} — {reason}")
        check("lý do phải là 'không ack nào phủ', KHÔNG phải 'đã có answer'",
              "KHÔNG ack nào" in reason, reason)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main():
    print("== retro_escalate selfcheck (bug ack-topic-counter) ==")
    for fn in (case_constants_in_sync, case_counter_slug_is_rejected,
               case_no_false_collapse_between_patterns, case_day_n_plus_1_still_covered,
               case_red_control_old_counter_shape, case_expired_ack_reescalates,
               case_suppress_days_clamped, case_first_time_posts,
               case_ack_sd0_covers_existing_instance, case_ack_sd0_has_escape_hatch,
               case_legacy_counter_question_still_recognised,
               case_different_pattern_not_collapsed, case_unrelated_ack_does_not_cover,
               case_ack_bare_topic_form_covers, case_corrupt_ts_is_fail_closed,
               case_archive_gz_is_read, case_resolved_question_is_not_basis_for_skip,
               case_older_answer_does_not_preresolve,
               case_missing_bus_fails_loud, case_cli_dry_run_writes_nothing,
               case_reject_message_example_is_actually_valid,
               case_extra_counter_units_rejected,
               case_fresh_window_ack_not_overridden_by_escape,
               case_escape_hatch_measures_ack_age, case_newest_question_wins,
               case_real_write_post_and_skip, case_skip_prefix_constant_in_sync,
               case_daily_retro_wired, case_daily_retro_guard_sees_skip_status,
               case_append_event_guard_is_mechanical):
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
