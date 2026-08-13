#!/usr/bin/env python3
"""
alphalens_report.py — Generate AlphaLens Paper Portfolio section for daily plan report.

Usage:
    python3 alphalens_report.py [--date YYYY-MM-DD]

Output: markdown string for inclusion in Discord daily report.
"""

import json
import os
import sys
import argparse
from pathlib import Path

WORKDIR = Path(os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude"))
PAPER_FILE = WORKDIR / "data" / "alphalens_paper.json"
BQ_CACHE = WORKDIR / "data" / "bq_cache"


def query_latest_prices(tickers: list[str]):
    """Query latest Close, PE, PB, ROE5Y from ticker_1m cache."""
    try:
        import duckdb
        con = duckdb.connect()
        tickers_sql = ",".join(f"'{t}'" for t in tickers)
        # Get latest available date for these tickers
        df = con.execute(f"""
            WITH ranked AS (
                SELECT ticker, time, Close, PE, PB, ROE5Y, VNINDEX,
                       ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY time DESC) AS rn
                FROM read_parquet('{BQ_CACHE}/ticker_1m.parquet')
                WHERE ticker IN ({tickers_sql})
            )
            SELECT ticker, time, Close, PE, PB, ROE5Y, VNINDEX
            FROM ranked WHERE rn = 1
            ORDER BY ticker
        """).df()
        return df, None
    except Exception as e:
        return None, str(e)


def query_pe_ma1y(tickers: list[str]):
    """Get PE_MA1Y from ticker_financial (latest per ticker)."""
    try:
        import duckdb
        con = duckdb.connect()
        tickers_sql = ",".join(f"'{t}'" for t in tickers)
        df = con.execute(f"""
            WITH ranked AS (
                SELECT ticker, time, PE_MA1Y,
                       ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY time DESC) AS rn
                FROM read_parquet('{BQ_CACHE}/ticker_financial.parquet')
                WHERE ticker IN ({tickers_sql})
            )
            SELECT ticker, PE_MA1Y FROM ranked WHERE rn = 1
        """).df()
        return {row['ticker']: row['PE_MA1Y'] for _, row in df.iterrows()}
    except Exception:
        return {}


def query_vnindex_latest():
    """Get latest VNINDEX close from ticker_1m."""
    try:
        import duckdb
        con = duckdb.connect()
        row = con.execute(f"""
            SELECT Close FROM read_parquet('{BQ_CACHE}/ticker_1m.parquet')
            WHERE ticker = 'VNINDEX'
            ORDER BY time DESC LIMIT 1
        """).df()
        if not row.empty:
            return float(row.iloc[0]['Close'])
    except Exception:
        pass
    return None


def generate_section(as_of_date: str = None) -> str:
    """Return formatted AlphaLens Paper Portfolio markdown section."""
    try:
        with open(PAPER_FILE) as f:
            paper = json.load(f)
    except Exception as e:
        return f"⚠️ AlphaLens: không đọc được {PAPER_FILE}: {e}"

    meta = paper.get("meta", {})
    positions = paper.get("positions", [])
    benchmark_entry = meta.get("benchmark_entry", 1860.01)
    tickers = [p["ticker"] for p in positions]

    # `entry_price` is a FROZEN raw price; `Close` below is retroactively dividend/split-adjusted
    # from today's vintage. Comparing them directly charges every post-entry corporate action to
    # the position as a price loss (Bẫy 2 of kb/data_registry/price-volume/
    # ticker_close_vs_price_dividend_adj.md) — MBB's 2026-08-11 ex-rights made this report show
    # -18,8% against a true +1,3%. Rebase the entry onto the adjusted scale first. Names with no
    # corporate action get factor 1,0 and are left bit-for-bit unchanged.
    from paper_entry_adjust import adjust_entries
    entry_asof = {p["ticker"]: (meta.get("entry_price_asof") or p.get("entry_date")) for p in positions}
    adj = adjust_entries([(p["ticker"], entry_asof[p["ticker"]], p["entry_price"]) for p in positions])

    prices_df, err = query_latest_prices(tickers)
    pe_ma1y_map = query_pe_ma1y(tickers)
    vni_current = query_vnindex_latest()

    lines = ["### 📊 AlphaLens Paper Portfolio"]
    if as_of_date:
        lines[0] += f" ({as_of_date})"

    if err or prices_df is None:
        lines.append(f"⚠️ Không lấy được giá: {err or 'no data'}")
    else:
        price_map = {row['ticker']: row for _, row in prices_df.iterrows()}
        data_date = prices_df['time'].max() if not prices_df.empty else "?"
        lines.append(f"*Giá tham chiếu: {data_date} | Entry: 2026-07-01*")
        lines.append("")

        pnl_list = []
        alert_lines = []

        for pos in positions:
            ticker = pos["ticker"]
            entry = pos["entry_price"]
            weight = pos.get("weight_paper", 0.25)

            if ticker not in price_map:
                lines.append(f"- **{ticker}**: N/A")
                continue

            row = price_map[ticker]
            current = float(row['Close'])
            a = adj.get((ticker, entry_asof[ticker]))
            if a is None:                      # cannot happen; degrade rather than crash the report
                pct = (current - entry) / entry * 100
            else:
                pct = a.pct_vs(current)
                if a.degraded:
                    alert_lines.append(f"⚠️ **{ticker}**: chưa quy đổi được giá vào về hệ điều chỉnh "
                                       f"({a.note}) — % dưới đây tính trên giá vào THÔ, có thể sai "
                                       f"nếu mã có sự kiện quyền sau ngày vào.")
                elif a.note:
                    alert_lines.append(f"⚠️ **{ticker}**: {a.note}")
            pnl_list.append(pct)

            pe_now = float(row['PE']) if row['PE'] else None
            pb_now = float(row['PB']) if row['PB'] else None
            roe5y = float(row['ROE5Y']) if row['ROE5Y'] else None

            sign = "+" if pct >= 0 else ""
            line = f"- **{ticker}**: {current:,.0f}đ ({sign}{pct:.1f}%)"
            if a is not None and a.is_adjusted:
                # say it out loud: a reader comparing against the JSON's entry_price must be able
                # to see WHY the denominator is not that number
                line += f" *[giá vào {a.entry_price:,.0f}→{a.entry_adj:,.0f} do quyền]*"
                if a.rights_events:
                    # the convention is a real fork in the number, not a footnote: state it on the
                    # line that carries the number, and show what the other convention would say
                    terp_pct = (current - a.entry_price * a.factor_terp) / (
                        a.entry_price * a.factor_terp) * 100
                    line += (f" *[quyền mua {', '.join(a.rights_events)} KHÔNG tính vào tỉ suất — "
                             f"sổ paper không có tài khoản tiền để thực hiện quyền; nếu giả định "
                             f"đã mua/bán quyền theo giá lý thuyết thì {terp_pct:+.1f}%]*")

            # DCF check (informational only — never gates this report). ACB/MBB/HDB are
            # financials -> dcf_line() auto-degrades to N/A via the same gate as Pha 2 production.
            try:
                from dcf_valuation import dcf_line
                dcf_str = dcf_line(ticker, as_of_date or data_date, price=current)
            except Exception as e:
                dcf_str = f"DCF: N/A (dcf_error: {str(e)[:40]})"
            line += f" | {dcf_str}"

            # Valuation annotation
            if ticker == "FPT":
                pe_ma1y = pe_ma1y_map.get("FPT")
                if pe_now and pe_ma1y:
                    line += f" | PE {pe_now:.1f} vs MA1Y {pe_ma1y:.1f}"
                    if pe_now > pe_ma1y:
                        alert_lines.append(f"🔴 **FPT EXIT ALERT**: PE {pe_now:.1f} > PE_MA1Y {pe_ma1y:.1f} — điều kiện entry bị phá!")
            else:
                if pb_now and roe5y:
                    just_pb = (roe5y - 0.05) / 0.08
                    line += f" | PB {pb_now:.2f} vs justPB {just_pb:.2f}"
                    if pb_now > just_pb:
                        alert_lines.append(f"🔴 **{ticker} EXIT ALERT**: PB {pb_now:.2f} > justified {just_pb:.2f} — điều kiện entry bị phá!")

            lines.append(line)

        # Portfolio P&L
        if pnl_list:
            portfolio_pnl = sum(pnl_list) / len(pnl_list)
            lines.append("")
            pnl_sign = "+" if portfolio_pnl >= 0 else ""

            if vni_current:
                vni_pnl = (vni_current - benchmark_entry) / benchmark_entry * 100
                vni_sign = "+" if vni_pnl >= 0 else ""
                alpha = portfolio_pnl - vni_pnl
                alpha_sign = "+" if alpha >= 0 else ""
                lines.append(f"**Portfolio**: {pnl_sign}{portfolio_pnl:.2f}% | **VNINDEX**: {vni_sign}{vni_pnl:.2f}% | **Alpha**: {alpha_sign}{alpha:.2f}pp")
            else:
                lines.append(f"**Portfolio P&L**: {pnl_sign}{portfolio_pnl:.2f}% (VNINDEX N/A)")

        # Alerts
        if alert_lines:
            lines.append("")
            lines.extend(alert_lines)

    lines.append(f"*End date: {meta.get('end_date','2026-09-30')} | Auditor: {meta.get('auditor','Taylor')}*")
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="Reporting date (YYYY-MM-DD)", default=None)
    args = parser.parse_args()
    print(generate_section(as_of_date=args.date))
