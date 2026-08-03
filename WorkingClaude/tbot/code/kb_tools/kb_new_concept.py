#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create a new KB concept node (v1, status=unverified unless overridden).

Usage:
    kb_new_concept.py <slug> --title "..." --body-file body.md \\
        [--tags a,b] [--aliases a,b] [--related slug1,slug2] \\
        [--owner tbot] [--status unverified] [--author tbot] [--sources a,b]

Body can also be piped on stdin instead of --body-file.
"""
import argparse
import sys

import _bootstrap  # noqa: F401
import okf


def _csv(s):
    return [x.strip() for x in s.split(",") if x.strip()] if s else []


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slug")
    ap.add_argument("--title", required=True)
    ap.add_argument("--body-file")
    ap.add_argument("--tags", default="")
    ap.add_argument("--aliases", default="")
    ap.add_argument("--related", default="")
    ap.add_argument("--owner", default="tbot")
    ap.add_argument("--status", default="unverified", choices=okf.STATUSES)
    ap.add_argument("--author", default="tbot")
    ap.add_argument("--reason", default="initial creation")
    ap.add_argument("--sources", default="")
    args = ap.parse_args()

    body = open(args.body_file, encoding="utf-8").read() if args.body_file else sys.stdin.read()
    if not body.strip():
        raise SystemExit("empty body — pass --body-file or pipe content on stdin")

    node = okf.new_concept(
        args.slug, args.title, body,
        tags=_csv(args.tags), aliases=_csv(args.aliases), related=_csv(args.related),
        owner=args.owner, status=args.status, author=args.author,
        change_reason=args.reason, sources=_csv(args.sources),
    )
    print(f"created {args.slug} v1 (status={node['status']})")


if __name__ == "__main__":
    main()
