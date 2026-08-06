#!/usr/bin/env python3
"""A/B đo phương án (B) — gross-up phí ma sát trong `needed` — trên SỔ THẬT SpaceX/ZaloPay.

🚨 **HẾT HIỆU LỰC từ 2026-08-06 (job `Taylor_20260806_033014`) — DÙNG
`jit_unpark_roundup_c_abc_20260806.py` THAY THẾ.** Lý do: chân A ở dòng 55 gọi
`allocate(needed_a, pool_a)` để tái lập "công thức CŨ", nhưng `allocate()` nay LÀM TRÒN LÊN 1 lô
(phương án C) nên chân A cũng bị làm tròn LÊN ⇒ script này giờ so B-với-B và in ra "KHÔNG ĐỔI" cho
mọi ca — nhãn SAI, số SAI. Script mới sửa đúng chỗ đó (`ceiling=needed` để ép làm tròn XUỐNG) và
so đủ 3 chân A/B/C. Giữ file này làm bằng chứng phiên đo (B) ngày 08-06, KHÔNG chạy lại để trích số.


Chạy ĐÚNG 3 mức giá tham chiếu đã đo trong báo cáo cũ (100k / 30k / 12k đ/cp), cùng một lệnh mua
LAG ~80tr, để trả lời một câu duy nhất: **sau khi gross-up, lệnh mua còn bị hụt tiền không?**

Chân A (công thức CŨ, `needed = tv0 − cash`) được tái lập ĐỘC LẬP ngay tại đây bằng chính
`allocate()`/`build_pool()` của module — không sửa file production, không cần checkout bản cũ.
Chân B đọc thẳng kết quả `compute_jit_unpark()` hiện hành.

    python3 mike/agents/Taylor/jit_unpark_grossup_ab_20260806.py
"""
import os
import sys

BIN = "/home/trido/thanhdt/WorkingClaude/mike/bin"
sys.path.insert(0, BIN)
from compute_jit_unpark import (compute_jit_unpark, allocate, build_pool,   # noqa: E402
                                ETF_FRICTION, LOT)
from compute_park_trim import etf_day_cap_live, live_share                  # noqa: E402
from park_holdings import park_holdings                                     # noqa: E402
from trading_bot.plan import _adv_for_gate                                  # noqa: E402

ASOF = "2026-08-05"
PRICES = (100_000, 30_000, 12_000)      # đúng 3 mức đã đo trong báo cáo cũ
BUY_VND = 80_000_000


def main():
    share, _, share_err = live_share()
    day_cap, _b, cap_err = etf_day_cap_live(ASOF)
    if share_err or cap_err:
        print(f"KHÔNG đo được share/trần rổ ({share_err} / {cap_err}) ⇒ dừng")
        return 1
    print(f"asof={ASOF}  trần TỔNG/phiên={day_cap/1e9:,.2f} tỷ  share={share}  "
          f"friction={ETF_FRICTION}")
    print(f"{'acct':<8}{'px':>8}{'qty kế→chốt':>14}{'hụt A (cũ)':>14}{'hụt B (mới)':>14}"
          f"{'Δ hụt':>12}{'mất tiền':>12}{'%lệnh':>8}  ghi chú")

    rows = []
    for acct in ("SpaceX", "ZaloPay"):
        h = park_holdings(acct, ASOF)
        for px in PRICES:
            qty = int(BUY_VND // px // LOT * LOT)
            o = {"id": f"BUY-FPT-{px}", "ticker": "FPT", "side": "buy", "qty": qty,
                 "ref_price": px, "book": "LAG", "play_type": "LAG_HI", "priority": 10}
            r = compute_jit_unpark(acct, asof=ASOF, orders=[o], holdings=h)
            m = r["buy_amendments"][0]
            tv0, cash0 = m["target_value_vnd"], m["cash_before_vnd"]
            gap_b = tv0 - m["buying_power_vnd"]

            # ── Chân A: tái lập công thức CŨ trên ĐÚNG cùng rổ, cùng trần ────────
            pool_a, _bl, _e = build_pool(h, ASOF, share, _adv_for_gate)
            needed_a = min(tv0 - max(cash0, 0.0), day_cap)
            gross_a = sum(q * pool_a[tk]["px"] for tk, q in allocate(needed_a, pool_a).items())
            gap_a = tv0 - (cash0 + gross_a * (1 - ETF_FRICTION))

            lost = (m["qty_plan"] - m.get("qty_final", 0)) * px
            note = ("KHÔNG ĐỔI (headroom mới < 1 lô bán)" if abs(gap_a - gap_b) < 1e-6
                    else f"nhét thêm được lô bán ⇒ hụt giảm {gap_a - gap_b:,.0f}đ")
            print(f"{acct:<8}{px:>8,}{m['qty_plan']:>7,}→{m.get('qty_final',0):<6,}"
                  f"{gap_a:>14,.0f}{gap_b:>14,.0f}{gap_a-gap_b:>12,.0f}"
                  f"{lost/1e6:>10,.2f}tr{lost/tv0*100:>7.2f}%  {note}")
            rows.append((acct, px, gap_a, gap_b, lost, m["status"]))

    print()
    n_zero = sum(1 for *_x, gap_b, _l, _s in [(a, p, ga, gb, l, s) for a, p, ga, gb, l, s in rows]
                 if gap_b <= 1e-6)
    n_same = sum(1 for _a, _p, ga, gb, _l, _s in rows if abs(ga - gb) < 1e-6)
    n_shrink = sum(1 for *_x, s in rows if s == "SHRINK")
    print(f"KẾT LUẬN: {n_zero}/{len(rows)} ca hụt tiền về 0 · {n_same}/{len(rows)} ca gross-up "
          f"là NO-OP đúng 0đ · {n_shrink}/{len(rows)} ca lệnh mua VẪN bị co.")
    print("⇒ Gross-up khử HẲN phần hụt do PHÍ, nhưng phần hụt do RỜI RẠC LÔ BÁN vẫn còn, và chỉ "
          "cần hụt 1đ là mất TRỌN 1 lô mua (chân buy dùng `round_lot(min(tv, bp)/px)`).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
