#!/usr/bin/env python3
"""reconcile_equity.py --account SpaceX --starting-capital 1000000000 \
       --snapshot data/execution_logs/verified_snapshot_SpaceX_2026-07-03.json \
       --balance-raw data/execution_logs/dnse_raw_2026-07-03.jsonl

Kiểm tra đẳng thức kế toán 2 chiều độc lập (theo yêu cầu user 2026-07-03):

    Vốn ban đầu + Lãi/lỗ chưa thực hiện - Phí giao dịch - Lãi vay margin
        ==  NAV thị trường (cổ phiếu) + Tiền mặt - Nợ vay margin

Vế trái tính từ đường P&L (giá vốn thật x khối lượng, xem verify_account_snapshot.py).
Vế phải tính từ đường bảng cân đối (số dư THẬT đọc trực tiếp từ balances API của DNSE,
trong dnse_raw_*.jsonl, kind=balances — không phải file tóm tắt trung gian).

Nếu 2 vế không khớp trong ngưỡng dung sai (mặc định 0.05% NAV, đủ rộng cho phí giao dịch
chưa itemize chi tiết) -> in cảnh báo rõ ràng, KHÔNG tự làm tròn/che giấu chênh lệch.
"""
import argparse
import json
import sys


def latest_balance(raw_path):
    latest = None
    with open(raw_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("kind") == "balances":
                latest = rec
    return latest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--account", required=True)
    ap.add_argument("--starting-capital", type=float, required=True)
    ap.add_argument("--snapshot", required=True,
                     help="output file of verify_account_snapshot.py")
    ap.add_argument("--balance-raw", required=True,
                     help="dnse_raw_*.jsonl containing a fresh kind=balances record")
    ap.add_argument("--trading-fees", type=float, default=None,
                     help="tổng phí giao dịch thật nếu đã biết; bỏ trống = không trừ, chỉ nêu residual")
    ap.add_argument("--tolerance-pct", type=float, default=0.05,
                     help="ngưỡng dung sai %% NAV cho residual chưa giải thích được")
    args = ap.parse_args()

    snap = json.load(open(args.snapshot, encoding="utf-8"))
    bal_rec = latest_balance(args.balance_raw)
    if bal_rec is None:
        print(f"❌ Không tìm thấy record kind=balances trong {args.balance_raw} — "
              f"KHÔNG thể đối chiếu.", file=sys.stderr)
        sys.exit(2)

    stock = bal_rec["payload"]["stock"]
    cash = stock["totalCash"]
    debt = stock["totalDebt"]
    accrued_fee = stock.get("depositFeeAmount", 0)
    bal_ts = bal_rec["ts"]

    unrealized_pnl = snap["total_unrealized_pnl"]
    mtm_stock = snap["total_mtm_value"]

    fees = args.trading_fees or 0.0

    # Vế trái: đường P&L
    lhs = args.starting_capital + unrealized_pnl - fees - accrued_fee
    # Vế phải: đường bảng cân đối (số dư THẬT từ broker)
    rhs = mtm_stock + cash - debt

    residual = lhs - rhs
    tolerance_vnd = rhs * args.tolerance_pct / 100.0
    within_tolerance = abs(residual) <= abs(tolerance_vnd) + 5_000_000  # sàn tuyệt đối nhỏ cho phí lặt vặt

    print(f"== Reconcile equity — {args.account} ==")
    print(f"Nguồn balance THẬT: {args.balance_raw} (ts={bal_ts}, kind=balances)")
    print(f"Nguồn P&L THẬT: {args.snapshot}")
    print()
    print(f"VẾ TRÁI  (Vốn ban đầu + Lãi/lỗ - phí - lãi vay):")
    print(f"  Vốn ban đầu:           {args.starting_capital:>16,.0f}")
    print(f"  + Lãi/lỗ chưa thực hiện:{unrealized_pnl:>+16,.0f}")
    print(f"  - Phí giao dịch:       {-fees:>16,.0f}  {'(chưa có số thật — nhập --trading-fees nếu có)' if not args.trading_fees else ''}")
    print(f"  - Phí/lãi margin tích lũy: {-accrued_fee:>12,.0f}")
    print(f"  = VẾ TRÁI:             {lhs:>16,.0f}")
    print()
    print(f"VẾ PHẢI  (NAV thị trường + Tiền mặt - Nợ margin, số THẬT từ broker):")
    print(f"  Giá trị cổ phiếu (MTM):{mtm_stock:>16,.0f}")
    print(f"  + Tiền mặt:            {cash:>16,.0f}")
    print(f"  - Nợ vay margin:       {-debt:>16,.0f}")
    print(f"  = VẾ PHẢI:             {rhs:>16,.0f}")
    print()
    print(f"CHÊNH LỆCH (trái - phải): {residual:>+16,.0f}  ({residual/rhs*100:+.3f}% của vế phải)")
    print(f"Ngưỡng dung sai: ±{args.tolerance_pct}% NAV + 5tr VND sàn tuyệt đối")
    print(f"KẾT LUẬN: {'✅ KHỚP trong ngưỡng dung sai' if within_tolerance else '❌ LỆCH VƯỢT NGƯỠNG — cần điều tra thêm'}")

    result = {
        "account": args.account, "balance_ts": bal_ts,
        "starting_capital": args.starting_capital, "unrealized_pnl": unrealized_pnl,
        "trading_fees_used": fees, "accrued_margin_fee": accrued_fee,
        "lhs_pnl_path": lhs, "mtm_stock": mtm_stock, "cash": cash, "margin_debt": debt,
        "rhs_balance_sheet_path": rhs, "residual": residual,
        "residual_pct_of_rhs": residual / rhs * 100, "within_tolerance": within_tolerance,
    }
    out_path = args.snapshot.replace("verified_snapshot", "reconcile_equity")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\nGhi ra: {out_path}")
    if not within_tolerance:
        sys.exit(1)


if __name__ == "__main__":
    main()
