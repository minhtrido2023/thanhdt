#!/usr/bin/env python3
"""
analyze_filter_sequence.py  (Phase 6)
======================================
Multi-filter convergence: khi nhiều filter cùng hit một ticker trong 30 ngày,
win rate thay đổi thế nào? Thứ tự có quan trọng không?

Approach: vectorized self-join (không loop row-by-row)
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

WINDOW   = 30
TARGET   = 10.0

# ── LOAD ─────────────────────────────────────────────────────────────────────
print("Loading ...")
df = pd.read_csv("data/profile_hit.csv")
df["time"] = pd.to_datetime(df["time"])

closed = df[df["Sell_filter"] != "Hold"].copy()
closed["is_good"] = (closed["Sell_profit"] > TARGET).astype(int)
closed["year"]    = closed["time"].dt.year

hold = df[df["Sell_filter"] == "Hold"].copy()

print(f"  Closed: {len(closed):,}  Hold: {len(hold):,}  WR: {closed['is_good'].mean():.1%}")

# Filter taxonomy
TECHNICAL   = {"RSILow30","BullDvg","TL3M","VolMax1Y","BKMA200"}
FUNDAMENTAL = {"UnderBV","Conservative","DividendYield","CashCowStock",
               "SuperGrowth","SurpriseEarning","TrendingGrowth"}
SUPPORT     = {"BuySupport","TradingValueMax"}

def ftype(f):
    if f in TECHNICAL:   return "Tech"
    if f in FUNDAMENTAL: return "Fund"
    return "Sup"

# All hits as reference (buy side only — the filter column)
all_hits = df[["ticker","time","filter"]].copy()
all_hits["ftype"] = all_hits["filter"].map(ftype)

# ── VECTORIZED SELF-JOIN per ticker ─────────────────────────────────────────
# For each closed deal, count distinct filters in [time-30d, time]
# Strategy: merge closed with all_hits on ticker, then filter by date window
# Process in chunks by ticker to avoid OOM

print(f"Building {WINDOW}-day convergence (vectorized self-join) ...")

WINDOW_TD = pd.Timedelta(days=WINDOW)

results = []
tickers = closed["ticker"].unique()
n_tck   = len(tickers)

for i, ticker in enumerate(tickers):
    if i % 100 == 0:
        print(f"  {i}/{n_tck} tickers ...", end="\r")

    c = closed[closed["ticker"] == ticker][["time","filter","Sell_profit","is_good","year"]].copy()
    h = all_hits[all_hits["ticker"] == ticker][["time","filter","ftype"]].copy()
    h = h.rename(columns={"time":"hit_time","filter":"hit_filter","ftype":"hit_ftype"})

    if c.empty or h.empty:
        continue

    # cross join: each deal row x each hit row
    c["_k"] = 1; h["_k"] = 1
    cross = c.merge(h, on="_k").drop("_k", axis=1)

    # keep only hits within [deal_time - 30d, deal_time]
    cross = cross[
        (cross["hit_time"] >= cross["time"] - WINDOW_TD) &
        (cross["hit_time"] <= cross["time"])
    ]

    if cross.empty:
        # no hits found (shouldn't happen, but handle gracefully)
        for _, row in c.iterrows():
            results.append({
                "ticker": ticker, "time": row["time"],
                "filter": row["filter"], "Sell_profit": row["Sell_profit"],
                "is_good": row["is_good"], "year": row["year"],
                "n_filters": 0, "filters_set": "",
                "n_types": 0, "has_tech": False, "has_fund": False,
                "first_ftype": ftype(row["filter"]), "days_span": 0,
            })
        continue

    # aggregate per deal
    agg = cross.groupby(["time","filter","Sell_profit","is_good","year"]).agg(
        n_filters    = ("hit_filter", "nunique"),
        filters_set  = ("hit_filter", lambda x: "|".join(sorted(set(x)))),
        has_tech     = ("hit_ftype",  lambda x: "Tech" in set(x)),
        has_fund     = ("hit_ftype",  lambda x: "Fund" in set(x)),
        n_types      = ("hit_ftype",  "nunique"),
        min_hit_time = ("hit_time",   "min"),
        max_hit_time = ("hit_time",   "max"),
    ).reset_index()

    agg["days_span"] = (agg["max_hit_time"] - agg["min_hit_time"]).dt.days
    agg["ticker"]    = ticker

    # first ftype = ftype of the earliest hit in window
    first_hits = cross.sort_values("hit_time").groupby(["time","filter"]).first().reset_index()
    first_hits = first_hits[["time","filter","hit_ftype"]].rename(columns={"hit_ftype":"first_ftype"})
    agg = agg.merge(first_hits, on=["time","filter"], how="left")

    results.append(agg[["ticker","time","filter","Sell_profit","is_good","year",
                         "n_filters","filters_set","has_tech","has_fund",
                         "n_types","first_ftype","days_span"]])

print(f"\n  Aggregating {n_tck} tickers ...")
enriched = pd.concat(results, ignore_index=True)
print(f"  Enriched: {len(enriched):,} deals")

# Sanity check
print(f"  n_filters distribution: {enriched['n_filters'].value_counts().sort_index().head(8).to_dict()}")

enriched["current_ftype"] = enriched["filter"].map(ftype)
enriched["seq_key"] = np.where(
    enriched["days_span"] > 0,
    enriched["first_ftype"].fillna("?") + "->" + enriched["current_ftype"],
    enriched["current_ftype"]
)

base_wr  = enriched["is_good"].mean()
base_avg = enriched["Sell_profit"].mean()
print(f"  Baseline WR: {base_wr:.1%}  avg profit: {base_avg:.1f}%")

# ── H1: WIN RATE BY N_FILTERS ────────────────────────────────────────────────
print(f"\n{'='*65}")
print(f"H1: Win Rate by # Unique Filters in {WINDOW}-day Window")
print(f"{'='*65}")
n_stats = []
for n in sorted(enriched["n_filters"].unique()):
    sub = enriched[enriched["n_filters"] == n]
    if len(sub) < 20: continue
    wr  = sub["is_good"].mean()
    avg = sub["Sell_profit"].mean()
    med = sub["Sell_profit"].median()
    lift= wr / base_wr - 1
    n_stats.append({"n_filters":n, "count":len(sub), "wr":wr, "avg":avg, "med":med, "lift":lift})
    print(f"  {n} filter(s): n={len(sub):>6}  WR={wr:.1%}  lift={lift:>+5.0%}  "
          f"avg={avg:.1f}%  med={med:.1f}%")
nd = pd.DataFrame(n_stats)

# ── H4: TOP COMBOS ────────────────────────────────────────────────────────────
print(f"\n{'='*65}")
print(f"H4: Top Filter Combos (2+ filters, n>=50, sorted by WR)")
print(f"{'='*65}")
combo_stats = (enriched[enriched["n_filters"] >= 2]
               .groupby("filters_set")
               .agg(n=("is_good","count"), wr=("is_good","mean"),
                    avg=("Sell_profit","mean"), med=("Sell_profit","median"))
               .query("n >= 50")
               .sort_values("wr", ascending=False))
print(f"{'Combo':<55} {'n':>6} {'WR':>7} {'Lift':>6} {'Avg':>7} {'Med':>7}")
print("-"*96)
for combo, row in combo_stats.head(25).iterrows():
    lift = row["wr"] / base_wr - 1
    print(f"  {combo:<53} {int(row['n']):>6} {row['wr']:>6.1%} {lift:>+5.0%} "
          f"{row['avg']:>6.1f}% {row['med']:>6.1f}%")

# ── H2: SEQUENCE ──────────────────────────────────────────────────────────────
print(f"\n{'='*65}")
print(f"H2: Sequence Pattern  (first filter type -> current type)")
print(f"{'='*65}")
seq_stats = (enriched[enriched["days_span"] > 0]
             .groupby("seq_key")
             .agg(n=("is_good","count"), wr=("is_good","mean"), avg=("Sell_profit","mean"))
             .query("n >= 50").sort_values("wr", ascending=False))
for seq, row in seq_stats.iterrows():
    print(f"  {seq:<22} n={int(row['n']):>5}  WR={row['wr']:.1%}  "
          f"lift={row['wr']/base_wr-1:>+5.0%}  avg={row['avg']:.1f}%")

# ── H3: TIME SPAN ─────────────────────────────────────────────────────────────
print(f"\n{'='*65}")
print(f"H3: Time Span Between First and Last Filter Hit (multi-filter only)")
print(f"{'='*65}")
multi = enriched[enriched["n_filters"] >= 2].copy()
bins  = [-1, 0, 3, 7, 14, 21, 30]
lbls  = ["same-day","1-3d","4-7d","8-14d","15-21d","22-30d"]
multi["span_bin"] = pd.cut(multi["days_span"], bins=bins, labels=lbls)
span_stats = multi.groupby("span_bin", observed=True).agg(
    n=("is_good","count"), wr=("is_good","mean"), avg=("Sell_profit","mean"))
for sb, row in span_stats.iterrows():
    print(f"  {str(sb):<10} n={int(row['n']):>5}  WR={row['wr']:.1%}  "
          f"lift={row['wr']/base_wr-1:>+5.0%}  avg={row['avg']:.1f}%")

# ── H5: TECH + FUND BOTH PRESENT ─────────────────────────────────────────────
print(f"\n{'='*65}")
print(f"H5: Tech AND Fund signals both in window")
print(f"{'='*65}")
for has_t in [False, True]:
    for has_f in [False, True]:
        sub = enriched[(enriched["has_tech"]==has_t) & (enriched["has_fund"]==has_f)]
        if len(sub) < 20: continue
        wr = sub["is_good"].mean()
        label = f"Tech={'Y' if has_t else 'N'} Fund={'Y' if has_f else 'N'}"
        print(f"  {label}  n={len(sub):>6}  WR={wr:.1%}  lift={wr/base_wr-1:>+5.0%}  "
              f"avg={sub['Sell_profit'].mean():.1f}%")

# ── YEAR-BY-YEAR STABILITY ────────────────────────────────────────────────────
print(f"\n{'='*65}")
print(f"Year x n_filters cross-tab (WR)")
print(f"{'='*65}")
yr = enriched.groupby(["year","n_filters"]).agg(
    n=("is_good","count"), wr=("is_good","mean")).reset_index()
pivot = yr.pivot(index="year", columns="n_filters", values="wr")
pivot.columns = [f"{c}f" for c in pivot.columns]
print(pivot.round(3).to_string())

# ── CONVERGENCE SCORE ─────────────────────────────────────────────────────────
print(f"\n{'='*65}")
print(f"CONVERGENCE SCORE  (practical entry gate)")
print(f"{'='*65}")
enriched["conv_score"] = (
    (enriched["n_filters"] - 1).clip(0, 4) +
    (enriched["has_tech"] & enriched["has_fund"]).astype(int) +
    (enriched["days_span"] <= 7).astype(int) +
    (enriched["n_filters"] >= 4).astype(int)
)

print(f"\n{'Score':>7} {'N':>7} {'WR':>8} {'Lift':>7} {'AvgProfit':>10} {'MedProfit':>10}")
print("-"*58)
conv_by_score = []
for s in sorted(enriched["conv_score"].unique()):
    sub = enriched[enriched["conv_score"] == s]
    if len(sub) < 20: continue
    wr  = sub["is_good"].mean()
    avg = sub["Sell_profit"].mean()
    med = sub["Sell_profit"].median()
    lift= wr / base_wr - 1
    conv_by_score.append({"score":s,"n":len(sub),"wr":wr,"avg":avg,"med":med,"lift":lift})
    print(f"  {s:>5}   {len(sub):>7}  {wr:>7.1%}  {lift:>+6.0%}  {avg:>9.1f}%  {med:>9.1f}%")

# 2025 only
te = enriched[enriched["year"] >= 2025]
base_te = te["is_good"].mean()
print(f"\n  2025+ (baseline WR={base_te:.1%}):")
for s in sorted(te["conv_score"].unique()):
    sub = te[te["conv_score"] == s]
    if len(sub) < 10: continue
    wr = sub["is_good"].mean()
    print(f"    Score {s}  n={len(sub):>4}  WR={wr:.1%}  "
          f"lift={wr/base_te-1:>+5.0%}  avg={sub['Sell_profit'].mean():.1f}%")

# ── HOLD POSITIONS WITH CONVERGENCE ──────────────────────────────────────────
print(f"\n{'='*65}")
print(f"Current HOLD positions — Convergence Score")
print(f"{'='*65}")

hold_results = []
hold_tickers = hold["ticker"].unique()
for ticker in hold_tickers:
    c = hold[hold["ticker"] == ticker][["time","filter"]].copy()
    h = all_hits[all_hits["ticker"] == ticker][["time","filter","ftype"]].copy()
    h = h.rename(columns={"time":"hit_time","filter":"hit_filter","ftype":"hit_ftype"})
    if c.empty or h.empty: continue
    c["_k"] = 1; h["_k"] = 1
    cross = c.merge(h, on="_k").drop("_k", axis=1)
    cross = cross[
        (cross["hit_time"] >= cross["time"] - WINDOW_TD) &
        (cross["hit_time"] <= cross["time"])
    ]
    if cross.empty: continue
    agg = cross.groupby(["time","filter"]).agg(
        n_filters   = ("hit_filter","nunique"),
        filters_set = ("hit_filter", lambda x: "|".join(sorted(set(x)))),
        has_tech    = ("hit_ftype",  lambda x: "Tech" in set(x)),
        has_fund    = ("hit_ftype",  lambda x: "Fund" in set(x)),
        min_ht      = ("hit_time",   "min"),
        max_ht      = ("hit_time",   "max"),
    ).reset_index()
    agg["days_span"] = (agg["max_ht"] - agg["min_ht"]).dt.days
    agg["ticker"]    = ticker
    agg["conv_score"]= (
        (agg["n_filters"]-1).clip(0,4) +
        (agg["has_tech"] & agg["has_fund"]).astype(int) +
        (agg["days_span"] <= 7).astype(int) +
        (agg["n_filters"] >= 4).astype(int)
    )
    hold_results.append(agg[["ticker","time","filter","n_filters",
                              "filters_set","days_span","conv_score"]])

if hold_results:
    hold_enr = pd.concat(hold_results, ignore_index=True)
    # Latest signal per ticker
    hold_best = (hold_enr.sort_values(["ticker","conv_score","time"],
                                       ascending=[True,False,False])
                 .drop_duplicates("ticker", keep="first")
                 .sort_values("conv_score", ascending=False))
    print(f"\nTop 30 HOLD by Convergence Score:")
    print(hold_best[["ticker","conv_score","n_filters","filters_set","days_span","filter"]].head(30).to_string(index=False))
    print(f"\n  Conv >= 4: {(hold_best['conv_score']>=4).sum()} tickers")
    print(f"  Conv >= 3: {(hold_best['conv_score']>=3).sum()} tickers")
    print(f"  Conv >= 2: {(hold_best['conv_score']>=2).sum()} tickers")
    hold_best.to_csv("data/hold_convergence_scored.csv", index=False)
    print(f"  Saved: hold_convergence_scored.csv")
else:
    hold_enr  = pd.DataFrame()
    hold_best = pd.DataFrame()

# ── CHARTS ───────────────────────────────────────────────────────────────────
print(f"\nGenerating charts ...")
fig = plt.figure(figsize=(24, 18), facecolor=DARK_BG)
gs  = gridspec.GridSpec(3, 4, figure=fig, hspace=0.50, wspace=0.40)

# P1: WR by n_filters
ax1 = fig.add_subplot(gs[0, :2])
if not nd.empty:
    col1 = [GREEN if r["lift"]>0.15 else (YELLOW if r["lift"]>0 else RED)
            for _, r in nd.iterrows()]
    bars1 = ax1.bar(nd["n_filters"], nd["wr"]*100, color=col1, alpha=0.85, width=0.7)
    ax1.axhline(base_wr*100, color=RED, lw=1.5, ls="--", label=f"Baseline {base_wr:.1%}")
    ax1.set_xticks(nd["n_filters"])
    for bar, (_, r) in zip(bars1, nd.iterrows()):
        ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,
                 f"{r['wr']:.0%}\n(n={int(r['count'])})",
                 ha="center", fontsize=8.5, color=TEXT_CLR, fontweight="bold")
ax1.set_xlabel("# Unique Filters Converging (30-day window)")
ax1.set_ylabel("Win Rate (>10% profit)")
ax1.set_title(f"H1: More Filter Convergence = Higher Win Rate\n({len(enriched):,} deals, 30-day window)",
              color=TEXT_CLR, fontweight="bold")
ax1.legend(fontsize=9); ax1.set_ylim(0, 90)

# P2: Sequence pattern
ax2 = fig.add_subplot(gs[0, 2])
if not seq_stats.empty:
    sp = seq_stats.reset_index().sort_values("wr")
    sc2 = [GREEN if r["wr"]>base_wr*1.1 else (YELLOW if r["wr"]>base_wr else RED)
           for _, r in sp.iterrows()]
    ax2.barh(range(len(sp)), sp["wr"]*100, color=sc2, alpha=0.85)
    ax2.axvline(base_wr*100, color=RED, lw=1.5, ls="--")
    ax2.set_yticks(range(len(sp)))
    ax2.set_yticklabels([f"{r['seq_key']}\n(n={int(r['n'])})"
                         for _, r in sp.iterrows()], fontsize=8)
    ax2.set_xlabel("Win Rate (%)")
ax2.set_title("H2: Sequence Pattern\n(first type -> current type)",
              color=TEXT_CLR, fontweight="bold")

# P3: Time span
ax3 = fig.add_subplot(gs[0, 3])
if not span_stats.empty:
    sp2 = span_stats.reset_index()
    sc3 = [GREEN if r["wr"]>base_wr*1.1 else (YELLOW if r["wr"]>base_wr else RED)
           for _, r in sp2.iterrows()]
    ax3.bar(range(len(sp2)), sp2["wr"]*100, color=sc3, alpha=0.85, width=0.7)
    ax3.axhline(base_wr*100, color=RED, lw=1.5, ls="--")
    ax3.set_xticks(range(len(sp2)))
    ax3.set_xticklabels(sp2["span_bin"].astype(str), fontsize=8, rotation=20)
    ax3.set_ylabel("Win Rate (%)")
    for i, (_, r) in enumerate(sp2.iterrows()):
        ax3.text(i, r["wr"]*100+0.5, f"{r['wr']:.0%}", ha="center",
                 fontsize=8, color=TEXT_CLR)
ax3.set_title("H3: Days Between First/Last Filter\n(shorter = fresher signal)",
              color=TEXT_CLR, fontweight="bold")

# P4: Convergence score
ax4 = fig.add_subplot(gs[1, :2])
csd = pd.DataFrame(conv_by_score)
if not csd.empty:
    col4 = [GREEN if r["lift"]>0.2 else (YELLOW if r["lift"]>0 else RED)
            for _, r in csd.iterrows()]
    bars4 = ax4.bar(csd["score"], csd["wr"]*100, color=col4, alpha=0.85)
    ax4.axhline(base_wr*100, color=RED, lw=1.5, ls="--", label=f"Baseline {base_wr:.1%}")
    ax4.set_xticks(csd["score"])
    for bar, (_, r) in zip(bars4, csd.iterrows()):
        ax4.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,
                 f"{r['wr']:.0%}\n(n={int(r['n'])})",
                 ha="center", fontsize=8, color=TEXT_CLR)
ax4.set_xlabel("Convergence Score (0=single filter, 6=max convergence)")
ax4.set_ylabel("Win Rate (%)")
ax4.set_title("Convergence Score vs Win Rate\n(+1 per extra filter, +1 tech+fund, +1 fresh, +1 if 4+ filters)",
              color=TEXT_CLR, fontweight="bold")
ax4.legend(fontsize=9); ax4.set_ylim(0, 95)

# P5: Year stability
ax5 = fig.add_subplot(gs[1, 2:])
cmap_yr = {1:RED, 2:YELLOW, 3:BLUE, 4:GREEN, 5:ORANGE}
for nf, grp in yr.groupby("n_filters"):
    if nf > 5: continue
    g2 = grp[grp["n"] >= 15]
    lw = 2.5 if nf >= 3 else 1.5
    ax5.plot(g2["year"], g2["wr"]*100, "o-", lw=lw,
             color=cmap_yr.get(nf, PURPLE), label=f"{nf} filter(s)")
ax5.axhline(base_wr*100, color=RED, lw=1.0, ls=":", alpha=0.7)
ax5.set_xlabel("Year"); ax5.set_ylabel("Win Rate (%)")
ax5.set_title("Multi-filter Stability by Year\n(convergence signal robust over time?)",
              color=TEXT_CLR, fontweight="bold")
ax5.legend(fontsize=9)

# P6: Top combos
ax6 = fig.add_subplot(gs[2, :2])
if not combo_stats.empty:
    tc = combo_stats.head(20).reset_index()
    sc6 = [GREEN if r["wr"]>base_wr*1.15 else (YELLOW if r["wr"]>base_wr else RED)
           for _, r in tc.iterrows()]
    ax6.barh(range(len(tc)), tc["wr"]*100, color=sc6, alpha=0.85)
    ax6.axvline(base_wr*100, color=RED, lw=1.5, ls="--")
    ax6.set_yticks(range(len(tc)))
    ax6.set_yticklabels([f"{r['filters_set'][:42]}\n(n={int(r['n'])})"
                          for _, r in tc.iterrows()], fontsize=7)
    for i, (_, r) in enumerate(tc.iterrows()):
        ax6.text(r["wr"]*100+0.3, i, f"{r['wr']:.0%}", va="center",
                 fontsize=7.5, color=TEXT_CLR)
    ax6.set_xlabel("Win Rate (%)")
ax6.set_title("Top 20 Filter Combos (n>=50)\nsorted by Win Rate",
              color=TEXT_CLR, fontweight="bold")

# P7: Tech + Fund presence
ax7 = fig.add_subplot(gs[2, 2])
labels7 = ["Tech only","Fund only","Both T+F","Sup only"]
wr7 = []
n7  = []
for ht, hf in [(True,False),(False,True),(True,True),(False,False)]:
    sub = enriched[(enriched["has_tech"]==ht)&(enriched["has_fund"]==hf)]
    wr7.append(sub["is_good"].mean()*100 if len(sub)>20 else 0)
    n7.append(len(sub))
col7 = [GREEN if w>base_wr*100*1.1 else (YELLOW if w>base_wr*100 else RED) for w in wr7]
bars7 = ax7.bar(range(4), wr7, color=col7, alpha=0.85)
ax7.axhline(base_wr*100, color=RED, lw=1.5, ls="--")
ax7.set_xticks(range(4)); ax7.set_xticklabels(labels7, fontsize=9, rotation=15)
ax7.set_ylabel("Win Rate (%)"); ax7.set_ylim(0, 85)
for bar, w, n in zip(bars7, wr7, n7):
    ax7.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,
             f"{w:.0f}%\n(n={n})", ha="center", fontsize=8.5, color=TEXT_CLR)
ax7.set_title("H5: Tech + Fund Both\nPresent in Window?",
              color=TEXT_CLR, fontweight="bold")

# P8: HOLD top picks by convergence
ax8 = fig.add_subplot(gs[2, 3])
if not hold_best.empty:
    top_h = hold_best.head(20).reset_index(drop=True)
    col8  = [GREEN if s>=4 else (BLUE if s>=3 else (YELLOW if s>=2 else RED))
             for s in top_h["conv_score"]]
    ax8.barh(range(len(top_h)), top_h["conv_score"], color=col8, alpha=0.85)
    ax8.set_yticks(range(len(top_h)))
    ax8.set_yticklabels([f"{r['ticker']}\n{r['n_filters']}f/{r['days_span']:.0f}d"
                         for _, r in top_h.iterrows()], fontsize=8)
    ax8.axvline(3, color=YELLOW, lw=1.2, ls="--")
    ax8.axvline(4, color=GREEN,  lw=1.2, ls="--")
    ax8.set_xlabel("Convergence Score")
ax8.set_title("Top HOLD Positions\nby Convergence Score",
              color=TEXT_CLR, fontweight="bold")

fig.suptitle(
    f"Multi-Filter Convergence Analysis  |  {len(enriched):,} deals  |  "
    f"14 filters  |  30-day window  |  Baseline WR={base_wr:.1%}",
    color=TEXT_CLR, fontsize=13, fontweight="bold", y=0.997)
plt.savefig("analyze_filter_sequence.png", dpi=150, bbox_inches="tight", facecolor=DARK_BG)
print("Chart saved: analyze_filter_sequence.png")

# ── FINAL SUMMARY ─────────────────────────────────────────────────────────────
print(f"\n{'='*70}")
print("KEY FINDINGS — Multi-Filter Convergence")
print(f"{'='*70}")
enriched.to_csv("data/enriched_with_convergence.csv", index=False)
print(f"\nSaved: enriched_with_convergence.csv  |  hold_convergence_scored.csv")
print("\nDone.")
