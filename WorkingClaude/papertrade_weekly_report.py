# -*- coding: utf-8 -*-
"""Weekly paper-trade summary — runs every Sunday after daily refresh.

Reads daily logs from all 5 systems + VNINDEX, produces a focused weekly summary:
  - This week's NAV change per system (5 trading days typical)
  - Cumulative since paper-trade start (2026-04-01)
  - V5 vs V4 watch (Kelly Q2 overlay tracking)
  - Top movers + alerts

Writes:
  data/papertrade_weekly_YYYY-MM-DD.md   — week summary
  data/papertrade_weekly_latest.md       — symlink/copy of latest week
"""
import os, sys, io, datetime as dt
from pathlib import Path
import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)
from simulate_holistic_nav import bq

SYSTEMS = [
    ("V1", "V11 Song Sinh + TQ34b",          "data/pt_v11_tq34b_logs.csv"),
    ("V2", "V12 Âm Dương + TQ34b",           "data/pt_v12_tq34b_logs.csv"),
    ("V3", "V12 Âm Dương + LIVE Tinh Tế",    "data/pt_v12_live_logs.csv"),
    ("V4", "V12.1 Ensemble (M1+M3r AND-HOLD)","data/pt_v121_ens_logs.csv"),
    ("V5", "V4 + Kelly Q2 NEUTRAL{1.0}",      "data/pt_v121_ens_q2_logs.csv"),
]
START = pd.Timestamp("2026-04-01")


def load_nav(path):
    full = os.path.join(WORKDIR, path)
    if not os.path.exists(full): return None
    df = pd.read_csv(full, parse_dates=["ymd"]).sort_values("ymd")
    return df.set_index("ymd")["nav"]


def stats(nav, window_start=None):
    nav = nav.dropna()
    if window_start is not None:
        nav = nav[nav.index >= window_start]
    if len(nav) < 2: return None
    ret = nav.iloc[-1]/nav.iloc[0] - 1
    peak = nav.cummax(); dd = ((nav-peak)/peak).min()
    daily = nav.pct_change().dropna()
    days = (nav.index[-1] - nav.index[0]).days
    cagr = (1+ret)**(365.25/max(days,1)) - 1 if days > 0 else 0
    vol_ann = daily.std() * np.sqrt(252) if len(daily) > 0 else 0
    sharpe = (daily.mean()*252)/vol_ann if vol_ann > 0 else 0
    return {"start": nav.index[0], "end": nav.index[-1],
            "first_nav": nav.iloc[0], "last_nav": nav.iloc[-1],
            "ret": ret, "cagr": cagr, "dd": dd, "sharpe": sharpe}


def main():
    today = dt.date.today()
    week_start = pd.Timestamp(today - dt.timedelta(days=7))

    md = []
    md.append(f"# Paper-Trade Weekly Summary — {today.strftime('%Y-%m-%d')}\n")
    md.append(f"*Window this week: {week_start.date()} → {today}*")
    md.append(f"*Cumulative since: {START.date()}* ({(pd.Timestamp(today)-START).days} days)\n")

    # ========== Cumulative table ==========
    md.append("## Cumulative since 2026-04-01\n")
    md.append("| System | Last NAV | Total Ret | CAGR | MaxDD | Sharpe |")
    md.append("|---|---:|---:|---:|---:|---:|")
    cum_stats = {}
    for key, name, path in SYSTEMS:
        nav = load_nav(path)
        if nav is None: continue
        s = stats(nav, START)
        if s is None: continue
        cum_stats[key] = s
        md.append(f"| **{key}** {name} | {s['last_nav']/1e9:.3f}B | "
                  f"{s['ret']*100:+.2f}% | {s['cagr']*100:+.2f}% | "
                  f"{s['dd']*100:+.2f}% | {s['sharpe']:+.2f} |")

    # VNI bench
    try:
        vni = bq(f"SELECT t.time, t.Close FROM tav2_bq.ticker AS t "
                 f"WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START.date()}' AND DATE '{today}' "
                 f"ORDER BY t.time")
        vni["time"] = pd.to_datetime(vni["time"])
        vni_nav = (vni.set_index("time")["Close"] / vni["Close"].iloc[0]) * 50e9
        s = stats(vni_nav, START)
        if s:
            md.append(f"| **VNI** Buy & Hold | {s['last_nav']/1e9:.3f}B | "
                      f"{s['ret']*100:+.2f}% | {s['cagr']*100:+.2f}% | "
                      f"{s['dd']*100:+.2f}% | {s['sharpe']:+.2f} |")
    except Exception as e:
        md.append(f"(VNI fetch failed: {e})")
    md.append("")

    # ========== This week ==========
    md.append("## This week (last 7 days)\n")
    md.append("| System | Week start NAV | Week end NAV | Week Ret | Week DD |")
    md.append("|---|---:|---:|---:|---:|")
    for key, name, path in SYSTEMS:
        nav = load_nav(path)
        if nav is None: continue
        w = stats(nav, week_start)
        if w is None: continue
        md.append(f"| **{key}** | {w['first_nav']/1e9:.3f}B | {w['last_nav']/1e9:.3f}B | "
                  f"{w['ret']*100:+.2f}% | {w['dd']*100:+.2f}% |")
    md.append("")

    # ========== V5 vs V4 watch ==========
    if "V4" in cum_stats and "V5" in cum_stats:
        v4, v5 = cum_stats["V4"], cum_stats["V5"]
        d_ret = (v5["ret"] - v4["ret"]) * 100
        d_dd  = (v5["dd"] - v4["dd"]) * 100
        d_sh  = v5["sharpe"] - v4["sharpe"]
        md.append("## V5 vs V4 — Kelly Q2 overlay watch\n")
        md.append(f"- **ΔRet (V5−V4)**: {d_ret:+.2f}pp  (backtest expect: +1pp FULL / +4pp OOS over 12y)")
        md.append(f"- **ΔDD  (V5−V4)**: {d_dd:+.2f}pp   (gate: ≥ -6pp; revert if worse)")
        md.append(f"- **ΔSharpe**:     {d_sh:+.2f}     (backtest expect ≈ flat)")
        if d_dd < -6:
            md.append(f"\n⚠️ **ALERT**: V5 DD widening > 6pp vs V4. Review needed.")
        elif d_ret < -3:
            md.append(f"\n⚠️ **ALERT**: V5 trailing V4 by > 3pp. Q2 overlay may not be working live.")
        else:
            md.append(f"\n🟢 V5 within expected band.")
        md.append("")

    # ========== Save ==========
    out_path = os.path.join(WORKDIR, "data", f"papertrade_weekly_{today.strftime('%Y-%m-%d')}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"Wrote {out_path}")

    # Also save as "latest"
    latest_path = os.path.join(WORKDIR, "data", "papertrade_weekly_latest.md")
    with open(latest_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"Wrote {latest_path}")

    # Console
    print("\n" + "="*70)
    print(f" WEEKLY SUMMARY — {today}")
    print("="*70)
    for key in ["V1","V2","V3","V4","V5"]:
        if key not in cum_stats: continue
        s = cum_stats[key]
        print(f" {key}  cum ret {s['ret']*100:+6.2f}%  CAGR {s['cagr']*100:+6.2f}%  DD {s['dd']*100:+6.2f}%")
    print("="*70)


if __name__ == "__main__":
    main()
