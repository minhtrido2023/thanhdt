import json
C=json.load(open("calc.json"))
P23={'BID':34250,'DGC':33700,'DRI':15400,'MBB':19800,'NCT':83100,'SIP':49900,'TPB':13000,'TV1':18400,'VIB':14200,'VPB':24100}
# (qty, broker costPrice, gross cash div deducted per share) từ dnse_raw 23/10 + ret_*.json tuần trước
POS={"SpaceX":{'DRI':(2500,12262.1622,1000.0),'TV1':(2300,18647.8261,1500.0),'VPB':(286,22020.9751,0.0),'MBB':(175,20656.7164,656.7164179104477),'VIB':(47,13619.7441,0.0),'TPB':(30,14173.913,434.7826086956522)},
 "ZaloPay":{'DGC':(10000,39775.0,8000.0),'DRI':(1300,12263.1579,1000.0),'TV1':(1400,18828.5715,1500.0),'VPB':(312,21225.8966,0.0),'MBB':(52,20511.0254,0.0),'VIB':(19,13607.3059,0.0)}}
fm=lambda x:f"{x:,.0f}".replace(",",".")
def pc(x): return f"{x:+.2f}%".replace(".",",").replace("+","+").replace("-","−")
res={}
for a,P in POS.items():
    rows=[];tc=tp=tmv=0;sub={}
    for t,(q,cp,g) in sorted(P.items(),key=lambda kv:-kv[1][0]*P23[kv[0]]):
        raw=cp+g; mv=q*P23[t]; pl=(P23[t]+0.95*g-raw)*q; cost=raw*q
        rows.append((t,q,raw,P23[t],mv,pl/cost*100,pl,cost)); tc+=cost;tp+=pl;tmv+=mv
    nav=C[a]['e']['nav']
    res[a]=dict(rows=rows,tc=tc,tp=tp,tmv=tmv,nav=nav)
    print(a,"mv",tmv,"nav mtm",C[a]['e']['mtm_stock'],"pl",round(tp),"cost",round(tc),round(tp/tc*100,2))
    for r in rows: print("|",r[0],"|",fm(r[1]),"|",fm(r[2]),"|",fm(r[3]),"|",fm(r[4]),"|",f"{r[4]/nav*100:.2f}".replace(".",","),"|",pc(r[5]),"|")
    if a=="ZaloPay":
        d=[r for r in rows if r[0]=="DGC"][0]; o=[r for r in rows if r[0]!="DGC"]
        print(" DGC pl",round(d[6]),d[5],"others pl",round(sum(r[6] for r in o)),"cost",round(sum(r[7] for r in o)),"pct",sum(r[6] for r in o)/sum(r[7] for r in o)*100,"mv",sum(r[4] for r in o))
    e=C[a]['e']; print(" cash",e['cash'],"egg",e['egg_assets'],"sum",tmv+e['cash']+e['egg_assets'],"nav",nav)
