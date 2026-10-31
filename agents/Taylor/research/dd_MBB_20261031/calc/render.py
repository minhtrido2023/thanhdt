import sys; sys.path.insert(0,'/tmp/pdflib')
import pymupdf as fitz
# usage: render.py pdf outprefix zoom pages(comma, 1-based) | sheet pdf outprefix
mode=sys.argv[1]
if mode=='sheet':
    d=fitz.open(sys.argv[2]); pre=sys.argv[3]; per=int(sys.argv[4]) if len(sys.argv)>4 else 6
    for s in range(0,d.page_count,per):
        pages=list(range(s,min(s+per,d.page_count)))
        W,H=600,850; cols=3; rows=(len(pages)+cols-1)//cols
        out=fitz.open(); pg=out.new_page(width=W*cols,height=H*rows)
        for i,p in enumerate(pages):
            r=fitz.Rect((i%cols)*W,(i//cols)*H,(i%cols+1)*W,(i//cols+1)*H)
            pg.show_pdf_page(r,d,p)
            pg.insert_text((r.x0+10,r.y0+20),f"P{p+1}",fontsize=18,color=(1,0,0))
        out[0].get_pixmap(matrix=fitz.Matrix(0.75,0.75)).save(f"{pre}_s{s+1:02d}.png")
else:
    d=fitz.open(sys.argv[2]); pre=sys.argv[3]; z=float(sys.argv[4])
    rot=int(sys.argv[6]) if len(sys.argv)>6 else 0
    for p in [int(x) for x in sys.argv[5].split(',')]:
        d[p-1].get_pixmap(matrix=fitz.Matrix(z,z).prerotate(rot)).save(f"{pre}_p{p:02d}.png")
