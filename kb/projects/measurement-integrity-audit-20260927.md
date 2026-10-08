# Measurement integrity audit — bối cảnh mở cadence (2026-09-27)
> Chuyển nguyên văn từ `kb/current_ops.md` (trim context_pack 2026-10-08). Lịch review quý vẫn ở file gốc.

## Chuyển từ kb/current_ops.md L123-128 (trim 2026-10-08, Wags_20261008_133659) — Lý do mở cadence
Lý do: bug custom30V double-count (`mcap = Close_adj × OShares`, −4,48pp CAGR) sống trong
production nhiều tháng, KHÔNG bị bắt bởi self-check 0 VND (kiểm sổ sách mô phỏng, không kiểm
tính đúng kinh tế của công thức) LẪN quant-skeptic (7 đòn cũ nhắm overfit/gaming, không nhắm lỗi
kế toán double-count). Chỉ lộ ra vì có audit CHỦ ĐỘNG quét 23 chuỗi return/level/weight/NAV theo
6 bất biến cố định — audit đó còn tìm thêm 7 bug không liên quan (FAIL-C/F/H, egg reconcile,
FAIL-G ICB routing, DSR/PBO family drift). Kết luận: không đợi ai đó thấy số lạ mới đi tìm.

