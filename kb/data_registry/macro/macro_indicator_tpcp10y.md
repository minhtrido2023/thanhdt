---
kind: table
status: UNVERIFIED
source: tav2_bq.macro_indicator (TradingEconomics scrape; series vn_bond_10y = lợi suất TPCP 10Y, vn_interbank_3m, us_bond_2y/10y; 41 series_key)
upstream_true: HNX/VBMA (lợi suất TPCP benchmark 10Y)
group: macro
writer: KHÔNG TÌM THẤY trong repo (grep macro_indicator/trading_economics/vn_bond_10y: 0 script ghi). Bảng tạo 2026-10-30 ~07:08 UTC; nạp 1 lần 10-30 (84.324 dòng) rồi top-up 41 dòng (1/series) ngày 11-01 15:00 UTC. Nghi writer ngoài repo (pipeline tav2) — cần Winston xác nhận.
cron: chưa xác định (crontab không có dòng nào gọi). Cadence nghi ngờ: hằng ngày, 1 dòng/series.
vintage: fetched_at 2026-10-30 07:25 (backfill) và 2026-11-01 15:00 UTC; dữ liệu quan sát cuối vn_bond_10y 2026-10-30, vn_interbank_3m 2026-10-28.
consumer: dcf_rate_display.py::tpcp_line (HIỂN THỊ dòng TPCP 10Y trong converge_report; không gate) · research dcf_rate_proxy_20261102
verified_by: Taylor, job Taylor_20261102_015334, 2026-11-02
---
# `tav2_bq.macro_indicator` — vn_bond_10y (TPCP 10Y)

**Status: UNVERIFIED** — chưa đối chiếu được nguồn thứ hai trong ngưỡng ≤0,2pp, writer/cron chưa xác định.

## Cột
series_key, country, name_en, observation_date, value, unit, source, source_url, te_slug, fetched_at, extra_json.
`vn_bond_10y`: 5.074 dòng, 2007-03-20 → 2026-10-30, đơn vị %.

## Đối chiếu nguồn thứ hai (đo 2026-11-02)
Nguồn B = bản tin VBMA tháng 6 và 7/2026 (vbma.org.vn, lợi suất 10Y cuối tháng: 6/2026 = 4,362%; 7/2026 = 4,403%; tháng 5 suy ra từ "+11bp" = 4,252%).
| Cuối tháng | BQ (TE) | VBMA | Lệch |
|---|---|---|---|
| 2026-05-29 | 4,458 | 4,252 (suy ra) | +0,21 |
| 2026-06-30 | 4,5226 | 4,362 | +0,16 |
| 2026-07-31 | 4,5368 | 4,403 | +0,13 |
Chiều đúng, mức lệch hệ thống +0,13…+0,21pp (TE cao hơn), 1/3 mốc vượt 0,2 và mốc tháng 5 là suy ra. Không tìm được VBMA/HNX cho 2022–2023 và 09–10/2026 (search chuẩn không ra). ⇒ giữ **UNVERIFIED**; Δ12T (cùng nguồn, cùng lệch hệ thống) đáng tin hơn mức tuyệt đối.

## Bẫy
- Dòng hiển thị luôn gắn nhãn UNVERIFIED; không dùng làm input gate/sizing.
- Backfill 10-30 và top-up 11-01 khác `fetched_at`; một ngày có thể bị ghi đè — dùng observation_date, không dùng fetched_at làm khoá thời gian.
- Fail-closed: quan sát cuối cách asof > 7 ngày ⇒ dòng in "không có dữ liệu", không điền số cũ.
