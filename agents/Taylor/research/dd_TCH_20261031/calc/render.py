import sys; sys.path.insert(0,'/tmp/pdflib')
import pymupdf as fitz
pdf, pages, prefix = sys.argv[1], sys.argv[2], sys.argv[3]
z = float(sys.argv[4]) if len(sys.argv)>4 else 1.6
d = fitz.open(pdf)
if pages=='count': print(d.page_count); sys.exit()
for p in [int(x) for x in pages.split(',')]:
    pix = d[p-1].get_pixmap(matrix=fitz.Matrix(z,z)); pix.save(f"{prefix}_p{p}.png"); print(f"{prefix}_p{p}.png")
