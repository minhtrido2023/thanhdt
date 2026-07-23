# -*- coding: utf-8 -*-
"""
Adaptive persistence gate — state-level analysis (metrics a & b).
Job Taylor_20260723_054325. Offline, reproducible from base_state.csv + vnindex.csv.

Baseline = production DT 4-gate (macro_state_live._dt_4gate, default=10).
Adaptive = shorten dwell for DE-RISK moves (ps<committed, i.e. more defensive) when
           VNINDEX has fallen K2 consecutive sessions AND base has persisted >=K1.
Ordering: 1=CRISIS 2=BEAR 3=NEUTRAL 4=BULL 5=EXBULL. Lower = more defensive.
"""
import numpy as np, pandas as pd, itertools, sys

HERE = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/adaptive_gate_20260723/"
bs = pd.read_csv(HERE+"base_state.csv", parse_dates=["time"])
vn = pd.read_csv(HERE+"vnindex.csv", parse_dates=["time"])
df = vn.merge(bs, on="time", how="inner").sort_values("time").reset_index(drop=True)
# restrict to the live era 2014+ (production warmup floor)
df = df[df["time"] >= "2014-01-01"].reset_index(drop=True)
states = df["state"].values.astype(int)
close  = df["Close"].values.astype(float)
time   = df["time"].values
N = len(df)
print(f"rows={N}  {df['time'].iloc[0].date()} -> {df['time'].iloc[-1].date()}")


# ---- production DT 4-gate (verbatim from macro_state_live.py) ----
def dt_4gate(states, default=10, enC=25, exC=10, enX=25, exX=10):
    out = states.copy(); committed = states[0]; ps, pr = states[0], 1
    for t in range(1, len(states)):
        s = states[t]
        if s == ps: pr += 1
        else: ps, pr = s, 1
        if ps == committed:
            out[t] = committed; continue
        need = (enC if ps == 1 else enX if ps == 5
                else exC if committed == 1 else exX if committed == 5 else default)
        if pr >= need: committed = ps
        out[t] = committed
    return out


def consec_down(close):
    n = len(close); cd = np.zeros(n, int)
    for t in range(1, n):
        cd[t] = cd[t-1]+1 if close[t] < close[t-1] else 0
    return cd


def dt_4gate_adaptive(states, close, default=10, enC=25, exC=10, enX=25, exX=10,
                      K1=3, K2=3, adapt_enC=False, K1c=10):
    cd = consec_down(close)
    out = states.copy(); committed = states[0]; ps, pr = states[0], 1
    for t in range(1, len(states)):
        s = states[t]
        if s == ps: pr += 1
        else: ps, pr = s, 1
        if ps == committed:
            out[t] = committed; continue
        need = (enC if ps == 1 else enX if ps == 5
                else exC if committed == 1 else exX if committed == 5 else default)
        is_derisk = ps < committed          # getting MORE defensive
        if is_derisk and cd[t] >= K2:
            if ps not in (1, 5):            # default-branch de-risk (BEAR/NEUTRAL/BULL)
                need = min(need, K1)
            elif ps == 1 and adapt_enC:     # into CRISIS (variant B)
                need = min(need, K1c)
        if pr >= need: committed = ps
        out[t] = committed
    return out


def transitions(series):
    """list of (idx, from, to) where committed state changes."""
    out = []
    for t in range(1, len(series)):
        if series[t] != series[t-1]:
            out.append((t, int(series[t-1]), int(series[t])))
    return out


def whipsaw_stats(series, revert_win=(10, 20)):
    """For each DE-RISK transition (to a more defensive state), does the committed state
       revert BACK UP within W sessions? A quick revert = the de-risk was a false alarm."""
    trs = transitions(series)
    derisk = [(t, a, b) for (t, a, b) in trs if b < a]
    res = {}
    for W in revert_win:
        rev = 0
        for (t, a, b) in derisk:
            seg = series[t:min(t+W+1, len(series))]
            if (seg > b).any():   # went back up above the de-risked level within W
                rev += 1
        res[W] = (len(derisk), rev)
    return res, derisk


def drawdown_episodes(close, thr=0.15):
    """peak-to-trough episodes with drop >= thr. Returns list of (peak_idx, trough_idx, depth)."""
    eps = []
    peak = close[0]; peak_i = 0; i = 0; n = len(close)
    in_ep = False; trough = close[0]; trough_i = 0
    # simple: scan running peak; when drop from peak >= thr, mark episode until new peak recovered
    running_peak = close[0]; running_peak_i = 0
    t = 0
    while t < n:
        if close[t] > running_peak:
            running_peak = close[t]; running_peak_i = t
        dd = close[t]/running_peak - 1
        if dd <= -thr:
            # find trough until price recovers back to running_peak
            tr_i = t; tr_v = close[t]
            j = t
            while j < n and close[j] < running_peak:
                if close[j] < tr_v: tr_v = close[j]; tr_i = j
                j += 1
            eps.append((running_peak_i, tr_i, tr_v/close[running_peak_i]-1))
            # resume after recovery
            running_peak = close[j] if j < n else running_peak
            running_peak_i = j if j < n else running_peak_i
            t = j
        else:
            t += 1
    return eps


# ================= build baseline + adaptive series =================
base = dt_4gate(states)
print(f"\nBASELINE default=10: {len(transitions(base))} transitions")

# pre-registered grid (N=10)
grid = []
for K1, K2 in itertools.product([3,5],[2,3,4,5]):
    grid.append(dict(K1=K1,K2=K2,adapt_enC=False,K1c=10,tag=f"F1_K1{K1}_K2{K2}"))
grid.append(dict(K1=3,K2=3,adapt_enC=True,K1c=10,tag="F2_K1c10_K2_3"))
grid.append(dict(K1=3,K2=4,adapt_enC=True,K1c=15,tag="F2_K1c15_K2_4"))
assert len(grid)==10, len(grid)

# episodes (real downtrends >=15%) and the two declared non-DD "false-alarm" windows
eps = drawdown_episodes(close, 0.15)
def d(i): return pd.Timestamp(time[i]).date()
print("\nReal >=15% DD episodes:")
for (p,tr,dep) in eps:
    print(f"  peak {d(p)} -> trough {d(tr)}  depth {dep*100:.1f}%")

# baseline whipsaw
bw, bderisk = whipsaw_stats(base)
print(f"\nBASELINE de-risk transitions={bw[10][0]}  revert<=10d={bw[10][1]}  revert<=20d={bw[20][1]}")

print("\n%-16s %5s %7s %7s %7s %7s" % ("config","trans","derisk","rev10","rev20","Δtrans"))
print("%-16s %5d %7d %7d %7d %7s" % ("BASELINE_def10", len(transitions(base)), bw[10][0], bw[10][1], bw[20][1], "-"))

results = {}
for g in grid:
    adp = dt_4gate_adaptive(states, close, K1=g["K1"], K2=g["K2"],
                            adapt_enC=g["adapt_enC"], K1c=g["K1c"])
    aw, aderisk = whipsaw_stats(adp)
    ntr = len(transitions(adp))
    results[g["tag"]] = adp
    print("%-16s %5d %7d %7d %7d %+7d" % (g["tag"], ntr, aw[10][0], aw[10][1], aw[20][1],
                                          ntr-len(transitions(base))))

# ============ metric b: lead-time to reach defensive state in real DD episodes ============
def defensive_lead(series_base, series_adp, eps, defensive_max=2):
    """For each real DD episode, first session (from peak) each series commits to state<=defensive_max (BEAR/CRISIS).
       Positive lead = adaptive reaches it earlier (fewer sessions after peak)."""
    rows=[]
    for (p,tr,dep) in eps:
        def first_def(series):
            for t in range(p, min(tr+1,len(series))):
                if series[t] <= defensive_max: return t
            return None
        fb=first_def(series_base); fa=first_def(series_adp)
        rows.append((d(p),d(tr),dep, fb, fa,
                     (None if (fb is None or fa is None) else fb-fa)))
    return rows

print("\n===== metric b: lead to state<=BEAR(2), PRIMARY F1_K1_3_K2_3 =====")
prim = results["F1_K13_K23"]
print("%-12s %-12s %6s %8s %8s %6s" % ("peak","trough","depth%","base_i","adp_i","lead"))
for (pp,tt,dep,fb,fa,lead) in defensive_lead(base, prim, eps):
    fbd = d(fb) if fb is not None else "never"
    fad = d(fa) if fa is not None else "never"
    print("%-12s %-12s %6.1f %8s %8s %6s" % (str(pp),str(tt),dep*100,str(fbd),str(fad),
          "" if lead is None else f"{lead:+d}"))

# false de-risk check: does adaptive ADD de-risk commits in calm windows (2014-09, 2026-01)?
def in_win(t, a, b): return (pd.Timestamp(a) <= pd.Timestamp(time[t]) <= pd.Timestamp(b))
for (lo,hi,name) in [("2014-08-01","2015-02-28","2014-H2"),
                     ("2025-12-01","2026-02-28","2026-early")]:
    bd = sum(1 for (t,a,b) in transitions(base) if b<a and in_win(t,lo,hi))
    ad = sum(1 for (t,a,b) in transitions(prim) if b<a and in_win(t,lo,hi))
    print(f"  false-alarm window {name}: baseline de-risk commits={bd}  adaptive={ad}")

# dump primary + baseline series for downstream harness feed
outdf = df[["time"]].copy()
outdf["state_base_dt4"]=base
outdf["state_adp_primary"]=prim
outdf.to_csv(HERE+"state_series_out.csv", index=False)
print("\nwrote state_series_out.csv")
