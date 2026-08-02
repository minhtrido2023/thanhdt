#!/usr/bin/env python3
"""One-off data fix — 5 dòng NAV lịch sử đếm 2 LẦN cổ tức tiền mặt (job Winston_20260802_082040).

BUG (coding_guidelines §21; báo cáo tuần 27–31/07/2026 Mục 11.5): DNSE ghi khoản
`cashDividendReceiving` vào `totalCash` ngay TỐI NGÀY CUỐI CÙNG CÒN HƯỞNG QUYỀN, trong khi giá
đóng cửa phiên đó VẪN CÒN quyền nhận cổ tức. daily_nav_snapshot.py (bản cũ) cộng nguyên
`totalCash` + cổ phiếu theo giá cum ⇒ cùng một khoản cổ tức đếm 2 lần, tự triệt tiêu ở phiên
sau. (Chốt chặn đã thêm vào daily_nav_snapshot.py cùng job này —
`cum_dividend_double_count()`, selfcheck `mike/bin/nav_cum_dividend_selfcheck.py` 38/38 PASS.)

USER ĐÃ DUYỆT sửa đúng 5 dòng dưới đây (2026-08-02). Mỗi con số đã được XÁC MINH ĐỘC LẬP,
KHÔNG copy từ báo cáo — 3 nguồn khớp từng đồng:
  1. `cashDividendReceiving` trong dnse_raw tăng đúng khoản đó vào đúng ngày (đã lọc accountNo).
  2. Vị thế point-in-time × cổ tức/cp suy từ tỉ số Close/Price của BQ (dividend_adjusted_return).
  3. Ex-date thật (BQ) nằm SAU ngày ghi nhận ⇒ giá phiên đó còn cum ⇒ đúng là đếm trùng.

  | ngày  | account | mã (qty × đ/cp)              | loại ra   | ex-date |
  |-------|---------|------------------------------|-----------|---------|
  | 16/07 | SpaceX  | BID 1.900 × 450              |   855.000 | 17/07   |
  | 24/07 | SpaceX  | NCT 500 × 8.000              | 4.000.000 | 27/07   |
  | 27/07 | SpaceX  | SAB 1.100 × 3.000            | 3.300.000 | 28/07   |
  | 16/07 | ZaloPay | BID 900 × 450                |   405.000 | 17/07   |
  | 24/07 | ZaloPay | NCT 373 × 8.000              | 2.984.000 | 27/07   |
  | 22/07 | ZaloPay | CTG 1.050 + VCB 800, × 450   |   832.500 | 23/07   |  ← duyệt sau (job ...085555)

Cột `cash` giảm đúng bằng khoản loại ra (khoản phải thu NẰM TRONG `totalCash` — đã kiểm: ngày
16/07 SpaceX totalCash tăng 857.770 = 855.000 cổ tức + 2.770 lãi tiền gửi), nên bất biến
`nav = mtm_stock + cash − margin_debt + offbook_assets` giữ nguyên. `mtm_stock` KHÔNG đổi.

DÒNG THỨ 6 — USER DUYỆT SAU (2026-08-02, job Winston_20260802_085555):
  * ZaloPay 22/07: cùng đúng lỗi này, +832.500đ (CTG 1.050 + VCB 800, × 450, ex-date 23/07)
    ⇒ nav 886.083.813 → 885.251.313. Ban đầu nằm NGOÀI phạm vi duyệt của 5 dòng trên; user
    duyệt riêng qua bus question `nav-zalopay-2207-dong-thu-6-can-duyet`. Đã xác minh lại 3
    nguồn ĐỘC LẬP từ dữ liệu gốc (không copy số từ bus question):
      1. Broker (đã lọc `account_no == 0001743768`): `cashDividendReceiving` 405.000 →
         1.237.500 lúc 22/07 19:04 ⇒ delta ĐÚNG 832.500. Số tiền trừ lấy theo delta
         `cashDividendReceiving` — KHÔNG theo delta `totalCash` — đúng như
         `cum_dividend_double_count()` định nghĩa (chỉ delta khoản phải thu mới nói được
         "bao nhiêu tiền cổ tức đang nằm trong totalCash"; delta totalCash lẫn cả tiền
         khớp lệnh/phí nên nhiễu). Cùng bản ghi đó `totalCash` chỉ +825.883, lệch 6.617đ —
         KHÔNG truy được về một trường phí/thuế cụ thể nào trong payload, nên KHÔNG khẳng
         định nguyên nhân. Phần lệch này không ảnh hưởng tính đúng của bản sửa vì số trừ
         lấy theo kênh `cashDividendReceiving`, và kênh đó đã được 3 nguồn độc lập khác
         xác nhận đúng từng đồng (quant-skeptic 2026-08-02 nêu đúng điểm này).
      2. Vị thế point-in-time bản ghi `positions` cuối ngày 22/07: CTG openQuantity 1.050,
         VCB 800 (khớp chính xác).
      3. Ex-date thật từ BQ (`detect_adjustments_batch`): CTG và VCB đều ex 23/07,
         last_cum_date 22/07, per_share 450đ ⇒ giá đóng cửa 22/07 CÒN cum ⇒ đúng là đếm trùng.
    Quét TOÀN BỘ 14 mã ZaloPay cửa sổ 20–26/07: CHỈ CTG + VCB có ex-date 23/07, tổng
    1.050×450 + 800×450 = 832.500 = ĐÚNG BẰNG delta của broker ⇒ quy kết đầy đủ, không sót mã.
  * ZaloPay 27/07: ĐÃ đúng sẵn (fix_nav_zalopay_20260727.py đã trừ 2.232.000đ cổ tức SAB);
    script này chỉ ghi bổ sung cột `cum_dividend_excl` cho dòng đó — KHÔNG đổi nav/cash/mtm.
  * SpaceX 22/07: cũng dính (+1.620.000) nhưng KHÔNG có dòng NAV nào ngày đó → không phải sửa.
  * SpaceX 09/07 (+2.400.000, MBB): quant-skeptic quét ngược tới ngày go-live nêu đây là mục
    còn mở. ĐÃ TRA LẠI, KHÔNG PHẢI lỗi này — MBB ex-date = 09/07, last_cum_date = 08/07; mà
    `cashDividendReceiving` của SpaceX ngày 08/07 (bản ghi 15:00:15) = 0, tới 09/07 mới thành
    2.400.000. Tức khoản phải thu chỉ vào tiền ĐÚNG PHIÊN ex, khi giá đã rơi ⇒ tiền và giá
    không cùng lúc chứa cổ tức ⇒ KHÔNG đếm trùng, không sửa. Đây đúng là ca mẫu đã ghi trong
    docstring `cum_dividend_double_count()` ("BQ trả lời dứt khoát: không còn ex-date nào phía
    sau 09/07 ⇒ KHÔNG trừ. Đúng."). Sau khi loại ca này: 6 dòng đã sửa là ĐẦY ĐỦ.
"""
import csv
import os
import shutil
import sys

EXEC_DIR = "/home/trido/thanhdt/WorkingClaude/data/execution_logs"
BACKUP_SUFFIX = ".bak_20260802_winston_cum_dividend_double_count"
RUN_TAG = "Winston_20260802_085555"   # job sửa dòng thứ 6 (ZaloPay 22/07)
FIELDNAMES = ["date", "nav", "mtm_stock", "cash", "margin_debt", "offbook_assets",
              "balance_ts", "cum_dividend_excl"]

# account -> date -> (nav cũ, cash cũ, khoản loại ra)
FIXES = {
    "SpaceX": {
        "2026-07-16": (957_558_637, 305_388_637, 855_000),
        "2026-07-24": (910_995_894, 47_065_894, 4_000_000),
        "2026-07-27": (900_428_641, 22_173_641, 3_300_000),
    },
    "ZaloPay": {
        "2026-07-16": (953_593_885, 168_398_885, 405_000),
        "2026-07-22": (886_083_813, 21_640_713, 832_500),   # dòng thứ 6, duyệt 2026-08-02
        "2026-07-24": (849_855_112, 27_380_812, 2_984_000),
    },
}
# Dòng đã đúng số tiền, chỉ điền cột tài liệu hoá (không đụng nav/cash/mtm).
ANNOTATE_ONLY = {"ZaloPay": {"2026-07-27": 2_232_000}}


def _num(row, key):
    return float(row.get(key) or 0)


def check_invariant(rows, label):
    bad = [(r["date"], _num(r, "nav"),
            _num(r, "mtm_stock") + _num(r, "cash") - _num(r, "margin_debt") + _num(r, "offbook_assets"))
           for r in rows
           if abs(_num(r, "nav") - (_num(r, "mtm_stock") + _num(r, "cash")
                                    - _num(r, "margin_debt") + _num(r, "offbook_assets"))) >= 1]
    if bad:
        print(f"❌ {label}: bất biến NAV SAI ở {len(bad)} dòng:", file=sys.stderr)
        for d, lhs, rhs in bad:
            print(f"     {d}: nav={lhs:,.0f} ≠ mtm+cash−nợ+offbook={rhs:,.0f}", file=sys.stderr)
        return False
    print(f"✔ {label}: bất biến nav = mtm_stock + cash − margin_debt + offbook_assets "
          f"đúng trên TOÀN BỘ {len(rows)} dòng.")
    return True


def process(account, apply_changes):
    path = os.path.join(EXEC_DIR, f"nav_history_{account}.csv")
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not check_invariant(rows, f"{account} TRƯỚC khi sửa"):
        print(f"❌ {account}: file đã sai bất biến TRƯỚC khi sửa — DỪNG, không ghi đè mù.",
              file=sys.stderr)
        return None

    by_date = {}
    for r in rows:
        by_date.setdefault(r["date"], []).append(r)

    for date, (old_nav, old_cash, excl) in FIXES.get(account, {}).items():
        hits = by_date.get(date, [])
        if len(hits) != 1:
            print(f"❌ {account} {date}: tìm thấy {len(hits)} dòng (kỳ vọng đúng 1) — DỪNG.",
                  file=sys.stderr)
            return None
        row = hits[0]
        # Idempotent (coding_guidelines §5): dòng đã sửa ở lần chạy trước phải nhận ra là
        # ĐÃ XONG, không phải "ai đó sửa bậy". Chỉ coi là đã-áp-dụng khi khớp CẢ BA:
        # nav mới, cash mới VÀ cột chứng cứ cum_dividend_excl đúng bằng khoản loại ra.
        if (abs(_num(row, "nav") - (old_nav - excl)) < 1
                and abs(_num(row, "cash") - (old_cash - excl)) < 1
                and abs(_num(row, "cum_dividend_excl") - excl) < 1):
            print(f"  {account} {date}: ĐÃ SỬA TỪ TRƯỚC (nav={old_nav - excl:,.0f}, "
                  f"loại {excl:,.0f}) — bỏ qua, không trừ lần hai.")
            continue
        if abs(_num(row, "nav") - old_nav) >= 1 or abs(_num(row, "cash") - old_cash) >= 1:
            print(f"❌ {account} {date}: nav={row['nav']} cash={row['cash']}, kỳ vọng "
                  f"{old_nav}/{old_cash} — file đã bị ai khác sửa? DỪNG.", file=sys.stderr)
            return None
        print(f"  {account} {date}: nav {old_nav:,.0f} → {old_nav - excl:,.0f} · "
              f"cash {old_cash:,.0f} → {old_cash - excl:,.0f} · loại {excl:,.0f}")
        row["nav"] = f"{old_nav - excl:.0f}"
        row["cash"] = f"{old_cash - excl:.0f}"
        row["cum_dividend_excl"] = f"{excl:.0f}"

    for date, excl in ANNOTATE_ONLY.get(account, {}).items():
        hits = by_date.get(date, [])
        if len(hits) == 1 and not hits[0].get("cum_dividend_excl"):
            hits[0]["cum_dividend_excl"] = f"{excl:.0f}"
            print(f"  {account} {date}: chỉ ghi chú cum_dividend_excl={excl:,.0f} "
                  f"(nav/cash GIỮ NGUYÊN — đã đúng từ trước)")

    if not check_invariant(rows, f"{account} SAU khi sửa"):
        return None
    if not apply_changes:
        print(f"  (dry-run — chưa ghi {path})")
        return rows

    backup = path + BACKUP_SUFFIX
    if not os.path.exists(backup):
        shutil.copy2(path, backup)
        print(f"✔ Backup: {backup}")
    # Backup riêng CHO LẦN CHẠY NÀY: bản trên giữ trạng thái gốc trước 5 dòng đầu, khôi phục
    # nó sẽ revert cả 6 dòng. Bản này cho phép revert đúng thay đổi của lần chạy hiện tại.
    run_backup = f"{path}.bak_{RUN_TAG}"
    if not os.path.exists(run_backup):
        shutil.copy2(path, run_backup)
        print(f"✔ Backup lần chạy này: {run_backup}")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        w.writeheader()
        w.writerows({k: r.get(k, "") for k in FIELDNAMES} for r in rows)
    os.replace(tmp, path)          # atomic (coding_guidelines §5)
    print(f"✔ Đã ghi {path} (atomic tmp + os.replace).")
    return rows


def main():
    apply_changes = "--apply" in sys.argv
    if not apply_changes:
        print("DRY-RUN (thêm --apply để ghi thật)\n")
    for account in ("SpaceX", "ZaloPay"):
        print(f"── {account} ──")
        if process(account, apply_changes) is None:
            return 2
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
