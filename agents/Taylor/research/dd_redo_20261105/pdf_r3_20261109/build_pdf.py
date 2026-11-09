import sys, unicodedata, os
sys.path.insert(0, '/tmp/pdflib')
import pymupdf
from markdown_it import MarkdownIt
R = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/dd_redo_20261105'
OUT = '/tmp/ddpdf_20261109/out'; os.makedirs(OUT, exist_ok=True)
FONT = '/home/trido/.claude/skills/dd-investor-report/fonts/'
jobs = {
 'SZL': ('SZL/REPORT_r3c.md', 'SZL/ERRATA_final_skeptic_20261109.md'),
 'FPT': ('FPT/REPORT_r3.md', 'FPT/ERRATA_final_skeptic_20261109.md'),
 'HHS': ('HHS/REPORT_r3.md', 'HHS/ERRATA_final_skeptic_20261109.md'),
 'SIP': ('SIP/REPORT_r3.md', 'SIP/ERRATA_final_skeptic_20261109.md'),
 'TCH': ('TCH/REPORT_r3b.md', 'TCH/ERRATA_final_20261109.md'),
 'MVC': ('MVC/REPORT_r3.md', 'MVC/ERRATA_final_skeptic_20261109.md'),
}
CSS = """
body{font-family:bvp;font-size:8.6pt;line-height:1.3}
h1{font-size:15pt;color:#12355b;margin:0 0 4pt 0}
h2{font-size:11.5pt;color:#12355b;margin:10pt 0 3pt 0;border-bottom:0.6pt solid #12355b}
h3{font-size:9.8pt;color:#1d4e89;margin:7pt 0 2pt 0}
p{margin:2pt 0 3pt 0}
table{border-collapse:collapse;width:100%;margin:3pt 0 5pt 0}
th{background:#e6edf5;font-weight:bold;border:0.5pt solid #9aa9ba;padding:2pt;font-size:7.6pt}
td{border:0.5pt solid #b8c2cf;padding:2pt;font-size:7.6pt;vertical-align:top}
li{margin:1pt 0}
code{font-size:7.6pt;color:#444}
"""
md = MarkdownIt('commonmark').enable('table')
for t,(rep,err) in jobs.items():
    body = open(f'{R}/{rep}', encoding='utf-8').read()
    e = open(f'{R}/{err}', encoding='utf-8').read()
    text = unicodedata.normalize('NFC', body + '\n\n---\n\n## Phụ lục — Errata cuối (09/11/2026)\n\n' + e.split('\n',1)[1] if e.startswith('#') else body + '\n\n' + e)
    html = md.render(text)
    arch = pymupdf.Archive(FONT)
    css = CSS + "\n@font-face{font-family:bvp;src:url(BeVietnamPro-Regular.ttf)}@font-face{font-family:bvp;font-weight:bold;src:url(BeVietnamPro-Bold.ttf)}"
    story = pymupdf.Story(html=html, user_css=css, archive=arch)
    path = f'{OUT}/{t}_DD_redo_r3_20261109.pdf'
    w = pymupdf.DocumentWriter(path)
    mb = pymupdf.paper_rect('a4-l'); where = mb + (28,28,-28,-30)
    more = 1; n=0
    while more:
        dev = w.begin_page(mb)
        more, _ = story.place(where)
        story.draw(dev); w.end_page(); n+=1
    w.close()
    print(t, n, 'pages', os.path.getsize(path))
