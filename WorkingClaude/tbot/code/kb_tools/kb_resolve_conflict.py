#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Close a conflict review: winner -> verified, loser -> rejected.

Usage:
    kb_resolve_conflict.py <review_id> --keep <slug> --reject <slug> --by <who> [--note "..."]
"""
import argparse

import _bootstrap  # noqa: F401
import okf


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("review_id")
    ap.add_argument("--keep", required=True)
    ap.add_argument("--reject", required=True)
    ap.add_argument("--by", required=True)
    ap.add_argument("--note", default="")
    args = ap.parse_args()

    okf.close_conflict_review(args.review_id, args.keep, args.reject, args.by, args.note)
    okf.set_current_status(args.keep, "verified", verified_by=args.by)
    okf.set_current_status(args.reject, "rejected")
    okf.append_changelog(args.keep, f"conflict {args.review_id} resolved: kept, verified by {args.by}")
    okf.append_changelog(args.reject, f"conflict {args.review_id} resolved: rejected by {args.by}")
    print(f"{args.review_id}: kept={args.keep} (verified), rejected={args.reject}")


if __name__ == "__main__":
    main()
