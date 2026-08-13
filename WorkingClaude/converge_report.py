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


def _production_nav_return():
    """Return (pct, first_date, last_date, None) for the REAL V2.4 production book (SpaceX),
    read straight from the verified NAV series `nav_history_SpaceX.csv` (col `nav` — already the
    total incl. off-book Trứng vàng; per coding_guidelines §6 this file IS the authoritative
    provenance, do not recompute NAV from anywhere else). Window = first available row (SpaceX
    go-live, ≠ the DC-book entry date) → latest row. Returns (None, None, None, err) on any
    failure; the caller degrades to a warning line instead of aborting the report."""
    try:
        import csv
        path = WORKDIR / "data" / "execution_logs" / "nav_history_SpaceX.csv"
        rows = []
        with open(path) as f:
            for r in csv.DictReader(f):
                nav = float(r["nav"])
                if nav > 0:
                    rows.append((r["date"], nav))
        if len(rows) < 2:
            return None, None, None, "chưa đủ 2 dòng NAV"
        rows.sort(key=lambda x: x[0])
        pct = (rows[-1][1] / rows[0][1] - 1) * 100
        return pct, rows[0][0], rows[-1][0], None
    except Exception as e:
        return None, None, None, str(e)


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

    # Same reference-frame fix as alphalens_report: `entry_price` is a frozen RAW snapshot (asof
    # meta.entry_price_asof) while `price` above is today's ADJUSTED Close. Rebase the entry or
    # every post-entry corporate action is charged to the position as a loss. Affected today:
    # MBB (ex-rights 08-11), CTR (08-07... 07-09 cash+stock div), HAH (07-14 cash div).
    from paper_entry_adjust import adjust_entries
    entry_asof = meta.get("entry_price_asof") or meta.get("start_date")
    adj = adjust_entries([(p["ticker"], entry_asof, p["entry_price"]) for p in seed])

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
            a = adj.get((tk, entry_asof))
            pct = a.pct_vs(cur) if a is not None else (cur - entry) / entry * 100
            pnl_w += w * pct; wsum += w
            sign = "+" if pct >= 0 else ""
            mode = pos.get("buy_mode", "")
            rebase = ""
            if a is not None and a.is_adjusted:
                rebase = f" *[giá vào {a.entry_price:,.0f}→{a.entry_adj:,.0f} do quyền]*"
            elif a is not None and a.degraded:
                rebase = " ⚠️*[chưa quy đổi được giá vào — % tính trên giá THÔ]*"
            lines.append(f"- **{tk}** ({pos.get('sector','')}): {cur:,.0f}đ ({sign}{pct:.1f}%){rebase} · {mode}")

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

            # ---- vs V2.4 PRODUCTION thật (SpaceX NAV), KHÁC khung ngày → ghi rõ, không so mù ----
            prod, p_first, p_last, p_err = _production_nav_return()
            if p_err:
                lines.append(f"⚠️ V2.4 production: không đọc được nav_history_SpaceX.csv ({p_err})")
            else:
                pr = "+" if prod >= 0 else ""
                ap_ = port - prod; aps = "+" if ap_ >= 0 else ""
                lines.append(
                    f"**V2.4 production (từ {p_first[5:]}, NAV thật)**: {pr}{prod:.2f}% "
                    f"(→{p_last[5:]}) | **Alpha vs production**: {aps}{ap_:.2f}pp "
                    f"*(xấp xỉ — KHÔNG cùng khung ngày: DC book tính từ "
                    f"{meta.get('entry_price_asof','?')}, production chỉ có NAV thật từ {p_first})*")

    # ---- live double-confirm diff (dynamic entry/exit signals) ----
    live = live_set if live_set is not None else _live_double_confirm()
    if live:
        seed_tk = {p["ticker"] for p in seed}
        adds = [f"{t}·{m}" for t, m in sorted(live.items()) if t not in seed_tk]
        drops = [t for t in sorted(seed_tk) if t not in live]
        lines.append("")
        lines.append(f"**Live double-confirm ({len(live)}):**")

        # DCF check per name (informational only, never gates). Reuse price already fetched
        # above when the ticker is in the seed set; else dcf_line() fetches its own via BQ cache.
        try:
            from dcf_valuation import dcf_line
        except Exception:
            dcf_line = None
        dcf_asof = as_of_date or data_date
        for tk, mode in sorted(live.items()):
            if dcf_line is not None:
                try:
                    dcf_str = dcf_line(tk, dcf_asof, price=price.get(tk))
                except Exception as e:
                    dcf_str = f"DCF: N/A (dcf_error: {str(e)[:40]})"
            else:
                dcf_str = "DCF: N/A"
            lines.append(f"- **{tk}**·{mode} — {dcf_str}")

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
