---
name: feedback-us-vn-correlation-interpretation
description: "Khi diễn giải US-VN correlation, tail dependence là yếu tố chính (NĐT Việt nhạy thông tin khủng hoảng); index-level decoupling phải kiểm chứng bằng breadth equal-weight trước khi kết luận"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a2b28dda-6763-49ca-a45e-ecb188ff20d4
---

Khi research/diễn giải tương quan VN ↔ US (đặc biệt downside contagion), tuân theo 2 nguyên tắc sau:

**1. Tail risk LÀ câu chuyện chính, không phải correlation trung bình**

Why: NĐT Việt cá nhân nhạy bén với thông tin khủng hoảng toàn cầu (margin call, foreign outflow, panic news). Mean correlation ~0.12-0.24 trông yếu nhưng đó là average của 2 chế độ trộn lẫn — điều thực sự matter là khi US rơi vào left tail (q ≤ 5%), VN có xác suất rơi cùng ×3-5 baseline. Đừng dán nhãn "yếu" lên correlation tổng quát rồi bỏ qua tail.

How to apply: trong report về US-VN linkage, ưu tiên trình bày (a) tail dependence ở q=1%/5%/10%, (b) conditional VN distribution theo US regime, (c) threshold scan SPX_DD bin → VN forward MaxDD. Hạn chế dùng full-sample Pearson làm kết luận chính.

**2. "Index decoupling" có thể là composition artifact — phải kiểm bằng breadth equal-weight**

Why: VNINDEX cap-weighted dễ bị 5-10 large-cap (VIC, VHM, VCB, BID, HPG...) dominate. Ví dụ 2025 tariff window: VNINDEX +42% trong khi SPX -19% trông như decoupling mạnh — NHƯNG equal-weight prune (453 tickers) chỉ median +6%, p25 -10%, 41% cổ phiếu flat-or-negative, chỉ 19% beat VNINDEX. Đó là VIC-led rally, không phải broad market decoupling. Báo cáo nói "VN decoupled" mà không check breadth là sai bản chất.

How to apply: trước khi gọi một episode là "VN decoupled" với US, query breadth (equal-weight mean/median/% positive) trên `tav2_bq.ticker` ∩ `ticker_prune` cho window đó. Nếu median EW << index return → đó là narrow leadership, không phải broad decoupling — sửa narrative tương ứng. Pattern SQL: lấy first/last close mỗi ticker trong window, tính return, aggregate.

Liên quan: [[breadth-universe-finding]] (luôn dùng ticker_prune cho breadth, không dùng all-1272), [[tam-quan-v3-1-spec]] (US override BEAR/CRISIS cap).
