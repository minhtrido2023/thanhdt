#!/usr/bin/env python3
"""Đóng các bus question "plan chưa duyệt" ngay khi plan ĐƯỢC DUYỆT.

Vì sao cần (coord-2026-09-21): `approve_plan_simple.sh` đã ghi bus một `decision`
topic `plan-approval-<ACC>-<DATE>`, nhưng câu hỏi của Winston mang topic KHÁC
(`plan-SpaceX-2026-09-21-chua-duyet`). Resolver của ops_health_check so theo TOPIC
(hoặc field `resolves`), nên duyệt xong câu hỏi vẫn "pending" ⇒ 12:45 checker vẫn
escalate, đốt 1 job wags_autofix cho việc user đã quyết từ 3 tiếng trước.

Phạm vi CỐ Ý HẸP — chỉ đóng câu hỏi mà "plan được duyệt" LÀ câu trả lời đầy đủ:
  - topic chứa cả <ACC> và <DATE>, VÀ khớp `chua-duyet / chua duyet / not_approved`;
  - LOẠI TRỪ lớp `ops-autofix-unresolved:` — một run-bot-fail cùng ngày có thể có
    root cause khác hẳn (2026-09-17: funding-gate double-count, không liên quan
    duyệt), và kể cả khi đúng root cause là duyệt thì lúc này bot CHƯA chạy lại,
    nên "đã duyệt" chưa chứng minh được là hết sự cố. Với lớp đó chỉ IN GỢI Ý để
    người đóng bằng tay sau khi xem journal.

Không đóng được thì KHÔNG fail lệnh duyệt (exit 0) — duyệt plan là việc chính.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
APPROVAL_SHAPE = re.compile(r"chua[-_ ]?duyet|not[-_ ]?approved", re.IGNORECASE)
AUTOFIX_PREFIX = "ops-autofix-unresolved:"


def pending(root: Path) -> list[dict]:
    env = dict(os.environ)
    env["BUS_AUDIT_ROOT"] = str(root)
    run = subprocess.run(
        [sys.executable, str(ROOT / "bin" / "bus_question_audit.py"), "--json"],
        env=env, capture_output=True, text=True, timeout=30,
    )
    return json.loads(run.stdout).get("pending", [])


def classify(questions: list[dict], account: str, date: str) -> tuple[list[dict], list[dict]]:
    """→ (đóng tự động, chỉ gợi ý)."""
    auto, hint = [], []
    for q in questions:
        topic = str(q.get("topic") or "")
        if account not in topic or date not in topic:
            continue
        if not APPROVAL_SHAPE.search(topic):
            continue
        (hint if topic.startswith(AUTOFIX_PREFIX) else auto).append(q)
    return auto, hint


def main() -> int:
    if len(sys.argv) < 4:
        print("usage: close_plan_approval_questions.py <account> <date> <approved_by> [--root DIR]",
              file=sys.stderr)
        return 2
    account, date, approved_by = sys.argv[1], sys.argv[2], sys.argv[3]
    root = Path(sys.argv[5]) if len(sys.argv) > 5 and sys.argv[4] == "--root" else ROOT

    try:
        qs = pending(root)
    except Exception as exc:
        print(f"⚠ không đọc được backlog câu hỏi ({exc}) — bỏ qua bước đóng tự động.")
        return 0

    auto, hint = classify(qs, account, date)
    for q in auto:
        ref = f"{q.get('agent')}/{q.get('topic')}"
        cmd = [sys.executable, str(ROOT / "bin" / "close_bus_question.py"), ref,
               "--resolution", f"Plan {account} {date} ĐÃ ĐƯỢC DUYỆT: {approved_by}.",
               "--evidence", f"data/trade_plans/plan_{account}_{date}.json approved_by={approved_by!r}"
                             f" (ghi bởi bin/approve_plan_simple.sh)",
               "--decided-by-user", "--actor", "Mike",
               "--root", str(root)]
        run = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        tail = ((run.stdout or "") + (run.stderr or "")).strip()
        # FAIL-LOUD: nuốt lỗi ở đây = câu hỏi vẫn treo mà không ai biết, đúng cái
        # vòng escalate-vô-ích mà thay đổi này sinh ra để diệt.
        if run.returncode != 0 or "CLOSED" not in tail:
            print(f"❌ KHÔNG đóng được {ref} (rc={run.returncode}) — đóng TAY bằng "
                  f"mike/bin/close_bus_question.py. Chi tiết: {tail.splitlines()[-1] if tail else '(im lặng)'}")
        else:
            print(tail.splitlines()[-1])
    for q in hint:
        ref = f"{q.get('agent')}/{q.get('topic')}"
        print(f"ℹ️ CÒN MỞ (không tự đóng — phải xem bot đã chạy lại chưa): {ref}\n"
              f"   Sau khi xác nhận journal có fill, đóng bằng:\n"
              f"   mike/bin/close_bus_question.py \"{ref}\" --resolution '...' --evidence '...'")
    if not auto and not hint:
        print("ℹ️ không có câu hỏi 'plan chưa duyệt' nào đang mở cho "
              f"{account} {date} — không cần đóng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
