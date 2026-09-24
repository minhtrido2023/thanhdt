#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck cho `verify_account_snapshot.broker_positions_from_raw()` — Việc 3 (job
Taylor_20260924_064510).

BUG ĐÃ SỬA: `out.setdefault(tk, {"qty": 0.0, "marketPrice": p.get("marketPrice")})` chỉ ghi
`marketPrice` của LÔ ĐẦU TIÊN gặp trong mảng `positions[]` cho mỗi mã — các lô sau (loan
package khác, cùng mã) bị bỏ qua hoàn toàn, kể cả khi giá của chúng MỚI HƠN/ĐÚNG HƠN. DNSE điều
chỉnh `marketPrice` theo TỪNG GÓI VAY và KHÔNG NGUYÊN TỬ (`price_frame.py` §G4, đo thật BID
2026-08-14: 35.800 vs 38.850, lệch 8,5%). Vá: giữ `marketPrice` LATEST non-None, đúng quy ước
`DNSEBroker.get_positions()` (`trading_bot/brokers.py`) đã dùng.

Chạy:  python3 mike/bin/verify_account_snapshot_broker_positions_marketprice_selfcheck.py
Phải PASS y hệt dưới TZ lạ (§16 + skill verify-before-done):
       env -u TZ python3 <repo>/mike/bin/verify_account_snapshot_broker_positions_marketprice_selfcheck.py

0 side-effect thật: mọi fixture nằm trong `tempfile.mkdtemp()`, `VAS.EXEC_DIR` bị monkeypatch
trỏ vào đó — không đụng `data/execution_logs/` production.
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import verify_account_snapshot as VAS  # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  ✓ " if cond else "  ✗ ") + name + (f"   [{detail}]" if detail and not cond else ""))


ACCOUNT_NO = "0002023347"
TMPDIR = tempfile.mkdtemp(prefix="vas_bp_selfcheck_")
ORIG_EXEC_DIR = VAS.EXEC_DIR


def write_fixture(asof, positions_records):
    """`positions_records` = list các bản ghi 'positions' liên tiếp (mỗi bản ghi là 1 lần
    poll broker); mỗi record là list các dict lô (loan package). Chỉ bản ghi CUỐI trong file
    được `broker_positions_from_raw` đọc (đúng hành vi `latest = ...` ghi đè theo dòng)."""
    path = os.path.join(TMPDIR, f"dnse_raw_{asof}.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for positions in positions_records:
            rec = {"kind": "positions", "account_no": ACCOUNT_NO,
                   "payload": {"positions": positions}}
            f.write(json.dumps(rec) + "\n")
    return path


def lot(symbol, qty, market_price):
    return {"symbol": symbol, "openQuantity": qty, "marketPrice": market_price}


def old_buggy_merge(positions):
    """Tái hiện Y HỆT logic CŨ (`out.setdefault(tk, {..., "marketPrice": p.get("marketPrice")})`)
    — giữ marketPrice của LÔ ĐẦU TIÊN gặp, bỏ qua mọi lô sau. Dùng để CHỨNG MINH NGƯỢC: nếu
    mutation guard revert bản vá về đúng dòng này, assertion ở test [2]/[4]/[5] phải bắt được."""
    out = {}
    for p in positions:
        qty = float(p.get("openQuantity") or 0)
        if qty <= 0:
            continue
        tk = p.get("symbol")
        row = out.setdefault(tk, {"qty": 0.0, "marketPrice": p.get("marketPrice")})
        row["qty"] += qty
    return out


print("[1] 1 lô duy nhất — hành vi KHÔNG đổi (control)")
VAS.EXEC_DIR = TMPDIR
write_fixture("2026-09-20", [[lot("BID", 1000, 38850.0)]])
out = VAS.broker_positions_from_raw(ACCOUNT_NO, "2026-09-20")
check("qty = 1000", out["BID"]["qty"] == 1000.0, out)
check("marketPrice = 38.850 (1 lô, không đổi)", out["BID"]["marketPrice"] == 38850.0, out)

print("\n[2] NHIỀU lô cùng mã, marketPrice KHÁC nhau — phải lấy giá LÔ CUỐI (LATEST), "
      "không phải lô đầu")
fixture2_positions = [lot("BID", 600, 38850.0), lot("BID", 400, 35800.0)]
write_fixture("2026-09-21", [fixture2_positions])
out = VAS.broker_positions_from_raw(ACCOUNT_NO, "2026-09-21")
check("qty = 1000 (cộng gộp 2 lô)", out["BID"]["qty"] == 1000.0, out)
check("marketPrice = 35.800 (giá LÔ CUỐI, KHÔNG phải 38.850 của lô đầu — BUG ĐÃ SỬA)",
      out["BID"]["marketPrice"] == 35800.0, out)
check("[CHỨNG MINH NGƯỢC] chạy lại ĐÚNG logic CŨ (setdefault giữ lô đầu) trên CÙNG fixture "
      "này ra 38.850 — SAI thật, không phải khác biệt lý thuyết",
      old_buggy_merge(fixture2_positions)["BID"]["marketPrice"] == 38850.0,
      old_buggy_merge(fixture2_positions))

print("\n[3] lô SAU có marketPrice=None (broker không trả giá cho gói vay đó) — phải GIỮ giá "
      "lô TRƯỚC, không ghi đè thành None")
write_fixture("2026-09-22", [[lot("MBB", 500, 22050.0), lot("MBB", 300, None)]])
out = VAS.broker_positions_from_raw(ACCOUNT_NO, "2026-09-22")
check("qty = 800", out["MBB"]["qty"] == 800.0, out)
check("marketPrice = 22.050 (giữ giá khác-None gần nhất, không bị None đè)",
      out["MBB"]["marketPrice"] == 22050.0, out)

print("\n[4] 3 mã khác nhau, mỗi mã 2-3 lô — không bị lẫn giá giữa các mã")
write_fixture("2026-09-23", [[
    lot("VCB", 200, 90000.0), lot("VCB", 100, 91000.0),
    lot("ACB", 500, 27000.0),
    lot("VNM", 1000, 60000.0), lot("VNM", 200, 60500.0), lot("VNM", 300, 61000.0),
]])
out = VAS.broker_positions_from_raw(ACCOUNT_NO, "2026-09-23")
check("VCB qty=300, marketPrice=91.000 (lô cuối)", out["VCB"]["qty"] == 300.0 and
      out["VCB"]["marketPrice"] == 91000.0, out.get("VCB"))
check("ACB qty=500, marketPrice=27.000 (1 lô)", out["ACB"]["qty"] == 500.0 and
      out["ACB"]["marketPrice"] == 27000.0, out.get("ACB"))
check("VNM qty=1500, marketPrice=61.000 (lô cuối trong 3 lô)", out["VNM"]["qty"] == 1500.0 and
      out["VNM"]["marketPrice"] == 61000.0, out.get("VNM"))

print("\n[5] CHỈ bản ghi 'positions' CUỐI trong file được dùng (nhiều lần poll trong ngày) — "
      "hành vi cũ của `latest = ...` không đổi")
write_fixture("2026-09-24", [
    [lot("TCB", 400, 35000.0)],                              # poll đầu ngày
    [lot("TCB", 400, 35200.0), lot("TCB", 100, 34900.0)],     # poll cuối ngày — lô mới mua thêm
])
out = VAS.broker_positions_from_raw(ACCOUNT_NO, "2026-09-24")
check("qty = 500 (chỉ đọc bản ghi CUỐI, không cộng dồn cả 2 poll)", out["TCB"]["qty"] == 500.0, out)
check("marketPrice = 34.900 (lô cuối của bản ghi CUỐI)", out["TCB"]["marketPrice"] == 34900.0, out)

print("\nZ. MUTATION GUARD — patch NGUYÊN HÀM về đúng bug cũ (chỉ đổi bước merge marketPrice), "
      "assertion chính ở test [2]/[4] phải bắt được")
ORIG_FN = VAS.broker_positions_from_raw


def _mutant_first_lot_only(account_no, asof):
    """Y HỆT `broker_positions_from_raw` thật (đọc file, lọc account, lấy bản ghi CUỐI) —
    CHỈ khác bước merge cuối: dùng `old_buggy_merge` (giữ marketPrice LÔ ĐẦU) thay vì LATEST."""
    path = os.path.join(VAS.EXEC_DIR, f"dnse_raw_{asof}.jsonl")
    if not os.path.exists(path):
        return None
    latest = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if rec.get("kind") != "positions" or rec.get("account_no") != account_no:
                continue
            latest = rec.get("payload", {}).get("positions") or []
    if latest is None:
        return None
    return old_buggy_merge(latest)


try:
    VAS.broker_positions_from_raw = _mutant_first_lot_only
    mutant_out2 = VAS.broker_positions_from_raw(ACCOUNT_NO, "2026-09-21")
    mutant_out4 = VAS.broker_positions_from_raw(ACCOUNT_NO, "2026-09-23")
    killed_2 = mutant_out2["BID"]["marketPrice"] != 35800.0
    killed_4 = (mutant_out4["VCB"]["marketPrice"] != 91000.0
                or mutant_out4["VNM"]["marketPrice"] != 61000.0)
    check("mutant (giữ lô đầu) bị assertion test [2] bắt được (marketPrice != 35.800)",
          killed_2, mutant_out2)
    check("mutant (giữ lô đầu) bị assertion test [4] bắt được (VCB/VNM marketPrice sai)",
          killed_4, mutant_out4)
finally:
    VAS.broker_positions_from_raw = ORIG_FN

VAS.EXEC_DIR = ORIG_EXEC_DIR

print(f"\n{'=' * 70}\nKẾT QUẢ: {len(PASS)} PASS / {len(FAIL)} FAIL")
if FAIL:
    print("FAIL:")
    for f in FAIL:
        print("  ·", f)
    sys.exit(1)
print("✅ ALL PASS")
