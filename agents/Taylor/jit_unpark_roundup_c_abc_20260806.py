#!/usr/bin/env python3
"""A/B/C phương án làm tròn LÊN 1 lô — đo trên SỔ THẬT SpaceX/ZaloPay, ĐÚNG 6 ca của báo cáo cũ.

Ba chân, cùng rổ / cùng trần / cùng giá, khác nhau ĐÚNG hai chỗ:

    A (trước 08-06)  needed = tv0 − cash            · làm tròn XUỐNG lô
    B (đã áp sáng)   needed = (tv0 − cash)/(1 − f)  · làm tròn XUỐNG lô
    C (HIỆN HÀNH)    needed = (tv0 − cash)/(1 − f)  · làm tròn LÊN ≤ 1 lô rẻ nhất

Chân A và B tái lập ĐỘC LẬP ngay tại đây bằng chính `allocate()` — không checkout bản cũ, không
chép lại logic. Mẹo: `allocate(x, pool, ceiling=x)` = đúng hành vi làm tròn XUỐNG, vì vòng
largest-remainder đã dừng khi mọi lô còn lại đắt hơn phần dư, nên `ceiling=x` chặn hẳn lô tròn LÊN.

Trả lời đúng 3 câu:
  1. Sau (C), 6/6 ca còn hụt tiền không?
  2. Lệnh mua còn bị co không (mất bao nhiêu VND)?
  3. Chi phí thật của (C) = bán dư bao nhiêu VND, có nằm dưới cận trên "1 lô rẻ nhất" không?

    python3 mike/agents/Taylor/jit_unpark_roundup_c_abc_20260806.py
"""
import os
import sys

BIN = "/home/trido/thanhdt/WorkingClaude/mike/bin"
sys.path.insert(0, BIN)
from compute_jit_unpark import (compute_jit_unpark, allocate, build_pool,   # noqa: E402
                                ETF_FRICTION, LOT, JIT_TRIGGER_FRAC,
                                SHRINK_FRAC, MIN_ORDER_VND)
from compute_park_trim import etf_day_cap_live, live_share                  # noqa: E402
from park_holdings import park_holdings                                     # noqa: E402
from trading_bot.plan import _adv_for_gate                                  # noqa: E402
from trading_bot.vn_market import round_lot                                 # noqa: E402

ASOF = "2026-08-05"
PRICES = (100_000, 30_000, 12_000)      # đúng 3 mức đã đo trong báo cáo cũ
BUY_VND = 80_000_000


def leg(pool, needed, tv0, cash0, px, round_up):
    """Chạy đúng chân bán + chân mua của module cho MỘT phương án. Trả (gross, gap, qty_final)."""
    a = allocate(needed, pool, ceiling=None if round_up else needed)
    gross = sum(q * pool[tk]["px"] for tk, q in a.items())
    bp = cash0 + gross * (1 - ETF_FRICTION)                    # margin_room = 0 (cấu hình R3)
    tv = tv0 if bp >= tv0 * JIT_TRIGGER_FRAC else bp * SHRINK_FRAC
    qf = 0 if tv < MIN_ORDER_VND else round_lot(min(tv, bp) / px)
    return gross, tv0 - bp, int(qf if qf >= LOT else 0)


def main():
    share, _lbl, share_err = live_share()
    day_cap, _b, cap_err = etf_day_cap_live(ASOF)
    if share_err or cap_err:
        print(f"KHÔNG đo được share/trần rổ ({share_err} / {cap_err}) ⇒ dừng")
        return 1
    print(f"asof={ASOF}  trần TỔNG/phiên={day_cap/1e9:,.2f} tỷ  share={share}  "
          f"friction={ETF_FRICTION}  lot={LOT}")
    print(f"\n{'acct':<8}{'px':>8}{'hụt A':>13}{'hụt B':>13}{'hụt C':>13}"
          f"{'qty A/B':>10}{'qty C':>8}{'mất A/B':>11}{'bán dư C':>12}{'1 lô rẻ nhất':>14}")

    rows = []
    for acct in ("SpaceX", "ZaloPay"):
        h = park_holdings(acct, ASOF)
        for px in PRICES:
            qty = int(BUY_VND // px // LOT * LOT)
            o = {"id": f"BUY-FPT-{px}", "ticker": "FPT", "side": "buy", "qty": qty,
                 "ref_price": px, "book": "LAG", "play_type": "LAG_HI", "priority": 10}
            # Chân C = module HIỆN HÀNH, không mô phỏng lại.
            r = compute_jit_unpark(acct, asof=ASOF, orders=[o], holdings=h)
            m = r["buy_amendments"][0]
            tv0, cash0 = m["target_value_vnd"], m["cash_before_vnd"]
            gross_c, gap_c, qty_c = m["jit_sell_vnd"], tv0 - m["buying_power_vnd"], m["qty_final"]

            # Chân A/B — rổ SẠCH mỗi lần (build_pool trả pool mới, chưa bị trừ `sold_qty`).
            need_a = min(tv0 - max(cash0, 0.0), day_cap)
            need_b = min((tv0 - max(cash0, 0.0)) / (1 - ETF_FRICTION), day_cap)
            pool_a, _bl, _e = build_pool(h, ASOF, share, _adv_for_gate)
            gross_a, gap_a, qty_a = leg(pool_a, need_a, tv0, cash0, px, round_up=False)
            pool_b, _bl, _e = build_pool(h, ASOF, share, _adv_for_gate)
            gross_b, gap_b, qty_b = leg(pool_b, need_b, tv0, cash0, px, round_up=False)

            cheapest = LOT * min(d["px"] for d in pool_a.values())
            lost_b = (qty - qty_b) * px
            over_c = gross_c - m["needed_vnd"]
            print(f"{acct:<8}{px:>8,}{gap_a:>13,.0f}{gap_b:>13,.0f}{gap_c:>13,.0f}"
                  f"{qty_a:>6,}/{qty_b:<3,}{qty_c:>8,}{lost_b/1e6:>9,.2f}tr"
                  f"{over_c/1e6:>10,.2f}tr{cheapest/1e6:>12,.2f}tr")
            rows.append(dict(acct=acct, px=px, qty_plan=qty, gap_a=gap_a, gap_b=gap_b,
                             gap_c=gap_c, qty_b=qty_b, qty_c=qty_c, lost_b=lost_b,
                             over_c=over_c, cheapest=cheapest, status=m["status"],
                             needed=m["needed_vnd"], tv0=tv0))

    n = len(rows)
    n_zero = sum(1 for x in rows if x["gap_c"] <= 1e-6)
    n_full = sum(1 for x in rows if x["qty_c"] == x["qty_plan"])
    n_bound = sum(1 for x in rows if 0 <= x["over_c"] < x["cheapest"])
    saved = sum(x["lost_b"] for x in rows)
    cost = sum(x["over_c"] for x in rows)
    print(f"\nKẾT LUẬN: {n_zero}/{n} ca hụt tiền về 0 · {n_full}/{n} ca mua ĐỦ nguyên lệnh · "
          f"{n_bound}/{n} ca bán dư nằm trong cận trên (0 ≤ dư < 1 lô rẻ nhất)")
    print(f"  Σ lệnh mua KHÔNG còn bị mất: {saved/1e6:,.2f}tr  ·  Σ bán dư phải trả: "
          f"{cost/1e6:,.2f}tr  ·  tỉ lệ đổi: 1đ bán dư cứu {saved/max(cost,1):,.1f}đ lệnh mua")
    print(f"  Bán dư/ca: max {max(x['over_c'] for x in rows)/1e6:,.2f}tr · "
          f"trung vị {sorted(x['over_c'] for x in rows)[n//2]/1e6:,.2f}tr · "
          f"cận trên lý thuyết (1 lô rẻ nhất của rổ) = "
          f"{max(x['cheapest'] for x in rows)/1e6:,.2f}tr")
    ok = n_zero == n and n_full == n and n_bound == n
    print(f"\n{'✅' if ok else '❌'} (C): "
          f"{'hết hụt 6/6, mua đủ 6/6, chi phí có cận trên chặt 6/6' if ok else 'CHƯA đạt'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
