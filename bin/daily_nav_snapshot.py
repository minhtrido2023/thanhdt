#!/usr/bin/env python3
"""daily_nav_snapshot.py --account SpaceX --date 2026-07-03 [--starting-capital 1000000000]

Tính NAV thật cuối ngày (dùng chung nguyên tắc với verify_account_snapshot.py /
reconcile_equity.py — KHÔNG đọc field ước tính, chỉ dùng fill thật + giá BQ + balance API
thật) và ghi vào lịch sử `data/execution_logs/nav_history_{account}.csv` để daily/weekly/
monthly report đều đọc từ MỘT nguồn duy nhất, nhất quán.

In ra 1 đoạn tóm tắt ngắn (dùng cho daily report — đơn giản, chỉ NAV + biến động) và ghi
JSON chi tiết ra `data/execution_logs/nav_snapshot_{account}_{date}.json`.
"""
import argparse
import csv
import glob
import json
import os
import subprocess
import sys

WC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXEC_DIR = os.path.join(WC_ROOT, "data", "execution_logs")
MIKE_BIN = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE_TMPL = os.path.join(EXEC_DIR, "nav_history_{account}.csv")


def trading_dates_with_fills(account, upto_date):
    dates = []
    for path in sorted(glob.glob(os.path.join(EXEC_DIR, f"exec_{account}_*_journal.csv"))):
        base = os.path.basename(path)
        date = base[len(f"exec_{account}_"):-len("_journal.csv")]
        if date <= upto_date:
            dates.append(date)
    return dates


def latest_balance(raw_path):
    if not os.path.exists(raw_path):
        return None
    latest = None
    with open(raw_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("kind") == "balances":
                latest = rec
    return latest


def load_history(account):
    path = HISTORY_FILE_TMPL.format(account=account)
    rows = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    return path, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--account", required=True)
    ap.add_argument("--account-no", default=None)
    ap.add_argument("--date", required=True)
    ap.add_argument("--starting-capital", type=float, default=1_000_000_000)
    args = ap.parse_args()

    dates = trading_dates_with_fills(args.account, args.date)
    if not dates:
        print(f"ℹ️ [{args.date}] Chưa có ngày giao dịch nào cho {args.account} — bỏ qua NAV snapshot.")
        return 0

    snapshot_out = os.path.join(EXEC_DIR, f"verified_snapshot_{args.account}_{args.date}.json")
    cmd = [sys.executable, os.path.join(MIKE_BIN, "verify_account_snapshot.py"),
           "--account", args.account, "--dates", ",".join(dates), "--asof", args.date,
           "--out", snapshot_out]
    if args.account_no:
        cmd += ["--account-no", args.account_no]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode not in (0,):
        print(f"❌ verify_account_snapshot.py thất bại (rc={r.returncode}) — KHÔNG tính NAV, "
              f"tránh báo số chưa xác minh.\nstderr: {r.stderr.strip()}", file=sys.stderr)
        return r.returncode

    snap = json.load(open(snapshot_out, encoding="utf-8"))
    mtm_stock = snap["total_mtm_value"]

    raw_path = os.path.join(EXEC_DIR, f"dnse_raw_{args.date}.jsonl")
    bal = latest_balance(raw_path)
    if bal is None:
        print(f"⚠️ [{args.date}] Không có record balances thật trong {raw_path} — "
              f"KHÔNG tính NAV (tránh dùng số ước tính/cũ).", file=sys.stderr)
        return 2

    stock = bal["payload"]["stock"]
    cash, debt = stock["totalCash"], stock["totalDebt"]
    nav = mtm_stock + cash - debt

    hist_path, hist_rows = load_history(args.account)
    prev_nav = None
    for row in hist_rows:
        if row["date"] < args.date:
            prev_nav = float(row["nav"])
    if prev_nav is None:
        prev_nav = args.starting_capital

    day_change = nav - prev_nav
    day_change_pct = day_change / prev_nav * 100 if prev_nav else 0

    hist_rows = [row for row in hist_rows if row["date"] != args.date]
    hist_rows.append({"date": args.date, "nav": f"{nav:.0f}", "mtm_stock": f"{mtm_stock:.0f}",
                       "cash": f"{cash:.0f}", "margin_debt": f"{debt:.0f}",
                       "balance_ts": bal["ts"]})
    hist_rows.sort(key=lambda r: r["date"])
    with open(hist_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "nav", "mtm_stock", "cash", "margin_debt", "balance_ts"])
        w.writeheader()
        w.writerows(hist_rows)

    since_inception = nav - args.starting_capital
    since_inception_pct = since_inception / args.starting_capital * 100

    lines = [
        f"💰 **NAV {args.date}: {nav:,.0f} VND** ({day_change:+,.0f} VND, {day_change_pct:+.2f}% so với hôm trước)",
        f"   Cổ phiếu {mtm_stock:,.0f} · Tiền mặt {cash:,.0f} · Nợ margin {debt:,.0f}",
        f"   Từ go-live: {since_inception:+,.0f} VND ({since_inception_pct:+.2f}%)",
    ]
    if debt > 1_000_000:
        lines.append(f"   ⚠️ Đang có nợ margin thật {debt:,.0f} VND — theo dõi lãi vay tích lũy.")
    print("\n".join(lines))

    out = {"account": args.account, "date": args.date, "nav": nav, "mtm_stock": mtm_stock,
           "cash": cash, "margin_debt": debt, "prev_nav": prev_nav, "day_change": day_change,
           "day_change_pct": day_change_pct, "since_inception": since_inception,
           "since_inception_pct": since_inception_pct, "balance_ts": bal["ts"],
           "source": "verify_account_snapshot.py (fills) + dnse_raw balances (real broker API)"}
    with open(os.path.join(EXEC_DIR, f"nav_snapshot_{args.account}_{args.date}.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
