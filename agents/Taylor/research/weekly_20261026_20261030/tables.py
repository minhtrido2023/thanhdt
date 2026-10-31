import json,csv,math
C=json.load(open("calc.json"))
EL="/home/trido/thanhdt/WorkingClaude/data/execution_logs/"
VN={'2026-10-16':1705.91,'2026-10-23':1774.15,'2026-10-26':1763.55,'2026-10-27':1761.87,'2026-10-28':1766.65,'2026-10-29':1755.61,'2026-10-30':1741.62}
P30={'DGC':33300,'DRI':14000,'HT1':12900,'MBB':19300,'MCH':135000,'SCL':29500,'TPB':12650,'TV1':19800,'VIB':13800,'VPB':22950}
# (qty, raw cost/share, net div/share đã nhận)
POS={"SpaceX":{'TV1':(2300,20148,1425),'DRI':(1250,13262,950),'MCH':(200,136300,0),'VPB':(1586,23607.5,0),'HT1':(2700,13468.52,0),'MBB':(175,21313,624.6),'TPB':(30,14609,413.3),'VIB':(47,13620,0)},
     "ZaloPay":{'DGC':(10000,47775,7600),'TV1':(1400,20329,1425),'DRI':(650,13263,950),'VPB':(930,(312*21225.8966+618*23766.6667)/930,0),'HT1':(1600,13468.75,0),'MBB':(52,20511,0),'MCH':(200,136300,0),'VIB':(19,13607,0)}}
FLOW={"SpaceX":-18023489,"ZaloPay":18023489}
res={}
for a in POS:
    N={r['date']:r for r in csv.DictReader(open(EL+f"nav_history_{a}.csv"))}
    ds=[d for d in sorted(N) if d>='2026-07-02']
    # chỉ số điều chỉnh dòng tiền (flow xảy ra trước đóng cửa 29/10)
    START={'SpaceX':1000000000,'ZaloPay':987865567}[a]
    ds=['start']+ds; N['start']={'nav':START}
    idx=[1.0]
    for i in range(1,len(ds)):
        n1=float(N[ds[i]]['nav'])-(FLOW[a] if ds[i]=='2026-10-29' else 0); n0=float(N[ds[i-1]]['nav'])
        idx.append(idx[-1]*n1/n0)
    rets=[idx[i]/idx[i-1]-1 for i in range(1,len(idx))]
    pk=idx[0];dd=0;ddd=None
    for d,v in zip(ds,idx):
        if v>pk: pk=v
        if v/pk-1<dd: dd=v/pk-1; ddd=d
    m=sum(rets)/len(rets); sd=(sum((x-m)**2 for x in rets)/(len(rets)-1))**.5
    # ngày trong tuần
    daily={}
    prev='2026-10-23'
    for d in ['2026-10-26','2026-10-27','2026-10-28','2026-10-29','2026-10-30']:
        n=float(N[d]['nav']); n0=float(N[prev]['nav'])
        r=(n-(FLOW[a] if d=='2026-10-29' else 0))/n0-1
        daily[d]=(n,r*100,(VN[d]/VN[prev]-1)*100); prev=d
    rows=[];tc=0;tv=0;td=0
    for t,(q,c,dv) in sorted(POS[a].items(),key=lambda kv:-kv[1][0]*P30[kv[0]]):
        mv=q*P30[t]; pnl=(mv+q*dv-q*c); rows.append((t,q,c,P30[t],mv,mv/float(N['2026-10-30']['nav'])*100,pnl/(q*c)*100,pnl,q*c)); tc+=q*c; tv+=mv; td+=pnl
    res[a]=dict(rows=rows,tot=(tv,tc,td,td/tc*100),nav=float(N['2026-10-30']['nav']),risk=dict(n=len(ds),dd=dd*100,ddd=ddd,vol=sd*100,ann=sd*math.sqrt(252)*100),daily=daily,
        cash=int(float(N['2026-10-30']['cash'])),egg=int(float(N['2026-10-30']['egg_assets'])),mtm=int(float(N['2026-10-30']['mtm_stock'])))
    r=res[a]; print(a,r['nav'],r['risk']); print(r['tot']); 
    for x in rows: print(" ",x[0],x[1],round(x[2]),x[3],x[4],round(x[5],2),round(x[6],2))
    for d,v in daily.items(): print(" ",d,v)
    print(" check",r['mtm']+r['cash']+r['egg']-r['nav'], "weights cash/egg",round(r['cash']/r['nav']*100,2),round(r['egg']/r['nav']*100,2), "idx_end",idx[-1])
json.dump(res,open("tables.json","w"),indent=1,default=str)
