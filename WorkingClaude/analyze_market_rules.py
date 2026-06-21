# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
"""
analyze_market_rules.py
========================
Kiem tra logic hien tai cua market_rule.md + market_overheat.md
va de xuat he thong cai tien.
"""
import os
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

# ══════════════════════════════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════════════════════════════
vni = pd.read_csv(os.path.join(WORKDIR, "VNINDEX.csv"), low_memory=False)
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
vni = vni[vni["time"] >= "2016-01-01"].copy().reset_index(drop=True)

num_cols = ["VNINDEX_PE","VNINDEX_PE_MA5Y","VNINDEX_PE_MA2Y","VNINDEX_PE_MA4Y",
            "Close","D_RSI","D_CMF","D_MACDdiff","MA200","MA50",
            "D_RSI_Min1W","D_RSI_Min3M","D_RSI_MinT3","D_RSI_Max1W","D_RSI_Max3M",
            "D_RSI_T1W","D_RSI_Min1W_Close","D_RSI_Min3M_Close",
            "D_RSI_Max1W_Close","D_RSI_Max3M_Close","D_RSI_Max1W_MACD","D_RSI_Max3M_MACD",
            "C_L1M","C_L1W"]
for c in num_cols:
    if c in vni.columns:
        vni[c] = pd.to_numeric(vni[c], errors="coerce")

# PE percentiles (global)
pe_vals = vni["VNINDEX_PE"].dropna().values
PE = {f"P{p}": float(np.percentile(pe_vals, p))
      for p in [5,10,15,20,25,30,40,50,60,65,70,75,80,85,90,95]}

# P3M trailing (3-month momentum)
vni["P3M"] = (vni["Close"] / vni["Close"].shift(63) - 1) * 100
p3m_vals = vni["P3M"].dropna().values
P3M = {f"P{p}": float(np.percentile(p3m_vals, p))
       for p in [5,10,15,20,80,85,90,95]}

# Forward returns (for validation)
for d in [20, 40, 63, 120]:
    vni[f"fwd_{d}"] = (vni["Close"].shift(-d) / vni["Close"] - 1) * 100

# ══════════════════════════════════════════════════════════════════════
# PHAN 1: CRIT-REVIEW LOGIC HIEN TAI
# ══════════════════════════════════════════════════════════════════════
print("=" * 70)
print("PHAN 1: KIEM TRA LOGIC HIEN TAI (market_rule.md)")
print("=" * 70)

print(f"""
[market_rule.md] Nguong PE hien dung:
  Market SELL khi PE >= P60 = {PE['P60']:.2f}x
  Market BUY  khi PE <= P60 = {PE['P60']:.2f}x
  Block 30 ngay  : PE in [P60,P65) = [{PE['P60']:.1f}, {PE['P65']:.1f})
  Block 60 ngay  : PE in [P65,P80) = [{PE['P65']:.1f}, {PE['P80']:.1f})
  Block 90 ngay  : PE in [P80,P90) = [{PE['P80']:.1f}, {PE['P90']:.1f})
  Block 1 nam    : PE in [P90,P95) = [{PE['P90']:.1f}, {PE['P95']:.1f})
  Block 1.5 nam  : PE >= P95       = {PE['P95']:.1f}x+
  Extreme rule   : PE >= P90 -> buy chi khi PE <= P20 = {PE['P20']:.1f}x
""")

# Test 1: Neu chi dung PE >= P60 lam sell signal, forward return nhu the nao?
vni_pe = vni.dropna(subset=["VNINDEX_PE","fwd_63"])
sell_zone_p60 = vni_pe[vni_pe["VNINDEX_PE"] >= PE["P60"]]
buy_zone_p60  = vni_pe[vni_pe["VNINDEX_PE"] <  PE["P60"]]

print("Ket qua neu dung P60 lam nguong PE:")
print(f"  Vung BUY (PE < {PE['P60']:.1f}x): {len(buy_zone_p60)} ngay | "
      f"Fwd 3M median = {buy_zone_p60['fwd_63'].median():+.1f}% | "
      f"Win3M = {(buy_zone_p60['fwd_63'] > 0).mean():.1%}")
print(f"  Vung SELL (PE >= {PE['P60']:.1f}x): {len(sell_zone_p60)} ngay | "
      f"Fwd 3M median = {sell_zone_p60['fwd_63'].median():+.1f}% | "
      f"Win3M = {(sell_zone_p60['fwd_63'] > 0).mean():.1%}")

# Test 2: So sanh cac nguong PE khac nhau
print("\nKhao sat nguong PE -> Forward return 3M:")
print(f"{'PE threshold':>14} {'N_buy_days':>10} {'Fwd3M_buy':>10} {'Win3M_buy':>10} {'N_sell_days':>12} {'Fwd3M_sell':>11} {'Win3M_sell':>11}")
print("-" * 90)
for pct_key in ["P40","P50","P60","P65","P70","P75","P80"]:
    thr = PE[pct_key]
    buy  = vni_pe[vni_pe["VNINDEX_PE"] <  thr]
    sell = vni_pe[vni_pe["VNINDEX_PE"] >= thr]
    if len(buy) < 10 or len(sell) < 10:
        continue
    print(f"  PE < {thr:.1f}x ({pct_key}) {len(buy):>10} {buy['fwd_63'].median():>+10.1f}% "
          f"{(buy['fwd_63']>0).mean():>10.1%} {len(sell):>12} {sell['fwd_63'].median():>+11.1f}% "
          f"{(sell['fwd_63']>0).mean():>11.1%}")

# Van de 1: PE >= P60 (16.3x) trong ACCUMULATION phase van mua duoc tot
print("\n[VAN DE 1]: PE >= P60 trong giai doan tich luy (duoi MA200)?")
vni_acc = vni_pe[(vni_pe["VNINDEX_PE"] >= PE["P60"]) & (vni_pe["Close"] < vni_pe["MA200"])]
vni_acc_bull = vni_pe[(vni_pe["VNINDEX_PE"] >= PE["P60"]) & (vni_pe["Close"] >= vni_pe["MA200"])]
print(f"  PE >= P60 + DUOI MA200: {len(vni_acc)} ngay | Fwd3M = {vni_acc['fwd_63'].median():+.1f}% -- NEN MUA!")
print(f"  PE >= P60 + TREN MA200: {len(vni_acc_bull)} ngay | Fwd3M = {vni_acc_bull['fwd_63'].median():+.1f}% -- DUNG BLOCK")

# Van de 2: Extreme rule P90 -> P20 qua chat
print(f"\n[VAN DE 2]: Rule PE>=P90 ({PE['P90']:.1f}x) -> chi buy lai PE<={PE['P20']:.1f}x")
extreme_sell = vni_pe[vni_pe["VNINDEX_PE"] >= PE["P90"]]
print(f"  So ngay PE >= P90: {len(extreme_sell)} ngay")
# Tim khi nao PE giam xuong P20 sau khi qua P90
if len(extreme_sell) > 0:
    first_extreme = extreme_sell.iloc[0]["time"]
    after_extreme = vni_pe[vni_pe["time"] > first_extreme]
    p20_reentry = after_extreme[after_extreme["VNINDEX_PE"] <= PE["P20"]]
    if len(p20_reentry) > 0:
        wait_days = (p20_reentry.iloc[0]["time"] - first_extreme).days
        print(f"  Phai cho {wait_days} ngay de PE xuong P20={PE['P20']:.1f}x !")
    else:
        print(f"  CHUA BAO GIO PE xuong P20 sau khi len P90 trong window nay!")

# ══════════════════════════════════════════════════════════════════════
# PHAN 2: CRIT-REVIEW MARKET_OVERHEAT
# ══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("PHAN 2: KIEM TRA LOGIC HIEN TAI (market_overheat.md)")
print("=" * 70)

print(f"""
[market_overheat.md] Nguong P3M (3-thang trailing):
  Overbuy  P95 threshold = P3M > {P3M['P95']:.1f}% (3M return)
  Overbuy  P90 threshold = P3M > {P3M['P90']:.1f}%
  Overbuy  P80 threshold = P3M > {P3M['P80']:.1f}%
  Oversell P10 threshold = P3M < {P3M['P10']:.1f}%
  Oversell P20 threshold = P3M < {P3M['P20']:.1f}%
""")

# Forward return sau overbuy/oversell
print("Forward return sau khi P3M extreme:")
print(f"{'P3M Zone':>18} {'N_days':>7} {'Fwd1M':>8} {'Fwd2M':>8} {'Fwd3M':>8} {'Win3M':>8}")
print("-" * 65)
vni_p3m = vni.dropna(subset=["P3M","fwd_63"])
for label, mask in [
    (f"Overbuy P95 (>{P3M['P95']:.0f}%)", vni_p3m["P3M"] > P3M["P95"]),
    (f"Overbuy P90 (>{P3M['P90']:.0f}%)", vni_p3m["P3M"] > P3M["P90"]),
    (f"Overbuy P80 (>{P3M['P80']:.0f}%)", vni_p3m["P3M"] > P3M["P80"]),
    ("Normal range",                        (vni_p3m["P3M"] >= P3M["P20"]) & (vni_p3m["P3M"] <= P3M["P80"])),
    (f"Oversell P20 (<{P3M['P20']:.0f}%)", vni_p3m["P3M"] < P3M["P20"]),
    (f"Oversell P10 (<{P3M['P10']:.0f}%)", vni_p3m["P3M"] < P3M["P10"]),
]:
    sub = vni_p3m[mask].dropna(subset=["fwd_20","fwd_40","fwd_63"])
    if len(sub) < 5:
        continue
    print(f"  {label:>18} {len(sub):>7} {sub['fwd_20'].median():>+8.1f}% {sub['fwd_40'].median():>+8.1f}% "
          f"{sub['fwd_63'].median():>+8.1f}% {(sub['fwd_63']>0).mean():>8.1%}")

# Van de 3: P3M overbuy KHONG BAO GIO can sell
print("\n[VAN DE 3]: P3M Overbuy co that su dan den suy giam?")
ob = vni_p3m[vni_p3m["P3M"] > P3M["P90"]]
print(f"  Sau P3M overbuy: Fwd3M = {ob['fwd_63'].median():+.1f}%, Win = {(ob['fwd_63']>0).mean():.1%}")
print(f"  => Overbuy KHONG co nghia la giam ngay - thuong van tang them {ob['fwd_63'].median():+.0f}% trong 3 thang!")

# Van de 4: P3M oversell la tin hieu mua
os_ = vni_p3m[vni_p3m["P3M"] < P3M["P10"]]
print(f"\n[VAN DE 4]: P3M Oversell la co hoi mua?")
print(f"  Sau P3M oversell: Fwd3M = {os_['fwd_63'].median():+.1f}%, Win = {(os_['fwd_63']>0).mean():.1%}")
print(f"  => Oversell la tin hieu MUA manh (bounce)")

# ══════════════════════════════════════════════════════════════════════
# PHAN 3: HE THONG CAI TIEN - UNIFIED MARKET STATE MACHINE
# ══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("PHAN 3: HE THONG CAI TIEN - UNIFIED MARKET STATE MACHINE")
print("=" * 70)

print("""
Cac diem yeu can sua:
[L1] market_rule.md dung nhan nguong PE >= P60 = 16.3x lam sell -> qua som
     (2016-2017: thi truong o PE 16-17x nhung van tang tot)
[L2] Khong phan biet phase: PE >= P60 nhung duoi MA200 van nen mua
[L3] Rule P90->P20 qua chat - co the doi 2+ nam khong mua
[L4] Moi thang 1 tin hieu - bo lo nhung dich chuyen nhanh (COVID)
[L5] Khong co BullDvg/BearDvg VNI signal
[L6] Khong xet lai suat SBV/Fed

[O1] market_overheat.md dung P3M overbuy lam canh bao sell -> sai logic
     (P3M cao = thi truong dang manh, thuc te FWD return van tot)
[O2] P3M oversell la tin hieu MUA, nhung code dang dung lam 'canh bao xau'
[O3] Phuc tap khong can thiet (future return so sanh percentile)
""")

# ══════════════════════════════════════════════════════════════════════
# PHAN 4: UNIFIED MARKET STATE MACHINE - CAI TIEN
# ══════════════════════════════════════════════════════════════════════
print("=" * 70)
print("PHAN 4: UNIFIED MARKET STATE (5 trang thai)")
print("=" * 70)

def compute_market_state(row, PE, P3M):
    """
    5 trang thai thi truong dua tren nhieu chi so ket hop:
    BULL    : thi truong tang, an toan cao
    NEUTRAL : thi truong sideway, giao dich co chon loc
    CAUTION : thi truong co rui ro, giam ty trong
    BEAR    : thi truong giam, giu nhieu tien
    PANIC   : thi truong hoang loan/suy sup - CO HOI MUA
    """
    pe = row.get("VNINDEX_PE", np.nan)
    rsi = row.get("D_RSI", np.nan)
    macd = row.get("D_MACDdiff", np.nan)
    cmf = row.get("D_CMF", np.nan)
    close = row.get("Close", np.nan)
    ma200 = row.get("MA200", np.nan)
    p3m = row.get("P3M", np.nan)

    if pd.isna(pe) or pd.isna(close) or pd.isna(ma200):
        return "UNKNOWN"

    above_ma200 = close > ma200

    # --- PANIC: uu tien cao nhat (mua dot) ---
    # P3M giam manh + RSI thap + duoi MA200
    if (not pd.isna(p3m) and p3m < P3M["P10"] and
        not pd.isna(rsi) and rsi < 0.35 and
        not above_ma200):
        return "PANIC"

    # --- BEAR: xu huong giam ro rang ---
    # Duoi MA200, RSI yeu, MACD am, P3M xau
    if not above_ma200:
        if (not pd.isna(rsi) and rsi < 0.45 and
            (pd.isna(macd) or macd < 0)):
            return "BEAR"

    # --- CAUTION: dinh dinh cao, rui ro ---
    # PE > P75 (16.8x) VA RSI cao VA P3M da tang nhieu
    if (pe >= PE["P75"] and
        not pd.isna(rsi) and rsi > 0.65 and
        (not pd.isna(p3m) and p3m > P3M["P80"])):
        return "CAUTION"

    # PE > P85 (17.5x) - bat buoc canh bao
    if pe >= PE["P85"]:
        if not pd.isna(rsi) and rsi > 0.55:
            return "CAUTION"

    # --- BULL: dieu kien tot de mua ---
    # Tren MA200, PE < P65 (16.5x), RSI khong qua cao
    if (above_ma200 and
        pe < PE["P65"] and
        not pd.isna(rsi) and rsi < 0.70 and
        (not pd.isna(macd) and macd >= 0)):
        return "BULL"

    # Duoi MA200 nhung PE re va co tin hieu phuc hoi
    if (not above_ma200 and
        pe < PE["P40"] and  # < 14.6x
        not pd.isna(rsi) and rsi > 0.35 and
        not pd.isna(macd) and macd > 0):
        return "BULL"

    # --- NEUTRAL: mac dinh ---
    return "NEUTRAL"

vni["market_state"] = vni.apply(lambda r: compute_market_state(r, PE, P3M), axis=1)

# Thong ke
print("\nPhan bo Market State (2016-2026):")
state_dist = vni.groupby("market_state").size()
for s, n in state_dist.items():
    pct = n / len(vni) * 100
    print(f"  {s:<10}: {n:>5} ngay ({pct:.1f}%)")

# Forward return theo state
print("\nForward return theo Market State (VALIDATION):")
vni_s = vni.dropna(subset=["market_state","fwd_63"])
print(f"\n{'State':>10} {'N':>5} {'PE_med':>7} {'Fwd1M':>8} {'Fwd2M':>8} {'Fwd3M':>8} {'Win3M':>8}")
print("-" * 65)
state_order = ["PANIC","BEAR","NEUTRAL","BULL","CAUTION","UNKNOWN"]
for state in state_order:
    sub = vni_s[vni_s["market_state"] == state].dropna(subset=["fwd_20","fwd_40","fwd_63","VNINDEX_PE"])
    if len(sub) < 5:
        continue
    print(f"  {state:>10} {len(sub):>5} {sub['VNINDEX_PE'].median():>7.1f} "
          f"{sub['fwd_20'].median():>+8.1f}% {sub['fwd_40'].median():>+8.1f}% "
          f"{sub['fwd_63'].median():>+8.1f}% {(sub['fwd_63']>0).mean():>8.1%}")

# ══════════════════════════════════════════════════════════════════════
# PHAN 5: BLOCK WINDOW RULES CAI TIEN
# ══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("PHAN 5: BLOCK WINDOW RULES CAI TIEN (thay the market_rule.md)")
print("=" * 70)

print("""
RULE CAI TIEN - SELL/BLOCK condition:
--------------------------------------
[R1] PE-based trigger (thay P60->P75):
     - PE >= P75 (16.8x) AND RSI > 0.65 AND P3M > P80 (10.9%)
       -> Market CAUTION: giam ty trong, KHONG mo vi the moi

[R2] Phase-aware (sua [L2]):
     - Chi block khi TREN MA200
     - Duoi MA200 thi PE cao cung khong block (dang hoi phuc)

[R3] Block window tang dan (rut ngan so voi hien tai):
     - PE in [P75, P85): block 30 ngay  (thay vi 60-90)
     - PE in [P85, P90): block 60 ngay  (thay vi 90)
     - PE in [P90, P95): block 120 ngay (thay vi 365)
     - PE >= P95        : block 180 ngay (thay vi 545)
     + BullDvgVNI signal co the mo block som hon

[R4] Reopen condition (sua [L3]):
     Hien tai: PE >= P90 -> chi mua lai PE <= P20 (QUA CHAT)
     Cai tien: PE >= P90 -> mua lai khi MOT TRONG CAC DIEU KIEN:
       (a) PE < P40 (14.6x) - thay vi P20 (13.3x)
       (b) BullDvgVNI signal fire
       (c) RSI < 0.35 (oversold)
       (d) Block window het han

[R5] BullDvgVNI override:
     Neu co BullDvgVNI1 hoac BullDvgVNI12 fire:
     -> Mo lai mua NGAY BAT KE block window

BUY SIGNAL condition (thay the):
---------------------------------
[B1] Market state != CAUTION AND != BEAR -> cho phep mua
[B2] Market state == BEAR -> chi cho cac filter chat luong cao:
     (SuperGrowth, SurpriseEarning, BullDvg)
[B3] Market state == PANIC -> FULL MUA, co the vay them

P3M OVERHEAT revision (sua market_overheat.md):
-------------------------------------------------
[O_FIX1] P3M overbuy (>P90) KHONG phai sell signal:
         -> la warning "thi truong da tang manh, nen than trong"
         -> KHONG block mua
         -> chi la tham so phu trong market state

[O_FIX2] P3M oversell (<P10) la BUY SIGNAL:
         -> ket hop voi RSI < 0.35 va duoi MA200
         -> = PANIC state -> full mua

[O_FIX3] Overbuy + PE >= P85 + RSI > 0.70 -> CAUTION (moi dung block)
""")

# ══════════════════════════════════════════════════════════════════════
# PHAN 6: BACKTEST RULES CU VS MOI
# ══════════════════════════════════════════════════════════════════════
print("=" * 70)
print("PHAN 6: SO SANH LOGIC CU vs MOI - Forward Return")
print("=" * 70)

vni_bt = vni.dropna(subset=["VNINDEX_PE","fwd_63","P3M","D_RSI","MA200"]).copy()

# OLD RULE: buy khi PE < P60
vni_bt["old_buy"]  = vni_bt["VNINDEX_PE"] < PE["P60"]
vni_bt["old_sell"] = vni_bt["VNINDEX_PE"] >= PE["P60"]

# NEW RULE: buy khi state in BULL/NEUTRAL/PANIC, sell khi CAUTION/BEAR
vni_bt["new_buy"]  = vni_bt["market_state"].isin(["BULL","NEUTRAL","PANIC"])
vni_bt["new_sell"] = vni_bt["market_state"].isin(["CAUTION","BEAR"])

old_buy_ret  = vni_bt[vni_bt["old_buy"]]["fwd_63"].median()
old_sell_ret = vni_bt[vni_bt["old_sell"]]["fwd_63"].median()
new_buy_ret  = vni_bt[vni_bt["new_buy"]]["fwd_63"].median()
new_sell_ret = vni_bt[vni_bt["new_sell"]]["fwd_63"].median()

print(f"\n[LOGIC CU - P60 threshold]:")
print(f"  Buy zone (PE < {PE['P60']:.1f}x):  {vni_bt['old_buy'].sum():>5} ngay | Fwd3M = {old_buy_ret:>+6.1f}% | Win = {(vni_bt[vni_bt['old_buy']]['fwd_63']>0).mean():.1%}")
print(f"  Sell zone (PE >= {PE['P60']:.1f}x): {vni_bt['old_sell'].sum():>5} ngay | Fwd3M = {old_sell_ret:>+6.1f}%")
print(f"  Chenh lech BUY vs SELL: {old_buy_ret - old_sell_ret:>+6.1f}pp")

print(f"\n[LOGIC MOI - Unified State Machine]:")
print(f"  Buy zone (BULL/NEUTRAL/PANIC): {vni_bt['new_buy'].sum():>5} ngay | Fwd3M = {new_buy_ret:>+6.1f}% | Win = {(vni_bt[vni_bt['new_buy']]['fwd_63']>0).mean():.1%}")
print(f"  Sell zone (CAUTION/BEAR):      {vni_bt['new_sell'].sum():>5} ngay | Fwd3M = {new_sell_ret:>+6.1f}%")
print(f"  Chenh lech BUY vs SELL: {new_buy_ret - new_sell_ret:>+6.1f}pp")

# Cac ngay ma old rule sai nhung new rule dung
false_block = vni_bt[(vni_bt["old_sell"] == True) & (vni_bt["new_buy"] == True)]
false_pass  = vni_bt[(vni_bt["old_buy"]  == True) & (vni_bt["new_sell"] == True)]
print(f"\n[CU block, MOI cho mua]: {len(false_block)} ngay | Fwd3M cu bi bo lo = {false_block['fwd_63'].median():>+.1f}%")
print(f"[CU cho mua, MOI block]: {len(false_pass)} ngay | Fwd3M cu da mua sai = {false_pass['fwd_63'].median():>+.1f}%")

# ══════════════════════════════════════════════════════════════════════
# PHAN 7: LICH SU CAC TRANG THAI THI TRUONG
# ══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("PHAN 7: LICH SU TRANG THAI THI TRUONG (gia tri hang thang)")
print("=" * 70)

vni["month"] = vni["time"].dt.to_period("M")
monthly = vni.groupby("month").agg(
    close=("Close","last"),
    pe=("VNINDEX_PE","last"),
    rsi=("D_RSI","last"),
    state=("market_state","last"),
    p3m=("P3M","last"),
).reset_index()
monthly = monthly[monthly["pe"].notna()]

print(f"\n{'Month':>8} {'VNI':>6} {'PE':>6} {'RSI':>6} {'P3M%':>6} {'State':>10}   Note")
print("-" * 75)
key_months = [
    "2018-01","2018-06","2018-12",
    "2020-01","2020-03","2020-06","2020-12",
    "2021-06","2021-11","2022-01",
    "2022-06","2022-10","2022-12",
    "2023-06","2023-12",
    "2024-06","2024-12",
    "2025-01","2025-06","2025-12",
    "2026-01","2026-04",
]
notes = {
    "2018-01":"Dinh 1200", "2018-06":"Giam manh", "2018-12":"Day sau ATH",
    "2020-03":"Day COVID", "2020-06":"Phuc hoi", "2020-12":"Tang manh",
    "2021-06":"Bull 2021", "2021-11":"Dinh 1500", "2022-01":"Bat dau suy",
    "2022-06":"Giam nhanh", "2022-10":"Day 900", "2022-12":"Bat dau hoi",
    "2023-06":"Phuc hoi tot", "2023-12":"Cuoi 2023",
    "2024-06":"Giua 2024", "2024-12":"Cuoi 2024",
    "2025-01":"Tang manh 2025", "2025-06":"ATH 1900?", "2025-12":"Cuoi 2025",
    "2026-01":"Dinh 1900", "2026-04":"Hien tai",
}
for m_str in key_months:
    try:
        m = pd.Period(m_str, "M")
        row = monthly[monthly["month"] == m]
        if len(row) == 0:
            continue
        r = row.iloc[0]
        note = notes.get(m_str, "")
        p3m_str = f"{r['p3m']:>+.1f}%" if not pd.isna(r['p3m']) else "  N/A"
        print(f"  {str(r['month']):>8} {r['close']:>6.0f} {r['pe']:>6.1f} {r['rsi']:>6.3f} {p3m_str:>6} {r['state']:>10}   {note}")
    except:
        pass

# ══════════════════════════════════════════════════════════════════════
# PHAN 8: TRANG THAI HIEN TAI + TONG KET DE XUAT
# ══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("PHAN 8: TRANG THAI HIEN TAI (2026-04-17)")
print("=" * 70)

latest = vni.dropna(subset=["VNINDEX_PE"]).iloc[-1]
cur_state = latest["market_state"]

print(f"""
  VNI Close   : {latest['Close']:.0f}
  VNINDEX_PE  : {latest['VNINDEX_PE']:.2f}x  (P{(pe_vals < latest['VNINDEX_PE']).mean()*100:.0f} lich su)
  D_RSI       : {latest['D_RSI']:.3f}
  D_CMF       : {latest['D_CMF']:.3f}
  D_MACDdiff  : {latest['D_MACDdiff']:.1f}
  MA200       : {latest['MA200']:.0f} | Close > MA200: {latest['Close'] > latest['MA200']}
  P3M trailing: {latest['P3M']:.1f}%  (P{(p3m_vals < latest['P3M']).mean()*100:.0f} lich su)
  Market State: {cur_state}
""")

# ══════════════════════════════════════════════════════════════════════
# PHAN 9: TONG KET - BANG SO SANH RULES CU vs MOI
# ══════════════════════════════════════════════════════════════════════
print("=" * 70)
print("PHAN 9: TONG KET SO SANH RULES")
print("=" * 70)
print(f"""
                    HIEN TAI (cu)              DE XUAT (moi)
---------------------------------------------------------------------------
Sell trigger   PE >= P60 = {PE['P60']:.1f}x           PE >= P75 = {PE['P75']:.1f}x
               (+ BearDvgVNI)                 + RSI > 0.65 + tren MA200
                                              (+ BearDvgVNI)

Buy trigger    PE <= P60 = {PE['P60']:.1f}x           State != CAUTION && != BEAR
               (sau cooldown)                  BullDvgVNI mo block som

Block window   P60-P65: 30 ngay               P75-P85: 30 ngay
               P65-P80: 60 ngay               P85-P90: 60 ngay
               P80-P90: 90 ngay               P90-P95: 120 ngay
               P90-P95: 365 ngay              >= P95:  180 ngay
               >= P95:  545 ngay

Reopen        PE >= P90 -> PE <= P20          PE >= P90 -> PE <= P40
              (doi 13.3x) [rat kho]           HOAC BullDvgVNI fire
                                              HOAC RSI < 0.35
                                              HOAC block het han

P3M overbuy   Xac dinh trang thai xau        WARNING chu - KHONG block
P3M oversell  Canh bao xau                   CO HOI MUA + PANIC state

Phase check   Khong phan biet                Phase-aware:
              (PE >= P60 la block)             duoi MA200 + PE cao = OK
                                              tren MA200 + PE cao = BLOCK

BullDvgVNI    Khong dung                     Override block window
SBV/Fed       Khong dung                     Dung trong Market Score tong hop

Ket qua:
  Old buy zone Fwd3M: {old_buy_ret:>+.1f}% (chenh {old_buy_ret - old_sell_ret:>+.1f}pp vs sell)
  New buy zone Fwd3M: {new_buy_ret:>+.1f}% (chenh {new_buy_ret - new_sell_ret:>+.1f}pp vs caution/bear)
  Ngay bi block sai boi rule cu: {len(false_block)} ngay (Fwd3M = {false_block['fwd_63'].median():>+.1f}%)
""")
print("Done!")
