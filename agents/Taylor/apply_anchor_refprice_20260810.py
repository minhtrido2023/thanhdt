# -*- coding: utf-8 -*-
"""Cập nhật 4 lệnh mua LAG trong plan 2026-08-10 sang cơ chế trần giá tuyệt đối.

Bối cảnh: cơ chế CŨ neo `ref_price = anchor/1,04` để trần đuổi % vô tình chạm đúng anchor.
Đo thật 2026-08-09: chase = clamp(2×rvol20d, 1,5%, 4%) cho DRI = 3,06% (KHÔNG phải 4%)
⇒ trần thực chỉ 12.500×1,0306 → làm tròn bước giá UPCOM = 12.800đ, trong khi thị trường
13.100–13.200đ ⇒ gần như chắc chắn KHÔNG khớp.

Từ commit a29ab4f, trần "không vượt anchor" được cưỡng chế bằng CODE
(`load_plan()` tự suy `hard_no_chase_ceiling_vnd` từ `entry_anchor_price`, executor clamp
ở mọi bước). Nên `ref_price` không còn phải gánh vai trò cái chốt cửa nữa — trả nó về
đúng nghĩa "giá tham chiếu thật" = anchor, để lệnh bám được giá đang chào tới sát anchor.

KHÔNG đổi `qty` — sizing là quyết định của DollarBill/user, không phải của bản vá cơ chế
giá. Hệ quả: ở giá xấu nhất (đúng anchor) giá trị lệnh vượt slot vài %, đã ghi rõ vào
`sizing_note` để user thấy khi duyệt.

Chạy: python mike/agents/Taylor/apply_anchor_refprice_20260810.py [--dry-run]
"""
import json
import os
import sys

ROOT = "/home/trido/thanhdt/WorkingClaude"
PLAN_DIR = os.path.join(ROOT, "data", "trade_plans")
PLAN_DATE = "2026-08-10"
FEE_RATE = 0.00075          # phí thật 0,075% (memory project-spacex-account-fee-margin-rates)

NEW_SOURCE = (
    "Giá tham chiếu THẬT = entry_anchor_price {a:,}đ (phiên chuẩn {d}, tav2_bq.ticker.Price "
    "giá thô, do mike/bin/filter_lag_entry_window.py trả về). KHÁC bản trước: không còn neo "
    "ngược ref_price = anchor/1,04. Luật 'giá live không vượt anchor' nay được cưỡng chế bằng "
    "CODE (commit a29ab4f, quant-skeptic CONFIRMED): load_plan() tự suy hard_no_chase_ceiling_vnd "
    "= entry_anchor_price, executor clamp giá đặt ở min(giá chào thật, {a:,}đ) tại MỌI bước và "
    "KHÔNG đặt lệnh nếu ngay cả giá sàn phiên đã > {a:,}đ. Lý do bỏ mẹo cũ: nó giả định chase "
    "cap luôn = 4%, nhưng chase = clamp(2×rvol20d, 1,5%, 4%) đo thật ngày 2026-08-09 chỉ ra "
    "3,06% cho DRI ⇒ trần thực 12.800đ (cách xa thị trường 13.100–13.200đ), và con số đó đổi "
    "theo rvol mỗi ngày."
)

MECH = (
    " CƠ CHẾ ĐẶT LỆNH (mới, commit a29ab4f): lệnh BÁM giá đang chào trên thị trường (q.ask, "
    "đọc lại mỗi ~8 phút qua vòng huỷ/đặt-lại) và đặt tại min(giá chào, {a:,}đ). Thị trường "
    "dưới anchor ⇒ mua đúng giá thị trường (rẻ hơn anchor); thị trường trên anchor ⇒ nằm chờ "
    "đúng tại {a:,}đ, KHÔNG BAO GIỜ khớp trên anchor."
)


def main(dry):
    for acct in ("SpaceX", "ZaloPay"):
        path = os.path.join(PLAN_DIR, f"plan_{acct}_{PLAN_DATE}.json")
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        print(f"== {acct}")
        for o in d["orders"]:
            if o["side"] != "buy":
                continue
            a = float(o["entry_anchor_price"])
            old_ref, qty = float(o["ref_price"]), int(o["qty"])
            cost = int(round(qty * a))
            fee = int(round(cost * FEE_RATE))
            o["ref_price"] = a
            o["ref_price_source"] = NEW_SOURCE.format(a=int(a), d=o["entry_anchor_date"])
            o["estimated_cost_vnd"] = cost
            o["fee_est_vnd"] = fee
            o["total_with_fee_vnd"] = cost + fee
            o["note"] = o["note"].split(" ⚠️")[0] + MECH.format(a=int(a)) + \
                " ⚠️ Nếu DT5G chuyển BEAR, allocator đặt w_LAG=0 ⇒ vị thế này sẽ bị bán theo cơ chế sẵn có."
            # slot lấy từ chính sizing_note cũ để không tự bịa lại mẫu số.
            # Phải neo vào "⇒ slot " — chuỗi "slot = weight_pct..." ở ĐẦU note khớp trước.
            try:
                seg = o["sizing_note"].split("⇒ slot ")[1]
                slot = float(seg.split("đ")[0].replace(",", ""))
            except (IndexError, ValueError):
                slot = None
            over = f"{(cost / slot - 1) * 100:+.1f}%" if slot else "n/a"
            o["sizing_note"] = o["sizing_note"] + (
                f" ⚠️ CẬP NHẬT 2026-08-09 (bản vá cơ chế giá a29ab4f): ref_price đổi "
                f"{old_ref:,.0f}đ → {a:,.0f}đ (= anchor, giá tham chiếu thật). qty GIỮ NGUYÊN "
                f"{qty:,}cp — sizing là quyết định của DollarBill/user, bản vá này chỉ đổi cơ chế "
                f"GIÁ. Hệ quả: ở giá xấu nhất (khớp đúng anchor) giá trị lệnh {cost:,}đ so với "
                f"slot {slot:,.0f}đ = {over}." if slot else
                f" ⚠️ CẬP NHẬT 2026-08-09: ref_price {old_ref:,.0f}đ → {a:,.0f}đ, qty giữ nguyên.")
            print(f"  {o['ticker']}: ref {old_ref:,.0f} → {a:,.0f} | qty {qty:,} (giữ) | "
                  f"chi phí xấu nhất {cost:,}đ vs slot {slot:,.0f}đ ({over})"
                  if slot else f"  {o['ticker']}: ref {old_ref:,.0f} → {a:,.0f}")
        if dry:
            print("  (dry-run — không ghi)")
            continue
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        os.replace(tmp, path)          # ghi nguyên tử (§5)
        print(f"  đã ghi {path}")


if __name__ == "__main__":
    main("--dry-run" in sys.argv)
