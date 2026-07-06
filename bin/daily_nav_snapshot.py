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


def unsettled_sell_receivable(account, dates, asof_date):
    """T+2 áp dụng CẢ 2 CHIỀU: mua tạo khoản phải trả (đã thấy `totalCash` âm ngay lúc đặt
    lệnh — double-buy 2026-07-02), NHƯNG bán tạo khoản phải thu KHÔNG được `totalCash` phản
    ánh cho đến khi thật sự settle ở T+2 (xác nhận thực nghiệm 2026-07-06: sau khi bán
    710,5tr VND, balances API vẫn báo `totalCash` y hệt hôm trước — không có field "tiền
    chờ về" nào trong payload). Thiếu bước này, NAV tính = cổ phiếu còn lại + cash hiện tại
    sẽ hụt đúng bằng tiền bán chưa settle → hiện tượng "NAV rớt -30%" giả ngay ngày trim
    (bug tìm thấy 2026-07-06, xem kb/INCIDENTS.md).

    Cộng lại phần bán trong ≤2 phiên giao dịch gần nhất (kể cả asof) làm khoản phải thu.
    Dùng `dates` (các phiên có journal, đã lọc trước) làm proxy lịch giao dịch thật — chấp
    nhận rủi ro nhỏ nếu có phiên KHÔNG giao dịch xen giữa (như 07-03 HOLD) làm lệch 1 phiên,
    nhưng phiên đó vốn không có lệnh bán nào nên không ảnh hưởng thực tế.
    """
    recent = [d for d in dates if d <= asof_date][-2:]
    total = 0.0
    detail = {}
    for d in recent:
        path = os.path.join(EXEC_DIR, f"exec_{account}_{d}_journal.csv")
        if not os.path.exists(path):
            continue
        latest_by_child = {}
        with open(path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("event") != "FILL":
                    continue
                child_oid = row.get("child_oid")
                if str(row.get("side") or "").lower() != "sell":
                    continue
                ts = row.get("ts", "")
                prev = latest_by_child.get(child_oid)
                if prev is None or ts >= prev[0]:
                    latest_by_child[child_oid] = (ts, float(row.get("qty") or 0),
                                                   float(row.get("price") or 0))
        day_total = sum(qty * price for _, qty, price in latest_by_child.values())
        if day_total:
            detail[d] = day_total
            total += day_total
    return total, detail


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
    raw_pending_receivable, pending_detail = unsettled_sell_receivable(args.account, dates, args.date)

    hist_path, hist_rows = load_history(args.account)
    prev_nav = None
    prev_debt = None
    for row in hist_rows:
        if row["date"] < args.date:
            prev_nav = float(row["nav"])
            prev_debt = float(row.get("margin_debt") or 0)
    if prev_nav is None:
        prev_nav = args.starting_capital

    # Margin bị trừ THẲNG từ tiền bán ngay khi khớp (không đợi T+2) — quan sát thực tế
    # 2026-07-06: dư nợ margin giảm 409.863.737 -> 0 CÙNG NGÀY với lệnh bán 710.675.000,
    # trong khi totalCash gần như không đổi (không có khoản "tiền chờ về" nào lộ diện
    # trong payload balances). Suy luận: phần bán dùng để TRẢ NỢ được ghi nhận ngay (không
    # phải chờ T+2), chỉ phần VƯỢT nợ mới thực sự là tiền chờ T+2 chưa vào totalCash.
    # Đây là SUY LUẬN dựa trên số liệu quan sát (nợ giảm đúng bằng phần này), KHÔNG phải
    # tài liệu chính thức DNSE xác nhận cơ chế netting — cần đối chiếu lại khi settle xong
    # thật (T+2 = 2026-07-08) để xác nhận đúng/sai. Xem kb/INCIDENTS.md.
    debt_extinguished_today = max(0.0, (prev_debt or 0) - debt)
    adjusted_pending_receivable = max(0.0, raw_pending_receivable - debt_extinguished_today)
    nav = mtm_stock + cash - debt + adjusted_pending_receivable
    nav_is_estimate = adjusted_pending_receivable > 0

    day_change = nav - prev_nav
    day_change_pct = day_change / prev_nav * 100 if prev_nav else 0

    hist_rows = [row for row in hist_rows if row["date"] != args.date]
    hist_rows.append({"date": args.date, "nav": f"{nav:.0f}", "mtm_stock": f"{mtm_stock:.0f}",
                       "cash": f"{cash:.0f}", "margin_debt": f"{debt:.0f}",
                       "pending_sell_receivable": f"{adjusted_pending_receivable:.0f}",
                       "nav_is_estimate": str(nav_is_estimate),
                       "balance_ts": bal["ts"]})
    hist_rows.sort(key=lambda r: r["date"])
    with open(hist_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "nav", "mtm_stock", "cash", "margin_debt",
                                          "pending_sell_receivable", "nav_is_estimate", "balance_ts"])
        w.writeheader()
        w.writerows(hist_rows)

    since_inception = nav - args.starting_capital
    since_inception_pct = since_inception / args.starting_capital * 100

    lines = [
        f"💰 **NAV {args.date}: {nav:,.0f} VND** ({day_change:+,.0f} VND, {day_change_pct:+.2f}% so với hôm trước)"
        + ("  ⚠️ ƯỚC TÍNH" if nav_is_estimate else ""),
        f"   Cổ phiếu {mtm_stock:,.0f} · Tiền mặt {cash:,.0f} · Nợ margin {debt:,.0f}",
    ]
    if raw_pending_receivable:
        lines.append(f"   + Tiền bán chờ T+2 về ({', '.join(pending_detail)}): "
                     f"{raw_pending_receivable:,.0f} tổng — CHƯA vào `totalCash`. "
                     f"{'Trong đó ước tính ' + format(debt_extinguished_today, ',.0f') + 'đ đã dùng trả nợ margin ngay (nợ giảm cùng ngày), phần còn lại ' + format(adjusted_pending_receivable, ',.0f') + 'đ mới thực sự đang chờ T+2.' if debt_extinguished_today else ''}")
    if nav_is_estimate:
        lines.append("   ⚠️ NAV trên là ƯỚC TÍNH dựa trên suy luận nợ margin được trả ngay từ tiền bán "
                     "(quan sát được, chưa xác nhận bằng tài liệu DNSE) — cần đối chiếu lại khi "
                     "settle T+2 xong thật (2026-07-08) để xác nhận đúng/sai.")
    lines.append(f"   Từ go-live: {since_inception:+,.0f} VND ({since_inception_pct:+.2f}%)")
    if debt > 1_000_000:
        lines.append(f"   ⚠️ Đang có nợ margin thật {debt:,.0f} VND — theo dõi lãi vay tích lũy.")
    print("\n".join(lines))

    out = {"account": args.account, "date": args.date, "nav": nav, "nav_is_estimate": nav_is_estimate,
           "mtm_stock": mtm_stock, "cash": cash, "margin_debt": debt,
           "raw_pending_sell_receivable": raw_pending_receivable,
           "debt_extinguished_today_est": debt_extinguished_today,
           "adjusted_pending_sell_receivable": adjusted_pending_receivable,
           "pending_sell_detail": pending_detail, "prev_nav": prev_nav, "day_change": day_change,
           "day_change_pct": day_change_pct, "since_inception": since_inception,
           "since_inception_pct": since_inception_pct, "balance_ts": bal["ts"],
           "source": "verify_account_snapshot.py (fills) + dnse_raw balances (real broker API)"}
    with open(os.path.join(EXEC_DIR, f"nav_snapshot_{args.account}_{args.date}.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
