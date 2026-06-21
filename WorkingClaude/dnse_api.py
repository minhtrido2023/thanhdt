# -*- coding: utf-8 -*-
"""DNSE OpenAPI v2 wrapper — REST (trading + inquiry + market data).

Nguồn đặc tả:
  - https://developers.dnse.com.vn (Guide + API Specification)
  - SDK chính thức github.com/dnse-tech/openapi-sdk (python/dnse/api/client.py)
    — phần ký HMAC tái tạo 1:1 theo SDK.

Khác PHS FLEX: KHÔNG login username/password. Mọi request ký bằng
API Key + API Secret (đăng ký 1 lần tại entradex.dnse.com.vn → Lightspeed API;
API Secret chỉ hiện đúng 1 lần). Đặt/sửa/hủy lệnh cần thêm trading-token
(hiệu lực 8h) lấy bằng OTP:
  - smart_otp: mã từ app EntradeX (hạn 30s)
  - email_otp: gọi send_email_otp() rồi nhập mã trong mail (hạn 2 phút)

Dùng:
    from dnse_api import DNSEClient

    c = DNSEClient.from_credentials_file()       # data/dnse_credentials.json
    accs = c.accounts()                          # {"accounts":[{"id":...},...],...}
    acc = accs["accounts"][0]["id"]

    c.balances(acc)                              # số dư tiền
    c.positions(acc)                             # danh mục
    c.latest_quote("HPG"); c.latest_trade("HPG") # bảng giá
    c.ppse(acc, "HPG", 25950)                    # sức mua

    c.send_email_otp()                           # nếu dùng email_otp
    c.create_trading_token("123456")             # otp → token 8h (tự cache)
    r = c.place_order(acc, "HPG", qty=100, side="buy", order_type="LO", price=25950)
    c.cancel_order(acc, r["id"])

data/dnse_credentials.json:
    {"api_key": "...", "api_secret": "...", "otp_type": "smart_otp",
     "loan_package_id": null}
"""

import base64
import hashlib
import hmac
import json
import os
import time
import uuid
from datetime import datetime, timezone
from urllib.parse import quote, urlencode

import requests

BASE_URL = "https://openapi.dnse.com.vn"
API_VERSION = "2026-05-07"
WORKDIR = os.path.dirname(os.path.abspath(__file__))
CRED_FILE = os.path.join(WORKDIR, "secrets", "dnse_credentials.json")
TOKEN_CACHE = os.path.join(WORKDIR, "data", "dnse_trading_token.json")
TRADING_TOKEN_TTL = 8 * 3600 - 300       # 8h trừ 5' đệm


class DNSEError(Exception):
    """Lỗi API DNSE (HTTP >= 400 hoặc body báo lỗi)."""

    def __init__(self, message, status=None, payload=None):
        super().__init__(message)
        self.status = status
        self.payload = payload


class DNSEClient:
    """REST client cho DNSE OpenAPI v2 (ký HMAC mỗi request)."""

    def __init__(self, api_key, api_secret, base_url=BASE_URL,
                 otp_type="smart_otp", loan_package_id=None,
                 token_cache=TOKEN_CACHE, timeout=30):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.otp_type = otp_type                  # "smart_otp" | "email_otp"
        self.loan_package_id = loan_package_id    # gói vay mặc định khi đặt lệnh
        self.token_cache = token_cache
        self.timeout = timeout
        self.trading_token = None
        self.token_expiry = 0
        self.session = requests.Session()
        self._load_token_cache()

    # ------------------------------------------------------------------ auth

    @classmethod
    def from_credentials_file(cls, path=None, **kwargs):
        """Tạo client từ data/dnse_credentials.json (api_key, api_secret,
        otp_type, loan_package_id; token cache đặt cạnh theo tên file)."""
        path = path or CRED_FILE
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        for k in ("api_key", "api_secret", "otp_type", "loan_package_id"):
            v = d.get(k)
            if v not in (None, "") and "DIEN_" not in str(v):
                kwargs.setdefault(k, v)
        if os.path.abspath(path) != os.path.abspath(CRED_FILE):
            stem = os.path.splitext(os.path.basename(path))[0]
            kwargs.setdefault("token_cache",
                              os.path.join(WORKDIR, "data", f"dnse_token_{stem}.json"))
        if "api_key" not in kwargs or "api_secret" not in kwargs:
            raise DNSEError(f"thiếu api_key/api_secret trong {path}")
        return cls(**kwargs)

    def send_email_otp(self):
        """Gửi OTP vào email (chỉ khi tài khoản dùng email_otp; hạn 2 phút)."""
        return self._request("POST", "/registration/send-email-otp")

    def create_trading_token(self, passcode, otp_type=None):
        """Đổi OTP lấy trading-token (hiệu lực 8h, tự cache ra file)."""
        r = self._request("POST", "/registration/trading-token",
                          body={"otpType": otp_type or self.otp_type,
                                "passcode": str(passcode)})
        tok = None
        if isinstance(r, dict):
            tok = r.get("trading-token") or r.get("tradingToken") or r.get("token")
        if not tok:
            raise DNSEError(f"không thấy trading-token trong response: {r}")
        self.trading_token = tok
        self.token_expiry = time.time() + TRADING_TOKEN_TTL
        self._save_token_cache()
        return r

    def has_trading_token(self):
        return bool(self.trading_token) and time.time() < self.token_expiry

    # --------------------------------------------------------------- trading

    def place_order(self, account_id, symbol, qty, side, order_type="LO",
                    price=None, market_type="STOCK", order_category="NORMAL",
                    loan_package_id=None):
        """Đặt lệnh — POST /accounts/orders?marketType=&orderCategory=.

        side: "buy"/"sell" (tự đổi sang NB/NS) hoặc truyền thẳng "NB"/"NS".
        order_type: LO, ATO, ATC, MTL (HOSE); LO/MTL/MOK/MAK/ATC/PLO (HNX).
        """
        body = {"accountNo": account_id, "symbol": symbol,
                "side": _side(side), "orderType": order_type,
                "quantity": int(qty)}
        if price is not None:
            body["price"] = price
        lp = loan_package_id or self.loan_package_id
        if lp is not None:
            body["loanPackageId"] = lp
        return self._request("POST", "/accounts/orders",
                             query={"marketType": market_type,
                                    "orderCategory": order_category},
                             body=body, trading=True)

    def modify_order(self, account_id, order_id, qty=None, price=None,
                     market_type="STOCK", order_category="NORMAL"):
        """Sửa lệnh LO (status New/PartiallyFilled) — PUT .../orders/{id}."""
        body = {}
        if price is not None:
            body["price"] = price
        if qty is not None:
            body["quantity"] = int(qty)
        return self._request("PUT", f"/accounts/{account_id}/orders/{order_id}",
                             query={"marketType": market_type,
                                    "orderCategory": order_category},
                             body=body, trading=True)

    def cancel_order(self, account_id, order_id, market_type="STOCK",
                     order_category="NORMAL"):
        """Hủy lệnh — DELETE /accounts/{acc}/orders/{id}."""
        return self._request("DELETE", f"/accounts/{account_id}/orders/{order_id}",
                             query={"marketType": market_type,
                                    "orderCategory": order_category},
                             trading=True)

    # --------------------------------------------------------------- inquiry

    def accounts(self):
        """Thông tin định danh + danh sách tiểu khoản — GET /accounts."""
        return self._request("GET", "/accounts")

    def balances(self, account_id):
        """Số dư tiền — GET /accounts/{acc}/balances."""
        return self._request("GET", f"/accounts/{account_id}/balances")

    def positions(self, account_id, market_type="STOCK"):
        """Danh mục đang nắm giữ — GET /accounts/{acc}/positions."""
        return self._request("GET", f"/accounts/{account_id}/positions",
                             query={"marketType": market_type})

    def orders(self, account_id, market_type="STOCK", order_category=None):
        """Sổ lệnh trong ngày — GET /accounts/{acc}/orders."""
        q = {"marketType": market_type}
        if order_category:
            q["orderCategory"] = order_category
        return self._request("GET", f"/accounts/{account_id}/orders", query=q)

    def order_detail(self, account_id, order_id, market_type="STOCK"):
        return self._request("GET", f"/accounts/{account_id}/orders/{order_id}",
                             query={"marketType": market_type})

    def order_history(self, account_id, from_date=None, to_date=None,
                      market_type="STOCK", page_size=None, page_index=None):
        """Lịch sử lệnh (tới 1 năm). Ngày dạng YYYY-MM-DD."""
        q = {"marketType": market_type}
        for k, v in (("from", from_date), ("to", to_date),
                     ("pageSize", page_size), ("pageIndex", page_index)):
            if v is not None:
                q[k] = v
        return self._request("GET", f"/accounts/{account_id}/orders/history",
                             query=q)

    def ppse(self, account_id, symbol, price, market_type="STOCK",
             loan_package_id=None):
        """Sức mua/bán tối đa theo mã+giá — GET /accounts/{acc}/ppse."""
        lp = loan_package_id or self.loan_package_id or 0
        return self._request("GET", f"/accounts/{account_id}/ppse",
                             query={"marketType": market_type, "symbol": symbol,
                                    "price": str(price),
                                    "loanPackageId": str(lp)})

    def loan_packages(self, account_id, market_type="STOCK", symbol=None):
        """Danh sách gói vay (lấy loanPackageId cho lệnh thường/margin)."""
        q = {"marketType": market_type}
        if symbol:
            q["symbol"] = symbol
        return self._request("GET", f"/accounts/{account_id}/loan-packages",
                             query=q)

    # ----------------------------------------------------------- market data

    def instruments(self, symbol=None, market_id=None, index_name=None,
                    limit=None, page=None):
        q = {k: v for k, v in (("symbol", symbol), ("marketId", market_id),
                               ("indexName", index_name), ("limit", limit),
                               ("page", page)) if v is not None}
        return self._request("GET", "/instruments", query=q or None)

    def secdef(self, symbol, board_id=None):
        """Security definition: trần/sàn/tham chiếu, lô, bước giá."""
        q = {"boardId": board_id} if board_id else None
        return self._request("GET", f"/price/{symbol}/secdef", query=q)

    def latest_trade(self, symbol, board_id=None):
        """Khớp lệnh mới nhất: matchPrice, totalVolumeTraded…"""
        q = {"boardId": board_id} if board_id else None
        return self._request("GET", f"/price/{symbol}/trades/latest", query=q)

    def latest_quote(self, symbol, board_id=None):
        """Top giá chờ mua/bán mới nhất."""
        q = {"boardId": board_id} if board_id else None
        return self._request("GET", f"/price/{symbol}/quotes/latest", query=q)

    def close_price(self, symbol, board_id=None):
        q = {"boardId": board_id} if board_id else None
        return self._request("GET", f"/price/{symbol}/close", query=q)

    def ohlc(self, symbol, resolution="1D", bar_type="stock", **query):
        query.update({"symbol": symbol, "resolution": resolution,
                      "type": bar_type})
        return self._request("GET", "/price/ohlc", query=query)

    def working_dates(self):
        return self._request("GET", "/market/working-dates")

    # -------------------------------------------------------------- plumbing

    def _sign(self, method, path):
        """Ký HMAC theo SDK chính thức: signing string = (request-target) +
        date (+ nonce), KHÔNG gồm query string; Date lệch quá ±1' bị từ chối."""
        date_value = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %z")
        nonce = uuid.uuid4().hex
        signing = (f"(request-target): {method.lower()} {path}\n"
                   f"date: {date_value}\n"
                   f"nonce: {nonce}")
        mac = hmac.new(self.api_secret.encode("utf-8"),
                       signing.encode("utf-8"), hashlib.sha256)
        sig = quote(base64.b64encode(mac.digest()).decode("utf-8"), safe="")
        header = (f'Signature keyId="{self.api_key}",algorithm="hmac-sha256",'
                  f'headers="(request-target) date",signature="{sig}",'
                  f'nonce="{nonce}"')
        return date_value, header

    def _request(self, method, path, query=None, body=None, trading=False):
        date_value, signature = self._sign(method, path)
        headers = {"Date": date_value, "X-Signature": signature,
                   "x-api-key": self.api_key, "version": API_VERSION}
        if trading:
            if not self.has_trading_token():
                raise DNSEError("chưa có trading-token còn hạn — gọi "
                                "create_trading_token(otp) trước khi đặt/sửa/hủy lệnh.")
            headers["trading-token"] = self.trading_token
        url = self.base_url + path
        if query:
            url += "?" + urlencode(query)
        r = self.session.request(method, url, headers=headers,
                                 json=body if body is not None else None,
                                 timeout=self.timeout)
        try:
            data = r.json() if r.text else {}
        except ValueError:
            raise DNSEError(f"HTTP {r.status_code}: {r.text[:300]}",
                            status=r.status_code)
        if r.status_code >= 400:
            msg = data.get("message") or data.get("error") or str(data) \
                if isinstance(data, dict) else str(data)
            raise DNSEError(f"HTTP {r.status_code}: {msg}",
                            status=r.status_code, payload=data)
        return data

    def _save_token_cache(self):
        if not self.token_cache:
            return
        try:
            os.makedirs(os.path.dirname(self.token_cache), exist_ok=True)
            with open(self.token_cache, "w", encoding="utf-8") as f:
                json.dump({"trading_token": self.trading_token,
                           "token_expiry": self.token_expiry}, f)
        except OSError:
            pass

    def _load_token_cache(self):
        if not (self.token_cache and os.path.exists(self.token_cache)):
            return
        try:
            with open(self.token_cache, encoding="utf-8") as f:
                d = json.load(f)
            if d.get("token_expiry", 0) > time.time():
                self.trading_token = d.get("trading_token")
                self.token_expiry = d["token_expiry"]
        except (OSError, ValueError, KeyError):
            pass


def _side(side):
    s = str(side).lower()
    if s in ("buy", "nb", "b"):
        return "NB"
    if s in ("sell", "ns", "s"):
        return "NS"
    raise DNSEError(f"side không hợp lệ: {side}")


if __name__ == "__main__":
    # Demo read-only: secdef + quote 1 mã (cần data/dnse_credentials.json)
    import argparse
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(description="DNSE OpenAPI wrapper demo")
    ap.add_argument("--symbol", default="HPG")
    ap.add_argument("--accounts", action="store_true", help="liệt kê tiểu khoản")
    args = ap.parse_args()

    c = DNSEClient.from_credentials_file()
    if args.accounts:
        print(json.dumps(c.accounts(), ensure_ascii=False, indent=2)[:2000])
    print("secdef:", json.dumps(c.secdef(args.symbol), ensure_ascii=False)[:500])
    print("trade :", json.dumps(c.latest_trade(args.symbol), ensure_ascii=False)[:500])
    print("quote :", json.dumps(c.latest_quote(args.symbol), ensure_ascii=False)[:500])
