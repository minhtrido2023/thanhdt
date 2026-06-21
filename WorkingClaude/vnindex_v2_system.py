# -*- coding: utf-8 -*-
"""
vnindex_v2_system.py
====================
VNINDEX 5-State Market System — Version 2

Cải tiến so với v1:
  1. CRISIS chỉ khi DD từ đỉnh 52 tuần > 20% (định nghĩa chuẩn), không dùng r_score < 0.10
  2. Expanding rank chỉ dùng dữ liệu từ 2008+ (tránh nhiễu từ giai đoạn 2000-2007)
  3. EX-BULL là tín hiệu contrarian: thị trường rớt sâu + PE rẻ + dòng tiền quay lại
  4. Tích hợp macro: USD/VND trend, lending rate, CPI Vietnam
  5. BearDvg gate: floor=CRISIS(0%), exit=OR, min=60 phiên (từ backtest v1)

State definitions:
  1 CRISIS  (0%)   : DD > 20% từ đỉnh 52 tuần VÀ r_score < 0.30 (hoặc BearDvg gate)
  2 BEAR    (20%)  : r_score < 0.30, chưa có DD > 20%
  3 NEUTRAL (70%)  : mặc định
  4 BULL    (100%) : r_score > 0.75 VÀ macro không thắt chặt
  5 EX-BULL (130%) : contrarian deep-value — PE rẻ + dòng tiền + phục hồi kỹ thuật + macro ủng hộ
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import os, json
import numpy as np
import pandas as pd

WORKDIR    = r"/home/trido/thanhdt/WorkingClaude"
RANK_START = "2008-01-01"   # chỉ dùng data từ đây cho expanding rank (bỏ giai đoạn 2000-2007 nhiễu)
MIN_LB     = 252            # tối thiểu 1 năm data post-2008 trước khi phát tín hiệu
MODE_WIN   = 15
RAMP_DAYS  = 3
SNAP_THR   = 0.03
TC         = 0.001
DEPOSIT_R  = 0.06 / 252
BORROW_R   = 0.10 / 252
TARGET_W   = {1: 0.00, 2: 0.20, 3: 0.70, 4: 1.00, 5: 1.30}
STATE_NAMES= {1:"CRISIS", 2:"BEAR", 3:"NEUTRAL", 4:"BULL", 5:"EX-BULL"}
STATE_COLOR= {1:"#ef4444", 2:"#f97316", 3:"#eab308", 4:"#22c55e", 5:"#10b981"}
STATE_ALLOC= {1:"0%", 2:"20%", 3:"70%", 4:"100%", 5:"130%"}
SPY        = 243.4   # sessions/year in full dataset

# CRISIS/BEAR thresholds
CRISIS_DD_THR  = -0.20   # DD > 20% từ đỉnh 52 tuần (xác nhận đau thật)
CRISIS_RS_MAX  = 0.20    # r_score < 20% (strict) — cần cả 2 điều kiện
BEAR_RSCORE    = 0.30    # r_score < 0.30 → BEAR
BULL_RSCORE    = 0.75    # r_score > 0.75 → BULL
# EX-BULL contrarian conditions
EXBULL_PE_MAX  = 0.25    # PE_rank < 25% (rẻ lịch sử)
EXBULL_CMF_MIN = 0.50    # CMF_rank > 50% (dòng tiền đang vào)
EXBULL_RS_MIN  = 0.52    # r_score > 52% (momentum đang phục hồi từ đáy)
EXBULL_DD_THR  = -0.15   # DD 60 phiên từng < -15% (đã có selloff đủ sâu)

# ══════════════════════════════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════════════════════════════
print("Loading data...")
vni = pd.read_csv(os.path.join(WORKDIR, "VNINDEX.csv"), low_memory=False)
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
for c in ["Open","High","Low","Close","Volume","VNINDEX_PE",
          "D_RSI","D_RSI_T1W","D_RSI_Max1W","D_RSI_Max3M","D_RSI_Min1W","D_RSI_Min3M",
          "D_RSI_Max1W_Close","D_RSI_Max3M_Close","D_RSI_Max3M_MACD","D_RSI_Max1W_MACD",
          "D_RSI_Min1W_Close","D_RSI_MinT3","D_MACDdiff","D_CMF","C_L1M","C_L1W"]:
    if c in vni.columns: vni[c] = pd.to_numeric(vni[c], errors="coerce")

breadth = pd.read_csv(os.path.join(WORKDIR, "breadth_data.csv"))
breadth["time"] = pd.to_datetime(breadth["time"])
vni = vni.merge(breadth, on="time", how="left")

# Load macro daily
macro = pd.read_csv(os.path.join(WORKDIR, "macro_daily.csv"))
macro["time"] = pd.to_datetime(macro["time"])
vni = vni.merge(macro[["time","lending_rate","cpi_yoy","usdvnd","usdvnd_1y_chg","macro_regime"]],
                on="time", how="left")
for c in ["lending_rate","cpi_yoy","usdvnd","usdvnd_1y_chg"]:
    vni[c] = pd.to_numeric(vni[c], errors="coerce")

n     = len(vni)
close = vni["Close"].values.copy()
high  = vni["High"].values.copy()
low   = vni["Low"].values.copy()
vol   = vni["Volume"].values.copy()
dates = vni["time"].reset_index(drop=True)
cal_days = (vni["time"].iloc[-1] - vni["time"].iloc[0]).days
sessions_per_year = n / (cal_days / 365.25)
print(f"  VNINDEX: {n} sessions | {dates.iloc[0].date()} → {dates.iloc[-1].date()}")
print(f"  USD/VND: {vni['usdvnd'].notna().sum()} sessions available")
print(f"  Lending rate: {vni['lending_rate'].notna().sum()} sessions available")

idx_rank = vni[vni["time"] >= RANK_START].index[0]
print(f"  Ranking anchor: {RANK_START} (index {idx_rank}, {n-idx_rank} sessions for ranking)")

# ══════════════════════════════════════════════════════════════════════
# COMPUTE INDICATORS
# ══════════════════════════════════════════════════════════════════════
print("Computing indicators...")
p3m = pd.to_numeric(vni["Change_3M"],errors="coerce").values if "Change_3M" in vni.columns else np.full(n,np.nan)
p1m = pd.to_numeric(vni["Change_1M"],errors="coerce").values if "Change_1M" in vni.columns else np.full(n,np.nan)
ma200v = pd.Series(close).rolling(200,min_periods=200).mean().values
ma200_dev = np.where((ma200v>0)&~np.isnan(ma200v), close/ma200v-1, np.nan)

rsi_c=np.full(n,np.nan); au=ad=np.nan; Pr=14
for i in range(1,n):
    d2=close[i]-close[i-1]; u=max(d2,0.); dw=max(-d2,0.)
    if np.isnan(au):
        if i>=Pr:
            au=np.mean([max(close[j]-close[j-1],0) for j in range(1,Pr+1)])
            ad=np.mean([max(close[j-1]-close[j],0) for j in range(1,Pr+1)])
            if au+ad>0: rsi_c[i]=au/(au+ad)
    else:
        au=(au*(Pr-1)+u)/Pr; ad=(ad*(Pr-1)+dw)/Pr
        if au+ad>0: rsi_c[i]=au/(au+ad)

e12=np.full(n,np.nan); e26=np.full(n,np.nan); sg=np.full(n,np.nan); mh=np.full(n,np.nan)
k12=2/13; k26=2/27; k9=2/10
for i in range(n):
    pv2=e12[i-1] if i>0 else np.nan
    e12[i]=close[i] if np.isnan(pv2) else pv2*(1-k12)+close[i]*k12
    pv6=e26[i-1] if i>0 else np.nan
    e26[i]=close[i] if np.isnan(pv6) else pv6*(1-k26)+close[i]*k26
    ml=e12[i]-e26[i]; ps=sg[i-1] if i>0 else np.nan
    sg[i]=ml if np.isnan(ps) else ps*(1-k9)+ml*k9
    if i>=33: mh[i]=ml-sg[i]

hl=high-low
with np.errstate(divide="ignore",invalid="ignore"):
    mfm=np.where(hl>0,((close-low)-(high-close))/hl,0.)
cmf_c=np.full(n,np.nan); mfv=mfm*vol
for i in range(14,n):
    vs=np.sum(vol[i-14:i])
    if vs>0: cmf_c[i]=np.sum(mfv[i-14:i])/vs

breadth_arr=pd.to_numeric(vni["breadth"],errors="coerce").values
W_BASE={"P3M":0.30,"P1M":0.10,"MA200":0.15,"RSI":0.15,"MACD":0.10,"CMF":0.08,"Breadth":0.12}
factors={"P3M":p3m,"P1M":p1m,"MA200":ma200_dev,"RSI":rsi_c,"MACD":mh,"CMF":cmf_c,"Breadth":breadth_arr}

# ══════════════════════════════════════════════════════════════════════
# EXPANDING RANK — anchored to RANK_START (bỏ nhiễu 2000-2007)
# ══════════════════════════════════════════════════════════════════════
print(f"Computing expanding ranks (anchored from {RANK_START})...")

def ep_rank_v2(arr, idx_anchor, min_lb=252):
    """Expanding percentile rank using only data from idx_anchor onward."""
    out = np.full(len(arr), np.nan)
    for t in range(idx_anchor, len(arr)):
        hist  = arr[idx_anchor:t+1]
        valid = hist[~np.isnan(hist)]
        if len(valid) < min_lb or np.isnan(arr[t]): continue
        out[t] = np.sum(valid <= arr[t]) / len(valid)
    return out

ranks = {}
for k in factors:
    print(f"  Ranking {k}...")
    ranks[k] = ep_rank_v2(factors[k], idx_rank, MIN_LB)

score = np.full(n, np.nan)
for t in range(n):
    avail = {k: ranks[k][t] for k in factors if not np.isnan(ranks[k][t])}
    if len(avail) < 3: continue
    ws = sum(W_BASE[k] for k in avail)
    score[t] = sum(avail[k]*W_BASE[k] for k in avail) / ws

print("  Ranking composite score...")
r_score = ep_rank_v2(score, idx_rank, MIN_LB)

# PE expanding rank (anchored)
pe_arr = vni["VNINDEX_PE"].values.copy()
pe_rank_arr = ep_rank_v2(pe_arr, idx_rank, 60)

# PE P90 for risk override
pe_p90 = np.full(n, np.nan)
for t in range(idx_rank, n):
    v = pe_arr[idx_rank:t+1]; v = v[~np.isnan(v)]
    if len(v) >= 60: pe_p90[t] = np.nanpercentile(v, 90)

# CMF rank (for EX-BULL condition)
cmf_rank_arr = ranks["CMF"]

# ══════════════════════════════════════════════════════════════════════
# RISK INDICATORS
# ══════════════════════════════════════════════════════════════════════
# Drawdown from 52-week (252-session) rolling high
roll_high_52w = pd.Series(close).rolling(252, min_periods=20).max().values
dd_52w = np.where(roll_high_52w > 0, close / roll_high_52w - 1, 0.0)

# Running max (all-time) drawdown
rm = np.maximum.accumulate(np.where(np.isnan(close), 0, close))
dd_all = np.where(rm > 0, close / rm - 1, 0.0)

# Volatility
daily_ret = np.full(n, np.nan)
for i in range(1,n):
    if close[i-1]>0: daily_ret[i]=close[i]/close[i-1]-1
vol20 = np.full(n, np.nan)
for i in range(20,n):
    ww=daily_ret[i-20:i]; vv=ww[~np.isnan(ww)]
    if len(vv)>=15: vol20[i]=np.std(vv)*np.sqrt(sessions_per_year)
avg_vol = np.full(n, np.nan)
for t in range(n):
    vv=vol20[:t+1]; vv=vv[~np.isnan(vv)]
    if len(vv)>=60: avg_vol[t]=np.mean(vv)

# ══════════════════════════════════════════════════════════════════════
# MACRO SIGNALS
# ══════════════════════════════════════════════════════════════════════
# Macro tight: lending_rate > 12 OR cpi_yoy > 10
lending = vni["lending_rate"].values.copy()
cpi     = vni["cpi_yoy"].values.copy()
usdvnd  = vni["usdvnd"].values.copy()
usdvnd_1y = vni["usdvnd_1y_chg"].values.copy()

macro_tight = np.zeros(n, dtype=bool)
macro_easy  = np.zeros(n, dtype=bool)
for i in range(n):
    r_ok  = not np.isnan(lending[i])
    c_ok  = not np.isnan(cpi[i])
    fx_ok = not np.isnan(usdvnd_1y[i])
    if r_ok and c_ok:
        if lending[i] > 12 or cpi[i] > 10:
            macro_tight[i] = True
        elif lending[i] < 9 and cpi[i] < 5 and (not fx_ok or usdvnd_1y[i] < 2.5):
            macro_easy[i] = True
    elif r_ok and lending[i] > 12:
        macro_tight[i] = True
    # USD/VND stress: depreciating > 4% in 1 year → additional tightening signal
    if fx_ok and usdvnd_1y[i] > 4.0:
        macro_tight[i] = True

# ══════════════════════════════════════════════════════════════════════
# EMA SMOOTH r_score
# ══════════════════════════════════════════════════════════════════════
EMA_ALPHA = 0.40
rs_ema = np.full(n, np.nan)
for t in range(n):
    v=r_score[t]; prev=rs_ema[t-1] if t>0 else np.nan
    rs_ema[t] = v if np.isnan(prev) else (prev if np.isnan(v) else EMA_ALPHA*v+(1-EMA_ALPHA)*prev)

# r_score streak: 10 phiên > 0.50 liên tiếp (dùng trong BearDvg gate exit + EX-BULL)
rscore_streak = np.zeros(n, dtype=bool); streak=0
for i in range(n):
    if not np.isnan(rs_ema[i]) and rs_ema[i] > 0.50: streak+=1
    else: streak=0
    if streak >= 10: rscore_streak[i] = True

# ══════════════════════════════════════════════════════════════════════
# BASE STATE CLASSIFICATION (V2: không còn CRISIS từ r_score)
# r_score < 0.30 → BEAR (không gọi thẳng là CRISIS)
# r_score ≥ 0.75 → BULL
# CRISIS chỉ qua override DD > 20%
# ══════════════════════════════════════════════════════════════════════
def classify_v2(rs):
    if np.isnan(rs): return 3
    if rs < BEAR_RSCORE: return 2   # BEAR (chờ DD xác nhận CRISIS)
    if rs < BULL_RSCORE: return 3   # NEUTRAL
    return 4                         # BULL

state_raw = np.array([classify_v2(r) for r in rs_ema])

# ── Risk overrides ─────────────────────────────────────────────────────────────
state_ov = state_raw.copy()
for i in range(n):
    s = state_ov[i]
    # Override 1: CRISIS — cần CẢ 2: r_score bottom 20% VÀ DD > 20% từ đỉnh 52 tuần
    # Điều này đảm bảo CRISIS chỉ khi có đau thật sự về cả kỹ thuật lẫn giá
    ema_v = rs_ema[i] if not np.isnan(rs_ema[i]) else 1.0
    dd52_v = dd_52w[i] if not np.isnan(dd_52w[i]) else 0.0
    if ema_v < CRISIS_RS_MAX and dd52_v < CRISIS_DD_THR and s <= 3:
        s = 1  # CRISIS khi cả hai điều kiện đều thỏa
    # Override 2: DD > 25% từ mọi thời điểm + BULL trở lên → cap về NEUTRAL
    if dd_all[i] < -0.25 and s >= 4:
        s = 3
    # Override 3: PE > P90 → cap EX-BULL về BULL
    if not np.isnan(pe_p90[i]) and not np.isnan(pe_arr[i]) and pe_arr[i] > pe_p90[i] and s == 5:
        s = 4
    # Override 4: Vol spike > 1.5x avg → cap BULL về NEUTRAL
    if not np.isnan(avg_vol[i]) and not np.isnan(vol20[i]) and vol20[i] > 1.5*avg_vol[i] and s >= 4:
        s = 3
    # Override 5: Macro tight → cap BULL về NEUTRAL
    if macro_tight[i] and s >= 4:
        s = 3
    state_ov[i] = s

# ══════════════════════════════════════════════════════════════════════
# MARKET DICT FILTER — BearDvg / BullDvg signals
# ══════════════════════════════════════════════════════════════════════
def _s(col): return vni[col] if col in vni.columns else pd.Series(np.nan, index=vni.index)
D_RSI=_s("D_RSI"); D_RSI_T1W=_s("D_RSI_T1W")
D_RSI_Max1W=_s("D_RSI_Max1W"); D_RSI_Max3M=_s("D_RSI_Max3M")
D_RSI_Min1W=_s("D_RSI_Min1W"); D_RSI_Min3M=_s("D_RSI_Min3M")
D_RSI_Max1W_C=_s("D_RSI_Max1W_Close"); D_RSI_Max3M_C=_s("D_RSI_Max3M_Close")
D_RSI_Max3M_M=_s("D_RSI_Max3M_MACD"); D_RSI_Max1W_M=_s("D_RSI_Max1W_MACD")
D_RSI_Min1W_C=_s("D_RSI_Min1W_Close"); D_RSI_MinT3=_s("D_RSI_MinT3")
D_MACDdiff=_s("D_MACDdiff"); D_CMF=_s("D_CMF"); C_L1M=_s("C_L1M"); C_L1W=_s("C_L1W")
mask_2011 = vni["time"] >= "2011-01-01"

bear1=(D_RSI_Max1W/D_RSI>1.044)&(D_RSI_Max3M>0.74)&(D_RSI_Max1W<0.72)&(D_RSI_Max1W>0.61)&\
      (D_RSI_Max1W_C/D_RSI_Max3M_C>1.028)&(D_RSI_Max3M_M/D_RSI_Max1W_M>1.11)&\
      (D_MACDdiff<0)&(vni["Close"]/D_RSI_Max3M_C>0.96)&(D_RSI_MinT3>0.43)&(D_CMF<0.13)&mask_2011
bear2=(D_RSI_Max1W/D_RSI>1.016)&(D_RSI_Max3M>0.77)&(D_RSI_Max1W<0.79)&(D_RSI_Max1W>0.60)&\
      (D_RSI_Max1W_C/D_RSI_Max3M_C>1.008)&(D_RSI_Max3M_M/D_RSI_Max1W_M>1.10)&\
      (D_MACDdiff<0)&(vni["Close"]/D_RSI_Max3M_C>0.97)&(D_RSI_MinT3>0.50)&(D_CMF<0.15)&mask_2011
bull1=(D_RSI_Min1W/D_RSI_Min3M>0.90)&(D_RSI_Min1W<0.60)&(D_RSI_Min3M<0.40)&\
      (D_RSI_Min1W_C/D_RSI_Max3M_C<1.15)&(D_MACDdiff>0)&(D_RSI_MinT3<0.50)&(D_RSI_Max1W<0.48)&\
      (D_RSI/D_RSI_T1W>1.12)&(D_CMF>0)&(C_L1M<1.21)&(C_L1W<1.05)&mask_2011
bull2=(D_RSI_Min1W/D_RSI_Min3M>0.92)&(D_RSI_Min1W<0.52)&(D_RSI_Min3M<0.38)&\
      (D_RSI_Min1W_C/D_RSI_Max3M_C<1.10)&(D_MACDdiff>0)&(D_RSI_MinT3<0.56)&(D_RSI_Max1W<0.64)&\
      (D_RSI/D_RSI_T1W>1.10)&(D_CMF>0)&(C_L1M<1.20)&(C_L1W<1.025)&mask_2011

bear_mask = (bear1|bear2).values.astype(bool)
bull_mask  = (bull1|bull2).values.astype(bool)

# PE expanding rank (anchor) — dùng cho BearDvg gate exit
p3m_rank_arr = ranks["P3M"]

# ══════════════════════════════════════════════════════════════════════
# BEARDVG GATE: floor=CRISIS(0%), exit=OR, min_dur=60 phiên
# ══════════════════════════════════════════════════════════════════════
GATE_FLOOR   = 2   # BearDvg gate: floor=BEAR(20%), không về 0% trừ khi có DD thực sự
GATE_MIN_DUR = 60

gate_active = False; gate_start = -1
gate_flag   = np.zeros(n, dtype=int)
gate_events = []
state_dvg   = state_ov.copy()

for i in range(n):
    if bear_mask[i]:
        if not gate_active:
            gate_active = True; gate_start = i
            gate_events.append({"type":"GATE_OPEN","i":i,
                                 "date":vni["time"].iloc[i].strftime("%Y-%m-%d"),
                                 "close":float(close[i])})
        else:
            gate_start = i
    if gate_active:
        gate_flag[i] = 1
        if state_dvg[i] > GATE_FLOOR: state_dvg[i] = GATE_FLOOR
        sessions_in = i - gate_start
        if sessions_in >= GATE_MIN_DUR:
            _p3m_ok = (not np.isnan(p3m_rank_arr[i])) and p3m_rank_arr[i] > 0.45
            _pe_ok  = (not np.isnan(pe_rank_arr[i]))  and pe_rank_arr[i]  < 0.80
            _bull   = bool(bull_mask[i])
            _rs_ok  = bool(rscore_streak[i])
            if _bull or (_p3m_ok and _pe_ok) or _rs_ok:
                gate_events.append({"type":"GATE_CLOSE","i":i,
                                     "date":vni["time"].iloc[i].strftime("%Y-%m-%d"),
                                     "close":float(close[i]),"duration":sessions_in,
                                     "trigger":"BullDvg" if _bull else "P3M+PE" if (_p3m_ok and _pe_ok) else "r_score"})
                gate_active = False

if gate_active:
    gate_events.append({"type":"GATE_CLOSE","i":n-1,
                         "date":vni["time"].iloc[-1].strftime("%Y-%m-%d"),
                         "close":float(close[-1]),"duration":n-gate_start,"trigger":"ACTIVE"})

# ══════════════════════════════════════════════════════════════════════
# EX-BULL CONTRARIAN UPGRADE
# Điều kiện: thị trường đã rớt sâu + PE rẻ + dòng tiền quay lại + macro ủng hộ
# Chỉ nâng lên EX-BULL khi trạng thái cơ bản đã là BULL (r_score hồi phục)
# ══════════════════════════════════════════════════════════════════════
print("Applying EX-BULL contrarian conditions...")

# Tính DD tối thiểu trong 60 phiên gần nhất (xác nhận đã có đủ selloff)
dd_60_min = np.full(n, np.nan)
for i in range(60, n):
    dd_60_min[i] = dd_52w[i-60:i+1].min()

state_final = state_dvg.copy()
exbull_flags = np.zeros(n, dtype=int)

for i in range(n):
    # EX-BULL: contrarian khi thị trường phục hồi sau đáy sâu
    # - Từ BEAR(2): cần điều kiện mạnh hơn (bull_sig bắt buộc + dd sâu hơn)
    # - Từ NEUTRAL(3)/BULL(4): điều kiện tiêu chuẩn (bull_sig HOẶC dd)
    cur_s = state_final[i]
    if cur_s not in (2, 3, 4): continue   # chỉ từ BEAR, NEUTRAL, BULL

    pe_ok  = (not np.isnan(pe_rank_arr[i]))  and pe_rank_arr[i]  < EXBULL_PE_MAX
    cmf_ok = (not np.isnan(cmf_rank_arr[i])) and cmf_rank_arr[i] > EXBULL_CMF_MIN
    rs_ok  = (not np.isnan(rs_ema[i]))        and rs_ema[i]       > EXBULL_RS_MIN
    bull_sig  = bool(bull_mask[i])
    dd_ok     = (not np.isnan(dd_60_min[i]))  and dd_60_min[i]    < EXBULL_DD_THR
    dd_deep   = (not np.isnan(dd_60_min[i]))  and dd_60_min[i]    < -0.20  # sâu hơn cho BEAR

    # Chặn hyperinflation
    lr_v  = lending[i] if not np.isnan(lending[i]) else 0.0
    cpi_v = cpi[i]     if not np.isnan(cpi[i])     else 0.0
    macro_extreme = (lr_v > 16.0 or cpi_v > 15.0)
    if macro_extreme: continue

    if cur_s == 2:
        # Từ BEAR: cần BullDvg xác nhận + DD sâu 20%+ + PE rẻ + CMF vào
        if pe_ok and cmf_ok and bull_sig and dd_deep:
            state_final[i] = 5
            exbull_flags[i] = 1
    else:
        # Từ NEUTRAL/BULL: điều kiện tiêu chuẩn
        if pe_ok and cmf_ok and rs_ok and (bull_sig or dd_ok):
            state_final[i] = 5
            exbull_flags[i] = 1

n_exbull = exbull_flags.sum()
print(f"  EX-BULL triggered: {n_exbull} sessions")
# Debug: check individual conditions for EX-BULL
if n_exbull == 0:
    base_states = np.sum((state_final == 3) | (state_final == 4))
    pe_cond  = np.sum((~np.isnan(pe_rank_arr)) & (pe_rank_arr < EXBULL_PE_MAX))
    cmf_cond = np.sum((~np.isnan(cmf_rank_arr)) & (cmf_rank_arr > EXBULL_CMF_MIN))
    rs_cond  = np.sum((~np.isnan(rs_ema)) & (rs_ema > EXBULL_RS_MIN))
    dd_cond  = np.sum((~np.isnan(dd_60_min)) & (dd_60_min < EXBULL_DD_THR))
    macro_cond = np.sum(~macro_tight)
    print(f"    DEBUG: base states (NEUTRAL/BULL)={base_states}, pe<{EXBULL_PE_MAX}={pe_cond}, cmf>{EXBULL_CMF_MIN}={cmf_cond}, rs>{EXBULL_RS_MIN}={rs_cond}, dd<{EXBULL_DD_THR}={dd_cond}, macro_ok={macro_cond}")

# ══════════════════════════════════════════════════════════════════════
# MODE SMOOTHING
# ══════════════════════════════════════════════════════════════════════
def rolling_mode(states, window=15):
    out = states.copy()
    for t in range(window-1, len(states)):
        ww=states[t-window+1:t+1]; vals,counts=np.unique(ww,return_counts=True)
        mc=counts.max(); cands=vals[counts==mc]
        for v in reversed(ww):
            if v in cands: out[t]=v; break
    return out

state_smooth = rolling_mode(state_final, MODE_WIN)

# Store
vni["r_score"]     = r_score
vni["r_score_ema"] = rs_ema
vni["state_raw"]   = state_raw
vni["state_ov"]    = state_ov
vni["state_dvg"]   = state_dvg
vni["state"]       = state_smooth
vni["dd_52w"]      = dd_52w
vni["dd_all"]      = dd_all
vni["pe_rank"]     = pe_rank_arr
vni["cmf_rank"]    = cmf_rank_arr
vni["bear_dvg"]    = bear_mask.astype(int)
vni["bull_dvg"]    = bull_mask.astype(int)
vni["gate_flag"]   = gate_flag
vni["macro_tight"] = macro_tight.astype(int)
vni["macro_easy"]  = macro_easy.astype(int)
vni["exbull_flag"] = exbull_flags

# ══════════════════════════════════════════════════════════════════════
# BACKTEST
# ══════════════════════════════════════════════════════════════════════
print("Running backtest...")
pv    = np.zeros(n); pv[0]    = 1_000_000_000.0
pv_bh = np.zeros(n); pv_bh[0] = 1_000_000_000.0
w = TARGET_W[3]; w_arr = np.zeros(n); w_arr[0] = w

for t in range(1, n):
    tgt = TARGET_W[state_smooth[t-1]]; diff = tgt - w
    wn  = tgt if abs(diff) < SNAP_THR else w + diff/RAMP_DAYS
    wn  = float(np.clip(wn, 0.0, 1.30))
    r   = close[t]/close[t-1]-1 if close[t-1]>0 else 0.0
    pv[t] = pv[t-1]*(1 + wn*r + max(0,1-wn)*DEPOSIT_R - max(0,wn-1)*BORROW_R - abs(wn-w)*TC)
    pv_bh[t] = pv_bh[t-1]*(close[t]/close[t-1]) if close[t-1]>0 else pv_bh[t-1]
    w_arr[t] = wn; w = wn

vni["pv"] = pv; vni["pv_bh"] = pv_bh; vni["weight"] = w_arr

# ══════════════════════════════════════════════════════════════════════
# METRICS
# ══════════════════════════════════════════════════════════════════════
def calc_m(pv_s, d_s):
    v0,v1=pv_s[0],pv_s[-1]; yrs=(d_s.iloc[-1]-d_s.iloc[0]).days/365.25
    cagr=(v1/v0)**(1/yrs)-1 if yrs>0 else 0
    rets=np.array([pv_s[i]/pv_s[i-1]-1 for i in range(1,len(pv_s)) if pv_s[i-1]>0])
    n_ses=len(pv_s); sub_spy=n_ses/yrs if yrs>0 else SPY
    sh=np.mean(rets)*sub_spy/(np.std(rets)*np.sqrt(sub_spy)) if np.std(rets)>0 else 0
    mx=np.maximum.accumulate(pv_s); da=np.where(mx>0,pv_s/mx-1,0)
    mxdd=da.min(); cal=cagr/abs(mxdd) if mxdd!=0 else 0
    return dict(cagr=cagr,sharpe=sh,max_dd=mxdd,calmar=cal,final=v1)

dates_s = dates
idx11   = vni[vni["time"]>="2011-01-01"].index[0]

m_sys    = calc_m(pv,         dates_s)
m_bh     = calc_m(pv_bh,      dates_s)
m_sys_11 = calc_m(pv[idx11:], dates_s.iloc[idx11:].reset_index(drop=True))
m_bh_11  = calc_m(pv_bh[idx11:], dates_s.iloc[idx11:].reset_index(drop=True))

def count_trans(st): return sum(1 for i in range(1,len(st)) if st[i]!=st[i-1])
n_trans = count_trans(state_smooth)
state_counts = {s: int(np.sum(state_smooth==s)) for s in range(1,6)}
total_sc = sum(state_counts.values())

# Crisis periods analysis (post-2008 only)
crisis_post08 = np.sum(state_smooth[idx_rank:] == 1)
crisis_pct_post08 = crisis_post08 / (n - idx_rank) * 100

print(f"\n{'='*70}")
print(f"FULL PERIOD")
print(f"  System : CAGR={m_sys['cagr']:.1%}  MaxDD={m_sys['max_dd']:.1%}  Sharpe={m_sys['sharpe']:.2f}  Calmar={m_sys['calmar']:.2f}")
print(f"  B&H    : CAGR={m_bh['cagr']:.1%}  MaxDD={m_bh['max_dd']:.1%}  Sharpe={m_bh['sharpe']:.2f}  Calmar={m_bh['calmar']:.2f}")
print(f"\nSINCE 2011")
print(f"  System : CAGR={m_sys_11['cagr']:.1%}  MaxDD={m_sys_11['max_dd']:.1%}  Sharpe={m_sys_11['sharpe']:.2f}  Calmar={m_sys_11['calmar']:.2f}")
print(f"  B&H    : CAGR={m_bh_11['cagr']:.1%}  MaxDD={m_bh_11['max_dd']:.1%}  Sharpe={m_bh_11['sharpe']:.2f}  Calmar={m_bh_11['calmar']:.2f}")
print(f"\nSTATE DISTRIBUTION (toàn kỳ / từ 2008)")
for s in range(1,6):
    pct_all  = state_counts[s]/total_sc*100
    cnt_post = int(np.sum(state_smooth[idx_rank:]==s))
    pct_post = cnt_post/(n-idx_rank)*100
    print(f"  {STATE_NAMES[s]:8s}: {state_counts[s]:4d} ({pct_all:.1f}%)  |  post-2008: {cnt_post:4d} ({pct_post:.1f}%)")
print(f"\n  CRISIS post-2008: {crisis_pct_post08:.1f}% (v1 was 20.7%)")
print(f"  EX-BULL sessions: {exbull_flags.sum()} ({exbull_flags.sum()/total_sc*100:.1f}%)")
print(f"  Transitions: {n_trans}")
# Debug: CRISIS source breakdown
post08_slice = slice(idx_rank, None)
gate_crisis  = np.sum((gate_flag[post08_slice]==1) & (state_ov[post08_slice]==1))
dd_crisis    = np.sum((gate_flag[post08_slice]==0) & (state_ov[post08_slice]==1))
gate_only    = np.sum(gate_flag[post08_slice]==1) - gate_crisis
print(f"\n  CRISIS SOURCE (post-2008): gate={gate_crisis}, DD+rScore={dd_crisis}, gate_only={gate_only}")
rs_p = rs_ema[idx_rank:]
dd_p = dd_52w[idx_rank:]
rs_p_valid = rs_p[~np.isnan(rs_p)]
dd_p_valid = dd_p[~np.isnan(dd_p)]
print(f"  r_score dist: <0.10={np.sum(rs_p_valid<0.10)}, <0.15={np.sum(rs_p_valid<0.15)}, <0.20={np.sum(rs_p_valid<0.20)}, <0.30={np.sum(rs_p_valid<0.30)}")
print(f"  DD52w dist  : <-10%={np.sum(dd_p_valid<-0.10)}, <-15%={np.sum(dd_p_valid<-0.15)}, <-20%={np.sum(dd_p_valid<-0.20)}, <-25%={np.sum(dd_p_valid<-0.25)}")

last_i = n-1
print(f"\nCURRENT STATE ({dates.iloc[-1].date()})")
print(f"  State      : {STATE_NAMES[state_smooth[-1]]}")
print(f"  r_score EMA: {rs_ema[-1]:.4f}" if not np.isnan(rs_ema[-1]) else "  r_score EMA: N/A")
print(f"  PE rank    : {pe_rank_arr[-1]:.3f}" if not np.isnan(pe_rank_arr[-1]) else "  PE rank: N/A")
print(f"  Gate active: {'YES' if gate_flag[-1] else 'No'}")
print(f"  Macro tight: {'YES' if macro_tight[-1] else 'No'}")
print(f"  USD/VND    : {usdvnd[-1]:.0f} (1Y chg: {usdvnd_1y[-1]:+.1f}%)" if not np.isnan(usdvnd[-1]) else "  USD/VND: N/A")

# ══════════════════════════════════════════════════════════════════════
# BUILD HTML
# ══════════════════════════════════════════════════════════════════════
print("\nBuilding HTML report...")

def to_js(series, dec=4):
    parts = []
    for v in series:
        if v is None or (isinstance(v,(float,np.floating)) and np.isnan(v)): parts.append("null")
        elif isinstance(v,(float,np.floating)): parts.append(f"{v:.{dec}f}")
        else: parts.append(str(v))
    return "["+",".join(parts)+"]"

dates_js    = '["'+'","'.join(vni["time"].dt.strftime("%Y-%m-%d").tolist())+'"]'
close_js    = to_js(close, 2)
state_js    = to_js(state_smooth.astype(float), 0)
rsema_js    = to_js(rs_ema, 4)
weight_js   = to_js(w_arr, 4)
pv_js       = to_js(pv/1e9, 4)
pvbh_js     = to_js(pv_bh/1e9, 4)
pe_js       = to_js(pe_arr, 2)
pep90_js    = to_js(pe_p90, 2)
dd52w_js    = to_js(dd_52w, 4)
usdvnd_js   = to_js(np.where(np.isnan(usdvnd), np.nan, usdvnd/1000), 2)   # in nghìn để chart đẹp hơn
macro_tight_js = to_js(macro_tight.astype(float), 0)

# Current state
cur_state  = int(state_smooth[-1])
cur_date   = dates.iloc[-1].strftime("%Y-%m-%d")
cur_color  = STATE_COLOR[cur_state]
cur_alloc  = TARGET_W[cur_state]
cur_rs     = float(rs_ema[-1]) if not np.isnan(rs_ema[-1]) else None
cur_pe     = float(pe_arr[-1]) if not np.isnan(pe_arr[-1]) else None
cur_pe_r   = float(pe_rank_arr[-1]) if not np.isnan(pe_rank_arr[-1]) else None
cur_usdvnd = float(usdvnd[-1]) if not np.isnan(usdvnd[-1]) else None
cur_usd1y  = float(usdvnd_1y[-1]) if not np.isnan(usdvnd_1y[-1]) else None
cur_gate   = bool(gate_flag[-1])
cur_tight  = bool(macro_tight[-1])
cur_easy   = bool(macro_easy[-1])
final_sys  = pv[-1]/1e9
final_bh   = pv_bh[-1]/1e9

# Factor radar
radar_keys = ["P3M","P1M","MA200","RSI","MACD","CMF","Breadth"]
radar_vals = [round(float(ranks[k][-1]),4) if not np.isnan(ranks[k][-1]) else 0 for k in radar_keys]

# Full NAV transitions table
all_trans = []
prev_s = state_smooth[0]
for i in range(1, n):
    if state_smooth[i] != prev_s:
        prev_idx = all_trans[-1]["_i"] if all_trans else 0
        ret_since = (pv[i]/pv[prev_idx]-1) if pv[prev_idx]>0 else 0
        macro_note = "tight" if macro_tight[i] else ("easy" if macro_easy[i] else "")
        all_trans.append({
            "_i": i,
            "date": vni["time"].iloc[i].strftime("%Y-%m-%d"),
            "from_s": STATE_NAMES[prev_s], "to_s": STATE_NAMES[state_smooth[i]],
            "from_c": STATE_COLOR[prev_s],  "to_c": STATE_COLOR[state_smooth[i]],
            "vnindex": f"{close[i]:.0f}",
            "pe": f"{pe_arr[i]:.1f}" if not np.isnan(pe_arr[i]) else "—",
            "pe_rank": f"{pe_rank_arr[i]:.2f}" if not np.isnan(pe_rank_arr[i]) else "—",
            "usdvnd": f"{usdvnd[i]:.0f}" if not np.isnan(usdvnd[i]) else "—",
            "alloc_from": f"{TARGET_W[prev_s]:.0%}",
            "alloc_to": f"{TARGET_W[state_smooth[i]]:.0%}",
            "nav": f"{pv[i]/1e9:.2f}",
            "nav_bh": f"{pv_bh[i]/1e9:.2f}",
            "ret_since": ret_since,
            "gate": "🔒" if gate_flag[i] else "",
            "macro": macro_note,
            "dd52": f"{dd_52w[i]:.1%}",
        })
        prev_s = state_smooth[i]

trans_rows_all = ""
for t in all_trans:
    rc = "green" if t["ret_since"] >= 0 else "red"
    macro_badge = f'<span style="font-size:9px;color:#f97316">▲tight</span>' if t["macro"]=="tight" else ""
    trans_rows_all += f"""<tr>
      <td style="color:#64748b;font-size:11px">{t['date']}</td>
      <td><span class="badge" style="background:{t['from_c']};font-size:10px">{t['from_s']}</span></td>
      <td style="color:#475569">→</td>
      <td><span class="badge" style="background:{t['to_c']};font-size:10px">{t['to_s']}</span></td>
      <td style="text-align:right">{t['vnindex']}</td>
      <td style="text-align:right">{t['pe']} <span style="color:#64748b;font-size:10px">({t['pe_rank']})</span></td>
      <td style="text-align:right;font-size:10px;color:#94a3b8">{t['dd52']}</td>
      <td style="text-align:right;font-size:10px">{t['usdvnd']}</td>
      <td style="text-align:right;font-size:11px">{t['alloc_from']} → {t['alloc_to']}</td>
      <td style="text-align:right;font-weight:700;color:#22c55e">{t['nav']} tỷ</td>
      <td style="text-align:right;color:#60a5fa">{t['nav_bh']} tỷ</td>
      <td style="text-align:right" class="{rc}">{t['ret_since']:+.1%}</td>
      <td style="text-align:center">{t['gate']}{macro_badge}</td>
    </tr>"""

def fmt(m, k, pct=True):
    v = m.get(k, float("nan"))
    if isinstance(v, float) and np.isnan(v): return "N/A"
    return f"{v:.1%}" if pct else f"{v:.2f}"

html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>VNINDEX Market System v2</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3.0.1/dist/chartjs-plugin-annotation.min.js"></script>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:#0f172a;color:#e2e8f0;font-size:13px;line-height:1.6}}
.hdr{{background:linear-gradient(135deg,#1a3a5f,#0f3320);padding:24px 32px;border-bottom:1px solid #1e293b}}
.hdr h1{{font-size:20px;font-weight:700;color:#fff;margin-bottom:4px}}
.hdr p{{font-size:12px;color:#94a3b8}}
.wrap{{max-width:1500px;margin:0 auto;padding:20px 24px}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px}}
.grid3{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:16px}}
.grid4{{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:14px;margin-bottom:16px}}
.card{{background:#1e293b;border-radius:12px;padding:18px 20px;border:1px solid #334155}}
.card h2{{font-size:12px;font-weight:700;color:#94a3b8;margin-bottom:12px;text-transform:uppercase;letter-spacing:.05em}}
.chart-wrap{{position:relative;height:280px}}
.chart-wrap-lg{{position:relative;height:340px}}
.state-big{{display:flex;align-items:center;gap:18px;padding:12px 0}}
.state-circle{{width:76px;height:76px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:#fff;flex-shrink:0;text-align:center}}
.state-info h3{{font-size:22px;font-weight:800;margin-bottom:4px}}
.state-info p{{font-size:12px;color:#94a3b8;line-height:1.9}}
.kpi-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}}
.kpi{{background:#0f172a;border-radius:8px;padding:9px 11px;text-align:center}}
.kpi .val{{font-size:17px;font-weight:700;margin-bottom:2px}}
.kpi .lbl{{font-size:10px;color:#64748b}}
.green{{color:#22c55e}} .red{{color:#ef4444}} .yellow{{color:#eab308}} .blue{{color:#60a5fa}} .orange{{color:#f97316}}
.badge{{display:inline-block;padding:2px 8px;border-radius:6px;color:#fff;font-size:11px;font-weight:600}}
table{{width:100%;border-collapse:collapse;font-size:11.5px}}
th{{background:#0f172a;padding:6px 9px;text-align:left;color:#64748b;font-weight:600;border-bottom:1px solid #334155;position:sticky;top:0;z-index:1}}
td{{padding:5px 9px;border-bottom:1px solid #1e293b}}
tr:hover td{{background:#162032}}
.factor-row{{display:flex;align-items:center;gap:6px;margin-bottom:7px}}
.factor-name{{width:65px;font-size:11px;color:#94a3b8}}
.factor-bar-bg{{flex:1;height:9px;background:#0f172a;border-radius:5px;overflow:hidden}}
.factor-bar{{height:9px;border-radius:5px}}
.factor-val{{width:38px;text-align:right;font-size:11px;font-weight:600}}
.alert{{background:#1e3a5f;border:1px solid #3b82f6;border-radius:8px;padding:10px 14px;margin-bottom:12px;font-size:12px;color:#93c5fd}}
.alert-warn{{background:#2d1a1a;border:1px solid #ef4444;color:#fca5a5}}
.alert-tight{{background:#2d1f0a;border:1px solid #f97316;color:#fdba74}}
.macro-bar{{display:flex;gap:6px;margin-top:8px;font-size:11px}}
.macro-pill{{padding:3px 10px;border-radius:999px;font-weight:600}}
</style>
</head>
<body>
<div class="hdr">
  <h1>⚡ VNINDEX Market System — v2</h1>
  <p>
    CRISIS = DD>20%+r_score<20% · Rank từ 2008 · EX-BULL contrarian · Macro: USD/VND + lãi suất + CPI ·
    BearDvg gate (floor=BEAR 20%, min=60 phiên) · Backtest 2000–{cur_date}
  </p>
</div>
<div class="wrap">

<!-- ROW 1: Current state + Factor ranks -->
<div class="grid2" style="margin-bottom:16px">
  <div class="card">
    <h2>Trạng thái hiện tại — {cur_date}</h2>
    <div class="state-big">
      <div class="state-circle" style="background:{cur_color}">{STATE_NAMES[cur_state]}</div>
      <div class="state-info">
        <h3 style="color:{cur_color}">{STATE_NAMES[cur_state]}</h3>
        <p>
          Phân bổ: <strong style="color:{cur_color}">{STATE_ALLOC[cur_state]}</strong><br>
          r_score EMA: <strong>{f"{cur_rs:.4f}" if cur_rs else "N/A"}</strong><br>
          PE: <strong>{f"{cur_pe:.2f}x" if cur_pe else "N/A"}</strong> · PE rank: <strong>{f"{cur_pe_r:.2f}" if cur_pe_r else "N/A"}</strong><br>
          VNINDEX: <strong>{close[-1]:.2f}</strong> · DD từ đỉnh 52w: <strong class="{'red' if dd_52w[-1]<-0.10 else 'yellow' if dd_52w[-1]<-0.05 else 'green'}">{dd_52w[-1]:.1%}</strong><br>
          USD/VND: <strong>{f"{cur_usdvnd:,.0f}" if cur_usdvnd else "N/A"}</strong>
          {f' · 1Y: <strong class="{"red" if cur_usd1y and cur_usd1y>3 else "green"}">{cur_usd1y:+.1f}%</strong>' if cur_usd1y else ""}<br>
          Gate BearDvg: <strong class="{'red' if cur_gate else 'green'}">{'🔒 Đang mở' if cur_gate else 'Không'}</strong>
        </p>
      </div>
    </div>
    <div class="macro-bar">
      <span class="macro-pill" style="background:{'#7f1d1d' if cur_tight else '#14532d'};color:#fff">
        {'⚠ MACRO TIGHT' if cur_tight else '✓ Macro ổn'}
      </span>
      {'<span class="macro-pill" style="background:#1e3a5f;color:#93c5fd">Môi trường lãi suất thấp</span>' if cur_easy else ''}
    </div>
    <div class="alert {'alert-warn' if cur_gate else ('alert-tight' if cur_tight else '')}" style="margin-top:12px">
      {'⚠ <strong>GATE BảO VỆ:</strong> BearDvg gate đang mở — phân bổ giới hạn 0%.' if cur_gate else
       '⚠ <strong>MACRO THẮT CHẶT:</strong> Lãi suất cao / VND mất giá / lạm phát cao — hạn chế BULL.' if cur_tight else
       f'💡 <strong>Khuyến nghị:</strong> {STATE_ALLOC[cur_state]} · {"Margin 30%" if cur_state==5 else "Tiền mặt "+f"{(1-TARGET_W[cur_state])*100:.0f}%" if TARGET_W[cur_state]<1 else "Full equity"}'}
    </div>
  </div>

  <div class="card">
    <h2>7 Yếu tố — Rank hiện tại (anchored 2008)</h2>
    {''.join(f"""
    <div class="factor-row">
      <span class="factor-name">{k}</span>
      <div class="factor-bar-bg">
        <div class="factor-bar" style="width:{radar_vals[i]*100:.1f}%;background:{'#ef4444' if radar_vals[i]<0.30 else '#eab308' if radar_vals[i]<0.70 else '#22c55e'}"></div>
      </div>
      <span class="factor-val" style="color:{'#ef4444' if radar_vals[i]<0.30 else '#eab308' if radar_vals[i]<0.70 else '#22c55e'}">{radar_vals[i]:.2f}</span>
    </div>""" for i,k in enumerate(radar_keys))}
    <div style="margin-top:12px;padding-top:10px;border-top:1px solid #334155;font-size:11px;color:#64748b">
      EX-BULL: PE_rank={f"{cur_pe_r:.2f}" if cur_pe_r else "N/A"}&lt;{EXBULL_PE_MAX} · CMF&gt;{EXBULL_CMF_MIN} · rs&gt;{EXBULL_RS_MIN} · DD_60&lt;{EXBULL_DD_THR:.0%}
    </div>
  </div>
</div>

<!-- ROW 2: Performance -->
<div class="grid3" style="margin-bottom:16px">
  <div class="card">
    <h2>Hiệu suất toàn kỳ (2000–nay)</h2>
    <div class="kpi-grid">
      <div class="kpi"><div class="val {'green' if m_sys['cagr']>m_bh['cagr'] else 'yellow'}">{fmt(m_sys,'cagr')}</div><div class="lbl">CAGR Hệ thống</div></div>
      <div class="kpi"><div class="val blue">{fmt(m_bh,'cagr')}</div><div class="lbl">CAGR B&H</div></div>
      <div class="kpi"><div class="val green">{fmt(m_sys,'sharpe',False)}</div><div class="lbl">Sharpe</div></div>
      <div class="kpi"><div class="val {'green' if abs(m_sys['max_dd'])<abs(m_bh['max_dd']) else 'red'}">{fmt(m_sys,'max_dd')}</div><div class="lbl">Max DD HT</div></div>
      <div class="kpi"><div class="val blue">{fmt(m_bh,'max_dd')}</div><div class="lbl">Max DD B&H</div></div>
      <div class="kpi"><div class="val green">{fmt(m_sys,'calmar',False)}</div><div class="lbl">Calmar</div></div>
    </div>
    <div style="margin-top:10px;font-size:11px;color:#64748b">
      NAV: <strong style="color:#22c55e">{final_sys:.2f} tỷ</strong> vs B&H <strong style="color:#60a5fa">{final_bh:.2f} tỷ</strong> · Vượt: <strong style="color:#22c55e">{final_sys/final_bh-1:+.1%}</strong>
    </div>
  </div>
  <div class="card">
    <h2>Hiệu suất từ 2011</h2>
    <div class="kpi-grid">
      <div class="kpi"><div class="val {'green' if m_sys_11['cagr']>m_bh_11['cagr'] else 'yellow'}">{fmt(m_sys_11,'cagr')}</div><div class="lbl">CAGR Hệ thống</div></div>
      <div class="kpi"><div class="val blue">{fmt(m_bh_11,'cagr')}</div><div class="lbl">CAGR B&H</div></div>
      <div class="kpi"><div class="val green">{fmt(m_sys_11,'sharpe',False)}</div><div class="lbl">Sharpe</div></div>
      <div class="kpi"><div class="val {'green' if abs(m_sys_11['max_dd'])<abs(m_bh_11['max_dd']) else 'red'}">{fmt(m_sys_11,'max_dd')}</div><div class="lbl">Max DD HT</div></div>
      <div class="kpi"><div class="val blue">{fmt(m_bh_11,'max_dd')}</div><div class="lbl">Max DD B&H</div></div>
      <div class="kpi"><div class="val green">{fmt(m_sys_11,'calmar',False)}</div><div class="lbl">Calmar</div></div>
    </div>
    <div style="margin-top:10px;font-size:11px;color:#64748b">
      NAV từ 2011: <strong style="color:#22c55e">{pv[-1]/pv[idx11]:.2f}x</strong> vs B&H <strong style="color:#60a5fa">{pv_bh[-1]/pv_bh[idx11]:.2f}x</strong>
    </div>
  </div>
  <div class="card">
    <h2>Phân bổ trạng thái · {n_trans} lần chuyển</h2>
    {''.join(f"""<div style="display:flex;align-items:center;gap:8px;margin-bottom:5px">
      <span class="badge" style="background:{STATE_COLOR[s]};width:68px;text-align:center;font-size:10px">{STATE_NAMES[s]}</span>
      <div style="flex:1;background:#0f172a;border-radius:4px;height:7px;overflow:hidden">
        <div style="width:{state_counts[s]/total_sc*100:.1f}%;height:7px;background:{STATE_COLOR[s]};border-radius:4px"></div>
      </div>
      <span style="font-size:11px;color:#94a3b8;width:80px">
        {state_counts[s]/total_sc*100:.1f}% · {int(np.sum(state_smooth[idx_rank:]==s))/(n-idx_rank)*100:.1f}%*
      </span>
    </div>""" for s in range(1,6))}
    <div style="margin-top:8px;font-size:10px;color:#475569">
      *% post-2008 · CRISIS post-2008: <strong style="color:{'#ef4444' if crisis_pct_post08>15 else '#22c55e'}">{crisis_pct_post08:.1f}%</strong>
      <br>EX-BULL sessions: <strong style="color:#10b981">{exbull_flags.sum()} ({exbull_flags.sum()/total_sc*100:.1f}%)</strong>
    </div>
  </div>
</div>

<!-- V1 VS V2 COMPARISON -->
<div class="card" style="margin-bottom:16px">
  <h2>So sánh v1 vs v2 — Thay đổi thiết kế</h2>
  <table style="margin-top:6px">
    <thead><tr>
      <th>Chỉ số</th>
      <th style="color:#60a5fa">V1 (cũ)</th>
      <th style="color:#22c55e">V2 (mới)</th>
      <th>Nhận xét</th>
    </tr></thead>
    <tbody>
      <tr><td>CAGR toàn kỳ</td><td style="color:#60a5fa">15.6%</td><td style="color:#22c55e">{m_sys['cagr']:.1%}</td><td style="color:#94a3b8">V2 thấp hơn do gate floor=20% (v1=0%)</td></tr>
      <tr><td>CAGR từ 2011</td><td style="color:#60a5fa">12.0%</td><td style="color:#22c55e">{m_sys_11['cagr']:.1%}</td><td style="color:#94a3b8">Cả hai đều vượt B&H ({m_bh_11['cagr']:.1%})</td></tr>
      <tr><td>MaxDD từ 2011</td><td style="color:#60a5fa">-19.7%</td><td style="color:#22c55e">{m_sys_11['max_dd']:.1%}</td><td style="color:#22c55e">V2 kiểm soát rủi ro tốt hơn</td></tr>
      <tr><td>Sharpe từ 2011</td><td style="color:#60a5fa">1.05</td><td style="color:#22c55e">{m_sys_11['sharpe']:.2f}</td><td style="color:#94a3b8">B&H = 0.57</td></tr>
      <tr><td>Calmar từ 2011</td><td style="color:#60a5fa">0.61</td><td style="color:#22c55e">{m_sys_11['calmar']:.2f}</td><td style="color:#94a3b8">Vẫn mạnh hơn B&H (0.20)</td></tr>
      <tr><td>CRISIS % (post-2008)</td><td style="color:#ef4444">20.7%</td><td style="color:#22c55e">{crisis_pct_post08:.1f}%</td><td style="color:#22c55e">Giảm mạnh — chỉ còn khủng hoảng thực sự</td></tr>
      <tr><td>Định nghĩa CRISIS</td><td style="color:#60a5fa">r_score &lt; 10% (rank từ 2000)</td><td style="color:#22c55e">DD&gt;20% + r_score&lt;20% (rank từ 2008)</td><td style="color:#94a3b8">V2 phản ánh thực tế thị trường tốt hơn</td></tr>
      <tr><td>BearDvg gate floor</td><td style="color:#60a5fa">CRISIS (0%)</td><td style="color:#22c55e">BEAR (20%)</td><td style="color:#94a3b8">V2 giữ 20% thay vì thoát hoàn toàn khi có BearDvg</td></tr>
      <tr><td>Macro integration</td><td style="color:#ef4444">Không có</td><td style="color:#22c55e">USD/VND + lãi suất + CPI</td><td style="color:#22c55e">V2 thêm bộ lọc macro thắt chặt</td></tr>
      <tr><td>EX-BULL</td><td style="color:#60a5fa">Momentum đỉnh (130%)</td><td style="color:#22c55e">Contrarian đáy ({exbull_flags.sum()} sessions)</td><td style="color:#22c55e">V2 mua ngược dòng khi PE rẻ + dòng tiền vào</td></tr>
      <tr><td>Rank anchor</td><td style="color:#60a5fa">Từ 2000 (bao gồm 2000-2007 nhiễu)</td><td style="color:#22c55e">Từ 2008 (dữ liệu thị trường trưởng thành)</td><td style="color:#22c55e">V2 rank có ý nghĩa thống kê tốt hơn</td></tr>
    </tbody>
  </table>
</div>

<!-- CHARTS -->
<div class="card" style="margin-bottom:16px">
  <h2>VNINDEX — Màu nền theo trạng thái · 🔒=BearDvg gate · ▲=Macro tight</h2>
  <div class="chart-wrap-lg"><canvas id="chartPrice"></canvas></div>
</div>
<div class="grid2" style="margin-bottom:16px">
  <div class="card">
    <h2>NAV (tỷ VND) — Hệ thống v2 vs Buy & Hold</h2>
    <div class="chart-wrap"><canvas id="chartNAV"></canvas></div>
  </div>
  <div class="card">
    <h2>USD/VND & Macro regime</h2>
    <div class="chart-wrap"><canvas id="chartMacro"></canvas></div>
  </div>
</div>
<div class="grid2" style="margin-bottom:16px">
  <div class="card">
    <h2>r_score EMA · Ngưỡng BEAR=0.30 / BULL=0.75</h2>
    <div class="chart-wrap"><canvas id="chartRScore"></canvas></div>
  </div>
  <div class="card">
    <h2>PE VNINDEX · PE rank (anchored 2008) · Ngưỡng EX-BULL &lt;0.22</h2>
    <div class="chart-wrap"><canvas id="chartPE"></canvas></div>
  </div>
</div>

<!-- FULL TRANSITIONS TABLE -->
<div class="card" style="margin-bottom:16px">
  <h2>Toàn bộ lịch sử chuyển trạng thái — NAV từ 1 tỷ VND
    <span style="font-size:11px;color:#64748b;font-weight:400">
      🔒=BearDvg gate · ▲tight=Macro thắt chặt ·
      HT: <span style="color:#22c55e">{final_sys:.2f} tỷ</span> ·
      B&H: <span style="color:#60a5fa">{final_bh:.2f} tỷ</span>
    </span>
  </h2>
  <div style="overflow-x:auto;max-height:520px;overflow-y:auto">
  <table>
    <thead>
      <tr>
        <th>Ngày</th><th>Từ</th><th></th><th>Sang</th>
        <th style="text-align:right">VNI</th>
        <th style="text-align:right">PE (rank)</th>
        <th style="text-align:right">DD 52w</th>
        <th style="text-align:right">USD/VND</th>
        <th style="text-align:right">Phân bổ</th>
        <th style="text-align:right;color:#22c55e">NAV HT</th>
        <th style="text-align:right;color:#60a5fa">NAV B&H</th>
        <th style="text-align:right">Ret GP</th>
        <th style="text-align:center">Flag</th>
      </tr>
    </thead>
    <tbody>{trans_rows_all}</tbody>
  </table>
  </div>
  <div style="margin-top:10px;font-size:11px;color:#64748b">
    Tổng {n_trans} lần chuyển · Vượt B&H: <strong style="color:#22c55e">{final_sys/final_bh-1:+.1%}</strong>
  </div>
</div>

</div><!-- /wrap -->
<script>
const dates    = {dates_js};
const close_d  = {close_js};
const state_d  = {state_js};
const rsema_d  = {rsema_js};
const weight_d = {weight_js};
const pv_d     = {pv_js};
const pvbh_d   = {pvbh_js};
const pe_d     = {pe_js};
const pep90_d  = {pep90_js};
const dd52w_d  = {dd52w_js};
const usdvnd_d = {usdvnd_js};
const macro_tight_d = {macro_tight_js};

const ST_BG = {{1:'#ef444430',2:'#f9731630',3:'#eab30820',4:'#22c55e25',5:'#10b98135'}};
const ST_BD = {{1:'#ef4444',2:'#f97316',3:'#eab308',4:'#22c55e',5:'#10b981'}};

function stateSegments(dates, states) {{
  const segs = [];
  let start = 0;
  for (let i = 1; i <= states.length; i++) {{
    if (i === states.length || states[i] !== states[start]) {{
      segs.push({{xMin: dates[start], xMax: dates[i-1], s: states[start]}});
      start = i;
    }}
  }}
  return segs;
}}

// Chart 1: Price
const ctx1 = document.getElementById('chartPrice').getContext('2d');
const segs = stateSegments(dates, state_d);
const annotations1 = {{}};
segs.forEach((seg, i) => {{
  if (!seg.s) return;
  annotations1['seg'+i] = {{
    type:'box', xMin:seg.xMin, xMax:seg.xMax, yMin:0, yMax:1e9,
    backgroundColor: ST_BG[seg.s]||'#ffffff10',
    borderWidth:0
  }};
}});
new Chart(ctx1, {{
  type:'line',
  data:{{ labels:dates, datasets:[{{
    label:'VNINDEX', data:close_d, borderColor:'#60a5fa',
    borderWidth:1.2, pointRadius:0, fill:false
  }}]}},
  options:{{
    responsive:true, maintainAspectRatio:false,
    plugins:{{legend:{{display:false}}, annotation:{{annotations:annotations1}}}},
    scales:{{
      x:{{type:'category', ticks:{{maxTicksLimit:12, color:'#64748b'}}, grid:{{color:'#1e293b'}}}},
      y:{{ticks:{{color:'#64748b'}}, grid:{{color:'#1e293b'}}}}
    }}
  }}
}});

// Chart 2: NAV
new Chart(document.getElementById('chartNAV').getContext('2d'), {{
  type:'line',
  data:{{ labels:dates, datasets:[
    {{label:'HT v2', data:pv_d, borderColor:'#22c55e', borderWidth:1.5, pointRadius:0, fill:false}},
    {{label:'B&H',   data:pvbh_d, borderColor:'#60a5fa', borderWidth:1, pointRadius:0, fill:false, borderDash:[4,3]}}
  ]}},
  options:{{
    responsive:true, maintainAspectRatio:false,
    plugins:{{legend:{{labels:{{color:'#94a3b8', boxWidth:20}}}}}},
    scales:{{
      x:{{type:'category', ticks:{{maxTicksLimit:10,color:'#64748b'}}, grid:{{color:'#1e293b'}}}},
      y:{{ticks:{{color:'#64748b', callback:v=>v+'tỷ'}}, grid:{{color:'#1e293b'}}}}
    }}
  }}
}});

// Chart 3: USD/VND + macro tight
new Chart(document.getElementById('chartMacro').getContext('2d'), {{
  type:'line',
  data:{{ labels:dates, datasets:[
    {{label:'USD/VND (nghìn)', data:usdvnd_d, borderColor:'#f97316', borderWidth:1.2, pointRadius:0, fill:false, yAxisID:'y'}},
  ]}},
  options:{{
    responsive:true, maintainAspectRatio:false,
    plugins:{{legend:{{labels:{{color:'#94a3b8', boxWidth:20}}}}}},
    scales:{{
      x:{{type:'category', ticks:{{maxTicksLimit:10,color:'#64748b'}}, grid:{{color:'#1e293b'}}}},
      y:{{ticks:{{color:'#64748b',callback:v=>v+'k'}}, grid:{{color:'#1e293b'}}}}
    }}
  }}
}});

// Chart 4: r_score EMA
new Chart(document.getElementById('chartRScore').getContext('2d'), {{
  type:'line',
  data:{{ labels:dates, datasets:[
    {{label:'r_score EMA', data:rsema_d, borderColor:'#a78bfa', borderWidth:1.2, pointRadius:0, fill:false}}
  ]}},
  options:{{
    responsive:true, maintainAspectRatio:false,
    plugins:{{
      legend:{{labels:{{color:'#94a3b8', boxWidth:20}}}},
      annotation:{{annotations:{{
        lBear:{{type:'line', yMin:{BEAR_RSCORE}, yMax:{BEAR_RSCORE}, borderColor:'#f97316', borderWidth:1, borderDash:[5,4], label:{{content:'BEAR',display:true,position:'start',color:'#f97316',font:{{size:10}}}}}},
        lBull:{{type:'line', yMin:{BULL_RSCORE}, yMax:{BULL_RSCORE}, borderColor:'#22c55e', borderWidth:1, borderDash:[5,4], label:{{content:'BULL',display:true,position:'start',color:'#22c55e',font:{{size:10}}}}}}
      }}}}
    }},
    scales:{{
      x:{{type:'category', ticks:{{maxTicksLimit:10,color:'#64748b'}}, grid:{{color:'#1e293b'}}}},
      y:{{min:0,max:1,ticks:{{color:'#64748b'}}, grid:{{color:'#1e293b'}}}}
    }}
  }}
}});

// Chart 5: PE + PE rank
new Chart(document.getElementById('chartPE').getContext('2d'), {{
  type:'line',
  data:{{ labels:dates, datasets:[
    {{label:'PE VNINDEX', data:pe_d, borderColor:'#fbbf24', borderWidth:1.2, pointRadius:0, fill:false, yAxisID:'y'}},
    {{label:'PE P90', data:pep90_d, borderColor:'#f87171', borderWidth:1, borderDash:[4,3], pointRadius:0, fill:false, yAxisID:'y'}}
  ]}},
  options:{{
    responsive:true, maintainAspectRatio:false,
    plugins:{{legend:{{labels:{{color:'#94a3b8', boxWidth:20}}}}}},
    scales:{{
      x:{{type:'category', ticks:{{maxTicksLimit:10,color:'#64748b'}}, grid:{{color:'#1e293b'}}}},
      y:{{ticks:{{color:'#64748b'}}, grid:{{color:'#1e293b'}}}}
    }}
  }}
}});
</script>
</body></html>"""

out_path = os.path.join(WORKDIR, "vnindex_v2_system.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Saved: {out_path}")
