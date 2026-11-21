import csv,sys
sys.path.insert(0,'/home/trido/thanhdt/WorkingClaude')
import pandas as pd
from deposit_rate_vn import deposit_events_df
ev=deposit_events_df()
def dep(d):
    return float(ev[ev.time<=pd.Timestamp(d)].iloc[-1].deposit_rate)
# diem spread: chi lay quan sat 12M, confidence>=MED hoac 2-nguon, kenh 'cao nhat Big-4'
pts=[("2026-01-21","VCB 12M online",6.0,"HIGH"),("2026-04-02","VCB 12M online",7.9,"HIGH"),
     ("2026-06-26","VCB 12M online (1 nguon)",7.4,"LOW"),("2026-10-05","BIDV/CTG 12M",7.4,"MED"),
     ("2026-10-12","Big-4 max 12M",7.4,"MED"),("2026-11-02","Big-4 max 12M",7.4,"MED")]
rows=[]
for d,l,c,q in pts:
    b=dep(d); rows.append((d,l,c,b,round(c-b,2),q))
pd.DataFrame(rows,columns="date label cctg12m dep12m_online spread_pp conf".split()).to_csv("spread_big4.csv",index=False)
print(pd.DataFrame(rows,columns="date label cctg12m dep12m_online spread_pp conf".split()))
s=[r[4] for r in rows]; print("N",len(s),"median",pd.Series(s).median(),"min",min(s),"max",max(s))
# Tier-2 vs Big-4 CCTG 7.4 va vs deposit 6.8 (cung ngay, ky han lech 6M vs 12M)
t2=[("2026-06-26","MB","6M",7.1),("2026-10-13","MB","6-9M",7.1),("2026-10-13","ACB","3M",7.2),("2026-10-13","VPB","(100tr)",9.2),
    ("2026-11-02","MB","6M",7.1),("2026-11-02","TCB","6M",7.6),("2026-11-02","VPB","184-389d",9.0)]
r2=[(d,b,t,c,dep(d),round(c-dep(d),2),(round(c-7.4,2) if d>="2026-10-05" else None)) for d,b,t,c in t2]
pd.DataFrame(r2,columns="date bank tenor cctg dep12m spread_vs_dep spread_vs_big4cctg".split()).to_csv("spread_tier2.csv",index=False)
print(pd.DataFrame(r2,columns="date bank tenor cctg dep12m spread_vs_dep spread_vs_big4cctg".split()))
