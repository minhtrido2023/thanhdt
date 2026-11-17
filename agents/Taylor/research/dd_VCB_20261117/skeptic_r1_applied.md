# skeptic_r1 — mục đã áp (job Taylor_20261117_111929)
assumptions md5 mới `44d627986de32354c80f18be29b5ee1e` (cũ acba98b2…). Tâm 42.035 / có trọng số 42.407 **không đổi** (ROE base 16% là giả định, không suy từ ROE lõi).

| # | Mục | Trạng thái | Vị trí |
|---|---|---|---|
| 1 | Thuế lãi đánh giá lại 0% | **ÁP** — LN lõi 29.861, tăng +12,5% (cũ 14,9%), ROE lõi 16,65% (cũ 17,0%) | assumptions:11; REPORT:23, :43, :49, :133, bảng §0; md5 REPORT:11 |
| 2 | Cơ cấu dự phòng 9.180 | **ÁP** — tách 6.190 cho vay + 2.997 TPDN; CC cho vay 0,47%; bỏ "chưa kiểm"; khoản 3,36→6,35 là dự phòng TPDN; CC 0,8% ≈ 1,7×; thêm chiều tốt (đã trích 97%) | REPORT:61-63, :81, :87, :89-90 (ngoại bảng), :134, :187 (§7 macro) |
| 3 | Bảng P/B 5 năm + BID/CTG/NH tư nhân | **ÁP** — BQ `ticker.PB` 2021-11-17→2026-11-17, đúng số skeptic (VCB 1,72 / P10 2,16 / TV 2,83; BID 1,19; CTG 1,16) | REPORT §5 sau "Vùng đọc" (~:170) |
| 4 | Hai giai đoạn | **ÁP, CÓ LỆCH**: tâm 45.100 ✓; Ke −100bp 54.900 ✓; **"g1 10% ≈ 52.100" chỉ đúng ở Ke 12,5%** — ở Ke 13,5% là 43.500. Ghi cả hai. Nhãn "đắt" → "đầu trên / đắt nhẹ, phụ thuộc mô hình" | REPORT:155-156, :159-168; calc.py:50-55 |
| 5 | ADV | **ÁP** — 175 tỷ (3 năm Price×Volume); 153 (Close×Volume); 281 (1 năm); 5% ≈ 8,75 tỷ/phiên | REPORT:28, :154; assumptions:20 |
| 6 | VCSH đầu kỳ 196.200 + đọc BCTC KT 2025 | **KHÔNG ÁP ĐƯỢC** — Read PDF cần poppler (không có); `pip install pymupdf` bị classifier chặn, tôi không lách. calc.py:48 giữ 196.200 nhưng gắn nhãn ước lượng; REPORT §10 ghi rõ chưa đọc (ý kiến KT, VCSH đầu kỳ, KH lớn/BĐS). Ngoại bảng +38%/+88% YTD (BCTC Q3 tr.18, lấy từ đính chính skeptic, **chưa tự đối chiếu trang**) đã ghi WARNING. | calc.py:48; REPORT:8, :89-90, §10 |

Chưa chạm: Ke 13,5% tâm, β thật mốc đọc, moat NARROW, pháp lý, mốc khoá. Không ghi dd_price_zones.json/PDF/email.
