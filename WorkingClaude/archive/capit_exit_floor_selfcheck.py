#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Self-check cho CAPIT exit floor guard (job Taylor_20260821_123019).

Bug đã sửa: khi paper-row CAPIT đóng ở phiên 60, target về 0 → diff step trong
`trading_bot.strategies.V23Strategy.build_plan` sinh lệnh bán TOÀN BỘ vị thế broker của mã đó
(kể cả phần custom30V parking cùng mã, vd PVT/SIP) — không chỉ phần CAPIT. Fix: floor sell qty
bằng `_capit_qty_per_ticker()` (đọc capit_episode.qty_per_account của episode ĐANG MỞ) +
`_capit_floor_diff()` (pure, áp trong diff step).

Test trực tiếp 2 hàm pure/fail-safe này — không cần dựng toàn bộ build_plan (paper book, recs,
broker network) vì guard là 1 khối logic tách biệt, độc lập với phần còn lại của build_plan.

Run: python3 capit_exit_floor_selfcheck.py   (exit 0 = PASS hết, khác 0 = có FAIL)
"""
import sys

from trading_bot.strategies import _capit_floor_diff, _capit_qty_per_ticker
import capit_episode as ce

PASS, FAIL = [], []


def ok(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f" — {detail}" if detail and not cond else ""))


# ============================================================================================
print("1. Episode CHƯA đóng (sessions<60 → paper-row vẫn còn) — không tới guard, diff bình thường")
# _capit_floor_diff chỉ nhận diff đã tính; "chưa tới guard" tương đương build_plan gọi hàm với
# capit_qty=None (mã không có trong dict trả về, vd basket rỗng vì episode paper-row chưa đóng
# hoặc mã không nằm trong episode qty_per_account).
diff, note = _capit_floor_diff(diff=-1000, tgt=0, have=1000, capit_qty=None)
ok("1a diff không đổi khi capit_qty=None", diff == -1000, f"got diff={diff}")
ok("1b không trả non_capit_have khi guard không áp", note is None, f"got={note}")

# ============================================================================================
print("2. PVT overlap (700 CAPIT + 300 parking), target=0, have=1000 → chỉ bán 700")
diff, non_capit_have = _capit_floor_diff(diff=(0 - 1000), tgt=0, have=1000, capit_qty=700)
ok("2a SELL qty đúng = 700 (không đụng 300 parking)", diff == -700, f"got diff={diff}")
ok("2b non_capit_have=300 đúng phần giữ lại", non_capit_have == 300, f"got={non_capit_have}")

# ============================================================================================
print("3. NCT không overlap (toàn bộ 500cp là CAPIT), target=0, have=500 → bán toàn bộ 500")
diff, non_capit_have = _capit_floor_diff(diff=(0 - 500), tgt=0, have=500, capit_qty=500)
ok("3a SELL qty = 500 (bán hết, không còn phần parking)", diff == -500, f"got diff={diff}")
ok("3b non_capit_have=0", non_capit_have == 0, f"got={non_capit_have}")

# ============================================================================================
print("4. Không có episode CAPIT đang mở → _capit_qty_per_ticker trả {} → guard không kích hoạt")


class _NoOpenEpisode:
    @staticmethod
    def _load(path):
        return {"episodes": []}

    @staticmethod
    def _open_episode(ledger):
        return None

    LEDGER_PATH = ce.LEDGER_PATH


import trading_bot.strategies as strat
_orig_import = __import__


def _fake_import_no_episode(name, *a, **kw):
    if name == "capit_episode":
        return _NoOpenEpisode
    return _orig_import(name, *a, **kw)


import builtins
builtins.__import__ = _fake_import_no_episode
try:
    qmap = _capit_qty_per_ticker("SpaceX")
finally:
    builtins.__import__ = _orig_import
ok("4a _capit_qty_per_ticker() = {} khi không có episode mở", qmap == {}, f"got={qmap}")
diff, note = _capit_floor_diff(diff=(0 - 500), tgt=0, have=500, capit_qty=qmap.get("PVT"))
ok("4b diff không đổi khi guard không áp (qty=None → =all)", diff == -500, f"got diff={diff}")

# ============================================================================================
print("5. Episode mở nhưng qty_per_account thiếu account/ticker này → fail-safe, không crash")


class _OpenEpisodeMissingQty:
    @staticmethod
    def _load(path):
        return {"episodes": [{"status": "open", "qty_per_account": {}}]}

    @staticmethod
    def _open_episode(ledger):
        return ledger["episodes"][0]

    LEDGER_PATH = ce.LEDGER_PATH


def _fake_import_missing_qty(name, *a, **kw):
    if name == "capit_episode":
        return _OpenEpisodeMissingQty
    return _orig_import(name, *a, **kw)


builtins.__import__ = _fake_import_missing_qty
try:
    qmap = _capit_qty_per_ticker("SpaceX")
finally:
    builtins.__import__ = _orig_import
ok("5a không crash, trả {} khi qty_per_account rỗng/thiếu account", qmap == {}, f"got={qmap}")
diff, note = _capit_floor_diff(diff=(0 - 500), tgt=0, have=500, capit_qty=qmap.get("PVT"))
ok("5b diff = như cũ (bán toàn bộ) khi fail-safe", diff == -500, f"got diff={diff}")

# 5c: import capit_episode thật lỗi (module raise) → vẫn {} không crash
def _fake_import_raises(name, *a, **kw):
    if name == "capit_episode":
        raise RuntimeError("simulated import failure")
    return _orig_import(name, *a, **kw)


builtins.__import__ = _fake_import_raises
try:
    qmap = _capit_qty_per_ticker("SpaceX")
finally:
    builtins.__import__ = _orig_import
ok("5c import lỗi → {} fail-safe, không raise", qmap == {}, f"got={qmap}")

# ============================================================================================
print("6. BUY không bị guard đụng (diff>0 giữ nguyên dù có capit_qty)")
diff, note = _capit_floor_diff(diff=200, tgt=1200, have=1000, capit_qty=700)
ok("6a diff BUY không đổi", diff == 200, f"got diff={diff}")
ok("6b không note khi BUY", note is None, f"got={note}")

# ============================================================================================
print(f"\n{len(PASS)} PASS, {len(FAIL)} FAIL")
if FAIL:
    print("FAILED:", FAIL)
    sys.exit(1)
sys.exit(0)
