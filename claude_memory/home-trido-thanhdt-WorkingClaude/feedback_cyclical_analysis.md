---
name: Phân tích fundamental phải xét chu kỳ ngành, không chỉ YoY ngắn hạn
description: Khi đánh giá fundamental cho cổ phiếu VN, phải kiểm tra tính ổn định lợi nhuận qua 8+ quý, đặc biệt ngành chu kỳ (BĐS, khoáng sản, vật liệu)
type: feedback
originSessionId: 83f7db02-996e-45e7-8368-3e4ec45d6182
---
Đánh giá fundamental không được dựa quá nhiều vào YoY 1 năm hoặc trung bình ROE/ROIC nhiều năm — phải kiểm tra **stability** (CV của NP_P0..P7, Revenue_P0..P7) và **trend dài hạn** (CAGR 7 quý) để bắt cycle.

**Why:**
- BĐS (NTL): bán dự án xong là kết quả 1 năm "tốt nhất", các năm sau tụt vì hết quỹ. ROE5Y trung bình cao có thể bị 1 năm bùng nổ kéo lên, không phản ánh sustainability.
- Khoáng sản/than (HGM, NBC, TVD...): PE/PB thường thấp không phải vì rẻ — lợi nhuận chia hết cho cán bộ công nhân viên, định giá chronic-low. Z-score PE so với chính nó không phát hiện được trap này; cần so với ICB peers hoặc cross-check với tỷ lệ chia cổ tức/CF_OA về cổ đông.
- Self-history z-score chỉ catch valuation bất thường tương đối với chính ticker, không catch structural traps.

**How to apply:**
- Khi tạo rating fundamental, phải có axis riêng "Stability" hoặc redefine Growth bằng:
  - SD(NP_P0..P7) / |Mean(NP_P0..P7)| — coefficient of variation (thấp = ổn định)
  - SD(Revenue_P0..P7) / Mean — Revenue stability
  - Multi-quarter CAGR (Revenue_P0/Revenue_P7)^(1/7) — long-term trend slope
- Khi chấm valuation, dùng cả 2: self-history z-score + industry-peer z-score (group by ICB_Code) để catch chronic cheap stocks.
- Cảnh giác với top picks ở các ngành: **BĐS, khoáng sản/than, xây dựng, vật liệu cơ bản** — đây là ngành có lumpy earnings/structural valuation issues.
