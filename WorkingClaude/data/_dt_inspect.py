import pandas as pd, numpy as np, glob, os
os.chdir(r"/home/trido/thanhdt/WorkingClaude")
def ntrans(s): a=np.asarray(s); return int((a[1:]!=a[:-1]).sum())
files=["data/vnindex_5state_tam_quan_v3_4b_full_history.csv"]+sorted(glob.glob("vnindex_5state_dt_*.csv"))
for f in files:
    d=pd.read_csv(f); d["time"]=pd.to_datetime(d["time"])
    col="state" if "state" in d.columns else d.columns[1]
    d=d[d["time"]>="2014-01-01"].sort_values("time")
    print(f"{f:48s} cols={list(d.columns)[:4]} trans2014={ntrans(d[col].values):4d} rows={len(d)} max={d['time'].max().date()}")
