import sys; sys.path.insert(0,'/home/trido/thanhdt/WorkingClaude'); sys.path.insert(0,'/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor')
import pandas as pd, numpy as np
from macro_state_live import _dt_4gate
from dt_gate_hazard_research import extract_episodes
N={1:'CRISIS',2:'BEAR',3:'NEUTRAL',4:'BULL',5:'EXBULL'}
b=pd.read_csv('base_v34b.csv',parse_dates=['time']); p=pd.read_csv('vnindex.csv',parse_dates=['time']); l=pd.read_csv('dt5g_live.csv',parse_dates=['time'])
raw=b.state.astype(int).values; com=_dt_4gate(raw)
m=b.assign(dt4=com).merge(l,on='time',how='left').merge(p,on='time',how='left')
print('selfcheck dt4 vs dt5g_live.state_raw diffs:',int((m.dt4!=m.state_raw).sum()),'| vs state:',int((m.dt4!=m.state_y).sum()),'/',len(m))
# trace from 2026-09-22
ps,pr=raw[0],1; c=raw[0]; rows=[]
for t in range(1,len(raw)):
    s=raw[t]
    if s==ps: pr+=1
    else: ps,pr=s,1
    need=None
    if ps!=c:
        need=(25 if ps==1 else 25 if ps==5 else 10 if c==1 else 10 if c==5 else 10)
        if pr>=need: c=ps
    rows.append((b.time[t].date(),N[s],N[c],pr if ps!=c or need else 0,need))
tr=pd.DataFrame(rows,columns=['time','base','committed','streak','need'])
tr['vni']=m.Close.values[1:]
print(tr[tr.time>=pd.Timestamp('2026-09-22').date()].to_string(index=False))
ep=extract_episodes(b.time.values,raw); print(ep.tail(4).to_string())
