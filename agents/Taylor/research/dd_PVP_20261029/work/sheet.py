import sys, io; sys.path.insert(0,'/tmp/pdflib'); sys.path.append('/home/trido/.local/lib/python3.10/site-packages'); import pymupdf
from PIL import Image
pdf,out,per,z=sys.argv[1],sys.argv[2],int(sys.argv[3]),float(sys.argv[4])
d=pymupdf.open(pdf); n=d.page_count
for s in range(0,n,per):
    ims=[Image.open(io.BytesIO(d[p].get_pixmap(matrix=pymupdf.Matrix(z,z)).tobytes('png'))) for p in range(s,min(s+per,n))]
    w,h=ims[0].size; cols=3; rows=(len(ims)+cols-1)//cols
    sh=Image.new('RGB',(w*cols,h*rows),'white')
    for i,im in enumerate(ims): sh.paste(im,((i%cols)*w,(i//cols)*h))
    sh.save(f"{out}_s{s+1:02d}-{min(s+per,n):02d}.png")
