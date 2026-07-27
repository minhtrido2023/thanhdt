#!/usr/bin/env python3
"""archive_memory.py — split an agent working-memory file (kb/memory/<id>.md) into a
HOT file (recent + still-open entries, stays on the SessionStart load path) and a COLD
archive (kb/memory/archive/<id>_history.md, NOT auto-loaded). Nothing is deleted — the
archive is an append-only audit trail.

A memory file is: a fixed HEAD (everything before the first `- [YYYY-...` bullet — role,
tools, curated sections, Mike's "Việc còn treo" block) followed by timestamped bullet
ENTRIES appended by remember.sh. HEAD is ALWAYS preserved verbatim. Each entry is the
`- [ts] ...` line plus any following continuation lines up to the next bullet.

An entry is KEPT (stays hot) if ANY of:
  1. it is among the last --keep entries (recency floor), OR
  2. its date >= today - --days (recent window), OR
  3. it matches --keep-open (an explicitly-still-open marker) — NEVER archived.
Otherwise it is a candidate to archive. With --require-done, a candidate is only actually
archived if it ALSO carries a DONE marker (XONG/DONE/…) — the conservative nightly mode
that removes ONLY provably-closed history. Without it (one-time deep clean), any non-kept
entry is archived.

Design invariants (coding_guidelines §3): dry-run by default; --apply writes the hot file
atomically (tmp + os.replace) so a mid-run kill leaves the original intact; the archive is
append-only; re-running is idempotent (kept entries never match the archive criteria again).
"""
import argparse, os, re, sys, datetime

BULLET_RE = re.compile(r'^- \[(\d{4}-\d{2}-\d{2})')
DONE_RE = re.compile(r'\bXONG\b|\bDONE\b|HOÀN TẤT|HOAN TAT|HOÀN THÀNH|HOAN THANH|✅')

# Generous "still open" default: any language an agent uses to flag unresolved work. Erring
# toward KEEP is the safe direction (the alternative — dropping a live item from hot-load —
# is the only real failure mode; over-keeping just costs a few KB, and it is recoverable
# from the archive regardless). Callers pass a stricter set for the aggressive one-time pass.
DEFAULT_OPEN = (
    # (1) still-open work
    r'ĐANG DỞ|DANG DO|ĐANG CHỜ|DANG CHO|CÒN MỞ|CON MO|CÒN TREO|CON TREO|CÒN NỢ|CON NO|'
    r'CHỜ VERIFY|CHO VERIFY|CHỜ USER|CHO USER|CHỜ user|CẦN USER|CAN USER|VIỆC MỞ|VIEC MO|'
    r'Việc mở|Viec mo|CHỜ DUYỆT|CHO DUYET|CHỜ Mike|CHO Mike|CHỜ APPROVE|user approve|'
    r'user duyệt|PENDING|TREO cho user|OPEN:|MỞ:|'
    # (2) durable standing rules/directives — "used every session", must stay hot even if the
    # entry also carries a done marker (e.g. "SCHEMA FIX XONG ... LƯU Ý CHO PLAN SAU")
    r'QUY TẮC|QUY TAC|User chỉ đạo|User chi dao|chỉ đạo|chi dao|LƯU Ý CHO|LUU Y CHO|'
    r'GỘP THREAD|TÁCH LẠI|ACCOUNT ROLES|Directive|directive'
)


def split_entries(text):
    """Return (head_str, [entry_str, ...]). head = lines before the first bullet."""
    lines = text.splitlines(keepends=True)
    first = None
    for i, ln in enumerate(lines):
        if BULLET_RE.match(ln):
            first = i
            break
    if first is None:
        return text, []                       # no bullets → whole file is head
    head = ''.join(lines[:first])
    entries, cur = [], []
    for ln in lines[first:]:
        if BULLET_RE.match(ln):
            if cur:
                entries.append(''.join(cur))
            cur = [ln]
        else:
            cur.append(ln)
    if cur:
        entries.append(''.join(cur))
    return head, entries


def classify(entries, keep, days, open_re, require_done, today):
    """Return (kept, archived) preserving order. today is a date."""
    cutoff = (today - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
    n = len(entries)
    kept, archived = [], []
    for idx, e in enumerate(entries):
        if idx >= n - keep:                   # recency floor
            kept.append(e); continue
        m = BULLET_RE.match(e)
        edate = m.group(1) if m else None
        if edate is None or edate >= cutoff:   # unparseable → keep (safe); or recent window
            kept.append(e); continue
        if open_re.search(e):                  # explicitly still open → never archive
            kept.append(e); continue
        if require_done and not DONE_RE.search(e):
            kept.append(e); continue           # conservative: only archive provably-done
        archived.append(e)
    return kept, archived


def main():
    ap = argparse.ArgumentParser(description="Archive closed entries out of a working-memory file.")
    ap.add_argument('memfile')
    ap.add_argument('--archive-dir', default=None,
                    help="dir for <id>_history.md (default: <memfile_dir>/archive)")
    ap.add_argument('--keep', type=int, default=6, help="always keep last N entries")
    ap.add_argument('--days', type=int, default=14, help="always keep entries newer than N days")
    ap.add_argument('--keep-open', default=DEFAULT_OPEN, help="regex: entries to never archive")
    ap.add_argument('--require-done', action='store_true',
                    help="only archive entries that ALSO carry a done marker (conservative)")
    ap.add_argument('--today', default=None, help="YYYY-MM-DD override (testing)")
    ap.add_argument('--apply', action='store_true', help="write changes (default: dry-run)")
    args = ap.parse_args()

    if not os.path.isfile(args.memfile):
        print(f"SKIP: {args.memfile} not found"); return 0
    today = (datetime.datetime.strptime(args.today, '%Y-%m-%d').date()
             if args.today else datetime.datetime.utcnow().date())
    open_re = re.compile(args.keep_open)

    text = open(args.memfile, encoding='utf-8').read()
    head, entries = split_entries(text)
    if not entries:
        print(f"NOOP {os.path.basename(args.memfile)}: no bullet entries"); return 0

    kept, archived = classify(entries, args.keep, args.days, open_re, args.require_done, today)
    if not archived:
        print(f"NOOP {os.path.basename(args.memfile)}: {len(kept)} entries, 0 to archive"); return 0

    arch_dir = args.archive_dir or os.path.join(os.path.dirname(args.memfile), 'archive')
    base = os.path.basename(args.memfile)[:-3] if args.memfile.endswith('.md') else os.path.basename(args.memfile)
    arch_path = os.path.join(arch_dir, f"{base}_history.md")
    arch_lines = sum(e.count('\n') for e in archived)

    print(f"{'APPLY' if args.apply else 'DRY-RUN'} {base}: keep {len(kept)}, archive "
          f"{len(archived)} entries ({arch_lines} lines) → {os.path.relpath(arch_path, os.path.dirname(args.memfile))}")
    if not args.apply:
        for e in archived:
            print("   - " + e.splitlines()[0][:110])
        return 0

    orig_mode = os.stat(args.memfile).st_mode & 0o777   # preserve the file's permissions
    os.makedirs(arch_dir, exist_ok=True)
    new_archive = not os.path.exists(arch_path)
    stamp = today.strftime('%Y-%m-%d')
    with open(arch_path, 'a', encoding='utf-8') as f:
        if f.tell() == 0:
            f.write(f"# {base} — working-memory archive (append-only; not auto-loaded)\n"
                    f"> Cold storage of closed/old entries moved out of kb/memory/{base}.md by "
                    f"archive_memory.py. Nothing here was deleted from history.\n")
        f.write(f"\n## Archived {stamp} (keep={args.keep} days={args.days} "
                f"require_done={args.require_done})\n")
        for e in archived:
            f.write(e if e.endswith('\n') else e + '\n')
    if new_archive:
        os.chmod(arch_path, orig_mode)      # archive inherits the source file's permissions

    new_text = head + ''.join(kept)
    tmp = args.memfile + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(new_text)
    os.chmod(tmp, orig_mode)                 # os.replace would otherwise drop mode → 0664
    os.replace(tmp, args.memfile)
    print(f"   wrote {len(new_text)} bytes hot / appended {arch_lines} lines to archive")
    return 0


if __name__ == '__main__':
    sys.exit(main())
