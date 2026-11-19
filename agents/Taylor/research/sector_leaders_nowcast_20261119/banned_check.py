"""Mô tả (không phải trial): T6/T9 khi bỏ HSG/NKG (BANNED) khỏi chân đầu ngành ⇒ steel chỉ còn HPG. Đọc panel_famq.csv."""
import os,sys,numpy as np,pandas as pd
O=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(O,'..','commodity_cycle_te_20261026'))
from common import px,univ,bench
P=px(); U=univ(); Bc=(1+bench(P,U)).cumprod(); idx=P.index
D=pd.read_csv(os.path.join(O,'panel_famq.csv'),parse_dates=['d0','sig'])
BAN={'HSG','NKG'}
def ret(t,a,b):
    if a is None or b is None or not t: return np.nan
    x=P.loc[a,t]; y=P.loc[b,t]; r=(y/x-1)[(x>0)&(y>0)]; return r.mean() if len(r) else np.nan
def off(d,n):
    i=idx.get_loc(d)+n; return idx[i] if i<len(idx) else None
v=[]
for r in D.itertuples():
    L=[t for t in r.L.split(',') if t not in BAN]; h3=off(r.sig,63)
    v.append((ret(L,r.sig,h3), Bc[h3]/Bc[r.sig]-1 if h3 is not None else np.nan, ret(L,r.sig,h3)-r.H3R if h3 is not None else np.nan))
D['L3x'],D['U3'],D['LR3x']=zip(*v); d=D.dropna(subset=['L3x','U3','c'])
s=np.sign(d.c)
print('T9 exBanned signed', round(float((s*(d.L3x-d.U3)).mean()),4),'n',len(d),'| down', round(float((d.L3x-d.U3)[d.c<0].mean()),4),'up',round(float((d.L3x-d.U3)[d.c>0].mean()),4))
print('T6 exBanned signed', round(float((s*d.LR3x).mean()),4))
