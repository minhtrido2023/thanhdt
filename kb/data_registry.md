# Data Registry — mọi nguồn dữ liệu hệ thống đang dùng

> Lập theo yêu cầu user 2026-07-11, sau sự cố SIGNAL_V11 đọc nhầm bảng `vnindex_5state`
> (base, KHÔNG phải DT5G) khiến sổ production `pt_v22_dt5g` vào lệnh theo trạng thái BULL
> GIẢ (xem `kb/INCIDENTS.md`). Đây là danh sách CHÍNH THỨC mọi nguồn dữ liệu (bảng BQ, file
> local, file trạng thái publish) đang được paper-trading/production/nghiên cứu dùng.

> **Last full audit: 2026-07-11** (seed + Taylor codebase sweep + `bin/data_registry_audit.sh` xây
> mới, chạy sạch FAIL=0/WARN=0). Cập nhật dòng này mỗi lần review định kỳ (Friday) hoặc audit thủ
> công chạy xong — xem mục 3 dưới.

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
   Review định kỳ TOÀN BỘ danh sách gắn vào **review KB thứ Sáu hàng tuần** (`kb_nightly.sh`
   Phase 5, dispatch Mike headless) — cơ chế nay có 2 phần cụ thể, không chỉ là kế hoạch:
   (a) chạy `bin/data_registry_audit.sh --bus` (script, không phải LLM tự đoán) — kiểm tra
   CƠ HỌC 2 việc: (i) các file từng bị bug base-leak/mislabel (`signal_v11_sql.py`,
   `pt_v4/pt_v22/pt_v23_audit`, `golive_recommend_v23.py`) chưa regress lại; (ii) freshness
   thật của 3 nguồn rủi ro cao nhất (`vnindex_5state_dt5g_live`, `custom30v_8l`,
   `fa_ratings_8l`) qua `bq show` trực tiếp, không suy đoán từ cache/mtime file phụ; (b) Mike
   đọc kết quả FAIL/WARN, xử lý theo mục 5 dưới nếu là vấn đề obsolete/regression, cập nhật
   dòng "Last full audit" ở đầu file. Ai muốn chạy tay ngoài lịch: `bin/data_registry_audit.sh`
   (thêm `--bus` để ghi bus event, mặc định chỉ in ra màn hình).
4. **Khi dispatch Taylor cho R&D mới:** prompt phải nhắc "tra `mike/kb/data_registry.md`
   trước khi chọn nguồn dữ liệu, đặc biệt bảng market-state/regime" — giống quy tắc đã có
   cho DollarBill (DNSE-vs-BQ, `coding_guidelines.md` §6).
5. **Đánh dấu obsolete khi quyết định migrate khỏi 1 nguồn** (user chỉ đạo 2026-07-11, sau
   phát hiện fa_ratings có thể bị thay bởi fa_ratings_8l) — BẮT BUỘC làm CẢ 3 bước sau CÙNG
   lúc với commit cutover, không để thành TODO làm sau (nếu tách rời, đúng lúc đó là lúc dễ
   dùng nhầm bản cũ nhất — bài học SIGNAL_V11 base-leak):
   - (a) Đổi `Status` của nguồn cũ → `DEPRECATED` kèm dòng **⚠️ SUPERSEDED BY `<nguồn mới>`
     ON `<ngày cutover>`** ngay trong ô "Bẫy", không chỉ đổi mỗi chữ Status.
   - (b) Chạy sweep xác nhận (grep toàn codebase + `bin/data_registry_audit.sh`) KHÔNG còn
     script production nào đọc nguồn cũ — nếu còn, liệt kê rõ tên file + lý do (vd "chỉ
     script research lịch sử, không sửa"). Không được nói "chắc không còn ai đọc" mà không
     grep thật.
   - (c) Ghi 1 dòng vào "Lịch sử" cuối file: ngày cutover, nguồn cũ→mới, ai duyệt, có
     PBO/DSR/quant-skeptic verify hay không (nếu là migration signal như fa_ratings→8l).
   Ràng buộc riêng cho case `fa_ratings` cụ thể: quyết định migrate PHẢI qua backtest song
   song + quant-skeptic + user sign-off trước (xem row `fa_ratings`/`fa_ratings_8l` — đây là
   ĐỔI SIGNAL, 66% tier khác nhau, không phải data refresh đơn thuần), KHÔNG được đánh dấu
   obsolete trước khi có kết quả đó.

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
| `data/vnindex_5state_tam_quan_v3_4b_full_history.csv` | CANONICAL (local base) | Bản CSV local của v3.4b base — input cho `build_dt_4gate.py` + ~30 script research | `daily_refresh_v34b_linux.sh` step [7] + cp root→`data/` 18:30 ICT (mirror fix 2026-07-10, audit Winston_20260710_173031) | Trước 07-10 bản `data/` đóng băng 06-30 trong khi bản root tươi — nếu thấy 2 bản lệch nhau, bản root là bản build, `data/` phải được cp theo |
| `data/vnindex_5state_dt_4gate.csv` | CANONICAL (DT4 local) | Chuỗi DT4 (base + DT 4-gate, KHÔNG macro) — research/ablation | `build_dt_4gate.py`, step [8] daily 18:30 (non-fatal, advisory-only) | **Cặp name-alike với bảng BQ `vnindex_5state_dt_4gate`** — bản BQ ĐÓNG BĂNG từ 2026-06-02 (verify `bq show` 2026-07-11), chỉ bản CSV local này còn sống. `sync_bq_cache.py` vẫn mirror bản BQ frozen vào `bq_cache/` → đọc DT4 qua cache/BQ = đọc dữ liệu chết |
| `tav2_bq.vnindex_5state_dt_4gate` | **DEAD (frozen 2026-06-02)** | Snapshot DT4 một lần lúc go-live DT5G | Không ai ghi nữa (verify lastModified 06-02, 6291 rows) | Xem dòng trên — muốn DT4 hiện tại: đọc cột `state_dt4` trong `dt5g_live` hoặc CSV local. ~20 script research cũ vẫn reference bảng này |
| `data/vnindex_5state.csv` | **TRAP (local, frozen)** | Bản CSV local cùng tên bảng trap BQ, đóng băng 2026-05-21 | Không ai ghi (mtime 05-21) | Twin local của trap `tav2_bq.vnindex_5state`: vừa là BASE (không phải DT5G) vừa STALE. ~29 script research cũ đọc — kết quả sai kép nếu tưởng là state production hiện tại |
| `data/vnindex_5state_dt_10_25_25.csv` | DEPRECATED | Output thời tuning DT-gate (tên tham số cũ của DT4) | Không ai ghi (mtime 2026-05-27) | Bị thay bởi `data/vnindex_5state_dt_4gate.csv`; ~16 script research-era còn reference |
| `tav2_bq.vnindex_5state_staging` / `_archive_*` / `_v2g_*` / `_tam_quan_v31/v33b_clean` / `_baseline_*` | ARCHIVE | Họ bảng archive/staging của lineage 5-state (ew_v1→dual_v3→v3.1→v3.4b→DT5G) | Đóng băng tại thời điểm archive tương ứng | Chỉ để tra lịch sử/forensic (vd `_archive_predeploy_20260711_*` từ vụ EW-leg). KHÔNG dùng làm state cho backtest mới — xem `vnindex_5state_registry.md` cho lineage đầy đủ |
| `tav2_bq.vn30f_daily` | DEAD (frozen 2026-06-08) | Snapshot daily VN30F cho 1 nghiên cứu euphoria-short | Không ai ghi (verify lastModified 06-08) | KHÔNG phải nguồn của ORB paper sleeve — `orb_pt.py` fetch 1-phút VN30F1M trực tiếp từ Vnstock/VCI API mỗi lần chạy |

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
| **PE / PB / PCF / PS** (cột trong `ticker` + `ticker_financial`) | CANONICAL — công thức đã verify | Định giá "tự tính từ tài chính thô" (bq_admin đổi từ nguồn bên-thứ-3 sang self-computed, ~2026-07). **Công thức xác nhận bằng tính tay** (job Winston_20260717_063633): **PE = Price / EPS_ttm** (EPS_ttm = Σ(NP_P0..P3)/OShares, 4 quý trailing) · **PB = Price / BVPS** · **PCF = Price / CF_ttm** · PS = Price/Rev_ttm. Nhất quán giữa `ticker` daily và `ticker_financial` quarterly; ngân hàng dùng cùng công thức NP-based. VNM/MBB khớp tới 4 chữ số. | Ingest ETL, cùng cadence `ticker_financial` | **(1) KHÔNG hồi tố** — verify toàn universe (~1260 mã × 2 ngày lịch sử 2023-06-01/2024-01-15) so snapshot pre-change `bq_cache/ticker/*.parquet` (June-25) vs BQ live: PE/PB/PCF/BVPS + PE_MA5Y/PB_SD5Y **giống hệt >99.7%** (0 PB đổi, ≤2 PE, ≤3 PCF>1% toàn mã illiquid); `ticker_financial` PE/PB/PS/PCF 100% identical July-8 vs July-16. → **mọi backtest đã pin + rating_8l an toàn, lịch sử KHÔNG bị viết lại**. **(2) Negative PE/PCF là bình thường & PRE-EXISTING** — mã lỗ → PE âm (52/797 mã), CF hoạt động âm → PCF âm (236/797); KHÔNG NULL-hóa (rating_8l đã tự guard: `cfo_yield` chỉ 1/PCF khi PCF>0). **(3) `bigquery_dictionary.json` STALE**: ghi range "0..Inf" cho PE/PB/PCF nhưng thực tế có âm; và KHÔNG ghi provenance self-computed — cần cập nhật (non-blocking). |
| **ROE / ROIC / FSCORE / quality-gate cột** (`ROE5Y, ROE_Min3Y/5Y, ROIC3Y/5Y, ROIC_Min3Y/5Y, ROIC_Trailing, FSCORE, Debt_Eq_P0, NP_P0..P3, CF_OA_P0..P3, CF_OA_3Y, OShares` trong `ticker`+`ticker_financial`) | CANONICAL — hồi tố đã verify AN TOÀN | Chỉ số chất lượng/quality-gate của 8L model, input `rating_8l.py`. bq_admin đang chủ động đổi phương pháp tính nhiều chỉ số FA (~2026-07, đã báo). | Ingest ETL, cùng cadence `ticker_financial` | **(1) KHÔNG HỒI TỐ — golden-floor ỔN ĐỊNH** (job Winston_20260717_070859): so pre-change cache June-25 (`bq_cache/ticker/*`) vs BQ live, toàn universe ~1160-1250 mã × 2 ngày (2020-01-15, 2023-06-01): **100% IDENTICAL 0-diff** cho ROE5Y/ROE_Min3Y/5Y, ROIC3Y/5Y/Min3Y/5Y, ROIC_Trailing, FSCORE, Debt_Eq_P0, NP_P0..P3, CF_OA_P0..P3, OShares, EVEB. **Golden-floor pass-set (`ROE_Min3Y≥0 ∧ CF_OA_3Y>0`): 0 FLIP** (588/588 @2020, 530/530 @2023). `ticker_financial` Jul-8 vs Jul-16: **0 change** mọi cột trên → R3/backtest pin + rating_8l value/quality **AN TOÀN**, lịch sử KHÔNG viết lại. **(2) `CF_OA_3Y` = tổng CF_OA thô đơn vị VND** (KHÔNG phải sum ratio CF_OA_P0..P2 như dictionary gợi ý) — nhưng **cùng dấu** sum(P0..P2) nên test golden-floor `>0` nhất quán; rating_8l đọc thẳng cột. **(3) Dividend_Min3Y ĐÃ ĐỔI method** (June-25→Jul-8: continuous/nội suy ~702.0/415.0 → round event-based VND/sh ~800/1500/0, ~54/1250 mã) — NHƯNG là **value-LENS `div_yield`, KHÔNG phải golden-floor gate** (rating_8l.py:674-676 xác nhận rõ), bản LIVE = đúng "event-based" model đã thiết kế/backtest, đổi TRƯỚC pin R3 07-11 + refresh fa_ratings_8l 07-12 → không tạo bất nhất ẩn. **(4) PB_MA5Y/PB_SD5Y** lệch nhỏ (~0.3-3%, ~57 mã, rolling 5Y stat feed pb_z) — non-material, không phải gate. **(5) Outlier ROE5Y/ROIC5Y cực đoan (±25..50) + Debt_Eq âm** = PRE-EXISTING (0 hồi tố), mẫu số equity≈0, rating_8l dùng percentile-zone + DẤU ROE_Min3Y nên robust. Hand-calc ROE_Trailing≈NP_ttm/equity khớp VNM/MBB/VCB(bank). |
| `tav2_bq.risk_rating` | CANONICAL (dùng `GROUP BY`/`DISTINCT`) | Beta/Dev/Risk_Rating theo quý | — | Có DÒNG TRÙNG LẶP đã biết (xem CLAUDE.md "Known data quality notes") |

## Vĩ mô

| Nguồn | Status | Là gì | Ai ghi / cadence | Bẫy |
|---|---|---|---|---|
| `us_market_history.csv` (VIX/SPX) | CANONICAL | Input Pillar B (macro gate DT5G) | `pull_us_market.py`, chạy trong `daily_refresh_v34b_linux.sh` bước [2] | Lag theo thiết kế (aligned T-1), không phải bug |
| SBV refi-rate (`sbv_macro_overlay`) | CANONICAL | Input Pillar A (macro gate DT5G) | `check_sbv_weekly.sh`, cron thứ Sáu 15:00 ICT | `fetch_status: fetch_failed` từng xảy ra (2026-07-10), tự fallback "assumed unchanged" — kiểm tra field này khi audit |
| `data/macro_health.json` | CANONICAL (gate) | Health-check các feed vĩ mô — `get_gated_state()` chỉ trả DT5G_macro khi file này tươi (<1440') và `recommended_state_source=="DT5G_macro"`, nếu không fail-CLOSED về DT4-only | `macro_healthcheck.py`, `papertrade_daily.sh` step [4], 15:30 ICT | File này stale = TOÀN BỘ consumer production tự rơi về DT4-only (đúng thiết kế fail-safe, nhưng dễ nhầm là bug khi thấy state khác nhau giữa 2 máy) |
| `data/breadth_data.csv` | DEAD (research, frozen 2026-05-26) | Snapshot breadth cho nghiên cứu cũ | Không ai ghi | Breadth-decoupling guard PRODUCTION **không** đọc file này — `macro_state_live.py` query thẳng `ticker_prune` (causal T-1). Đừng "fix freshness" file này cho production |
| `deposit_rate_vn.py` (`DEPOSIT_EVENTS` + `data/deposit_rate_vn_events.csv` append-only) | **CANONICAL-PROXY** | Big-4 (VCB/BIDV/CTG/Agribank) lãi suất tiết kiệm 12M, step-series 26 mốc frozen 2011→2026-06 (hardcode) + CSV extension append-only cho mốc tương lai, forward-fill | 26 mốc frozen calibrate **1 lần** (2026-06-19) từ hình dạng lending-rate Trading Economics 1999-2023 + vài mốc web Big-4 (KHÔNG sửa lại — caveat b). **ĐÃ có refresh routine Layer A (cài 2026-07-17, `Winston_20260717_072420`)**: cron `refresh_deposit_rate_vn.sh` 08:10 ICT ngày 3 hàng tháng chỉ NHẮC Discord + best-effort fetch (KHÔNG tự ghi); con người xác nhận rồi chạy `append_deposit_rate.py --rate --effective --source` append 1 dòng CSV (chỉ effective_date > 2026-06-01 mới có hiệu lực = point-in-time thật). Freshness WARN >45 ngày ở `ops_health_check.sh` §8 | 3 caveat bắt buộc đọc trước khi dùng: **(a)** chỉ phủ Big-4, chưa có chuỗi top10 ngoài nhóm này; **(b)** toàn bộ 26 mốc được neo hồi tố CÙNG 1 lần ngày 2026-06-19 — KHÔNG phải point-in-time thật cho quá khứ, mọi backtest chạy trên lịch sử (kể cả dự án Pillar A′ đang pre-registered, `Taylor_20260713_124803`) mang bias hindsight biết trước, chỉ mốc THÊM MỚI từ nay trở đi mới có thể là point-in-time thật; **(c)** đang là input **LIVE production** qua `current_deposit_rate()`: (i) `rating_8l.py` gentle NEUTRAL-only deposit tilt ±0.03 trên `value_score_v3` (validated 2026-06-19, chạy mỗi ngày trong `pt_8l_daily.sh` 17:45 ICT — KHÔNG dormant, ảnh hưởng rating sống mỗi ngày), (ii) deposit-gate RECOVERY_PARK floor 7.5% (dormant từ 2013). Routine cập nhật tháng (Layer A): `mike/agents/Winston/proposal_deposit_rate_monthly_refresh_20260713.md` (job `Winston_20260713_131255`) — **ĐÃ duyệt + cài đặt 2026-07-17** (`Winston_20260717_072420`): CSV append-only + `append_deposit_rate.py` + cron nhắc ngày 3 + WARN freshness; **(iii) `dcf_valuation.py` + `dcf_backtest.py`** (DCF 2-stage FCFE — dùng `current_deposit_rate()` làm risk-free rate baseline, job Taylor_20260714_051643, research tool, NOT wired production) |
| `cpi_vn.py` (`NSO_CPI_YOY_REAL` + `CPI_ANCHORS`) | CANONICAL-PROXY (2 tầng) | CPI YoY Việt Nam, monthly — **Tier 1 THẬT** (NSO chart-embed slug `cpi`, 2025-06→2026-06, cửa sổ rolling 13 tháng) đè lên **Tier 2 PROXY** nội suy tuyến tính (2011→2025-05) | Fetch tay **1 lần** (job `Taylor_20260706_105930`, 2026-07-06, parse trực tiếp JSON Highcharts embed của NSO) — **CHƯA có cron/refresh tự động**, không phải chuỗi tự tươi | **KHÔNG PHẢI `Inflation_7` trong `tav2_bq.ticker`** — đó là HẰNG SỐ 7%/năm chiết khấu trading value, không liên quan CPI thật (xem CLAUDE.md). 3 gotcha: (a) cửa sổ NSO rolling CHỈ 13 tháng — không refetch định kỳ, Tier 1 tự "trôi ra" theo thời gian mà KHÔNG báo lỗi (đã verify thực nghiệm 2026-07-13: gọi `cpi_monthly_df(end=...)` cho tháng sau 2026-06 vẫn trả SỐ — không NaN — do nội suy/ngoại suy Tier-2 âm thầm, chỉ phân biệt được qua cột `is_real_nso=False`, dễ tưởng nhầm vẫn là dữ liệu thật); (b) hôm nay 2026-07-13 đã qua tháng NSO gần nhất công bố (06/2026) — cần refetch để lấy in tháng 07 khi NSO đăng; (c) consumer hiện tại: `macro_confidence_regime.py` (`merge_cpi`); **`dcf_valuation.py` + `dcf_backtest.py`** (DCF 2-stage FCFE — CPI làm inflation input cho terminal growth rate, job Taylor_20260714_051643, research tool, NOT wired production) — KHÔNG phải input Pillar A/A′/B của DT5G macro gate (Taylor cần chuỗi này CHO Pillar A′ "lãi suất huy động thực" — đã báo tồn tại, đỡ phải tự tìm/tự dựng lại). Routine tháng có thể gộp chung đề xuất với `deposit_rate_vn.py` (xem file proposal trên) |
| `gdp_growth_vn.py` (`GDP_ANNUAL`) | **CANONICAL** (single-tier REAL, không proxy) | Tăng trưởng GDP THỰC Việt Nam, annual — World Bank Open Data API `NY.GDP.MKTP.KD.ZG` ("GDP growth annual %", growth của GDP giá cố định = REAL), chuỗi đầy đủ 26 năm 2000-2025 (long-run 15y avg = 6.22%) | Fetch **1 lần** 2026-07-17 (job `Taylor_20260717_063638`), WB `lastupdated`=2026-07-13; refresh idempotent bằng `refresh_gdp_growth_vn.py` (re-fetch WB API, ghi đè `GDP_ANNUAL` atomic, chỉ khi khác) — cadence **hàng năm, low-urgency**, CHƯA cài cron | Cùng nhà cung cấp với feed WB CMO commodity đã có (`auto_update_commodity_wb.*`). Dùng làm thành phần real-growth của DCF terminal growth (`dcf_earning_power.py`, job Taylor_20260717_063638 — **research, NOT wired production**; kết luận: GDP terminal g là level/display fix, KHÔNG phải alpha). 2 lưu ý: (a) point-in-time `longrun_real_gdp(asof)` chỉ dùng năm ≤ asof.year−1 (năm đã công bố trọn); (b) PHẢI dùng bình quân dài hạn 15-20y (đã fade sẵn hiệu ứng hội tụ + COVID trough), KHÔNG dùng năm gần nhất làm terminal g vĩnh viễn (Damodaran convergence — dùng thẳng 7-8% hiện tại phóng đại grossly, hit Gordon guard 23% releases) |

## 8L Rating / Composite v3 (quality gate production)

| Nguồn | Status | Là gì | Ai ghi / cadence | Bẫy |
|---|---|---|---|---|
| `tav2_bq.fa_ratings` | **CANONICAL, ĐANG REFRESH ĐỊNH KỲ** (hết static từ 2026-07-12) | Panel tier A–E legacy (thang cũ, per-quarter percentile, 7 trục Quality/Stability/Cash/Shareholder/Growth/Health/Valuation, weights 18/18/18/15/13/8/10) — vẫn là input PRODUCTION: `SIGNAL_V11.sql` (`fa_tier` của book BAL), `pt_v22_dt5g.py`, `pt_v23_audit_2014.py` + ~50 script research | **Builder = `fundamental_rating.py`** (repo root, KHÔNG mất — sửa lại 2026-07-11, ghi nhầm trước đó vì tên không theo pattern `build_fa_ratings_*`). Refresh = **`refresh_fa_ratings.py` (append-only: frozen quarters không đụng, 2 quý mở re-rank, quý mới append khi cohort ≥30) qua wrapper `mike/bin/refresh_fa_ratings.sh`**, cron **weekly thứ Bảy 09:15 ICT ĐÃ CÀI + identity fix `a9716f6` (source `wc_env.sh`) + test ghi THẬT 2026-07-12 OK: lastModified 07-12, 12.406 rows, invariant 48/48 quý đóng băng giữ nguyên** (quant-skeptic CONFIRMED — hết câu hỏi treo, lần scheduled đầu 07-18 chỉ là chạy bình thường). Mùa BCTC Q2: thêm cron TẠM T3 20:45 ICT đến hết 2026-08-04 (job Winston_20260713_103213, xem `cron_registry.md`) | 2 bẫy: (1) **name-alike với `fa_ratings_8l`** nhưng KHÁC thang đo (A–E vs rating 1–5/tier) và khác spec — đổi lẫn nhau làm lệch mọi as-of join; (2) quý mới chỉ vào khi cohort ≥30 mã (đầu mùa BCTC, as-of join "kéo dài tier cuối" của quý trước cho tới lúc đó — đúng thiết kế, không phải staleness). **2026-07-11 feasibility (Taylor job Taylor_20260711_145129)**: lineage 100% khớp (12.367/12.367 rows đối chứng `data/fundamental_rating_all.csv`), reproduction test chạy lại builder hôm nay = 82.3% exact tier / 99.9% ±1 bậc (18% lệch do adjusted-Close hồi tố, không phải lỗi formula), phủ tới 2026-07-08 (gồm 2026Q2) → rebuild + append-only refresh KHẢ THI. **2026-07-11 cơ chế refresh ĐÃ XÂY + dry-run verified (job Taylor_20260711_153405)**: frozen match 82.51% exact / 99.98% ±1 (floor abort 70%/99%), publish = DELETE 2 quý mở + INSERT trong 1 transaction (frozen rows không bị rewrite byte nào), quý mới cohort <30 chưa append (chặn tier-A giả từ cohort 1 dòng); staging table `tav2_bq.fa_ratings_refresh_staging` (chỉ refresh dùng, đừng đọc). Freshness WARN-only đã wire vào `bq_freshness_check.sh` + `data_registry_audit.sh` |
| `deploy_v11/fundamental_rating.py` | REAL nhưng STALE snapshot — external deploy package | Bản copy `fundamental_rating.py` bên trong `deploy_v11/` (gói triển khai BA-System V11 để đóng zip gửi ra ngoài, xem `deploy_v11/README.md`/`DEPLOY.md`) — KHÔNG phải research variant, là artifact deploy thật | Con người, ad-hoc mỗi lần đóng gói zip mới để giao (lần cuối commit `10ae395`, reorg 06-21) — KHÔNG có cron/script nào trong repo này tự sync | **2026-07-11 (Winston, job Winston_20260711_160905)**: xác nhận `crontab -l` + grep repo KHÔNG có gì gọi thư mục `deploy_v11/` — không phải dead code, chỉ là bản đóng gói ngoài, nên GIỮ NGUYÊN (không archive). Đã lệch khỏi bản canonical repo-root: thiếu pandas-3 date-parse fix + `FA_OUT_*` env override (thêm hôm nay 07-11) + POSIX `cat` (còn Windows `type` cứng). Cần đồng bộ tay lần đóng gói zip tiếp theo, không tự động. |
| `tav2_bq.fa_ratings_8l` | CANONICAL (as-of 8L) — refresh định kỳ, ghi-BQ đã xác nhận THẬT 2026-07-12 | Lịch sử point-in-time 8L rating (ticker, time=eff_date, route, rating 1–5, tier) — nguồn cho custom30 builders, `custom_basket.rating_asof`, regime_size overlay, DC-book double-confirm, mọi audit as-of, dự án re-tune SIGNAL_V11 | `rating_8l_history.py refresh_bq_table()` qua wrapper `mike/bin/refresh_fa_ratings_8l.sh`, cron **weekly thứ Bảy 08:30 ICT** (Winston proposal + user approved 2026-07-11) + cron TẠM **T3 20:00 ICT đến hết 2026-08-04** cho mùa BCTC Q2 (job Winston_20260713_103213, guard tự hết hạn — xem `cron_registry.md`). Bao gồm forensic-exclude override rows (append-at-flag-date, no hindsight) | Republish làm mọi backtest as-of lệch nhẹ → CSV pinned trong `results_registry.md` mới là chuẩn đối chứng. Lịch sử identity: test tay 2026-07-11 từng fail (`Access Denied` — wrapper thiếu `source wc_env.sh`, rơi về service account read-only `bq-reader-8l`); **fix `a9716f6` + test ghi THẬT 2026-07-12 OK: lastModified 06-20→07-12, rows 52.433→52.449, quant-skeptic CONFIRMED** — hết câu hỏi identity treo, lần scheduled đầu (07-14 T3 tạm / 07-18 T7) chỉ là chạy bình thường (wrapper alert Trading Daily nếu fail, không im lặng) |
| `data/rating_8l.csv` (+ `rating_8l_top30/_buynow/_screener.csv`) | CANONICAL (live snapshot) | Rating 8L HIỆN TẠI (2-axis quality×value, screener) | `rating_8l.py`, `pt_8l_daily.sh` step [1], 17:45 ICT hàng ngày | Là snapshot hôm nay, KHÔNG phải lịch sử PIT — backtest phải dùng `fa_ratings_8l` as-of, không được join CSV này vào quá khứ |
| `data/moat_tags.csv` | CANONICAL (human-curated) | Registry moat 5F-audit — CHỈ `moat_tier==WIDE` được +1 notch (standing rule user 2026-06-14) | Con người (Taylor/user) sau mỗi 5F audit; ad-hoc by design (mtime 06-14) | Không phải file tự sinh — đừng "refresh" bằng quant proxy; thiếu tên trong registry = notch chỉ là placeholder tạm |
| `data/forensic_flags.csv` | CANONICAL (human-curated) | Cờ forensic exclude (related-party/manipulation) — bơm override rating 5/E vào `fa_ratings_8l` từ ngày flag | Con người, ad-hoc (mtime 06-20) | Date-aware, không hindsight — sửa ngày flag trong quá khứ = bơm look-ahead vào mọi backtest as-of |
| `tav2_bq.fa_ratings_v5/_v8c/_v9/_ew5/_pre2014` | DEPRECATED (research variants) | Các biến thể rating thời nghiên cứu (v9 = RE-rebuild, pre2014 = phần mở rộng backtest trước 2014) | Đóng băng (pre2014 lastModified 05-16; các bản khác cũ hơn) | Chỉ vài script research cũ đọc. KHÔNG dùng cho việc mới — bản sống là `fa_ratings_8l`. **2026-07-11 (Winston, job Winston_20260711_160905, coding_guidelines §10):** 4 builder script variant tương ứng ở repo root — `build_fa_ratings_v9.py`, `build_fa_ratings_pre2014.py`, `fundamental_rating_v5.py`, `fundamental_rating_v8c.py` — đã xác nhận KHÔNG có caller active nào (grep toàn repo + `crontab -l` thật, chỉ có self-reference + audit script + doc mention) và **git-mv vào `archive/`** (giữ nguyên lịch sử git, không xoá). `mike/bin/data_registry_audit.sh` mục D đã hết WARN cho 4 file này. |

## Custom30 parking baskets (V2.4 NEUTRAL parking — money-path)

| Nguồn | Status | Là gì | Ai ghi / cadence | Bẫy |
|---|---|---|---|---|
| `tav2_bq.custom30v_8l` | **CANONICAL** (production parking) | Rổ custom30V (yieldcombo, namecap≤10%) — đúng rổ đã backtest +7.4pp; `golive_recommend_v23.py` đọc qua `custom30.TABLE_V`, `pt_v22_dt5g.py`/DC-book/screens cũng đọc | `custom30_history.py` với `CUSTOM30_TABLE=custom30v_8l`, `papertrade_daily.sh` step [6b] 15:30 ICT — **writer từng mồ côi 2026-06-18→07-11** (drop sau cutover 06-30), revive job Taylor_20260711_035824, **verify sống 07-11 15:45 ICT** (chạy tay, job Taylor_20260711_084145: 1440 rows/48 rebals, rebal hiện tại 2026-05-05, overlap 16/30 vs blend — đúng rổ yieldcombo) | 07-11 là THỨ BẢY → cron 1-5 không chạy cuối tuần; lần cron ĐẦU TIÊN chạy [6b] = T2 07-13 15:30 ICT (fix e02a75b vào sau lần cron cuối T6 07-10). Deadline thật = rebalance quý ~2026-08-05: nếu `MAX(rebal_date)` không nhích sau 08-05 → writer lại chết |
| `tav2_bq.custom30_8l` | **TRAP** (legacy blend, vẫn tươi hàng ngày) | Rổ blend liquidity-led — spec live TRƯỚC 2026-06-30, nay chỉ giữ cho audit ([6] default env của cùng script) | `custom30_history.py` default env, step [6] daily 15:30 (lastModified 07-10 — bảng SỐNG) | **Đã gây bug mislabel thật**: `golive_recommend_v23.py` đọc nhầm bảng này tới 2026-07-11 trong khi advisory ghi "custom30V" (fix cùng ngày). Bẫy kép: bảng tươi hàng ngày nên nhìn freshness không phát hiện được — "tươi" ≠ "đúng rổ". Code mới phải dùng `custom30.TABLE_V`, không hardcode tên |
| `data/custom30_8l_publish.csv` | DERIVED | Bản publish local của rổ hiện tại (env `CUSTOM30_CSV`) | Cùng script/cadence trên | Tên file mặc định là `custom30_8l_publish.csv` kể cả khi build rổ V — nhìn tên file không suy ra được rổ nào bên trong, phải xem env của lần chạy |

## BQ local cache (DuckDB/parquet — `data/bq_cache/`)

| Nguồn | Status | Là gì | Ai ghi / cadence | Bẫy |
|---|---|---|---|---|
| `data/bq_cache/*.parquet` (11 bảng: `ticker`, `ticker_prune`, `ticker_financial`, `ticker_1m`, `vnindex_5state_dt5g_live`, `vnindex_5state`, `vnindex_5state_tam_quan_v34b_clean`, `vnindex_5state_dt_4gate`, `fa_ratings`, `fa_ratings_8l`, `custom30v_8l`) | DERIVED (mirror) | Cache local threads=1 (~100ms vs 5-15s BQ) cho backtest/sim | `sync_bq_cache.py` qua `sync_bq_cache_daily.sh`, cron 23:45 ICT | 3 bẫy: (1) trễ 1 ngày cho mọi script chạy trước 23:45 (sự cố 2026-07-09); (2) **cache mirror CẢ bảng trap y nguyên tên** — `bq_cache/vnindex_5state.parquet` = v3.4b BASE chứ không phải DT5G, đọc cache không cứu khỏi đọc nhầm bảng; (3) cache mirror cả bảng FROZEN (`vnindex_5state_dt_4gate` chết 06-02) — mtime parquet là hôm qua nhưng DATA bên trong đứng yên từ nguồn (`fa_ratings` từng thuộc nhóm này, hết frozen từ 2026-07-12 khi refresh weekly sống lại). Riêng `fa_ratings`/`fa_ratings_8l`: nguồn refresh kiểu DELETE+INSERT/re-rank → sync chuyển sang `full_only` (full re-download mỗi đêm kể cả `--delta`, job Winston_20260713_103213) — delta-append cũ không vớt được row bị rewrite, gây count-mismatch giả mỗi thứ Bảy. Từng có bug sync `ticker` chết âm thầm ~06-26 (chunk parquet cũ) — đã fix; (4) **`ticker`/`ticker_prune` là THƯ MỤC chunked theo năm** (`data/bq_cache/ticker_prune/<year>.parquet`, đọc bằng glob `ticker_prune/*.parquet`) từ 2026-06-26 — file monolith cũ `ticker_prune.parquet` KHÔNG được sync nữa, đóng băng 06-26, user phát hiện stale 07-13; đã archive sang `data/archive/ticker_prune_monolith_frozen_20260626.parquet` + sửa hết 28 file .py từng đọc nhầm (27 script research/screen + `trading_bot/executor.py:507`) sang chunked (job Winston_20260713_143546). Đường dẫn đúng DUY NHẤT giờ là thư mục chunked |

## LAG book (PEAD) — caches bắt buộc cho paper sims

| Nguồn | Status | Là gì | Ai ghi / cadence | Bẫy |
|---|---|---|---|---|
| `data/earnings_px.pkl`, `data/lagged_pos_ov.pkl`, `data/earnings_surprise_data.pkl`, `data/earnings_events_classified.csv` | CANONICAL (LAG caches) | 4 cache LAG-leg (giá daily, Open+Volume, NP quý, events phân loại) mà pt_v22/pt_v4/mọi V12 sim phụ thuộc | `refresh_lagged_caches.py`, `papertrade_daily.sh` step [2], 15:30 ICT (mtime 07-10 ✓) | (1) Pickle ghi bằng pandas 3 — PHẢI đọc bằng `$DNA_PYEXE`, system python3/pandas 2.3 raise `NotImplementedError` (guidelines §8); (2) `pt_dates.detect_end_date()` cap END_DATE theo max time của `lagged_pos_ov.pkl` → file này stale = MỌI paper sim lặng lẽ đóng băng ngày cuối (đây chính là lý do sinh ra refresh step) |

## Research caches lớn (KHÔNG production — đừng nhầm là sống)

| Nguồn | Status | Là gì | Ai ghi / cadence | Bẫy |
|---|---|---|---|---|
| `data/ba_v11_unified_12y_sig.pkl` | Research cache — **rebuilt 2026-07-11 trên DT5G, max 2026-07-10** | Signal cache BAL/V11 cho ~90 script sim/tune | Rebuild tay khi cần. **Builder thật = `build_pkl_v11_current.py`** (dòng cũ ghi nhầm `build_state_free_signals.py` — script đó build bản state-FREE `ba_v11_state_free_sig.pkl` khác, chỉ ĐỌC pkl unified làm đối chứng; sửa 2026-07-11, job Taylor_20260711_165407). Bản rebuild DT5G: `mike/agents/Taylor/momdeal/rebuild_pkl_dt5g.py` | Production KHÔNG đọc file này (pt_v22/golive query BQ trực tiếp). ⚠️ Bản TRƯỚC 07-11 built trên bảng BASE (pre-F3) — state5/play_type bên trong là base, không phải DT5G; bản hiện tại đã verify 1.085/1.085 ngày divergent khớp `dt5g_live`. Backup bản base: `.bak_predt5g_20260711`. Sim đối chiếu kết quả cũ (trước 07-11) phải nhớ pkl đã ĐỔI cả state-source lẫn end-date |
| `data/VNINDEX.csv` | Research snapshot, frozen 2026-06-16 | VNINDEX daily + indicator + PE offline (~87 script đọc) | Vài script research tự ghi lại khi chạy; không có cron | CLAUDE.md gốc mô tả như file chuẩn offline nhưng KHÔNG tự tươi — phân tích thị trường "hiện tại" phải kiểm tra max(time) trước, hoặc query BQ |
| `data/fa_ratings_lh.csv` (05-15), `data/intraday_full.pkl` (05-17), `data/value_panel_2014.csv` (pinned PIT) | Research static | Panel nghiên cứu đông cứng (lh = long-history ratings; intraday study; value panel audit R3) | Không ai ghi định kỳ | `value_panel_2014.csv` đông cứng CHỦ ĐÍCH (input pinned của audit trong results_registry) — đừng refresh nó; 2 file kia stale tự nhiên |

## Trading bot / execution (money-path thật)

| Nguồn | Status | Là gì | Ai ghi / cadence | Bẫy |
|---|---|---|---|---|
| `secrets/trading_bot_accounts.json` | CANONICAL (config) | Hồ sơ account (enabled/mode/broker, `excluded_tickers`, override paper: extreme_regime, chase_cap) | Con người/Mike khi onboard hoặc đổi config | `excluded_tickers` case-sensitive (selfcheck đã cover); account mới `enabled:true/mode:live` TỰ ĐỘNG được cron dùng-chung nhận — thêm account = kiểm tra lại toàn bộ điểm đọc file này |
| `data/trading_rules.json` | CANONICAL (rules) | Hạn mức/rule giao dịch — Mafee đọc để CHẶN lệnh, DollarBill đọc để lập plan (neutral_parking 0.70, risk_dial_override…) | Taylor đề xuất, **user duyệt** mới áp live (mtime 07-03 = v2.1) | Sửa giữa phiên KHÔNG có hiệu lực tới lần load kế tiếp của bot (bot_execute đọc lúc start) |
| `data/trade_plans/plan_<account>_<YYYY-MM-DD>.json` | CANONICAL (plan) | Plan T+1 bot thực thi — tên file là CONTRACT | DollarBill (dispatch 19:00 ICT chain) ghi; user duyệt trước 08:45 | **Sự cố thật 2026-07-06**: `load_plan()` CHỈ đọc đúng tên chính tắc — file suffix `_v2`/`_superseded` vô hình với bot. Plan duyệt lại PHẢI đè lên tên chính thức, không để dạng suffix. `filter_excluded_tickers()` áp SAU load — generator quên exclude không sao, nhưng đổi tên file sai là chạy nhầm plan |
| `data/execution_logs/dnse_raw_<date>.jsonl` | CANONICAL (broker raw, authoritative) | Log thô mọi call DNSE — nguồn CHUẨN cho fill price (`averagePrice`/`fillQuantity`), balances, đối soát | `trading_bot/brokers.py` ghi mỗi call, trong phiên | File DÙNG CHUNG mọi account theo ngày — mỗi bản ghi phải lọc theo `account_no`/`label` (bug NAV lẫn account 2026-07-06 đã vá). Đây là nguồn duy nhất được phép làm cost-basis cho report (guidelines §6) |
| `data/execution_logs/exec_<label>_<date>_state.json` / `_journal.csv` | CANONICAL (bot state) | State + journal executor per account/ngày (idempotency guard `_ghost_tickers`, atomic write) | `trading_bot/executor.py`, liên tục trong phiên | Ghost-pause cần unpause THỦ CÔNG (by design); selfcheck driving Executor phải dùng TAG account riêng + dọn fixture cũ (guidelines §7) |
| `data/execution_logs/nav_history_<account>.csv` | CANONICAL (NAV series) | Chuỗi NAV ngày — nguồn duy nhất mọi báo cáo daily/weekly/monthly | `daily_nav_snapshot.py` trong `eod_trading_report.sh`, 15:00 ICT | MTM cùng ngày phải dùng giá DNSE, BQ chỉ cho ngày quá khứ (sự cố 07-06 đã vá); P&L cho vị thế legacy (ZaloPay) chưa đúng — known gap |
| `data/BOT_STOP` | CANONICAL (kill-switch) | File tồn tại = dừng mọi giao dịch tức thì | Con người tạo/xóa | Kiểm tra sự tồn tại của nó trước khi kết luận "bot không chạy là bug" |

## Paper-trading harness (account `main` + sleeves)

| Nguồn | Status | Là gì | Ai ghi / cadence | Bẫy |
|---|---|---|---|---|
| `data/trade_plans/plan_main_<date>.json` | CANONICAL (paper probe) | Probe plan cho paper `main` — evidence EXTREME gate + vol-scale chase-cap + fill-timing | `mike/bin/paper_main_probe_plan.py`, cron 08:52 ICT | PAPER-ONLY — account `main` mode=paper; đừng lấy plan này làm mẫu cho plan live (sizing/window cố ý khác) |
| `data/execution_logs/exec_main_*` | CANONICAL (paper evidence) | State/journal PaperBroker của `main` — dữ liệu gốc cho `execution_quality_review.py` + điều kiện go-live 3 patch | `bot_execute.py --account main`, cron 09:10/10:46/13:05 ICT | Evidence tích theo PHIÊN THẬT — ngày bot main không chạy (early_check alert) = lỗ hổng evidence, kéo dài lịch sign-off |
| `data/dc_book_waterfall_paper_state.json` | CANONICAL (paper sleeve) | State DC-book NEUTRAL idle-cash waterfall (paper, review event-anchored) | `dc_book_waterfall_paper.py --update`, cron 15:05 ICT | Atomic write có sẵn; đọc `history[-1]` cho EOD report — đừng tự tính lại từ đầu |
| `data/orb_pt_log.csv` + `data/orb_pt_status.json` | CANONICAL (paper sleeve) | ORB intraday VN30F1M paper (sleeve 1B riêng) | `orb_pt.py`, `papertrade_daily.sh` step [17] — **nguồn dữ liệu = Vnstock/VCI API 1-phút fetch sống mỗi lần chạy, KHÔNG phải BQ** | Flaky: phụ thuộc API ngoài, từng chết 4/8 phiên không ai hay (audit Winston 07-11 → nay có FAIL-alert cuối chain); mtime 07-08 lúc rà = đã miss phiên. Phiên chưa đóng đủ bar thì tự skip (by design) |

(Sổ vị thế production `data/pt_v22_dt5g_open_positions.csv` — xem section Market state ở trên.)

## Feeds hàng hóa / FX / khác (Winston — Data Ops)

| Nguồn | Status | Là gì | Ai ghi / cadence | Bẫy |
|---|---|---|---|---|
| `data/vcb_fx_rate.csv` | CANONICAL | Tỷ giá USD/VND VCB | `vcb_fx_feed.py`, cron 08:15 ICT T2-T6 (mtime 07-10 ✓) | — |
| `data/bdi_daily_real.csv` | CANONICAL | Baltic Dry Index daily | `fetch_bdi_daily.py`, `papertrade_daily.sh` step [21] (mtime 07-10 ✓) | — |
| `data/hog_price_vn.csv` | CANONICAL | Giá heo hơi (3tres3) | `hog_price_feed.py`, cron thứ Hai 09:00 ICT (mtime 07-06 ✓ = thứ Hai trước) | Cadence TUẦN — thấy mtime 5-6 ngày tuổi là bình thường |
| `data/<commodity>_monthly.csv` (6 file WB CMO) | CANONICAL | Giá hàng hóa tháng (World Bank CMO) | `auto_update_commodity_wb.sh`, cron ngày 5 + 10 hàng tháng 08:00 ICT (atomic + .bak) | Cadence THÁNG, 2 attempt vì WB publish trễ — đừng báo stale giữa tháng |
| `data/rubber_alert_state.json` | CANONICAL (state) | State alert cao su tuần | `rubber_weekly.sh`, cron 18:35 ICT T2-T6 | Là state chống alert lặp, không phải chuỗi giá |
| New-listings queue | CANONICAL | Danh sách niêm yết mới cho 8L research queue | `fetch_new_listings_daily.sh` → `fetch_new_listings.py`, cron 18:10 ICT T2-T6 | — |

## Cấu hình chiến lược / meta

| Nguồn | Status | Là gì | Ai ghi / cadence | Bẫy |
|---|---|---|---|---|
| `filter.json` | CANONICAL (source of truth) | Định nghĩa mọi buy/sell filter (`_Strategy`/`~Signal`/`$Strategy`/`Init`/MARKET_DICT_FILTER) | Con người khi đổi chiến lược; `gen_sql.py` convert → `sql_queries/*.sql` | Sửa filter.json mà quên chạy lại gen_sql = SQL cũ vẫn được dùng |
| `bigquery_dictionary.json` | CANONICAL (dictionary) | Semantic dictionary mọi cột BQ — tra TRƯỚC khi viết filter/query | Cập nhật tay khi schema đổi | — |
| `sql_queries/*.csv` | DERIVED (cache kết quả) | Kết quả query lần chạy cuối | Bash script sinh từ gen_sql | Là cache — không có timestamp guarantee, đừng dùng làm dữ liệu "hiện tại" |
| `data/results_registry.md` | CANONICAL (pinned baselines) | Số tham chiếu chính thức mọi backtest (R3 mới nhất: 28.82%/1.90/−15.7%/1.83, re-pin dt5g 2026-07-11 commit 09724bc) | Taylor, sau mỗi lần pin/re-pin | Filename CSV canonical là artifact read-only — experiment PHẢI đổi tên output (guidelines §8, sự cố overwrite 07-06); regenerate phải dùng đúng lệnh pin + `$DNA_PYEXE` |

## Quy tắc chọn universe (ticker vs ticker_prune vs ticker_1m)

- **Backtest/ML/breadth** → `ticker_prune` (universe chất lượng; breadth chỉ có nghĩa từ ~2008).
- **Live screening/daily eval** → `ticker_1m` (có Trading_Value, pattern stats, outcome cols).
- **`ticker` full** → chỉ khi cần phủ toàn bộ mã (15.2M rows, có đuôi illiquid có thể trễ ingest
  — freshness triage chỉ tính `ticker_prune`+VNINDEX, xem memory `dataops-completeness-universe`).
- Cột `profit_*` (forward-looking) ở cả 3 bảng: CHỈ để train, cấm dùng filter live.

## Cần bổ sung (phần còn thiếu thật sau sweep 2026-07-11)

- Nguồn dữ liệu của BA-system Telegram (`telegram_recommend.py`, cron 18:00 ICT) — chưa rà.
- `webui/utils.py` (codebase ngoài — MarketEvaluation) — nguồn dữ liệu riêng của nó chưa rà.
- PHS broker (BLOCKED, paper-only) — chưa có nguồn nào wire, rà khi credential thông.
- Các bảng BQ archive lẻ chưa liệt kê từng dòng (họ `_archive_*`) — đã gộp 1 dòng ARCHIVE,
  chi tiết tra `vnindex_5state_registry.md`.

## Lịch sử
- 2026-07-17 (Winston, job Winston_20260717_072420): triển khai Layer A refresh routine cho `deposit_rate_vn.py` (user approved). Thêm `data/deposit_rate_vn_events.csv` (append-only, 5 cột) + patch `deposit_events_df()` (backward-compatible: CSV rỗng = hành vi cũ y hệt, verified regression `current_deposit_rate()`=6.80%) + `append_deposit_rate.py` (CLI append idempotent + atomic + verify) + `refresh_deposit_rate_vn.sh` (cron nhắc 08:10 ICT ngày 3, best-effort fetch KHÔNG tự ghi) + WARN freshness >45 ngày trong `ops_health_check.sh` §8. Đổi status entry `deposit_rate_vn.py` từ "CHƯA có cron" → đã có refresh routine.
- 2026-07-17 (Taylor, job Taylor_20260717_063638): thêm nguồn mới `gdp_growth_vn.py` (World Bank real GDP annual, CANONICAL single-tier) cho DCF terminal-growth research. Thêm consumer mới cho `deposit_rate_vn.py`: `dcf_refresh_gate.py` (gate refresh có điều kiện theo biên độ 1pp). DCF earning-power/terminal-g study: research, NOT wired production (quant-skeptic CONFIRMED — earning-power NO-GO redundant w/ 1/PE, GDP terminal-g = level/display fix không phải alpha).
- 2026-07-14 (Winston, job Winston_20260714_055051): thêm `dcf_valuation.py` + `dcf_backtest.py` làm consumer mới vào 2 entry đã có — `deposit_rate_vn.py` (dùng `current_deposit_rate()` làm risk-free rate baseline) và `cpi_vn.py` (CPI làm terminal growth rate input). Cả 2 là research tool, NOT wired production (job Taylor_20260714_051643).
- 2026-07-13 (Winston, job Winston_20260713_131255): thêm 2 row thiếu trong mục "Vĩ mô" —
  `deposit_rate_vn.py` (data prerequisite §2 plan Pillar A′, `Taylor_20260713_124803`) và
  `cpi_vn.py` (phát hiện PHỤ trong lúc làm, đã có sẵn từ 2026-07-06 nhưng chưa vào registry). Cả
  2 là proxy hồi tố/fetch-tay-1-lần, KHÔNG có cron refresh — gap vận hành giống nhau, đề xuất
  routine tháng ở `proposal_deposit_rate_monthly_refresh_20260713.md` (chưa duyệt/cài).
- 2026-07-13 (Winston, job Winston_20260713_103213): cập nhật 3 row lỗi thời sau khi refresh
  fa_ratings/fa_ratings_8l sống lại 07-12 (identity fix `a9716f6`, test ghi thật OK, quant-skeptic
  CONFIRMED): row `fa_ratings` hết "STATIC/chờ duyệt cron/lastModified 05-10", row `fa_ratings_8l`
  hết "cron chưa xác nhận ghi được/đứng 06-20", row `bq_cache` hết "fa_ratings chết 05-10". Kèm
  cùng commit: `sync_bq_cache.py` chuyển 2 bảng này sang `full_only` (delta-append không tương
  thích refresh DELETE+INSERT/re-rank) + cron tạm T3 mùa BCTC đến 2026-08-04 (xem
  `cron_registry.md`).
- 2026-07-11: tạo lần đầu, seed từ sự cố SIGNAL_V11 base-leak + các gotcha đã biết trong
  CLAUDE.md/coding_guidelines.md.
- 2026-07-11 (Taylor sweep, job Taylor_20260711_080014): rà toàn codebase (grep mọi `tav2_bq.*`,
  file `data/*` dùng chung, crontab thật, `bq show` lastModified thật, mtime thật). Thêm 8 section
  mới (~35 nguồn): 8L rating, custom30 baskets, bq_cache, LAG caches, research caches, trading
  bot/execution, paper harness, feeds Winston, config/meta, quy tắc universe. TRAP/rủi ro mới phát
  hiện: `custom30_8l` vs `custom30v_8l` (mislabel bug thật 07-11, bảng sai lại TƯƠI hàng ngày);
  `tav2_bq.fa_ratings` STATIC không writer nhưng vẫn là input production SIGNAL_V11;
  `vnindex_5state_dt_4gate` BQ chết 06-02 nhưng CSV local sống (cache mirror bản chết);
  `data/vnindex_5state.csv` twin local của bảng trap; cache DuckDB mirror nguyên tên cả bảng trap.
- 2026-07-11 (họp team, job Taylor_20260711_084145, quant-skeptic CONFIRMED): `custom30v_8l` đóng
  gap (root cause = lịch thứ Bảy, không phải writer hỏng — xem row Custom30). `fa_ratings` →
  khuyến nghị migrate sang `fa_ratings_8l` NHƯNG qua full validation (66% tier khác nhau = đổi
  signal), CHƯA đánh dấu DEPRECATED — đang ở bước backtest song song (job Taylor_20260711_094714,
  user duyệt hướng validate 2026-07-11). Xem mục 5 "Nguyên tắc bắt buộc" cho quy trình obsolete
  đầy đủ, thêm cùng ngày theo yêu cầu user ("quản lý phần này phải thật sự cẩn trọng").
- 2026-07-12 (Taylor, job Taylor_20260711_165407, momdeal Phase 0): sửa row `ba_v11_unified_12y_sig.pkl`
  — builder ghi nhầm (`build_state_free_signals.py` → thật ra là `build_pkl_v11_current.py`); pkl rebuilt
  trên `dt5g_live` (bản cũ base-leak pre-F3), backup `.bak_predt5g_20260711`. Phát hiện thêm:
  `bigquery_dictionary.json` THIẾU định nghĩa họ cột `profit_*` (forward return, đơn vị **PHẦN TRĂM** —
  verify thực nghiệm = `LEAD(Close,40)/Close−1 ×100` cho profit_2M) — Winston nên bổ sung dictionary.
- 2026-07-11: xây `bin/data_registry_audit.sh` (regression-guard cơ học cho 2 sự cố base-leak +
  custom30-mislabel, freshness re-check 3 nguồn rủi ro cao nhất, reference-count snapshot cho
  nguồn deprecated/dead) — wire vào Friday KB editorial review (`kb_nightly.sh` Phase 5). Chạy
  thật lần đầu: FAIL=0/WARN=0, xác nhận cả regression-guard lẫn freshness đều đúng thực tế.
