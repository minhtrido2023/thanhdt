# -*- coding: utf-8 -*-
"""
analyze_f_system_v3.py
=======================
F-system backtest dung VN30 cho forward returns (thay vi VNINDEX).
  - State machine / r_score: van dung VNINDEX (H-system signal)
  - Forward return T+h: dung VN30 close (vi trade VN30F futures)
  - vol_20d, p1m features: dung VN30
  - bear_ret (SIG-A): dung VN30
VN30 co tu 2012-02-06 -> SIG-A truoc 2012 se NaN (bi loai khoi WR calc).
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import os, numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
W_BASE = {"P3M":0.30,"P1M":0.10,"MA200":0.15,"RSI":0.15,"MACD":0.10,"CMF":0.08,"Breadth":0.12}
MIN_LB=252; MIN_FACTORS=3; MODE_WIN=15; MIN_STAY=7; EMA_ALPHA=0.40
STATE_NAMES={1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}
TC = 0.001   # 0.1% round-trip derivatives

# ══════════════════════════════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════════════════════════════
print("Loading data...")
vni = pd.read_csv(os.path.join(WORKDIR,"data/VNINDEX.csv"), low_memory=False)
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)

for col in ["Close","Open","High","Low","Volume","D_RSI","D_MACDdiff","D_CMF",
            "VNINDEX_PE","VN30","VN30_T1M"]:
    if col in vni.columns:
        vni[col] = pd.to_numeric(vni[col], errors="coerce")

b_path = os.path.join(WORKDIR,"data/breadth_data.csv")
if os.path.exists(b_path):
    b = pd.read_csv(b_path); b["time"] = pd.to_datetime(b["time"])
    b["breadth"] = pd.to_numeric(b["breadth"], errors="coerce")
    vni = vni.merge(b, on="time", how="left")
else:
    vni["breadth"] = np.nan

n     = len(vni)
close = vni["Close"].values.copy()         # VNINDEX close (for state machine only)
vn30  = vni["VN30"].values.copy()          # VN30 close (for returns & features)

cal_days = (vni["time"].iloc[-1]-vni["time"].iloc[0]).days
SPY = n / (cal_days/365.25)

print(f"  VNINDEX: {len(vni)} rows | VN30 valid: {(~np.isnan(vn30)).sum()} rows "
      f"({vni.loc[~pd.isna(vni['VN30']),'time'].min().date()} -> "
      f"{vni.loc[~pd.isna(vni['VN30']),'time'].max().date()})")

# ══════════════════════════════════════════════════════════════════════
# COMPUTE STATE MACHINE ON VNINDEX (unchanged)
# ══════════════════════════════════════════════════════════════════════
print("Computing VNINDEX state machine...")

def rolling_ret_arr(arr, w):
    out = np.full(len(arr), np.nan)
    for i in range(w, len(arr)):
        if arr[i-w] > 0: out[i] = arr[i]/arr[i-w] - 1
    return out

def expanding_rank(arr):
    out = np.full(len(arr), np.nan)
    for i in range(MIN_LB, len(arr)):
        win   = arr[max(0,i-3000):i+1]
        valid = win[~np.isnan(win)]
        if len(valid) < 10 or np.isnan(arr[i]): continue
        out[i] = np.searchsorted(np.sort(valid), arr[i]) / len(valid)
    return out

p3m_vni = rolling_ret_arr(close, 63)
p1m_vni = rolling_ret_arr(close, 21)
ma200   = np.full(n, np.nan)
for i in range(199,n): ma200[i] = np.mean(close[i-199:i+1])
ma200_dev = np.where(ma200>0, close/ma200-1, np.nan)
rsi_arr   = vni["D_RSI"].values.copy() if "D_RSI" in vni.columns else np.full(n, np.nan)
macd_arr  = vni["D_MACDdiff"].values.copy() if "D_MACDdiff" in vni.columns else np.full(n, np.nan)
cmf_arr   = vni["D_CMF"].values.copy() if "D_CMF" in vni.columns else np.full(n, np.nan)
brdt_arr  = vni["breadth"].values.copy() if "breadth" in vni.columns else np.full(n, np.nan)

ranks = {
    "P3M": expanding_rank(p3m_vni), "P1M": expanding_rank(p1m_vni),
    "MA200": expanding_rank(ma200_dev), "RSI": expanding_rank(rsi_arr),
    "MACD": expanding_rank(macd_arr), "CMF": expanding_rank(cmf_arr),
    "Breadth": expanding_rank(brdt_arr),
}
score = np.full(n, np.nan)
for i in range(n):
    vals = [(w,ranks[k][i]) for k,w in W_BASE.items() if not np.isnan(ranks[k][i])]
    if len(vals) >= MIN_FACTORS:
        tw = sum(x[0] for x in vals)
        score[i] = sum(x[0]*x[1] for x in vals) / tw

r_score = np.full(n, np.nan); last = None
for i in range(n):
    if np.isnan(score[i]):
        r_score[i] = last
    else:
        r_score[i] = EMA_ALPHA*score[i]+(1-EMA_ALPHA)*last if last is not None else score[i]
        last = r_score[i]

def classify(rs):
    if np.isnan(rs): return 3
    if rs<0.10: return 1
    elif rs<0.20: return 2
    elif rs<0.70: return 3
    elif rs<0.90: return 4
    else: return 5

state_raw = np.array([classify(v) for v in r_score])

pe_arr  = vni["VNINDEX_PE"].values.copy() if "VNINDEX_PE" in vni.columns else np.full(n, np.nan)
pe_p90  = np.full(n, np.nan)
for i in range(252,n):
    w2 = pe_arr[max(0,i-3000):i+1]; v2 = w2[~np.isnan(w2)]
    if len(v2)>=50: pe_p90[i] = np.percentile(v2, 90)

pk = close[0]; dd_a = np.zeros(n)
for i in range(n):
    if close[i]>pk: pk=close[i]
    dd_a[i] = close[i]/pk - 1

# vol20 on VNINDEX (for state overrides)
log_r_vni = np.concatenate([[np.nan], np.diff(np.log(np.where(close>0, close, np.nan)))])
vol20_vni = np.full(n, np.nan)
for i in range(20,n): vol20_vni[i] = np.nanstd(log_r_vni[i-19:i+1]) * np.sqrt(SPY)
vol20_vni_ma = np.full(n, np.nan)
for i in range(60,n): vol20_vni_ma[i] = np.nanmean(vol20_vni[i-59:i+1])

so = state_raw.copy()
for i in range(n):
    s = so[i]
    if not np.isnan(pe_p90[i]) and not np.isnan(pe_arr[i]) and pe_arr[i]>pe_p90[i] and s>=4:
        so[i] = min(s,4)
    if dd_a[i] < -0.25 and s>=3:
        so[i] = min(s,3)
    if (not np.isnan(vol20_vni[i]) and not np.isnan(vol20_vni_ma[i])
            and vol20_vni_ma[i]>0 and vol20_vni[i]>1.5*vol20_vni_ma[i] and s>=4):
        so[i] = min(s,4)

def rolling_mode(arr, w):
    out = arr.copy()
    for i in range(w-1, len(arr)):
        win = arr[i-w+1:i+1]
        counts = np.bincount(win, minlength=6)
        out[i] = np.argmax(counts)
    return out

def min_stay_filter(arr, ms):
    out = arr.copy(); i = 0
    while i < len(arr):
        j = i+1
        while j<len(arr) and arr[j]==arr[i]: j+=1
        if j-i < ms:
            prev = out[i-1] if i>0 else arr[i]; out[i:j] = prev
        i = j
    return out

ss = rolling_mode(so, MODE_WIN)
ss = min_stay_filter(ss, MIN_STAY)
vni["state"] = ss
vni["r_score"] = r_score

# ══════════════════════════════════════════════════════════════════════
# COMPUTE VN30-BASED FEATURES (for return measurement & scoring)
# ══════════════════════════════════════════════════════════════════════
print("Computing VN30 features...")

# vol20 on VN30
log_r_vn30 = np.full(n, np.nan)
for i in range(1,n):
    if not np.isnan(vn30[i]) and not np.isnan(vn30[i-1]) and vn30[i-1]>0:
        log_r_vn30[i] = np.log(vn30[i]/vn30[i-1])

vol20_vn30 = np.full(n, np.nan)
for i in range(20,n):
    w2 = log_r_vn30[i-19:i+1]; valid = w2[~np.isnan(w2)]
    if len(valid) >= 15:
        vol20_vn30[i] = np.std(valid) * np.sqrt(SPY)

# p1m on VN30 (21-session rolling return)
p1m_vn30 = np.full(n, np.nan)
for i in range(21,n):
    if not np.isnan(vn30[i]) and not np.isnan(vn30[i-21]) and vn30[i-21]>0:
        p1m_vn30[i] = vn30[i]/vn30[i-21] - 1

vni["vol20_vn30"] = vol20_vn30
vni["p1m_vn30"]   = p1m_vn30

# Median vol (VN30, historical)
valid_vol_vn30 = vol20_vn30[~np.isnan(vol20_vn30)]
MEDIAN_VOL_VN30 = float(np.median(valid_vol_vn30)) if len(valid_vol_vn30)>0 else 0.18
print(f"  VN30 median vol20: {MEDIAN_VOL_VN30:.1%}")

# ══════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════
def fwd_ret_vn30(idx, h):
    """T+1 entry (next open approx next close), exit at VN30 close T+h+1.
    Dung VN30 vi trade VN30F futures."""
    if idx+h+1 >= n: return np.nan
    entry = vn30[idx+1]
    exit_ = vn30[idx+h+1]
    if np.isnan(entry) or np.isnan(exit_) or entry<=0: return np.nan
    return exit_/entry - 1

def kelly_leverage(p, b, frac=0.3):
    if b<=0: return 0
    f_star = (p*b - (1-p)) / b
    return min(max(0, f_star) * frac * 10, 3.0)  # scale to leverage, cap 3x

def feature_analysis(records, feature_cols, target_col, n_bins=3):
    df = pd.DataFrame(records)
    if len(df)<5: return
    for fc in feature_cols:
        if fc not in df.columns: continue
        vals = df[fc].dropna()
        if len(vals)<5: continue
        try:
            df[fc+"_bin"] = pd.qcut(df[fc], q=n_bins, labels=False, duplicates="drop")
        except: continue
        grp = df.groupby(fc+"_bin").agg(
            n=(target_col,"count"),
            wr=(target_col, lambda x: (x>0).mean()),
            mean_ret=(target_col,"mean"),
        ).reset_index()
        print(f"    {fc}:")
        for _,row in grp.iterrows():
            bar = int(row["wr"]*20)*"|"
            print(f"      bin{int(row[fc+'_bin'])}: n={int(row['n']):>4}  "
                  f"WR={row['wr']*100:>5.1f}%  mean={row['mean_ret']*100:>+6.3f}%  {bar}")

# ══════════════════════════════════════════════════════════════════════
# SIG-A: BEAR -> NEUTRAL TRANSITION  (returns on VN30)
# ══════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("SIG-A: BEAR -> NEUTRAL TRANSITION  [returns: VN30]")
print("="*70)

segs = []
i = 0
while i < n:
    j = i+1
    while j<n and ss[j]==ss[i]: j+=1
    segs.append({"state":int(ss[i]),"start":i,"end":j-1,"dur":j-i,
                 "date_start":vni["time"].iloc[i],"date_end":vni["time"].iloc[j-1]})
    i = j

siga_records = []
for si in range(1, len(segs)):
    seg  = segs[si]
    prev = segs[si-1]
    if prev["state"]!=2 or seg["state"]!=3: continue
    entry_i = seg["start"]
    if entry_i < MIN_LB: continue

    # bear_ret on VN30 (NaN if VN30 not available)
    bs = prev["start"]; be = prev["end"]
    if not np.isnan(vn30[bs]) and not np.isnan(vn30[be]) and vn30[bs]>0:
        bear_ret_vn30 = vn30[be]/vn30[bs] - 1
    else:
        bear_ret_vn30 = np.nan

    rec = dict(
        date          = vni["time"].iloc[entry_i],
        bear_dur      = prev["dur"],
        bear_ret      = bear_ret_vn30,             # VN30 bear return
        r_score_entry = float(r_score[entry_i]) if not np.isnan(r_score[entry_i]) else np.nan,
        vol_entry     = float(vol20_vn30[entry_i]) if not np.isnan(vol20_vn30[entry_i]) else np.nan,
        p1m_entry     = float(p1m_vn30[entry_i])   if not np.isnan(p1m_vn30[entry_i])  else np.nan,
    )
    for h in [1,2,3,5,10]:
        rec[f"ret_T{h}"] = fwd_ret_vn30(entry_i, h)
        rec[f"win_T{h}"] = ((rec[f"ret_T{h}"] or 0) - TC > 0)
    siga_records.append(rec)

df_a = pd.DataFrame(siga_records)
# Filter to rows that have VN30 data
df_a_vn30 = df_a[df_a["ret_T5"].notna()].copy()

print(f"\n  Total BEAR->NEUTRAL signals (all): {len(df_a)}")
print(f"  With VN30 data (2012+): {len(df_a_vn30)}")
if len(df_a_vn30) > 0:
    print(f"  Date range: {df_a_vn30['date'].min().date()} -> {df_a_vn30['date'].max().date()}")

print("\n  --- Overall performance (VN30 returns) ---")
print(f"  {'Horizon':>8} {'n':>5} {'WR':>7} {'MeanRet':>9} {'MeanNet':>9} "
      f"{'AvgWin':>8} {'AvgLoss':>8} {'PF':>6}")
print("  "+"-"*68)
for h in [1,2,3,5,10]:
    rets = df_a_vn30[f"ret_T{h}"].dropna().values
    if len(rets)==0: continue
    nets = rets - TC
    wr   = (nets>0).mean()
    mret = rets.mean()*100; mnet = nets.mean()*100
    avg_w = rets[nets>0].mean()*100 if (nets>0).any() else 0
    avg_l = rets[nets<0].mean()*100 if (nets<0).any() else 0
    pf    = abs(rets[nets>0].sum()/rets[nets<0].sum()) if (nets<0).any() else 99
    print(f"  T+{h:>6}: {len(rets):>5} {wr*100:>6.1f}% {mret:>+8.3f}% {mnet:>+8.3f}% "
          f"{avg_w:>+7.3f}% {avg_l:>+7.3f}% {pf:>6.2f}")

print("\n  --- Individual trades (T+5, VN30) ---")
print(f"  {'Date':<12} {'BearDur':>8} {'BearRet':>9} {'rs_entry':>9} {'vol':>7} "
      f"{'ret_T5(VN30)':>13} {'ret_T3':>8}")
print("  "+"-"*75)
for _,row in df_a.iterrows():
    r5 = row.get("ret_T5", float("nan")); r3 = row.get("ret_T3", float("nan"))
    has_vn30 = not np.isnan(r5)
    flag = "WIN" if has_vn30 and r5-TC>0 else ("LOSS" if has_vn30 else "no_vn30")
    r5s  = f"{r5*100:>+7.2f}%" if has_vn30 else "    N/A"
    r3s  = f"{r3*100:>+6.2f}%" if not np.isnan(r3) else "   N/A"
    br   = f"{row['bear_ret']*100:>+8.1f}%" if not np.isnan(row['bear_ret']) else "     N/A"
    print(f"  {str(row['date'].date()):<12} {row['bear_dur']:>8.0f} {br} "
          f"{row['r_score_entry']:>9.3f} "
          f"{row['vol_entry']*100 if not np.isnan(row['vol_entry']) else float('nan'):>6.1f}% "
          f"{r5s} {r3s}  {flag}")

# Feature analysis
print("\n  --- Feature vs Win Rate T+5 (VN30, only 2012+) ---")
df_a_vn30["win_T5_num"] = (df_a_vn30["ret_T5"] - TC > 0).astype(float)
feature_analysis(df_a_vn30, ["bear_dur","bear_ret","r_score_entry","vol_entry","p1m_entry"], "win_T5_num")

# Composite score
print("\n  --- Composite probability model (SIG-A) ---")
median_vol_a = float(np.nanmedian(df_a_vn30["vol_entry"].values)) if len(df_a_vn30)>0 else MEDIAN_VOL_VN30
print(f"  Median vol (SIG-A sample): {median_vol_a:.1%}")

def score_siga(row):
    s=0
    if not np.isnan(row["bear_dur"])      and row["bear_dur"]>15:          s+=1
    if not np.isnan(row["bear_ret"])      and row["bear_ret"]<-0.08:       s+=1
    if not np.isnan(row["r_score_entry"]) and row["r_score_entry"]<0.32:   s+=1
    if not np.isnan(row["vol_entry"])     and row["vol_entry"]<median_vol_a: s+=1
    if not np.isnan(row["p1m_entry"])     and row["p1m_entry"]<-0.05:      s+=1
    return s

df_a_vn30["comp_score"] = df_a_vn30.apply(score_siga, axis=1)
df_a["comp_score"]      = df_a.apply(score_siga, axis=1)

print(f"\n  {'Score':>6} {'n':>5} {'WR_T3':>8} {'WR_T5':>8} {'Net_T3':>9} {'Net_T5':>9} "
      f"{'b=W/L':>7} {'f*':>6} {'Kelly30%':>9} {'Rec_Lev':>9}")
print("  "+"-"*80)
for sc in sorted(df_a_vn30["comp_score"].unique()):
    sub = df_a_vn30[df_a_vn30["comp_score"]==sc]
    wr3 = (sub["ret_T3"]-TC>0).mean(); wr5 = (sub["ret_T5"]-TC>0).mean()
    net3= sub["ret_T3"].mean()-TC; net5 = sub["ret_T5"].mean()-TC
    w5  = sub["ret_T5"][sub["ret_T5"]-TC>0].mean()  if (sub["ret_T5"]-TC>0).any() else 0
    l5  = abs(sub["ret_T5"][sub["ret_T5"]-TC<0].mean()) if (sub["ret_T5"]-TC<0).any() else 0.01
    b5  = w5/l5 if l5>0 else 0
    f_s = (wr5*b5-(1-wr5))/b5 if b5>0 else 0
    lev = kelly_leverage(wr5, b5, 0.3)
    flag= "OK" if net5>0 and wr5>0.55 else ("?" if net5>0 else "")
    print(f"  {sc:>6} {len(sub):>5} {wr3*100:>7.1f}% {wr5*100:>7.1f}% "
          f"{net3*100:>+8.3f}% {net5*100:>+8.3f}% "
          f"{b5:>7.2f} {f_s:>6.3f}  {lev:>6.2f}x  {flag}")

# ══════════════════════════════════════════════════════════════════════
# SIG-B: r_score VALLEY  (returns on VN30)
# ══════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("SIG-B: r_score VALLEY (TURN SIGNAL)  [returns: VN30]")
print("="*70)

MIN_DELTA = 0.010

sigb_records = []
for i in range(2, n-6):
    rs_prev = r_score[i-1]; rs_cur = r_score[i]; rs_next = r_score[i+1]
    if any(np.isnan([rs_prev, rs_cur, rs_next])): continue
    if i < MIN_LB: continue
    if not (rs_cur < rs_prev and rs_cur < rs_next): continue
    delta_up = rs_next - rs_cur
    if delta_up < MIN_DELTA: continue

    # Valley depth (lookback 30 sessions of r_score)
    prior_peak_rs = float(np.nanmax(r_score[max(0,i-30):i+1]))
    valley_depth  = prior_peak_rs - rs_cur
    prior_peak_idx = i-1
    for j in range(i-1, max(0,i-60), -1):
        if not np.isnan(r_score[j]) and r_score[j] == prior_peak_rs:
            prior_peak_idx = j; break
    valley_dur = i - prior_peak_idx

    rec = dict(
        date           = vni["time"].iloc[i],
        r_score_valley = rs_cur,
        delta_up       = delta_up,
        valley_depth   = valley_depth,
        valley_dur     = valley_dur,
        state          = int(ss[i]),
        state_name     = STATE_NAMES[int(ss[i])],
        vol_entry      = float(vol20_vn30[i]) if not np.isnan(vol20_vn30[i]) else np.nan,
        p1m_entry      = float(p1m_vn30[i])   if not np.isnan(p1m_vn30[i])   else np.nan,
        dd_entry       = float(dd_a[i]),
    )
    for h in [1,2,3,5,10]:
        rec[f"ret_T{h}"] = fwd_ret_vn30(i, h)
        rec[f"win_T{h}"] = ((rec[f"ret_T{h}"] or 0) - TC > 0)
    sigb_records.append(rec)

df_b = pd.DataFrame(sigb_records)
df_b = df_b[df_b["date"] >= "2012-02-06"].reset_index(drop=True)  # VN30 start
df_b_valid = df_b[df_b["ret_T5"].notna()].copy()

print(f"\n  Total valley signals (2012+): {len(df_b_valid)}")
if len(df_b_valid) > 0:
    freq_b = len(df_b_valid) / ((df_b_valid["date"].max()-df_b_valid["date"].min()).days/365.25)
    print(f"  Frequency: {freq_b:.1f} signals/year")
    print(f"  Date range: {df_b_valid['date'].min().date()} -> {df_b_valid['date'].max().date()}")

print("\n  --- Overall performance (VN30 returns) ---")
print(f"  {'Horizon':>8} {'n':>5} {'WR':>7} {'MeanRet':>9} {'MeanNet':>9} "
      f"{'AvgWin':>8} {'AvgLoss':>8} {'PF':>6}")
print("  "+"-"*68)
for h in [1,2,3,5,10]:
    rets = df_b_valid[f"ret_T{h}"].dropna().values
    if len(rets)==0: continue
    nets = rets-TC
    wr   = (nets>0).mean(); mret=rets.mean()*100; mnet=nets.mean()*100
    avg_w= rets[nets>0].mean()*100 if (nets>0).any() else 0
    avg_l= rets[nets<0].mean()*100 if (nets<0).any() else 0
    pf   = abs(rets[nets>0].sum()/rets[nets<0].sum()) if (nets<0).any() else 99
    print(f"  T+{h:>6}: {len(rets):>5} {wr*100:>6.1f}% {mret:>+8.3f}% {mnet:>+8.3f}% "
          f"{avg_w:>+7.3f}% {avg_l:>+7.3f}% {pf:>6.2f}")

print("\n  --- Win rate by state ---")
for sn in ["CRISIS","BEAR","NEUTRAL","BULL","EX-BULL"]:
    sub = df_b_valid[df_b_valid["state_name"]==sn]
    if len(sub)<3: continue
    wr5=(sub["ret_T5"]-TC>0).mean(); net5=sub["ret_T5"].mean()-TC
    print(f"    {sn:<12}: n={len(sub):>4}  WR_T5={wr5*100:>5.1f}%  net_T5={net5*100:>+6.3f}%")

print("\n  --- Feature vs Win Rate T+5 (VN30) ---")
df_b_valid["win_T5_num"] = (df_b_valid["ret_T5"]-TC>0).astype(float)
feature_analysis(df_b_valid,
    ["r_score_valley","delta_up","valley_depth","valley_dur","vol_entry","p1m_entry"],
    "win_T5_num")

# Composite score
print("\n  --- Composite probability model (SIG-B) ---")
median_vol_b = float(np.nanmedian(df_b_valid["vol_entry"].values)) if len(df_b_valid)>0 else MEDIAN_VOL_VN30
print(f"  Median vol (SIG-B sample): {median_vol_b:.1%}")
print("  Rules (tham khao tu backtest VN30):")
print("  +1: r_score_valley < 0.40 | +1: delta_up > 0.015 | +1: valley_depth > 0.05")
print("  +1: state in NEUTRAL/BULL/EX-BULL | +1: p1m < -3% | +1: vol < median")

def score_sigb(row):
    s=0
    if not np.isnan(row["r_score_valley"]) and row["r_score_valley"]<0.40:     s+=1
    if not np.isnan(row["delta_up"])        and row["delta_up"]>0.015:          s+=1
    if not np.isnan(row["valley_depth"])    and row["valley_depth"]>0.05:       s+=1
    if row["state"] in [3,4,5]:                                                  s+=1
    if not np.isnan(row["p1m_entry"])       and row["p1m_entry"]<-0.03:         s+=1
    if not np.isnan(row["vol_entry"])       and row["vol_entry"]<median_vol_b:  s+=1
    return s

df_b_valid["comp_score"] = df_b_valid.apply(score_sigb, axis=1)

print(f"\n  {'Score':>6} {'n':>5} {'WR_T3':>8} {'WR_T5':>8} {'Net_T3':>9} {'Net_T5':>9} "
      f"{'b=W/L':>7} {'f*':>6} {'Kelly30%':>9} {'Rec_Lev':>9}")
print("  "+"-"*80)
for sc in sorted(df_b_valid["comp_score"].unique()):
    sub = df_b_valid[df_b_valid["comp_score"]==sc]
    wr3=(sub["ret_T3"]-TC>0).mean(); wr5=(sub["ret_T5"]-TC>0).mean()
    net3=sub["ret_T3"].mean()-TC; net5=sub["ret_T5"].mean()-TC
    w5=sub["ret_T5"][sub["ret_T5"]-TC>0].mean()  if (sub["ret_T5"]-TC>0).any() else 0
    l5=abs(sub["ret_T5"][sub["ret_T5"]-TC<0].mean()) if (sub["ret_T5"]-TC<0).any() else 0.01
    b5=w5/l5 if l5>0 else 0
    f_s=(wr5*b5-(1-wr5))/b5 if b5>0 else 0
    lev=kelly_leverage(wr5,b5,0.3)
    flag="OK" if net5>0 and wr5>0.55 else ("?" if net5>0 else "")
    print(f"  {sc:>6} {len(sub):>5} {wr3*100:>7.1f}% {wr5*100:>7.1f}% "
          f"{net3*100:>+8.3f}% {net5*100:>+8.3f}% "
          f"{b5:>7.2f} {f_s:>6.3f}  {lev:>6.2f}x  {flag}")

# ══════════════════════════════════════════════════════════════════════
# COMBINED STRATEGY
# ══════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("COMBINED F-SYSTEM: SIG-A + SIG-B (score >= 3, VN30 returns)")
print("="*70)

all_trades = []
for _,row in df_a_vn30.iterrows():
    if row["comp_score"] < 1: continue
    r5 = row.get("ret_T5", float("nan"))
    if np.isnan(r5): continue
    all_trades.append(dict(date=row["date"], signal="SIG-A",
                           score=row["comp_score"], ret_T5=r5, net_T5=r5-TC))
for _,row in df_b_valid.iterrows():
    if row["comp_score"] < 3: continue
    r5 = row.get("ret_T5", float("nan"))
    if np.isnan(r5): continue
    all_trades.append(dict(date=row["date"], signal="SIG-B",
                           score=row["comp_score"], ret_T5=r5, net_T5=r5-TC))

df_trades = pd.DataFrame(all_trades).sort_values("date").reset_index(drop=True)

if len(df_trades) > 0:
    yrs = (df_trades["date"].max()-df_trades["date"].min()).days/365.25
    print(f"\n  Total trades: {len(df_trades)} over {yrs:.1f} years = {len(df_trades)/yrs:.1f}/yr")
    wr   = (df_trades["net_T5"]>0).mean()
    mnet = df_trades["net_T5"].mean()
    avg_w= df_trades.loc[df_trades["net_T5"]>0,"net_T5"].mean() if (df_trades["net_T5"]>0).any() else 0
    avg_l= df_trades.loc[df_trades["net_T5"]<0,"net_T5"].mean() if (df_trades["net_T5"]<0).any() else 0
    pf   = abs(df_trades.loc[df_trades["net_T5"]>0,"net_T5"].sum() /
               df_trades.loc[df_trades["net_T5"]<0,"net_T5"].sum()) if (df_trades["net_T5"]<0).any() else 99
    print(f"  WR={wr*100:.1f}%  MeanNet={mnet*100:>+.3f}%  "
          f"AvgWin={avg_w*100:>+.3f}%  AvgLoss={avg_l*100:>+.3f}%  PF={pf:.2f}")

    print(f"\n  {'Date':<12} {'Sig':>6} {'Score':>6} {'ret_T5(VN30)':>13} {'net_T5':>9}")
    print("  "+"-"*55)
    for _,row in df_trades.iterrows():
        flag = "W" if row["net_T5"]>0 else "L"
        print(f"  {str(row['date'].date()):<12} {row['signal']:>6} {int(row['score']):>6}  "
              f"{row['ret_T5']*100:>+7.2f}%   {row['net_T5']*100:>+7.2f}%  {flag}")

print("\nDone.")
