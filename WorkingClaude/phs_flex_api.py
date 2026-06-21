# -*- coding: utf-8 -*-
"""
PHS Open API FLEX wrapper — REST (trading + inquiry) và Streaming (socket.io v2).

Nguồn đặc tả:
  - "TÀI LIỆU ĐẶC TẢ OPEN API FLEX v0.1" (REST, 13/10/2025)
  - "TÀI LIỆU TÍCH HỢP KÊNH STREAMING OPEN API FLEX" (websocket)

Dùng REST:
    from phs_flex_api import FlexClient

    c = FlexClient()
    c.login("so_tai_khoan", "mat_khau")          # lưu access_token + otp_token
    accounts = c.sub_accounts()                  # danh sách tiểu khoản
    acc = accounts[0]["id"]

    c.cash_balance(acc)                          # số dư tiền
    c.portfolio(acc)                             # chứng khoán hiện có
    c.buying_power(acc, "HPG")                   # sức mua tối đa
    c.instruments(symbols="HPG,VNM")             # bảng giá snapshot

    c.verify_smart_otp(123456)                   # xác thực Smart OTP trước khi đặt lệnh
    r = c.place_order(acc, "HPG", qty=100, side="buy", order_type="LO", price=27500)
    c.modify_order(acc, r["orderId"], qty=200, price=27000)
    c.cancel_order(acc, r["orderId"])

Dùng Streaming (cần socket.io v2 → pin dependency cũ):
    pip install "python-socketio[client]>=4.6,<5" "python-engineio>=3.14,<4"

    from phs_flex_api import FlexStream

    s = FlexStream(access_token=c.access_token)
    s.on_instrument(lambda msg: print("instrument:", msg))
    s.on_trade(lambda msg: print("trade:", msg))
    s.on_account(lambda msg: print("account:", msg))
    s.connect()
    s.subscribe_instrument(["HPG", "VNM"])
    s.subscribe_trade(["HPG"])
    s.subscribe_account([acc])                   # cần access_token
    s.wait()                                     # block; Ctrl+C để dừng
"""

import json
import os
import time
import uuid

import requests

BASE_URL = "https://fgateway.phs.vn"
def _phs_secret(key, default=""):
    """Load a PHS API secret from env var, else gitignored phs_secret.json
    next to this file. Keeps credentials out of source control."""
    v = os.environ.get(key)
    if v:
        return v
    _path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "phs_secret.json")
    try:
        with open(_path, "r", encoding="utf-8") as _f:
            return json.load(_f).get(key, default)
    except Exception:
        return default


CLIENT_ID = _phs_secret("PHS_CLIENT_ID")
CLIENT_SECRET = _phs_secret("PHS_CLIENT_SECRET")
TOKEN_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "data", "phs_flex_token.json")


class FlexError(Exception):
    """Lỗi API FLEX trả về ({"s": "error", "errmsg": ...}) hoặc lỗi HTTP."""

    def __init__(self, message, status=None, payload=None):
        super().__init__(message)
        self.status = status
        self.payload = payload


class FlexClient:
    """REST client cho Open API FLEX (nhóm Trading + Inquiry)."""

    def __init__(self, base_url=BASE_URL, client_id=CLIENT_ID,
                 client_secret=CLIENT_SECRET, lang="vi", via="K",
                 token_cache=TOKEN_CACHE, timeout=30):
        self.base_url = base_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self.lang = lang
        self.via = via
        self.timeout = timeout
        self.token_cache = token_cache

        self.access_token = None
        self.refresh_token = None
        self.otp_token = None
        self.token_expiry = 0          # epoch giây
        self._username = None
        self._password = None

        self.session = requests.Session()
        self._load_token_cache()

    # ------------------------------------------------------------------ auth

    @classmethod
    def from_credentials_file(cls, path=None, auto_login=True, **kwargs):
        """Tạo client từ data/phs_credentials.json.

        File hỗ trợ: username, password, client_id, client_secret (cặp client
        do PHS cấp riêng cho từng khách hàng — bắt buộc để ĐẶT LỆNH; cặp mặc
        định trong tài liệu chỉ dùng được inquiry + market data).
        """
        path = path or os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "data", "phs_credentials.json")
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        for k in ("client_id", "client_secret"):
            v = d.get(k, "")
            if v and "DIEN_" not in v:
                kwargs.setdefault(k, v)
        c = cls(**kwargs)
        user, pw = d.get("username", ""), d.get("password", "")
        if auto_login and user and pw and "DIEN_" not in user and not c.access_token:
            c.login(user, pw)
        elif user and "DIEN_" not in user:
            c._username, c._password = user, pw   # cho phép auto re-login khi 401
        return c

    def login(self, username, password):
        """1.1 Đăng nhập — POST /oeqt/sso/oauth/token (grant_type=password)."""
        self._username, self._password = username, password
        return self._token_request({
            "grant_type": "password",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": username,
            "password": password,
        })

    def refresh(self):
        """Làm mới token bằng refresh_token; hết cách thì login lại."""
        if self.refresh_token:
            try:
                return self._token_request({
                    "grant_type": "refresh_token",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": self.refresh_token,
                })
            except FlexError:
                pass
        if self._username and self._password:
            return self.login(self._username, self._password)
        raise FlexError("Không có refresh_token/credentials để làm mới token — gọi login() trước.")

    def verify_smart_otp(self, otp_value):
        """1.2 Xác thực Smart OTP đặt lệnh — POST /oeqt/verifySmartOtp."""
        return self._request("POST", "/oeqt/verifySmartOtp",
                             body={"otpValue": int(otp_value)})

    def _token_request(self, form):
        r = self.session.post(self.base_url + "/oeqt/sso/oauth/token",
                              data=form, timeout=self.timeout)
        data = self._parse(r)
        self.access_token = data.get("access_token")
        self.refresh_token = data.get("refresh_token", self.refresh_token)
        self.otp_token = data.get("otp_token", self.otp_token)
        self.token_expiry = time.time() + int(data.get("expires_in", 28800)) - 60
        self._save_token_cache()
        return data

    # --------------------------------------------------------------- trading

    def place_order(self, account_id, symbol, qty, side, order_type="LO",
                    price=None, time_type="T", request_id=None, **extra):
        """1.3 Đặt lệnh — POST /oeqt/accounts/{accountId}/orders.

        side: "buy"/"sell" · order_type: "LO","ATO","ATC",… · time_type: "T"/"G"
        price → limitPrice. extra: stopPrice, durationType, durationDateTime,
        stopLoss, takeProfit, digitalSignature, splitval, effdate, expdate.
        Trả về {"orderId": ...}.
        """
        body = {"instrument": symbol, "qty": qty, "side": side,
                "type": order_type, "timetype": time_type}
        if price is not None:
            body["limitPrice"] = price
        body.update({k: v for k, v in extra.items() if v is not None})
        return self._request("POST", f"/oeqt/accounts/{account_id}/orders",
                             params={"requestId": request_id or uuid.uuid4().hex},
                             body=body, otp=True)

    def modify_order(self, account_id, order_id, qty, price=None,
                     request_id=None, **extra):
        """1.4 Sửa lệnh — PUT /oeqt/accounts/{accountId}/orders/{orderId}.

        extra: stopPrice, durationType, durationDateTime, stopLoss,
        takeProfit, digitalSignature, isbuyin.
        """
        body = {"qty": qty}
        if price is not None:
            body["limitPrice"] = price
        body.update({k: v for k, v in extra.items() if v is not None})
        return self._request("PUT", f"/oeqt/accounts/{account_id}/orders/{order_id}",
                             params={"requestId": request_id or uuid.uuid4().hex},
                             body=body, otp=True)

    def cancel_order(self, account_id, order_id, time_type="T", isbuyin="N",
                     request_id=None):
        """1.5 Huỷ lệnh — DELETE /oeqt/accounts/{accountId}/orders/{orderId}."""
        return self._request("DELETE", f"/oeqt/accounts/{account_id}/orders/{order_id}",
                             params={"requestId": request_id or uuid.uuid4().hex,
                                     "timeType": time_type, "isbuyin": isbuyin},
                             otp=True)

    # --------------------------------------------------------------- inquiry

    def daily_orders(self, account_id):
        """1.6 Sổ lệnh trong ngày."""
        return self._request("GET", f"/oeqt/inq/accounts/{account_id}/dailyOrder")

    def portfolio(self, account_id):
        """1.7 Chứng khoán hiện có."""
        return self._request("GET", f"/oeqt/inq/accounts/{account_id}/securitiesPortfolio")

    def buying_power(self, account_id, symbol, price=None):
        """1.8 Sức mua tối đa (theo mã, tuỳ chọn theo giá)."""
        params = {"symbol": symbol}
        if price is not None:
            params["quotePrice"] = price
        return self._request("GET", f"/oeqt/inq/accounts/{account_id}/availableTrade",
                             params=params)

    def instruments(self, symbols=None, brief=None, exchange=None):
        """1.9 Danh sách mã CK + bảng giá snapshot — /oeqt/datafeed/instrument.

        symbols: "HPG,VNM" hoặc list. brief=True chỉ lấy gọn.
        """
        if isinstance(symbols, (list, tuple)):
            symbols = ",".join(symbols)
        params = {}
        if symbols:
            params["symbols"] = symbols
        if brief is not None:
            params["brief"] = "true" if brief else "false"
        if exchange:
            params["exchange"] = exchange
        return self._request("GET", "/oeqt/datafeed/instrument", params=params)

    def cash_balance(self, account_id):
        """2.1 Thông tin số dư tiền."""
        return self._request("GET", f"/oeqt/inq/accounts/{account_id}/ciaccount")

    def account_summary(self, account_id):
        """2.2 Tổng hợp tài khoản."""
        return self._request("GET", f"/oeqt/inq/accounts/{account_id}/subAccountSummary")

    def order_history(self, account_id, from_date, to_date, symbol="ALL",
                      exec_type="ALL", status="ALL"):
        """2.3 Lịch sử đặt lệnh. Ngày dạng DD/MM/YYYY. exec_type: ALL/NB/NS."""
        return self._request("GET", f"/oeqt/inq/accounts/{account_id}/orderReport",
                             params={"fromDate": from_date, "toDate": to_date,
                                     "symbol": symbol, "execType": exec_type,
                                     "status": status})

    def sub_accounts(self):
        """2.4 Lấy thông tin các tiểu khoản — GET /oeqt/accounts."""
        return self._request("GET", "/oeqt/accounts")

    # -------------------------------------------------------------- plumbing

    def _headers(self, otp=False):
        h = {"x-lang": self.lang, "x-via": self.via}
        if self.access_token:
            h["Authorization"] = "Bearer " + self.access_token
        if otp:
            if not self.otp_token:
                raise FlexError("Chưa có otp_token — login() rồi verify_smart_otp() trước khi đặt/sửa/hủy lệnh.")
            h["x-otp-token"] = self.otp_token
        return h

    def _request(self, method, path, params=None, body=None, otp=False, _retry=True):
        if self.access_token and time.time() > self.token_expiry:
            try:
                self.refresh()
            except FlexError:
                pass
        r = self.session.request(method, self.base_url + path,
                                 headers=self._headers(otp=otp), params=params,
                                 json=body, timeout=self.timeout)
        if r.status_code == 401 and _retry and (self.refresh_token or self._password):
            self.refresh()
            return self._request(method, path, params=params, body=body,
                                 otp=otp, _retry=False)
        return self._parse(r)

    @staticmethod
    def _parse(r):
        try:
            data = r.json()
        except ValueError:
            raise FlexError(f"HTTP {r.status_code}: {r.text[:300]}", status=r.status_code)
        if isinstance(data, dict) and data.get("s") not in (None, "ok") :
            # server trả lỗi với s="error" hoặc s="500"… kèm errmsg
            raise FlexError(data.get("errmsg", f"s={data.get('s')}"),
                            status=r.status_code, payload=data)
        if r.status_code >= 400:
            raise FlexError(f"HTTP {r.status_code}: {data}", status=r.status_code,
                            payload=data)
        if isinstance(data, dict) and data.get("s") == "ok":
            return data.get("d", data)
        return data

    def _save_token_cache(self):
        if not self.token_cache:
            return
        try:
            os.makedirs(os.path.dirname(self.token_cache), exist_ok=True)
            with open(self.token_cache, "w", encoding="utf-8") as f:
                json.dump({"access_token": self.access_token,
                           "refresh_token": self.refresh_token,
                           "otp_token": self.otp_token,
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
                self.access_token = d.get("access_token")
                self.refresh_token = d.get("refresh_token")
                self.otp_token = d.get("otp_token")
                self.token_expiry = d["token_expiry"]
        except (OSError, ValueError, KeyError):
            pass


class FlexStream:
    """Streaming client (socket.io v2, sails.io) — room instrument/trade/account.

    Server chạy socket.io v2 nên BẮT BUỘC dùng python-socketio 4.x:
        pip install "python-socketio[client]>=4.6,<5" "python-engineio>=3.14,<4"
    """

    SIO_PATH = "/seqt/realtime/socket.io"

    def __init__(self, base_url=BASE_URL, client_id=CLIENT_ID,
                 client_secret=CLIENT_SECRET, access_token=None):
        import socketio  # import trễ để REST dùng được mà không cần socketio
        self.base_url = base_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self._subs = []          # nhớ các subscription để resubscribe khi reconnect
        self.sio = socketio.Client(reconnection=True, reconnection_delay=2)
        self.sio.on("connect", self._on_connect)
        self.sio.on("disconnect", lambda: print("[FlexStream] disconnected"))

    # đăng ký callback: hàm nhận 1 tham số msg (dict theo cấu trúc table/action/data)
    def on_instrument(self, callback):
        self.sio.on("instrument", callback)

    def on_trade(self, callback):
        self.sio.on("trade", callback)

    def on_account(self, callback):
        self.sio.on("account", callback)

    def connect(self):
        query = ("__sails_io_sdk_version=1.2.1"
                 "&__sails_io_sdk_platform=browser"
                 "&__sails_io_sdk_language=javascript"
                 f"&clientid={self.client_id}"
                 f"&clientsecret={self.client_secret}")
        self.sio.connect(f"{self.base_url}?{query}",
                         socketio_path=self.SIO_PATH,
                         transports=["websocket"])

    def _on_connect(self):
        print("[FlexStream] connected, sid =", self.sio.sid)
        for args, token in self._subs:   # resubscribe sau reconnect
            self._send(args, "subscribe", token)

    def subscribe_instrument(self, symbols):
        self._subscribe([f"instrument:{s}" for s in self._aslist(symbols)])

    def subscribe_trade(self, symbols):
        self._subscribe([f"trade:{s}" for s in self._aslist(symbols)])

    def subscribe_account(self, sub_accounts):
        if not self.access_token:
            raise FlexError("Room account cần access_token (lấy từ FlexClient.login).")
        self._subscribe([f"account:{a}" for a in self._aslist(sub_accounts)],
                        token=self.access_token)

    def unsubscribe_instrument(self, symbols):
        self._unsubscribe([f"instrument:{s}" for s in self._aslist(symbols)])

    def unsubscribe_trade(self, symbols):
        self._unsubscribe([f"trade:{s}" for s in self._aslist(symbols)])

    def unsubscribe_account(self, sub_accounts):
        self._unsubscribe([f"account:{a}" for a in self._aslist(sub_accounts)],
                          token=self.access_token)

    def wait(self):
        self.sio.wait()

    def disconnect(self):
        self.sio.disconnect()

    def _subscribe(self, args, token=None):
        self._subs.append((args, token))
        if self.sio.connected:
            self._send(args, "subscribe", token)

    def _unsubscribe(self, args, token=None):
        self._subs = [(a, t) for a, t in self._subs if a != args]
        if self.sio.connected:
            self._send(args, "unsubscribe", token)

    def _send(self, args, op, token=None):
        data = {"args": args, "op": op}
        if token:
            data["token"] = token
        self.sio.emit("get", {"data": data, "method": "get", "url": "/client/send"})

    @staticmethod
    def _aslist(x):
        return [x] if isinstance(x, str) else list(x)


if __name__ == "__main__":
    # Demo read-only: bảng giá snapshot (không cần đăng nhập nếu server cho phép),
    # sau đó nếu có credentials trong env thì login và liệt kê tiểu khoản.
    import argparse

    ap = argparse.ArgumentParser(description="PHS FLEX wrapper demo")
    ap.add_argument("--symbols", default="HPG,VNM", help="mã CK, phân cách dấu phẩy")
    ap.add_argument("--stream", action="store_true", help="stream realtime thay vì snapshot")
    args = ap.parse_args()

    client = FlexClient()
    user = os.environ.get("PHS_USERNAME")
    pw = os.environ.get("PHS_PASSWORD")
    if user and pw and not client.access_token:
        client.login(user, pw)
        print("Đăng nhập OK, tiểu khoản:",
              [a.get("id") for a in client.sub_accounts()])

    if args.stream:
        stream = FlexStream(access_token=client.access_token)
        stream.on_instrument(lambda m: print("instrument:", json.dumps(m, ensure_ascii=False)[:400]))
        stream.on_trade(lambda m: print("trade:", json.dumps(m, ensure_ascii=False)[:400]))
        stream.connect()
        stream.subscribe_instrument(args.symbols.split(","))
        stream.subscribe_trade(args.symbols.split(","))
        try:
            stream.wait()
        except KeyboardInterrupt:
            stream.disconnect()
    else:
        rows = client.instruments(symbols=args.symbols)
        print(json.dumps(rows, ensure_ascii=False, indent=2)[:3000])
