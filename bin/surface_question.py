#!/usr/bin/env python3
"""surface_question.py — đưa 1 câu hỏi bus lên Discord KÈM thẻ `[#q<6hex>]` để Decision Inbox khớp được.

Vì sao: "A" trần luôn nhập nhằng khi nhiều câu mở cùng lúc. Cog (decision_inbox_cog.py) ghi nhận mọi tin của BOT có
thẻ `[#q…]` ⇒ map message_id → câu hỏi ⇒ user *reply* thẳng tin đó (hoặc gõ `A #q…`) là khớp tuyệt đối.
Mọi tin Mike/agent gửi user để hỏi 1 câu bus PHẢI mang thẻ này (dùng script này, hoặc `--tag` lấy thẻ dán vào tay).

  surface_question.py Agent/topic --channel <tên trong kb/discord_channels.json>   # đăng
  surface_question.py Agent/topic --dry-run                                         # chỉ in tin sẽ đăng
  surface_question.py Agent/topic --tag                                             # chỉ in thẻ
  surface_question.py --list                                                        # mọi câu mở có options + thẻ
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import decision_inbox as di  # noqa: E402


def _opts(q: dict) -> list[str]:
    """Option đã mang nhãn tường minh thì giữ nguyên; nhãn suy ra thì thêm `A: ` phía trước."""
    return [(txt if not q["labels_inferred"] else f"{lab}: {txt}")[:300] for lab, txt in q["labels"].items()]


def compose(q: dict) -> str:
    head = str(q["payload"].get("question") or q["payload"].get("summary") or "")[:500]
    lines = [f"❓ {q['ref']} [#{q['tag']}]"]
    if head:
        lines.append(head)
    lines += _opts(q)
    lines.append(f"Trả lời: reply thẳng tin này với chữ cái (vd `A`), hoặc gõ `A #{q['tag']}`.")
    return "\n".join(lines)[:1900]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("ref", nargs="?", help="Agent/topic của câu hỏi đang mở")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--tag", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--channel", default="", help="TÊN kênh trong kb/discord_channels.json (bỏ trống ⇒ $DISCORD_THREAD_ID)")
    ap.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    a = ap.parse_args()
    pending = [q for q in di.load_pending(a.root) if q["labels"]]
    if a.list:
        for q in pending:
            print(f"[#{q['tag']}] {q['ref']} risk={q['risk']} options={'/'.join(q['labels'])}")
        return 0
    if not a.ref:
        ap.error("cần Agent/topic (hoặc --list)")
    hits = [q for q in pending if q["ref"] == a.ref]
    if not hits:
        print(f"surface_question: không có câu hỏi MỞ có options tên {a.ref!r}", file=sys.stderr)
        return 1
    if len(hits) > 1:
        print(f"surface_question: {a.ref!r} có {len(hits)} bản đang mở — đóng bớt bản cũ trước", file=sys.stderr)
        return 1
    q = hits[0]
    if any(o["tag"] == q["tag"] and o is not q for o in pending):
        print(f"surface_question: thẻ #{q['tag']} va chạm với câu khác — không đăng", file=sys.stderr)
        return 1
    if a.tag:
        print(f"[#{q['tag']}]")
        return 0
    msg = compose(q)
    if a.dry_run:
        print(msg)
        return 0
    cmd = [str(a.root / "bin" / "notify_thread.sh"), msg] + ([a.channel] if a.channel else [])
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    sys.stdout.write(r.stdout)
    sys.stderr.write(r.stderr)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
