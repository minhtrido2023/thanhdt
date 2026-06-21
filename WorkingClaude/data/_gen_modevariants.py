import numpy as np, pandas as pd, os, sys
sys.path.insert(0, r"/home/trido/thanhdt/WorkingClaude")
os.chdir(r"/home/trido/thanhdt/WorkingClaude")
from exp_velocity_minstay import rolling_mode, min_stay_filter, count_transitions
m=pd.read_csv("data/vnindex_5state_intermediate.csv"); m["time"]=pd.to_datetime(m["time"])
dvg=m["state_dvg"].values.astype(int)
variants={
  "mode15_ms7": min_stay_filter(rolling_mode(dvg,15),7),   # canonical
  "mode7_ms7":  min_stay_filter(rolling_mode(dvg,7),7),
  "mode5_ms7":  min_stay_filter(rolling_mode(dvg,5),7),
  "nomode_ms7": min_stay_filter(dvg,7),
}
for name,st in variants.items():
    out=pd.DataFrame({"time":m["time"].dt.strftime("%Y-%m-%d"),"state":st})
    p=f"data/state_modevar_{name}.csv"; out.to_csv(p,index=False)
    print(f"{name:14s} trans={count_transitions(st):4d}  -> {p}")
