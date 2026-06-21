import pandas as pd, numpy as np, os
os.chdir(r"/home/trido/thanhdt/WorkingClaude")
gate=pd.read_csv("vnindex_5state_dt_4gate.csv"); gate["time"]=pd.to_datetime(gate["time"])
base=pd.read_csv("vnindex_5state_tam_quan_v3_4b_full_history.csv"); base["time"]=pd.to_datetime(base["time"])
vni=pd.read_csv("VNINDEX.csv",usecols=["time","Close"]); vni["time"]=pd.to_datetime(vni["time"]); vni=vni.sort_values("time"); vni["ret"]=vni["Close"].pct_change()
def py(df,col):
    df=df.sort_values("time").copy(); df["yr"]=df["time"].dt.year; df["chg"]=(df[col]!=df[col].shift(1)).astype(int); df.iloc[0,df.columns.get_loc("chg")]=0
    return df.groupby("yr")["chg"].sum()
g=py(gate,"state"); b=py(base,"state"); vol=vni.assign(yr=vni["time"].dt.year).groupby("yr")["ret"].std()*np.sqrt(252)*100
def s(ser,a,bb): return ser[(ser.index>=a)&(ser.index<=bb)]
print(f"{'era':>12}{'yrs':>5}{'gate/yr':>9}{'raw/yr':>9}{'avgVol%':>9}")
for nm,a,bb in [("2001-2007",2001,2007),("2008-2013",2008,2013),("2014-2019",2014,2019),("2020-2026",2020,2026)]:
    ny=bb-a+1
    print(f"{nm:>12}{ny:>5}{s(g,a,bb).sum()/ny:>9.1f}{s(b,a,bb).sum()/ny:>9.1f}{s(vol,a,bb).mean():>9.1f}")
