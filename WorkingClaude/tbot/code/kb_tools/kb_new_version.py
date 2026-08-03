#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add a new version to an existing concept, superseding the current one.

The new version starts at status=unverified by default — editing content is a
new claim that hasn't been re-verified yet, even if the prior version was
verified. Pass --status verified only if you're re-affirming with the same
evidence (rare; prefer kb_verify.py after review instead).

Usage:
    kb_new_version.py <slug> --body-file body.md --reason "why this changed" \\
        [--author tbot] [--status unverified] [--sources a,b]
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
    ap.add_argument("--body-file")
    ap.add_argument("--reason", required=True)
    ap.add_argument("--author", default="tbot")
    ap.add_argument("--status", default="unverified", choices=okf.STATUSES)
    ap.add_argument("--sources", default="")
    args = ap.parse_args()

    body = open(args.body_file, encoding="utf-8").read() if args.body_file else sys.stdin.read()
    if not body.strip():
        raise SystemExit("empty body — pass --body-file or pipe content on stdin")

    node = okf.new_version(args.slug, body, args.reason, author=args.author,
                            status=args.status, sources=_csv(args.sources))
    print(f"{args.slug}: now v{node['current_version']} (status={node['status']})")


if __name__ == "__main__":
    main()
