# -*- coding: utf-8 -*-
"""
vnindex_5state_v2g_full.py
==========================
Run v2g winner + baseline on FULL data (2000-2026) pulled from BigQuery.
Then quarterly walk-forward (QWF) snapshots.

v2g config:
  - No smoothing (mode_win=1, min_stay=1)
  - BearDvg gate: floor=CRISIS(0%), min_dur=30 phiên
  - Exit gate: BullDvg OR Capitulation bounce (dd<-15% + close/close[5d]>1.05 + rsi rise + cmf>0)
  - NO E3/E4 (r_score recovery / MACD oversold cross) — they hurt CAGR
"""
import sys, io, os, subprocess, tempfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np
import pandas as pd
from io import StringIO

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
BQ = r"bq"
PROJECT = "lithe-record-440915-m9"

def bq(sql):
    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); path = f.name
    try:
        cmd = (f'"{BQ}" query --use_legacy_sql=false --project_id={PROJECT} '
               f'--format=csv --max_rows=200000 < "{path}"')
        out = subprocess.run(cmd, capture_output=True, text=True, check=True, shell=True)
    finally:
        os.unlink(path)
    txt = out.stdout.strip()
    if not txt:
        return pd.DataFrame()
    try:
        return pd.read_csv(StringIO(out.stdout))
    except pd.errors.EmptyDataError:
        return pd.DataFrame()

# ════════════════════ PARAMS ════════════════════
W_BASE = {"P3M":0.30, "P1M":0.10, "MA200":0.15, "RSI":0.15, "MACD":0.10, "CMF":0.08, "Breadth":0.12}
MIN_LB, MIN_FACTORS, EMA_ALPHA = 252, 3, 0.40
RAMP_DAYS, SNAP_THR = 3, 0.03
TC, DEPOSIT_R, BORROW_R = 0.001, 0.06/252, 0.10/252
TARGET_W = {1:0.00, 2:0.20, 3:0.70, 4:1.00, 5:1.30}
STATE_NAMES = {1:"CRISIS", 2:"BEAR", 3:"NEUTRAL", 4:"BULL", 5:"EX-BULL"}

# ════════════════════ LOAD FROM BQ ════════════════════
cache_path = os.path.join(WORKDIR, "data/vnindex_full_2000_2026.csv")
if os.path.exists(cache_path):
    print(f"Loading cached {cache_path} ...")
    vni = pd.read_csv(cache_path)
    vni["time"] = pd.to_datetime(vni["time"])
else:
    print("Pulling VNINDEX OHLCV+PE from BQ (2000-2026) ...")
    vni = bq("""
    SELECT t.time, t.Open, t.High, t.Low, t.Close, t.Volume, t.VNINDEX_PE
    FROM tav2_bq.ticker AS t
    WHERE t.ticker = "VNINDEX"
    ORDER BY t.time
    """)
    vni["time"] = pd.to_datetime(vni["time"])
    # Append rolling 1m for latest
    print("Appending ticker_1m for latest ...")
    last_t = vni["time"].max()
    add = bq(f"""
    SELECT t.time, t.Open, t.High, t.Low, t.Close, t.Volume, t.VNINDEX_PE
    FROM tav2_bq.ticker_1m AS t
    WHERE t.ticker = "VNINDEX" AND t.time > "{last_t.strftime('%Y-%m-%d')}"
    ORDER BY t.time
    """)
    if len(add) > 0:
        add["time"] = pd.to_datetime(add["time"])
        vni = pd.concat([vni, add], ignore_index=True).drop_duplicates("time").sort_values("time").reset_index(drop=True)

    print("Pulling breadth (% tickers above MA50) ...")
    # breadth from BQ: per day, count of tickers with Close > MA50 / total
    br = bq("""
    SELECT t.time,
           SAFE_DIVIDE(SUM(CASE WHEN t.Close > t.MA50 THEN 1 ELSE 0 END), COUNT(*)) AS breadth
    FROM tav2_bq.ticker AS t
    WHERE t.MA50 IS NOT NULL AND t.Close IS NOT NULL
    GROUP BY t.time
    ORDER BY t.time
    """)
    br["time"] = pd.to_datetime(br["time"])
    vni = vni.merge(br, on="time", how="left")
    vni.to_csv(cache_path, index=False)
    print(f"Cached → {cache_path}  ({len(vni)} rows)")

# Sanitize numeric + clamp outliers
for c in ["Open","High","Low","Close","Volume","VNINDEX_PE","breadth"]:
    if c in vni.columns:
        vni[c] = pd.to_numeric(vni[c], errors="coerce")
for col in ["Close","Open","High","Low"]:
    a = vni[col].values.astype(float)
    for i in range(1, len(a)):
        if a[i-1] > 0 and a[i] > 0:
            if abs(a[i]/a[i-1] - 1) > 0.5:
                a[i] = a[i-1]
    vni[col] = a

vni = vni.sort_values("time").reset_index(drop=True)
n = len(vni)
print(f"  rows={n}  {vni['time'].iloc[0].date()} → {vni['time'].iloc[-1].date()}")
cal_days = (vni["time"].iloc[-1] - vni["time"].iloc[0]).days
spy = n/(cal_days/365.25) if cal_days>0 else 252
print(f"  sessions/year = {spy:.1f}")

close = vni["Close"].values.astype(float)
high  = vni["High"].values.astype(float)
low   = vni["Low"].values.astype(float)
vol_  = vni["Volume"].values.astype(float)
pe    = vni["VNINDEX_PE"].values.astype(float)
breadth_arr = vni["breadth"].values.astype(float) if "breadth" in vni.columns else np.full(n, np.nan)

# ════════════════════ INDICATORS ════════════════════
print("Computing indicators ...")
p3m = np.full(n, np.nan); p1m = np.full(n, np.nan)
for i in range(60, n):
    if close[i-60] > 0: p3m[i] = close[i]/close[i-60] - 1
for i in range(20, n):
    if close[i-20] > 0: p1m[i] = close[i]/close[i-20] - 1
ma200 = pd.Series(close).rolling(200, min_periods=200).mean().values
ma200_dev = np.where((ma200>0)&~np.isnan(ma200), close/ma200-1, np.nan)

# RSI
rsi = np.full(n, np.nan); avg_u = avg_d = np.nan; period = 14
for i in range(1, n):
    diff = close[i]-close[i-1]; u = max(diff,0); d = max(-diff,0)
    if np.isnan(avg_u):
        if i >= period:
            g = [max(close[j]-close[j-1],0) for j in range(1,period+1)]
            l = [max(close[j-1]-close[j],0) for j in range(1,period+1)]
            avg_u = np.mean(g); avg_d = np.mean(l)
            if (avg_u+avg_d)>0: rsi[i] = avg_u/(avg_u+avg_d)
    else:
        avg_u = (avg_u*(period-1)+u)/period
        avg_d = (avg_d*(period-1)+d)/period
        if (avg_u+avg_d)>0: rsi[i] = avg_u/(avg_u+avg_d)

# MACD
ema12 = np.full(n,np.nan); ema26 = np.full(n,np.nan); signal = np.full(n,np.nan); macd_hist = np.full(n,np.nan)
k12,k26,k9 = 2/13, 2/27, 2/10
for i in range(n):
    if i==0 or np.isnan(ema12[i-1]):
        ema12[i]=close[i]; ema26[i]=close[i]
    else:
        ema12[i] = ema12[i-1]*(1-k12) + close[i]*k12
        ema26[i] = ema26[i-1]*(1-k26) + close[i]*k26
    macd_line = ema12[i]-ema26[i]
    if i==0 or np.isnan(signal[i-1]): signal[i]=macd_line
    else: signal[i] = signal[i-1]*(1-k9) + macd_line*k9
    if i>=33: macd_hist[i] = macd_line - signal[i]

# CMF
hl = high - low
mfm = np.where(hl>0, ((close-low)-(high-close))/np.where(hl>0,hl,1), 0)
mfv = mfm * vol_
cmf = np.full(n, np.nan)
for i in range(14, n):
    s_v = np.sum(vol_[i-14:i])
    if s_v>0: cmf[i] = np.sum(mfv[i-14:i])/s_v

vni["f_P3M"]=p3m; vni["f_P1M"]=p1m; vni["f_MA200"]=ma200_dev
vni["f_RSI"]=rsi; vni["f_MACD"]=macd_hist; vni["f_CMF"]=cmf; vni["f_Breadth"]=breadth_arr

def expanding_pct_rank(arr, min_lb=252):
    out = np.full(len(arr), np.nan)
    for t in range(len(arr)):
        h = arr[:t+1]; v = h[~np.isnan(h)]
        if len(v)<min_lb or np.isnan(arr[t]): continue
        out[t] = np.sum(v <= arr[t])/len(v)
    return out

FK = ["P3M","P1M","MA200","RSI","MACD","CMF","Breadth"]
print("Computing ranks ...")
ranks = {}
for k in FK:
    ranks[k] = expanding_pct_rank(vni[f"f_{k}"].values, MIN_LB)

score = np.full(n, np.nan)
for t in range(n):
    avail = {k: ranks[k][t] for k in FK if not np.isnan(ranks[k][t])}
    if len(avail)<MIN_FACTORS: continue
    ws = sum(W_BASE[k] for k in avail)
    score[t] = sum(avail[k]*W_BASE[k] for k in avail)/ws
r_score = expanding_pct_rank(score, MIN_LB)
r_score_ema = np.full(n, np.nan)
for t in range(n):
    v = r_score[t]; prev = r_score_ema[t-1] if t>0 else np.nan
    if np.isnan(v): r_score_ema[t]=prev
    elif np.isnan(prev): r_score_ema[t]=v
    else: r_score_ema[t] = EMA_ALPHA*v + (1-EMA_ALPHA)*prev

def classify_raw(rs):
    if np.isnan(rs): return 3
    if rs<0.10: return 1
    if rs<0.20: return 2
    if rs<0.70: return 3
    if rs<0.90: return 4
    return 5
state_raw = np.array([classify_raw(r) for r in r_score_ema])

# Risk overrides
print("Computing risk overrides ...")
pe_p90 = np.full(n, np.nan)
for t in range(n):
    v = pe[:t+1]; v = v[~np.isnan(v)]
    if len(v)>=60: pe_p90[t] = np.nanpercentile(v, 90)
running_max = np.maximum.accumulate(np.where(np.isnan(close), 0, close))
dd = np.where(running_max>0, close/running_max-1, 0.0)
daily_ret = np.full(n, np.nan)
for i in range(1,n):
    if close[i-1]>0: daily_ret[i] = close[i]/close[i-1]-1
vol20 = np.full(n, np.nan)
for i in range(20,n):
    w = daily_ret[i-20:i]; v = w[~np.isnan(w)]
    if len(v)>=15: vol20[i] = np.std(v)*np.sqrt(spy)
avg_vol_exp = np.full(n, np.nan)
for t in range(n):
    h = vol20[:t+1]; v = h[~np.isnan(h)]
    if len(v)>=60: avg_vol_exp[t] = np.mean(v)

state_ov = state_raw.copy()
for i in range(n):
    s = state_ov[i]
    if not np.isnan(pe_p90[i]) and not np.isnan(pe[i]) and pe[i]>pe_p90[i] and s==5: s=4
    if dd[i] < -0.25 and s>=4: s=3
    if not np.isnan(avg_vol_exp[i]) and not np.isnan(vol20[i]) and vol20[i]>1.5*avg_vol_exp[i] and s==5: s=4
    state_ov[i] = s

# ════════════════════ BEAR/BULL DVG ════════════════════
print("Computing BearDvg / BullDvg signals ...")
D_RSI = rsi
def roll_max(a,w): return pd.Series(a).rolling(w, min_periods=1).max().values
def roll_min(a,w): return pd.Series(a).rolling(w, min_periods=1).min().values
def arg_close_max(rsi_a, close_a, w):
    out = np.full(len(rsi_a), np.nan)
    for i in range(len(rsi_a)):
        lo = max(0, i-w+1); seg = rsi_a[lo:i+1]
        if np.all(np.isnan(seg)): continue
        k = int(np.nanargmax(seg)); out[i] = close_a[lo+k]
    return out
def arg_macd_max(rsi_a, macd_a, w):
    out = np.full(len(rsi_a), np.nan)
    for i in range(len(rsi_a)):
        lo = max(0, i-w+1); seg = rsi_a[lo:i+1]
        if np.all(np.isnan(seg)): continue
        k = int(np.nanargmax(seg)); out[i] = macd_a[lo+k]
    return out
def arg_close_min(rsi_a, close_a, w):
    out = np.full(len(rsi_a), np.nan)
    for i in range(len(rsi_a)):
        lo = max(0, i-w+1); seg = rsi_a[lo:i+1]
        if np.all(np.isnan(seg)): continue
        k = int(np.nanargmin(seg)); out[i] = close_a[lo+k]
    return out

D_RSI_T1W     = np.concatenate([[np.nan]*5, D_RSI[:-5]])
D_RSI_Max1W   = roll_max(D_RSI, 5);    D_RSI_Max3M = roll_max(D_RSI, 60)
D_RSI_Min1W   = roll_min(D_RSI, 5);    D_RSI_Min3M = roll_min(D_RSI, 60)
D_RSI_Max1W_C = arg_close_max(D_RSI, close, 5);  D_RSI_Max3M_C = arg_close_max(D_RSI, close, 60)
D_RSI_Max1W_M = arg_macd_max(D_RSI, macd_hist, 5); D_RSI_Max3M_M = arg_macd_max(D_RSI, macd_hist, 60)
D_RSI_Min1W_C = arg_close_min(D_RSI, close, 5)
D_RSI_MinT3   = roll_min(D_RSI, 3)
D_CMF, D_MACDdiff = cmf, macd_hist
C_L1W = close/np.where(roll_min(close,5)>0, roll_min(close,5), 1)
C_L1M = close/np.where(roll_min(close,20)>0, roll_min(close,20), 1)
mask_2011 = (vni["time"]>="2011-01-01").values

with np.errstate(divide='ignore', invalid='ignore'):
    bear1 = ((D_RSI_Max1W/np.where(D_RSI>0,D_RSI,np.nan)>1.044) & (D_RSI_Max3M>0.74) &
             (D_RSI_Max1W<0.72) & (D_RSI_Max1W>0.61) &
             (D_RSI_Max1W_C/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan)>1.028) &
             (D_RSI_Max3M_M/np.where(D_RSI_Max1W_M!=0,D_RSI_Max1W_M,np.nan)>1.11) &
             (D_MACDdiff<0) & (close/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan)>0.96) &
             (D_RSI_MinT3>0.43) & (D_CMF<0.13) & mask_2011)
    bear2 = ((D_RSI_Max1W/np.where(D_RSI>0,D_RSI,np.nan)>1.016) & (D_RSI_Max3M>0.77) &
             (D_RSI_Max1W<0.79) & (D_RSI_Max1W>0.60) &
             (D_RSI_Max1W_C/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan)>1.008) &
             (D_RSI_Max3M_M/np.where(D_RSI_Max1W_M!=0,D_RSI_Max1W_M,np.nan)>1.10) &
             (D_MACDdiff<0) & (close/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan)>0.97) &
             (D_RSI_MinT3>0.50) & (D_CMF<0.15) & mask_2011)
    bull1 = ((D_RSI_Min1W/np.where(D_RSI_Min3M>0,D_RSI_Min3M,np.nan)>0.90) & (D_RSI_Min1W<0.60) &
             (D_RSI_Min3M<0.40) & (D_RSI_Min1W_C/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan)<1.15) &
             (D_MACDdiff>0) & (D_RSI_MinT3<0.50) & (D_RSI_Max1W<0.48) &
             (D_RSI/np.where(D_RSI_T1W>0,D_RSI_T1W,np.nan)>1.12) & (D_CMF>0) &
             (C_L1M<1.21) & (C_L1W<1.05) & mask_2011)
    bull2 = ((D_RSI_Min1W/np.where(D_RSI_Min3M>0,D_RSI_Min3M,np.nan)>0.92) & (D_RSI_Min1W<0.52) &
             (D_RSI_Min3M<0.38) & (D_RSI_Min1W_C/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan)<1.10) &
             (D_MACDdiff>0) & (D_RSI_MinT3<0.56) & (D_RSI_Max1W<0.64) &
             (D_RSI/np.where(D_RSI_T1W>0,D_RSI_T1W,np.nan)>1.10) & (D_CMF>0) &
             (C_L1M<1.20) & (C_L1W<1.025) & mask_2011)

bear_mask = np.nan_to_num(bear1, nan=0).astype(bool) | np.nan_to_num(bear2, nan=0).astype(bool)
bull_mask = np.nan_to_num(bull1, nan=0).astype(bool) | np.nan_to_num(bull2, nan=0).astype(bool)
print(f"  BearDvg events: {bear_mask.sum()} | BullDvg events: {bull_mask.sum()}")

pe_rank = np.full(n, np.nan)
for t in range(n):
    if np.isnan(pe[t]): continue
    v = pe[:t+1]; v = v[~np.isnan(v)]
    if len(v)>=60: pe_rank[t] = np.sum(v<=pe[t])/len(v)
p3m_rank = ranks["P3M"]

# ════════════════════ E2 capitulation signal ════════════════════
E2 = np.zeros(n, dtype=bool)
for i in range(5, n):
    if (dd[i] < -0.15
        and close[i] > close[i-5]*1.05
        and not np.isnan(rsi[i]) and not np.isnan(rsi[i-5])
        and rsi[i] > rsi[i-5]*1.15
        and not np.isnan(cmf[i]) and cmf[i] > 0):
        E2[i] = True
print(f"  E2 capitulation events: {E2.sum()}")

# ════════════════════ V2G GATE + STATE (no smoothing) ════════════════════
print("Building v2g state series ...")
GATE_MIN_V2G = 30
state_v2g = state_ov.copy()
ga = False; gs = -1
gate_events_v2g = []
for i in range(n):
    if bear_mask[i]:
        if not ga:
            ga = True; gs = i
            gate_events_v2g.append({"type":"OPEN","date":vni["time"].iloc[i].strftime("%Y-%m-%d"),"close":float(close[i])})
        else:
            gs = i
    if ga:
        if state_v2g[i] > 1: state_v2g[i] = 1
        sessions_in = i - gs
        if sessions_in >= GATE_MIN_V2G:
            if bull_mask[i] or E2[i]:
                trig = "BullDvg" if bull_mask[i] else "Capitulation"
                gate_events_v2g.append({"type":"CLOSE","date":vni["time"].iloc[i].strftime("%Y-%m-%d"),
                                         "close":float(close[i]),"duration":sessions_in,"trigger":trig})
                ga = False

# ════════════════════ BASELINE STATE (smooth + gate60) ════════════════════
print("Building baseline state series ...")
def rolling_mode(states, window):
    out = states.copy()
    for t in range(window-1, len(states)):
        win = states[t-window+1:t+1]
        vals, counts = np.unique(win, return_counts=True)
        mc = counts.max(); cand = vals[counts==mc]
        for v in reversed(win):
            if v in cand: out[t]=v; break
    return out
def min_stay_filter(states, min_days):
    out = states.copy(); changed = True
    while changed:
        changed = False; i = 0
        while i < len(out):
            j = i+1
            while j<len(out) and out[j]==out[i]: j += 1
            if (j-i) < min_days:
                fill = out[i-1] if i>0 else (out[j] if j<len(out) else out[i])
                out[i:j] = fill; changed = True
            i = j
    return out

_rscore_streak10 = np.zeros(n, dtype=bool); _st=0
for i in range(n):
    if not np.isnan(r_score_ema[i]) and r_score_ema[i]>0.65: _st += 1
    else: _st = 0
    if _st>=10: _rscore_streak10[i] = True

state_b_dvg = state_ov.copy()
ga = False; gs = -1
for i in range(n):
    if bear_mask[i]:
        if not ga: ga=True; gs=i
        else: gs=i
    if ga:
        if state_b_dvg[i]>1: state_b_dvg[i]=1
        sessions_in = i-gs
        if sessions_in >= 60:
            _p3m_ok = (not np.isnan(p3m_rank[i])) and p3m_rank[i]>0.45
            _pe_ok  = (not np.isnan(pe_rank[i]))  and pe_rank[i]<0.80
            _bull_ok = bool(bull_mask[i])
            _rs_ok = bool(_rscore_streak10[i])
            if _bull_ok or (_p3m_ok and _pe_ok) or _rs_ok:
                ga = False
state_baseline = rolling_mode(state_b_dvg, 15)
state_baseline = min_stay_filter(state_baseline, 7)

# ════════════════════ BACKTEST ════════════════════
def backtest(state_arr):
    pv = np.zeros(n); pv[0] = 1e9; w = TARGET_W[3]; wa = np.zeros(n); wa[0]=w
    for t in range(1, n):
        tgt = TARGET_W[state_arr[t-1]]; d_ = tgt - w
        w_new = tgt if abs(d_)<SNAP_THR else w + d_/RAMP_DAYS
        w_new = float(np.clip(w_new, 0, 1.30))
        r = close[t]/close[t-1]-1 if close[t-1]>0 else 0.0
        pv[t] = pv[t-1]*(1 + w_new*r + max(0,1-w_new)*DEPOSIT_R
                          - max(0,w_new-1)*BORROW_R - abs(w_new-w)*TC)
        w = w_new; wa[t] = w
    return pv, wa

print("Backtesting v2g + baseline + B&H ...")
pv_v2g, w_v2g = backtest(state_v2g)
pv_base, w_base = backtest(state_baseline)
pv_bh = np.zeros(n); pv_bh[0] = 1e9
for t in range(1,n):
    pv_bh[t] = pv_bh[t-1]*(close[t]/close[t-1]) if close[t-1]>0 else pv_bh[t-1]

# ════════════════════ METRICS ════════════════════
def metrics(pv, dates, i0=None, i1=None):
    a = np.asarray(pv, float)
    if i0 is None: i0 = 0
    if i1 is None: i1 = len(a)-1
    a = a[i0:i1+1]
    valid = np.where(a>0)[0]
    if len(valid)<2: return {}
    j0, j1 = valid[0], valid[-1]
    yrs = (dates.iloc[i0+j1] - dates.iloc[i0+j0]).days/365.25
    cagr = (a[j1]/a[j0])**(1/yrs)-1 if yrs>0 else 0
    sub = a[j0:j1+1]; rets = np.diff(sub)/sub[:-1]
    spy_ = (len(sub)-1)/yrs if yrs>0 else 252
    sh = np.mean(rets)*spy_/(np.std(rets)*np.sqrt(spy_)) if np.std(rets)>0 else 0
    rm = np.maximum.accumulate(sub); ddx = sub/rm - 1
    mdd = float(np.min(ddx))
    cal = cagr/abs(mdd) if mdd<0 else np.inf
    return {"cagr":cagr, "sharpe":sh, "max_dd":mdd, "calmar":cal, "n_yrs":yrs, "final":a[j1]/a[j0]}

dates = vni["time"]

# Full + since-2011 windows
mask_pre2011 = (vni["time"]<"2011-01-01").values
idx_2011 = np.where(~mask_pre2011)[0]
i_2011 = idx_2011[0] if len(idx_2011)>0 else 0

m_full_v2g  = metrics(pv_v2g, dates)
m_full_base = metrics(pv_base, dates)
m_full_bh   = metrics(pv_bh, dates)

# Rebase pv from 2011
def rebase(pv, i0):
    p = pv[i0:].copy().astype(float)
    if p[0]>0: p = p/p[0]*1e9
    return p
pv_v2g_2011  = rebase(pv_v2g, i_2011)
pv_base_2011 = rebase(pv_base, i_2011)
pv_bh_2011   = rebase(pv_bh, i_2011)
dates_2011 = dates.iloc[i_2011:].reset_index(drop=True)
m_2011_v2g  = metrics(pv_v2g_2011,  dates_2011)
m_2011_base = metrics(pv_base_2011, dates_2011)
m_2011_bh   = metrics(pv_bh_2011,   dates_2011)

def fmt(m):
    if not m: return "N/A"
    return f"CAGR={m['cagr']*100:5.2f}%  Sh={m['sharpe']:.2f}  DD={m['max_dd']*100:6.2f}%  Cm={m['calmar']:.2f}  ×{m['final']:.2f}"

print("\n" + "="*100)
print(f"{'PERIOD':<14} {'v2g (no-smooth, gate30)':<48} {'baseline (smooth, gate60)':<48} {'B&H'}")
print("="*100)
print(f"{'FULL 2000-2026':<14} {fmt(m_full_v2g):<48} {fmt(m_full_base):<48} {fmt(m_full_bh)}")
print(f"{'SINCE 2011':<14} {fmt(m_2011_v2g):<48} {fmt(m_2011_base):<48} {fmt(m_2011_bh)}")

# ════════════════════ CRISIS lag stats ════════════════════
def crisis_lag(state_arr, since=None):
    segs = []; i = 0
    start_idx = 0
    if since is not None:
        start_idx = int(np.argmax(dates >= pd.Timestamp(since)))
    while i < len(state_arr):
        if state_arr[i]==1:
            j = i
            while j<len(state_arr) and state_arr[j]==1: j += 1
            if j-1 >= start_idx: segs.append((max(i,start_idx), j-1))
            i = j
        else: i += 1
    rows = []
    for k,(s,e) in enumerate(segs,1):
        sc = close[s:e+1]
        if np.all(np.isnan(sc)): continue
        bl = int(np.nanargmin(sc)); bi = s+bl
        rows.append({"days":e-s+1, "lag":e-bi,
                     "bot_to_exit_%": (sc[-1]/sc[bl]-1)*100})
    return pd.DataFrame(rows)

print("\n" + "="*70)
print("CRISIS lag stats (bottom → exit, since 2011)")
print("="*70)
lag_v2g = crisis_lag(state_v2g, since="2011-01-01")
lag_base = crisis_lag(state_baseline, since="2011-01-01")
print(f"{'system':<12} {'n_segs':>7} {'median_lag':>11} {'mean_lag':>9} {'median_rally':>13} {'mean_rally':>11}")
print(f"{'v2g':<12} {len(lag_v2g):>7} {lag_v2g['lag'].median():>11.1f} {lag_v2g['lag'].mean():>9.1f} {lag_v2g['bot_to_exit_%'].median():>12.1f}% {lag_v2g['bot_to_exit_%'].mean():>10.1f}%")
print(f"{'baseline':<12} {len(lag_base):>7} {lag_base['lag'].median():>11.1f} {lag_base['lag'].mean():>9.1f} {lag_base['bot_to_exit_%'].median():>12.1f}% {lag_base['bot_to_exit_%'].mean():>10.1f}%")

# ════════════════════ STATE DISTRIBUTION ════════════════════
print("\nState distribution (% time):")
print(f"{'state':<10} {'v2g':>8} {'baseline':>10}")
for s in range(1,6):
    pv_pct = np.sum(state_v2g==s)/n*100
    pb_pct = np.sum(state_baseline==s)/n*100
    print(f"  {STATE_NAMES[s]:<8} {pv_pct:>7.1f}% {pb_pct:>9.1f}%")

n_trans_v2g = int(np.sum(np.diff(state_v2g) != 0))
n_trans_base = int(np.sum(np.diff(state_baseline) != 0))
print(f"\nTransitions: v2g={n_trans_v2g}  baseline={n_trans_base}")

# ════════════════════ SAVE STATE FILES ════════════════════
out_df = pd.DataFrame({
    "time": vni["time"],
    "Close": close,
    "state_v2g": state_v2g,
    "state_baseline": state_baseline,
    "state_raw": state_raw,
    "r_score": r_score,
    "r_score_ema": r_score_ema,
    "bear_dvg": bear_mask.astype(int),
    "bull_dvg": bull_mask.astype(int),
    "E2_capitulation": E2.astype(int),
    "pv_v2g": pv_v2g,
    "pv_baseline": pv_base,
    "pv_bh": pv_bh,
    "weight_v2g": w_v2g,
    "weight_baseline": w_base,
})
out_df.to_csv(os.path.join(WORKDIR, "data/vnindex_5state_v2g_full_history.csv"), index=False)
print(f"\nSaved → vnindex_5state_v2g_full_history.csv  ({len(out_df)} rows)")

# ════════════════════ QWF: rolling 1Y, 3Y, 5Y at quarter-ends ════════════════════
print("\n" + "="*100)
print("QUARTERLY WALK-FORWARD (rolling 1Y, 3Y, 5Y at each quarter-end since 2014)")
print("="*100)

# Build quarter-end indices
qends = pd.date_range(start="2014-03-31", end=dates.iloc[-1], freq="QE")  # quarter-end
qend_rows = []
def metrics_window(pv_arr, dates_, end_idx, years):
    end_t = dates_.iloc[end_idx]
    start_t = end_t - pd.DateOffset(years=years)
    start_idx_arr = np.where(dates_ >= start_t)[0]
    if len(start_idx_arr) == 0: return {}
    si = start_idx_arr[0]
    if end_idx - si < 30: return {}
    return metrics(pv_arr, dates_, si, end_idx)

for qe in qends:
    arr = np.where(dates <= qe)[0]
    if len(arr) == 0: continue
    ei = arr[-1]
    row = {"q_end": qe.strftime("%Y-%m-%d")}
    for yrs in [1, 3, 5]:
        for nm, pvx in [("v2g", pv_v2g), ("base", pv_base), ("bh", pv_bh)]:
            m = metrics_window(pvx, dates, ei, yrs)
            if m:
                row[f"{nm}_{yrs}Y_cagr"] = m["cagr"]*100
                row[f"{nm}_{yrs}Y_sh"]   = m["sharpe"]
                row[f"{nm}_{yrs}Y_dd"]   = m["max_dd"]*100
                row[f"{nm}_{yrs}Y_cm"]   = m["calmar"]
    qend_rows.append(row)
qdf = pd.DataFrame(qend_rows)
qdf.to_csv(os.path.join(WORKDIR, "data/vnindex_5state_v2g_qwf.csv"), index=False)
print(f"Saved → vnindex_5state_v2g_qwf.csv  ({len(qdf)} quarter snapshots)")

# Snapshot most recent + trailing-3Y traffic light
latest = qdf.iloc[-1]
print(f"\n=== LATEST SNAPSHOT @ {latest['q_end']} ===")
for yrs in [1,3,5]:
    print(f"\n--- Trailing {yrs}Y ---")
    print(f"  {'sys':<10} {'CAGR':>7} {'Sharpe':>8} {'MaxDD':>8} {'Calmar':>8}")
    for nm in ["v2g","base","bh"]:
        c = latest.get(f"{nm}_{yrs}Y_cagr", np.nan)
        s = latest.get(f"{nm}_{yrs}Y_sh", np.nan)
        d = latest.get(f"{nm}_{yrs}Y_dd", np.nan)
        cm = latest.get(f"{nm}_{yrs}Y_cm", np.nan)
        print(f"  {nm:<10} {c:>6.2f}% {s:>8.2f} {d:>7.2f}% {cm:>8.2f}")

# Aggregate stats across all quarters
print("\n" + "="*70)
print("QWF SUMMARY: distribution of trailing-3Y metrics over all quarters")
print("="*70)
print(f"{'system':<10} {'median CAGR':>13} {'median Sharpe':>15} {'median MaxDD':>14} {'win quarters':>14}")
for nm in ["v2g","base","bh"]:
    col_c = f"{nm}_3Y_cagr"; col_s = f"{nm}_3Y_sh"; col_d = f"{nm}_3Y_dd"
    if col_c not in qdf.columns: continue
    sub = qdf[col_c].dropna()
    sh_med = qdf[col_s].dropna().median()
    dd_med = qdf[col_d].dropna().median()
    # win quarters = how many quarters v2g beat bh on cagr_3Y
    if nm != "bh":
        win = (qdf[col_c] > qdf["bh_3Y_cagr"]).mean()*100
    else:
        win = 100.0
    print(f"  {nm:<8} {sub.median():>12.2f}% {sh_med:>15.2f} {dd_med:>13.2f}% {win:>13.1f}%")

# Traffic light: v2g 3Y in expected range
print("\n=== TRAFFIC LIGHT (v2g trailing-3Y at all quarter snapshots) ===")
red_q = 0; yellow_q = 0; green_q = 0
for _, row in qdf.iterrows():
    c = row.get("v2g_3Y_cagr", np.nan)
    s = row.get("v2g_3Y_sh", np.nan)
    d = row.get("v2g_3Y_dd", np.nan)
    bh_c = row.get("bh_3Y_cagr", np.nan)
    if np.isnan(c): continue
    # Green if v2g beats bh AND DD < -25%
    # Red if v2g loses to bh by >5pp OR DD > -25%
    # Yellow otherwise
    if not np.isnan(bh_c) and c > bh_c and d > -25:
        green_q += 1
    elif (not np.isnan(bh_c) and (c < bh_c - 5)) or d < -25:
        red_q += 1
    else:
        yellow_q += 1
print(f"  GREEN : {green_q} quarters")
print(f"  YELLOW: {yellow_q} quarters")
print(f"  RED   : {red_q} quarters")
