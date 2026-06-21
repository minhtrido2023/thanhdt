# -*- coding: utf-8 -*-
"""
F_System Accuracy Analysis:
  - Win rate / avg return của từng state khi giữ position
  - Accuracy của từng loại transition (chuyển từ state X → Y)
  - So sánh H-smoothing vs F-smoothing
  - Phân tích theo từng giai đoạn IS (2011-2020) và OOS (2021+)
Output: in ra console + f_system_accuracy.html
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

# ── Load data ────────────────────────────────────────────────────────────────
vni = pd.read_csv(WORKDIR + "/data/VNINDEX.csv", low_memory=False)
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
for col in ["Open","High","Low","Close","Volume","VNINDEX_PE",
            "D_RSI","D_RSI_T1W","D_RSI_Max1W","D_RSI_Max3M",
            "D_RSI_Min1W","D_RSI_Min3M","D_RSI_Max1W_Close",
            "D_RSI_Max3M_Close","D_RSI_Max3M_MACD","D_RSI_Max1W_MACD",
            "D_RSI_Min1W_Close","D_RSI_MinT3","D_MACDdiff","D_CMF","C_L1M","C_L1W","VN30"]:
    if col in vni.columns: vni[col] = pd.to_numeric(vni[col], errors="coerce")
if "breadth" not in vni.columns: vni["breadth"] = np.nan

# Underlying: VN30 scaled to VNINDEX base
vn30_raw  = vni["VN30"].values if "VN30" in vni.columns else np.full(len(vni), np.nan)
vnidx_raw = vni["Close"].values.copy()
vn30_start_idx = np.where(~np.isnan(vn30_raw))[0]
if len(vn30_start_idx) > 0:
    s = vn30_start_idx[0]
    scale = vnidx_raw[s] / vn30_raw[s]
    underlying = vnidx_raw.copy()
    for i in range(s, len(vni)):
        if not np.isnan(vn30_raw[i]):
            underlying[i] = vn30_raw[i] * scale
else:
    underlying = vnidx_raw.copy()

close = vni["Close"].values.copy()
high  = vni["High"].values.copy()
low   = vni["Low"].values.copy()
vol   = vni["Volume"].values.copy()
n     = len(close)
cal_days = (vni["time"].iloc[-1] - vni["time"].iloc[0]).days
SPY = n / (cal_days / 365.25)

# ── Signal pipeline (identical to H_System / F_System) ──────────────────────
def _ema(arr, k):
    out = np.full(len(arr), np.nan)
    for i in range(len(arr)):
        out[i] = arr[i] if (i==0 or np.isnan(out[i-1])) else out[i-1]*(1-k)+arr[i]*k
    return out

def _rank(arr, min_lb=252):
    out = np.full(len(arr), np.nan)
    for t in range(len(arr)):
        if np.isnan(arr[t]): continue
        v = arr[:t+1]; v = v[~np.isnan(v)]
        if len(v) >= min_lb: out[t] = np.sum(v <= arr[t]) / len(v)
    return out

p3m = np.full(n, np.nan)
for i in range(60, n):
    if close[i-60] > 0: p3m[i] = close[i]/close[i-60] - 1
p1m = np.full(n, np.nan)
for i in range(20, n):
    if close[i-20] > 0: p1m[i] = close[i]/close[i-20] - 1
ma200 = pd.Series(close).rolling(200, min_periods=200).mean().values
ma200_dev = np.where((ma200>0) & ~np.isnan(ma200), close/ma200 - 1, np.nan)
rsi = np.full(n, np.nan); au = ad = np.nan
for i in range(1, n):
    d = close[i]-close[i-1]; u = max(d,0); dn = max(-d,0)
    if np.isnan(au):
        if i >= 14:
            au = np.mean([max(close[j]-close[j-1],0) for j in range(1,15)])
            ad = np.mean([max(close[j-1]-close[j],0) for j in range(1,15)])
            if au+ad > 0: rsi[i] = au/(au+ad)
    else:
        au = (au*13+u)/14; ad = (ad*13+dn)/14
        if au+ad > 0: rsi[i] = au/(au+ad)
e12 = _ema(close, 2/13); e26 = _ema(close, 2/27)
macd_l = e12-e26; sig9 = _ema(macd_l, 2/10)
macd_hist = np.where(np.arange(n) >= 33, macd_l-sig9, np.nan)
hl = high-low; mfm = np.where(hl>0, ((close-low)-(high-close))/hl, 0.0)
cmf = np.full(n, np.nan)
for i in range(14, n):
    vs = np.sum(vol[i-14:i])
    if vs > 0: cmf[i] = np.sum(mfm[i-14:i]*vol[i-14:i]) / vs
br_arr = vni["breadth"].values

W = {"P3M":0.30,"P1M":0.10,"MA200":0.15,"RSI":0.15,"MACD":0.10,"CMF":0.08,"Breadth":0.12}
raw = {"P3M":p3m,"P1M":p1m,"MA200":ma200_dev,"RSI":rsi,"MACD":macd_hist,"CMF":cmf,"Breadth":br_arr}
ranks = {k: _rank(v) for k,v in raw.items()}
score = np.full(n, np.nan)
for t in range(n):
    av = {k: ranks[k][t] for k in ranks if not np.isnan(ranks[k][t])}
    if len(av) >= 3:
        ws = sum(W[k] for k in av)
        score[t] = sum(av[k]*W[k] for k in av) / ws
r_score = _rank(score)
r_ema = np.full(n, np.nan)
for t in range(n):
    v = r_score[t]; p = r_ema[t-1] if t > 0 else np.nan
    r_ema[t] = v if np.isnan(p) else (p if np.isnan(v) else 0.40*v + 0.60*p)

pe_arr  = vni["VNINDEX_PE"].values.copy()
pe_p90  = np.full(n, np.nan)
for t in range(n):
    h = pe_arr[:t+1]; h = h[~np.isnan(h)]
    if len(h) >= 60: pe_p90[t] = np.nanpercentile(h, 90)
rm_c   = np.maximum.accumulate(np.where(np.isnan(close), 0, close))
dd_raw = np.where(rm_c > 0, close/rm_c-1, 0.0)
dr = np.full(n, np.nan)
for i in range(1, n):
    if close[i-1] > 0: dr[i] = close[i]/close[i-1]-1
v20_a = np.full(n, np.nan)
for i in range(20, n):
    w2 = dr[i-20:i]; w2 = w2[~np.isnan(w2)]
    if len(w2) >= 15: v20_a[i] = np.std(w2)*np.sqrt(SPY)
avg_vol_a = np.full(n, np.nan)
for t in range(n):
    h = v20_a[:t+1]; h = h[~np.isnan(h)]
    if len(h) >= 60: avg_vol_a[t] = np.mean(h)

def classify(rs):
    if np.isnan(rs): return 3
    if rs < 0.10: return 1
    elif rs < 0.20: return 2
    elif rs < 0.70: return 3
    elif rs < 0.90: return 4
    else: return 5

st = np.array([classify(r) for r in r_ema])
for i in range(n):
    s = st[i]
    if not np.isnan(pe_p90[i]) and not np.isnan(pe_arr[i]) and pe_arr[i] > pe_p90[i] and s == 5: s = 4
    if dd_raw[i] < -0.25 and s >= 4: s = 3
    if not np.isnan(avg_vol_a[i]) and not np.isnan(v20_a[i]) and v20_a[i] > 1.5*avg_vol_a[i] and s == 5: s = 4
    st[i] = s

def _s(c): return vni[c] if c in vni.columns else pd.Series(np.nan, index=vni.index)
_mask = vni["time"] >= "2011-01-01"
_DR=_s("D_RSI");_DRT=_s("D_RSI_T1W");_DM1W=_s("D_RSI_Max1W");_DM3M=_s("D_RSI_Max3M")
_DN1W=_s("D_RSI_Min1W");_DN3M=_s("D_RSI_Min3M");_DM1WC=_s("D_RSI_Max1W_Close")
_DM3MC=_s("D_RSI_Max3M_Close");_DM3MM=_s("D_RSI_Max3M_MACD");_DM1WM=_s("D_RSI_Max1W_MACD")
_DN1WC=_s("D_RSI_Min1W_Close");_DMT3=_s("D_RSI_MinT3");_DMACD=_s("D_MACDdiff")
_DCMF=_s("D_CMF");_CL1M=_s("C_L1M");_CL1W=_s("C_L1W")
bear_mask = (
 ((_DM1W/_DR>1.044)&(_DM3M>0.74)&(_DM1W<0.72)&(_DM1W>0.61)&
  (_DM1WC/_DM3MC>1.028)&(_DM3MM/_DM1WM>1.11)&(_DMACD<0)&
  (vni["Close"]/_DM3MC>0.96)&(_DMT3>0.43)&(_DCMF<0.13)&_mask)
 |((_DM1W/_DR>1.016)&(_DM3M>0.77)&(_DM1W<0.79)&(_DM1W>0.60)&
  (_DM1WC/_DM3MC>1.008)&(_DM3MM/_DM1WM>1.10)&(_DMACD<0)&
  (vni["Close"]/_DM3MC>0.97)&(_DMT3>0.50)&(_DCMF<0.15)&_mask)
).values.astype(bool)
bull_mask = (
 ((_DN1W/_DN3M>0.90)&(_DN1W<0.60)&(_DN3M<0.40)&(_DN1WC/_DM3MC<1.15)&
  (_DMACD>0)&(_DMT3<0.50)&(_DM1W<0.48)&(_DR/_DRT>1.12)&(_DCMF>0)&
  (_CL1M<1.21)&(_CL1W<1.05)&_mask)
 |((_DN1W/_DN3M>0.92)&(_DN1W<0.52)&(_DN3M<0.38)&(_DN1WC/_DM3MC<1.10)&
  (_DMACD>0)&(_DMT3<0.56)&(_DM1W<0.64)&(_DR/_DRT>1.12)&(_DCMF>0)&
  (_CL1M<1.20)&(_CL1W<1.025)&_mask)
).values.astype(bool)
pe_rank = np.full(n, np.nan)
for t in range(n):
    if np.isnan(pe_arr[t]): continue
    h = pe_arr[:t+1]; h = h[~np.isnan(h)]
    if len(h) >= 60: pe_rank[t] = np.sum(h <= pe_arr[t]) / len(h)
p3m_rank = ranks["P3M"]
streak = np.zeros(n, dtype=bool); _k = 0
for i in range(n):
    if not np.isnan(r_ema[i]) and r_ema[i] > 0.65: _k += 1
    else: _k = 0
    if _k >= 10: streak[i] = True
gate_active = False; gate_start = -1; st_dvg = st.copy()
for i in range(n):
    if bear_mask[i]: gate_active = True; gate_start = i
    if gate_active:
        if st_dvg[i] > 1: st_dvg[i] = 1
        if i - gate_start >= 60:
            p3_ok = (not np.isnan(p3m_rank[i])) and p3m_rank[i] > 0.45
            pe_ok = (not np.isnan(pe_rank[i])) and pe_rank[i] < 0.80
            if bull_mask[i] or (p3_ok and pe_ok) or bool(streak[i]): gate_active = False

def rolling_mode(states, w=15):
    out = states.copy()
    for t in range(w-1, len(states)):
        ww = states[t-w+1:t+1]; vs, cs = np.unique(ww, return_counts=True)
        cands = vs[cs == cs.max()]
        for v in reversed(ww):
            if v in cands: out[t] = v; break
    return out

def min_stay_filter(states, m=7):
    out = states.copy(); changed = True
    while changed:
        changed = False; i = 0
        while i < len(out):
            j = i+1
            while j < len(out) and out[j] == out[i]: j += 1
            if j - i < m:
                fill = out[i-1] if i > 0 else (out[j] if j < len(out) else out[i])
                out[i:j] = fill; changed = True
            i = j
    return out

st_smooth_H = min_stay_filter(rolling_mode(st_dvg, 15), 7)  # H-canonical
st_smooth_F = min_stay_filter(rolling_mode(st_dvg,  5), 3)  # F-lighter

STATE_NAMES = {1:"CRISIS", 2:"BEAR", 3:"NEUTRAL", 4:"BULL", 5:"EX-BULL"}
STATE_COLOR  = {1:"#d62728", 2:"#ff7f0e", 3:"#aec7e8", 4:"#2ca02c", 5:"#1f77b4"}
POS_F  = {1:-0.30, 2:-0.10, 3:+0.50, 4:+1.00, 5:+1.50}  # NE=0.50 / F-smoothing (OOS best)
POS_H  = {1:-0.30, 2:-0.10, 3:+0.20, 4:+1.00, 5:+1.50}  # NE=0.20 / H-smoothing (IS best)

# ── Build analysis dataframe ─────────────────────────────────────────────────
dates = vni["time"].values
ret_und = np.full(n, np.nan)
for i in range(1, n):
    if underlying[i-1] > 0: ret_und[i] = underlying[i]/underlying[i-1] - 1

def forward_ret(ret_arr, horizons):
    """Compound forward returns over horizons (list of sessions)."""
    out = {}
    for h in horizons:
        fwd = np.full(n, np.nan)
        for t in range(n - h):
            r = 1.0
            for k in range(1, h+1):
                if not np.isnan(ret_arr[t+k]): r *= (1+ret_arr[t+k])
            fwd[t] = r - 1
        out[h] = fwd
    return out

HORIZONS = [5, 10, 20, 60]  # T+1W, T+2W, T+1M, T+3M
fwd = forward_ret(ret_und, HORIZONS)

# Build base dataframe
df_H = pd.DataFrame({
    "date":  pd.to_datetime(dates),
    "state": st_smooth_H,
    "pos":   [POS_H[s] for s in st_smooth_H],
    "ret1":  ret_und,
})
df_F = pd.DataFrame({
    "date":  pd.to_datetime(dates),
    "state": st_smooth_F,
    "pos":   [POS_F[s] for s in st_smooth_F],
    "ret1":  ret_und,
})
for h in HORIZONS:
    df_H[f"fwd{h}"] = fwd[h]
    df_F[f"fwd{h}"] = fwd[h]

# Period masks
IS_START  = "2011-01-01"; IS_END  = "2020-12-31"
OOS_START = "2021-01-01"

# ── Analysis functions ───────────────────────────────────────────────────────
def analyze_state(df, label, period_mask=None, pos_map=None):
    """
    Analyze accuracy per state.
    'Accuracy' = % of sessions where sign(pos) == sign(fwd return)
    (positive position → market goes up, negative → market goes down)
    """
    d = df[period_mask].copy() if period_mask is not None else df.copy()
    rows = []
    for st_id in [1,2,3,4,5]:
        sub = d[d["state"] == st_id].copy()
        if len(sub) < 5: continue
        p = sub["pos"].iloc[0]  # position for this state
        for h in HORIZONS:
            col = f"fwd{h}"
            valid = sub[col].dropna()
            if len(valid) < 3: continue
            n_sess = len(valid)
            avg_ret = valid.mean() * 100
            med_ret = valid.median() * 100
            # Win rate: signed correctly
            if p > 0:
                wr = (valid > 0).sum() / n_sess * 100
            elif p < 0:
                wr = (valid < 0).sum() / n_sess * 100
            else:
                wr = np.nan
            # Position-weighted P&L
            pnl = (valid * p).mean() * 100
            rows.append({
                "State": STATE_NAMES[st_id], "st_id": st_id,
                "Position": p, "Horizon": h,
                "Sessions": n_sess, "AvgRet%": round(avg_ret,2),
                "MedRet%": round(med_ret,2),
                "WinRate%": round(wr,1) if not np.isnan(wr) else np.nan,
                "PosWeightPnL%": round(pnl,2),
            })
    return pd.DataFrame(rows)

def analyze_transitions(df, label, period_mask=None, pos_map=None):
    """
    For each entry transition (prev_state → cur_state),
    measure forward return over all horizons.
    """
    d = df[period_mask].copy() if period_mask is not None else df.copy()
    d = d.reset_index(drop=True)
    # Find transition points
    trans = []
    for i in range(1, len(d)):
        ps = d["state"].iloc[i-1]
        cs = d["state"].iloc[i]
        if ps != cs:
            trans.append({"idx": i, "from": ps, "to": cs,
                          "date": d["date"].iloc[i],
                          "pos": d["pos"].iloc[i]})
    if not trans: return pd.DataFrame()
    td = pd.DataFrame(trans)
    # Add forward returns at transition point
    for h in HORIZONS:
        col = f"fwd{h}"
        td[col] = [d[col].iloc[t["idx"]] if t["idx"] < len(d) else np.nan for _, t in td.iterrows()]
    # Aggregate
    _pos_map_for_trans = pos_map if pos_map is not None else POS_F
    rows = []
    for (fr, to), grp in td.groupby(["from","to"]):
        p = _pos_map_for_trans[to]  # position AFTER transition
        for h in HORIZONS:
            col = f"fwd{h}"
            valid = grp[col].dropna()
            if len(valid) < 2: continue
            n_t = len(valid)
            avg_ret = valid.mean()*100
            med_ret = valid.median()*100
            if p > 0:   wr = (valid > 0).sum()/n_t*100
            elif p < 0: wr = (valid < 0).sum()/n_t*100
            else:       wr = np.nan
            pnl = (valid * p).mean()*100
            rows.append({
                "From": STATE_NAMES[fr], "To": STATE_NAMES[to],
                "from_id": fr, "to_id": to,
                "NewPos": p, "Horizon": h,
                "Count": n_t,
                "AvgRet%": round(avg_ret,2),
                "MedRet%": round(med_ret,2),
                "WinRate%": round(wr,1) if not np.isnan(wr) else np.nan,
                "PosWeightPnL%": round(pnl,2),
            })
    return pd.DataFrame(rows)

# Run all analyses
mask_is  = (df_F["date"] >= IS_START)  & (df_F["date"] <= IS_END)
mask_oos = (df_F["date"] >= OOS_START)
mask_is_H  = (df_H["date"] >= IS_START)  & (df_H["date"] <= IS_END)
mask_oos_H = (df_H["date"] >= OOS_START)

st_F_full = analyze_state(df_F, "F-full")
st_F_IS   = analyze_state(df_F, "F-IS",  mask_is)
st_F_OOS  = analyze_state(df_F, "F-OOS", mask_oos)
st_H_full = analyze_state(df_H, "H-full")
st_H_IS   = analyze_state(df_H, "H-IS",  mask_is_H)
st_H_OOS  = analyze_state(df_H, "H-OOS", mask_oos_H)

tr_F_full = analyze_transitions(df_F, "F-full", pos_map=POS_F)
tr_F_IS   = analyze_transitions(df_F, "F-IS",  mask_is,  pos_map=POS_F)
tr_F_OOS  = analyze_transitions(df_F, "F-OOS", mask_oos, pos_map=POS_F)
tr_H_full = analyze_transitions(df_H, "H-full", pos_map=POS_H)
tr_H_IS   = analyze_transitions(df_H, "H-IS",  mask_is_H,  pos_map=POS_H)
tr_H_OOS  = analyze_transitions(df_H, "H-OOS", mask_oos_H, pos_map=POS_H)

# ── Console print ────────────────────────────────────────────────────────────
def print_state_table(df_res, label, horizon=20):
    sub = df_res[df_res["Horizon"]==horizon].copy()
    print(f"\n{'='*78}")
    print(f"  STATE ACCURACY [{label}] — horizon T+{horizon} sessions (~{horizon//20}M)")
    print(f"{'='*78}")
    print(f"  {'State':<10} {'Pos':>6} {'Sessions':>9} {'AvgRet%':>9} {'MedRet%':>9} {'WinRate%':>10} {'PnL(pos)%':>11}")
    print(f"  {'-'*10} {'-'*6} {'-'*9} {'-'*9} {'-'*9} {'-'*10} {'-'*11}")
    for _, r in sub.sort_values("st_id").iterrows():
        wr = f"{r['WinRate%']:.1f}%" if not pd.isna(r["WinRate%"]) else "  n/a"
        print(f"  {r['State']:<10} {r['Position']:>+6.2f} {r['Sessions']:>9} {r['AvgRet%']:>+9.2f}% {r['MedRet%']:>+9.2f}% {wr:>10} {r['PosWeightPnL%']:>+10.2f}%")

def print_transition_table(df_res, label, horizon=20):
    sub = df_res[df_res["Horizon"]==horizon].copy()
    if sub.empty: return
    # Sort by WinRate% desc
    sub = sub.sort_values("WinRate%", ascending=False)
    print(f"\n{'='*85}")
    print(f"  TRANSITION ACCURACY [{label}] — horizon T+{horizon} sessions")
    print(f"{'='*85}")
    print(f"  {'Transition':<22} {'Pos':>6} {'Count':>6} {'AvgRet%':>9} {'MedRet%':>9} {'WinRate%':>10} {'PnL(pos)%':>11}")
    print(f"  {'-'*22} {'-'*6} {'-'*6} {'-'*9} {'-'*9} {'-'*10} {'-'*11}")
    for _, r in sub.iterrows():
        wr = f"{r['WinRate%']:.1f}%" if not pd.isna(r["WinRate%"]) else "  n/a"
        tr_name = f"{r['From']} → {r['To']}"
        print(f"  {tr_name:<22} {r['NewPos']:>+6.2f} {r['Count']:>6} {r['AvgRet%']:>+9.2f}% {r['MedRet%']:>+9.2f}% {wr:>10} {r['PosWeightPnL%']:>+10.2f}%")

# ── F-System print ─────────────────────────────────────────────────────────
print("\n" + "█"*78)
print("  F-SYSTEM (NE=0.50, F-smooth) — STATE ACCURACY")
print("█"*78)
for h in [10, 20, 60]:
    print_state_table(st_F_full, "F-smooth NE=0.50, Full 2011+", h)
    print_state_table(st_F_IS,   "F-smooth NE=0.50, IS 2011-2020", h)
    print_state_table(st_F_OOS,  "F-smooth NE=0.50, OOS 2021+", h)

print("\n\n" + "█"*78)
print("  F-SYSTEM — TRANSITION ACCURACY")
print("█"*78)
for h in [10, 20, 60]:
    print_transition_table(tr_F_full, "Full 2011+", h)
    print_transition_table(tr_F_IS,   "IS 2011-2020", h)
    print_transition_table(tr_F_OOS,  "OOS 2021+", h)

# ── H-System print ─────────────────────────────────────────────────────────
print("\n\n" + "█"*78)
print("  H-SYSTEM (NE=0.20, H-smooth) — STATE ACCURACY")
print("█"*78)
for h in [10, 20, 60]:
    print_state_table(st_H_full, "H-smooth NE=0.20, Full 2011+", h)
    print_state_table(st_H_IS,   "H-smooth NE=0.20, IS 2011-2020", h)
    print_state_table(st_H_OOS,  "H-smooth NE=0.20, OOS 2021+", h)

print("\n\n" + "█"*78)
print("  H-SYSTEM — TRANSITION ACCURACY")
print("█"*78)
for h in [10, 20, 60]:
    print_transition_table(tr_H_full, "Full 2011+", h)
    print_transition_table(tr_H_IS,   "IS 2011-2020", h)
    print_transition_table(tr_H_OOS,  "OOS 2021+", h)

# ── Build HTML ───────────────────────────────────────────────────────────────
def df_to_html_table(df_in, highlight_col=None, color_col=None, title=""):
    rows_html = ""
    for _, r in df_in.iterrows():
        cells = ""
        for col in df_in.columns:
            if col in ["st_id","from_id","to_id"]: continue
            v = r[col]
            style = ""
            if col == highlight_col:
                if isinstance(v, float) and not np.isnan(v):
                    if v >= 70: style = "background:#c8e6c9;font-weight:bold"
                    elif v >= 55: style = "background:#fff9c4"
                    elif v <= 40: style = "background:#ffcdd2"
            if col in ["AvgRet%","MedRet%","PosWeightPnL%"] and isinstance(v, float):
                style = ("color:#1a7a1a" if v > 0 else "color:#c62828") if not np.isnan(v) else ""
            txt = f"{v:+.2f}%" if isinstance(v, float) and col.endswith("%") and not np.isnan(v) else str(v)
            cells += f'<td style="{style}">{txt}</td>'
        rows_html += f"<tr>{cells}</tr>\n"
    cols = [c for c in df_in.columns if c not in ["st_id","from_id","to_id"]]
    header = "".join(f"<th>{c}</th>" for c in cols)
    return f"""
<div style="margin:20px 0">
<h3 style="font-family:sans-serif;color:#333">{title}</h3>
<table style="border-collapse:collapse;font-family:monospace;font-size:13px;width:100%">
<thead style="background:#37474f;color:#fff"><tr>{header}</tr></thead>
<tbody>
{rows_html}
</tbody>
</table></div>"""

# Pivot: show all horizons side by side
def pivot_state(df_res, label):
    rows = []
    for st_id in [1,2,3,4,5]:
        sub = df_res[df_res["st_id"]==st_id]
        if sub.empty: continue
        row = {"State": STATE_NAMES[st_id], "st_id": st_id,
               "Pos": sub["Position"].iloc[0],
               "Sessions": sub["Sessions"].iloc[0]}
        for h in HORIZONS:
            s2 = sub[sub["Horizon"]==h]
            if not s2.empty:
                row[f"WR_{h}"] = s2["WinRate%"].values[0]
                row[f"Avg_{h}"] = s2["AvgRet%"].values[0]
                row[f"PnL_{h}"] = s2["PosWeightPnL%"].values[0]
        rows.append(row)
    return pd.DataFrame(rows)

def pivot_trans(df_res, label):
    rows = []
    seen = set()
    for _, r in df_res.sort_values(["from_id","to_id"]).iterrows():
        key = (r["from_id"], r["to_id"])
        if key in seen: continue
        seen.add(key)
        row = {"Transition": f"{r['From']} → {r['To']}",
               "from_id": r["from_id"], "to_id": r["to_id"],
               "NewPos": r["NewPos"],
               "Count": r["Count"]}
        for h in HORIZONS:
            s2 = df_res[(df_res["from_id"]==r["from_id"]) & (df_res["to_id"]==r["to_id"]) & (df_res["Horizon"]==h)]
            if not s2.empty:
                row[f"WR_{h}"] = s2["WinRate%"].values[0]
                row[f"Avg_{h}"] = s2["AvgRet%"].values[0]
                row[f"PnL_{h}"] = s2["PosWeightPnL%"].values[0]
        rows.append(row)
    return pd.DataFrame(rows)

def state_pivot_to_html(df_pivot, title):
    cols_order = ["State","Pos","Sessions"] + \
                 [f"WR_{h}" for h in HORIZONS] + \
                 [f"Avg_{h}" for h in HORIZONS] + \
                 [f"PnL_{h}" for h in HORIZONS]
    cols_order = [c for c in cols_order if c in df_pivot.columns]
    df_pivot = df_pivot[cols_order].copy()

    header_row1 = "<tr><th rowspan='2'>State</th><th rowspan='2'>Pos</th><th rowspan='2'>Sessions</th>"
    header_row1 += "".join(f"<th colspan='4'>{g}</th>" for g in ["Win Rate %","Avg Return %","Pos PnL %"])
    header_row1 += "</tr>"
    header_row2 = "<tr>" + "".join(f"<th>T+{h}</th>" for g in range(3) for h in HORIZONS) + "</tr>"

    rows_html = ""
    for _, r in df_pivot.iterrows():
        bg = STATE_COLOR.get(int(r.get("st_id",3)) if "st_id" in r else 3, "#fff")
        cells = f'<td style="background:{bg};color:#fff;font-weight:bold;padding:4px 8px">{r["State"]}</td>'
        cells += f'<td style="text-align:center">{r["Pos"]:+.2f}</td>'
        cells += f'<td style="text-align:center">{int(r["Sessions"])}</td>'
        for col in [f"WR_{h}" for h in HORIZONS]:
            v = r.get(col, np.nan)
            if pd.isna(v): cells += "<td>-</td>"; continue
            bg2 = "#c8e6c9" if v>=65 else ("#fff9c4" if v>=52 else ("#ffcdd2" if v<=42 else ""))
            cells += f'<td style="background:{bg2};text-align:center">{v:.1f}%</td>'
        for col in [f"Avg_{h}" for h in HORIZONS]:
            v = r.get(col, np.nan)
            if pd.isna(v): cells += "<td>-</td>"; continue
            c2 = "#1a7a1a" if v>0 else "#c62828"
            cells += f'<td style="color:{c2};text-align:center">{v:+.2f}%</td>'
        for col in [f"PnL_{h}" for h in HORIZONS]:
            v = r.get(col, np.nan)
            if pd.isna(v): cells += "<td>-</td>"; continue
            c2 = "#1a7a1a" if v>0 else "#c62828"
            fw = "bold" if abs(v)>2 else "normal"
            cells += f'<td style="color:{c2};font-weight:{fw};text-align:center">{v:+.2f}%</td>'
        rows_html += f"<tr>{cells}</tr>\n"

    return f"""
<div style="margin:24px 0">
<h3 style="font-family:sans-serif;color:#333;border-left:4px solid #37474f;padding-left:10px">{title}</h3>
<table style="border-collapse:collapse;font-family:monospace;font-size:13px;width:100%;border:1px solid #ddd">
<thead style="background:#37474f;color:#fff">{header_row1}{header_row2}</thead>
<tbody>{rows_html}</tbody>
</table></div>"""

def trans_pivot_to_html(df_pivot, title):
    cols_order = ["Transition","NewPos","Count"] + \
                 [f"WR_{h}" for h in HORIZONS] + \
                 [f"Avg_{h}" for h in HORIZONS] + \
                 [f"PnL_{h}" for h in HORIZONS]
    cols_order = [c for c in cols_order if c in df_pivot.columns]
    df_p = df_pivot.sort_values(["from_id","to_id"]).copy()

    header_row1 = "<tr><th rowspan='2'>Transition</th><th rowspan='2'>NewPos</th><th rowspan='2'>Count</th>"
    header_row1 += "".join(f"<th colspan='4'>{g}</th>" for g in ["Win Rate %","Avg Return %","Pos PnL %"])
    header_row1 += "</tr>"
    header_row2 = "<tr>" + "".join(f"<th>T+{h}</th>" for g in range(3) for h in HORIZONS) + "</tr>"

    rows_html = ""
    prev_from = None
    for _, r in df_p.iterrows():
        sep = ' style="border-top:2px solid #aaa"' if r["from_id"] != prev_from else ""
        prev_from = r["from_id"]
        from_c = STATE_COLOR.get(int(r["from_id"]), "#ccc")
        to_c   = STATE_COLOR.get(int(r["to_id"]),   "#ccc")
        tr_html = (f'<span style="background:{from_c};color:#fff;border-radius:3px;padding:1px 5px">'
                   f'{r["Transition"].split(" → ")[0]}</span> → '
                   f'<span style="background:{to_c};color:#fff;border-radius:3px;padding:1px 5px">'
                   f'{r["Transition"].split(" → ")[1]}</span>')
        cells = f'<td{sep} style="white-space:nowrap;padding:4px 8px">{tr_html}</td>'
        cells += f'<td{sep} style="text-align:center">{r["NewPos"]:+.2f}</td>'
        cells += f'<td{sep} style="text-align:center">{int(r["Count"])}</td>'
        for col in [f"WR_{h}" for h in HORIZONS]:
            v = r.get(col, np.nan)
            if pd.isna(v): cells += f"<td{sep}>-</td>"; continue
            bg2 = "#c8e6c9" if v>=65 else ("#fff9c4" if v>=52 else ("#ffcdd2" if v<=42 else ""))
            fw  = "bold" if v>=65 or v<=40 else "normal"
            cells += f'<td{sep} style="background:{bg2};text-align:center;font-weight:{fw}">{v:.1f}%</td>'
        for col in [f"Avg_{h}" for h in HORIZONS]:
            v = r.get(col, np.nan)
            if pd.isna(v): cells += f"<td{sep}>-</td>"; continue
            c2 = "#1a7a1a" if v>0 else "#c62828"
            cells += f'<td{sep} style="color:{c2};text-align:center">{v:+.2f}%</td>'
        for col in [f"PnL_{h}" for h in HORIZONS]:
            v = r.get(col, np.nan)
            if pd.isna(v): cells += f"<td{sep}>-</td>"; continue
            c2 = "#1a7a1a" if v>0 else "#c62828"
            fw = "bold" if abs(v)>2 else "normal"
            cells += f'<td{sep} style="color:{c2};font-weight:{fw};text-align:center">{v:+.2f}%</td>'
        rows_html += f"<tr>{cells}</tr>\n"

    return f"""
<div style="margin:24px 0">
<h3 style="font-family:sans-serif;color:#333;border-left:4px solid #1565c0;padding-left:10px">{title}</h3>
<table style="border-collapse:collapse;font-family:monospace;font-size:13px;width:100%;border:1px solid #ddd">
<thead style="background:#1565c0;color:#fff">{header_row1}{header_row2}</thead>
<tbody>{rows_html}</tbody>
</table></div>"""

# Build pivots
pv_F_full = pivot_state(st_F_full, "F-full")
pv_F_IS   = pivot_state(st_F_IS,   "F-IS")
pv_F_OOS  = pivot_state(st_F_OOS,  "F-OOS")
pv_H_full = pivot_state(st_H_full, "H-full")
pv_H_IS   = pivot_state(st_H_IS,   "H-IS")
pv_H_OOS  = pivot_state(st_H_OOS,  "H-OOS")

ptr_F_full = pivot_trans(tr_F_full, "F-full")
ptr_F_IS   = pivot_trans(tr_F_IS,   "F-IS")
ptr_F_OOS  = pivot_trans(tr_F_OOS,  "F-OOS")
ptr_H_full = pivot_trans(tr_H_full, "H-full")
ptr_H_IS   = pivot_trans(tr_H_IS,   "H-IS")
ptr_H_OOS  = pivot_trans(tr_H_OOS,  "H-OOS")

# Add st_id back after pivot
id_map = {STATE_NAMES[i]:i for i in range(1,6)}
for pv in [pv_F_full, pv_F_IS, pv_F_OOS, pv_H_full, pv_H_IS, pv_H_OOS]:
    if "st_id" not in pv.columns:
        pv["st_id"] = pv["State"].map(id_map)

html_body = f"""
<h2 style="font-family:sans-serif;border-bottom:2px solid #37474f;padding-bottom:6px">
  F_System &amp; H_System — Độ chính xác dự báo theo State &amp; Transition</h2>
<p style="font-family:sans-serif;color:#555;font-size:13px">
  <b>Win Rate</b> = % phiên thị trường đi đúng chiều position (long→tăng, short→giảm)<br>
  <b>Pos PnL</b> = position × avg_forward_return (lợi nhuận kỳ vọng thực tế)<br>
  <span style="background:#c8e6c9;padding:2px 6px;border-radius:3px">Xanh ≥65%</span>&nbsp;
  <span style="background:#fff9c4;padding:2px 6px;border-radius:3px">Vàng 52–64%</span>&nbsp;
  <span style="background:#ffcdd2;padding:2px 6px;border-radius:3px">Đỏ ≤42%</span>
</p>

<h2 style="font-family:sans-serif;margin-top:32px;color:#1b5e20">▶ F_System (F-smooth rm=5/ms=3 | CRISIS={POS_F[1]:+.2f} / BEAR={POS_F[2]:+.2f} / NEUTRAL={POS_F[3]:+.2f} / BULL={POS_F[4]:+.2f} / EX-BULL={POS_F[5]:+.2f})</h2>

<h3 style="font-family:sans-serif;color:#37474f;margin-top:20px">A1. F_System — Độ chính xác theo State</h3>
{state_pivot_to_html(pv_F_full, "F-smooth (NE=0.50) — Toàn bộ 2011 → nay")}
{state_pivot_to_html(pv_F_IS,   "F-smooth (NE=0.50) — IS: 2011–2020")}
{state_pivot_to_html(pv_F_OOS,  "F-smooth (NE=0.50) — OOS: 2021 → nay")}

<h3 style="font-family:sans-serif;color:#1565c0;margin-top:28px">A2. F_System — Độ chính xác theo Transition</h3>
<p style="font-family:sans-serif;color:#555;font-size:13px">
  Đo lường forward return <i>ngay tại thời điểm chuyển trạng thái</i>.
</p>
{trans_pivot_to_html(ptr_F_full, "F-smooth — Toàn bộ 2011 → nay")}
{trans_pivot_to_html(ptr_F_IS,   "F-smooth — IS: 2011–2020")}
{trans_pivot_to_html(ptr_F_OOS,  "F-smooth — OOS: 2021 → nay")}

<hr style="margin:40px 0;border:2px solid #37474f">

<h2 style="font-family:sans-serif;margin-top:32px;color:#b71c1c">▶ H_System (H-smooth rm=15/ms=7 | CRISIS={POS_H[1]:+.2f} / BEAR={POS_H[2]:+.2f} / NEUTRAL={POS_H[3]:+.2f} / BULL={POS_H[4]:+.2f} / EX-BULL={POS_H[5]:+.2f})</h2>

<h3 style="font-family:sans-serif;color:#37474f;margin-top:20px">B1. H_System — Độ chính xác theo State</h3>
{state_pivot_to_html(pv_H_full, "H-smooth (NE=0.20) — Toàn bộ 2011 → nay")}
{state_pivot_to_html(pv_H_IS,   "H-smooth (NE=0.20) — IS: 2011–2020")}
{state_pivot_to_html(pv_H_OOS,  "H-smooth (NE=0.20) — OOS: 2021 → nay")}

<h3 style="font-family:sans-serif;color:#1565c0;margin-top:28px">B2. H_System — Độ chính xác theo Transition</h3>
{trans_pivot_to_html(ptr_H_full, "H-smooth — Toàn bộ 2011 → nay")}
{trans_pivot_to_html(ptr_H_IS,   "H-smooth — IS: 2011–2020")}
{trans_pivot_to_html(ptr_H_OOS,  "H-smooth — OOS: 2021 → nay")}
"""

html = f"""<!DOCTYPE html><html lang="vi"><head>
<meta charset="utf-8">
<title>F_System Accuracy Analysis</title>
<style>
  body {{font-family:sans-serif;margin:24px;background:#fafafa;color:#222}}
  table {{margin-bottom:8px}}
  th,td {{padding:4px 10px;border:1px solid #ddd;white-space:nowrap}}
  thead th {{font-size:12px}}
  h2 {{margin-top:32px}}
</style>
</head><body>
{html_body}
<p style="color:#aaa;font-size:11px;margin-top:40px">Generated {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}</p>
</body></html>"""

out_path = WORKDIR + "/f_system_accuracy.html"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"\n\nHTML saved: {out_path}")
