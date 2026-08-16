#!/usr/bin/env python3
"""render_report_html.py <report.md> [--out out.html]

Chuyển 1 báo cáo markdown (định dạng Taylor vẫn dùng: #/##/### header, bảng pipe,
**bold**, danh sách, footnote \\*) thành email HTML theo đúng chuẩn trình bày ngành quản
lý đầu tư — KHÔNG tự sáng tác, dựa trên nghiên cứu thật (xem báo cáo cho user, dẫn nguồn):

- CFA Institute Asset Manager Code (Performance & Valuation): báo cáo phải "fair, accurate,
  relevant, timely, and complete"; nguyên tắc "current, consistent, easy to get, easy to
  understand" — nghĩa là bảng số liệu đầu tiên, không phải bơi qua văn xuôi mới tới số.
- GIPS Standards: đưa performance + benchmark cạnh nhau ngay từ đầu, disclosure rõ ràng,
  risk metric có ngữ cảnh (không chỉ 1 con số trôi nổi).
- Quy ước "tear sheet"/fund fact sheet: 1 khối tóm tắt (masthead + bảng số liệu) ở TRÊN
  CÙNG, bố cục sạch, bảng có border/zebra rõ ràng thay vì text thô.
- Quy ước thư gửi nhà đầu tư (investor letter): Performance Summary -> Portfolio/Market
  Commentary -> Risk -> Outlook -> Disclaimer chuẩn cuối thư.
- Disclaimer chuẩn ngành ("past performance is not indicative of future results", "for
  informational purposes only") — luôn xuất hiện cuối thư thật.

Sửa CHÍNH của bản này so với plain-text markdown cũ:
  1. Render bảng/heading THẬT (HTML) thay vì để nguyên ký tự #, |, **, --- (nhìn như
     markdown chưa qua xử lý = "kiểu LLM" đúng như user phản ánh).
  2. Giảm mật độ in đậm trong VĂN XUÔI: **bold** bọc CẢ CÂU dài (>8 "từ") bị hạ xuống
     chữ thường -- đúng quy ước thư thật (chỉ bold nhãn ngắn/số liệu, không bold nguyên
     câu). Bold trong Ô BẢNG hoặc gạch đầu dòng NGẮN thì giữ nguyên (đúng vai trò làm nổi
     số liệu, không phải nhấn mạnh cảm xúc).
"""
import argparse
import base64
import html
import os
import re
import sys

FOOTNOTE_MARK = ""  # placeholder tránh escaped \* bị bắt nhầm là bold


def protect_escapes(text):
    text = text.replace(r"\*\*", FOOTNOTE_MARK * 2)
    text = text.replace(r"\*", FOOTNOTE_MARK)
    return text


def restore_escapes(text):
    return text.replace(FOOTNOTE_MARK * 2, "**").replace(FOOTNOTE_MARK, "*")


def word_count(s):
    return len(re.findall(r"\S+", s))


def render_inline(text, in_table_or_list=False):
    text = protect_escapes(text)
    text = html.escape(text, quote=False)

    def bold_sub(m):
        inner = m.group(1)
        if in_table_or_list or word_count(inner) <= 8:
            return f"<strong>{inner}</strong>"
        return inner  # cả câu dài bị bold -- hạ về chữ thường (quy ước thư thật)

    text = re.sub(r"\*\*(.+?)\*\*", bold_sub, text)
    text = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em>\1</em>", text)
    text = restore_escapes(text)
    # Bất kỳ dấu * còn sót lại (không khớp cặp bold/italic) là marker chú thích chân
    # trang kiểu học thuật (*, **) — hiển thị dạng superscript thay vì để dấu * trần
    # trông như markdown lỗi.
    text = re.sub(r"\*{1,2}", lambda m: f"<sup>{m.group(0)}</sup>", text)
    return text


def parse_table(lines):
    header = [c.strip() for c in lines[0].strip().strip("|").split("|")]
    aligns = [c.strip() for c in lines[1].strip().strip("|").split("|")]
    align_css = []
    for a in aligns:
        if a.endswith(":") and a.startswith(":"):
            align_css.append("center")
        elif a.endswith(":"):
            align_css.append("right")
        else:
            align_css.append("left")
    rows = []
    for ln in lines[2:]:
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        rows.append(cells)
    return header, align_css, rows


def table_html(lines):
    header, align_css, rows = parse_table(lines)
    out = ['<table style="border-collapse:collapse;width:100%;margin:14px 0;font-size:13.5px;">']
    out.append("<thead><tr>")
    for i, h in enumerate(header):
        a = align_css[i] if i < len(align_css) else "left"
        out.append(f'<th style="text-align:{a};padding:6px 10px;background:#1c2b3a;'
                    f'color:#f2f4f6;border:1px solid #1c2b3a;font-weight:600;">'
                    f'{render_inline(h, True)}</th>')
    out.append("</tr></thead><tbody>")
    for ri, row in enumerate(rows):
        bg = "#f7f8fa" if ri % 2 == 1 else "#ffffff"
        out.append(f'<tr style="background:{bg};">')
        for i, cell in enumerate(row):
            a = align_css[i] if i < len(align_css) else "left"
            out.append(f'<td style="text-align:{a};padding:6px 10px;border:1px solid #dfe3e8;'
                        f'color:#1c2b3a;">{render_inline(cell, True)}</td>')
        out.append("</tr>")
    out.append("</tbody></table>")
    return "\n".join(out)


def is_table_line(ln):
    return ln.strip().startswith("|") or ("|" in ln and ln.count("|") >= 2)


def is_sep_row(ln):
    return bool(re.fullmatch(r"\s*\|?[\s:|-]+\|?\s*", ln)) and "-" in ln


def is_block_start(stripped):
    """Dòng bắt đầu 1 block-level construct mới (header/hr/table/list-item) — paragraph/
    list-item continuation KHÔNG được nuốt các dòng này vào."""
    if stripped == "":
        return True
    if re.fullmatch(r"-{3,}", stripped):
        return True
    if re.match(r"^#{1,4}\s+", stripped):
        return True
    if re.match(r"^[-*]\s+", stripped):
        return True
    if re.match(r"^\d+\.\s+", stripped) and not re.search(r"·\s*\d+\.", stripped):
        return True  # mục lục kiểu "1. A · 2. B" nén nhiều mục KHÔNG tính là list-item mới
    if is_table_line(stripped):
        return True
    return False


def image_html(m, base_dir=None):
    alt = m.group(1)
    src = m.group(2).strip()
    if src.lower().startswith("data:"):
        return f'<img src="{html.escape(src)}" alt="{html.escape(alt)}" ' \
               f'style="max-width:100%;height:auto;margin:14px 0;">'
    path = src if os.path.isabs(src) else os.path.join(base_dir or ".", src)
    if not os.path.isfile(path):
        return f'<p style="color:#8a2020;">[Ảnh thiếu: {html.escape(alt)} — {html.escape(path)}]</p>'
    ext = os.path.splitext(path)[1].lower()
    mime = "image/png" if ext == ".png" else "image/jpeg" if ext in (".jpg", ".jpeg") else "image/svg+xml"
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    return f'<img src="data:{mime};base64,{data}" alt="{html.escape(alt)}" ' \
           f'style="max-width:100%;height:auto;margin:14px 0;border:1px solid #dfe3e8;">'


def render_body(md_text, base_dir=None):
    lines = md_text.split("\n")
    out = []
    i = 0
    list_tag = None  # None | "ul" | "ol"

    def close_list():
        nonlocal list_tag
        if list_tag:
            out.append(f"</{list_tag}>")
            list_tag = None

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped == "":
            close_list()
            i += 1
            continue

        image_match = re.fullmatch(r"!\[([^\]]*)\]\(([^)]+)\)", stripped)
        if image_match:
            close_list()
            out.append(image_html(image_match, base_dir))
            i += 1
            continue

        if re.fullmatch(r"-{3,}", stripped):
            close_list()
            out.append('<hr style="border:none;border-top:1px solid #d5d9de;margin:22px 0;">')
            i += 1
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            close_list()
            level = len(m.group(1))
            content = render_inline(m.group(2))
            sizes = {1: "22px", 2: "18px", 3: "15.5px", 4: "14px"}
            colors = {1: "#0d1b2a", 2: "#13293d", 3: "#1c2b3a", 4: "#1c2b3a"}
            out.append(f'<h{min(level,4)} style="font-size:{sizes.get(level,"14px")};'
                        f'color:{colors.get(level,"#1c2b3a")};margin:20px 0 8px 0;'
                        f'font-family:Georgia,\'Times New Roman\',serif;">{content}</h{min(level,4)}>')
            i += 1
            continue

        if is_table_line(line) and i + 1 < len(lines) and is_sep_row(lines[i + 1]):
            block = [line]
            j = i + 1
            while j < len(lines) and is_table_line(lines[j]):
                block.append(lines[j])
                j += 1
            close_list()
            out.append(table_html(block))
            i = j
            continue

        # Mục lục kiểu "1. A · 2. B · 3. C" nén nhiều mục/dòng bằng dấu · KHÔNG phải
        # list item thật (mỗi dòng không phải 1 mục riêng) — coi là đoạn văn thường,
        # tránh xé thành nhiều <li> cụt đầu (bug tự bắt khi kiểm thử mục 'MỤC LỤC').
        is_numbered = re.match(r"^\d+\.\s+", stripped)
        looks_like_inline_toc = bool(is_numbered and re.search(r"·\s*\d+\.", stripped))

        lm = None if looks_like_inline_toc else (
            re.match(r"^[-*]\s+(.*)$", stripped) or re.match(r"^\d+\.\s+(.*)$", stripped))
        if lm:
            wanted_tag = "ol" if is_numbered else "ul"
            if list_tag != wanted_tag:
                close_list()
                out.append(f'<{wanted_tag} style="margin:8px 0;padding-left:22px;">')
                list_tag = wanted_tag
            # gộp các dòng tiếp nối (soft-wrap) vào CÙNG 1 list item, dừng khi gặp
            # block-level construct mới (item kế tiếp, header, hr, bảng, dòng trống)
            item_lines = [lm.group(1)]
            j = i + 1
            while j < len(lines) and not is_block_start(lines[j].strip()):
                item_lines.append(lines[j].strip())
                j += 1
            out.append(f'<li style="margin:4px 0;line-height:1.55;">'
                        f'{render_inline(" ".join(item_lines), True)}</li>')
            i = j
            continue

        close_list()
        # gộp các dòng tiếp nối (soft-wrap trong .md gốc) vào CÙNG 1 đoạn văn thật —
        # markdown coi 1 block liên tục các dòng không-trống là 1 paragraph, KHÔNG phải
        # mỗi dòng 1 đoạn (bug đã tự bắt khi kiểm thử: câu bị cắt vụn thành nhiều <p>).
        para_lines = [stripped]
        j = i + 1
        while j < len(lines) and not is_block_start(lines[j].strip()):
            para_lines.append(lines[j].strip())
            j += 1
        out.append(f'<p style="margin:8px 0;line-height:1.6;color:#26333f;">'
                    f'{render_inline(" ".join(para_lines))}</p>')
        i = j

    close_list()
    return "\n".join(out)


DISCLAIMER = """
<div style="margin-top:32px;padding-top:16px;border-top:2px solid #1c2b3a;
            font-size:11px;color:#6b7680;line-height:1.6;">
  <p style="margin:4px 0;"><strong>Miễn trừ trách nhiệm:</strong> Tài liệu này chỉ nhằm mục đích
  thông tin nội bộ, không phải lời khuyên đầu tư hay đề nghị mua/bán bất kỳ chứng khoán nào
  (for informational purposes only; not investment advice or an offer to buy or sell any
  security).</p>
  <p style="margin:4px 0;">Hiệu suất quá khứ không đảm bảo hoặc dự báo hiệu suất tương lai
  (past performance is not indicative of future results). Số liệu hiệu suất trong giai đoạn ngắn
  (dưới 12 tháng) có ý nghĩa thống kê hạn chế và không nên ngoại suy.</p>
  <p style="margin:4px 0;">Phương pháp tính toán, nguồn dữ liệu và các khoảng trống/giới hạn số
  liệu đã biết được công bố đầy đủ trong phần phụ lục của báo cáo này.</p>
</div>
"""


def render_html(md_text, title, base_dir=None):
    body = render_body(md_text, base_dir)
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#eef1f4;">
<div style="max-width:760px;margin:0 auto;background:#ffffff;
            font-family:Arial,Helvetica,sans-serif;">
  <div style="background:#0d1b2a;padding:20px 28px;">
    <div style="color:#9fb0c3;font-size:11px;letter-spacing:1.5px;text-transform:uppercase;">
      Báo cáo hiệu suất &amp; vận hành</div>
    <div style="color:#ffffff;font-size:20px;font-weight:600;margin-top:4px;
                font-family:Georgia,'Times New Roman',serif;">{html.escape(title)}</div>
  </div>
  <div style="padding:22px 28px;">
{body}
{DISCLAIMER}
  </div>
</div>
</body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("report_path")
    ap.add_argument("--out")
    ap.add_argument("--title")
    args = ap.parse_args()

    with open(args.report_path, encoding="utf-8") as f:
        md_text = f.read()

    title = args.title
    if not title:
        first_line = md_text.split("\n", 1)[0]
        title = re.sub(r"^#+\s*", "", first_line).strip()

    html_out = render_html(md_text, title, os.path.dirname(os.path.abspath(args.report_path)))

    out_path = args.out or (os.path.splitext(args.report_path)[0] + ".html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"✅ Đã render {out_path}")


if __name__ == "__main__":
    main()
