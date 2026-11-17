# r3 — mục đã áp (job Taylor_20261117_155604)
assumptions md5 `55731df5d9c0c9292b5695cc5d6c4cce` (trước `44d627986de32354c80f18be29b5ee1e`). calc.py chạy lại: `/tmp/calc_r3.out`.

| Mục | Trạng thái | Vị trí |
|---|---|---|
| A | ÁP. 3 mốc ROE 13,2% / 14,6% / 16% ⇒ 28.958 / 35.497 / 42.035. **Tâm = 14,6%** (trung điểm; lý do: 13,2% bỏ tăng PPOP 2026, 16% dùng PPOP đỉnh NIM). Bỏ chữ "thận trọng". Đây là PHÁN ĐOÁN của tôi (ước lượng), Mike/user đổi được: chỉ cần sửa `scenarios.base.roe` | assumptions:`roe_anchors`, `scenarios.base`; REPORT:15-17, :26-27, §5 "Ba mốc ROE bền" (~:134-137), bảng kịch bản, độ nhạy, moat :205-207 |
| B | ÁP. "phụ thuộc mô hình" → "độ nhạy theo r/Ke" (giá 52.100 chỉ đạt ở Ke ≈11,4% hoặc ROE ≈18,2%) | REPORT:~156 |
| C | ÁP. CBBank (= NH TNHH MTV Ngoại thương Công nghệ số) được miễn hợp nhất/loại khỏi CAR, ghi nguồn skeptic R2 (chưa tự đối chiếu); bỏ câu NCI 92 tỷ; trigger viết lại (hỗ trợ >5% LNST HOẶC bỏ miễn trừ) | REPORT:117-121, §9 :233 |
| D1 | ÁP. VCSH đầu kỳ 196.112,9 (nguồn skeptic R2, chưa tự đối chiếu BCTC KT) | calc.py:48; REPORT §10 |
| D2 | ÁP. Xoá câu đính chính "g1 10% ≈ 52.100" | REPORT:~168 |
| D3 | **KHÔNG ÁP** "bảo lãnh nhân 2,37": brief không nói nhân vào đại lượng nào, repo không có nguồn; không đoán | — |
| D4 | **KHÔNG ÁP** "cổ tức tiền trừ 2%": không rõ trừ khỏi tỷ lệ chia ~10% hay khỏi g; không đoán | REPORT:136,160 (chờ làm rõ) |

## Tâm / biên mới (r 13,5%, g 7%)
- Tâm **35.497**; có trọng số **39.137**; Ke ±100bp **30.764–41.950**; rẻ ≤ 30.200
- Mốc ROE: 13,2% **28.958** · 14,6% **35.497** · 16% **42.035**
- Ke β thật 12%: **46.145** (dưới giá 52.100); giá hàm ý ROE 18,15% hoặc Ke 11,43%
- Hai giai đoạn (Ke 13,5%): 36.843 / 36.135; (12,5%): 45.069 / 43.429
- Kịch bản: xấu 30.359 · bull 55.198 (không đổi)
