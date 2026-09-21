#!/usr/bin/env python3
"""Selfcheck cho bin/close_plan_approval_questions.py (coord-2026-09-21).

Kiểm HÀNH VI, không so chuỗi: dựng bus + thư mục plan sandbox thật, chạy script thật,
rồi hỏi lại bin/bus_question_audit.py xem câu hỏi còn pending không.

Ca (a) `approved_at=None` là kịch bản THẬT của 8/9 lần duyệt plan tháng 9 (duyệt bằng
sửa JSON trực tiếp, không qua approve_plan_simple.sh) — đây chính là chỗ bản vá vòng 1
hụt, arch-review bắt được.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "cpaq", ROOT / "bin" / "close_plan_approval_questions.py")
cpaq = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cpaq)

FAILS: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"{'✅' if cond else '❌'} {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILS.append(name)


# ── 1. classify(): chỉ bắt đúng lớp câu hỏi ─────────────────────────────────────
Q = lambda t, a="Winston": {"agent": a, "topic": t}
qs = [
    Q("plan-SpaceX-2026-09-21-chua-duyet"),                              # → auto
    Q("ops-autofix-unresolved: run-bot-fail-SpaceX-2026-09-21"),         # → không khớp shape
    Q("ops-autofix-unresolved: plan-SpaceX-2026-09-21-chua-duyet"),      # → chỉ gợi ý
    Q("plan-ZaloPay-2026-09-21-chua-duyet"),                             # → account khác
    Q("plan-SpaceX-2026-09-18-chua-duyet"),                              # → ngày khác
    Q("funding-gate-open-order-double-count-SpaceX-2026-09-21"),         # → không phải chuyện duyệt
]
auto, hint = cpaq.classify(qs, "SpaceX", "2026-09-21")
check("auto-close ĐÚNG 1 câu hỏi 'chưa duyệt' của đúng account+ngày",
      [q["topic"] for q in auto] == ["plan-SpaceX-2026-09-21-chua-duyet"],
      str([q["topic"] for q in auto]))
check("lớp ops-autofix-unresolved KHÔNG bị tự đóng (chỉ gợi ý)",
      [q["topic"] for q in hint] == ["ops-autofix-unresolved: plan-SpaceX-2026-09-21-chua-duyet"],
      str([q["topic"] for q in hint]))
check("run-bot-fail (root cause có thể là funding-gate) KHÔNG bị đụng tới",
      all("run-bot-fail" not in q["topic"] for q in auto + hint))
check("account/ngày khác KHÔNG bị cuốn theo",
      all("ZaloPay" not in q["topic"] and "09-18" not in q["topic"] for q in auto + hint))


def build(root: Path, plans: dict[str, dict], topics: tuple[str, ...]) -> Path:
    """Dựng bus + plan dir sandbox. → plan_dir"""
    inbox = root / "bus" / "inbox"
    inbox.mkdir(parents=True)
    # append_event.sh lấy ROOT từ vị trí CHÍNH NÓ ⇒ copy vào sandbox thì nó ghi vào bus
    # sandbox, không đụng bus thật. Đây là điều kiện để selfcheck chạy end-to-end an toàn.
    (root / "bin").mkdir()
    for dep in ("append_event.sh", "mike_json.py"):
        src = ROOT / "bin" / dep
        if src.exists():
            dst = root / "bin" / dep
            dst.write_bytes(src.read_bytes())
            dst.chmod(0o755)
    plan_dir = root / "data" / "trade_plans"
    plan_dir.mkdir(parents=True)
    for name, body in plans.items():
        (plan_dir / name).write_text(json.dumps(body, ensure_ascii=False), encoding="utf-8")
    ts = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=6)).strftime("%Y-%m-%dT%H:%M:%SZ")
    with (inbox / "Winston.jsonl").open("w", encoding="utf-8") as f:
        for topic in topics:
            f.write(json.dumps({"event_id": topic, "ts": ts, "agent_id": "Winston",
                                "event_type": "question", "topic": topic,
                                "payload": {"question": "x"}}, ensure_ascii=False) + "\n")
    return plan_dir


def pending_topics(root: Path) -> list[str]:
    env = dict(os.environ, BUS_AUDIT_ROOT=str(root))
    r = subprocess.run([sys.executable, str(ROOT / "bin" / "bus_question_audit.py"), "--json"],
                       env=env, capture_output=True, text=True, timeout=30)
    return [q["topic"] for q in json.loads(r.stdout).get("pending", [])]


def run_closer(root: Path, plan_dir: Path, *extra: str):
    return subprocess.run(
        [sys.executable, str(ROOT / "bin" / "close_plan_approval_questions.py"),
         "--root", str(root), "--plan-dir", str(plan_dir), *extra],
        env=dict(os.environ, MIKE_ROOT=str(root), BUS_AUDIT_ROOT=str(root)),
        capture_output=True, text=True, timeout=120)


TOPICS = ("plan-SpaceX-2026-09-21-chua-duyet",
          "ops-autofix-unresolved: plan-SpaceX-2026-09-21-chua-duyet",
          "ops-autofix-unresolved: run-bot-fail-SpaceX-2026-09-21")

# ── 2. Ca THẬT của sự cố: approved_by có, approved_at=None (duyệt bằng sửa JSON tay) ──
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    plan_dir = build(root, {"plan_SpaceX_2026-09-21.json": {
        "approved_by": "user (John) - Discord", "approved_at": None,
        "orders": [{"ticker": "MBB"}]}}, TOPICS)
    before = pending_topics(root)
    check("sandbox dựng đúng: 3 câu hỏi đang pending", len(before) == 3, str(before))

    run = run_closer(root, plan_dir)
    after = pending_topics(root)
    check("chạy xong exit 0", run.returncode == 0, run.stderr[-400:])
    check("approved_at=None (kịch bản 8/9 lần duyệt tháng 9) VẪN đóng được câu hỏi",
          "plan-SpaceX-2026-09-21-chua-duyet" not in after, str(after))
    check("2 câu hỏi ops-autofix VẪN MỞ (cần người xác nhận bot chạy lại)",
          len([t for t in after if t.startswith("ops-autofix-unresolved:")]) == 2, str(after))
    check("in gợi ý đóng tay cho câu hỏi còn mở",
          "close_bus_question.py" in run.stdout, run.stdout[-400:])
    # Evidence phải là thứ ĐỌC ĐƯỢC TỪ FILE (arch-review vòng 1: bản cũ bịa evidence từ
    # argv và còn khẳng định sai "ghi bởi approve_plan_simple.sh"). Đọc event THẬT đã ghi.
    _ev = ""
    for _f in sorted((root / "bus" / "inbox").glob("*.jsonl")):
        for _ln in _f.read_text(encoding="utf-8").splitlines():
            _r = json.loads(_ln)
            if _r.get("event_type") == "answer" and "chua-duyet" in str(_r.get("topic")):
                _ev = json.dumps(_r.get("payload"), ensure_ascii=False)
    check("evidence TRÍCH TỪ FILE plan (path + approved_at đọc được), không bịa từ argv",
          "plan_SpaceX_2026-09-21.json" in _ev and "approved_at=None" in _ev
          and "approve_plan_simple.sh" not in _ev, _ev[-300:] or "(không thấy answer event)")

    run2 = run_closer(root, plan_dir)
    check("chạy lại idempotent (exit 0, không đóng nhầm câu hỏi còn lại)",
          run2.returncode == 0 and
          len([t for t in pending_topics(root) if t.startswith("ops-autofix-unresolved:")]) == 2,
          run2.stdout[-300:])

# ── 3. Plan CHƯA duyệt ⇒ tuyệt đối không đóng gì ────────────────────────────────
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    plan_dir = build(root, {"plan_SpaceX_2026-09-21.json": {
        "approved_by": None, "approved_at": None, "orders": []}}, TOPICS)
    run = run_closer(root, plan_dir)
    after = pending_topics(root)
    check("plan CHƯA có approved_by ⇒ KHÔNG đóng gì (câu hỏi vẫn đúng)",
          "plan-SpaceX-2026-09-21-chua-duyet" in after and run.returncode == 0, str(after))

# ── 4. Không có file plan ⇒ không đóng, không nổ ────────────────────────────────
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    plan_dir = build(root, {}, TOPICS)
    run = run_closer(root, plan_dir)
    check("thiếu file plan ⇒ không đóng, exit 0",
          run.returncode == 0 and "plan-SpaceX-2026-09-21-chua-duyet" in pending_topics(root),
          run.stdout[-300:])

# ── 5. --root thiếu DIR phải FAIL, không âm thầm rơi về bus THẬT ────────────────
bad = subprocess.run([sys.executable, str(ROOT / "bin" / "close_plan_approval_questions.py"),
                      "--root"], capture_output=True, text=True, timeout=30)
check("--root thiếu giá trị ⇒ báo lỗi (không im lặng dùng bus production)",
      bad.returncode != 0 and "expected one argument" in (bad.stderr or ""), bad.stderr[-200:])

print()
if FAILS:
    print(f"❌ FAIL {len(FAILS)}: {FAILS}")
    raise SystemExit(1)
print("✅ ALL PASS")
