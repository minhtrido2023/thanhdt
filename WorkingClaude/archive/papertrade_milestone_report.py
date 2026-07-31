# -*- coding: utf-8 -*-
"""Paper-trade milestone reports — Jun 30 (mid-term) + Aug 31 (final).

Comprehensive analysis vs weekly:
  - Cumulative + month-by-month stats per system
  - Realized vs backtest expectation (per-system table)
  - V5 vs V4 detailed comparison (Kelly Q2 verdict)
  - Drawdown chronology + recovery times
  - Per-system trade activity (count + turnover)
  - Final recommendation block

Usage:
  python papertrade_milestone_report.py           # auto-detect milestone
  python papertrade_milestone_report.py mid       # force mid-term (Jun 30)
  python papertrade_milestone_report.py final     # force final (Aug 31)

Writes:
  data/papertrade_milestone_<tag>_YYYY-MM-DD.md
"""
import os, sys, io, datetime as dt
import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)
from simulate_holistic_nav import bq

SYSTEMS = [
    ("V1", "V11 Song Sinh + TQ34b",          "data/pt_v11_tq34b_logs.csv",
     "data/pt_v11_tq34b_transactions.csv",
     {"backtest_full_cagr": 21.14, "backtest_oos_cagr": 28.88,
      "backtest_full_dd": -17.82, "backtest_full_sharpe": 1.45}),
    ("V2", "V12 Âm Dương + TQ34b",           "data/pt_v12_tq34b_logs.csv",
     "data/pt_v12_tq34b_transactions.csv",
     {"backtest_full_cagr": 21.96, "backtest_oos_cagr": 23.22,
      "backtest_full_dd": -14.39, "backtest_full_sharpe": 1.65}),
    ("V3", "V12 Âm Dương + LIVE Tinh Tế",    "data/pt_v12_live_logs.csv",
     "data/pt_v12_live_transactions.csv",
     {"backtest_full_cagr": 22.0, "backtest_oos_cagr": 23.0,
      "backtest_full_dd": -14.5, "backtest_full_sharpe": 1.65}),
    ("V4", "V12.1 Ensemble (M1+M3r AND-HOLD)","data/pt_v121_ens_logs.csv",
     "data/pt_v121_ens_transactions.csv",
     {"backtest_full_cagr": 24.70, "backtest_oos_cagr": 31.92,
      "backtest_full_dd": -15.43, "backtest_full_sharpe": 1.76}),
    ("V5", "V4 + Kelly Q2 NEUTRAL{1.0}",      "data/pt_v121_ens_q2_logs.csv",
     "data/pt_v121_ens_q2_transactions.csv",
     {"backtest_full_cagr": 25.71, "backtest_oos_cagr": 36.16,
      "backtest_full_dd": -16.93, "backtest_full_sharpe": 1.70}),
]
START = pd.Timestamp("2026-04-01")


def load_nav(path):
    full = os.path.join(WORKDIR, path)
    if not os.path.exists(full): return None
    df = pd.read_csv(full, parse_dates=["ymd"]).sort_values("ymd")
    return df.set_index("ymd")["nav"]


def load_tx(path):
    full = os.path.join(WORKDIR, path)
    if not os.path.exists(full): return None
    df = pd.read_csv(full, parse_dates=["ymd"])
    return df[df["reason"] != "MTM_UNREALIZED"] if "reason" in df.columns else df


def stats_full(nav, start=START):
    nav = nav[nav.index >= start].dropna()
    if len(nav) < 2: return None
    ret = nav.iloc[-1]/nav.iloc[0] - 1
    days = (nav.index[-1] - nav.index[0]).days
    cagr = (1+ret)**(365.25/max(days,1)) - 1 if days > 0 else 0
    peak = nav.cummax(); dd_s = (nav-peak)/peak
    dd = dd_s.min()
    daily = nav.pct_change().dropna()
    vol_ann = daily.std() * np.sqrt(252) if len(daily) > 0 else 0
    sharpe = (daily.mean()*252)/vol_ann if vol_ann > 0 else 0
    calmar = cagr/abs(dd) if dd < 0 else float("nan")
    # DD chronology
    dd_trough_date = dd_s.idxmin() if len(dd_s) > 0 else None
    return {"first_nav": nav.iloc[0], "last_nav": nav.iloc[-1],
            "ret": ret, "cagr": cagr, "dd": dd, "sharpe": sharpe, "calmar": calmar,
            "vol_ann": vol_ann, "days": days, "dd_trough_date": dd_trough_date}


def monthly_returns(nav, start=START):
    nav = nav[nav.index >= start].dropna()
    if len(nav) < 2: return pd.Series(dtype=float)
    monthly = nav.resample("ME").last()
    monthly_ret = monthly.pct_change().fillna(monthly.iloc[0]/nav.iloc[0] - 1)
    return monthly_ret


def main():
    today = dt.date.today()

    # Auto-detect tag
    tag = "mid"
    if len(sys.argv) > 1: tag = sys.argv[1]
    else:
        if today.month >= 8: tag = "final"
        elif today.month >= 6: tag = "mid"

    md = []
    md.append(f"# Paper-Trade MILESTONE Report — {tag.upper()}\n")
    md.append(f"*Generated: {today.strftime('%Y-%m-%d')}*")
    md.append(f"*Window: {START.date()} → {today}* ({(pd.Timestamp(today)-START).days} days)\n")

    # ========== A. Per-system cumulative stats vs backtest ==========
    md.append("## A. Realized vs Backtest expectation\n")
    md.append("| Sys | Name | Realized CAGR | Backtest FULL/OOS | Realized DD | Backtest DD | Realized Sharpe | Backtest Sharpe | Verdict |")
    md.append("|---|---|---:|---:|---:|---:|---:|---:|---|")
    all_stats = {}
    for key, name, log_path, tx_path, bt in SYSTEMS:
        nav = load_nav(log_path)
        if nav is None: continue
        s = stats_full(nav)
        if s is None: continue
        all_stats[key] = s
        verdict = "🟢" if s["cagr"]*100 >= bt["backtest_full_cagr"]*0.5 else "🟡" if s["cagr"]*100 > 0 else "🔴"
        md.append(f"| **{key}** | {name} | {s['cagr']*100:+.2f}% | "
                  f"{bt['backtest_full_cagr']:.2f}% / {bt['backtest_oos_cagr']:.2f}% | "
                  f"{s['dd']*100:+.2f}% | {bt['backtest_full_dd']:.2f}% | "
                  f"{s['sharpe']:+.2f} | {bt['backtest_full_sharpe']:.2f} | {verdict} |")
    md.append("")

    # ========== B. Monthly breakdown per system ==========
    md.append("## B. Monthly returns per system\n")
    monthly_data = {key: monthly_returns(load_nav(log_path)) for key,_,log_path,_,_ in SYSTEMS if load_nav(log_path) is not None}
    if monthly_data:
        all_months = sorted(set().union(*[m.index for m in monthly_data.values()]))
        cols = ["Month"] + [k for k,_,_,_,_ in SYSTEMS if k in monthly_data]
        md.append("| " + " | ".join(cols) + " |")
        md.append("|" + "|".join(["---"]*len(cols)) + "|")
        for m in all_months:
            row = [m.strftime("%Y-%m")]
            for key,_,_,_,_ in SYSTEMS:
                if key not in monthly_data: continue
                if m in monthly_data[key].index:
                    row.append(f"{monthly_data[key][m]*100:+.2f}%")
                else:
                    row.append("—")
            md.append("| " + " | ".join(row) + " |")
    md.append("")

    # ========== C. V5 vs V4 Kelly Q2 verdict ==========
    if "V4" in all_stats and "V5" in all_stats:
        v4, v5 = all_stats["V4"], all_stats["V5"]
        d_ret = (v5["ret"] - v4["ret"]) * 100
        d_dd  = (v5["dd"] - v4["dd"]) * 100
        d_sh  = v5["sharpe"] - v4["sharpe"]
        d_calmar = v5["calmar"] - v4["calmar"]
        md.append("## C. V5 (Kelly Q2 overlay) vs V4 (baseline ensemble) — FINAL VERDICT\n")
        md.append(f"- Realized ΔRet:    **{d_ret:+.2f}pp**  (backtest expected: +1pp FULL / +4pp OOS)")
        md.append(f"- Realized ΔDD:     **{d_dd:+.2f}pp**   (backtest expected: -4pp wider; gate: ≥ -6pp)")
        md.append(f"- Realized ΔSharpe: **{d_sh:+.2f}**     (backtest expected: ≈ flat)")
        md.append(f"- Realized ΔCalmar: **{d_calmar:+.2f}** (backtest expected: -0.5)")

        if d_ret > 1.0 and d_dd > -6:
            verdict = "🟢 **GREEN — Q2 alpha confirmed, deploy to production**"
        elif d_ret > 0 and d_dd > -8:
            verdict = "🟡 **YELLOW — Q2 modestly positive, continue paper trade or partial deploy**"
        elif d_ret < -2 or d_dd < -10:
            verdict = "🔴 **RED — Q2 hurts performance, revert to V4 baseline**"
        else:
            verdict = "🟡 **YELLOW — mixed signal, hold position**"
        md.append(f"\n**Final verdict: {verdict}**")
        md.append("")

    # ========== D. Trade activity per system ==========
    md.append("## D. Trade activity (transactions count)\n")
    md.append("| Sys | Total tx | Stock tx | ETF tx | ETF turnover (B) |")
    md.append("|---|---:|---:|---:|---:|")
    for key, name, _, tx_path, _ in SYSTEMS:
        tx = load_tx(tx_path)
        if tx is None: continue
        tx_in_window = tx[tx["ymd"] >= START]
        stock_tx = tx_in_window[tx_in_window["play_type"] != "ETF_PARK"] if "play_type" in tx_in_window.columns else tx_in_window
        etf_tx = tx_in_window[tx_in_window["play_type"] == "ETF_PARK"] if "play_type" in tx_in_window.columns else pd.DataFrame()
        etf_turn = (etf_tx["buy_amount"].sum() + etf_tx["sell_amount"].sum()) / 1e9 if not etf_tx.empty else 0
        md.append(f"| **{key}** | {len(tx_in_window)} | {len(stock_tx)} | {len(etf_tx)} | {etf_turn:.2f}B |")
    md.append("")

    # ========== E. Recommendation ==========
    md.append("## E. Recommendation\n")
    if all_stats:
        ranked = sorted(all_stats.items(), key=lambda kv: kv[1]["sharpe"], reverse=True)
        md.append("**Ranking by realized Sharpe (live data):**")
        for i, (k, s) in enumerate(ranked, 1):
            md.append(f"  {i}. **{k}** — CAGR {s['cagr']*100:+.2f}% / Sharpe {s['sharpe']:+.2f} / DD {s['dd']*100:+.2f}%")
        md.append("")
        top = ranked[0][0]
        md.append(f"**Lead candidate after {tag} milestone: {top}**")
        if tag == "final":
            md.append(f"\n→ **Deploy {top} to real NAV for production starting Sept 2026.**")
        else:
            md.append(f"\n→ Continue paper trade through Aug 31, monitor V5 vs V4 gap.")
    md.append("")

    # ========== Save ==========
    out_path = os.path.join(WORKDIR, "data",
                            f"papertrade_milestone_{tag}_{today.strftime('%Y-%m-%d')}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"Wrote {out_path}")

    print("\n" + "="*80)
    print(f" {tag.upper()} MILESTONE REPORT — {today}")
    print("="*80)
    for k, s in all_stats.items():
        print(f" {k}  CAGR {s['cagr']*100:+6.2f}%  DD {s['dd']*100:+6.2f}%  Sharpe {s['sharpe']:+.2f}")
    print("="*80)


if __name__ == "__main__":
    main()
