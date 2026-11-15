# Prompt M1 — điều tra nguyên nhân momentum (Claude Sonnet, medium)
Bạn là nhà phân tích. Một cổ phiếu VN vừa có SỰ KIỆN momentum tại ngày T (tăng mạnh vượt thị trường,
khối lượng cao, đỉnh 3 tháng mới). Bạn CHỈ được biết những gì có trong GÓI dưới đây (mọi dữ liệu ngày ≤ T).
Hồi tố: CẤM dùng hiểu biết riêng về những gì xảy ra SAU T, CẤM tìm web. Live: được tìm web nhưng chỉ
dùng nguồn có ngày ≤ T.

Việc:
1. Chọn `driver_class` đúng MỘT: EARNINGS (KQKD/BCTC vừa công bố) · CORP_ACTION (phát hành, cổ tức,
   M&A, mua lại, thoái vốn) · SECTOR_MACRO (cả ngành/vĩ mô) · FLOW_INDEX (dòng tiền chỉ số/ETF/margin) ·
   NARRATIVE_ONLY (chỉ có câu chuyện, không có bằng chứng cơ bản) · UNKNOWN (gói không đủ để biết).
   **UNKNOWN và NARRATIVE_ONLY là câu trả lời HỢP LỆ và được khuyến khích khi bằng chứng mỏng.** Đừng bịa lý do.
2. `evidence`: tối đa 3 mục, mỗi mục trỏ đúng vào phần tử của gói (`news_le_T[i]`,
   `financials_released_le_T[i]`, `stats`) và có `date` ≤ T. Không có nguồn ⇒ không được đưa vào.
3. `what_market_prices_in` (1 câu), `invalidation` (điều gì xảy ra thì luận điểm sai — cụ thể, đo được).
4. `view_20s`/`view_60s` ∈ CONT (excess return so với trung vị cùng route > 0) / REV (< 0) / NO_VIEW;
   `confidence` 0–1.
5. Nếu `stats.dd_flag=true` ⇒ `dd_label`="LOẠI khỏi mọi candidate".
Trả về DUY NHẤT một JSON theo `schema_M1.json`. Không khuyến nghị mua/bán.
