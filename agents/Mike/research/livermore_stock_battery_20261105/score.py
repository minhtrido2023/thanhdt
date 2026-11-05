import json,csv,math
from math import comb
t={x["label"]:x for x in json.load(open("SEALED_truth.json"))}
r=list(csv.DictReader(open("livermore_results.csv")))
n=len(r); hit=0; br=0
b1=b2=b3=0; b2br=0
yrs={}
for x in r:
    T=t[x["label"]]; up=T["up"]; p=float(x["H20_P_UP"]); d=1 if x["H20_DIR"]=="UP" else 0
    h=int(d==up); hit+=h; br+=(p-up)**2
    b1+=int(up==1); b2+=int(T["mom20"]==up); b3+=int(T["mom60"]==up)
    y=T["asof"][:4]; a=yrs.setdefault(y,[0,0]); a[0]+=h; a[1]+=1
base=sum(T["up"] for T in t.values())/len(t)
def pbin(k,n,p): return sum(comb(n,i)*p**i*(1-p)**(n-i) for i in range(k,n+1))
print(f"N={n} hit={hit} ({hit/n:.3f}) Brier={br/n:.4f}  [coin Brier 0.25, always-UP Brier={sum((1-T['up'])**2 for T in t.values())/n:.4f}]")
print(f"B0 coin 50 | B1 always-UP {b1} | B2 mom20 {b2} | B3 mom60 {b3}  | base rate up={base:.2f}")
print(f"P(X>={hit}|p=0.5)={pbin(hit,n,0.5):.3f}  P(X>={hit}|p=base)={pbin(hit,n,base):.3f}")
up_calls=[x for x in r if x["H20_DIR"]=="UP"]; dn=[x for x in r if x["H20_DIR"]=="DOWN"]
print("UP calls",len(up_calls),"hit",sum(t[x['label']]['up']==1 for x in up_calls),"| DOWN calls",len(dn),"hit",sum(t[x['label']]['up']==0 for x in dn))
print("by year:",{k:f"{v[0]}/{v[1]}" for k,v in sorted(yrs.items())})
crit = (br/n<0.25) and hit>max(b1,b2,b3) and pbin(hit,n,base)<0.10
print("PREREG criterion (Brier<0.25, hit>max(B1,B2,B3), p<0.10):", "SỐNG" if crit else "KHÔNG ĐẠT")
