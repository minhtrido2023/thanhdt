# -*- coding: utf-8 -*-
"""plan_buying_power_shadow_replay.py — self-check + REPLAY lịch sử cho shadow logger
`bot_execute._log_plan_buying_power_shadow` (rule PLAN_BUYING_POWER, trạng thái WARN_ONLY).

Chạy:  $DNA_PYEXE plan_buying_power_shadow_replay.py

Ba phần:
  1. UNIT — broker giả lập: đúng cột/giá trị, chỉ live, chỉ khi có lệnh mua, không đo được
     sức mua → "unknown", và TUYỆT ĐỐI không raise / không sửa plan.
  2. REPLAY A — 3 ngày sự cố funding_required (bản plan VI PHẠM trước khi bị sửa, số lấy từ
     bus event của chính các job DollarBill lúc đó) vs sức mua THẬT đọc từ
     `data/execution_logs/dnse_raw_<plan_date>.jsonl` (lọc theo account_no — §12). Kỳ vọng:
     would_block=true cả 3.
  3. REPLAY B — plan THẬT đã được sửa/duyệt của chính các ngày đó + ZaloPay 07-28. Kỳ vọng:
     would_block=false (rule không kêu oan trên ngày lành).

⚠️ HẠN CHẾ ĐÃ BIẾT (đọc trước khi diễn giải kết quả): trong toàn bộ `dnse_raw_*.jsonl` KHÔNG
có MỘT bản ghi `ppse` nào của SpaceX (0/∞) — chỉ có `balances`. Nên REPLAY A/B dùng PROXY
`availableCash` + `totalCash` thay cho `pp0Buy` thật. Với account CÓ MARGIN như SpaceX,
pp0Buy ≥ cash (có thể lớn hơn NHIỀU nhờ thế chấp danh mục ~860M) ⇒ verdict "would_block=true"
của REPLAY A là kết luận theo cận-dưới-của-sức-mua, KHÔNG phải bằng chứng rule sẽ bắn với số
pp0Buy thật. Đây chính là câu hỏi mà ≥10 phiên shadow log (đo pp0Buy sống lúc 09:05) sinh ra
để trả lời — không được kết luận thay nó ở đây. Bằng chứng cash ≠ sức mua: ZaloPay 07-28
availableCash 5,68M / totalCash 32,01M / pp0Buy THẬT 25,54M.
"""
import csv
import dataclasses
import json
import os
import sys
import tempfile

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
sys.path.insert(0, WORKDIR)

import bot_execute
from trading_bot.plan import (PlannedOrder, TradePlan, load_plan, net_offsetting_orders)

PASS = FAIL = 0

SPACEX_NO = "0002023347"
ZALOPAY_NO = "0001743768"


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name}  {detail}")


class FakeBroker:
    def __init__(self, bp=None, boom=False):
        self.bp, self.boom, self.calls = bp, boom, []

    def get_buying_power(self, symbol, price):
        if self.boom:
            raise RuntimeError("ppse down")
        self.calls.append((symbol, price))
        return self.bp


def mk_plan(specs, plan_date="2026-07-29", account="SELFCHECK"):
    orders = [PlannedOrder(id=f"{sd.upper()}-{tk}-{i:02d}", ticker=tk, side=sd, qty=qty,
                           ref_price=px, book="CAPIT")
              for i, (tk, sd, qty, px) in enumerate(specs)]
    return TradePlan(plan_date=plan_date, signal_date=plan_date, strategy="t",
                     strategy_version="0", state=3, state_name="NEUTRAL",
                     nav_basis={}, orders=orders, account=account)


def run_logger(plan, broker, mode="live", label="TEST"):
    """Gọi ĐÚNG hàm production, chỉ đổi đích ghi CSV sang file tạm."""
    fd, path = tempfile.mkstemp(suffix=".csv")
    os.close(fd)
    os.unlink(path)
    orig = bot_execute._BP_SHADOW_LOG
    bot_execute._BP_SHADOW_LOG = path
    try:
        before = [dataclasses.asdict(o) for o in plan.orders]
        bot_execute._log_plan_buying_power_shadow(label, plan, broker, mode)
        after = [dataclasses.asdict(o) for o in plan.orders]
        assert before == after, "shadow logger ĐÃ SỬA plan — vi phạm hợp đồng WARN_ONLY"
        rows = []
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            os.unlink(path)
        return rows
    finally:
        bot_execute._BP_SHADOW_LOG = orig


print("=" * 78)
print("  1. UNIT (broker giả lập)")
print("=" * 78)

p = mk_plan([("PVT", "buy", 3200, 16656.0), ("TV1", "buy", 300, 19400.0)])
rows = run_logger(p, FakeBroker(bp=10_412_823.0))
exp_val = 3200 * 16656.0 + 300 * 19400.0
check("ghi đúng 1 dòng, đủ 6 cột",
      len(rows) == 1 and list(rows[0].keys()) == list(bot_execute._BP_SHADOW_COLS), f"{rows}")
check("Σ mua đúng + would_block=true khi vượt sức mua",
      rows and float(rows[0]["orders_buy_value_vnd"]) == exp_val
      and rows[0]["would_block"] == "true"
      and float(rows[0]["buying_power_vnd"]) == 10_412_823.0, f"{rows}")
check("ppse hỏi theo lệnh mua LỚN NHẤT (pp0Buy là số cấp account)",
      rows and rows[0]["buying_power_source"].endswith("@PVT"), f"{rows}")

rows = run_logger(mk_plan([("PVT", "buy", 100, 16656.0)]), FakeBroker(bp=500_000_000.0))
check("đủ sức mua → would_block=false", rows and rows[0]["would_block"] == "false", f"{rows}")

rows = run_logger(mk_plan([("PVT", "buy", 100, 16656.0)]), FakeBroker(bp=None))
check("broker trả None → would_block=unknown, không đoán",
      rows and rows[0]["would_block"] == "unknown" and rows[0]["buying_power_vnd"] == ""
      and rows[0]["buying_power_source"] == "unavailable:ppse", f"{rows}")

rows = run_logger(mk_plan([("PVT", "buy", 100, 16656.0)]), FakeBroker(boom=True))
check("ppse NỔ → vẫn ghi log, would_block=unknown, KHÔNG raise",
      rows and rows[0]["would_block"] == "unknown"
      and rows[0]["buying_power_source"].startswith("unavailable:"), f"{rows}")

rows = run_logger(mk_plan([("VPB", "sell", 800, 25000.0)]), FakeBroker(bp=1.0))
check("plan chỉ có lệnh BÁN → không ghi (không log ồn)", rows == [], f"{rows}")

rows = run_logger(mk_plan([("PVT", "buy", 100, 16656.0)]), FakeBroker(bp=1.0), mode="paper")
check("account paper → không ghi (phạm vi = live)", rows == [], f"{rows}")

rows = run_logger(mk_plan([("PVT", "buy", 100, 16656.0), ("VPB", "sell", 800, 25000.0)]),
                  FakeBroker(bp=1_000_000.0))
check("chỉ tính vế MUA, không trừ/không cộng lệnh bán",
      rows and float(rows[0]["orders_buy_value_vnd"]) == 100 * 16656.0, f"{rows}")


class _BadBroker:
    def get_buying_power(self, s, p):
        raise SystemError("nổ sâu")

    def __getattr__(self, k):
        raise SystemError("nổ sâu")


try:
    rows = run_logger(mk_plan([("PVT", "buy", 100, 16656.0)]), _BadBroker())
    check("mọi lỗi đều nuốt, không bao giờ raise ra phiên", True)
except Exception as ex:
    check("mọi lỗi đều nuốt, không bao giờ raise ra phiên", False, f"{ex}")

# ---------------------------------------------------------------- dữ liệu broker lịch sử


def broker_facts(day, account_no):
    """Đọc dnse_raw của NGÀY đó, LỌC THEO account_no ngay dòng đầu (coding_guidelines §12).

    Trả {"pp0Buy":…, "availableCash":…, "totalCash":…} của bản ghi ĐẦU TIÊN trong ngày —
    tức bản đọc lúc ~09:15 đầu phiên, ĐÚNG thời điểm shadow logger chạy thật (ngay sau
    broker.connect() của bot_execute). Bản ghi cuối ngày (19:10 EOD) là số SAU khi đã mua
    bán, không phải sức mua mà cổng nhìn thấy lúc quyết định.
    """
    path = os.path.join("data", "execution_logs", f"dnse_raw_{day}.jsonl")
    out = {"pp0Buy": None, "availableCash": None, "totalCash": None, "ts": None}
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if str(rec.get("account_no")) != str(account_no):
                continue
            if rec.get("kind") == "balances" and out["totalCash"] is None:
                s = (rec.get("payload") or {}).get("stock") or {}
                if s.get("totalCash") is not None:
                    out["availableCash"] = float(s.get("availableCash") or 0)
                    out["totalCash"] = float(s.get("totalCash") or 0)
                    out["ts"] = rec.get("ts")
            elif rec.get("kind") == "ppse" and out["pp0Buy"] is None:
                v = ((rec.get("payload") or {}).get("resp") or {}).get("pp0Buy")
                if v is not None:
                    out["pp0Buy"] = float(v)
    return out


print("=" * 78)
print("  2. REPLAY A — 3 bản plan VI PHẠM (trước khi bị sửa) vs sức mua THẬT của ngày đó")
print("=" * 78)

# (plan_date, account_no, label, Σ orders[] mua của bản VI PHẠM, nguồn số)
INCIDENTS = [
    ("2026-07-24", SPACEX_NO, "SpaceX", 177_347_911,
     "bus plan-2026-07-24 (07-23T12:17:51Z): 6 lệnh 177.347.911đ, đòi rút Trứng vàng 134M"),
    ("2026-07-28", SPACEX_NO, "SpaceX", 460_740_000,
     "bus fix-plan-07-28-funding-required (07-27T16:42:57Z): 8 lệnh 460,74M, 7x funding_required"),
    ("2026-07-29", SPACEX_NO, "SpaceX", 146_477_276,
     "bus plan-SpaceX-2026-07-29-cash-fix (07-28T15:26:18Z): 4 lệnh 146.477.276đ, 'user sẽ nạp 136M'"),
]

for day, acc_no, label, buy_value, src in INCIDENTS:
    facts = broker_facts(day, acc_no)
    bp = facts["pp0Buy"] if facts["pp0Buy"] is not None else facts["availableCash"]
    proxy = "ppse.pp0Buy THẬT" if facts["pp0Buy"] is not None else "PROXY balances.availableCash"
    print(f"\n  {label} {day} — {src}")
    print(f"    broker {facts['ts']}: availableCash={facts['availableCash']:,.0f}đ  "
          f"totalCash={facts['totalCash']:,.0f}đ  pp0Buy={facts['pp0Buy']}")
    # Chạy ĐÚNG hàm production với sức mua lịch sử.
    plan = mk_plan([("PVT", "buy", 1, buy_value)], plan_date=day, account=label)
    rows = run_logger(plan, FakeBroker(bp=bp), label=label)
    check(f"replay {label} {day}: would_block=true ({proxy})",
          rows and rows[0]["would_block"] == "true",
          f"{rows}")
    # Kiểm tra thêm bằng cận TRÊN dễ dãi nhất trong dữ liệu có thật (totalCash).
    rows2 = run_logger(mk_plan([("PVT", "buy", 1, buy_value)], plan_date=day, account=label),
                       FakeBroker(bp=facts["totalCash"]), label=label)
    check(f"… và vẫn true khi nới sức mua lên totalCash {facts['totalCash']:,.0f}đ",
          rows2 and rows2[0]["would_block"] == "true", f"{rows2}")
    print(f"    Σ mua {buy_value:,.0f}đ / sức mua {bp:,.0f}đ = "
          f"{buy_value / max(bp, 1):.1f}× — thiếu {buy_value - bp:,.0f}đ")

print()
print("=" * 78)
print("  3. REPLAY B — plan THẬT (bản đã sửa/đã duyệt) của chính các ngày đó → phải im lặng")
print("=" * 78)

BENIGN = [("2026-07-24", SPACEX_NO, "SpaceX"), ("2026-07-28", SPACEX_NO, "SpaceX"),
          ("2026-07-29", SPACEX_NO, "SpaceX"), ("2026-07-28", ZALOPAY_NO, "ZaloPay"),
          ("2026-07-27", ZALOPAY_NO, "ZaloPay"), ("2026-07-23", ZALOPAY_NO, "ZaloPay")]

for day, acc_no, label in BENIGN:
    plan = load_plan(day, account=label)
    if plan is None:
        print(f"  – {label} {day}: không có plan file, bỏ qua")
        continue
    # Shadow logger ngồi SAU toàn bộ cascade → phải netting trước cho đúng plan mà nó thấy
    # (ZaloPay 07-27: BUY VPB 700 + SELL VPB 800 → 1 lệnh SELL, vế mua thật = 0). Các trần
    # %ADV chỉ CẮT BỚT lệnh mua nên bỏ qua chúng là hướng BẢO THỦ (Σ mua ≥ thực tế).
    plan, _ = net_offsetting_orders(plan)
    facts = broker_facts(day, acc_no)
    bp = facts["pp0Buy"] if facts["pp0Buy"] is not None else facts["availableCash"]
    proxy = "pp0Buy THẬT" if facts["pp0Buy"] is not None else "PROXY availableCash"
    buys = [o for o in plan.orders if o.side == "buy"]
    if bp is None:
        print(f"  – {label} {day}: không có dữ liệu broker ngày đó, bỏ qua")
        continue
    rows = run_logger(plan, FakeBroker(bp=bp), label=label)
    if not buys:
        check(f"replay {label} {day}: HOLD/không có lệnh mua → KHÔNG log dòng nào", rows == [],
              f"{rows}")
        continue
    tot = sum(o.value for o in buys)
    print(f"  {label} {day}: Σ mua {tot:,.0f}đ vs sức mua {bp:,.0f}đ ({proxy})")
    check(f"replay {label} {day}: would_block=false (không kêu oan)",
          rows and rows[0]["would_block"] == "false", f"{rows}")

print("=" * 78)
print(f"  TỔNG: {PASS} PASS / {FAIL} FAIL")
sys.exit(1 if FAIL else 0)
