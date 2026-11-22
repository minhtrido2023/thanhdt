#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck: lỗi ppse của `DNSEBroker.get_max_buy_qty/get_buying_power` (cq-2026-11-22 hard-boundary).

Khoá 3 điều: (1) lỗi ppse ⇒ vẫn trả None (caller fail-safe như cũ) VÀ để lại đúng 1 bản ghi
`ppse_error` có lý do thật (§29); (2) log lỗi KHÔNG BAO GIỜ ném ra — kể cả message có surrogate lẻ
(`_log_raw` chỉ bắt OSError; executor.py:2163 không bọc try ⇒ ném = STEP_FAIL cả lượt step);
(3) đường bình thường giữ nguyên giá trị. Mutant: bỏ try trong `_log_ppse_error` ⇒ (2) phải FAIL.

Chạy:  python3 WorkingClaude/brokers_ppse_error_selfcheck.py
       cd /tmp && env -u TZ python3 <repo>/WorkingClaude/brokers_ppse_error_selfcheck.py
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")          # §5b

import trading_bot.brokers as BR   # noqa: E402
from trading_bot.brokers import DNSEBroker   # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  ✓ " if cond else "  ✗ ") + name + (f"   [{detail}]" if detail and not cond else ""))


class _Client:
    def __init__(self, exc=None, resp=None):
        self.exc, self.resp = exc, resp

    def ppse(self, *a, **k):
        if self.exc:
            raise self.exc
        return self.resp


def _broker(client, raw_log):
    b = DNSEBroker.__new__(DNSEBroker)
    b.client, b.account_id, b._raw_log = client, "ACC1", raw_log
    b._account_default_lp = lambda: None
    b.account_label = "T"
    return b


def _records(path):
    if not os.path.exists(path):
        return []
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def _run(exc, label):
    d = tempfile.mkdtemp(prefix="ppse_err_")
    BR.EXEC_DIR = d
    path = os.path.join(d, "raw.jsonl")
    b = _broker(_Client(exc=exc), path)
    try:
        r = (b.get_max_buy_qty("FPT", 100000), b.get_buying_power("FPT", 100000))
        err = None
    except Exception as e:           # noqa: BLE001
        r, err = None, e
    return r, err, _records(path)


# (a) lỗi thường ⇒ None + 1 bản ghi/lần gọi, có lý do thật
r, err, recs = _run(RuntimeError("HTTP 500 boom"), "a")
check("a1 lỗi thường ⇒ cả 2 hàm trả None", err is None and r == (None, None), repr((r, err)))
pe = [x for x in recs if x.get("kind") == "ppse_error"]
check("a2 đúng 2 bản ghi ppse_error (1/lần gọi)", len(pe) == 2, str(len(pe)))
check("a3 bản ghi mang lý do thật + fn", all("boom" in x["payload"]["error"] for x in pe)
      and {x["payload"]["fn"] for x in pe} == {"get_max_buy_qty", "get_buying_power"})

# (b) message có surrogate lẻ ⇒ VẪN trả None, không ném
r, err, recs = _run(RuntimeError("Boom: x\ud800y"), "b")
check("b1 surrogate lẻ ⇒ không ném, trả None", err is None and r == (None, None), repr(err))

# (c) _raw_log=None ⇒ None, không ghi gì
b = _broker(_Client(exc=RuntimeError("x")), None)
check("c1 _raw_log=None ⇒ None", b.get_max_buy_qty("FPT", 1) is None and b.get_buying_power("FPT", 1) is None)

# (d) đường bình thường không đổi
d = tempfile.mkdtemp(prefix="ppse_ok_")
BR.EXEC_DIR = d
b = _broker(_Client(resp={"qmaxBuy": 300, "pp0Buy": 3e7}), os.path.join(d, "raw.jsonl"))
check("d1 bình thường: qmaxBuy=300", b.get_max_buy_qty("FPT", 100000) == 300)
check("d2 bình thường: pp0Buy=3e7", b.get_buying_power("FPT", 100000) == 3e7)
check("d3 bình thường: KHÔNG có ppse_error", not [x for x in _records(os.path.join(d, "raw.jsonl"))
                                                  if x.get("kind") == "ppse_error"])

# (e) MUTANT: bỏ try quanh log ⇒ b1 phải FAIL (chứng minh test thật sự bắt lỗi)
orig = DNSEBroker._log_ppse_error
def _mut(self, fn, symbol, price, exc):
    self._log_raw("ppse_error", {"fn": fn, "symbol": symbol, "price": price,
                                 "error": f"{type(exc).__name__}: {exc}"})
DNSEBroker._log_ppse_error = _mut
r, err, _ = _run(RuntimeError("Boom: x\ud800y"), "mut")
check("e1 MUTANT (bỏ try) ⇒ ném UnicodeEncodeError (test có răng)", isinstance(err, UnicodeEncodeError), repr(err))
DNSEBroker._log_ppse_error = orig

print(f"\n{len(PASS)} PASS / {len(FAIL)} FAIL")
sys.exit(1 if FAIL else 0)
