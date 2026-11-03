# render trang PDF scan ra PNG (xoay neu can). usage: render.py file page1,page2 outprefix zoom rotate
import sys; sys.path.insert(0,"/tmp/pdflib"); import pymupdf
f,pages,out,z,rot=sys.argv[1],sys.argv[2],sys.argv[3],float(sys.argv[4]),int(sys.argv[5])
d=pymupdf.open(f)
for p in [int(x) for x in pages.split(",")]:
    pg=d[p-1]; pg.set_rotation((pg.rotation+rot)%360)
    pg.get_pixmap(matrix=pymupdf.Matrix(z,z)).save(f"{out}_p{p}.png")
