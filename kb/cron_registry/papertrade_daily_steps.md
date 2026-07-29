---
kind: reference
group: cron-detail
title: papertrade_daily.sh (15:30) — step nội bộ + phân loại nguồn dữ liệu A/B/C
belongs_to: ../cron_registry.md  # dòng bảng chính 15:30
---

# §papertrade_daily.sh (15:30) — step nội bộ + phân loại nguồn dữ liệu

> Chi tiết kỹ thuật của 1 cron cụ thể (23 slot step, 15 slot còn active) — tách khỏi bảng chính vì
> không cần đọc mỗi lần tra lịch tổng. Bảng chính (dòng 15:30) chỉ trỏ tới đây.

## Chuỗi thực thi (rút gọn)

`[1] pull_us_market` (Pillar B feed) → `[2] refresh_lagged_caches` (input LAG live) → `[3] snapshot_state_vintage`
→ `[4] macro_healthcheck` (ghi `macro_health.json`, input fail-safe `get_gated_state`) → `[6]`/`[6b] custom30_history`
(blend audit / **production** `custom30v_8l`) → `[7][8][11][12] pt_v11/pt_v12/pt_v4/pt_v22` (control-arm
`engine_room_oos` panel, review 2026-12-01 — **pt_v22 là PRODUCTION**, đọc bởi `trading_bot/strategies.py`)
→ `[14] papertrade_compare` (ghi `compare5.csv`, đọc bởi report 16:00) → `[17] orb_pt` (trial mở, event-end)
→ `[20] pt_capitulation_shadow` → `[21] fetch_bdi_daily` → `[22] edge_health_monitor --refresh`
(rebuild `data/lag_edge_health.csv` vô điều kiện mỗi lần chạy; dừng ở 2026-05-11 là ĐÚNG lịch sử mùa vụ
(zero sự kiện NP_R 05-05→07-07), KHÔNG phải bug — điều tra + đóng 2026-07-12, `Taylor_20260712_155038`)
→ `[26] phosphorus_dgc_weekly` (Fri only). Block RETIRED `[15][16][18][23][24][25]` giữ nguyên comment-out
(archive pattern, KHÔNG xoá — xem coding_guidelines §10).
`[19] crisis_alert_push` ĐÃ TÁCH sang `mike/bin/paper_late_feeds.sh` 20:05 (2026-07-29, xem dưới).

## Phân loại nguồn dữ liệu A/B/C — vì sao "dời hết sang 19:00" KHÔNG có tác dụng

Đo thật 2026-07-29 (job `Winston_20260729_103816`):
- **Upstream tav2 ingest** ghi xong `ticker` 17:23 · `ticker_prune` 17:17 · `ticker_financial` 17:21 ·
  `ticker_1m` 16:02 ICT → BQ LIVE có close phiên T từ **~17:2x**.
- **`BQ_LOCAL_CACHE=data/bq_cache`** (export trong `wc_env.sh`, `papertrade_daily.sh` source nó) chỉ được
  `sync_bq_cache_daily.sh` đổ lại lúc **23:45**. `simulate_holistic_nav.bq()` khi thấy biến này thì route
  100% query sang DuckDB/parquet, **không có fallback về BQ live**.
- ⇒ Mọi step loại (A) thấy **T-1 bất kể chạy 15:30 hay 19:00** — dời giờ chỉ làm báo cáo muộn hơn, không tươi hơn.

| Step | Nguồn đọc | Loại | Dời sang sau 17:30 có lợi? |
|---|---|---|---|
| `[1] pull_us_market` | yfinance (US market) | **C** | Không — phiên US ngày T chưa mở vào bất kỳ giờ ICT nào trong ngày; T-1 US là đúng thiết kế (Pillar B align VN T-1) |
| `[2] refresh_lagged_caches` | `simulate_holistic_nav.bq()` → cache | **A** | Không |
| `[3] snapshot_state_vintage` | `bq()` → cache | **A** | Không |
| `[4] macro_healthcheck` | `bq()` → cache + `us_market_history.csv` | **A** | Không |
| `[6] custom30_history` (blend audit) | `bq()` → cache | **A** | Không |
| `[6b] custom30v_history` → `custom30v_8l` | `bq()` → cache | **A** | Không — **và có deadline cứng: phải xong TRƯỚC 19:00** (`golive_recommend_v23` đọc bảng này) |
| `[7] pt_v11_tq34b` | `bq()` → cache (+ `macro_state_live` cũng qua cache) | **A** | Không |
| `[8] pt_v12_macro` | như trên | **A** | Không |
| `[11] pt_v4_dt5g` | như trên | **A** | Không |
| `[12] pt_v22_dt5g` (**PRODUCTION**) | như trên | **A** | Không |
| `[14] papertrade_compare` | `bq()` → cache + output sim | **A** | Không |
| `[17] orb_pt` | **vnstock LIVE** (bar 1m VN30F) | **C** | Không cần — VN đóng cửa 14:45 nên 15:30 ĐÃ là asof T |
| `[19] crisis_alert_push` | **BQ LIVE** (`dna_report._bq` subprocess: `ticker_prune` JOIN `dt5g_live`) | **B** | **CÓ** → đã tách sang `paper_late_feeds.sh` 20:05 |
| `[20] pt_capitulation_shadow` | **BQ LIVE** (subprocess `bq query`) | **B** | CÓ về dữ liệu, **NHƯNG chưa dời được** — xem ràng buộc dưới |
| `[21] fetch_bdi_daily` | web scrape handybulk.com | **C** | **CÓ** → chạy THÊM lần 2 lúc 20:05 (vẫn giữ lần 15:30) |
| `[22] edge_health_monitor --refresh` | **BQ LIVE** (subprocess) nhưng panel **theo THÁNG** | **B** | Không — granularity tháng, close phiên T không đổi kết quả; và `bq_freshness_check` 19:00 kiểm tra tuổi `lag_edge_health.csv` nên giữ trước 19:00 |
| `[26] phosphorus_dgc_weekly` (Fri) | SunSirs web + BQ LIVE dữ liệu **theo quý** | **B/C** | Không — không có độ nhạy same-day |

Ngoài chain, cùng họ paper:

| Cron | Nguồn | Loại | Ghi chú |
|---|---|---|---|
| `dc_book_waterfall_paper.py` 15:05 | đọc thẳng `data/bq_cache/*.parquet` bằng duckdb | **A** | Dời giờ vô ích; phải xong trước report 16:00 |
| `paper_main_probe_plan.py` 08:52 | `CACHE_PARQUET` (duckdb) | **A** | **ĐÚNG BẢN CHẤT** — plan cho phiên sáng CÙNG NGÀY buộc phải dùng tín hiệu T-1; **không được** dời |
| `paper_programs_daily_report.sh` 16:00 | chỉ đọc artifact do các cron trên sinh | — | Vintage = vintage của artifact nó đọc; mỗi mục tự in `asof` |

## Ràng buộc thứ tự (không được phá)

```
15:05 dc_book_waterfall ──┐
15:30 papertrade_daily ───┼──► 16:00 paper_programs_daily_report (đọc artifact)
   ├ [2]  → earnings_surprise_data.pkl ─┐
   ├ [6b] → tav2_bq.custom30v_8l ───────┼──► 19:00 bq_freshness_check → golive_recommend_v23
   ├ [20] → pt_capitulation_state.json ─┘        └─► note CAPIT_FIRED trong dispatch DollarBill
   └ [22] → data/lag_edge_health.csv ───────────► 19:00 check tuổi file
18:30 daily_refresh_v34b (base) ──► 19:00 publish_gated_state (dt5g_live có phiên T lúc ~19:00-19:03)
                                        └──► 19:10 eod · 19:20 pt_8l · 19:35 telegram · 20:05 paper_late_feeds
```

⇒ **Không thể dời cả chuỗi 15:30 sang 19:00**: `[2]`, `[6b]`, `[20]`, `[22]` đều là input của chuỗi 19:00
(đường plan tiền thật) → sẽ đụng độ / đảo thứ tự.

## Vì sao `[20] pt_capitulation_shadow` CHƯA dời (đề xuất, chờ duyệt)

`[20]` JOIN `ticker_prune × vnindex_5state_dt5g_live` nên asof = min(2 bảng). `dt5g_live` chỉ có phiên T sau
`publish_gated_state` **19:00-19:03** → chạy trước 19:00 thì asof luôn ≤ T-1 dù ingest đã xong 17:2x.
Nhưng `bq_freshness_check.sh` 19:00 đọc `pt_capitulation_state.json` để gắn note **CAPIT_FIRED** vào dispatch
DollarBill (đường plan tiền thật) → dời `[20]` ra sau 19:00 sẽ khiến note đó đọc file cũ hơn.
**Đề xuất (cần Mike/user duyệt, KHÔNG tự làm)**: đưa `[20]` vào CHÍNH chuỗi 19:00, chèn sau `pipeline-1
publish_gated_state` và trước `pipeline-2 golive_recommend_v23` → CAPIT_FIRED lúc dispatch phản ánh close
phiên T (sớm hơn hiện tại đúng 1 phiên) mà không phá thứ tự nào.

## Muốn nhóm (A) same-day thì phải làm gì — 2 lựa chọn, đều cần duyệt

1. **Giữ nguyên** (mặc định hiện tại): vintage T-1 của nhóm (A) là **sàn cấu trúc**, không phải bug — dời giờ
   trong ngày không sửa được. Báo cáo phải tự in `asof` thật cho từng mục (đã làm 2026-07-29).
2. **Đổi cách đọc dữ liệu** — hai hướng, KHÔNG tự ý làm:
   - (a) *Rẻ hơn, chỉ đổi lịch*: dời `sync_bq_cache_daily.sh` **23:45 → ~18:00** (sau ingest 17:2x) rồi dời chuỗi
     15:30 xuống sau đó. Không sửa dòng code đọc nào, nhưng **đổi vintage của artifact PRODUCTION**
     (`pt_v22` → `trading_bot/strategies.py`, `custom30v_8l` → `golive_recommend_v23`) và bỏ mất phần ingest
     muộn sau 18:00 → cần Taylor + user duyệt.
   - (b) *Đắt hơn*: sửa script bỏ qua `BQ_LOCAL_CACHE`, đọc BQ live. Cache tồn tại vì lý do hiệu năng ngay từ
     đầu (sim quét nhiều năm dữ liệu) → tăng thời gian chạy + tải/chi phí BQ đáng kể.

↩ [Về cron_registry (bảng chính)](../cron_registry.md) · [index nhóm cron-detail](index.md)
