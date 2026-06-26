"""Are we MISSING crisis opportunities? Enumerate every VNINDEX drawdown episode 2013->now,
measure the OPPORTUNITY at each trough (forward 6M/12M index return), the VALUATION at the trough
(market PE percentile + liquid-universe median own-pbz = recovery-park's actual signal), and whether
our re-risk gates WOULD fire there (DT5G state in CRISIS/BEAR AND median pbz<=-0.5).

Goal: separate 'good opportunities we could capture' from 'value traps the gate correctly avoids',
and see how many good ones our current (conservative) re-risk machinery actually catches.

profit cols are NOT used here — forward return = pure VNINDEX close-to-close (no look-ahead beyond
the realized index path). DT5G state from 2014; pre-2014 uses base vnindex_5state. Cache threads=1."""
import os, sys
os.environ.setdefault("BQ_LOCAL_CACHE", "data/bq_cache")
os.chdir("/home/trido/thanhdt/WorkingClaude"); sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
import numpy as np, pandas as pd
from bq_local_cache import get_cache
lc = get_cache()

# --- VNINDEX level + market PE (mirror on stock rows) ---
v = lc.query("""SELECT t.time, MAX(t.VNINDEX) vni, MAX(t.VNINDEX_PE) pe
FROM tav2_bq.ticker t WHERE t.time>=DATE '2013-01-01' AND t.VNINDEX IS NOT NULL
GROUP BY t.time ORDER BY t.time""")
v["time"] = pd.to_datetime(v["time"]); v = v.sort_values("time").reset_index(drop=True)
v["pe_pct5y"] = v["pe"].rolling(1250, min_periods=250).apply(lambda s: (s.iloc[-1] >= s).mean(), raw=False)

# --- liquid-universe median own-pbz per date (recovery-park signal) ---
pb = lc.query("""SELECT t.time, APPROX_QUANTILES((t.PB-t.PB_MA5Y)/NULLIF(t.PB_SD5Y,0),2)[OFFSET(1)] pbz_med
FROM tav2_bq.ticker_prune t WHERE t.time>=DATE '2013-01-01' AND t.PB_SD5Y>0
GROUP BY t.time""")
pb["time"] = pd.to_datetime(pb["time"])
v = v.merge(pb, on="time", how="left")

# --- DT5G state (2014+) + base state fallback ---
st = lc.query("SELECT s.time, s.state FROM tav2_bq.vnindex_5state_dt5g_live s")
st["time"] = pd.to_datetime(st["time"])
v = v.merge(st, on="time", how="left")
ST = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EXBULL"}

# --- DISTINCT drawdown troughs: local minima with dd<=-12% from running peak, confirmed by a
# >=+12% rebound off the trough, and separated from the prior trough by >=+12% (so multi-year
# below-peak stretches like 2018->2020 or 2022->2025 split into the distinct dips a human counts). ---
vni = v["vni"].values
peak = np.maximum.accumulate(vni)
dd = vni/peak - 1
W = 63                                  # +-3 months local-min window
DDT = -0.12; REB = 0.12
cand = []
for i in range(len(vni)):
    if dd[i] > DDT: continue
    lo = max(0, i-W); hi = min(len(vni), i+W+1)
    if vni[i] != vni[lo:hi].min(): continue          # local min over +-W
    fwd_max = vni[i:hi].max()
    if fwd_max/vni[i]-1 < REB and i < len(vni)-W: continue   # needs a real rebound (skip if still falling at series end)
    cand.append(i)
# de-dup troughs closer than W days, keep the deeper; require >=+REB intervening bounce between kept troughs
episodes = []
for i in cand:
    if episodes:
        j = episodes[-1]
        between_max = vni[j:i+1].max()
        same_dip = (between_max/max(vni[i],vni[j])-1 < REB) or (i-j < W)
        if same_dip:
            if vni[i] < vni[j]: episodes[-1] = i      # deeper trough of the same dip
            continue
    episodes.append(i)

def fwd(i, h):
    j = min(i+h, len(v)-1)
    return v["vni"].iloc[j]/v["vni"].iloc[i]-1 if v["vni"].iloc[i]>0 else np.nan

rows = []
for ti in episodes:
    r = v.iloc[ti]
    peak_i = v.iloc[:ti+1]["vni"].idxmax()
    dd_depth = r["vni"]/v["vni"].iloc[peak_i]-1
    state = ST.get(int(r["state"]), "?") if pd.notna(r["state"]) else "pre2014"
    pbz = r["pbz_med"]
    park_fire = (state in ("CRISIS","BEAR")) and pd.notna(pbz) and pbz <= -0.5
    rows.append({"trough": r["time"].date(), "vni": round(r["vni"]),
                 "dd_depth%": round(dd_depth*100,1),
                 "PE": round(r["pe"],1) if pd.notna(r["pe"]) else None,
                 "PE_pctile5y": round(r["pe_pct5y"],2) if pd.notna(r["pe_pct5y"]) else None,
                 "pbz_med": round(pbz,2) if pd.notna(pbz) else None,
                 "state": state,
                 "fwd6M%": round(fwd(ti,126)*100,1), "fwd12M%": round(fwd(ti,252)*100,1),
                 "recpark_fires": "YES" if park_fire else "no"})
R = pd.DataFrame(rows)
print(f"=== VNINDEX drawdown episodes (>=15% peak->trough) 2013->now: {len(R)} troughs ===\n")
print(R.to_string(index=False))

print("\n--- READ ---")
print("OPPORTUNITY = fwd6M/12M from trough. VALUE-TRAP risk = expensive (high PE_pctile / pbz_med>0).")
print("recpark_fires = our conservative re-risk gate would deploy idle cash there (CRISIS/BEAR & cheap).")
good = R[(R["fwd12M%"]>15)]
print(f"\nGood opportunities (fwd12M>15%): {len(good)}/{len(R)}; of those, recpark fired on "
      f"{(good['recpark_fires']=='YES').sum()} (rest = caught by NEUTRAL re-risk/price-based DT base, or missed).")
print(f"Mean fwd12M where recpark FIRES: {R[R.recpark_fires=='YES']['fwd12M%'].mean():.1f}% "
      f"vs where it does NOT: {R[R.recpark_fires=='no']['fwd12M%'].mean():.1f}%  "
      f"(gate should concentrate on the higher-return troughs).")
