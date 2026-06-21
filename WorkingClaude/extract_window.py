import sys, pandas as pd, numpy as np
df = pd.read_csv(sys.argv[1], low_memory=False); start = sys.argv[2]
d = df[df["combined_nav"].notna() & df["ymd"].notna()].copy()
d["ymd"] = pd.to_datetime(d["ymd"], errors="coerce")
d = d.dropna(subset=["ymd"]).sort_values("ymd")
nav = d.groupby("ymd")["combined_nav"].last().astype(float)
vni = d.groupby("ymd")["vni_close"].last().astype(float)
w = nav[nav.index >= start]; wv = vni[vni.index >= start]
def mdd(s): return (s / s.cummax() - 1).min() * 100
print(f"window {w.index[0].date()} -> {w.index[-1].date()} ({(w.index[-1]-w.index[0]).days}d)")
print(f"  SLEEVE : ret {(w.iloc[-1]/w.iloc[0]-1)*100:+6.1f}%   maxDD {mdd(w):6.1f}%   "
      f"NAV {w.iloc[0]/1e9:.2f}B -> {w.iloc[-1]/1e9:.2f}B")
print(f"  VNINDEX: ret {(wv.iloc[-1]/wv.iloc[0]-1)*100:+6.1f}%   maxDD {mdd(wv):6.1f}%")
print(f"  ALPHA  : {((w.iloc[-1]/w.iloc[0]) - (wv.iloc[-1]/wv.iloc[0]))*100:+6.1f}pp")
me = w.resample("ME").last(); mv = wv.resample("ME").last()
pv, pi = w.iloc[0], wv.iloc[0]
print("  monthly:")
for t in me.index:
    print(f"    {t.strftime('%Y-%m')}: sleeve {(me[t]/pv-1)*100:+6.1f}%   vni {(mv[t]/pi-1)*100:+6.1f}%")
    pv, pi = me[t], mv[t]
