# -*- coding: utf-8 -*-
"""
F_System Backtest: Futures-based VN30F trading system.
Su dung cung 5-state pipeline nhu H_System nhung:
  - LONG + SHORT thay vi chi long/cash
  - TC thap hon (0.03% round-trip vs 0.1%)
  - T+0 snap (khong ramp)
  - Underlying: VN30 tu 2012, VNINDEX truoc do
Output: f_system_report.html
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

# ── Load data ────────────────────────────────────────────────────────────────
vni = pd.read_csv(WORKDIR + "/VNINDEX.csv", low_memory=False)
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
for col in ["Open","High","Low","Close","Volume","VNINDEX_PE",
            "D_RSI","D_RSI_T1W","D_RSI_Max1W","D_RSI_Max3M",
            "D_RSI_Min1W","D_RSI_Min3M","D_RSI_Max1W_Close",
            "D_RSI_Max3M_Close","D_RSI_Max3M_MACD","D_RSI_Max1W_MACD",
            "D_RSI_Min1W_Close","D_RSI_MinT3","D_MACDdiff","D_CMF","C_L1M","C_L1W","VN30"]:
    if col in vni.columns: vni[col] = pd.to_numeric(vni[col], errors="coerce")
if "breadth" not in vni.columns: vni["breadth"] = np.nan

# Underlying: dung VN30 tu khi co du lieu, VNINDEX truoc do
# Tin hieu (pipeline) van dung VNINDEX de dam bao nhat quan voi H_System
vn30_raw = vni["VN30"].values if "VN30" in vni.columns else np.full(len(vni), np.nan)
vnidx_raw = vni["Close"].values.copy()
# Chuan hoa VN30 ve cung don vi voi VNINDEX (base = VNINDEX tai ngay dau VN30)
vn30_start_idx = np.where(~np.isnan(vn30_raw))[0]
if len(vn30_start_idx) > 0:
    s = vn30_start_idx[0]
    scale = vnidx_raw[s] / vn30_raw[s]  # scale factor
    underlying = vnidx_raw.copy()
    for i in range(s, len(vni)):
        if not np.isnan(vn30_raw[i]):
            underlying[i] = vn30_raw[i] * scale
else:
    underlying = vnidx_raw.copy()

close = vni["Close"].values.copy()  # VNINDEX - for signal pipeline
high  = vni["High"].values.copy()
low   = vni["Low"].values.copy()
vol   = vni["Volume"].values.copy()
n = len(close)
cal_days = (vni["time"].iloc[-1] - vni["time"].iloc[0]).days
SPY = n / (cal_days / 365.25)

# ── Pipeline (identical to H_System) ────────────────────────────────────────
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

pe_arr = vni["VNINDEX_PE"].values.copy()
pe_p90 = np.full(n, np.nan)
for t in range(n):
    h = pe_arr[:t+1]; h = h[~np.isnan(h)]
    if len(h) >= 60: pe_p90[t] = np.nanpercentile(h, 90)
rm_c = np.maximum.accumulate(np.where(np.isnan(close), 0, close))
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

# BearDvg gate (identical to H_System)
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
  (_DMACD>0)&(_DMT3<0.56)&(_DM1W<0.64)&(_DR/_DRT>1.10)&(_DCMF>0)&
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

# Smoothing variants
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

# H_System smoothing (canonical)
st_smooth_H = min_stay_filter(rolling_mode(st_dvg, 15), 7)
# F_System lighter smoothing (rm=5, ms=3) - phan ung nhanh hon
st_smooth_F = min_stay_filter(rolling_mode(st_dvg, 5), 3)
# No smoothing (chi r_ema)
st_smooth_raw = st_dvg.copy()

STATE_NAMES = {1:"CRISIS", 2:"BEAR", 3:"NEUTRAL", 4:"BULL", 5:"EX-BULL"}

# ── F_System position maps ───────────────────────────────────────────────────
# H_System reference
H_WEIGHT = {1: 0.00, 2: 0.20, 3: 0.70, 4: 1.00, 5: 1.30}

# F_System position maps (fraction of capital, negative = short)
F_MAPS = {
    # Ten             CRISIS  BEAR    NEUTRAL  BULL    EX-BULL
    "F_Balanced":  {1:-1.00, 2:-0.30, 3: 0.00, 4:+1.00, 5:+1.50},
    "F_HAdapted":  {1:-1.00, 2:-0.20, 3:+0.70, 4:+1.00, 5:+1.30},  # H_System + short CRISIS/BEAR
    "F_Conservative": {1:-0.50, 2:-0.20, 3: 0.00, 4:+1.00, 5:+1.30},
    "F_Aggressive": {1:-1.00, 2:-0.50, 3:+0.30, 4:+1.00, 5:+1.50},
}

# ── Simulate ─────────────────────────────────────────────────────────────────
# H_System tham chieu: HT+Rec (0.1%/yr deposit, Recovery Boost)
# F_System: TC=0.03% round-trip, no deposit/borrow (futures embedded)
#           Roll cost: 1.2%/yr on |position| (12 rolls/yr @ 0.10%)
#           T+0: snap to target immediately (no ramp)

TC_F   = 0.0003   # 0.03% per unit of |Δposition|
ROLL_C = 0.012    # 1.2%/yr roll cost on |position|, applied per session

# H_System HT+Rec reference
REC_W  = 1.30; REC_D = 20
rec_map = {}
i = 0
while i < n-1:
    if st_smooth_H[i] == 1:
        start = i
        while i < n-1 and st_smooth_H[i] == 1: i += 1
        end = i
        if end - start >= 2 and end < n:
            for t in range(end, min(end+REC_D, n)):
                if st_smooth_H[t] != 1: rec_map[t] = REC_W
    else: i += 1

def simulate_H(dep_annual=0.001):
    DR = dep_annual/SPY; BR = 0.10/SPY; TC = 0.001
    pv = np.zeros(n); pv[0] = 1e9; w = H_WEIGHT[3]
    trades = 0
    for t in range(1, n):
        base = H_WEIGHT[st_smooth_H[t-1]]
        target = max(base, rec_map[t-1]) if (t-1) in rec_map else base
        diff = target - w
        w_new = target if abs(diff) < 0.03 else w + diff/3
        w_new = float(np.clip(w_new, 0.0, 1.50))
        if abs(w_new - w) > 0.01: trades += 1
        rm = underlying[t]/underlying[t-1]-1 if underlying[t-1] > 0 else 0.0
        pv[t] = pv[t-1] * (1.0 + w_new*rm
                           + max(0.0, 1.0-w_new)*DR
                           - max(0.0, w_new-1.0)*BR
                           - abs(w_new-w)*TC)
        w = w_new
    return pv, trades

def simulate_F(pos_map, st_arr, include_roll=True):
    """Futures simulation: T+0 snap, TC=0.03%/trade, roll cost 1.2%/yr."""
    TC = TC_F; RC = ROLL_C / SPY
    pv = np.zeros(n); pv[0] = 1e9
    pos = pos_map[3]  # start neutral
    trades = 0; long_days = 0; short_days = 0; flat_days = 0
    # Track contribution
    contrib_long = 0.0; contrib_short = 0.0
    for t in range(1, n):
        target = pos_map[int(st_arr[t-1])]
        diff = target - pos
        pos_new = target  # T+0 snap
        if abs(diff) > 0.01: trades += 1
        rm = underlying[t]/underlying[t-1]-1 if underlying[t-1] > 0 else 0.0
        pnl_pos   = pos_new * rm
        cost_tc   = abs(diff) * TC
        cost_roll = abs(pos_new) * RC if include_roll else 0.0
        pv[t] = pv[t-1] * (1.0 + pnl_pos - cost_tc - cost_roll)
        # Attribution
        if pos_new > 0.01:
            long_days += 1; contrib_long += pos_new * rm
        elif pos_new < -0.01:
            short_days += 1; contrib_short += pos_new * rm
        else:
            flat_days += 1
        pos = pos_new
    return pv, trades, long_days, short_days, flat_days, contrib_long, contrib_short

# B&H reference
pv_bh = np.zeros(n); pv_bh[0] = 1e9
for t in range(1, n):
    pv_bh[t] = pv_bh[t-1] * (underlying[t]/underlying[t-1] if underlying[t-1] > 0 else 1.0)

pv_H, trades_H = simulate_H(0.001)
results = {}
for name, pm in F_MAPS.items():
    pv, trades, ld, sd, fd, cl, cs = simulate_F(pm, st_smooth_H, include_roll=True)
    results[name] = {"pv": pv, "trades": trades, "long_days": ld,
                     "short_days": sd, "flat_days": fd,
                     "contrib_long": cl, "contrib_short": cs}

# Also test F_Balanced with lighter smoothing
pv_F_light, tr_l, ld_l, sd_l, fd_l, cl_l, cs_l = simulate_F(
    F_MAPS["F_Balanced"], st_smooth_F, include_roll=True)
results["F_Balanced_Light"] = {
    "pv": pv_F_light, "trades": tr_l, "long_days": ld_l,
    "short_days": sd_l, "flat_days": fd_l,
    "contrib_long": cl_l, "contrib_short": cs_l,
}

# ── Metrics ──────────────────────────────────────────────────────────────────
def metrics(pv, i0=0, i1=None):
    sl = pv[i0:] if i1 is None else pv[i0:i1]
    ds = vni["time"].reset_index(drop=True).iloc[i0:] if i1 is None else vni["time"].reset_index(drop=True).iloc[i0:i1]
    a = np.asarray(sl, dtype=float); v = np.where(a > 0)[0]
    if len(v) < 10: return {}
    i0_, i1_ = v[0], v[-1]; v0, v1 = a[i0_], a[i1_]
    ds2 = ds.reset_index(drop=True)
    yrs = (ds2.iloc[i1_] - ds2.iloc[i0_]).days / 365.25
    if yrs <= 0: return {}
    cagr = (v1/v0)**(1/yrs) - 1
    sub = a[i0_:i1_+1]; rets = np.diff(sub)/sub[:-1]; spy_s = len(rets)/yrs
    mr = np.mean(rets); sr = np.std(rets)
    sharpe = mr*spy_s / (sr*np.sqrt(spy_s)) if sr > 0 else 0
    down = rets[rets < 0]; ds3 = np.sqrt(np.mean(down**2)) if len(down) > 0 else 0
    sortino = mr*spy_s / (ds3*np.sqrt(spy_s)) if ds3 > 0 else 0
    rm2 = np.maximum.accumulate(sub); dd2 = np.where(rm2 > 0, sub/rm2-1, 0)
    mdd = dd2.min(); calmar = cagr/abs(mdd) if mdd != 0 else 0
    under = dd2 < 0; mx = 0; cu = 0
    for u in under:
        cu = cu+1 if u else 0; mx = max(mx, cu)
    return {"cagr": cagr, "sharpe": sharpe, "sortino": sortino,
            "mdd": mdd, "calmar": calmar, "ddur": mx, "final": v1/1e9}

idx11 = vni[vni["time"] >= "2011-01-01"].index[0]
idx21 = vni[vni["time"] >= "2021-01-01"].index[0]

PERIODS = [("Toan ky (2000+)", 0, None), ("Tu 2011", idx11, None), ("OOS (2021+)", idx21, None)]

# Print summary
print("=" * 90)
print("  F_SYSTEM vs H_SYSTEM: BACKTEST SUMMARY (underlying: VN30 tu 2012, VNINDEX truoc do)")
print("=" * 90)

all_systems = {
    "HT+Rec (H_System)": (pv_H, trades_H),
    **{k: (v["pv"], v["trades"]) for k, v in results.items()},
    "B&H": (pv_bh, 0),
}

for period_lbl, i0, i1 in PERIODS:
    print(f"\n  [{period_lbl}]")
    print(f"  {'System':<25} {'CAGR':>8} {'Sharpe':>7} {'MaxDD':>8} {'Calmar':>8} {'Trades':>8} {'NAV':>8}")
    print(f"  {'-'*25} {'-'*8} {'-'*7} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
    for name, (pv, tr) in all_systems.items():
        m = metrics(pv, i0, i1)
        if not m: continue
        print(f"  {name:<25} {m['cagr']*100:>+7.1f}% {m['sharpe']:>7.2f} {m['mdd']*100:>+7.1f}% "
              f"{m['calmar']:>8.2f} {tr:>8d} {m['final']:>7.1f}t")

print()
print("=" * 90)
print("  ATTRIBUTION: Long vs Short contribution (tu 2011)")
print("=" * 90)
for k, v in results.items():
    if k == "F_Balanced_Light":
        label = "F_Balanced (Light smooth)"
    else:
        label = k
    n_tot = v["long_days"] + v["short_days"] + v["flat_days"]
    print(f"\n  {label}:")
    print(f"    Long  days: {v['long_days']:4d} ({v['long_days']/n_tot*100:.0f}%)  | cumulative PnL: {v['contrib_long']*100:+.1f}%")
    print(f"    Short days: {v['short_days']:4d} ({v['short_days']/n_tot*100:.0f}%)  | cumulative PnL: {v['contrib_short']*100:+.1f}%")
    print(f"    Flat  days: {v['flat_days']:4d} ({v['flat_days']/n_tot*100:.0f}%)")

# ── Annual comparison ─────────────────────────────────────────────────────────
annual = []
for yr in sorted(vni["time"].dt.year.unique()):
    mask = vni["time"].dt.year == yr; idx = vni[mask].index
    if len(idx) < 10: continue
    i0, i1 = idx[0], idx[-1]
    if pv_H[i0] <= 0: continue
    row = {"yr": yr,
           "H":  pv_H[i1]/pv_H[i0]-1,
           "bh": pv_bh[i1]/pv_bh[i0]-1}
    for k, v in results.items():
        if v["pv"][i0] > 0:
            row[k] = v["pv"][i1]/v["pv"][i0]-1
    annual.append(row)

print()
print("=" * 90)
print("  ANNUAL RETURNS")
print("=" * 90)
hdr = f"  {'Year':>6}  {'H+Rec':>8}  {'F_Balan':>8}  {'F_HAdpt':>8}  {'F_Consv':>8}  {'F_Aggr':>8}  {'F_Bl_Lt':>8}  {'B&H':>8}"
print(hdr)
print(f"  {'-'*6}  {'-'*8}  {'-'*8}  {'-'*8}  {'-'*8}  {'-'*8}  {'-'*8}  {'-'*8}")
for a in annual:
    if a["yr"] < 2011: continue
    oos = " *" if a["yr"] >= 2021 else "  "
    def p(k): return f"{a.get(k,float('nan'))*100:>+7.1f}%" if k in a else "       —"
    print(f"  {a['yr']:>4}{oos}  {p('H'):>8}  {p('F_Balanced'):>8}  {p('F_HAdapted'):>8}  "
          f"{p('F_Conservative'):>8}  {p('F_Aggressive'):>8}  {p('F_Balanced_Light'):>8}  {p('bh'):>8}")

# ── HTML Report ───────────────────────────────────────────────────────────────
print("\nGenerating HTML report...")

step = 5
idx_s = list(range(0, n, step))
dates_s = [vni["time"].iloc[i].strftime("%Y-%m-%d") for i in idx_s]
def norm(pv, i0=0): return [round(float(pv[i]/pv[max(i0,0)]*100), 2) for i in idx_s]
def dd_arr(pv): rm=np.maximum.accumulate(pv); return [round(float((pv[i]/rm[i]-1)*100),2) for i in idx_s]

best_F = "F_Balanced"
m_best = metrics(results[best_F]["pv"], idx11)
m_H    = metrics(pv_H, idx11)
m_bh   = metrics(pv_bh, idx11)

# Annual table HTML
ann_rows = ""
for a in annual:
    if a["yr"] < 2011: continue
    oos = " ◄" if a["yr"] >= 2021 else ""
    bh = a.get("bh", 0)
    H  = a.get("H", 0)
    Fb = a.get("F_Balanced", 0)
    Fa = a.get("F_Aggressive", 0)

    def rc(v): return "green" if v > bh+0.005 else ("red" if v < bh-0.005 else "")
    bear_yr = bh < -0.05
    bull_yr = bh > 0.15
    bg = ' style="background:#2d1a1a"' if bear_yr else (' style="background:#1a2d1a"' if bull_yr else "")

    def pp(v):
        c = "#4ade80" if v >= 0 else "#f87171"
        return f'<span style="color:{c}">{v*100:+.1f}%</span>'

    ann_rows += (f'<tr{bg}>'
        f'<td style="padding:4px 8px"><strong>{a["yr"]}</strong>{oos}</td>'
        f'<td style="padding:4px 8px;text-align:center">{pp(H)}</td>'
        f'<td style="padding:4px 8px;text-align:center;background:#0a1f0a">{pp(Fb)}</td>'
        f'<td style="padding:4px 8px;text-align:center">{pp(Fa)}</td>'
        f'<td style="padding:4px 8px;text-align:center;color:#60a5fa">{pp(bh)}</td>'
        f'<td style="padding:4px 8px;font-size:11px;color:#64748b">'
        f'{"🔴 Bear" if bear_yr else ("🟢 Bull" if bull_yr else "")}</td>'
        f'</tr>\n')

# Period metric rows
def mrow(lbl, pv, style=""):
    rows = ""
    for period_lbl, i0, i1 in PERIODS:
        m = metrics(pv, i0, i1)
        if not m: continue
        cg = "#4ade80" if m["cagr"] > 0 else "#f87171"
        md = "#4ade80" if m["mdd"] > -0.25 else ("#fbbf24" if m["mdd"] > -0.40 else "#f87171")
        rows += (f'<tr{style}>'
            f'<td style="padding:5px 10px">{lbl}</td>'
            f'<td style="padding:5px 8px;color:#94a3b8;font-size:11px">{period_lbl}</td>'
            f'<td style="padding:5px 8px;text-align:center;color:{cg};font-weight:700">{m["cagr"]*100:+.1f}%</td>'
            f'<td style="padding:5px 8px;text-align:center">{m["sharpe"]:.2f}</td>'
            f'<td style="padding:5px 8px;text-align:center">{m["sortino"]:.2f}</td>'
            f'<td style="padding:5px 8px;text-align:center;color:{md}">{m["mdd"]*100:.1f}%</td>'
            f'<td style="padding:5px 8px;text-align:center">{m["calmar"]:.2f}</td>'
            f'<td style="padding:5px 8px;text-align:center">{m["final"]:.1f}t</td>'
            f'</tr>\n')
    return rows

metric_rows = ""
metric_rows += mrow("HT+Rec (H_System)", pv_H)
metric_rows += mrow("F_Balanced", results["F_Balanced"]["pv"], ' style="background:#0a1a0a"')
metric_rows += mrow("F_HAdapted", results["F_HAdapted"]["pv"])
metric_rows += mrow("F_Conservative", results["F_Conservative"]["pv"])
metric_rows += mrow("F_Aggressive", results["F_Aggressive"]["pv"])
metric_rows += mrow("F_Balanced_Light", results["F_Balanced_Light"]["pv"])
metric_rows += mrow("B&H", pv_bh)

# KPI cards for F_Balanced from 2011
kpi_m = metrics(results["F_Balanced"]["pv"], idx11)
kpi_H = metrics(pv_H, idx11)
kpi_bh = metrics(pv_bh, idx11)

nav_data = {
    "H+Rec": norm(pv_H),
    "F_Balanced": norm(results["F_Balanced"]["pv"]),
    "F_HAdapted": norm(results["F_HAdapted"]["pv"]),
    "F_Aggressive": norm(results["F_Aggressive"]["pv"]),
    "BH": norm(pv_bh),
}
dd_data = {
    "H+Rec": dd_arr(pv_H),
    "F_Balanced": dd_arr(results["F_Balanced"]["pv"]),
    "F_Aggressive": dd_arr(results["F_Aggressive"]["pv"]),
    "BH": dd_arr(pv_bh),
}

import json

html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>F_System Backtest Report</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
* {{ box-sizing:border-box;margin:0;padding:0 }}
body {{ background:#0a0f1e;color:#e2e8f0;font-family:'Segoe UI',sans-serif;padding:20px }}
h1 {{ font-size:22px;color:#f8fafc;margin-bottom:4px }}
h2 {{ font-size:15px;color:#94a3b8;font-weight:600;margin:20px 0 10px }}
.subtitle {{ color:#64748b;font-size:13px;margin-bottom:16px }}
.kpis {{ display:flex;gap:12px;flex-wrap:wrap;margin-bottom:20px }}
.kpi-group {{ background:#1e293b;border:1px solid #334155;border-radius:10px;padding:12px 16px;flex:1;min-width:200px }}
.kpi-group h3 {{ font-size:11px;color:#64748b;margin-bottom:8px;text-transform:uppercase;letter-spacing:.5px }}
.kpi {{ display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid #1e293b }}
.kpi .lbl {{ font-size:11px;color:#94a3b8 }}
.kpi .val {{ font-size:12px;font-weight:700 }}
.green {{ color:#4ade80 }} .red {{ color:#f87171 }} .blue {{ color:#60a5fa }}
.yellow {{ color:#fbbf24 }} .purple {{ color:#a78bfa }}
.chart-wrap {{ background:#1e293b;border:1px solid #334155;border-radius:10px;padding:16px;margin-bottom:16px }}
.charts-row {{ display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px }}
table {{ width:100%;border-collapse:collapse }}
thead th {{ background:#0f172a;color:#64748b;font-size:10px;font-weight:700;text-transform:uppercase;
            padding:7px 8px;border-bottom:2px solid #334155;white-space:nowrap }}
tr:hover td {{ background:rgba(96,165,250,0.06)!important }}
td {{ border-bottom:1px solid #1e293b;font-size:12px;padding:5px 8px }}
.tbl-wrap {{ background:#1e293b;border:1px solid #334155;border-radius:10px;padding:12px;margin-bottom:16px;overflow-x:auto }}
.note {{ background:#1e293b;border:1px solid #334155;border-radius:8px;padding:12px;font-size:12px;color:#94a3b8;margin-top:14px }}
.badge {{ padding:2px 8px;border-radius:8px;font-size:11px;font-weight:700 }}
.badge-crisis {{ background:#7f1d1d;color:#fca5a5 }}
.badge-bull   {{ background:#14532d;color:#86efac }}
.badge-bear   {{ background:#7c2d12;color:#fdba74 }}
.badge-neutral {{ background:#1e293b;color:#94a3b8;border:1px solid #334155 }}
.pos-map {{ display:flex;gap:6px;flex-wrap:wrap;margin:8px 0 }}
.pos-badge {{ padding:4px 10px;border-radius:6px;font-size:11px;font-weight:700;font-family:monospace }}
</style>
</head>
<body>
<h1>📈 F_System — Futures VN30 Trading System</h1>
<p class="subtitle">Long + Short · T+0 execution · TC=0.03% round-trip · Roll cost 1.2%/yr · Underlying: VN30 (tu 2012) / VNINDEX</p>

<h2>⚡ Đặc điểm F_System vs H_System</h2>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:20px">
  <div class="chart-wrap">
    <h3 style="font-size:12px;color:#f8fafc;margin-bottom:10px">H_System (Equity)</h3>
    <div class="pos-map">
      <span class="pos-badge" style="background:#7f1d1d;color:#fca5a5">CRISIS → 0% (cash)</span>
      <span class="pos-badge" style="background:#7c2d12;color:#fdba74">BEAR → +20%</span>
      <span class="pos-badge" style="background:#1e293b;color:#94a3b8;border:1px solid #334155">NEUTRAL → +70%</span>
      <span class="pos-badge" style="background:#14532d;color:#86efac">BULL → +100%</span>
      <span class="pos-badge" style="background:#3b0764;color:#c4b5fd">EX-BULL → +130%</span>
    </div>
    <div style="font-size:11px;color:#64748b;margin-top:6px">
      ⚠ T+2 settlement · TC=0.1% · Ramp 3 sessions · Chỉ Long / Cash<br>
      CRISIS = thua lỗ cơ hội (đứng ngoài thị trường giảm)
    </div>
  </div>
  <div class="chart-wrap" style="border-color:#22c55e">
    <h3 style="font-size:12px;color:#4ade80;margin-bottom:10px">F_System (Futures)</h3>
    <div class="pos-map">
      <span class="pos-badge" style="background:#7f1d1d;color:#fca5a5">CRISIS → <strong>−100% SHORT</strong></span>
      <span class="pos-badge" style="background:#7c2d12;color:#fdba74">BEAR → −30% SHORT</span>
      <span class="pos-badge" style="background:#1e293b;color:#94a3b8;border:1px solid #334155">NEUTRAL → Flat 0%</span>
      <span class="pos-badge" style="background:#14532d;color:#86efac">BULL → +100%</span>
      <span class="pos-badge" style="background:#3b0764;color:#c4b5fd">EX-BULL → +150%</span>
    </div>
    <div style="font-size:11px;color:#64748b;margin-top:6px">
      ✅ T+0 snap · TC=0.03% · Không ramp · Long + <strong>Short</strong><br>
      CRISIS = <strong>PROFIT từ thị trường giảm</strong> (short position)
    </div>
  </div>
</div>

<h2>📊 KPI So Sánh (từ 2011)</h2>
<div class="kpis">
  <div class="kpi-group">
    <h3>HT+Rec (H_System best)</h3>
    <div class="kpi"><span class="lbl">CAGR</span><span class="val {'green' if kpi_H.get('cagr',0)>0 else 'red'}">{kpi_H.get('cagr',0)*100:+.1f}%</span></div>
    <div class="kpi"><span class="lbl">Sharpe</span><span class="val">{kpi_H.get('sharpe',0):.2f}</span></div>
    <div class="kpi"><span class="lbl">MaxDD</span><span class="val red">{kpi_H.get('mdd',0)*100:.1f}%</span></div>
    <div class="kpi"><span class="lbl">Calmar</span><span class="val">{kpi_H.get('calmar',0):.2f}</span></div>
    <div class="kpi"><span class="lbl">NAV cuoi ky</span><span class="val">{kpi_H.get('final',0):.1f}t</span></div>
  </div>
  <div class="kpi-group" style="border-color:#22c55e">
    <h3 style="color:#4ade80">F_Balanced (best F)</h3>
    <div class="kpi"><span class="lbl">CAGR</span><span class="val {'green' if kpi_m.get('cagr',0)>0 else 'red'}">{kpi_m.get('cagr',0)*100:+.1f}%</span></div>
    <div class="kpi"><span class="lbl">Sharpe</span><span class="val">{kpi_m.get('sharpe',0):.2f}</span></div>
    <div class="kpi"><span class="lbl">MaxDD</span><span class="val red">{kpi_m.get('mdd',0)*100:.1f}%</span></div>
    <div class="kpi"><span class="lbl">Calmar</span><span class="val">{kpi_m.get('calmar',0):.2f}</span></div>
    <div class="kpi"><span class="lbl">NAV cuoi ky</span><span class="val green">{kpi_m.get('final',0):.1f}t</span></div>
  </div>
  <div class="kpi-group">
    <h3>B&H (tham chieu)</h3>
    <div class="kpi"><span class="lbl">CAGR</span><span class="val {'green' if kpi_bh.get('cagr',0)>0 else 'red'}">{kpi_bh.get('cagr',0)*100:+.1f}%</span></div>
    <div class="kpi"><span class="lbl">Sharpe</span><span class="val">{kpi_bh.get('sharpe',0):.2f}</span></div>
    <div class="kpi"><span class="lbl">MaxDD</span><span class="val red">{kpi_bh.get('mdd',0)*100:.1f}%</span></div>
    <div class="kpi"><span class="lbl">Calmar</span><span class="val">{kpi_bh.get('calmar',0):.2f}</span></div>
    <div class="kpi"><span class="lbl">NAV cuoi ky</span><span class="val">{kpi_bh.get('final',0):.1f}t</span></div>
  </div>
</div>

<div class="charts-row">
  <div class="chart-wrap"><h3 style="font-size:12px;color:#94a3b8;margin-bottom:10px">NAV (log scale, base=100)</h3>
    <canvas id="navChart" height="200"></canvas></div>
  <div class="chart-wrap"><h3 style="font-size:12px;color:#94a3b8;margin-bottom:10px">Drawdown</h3>
    <canvas id="ddChart" height="200"></canvas></div>
</div>

<h2>📋 Bảng Metrics Đầy Đủ</h2>
<div class="tbl-wrap">
<table>
<thead><tr>
  <th>Hệ thống</th><th>Giai đoạn</th>
  <th>CAGR</th><th>Sharpe</th><th>Sortino</th><th>MaxDD</th><th>Calmar</th><th>NAV</th>
</tr></thead>
<tbody>{metric_rows}</tbody>
</table>
</div>

<h2>📅 Kết Quả Hàng Năm (từ 2011)</h2>
<div class="tbl-wrap">
<table>
<thead><tr>
  <th>Năm</th><th>HT+Rec</th>
  <th style="color:#4ade80">F_Balanced</th>
  <th>F_Aggressive</th><th style="color:#60a5fa">B&H</th><th>Ghi chú</th>
</tr></thead>
<tbody>{ann_rows}</tbody>
</table>
</div>

<div class="note">
  <strong>Thiết kế F_System:</strong><br>
  • <strong>Signal</strong>: Cùng 7-factor pipeline (P3M, MA200, RSI, MACD, CMF, Breadth) → r_ema (EMA=0.40)<br>
  • <strong>State → Position</strong>: CRISIS=−100% SHORT | BEAR=−30% | NEUTRAL=Flat | BULL=+100% | EX-BULL=+150%<br>
  • <strong>Execution</strong>: T+0 snap (futures settlement), không ramp<br>
  • <strong>Chi phí</strong>: TC=0.03% round-trip (vs H_System 0.1%) | Roll cost=0.10%/tháng=1.2%/yr trên |position|<br>
  • <strong>Underlying</strong>: VN30 từ 2012-02-06 (chuẩn hóa về VNINDEX), VNINDEX trước đó<br>
  • <strong>BearDvg gate</strong>: Giữ nguyên — khi gate active, CRISIS SHORT là beneficial<br>
  • <strong>Lưu ý</strong>: VN30F thực tế ra đời 2017; backtest trước 2017 dùng VN30 index như proxy (basis risk không được mô hình hóa)
</div>

<script>
const labels = {json.dumps(dates_s)};
const nav = {json.dumps(nav_data)};
const dd  = {json.dumps(dd_data)};

const c1 = document.getElementById('navChart').getContext('2d');
new Chart(c1, {{
  type: 'line',
  data: {{
    labels,
    datasets: [
      {{label:'HT+Rec',    data:nav['H+Rec'],      borderColor:'#60a5fa',borderWidth:1.5,pointRadius:0,tension:0.3}},
      {{label:'F_Balanced',data:nav['F_Balanced'],  borderColor:'#4ade80',borderWidth:2,  pointRadius:0,tension:0.3}},
      {{label:'F_Aggr',    data:nav['F_Aggressive'],borderColor:'#a78bfa',borderWidth:1.5,pointRadius:0,tension:0.3}},
      {{label:'B&H',       data:nav['BH'],          borderColor:'#94a3b8',borderWidth:1,  pointRadius:0,tension:0.3,borderDash:[4,4]}},
    ]
  }},
  options: {{
    responsive:true, animation:false,
    scales: {{
      x: {{ticks:{{maxTicksLimit:10,color:'#475569'}}, grid:{{color:'#1e293b'}}}},
      y: {{type:'logarithmic', ticks:{{color:'#475569'}}, grid:{{color:'#1e293b'}}}}
    }},
    plugins: {{legend:{{labels:{{color:'#94a3b8',font:{{size:11}}}}}}, tooltip:{{mode:'index',intersect:false}}}}
  }}
}});

const c2 = document.getElementById('ddChart').getContext('2d');
new Chart(c2, {{
  type: 'line',
  data: {{
    labels,
    datasets: [
      {{label:'HT+Rec',    data:dd['H+Rec'],      borderColor:'#60a5fa',borderWidth:1.5,pointRadius:0,fill:false,tension:0.3}},
      {{label:'F_Balanced',data:dd['F_Balanced'],  borderColor:'#4ade80',borderWidth:2,  pointRadius:0,fill:false,tension:0.3}},
      {{label:'F_Aggr',    data:dd['F_Aggressive'],borderColor:'#a78bfa',borderWidth:1.5,pointRadius:0,fill:false,tension:0.3}},
      {{label:'B&H',       data:dd['BH'],          borderColor:'#94a3b8',borderWidth:1,  pointRadius:0,fill:false,tension:0.3,borderDash:[4,4]}},
    ]
  }},
  options: {{
    responsive:true, animation:false,
    scales: {{
      x: {{ticks:{{maxTicksLimit:10,color:'#475569'}}, grid:{{color:'#1e293b'}}}},
      y: {{ticks:{{color:'#475569',callback:v=>v+'%'}}, grid:{{color:'#1e293b'}}}}
    }},
    plugins: {{legend:{{labels:{{color:'#94a3b8',font:{{size:11}}}}}}, tooltip:{{mode:'index',intersect:false}}}}
  }}
}});
</script>
</body>
</html>"""

out = WORKDIR + "/f_system_report.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print(f"\nSaved: {out}")
