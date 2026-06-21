#!/usr/bin/env python3
"""
rank_profile_hits.py
====================
Cross-reference profile_hit.csv deals with 7-axis fundamental rating to evaluate
whether the v4 workflow improves deal selection.

Workflow tested:
  Step 1: User's system scans potential deals (profile_hit.csv)
  Step 2: Rank deals by v4 fundamental tier/score
  Step 3: Evaluate: do A-tier deals outperform C/D/E-tier deals?

Metrics:
  - Median Sell_profit (realized)
  - Median P3M (forward 3-month unrealized return)
  - Win rate (>0%)
  - Beat VNINDEX rate (using profit_3M from rating, proxy)
  - Coverage (% of deals that have a rating match)
"""
import warnings; warnings.filterwarnings("ignore")
import pandas as pd, numpy as np
from datetime import timedelta

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
MAX_RATING_AGE = 400   # days — same as live_picks_2026.py
MIN_DEAL_DATE  = "2015-01-01"

# ─── Load data ───────────────────────────────────────────────────────────────
print("Loading profile_hit.csv ...")
hits = pd.read_csv(f"{WORKDIR}/data/profile_hit.csv", parse_dates=["time"])
hits = hits[hits["time"] >= MIN_DEAL_DATE].copy()
print(f"  {len(hits):,} deals from {MIN_DEAL_DATE} onward")
print(f"  {hits['ticker'].nunique()} unique tickers | {hits['filter'].nunique()} strategies")

print("Loading fundamental_rating_all.csv ...")
rat = pd.read_csv(f"{WORKDIR}/data/fundamental_rating_all.csv", parse_dates=["time"])
rat = rat.sort_values(["ticker", "time"]).reset_index(drop=True)
print(f"  {len(rat):,} (ticker, quarter) ratings | {rat['ticker'].nunique()} tickers")
print(f"  Quarters: {rat['quarter'].nunique()} | Date range: {rat['time'].min().date()} -> {rat['time'].max().date()}")

# ─── Match each deal to most recent rating (at-or-before deal date, within MAX_RATING_AGE) ─
print("\nMatching deals to fundamental ratings ...")
rat_indexed = rat.set_index(["ticker", "time"])

KEEP_RATING = ["tier", "total_score", "score_pct",
               "score_quality", "score_stability", "score_cash",
               "score_shareholder", "score_growth", "score_health", "score_valuation",
               "NP_R", "NP_CV", "Rev_CV", "LT_CAGR", "DY", "quarter"]

def find_rating(ticker, deal_date):
    """Return most recent rating row for ticker at-or-before deal_date within MAX_RATING_AGE."""
    sub = rat[(rat["ticker"] == ticker) & (rat["time"] <= deal_date)]
    if sub.empty:
        return None
    row = sub.iloc[-1]  # already sorted by time
    age = (deal_date - row["time"]).days
    if age > MAX_RATING_AGE:
        return None
    return row

# Build match table
records = []
tickers_in_rating = set(rat["ticker"].unique())
for _, deal in hits.iterrows():
    tk = deal["ticker"]
    dt = deal["time"]
    rec = {"deal_idx": deal.name}
    if tk not in tickers_in_rating:
        rec["tier"] = "NO_RATING"
    else:
        row = find_rating(tk, dt)
        if row is None:
            rec["tier"] = "NO_RATING"
        else:
            for c in KEEP_RATING:
                rec[c] = row[c]
    records.append(rec)

matched = pd.DataFrame(records).set_index("deal_idx")
hits = hits.join(matched, how="left")

# Fill missing tier
hits["tier"] = hits["tier"].fillna("NO_RATING")
covered = (hits["tier"] != "NO_RATING").mean() * 100
print(f"  Coverage: {covered:.1f}% of deals matched to a fundamental rating")
print(f"  Tier distribution:\n{hits['tier'].value_counts().sort_index().to_string()}")

# ─── Core metric function ─────────────────────────────────────────────────────
def summarize(group, name=""):
    sp = group["Sell_profit"].dropna()
    p3m = group["P3M"].dropna()
    n = len(group)
    return {
        "N_deals":       n,
        "N_sell":        len(sp),
        "MedSellProfit": sp.median() if len(sp) else np.nan,
        "MeanSellProfit": sp.mean() if len(sp) else np.nan,
        "WinRate":       (sp > 0).mean() * 100 if len(sp) else np.nan,
        "N_P3M":         len(p3m),
        "MedP3M":        p3m.median() if len(p3m) else np.nan,
        "MeanP3M":       p3m.mean() if len(p3m) else np.nan,
        "P3M_WinRate":   (p3m > 0).mean() * 100 if len(p3m) else np.nan,
    }

# ─── Analysis 1: Returns by fundamental tier ─────────────────────────────────
print("\n" + "="*80)
print("=== ANALYSIS 1: Deal performance by fundamental tier ===")
print("="*80)
tiers_all = ["A", "B", "C", "D", "E", "NO_RATING"]
rows = []
for t in tiers_all:
    g = hits[hits["tier"] == t]
    s = summarize(g, t)
    s["tier"] = t
    rows.append(s)
tier_df = pd.DataFrame(rows).set_index("tier")
print(f"\n{'Tier':<12}{'N':>7}{'MedSell%':>10}{'MeanSell%':>11}{'WinRate':>9}"
      f"{'N_P3M':>7}{'MedP3M%':>9}{'MeanP3M%':>10}{'P3MWin%':>9}")
print("-"*84)
for t in tiers_all:
    r = tier_df.loc[t]
    print(f"{t:<12}{r['N_deals']:>7,}{r['MedSellProfit']:>10.1f}{r['MeanSellProfit']:>11.1f}"
          f"{r['WinRate']:>9.1f}{r['N_P3M']:>7,}{r['MedP3M']:>9.1f}{r['MeanP3M']:>10.1f}"
          f"{r['P3M_WinRate']:>9.1f}")

# ─── Analysis 2: A+B vs C+D+E (active filter) ────────────────────────────────
print("\n" + "="*80)
print("=== ANALYSIS 2: A+B (quality) vs C+D+E (low quality) ===")
print("="*80)
ab  = hits[hits["tier"].isin(["A", "B"])]
cde = hits[hits["tier"].isin(["C", "D", "E"])]
nr  = hits[hits["tier"] == "NO_RATING"]

for grp, label in [(ab, "A+B (top quality)"), (cde, "C+D+E (mid-low)"), (nr, "NO_RATING")]:
    s = summarize(grp)
    sp_med = s["MedSellProfit"]; sp_win = s["WinRate"]
    p3_med = s["MedP3M"]; p3_win = s["P3M_WinRate"]
    print(f"\n  {label} (N={s['N_deals']:,})")
    print(f"    Realized Sell: median={sp_med:.1f}%, win={sp_win:.1f}%")
    print(f"    Forward P3M:   median={p3_med:.1f}%, win={p3_win:.1f}%")

# ─── Analysis 3: Break down by strategy x tier ───────────────────────────────
print("\n" + "="*80)
print("=== ANALYSIS 3: Performance by strategy x tier (top strategies) ===")
print("="*80)
top_filters = hits["filter"].value_counts().head(8).index.tolist()
print(f"\n{'Strategy':<20}{'Tier':<6}{'N':>6}{'MedSell%':>10}{'WinRate':>9}{'MedP3M%':>9}")
print("-"*62)
for flt in top_filters:
    fg = hits[hits["filter"] == flt]
    for t in ["A", "B", "C", "D", "E"]:
        g = fg[fg["tier"] == t]
        if len(g) < 10:
            continue
        sp = g["Sell_profit"].dropna()
        p3 = g["P3M"].dropna()
        med_sell = sp.median() if len(sp) else np.nan
        win      = (sp > 0).mean()*100 if len(sp) else np.nan
        med_p3   = p3.median() if len(p3) else np.nan
        print(f"{flt:<20}{t:<6}{len(g):>6,}{med_sell:>10.1f}{win:>9.1f}{med_p3:>9.1f}")
    print()

# ─── Analysis 4: Total_score quintile analysis ───────────────────────────────
print("="*80)
print("=== ANALYSIS 4: Deal returns by total_score quintile (finer granularity) ===")
print("="*80)
rated = hits[hits["tier"] != "NO_RATING"].copy()
rated["score_q"] = pd.qcut(rated["total_score"], 5,
                            labels=["Q1(low)", "Q2", "Q3", "Q4", "Q5(high)"])
print(f"\n{'ScoreQ':<12}{'N':>7}{'MedSell%':>10}{'WinRate%':>10}{'MedP3M%':>9}")
print("-"*50)
for q in ["Q1(low)", "Q2", "Q3", "Q4", "Q5(high)"]:
    g = rated[rated["score_q"] == q]
    sp = g["Sell_profit"].dropna()
    p3 = g["P3M"].dropna()
    print(f"{q:<12}{len(g):>7,}{sp.median():>10.1f}{(sp>0).mean()*100:>10.1f}{p3.median():>9.1f}")

# ─── Analysis 5: Year-by-year A+B vs C+D+E (P3M) ────────────────────────────
print("\n" + "="*80)
print("=== ANALYSIS 5: Year-by-year A+B alpha over C+D+E (P3M median) ===")
print("="*80)
hits["year"] = hits["time"].dt.year
print(f"\n{'Year':<6}{'AB_P3M':>10}{'AB_N':>7}{'CDE_P3M':>10}{'CDE_N':>7}{'Alpha':>8}")
print("-"*50)
for yr in sorted(hits["year"].unique()):
    yr_df = hits[hits["year"] == yr]
    ab_g  = yr_df[yr_df["tier"].isin(["A","B"])]["P3M"].dropna()
    cde_g = yr_df[yr_df["tier"].isin(["C","D","E"])]["P3M"].dropna()
    if len(ab_g) < 5 or len(cde_g) < 5:
        continue
    alpha = ab_g.median() - cde_g.median()
    print(f"{yr:<6}{ab_g.median():>10.1f}{len(ab_g):>7}{cde_g.median():>10.1f}{len(cde_g):>7}{alpha:>+8.1f}")

# ─── Analysis 6: Current live deals (recent 60 days) by tier ─────────────────
print("\n" + "="*80)
print("=== ANALYSIS 6: Recent deals (last 60 days) ranked by fundamental score ===")
print("="*80)
TODAY = pd.Timestamp("2026-05-09")
recent = hits[(hits["time"] >= TODAY - pd.Timedelta(days=60))].copy()
recent = recent[recent["tier"].isin(["A","B","C","D","E"])].copy()
recent = recent.sort_values(["total_score"], ascending=False)
recent_top = recent.drop_duplicates("ticker").head(30)
print(f"\nTop 30 unique tickers from recent deals, sorted by fundamental score:")
print(f"{'Tkr':<7}{'Filter':<22}{'Date':<12}{'Tier':<5}{'Score':>7}"
      f"{'Q':>5}{'St':>5}{'Cs':>5}{'Sh':>5}{'Gr':>5}{'H':>5}{'V':>5}"
      f"{'NP_R%':>7}{'P3M%':>7}")
print("-"*105)
for _, r in recent_top.iterrows():
    np_r_pct = r.get("NP_R", float("nan")) * 100
    p3m = r.get("P3M", float("nan"))
    p3m_s = f"{p3m:>7.1f}" if pd.notna(p3m) else "   N/A"
    print(f"{r['ticker']:<7}{r['filter']:<22}{str(r['time'].date()):<12}"
          f"{r['tier']:<5}{r['total_score']:>7.3f}"
          f"{r['score_quality']:>5.2f}{r['score_stability']:>5.2f}"
          f"{r['score_cash']:>5.2f}{r['score_shareholder']:>5.2f}"
          f"{r['score_growth']:>5.2f}{r['score_health']:>5.2f}"
          f"{r['score_valuation']:>5.2f}"
          f"{np_r_pct:>7.0f}{p3m_s}")

# ─── Summary verdict ──────────────────────────────────────────────────────────
print("\n" + "="*80)
print("=== VERDICT: Workflow effectiveness ===")
print("="*80)
ab_sell  = hits[hits["tier"].isin(["A","B"])]["Sell_profit"].median()
cde_sell = hits[hits["tier"].isin(["C","D","E"])]["Sell_profit"].median()
ab_p3m   = hits[hits["tier"].isin(["A","B"])]["P3M"].median()
cde_p3m  = hits[hits["tier"].isin(["C","D","E"])]["P3M"].median()
ab_win   = (hits[hits["tier"].isin(["A","B"])]["Sell_profit"] > 0).mean() * 100
cde_win  = (hits[hits["tier"].isin(["C","D","E"])]["Sell_profit"] > 0).mean() * 100

print(f"""
  Realized sell profit:  A+B = {ab_sell:.1f}%  vs  C+D+E = {cde_sell:.1f}%  (alpha {ab_sell-cde_sell:+.1f}pp)
  Forward P3M:           A+B = {ab_p3m:.1f}%   vs  C+D+E = {cde_p3m:.1f}%   (alpha {ab_p3m-cde_p3m:+.1f}pp)
  Win rate:              A+B = {ab_win:.1f}%   vs  C+D+E = {cde_win:.1f}%

  Coverage: {covered:.0f}% of deals had a matching fundamental rating

  Workflow verdict:
""")

if ab_p3m > cde_p3m + 2 and ab_win > cde_win + 3:
    print("  EFFECTIVE - Fundamental filter adds clear alpha. Recommend using tier A+B as a")
    print("  mandatory pre-screen before entering any deal from the scanning system.")
elif ab_p3m > cde_p3m:
    print("  MODERATELY EFFECTIVE - A+B outperforms C+D+E but margin is modest.")
    print("  Fundamental filter helps but is not the dominant factor in deal selection.")
    print("  Consider using score as a tiebreaker rather than a hard filter.")
else:
    print("  WEAK - Fundamental tier does not strongly predict deal profitability in this dataset.")
    print("  Possible reasons: strategy signals are already quality-filtered, or holding period")
    print("  mismatch (short-term technical deals may not depend on 8-quarter fundamentals).")

print(f"\nOutput: rank_profile_hits_results.csv")
recent_top.to_csv(f"{WORKDIR}/data/rank_profile_hits_results.csv", index=False)
