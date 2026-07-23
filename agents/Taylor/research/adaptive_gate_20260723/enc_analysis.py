# -*- coding: utf-8 -*-
"""
Family-2 (enC shortcut) focused analysis + noise quantification.
The ONLY path that can buy lead in real crashes is shortening enC (into-CRISIS),
because real crashes go NEUTRAL->raw-CRISIS, not NEUTRAL->raw-BEAR.
Question: does shortening enC on '3 consecutive down closes' buy lead WITHOUT
exploding false-panic commits? The raw base fires CRISIS 763/3130 days (24%).
"""
import numpy as np, pandas as pd, sys
sys.path.insert(0,'/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/adaptive_gate_20260723')
from state_analysis import dt_4gate, dt_4gate_adaptive, consec_down, df, states, close, time

d=pd.to_datetime(time)
cd=consec_down(close)
base=dt_4gate(states)

def transitions(series):
    return [(t,int(series[t-1]),int(series[t])) for t in range(1,len(series)) if series[t]!=series[t-1]]

# --- how noisy is raw CRISIS? count raw=1 "episodes" and their fwd outcome ---
raw=states
# raw crisis onsets (raw flips to 1)
onsets=[t for t in range(1,len(raw)) if raw[t]==1 and raw[t-1]!=1]
print(f"raw-CRISIS onset events: {len(onsets)}")
# for each onset, did VNINDEX fall >=8% within 40 sessions after (=a 'real' crisis start)?
real=0; fake=0
for t in onsets:
    fwd=close[t:min(t+40,len(close))]
    mn=fwd.min()/close[t]-1
    if mn<=-0.08: real+=1
    else: fake+=1
print(f"  raw-CRISIS onsets that dropped >=8% within 40d: {real} REAL / {fake} FAKE ({100*fake/(real+fake):.0f}% fake)")

# --- Family-2 CRISIS commit timing vs default enC=25 ---
def crisis_commits(series):
    return [t for t in range(1,len(series)) if series[t]==1 and series[t-1]!=1]

for tag,kw in [("BASE_enC25",dict()),
               ("F2_K1c10_K23",dict(adapt_enC=True,K1c=10,K2=3,K1=3)),
               ("F2_K1c15_K24",dict(adapt_enC=True,K1c=15,K2=4,K1=3)),
               ("F2_K1c7_K23", dict(adapt_enC=True,K1c=7, K2=3,K1=3))]:
    s = base if not kw else dt_4gate_adaptive(states,close,**kw)
    cc=crisis_commits(s)
    # for each CRISIS commit, fwd 20d min return (did it keep falling = good, or bounce = false panic)
    false_panic=0; good=0; leads=[]
    for t in cc:
        fwd=close[t:min(t+20,len(close))]
        fret=close[min(t+20,len(close)-1)]/close[t]-1   # 20d fwd return after committing CRISIS
        if fret>0.03: false_panic+=1     # market rose >3% after we de-risked to CRISIS = we sold the bottom
        elif fret< -0.03: good+=1
    print(f"{tag:15s} CRISIS_commits={len(cc):3d}  false_panic(fwd20>+3%)={false_panic:2d}  good(fwd20<-3%)={good:2d}  total_trans={len(transitions(s))}")

# --- explicit lead time INTO CRISIS in the 2 real deep crashes ---
print("\nLead INTO CRISIS(==1) in real deep crashes:")
for tag,kw in [("BASE",dict()),("F2_K1c10_K23",dict(adapt_enC=True,K1c=10,K2=3,K1=3)),
               ("F2_K1c7_K23",dict(adapt_enC=True,K1c=7,K2=3,K1=3))]:
    s = base if not kw else dt_4gate_adaptive(states,close,**kw)
    row=[tag]
    for lo,hi in [("2018-04-01","2018-07-01"),("2022-01-01","2022-06-01"),
                  ("2025-03-01","2025-06-01"),("2026-06-01","2026-07-22")]:
        m=(d>=pd.Timestamp(lo))&(d<=pd.Timestamp(hi))
        idx=np.where(m)[0]
        fc=next((t for t in idx if s[t]==1),None)
        row.append(str(d[fc].date()) if fc is not None else "never")
    print(f"  {row[0]:14s} 2018:{row[1]:11s} 2022:{row[2]:11s} 2025:{row[3]:11s} 2026:{row[4]:11s}")
