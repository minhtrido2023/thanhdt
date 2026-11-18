import sys; sys.path.insert(0,'/tmp/pdflib'); import pymupdf
f,tag,pages=sys.argv[1],sys.argv[2],sys.argv[3]
d=pymupdf.open(f); print(tag,len(d))
ps=range(len(d)) if pages=='all' else [int(x)-1 for x in pages.split(',')]
for i in ps:
    d[i].get_pixmap(matrix=pymupdf.Matrix(1.6,1.6)).save(f'png/{tag}_p{i+1:02d}.png')
