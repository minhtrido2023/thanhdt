#!/usr/bin/env python3
"""Selfcheck cho `trading_bot/plan_funding_gate.py` — gate CỨNG Σ lệnh MUA ≤ sức mua thật.

Chạy:  python3 plan_funding_gate_selfcheck.py
Không đụng mạng, không đụng broker thật, không ghi file nào — broker là stub trong file này.

Phủ (theo skill verify-before-done — nêu rõ phụ thuộc môi trường, không phụ thuộc TZ/credential):
  A. plan VI PHẠM (Σ mua > sức mua)            → BLOCK, 0 lệnh được phép đặt
  B. plan HỢP LỆ  (Σ mua < sức mua)            → OK, gate không cản trở gì
  C. BIÊN: Σ mua == ĐÚNG BẰNG sức mua          → OK  (luật là `≤`, không phải `<`)
  D. BIÊN: Σ mua vượt sức mua đúng 1 đồng      → BLOCK
  E. phí 0,075% được TÍNH vào Σ                → BLOCK khi chỉ vượt nhờ phần phí
  F. nhiều gói vay (cash_only + default)       → đo per-nhóm, cộng tỉ lệ tiêu thụ
  G. ca TV1 2026-07-29 THẬT (gói default sai)  → gate KHÔNG chặn oan (naive gate thì chặn)
  H. pp0Buy không đo được + Σ trong cận ngoài  → UNVERIFIED (không chặn)
  I. pp0Buy không đo được + Σ vượt cận ngoài   → BLOCK
  J. pp0Buy == 0 do HẾT TIỀN THẬT              → BLOCK (cận ngoài bắt được)
  K. replay sự cố THẬT 07-27 (460,7M/12,4M)    → BLOCK
  L. replay sự cố THẬT 07-28 (146,5M/10,41M)   → BLOCK
  M. plan chỉ có lệnh BÁN / mode=paper         → SKIPPED (không cản trở)
  N. get_buying_power ném exception            → không nổ, rơi về cận ngoài
  O. ĐÒN BẨY CAPIT (order.loan_package_id):    → gói vay phải giải qua _validate_lever_package
     giống hệt `DNSEBroker.place_order`, vì gói không hợp lệ cho mã bị HẠ về gói default
     (sức mua NHỎ HƠN) TRƯỚC khi lệnh đi ra. Đo theo gói khai báo = ĐO THỪA sức mua.
"""
import os
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trading_bot.plan_funding_gate import (      # noqa: E402
    check_plan_funding, funding_block_reason, FEE_RATE, FALLBACK_LEVERAGE_MULT)

PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} — {detail}")


# ── stub tối thiểu: đúng những thuộc tính gate đọc, không hơn ─────────────────────────────
def order(ticker, qty, price, side="buy", cash_only=False, loan_package_id=None, priority=5):
    o = types.SimpleNamespace()
    o.ticker, o.qty, o.ref_price, o.side = ticker, qty, price, side
    o.cash_only, o.loan_package_id = cash_only, loan_package_id
    # priority=5 = ĐÚNG default của dataclass Order (plan.py:26). Giữ nguyên cho mọi ca cũ ⇒
    # mua lẫn bán đều =5 ⇒ điều kiện `<` NGHIÊM NGẶT sai ⇒ 0 tín dụng JIT ⇒ hành vi y hệt trước.
    o.priority = priority
    return o


def plan(orders, account="SpaceX", plan_date="2026-08-05"):
    p = types.SimpleNamespace()
    p.orders, p.account, p.plan_date = orders, account, plan_date
    return p


class StubBroker:
    """`bp_by_package`: {loan_package_id (hoặc None) -> pp0Buy}. Thiếu key → None (không đo được).
    `resolve`: {ticker -> package} cho lệnh cash_only, mô phỏng _resolve_loan_package_id.
    `lever_valid`: {ticker -> set(gói hợp lệ)} cho đòn bẩy CAPIT, mô phỏng
    _validate_lever_package (brokers.py:596-626) — gói KHÔNG hợp lệ cho mã ⇒ trả gói DEFAULT
    của account, tức lệnh đi ra KHÔNG có đòn bẩy. `account_default` = client.loan_package_id."""

    def __init__(self, bp_by_package=None, cash=0.0, resolve=None, raise_on_bp=False,
                 lever_valid=None, account_default=None, raise_on_validate=False,
                 no_validate=False):
        self.bp = bp_by_package or {}
        self.cash = cash
        self.resolve = resolve or {}
        self.raise_on_bp = raise_on_bp
        self.lever_valid = lever_valid or {}
        self.raise_on_validate = raise_on_validate
        self.client = types.SimpleNamespace(loan_package_id=account_default)
        if no_validate:
            # Broker không hỗ trợ khái niệm gói vay chỉ định (paper broker, broker khác).
            self._validate_lever_package = None
        self.calls = []
        self.validate_calls = []

    def get_buying_power(self, symbol, price, loan_package_id=None):
        self.calls.append((symbol, price, loan_package_id))
        if self.raise_on_bp:
            raise RuntimeError("ppse timeout")
        return self.bp.get(loan_package_id)

    def get_cash(self):
        return self.cash

    def _resolve_loan_package_id(self, symbol):
        return self.resolve.get(symbol, None)

    def _validate_lever_package(self, symbol, want):
        """Cùng contract với DNSEBroker._validate_lever_package: (id_sẽ_dùng, ok, note)."""
        self.validate_calls.append((symbol, want))
        if self.raise_on_validate:
            raise RuntimeError("loan_packages timeout")
        default = self.client.loan_package_id
        if str(want) in {str(i) for i in self.lever_valid.get(symbol, set())}:
            return want, True, ""
        return default, False, f"gói {want} KHÔNG hợp lệ cho {symbol}"


print("=" * 78)
print("SELFCHECK plan_funding_gate — gate CỨNG Σ lệnh MUA ≤ sức mua thật (pp0Buy)")
print("=" * 78)

# ── A. plan VI PHẠM ───────────────────────────────────────────────────────────────────────
print("\n[A] plan VI PHẠM: Σ mua 100M vs sức mua 20M")
p = plan([order("FPT", 1000, 100_000)])
v = check_plan_funding(p, StubBroker({None: 20_000_000}, cash=20_000_000), "live")
check("action == BLOCK", v["action"] == "BLOCK", v["action"])
check("funding_block_reason trả chuỗi (caller sẽ chặn)",
      isinstance(funding_block_reason(p, StubBroker({None: 20_000_000}), "live"), str))
check("reason nêu đúng cả 2 số", "100,075,000" in v["reason"] and "20,000,000" in v["reason"],
      v["reason"])

# ── B. plan HỢP LỆ ────────────────────────────────────────────────────────────────────────
print("\n[B] plan HỢP LỆ: Σ mua 10M vs sức mua 50M")
p = plan([order("ACB", 400, 25_000)])
v = check_plan_funding(p, StubBroker({None: 50_000_000}), "live")
check("action == OK", v["action"] == "OK", v["action"])
check("funding_block_reason trả None (không cản trở)",
      funding_block_reason(p, StubBroker({None: 50_000_000}), "live") is None)

# ── C/D. BIÊN `≤` ─────────────────────────────────────────────────────────────────────────
print("\n[C] BIÊN: Σ mua ĐÚNG BẰNG sức mua → phải KHÔNG chặn (luật là ≤)")
need = 1000 * 100_000 * (1 + FEE_RATE)
v = check_plan_funding(plan([order("FPT", 1000, 100_000)]),
                       StubBroker({None: need}), "live")
check("action == OK khi hoà đúng bằng", v["action"] == "OK", f"{v['action']} U={v['utilization']!r}")

print("[D] BIÊN: sức mua thiếu ĐÚNG 1 đồng → phải CHẶN")
v = check_plan_funding(plan([order("FPT", 1000, 100_000)]),
                       StubBroker({None: need - 1}, cash=need), "live")
check("action == BLOCK khi thiếu 1đ", v["action"] == "BLOCK", v["action"])

# ── E. phí có được tính không ─────────────────────────────────────────────────────────────
print("\n[E] phí 0,075%: sức mua = ĐÚNG giá trị lệnh (chưa phí) → phải CHẶN vì thiếu phần phí")
gross = 1000 * 100_000
v = check_plan_funding(plan([order("FPT", 1000, 100_000)]),
                       StubBroker({None: gross}, cash=gross), "live")
check("action == BLOCK (phí được tính vào Σ)", v["action"] == "BLOCK", v["action"])
check(f"need = gross × (1+{FEE_RATE})", abs(v["need_vnd"] - gross * (1 + FEE_RATE)) < 1e-6,
      v["need_vnd"])

# ── F. nhiều gói vay ──────────────────────────────────────────────────────────────────────
print("\n[F] 2 nhóm gói vay: mỗi nhóm tiêu thụ 60% sức mua nhóm mình → Σ tỉ lệ 1,2 → CHẶN")
b = StubBroker({None: 100_000_000, 1122: 50_000_000}, cash=50_000_000, resolve={"TV1": 1122})
o1 = order("FPT", 600, 100_000)                       # 60,045M / 100M = 0,60
o2 = order("TV1", 1500, 20_000, cash_only=True)       # 30,0225M / 50M = 0,60
v = check_plan_funding(plan([o1, o2]), b, "live")
check("action == BLOCK (0,60 + 0,60 = 1,20)", v["action"] == "BLOCK", v["action"])
check("utilization ≈ 1,20", abs(v["utilization"] - 1.2) < 1e-3, v["utilization"])
check("2 nhóm gói vay được tách", len(v["groups"]) == 2, v["groups"])
check("nhóm cash_only được đo bằng gói ĐÃ GIẢI (1122), không phải default",
      (("TV1", 20000, 1122) in b.calls), b.calls)

print("[F2] cùng cấu hình nhưng mỗi nhóm chỉ 40% → Σ 0,80 → OK")
b2 = StubBroker({None: 100_000_000, 1122: 50_000_000}, cash=50_000_000, resolve={"TV1": 1122})
v = check_plan_funding(plan([order("FPT", 400, 100_000),
                            order("TV1", 1000, 20_000, cash_only=True)]), b2, "live")
check("action == OK", v["action"] == "OK", f"{v['action']} U={v.get('utilization')}")

# ── G. ca THẬT TV1 2026-07-29 (false positive của shadow log) ─────────────────────────────
print("\n[G] REPLAY THẬT 2026-07-29 SpaceX/TV1 — dòng DUY NHẤT trong shadow log, would_block=true")
print("    Sự thật: place_order @gói 1122 được DNSE NHẬN (id 36241); pp0Buy=0 chỉ vì shadow log")
print("    query gói default 1841. availableCash lúc 09:15:14 = 10.412.823đ.")
b = StubBroker({1841: 0, 1122: 0},            # DNSE trả 0 ở CẢ 2 gói trong log thật
               cash=10_412_823, resolve={"TV1": 1122})
v = check_plan_funding(plan([order("TV1", 300, 19_400, cash_only=True)]), b, "live")
check("KHÔNG chặn oan (action != BLOCK)", v["action"] != "BLOCK",
      f"{v['action']}: {v['reason']}")
check("action == UNVERIFIED (báo to, không chặn)", v["action"] == "UNVERIFIED", v["action"])
check("có đo bằng gói 1122 (đúng gói place_order dùng)",
      any(c[2] == 1122 for c in b.calls), b.calls)
check("KHÔNG hề đo bằng gói default None/1841",
      not any(c[2] is None for c in b.calls), b.calls)

# ── H/I/J. nhánh không đo được ────────────────────────────────────────────────────────────
print("\n[H] pp0Buy không đo được, Σ 20M trong cận ngoài (cash 10M × 3 = 30M) → UNVERIFIED")
v = check_plan_funding(plan([order("FPT", 200, 100_000)]),
                       StubBroker({}, cash=10_000_000), "live")
check("action == UNVERIFIED", v["action"] == "UNVERIFIED", v["action"])
check("không chặn", funding_block_reason(plan([order("FPT", 200, 100_000)]),
                                         StubBroker({}, cash=10_000_000), "live") is None)

print("[I] pp0Buy không đo được, Σ 50M VƯỢT cận ngoài 30M → BLOCK")
v = check_plan_funding(plan([order("FPT", 500, 100_000)]),
                       StubBroker({}, cash=10_000_000), "live")
check("action == BLOCK", v["action"] == "BLOCK", v["action"])
check(f"cận ngoài = cash × {FALLBACK_LEVERAGE_MULT:g}",
      abs(v["fallback_bound_vnd"] - 30_000_000) < 1e-6, v["fallback_bound_vnd"])

print("[I2] cận ngoài CỘNG tiền bán trong plan (T+0 reuse): cash 1M + bán 20M → bound 63M")
v = check_plan_funding(plan([order("FPT", 500, 100_000),
                            order("VNM", 400, 50_000, side="sell")]),
                       StubBroker({}, cash=1_000_000), "live")
check("action == UNVERIFIED (50M ≤ 63M)", v["action"] == "UNVERIFIED",
      f"{v['action']} bound={v['fallback_bound_vnd']}")

print("[J] pp0Buy = 0 vì HẾT TIỀN THẬT (cash 0) → cận ngoài bắt được → BLOCK")
v = check_plan_funding(plan([order("FPT", 100, 100_000)]),
                       StubBroker({None: 0}, cash=0), "live")
check("action == BLOCK", v["action"] == "BLOCK", v["action"])

# ── K/L. replay 2 sự cố THẬT ──────────────────────────────────────────────────────────────
print("\n[K] REPLAY sự cố THẬT 2026-07-27: 7/8 lệnh funding_required, Σ 460,7M vs cash 12,4M")
v = check_plan_funding(plan([order("X%02d" % i, 1000, 65_814) for i in range(7)]),
                       StubBroker({}, cash=12_400_000), "live")
check("action == BLOCK (sự cố này ĐÃ BỊ CHẶN)", v["action"] == "BLOCK", v["action"])

print("[L] REPLAY sự cố THẬT 2026-07-28: 4 lệnh Σ 146,5M vs cash 10,41M ('user sẽ nạp 136M')")
v = check_plan_funding(plan([order("Y%d" % i, 1000, 36_625) for i in range(4)]),
                       StubBroker({}, cash=10_410_000), "live")
check("action == BLOCK (sự cố này ĐÃ BỊ CHẶN)", v["action"] == "BLOCK", v["action"])

print("[L2] cùng ngày 07-28, plan ZaloPay xử lý ĐÚNG (1 lệnh CSV 25,5M vừa đủ ppse) → OK")
v = check_plan_funding(plan([order("CSV", 1000, 25_000)], account="ZaloPay"),
                       StubBroker({None: 25_540_000}, cash=5_680_000), "live")
check("action == OK (không chặn plan làm đúng)", v["action"] == "OK",
      f"{v['action']}: {v['reason']}")

# ── M/N. không cản trở / không nổ ─────────────────────────────────────────────────────────
print("\n[M] plan chỉ có lệnh BÁN → SKIPPED; mode=paper → SKIPPED")
v = check_plan_funding(plan([order("VNM", 100, 60_000, side="sell")]),
                       StubBroker({}, cash=0), "live")
check("chỉ bán → SKIPPED", v["action"] == "SKIPPED", v["action"])
v = check_plan_funding(plan([order("FPT", 10_000, 100_000)]), StubBroker({}, cash=0), "paper")
check("mode=paper → SKIPPED (dù vượt tiền)", v["action"] == "SKIPPED", v["action"])
v = check_plan_funding(plan([]), StubBroker({}, cash=0), "live")
check("plan rỗng → SKIPPED", v["action"] == "SKIPPED", v["action"])

print("\n[N] get_buying_power ném exception → gate KHÔNG nổ, rơi về cận ngoài")
v = check_plan_funding(plan([order("FPT", 100, 100_000)]),
                       StubBroker({}, cash=50_000_000, raise_on_bp=True), "live")
check("không raise, action == UNVERIFIED", v["action"] == "UNVERIFIED", v["action"])
check("lỗi được ghi lại để log", v["groups"][0]["error"] == "RuntimeError", v["groups"])

print("[N2] get_cash cũng lỗi → cash coi như 0 → BLOCK (fail-safe, không đoán có tiền)")
bad = StubBroker({}, cash=0, raise_on_bp=True)
bad.get_cash = lambda: (_ for _ in ()).throw(RuntimeError("balances down"))
v = check_plan_funding(plan([order("FPT", 100, 100_000)]), bad, "live")
check("action == BLOCK", v["action"] == "BLOCK", v["action"])

# ── O. ĐÒN BẨY CAPIT: gói khai báo ≠ gói lệnh THẬT sẽ đi ra ───────────────────────────────
# `DNSEBroker.place_order` (brokers.py:629-644) KHÔNG tin thẳng `order.loan_package_id`: nó gọi
# `_validate_lever_package(symbol, want)` trước; gói không hợp lệ cho mã đó ⇒ HẠ về gói default
# account ⇒ lệnh đi ra KHÔNG có đòn bẩy ⇒ sức mua NHỎ HƠN (gói 1840 initialRate 0,5 = gấp đôi
# 1841). Gate đo bằng gói KHAI BÁO sẽ tưởng có sức mua gấp đôi ⇒ ĐÚNG kiểu "list-rồi-đợi-tiền"
# mà gate này sinh ra để ngăn, chỉ khác nhánh code.
print("\n[O] ĐÒN BẨY CAPIT — gói vay phải giải qua _validate_lever_package như place_order")
LEVER, DEFLT = 1840, 1841
BP = {LEVER: 200_000_000, DEFLT: 80_000_000}      # gói 1840 initialRate 0,5 ⇒ sức mua gấp đôi
need_1000 = 1000 * 100_000 * (1 + FEE_RATE)       # 100.075.000đ

print("[O1] gói 1840 HỢP LỆ cho FPT → đo bằng ĐÚNG 1840 (200M) → OK, không hạ oan đòn bẩy")
b = StubBroker(BP, cash=20_000_000, lever_valid={"FPT": {LEVER}}, account_default=DEFLT)
v = check_plan_funding(plan([order("FPT", 1000, 100_000, loan_package_id=LEVER)]), b, "live")
check("action == OK", v["action"] == "OK", f"{v['action']}: {v['reason']}")
check("đo bằng gói 1840 (gói lệnh thật dùng)", any(c[2] == LEVER for c in b.calls), b.calls)
check("KHÔNG đo bằng gói default 1841", not any(c[2] == DEFLT for c in b.calls), b.calls)
check("có gọi _validate_lever_package(FPT, 1840)", ("FPT", LEVER) in b.validate_calls,
      b.validate_calls)

print("[O2] ★ gói 1840 KHÔNG hợp lệ cho SAB → place_order HẠ về 1841 (80M) → Σ 100,075M > 80M")
print("     ⇒ phải CHẶN. Đo theo gói KHAI BÁO (200M) sẽ cho OK = RỦI RO DƯỚI-CHẶN.")
b = StubBroker(BP, cash=20_000_000, lever_valid={"FPT": {LEVER}}, account_default=DEFLT)
v = check_plan_funding(plan([order("SAB", 1000, 100_000, loan_package_id=LEVER)]), b, "live")
check("action == BLOCK", v["action"] == "BLOCK", f"{v['action']}: {v['reason']}")
check("đo bằng gói FALLBACK 1841", any(c[2] == DEFLT for c in b.calls), b.calls)
check("KHÔNG hề đo bằng gói 1840 (gói lệnh KHÔNG đi ra được)",
      not any(c[2] == LEVER for c in b.calls), b.calls)
check("sức mua báo cáo = 80M (không phải 200M)", v["buying_power_vnd"] == 80_000_000,
      v["buying_power_vnd"])
check("utilization ≈ 1,2509 (100,075/80)", abs(v["utilization"] - need_1000 / 80_000_000) < 1e-9,
      v["utilization"])

print("[O3] broker KHÔNG có _validate_lever_package → KHÔNG được giả định đòn bẩy áp được:")
print("     đo bằng gói default account (80M) → BLOCK (fail-safe, không đo thừa sức mua)")
b = StubBroker(BP, cash=200_000_000, account_default=DEFLT, no_validate=True)
v = check_plan_funding(plan([order("SAB", 1000, 100_000, loan_package_id=LEVER)]), b, "live")
check("action == BLOCK", v["action"] == "BLOCK", f"{v['action']}: {v['reason']}")
check("đo bằng gói default 1841", any(c[2] == DEFLT for c in b.calls), b.calls)

print("[O4] _validate_lever_package ném exception → không nổ, đo bằng gói default → BLOCK")
b = StubBroker(BP, cash=200_000_000, account_default=DEFLT, raise_on_validate=True)
v = check_plan_funding(plan([order("SAB", 1000, 100_000, loan_package_id=LEVER)]), b, "live")
check("không raise, action == BLOCK", v["action"] == "BLOCK", f"{v['action']}: {v['reason']}")
check("đo bằng gói default 1841", any(c[2] == DEFLT for c in b.calls), b.calls)

print("[O5] plan HỖN HỢP: FPT@1840 hợp lệ (0,50) + SAB@1840 bị hạ về 1841 (0,60) → Σ 1,10 → BLOCK")
b = StubBroker(BP, cash=20_000_000, lever_valid={"FPT": {LEVER}}, account_default=DEFLT)
v = check_plan_funding(plan([order("FPT", 1000, 100_000, loan_package_id=LEVER),
                             order("SAB", 1200, 40_000, loan_package_id=LEVER)]), b, "live")
check("action == BLOCK", v["action"] == "BLOCK", f"{v['action']}: {v['reason']}")
check("tách ĐÚNG 2 nhóm gói vay (1840 + 1841)", len(v["groups"]) == 2,
      [(g["loan_package_id"], g["package_source"]) for g in v["groups"]])
check("FPT đo bằng 1840", ("FPT", 100_000, LEVER) in b.calls, b.calls)
check("SAB đo bằng 1841", ("SAB", 40_000, DEFLT) in b.calls, b.calls)
check("utilization ≈ 1,10", abs(v["utilization"] - 1.1010) < 1e-3, v["utilization"])

# ── P. TÍN DỤNG JIT: lệnh BÁN cùng plan chạy TRƯỚC cấp vốn cho lệnh mua (2026-08-07) ──────
# Lỗ hổng thật: cơ chế L2 JIT-unpark (LIVE 2026-08-06) bán PARK ĐỂ tự cấp vốn cho lệnh mua cùng
# plan, nhưng nhánh (1) chỉ đo pp0Buy lúc gate chạy (chưa lệnh bán nào khớp) ⇒ CHẶN OAN sạch plan.
BUY = order("FPT", 1000, 100_000)                       # need = 100.075.000đ (đã gồm phí)
NEED_FPT = 1000 * 100_000 * (1 + FEE_RATE)
SELL_NET = 700 * 60_000 * (1 - FEE_RATE)                # 41.968.500đ net phí

print("\n[P1] ★ (a) mua 100,075tr / sức mua 60tr — THIẾU nếu không tính lệnh bán;")
print("     bán VNM 42tr (priority 1) chạy TRƯỚC mua (priority 5) ⇒ ĐỦ ⇒ phải KHÔNG chặn")
v = check_plan_funding(plan([order("VNM", 700, 60_000, side="sell", priority=1),
                             order("FPT", 1000, 100_000, priority=5)]),
                       StubBroker({None: 60_000_000}, cash=60_000_000), "live")
check("action == OK (trước fix: BLOCK)", v["action"] == "OK", f"{v['action']}: {v['reason']}")
check("tín dụng JIT = net phí 41.968.500đ", abs(v["jit_sell_credit_vnd"] - SELL_NET) < 1,
      v["jit_sell_credit_vnd"])
check("đếm đúng 1 lệnh bán đủ điều kiện", v["jit_sell_orders"] == 1, v["jit_sell_orders"])
check("utilization = need/(bp+credit) ≈ 0,9814",
      abs(v["utilization"] - NEED_FPT / (60_000_000 + SELL_NET)) < 1e-9, v["utilization"])
check("reason nêu rõ có tín dụng JIT", "tín dụng JIT" in v["reason"], v["reason"])

print("\n[P2] ★★ (b) REGRESSION GUARD — CÙNG SỐ TIỀN nhưng lệnh bán priority 7 > mua 5")
print("      (bán chạy SAU mua ⇒ lúc mua chưa có đồng nào) ⇒ PHẢI VẪN CHẶN")
v = check_plan_funding(plan([order("VNM", 700, 60_000, side="sell", priority=7),
                             order("FPT", 1000, 100_000, priority=5)]),
                       StubBroker({None: 60_000_000}, cash=60_000_000), "live")
check("action == BLOCK (KHÔNG được nới)", v["action"] == "BLOCK", f"{v['action']}: {v['reason']}")
check("tín dụng JIT = 0", v["jit_sell_credit_vnd"] == 0, v["jit_sell_credit_vnd"])

print("\n[P3] ★★ BIÊN: bán priority 5 BẰNG mua 5 (cùng lượt, chưa khớp) ⇒ PHẢI VẪN CHẶN")
print("      (luật là `<` NGHIÊM NGẶT, không phải `≤`)")
v = check_plan_funding(plan([order("VNM", 700, 60_000, side="sell", priority=5),
                             order("FPT", 1000, 100_000, priority=5)]),
                       StubBroker({None: 60_000_000}, cash=60_000_000), "live")
check("action == BLOCK", v["action"] == "BLOCK", f"{v['action']}: {v['reason']}")
check("tín dụng JIT = 0", v["jit_sell_credit_vnd"] == 0, v["jit_sell_credit_vnd"])

print("\n[P4] ★ (c) VƯỢT THẬT kể cả sau khi cộng TOÀN BỘ tiền bán ⇒ PHẢI VẪN CHẶN")
print("      mua 100,075tr / sức mua 20tr + bán 18tr (net 17,99tr) = 37,99tr")
v = check_plan_funding(plan([order("VNM", 300, 60_000, side="sell", priority=1),
                             order("FPT", 1000, 100_000, priority=5)]),
                       StubBroker({None: 20_000_000}, cash=20_000_000), "live")
check("action == BLOCK", v["action"] == "BLOCK", f"{v['action']}: {v['reason']}")
check("có cộng tín dụng nhưng vẫn không đủ",
      v["jit_sell_credit_vnd"] > 0 and v["utilization"] > 1.0,
      (v["jit_sell_credit_vnd"], v["utilization"]))

print("\n[P5] ★ REPLAY PLAN THẬT bị chặn oan — ZaloPay 2026-08-07 (8 bán PARK prio 0 + DRI prio 1)")
ZP_SELLS = [("BID", 300, 37_900.0), ("CTG", 300, 31_350.0), ("HDB", 200, 26_550.0),
            ("MBB", 400, 23_900.0), ("TCB", 300, 29_200.0), ("VCB", 400, 59_000.0),
            ("VHM", 300, 77_100.0), ("VPB", 300, 25_150.0)]
zp = plan([order(t, q, px, side="sell", priority=0) for t, q, px in ZP_SELLS]
          + [order("DRI", 1800, 13_100.0, priority=1)], account="ZaloPay")
ZP_GROSS = sum(q * px for _, q, px in ZP_SELLS)                      # 98.680.000đ
v = check_plan_funding(zp, StubBroker({None: 5_000_000}, cash=5_000_000), "live")
check("Σ tiền bán gộp = 98.680.000đ", abs(ZP_GROSS - 98_680_000) < 1, ZP_GROSS)
check("tín dụng JIT = 98.680.000 × (1−0,075%)",
      abs(v["jit_sell_credit_vnd"] - ZP_GROSS * (1 - FEE_RATE)) < 1, v["jit_sell_credit_vnd"])
check("đếm đủ 8 lệnh bán", v["jit_sell_orders"] == 8, v["jit_sell_orders"])
check("action == OK — plan TỰ CẤP VỐN không còn bị chặn oan", v["action"] == "OK",
      f"{v['action']}: {v['reason']}")
print(f"      → sức mua 5,00tr + JIT {v['jit_sell_credit_vnd']/1e6:.2f}tr "
      f"vs Σ mua {v['need_vnd']/1e6:.2f}tr ⇒ util {v['utilization']*100:.1f}%")
v0 = check_plan_funding(plan([order("DRI", 1800, 13_100.0, priority=1)], account="ZaloPay"),
                        StubBroker({None: 5_000_000}, cash=5_000_000), "live")
check("KHÔNG có lệnh bán thì VẪN chặn (đúng — lúc đó tiền thật sự không tồn tại)",
      v0["action"] == "BLOCK", f"{v0['action']}: {v0['reason']}")

print("\n[P6] ★★ CHỐNG CHE GIẤU: cộng TỈ LỆ TIÊU THỤ (Σ), KHÔNG phải max, KHÔNG cộng gộp tiền.")
print("      nhóm A (1841) need 100,075tr / bp 10tr  ← vượt THẬT")
print("      nhóm B (1840) need 1,00tr   / bp 1.000tr ← thừa mứa")
print("      Cộng gộp plan-wide sẽ cho OK OAN (101tr ≤ 1.010tr+50tr); Σ tỉ lệ phải CHẶN.")
# resolve SAB→1841: từ 2026-08-07 `_effective_loan_package` giải gói theo MÃ cho MỌI lệnh không
# có đòn bẩy chỉ định (không còn chỉ `cash_only`), nên stub phải khai ánh xạ để nhóm ra 1841.
b = StubBroker({DEFLT: 10_000_000, LEVER: 1_000_000_000}, cash=10_000_000,
               resolve={"SAB": DEFLT}, lever_valid={"FPT": {LEVER}}, account_default=DEFLT)
v = check_plan_funding(plan([order("VNM", 1000, 50_000, side="sell", priority=0),
                             order("SAB", 1000, 100_000, priority=5),
                             order("FPT", 10, 100_000, loan_package_id=LEVER, priority=5)]),
                       b, "live")
check("action == BLOCK (nhóm A vượt, B KHÔNG gánh hộ được)", v["action"] == "BLOCK",
      f"{v['action']}: {v['reason']}")
gA = [g for g in v["groups"] if g["loan_package_id"] == DEFLT][0]
gB = [g for g in v["groups"] if g["loan_package_id"] == LEVER][0]
check("nhóm A vẫn util(thô) > 1 — tiêu quá cả hũ chung", gA["utilization"] > 1.0,
      gA["utilization"])
check("nhóm B util(thô) ≈ 0 nhưng KHÔNG gánh hộ được cho A", gB["utilization"] < 0.01,
      gB["utilization"])
check("hũ chung = min pp0Buy = 10tr (KHÔNG phải 10tr + 1.000tr)",
      v["shared_pot_vnd"] == 10_000_000, v["shared_pot_vnd"])
check("Σ tỉ lệ thô ≈ 10,0085 (A 10,0075 + B 0,001)", abs(v["raw_utilization"] - 10.0085) < 1e-3,
      v["raw_utilization"])
check("kể cả sau khi cộng TOÀN BỘ tín dụng JIT vào trần vẫn CHẶN",
      v["utilization"] > 1.0, (v["utilization"], v["headroom_ratio"]))

print("\n[P7] ★ FAIL-SAFE: lệnh KHÔNG có field `priority` (object cũ) ⇒ mặc định 5 cả hai bên")
print("      ⇒ 5 < 5 sai ⇒ 0 tín dụng ⇒ hành vi Y HỆT trước khi có patch")
o_sell = order("VNM", 700, 60_000, side="sell"); del o_sell.priority
o_buy = order("FPT", 1000, 100_000); del o_buy.priority
v = check_plan_funding(plan([o_sell, o_buy]),
                       StubBroker({None: 60_000_000}, cash=60_000_000), "live")
check("action == BLOCK (không tự nới khi thiếu thông tin thứ tự)", v["action"] == "BLOCK",
      f"{v['action']}: {v['reason']}")
check("tín dụng JIT = 0", v["jit_sell_credit_vnd"] == 0, v["jit_sell_credit_vnd"])

# ── Q. HŨ TIỀN CHUNG: nhiều nhóm gói vay KHÔNG có tiền riêng (bug thật 2026-08-10) ───────
# Sự cố: ZaloPay cash-only, 4 lệnh mua tách 2 nhóm gói vay, CẢ HAI nhóm trả về CÙNG pp0Buy
# 5.818.854đ (một hũ tiền, hai cách nhìn). Bản 08-07 đặt hũ ĐẦY ĐỦ vào mẫu số TỪNG nhóm rồi
# mới chia JIT theo tỉ lệ ⇒ tín dụng JIT bị chia loãng đúng số nhóm ⇒ util 105,6% ⇒ CHẶN OAN
# plan đã duyệt (tỉ lệ THẬT 54,6%). Nhóm Q khoá cả hai chiều: không chặn oan, và không nới.
print("\n" + "=" * 78)
print("[Q] HŨ TIỀN CHUNG giữa các nhóm gói vay (sự cố thật ZaloPay 2026-08-10)")
print("=" * 78)

ZP10_SELLS = [("BID", 600, 39_050.0), ("CTG", 600, 32_500.0), ("HDB", 200, 26_550.0),
              ("MBB", 900, 24_150.0), ("TCB", 600, 29_700.0), ("VCB", 700, 59_700.0),
              ("VHM", 300, 73_000.0), ("VPB", 500, 25_000.0)]
ZP10_BUYS = [("DRI", 1900, 13_000.0), ("POW", 1800, 13_400.0),
             ("SCL", 1000, 24_200.0), ("SSI", 800, 24_450.0)]
PP0 = 5_818_854.0                      # pp0Buy ĐO THẬT trên broker sống, GIỐNG HỆT ở cả 2 nhóm
ZP10_RESOLVE = {"DRI": 1258, "SCL": 1258, "POW": 1826, "SSI": 1826}   # đúng nhóm đo được 09:1x
ZP10_JIT = sum(q * px for _, q, px in ZP10_SELLS) * (1 - FEE_RATE)
ZP10_NEED = sum(q * px for _, q, px in ZP10_BUYS) * (1 + FEE_RATE)


def zp10_plan(with_sells=True, buys=ZP10_BUYS):
    os_ = [order(t, q, px, side="sell", priority=0) for t, q, px in ZP10_SELLS] if with_sells else []
    return plan(os_ + [order(t, q, px, priority=1) for t, q, px in buys], account="ZaloPay")


def zp10_broker():
    return StubBroker({1258: PP0, 1826: PP0}, cash=PP0, resolve=dict(ZP10_RESOLVE))


print("\n[Q1] ★★ REPLAY THẬT — 4 lệnh mua tách 2 nhóm (1258/1826) CÙNG pp0Buy 5.818.854đ,")
print("     8 lệnh bán PARK prio 0 cấp 163,86tr ⇒ tiêu thụ THẬT 54,6% ⇒ PHẢI KHÔNG CHẶN")
v = check_plan_funding(zp10_plan(), zp10_broker(), "live")
check("Σ need = 92.649.435đ", abs(v["need_vnd"] - 92_649_435) < 1, v["need_vnd"])
check("tín dụng JIT = 163.862.011đ", abs(v["jit_sell_credit_vnd"] - 163_862_011.25) < 1,
      v["jit_sell_credit_vnd"])
check("tách đúng 2 nhóm gói vay", len(v["groups"]) == 2,
      [(g["loan_package_id"], g["need_vnd"]) for g in v["groups"]])
check("nhóm 1258 need 48.936.675đ (DRI+SCL)",
      abs([g for g in v["groups"] if g["loan_package_id"] == 1258][0]["need_vnd"] - 48_936_675) < 1)
check("nhóm 1826 need 43.712.760đ (POW+SSI)",
      abs([g for g in v["groups"] if g["loan_package_id"] == 1826][0]["need_vnd"] - 43_712_760) < 1)
check("★ action == OK (bản 08-07: BLOCK OAN)", v["action"] == "OK", f"{v['action']}: {v['reason']}")
check("★ util == tỉ lệ THẬT cấp plan 54,6% (bản 08-07 ra 105,6%)",
      abs(v["utilization"] - ZP10_NEED / (PP0 + ZP10_JIT)) < 1e-12
      and abs(v["utilization"] - 0.546) < 1e-3, v["utilization"])
check("★ hũ chung đếm MỘT lần: 5.818.854đ (bản 08-07 báo 11.637.708đ = ×2)",
      v["shared_pot_vnd"] == PP0 and v["buying_power_vnd"] == PP0,
      (v["shared_pot_vnd"], v["buying_power_vnd"]))
check("reason KHÔNG chứa con số đếm đôi 11.637.708", "11,637,708" not in v["reason"], v["reason"])
print(f"      → hũ {PP0/1e6:.2f}tr + JIT {ZP10_JIT/1e6:.2f}tr vs Σ mua {v['need_vnd']/1e6:.2f}tr "
      f"⇒ util {v['utilization']*100:.1f}%")

print("\n[Q1b] ★★ CHỨNG MINH NGƯỢC — công thức CŨ (hũ lặp ở mọi mẫu số + JIT chia tỉ lệ) trên")
print("      CHÍNH dữ liệu này ra 1,0556 > 1 ⇒ ca [Q1] thật sự khoá được bug, không phải khẳng định suông")
old_u = sum(g["need_vnd"] / (PP0 + ZP10_JIT * g["need_vnd"] / v["need_vnd"]) for g in v["groups"])
check("công thức cũ ra ≈ 1,0556 (đã CHẶN OAN)", abs(old_u - 1.0556) < 1e-3, old_u)
check("công thức mới ra < 1 trên cùng dữ liệu", v["utilization"] < 1.0, v["utilization"])

print("\n[Q2] ★★ REGRESSION — CÙNG 2 nhóm cùng hũ nhưng BỎ HẾT lệnh bán (JIT=0):")
print("      92,65tr > hũ 5,82tr ⇒ PHẢI VẪN CHẶN (tiền thật sự không tồn tại)")
v2 = check_plan_funding(zp10_plan(with_sells=False), zp10_broker(), "live")
check("action == BLOCK", v2["action"] == "BLOCK", f"{v2['action']}: {v2['reason']}")
check("tín dụng JIT = 0", v2["jit_sell_credit_vnd"] == 0, v2["jit_sell_credit_vnd"])

print("\n[Q3] ★★★ LỖ HỔNG mà phương án `max` sẽ mở ra — 2 nhóm CÙNG hũ 100tr, mỗi nhóm tiêu")
print("      60tr (60% hũ). max(0,60; 0,60) = 0,60 ⇒ 'OK' OAN dù plan cần 120% số tiền đang có.")
print("      Σ tỉ lệ = 1,20 ⇒ PHẢI CHẶN. Đây là lý do giữ Σ, chỉ sửa chỗ đếm đôi hũ + JIT.")
SHARED = 100_000_000.0
b = StubBroker({1258: SHARED, 1826: SHARED}, cash=SHARED,
               resolve={"DRI": 1258, "POW": 1826})
gross60 = 60_000_000 / (1 + FEE_RATE)
v3 = check_plan_funding(plan([order("DRI", 1, gross60, priority=1),
                              order("POW", 1, gross60, priority=1)], account="ZaloPay"),
                        b, "live")
check("MỖI nhóm riêng lẻ đều DƯỚI 1 (max sẽ cho OK)",
      all(g["utilization"] < 1.0 for g in v3["groups"]),
      [g["utilization"] for g in v3["groups"]])
check("★ action == BLOCK (Σ = 1,20)", v3["action"] == "BLOCK", f"{v3['action']}: {v3['reason']}")
check("util ≈ 1,20", abs(v3["utilization"] - 1.2) < 1e-6, v3["utilization"])

print("\n[Q4] BIÊN `≤` trên hũ chung: Σ mua ĐÚNG BẰNG hũ + JIT → OK; thiếu 1đ nữa → BLOCK")
POT4, JIT4_GROSS = 20_000_000.0, 80_000_000.0
jit4 = JIT4_GROSS * (1 - FEE_RATE)
exact_gross = (POT4 + jit4) / (1 + FEE_RATE)          # chia đôi cho 2 nhóm
b4 = StubBroker({1258: POT4, 1826: POT4}, cash=POT4, resolve={"DRI": 1258, "POW": 1826})
v4 = check_plan_funding(plan([order("VNM", 1, JIT4_GROSS, side="sell", priority=0),
                              order("DRI", 1, exact_gross / 2, priority=1),
                              order("POW", 1, exact_gross / 2, priority=1)],
                             account="ZaloPay"), b4, "live")
check("hoà ĐÚNG BẰNG → OK", v4["action"] == "OK", f"{v4['action']} u={v4['utilization']!r}")
b4b = StubBroker({1258: POT4 - 1, 1826: POT4 - 1}, cash=POT4,
                 resolve={"DRI": 1258, "POW": 1826})
v4b = check_plan_funding(plan([order("VNM", 1, JIT4_GROSS, side="sell", priority=0),
                               order("DRI", 1, exact_gross / 2, priority=1),
                               order("POW", 1, exact_gross / 2, priority=1)],
                              account="ZaloPay"), b4b, "live")
check("hũ thiếu 1đ → BLOCK", v4b["action"] == "BLOCK", f"{v4b['action']} u={v4b['utilization']!r}")

print("\n[Q5] HŨ KHÁC NHAU (margin, gói 1840 đòn bẩy 2× gói 1841): hũ chung = min = 80tr,")
print("      JIT quy đổi 1:1 trên hũ ít đòn bẩy nhất = CẬN THẬN TRỌNG, không bao giờ nới")
b5 = StubBroker({LEVER: 200_000_000, DEFLT: 80_000_000}, cash=20_000_000,
                lever_valid={"FPT": {LEVER}}, account_default=DEFLT, resolve={"SAB": DEFLT})
v5 = check_plan_funding(plan([order("FPT", 1000, 100_000, loan_package_id=LEVER, priority=5),
                              order("SAB", 1200, 40_000, priority=5)]), b5, "live")
check("hũ chung = 80tr (min), KHÔNG phải 280tr (Σ)", v5["shared_pot_vnd"] == 80_000_000,
      v5["shared_pot_vnd"])
check("không có lệnh bán ⇒ trần = 1,0 ⇒ hành vi Y HỆT [O5] (BLOCK, util 1,101)",
      v5["action"] == "BLOCK" and abs(v5["utilization"] - 1.1010) < 1e-3,
      (v5["action"], v5["utilization"]))

print("\n[Q6] NHÓM KHÔNG ĐO ĐƯỢC lẫn nhóm đo được: JIT bị CHIẾT KHẤU theo tỉ trọng nhu cầu đo")
print("      được (nhóm không đo không nằm trong Σ tỉ lệ ⇒ không được hưởng phần tín dụng của nó)")
b6 = StubBroker({1258: 10_000_000}, cash=10_000_000, resolve={"DRI": 1258, "POW": 1826})
v6 = check_plan_funding(plan([order("VNM", 1, 100_000_000, side="sell", priority=0),
                              order("DRI", 1, 10_000_000, priority=1),
                              order("POW", 1, 10_000_000, priority=1)],
                             account="ZaloPay"), b6, "live")
check("có 1 nhóm không đo được ⇒ đi nhánh cận ngoài", v6["action"] in ("UNVERIFIED", "BLOCK"),
      v6["action"])
check("JIT hiệu lực = 50% JIT gộp (1/2 nhu cầu đo được)",
      abs(v6["jit_credit_effective_vnd"] - v6["jit_sell_credit_vnd"] * 0.5) < 1,
      (v6["jit_credit_effective_vnd"], v6["jit_sell_credit_vnd"]))

print("\n" + "=" * 78)
print(f"KẾT QUẢ: {PASS} PASS / {FAIL} FAIL")
print("=" * 78)
sys.exit(1 if FAIL else 0)
