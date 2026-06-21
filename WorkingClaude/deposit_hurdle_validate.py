# -*- coding: utf-8 -*-
"""
deposit_hurdle_validate.py — validate the STATE-CONDITIONAL absolute deposit hurdle.
Idea (user): a stock's earnings yield 1/PE must clear deposit + a risk premium to deserve
a BUY in cash-competitive regimes. Apply ONLY in NEUTRAL/BEAR/CRISIS (state<=3), OFF in
BULL/EX-BULL; should bite hardest in BEAR/CRISIS; DEMOTE (not kill); must NOT over-filter.

Test design:
  - "BUY candidate" proxy = cheapest tercile by 1/PE within month & route (what the value axis surfaces).
  - hurdle: spread = 100/PE - deposit_rate (pp). pass if spread >= X.
  - For candidates, compare forward profit_2M of PASS vs FAIL buckets, split by DT5G state.
    Gate ADDS value iff FAIL bucket has clearly worse fwd returns in BEAR/CRISIS (state 1,2).
  - Pass-rate by year/state → over-filter check (how many deals would be demoted).
"""
import os, sys, subprocess, tempfile
from io import StringIO
import numpy as np, pandas as pd
WORKDIR = os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude")
sys.path.insert(0, WORKDIR)
from deposit_rate_vn import merge_deposit

def bq(sql):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False) as f:
        f.write(sql); tmp=f.name
    r=subprocess.run(f'cat "{tmp}" | bq query --quiet --use_legacy_sql=false '
                     f'--project_id=lithe-record-440915-m9 --format=csv --max_rows=100000',
                     capture_output=True,text=True,shell=True,timeout=300)
    os.unlink(tmp)
    if not r.stdout.strip(): raise RuntimeError("bq empty:\n"+r.stderr[-1500:])
    return pd.read_csv(StringIO(r.stdout.strip()))

df = pd.read_csv(f"{WORKDIR}/data/value_panel_2014.csv", parse_dates=["time"])
df = merge_deposit(df)
df["F_ey"] = np.where(df.PE>0, 100.0/df.PE, np.nan)
df["spread"] = df.F_ey - df.deposit_rate
df["mo"] = df.time.dt.to_period("M").dt.to_timestamp()

# DT5G monthly state (last obs per month)
st = bq("""SELECT s.time, s.state FROM tav2_bq.vnindex_5state_dt5g_live AS s
           WHERE s.time>=DATE '2014-01-01'
           QUALIFY ROW_NUMBER() OVER (PARTITION BY DATE_TRUNC(s.time,MONTH) ORDER BY s.time DESC)=1""")
st["mo"]=pd.to_datetime(st.time).dt.to_period("M").dt.to_timestamp()
df = df.merge(st[["mo","state"]], on="mo", how="left")
SNAME={1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EXBULL"}

LIQ=5e9
b = df[(df.turnover>=LIQ)&df.F_ey.notna()&df.profit_2M.notna()&df.state.notna()].copy()
# BUY-candidate proxy: cheapest tercile by 1/PE within (month, route)
b["ey_rank"] = b.groupby(["mo","route"]).F_ey.rank(pct=True)
cand = b[b.ey_rank>=0.667].copy()           # top-third earnings-yield = "value BUY zone"
print(f"panel rows={len(df)}  liquid+EY={len(b)}  BUY-candidates={len(cand)}")
print("state coverage (months):", df.dropna(subset=['state']).groupby('state').mo.nunique().to_dict())

print("\n### Forward profit_2M (median %) of BUY-candidates: PASS vs FAIL hurdle, by state ###")
for X in (2,3,4):
    print(f"\n  hurdle X = {X}pp  (pass: 1/PE - deposit >= {X})")
    print(f"    {'state':<9}{'n_pass':>7}{'n_fail':>7}{'pass%':>7}{'med_PASS':>10}{'med_FAIL':>10}{'edge(P-F)':>11}")
    for sgrp in (1,2,3,4,5):
        g=cand[cand.state==sgrp]
        if len(g)<40: continue
        p=g[g.spread>=X].profit_2M; f=g[g.spread<X].profit_2M
        if len(p)<10 or len(f)<10:
            print(f"    {SNAME[sgrp]:<9}{len(p):>7}{len(f):>7}{100*len(p)/len(g):>6.0f}%{'(thin)':>21}"); continue
        edge=p.median()-f.median()
        print(f"    {SNAME[sgrp]:<9}{len(p):>7}{len(f):>7}{100*len(p)/len(g):>6.0f}%{p.median():>10.2f}{f.median():>10.2f}{edge:>+11.2f}")

print("\n### Over-filter check: % of BUY-candidates DEMOTED by gate (state<=3 only), by year ###")
g3=cand[cand.state<=3]
for X in (2,3,4):
    yr=g3.groupby(g3.time.dt.year).apply(lambda d: 100*(d.spread<X).mean())
    print(f"  X={X}pp demote%:", " ".join(f"{y}:{v:.0f}" for y,v in yr.items()))
print("\n[done]")
