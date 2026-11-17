import json, sys, datetime as dt, pandas as pd, numpy as np
from zoneinfo import ZoneInfo
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from dnse_api import DNSEClient
c = DNSEClient.from_credentials_file(); ICT=ZoneInfo("Asia/Ho_Chi_Minh")
vci = pd.read_csv("vn30f1m_tail_20260920_20261116.csv")
vci["time"]=pd.to_datetime(vci["time"]); vci["date"]=vci.time.dt.date.astype(str); vci["hm"]=vci.time.dt.strftime("%H:%M")
days = sorted(vci.date.unique())[-30:]
rows=[]
def summ(g):
    g=g.sort_values("time"); op=g[g.hm<="09:30"]; seg=g[(g.hm>"09:30")&(g.hm<="14:30")]
    if len(op)<10 or len(seg)==0: return None
    c0=float(g.close.iloc[0]); e=float(op.close.iloc[-1]); x=float(seg.close.iloc[-1])
    return dict(hm0=g.hm.iloc[0], c0=c0, entry=e, exit=x, or_ret=e/c0-1, sig=int(np.sign(e/c0-1)), n=len(g))
allb=[]
for d in days:
    y,m,dd=map(int,d.split("-"))
    f=int(dt.datetime(y,m,dd,8,59,tzinfo=ICT).timestamp()); t=int(dt.datetime(y,m,dd,14,46,tzinfo=ICT).timestamp())
    r=c.ohlc("VN30F1M", resolution="1", bar_type="derivative", **{"from":f,"to":t})
    if not r.get("t"): rows.append(dict(date=d, dnse=None)); continue
    g=pd.DataFrame({"time":[dt.datetime.fromtimestamp(x,ICT).replace(tzinfo=None) for x in r["t"]],"open":r["o"],"high":r["h"],"low":r["l"],"close":r["c"],"volume":r["v"]})
    g["hm"]=g.time.dt.strftime("%H:%M"); g["date"]=d; allb.append(g)
    a=summ(g); b=summ(vci[vci.date==d])
    rows.append(dict(date=d, dnse=a, vci=b))
pd.concat(allb).to_csv("dnse_vn30f1m_1m_30d.csv", index=False)
agree=0; n=0; de=[]; dor=[]
for r in rows:
    a,b=r.get("dnse"),r.get("vci")
    if not a or not b: print(r["date"], "missing", bool(a), bool(b)); continue
    n+=1; agree+= a["sig"]==b["sig"]; de.append(a["entry"]-b["entry"]); dor.append((a["or_ret"]-b["or_ret"])*1e4)
    print(r["date"], f"DNSE hm0={a['hm0']} c0={a['c0']} e={a['entry']} x={a['exit']} sig={a['sig']} n={a['n']} | VCI hm0={b['hm0']} c0={b['c0']} e={b['entry']} x={b['exit']} sig={b['sig']} n={b['n']}")
print(f"N={n} sig agree {agree}/{n}; entry diff max|.|={np.max(np.abs(de)):.2f}d; OR diff bps max|.|={np.max(np.abs(dor)):.2f}, mean={np.mean(dor):.2f}")
