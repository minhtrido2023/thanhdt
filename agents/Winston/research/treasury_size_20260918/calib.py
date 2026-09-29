import pandas as pd, os
D=os.path.dirname(os.path.abspath(__file__))
ev=pd.read_csv(f"{D}/events.csv",parse_dates=["public_date"]); fin=pd.read_csv(f"{D}/fin.csv",parse_dates=["time"])
ca=pd.read_csv(f"{D}/ca.csv")
fin=fin.dropna(subset=["OShares"]); fin=fin[fin.OShares>0]
base=fin.groupby("ticker").OShares.median()
s=ev[ev.shares_delta.notna()].copy()
s["pct"]=s.shares_delta.abs()/s.ticker.map(base)
s=s.dropna(subset=["pct"])
print(f"Co THAT cua {len(s)} su kien, tinh theo % OShares trung vi cua ma:")
for q in [.5,.75,.9,.95,.99,1.0]: print(f"  p{int(q*100):<3} {s.pct.quantile(q):7.2%}")
print(f"  so ca > 10%: {(s.pct>0.10).sum()} | >15%: {(s.pct>0.15).sum()} | >25%: {(s.pct>0.25).sum()}")
print("\nDo phu corporate_action: so ma co >=1 dong ISS/DIV/AIS/MA")
cac=ca[ca.event_code.isin(["ISS","DIV","AIS","MA"])]
alltk=set(ev.ticker.unique()); cov=set(cac.ticker.unique())
print(f"  {len(alltk&cov)}/{len(alltk)} ma co du lieu CA | {len(alltk-cov)} ma KHONG co dong CA nao")
