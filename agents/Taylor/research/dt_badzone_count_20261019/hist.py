import sys; sys.path.insert(0,'/home/trido/thanhdt/WorkingClaude')
import pandas as pd, numpy as np
from macro_state_live import _dt_4gate
N={1:'CRISIS',2:'BEAR',3:'NEUTRAL',4:'BULL',5:'EXBULL'}; W={1:0,2:.2,3:.7,4:1.,5:1.3}
b=pd.read_csv('base_v34b.csv',parse_dates=['time']).merge(pd.read_csv('vnindex.csv',parse_dates=['time']),on='time')
raw=b.state.astype(int).values; px=b.Close.values; T=b.time; n=len(raw)
dt4=_dt_4gate(raw)
def gate_group(states,need_bad=10):
    """C: like DT_10_25_25, plus: while committed in {N,BULL,EXB} and base in {BEAR,CRISIS}, count group streak; >=need_bad -> commit BEAR."""
    out=states.copy(); c=states[0]; ps,pr=states[0],1; g=0
    for t in range(1,len(states)):
        s=states[t]
        if s==ps: pr+=1
        else: ps,pr=s,1
        g = g+1 if (s in (1,2) and c>=3) else 0
        if ps!=c:
            need=(25 if ps==1 else 25 if ps==5 else 10 if c==1 else 10 if c==5 else 10)
            if pr>=need: c=ps
            elif c>=3 and g>=need_bad: c=2
        out[t]=c
    return out
# badzone episodes (raw in bad, committed not bad), contiguous
bad=np.isin(raw,(1,2))&~np.isin(dt4,(1,2))
eps=[];i=0
while i<n:
    if bad[i]:
        j=i
        while j+1<n and bad[j+1]: j+=1
        z=raw[i:j+1]; fl=int((np.diff(z)!=0).sum())
        eps.append(dict(start=T[i].date(),end=T[j].date(),n=j-i+1,flips=fl,nB=int((z==2).sum()),nC=int((z==1).sum()),
          ret_in=px[j]/px[i-1]-1,ret_at15=(px[i+14]/px[i-1]-1) if j-i+1>=15 else np.nan,
          fwd20_from15=(px[min(i+14+20,n-1)]/px[i+14]-1) if j-i+1>=15 and i+34<n else np.nan,
          fwd60_from15=(px[min(i+14+60,n-1)]/px[i+14]-1) if j-i+1>=15 and i+74<n else np.nan,
          next_dt4=N[dt4[min(j+1,n-1)]], minfwd60=(px[i+14:min(i+75,n)].min()/px[i+14]-1) if j-i+1>=15 else np.nan))
        i=j+1
    else: i+=1
E=pd.DataFrame(eps); E.to_csv('badzone_episodes.csv',index=False)
print('all badzone eps',len(E),'| n>=10:',(E.n>=10).sum(),'| n>=15:',(E.n>=15).sum(),'| n>=15 & flips>=1:',((E.n>=15)&(E.flips>=1)).sum())
pd.set_option('display.width',250)
print(E[E.n>=10].round(3).to_string(index=False))
# variants -> NAV proxy on VNINDEX
gC=gate_group(raw)
def nav(states=None,w=None,start='2014-06-01'):
    if w is None: w=np.array([W[s] for s in states])
    r=np.r_[0,px[1:]/px[:-1]-1]; wl=np.r_[0,w[:-1]]  # weight decided EOD t applies t+1 (T+1)
    tc=np.r_[0,np.abs(np.diff(wl))]*0.001
    d=r*wl-tc; d=d[T>=start]; tt=T[T>=start]
    eq=np.cumprod(1+d); yrs=(tt.iloc[-1]-tt.iloc[0]).days/365.25
    dd=(eq/np.maximum.accumulate(eq)-1).min()
    return eq[-1]**(1/yrs)-1, dd
wA=np.array([W[s] for s in dt4])
# B: partial cap when badzone streak >= Nb (committed still >= NEUTRAL)
def overlay(Nb,cap):
    w=wA.copy(); g=0
    for t in range(n):
        g=g+1 if bad[t] else 0
        if g>=Nb: w[t]=min(w[t],cap)
    return w
res=[]
for name,w in [('A_DT4',wA),('C_group10->BEAR',np.array([W[s] for s in gC])),
               ('B_N10_cap50',overlay(10,.5)),('B_N15_cap50',overlay(15,.5)),('B_N15_cap20',overlay(15,.2)),('B_N10_cap20',overlay(10,.2))]:
    row=[name]
    for a,z in [('2014-06-01',None),('2014-06-01','2019-12-31'),('2020-01-01',None)]:
        ww=w; 
        if z: 
            k=T<=z; 
            cg,dd=nav(w=w[k.values] if False else None) if False else (None,None)
        row+= list(nav(w=w,start=a)) if z is None else []
    res.append(row)
# IS split separately
def nav_rng(w,a,z):
    r=np.r_[0,px[1:]/px[:-1]-1]; wl=np.r_[0,w[:-1]]; tc=np.r_[0,np.abs(np.diff(wl))]*0.001; d=(r*wl-tc)
    k=((T>=a)&(T<=z)).values; d=d[k]; tt=T[k]; eq=np.cumprod(1+d); yrs=(tt.iloc[-1]-tt.iloc[0]).days/365.25
    return round((eq[-1]**(1/yrs)-1)*100,2), round(((eq/np.maximum.accumulate(eq))-1).min()*100,1)
out=[]
for name,w in [('A_DT4',wA),('C_group10->BEAR',np.array([W[s] for s in gC])),
               ('B_N10_cap50',overlay(10,.5)),('B_N15_cap50',overlay(15,.5)),('B_N10_cap20',overlay(10,.2)),('B_N15_cap20',overlay(15,.2))]:
    out.append([name,*nav_rng(w,'2014-06-01','2026-12-31'),*nav_rng(w,'2014-06-01','2019-12-31'),*nav_rng(w,'2020-01-01','2026-12-31'),int((w!=wA).sum())])
R=pd.DataFrame(out,columns=['variant','CAGR_full','DD_full','CAGR_IS','DD_IS','CAGR_OOS','DD_OOS','days_diff'])
print(R.to_string(index=False)); R.to_csv('variants_vnindex_proxy.csv',index=False)
print('C commits BEAR now?', N[gC[-1]], '| C first BEAR commit in current zone:', [T[t].date() for t in range(n-20,n) if gC[t]==2 and gC[t-1]!=2])
# C: dates where C differs from A, grouped
d=np.where(gC!=dt4)[0]; 
if len(d):
    grp=np.split(d,np.where(np.diff(d)>1)[0]+1)
    for g in grp: print('C!=A',T[g[0]].date(),'->',T[g[-1]].date(),len(g),'d','C=',N[gC[g[0]]],'A=',N[dt4[g[0]]],'VNI over span %+.1f%%'%((px[g[-1]]/px[g[0]-1]-1)*100))
