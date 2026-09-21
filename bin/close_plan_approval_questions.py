#!/usr/bin/env python3
"""Đóng bus question "plan chưa duyệt" khi PLAN THẬT SỰ ĐÃ ĐƯỢC DUYỆT.

Vì sao cần (coord-2026-09-21): câu hỏi escalate của Winston mang topic
`plan-SpaceX-2026-09-21-chua-duyet`, còn đường duyệt ghi bus `decision` topic
`plan-approval-<ACC>-<DATE>`. Resolver của ops_health_check so theo topic/`resolves`
⇒ user duyệt 09:10 ICT, bot khớp 3/3 lệnh 09:15, mà checker 12:45 vẫn escalate → đốt
một job wags_autofix cho việc đã xong từ 3 tiếng trước.

NGUỒN SỰ THẬT LÀ ARTIFACT, KHÔNG PHẢI LỜI KHAI CỦA CALLER (arch-review vòng 1,
killer objection): 8/9 lần duyệt plan trong tháng 9 KHÔNG chạy qua
`approve_plan_simple.sh` (chỉ script đó ghi `approved_at`; 8 plan có `approved_by`
mà `approved_at=None` ⇒ duyệt bằng cách sửa JSON trực tiếp), GỒM CẢ lần duyệt gây ra
sự cố này. Nên script MỞ chính file plan và chỉ đóng khi đọc được `approved_by`
non-empty; evidence trích từ giá trị ĐỌC ĐƯỢC, không bịa từ argv. Nhờ vậy nó đúng ở
CẢ HAI chỗ gọi: ngay sau khi duyệt (đường nhanh) và trong ops_health_check trước khi
escalate (đường bền — chỗ sự cố thật sự đi qua).

Phạm vi CỐ Ý HẸP — chỉ đóng câu hỏi mà "plan đã duyệt" LÀ câu trả lời đầy đủ:
  - topic chứa cả <ACC> và <DATE>, VÀ khớp `chua-duyet / chua duyet / not_approved`;
  - LOẠI TRỪ lớp `ops-autofix-unresolved:` — run-bot-fail cùng ngày có thể có root
    cause khác hẳn (2026-09-17: funding-gate double-count, không liên quan duyệt), và
    kể cả khi đúng root cause là duyệt thì "đã duyệt" chưa chứng minh bot đã chạy lại
    thành công. Lớp đó chỉ IN GỢI Ý để người đóng tay sau khi xem journal.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
APPROVAL_SHAPE = re.compile(r"chua[-_ ]?duyet|not[-_ ]?approved", re.IGNORECASE)
AUTOFIX_PREFIX = "ops-autofix-unresolved:"
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


def pending(root: Path) -> list[dict]:
    env = dict(os.environ)
    env["BUS_AUDIT_ROOT"] = str(root)
    run = subprocess.run(
        [sys.executable, str(ROOT / "bin" / "bus_question_audit.py"), "--json"],
        env=env, capture_output=True, text=True, timeout=30,
    )
    return json.loads(run.stdout).get("pending", [])


def classify(questions: list[dict], account: str = "", date: str = "") -> tuple[list, list]:
    """→ (ứng viên đóng tự động, chỉ gợi ý). account/date rỗng = không lọc thêm."""
    auto, hint = [], []
    for q in questions:
        topic = str(q.get("topic") or "")
        if not APPROVAL_SHAPE.search(topic):
            continue
        if account and account not in topic:
            continue
        if date and date not in topic:
            continue
        (hint if topic.startswith(AUTOFIX_PREFIX) else auto).append(q)
    return auto, hint


def topic_target(topic: str, plan_dir: Path) -> tuple[str, str] | None:
    """Suy (account, date) từ topic — chỉ nhận account có FILE PLAN thật cho ngày đó."""
    m = DATE_RE.search(topic)
    if not m:
        return None
    date = m.group(0)
    for p in sorted(plan_dir.glob(f"plan_*_{date}.json")):
        acc = p.name[len("plan_"):-len(f"_{date}.json")]
        if acc and acc in topic:
            return acc, date
    return None


def approval_evidence(plan_dir: Path, account: str, date: str) -> tuple[str, str] | None:
    """Đọc plan THẬT. → (approved_by, dòng evidence) hoặc None nếu chưa duyệt/không đọc được."""
    path = plan_dir / f"plan_{account}_{date}.json"
    try:
        plan = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"⚠ không đọc được {path} ({exc}) — KHÔNG đóng gì.")
        return None
    # `approved_by_user`: biến thể preflight_check.sh:63 / merge_park_orders.py:127 cũng
    # coi là đã duyệt — phải khớp cùng luật với checker, nếu không hai bên trôi lệch nhau.
    by = next((str(plan.get(k) or "").strip()
               for k in ("approved_by", "approved_by_user")
               if str(plan.get(k) or "").strip()), "")
    if not by:
        return None
    at = plan.get("approved_at")
    return by, (f"{path} đọc lúc đóng: approved_by={by!r} approved_at={at!r}, "
                f"orders={len(plan.get('orders') or [])}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--account", default="", help="lọc theo account (rỗng = mọi account)")
    ap.add_argument("--date", default="", help="lọc theo ngày plan (rỗng = mọi ngày)")
    ap.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    ap.add_argument("--plan-dir", type=Path, default=None, help=argparse.SUPPRESS)
    a = ap.parse_args()
    plan_dir = a.plan_dir if a.plan_dir is not None else a.root.parent / "data" / "trade_plans"

    try:
        qs = pending(a.root)
    except Exception as exc:
        print(f"⚠ không đọc được backlog câu hỏi ({exc}) — bỏ qua bước đóng tự động.")
        return 0

    auto, hint = classify(qs, a.account, a.date)
    failed = closed = 0
    for q in auto:
        topic = str(q.get("topic") or "")
        ref = f"{q.get('agent')}/{topic}"
        target = topic_target(topic, plan_dir)
        if not target:
            print(f"ℹ️ bỏ qua {ref}: không suy được plan (account/ngày) khớp file thật.")
            continue
        acc, date = target
        ev = approval_evidence(plan_dir, acc, date)
        if ev is None:
            print(f"ℹ️ bỏ qua {ref}: plan {acc} {date} CHƯA có approved_by — câu hỏi còn đúng.")
            continue
        by, evidence = ev
        run = subprocess.run(
            [sys.executable, str(ROOT / "bin" / "close_bus_question.py"), ref,
             "--resolution", f"Plan {acc} {date} ĐÃ ĐƯỢC DUYỆT: {by}.",
             "--evidence", evidence, "--decided-by-user", "--actor", "Mike",
             "--root", str(a.root)],
            capture_output=True, text=True, timeout=60)
        tail = ((run.stdout or "") + (run.stderr or "")).strip()
        # FAIL-LOUD: nuốt lỗi ở đây = câu hỏi vẫn treo mà không ai biết, đúng cái vòng
        # escalate-vô-ích mà thay đổi này sinh ra để diệt.
        if run.returncode != 0 or "CLOSED" not in tail:
            failed += 1
            print(f"❌ KHÔNG đóng được {ref} (rc={run.returncode}) — đóng TAY bằng "
                  f"mike/bin/close_bus_question.py. Chi tiết: "
                  f"{tail.splitlines()[-1] if tail else '(im lặng)'}")
        else:
            closed += 1
            print(tail.splitlines()[-1])
    for q in hint:
        ref = f"{q.get('agent')}/{q.get('topic')}"
        print(f"ℹ️ CÒN MỞ (không tự đóng — phải xem bot đã chạy lại chưa): {ref}\n"
              f"   Sau khi xác nhận journal có fill, đóng bằng:\n"
              f"   mike/bin/close_bus_question.py \"{ref}\" --resolution '...' --evidence '...'")
    if not auto and not hint:
        print("ℹ️ không có câu hỏi 'plan chưa duyệt' nào đang mở"
              + (f" cho {a.account} {a.date}".rstrip() if (a.account or a.date) else "")
              + " — không cần đóng.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
