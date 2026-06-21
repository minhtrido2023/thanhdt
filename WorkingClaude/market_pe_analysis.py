#!/usr/bin/env python3
"""
market_pe_analysis.py
======================
Phan tich moi quan he giua PE thi truong va cac giai doan VNIndex
- PE histogram phan bo theo tung giai doan
- PE median vs VNIndex qua thoi gian
- PE signal cho dinh / day thi truong
- Danh gia PE hien tai
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as mticker
from scipy import stats

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

# ── LOAD DATA ──────────────────────────────────────────────────────────────────
pe  = pd.read_csv("market_pe_monthly.csv")
vni = pd.read_csv("vnindex_data.csv")

pe["month"]  = pd.to_datetime(pe["month"])
vni["time"]  = pd.to_datetime(vni["time"])

# Monthly VNINDEX from daily data
vni["month"] = vni["time"].dt.to_period("M").dt.to_timestamp()
vni_m = vni.groupby("month").agg(
    vni_avg=("VNINDEX","mean"),
    vni_max=("VNINDEX","max"),
    vni_min=("VNINDEX","min"),
    rsi_avg=("VNINDEX_RSI","mean"),
    cmf_avg=("VNINDEX_CMF","mean"),
    macd_avg=("VNINDEX_MACDdiff","mean"),
    rsi_max=("VNINDEX_RSI","max"),
    rsi_min=("VNINDEX_RSI","min"),
).reset_index()

# Merge PE + VNINDEX
df = pe.merge(vni_m, on="month", how="inner", suffixes=("_pe",""))
# Resolve column conflict: use vni_m's vni_avg (more granular from daily)
df = df.rename(columns={"vni_avg_pe":"vni_avg_bq"})
df = df.sort_values("month").reset_index(drop=True)

# PE ratios: % stocks in each bucket
total = df["n_valid"]
df["pct_cheap"]     = df["n_cheap"]     / total * 100   # PE < 12
df["pct_fair"]      = df["n_fair"]      / total * 100   # PE 12-20
df["pct_growth"]    = df["n_growth"]    / total * 100   # PE 20-35
df["pct_expensive"] = df["n_expensive"] / total * 100   # PE 35-100

# Market phase labels
def label_phase(row):
    rsi = row["rsi_avg"]
    cmf = row["cmf_avg"]
    macd = row["macd_avg"]
    if rsi > 0.68:                              return "DIST/DINH"
    elif rsi > 0.55 and macd > 0:              return "TANG_MANH"
    elif rsi > 0.45 and macd > 0:              return "TANG_SOM"
    elif rsi < 0.35:                            return "GIAM_MANH"
    elif rsi < 0.45 and cmf < 0 and macd < 0: return "GIAM_MANH"
    elif rsi < 0.45 and macd < 0:              return "DIEU_CHINH"
    elif macd < -3:                             return "GIAM_MANH"
    else:                                       return "TICH_LUY"

df["phase"] = df.apply(label_phase, axis=1)

phase_colors = {
    "DIST/DINH":  YELLOW,
    "TANG_MANH":  LIME,
    "TANG_SOM":   GREEN,
    "GIAM_MANH":  RED,
    "DIEU_CHINH": ORANGE,
    "TICH_LUY":   TEAL,
}
phase_vi = {
    "DIST/DINH":  "Phan phoi/Dinh",
    "TANG_MANH":  "Tang truong manh",
    "TANG_SOM":   "Tang truong som",
    "GIAM_MANH":  "Giam manh",
    "DIEU_CHINH": "Dieu chinh",
    "TICH_LUY":   "Tich luy/Day",
}

# ── PRINT: PE stats by phase ───────────────────────────────────────────────────
print("="*75)
print("PE PHAN BO THEO TUNG GIAI DOAN THI TRUONG (2014-2026)")
print("="*75)
print(f"\n{'Giai doan':<22} {'n':>4}  {'VNI':>7}  {'PE_P25':>7}  {'PE_MED':>7}  {'PE_P75':>7}  "
      f"{'%Cheap':>7}  {'%Fair':>7}  {'%Grow':>7}  {'%Exp':>7}  {'PB_med':>7}")
print("-"*95)

phase_pe = {}
for ph in ["TANG_MANH","TANG_SOM","DIST/DINH","DIEU_CHINH","GIAM_MANH","TICH_LUY"]:
    sub = df[df["phase"]==ph]
    if len(sub) == 0: continue
    phase_pe[ph] = sub
    print(f"  {phase_vi[ph]:<22} {len(sub):>4}  "
          f"{sub['vni_avg'].mean():>7.0f}  "
          f"{sub['pe_p25'].mean():>7.1f}  "
          f"{sub['pe_median'].mean():>7.1f}  "
          f"{sub['pe_p75'].mean():>7.1f}  "
          f"{sub['pct_cheap'].mean():>7.1f}%  "
          f"{sub['pct_fair'].mean():>7.1f}%  "
          f"{sub['pct_growth'].mean():>7.1f}%  "
          f"{sub['pct_expensive'].mean():>7.1f}%  "
          f"{sub['pb_median'].mean():>7.2f}")

print("-"*95)
print(f"  {'TONG THE':<22} {len(df):>4}  "
      f"{df['vni_avg'].mean():>7.0f}  "
      f"{df['pe_p25'].mean():>7.1f}  "
      f"{df['pe_median'].mean():>7.1f}  "
      f"{df['pe_p75'].mean():>7.1f}  "
      f"{df['pct_cheap'].mean():>7.1f}%  "
      f"{df['pct_fair'].mean():>7.1f}%  "
      f"{df['pct_growth'].mean():>7.1f}%  "
      f"{df['pct_expensive'].mean():>7.1f}%  "
      f"{df['pb_median'].mean():>7.2f}")

# ── KEY TURNING POINTS PE ────────────────────────────────────────────────────
print(f"\n{'='*75}")
print("PE TAI CAC DINH / DAY LICH SU")
print(f"{'='*75}")

turning_points = [
    ("2015-06", "DINH 2015",   640),
    ("2018-04", "DINH 2018",  1200),
    ("2020-03", "DAY COVID",   655),
    ("2021-11", "DINH 2021",  1500),
    ("2022-11", "DAY 2022",    870),
    ("2024-01", "DAY 2024",   1050),
    ("2025-09", "DINH 2025",  1800),
    ("2026-03", "HIEN TAI",   1663),
]
print(f"\n{'Thoi diem':<12} {'Ghi chu':<15} {'VNI':>7}  {'PE_P25':>7}  {'PE_MED':>7}  {'PE_P75':>7}  {'%Cheap':>7}  {'%Exp':>7}  {'PB_med':>7}")
print("-"*90)
for date_str, label, approx_vni in turning_points:
    try:
        row = df[df["month"].dt.strftime("%Y-%m") == date_str]
        if len(row) == 0:
            row = df.iloc[(df["month"] - pd.Timestamp(date_str+"-01")).abs().argsort()[:1]]
        row = row.iloc[0]
        print(f"  {date_str:<12} {label:<15} {row['vni_avg']:>7.0f}  "
              f"{row['pe_p25']:>7.1f}  {row['pe_median']:>7.1f}  {row['pe_p75']:>7.1f}  "
              f"{row['pct_cheap']:>7.1f}%  {row['pct_expensive']:>7.1f}%  "
              f"{row['pb_median']:>7.2f}")
    except:
        print(f"  {date_str:<12} {label:<15} {'N/A':>7}")

# ── CORRELATION ANALYSIS ────────────────────────────────────────────────────
print(f"\n{'='*75}")
print("TUONG QUAN: PE vs VNIndex")
print(f"{'='*75}")
corr_vni_pe  = df["vni_avg"].corr(df["pe_median"])
corr_vni_pct = df["vni_avg"].corr(df["pct_cheap"])
corr_rsi_pe  = df["rsi_avg"].corr(df["pe_median"])
corr_rsi_pct = df["rsi_avg"].corr(df["pct_cheap"])
print(f"  VNI avg  vs PE median:  r = {corr_vni_pe:+.3f}  {'(tuong quan thuan - VNI cao -> PE cao)' if corr_vni_pe>0 else '(tuong quan nghich)'}")
print(f"  VNI avg  vs %Cheap:     r = {corr_vni_pct:+.3f}  {'(VNI cao -> it co phieu re)' if corr_vni_pct<0 else '(VNI cao -> nhieu co phieu re - earnings tang)'}")
print(f"  RSI avg  vs PE median:  r = {corr_rsi_pe:+.3f}  {'(thi truong bong -> PE cao)' if corr_rsi_pe>0 else '(RSI cao nhung PE khong tang - earnings tot)'}")
print(f"  RSI avg  vs %Cheap:     r = {corr_rsi_pct:+.3f}")

# PE expansion/compression ratio
print(f"\nPE expansion tu day->dinh:")
print(f"  Day 2020 (VNI=655):  PE_median = {df[df['month'].dt.strftime('%Y-%m')=='2020-03']['pe_median'].values[0]:.1f}")
print(f"  Dinh 2021 (VNI=1500): PE_median = {df[df['month'].dt.strftime('%Y-%m')=='2021-11']['pe_median'].values[0]:.1f}")
print(f"  Day 2022 (VNI=870):  PE_median = {df[df['month'].dt.strftime('%Y-%m')=='2022-11']['pe_median'].values[0]:.1f}")
print(f"  Jan 2026 (VNI=1858): PE_median = {df[df['month'].dt.strftime('%Y-%m')=='2026-01']['pe_median'].values[0]:.1f}")
print(f"  Mar 2026 (VNI=1663): PE_median = {df[df['month'].dt.strftime('%Y-%m')=='2026-03']['pe_median'].values[0]:.1f}")

# ── CURRENT STATE ───────────────────────────────────────────────────────────
print(f"\n{'='*75}")
print("DANH GIA PE HIEN TAI (March 2026)")
print(f"{'='*75}")
cur = df.iloc[-1]
hist_pe_med = df["pe_median"]
pct_rank = (hist_pe_med < cur["pe_median"]).mean()
print(f"""
PE Median thi truong hien tai: {cur['pe_median']:.2f}x
  - Percentile lich su (2014-2026): {pct_rank:.0%} (cao hon {pct_rank:.0%} so voi lich su)
  - PE_P25: {cur['pe_p25']:.1f}  PE_P75: {cur['pe_p75']:.1f}
  - % co phieu re (PE<12): {cur['pct_cheap']:.1f}%
  - % co phieu hop ly (PE 12-20): {cur['pct_fair']:.1f}%
  - % co phieu tang truong (PE 20-35): {cur['pct_growth']:.1f}%
  - % co phieu dat (PE>35): {cur['pct_expensive']:.1f}%
  - PB Median: {cur['pb_median']:.2f}x

So sanh voi cac moc lich su:
  - PE_median thap nhat (2014): {hist_pe_med.min():.1f}x  => hien tai cao hon {cur['pe_median']/hist_pe_med.min()-1:.0%}
  - PE_median trung binh: {hist_pe_med.mean():.1f}x  => hien tai {'cao' if cur['pe_median']>hist_pe_med.mean() else 'thap'} hon {abs(cur['pe_median']/hist_pe_med.mean()-1):.0%}
  - PE_median cao nhat: {hist_pe_med.max():.1f}x  => hien tai = {cur['pe_median']/hist_pe_med.max():.0%} so voi peak

NHAN XET:
  PE_median {cur['pe_median']:.1f}x la muc {'THAP-TRUNG BINH' if cur['pe_median'] < hist_pe_med.quantile(0.4) else 'TRUNG BINH' if cur['pe_median'] < hist_pe_med.quantile(0.6) else 'TRUNG BINH-CAO' if cur['pe_median'] < hist_pe_med.quantile(0.8) else 'CAO'}.
  {cur['pct_cheap']:.0f}% co phieu co PE < 12 (vung 're') -> van con nhieu co phieu gia tri.
  PE thi truong KHONG cao bat thuong du VNI dang o ATH ->
  earnings cac cong ty da tang rat manh de bao giao PE hien tai.
  -> Day la tin hieu TICH CUC: tang truong VNI duoc ho tro boi earnings that su.
""")

# ── CHART ─────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(26, 22), facecolor=DARK_BG)
gs = gridspec.GridSpec(4, 3, figure=fig, hspace=0.50, wspace=0.35,
                       height_ratios=[2.5, 2, 2, 2])

months = df["month"]
years_ticks = pd.date_range("2014-01-01","2027-01-01",freq="YS")

# ── P1: VNIndex + PE Median over time ─────────────────────────────────────────
ax1a = fig.add_subplot(gs[0, :])
ax1b = ax1a.twinx()

# Background phase shading
for ph, col in phase_colors.items():
    mask = df["phase"] == ph
    if mask.sum() == 0: continue
    for i in df[mask].index:
        ax1a.axvspan(df["month"].iloc[i],
                     df["month"].iloc[min(i+1, len(df)-1)],
                     alpha=0.15, color=col, zorder=1)

ax1a.fill_between(months, df["vni_min"], df["vni_max"], alpha=0.15, color=TEXT_CLR)
ax1a.plot(months, df["vni_avg"], color=TEXT_CLR, lw=2.0, zorder=5, label="VNIndex")
ax1b.plot(months, df["pe_median"], color=CYAN, lw=2.5, zorder=6, label="PE Median")
ax1b.fill_between(months, df["pe_p25"], df["pe_p75"],
                  alpha=0.20, color=CYAN, label="PE P25-P75")

# Reference lines for PE
ax1b.axhline(df["pe_median"].mean(), color=CYAN, lw=1.0, ls=":", alpha=0.5)
ax1b.axhline(df["pe_median"].quantile(0.75), color=YELLOW, lw=1.0, ls="--", alpha=0.5)
ax1b.axhline(df["pe_median"].quantile(0.25), color=GREEN, lw=1.0, ls="--", alpha=0.5)

# Annotations at key peaks/troughs
annotations = [
    ("2018-04", "Dinh 2018\nPE={:.1f}", RED),
    ("2020-03", "Day COVID\nPE={:.1f}", GREEN),
    ("2021-11", "Dinh 2021\nPE={:.1f}", RED),
    ("2022-11", "Day 2022\nPE={:.1f}", GREEN),
    ("2026-01", "ATH 2026\nPE={:.1f}", YELLOW),
]
for date_str, label_fmt, col in annotations:
    row_mask = df["month"].dt.strftime("%Y-%m") == date_str
    if row_mask.sum() == 0: continue
    row = df[row_mask].iloc[0]
    ax1b.scatter([row["month"]], [row["pe_median"]], color=col, s=120, zorder=10)
    ax1b.annotate(label_fmt.format(row["pe_median"]),
                  xy=(row["month"], row["pe_median"]),
                  xytext=(0, 18), textcoords="offset points",
                  fontsize=7.5, color=col, ha="center", fontweight="bold",
                  arrowprops=dict(arrowstyle="->", color=col, lw=0.8))

ax1a.set_ylabel("VNIndex", fontsize=11, color=TEXT_CLR)
ax1b.set_ylabel("PE Median (thi truong)", fontsize=11, color=CYAN)
ax1b.tick_params(colors=CYAN)
ax1a.set_title("VNIndex & PE Median thi truong 2014-2026\n"
               "(Vung to mau = giai doan; Dai CYAN = PE P25-P75)",
               color=TEXT_CLR, fontweight="bold", fontsize=12)
lines1, labs1 = ax1a.get_legend_handles_labels()
lines2, labs2 = ax1b.get_legend_handles_labels()
ax1a.legend(lines1+lines2, labs1+labs2, loc="upper left", fontsize=9, framealpha=0.3)
ax1a.set_xlim(months.iloc[0], pd.Timestamp("2027-01-01"))
ax1a.set_ylim(300, df["vni_max"].max()*1.15)
ax1b.set_ylim(4, 28)
ax1a.grid(True, alpha=0.2)
for yr in years_ticks:
    ax1a.axvline(yr, color=GRID_CLR, lw=0.5, alpha=0.5)

# Phase legend
import matplotlib.patches as mpatches
legend_patches = [mpatches.Patch(color=c, alpha=0.6, label=phase_vi[p])
                  for p, c in phase_colors.items()]
ax1a.legend(handles=legend_patches, loc="upper left", fontsize=8,
            ncol=3, framealpha=0.3, facecolor=PANEL_BG)

# ── P2: PE Histogram by Phase ─────────────────────────────────────────────────
pe_buckets = ["pct_cheap","pct_fair","pct_growth","pct_expensive"]
pe_labels  = ["PE<12\n(Re)", "PE 12-20\n(Hop ly)", "PE 20-35\n(Tang tr.)", "PE>35\n(Dat)"]
pe_cols    = [GREEN, BLUE, YELLOW, RED]

phases_order = ["GIAM_MANH","TICH_LUY","TANG_SOM","TANG_MANH","DIST/DINH","DIEU_CHINH"]
ax2 = fig.add_subplot(gs[1, :2])
x = np.arange(len(phases_order))
w = 0.18
for i, (bkt, lbl, col) in enumerate(zip(pe_buckets, pe_labels, pe_cols)):
    means = [df[df["phase"]==ph][bkt].mean() if (df["phase"]==ph).sum()>0 else 0
             for ph in phases_order]
    bars = ax2.bar(x + (i-1.5)*w, means, w, label=lbl, color=col, alpha=0.85)
    for bar, val in zip(bars, means):
        if val > 3:
            ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.3,
                     f"{val:.0f}%", ha="center", fontsize=6.5, color=col)

ax2.set_xticks(x)
ax2.set_xticklabels([phase_vi[p] for p in phases_order], fontsize=8.5, rotation=10)
ax2.set_ylabel("% so phieu trong gio hang", fontsize=10)
ax2.set_title("Phan bo % Co phieu theo Nhom PE trong tung Giai doan thi truong",
              color=TEXT_CLR, fontweight="bold", fontsize=11)
ax2.legend(fontsize=9, loc="upper right", framealpha=0.3)
ax2.set_ylim(0, 80)
ax2.grid(True, alpha=0.2, axis="y")

# ── P3: PE Median box/violin by Phase ─────────────────────────────────────────
ax3 = fig.add_subplot(gs[1, 2])
pe_data_by_phase = [df[df["phase"]==ph]["pe_median"].values
                    for ph in phases_order]
parts = ax3.violinplot(pe_data_by_phase, positions=range(len(phases_order)),
                       showmedians=True, showextrema=True)
for i, (pc, ph) in enumerate(zip(parts["bodies"], phases_order)):
    pc.set_facecolor(phase_colors[ph])
    pc.set_alpha(0.7)
parts["cmedians"].set_color(TEXT_CLR)
parts["cbars"].set_color(GRID_CLR)
parts["cmaxes"].set_color(GRID_CLR)
parts["cmins"].set_color(GRID_CLR)

ax3.set_xticks(range(len(phases_order)))
ax3.set_xticklabels([phase_vi[p].replace(" ","\n") for p in phases_order], fontsize=7)
ax3.set_ylabel("PE Median (thi truong)", fontsize=10)
ax3.set_title("Phan phoi PE Median\ntheo Giai doan", color=TEXT_CLR, fontweight="bold", fontsize=10)
ax3.axhline(df["pe_median"].mean(), color=CYAN, lw=1.2, ls="--", alpha=0.7, label="Overall avg")
ax3.scatter(len(phases_order)-0.5,
            df.iloc[-1]["pe_median"], color=CYAN, s=150, zorder=10,
            marker="*", label=f"Hien tai {df.iloc[-1]['pe_median']:.1f}x")
ax3.legend(fontsize=8, framealpha=0.3)
ax3.grid(True, alpha=0.2, axis="y")

# ── P4: % Cheap over time + VNI ───────────────────────────────────────────────
ax4a = fig.add_subplot(gs[2, :2])
ax4b = ax4a.twinx()
ax4a.fill_between(months, df["pct_cheap"], alpha=0.4, color=GREEN, label="% PE<12 (Re)")
ax4a.plot(months, df["pct_cheap"], color=GREEN, lw=1.5)
ax4a.fill_between(months, df["pct_expensive"], alpha=0.3, color=RED, label="% PE>35 (Dat)")
ax4a.plot(months, df["pct_expensive"], color=RED, lw=1.2, ls="--")
ax4b.plot(months, df["vni_avg"], color=TEXT_CLR, lw=1.8, alpha=0.7, label="VNIndex")
ax4a.set_ylabel("% Co phieu trong gio hang", fontsize=10)
ax4b.set_ylabel("VNIndex", fontsize=10)
ax4a.set_title("% Co phieu Re (PE<12) vs Dat (PE>35) va VNIndex",
               color=TEXT_CLR, fontweight="bold", fontsize=10)
lines1, labs1 = ax4a.get_legend_handles_labels()
lines2, labs2 = ax4b.get_legend_handles_labels()
ax4a.legend(lines1+lines2, labs1+labs2, fontsize=8, framealpha=0.3)
ax4a.set_xlim(months.iloc[0], pd.Timestamp("2027-01-01"))
ax4a.set_ylim(0, 90)
ax4a.grid(True, alpha=0.2)
for yr in years_ticks:
    ax4a.axvline(yr, color=GRID_CLR, lw=0.5, alpha=0.4)

# ── P5: PE_median vs VNI scatter colored by phase ─────────────────────────────
ax5 = fig.add_subplot(gs[2, 2])
for ph, col in phase_colors.items():
    sub = df[df["phase"]==ph]
    if len(sub) == 0: continue
    ax5.scatter(sub["pe_median"], sub["vni_avg"],
                color=col, alpha=0.75, s=45, label=phase_vi[ph], zorder=4)

# Trend line
slope, intercept, r, p, se = stats.linregress(df["pe_median"], df["vni_avg"])
pe_range = np.linspace(df["pe_median"].min(), df["pe_median"].max(), 100)
ax5.plot(pe_range, slope*pe_range+intercept, color=CYAN, lw=1.5, ls="--",
         alpha=0.7, label=f"Trend (r={r:.2f})")
# Current point
cur = df.iloc[-1]
ax5.scatter([cur["pe_median"]], [cur["vni_avg"]], color=CYAN, s=200,
            marker="*", zorder=10, label=f"Hien tai ({cur['pe_median']:.1f}x, {cur['vni_avg']:.0f})")
ax5.set_xlabel("PE Median (thi truong)", fontsize=10)
ax5.set_ylabel("VNIndex avg", fontsize=10)
ax5.set_title("PE Median vs VNIndex\n(mau = giai doan)", color=TEXT_CLR, fontweight="bold", fontsize=10)
ax5.legend(fontsize=7, framealpha=0.3, loc="upper left")
ax5.grid(True, alpha=0.2)

# ── P6: PE Histogram snapshot: 4 key moments ──────────────────────────────────
ax6 = fig.add_subplot(gs[3, :])
snapshot_months = [
    ("2018-04", "Dinh 2018 (VNI=1200)", RED),
    ("2020-03", "Day COVID (VNI=655)", GREEN),
    ("2021-11", "Dinh 2021 (VNI=1500)", ORANGE),
    ("2022-11", "Day 2022 (VNI=870)", TEAL),
    ("2026-01", "ATH 2026 (VNI=1858)", YELLOW),
    ("2026-03", "Hien tai (VNI=1663)", CYAN),
]

pe_bins = ["PE<8", "PE 8-12", "PE 12-16", "PE 16-20", "PE 20-25", "PE 25-35", "PE>35"]
x_bins  = np.arange(len(pe_bins))
w_snap  = 0.12

for i, (date_str, label, col) in enumerate(snapshot_months):
    row_mask = df["month"].dt.strftime("%Y-%m") == date_str
    if row_mask.sum() == 0:
        nearest = df.iloc[(df["month"] - pd.Timestamp(date_str+"-01")).abs().argsort()[:1]]
        row = nearest.iloc[0]
    else:
        row = df[row_mask].iloc[0]
    n = row["n_valid"]
    # Reconstruct approximate bin proportions from percentile data
    p10, p25, p50, p75, p90 = (row["pe_p10"], row["pe_p25"],
                                row["pe_median"], row["pe_p75"], row["pe_p90"])
    cheap_pct     = row["pct_cheap"]       # PE<12
    fair_pct      = row["pct_fair"]        # 12-20
    growth_pct    = row["pct_growth"]      # 20-35
    expensive_pct = row["pct_expensive"]   # 35+

    bins_pct = [
        max(0, cheap_pct * (1 - (p25-8)/max(p25-4,1))),   # PE<8 est
        cheap_pct - max(0, cheap_pct * (1 - (p25-8)/max(p25-4,1))),  # 8-12
        fair_pct * 0.55,   # 12-16
        fair_pct * 0.45,   # 16-20
        growth_pct * 0.45, # 20-25
        growth_pct * 0.55, # 25-35
        expensive_pct,     # >35
    ]
    bars = ax6.bar(x_bins + (i-2.5)*w_snap, bins_pct, w_snap,
                   color=col, alpha=0.75, label=label)

ax6.set_xticks(x_bins)
ax6.set_xticklabels(pe_bins, fontsize=10)
ax6.set_ylabel("% co phieu", fontsize=10)
ax6.set_xlabel("Nhom PE", fontsize=10)
ax6.set_title("Histogram PE thi truong tai cac moc lich su quan trong\n"
              "(So sanh cau truc PE: Dinh vs Day vs Hien tai)",
              color=TEXT_CLR, fontweight="bold", fontsize=11)
ax6.legend(fontsize=8.5, framealpha=0.3, loc="upper right")
ax6.grid(True, alpha=0.2, axis="y")
ax6.set_ylim(0, 75)

fig.suptitle(
    "Phan tich PE Thi truong & Giai doan VNIndex 2014-2026  |  "
    f"PE Median hien tai: {df.iloc[-1]['pe_median']:.1f}x  |  VNI: {df.iloc[-1]['vni_avg']:.0f}",
    color=TEXT_CLR, fontsize=13, fontweight="bold", y=0.998
)

plt.savefig("market_pe_analysis.png", dpi=150, bbox_inches="tight", facecolor=DARK_BG)
print("Chart saved: market_pe_analysis.png")
