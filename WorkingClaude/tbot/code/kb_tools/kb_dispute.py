#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Open a conflict review between two concepts and mark both current versions disputed.

Usage:
    kb_dispute.py <slug_a> <slug_b> --reason "why they contradict" [--by tbot]
"""
import argparse

import _bootstrap  # noqa: F401
import okf


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slug_a")
    ap.add_argument("slug_b")
    ap.add_argument("--reason", required=True)
    ap.add_argument("--by", default="tbot")
    args = ap.parse_args()

    for slug in (args.slug_a, args.slug_b):
        if not okf.concept_exists(slug):
            raise SystemExit(f"no such concept: {slug}")

    review_id, path = okf.open_conflict_review(args.slug_a, args.slug_b, args.reason,
                                                opened_by=args.by)
    okf.set_current_status(args.slug_a, "disputed")
    okf.set_current_status(args.slug_b, "disputed")
    okf.append_changelog(args.slug_a, f"disputed vs {args.slug_b} — review {review_id}")
    okf.append_changelog(args.slug_b, f"disputed vs {args.slug_a} — review {review_id}")
    print(f"opened conflict review {review_id} -> {path}")
    print(f"{args.slug_a} and {args.slug_b}: current version -> disputed")


if __name__ == "__main__":
    main()
