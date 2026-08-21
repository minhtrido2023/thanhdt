#!/usr/bin/env python3
"""Trả về 0 nếu LƯỢT PROMPT NGƯỜI DÙNG GẦN NHẤT trong transcript có marker "[now:".

Vì sao không dùng `tail -n 30 | grep` như bản đầu (sửa 2026-08-22, weekly ops audit):
JSONL đếm theo DÒNG BẢN GHI, không theo LƯỢT. Một lượt Mike gọi nhiều tool sinh hàng chục
dòng assistant/attachment, nên "30 dòng cuối" của một phiên bận rộn có thể KHÔNG chứa lượt
prompt nào — đo thật trên c31c975c...jsonl: prompt cuối có "[now:" nằm ở dòng 377/409, tức
dòng thứ 33 từ cuối ⇒ FAIL GIẢ trong khi injection hoàn toàn đúng. Cái cần khẳng định là
"prompt tới model CÓ mang giờ", nên phải neo vào chính bản ghi prompt.
"""
import json
import sys


def is_real_prompt(d):
    m = d.get("message") or {}
    if m.get("role") != "user":
        return False
    c = m.get("content")
    if isinstance(c, str):
        return True
    if isinstance(c, list):
        return any(isinstance(b, dict) and b.get("type") == "text" for b in c)
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
