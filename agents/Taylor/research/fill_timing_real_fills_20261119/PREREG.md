# PREREG — fill_timing_real_fills_20261119 (job Taylor_20261119_052911) — khoá TRƯỚC khi tính fill-vs-open
Read-only production. Không đổi config, không đặt lệnh.
## (1) Phân loại lệnh (join, chưa dùng giá)
- Nguồn lệnh: dnse_raw_2026-*.jsonl kind=orders, lọc accountNo ∈ {0002023347 SpaceX, 0001743768 ZaloPay} (§12), fillQuantity>0, transDate 2026-07-01→2026-11-16, dedupe (account,id).
- Join với journal exec_{SpaceX,ZaloPay}_{date}_journal.csv sự kiện PLACE theo child_oid==order id (journal label 'main' = paper, loại).
- Nhãn từ chính note PLACE (executor.py:2203-2208): HYB_IN_BLOCK ("hyb:blk"), HYB_OUT_OF_BLOCK ("ft:out×N hyb"), FT_BASE_IN ("ft:in-window" không hyb), FT_BASE_OUT ("ft:out×N" không hyb), GAP_OVERRIDE (gap_z). Không join được ⇒ NO_JOURNAL_MATCH (báo tỉ lệ).
- Tách thêm theo ngày: trước/sau 2026-08-26 (commit 9be375a44 bật HYBRID live) và theo giờ đặt (created, ICT).
- Cột lý do + file:dòng code từng nhánh. Cờ urgency=high / EXTREME / gap bypass chỉ nêu nếu journal có bằng chứng; không suy.
## (2) fill-vs-open
- Giá khớp = averagePrice (dnse_raw order). Open = tav2_bq.ticker.Open? KIỂM bigquery_dictionary.json: nếu Open là giá điều chỉnh thì dùng Open*(Price/Close) cùng ngày làm open chưa điều chỉnh (adj factor trong ngày = 1); ghi cách làm.
- bps = (fill/open−1)*1e4 cho BUY; (open/fill−1)*1e4 cho SELL (dương = tốt cho SELL, âm = tốt cho BUY nên BUY báo (fill/open−1), SELL báo (fill/open−1) luôn theo cùng dấu giá: ĐỊNH NGHĨA CUỐI: bps = (fill/open−1)*1e4 cả hai chiều; BUY âm tốt, SELL dương tốt, như README OOS).
- Gộp theo (account,date,sym,side) có trọng số qty trước (đơn vị = lệnh-mã-ngày), nhóm: BUY/SELL × {HYB_IN_BLOCK, HYB_OUT_OF_BLOCK, nhóm không HYBRID (FT_BASE/pre-08-26/khác)}.
- CI95: bootstrap khối theo tuần ISO, 5000 lần, seed 20261119; chỉ báo khi nhóm ≥30 đơn vị-mã-ngày VÀ ≥8 tuần; còn lại "không đủ N", chỉ mean mô tả.
- So ngưỡng rollback +22 bps (BUY): mean nhóm BUY HYBRID và cận trên CI.
- Cảnh báo ex-post: tách ngày giảm/tăng (median return open→close của mã trong dữ liệu phiên) chỉ mô tả.
- Không kết luận edge.
