import sys; sys.path.insert(0,'/tmp/pdflib'); import pymupdf
pdf, pages, out = sys.argv[1], sys.argv[2], sys.argv[3]
d = pymupdf.open(pdf); print(pdf, d.page_count)
ps = range(d.page_count) if pages=='all' else [int(x) for x in pages.split(',')]
z = float(sys.argv[4]) if len(sys.argv)>4 else 1.6
for p in ps:
    pix = d[p].get_pixmap(matrix=pymupdf.Matrix(z,z)); pix.save(f"{out}_p{p+1:02d}.png")
