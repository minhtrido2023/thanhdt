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
| 08:10 (ngày 3) | `refresh_deposit_rate_vn.sh` | best-effort direct fetch (CafeF, timeout 15s, hay fail — **KHÔNG BQ**) — **CHỈ ĐỌC, KHÔNG dispatch agent** | Gửi notify.sh nhắc thủ công vào Trading Daily; **người thật** chạy `append_deposit_rate.py --source manual_verify` để ghi `data/deposit_rate_vn_events.csv` (auto-write bị loại bỏ 2026-07-20 sau 6 vòng adversarial review) | `rating_8l.py` NEUTRAL tilt (LIVE) + `dcf_refresh_gate.py` (ngày 11) | trước DCF refresh-gate ngày 11 | `data/refresh_deposit_rate_vn_YYYY-MM.log` |
| 08:10 (ngày 11) | `dcf_refresh_gate.py` | `deposit_rate_vn.current_deposit_rate()` (as-of, step series — **KHÔNG BQ/cache**) + prior `data/dcf_refresh_state.json` | `data/dcf_refresh_state.json` (atomic) + `data/dcf_refresh_gate.log` (append) | ai tái tạo số DCF cho report/dashboard: gọi `run_gate()`, chỉ recompute fair value khi `refresh=True` | SAU deposit-rate ngày 3 | `data/dcf_refresh_gate.log` |
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
| 19:10 (T2-T6) | `eod_trading_report.sh` (`for_each_live_account.sh`) | `state.json` fill giá thật + `daily_nav_snapshot.py` + `dna_report.build_dt_gate_line()` đọc `dt5g_live` BQ live | Discord Trading report | user | sau publish DT5G ~19:01 (9' buffer); sau ATC ~14:50 (fill đã có từ ~14:50, chỉ cần chờ regime T) | `verify_account_snapshot.py` cross-check |
| 15:05 (T2-T6) | `dc_book_waterfall_paper.py --update` | live BQ/DNSE | DC-book paper NAV | Paper Programs report 15:20 | trước 15:20 | idempotent theo data_date |
| 15:20 (T2-T6) | `paper_programs_daily_report.sh --post` | `papertrade_compare5.csv` + registry | Discord Trading report | user | sau 15:05/15:30(hôm trước) | render registry |
| 15:30 (T2-T6) | `papertrade_daily.sh` (23 step, xem chi tiết §papertrade) | cache T-1 (đa số step) + BQ live (vài step) | nhiều CSV/BQ table sim | 15:20 report hôm sau, dashboards | — | continue-on-error + FAIL alert cuối chain |
| 19:20 (T2-T6) | `pt_8l_daily.sh` (9 step 8L production) | `rating_8l.py`+`cheap_pb_floor.py` đọc `dt5g_live` BQ live; step [9] `sector_lens_monitor.py` đọc **BQ_LOCAL_CACHE** (T-1, known limitation chấp nhận được — chỉ ảnh hưởng monitor nội bộ, không chạm trading production) | rating/screener/dna/alerts | user Telegram | sau publish DT5G ~19:01; sau eod_trading_report 10' | — |
| 19:35 (T2-T6) | `telegram_run_daily.sh` | `dt5g_live` BQ live; đọc sau `pt_8l_daily` để `rating_8l.csv` tươi cho cột R | Telegram BA-system report | user | sau pt_8l_daily 15' | — |
| 18:10 (T2-T6) | `fetch_new_listings_daily.sh` | web listings | queue nghiên cứu 8L | Winston | — | — |
| 18:30 (T2-T6) | `daily_refresh_v34b_linux.sh` (13 step) | ticker_prune BQ live (ingest xong ~17:30) | `vnindex_5state` (base) + `_v34b_clean` + `dt5g_live` (fix C1 07-12: publish đọc LIVE, không qua cache) | pt_8l/telegram hôm sau, bq_freshness 19:00, mọi consumer regime | ~90' worst-case + retry | step [13] mtime-assert |
| 18:35 (T2-T6) | `rubber_weekly.sh` | web feed | rubber alert | Winston | lệch 5' so 18:30 (tránh trùng CPU) | — |
| 18:40 (T2-T6) | `update_shares_live.sh --scan` | corp-action feed | detection-only alert (KHÔNG merge `updated_at` — chỉ MERGE khi xử lý tay) | Winston/Taylor | — | freshness check `shares_outstanding_live` hạ BLOCK→WARN (H2 fix, commit `6459b6d`, 2026-07-12) — cadence event-driven thật, không phải daily |
| 19:00 (T2-T6) | `bq_freshness_check.sh --quiet` (pipeline BQ freshness + DT5G/recommend + dispatch Bill) | BQ live (không cache) cho freshness; pipeline-1 `publish_gated_state` (fix C1) | freshness log + golive recommend + bus | 21:00 send_plan, DollarBill | sau 18:30 (30') | `MAX(time)` từng bảng |
| 19:00 (daily) | `kb_nightly.sh` | events_buffer | trim/archive | — | — | — |
| 20:00 (DAILY, ♾️VĨNH VIỄN — chỉ chạy thật trong cửa sổ mùa BCTC) | `fa_ratings_earnings_window_daily.sh` — gate ngày ICT trong wrapper: **tháng ∈ {1,4,7,10} ∧ ngày ≥ 15 ∧ weekday T2-T6 ∧ không lễ VN** (`trading_bot.vn_market.is_holiday`, fixed-list; lễ biến động như Tết ÂL CHƯA encode — best-effort, đã ghi trong comment script). Không cần check "≤ ngày cuối tháng": date hợp lệ không vượt quá số ngày thật của tháng, cửa sổ tự đóng khi sang tháng vì điều kiện tháng fail. Đúng gate → chạy `refresh_fa_ratings_8l.sh` rồi `refresh_fa_ratings.sh` sau đúng 45' (giữ spacing mẫu Sat); sai gate → no-op, log 1 dòng skip-reason, không alert | `ticker_financial` BQ live (đọc-ghi, ingest same-day ~17:30 → bắt filings trong ngày) | `tav2_bq.fa_ratings_8l` (20:00) + `tav2_bq.fa_ratings` (20:45) | như 2 dòng Sat; mùa BCTC cohort ngày đầu chưa đầy đủ → cần re-rate mỗi ngày để bắt kịp mã mới báo cáo (user directive 2026-07-14) | sau ingest 17:30 + daily_refresh 18:30 + pipeline 19:00; trước sync cache 23:45 (cache full_only vớt ngay đêm đó) | `bq show` lastModified+numRows; 2 wrapper con tự alert nếu fail; gate test 18 ca (`--check YYYY-MM-DD`) |
| 21:00 (T2-T6) | `send_plan_report.sh` (`for_each_live_account.sh`) | file plan `plan_<acct>_<T+1 date>.json` | Discord DollarBill plan channel + marker `mike/state/plan_report_sent/<acct>_<date>.json` (md5 nội dung, loại field approval) | user (duyệt qua đêm) | sau 19:00 (2h) | verify `plan_date`=next_trading_day + field `orders` |
| 23:00 (T2-T6) — ĐÃ CÀI 2026-07-13 (commit `4216295`, quant-skeptic CONFIRMED) | `send_plan_report.sh --second-chance` (`for_each_live_account.sh`) | file plan (bản mới nhất trên đĩa lúc 23:00) + marker 21:00 | gửi lại plan cho user NẾU: 21:00 fail mà giờ file đúng, HOẶC plan đổi nội dung sau khi gửi; NO-OP nếu đã gửi + không đổi | user (duyệt qua đêm — sự cố 07-13: plan fix 22:17 không ai gửi lại) | sau khung re-dispatch tối (~22:1x đo thật), trước sync 23:45 (45') | idempotent qua marker md5; escalate lần 2 nếu vẫn thiếu/sai |
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
→ `[19][20][21][22]` alerts/feeds (`[22] edge_health_monitor --refresh` — rebuild `data/lag_edge_health.csv`
vô điều kiện mỗi lần chạy; dừng ở 2026-05-11 là ĐÚNG lịch sử mùa vụ (zero sự kiện NP_R 05-05→07-07),
KHÔNG phải bug — điều tra + đóng 2026-07-12, `Taylor_20260712_155038`) → `[26] phosphorus_dgc_weekly`
(Fri only). Block RETIRED `[15][16][18][23][24][25]`
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
- 2026-07-20 (Mike, user approved trực tiếp — "để bạn tự động cập nhật thông tin mà không phụ
  thuộc tôi"): nâng cấp `refresh_deposit_rate_vn.sh` từ CHỈ-NHẮC sang tự-xác-nhận-và-ghi. Không
  còn dừng ở "nhắc con người chạy `append_deposit_rate.py`" — giờ tự dispatch Winston mỗi tháng để
  WebSearch-crosscheck lãi suất Big-4 12M kênh online qua ≥2 nguồn độc lập (hoặc 1 bài báo liệt kê
  đủ 4 ngân hàng cùng ngày, tự nó là đối chiếu chéo), CHỈ ghi khi đủ bằng chứng — nếu mâu thuẫn/thiếu
  bằng chứng thì escalate y hệt luồng cũ, không tự đoán. Thêm `--source web_crosscheck_auto` vào
  `append_deposit_rate.py` (bắt buộc `--note` non-empty, tách biệt khỏi `manual_verify` để giữ đúng
  provenance — không phải người trực tiếp xác nhận). Test end-to-end thật ngay trong phiên (không
  đợi cron ngày 3): Winston tìm được 3 nguồn (CafeF 18/7, Kenh14 16/7, CafeF 13/7) đều xác nhận
  6.8% — khớp record đã có sẵn cùng ngày (do Mike tự tay append trước đó) nên tự SKIP đúng
  (idempotent), không ghi trùng. 4 câu hỏi §11 không đổi so với entry gốc bên dưới (vẫn đọc
  `current_deposit_rate()` KHÔNG BQ/cache, vẫn chạy ngày 3 trước DCF gate ngày 11, vẫn KHÔNG cần T
  chính xác, vẫn consumer = `rating_8l.py` NEUTRAL tilt + `dcf_refresh_gate.py`) — chỉ đổi CƠ CHẾ
  ghi (agent-driven crosscheck thay vì chờ người), không đổi lịch/nguồn/consumer. Chi tiết đầy đủ +
  review đối kháng: `kb/projects/deposit-rate-autocheck.md`.
- 2026-07-17 (Taylor, job `Taylor_20260717_074106`, **user approved trực tiếp**): thêm 1 dòng cron
  `10 1 11 * *` (08:10 ICT ngày 11 hàng tháng) gọi `dcf_refresh_gate.py` — cổng refresh có điều kiện:
  recompute DCF **chỉ khi** lãi suất Big-4 12M dịch ≥1.0pp so lần dùng trước (boundary =1.0pp
  **INCLUSIVE** — CHỐT, flag `THRESHOLD_INCLUSIVE=True`, không còn "chờ user"); else giữ số cũ (SKIP).
  Gate chỉ QUYẾT ĐỊNH + PERSIST, không tự chạy recompute. 4 câu hỏi §11: (1) đọc
  `deposit_rate_vn.current_deposit_rate()` (as-of, step series) + prior state JSON — **KHÔNG BQ/cache**,
  granularity tháng nên không vintage-sensitive; (2) nguồn tươi phụ thuộc deposit-rate ngày 3 đã cập
  nhật (con người xác nhận số) → chạy ngày 11 để nằm SAU ngày 3; (3) KHÔNG cần T chính xác
  (`_now_ict_date` dùng UTC date, monthly-granularity vô hại); (4) consumer = whoever tái tạo số DCF
  cho report/dashboard, gọi `run_gate()` trước rồi chỉ recompute fair value khi `refresh=True` —
  reference tool, KHÔNG deadline pipeline hàng ngày. **Fail-safe:** mọi lỗi → `refresh=True` (recompute
  thay vì phục vụ stale trên gate hỏng). Ngày 11 > ngày 3 deposit; cùng phút 08:10 nhưng khác ngày →
  không trùng thực thi. First-run/no-state → REFRESH init. Selfcheck `dcf_refresh_gate_selfcheck.py`
  24/24 PASS. Đi kèm Việc A cùng job: default terminal-growth DISPLAY của `dcf_valuation.py` đổi
  CPI→`cap_rf` (level fix, không alpha — DCF non-decisional trong prod).
- 2026-07-17 (Winston, job `Winston_20260717_072420`, **user approved trực tiếp**): thêm 1 dòng cron
  `10 1 3 * *` (08:10 ICT ngày 3 hàng tháng) gọi `refresh_deposit_rate_vn.sh` — Layer A của
  `proposal_deposit_rate_monthly_refresh_20260713.md`. Script chỉ NHẮC (best-effort fetch CafeF/VCB
  timeout 15s hay fail, KHÔNG tự ghi) + post Discord + status bus; con người xác nhận số rồi chạy
  `append_deposit_rate.py` append vào `data/deposit_rate_vn_events.csv` (append-only, chỉ mốc
  effective_date > 2026-06-01 mới có hiệu lực). 4 câu hỏi §11: (1) đọc web external best-effort
  (CafeF/VCB, có thể fail) + `current_deposit_rate()` — **KHÔNG BQ/cache**; (2) nguồn Big-4 posted
  rate đổi bất thường, thường đầu tháng → chạy ngày 3 hợp lý, không cần T thật trong ngày; (3)
  KHÔNG cần T chính xác (tilt tần suất tháng, sai vài ngày vô hại); (4) consumer = `rating_8l.py`
  NEUTRAL tilt LIVE (đọc bất kỳ lúc nào có, không deadline cứng) + `dcf_refresh_gate.py` (dùng
  quanh ngày 11 → ngày 3 nằm trước). Không trùng phút với cron nào (08:00 commodity ngày 5/10 khác
  phút+ngày; 08:15 vcb_fx T2-T6). Freshness WARN >45 ngày ở `ops_health_check.sh` §8.
- 2026-07-15 (Winston, job `Winston_20260715_061920`, user duyệt dispatch): đổi giờ 3 cron đọc `dt5g_live` để luôn đọc regime HÔM NAY thay vì hôm qua (fix M3 audit `Winston_20260712_142100`): (1) `eod_trading_report.sh` 15:00→19:10 ICT (`0 8` → `10 12` UTC); (2) `pt_8l_daily.sh` 17:45→19:20 ICT (`45 10` → `20 12` UTC); (3) `telegram_run_daily.sh` 18:00→19:35 ICT (`0 11` → `35 12` UTC). Buffer sau publish DT5G ~19:01: eod 9', pt_8l 19', telegram 34'. Không trùng phút với nhau hoặc với bq_freshness 19:00. sector_lens_monitor.py step [9] vẫn đọc cache T-1 — user xác nhận KHÔNG CẦN SỬA, known limitation, chỉ ảnh hưởng công cụ nghiên cứu nội bộ, không chạm trading production.
- 2026-07-14 (Winston, job `Winston_20260714_160739`, **user directive trực tiếp — quy tắc vĩnh
  viễn mỗi quý**): thay 2 dòng T3 tạm thời (hết hạn 08-04) bằng **1 dòng cron DAILY 20:00 ICT**
  gọi `mike/bin/fa_ratings_earnings_window_daily.sh` — wrapper tự gate: chỉ chạy thật khi
  **tháng ∈ {1,4,7,10} ∧ ngày ≥ 15 ∧ T2-T6 ∧ không lễ VN** (công thức: cửa sổ = từ 15 của tháng
  đầu quý đến hết tháng đó; điều kiện "ngày ≥ 15" là đủ vì date hợp lệ không vượt số ngày thật
  của tháng — không cần bảng số-ngày-từng-tháng/năm nhuận; lễ VN = `vn_market.is_holiday`
  fixed-list, lễ biến động Tết ÂL chưa encode → best-effort, ngày Tết chạy thừa vô hại).
  Trong cửa sổ: `refresh_fa_ratings_8l.sh` 20:00 → `refresh_fa_ratings.sh` 20:45 (spacing 45'
  giữ nguyên mẫu Sat/T3-tạm). Ngoài cửa sổ: no-op im lặng (log skip-reason). Dòng Sat 08:30/09:15
  GIỮ NGUYÊN (baseline quanh năm, gate loại weekend nên không trùng). Cửa sổ đầu tiên:
  **2026-07-15 → 2026-07-31**. Gate test 18 ca mô phỏng PASS (07-14 F/07-15 T/07-31 T/08-01 F/
  08-03 F/04-30 lễ F/05-15 F/10-15 T/10-31 Sat F/01-15 T/…) qua `--check YYYY-MM-DD`.
  4 câu hỏi §11: (1) đọc `ticker_financial` BQ live qua 2 wrapper con đã source `wc_env.sh`
  (identity fix `a9716f6`), ghi BQ `fa_ratings_8l`+`fa_ratings`; (2) nguồn tươi same-day ~17:30
  ICT → 20:00 bắt được filings trong ngày; (3) cần T same-day trong mùa cao điểm BCTC; (4)
  consumer = custom30 builder/DC-book/golive sizing/as-of joins, deadline = rebalance quý +
  cohort đầy dần từng ngày; trước sync cache 23:45 nên cache vớt bản mới ngay đêm đó.
- 2026-07-13 (Winston, job `Winston_20260713_103213`, user approved): thêm 2 dòng cron **TẠM THỜI
  mùa BCTC Q2** — refresh `fa_ratings_8l` (T3 20:00 ICT) + `fa_ratings` (T3 20:45 ICT), guard
  `[ $(date +%Y%m%d) -le 20260804 ]` ngay trong dòng cron → **tự no-op sau 2026-08-04**, xoá dòng
  chết khi tiện. Lịch chạy: 07-14, 07-21, 07-28, 08-04 — lần cuối đúng tối trước rebalance quý
  ~08-05 (đóng điểm nóng audit `Winston_20260713_100733` q6: mã công bố 08-02..08-04 sẽ kịp có Q2
  rating tại rebalance). 4 câu hỏi: (1) đọc `ticker_financial` BQ live, ghi BQ qua wrapper đã
  source `wc_env.sh` (identity fix `a9716f6`); (2) nguồn tươi same-day ~17:30 ICT → 20:00 bắt được
  filings trong ngày (hơn hẳn 08:30 sáng); (3) cần T same-day trong mùa cao điểm; (4) consumer =
  custom30 builder/DC-book/as-of joins, deadline rebalance ~08-05 15:30. Slot 20:00 trống (giữ chỗ
  cũ), tránh hẳn khung giao dịch sáng, trước sync cache 23:45 → cache (giờ full_only, cùng commit)
  vớt bản mới ngay đêm đó. Kèm cùng commit: `sync_bq_cache.py` chuyển `fa_ratings`/`fa_ratings_8l`
  sang `full_only` (delta-append không tương thích refresh DELETE+INSERT/re-rank — hết alert
  count-mismatch giả mỗi thứ Bảy).
- 2026-07-13: thêm second-chance 23:00 cho `send_plan_report.sh` (sự cố kb/INCIDENTS.md 2026-07-13
  root-cause 1: plan sửa/re-dispatch sau 21:00 không bao giờ được gửi lại duyệt). Script đã hỗ trợ
  `--second-chance`/`--dry-run` + marker idempotent `state/plan_report_sent/` (Winston, job
  `Winston_20260713_014816`). 4 câu hỏi §11: (1) đọc file plan local + marker, không BQ/cache;
  (2) plan tươi sau pipeline 19:00, re-dispatch muộn đo thật 22:17 (07-13); (3) cần bản mới nhất
  trên đĩa lúc chạy; (4) consumer = user duyệt qua đêm, deadline preflight 08:45. Dòng cron đề xuất
  (CHƯA cài, chờ Mike): `0 16 * * 1-5 /home/trido/thanhdt/WorkingClaude/mike/bin/for_each_live_account.sh /home/trido/thanhdt/WorkingClaude/mike/bin/send_plan_report.sh --second-chance >> /home/trido/thanhdt/WorkingClaude/mike/logs/send_plan_report.log 2>&1   # 23:00 ICT — second-chance gui lai plan T+1 bi sua sau 21:00 (idempotent, su co 2026-07-13)`
- 2026-07-12: seed v1 từ audit `Winston_20260712_142100` + `Winston_20260712_151206`. Xoá 1 dòng
  crontab dangling comment (`# V2.4 go-live flip`). Fix C1 (publish DT5G đọc live, commit `4995262`,
  quant-skeptic CONFIRMED). Fix H2 (shares_outstanding_live BLOCK→WARN, commit `6459b6d`). Điều tra
  `lag_edge_health.csv` "staleness" → kết luận KHÔNG phải bug (job `Taylor_20260712_155038`, xem
  `kb/current_ops.md`).
