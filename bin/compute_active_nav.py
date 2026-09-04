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
    (real-time, không phải file trung gian). Cấu phần tiền: xem §cash.
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

§cash — CẤU PHẦN TIỀN = `totalCash − totalDebt`, KHÔNG phải `availableCash`
(bug sửa 2026-08-10, job Taylor_20260810_004252; cùng LOẠI bug với mẫu số pool của
`compute_park_trim.py` sửa 2026-08-09, job Taylor_20260809_150316 — lần thứ hai trong
hai ngày, xem kb/coding_guidelines.md §25).

  Trước:  cash = DNSEBroker.get_cash() → `availableCash` (field đầu tiên của qget).
  Sau:    cash = totalCash − totalDebt (đọc THẲNG từ block `stock` của balances).

VÌ SAO. `availableCash` là "tiền TIÊU ĐƯỢC NGAY", KHÔNG phải "vốn tôi SỞ HỮU": nó không
gồm tiền bán chưa settle T+2, cổ tức phải thu, lãi tiền gửi. Đo thật SpaceX 2026-08-09:

    11:25 (trước khớp):                      availableCash 4.821.143   totalCash  14.596.323
    19:10 (sau khi bán 13 mã PARK, 189,4tr): availableCash 4.821.143   totalCash 203.656.265

⇒ toàn bộ 189,06tr tiền bán chỉ hiện ở `totalCash`. Với active_nav, hệ quả là NAV bị
KHAI THIẾU đúng bằng lượng tiền đang trên đường về: SpaceX 08-09 cho active_nav
762.476.143đ trong khi NAV thật ~961.311.265đ (−20,7%). Vì active_nav là MẪU của mọi
phép sizing (`LAG_book = active_nav × w_lag`, slot CAPIT, trần chia %ADV giữa 2 account),
khai thiếu = under-deploy vốn có thật, và nặng nhất đúng vào phiên sau một đợt bán lớn.

TRỪ `totalDebt`: NAV = Tiền + Cổ phiếu − Nợ, cùng quy ước với `daily_nav_snapshot.py:449`
và `reconcile_equity.py`. Bản cũ không trừ nợ margin ⇒ với account có vay, active_nav
KHAI THỪA phần nợ (gap đã được nêu trong `research/margin_kelly_production_wiring_20260803.md`
mục cuối). Hai sai lệch NGƯỢC CHIỀU nhau nên KHÔNG triệt tiêu ổn định — phải sửa cả hai.

RANH GIỚI — chỗ nào VẪN phải dùng `availableCash`, đừng "thống nhất" nhầm:
  · `DNSEBroker.get_cash()` (trading_bot/brokers.py) — GIỮ NGUYÊN `availableCash`.
    `check_plan_funding()`/executor hỏi "đặt lệnh NGAY được bao nhiêu", đó là sức mua thật,
    không phải NAV báo cáo. Sửa nó = nới lỏng gate tiền, hướng sai nguy hiểm.
  · `compute_jit_unpark.py` (L2) — CỐ Ý `availableCash`, cùng lý do.
  Ranh giới: cơ sở TÍNH TỶ TRỌNG mục tiêu → totalCash−totalDebt; sức mua THỰC THI → ppse/
  availableCash. Đúng tinh thần đã áp cho `manual_offbook_assets_vnd` (vào NAV, không vào
  sức mua).

FAIL-CLOSED. Ba guard (tái dùng NGUYÊN VẸN từ `park_holdings.py`, không viết lại —
`_stock_block_all_zero` / `_cash_fields_all_zero` / `_cash_fields_inconsistent`) bắt lỗi
feed DNSE trả block `stock` toàn 0 hoặc chỉ ăn 2/3 field tiền (sự cố thật 2026-07-27).
Bất kỳ guard nào nổ, hoặc thiếu `totalCash`/`totalDebt` ⇒ THOÁT mã 4, KHÔNG ghi file, và
TUYỆT ĐỐI không âm thầm rơi về `availableCash` (rơi về = tái lập đúng bug vừa sửa). File
active_nav cũ ở lại nguyên vẹn; consumer `golive_recommend_v23._account_nav_basis()` tự
hết hạn theo `computed_at` sau 5 ngày rồi lùi về `nav_history` — đường lùi đã có sẵn.

Cổ tức phải thu (`cashDividendReceiving`) NẰM TRONG `totalCash` trước ngày ex ⇒ có thể
đếm 2 lần với giá cổ phiếu chưa rơi quyền, tối đa 1-2 phiên rồi tự triệt tiêu
(`daily_nav_snapshot.cum_dividend_double_count`). Script này KHÔNG hiệu chỉnh (cần lịch sử
dnse_raw + ex-date từ BQ, ngoài phạm vi bản vá này) mà CÔNG BỐ: in cảnh báo + ghi
`cash_dividend_receiving_vnd` vào JSON khi khoản đó vượt 0,5% NAV.
"""
import argparse
import json
import os
import subprocess
import sys

BQ_PATH_PREFIX = "/home/trido/google-cloud-sdk/bin"
WC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.path.insert(0, WC_ROOT)
from trading_bot.vn_market import today_ict  # noqa: E402 — ICT thật, không phụ thuộc TZ host (§16)


def get_account_profile(label):
    accounts_path = os.path.join(WC_ROOT, "secrets", "trading_bot_accounts.json")
    accounts = json.load(open(accounts_path, encoding="utf-8")).get("accounts", [])
    for a in accounts:
        if a.get("label") == label:
            return a
    return None


def cash_basis(bal):
    """`totalCash − totalDebt` từ payload `balances` thô (§cash). → (VND|None, chi_tiết).

    None = KHÔNG dựng được cơ sở tiền đáng tin ⇒ caller PHẢI fail-closed. Ba guard tái dùng
    nguyên vẹn từ `park_holdings.py` (nơi chúng đã qua 3 vòng quant-skeptic 2026-08-09) —
    import chứ không chép lại, để sửa một chỗ là cả hai đường cùng đổi.

    `chi_tiết` luôn mang đủ cả ba field tiền thô + `reason` (khi None) để provenance trong
    JSON đầu ra không nói dối về việc số này đến từ đâu.
    """
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from park_holdings import (_cash_fields_all_zero, _cash_fields_inconsistent,
                               _f_or_none, _stock_block_all_zero)

    row = bal[0] if isinstance(bal, list) and bal else bal
    if isinstance(row, dict) and isinstance(row.get("stock"), dict):
        row = row["stock"]                      # balances thật: {"stock": {...}, "derivative": {...}}
    st = row if isinstance(row, dict) else {}
    detail = {"cash_total_vnd": _f_or_none(st.get("totalCash")),
              "cash_debt_vnd": _f_or_none(st.get("totalDebt")),
              "cash_available_vnd": _f_or_none(st.get("availableCash")),
              "cash_dividend_receiving_vnd": _f_or_none(st.get("cashDividendReceiving")),
              "cash_basis": "totalCash-totalDebt", "reason": None}

    if _stock_block_all_zero(st):
        detail["reason"] = ("block `stock` của balances TOÀN SỐ 0 — lỗi feed DNSE tạm thời "
                            "(sự cố thật 2026-07-27), KHÔNG phải tiền mặt thật về 0")
    elif _cash_fields_all_zero(st):
        detail["reason"] = ("cả totalCash/totalDebt/availableCash đều = 0 trong khi field khác "
                            "vẫn sống — lỗi feed chỉ ăn phần tiền")
    elif _cash_fields_inconsistent(st):
        detail["reason"] = (f"totalCash {float(st['totalCash']):,.0f}đ < availableCash "
                            f"{float(st['availableCash']):,.0f}đ — vi phạm bất biến kế toán "
                            f"(totalCash luôn CHỨA availableCash) ⇒ block tiền không đáng tin")
    elif detail["cash_total_vnd"] is None or detail["cash_debt_vnd"] is None:
        detail["reason"] = "DNSE không trả `totalCash`/`totalDebt` trong block `stock`"
    if detail["reason"]:
        return None, detail
    return detail["cash_total_vnd"] - detail["cash_debt_vnd"], detail


def live_balance_and_positions(account_id, label):
    """Gọi trực tiếp DNSEBroker — real-time, không qua file trung gian.

    KHÔNG dùng `b.get_cash()`: hàm đó trả `availableCash` = sức mua tức thời, đúng cho
    executor/funding-gate nhưng SAI cho cơ sở NAV (§cash). Đọc thẳng payload `balances` thô
    để lấy được cả hai field `totalCash`/`totalDebt` mà `get_cash()` đã bóp về một số.
    """
    sys.path.insert(0, WC_ROOT)
    from trading_bot.brokers import DNSEBroker
    b = DNSEBroker(account_id=account_id, credentials_file=None, label=label)
    b.connect()
    bal = b.client.balances(account_id)
    b._log_raw("balances", bal)                 # cùng dấu vết audit như get_cash() vẫn ghi
    cash, cash_detail = cash_basis(bal)
    # Trứng vàng — live API trả thẳng (không có wrapper "payload" như trong log file).
    egg_value = float((bal.get("egg") or {}).get("totalValue") or 0)
    positions = b.get_positions()
    return cash, positions, cash_detail, egg_value


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
        # `bq` ghi lỗi ra STDOUT chứ không phải stderr (kb/incidents/2026-08/
        # 2026-08-29-bq-error-on-stdout-empty-diagnosis.md) — chỉ đọc stderr thì
        # người vận hành nhận chuỗi RỖNG. Không đổi luồng, chỉ đổi chuỗi chẩn đoán.
        return None, (out.stderr.strip() or out.stdout.strip())
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
    today = today_ict().isoformat()
    if asof is None or asof == today:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from verify_account_snapshot import dnse_close_prices
        # with_source=True: mã đang GDKHQ được lấy giá THUỘC PHIÊN HÔM NAY — khớp lệnh sống
        # ('dnse_trade_today') hoặc giá tham chiếu sàn ('dnse_secdef_basic') — thay vì giá
        # đóng cửa phiên trước. Provenance phải nói đúng nguồn nào, đừng khai tất cả là
        # 'dnse_g1' (xem docstring dnse_close_prices: HAI cửa sổ tiền phiên / giữa phiên).
        prices, price_source = dnse_close_prices(tickers, with_source=True)
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
    offbook_asof = profile.get("manual_offbook_assets_asof") or ""
    offbook_stale_warning = None
    if offbook and offbook_asof:
        asof_ref = args.asof or today_ict().isoformat()
        try:
            age_days = (_dt_stale.date.fromisoformat(asof_ref)
                        - _dt_stale.date.fromisoformat(offbook_asof)).days
            if age_days > 21:
                offbook_stale_warning = (
                    f"manual_offbook_assets_asof ({offbook_asof}) đã {age_days} ngày — xác nhận "
                    f"lại số dư off-book với user trước khi dùng làm cơ sở sizing.")
        except ValueError:
            pass

    cash, positions, cash_detail, egg_value = live_balance_and_positions(account_id, args.account)
    if cash is None:
        # FAIL-CLOSED (§cash): không ghi đè file active_nav cũ bằng một con số sai. Consumer
        # (`golive_recommend_v23._account_nav_basis`) tự thấy file quá hạn theo `computed_at`
        # rồi lùi về nav_history — đường lùi có sẵn, không cần đoán số ở đây.
        print(f"❌ Không dựng được cơ sở tiền cho {args.account}: {cash_detail['reason']} "
              f"⇒ KHÔNG ghi active_nav (giữ nguyên file cũ). Chạy lại để lấy bản đọc balance "
              f"tươi; TUYỆT ĐỐI không thay bằng `availableCash` (xem §cash trong docstring).",
              file=sys.stderr)
        sys.exit(4)
    tickers = list(positions.keys())
    if not tickers:
        print(f"⚠️ Account {args.account} không có vị thế nào — "
              f"active_nav = cash + egg + offbook = {cash + egg_value + offbook:,.0f} "
              f"(cash {cash:,.0f}, egg {egg_value:,.0f}, offbook {offbook:,.0f})")
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

    total_nav = cash + total_mv + egg_value + offbook
    active_nav = total_nav - excluded_mv

    print(f"== Active NAV — {args.account} (account_id={account_id}) ==")
    print(f"{'Mã':6s} {'KL':>10s} {'Giá':>10s} {'Giá trị':>16s}  {'excluded?'}")
    for tk, qty, px, mv, is_excl in sorted(rows, key=lambda r: -r[3]):
        flag = "🔒 EXCLUDED" if is_excl else ""
        print(f"{tk:6s} {qty:>10,.0f} {px:>10,.0f} {mv:>16,.0f}  {flag}")
    print()
    print(f"Tiền mặt (totalCash − totalDebt): {cash:>16,.0f}")
    print(f"  · totalCash:            {cash_detail['cash_total_vnd']:>16,.0f}  "
          f"(gồm tiền bán chưa settle T+2, cổ tức phải thu, lãi tiền gửi)")
    print(f"  · − totalDebt:          {cash_detail['cash_debt_vnd']:>16,.0f}")
    print(f"  · availableCash:        {(cash_detail['cash_available_vnd'] or 0):>16,.0f}  "
          f"(sức mua TỨC THÌ — KHÔNG dùng làm cơ sở NAV, chỉ để đối chiếu)")
    print(f"Tổng giá trị cổ phiếu:    {total_mv:>16,.0f}")
    print(f"  trong đó excluded:      {excluded_mv:>16,.0f}  ({', '.join(sorted(excluded)) or '(none)'})")
    if egg_value:
        print(f"Trứng vàng (tự đọc từ egg.totalValue trong balances API): {egg_value:>16,.0f}")
    if offbook:
        print(f"Off-book (user tự báo, KHÔNG phải sức mua ngay):          {offbook:>16,.0f}")
    print(f"= TỔNG NAV:               {total_nav:>16,.0f}")
    print(f"= ACTIVE NAV (cho chiến lược V2.4, loại trừ excluded_tickers): {active_nav:>16,.0f}")
    if egg_value:
        print(f"ℹ️ Trứng vàng {egg_value:,.0f} đã cộng vào NAV tự động — KHÔNG phải sức mua đặt lệnh ngay.")
    if offbook:
        print(f"⚠️ ACTIVE NAV đã cộng {offbook:,.0f} off-book làm cơ sở TÍNH TỶ TRỌNG mục tiêu — "
              f"nhưng sức mua THỰC THI NGAY vẫn phải kiểm tra `cash`/ppse live (DNSE), vì số "
              f"off-book cần user rút tay trước khi bot đặt lệnh được.")
    if offbook_stale_warning:
        print(f"⚠️ {offbook_stale_warning}")
    # Cổ tức phải thu đã nằm trong totalCash nhưng giá cổ phiếu có thể chưa rơi ex-date ⇒
    # đếm 2 lần, tối đa 1-2 phiên rồi tự triệt tiêu (§cash). Chỉ CÔNG BỐ khi đủ lớn để đổi
    # quy mô lệnh; không tự hiệu chỉnh (cần ex-date từ BQ, ngoài phạm vi script này).
    div_recv = cash_detail.get("cash_dividend_receiving_vnd") or 0
    div_warning = None
    if div_recv > 0.005 * active_nav:
        div_warning = (
            f"cổ tức phải thu {div_recv:,.0f}đ ({div_recv / active_nav:.2%} active_nav) đã nằm "
            f"trong totalCash — nếu cổ phiếu CHƯA qua ex-date thì NAV đang đếm 2 lần khoản này "
            f"(tự triệt tiêu sau 1-2 phiên; xem daily_nav_snapshot.cum_dividend_double_count).")
        print(f"⚠️ {div_warning}")

    result = {
        "account": args.account, "account_id": account_id,
        # Ngày tính, ghi vào NỘI DUNG file: file này ghi ad-hoc (không cron) nên consumer
        # phải tự kiểm tra nó còn tươi không — và phải kiểm theo nội dung, không theo mtime
        # (mtime tươi/nội dung cũ là bẫy đã gặp thật, sự cố lag_edge_health 2026-07-12).
        # Consumer: golive_recommend_v23._account_nav_basis() (chia trần %ADV cho CAPIT).
        "computed_at": today_ict().isoformat(),
        # `cash` = totalCash − totalDebt kể từ 2026-08-10 (trước đó là `availableCash`, §cash).
        # Ba field thô đi kèm để consumer/audit tái lập được con số mà không phải gọi lại API.
        "cash": cash,
        "cash_total_vnd": cash_detail["cash_total_vnd"],
        "cash_debt_vnd": cash_detail["cash_debt_vnd"],
        "cash_available_vnd": cash_detail["cash_available_vnd"],
        "cash_dividend_receiving_vnd": cash_detail["cash_dividend_receiving_vnd"],
        "cash_basis": cash_detail["cash_basis"],
        "cash_dividend_double_count_warning": div_warning,
        "total_stock_value": total_mv, "excluded_value": excluded_mv,
        "egg_assets": egg_value, "egg_assets_auto": True,
        "offbook_assets": offbook, "offbook_assets_asof": offbook_asof,
        "offbook_stale_warning": offbook_stale_warning,
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
