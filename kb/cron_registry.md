# Cron Registry — mọi job crontab, theo thứ tự thời gian ICT

> Nguồn seed v1: audit `mike/agents/Winston/audit_cron_order_20260712.md` +
> `mike/agents/Winston/audit_paper_cron_cleanup_20260712.md` (2026-07-12). **Cập nhật file này CÙNG
> COMMIT** với mọi thay đổi crontab (thêm/xoá/đổi giờ một dòng) — xem quy tắc thêm cron mới ở cuối file.
> Giờ = ICT (UTC+7). Cột "Đọc" ghi rõ vintage (live/T-1/T-2...) — cache `BQ_LOCAL_CACHE` luôn = T-1,
> sync 23:45 T2-T6, KHÔNG sync cuối tuần.

## Bảng chính

| Giờ ICT | Script | Đọc (nguồn + vintage) | Ghi | Consumer | Buffer/depends-on | Verify-artifact |
|---|---|---|---|---|---|---|
| 06:00 (T2-T6) | `newdeals_daily_report.py` | BQ live | Telegram/Discord watchlist | AlphaLens paper monitor (đến 09-30) | độc lập | — |
| 08:00 (ngày 5, 10) | `auto_update_commodity_wb.sh` | World Bank CMO (idempotent, 2 attempts) | `iron_ore/urea/dap_monthly.csv` | feed archive, chưa có consumer sống | độc lập | — |
| 08:15 (T2-T6) | `vcb_fx_feed.py` | VCB web | `vcb_fx_rate.csv` | feed archive | độc lập | — |
| 08:20 (T2-T6) | `ops_health_check.sh` "Trước phiên sáng" | trạng thái vận hành (plan conflict, journal error, circuit breaker, câu hỏi 48h) | Discord Trading Daily | user | trước preflight 08:45 | post message |
| 08:30 (Sat) | `refresh_fa_ratings_8l.sh` | `ticker_financial` BQ live (đọc-ghi) | `tav2_bq.fa_ratings_8l` | custom30 builder, golive sizing, DC-book, SIGNAL_V11 8L re-tune | trước 09:15 (45') | `bq show` lastModified+numRows |
| 08:45 (T2-T6) | `preflight_check.sh` | plan file `plan_<acct>_<date>.json`, circuit breaker | GREEN/RED gate | user (duyệt trước mở cửa 09:00) | sau plan T+1 (đêm hôm trước 21:00) | verify plan_date + field orders |
| 08:52 (T2-T6) | `paper_main_probe_plan.py` | — | probe plan cho paper `main` | 09:10/10:46 bot_execute --account main | — | (a) trial mở — xem F1 dưới |
| 09:05 (T2-T6) | `run_bot.sh --account SpaceX/ZaloPay --auto-otp` | plan file (đã verify ở preflight) | lệnh thật DNSE | — | — | fill log |
| 09:00-14:55 (mỗi 5', T2-T6) | `bot_heartbeat.sh <acct>` | process liveness | Discord fill digest | user | grace 09:00-09:10/13:00-13:10 | — |
| 09:10 (T2/T4/T6) | `bot_execute.py --account main` (SELL-window evidence) | — | paper fill log | fill-timing checkpoint (~07-31) | — | (a) trial mở |
| 09:40 (T2/T4/T6) | `paper_main_early_check.sh morning` | paper main fill log | early-fail alert | user | 30' sau 09:10 | — |
| 10:46 (T3/T5) | `bot_execute.py --account main` (BUY-window evidence) | — | paper fill log | fill-timing checkpoint (~07-31) | — | (a) trial mở |
| 11:16 (T3/T5) | `paper_main_early_check.sh morning` | — | early-fail alert | user | 30' sau 10:46 | — |
| 11:30 (T2-T6) | `pkill bot_execute --account SpaceX/ZaloPay` | — | dừng bot nghỉ trưa | — | pattern `[b]ot_execute` (fix 07-06) | — |
| 11:31 | `session_announce.sh lunch` | — | Discord thông báo | user | — | — |
| 11:32 (T2-T6) | `pkill bot_execute --account main` | — | dừng paper main nghỉ trưa | — | — | — |
| 12:45 (T2-T6) | `ops_health_check.sh` "Trước phiên chiều" | như 08:20 | Discord Trading Daily | user | trước resume 13:00 | — |
| 13:00 (T2-T6) | `run_bot.sh --account SpaceX/ZaloPay --auto-otp` (resume) | state.json | lệnh thật DNSE | — | — | fill log |
| 13:01 | `session_announce.sh afternoon` | — | Discord thông báo | user | — | — |
| 13:05 (T2-T6) | `bot_execute.py --account main` (afternoon) | — | paper fill log | fill-timing/EXTREME/chase-cap evidence | — | (a) trial mở |
| 13:35 (T2-T6) | `paper_main_early_check.sh afternoon` | — | early-fail alert | user | 30' sau 13:05 | — |
| 14:50 (T2-T6) | `session_announce.sh close` | — | Discord thông báo | user | — | — |
| 15:00 (T2-T6) | `eod_trading_report.sh` (`for_each_live_account.sh`) | `state.json` fill giá thật + `daily_nav_snapshot.py` | Discord Trading report | user | sau ATC ~14:50 | `verify_account_snapshot.py` cross-check |
| 15:05 (T2-T6) | `dc_book_waterfall_paper.py --update` | live BQ/DNSE | DC-book paper NAV | Paper Programs report 15:20 | trước 15:20 | idempotent theo data_date |
| 15:20 (T2-T6) | `paper_programs_daily_report.sh --post` | `papertrade_compare5.csv` + registry | Discord Trading report | user | sau 15:05/15:30(hôm trước) | render registry |
| 15:30 (T2-T6) | `papertrade_daily.sh` (23 step, xem chi tiết §papertrade) | cache T-1 (đa số step) + BQ live (vài step) | nhiều CSV/BQ table sim | 15:20 report hôm sau, dashboards | — | continue-on-error + FAIL alert cuối chain |
| 17:45 (T2-T6) | `pt_8l_daily.sh` (9 step 8L production) | `dt5g_live` — **⚠️ trước refresh 18:30 → luôn đọc regime HÔM QUA** (M3, optional reorder) | rating/screener/dna/alerts | user Telegram | — | — |
| 18:00 (T2-T6) | `telegram_run_daily.sh` | `dt5g_live` — cùng vấn đề M3 | Telegram BA-system report | user | — | — |
| 18:10 (T2-T6) | `fetch_new_listings_daily.sh` | web listings | queue nghiên cứu 8L | Winston | — | — |
| 18:30 (T2-T6) | `daily_refresh_v34b_linux.sh` (13 step) | ticker_prune BQ live (ingest xong ~17:30) | `vnindex_5state` (base) + `_v34b_clean` + `dt5g_live` (fix C1 07-12: publish đọc LIVE, không qua cache) | pt_8l/telegram hôm sau, bq_freshness 19:00, mọi consumer regime | ~90' worst-case + retry | step [13] mtime-assert |
| 18:35 (T2-T6) | `rubber_weekly.sh` | web feed | rubber alert | Winston | lệch 5' so 18:30 (tránh trùng CPU) | — |
| 18:40 (T2-T6) | `update_shares_live.sh --scan` | corp-action feed | detection-only alert (KHÔNG merge `updated_at` — chỉ MERGE khi xử lý tay) | Winston/Taylor | — | ⚠️ H2: freshness check calibrate sai giả định writer-daily, đang hạ BLOCK→WARN (2026-07-12) |
| 19:00 (T2-T6) | `bq_freshness_check.sh --quiet` (pipeline BQ freshness + DT5G/recommend + dispatch Bill) | BQ live (không cache) cho freshness; pipeline-1 `publish_gated_state` (fix C1) | freshness log + golive recommend + bus | 21:00 send_plan, DollarBill | sau 18:30 (30') | `MAX(time)` từng bảng |
| 19:00 (daily) | `kb_nightly.sh` | events_buffer | trim/archive | — | — | — |
| 20:00 (daily) | *(giữ chỗ — không có job)* | | | | | |
| 21:00 (T2-T6) | `send_plan_report.sh` (`for_each_live_account.sh`) | file plan `plan_<acct>_<T+1 date>.json` | Discord DollarBill plan channel | user (duyệt qua đêm) | sau 19:00 (2h) | verify `plan_date`=next_trading_day + field `orders` |
| 23:45 (T2-T6) | `sync_bq_cache_daily.sh` | BQ live | `data/bq_cache/*` (DuckDB parquet) | mọi script source `wc_env.sh` + `BQ_LOCAL_CACHE` (papertrade, sims, backtest) | sau daily_refresh (~5h dư) | preflight_bq_cache.py 12 bảng (thiếu `custom30_8l` — L6b, chưa fix) |
| 00:00 (daily) | `fleet_backup.sh` | git repo | GitHub `mike-fleet` branch | DR | sau sync 23:45 (~15') | — |
| 00:30 (daily) | `daily_retro.sh` | events hôm qua trọn vẹn | retro report + Wags verify | user | sau backup (00:00) | — |
| 02:00 (daily) | `kb_nightly.sh` | events_buffer | trim/archive KB | — | — | — |
| Friday 15:00 | `check_sbv_weekly.sh` | SBV web | `sbv_macro_overlay` | DT5G Pillar A | — | — |
| Mon 09:00 | `hog_price_feed.py` | web | feed archive | chưa consumer sống | — | — |
| Sat 09:15 | `refresh_fa_ratings.sh` | `ticker_financial` BQ live (append-only) | `tav2_bq.fa_ratings` | custom30 builder cũ, audit | sau fa_ratings_8l (45') | `bq show` lastModified+numRows, invariant quý đóng băng |
| mỗi giờ :07 | `consolidate.sh` | bus | KB | — | — | — |
| mỗi 10' | `watchdog.sh`, `discover_sessions.py`, `resume_pending.py` | — | — | — | — | — |
| @reboot + mỗi 5' | `discord_bot/start.sh` | — | supervisor | — | — | — |

### §papertrade_daily.sh (15:30) — step nội bộ đáng chú ý
`[1] pull_us_market` (Pillar B feed) → `[2] refresh_lagged_caches` (input LAG live) → `[3] snapshot_state_vintage`
→ `[4] macro_healthcheck` (ghi `macro_health.json`, input fail-safe `get_gated_state`) → `[6]`/`[6b] custom30_history`
(blend audit / **production** `custom30v_8l`) → `[7][8][11][12] pt_v11/pt_v12/pt_v4/pt_v22` (control-arm
`engine_room_oos` panel, review 2026-12-01 — **pt_v22 là PRODUCTION**, đọc bởi `trading_bot/strategies.py`)
→ `[14] papertrade_compare` (ghi `compare5.csv`, đọc bởi registry 15:20) → `[17] orb_pt` (trial mở, event-end)
→ `[19][20][21][22]` alerts/feeds (`[22] edge_health_monitor --refresh` — ⚠️ bug logic đang fix 2026-07-12,
xem `data/lag_edge_health.csv`) → `[26] phosphorus_dgc_weekly` (Fri only). Block RETIRED `[15][16][18][23][24][25]`
giữ nguyên comment-out (archive pattern, KHÔNG xoá — xem coding_guidelines §10).

## Quy tắc thêm cron mới — 4 câu hỏi bắt buộc trả lời TRƯỚC khi chọn giờ

1. **ĐỌC gì, vintage nào?** Phân loại: BQ live / BQ local cache (luôn T-1, không sync cuối tuần,
   ⚠️ có thể ẨN — mọi script source `wc_env.sh` và đi qua `simulate_holistic_nav.bq` là consumer
   cache dù code không nhắc chữ "cache"; phải grep CHUỖI IMPORT, không chỉ tên biến — bài học C1:
   `publish_gated_state.py` tưởng đọc live suốt ~2.5 tuần) / DNSE live API (bắt buộc cho MTM
   same-day) / file local (ghi rõ ai ghi, lúc nào) / web external (retry bao lâu).
2. **Nguồn đó TƯƠI lúc nào?** Đo thật bằng log/query khi nghi ngờ — KHÔNG dùng mốc trong comment
   cũ (đã sai nhiều lần). Mốc đã đo (2026-07): ticker/ticker_prune ingest same-day ≤~17:30 ICT;
   DT5G tươi sau daily_refresh 18:30 (đọc live); recommendations/plan tươi sau pipeline 19:00;
   cache tươi-T-1 sau 23:45.
3. **Job cần T hay T-1?** T-1 đúng cho planning-trước-mở-cửa/paper report → cache OK, giờ nào
   cũng được miễn sau 23:45 đêm trước. Cần T (regime EOD, MTM same-day, freshness gate) → BẮT BUỘC
   nguồn live VÀ chạy sau mốc nguồn có T.
4. **Ai tiêu thụ, deadline của họ?** Vẽ chuỗi job→consumer→deadline cuối (thường preflight 08:45
   sáng hôm sau).

### Chống xung đột tài nguyên
- ≥2 writer cùng đích → atomic write (tmp+`os.replace`) hoặc append-only+tag nguồn hoặc tách giờ.
- File đọc-sửa-ghi (kiểu `events_buffer.md`) → flock cùng lock với writer khác.
- Không đặt 2 job nặng CPU/network trùng phút — lệch tối thiểu 5' (tiền lệ rubber 18:30→18:35).
- pkill trong cron: pattern không tự khớp chính nó (`[b]ot_execute` — bài học 07-06).

### Buffer — nguyên tắc "buffer + VERIFY ARTIFACT, không tin giờ"
Buffer tối thiểu = runtime upstream đo thật (gồm retry) + ≥10' dự phòng. Buffer KHÔNG BAO GIỜ là
bảo chứng duy nhất — downstream production PHẢI verify artifact (mtime, ngày trong file, MAX(time)
BQ) trước khi dùng. Publish bảng production (regime/giá/plan) PHẢI đọc nguồn live — `env -u
BQ_LOCAL_CACHE` nếu import chain có thể dính cache (bài học C1).

### Ghi lại ở đâu
- Comment crontab: giờ ICT + "sau X vì Y, trước Z vì W" + ngày đổi + commit.
- **File này** — cập nhật CÙNG COMMIT với mọi thay đổi crontab.
- Đổi giờ 1 job giữa ngày → kiểm tra job có bị nhảy khe hôm đó không, chạy tay bù nếu cần
  (bài học C1b, 07-10 daily_refresh miss vì đổi giờ giữa ngày).
- Cuối tuần/lễ: khai báo rõ job chạy 1-5/6/0-4/daily; nhớ cache không sync cuối tuần, lễ VN chưa
  encode đủ trong `vn_market.py`.

## Log thay đổi
- 2026-07-12: seed v1 từ audit `Winston_20260712_142100` + `Winston_20260712_151206`. Xoá 1 dòng
  crontab dangling comment (`# V2.4 go-live flip`). Fix C1 (publish DT5G đọc live, commit `4995262`).
  H2 (shares_outstanding_live BLOCK→WARN) đang dispatch.
