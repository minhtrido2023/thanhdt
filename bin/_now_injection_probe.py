#!/usr/bin/env python3
"""Trả về 0 nếu LƯỢT PROMPT NGƯỜI DÙNG GẦN NHẤT trong transcript có marker "[now:".

Vì sao không dùng `tail -n 30 | grep` như bản đầu (sửa 2026-08-22, weekly ops audit):
JSONL đếm theo DÒNG BẢN GHI, không theo LƯỢT. Một lượt Mike gọi nhiều tool sinh hàng chục
dòng assistant/attachment, nên "30 dòng cuối" của một phiên bận rộn có thể KHÔNG chứa lượt
prompt nào — đo thật trên c31c975c...jsonl: prompt cuối có "[now:" nằm ở dòng 377/409, tức
dòng thứ 33 từ cuối ⇒ FAIL GIẢ trong khi injection hoàn toàn đúng. Cái cần khẳng định là
"prompt tới model CÓ mang giờ", nên phải neo vào chính bản ghi prompt.

Bỏ qua bản ghi do /compact sinh ra (sửa 2026-10-24, selfcheck-red sweep): một lần compact ghi
4 bản ghi role=user — summary (isCompactSummary), caveat (isMeta), <command-name>/compact,
<local-command-stdout> — không cái nào đi qua UserPromptSubmit nên không bao giờ có "[now:".
Đo thật trên 0f99ac36...jsonl: 5/5 prompt Discord thật có "[now:", nhưng 2 lần compact lúc
16:45Z 23/10 nằm cuối file ⇒ cả 3 topic FAIL GIẢ.
"""
import json
import sys

_LOCAL_COMMAND_PREFIXES = ("<command-name>", "<local-command-stdout>", "<local-command-caveat>")


def is_real_prompt(d):
    m = d.get("message") or {}
    if m.get("role") != "user":
        return False
    if d.get("isMeta") or d.get("isCompactSummary"):
        return False
    c = m.get("content")
    if isinstance(c, str):
        return not c.lstrip().startswith(_LOCAL_COMMAND_PREFIXES)
    if isinstance(c, list):
        texts = [b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text"]
        return bool(texts) and not texts[0].lstrip().startswith(_LOCAL_COMMAND_PREFIXES)
    return False


def prompt_text(d):
    c = d["message"]["content"]
    if isinstance(c, str):
        return c
    return " ".join(b.get("text", "") for b in c if isinstance(b, dict))


def main():
    path = sys.argv[1]
    last = None
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            if is_real_prompt(d):
                last = d
    if last is None:
        print("NO_PROMPT")
        return 2
    if "[now:" in prompt_text(last):
        print("OK")
        return 0
    print("NO_NOW")
    return 1


if __name__ == "__main__":
    sys.exit(main())
