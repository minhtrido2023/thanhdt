#!/usr/bin/env python3
"""
market_phase_analysis.py
=========================
Phan tich giai doan thi truong VNINDEX 2000-2026
- Ket hop VNINDEX technical data (BQ 2014-2026)
- Lich su lai suat ngan hang / SBV (2000-2026)
- Macro context: lam phat, tang truong GDP
- Phan loai giai doan, du bao hien tai
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch

DARK_BG="#0f1117"; PANEL_BG="#1a1d27"; GRID_CLR="#2a2d3a"; TEXT_CLR="#e0e0e0"
BLUE="#4fa3e0"; GREEN="#4ecb71"; RED="#e05c5c"; YELLOW="#f0c060"
ORANGE="#f0904a"; PURPLE="#b57bee"; TEAL="#4ecbbb"; CYAN="#4ecbee"
PINK="#e07bb5"; LIME="#b5e04a"
plt.rcParams.update({
    "figure.facecolor":DARK_BG,"axes.facecolor":PANEL_BG,"axes.edgecolor":GRID_CLR,
    "axes.labelcolor":TEXT_CLR,"xtick.color":TEXT_CLR,"ytick.color":TEXT_CLR,
    "text.color":TEXT_CLR,"grid.color":GRID_CLR,"grid.linestyle":"--","grid.alpha":0.3,
    "font.family":"DejaVu Sans",
})

# ── LOAD DATA: kết hợp VNINDEX.csv (pre-2014, ngày thực tế) + BQ 2014-2026 ────
import os
WORKDIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else r"/home/trido/thanhdt/WorkingClaude"

# Pre-2014: VNINDEX.csv chứa ngày giao dịch thực (bao gồm 3 ngày/tuần pre-2007)
vni_raw = pd.read_csv(
    os.path.join(WORKDIR, "data/VNINDEX.csv"),
    usecols=["time", "Close", "VNINDEX_RSI", "VNINDEX_CMF", "VNINDEX_MACDdiff"],
    low_memory=False
)
vni_raw["time"] = pd.to_datetime(vni_raw["time"])
df_pre14 = vni_raw[vni_raw["time"] < "2014-01-01"].copy()
df_pre14 = df_pre14.rename(columns={"Close": "VNINDEX"})
for col in ["VNINDEX_RSI", "VNINDEX_CMF", "VNINDEX_MACDdiff"]:
    df_pre14[col] = pd.to_numeric(df_pre14[col], errors="coerce")
print(f"Pre-2014 (VNINDEX.csv): {len(df_pre14)} sessions  ({df_pre14['time'].min().date()} → {df_pre14['time'].max().date()})")

# 2014-2026: BQ data
df_bq = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_data.csv"))
df_bq["time"] = pd.to_datetime(df_bq["time"])
print(f"Post-2014 (BQ data)  : {len(df_bq)} sessions  ({df_bq['time'].min().date()} → {df_bq['time'].max().date()})")

# Kết hợp → toàn bộ lịch sử với ngày giao dịch thực tế
df = pd.concat([df_pre14, df_bq], ignore_index=True)
df = df.sort_values("time").reset_index(drop=True)

# Compute moving averages trên toàn bộ dataset (liên tục từ 2000, không hardcode)
df["MA50"]  = df["VNINDEX"].rolling(50).mean()
df["MA200"] = df["VNINDEX"].rolling(200).mean()
df["MA20"]  = df["VNINDEX"].rolling(20).mean()

# RSI trend: 20-session rolling avg of RSI
df["RSI_MA20"] = df["VNINDEX_RSI"].rolling(20).mean()
df["RSI_MA60"] = df["VNINDEX_RSI"].rolling(60).mean()

# CMF trend
df["CMF_MA20"] = df["VNINDEX_CMF"].rolling(20).mean()

print(f"\nCombined VNINDEX data: {len(df)} sessions  ({df['time'].iloc[0].date()} → {df['time'].iloc[-1].date()})")
print(f"VNI latest: {df['VNINDEX'].iloc[-1]:.2f} | RSI: {df['VNINDEX_RSI'].iloc[-1]:.4f} | CMF: {df['VNINDEX_CMF'].iloc[-1]:.4f}")

# ── HISTORICAL PHASES: tính tự động từ data thực thay vì hardcode ────────────
# Tóm tắt các giai đoạn chính từ data thực (computed below sau classify_phase)

# ── INTEREST RATE HISTORY (Vietnam SBV + commercial deposit 12M) ──────────────
# (year, SBV_base_rate, commercial_deposit_12m, inflation, notes)
rate_history = [
    (2000, 7.5,  6.0,  -0.6, "On dinh sau khung hoang Dong Nam A"),
    (2001, 7.5,  5.5,  -0.4, "Nen kinh te on dinh"),
    (2002, 7.5,  6.0,   4.0, "Tang truong on dinh"),
    (2003, 7.5,  6.5,   3.0, "Phuc hoi"),
    (2004, 7.5,  7.0,   9.5, "Lam phat tang, SBV tang lai suat"),
    (2005, 7.8,  7.5,   8.4, "On dinh"),
    (2006, 8.25, 8.0,   7.5, "SBV tang nhe"),
    (2007, 8.25, 8.5,   8.3, "Dot bien tang truong, thi truong bung phat"),
    (2008, 14.0, 19.0,  23.0, "KHUNG HOANG: Lam phat dinh, SBV tang gap doi"),
    (2009, 7.0,  9.0,   6.9, "Cat manh: SBV giam 7pp trong 6 thang"),
    (2010, 9.0,  12.0,  9.2, "Lam phat quay lai, tang lai suat"),
    (2011, 14.0, 14.0,  18.6, "DINH LAI SUAT: SBV cap khong cho tang qua 14%"),
    (2012, 9.0,  9.0,   9.2, "Cat lai suat: -5pp"),
    (2013, 7.0,  7.0,   6.0, "Tiep tuc cat, on dinh"),
    (2014, 6.5,  6.0,   4.1, "La mat on dinh"),
    (2015, 6.5,  5.5,   0.6, "Lam phat thap nhat lich su, on dinh"),
    (2016, 6.5,  6.0,   4.7, "Phuc hoi nhe"),
    (2017, 6.25, 6.5,   3.5, "Tang truong manh, lai suat on"),
    (2018, 6.25, 7.0,   3.5, "Ket thuc bull run, on dinh"),
    (2019, 6.0,  6.5,   2.8, "Duy tri, trade war US-China"),
    (2020, 4.0,  4.5,   3.2, "COVID: SBV cat 3 lan, lai suat ve lich su"),
    (2021, 4.0,  4.0,   1.8, "DINH THAP: Cat kich thich toi da"),
    (2022, 6.0,  8.5,   3.2, "Tang gap: SBV tang khan cap 200bp thang 10"),
    (2023, 4.5,  5.0,   3.3, "Cat 4 lan: khoi phuc, kinh te phuc hoi"),
    (2024, 4.5,  4.8,   4.2, "On dinh, cho doi tang truong"),
    (2025, 4.5,  5.0,   3.5, "On dinh, thue quan Trump bat on"),
    (2026, 4.5,  5.0,   3.0, "Du bao: on dinh, rui ro toan cau"),
]
rate_df = pd.DataFrame(rate_history, columns=["year","sbv_rate","deposit_rate","inflation","note"])

# ── PHASE CLASSIFICATION (BQ data 2014-2026) ─────────────────────────────────
# Define 7 phases using RSI + CMF + MACDdiff + MA relationship
def classify_phase(row):
    rsi = row["VNINDEX_RSI"]
    cmf = row["VNINDEX_CMF"]
    macd = row["VNINDEX_MACDdiff"]
    rsi_ma20 = row["RSI_MA20"]
    close = row["VNINDEX"]
    ma200 = row["MA200"]

    if pd.isna(ma200):
        return "unknown"

    price_vs_200 = close / ma200
    rsi_decl = rsi < rsi_ma20 if not pd.isna(rsi_ma20) else False

    # Phase logic
    if rsi < 0.32 and cmf < -0.05:
        return "BEAR_STRONG"      # Giam manh
    elif rsi < 0.40 and macd < -2:
        return "BEAR_STRONG"
    elif rsi < 0.45 and macd < 0 and cmf < 0 and price_vs_200 < 0.98:
        return "BEAR_EARLY"       # Giam som
    elif rsi < 0.42 and macd < 0:
        return "ACCUMULATION"     # Tich luy / Day
    elif rsi >= 0.42 and rsi < 0.55 and macd > 0 and cmf > -0.05:
        return "BULL_EARLY"       # Tang som
    elif rsi >= 0.55 and rsi < 0.72 and macd > 0 and price_vs_200 > 1.05:
        return "BULL_STRONG"      # Tang manh
    elif rsi >= 0.70 and (macd < 0 or rsi_decl):
        return "DISTRIBUTION"     # Phan phoi
    elif rsi >= 0.62 and macd < 0 and cmf < 0:
        return "BEAR_EARLY"
    elif rsi >= 0.42 and rsi < 0.62 and macd < 0 and cmf < -0.05:
        return "RECOVERY"         # Phuc hoi ky thuat
    elif rsi >= 0.62 and macd > 0 and price_vs_200 > 1.0:
        return "BULL_STRONG"
    else:
        return "BULL_EARLY"

df["phase"] = df.apply(classify_phase, axis=1)

# Phase colors
phase_colors = {
    "ACCUMULATION":  TEAL,
    "BULL_EARLY":    GREEN,
    "BULL_STRONG":   LIME,
    "DISTRIBUTION":  YELLOW,
    "BEAR_EARLY":    ORANGE,
    "BEAR_STRONG":   RED,
    "RECOVERY":      BLUE,
    "unknown":       GRID_CLR,
}
phase_labels = {
    "ACCUMULATION": "Tich luy / Day",
    "BULL_EARLY":   "Tang truong som",
    "BULL_STRONG":  "Tang truong manh",
    "DISTRIBUTION": "Phan phoi / Dinh",
    "BEAR_EARLY":   "Giam som",
    "BEAR_STRONG":  "Giam manh",
    "RECOVERY":     "Phuc hoi ky thuat",
}

# Print phase distribution
print(f"\n=== PHASE DISTRIBUTION ({df['time'].iloc[0].year}-{df['time'].iloc[-1].year}) ===")
phase_counts = df["phase"].value_counts()
for ph, cnt in phase_counts.items():
    pct = cnt/len(df)*100
    label = phase_labels.get(ph, ph)
    print(f"  {label:25s}: {cnt:4d} ngay ({pct:.1f}%)")

# Print recent 90 days phase
recent_90 = df.tail(90)
print(f"\n=== RECENT 90 DAYS ===")
print(f"Phase distribution last 90 trading days:")
print(recent_90["phase"].value_counts().to_string())

# Key stats by phase
print("\n=== STATS BY PHASE ===")
phase_stats = df.groupby("phase").agg(
    n=("VNINDEX","count"),
    vni_avg=("VNINDEX","mean"),
    rsi_avg=("VNINDEX_RSI","mean"),
    cmf_avg=("VNINDEX_CMF","mean"),
    macd_avg=("VNINDEX_MACDdiff","mean"),
).round(3)
print(phase_stats.to_string())

# ── HISTORICAL CONTEXT: tóm tắt tự động từ data thực ─────────────────────────
print("\n=== LICH SU GIAI DOAN THI TRUONG (từ data thực tế) ===")
# Phát hiện các đợt trend chính dựa trên phase transitions
df["phase_group"] = (df["phase"] != df["phase"].shift()).cumsum()
phase_summary = df.groupby("phase_group").agg(
    phase=("phase", "first"),
    start=("time", "first"),
    end=("time", "last"),
    vni_start=("VNINDEX", "first"),
    vni_end=("VNINDEX", "last"),
    n_sessions=("VNINDEX", "count"),
).reset_index(drop=True)
phase_summary["return_pct"] = (phase_summary["vni_end"] / phase_summary["vni_start"] - 1) * 100
phase_summary["label"] = phase_summary["phase"].map(phase_labels)
# Chỉ hiển thị các giai đoạn >= 20 phiên để lọc bỏ noise ngắn hạn
major_phases = phase_summary[phase_summary["n_sessions"] >= 20].copy()
print(f"\n{'Bắt đầu':<12} {'Kết thúc':<12} {'Giai đoạn':<25} {'VNI start':>9} {'VNI end':>9} {'Return':>8} {'Phiên':>6}")
print("-"*90)
for _, row in major_phases.iterrows():
    print(f"  {str(row['start'].date()):<10} {str(row['end'].date()):<10}  "
          f"{str(row['label']):<25} {row['vni_start']:>9.0f} {row['vni_end']:>9.0f} "
          f"{row['return_pct']:>+7.1f}% {row['n_sessions']:>5d}")

# ── CURRENT MARKET ASSESSMENT ─────────────────────────────────────────────────
print(f"\n{'='*80}")
print("DANH GIA THI TRUONG HIEN TAI (April 2026)")
print(f"{'='*80}")

latest = df.iloc[-1]
prev30 = df.iloc[-30]
prev90 = df.iloc[-90]

print(f"\nVNINDEX hien tai (2026-03-30): {latest['VNINDEX']:.2f}")
print(f"  vs 30 ngay truoc ({prev30['time'].date()}): {prev30['VNINDEX']:.2f} ({(latest['VNINDEX']/prev30['VNINDEX']-1)*100:+.1f}%)")
print(f"  vs 90 ngay truoc ({prev90['time'].date()}): {prev90['VNINDEX']:.2f} ({(latest['VNINDEX']/prev90['VNINDEX']-1)*100:+.1f}%)")
print(f"  MA50:  {latest['MA50']:.2f}  (VNI/MA50 = {latest['VNINDEX']/latest['MA50']:.3f})")
print(f"  MA200: {latest['MA200']:.2f}  (VNI/MA200 = {latest['VNINDEX']/latest['MA200']:.3f})")
print(f"\nRSI indicators:")
print(f"  Current RSI:    {latest['VNINDEX_RSI']:.4f}  (zone: {'Oversold' if latest['VNINDEX_RSI']<0.35 else 'Low' if latest['VNINDEX_RSI']<0.45 else 'Neutral' if latest['VNINDEX_RSI']<0.55 else 'High' if latest['VNINDEX_RSI']<0.70 else 'Overbought'})")
print(f"  RSI 30d ago:    {prev30['VNINDEX_RSI']:.4f}")
print(f"  RSI 90d ago:    {prev90['VNINDEX_RSI']:.4f}")
print(f"  RSI_Max3M:      {latest['VNINDEX_RSI_Max3M']:.4f}  (3-month RSI peak = {latest['VNINDEX_RSI_Max3M']:.4f})")
print(f"  RSI_Max1W:      {latest['VNINDEX_RSI_Max1W']:.4f}")
print(f"\nMomentum:")
print(f"  CMF:            {latest['VNINDEX_CMF']:.4f}  (money flow {'vao' if latest['VNINDEX_CMF']>0 else 'ra'})")
print(f"  CMF 30d avg:    {df['VNINDEX_CMF'].tail(30).mean():.4f}")
print(f"  MACDdiff:       {latest['VNINDEX_MACDdiff']:.4f}  ({'tang' if latest['VNINDEX_MACDdiff']>0 else 'giam'}, {'improving' if latest['VNINDEX_MACDdiff'] > df['VNINDEX_MACDdiff'].iloc[-15] else 'deteriorating'})")
print(f"  MACDdiff 15d ago: {df['VNINDEX_MACDdiff'].iloc[-15]:.4f}")

# Historical RSI context
print(f"\nLich su RSI zones:")
for zone_name, (lo, hi) in [
    ("RSI < 0.35 (Oversold)",   (0, 0.35)),
    ("RSI 0.35-0.45 (Low)",     (0.35, 0.45)),
    ("RSI 0.45-0.55 (Neutral)", (0.45, 0.55)),
    ("RSI 0.55-0.70 (High)",    (0.55, 0.70)),
    ("RSI > 0.70 (Overbought)", (0.70, 1.0)),
]:
    mask = (df["VNINDEX_RSI"] >= lo) & (df["VNINDEX_RSI"] < hi)
    n = mask.sum()
    avg_vni = df[mask]["VNINDEX"].mean()
    print(f"  {zone_name:<30}: {n:4d} ngay ({n/len(df):.1%})  avg VNI={avg_vni:.0f}")

# Compare current to all similar RSI moments
print(f"\nCac ngay tuong tu (RSI 0.38-0.45, CMF < 0):")
similar = df[(df["VNINDEX_RSI"]>=0.38) & (df["VNINDEX_RSI"]<=0.45) & (df["VNINDEX_CMF"]<0)]
if len(similar) > 0:
    print(f"  n={len(similar)} ngay  avg VNI={similar['VNINDEX'].mean():.0f}")
    print(f"  Giai doan pho bien:")
    yr_counts = similar.groupby(similar["time"].dt.year)["VNINDEX"].count()
    print("  ", yr_counts.to_dict())
    # 3-month forward return for similar days (excluding last 90 days to avoid lookahead)
    similar_old = similar[similar["time"] < df["time"].iloc[-90]]
    if len(similar_old) > 20:
        fwd_returns = []
        for idx in similar_old.index:
            fwd_idx = min(idx + 60, len(df)-1)
            ret = df["VNINDEX"].iloc[fwd_idx] / df["VNINDEX"].iloc[idx] - 1
            fwd_returns.append(ret)
        fwd = np.array(fwd_returns)
        print(f"\n  Forward 3-month returns from similar RSI/CMF moments:")
        print(f"    Avg: {fwd.mean():+.1%}  Median: {np.median(fwd):+.1%}")
        print(f"    % positive: {(fwd>0).mean():.1%}")
        print(f"    % > +10%: {(fwd>0.10).mean():.1%}")
        print(f"    % < -10%: {(fwd<-0.10).mean():.1%}")

# ── VERDICT ────────────────────────────────────────────────────────────────────
print(f"\n{'='*80}")
print("KET LUAN: THI TRUONG HIEN TAI DANG O GIAI DOAN NAO?")
print(f"{'='*80}")
print("""
GIAI DOAN HIEN TAI: DIEU CHINH / TICH LUY SAU DINH (Correction/Accumulation)
Confidence: TRUNG BINH-CAO

=== BUNG CO (Evidence FOR this phase) ===

1. GIA TRI TUYET DOI: VNI ~1,662 - DINH LICH SU MOI (ATH)
   - 2021 peak: ~1,500  ->  2026 peak: ~1,800+ (uoc luong)
   - Hien tai da dieu chinh ~7-10% tu dinh 2026
   - ATH = thi truong da qua giai doan tang manh, vao giai doan phan phoi/dieu chinh

2. RSI PULLBACK MANH: 0.76 (3 thang truoc) -> 0.42 (hien tai)
   - Giam 34pp trong 3 thang = su suy yeu momentum dang ke
   - RSI 0.42 = vung thap (Low zone), GAN oversold nhung chua den
   - Tuong tu giai doan: Apr-2018 (sau dinh 1,200), Nov-2021 (sau dinh 1,500)

3. CMF AM: -0.19 (money flow dang roi khoi thi truong)
   - Nhà dau tu lon dang phan phoi, ban ra
   - Chua co dau hieu dong tien quay lai

4. MACD PHUC HOI: tu -13 -> -0.68 (30 ngay truoc)
   - MACD dang "leo" ve phia 0 = ap luc giam dang yeu di
   - Chua cat len duong 0 -> chua xac nhan tang tro lai

5. MACRO: LAI SUAT ON DINH ~4.5-5%
   - Khong co rui ro tang lai suat dot ngot (SBV)
   - Nhung rui ro toan cau: Thue quan Trump, Fed chua cat
   - Moi truong lai suat "trung tinh" - khong cuc ki ho tro tang

=== RUI RO / HANG CO (Evidence AGAINST recovery) ===

1. TRUMP TARIFF RISK (rui ro lon nhat hien tai)
   - VN la nuoc xuat khau lon sang My, thue quan 46% se anh huong GDP
   - Thi truong dang "price in" rui ro nay -> giai thich RSI giam
   - Neu thue quan duoc dam phan ha xuong: catalyst tang manh
   - Neu thue quan duy tri/tang: them ap luc ban ra

2. GLOBAL UNCERTAINTY: USD strength, recession fears
   - EM (Emerging Markets) bi anh huong khi USD manh
   - VN la EM -> dong tien nuoc ngoai co the rut

3. VNI o ATH = valuation cao
   - Khong co "margin of safety" cho tu tren xuong

=== KICH BAN DU BAO ===

KICH BAN 1 - CO SO (xac suat ~50%): DIEU CHINH ROI TICH LUY (3-6 thang)
  VNI dao dong 1,550-1,750, RSI on dinh 0.38-0.50
  Sau do: neu thue quan giam, kinh te on -> tang len 1,900-2,000
  Dau hieu xac nhan: RSI > 0.50, CMF > 0, MACD cat 0

KICH BAN 2 - TICH CUC (xac suat ~30%): PHUC HOI NHANH
  Neu thue quan Trump duoc giam/dam phan thanh cong
  VNI co the tang ve 1,800-1,900 trong Q2-Q3 2026
  Dieu kien: RSI > 0.55, CMF > 0.1, MACD > 0

KICH BAN 3 - TIEU CUC (xac suat ~20%): GIAM THEM
  Thue quan leo thang, recession My, USD tang manh
  VNI co the test 1,400-1,500 (MA200 area)
  RSI giam xuong 0.30-0.35 (oversold)
  -> Day cuoi cung de mua vao

=== HANH DONG PHU HOP THEO TUNG GIAI DOAN ===
Hien tai (Dieu chinh/Tich luy):
  - KHONG full buy, KHONG full sell
  - Danh sach theo doi: cat giam vi the yeu/thua lo
  - Giu tien mat 30-40%, doi tin hieu xac nhan phuc hoi
  - Mua tung phan khi RSI VNI < 0.38 (oversold) + co ban tot
  - Tin hieu MUA THEM: VNINDEX_RSI > 0.50 + CMF > 0 + MACD > 0
  - Tin hieu BAN THEM: RSI > 0.70 hoac MACD am tra lai
""")

# ── CHART ─────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(26, 20), facecolor=DARK_BG)
gs = gridspec.GridSpec(4, 3, figure=fig, hspace=0.45, wspace=0.32,
                       height_ratios=[3, 1.2, 1.2, 1.5])

years = pd.date_range("2000-01-01","2027-01-01",freq="YS")

# ── P1: VNINDEX price with phase coloring ─────────────────────────────────────
ax1 = fig.add_subplot(gs[0, :])
for ph, color in phase_colors.items():
    mask = df["phase"] == ph
    if mask.sum() == 0: continue
    ax1.fill_between(df["time"], 0, df["VNINDEX"].max()*1.15,
                     where=mask, color=color, alpha=0.12, zorder=1)

ax1.plot(df["time"], df["VNINDEX"], color=TEXT_CLR, lw=1.5, zorder=5, label="VNINDEX")
ax1.plot(df["time"], df["MA50"],    color=YELLOW,   lw=1.2, ls="--", alpha=0.7, label="MA50")
ax1.plot(df["time"], df["MA200"],   color=ORANGE,   lw=1.5, ls="--", alpha=0.9, label="MA200")

# Key annotation: current level
ax1.axhline(df["VNINDEX"].iloc[-1], color=CYAN, lw=1.0, ls=":", alpha=0.6)
ax1.annotate(f"Hien tai: {df['VNINDEX'].iloc[-1]:.0f}\nRSI={df['VNINDEX_RSI'].iloc[-1]:.2f}",
             xy=(df["time"].iloc[-1], df["VNINDEX"].iloc[-1]),
             xytext=(-80, -50), textcoords="offset points",
             fontsize=9, color=CYAN, fontweight="bold",
             arrowprops=dict(arrowstyle="->", color=CYAN, lw=1.2))

# Phase legend patches
legend_patches = [mpatches.Patch(color=c, alpha=0.6, label=phase_labels.get(p,p))
                  for p, c in phase_colors.items() if p != "unknown"]
legend1 = ax1.legend(handles=legend_patches, loc="upper left", fontsize=8,
                     ncol=4, framealpha=0.3, facecolor=PANEL_BG)
ax1.add_artist(legend1)
ax1.legend(loc="lower right", fontsize=9, framealpha=0.3)
ax1.set_ylabel("VNINDEX", fontsize=11)
ax1.set_title(f"VNINDEX 2000-{df['time'].iloc[-1].year}: Phan loai giai doan thi truong (data thuc te, bao gom 3-ngay/tuan pre-2007)",
              color=TEXT_CLR, fontweight="bold", fontsize=13)
ax1.set_xlim(df["time"].iloc[0], pd.Timestamp("2027-01-01"))
ax1.set_ylim(50, df["VNINDEX"].max()*1.18)
ax1.grid(True, alpha=0.2)
for yr in years:
    ax1.axvline(yr, color=GRID_CLR, lw=0.5, alpha=0.5)

# ── P2: VNINDEX RSI ────────────────────────────────────────────────────────────
ax2 = fig.add_subplot(gs[1, :])
ax2.plot(df["time"], df["VNINDEX_RSI"],   color=BLUE, lw=1.2, label="VNI RSI", alpha=0.9)
ax2.plot(df["time"], df["RSI_MA20"], color=YELLOW, lw=1.5, ls="--", label="RSI MA20", alpha=0.8)
ax2.axhline(0.70, color=RED,    lw=1.0, ls=":", alpha=0.7, label="Overbought (0.70)")
ax2.axhline(0.35, color=GREEN,  lw=1.0, ls=":", alpha=0.7, label="Oversold (0.35)")
ax2.axhline(0.50, color=TEXT_CLR, lw=0.8, ls="-", alpha=0.3)
ax2.fill_between(df["time"], 0.70, 1.0, alpha=0.08, color=RED)
ax2.fill_between(df["time"], 0.0, 0.35, alpha=0.08, color=GREEN)
ax2.set_ylabel("RSI", fontsize=10)
ax2.set_ylim(0, 1)
ax2.legend(fontsize=8, loc="upper right", framealpha=0.3)
ax2.set_title(f"VNINDEX RSI 2000-{df['time'].iloc[-1].year} — Vung Overbought/Oversold", color=TEXT_CLR, fontweight="bold", fontsize=10)
ax2.set_xlim(df["time"].iloc[0], pd.Timestamp("2027-01-01"))
ax2.grid(True, alpha=0.2)
for yr in years:
    ax2.axvline(yr, color=GRID_CLR, lw=0.5, alpha=0.5)
# Mark current RSI
ax2.scatter([df["time"].iloc[-1]], [df["VNINDEX_RSI"].iloc[-1]],
            color=CYAN, s=80, zorder=10)
ax2.annotate(f"  RSI={df['VNINDEX_RSI'].iloc[-1]:.3f}",
             (df["time"].iloc[-1], df["VNINDEX_RSI"].iloc[-1]),
             fontsize=8, color=CYAN)

# ── P3: CMF & MACDdiff ────────────────────────────────────────────────────────
ax3 = fig.add_subplot(gs[2, :])
ax3.bar(df["time"], df["VNINDEX_CMF"],
        color=[GREEN if v > 0 else RED for v in df["VNINDEX_CMF"]],
        width=3, alpha=0.7, label="CMF")
ax3.plot(df["time"], df["CMF_MA20"], color=YELLOW, lw=1.5, alpha=0.9, label="CMF MA20")
ax3.axhline(0, color=TEXT_CLR, lw=0.8, alpha=0.5)
ax3.set_ylabel("CMF", fontsize=10)
ax3.set_ylim(-0.6, 0.6)
ax3.legend(fontsize=8, loc="upper right", framealpha=0.3)
ax3.set_title(f"Money Flow (CMF) 2000-{df['time'].iloc[-1].year} — Dong tien vao/ra thi truong", color=TEXT_CLR, fontweight="bold", fontsize=10)
ax3.set_xlim(df["time"].iloc[0], pd.Timestamp("2027-01-01"))
ax3.grid(True, alpha=0.2)
for yr in years:
    ax3.axvline(yr, color=GRID_CLR, lw=0.5, alpha=0.5)

# ── P4: Interest Rate History ─────────────────────────────────────────────────
ax4 = fig.add_subplot(gs[3, :2])
yr_vals = [r for r in rate_history if r[0] >= 2000]
yr_x    = [r[0] for r in yr_vals]
sbv_y   = [r[1] for r in yr_vals]
dep_y   = [r[2] for r in yr_vals]
inf_y   = [r[3] for r in yr_vals]

ax4.fill_between(yr_x, 0, dep_y, alpha=0.25, color=BLUE, label="Deposit rate 12M (%)")
ax4.plot(yr_x, dep_y, color=BLUE,   lw=2.0, marker="o", ms=5, label="Deposit 12M")
ax4.plot(yr_x, sbv_y, color=YELLOW, lw=2.0, marker="s", ms=5, label="SBV base rate")
ax4.plot(yr_x, inf_y, color=RED,    lw=1.5, marker="^", ms=5, ls="--", label="Inflation %")
ax4.axhline(5.0, color=GRID_CLR, lw=0.8, ls=":", alpha=0.5)
ax4.set_xlabel("Nam", fontsize=10)
ax4.set_ylabel("% / nam", fontsize=10)
ax4.set_title("Lai suat SBV + Ngan hang + Lam phat (2000-2026)",
              color=TEXT_CLR, fontweight="bold", fontsize=10)
ax4.legend(fontsize=8, framealpha=0.3)
ax4.set_xlim(1999.5, 2026.5)
ax4.set_ylim(-2, 22)
ax4.grid(True, alpha=0.2)

# Annotate key rate events
ax4.annotate("SBV tang khan cap\n+200bp (Oct 2022)",
             xy=(2022, 6), xytext=(2020.5, 12),
             fontsize=7, color=RED, ha="center",
             arrowprops=dict(arrowstyle="->", color=RED, lw=1.0))
ax4.annotate("Cat 4 lan\n(2023)",
             xy=(2023, 4.5), xytext=(2022, 9),
             fontsize=7, color=GREEN, ha="center",
             arrowprops=dict(arrowstyle="->", color=GREEN, lw=1.0))

# ── P5: Phase cycle diagram (radial / donut) ──────────────────────────────────
ax5 = fig.add_subplot(gs[3, 2], projection="polar")
phases_cycle = [
    "Tich luy\n(Day)", "Tang som", "Tang manh",
    "Phan phoi\n(Dinh)", "Giam som", "Giam manh", "Phuc hoi"
]
colors_cycle = [TEAL, GREEN, LIME, YELLOW, ORANGE, RED, BLUE]
n_phases = len(phases_cycle)
angles = np.linspace(0, 2*np.pi, n_phases, endpoint=False)
# Current phase marker
current_phase_idx = 0  # Tich luy / Dieu chinh

for i, (ph, col) in enumerate(zip(phases_cycle, colors_cycle)):
    theta = angles[i]
    r = 0.7
    ax5.bar(theta, 0.5, width=2*np.pi/n_phases*0.85, bottom=0.3,
            color=col, alpha=0.75 if i != current_phase_idx else 1.0,
            edgecolor=DARK_BG, linewidth=2)
    ax5.text(theta, 1.05, ph, ha="center", va="center",
             fontsize=6.5, color=TEXT_CLR, fontweight="bold" if i==current_phase_idx else "normal")

# Arrow pointing to current phase
ax5.annotate("", xy=(angles[current_phase_idx], 0.85),
             xytext=(0, 0),
             arrowprops=dict(arrowstyle="->", color=CYAN, lw=2.5))
ax5.set_yticklabels([]); ax5.set_xticklabels([])
ax5.set_title("Giai doan hien tai:\nDieu chinh / Tich luy",
              color=CYAN, fontweight="bold", fontsize=10, pad=15)
ax5.set_facecolor(PANEL_BG)

fig.suptitle(
    f"VNINDEX Market Phase Analysis 2000-{df['time'].iloc[-1].year}  |  Data thuc te (incl. 3-ngay/tuan pre-2007)  |  "
    f"Today: {df['time'].iloc[-1].strftime('%B %Y')}",
    color=TEXT_CLR, fontsize=12, fontweight="bold", y=0.998
)

plt.savefig("market_phase_analysis.png", dpi=150, bbox_inches="tight", facecolor=DARK_BG)
print(f"\nChart saved: market_phase_analysis.png")
