#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck: `DNSEBroker.modify_order` nhánh HTTP 500 REMOTE_SERVER_ERROR phải tìm lệnh mới
CHỈ trong cùng mã (và cùng chiều nếu biết) với lệnh cũ.

Trước 2026-11-22 heuristic "id số lớn nhất còn sống" quét MỌI mã ⇒ trả order_id của mã khác.
Khoá: (1) lệnh mới cùng mã được chọn dù có lệnh MÃ KHÁC id lớn hơn; (2) không có lệnh cùng mã ⇒ None
(không nhặt lệnh mã khác); (3) lệnh cũ không còn trong sổ / thiếu symbol ⇒ None (fail-safe, caller
cancel+replace); (4) khác chiều cùng mã bị loại; (5) đường thành công không 500 giữ nguyên.
Mutant: bỏ `and _same(u)` khỏi candidates ⇒ (1)/(2)/(4) phải FAIL.

Chạy:  python3 WorkingClaude/brokers_modify_order_selfcheck.py
       cd /tmp && env -u TZ python3 <repo>/WorkingClaude/brokers_modify_order_selfcheck.py
"""
import importlib.util
import os
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")          # §5b

import trading_bot.brokers as BR   # noqa: E402
import dnse_api                    # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  ✓ " if cond else "  ✗ ") + name + (f"   [{detail}]" if detail and not cond else ""))


def _err500():
    e = dnse_api.DNSEError.__new__(dnse_api.DNSEError)
    e.status, e.payload = 500, {"code": "REMOTE_SERVER_ERROR"}
    Exception.__init__(e, "500 REMOTE_SERVER_ERROR")
    return e


class _Client:
    def __init__(self, exc=None, resp=None):
        self.exc, self.resp = exc, resp

    def modify_order(self, *a, **k):
        if self.exc:
            raise self.exc
        return self.resp


def _ord(oid, symbol, status, side="NB"):
    d = {"id": oid, "orderStatus": status, "side": side}
    if symbol:
        d["symbol"] = symbol
    return d


def _make(mod, orders, resp=None, exc=None):
    b = mod.DNSEBroker.__new__(mod.DNSEBroker)
    b.client = _Client(exc if exc is not None else None, resp)
    b.account_id, b.account_label = "ACC1", "T"
    b._raw_log = os.path.join(tempfile.mkdtemp(), "raw.jsonl")
    ups = {str(o["id"]): mod.OrderUpdate(o["id"], o["orderStatus"], 0, None, raw=o) for o in orders}
    b.poll_orders = lambda: ups
    return b


def run_all(mod, tag):
    import time as _t
    mod.time = types.SimpleNamespace(sleep=lambda s: None, time=_t.time)   # bỏ sleep(1)
    print(f"== {tag}")
    old = _ord(100, "VNM", "Canceled")
    # (1) lệnh mới cùng mã; có lệnh mã KHÁC id lớn hơn
    b = _make(mod, [old, _ord(105, "VNM", "New"), _ord(999, "FPT", "New")], exc=_err500())
    check(f"{tag}: chọn lệnh mới CÙNG mã dù mã khác id lớn hơn", b.modify_order(100, 10, 50000) == "105")
    # (2) không có lệnh cùng mã, chỉ có mã khác
    b = _make(mod, [old, _ord(999, "FPT", "New")], exc=_err500())
    check(f"{tag}: không nhặt lệnh mã khác ⇒ None", b.modify_order(100, 10, 50000) is None)
    # (3) lệnh cũ không còn trong sổ ⇒ fail-safe None
    b = _make(mod, [_ord(999, "FPT", "New")], exc=_err500())
    check(f"{tag}: lệnh cũ vắng sổ ⇒ None", b.modify_order(100, 10, 50000) is None)
    # (3b) lệnh cũ thiếu symbol ⇒ None
    b = _make(mod, [_ord(100, None, "Canceled"), _ord(105, "VNM", "New")], exc=_err500())
    check(f"{tag}: lệnh cũ thiếu symbol ⇒ None", b.modify_order(100, 10, 50000) is None)
    # (4) cùng mã khác chiều bị loại
    b = _make(mod, [old, _ord(105, "VNM", "New", side="NS")], exc=_err500())
    check(f"{tag}: cùng mã khác chiều bị loại ⇒ None", b.modify_order(100, 10, 50000) is None)
    # (4b) chọn id lớn nhất trong cùng mã+chiều
    b = _make(mod, [old, _ord(105, "VNM", "New"), _ord(110, "VNM", "New")], exc=_err500())
    check(f"{tag}: nhiều ứng viên cùng mã ⇒ id lớn nhất", b.modify_order(100, 10, 50000) == "110")
    # (5) lệnh cũ vẫn sống ⇒ None (modify chưa xong) — giữ nguyên
    b = _make(mod, [_ord(100, "VNM", "New"), _ord(105, "VNM", "New")], exc=_err500())
    check(f"{tag}: lệnh cũ còn sống ⇒ None", b.modify_order(100, 10, 50000) is None)
    # (6) đường thành công
    b = _make(mod, [], resp={"id": 777})
    check(f"{tag}: đường thành công trả id mới", b.modify_order(100, 10, 50000) == "777")


def load_mutant():
    src = open(os.path.join(HERE, "trading_bot", "brokers.py"), encoding="utf-8").read()
    assert "and _same(u)]" in src, "mutant anchor không còn — cập nhật selfcheck"
    src = src.replace("and _same(u)]", "]")
    spec = importlib.util.spec_from_loader("trading_bot.brokers_mut", loader=None)
    m = importlib.util.module_from_spec(spec)
    m.__package__ = "trading_bot"
    m.__file__ = os.path.join(HERE, "trading_bot", "brokers.py")
    exec(compile(src, m.__file__, "exec"), m.__dict__)
    return m


run_all(BR, "REAL")
real_fail = list(FAIL)
FAIL.clear()
run_all(load_mutant(), "MUTANT")
mutant_fail = list(FAIL)
check("MUTANT bị bắt (≥3 check FAIL khi bỏ lọc)", len(mutant_fail) >= 3, f"chỉ {len(mutant_fail)}")
print(f"\nREAL fail={len(real_fail)} | mutant fail={len(mutant_fail)} (kỳ vọng ≥3)")
ok = not real_fail and len(mutant_fail) >= 3
print("PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
