#!/usr/bin/env python3
"""
eval_convergence_score.py
=========================
Đánh giá Convergence Score trên test set 2023+
- WR theo từng năm x từng conv_score
- WR theo từng năm x n_filters
- So sánh với baseline từng năm
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

DARK_BG="#0f1117"; PANEL_BG="#1a1d27"; GRID_CLR="#2a2d3a"; TEXT_CLR="#e0e0e0"
BLUE="#4fa3e0"; GREEN="#4ecb71"; RED="#e05c5c"; YELLOW="#f0c060"
ORANGE="#f0904a"; PURPLE="#b57bee"; TEAL="#4ecbbb"; CYAN="#4ecbee"
plt.rcParams.update({
    "figure.facecolor":DARK_BG,"axes.facecolor":PANEL_BG,"axes.edgecolor":GRID_CLR,
    "axes.labelcolor":TEXT_CLR,"xtick.color":TEXT_CLR,"ytick.color":TEXT_CLR,
    "text.color":TEXT_CLR,"grid.color":GRID_CLR,"grid.linestyle":"--","grid.alpha":0.4,
    "font.family":"DejaVu Sans",
})

TRAIN_YEAR = 2019

# ── LOAD ─────────────────────────────────────────────────────────────────────
df = pd.read_csv("data/enriched_with_convergence.csv")
df["time"] = pd.to_datetime(df["time"])
df["year"] = df["time"].dt.year

train = df[df["year"] <= TRAIN_YEAR].copy()
test  = df[df["year"] >  TRAIN_YEAR].copy()
TEST_YEARS = sorted(test["year"].unique())

print(f"Train <=2022: {len(train):,}  WR={train['is_good'].mean():.1%}")
print(f"Test  >=2023: {len(test):,}   WR={test['is_good'].mean():.1%}")
print(f"Test years  : {TEST_YEARS}")

# Baseline WR per year
base_by_year = test.groupby("year")["is_good"].mean()
print(f"\nBaseline WR by year (test):")
for y, wr in base_by_year.items():
    n = (test["year"]==y).sum()
    print(f"  {y}: WR={wr:.1%}  n={n:,}")

# ── TABLE 1: Conv Score x Year ────────────────────────────────────────────────
print(f"\n{'='*75}")
print(f"CONVERGENCE SCORE x YEAR  (Win Rate, test set 2023+)")
print(f"{'='*75}")

scores = sorted(test["conv_score"].unique())
years  = TEST_YEARS

# Print header
hdr = f"{'Conv':>6}  " + "".join(f"  {y}(WR/n)" for y in years) + "  ALL"
print(hdr)
print("-"*len(hdr))

rows_table = []
for s in scores:
    sub_all = test[test["conv_score"]==s]
    if len(sub_all) < 10: continue
    row = {"conv_score": s}
    parts = []
    for y in years:
        sub = test[(test["conv_score"]==s) & (test["year"]==y)]
        if len(sub) < 5:
            parts.append("    -    ")
            row[f"wr_{y}"] = np.nan
            row[f"n_{y}"]  = 0
        else:
            wr = sub["is_good"].mean()
            row[f"wr_{y}"] = wr
            row[f"n_{y}"]  = len(sub)
            lift = wr - base_by_year[y]
            parts.append(f"{wr:.0%}({lift:+.0%})/{len(sub)}")
    row["wr_all"] = sub_all["is_good"].mean()
    row["n_all"]  = len(sub_all)
    rows_table.append(row)
    all_str = f"{sub_all['is_good'].mean():.0%}/{len(sub_all)}"
    print(f"  {s:>4}   " + "  ".join(f"{p:>13}" for p in parts) + f"  {all_str}")

# Baseline row
parts_b = []
for y in years:
    sub = test[test["year"]==y]
    parts_b.append(f"{sub['is_good'].mean():.0%}(+0%)/{len(sub)}")
print("-"*len(hdr))
print(f"  BASE   " + "  ".join(f"{p:>13}" for p in parts_b) +
      f"  {test['is_good'].mean():.0%}/{len(test)}")

# ── TABLE 2: n_filters x Year ─────────────────────────────────────────────────
print(f"\n{'='*75}")
print(f"N_FILTERS x YEAR  (Win Rate, test set 2023+)")
print(f"{'='*75}")

nf_list = sorted(test["n_filters"].unique())
hdr2 = f"{'nFilt':>6}  " + "".join(f"  {y}(WR/n)" for y in years) + "  ALL"
print(hdr2)
print("-"*len(hdr2))

rows_nf = []
for nf in nf_list:
    sub_all = test[test["n_filters"]==nf]
    if len(sub_all) < 10: continue
    row = {"n_filters": nf}
    parts = []
    for y in years:
        sub = test[(test["n_filters"]==nf) & (test["year"]==y)]
        if len(sub) < 5:
            parts.append("    -    ")
            row[f"wr_{y}"] = np.nan
            row[f"n_{y}"]  = 0
        else:
            wr = sub["is_good"].mean()
            row[f"wr_{y}"] = wr
            row[f"n_{y}"]  = len(sub)
            lift = wr - base_by_year[y]
            parts.append(f"{wr:.0%}({lift:+.0%})/{len(sub)}")
    row["wr_all"] = sub_all["is_good"].mean()
    row["n_all"]  = len(sub_all)
    rows_nf.append(row)
    all_str = f"{sub_all['is_good'].mean():.0%}/{len(sub_all)}"
    print(f"  {nf:>4}f  " + "  ".join(f"{p:>13}" for p in parts) + f"  {all_str}")

print("-"*len(hdr2))
parts_b2 = []
for y in years:
    sub = test[test["year"]==y]
    parts_b2.append(f"{sub['is_good'].mean():.0%}(+0%)/{len(sub)}")
print(f"  BASE   " + "  ".join(f"{p:>13}" for p in parts_b2) +
      f"  {test['is_good'].mean():.0%}/{len(test)}")

# ── TABLE 3: Lift above baseline, conv_score x year ──────────────────────────
print(f"\n{'='*75}")
print(f"LIFT ABOVE BASELINE (pp) — Conv Score x Year")
print(f"{'='*75}")
pivot_wr = pd.DataFrame(rows_table).set_index("conv_score")
for y in years:
    col = f"wr_{y}"
    if col in pivot_wr.columns:
        pivot_wr[f"lift_{y}"] = (pivot_wr[col] - base_by_year.get(y, np.nan)) * 100

lift_cols = [f"lift_{y}" for y in years if f"lift_{y}" in pivot_wr.columns]
wr_cols   = [f"wr_{y}"   for y in years if f"wr_{y}"   in pivot_wr.columns]
n_cols    = [f"n_{y}"    for y in years if f"n_{y}"    in pivot_wr.columns]

print(f"\n  WR table:")
print(pivot_wr[wr_cols].round(3).to_string())
print(f"\n  Lift (pp above baseline) table:")
print(pivot_wr[lift_cols].round(1).to_string())

# ── TABLE 4: Avg profit by conv_score x year ─────────────────────────────────
print(f"\n{'='*75}")
print(f"AVG PROFIT by Conv Score x Year")
print(f"{'='*75}")
hdr3 = f"{'Conv':>6}  " + "".join(f"  {y}(avg/med)" for y in years)
print(hdr3)
print("-"*len(hdr3))
for s in scores:
    sub_all = test[test["conv_score"]==s]
    if len(sub_all) < 10: continue
    parts = []
    for y in years:
        sub = test[(test["conv_score"]==s) & (test["year"]==y)]
        if len(sub) < 5:
            parts.append("    -     ")
        else:
            parts.append(f"{sub['Sell_profit'].mean():.0f}%/{sub['Sell_profit'].median():.0f}%")
    print(f"  {s:>4}   " + "  ".join(f"{p:>13}" for p in parts))
# baseline
parts_b3 = []
for y in years:
    sub = test[test["year"]==y]
    parts_b3.append(f"{sub['Sell_profit'].mean():.0f}%/{sub['Sell_profit'].median():.0f}%")
print("-"*len(hdr3))
print(f"  BASE   " + "  ".join(f"{p:>13}" for p in parts_b3))

# ── CHART ─────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(22, 16), facecolor=DARK_BG)
gs  = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)

year_colors = {2023: BLUE, 2024: YELLOW, 2025: ORANGE, 2026: RED}

# P1: WR by conv_score, each year as separate line
ax1 = fig.add_subplot(gs[0, :])
wr_df = pd.DataFrame(rows_table).set_index("conv_score")
for y in years:
    col = f"wr_{y}"
    nc  = f"n_{y}"
    if col not in wr_df.columns: continue
    ydata = wr_df[col].dropna()
    if ydata.empty: continue
    base = base_by_year.get(y, 0)
    ax1.plot(ydata.index, ydata.values*100, "o-", lw=2.5,
             color=year_colors.get(y, PURPLE), label=f"{y} (base={base:.0%})",
             markersize=8)
    # annotate n
    for idx, val in ydata.items():
        n = wr_df.loc[idx, nc] if nc in wr_df.columns else 0
        if n >= 5:
            ax1.annotate(f"n={int(n)}", (idx, val*100),
                         textcoords="offset points", xytext=(0,8),
                         fontsize=7, color=year_colors.get(y, PURPLE), ha="center")

# Baseline dashed lines
for y in years:
    base = base_by_year.get(y, 0)
    ax1.axhline(base*100, color=year_colors.get(y, PURPLE),
                lw=1.0, ls=":", alpha=0.6)

ax1.set_xlabel("Convergence Score", fontsize=11)
ax1.set_ylabel("Win Rate (>10% profit)", fontsize=11)
ax1.set_xticks(scores)
ax1.set_title(
    f"Convergence Score vs Win Rate — Test Set 2023–2026\n"
    f"(dotted lines = baseline WR per year; n shown above each point)",
    color=TEXT_CLR, fontweight="bold", fontsize=12)
ax1.legend(fontsize=10, loc="upper left")
ax1.set_ylim(0, 85)
ax1.grid(True, alpha=0.3)

# P2: Lift heatmap (conv_score x year)
ax2 = fig.add_subplot(gs[1, 0])
lift_mat = pivot_wr[lift_cols].values  # conv_score x year
im2 = ax2.imshow(lift_mat, aspect="auto", cmap="RdYlGn",
                  vmin=-20, vmax=25)
ax2.set_xticks(range(len(years))); ax2.set_xticklabels(years)
ax2.set_yticks(range(len(pivot_wr))); ax2.set_yticklabels([f"Conv {i}" for i in pivot_wr.index])
plt.colorbar(im2, ax=ax2, label="Lift above baseline (pp)")
for i in range(len(pivot_wr)):
    for j in range(len(years)):
        val = lift_mat[i, j]
        if not np.isnan(val):
            ax2.text(j, i, f"{val:+.0f}", ha="center", va="center",
                     fontsize=10, color="white" if abs(val)>12 else TEXT_CLR,
                     fontweight="bold")
ax2.set_title("Lift vs Baseline (pp)\nConv Score × Year", color=TEXT_CLR, fontweight="bold")

# P3: n_filters x year WR
ax3 = fig.add_subplot(gs[1, 1])
nf_df = pd.DataFrame(rows_nf).set_index("n_filters")
for y in years:
    col = f"wr_{y}"
    if col not in nf_df.columns: continue
    ydata = nf_df[col].dropna()
    if ydata.empty: continue
    ax3.plot(ydata.index, ydata.values*100, "s--", lw=2.0,
             color=year_colors.get(y, PURPLE), label=str(y), markersize=7)

for y in years:
    base = base_by_year.get(y, 0)
    ax3.axhline(base*100, color=year_colors.get(y, PURPLE), lw=0.8, ls=":", alpha=0.5)

ax3.set_xlabel("# Unique Filters in 30-day Window", fontsize=10)
ax3.set_ylabel("Win Rate (%)", fontsize=10)
ax3.set_title("n_filters vs Win Rate by Year\n(dotted = baseline per year)",
              color=TEXT_CLR, fontweight="bold")
ax3.legend(fontsize=9)
ax3.set_ylim(0, 85)

fig.suptitle(
    f"Convergence Score Evaluation  |  Test 2023-2026  |  "
    f"Train ≤2022 ({len(train):,} deals)  |  Test ≥2023 ({len(test):,} deals)",
    color=TEXT_CLR, fontsize=13, fontweight="bold", y=0.995)

plt.savefig("eval_convergence_score.png", dpi=150, bbox_inches="tight", facecolor=DARK_BG)
print(f"\nChart saved: eval_convergence_score.png")

# ── FINAL VERDICT ─────────────────────────────────────────────────────────────
print(f"\n{'='*75}")
print(f"VERDICT — Conv Score effectiveness by year")
print(f"{'='*75}")
for y in TEST_YEARS:
    base = base_by_year.get(y, 0)
    print(f"\n  [{y}]  Baseline WR = {base:.1%}")
    for s in scores:
        sub = test[(test["conv_score"]==s) & (test["year"]==y)]
        if len(sub) < 10: continue
        wr   = sub["is_good"].mean()
        lift = (wr - base) * 100
        avg  = sub["Sell_profit"].mean()
        mark = " <-- BEST" if lift == max(
            (test[(test["conv_score"]==ss)&(test["year"]==y)]["is_good"].mean() - base)*100
            for ss in scores
            if len(test[(test["conv_score"]==ss)&(test["year"]==y)]) >= 10
        ) else ""
        print(f"    Conv={s}  n={len(sub):>4}  WR={wr:.1%}  lift={lift:>+5.1f}pp  "
              f"avg={avg:.1f}%{mark}")
print()
