#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate every concept: schema conformance, version-chain integrity, alias collisions.

Exit 0 with no output on a clean KB; exit 1 and print every problem found
otherwise. Intended to run before trusting the KB (and as a pre-commit gate,
same discipline as this repo's shellcheck_gate.sh for bash).

Usage:
    kb_lint.py
"""
import os

import _bootstrap  # noqa: F401
import okf


def check_concept(slug, node_schema, version_schema):
    errors = []
    node = okf.load_node(slug)
    for e in okf.validate_schema(node, node_schema):
        errors.append(f"{slug}/node.yaml: {e}")

    versions = okf.list_versions(slug)
    if not versions:
        errors.append(f"{slug}: no version files found")
        return errors
    expected = list(range(1, max(versions) + 1))
    if versions != expected:
        errors.append(f"{slug}: version files {versions} have gaps, expected {expected}")

    cur = node.get("current_version")
    if cur != max(versions):
        errors.append(f"{slug}: node.yaml current_version={cur} but highest file is v{max(versions)}")

    for v in versions:
        meta, _ = okf.load_version(slug, v)
        for e in okf.validate_schema(meta, version_schema):
            errors.append(f"{slug}/v{v}.md: {e}")
        if meta.get("version") != v:
            errors.append(f"{slug}/v{v}.md: frontmatter version={meta.get('version')} != filename v{v}")
        expected_supersedes = None if v == 1 else f"v{v - 1}"
        if meta.get("supersedes") != expected_supersedes:
            errors.append(f"{slug}/v{v}.md: supersedes={meta.get('supersedes')!r}, "
                           f"expected {expected_supersedes!r}")
        if v != cur and meta.get("status") != "superseded":
            errors.append(f"{slug}/v{v}.md: non-current version has status="
                           f"{meta.get('status')!r}, expected 'superseded'")
        if v == cur and node.get("status") != meta.get("status"):
            errors.append(f"{slug}: node.yaml status={node.get('status')!r} != "
                           f"current version status={meta.get('status')!r}")
    return errors


def check_aliases(slugs):
    errors = []
    owner = {}
    for slug in slugs:
        node = okf.load_node(slug)
        for a in [slug] + node.get("aliases", []):
            if a in owner and owner[a] != slug:
                errors.append(f"alias collision: {a!r} claimed by both {owner[a]!r} and {slug!r}")
            owner[a] = slug
    return errors


def main():
    node_schema = okf.load_schema("node.schema.json")
    version_schema = okf.load_schema("version.schema.json")
    slugs = okf.list_concepts()

    errors = []
    for slug in slugs:
        errors.extend(check_concept(slug, node_schema, version_schema))
    errors.extend(check_aliases(slugs))

    if errors:
        print(f"kb_lint: {len(errors)} problem(s) across {len(slugs)} concept(s)")
        for e in errors:
            print(f"  - {e}")
        raise SystemExit(1)
    print(f"kb_lint: clean ({len(slugs)} concept(s))")


if __name__ == "__main__":
    main()
