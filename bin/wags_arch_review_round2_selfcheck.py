#!/usr/bin/env python3
"""Selfcheck cho cơ chế "arch-review NEEDS_CHANGES 2 vòng liên tiếp cùng topic trong ≤24h
⇒ tự động escalate bus question RIÊNG cho Mike/user" (user mandate 2026-09-19,
retro-2026-09-17 + retro-2026-09-18).

Hai phần, cùng nguyên tắc "TRÍCH khối thật, không copy thuật toán" đã dùng ở
wags_bus_verdict_selfcheck.py / wags_autofix_postq_selfcheck.py:

  A. bin/wags_arch_review_round2.py chạy trực tiếp (subprocess thật) trên bus giả — streak
     liên tiếp, reset bởi CONFIRMED, cửa sổ 24h, prefix có hậu tố mô tả, payload hỏng.
  B. Khối WAGS_ROUND2_ESCALATE_BEGIN/END trong wags_autofix.sh — TRÍCH ra chạy trong đúng
     ngữ cảnh `bash -c '…'` mà production dùng (idiom '"$VAR"' nội suy từ shell ngoài),
     với `_post_q`/`_notify_arch` được STUB để quan sát có gọi hay không (đúng call nào),
     và `wags_bus_question_pending.py` (qua `bus_question_audit.py` thật) chạy THẬT trên
     fixture bus/inbox/*.jsonl để dedup round-3+ không bị escalate lặp — VÀ để một cụm MỚI
     sau khi cụm cũ đã ĐƯỢC ĐÓNG (answer/decision thật, không phải chỉ hết cửa sổ thời gian)
     vẫn escalate lại — là hành vi thật, không phải giả định.

Chạy: python3 bin/wags_arch_review_round2_selfcheck.py   (exit 0 = PASS, 1 = FAIL)
"""
import datetime as dt
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DETECTOR = ROOT / "bin" / "wags_arch_review_round2.py"
AUTOFIX_SRC = Path(os.environ.get("WAGS_AUTOFIX_SRC") or (ROOT / "bin" / "wags_autofix.sh"))
MIKE_JSON = ROOT / "bin" / "mike_json.py"
PENDING_CHECK = ROOT / "bin" / "wags_bus_question_pending.py"
BUS_AUDIT = ROOT / "bin" / "bus_question_audit.py"

LABEL = "coord-2026-09-19"
PREFIX = f"ARCH-REVIEW: wags-fix: {LABEL}"

# arch-review coord-2026-09-19 round 3: Part B từng dùng mốc TUYỆT ĐỐI (2026-09-19T…) trong
# lúc khối WAGS_ROUND2_ESCALATE giờ tính "fresh" bằng `date -u` (giờ CHẠY THẬT) — selfcheck sẽ
# tự đỏ đúng 24h sau khi mốc tuyệt đối đó già hơn 24h, không liên quan gì tới lỗi thật. Mọi
# fixture ts trong Part B giờ tính TƯƠNG ĐỐI so với "bây giờ" của chính lần chạy.
_NOW = dt.datetime.now(dt.timezone.utc)


def _iso(hours_ago=0.0):
    return (_NOW - dt.timedelta(hours=hours_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")

fails = []


def check(name, cond, detail=""):
    if cond:
        print(f"  PASS  {name}")
    else:
        fails.append(f"{name} — {detail}")
        print(f"  FAIL  {name} — {detail}")


def ev(topic, ts, payload):
    return {"agent_id": "arch-reviewer", "event_type": "verification", "topic": topic,
            "ts": ts, "payload": payload, "event_id": f"arch-{ts}"}


def mkinbox(events):
    d = tempfile.mkdtemp(prefix="wags_round2_selfcheck_")
    path = os.path.join(d, "arch-reviewer.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    return d, path


def run_detector(path, prefix=PREFIX, window=24, now_iso=None):
    args = [sys.executable, str(DETECTOR), path, prefix, str(window)]
    if now_iso is not None:
        args.append(now_iso)
    p = subprocess.run(args, capture_output=True, text=True)
    try:
        out = json.loads(p.stdout.strip())
    except Exception:
        out = None
    return p.returncode, out, p.stderr


# ══ Phần A — bin/wags_arch_review_round2.py trực tiếp ═══════════════════════════════════

# ── Ca 1: 2 NEEDS_CHANGES liên tiếp trong 24h ⇒ escalate, round_count=2
def case_two_needs_changes_within_window_escalates():
    d, path = mkinbox([
        ev(PREFIX, "2026-09-19T01:23:01Z", {"verdict": "NEEDS_CHANGES", "required_changes": ["a", "b"]}),
        ev(PREFIX, "2026-09-19T05:48:16Z", {"verdict": "NEEDS_CHANGES", "required_changes": ["b", "c"]}),
    ])
    try:
        rc, out, _ = run_detector(path)
        check("2 NEEDS_CHANGES liên tiếp trong 24h: escalate=True, round_count=2",
              rc == 0 and out and out.get("escalate") is True and out.get("round_count") == 2,
              f"rc={rc} out={out}")
        check("giữ nguyên first_ts/latest_ts đúng 2 mốc thật",
              out and out.get("first_ts") == "2026-09-19T01:23:01Z"
              and out.get("latest_ts") == "2026-09-19T05:48:16Z", out)
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── Ca 2: chỉ 1 verdict xấu ⇒ KHÔNG escalate (round-1 bình thường)
def case_single_needs_changes_no_escalate():
    d, path = mkinbox([ev(PREFIX, "2026-09-19T01:23:01Z", {"verdict": "NEEDS_CHANGES"})])
    try:
        rc, out, _ = run_detector(path)
        check("chỉ 1 NEEDS_CHANGES: escalate=False, round_count=1",
              rc == 1 and out and out.get("escalate") is False and out.get("round_count") == 1,
              f"rc={rc} out={out}")
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── Ca 3: 2 verdict xấu nhưng CÁCH NHAU >24h ⇒ KHÔNG escalate (không phải "liên tiếp")
def case_two_bad_verdicts_outside_window_no_escalate():
    d, path = mkinbox([
        ev(PREFIX, "2026-09-17T01:23:01Z", {"verdict": "NEEDS_CHANGES"}),
        ev(PREFIX, "2026-09-19T05:48:16Z", {"verdict": "REFUTED"}),
    ])
    try:
        rc, out, _ = run_detector(path)
        check("2 verdict xấu cách nhau >24h: escalate=False (nhưng round_count vẫn báo đúng 2)",
              rc == 1 and out and out.get("escalate") is False and out.get("round_count") == 2,
              f"rc={rc} out={out}")
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── Ca 4: CONFIRMED giữa 2 NEEDS_CHANGES ⇒ RESET streak — verdict sau là ca MỚI, không
#    phải "round 2 chưa xong" của verdict trước CONFIRMED.
def case_confirmed_resets_streak():
    d, path = mkinbox([
        ev(PREFIX, "2026-09-17T01:23:01Z", {"verdict": "NEEDS_CHANGES"}),
        ev(PREFIX, "2026-09-17T05:48:16Z", {"verdict": "CONFIRMED"}),
        ev(PREFIX, "2026-09-19T02:00:00Z", {"verdict": "NEEDS_CHANGES"}),
    ])
    try:
        rc, out, _ = run_detector(path)
        check("CONFIRMED cắt streak: verdict xấu SAU đó tính lại từ đầu (round_count=1, không escalate)",
              rc == 1 and out and out.get("escalate") is False and out.get("round_count") == 1,
              f"rc={rc} out={out}")
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── Ca 5: 3 vòng xấu liên tiếp trong 24h ⇒ round_count=3, vẫn escalate=True (không chỉ dừng
#    ở đúng 2) — caller (wags_autofix.sh) chịu trách nhiệm dedup không mở trùng câu hỏi.
def case_three_rounds_still_escalates():
    d, path = mkinbox([
        ev(PREFIX, "2026-09-19T01:00:00Z", {"verdict": "NEEDS_CHANGES"}),
        ev(PREFIX, "2026-09-19T05:00:00Z", {"verdict": "REFUTED"}),
        ev(PREFIX, "2026-09-19T09:00:00Z", {"verdict": "NEEDS_CHANGES"}),
    ])
    try:
        rc, out, _ = run_detector(path)
        check("3 vòng xấu liên tiếp trong 24h: escalate=True, round_count=3",
              rc == 0 and out and out.get("escalate") is True and out.get("round_count") == 3,
              f"rc={rc} out={out}")
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── Ca 6: topic khớp TIỀN TỐ (arch-reviewer nối mô tả phía sau) vẫn nhận, topic khác hẳn thì không
def case_topic_prefix_scope():
    d, path = mkinbox([
        ev(f"{PREFIX} — vòng 1", "2026-09-19T01:00:00Z", {"verdict": "NEEDS_CHANGES"}),
        ev(f"{PREFIX} — vòng 2, gate state_source", "2026-09-19T05:00:00Z", {"verdict": "NEEDS_CHANGES"}),
        ev("ARCH-REVIEW: wags-fix: coord-KHAC-HAN", "2026-09-19T06:00:00Z", {"verdict": "REFUTED"}),
    ])
    try:
        rc, out, _ = run_detector(path)
        check("topic khớp tiền tố (hậu tố mô tả khác nhau mỗi vòng) vẫn gộp streak: escalate=True, round_count=2",
              rc == 0 and out and out.get("escalate") is True and out.get("round_count") == 2,
              f"rc={rc} out={out}")
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── Ca 7: payload hỏng / event_type khác / file thiếu ⇒ không escalate, không crash
def case_broken_input_is_safe():
    d = tempfile.mkdtemp(prefix="wags_round2_selfcheck_")
    try:
        rc, out, err = run_detector(os.path.join(d, "khong-ton-tai.jsonl"))
        check("file thiếu: escalate=False, không traceback",
              rc == 1 and out and out.get("escalate") is False and "Traceback" not in err,
              f"rc={rc} out={out} err={err}")
    finally:
        shutil.rmtree(d, ignore_errors=True)

    path = os.path.join(d if os.path.isdir(d) else tempfile.mkdtemp(), "arch-reviewer.jsonl")
    d2 = os.path.dirname(path)
    os.makedirs(d2, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("dong hong khong phai json {{\n")
        f.write(json.dumps(ev(PREFIX, "2026-09-19T01:00:00Z", "khong phai dict")) + "\n")
        f.write(json.dumps(ev(PREFIX, "2026-09-19T02:00:00Z", {"verdict": "UNKNOWN_VERDICT"})) + "\n")
        f.write(json.dumps({"agent_id": "arch-reviewer", "event_type": "finding", "topic": PREFIX,
                            "ts": "2026-09-19T03:00:00Z", "payload": {"verdict": "NEEDS_CHANGES"}}) + "\n")
    try:
        rc, out, err = run_detector(path)
        check("dòng hỏng / payload không phải dict / verdict lạ / event_type != verification: "
              "đều bị bỏ qua an toàn, không escalate giả",
              rc == 1 and out and out.get("escalate") is False and "Traceback" not in err,
              f"rc={rc} out={out} err={err}")
    finally:
        shutil.rmtree(d2, ignore_errors=True)


# ── Ca 7b (required_change #4, arch-review coord-2026-09-19 round 3): streak MẠN TÍNH — mốc
#    round đầu đã 3 ngày (first->latest > 24h, cửa sổ CŨ sẽ nói escalate=False vĩnh viễn), 2
#    vòng GẦN NHẤT chỉ cách nhau 1h, now_iso NGAY sau round mới nhất ⇒ PHẢI vẫn escalate=True
#    (mỏ neo last-two, không phải first->latest).
def case_last_two_anchor_beats_first_to_latest():
    now = dt.datetime.now(dt.timezone.utc)

    def iso(hours_ago):
        return (now - dt.timedelta(hours=hours_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")

    d, path = mkinbox([
        ev(PREFIX, iso(72), {"verdict": "NEEDS_CHANGES"}),
        ev(PREFIX, iso(2), {"verdict": "NEEDS_CHANGES"}),
        ev(PREFIX, iso(1), {"verdict": "REFUTED"}),
    ])
    try:
        rc, out, _ = run_detector(path, now_iso=iso(0))
        check("streak mạn tính (round đầu 72h trước, 2 vòng gần nhất cách 1h): "
              "escalate=True nhờ mỏ neo LAST-TWO (mỏ neo first->latest cũ sẽ cho False vì 71h>24h)",
              rc == 0 and out and out.get("escalate") is True
              and out.get("last_two_gap_hours") == 1.0, f"rc={rc} out={out}")
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── Ca 7c: 2 vòng gần nhất SÁT nhau nhưng cả cụm đó đã CŨ so với now_iso thật (vd dữ liệu
#    tĩnh/đồng bộ trễ) ⇒ KHÔNG escalate — "gần nhau" không đủ, phải "gần nhau VÀ gần NGAY BÂY GIỜ".
def case_now_iso_staleness_blocks_escalate():
    now = dt.datetime.now(dt.timezone.utc)

    def iso(hours_ago):
        return (now - dt.timedelta(hours=hours_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")

    d, path = mkinbox([
        ev(PREFIX, iso(74), {"verdict": "NEEDS_CHANGES"}),
        ev(PREFIX, iso(73), {"verdict": "REFUTED"}),
    ])
    try:
        rc, out, _ = run_detector(path, now_iso=iso(0))
        check("2 vòng gần nhau (1h) nhưng CẢ CỤM đã 73h trước 'now' thật: escalate=False, fresh=False",
              rc == 1 and out and out.get("escalate") is False and out.get("fresh") is False,
              f"rc={rc} out={out}")
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ══ Phần B — khối WAGS_ROUND2_ESCALATE trong wags_autofix.sh (trích, không copy) ═════════

def extract_block():
    src = AUTOFIX_SRC.read_text(encoding="utf-8")
    m = re.search(r"# WAGS_ROUND2_ESCALATE_BEGIN[^\n]*\n(.*?)[ \t]*# WAGS_ROUND2_ESCALATE_END",
                  src, re.S)
    if not m:
        return None
    return m.group(1)


# Khung ngoài TÁI LẬP ĐÚNG 2 tầng nháy của production (xem wags_bus_verdict_selfcheck.py /
# wags_autofix_postq_selfcheck.py — chạy khối trong `bash -c '…'` NẰM TRONG một script file,
# để lớp bash NGOÀI resolve các idiom '"$VAR"' giống hệt cách wags_autofix.sh tự dựng lệnh
# `setsid bash -c '<BIGSTRING>'` — chạy khối bằng đúng MỘT lớp `bash -c "…"` trực tiếp (như
# bản đầu tiên của file này) làm '"$PIPELOG"' không được resolve, tự tạo lỗi harness giả.
_HARNESS = r"""
ROOT=__ROOT__
LABEL=__LABEL__
VERDICT=__VERDICT__
PIPELOG=__PIPELOG__
POSTQ_LOG=__POSTQ_LOG__
NOTIFY_LOG=__NOTIFY_LOG__
bash -c '
  ROOT="'"$ROOT"'"; LABEL="'"$LABEL"'"; verdict="'"$VERDICT"'"
  POSTQ_LOG="'"$POSTQ_LOG"'"; NOTIFY_LOG="'"$NOTIFY_LOG"'"
  _post_q() { printf "TOPIC=%s\n" "$1" >> "$POSTQ_LOG"; printf "PAYLOAD=%s\n" "$2" >> "$POSTQ_LOG"; }
  _notify_arch() { printf "%s\n" "$1" >> "$NOTIFY_LOG"; }
__BLOCK__
'
"""


def run_block(sandbox_root, verdict):
    """Chạy khối thật trong đúng 2 tầng nháy như production, với `_post_q`/`_notify_arch`
    stub (chỉ ghi log để quan sát), rồi trả (rc, stderr, postq_log, notify_log, pipelog)."""
    block = extract_block()
    if block is None:
        return None
    pipelog = os.path.join(sandbox_root, "pipe.log")
    postq_log = os.path.join(sandbox_root, "postq.log")
    notify_log = os.path.join(sandbox_root, "notify.log")
    script = (_HARNESS
              .replace("__ROOT__", shlex.quote(sandbox_root))
              .replace("__LABEL__", shlex.quote(LABEL))
              .replace("__VERDICT__", shlex.quote(verdict))
              .replace("__PIPELOG__", shlex.quote(pipelog))
              .replace("__POSTQ_LOG__", shlex.quote(postq_log))
              .replace("__NOTIFY_LOG__", shlex.quote(notify_log))
              .replace("__BLOCK__", block))
    sp = os.path.join(sandbox_root, "run.sh")
    with open(sp, "w", encoding="utf-8") as f:
        f.write(script)
    p = subprocess.run(["bash", sp], capture_output=True, text=True)
    postq = Path(postq_log).read_text(encoding="utf-8") if os.path.exists(postq_log) else ""
    notify = Path(notify_log).read_text(encoding="utf-8") if os.path.exists(notify_log) else ""
    log = Path(pipelog).read_text(encoding="utf-8") if os.path.exists(pipelog) else ""
    return p.returncode, p.stderr, postq, notify, log


# ══ Phần B2 — khối WAGS_ROUND2_CLOSE trong wags_autofix.sh (trích, không copy) ═══════════
# arch-review coord-2026-09-19 round 3: bản trước KHÔNG có bất kỳ selfcheck nào chạy khối
# này — comment ở wags_autofix.sh tự nhận "đổi/xoá marker ⇒ selfcheck FAIL ngay" là SAI (đã
# xác minh: đổi tên marker mà toàn bộ file vẫn "OK: toàn bộ assertion PASS"). Đây chính là
# đường mà bug topic-mismatch (close dùng ref khác hẳn topic mà escalate post) lọt qua.

def extract_close_block():
    src = AUTOFIX_SRC.read_text(encoding="utf-8")
    m = re.search(r"# WAGS_ROUND2_CLOSE_BEGIN[^\n]*\n(.*?)[ \t]*# WAGS_ROUND2_CLOSE_END",
                  src, re.S)
    if not m:
        return None
    return m.group(1)


_HARNESS_CLOSE = r"""
ROOT=__ROOT__
LABEL=__LABEL__
BUS_VERDICT=__BUS_VERDICT__
PIPELOG=__PIPELOG__
NOTIFY_LOG=__NOTIFY_LOG__
bash -c '
  ROOT="'"$ROOT"'"; LABEL="'"$LABEL"'"; bus_verdict="'"$BUS_VERDICT"'"
  NOTIFY_LOG="'"$NOTIFY_LOG"'"
  _notify_arch() { printf "%s\n" "$1" >> "$NOTIFY_LOG"; }
__BLOCK__
'
"""


def run_close_block(sandbox_root, bus_verdict, close_stub_rc=0):
    """Chạy khối WAGS_ROUND2_CLOSE thật (trích từ wags_autofix.sh) với close_bus_question.py
    STUB (ghi lại argv, trả exit=close_stub_rc) — trả (rc, stderr, notify_log, pipelog,
    stub_calls_jsonl)."""
    block = extract_close_block()
    if block is None:
        return None
    pipelog = os.path.join(sandbox_root, "pipe.log")
    notify_log = os.path.join(sandbox_root, "notify.log")
    script = (_HARNESS_CLOSE
              .replace("__ROOT__", shlex.quote(sandbox_root))
              .replace("__LABEL__", shlex.quote(LABEL))
              .replace("__BUS_VERDICT__", shlex.quote(bus_verdict))
              .replace("__PIPELOG__", shlex.quote(pipelog))
              .replace("__NOTIFY_LOG__", shlex.quote(notify_log))
              .replace("__BLOCK__", block))
    sp = os.path.join(sandbox_root, "run_close.sh")
    with open(sp, "w", encoding="utf-8") as f:
        f.write(script)
    env = dict(os.environ)
    env["CLOSE_STUB_RC"] = str(close_stub_rc)
    p = subprocess.run(["bash", sp], capture_output=True, text=True, env=env)
    notify = Path(notify_log).read_text(encoding="utf-8") if os.path.exists(notify_log) else ""
    log = Path(pipelog).read_text(encoding="utf-8") if os.path.exists(pipelog) else ""
    stub_log = os.path.join(sandbox_root, "close_stub_calls.log")
    calls = Path(stub_log).read_text(encoding="utf-8") if os.path.exists(stub_log) else ""
    return p.returncode, p.stderr, notify, log, calls


# Stub close_bus_question.py — KHÔNG dùng bản thật (bản thật gọi append_event.sh + đọc
# resolver qua bus_question_audit.py thật, quá nặng để test riêng nhánh gate/error-surfacing
# của khối CLOSE). Ghi lại argv nó nhận được (để đối chiếu ref byte-identical với topic mà
# khối ESCALATE post) và trả exit code lấy từ env CLOSE_STUB_RC (mặc định 0 = thành công).
_CLOSE_STUB = '''#!/usr/bin/env python3
import json, os, sys
log = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "close_stub_calls.log")
with open(log, "a", encoding="utf-8") as f:
    f.write(json.dumps(sys.argv[1:], ensure_ascii=False) + "\\n")
sys.exit(int(os.environ.get("CLOSE_STUB_RC", "0")))
'''


def mksandbox(arch_events, wags_events=None):
    d = tempfile.mkdtemp(prefix="wags_round2_block_")
    os.makedirs(os.path.join(d, "bin"))
    os.makedirs(os.path.join(d, "bus", "inbox"))
    shutil.copy2(DETECTOR, os.path.join(d, "bin", "wags_arch_review_round2.py"))
    shutil.copy2(MIKE_JSON, os.path.join(d, "bin", "mike_json.py"))
    shutil.copy2(PENDING_CHECK, os.path.join(d, "bin", "wags_bus_question_pending.py"))
    shutil.copy2(BUS_AUDIT, os.path.join(d, "bin", "bus_question_audit.py"))
    with open(os.path.join(d, "bin", "close_bus_question.py"), "w", encoding="utf-8") as f:
        f.write(_CLOSE_STUB)
    with open(os.path.join(d, "bus", "inbox", "arch-reviewer.jsonl"), "w", encoding="utf-8") as f:
        for e in arch_events:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    with open(os.path.join(d, "bus", "inbox", "Wags.jsonl"), "w", encoding="utf-8") as f:
        for e in (wags_events or []):
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    return d


# ── Ca 14: marker CLOSE phải còn ở đó
def case_close_marker_exists():
    blk = extract_close_block()
    check("wags_autofix.sh: còn marker WAGS_ROUND2_CLOSE_BEGIN/END",
          bool(blk) and "close_bus_question.py" in blk,
          "không trích được khối — marker bị xoá/đổi tên?")


# ── Ca 15: bus_verdict=CONFIRMED ⇒ close ĐƯỢC gọi, đúng ref, KHÔNG báo lỗi
def case_close_calls_when_bus_confirmed():
    d = mksandbox([])
    try:
        r = run_close_block(d, "CONFIRMED", close_stub_rc=0)
        check("bus_verdict=CONFIRMED: close_bus_question.py ĐƯỢC gọi", bool(r and r[4].strip()), r and r[4])
        expected_ref = f"Wags/wags-arch-review-round2-unresolved: {LABEL}"
        got_ref = None
        if r and r[4].strip():
            got_ref = json.loads(r[4].splitlines()[0])[0]
        check("ref đóng BYTE-IDENTICAL với topic mà khối ESCALATE post đi (chính bug session "
              "này tìm thấy: 2 chuỗi khác nhau ⇒ close_bus_question.py no-op im lặng)",
              got_ref == expected_ref, f"got={got_ref!r} expected={expected_ref!r}")
        check("đóng THÀNH CÔNG: không báo Discord THẤT BẠI", r and "THẤT BẠI" not in r[2], r and r[2])
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── Ca 16: bus_verdict=NEEDS_CHANGES ⇒ close KHÔNG được gọi (không tự đóng bằng verdict
#    chưa xác nhận thật)
def case_close_not_called_when_bus_needs_changes():
    d = mksandbox([])
    try:
        r = run_close_block(d, "NEEDS_CHANGES", close_stub_rc=0)
        check("bus_verdict=NEEDS_CHANGES: close_bus_question.py KHÔNG được gọi", r and r[4] == "", r and r[4])
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── Ca 17: bus_verdict rỗng (bus im lặng, không tìm thấy verification) ⇒ KHÔNG được đóng —
#    "không có bằng chứng" không phải "bằng chứng ngược"
def case_close_not_called_when_bus_empty():
    d = mksandbox([])
    try:
        r = run_close_block(d, "", close_stub_rc=0)
        check("bus_verdict rỗng: close_bus_question.py KHÔNG được gọi", r and r[4] == "", r and r[4])
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── Ca 18: close_bus_question.py thất bại (vd BLOCKED bởi rollup) ⇒ PHẢI thấy được, không
#    bị nuốt bằng `|| true` (đây chính là điều required_change #2/#3 yêu cầu)
def case_close_failure_is_surfaced():
    d = mksandbox([])
    try:
        r = run_close_block(d, "CONFIRMED", close_stub_rc=4)
        check("close_bus_question.py thất bại (exit=4): CÓ ghi dòng lỗi vào pipelog (không nuốt bằng || true)",
              r and "loi exit=4" in r[3], r and r[3])
        check("close_bus_question.py thất bại: CÓ báo Discord THẤT BẠI riêng (không im lặng)",
              r and "THẤT BẠI" in r[2], r and r[2])
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── Ca 8: marker phải còn ở đó
def case_marker_exists():
    blk = extract_block()
    check("wags_autofix.sh: còn marker WAGS_ROUND2_ESCALATE_BEGIN/END",
          bool(blk) and "wags_arch_review_round2.py" in blk,
          "không trích được khối — marker bị xoá/đổi tên?")


# ── Ca 9: verdict=NEEDS_CHANGES, round 2 vừa xảy ra trong bus, chưa có escalate trước đó
#    ⇒ _post_q ĐƯỢC gọi với đúng topic "wags-arch-review-round2-unresolved: <LABEL>"
def case_escalates_when_round2_fresh():
    d = mksandbox([
        ev(PREFIX, _iso(5), {"verdict": "NEEDS_CHANGES", "required_changes": ["x"]}),
        ev(PREFIX, _iso(1), {"verdict": "NEEDS_CHANGES", "required_changes": ["y"]}),
    ])
    try:
        r = run_block(d, "NEEDS_CHANGES")
        check("round-2 mới, chưa từng escalate: khối chạy KHÔNG lỗi", r and r[0] == 0, r and r[1])
        check("round-2 mới: _post_q ĐƯỢC gọi với topic round2-unresolved đúng LABEL",
              r and f"TOPIC=wags-arch-review-round2-unresolved: {LABEL}" in r[2], r and r[2])
        check("round-2 mới: có báo Discord riêng (khác câu hỏi round-1 thường)",
              r and "2+ VÒNG LIÊN TIẾP" in r[3], r and r[3])
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── Ca 10: verdict=NEEDS_CHANGES nhưng chỉ round-1 (chưa có round-2) ⇒ KHÔNG escalate riêng
#    (câu hỏi round-1 thường vẫn đi qua _post_q "wags-fix-not-confirmed" ở NHÁNH KHÁC, không
#    phải khối này — khối này chỉ lo phần round-2-liên-tiếp).
def case_no_escalate_on_round1_only():
    d = mksandbox([ev(PREFIX, _iso(1), {"verdict": "NEEDS_CHANGES"})])
    try:
        r = run_block(d, "NEEDS_CHANGES")
        check("chỉ round-1: khối chạy không lỗi", r and r[0] == 0, r and r[1])
        check("chỉ round-1: _post_q KHÔNG được gọi (chưa phải round-2 liên tiếp)",
              r and r[2] == "", r and r[2])
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── Ca 11: verdict=CONFIRMED (round tiếp theo đã pass) ⇒ khối không escalate gì (điều kiện
#    `if verdict = NEEDS_CHANGES || REFUTED` chặn ngay từ đầu)
def case_no_escalate_on_confirmed():
    d = mksandbox([
        ev(PREFIX, _iso(5), {"verdict": "NEEDS_CHANGES"}),
        ev(PREFIX, _iso(1), {"verdict": "NEEDS_CHANGES"}),
    ])
    try:
        r = run_block(d, "CONFIRMED")
        check("verdict CONFIRMED: khối không gọi _post_q (dù bus có sẵn 2 vòng xấu trước đó)",
              r and r[2] == "", r and r[2])
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── Ca 12 (DEDUP — quan trọng nhất): round-2 escalate ĐÃ mở từ trước (có trong Wags.jsonl,
#    ts >= first_ts của streak hiện tại) ⇒ KHÔNG mở trùng câu hỏi thứ 2 khi round-3 cũng xấu.
def case_dedup_does_not_reopen():
    d = mksandbox(
        [
            ev(PREFIX, _iso(9), {"verdict": "NEEDS_CHANGES"}),
            ev(PREFIX, _iso(5), {"verdict": "NEEDS_CHANGES"}),
            ev(PREFIX, _iso(1), {"verdict": "REFUTED"}),  # round 3, vẫn xấu
        ],
        wags_events=[{
            "agent_id": "Wags", "event_type": "question",
            "topic": f"wags-arch-review-round2-unresolved: {LABEL}",
            "ts": _iso(4.99), "payload": {"label": LABEL},
            "event_id": "wags-round2-q-1",
        }],
    )
    try:
        r = run_block(d, "REFUTED")
        check("đã escalate từ round-2 (mở ngay sau round 2, trước round 3 REFUTED): "
              "round-3 KHÔNG mở câu hỏi trùng — _post_q không được gọi",
              r and r[2] == "", r and r[2])
        check("có ghi dấu vết KHÔNG-mở-trùng vào pipelog (người đọc log hiểu vì sao im lặng)",
              r and "dang PENDING tu truoc" in r[4], r and r[4])
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── Ca 13: câu hỏi round-2-unresolved ĐÃ ĐƯỢC ĐÓNG (chỉ còn answer, không còn question mở)
#    rồi một CỤM MỚI (streak mới, first_ts mới hơn ts của câu hỏi đã đóng) lại xấu 2 vòng
#    liên tiếp ⇒ PHẢI escalate lại (đây là sự cố MỚI, không phải cùng câu hỏi cũ).
def case_new_cluster_after_old_closed_escalates_again():
    d = mksandbox(
        [
            ev(PREFIX, _iso(240), {"verdict": "NEEDS_CHANGES"}),           # cụm cũ, 10 ngày trước
            ev(PREFIX, _iso(236), {"verdict": "NEEDS_CHANGES"}),
            ev(PREFIX, _iso(232), {"verdict": "CONFIRMED"}),  # cụm cũ đã đóng, reset streak
            ev(PREFIX, _iso(5), {"verdict": "NEEDS_CHANGES"}),  # cụm MỚI
            ev(PREFIX, _iso(1), {"verdict": "NEEDS_CHANGES"}),
        ],
        wags_events=[{
            "agent_id": "Wags", "event_type": "question",
            "topic": f"wags-arch-review-round2-unresolved: {LABEL}",
            "ts": _iso(235.99), "payload": {"label": LABEL},
            "event_id": "wags-round2-q-old",
        }, {
            "agent_id": "Mike", "event_type": "answer",
            "topic": f"wags-arch-review-round2-unresolved: {LABEL}",
            "ts": _iso(234), "payload": {"decided_by": "user", "resolution": "da xu ly cum cu (fixture: dong that)"},
            "event_id": "wags-round2-q-old-closed",
        }],
    )
    try:
        r = run_block(d, "NEEDS_CHANGES")
        check("cụm cũ đã đóng (CONFIRMED reset streak) + cụm mới xấu 2 vòng: "
              "PHẢI escalate lại (first_ts cụm mới > ts câu hỏi cũ, dedup không chặn oan)",
              r and f"TOPIC=wags-arch-review-round2-unresolved: {LABEL}" in r[2], r and r[2])
    finally:
        shutil.rmtree(d, ignore_errors=True)


def main():
    print("wags_arch_review_round2_selfcheck: detector (A) + khối escalate (B) + khối close (B2) trong wags_autofix.sh")
    for fn in (case_two_needs_changes_within_window_escalates, case_single_needs_changes_no_escalate,
               case_two_bad_verdicts_outside_window_no_escalate, case_confirmed_resets_streak,
               case_three_rounds_still_escalates, case_topic_prefix_scope, case_broken_input_is_safe,
               case_last_two_anchor_beats_first_to_latest, case_now_iso_staleness_blocks_escalate,
               case_marker_exists, case_escalates_when_round2_fresh, case_no_escalate_on_round1_only,
               case_no_escalate_on_confirmed, case_dedup_does_not_reopen,
               case_new_cluster_after_old_closed_escalates_again,
               case_close_marker_exists, case_close_calls_when_bus_confirmed,
               case_close_not_called_when_bus_needs_changes, case_close_not_called_when_bus_empty,
               case_close_failure_is_surfaced):
        print(f"\n[{fn.__name__}]")
        fn()
    if fails:
        print(f"\nFAIL: {len(fails)} assertion hỏng")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("\nOK: toàn bộ assertion PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
