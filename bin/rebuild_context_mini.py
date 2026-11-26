#!/usr/bin/env python3
"""Refresh kb/context_taylor_mini.md if it carries a RECENT block; skip cleanly in static mode.

Since 2026-10-22, RECENT events live in kb/context_recent.md and hooks/session_start.sh injects
them directly for mini-pack agents as well. When context_taylor_mini.md has no
<!--RECENT-START-->...<!--RECENT-END--> marker, this helper is a no-op exit 0.
"""

import os
import re
import sys


def _read_version(root: str, pack_content: str) -> str:
    ver_path = os.path.join(root, "kb", "version.txt")
    if os.path.exists(ver_path):
        try:
            txt = open(ver_path, encoding="utf-8").read().strip()
            if txt.isdigit():
                return txt
        except OSError:
            pass
    ver_match = re.search(r"\(v(\d+)\)", pack_content[:200])
    return ver_match.group(1) if ver_match else "?"


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_recent = os.path.join(root, "kb", "context_recent.md")
    src_pack = os.path.join(root, "kb", "context_pack.md")
    dst = os.path.join(root, "kb", "context_taylor_mini.md")

    if not os.path.exists(dst):
        print(f"[rebuild_context_mini] {dst} not found, skipping", file=sys.stderr)
        return

    with open(dst, encoding="utf-8") as f:
        dst_content = f.read()

    if not re.search(r"<!--RECENT-START-->.*?<!--RECENT-END-->", dst_content, re.DOTALL):
        print("[rebuild_context_mini] context_taylor_mini.md is static (RECENT injected at SessionStart), skipping")
        return

    pack_content = ""
    if os.path.exists(src_pack):
        with open(src_pack, encoding="utf-8") as f:
            pack_content = f.read()

    recent_block = ""
    if os.path.exists(src_recent):
        with open(src_recent, encoding="utf-8") as f:
            recent_raw = f.read().strip()
        if recent_raw:
            recent_block = f"\n{recent_raw}\n"

    if not recent_block and pack_content:
        recent_match = re.search(r"<!--RECENT-START-->(.*?)<!--RECENT-END-->", pack_content, re.DOTALL)
        if recent_match:
            recent_block = recent_match.group(1)

    if not recent_block:
        print("[rebuild_context_mini] No RECENT content in context_recent.md or context_pack.md, skipping", file=sys.stderr)
        return

    ver = _read_version(root, pack_content)

    new_dst = re.sub(
        r"<!--RECENT-START-->.*?<!--RECENT-END-->",
        f"<!--RECENT-START-->{recent_block}<!--RECENT-END-->",
        dst_content,
        flags=re.DOTALL,
    )
    new_dst = re.sub(r"\(v\d+\)", f"(v{ver})", new_dst, count=1)

    if new_dst == dst_content:
        print(f"[rebuild_context_mini] no change (v{ver})")
        return

    with open(dst, "w", encoding="utf-8") as f:
        f.write(new_dst)
    print(f"[rebuild_context_mini] updated RECENT block → v{ver}")


if __name__ == "__main__":
    main()
