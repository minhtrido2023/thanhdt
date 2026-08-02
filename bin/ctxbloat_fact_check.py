#!/usr/bin/env python3
"""ctxbloat_fact_check.py OLD_FILE NEW_FILE — mechanical gate for kb_nightly.sh's context-bloat
auto-fix (Phase 4.6). Extracts every "fact token" (date, %/KB/VND number, filename/path, backtick
code span) from OLD_FILE and NEW_FILE and asserts OLD ⊆ NEW — a compression pass is only allowed
to remove narrative/prose, never a fact. Same philosophy as this repo's own
kb/coding_guidelines.md "Enforcement policy": prefer a mechanical check over trusting an LLM's
prose claim of "I only cut narrative." Exit 0 = no fact dropped (safe to apply). Exit 1 = at
least one fact token present in OLD is missing from NEW (reject, do not apply).

Deliberately does NOT try to judge whether the compression is "good writing" — only whether it is
FACT-PRESERVING. A false negative (flags something that wasn't really a fact, e.g. a stray number
in an example) is a safe failure mode here: it just sends the episode to human escalation instead
of auto-applying, matching the existing fail-safe-pause discipline (coding_guidelines.md §5).
"""
import re
import sys

# STRICT classes: precise facts that must survive byte-for-byte (a % or date rarely repeats
# elsewhere in different clothing, so an exact-string diff is the right amount of strict).
STRICT_PATTERNS = {
    "date": re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),
    "percent": re.compile(r"\b\d+(?:[.,]\d+)?\s?%"),
    "kb_vnd": re.compile(r"\b\d+(?:[.,]\d+)?\s?(?:KB|MB|GB|VND|pp|tr\b|B VND)", re.IGNORECASE),
    "commit_sha": re.compile(r"\b[0-9a-f]{7,40}\b"),
    "job_id": re.compile(r"\b[A-Z][A-Za-z]+_\d{8}_\d{6}\b"),
}
# LOOSE class: filenames/paths. A script name is legitimately mentioned 2-3x in prose and
# de-duplicating repeat mentions (or dropping a `bin/` path prefix on a repeat mention) is NOT a
# fact loss -- so this checks only that the file's BASENAME still appears SOMEWHERE in NEW
# (any formatting), not that the exact backtick span/path prefix survived verbatim. Only fires
# when a filename disappears from the document entirely.
PATH_PATTERN = re.compile(r"\b[\w][\w./-]*\.(?:py|sh|md|json|csv|jsonl|txt)\b")


def extract_strict(text):
    return {kind: set(m.strip() for m in pat.findall(text)) for kind, pat in STRICT_PATTERNS.items()}


def extract_basenames(text):
    return set(m.split("/")[-1] for m in PATH_PATTERN.findall(text))


def main():
    if len(sys.argv) != 3:
        print("usage: ctxbloat_fact_check.py OLD_FILE NEW_FILE", file=sys.stderr)
        return 2
    old_path, new_path = sys.argv[1], sys.argv[2]
    with open(old_path, encoding="utf-8") as f:
        old_text = f.read()
    with open(new_path, encoding="utf-8") as f:
        new_text = f.read()

    old_strict = extract_strict(old_text)
    new_strict = extract_strict(new_text)

    dropped_any = False
    for kind in STRICT_PATTERNS:
        dropped = old_strict[kind] - new_strict[kind]
        if dropped:
            dropped_any = True
            print(f"FACT-CHECK FAIL [{kind}]: {len(dropped)} token(s) present in OLD, missing in NEW:")
            for tok in sorted(dropped)[:30]:
                print(f"    {tok!r}")
            if len(dropped) > 30:
                print(f"    ... and {len(dropped) - 30} more")

    old_basenames = extract_basenames(old_text)
    dropped_files = set()
    for base in old_basenames:
        if base not in new_text:  # substring check, ANY formatting/prefix counts as "still there"
            dropped_files.add(base)
    if dropped_files:
        dropped_any = True
        print(f"FACT-CHECK FAIL [filename]: {len(dropped_files)} file(s) mentioned in OLD, absent from NEW entirely:")
        for f in sorted(dropped_files):
            print(f"    {f!r}")

    if dropped_any:
        print("VERDICT: REJECT — at least one fact was dropped, do not apply this compression.")
        return 1

    print("VERDICT: PASS — every fact token in OLD is present in NEW.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
