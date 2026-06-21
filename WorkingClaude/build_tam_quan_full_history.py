# -*- coding: utf-8 -*-
"""
build_tam_quan_full_history.py
==============================
Rebuild Tam Quan v3 state covering FULL HISTORY 2006-now (extending pre-2014).

Pipeline (same as v3 but with extended universe pull):
  1. Pull universe 2005-01-01 to now (extends 1y warmup before 2006)
  2. EW universe: ≥252 sessions history + 60d avg trading value ≥ 500M VND (relaxed
     to 100M VND if pre-2014 too sparse — pre-2014 market was thinner)
  3. Concentration: trading-value HHI + CR3 + cap-EW 60d divergence; expanding rank
  4. VNINDEX_EW from 2006-01-03 onwards (need 252 sessions warmup from 2005)
  5. Raw VNI factors (8 with PE-comp), EW factors (7)
  6. Dynamic α blend, EMA, classify, overrides, v2g gate, s3 smoothing

Output: vnindex_5state_dual_v3_full_history.csv (2007-2013 stress-test ready)
"""
import sys, io, os, subprocess, tempfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
BQ      = r"bq"
PROJECT = "lithe-record-440915-m9"

# Params
W_BASE_7    = {"P3M":0.30, "P1M":0.10, "MA200":0.15, "RSI":0.15,
               "MACD":0.10, "CMF":0.08, "Breadth":0.12}
W_PE        = 0.03
MIN_LB      = 252
MIN_FACTORS = 3
EMA_ALPHA   = 0.40
CONC_EMA    = 0.20
GATE_MIN_V2G = 30
MODE_WIN_S3 = 3
MIN_STAY_S3 = 2
EW_START    = pd.Timestamp("2006-01-03")
LIQ_MIN_PRE2014  = 1e8   # 100M VND pre-2014 (thinner market — matches sim_v11_pre2014 convention)
LIQ_MIN_POST2014 = 5e8   # 500M VND post-2014
LIQ_CUTOVER      = pd.Timestamp("2014-01-01")
HIST_MIN    = 252
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}
DVG_MASK_START = "2007-01-01"

CACHE_UNIV_FULL = os.path.join(WORKDIR, "data/_cache_universe_2005_now.pkl")

print("="*70); print("Tam Quan v3 — FULL HISTORY (2006-now) for stress test"); print("="*70)

# ─────────────────────────────────────────────────────────────────────
# Step 1: Pull universe 2005+
# ─────────────────────────────────────────────────────────────────────
def bq_csv(sql):
    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); qp = f.name
    cmd = f'"{BQ}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=20000000 < "{qp}"'
    r = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    os.unlink(qp)
    if r.returncode != 0: raise RuntimeError(r.stderr[:500])
    return pd.read_csv(io.StringIO(r.stdout))

if os.path.exists(CACHE_UNIV_FULL):
    print(f"\n[1] Cache hit: {CACHE_UNIV_FULL}")
    univ = pd.read_pickle(CACHE_UNIV_FULL)
else:
    print("\n[1] Pulling universe 2005-2026 (this may take 1-2 min)...")
    sql = """
    SELECT t.time, t.ticker, t.Close, t.Volume, t.MA50, t.D_CMF
    FROM tav2_bq.ticker AS t
    WHERE t.time >= '2005-01-01'
      AND t.ticker != 'VNINDEX' AND t.ticker != 'VN30'
      AND t.ticker NOT LIKE 'VN30F%'
      AND t.ticker NOT LIKE 'E1VFVN30%'
      AND t.ticker NOT LIKE 'FUE%'
      AND t.Close IS NOT NULL AND t.Close > 0
    """
    univ = bq_csv(sql)
    univ["time"] = pd.to_datetime(univ["time"])
    univ.to_pickle(CACHE_UNIV_FULL)
    print(f"  Cached: {len(univ):,} rows, {univ['ticker'].nunique()} tickers")
print(f"  Universe: {len(univ):,} rows | {univ['time'].min().date()} → {univ['time'].max().date()}")

# Load VNI
vni = pd.read_pickle(os.path.join(WORKDIR, "data/_cache_vnindex_2000_now.pkl"))
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)

# ─────────────────────────────────────────────────────────────────────
# Step 2: Point-in-time eligibility (regime-dependent liquidity threshold)
# ─────────────────────────────────────────────────────────────────────
print("\n[2] Point-in-time eligibility")
univ = univ.sort_values(["ticker","time"]).reset_index(drop=True)
univ["tv"] = univ["Close"] * univ["Volume"]
g = univ.groupby("ticker", group_keys=False)
univ["tv_avg60"] = g["tv"].transform(lambda s: s.rolling(60, min_periods=30).mean())
univ["session_n"] = g.cumcount() + 1
univ["log_ret"]   = g["Close"].transform(lambda s: np.log(s / s.shift(1)))
univ["above_ma50"] = np.where(univ["MA50"].notna() & (univ["Close"] > univ["MA50"]), 1.0,
                              np.where(univ["MA50"].notna(), 0.0, np.nan))

# Liq threshold: 100M pre-2014, 500M post (relaxed for thinner pre-2014 market)
univ["liq_min"] = np.where(univ["time"] < LIQ_CUTOVER, LIQ_MIN_PRE2014, LIQ_MIN_POST2014)
univ["eligible"] = (univ["session_n"] >= HIST_MIN) & (univ["tv_avg60"] >= univ["liq_min"])
print(f"  Eligible rows: {univ['eligible'].sum():,} / {len(univ):,}")

# ─────────────────────────────────────────────────────────────────────
# Step 3: Daily EW + breadth + median CMF
# ─────────────────────────────────────────────────────────────────────
print("\n[3] Aggregate daily EW + breadth + CMF")
sub = univ[univ["eligible"].fillna(False)].copy()
daily = sub.groupby("time").agg(
    n_universe=("ticker","count"),
    ret_ew=("log_ret","mean"),
    cmf_med=("D_CMF","median"),
    breadth=("above_ma50","mean"),
).reset_index().sort_values("time").reset_index(drop=True)
daily["ret_ew"] = daily["ret_ew"].fillna(0)
daily = daily[daily["time"] >= EW_START].reset_index(drop=True)
daily["close_ew"] = 100.0 * np.exp(daily["ret_ew"].cumsum())
print(f"  EW series: {len(daily)} | {daily['time'].min().date()} → {daily['time'].max().date()}")
print(f"  Universe size: min={daily['n_universe'].min()} max={daily['n_universe'].max()} median={int(daily['n_universe'].median())}")

# ─────────────────────────────────────────────────────────────────────
# Step 4: Concentration history (HHI_tv + CR3 + cap-EW div)
# ─────────────────────────────────────────────────────────────────────
print("\n[4] Concentration history")
# Use ALL non-zero-TV rows (regardless of eligibility) for concentration of market overall
all_tv = univ[univ["tv"] > 0].copy()
all_tv["tv_total"] = all_tv.groupby("time")["tv"].transform("sum")
all_tv["w"] = all_tv["tv"] / all_tv["tv_total"]
all_tv["w2"] = all_tv["w"]**2
sub_ = all_tv[["time","w"]].sort_values(["time","w"], ascending=[True,False])
sub_["rk"] = sub_.groupby("time").cumcount() + 1
hhi_s = all_tv.groupby("time")["w2"].sum()
n_s = all_tv.groupby("time")["w"].count()
cr3 = sub_[sub_["rk"]<=3].groupby("time")["w"].sum().reindex(hhi_s.index).fillna(0)

conc = pd.DataFrame({
    "time": hhi_s.index, "HHI_tv": hhi_s.values, "CR3": cr3.values,
    "n_tickers": n_s.values,
}).sort_values("time").reset_index(drop=True)

# Cap-EW 60d divergence
vni_post = vni[vni["time"] >= EW_START][["time","Close"]].rename(columns={"Close":"vni_close"})
ew_post  = daily[["time","close_ew"]].rename(columns={"close_ew":"ew_close"})
m = vni_post.merge(ew_post, on="time", how="inner").sort_values("time").reset_index(drop=True)
m["ret_vni_60d"] = np.log(m["vni_close"] / m["vni_close"].shift(60))
m["ret_ew_60d"]  = np.log(m["ew_close"]  / m["ew_close"].shift(60))
m["capEW_div_60d"] = (m["ret_vni_60d"] - m["ret_ew_60d"]).abs()
conc = conc.merge(m[["time","capEW_div_60d"]], on="time", how="left")

def expanding_pct_rank(arr, min_lb=252):
    arr = np.asarray(arr, dtype=float)
    out = np.full(len(arr), np.nan)
    for t in range(len(arr)):
        if np.isnan(arr[t]): continue
        h = arr[:t+1]; v = h[~np.isnan(h)]
        if len(v) < min_lb: continue
        out[t] = np.sum(v <= arr[t]) / len(v)
    return out

conc["hhi_rank"] = expanding_pct_rank(conc["HHI_tv"].values, 252)
conc["cr3_rank"] = expanding_pct_rank(conc["CR3"].values, 252)
conc["div_rank"] = expanding_pct_rank(conc["capEW_div_60d"].values, 252)

def composite(row):
    vals = [row["hhi_rank"], row["cr3_rank"], row["div_rank"]]
    valid = [v for v in vals if not np.isnan(v)]
    return np.mean(valid) if len(valid) >= 2 else np.nan
conc["concentration_score"] = conc.apply(composite, axis=1)
print(f"  Concentration: {len(conc)} rows | first valid: {conc.dropna(subset=['concentration_score'])['time'].min()}")

# ─────────────────────────────────────────────────────────────────────
# Step 5: Splice composite series (raw pre-EW_START, EW post)
# ─────────────────────────────────────────────────────────────────────
print("\n[5] Splice raw VNI + EW")
vni_pre = vni[vni["time"] < EW_START].copy()
splice_anchor = vni[vni["time"] >= EW_START].iloc[0]
anchor_date = splice_anchor["time"]; anchor_vni = splice_anchor["Close"]
ew_anchor_row = daily[daily["time"] == anchor_date]
if len(ew_anchor_row) == 0:
    ew_anchor_row = daily[daily["time"] >= anchor_date].iloc[[0]]
    anchor_date = ew_anchor_row.iloc[0]["time"]
    anchor_vni = vni[vni["time"] == anchor_date].iloc[0]["Close"]
scale = anchor_vni / ew_anchor_row.iloc[0]["close_ew"]
daily["close_ew_scaled"] = daily["close_ew"] * scale
print(f"  Anchor: {anchor_date.date()} vni={anchor_vni:.2f} ew={ew_anchor_row.iloc[0]['close_ew']:.2f} scale={scale:.4f}")

# Composite Close, D_CMF, breadth, etc.
cols_keep = ["time","Close","VNINDEX_PE","D_CMF","D_RSI","D_RSI_T1W",
             "D_RSI_Max1W","D_RSI_Max3M","D_RSI_Min1W","D_RSI_Min3M",
             "D_RSI_Max1W_Close","D_RSI_Max3M_Close","D_RSI_Max3M_MACD","D_RSI_Max1W_MACD",
             "D_RSI_MinT3","C_L1M","C_L1W"]
pre = vni_pre[cols_keep].copy()
pre["breadth"] = np.nan
pre["source"]  = "raw_vni"

post = vni[vni["time"] >= EW_START][[c for c in cols_keep if c != "Close" and c != "D_CMF"] + ["Close"]].copy()
post = post.rename(columns={"Close":"Close_raw"})  # rename to avoid collision
post = post.merge(daily[["time","close_ew_scaled","cmf_med","breadth","n_universe"]], on="time", how="left")
post = post.dropna(subset=["close_ew_scaled"])
post = post.rename(columns={"close_ew_scaled":"Close","cmf_med":"D_CMF"})
post["source"] = "ew"
# Re-align columns
common_cols = ["time","Close","VNINDEX_PE","D_CMF","D_RSI","D_RSI_T1W",
               "D_RSI_Max1W","D_RSI_Max3M","D_RSI_Min1W","D_RSI_Min3M",
               "D_RSI_Max1W_Close","D_RSI_Max3M_Close","D_RSI_Max3M_MACD","D_RSI_Max1W_MACD",
               "D_RSI_MinT3","C_L1M","C_L1W","breadth","source"]
pre = pre[common_cols]
post = post[common_cols]
df = pd.concat([pre, post], ignore_index=True).sort_values("time").reset_index(drop=True)
print(f"  Composite series: {len(df)} rows | pre={len(pre)} post={len(post)}")

# Save full EW for reuse
ew_out = df.copy()
ew_out["f_Breadth"] = ew_out["breadth"]
ew_out.to_csv(os.path.join(WORKDIR, "data/vnindex_5state_ew_full_history.csv"), index=False)

# ─────────────────────────────────────────────────────────────────────
# Step 6: Recompute factors on composite Close + EW r_score
# ─────────────────────────────────────────────────────────────────────
print("\n[6] Recompute factors (raw 8-factor + EW r_score)")
close_raw = vni["Close"].values.astype(float)
n_full_raw = len(close_raw)
def lagged_return(arr, k):
    out = np.full(len(arr), np.nan)
    for i in range(k, len(arr)):
        if arr[i-k] > 0 and not np.isnan(arr[i-k]) and not np.isnan(arr[i]):
            out[i] = arr[i]/arr[i-k] - 1
    return out
p3m_raw = lagged_return(close_raw, 60); p1m_raw = lagged_return(close_raw, 20)
ma200_raw = pd.Series(close_raw).rolling(200, min_periods=200).mean().values
ma200_dev_raw = np.where((ma200_raw>0)&~np.isnan(ma200_raw), close_raw/ma200_raw-1, np.nan)

rsi_raw = np.full(n_full_raw,np.nan); avg_u=avg_d=np.nan; period=14
for i in range(1, n_full_raw):
    diff = close_raw[i]-close_raw[i-1]
    if np.isnan(diff): continue
    u = max(diff,0.0); d = max(-diff,0.0)
    if np.isnan(avg_u):
        if i >= period:
            gns = [max(close_raw[j]-close_raw[j-1],0) for j in range(1,period+1)]
            lss = [max(close_raw[j-1]-close_raw[j],0) for j in range(1,period+1)]
            avg_u = np.mean(gns); avg_d = np.mean(lss)
            if (avg_u+avg_d)>0: rsi_raw[i] = avg_u/(avg_u+avg_d)
    else:
        avg_u = (avg_u*(period-1)+u)/period
        avg_d = (avg_d*(period-1)+d)/period
        if (avg_u+avg_d)>0: rsi_raw[i] = avg_u/(avg_u+avg_d)

ema12 = np.full(n_full_raw,np.nan); ema26 = np.full(n_full_raw,np.nan)
signal_ = np.full(n_full_raw,np.nan); macd_hist_raw = np.full(n_full_raw,np.nan)
k12,k26,k9 = 2/13,2/27,2/10
for i in range(n_full_raw):
    if np.isnan(close_raw[i]): continue
    if i==0 or np.isnan(ema12[i-1]): ema12[i]=close_raw[i]; ema26[i]=close_raw[i]
    else:
        ema12[i] = ema12[i-1]*(1-k12)+close_raw[i]*k12
        ema26[i] = ema26[i-1]*(1-k26)+close_raw[i]*k26
    macd_line = ema12[i]-ema26[i]
    if i==0 or np.isnan(signal_[i-1]): signal_[i]=macd_line
    else: signal_[i] = signal_[i-1]*(1-k9)+macd_line*k9
    if i>=33: macd_hist_raw[i] = macd_line - signal_[i]

# Raw VNI 8 factors
cmf_raw = vni["D_CMF"].values.astype(float)
pe_raw  = vni["VNINDEX_PE"].values.astype(float)
vni["f_P3M"]=p3m_raw; vni["f_P1M"]=p1m_raw; vni["f_MA200"]=ma200_dev_raw
vni["f_RSI"]=rsi_raw; vni["f_MACD"]=macd_hist_raw; vni["f_CMF"]=cmf_raw
vni["f_PE"] = pe_raw
# Breadth — from EW universe via ew_out
vni = vni.merge(ew_out[["time","f_Breadth"]], on="time", how="left")

FACTOR_KEYS_8 = ["P3M","P1M","MA200","RSI","MACD","CMF","Breadth","PE"]
W_8 = dict(W_BASE_7); W_8["PE"] = W_PE
ranks_raw = {}
for k in FACTOR_KEYS_8:
    print(f"  Rank {k} (raw VNI)...")
    ranks_raw[k] = expanding_pct_rank(vni[f"f_{k}"].values, MIN_LB)

score_raw_v = np.full(n_full_raw, np.nan)
for t in range(n_full_raw):
    avail = {k: ranks_raw[k][t] for k in FACTOR_KEYS_8 if not np.isnan(ranks_raw[k][t])}
    if len(avail) < MIN_FACTORS: continue
    ws = sum(W_8[k] for k in avail)
    score_raw_v[t] = sum(avail[k]*W_8[k] for k in avail)/ws
r_score_raw = expanding_pct_rank(score_raw_v, MIN_LB)
vni["r_score_raw"] = r_score_raw

# EW factors on Composite Close (df has post-EW_START with close=close_ew_scaled, pre with raw)
close_ew = df["Close"].values.astype(float)
n_full = len(close_ew)
p3m_ew = lagged_return(close_ew, 60); p1m_ew = lagged_return(close_ew, 20)
ma200_ew = pd.Series(close_ew).rolling(200, min_periods=200).mean().values
ma200_dev_ew = np.where((ma200_ew>0)&~np.isnan(ma200_ew), close_ew/ma200_ew-1, np.nan)

rsi_ew = np.full(n_full,np.nan); avg_u=avg_d=np.nan
for i in range(1, n_full):
    diff = close_ew[i]-close_ew[i-1]
    if np.isnan(diff): continue
    u = max(diff,0.0); d = max(-diff,0.0)
    if np.isnan(avg_u):
        if i >= period:
            gns = [max(close_ew[j]-close_ew[j-1],0) for j in range(1,period+1)]
            lss = [max(close_ew[j-1]-close_ew[j],0) for j in range(1,period+1)]
            avg_u = np.mean(gns); avg_d = np.mean(lss)
            if (avg_u+avg_d)>0: rsi_ew[i] = avg_u/(avg_u+avg_d)
    else:
        avg_u = (avg_u*(period-1)+u)/period
        avg_d = (avg_d*(period-1)+d)/period
        if (avg_u+avg_d)>0: rsi_ew[i] = avg_u/(avg_u+avg_d)

ema12_e = np.full(n_full,np.nan); ema26_e = np.full(n_full,np.nan)
signal_e = np.full(n_full,np.nan); macd_hist_ew = np.full(n_full,np.nan)
for i in range(n_full):
    if np.isnan(close_ew[i]): continue
    if i==0 or np.isnan(ema12_e[i-1]): ema12_e[i]=close_ew[i]; ema26_e[i]=close_ew[i]
    else:
        ema12_e[i] = ema12_e[i-1]*(1-k12)+close_ew[i]*k12
        ema26_e[i] = ema26_e[i-1]*(1-k26)+close_ew[i]*k26
    macd_line = ema12_e[i]-ema26_e[i]
    if i==0 or np.isnan(signal_e[i-1]): signal_e[i]=macd_line
    else: signal_e[i] = signal_e[i-1]*(1-k9)+macd_line*k9
    if i>=33: macd_hist_ew[i] = macd_line - signal_e[i]

cmf_ew = df["D_CMF"].values.astype(float)
df["f_P3M"]=p3m_ew; df["f_P1M"]=p1m_ew; df["f_MA200"]=ma200_dev_ew
df["f_RSI"]=rsi_ew; df["f_MACD"]=macd_hist_ew; df["f_CMF"]=cmf_ew
df["f_Breadth"] = df["breadth"]

FACTOR_KEYS_7 = ["P3M","P1M","MA200","RSI","MACD","CMF","Breadth"]
ranks_ew = {}
for k in FACTOR_KEYS_7:
    print(f"  Rank {k} (EW composite)...")
    ranks_ew[k] = expanding_pct_rank(df[f"f_{k}"].values, MIN_LB)
score_ew_v = np.full(n_full, np.nan)
for t in range(n_full):
    avail = {k: ranks_ew[k][t] for k in FACTOR_KEYS_7 if not np.isnan(ranks_ew[k][t])}
    if len(avail) < MIN_FACTORS: continue
    ws = sum(W_BASE_7[k] for k in avail)
    score_ew_v[t] = sum(avail[k]*W_BASE_7[k] for k in avail)/ws
r_score_ew = expanding_pct_rank(score_ew_v, MIN_LB)
df["r_score_ew"] = r_score_ew

# ─────────────────────────────────────────────────────────────────────
# Step 7: Merge into VNI timeline + dynamic α blend
# ─────────────────────────────────────────────────────────────────────
print("\n[7] Merge raw VNI + EW + concentration; dynamic α")
master = vni[["time","Close","VNINDEX_PE","r_score_raw"]].copy()
master = master.merge(df[["time","r_score_ew"]], on="time", how="left")
master = master.merge(conc[["time","concentration_score"]], on="time", how="left")

# Smooth concentration
cs = master["concentration_score"].values
cs_ema = np.full(len(cs), np.nan)
for t in range(len(cs)):
    v = cs[t]; prev = cs_ema[t-1] if t>0 else np.nan
    if np.isnan(v): cs_ema[t] = prev
    elif np.isnan(prev): cs_ema[t] = v
    else: cs_ema[t] = CONC_EMA*v + (1-CONC_EMA)*prev
master["concentration_smooth"] = cs_ema

def alpha_from_c(c):
    if np.isnan(c): return 1.0
    return max(0.3, min(1.0, 1.0 - 2.0*max(0, c-0.5)))
master["alpha"] = master["concentration_smooth"].apply(alpha_from_c)

a = master["alpha"].values
r_raw = master["r_score_raw"].values
r_ew  = master["r_score_ew"].values
r_dual = np.where(np.isnan(r_ew), r_raw,
                  np.where(np.isnan(r_raw), r_ew, a*r_raw + (1-a)*r_ew))

# ─────────────────────────────────────────────────────────────────────
# Step 8: Full Tinh Tế pipeline
# ─────────────────────────────────────────────────────────────────────
print("\n[8] EMA → classify → overrides → v2g gate → s3 smoothing")
n = len(master)
close = master["Close"].values.astype(float)
pe = master["VNINDEX_PE"].values.astype(float)
spy = n / ((master["time"].iloc[-1] - master["time"].iloc[0]).days / 365.25)

rs_ema = np.full(n, np.nan)
for t in range(n):
    v=r_dual[t]; prev=rs_ema[t-1] if t>0 else np.nan
    if np.isnan(v): rs_ema[t]=prev
    elif np.isnan(prev): rs_ema[t]=v
    else: rs_ema[t] = EMA_ALPHA*v + (1-EMA_ALPHA)*prev

def classify_raw(rs):
    if np.isnan(rs): return 3
    if rs<0.10: return 1
    if rs<0.20: return 2
    if rs<0.70: return 3
    if rs<0.90: return 4
    return 5
state_raw = np.array([classify_raw(r) for r in rs_ema])

pe_p90 = np.full(n, np.nan)
for t in range(n):
    h = pe[:t+1]; v = h[~np.isnan(h)]
    if len(v)>=60: pe_p90[t] = np.nanpercentile(v, 90)
rmx = np.maximum.accumulate(np.where(np.isnan(close), 0, close))
dd_arr = np.where(rmx>0, close/rmx-1, 0.0)
daily_ret = np.full(n, np.nan)
for i in range(1, n):
    if close[i-1]>0 and not np.isnan(close[i-1]) and not np.isnan(close[i]):
        daily_ret[i] = close[i]/close[i-1]-1
vol20 = np.full(n, np.nan)
for i in range(20, n):
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
    if dd_arr[i] < -0.25 and s>=4: s=3
    if not np.isnan(avg_vol_exp[i]) and not np.isnan(vol20[i]) and vol20[i]>1.5*avg_vol_exp[i] and s==5: s=4
    state_ov[i] = s

# BearDvg/BullDvg/E2/S2_bull from raw VNI dynamics
def roll_max(a,w): return pd.Series(a).rolling(w, min_periods=1).max().values
def roll_min(a,w): return pd.Series(a).rolling(w, min_periods=1).min().values
def arg_close_max(rsi_a, c_a, w):
    out = np.full(len(rsi_a), np.nan)
    for i in range(len(rsi_a)):
        lo = max(0, i-w+1); seg = rsi_a[lo:i+1]
        if np.all(np.isnan(seg)): continue
        k = int(np.nanargmax(seg)); out[i] = c_a[lo+k]
    return out
def arg_macd_max(rsi_a, m_a, w):
    out = np.full(len(rsi_a), np.nan)
    for i in range(len(rsi_a)):
        lo = max(0, i-w+1); seg = rsi_a[lo:i+1]
        if np.all(np.isnan(seg)): continue
        k = int(np.nanargmax(seg)); out[i] = m_a[lo+k]
    return out
def arg_close_min(rsi_a, c_a, w):
    out = np.full(len(rsi_a), np.nan)
    for i in range(len(rsi_a)):
        lo = max(0, i-w+1); seg = rsi_a[lo:i+1]
        if np.all(np.isnan(seg)): continue
        k = int(np.nanargmin(seg)); out[i] = c_a[lo+k]
    return out

D_RSI = rsi_raw  # use raw VNI RSI for divergence signals (fundamental market dynamics)
close_for_dvg = close_raw
D_RSI_T1W = np.concatenate([[np.nan]*5, D_RSI[:-5]])
D_RSI_Max1W = roll_max(D_RSI,5); D_RSI_Max3M = roll_max(D_RSI,60)
D_RSI_Min1W = roll_min(D_RSI,5); D_RSI_Min3M = roll_min(D_RSI,60)
D_RSI_Max1W_C = arg_close_max(D_RSI, close_for_dvg, 5); D_RSI_Max3M_C = arg_close_max(D_RSI, close_for_dvg, 60)
D_RSI_Max1W_M = arg_macd_max(D_RSI, macd_hist_raw, 5); D_RSI_Max3M_M = arg_macd_max(D_RSI, macd_hist_raw, 60)
D_RSI_Min1W_C = arg_close_min(D_RSI, close_for_dvg, 5)
D_RSI_MinT3 = roll_min(D_RSI, 3)
C_L1W = close_for_dvg/np.where(roll_min(close_for_dvg,5)>0, roll_min(close_for_dvg,5), 1)
C_L1M = close_for_dvg/np.where(roll_min(close_for_dvg,20)>0, roll_min(close_for_dvg,20), 1)
mask_d = (vni["time"]>=DVG_MASK_START).values

with np.errstate(divide='ignore', invalid='ignore'):
    bear1 = ((D_RSI_Max1W/np.where(D_RSI>0,D_RSI,np.nan)>1.044) & (D_RSI_Max3M>0.74) &
             (D_RSI_Max1W<0.72) & (D_RSI_Max1W>0.61) &
             (D_RSI_Max1W_C/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan)>1.028) &
             (D_RSI_Max3M_M/np.where(D_RSI_Max1W_M!=0,D_RSI_Max1W_M,np.nan)>1.11) &
             (macd_hist_raw<0) & (close_for_dvg/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan)>0.96) &
             (D_RSI_MinT3>0.43) & (cmf_raw<0.13) & mask_d)
    bear2 = ((D_RSI_Max1W/np.where(D_RSI>0,D_RSI,np.nan)>1.016) & (D_RSI_Max3M>0.77) &
             (D_RSI_Max1W<0.79) & (D_RSI_Max1W>0.60) &
             (D_RSI_Max1W_C/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan)>1.008) &
             (D_RSI_Max3M_M/np.where(D_RSI_Max1W_M!=0,D_RSI_Max1W_M,np.nan)>1.10) &
             (macd_hist_raw<0) & (close_for_dvg/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan)>0.97) &
             (D_RSI_MinT3>0.50) & (cmf_raw<0.15) & mask_d)
    bull1 = ((D_RSI_Min1W/np.where(D_RSI_Min3M>0,D_RSI_Min3M,np.nan)>0.90) & (D_RSI_Min1W<0.60) &
             (D_RSI_Min3M<0.40) & (D_RSI_Min1W_C/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan)<1.15) &
             (macd_hist_raw>0) & (D_RSI_MinT3<0.50) & (D_RSI_Max1W<0.48) &
             (D_RSI/np.where(D_RSI_T1W>0,D_RSI_T1W,np.nan)>1.12) & (cmf_raw>0) &
             (C_L1M<1.21) & (C_L1W<1.05) & mask_d)
    bull2 = ((D_RSI_Min1W/np.where(D_RSI_Min3M>0,D_RSI_Min3M,np.nan)>0.92) & (D_RSI_Min1W<0.52) &
             (D_RSI_Min3M<0.38) & (D_RSI_Min1W_C/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan)<1.10) &
             (macd_hist_raw>0) & (D_RSI_MinT3<0.56) & (D_RSI_Max1W<0.64) &
             (D_RSI/np.where(D_RSI_T1W>0,D_RSI_T1W,np.nan)>1.10) & (cmf_raw>0) &
             (C_L1M<1.20) & (C_L1W<1.025) & mask_d)
bear_mask = np.nan_to_num(bear1,nan=0).astype(bool) | np.nan_to_num(bear2,nan=0).astype(bool)
bull_mask = np.nan_to_num(bull1,nan=0).astype(bool) | np.nan_to_num(bull2,nan=0).astype(bool)

E2 = np.zeros(n, dtype=bool)
for i in range(5, n):
    if (dd_arr[i] < -0.15
        and close[i] > close[i-5]*1.05
        and not np.isnan(rsi_raw[i]) and not np.isnan(rsi_raw[i-5])
        and rsi_raw[i] > rsi_raw[i-5]*1.15
        and not np.isnan(cmf_raw[i]) and cmf_raw[i] > 0):
        E2[i] = True

pe_slope = np.full(n, np.nan)
SLOPE_WIN = 120
for t in range(SLOPE_WIN, n):
    seg = pe[t-SLOPE_WIN+1:t+1]
    valid = ~np.isnan(seg)
    if valid.sum() >= 60:
        x = np.arange(SLOPE_WIN)[valid]; y = seg[valid]
        if len(x) > 1 and np.var(x) > 0:
            slope = (np.mean(x*y) - np.mean(x)*np.mean(y)) / np.var(x)
            pe_slope[t] = slope / np.nanmean(seg)
s2_bull = (pe_slope < -0.0010) & ~np.isnan(pe_slope)
print(f"  BearDvg: {bear_mask.sum()} | BullDvg: {bull_mask.sum()} | E2: {E2.sum()} | S2_bull: {s2_bull.sum()}")

# v2g gate
state_v2g = state_ov.copy()
ga = False; gs = -1; n_open=n_close=0
for i in range(n):
    if bear_mask[i]:
        if not ga: ga=True; gs=i; n_open+=1
        else: gs=i
    if ga:
        if state_v2g[i] > 1: state_v2g[i] = 1
        sessions_in = i - gs
        if sessions_in >= GATE_MIN_V2G:
            if bull_mask[i] or E2[i] or s2_bull[i]: ga=False; n_close+=1
print(f"  Gate events: {n_open} open / {n_close} close")

# s3 smoothing
def rolling_mode(states, window):
    if window <= 1: return states.copy()
    out = states.copy()
    for t in range(window-1, len(states)):
        win = states[t-window+1:t+1]
        vals, counts = np.unique(win, return_counts=True)
        mc = counts.max(); cand = vals[counts==mc]
        for v in reversed(win):
            if v in cand: out[t]=v; break
    return out
def min_stay_filter(states, min_days):
    if min_days <= 1: return states.copy()
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

state_final = rolling_mode(state_v2g, MODE_WIN_S3)
state_final = min_stay_filter(state_final, MIN_STAY_S3)

master["state_raw"] = state_raw
master["state"]     = state_final

# Save outputs
staging_out = pd.DataFrame({
    "time": master["time"].dt.strftime("%Y-%m-%d"),
    "state": master["state"].astype(int),
    "state_raw": master["state_raw"].astype(int),
})
staging_out.to_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_full_history.csv"), index=False)
master[["time","Close","concentration_smooth","alpha","r_score_raw","r_score_ew",
        "state_raw","state"]].to_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_full_history_diag.csv"), index=False)

# Summary
print("\n" + "="*70); print("STRESS TEST SUMMARY"); print("="*70)
sub_stress = master[(master["time"]>="2007-01-01") & (master["time"]<="2013-12-31")]
print(f"\nState distribution 2007-2013 ({len(sub_stress)} sessions):")
dist = sub_stress["state"].value_counts(normalize=True).sort_index() * 100
for s in [1,2,3,4,5]:
    print(f"  {STATE_NAMES[s]:<10} {dist.get(s, 0.0):>5.1f}%")

# Notable events
events = [
    ("2007-03-12", "Pre-GFC peak ~1170"),
    ("2008-03-13", "First crash leg 647"),
    ("2008-12-15", "GFC bottom ~315"),
    ("2009-09-08", "Recovery peak 624"),
    ("2009-12-15", "Late 2009 retrace"),
    ("2011-08-19", "Inflation crisis bottom ~400"),
    ("2012-09-13", "2012 correction ~390"),
    ("2013-12-31", "End stress test 505"),
]
print(f"\nKey events:")
for d, label in events:
    row = master[master["time"] == pd.Timestamp(d)]
    if len(row) == 0:
        idx = (master["time"] - pd.Timestamp(d)).abs().idxmin()
        row = master.iloc[[idx]]
    r = row.iloc[0]
    sname = STATE_NAMES.get(int(r['state']), '?')
    cs_v = r['concentration_smooth'] if not pd.isna(r['concentration_smooth']) else float('nan')
    print(f"  {r['time'].strftime('%Y-%m-%d')} {label:<32}  state={sname:<8}  α={r['alpha']:.2f}  c={cs_v:.2f}")

print(f"\n→ vnindex_5state_tam_quan_full_history.csv (stress-test-ready)")
