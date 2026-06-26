"""PROXY (cheap, causal daily — no harness yet) for the state-BLIND deep-cheap re-risk trigger.
User hypothesis: drop the CRISIS/BEAR state filter, but KEEP a valuation gate (pbz_med and/or
PE_pctile5y) as the real 'is this genuine fear' discriminator. Test whether that catches 2025-04
(+55% 12M, blocked today by the state filter) WITHOUT re-admitting the 2018/2019 NEUTRAL duds, and
WITHOUT over-firing in expensive markets.

Each gate is a CAUSAL daily rule (all inputs as-of T). We then look at the realized forward VNINDEX
6M return on every fire-day (the outcome, not an input). A good gate: high mean fwd6M, fires rarely,
covers the good troughs (2020/2022/2023/2025), skips the duds (2018/2019). Cache threads=1."""
import os, sys
os.environ.setdefault("BQ_LOCAL_CACHE", "data/bq_cache")
os.chdir("/home/trido/thanhdt/WorkingClaude"); sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
import numpy as np, pandas as pd
from bq_local_cache import get_cache
lc = get_cache()

v = lc.query("""SELECT t.time, MAX(t.VNINDEX) vni, MAX(t.VNINDEX_PE) pe
FROM tav2_bq.ticker t WHERE t.time>=DATE '2013-01-01' AND t.VNINDEX IS NOT NULL
GROUP BY t.time ORDER BY t.time""")
v["time"] = pd.to_datetime(v["time"]); v = v.sort_values("time").reset_index(drop=True)
v["pe_pct5y"] = v["pe"].rolling(1250, min_periods=250).apply(lambda s: (s.iloc[-1] >= s).mean())
pb = lc.query("""SELECT t.time, APPROX_QUANTILES((t.PB-t.PB_MA5Y)/NULLIF(t.PB_SD5Y,0),2)[OFFSET(1)] pbz_med
FROM tav2_bq.ticker_prune t WHERE t.time>=DATE '2013-01-01' AND t.PB_SD5Y>0 GROUP BY t.time""")
pb["time"] = pd.to_datetime(pb["time"]); v = v.merge(pb, on="time", how="left")
st = lc.query("SELECT s.time, s.state FROM tav2_bq.vnindex_5state_dt5g_live s")
st["time"] = pd.to_datetime(st["time"]); v = v.merge(st, on="time", how="left")

# capitulation proxy (causal): VNINDEX 20-day return <= -10% (sharp panic velocity). A light
# stand-in for the harness's per-name A&C-confirm vol-spike — enough to test the valuation gates.
v["ret20"] = v["vni"]/v["vni"].shift(20) - 1
def fwd(i, h=126):
    j = min(i+h, len(v)-1); return v["vni"].iloc[j]/v["vni"].iloc[i]-1 if v["vni"].iloc[i]>0 else np.nan
v["fwd6M"] = [fwd(i) for i in range(len(v))]
GOOD_TROUGHS = ["2020-03-24","2022-11-15","2023-10-31","2025-04-08"]   # the +>=20% rebounds
DUD_TROUGHS  = ["2018-07-11","2019-01-03"]                              # cheap-ish by pbz but low payoff

gates = {
 "G0 current (state{1,2} & pbz<=-.5)":      (v["state"].isin([1,2])) & (v["pbz_med"]<=-0.5),
 "G1 state-blind pbz<=-.5":                  (v["pbz_med"]<=-0.5),
 "G2 state-blind pbz<=-.5 & PE_pct<=.20":    (v["pbz_med"]<=-0.5) & (v["pe_pct5y"]<=0.20),
 "G2b stricter pbz<=-.5 & PE_pct<=.10":      (v["pbz_med"]<=-0.5) & (v["pe_pct5y"]<=0.10),
 "G3 PE_pct<=.20 only":                      (v["pe_pct5y"]<=0.20),
 "G4 +capit: pbz<=-.5 & PE_pct<=.20 & ret20<=-10%": (v["pbz_med"]<=-0.5)&(v["pe_pct5y"]<=0.20)&(v["ret20"]<=-0.10),
}

def covers(mask, dates, win=25):
    idx = [v.index[v["time"]==pd.Timestamp(d)][0] for d in dates if (v["time"]==pd.Timestamp(d)).any()]
    return sum(any(mask.iloc[max(0,i-win):i+win+1]) for i in idx)

print(f"{'gate':<48} {'fires':>5} {'fwd6M_mean':>10} {'fwd6M_med':>9} {'%>0':>5} {'good/4':>6} {'dud/2':>5}")
for name, m in gates.items():
    m = m.fillna(False)
    f = v[m & v["fwd6M"].notna()]
    n = int(m.sum())
    mean = f["fwd6M"].mean()*100 if len(f) else float("nan")
    med  = f["fwd6M"].median()*100 if len(f) else float("nan")
    pos  = (f["fwd6M"]>0).mean()*100 if len(f) else float("nan")
    print(f"{name:<48} {n:>5} {mean:>9.1f}% {med:>8.1f}% {pos:>4.0f}% "
          f"{covers(m,GOOD_TROUGHS):>5}/4 {covers(m,DUD_TROUGHS):>4}/2")

print("\nREAD: want HIGH fwd6M_mean + covers good 4/4 + covers dud 0/2 + not too many fires (no over-fire).")
print("If G2/G4 catches the 2025 good trough while skipping 2018/2019 duds, the user's PE_pctile+pbz")
print("discriminator works state-blind -> escalate to the full pt_v23 harness with real A&C capitulation.")
# explicit: does each gate fire on 2025-04 and on 2018/2019?
for d in ["2018-07-11","2019-01-03","2025-04-08"]:
    i = v.index[v["time"]==pd.Timestamp(d)]
    if len(i):
        i=i[0]; row=v.iloc[i]
        print(f"  {d}: pbz={row.pbz_med:+.2f} PE_pct={row.pe_pct5y:.2f} state={row.state:.0f} ret20={row.ret20*100:+.0f}% "
              f"=> G1 {'Y' if row.pbz_med<=-0.5 else 'n'} | G2 {'Y' if (row.pbz_med<=-0.5 and row.pe_pct5y<=0.20) else 'n'} "
              f"| G4 {'Y' if (row.pbz_med<=-0.5 and row.pe_pct5y<=0.20 and row.ret20<=-0.10) else 'n'}")
