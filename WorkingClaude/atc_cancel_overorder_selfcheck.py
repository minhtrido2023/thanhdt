#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Self-check `_atc_sweep`: huỷ LO thất bại KHÔNG còn dẫn tới đặt vượt kế hoạch (2026-09-28).

Nguồn: `failopen_inventory_20260928/REPORT_DOT2.md` §4.2 E-3 — `cancel_order` fail ⇒
`except Exception: pass` ⇒ lệnh LO **vẫn sống trên sổ sàn** mà `raw_remaining = o.qty - filled`
KHÔNG trừ phần đang treo ⇒ LO + ATC cùng khớp ⇒ vượt `o.qty`. `atc_remainder_sell = True`.

⚠️ KHÔNG đặt lệnh, KHÔNG chạm broker: chạy KHỐI trích nguyên văn với `self`/`broker` giả.
§5b: đặt `MIKE_BOT_TEST_MODE=1` trước mọi thứ (khối này không dựng Executor nhưng giữ quy ước).

Chạy:  $DNA_PYEXE atc_cancel_overorder_selfcheck.py
"""
import os

os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")

import re          # noqa: E402
import subprocess  # noqa: E402
import sys         # noqa: E402
import textwrap    # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REL = "WorkingClaude/trading_bot/executor.py"
OLD_REF = os.environ.get("ATC_OLD_REF", "").strip() or "df8d7b9a"
LOT = 100
_n = 0


def ok(cond, msg):
    global _n
    _n += 1
    if not cond:
        raise AssertionError(msg)


def src(ref=None):
    if ref is None:
        return open(os.path.join(HERE, "trading_bot", "executor.py"), encoding="utf-8").read()
    r = subprocess.run(["git", "show", f"{ref}:{REL}"], cwd=HERE, capture_output=True, text=True)
    if r.returncode != 0:
        raise AssertionError(f"không đọc được {ref}:{REL} — git: {r.stderr.strip()}")
    return r.stdout


def cut_block(text, what):
    """Khối ATC: neo bằng `remaining = round_lot(raw_remaining)` rồi đi LÙI tới `_open_child`.

    Không neo xuôi từ `c = self._open_child(ps)`: chuỗi đó còn xuất hiện ở hàm KHÁC phía trên
    (`_place_slices`) ⇒ cắt xuôi sẽ ôm trọn mấy hàm ở giữa (đã cắn khi viết selfcheck này).
    """
    lines = text.splitlines(keepends=True)
    j = next((k for k, l in enumerate(lines)
              if l.strip() == "remaining = round_lot(raw_remaining)"), None)
    assert j is not None, f"không thấy `remaining = round_lot(raw_remaining)` trong {what}"
    i = next((k for k in range(j, -1, -1)
              if lines[k].strip() == "c = self._open_child(ps)"), None)
    assert i is not None, f"không thấy `c = self._open_child(ps)` phía trên trong {what}"
    block = lines[i:j + 1]
    pad = len(block[0]) - len(block[0].lstrip())
    return "".join((l[pad:] if l[:pad].strip() == "" else l.lstrip()) for l in block)


def l_strip(s):
    return s.strip()


class FakeBroker:
    def __init__(self, fail):
        self.fail = fail
        self.cancelled = []

    def cancel_order(self, oid):
        if self.fail:
            raise RuntimeError("DNSE tu choi huy: order already in matching queue")
        self.cancelled.append(oid)


class FakeSelf:
    def __init__(self, child, fail):
        self.broker = FakeBroker(fail)
        self._child = child
        self.journal = []
        self.released = []

    def _open_child(self, ps):
        return self._child

    def _release_child(self, tk, c):
        self.released.append(c["oid"])

    def _journal(self, event, o=None, child_oid="", qty="", price="", note=""):
        self.journal.append({"event": event, "oid": child_oid, "qty": qty, "note": note})


class O:
    ticker = "AAA"
    qty = 1000
    side = "sell"


def run(ref, cancel_fails, child_qty=400, child_filled=0, parent_filled=200):
    child = {"oid": "OID-LO-1", "qty": child_qty, "filled": child_filled, "status": "open"}
    ps = {"filled": parent_filled, "children": [child]}
    slf = FakeSelf(child, cancel_fails)
    g = {"self": slf, "ps": ps, "o": O(), "round_lot": lambda q: (int(q) // LOT) * LOT,
         "LOT": LOT, "int": int, "max": max, "type": type}
    exec(cut_block(src(ref), f"khối ATC @{ref or 'HEAD'}"), g)
    return g["remaining"], slf, child


def t_cancel_ok_unchanged():
    """Huỷ THÀNH CÔNG ⇒ hai bản y nhau: remaining = qty − filled, không journal thêm."""
    r_new, s_new, _ = run(None, cancel_fails=False)
    r_old, s_old, _ = run(OLD_REF, cancel_fails=False)
    ok(r_new == r_old == 800, f"huỷ OK: remaining phải 800 (1000−200), được {r_new}/{r_old}")
    ok(s_new.journal == [] and s_old.journal == [],
       f"huỷ OK: không được journal thêm: {s_new.journal} / {s_old.journal}")
    ok(s_new.released == s_old.released == ["OID-LO-1"], "huỷ OK: phải release child")


def t_cancel_fail_two_sided():
    """Huỷ THẤT BẠI — điểm khác biệt thật."""
    r_old, s_old, c_old = run(OLD_REF, cancel_fails=True)
    ok(r_old == 800,
       f"bản CŨ: remaining vẫn 800 dù 400cp còn treo ⇒ tổng đặt 800+400=1200 > qty 1000 (được {r_old})")
    ok(s_old.journal == [], f"bản CŨ phải CÂM TUYỆT ĐỐI, nhưng journal: {s_old.journal}")
    ok(c_old["status"] == "open", "bản CŨ: child vẫn open (đúng) — nhưng không ai trừ nó ra")

    r_new, s_new, c_new = run(None, cancel_fails=True)
    ok(r_new == 400, f"bản MỚI: remaining phải 1000−200−400 = 400, được {r_new}")
    ok(r_new + (c_new["qty"] - c_new["filled"]) + 200 == O.qty,
       f"BẤT BIẾN: ATC({r_new}) + LO còn treo(400) + đã khớp(200) = qty(1000)")
    ok(len(s_new.journal) == 1 and s_new.journal[0]["event"] == "CANCEL_FAIL",
       f"bản MỚI phải journal CANCEL_FAIL: {s_new.journal}")
    j = s_new.journal[0]
    ok("RuntimeError" in j["note"], f"không trích LỖI THẬT (§29): {j['note']}")
    ok("matching queue" in j["note"], f"không mang thông điệp lỗi gốc: {j['note']}")
    ok(j["oid"] == "OID-LO-1" and j["qty"] == 400, f"journal thiếu oid/qty: {j}")
    ok(s_new.released == [], "bản MỚI: huỷ thất bại thì KHÔNG được release child")


def t_cancel_fail_covers_all_remaining():
    """Phần còn treo phủ kín phần còn lại ⇒ remaining < LOT ⇒ bỏ ATC lượt này (bảo thủ)."""
    r_new, _, _ = run(None, cancel_fails=True, child_qty=800, parent_filled=200)
    ok(r_new == 0, f"bản MỚI: 1000−200−800 = 0 ⇒ dưới LOT ⇒ bỏ ATC, được {r_new}")
    r_old, _, _ = run(OLD_REF, cancel_fails=True, child_qty=800, parent_filled=200)
    ok(r_old == 800, f"bản CŨ: vẫn 800 ⇒ 800+800=1600 = 1,6× kế hoạch (được {r_old})")


def t_child_partially_filled():
    """Child đã khớp một phần: chỉ trừ phần CHƯA khớp (phần đã khớp nằm trong ps['filled'])."""
    r_new, _, _ = run(None, cancel_fails=True, child_qty=400, child_filled=100, parent_filled=300)
    ok(r_new == 400, f"1000−300−(400−100)=400, được {r_new}")


TESTS = [t_cancel_ok_unchanged, t_cancel_fail_two_sided, t_cancel_fail_covers_all_remaining,
         t_child_partially_filled]

if __name__ == "__main__":
    print(f"TZ={os.environ.get('TZ', '(unset)')}  python={sys.version.split()[0]}  OLD_REF={OLD_REF}")
    fails = 0
    for t in TESTS:
        try:
            t()
            print(f"  PASS {t.__name__}")
        except AssertionError as e:
            fails += 1
            print(f"  FAIL {t.__name__}: {e}")
    print()
    print(f"{'PASS' if not fails else 'FAIL'}  ({_n} assertion"
          + (")" if not fails else f", {fails} test FAIL)"))
    sys.exit(1 if fails else 0)
