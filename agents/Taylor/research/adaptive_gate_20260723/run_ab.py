# -*- coding: utf-8 -*-
"""
A/B driver: run run_5systems_prodspec with STATE_OVERRIDE=dt5g, patching the DT-4gate
to the ADAPTIVE variant. Faithful because the macro cap is base-independent:
  adaptive_DT5G[t] = min(adaptive_dt4[t], cap[t]) if cap!=9 else adaptive_dt4[t]
where cap comes from the UNMODIFIED production pipeline and adaptive_dt4 re-gates the
raw v34b base with the price-evidence shortcut.

Env: ADAPT_MODE = base | adaptive   ADAPT_K1 ADAPT_K2 ADAPT_ENC ADAPT_K1C
Output CSV (from the harness) is renamed to include the mode tag.
"""
import os, sys
WORKDIR="/home/trido/thanhdt/WorkingClaude"; os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
import numpy as np, pandas as pd
import macro_state_live as msl

MODE = os.environ.get("ADAPT_MODE","adaptive")
K1  = int(os.environ.get("ADAPT_K1","3"));   K2  = int(os.environ.get("ADAPT_K2","3"))
ENC = os.environ.get("ADAPT_ENC","0")=="1";  K1C = int(os.environ.get("ADAPT_K1C","10"))

def consec_down(close):
    n=len(close); cd=np.zeros(n,int)
    for t in range(1,n): cd[t]=cd[t-1]+1 if close[t]<close[t-1] else 0
    return cd

def dt_4gate_adaptive(states, close, default=10,enC=25,exC=10,enX=25,exX=10,
                      K1=3,K2=3,adapt_enC=False,K1c=10):
    cd=consec_down(close); out=states.copy(); committed=states[0]; ps,pr=states[0],1
    for t in range(1,len(states)):
        s=states[t]
        if s==ps: pr+=1
        else: ps,pr=s,1
        if ps==committed: out[t]=committed; continue
        need=(enC if ps==1 else enX if ps==5 else exC if committed==1 else exX if committed==5 else default)
        if ps<committed and cd[t]>=K2:
            if ps not in (1,5): need=min(need,K1)
            elif ps==1 and adapt_enC: need=min(need,K1c)
        if pr>=need: committed=ps
        out[t]=committed
    return out

_ORIG = msl.get_macro_state
def get_macro_state_adaptive(start,end,bq=None):
    m = _ORIG(start,end,bq=bq)   # time, state, state_dt4, cap, easing  (cap base-independent)
    if MODE=="base":
        return m
    # raw v34b base + close aligned to m['time']
    if bq is None:
        from simulate_holistic_nav import bq as _bq; bq=_bq
    qs = min(pd.Timestamp(start), pd.Timestamp("2014-01-01")).strftime("%Y-%m-%d")
    raw = bq(f"SELECT s.time, s.state FROM tav2_bq.vnindex_5state_tam_quan_v34b_clean AS s "
             f"WHERE s.time BETWEEN DATE '{qs}' AND DATE '{end}' ORDER BY s.time")
    raw["time"]=pd.to_datetime(raw["time"])
    px = bq(f"SELECT t.time, t.Close FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' "
            f"AND t.time BETWEEN DATE '{qs}' AND DATE '{end}' ORDER BY t.time")
    px["time"]=pd.to_datetime(px["time"])
    g = raw.merge(px,on="time",how="left").sort_values("time").reset_index(drop=True)
    g["Close"]=g["Close"].ffill()
    adt4 = dt_4gate_adaptive(g["state"].values.astype(int), g["Close"].values.astype(float),
                             K1=K1,K2=K2,adapt_enC=ENC,K1c=K1C)
    g["adt4"]=adt4
    # slice to output window and align to m by time
    mm = m.merge(g[["time","adt4"]], on="time", how="left")
    mm["adt4"]=mm["adt4"].ffill().bfill().astype(int)
    cap = mm["cap"].values.astype(int)
    a4  = mm["adt4"].values
    sm  = np.where(cap!=9, np.minimum(a4,cap), a4).astype(int)
    out = pd.DataFrame({"time":mm["time"],"state":sm,"state_dt4":a4,
                        "cap":mm["cap"],"easing":mm["easing"]})
    ndiff=int((out["state"]!=m["state"]).sum())
    print(f"[ADAPTIVE gate K1={K1} K2={K2} encAdapt={ENC} K1c={K1C}] "
          f"{ndiff} DT5G days differ from production base-gate ({len(out)} rows)")
    return out

msl.get_macro_state = get_macro_state_adaptive
os.environ["STATE_OVERRIDE"]="dt5g"
os.environ.setdefault("START_DATE","2014-01-01")
os.environ.setdefault("END_DATE","2026-05-15")

# exec the canonical harness in this patched namespace
src=open(os.path.join(WORKDIR,"run_5systems_prodspec.py")).read()
g=dict(__name__="__main__", __file__=os.path.join(WORKDIR,"run_5systems_prodspec.py"))
exec(compile(src, "run_5systems_prodspec.py","exec"), g)
