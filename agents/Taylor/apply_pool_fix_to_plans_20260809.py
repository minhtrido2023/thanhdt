#!/usr/bin/env python3
"""Áp bản sửa mẫu số pool L1 (job Taylor_20260809_150316) vào 2 plan 2026-08-10.

CHỈ sửa phần L1 (park-trim compliance). Phần L2 (JIT unpark — tiền mua 4 lệnh LAG) GIỮ NGUYÊN
TUYỆT ĐỐI: hai lý do bán khác nhau, xoá nhầm L2 thì 4 lệnh mua LAG mất nguồn vốn.

  SpaceX : L1 110.140.000đ → 0 (PARK 69,0% < trần 80% ⇒ NO_TRIM). 13 lệnh bán giữ nguyên số
           lệnh nhưng co về đúng phần L2 = 136.030.000đ.
  ZaloPay: L1 85.005.000đ → 79.035.000đ (vẫn TRIM, PARK 95,8% > 80%). Đúng 1 lô VCB đổi:
           qty 800 → 700.

Ghi ATOMIC (tmp + os.replace, §5). Giữ requires_user_approval=true / approved_by=null.
"""
import datetime as dt
import json
import os
import shutil
import sys

WC = "/home/trido/thanhdt/WorkingClaude"
PLAN_DIR = os.path.join(WC, "data", "trade_plans")
FEE = 0.00075                      # 0,075% — phí thật của tài khoản, KHÔNG phải 0,1%
JOB = "Taylor_20260809_150316"
STAMP = dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat(timespec="seconds")

# L1 mới, đo live asof 2026-08-09 bằng compute_park_trim.py ĐÃ SỬA (pool = totalCash − totalDebt
# + park_mv). SpaceX rỗng vì NO_TRIM.
NEW_L1 = {
    "SpaceX": {},
    "ZaloPay": {"BID": 200, "CTG": 300, "HDB": 200, "MBB": 300,
                "TCB": 300, "VCB": 300, "VHM": 200, "VPB": 300},
}


def atomic_write(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def apply(acc, l1_result):
    path = os.path.join(PLAN_DIR, f"plan_{acc}_2026-08-10.json")
    shutil.copy2(path, path + f".bak_{JOB}")
    d = json.load(open(path, encoding="utf-8"))
    new_l1 = NEW_L1[acc]
    changed = []

    for o in d["orders"]:
        if o.get("side") != "sell":
            continue
        tk = o["ticker"]
        old_qty, old_l1 = o["qty"], o.get("qty_l1_park_trim", 0)
        l2 = o.get("qty_l2_jit_unpark", 0)
        l1 = new_l1.get(tk, 0)
        if l1 > old_l1:                       # chỉ được GIỮ NGUYÊN hoặc GIẢM
            raise SystemExit(f"{acc}/{tk}: L1 mới {l1} > L1 cũ {old_l1} — dừng, cần xem lại")
        qty = l1 + l2
        if qty <= 0:
            raise SystemExit(f"{acc}/{tk}: qty mới = 0 — cần xoá lệnh, không phải sửa qty")
        o["qty"], o["qty_l1_park_trim"] = qty, l1
        o["estimated_proceeds_vnd"] = round(qty * o["ref_price"])
        o["fee_est_vnd"] = round(qty * o["ref_price"] * FEE)
        o["play_type"] = ("PARK_TRIM+JIT_UNPARK" if l1 and l2
                          else ("PARK_TRIM" if l1 else "JIT_UNPARK"))
        if qty != old_qty:
            changed.append(f"{tk} {old_qty}→{qty} (L1 {old_l1}→{l1}, L2 {l2} giữ nguyên)")

    # ── khối park_trim_proposal: thay bằng kết quả THẬT của script đã sửa ──
    pt = d["park_trim_proposal"]
    pt_old_total = pt.get("trim_proposed_vnd")
    pt["pool_basis"] = "totalCash − totalDebt + park_mv (SỬA 2026-08-09, job " + JOB + ")"
    pt["pool_basis_prev"] = "availableCash + park_mv (SAI — bỏ sót tiền bán chưa settle T+2)"
    pt["pool_vnd"] = l1_result["pool_vnd"]
    pt["decision"] = l1_result["decision"]
    pt["trim_total_vnd"] = l1_result.get("trim_total_vnd")
    pt["trim_proposed_vnd"] = l1_result.get("trim_proposed_vnd", 0)
    pt["orders"] = l1_result.get("orders", [])
    pt["superseded_note"] = (
        f"L1 cũ {pt_old_total:,.0f}đ tính trên pool = availableCash + park_mv. availableCash "
        f"KHÔNG chứa tiền bán chưa settle T+2 (đo SpaceX 08-07: bán 189,4tr mà availableCash "
        f"11:25 và 19:10 y hệt 4.821.143đ) ⇒ mẫu số co lại đúng bằng lượng vừa bán ⇒ vòng lặp "
        f"tự kích đòi trim tiếp. L1 mới = {pt['trim_proposed_vnd']:,.0f}đ.")

    # ── tổng: TÍNH LẠI TỪ orders[], không sửa tay ──
    sells = [o for o in d["orders"] if o["side"] == "sell"]
    buys = [o for o in d["orders"] if o["side"] == "buy"]
    sg = sum(o["qty"] * o["ref_price"] for o in sells)
    bg = sum(o["qty"] * o["ref_price"] for o in buys)
    sfee, bfee = round(sg * FEE), round(bg * FEE)
    cash0 = d["orders_summary"]["available_cash_before_vnd"]
    s = d["orders_summary"]
    s.update({"total_orders": len(d["orders"]), "total_sell_orders": len(sells),
              "total_buy_orders": len(buys),
              "sell_gross_vnd": round(sg), "sell_fee_est_vnd": sfee,
              "sell_net_proceeds_vnd": round(sg) - sfee,
              "buy_gross_vnd": round(bg), "buy_fee_est_vnd": bfee,
              "buy_total_with_fee_vnd": round(bg) + bfee,
              "net_cash_change_vnd": (round(sg) - sfee) - (round(bg) + bfee),
              "cash_after_all_orders_vnd": cash0 + (round(sg) - sfee) - (round(bg) + bfee),
              "funding_check_sell_ge_buy": (cash0 + round(sg) - sfee) >= (round(bg) + bfee),
              "sell_split_note": (
                  f"L1 park_trim {sum(o.get('qty_l1_park_trim', 0) * o['ref_price'] for o in sells):,.0f}đ "
                  f"+ L2 jit_unpark {sum(o.get('qty_l2_jit_unpark', 0) * o['ref_price'] for o in sells):,.0f}đ, "
                  f"gộp 1 lệnh/mã ⇒ {len(sells)} lệnh bán. (Sửa mẫu số pool {STAMP[:10]}.)")})

    cp = d["cash_planning"]
    cp["discipline_check"] = (
        f"MUA = {round(bg) + bfee:,.0f}đ. Nguồn = cash đã settle {cash0:,.0f}đ + bán PARK ròng "
        f"{round(sg) - sfee:,.0f}đ (nằm NGAY TRONG orders[] này, priority 0, chạy TRƯỚC) = "
        f"{cash0 + round(sg) - sfee:,.0f}đ ≥ {round(bg) + bfee:,.0f}đ "
        f"{'✅' if (cash0 + round(sg) - sfee) >= (round(bg) + bfee) else '❌'}. Vẫn dùng "
        f"availableCash (bảo thủ) làm nguồn TÀI TRỢ — KHÁC với mẫu số TỶ LỆ của L1, xem "
        f"pool_fix_{JOB}.")
    cp["cash_end_after_all_vnd"] = cash0 + (round(sg) - sfee) - (round(bg) + bfee)

    d[f"pool_fix_{JOB}"] = {
        "what": "Sửa mẫu số pool của L1 park-trim: availableCash → (totalCash − totalDebt).",
        "why": ("availableCash KHÔNG bao giờ chứa tiền bán chưa settle T+2. Bằng chứng SpaceX "
                "2026-08-07 cùng account: 11:25 availableCash 4.821.143 / totalCash 14.596.323; "
                "19:10 sau khi bán 13 mã PARK 189,4tr thì availableCash VẪN 4.821.143 (không đổi "
                "1 đồng) còn totalCash 203.656.265. Dùng nó làm mẫu số ⇒ bán X làm pool giảm đúng "
                "X ⇒ tỷ lệ PARK/pool gần như đứng yên ⇒ phiên sau lại đòi trim (vòng lặp tự kích)."),
        "impact_here": changed or "không lệnh nào đổi",
        "l1_before_vnd": pt_old_total, "l1_after_vnd": pt["trim_proposed_vnd"],
        "l2_untouched": "L2 JIT-unpark GIỮ NGUYÊN — nguồn vốn của 4 lệnh mua LAG.",
        "margin_debt": ("Mẫu số cũng trừ totalDebt (phản biện quant-skeptic vòng 1). Ngày 08-07 "
                        "totalDebt = 0 ở cả 2 account ⇒ không ảnh hưởng số ở đây."),
        "all_zero_feed_guard": (
            "Vòng 2 quant-skeptic REFUTED: guard cũ chỉ bắt field THIẾU (None), không bắt field "
            "CÓ MÀ BẰNG 0 — đúng hình dạng lỗi feed DNSE 2026-07-27. Đã vá 2 tầng: "
            "park_holdings._cash_fields_all_zero (ở nguồn, cả nhánh live-read lẫn file-read) + "
            "guard trong compute_trim (cho holdings tới từ đường khác). Tái hiện kịch bản vòng 2 "
            "bằng cách gọi thẳng compute_trim: nay BLOCKED_CASH_BASIS / 0 lệnh (trước: TRIM, "
            "3 lệnh ~298tr). Nợ kỹ thuật CÒN LẠI: detector toàn-0 vẫn là 2 bản sao "
            "(daily_nav_snapshot.py và park_holdings.py), chưa tách helper dùng chung."),
        "gate": ("quant-skeptic CONFIRMED (high) vòng 3 VÀ vòng 4 — cả hai vòng reviewer tự gọi "
                 "DNSE live và tái lập ĐÚNG TỚI TỪNG ĐỒNG hai số dưới đây. Selfcheck "
                 "compute_park_trim 63/63 trên 4 môi trường TZ (env -u TZ / Asia/Ho_Chi_Minh / "
                 "UTC / America/New_York); corp_action 56/56, compute_jit_unpark 67/67, "
                 "book_tagging PASS."),
        "residual_gap_disclosed": (
            "CHƯA đóng (quant-skeptic vòng 4 nêu, tôi công nhận): lỗi feed làm SAI cả ba field "
            "theo cùng một tỉ lệ (tự nhất quán nhưng sai độ lớn) vượt được cả ba lớp guard hiện "
            "có, vì mọi lớp đều kiểm quan hệ/giá trị chứ không kiểm độ lớn. Lớp bắt được nó là "
            "circuit-breaker theo BIẾN ĐỘNG pool giữa hai phiên — cần sổ pool lịch sử, hiện chưa "
            "ghi. KHÔNG ảnh hưởng số của phiên 08-10 (reviewer đã tái lập độc lập), nhưng đừng "
            "đọc 'không BLOCKED' = 'mẫu số chắc chắn đúng'."),
        "job": JOB, "verified_by_job": "Taylor_20260809_161845", "applied_at": STAMP,
    }
    assert d["requires_user_approval"] is True and d["approved_by"] is None, "cờ duyệt bị đụng"
    atomic_write(path, d)
    print(f"[{acc}] L1 {pt_old_total:,.0f}đ → {pt['trim_proposed_vnd']:,.0f}đ | "
          f"bán {sg:,.0f}đ, mua {bg:,.0f}đ, cash cuối {cp['cash_end_after_all_vnd']:,.0f}đ")
    for c in changed:
        print(f"    · {c}")
    if not changed:
        print("    · (không lệnh nào đổi)")


if __name__ == "__main__":
    for acc in ("SpaceX", "ZaloPay"):
        res = json.load(open(f"/tmp/l1_fixed_{acc}.json", encoding="utf-8"))
        apply(acc, res)
    print("\nXONG — requires_user_approval vẫn true, approved_by vẫn null.")
