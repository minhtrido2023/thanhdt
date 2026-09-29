import os, sys, numpy as np, pandas as pd
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)
sys.path.insert(0, os.path.join(WORKDIR, "mike/agents/Taylor/research/adaptive_exclusion_20260904"))
from simulate_holistic_nav import bq
import custom_basket_dynfork as cbd

START, END = "2014-01-01", "2026-06-15"
V3DIR = os.path.join(WORKDIR, "mike/agents/Taylor/research/adaptive_exclusion_20260904/v3")
CACHE = os.path.join(V3DIR, "cache"); os.makedirs(CACHE, exist_ok=True)
DYN_CSV = os.path.join(V3DIR, "dynamic_exclude_events_v3_is_only.csv")

def _m(s, r):
    yrs = (s.index[-1]-s.index[0]).days/365.25
    cagr = (s.iloc[-1]/s.iloc[0])**(1/yrs)-1
    spd = len(r)/yrs
    sharpe = r.mean()/r.std()*np.sqrt(spd) if r.std()>0 else 0
    dd = (s/s.cummax()-1).min()
    return dict(CAGR=cagr*100, Sharpe=sharpe, MaxDD=dd*100, Calmar=(cagr*100)/abs(dd*100) if dd<0 else 0)

def window(lvl, a, b):
    s = pd.Series(lvl).sort_index(); s.index = pd.to_datetime(s.index)
    if a is not None: s = s[s.index >= a]
    if b is not None: s = s[s.index <= b]
    s = s / s.iloc[0]
    return _m(s, s.pct_change().dropna())

navp = os.path.join(CACHE, "nav_scenarioE.csv"); memp = os.path.join(CACHE, "mem_scenarioE.csv")
if os.path.exists(navp) and os.path.exists(memp):
    print("[load cached] scenarioE")
    sv = pd.read_csv(navp, parse_dates=["date"]).set_index("date")["nav"]
    memdf = pd.read_csv(memp, parse_dates=["rebal_date"])
else:
    os.environ["BASKET_SELECT"] = "yieldcombo"
    os.environ["BASKET_EXCLUDE"] = ""
    os.environ["BASKET_DYNAMIC_GATE_CSV"] = DYN_CSV
    print("[build] scenarioE: BANNED empty + IS-only-threshold gate (v3, blind-selected thresholds)")
    lvl, adv, memdf, bx = cbd.build_pit(bq, START, END, quality="none", rebal="q2m5",
                                        gate_rating=3, weight_scheme="namecap")
    sv = pd.Series(lvl); sv.index = pd.to_datetime(sv.index); sv = sv.sort_index()
    sv.rename("nav").rename_axis("date").to_csv(navp)
    memdf.to_csv(memp, index=False)

WINS = [("FULL 2014->now", None, None), ("IS 2014-2019", None, pd.Timestamp("2019-12-31")),
        ("OOS 2020->now", pd.Timestamp("2020-01-01"), None)]
rows = []
for wt, a, b in WINS:
    x = window(sv, a, b); x.update(window=wt)
    rows.append(x)
    print(f"  {wt:<16} CAGR {x['CAGR']:6.2f}%  Sharpe {x['Sharpe']:.2f}  MaxDD {x['MaxDD']:6.1f}%  Calmar {x['Calmar']:.2f}")
pd.DataFrame(rows).to_csv(os.path.join(V3DIR, "scenarioE_metrics.csv"), index=False)
print("[done step5 scenario E]")
