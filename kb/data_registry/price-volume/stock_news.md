---
kind: bigquery-table
status: PARTIAL
source: lithe-record-440915-m9.tav2_bq.stock_news
group: price-volume
scope: tin công bố thông tin doanh nghiệp per mã (cổ tức, M&A/sở hữu, phát hành, mua lại CP quỹ, tạm ngừng GD...) — nguồn NGÀY CÔNG BỐ cho event-study / first-disclosure
writer: UNKNOWN — không script/cron nào trong repo Mike ghi bảng này (grep mike/bin, root *.py/*.sh, crontab: 0 hit, 2026-10-20). Ghi bởi vendor/pipeline ngoài repo, cùng họ với treasury_news.
verified_at: 2026-10-20 (bq query thật, job Winston_20261020_113649)
---

# `tav2_bq.stock_news`

**Status đề xuất: PARTIAL** — dùng được làm nguồn *ngày công bố đầu tiên* cho sự kiện doanh nghiệp,
nhưng PHẢI qua bộ lọc PIT dưới đây; KHÔNG dùng `ingested_at` làm thời điểm biết tin.

## Là gì (đo thật 2026-10-20)
- 60.311 dòng, 13,5 MB, 1.730 mã, `id`/`news_id` đều duy nhất (60.311 distinct). Tạo 2026-09-13 19:23 UTC,
  sửa lần cuối 2026-10-19 16:03 UTC. Partition THÁNG theo `public_date`, cluster `ticker`.
- `public_date` 2015-03-02 → 2026-10-16 (không NULL). Không có cột `title` NULL ở mẫu; `ticker` không NULL.
- Schema: `id`, `ticker`, `news_id`, `title`, `short_content`, `public_date` (DATE), `public_datetime`
  (STRING), `matched_event_codes`, `action_type`, `shares_delta`, `ref_price`, `category`, `icb_code`,
  `source`, `source_link`, `image_url`, `first_ingested_at` (STRING), `ingested_at` (TIMESTAMP).
- **Cột chết (100% NULL):** `ref_price`, `category`, `icb_code`, `source`, `source_link`, `short_content`
  (và `image_url` chưa xác minh). Đừng wire.
- `matched_event_codes` (phân loại bằng rule trên tiêu đề, KHÔNG phải nhãn vendor): DIV 27.233 · MA 14.127 ·
  ISS 9.156 · DIV,ISS 4.154 · BUYBACK 2.175 · AIS 1.824 · SUSP 1.034 · NLIS 173 · MOVE 168 + tổ hợp nhỏ.
  Không có mã BCTC: tin BCTC phải bắt bằng regex tiêu đề (`báo cáo tài chính|BCTC` = 13.233 dòng) — do `DIV`
  chiếm đa số, đừng suy "không có BCTC".
- `action_type` chỉ 2.384/60.311 (3,95%) có giá trị (họ BUYBACK: `buy_done`, `sell_done`...);
  `shares_delta` chỉ 568 dòng (0,94%). Muốn dữ liệu buyback có cấu trúc → `treasury_news_buyback.md`.

## Độ phủ theo năm (dòng / số mã)
2015 874/365 · 2016 2.930/788 · 2017 3.173/918 · 2018 4.375/1.083 · 2019 5.679/1.342 · **2020 11.200/1.551 ·
2021 11.248/1.550** · **2022 3.958/1.025** · 2023 4.448/1.087 · 2024 4.348/1.044 · 2025 4.432/1.028 · 2026
(tới 10-16) 3.646/1.019.
- ⚠️ **Gãy chuỗi:** 2020–2021 gấp ~2,5× các năm sau; sụt đột ngột từ 2021-10 (374/tháng) → 2022-02 (119/tháng).
  Mật độ tin/mã KHÔNG đồng nhất theo thời gian ⇒ cấm đếm "số tin" làm tín hiệu xuyên 2021→2022 (đổi phủ
  nguồn, không phải đổi hoạt động doanh nghiệp). Nguyên nhân chưa xác minh.
- Trước ~2016 thưa (365 mã năm 2015).

## Bẫy PIT / look-ahead
1. **`ingested_at` KHÔNG phải thời điểm công bố.** 59.603 dòng (98,8%) có `ingested_at` = 2026-09-13 (một lần
   backfill; `public_date` ≤ 2026-09-04). Sau đó nạp tăng dần nhưng **trễ**: 663 dòng nạp muộn >3 ngày sau
   `public_date`; ngày 2026-10-19 nạp 199 dòng có `public_date` lùi tới 2024-10-25 (đợt vá, ETF `FUE*`).
   ⇒ Một tin có `public_date`=T có thể chỉ xuất hiện trong bảng ở T+vài ngày hoặc cả năm sau. Backtest
   dùng `public_date` như thể mọi tin đều có mặt ngay là **look-ahead nhẹ về độ phủ**; live thì luôn trễ.
   Không có vintage/snapshot của bảng này (khác `corporate_action_snapshots`).
2. **`public_date` là ngày công bố (đúng), `public_datetime` là STRING.** `public_date` = phần ngày của
   `public_datetime` ở 100% dòng (0 lệch). Nhưng 59.612 dòng `public_datetime` là giờ địa phương KHÔNG
   có múi giờ (ICT ngầm định); chỉ ~699 dòng có hậu tố `+07:00`. Tin sau 15:00 ICT (sau đóng cửa) có cùng
   `public_date` T nhưng giá chỉ phản ứng T+1 — event-study phải xét giờ, dùng `public_datetime` đã
   parse với TZ=Asia/Ho_Chi_Minh (§16), không dùng `public_date` nhìn thẳng làm "ngày giao dịch phản ứng".
3. **`first_ingested_at`** (STRING, ngày) NULL ở 708 dòng — toàn bộ là dòng nạp sau 2026-09-14; 59.603 dòng
   còn lại chỉ có giá trị 2026-09-02→09-13 (ngày vendor thu lần đầu, không phải ngày công bố). Ngữ nghĩa
   chính xác chưa xác minh với vendor.
4. **Có dòng trùng nội dung** (id khác nhau): 118 nhóm (ticker, public_date, title), 120 dòng thừa
   (0,2%) — ví dụ AAV 2019-04-09, AGG 2021-01-22. `news_id` không dedupe được. Khi đếm sự kiện phải
   `GROUP BY ticker, public_date, title`.
5. **Universe lẫn chứng chỉ quỹ/ETF + mã lịch sử.** 49 dòng ticker không khớp `^[A-Z0-9]{3,4}$`
   (ETF `FUE*`, tiêu đề "tạm ngừng giao dịch hoán đổi"); 443/1.730 mã KHÔNG có dòng nào trong `ticker` từ
   2025-01-01 (đã hủy niêm yết / mã cũ / ETF) ⇒ **không phải survivorship-free ở chiều ngược lại: có mã
   hủy niêm yết, nhưng độ phủ mã hủy chưa đo**. Join với universe phải qua `universe_pit`, không `ticker_prune` (§9b).
6. **Tên bảng vs cột**: luôn alias `AS n`, không `GROUP BY ticker` trần khi join `ticker` (bảng `ticker` có
   cùng tên cột → lỗi STRUCT, đã gặp khi kiểm tra này).

## Cách dùng an toàn
- Event-study ngày công bố: dùng `public_date`/`public_datetime` (parse ICT), loại trùng, và nếu cần PIT
  nghiêm ngặt chỉ chấp nhận tin có `DATE(ingested_at) <= public_date + k` (k chọn rõ, vd 3) — chấp nhận mất
  ~98,8% lịch sử vì backfill 09-13; HOẶC coi kết quả là *ceiling* (độ phủ nhìn lại), ghi rõ.
- Chỉ so sánh tần suất tin trong CÙNG chế độ phủ (2015–2019 | 2020–2021 | 2022+), không xuyên chế độ.
- Đã có một dùng trong research: Taylor `rating_8l_lag_20261020/analyze_lag.py` (A2: ngày BCTC từ tiêu đề, so
  với `Release_Date`) — kết quả thuộc về report đó, không lặp ở đây.
- Cổ tức/quyền: vẫn lấy từ `corporate_action` (CANONICAL), `stock_news` chỉ là tin báo trước.

## Chưa xác minh
- Cơ chế/cron ghi bảng và vendor nguồn (không có code trong repo).
- Nguyên nhân gãy chuỗi 2021-10→2022-02 và đỉnh 2020–2021.
- Cột `image_url`; ngữ nghĩa `first_ingested_at`; độ phủ so với nguồn gốc (HOSE/HNX disclosure).
- Có hay không hồi tố sửa/xoá `public_date` của dòng cũ (không có vintage để đo).
