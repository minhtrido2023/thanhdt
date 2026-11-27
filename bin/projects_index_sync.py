#!/usr/bin/env python3
"""projects_index_sync.py --check|--fix

Đối chiếu file thật trong `kb/projects/*.md` (trừ `INDEX.md`) với `kb/projects/INDEX.md`.
Tương thích 100% với parser của `bin/work_tree_build.py` (## Dự án đã đóng / ## Dự án ĐANG MỞ)
và `bin/kb_recall.sh`.
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS_DIR = os.path.join(ROOT, "kb", "projects")
INDEX_FP = os.path.join(PROJECTS_DIR, "INDEX.md")

CLOSED_HDR = "## Dự án đã đóng — 1 dòng/dự án, chi tiết `cat kb/projects/<file>.md`"
DD_HDR = "## Dự án đã đóng — Due Diligence (DD cổ phiếu)"
OPEN_HDR = "## Dự án ĐANG MỞ, chi tiết tách riêng (không inline `current_ops.md`)"


def _strip_quotes(val):
    val = val.strip()
    if len(val) >= 2 and val[0] == "'" and val[-1] == "'":
        return val[1:-1]
    if len(val) >= 2 and val[0] == '"' and val[-1] == '"':
        return val[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return val


def real_files():
    """{filename ('foo.md'): abspath} for every project markdown file, excluding INDEX.md."""
    out = {}
    for fp in sorted(glob.glob(os.path.join(PROJECTS_DIR, "*.md"))):
        bn = os.path.basename(fp)
        if bn.upper() == "INDEX.MD":
            continue
        out[bn] = fp
    return out


def parse_meta(fp):
    """Read YAML frontmatter + heading fallback."""
    with open(fp, encoding="utf-8", errors="ignore") as f:
        text = f.read()
    fm = {}
    body = text
    m = re.match(r"^---\n(.*?)\n---\n?", text, re.S)
    if m:
        body = text[m.end():]
        for key in ("kind", "owner", "status", "updated", "title"):
            km = re.search(
                r"^%s:[ \t]*(?:[>|]-?[ \t]*\n((?:[ \t]+[^\n]+\n?)+)|([^\n]+))$" % key,
                m.group(1),
                re.M,
            )
            if km:
                raw = km.group(1) if km.group(1) is not None else km.group(2)
                fm[key] = _strip_quotes(re.sub(r"\s+", " ", raw).strip())
    if not fm.get("title"):
        for ln in body.splitlines():
            s = ln.strip()
            if s.startswith("#"):
                fm["title"] = s.lstrip("#").strip()
                break
    bn = os.path.basename(fp)
    if not fm.get("updated"):
        dm = re.search(r"(\d{4})(\d{2})(\d{2})", bn)
        if dm:
            fm["updated"] = f"{dm.group(1)}-{dm.group(2)}-{dm.group(3)}"
        else:
            fm["updated"] = "2026-11-27"
    if not fm.get("kind"):
        fm["kind"] = "dd" if ("-dd-" in bn or bn.startswith("dd-")) else "project"
    if not fm.get("status"):
        fm["status"] = "closed"
    return fm


def indexed_refs(index_text):
    """Return (refs_in_projects, orphan_local_refs, duplicate_refs) from bullet lines only."""
    counts = {}
    orphans = []
    # Only scan entry bullet lines (and indented continuations), skipping ## headings / comments
    entry_lines = [
        ln for ln in index_text.splitlines()
        if not ln.startswith("#") and not ln.lstrip().startswith("<!--")
    ]
    scan_text = "\n".join(entry_lines)
    for m in re.finditer(r"`([^`\s]+\.md)`|\(([^)\s]+\.md)\)", scan_text):
        ref = m.group(1) or m.group(2)
        if "/" in ref and not ref.startswith("kb/projects/"):
            continue  # external path e.g. agents/Taylor/research/.../REPORT.md
        bn = os.path.basename(ref)
        if bn.upper() == "INDEX.MD" or bn == "current_ops.md":
            continue
        counts[bn] = counts.get(bn, 0) + 1
        if not os.path.exists(os.path.join(PROJECTS_DIR, bn)):
            orphans.append(bn)
    dups = sorted(k for k, v in counts.items() if v > 1)
    return counts, sorted(set(orphans)), dups


def cmd_check():
    if not os.path.exists(INDEX_FP):
        print("THIẾU kb/projects/INDEX.md")
        return 1
    reals = real_files()
    with open(INDEX_FP, encoding="utf-8") as f:
        idx_text = f.read()
    counts, orphans, dups = indexed_refs(idx_text)
    missing = sorted(set(reals) - set(counts))
    if not missing and not orphans and not dups:
        print(f"OK: {len(reals)} file thật trong kb/projects/ khớp 100% với INDEX.md — 0 drift.")
        return 0
    if missing:
        print(f"THIẾU trong INDEX.md ({len(missing)}):")
        for bn in missing[:30]:
            print(f"  {bn}")
        if len(missing) > 30:
            print(f"  ... (+{len(missing) - 30} file)")
    if orphans:
        print(f"ORPHAN trong INDEX.md ({len(orphans)}): {orphans}")
    if dups:
        print(f"TRÙNG LẶP trong INDEX.md ({len(dups)}): {dups}")
    return 1


def _format_entry(bn, meta):
    dt_str = meta["updated"]
    title = re.sub(r"[`*]", "", meta.get("title") or bn).strip()
    if len(title) > 110:
        title = title[:109].rstrip() + "…"
    status = meta.get("status", "closed").upper()
    return f"- {dt_str} {title} → `{bn}` — **{status}**"


def cmd_fix():
    reals = real_files()
    with open(INDEX_FP, encoding="utf-8") as f:
        idx_text = f.read()

    # 1) Prune orphan lines (lines referencing missing kb/projects/<bn>.md)
    _, orphans, _ = indexed_refs(idx_text)
    orphan_set = set(orphans)
    lines = idx_text.splitlines()
    if orphan_set:
        lines = [ln for ln in lines if not any(o in ln for o in orphan_set)]
        idx_text = "\n".join(lines) + "\n"

    # 2) Find missing files and split by active / dd / closed
    counts, _, _ = indexed_refs(idx_text)
    missing = sorted(set(reals) - set(counts))
    if not missing and not orphan_set:
        print("OK: không có drift, không cần sửa gì.")
        return 0

    add_open, add_dd, add_closed = [], [], []
    for bn in missing:
        meta = parse_meta(reals[bn])
        entry = (meta["updated"], bn, _format_entry(bn, meta))
        st = meta["status"].lower()
        if st in ("active", "open", "in-progress", "monitoring"):
            add_open.append(entry)
        elif meta["kind"] == "dd":
            add_dd.append(entry)
        else:
            add_closed.append(entry)

    add_open.sort(reverse=True)
    add_dd.sort(reverse=True)
    add_closed.sort(reverse=True)

    lines = idx_text.splitlines()

    def _insert_under(hdr_prefix, new_rows, create_hdr=None):
        if not new_rows:
            return
        pos = None
        for i, ln in enumerate(lines):
            if ln.startswith(hdr_prefix):
                pos = i + 1
                # Skip HTML comments immediately after header
                while pos < len(lines) and (lines[pos].strip().startswith("<!--") or "-->" in lines[pos]):
                    if "-->" in lines[pos]:
                        pos += 1
                        break
                    pos += 1
                break
        if pos is None:
            if create_hdr is None:
                return
            lines.extend(["", create_hdr] + [r[2] for r in new_rows])
            return
        lines[pos:pos] = [r[2] for r in new_rows]

    if add_closed:
        _insert_under("## Dự án đã đóng — 1 dòng", add_closed, CLOSED_HDR)
    if add_open:
        _insert_under("## Dự án ĐANG MỞ", add_open, OPEN_HDR)
    if add_dd:
        _insert_under("## Dự án đã đóng — Due Diligence", add_dd, DD_HDR)

    out_text = "\n".join(lines).rstrip() + "\n"
    with open(INDEX_FP, "w", encoding="utf-8") as f:
        f.write(out_text)
    print(
        f"Đã cập nhật kb/projects/INDEX.md (+{len(add_closed)} closed, "
        f"+{len(add_open)} open, +{len(add_dd)} dd, -{len(orphan_set)} orphan)."
    )
    return 0


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("--check", "--fix"):
        sys.stderr.write("usage: projects_index_sync.py --check|--fix\n")
        return 2
    if sys.argv[1] == "--check":
        return cmd_check()
    return cmd_fix()


if __name__ == "__main__":
    sys.exit(main())
