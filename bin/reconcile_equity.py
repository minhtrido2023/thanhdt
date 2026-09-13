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

Phí giao dịch tự tính từ tổng giá vốn thật trong snapshot × phí MUA thật (`dnse_fee_rates.py`,
0,097% đo trên email khớp lệnh DNSE 2026-09-13 — thay 0,075% cũ; --fee-rate-pct ép cả 2 chiều) — không cần nhập tay --trading-fees nữa (vẫn có thể override).
Lãi vay margin THẬT lấy từ field depositFeeAmount của balances API (số đã ghi nhận chính thức).
Phần dư (residual) còn lại sau khi trừ phí+lãi thật được so sánh với MỘT ƯỚC TÍNH lãi margin
tích lũy nhưng CHƯA post vào depositFeeAmount (--margin-rate-annual, mặc định 12.5%/năm theo
user cung cấp — CHƯA xác minh với hợp đồng/biểu phí DNSE, chỉ là ước tính) — in ra như một lời
giải thích khả dĩ cho residual, KHÔNG đưa vào đẳng thức chính (giữ đẳng thức chính 100% dữ liệu
thật, ước tính chỉ nằm ở phần diễn giải).

Nếu 2 vế (dùng số THẬT) không khớp trong ngưỡng dung sai (mặc định 0.05% NAV) -> in cảnh báo rõ
ràng, KHÔNG tự làm tròn/che giấu chênh lệch.

BỔ SUNG 2026-09-13 (aria-A1, job Taylor_20260913_053329) — vế trái cộng thêm 2 cấu phần THẬT:
  + Lãi/lỗ ĐÃ THỰC HIỆN: replay đúng các fill `dnse_fill_events()` của CHÍNH các ngày
    `dates_included` trong snapshot (cùng nguồn + cùng quy ước lô-đang-sống `CostBook` với
    unrealized ⇒ realized + unrealized = Σbán − Σmua + MTM). Phần bán VƯỢT KL trace được (vị
    thế legacy mua trước bot) không có giá vốn ⇒ KHÔNG cộng, in riêng `untraced_sell_proceeds`.
  + Cổ tức tiền mặt đã ghi nhận: delta dương `cashDividendReceiving` (tầng 2 của
    `dividend_adjusted_return.py`, §21) — số GỘP đã vào `totalCash`; trừ thuế TNCN 5% trên phần
    ĐÃ chi trả (phần còn phải thu vẫn ghi gộp trong totalCash).
Bản cũ thiếu 2 cấu phần này ⇒ residual +23,7tr (+2,41% NAV) SpaceX 2026-08-28. Công thức
unrealized/fee giữ nguyên; `--no-realized` tái lập đúng số của bản cũ.
Phần DIỄN GIẢI residual thêm: phí thật theo chiều (mua/bán) trên TỔNG giá trị khớp (vế trái chỉ trừ trên
giá vốn đang giữ), thuế TNCN 0,1% giá trị bán, lãi margin ước 12,5%/năm tích luỹ theo dư nợ
từng ngày. Còn dư >0,3% NAV sau diễn giải ⇒ in rõ "CHƯA GIẢI THÍCH ĐƯỢC", không ép về 0.

BỔ SUNG 2026-09-13 (aria-F2) — account có vị thế LEGACY lúc go-live (ZaloPay): bỏ --starting-capital
⇒ đọc `data/account_seed_capital.json`: vốn đầu kỳ = NAV thật ngày go-live (tiền + MTM toàn bộ vị
thế), lô legacy lấy MTM ngày đó làm GIÁ VỐN GIẢ ĐỊNH (nạp trước khi replay fill) ⇒ bán legacy có
realized, legacy còn giữ có unrealized + MTM; fill broker xác nhận (email/sao kê) mà dnse_raw thiếu
được cộng vào replay. Truyền --starting-capital ⇒ bỏ qua file, hành vi cũ y nguyên (SpaceX).
"""
import argparse
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dnse_fee_rates import FEE_RATE_BUY_PCT, FEE_RATE_SELL_PCT, SELL_TAX_RATE  # noqa: E402
UNEXPLAINED_WARN_PCT = 0.3   # dư sau diễn giải vượt ngưỡng này (% NAV) ⇒ báo chưa giải thích được


def realized_pnl_from_events(events_by_date, asof, corp_actions, seed_lots=None):
    """Lãi/lỗ đã thực hiện theo lô-đang-sống, replay y hệt `build_cost_books()`.

    Trả dict: realized (tổng), by_ticker, untraced_sell_proceeds (tiền bán phần KL không trace
    được giá vốn — legacy), buy_value, sell_value (tổng giá trị khớp, dùng cho diễn giải phí).
    seed_lots: {ticker: (qty, price, date)} lô legacy nạp TRƯỚC replay (giá vốn giả định = MTM
    ngày seed, KHÔNG tính vào buy_value). Trả thêm `books` {ticker: (qty, basis)} tại asof.
    Pure — không đọc file, để selfcheck khoá được bằng fixture.
    """
    from verify_account_snapshot import CostBook, corp_action_multiplier
    books = defaultdict(CostBook)
    by_tk = defaultdict(float)
    untraced = defaultdict(float)
    buy_value = sell_value = 0.0
    for tk, (qty, price, date) in (seed_lots or {}).items():
        books[tk].buy(qty * corp_action_multiplier(tk, date, asof, corp_actions), qty * price, date)
    for date in sorted(events_by_date):
        for _ts, _key, tk, side, qty, price in events_by_date[date]:
            m = corp_action_multiplier(tk, date, asof, corp_actions)
            book = books[tk]
            value = qty * price
            if side != "sell":
                buy_value += value
                book.buy(qty * m, value, date)
                continue
            sell_value += value
            q = qty * m
            covered = min(q, book.qty) if book.qty > 0 else 0.0
            if covered > 0:
                basis_out = book.basis * covered / book.qty
                by_tk[tk] += value * covered / q - basis_out
            if q > covered:
                untraced[tk] += value * (q - covered) / q
            book.sell(q, date)
    return {"realized": sum(by_tk.values()), "by_ticker": dict(by_tk),
            "untraced_sell_proceeds": sum(untraced.values()),
            "untraced_by_ticker": dict(untraced),
            "buy_value": buy_value, "sell_value": sell_value,
            "books": {tk: (b.qty, b.basis) for tk, b in books.items()}}


def net_cash_dividends(gross_deltas, receivable_asof, start, asof, tax_rate):
    """Cổ tức tiền mặt RÒNG đã vào `totalCash` trong [start, asof].

    gross_deltas: {ngày: delta dương cashDividendReceiving} (`broker_cash_deltas()`).
    Phần đã chi trả = gộp ghi nhận − còn phải thu tại asof; thuế chỉ trừ trên phần đã chi trả
    (DNSE ghi phải thu GỘP, trừ thuế lúc chi trả thật — docstring TẦNG 4 dividend_adjusted_return).
    """
    gross = sum(v for d, v in gross_deltas.items() if start <= d <= asof)
    paid = max(gross - receivable_asof, 0.0)
    tax = paid * tax_rate
    return {"gross": gross, "receivable_asof": receivable_asof, "paid": paid,
            "tax": tax, "net": gross - tax}


def margin_interest_estimate(daily_debt, start, asof, rate_annual):
    """Lãi margin ƯỚC TÍNH cộng dồn theo NGÀY LỊCH: dư nợ cuối ngày gần nhất (carry-forward)
    × rate/365. daily_debt: {ngày ISO: totalDebt}. Ngày trước bản ghi đầu tiên = 0."""
    import datetime as _dt
    d = _dt.date.fromisoformat(start)
    end = _dt.date.fromisoformat(asof)
    debt, total = 0.0, 0.0
    while d <= end:
        debt = daily_debt.get(d.isoformat(), debt)
        total += debt * rate_annual / 365.0
        d += _dt.timedelta(days=1)
    return total


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
    ap.add_argument("--starting-capital", type=float, default=None,
                     help="bỏ trống ⇒ đọc data/account_seed_capital.json (NAV go-live + lô legacy)")
    ap.add_argument("--seed-file", default=None,
                     help="mặc định <WC_ROOT>/data/account_seed_capital.json")
    ap.add_argument("--snapshot", required=True,
                     help="output file of verify_account_snapshot.py")
    ap.add_argument("--balance-raw", required=True,
                     help="dnse_raw_*.jsonl containing a fresh kind=balances record")
    ap.add_argument("--trading-fees", type=float, default=None,
                     help="tổng phí giao dịch thật nếu đã biết; bỏ trống = tự tính theo --fee-rate-pct")
    ap.add_argument("--fee-rate-pct", type=float, default=None,
                     help="ép phí %% CẢ 2 chiều; bỏ trống = phí thật dnse_fee_rates.py "
                          f"(mua {FEE_RATE_BUY_PCT:g}%%, bán {FEE_RATE_SELL_PCT:g}%%, đo 2026-09-13)")
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
    ap.add_argument("--no-realized", action="store_true",
                     help="bỏ realized P&L + cổ tức khỏi vế trái — tái lập đúng bản trước 2026-09-13")
    ap.add_argument("--div-tax-rate", type=float, default=0.05,
                     help="thuế TNCN cổ tức tiền mặt trên phần đã chi trả (cá nhân cư trú 5%%)")
    args = ap.parse_args()

    fee_buy_pct = FEE_RATE_BUY_PCT if args.fee_rate_pct is None else args.fee_rate_pct
    fee_sell_pct = FEE_RATE_SELL_PCT if args.fee_rate_pct is None else args.fee_rate_pct
    import wc_paths
    WC_ROOT = wc_paths.find_wc_root(__file__)   # marker `wc_env.sh`, xem wc_paths

    seed = None
    if args.starting_capital is None:
        seed_path = args.seed_file or os.path.join(WC_ROOT, "data", "account_seed_capital.json")
        seed = (json.load(open(seed_path, encoding="utf-8")) if os.path.exists(seed_path) else {}).get(args.account)
        if seed is None:
            print(f"❌ Không có --starting-capital và {seed_path} không có entry '{args.account}'.",
                  file=sys.stderr)
            sys.exit(2)
        args.starting_capital = float(seed["nav"])

    account_no = args.account_no
    if not account_no:
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

    fees = args.trading_fees if args.trading_fees is not None else true_cost_basis * fee_buy_pct / 100.0

    # Realized + cổ tức (aria-A1): cùng ngày fill + cùng asof với snapshot unrealized.
    asof = snap["asof"]
    dates = snap.get("dates_included") or []
    start = dates[0] if dates else asof
    if seed:
        import datetime as _dt
        if seed.get("account_no") and seed["account_no"] != account_no:
            print(f"❌ seed account_no {seed['account_no']} ≠ {account_no}", file=sys.stderr)
            sys.exit(2)
        start = (_dt.date.fromisoformat(seed["date"]) + _dt.timedelta(days=1)).isoformat()
    from verify_account_snapshot import dnse_fill_events
    from corp_actions import load_corp_actions
    from dividend_adjusted_return import broker_cash_deltas, _broker_records
    events_by_date = {}
    for d in dates:
        ev, err = dnse_fill_events(account_no, d)
        if ev is None:
            print(f"❌ {err} — snapshot dùng ngày {d} nhưng không đọc lại được fill, "
                  f"KHÔNG tính realized thiếu ngày.", file=sys.stderr)
            sys.exit(2)
        events_by_date[d] = list(ev)
    seed_lots, legacy_mtm, legacy_unreal, legacy_lines = None, 0.0, 0.0, []
    if seed:
        for fx in seed.get("missing_fills_broker_confirmed", []):
            if fx["date"] <= asof:
                events_by_date.setdefault(fx["date"], []).append(
                    (fx["date"] + "T23:59:59", "broker-confirmed", fx["ticker"], fx["side"],
                     float(fx["qty"]), float(fx["price"])))
        for d in events_by_date:
            events_by_date[d].sort(key=lambda e: e[0])
        seed_lots = {tk: (float(p["qty"]), float(p["price"]), seed["date"])
                     for tk, p in seed["legacy_positions"].items()}
    corp = load_corp_actions()
    rz = realized_pnl_from_events(events_by_date, asof, corp, seed_lots=seed_lots)
    if seed:
        # Legacy mà snapshot đã LOẠI khỏi P&L (không có lịch sử mua) ⇒ lấy từ lô seed đã replay.
        # Mã legacy snapshot VẪN giữ (vd lô mới sau khi bán sạch legacy) ⇒ đã nằm trong snapshot.
        from verify_account_snapshot import broker_positions_from_raw
        broker_pos = broker_positions_from_raw(account_no, asof) or {}
        in_snap = {p["ticker"] for p in snap.get("positions", [])}
        for tk in sorted(seed_lots):
            if tk in in_snap:
                continue
            bq, basis = rz["books"].get(tk, (0.0, 0.0))
            bp = broker_pos.get(tk)
            if bq <= 1e-9 and not bp:
                continue
            if not bp or abs(bq - bp["qty"]) > 0.5:
                print(f"⚠️ legacy {tk}: KL replay {bq:,.2f} ≠ broker {bp['qty'] if bp else 0:,.2f} "
                      f"({asof}) — thiếu fill/corp-action, residual sẽ lộ phần này", file=sys.stderr)
            if not bp:
                continue
            px = float(bp["marketPrice"])
            legacy_mtm += bp["qty"] * px
            legacy_unreal += bq * px - basis
            legacy_lines.append((tk, bp["qty"], bq, px, basis))
        mtm_stock += legacy_mtm
        unrealized_pnl += legacy_unreal
    daily_debt = {}
    for rec in sorted(_broker_records("balances", account_no), key=lambda r: r.get("ts") or ""):
        ts = rec.get("ts") or ""
        if ts > bal_ts:
            break
        st = rec.get("payload", {}).get("stock") or {}
        if all((st.get(k) or 0) == 0 for k in ("totalCash", "availableCash", "totalDebt")):
            continue   # khối stock toàn 0 — lỗi API tạm thời đã biết của DNSE
        daily_debt[ts[:10]] = float(st.get("totalDebt") or 0)
    receivable_asof = float(stock.get("cashDividendReceiving") or 0)
    div = net_cash_dividends(broker_cash_deltas(account_no), receivable_asof, start,
                             bal_ts[:10], args.div_tax_rate)
    realized = 0.0 if args.no_realized else rz["realized"]
    dividends_net = 0.0 if args.no_realized else div["net"]

    # Vế trái: đường P&L — CHỈ dùng số THẬT (fee-rate xác nhận + depositFeeAmount thật từ API)
    lhs = args.starting_capital + unrealized_pnl + realized + dividends_net - fees - accrued_fee
    # Vế phải: đường bảng cân đối (số dư THẬT từ broker) + offbook (user tự báo, vd Trứng vàng —
    # tiền vẫn của user, chỉ ngoài phạm vi balances() API, xem --offbook-assets ở trên)
    rhs = mtm_stock + cash - debt + args.offbook_assets

    residual = lhs - rhs
    tolerance_vnd = rhs * args.tolerance_pct / 100.0
    within_tolerance = abs(residual) <= abs(tolerance_vnd) + 5_000_000  # sàn tuyệt đối nhỏ cho phí lặt vặt

    daily_margin_interest_est = debt * args.margin_rate_annual / 365.0
    days_implied = residual / daily_margin_interest_est if daily_margin_interest_est else None

    # Diễn giải residual (ƯỚC TÍNH) — dương = vế trái cao hơn tiền thật ⇒ chi phí chưa trừ đủ.
    turnover = rz["buy_value"] + rz["sell_value"]
    fee_gap_est = (rz["buy_value"] * fee_buy_pct + rz["sell_value"] * fee_sell_pct) / 100.0 - fees
    sell_tax_est = rz["sell_value"] * SELL_TAX_RATE
    margin_cum_est = margin_interest_estimate(daily_debt, start, bal_ts[:10], args.margin_rate_annual)
    margin_gap_est = max(margin_cum_est - accrued_fee, 0.0)
    explained_est = fee_gap_est + sell_tax_est + margin_gap_est
    unexplained = residual - explained_est
    unexplained_pct = unexplained / rhs * 100

    print(f"== Reconcile equity — {args.account} ==")
    print(f"Nguồn balance THẬT: {args.balance_raw} (ts={bal_ts}, kind=balances)")
    print(f"Nguồn P&L THẬT: {args.snapshot}")
    print()
    print(f"VẾ TRÁI  (Vốn ban đầu + Lãi/lỗ - phí - lãi vay, TOÀN BỘ SỐ THẬT):")
    print(f"  Vốn ban đầu:           {args.starting_capital:>16,.0f}"
          + (f"  (NAV thật {seed['date']} từ account_seed_capital.json)" if seed else ""))
    for tk, bqty, rqty, px, basis in legacy_lines:
        print(f"    legacy {tk}: broker {bqty:,.0f}cp (replay {rqty:,.0f}) × {px:,.0f} − giá vốn "
              f"MTM-seed {basis:,.0f} ⇒ đã cộng vào unrealized + MTM")
    for fx in (seed or {}).get("missing_fills_broker_confirmed", []):
        print(f"    + fill broker xác nhận dnse_raw thiếu: {fx['date']} {fx['side']} {fx['qty']} "
              f"{fx['ticker']} @{fx['price']:,} ({fx['evidence']})")
    print(f"  + Lãi/lỗ chưa thực hiện:{unrealized_pnl:>+16,.0f}")
    if args.no_realized:
        print(f"  (--no-realized: BỎ realized {rz['realized']:+,.0f} + cổ tức {div['net']:+,.0f})")
    else:
        print(f"  + Lãi/lỗ ĐÃ thực hiện (fill thật, lô-đang-sống): {realized:>+16,.0f}")
        print(f"  + Cổ tức tiền mặt ròng (gộp {div['gross']:,.0f} − thuế {div['tax']:,.0f}): {dividends_net:>+12,.0f}")
    if rz["untraced_sell_proceeds"]:
        print(f"  (KHÔNG cộng: tiền bán vị thế legacy không có giá vốn {rz['untraced_sell_proceeds']:,.0f} "
              f"— {sorted(rz['untraced_by_ticker'])})")
    print(f"  - Phí giao dịch ({fee_buy_pct:g}% x giá vốn thật): {-fees:>16,.0f}")
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
    print(f"  Phí mua {fee_buy_pct:g}%/bán {fee_sell_pct:g}% trên TỔNG khớp mua+bán {turnover:,.0f} (vế trái mới trừ trên giá vốn đang giữ): {fee_gap_est:>+14,.0f}")
    print(f"  Thuế TNCN {SELL_TAX_RATE*100:.1f}% giá trị bán {rz['sell_value']:,.0f}:            {sell_tax_est:>+14,.0f}")
    print(f"  Lãi margin ước {args.margin_rate_annual*100:.1f}%/năm cộng dồn {start}→{bal_ts[:10]} (trừ phần đã post): {margin_gap_est:>+14,.0f}")
    print(f"  = Giải thích được (ước):  {explained_est:>+16,.0f}")
    print(f"  DƯ SAU DIỄN GIẢI:         {unexplained:>+16,.0f}  ({unexplained_pct:+.4f}% NAV) — "
          f"{'trong ±' + str(UNEXPLAINED_WARN_PCT) + '% NAV' if abs(unexplained_pct) <= UNEXPLAINED_WARN_PCT else '⚠️ CHƯA GIẢI THÍCH ĐƯỢC (>' + str(UNEXPLAINED_WARN_PCT) + '% NAV)'}")

    result = {
        "account": args.account, "balance_ts": bal_ts,
        "starting_capital": args.starting_capital, "unrealized_pnl": unrealized_pnl,
        "realized_included": not args.no_realized, "realized_pnl": rz["realized"],
        "realized_by_ticker": rz["by_ticker"],
        "untraced_sell_proceeds": rz["untraced_sell_proceeds"],
        "untraced_by_ticker": rz["untraced_by_ticker"],
        "cash_dividends": div, "fill_buy_value": rz["buy_value"], "fill_sell_value": rz["sell_value"],
        "fee_rate_pct_used": fee_buy_pct, "fee_rate_sell_pct_used": fee_sell_pct, "trading_fees_used": fees,
        "seed_capital_used": seed, "legacy_mtm_added": legacy_mtm, "legacy_unrealized_added": legacy_unreal,
        "accrued_margin_fee_real": accrued_fee,
        "lhs_pnl_path": lhs, "mtm_stock": mtm_stock, "cash": cash, "margin_debt": debt,
        "offbook_assets_used": args.offbook_assets,
        "rhs_balance_sheet_path": rhs, "residual": residual,
        "residual_pct_of_rhs": residual / rhs * 100, "within_tolerance": within_tolerance,
        "margin_rate_annual_estimate": args.margin_rate_annual,
        "daily_margin_interest_estimate": daily_margin_interest_est,
        "residual_implied_days_of_margin_interest": days_implied,
        "explain_fee_on_turnover_gap_est": fee_gap_est, "explain_sell_tax_est": sell_tax_est,
        "explain_margin_interest_cum_est": margin_cum_est, "explain_margin_gap_est": margin_gap_est,
        "unexplained_after_estimates": unexplained, "unexplained_pct_of_rhs": unexplained_pct,
    }
    out_path = args.snapshot.replace("verified_snapshot", "reconcile_equity")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\nGhi ra: {out_path}")
    if not within_tolerance:
        sys.exit(1)


if __name__ == "__main__":
    main()
