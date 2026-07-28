---
kind: bigquery-column
status: TRAP
source: cột mirror t.VNINDEX trên hàng CỔ PHIẾU (trong tav2_bq.ticker VÀ ticker_prune)
group: price-volume
issue: CORRUPTED 2026-04-01..04-29 (LOW severity, CHƯA sửa)
detected: 2026-07-22 (job Winston_20260722_174537)
writer: bq_admin (cơ chế ghi không rõ)
---

# Cột mirror `t.VNINDEX` trên các hàng CỔ PHIẾU (trong `tav2_bq.ticker` VÀ `ticker_prune`)

**Status: ⚠️ TRAP — CORRUPTED 2026-04-01..04-29** (phát hiện 2026-07-22, job `Winston_20260722_174537`, LOW severity, CHƯA sửa)

## Là gì
Cột tiện ích gắn giá trị VNINDEX theo NGÀY lên mọi hàng cổ phiếu (để JOIN không cần join riêng bảng
index) — **KHÁC với hàng `ticker='VNINDEX'` gốc** (Open/High/Low/Close/Price/Volume của chính hàng đó
vẫn SẠCH, không liên quan).

## Ai ghi / cadence
bq_admin, cơ chế ghi không rõ (nghi 1 đợt bulk rewrite/backfill bỏ sót vài mã ít active).

## Bẫy
Trong đúng 20 phiên 04-01→04-29/2026, cột mirror bị làm tròn tới hàng chục (`ROUND(true_close,-1)`,
sai số ≤4,99 điểm/≤0,29%) trên ~1.256 mã (6 mã ít active C92/L43/SDV/VES/VMD/YBC vẫn giữ giá trị
thật; L43 còn lỗi riêng chia nhầm /1000). `ticker_1m` KHÔNG bị ảnh hưởng (bảng chỉ có từ 05-20).
**Production KHÔNG bị ảnh hưởng** — `macro_state_live.py` (DT5G)/`dna_report.py` đọc thẳng hàng
`ticker='VNINDEX'` gốc, không đụng cột mirror. Chỉ ảnh hưởng research/backtest nào lỡ đọc cột mirror
thay vì JOIN hàng VNINDEX gốc — sai số nhỏ (MA200 lệch ≤0,016%, lợi nhuận 6 tháng lệch ≤0,29%, hết
ảnh hưởng cửa sổ 6 tháng ~cuối 10/2026, MA200 ~giữa 2/2027). Còn 1 điểm lệch RIÊNG chưa gộp vào đây:
`2025-04-09` mirror=1132,79 vs Close thật=1094,30 (lệch 38,49 điểm, dấu hiệu khác — nghi sai ngày/dịch
hàng, chưa điều tra sâu). **Chưa báo bq_admin, chưa sửa** — quyết định chờ user.
