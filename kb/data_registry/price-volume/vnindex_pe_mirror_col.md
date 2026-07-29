---
kind: bigquery-column
status: TRAP (pending fix)
source: cột mirror t.VNINDEX_PE trên hàng CỔ PHIẾU (trong tav2_bq.ticker VÀ ticker_prune)
group: price-volume
issue: NULL toàn bộ trước 2016-07-01 — bq_admin xác nhận là BUG (2026-07-29), sẽ backfill full 2006-03-30→
detected: 2026-07-29 (Taylor job Taylor_20260729_024754, verify sâu bởi Mike qua BQ Python SDK)
writer: bq_admin
---

# Cột mirror `t.VNINDEX_PE` (PE thị trường) trên các hàng CỔ PHIẾU (`tav2_bq.ticker` VÀ `ticker_prune`)

**Status: ⚠️ TRAP, ĐANG CHỜ FIX** — bq_admin xác nhận 2026-07-29 đây là BUG, cam kết backfill đầy đủ
từ 2006-03-30. Tính đến 2026-07-29, cột này **NULL 100% mọi hàng trước 2016-07-01** trong CẢ `ticker`
lẫn `ticker_prune` — verify bằng 3 cách độc lập (schema, sample thô quanh 2006-03, đếm non-null theo
từng năm 2000→2026, năm 2015 vẫn 0/171.683, năm 2016 mới có 104.050/196.110). Việc backfill CHƯA xảy
ra tại thời điểm ghi entry này — kiểm tra lại `MIN(time) WHERE VNINDEX_PE IS NOT NULL` trước khi tin
đã sửa.

## Là gì
Cột tiện ích gắn giá trị PE thị trường VNINDEX theo NGÀY lên mọi hàng cổ phiếu (mirror, giống cơ chế
`t.VNINDEX` — xem [[vnindex_mirror_col]]). Ý định thiết kế (theo mô tả cột, `CLAUDE.md`) là có dữ liệu
từ 2006-03-30, khớp với file local `data/VNINDEX.csv` (đã verify: VNINDEX_PE non-null 2006-03-30→
2026-05-26, nhưng file đó dừng cập nhật 2 tháng — không dùng cho giá trị hiện tại).

## Bẫy hiện tại (trước khi bq_admin backfill xong)
Bất kỳ query nào lấy percentile/lịch sử PE thị trường qua `WHERE VNINDEX_PE IS NOT NULL` trên
`ticker`/`ticker_prune` sẽ tưởng lịch sử chỉ bắt đầu 2016-07-01 — **KHÔNG phải giới hạn thật của thị
trường** (thị trường VN có dữ liệu định giá từ ~2007, xem `ticker_prune` note trong `CLAUDE.md`), mà
là bug đang chờ sửa. Workaround hiện tại (dùng trong `market_regime_probability_20260729.md`): tự
dựng PE thị trường cap-weighted từ cột `PE` per-ticker (`Σ Price×OShares / Σ EPS×OShares`, đã verify
per-ticker PE non-null có dữ liệu thật từ 2007, KHÔNG bị bug này) — corr 0,945 với PE chính thức trên
2016+, tin cậy tương đương làm proxy cho giai đoạn thiếu.

## Sau khi bq_admin backfill xong
- Re-verify `MIN(time) WHERE VNINDEX_PE IS NOT NULL` = 2006-03-30 (hoặc ngày backfill thật công bố).
- Đối chiếu PE tự dựng (workaround) vs PE chính thức mới backfill trên đoạn 2007-2016 — nếu lệch lớn
  bất thường so với corr 0,945 đã đo trên 2016+, báo lại (có thể workaround có giả định sai cho giai
  đoạn thị trường mỏng).
- Cập nhật status field ở trên thành `CANONICAL`, xoá cảnh báo TRAP.
