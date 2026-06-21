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
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .config import DATA_DIR, EXEC_DIR
from .vn_market import normalize_price_vnd

PAPER_STATE_FILE = os.path.join(DATA_DIR, "bot_paper_account.json")  # legacy (label main)
DEFAULT_CREDENTIALS = os.path.join(DATA_DIR, "phs_credentials.json")
DEFAULT_DNSE_CREDENTIALS = os.path.join(DATA_DIR, "dnse_credentials.json")

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


class Quote:
    """Snapshot giá chuẩn hóa từ payload instrument PHS (mọi giá VND)."""

    def __init__(self, raw):
        self.raw = raw
        p = lambda *n: normalize_price_vnd(_fnum(qget(raw, *n)))
        self.symbol = qget(raw, "symbol", "instrument", "code", "sym")
        self.exchange = qget(raw, "exchange", "market", "floorcode", default="HOSE")
        self.last = p("lastprice", "last", "matchprice", "closeprice", "close", "price")
        self.ref = p("refprice", "reference", "basicprice", "referenceprice",
                     "priorcloseprice", "ref")
        self.ceiling = p("ceiling", "ceilingprice", "ce", "highlimit")
        self.floor = p("floor", "floorprice", "fl", "lowlimit")
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
        """Lệnh không còn sống (hủy/từ chối/khớp hết) — best-effort theo status string."""
        s = self.status.lower()
        if "partial" in s:        # PartiallyFilled (DNSE) vẫn đang sống
            return False
        return any(k in s for k in ("cancel", "hủy", "huy", "reject", "từ chối",
                                    "fill", "khớp hết", "matchall", "expire", "f", "x"))


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
                f.write(json.dumps({"ts": dt.datetime.now().isoformat(timespec="seconds"),
                                    "kind": kind, "payload": payload},
                                   ensure_ascii=False, default=str) + "\n")
        except OSError:
            pass

    def connect(self):
        raise NotImplementedError

    def get_cash(self):
        """Tiền mặt khả dụng (VND)."""
        raise NotImplementedError

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

    def place_order(self, symbol, qty, side, price=None, order_type="LO"):
        """→ order_id (str)."""
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
            EXEC_DIR, f"phs_raw_{dt.date.today():%Y-%m-%d}.jsonl")

    def connect(self):
        self.client = get_flex_client(self.credentials_file)
        if self.quote_only:
            print("[phs] chế độ quote-only (datafeed)")
            return self
        if not self.client.access_token:
            raise RuntimeError(f"PHS login thất bại ({self.label}) — kiểm tra "
                               f"{self.credentials_file or 'data/phs_credentials.json'}")
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
        if q and not q.ok():
            self._log_raw("quote_unmapped", row)   # mapping field chưa khớp → cần xem raw
        self._quote_cache[symbol] = (_t.time(), q)
        return q

    def place_order(self, symbol, qty, side, price=None, order_type="LO"):
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
                 credentials_file=None, label="main"):
        self.account_id = account_id
        self.label = label
        self._otp = otp
        self.quote_only = quote_only
        self.credentials_file = credentials_file
        self.client = None
        self._quote_cache = {}      # symbol -> (ts, Quote)
        self._secdef_cache = {}     # symbol -> dict (trần/sàn/ref — tĩnh trong ngày)
        self._quote_ttl = 3.0
        self._raw_log = os.path.join(
            EXEC_DIR, f"dnse_raw_{dt.date.today():%Y-%m-%d}.jsonl")

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
            if sym and total > 0:
                out[sym] = {"total": total, "sellable": sellable}
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
        # 2) khớp lệnh mới nhất — {"trades":[board G1: matchPrice, totalVolumeTraded]}
        try:
            raw.update(self._pick_board(self.client.latest_trade(symbol), "trades"))
        except Exception as e:
            print(f"[dnse] ⚠ trade {symbol} lỗi: {e}")
        # 3) top giá chờ — {"quotes":[board G1: bid/offer = [{price, quantity},…]]}
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
        except Exception as e:
            print(f"[dnse] ⚠ quote {symbol} lỗi: {e}")
        q = Quote(raw)
        if not q.ok():
            self._log_raw("quote_unmapped", raw)
        self._quote_cache[symbol] = (_t.time(), q)
        return q

    def place_order(self, symbol, qty, side, price=None, order_type="LO"):
        r = self.client.place_order(self.account_id, symbol, qty=int(qty),
                                    side=side, order_type=order_type, price=price)
        self._log_raw("place_order", {"req": [symbol, qty, side, price, order_type],
                                      "resp": r})
        oid = qget(r, "id", "orderid", "orderId")
        if oid is None:
            raise RuntimeError(f"place_order không trả id: {r}")
        return str(oid)

    def cancel_order(self, order_id):
        r = self.client.cancel_order(self.account_id, order_id)
        self._log_raw("cancel_order", {"order_id": order_id, "resp": r})
        return r

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

    def place_order(self, symbol, qty, side, price=None, order_type="LO"):
        oid = f"P{self.state['next_id']:06d}"
        self.state["next_id"] += 1
        self.state["open_orders"][oid] = {
            "symbol": symbol, "qty": int(qty), "side": side, "price": price,
            "type": order_type, "filled": 0, "status": "open",
            "ts": dt.datetime.now().isoformat(timespec="seconds")}
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
        for oid in list(self.state["open_orders"]):
            self._try_fill(oid)
        self._save()
        return {oid: OrderUpdate(oid, o["status"], o["filled"], o.get("avg_price"))
                for oid, o in self.state["open_orders"].items()}

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
            {"ts": dt.datetime.now().isoformat(timespec="seconds"), "order_id": oid,
             "symbol": o["symbol"], "side": o["side"], "qty": qty,
             "price": fill_px, "fee": round(fee)})


BROKER_CLASSES = {"phs": PHSBroker, "dnse": DNSEBroker}

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
                                     label=p["label"])
    if quote_src is None and need_quotes:
        quote_src = get_quote_source(btype, p.get("credentials_file"))
    return PaperBroker(init_cash=cfg["paper_init_cash"],
                       fee_rate=cfg["paper_fee_rate"],
                       quote_source=quote_src, label=p["label"])
