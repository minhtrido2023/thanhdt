#!/usr/bin/env python3
"""
backtest_crisis_capitulation.py
===============================================================================
Answers "gi? d?n khi nao?" — backtests the DT5G x 8L crisis-capitulation entry
under 7 exit rules, so the data picks the holding period.

Tactical sleeve: in CASH, deploys 100% into an equal-weight basket of 8L
quality+golden names when the capitulation signal fires (T+1, 0.3% round-trip),
holds per the exit rule, returns to cash. Two entry triggers compared:
  STRONG = oversold breadth >= 40% (extreme washout, any state)
  WATCH  = DT5G CRISIS & oversold >= 5.7%

Basket (graded fallback): quality&golden(pb_z<-1) -> quality&pb_z<0 -> quality,
all with liquidity >= 2B/day. Benchmark = EW prune index over the same window.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, subprocess
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
PROJECT = "lithe-record-440915-m9"
SDK_BIN = r"C:\Users\hotro\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin"
COST = 0.003   # round-trip
CAP  = 252     # max hold (trading days)

def bq(sql):
    env = dict(os.environ); env["PATH"] = env.get("PATH","")+os.pathsep+SDK_BIN
    env.setdefault("CLOUDSDK_PYTHON", SDK_BIN+r"\..\platform\bundledpython\python.exe")
    s = " ".join(sql.split())
    o = subprocess.run([SDK_BIN+r"\bq.cmd","query","--use_legacy_sql=false",
        f"--project_id={PROJECT}","--format=csv","--max_rows=200000",s],
        capture_output=True, text=True, env=env)
    if o.returncode != 0: raise RuntimeError(o.stdout+o.stderr)
    return pd.read_csv(io.StringIO(o.stdout))

# ---- daily state + EW index benchmark ---------------------------------------
D = pd.read_csv(os.path.join(WORKDIR,"data","daily_comovement_dt5g.csv"), parse_dates=["time"]).sort_values("time").reset_index(drop=True)
D["ew"] = (1+D["avg_ret"]).cumprod()
state_by = D.set_index("time")["state"]
tdates = D["time"].tolist()

def declust(d, gap=30):
    d = d.sort_values("time").copy(); d["g"]=d["time"].diff().dt.days.fillna(999); d["c"]=(d["g"]>=gap).cumsum()
    return d.groupby("c").first()["time"].tolist()

triggers = {
    "STRONG": declust(D[D["pct_oversold"]>=0.40]),
    "WATCH":  declust(D[(D["state"]==1)&(D["pct_oversold"]>=0.057)]),
}

def basket_paths(d):
    """all (quality & liq>=2) names at d with entry pb_z + forward 380d Close/pb_z path."""
    ds = pd.Timestamp(d).date()
    q = bq(f"""
    WITH elig AS (
      SELECT p.ticker, SAFE_DIVIDE(p.PB-p.PB_MA5Y,p.PB_SD5Y) AS pbz0
      FROM tav2_bq.ticker_prune p
      WHERE p.time = DATE '{ds}' AND p.ROE_Min5Y>=0.12 AND p.ROIC5Y>=0.10 AND p.FSCORE>=6
        AND COALESCE(p.Price,p.Close)*p.Volume/1e9 >= 2 )
    SELECT f.time, f.ticker, f.Close, SAFE_DIVIDE(f.PB-f.PB_MA5Y,f.PB_SD5Y) AS pbz, e.pbz0
    FROM tav2_bq.ticker_prune f JOIN elig e USING(ticker)
    WHERE f.time >= DATE '{ds}' AND f.time <= DATE_ADD(DATE '{ds}', INTERVAL 380 DAY)
    ORDER BY f.ticker, f.time """)
    if len(q)==0: return None, None, None
    q["time"]=pd.to_datetime(q["time"])
    pbz0 = q.groupby("ticker")["pbz0"].first()
    # graded basket tier
    golden = pbz0[pbz0 < -1].index.tolist()
    cheap  = pbz0[pbz0 < 0].index.tolist()
    allq   = pbz0.index.tolist()
    if   len(golden)>=3: names, tier = golden, "Q+golden"
    elif len(cheap) >=3: names, tier = cheap,  "Q+cheap"
    else:                names, tier = allq,   "Q-all"
    q = q[q["ticker"].isin(names)]
    px  = q.pivot(index="time", columns="ticker", values="Close").sort_index().ffill()
    pbz = q.pivot(index="time", columns="ticker", values="pbz").sort_index().ffill()
    return px, pbz, (tier, len(names))

def run_event(d):
    px, pbz, meta = basket_paths(d)
    if px is None or len(px) < 5: return None
    tier, nn = meta
    idx = px.index
    cum = px.div(px.iloc[0])            # per-ticker cumret from entry
    nav = cum.mean(axis=1).values       # equal-weight basket NAV (k=0..)
    pbz_med = pbz.median(axis=1).values
    st = np.array([int(state_by.get(t, 3)) for t in idx])
    K = len(nav)-1
    # EW benchmark over same dates
    ewser = D.set_index("time")["ew"].reindex(idx).ffill().values
    def at(k): k=min(k,K); return nav[k]/nav[0]-1 - COST
    def alpha(k): k=min(k,K); return (nav[k]/nav[0]-1) - (ewser[k]/ewser[0]-1)
    rules = {}
    for h in (40,60,120,252): rules[f"FIX{h}"]=(min(h,K))
    # REGIME: first reach BULL/EXBULL
    reg = np.where(np.isin(st, [4,5]))[0]; reg = reg[reg>0]
    rules["REGIME_BULL"] = int(reg[0]) if len(reg) else min(CAP,K)
    # VAL: pb_z normalized >=0
    val = np.where(pbz_med >= 0)[0]; val = val[val>0]
    rules["VAL_pbz>=0"] = int(val[0]) if len(val) else min(CAP,K)
    # TRAIL 15%
    peak=nav[0]; tk=min(CAP,K)
    for k in range(1,min(CAP,K)+1):
        peak=max(peak,nav[k])
        if nav[k] <= peak*0.85: tk=k; break
    rules["TRAIL15"]=tk
    out={"date":pd.Timestamp(d).date(),"tier":tier,"n":nn,"K":K}
    for r,k in rules.items():
        out[r+"_ret"]=round(at(k)*100,1); out[r+"_hold"]=int(min(k,K)); out[r+"_alpha"]=round(alpha(k)*100,1)
    return out

for trig, dates in triggers.items():
    print("="*86); print(f"TRIGGER = {trig}   ({len(dates)} episodes)"); print("="*86)
    recs=[run_event(d) for d in dates]; recs=[r for r in recs if r]
    R=pd.DataFrame(recs)
    rules=["FIX40","FIX60","FIX120","FIX252","REGIME_BULL","VAL_pbz>=0","TRAIL15"]
    # per-event table (return per rule)
    cols=["date","tier","n"]+[r+"_ret" for r in rules]
    print(R[cols].to_string(index=False))
    # rule summary
    print(f"\n  exit-rule summary ({trig}):")
    print(f"  {'rule':<13}{'medRet':>8}{'meanRet':>9}{'win%':>7}{'medHold':>9}{'medAlpha':>10}")
    for r in rules:
        rr=R[r+"_ret"]; print(f"  {r:<13}{rr.median():>8.1f}{rr.mean():>9.1f}{100*(rr>0).mean():>7.0f}"
                              f"{R[r+'_hold'].median():>9.0f}{R[r+'_alpha'].median():>10.1f}")
    # sleeve NAV (compound events in time order, cash between) for each rule
    print(f"\n  sleeve NAV (compounded across episodes, cash between):")
    for r in rules:
        mult=np.prod(1+R.sort_values('date')[r+'_ret'].values/100)
        print(f"    {r:<13} x{mult:.2f}")
    R.to_csv(os.path.join(WORKDIR,"data",f"bt_capitulation_{trig}.csv"),index=False)
print("\nSaved: data/bt_capitulation_STRONG.csv, data/bt_capitulation_WATCH.csv")
