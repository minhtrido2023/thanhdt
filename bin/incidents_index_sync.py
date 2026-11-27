#!/usr/bin/env python3
"""incidents_index_sync.py --check|--fix

Đối chiếu file thật trong `kb/incidents/<YYYY-MM>/*.md` (và `retro/*.md` khi có `retro/index.md`)
với các bảng liệt kê trong `kb/incidents/index.md` + `kb/incidents/archive-*.md`.

--check: kiểm thiếu, orphan, và trùng lặp link; exit 1 nếu có drift, exit 0 nếu sạch.
--fix:   xoá dòng trùng lặp/orphan, chèn dòng thiếu từ frontmatter/heading, cập nhật
         `retro/index.md` + top-14 RETRO trong `index.md` (nếu `retro/index.md` tồn tại),
         và cập nhật `entries:` trong frontmatter `index.md`.
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INCIDENTS_DIR = os.path.join(ROOT, "kb", "incidents")
INDEX_FP = os.path.join(INCIDENTS_DIR, "index.md")
RETRO_INDEX_FP = os.path.join(INCIDENTS_DIR, "retro", "index.md")

MONTH_RE = re.compile(r"^### (\d{4}-\d{2})\s*$", re.M)
LINK_RE = re.compile(
    r"^\| *(\d{4}-\d{2}-\d{2}) *\| *\[(.+)\]\((\d{4}-\d{2}/[^)]+\.md)\) *\| *([^|\n]*?) *\| *$"
)
RETRO_ROW_RE = re.compile(
    r"^\| *(\d{4}-\d{2}-\d{2}) *\| *\[(.+)\]\(((?:retro/)?retro-[^)]+\.md)\) *\|"
)
MAX_INDEX_RETROS = 14
RETRO_LABEL_MAX = 180


def _strip_quotes(val):
    val = val.strip()
    if len(val) >= 2 and ((val[0] == "'" and val[-1] == "'") or (val[0] == '"' and val[-1] == '"')):
        return val[1:-1]
    return val


def real_files():
    """{relpath ('2026-08/xxx.md'): abspath} for every incident file, excluding retro/archive."""
    out = {}
    for fp in glob.glob(os.path.join(INCIDENTS_DIR, "20*", "*.md")):
        month_dir = os.path.basename(os.path.dirname(fp))
        if not re.match(r"^\d{4}-\d{2}$", month_dir):
            continue
        rel = "%s/%s" % (month_dir, os.path.basename(fp))
        out[rel] = fp
    return out


def retro_files():
    """{filename ('retro-2026-08-01.md'): abspath} for every retro file."""
    out = {}
    rdir = os.path.join(INCIDENTS_DIR, "retro")
    if not os.path.isdir(rdir):
        return out
    for fp in glob.glob(os.path.join(rdir, "*.md")):
        bn = os.path.basename(fp)
        if bn == "index.md":
            continue
        out[bn] = fp
    return out


def archive_files():
    return sorted(glob.glob(os.path.join(INCIDENTS_DIR, "archive-*.md")))


def parse_rows(text):
    rows = []
    for ln in text.splitlines():
        m = LINK_RE.match(ln.strip())
        if m:
            rows.append(m.groups())
    return rows


def linked_rows():
    """Return (all_rows, index_text, archive_texts_dict)."""
    with open(INDEX_FP, encoding="utf-8") as f:
        index_text = f.read()
    all_rows = parse_rows(index_text)
    arch_texts = {}
    for afp in archive_files():
        with open(afp, encoding="utf-8") as f:
            txt = f.read()
        arch_texts[afp] = txt
        all_rows.extend(parse_rows(txt))
    return all_rows, index_text, arch_texts


def parse_frontmatter(fp):
    with open(fp, encoding="utf-8") as f:
        text = f.read()
    fm = {}
    body = text
    m = re.match(r"^---\n(.*?)\n---\n?", text, re.S)
    if m:
        body = text[m.end():]
        for key in ("date", "status", "title", "updated"):
            km = re.search(
                r"^%s:[ \t]*(?:[>|]-?[ \t]*\n((?:[ \t]+[^\n]+\n?)+)|([^\n]+))$" % key,
                m.group(1),
                re.M,
            )
            if km:
                raw = km.group(1) if km.group(1) is not None else km.group(2)
                val = re.sub(r"\s+", " ", raw).strip()
                fm[key] = _strip_quotes(val)
    if "title" not in fm or not fm["title"]:
        for ln in body.splitlines():
            s = ln.strip()
            if s.startswith("#"):
                fm["title"] = s.lstrip("#").strip()
                break
    return fm


def _short(text, limit=RETRO_LABEL_MAX):
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _escape_cell(text):
    return text.replace("|", "\\|")


def _retro_index_check():
    if not os.path.exists(RETRO_INDEX_FP):
        return [], [], []
    reals = set(retro_files())
    with open(RETRO_INDEX_FP, encoding="utf-8") as f:
        txt = f.read()
    seen = {}
    dups = []
    for ln in txt.splitlines():
        m = RETRO_ROW_RE.match(ln.strip())
        if not m:
            continue
        bn = os.path.basename(m.group(3))
        seen[bn] = seen.get(bn, 0) + 1
        if seen[bn] == 2:
            dups.append(bn)
    missing = sorted(reals - set(seen))
    orphaned = sorted(set(seen) - reals)
    return missing, orphaned, sorted(dups)


def cmd_check(real, linked):
    counts = {}
    for row in linked:
        rel = row[2]
        counts[rel] = counts.get(rel, 0) + 1
    linked_paths = set(counts)
    missing = sorted(set(real) - linked_paths)
    orphaned = sorted(linked_paths - set(real))
    dups = sorted(p for p, c in counts.items() if c > 1)
    r_miss, r_orph, r_dup = _retro_index_check()

    if not missing and not orphaned and not dups and not r_miss and not r_orph and not r_dup:
        msg = "OK: %d file thật khớp đúng %d dòng — 0 drift, 0 trùng lặp." % (
            len(real),
            len(linked_paths),
        )
        if os.path.exists(RETRO_INDEX_FP):
            msg += " retro/index.md sạch."
        print(msg)
        return 0
    if missing:
        print("THIẾU trong index/archive (%d):" % len(missing))
        for rel in missing:
            print("  %s" % rel)
    if orphaned:
        print("ORPHAN trong index/archive — file không còn tồn tại (%d):" % len(orphaned))
        for rel in orphaned:
            print("  %s" % rel)
    if dups:
        print("TRÙNG LẶP trong index/archive (%d):" % len(dups))
        for rel in dups:
            print("  %s (%dx)" % (rel, counts[rel]))
    if r_miss or r_orph or r_dup:
        print("DRIFT retro/index.md: missing=%d orphaned=%d dups=%d" % (len(r_miss), len(r_orph), len(r_dup)))
    return 1


def build_row(rel, fp):
    fm = parse_frontmatter(fp)
    date = fm.get("date", rel.split("/")[1][:10])
    title = _escape_cell(fm.get("title", rel))
    status = _escape_cell(fm.get("status") or "logged")
    return "| %s | [%s](%s) | %s |" % (date, title, rel, status)


def _dedup_and_prune_lines(lines, orphaned_set):
    """Drop orphan rows and duplicate relpath rows (keep best/first)."""
    row_indices_by_rel = {}
    parsed_by_idx = {}
    for idx, ln in enumerate(lines):
        m = LINK_RE.match(ln.strip())
        if not m:
            continue
        rel = m.group(3)
        if rel in orphaned_set:
            parsed_by_idx[idx] = (rel, None)
            continue
        parsed_by_idx[idx] = (rel, m.groups())
        row_indices_by_rel.setdefault(rel, []).append(idx)

    drop_indices = set()
    for idx, (rel, grp) in parsed_by_idx.items():
        if grp is None:
            drop_indices.add(idx)

    dups_removed = 0
    for rel, idxs in row_indices_by_rel.items():
        if len(idxs) <= 1:
            continue
        # Keep the single best row: prefer status != '?', then non-relpath title, then first index
        def score(i):
            _, title, _, status = parsed_by_idx[i][1]
            return (
                1 if status.strip() not in ("", "?") else 0,
                1 if title.strip() != rel else 0,
                -i,
            )

        best = max(idxs, key=score)
        for i in idxs:
            if i != best:
                drop_indices.add(i)
                dups_removed += 1

    cleaned = [ln for idx, ln in enumerate(lines) if idx not in drop_indices]
    return cleaned, dups_removed


def _sync_retro_indexes(index_lines):
    """Sync retro/index.md (all retros) and top MAX_INDEX_RETROS in index.md."""
    reals = retro_files()
    entries = []
    for bn, fp in reals.items():
        fm = parse_frontmatter(fp)
        dm = re.search(r"(\d{4}-\d{2}-\d{2})", fm.get("date", bn))
        dt_str = dm.group(1) if dm else bn
        title = _escape_cell(_short(fm.get("title", bn)))
        entries.append((dt_str, bn, title))
    entries.sort(key=lambda x: (x[0], x[1]), reverse=True)

    retro_doc = [
        "---",
        "kind: retro-index",
        "title: Daily RETRO Archive Index",
        "owner: Mike",
        "status: generated",
        "updated: %s" % (entries[0][0] if entries else "2026-11-27"),
        "entries: %d" % len(entries),
        "---",
        "",
        "# Daily RETRO Archive Index (%d bản)" % len(entries),
        "",
        "> Tự đồng bộ bởi `bin/incidents_index_sync.py`. 14 bản mới nhất hiển thị tại [index.md](../index.md).",
        "",
        "| Ngày | Tóm tắt RETRO |",
        "|---|---|",
    ]
    for dt_str, bn, title in entries:
        retro_doc.append("| %s | [%s](%s) |" % (dt_str, title, bn))
    retro_text = "\n".join(retro_doc) + "\n"

    retro_changed = True
    if os.path.exists(RETRO_INDEX_FP):
        with open(RETRO_INDEX_FP, encoding="utf-8") as f:
            retro_changed = f.read() != retro_text
    if retro_changed:
        with open(RETRO_INDEX_FP, "w", encoding="utf-8") as f:
            f.write(retro_text)

    # Update ## RETRO section in index.md
    r_hdr = None
    for i, ln in enumerate(index_lines):
        if ln.startswith("## RETRO"):
            r_hdr = i
            break
    if r_hdr is not None:
        end_idx = len(index_lines)
        for j in range(r_hdr + 1, len(index_lines)):
            if index_lines[j].startswith("## "):
                end_idx = j
                break
        new_sec = [
            "## RETRO hằng ngày (14 bản mới nhất)",
            "",
            "> Kho đầy đủ (%d bản): [`retro/index.md`](retro/index.md) — tự đồng bộ bởi `bin/incidents_index_sync.py`."
            % len(entries),
            "",
            "| Ngày | Tóm tắt RETRO |",
            "|---|---|",
        ]
        for dt_str, bn, title in entries[:MAX_INDEX_RETROS]:
            new_sec.append("| %s | [%s](retro/%s) |" % (dt_str, title, bn))
        new_sec.append("")
        index_lines[r_hdr:end_idx] = new_sec
    return index_lines, retro_changed


def cmd_fix(real, linked, index_text, arch_texts):
    counts = {}
    for row in linked:
        counts[row[2]] = counts.get(row[2], 0) + 1
    linked_paths = set(counts)
    missing = sorted(set(real) - linked_paths)
    orphaned = set(linked_paths - set(real))

    # 1) Deduplicate & remove orphans across archive files first (if any)
    seen_global = set()
    for afp, atxt in arch_texts.items():
        alines = atxt.split("\n")
        alines, ad_dups = _dedup_and_prune_lines(alines, orphaned)
        new_atxt = "\n".join(alines)
        if new_atxt != atxt:
            with open(afp, "w", encoding="utf-8") as f:
                f.write(new_atxt)
            if ad_dups:
                print("Đã dọn %d dòng trùng trong %s." % (ad_dups, os.path.basename(afp)))
        for row in parse_rows(new_atxt):
            seen_global.add(row[2])

    # 2) Deduplicate & prune index.md (including anything already in archive-*)
    lines = index_text.split("\n")
    lines, dups_removed = _dedup_and_prune_lines(lines, orphaned | seen_global)
    if orphaned:
        print("Đã xoá %d dòng orphan." % len(orphaned))
    if dups_removed:
        print("Đã xoá %d dòng trùng lặp trong index.md." % dups_removed)

    # 3) Insert missing rows grouped by month into index.md
    by_month = {}
    for rel in missing:
        month = rel.split("/")[0]
        by_month.setdefault(month, []).append(rel)

    for month, rels in by_month.items():
        rows = sorted((build_row(rel, real[rel]) for rel in rels), reverse=True)
        header_idx = None
        for i, ln in enumerate(lines):
            if ln.strip() == "### %s" % month:
                header_idx = i
                break
        if header_idx is not None:
            insert_at = None
            for j in range(header_idx, min(header_idx + 6, len(lines))):
                if lines[j].startswith("|---"):
                    insert_at = j + 1
                    break
            if insert_at is None:
                insert_at = header_idx + 1
                lines[insert_at:insert_at] = ["", "| Ngày | Sự cố | status |", "|---|---|---|"]
                insert_at += 3
            lines[insert_at:insert_at] = rows
        else:
            new_section = ["### %s" % month, "", "| Ngày | Sự cố | status |", "|---|---|---|"] + rows + [""]
            insert_at = len(lines)
            for i, ln in enumerate(lines):
                mm = MONTH_RE.match(ln)
                if mm and mm.group(1) < month:
                    insert_at = i
                    break
                if ln.startswith("## RETRO"):
                    insert_at = i
                    break
            lines[insert_at:insert_at] = new_section
        print("Đã chèn %d dòng vào tháng %s." % (len(rows), month))

    # 4) Sync retro/index.md & top-14 RETRO in index.md ONLY if retro/index.md exists
    if os.path.exists(RETRO_INDEX_FP):
        lines, retro_changed = _sync_retro_indexes(lines)
        if retro_changed:
            print("Đã đồng bộ kb/incidents/retro/index.md.")

    new_text = "\n".join(lines)

    # 5) Update entries: count in frontmatter
    n_incidents = len(real)
    n_retro = len(retro_files())
    n_open = 1 if os.path.exists(os.path.join(INCIDENTS_DIR, "_open-not-yet-hardened.md")) else 0
    total = n_incidents + n_retro + n_open
    new_text = re.sub(
        r"^entries: .*$",
        "entries: %d file (%d sự cố + %d RETRO + %d mục open-items chung)" % (total, n_incidents, n_retro, n_open),
        new_text,
        count=1,
        flags=re.M,
    )

    if new_text != index_text:
        with open(INDEX_FP, "w", encoding="utf-8") as f:
            f.write(new_text)
        print("Đã ghi kb/incidents/index.md — entries: %d (%d sự cố + %d RETRO + %d open-items)." % (
            total, n_incidents, n_retro, n_open
        ))
    else:
        print("OK: không có thay đổi cần ghi.")
    return 0


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("--check", "--fix"):
        sys.stderr.write("usage: incidents_index_sync.py --check|--fix\n")
        return 2
    real = real_files()
    linked, index_text, arch_texts = linked_rows()
    if sys.argv[1] == "--check":
        return cmd_check(real, linked)
    return cmd_fix(real, linked, index_text, arch_texts)


if __name__ == "__main__":
    sys.exit(main())
