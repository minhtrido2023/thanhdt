# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
"""
analyze_market_phase_pe.py
===========================
Phan tich pha thi truong VNIndex + histogram VNINDEX_PE
ket hop voi hieu qua cua cac buy filter trong filter.json
"""

import os, json
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

# ─────────────────────────────────────────────────────────────────────
# BUOC 1: Load VNINDEX.csv
# ─────────────────────────────────────────────────────────────────────
print("=" * 70)
print("BUOC 1: Load VNINDEX.csv")
print("=" * 70)

vni = pd.read_csv(os.path.join(WORKDIR, "VNINDEX.csv"), low_memory=False)
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)

# Chon cot can thiet
cols_need = [
    "time", "Close", "Volume",
    "D_RSI", "D_RSI_T1W", "D_CMF", "D_MACDdiff",
    "MA10", "MA20", "MA50", "MA200",
    "VNINDEX_PE", "VNINDEX_PE_MA2Y", "VNINDEX_PE_MA4Y", "VNINDEX_PE_MA5Y",
]
# Chi lay cot co trong file
cols_need = [c for c in cols_need if c in vni.columns]
vni = vni[cols_need].copy()

# Bo NaN o cac cot chinh
vni = vni.dropna(subset=["Close"])
vni["VNINDEX_PE"] = pd.to_numeric(vni["VNINDEX_PE"], errors="coerce")

print(f"Rows: {len(vni):,} | Date range: {vni['time'].min().date()} -> {vni['time'].max().date()}")
print(f"\nVNINDEX_PE stats:")
pe_valid = vni["VNINDEX_PE"].dropna()
print(f"  Count: {len(pe_valid):,}")
print(f"  Min: {pe_valid.min():.2f}  |  Max: {pe_valid.max():.2f}")
print(f"  Median: {pe_valid.median():.2f}  |  Mean: {pe_valid.mean():.2f}")
print(f"  P10: {pe_valid.quantile(0.10):.2f}  |  P25: {pe_valid.quantile(0.25):.2f}")
print(f"  P75: {pe_valid.quantile(0.75):.2f}  |  P90: {pe_valid.quantile(0.90):.2f}")

# ─────────────────────────────────────────────────────────────────────
# BUOC 2: Phan loai pha thi truong
# ─────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("BUOC 2: Phan loai pha thi truong (Market Phase)")
print("=" * 70)

def classify_phase(row):
    """
    7 phase dua tren Close/MA200, D_RSI, D_MACDdiff, D_CMF
    """
    close = row.get("Close", np.nan)
    ma200 = row.get("MA200", np.nan)
    rsi   = row.get("D_RSI", np.nan)
    macd  = row.get("D_MACDdiff", np.nan)
    cmf   = row.get("D_CMF", np.nan)

    if pd.isna(close) or pd.isna(ma200):
        return "UNKNOWN"

    above_ma200 = (close > ma200)

    # TICH LUY (Accumulation): gia duoi MA200 nhung RSI khong qua thap
    if not above_ma200 and (pd.isna(rsi) or 0.30 <= rsi <= 0.55):
        return "ACCUMULATION"

    # DAY MANH (Bear Bottom): gia duoi MA200, RSI rat thap
    if not above_ma200 and not pd.isna(rsi) and rsi < 0.30:
        return "BEAR_BOTTOM"

    # PHUC HOI (Recovery): gia vua vuot MA200, MACD con am hoac gan 0
    if above_ma200 and not pd.isna(macd) and macd < 0:
        return "RECOVERY"

    # TANG TRUONG (Bull Early): gia tren MA200, MACD duong, RSI trung binh
    if above_ma200 and not pd.isna(rsi) and rsi < 0.60:
        return "BULL_EARLY"

    # TANG MANH (Bull Strong): gia tren MA200, RSI cao, MACD duong
    if above_ma200 and not pd.isna(rsi) and 0.60 <= rsi <= 0.80:
        return "BULL_STRONG"

    # PHAN PHOI (Distribution): RSI qua cao, bao hieu dinh
    if above_ma200 and not pd.isna(rsi) and rsi > 0.80:
        return "DISTRIBUTION"

    return "NEUTRAL"

vni["phase"] = vni.apply(classify_phase, axis=1)

# Thong ke phase
phase_counts = vni["phase"].value_counts()
print("\nPhase distribution (total days):")
for phase, cnt in phase_counts.items():
    pct = cnt / len(vni) * 100
    print(f"  {phase:<16} {cnt:>5d} days ({pct:.1f}%)")

# ─────────────────────────────────────────────────────────────────────
# BUOC 3: PE histogram theo phase
# ─────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("BUOC 3: VNINDEX_PE theo tung Market Phase")
print("=" * 70)

vni_pe = vni.dropna(subset=["VNINDEX_PE"])

phase_order = ["BEAR_BOTTOM", "ACCUMULATION", "RECOVERY", "BULL_EARLY", "BULL_STRONG", "DISTRIBUTION", "NEUTRAL"]

print(f"\n{'Phase':<16} {'N':>6} {'PE_Min':>7} {'PE_P25':>7} {'PE_Med':>7} {'PE_P75':>7} {'PE_Max':>7} {'PE_Mean':>8}")
print("-" * 75)

phase_pe_stats = {}
for phase in phase_order:
    sub = vni_pe[vni_pe["phase"] == phase]["VNINDEX_PE"]
    if len(sub) < 5:
        continue
    stats = {
        "n": len(sub),
        "min": sub.min(),
        "p25": sub.quantile(0.25),
        "median": sub.median(),
        "p75": sub.quantile(0.75),
        "max": sub.max(),
        "mean": sub.mean(),
    }
    phase_pe_stats[phase] = stats
    print(f"  {phase:<16} {stats['n']:>6} {stats['min']:>7.1f} {stats['p25']:>7.1f} {stats['median']:>7.1f} {stats['p75']:>7.1f} {stats['max']:>7.1f} {stats['mean']:>8.1f}")

# ─────────────────────────────────────────────────────────────────────
# BUOC 4: PE theo nam - Lich su VNINDEX_PE
# ─────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("BUOC 4: Lich su VNINDEX_PE theo nam")
print("=" * 70)

vni_pe["year"] = vni_pe["time"].dt.year
yearly = vni_pe.groupby("year").agg(
    close_mean=("Close", "mean"),
    pe_median=("VNINDEX_PE", "median"),
    pe_min=("VNINDEX_PE", "min"),
    pe_max=("VNINDEX_PE", "max"),
    pe_mean=("VNINDEX_PE", "mean"),
    days=("VNINDEX_PE", "count")
).reset_index()
yearly = yearly[yearly["days"] >= 50]  # Chi lay nam co du du lieu

print(f"\n{'Year':>5} {'VNINDEX_avg':>11} {'PE_min':>7} {'PE_med':>7} {'PE_max':>7} {'Nhan dinh'}")
print("-" * 75)

key_events = {
    2000: "Khai truong HOSE", 2001: "Bong bong no", 2006: "Bull run",
    2007: "Dinh 1170", 2008: "Khung hoang TC the gioi", 2009: "Phuc hoi",
    2012: "Khung hoang 2012", 2017: "Bull run manh", 2018: "Dinh 1200",
    2020: "COVID day 660", 2021: "Dinh 1500", 2022: "Suy thoai 900",
    2024: "Phuc hoi", 2025: "ATH 1900", 2026: "Dieu chinh"
}
for _, row in yearly.iterrows():
    yr = int(row["year"])
    note = key_events.get(yr, "")
    print(f"  {yr:>4} {row['close_mean']:>11.0f} {row['pe_min']:>7.1f} {row['pe_median']:>7.1f} {row['pe_max']:>7.1f}   {note}")

# ─────────────────────────────────────────────────────────────────────
# BUOC 5: Load profile_hit.csv - Join voi VNINDEX context luc mua
# ─────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("BUOC 5: Join profile_hit.csv voi VNINDEX context")
print("=" * 70)

prof = pd.read_csv(os.path.join(WORKDIR, "profile_hit.csv"), index_col=0, low_memory=False)
prof["time"] = pd.to_datetime(prof["time"])
prof = prof[prof["Sell_profit"].notna()].copy()

print(f"profile_hit: {len(prof):,} deals | {prof['ticker'].nunique()} tickers")

# Lay VNINDEX context tai ngay mua
vni_context = vni[["time", "Close", "D_RSI", "D_CMF", "D_MACDdiff",
                     "MA50", "MA200", "VNINDEX_PE",
                     "VNINDEX_PE_MA2Y", "VNINDEX_PE_MA4Y", "VNINDEX_PE_MA5Y",
                     "phase"]].copy()
vni_context.columns = ["time", "VNI_Close", "VNI_RSI", "VNI_CMF", "VNI_MACD",
                         "VNI_MA50", "VNI_MA200", "VNI_PE",
                         "VNI_PE_MA2Y", "VNI_PE_MA4Y", "VNI_PE_MA5Y",
                         "VNI_phase"]

# Merge: dung merge_asof de map ngay mua -> ngay co data VNINDEX gan nhat
prof_sorted = prof.sort_values("time")
vni_sorted  = vni_context.sort_values("time")
prof_vni = pd.merge_asof(prof_sorted, vni_sorted, on="time", direction="backward", tolerance=pd.Timedelta("7d"))
match_rate = prof_vni["VNI_PE"].notna().mean()
print(f"VNINDEX context match rate: {match_rate:.1%}")

# PE valuation signal: so sanh PE hien tai vs MA
prof_vni["VNI_PE_vs_MA5Y"] = prof_vni["VNI_PE"] / prof_vni["VNI_PE_MA5Y"].replace(0, np.nan)
prof_vni["VNI_PE_vs_MA2Y"] = prof_vni["VNI_PE"] / prof_vni["VNI_PE_MA2Y"].replace(0, np.nan)

# ─────────────────────────────────────────────────────────────────────
# BUOC 6: Profit theo Market Phase luc mua
# ─────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("BUOC 6: Profit theo Market Phase tai thoi diem MUA")
print("=" * 70)

phase_profit = prof_vni.groupby("VNI_phase").agg(
    n_deals=("Sell_profit", "count"),
    median_profit=("Sell_profit", "median"),
    mean_profit=("Sell_profit", "mean"),
    winrate=("Sell_profit", lambda x: (x > 0).mean()),
    pct_profit_gt10=("Sell_profit", lambda x: (x > 10).mean()),
    pct_loss_lt_5=("Sell_profit", lambda x: (x < -5).mean()),
    pe_median=("VNI_PE", "median"),
).reset_index()

phase_profit = phase_profit.sort_values("median_profit", ascending=False)

print(f"\n{'Phase':<16} {'Deals':>7} {'PE_med':>7} {'Med_P%':>7} {'Win%':>7} {'P>10%':>7} {'L<-5%':>7}")
print("-" * 70)
for _, row in phase_profit.iterrows():
    print(f"  {row['VNI_phase']:<16} {row['n_deals']:>7.0f} {row['pe_median']:>7.1f} "
          f"{row['median_profit']:>7.1f} {row['winrate']:>7.1%} "
          f"{row['pct_profit_gt10']:>7.1%} {row['pct_loss_lt_5']:>7.1%}")

# ─────────────────────────────────────────────────────────────────────
# BUOC 7: Profit theo VNINDEX_PE buckets (histogram analysis)
# ─────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("BUOC 7: Profit theo VNINDEX_PE buckets")
print("=" * 70)

# Tao PE buckets dua tren phan vi lich su
pe_buckets = [0, 8, 10, 12, 14, 16, 18, 20, 25, 999]
pe_labels  = ["<8", "8-10", "10-12", "12-14", "14-16", "16-18", "18-20", "20-25", ">25"]

prof_pe = prof_vni.dropna(subset=["VNI_PE"]).copy()
prof_pe["PE_bucket"] = pd.cut(prof_pe["VNI_PE"], bins=pe_buckets, labels=pe_labels, right=False)

pe_profit = prof_pe.groupby("PE_bucket", observed=True).agg(
    n_deals=("Sell_profit", "count"),
    median_profit=("Sell_profit", "median"),
    mean_profit=("Sell_profit", "mean"),
    winrate=("Sell_profit", lambda x: (x > 0).mean()),
    pct_profit_gt10=("Sell_profit", lambda x: (x > 10).mean()),
    pct_loss_lt_5=("Sell_profit", lambda x: (x < -5).mean()),
    vni_avg=("VNI_Close", "mean"),
).reset_index()

print(f"\n{'PE_Range':>8} {'Deals':>7} {'VNI_avg':>8} {'Med_P%':>8} {'Win%':>7} {'P>10%':>7} {'L<-5%':>7}  Note")
print("-" * 85)
for _, row in pe_profit.iterrows():
    # Danh gia
    if row["median_profit"] > 15: note = "[[ TOT NHAT ]]"
    elif row["median_profit"] > 8: note = "[ Tot ]"
    elif row["median_profit"] > 3: note = "Trung binh"
    elif row["median_profit"] > 0: note = "Yeu"
    else: note = "!!! Nguy hiem !!!"
    print(f"  {str(row['PE_bucket']):>8} {row['n_deals']:>7.0f} {row['vni_avg']:>8.0f} "
          f"{row['median_profit']:>8.1f} {row['winrate']:>7.1%} "
          f"{row['pct_profit_gt10']:>7.1%} {row['pct_loss_lt_5']:>7.1%}  {note}")

# ─────────────────────────────────────────────────────────────────────
# BUOC 8: Profit theo PE buckets X per Filter
# ─────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("BUOC 8: Profit theo Filter x PE Range (ma tran hieu qua)")
print("=" * 70)

# Pivot: filter x PE bucket -> median profit
pivot = prof_pe.groupby(["filter", "PE_bucket"], observed=True)["Sell_profit"].median().unstack("PE_bucket")
print("\nMedian Profit (%) theo Filter x VNINDEX_PE bucket:")
print(pivot.to_string())

# ─────────────────────────────────────────────────────────────────────
# BUOC 9: VNINDEX_PE vs MA - Valuation Signal
# ─────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("BUOC 9: Valuation signal - PE hien tai vs MA lich su")
print("=" * 70)

# PE/MA5Y buckets: <0.8 = re lich su, 0.8-1.0 = binh thuong, >1.2 = dat
pe_ratio_buckets = [0, 0.7, 0.85, 1.0, 1.15, 1.30, 999]
pe_ratio_labels  = ["RE <0.7x", "Re 0.7-0.85x", "Binh 0.85-1x", "Cao 1-1.15x", "Dat 1.15-1.3x", "QDat >1.3x"]

prof_ratio = prof_vni.dropna(subset=["VNI_PE_vs_MA5Y"]).copy()
prof_ratio = prof_ratio[(prof_ratio["VNI_PE_vs_MA5Y"] > 0) & (prof_ratio["VNI_PE_vs_MA5Y"] < 5)]
prof_ratio["PE_vs_hist"] = pd.cut(prof_ratio["VNI_PE_vs_MA5Y"],
                                    bins=pe_ratio_buckets, labels=pe_ratio_labels, right=False)

ratio_profit = prof_ratio.groupby("PE_vs_hist", observed=True).agg(
    n_deals=("Sell_profit", "count"),
    median_profit=("Sell_profit", "median"),
    winrate=("Sell_profit", lambda x: (x > 0).mean()),
    pct_profit_gt10=("Sell_profit", lambda x: (x > 10).mean()),
    pct_loss_lt_5=("Sell_profit", lambda x: (x < -5).mean()),
    pe_mean=("VNI_PE", "mean"),
    vni_mean=("VNI_Close", "mean"),
).reset_index()

print(f"\n{'PE_vs_MA5Y':>14} {'Deals':>7} {'PE_cur':>7} {'VNI':>7} {'Med_P%':>8} {'Win%':>7} {'P>10%':>7} {'L<-5%':>7}")
print("-" * 80)
for _, row in ratio_profit.iterrows():
    print(f"  {str(row['PE_vs_hist']):>14} {row['n_deals']:>7.0f} {row['pe_mean']:>7.1f} {row['vni_mean']:>7.0f} "
          f"{row['median_profit']:>8.1f} {row['winrate']:>7.1%} "
          f"{row['pct_profit_gt10']:>7.1%} {row['pct_loss_lt_5']:>7.1%}")

# ─────────────────────────────────────────────────────────────────────
# BUOC 10: Phase x PE combined signal
# ─────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("BUOC 10: Phase + PE combined - Tim vung vang mua tot nhat")
print("=" * 70)

# Gom phase + PE bucket
prof_combined = prof_vni.dropna(subset=["VNI_PE", "VNI_phase"]).copy()
prof_combined["PE_bucket"] = pd.cut(prof_combined["VNI_PE"],
                                     bins=[0, 10, 14, 18, 999],
                                     labels=["RE (<10)", "OK (10-14)", "Cao (14-18)", "Dat (>18)"],
                                     right=False)

combined = prof_combined.groupby(["VNI_phase", "PE_bucket"], observed=True).agg(
    n=("Sell_profit", "count"),
    med_profit=("Sell_profit", "median"),
    winrate=("Sell_profit", lambda x: (x > 0).mean()),
).reset_index()

combined = combined[combined["n"] >= 30]  # Chi hien thi khi co du deals
combined = combined.sort_values("med_profit", ascending=False)

print(f"\n{'Phase':<16} {'PE_Range':<12} {'Deals':>6} {'Med_P%':>8} {'Win%':>7}   Danh gia")
print("-" * 70)
for _, row in combined.iterrows():
    if row["med_profit"] > 15: rating = ">>> VANG <<<"
    elif row["med_profit"] > 8: rating = ">> Tot <<"
    elif row["med_profit"] > 3: rating = "> Kha <"
    elif row["med_profit"] >= 0: rating = "Trung binh"
    else: rating = "!!! Tranh !!!"
    print(f"  {row['VNI_phase']:<16} {str(row['PE_bucket']):<12} {row['n']:>6} {row['med_profit']:>8.1f} "
          f"{row['winrate']:>7.1%}   {rating}")

# ─────────────────────────────────────────────────────────────────────
# BUOC 11: Filter VNINDEX tu filter.json - Co filter nao dung VNI?
# ─────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("BUOC 11: VNINDEX indicators trong filter.json")
print("=" * 70)

with open(os.path.join(WORKDIR, "filter.json"), encoding="utf-8") as f:
    filters = json.load(f)

vni_keywords = ["VNINDEX", "VNI_", "vnindex"]
print("\nCac filter co dieu kien lien quan den VNINDEX:")
for k, v in filters.items():
    if any(kw in str(v) for kw in vni_keywords):
        print(f"  {k}: {v}")

# Khong co filter truc tiep dung VNINDEX? -> Phan tich VNI_RSI luc mua
print("\nThong ke VNI_RSI luc mua (tu profile_hit.csv voi VNI context):")
vni_rsi_buckets = [0, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 1.0]
vni_rsi_labels  = ["OvrSold<0.3", "0.3-0.4", "0.4-0.5", "0.5-0.6", "0.6-0.7", "0.7-0.8", "OvrBought>0.8"]

prof_rsi = prof_vni.dropna(subset=["VNI_RSI"]).copy()
prof_rsi["VNI_RSI_bucket"] = pd.cut(prof_rsi["VNI_RSI"],
                                      bins=vni_rsi_buckets, labels=vni_rsi_labels, right=False)

rsi_profit = prof_rsi.groupby("VNI_RSI_bucket", observed=True).agg(
    n=("Sell_profit", "count"),
    med_profit=("Sell_profit", "median"),
    winrate=("Sell_profit", lambda x: (x > 0).mean()),
    pe_mean=("VNI_PE", "mean"),
).reset_index()

print(f"\n{'VNI_RSI':>14} {'Deals':>7} {'PE_avg':>7} {'Med_P%':>8} {'Win%':>7}")
print("-" * 55)
for _, row in rsi_profit.iterrows():
    flag = " *** TOT ***" if row["med_profit"] > 12 else (" !! Kem !!" if row["med_profit"] < 3 else "")
    print(f"  {str(row['VNI_RSI_bucket']):>14} {row['n']:>7.0f} {row['pe_mean']:>7.1f} "
          f"{row['med_profit']:>8.1f} {row['winrate']:>7.1%}{flag}")

# ─────────────────────────────────────────────────────────────────────
# BUOC 12: De xuat bo loc VNINDEX_PE vao filter gate
# ─────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("BUOC 12: De xuat bo loc VNINDEX_PE / VNI_RSI vao gate")
print("=" * 70)

# Test: Bo sung gate VNINDEX_PE < threshold
print("\nTest: neu them gate VNINDEX_PE < X vao truoc moi buy filter:")
print(f"\n{'PE_gate':>8} {'Deals':>8} {'Med_P%':>8} {'Win%':>8} {'Deals_pct':>10}   Delta_vs_all")
print("-" * 70)

base_med = prof_pe["Sell_profit"].median()
base_win = (prof_pe["Sell_profit"] > 0).mean()
base_n   = len(prof_pe)

for pe_cut in [10, 12, 14, 15, 16, 17, 18, 20]:
    sub = prof_pe[prof_pe["VNI_PE"] < pe_cut]
    if len(sub) < 100:
        continue
    med = sub["Sell_profit"].median()
    win = (sub["Sell_profit"] > 0).mean()
    delta_med = med - base_med
    delta_win = win - base_win
    flag = " <<< RECOMMEND" if (delta_med > 3 and len(sub) > 0.5 * base_n) else ""
    print(f"  PE<{pe_cut:>3} {len(sub):>8,} {med:>8.1f} {win:>8.1%} {len(sub)/base_n:>10.1%}   "
          f"{delta_med:>+6.1f}pp / {delta_win:>+6.1%}{flag}")

# Test gate VNI_RSI
print(f"\nTest: neu them gate VNI_RSI < X:")
print(f"\n{'RSI_gate':>8} {'Deals':>8} {'Med_P%':>8} {'Win%':>8} {'Deals_pct':>10}   Delta_vs_all")
print("-" * 70)

prof_rsi2 = prof_vni.dropna(subset=["VNI_RSI"]).copy()
base_med2 = prof_rsi2["Sell_profit"].median()
base_win2 = (prof_rsi2["Sell_profit"] > 0).mean()
base_n2   = len(prof_rsi2)

for rsi_cut in [0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70]:
    sub = prof_rsi2[prof_rsi2["VNI_RSI"] < rsi_cut]
    if len(sub) < 100:
        continue
    med = sub["Sell_profit"].median()
    win = (sub["Sell_profit"] > 0).mean()
    delta_med = med - base_med2
    flag = " <<< RECOMMEND" if (delta_med > 3 and len(sub) > 0.3 * base_n2) else ""
    print(f"  RSI<{rsi_cut:.2f} {len(sub):>8,} {med:>8.1f} {win:>8.1%} {len(sub)/base_n2:>10.1%}   "
          f"{delta_med:>+6.1f}pp{flag}")

# ─────────────────────────────────────────────────────────────────────
# BUOC 13: Tinh trang hien tai (2026-04)
# ─────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("BUOC 13: Tinh trang hien tai (2026-04)")
print("=" * 70)

latest = vni.dropna(subset=["VNINDEX_PE"]).iloc[-1]
print(f"\n  Date     : {latest['time'].date()}")
print(f"  VNI Close: {latest['Close']:.0f}")
print(f"  VNINDEX_PE       : {latest['VNINDEX_PE']:.2f}x")
if pd.notna(latest.get("VNINDEX_PE_MA2Y")): print(f"  PE vs MA2Y       : {latest['VNINDEX_PE']/latest['VNINDEX_PE_MA2Y']:.2f}x")
if pd.notna(latest.get("VNINDEX_PE_MA5Y")): print(f"  PE vs MA5Y       : {latest['VNINDEX_PE']/latest['VNINDEX_PE_MA5Y']:.2f}x")
if pd.notna(latest.get("D_RSI")):  print(f"  VNI RSI          : {latest['D_RSI']:.3f}")
if pd.notna(latest.get("D_CMF")):  print(f"  VNI CMF          : {latest['D_CMF']:.3f}")
if pd.notna(latest.get("D_MACDdiff")): print(f"  VNI MACDdiff     : {latest['D_MACDdiff']:.2f}")
print(f"  Market Phase : {latest['phase']}")

# So sanh PE hien tai voi phan vi lich su
pe_cur = latest["VNINDEX_PE"]
pe_hist = vni_pe["VNINDEX_PE"]
pe_pctile = (pe_hist <= pe_cur).mean()
print(f"\n  PE hien tai {pe_cur:.2f}x nam o percentile {pe_pctile:.1%} lich su")
print(f"  (0% = re nhat lich su, 100% = dat nhat lich su)")

# Danh gia thi truong hien tai theo dieu kien filter
print(f"\n  Ket luan theo du lieu:")
if pe_cur < 12:
    print(f"  PE {pe_cur:.1f}x = VUNG RE LICH SU -> Dieu kien tot de mua theo tat ca filter")
elif pe_cur < 16:
    print(f"  PE {pe_cur:.1f}x = VUNG BINH THUONG -> Co the mua nhung co chon loc filter")
elif pe_cur < 20:
    print(f"  PE {pe_cur:.1f}x = VUNG CAO -> Chi nen mua filter chat luong cao (SuperGrowth, SurpriseEarning)")
else:
    print(f"  PE {pe_cur:.1f}x = VUNG NGUY HIEM -> Han che mua, uu tien cash/phong thu")

rsi_cur = latest.get("D_RSI", np.nan)
if not pd.isna(rsi_cur):
    if rsi_cur < 0.35:
        print(f"  RSI {rsi_cur:.2f} = OVERSOLD -> Tin hieu tich luy manh")
    elif rsi_cur < 0.50:
        print(f"  RSI {rsi_cur:.2f} = Yeu -> Thi truong dang phan hoi, co the mua dan")
    elif rsi_cur < 0.65:
        print(f"  RSI {rsi_cur:.2f} = Trung binh -> Trung tinh")
    else:
        print(f"  RSI {rsi_cur:.2f} = Cao -> Thi truong da tang du, than trong")

print("\nDone!")
