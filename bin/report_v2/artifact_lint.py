"""report_v2.artifact_lint — kiểm cơ học artifact báo cáo TRƯỚC KHI gửi (report_delivery_gate +
send_report_email dùng chung, để hai bên không trôi khỏi nhau).

Vì sao (REPORT_STYLE_V2 + DIFF_VS_OLD (a)): báo cáo tuần 26–30/10 lọt cổng COMPLETE dù in repr tuple
`['| Nguồn | Đóng góp |\\n…', 515443.0]`. Luật văn xuôi không chặn được ⇒ chặn bằng code.

  • MỌI báo cáo .md: chặn repr tuple/list của bảng (`['|`, `\\n|`).
  • Báo cáo v2 (có dòng `report_v2_manifest:`): .md khai sha256 PDF; manifest khai sha256 PDF/HTML/ảnh.
    Lệch bất kỳ ⇒ CHẶN (file đã bị sửa sau khi dựng). PDF + HTML: chặn markdown thô (`**`, dòng `|---`,
    `\\n|`, `['|`, `# `, `![`), `None`/`nan`, tên nội bộ (Livermore/Taylor/Bobby/LAG/PARK/DT5G/PEAD…),
    font PDF không phải Be Vietnam Pro hoặc không nhúng, số trang > trần.
Trả về danh sách vấn đề (rỗng = sạch). Không gửi gì, không đọc mạng.
"""
import hashlib
import html as H
import json
import os
import re

MANIFEST_TAG = "report_v2_manifest:"
TAG_RE = re.compile(r"<!--\s*report_v2_manifest:\s*(\S+)\s+pdf_sha256=([0-9a-f]{64})\s+pdf=(\S+)\s*-->")
REPR_MD = [r"\['\|", r"\\n\|"]
RAW_MD = [r"\['\|", r"\*\*", r"^\s*\|[-:| ]+\|\s*$", r"^#{1,4} ", r"\\n\|", r"!\[", r"\bNone\b", r"\bnan\b"]
INTERNAL = re.compile(r"\b(Livermore|Taylor|Bobby|Winston|Wendy|Spyros|Mafee|DollarBill|LAG|PARK|DT5G|DT4|PEAD|"
                      r"CAPIT|custom30V?|tav2_\w+|BigQuery|universe_pit|dnse_raw\w*|nav_history\w*|Traceback|"
                      r"[\w-]+\.(?:jsonl|csv|py|pkl))\b")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_tag(md_text):
    """→ (manifest_rel, pdf_sha256, pdf_rel) | None."""
    m = TAG_RE.search(md_text)
    return (m.group(1), m.group(2), m.group(3)) if m else None


def strip_tag(md_text):
    """Bỏ dòng chú thích máy đọc trước khi đăng Discord (Discord không ẩn HTML comment)."""
    return TAG_RE.sub("", md_text).rstrip() + "\n"


def load_v2(md_path):
    """→ (manifest, dir) nếu .md là báo cáo v2, None nếu không. Lệch sha ⇒ ValueError."""
    with open(md_path, encoding="utf-8") as fh:
        text = fh.read()
    tag = parse_tag(text)
    if not tag:
        return None
    base = os.path.dirname(os.path.abspath(md_path))
    man_path = os.path.normpath(os.path.join(base, tag[0]))
    with open(man_path, encoding="utf-8") as fh:
        man = json.load(fh)
    d = os.path.dirname(man_path)
    pdf = os.path.join(d, man["pdf"])
    if os.path.normpath(os.path.join(base, tag[2])) != os.path.normpath(pdf):
        raise ValueError(f"đường dẫn PDF khai trong .md ({tag[2]}) ≠ manifest ({man['pdf']})")
    got = sha256(pdf)
    if got != tag[1] or got != man["pdf_sha256"]:
        raise ValueError(f"sha256 PDF lệch: file {got[:12]} · .md khai {tag[1][:12]} · manifest {man['pdf_sha256'][:12]}")
    if sha256(os.path.join(d, man["html"])) != man["html_sha256"]:
        raise ValueError("sha256 HTML email lệch manifest (file bị sửa sau khi dựng)")
    for cid, meta in man.get("cid", {}).items():
        if sha256(os.path.join(d, meta["file"])) != meta["sha256"]:
            raise ValueError(f"sha256 ảnh {cid} ({meta['file']}) lệch manifest")
    return man, d


def _pdf_scan(pdf):
    import pymupdf
    texts, fonts = [], set()
    with pymupdf.open(pdf) as doc:
        for p in doc:
            texts.append(p.get_text())
            for f in p.get_fonts(full=True):
                # f = (xref, ext, type, basefont, name, encoding, ...); ext "n/a" ⇒ không nhúng
                fonts.add((f[3], f[1] != "n/a" and f[0] > 0))
        n = doc.page_count
    return texts, fonts, n


def lint_md(md_text):
    return [f".md có repr bảng/tuple ({pat}) gần: {md_text[max(0, m.start() - 30):m.end() + 30]!r}"
            for pat in REPR_MD for m in re.finditer(pat, md_text)][:5]


def lint_v2(md_path, investor_facing):
    """→ [vấn đề]. md_path không phải v2 ⇒ chỉ lint_md."""
    with open(md_path, encoding="utf-8") as fh:
        text = fh.read()
    probs = lint_md(text)
    try:
        got = load_v2(md_path)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        return probs + [f"artifact v2 không kiểm được: {type(exc).__name__}: {exc}"]
    if got is None:
        return probs
    man, d = got
    texts, fonts, n = _pdf_scan(os.path.join(d, man["pdf"]))
    cap = man.get("page_cap")
    if cap and n > cap:
        probs.append(f"PDF {n} trang > trần {cap}")
    bad_fonts = sorted({f for f, _ in fonts if "BeVietnamPro" not in f.replace(" ", "")})
    not_emb = sorted({f for f, emb in fonts if not emb})
    if bad_fonts:
        probs.append(f"PDF có font không phải Be Vietnam Pro: {bad_fonts}")
    if not_emb:
        probs.append(f"PDF có font KHÔNG nhúng: {not_emb}")
    with open(os.path.join(d, man["html"]), encoding="utf-8") as fh:
        raw_html = fh.read()
    html_text = H.unescape(re.sub(r"<style.*?</style>", " ", raw_html, flags=re.S))
    html_text = re.sub(r"<br\s*/?>|</(p|li|tr|h\d)>", "\n", html_text)
    html_text = re.sub(r"<[^>]+>", " ", html_text)
    for where, t in [(f"PDF trang {i + 1}", x) for i, x in enumerate(texts)] + [("HTML email", html_text)]:
        for pat in RAW_MD:
            m = re.search(pat, t, flags=re.M)
            if m:
                probs.append(f"{where}: markdown thô/giá trị rỗng ({pat}) gần {t[max(0, m.start() - 25):m.end() + 25]!r}")
        if investor_facing:
            m = INTERNAL.search(t)
            if m:
                probs.append(f"{where}: tên nội bộ '{m.group(0)}' trong báo cáo nhà đầu tư")
    for m in re.finditer(r"<img\b[^>]*>", raw_html):
        tag = m.group(0)
        if not re.search(r'\balt="[^"]*"', tag) or not re.search(r'src="cid:[^"]+"', tag):
            probs.append(f"HTML email: thẻ ảnh hỏng {tag[:80]!r}")
    return probs
