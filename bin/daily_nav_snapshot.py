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


def today_sell_value(account, date):
    """Tổng giá trị lệnh BÁN đã khớp trong ngày (dùng để cảnh báo balance có thể còn stale
    khi so với biến động cash — xem ghi chú ở latest_balance)."""
    path = os.path.join(EXEC_DIR, f"exec_{account}_{date}_journal.csv")
    if not os.path.exists(path):
        return 0.0
    latest_by_child = {}
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("event") != "FILL" or str(row.get("side") or "").lower() != "sell":
                continue
            child_oid = row.get("child_oid")
            ts = row.get("ts", "")
            prev = latest_by_child.get(child_oid)
            if prev is None or ts >= prev[0]:
                latest_by_child[child_oid] = (ts, float(row.get("qty") or 0),
                                               float(row.get("price") or 0))
    return sum(qty * price for _, qty, price in latest_by_child.values())


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

    # NAV = Tiền + Cổ phiếu − Nợ (đúng như app DNSE hiển thị "Tài sản ròng" — user xác nhận
    # 2026-07-06 bằng ảnh chụp thật, khớp chính xác đến từng đồng: 709.276.086 + 683.590.000
    # − 409.863.737 = 983.002.349). KHÔNG cần tự ước tính "tiền bán chờ T+2" cộng riêng —
    # `totalCash` của DNSE RỐT CUỘC cũng tự cộng khoản này vào, chỉ là CẦN THỜI GIAN để hệ
    # thống broker cập nhật (có vẻ qua 1 đợt đối soát cuối ngày, không tức thời sau khớp
    # lệnh). Bài học rút ra CÙNG NGÀY (xem kb/INCIDENTS.md): lần đọc balance sớm hơn cùng
    # ngày (giữa phiên chiều) từng cho totalDebt=0 SAI — không phải do nợ được trả ngay như
    # suy luận ban đầu, mà đơn giản là dữ liệu balance LÚC ĐÓ CHƯA CẬP NHẬT XONG (stale).
    # Lần đọc sau (cuối ngày) mới đúng, khớp ảnh chụp thật. => KHÔNG tự suy luận/mô hình hoá
    # thêm gì — chỉ cần đảm bảo balance record dùng để tính NAV là bản MỚI NHẤT trong ngày
    # (đã tự động nhờ latest_balance() lấy dòng cuối), và cảnh báo rõ nếu có dấu hiệu stale.
    nav = mtm_stock + cash - debt

    sell_today = today_sell_value(args.account, args.date)
    stale_warning = None
    if sell_today > 1_000_000 and cash < sell_today * 0.5:
        stale_warning = (f"Hôm nay có bán {sell_today:,.0f}đ nhưng tiền mặt ({cash:,.0f}đ) "
                         f"không phản ánh tương xứng — balance có thể CHƯA cập nhật xong "
                         f"(đối soát cuối ngày), nên chạy lại script này muộn hơn/ngày mai "
                         f"để lấy số chính xác trước khi tin tưởng hoàn toàn.")

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
        w = csv.DictWriter(f, fieldnames=["date", "nav", "mtm_stock", "cash", "margin_debt",
                                          "balance_ts"])
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
    if stale_warning:
        lines.append(f"   ⚠️ {stale_warning}")
    print("\n".join(lines))

    out = {"account": args.account, "date": args.date, "nav": nav,
           "mtm_stock": mtm_stock, "cash": cash, "margin_debt": debt,
           "stale_warning": stale_warning, "prev_nav": prev_nav, "day_change": day_change,
           "day_change_pct": day_change_pct, "since_inception": since_inception,
           "since_inception_pct": since_inception_pct, "balance_ts": bal["ts"],
           "source": "verify_account_snapshot.py (fills) + dnse_raw balances (real broker API, "
                     "chọn bản GHI CUỐI CÙNG trong ngày — balance có thể cần thời gian đối soát "
                     "cuối phiên mới phản ánh đúng, xem cảnh báo staleness nếu có)"}
    with open(os.path.join(EXEC_DIR, f"nav_snapshot_{args.account}_{args.date}.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
