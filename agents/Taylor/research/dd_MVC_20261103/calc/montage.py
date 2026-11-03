import sys; sys.path.insert(0,"/tmp/pdflib"); import pymupdf
f,start,end,out,z=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4],float(sys.argv[5])
ROT=int(sys.argv[6]) if len(sys.argv)>6 else 0
d=pymupdf.open(f); pages=list(range(start-1,min(end,d.page_count)))
pw,ph=d[0].rect.width*z,d[0].rect.height*z; cols=4; rows=(len(pages)+cols-1)//cols
doc=pymupdf.open(); pg=doc.new_page(width=pw*cols,height=ph*rows)
for k,i in enumerate(pages):
    r=pymupdf.Rect((k%cols)*pw,(k//cols)*ph,(k%cols+1)*pw,(k//cols+1)*ph); pg.show_pdf_page(r,d,i,rotate=ROT)
    pg.insert_text((r.x0+5,r.y0+12),f"p{i+1}",fontsize=12,color=(1,0,0))
pg.get_pixmap(matrix=pymupdf.Matrix(1,1)).save(out)
