---
name: Bắt buộc backtest MCP trước khi đề xuất cải tiến
description: Mọi đề xuất cải tiến filter/sell pattern/weight phải được validate qua MCP simulation trước khi trình bày, không chỉ dựa trên phân tích profile_hit.csv
type: feedback
originSessionId: afd1283e-9ed8-4ec5-8a51-488c813fe806
---
Khi đề xuất cải tiến (sell pattern, buy filter, weight, scoring), phải hoàn thành workflow đủ 3 bước trước khi kết luận:

**Bước 1 — Phân tích trên profile_hit.csv:**
- Tính win rate, avg profit, profit factor theo từng sell pattern / strategy
- Xác định điểm yếu cần cải thiện (VD: cutloss rate cao, holding quá dài, sell quá sớm)

**Bước 2 — Đề xuất cải tiến và build dict_filter mới:**
- Điều chỉnh filter expression / sell pattern / weight cụ thể
- Ghi rõ lý do thay đổi và kỳ vọng

**Bước 3 — Backtest qua MCP simulation (BẮT BUỘC):**
- Submit job với dict_filter mới lên MCP simulation_v1_6_webui
- So sánh kết quả vs baseline (profile email hiện tại)
- Chỉ kết luận đề xuất hiệu quả nếu MCP simulation cho thấy cải thiện rõ ràng trên ít nhất: CAGR, Sharpe, hoặc Calmar

**Why:** Phân tích trên profile_hit.csv chỉ đánh giá từng deal riêng lẻ, không phản ánh hiệu ứng portfolio (utilization, slot competition, market timing). Một sell pattern tốt trên paper có thể làm giảm CAGR thực tế do giảm holding time hoặc tăng cash idle.

**How to apply:**
- Không trình bày đề xuất là "cải tiến" nếu chưa qua bước 3
- Nếu MCP simulation không cho thấy cải thiện rõ → nói thẳng và giải thích tại sao kết quả khác với kỳ vọng từ bước 1
- Với đề xuất nhiều thay đổi cùng lúc: test từng thay đổi riêng để biết cái nào có tác dụng
