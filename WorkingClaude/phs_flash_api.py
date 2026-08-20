# -*- coding: utf-8 -*-
"""PHS FlashAPI (flashapi.phs.vn) wrapper — REST cơ sở + phái sinh.

KHÁC `phs_flex_api.py` (`fgateway.phs.vn`): FlashAPI là sản phẩm MỚI, riêng biệt —
đăng nhập bằng chính username/password tài khoản chứng khoán, KHÔNG cần
client_id/client_secret. Một lần login trả cả `access_token` (Bearer) lẫn
`otp_token` (header `x-otp-token` cho mọi lệnh ghi), hiệu lực 28.800s = 8h.
KHÔNG có endpoint refresh được tài liệu hoá ⇒ hết hạn thì LOGIN LẠI.

Cơ sở và phái sinh là HAI phiên đăng nhập khác nhau và HAI TIỂU KHOẢN khác nhau
(PHS support xác nhận 2026-08-20):
  - master `022Cxxxx` → chỉ để login, KHÔNG dùng làm accountId trong path
  - tiểu khoản cơ sở  `0120xxxx`  → path `/accounts/{eqt}/underlying/...`
  - tiểu khoản phái sinh `02120xxxx` → path `/accounts/{fno}/derivative/...`

Dùng:
    from phs_flash_api import PHSFlashClient
    c = PHSFlashClient.from_credentials_file()        # secrets/phs_flash_credentials.json
    c.get_positions(c.eqt_account_id)                 # danh mục cơ sở
    c.get_quote(["ACB", "FPT"])                       # bảng giá (không cần token)
    c.get_buying_power(c.eqt_account_id, "VIC", 222000)
    c.place_order(c.eqt_account_id, {"instrument": "ACB", "qty": 100, "side": "buy",
                                     "type": "LO", "limitPrice": 23000, "timetype": "T"})

ĐÃ PROBE THẬT trên sandbox 2026-08-20 (demo creds công khai 022C099995/123456aA@ —
sandbox KHÔNG validate accountId lẫn Bearer token, trả fixture cho mọi input):
  - `POST /auth/gen-secret-key/{underlying,derivative}` → 200, otp_token NGẪU NHIÊN mỗi lần.
  - `GET  /accounts/{id}/underlying/portfolio|balance|dailyOrder` → 200.
  - `GET  /accounts/{id}/derivative/balance|openPositions|dailyOrder` → 200.
  - `GET  /priceboard/symbol-latest-data?symbolList=ACB,FPT` → 200, KHÔNG cần Bearer.
  - `POST /accounts/{id}/orders/underlying` → 200 `{"orderid": "8000180326000219"}` CỐ ĐỊNH.
  - `GET  /accounts/{id}/underlying/buyingPower` và `/underlying/assets` → **404 trong
    sandbox** (chỉ có ở production per PHS support; sandbox dùng `/underlying/balance`).
    ⇒ `get_buying_power()` chọn path theo `env`, KHÔNG phải fallback im lặng khi 404.

ĐÍNH CHÍNH TÀI LIỆU PHS (đo được, không suy đoán): trang `trading-underlying.md` bảo
sandbox nhận "fixture OTP token" `552066a35eb30a9815afc952b14287a8` — SAI. Gửi đúng
chuỗi đó bị 401 `Invalid x-otp-token (use otp_token from the matching auth response)`;
gửi `otp_token` của chính lần login thì 200. Wrapper này luôn dùng token từ login.

CÒN TREO (chưa build được vì thiếu xác nhận, KHÔNG đoán):
  - Đặt/hủy lệnh PHÁI SINH: body chưa xác nhận ⇒ `place_order`/`cancel_order` với
    asset_type="derivative" chủ động RAISE thay vì đoán field (phase 1 chỉ đọc).
  - Bid/ask LÔ CHẴN: `symbol-latest-data` chỉ có 3 mức LÔ LẺ (`bbOd`/`boOd`); chưa có
    L2 lô chẵn ⇒ wrapper KHÔNG dựng l2_snapshot (xem PHSFlashBroker.get_quote).
  - `refresh_token` trả về nhưng không có endpoint refresh ⇒ re-login mỗi 8h.

secrets/phs_flash_credentials.json (mẫu ở file .sample cùng thư mục):
    {"username": "...", "password": "...", "eqt_account_id": "0120xxxx",
     "fno_account_id": "02120xxxx", "env": "sandbox"}
"""

import json
import os
import time

import requests

BASE_URLS = {
    "sandbox": "https://flashapi.phs.vn/sandbox/oapi",
    "production": "https://flashapi.phs.vn/oapi",
}
WORKDIR = os.path.dirname(os.path.abspath(__file__))
CRED_FILE = os.path.join(WORKDIR, "secrets", "phs_flash_credentials.json")
TOKEN_CACHE = os.path.join(WORKDIR, "data", "phs_flash_token.json")
TOKEN_TTL = 8 * 3600                      # expires_in = 28800 theo login response
TOKEN_MARGIN = 300                        # re-login khi còn dưới 5' (yêu cầu dispatch)
ASSET_TYPES = ("underlying", "derivative")

# Trạng thái lệnh CƠ SỞ — nguồn: hai trang tài liệu PHS trùng khớp nhau
# (`ref-order-status-codes.md` §10.2 và `api-reference/error-status.md`), CỘNG bằng chứng
# sandbox: bản ghi dailyOrder có orstatuscode="8" kèm status="Chờ gửi"/orstatus="Sending
# pending" = "Pending send" ⇒ khớp bảng này.
# ⚠ Bảng mã trong prompt dispatch (0=Mới tạo, 3=Khớp hết, 5=Hủy hết, 8=Chờ cancel…) MÂU
# THUẪN với tài liệu ở gần như mọi mã; không dùng — 3=Cancelled chứ KHÔNG phải "khớp hết",
# map nhầm chiều đó là báo khớp cho một lệnh đã huỷ.
UNDERLYING_ORDER_STATUS = {
    "0": "Rejected by exchange", "1": "Open", "2": "Sent", "3": "Cancelled",
    "4": "Matched", "5": "Expired", "6": "Rejected", "7": "Completed",
    "8": "Pending send", "9": "Pending approval", "10": "Amended", "11": "Sending",
    "12": "Fully matched (filled)", "13": "Pending confirmation", "14": "Processing",
    "15": "Processed", "A": "Amending", "C": "Cancelling", "P": "Pending processing",
    "E": "Expired", "R": "Cancelled", "W": "Pending bank margin deposit",
}


class PHSFlashError(Exception):
    """Lỗi FlashAPI (HTTP >= 400 hoặc body `s` != "ok")."""

    def __init__(self, message, status=None, payload=None):
        super().__init__(message)
        self.status = status
        self.payload = payload


class PHSFlashClient:
    """REST client cho PHS FlashAPI. Token tách riêng theo asset_type (2 lần login)."""

    def __init__(self, username=None, password=None, env="sandbox",
                 eqt_account_id=None, fno_account_id=None,
                 token_cache=TOKEN_CACHE, timeout=30, lang="vi", via="K"):
        if env not in BASE_URLS:
            raise PHSFlashError(f"env không hợp lệ: {env} (chọn {sorted(BASE_URLS)})")
        self.env = env
        self.base_url = BASE_URLS[env]
        self.username = username
        self.password = password
        self.eqt_account_id = eqt_account_id
        self.fno_account_id = fno_account_id
        self.token_cache = token_cache
        self.timeout = timeout
        self.lang = lang
        self.via = via
        self.session = requests.Session()
        # {asset_type: {"access_token","refresh_token","otp_token","expiry"}}
        self._tokens = {a: {} for a in ASSET_TYPES}
        self._load_token_cache()

    # ------------------------------------------------------------------ auth

    @classmethod
    def from_credentials_file(cls, path=None, **kwargs):
        path = path or CRED_FILE
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        for k in ("username", "password", "env", "eqt_account_id", "fno_account_id"):
            v = d.get(k)
            if v not in (None, "") and not str(v).startswith("your_"):
                kwargs.setdefault(k, v)
        if os.path.abspath(path) != os.path.abspath(CRED_FILE):
            stem = os.path.splitext(os.path.basename(path))[0]
            kwargs.setdefault("token_cache",
                              os.path.join(WORKDIR, "data", f"phs_flash_token_{stem}.json"))
        if not kwargs.get("username") or not kwargs.get("password"):
            raise PHSFlashError(f"thiếu username/password trong {path}")
        return cls(**kwargs)

    def login(self, username=None, password=None, asset_type="underlying"):
        """POST /auth/gen-secret-key/{underlying|derivative} → access_token + otp_token.

        KHÔNG có refresh endpoint: hết hạn thì gọi lại chính hàm này (xem
        `_refresh_if_needed`). Trả nguyên payload để caller đọc `expires_in` nếu cần.
        """
        self._check_asset(asset_type)
        user = username or self.username
        pw = password or self.password
        if not user or not pw:
            raise PHSFlashError("thiếu username/password để login")
        self.username, self.password = user, pw
        r = self.session.post(f"{self.base_url}/auth/gen-secret-key/{asset_type}",
                              json={"username": user, "password": pw},
                              timeout=self.timeout)
        data = self._parse(r)
        if not isinstance(data, dict) or not data.get("access_token"):
            raise PHSFlashError(f"login {asset_type} không trả access_token: {data}")
        self._tokens[asset_type] = {
            "access_token": data["access_token"],
            "refresh_token": data.get("refresh_token"),
            "otp_token": data.get("otp_token"),
            "expiry": time.time() + int(data.get("expires_in") or TOKEN_TTL),
        }
        self._save_token_cache()
        return data

    def _refresh_if_needed(self, asset_type="underlying"):
        """Login lại khi chưa có token hoặc token còn dưới TOKEN_MARGIN giây."""
        self._check_asset(asset_type)
        t = self._tokens.get(asset_type) or {}
        if not t.get("access_token") or t.get("expiry", 0) - time.time() < TOKEN_MARGIN:
            self.login(asset_type=asset_type)
        return self._tokens[asset_type]

    def has_token(self, asset_type="underlying"):
        t = self._tokens.get(asset_type) or {}
        return bool(t.get("access_token")) and t.get("expiry", 0) > time.time()

    # ------------------------------------------------------------- cơ sở (đọc)

    def get_positions(self, eqt_account_id=None):
        """GET /accounts/{eqt}/underlying/portfolio → list vị thế cơ sở."""
        acc = self._acc(eqt_account_id, "underlying")
        return self._request("GET", f"/accounts/{acc}/underlying/portfolio")

    def get_buying_power(self, eqt_account_id=None, symbol=None, quote_price=None):
        """Sức mua cơ sở → list, field `ppse` (VND) + `maxqty`/`maxqtty` (số CP).

        Production: `GET /underlying/buyingPower?symbol=&quotePrice=` (PHS support xác
        nhận; symbol + quotePrice BẮT BUỘC vì sức mua phụ thuộc tỷ lệ ký quỹ của mã).
        Sandbox: endpoint đó 404, chỉ có `/underlying/balance` (không nhận tham số) —
        chọn theo `self.env` chứ KHÔNG bắt 404 rồi đổi path, để môi trường nào trả số gì
        là đọc được từ code, không phải đoán từ log.
        """
        acc = self._acc(eqt_account_id, "underlying")
        if self.env == "sandbox":
            return self._request("GET", f"/accounts/{acc}/underlying/balance")
        if not symbol or quote_price is None:
            raise PHSFlashError("production/buyingPower cần symbol + quote_price")
        return self._request("GET", f"/accounts/{acc}/underlying/buyingPower",
                             params={"symbol": symbol, "quotePrice": int(quote_price)})

    def get_daily_orders(self, account_id=None, asset_type="underlying"):
        """GET /accounts/{id}/{underlying|derivative}/dailyOrder → sổ lệnh trong ngày."""
        self._check_asset(asset_type)
        acc = self._acc(account_id, asset_type)
        return self._request("GET", f"/accounts/{acc}/{asset_type}/dailyOrder",
                             asset_type=asset_type)

    # -------------------------------------------------------------- bảng giá

    def get_quote(self, symbol_list):
        """GET /priceboard/symbol-latest-data?symbolList=... → list snapshot.

        Nhận str ("ACB") hoặc list (["ACB","FPT"]). Field: `c` giá khớp mới nhất,
        `re` tham chiếu, `ce` trần, `fl` sàn, `marketId` (STO/STX/UPX), `vo` KL luỹ kế.
        Endpoint này KHÔNG cần Bearer (đo sandbox 2026-08-20). ⚠ Sandbox BỎ QUA
        `symbolList` — luôn trả đúng 1 fixture ACB, kể cả khi hỏi FPT hay mã không tồn
        tại ⇒ khả năng hỏi NHIỀU mã một lần CHƯA verify được, phải đo lại ở production.
        """
        syms = symbol_list if isinstance(symbol_list, str) else ",".join(symbol_list)
        return self._request("GET", "/priceboard/symbol-latest-data",
                             params={"symbolList": syms}, auth=False)

    # ------------------------------------------------------------ cơ sở (ghi)

    def place_order(self, account_id, order_params, asset_type="underlying"):
        """POST /accounts/{id}/orders/{asset_type} → {"orderid": "..."}.

        `order_params` (cơ sở, tất cả BẮT BUỘC theo tài liệu C1):
            instrument, qty, side ("buy"/"sell"), type (LO/ATO/ATC/MP với HOSE;
            LO/MOK/MAK/PLO với HNX+UPCOM), limitPrice, timetype ("T").
        """
        self._check_asset(asset_type)
        if asset_type == "derivative":
            raise PHSFlashError(
                "đặt lệnh phái sinh chưa build — body chưa được xác nhận với PHS "
                "(phase 1 chỉ đọc balance/openPositions). Không đoán field.")
        missing = [k for k in ("instrument", "qty", "side", "type", "limitPrice",
                               "timetype") if order_params.get(k) in (None, "")]
        if missing:
            raise PHSFlashError(f"place_order thiếu tham số bắt buộc: {missing}")
        acc = self._acc(account_id, asset_type)
        return self._request("POST", f"/accounts/{acc}/orders/{asset_type}",
                             body=dict(order_params), asset_type=asset_type, otp=True)

    def cancel_order(self, account_id, order_id, asset_type="underlying",
                     time_type="T", isbuyin="N"):
        """DELETE /accounts/{id}/orders/{asset_type}/{orderId}?timeType=&isbuyin=

        Tài liệu PHS tự mâu thuẫn về tên query (bảng tham số ghi `timetype`, ví dụ cURL
        chạy được ghi `timeType`) — theo ví dụ cURL. Phải verify lại trên production
        trước khi go-live.
        """
        self._check_asset(asset_type)
        if asset_type == "derivative":
            raise PHSFlashError("hủy lệnh phái sinh chưa build — xem place_order()")
        acc = self._acc(account_id, asset_type)
        return self._request("DELETE",
                             f"/accounts/{acc}/orders/{asset_type}/{order_id}",
                             params={"timeType": time_type, "isbuyin": isbuyin},
                             asset_type=asset_type, otp=True)

    # ------------------------------------------------------------- phái sinh

    def get_derivative_balance(self, fno_account_id=None):
        """GET /accounts/{fno}/derivative/balance → dict (pp, nav, cashonhand,
        acccountstatus, requiredmarginamt…). Chú ý: `d` là DICT, không phải list."""
        acc = self._acc(fno_account_id, "derivative")
        return self._request("GET", f"/accounts/{acc}/derivative/balance",
                             asset_type="derivative")

    def get_derivative_positions(self, fno_account_id=None):
        """GET /accounts/{fno}/derivative/openPositions → list vị thế mở."""
        acc = self._acc(fno_account_id, "derivative")
        return self._request("GET", f"/accounts/{acc}/derivative/openPositions",
                             asset_type="derivative")

    # -------------------------------------------------------------- plumbing

    @staticmethod
    def _check_asset(asset_type):
        if asset_type not in ASSET_TYPES:
            raise PHSFlashError(f"asset_type không hợp lệ: {asset_type}")

    def _acc(self, account_id, asset_type):
        """Tiểu khoản theo loại tài sản — cơ sở và phái sinh là HAI số khác nhau, đưa
        nhầm số vào path là gọi API trên tài khoản không tồn tại (fail-closed ở đây)."""
        acc = account_id or (self.eqt_account_id if asset_type == "underlying"
                             else self.fno_account_id)
        if not acc:
            raise PHSFlashError(
                f"thiếu tiểu khoản {'cơ sở (eqt)' if asset_type == 'underlying' else 'phái sinh (fno)'}"
                " — khai trong secrets/phs_flash_credentials.json hoặc truyền account_id")
        return acc

    def _headers(self, asset_type, otp=False, auth=True):
        h = {"x-lang": self.lang, "x-via": self.via}
        if auth:
            h["Authorization"] = "Bearer " + self._tokens[asset_type]["access_token"]
        if otp:
            tok = (self._tokens.get(asset_type) or {}).get("otp_token")
            if not tok:
                raise PHSFlashError("chưa có otp_token — login() trước khi ghi")
            h["x-otp-token"] = tok
        return h

    def _request(self, method, path, params=None, body=None,
                 asset_type="underlying", otp=False, auth=True, _retry=True):
        if auth:
            self._refresh_if_needed(asset_type)
        r = self.session.request(method, self.base_url + path,
                                 headers=self._headers(asset_type, otp=otp, auth=auth),
                                 params=params, json=body, timeout=self.timeout)
        if r.status_code == 401 and auth and _retry:
            # token có thể bị vô hiệu trước hạn (login nơi khác) → login lại đúng 1 lần
            self.login(asset_type=asset_type)
            return self._request(method, path, params=params, body=body,
                                 asset_type=asset_type, otp=otp, auth=auth, _retry=False)
        return self._parse(r)

    @staticmethod
    def _parse(r):
        """Body có 2 dạng: {"s":"ok","d":...} (tài khoản/lệnh) và list thuần (priceboard)."""
        try:
            data = r.json() if r.text else {}
        except ValueError:
            raise PHSFlashError(f"HTTP {r.status_code}: {r.text[:300]}", status=r.status_code)
        if isinstance(data, dict) and data.get("s") not in (None, "ok"):
            raise PHSFlashError(data.get("errmsg") or data.get("message")
                                or f"s={data.get('s')}", status=r.status_code, payload=data)
        if r.status_code >= 400:
            raise PHSFlashError(f"HTTP {r.status_code}: {str(data)[:300]}",
                                status=r.status_code, payload=data)
        if isinstance(data, dict) and data.get("s") == "ok":
            return data.get("d", data)
        return data

    def _save_token_cache(self):
        if not self.token_cache:
            return
        try:
            os.makedirs(os.path.dirname(self.token_cache), exist_ok=True)
            tmp = self.token_cache + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump({"env": self.env, "tokens": self._tokens}, f)
            os.replace(tmp, self.token_cache)      # ghi nguyên tử (coding_guidelines §5)
        except OSError:
            pass

    def _load_token_cache(self):
        if not (self.token_cache and os.path.exists(self.token_cache)):
            return
        try:
            with open(self.token_cache, encoding="utf-8") as f:
                d = json.load(f)
        except (OSError, ValueError):
            return
        # Token của sandbox KHÔNG dùng được cho production (và ngược lại) — cache ghi
        # kèm env chính là để không nạp nhầm.
        if d.get("env") != self.env:
            return
        for a in ASSET_TYPES:
            t = (d.get("tokens") or {}).get(a) or {}
            if t.get("access_token") and t.get("expiry", 0) - time.time() > TOKEN_MARGIN:
                self._tokens[a] = t


def underlying_status_label(row):
    """Nhãn trạng thái lệnh cơ sở từ 1 dòng dailyOrder.

    Ưu tiên bảng mã chính thức (`orstatuscode`/`orstatusvalue`); không tra được thì trả
    chuỗi mô tả tiếng Anh của chính broker (`orstatus`), cuối cùng là `status` (tiếng Việt).
    Mã 4 "Matched" KHÔNG cho biết đã khớp hết hay chưa — chỉ nâng lên "filled" khi
    `remainqtty` == 0 (số ĐO được của broker), không suy từ tên trạng thái.
    """
    if not isinstance(row, dict):
        return ""
    code = row.get("orstatuscode") or row.get("orstatusvalue") or row.get("status_code")
    label = UNDERLYING_ORDER_STATUS.get(str(code).strip()) if code is not None else None
    if label == "Matched":
        remain = row.get("remainqtty")
        try:
            if remain is not None and float(remain) == 0:
                label = "Fully matched (filled)"
            elif remain is not None:
                label = "Matched (partial)"
        except (TypeError, ValueError):
            pass
    return label or row.get("orstatus") or row.get("status") or ""
