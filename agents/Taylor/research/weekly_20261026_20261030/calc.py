import csv, json, math, collections
EL="/home/trido/thanhdt/WorkingClaude/data/execution_logs/"
def nav(a): return {r['date']:r for r in csv.DictReader(open(EL+f"nav_history_{a}.csv"))}
# BQ tav2_bq.ticker.Price (đo 31/10 qua bq query) — đóng cửa thật
P23={'DGC':33700,'DRI':15400,'HT1':13550,'MBB':19800,'MCH':141900,'SCL':31100,'TPB':13000,'TV1':18400,'VIB':14200,'VPB':24100}
P30={'DGC':33300,'DRI':14000,'HT1':12900,'MBB':19300,'MCH':135000,'SCL':29500,'TPB':12650,'TV1':19800,'VIB':13800,'VPB':22950}
H0={"SpaceX":{'DRI':2500,'MBB':175,'TPB':30,'TV1':2300,'VIB':47,'VPB':286},
    "ZaloPay":{'DGC':10000,'DRI':1300,'MBB':52,'TV1':1400,'VIB':19,'VPB':312}}
H1={"SpaceX":{'DRI':1250,'HT1':2700,'MBB':175,'MCH':200,'TPB':30,'TV1':2300,'VIB':47,'VPB':1586},
    "ZaloPay":{'DGC':10000,'DRI':650,'HT1':1600,'MBB':52,'MCH':200,'TV1':1400,'VIB':19,'VPB':930}}
ACC={"SpaceX":"0002023347","ZaloPay":"0001743768"}
TVDIV_TAX={"SpaceX":int(2300*1500*.05),"ZaloPay":int(1400*1500*.05)}
FLOW={"SpaceX":-18023489,"ZaloPay":18023489}
UPCOM={'SCL','MCH'}
trades=collections.defaultdict(list) # acct -> (date,side,tk,qty,val,fee,tax,src)
# 26-28: broker confirm (fee/tax thật)
for dd in ("26","27","28"):
    for r in csv.DictReader(open(EL+f"dnse_khoplenh_broker_confirm_{dd}-10-2026.csv")):
        a=[k for k,v in ACC.items() if v==r['tieu_khoan']][0]
        trades[a].append((f"2026-10-{dd}","B" if r['loai_lenh']=="MUA" else "S",r['ma'],int(r['khoi_luong']),int(r['gia_tri_khop']),int(r['phi_tra_so'])+int(r['phi_dnse']),float(r['thue']),"confirm"))
# 29-30: fill từ dnse_raw orders (bot) + sổ lệnh tay (SCL 29/10) — phí/thuế theo biểu (ước lượng, chưa có sao kê)
raw={("SpaceX","2026-10-29"):[("MCH","B",200,136300),("VPB","S",200,23450)],
     ("ZaloPay","2026-10-29"):[("MCH","B",200,136300),("VPB","S",282,23418)],
     ("SpaceX","2026-10-30"):[("SCL","S",300,29900)],("ZaloPay","2026-10-30"):[("SCL","S",200,29900)]}
manual={("SpaceX","2026-10-29"):[("SCL","S",800,29600)],("ZaloPay","2026-10-29"):[("SCL","S",500,29600)]}
for src,dct in (("raw",raw),("manual",manual)):
    for (a,d),L in dct.items():
        for tk,s,q,px in L:
            v=q*px; fee=round(v*(0.00088 if tk in UPCOM else 0.00097)); tax=v*0.001 if s=="S" else 0
            trades[a].append((d,s,tk,q,v,fee,tax,src+"-est"))
out={}
for a in ACC:
    N=nav(a); n0=N['2026-10-23']; n1=N['2026-10-30']
    g=lambda n:{k:int(float(n[k])) for k in('nav','mtm_stock','cash','egg_assets')}
    d,e=g(n0),g(n1)
    qty=collections.Counter(H0[a])
    buy=collections.defaultdict(lambda:[0,0]); sell=collections.defaultdict(lambda:[0,0])
    fee=0;tax=0;fee_est=0;tax_est=0
    for dt,s,tk,q,v,f,t,src in trades[a]:
        x=buy if s=="B" else sell; x[tk][0]+=q; x[tk][1]+=v
        qty[tk]+= q if s=="B" else -q
        fee+=f; tax+=t
        if src.endswith("est"): fee_est+=f; tax_est+=t
    qty={k:v for k,v in qty.items() if v}
    assert qty==H1[a],(a,qty,H1[a])
    attr={}
    for t in set(H0[a])|set(buy)|set(sell)|set(H1[a]):
        attr[t]=H1[a].get(t,0)*P30[t]-H0[a].get(t,0)*P23.get(t,0)-buy[t][1]+sell[t][1]
    # kiểm mtm
    mtm1=sum(q*P30[t] for t,q in H1[a].items()); mtm0=sum(q*P23[t] for t,q in H0[a].items())
    price=sum(attr.values())
    dn=e['nav']-d['nav']; dnadj=dn-FLOW[a]
    other=dnadj-price+fee+tax+TVDIV_TAX[a]   # = lãi egg + lãi không kỳ hạn (số dư)
    out[a]=dict(d=d,e=e,dn=dn,flow=FLOW[a],dnadj=dnadj,attr=attr,price=round(price),fee=fee,tax=tax,fee_est=fee_est,tax_est=tax_est,
        divtax=TVDIV_TAX[a],interest=round(other),mtm_calc=(mtm0,mtm1),mtm_csv=(d['mtm_stock'],e['mtm_stock']),
        buy={k:v for k,v in buy.items()},sell={k:v for k,v in sell.items()})
    dates=[x for x in sorted(N) if x>='2026-07-02']
    for cut in ('2026-10-23','2026-10-30'):
        s=[float(N[x]['nav']) for x in dates if x<=cut]
        out[a][f'n_{cut}']=len(s)
    out[a]['daily']={x:float(N[x]['nav']) for x in dates if '2026-10-23'<=x<='2026-10-30'}
for a in ACC: out[a]['trades']=trades[a]
json.dump(out,open("calc.json","w"),indent=1,ensure_ascii=False)
for a,o in out.items():
    print(a,{k:o[k] for k in('dn','flow','dnadj','price','fee','tax','fee_est','tax_est','divtax','interest','mtm_calc','mtm_csv')})
    print(" attr",{k:round(v) for k,v in o['attr'].items()})
    print(" buy",o['buy'],"sell",o['sell'])
