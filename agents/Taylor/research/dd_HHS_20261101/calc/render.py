import sys; sys.path.insert(0,'/tmp/pdflib')
import fitz
pdf, prefix, pages = sys.argv[1], sys.argv[2], sys.argv[3]
d = fitz.open(pdf); print('pages', len(d))
if pages=='count': sys.exit()
rng=[]
for part in pages.split(','):
    a,_,b=part.partition('-'); rng += list(range(int(a), int(b or a)+1))
for p in rng:
    pix = d[p-1].get_pixmap(matrix=fitz.Matrix(1.6,1.6)); pix.save(f'img/{prefix}_p{p}.png')
