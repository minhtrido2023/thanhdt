import sys; sys.path.insert(0,'/tmp/pdflib')
import pymupdf as fitz
pdf, pages, out, zoom = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]) if len(sys.argv)>4 else 1.6
d=fitz.open(pdf)
if pages=='info': print(pdf, d.page_count); sys.exit()
for p in pages.split(','):
    a,b=(p.split('-')+[p])[:2]
    for i in range(int(a),int(b)+1):
        d[i-1].get_pixmap(matrix=fitz.Matrix(zoom,zoom)).save(f"{out}_{i:02d}.png")
