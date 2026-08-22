#!/usr/bin/env python3
"""phs_flash_api_selfcheck.py — khoá hồi quy cho adapter PHS FlashAPI (phase 1, CHƯA go-live).

Chạy THẬT trên sandbox `flashapi.phs.vn/sandbox/oapi` với demo credentials CÔNG KHAI trong
tài liệu PHS (022C099995 / 123456aA@) — CẦN MẠNG. Sandbox không đẩy lệnh nào ra sàn; dù vậy
selfcheck này CHỈ ĐỌC, không gọi place_order/cancel_order (đường ghi được kiểm bằng các cổng
fail-closed, không bằng cách bắn lệnh).

Hai nhóm assertion:
  A. Hợp đồng với server sandbox — endpoint còn sống và còn đủ field mình đang map.
  B. Logic của adapter — ánh xạ Quote, nhãn trạng thái, `is_dead`, và các chốt FAIL-CLOSED
     (phái sinh chưa cho đặt lệnh; production không đoán field tiền; thiếu tiểu khoản thì
     dừng chứ không gọi bừa).

Phụ thuộc môi trường (skill verify-before-done): (1) MẠNG tới flashapi.phs.vn — mất mạng là
FAIL chứ không phải PASS im lặng; (2) TZ chỉ ảnh hưởng tên file log thô của broker
(`data/execution_logs/phs_flash_raw_<ngày>.jsonl`) → đã chạy lại dưới `env -u TZ` và
`TZ=UTC`, kết quả không đổi; (3) token cache dùng file TẠM, không đụng data/phs_flash_token.json.

Chạy: python3 phs_flash_api_selfcheck.py
"""
import os
import sys
import tempfile
import time

WC_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WC_ROOT)

from phs_flash_api import (PHSFlashClient, PHSFlashError, UNDERLYING_ORDER_STATUS,
                           underlying_status_label)
from trading_bot.brokers import PHSFlashBroker, PHSFlashOrderUpdate

SANDBOX_USER, SANDBOX_PW = "022C099995", "123456aA@"
SANDBOX_ACC = "022C099995"          # sandbox trả fixture cho mọi accountId
FAILS = []


def check(cond, msg):
    print(("  OK  " if cond else " FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def raises(fn, msg, exc=Exception):
    try:
        fn()
    except exc:
        check(True, msg)
        return
    check(False, msg + " (KHÔNG raise — cổng fail-closed hở)")


tmpdir = tempfile.mkdtemp(prefix="phs_flash_selfcheck_")
cache = os.path.join(tmpdir, "token.json")

print("== A. Sandbox: auth ==")
c = PHSFlashClient(username=SANDBOX_USER, password=SANDBOX_PW, env="sandbox",
                   eqt_account_id=SANDBOX_ACC, fno_account_id=SANDBOX_ACC,
                   token_cache=cache)
r = c.login(asset_type="underlying")
check(bool(r.get("access_token")), "login underlying → access_token")
check(bool(r.get("otp_token")), "login underlying → otp_token (header ghi lệnh)")
check(int(r.get("expires_in") or 0) == 28800, f"expires_in = 28800s/8h (thấy {r.get('expires_in')})")
check(c.has_token("underlying") and not c.has_token("derivative"),
      "token tách riêng theo asset_type (login cơ sở KHÔNG cấp token phái sinh)")

tok1 = c._tokens["underlying"]["access_token"]
c._refresh_if_needed("underlying")
check(c._tokens["underlying"]["access_token"] == tok1,
      "_refresh_if_needed: token còn hạn → KHÔNG login lại")
c._tokens["underlying"]["expiry"] = time.time() + 60          # còn 1' < margin 5'
c._refresh_if_needed("underlying")
check(c._tokens["underlying"]["expiry"] - time.time() > 3600,
      "_refresh_if_needed: còn <5' → tự login lại (token mới hạn 8h)")
check(os.path.exists(cache), "token cache ghi ra file (atomic tmp+replace)")

c2 = PHSFlashClient(username=SANDBOX_USER, password=SANDBOX_PW, env="sandbox",
                    token_cache=cache)
check(c2.has_token("underlying"), "cache cùng env → nạp lại được, không cần login")
c3 = PHSFlashClient(username=SANDBOX_USER, password=SANDBOX_PW, env="production",
                    token_cache=cache)
check(not c3.has_token("underlying"),
      "cache của sandbox KHÔNG nạp vào client production (token không dùng chéo được)")

print("\n== A. Sandbox: đọc tài khoản cơ sở ==")
pos = c.get_positions(SANDBOX_ACC)
check(isinstance(pos, list) and pos, f"portfolio → list không rỗng ({len(pos) if isinstance(pos, list) else 0} dòng)")
p0 = pos[0] if isinstance(pos, list) and pos else {}
for f in ("symbol", "total", "trade", "costPrice", "pnlAmt", "receivingT2"):
    check(f in p0, f"portfolio có field `{f}`")

bp = c.get_buying_power(SANDBOX_ACC)          # sandbox → /underlying/buyingpower
check(isinstance(bp, list) and bp, "buying power (sandbox: underlying/buyingpower) → list")
b0 = bp[0] if isinstance(bp, list) and bp else {}
check("ppse" in b0, "buying power có field `ppse` (sức mua an toàn)")
check("maxqtty" in b0 or "maxqty" in b0, "buying power có field maxqty/maxqtty")

orders = c.get_daily_orders(SANDBOX_ACC)
check(isinstance(orders, list), "dailyOrder cơ sở → list")
o0 = orders[0] if isinstance(orders, list) and orders else {}
for f in ("orderid", "orstatuscode", "execqtty", "remainqtty", "symbol"):
    check(f in o0, f"dailyOrder có field `{f}`")

print("\n== A. Sandbox: bảng giá ==")
q = c.get_quote(["ACB", "FPT"])
# Verify lại 2026-08-22: sandbox nay TÔN TRỌNG symbolList (2 mã hỏi → 2 dòng khác nhau,
# mã trả đúng theo `s`) — trước đó (đo 2026-08-20) luôn trả 1 fixture ACB bất kể hỏi gì.
check(isinstance(q, list) and len(q) == 2,
      f"symbol-latest-data → 2 dòng đúng số mã hỏi (thấy {len(q) if isinstance(q, list) else q})")
row = q[0] if isinstance(q, list) and q else {}
for f in ("s", "c", "re", "ce", "fl", "marketId", "vo"):
    check(f in row, f"quote có field `{f}`")
check(abs((row.get("ce", 0) + row.get("fl", 0)) / 2 - row.get("re", 0)) <= 1,
      "quote nhất quán: (ce+fl)/2 ≈ re (kiểm chéo trực giao, không cùng 1 field)")

print("\n== A. Sandbox: đọc phái sinh (phase 1 chỉ đọc) ==")
c.login(asset_type="derivative")
check(c.has_token("derivative"), "login derivative → token riêng")
db = c.get_derivative_balance(SANDBOX_ACC)
check(isinstance(db, dict), "derivative/balance → DICT (không phải list như bên cơ sở)")
for f in ("pp", "nav", "cashonhand", "acccountstatus"):
    check(f in db, f"derivative balance có field `{f}`")
dp = c.get_derivative_positions(SANDBOX_ACC)
check(isinstance(dp, list), "derivative/openPositions → list")
if dp:
    for f in ("symbol", "qtty", "vwap", "position"):
        check(f in dp[0], f"openPositions có field `{f}`")

print("\n== B. Cổng FAIL-CLOSED của client ==")
raises(lambda: c.place_order(SANDBOX_ACC, {"instrument": "ACB"}, asset_type="derivative"),
       "place_order phái sinh → raise (body chưa xác nhận với PHS, không đoán)", PHSFlashError)
raises(lambda: c.cancel_order(SANDBOX_ACC, "1", asset_type="derivative"),
       "cancel_order phái sinh → raise", PHSFlashError)
raises(lambda: c.place_order(SANDBOX_ACC, {"instrument": "ACB", "qty": 1, "side": "buy"}),
       "place_order thiếu type/limitPrice/timetype → raise trước khi gọi API", PHSFlashError)
no_acc = PHSFlashClient(username="u", password="p", env="sandbox")
raises(no_acc.get_positions,
       "thiếu tiểu khoản cơ sở → raise (không gọi API với accountId rỗng)", PHSFlashError)
raises(lambda: no_acc.get_derivative_balance(),
       "thiếu tiểu khoản phái sinh → raise (eqt và fno là HAI số khác nhau)", PHSFlashError)
raises(lambda: c.get_daily_orders(SANDBOX_ACC, asset_type="futures"),
       "asset_type lạ → raise", PHSFlashError)
prod = PHSFlashClient(username="u", password="p", env="production", eqt_account_id="0120x")
raises(lambda: prod.get_buying_power("0120x"),
       "production get_buying_power thiếu symbol+quotePrice → raise (không đọc bừa endpoint khác)",
       PHSFlashError)
raises(lambda: PHSFlashClient(username="u", password="p", env="uat"),
       "env lạ → raise", PHSFlashError)

print("\n== B. Nhãn trạng thái lệnh cơ sở ==")
check(UNDERLYING_ORDER_STATUS["3"] == "Cancelled" and UNDERLYING_ORDER_STATUS["12"].startswith("Fully"),
      "bảng mã theo TÀI LIỆU PHS (3=Cancelled, 12=Fully matched) — không theo bảng trong prompt dispatch")
check(underlying_status_label({"orstatuscode": "8"}) == "Pending send",
      "code 8 → 'Pending send' (khớp bản ghi sandbox status='Chờ gửi')")
check(underlying_status_label({"orstatuscode": "4", "remainqtty": 0}) == "Fully matched (filled)",
      "code 4 + remainqtty=0 → filled (suy từ SỐ ĐO, không từ tên trạng thái)")
check(underlying_status_label({"orstatuscode": "4", "remainqtty": 50}) == "Matched (partial)",
      "code 4 + remainqtty>0 → partial")
check(underlying_status_label({"orstatus": "Sending pending"}) == "Sending pending",
      "không có mã → rơi về chuỗi mô tả của broker, không bịa")

print("\n== B. is_dead theo MÃ, không theo heuristic chuỗi ==")
mk = lambda code, remain=None: PHSFlashOrderUpdate(
    "1", underlying_status_label({"orstatuscode": code, "remainqtty": remain}),
    0, None, raw={"remainqtty": remain}, code=code)
for code in ("0", "3", "5", "6", "12", "E", "R"):
    check(mk(code).is_dead, f"code {code} ({UNDERLYING_ORDER_STATUS[code]}) → dead")
for code in ("1", "2", "8", "9", "11", "13", "14"):
    check(not mk(code).is_dead, f"code {code} ({UNDERLYING_ORDER_STATUS[code]}) → còn sống")
check(mk("4", 0).is_dead and not mk("4", 100).is_dead,
      "code 4: chết khi remainqtty=0, sống khi còn dư")
check(not mk("ZZ").is_dead, "mã lạ → coi là CÒN SỐNG (fail-safe: kẹt còn hơn phơi nhiễm kép)")
check(PHSFlashOrderUpdate("1", "Pending confirmation", 0, None, raw={}, code="13").is_dead is False,
      "'Pending confirmation' KHÔNG bị coi là chết (bẫy heuristic 'f' của OrderUpdate gốc)")

print("\n== B. PHSFlashBroker (client sandbox tiêm thẳng, không đụng secrets thật) ==")
b = PHSFlashBroker(account_id=SANDBOX_ACC, fno_account_id=SANDBOX_ACC, label="selfcheck")
b.client = c
# Log thô đi vào tmpdir: dữ liệu fixture của sandbox KHÔNG được lẫn vào
# data/execution_logs/ — nơi các script kế toán đọc payload broker THẬT.
b._raw_log = os.path.join(tmpdir, "phs_flash_raw.jsonl")
qt = b.get_quote("ACB")
check(qt is not None and qt.ok(), "broker.get_quote('ACB') → Quote hợp lệ")
check(qt.symbol == "ACB", f"Quote.symbol = ACB (thấy {qt.symbol})")
for name, v in (("last", qt.last), ("ref", qt.ref), ("ceiling", qt.ceiling), ("floor", qt.floor)):
    check(v is not None and v > 0, f"Quote.{name} có giá trị > 0 ({v})")
check(qt.exchange == "HOSE" and qt.exchange_known,
      f"Quote.exchange suy từ marketId=STO → HOSE, exchange_known=True (thấy {qt.exchange}/{qt.exchange_known})")
check(abs(qt.ceiling / qt.ref - 1 - 0.07) < 0.005,
      f"biên độ ceiling/ref−1 ≈ 7% đúng sàn HOSE (thấy {qt.ceiling / qt.ref - 1:.4f})")
check(qt.day_volume and qt.day_volume > 0, f"Quote.day_volume map từ `vo` ({qt.day_volume})")
check(qt.l2_snapshot is None,
      "KHÔNG dựng l2_snapshot từ bbOd/boOd (đó là lô LẺ, dựng L2 từ đó là bịa thanh khoản)")
check(b.get_quote("ACB") is qt, "quote cache 3s: gọi lại trả đúng object cũ")
check(b.get_quote("FPT") is not None and b.get_quote("FPT").symbol == "FPT",
      "hỏi FPT → feed nay trả đúng dòng FPT (sandbox verify lại 2026-08-22: đã tôn trọng "
      "symbolList, không còn fixture ACB cố định)")

# Cổng fail-closed (§B.mismatch) là bất biến CẤU TRÚC, không phải quan sát sandbox hôm nay —
# test bằng row giả mạo mã, không phụ thuộc sandbox có còn trộn mã hay không (§23).
_orig_get_quote = c.get_quote
c.get_quote = lambda symbol_list: [{"s": "ACB", "c": 1000, "re": 1000, "ce": 1070,
                                     "fl": 930, "marketId": "STO", "vo": 1}]
b._quote_cache.clear()
check(b.get_quote("FPT") is None,
      "row trả về mã KHÁC mã đã hỏi → None, KHÔNG gán giá mã khác (fail-closed giả lập)")
c.get_quote = _orig_get_quote
b._quote_cache.clear()

bpos = b.get_positions()
check(isinstance(bpos, dict) and bpos, f"broker.get_positions() → dict ({len(bpos)} mã)")
sym0 = next(iter(bpos))
check(set(("total", "sellable", "receivable")) <= set(bpos[sym0]),
      "vị thế có total/sellable/receivable")
check(bpos[sym0]["total"] > 0 and bpos[sym0]["sellable"] >= 0, "total>0, sellable hợp lệ")
raw0 = [x for x in pos if x.get("symbol") == sym0][0]
check(bpos[sym0]["receivable"] == sum(raw0.get(k, 0) for k in
                                      ("receivingT0", "receivingT1", "receivingT2")),
      "receivable = T0+T1+T2 (không chỉ T2 — CP mua 1-2 phiên trước vẫn là chờ về)")

upd = b.poll_orders()
check(isinstance(upd, dict) and all(isinstance(u, PHSFlashOrderUpdate) for u in upd.values()),
      f"broker.poll_orders() → {{oid: PHSFlashOrderUpdate}} ({len(upd)} lệnh)")
if upd:
    u0 = next(iter(upd.values()))
    check(bool(u0.status) and u0.code is not None,
          f"OrderUpdate mang cả nhãn lẫn mã trạng thái ({u0.status!r}, code={u0.code})")

check(b.get_cash() > 0, "broker.get_cash() (sandbox) = ppse > 0")
check(os.path.exists(b._raw_log) and not os.path.exists(
          os.path.join(WC_ROOT, "data", "execution_logs", "phs_flash_raw_selfcheck.jsonl")),
      "payload thô ghi vào tmpdir, không lẫn vào data/execution_logs/")
bprod = PHSFlashBroker(account_id="0120x", label="selfcheck-prod")
bprod.client = prod
raises(bprod.get_cash,
       "broker.get_cash() ở PRODUCTION → raise (không đoán field tiền của /underlying/assets)",
       RuntimeError)
raises(lambda: b.place_order("ACB", 100, "buy", price=None, order_type="MP"),
       "place_order thiếu price → raise (limitPrice bắt buộc, giá trị cho lệnh thị trường chưa xác nhận)",
       RuntimeError)

print()
if FAILS:
    print(f"SELFCHECK FAILED — {len(FAILS)} assertion(s):")
    for m in FAILS:
        print("  - " + m)
    sys.exit(1)
print(f"SELFCHECK PASSED — all assertions OK ({tmpdir})")
