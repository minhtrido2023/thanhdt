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
def order(ticker, qty, price, side="buy", cash_only=False, loan_package_id=None):
    o = types.SimpleNamespace()
    o.ticker, o.qty, o.ref_price, o.side = ticker, qty, price, side
    o.cash_only, o.loan_package_id = cash_only, loan_package_id
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

print("\n" + "=" * 78)
print(f"KẾT QUẢ: {PASS} PASS / {FAIL} FAIL")
print("=" * 78)
sys.exit(1 if FAIL else 0)
