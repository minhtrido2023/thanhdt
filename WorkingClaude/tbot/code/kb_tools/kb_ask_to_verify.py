#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Open a verification request for a concept (does not change its status).

Usage:
    kb_ask_to_verify.py <slug> --note "what needs checking" [--by tbot]
"""
import argparse

import _bootstrap  # noqa: F401
import okf


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slug")
    ap.add_argument("--note", required=True)
    ap.add_argument("--by", default="tbot")
    args = ap.parse_args()

    if not okf.concept_exists(args.slug):
        raise SystemExit(f"no such concept: {args.slug}")

    req_id, path = okf.open_ask_to_verify(args.slug, args.note, requested_by=args.by)
    print(f"opened ask-to-verify {req_id} -> {path}")


if __name__ == "__main__":
    main()
