import sys, pandas as pd
D=sys.argv[1]
d=pd.read_csv(f"{D}/bq_tch_daily.csv",parse_dates=["time"]).set_index("time")
d["val"]=d.Price*d.Volume/1e9
print("ADV20 val bn",round(d.val.iloc[-20:].mean(),1),"ADV60",round(d.val.iloc[-60:].mean(),1),"vol20 mn",round(d.Volume.iloc[-20:].mean()/1e6,2),"vol60",round(d.Volume.iloc[-60:].mean()/1e6,2))
print(d.loc["2026-10-15":,["Close","Volume","VNINDEX"]].to_string())
y=d.loc["2026"]; print("2026 max/min close", y.Close.idxmax().date(), y.Close.max(), y.Close.idxmin().date(), y.Close.min())
print(d.loc["2026-04-24":"2026-05-05",["Close","Price"]].to_string())
print(d.loc["2026-10-05":"2026-10-10",["Close","Low"]].to_string())
print(d.Close.resample("QE").last().tail(16).to_string())
print("1y ret", round(d.Close.iloc[-1]/d.Close.loc[:"2025-10-31"].iloc[-1]-1,3), "VNI 1y", round(d.VNINDEX.iloc[-1]/d.VNINDEX.loc[:"2025-10-31"].iloc[-1]-1,3))
for dt in ["2026-10-29","2026-07-29","2026-04-29","2026-01-29","2025-11-03","2025-07-28"]:
    i=d.index.searchsorted(pd.Timestamp(dt)); s=d.iloc[i-1:i+3]
    print(dt, [(x.date().isoformat(),c,round(v/1e6,1), round(vi,1)) for x,c,v,vi in zip(s.index,s.Close,s.Volume,s.VNINDEX)])
