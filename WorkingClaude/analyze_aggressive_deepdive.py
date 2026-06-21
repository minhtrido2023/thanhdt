"""Deep-dive analysis of AGGRESSIVE 7p 45d -15% strategy.

Analyzes:
  - Top winners & losers
  - Hold-time distribution
  - Tier mix of trades
  - Sector breakdown
  - Drawdown periods (start/end/recovery)
  - Monthly returns distribution
  - Win/lose streaks
  - 2022 detailed trade log
"""
import os
import sys
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import (
    simulate, metrics, bq, SIGNAL_QUERY, VNI_QUERY,
    START_DATE, END_DATE, INIT_NAV
)

print("Loading data...")
sig = bq(SIGNAL_QUERY.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())
prices = {}
for tk, g in sig.groupby("ticker"):
    prices[tk] = dict(zip(g["time"], g["Close"]))

# Run AGGRESSIVE 7p 45d -15%
TIERS_AGG = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "MOMENTUM_A",
             "MOMENTUM_S_N", "DEEP_VALUE_RECOVERY"]

print("Running AGGRESSIVE 7p 45d -15% simulation...")
nav_df, trades_df = simulate(
    sig, prices, vni_dates,
    allowed_tiers=TIERS_AGG,
    max_positions=7,
    hold_days=45,
    stop_loss=-0.15,
    min_hold=2,
)

# Add tier info to trades
sig_lookup = sig.set_index(["ticker", "time"])[["play_type", "ta"]].to_dict("index")

def get_play_type(row):
    # Find the signal date (entry_date - 1 trading day) — but we queued at signal day
    # The signal was at entry_date - 1 trading day. Use the closest preceding signal day for that ticker.
    tk = row["ticker"]
    entry_date = pd.Timestamp(row["entry_date"])
    # Get all sigs for this ticker
    tk_sigs = sig[sig["ticker"] == tk].sort_values("time")
    # Last signal before or equal to entry_date - 0 (signal triggered on day before entry)
    prior = tk_sigs[tk_sigs["time"] < entry_date]
    if len(prior) == 0:
        return "?"
    # Most recent signal that triggered the entry
    return prior.iloc[-1]["play_type"]

print("Tagging trades with play_type...")
trades_df["entry_date"] = pd.to_datetime(trades_df["entry_date"])
trades_df["exit_date"] = pd.to_datetime(trades_df["exit_date"])
trades_df["play_type"] = trades_df.apply(get_play_type, axis=1)
trades_df["yr"] = trades_df["entry_date"].dt.year
trades_df["entry_mo"] = trades_df["entry_date"].dt.to_period("M")

# Sector lookup (for top tickers)
print("Computing sector lookup...")
sec_query = """
SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code / 1000) AS INT64) AS sector_top
FROM tav2_bq.ticker AS t
WHERE t.ICB_Code IS NOT NULL AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
"""
sec_df = bq(sec_query)
sec_map = sec_df.set_index("ticker")["sector_top"].to_dict()
trades_df["sector_top"] = trades_df["ticker"].map(sec_map).fillna(-1).astype(int)

m = metrics(nav_df, trades_df, "AGGRESSIVE_7p_45d_15sl")
print(f"\n  Strategy: CAGR={m['cagr_pct']:.1f}%, Sharpe={m['sharpe']:.2f}, "
      f"MaxDD={m['max_dd_pct']:.1f}%")
print(f"  Total trades: {m['n_trades']}")

# ────────────────────────────────────────────────────────────────────────
# 1. Top winners & losers
# ────────────────────────────────────────────────────────────────────────
print("\n" + "═" * 90)
print("  TOP 10 WINNERS")
print("═" * 90)
top_w = trades_df.nlargest(10, "ret_net")
print(top_w[["ticker", "entry_date", "exit_date", "entry_price", "exit_price",
              "ret_net", "days_held", "reason", "play_type", "sector_top"]].to_string(
    index=False, formatters={"ret_net": "{:+.1%}".format,
                             "entry_price": "{:,.0f}".format,
                             "exit_price": "{:,.0f}".format}))

print("\n" + "═" * 90)
print("  TOP 10 LOSERS")
print("═" * 90)
top_l = trades_df.nsmallest(10, "ret_net")
print(top_l[["ticker", "entry_date", "exit_date", "entry_price", "exit_price",
              "ret_net", "days_held", "reason", "play_type", "sector_top"]].to_string(
    index=False, formatters={"ret_net": "{:+.1%}".format,
                             "entry_price": "{:,.0f}".format,
                             "exit_price": "{:,.0f}".format}))

# ────────────────────────────────────────────────────────────────────────
# 2. Tier mix breakdown
# ────────────────────────────────────────────────────────────────────────
print("\n" + "═" * 90)
print("  TIER MIX OF TRADES (AGGRESSIVE_7p_45d_15sl)")
print("═" * 90)
tier_stats = trades_df.groupby("play_type").agg(
    n=("ret_net", "count"),
    avg_ret=("ret_net", "mean"),
    median_ret=("ret_net", "median"),
    win=("ret_net", lambda x: (x > 0).mean() * 100),
    avg_hold=("days_held", "mean"),
).sort_values("avg_ret", ascending=False)
tier_stats["pct_of_trades"] = tier_stats["n"] / len(trades_df) * 100
tier_stats["contribution"] = tier_stats["n"] * tier_stats["avg_ret"]
print(tier_stats.to_string(float_format=lambda x: f"{x:.2f}"))

# ────────────────────────────────────────────────────────────────────────
# 3. Sector breakdown
# ────────────────────────────────────────────────────────────────────────
sec_names = {0: "Misc/Oil&Gas", 1: "Materials", 2: "Industrials",
             3: "Cons Goods", 4: "Health", 5: "Cons Services",
             7: "Utilities", 8: "Financials/RE", 9: "Tech/Telecom"}
print("\n" + "═" * 90)
print("  SECTOR BREAKDOWN")
print("═" * 90)
sec_stats = trades_df.groupby("sector_top").agg(
    n=("ret_net", "count"),
    avg_ret=("ret_net", "mean"),
    win=("ret_net", lambda x: (x > 0).mean() * 100),
).sort_values("avg_ret", ascending=False)
sec_stats["sector"] = sec_stats.index.map(lambda x: sec_names.get(x, str(x)))
print(sec_stats.to_string(float_format=lambda x: f"{x:.2f}"))

# ────────────────────────────────────────────────────────────────────────
# 4. Drawdown analysis
# ────────────────────────────────────────────────────────────────────────
print("\n" + "═" * 90)
print("  TOP 5 DRAWDOWN PERIODS")
print("═" * 90)
nav = nav_df["nav"].values
times = pd.to_datetime(nav_df["time"])
peak = np.maximum.accumulate(nav)
dd = (nav - peak) / peak

# Find drawdown periods
in_dd = dd < -0.05  # more than 5% drawdown
dd_periods = []
i = 0
while i < len(dd):
    if dd[i] < -0.05:
        start = i
        # Find peak before this DD
        peak_before_idx = i
        while peak_before_idx > 0 and nav[peak_before_idx - 1] >= nav[start]:
            peak_before_idx -= 1
        # Find end (return to peak)
        end = i
        peak_val = peak[i]
        while end < len(dd) and nav[end] < peak_val:
            end += 1
        max_dd_in_period = dd[start:min(end+1, len(dd))].min()
        max_dd_idx = start + np.argmin(dd[start:min(end+1, len(dd))])
        recovery_days = end - start
        dd_periods.append({
            "peak_date": times.iloc[peak_before_idx].date(),
            "trough_date": times.iloc[max_dd_idx].date(),
            "recovery_date": times.iloc[end].date() if end < len(times) else "ongoing",
            "max_dd_pct": max_dd_in_period * 100,
            "trough_to_peak_days": max_dd_idx - peak_before_idx,
            "recovery_days": end - max_dd_idx if end < len(times) else None,
            "total_days": end - peak_before_idx if end < len(times) else None,
        })
        i = end + 1
    else:
        i += 1

dd_periods_df = pd.DataFrame(dd_periods).sort_values("max_dd_pct").head(5)
print(dd_periods_df.to_string(index=False))

# ────────────────────────────────────────────────────────────────────────
# 5. Monthly return distribution
# ────────────────────────────────────────────────────────────────────────
print("\n" + "═" * 90)
print("  MONTHLY RETURN DISTRIBUTION")
print("═" * 90)
nav_df2 = nav_df.copy()
nav_df2["time"] = pd.to_datetime(nav_df2["time"])
nav_df2 = nav_df2.set_index("time")
monthly_nav = nav_df2["nav"].resample("ME").last()
monthly_ret = monthly_nav.pct_change().dropna() * 100

print(f"  N months: {len(monthly_ret)}")
print(f"  Mean: {monthly_ret.mean():.2f}%, Median: {monthly_ret.median():.2f}%, Std: {monthly_ret.std():.2f}%")
print(f"  Best month: {monthly_ret.max():.2f}% ({monthly_ret.idxmax().date()})")
print(f"  Worst month: {monthly_ret.min():.2f}% ({monthly_ret.idxmin().date()})")
print(f"  % positive months: {(monthly_ret > 0).mean()*100:.1f}%")
print(f"  % months > 5%: {(monthly_ret > 5).mean()*100:.1f}%")
print(f"  % months < -5%: {(monthly_ret < -5).mean()*100:.1f}%")

# Distribution percentiles
print("\n  Percentiles:")
for p in [1, 5, 10, 25, 50, 75, 90, 95, 99]:
    print(f"    P{p:3d}: {monthly_ret.quantile(p/100):>+7.2f}%")

# ────────────────────────────────────────────────────────────────────────
# 6. 2022 detailed
# ────────────────────────────────────────────────────────────────────────
print("\n" + "═" * 90)
print("  2022 TRADE LOG (year of -15.4% drawdown)")
print("═" * 90)
trades_2022 = trades_df[trades_df["yr"] == 2022].sort_values("entry_date")
print(f"  Total 2022 entries: {len(trades_2022)}")
if len(trades_2022):
    print(f"  Avg ret: {trades_2022['ret_net'].mean()*100:+.2f}%")
    print(f"  Win rate: {(trades_2022['ret_net'] > 0).mean()*100:.1f}%")
    print(f"  Stops triggered: {(trades_2022['reason'] == 'STOP').sum()}")
    print(f"\n  Top 10 worst 2022 trades:")
    print(trades_2022.nsmallest(10, "ret_net")[
        ["ticker", "entry_date", "exit_date", "ret_net", "reason", "play_type"]
    ].to_string(index=False, formatters={"ret_net": "{:+.1%}".format}))

# ────────────────────────────────────────────────────────────────────────
# 7. Win/lose streaks
# ────────────────────────────────────────────────────────────────────────
print("\n" + "═" * 90)
print("  WIN/LOSE STREAKS")
print("═" * 90)
trades_sorted = trades_df.sort_values("exit_date")
trades_sorted["win"] = trades_sorted["ret_net"] > 0
streaks = []
current_streak = 1
for i in range(1, len(trades_sorted)):
    if trades_sorted["win"].iloc[i] == trades_sorted["win"].iloc[i-1]:
        current_streak += 1
    else:
        streaks.append((trades_sorted["win"].iloc[i-1], current_streak))
        current_streak = 1
streaks.append((trades_sorted["win"].iloc[-1], current_streak))
win_streaks = [s[1] for s in streaks if s[0]]
lose_streaks = [s[1] for s in streaks if not s[0]]
print(f"  Max win streak: {max(win_streaks)} consecutive wins")
print(f"  Max lose streak: {max(lose_streaks)} consecutive losses")
print(f"  Avg win streak: {np.mean(win_streaks):.1f}")
print(f"  Avg lose streak: {np.mean(lose_streaks):.1f}")

# ────────────────────────────────────────────────────────────────────────
# 8. Yearly breakdown
# ────────────────────────────────────────────────────────────────────────
print("\n" + "═" * 90)
print("  YEAR-BY-YEAR BREAKDOWN")
print("═" * 90)
yr_breakdown = trades_df.groupby("yr").agg(
    n_trades=("ret_net", "count"),
    avg_ret=("ret_net", "mean"),
    median_ret=("ret_net", "median"),
    win_rate=("ret_net", lambda x: (x > 0).mean() * 100),
    n_wins=("ret_net", lambda x: (x > 0).sum()),
    n_losses=("ret_net", lambda x: (x <= 0).sum()),
    sum_winners=("ret_net", lambda x: x[x > 0].sum() * 100),
    sum_losers=("ret_net", lambda x: x[x <= 0].sum() * 100),
)
yr_breakdown["profit_factor"] = (
    yr_breakdown["sum_winners"] / yr_breakdown["sum_losers"].abs().replace(0, np.nan)
)
print(yr_breakdown.to_string(float_format=lambda x: f"{x:.2f}"))

trades_df.to_csv(os.path.join(WORKDIR, "data/aggressive_trades_full.csv"), index=False)
print("\n  Saved: aggressive_trades_full.csv")
