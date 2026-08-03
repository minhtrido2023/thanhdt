#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Flag concepts that share a fact_key but disagree on fact_value.

Only compares concepts currently `verified` or `unverified` (a `disputed` pair
is already flagged; `rejected`/`superseded` are settled/historical). This is a
REPORT, not a gate — it surfaces candidates for kb_dispute.py, never resolves
anything itself. fact_key/fact_value are optional node.yaml fields; concepts
without them are skipped.

Usage:
    kb_contradiction_sweep.py
"""
import os

import _bootstrap  # noqa: F401
import okf


def main():
    slugs = okf.list_concepts()
    groups = {}
    for slug in slugs:
        node = okf.load_node(slug)
        if node.get("status") not in ("verified", "unverified"):
            continue
        key = node.get("fact_key")
        if not key:
            continue
        groups.setdefault(key, []).append((slug, node.get("fact_value"), node.get("status")))

    findings = []
    for key, rows in sorted(groups.items()):
        distinct_values = {v for _, v, _ in rows}
        if len(distinct_values) > 1:
            findings.append((key, rows))

    date = okf.today()
    report_path = os.path.join(okf.PROCESS_DIR, "contradiction_sweeps", f"{date}.md")
    lines = [f"# Contradiction sweep — {date}", ""]
    if not findings:
        lines.append("No contradictions found.")
    else:
        lines.append(f"{len(findings)} fact_key(s) with disagreeing values:")
        lines.append("")
        for key, rows in findings:
            lines.append(f"## `{key}`")
            for slug, value, status in rows:
                lines.append(f"- `{slug}` ({status}): `{value!r}`")
            lines.append("")
        lines.append("Next step for each: `kb_dispute.py <slug_a> <slug_b> --reason ...` "
                      "to open a conflict review — this report does not do it for you.")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"contradiction sweep: {len(findings)} conflict(s) found -> {report_path}")


if __name__ == "__main__":
    main()
