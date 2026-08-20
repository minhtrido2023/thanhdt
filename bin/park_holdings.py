#!/usr/bin/env python3
"""Dựng lại vị thế THEO BOOK (PARK/LAG/CAPIT/...) cho một account tại một ngày.

VÌ SAO (§A7 báo cáo `park_unpark_live_wiring_20260803.md`): live KHÔNG có sổ quy vị thế về
book, nên `park_mv_live` trước đây phải SUY LUẬN THEO TÊN MÃ — cách đó đã sai thật với VPB
(nằm cả LAG lẫn PARK) và với VND. Không có sổ này thì L1 (park-target compliance) không có
đầu vào đúng, và lỗi sẽ là dạng IM LẶNG: park_mv thấp hơn thực tế ⇒ "chưa vượt target" ⇒
không trim gì cả.

CƠ CHẾ (đúng §F2 của thiết kế):
  điểm xuất phát = bootstrap snapshot ngày 0 (đã được USER duyệt), rồi FIFO tiến lên bằng
  các dòng FILL của journal executor SAU thời điểm snapshot.

  1. FILL `qty` là TÍCH LUỸ THEO `child_oid`, KHÔNG phải delta ⇒
     delta = qty(dòng này) − qty(dòng trước CÙNG child_oid). Cộng dồn thô = đếm trùng
     (bẫy số 1 của file journal).
  2. side=buy  → push lô {ticker, book, play_type, entry_date, qty, price}.
  3. side=sell → tiêu thụ FIFO **TRONG CÙNG BOOK** của lệnh bán. Đây chính là chỗ cách
     suy-luận-theo-tên chết.
  4. Lệnh bán KHÔNG có tag book (journal cũ 10 cột, hoặc GHOST_ORDER) → FIFO theo ticker
     oldest-first + gắn cờ UNVERIFIED cho toàn bộ ticker đó. Số UNVERIFIED **CẤM** dùng làm
     cơ sở sinh lệnh trim (§21 coding_guidelines — cùng tinh thần "không đưa số chưa đối
     soát vào quyết định").
  5. park_mv = Σ(qty × marketPrice của broker) trên các lô book == "PARK".
     Giá từ DNSE, KHÔNG từ BQ (§6 bright-line: BQ same-day = giá hôm qua).

ĐỐI SOÁT BẮT BUỘC: Σ qty các lô mỗi ticker phải bằng `openQuantity` của broker. Lệch ⇒ BÁO
RÕ (`reconcile.ok=False`), **KHÔNG tự sửa lô cho khớp** (§5 coding_guidelines: không
đoán-rồi-gộp). Caller phải tự quyết định có dùng số hay không.

Tương thích ngược: journal cũ 10 cột / mới 12 cột đều đọc được — csv.DictReader +
row.get("book", ""), tuyệt đối không đọc theo chỉ số cột.

Dùng như thư viện:
    from park_holdings import park_holdings
    h = park_holdings("SpaceX")            # asof mặc định = hôm nay (ICT)
    h["park_mv_vnd"], h["reconcile"]["ok"]

Dùng như CLI:
    python3 mike/bin/park_holdings.py --account SpaceX [--asof 2026-08-03] [--json]
"""
import argparse
import csv
import datetime as dt
import glob
import json
import math
import os
import re
import sys
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from corp_actions import load_corp_actions, validate as validate_action   # noqa: E402

ICT = ZoneInfo("Asia/Ho_Chi_Minh")          # §16: neo TZ tường minh, không tin TZ của process
WC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXEC_DIR = os.path.join(WC_ROOT, "data", "execution_logs")
PLAN_DIR = os.path.join(WC_ROOT, "data", "trade_plans")

# Ánh xạ tên `book` của plan → tên sổ chuẩn. GIỮ ĐỒNG BỘ với bootstrap builder
# (mike/agents/Taylor/bootstrap_book_20260804/make_snapshot.py::BOOK_MAP) — hai bên lệch nhau
# thì lô bootstrap và lô replay rơi vào 2 sổ khác nhau và FIFO trong-cùng-book sẽ sai.
BOOK_MAP = {
    "custom30V_parking": "PARK",
    "PARK": "PARK",
    "CAPIT": "CAPIT",
    "LAG": "LAG",
    "BAL": "BAL",
    "DISCRETIONARY_SPECIAL": "DISCRETIONARY_SPECIAL",
    "legacy_orphan": "LEGACY_ORPHAN",
    "LEGACY_ORPHAN": "LEGACY_ORPHAN",
    "EXCLUDED": "EXCLUDED",
}
BOOTSTRAP_GLOB = "bootstrap_book_snapshot_{label}_*.json"
_JOURNAL_RE = re.compile(r"^exec_(?P<label>.+)_(?P<date>\d{4}-\d{2}-\d{2})_journal\.csv$")


def today_ict():
    return dt.datetime.now(ICT).date().isoformat()


def norm_book(raw):
    raw = (raw or "").strip()
    if not raw:
        return ""
    return BOOK_MAP.get(raw, raw.upper())


# ───────────────────────────────────────────────────────────── nguồn dữ liệu

def account_profile(label):
    path = os.path.join(WC_ROOT, "secrets", "trading_bot_accounts.json")
    for a in json.load(open(path, encoding="utf-8")).get("accounts", []):
        if a.get("label") == label:
            return a
    raise SystemExit(f"[park_holdings] không có account '{label}' trong {path}")


def load_bootstrap(label, plan_dir=PLAN_DIR):
    """Snapshot ngày 0 đã được USER duyệt. Bắt buộc `_status` bắt đầu bằng APPROVED —
    một snapshot mới chỉ là ĐỀ XUẤT không được phép làm điểm xuất phát cho số đi vào lệnh."""
    cands = sorted(glob.glob(os.path.join(plan_dir, BOOTSTRAP_GLOB.format(label=label))))
    if not cands:
        raise SystemExit(f"[park_holdings] THIẾU bootstrap snapshot cho '{label}' trong {plan_dir} — "
                         f"không có ngày 0 thì sổ chỉ thấy phần mua SAU cutover ⇒ park_mv THẤP HƠN "
                         f"thực tế ⇒ L1 im lặng không trim. Xem §F3 thiết kế.")
    path = cands[-1]
    snap = json.load(open(path, encoding="utf-8"))
    status = str(snap.get("_status", ""))
    if not status.upper().startswith("APPROVED"):
        raise SystemExit(f"[park_holdings] {os.path.basename(path)} có _status='{status[:40]}' — "
                         f"CHƯA được duyệt, không dùng làm ngày 0.")
    if not snap.get("reconcile_ok"):
        raise SystemExit(f"[park_holdings] {os.path.basename(path)} có reconcile_ok=false — "
                         f"ngày 0 chưa khớp broker, không dùng.")
    return snap, path


def journal_files(label, since_date, until_date, exec_dir=EXEC_DIR):
    """Journal của ĐÚNG account này, ngày trong [since_date, until_date], sắp theo NGÀY
    parse ra date (không sort chuỗi tên file — §F2 bước 1)."""
    out = []
    for p in glob.glob(os.path.join(exec_dir, "exec_*_journal.csv")):
        m = _JOURNAL_RE.match(os.path.basename(p))
        if not m or m.group("label") != label:
            continue
        d = m.group("date")
        if since_date <= d <= until_date:
            out.append((d, p))
    return [p for _, p in sorted(out)]


def _stock_block_all_zero(st):
    """DNSE thỉnh thoảng trả block `stock` TOÀN SỐ 0 (lỗi API tạm thời, KHÔNG phải tiền về 0).

    Sự cố THẬT 2026-07-27: cả 2 bản đọc 19:04:59 và 19:10:20 đều toàn 0, `daily_nav_snapshot.py`
    ghi NAV thiếu 32.011.420đ (−3,83%). Nó đã được vá; chỗ này KHÔNG — và với mẫu số pool thì
    hậu quả nặng hơn NAV sai: totalCash=0 ⇒ pool = park_mv ⇒ PARK "chiếm 100% pool" ⇒ L1 đề xuất
    BÁN GẦN SẠCH sổ PARK. Nên fail-closed. (quant-skeptic REFUTED vòng 2, 2026-08-09 — bản vá
    trước chỉ chặn field THIẾU (None), không chặn field CÓ MÀ BẰNG 0.)

    Điều kiện giống hệt `daily_nav_snapshot.py:439` — nếu sửa một nơi, sửa cả hai (đã lệch 1 lần).
    """
    numeric = [v for v in st.values()
               if isinstance(v, (int, float)) and not isinstance(v, bool)]
    return bool(numeric) and not any(numeric)


def _cash_fields_all_zero(st):
    """CHỈ ba field tiền (`totalCash`/`totalDebt`/`availableCash`) đều CÓ MẶT và đều bằng 0.

    Vì sao cần THÊM `_stock_block_all_zero`: lỗi feed có thể chỉ ăn phần tiền mà vẫn để một
    field khác khác 0 (`depositInterest` cộng dồn liên tục nên hiếm khi đúng 0) — lúc đó test
    "toàn block bằng 0" trả False mà mẫu số pool vẫn hỏng đúng kiểu tệ nhất: pool = park_mv
    ⇒ PARK chiếm 100% pool ⇒ L1 đề xuất bán gần sạch sổ.

    CỐ Ý fail-closed cả trên trạng thái THẬT "đã đầu tư hết, không còn đồng nào": không phân
    biệt được nó với lỗi feed, và hướng sai của việc chặn (không bán gì) rẻ hơn nhiều so với
    hướng sai của việc tin (bán gần sạch sổ PARK). Thiếu field ⇒ trả False, vì `_f_or_none`
    đã cho None và consumer chặn theo None rồi.
    """
    keys = ("totalCash", "totalDebt", "availableCash")
    vals = [st.get(k) for k in keys]
    if any(v is None for v in vals):
        return False
    return all(float(v) == 0 for v in vals)


def _cash_fields_inconsistent(st):
    """`totalCash` < `availableCash` — BẤT BIẾN kế toán bị vi phạm ⇒ block tiền không đáng tin.

    totalCash = availableCash + tiền bán chưa settle + cổ tức chờ + lãi tiền gửi, nên nó KHÔNG
    BAO GIỜ nhỏ hơn availableCash. Kiểm hằng đẳng thức ZaloPay 2026-08-07: 5.818.854 +
    6.453.500 (cổ tức) + 318 (lãi) = 12.272.672 = totalCash, khớp tuyệt đối; SpaceX cùng ngày
    203.656.265 ≥ 4.821.143.

    VÌ SAO cần THÊM `_cash_fields_all_zero` (quant-skeptic vòng 3, 2026-08-09): hai phép thử kia
    đòi CẢ BA field cùng = 0, nên một lỗi feed chỉ ăn HAI trong ba (totalCash=0, totalDebt=0
    nhưng availableCash còn sống) lọt qua nguyên vẹn — reviewer dựng lại được và nó cho TRIM
    BÁN SẠCH 100% sổ PARK, đúng thảm hoạ ban đầu bằng một đường khác. Bất biến này bắt đúng ca
    đó (0 < 5.000.000) mà KHÔNG phụ thuộc field nào bằng 0.

    Cả hai số đọc từ CÙNG một bản ghi `balances` nên không có lệch do đọc hai thời điểm.
    Thiếu field ⇒ False (để `_f_or_none`→None lo, không nhập nhèm hai chế độ hỏng).
    """
    tc, ac = st.get("totalCash"), st.get("availableCash")
    if tc is None or ac is None:
        return False
    return float(tc) < float(ac)


def _f_or_none(v):
    """float(v) hoặc None — KHÔNG rơi về 0: 0 và 'không đo được' phải phân biệt được, vì
    consumer fail-closed dựa vào None (0 đ tiền mặt là trạng thái hợp lệ, thiếu field thì không)."""
    return None if v is None else float(v)


def read_broker_snapshot(label, account_no, asof, exec_dir=EXEC_DIR):
    """Vị thế + tiền của broker tại `asof`.

    asof == hôm nay  → gọi DNSE LIVE (§6: same-day không bao giờ đọc BQ, và file
                        dnse_raw hôm nay có thể chưa có bản ghi nào).
    asof quá khứ     → đọc data/execution_logs/dnse_raw_{asof}.jsonl, LỌC accountNo ngay
                        dòng đầu (§12 — file này DÙNG CHUNG cho mọi account).

    Trả (positions {tk: {qty, market_price}}, cash_available, meta).

    `meta` LUÔN mang thêm `total_cash_vnd` + `dividend_receiving_vnd` (None nếu DNSE không trả
    field đó). VÌ SAO tách khỏi `cash_available` thay vì đổi tại chỗ (bug 2026-08-09, job
    Taylor_20260809_150316): HAI consumer cần HAI ngữ nghĩa KHÁC nhau —
      · L1 `compute_park_trim` cần MẪU SỐ "toàn bộ vốn nhàn rỗi tôi sở hữu"  → totalCash.
      · L2 `compute_jit_unpark` cần "tiền tôi TIÊU được ngay phiên tới"      → availableCash.
    `availableCash` KHÔNG gồm tiền bán chưa settle: đo thật 2026-08-07 SpaceX, bán 189,4tr lúc
    trong phiên mà availableCash 11:25 và 19:10 GIỐNG HỆT nhau (4.821.143đ), toàn bộ 189,06tr
    chỉ hiện ở totalCash. Dùng nó làm mẫu số ⇒ pool co lại ĐÚNG BẰNG lượng vừa bán ⇒ tỷ lệ
    PARK/pool gần như không giảm ⇒ vòng lặp tự kích (xem `compute_park_trim` §pool).
    """
    if asof == today_ict():
        sys.path.insert(0, WC_ROOT)
        from trading_bot.brokers import DNSEBroker
        b = DNSEBroker(account_id=account_no, credentials_file=None, label=label)
        b.connect()
        # DNSE trả một dòng cho MỖI loan package cùng mã (y hệt bug ZaloPay 2026-08-11
        # BID/MBB/VCB đã vá ở DNSEBroker.get_positions(), commit 36846b8) — dùng LẠI hàm đã
        # dedupe/aggregate đó thay vì tự parse client.positions() lần nữa (từng lặp lại đúng
        # bug bằng dict-overwrite ở đây, gây BLOCKED_RECONCILE giả cho L1 park-trim).
        raw_pos = b.get_positions()
        bal = b.client.balances(account_no)
        pos = {sym: {"qty": p["total"], "market_price": float(p.get("marketPrice") or 0),
                     "sellable": p.get("sellable", p["total"])}
               for sym, p in raw_pos.items() if p.get("total", 0) > 0}
        braw = (bal[0] if isinstance(bal, list) and bal else bal) or {}
        # Trứng vàng — sibling của "stock" trong payload gốc (giống compute_active_nav.py §cash),
        # phải đọc TRƯỚC khi st bị thu hẹp về block "stock" ở dòng dưới.
        egg_value = float((braw.get("egg") or {}).get("totalValue") or 0) \
            if isinstance(braw, dict) else 0.0
        st = braw.get("stock", braw) if isinstance(braw, dict) else {}
        cash = float(st.get("availableCash") or 0)   # tiền TIÊU ĐƯỢC ngay (L2 dùng)
        _zero = (_stock_block_all_zero(st) or _cash_fields_all_zero(st)
                 or _cash_fields_inconsistent(st))
        return pos, cash, {"source": "dnse_live", "asof": asof,
                           "total_cash_vnd": None if _zero else _f_or_none(st.get("totalCash")),
                           "dividend_receiving_vnd": _f_or_none(st.get("cashDividendReceiving")),
                           "total_debt_vnd": None if _zero else _f_or_none(st.get("totalDebt")),
                           "egg_assets_vnd": egg_value,
                           "balance_all_zero": _zero,
                           "ts": dt.datetime.now(ICT).isoformat(timespec="seconds")}

    path = os.path.join(exec_dir, f"dnse_raw_{asof}.jsonl")
    if not os.path.exists(path):
        raise SystemExit(f"[park_holdings] không có {path} để đối soát tại asof={asof}")
    pos, cash, ts_pos, ts_bal = {}, None, None, None
    total_cash = div_recv = total_debt = None
    egg_assets = 0.0
    all_zero = False
    for line in open(path, encoding="utf-8"):
        try:
            rec = json.loads(line)
        except Exception:
            continue
        if str(rec.get("account_no")) != str(account_no):     # §12 — lọc TRƯỚC mọi phép tính
            continue
        payload = rec.get("payload") or {}
        if rec.get("kind") == "positions":
            cur = {}
            for p in (payload.get("positions") or payload.get("data") or []):
                if str(p.get("accountNo") or account_no) != str(account_no):
                    continue
                if str(p.get("status", "OPEN")).upper() == "CLOSED":
                    continue
                q = int(p.get("openQuantity") or 0)
                if q > 0 and p.get("symbol"):
                    sym = p["symbol"]
                    mp = float(p.get("marketPrice") or 0) or None
                    sellable = int(p.get("tradeQuantity") or 0)
                    # cùng bug loan-package-per-dòng như nhánh "hôm nay" ở trên — cộng gộp
                    # thay vì ghi đè (nhánh này còn đọc TRỰC TIẾP jsonl, không qua
                    # DNSEBroker.get_positions() được, nên phải tự lặp lại đúng logic dedupe).
                    prev = cur.get(sym)
                    if prev:
                        q += prev["qty"]
                        sellable += prev["sellable"]
                        if mp is None:
                            mp = prev.get("market_price")
                    cur[sym] = {"qty": q, "market_price": mp or 0.0, "sellable": sellable}
            if cur and (ts_pos is None or rec.get("ts", "") >= ts_pos):
                pos, ts_pos = cur, rec.get("ts", "")          # bản ghi MỚI NHẤT trong ngày
        elif rec.get("kind") == "balances":
            st = payload.get("stock", payload) if isinstance(payload, dict) else {}
            if "availableCash" in st and (ts_bal is None or rec.get("ts", "") >= ts_bal):
                cash, ts_bal = float(st.get("availableCash") or 0), rec.get("ts", "")
                all_zero = (_stock_block_all_zero(st) or _cash_fields_all_zero(st)
                            or _cash_fields_inconsistent(st))
                total_cash = None if all_zero else _f_or_none(st.get("totalCash"))
                div_recv = _f_or_none(st.get("cashDividendReceiving"))
                total_debt = None if all_zero else _f_or_none(st.get("totalDebt"))
                # Trứng vàng — sibling của "stock" trong payload gốc, cùng bản ghi balances.
                egg_assets = float((payload.get("egg") or {}).get("totalValue") or 0) \
                    if isinstance(payload, dict) else 0.0
    if not pos:
        raise SystemExit(f"[park_holdings] {path} không có bản ghi positions nào của account "
                         f"{account_no} — không đối soát được")
    return pos, cash, {"source": os.path.basename(path), "asof": asof,
                       "total_cash_vnd": total_cash, "dividend_receiving_vnd": div_recv,
                       "total_debt_vnd": total_debt, "egg_assets_vnd": egg_assets,
                       "balance_all_zero": all_zero,
                       "ts_positions": ts_pos, "ts_balances": ts_bal}


# ─────────────────────────────────────────────────────────────── sổ lô FIFO

class LotBook:
    """Sổ lô theo (ticker, book). Bán tiêu thụ FIFO TRONG CÙNG BOOK."""

    def __init__(self):
        self.lots = []              # thứ tự append = thứ tự thời gian
        self.unverified = set()     # ticker có ít nhất một thao tác không xác định được book
        self.warnings = []

    def buy(self, ticker, book, qty, price, date, source, play_type=""):
        if qty <= 0:
            return
        self.lots.append({"ticker": ticker, "book": book, "play_type": play_type,
                          "entry_date": date, "qty": int(qty), "price": float(price or 0),
                          "source": source})

    def sell(self, ticker, book, qty, date, source):
        """Trả số lượng KHÔNG khớp được lô nào (thừa) — caller phải báo, không tự bỏ qua."""
        if qty <= 0:
            return 0
        remain = int(qty)
        if book:
            pool = [l for l in self.lots if l["ticker"] == ticker and l["book"] == book]
        else:
            # §F2 bước 4: bán không tag book → FIFO theo ticker oldest-first + cờ UNVERIFIED
            pool = [l for l in self.lots if l["ticker"] == ticker]
            self.unverified.add(ticker)
            self.warnings.append(f"{date} SELL {ticker} {qty}cp KHÔNG có tag book ({source}) → "
                                 f"FIFO oldest-first toàn ticker, {ticker} gắn cờ UNVERIFIED")
        for lot in pool:
            if remain <= 0:
                break
            take = min(lot["qty"], remain)
            lot["qty"] -= take
            remain -= take
        self.lots = [l for l in self.lots if l["qty"] > 0]
        if remain > 0:
            self.unverified.add(ticker)
            self.warnings.append(f"{date} SELL {ticker} {qty}cp ({source}) THỪA {remain}cp so với "
                                 f"lô đang có trong sổ book='{book or 'KHÔNG TAG'}' → {ticker} UNVERIFIED")
        return remain

    def corp_action_split(self, ticker, multiplier, ex_date, effective_ts, source,
                          event_id=""):
        """Sự kiện doanh nghiệp làm ĐỔI SỐ LƯỢNG (chia tách / thưởng / cổ tức cổ phiếu).

        Nhân `qty` và chia `price` của các lô ĐƯỢC HƯỞNG QUYỀN ⇒ tổng giá vốn (qty×price) BẤT
        BIẾN. Đây đúng cơ chế broker đã làm (đo 2026-08-05: SpaceX VHM 500@149.800 → 1000@74.900,
        ZaloPay 300@148.633 → 600@74.317).

        ĐƯỢC HƯỞNG QUYỀN = lô có `entry_date < ex_date`. Lô mua TỪ ex_date trở đi không hưởng
        quyền ⇒ KHÔNG nhân. Đây là lý do `ex_date` phải tách khỏi `effective_ts` (ngày broker
        thật sự đổi số dư) — ca VHM 2026-08 hai ngày này lệch nhau đúng một phiên.

        LÀM TRÒN Ở MỨC VỊ THẾ, KHÔNG PHẢI MỨC LÔ. Tỉ lệ hiếm khi chia hết cho từng lô: ca MBB
        2026-08-11 (cổ tức CP 15%) ZaloPay giữ 202cp qua 2 lô 100+102 — 100×1,15=115 nguyên
        nhưng 102×1,15=117,3 thì không. Broker KHÔNG làm tròn từng lô: nó tính quyền trên TỔNG
        vị thế rồi làm tròn XUỐNG một lần (202×1,15=232,3 → 232), phần lẻ trả tiền/bỏ. Vì vậy
        ở đây cũng làm tròn đúng một lần trên tổng, rồi chia phần dôi về từng lô bằng
        largest-remainder (Hamilton) — tie-break theo thứ tự lô trong sổ nên hoàn toàn tất định.
        Giá vốn mỗi lô đặt lại = (tổng giá vốn CŨ của lô) / (qty MỚI của lô) ⇒ tổng giá vốn bất
        biến ở CẢ mức lô lẫn mức vị thế, kể cả khi hệ số hiệu dụng ≠ multiplier khai báo (MBB
        ZaloPay: 232/202 = 1,14851 chứ không phải 1,15 — và broker cũng hạ costPrice theo đúng
        1,14851, đã đối chiếu khớp tới đồng).

        ĐÂY KHÔNG PHẢI "ĐOÁN RỒI GỘP" (§5): quy tắc làm tròn nằm sai chỗ sẽ lộ ra NGAY ở cổng
        đối soát bên dưới (Σ lô phải bằng `openQuantity` broker) — sai thì BLOCKED chứ không
        lặng lẽ trôi. Cái phải fail-closed là "sự kiện có thật không" (cổng `_status: CONFIRMED`
        + ≥2 nguồn độc lập trong `corp_actions.json`), không phải phép chia.
        """
        pool = [l for l in self.lots if l["ticker"] == ticker]
        if not pool:
            return 0                                   # không giữ mã này — no-op, không phải lỗi
        entitled = [l for l in pool if l["entry_date"] < ex_date]
        if not entitled:
            self.warnings.append(
                f"{effective_ts[:10]} corp action {event_id or ticker} ×{multiplier}: đang giữ "
                f"{ticker} nhưng KHÔNG lô nào có entry_date < ex_date {ex_date} ⇒ không hưởng "
                f"quyền, sổ giữ nguyên")
            return 0

        old_total = sum(l["qty"] for l in entitled)
        # +1e-9 chống hụt một đơn vị do sai số nhị phân (1100×1,15 ra 1265,0000000000002 nhưng
        # 202×1,15 ra 232,29999999999998 — không cộng epsilon thì có ca floor xuống 1264).
        new_total = int(math.floor(old_total * multiplier + 1e-9))
        extra = new_total - old_total
        if extra <= 0:
            self.warnings.append(
                f"{effective_ts[:10]} corp action {event_id or ticker} ×{multiplier}: vị thế "
                f"{old_total}cp quá nhỏ, quyền làm tròn xuống còn 0cp ⇒ sổ giữ nguyên")
            return 0

        # Hamilton: mỗi lô nhận phần nguyên của quyền chính xác, phần dôi do làm tròn xuống ở
        # mức vị thế chia tiếp cho các lô có phần lẻ lớn nhất.
        raw = [l["qty"] * (multiplier - 1.0) for l in entitled]
        add = [int(math.floor(r + 1e-9)) for r in raw]
        rem = extra - sum(add)
        if rem < 0 or rem > len(entitled):
            self.unverified.add(ticker)
            self.warnings.append(
                f"{effective_ts[:10]} corp action {event_id or ticker} ×{multiplier}: chia phần "
                f"dôi ra số vô lý (rem={rem}, {len(entitled)} lô) ⇒ KHÔNG áp dụng, {ticker} "
                f"UNVERIFIED — cần người xử lý")
            return 0
        order = sorted(range(len(entitled)), key=lambda i: (-(raw[i] - add[i]), i))
        for i in order[:rem]:
            add[i] += 1

        for l, a in zip(entitled, add):
            cost = l["qty"] * float(l["price"])         # tổng giá vốn lô — BẤT BIẾN qua sự kiện
            l["qty"] = l["qty"] + a
            l["price"] = cost / l["qty"] if l["qty"] else 0.0
            l["corp_actions"] = l.get("corp_actions", []) + [event_id or f"{ticker}×{multiplier}"]
        eff = new_total / old_total
        self.warnings.append(
            f"{effective_ts[:10]} corp action {event_id or ticker} ×{multiplier} (ex {ex_date}, "
            f"{source}): {len(entitled)} lô {ticker} {old_total}→{new_total}cp (hệ số hiệu dụng "
            f"{eff:.6f} sau làm tròn mức vị thế) — tổng giá vốn không đổi")
        return len(entitled)

    def by_ticker_qty(self):
        out = {}
        for l in self.lots:
            out[l["ticker"]] = out.get(l["ticker"], 0) + l["qty"]
        return out


def _fill_deltas(path):
    """Sinh (ts, ticker, side, book, play_type, delta_qty, price) cho từng dòng FILL.

    delta = qty(dòng này) − qty(dòng TRƯỚC CÙNG child_oid). Đây là điểm chết người: cộng dồn
    thô Σqty sẽ đếm trùng vì `qty` là TÍCH LUỸ theo child_oid (đo thật trên
    exec_SpaceX_2026-07-29_journal.csv: 3 dòng FILL cùng parent, qty tăng dần).
    """
    prev = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):                # DictReader: journal 10 cột và 12 cột
            if (row.get("event") or "") != "FILL":   # đều đọc được, không theo vị trí cột
                continue
            try:
                cum = int(round(float(row.get("qty") or 0)))
            except (TypeError, ValueError):
                continue
            oid = row.get("child_oid") or f"__noid__{row.get('parent_id')}"
            delta = cum - prev.get(oid, 0)
            prev[oid] = cum
            if delta <= 0:
                continue
            try:
                px = float(row.get("price") or 0)
            except (TypeError, ValueError):
                px = 0.0
            yield {"ts": row.get("ts") or "", "ticker": row.get("ticker") or "",
                   "side": (row.get("side") or "").lower(),
                   "book": norm_book(row.get("book", "")),
                   "play_type": row.get("play_type", "") or "",
                   "qty": delta, "price": px, "parent_id": row.get("parent_id") or ""}


def park_holdings(account_label, asof=None, plan_dir=PLAN_DIR, exec_dir=EXEC_DIR,
                  broker=None, corp_actions=None):
    """Vị thế theo book tại `asof` (mặc định hôm nay ICT).

    `broker` = (positions, cash, meta) truyền sẵn — chỉ dùng cho selfcheck; production để None.
    `corp_actions` = danh sách record truyền sẵn — cũng chỉ cho selfcheck; production để None
    (đọc `data/corp_actions.json`, và CHỈ record đã `CONFIRMED` — xem `mike/bin/corp_actions.py`).
    """
    asof = asof or today_ict()
    prof = account_profile(account_label)
    account_no = prof.get("account_id")
    excluded = set(prof.get("excluded_tickers") or [])

    snap, snap_path = load_bootstrap(account_label, plan_dir)
    day0 = snap["day0_date"]
    snap_ts = (snap.get("broker_source") or {}).get("ts") or ""
    if asof < day0:
        raise SystemExit(f"[park_holdings] asof={asof} TRƯỚC ngày 0 của bootstrap ({day0}) — "
                         f"sổ không lùi được về trước snapshot.")

    book = LotBook()
    for p in snap["positions"]:
        book.buy(p["ticker"], norm_book(p.get("book")), p["qty"], p.get("cost_price_vnd"),
                 p.get("entry_date") or day0, "bootstrap", p.get("play_type", ""))
        if p.get("needs_user_confirmation") and not str(snap.get("_status", "")).upper().startswith("APPROVED"):
            book.unverified.add(p["ticker"])

    # Replay: journal từ ngày 0 trở đi, và CHỈ các dòng FILL sau thời điểm chụp snapshot
    # (chống đếm trùng phần đã nằm trong bootstrap). Corp action đi CHUNG một dòng thời gian với
    # fill — một lô chỉ được nhân nếu nó đã tồn tại trong sổ tại thời điểm sự kiện, nên thứ tự
    # thời gian là bắt buộc, không phải "chạy hai vòng cho gọn".
    acts = load_corp_actions() if corp_actions is None else [validate_action(a) for a in corp_actions]
    acts = [a for a in acts
            if (not snap_ts or a["broker_effective_ts"] > snap_ts)   # đã nằm trong bootstrap rồi
            and a["broker_effective_ts"][:10] <= asof]               # chưa tới thì chưa áp
    # khoá sắp xếp: (ts, 0)=fill trước, (ts, 1)=corp action sau ⇒ lô khớp CÙNG thời điểm vẫn kịp
    # vào sổ để được hưởng quyền.
    timeline = [(ev["ts"], 0, ev, os.path.basename(path))
                for path in journal_files(account_label, day0, asof, exec_dir)
                for ev in _fill_deltas(path)
                if not (snap_ts and ev["ts"] and ev["ts"] <= snap_ts)]
    timeline += [(a["broker_effective_ts"], 1, a, "corp_actions.json") for a in acts]
    timeline.sort(key=lambda x: (x[0], x[1]))

    applied, applied_acts = [], []
    for _ts, kind, ev, fname in timeline:
        if kind == 1:
            n = book.corp_action_split(ev["ticker"], ev["qty_multiplier"], ev["ex_date"],
                                       ev["broker_effective_ts"], fname, ev["id"])
            applied_acts.append(dict(ev, lots_adjusted=n))
            continue
        src = f"{fname}:{ev['parent_id']}"
        if ev["side"] == "buy":
            book.buy(ev["ticker"], ev["book"], ev["qty"], ev["price"], ev["ts"][:10], src,
                     ev["play_type"])
        elif ev["side"] == "sell":
            book.sell(ev["ticker"], ev["book"], ev["qty"], ev["ts"][:10], src)
        else:
            book.unverified.add(ev["ticker"])
            book.warnings.append(f"{ev['ts'][:10]} side='{ev['side']}' lạ ({src}) → "
                                 f"{ev['ticker']} UNVERIFIED")
            continue
        applied.append(ev)

    # Cửa sổ xám: mua SAU khi broker đã credit nhưng TRƯỚC ex_date. Lô đó vẫn được hưởng quyền
    # (entry_date < ex_date) nhưng broker sẽ credit nó ở một nhịp khác mà ta không quan sát được
    # ⇒ không tự đoán, gắn cờ để cổng UNVERIFIED chặn sinh lệnh.
    for a in applied_acts:
        gray = [ev for ev in applied if ev["ticker"] == a["ticker"] and ev["side"] == "buy"
                and ev["ts"] >= a["broker_effective_ts"] and ev["ts"][:10] < a["ex_date"]]
        if gray:
            book.unverified.add(a["ticker"])
            book.warnings.append(
                f"{a['ticker']} có {len(gray)} lệnh MUA khớp sau lúc broker credit "
                f"({a['broker_effective_ts']}) nhưng trước ex_date {a['ex_date']} — phần quyền của "
                f"các lô này credit ở nhịp khác, KHÔNG tự suy ⇒ UNVERIFIED")

    positions, cash, bmeta = broker if broker else read_broker_snapshot(
        account_label, account_no, asof, exec_dir)

    # ── Đối soát: Σ lô mỗi ticker PHẢI bằng openQuantity broker. Lệch → BÁO, KHÔNG tự sửa.
    ledger_qty = book.by_ticker_qty()
    mismatches = []
    for tk in sorted(set(ledger_qty) | set(positions)):
        lq, bq = ledger_qty.get(tk, 0), positions.get(tk, {}).get("qty", 0)
        if lq != bq:
            mismatches.append({"ticker": tk, "ledger_qty": lq, "broker_qty": bq, "diff": lq - bq})
            book.unverified.add(tk)
    reconcile = {"ok": not mismatches, "n_tickers": len(set(ledger_qty) | set(positions)),
                 "mismatches": mismatches, "broker": bmeta}

    # ── Định giá theo marketPrice broker (§6: KHÔNG BQ)
    by_book, park_lots = {}, []
    for l in book.lots:
        px = positions.get(l["ticker"], {}).get("market_price", 0)
        mv = l["qty"] * px
        b = by_book.setdefault(l["book"] or "UNTAGGED",
                               {"qty": 0, "mv_vnd": 0.0, "tickers": set()})
        b["qty"] += l["qty"]
        b["mv_vnd"] += mv
        b["tickers"].add(l["ticker"])
        if l["book"] == "PARK":
            park_lots.append(dict(l, market_price=px, mv_vnd=mv))
    for b in by_book.values():
        b["tickers"] = sorted(b["tickers"])

    # excluded_tickers (DGC/ZaloPay) không bao giờ là PARK — kiểm tra bất biến, không tự sửa.
    bad_excl = sorted({l["ticker"] for l in park_lots} & excluded)
    if bad_excl:
        book.warnings.append(f"⛔ ticker EXCLUDED nằm trong sổ PARK: {bad_excl} — sai bất biến, "
                             f"KHÔNG được trim, cần người xử lý")
        for tk in bad_excl:
            book.unverified.add(tk)

    park_mv = sum(l["mv_vnd"] for l in park_lots)
    park_mv_verified = sum(l["mv_vnd"] for l in park_lots if l["ticker"] not in book.unverified)
    return {
        "account_label": account_label, "account_no": account_no, "asof": asof,
        "day0_date": day0, "bootstrap": os.path.basename(snap_path),
        "excluded_tickers": sorted(excluded),
        "lots": book.lots, "park_lots": park_lots, "by_book": by_book,
        "broker_positions": positions,
        "park_mv_vnd": park_mv, "park_mv_verified_vnd": park_mv_verified,
        "cash_available_vnd": cash,
        # `broker=` bơm tay (selfcheck) không có key ⇒ rơi về availableCash + đánh dấu basis, để
        # ca test không phải khai thêm field; production LUÔN có key (read_broker_snapshot đặt
        # tường minh, kể cả None) ⇒ None = DNSE thiếu field thật ⇒ consumer fail-closed.
        "cash_total_vnd": bmeta["total_cash_vnd"] if "total_cash_vnd" in bmeta else cash,
        "cash_dividend_receiving_vnd": bmeta.get("dividend_receiving_vnd"),
        # Trứng vàng (DNSE egg product) — vốn CHỦ SỞ HỮU thật, KHÔNG nằm trong
        # availableCash/cash_total_vnd (bmeta không có key ⇒ 0.0, vd `broker=` bơm tay ở
        # selfcheck). compute_park_trim.py (L1) VÀ compute_jit_unpark.py (L2) đều cộng field này
        # vào cash/pool riêng của mình (2026-08-19, user duyệt — xem §pool-egg-L2 trong
        # compute_jit_unpark.py). Consumer KHÔNG được cộng: `check_plan_funding()`/`executor.py`
        # (gate thực thi thật — "tiêu được ngay bao nhiêu", RANH GIỚI CỨNG khác hẳn L1/L2).
        "egg_assets_vnd": bmeta.get("egg_assets_vnd") or 0.0,
        # Nợ margin: pool phải là VỐN CHỦ SỞ HỮU nhàn rỗi, không gồm tiền đi vay (cùng quy ước
        # NAV = totalCash − totalDebt của daily_nav_snapshot.py/reconcile_equity.py). SpaceX là
        # tài khoản margin và ĐÃ từng nợ thật 409,9tr (sự cố 2026-07-03) ⇒ không phải giả định.
        "cash_debt_vnd": bmeta["total_debt_vnd"] if "total_debt_vnd" in bmeta else 0.0,
        "balance_all_zero": bool(bmeta.get("balance_all_zero")),
        "cash_basis": "total_cash" if "total_cash_vnd" in bmeta else "available_fallback",
        "unverified_tickers": sorted(book.unverified), "warnings": book.warnings,
        "n_fills_applied": len(applied), "reconcile": reconcile,
        "corp_actions_applied": [{"id": a["id"], "ticker": a["ticker"],
                                  "qty_multiplier": a["qty_multiplier"], "ex_date": a["ex_date"],
                                  "broker_effective_ts": a["broker_effective_ts"],
                                  "lots_adjusted": a["lots_adjusted"]} for a in applied_acts],
    }


def main():
    ap = argparse.ArgumentParser(description="Vị thế theo book (PARK/LAG/CAPIT/...) cho 1 account")
    ap.add_argument("--account", required=True)
    ap.add_argument("--asof", default=None, help="YYYY-MM-DD (mặc định: hôm nay ICT)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    h = park_holdings(a.account, a.asof)
    if a.json:
        out = dict(h)
        out["by_book"] = {k: dict(v) for k, v in h["by_book"].items()}
        print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
        return 0 if h["reconcile"]["ok"] else 1
    print(f"=== {h['account_label']} ({h['account_no']}) asof={h['asof']} "
          f"| ngày 0 {h['day0_date']} ({h['bootstrap']}) | {h['n_fills_applied']} FILL replay ===")
    print(f"broker: {h['reconcile']['broker']}")
    for b in sorted(h["by_book"]):
        v = h["by_book"][b]
        print(f"  {b:<22} qty {v['qty']:>8,}  MV {v['mv_vnd']/1e6:>10,.2f} tr  "
              f"n={len(v['tickers'])}  {','.join(v['tickers'][:8])}"
              f"{'...' if len(v['tickers']) > 8 else ''}")
    print(f"  PARK MV = {h['park_mv_vnd']/1e6:,.2f} tr  "
          f"(đã đối soát: {h['park_mv_verified_vnd']/1e6:,.2f} tr)")
    print(f"  availableCash = {(h['cash_available_vnd'] or 0)/1e6:,.2f} tr  (tiêu được ngay — L2)")
    _tc = h["cash_total_vnd"]
    _dv = h["cash_dividend_receiving_vnd"]
    _tc_s = "KHÔNG ĐO ĐƯỢC" if _tc is None else f"{_tc/1e6:,.2f} tr"
    _dv_s = "?" if _dv is None else f"{_dv/1e6:,.2f} tr"
    print(f"  totalCash     = {_tc_s}  (gồm tiền bán chưa settle + cổ tức chờ nhận {_dv_s}) "
          f"— mẫu số pool L1 [basis={h['cash_basis']}]")
    r = h["reconcile"]
    print(f"đối soát broker: {'✅ KHỚP' if r['ok'] else '❌ LỆCH'} ({r['n_tickers']} mã)")
    for m in r["mismatches"]:
        print(f"   ✗ {m['ticker']}: sổ {m['ledger_qty']:,} vs broker {m['broker_qty']:,} "
              f"(lệch {m['diff']:+,}) — KHÔNG tự sửa, cần người xử lý")
    for w in h["warnings"]:
        print(f"   ⚠ {w}")
    if h["unverified_tickers"]:
        print(f"UNVERIFIED (cấm dùng sinh lệnh trim): {', '.join(h['unverified_tickers'])}")
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
