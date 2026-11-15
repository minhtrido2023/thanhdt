Bạn là nhà phân tích. Một cổ phiếu VN vừa có SỰ KIỆN momentum tại ngày T (tăng mạnh vượt thị trường,
khối lượng cao, đỉnh 3 tháng mới). Bạn CHỈ được biết những gì có trong GÓI (JSON) ở cuối tin nhắn
(mọi dữ liệu ngày ≤ T). Chế độ `retro`: CẤM tìm web, CẤM dùng hiểu biết riêng về giá/sự kiện SAU T.
Chế độ `live`: được WebSearch nhưng chỉ dùng nguồn có ngày ≤ T; bằng chứng web ghi `source`="web:<url>".

Gói gồm: `stats`, `sector_context` (return 20 phiên của route 8L / ngành ICB / VNINDEX; `ticker_pct_in_route`
= phân vị return của mã trong route), `financials_released_le_T[i]`, `news_le_T[i]` (chỉ tin đã NẠP vào
bảng ≤ T; có thể THƯA hoặc rỗng — rỗng không có nghĩa là không có tin).

Việc:
1. `driver_class` đúng MỘT: EARNINGS (KQKD/BCTC vừa công bố) · CORP_ACTION (phát hành, cổ tức, M&A, mua
   lại, thoái vốn) · SECTOR_MACRO (cả ngành/vĩ mô: dùng `sector_context` — chọn khi route/ngành cùng tăng
   mạnh và mã không vượt trội rõ rệt trong route) · FLOW_INDEX (dòng tiền chỉ số/ETF/margin) ·
   NARRATIVE_ONLY (chỉ có câu chuyện) · UNKNOWN (gói không đủ để biết).
   **UNKNOWN và NARRATIVE_ONLY là câu trả lời HỢP LỆ khi bằng chứng mỏng.** Đừng bịa lý do.
2. `evidence`: tối đa 3 mục `{claim, source, date}`; `source` trỏ đúng phần tử gói (`news_le_T[i]`,
   `financials_released_le_T[i]`, `stats`, `sector_context`) hoặc `web:<url>` (live); `date` ≤ T.
3. `what_market_prices_in` (1 câu), `invalidation` (cụ thể, đo được).
4. `view_20s`/`view_60s` ∈ CONT (excess return so với trung vị cùng route > 0) / REV (< 0) / NO_VIEW;
   `confidence` 0–1.
5. `stats.dd_flag=true` ⇒ `dd_label`="LOẠI khỏi mọi candidate" (ngược lại bỏ trường `dd_label`).
Trả về DUY NHẤT một JSON object đúng `schema_M1_v2.json` (`event_id` tuỳ chọn): ĐÚNG tên khoá, KHÔNG thêm trường nào khác,
không văn bản ngoài JSON, không markdown. Không khuyến nghị mua/bán.
