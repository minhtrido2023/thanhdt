#!/usr/bin/env python3
"""Selfcheck surface_question.py + vòng khép kín: tin đăng có thẻ ⇒ cog ghi surfaced ⇒ reply 'A' khớp (tmp root)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from decision_inbox_selfcheck import Env  # noqa: E402

TOOL = HERE / "surface_question.py"
N = [0, 0]
NOTIFY = """#!/usr/bin/env python3
import json, pathlib, sys
pathlib.Path(__file__).resolve().parents[1].joinpath("posted.jsonl").open("a", encoding="utf-8").write(
    json.dumps({"argv": sys.argv[1:]}, ensure_ascii=False) + "\\n")
"""


def check(name, cond, detail=""):
    N[0] += 1
    if not cond:
        N[1] += 1
        print(f"FAIL {name}: {detail}", file=sys.stderr)


def run(root, *args):
    return subprocess.run([sys.executable, str(TOOL), *args, "--root", str(root)], capture_output=True, text=True)


with tempfile.TemporaryDirectory() as td:
    e = Env(td)
    n = e.root / "bin" / "notify_thread.sh"
    n.write_text(NOTIFY, encoding="utf-8")
    n.chmod(0o755)
    qa = e.q("Mike", "docs-surface", ["A: giữ", "B: đổi"], question="Giữ hay đổi?")
    qb = e.q("Taylor", "docs-infer", ["giữ nguyên", "đổi"])
    e.q("Mike", "no-options-question", [])
    r = run(e.root, "--list")
    check("L1 --list: chỉ câu có options, kèm thẻ", r.returncode == 0 and f"[#{qa['tag']}] Mike/docs-surface" in r.stdout
          and f"[#{qb['tag']}]" in r.stdout and "no-options" not in r.stdout, r.stdout + r.stderr)
    r = run(e.root, "Mike/docs-surface", "--tag")
    check("T1 --tag in đúng thẻ", r.stdout.strip() == f"[#{qa['tag']}]", r.stdout + r.stderr)
    r = run(e.root, "Mike/docs-surface", "--dry-run")
    check("D1 dry-run: có thẻ, câu hỏi, 2 option, hướng dẫn trả lời", f"[#{qa['tag']}]" in r.stdout and "Giữ hay đổi?" in r.stdout
          and "A: giữ" in r.stdout and "B: đổi" in r.stdout and "reply" in r.stdout, r.stdout)
    check("D1 dry-run không đăng", not (e.root / "posted.jsonl").exists())
    r = run(e.root, "Taylor/docs-infer", "--dry-run")
    check("D2 nhãn suy ra ⇒ thêm 'A: '/'B: '", "A: giữ nguyên" in r.stdout and "B: đổi" in r.stdout, r.stdout)
    r = run(e.root, "Mike/khong-co", "--dry-run")
    check("X1 câu không tồn tại ⇒ rc=1", r.returncode == 1 and "không có câu hỏi MỞ" in r.stderr, r.stderr)
    r = run(e.root, "Mike/no-options-question", "--dry-run")
    check("X2 câu không có options ⇒ rc=1", r.returncode == 1, r.stderr)
    r = run(e.root, "Mike/docs-surface", "--channel", "architecture")
    posted = [json.loads(x) for x in (e.root / "posted.jsonl").read_text(encoding="utf-8").splitlines()]
    check("P1 đăng qua notify_thread.sh: msg có thẻ + tên kênh ở arg 2", r.returncode == 0 and len(posted) == 1
          and f"[#{qa['tag']}]" in posted[0]["argv"][0] and posted[0]["argv"][1] == "architecture", str(posted))
    # vòng khép kín: tin bot (nội dung đúng như đã đăng) ⇒ surfaced ⇒ reply 'A' khớp, kể cả khi có 2 câu mở
    e.bot("b1", "c1", qa["tag"])
    e.run({"kind": "bot_message", "message_id": "b2", "channel_id": "c1", "content": posted[0]["argv"][0]})
    res = e.user("m1", "c1", "A", ref="b2")
    check("C1 reply 'A' vào tin đã đăng ⇒ đóng đúng câu, matched_by=reply_to", res["outcome"] == "closed"
          and res["ref"] == "Mike/docs-surface" and res["matched_by"] == "reply_to", str(res))
    check("C2 câu kia không bị đụng", len(e.answers("docs-infer")) == 0)

if N[1]:
    print(f"surface_question_selfcheck: {N[0] - N[1]}/{N[0]} PASS, {N[1]} FAIL", file=sys.stderr)
    sys.exit(1)
print(f"surface_question_selfcheck: {N[0]}/{N[0]} PASS")
