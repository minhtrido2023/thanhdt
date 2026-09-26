---
kind: derived-file
status: DERIVED (VCB bid_tf/ask — khớp `data/vcb_fx_rate.csv` 3/3 tháng chồng lấn ≤20đ = 1 bước giá) · UNVERIFIED (trung tâm, tự do, NHNN — chưa có nguồn thứ 2)
source: data/fiinprox_usd_fx_monthly_20260926.csv (raw: data/fiinprox_fx_raw/usd_YYYY.txt, builder bin/fiinprox_consolidate.py)
group: macro
writer: cron bin/fiinprox_harvest_tick.sh (headless → FiinXMCP execute_api → client.economy.currency.list_exchange_rates Monthly) 2026-09-26; hợp nhất Mike 2026-09-26. ĐÃ DỪNG
upstream: FiinPro-X trial, HẾT HẠN 2026-09-28 — snapshot một lần. Nối tiếp: VCB qua `vcb_fx_feed.py` (ngày, từ 2026-07-03); trung tâm/NHNN: sbv.gov.vn (chưa có scraper); TỰ DO: KHÔNG có nguồn
created: 2026-09-26
---

# `fiinprox_usd_fx_monthly` — tỷ giá USD/VND cuối tháng, 2012-01→2026-09 (177 tháng)

Giá trị = bản ghi CUỐI CÙNG trong tháng của từng tổ chức (không phải bình quân tháng). VND/USD nguyên.
Cột: `central` (tỷ giá trung tâm NHNN, `ask_rate`) · `vcb_bid_tf` (VCB mua chuyển khoản) ·
`vcb_ask` (VCB bán) · `free_ask` (thị trường tự do, bán) · `sbv_ask` (NHNN bán, sở giao dịch).

Độ phủ: `central`/`vcb_*` đủ (trống 3 tháng VCB đầu 2012); `free_ask` trống **cả năm 2012**
(có từ 2013-01); `sbv_ask` trống 54 tháng rải rác (2012-2018 phần lớn, 2019-04, 2024-04).

## Đối chiếu (2026-09-26)
- vs `data/vcb_fx_rate.csv` (feed ngày, cuối tháng): 2026-07 ask 26.490 vs 26.470 · 2026-08 26.260
  vs 26.260 · 2026-08 bid_tf 25.880 vs 25.880 · 2026-09 26.170 vs 26.180 ⇒ lệch ≤20đ, do ngày
  cuối tháng khác nhau 1 phiên. Chỉ 3 tháng chồng lấn — đủ để tin cột VCB, KHÔNG đủ cho các cột khác.
- Lấp lỗ hổng #10: `macro_usdvnd.csv` dừng 2026-04-29 (consumer `textile_screen.py`,
  `save_macro_data.py`) — file này là nguồn backfill tháng 2012→2026 nếu consumer chấp nhận tần suất tháng.

## Bẫy
1. **Trước 2016-01-04 không có "tỷ giá trung tâm"** (cơ chế ra đời 01/2016) — `central` các năm
   2012-2015 là tỷ giá bình quân liên ngân hàng cũ mà provider gán cùng nhãn. Đừng nối 2 chế độ như một.
2. `free_ask − central` (premium tự do) là ứng viên chỉ báo stress (H6) — nhưng tự do KHÔNG có nguồn
   nối tiếp sau trial ⇒ chỉ dùng cho phân loại LỊCH SỬ, không làm cổng sống.
3. Giá trị cuối tháng nhạy với ngày cuối rơi vào cuối tuần/lễ; muốn bình quân tháng phải harvest lại
   (không còn quyền).

↩ [Về nhóm macro](index.md) · [Về index tổng](../index.md)
