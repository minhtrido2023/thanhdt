import sys; sys.path.insert(0,'/tmp/pdflib')
import fitz
pdf, pages, tag = sys.argv[1], sys.argv[2], sys.argv[3]
d = fitz.open(pdf)
a,b = map(int, pages.split('-')) if '-' in pages else (int(pages),int(pages))
for p in range(a,b+1):
    pix = d[p-1].get_pixmap(matrix=fitz.Matrix(1.6,1.6))
    pix.save(f'png/{tag}_p{p:02d}.png')
print(len(d))
