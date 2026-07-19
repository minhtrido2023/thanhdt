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

Phí giao dịch (--fee-rate-pct, mặc định 0.075%, xác nhận bởi user 2026-07-03) tự tính từ
tổng giá vốn thật trong snapshot — không cần nhập tay --trading-fees nữa (vẫn có thể override).
Lãi vay margin THẬT lấy từ field depositFeeAmount của balances API (số đã ghi nhận chính thức).
Phần dư (residual) còn lại sau khi trừ phí+lãi thật được so sánh với MỘT ƯỚC TÍNH lãi margin
tích lũy nhưng CHƯA post vào depositFeeAmount (--margin-rate-annual, mặc định 12.5%/năm theo
user cung cấp — CHƯA xác minh với hợp đồng/biểu phí DNSE, chỉ là ước tính) — in ra như một lời
giải thích khả dĩ cho residual, KHÔNG đưa vào đẳng thức chính (giữ đẳng thức chính 100% dữ liệu
thật, ước tính chỉ nằm ở phần diễn giải).

Nếu 2 vế (dùng số THẬT) không khớp trong ngưỡng dung sai (mặc định 0.05% NAV) -> in cảnh báo rõ
ràng, KHÔNG tự làm tròn/che giấu chênh lệch.
"""
import argparse
import json
import sys


def latest_balance(raw_path, account_no=None):
    """Bản ghi 'balances' MỚI NHẤT cho ĐÚNG account_no (file dùng CHUNG cho mọi account cùng
    ngày, xem daily_nav_snapshot.py — cùng bug, cùng fix: nếu account_no được truyền vào mà
    KHÔNG có bản ghi nào khớp, RAISE thay vì âm thầm dùng bản ghi có thể sai account. Phát
    hiện 2026-07-19: bản gốc không lọc account_no ⇒ ZaloPay reconcile từng lấy nhầm cash của
    SpaceX (3.160.463 thay vì 22.465.980 thật), job Taylor_20260719_055139."""
    latest = None
    seen_other_account = False
    with open(raw_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("kind") != "balances":
                continue
            if account_no is not None and rec.get("account_no") not in (None, account_no):
                seen_other_account = True
                continue
            latest = rec
    if latest is None and seen_other_account:
        raise RuntimeError(
            f"{raw_path} có bản ghi balances nhưng KHÔNG bản nào khớp account_no="
            f"{account_no!r} — file này dùng chung cho nhiều account, tránh dùng nhầm.")
    return latest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--account", required=True)
    ap.add_argument("--account-no", default=None,
                     help="account_id thật (vd 0002023347) — BẮT BUỘC truyền hoặc để script tự "
                          "tra secrets/trading_bot_accounts.json theo --account, vì "
                          "--balance-raw dùng CHUNG cho mọi account cùng ngày.")
    ap.add_argument("--starting-capital", type=float, required=True)
    ap.add_argument("--snapshot", required=True,
                     help="output file of verify_account_snapshot.py")
    ap.add_argument("--balance-raw", required=True,
                     help="dnse_raw_*.jsonl containing a fresh kind=balances record")
    ap.add_argument("--trading-fees", type=float, default=None,
                     help="tổng phí giao dịch thật nếu đã biết; bỏ trống = tự tính theo --fee-rate-pct")
    ap.add_argument("--fee-rate-pct", type=float, default=0.075,
                     help="phí giao dịch %% trên tổng giá vốn (mặc định 0.075%%, xác nhận 2026-07-03)")
    ap.add_argument("--margin-rate-annual", type=float, default=0.125,
                     help="lãi suất margin ước tính %%/năm (mặc định 12.5%%, do user cung cấp — "
                          "CHƯA xác minh với DNSE, chỉ dùng để DIỄN GIẢI residual)")
    ap.add_argument("--tolerance-pct", type=float, default=0.05,
                     help="ngưỡng dung sai %% NAV cho residual chưa giải thích được")
    ap.add_argument("--offbook-assets", type=float, default=0.0,
                     help="tài sản off-book user tự báo (vd Trứng vàng DNSE, không lộ qua API) "
                          "asof ngày --balance-raw — cộng vào vế phải để KHÔNG báo residual giả "
                          "khi user đã chuyển tiền rảnh ra ngoài tài khoản giao dịch. Lấy số này "
                          "từ manual_offbook_assets_vnd trong secrets/trading_bot_accounts.json.")
    args = ap.parse_args()

    account_no = args.account_no
    if not account_no:
        import os
        WC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sys.path.insert(0, WC_ROOT)
        from trading_bot.config import load_config, load_accounts
        _match = next((p for p in load_accounts(load_config()) if p["label"] == args.account), None)
        account_no = _match.get("account_id") if _match else None

    snap = json.load(open(args.snapshot, encoding="utf-8"))
    try:
        bal_rec = latest_balance(args.balance_raw, account_no=account_no)
    except RuntimeError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(2)
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
    true_cost_basis = snap["total_cost_value"]

    fees = args.trading_fees if args.trading_fees is not None else true_cost_basis * args.fee_rate_pct / 100.0

    # Vế trái: đường P&L — CHỈ dùng số THẬT (fee-rate xác nhận + depositFeeAmount thật từ API)
    lhs = args.starting_capital + unrealized_pnl - fees - accrued_fee
    # Vế phải: đường bảng cân đối (số dư THẬT từ broker) + offbook (user tự báo, vd Trứng vàng —
    # tiền vẫn của user, chỉ ngoài phạm vi balances() API, xem --offbook-assets ở trên)
    rhs = mtm_stock + cash - debt + args.offbook_assets

    residual = lhs - rhs
    tolerance_vnd = rhs * args.tolerance_pct / 100.0
    within_tolerance = abs(residual) <= abs(tolerance_vnd) + 5_000_000  # sàn tuyệt đối nhỏ cho phí lặt vặt

    daily_margin_interest_est = debt * args.margin_rate_annual / 365.0
    days_implied = residual / daily_margin_interest_est if daily_margin_interest_est else None

    print(f"== Reconcile equity — {args.account} ==")
    print(f"Nguồn balance THẬT: {args.balance_raw} (ts={bal_ts}, kind=balances)")
    print(f"Nguồn P&L THẬT: {args.snapshot}")
    print()
    print(f"VẾ TRÁI  (Vốn ban đầu + Lãi/lỗ - phí - lãi vay, TOÀN BỘ SỐ THẬT):")
    print(f"  Vốn ban đầu:           {args.starting_capital:>16,.0f}")
    print(f"  + Lãi/lỗ chưa thực hiện:{unrealized_pnl:>+16,.0f}")
    print(f"  - Phí giao dịch ({args.fee_rate_pct}% x giá vốn thật): {-fees:>16,.0f}")
    print(f"  - Phí/lãi margin đã POST (depositFeeAmount, API thật): {-accrued_fee:>12,.0f}")
    print(f"  = VẾ TRÁI:             {lhs:>16,.0f}")
    print()
    print(f"VẾ PHẢI  (NAV thị trường + Tiền mặt - Nợ margin, số THẬT từ broker):")
    print(f"  Giá trị cổ phiếu (MTM):{mtm_stock:>16,.0f}")
    print(f"  + Tiền mặt:            {cash:>16,.0f}")
    print(f"  - Nợ vay margin:       {-debt:>16,.0f}")
    if args.offbook_assets:
        print(f"  + Off-book (tự báo):   {args.offbook_assets:>16,.0f}")
    print(f"  = VẾ PHẢI:             {rhs:>16,.0f}")
    print()
    print(f"CHÊNH LỆCH (trái - phải, TOÀN BỘ SỐ THẬT): {residual:>+16,.0f}  ({residual/rhs*100:+.4f}% của vế phải)")
    print(f"Ngưỡng dung sai: ±{args.tolerance_pct}% NAV + 5tr VND sàn tuyệt đối")
    print(f"KẾT LUẬN (đẳng thức chính, chỉ số thật): {'✅ KHỚP' if within_tolerance else '❌ LỆCH VƯỢT NGƯỠNG — cần điều tra thêm'}")
    print()
    print(f"--- DIỄN GIẢI residual (ƯỚC TÍNH, KHÔNG phải số thật — margin rate {args.margin_rate_annual*100:.1f}%/năm do user cung cấp, chưa xác minh với DNSE) ---")
    print(f"  Lãi margin ước tính/ngày trên dư nợ hiện tại: {daily_margin_interest_est:>16,.0f} VND/ngày")
    if days_implied is not None:
        print(f"  Residual {residual:+,.0f} tương đương ~{days_implied:.2f} ngày lãi margin tích lũy CHƯA post vào depositFeeAmount")
    print(f"  (depositFeeAmount hiện tại chỉ {accrued_fee:,.0f}đ — có thể lãi margin post theo chu kỳ, không phải hàng ngày; cần đối chiếu sao kê DNSE để xác nhận chính xác)")

    result = {
        "account": args.account, "balance_ts": bal_ts,
        "starting_capital": args.starting_capital, "unrealized_pnl": unrealized_pnl,
        "fee_rate_pct_used": args.fee_rate_pct, "trading_fees_used": fees,
        "accrued_margin_fee_real": accrued_fee,
        "lhs_pnl_path": lhs, "mtm_stock": mtm_stock, "cash": cash, "margin_debt": debt,
        "offbook_assets_used": args.offbook_assets,
        "rhs_balance_sheet_path": rhs, "residual": residual,
        "residual_pct_of_rhs": residual / rhs * 100, "within_tolerance": within_tolerance,
        "margin_rate_annual_estimate": args.margin_rate_annual,
        "daily_margin_interest_estimate": daily_margin_interest_est,
        "residual_implied_days_of_margin_interest": days_implied,
    }
    out_path = args.snapshot.replace("verified_snapshot", "reconcile_equity")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\nGhi ra: {out_path}")
    if not within_tolerance:
        sys.exit(1)


if __name__ == "__main__":
    main()
