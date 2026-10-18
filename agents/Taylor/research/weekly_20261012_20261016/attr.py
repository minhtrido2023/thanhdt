import json,collections,sys
RAW="/home/trido/thanhdt/WorkingClaude/data/execution_logs/dnse_raw_2026-10-16.jsonl"
P09={'BID':33900,'DGC':33800,'DRI':16900,'MBB':19050,'MSB':14600,'NCT':83700,'PVT':25200,'SAB':42900,'SIP':49400,'TPB':11450,'TV1':19300,'VIB':13650,'VNM':57700,'VPB':23800,'VPI':55500}
P16={'BID':33950,'DGC':32800,'DRI':15700,'MBB':19850,'MSB':14800,'NCT':83100,'PVT':23650,'SAB':43000,'SIP':48300,'TPB':12000,'TV1':18500,'VIB':13850,'VNM':57800,'VPB':24500,'VPI':48100}
H09={"SpaceX":{'DRI':3700,'SIP':1700,'VNM':900,'SAB':1100,'VPI':800,'TV1':2300,'NCT':500,'PVT':3500,'VPB':286,'MBB':175,'MSB':100,'VIB':47,'TPB':30},
"ZaloPay":{'DGC':10000,'PVT':2071,'SIP':749,'VNM':601,'DRI':1900,'SAB':744,'NCT':373,'TV1':1400,'VPI':400,'VPB':312,'MBB':52,'MSB':40,'VIB':19}}
NAV={"SpaceX":(986698574,969426082,9109074,355941844,500533900,501352538),"ZaloPay":(939394841,920292705,4909765,199778103,318890326,319412252)}
for a,no in (("SpaceX","0002023347"),("ZaloPay","0001743768")):
    last=None
    for l in open(RAW):
        try:r=json.loads(l)
        except: continue
        if r.get("kind")=="orders" and str(r.get("account_no"))==no: last=r
    sold=collections.defaultdict(lambda:[0,0.0])
    for o in last["payload"]["orders"]:
        if o["orderStatus"]=="Filled" and o["side"]=="NS":
            sold[o["symbol"]][0]+=o["fillQuantity"]; sold[o["symbol"]][1]+=o["fillQuantity"]*o["averagePrice"]
    H=H09[a]; attr={}; gross=0
    for t,q in H.items():
        sq,sv=sold.get(t,[0,0.0]); gross+=sv
        attr[t]=(q-sq)*(P16[t]-P09[t]) + (sv - sq*P09[t])
    price_tot=sum(attr.values())
    n0,n1,c0,c1,e0,e1=NAV[a]
    dn=n1-n0
    fee=gross*0.00097; tax=gross*0.001
    egg=e1-e0
    print(a,"sold",{t:(v[0],round(v[1]/v[0],1)) for t,v in sold.items()},"gross",round(gross))
    print(" attr",{t:round(v/1e6,2) for t,v in sorted(attr.items(),key=lambda x:x[1])})
    print(" price_tot",round(price_tot),"dNAV",dn,"nonprice",round(dn-price_tot),"egg",egg)
    print(" est fee+tax",round(fee+tax),"cash identity: dcash",c1-c0,"gross",round(gross),"resid",round(c1-c0-gross),"(= -fee-tax-divtax+interest)")
