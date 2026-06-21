import pandas as pd, numpy as np, os
os.chdir(r"/home/trido/thanhdt/WorkingClaude")
gate=pd.read_csv("vnindex_5state_dt_4gate.csv"); gate["time"]=pd.to_datetime(gate["time"])
base=pd.read_csv("vnindex_5state_tam_quan_v3_4b_full_history.csv"); base["time"]=pd.to_datetime(base["time"])
vni=pd.read_csv("VNINDEX.csv",usecols=["time","Close"]); vni["time"]=pd.to_datetime(vni["time"])
vni=vni.sort_values("time"); vni["ret"]=vni["Close"].pct_change()

def per_year(df,col):
    df=df.sort_values("time").copy(); df["yr"]=df["time"].dt.year
    df["chg"]=(df[col]!=df[col].shift(1)).astype(int); df.iloc[0,df.columns.get_loc("chg")]=0
    return df.groupby("yr")["chg"].sum()

g=per_year(gate,"state"); b=per_year(base,"state")
vol=vni.assign(yr=vni["time"].dt.year).groupby("yr")["ret"].std()*np.sqrt(252)*100

print(f"{'year':>5}{'GATE dt_10_25_25':>18}{'RAW v3.4b base':>16}{'VNI ann.vol%':>14}")
for y in range(2000,2027):
    gg=int(g.get(y,0)); bb=int(b.get(y,0)); vv=vol.get(y,np.nan)
    print(f"{y:>5}{gg:>18}{bb:>16}{vv:>14.1f}")
print(f"\nTOTAL gate={int(g.sum())}  raw={int(b.sum())}")
# era split
def era(s,a,b): return int(s[(s.index>=a)&(s.index<=b)].sum())
print(f"\n{'era':>14}{'gate':>8}{'raw':>8}{'avg vol%':>10}")
for nm,a,b in [("2000-2007",2000,2007),("2008-2013",2008,2013),("2014-2019",2014,2019),("2020-2026",2020,2026)]:
    av=vol[(vol.index>=a)&(vol.index<=b)].mean()
    print(f"{nm:>14}{era(g,a,b):>8}{era(b_:=b,a,b) if False else era(b,a,b):>8}{av:>10.1f}")
