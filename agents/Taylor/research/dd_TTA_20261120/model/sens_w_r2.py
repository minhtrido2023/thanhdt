import itertools, sys
sys.path.insert(0,'.')
from dcf_tta_r2 import model, scen, IMPL_PAY, retro_bn, retro_nm_tran, retro_bn_tran
S=scen(); ks=['A','B',"B'",'C']
V={m:{k:model(mode=m,**S[k])[1] for k in ks} for m in ('V1','V2')}
def c(w,m='V1'): return sum(w[k]*V[m][k] for k in ks)
W={'central 0,15/0,25/0,35/0,25':dict(A=.15,B=.25,**{"B'":.35},C=.25),
   'lạc quan 0,25/0,30/0,30/0,15':dict(A=.25,B=.30,**{"B'":.30},C=.15),
   'r1-style 0,25/0,50/0/0,25':dict(A=.25,B=.5,**{"B'":0},C=.25),
   'A/B\'/C 0,25/0,5/0,25':dict(A=.25,B=0,**{"B'":.5},C=.25),
   'bi quan 0,10/0,15/0,35/0,40':dict(A=.10,B=.15,**{"B'":.35},C=.40),
   'khớp hành vi trả 0/0/0,5/0,5':dict(A=0,B=0,**{"B'":.5},C=.5),
   'đều 0,25 x4':dict(A=.25,B=.25,**{"B'":.25},C=.25)}
for n,w in W.items():
    mean_pay=sum(w[k]*IMPL_PAY[k] for k in ks)
    r=[round(c(w,m)) for m in ('V1','V2')]
    print(f"{n:34s} pay={mean_pay:.2f} V1={r[0]} sauTK={round(r[0]*.9)} BAS={round(r[0]*.9*.85)} | V2={r[1]} sauTK={round(r[1]*.9)}")
# lưới P(A) vs P(C), phần còn lại chia B:B' = 1:1.4
print('lưới V1 sauTK: hàng P(A), cột P(C)')
for a in (0,.1,.15,.2,.25,.35):
    row=[]
    for cc in (.1,.2,.25,.3,.4):
        rest=1-a-cc; w=dict(A=a,B=rest*.417,**{"B'":rest*.583},C=cc); row.append(round(c(w)*.9))
    print(a,row)
# hành vi trả EPTC (đo từ BCTC)
inv25=160.6/(1-.62); print('hoá đơn mặt trời 2025 ngụ ý',round(inv25))
inv9=295.5*1.08; print('9T/26 hoá đơn',round(inv9,1),'trả',round((inv9-161.9)/inv9,3))
full=98*2.408+85*1.826; 
print('rev full',round(full,1),'B',round((98*1.826+85*1.826)/full,3),"B'",round((98*1.826+85*1.1849)/full,3),'C',round((183*1.1849)/full,3))
