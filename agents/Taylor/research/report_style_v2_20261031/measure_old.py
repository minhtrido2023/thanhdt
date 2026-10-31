"""Đo bản cũ (md) để so: số từ (tất cả / văn xuôi), số hình, số bảng, số trang khi quy đổi A4 cùng font/cỡ
chữ bằng chính build_pdf (khung template SCL md_to_html). Ghi recon/old_metrics.json."""
import importlib.util, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build_report_v2 as R
spec = importlib.util.spec_from_file_location("tpl", f"{R.SKILL}/templates/build_report_SCL_example.py")
T = importlib.util.module_from_spec(spec); spec.loader.exec_module(T)
REP = "/home/trido/thanhdt/WorkingClaude/mike/reports"
OLD = {"weekly": "SpaceX_weekly_report_2026-10-26_to_2026-10-30.md", "daily": "SpaceX_daily_report_2026-10-30.md",
       "monthly_sep (tham chiếu cho quý)": "SpaceX_monthly_report_2026-09.md",
       "weekly_ZaloPay": "ZaloPay_weekly_report_2026-10-26_to_2026-10-30.md"}
out = {}
for k, f in OLD.items():
    md = open(f"{REP}/{f}", encoding="utf-8").read()
    lines = md.split("\n")
    tables = sum(1 for i, l in enumerate(lines) if re.fullmatch(r"\|[\s:|-]+\|", l.strip()))
    imgs = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", md)
    prose = [l for l in lines if l.strip() and not l.strip().startswith("|") and not l.strip().startswith("![")]
    blocks = []
    for part in re.split(r"(!\[[^\]]*\]\([^)]+\))", md):
        m = re.fullmatch(r"!\[[^\]]*\]\(([^)]+)\)", part)
        if m:
            blocks.append(R.img(os.path.join(REP, m.group(1)))); continue
        h = T.md_to_html(part).replace("<PAGEBREAK/>", "")
        blocks += [x for x in re.split(r"\n(?=<h\d>|<p>|<table>|<ul>|<ol>)", h) if x.strip()]
    pdf = f"{HERE}/recon/old_{k.split(' ')[0]}.pdf"
    n = R.build_pdf(blocks, pdf, header_left=f, footer="quy đổi A4 để so sánh")
    out[k] = {"file": f, "words_all": len(md.split()), "words_prose": len(" ".join(prose).split()), "charts": len(imgs),
              "tables": tables, "pages_a4_equiv": n, "tuple_repr": "['|" in md,
              "longest_paragraph_words": max(len(pg.split()) for pg in re.split(r"\n\s*\n", md)
                                             if pg.strip() and not pg.strip().startswith(("|", "![", "#")))}
json.dump(out, open(f"{HERE}/recon/old_metrics.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
