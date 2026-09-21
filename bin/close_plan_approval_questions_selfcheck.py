#!/usr/bin/env python3
"""Selfcheck cho bin/close_plan_approval_questions.py (coord-2026-09-21).

Kiểm HÀNH VI, không so chuỗi: dựng bus sandbox thật, chạy script thật, rồi hỏi lại
bin/bus_question_audit.py xem câu hỏi còn pending không.
"""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "bin"))
import importlib.util

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
    Q("ops-autofix-unresolved: run-bot-fail-SpaceX-2026-09-21"),         # → chỉ gợi ý (không khớp shape)
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

# ── 2. end-to-end: bus sandbox, câu hỏi thật biến mất khỏi pending ──────────────
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    inbox = root / "bus" / "inbox"
    inbox.mkdir(parents=True)
    # append_event.sh lấy ROOT từ vị trí CHÍNH NÓ ⇒ copy vào sandbox thì nó ghi vào bus
    # sandbox, không đụng bus thật. Đây là điều kiện để selfcheck chạy end-to-end an toàn.
    (root / "bin").mkdir()
    for dep in ("append_event.sh", "mike_json.py"):
        src = ROOT / "bin" / dep
        if src.exists():
            (root / "bin" / dep).write_bytes(src.read_bytes())
            (root / "bin" / dep).chmod(0o755)
    ts = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=6)
          ).strftime("%Y-%m-%dT%H:%M:%SZ")
    with (inbox / "Winston.jsonl").open("w", encoding="utf-8") as f:
        for topic in ("plan-SpaceX-2026-09-21-chua-duyet",
                      "ops-autofix-unresolved: plan-SpaceX-2026-09-21-chua-duyet",
                      "ops-autofix-unresolved: run-bot-fail-SpaceX-2026-09-21"):
            f.write(json.dumps({"event_id": topic, "ts": ts, "agent_id": "Winston",
                                "event_type": "question", "topic": topic,
                                "payload": {"question": "x"}}, ensure_ascii=False) + "\n")

    def pending_topics() -> list[str]:
        env = dict(os.environ, BUS_AUDIT_ROOT=str(root))
        r = subprocess.run([sys.executable, str(ROOT / "bin" / "bus_question_audit.py"), "--json"],
                           env=env, capture_output=True, text=True, timeout=30)
        return [q["topic"] for q in json.loads(r.stdout).get("pending", [])]

    before = pending_topics()
    check("sandbox dựng đúng: 3 câu hỏi đang pending", len(before) == 3, str(before))

    env = dict(os.environ, MIKE_ROOT=str(root), BUS_AUDIT_ROOT=str(root))
    run = subprocess.run(
        [sys.executable, str(ROOT / "bin" / "close_plan_approval_questions.py"),
         "SpaceX", "2026-09-21", "user (John) - selfcheck", "--root", str(root)],
        env=env, capture_output=True, text=True, timeout=120)
    after = pending_topics()
    check("chạy xong exit 0", run.returncode == 0, run.stderr[-400:])
    check("câu hỏi 'chưa duyệt' ĐÃ ĐÓNG sau khi duyệt",
          "plan-SpaceX-2026-09-21-chua-duyet" not in after, str(after))
    check("câu hỏi ops-autofix VẪN MỞ (cần người xác nhận bot chạy lại)",
          "ops-autofix-unresolved: run-bot-fail-SpaceX-2026-09-21" in after and
          "ops-autofix-unresolved: plan-SpaceX-2026-09-21-chua-duyet" in after, str(after))
    check("in gợi ý đóng tay cho câu hỏi còn mở",
          "close_bus_question.py" in run.stdout, run.stdout[-400:])

    # 3. idempotent: chạy lại không hỏng, không đóng thêm gì
    run2 = subprocess.run(
        [sys.executable, str(ROOT / "bin" / "close_plan_approval_questions.py"),
         "SpaceX", "2026-09-21", "user (John) - selfcheck", "--root", str(root)],
        env=env, capture_output=True, text=True, timeout=120)
    check("chạy lại idempotent (exit 0, không đóng nhầm câu hỏi còn lại)",
          run2.returncode == 0 and
          "ops-autofix-unresolved: run-bot-fail-SpaceX-2026-09-21" in pending_topics(),
          run2.stdout[-300:])

print()
if FAILS:
    print(f"❌ FAIL {len(FAILS)}: {FAILS}")
    raise SystemExit(1)
print("✅ ALL PASS")
