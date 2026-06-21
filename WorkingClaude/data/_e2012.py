import pandas as pd, numpy as np, os
os.chdir(r"/home/trido/thanhdt/WorkingClaude")
v=pd.read_csv("data/VNINDEX.csv",usecols=["time","Close"]); v["time"]=pd.to_datetime(v["time"])
nav=pd.read_csv("data/dt4g_macro_overlay_nav.csv"); nav["time"]=pd.to_datetime(nav["time"])
d=nav.merge(v,on="time",how="left")
seg=d[(d["time"]>="2012-04-18")&(d["time"]<="2012-07-31")].reset_index(drop=True)
# easing-floor window = base CRISIS (state==1) but w_macro>=0.7
seg["base_crisis"]=(seg["state"]==1)
floor=seg[(seg["base_crisis"])&(seg["w_macro"]>=0.7)]
print("Base went CRISIS on:", seg[seg["base_crisis"]]["time"].min().date())
print(f"Easing-floor held NEUTRAL(w>=0.7) despite base-CRISIS: {len(floor)} sessions")
if len(floor):
    print("  from", floor["time"].min().date(), "to", floor["time"].max().date())
p0=seg["Close"].iloc[0]
peak=seg["Close"].max(); 
# price at start of floor window vs trough after
fstart=floor["time"].min(); 
after=seg[seg["time"]>=fstart]
trough=after["Close"].min(); troughd=after.loc[after["Close"].idxmin(),"time"]
print(f"\nVNINDEX 2012-04-18={p0:.1f}")
print(f"At easing-floor start ({fstart.date()})={seg.loc[seg['time']==fstart,'Close'].values[0]:.1f}")
print(f"Trough after floor start = {trough:.1f} on {troughd.date()}  (drop {(trough/seg.loc[seg['time']==fstart,'Close'].values[0]-1)*100:+.1f}% while floored at 70%)")
# NAV cost: macro (with easing floor) vs a hypothetical no-easing (follow base weight)
print(f"\nIn this window: nav_base end/start = {seg['nav_base'].iloc[-1]/seg['nav_base'].iloc[0]:.4f}")
print(f"               nav_macro end/start = {seg['nav_macro'].iloc[-1]/seg['nav_macro'].iloc[0]:.4f}")
