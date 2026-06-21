import numpy as np, pandas as pd, os, sys
sys.path.insert(0, r"/home/trido/thanhdt/WorkingClaude")
os.chdir(r"/home/trido/thanhdt/WorkingClaude")
from simulate_state_timing import simulate_timing
from exp_velocity_minstay import rolling_mode, min_stay_filter, min_stay_velocity, count_transitions, MODE_WIN, MIN_STAY
m=pd.read_csv("data/vnindex_5state_intermediate.csv"); m["time"]=pd.to_datetime(m["time"])
dvg=m["state_dvg"].values.astype(int); rema=m["r_score_ema"].values.astype(float)

def short_derisk_runs(states, min_days=7):
    runs=0; i=0
    while i<len(states):
        j=i+1
        while j<len(states) and states[j]==states[i]: j+=1
        if i>0 and states[i]<states[i-1] and (j-i)<min_days: runs+=1
        i=j
    return runs

mode_state=rolling_mode(dvg,MODE_WIN)
print(f"short de-risk runs (<7) in state_dvg (pre-mode) : {short_derisk_runs(dvg)}")
print(f"short de-risk runs (<7) in mode_state (post-mode15): {short_derisk_runs(mode_state)}")

# Apply velocity-min_stay DIRECTLY on state_dvg (skip mode15) — does the idea do anything?
print("\n--- velocity-min_stay applied to state_dvg directly (NO mode15) ---")
for start in ("2011-01-01","2014-01-01"):
    base_v=min_stay_filter(dvg,MIN_STAY)  # plain min_stay, no mode
    rb=simulate_timing(pd.DataFrame({"time":m["time"],"state":base_v}),start_date=start)
    print(f"  [{start}] plain min_stay7 (no mode): CAGR {rb['cagr']*100:.2f}% DD {rb['max_dd']*100:.1f}% trans {count_transitions(base_v[(m['time']>=start).values])}")
    for vk in (3,5):
        slope=np.full(len(rema),np.nan); slope[vk:]=rema[vk:]-rema[:-vk]
        for q in (0.10,0.20,0.30):
            vs=min_stay_velocity(dvg,slope,MIN_STAY,vk=vk,q=q,floor=2)
            r=simulate_timing(pd.DataFrame({"time":m["time"],"state":vs}),start_date=start)
            d=(r['cagr']-rb['cagr'])*100
            print(f"  [{start}] velo vk{vk} q{int(q*100)} : CAGR {r['cagr']*100:.2f}% ({d:+.2f}pp) DD {r['max_dd']*100:.1f}% trans {count_transitions(vs[(m['time']>=start).values])}")
