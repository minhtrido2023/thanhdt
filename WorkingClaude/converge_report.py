#!/usr/bin/env python3
"""converge_report.py — ConvergePort Paper Portfolio section for the daily "New deals" report.

Job Taylor_20260706_093329. RESEARCH / PAPER ONLY (no production file touched). Mirrors
alphalens_report.generate_section(): reads data/converge_portfolio_paper.json, prices the seed
double-confirm book (weighted P&L vs entry + vs VNINDEX benchmark), and — because ConvergePort is
a DYNAMIC book (unlike the static AlphaLens 4-name) — also shows the LIVE double-confirm set today
with ADD/DROP vs the seed (the entry/exit signals a live rebalance would act on). Degrades to a
single ⚠️ line on any failure; never raises (the caller must not be aborted by this optional block).

Backtest that justified the launch: FULL 2014-08->now +5.0pp CAGR / +0.23 Sharpe / +0.11 Calmar vs
custom30V-thuan; edge in IS(+1.5pp) AND OOS(+8.3pp); leave-one-year-out stable; DSR 0.998. See
converge_portfolio_backtest.py + mike/agents/Taylor/converge_portfolio_framework.md.
"""
import json
import os
from pathlib import Path

WORKDIR = Path(os.environ.get("WORKDIR_8L", os.environ.get("WORKDIR", "/home/trido/thanhdt/WorkingClaude")))
PAPER_FILE = WORKDIR / "data" / "converge_portfolio_paper.json"
BQ_CACHE = WORKDIR / "data" / "bq_cache"


def _latest_prices(tickers):
    """Latest Close per ticker + latest VNINDEX, from the ticker cache (as-of freshest row)."""
    try:
        import duckdb
        con = duckdb.connect(); con.execute("SET threads=1")
        tsql = ",".join(f"'{t}'" for t in tickers + ["VNINDEX"])
        df = con.execute(f"""
            WITH r AS (SELECT ticker, time, Close, VNINDEX,
                       ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY time DESC) rn
                       FROM read_parquet('{BQ_CACHE}/ticker/*.parquet') WHERE ticker IN ({tsql}))
            SELECT ticker, time, Close, VNINDEX FROM r WHERE rn=1""").df()
        con.close()
        price = {row["ticker"]: float(row["Close"]) for _, row in df.iterrows()}
        # VNINDEX current = the VNINDEX mirror on any stock row (freshest), else the VNINDEX ticker row
        vni = None
        stk = df[df["ticker"] != "VNINDEX"]
        if not stk.empty:
            vni = float(stk.sort_values("time").iloc[-1]["VNINDEX"])
        elif "VNINDEX" in price:
            vni = price["VNINDEX"]
        data_date = str(df["time"].max()) if not df.empty else "?"
        return price, vni, data_date, None
    except Exception as e:
        return {}, None, "?", str(e)


def _live_double_confirm():
    """Current live double-confirm set {ticker: buy_mode} via the live sector-lens + 8L rating.
    Returns {} on any failure (the diff is then simply omitted)."""
    try:
        import sector_lens_monitor as slm
        r = slm.compute_status()
        ratings = slm.load_ratings()
        df = r["df"]
        out = {}
        for _, row in df[df["status"] == "BUY"].iterrows():
            rt = ratings.get(row["ticker"])
            if rt is not None and int(rt) <= 2:
                out[row["ticker"]] = row["buy_mode"] or "ACCUMULATE"
        return out
    except Exception:
        return {}


def generate_section(as_of_date=None, live_set=None):
    """Return the ConvergePort markdown section. live_set (optional) = precomputed
    {ticker: buy_mode} to avoid recomputing the sector-lens; falls back to _live_double_confirm()."""
    try:
        with open(PAPER_FILE) as f:
            paper = json.load(f)
    except Exception as e:
        return f"⚠️ ConvergePort: không đọc được {PAPER_FILE}: {e}"

    meta = paper.get("meta", {})
    seed = paper.get("seed_double_confirm_set", [])
    bench_entry = meta.get("benchmark_entry", 1871.91)
    tickers = [p["ticker"] for p in seed]

    price, vni, data_date, err = _latest_prices(tickers)

    lines = ["### 🔗 DC Book (double-confirm) — Paper Portfolio"]
    if as_of_date:
        lines[0] += f" ({as_of_date})"
    lines.append(f"*Giá tham chiếu: {data_date} | Entry: {meta.get('start_date','2026-07-06')} "
                 f"(giá {meta.get('entry_price_asof','?')}) | equal-weight, cap 20%, idle→custom30V*")
    lines.append("")

    if err:
        lines.append(f"⚠️ Không lấy được giá: {err}")
    else:
        wsum = 0.0
        pnl_w = 0.0
        for pos in seed:
            tk = pos["ticker"]; entry = pos["entry_price"]; w = pos.get("weight_paper", 0.0)
            cur = price.get(tk)
            if cur is None:
                lines.append(f"- **{tk}**: N/A"); continue
            pct = (cur - entry) / entry * 100
            pnl_w += w * pct; wsum += w
            sign = "+" if pct >= 0 else ""
            mode = pos.get("buy_mode", "")
            lines.append(f"- **{tk}** ({pos.get('sector','')}): {cur:,.0f}đ ({sign}{pct:.1f}%) · {mode}")

        if wsum > 0:
            port = pnl_w / wsum
            ps = "+" if port >= 0 else ""
            lines.append("")
            if vni:
                vpnl = (vni - bench_entry) / bench_entry * 100
                vs = "+" if vpnl >= 0 else ""
                a = port - vpnl; as_ = "+" if a >= 0 else ""
                lines.append(f"**Portfolio (seed, weighted)**: {ps}{port:.2f}% | "
                             f"**VNINDEX**: {vs}{vpnl:.2f}% | **Alpha**: {as_}{a:.2f}pp")
            else:
                lines.append(f"**Portfolio (seed, weighted)**: {ps}{port:.2f}% (VNINDEX N/A)")

    # ---- live double-confirm diff (dynamic entry/exit signals) ----
    live = live_set if live_set is not None else _live_double_confirm()
    if live:
        seed_tk = {p["ticker"] for p in seed}
        adds = [f"{t}·{m}" for t, m in sorted(live.items()) if t not in seed_tk]
        drops = [t for t in sorted(seed_tk) if t not in live]
        lines.append("")
        lines.append(f"**Live double-confirm ({len(live)}):** " + ", ".join(sorted(live)))
        if adds:
            lines.append(f"🟢 ENTER (mới double-confirm, chưa trong seed): {', '.join(adds)}")
        if drops:
            lines.append(f"🔴 EXIT (seed rời double-confirm): {', '.join(drops)}")
        if not adds and not drops:
            lines.append("*(không thay đổi so với seed)*")

    lines.append(f"*Review: {meta.get('review_date','2026-10-06')} | Auditor: "
                 f"{meta.get('auditor','Taylor')} | PAPER — research/monitor, not an order*")
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None)
    a = ap.parse_args()
    print(generate_section(as_of_date=a.date))
