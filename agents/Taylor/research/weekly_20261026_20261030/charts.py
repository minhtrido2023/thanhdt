import json,subprocess,os
T=json.load(open("tables.json")); C=json.load(open("calc.json"))
dates=["2026-10-23","2026-10-26","2026-10-27","2026-10-28","2026-10-29","2026-10-30"]
vn=[1774.15,1763.55,1761.87,1766.65,1755.61,1741.62]
FLOW={"SpaceX":-18023489,"ZaloPay":18023489}
R="/home/trido/thanhdt/WorkingClaude/mike/"
for a in ("SpaceX","ZaloPay"):
    nav=[C[a]["daily"][d] for d in dates]
    adj=[n-(FLOW[a] if d>="2026-10-29" else 0) for n,d in zip(nav,dates)]
    N=T[a]["nav"]; rows=T[a]["rows"]
    stocks=[(r[0],round(r[5],2)) for r in rows]
    top=stocks[:5]; other=round(sum(x[1] for x in stocks[5:]),2)
    cashpct=round(100-sum(x[1] for x in stocks),2)
    alloc=[list(x) for x in top]
    if other>0: alloc.append(["Cổ phiếu khác",other])
    alloc.append(["Tiền mặt & tiền gửi",cashpct]); alloc.sort(key=lambda x:-x[1])
    json.dump(alloc,open(f"alloc_{a}.json","w"),ensure_ascii=False)
    for label,series,suffix in (("weekly_2026-10-26_to_2026-10-30",nav,"26-30/10/2026"),("weekly_2026-10-26_to_2026-10-30_adj",adj,"26-30/10/2026 (đã loại dòng tiền)")):
        subprocess.run(["python3",R+"bin/report_charts.py","--account",a,"--label",label,"--title-suffix",suffix,"--dates",json.dumps(dates),"--nav",json.dumps(series),"--vnindex",json.dumps(vn),"--allocation",json.dumps(alloc,ensure_ascii=False)],check=True)
