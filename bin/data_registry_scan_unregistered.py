#!/usr/bin/env python3
"""data_registry_scan_unregistered.py — Section E helper for data_registry_audit.sh.

Scans a fixed list of production entry-point files for `data/*` file references
(os.path.join(WORKDIR,"data",...) and quoted "data/..." literals), then checks whether the
basename of each reference appears anywhere under mike/kb/data_registry/**/*.md. Prints one line
per finding; the caller (data_registry_audit.sh) parses stdout and feeds it through its own
ok()/warn()/log() functions.

Built 2026-08-28 (job Taylor_20260828_081256) after bank_lens_v3.csv/power_lens.csv were found
stale ~3 months with zero registry entry and zero cron. Report-only, WARN-severity only — a hit
can be a legitimate self-generated state/log file; final judgment stays with the human reading
the report (coding_guidelines.md §9).
"""
import os
import re
import sys

# dirs that are known execution-log/state/cache areas -- never registry-tracked as "input sources"
HARD_EXCLUDE_DIRS = (
    "data/execution_logs/", "data/trade_plans/", "data/margin_approvals/",
    "data/bq_cache/", "data/_quarantine/",
)
# filename patterns that are self-generated OUTPUT written by trading_bot itself, not an input
SELF_GEN_RE = re.compile(r"^(journal_.*\.csv|nav_history_.*\.csv)$")
# ambiguous state/status/log/cache filenames -- don't guess, hand to a human instead of WARN/OK
AMBIGUOUS_RE = re.compile(r"(_state\.|_status\.|_journal\.|\.log$|_cache\.|_log\.)")

JOIN_RE = re.compile(r'os\.path\.join\(([^)]*)\)')
LIT_RE = re.compile(r'["\']([^"\']*)["\']')
QUOTED_DATA_RE = re.compile(r'["\'](data/[^"\'{}\s]+)["\']')


def scan(root: str, targets: list[str]) -> int:
    registry_dir = os.path.join(root, "mike", "kb", "data_registry")
    registry_basenames = set()
    for dirpath, _, files in os.walk(registry_dir):
        for fn in files:
            if fn.endswith(".md"):
                try:
                    with open(os.path.join(dirpath, fn), encoding="utf-8", errors="ignore") as fh:
                        registry_basenames.add(fh.read())
                except OSError:
                    pass

    def in_registry(basename: str) -> bool:
        return any(basename in txt for txt in registry_basenames)

    found: dict[str, str] = {}

    def record(relpath: str, srcfile: str) -> None:
        relpath = relpath.strip()
        if not relpath or not relpath.startswith("data/") or relpath in ("data", "data/"):
            return
        found.setdefault(relpath, srcfile)

    for t in targets:
        path = os.path.join(root, t)
        if not os.path.isfile(path):
            continue
        try:
            with open(path, encoding="utf-8", errors="ignore") as fh:
                text = fh.read()
        except OSError:
            continue

        # pattern 1: os.path.join(VAR, "data", "sub", "file.ext")
        for m in JOIN_RE.finditer(text):
            args = LIT_RE.findall(m.group(1))
            if "data" in args:
                idx = args.index("data")
                rest = args[idx + 1:]
                if rest:
                    record("data/" + "/".join(rest), t)

        # pattern 2: direct quoted literal "data/xxx" (f-string {vars} excluded via char class)
        for m in QUOTED_DATA_RE.finditer(text):
            record(m.group(1), t)

    warn_list, ambiguous_list, ok_count = [], [], 0
    for relpath, srcfile in sorted(found.items()):
        # relpath may or may not carry a trailing slash (os.path.join(WORKDIR,"data","margin_approvals")
        # -> "data/margin_approvals", no slash) while HARD_EXCLUDE_DIRS entries always do -- compare the
        # normalized (trailing-slash-stripped) value on both sides, per coding_guidelines.md §28 (never
        # compare raw un-normalized strings between two sources).
        rp_norm = relpath.rstrip("/")
        if any(rp_norm == d.rstrip("/") or relpath.startswith(d) for d in HARD_EXCLUDE_DIRS):
            continue
        basename = os.path.basename(relpath)
        if SELF_GEN_RE.match(basename):
            continue
        if in_registry(basename):
            ok_count += 1
            continue
        if AMBIGUOUS_RE.search(basename):
            ambiguous_list.append((relpath, srcfile))
        else:
            warn_list.append((relpath, srcfile))

    print(f"INFO scanned {len(targets)} target file(s), {len(found)} distinct data/* reference(s), {ok_count} already registered")
    for relpath, srcfile in warn_list:
        print(f"WARN {relpath} (read by {srcfile}) -- not found in any mike/kb/data_registry/**/*.md, register it or confirm it's self-generated output")
    for relpath, srcfile in ambiguous_list:
        print(f"UNSURE {relpath} (read by {srcfile}) -- looks like a state/log/cache file (ambiguous input-vs-output); CẦN NGƯỜI PHÂN LOẠI, not auto-classified")
    return 0


if __name__ == "__main__":
    sys.exit(scan(sys.argv[1], sys.argv[2:]))
