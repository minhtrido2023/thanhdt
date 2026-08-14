#!/usr/bin/env python3
"""Selfcheck cho `trading_bot/plan_cash_commitment.py` — headroom tiền cho luồng sinh lệnh
thứ hai (injector 20:30) sau khi luồng thứ nhất (DollarBill ~19:0x) đã dự chi.

Chạy:  python3 plan_cash_commitment_selfcheck.py
       env -u TZ python3 plan_cash_commitment_selfcheck.py    (phải cho kết quả Y HỆT)

PHỤ THUỘC MÔI TRƯỜNG (khai theo skill verify-before-done):
  • KHÔNG mạng, KHÔNG broker thật, KHÔNG credential — broker là stub trong chính file này.
  • KHÔNG đọc/ghi file nào (không plan JSON, không state file).
  • KHÔNG phụ thuộc TZ: module không gọi datetime/date ở bất kỳ nhánh nào (§16
    coding_guidelines) — case R chứng minh bằng cách chạy lại chính selfcheck dưới 3 TZ.
  • Phụ thuộc DUY NHẤT: import được `trading_bot.plan_funding_gate` (A1, đã LIVE).

Phủ:
  A. plan rỗng                              → headroom = toàn bộ sức mua
  B. plan đã dự chi                         → headroom = (1−U) × pp0Buy
  C. replay THẬT 07-24 (49,9M vs 49,1M)     → cận tiền mặt bắt được phần thiếu 0,78M
  D. headroom < 1 lô                        → SKIP_NO_CASH, order=None
  E. headroom giữa chừng                    → SHRINK về bội số lô, không phải bỏ phiên
  F. headroom dư                            → PASS, qty nguyên vẹn
  G. BIÊN: headroom == ĐÚNG chi phí lệnh    → PASS (luật `≤`)
  H. BIÊN: thiếu đúng 1 đồng                → SHRINK/SKIP, không PASS
  I. phí 0,075% được tính vào chi phí       → chặn khi chỉ vượt nhờ phần phí
  J. pp0Buy không đo được                   → cận TIỀN MẶT, KHÔNG nhân đòn bẩy
  K. broker chết hoàn toàn                  → headroom None → SKIP (fail-safe, KHÔNG chèn)
  L. lệnh mua thiếu giá trong plan          → headroom None (không coi là chi phí 0)
  M. tiền BÁN trong plan được cộng vào cận  (ppse cộng tiền bán T+0)
  N. mode=paper                             → PASS_NOT_LIVE, không cản trở
  O. gói vay cash_only giải ĐÚNG hàm broker (bẫy TV1 1122 vs 1841)
  P. A1 verdict=BLOCK                       → headroom = 0 tuyệt đối
  Q. re-plan nuốt mất tranche đã chèn       → replan_dropped_injection = True
  R. bất biến TZ (chạy lại dưới 3 TZ)
"""
import os
import subprocess
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trading_bot.plan_cash_commitment import (      # noqa: E402
    FEE_RATE, cap_qty_to_headroom, commitment_summary, gate_injected_order,
    order_cost_vnd, replan_dropped_injection, residual_headroom)

PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} — {detail}")


# ── stub: đúng những gì module đọc, không hơn ────────────────────────────────────────────
def order(ticker, qty, price, side="buy", book="BAL", oid=None, cash_only=False,
          loan_package_id=None):
    o = types.SimpleNamespace()
    o.id = oid or f"{side.upper()}-{ticker}-00"
    o.ticker, o.qty, o.ref_price, o.side, o.book = ticker, qty, price, side, book
    o.cash_only, o.loan_package_id = cash_only, loan_package_id
    return o


def plan(orders, account="SpaceX"):
    p = types.SimpleNamespace()
    p.orders, p.account, p.plan_date = orders, account, "2026-08-05"
    return p


class Broker:
    """pp0Buy theo gói vay; cash riêng. `resolve` mô phỏng `_resolve_loan_package_id`."""

    def __init__(self, pp_by_package=None, cash=0.0, resolve=None, raise_pp=False,
                 raise_cash=False, default_package=1841):
        self.pp = pp_by_package or {}
        self.cash = cash
        self.resolve = resolve or {}
        self.raise_pp, self.raise_cash = raise_pp, raise_cash
        self.client = types.SimpleNamespace(loan_package_id=default_package)
        self.calls = []

    def get_buying_power(self, symbol, price, loan_package_id=None):
        # `ppse` THẬT với loan_package_id=None trả số của gói MẶC ĐỊNH account, không phải
        # rỗng. Stub sai chỗ này từng làm case B "PASS nhầm lý do": nhánh pp0Buy im lặng
        # rơi về cận tiền mặt mà vẫn ra đúng con số vì cash == pp0Buy trong ca đó.
        self.calls.append((symbol, price, loan_package_id))
        if self.raise_pp:
            raise RuntimeError("ppse down")
        key = self.client.loan_package_id if loan_package_id is None else loan_package_id
        return self.pp.get(key)

    def get_cash(self):
        if self.raise_cash:
            raise RuntimeError("balances down")
        return self.cash

    def _resolve_loan_package_id(self, symbol):
        return self.resolve.get(symbol, self.client.loan_package_id)


LOT = 100
DISC = dict(id="BUY-TV1-DISC-2026-08-05", ticker="TV1", side="buy", qty=200,
            ref_price=19900, limit_price_vnd=19900, book="DISCRETIONARY_SPECIAL",
            cash_only=True)
DISC_COST = 200 * 19900 * (1 + FEE_RATE)          # 3.982.985đ


def run():
    print("=" * 78)
    print("SELFCHECK plan_cash_commitment.py — headroom tiền giữa 2 luồng sinh lệnh")
    print("=" * 78)

    # A. plan rỗng → headroom = toàn bộ sức mua
    print("\n[A] plan rỗng → headroom = toàn bộ sức mua")
    b = Broker(pp_by_package={1122: 50_000_000}, cash=50_000_000,
               resolve={"TV1": 1122})
    h = residual_headroom(plan([]), b, "live", "TV1", 19900, cash_only=True)
    check("headroom = 50M", abs(h["headroom_vnd"] - 50_000_000) < 1, h)
    check("basis = pp0buy_residual", h["basis"] == "pp0buy_residual", h["basis"])
    check("committed = 0", h["committed_vnd"] == 0, h["committed_vnd"])

    # B. plan đã dự chi → (1−U) × pp0Buy.  cash CỐ Ý ≠ pp0Buy (cash 8M << pp0Buy 50M, đúng
    # kiểu account margin) để hai công thức KHÔNG thể ra cùng số ⇒ test phân biệt được nhánh.
    print("\n[B] plan đã dự chi 20M / sức mua 50M (cash chỉ 8M) → headroom theo pp0Buy")
    orders = [order("PVT", 1000, 20_000, book="CAPIT")]   # 20M + phí
    b = Broker(pp_by_package={1122: 50_000_000, 1841: 50_000_000}, cash=8_000_000,
               resolve={"TV1": 1122})
    h = residual_headroom(plan(orders), b, "live", "TV1", 19900, cash_only=True)
    committed = 1000 * 20_000 * (1 + FEE_RATE)
    expect = (1 - committed / 50_000_000) * 50_000_000
    check(f"headroom ≈ {expect:,.0f}", abs(h["headroom_vnd"] - expect) < 1,
          f"{h['headroom_vnd']} vs {expect}")
    check("basis = pp0buy_residual (KHÔNG rơi nhầm về cận tiền mặt 8M)",
          h["basis"] == "pp0buy_residual", h)
    check("committed đúng phần V2.4", abs(h["committed_vnd"] - committed) < 1, h)

    # C. REPLAY sự cố THẬT 2026-07-24 SpaceX: V2.4 45,9M + TV1 3,98M vs cash 49,125M
    print("\n[C] REPLAY THẬT 07-24: V2.4 45,9M + tranche TV1 3,98M vs cash 49.125.163đ")
    v24 = [order("PVT", 1000, 45_900, book="CAPIT", oid="BUY-PVT-00")]  # 45,9M
    b = Broker(pp_by_package={}, cash=49_125_163, resolve={"TV1": 1122})  # pp0Buy đo hụt
    o, rec = gate_injected_order(dict(DISC), plan(v24), b, "live", LOT)
    committed = 45_900_000 * (1 + FEE_RATE)
    check("cận tiền mặt được dùng", rec["basis"] == "cash_bound", rec["basis"])
    check("headroom = cash − đã dự chi (~3,19M < 3,98M cần)",
          abs(rec["headroom_vnd"] - (49_125_163 - committed)) < 1, rec["headroom_vnd"])
    check("KHÔNG chèn đủ 200cp (đúng: 07-24 thiếu 0,78M)", rec["qty_after"] < 200,
          rec["qty_after"])
    check("SHRINK về 100cp thay vì bỏ hẳn", o is not None and rec["qty_after"] == 100, rec)
    check("qty đã ghi vào order dict", o["qty"] == 100 if o else False, o)
    # kiểm chứng số học sự cố: nếu KHÔNG có gate, tổng vượt cash đúng ~0,78M
    # Con số sự cố "~0,78M" trong báo cáo là phần vượt TRƯỚC phí (754.837đ); cộng phí
    # 0,075% của cả hai chân thành 792.247đ. Neo cả hai để không ai đọc lệch cơ sở.
    gross_no_gate = 45_900_000 + 200 * 19900
    total_no_gate = committed + DISC_COST
    check("không gate ⇒ vượt cash 754.837đ (trước phí, = '~0,78M' của báo cáo)",
          abs((gross_no_gate - 49_125_163) - 754_837) < 1, gross_no_gate - 49_125_163)
    check("không gate ⇒ vượt cash 792.247đ (sau phí 0,075%)",
          abs((total_no_gate - 49_125_163) - 792_247) < 1, total_no_gate - 49_125_163)

    # D. headroom < 1 lô → SKIP
    print("\n[D] headroom 1,0M < 1 lô (≈1,99M) → SKIP_NO_CASH")
    b = Broker(pp_by_package={}, cash=1_000_000, resolve={"TV1": 1122})
    o, rec = gate_injected_order(dict(DISC), plan([]), b, "live", LOT)
    check("order = None", o is None, o)
    check("action = SKIP_NO_CASH", rec["action"] == "SKIP_NO_CASH", rec["action"])
    check("có human_note nêu rõ phải re-plan nếu muốn ưu tiên",
          "re-plan" in rec["human_note"], rec.get("human_note"))

    # E. SHRINK
    print("\n[E] headroom đủ 100cp nhưng không đủ 200cp → SHRINK")
    b = Broker(pp_by_package={}, cash=3_000_000, resolve={"TV1": 1122})
    o, rec = gate_injected_order(dict(DISC), plan([]), b, "live", LOT)
    check("action = SHRINK", rec["action"] == "SHRINK", rec["action"])
    check("qty 200→100", rec["qty_before"] == 200 and rec["qty_after"] == 100, rec)
    check("ghi lại qty gốc để audit", o.get("cash_gate_shrunk_from_qty") == 200, o)

    # F. PASS
    print("\n[F] headroom dư → PASS nguyên vẹn")
    b = Broker(pp_by_package={1122: 100_000_000}, cash=100_000_000, resolve={"TV1": 1122})
    o, rec = gate_injected_order(dict(DISC), plan([]), b, "live", LOT)
    check("action = PASS", rec["action"] == "PASS", rec["action"])
    check("qty giữ 200", o["qty"] == 200, o["qty"])

    # G/H/I. biên + phí
    print("\n[G/H/I] biên bằng đúng chi phí / thiếu 1 đồng / phần phí")
    b = Broker(pp_by_package={}, cash=DISC_COST, resolve={"TV1": 1122})
    o, rec = gate_injected_order(dict(DISC), plan([]), b, "live", LOT)
    check("G: headroom == đúng chi phí → PASS 200cp", rec["action"] == "PASS", rec)
    b = Broker(pp_by_package={}, cash=DISC_COST - 1, resolve={"TV1": 1122})
    o, rec = gate_injected_order(dict(DISC), plan([]), b, "live", LOT)
    check("H: thiếu 1đ → KHÔNG PASS 200cp", rec["qty_after"] == 100, rec)
    # I: đủ tiền cho giá gốc nhưng KHÔNG đủ khi cộng phí
    b = Broker(pp_by_package={}, cash=200 * 19900, resolve={"TV1": 1122})
    o, rec = gate_injected_order(dict(DISC), plan([]), b, "live", LOT)
    check("I: phí 0,075% được tính (3.980.000đ không đủ)", rec["qty_after"] == 100, rec)
    check("I: order_cost_vnd gồm phí", abs(order_cost_vnd(DISC) - DISC_COST) < 1e-6,
          order_cost_vnd(DISC))

    # J. pp0Buy không đo được → cận tiền mặt, KHÔNG nhân đòn bẩy
    print("\n[J] pp0Buy = None → cận TIỀN MẶT, không nhân đòn bẩy")
    b = Broker(pp_by_package={}, cash=10_000_000, resolve={"TV1": 1122})
    h = residual_headroom(plan([]), b, "live", "TV1", 19900, cash_only=True)
    check("basis = cash_bound", h["basis"] == "cash_bound", h["basis"])
    check("headroom = ĐÚNG cash, không ×3 như A1", h["headroom_vnd"] == 10_000_000,
          h["headroom_vnd"])
    check("reason nói rõ không nhân đòn bẩy", "KHÔNG nhân đòn bẩy" in h["reason"], h["reason"])

    # K. broker chết hoàn toàn → None → SKIP
    print("\n[K] broker chết (ppse + balances đều lỗi) → fail-safe KHÔNG chèn")
    b = Broker(raise_pp=True, raise_cash=True, resolve={"TV1": 1122})
    h = residual_headroom(plan([]), b, "live", "TV1", 19900, cash_only=True)
    check("headroom = None", h["headroom_vnd"] is None, h)
    check("basis = unknown", h["basis"] == "unknown", h["basis"])
    o, rec = gate_injected_order(dict(DISC), plan([]), b, "live", LOT)
    check("→ SKIP, order=None", o is None and rec["action"] == "SKIP_NO_CASH", rec["action"])
    check("cap_qty_to_headroom(None) = 0", cap_qty_to_headroom(200, 19900, None, LOT) == 0)

    # L. lệnh mua thiếu giá → không được coi là chi phí 0
    print("\n[L] lệnh mua trong plan thiếu giá → headroom KHÔNG XÁC ĐỊNH")
    bad = order("XXX", 1000, None, book="LAG", oid="BUY-XXX-99")
    b = Broker(pp_by_package={1122: 50_000_000}, cash=50_000_000, resolve={"TV1": 1122})
    h = residual_headroom(plan([bad]), b, "live", "TV1", 19900, cash_only=True)
    check("headroom = None", h["headroom_vnd"] is None, h)
    check("liệt kê id lệnh thiếu giá", "BUY-XXX-99" in h["unpriced"], h["unpriced"])
    check("order_cost_vnd trả None chứ không 0", order_cost_vnd(bad) is None,
          order_cost_vnd(bad))

    # M. tiền BÁN được cộng vào cận tiền mặt
    print("\n[M] lệnh BÁN trong plan → cộng vào cận (ppse cộng tiền bán T+0)")
    sells = [order("HDB", 1000, 30_000, side="sell", book="BAL", oid="SELL-HDB-01")]
    b = Broker(pp_by_package={}, cash=1_000_000, resolve={"TV1": 1122})
    h = residual_headroom(plan(sells), b, "live", "TV1", 19900, cash_only=True)
    net_sell = 30_000_000 * (1 - FEE_RATE)
    check("headroom = cash + tiền bán ròng",
          abs(h["headroom_vnd"] - (1_000_000 + net_sell)) < 1, h["headroom_vnd"])
    check("sell_proceeds đã TRỪ phí", abs(h["sell_proceeds_vnd"] - net_sell) < 1,
          h["sell_proceeds_vnd"])

    # N. mode paper
    print("\n[N] mode=paper → PASS_NOT_LIVE, không cản trở")
    b = Broker(pp_by_package={}, cash=0)
    o, rec = gate_injected_order(dict(DISC), plan([]), b, "paper", LOT)
    check("action = PASS_NOT_LIVE", rec["action"] == "PASS_NOT_LIVE", rec["action"])
    check("order giữ nguyên 200cp", o["qty"] == 200, o)

    # O. bẫy TV1: phải hỏi pp0Buy bằng gói 1122, KHÔNG phải 1841
    print("\n[O] bẫy TV1 07-29: gói cash_only phải giải qua _resolve_loan_package_id")
    b = Broker(pp_by_package={1122: 40_000_000, 1841: 0}, cash=5_000_000,
               resolve={"TV1": 1122}, default_package=1841)
    h = residual_headroom(plan([]), b, "live", "TV1", 19900, cash_only=True)
    check("đã gọi ppse với gói 1122", (("TV1", 19900, 1122) in b.calls), b.calls)
    check("headroom = 40M (gói đúng), KHÔNG 0 (gói 1841)",
          abs(h["headroom_vnd"] - 40_000_000) < 1, h["headroom_vnd"])
    # cash_only=False → gói default account
    b2 = Broker(pp_by_package={1122: 40_000_000, 1841: 0}, cash=5_000_000,
                resolve={"TV1": 1122}, default_package=1841)
    h2 = residual_headroom(plan([]), b2, "live", "TV1", 19900, cash_only=False)
    check("cash_only=False → dùng gói default (None→broker tự chọn)",
          (("TV1", 19900, None) in b2.calls), b2.calls)

    # P. A1 verdict = BLOCK → headroom 0 tuyệt đối
    print("\n[P] plan hiện tại ĐÃ vượt sức mua (A1 BLOCK) → headroom = 0")
    over = [order("PVT", 10000, 20_000, book="CAPIT")]     # 200M
    b = Broker(pp_by_package={1841: 50_000_000, 1122: 50_000_000}, cash=50_000_000,
               resolve={"TV1": 1122})
    h = residual_headroom(plan(over), b, "live", "TV1", 19900, cash_only=True)
    check("headroom = 0", h["headroom_vnd"] == 0.0, h["headroom_vnd"])
    check("reason nêu A1 BLOCK", "BLOCK" in h["reason"], h["reason"])
    o, rec = gate_injected_order(dict(DISC), plan(over), b, "live", LOT)
    check("→ SKIP_NO_CASH", o is None and rec["action"] == "SKIP_NO_CASH", rec["action"])

    # Q. re-plan nuốt mất tranche đã chèn
    print("\n[Q] plan bị GHI LẠI sau khi injector chèn → phải phát hiện để chèn LẠI")
    ledger = [{"plan_date": "2026-08-05", "injected_qty": 200}]
    check("ledger có + plan KHÔNG có order → True",
          replan_dropped_injection([], ledger, "2026-08-05", "TV1",
                                   "DISCRETIONARY_SPECIAL") is True)
    check("ledger có + plan CÓ order → False (đã chèn rồi, đừng chèn 2 lần)",
          replan_dropped_injection([DISC], ledger, "2026-08-05", "TV1",
                                   "DISCRETIONARY_SPECIAL") is False)
    check("ledger rỗng → False",
          replan_dropped_injection([], [], "2026-08-05", "TV1",
                                   "DISCRETIONARY_SPECIAL") is False)
    check("ledger ngày KHÁC → False",
          replan_dropped_injection([], [{"plan_date": "2026-08-04"}], "2026-08-05",
                                   "TV1", "DISCRETIONARY_SPECIAL") is False)

    # S. plan dạng DICT JSON THÔ — đúng hình dạng injector cầm (không phải TradePlan)
    print("\n[S] plan là dict JSON thô (hình dạng THẬT của injector) → không được nổ")
    raw_plan = {"plan_date": "2026-08-05", "account": "SpaceX", "orders": [
        {"id": "BUY-PVT-00", "ticker": "PVT", "side": "buy", "qty": 1000,
         "ref_price": 20_000, "estimated_cost_vnd": 20_000_000, "book": "CAPIT"},
        {"id": "SELL-HDB-01", "ticker": "HDB", "side": "sell", "qty": 100,
         "ref_price": 30_000, "book": "BAL"}]}
    b = Broker(pp_by_package={1122: 50_000_000, 1841: 50_000_000}, cash=8_000_000,
               resolve={"TV1": 1122})
    h = residual_headroom(raw_plan, b, "live", "TV1", 19900, cash_only=True)
    committed = 1000 * 20_000 * (1 + FEE_RATE)
    check("dict plan cho CÙNG kết quả như object plan (case B)",
          abs(h["headroom_vnd"] - (1 - committed / 50_000_000) * 50_000_000) < 1, h)
    check("basis = pp0buy_residual (đi qua check_plan_funding, không AttributeError)",
          h["basis"] == "pp0buy_residual", h["basis"])
    o, rec = gate_injected_order(dict(DISC), raw_plan, b, "live", LOT)
    check("gate_injected_order chạy trên dict plan", rec["action"] == "PASS", rec["action"])
    # order chỉ có limit_price_vnd (không ref_price) — dạng engine gom sinh ra
    only_limit = {"id": "X", "ticker": "TV1", "side": "buy", "qty": 100,
                  "limit_price_vnd": 19900, "book": "DISCRETIONARY_SPECIAL"}
    check("order chỉ có limit_price_vnd vẫn tính được chi phí",
          abs(order_cost_vnd(only_limit) - 100 * 19900 * (1 + FEE_RATE)) < 1e-6,
          order_cost_vnd(only_limit))

    # commitment_summary phụ trợ
    print("\n[extra] commitment_summary: tách book, loại trừ id, đếm")
    mix = [order("A", 100, 10_000, book="LAG", oid="B1"),
           order("B", 100, 20_000, book="CAPIT", oid="B2"),
           order("C", 100, 30_000, side="sell", book="BAL", oid="S1")]
    s = commitment_summary(mix)
    check("by_book tách đúng", set(s["by_book"]) == {"LAG", "CAPIT"}, s["by_book"])
    check("n_buys=2 n_sells=1", s["n_buys"] == 2 and s["n_sells"] == 1, s)
    s2 = commitment_summary(mix, exclude_ids=["B2"])
    check("exclude_ids loại đúng lệnh", "CAPIT" not in s2["by_book"], s2["by_book"])
    check("dict và dataclass cho cùng kết quả",
          abs(order_cost_vnd({"qty": 100, "ref_price": 10_000})
              - order_cost_vnd(order("A", 100, 10_000))) < 1e-9)
    check("qty âm/0 → None", order_cost_vnd({"qty": 0, "ref_price": 10_000}) is None)
    check("lot_size lớn hơn qty mua nổi → 0",
          cap_qty_to_headroom(200, 19900, 3_000_000, 1000) == 0)

    # ── S. ADAPTER `_GateOrder` KHÔNG ĐƯỢC TRÔI KHỎI `check_plan_funding` ────────────────
    # Đây là bug THẬT đã xảy ra, không phải giả định: 911f12b (2026-08-11) thêm
    # `_remaining_quantities()` đọc `o.id`, adapter không có ⇒ `residual_headroom()` nổ
    # AttributeError trên MỌI account live. Ẩn 3 ngày vì `{str(o.id): ...}` là
    # dict-comprehension — plan RỖNG không chạm `.id` lần nào, và phiên 08-13 tình cờ có
    # plan rỗng lúc injector chạy.
    #
    # S1/S2 là CONTROL tái lập đúng ca lỗi. S3 là cái ngăn lần TRÔI TIẾP THEO: thay vì chép
    # tay danh sách field (sẽ mốc y như docstring cũ đã mốc), nó ĐO ĐỘNG — cho gate ăn một
    # plan gồm các probe ghi lại MỌI attribute bị đọc, rồi đòi `_GateOrder` phải phủ hết.
    # §22: luật văn xuôi áp sai thì chuyển thành code.
    print("\n[S] adapter _GateOrder phủ đủ hình dạng `check_plan_funding` đọc")
    from trading_bot.plan_cash_commitment import _GateOrder, _as_gate_plan
    from trading_bot.plan_funding_gate import check_plan_funding

    check("S1 _GateOrder có `.id` (field mà 911f12b thêm vào gate)",
          "id" in _GateOrder.__slots__, str(_GateOrder.__slots__))

    # S2 — CONTROL: plan KHÔNG rỗng là ca đã nổ. Plan rỗng vẫn phải chạy (ca 08-13 may mắn).
    b = Broker(pp_by_package={1122: 50_000_000, 1841: 50_000_000}, cash=8_000_000,
               resolve={"TV1": 1122})
    orders_s = [order("TV1", 100, 20_000, oid="X1"),
                order("POW", 200, 13_000, oid="X2"),
                order("SSI", 50, 24_000, side="sell", oid="S9")]
    try:
        check_plan_funding(_as_gate_plan(plan(orders_s)), b, "live")
        check("S2 plan CÓ SẴN order → gate chạy được (ca nổ AttributeError trước khi vá)", True)
    except AttributeError as e:
        check("S2 plan CÓ SẴN order → gate chạy được (ca nổ AttributeError trước khi vá)",
              False, f"{type(e).__name__}: {e}")

    # S3 — bất biến chống-trôi: đo THẬT attribute nào gate đọc trên order, không chép tay.
    class _Probe:
        """Ghi lại mọi attribute bị đọc, uỷ quyền về order thật."""

        def __init__(self, real, seen):
            object.__setattr__(self, "_real", real)
            object.__setattr__(self, "_seen", seen)

        def __getattr__(self, n):
            object.__getattribute__(self, "_seen").add(n)
            return getattr(object.__getattribute__(self, "_real"), n)

    seen = set()
    gp = _as_gate_plan(plan(orders_s))
    probed = types.SimpleNamespace(
        orders=[_Probe(o, seen) for o in gp.orders], plan_date=gp.plan_date)
    for st in (None, {"plan_date": gp.plan_date, "parents": {}}):
        try:
            check_plan_funding(probed, b, "live", execution_state=st)
        except Exception:
            pass          # chỉ cần THU attribute, verdict không phải việc của ca này
    # Field gate ĐỌC mà adapter CỐ Ý không mang — mỗi mục phải có lý do + ca chứng minh
    # fail-safe ở dưới. Danh sách này là chỗ khai báo QUYẾT ĐỊNH, không phải chỗ giấu rác:
    # thêm mục vào đây = phải thêm ca S4 tương ứng chứng minh hướng lệch là AN TOÀN.
    _KNOWN_GAPS = {
        # `_order_priority` có default 5 nên KHÔNG crash. Bỏ qua `priority` ⇒ mọi lệnh =5 ⇒
        # điều kiện `sell_prio < min_buy_prio` (NGHIÊM NGẶT) luôn sai ⇒ injector KHÔNG bao
        # giờ được cấp tín dụng JIT từ tiền bán. Hướng lệch = CHẶT HƠN gate thật (S4 chứng
        # minh). Mang `priority` vào adapter sẽ NỚI một cổng tiền ⇒ đổi hành vi cấp vốn
        # live, KHÔNG tự làm trong khuôn khổ vá lỗi này — đã escalate cho user/quant-skeptic
        # (bus finding job Taylor_20260814_080528).
        "priority",
    }
    missing = {a for a in seen if not a.startswith("_")} - set(_GateOrder.__slots__)
    check("S3 không có attribute MỚI nào gate đọc mà adapter thiếu "
          f"(đo động, {len(seen)} attr; {len(_KNOWN_GAPS)} gap đã khai báo)",
          not (missing - _KNOWN_GAPS),
          f"THIẾU CHƯA KHAI: {sorted(missing - _KNOWN_GAPS)} — thêm field vào gate thì "
          f"phải thêm vào adapter, hoặc khai vào _KNOWN_GAPS kèm ca S4 chứng minh fail-safe")
    check("S3b mọi gap đã khai vẫn CÒN THẬT (khai thừa = danh sách bắt đầu mốc)",
          _KNOWN_GAPS <= missing, f"khai thừa: {sorted(_KNOWN_GAPS - missing)}")

    # S4 — gap `priority` phải lệch về phía CHẶT HƠN, không bao giờ nới.
    from trading_bot.plan_funding_gate import _jit_sell_credit
    real_orders = [order("AAA", 100, 20_000, side="sell", oid="S1"),
                   order("BBB", 100, 20_000, oid="B1")]
    real_orders[0].priority, real_orders[1].priority = 1, 5      # bán TRƯỚC mua
    real_plan = plan(real_orders)
    gate_plan = _as_gate_plan(real_plan)
    real_buys = [o for o in real_plan.orders if o.side == "buy"]
    gate_buys = [o for o in gate_plan.orders if o.side == "buy"]
    credit_real = _jit_sell_credit(real_plan, real_buys)[0]
    credit_gate = _jit_sell_credit(gate_plan, gate_buys)[0]
    check("S4 gap `priority` lệch về phía CHẶT HƠN: adapter cấp tín dụng JIT ≤ gate thật",
          credit_gate <= credit_real, f"adapter={credit_gate:,.0f} vs thật={credit_real:,.0f}")
    check("S4b …và ca này tín dụng thật > 0 (nếu không, S4 đúng một cách vô nghĩa)",
          credit_real > 0, f"thật={credit_real:,.0f}")

    print("\n" + "=" * 78)
    print(f"KẾT QUẢ: {PASS} PASS / {FAIL} FAIL")
    print("=" * 78)
    return FAIL


def tz_invariance():
    """R. Chạy lại CHÍNH file này dưới 3 TZ + không TZ; output phải byte-identical."""
    print("\n[R] bất biến TZ — chạy lại selfcheck dưới env khác nhau")
    me = os.path.abspath(__file__)
    outs = {}
    for label, env in (("no-TZ", None), ("UTC", "UTC"), ("ICT", "Asia/Ho_Chi_Minh"),
                       ("NY", "America/New_York")):
        e = dict(os.environ)
        e.pop("TZ", None)
        if env:
            e["TZ"] = env
        e["_SELFCHECK_NO_TZ_LOOP"] = "1"
        r = subprocess.run([sys.executable, me], env=e, capture_output=True, text=True)
        outs[label] = r.stdout
    base = outs["no-TZ"]
    ok = all(v == base for v in outs.values())
    print(f"  {'✅' if ok else '❌'} output byte-identical ở 4 cấu hình TZ "
          f"({', '.join(outs)})")
    return 0 if ok else 1


if __name__ == "__main__":
    rc = run()
    if not os.environ.get("_SELFCHECK_NO_TZ_LOOP"):
        rc += tz_invariance()
    sys.exit(1 if rc else 0)
