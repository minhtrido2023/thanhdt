#!/usr/bin/env python3
"""CAPIT tranche event-study — ANALYSIS (job Taylor_20260726_125456).
Compares deployment schedules for each historical CAPIT washout fire:
  LUMP  : full size at fire date d0 (fill T+1 Open)  [= current production]
  T333  : 33/33/34 across d0 / stabilization / confirmation
  T532  : 50/30/20 across the same triggers
Triggers use ONLY existing signals (breadth_oversold, DT5G state):
  T2 (stabilization) : oversold rolled >=15% off its post-d0 peak (peaked, easing)
  T3 (confirmation)  : oversold < 0.20  OR  state improved above state@d0
  backstop           : any un-triggered tranche deploys at d0+MAXWAIT (default 40 sess)
Metrics per event: cost basis (vs lump), max MTM drawdown of committed capital,
terminal return at +60 (CAPIT_HOLD) and +120 sessions. Fills = T+1 Open (audit-faithful).
RESEARCH-ONLY.
"""
import os, json
import pandas as pd, numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
MAXWAIT = int(os.environ.get("MAXWAIT","40"))
T3_THR  = float(os.environ.get("T3_THR","0.20"))
HOLD    = 60
HOLD2   = 120

br  = pd.read_csv(f"{OUT}/breadth.csv", parse_dates=["time"]).sort_values("time").reset_index(drop=True)
st  = pd.read_csv(f"{OUT}/state.csv", parse_dates=["time"])
ev  = pd.read_csv(f"{OUT}/events.csv", parse_dates=["date"])
px  = pd.read_csv(f"{OUT}/prices.csv", parse_dates=["time"])
baskets = json.load(open(f"{OUT}/baskets.json"))

ovs = br.set_index("time")["oversold"]
sess = list(br["time"])                       # trading-session calendar (breadth days)
sidx = {d:i for i,d in enumerate(sess)}
state_ff = st.set_index("time")["state"].reindex(sess, method="ffill")
state_map = dict(zip(sess, state_ff.values))

# per-name price frames
px_by = {t: g.set_index("time").sort_index() for t,g in px.groupby("ticker")}

def sess_at(d, k):
    """session index d shifted by k sessions on the breadth calendar; None if OOB."""
    i = sidx.get(pd.Timestamp(d))
    if i is None:
        # align to nearest prior session
        arr = [x for x in sess if x <= pd.Timestamp(d)]
        if not arr: return None
        i = sidx[arr[-1]]
    j = i + k
    return sess[j] if 0 <= j < len(sess) else None

def find_T2(d0):
    i0 = sidx[pd.Timestamp(d0)]
    peak = ovs.iloc[i0]
    for j in range(i0+3, min(i0+MAXWAIT+1, len(sess))):
        peak = max(peak, ovs.iloc[j])
        if ovs.iloc[j] < 0.85*peak:
            return sess[j]
    return None

def find_T3(d0, t2):
    start = sidx[pd.Timestamp(t2)]+3 if t2 is not None else sidx[pd.Timestamp(d0)]+3
    s0 = state_map[pd.Timestamp(d0)]
    for j in range(start, min(sidx[pd.Timestamp(d0)]+MAXWAIT+1, len(sess))):
        if ovs.iloc[j] < T3_THR or (pd.notna(state_map[sess[j]]) and state_map[sess[j]] > s0):
            return sess[j]
    return None

def fill_open(t, name):
    """Open at session AFTER trigger t (T+1 fill). Fallback to nearest available."""
    nx = sess_at(t, 1)
    g = px_by.get(name)
    if g is None or nx is None: return None
    sub = g[g.index >= nx]
    if len(sub)==0: return None
    return float(sub["Open"].iloc[0])

def close_at(t, name):
    g = px_by.get(name)
    if g is None or t is None: return None
    sub = g[g.index <= pd.Timestamp(t)]
    if len(sub)==0: return None
    return float(sub["Close"].iloc[-1])

def path_close(name, d_from, d_to):
    g = px_by.get(name)
    if g is None: return None
    sub = g[(g.index>=pd.Timestamp(d_from)) & (g.index<=pd.Timestamp(d_to))]
    return sub["Close"] if len(sub) else None

SPLITS = {"LUMP":[1.0], "T333":[0.33,0.33,0.34], "T532":[0.50,0.30,0.20]}

def simulate_event(d0, names, split, backstop=True):
    """Return dict of metrics for one event/schedule. Equal-weight basket, capital=1."""
    d0 = pd.Timestamp(d0)
    t2 = find_T2(d0) if len(split)>1 else None
    t3 = find_T3(d0, t2) if len(split)>1 else None
    trig = [d0, t2, t3][:len(split)]
    # backstop: replace missing triggers with d0+MAXWAIT
    bs = sess_at(d0, MAXWAIT)
    fills = []
    for k,tk in enumerate(trig):
        if tk is None:
            tk = bs if backstop else None
        fills.append(tk)
    exitE  = sess_at(d0, HOLD)
    exitE2 = sess_at(d0, HOLD2)
    # per-name aggregation (equal weight)
    per = []
    for nm in names:
        buy0 = fill_open(d0, nm)                       # lump reference entry (also T1 entry)
        if not buy0 or buy0<=0: continue
        cexit  = close_at(exitE, nm)
        cexit2 = close_at(exitE2, nm)
        if not cexit: continue
        # weighted entry (cost basis) in units of lump entry
        wentry_num = 0.0; deployed = 0.0; term = 0.0; term2 = 0.0; idle = 0.0
        for f,tk in zip(split, fills):
            if tk is None:            # no backstop, tranche never deploys -> stays cash
                idle += f; continue
            fp = fill_open(tk, nm)
            if not fp or fp<=0:
                idle += f; continue
            wentry_num += f*fp
            deployed  += f
            term  += f*(cexit/fp)
            term2 += f*(cexit2/fp) if cexit2 else f*(cexit/fp)
        idle_val = idle*1.0                            # deposit ~0 over the window; conservative
        cb = (wentry_num/deployed)/buy0 if deployed>0 else np.nan   # cost basis ratio vs lump
        per.append({"name":nm,"cb":cb,"term":term+idle_val,"term2":term2+idle_val,
                    "deployed":deployed})
    if not per:
        return None
    pdf = pd.DataFrame(per)
    # basket MTM drawdown of committed capital over [d0, exitE]
    # build daily equal-weight value of the schedule
    dd = simulate_path_dd(d0, names, split, fills, exitE)
    return {"cb":pdf["cb"].mean(), "ret60":pdf["term"].mean()-1, "ret120":pdf["term2"].mean()-1,
            "maxdd":dd, "t2":t2, "t3":t3, "fills":[str(f.date()) if f is not None else None for f in fills],
            "avg_deployed":pdf["deployed"].mean()}

def simulate_path_dd(d0, names, split, fills, exitE):
    """max MTM drawdown of the committed-capital portfolio over [d0, exitE]."""
    if exitE is None: return np.nan
    d0 = pd.Timestamp(d0)
    days = [d for d in sess if d0<=d<=pd.Timestamp(exitE)]
    if not days: return np.nan
    # entry price per name per tranche
    vals = []
    for d in days:
        v = 0.0; wsum=0.0
        for nm in names:
            buy0 = fill_open(d0, nm)
            if not buy0: continue
            cd = close_at(d, nm)
            if not cd: continue
            nmval = 0.0; idle=0.0
            for f,tk in zip(split, fills):
                if tk is None or pd.Timestamp(tk)>d:      # not yet deployed -> cash (value f)
                    idle += f; continue
                fp = fill_open(tk, nm)
                if not fp: idle += f; continue
                nmval += f*(cd/fp)
            vals_nm = nmval + idle
            v += vals_nm; wsum += 1
        vals.append(v/wsum if wsum else np.nan)
    s = pd.Series(vals).dropna()
    if len(s)<2: return np.nan
    peak = s.cummax()
    return float((s/peak-1).min())

# ---- run ----
rows = []
for _, e in ev.iterrows():
    d0 = e["date"]; key = str(d0.date())
    names = baskets.get(key, [])
    if len(names) < 3:
        rows.append({"date":key,"state":e["state"],"dd52":e["dd52"],"n":len(names),"note":"skip(<3 names)"})
        continue
    # need forward data to exit; current live event has too little -> flag
    exitE = sess_at(d0, HOLD)
    too_recent = exitE is None or (pd.Timestamp(sess[-1]) - pd.Timestamp(d0)).days < 90
    r = {"date":key,"state":int(e["state"]),"dd52":e["dd52"],"n":len(names),
         "peak_ovs":e["peak_oversold"],"grind":bool(e["grind"])}
    for sk,split in SPLITS.items():
        m = simulate_event(d0, names, split)
        if m is None: continue
        r[f"{sk}_ret60"]  = m["ret60"]
        r[f"{sk}_ret120"] = m["ret120"]
        r[f"{sk}_dd"]     = m["maxdd"]
        if sk!="LUMP":
            r[f"{sk}_cb"]  = m["cb"]
            r[f"{sk}_t2"]  = m["fills"][1]
            r[f"{sk}_t3"]  = m["fills"][2]
    r["too_recent"] = too_recent
    rows.append(r)

res = pd.DataFrame(rows)
res.to_csv(f"{OUT}/results.csv", index=False)
pd.set_option("display.width",240); pd.set_option("display.max_columns",50)

# analysis-grade subset (have >=90d forward, >=3 names)
val = res[(res.get("too_recent")==False) & (res["n"]>=3)].copy()

print("="*130)
print(f"CAPIT TRANCHE EVENT-STUDY  (MAXWAIT={MAXWAIT}, T3_THR={T3_THR}, HOLD={HOLD}/{HOLD2})")
print("="*130)
show = ["date","state","dd52","n","peak_ovs","LUMP_ret60","T333_ret60","T532_ret60",
        "LUMP_ret120","T333_ret120","T532_ret120","T333_cb","T532_cb","LUMP_dd","T333_dd","T532_dd"]
show = [c for c in show if c in res.columns]
print(res[show].round(3).to_string(index=False))

print("\n--- AGGREGATE over analysis-grade events (n_events=%d) ---" % len(val))
for h in ["ret60","ret120"]:
    print(f"\n[{h}] mean:")
    for sk in SPLITS:
        c=f"{sk}_{h}"
        if c in val: print(f"   {sk:5s}: mean {val[c].mean():+.3%}   median {val[c].median():+.3%}")
    print(f"[{h}] tranche - lump (paired mean delta):")
    for sk in ["T333","T532"]:
        c=f"{sk}_{h}"; l=f"LUMP_{h}"
        if c in val and l in val:
            d=(val[c]-val[l]); print(f"   {sk}-LUMP: {d.mean():+.3%}  (win {int((d>0).sum())}/{d.notna().sum()})")
print("\n[cost basis vs lump] (<1 = tranche cheaper avg entry):")
for sk in ["T333","T532"]:
    c=f"{sk}_cb"
    if c in val: print(f"   {sk}: mean {val[c].mean():.4f}  median {val[c].median():.4f}  cheaper in {int((val[c]<1).sum())}/{val[c].notna().sum()}")
print("\n[max MTM drawdown of committed capital] (less negative = better):")
for sk in SPLITS:
    c=f"{sk}_dd"
    if c in val: print(f"   {sk:5s}: mean {val[c].mean():+.3%}  median {val[c].median():+.3%}")

# ---- IS/OOS split + per-event LOO on the analysis-grade set ----
print("\n" + "="*130)
print("WALK-FORWARD IS(2014-19) / OOS(2020+)  +  LEAVE-ONE-OUT robustness")
print("="*130)
val = val.copy()
val["yr"] = pd.to_datetime(val["date"]).dt.year
IS  = val[val["yr"]<=2019]; OOS = val[val["yr"]>=2020]
for lbl,sub in [("IS 2014-19",IS),("OOS 2020+",OOS)]:
    print(f"\n[{lbl}] n={len(sub)}")
    for h in ["ret60","ret120"]:
        for sk in ["T333","T532"]:
            d=(sub[f"{sk}_{h}"]-sub[f"LUMP_{h}"])
            print(f"   {sk}-LUMP {h}: {d.mean():+.3%} (win {int((d>0).sum())}/{d.notna().sum()})")
    for sk in ["T333","T532"]:
        dd=(sub[f"{sk}_dd"]-sub[f"LUMP_dd"])
        print(f"   {sk}-LUMP maxdd: {dd.mean():+.3%} (better in {int((dd>0).sum())}/{dd.notna().sum()})")

print("\n[LOO] drop each event, recompute mean(T333-LUMP ret60):")
d = (val["T333_ret60"]-val["LUMP_ret60"]).values
dates = val["date"].values
base = np.nanmean(d)
print(f"   full mean = {base:+.3%}")
for i in range(len(d)):
    loo = np.nanmean(np.delete(d,i))
    flag = "  <-- flips >0" if loo>0 else ""
    print(f"   drop {dates[i]}: {loo:+.3%}{flag}")
