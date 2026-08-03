#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""End-to-end selfcheck for tbot's kb_tools.

Runs entirely against an isolated tmpdir (monkey-patches okf.CONCEPTS_DIR/
INDEX_DIR/PROCESS_DIR) — never touches the real kb/concepts or kb/process, so
it's safe to run any time without polluting real data. Exercises the full
lifecycle: create -> new_version -> contradiction_sweep (catches it) ->
ask_to_verify -> verify -> dispute -> resolve_conflict ->
contradiction_sweep (clean now) -> reindex -> lint.

Run under `env -u TZ` too, per this repo's date-logic testing convention —
today() depends on local date and a foreign TZ is the cheapest way to catch a
silent assumption.
"""
import json
import os
import shutil
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(_HERE, "..", "lib")))
sys.path.insert(0, os.path.normpath(os.path.join(_HERE, "..", "kb_tools")))
import okf  # noqa: E402

FAILURES = []


def check(name, cond):
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        FAILURES.append(name)


def main():
    tmp = tempfile.mkdtemp(prefix="tbot_kb_selfcheck_")
    okf.CONCEPTS_DIR = os.path.join(tmp, "concepts")
    okf.INDEX_DIR = os.path.join(tmp, "_index")
    okf.PROCESS_DIR = os.path.join(tmp, "process")
    os.makedirs(okf.CONCEPTS_DIR, exist_ok=True)
    for d in ("ask_to_verify", "conflict_review", "contradiction_sweeps"):
        os.makedirs(os.path.join(okf.PROCESS_DIR, d), exist_ok=True)

    import kb_contradiction_sweep
    import kb_reindex
    import kb_lint

    try:
        node = okf.new_concept("alpha-fact", "Alpha test fact", "alpha body v1",
                                tags=["selfcheck"], author="selfcheck")
        node["fact_key"] = "test-fact"
        node["fact_value"] = "A"
        okf.save_node("alpha-fact", node)
        check("alpha created v1 unverified",
              node["status"] == "unverified" and node["current_version"] == 1)

        node = okf.new_version("alpha-fact", "alpha body v2", "clarified wording",
                                author="selfcheck")
        check("alpha now v2", node["current_version"] == 2)
        v1meta, _ = okf.load_version("alpha-fact", 1)
        check("alpha v1 marked superseded", v1meta["status"] == "superseded")

        nodeb = okf.new_concept("beta-fact", "Beta test fact", "beta body v1",
                                 tags=["selfcheck"], author="selfcheck")
        nodeb["fact_key"] = "test-fact"
        nodeb["fact_value"] = "B"
        okf.save_node("beta-fact", nodeb)

        kb_contradiction_sweep.main()
        report_path = os.path.join(okf.PROCESS_DIR, "contradiction_sweeps", f"{okf.today()}.md")
        report = open(report_path, encoding="utf-8").read()
        check("sweep #1 flags test-fact conflict",
              "test-fact" in report and "alpha-fact" in report and "beta-fact" in report)

        req_id, req_path = okf.open_ask_to_verify("alpha-fact", "please confirm",
                                                    requested_by="selfcheck")
        check("ask-to-verify request open",
              okf.read_frontmatter(req_path)[0]["status"] == "open")
        node = okf.set_current_status("alpha-fact", "verified", verified_by="selfcheck")
        for path, _m in okf.find_open_ask_to_verify("alpha-fact"):
            okf.close_ask_to_verify(path, "selfcheck", "confirmed for test")
        check("alpha verified", node["status"] == "verified")
        check("ask-to-verify request closed",
              okf.read_frontmatter(req_path)[0]["status"] == "resolved")

        review_id, _review_path = okf.open_conflict_review(
            "alpha-fact", "beta-fact", "conflicting fact_value", opened_by="selfcheck")
        okf.set_current_status("alpha-fact", "disputed")
        okf.set_current_status("beta-fact", "disputed")
        check("both disputed",
              okf.load_node("alpha-fact")["status"] == "disputed"
              and okf.load_node("beta-fact")["status"] == "disputed")

        okf.close_conflict_review(review_id, "alpha-fact", "beta-fact", "selfcheck",
                                   "alpha has better sourcing")
        okf.set_current_status("alpha-fact", "verified", verified_by="selfcheck")
        okf.set_current_status("beta-fact", "rejected")
        check("alpha verified after resolution",
              okf.load_node("alpha-fact")["status"] == "verified")
        check("beta rejected after resolution",
              okf.load_node("beta-fact")["status"] == "rejected")

        kb_contradiction_sweep.main()
        report2 = open(report_path, encoding="utf-8").read()
        check("sweep #2 clean after resolution", "No contradictions found." in report2)

        kb_reindex.main()
        aliases = json.load(open(os.path.join(okf.INDEX_DIR, "aliases.json"), encoding="utf-8"))
        check("reindex captured both concepts",
              aliases.get("alpha-fact") == "alpha-fact" and aliases.get("beta-fact") == "beta-fact")

        try:
            kb_lint.main()
            lint_ok = True
        except SystemExit as e:
            lint_ok = (e.code == 0 or e.code is None)
        check("lint clean", lint_ok)

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILURE(S): {FAILURES}")
        raise SystemExit(1)
    print("all checks passed")


if __name__ == "__main__":
    main()
