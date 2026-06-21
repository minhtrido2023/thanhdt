#!/usr/bin/env python3
"""
Portfolio analysis tool.

Usage:
    python analyze_portfolio.py \
        --logs data/v1_debug_logs_df.csv \
        --transactions data/v1_debug_transactions_df.csv \
        --output report.md
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fmt_vnd(value: float, unit: str = "B") -> str:
    """Format a VND amount as billions (B) or millions (M)."""
    if unit == "B":
        return f"{value / 1e9:,.2f}B"
    return f"{value / 1e6:,.1f}M"


def fmt_pct(value: float) -> str:
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}%"


def pct(a: float, b: float) -> float:
    """Return (a/b - 1) * 100 avoiding div-by-zero."""
    return (a / b - 1) * 100 if b else 0.0


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_data(logs_path: str, tx_path: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    def _load(path: str) -> pd.DataFrame:
        p = Path(path)
        if p.suffix == ".jsonl":
            df = pd.read_json(p, lines=True)
        else:
            df = pd.read_csv(p)
        df["ymd"] = pd.to_datetime(df["ymd"])
        return df

    logs = _load(logs_path)
    tx = _load(tx_path)
    logs.sort_values("ymd", inplace=True)
    tx.sort_values("ymd", inplace=True)
    return logs, tx


# ---------------------------------------------------------------------------
# Portfolio overview
# ---------------------------------------------------------------------------

def portfolio_overview(logs: pd.DataFrame) -> dict:
    first = logs.iloc[0]
    last = logs.iloc[-1]
    initial_nav = first["nav"]
    final_nav = last["nav"]
    peak_nav = logs["nav"].max()
    trough_nav = logs["nav"].min()
    total_return = pct(final_nav, initial_nav)

    # Max drawdown from peak
    logs = logs.copy()
    logs["rolling_peak"] = logs["nav"].cummax()
    logs["drawdown"] = (logs["nav"] - logs["rolling_peak"]) / logs["rolling_peak"] * 100
    max_drawdown = logs["drawdown"].min()
    max_drawdown_date = logs.loc[logs["drawdown"].idxmin(), "ymd"]

    trading_days = len(logs)
    date_range_days = (last["ymd"] - first["ymd"]).days
    years = date_range_days / 365.25
    cagr = ((final_nav / initial_nav) ** (1 / years) - 1) * 100 if years > 0 else 0

    return {
        "start_date": first["ymd"].strftime("%Y-%m-%d"),
        "end_date": last["ymd"].strftime("%Y-%m-%d"),
        "years": years,
        "trading_days": trading_days,
        "initial_nav": initial_nav,
        "final_nav": final_nav,
        "peak_nav": peak_nav,
        "total_return": total_return,
        "cagr": cagr,
        "max_drawdown": max_drawdown,
        "max_drawdown_date": max_drawdown_date.strftime("%Y-%m-%d"),
        "avg_holdings": logs["num_holdings"].mean(),
        "max_holdings": int(logs["num_holdings"].max()),
        "total_tx": int(last["num_transactions"]),
    }


# ---------------------------------------------------------------------------
# Position-level P&L  (group by holding_id)
# ---------------------------------------------------------------------------

def compute_positions(tx: pd.DataFrame) -> pd.DataFrame:
    """
    For each holding_id compute:
      - ticker, first_buy_date, last_activity_date
      - total_invested, total_proceeds, total_fees
      - pnl, pnl_pct, status (open/closed)
      - holding_days
    """
    rows = []
    for hid, grp in tx.groupby("holding_id"):
        buys = grp[grp["action"] == "buy"]
        sells = grp[grp["action"] == "sell"]

        ticker = grp["ticker"].iloc[0]
        first_buy = buys["ymd"].min() if not buys.empty else grp["ymd"].min()
        last_date = grp["ymd"].max()

        total_invested = buys["buy_amount"].sum()
        total_proceeds = sells["sell_amount"].sum()
        total_fees = grp["fee"].sum()

        is_closed = not sells.empty
        # For open positions, proceeds = 0 so pnl is unrealised cost
        pnl = total_proceeds - total_invested - total_fees
        pnl_pct = pct(total_proceeds, total_invested + total_fees) if is_closed else None

        holding_days = (last_date - first_buy).days if is_closed else None

        rows.append({
            "holding_id": hid,
            "ticker": ticker,
            "first_buy": first_buy,
            "last_date": last_date,
            "total_invested": total_invested,
            "total_proceeds": total_proceeds,
            "total_fees": total_fees,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "holding_days": holding_days,
            "status": "closed" if is_closed else "open",
            "num_buys": len(buys),
            "num_sells": len(sells),
        })

    positions = pd.DataFrame(rows)
    positions.sort_values("first_buy", inplace=True)
    return positions


# ---------------------------------------------------------------------------
# Transaction summary
# ---------------------------------------------------------------------------

def transaction_summary(tx: pd.DataFrame, positions: pd.DataFrame) -> dict:
    buys = tx[tx["action"] == "buy"]
    sells = tx[tx["action"] == "sell"]
    closed = positions[positions["status"] == "closed"]
    open_pos = positions[positions["status"] == "open"]

    winners = closed[closed["pnl"] > 0]
    losers = closed[closed["pnl"] <= 0]
    win_rate = len(winners) / len(closed) * 100 if len(closed) > 0 else 0

    return {
        "total_buys": len(buys),
        "total_sells": len(sells),
        "total_fees": tx["fee"].sum(),
        "total_invested": buys["buy_amount"].sum(),
        "total_proceeds": sells["sell_amount"].sum(),
        "unique_tickers": tx["ticker"].nunique(),
        "num_positions": len(positions),
        "num_closed": len(closed),
        "num_open": len(open_pos),
        "num_winners": len(winners),
        "num_losers": len(losers),
        "win_rate": win_rate,
        "avg_pnl_pct_winners": winners["pnl_pct"].mean() if len(winners) > 0 else 0,
        "avg_pnl_pct_losers": losers["pnl_pct"].mean() if len(losers) > 0 else 0,
        "avg_holding_days": closed["holding_days"].mean() if len(closed) > 0 else 0,
        "median_holding_days": closed["holding_days"].median() if len(closed) > 0 else 0,
        "total_realised_pnl": closed["pnl"].sum(),
        "total_open_cost": open_pos["total_invested"].sum(),
    }


# ---------------------------------------------------------------------------
# Yearly breakdown
# ---------------------------------------------------------------------------

def yearly_breakdown(logs: pd.DataFrame, tx: pd.DataFrame) -> pd.DataFrame:
    logs = logs.copy()
    logs["year"] = logs["ymd"].dt.year

    # NAV at start/end of each year
    year_first = logs.groupby("year").first()[["nav"]].rename(columns={"nav": "nav_start"})
    year_last = logs.groupby("year").last()[["nav"]].rename(columns={"nav": "nav_end"})
    yearly = year_first.join(year_last)
    yearly["return_pct"] = (yearly["nav_end"] / yearly["nav_start"] - 1) * 100

    # Transaction counts per year
    tx = tx.copy()
    tx["year"] = tx["ymd"].dt.year
    tx_counts = tx.groupby(["year", "action"]).size().unstack(fill_value=0)
    if "buy" not in tx_counts.columns:
        tx_counts["buy"] = 0
    if "sell" not in tx_counts.columns:
        tx_counts["sell"] = 0

    yearly = yearly.join(tx_counts[["buy", "sell"]], how="left").fillna(0)
    yearly[["buy", "sell"]] = yearly[["buy", "sell"]].astype(int)
    return yearly.reset_index()


# ---------------------------------------------------------------------------
# Top/bottom positions table
# ---------------------------------------------------------------------------

def top_positions(positions: pd.DataFrame, n: int = 10) -> tuple[pd.DataFrame, pd.DataFrame]:
    closed = positions[positions["status"] == "closed"].copy()
    closed.sort_values("pnl", ascending=False, inplace=True)
    top = closed.head(n)
    bottom = closed.tail(n).sort_values("pnl")
    return top, bottom


# ---------------------------------------------------------------------------
# Most traded tickers
# ---------------------------------------------------------------------------

def most_traded(tx: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    counts = tx.groupby("ticker").agg(
        total_trades=("action", "count"),
        buys=("action", lambda x: (x == "buy").sum()),
        sells=("action", lambda x: (x == "sell").sum()),
        total_invested=("buy_amount", "sum"),
        total_proceeds=("sell_amount", "sum"),
    ).reset_index()
    counts.sort_values("total_trades", ascending=False, inplace=True)
    return counts.head(n)


# ---------------------------------------------------------------------------
# Active periods (monthly trade activity)
# ---------------------------------------------------------------------------

def monthly_activity(tx: pd.DataFrame) -> pd.DataFrame:
    tx = tx.copy()
    tx["month"] = tx["ymd"].dt.to_period("M")
    monthly = tx.groupby("month").agg(
        trades=("action", "count"),
        buys=("action", lambda x: (x == "buy").sum()),
        sells=("action", lambda x: (x == "sell").sum()),
        volume=("buy_amount", "sum"),
    ).reset_index()
    monthly["month"] = monthly["month"].astype(str)
    return monthly


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

def pos_row(p: pd.Series) -> str:
    pnl_str = fmt_vnd(p["pnl"])
    pct_str = fmt_pct(p["pnl_pct"]) if p["pnl_pct"] is not None else "—"
    hold_str = f"{int(p['holding_days'])}d" if p["holding_days"] is not None else "open"
    return (
        f"| {p['ticker']} | {p['first_buy'].strftime('%Y-%m-%d')} | "
        f"{p['last_date'].strftime('%Y-%m-%d')} | {hold_str} | "
        f"{fmt_vnd(p['total_invested'])} | {fmt_vnd(p['total_proceeds'])} | "
        f"{pnl_str} | {pct_str} |"
    )


def render_md(
    overview: dict,
    summary: dict,
    yearly: pd.DataFrame,
    top: pd.DataFrame,
    bottom: pd.DataFrame,
    most_tx: pd.DataFrame,
    positions: pd.DataFrame,
    logs: pd.DataFrame,
) -> str:
    lines = []
    a = lines.append

    a("# Portfolio Simulation Report")
    a("")
    a(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    a("")

    # ---- Overview ----
    a("## Overview")
    a("")
    a(f"| | |")
    a(f"|---|---|")
    a(f"| **Period** | {overview['start_date']} → {overview['end_date']} ({overview['years']:.1f} years, {overview['trading_days']} trading days) |")
    a(f"| **Initial NAV** | {fmt_vnd(overview['initial_nav'])} VND |")
    a(f"| **Final NAV** | {fmt_vnd(overview['final_nav'])} VND |")
    a(f"| **Total Return** | {fmt_pct(overview['total_return'])} |")
    a(f"| **CAGR** | {fmt_pct(overview['cagr'])} |")
    a(f"| **Peak NAV** | {fmt_vnd(overview['peak_nav'])} VND |")
    a(f"| **Max Drawdown** | {fmt_pct(overview['max_drawdown'])} (on {overview['max_drawdown_date']}) |")
    a(f"| **Avg / Max Holdings** | {overview['avg_holdings']:.1f} / {overview['max_holdings']} positions |")
    a(f"| **Total Transactions** | {overview['total_tx']} |")
    a("")

    # ---- Transaction summary ----
    a("## Transaction Summary")
    a("")
    a(f"| | |")
    a(f"|---|---|")
    a(f"| **Total buy orders** | {summary['total_buys']} |")
    a(f"| **Total sell orders** | {summary['total_sells']} |")
    a(f"| **Unique tickers traded** | {summary['unique_tickers']} |")
    a(f"| **Total capital deployed** | {fmt_vnd(summary['total_invested'])} VND |")
    a(f"| **Total proceeds** | {fmt_vnd(summary['total_proceeds'])} VND |")
    a(f"| **Total fees paid** | {fmt_vnd(summary['total_fees'])} VND |")
    a(f"| **Closed positions** | {summary['num_closed']} |")
    a(f"| **Open positions** | {summary['num_open']} |")
    a(f"| **Win rate (closed)** | {summary['win_rate']:.1f}% ({summary['num_winners']} wins / {summary['num_losers']} losses) |")
    a(f"| **Avg gain (winners)** | {fmt_pct(summary['avg_pnl_pct_winners'])} |")
    a(f"| **Avg loss (losers)** | {fmt_pct(summary['avg_pnl_pct_losers'])} |")
    a(f"| **Avg holding period** | {summary['avg_holding_days']:.0f} days (median {summary['median_holding_days']:.0f}d) |")
    a(f"| **Total realised P&L** | {fmt_vnd(summary['total_realised_pnl'])} VND |")
    a(f"| **Open positions cost** | {fmt_vnd(summary['total_open_cost'])} VND |")
    a("")

    # ---- Yearly breakdown ----
    a("## Year-by-Year Performance")
    a("")
    a("| Year | NAV Start | NAV End | Return | Buy Orders | Sell Orders |")
    a("|---|---|---|---|---|---|")
    for _, row in yearly.iterrows():
        a(f"| {int(row['year'])} | {fmt_vnd(row['nav_start'])} | {fmt_vnd(row['nav_end'])} | "
          f"{fmt_pct(row['return_pct'])} | {int(row['buy'])} | {int(row['sell'])} |")
    a("")

    # ---- Top winners ----
    a("## Top 10 Most Profitable Positions")
    a("")
    a("| Ticker | Buy Date | Close Date | Held | Invested | Proceeds | P&L | Return |")
    a("|---|---|---|---|---|---|---|---|")
    for _, row in top.iterrows():
        a(pos_row(row))
    a("")

    # ---- Worst losers ----
    a("## Top 10 Biggest Losses")
    a("")
    a("| Ticker | Buy Date | Close Date | Held | Invested | Proceeds | P&L | Return |")
    a("|---|---|---|---|---|---|---|---|")
    for _, row in bottom.iterrows():
        a(pos_row(row))
    a("")

    # ---- Most traded ----
    a("## Most Frequently Traded Tickers")
    a("")
    a("| Ticker | Total Trades | Buys | Sells | Total Invested | Total Proceeds |")
    a("|---|---|---|---|---|---|")
    for _, row in most_tx.iterrows():
        a(f"| {row['ticker']} | {int(row['total_trades'])} | {int(row['buys'])} | {int(row['sells'])} | "
          f"{fmt_vnd(row['total_invested'])} | {fmt_vnd(row['total_proceeds'])} |")
    a("")

    # ---- Open positions ----
    open_pos = positions[positions["status"] == "open"].copy()
    open_pos.sort_values("total_invested", ascending=False, inplace=True)
    if not open_pos.empty:
        a("## Currently Open Positions")
        a("")
        a("| Ticker | First Buy | Total Invested | Num Buys |")
        a("|---|---|---|---|")
        for _, row in open_pos.iterrows():
            a(f"| {row['ticker']} | {row['first_buy'].strftime('%Y-%m-%d')} | "
              f"{fmt_vnd(row['total_invested'])} | {int(row['num_buys'])} |")
        a("")

    # ---- P&L distribution ----
    closed = positions[positions["status"] == "closed"].copy()
    if not closed.empty:
        bins = [-999, -20, -10, -5, 0, 5, 10, 20, 50, 100, 9999]
        labels = ["<-20%", "-20→-10%", "-10→-5%", "-5→0%", "0→5%", "5→10%", "10→20%", "20→50%", "50→100%", ">100%"]
        closed["bucket"] = pd.cut(closed["pnl_pct"], bins=bins, labels=labels)
        dist = closed.groupby("bucket", observed=False).size().reset_index(name="count")

        a("## Return Distribution (Closed Positions)")
        a("")
        a("| Return Range | # Positions |")
        a("|---|---|")
        for _, row in dist.iterrows():
            bar = "█" * min(int(row["count"]), 40)
            a(f"| {row['bucket']} | {int(row['count'])} {bar} |")
        a("")

    # ---- Notable transactions ----
    a("## Notable Single Transactions")
    a("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate portfolio analysis report.")
    parser.add_argument("--logs", default="data/v1_debug_logs_df.csv", help="Path to daily logs CSV")
    parser.add_argument("--transactions", default="data/v1_debug_transactions_df.csv", help="Path to transactions CSV")
    parser.add_argument("--output", default="report.md", help="Output markdown file path (.md)")
    args = parser.parse_args()

    print("Loading data...")
    logs, tx = load_data(args.logs, args.transactions)
    print(f"  {len(logs)} daily log rows, {len(tx)} transaction rows")

    print("Computing positions...")
    positions = compute_positions(tx)
    print(f"  {len(positions)} positions ({positions['status'].value_counts().to_dict()})")

    print("Generating report sections...")
    overview = portfolio_overview(logs)
    summary = transaction_summary(tx, positions)
    yearly = yearly_breakdown(logs, tx)
    top, bottom = top_positions(positions)
    most_tx = most_traded(tx)

    md = render_md(overview, summary, yearly, top, bottom, most_tx, positions, logs)
    md += notable_transactions_section(tx)

    md_path = Path(args.output).with_suffix(".md")
    md_path.write_text(md, encoding="utf-8")
    print(f"Markdown written to: {md_path.resolve()}")


def notable_transactions_section(tx: pd.DataFrame) -> str:
    lines = []
    a = lines.append

    buys = tx[tx["action"] == "buy"].copy()
    sells = tx[tx["action"] == "sell"].copy()

    # Top 5 largest buys by buy_amount
    top_buys = buys.nlargest(5, "buy_amount")
    a("### Largest Individual Buys")
    a("")
    a("| Date | Ticker | Amount | Price |")
    a("|---|---|---|---|")
    for _, row in top_buys.iterrows():
        a(f"| {row['ymd'].strftime('%Y-%m-%d')} | {row['ticker']} | "
          f"{fmt_vnd(row['buy_amount'])} | {row['adj_price']:,.0f} |")
    a("")

    # Top 5 largest sells by sell_amount
    top_sells = sells.nlargest(5, "sell_amount")
    a("### Largest Individual Sells")
    a("")
    a("| Date | Ticker | Proceeds | Price |")
    a("|---|---|---|---|")
    for _, row in top_sells.iterrows():
        a(f"| {row['ymd'].strftime('%Y-%m-%d')} | {row['ticker']} | "
          f"{fmt_vnd(row['sell_amount'])} | {row['adj_price']:,.0f} |")
    a("")

    return "\n".join(lines)


if __name__ == "__main__":
    main()
