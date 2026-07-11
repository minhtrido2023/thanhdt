# Data Registry — mọi nguồn dữ liệu hệ thống đang dùng

> Lập theo yêu cầu user 2026-07-11, sau sự cố SIGNAL_V11 đọc nhầm bảng `vnindex_5state`
> (base, KHÔNG phải DT5G) khiến sổ production `pt_v22_dt5g` vào lệnh theo trạng thái BULL
> GIẢ (xem `kb/INCIDENTS.md`). Đây là danh sách CHÍNH THỨC mọi nguồn dữ liệu (bảng BQ, file
> local, file trạng thái publish) đang được paper-trading/production/nghiên cứu dùng.

## Nguyên tắc bắt buộc

1. **Trước khi dùng 1 nguồn dữ liệu trong nghiên cứu/code MỚI — tra bảng này trước.** Nếu
   nguồn chưa có trong danh sách, KHÔNG coi mặc định là an toàn — thêm vào danh sách này
   (hoặc hỏi người review) trước khi wire vào bất kỳ paper-trading/production nào.
2. **Cột "Status" là điều quan trọng nhất, đọc trước khi dùng:**
   - `CANONICAL` — nguồn đúng, dùng trực tiếp được.
   - `TRAP` — tên/vị trí DỄ NHẦM với 1 nguồn canonical khác, đã có tiền lệ bug thật. Đọc kỹ
     cột "Bẫy" trước khi động vào.
   - `DERIVED` — tính từ 1 nguồn canonical khác, an toàn nếu nguồn gốc còn đúng.
   - `DEPRECATED/DEAD` — không còn được cập nhật hoặc không nên dùng nữa, chỉ giữ để tham
     chiếu lịch sử.
3. **Người review + tần suất:** Winston (data-ops) giữ danh sách này tươi — cập nhật ngay
   khi phát hiện nguồn dữ liệu mới trong lúc làm việc khác (không cần đợi review định kỳ).
   Review định kỳ TOÀN BỘ danh sách (freshness thật + rà thêm nguồn mới chưa ghi) gắn vào
   **review KB thứ Sáu hàng tuần** (`kb_nightly.sh`, đã có sẵn cơ chế dispatch Mike headless)
   — Mike đọc danh sách, dispatch Winston verify từng nguồn còn "chưa review >30 ngày".
4. **Khi dispatch Taylor cho R&D mới:** prompt phải nhắc "tra `mike/kb/data_registry.md`
   trước khi chọn nguồn dữ liệu, đặc biệt bảng market-state/regime" — giống quy tắc đã có
   cho DollarBill (DNSE-vs-BQ, `coding_guidelines.md` §6).

---

## Market state / regime (nhóm rủi ro cao nhất — đã có sự cố thật)

| Nguồn | Status | Là gì | Ai ghi / cadence | Bẫy |
|---|---|---|---|---|
| `tav2_bq.vnindex_5state_dt5g_live` | **CANONICAL** | Trạng thái thị trường PRODUCTION (DT-gate + macro gate, 49 transitions) | `macro_state_live.py` → `daily_refresh_v34b_linux.sh` cron 18:30 ICT (dời từ 23:15, 2026-07-10) | Không có, đây là nguồn ĐÚNG duy nhất cho production |
| `tav2_bq.vnindex_5state` | **TRAP** | v3.4b BASE thô (không DT-gate, không macro-cap, ~153 transitions) — **KHÔNG PHẢI DT5G** | `daily_refresh_v34b_linux.sh` (cùng cron, bước load bare) | **Đã gây sự cố thật 2 lần**: (1) 2026-07 EW-leg reorg bug tạo BULL giả; (2) 2026-07-11 phát hiện `SIGNAL_V11.sql` + 4 script production (`golive_recommend_v23.py`, `pt_v4_dt5g.py`, `pt_v22_dt5g.py`, `pt_v23_audit_2014.py`) đọc nhầm bảng này — sổ `pt_v22` vào 6 mã theo BULL giả. Byte-identical với `vnindex_5state_tam_quan_v34b_clean`. |
| `tav2_bq.vnindex_5state_tam_quan_v34b_clean` | DERIVED | Bản sync của v3.4b base (== bare `vnindex_5state`) | Cùng cron 18:30, bước "SYNCS _v34b_clean" | Là INPUT cho DT-gate tính `dt5g_live` — đọc để audit base, không phải để lấy state production |
| `deploy_golive_dt5g_v4/golive_state_today.json` | DERIVED (từ `dt5g_live`) | File publish nhanh cho DollarBill đọc | `publish_gated_state.py`, chạy trong `bq_freshness_check.sh` cron 19:00 ICT | Field `as_of` phải khớp NGÀY HÔM NAY — nếu lệch 1 ngày, xem sự cố cron-order 2026-07-10 (đã sửa) |
| `golive_v23_recommendations_<date>.csv` | DERIVED | Khuyến nghị BAL/LAG hàng ngày | `golive_recommend_v23.py`, đọc `dt5g_live` (đã fix 2026-07-11, trước đó đọc nhầm base) | Kiểm tra `state_source` field = `DT5G_macro`, không phải suy đoán |
| `data/pt_v22_dt5g_open_positions.csv` | DERIVED | Sổ vị thế production (trading_bot/strategies.py đọc để build plan sống SpaceX/ZaloPay) | `pt_v22_dt5g.py`, cron papertrade_daily.sh 15:30 ICT | Money-path THẬT — bug ở đây ảnh hưởng lệnh thật. Đã fix 2026-07-11 (commit 0537514/9149c0f), có selfcheck riêng (`money_path_freshness_selfcheck.py` section F, 29/29 PASS) |
| `data/pt_v12_live_logs.csv` | **DEAD** | Alt-state research variant | KHÔNG chạy — output đóng băng từ 2026-05-27 (6+ tuần) | Không phải production consumer (xác nhận: không trong crontab, không trong `papertrade_daily.sh`, `papertrade_compare.py` ghi rõ "Removed"). Vẫn còn code SIGNAL_V11 thô — nếu hồi sinh PHẢI vá cùng pattern trước khi chạy lại |
| `data/pt_v12_macro*.csv` | Research (by-design) | Engine-room A/B state-source so sánh | `papertrade_daily.sh` step 8, chạy hàng ngày | KHÔNG phải production, là paper cohort review có chủ đích (mốc review 2026-12-01) — không cần vá theo pattern trên |

## Giá / khối lượng cổ phiếu

| Nguồn | Status | Là gì | Ai ghi / cadence | Bẫy |
|---|---|---|---|---|
| DNSE API live (`dnse_api.py` secdef/latest_trade/positions/balances) | **CANONICAL cho dữ liệu TRONG NGÀY** | Giá/khối lượng/vị thế thật, real-time | Broker, không có độ trễ | Đây là nguồn BẮT BUỘC cho mọi tính toán cùng ngày (xem `coding_guidelines.md` §6 bright-line rule, user directive 2026-07-09) |
| `tav2_bq.ticker` / `ticker_1m` / `ticker_prune` | CANONICAL cho **lịch sử** | OHLCV + chỉ báo, backtest/nghiên cứu | Ingest ETL (đã xác nhận 2026-07-10: `ticker`/`ticker_prune` của HÔM NAY đã đầy đủ trước 18:45 ICT, không cần đợi tới đêm) | **TRAP nếu dùng cho dữ liệu TRONG NGÀY**: BQ cache local (`data/bq_cache`) chỉ sync 23:45 ICT — script chạy trước giờ đó đọc cache sẽ luôn trễ 1 ngày (sự cố thật 2026-07-09, DollarBill BID/MBB lệch +5.7%). BQ TABLE gốc (không qua cache) có thể fresh sớm hơn nhiều — đừng lẫn 2 khái niệm "BQ" và "BQ cache local" |
| `tav2_bq.shares_outstanding_live` | CANONICAL (override) | Số cổ phiếu lưu hành đã điều chỉnh corp-action, override `ticker_financial.OShares` (quý, có thể trễ ~3 tháng) | `update_shares_live.py --ticker`/`--ack-cash`, do Winston chạy tay sau khi phân loại | Chỉ có hiệu lực nếu consumer JOIN đúng cú pháp (xem template cuối `update_shares_live.py`) — không JOIN thì vẫn dùng OShares quý cũ |
| `data/corp_action_pending.json` + `data/corp_action_backlog.json` | Vận hành | Theo dõi corp-action đã alert/chưa resolve | `update_shares_live.py --scan`, cron 18:40 ICT hàng ngày | Đã từng có backlog 21 ngày không ai xử lý trước khi thêm heartbeat + escalate (2026-07-10) |

## Fundamentals / tài chính

| Nguồn | Status | Là gì | Ai ghi / cadence | Bẫy |
|---|---|---|---|---|
| `tav2_bq.ticker_financial` | CANONICAL | Báo cáo tài chính quý | Ingest theo lịch công bố BCTC (~60-85 ngày lệch cho phép, `MAX_FIN_LAG=90` trong `bq_freshness_check.sh`) | OShares ở đây bị trễ quanh ex-date corp-action — xem `shares_outstanding_live` ở trên |
| `tav2_bq.risk_rating` | CANONICAL (dùng `GROUP BY`/`DISTINCT`) | Beta/Dev/Risk_Rating theo quý | — | Có DÒNG TRÙNG LẶP đã biết (xem CLAUDE.md "Known data quality notes") |

## Vĩ mô

| Nguồn | Status | Là gì | Ai ghi / cadence | Bẫy |
|---|---|---|---|---|
| `us_market_history.csv` (VIX/SPX) | CANONICAL | Input Pillar B (macro gate DT5G) | `pull_us_market.py`, chạy trong `daily_refresh_v34b_linux.sh` bước [2] | Lag theo thiết kế (aligned T-1), không phải bug |
| SBV refi-rate (`sbv_macro_overlay`) | CANONICAL | Input Pillar A (macro gate DT5G) | `check_sbv_weekly.sh`, cron thứ Sáu 15:00 ICT | `fetch_status: fetch_failed` từng xảy ra (2026-07-10), tự fallback "assumed unchanged" — kiểm tra field này khi audit |

## Cần bổ sung (chưa rà hết — giao Taylor sweep tiếp)

Danh sách trên chỉ mới phủ các nguồn ĐÃ TỪNG gây sự cố thật hoặc được nhắc trong CLAUDE.md.
Codebase còn nhiều bảng BQ/file khác (8L rating, ETF liquidity, custom30V basket, ORB
intraday, v.v.) chưa được rà và ghi vào đây — xem việc dispatch Taylor cùng ngày lập file
này để mở rộng danh sách.

## Lịch sử
- 2026-07-11: tạo lần đầu, seed từ sự cố SIGNAL_V11 base-leak + các gotcha đã biết trong
  CLAUDE.md/coding_guidelines.md. Dispatch Taylor sweep mở rộng đang chạy — xem cập nhật kế tiếp.
