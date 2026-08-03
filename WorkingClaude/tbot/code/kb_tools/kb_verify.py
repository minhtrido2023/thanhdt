#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mark a concept's current version verified, closing any open ask-to-verify request.

Usage:
    kb_verify.py <slug> --by <who confirmed it> [--note "how it was confirmed"]
"""
import argparse

import _bootstrap  # noqa: F401
import okf


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slug")
    ap.add_argument("--by", required=True)
    ap.add_argument("--note", default="")
    args = ap.parse_args()

    node = okf.set_current_status(args.slug, "verified", verified_by=args.by)
    closed = 0
    for path, _meta in okf.find_open_ask_to_verify(args.slug):
        okf.close_ask_to_verify(path, args.by, args.note)
        closed += 1
    okf.append_changelog(args.slug, f"v{node['current_version']} verified by {args.by}. {args.note}".strip())
    print(f"{args.slug}: v{node['current_version']} -> verified "
          f"(closed {closed} open ask-to-verify request(s))")


if __name__ == "__main__":
    main()
