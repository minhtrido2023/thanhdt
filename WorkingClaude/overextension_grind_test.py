#!/usr/bin/env python3
"""overextension_grind_test.py — does a LONG/STRETCHED prior rally precede the GRIND
declines (2018, 2022) vs the V-bottoms (2020, 2025)? Tiny-n exploratory, NOT a rule."""
import warnings; warnings.filterwarnings("ignore")
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
W=r"/home/trido/thanhdt/WorkingClaude"
V=pd.read_csv(os.path.join(W,"data","_vnindex_daily.csv"),parse_dates=["time"]).sort_values("time").reset_index(drop=True)
V["ma200"]=V["VNINDEX"].rolling(200).mean()
M=pd.read_csv(os.path.join(W,"data","washout_master_table.csv"),parse_dates=["date"])
st=pd.read_csv(os.path.join(W,"data","daily_comovement_dt5g.csv"),parse_dates=["time"]).set_index("time")["state"]
vi=V.set_index("time")
def idx(d):
    return vi.index.searchsorted(pd.Timestamp(d))
rows=[]
for _,r in M.iterrows():
    d=r["date"]; i=idx(d)
    win=vi.iloc[max(0,i-504):i+1]               # look back 2y for the pre-decline peak
    pk=win["VNINDEX"].idxmax(); pkpos=vi.index.get_loc(pk)
    peak=vi["VNINDEX"].loc[pk]; ma_pk=vi["ma200"].iloc[pkpos]
    stretch=peak/ma_pk-1 if ma_pk==ma_pk else np.nan       # % above MA200 at the peak
    run2y=peak/vi["VNINDEX"].iloc[max(0,pkpos-504)]-1       # 2y run into the peak
    # days above MA200 in the 1y before the peak (persistence of the bull)
    seg=vi.iloc[max(0,pkpos-252):pkpos+1]; days_above=(seg["VNINDEX"]>seg["ma200"]).mean()
    # DT5G: was market in EX-BULL(5) or BULL(4) in the 6m before this washout's peak
    s6=st.reindex(vi.iloc[max(0,pkpos-126):pkpos+1].index).dropna()
    maxstate=int(s6.max()) if len(s6) else np.nan
    exbull=bool((s6==5).any()) if len(s6) else False
    rows.append(dict(washout=d.date(), regime=r["regime"], basket60=r["basket60"], win=r["basket60"]>0,
        peak_date=pk.date(), stretch_ma200=round(stretch*100,1), run_2y=round(run2y*100,0),
        bull_persist=round(days_above*100,0), max_state_6m=maxstate, exbull_before=exbull,
        further_drop=r["further_drop"]))
T=pd.DataFrame(rows)
# grind = the prolonged-bear declines per history (2018, 2022 cluster); tag by further_drop depth & known
T["GRIND"]=T["washout"].astype(str).str.startswith(("2018","2022"))
print("Overextension BEFORE each washout (peak in the prior 2y) vs outcome:")
print(T[["washout","regime","peak_date","stretch_ma200","run_2y","bull_persist","max_state_6m","exbull_before","further_drop","basket60","GRIND"]].to_string(index=False))
print("\nGRIND (2018/2022) vs the rest — was the prior rally more stretched?")
for lab,g in T.groupby("GRIND"):
    print(f"  GRIND={lab}: n={len(g)} | stretch_MA200 {g.stretch_ma200.mean():5.1f}% | run_2y {g.run_2y.mean():5.0f}% "
          f"| bull_persist {g.bull_persist.mean():3.0f}% | exbull_before {100*g.exbull_before.mean():3.0f}% "
          f"| further_drop {g.further_drop.mean():5.1f}%")
print("\nNote: 2020 COVID is the key counter-example — long rally too, but a V not a grind (exogenous shock + stimulus).")
print(T[T.washout.astype(str).str.startswith('2020')][['washout','stretch_ma200','run_2y','exbull_before','basket60','further_drop']].to_string(index=False))
