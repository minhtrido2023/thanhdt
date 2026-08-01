#!/usr/bin/env python3
"""One-off data fix — nav_history_ZaloPay.csv dòng 2026-07-27 (job Winston_20260801_090422).

BUG: DNSE trả balances TOÀN SỐ 0 lúc 19:04:59 + 19:10:20 ngày 27/07; daily_nav_snapshot.py
(bản cũ) nhận số 0 đó → ghi cash=0, NAV=804.077.200. Thiếu toàn bộ tiền mặt.
(Chốt chặn đã thêm vào daily_nav_snapshot.py cùng job này để không tái diễn.)

SỐ ĐÚNG (tự dựng lại độc lập, xem phần verify bên dưới):
  mtm_stock = 804.077.200  (GIỮ NGUYÊN — đã đối chiếu khớp 100%, không dính bug)
  cash      =  29.779.420  (KHÔNG phải 32.011.420 — xem ghi chú SAB bên dưới)
  NAV       = 833.856.620

Nguồn cash: bản đọc balances TƯƠI 2026-07-28T09:15:15 (totalCash=32.011.420) — bản ghi đầu
tiên sau ngày 27/07, chụp TRƯỚC cú khớp CSV 09:15:35 nên chưa nhiễm giao dịch 28/07.
TRỪ ĐI 2.232.000 = cổ tức SAB (744 cp × 3.000đ/cp) vì SAB có ex-date 28/07, KHÔNG phải 27/07:
  - Cuối 27/07 SAB vẫn giao dịch CUM-cổ-tức, giá ATC 46.600 đã nằm trong mtm_stock 804.077.200.
  - `cashDividendReceiving` nhảy 4.221.500 → 6.453.500 (+2.232.000) trong khoảng
    27/07 09:50 → 28/07 09:15, tức được ghi nhận vào sáng ex-date 28/07.
  => Cộng khoản phải thu này vào cash ngày 27/07 sẽ ĐẾM 2 LẦN cùng 1 giá trị cổ tức.
"""
import csv
import os
import shutil
import sys

HIST = "/home/trido/thanhdt/WorkingClaude/data/execution_logs/nav_history_ZaloPay.csv"
BACKUP = HIST + ".bak_20260801_winston_fix0727"

TARGET_DATE = "2026-07-27"
NEW = {
    "date": TARGET_DATE,
    "nav": "833856620",
    "mtm_stock": "804077200",
    "cash": "29779420",
    "margin_debt": "0",
    "offbook_assets": "0",
    # Provenance THẬT của con số cash (bản đọc 27/07 tối đã hỏng) — không consumer nào
    # ràng buộc balance_ts phải cùng ngày với cột date (đã grep toàn repo trước khi ghi).
    "balance_ts": "2026-07-28T09:15:15",
}
EXPECT_OLD = {"nav": "804077200", "cash": "0"}


def main():
    with open(HIST, encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        fieldnames = rdr.fieldnames
        rows = list(rdr)

    hits = [r for r in rows if r["date"] == TARGET_DATE]
    if len(hits) != 1:
        print(f"❌ Tìm thấy {len(hits)} dòng {TARGET_DATE} (kỳ vọng đúng 1) — DỪNG.", file=sys.stderr)
        return 2
    old = dict(hits[0])
    for k, v in EXPECT_OLD.items():
        if old.get(k) != v:
            print(f"❌ Dòng {TARGET_DATE} có {k}={old.get(k)!r}, kỳ vọng {v!r} — file đã bị "
                  f"sửa bởi ai khác? DỪNG, không ghi đè mù.", file=sys.stderr)
            return 2

    if not os.path.exists(BACKUP):
        shutil.copy2(HIST, BACKUP)
        print(f"✔ Backup: {BACKUP}")
    print(f"CŨ : {old}")
    hits[0].update(NEW)
    print(f"MỚI: {dict(hits[0])}")

    tmp = HIST + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows({k: r.get(k, "") for k in fieldnames} for r in rows)
    os.replace(tmp, HIST)
    print("✔ Đã ghi (atomic tmp + os.replace).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
