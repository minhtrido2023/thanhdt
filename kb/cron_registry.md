---
kind: registry-main
title: Cron Registry — mọi job crontab, theo thứ tự thời gian ICT
owner: Winston (data-ops)
format: OKF (markdown + YAML frontmatter); bảng chính CỐ Ý giữ 1 khối liền mạch (xem note dưới)
reference_dir: cron_registry/  # policy 4-câu-hỏi + step-detail papertrade + CHANGELOG tách ra đó
enforced_by: kb/coding_guidelines.md §11
---

# Cron Registry — mọi job crontab, theo thứ tự thời gian ICT

> Nguồn seed v1: audit `mike/agents/Winston/audit_cron_order_20260712.md` +
> `mike/agents/Winston/audit_paper_cron_cleanup_20260712.md` (2026-07-12). **Cập nhật file này CÙNG
> COMMIT** với mọi thay đổi crontab (thêm/xoá/đổi giờ một dòng) — quy tắc thêm cron mới ở
> [`cron_registry/_adding-cron-policy.md`](cron_registry/_adding-cron-policy.md).
> Giờ = ICT (UTC+7). Cột "Đọc" ghi rõ vintage (live/T-1/T-2...) — cache `BQ_LOCAL_CACHE` luôn = T-1,
> sync 23:45 T2-T6, KHÔNG sync cuối tuần.

> 📎 **Phần tham chiếu tách ra [`cron_registry/`](cron_registry/)** (2026-07-28, OKF): quy tắc thêm
> cron mới (4 câu hỏi §11) → [`cron_registry/_adding-cron-policy.md`](cron_registry/_adding-cron-policy.md);
> chi tiết step `papertrade_daily.sh` → [`cron_registry/papertrade_daily_steps.md`](cron_registry/papertrade_daily_steps.md);
> Log thay đổi → [`cron_registry/CHANGELOG.md`](cron_registry/CHANGELOG.md). **BẢNG CHÍNH DƯỚI ĐÂY
> KHÔNG tách** — giữ 1 khối liền mạch vì giá trị cốt lõi là thấy buffer/phụ thuộc GIỮA các dòng liền
> kề (chống vintage-mismatch kiểu C1 2026-07-12).

## Bảng chính

| Giờ ICT | Script | Đọc (nguồn + vintage) | Ghi | Consumer | Buffer/depends-on | Verify-artifact |
|---|---|---|---|---|---|---|
| 06:00 (T2-T6) | `newdeals_daily_report.py` | BQ live | Telegram/Discord watchlist | AlphaLens paper monitor (đến 09-30) | độc lập | — |
| 08:00 (ngày 5, 10) | `auto_update_commodity_wb.sh` | World Bank CMO (idempotent, 2 attempts) | `iron_ore/urea/dap_monthly.csv` | feed archive, chưa có consumer sống | độc lập | — |
| 08:10 (ngày 3) | `refresh_deposit_rate_vn.sh` | best-effort direct fetch (CafeF, timeout 15s, hay fail — **KHÔNG BQ**) — **CHỈ ĐỌC, KHÔNG dispatch agent** | Gửi notify.sh nhắc thủ công vào Trading Daily; **người thật** chạy `append_deposit_rate.py --source manual_verify` để ghi `data/deposit_rate_vn_events.csv` (auto-write bị loại bỏ 2026-07-20 sau 6 vòng adversarial review) | `rating_8l.py` NEUTRAL tilt (LIVE) + `dcf_refresh_gate.py` (ngày 11) | trước DCF refresh-gate ngày 11 | `data/refresh_deposit_rate_vn_YYYY-MM.log` |
| 08:10 (ngày 11) | `dcf_refresh_gate.py` | `deposit_rate_vn.current_deposit_rate()` (as-of, step series — **KHÔNG BQ/cache**) + prior `data/dcf_refresh_state.json` | `data/dcf_refresh_state.json` (atomic) + `data/dcf_refresh_gate.log` (append) | ai tái tạo số DCF cho report/dashboard: gọi `run_gate()`, chỉ recompute fair value khi `refresh=True` | SAU deposit-rate ngày 3 | `data/dcf_refresh_gate.log` |
| 08:15 (T2-T6) | `vcb_fx_feed.py` | VCB web | `vcb_fx_rate.csv` | feed archive | độc lập | — |
| 08:20 (T2-T6) | `ops_health_check.sh` "Trước phiên sáng" | trạng thái vận hành (plan conflict, journal error, circuit breaker, câu hỏi 48h) + **`anomaly_scan.py`** (BQ cache T-1: giá/KL mã đang giữ + watchlist 8L≤2) | Discord Trading Daily + **`data/anomaly_flags.json`** | user; **`golive_recommend_v23.py` (gate rổ CAPIT, cron 19:00 cùng ngày)** | trước preflight 08:45 | post message; cờ ghi trước khi CAPIT đọc tối cùng ngày |
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
| 15:05 (T2-T6) | `dc_book_waterfall_paper.py --update` | live BQ/DNSE | DC-book paper NAV | Paper Programs report 16:00 | trước 16:00 | idempotent theo data_date |
| 15:30 (T2-T6) | `papertrade_daily.sh` (23 step, chi tiết [cron_registry/papertrade_daily_steps.md](cron_registry/papertrade_daily_steps.md)) | cache T-1 (đa số step) + BQ live (vài step) | nhiều CSV/BQ table sim | **report 16:00 CÙNG NGÀY** (trước 2026-07-29 là "16:00 hôm sau" vì report chạy 15:20 = TRƯỚC chain), dashboards | runtime đo thật 8-12' (worst DONE 15:42) | continue-on-error + FAIL alert cuối chain |
| 16:00 (T2-T6) — **đổi từ 15:20 ngày 2026-07-29** (job `Winston_20260729_084600`) | `paper_programs_daily_report.sh --post` | file artifact do `papertrade_daily.sh` 15:30 sinh: `orb_pt_status.json` (vintage **T** — orb_pt.py kéo bar 1m VN30F LIVE từ vnstock), `pt_capitulation_state.json` + `papertrade_compare5.csv` (vintage **T-1** — sim/BQ chưa có close phiên T lúc 15:30) + registry | Discord Trading report | user | **sau 15:30 chain** (buffer 18' so worst 15:42); sau 15:05 dc_book | render registry; mỗi mục tự in `asof` = vintage thật |
| 19:20 (T2-T6) | `pt_8l_daily.sh` (9 step 8L production) | `rating_8l.py`+`cheap_pb_floor.py` đọc `dt5g_live` BQ live; step [9] `sector_lens_monitor.py` đọc **BQ_LOCAL_CACHE** (T-1, known limitation chấp nhận được — chỉ ảnh hưởng monitor nội bộ, không chạm trading production) | rating/screener/dna/alerts | user Telegram | sau publish DT5G ~19:01; sau eod_trading_report 10' | — |
| 19:35 (T2-T6) | `telegram_run_daily.sh` | `dt5g_live` BQ live; đọc sau `pt_8l_daily` để `rating_8l.csv` tươi cho cột R | Telegram BA-system report | user | sau pt_8l_daily 15' | — |
| 20:05 (T2-T6) — **CÀI MỚI 2026-07-29** (job `Winston_20260729_103816`) | `mike/bin/paper_late_feeds.sh` = 2 step TÁCH khỏi `papertrade_daily.sh` 15:30: `[19] crisis_alert_push` + `[21] fetch_bdi_daily` | **[19]** BQ **LIVE** (`ticker_prune` JOIN `dt5g_live`, qua `dna_report._bq` subprocess — KHÔNG qua cache) → asof=**T** ở 20:05 (ở 15:30 luôn T-1); **[21]** scrape handybulk.com (Baltic công bố ~13:00 London ≈ 19-20:00 ICT) | Telegram capitulation push (im lặng khi DORMANT) + `data/bdi_daily_real.csv` | user (crisis alert); `freight_map.py` (ad-hoc, không deadline) | **sau** ingest tav2 ~17:2x **và** publish DT5G 19:00-19:03; **trước** `send_plan_report` 21:00 (user thấy cảnh báo trước khi duyệt plan) | continue-on-error + FAIL alert Telegram+Discord như chain 15:30; `[21]` VẪN chạy song song ở 15:30 (script chỉ lấy ngày mới nhất trên trang → bỏ 1 phiên = mất vĩnh viễn; 2 lần/ngày + dedup `date` keep=last = idempotent, không thủng chuỗi) |
| 18:10 (T2-T6) | `fetch_new_listings_daily.sh` | web listings | queue nghiên cứu 8L | Winston | — | — |
| 18:30 (T2-T6) | `daily_refresh_v34b_linux.sh` (13 step) | ticker_prune BQ live (ingest xong ~17:30) | `vnindex_5state` (base) + `_v34b_clean` + `dt5g_live` (fix C1 07-12: publish đọc LIVE, không qua cache) | pt_8l/telegram hôm sau, bq_freshness 19:00, mọi consumer regime | ~90' worst-case + retry | step [13] mtime-assert |
| 18:35 (T2-T6) | `rubber_weekly.sh` | web feed | rubber alert | Winston | lệch 5' so 18:30 (tránh trùng CPU) | — |
| 18:40 (T2-T6) | `update_shares_live.sh --scan` | corp-action feed | detection-only alert (KHÔNG merge `updated_at` — chỉ MERGE khi xử lý tay) | Winston/Taylor | — | freshness check `shares_outstanding_live` hạ BLOCK→WARN (H2 fix, commit `6459b6d`, 2026-07-12) — cadence event-driven thật, không phải daily |
| 18:45 (T2-T6) — **CÀI MỚI 2026-07-29** (job `Taylor_20260729_104614`, WATCH-only shadow, xem `kb/current_ops.md` §Đang R&D + [research](../agents/Taylor/research/insider_transaction_scoping_20260729.md)) | `mike/agents/Taylor/insider_flags.py` | `tav2_bq.insider_transaction` BQ **LIVE** (bảng chưa có trong `bq_cache`) + `ticker_financial.OShares` as-of BQ live | `data/insider_flags.json` (atomic tmp+`os.replace`; merge chỉ giữ bản `last_alert` mới hơn) | **KHÔNG AI hiện tại** (shadow tích luỹ, chưa wire due-diligence — cần quant-skeptic trước khi wire); consumer tương lai = báo cáo due-diligence, chuỗi kết thúc ở `send_plan_report` 21:00 | sau `ticker_financial` ingest ~17:30; trước `bq_freshness_check` 19:00; T-1 là đủ (TTL cờ 90 ngày, không cần same-day) | `--selftest` 8/8 (khớp `exp_insider/panel2.csv`); cổng freshness: `MAX(public_date)` cũ >10 phiên (dự kiến trip ~2026-08-07 nếu bq_admin chưa fix cadence bug) → log WARN + `exit 3`, KHÔNG ghi (không đóng băng cờ cũ tạo cảm giác sạch giả) |
| 19:00 (T2-T6) | `bq_freshness_check.sh --quiet` (pipeline BQ freshness + DT5G/recommend + dispatch Bill) | BQ live (không cache) cho freshness; pipeline-1 `publish_gated_state` (fix C1); **pipeline-1b `build_universe_pit.py --date $TODAY`** (đọc `tav2_bq.ticker` LIVE, vintage T; ghi `tav2_mike.universe_pit`); **pipeline-1c `build_universe_pit_quality.py --date $TODAY`** (ghi `tav2_mike.universe_pit_quality`) — cả 2 chạy SAU ticker FRESH BLOCK, TRƯỚC golive_recommend_v23 (wire 2026-07-22, Taylor_20260722_100814) | freshness log + universe_pit/quality + golive recommend + bus | 21:00 send_plan, DollarBill; golive_recommend_v23 (panel D1), custom_basket.py (custom30V), tương lai: CAPIT breadth P4 | sau 18:30 (30') | `MAX(time)` từng bảng; universe_pit/$TODAY count>0 sau build |
| 19:00 (daily) | `kb_nightly.sh` | events_buffer | trim/archive | — | — | — |
| 20:00 (DAILY, ♾️VĨNH VIỄN — chỉ chạy thật trong cửa sổ mùa BCTC) | `fa_ratings_earnings_window_daily.sh` — gate ngày ICT trong wrapper: **tháng ∈ {1,4,7,10} ∧ ngày ≥ 15 ∧ weekday T2-T6 ∧ không lễ VN** (`trading_bot.vn_market.is_holiday`, fixed-list; lễ biến động như Tết ÂL CHƯA encode — best-effort, đã ghi trong comment script). Không cần check "≤ ngày cuối tháng": date hợp lệ không vượt quá số ngày thật của tháng, cửa sổ tự đóng khi sang tháng vì điều kiện tháng fail. Đúng gate → chạy `refresh_fa_ratings_8l.sh` rồi `refresh_fa_ratings.sh` sau đúng 45' (giữ spacing mẫu Sat); sai gate → no-op, log 1 dòng skip-reason, không alert | `ticker_financial` BQ live (đọc-ghi, ingest same-day ~17:30 → bắt filings trong ngày) | `tav2_bq.fa_ratings_8l` (20:00) + `tav2_bq.fa_ratings` (20:45) | như 2 dòng Sat; mùa BCTC cohort ngày đầu chưa đầy đủ → cần re-rate mỗi ngày để bắt kịp mã mới báo cáo (user directive 2026-07-14) | sau ingest 17:30 + daily_refresh 18:30 + pipeline 19:00; trước sync cache 23:45 (cache full_only vớt ngay đêm đó) | `bq show` lastModified+numRows; 2 wrapper con tự alert nếu fail; gate test 18 ca (`--check YYYY-MM-DD`) |
| 20:30 (T2-T6) — **ĐÃ CÀI 2026-07-24** (quant-skeptic CONFIRMED `Taylor_20260724_024201` + hardening `Taylor_20260724_030732` [dry-run đường DNSE thật phát hiện+fix bug đọc nhầm `account_no`→`account_id`; thêm session guard chặn giữa phiên] + user duyệt trực tiếp) | `inject_discretionary_orders.sh` (`live_dnse_labels()` loop → `discretionary_accumulation_inject.py`) | state `data/trade_plans/discretionary/state_*_<acct>.json` (active) + **broker positions LIVE (filled thật) + DNSE quote LIVE (giá/KL phiên gần nhất — KHÔNG BQ, same-day §6)** | chèn order `book=DISCRETIONARY_SPECIAL` vào `plan_<acct>_<T+1>.json` (atomic) + cập nhật ledger state | Mafee (plan-bound, sau khi user duyệt plan) | **SAU** DollarBill ghi plan (dispatch --bg ~19:0x); **TRƯỚC** send_plan_report 21:00 (để user duyệt plan đã có lệnh gom) | idempotent: dedup order-id + ticker/book + ledger plan_date; fail-safe thiếu broker/giá/KL → no-op; guard tự chối chạy giữa phiên (chỉ chạy khi `vn_market.session_phase()` = PRE/CLOSED — `day_volume` phải là phiên đã chốt cho đúng logic opportunistic); `hard_expiry` (kiểm toán/đình chỉ GD) vẫn cần người set tay trong state, không tự động được |
| 21:00 (T2-T6) | `send_plan_report.sh` (`for_each_live_account.sh`) | file plan `plan_<acct>_<T+1 date>.json` | Discord DollarBill plan channel + marker `mike/state/plan_report_sent/<acct>_<date>.json` (md5 nội dung, loại field approval) | user (duyệt qua đêm) | sau 19:00 (2h) | verify `plan_date`=next_trading_day + field `orders` |
| 23:00 (T2-T6) — ĐÃ CÀI 2026-07-13 (commit `4216295`, quant-skeptic CONFIRMED) | `send_plan_report.sh --second-chance` (`for_each_live_account.sh`) | file plan (bản mới nhất trên đĩa lúc 23:00) + marker 21:00 | gửi lại plan cho user NẾU: 21:00 fail mà giờ file đúng, HOẶC plan đổi nội dung sau khi gửi; NO-OP nếu đã gửi + không đổi | user (duyệt qua đêm — sự cố 07-13: plan fix 22:17 không ai gửi lại) | sau khung re-dispatch tối (~22:1x đo thật), trước sync 23:45 (45') | idempotent qua marker md5; escalate lần 2 nếu vẫn thiếu/sai |
| 23:45 (T2-T6) | `sync_bq_cache_daily.sh` | BQ live | `data/bq_cache/*` (DuckDB parquet) | mọi script source `wc_env.sh` + `BQ_LOCAL_CACHE` (papertrade, sims, backtest) | sau daily_refresh (~5h dư) | preflight_bq_cache.py 12 bảng (thiếu `custom30_8l` — L6b, chưa fix) |
| 00:00 (daily) | `fleet_backup.sh` | git repo | GitHub `mike-fleet` branch | DR | sau sync 23:45 (~15') | — |
| 00:30 (daily) | `daily_retro.sh` | events hôm qua trọn vẹn | retro report + Wags verify | user | sau backup (00:00) | — |
| 02:00 (daily) | `kb_nightly.sh` | events_buffer | trim/archive KB | — | — | — |
| Friday 08:10 (thêm 2026-07-23) | `fearbuy_weekly_scan.sh` | `anomaly_scan.py` (BQ cache T-1) + WebSearch tin khởi tố/bắt lãnh đạo DN niêm yết 7-14 ngày | dispatch Taylor → bus finding + `calculated_fear_state_backstop.md` (nếu case mới) → Discord Taylor thread `1521735922066919515` | user (recon, không tự mua) | trước `ops_health_check.sh` 08:20 (10') | bus finding phải luôn có (kể cả "0 case mới" — quy tắc quiet-heartbeat, không im lặng) |
| Friday 15:00 | `check_sbv_weekly.sh` | SBV web | `sbv_macro_overlay` | DT5G Pillar A | — | — |
| Mon 09:00 | `hog_price_feed.py` | web | feed archive | chưa consumer sống | — | — |
| Sat 09:15 | `refresh_fa_ratings.sh` | `ticker_financial` BQ live (append-only) | `tav2_bq.fa_ratings` | custom30 builder cũ, audit | sau fa_ratings_8l (45') | `bq show` lastModified+numRows, invariant quý đóng băng |
| mỗi giờ :07 | `consolidate.sh` | bus | KB | — | — | — |
| mỗi 10' | `watchdog.sh`, `discover_sessions.py`, `resume_pending.py` | — | — | — | — | — |
| @reboot + mỗi 5' | `discord_bot/start.sh` | — | supervisor | — | — | — |

---

> **Bảng chính kết thúc ở đây.** Các phần đã tách sang [`cron_registry/`](cron_registry/):
> - Quy tắc thêm/sửa cron (4 câu hỏi §11 + chống xung đột + buffer + ghi ở đâu) → [`cron_registry/_adding-cron-policy.md`](cron_registry/_adding-cron-policy.md)
> - Chi tiết step `papertrade_daily.sh` (15:30) → [`cron_registry/papertrade_daily_steps.md`](cron_registry/papertrade_daily_steps.md)
> - Log thay đổi lịch cron → [`cron_registry/CHANGELOG.md`](cron_registry/CHANGELOG.md)
