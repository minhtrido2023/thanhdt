#!/usr/bin/env python3
"""incidents_index_sync.py --check|--fix

Đối chiếu file thật trong `kb/incidents/<YYYY-MM>/*.md` với bảng liệt kê trong
`kb/incidents/index.md`. Sinh ra sau khảo sát vận hành 2026-08-01 (item #4 đã duyệt): việc
đồng bộ này trước đây giao cho 1 job LLM/tuần (`weekly_ops_audit.sh` mục 5) cho một phép so
2 danh sách file — đắt và không tất định cho 1 việc cơ học. Bắt được ngay lần viết đầu: file
`2026-08-01-dispatch-max-turns-export-missing-bg-broken.md` (chính sự cố dispatch.sh hôm nay)
thiếu trong index, và số đếm `entries:` trong frontmatter đã lệch từ trước đó nữa (54 sự cố
ghi trong frontmatter ≠ 55 dòng thật đang link trong bảng, TRƯỚC KHI tính luôn file thiếu).

--check: in báo cáo drift (thiếu/orphan), exit 1 nếu có drift, exit 0 nếu sạch.
--fix: chèn dòng thiếu vào đúng bảng tháng (đọc frontmatter file lấy title/status), xoá dòng
  orphan (file không còn tồn tại), cập nhật `entries:` trong frontmatter. Sắp theo NGÀY MỚI
  NHẤT TRƯỚC (khớp quy ước "Newest first" của chính index.md).

KHÔNG đụng `kb/incidents/retro/` (đếm riêng, không nằm trong bảng YYYY-MM) hay
`_open-not-yet-hardened.md` (đếm riêng, không phải 1 sự cố có ngày/tháng).
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INCIDENTS_DIR = os.path.join(ROOT, "kb", "incidents")
INDEX_FP = os.path.join(INCIDENTS_DIR, "index.md")

MONTH_RE = re.compile(r"^### (\d{4}-\d{2})\s*$", re.M)
LINK_RE = re.compile(r"\| *(\d{4}-\d{2}-\d{2}) *\| *\[(.+?)\]\((\d{4}-\d{2}/[^)]+\.md)\) *\| *(\S+) *\|")


def real_files():
    """{relpath ('2026-08/xxx.md'): abspath} for every incident file, excluding retro/open-items."""
    out = {}
    for fp in glob.glob(os.path.join(INCIDENTS_DIR, "20*", "*.md")):
        month_dir = os.path.basename(os.path.dirname(fp))
        if not re.match(r"^\d{4}-\d{2}$", month_dir):
            continue
        rel = "%s/%s" % (month_dir, os.path.basename(fp))
        out[rel] = fp
    return out


def linked_rows():
    """[(date, title, relpath, status)] parsed from every table row in index.md, in file order."""
    with open(INDEX_FP, encoding="utf-8") as f:
        text = f.read()
    return LINK_RE.findall(text), text


def parse_frontmatter(fp):
    with open(fp, encoding="utf-8") as f:
        text = f.read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    fm = {}
    if not m:
        return fm
    for key in ("date", "status", "title"):
        km = re.search(r"^%s: *>?-? *\n?( .*(?:\n +\S.*)*|\S.*)$" % key, m.group(1), re.M)
        if km:
            val = km.group(1).strip()
            # multi-line ">-" block scalar: join lines, collapse internal whitespace
            val = re.sub(r"\s+", " ", val).strip()
            fm[key] = val
    return fm


def cmd_check(real, linked, index_text):
    linked_paths = {row[2] for row in linked}
    missing = sorted(set(real) - linked_paths)   # on disk, not linked
    orphaned = sorted(linked_paths - set(real))   # linked, file gone
    if not missing and not orphaned:
        print("OK: %d file thật khớp đúng %d dòng trong index.md — 0 drift." %
              (len(real), len(linked_paths)))
        return 0
    if missing:
        print("THIẾU trong index.md (%d):" % len(missing))
        for rel in missing:
            print("  %s" % rel)
    if orphaned:
        print("ORPHAN trong index.md — file không còn tồn tại (%d):" % len(orphaned))
        for rel in orphaned:
            print("  %s" % rel)
    return 1


def build_row(rel, fp):
    fm = parse_frontmatter(fp)
    date = fm.get("date", rel.split("/")[1][:10])
    title = fm.get("title", rel)
    status = fm.get("status", "?")
    return "| %s | [%s](%s) | %s |" % (date, title, rel, status)


def cmd_fix(real, linked, index_text):
    linked_paths = {row[2] for row in linked}
    missing = sorted(set(real) - linked_paths)
    orphaned = sorted(linked_paths - set(real))
    if not missing and not orphaned:
        print("OK: không có drift, không cần sửa gì.")
        return 0

    lines = index_text.split("\n")

    # 1) Xoá orphan rows (match nguyên dòng chứa relpath đó).
    if orphaned:
        lines = [ln for ln in lines if not any(rel in ln for rel in orphaned)]
        print("Đã xoá %d dòng orphan." % len(orphaned))

    # 2) Chèn missing rows — nhóm theo tháng, chèn ngay dưới header bảng của đúng tháng đó
    #    (dòng `| Ngày | Sự cố | status |` + dòng gạch `|---|---|---|`), sắp NGÀY MỚI NHẤT TRƯỚC.
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
            # tìm dòng gạch ngay sau header (bảng đã có) để chèn NGAY SAU nó
            insert_at = None
            for j in range(header_idx, min(header_idx + 6, len(lines))):
                if lines[j].startswith("|---"):
                    insert_at = j + 1
                    break
            if insert_at is None:
                # bảng chưa có (chỉ có header tháng) — tạo mới ngay dưới header
                insert_at = header_idx + 1
                lines[insert_at:insert_at] = ["", "| Ngày | Sự cố | status |", "|---|---|---|"]
                insert_at += 3
            lines[insert_at:insert_at] = rows
        else:
            # tháng chưa tồn tại trong index — tạo section mới, chèn theo đúng vị trí giảm dần
            # (tìm section tháng đầu tiên NHỎ HƠN, chèn ngay trước nó; không có thì thêm cuối
            # phần "## Sự cố (mới nhất trước)")
            new_section = ["### %s" % month, "", "| Ngày | Sự cố | status |", "|---|---|---|"] + rows + [""]
            insert_at = len(lines)
            for i, ln in enumerate(lines):
                mm = MONTH_RE.match(ln)
                if mm and mm.group(1) < month:
                    insert_at = i
                    break
            lines[insert_at:insert_at] = new_section
        print("Đã chèn %d dòng vào tháng %s." % (len(rows), month))

    new_text = "\n".join(lines)

    # 3) Cập nhật entries: N trong frontmatter — đếm THẬT, không đoán.
    n_incidents = len(real)  # sau fix, = số dòng sẽ có trong bảng
    n_retro = len(glob.glob(os.path.join(INCIDENTS_DIR, "retro", "*.md")))
    n_open = 1 if os.path.exists(os.path.join(INCIDENTS_DIR, "_open-not-yet-hardened.md")) else 0
    total = n_incidents + n_retro + n_open
    new_text = re.sub(
        r"^entries: .*$",
        "entries: %d file (%d sự cố + %d RETRO + %d mục open-items chung)" %
        (total, n_incidents, n_retro, n_open),
        new_text, count=1, flags=re.M)

    with open(INDEX_FP, "w", encoding="utf-8") as f:
        f.write(new_text)
    print("Đã ghi kb/incidents/index.md — entries: %d (%d sự cố + %d RETRO + %d open-items)." %
          (total, n_incidents, n_retro, n_open))
    return 0


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("--check", "--fix"):
        sys.stderr.write("usage: incidents_index_sync.py --check|--fix\n")
        return 2
    real = real_files()
    linked, index_text = linked_rows()
    if sys.argv[1] == "--check":
        return cmd_check(real, linked, index_text)
    return cmd_fix(real, linked, index_text)


if __name__ == "__main__":
    sys.exit(main())
