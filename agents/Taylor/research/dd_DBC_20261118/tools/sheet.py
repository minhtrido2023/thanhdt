import sys; sys.path.insert(0,'/tmp/pdflib')
import pymupdf as fitz
pdf,start,end,out=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]
cols=int(sys.argv[5]) if len(sys.argv)>5 else 4
src=fitz.open(pdf); n=end-start+1; rows=(n+cols-1)//cols
W,H=595/2,842/2
doc=fitz.open(); pg=doc.new_page(width=W*cols,height=H*rows)
for k,i in enumerate(range(start,end+1)):
    r=fitz.Rect((k%cols)*W,(k//cols)*H,(k%cols+1)*W,(k//cols+1)*H)
    pg.show_pdf_page(r,src,i-1); pg.insert_text((r.x0+5,r.y0+15),str(i),fontsize=14,color=(1,0,0))
pg.get_pixmap(matrix=fitz.Matrix(1.3,1.3)).save(out)
