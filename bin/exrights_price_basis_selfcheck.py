#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regression self-check cho GIÁ THAM CHIẾU ĐÚNG PHIÊN (`verify_account_snapshot.dnse_close_prices`).

SỰ CỐ (2026-08-11, job Taylor_20260810_183618)
----------------------------------------------
`close_price` boardId=G1 trả giá đóng cửa của PHIÊN GẦN NHẤT ĐÃ XONG. Chạy hàm này TRƯỚC khi
phiên hôm nay đóng (tiền phiên 01:30, hay giữa phiên 10:00) ⇒ giá thuộc phiên TRƯỚC. Với một mã
đang GIAO DỊCH KHÔNG HƯỞNG QUYỀN hôm nay, giá phiên trước là giá CHƯA điều chỉnh trong khi
`openQuantity` của broker thì ĐÃ điều chỉnh ⇒ nhân giá cũ với số lượng mới = thổi phồng NAV.

Ca thật MBB 2026-08-11 (cổ tức CP 15% + quyền mua 10:1 giá 10.000đ): G1 close 24.250 (phiên
08-10) vs giá tham chiếu sàn hôm nay 20.200 ⇒ SpaceX +5.013.250đ (~0,5% NAV). User bắt được
bằng ẢNH CHỤP APP DNSE, không phải bằng cảnh báo của hệ thống.

BẢN VÁ: giá G1 không thuộc phiên HÔM NAY ⇒ lấy `secdef.basicPrice` — giá tham chiếu CHÍNH THỨC
của sàn cho phiên hiện tại, đã gồm mọi điều chỉnh corp action. Tổng quát: không cần biết mã nào
có sự kiện gì, chỉ cần biết "giá đang cầm thuộc phiên nào".

Chạy: python3 mike/bin/exrights_price_basis_selfcheck.py     (exit 0 = pass)
KHÔNG chạm mạng/BQ/DNSE/bus — client là fake, mọi số liệu đóng băng trong file này.
"""
import importlib.util
import io
import json
import os
import subprocess
import sys
import types

MIKE_BIN = os.path.dirname(os.path.abspath(__file__))
WC_ROOT = os.path.dirname(os.path.dirname(MIKE_BIN))

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'✓' if cond else '✗'} {name}" + (f"  — {detail}" if detail else ""))


# ── Fixture đóng băng từ bản đọc THẬT sáng 2026-08-11 01:36 ICT (§23: đóng băng, không đọc live)
TODAY = "2026-08-11"
PREV = "2026-08-10"

# (close G1 nghìn đồng, ngày của close đó, basicPrice nghìn đồng)
REAL = {
    # mã đang GDKHQ: close phiên trước CHƯA điều chỉnh, basicPrice ĐÃ điều chỉnh
    "MBB": (24.25, PREV, 20.2),
    # HNX/UPCOM: giá tham chiếu ≠ giá đóng cửa phiên trước kể cả khi KHÔNG có corp action
    "SCL": (23.3, PREV, 23.4),
    "TV1": (19.8, PREV, 19.7),
    # ngày thường: hai nguồn trùng khít ⇒ bản vá phải là no-op
    "ACB": (22.65, PREV, 22.65),
    "VCB": (60.3, PREV, 60.3),
}


class FakeClient:
    """Bắt chước DNSE client. `secdef_calls` để chứng minh nhánh mới KHÔNG chạy khi không cần."""

    def __init__(self, table, close_day=None, secdef_raises=False, secdef_empty=False):
        self.table, self.close_day = table, close_day
        self.secdef_raises, self.secdef_empty = secdef_raises, secdef_empty
        self.secdef_calls = []

    def close_price(self, tk):
        if tk not in self.table:
            raise KeyError(tk)
        px, day, _ = self.table[tk]
        return {"prices": [
            {"boardId": "G7", "symbol": tk, "closePrice": 0, "time": f"{day} 09:00:00.122"},
            {"boardId": "G1", "symbol": tk, "closePrice": px,
             "time": f"{self.close_day or day} 14:45:03.261"},
        ]}

    def secdef(self, tk):
        self.secdef_calls.append(tk)
        if self.secdef_raises:
            raise RuntimeError("network down")
        if self.secdef_empty or tk not in self.table:
            return []
        bp = self.table[tk][2]
        return [{"boardId": b, "symbol": tk, "basicPrice": bp} for b in ("T3", "G1", "G4")]


def load_vas(client):
    """Nạp verify_account_snapshot với `get_dnse_client` đã bị thay bằng fake — hàm import
    trong THÂN hàm nên phải chèn module giả vào sys.modules TRƯỚC khi gọi."""
    fake_brokers = types.ModuleType("trading_bot.brokers")
    fake_brokers.get_dnse_client = lambda: client
    fake_tb = sys.modules.get("trading_bot") or types.ModuleType("trading_bot")
    sys.modules["trading_bot"] = fake_tb
    sys.modules["trading_bot.brokers"] = fake_brokers
    spec = importlib.util.spec_from_file_location(
        "_sc_vas", os.path.join(MIKE_BIN, "verify_account_snapshot.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_sc_vas"] = mod
    spec.loader.exec_module(mod)
    return mod


def call(client, tickers, **kw):
    """Gọi hàm thật, nuốt stderr để trả về cả cảnh báo cho test kiểm nội dung."""
    vas = load_vas(client)
    err, sys.stderr = sys.stderr, io.StringIO()
    try:
        out = vas.dnse_close_prices(tickers, **kw)
        warn = sys.stderr.getvalue()
    finally:
        sys.stderr = err
    return out, warn


# ══════════════════════════════════════════════════════════════════════════════════════════
print("[1] G1 close ĐÃ thuộc phiên HÔM NAY ⇒ dùng nguyên giá ATC, KHÔNG đụng secdef")
# Đây là đường chạy chính EOD 17:30 / báo cáo 15:00 — bản vá TUYỆT ĐỐI không được đổi hành vi
# ở đây, nếu không là làm hỏng đúng cái fix 2026-07-06 đã dựng.
c = FakeClient(REAL, close_day=TODAY)
px, warn = call(c, ["MBB", "ACB"], with_source=True)
prices, src = px
check("MBB giữ giá đóng cửa hôm nay 24.250 (KHÔNG bị thay bằng 20.200)",
      prices["MBB"] == 24250.0, prices["MBB"])
check("nguồn khai 'dnse_g1_today'", set(src.values()) == {"dnse_g1_today"}, src)
check("secdef KHÔNG hề được gọi (không tốn round-trip trên đường chạy chính)",
      c.secdef_calls == [], c.secdef_calls)
check("không in cảnh báo thay giá", "secdef" not in warn, warn[:80])

print("\n[2] G1 close thuộc phiên TRƯỚC + mã đang GDKHQ ⇒ lấy secdef.basicPrice (CA THẬT MBB)")
c = FakeClient(REAL)
(prices, src), warn = call(c, ["MBB"], with_source=True)
check("MBB 24.250 → 20.200 (giá tham chiếu sàn cho phiên ex)", prices["MBB"] == 20200.0,
      prices["MBB"])
check("nguồn khai 'dnse_secdef_basic' — provenance KHÔNG nói dối",
      src["MBB"] == "dnse_secdef_basic", src)
check("có cảnh báo nêu rõ mã + cả hai giá + phiên của giá cũ",
      "MBB" in warn and "24,250" in warn and "20,200" in warn and PREV in warn, warn[:160])
check("số học khớp công thức điều chỉnh HOSE gộp cổ tức CP 15% + quyền mua 10:1 @10.000đ",
      abs((24250 + 10000 * 0.10) / (1 + 0.15 + 0.10) - 20200.0) < 1e-9)

print("\n[3] TỔNG QUÁT, không chỉ ex-date: UPCOM/HNX có giá tham chiếu ≠ giá đóng cửa")
c = FakeClient(REAL)
(prices, src), _ = call(c, ["SCL", "TV1"], with_source=True)
check("TV1 19.800 → 19.700 (UPCOM tham chiếu = giá BÌNH QUÂN phiên trước)",
      prices["TV1"] == 19700.0, prices["TV1"])
check("SCL 23.300 → 23.400", prices["SCL"] == 23400.0, prices["SCL"])
check("cả hai khai đúng nguồn secdef",
      src == {"SCL": "dnse_secdef_basic", "TV1": "dnse_secdef_basic"}, src)

print("\n[4] Ngày thường (hai nguồn trùng) ⇒ giá không đổi, KHÔNG spam cảnh báo")
c = FakeClient(REAL)
(prices, _), warn = call(c, ["ACB", "VCB"], with_source=True)
check("ACB/VCB giữ nguyên giá", prices == {"ACB": 22650.0, "VCB": 60300.0}, prices)
check("KHÔNG in cảnh báo khi hai nguồn bằng nhau (cảnh báo phải hiếm mới có nghĩa)",
      "secdef" not in warn, warn[:80])

print("\n[5] FAIL-SAFE: secdef lỗi/rỗng ⇒ GIỮ giá G1 cũ, không crash, không trả rỗng")
for label, kw in (("secdef ném exception", {"secdef_raises": True}),
                  ("secdef trả rỗng", {"secdef_empty": True})):
    c = FakeClient(REAL, **kw)
    (prices, src), _ = call(c, ["MBB"], with_source=True)
    check(f"{label} ⇒ MBB vẫn có giá (24.250, hành vi CŨ) chứ không biến mất",
          prices.get("MBB") == 24250.0, prices)
    check(f"  …và nguồn khai đúng là 'dnse_g1_today' (không khai khống secdef)",
          src.get("MBB") == "dnse_g1_today", src)

print("\n[6] Tương thích ngược: with_source=False trả dict phẳng như chữ ký cũ")
# daily_nav_snapshot.py và verify_account_snapshot.main() gọi KHÔNG kèm kwarg — đổi kiểu trả về
# ở đó sẽ hỏng lặng lẽ (dict → tuple thì `prices.get(t)` ném AttributeError giữa đường EOD).
c = FakeClient(REAL)
out, _ = call(c, ["MBB", "ACB"])
check("trả về dict (không phải tuple)", isinstance(out, dict), type(out).__name__)
check("giá vẫn là giá ĐÃ VÁ", out == {"MBB": 20200.0, "ACB": 22650.0}, out)

print("\n[7] Mã lỗi API bị BỎ QUA, không kéo sập cả rổ")
c = FakeClient(REAL)
(prices, _), _ = call(c, ["MBB", "KHONGCO"], with_source=True)
check("mã không tồn tại vắng khỏi kết quả, mã còn lại vẫn đúng",
      prices == {"MBB": 20200.0}, prices)

print("\n[8] `time` thiếu/méo ⇒ fail-safe về hành vi CŨ (không đoán sang nhánh mới)")


class NoTimeClient(FakeClient):
    def close_price(self, tk):
        return {"prices": [{"boardId": "G1", "symbol": tk, "closePrice": self.table[tk][0]}]}


c = NoTimeClient(REAL)
(prices, src), _ = call(c, ["MBB"], with_source=True)
check("thiếu field `time` ⇒ giữ giá G1, KHÔNG gọi secdef",
      prices["MBB"] == 24250.0 and c.secdef_calls == [], (prices, c.secdef_calls))

print("\n[9] CA CHỨNG MINH NGƯỢC — bỏ bản vá thì cổng 5% của daily_nav_snapshot CHẶN NAV hôm nay")
# daily_nav_snapshot.py từ chối tính NAV khi |close_price − positions.marketPrice| > 5%
# (PRICE_XCHECK_TOLERANCE_PCT, dựng sau ca VHM 2026-08-05). marketPrice THẬT của MBB sáng
# 08-11 = 20.200 ở CẢ HAI account. Không có bản vá ⇒ lệch 16,7% ⇒ NAV hôm nay bị CHẶN.
MARKET_PRICE_MBB = 20200.0                     # đọc thật từ dnse_raw_2026-08-11.jsonl, 2 account
TOL = 5.0
old_diff = abs(24250.0 - MARKET_PRICE_MBB) / MARKET_PRICE_MBB * 100
new_diff = abs(20200.0 - MARKET_PRICE_MBB) / MARKET_PRICE_MBB * 100
check(f"KHÔNG vá: lệch {old_diff:.1f}% > {TOL}% ⇒ cổng chặn (bug có thật, không phải giả định)",
      old_diff > TOL, f"{old_diff:.2f}%")
check(f"CÓ vá: lệch {new_diff:.1f}% ⇒ cổng thông, NAV tính được", new_diff <= TOL,
      f"{new_diff:.2f}%")
src_txt = open(os.path.join(MIKE_BIN, "daily_nav_snapshot.py"), encoding="utf-8").read()
check("cổng 5% vẫn còn nguyên trong daily_nav_snapshot.py (bản vá KHÔNG gỡ lưới an toàn)",
      "PRICE_XCHECK_TOLERANCE_PCT = 5.0" in src_txt)

print("\n[10] §16 — neo TZ tường minh: kết quả KHÔNG đổi theo TZ của tiến trình gọi")
# Ngày 'hôm nay' quyết định nhánh nào chạy. Máy đặt TZ=America/New_York lúc 01:30 ICT vẫn đang
# là 'hôm qua' theo giờ Mỹ ⇒ nếu hàm dùng date.today() trần thì nhánh chọn sai.
probe = r'''
import io, os, sys, types, importlib.util
sys.path.insert(0, %r)
import datetime as dt
from zoneinfo import ZoneInfo
fake_brokers = types.ModuleType("trading_bot.brokers")
class C:
    def close_price(self, tk):
        # close luôn là 'hôm qua theo giờ ICT' bất kể TZ tiến trình
        d = (dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date() - dt.timedelta(days=1)).isoformat()
        return {"prices": [{"boardId": "G1", "symbol": tk, "closePrice": 24.25,
                            "time": d + " 14:45:03.261"}]}
    def secdef(self, tk):
        return [{"boardId": "G1", "symbol": tk, "basicPrice": 20.2}]
fake_brokers.get_dnse_client = lambda: C()
sys.modules["trading_bot"] = types.ModuleType("trading_bot")
sys.modules["trading_bot.brokers"] = fake_brokers
spec = importlib.util.spec_from_file_location("_p", %r)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
sys.stderr = io.StringIO()
print(m.dnse_close_prices(["MBB"])["MBB"])
''' % (WC_ROOT, os.path.join(MIKE_BIN, "verify_account_snapshot.py"))

results = {}
for label, env in (("TZ=Asia/Ho_Chi_Minh", {"TZ": "Asia/Ho_Chi_Minh"}),
                   ("env -u TZ", None),
                   ("TZ=America/New_York", {"TZ": "America/New_York"}),
                   ("TZ=UTC", {"TZ": "UTC"})):
    e = dict(os.environ)
    e.pop("TZ", None)
    if env:
        e.update(env)
    r = subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True, env=e)
    results[label] = (r.stdout.strip().splitlines() or [""])[-1]
    check(f"{label} ⇒ 20200.0", results[label] == "20200.0", results[label] or r.stderr[-160:])
check("mọi môi trường TZ cho KẾT QUẢ ĐỒNG NHẤT", len(set(results.values())) == 1, results)

print(f"\n{'=' * 74}\nKẾT QUẢ: {len(PASS)} PASS / {len(FAIL)} FAIL")
if FAIL:
    print("FAIL:")
    for f in FAIL:
        print("  ·", f)
sys.exit(1 if FAIL else 0)
