# -*- coding: utf-8 -*-
"""capit_regime_context.py — test the user's hypothesis (2026-06-12): a washout that fires
SOON AFTER an EX-BULL phase, WITHOUT an intervening correction, is dangerous because the market
is still extended above its long-run mean -> the 'panic' is just the first leg of mean reversion,
not a true capitulation bottom.

For each CAPIT washout event, compute context features and line them up against the realized
forward VNINDEX return (the sleeve-free signal outcome):
  - close/MA200            : extension above the 200d mean (>1 = still above mean = air below)
  - days_since_exbull      : sessions since the last DT5G EX-BULL (state 5)
  - corrected_since_exbull : did a CRISIS/BEAR (state<=2) occur between that EX-BULL and the event?
  - drawdown_since_exb_pk  : decline from the post-EX-BULL price peak to the event (how far it has fallen)
  - dd52w                  : 52w drawdown at event
  - fwd20/60/120 VNINDEX   : outcome
"""
import os, sys, io, bisect
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
from simulate_holistic_nav import bq

# events from the audit ledger
A = pd.read_csv("data/v23c_golive_audit_2014_now.csv", low_memory=False)
ev = A[A["record_type"] == "EVENT_CAPIT"].copy()
ev["ymd"] = pd.to_datetime(ev["ymd"]); ev = ev.reset_index(drop=True)

# VNINDEX close + MA200, DT5G states
vni = bq("SELECT t.time, t.Close, t.MA200 FROM tav2_bq.ticker t WHERE t.ticker='VNINDEX' "
         "AND t.time BETWEEN DATE '2013-01-01' AND DATE '2026-06-11' ORDER BY t.time")
vni["time"] = pd.to_datetime(vni["time"])
vd = list(vni["time"]); close = vni["Close"].values; ma200 = vni["MA200"].values
cidx = {t: i for i, t in enumerate(vd)}
st = bq("SELECT s.time, s.state FROM tav2_bq.vnindex_5state_dt5g_live s ORDER BY s.time")
st["time"] = pd.to_datetime(st["time"])
state_ser = st.set_index("time")["state"]
sdays = list(state_ser.index); sval = state_ser.values

def fwd(d0, h):
    i = bisect.bisect_left(vd, pd.Timestamp(d0))
    if i >= len(vd) or i + h >= len(vd): return np.nan
    return (close[i + h] / close[i] - 1) * 100

def last_exbull_before(d0):
    # last session with state==5 strictly before d0
    j = bisect.bisect_left(sdays, pd.Timestamp(d0))
    for k in range(j - 1, -1, -1):
        if sval[k] == 5: return sdays[k]
    return None

rows = []
for r in ev.itertuples():
    d0 = r.ymd; size = float(r.value)
    i = cidx.get(pd.Timestamp(d0))
    if i is None:
        i = bisect.bisect_left(vd, pd.Timestamp(d0)); i = min(i, len(vd) - 1)
    ext = close[i] / ma200[i] if ma200[i] and not np.isnan(ma200[i]) else np.nan
    leb = last_exbull_before(d0)
    dse = (pd.Timestamp(d0) - leb).days if leb is not None else None
    # corrected since exbull: any state<=2 between leb and d0
    corrected = None; dd_since_pk = np.nan
    if leb is not None:
        seg = state_ser[(state_ser.index >= leb) & (state_ser.index < pd.Timestamp(d0))]
        corrected = bool((seg <= 2).any())
        # peak price from leb to d0, drawdown to event
        cseg = vni[(vni["time"] >= leb) & (vni["time"] <= pd.Timestamp(d0))]["Close"]
        if len(cseg): dd_since_pk = (close[i] / cseg.max() - 1) * 100
    # dd52w
    lo = max(0, i - 252)
    dd52 = (close[i] / np.nanmax(close[lo:i + 1]) - 1) * 100
    rows.append({"date": d0.date(), "state": int(r.state), "size": size,
                 "ext_ma200": ext, "dd52w": dd52,
                 "days_since_exbull": dse, "corrected_since_exb": corrected,
                 "dd_since_exb_peak": dd_since_pk,
                 "fwd60": fwd(d0, 60), "fwd120": fwd(d0, 120)})
d = pd.DataFrame(rows)

pd.set_option("display.width", 200); pd.set_option("display.max_columns", 20)
print("CAPIT washout events — regime context vs forward VNINDEX outcome")
print("(sorted by fwd60; hypothesis: recent EX-BULL + ext>1 + not-yet-corrected => bad)\n")
ds = d.sort_values("fwd60")
for r in ds.itertuples():
    dse = f"{r.days_since_exbull:>4}d" if r.days_since_exbull is not None else "  none"
    corr = ("yes" if r.corrected_since_exb else "NO ") if r.corrected_since_exb is not None else " - "
    print(f"  {str(r.date):>11} st{r.state} sz{r.size:.2f} | ext_MA200 {r.ext_ma200:>5.2f} "
          f"dd52w {r.dd52w:>+6.1f}% | since_EXB {dse} corrected {corr} "
          f"dd_since_pk {r.dd_since_exb_peak:>+6.1f}% | fwd60 {r.fwd60:>+6.1f}% fwd120 {r.fwd120:>+6.1f}%")

# Hypothesis split: "early post-euphoria" = recent EX-BULL (<=400d) AND not yet corrected AND still extended (ext>=1)
d["early_post_euphoria"] = d.apply(
    lambda x: (x["days_since_exbull"] is not None and x["days_since_exbull"] <= 400
               and (x["corrected_since_exb"] is False)
               and (pd.notna(x["ext_ma200"]) and x["ext_ma200"] >= 1.0)), axis=1)
print("\n" + "=" * 70)
print("HYPOTHESIS SPLIT — 'early post-euphoria' (EX-BULL<=400d ago, NOT corrected, ext>=1.0):")
for flag, g in d.groupby("early_post_euphoria"):
    lbl = "EARLY-POST-EUPHORIA (risky)" if flag else "other (corrected / not-post-EXB / cheap)"
    print(f"  {lbl:<42} n={len(g):>2}  mean fwd60 {g['fwd60'].mean():>+6.1f}%  "
          f"win {(g['fwd60']>0).mean()*100:>3.0f}%  worst {g['fwd60'].min():>+6.1f}%")
print("\nEvents flagged early-post-euphoria:", list(d[d['early_post_euphoria']]['date'].astype(str)))
