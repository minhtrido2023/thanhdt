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

§exdate_frame — ĐÊM TRƯỚC GDKHQ, KHỐI LƯỢNG VÀ GIÁ PHẢI CÙNG MỘT HỆ QUY CHIẾU (bug 2026-09-23,
VPB ISS 0,2604104 ex-date 24/09). DNSE credit KL mới vào `positions` ngay tối T-1 (SpaceX
1.100→1.386) trong khi giá đóng cửa G1 của phiên T-1 vẫn là giá CÒN QUYỀN 27.800 — cả hai đều
đúng, nhưng nhân chéo thì sai: 1.386×27.800 = 38.530.800 thay vì 1.386×22.050 = 30.561.300,
active_nav phồng 7.969.500đ (+0,80%) và plan 24/09 đã sinh lệnh PARK_TRIM VPB trên rổ phồng đó.
Vá: mã có bằng chứng credit sớm (`exdate_frame.classify_positions`, tái dùng
`daily_nav_snapshot.classify_qty_residual`) được định giá bằng `marketPrice` của CHÍNH bản ghi
vị thế — sau khi đối soát nó tái tạo được giá cum qua hệ số sự kiện. KL đổi KHÔNG giải thích
được, hoặc credit sớm mà không dựng nổi giá cùng hệ ⇒ **rc=6, KHÔNG ghi file** (đây là mẫu số
sizing; số sai tệ hơn số cũ). Chi tiết + vì sao KHÔNG tin thẳng marketPrice: bin/exdate_frame.py.
Cổng chỉ chạy ở nhánh asof=hôm nay, nên lối vòng của nó (`--asof <quá khứ>` vẫn đọc vị thế LIVE
rồi ghi ĐÈ file canonical, rc=0, không cảnh báo) bị chốt bằng **rc=7**: `--asof` khác hôm nay bắt
buộc có `--out` trỏ đi nơi khác (§8 — output khảo sát không được mang tên file canonical).

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

§excluded_dividend — cổ tức phải thu của MÃ EXCLUDED bị loại khỏi active_nav tới khi tiền về
(Option B, user quyết 2026-09-19, bus topic
`Wags/zalopay-active-nav-excluded-ticker-dividend-receivable-option-c`). Sự cố gốc: ZaloPay
DGC (excluded) có 80.000.000đ cổ tức receivable nằm trong `totalCash` từ 2026-09-14, làm
active_nav phồng ~13% ⇒ mọi lệnh mua ZaloPay tính theo active_nav bị phồng theo (VPI 17/09:
500cp thay vì ~400cp đúng — arch-review Wags_20260917_012008). `cashDividendReceiving` là một
số TỔNG do DNSE trả (không tách theo mã), nên không thể tự suy ra khoản nào thuộc mã nào —
nguồn sự thật là entry cấu hình `excluded_dividend_receivable` trong `trading_bot_accounts.json`
(ticker + amount_vnd + expected_arrival_date), user tự khai, CÙNG kiểu với
`manual_offbook_assets_vnd`. TÍN HIỆU DỪNG LOẠI là `cash_dividend_receiving_vnd` do DNSE trả tự
hạ xuống (tiền đã settle thật) — KHÔNG PHẢI `expected_arrival_date` đã qua (arch-review
2026-09-19, bản đầu dùng ngày làm điều kiện dừng: tiền về TRỄ hơn dự kiến ⇒ code cũ tự ngừng loại
trong im lặng, tái lập đúng bug đang sửa). `expected_arrival_date` chỉ gắn cờ `overdue` để cảnh
báo. Vì `cashDividendReceiving` là số TỔNG không tách theo mã, cơ chế kẹp (`min(amt, remaining)`)
là BẢO THỦ theo một chiều: nếu tiền DGC về sớm ĐÚNG LÚC một mã khác (không-excluded) cũng có
receivable phát sinh, cap vẫn thấy đủ 80tr và có thể loại NHẦM phần của mã kia — hướng sai luôn là
UNDER-size (an toàn hơn OVER-size), không phải hướng ngược lại. RETROACTIVE: KHÔNG áp cho plan ĐÃ
duyệt/đã khớp trước 2026-09-19 (VPI 500cp 17/09 giữ nguyên) — chỉ áp từ lần chạy kế tiếp trở đi.
"""
import argparse
import datetime as _dt_stale
import json
import os
import subprocess
import sys

BQ_PATH_PREFIX = "/home/trido/google-cloud-sdk/bin"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wc_paths  # noqa: E402

WC_ROOT = wc_paths.find_wc_root(__file__)

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


def excluded_dividend_pending(excluded_tickers, dividend_receivable_config,
                              cash_dividend_receiving_vnd, asof_ref):
    """Phần `cash_dividend_receiving_vnd` (đã nằm trong `cash`) thuộc mã trong
    `excluded_tickers`, CHƯA thật sự về ⇒ phải loại khỏi active_nav (§excluded_dividend).

    TÍN HIỆU DỪNG LOẠI là chính DNSE hạ `cash_dividend_receiving_vnd` (tiền đã settle thật),
    KHÔNG PHẢI `expected_arrival_date` đã qua. `expected_arrival_date` chỉ dùng để gắn cờ
    `overdue` (cảnh báo tiền về TRỄ hơn dự kiến) — arch-review 2026-09-19 chỉ ra bản đầu dùng
    ngày làm điều kiện DỪNG sẽ tự tái lập đúng bug đang sửa nếu tiền về trễ: qua ngày mà DNSE
    vẫn báo receivable, code cũ ngừng loại trong im lặng, active_nav phồng lại. Bản này không có
    đường đó — miễn `cash_dividend_receiving_vnd` còn > 0 (kẹp `remaining`) thì còn loại, bất kể
    ngày nào; nếu đã quá `expected_arrival_date` mà vẫn còn loại thì chỉ khác ở chỗ `overdue=True`
    trong detail (để caller cảnh báo, KHÔNG đổi hành vi loại/không loại).

    `expected_arrival_date` sai định dạng (không phải ISO `YYYY-MM-DD`) hoặc entry không phải
    dict ⇒ NỔ lỗi rõ ràng (ValueError) — không đoán, không âm thầm loại vĩnh viễn/bỏ qua (§29).

    Trả (tổng cần trừ khỏi active_nav, chi tiết từng entry còn hiệu lực kèm `overdue`).
    """
    remaining = float(cash_dividend_receiving_vnd or 0)
    asof_date = _dt_stale.date.fromisoformat(asof_ref)
    pending, detail = 0.0, []
    for ent in dividend_receivable_config or []:
        if not isinstance(ent, dict):
            raise ValueError(f"excluded_dividend_receivable: entry không phải dict: {ent!r}")
        tk, arrival_raw = ent.get("ticker"), ent.get("expected_arrival_date")
        amt = float(ent.get("amount_vnd") or 0)
        if tk not in excluded_tickers or amt <= 0:
            continue
        overdue = False
        if arrival_raw:
            try:
                overdue = asof_date >= _dt_stale.date.fromisoformat(arrival_raw)
            except ValueError as e:
                raise ValueError(
                    f"excluded_dividend_receivable[{tk}]: expected_arrival_date không đúng "
                    f"ISO 'YYYY-MM-DD': {arrival_raw!r} ({e})") from e
        take = min(amt, remaining)
        if take <= 0:
            continue  # DNSE không còn báo receivable nào cho phần này ⇒ coi như tiền đã về
        pending += take
        remaining -= take
        detail.append({"ticker": tk, "amount_vnd": take,
                       "expected_arrival_date": arrival_raw, "overdue": overdue})
    return pending, detail


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


def bq_close_sql(tickers, as_of_date=None):
    """Giá Close của phiên MỚI NHẤT (≤ as_of_date) THEO TỪNG MÃ.

    Trước 2026-09-13 ngày giá = MAX(time) của mã đầu alphabet, áp cho cả danh mục ⇒ mã đó
    ngừng giao dịch/thiếu dòng thì mọi mã khác cũng lấy giá cũ (code-quality 2026-09-13).
    """
    tick_list = ",".join(f"'{t}'" for t in sorted(tickers))
    # [F1] `as_of_date=""` KHÔNG được âm thầm thành "TRUE" (= không lọc ngày). Chuỗi rỗng ở đây
    # chỉ có thể là một biến shell chưa set chảy xuống tới đây; nó có nghĩa "tôi ĐỊNH lọc theo
    # ngày" chứ không phải "tôi cố ý không lọc". Caller chuẩn hoá ở main(); dòng này là lớp thứ
    # hai để hàm không thể bị gọi sai từ chỗ khác. None = cố ý không lọc, vẫn hợp lệ.
    if as_of_date is not None and not str(as_of_date).strip():
        raise ValueError("bq_close_sql: as_of_date là chuỗi RỖNG — phải là None (cố ý không lọc "
                         "ngày) hoặc 'YYYY-MM-DD'. Chuỗi rỗng thành 'TRUE' = lấy phiên mới nhất "
                         "của mọi thời điểm, im lặng.")
    date_clause = (f"t.time <= '{as_of_date}'" if as_of_date else "TRUE")
    return f"""
    SELECT t.ticker, t.Close, CAST(t.time AS STRING) AS time
    FROM tav2_bq.ticker AS t
    WHERE t.ticker IN ({tick_list}) AND {date_clause}
    QUALIFY ROW_NUMBER() OVER (PARTITION BY t.ticker ORDER BY t.time DESC) = 1
    """


def parse_close_rows(rows):
    """rows BQ → ({tk: Close}, {tk: ngày giá} của các mã có ngày giá CŨ HƠN ngày mới nhất
    trong danh mục). Mã tụt ngày không bị bỏ — chỉ bị gọi tên để người vận hành thấy."""
    prices = {r["ticker"]: float(r["Close"]) for r in rows}
    dates = {r["ticker"]: str(r["time"]) for r in rows}
    newest = max(dates.values()) if dates else None
    lagging = {tk: d for tk, d in sorted(dates.items()) if d != newest}
    return prices, lagging, newest


def bq_close_prices(tickers, as_of_date=None):
    env = dict(os.environ)
    env["PATH"] = BQ_PATH_PREFIX + ":" + env.get("PATH", "")
    sql = bq_close_sql(tickers, as_of_date)
    cmd = ["bq", "query", "--use_legacy_sql=false",
           "--project_id=lithe-record-440915-m9", "--format=json",
           "--max_rows=5000", sql]
    out = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if out.returncode != 0:
        # `bq` ghi lỗi ra STDOUT chứ không phải stderr (kb/incidents/2026-08/
        # 2026-08-29-bq-error-on-stdout-empty-diagnosis.md) — chỉ đọc stderr thì
        # người vận hành nhận chuỗi RỖNG. Không đổi luồng, chỉ đổi chuỗi chẩn đoán.
        return None, (out.stderr.strip() or out.stdout.strip())
    prices, lagging, newest = parse_close_rows(json.loads(out.stdout))
    if lagging:
        print(f"⚠️ BQ: các mã có phiên giá cũ hơn {newest} (dùng giá phiên gần nhất của CHÍNH "
              f"mã đó — kiểm tra ngừng giao dịch/thiếu dòng): {lagging}", file=sys.stderr)
    return prices, None


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


def previous_stock_value(path):
    """total_stock_value của file active_nav lần trước; không có/đọc lỗi ⇒ 0 (account mới)."""
    try:
        with open(path, encoding="utf-8") as f:
            return float(json.load(f).get("total_stock_value") or 0)
    except (OSError, ValueError, AttributeError):
        return 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--account", required=True, help="label trong trading_bot_accounts.json")
    ap.add_argument("--account-id", default=None, help="override account_id nếu cần")
    ap.add_argument("--asof", default=None,
                    help="ngày giá đóng cửa (mặc định/hôm nay: DNSE live; ngày quá khứ: BQ)")
    ap.add_argument("--out", default=None)
    ap.add_argument("--confirm-flat", action="store_true",
                    help="xác nhận account ĐÃ bán sạch thật — cho ghi positions rỗng dù file "
                         "active_nav trước còn cổ phiếu")
    args = ap.parse_args()
    # [F1] `--asof ""` (hình dạng `--asof "$ASOF"` với biến CHƯA SET) là chuỗi RỖNG ⇒ FALSY ⇒
    # trượt qua CẢ BA tầng cùng lúc: chốt chặn ngay dưới, cổng §exdate_frame (`args.asof is
    # None`) và `bq_close_sql` (`if as_of_date else "TRUE"` = không lọc ngày). Mike chạy thật
    # trên file production: rc=0, canonical bị ghi đè, VPB = 38.530.800 (đúng con số bug gốc),
    # và tín hiệu duy nhất là ⚠️ chứ không phải ❌ ⇒ `cron_health_check.py` (pattern `^\s*❌`)
    # MÙ HẲN. Chuẩn hoá MỘT LẦN ở đây, đúng tiền lệ `park_holdings.py:550` (`asof or today_ict()`):
    # từ dòng này trở xuống `args.asof` chỉ có hai dạng — None, hoặc chuỗi ngày không rỗng.
    args.asof = (args.asof or "").strip() or None
    canonical_out = os.path.join(
        WC_ROOT, "data", "execution_logs", f"active_nav_{args.account}.json")
    out_path = args.out or canonical_out
    # [F2] Chốt chặn dưới đây từng kiểm `--out` CÓ/KHÔNG chứ không kiểm nó TRỎ ĐI ĐÂU, mà
    # CHÍNH thông điệp rc=6/rc=7 lại dạy người vận hành dùng `--out` ⇒ ai chép đúng đường dẫn
    # canonical vào đó (hoặc script hoá thành biến) là ghi số phồng với rc=0, không cảnh báo.
    # `realpath` để `./`, symlink và đường dẫn tương đối không lách qua được.
    writes_canonical = os.path.realpath(out_path) == os.path.realpath(canonical_out)

    # ── §exdate_frame [R4] — `--asof` QUÁ KHỨ KHÔNG được ghi đè file canonical ─────
    # Cổng §exdate_frame dưới đây chỉ chạy ở nhánh asof=hôm nay, nhưng `get_positions()`
    # LUÔN trả vị thế LIVE bất kể `--asof`. Nên sau một rc=6, đúng một lệnh
    # `--asof <hôm qua>` ghi CHÍNH con số phồng đó vào file canonical, không cảnh báo,
    # rc=0 — cổng fail-closed có lối vòng, và thông điệp rc=6 lại vừa bảo "chạy lại".
    # Lý lẽ "giá BQ quá khứ đã điều chỉnh hồi tố ⇒ cùng hệ với KL đã credit" KHÔNG cứu được
    # ca này: tháng 9/2026 đo được 8 sự kiện vendor CHƯA hồi tố, trong cửa sổ đó Close quá
    # khứ vẫn là giá cum nhân với KL đã credit = y nguyên bug.
    # Vẫn cho chạy để người vận hành đối chiếu/khảo sát — chỉ bắt nói rõ đích đến (§8:
    # output khảo sát không bao giờ được trỏ vào tên file canonical).
    if args.asof and args.asof != today_ict().isoformat() and writes_canonical:
        print(f"❌ --asof {args.asof!r} là ngày KHÁC hôm nay ⇒ TỪ CHỐI ghi đè {out_path}. "
              f"Vị thế luôn đọc LIVE (get_positions), giá lại lấy của {args.asof}: hai con số "
              f"KHÁC HỆ QUY CHIẾU, và cổng §exdate_frame (chặn đúng lớp lỗi đó) chỉ chạy ở "
              f"nhánh asof=hôm nay. Muốn khảo sát: thêm `--out <đường dẫn tạm>` — đường dẫn "
              f"KHÁC {canonical_out} (trỏ vào chính nó cũng bị từ chối y hệt). Muốn refresh "
              f"số sizing thật: bỏ `--asof`.", file=sys.stderr)
        sys.exit(7)

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
    asof_ref = args.asof or today_ict().isoformat()
    excluded_div_config = profile.get("excluded_dividend_receivable") or []
    if offbook and offbook_asof:
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
        # DNSE CÓ trả positions rỗng TẠM THỜI (dnse_raw_2026-08-20 SpaceX: 19:06:46 27 mã →
        # 19:07:16 0 mã → 19:07:46 27 mã). File trước còn cổ phiếu ⇒ coi là lỗi feed, FAIL-CLOSED
        # (không ghi NAV = cash+egg khai thiếu ~9 lần); bán sạch thật thì chạy lại với --confirm-flat.
        prev_stock = previous_stock_value(out_path)
        if prev_stock > 0 and not args.confirm_flat:
            print(f"❌ {args.account}: DNSE trả 0 vị thế nhưng {out_path} (lần trước) còn "
                  f"{prev_stock:,.0f}đ cổ phiếu ⇒ nghi lỗi feed tạm thời, KHÔNG ghi active_nav. "
                  f"Chạy lại; nếu account THẬT SỰ đã bán sạch: thêm --confirm-flat.",
                  file=sys.stderr)
            sys.exit(5)
        # VẪN ghi file (positions rỗng): return sớm để lại active_nav_{account}.json CŨ sống
        # tới 5 ngày ở consumer (ca account mới mở / sau PARK bán sạch — code-quality 2026-09-13).
        print(f"⚠️ Account {args.account} không có vị thế nào — "
              f"active_nav = cash + egg + offbook = {cash + egg_value + offbook:,.0f} "
              f"(cash {cash:,.0f}, egg {egg_value:,.0f}, offbook {offbook:,.0f})")
        prices, price_source = {}, {}
    else:
        prices, price_source, err = resolve_prices(tickers, args.asof)
        if prices is None:
            print(f"❌ Không lấy được giá BQ: {err}", file=sys.stderr)
            sys.exit(3)

    # ── §exdate_frame — "khối lượng của ai thì giá của người đó" ──────────────────
    # Tối T-1 của một GDKHQ, DNSE credit KL mới vào positions NGAY trong khi giá đóng cửa G1
    # của phiên hôm nay vẫn (đúng) là giá CÒN QUYỀN. Nhân chéo hai hệ = active_nav phồng
    # (đo thật VPB 2026-09-23: SpaceX +7.969.500đ, ZaloPay +8.694.000đ ⇒ plan 24/09 in
    # "NAV cơ sở 990.981.660" và sinh lệnh PARK_TRIM VPB trên rổ phồng). Xem bin/exdate_frame.py.
    # CHỈ chạy ở nhánh asof=hôm nay (nhánh --asof QUÁ KHỨ trộn giá BQ lịch sử với vị thế LIVE —
    # một vấn đề KHÁC). Để cổng này KHÔNG có lối vòng, nhánh kia đã bị chốt hai lớp ở trên:
    # `--asof` ngày khác hôm nay không có `--out` ⇒ rc=7, không chạm file canonical; có `--out`
    # ⇒ chạy nhưng in cảnh báo cổng BỊ TẮT (nhánh `elif tickers` cuối khối này).
    if tickers and (args.asof is None or args.asof == today_ict().isoformat()):
        import exdate_frame
        credited, blocked = exdate_frame.classify_positions(
            args.account, account_id, asof_ref, positions)
        for tk, detail in sorted(credited.items()):
            px_new, why = exdate_frame.verify_post_event_price(
                prices.get(tk), (positions[tk] or {}).get("marketPrice"),
                1.0 + float(detail["exercise_ratio"]))
            if px_new is None:
                blocked[tk] = (
                    f"broker ĐÃ credit sớm {detail['residual']:+,.0f}cp (khớp tỉ lệ "
                    f"{detail['exercise_ratio']} của {detail['event_code']} ex-date "
                    f"{detail['ex_date']}) nhưng KHÔNG dựng được giá cùng hệ: {why}")
                continue
            print(f"ℹ️ {tk}: broker đã CREDIT SỚM {detail['residual']:+,.0f}cp "
                  f"(KL {detail['qty_prev']:,.0f}→{detail['qty_now']:,.0f}, khớp tỉ lệ "
                  f"{detail['exercise_ratio']} của {detail['event_code']} ex-date "
                  f"{detail['ex_date']}) ⇒ định giá theo giá tham chiếu SAU sự kiện của CHÍNH "
                  f"bản ghi vị thế đó thay cho giá đóng cửa còn quyền {prices[tk]:,.0f}: {why}",
                  file=sys.stderr)
            prices[tk] = px_new
            price_source[tk] = "dnse_position_marketprice_corpaction"
        if blocked:
            # FAIL-CLOSED. active_nav là MẪU SỐ của mọi phép sizing (LAG_book, slot CAPIT,
            # trần %ADV) — ghi một con số có thể sai còn tệ hơn để consumer thấy file quá hạn
            # rồi lùi về nav_history (đường lùi có sẵn ở golive_recommend_v23, 5 ngày).
            # [R3] Đường phục hồi phải là việc CHÍNH script này chạy được. `corp_action_auto_confirm
            # .py` + `--from-raw` là đường của `daily_nav_snapshot`: nó đọc data/corp_actions.json
            # qua `confirmed_share_event_multiplier`. Script NÀY không đọc file đó ở bất kỳ nhánh
            # nào, nên "chờ auto_confirm rồi chạy lại" cho kết quả Y HỆT — lặp vô ích (§29).
            print(f"❌ {args.account}: KHỐI LƯỢNG vị thế đổi NGOÀI lệnh khớp thật và KHÔNG quy "
                  f"được về một hệ quy chiếu giá cho {len(blocked)} mã ⇒ KHÔNG ghi active_nav "
                  f"(giữ nguyên file cũ), CẦN NGƯỜI xử lý: "
                  + "; ".join(f"{t}: {w}" for t, w in sorted(blocked.items())) +
                  ". Việc phải làm: (1) mã 'KHÔNG dựng được giá cùng hệ' — NGƯỜI xác minh giá "
                  "tham chiếu sau sự kiện (bảng giá sở/HOSE, thông báo GDKHQ) rồi đối chiếu với "
                  "marketPrice broker; (2) mã 'CHƯA GIẢI THÍCH ĐƯỢC' — kiểm journal fill và lịch "
                  "corp-action theo đúng vế đã nêu trong từng dòng trên. Chạy lại khi CHƯA có "
                  "thêm bằng chứng sẽ cho kết quả Y HỆT: script này không đọc "
                  "data/corp_actions.json, `corp_action_auto_confirm.py`/`--from-raw` là đường "
                  "phục hồi của daily_nav_snapshot.py, KHÔNG phải của đây. Cần xem số mà không "
                  "ghi đè file sizing: chạy lại với `--out <đường dẫn tạm>`.",
                  file=sys.stderr)
            sys.exit(6)
    elif tickers:
        # [R4] asof khác hôm nay ⇒ cổng §exdate_frame KHÔNG chạy. Nói ra, đừng im lặng: nhánh
        # này chỉ tới được khi có `--out` (xem chốt chặn ngay sau parse_args), tức là output
        # KHÔNG phải file sizing canonical — nhưng người đọc con số vẫn cần biết nó chưa qua cổng.
        print(f"⚠️ --asof {args.asof!r} ≠ hôm nay ⇒ cổng §exdate_frame (KL và giá phải CÙNG hệ "
              f"quy chiếu) KHÔNG chạy cho bản chạy này. Vị thế vẫn là LIVE còn giá là của "
              f"{args.asof!r}: nếu trong khoảng đó có sự kiện tỉ lệ mà vendor CHƯA hồi tố cột "
              f"Close thì giá trị danh mục dưới đây PHỒNG theo hệ số sự kiện. Số này dùng để "
              f"đối chiếu, KHÔNG dùng làm mẫu số sizing.", file=sys.stderr)

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
    excluded_div_pending_vnd, excluded_div_pending_detail = excluded_dividend_pending(
        excluded, excluded_div_config, cash_detail.get("cash_dividend_receiving_vnd"), asof_ref)
    active_nav -= excluded_div_pending_vnd

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
    if excluded_div_pending_vnd:
        print(f"  − cổ tức phải thu của mã excluded (theo khai báo config, loại khỏi active_nav "
              f"tới khi tiền về): {excluded_div_pending_vnd:>16,.0f}")
        for d in excluded_div_pending_detail:
            flag = "  ⚠️ QUÁ HẠN dự kiến, DNSE vẫn báo receivable — cập nhật config" if d["overdue"] else ""
            print(f"    · {d['ticker']}: {d['amount_vnd']:,.0f}đ, dự kiến về "
                  f"{d['expected_arrival_date'] or '(chưa khai)'}{flag}")
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
    # Trừ phần đã loại khỏi active_nav ở trên (§excluded_dividend) trước khi so ngưỡng — phần đó
    # KHÔNG còn trong active_nav nên không thể "đếm 2 lần trong active_nav" nữa (R4, arch-review
    # 2026-09-19: bản trước chia div_recv GỘP cho active_nav ĐÃ TRỪ, cho tỷ lệ vô nghĩa).
    div_recv_remaining = (cash_detail.get("cash_dividend_receiving_vnd") or 0) - excluded_div_pending_vnd
    div_warning = None
    if active_nav > 0 and div_recv_remaining > 0.005 * active_nav:
        div_warning = (
            f"cổ tức phải thu {div_recv_remaining:,.0f}đ ({div_recv_remaining / active_nav:.2%} "
            f"active_nav, KHÔNG TÍNH phần mã excluded đã loại ở trên) đã nằm trong totalCash — "
            f"nếu cổ phiếu CHƯA qua ex-date thì active_nav đang đếm 2 lần khoản này "
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
        "excluded_dividend_receivable_pending_vnd": excluded_div_pending_vnd,
        "excluded_dividend_receivable_detail": excluded_div_pending_detail,
        "positions": [{"ticker": tk, "qty": qty, "price": px, "value": mv, "excluded": is_excl,
                        "price_source": price_source.get(tk, "?")}
                       for tk, qty, px, mv, is_excl in rows],
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\nGhi ra: {out_path}")


if __name__ == "__main__":
    main()
