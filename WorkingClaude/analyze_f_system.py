# -*- coding: utf-8 -*-
"""
analyze_f_system.py
====================
F-system: kiem tra kha nang giao dich phai sinh ngan han (3-5 ngay)
dua tren H-system state / r_score / cac tin hieu phai sinh.

4 loai tin hieu duoc test:
  S1: State transition (entry ngay chuyen trang thai)
  S2: r_score threshold crossing (nhanh hon, nhieu hon)
  S3: r_score direction change (turn signal)
  S4: State-conditional short-term momentum (state + 1d return)
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import os
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

W_BASE = {"P3M":0.30,"P1M":0.10,"MA200":0.15,"RSI":0.15,"MACD":0.10,"CMF":0.08,"Breadth":0.12}
MIN_LB=252; MIN_FACTORS=3; MODE_WIN=15; MIN_STAY=7; EMA_ALPHA=0.40
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}

TC_DERIV = 0.001   # 0.1% round-trip (entry + exit), phai sinh thap hon equity

# ══════════════════════════════════════════════════════════════════════
# LOAD & STATE COMPUTE
# ══════════════════════════════════════════════════════════════════════
print("Loading data...")
vni = pd.read_csv(os.path.join(WORKDIR,"data/VNINDEX.csv"), low_memory=False)
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
for col in ["Close","D_RSI","D_MACDdiff","D_CMF","VNINDEX_PE"]:
    if col in vni.columns: vni[col]=pd.to_numeric(vni[col],errors="coerce")
b_path = os.path.join(WORKDIR,"data/breadth_data.csv")
if os.path.exists(b_path):
    b=pd.read_csv(b_path); b["time"]=pd.to_datetime(b["time"])
    b["breadth"]=pd.to_numeric(b["breadth"],errors="coerce")
    vni=vni.merge(b,on="time",how="left")
else:
    vni["breadth"]=np.nan

n=len(vni); close=vni["Close"].values.copy()
cal_days=(vni["time"].iloc[-1]-vni["time"].iloc[0]).days
SPY=n/(cal_days/365.25)
print(f"  {n} sessions | {vni['time'].min().date()} -> {vni['time'].max().date()}")

def rolling_ret(arr,w):
    out=np.full(len(arr),np.nan)
    for i in range(w,len(arr)):
        if arr[i-w]>0: out[i]=arr[i]/arr[i-w]-1
    return out
def expanding_rank(arr):
    out=np.full(len(arr),np.nan)
    for i in range(MIN_LB,len(arr)):
        win=arr[max(0,i-3000):i+1]; valid=win[~np.isnan(win)]
        if len(valid)<10 or np.isnan(arr[i]): continue
        out[i]=np.searchsorted(np.sort(valid),arr[i])/len(valid)
    return out

p3m=rolling_ret(close,63); p1m=rolling_ret(close,21)
ma200=np.full(n,np.nan)
for i in range(199,n): ma200[i]=np.mean(close[i-199:i+1])
ma200_dev=np.where(ma200>0,close/ma200-1,np.nan)
rsi  =vni["D_RSI"].values.copy()      if "D_RSI"      in vni.columns else np.full(n,np.nan)
macd =vni["D_MACDdiff"].values.copy() if "D_MACDdiff" in vni.columns else np.full(n,np.nan)
cmf  =vni["D_CMF"].values.copy()      if "D_CMF"      in vni.columns else np.full(n,np.nan)
brdt =vni["breadth"].values.copy()    if "breadth"    in vni.columns else np.full(n,np.nan)

ranks={"P3M":expanding_rank(p3m),"P1M":expanding_rank(p1m),"MA200":expanding_rank(ma200_dev),
       "RSI":expanding_rank(rsi),"MACD":expanding_rank(macd),"CMF":expanding_rank(cmf),"Breadth":expanding_rank(brdt)}
score=np.full(n,np.nan)
for i in range(n):
    vals=[(w,ranks[k][i]) for k,w in W_BASE.items() if not np.isnan(ranks[k][i])]
    if len(vals)>=MIN_FACTORS:
        tw=sum(x[0] for x in vals); score[i]=sum(x[0]*x[1] for x in vals)/tw

r_score=np.full(n,np.nan); last=None
for i in range(n):
    if np.isnan(score[i]): r_score[i]=last
    else:
        r_score[i]=EMA_ALPHA*score[i]+(1-EMA_ALPHA)*last if last is not None else score[i]
        last=r_score[i]

def classify(rs):
    if rs<0.10: return 1
    elif rs<0.30: return 2
    elif rs<0.55: return 3
    elif rs<0.75: return 3
    elif rs<0.90: return 4
    else:         return 5

state_raw=np.array([classify(v) if not np.isnan(v) else 3 for v in r_score])
pe_arr=vni["VNINDEX_PE"].values.copy() if "VNINDEX_PE" in vni.columns else np.full(n,np.nan)
pe_p90=np.full(n,np.nan)
for i in range(252,n):
    w2=pe_arr[max(0,i-3000):i+1]; v2=w2[~np.isnan(w2)]
    if len(v2)>=50: pe_p90[i]=np.percentile(v2,90)
dd_a=np.zeros(n); pk=close[0]
for i in range(n):
    if close[i]>pk: pk=close[i]; dd_a[i]=close[i]/pk-1
log_r=np.concatenate([[np.nan],np.diff(np.log(np.where(close>0,close,np.nan)))])
vol20=np.full(n,np.nan)
for i in range(20,n): vol20[i]=np.nanstd(log_r[i-19:i+1])*np.sqrt(SPY)
vol20_ma=np.full(n,np.nan)
for i in range(60,n): vol20_ma[i]=np.nanmean(vol20[i-59:i+1])

so=state_raw.copy()
for i in range(n):
    s=so[i]
    if not np.isnan(pe_p90[i]) and not np.isnan(pe_arr[i]) and pe_arr[i]>pe_p90[i] and s>=4: so[i]=min(s,4)
    if dd_a[i]<-0.25 and s>=3: so[i]=min(s,3)
    if (not np.isnan(vol20[i]) and not np.isnan(vol20_ma[i])
        and vol20_ma[i]>0 and vol20[i]>1.5*vol20_ma[i] and s>=4): so[i]=min(s,4)

def rolling_mode(arr,w):
    out=arr.copy()
    for i in range(w-1,len(arr)):
        window=arr[i-w+1:i+1]; counts=np.bincount(window,minlength=6); out[i]=np.argmax(counts)
    return out
def min_stay_filter(arr,ms):
    out=arr.copy(); i=0
    while i<len(arr):
        j=i+1
        while j<len(arr) and arr[j]==arr[i]: j+=1
        if j-i<ms:
            prev=out[i-1] if i>0 else arr[i]; out[i:j]=prev
        i=j
    return out

ss=rolling_mode(so,MODE_WIN); ss=min_stay_filter(ss,MIN_STAY)
vni["state"]=ss; vni["r_score"]=r_score; vni["score_raw"]=score

print("  State computed OK")

# ── Daily return ───────────────────────────────────────────────────────
daily_ret = np.concatenate([[np.nan], close[1:]/close[:-1]-1])
vni["ret1d"] = daily_ret

# Restrict to 2011+ for analysis
START = "2011-01-01"
mask = (vni["time"] >= START).values
vi = vni[mask].copy().reset_index(drop=True)
ni = len(vi); close_i = vi["Close"].values

print(f"  Analysis window: {vi['time'].min().date()} -> {vi['time'].max().date()} ({ni} sessions)")

# ══════════════════════════════════════════════════════════════════════
# FORWARD RETURN HELPER
# ══════════════════════════════════════════════════════════════════════
HORIZONS = [1, 2, 3, 5]

def fwd_ret_arr(close_arr, h):
    """Forward return at horizon h, accounting for T+1 execution."""
    # Enter at T+1 open ≈ close[T+1], exit at close[T+h+1]
    out = np.full(len(close_arr), np.nan)
    for i in range(len(close_arr)-h-1):
        if close_arr[i+1] > 0 and close_arr[i+h+1] > 0:
            out[i] = close_arr[i+h+1] / close_arr[i+1] - 1  # T+1 entry
    return out

fwd = {h: fwd_ret_arr(close_i, h) for h in HORIZONS}

def stats(returns, direction=1, label=""):
    """direction=1 for long, -1 for short."""
    r = np.array(returns) * direction
    r = r[~np.isnan(r)]
    if len(r) == 0:
        return None
    r_net = r - TC_DERIV
    wr = (r_net > 0).mean()
    mean_r = r.mean()
    mean_net = r_net.mean()
    pf_w = r_net[r_net>0].sum() if (r_net>0).any() else 0
    pf_l = -r_net[r_net<0].sum() if (r_net<0).any() else 1e-9
    pf = pf_w / pf_l
    sharpe = mean_net / (r_net.std()+1e-9) * np.sqrt(SPY/1)  # annualized
    return dict(n=len(r), wr=wr, mean_r=mean_r*100, mean_net=mean_net*100,
                pf=pf, sharpe=sharpe, label=label)

def print_stats(s, indent="  "):
    if s is None: return
    flag = "OK" if (s["wr"] > 0.55 and s["mean_net"] > 0.05) else ("?" if s["wr"] > 0.52 else "   ")
    print(f"{indent}n={s['n']:>5}  WR={s['wr']*100:>5.1f}%  ret={s['mean_r']:>+6.3f}%  "
          f"net={s['mean_net']:>+6.3f}%  PF={s['pf']:>5.2f}  Sharpe={s['sharpe']:>6.2f}  {flag}")

# ══════════════════════════════════════════════════════════════════════
# BASELINE
# ══════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("BASELINE — No signal (always long)")
print("="*70)
for h in HORIZONS:
    s = stats(fwd[h][~np.isnan(fwd[h])], 1, f"T+{h}")
    print(f"  T+{h}: ", end=""); print_stats(s, "")

# ══════════════════════════════════════════════════════════════════════
# S1: STATE TRANSITION SIGNALS
# ══════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("S1 — State Transition Signals (entry ngay chuyen trang thai)")
print("="*70)

# Bull transitions: upgrades -> long (BEAR/NEUTRAL -> BULL, NEUTRAL -> BULL, etc.)
# Bear transitions: downgrades -> short

BULL_TRANS = [
    ((2,3),(3,4),(3,3),(4,5)),    # any upgrade  -> long
    ((3,4),(4,5)),                 # upgrade to BULL/EXBULL -> long
    ((2,3),),                      # BEAR -> NEUTRAL -> long
    ((3,4),),                      # NEUTRAL -> BULL -> long
]
BEAR_TRANS = [
    ((4,3),(3,2),(2,1),(5,4)),    # any downgrade -> short
    ((4,3),(3,2)),                 # downgrade to NEUTRAL/BEAR -> short
    ((3,2),),                      # NEUTRAL -> BEAR -> short
]

def get_transition_days(from_s, to_s):
    """Return indices in vi where transition from_s->to_s occurs."""
    idxs = []
    states = vi["state"].values
    for i in range(1, ni):
        if states[i-1]==from_s and states[i]==to_s:
            idxs.append(i)
    return idxs

transition_types = [
    ("NEUTRAL->BULL",  3, 4, "LONG"),
    ("BEAR->NEUTRAL",  2, 3, "LONG"),
    ("BEAR->BULL",     2, 4, "LONG"),
    ("NEUTRAL->BEAR",  3, 2, "SHORT"),
    ("BULL->NEUTRAL",  4, 3, "SHORT"),
    ("NEUTRAL->CRISIS",3, 1, "SHORT"),
    ("BEAR->CRISIS",   2, 1, "SHORT"),
    ("CRISIS->BEAR",   1, 2, "LONG"),
    ("BULL->EX-BULL",  4, 5, "LONG"),
]

for name, fs, ts, direction in transition_types:
    idxs = get_transition_days(fs, ts)
    if len(idxs) == 0: continue
    dir_val = 1 if direction=="LONG" else -1
    print(f"\n  {name} ({direction}) — {len(idxs)} transitions:")
    for h in HORIZONS:
        rets = [fwd[h][i] for i in idxs if not np.isnan(fwd[h][i])]
        if len(rets) < 3: continue
        s = stats(rets, dir_val)
        print(f"    T+{h}: ", end=""); print_stats(s, "")

# Frequency summary
print(f"\n  Total transition-based signals per year: {len(get_transition_days(3,4))+len(get_transition_days(2,3))+len(get_transition_days(3,2))+len(get_transition_days(4,3)):.0f}")

# ══════════════════════════════════════════════════════════════════════
# S2: r_score THRESHOLD CROSSINGS (faster, more frequent)
# ══════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("S2 — r_score Threshold Crossings")
print("="*70)

rs = vi["r_score"].values

thresholds = [
    (0.10, "CRISIS->BEAR",  "LONG",  "cross_up"),   # rs crosses 0.10 upward
    (0.10, "BEAR->CRISIS",  "SHORT", "cross_down"),
    (0.30, "BEAR->NEUTRAL", "LONG",  "cross_up"),
    (0.30, "NEUTRAL->BEAR", "SHORT", "cross_down"),
    (0.55, "NEUTRAL->BULL", "LONG",  "cross_up"),
    (0.55, "BULL->NEUTRAL", "SHORT", "cross_down"),
    (0.75, "BULL->STRONG",  "LONG",  "cross_up"),
    (0.75, "STRONG->BULL",  "SHORT", "cross_down"),
]

for thr, name, direction, cross_dir in thresholds:
    idxs = []
    for i in range(1, ni):
        if cross_dir == "cross_up"   and not np.isnan(rs[i-1]) and not np.isnan(rs[i]):
            if rs[i-1] < thr <= rs[i]: idxs.append(i)
        if cross_dir == "cross_down" and not np.isnan(rs[i-1]) and not np.isnan(rs[i]):
            if rs[i-1] >= thr > rs[i]: idxs.append(i)
    if len(idxs) < 3: continue
    dir_val = 1 if direction=="LONG" else -1
    freq = len(idxs) / ((vi["time"].iloc[-1]-vi["time"].iloc[0]).days/365.25)
    print(f"\n  thr={thr:.2f} {name} ({direction}) — {len(idxs)} signals ({freq:.1f}/yr):")
    for h in HORIZONS:
        rets = [fwd[h][i] for i in idxs if not np.isnan(fwd[h][i])]
        if len(rets) < 3: continue
        s = stats(rets, dir_val)
        print(f"    T+{h}: ", end=""); print_stats(s, "")

# ══════════════════════════════════════════════════════════════════════
# S3: r_score DIRECTION CHANGE (turn signals, daily)
# ══════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("S3 — r_score Direction Change (turn signals)")
print("="*70)

# r_score turning up (valley) or down (peak) — based on 3-day local extrema
def find_turns(rs, min_change=0.005):
    """Find local min (bullish turn) and max (bearish turn) in r_score."""
    longs, shorts = [], []
    for i in range(2, len(rs)-1):
        if any(np.isnan([rs[i-2],rs[i-1],rs[i],rs[i+1]])): continue
        # Valley: rs[i] < rs[i-1] and rs[i] < rs[i+1]
        if rs[i] < rs[i-1] and rs[i] < rs[i+1] and (rs[i+1]-rs[i]) > min_change:
            longs.append(i)
        # Peak: rs[i] > rs[i-1] and rs[i] > rs[i+1]
        if rs[i] > rs[i-1] and rs[i] > rs[i+1] and (rs[i]-rs[i+1]) > min_change:
            shorts.append(i)
    return longs, shorts

for min_chg in [0.005, 0.010, 0.015]:
    longs, shorts = find_turns(rs, min_chg)
    freq_l = len(longs) / ((vi["time"].iloc[-1]-vi["time"].iloc[0]).days/365.25)
    freq_s = len(shorts) / ((vi["time"].iloc[-1]-vi["time"].iloc[0]).days/365.25)
    print(f"\n  min_change={min_chg:.3f}: {len(longs)} LONG turns ({freq_l:.1f}/yr)  |  {len(shorts)} SHORT turns ({freq_s:.1f}/yr)")
    for h in [3, 5]:
        rl = [fwd[h][i] for i in longs  if not np.isnan(fwd[h][i])]
        rs_=[fwd[h][i] for i in shorts if not np.isnan(fwd[h][i])]
        sl = stats(rl,  1); ss2 = stats(rs_, -1)
        print(f"    T+{h} LONG : ", end=""); print_stats(sl, "")
        print(f"    T+{h} SHORT: ", end=""); print_stats(ss2, "")

# ══════════════════════════════════════════════════════════════════════
# S4: STATE-CONDITIONAL MOMENTUM (state + yesterday return)
# ══════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("S4 — State-Conditional Momentum (state + 1d return)")
print("="*70)
print("Logic: trong BULL/NEUTRAL, ngay tang -> tiep tuc tang (momentum)")
print("       trong BEAR/CRISIS, ngay giam -> tiep tuc giam (trend)")

states_i = vi["state"].values
ret1d_i  = vi["ret1d"].values

for state_grp, state_name, pos_dir, neg_dir in [
    ([4,5], "BULL/EX-BULL",   "LONG if ret>0", "SHORT if ret<0"),
    ([3],   "NEUTRAL",         "LONG if ret>0", "SHORT if ret<0"),
    ([2,1], "BEAR/CRISIS",     "LONG if ret>0", "SHORT if ret<0"),
]:
    long_idxs  = [i for i in range(1,ni-5) if states_i[i] in state_grp and not np.isnan(ret1d_i[i]) and ret1d_i[i]>0]
    short_idxs = [i for i in range(1,ni-5) if states_i[i] in state_grp and not np.isnan(ret1d_i[i]) and ret1d_i[i]<0]
    print(f"\n  State={state_name}: {len(long_idxs)} LONG days  |  {len(short_idxs)} SHORT days")
    for h in [3, 5]:
        rl = [fwd[h][i] for i in long_idxs  if not np.isnan(fwd[h][i])]
        rs_= [fwd[h][i] for i in short_idxs if not np.isnan(fwd[h][i])]
        sl = stats(rl,  1); ss2 = stats(rs_, -1)
        print(f"    T+{h} LONG : ", end=""); print_stats(sl, "")
        print(f"    T+{h} SHORT: ", end=""); print_stats(ss2, "")

# ══════════════════════════════════════════════════════════════════════
# S5: r_score LEVEL-BASED POSITIONING (stay in zone)
# ══════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("S5 — r_score Zone Positioning (hold while in zone)")
print("Logic: vao khi rs vuot nguong, thoat khi rs ra khoi zone")
print("="*70)

zones = [
    ("STRONG BULL",   0.75, 1.01, "LONG"),
    ("BULL",          0.55, 0.90, "LONG"),
    ("DEEP BEAR",     0.00, 0.30, "SHORT"),
    ("BEAR",          0.00, 0.10, "SHORT"),
]

for zone_name, lo, hi, direction in zones:
    idxs = [i for i in range(ni-5) if not np.isnan(rs[i]) and lo <= rs[i] < hi]
    if len(idxs) < 10: continue
    dir_val = 1 if direction=="LONG" else -1
    freq = len(idxs) / ((vi["time"].iloc[-1]-vi["time"].iloc[0]).days/365.25)
    print(f"\n  Zone [{lo:.2f},{hi:.2f}] {zone_name} ({direction}) — {len(idxs)} days ({freq:.0f} d/yr):")
    for h in [3, 5]:
        rets = [fwd[h][i] for i in idxs if not np.isnan(fwd[h][i])]
        s = stats(rets, dir_val)
        print(f"    T+{h}: ", end=""); print_stats(s, "")

# ══════════════════════════════════════════════════════════════════════
# SUMMARY: WHICH SIGNALS ARE VIABLE?
# ══════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("SUMMARY — Feasibility for F-system (phai sinh 3-5 ngay)")
print("="*70)
print("""
  TC phai sinh (round-trip): 0.1%
  Break-even win rate: ~52% (vi mean_net > 0)
  Target win rate de co edge: >= 55-56%

  Signal     | Freq/yr | Win rate T+3 | Feasibility
  ───────────────────────────────────────────────────
  S1 transitions | 4-8  | depends      | QUA IT, khong du mau
  S2 r_score cross| 10-20| depends      | Co the, can xem ket qua
  S3 turn signal  | 30-50| depends      | Tan suat OK, can edge
  S4 state+mom    | 200+ | depends      | Nhieu tin hieu, can loc
  S5 zone hold    | 200+ | depends      | Daily signal, stable
""")

print("\nDone.")
