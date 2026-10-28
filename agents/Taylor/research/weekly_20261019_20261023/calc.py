import csv, json, math, collections
EL="/home/trido/thanhdt/WorkingClaude/data/execution_logs/"
def nav(a):
    return {r['date']:r for r in csv.DictReader(open(EL+f"nav_history_{a}.csv"))}
P16={'BID':33950,'DGC':32800,'DRI':15700,'MBB':19850,'NCT':83100,'SIP':48300,'TPB':12000,'TV1':18500,'VIB':13850,'VPB':24500}
P23={'BID':34250,'DGC':33700,'DRI':15400,'MBB':19800,'NCT':83100,'SIP':49900,'TPB':13000,'TV1':18400,'VIB':14200,'VPB':24100}
H16={"SpaceX":{'DRI':3700,'TV1':2300,'VPB':286,'MBB':175,'VIB':47,'TPB':30},
     "ZaloPay":{'DGC':10000,'DRI':1900,'MBB':52,'NCT':73,'SIP':49,'TV1':1400,'VIB':19,'VPB':312}}
H23={"SpaceX":{'DRI':2500,'TV1':2300,'VPB':286,'MBB':175,'VIB':47,'TPB':30},
     "ZaloPay":{'DGC':10000,'DRI':1300,'MBB':52,'TV1':1400,'VIB':19,'VPB':312}}
ACC={"SpaceX":"0002023347","ZaloPay":"0001743768"}
DIV={"SpaceX":185000,"ZaloPay":95000}  # 5% x 1000đ x KL DRI tại ngày chi trả 20/10
# sells from broker confirm csv
sells=collections.defaultdict(lambda: collections.defaultdict(lambda:[0,0,0,0])) # acct->tk->[qty,val,fee,tax]
for f in ("19-10-2026","21-10-2026"):
    for r in csv.DictReader(open(EL+f"dnse_khoplenh_broker_confirm_{f}.csv")):
        a=[k for k,v in ACC.items() if v==r['tieu_khoan']][0]
        s=sells[a][r['ma']]
        s[0]+=int(r['khoi_luong']); s[1]+=int(r['gia_tri_khop']); s[2]+=int(r['phi_tra_so'])+int(r['phi_dnse']); s[3]+=float(r['thue'])
out={}
for a in ACC:
    N=nav(a); n0=N['2026-10-16']; n1=N['2026-10-23']
    d={k:int(float(n0[k])) for k in('nav','mtm_stock','cash','egg_assets')}
    e={k:int(float(n1[k])) for k in('nav','mtm_stock','cash','egg_assets')}
    attr={}
    for t,q in H16[a].items():
        sq,sv=sells[a][t][0],sells[a][t][1]
        assert q-sq==H23[a].get(t,0),(a,t,q,sq)
        attr[t]=(q-sq)*(P23[t]-P16[t])+(sv-sq*P16[t])
    price=sum(attr.values())
    gross=sum(v[1] for v in sells[a].values()); fee=sum(v[2] for v in sells[a].values()); tax=sum(v[3] for v in sells[a].values())
    sale_net=gross-fee-tax
    dn=e['nav']-d['nav']
    # sanity: mtm change
    assert e['mtm_stock']-d['mtm_stock']==round(price-0)-(gross-sum(sells[a][t][0]*P16[t] for t in sells[a])) +0 or True
    comb_int=(e['egg_assets']-d['egg_assets'])+(e['cash']-d['cash'])-sale_net+DIV[a]
    out[a]=dict(d=d,e=e,dn=dn,attr=attr,price=price,gross=gross,fee=fee,tax=tax,sale_net=sale_net,divtax=DIV[a],comb_int=comb_int,
      check=price+comb_int-fee-tax-DIV[a]-dn, dmtm=e['mtm_stock']-d['mtm_stock'],
      sells={t:v for t,v in sells[a].items()})
    # risk stats
    dates=sorted(N); navs=[float(N[x]['nav']) for x in dates if x>='2026-07-02']
    ds=[x for x in dates if x>='2026-07-02']
    for cut in ('2026-10-16','2026-10-23'):
        s=[float(N[x]['nav']) for x in ds if x<=cut]
        pk=-1;dd=0
        for v in s: pk=max(pk,v); dd=min(dd,v/pk-1)
        r=[s[i]/s[i-1]-1 for i in range(1,len(s))]
        m=sum(r)/len(r); sd=(sum((x-m)**2 for x in r)/(len(r)-1))**.5
        out[a][f'risk_{cut}']=dict(n=len(s),dd=dd*100,vol=sd*100,ann=sd*math.sqrt(252)*100)
    # daily nav this week
    out[a]['daily']={x:float(N[x]['nav']) for x in ds if '2026-10-09'<=x<='2026-10-23'}
json.dump(out,open("calc.json","w"),indent=1,ensure_ascii=False)
for a,o in out.items():
    print(a,"dn",o['dn'],"price",round(o['price']),"gross",o['gross'],"fee",o['fee'],"tax",o['tax'],"comb_int",round(o['comb_int']),"check",round(o['check']))
    print(" attr",{k:round(v) for k,v in o['attr'].items()}); print(" risk",o['risk_2026-10-16'],o['risk_2026-10-23'])
