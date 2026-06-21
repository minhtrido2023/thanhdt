# -*- coding: utf-8 -*-
"""
build_v3_4_bull_aware.py
========================
v3.4 = v3.1 + "bull-regime conditional US override" + RSI gate + conc filter (v3.3b).

Key change from v3.3b:
  • When BTC (Bull Trend Confirmed) is True at day t → US override is BYPASSED.
    Use v3 staging state instead (pre-US-cap).
    Rationale: 17-43 US override fires post-2014 happened during confirmed bull,
    and forward T+60 mean was +13-17% with 100% positive — override was 100% wrong.
  • RSI gate + conc filter applied on top (same as v3.3b).

3 variants tested with different BTC definitions:
  v3.4a: BTC = BTC_RP_loose (P30 OR R3M) — broadest, fires ~38% post-2014
  v3.4b: BTC = BTC_R6M  (return-based stricter) — ~22% coverage
  v3.4c: BTC = BTC_RP   (P60 AND R6M) — strictest, ~15% coverage

Output: vnindex_5state_tam_quan_v3_4{x}_full_history.csv
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}
RSI_THR = 55
CONC_THR = 0.55

# Load
v31 = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_1_full_history.csv"))
v31["time"] = pd.to_datetime(v31["time"]); v31 = v31.sort_values("time").reset_index(drop=True)

v3_stg = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_dual_v3_staging.csv"))
v3_stg["time"] = pd.to_datetime(v3_stg["time"])
v3_stg = v3_stg.rename(columns={"state": "state_v3"})

dr  = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_dual_v3_full.csv"))
dr["time"] = pd.to_datetime(dr["time"])

diag = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_1_diag.csv"))
diag["time"] = pd.to_datetime(diag["time"])

df = v31.merge(v3_stg[["time","state_v3"]], on="time", how="left").merge(
    dr[["time","Close","concentration_smooth"]], on="time", how="left").merge(
    diag[["time","override_fired"]], on="time", how="left").reset_index(drop=True)

n = len(df); close = df["Close"].values
v31_state = df["state"].values.astype(int)
v3_state  = df["state_v3"].values.astype(int)
conc = df["concentration_smooth"].values

# RSI(14)
def rsi14(c):
    delta = np.diff(c, prepend=c[0])
    up   = np.where(delta>0, delta, 0.0); down = np.where(delta<0, -delta, 0.0)
    out = np.full(len(c), np.nan)
    for i in range(14, len(c)):
        gain = up[i-13:i+1].mean(); loss = down[i-13:i+1].mean()
        rs = gain/loss if loss>0 else 100; out[i] = 100 - 100/(1+rs)
    return out
rsi = rsi14(close)

# MA200 + returns for BTC
ma200 = pd.Series(close).rolling(200).mean().values
ma200_dev = close/ma200 - 1
ret_60d  = pd.Series(close).pct_change(60).values
ret_120d = pd.Series(close).pct_change(120).values

# Consecutive day counters
def consec(mask):
    out = np.zeros(len(mask), dtype=int)
    for t in range(len(mask)):
        if mask[t]: out[t] = (out[t-1] + 1) if t > 0 else 1
    return out

p_above_5 = (ma200_dev > 0.05) & ~np.isnan(ma200_dev)
consec_p5 = consec(p_above_5)

BTC = {
    "BTC_P30":    consec_p5 >= 30,
    "BTC_P60":    consec_p5 >= 60,
    "BTC_R6M":    ((ret_120d > 0.15) & (ma200_dev > 0)) & ~np.isnan(ret_120d),
    "BTC_R3M":    ((ret_60d  > 0.08) & (ma200_dev > 0)) & ~np.isnan(ret_60d),
}
BTC["BTC_RP"]       = BTC["BTC_P60"] & BTC["BTC_R6M"]
BTC["BTC_RP_loose"] = BTC["BTC_P30"] | BTC["BTC_R3M"]

# Smoothing
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

def build_v34(btc_arr, label):
    """
    Build v3.4 state series:
      1. Base state: use v3_state (pre-override) when BTC is True
                     use v31_state (with override) when BTC is False
      2. Re-smooth (mode3 + ms2)
      3. Apply RSI gate + conc filter (v3.3b layer)
    """
    # Step 1: blend
    base = np.where(btc_arr, v3_state, v31_state)
    n_overrides_bypassed = int(((v3_state != v31_state) & btc_arr).sum())
    print(f"  {label}: bypassed {n_overrides_bypassed} US-override days where BTC=True")

    # Step 2: re-smooth
    base = rolling_mode(base, 3)
    base = min_stay_filter(base, 2)

    # Step 3: RSI gate + conc filter
    result = base.copy()
    blocked = False; blocked_at = None
    for t in range(1, n):
        cur = base[t]; prev = base[t-1]; cr = rsi[t]; cc = conc[t]
        if blocked:
            if (cr is None) or np.isnan(cr) or (cr < RSI_THR):
                blocked=False; result[t]=cur
            elif cur >= blocked_at:
                blocked=False; result[t]=cur
            elif (blocked_at - cur) >= 2:
                blocked=False; result[t]=cur
            else:
                result[t] = blocked_at
        else:
            is_1step = (prev - cur == 1)
            rsi_ok = (cr is not None) and (not np.isnan(cr)) and (cr >= RSI_THR)
            conc_ok = (cc is None) or np.isnan(cc) or (cc <= CONC_THR)
            if is_1step and rsi_ok and conc_ok:
                blocked = True; blocked_at = prev; result[t] = blocked_at
    return result

# Build 3 variants
print("Building v3.4 variants ...")
for suffix, btc_key in [("a", "BTC_RP_loose"), ("b", "BTC_R6M"), ("c", "BTC_RP")]:
    btc_arr = BTC[btc_key]
    result = build_v34(btc_arr, f"v3.4{suffix} ({btc_key})")
    n_trans = int((np.diff(result)!=0).sum())
    elev_days = int((result > v31_state).sum())
    print(f"    transitions: {n_trans} | elevated days vs v3.1: {elev_days}")

    out = pd.DataFrame({"time": df["time"].dt.strftime("%Y-%m-%d"),
                        "state": result.astype(int),
                        "state_raw": df["state_raw"].astype(int)})
    out_path = os.path.join(WORKDIR, f"vnindex_5state_tam_quan_v3_4{suffix}_full_history.csv")
    out.to_csv(out_path, index=False)
    print(f"    ✓ Saved {os.path.basename(out_path)}\n")

# Print distribution comparison
print(f"\n{'State':<10}{'v3.1':>8}{'v3.3b':>8}{'v3.4a':>8}{'v3.4b':>8}{'v3.4c':>8}")
v33b = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_3b_full_history.csv"))["state"].values
v34a = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_4a_full_history.csv"))["state"].values
v34b = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_4b_full_history.csv"))["state"].values
v34c = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_4c_full_history.csv"))["state"].values
for s in [1,2,3,4,5]:
    p1 = (v31_state==s).mean()*100
    p33b = (v33b==s).mean()*100
    p4a = (v34a==s).mean()*100; p4b = (v34b==s).mean()*100; p4c = (v34c==s).mean()*100
    print(f"  {STATE_NAMES[s]:<8}{p1:>7.1f}%{p33b:>7.1f}%{p4a:>7.1f}%{p4b:>7.1f}%{p4c:>7.1f}%")
