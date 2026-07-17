#!/usr/bin/env python3
"""compute_active_nav.py --account ZaloPay --account-id 0001743768

Tính NAV "khả dụng cho chiến lược" (active NAV) cho MỘT account bất kỳ có
`excluded_tickers` (giữ legacy/special-situation holding ngoài rebalancing V2.4 —
xem trading_bot/config.py ACCOUNT_DEFAULTS). Khác `daily_nav_snapshot.py` (dựa vào
lịch sử FILL trong journal của CHÍNH bot để tính giá vốn/P&L) — script này CHỈ cần
giá trị thị trường hiện tại, không cần lịch sử khớp lệnh, nên dùng được cho account
có vị thế mua từ TRƯỚC khi bot quản lý (không có trong journal nội bộ).

    active_nav = tổng_NAV − giá_trị_thị_trường(các mã trong excluded_tickers)

Nguồn số liệu:
  - Vị thế + cash/nợ margin: đọc trực tiếp balances/positions THẬT qua DNSEBroker
    (real-time, không phải file trung gian).
  - Giá thị trường: nếu --asof là HÔM NAY (hoặc bỏ trống) → giá DNSE live
    (close_price boardId=G1, cùng nguồn verify_account_snapshot.dnse_close_prices);
    BQ tav2_bq.ticker Close CHỈ dùng cho ngày quá khứ. Bright-line rule 2026-07-09
    (kb/coding_guidelines.md §6): BQ chỉ sync đêm 23:45 ICT nên chạy intraday mà đọc
    BQ là cầm chắc giá hôm-trước — script này là cơ sở sizing plan (DollarBill đọc
    active_nav), giá stale ở đây = sai quy mô lệnh thật (audit Taylor_20260711_031821 F1).

Dùng để: (1) DollarBill/Mike biết đúng cơ sở NAV khi lên plan cho account có
excluded_tickers (target % phải tính trên active_nav, KHÔNG phải tổng NAV — nếu
không sẽ tính sai quy mô lệnh, cố gắng deploy vốn không thực sự có sẵn); (2) báo
cáo tách riêng phần NAV "chiến lược V2.4" khỏi phần legacy khi so sánh hiệu suất
giữa các account (vd SpaceX vs ZaloPay) — số báo cáo không bị lẫn biến động của
mã đang giữ ngoài chiến lược.
"""
import argparse
import json
import os
import subprocess
import sys

BQ_PATH_PREFIX = "/home/trido/google-cloud-sdk/bin"
WC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_account_profile(label):
    accounts_path = os.path.join(WC_ROOT, "secrets", "trading_bot_accounts.json")
    accounts = json.load(open(accounts_path, encoding="utf-8")).get("accounts", [])
    for a in accounts:
        if a.get("label") == label:
            return a
    return None


def live_balance_and_positions(account_id, label):
    """Gọi trực tiếp DNSEBroker — real-time, không qua file trung gian."""
    sys.path.insert(0, WC_ROOT)
    from trading_bot.brokers import DNSEBroker
    b = DNSEBroker(account_id=account_id, credentials_file=None, label=label)
    b.connect()
    cash = b.get_cash()
    positions = b.get_positions()
    return cash, positions


def bq_close_prices(tickers, as_of_date=None):
    env = dict(os.environ)
    env["PATH"] = BQ_PATH_PREFIX + ":" + env.get("PATH", "")
    tick_list = ",".join(f"'{t}'" for t in sorted(tickers))
    date_clause = (f"t2.time <= '{as_of_date}'" if as_of_date else "TRUE")
    sql = f"""
    SELECT t.ticker, t.Close
    FROM tav2_bq.ticker AS t
    WHERE t.ticker IN ({tick_list})
    AND t.time = (SELECT MAX(t2.time) FROM tav2_bq.ticker AS t2
                  WHERE t2.ticker = '{sorted(tickers)[0]}' AND {date_clause})
    """
    cmd = ["bq", "query", "--use_legacy_sql=false",
           "--project_id=lithe-record-440915-m9", "--format=json",
           "--max_rows=5000", sql]
    out = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if out.returncode != 0:
        return None, out.stderr.strip()
    rows = json.loads(out.stdout)
    return {r["ticker"]: float(r["Close"]) for r in rows}, None


def resolve_prices(tickers, asof):
    """Chọn nguồn giá theo bright-line rule: hôm nay (hoặc None) → DNSE live,
    ngày quá khứ → BQ Close. Mirror đúng nhánh asof==today của
    verify_account_snapshot.py / daily_nav_snapshot.py — không tự chế logic mới.

    Trả về (prices: {tk: px}, price_source: {tk: nguồn}, err: str|None).
    Ticker DNSE thiếu giá (API hiccup) → fallback BQ từng mã + cảnh báo LỚN ra stderr
    (đánh dấu nguồn 'bq_close_stale' để provenance trong output JSON không nói dối).
    """
    import datetime as _dt
    today = _dt.date.today().isoformat()
    if asof is None or asof == today:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from verify_account_snapshot import dnse_close_prices
        prices = dnse_close_prices(tickers)
        price_source = {tk: "dnse_g1" for tk in prices}
        missing = [t for t in tickers if t not in prices]
        if missing:
            bq_px, err = bq_close_prices(missing)
            if bq_px:
                for tk, px in bq_px.items():
                    prices[tk] = px
                    price_source[tk] = "bq_close_stale"
            print(f"⚠️ DNSE thiếu giá live cho {missing} — tạm dùng giá BQ (có thể trễ "
                  f"≥1 ngày giao dịch, BQ chỉ sync đêm 23:45 ICT) — active_nav có thể lệch",
                  file=sys.stderr)
        return prices, price_source, None
    prices, err = bq_close_prices(tickers, asof)
    if prices is None:
        return None, None, err
    return prices, {tk: "bq_close" for tk in prices}, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--account", required=True, help="label trong trading_bot_accounts.json")
    ap.add_argument("--account-id", default=None, help="override account_id nếu cần")
    ap.add_argument("--asof", default=None,
                    help="ngày giá đóng cửa (mặc định/hôm nay: DNSE live; ngày quá khứ: BQ)")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    profile = get_account_profile(args.account)
    if profile is None:
        print(f"❌ Không tìm thấy account '{args.account}' trong trading_bot_accounts.json",
              file=sys.stderr)
        sys.exit(2)

    account_id = args.account_id or profile.get("account_id")
    excluded = set(profile.get("excluded_tickers") or [])
    # Tài sản off-book (vd "Trứng vàng" DNSE — không lộ qua OpenAPI, user tự báo, xem
    # trading_bot/config.py ACCOUNT_DEFAULTS): cộng vào total_nav để KHÔNG hụt cơ sở tính
    # tỷ trọng mục tiêu của chiến lược khi user tạm chuyển tiền rảnh ra ngoài tài khoản giao
    # dịch — số THỰC SỰ đặt lệnh được vẫn phải kiểm qua `cash`/ppse live, KHÔNG phải số này.
    offbook = float(profile.get("manual_offbook_assets_vnd") or 0)

    cash, positions = live_balance_and_positions(account_id, args.account)
    tickers = list(positions.keys())
    if not tickers:
        print(f"⚠️ Account {args.account} không có vị thế nào — "
              f"active_nav = cash + offbook = {cash + offbook:,.0f} "
              f"(cash {cash:,.0f} + offbook {offbook:,.0f})")
        return

    prices, price_source, err = resolve_prices(tickers, args.asof)
    if prices is None:
        print(f"❌ Không lấy được giá BQ: {err}", file=sys.stderr)
        sys.exit(3)

    rows = []
    total_mv = 0.0
    excluded_mv = 0.0
    for tk, pos in positions.items():
        qty = pos.get("total", 0)
        px = prices.get(tk)
        if px is None:
            print(f"⚠️ Thiếu giá cho {tk} — bỏ qua khỏi tổng (có thể làm lệch active_nav)",
                  file=sys.stderr)
            continue
        mv = qty * px
        total_mv += mv
        is_excluded = tk in excluded
        if is_excluded:
            excluded_mv += mv
        rows.append((tk, qty, px, mv, is_excluded))

    total_nav = cash + total_mv + offbook
    active_nav = total_nav - excluded_mv

    print(f"== Active NAV — {args.account} (account_id={account_id}) ==")
    print(f"{'Mã':6s} {'KL':>10s} {'Giá':>10s} {'Giá trị':>16s}  {'excluded?'}")
    for tk, qty, px, mv, is_excl in sorted(rows, key=lambda r: -r[3]):
        flag = "🔒 EXCLUDED" if is_excl else ""
        print(f"{tk:6s} {qty:>10,.0f} {px:>10,.0f} {mv:>16,.0f}  {flag}")
    print()
    print(f"Tiền mặt:                 {cash:>16,.0f}")
    print(f"Tổng giá trị cổ phiếu:    {total_mv:>16,.0f}")
    print(f"  trong đó excluded:      {excluded_mv:>16,.0f}  ({', '.join(sorted(excluded)) or '(none)'})")
    if offbook:
        print(f"Off-book (vd Trứng vàng, user tự báo, KHÔNG phải sức mua ngay): {offbook:>16,.0f}")
    print(f"= TỔNG NAV:               {total_nav:>16,.0f}")
    print(f"= ACTIVE NAV (cho chiến lược V2.4, loại trừ excluded_tickers): {active_nav:>16,.0f}")
    if offbook:
        print(f"⚠️ ACTIVE NAV đã cộng {offbook:,.0f} off-book làm cơ sở TÍNH TỶ TRỌNG mục tiêu — "
              f"nhưng sức mua THỰC THI NGAY vẫn phải kiểm tra `cash`/ppse live (DNSE), vì số "
              f"off-book cần user rút tay trước khi bot đặt lệnh được.")

    result = {
        "account": args.account, "account_id": account_id,
        "cash": cash, "total_stock_value": total_mv, "excluded_value": excluded_mv,
        "offbook_assets": offbook,
        "excluded_tickers": sorted(excluded), "total_nav": total_nav, "active_nav": active_nav,
        "positions": [{"ticker": tk, "qty": qty, "price": px, "value": mv, "excluded": is_excl,
                        "price_source": price_source.get(tk, "?")}
                       for tk, qty, px, mv, is_excl in rows],
    }
    out_path = args.out or os.path.join(
        WC_ROOT, "data", "execution_logs", f"active_nav_{args.account}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\nGhi ra: {out_path}")


if __name__ == "__main__":
    main()
