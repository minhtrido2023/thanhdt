import sys; sys.path.insert(0,'/tmp/pdflib')
import fitz
pdf, pages, out = sys.argv[1], sys.argv[2], sys.argv[3]
d = fitz.open(pdf)
if pages == 'info':
    print(pdf, d.page_count, sum(len(p.get_text()) for p in d)); sys.exit()
for p in pages.split(','):
    i=int(p)-1
    pix=d[i].get_pixmap(matrix=fitz.Matrix(1.6,1.6))
    pix.save(f"{out}_p{p}.png")
