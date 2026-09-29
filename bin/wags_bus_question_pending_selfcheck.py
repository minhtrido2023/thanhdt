#!/usr/bin/env python3
"""Selfcheck cho bin/wags_bus_question_pending.py (CLI trực tiếp, không qua khối
wags_autofix.sh — case dedup/new-cluster ở wags_arch_review_round2_selfcheck.py đã phủ
đường tích hợp thật; file này phủ các nhánh CHƯA được test ở đó: pending thật, đã đóng,
chưa từng tồn tại, và nhánh fail-closed khi audit lỗi (usage sai / thiếu bus_question_audit.py).

Chạy: python3 bin/wags_bus_question_pending_selfcheck.py   (exit 0 = PASS, 1 = FAIL)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "bin" / "wags_bus_question_pending.py"
AUDIT = ROOT / "bin" / "bus_question_audit.py"

fails = []


def check(name, cond, detail=""):
    if cond:
        print(f"  PASS  {name}")
    else:
        fails.append(f"{name} — {detail}")
        print(f"  FAIL  {name} — {detail}")


def mksandbox(events, with_audit=True):
    d = tempfile.mkdtemp(prefix="wags_pending_selfcheck_")
    os.makedirs(os.path.join(d, "bin"))
    os.makedirs(os.path.join(d, "bus", "inbox"))
    if with_audit:
        shutil.copy2(AUDIT, os.path.join(d, "bin", "bus_question_audit.py"))
    with open(os.path.join(d, "bus", "inbox", "Wags.jsonl"), "w", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    return d


def run(root, agent, topic):
    p = subprocess.run([sys.executable, str(SCRIPT), root, agent, topic],
                        capture_output=True, text=True, timeout=30)
    return p.returncode, p.stderr


def case_open_question_is_pending():
    d = mksandbox([{"agent_id": "Wags", "event_type": "question", "topic": "foo-topic",
                     "ts": "2026-09-19T01:00:00Z", "payload": {}, "event_id": "q1"}])
    try:
        rc, err = run(d, "Wags", "foo-topic")
        check("câu hỏi mở, chưa có resolver: exit=0 (pending)", rc == 0, f"rc={rc} err={err}")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def case_closed_question_is_not_pending():
    d = mksandbox([
        {"agent_id": "Wags", "event_type": "question", "topic": "foo-topic",
         "ts": "2026-09-19T01:00:00Z", "payload": {}, "event_id": "q1"},
        {"agent_id": "Mike", "event_type": "answer", "topic": "foo-topic",
         "ts": "2026-09-19T02:00:00Z", "payload": {"decided_by": "user"}, "event_id": "a1"},
    ])
    try:
        rc, err = run(d, "Wags", "foo-topic")
        check("câu hỏi đã có answer sau ts: exit=1 (không còn pending)", rc == 1, f"rc={rc} err={err}")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def case_never_existed_is_not_pending():
    d = mksandbox([])
    try:
        rc, err = run(d, "Wags", "chua-tung-co")
        check("topic chưa từng tồn tại: exit=1 (không pending)", rc == 1, f"rc={rc} err={err}")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def case_wrong_agent_does_not_match():
    # bus_question_audit.py suy ra "agent" của 1 câu hỏi từ TÊN FILE inbox
    # (bus/inbox/<Agent>.jsonl), không phải field agent_id trong event — nên để mô phỏng
    # đúng "câu hỏi của agent khác", phải ghi vào file inbox CỦA agent đó, không phải chỉnh
    # field agent_id trong cùng 1 file Wags.jsonl (làm vậy vẫn tính là agent=Wags).
    d = mksandbox([])
    with open(os.path.join(d, "bus", "inbox", "Mike.jsonl"), "w", encoding="utf-8") as f:
        f.write(json.dumps({"agent_id": "Mike", "event_type": "question", "topic": "foo-topic",
                             "ts": "2026-09-19T01:00:00Z", "payload": {}, "event_id": "q1"},
                            ensure_ascii=False) + "\n")
    try:
        rc, err = run(d, "Wags", "foo-topic")
        check("cùng topic nhưng câu hỏi nằm ở inbox agent KHÁC: exit=1 (không khớp nhầm chéo agent)",
              rc == 1, f"rc={rc} err={err}")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def case_audit_missing_fails_closed_as_not_pending():
    # bus_question_audit.py bị thiếu ⇒ không đọc được trạng thái thật ⇒ PHẢI trả "không
    # pending" (fail-closed như "không có bằng chứng đang pending", để caller đi nhánh mở
    # escalate thay vì im lặng nuốt mất — không được lẫn với "chắc chắn đã đóng").
    d = mksandbox([{"agent_id": "Wags", "event_type": "question", "topic": "foo-topic",
                     "ts": "2026-09-19T01:00:00Z", "payload": {}, "event_id": "q1"}],
                  with_audit=False)
    try:
        rc, err = run(d, "Wags", "foo-topic")
        check("bus_question_audit.py bị thiếu: exit=1 (fail-closed = không pending), không traceback vỡ ra",
              rc == 1 and "Traceback" not in err, f"rc={rc} err={err}")
        check("bus_question_audit.py bị thiếu: CÓ ghi dấu vết AUDIT_UNREADABLE ra stderr (không im "
              "lặng lẫn với 'đã đóng thật' — arch-review coord-2026-09-19 round 3)",
              "AUDIT_UNREADABLE" in err, f"err={err}")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def case_bad_usage_exits_nonzero():
    p = subprocess.run([sys.executable, str(SCRIPT), "only-one-arg"],
                        capture_output=True, text=True, timeout=30)
    check("gọi thiếu tham số: exit != 0, có usage trên stderr",
          p.returncode != 0 and "usage" in p.stderr, f"rc={p.returncode} err={p.stderr}")


def main():
    print("wags_bus_question_pending_selfcheck: CLI trực tiếp (pending/closed/never/fail-closed)")
    for fn in (case_open_question_is_pending, case_closed_question_is_not_pending,
               case_never_existed_is_not_pending, case_wrong_agent_does_not_match,
               case_audit_missing_fails_closed_as_not_pending, case_bad_usage_exits_nonzero):
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
