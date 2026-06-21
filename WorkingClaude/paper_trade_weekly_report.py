# -*- coding: utf-8 -*-
"""Weekly paper-trade Telegram report.

Sends a summary of paper_trade_entries.csv + paper_trade_exits.csv to Telegram.
Compares live metrics with backtest baseline (memory: layer3_rules_backtest.md):
  - TOP30 expected miss 0.03%, per-trade lift +0.90pp
  - MIDCAP        miss 0.40%,        lift +1.18pp
  - PENNY         miss 1.60%,        lift +1.73pp

Designed for Windows Task Scheduler — call every Friday after the daily run.

Usage:
  python paper_trade_weekly_report.py            # build + send
  python paper_trade_weekly_report.py --dry-run  # build, print, don't send
"""
import os
import sys
import io
import argparse
from datetime import date, timedelta

import pandas as pd

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)

ENTRIES_FILE = os.path.join(WORKDIR, "paper_trade_entries.csv")
EXITS_FILE = os.path.join(WORKDIR, "paper_trade_exits.csv")
LOG_FILE = os.path.join(WORKDIR, "paper_trade_weekly_log.txt")

from telegram_recommend import load_config, send_telegram_text, send_telegram_document


def html_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_report(week_lookback_days: int = 7) -> str:
    today = date.today()
    week_start = today - timedelta(days=week_lookback_days)
    review_date = date(2026, 6, 12)
    days_to_review = (review_date - today).days

    lines = []
    lines.append("<b>📊 Paper-Trade Weekly Report</b>")
    lines.append(f"<i>Tuần: {week_start.isoformat()} → {today.isoformat()}</i>")
    lines.append(f"<i>Review chính thức: {review_date.isoformat()} ({days_to_review}d nữa)</i>")
    lines.append("")

    # ---- Entries ----
    if not os.path.exists(ENTRIES_FILE):
        lines.append("⚠️ Chưa có entries nào được log.")
        return "\n".join(lines)

    e = pd.read_csv(ENTRIES_FILE)
    e["exec_date"] = pd.to_datetime(e["exec_date"]).dt.date

    e_total = e.copy()
    e_week = e[(e["exec_date"] >= week_start) & (e["exec_date"] <= today)].copy()

    # All-time
    lines.append(f"<b>━━ Tổng kể từ 2026-05-12 ━━</b>")
    lines.append(f"Entries: <b>{len(e_total)}</b>")
    if len(e_total):
        miss_rate = e_total["missed"].mean() * 100
        lines.append(f"Miss rate: <b>{miss_rate:.2f}%</b> ({e_total['missed'].sum()}/{len(e_total)})")
        e_total["fill_save_pct"] = (e_total["baseline_open_price"] - e_total["fill_price"]) / e_total["baseline_open_price"] * 100
        # Per rule
        agg = e_total.groupby("rule")["fill_save_pct"].agg(["count", "mean", "median"]).round(3)
        lines.append("")
        lines.append("<b>Fill saving vs OPEN baseline (per rule):</b>")
        lines.append("<pre>")
        lines.append(f"{'rule':<18}{'n':>4}{'mean%':>8}{'med%':>8}")
        for rule, row in agg.iterrows():
            lines.append(f"{rule:<18}{int(row['count']):>4}{row['mean']:>8.3f}{row['median']:>8.3f}")
        lines.append("</pre>")

    # Week
    lines.append("")
    lines.append(f"<b>━━ Tuần này ({len(e_week)} entries) ━━</b>")
    if len(e_week):
        for _, r in e_week.iterrows():
            saving = (r["baseline_open_price"] - r["fill_price"]) / r["baseline_open_price"] * 100
            miss_tag = "❌ MISS" if r["missed"] else "✅ FILL"
            lines.append(
                f"{miss_tag} <b>{html_escape(r['ticker'])}</b> {r['exec_date']} "
                f"{html_escape(r['rule'])} @ {r['fill_price']:.2f} "
                f"(save {saving:+.2f}%)"
            )
    else:
        lines.append("<i>(Không có entry mới tuần này)</i>")

    # ---- Backtest comparison ----
    if len(e_total):
        lines.append("")
        lines.append("<b>━━ So với backtest baseline ━━</b>")
        live_miss = e_total["missed"].mean() * 100
        live_save_mean = e_total["fill_save_pct"].mean()
        # Backtest expected (TOP30-weighted; most picks là COMPOUNDER_BUY = TOP30)
        bt_miss_top30 = 0.03
        bt_lift_top30 = 0.90
        lines.append(f"Live miss rate: <b>{live_miss:.2f}%</b> vs backtest TOP30 <i>{bt_miss_top30}%</i>")
        lines.append(f"Live fill saving (mean): <b>{live_save_mean:+.3f}%</b>")
        lines.append(f"Backtest expected per-trade lift TOP30: <i>+{bt_lift_top30}pp</i>")
        delta = "✅ aligned" if live_save_mean > 0 else "⚠️ inverse"
        lines.append(f"Direction: {delta}")

    # ---- Exits ----
    lines.append("")
    if os.path.exists(EXITS_FILE):
        x = pd.read_csv(EXITS_FILE)
        lines.append(f"<b>━━ Exits hoàn tất: {len(x)} ━━</b>")
        if len(x):
            lines.append(f"Mean net return (rule): <b>{x['net_ret_pct'].mean():+.3f}%</b>")
            lines.append(f"Mean net return (baseline OPEN): <b>{x['baseline_net_ret_pct'].mean():+.3f}%</b>")
            lines.append(f"Mean lift vs baseline: <b>{x['lift_vs_baseline_pp'].mean():+.3f}pp</b>")
            hit = (x["lift_vs_baseline_pp"] > 0).mean() * 100
            lines.append(f"Lift hit rate: <b>{hit:.1f}%</b>")
    else:
        lines.append("<b>━━ Exits ━━</b>")
        lines.append("<i>Chưa có exit (cần đủ 45 phiên hold ~ 2026-07-15)</i>")

    lines.append("")
    lines.append(f"<i>Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</i>")

    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true", help="Build but don't send")
    p.add_argument("--attach-csv", action="store_true", default=True,
                   help="Attach entries+exits CSV (default: True)")
    args = p.parse_args()

    msg = build_report()

    if args.dry_run:
        print(msg)
        return

    cfg = load_config()
    token, chat_id = cfg["bot_token"], cfg["chat_id"]

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{pd.Timestamp.now().isoformat(timespec='seconds')}] Sending weekly report ({len(msg)} chars)\n")

    resp = send_telegram_text(token, chat_id, msg)
    if not resp.get("ok"):
        print(f"ERROR sending text: {resp}")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"  ERROR: {resp}\n")
        sys.exit(1)
    print(f"OK — sent {len(msg)} chars to chat {chat_id}")

    if args.attach_csv:
        for fp, caption in [
            (ENTRIES_FILE, "paper_trade_entries.csv"),
            (EXITS_FILE, "paper_trade_exits.csv"),
        ]:
            if os.path.exists(fp):
                r = send_telegram_document(token, chat_id, fp, caption=caption)
                if r.get("ok"):
                    print(f"  attached: {caption}")
                else:
                    print(f"  attach FAIL {caption}: {r}")


if __name__ == "__main__":
    main()
