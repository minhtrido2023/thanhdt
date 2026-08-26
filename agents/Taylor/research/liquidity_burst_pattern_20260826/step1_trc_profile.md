# Bước 1 — Profile TRC (Cao su Tây Ninh)

## Timeline đo được (BQ `tav2_bq.ticker` + `ticker_financial` + `corporate_action`, 2026-08-26)

**Giai đoạn tích lũy 1**: ADV_3M (rolling 63 phiên, VND) < 2 tỷ liên tục **2022-07 → 2024-09
(27 tháng)** — vượt xa ngưỡng 6 tháng. Đáy sâu nhất 0,15-0,2B (2018, 2021, 2023-2024).

**Catalyst = BCTC, KHÔNG PHẢI corp-action** (khác giả thuyết ban đầu — corp-action 1:3 là sự
kiện MỚI 2026, tách biệt khỏi burst 2024-2025 đã xảy ra):
- 2024Q3 (release 2024-10-14): NP 73,1B (vs 12,8B Q2, vs 12,3B cùng kỳ 2023) — GPM nhảy 20,6%→28,4%.
- 2024Q4 (release 2025-01-20): NP 120,0B, Revenue_YoY +22,3%, GPM 36,4% — quý đỉnh.
- 2025Q1 (release 2025-04-22): NP 70,4B, Revenue_YoY +55,4%.
- Không có corp-action ISS/split nào trong cửa sổ này (kiểm tra toàn bộ lịch sử `corporate_action`
  của TRC 2007-2026: chỉ có DIV tiền mặt hàng năm, event ISS DUY NHẤT là 2026-08-18 "Cổ phiếu
  thưởng" tỷ lệ 1:3 — status `announced`, exright_date 2026-09-15, **CHƯA THỰC HIỆN**).

**Burst**: ADV_3M 2024-09 (0,74B) → 2024-10 (2,17B, ×2,9 ngay tháng release) → 2025-01 (7,76B) →
đỉnh 2025-04 (17,95B) = **×24 từ đáy**, vượt xa điều kiện ×3/2B trong 3 tháng.

**Giá**: Close 2024-08-14: 34.840đ → 2024-10-14 (catalyst): 38.610đ (+10,8% pre-move, thị trường
đã bắt đầu phản ứng TRƯỚC khi ADV bùng nổ đầy đủ) → đỉnh 2025-02-20: 79.990đ (**+107%** so với
catalyst date, **+130%** so với đáy tháng 8) → phân phối về 2025-04-22: 60.090đ (**-25% từ đỉnh**,
vẫn +56% so với catalyst). VNINDEX cùng kỳ: 1230→1287→1197 (đi ngang/giảm nhẹ) — TRC outperform
rõ rệt, không phải beta thị trường.

**Giai đoạn tích lũy 2 (đang mở, KHÔNG ĐỦ 6 tháng)**: ADV_3M giảm lại 2026-04 (5,27B) → 2026-06
(2,47B, gần chạm ngưỡng 2B nhưng KHÔNG xuống dưới liên tục ≥6 tháng) → 2026-07 (3,33B) → catalyst
mới (thông báo bonus 1:3, 2026-08-18) → 2026-08 ADV đã nhích lên 5,94B (thị trường pre-position
trước ex-date, CHƯA burst thật vì exright_date 2026-09-15 chưa tới). Giá 2026-08-18: 82.600đ →
2026-08-25: 86.100đ.

## Kết luận Bước 1
1. **Case TRC gốc (2024-2025) là BCTC-driven, không phải corp-action-driven** — giả thuyết ban đầu
   của user (nhắc "chia cổ phiếu 1:3") mô tả đúng sự kiện **hiện tại** (2026-08, chưa xảy ra burst)
   nhưng KHÔNG phải cơ chế đã tạo ra burst lịch sử 2024-2025. Hai catalyst khác nhau, cùng 1 mã,
   cách nhau ~2 năm — TRC là **2 episode LBC nối tiếp**, episode 1 đã hoàn thành đầy đủ 4 pha
   (tích lũy→catalyst→burst→phân phối), episode 2 mới ở pha catalyst, chưa có burst.
2. Pattern định nghĩa ở Bước 2 (LBC) cần mở rộng catalyst = BCTC HOẶC corp-action, không chỉ
   corp-action — episode 1 của chính seed case sẽ bị bỏ sót nếu chỉ scan corp-action.
3. Độ trễ giữa catalyst và burst đỉnh: ~4 tháng (release 2024-10-14 → đỉnh ADV 2025-04, đỉnh giá
   2025-02). Return đã bắt đầu di chuyển ngay tại ngày release (giá +10,8% từ T-60 đến T0) — dấu
   hiệu khả năng có "leak"/accumulation sớm trước khi ADV chính thức breakout.
