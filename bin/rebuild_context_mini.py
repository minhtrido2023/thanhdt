#!/usr/bin/env python3
"""Rebuild kb/context_taylor_mini.md: freshen RECENT block from context_pack.md each consolidate run.

Only the <!--RECENT-START-->...<!--RECENT-END--> block and the version tag in the title are
updated. All other content in context_taylor_mini.md is maintained manually (rarely changes;
weekly KB audit-lens catches drift).
"""

import re
import sys
import os


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src = os.path.join(root, 'kb/context_pack.md')
    dst = os.path.join(root, 'kb/context_taylor_mini.md')

    if not os.path.exists(src):
        print(f'[rebuild_context_mini] {src} not found, skipping', file=sys.stderr)
        return
    if not os.path.exists(dst):
        print(f'[rebuild_context_mini] {dst} not found, skipping', file=sys.stderr)
        return

    with open(src, encoding='utf-8') as f:
        src_content = f.read()
    with open(dst, encoding='utf-8') as f:
        dst_content = f.read()

    # Extract RECENT block from context_pack.md
    recent_match = re.search(r'<!--RECENT-START-->(.*?)<!--RECENT-END-->', src_content, re.DOTALL)
    if not recent_match:
        print('[rebuild_context_mini] No RECENT block in context_pack.md, skipping', file=sys.stderr)
        return
    recent_block = recent_match.group(1)

    # Extract version from context_pack.md first line
    ver_match = re.search(r'\(v(\d+)\)', src_content[:200])
    ver = ver_match.group(1) if ver_match else '?'

    # Replace RECENT block in mini file
    new_dst = re.sub(
        r'<!--RECENT-START-->.*?<!--RECENT-END-->',
        f'<!--RECENT-START-->{recent_block}<!--RECENT-END-->',
        dst_content,
        flags=re.DOTALL,
    )

    # Update version in title line (first occurrence only)
    new_dst = re.sub(r'\(v\d+\)', f'(v{ver})', new_dst, count=1)

    if new_dst == dst_content:
        print(f'[rebuild_context_mini] no change (v{ver})')
        return

    with open(dst, 'w', encoding='utf-8') as f:
        f.write(new_dst)
    print(f'[rebuild_context_mini] updated RECENT block → v{ver}')


if __name__ == '__main__':
    main()
