# -*- coding: utf-8 -*-
"""Broker adapters — interface chung + PHS FLEX + DNSE OpenAPI + Paper (mô phỏng).

Chọn broker theo account profile: "broker": "phs" (mặc định) | "dnse".
PaperBroker dùng quote THẬT (từ PHS datafeed hoặc DNSE market data tùy broker
của profile) nhưng khớp mô phỏng, tiền/danh mục ảo data/bot_paper_<label>.json.

PHSBroker: lệnh thật qua phs_flex_api — hiện PHS chưa cấp client_id/secret riêng
nên place_order bị từ chối (-700003) cho tới khi có cặp khóa.
DNSEBroker: lệnh thật qua dnse_api (API key + HMAC; trading-token 8h bằng OTP).

Field name chưa chuẩn hóa hết → qget() thử nhiều tên; payload thô ghi vào
data/execution_logs/<broker>_raw_<date>.jsonl để tinh chỉnh mapping.
"""

import datetime as dt
import json
import os
import sys
import time
import uuid
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .config import DATA_DIR, EXEC_DIR
from .vn_market import normalize_price_vnd, now_ict, today_ict

PAPER_STATE_FILE = os.path.join(os.path.dirname(DATA_DIR), "secrets", "bot_paper_account.json")  # legacy (label main)
DEFAULT_CREDENTIALS = os.path.join(os.path.dirname(DATA_DIR), "secrets", "phs_credentials.json")
DEFAULT_DNSE_CREDENTIALS = os.path.join(os.path.dirname(DATA_DIR), "secrets", "dnse_credentials.json")
DEFAULT_PHS_FLASH_CREDENTIALS = os.path.join(os.path.dirname(DATA_DIR), "secrets",
                                             "phs_flash_credentials.json")

# Pool FlexClient theo credentials file: nhiều tiểu khoản chung 1 login dùng chung
# client + token (login lại nhiều lần có thể vô hiệu token cũ của nhau).
_FLEX_POOL = {}


def get_flex_client(credentials_file=None):
    from phs_flex_api import FlexClient
    path = os.path.abspath(credentials_file or DEFAULT_CREDENTIALS)
    if path in _FLEX_POOL:
        return _FLEX_POOL[path]
    if path == os.path.abspath(DEFAULT_CREDENTIALS):
        token_cache = None                     # dùng cache mặc định của wrapper
    else:
        stem = os.path.splitext(os.path.basename(path))[0]
        token_cache = os.path.join(DATA_DIR, f"phs_flex_token_{stem}.json")
    try:
        kw = {"token_cache": token_cache} if token_cache else {}
        c = FlexClient.from_credentials_file(path=path, **kw)
    except FileNotFoundError:
        c = FlexClient()
    _FLEX_POOL[path] = c
    return c


# Pool DNSEClient theo credentials file (api_key/secret + trading-token cache chung)
_DNSE_POOL = {}


def get_dnse_client(credentials_file=None):
    from dnse_api import DNSEClient
    path = os.path.abspath(credentials_file or DEFAULT_DNSE_CREDENTIALS)
    if path not in _DNSE_POOL:
        _DNSE_POOL[path] = DNSEClient.from_credentials_file(path=path)
    return _DNSE_POOL[path]


# Pool PHSFlashClient theo credentials file (1 login dùng chung cho mọi tiểu khoản
# của cùng bộ credentials; token cache đặt cạnh theo tên file).
_PHS_FLASH_POOL = {}


def get_phs_flash_client(credentials_file=None):
    from phs_flash_api import PHSFlashClient
    path = os.path.abspath(credentials_file or DEFAULT_PHS_FLASH_CREDENTIALS)
    if path not in _PHS_FLASH_POOL:
        _PHS_FLASH_POOL[path] = PHSFlashClient.from_credentials_file(path=path)
    return _PHS_FLASH_POOL[path]


def qget(d, *names, default=None):
    """Lấy giá trị đầu tiên khác None theo danh sách tên khóa (không phân biệt hoa/thường)."""
    if not isinstance(d, dict):
        return default
    lower = {str(k).lower(): v for k, v in d.items()}
    for n in names:
        v = lower.get(n.lower())
        if v not in (None, "", "null"):
            return v
    return default


def _fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


# Mã sàn THẬT trong payload DNSE là `marketId`, không phải `exchange`/`market`/`floorcode`.
# ĐO 43 mã ngày 2026-08-15 (mọi mã từng xuất hiện ở lệnh MUA trong 97 plan + đối chứng UPCOM):
# payload KHÔNG chứa bất kỳ key nào trong ba key cũ ⇒ `qget(...)` luôn rơi về `default="HOSE"`
# cho **43/43 mã**, kể cả SHS/MBS (HNX) và DRI/SCL/TV1 (UPCOM). Đó là fail-OPEN: đoán sai một
# cách im lặng thay vì từ chối.
#
# Hệ quả đã cắn thật 2026-07-01 và ĐÃ được ghi nhận: SHS/MBS bị DNSE từ chối **1.494 lần**
# ("Invalid price lot") vì `_limit_price` làm tròn theo bước giá HOSE. Lúc đó chữa ở ngọn bằng
# `Executor._retry_tick_mismatch()` (thử-sai rồi học) với lý do ghi thẳng trong
# `tick_retry_selfcheck.py`: *"no guessing the live JSON field name"*. Nay tên trường đã ĐO
# được, nên sửa tận gốc; cơ chế retry GIỮ NGUYÊN làm lưới an toàn.
#
# Kiểm chéo bằng một tín hiệu TRỰC GIAO (không phải cùng một trường): biên độ giá thật đo từ
# `q.ceiling/q.ref − 1` = 7% / 10% / 15% khớp ánh xạ này ở **43/43 mã**.
MARKET_ID_TO_EXCHANGE = {"STO": "HOSE", "STX": "HNX", "UPX": "UPCOM"}

# Biên độ dao động giá theo sàn (quy chế giao dịch HOSE/HNX/UPCOM). Dùng làm phép kiểm TRỰC
# GIAO cho `marketId`: nếu `q.ceiling/q.ref − 1` không khớp biên độ của sàn vừa suy ra thì
# snapshot không nhất quán ⇒ người gọi phải fail-closed, không được đoán.
EXCHANGE_BAND_PCT = {"HOSE": 0.07, "HNX": 0.10, "UPCOM": 0.15}


class Quote:
    """Snapshot giá chuẩn hóa từ payload instrument PHS (mọi giá VND)."""

    def __init__(self, raw):
        self.raw = raw
        p = lambda *n: normalize_price_vnd(_fnum(qget(raw, *n)))
        self.symbol = qget(raw, "symbol", "instrument", "code", "sym")
        # `market_id` = mã sàn THÔ của feed (STO/STX/UPX). Giữ lại nguyên bản để người đọc log
        # truy được kết luận về sàn đến từ đâu, thay vì chỉ thấy nhãn đã chuẩn hoá.
        self.market_id = qget(raw, "marketid", "market_id")
        _mapped = MARKET_ID_TO_EXCHANGE.get(str(self.market_id or "").strip().upper())
        _explicit = qget(raw, "exchange", "market", "floorcode")
        # `exchange_known` là thứ MỌI cổng fail-closed phải hỏi. `exchange` vẫn giữ mặc định
        # "HOSE" để đường tính bước giá (`_limit_price` + retry học sàn) không đổi hành vi khi
        # feed câm — đổi cái đó là một thay đổi khác, không thuộc phạm vi sửa lỗi này.
        self.exchange = _mapped or _explicit or "HOSE"
        self.exchange_known = bool(_mapped or _explicit)
        self.last = p("lastprice", "last", "matchprice", "closeprice", "close", "price")
        self.ref = p("refprice", "reference", "basicprice", "referenceprice",
                     "priorcloseprice", "ref")
        self.ceiling = p("ceiling", "ceilingprice", "ce", "highlimit")
        self.floor = p("floor", "floorprice", "fl", "lowlimit")
        # Dấu thời gian bản ghi tham chiếu (secdef) — KHÔNG phải `time` khớp lệnh. None khi feed
        # không cấp; cổng G6 (price_frame) coi None là "không phát biểu được", không phải FAIL.
        self.secdef_time = qget(raw, "secdeftime")
        self.bid = p("bestbid1price", "bidprice1", "bestbid", "b1", "bidprice")
        self.ask = p("bestoffer1price", "askprice1", "offerprice1", "bestoffer", "o1", "askprice")
        v = _fnum(qget(raw, "totaltrading", "totalvolumetraded", "totalvolume",
                       "accumulatedvolume", "totalvol", "nmtotaltradedqty",
                       "totaltradingqtty", "volume"))
        self.day_volume = v  # KL khớp lũy kế trong ngày (có thể None)

    def ok(self):
        return self.last is not None or self.ref is not None

    def __repr__(self):
        return (f"Quote({self.symbol} last={self.last} ref={self.ref} "
                f"bid={self.bid} ask={self.ask} ce={self.ceiling} fl={self.floor} "
                f"vol={self.day_volume})")


class OrderUpdate:
    """Trạng thái 1 lệnh từ sổ lệnh broker."""

    def __init__(self, order_id, status="", filled_qty=0, avg_price=None, raw=None):
        self.order_id = str(order_id)
        self.status = str(status)
        self.filled_qty = int(filled_qty or 0)
        self.avg_price = avg_price
        self.raw = raw

    @property
    def is_dead(self):
        """Lệnh không còn sống (hủy/từ chối/khớp hết) — best-effort theo status string.

        KHÔNG khớp substring đơn ký tự `"f"`/`"x"` (đã gỡ — cùng lỗi mà `PHSFlashOrderUpdate`
        tự nhận ở docstring lớp con: một status CÒN SỐNG như "Pending confirmation" chứa 'f'
        sẽ bị coi là chết). `DNSEBroker`/`PHSBroker` dùng thẳng lớp này qua `poll_orders()` nên
        heuristic phải đúng ở đây, không chỉ ở subclass PHS FlashAPI."""
        s = self.status.lower()
        if "partial" in s:        # PartiallyFilled (DNSE) vẫn đang sống
            return False
        return any(k in s for k in ("cancel", "hủy", "huy", "reject", "từ chối",
                                    "fill", "khớp hết", "matchall", "expire"))


# --------------------------------------------------------------------- base

class BrokerBase:
    name = "base"
    can_trade_live = False
    _raw_log = None          # path jsonl ghi payload thô (set ở subclass)

    def _log_raw(self, kind, payload):
        if not self._raw_log:
            return
        try:
            os.makedirs(EXEC_DIR, exist_ok=True)
            with open(self._raw_log, "a", encoding="utf-8") as f:
                # account_no/label ở TOP-LEVEL record (không chỉ trong payload) — bắt buộc
                # từ 2026-07-06 khi 2 account live cùng broker dùng CHUNG 1 file theo ngày
                # (dnse_raw_{date}.jsonl không phân biệt account trong tên file). Trước đó
                # chỉ 1 account (SpaceX) nên chưa lộ; ZaloPay go-live cùng ngày làm record
                # "balances" của 2 account xen kẽ, khiến latest_balance() lấy nhầm account
                # (xem kb/INCIDENTS.md 2026-07-06 — NAV SpaceX báo sai 688.5tr vì đọc balance
                # ZaloPay). "kind" khác như orders/place_order vốn đã có accountNo riêng
                # trong payload nên không bị ảnh hưởng, nhưng thêm ở đây cho MỌI kind để
                # nhất quán và phòng ngừa các payload khác thiếu accountNo.
                f.write(json.dumps({"ts": now_ict().isoformat(timespec="seconds"),
                                    "kind": kind, "account_no": getattr(self, "account_id", None),
                                    "account_label": getattr(self, "label", None),
                                    "payload": payload},
                                   ensure_ascii=False, default=str) + "\n")
        except OSError:
            pass

    def connect(self):
        raise NotImplementedError

    def get_cash(self):
        """Tiền mặt khả dụng (VND)."""
        raise NotImplementedError

    def get_max_buy_qty(self, symbol, price, loan_package_id=None):
        """Sức mua tối đa (số CP) theo mã+giá từ CHÍNH broker, hoặc None nếu broker không
        hỗ trợ/lỗi. Khác get_cash(): sức mua của broker thường ĐÃ TÍNH cả tiền bán chờ về
        (T+0 reuse) mà availableCash chưa phản ánh — xác nhận thực nghiệm DNSE 2026-07-07
        (ZaloPay cash-only: bán MSH 09:42, availableCash đứng yên nhưng ppse pp0Buy đã
        cộng đủ tiền bán lúc 09:56, user dự đoán đúng). None = caller tự rơi về check
        get_cash() cũ (fail-safe, không nới lỏng khi không chắc).

        `loan_package_id`: đo sức mua THEO ĐÚNG gói vay mà lệnh sẽ dùng (đòn bẩy CAPIT dùng
        gói 1840 initialRate 0,5 ⇒ sức mua GẤP ĐÔI gói default 1841 — Mafee đo 2026-08-03).
        Bỏ trống ⇒ gói default account: đúng cho lệnh thường, nhưng nếu lệnh đi ra bằng 1840
        mà lại đo bằng 1841 thì sức mua bị báo thiếu một nửa, lệnh đòn bẩy sẽ kẹt WAIT_CASH
        trông y hệt "thiếu tiền bình thường" (arch-reviewer 2026-08-03, phát hiện #2)."""
        return None

    def get_buying_power(self, symbol, price, loan_package_id=None):
        """Sức mua CÒN LẠI tính bằng VND theo chính broker, hoặc None nếu broker không hỗ
        trợ/lỗi. Anh em với get_max_buy_qty() (cùng nguồn ppse) nhưng trả TIỀN chứ không
        phải số CP — cần cho các kiểm tra ở cấp PLAN (Σ giá trị lệnh mua vs sức mua), nơi
        không có một mã/giá duy nhất để quy ra số CP. None = không đo được (caller KHÔNG
        được đoán thay).

        `loan_package_id`: đo sức mua THEO ĐÚNG gói vay mà lệnh sẽ dùng (đòn bẩy CAPIT dùng
        gói 1840 initialRate 0,5 ⇒ sức mua GẤP ĐÔI gói default 1841 — Mafee đo 2026-08-03).
        Bỏ trống ⇒ gói default account: đúng cho lệnh thường, nhưng nếu lệnh đi ra bằng 1840
        mà lại đo bằng 1841 thì sức mua bị báo thiếu một nửa, lệnh đòn bẩy sẽ kẹt WAIT_CASH
        trông y hệt "thiếu tiền bình thường" (arch-reviewer 2026-08-03, phát hiện #2)."""
        return None

    def get_positions(self):
        """→ {symbol: {"total": n, "sellable": n}}."""
        raise NotImplementedError

    def get_quote(self, symbol):
        """→ Quote | None."""
        raise NotImplementedError

    def get_nav(self):
        cash = self.get_cash()
        pos = self.get_positions()
        mv = 0.0
        for sym, p in pos.items():
            q = self.get_quote(sym)
            px = (q.last or q.ref) if q and q.ok() else 0
            mv += p["total"] * (px or 0)
        return cash + mv

    def place_order(self, symbol, qty, side, price=None, order_type="LO",
                    cash_only=False, loan_package_id=None):
        """→ order_id (str). cash_only=True: lệnh tiền mặt thuần — chọn gói vay HỢP LỆ
        RIÊNG cho mã này (vd TV1/UPCOM cần 1122 thay vì gói mainboard 1841) thay vì gói
        default account; xem DNSEBroker._resolve_loan_package_id. Broker không dùng gói
        vay DNSE có thể bỏ qua cờ này.

        loan_package_id: gói vay CHỈ ĐỊNH cho ĐÚNG lệnh này (đòn bẩy sleeve CAPIT, chính
        sách capit_margin_lever — do trading_bot.plan.apply_capit_lever cấp, không phải do
        plan generator tự khai). None = hành vi cũ nguyên vẹn (gói default account)."""
        raise NotImplementedError

    def cancel_order(self, order_id):
        raise NotImplementedError

    def poll_orders(self):
        """→ {order_id: OrderUpdate} cho các lệnh trong ngày."""
        raise NotImplementedError


# ---------------------------------------------------------------- PHS live

class PHSBroker(BrokerBase):
    name = "phs"
    can_trade_live = True

    def __init__(self, account_id=None, otp=None, quote_only=False,
                 credentials_file=None, label="main"):
        self.account_id = account_id
        self.label = label
        self._otp = otp
        self.quote_only = quote_only   # chỉ dùng datafeed, không cần login đủ
        self.credentials_file = credentials_file
        self.client = None
        self._quote_cache = {}      # symbol -> (ts, Quote)
        self._quote_ttl = 3.0       # giây
        self._raw_log = os.path.join(
            EXEC_DIR, f"phs_raw_{today_ict():%Y-%m-%d}.jsonl")

    def connect(self):
        self.client = get_flex_client(self.credentials_file)
        if self.quote_only:
            print("[phs] chế độ quote-only (datafeed)")
            return self
        if not self.client.access_token:
            raise RuntimeError(f"PHS login thất bại ({self.label}) — kiểm tra "
                               f"{self.credentials_file or 'secrets/phs_credentials.json'}")
        if self.account_id is None:
            accs = self.client.sub_accounts()
            self._log_raw("sub_accounts", accs)
            self.account_id = accs[0]["id"]
        if self._otp is not None and not getattr(self.client, "_otp_verified", False):
            self.client.verify_smart_otp(self._otp)
            self.client._otp_verified = True   # 1 lần / login, dùng chung các tiểu khoản
            print(f"[phs] Smart OTP đã xác thực ({self.label})")
        print(f"[phs] kết nối OK [{self.label}] tiểu khoản {self.account_id}")
        return self

    def get_cash(self):
        bal = self.client.cash_balance(self.account_id)
        self._log_raw("cash_balance", bal)
        row = bal[0] if isinstance(bal, list) and bal else bal
        v = _fnum(qget(row, "pp", "balance", "avlcash", "cashbal", default=0))
        return v or 0.0

    def get_positions(self):
        port = self.client.portfolio(self.account_id) or []
        self._log_raw("portfolio", port)
        out = {}
        for p in port:
            sym = qget(p, "symbol", "instrument", "code")
            total = int(_fnum(qget(p, "total", "totalqtty", "qty", default=0)) or 0)
            sellable = int(_fnum(qget(p, "trade", "avlqtty", "sellable",
                                      "availableqtty", default=total)) or total)
            if sym and total > 0:
                out[sym] = {"total": total, "sellable": sellable}
        return out

    def get_quote(self, symbol):
        import time as _t
        hit = self._quote_cache.get(symbol)
        if hit and _t.time() - hit[0] < self._quote_ttl:
            return hit[1]
        try:
            rows = self.client.instruments(symbols=symbol)
        except Exception as e:
            print(f"[phs] ⚠ quote {symbol} lỗi: {e}")
            return None
        row = rows[0] if isinstance(rows, list) and rows else rows
        q = Quote(row) if isinstance(row, dict) else None
        if q:
            if not q.ok():
                self._log_raw("quote_unmapped", row)
            q.l2_snapshot = self._phs_l2_snapshot(symbol, row) if isinstance(row, dict) else None
        self._quote_cache[symbol] = (_t.time(), q)
        return q

    @staticmethod
    def _phs_l2_snapshot(symbol, row):
        """Build orderbook_l2_v1 snapshot từ PHS flat bid/ask fields (3 mức).
        Trả None nếu không có data. Không raise — nằm trên đường đặt lệnh."""
        try:
            import time as _t
            captured = now_ict()
            captured_epoch_ms = int(_t.time() * 1000)
            bids, offers = [], []
            for i in (1, 2, 3):
                p = normalize_price_vnd(_fnum(row.get(f"bidPrice{i}")))
                v = _fnum(row.get(f"bidVol{i}"))
                if p is not None and v is not None:
                    bids.append({"price": p, "quantity": v})
            for i in (1, 2, 3):
                p = normalize_price_vnd(_fnum(row.get(f"offerPrice{i}")))
                v = _fnum(row.get(f"offerVol{i}"))
                if p is not None and v is not None:
                    offers.append({"price": p, "quantity": v})
            if not bids and not offers:
                return None
            return {
                "schema_version": "orderbook_l2_v1",
                "symbol": symbol,
                "board_id": row.get("FloorCode") or row.get("exchange") or "G1",
                "captured_at": captured.isoformat(timespec="milliseconds"),
                "captured_epoch_ms": captured_epoch_ms,
                # PHS instruments không có sub-second timestamp; dùng capture time làm proxy.
                # source_age_ms=0 là đúng với nghĩa "vừa fetch xong", không phải stale.
                "source_ts": captured.isoformat(timespec="milliseconds"),
                "source_age_ms": 0,
                "source_time_status": "ok",
                "price_unit": "VND",
                "quantity_unit": "shares",
                "bids": bids,
                "offers": offers,
                "n_bid": len(bids),
                "n_offer": len(offers),
                "last": normalize_price_vnd(_fnum(row.get("closePrice") or row.get("averagePrice"))),
                "day_volume": _fnum(row.get("totalTrading")),
            }
        except Exception:
            return None

    def place_order(self, symbol, qty, side, price=None, order_type="LO",
                    cash_only=False, loan_package_id=None):
        # PHS không dùng gói vay DNSE → cờ cash_only/loan_package_id không áp dụng, chấp nhận
        # để interface đồng nhất với DNSEBroker (executor gọi chung 1 chữ ký).
        r = self.client.place_order(self.account_id, symbol, qty=int(qty), side=side,
                                    order_type=order_type, price=price)
        self._log_raw("place_order", {"req": [symbol, qty, side, price, order_type],
                                      "resp": r})
        oid = qget(r, "orderId", "orderid", "id")
        if not oid:
            raise RuntimeError(f"place_order không trả orderId: {r}")
        return str(oid)

    def cancel_order(self, order_id):
        r = self.client.cancel_order(self.account_id, order_id)
        self._log_raw("cancel_order", {"order_id": order_id, "resp": r})
        return r

    def poll_orders(self):
        rows = self.client.daily_orders(self.account_id) or []
        self._log_raw("daily_orders", rows)
        out = {}
        for o in rows:
            oid = qget(o, "orderid", "orderId", "id")
            if oid is None:
                continue
            filled = _fnum(qget(o, "execqtty", "matchedqtty", "matchqtty",
                                "cumqty", "fillqty", "matchedqty", default=0)) or 0
            avg = normalize_price_vnd(_fnum(qget(o, "avgprice", "matchprice",
                                                 "execprice", "avgpx")))
            out[str(oid)] = OrderUpdate(oid, qget(o, "status", "orderstatus",
                                                  default=""), filled, avg, raw=o)
        return out


# --------------------------------------------------------------- DNSE live

class DNSEBroker(BrokerBase):
    """DNSE OpenAPI v2 (dnse_api.DNSEClient).

    Inquiry + market data chỉ cần api_key/secret (ký HMAC, không login);
    đặt/sửa/hủy lệnh cần trading-token (OTP smart/email, hiệu lực 8h, tự cache
    trong data/dnse_trading_token*.json — còn hạn thì không cần --otp).
    """

    name = "dnse"
    can_trade_live = True

    def __init__(self, account_id=None, otp=None, quote_only=False,
                 credentials_file=None, label="main", auto_otp=False,
                 loan_package_id=None):
        self.account_id = account_id
        self.label = label
        self._otp = otp
        self._auto_otp = auto_otp
        self.quote_only = quote_only
        self.credentials_file = credentials_file
        self._loan_package_id = loan_package_id  # per-account override; applied after connect()
        self.client = None
        self._quote_cache = {}      # symbol -> (ts, Quote)
        self._secdef_cache = {}     # symbol -> dict (trần/sàn/ref — tĩnh trong ngày)
        self._loan_pkg_cache = {}   # symbol -> loanPackageId đã giải (cash_only, theo phiên)
        self._lever_pkg_cache = {}  # (symbol, gói CHỈ ĐỊNH) -> (id dùng, ok, note) — đòn bẩy CAPIT
        self._quote_ttl = 3.0
        self._l2_log_last = {}      # symbol -> time.time() lần ghi L2 gần nhất (throttle, xem _log_l2)
        self._raw_log = os.path.join(
            EXEC_DIR, f"dnse_raw_{today_ict():%Y-%m-%d}.jsonl")

    def connect(self):
        self.client = get_dnse_client(self.credentials_file)
        if self.quote_only:
            print("[dnse] chế độ quote-only (market data)")
            return self
        if self.account_id is None:
            accs = self.client.accounts()
            self._log_raw("accounts", accs)
            rows = accs.get("accounts") if isinstance(accs, dict) else accs
            if not rows:
                raise RuntimeError(f"[dnse:{self.label}] không thấy tiểu khoản: {accs}")
            self.account_id = qget(rows[0], "id", "accountno", "account")
        if self._otp is not None and not self.client.has_trading_token():
            self.client.create_trading_token(self._otp)
            print(f"[dnse] trading-token đã tạo ({self.label}, hạn 8h)")
        if self._auto_otp and not self.client.has_trading_token():
            import time as _time
            from gmail_otp_reader import fetch_dnse_otp, _build_gmail_service, _save_last_id
            print(f"[dnse] auto-OTP: pre-mark latest OTP email ({self.label})...")
            try:
                svc = _build_gmail_service()
                q2 = 'from:noreply@mail.dnse.com.vn subject:"Xác thực với Email OTP"'
                resp = svc.users().messages().list(userId="me", q=q2, maxResults=1).execute()
                msgs = resp.get("messages", [])
                if msgs:
                    _save_last_id(msgs[0]["id"])
            except Exception:
                pass
            print(f"[dnse] auto-OTP: gửi email OTP ({self.label})...")
            send_ts = _time.time()
            self.client.send_email_otp()
            otp = fetch_dnse_otp(timeout=120, sent_after=send_ts)
            self.client.create_trading_token(otp)
            print(f"[dnse] auto-OTP: trading-token OK ({self.label}, hạn 8h)")
        if self._loan_package_id is not None:
            self.client.loan_package_id = self._loan_package_id
        if not self.client.has_trading_token():
            print(f"[dnse] ⚠ chưa có trading-token ({self.label}) — inquiry OK, "
                  f"đặt lệnh sẽ bị từ chối (cần --otp; email_otp: gửi mã bằng "
                  f"--send-otp trước)")
        print(f"[dnse] kết nối OK [{self.label}] tiểu khoản {self.account_id}")
        return self

    def get_cash(self):
        bal = self.client.balances(self.account_id)
        self._log_raw("balances", bal)
        row = bal[0] if isinstance(bal, list) and bal else bal
        if isinstance(row, dict) and isinstance(row.get("stock"), dict):
            row = row["stock"]          # balances thật: {"stock": {...}, "derivative": {...}}
        v = _fnum(qget(row, "availablecash", "withdrawablecash", "purchasingpower",
                       "cashavailable", "totalcash", "cash", "balance",
                       default=0))
        return v or 0.0

    def _cash_totalcash_minus_debt(self):
        """`totalCash − totalDebt` (§25 "SỞ HỮU") từ payload `balances` thô — cơ sở đúng cho
        NAV/get_nav(), KHÁC get_cash() (§25 "TIÊU ĐƯỢC NGAY" — availableCash-family, thiếu
        tiền bán chờ về/cổ tức phải thu). None nếu DNSE không trả đủ hai field, HOẶC nếu cả
        ba field tiền (totalCash/totalDebt/availableCash) đều = 0 (bẫy fail-closed §25/
        `park_holdings._cash_fields_all_zero` — DNSE thỉnh thoảng trả block toàn 0 do lỗi
        API tạm thời, sự cố thật 2026-07-27, KHÔNG phải tiền về 0 thật)."""
        bal = self.client.balances(self.account_id)
        self._log_raw("balances", bal)
        row = bal[0] if isinstance(bal, list) and bal else bal
        if isinstance(row, dict) and isinstance(row.get("stock"), dict):
            row = row["stock"]
        tc = _fnum(qget(row, "totalcash", default=None))
        td = _fnum(qget(row, "totaldebt", default=None))
        if tc is None or td is None:
            return None
        av = _fnum(qget(row, "availablecash", default=None))
        if tc == 0 and td == 0 and (av is None or av == 0):
            return None
        return tc - td

    def get_nav(self):
        """NAV = totalCash−totalDebt (§25 cơ sở "SỞ HỮU") + market value vị thế — KHÔNG dùng
        `get_cash()` làm cơ sở NAV (đó là sức mua tức thời, coding_guidelines.md §25). Field
        tiền thiếu ⇒ rơi về `get_cash()` (hành vi cũ) thay vì raise, vì get_nav() không có
        hợp đồng fail-closed như compute_active_nav.py."""
        cash = self._cash_totalcash_minus_debt()
        if cash is None:
            cash = self.get_cash()
        pos = self.get_positions()
        mv = 0.0
        for sym, p in pos.items():
            q = self.get_quote(sym)
            px = (q.last or q.ref) if q and q.ok() else 0
            mv += p["total"] * (px or 0)
        return cash + mv

    def get_max_buy_qty(self, symbol, price, loan_package_id=None):
        """Sức mua tối đa theo mã+giá qua GET /accounts/{acc}/ppse (qmaxBuy). ppse đã tính
        cả tiền bán chờ về T+0 — availableCash thì chưa (xem BrokerBase docstring). Mọi
        lỗi → None (caller rơi về check get_cash cũ, không nới lỏng khi không chắc)."""
        try:
            r = self.client.ppse(self.account_id, symbol, int(price),
                                 loan_package_id=loan_package_id)
            self._log_raw("ppse", {"symbol": symbol, "price": price,
                                   "loan_package_id": loan_package_id, "resp": r})
            v = _fnum(qget(r, "qmaxBuy", "qmaxbuy"))
            return int(v) if v is not None and v >= 0 else None
        except Exception:
            return None

    def get_buying_power(self, symbol, price, loan_package_id=None):
        """Sức mua VND = `pp0Buy` của GET /accounts/{acc}/ppse (cùng response với qmaxBuy).
        pp0Buy là số của CHÍNH broker: đã gồm tiền bán chờ về T+0 và hạn mức vay của gói
        loanPackageId đang dùng (đo được 2026-07-28 ZaloPay cash-only: pp0Buy 25,54M trong
        khi availableCash chỉ 5,68M). Mọi lỗi → None, KHÔNG suy ra từ get_cash()."""
        try:
            r = self.client.ppse(self.account_id, symbol, int(price),
                                 loan_package_id=loan_package_id)
            self._log_raw("ppse", {"symbol": symbol, "price": price,
                                   "loan_package_id": loan_package_id, "resp": r})
            v = _fnum(qget(r, "pp0Buy", "pp0buy"))
            return float(v) if v is not None and v >= 0 else None
        except Exception:
            return None

    def positions_raw(self):
        """Danh sách vị thế THÔ — MỘT DÒNG MỖI DEAL/GÓI VAY, chưa cộng gộp theo mã.

        `get_positions()` ngay dưới cộng gộp và giữ đúng MỘT `marketPrice` cho mỗi mã. Việc
        gộp đó đúng cho mọi mục đích kế toán, nhưng nó XOÁ đúng bằng chứng mà cổng đồng-hệ
        (`price_frame.check_same_frame`, G4) cần đọc: ngày 2026-08-14 19:10:23, BID có lô
        gói-vay 1826 đã ở hệ quy chiếu MỚI (107cp @35.800) trong khi lô 1258 còn hệ CŨ
        (300cp @38.850) — TRONG CÙNG MỘT bản đọc. DNSE điều chỉnh theo TỪNG GÓI VAY và cú lật
        KHÔNG nguyên tử. Nhìn qua bản gộp thì bản đọc đó trông hoàn toàn lành.

        Không log lại `_log_raw` (get_positions đã log cùng payload nếu được gọi cùng phiên);
        trả list rỗng khi payload không đúng dạng, caller fail-closed theo ngữ cảnh của nó.
        """
        r = self.client.positions(self.account_id)
        rows = r.get("positions") or r.get("data") if isinstance(r, dict) else r
        return list(rows or [])

    def get_positions(self):
        r = self.client.positions(self.account_id)
        self._log_raw("positions", r)
        rows = r.get("positions") or r.get("data") if isinstance(r, dict) else r
        out = {}
        for p in rows or []:
            if str(qget(p, "status", default="OPEN")).upper() == "CLOSED":
                continue
            sym = qget(p, "symbol", "instrument", "code")
            total = int(_fnum(qget(p, "openquantity", "quantity", "totalquantity",
                                   "qty", default=0)) or 0)
            # tradeQuantity = KL bán được (đã về); accumulate có thể gồm CP chờ về
            sellable = int(_fnum(qget(p, "tradequantity", "availablequantity",
                                      "sellablequantity", "availableqty",
                                      default=total)) or total)
            # marketPrice: giá tham chiếu riêng của khối vị thế (KHÁC giá ATC của
            # close_price() — xem docstring dnse_close_prices trong verify_account_snapshot.py)
            # nhưng tự động phản ánh corporate action đã được broker ghi nhận vào vị thế
            # (vd chia tách/thưởng cổ phiếu) NGAY khi qty được cập nhật — dùng để đối chiếu
            # chéo, không thay thế close_price làm nguồn giá chính (bug VHM 2026-08-05).
            market_price = _fnum(qget(p, "marketprice", default=None))
            if sym and total > 0:
                # DNSE trả một dòng cho MỖI deal/loan package, nên cùng mã có thể xuất hiện
                # nhiều lần. Ghi đè dòng trước làm mất đúng giá trị các deal cũ khi tính NAV
                # (ZaloPay 2026-08-11: BID/MBB/VCB thiếu 24,01tr). API public của broker là
                # vị thế TỔNG theo mã, vì vậy phải cộng gộp quantity và sellable; marketPrice
                # là giá mark chung, giữ giá mới nhất khác-None để caller vẫn cross-check CA.
                prev = out.get(sym)
                if prev:
                    total += prev["total"]
                    sellable += prev["sellable"]
                    if market_price is None:
                        market_price = prev.get("marketPrice")
                out[sym] = {"total": total, "sellable": sellable, "marketPrice": market_price}
        return out

    @staticmethod
    def _pick_board(payload, list_key):
        """Payload DNSE: list các board (G1 lô chẵn, G4 lô lẻ, T* thỏa thuận)
        hoặc dict {list_key: [...]}. → dict của board G1 (ưu tiên) / đầu tiên."""
        rows = payload
        if isinstance(payload, dict):
            rows = payload.get(list_key) or payload.get("data") or [payload]
        if not isinstance(rows, list):
            return {}
        g1 = [r for r in rows if isinstance(r, dict) and r.get("boardId") == "G1"]
        rows = g1 or [r for r in rows if isinstance(r, dict)]
        return rows[0] if rows else {}

    # P5 — GHI LẠI 10 mức giá chờ (job Taylor_20260812_095213). DNSE G1 THẬT SỰ trả về
    # `quotes[].bid/offer` = list 10 mức {price, quantity}, nhưng `Quote` chỉ giữ mức 1
    # (`bidPrice1`/`offerPrice1`) và dòng `raw.update(... not isinstance(v,(list,dict)))` bên
    # dưới vứt bỏ toàn bộ mảng. Hệ quả đo được (research/thin_exec_20260812 §P5): KHÔNG tồn
    # tại order-book lịch sử cho mã VN ở bất kỳ nguồn nào ta có (vnstock `price_depth()` =
    # NotImplementedError; `intraday()` chỉ có phiên hôm nay) ⇒ mọi chữ "depth" trong nghiên
    # cứu đó phải thay bằng KL ĐÃ KHỚP, tức CẬN DƯỚI của thanh khoản khả dụng.
    #
    # Đây là LOGGING THUẦN: không đổi `Quote`, không đổi giá/KL đặt lệnh, không thêm một lời
    # gọi API nào (ghi lại chính payload đã lấy về). Mục đích duy nhất: tích luỹ 4-6 tuần dữ
    # liệu để trả lời "KL CHỜ thật ở dưới trần là bao nhiêu" — câu hỏi hiện KHÔNG backtest
    # được, và không có nó thì mọi con số cho hướng depth-aware sizing đều là bịa.
    _L2_MAX_LEVELS = 10

    def _l2_levels(self, arr):
        """[{price, quantity}] × ≤10 mức, giá đã chuẩn hoá VND. [] nếu payload không đúng dạng."""
        out = []
        if not isinstance(arr, list):
            return out
        for lv in arr[:self._L2_MAX_LEVELS]:
            if not isinstance(lv, dict):
                continue
            p = normalize_price_vnd(_fnum(qget(lv, "price", "p")))
            v = _fnum(qget(lv, "quantity", "qtty", "volume", "qty", "q"))
            if p is None and v is None:
                continue
            out.append({"price": p, "quantity": v})
        return out

    @staticmethod
    def _l2_source_time(qt, captured):
        """Chuẩn hoá timestamp của feed về ISO ICT + age_ms; không đoán khi parse không được."""
        raw = qget(qt, "time", "timestamp", "quoteTime", "tradingTime")
        if raw in (None, ""):
            return None, None, "missing"
        try:
            s = str(raw).strip().replace("Z", "+00:00")
            if len(s) <= 15 and ":" in s and "T" not in s and "-" not in s:
                parsed = dt.datetime.combine(captured.date(), dt.time.fromisoformat(s))
            else:
                parsed = dt.datetime.fromisoformat(s)
            ict = ZoneInfo("Asia/Ho_Chi_Minh")
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=ict)
            parsed = parsed.astimezone(ict)
            cap = captured.replace(tzinfo=ict) if captured.tzinfo is None else captured.astimezone(ict)
            return parsed.isoformat(timespec="milliseconds"), int((cap - parsed).total_seconds() * 1000), "ok"
        except (TypeError, ValueError, OverflowError):
            return str(raw), None, "unparseable"

    def _log_l2(self, symbol, qt, raw):
        """Ghi 1 bản ghi `kind="quote_l2"` vào dnse_raw_<date>.jsonl. KHÔNG BAO GIỜ raise —
        lỗi ghi log tuyệt đối không được làm hỏng đường lấy quote (nó nằm trên đường đặt lệnh).

        THROTTLE mặc định 60s/mã (`DNSE_L2_LOG_SEC`, 0 = ghi mọi lần fetch). Vì sao không ghi
        mọi lần: `dnse_raw_*.jsonl` là file KẾ TOÁN dùng chung (15+ consumer quét toàn file —
        daily_nav_snapshot, verify_account_snapshot, park_holdings…). Cache quote TTL 3s +
        poll 20s ⇒ ~3 lần fetch/phút/mã ⇒ ghi mọi lần sẽ thêm ~16k bản ghi/ngày (~24MB, gấp
        đôi file hiện tại 17-31MB) để đổi lấy độ phân giải mà nghiên cứu KHÔNG cần: bucket
        phân tích là 30 phút, và TV1 chỉ ~40k cp khớp CẢ NGÀY. 60s cho 30 mẫu/bucket.
        """
        try:
            captured = now_ict()
            captured_epoch_ms = int(time.time() * 1000)
            bids = self._l2_levels(qget(qt, "bid", "bids"))
            offers = self._l2_levels(qget(qt, "offer", "offers", "asks"))
            if not bids and not offers:
                return None
            source_ts, source_age_ms, source_status = self._l2_source_time(qt, captured)
            snapshot = {
                "schema_version": "orderbook_l2_v1",
                "symbol": symbol,
                "board_id": qget(qt, "boardId", "board", default="G1") or "G1",
                "captured_at": captured.isoformat(timespec="milliseconds"),
                "captured_epoch_ms": captured_epoch_ms,
                "source_ts": source_ts,
                "source_age_ms": source_age_ms,
                "source_time_status": source_status,
                "price_unit": "VND",
                "quantity_unit": "shares",
                "bids": bids,
                "offers": offers,
                "n_bid": len(bids),
                "n_offer": len(offers),
                "last": normalize_price_vnd(_fnum(qget(raw, "matchPrice", "lastPrice"))),
                "day_volume": _fnum(qget(raw, "totalVolumeTraded", "totalTrading")),
            }
            gap = float(os.environ.get("DNSE_L2_LOG_SEC", "60"))
            last = self._l2_log_last.get(symbol)
            nowt = time.time()
            if gap <= 0 or last is None or nowt - last >= gap:
                self._l2_log_last[symbol] = nowt
                # Tên field CỐ Ý tránh `resp`/`orders`: execution_quality_review.py là consumer
                # DUY NHẤT không lọc kind; không có 2 key đó ⇒ nó bỏ qua sạch.
                self._log_raw("quote_l2", {**snapshot,
                    "note": "P5 depth logging — logging thuần, KHÔNG đổi hành vi đặt lệnh"})
            # Kể cả throttle không ghi file, trả snapshot fetch hiện tại cho telemetry child-order.
            return snapshot
        except Exception:
            return None

    def get_quote(self, symbol):
        import time as _t
        hit = self._quote_cache.get(symbol)
        if hit and _t.time() - hit[0] < self._quote_ttl:
            return hit[1]
        raw = {"symbol": symbol}
        # 1) secdef (trần/sàn/tham chiếu theo board) — tĩnh, cache cả phiên
        sd = self._secdef_cache.get(symbol)
        if sd is None:
            try:
                sd = self._pick_board(self.client.secdef(symbol), "secdefs")
                self._secdef_cache[symbol] = sd
            except Exception as e:
                sd = {}
                print(f"[dnse] ⚠ secdef {symbol} lỗi: {e}")
        raw.update(sd)
        # Dấu thời gian RIÊNG của bản ghi secdef, chụp TRƯỚC khi `latest_trade`/`latest_quote`
        # ghi đè khoá `time` bằng giờ khớp lệnh. Đây là thứ DUY NHẤT cho biết `basicPrice` đang
        # nói về PHIÊN NÀO: sau ~15:00 ICT, DNSE lật secdef sang phiên kế (đo thật BID 08-17
        # 19:23:45 → basicPrice 35,9 = tham chiếu 08-18). price_frame.check_snapshot_session (G6).
        if isinstance(sd, dict) and sd.get("time") is not None:
            raw["secdefTime"] = sd["time"]
        # 2) khớp lệnh mới nhất — {"trades":[board G1: matchPrice, totalVolumeTraded]}
        try:
            raw.update(self._pick_board(self.client.latest_trade(symbol), "trades"))
        except Exception as e:
            print(f"[dnse] ⚠ trade {symbol} lỗi: {e}")
        # 3) top giá chờ — {"quotes":[board G1: bid/offer = [{price, quantity},…]]}
        l2_snapshot = None
        try:
            qt = self._pick_board(self.client.latest_quote(symbol), "quotes")
            for side_key, flat in (("bid", "bidPrice1"), ("bids", "bidPrice1"),
                                   ("offer", "offerPrice1"), ("offers", "offerPrice1"),
                                   ("asks", "offerPrice1")):
                arr = qt.get(side_key) if isinstance(qt, dict) else None
                if isinstance(arr, list) and arr:
                    top = arr[0]
                    raw.setdefault(flat, qget(top, "price", "p")
                                   if isinstance(top, dict) else top)
            if isinstance(qt, dict):
                raw.update({k: v for k, v in qt.items()
                            if not isinstance(v, (list, dict)) and k not in raw})
                l2_snapshot = self._log_l2(symbol, qt, raw)  # P5: giữ 10 mức + metadata v1
        except Exception as e:
            print(f"[dnse] ⚠ quote {symbol} lỗi: {e}")
        q = Quote(raw)
        q.l2_snapshot = l2_snapshot
        if not q.ok():
            self._log_raw("quote_unmapped", raw)
        self._quote_cache[symbol] = (_t.time(), q)
        return q

    @staticmethod
    def _extract_loan_pkgs(payload):
        """Chuẩn hoá payload loan-packages → list[dict]. DNSE có thể trả list thẳng
        hoặc {loanPackages|loanPackageList|data|items: [...]}."""
        if isinstance(payload, dict):
            for k in ("loanPackages", "loanPackageList", "data", "items"):
                if isinstance(payload.get(k), list):
                    return [r for r in payload[k] if isinstance(r, dict)]
            return []
        if isinstance(payload, list):
            return [r for r in payload if isinstance(r, dict)]
        return []

    def _resolve_loan_package_id(self, symbol):
        """loanPackageId HỢP LỆ cho `symbol` — chỉ gọi cho lệnh cash_only (book
        DISCRETIONARY_SPECIAL). Bug TV1 07-28 (kb/INCIDENTS.md): gói default 1841 của
        SpaceX chỉ hợp lệ CP mainboard (HOSE/HNX), KHÔNG hợp lệ UPCOM (TV1) → DNSE
        reject. Fix cũ ("bỏ trường") cũng sai: DNSE bắt buộc loanPackageId → HTTP 400.

        Chọn ID (query GET /accounts/{acc}/loan-packages?symbol=X):
          - default account (self.client.loan_package_id) CÓ trong danh sách gói hợp lệ
            của symbol → dùng default (BAL/LAG/CAPIT mainboard KHÔNG đổi hành vi).
          - default KHÔNG có (như TV1) → ưu tiên gói type='N' (thuần tiền mặt) trước
            type='M' (margin), rồi tới gói đầu tiên trong danh sách.
        Fail-safe: query lỗi/timeout/rỗng → trả về default account (KHÔNG bỏ trường —
        thiếu loanPackageId = HTTP 400; well-formed request bị business-reject vẫn an
        toàn hơn request thiếu trường bắt buộc). Cache theo symbol trong phiên (bot
        restart mỗi phiên sáng/chiều → cache tự làm mới)."""
        if symbol in self._loan_pkg_cache:
            return self._loan_pkg_cache[symbol]
        default = getattr(self.client, "loan_package_id", None)
        resolved = default
        try:
            raw = self.client.loan_packages(self.account_id, symbol=symbol)
            pkgs = self._extract_loan_pkgs(raw)
            ids = [qget(p, "id", "loanpackageid", "loanproductid") for p in pkgs]
            ids = [i for i in ids if i is not None]
            ids_norm = {str(i) for i in ids}
            if default is not None and str(default) in ids_norm:
                resolved = default                      # gói default hợp lệ → giữ nguyên
            elif ids:
                cash_pkgs = [p for p in pkgs
                             if str(qget(p, "type", default="")).upper() == "N"]
                pick = (cash_pkgs or pkgs)[0]
                resolved = qget(pick, "id", "loanpackageid", "loanproductid")
            # else: danh sách rỗng → giữ default (fail-safe)
            self._log_raw("loan_packages_resolve",
                          {"symbol": symbol, "default": default,
                           "valid_ids": ids, "resolved": resolved})
        except Exception as e:
            print(f"[dnse] ⚠ loan_packages {symbol} lỗi ({e}) → gói default {default}")
            resolved = default
        self._loan_pkg_cache[symbol] = resolved
        return resolved

    def _validate_lever_package(self, symbol, want):
        """Gói vay CHỈ ĐỊNH `want` có hợp lệ cho `symbol` không → (id_sẽ_dùng, ok, note).

        Dùng cho đòn bẩy sleeve CAPIT (gói 1840 "RocketX"). KHÔNG hợp lệ / không kiểm được
        (mạng lỗi, danh sách rỗng) → trả gói DEFAULT của account, tức lệnh đi ra KHÔNG có đòn
        bẩy. Đây là chiều fail-safe ĐÚNG: đặt lệnh với ít đòn bẩy hơn dự kiến chỉ làm sleeve
        under-deploy (hoặc bị DNSE từ chối vì thiếu sức mua — vẫn an toàn), còn đặt với NHIỀU
        đòn bẩy hơn duyệt là rủi ro margin call bằng tiền thật. Đối xứng với
        _resolve_loan_package_id: không bao giờ BỎ trường (thiếu = HTTP 400, bug TV1 07-28).
        Cache theo (symbol, want) trong phiên."""
        cache = self.__dict__.setdefault("_lever_pkg_cache", {})
        key = (symbol, str(want))
        if key in cache:
            return cache[key]
        default = getattr(self.client, "loan_package_id", None)
        try:
            pkgs = self._extract_loan_pkgs(
                self.client.loan_packages(self.account_id, symbol=symbol))
            ids = {str(qget(p, "id", "loanpackageid", "loanproductid")) for p in pkgs}
            ids.discard("None")
            if not ids:
                res = (default, False, f"danh sách gói vay RỖNG cho {symbol}")
            elif str(want) in ids:
                res = (want, True, "")
            else:
                res = (default, False, f"gói {want} KHÔNG hợp lệ cho {symbol} "
                                       f"(hợp lệ: {sorted(ids)})")
        except Exception as e:
            res = (default, False, f"không kiểm được danh sách gói vay ({e})")
        self._log_raw("lever_package_validate",
                      {"symbol": symbol, "want": want, "resolved": res[0],
                       "ok": res[1], "note": res[2], "account_default": default})
        cache[key] = res
        return res

    def place_order(self, symbol, qty, side, price=None, order_type="LO",
                    cash_only=False, loan_package_id=None):
        lever_note, lever_ok = "", None
        if loan_package_id is not None:
            # Gói CHỈ ĐỊNH (đòn bẩy CAPIT) — ưu tiên cao nhất, nhưng phải hợp lệ với mã.
            lp, lever_ok, lever_note = self._validate_lever_package(symbol, loan_package_id)
            if not lever_ok:
                print(f"[dnse] ⚠ ĐÒN BẨY KHÔNG ÁP ĐƯỢC cho {symbol}: {lever_note} → dùng gói "
                      f"default {lp} (lệnh này KHÔNG có đòn bẩy — fail-safe, KHÔNG chặn lệnh)")
        elif side == "buy":
            # KHÔNG có gói chỉ định, lệnh MUA → giải gói hợp lệ cho MÃ, bất kể cash_only
            # (sửa 2026-08-07, ca DRI/UPCOM: lệnh thường trên UPCOM đi ra bằng lp=None ⇒
            # dnse_api rơi về gói default account 1841 = mainboard-only ⇒ DNSE reject
            # cả ppse lẫn place_order, biểu hiện y hệt "thiếu tiền" WAIT_CASH vô hạn).
            # An toàn gọi vô điều kiện: _resolve_loan_package_id GIỮ NGUYÊN gói default
            # khi default hợp lệ cho mã → no-op với mọi lệnh mainboard BAL/LAG/CAPIT.
            lp = self._resolve_loan_package_id(symbol)
        else:
            # Lệnh BÁN không mang loanPackageId (trừ khi chỉ định rõ ở trên) — DNSE tự
            # chọn deal khớp trong sổ vị thế. Resolve theo mã ở đây ép DNSE tìm deal đúng
            # gói vay đó, và deal PARK/vị thế cũ thường không nằm trong gói đó → HTTP 400
            # "deal not found" (bug 2026-08-10, 08-07→c22bd1c mở rộng nhầm sang cả BÁN).
            lp = None
        r = self.client.place_order(self.account_id, symbol, qty=int(qty),
                                    side=side, order_type=order_type, price=price,
                                    loan_package_id=lp)
        self._log_raw("place_order", {"req": [symbol, qty, side, price, order_type],
                                      "cash_only": cash_only, "loan_package_id": lp,
                                      "lever_requested": loan_package_id,
                                      "lever_applied": lever_ok, "lever_note": lever_note,
                                      "resp": r})
        oid = qget(r, "id", "orderid", "orderId")
        if oid is None:
            raise RuntimeError(f"place_order không trả id: {r}")
        return str(oid)

    def cancel_order(self, order_id):
        r = self.client.cancel_order(self.account_id, order_id)
        self._log_raw("cancel_order", {"order_id": order_id, "resp": r})
        return r

    def modify_order(self, order_id, qty, price):
        """Sửa lệnh LO trên DNSE. QUIRK đã verify 2026-06-26:
        DNSE luôn trả HTTP 500 'REMOTE_SERVER_ERROR' khi modify thành công
        (implement modify = cancel + re-place phía server, response bị lỗi).
        Old order bị Canceled, new order_id xuất hiện với price/qty mới.

        Returns: new_oid (str) nếu tìm được, None nếu không (caller dùng cancel+replace).
        """
        from dnse_api import DNSEError as _DNSEError
        try:
            r = self.client.modify_order(self.account_id, order_id, qty=qty, price=price)
            new_oid = str(qget(r, "id", "orderid", "orderId") or "")
            self._log_raw("modify_order", {"req": [order_id, qty, price],
                                           "resp": r, "new_oid": new_oid})
            return new_oid or None
        except _DNSEError as e:
            # 500 REMOTE_SERVER_ERROR = DNSE modify quirk — re-poll for new order_id
            if e.status == 500 and "REMOTE_SERVER_ERROR" in str(
                    (e.payload or {}).get("code", "")):
                self._log_raw("modify_order", {
                    "req": [order_id, qty, price],
                    "quirk": "HTTP 500 but success expected — re-polling",
                    "old_oid": order_id})
                import time as _time
                _time.sleep(1)
                updates = self.poll_orders()
                old = updates.get(str(order_id))
                if old and not old.is_dead:
                    return None  # modify thực ra chưa xong
                # Tìm order mới nhất còn sống (heuristic: id số lớn nhất)
                candidates = [(int(k), k) for k, u in updates.items()
                              if not u.is_dead and k != str(order_id)]
                if candidates:
                    new_oid = str(max(candidates)[1])
                    self._log_raw("modify_order_new_oid", {
                        "old_oid": order_id, "new_oid": new_oid,
                        "price": price, "qty": qty})
                    return new_oid
                return None
            raise  # khác 500 REMOTE_SERVER_ERROR → re-raise

    def poll_orders(self):
        r = self.client.orders(self.account_id)
        self._log_raw("orders", r)
        rows = r.get("orders") or r.get("data") if isinstance(r, dict) else r
        out = {}
        for o in rows or []:
            oid = qget(o, "id", "orderid", "orderId")
            if oid is None:
                continue
            filled = _fnum(qget(o, "fillquantity", "filledquantity", "cumqty",
                                "matchedquantity", "fillqty", "execqtty",
                                default=0)) or 0
            avg = normalize_price_vnd(_fnum(qget(o, "averageprice", "avgprice",
                                                 "fillprice", "matchprice")))
            out[str(oid)] = OrderUpdate(oid, qget(o, "orderstatus", "status",
                                                  default=""), filled, avg, raw=o)
        return out


# ---------------------------------------------------------- PHS FlashAPI live

class PHSFlashOrderUpdate(OrderUpdate):
    """OrderUpdate cho PHS FlashAPI — `is_dead` quyết bởi MÃ trạng thái, không phải
    heuristic chuỗi của lớp cha.

    Lý do: heuristic cha khớp cả ký tự đơn `"f"`/`"x"`, nên một trạng thái CÒN SỐNG như
    "Pending confirmation" (mã 13) sẽ bị coi là chết — chết-nhầm làm executor đóng con
    lệnh và giải phóng chỗ trong khi lệnh vẫn còn khớp được. Ở đây deadness đến từ một
    TẬP MÃ ĐÓNG lấy từ tài liệu chính thức; mã lạ ⇒ coi là CÒN SỐNG (fail-safe: kẹt một
    con lệnh còn hơn tạo trạng thái phơi nhiễm kép).
    """

    DEAD_CODES = {"0", "3", "5", "6", "12", "E", "R"}   # reject/cancel/expire/fully-matched

    def __init__(self, order_id, status="", filled_qty=0, avg_price=None, raw=None,
                 code=None):
        super().__init__(order_id, status, filled_qty, avg_price, raw)
        self.code = None if code is None else str(code).strip()

    @property
    def is_dead(self):
        if self.code in self.DEAD_CODES:
            return True
        if self.code == "4":            # "Matched" — chỉ chết khi không còn dư (số ĐO được)
            remain = _fnum(qget(self.raw, "remainqtty", "remain_qtty"))
            return remain is not None and remain == 0
        return False


class PHSFlashBroker(BrokerBase):
    """Broker PHS FlashAPI (flashapi.phs.vn) — KHÁC hẳn PHSBroker/FLEX (fgateway.phs.vn).

    Account profile trong secrets/trading_bot_accounts.json:
        {"label": "PHS", "mode": "paper", "broker": "phs_flash",
         "account_id": "0120xxxx",              # TIỂU KHOẢN CƠ SỞ, không phải 022Cxxxx
         "credentials_file": "secrets/phs_flash_credentials.json",
         "fno_account_id": "02120xxxx"}         # chỉ cần khi đọc phái sinh

    CHƯA GO-LIVE: hồ sơ đăng ký FlashAPI chưa nộp, mọi số dưới đây mới verify trên
    sandbox (sandbox trả fixture cho mọi accountId và KHÔNG validate Bearer token).
    """

    name = "phs_flash"
    can_trade_live = True

    def __init__(self, account_id=None, otp=None, quote_only=False,
                 credentials_file=None, label="main", fno_account_id=None,
                 loan_package_id=None):
        self.account_id = account_id          # tiểu khoản CƠ SỞ (eqt)
        self.fno_account_id = fno_account_id  # tiểu khoản PHÁI SINH (fno)
        self.label = label
        self._otp = otp                       # FlashAPI lấy otp_token ngay từ login
        self.quote_only = quote_only
        self.credentials_file = credentials_file
        self.client = None
        self._quote_cache = {}                # symbol -> (ts, Quote)
        self._quote_ttl = 3.0
        self._raw_log = os.path.join(
            EXEC_DIR, f"phs_flash_raw_{today_ict():%Y-%m-%d}.jsonl")

    def connect(self):
        self.client = get_phs_flash_client(self.credentials_file)
        self.account_id = self.account_id or self.client.eqt_account_id
        self.fno_account_id = self.fno_account_id or self.client.fno_account_id
        if self.quote_only:
            print(f"[phs_flash] chế độ quote-only ({self.client.env})")
            return self
        self.client.login(asset_type="underlying")
        if not self.account_id:
            raise RuntimeError(f"PHS FlashAPI ({self.label}): thiếu tiểu khoản cơ sở "
                               "(account_id/eqt_account_id)")
        print(f"[phs_flash] login OK ({self.client.env}, eqt={self.account_id})")
        return self

    # ------------------------------------------------------------------ tiền

    def get_cash(self):
        """Sức mua an toàn `ppse` — KHÔNG phải tiền SỞ HỮU (coding_guidelines §25: đây là
        vế "tiêu được ngay"). Consumer tính NAV/mẫu số tỷ trọng KHÔNG được dùng hàm này.

        Production fail-closed: `/underlying/buyingPower` bắt buộc symbol+quotePrice, còn
        `/underlying/assets` chưa probe được field (404 ở sandbox) ⇒ thà raise còn hơn đọc
        đại một field tên nghe giống tiền.
        """
        if self.client.env != "sandbox":
            raise RuntimeError(
                "[phs_flash] get_cash() chưa dùng được ở production: buyingPower cần "
                "symbol+quotePrice → gọi get_buying_power(symbol, price); trường tiền của "
                "/underlying/assets chưa được xác nhận với PHS.")
        rows = self.client.get_buying_power(self.account_id)
        self._log_raw("underlying_balance", rows)
        row = rows[0] if isinstance(rows, list) and rows else rows
        return _fnum(qget(row, "ppse", default=0)) or 0.0

    def get_max_buy_qty(self, symbol, price, loan_package_id=None):
        """Số CP mua tối đa theo chính broker (`maxqty`). Lỗi → None (caller tự fail-safe)."""
        try:
            rows = self.client.get_buying_power(self.account_id, symbol, int(price))
            self._log_raw("buying_power", {"symbol": symbol, "price": price, "resp": rows})
            row = rows[0] if isinstance(rows, list) and rows else rows
            v = _fnum(qget(row, "maxqty", "maxqtty"))
            return int(v) if v is not None and v >= 0 else None
        except Exception:
            return None

    def get_buying_power(self, symbol, price, loan_package_id=None):
        """Sức mua VND (`ppse`) theo mã + giá. Lỗi → None, KHÔNG suy ra từ get_cash()."""
        try:
            rows = self.client.get_buying_power(self.account_id, symbol, int(price))
            self._log_raw("buying_power", {"symbol": symbol, "price": price, "resp": rows})
            row = rows[0] if isinstance(rows, list) and rows else rows
            v = _fnum(qget(row, "ppse"))
            return float(v) if v is not None and v >= 0 else None
        except Exception:
            return None

    # ------------------------------------------------------------- danh mục

    def get_positions(self):
        rows = self.client.get_positions(self.account_id) or []
        self._log_raw("portfolio", rows)
        out = {}
        for p in rows:
            sym = qget(p, "symbol", "instrument", "code")
            total = int(_fnum(qget(p, "total", default=0)) or 0)
            sellable = int(_fnum(qget(p, "trade", default=total)) or total)
            # CP chờ về = CẢ BA chặng T0/T1/T2 (mua T0 về T+2), không chỉ receivingT2:
            # chỉ lấy T2 sẽ báo thiếu đúng phần vừa mua 1-2 phiên trước. Chưa có consumer
            # nào đọc khóa này — thêm để đủ thông tin, không đổi ngữ nghĩa total/sellable.
            receivable = sum(int(_fnum(qget(p, k, default=0)) or 0)
                             for k in ("receivingT0", "receivingT1", "receivingT2"))
            if sym and total > 0:
                out[sym] = {"total": total, "sellable": sellable,
                            "receivable": receivable,
                            "costPrice": _fnum(qget(p, "costprice"))}
        return out

    # ------------------------------------------------------------- bảng giá

    def get_quote(self, symbol):
        import time as _t
        hit = self._quote_cache.get(symbol)
        if hit and _t.time() - hit[0] < self._quote_ttl:
            return hit[1]
        try:
            rows = self.client.get_quote(symbol)
        except Exception as e:
            print(f"[phs_flash] ⚠ quote {symbol} lỗi: {e}")
            return None
        # Lấy ĐÚNG dòng của mã đã hỏi, KHÔNG lấy rows[0]: feed trả list và không đảm bảo
        # thứ tự/đủ mã (sandbox còn trả nguyên fixture ACB cho mọi symbolList). Lấy nhầm
        # dòng nghĩa là gán giá của mã KHÁC cho lệnh — sai im lặng, nên fail-closed: không
        # khớp mã ⇒ trả None để caller tự xử, không đoán.
        rows = rows if isinstance(rows, list) else [rows]
        row = next((r for r in rows if isinstance(r, dict)
                    and str(r.get("s", "")).strip().upper() == str(symbol).strip().upper()),
                   None)
        if row is None:
            self._log_raw("quote_symbol_mismatch",
                          {"asked": symbol, "got": [r.get("s") for r in rows if isinstance(r, dict)]})
        q = None
        if isinstance(row, dict):
            q = Quote(self._quote_aliases(row))
            if not q.ok():
                self._log_raw("quote_unmapped", row)
            # KHÔNG dựng l2_snapshot: symbol-latest-data chỉ có 3 mức LÔ LẺ (bbOd/boOd),
            # không phải sổ lệnh lô chẵn — dựng L2 từ đó là bịa thanh khoản.
            q.l2_snapshot = None
        self._quote_cache[symbol] = (_t.time(), q)
        return q

    @staticmethod
    def _quote_aliases(row):
        """Thêm khóa alias mà `Quote` biết đọc, GIỮ NGUYÊN payload thô bên dưới.

        Tên trường FlashAPI viết tắt một ký tự (`c` giá khớp, `re` tham chiếu, `s` mã) nên
        `Quote` — vốn dò theo tên dài — không tự khớp được. Bid/ask CỐ Ý bỏ trống: feed chỉ
        cấp lô lẻ.
        """
        return dict(row,
                    symbol=row.get("s"),
                    lastPrice=row.get("c"),
                    refPrice=row.get("re"),
                    totalVolume=row.get("vo"))

    # ------------------------------------------------------------------ lệnh

    def place_order(self, symbol, qty, side, price=None, order_type="LO",
                    cash_only=False, loan_package_id=None):
        """Đặt lệnh cơ sở. `cash_only`/`loan_package_id` là khái niệm gói vay của DNSE,
        PHS không dùng → bỏ qua (giữ chữ ký chung cho executor).

        Order type hợp lệ (PHS support xác nhận): HOSE = LO/ATO/ATC/MP;
        HNX+UPCOM = LO/MOK/MAK/PLO.
        """
        if price is None:
            # `limitPrice` là trường BẮT BUỘC của API kể cả với lệnh không phải LO; giá trị
            # hợp lệ cho ATO/ATC/MP chưa được PHS xác nhận ⇒ chặn ở đây thay vì gửi 0.
            raise RuntimeError(f"[phs_flash] {order_type} thiếu price — FlashAPI bắt buộc "
                               "limitPrice, giá trị cho lệnh thị trường chưa xác nhận với PHS")
        params = {"instrument": symbol, "qty": int(qty), "side": str(side).lower(),
                  "type": order_type, "limitPrice": int(price), "timetype": "T"}
        r = self.client.place_order(self.account_id, params)
        self._log_raw("place_order", {"req": params, "resp": r})
        oid = qget(r, "orderid", "orderId", "id")
        if not oid:
            raise RuntimeError(f"place_order không trả orderid: {r}")
        return str(oid)

    def cancel_order(self, order_id):
        r = self.client.cancel_order(self.account_id, order_id)
        self._log_raw("cancel_order", {"order_id": order_id, "resp": r})
        return r

    def poll_orders(self):
        from phs_flash_api import underlying_status_label
        rows = self.client.get_daily_orders(self.account_id) or []
        self._log_raw("daily_orders", rows)
        out = {}
        for o in rows:
            oid = qget(o, "orderid", "orderId", "id")
            if oid is None:
                continue
            filled = _fnum(qget(o, "execqtty", "matchqtty", default=0)) or 0
            avg = normalize_price_vnd(_fnum(qget(o, "execprice", "matchprice", "avgprice")))
            code = qget(o, "orstatuscode", "orstatusvalue", "status_code")
            out[str(oid)] = PHSFlashOrderUpdate(
                oid, underlying_status_label(o), filled, avg, raw=o, code=code)
        return out

    # -------------------------------------------------------------- phái sinh

    def get_derivative_balance(self):
        """Phase 1 chỉ ĐỌC phái sinh (đặt lệnh phái sinh chưa xác nhận spec)."""
        r = self.client.get_derivative_balance(self.fno_account_id)
        self._log_raw("derivative_balance", r)
        return r

    def get_derivative_positions(self):
        r = self.client.get_derivative_positions(self.fno_account_id)
        self._log_raw("derivative_positions", r)
        return r


# --------------------------------------------------------------- Paper sim

class PaperBroker(BrokerBase):
    """Khớp mô phỏng trên quote thật. Lệnh LO mua khớp khi limit ≥ ask (hoặc last),
    bán khớp khi limit ≤ bid (hoặc last); ATO/ATC khớp ngay tại ref/last.
    Trạng thái tiền + danh mục: data/bot_paper_account.json (bền qua nhiều phiên).
    """

    name = "paper"
    can_trade_live = False

    def __init__(self, init_cash=1_000_000_000, fee_rate=0.0015, quote_source=None,
                 fill_at_ref_if_no_quote=False, label="main"):
        self.fee_rate = fee_rate
        self.quote_source = quote_source        # PHSBroker (chỉ dùng quote) hoặc None
        self.fill_at_ref = fill_at_ref_if_no_quote
        self.label = label
        self.state_file = (PAPER_STATE_FILE if label == "main"
                           else os.path.join(DATA_DIR, f"bot_paper_{label}.json"))
        self._init_cash = init_cash
        self.state = None
        self._fallback_ref = {}                 # symbol -> ref_price từ plan (offline)

    def connect(self):
        if self.quote_source is not None:
            try:
                if self.quote_source.client is None:
                    self.quote_source.connect()
            except Exception as e:
                print(f"[paper] ⚠ không kết nối được PHS quote ({e}) — "
                      f"dùng ref_price của plan làm giá mô phỏng")
                self.quote_source = None
        self._load()
        print(f"[paper] tài khoản ảo [{self.label}]: cash "
              f"{self.state['cash']/1e6:,.0f}M, {len(self.state['positions'])} mã")
        return self

    # ----- state -----
    def _load(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, encoding="utf-8") as f:
                self.state = json.load(f)
        else:
            self.state = {"cash": self._init_cash, "positions": {},
                          "open_orders": {}, "fills": [], "next_id": 1}
            self._save()
        self.state.setdefault("open_orders", {})
        self.state.setdefault("fills", [])

    def _save(self):
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def set_fallback_refs(self, mapping):
        """{symbol: ref_price} từ plan — giá mô phỏng khi không có quote PHS."""
        self._fallback_ref.update(mapping or {})

    # ----- interface -----
    def get_cash(self):
        return float(self.state["cash"])

    def get_positions(self):
        return {s: {"total": int(q), "sellable": int(q)}
                for s, q in self.state["positions"].items() if q > 0}

    def get_quote(self, symbol):
        if self.quote_source is not None:
            q = self.quote_source.get_quote(symbol)
            if q and q.ok():
                return q
        ref = self._fallback_ref.get(symbol)
        if ref:
            return Quote({"symbol": symbol, "refPrice": ref, "lastPrice": ref})
        return None

    def place_order(self, symbol, qty, side, price=None, order_type="LO",
                    cash_only=False, loan_package_id=None):
        # Paper broker không vay thật → cờ cash_only không áp dụng. `loan_package_id` thì có
        # GHI LẠI (không dùng để tính tiền): diễn tập đòn bẩy CAPIT cần bằng chứng cờ vay đi
        # trọn đường từ tín hiệu → plan → lệnh, chứ không phải mô tả suông.
        oid = f"P{self.state['next_id']:06d}"
        self.state["next_id"] += 1
        self.state["open_orders"][oid] = {
            "symbol": symbol, "qty": int(qty), "side": side, "price": price,
            "type": order_type, "filled": 0, "status": "open",
            "loanPackageId": loan_package_id,
            "ts": now_ict().isoformat(timespec="seconds")}
        self._try_fill(oid)
        self._save()
        return oid

    def cancel_order(self, order_id):
        o = self.state["open_orders"].get(order_id)
        if o and o["status"] == "open":
            o["status"] = "cancelled"
            self._save()
        return {"orderId": order_id, "status": "cancelled"}

    def poll_orders(self):
        # Day-scope like the real broker: DNSEBroker.poll_orders() returns TODAY's order
        # book only, but open_orders here persists across sessions (bot_paper_account.json)
        # — returning all-time orders fed yesterday's FILLED orders to the ghost guard
        # (Executor._ghost_tickers: not in today's fresh state + filled>0 → ghost), pausing
        # every plan ticker each new day (observed 2026-07-08/09, all 6 probe tickers).
        # Same filter on the fill loop: a stale "open" order from a prior day must not
        # fill against today's ref price and mutate cash/positions.
        today = today_ict().isoformat()
        for oid, o in list(self.state["open_orders"].items()):
            if o.get("ts", "")[:10] == today:
                self._try_fill(oid)
        self._save()
        # raw={"symbol": ...}: without it Executor._ghost_tickers() (executor.py) can
        # never resolve a symbol for a paper order (qget(None, ...) -> None), so paper
        # trading could never rehearse the idempotency guard — same shape as the real
        # DNSEBroker.poll_orders(), which always sets raw to the full broker order row.
        # `loanPackageId` added 2026-08-03 for the same reason, one guard later:
        # Executor._lever_package_audit() reads the loan package off the broker order row
        # (verified present on 23.124 real DNSE rows in data/execution_logs/dnse_raw_*.jsonl).
        # Omitting it here would leave the CAPIT-leverage guard un-rehearsable on paper —
        # exactly the hole raw=None left in the ghost guard until 2026-07-02.
        return {oid: OrderUpdate(oid, o["status"], o["filled"], o.get("avg_price"),
                                 raw={"symbol": o["symbol"],
                                      "loanPackageId": o.get("loanPackageId")})
                for oid, o in self.state["open_orders"].items()
                if o.get("ts", "")[:10] == today}

    # ----- fill engine -----
    def _try_fill(self, oid):
        o = self.state["open_orders"][oid]
        if o["status"] != "open":
            return
        q = self.get_quote(o["symbol"])
        if q is None or not q.ok():
            return
        last = q.last or q.ref
        fill_px = None
        if o["type"] in ("ATO", "ATC"):
            fill_px = last
        elif o["price"] is None:
            fill_px = last
        else:
            if o["side"] == "buy":
                mkt = q.ask or last
                if mkt is not None and o["price"] >= mkt:
                    fill_px = min(o["price"], mkt)
            else:
                mkt = q.bid or last
                if mkt is not None and o["price"] <= mkt:
                    fill_px = mkt
        if fill_px is None:
            return
        qty = o["qty"] - o["filled"]
        value = qty * fill_px
        fee = value * self.fee_rate
        if o["side"] == "buy":
            if self.state["cash"] < value + fee:
                o["status"] = "rejected_cash"
                return
            self.state["cash"] -= value + fee
            self.state["positions"][o["symbol"]] = \
                self.state["positions"].get(o["symbol"], 0) + qty
        else:
            have = self.state["positions"].get(o["symbol"], 0)
            if have < qty:
                o["status"] = "rejected_qty"
                return
            self.state["cash"] += value - fee
            self.state["positions"][o["symbol"]] = have - qty
        o["filled"] = o["qty"]
        o["avg_price"] = fill_px
        o["status"] = "filled"
        self.state["fills"].append(
            {"ts": now_ict().isoformat(timespec="seconds"), "order_id": oid,
             "symbol": o["symbol"], "side": o["side"], "qty": qty,
             "price": fill_px, "fee": round(fee)})


BROKER_CLASSES = {"phs": PHSBroker, "dnse": DNSEBroker,
                  "phs_flash": PHSFlashBroker}

# Pool nguồn quote dùng chung (1 per broker-type × credentials) cho paper accounts
_QUOTE_POOL = {}


def get_quote_source(broker_type, credentials_file=None):
    key = (broker_type, os.path.abspath(credentials_file or "default"))
    if key not in _QUOTE_POOL:
        cls = BROKER_CLASSES[broker_type]
        _QUOTE_POOL[key] = cls(quote_only=True, credentials_file=credentials_file)
    return _QUOTE_POOL[key]


def make_broker(cfg, otp=None, need_quotes=True, profile=None, quote_src=None):
    """Factory theo mode + broker. profile = account profile
    (label/broker/credentials_file/account_id); broker: "phs" | "dnse".
    quote_src override nguồn quote cho paper (mặc định pool theo broker)."""
    p = profile or {"label": "main", "credentials_file": None,
                    "account_id": cfg.get("account_id")}
    btype = (p.get("broker") or cfg.get("broker") or "phs").lower()
    if btype not in BROKER_CLASSES:
        raise KeyError(f"broker '{btype}' không hỗ trợ — có: {sorted(BROKER_CLASSES)}")
    if cfg["mode"] == "live":
        return BROKER_CLASSES[btype](account_id=p.get("account_id"), otp=otp,
                                     credentials_file=p.get("credentials_file"),
                                     label=p["label"],
                                     loan_package_id=p.get("loan_package_id"))
    if quote_src is None and need_quotes:
        quote_src = get_quote_source(btype, p.get("credentials_file"))
    return PaperBroker(init_cash=cfg["paper_init_cash"],
                       fee_rate=cfg["paper_fee_rate"],
                       quote_source=quote_src, label=p["label"])
