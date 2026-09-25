---
kind: reference
title: Production manifest ARIA — tự sinh, ĐỪNG sửa tay
generated_by: python3 mike/bin/production_manifest.py
generated_at: 2026-09-25T20:52:52Z
---

# Production manifest (auto-generated — sửa `mike/bin/production_manifest.py`, không sửa file này)

Tái sinh: `cd /home/trido/thanhdt/WorkingClaude && python3 mike/bin/production_manifest.py` · Kiểm drift: `bash mike/bin/production_manifest_selfcheck.sh` (lệch bản commit = FAIL).

**471 file** — T0 money-path **119** · T1 dữ liệu/regime/paper **106** · T2 fleet-ops **72** · T3 selfcheck **174** · gốc: 103 (systemd: unavailable).

Phương pháp: gốc = `crontab -l` + systemd user units + hook `.claude/settings*.json`; đóng bao AST import + tham chiếu exec `*.py|*.sh` resolve ra file có thật, lặp tới điểm bất động. Tầng = nhỏ nhất theo các gốc với tới, KHÔNG đi xuyên entry script của gốc khác (và dispatch.sh với gốc ngoài T2) — tầng blast radius thuần nằm ở `blast_tier` trong JSON. T3 = selfcheck ngoài bao đóng import/exec trực tiếp file T0–T2. Loại trừ: mike_paseo/, wt-*/ (mọi worktree), .claude/worktrees/, venv/__pycache__/node_modules.

**Giới hạn (không thấy được cơ học):** script do agent tự chọn khi được dispatch, kể cả script được NÊU TÊN trong prompt gửi agent (vd kb_nightly.sh bảo agent chạy data_registry_audit.sh, daily_retro.sh bảo chạy wakeup_audit.py); lệnh nằm trong chuỗi có khoảng trắng không phải `bash -c`/`python3 -c`; đường dẫn ghép từ biến runtime; `importlib.import_module`; import trong hàm tự-kiểm nội tuyến (`def _selfcheck`) CỐ Ý bỏ; file chưa track git CỐ Ý bỏ (liệt kê ở `untracked_refs` trong JSON); file config/dữ liệu (.json). Cạnh `ref` = đường dẫn trong mảng bash.

**Chủ sở hữu + nhịp:** Wags. Lệch = FAIL của `production_manifest_selfcheck.sh` trong `run_selfchecks.sh` ⇒ `weekly_ops_audit.sh` thấy MỖI TUẦN (bộ dò đỏ hằng ngày chỉ báo 1 lần/file vì `known_red`). Thay đổi cố ý (thêm/đổi cron, import mới) ⇒ tái sinh + commit cùng lúc. File không có ở đây KHÔNG chắc chắn là research — manifest là cận dưới của production.

| path | tầng | depth | cách vào | gốc quyết định tầng (+ số gốc khác) |
|---|---|---|---|---|
| `alt_valuation_lens.py` | T0 | 2 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+18) |
| `anomaly_gate.py` | T0 | 1 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+2) |
| `bot_execute.py` | T0 | 0 | exec | cron `10 2 * * 1,3,5` bot_execute.py (+2) |
| `bq_local_cache.py` | T0 | 2 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+28) |
| `bull_div_boost.py` | T0 | 3 | import | cron `10 2 * * 1,3,5` bot_execute.py (+12) |
| `capit_episode.py` | T0 | 2 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+13) |
| `corp_action_lib.py` | T0 | 1 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+39) |
| `cpi_vn.py` | T0 | 2 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+20) |
| `custom30.py` | T0 | 2 | import | cron `0 12 * * 1-5` bq_freshness_check.sh |
| `dcf_valuation.py` | T0 | 1 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+20) |
| `deploy_golive_dt5g_v4/golive_recommend_v23.py` | T0 | 1 | exec | cron `0 12 * * 1-5` bq_freshness_check.sh |
| `deploy_golive_dt5g_v4/publish_gated_state.py` | T0 | 1 | exec | cron `0 12 * * 1-5` bq_freshness_check.sh (+2) |
| `deposit_rate_vn.py` | T0 | 1 | exec | cron `0 12 * * 1-5` bq_freshness_check.sh (+24) |
| `dna_report.py` | T0 | 1 | import | cron `0 14 * * 1-5` send_plan_report.sh (+3) |
| `dnse_api.py` | T0 | 2 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+33) |
| `dt5g_freshness.py` | T0 | 1 | exec | cron `10 12 * * 1-5` eod_trading_report.sh (+1) |
| `fetch_dnse_khoplenh_email.py` | T0 | 2 | exec | cron `10 12 * * 1-5` eod_trading_report.sh |
| `gdp_growth_vn.py` | T0 | 2 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+20) |
| `gmail_otp_reader.py` | T0 | 1 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+32) |
| `lag_forensic_filter.py` | T0 | 2 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+16) |
| `lag_liq_ledger.py` | T0 | 1 | exec | cron `0 12 * * 1-5` bq_freshness_check.sh |
| `lag_liquidity_filter.py` | T0 | 2 | import | cron `0 12 * * 1-5` bq_freshness_check.sh |
| `lag_live_schedule.py` | T0 | 2 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+2) |
| `lag_rating_filter.py` | T0 | 2 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+16) |
| `macro_state_live.py` | T0 | 2 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+4) |
| `mike/agents/Mafee/push_recommend_v23_to_bq.py` | T0 | 1 | exec | cron `0 12 * * 1-5` bq_freshness_check.sh |
| `mike/bin/append_event.sh` | T0 | 1 | exec | cron `0 12 * * 1-5` bq_freshness_check.sh (+50) |
| `mike/bin/bot_heartbeat.sh` | T0 | 0 | exec | cron `*/5 2-7 * * 1-5` bot_heartbeat.sh |
| `mike/bin/bq_freshness_check.sh` | T0 | 0 | exec | cron `0 12 * * 1-5` bq_freshness_check.sh |
| `mike/bin/broker_fill_confirm.py` | T0 | 1 | import | cron `10 12 * * 1-5` eod_trading_report.sh |
| `mike/bin/build_universe_pit.py` | T0 | 1 | exec | cron `0 12 * * 1-5` bq_freshness_check.sh |
| `mike/bin/build_universe_pit_quality.py` | T0 | 1 | exec | cron `0 12 * * 1-5` bq_freshness_check.sh |
| `mike/bin/bus_question_audit.py` | T0 | 1 | exec | cron `30 1 * * *` check_report_cadence.sh (+11) |
| `mike/bin/check_report_cadence.sh` | T0 | 0 | exec | cron `30 1 * * *` check_report_cadence.sh (+2) |
| `mike/bin/compute_active_nav.py` | T0 | 1 | exec | cron `15 13 * * 1-5` compute_active_nav_all.sh (+3) |
| `mike/bin/compute_active_nav_all.sh` | T0 | 0 | exec | cron `15 13 * * 1-5` compute_active_nav_all.sh |
| `mike/bin/compute_jit_unpark.py` | T0 | 1 | exec | cron `40 12 * * 1-5` jit_unpark_daily.sh (+1) |
| `mike/bin/compute_park_trim.py` | T0 | 1 | exec | cron `30 12 * * 1-5` park_trim_daily.sh (+2) |
| `mike/bin/corp_action_auto_confirm.py` | T0 | 0 | exec | cron `25 12 * * 1-5` corp_action_auto_confirm.py |
| `mike/bin/corp_action_daily.py` | T0 | 1 | exec | cron `0 12 * * 1-5` bq_freshness_check.sh (+24) |
| `mike/bin/corp_action_daily_selfcheck.py` | T0 | 2 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+24) |
| `mike/bin/corp_actions.py` | T0 | 1 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+24) |
| `mike/bin/daily_nav_snapshot.py` | T0 | 1 | exec | cron `0 12 * * 1-5` bq_freshness_check.sh (+24) |
| `mike/bin/discord_channel.sh` | T0 | 1 | exec | cron `0 12 * * 1-5` bq_freshness_check.sh (+63) |
| `mike/bin/discord_channels.py` | T0 | 1 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+24) |
| `mike/bin/discretionary_accumulation_inject.py` | T0 | 1 | exec | cron `30 13 * * 1-5` inject_discretionary_orders.sh |
| `mike/bin/discretionary_margin_check_exits_daily.sh` | T0 | 0 | exec | cron `20 8 * * 1-5` discretionary_margin_check_exits_daily.sh |
| `mike/bin/discretionary_margin_gate.py` | T0 | 1 | exec | cron `20 8 * * 1-5` discretionary_margin_check_exits_daily.sh (+3) |
| `mike/bin/dispatch.sh` | T0 | 1 | exec | cron `0 12 * * 1-5` bq_freshness_check.sh (+19) |
| `mike/bin/dividend_adjusted_return.py` | T0 | 2 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+24) |
| `mike/bin/dnse_fee_rates.py` | T0 | 1 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+1) |
| `mike/bin/dt5g_writer_watch.py` | T0 | 1 | exec | cron `0 12 * * 1-5` bq_freshness_check.sh (+1) |
| `mike/bin/eod_trading_report.sh` | T0 | 0 | exec | cron `10 12 * * 1-5` eod_trading_report.sh |
| `mike/bin/exdate_frame.py` | T0 | 2 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+24) |
| `mike/bin/extreme_regime_dd_alert.sh` | T0 | 1 | exec | cron `5 2 * * 1-5` run_bot.sh (+1) |
| `mike/bin/for_each_live_account.sh` | T0 | 0 | exec | cron `0 14 * * 1-5` send_plan_report.sh (+5) |
| `mike/bin/incident_lookup.py` | T0 | 2 | exec | cron `5 2 * * 1-5` run_bot.sh (+6) |
| `mike/bin/inject_discretionary_orders.sh` | T0 | 0 | exec | cron `30 13 * * 1-5` inject_discretionary_orders.sh |
| `mike/bin/jit_unpark_daily.sh` | T0 | 0 | exec | cron `40 12 * * 1-5` jit_unpark_daily.sh |
| `mike/bin/json_payload_diag.py` | T0 | 2 | exec | cron `0 12 * * 1-5` bq_freshness_check.sh (+50) |
| `mike/bin/late_plan_catchup.sh` | T0 | 0 | exec | cron `45 14 * * 1-5` late_plan_catchup.sh (+2) |
| `mike/bin/merge_park_daily.sh` | T0 | 0 | exec | cron `20 13 * * 1-5` merge_park_daily.sh |
| `mike/bin/merge_park_orders.py` | T0 | 1 | exec | cron `20 13 * * 1-5` merge_park_daily.sh |
| `mike/bin/mike_json.py` | T0 | 1 | exec | cron `0 12 * * 1-5` bq_freshness_check.sh (+53) |
| `mike/bin/nav_exdate_forecast.py` | T0 | 1 | exec | cron `0 12 * * 1-5` bq_freshness_check.sh |
| `mike/bin/nav_period_returns.py` | T0 | 2 | exec | cron `10 12 * * 1-5` eod_trading_report.sh (+5) |
| `mike/bin/nav_snapshot_daily.sh` | T0 | 0 | exec | cron `50 12 * * 1-5` nav_snapshot_daily.sh |
| `mike/bin/nav_sync_retry.sh` | T0 | 0 | exec | cron `*/15 12-14 * * 1-5` nav_sync_retry.sh |
| `mike/bin/notify.sh` | T0 | 1 | exec | cron `0 12 * * 1-5` bq_freshness_check.sh (+44) |
| `mike/bin/notify_discord.sh` | T0 | 1 | exec | cron `0 12 * * 1-5` bq_freshness_check.sh (+44) |
| `mike/bin/notify_thread.sh` | T0 | 1 | exec | cron `0 12 * * 1-5` bq_freshness_check.sh (+58) |
| `mike/bin/ops_autofix.sh` | T0 | 1 | exec | cron `5 2 * * 1-5` run_bot.sh (+6) |
| `mike/bin/park_holdings.py` | T0 | 2 | import | cron `15 13 * * 1-5` compute_active_nav_all.sh (+3) |
| `mike/bin/park_trim_daily.sh` | T0 | 0 | exec | cron `30 12 * * 1-5` park_trim_daily.sh |
| `mike/bin/plan_approval_reminder.sh` | T0 | 0 | exec | cron `50 1 * * 1-5` plan_approval_reminder.sh |
| `mike/bin/preflight_check.sh` | T0 | 0 | exec | cron `45 1 * * 1-5` preflight_check.sh |
| `mike/bin/render_report_html.py` | T0 | 2 | import | cron `5 2 * * 1-5` run_bot.sh (+10) |
| `mike/bin/report_delivery_gate.py` | T0 | 1 | exec | cron `10 12 * * 1-5` eod_trading_report.sh (+5) |
| `mike/bin/report_return_gate.py` | T0 | 1 | import | cron `5 2 * * 1-5` run_bot.sh (+11) |
| `mike/bin/run_bot.sh` | T0 | 0 | exec | cron `5 2 * * 1-5` run_bot.sh (+1) |
| `mike/bin/send_plan_report.sh` | T0 | 0 | exec | cron `0 14 * * 1-5` send_plan_report.sh (+1) |
| `mike/bin/send_report_email.py` | T0 | 1 | exec | cron `5 2 * * 1-5` run_bot.sh (+10) |
| `mike/bin/session_announce.sh` | T0 | 0 | exec | cron `31 4 * * 1-5` session_announce.sh (+2) |
| `mike/bin/signal_holds.py` | T0 | 1 | exec | cron `0 12 * * 1-5` bq_freshness_check.sh (+16) |
| `mike/bin/vendor_mismatch_alert.sh` | T0 | 1 | exec | cron `10 12 * * 1-5` eod_trading_report.sh (+3) |
| `mike/bin/verify_account_snapshot.py` | T0 | 2 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+24) |
| `mike/bin/wc_paths.py` | T0 | 1 | exec | cron `0 12 * * 1-5` bq_freshness_check.sh (+27) |
| `moat_5f.py` | T0 | 2 | import | cron `0 14 * * 1-5` send_plan_report.sh (+4) |
| `oshares_live.py` | T0 | 1 | exec | cron `0 12 * * 1-5` bq_freshness_check.sh (+25) |
| `oshares_pit.py` | T0 | 2 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+25) |
| `oshares_selfcheck_fixture.py` | T0 | 2 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+25) |
| `paper_entry_adjust.py` | T0 | 2 | import | cron `5 2 * * 1-5` run_bot.sh (+11) |
| `paper_entry_corpaction_crosscheck.py` | T0 | 2 | import | cron `5 2 * * 1-5` run_bot.sh (+11) |
| `phs_flash_api.py` | T0 | 2 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+32) |
| `phs_flex_api.py` | T0 | 2 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+32) |
| `recommend_holistic.py` | T0 | 2 | import | cron `10 2 * * 1,3,5` bot_execute.py (+12) |
| `sbv_macro_overlay.py` | T0 | 1 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+14) |
| `signal_v11_sql.py` | T0 | 2 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+2) |
| `simulate_holistic_nav.py` | T0 | 2 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+20) |
| `state_publish_immutable.py` | T0 | 1 | exec | cron `0 12 * * 1-5` bq_freshness_check.sh (+3) |
| `telegram_recommend.py` | T0 | 1 | exec | cron `10 2 * * 1,3,5` bot_execute.py (+12) |
| `trading_bot/__init__.py` | T0 | 1 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+55) |
| `trading_bot/brokers.py` | T0 | 1 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+32) |
| `trading_bot/config.py` | T0 | 1 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+52) |
| `trading_bot/discretionary_accumulation.py` | T0 | 2 | import | cron `30 13 * * 1-5` inject_discretionary_orders.sh |
| `trading_bot/due_diligence.py` | T0 | 1 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+18) |
| `trading_bot/exdate_gate.py` | T0 | 1 | import | cron `10 2 * * 1,3,5` bot_execute.py (+2) |
| `trading_bot/executor.py` | T0 | 1 | import | cron `10 2 * * 1,3,5` bot_execute.py (+4) |
| `trading_bot/gdkhq_rollout.py` | T0 | 1 | import | cron `10 2 * * 1,3,5` bot_execute.py (+2) |
| `trading_bot/netting_recon.py` | T0 | 1 | import | cron `10 2 * * 1,3,5` bot_execute.py (+2) |
| `trading_bot/no_chase_ceiling.py` | T0 | 2 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+19) |
| `trading_bot/plan.py` | T0 | 1 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+16) |
| `trading_bot/plan_cash_commitment.py` | T0 | 2 | import | cron `30 13 * * 1-5` inject_discretionary_orders.sh |
| `trading_bot/plan_funding_gate.py` | T0 | 1 | import | cron `30 13 * * 1-5` inject_discretionary_orders.sh (+5) |
| `trading_bot/price_frame.py` | T0 | 1 | import | cron `10 2 * * 1,3,5` bot_execute.py (+5) |
| `trading_bot/strategies.py` | T0 | 1 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+18) |
| `trading_bot/vn_market.py` | T0 | 1 | import | cron `0 12 * * 1-5` bq_freshness_check.sh (+47) |
| `value_radar.py` | T0 | 2 | import | cron `0 14 * * 1-5` send_plan_report.sh (+3) |
| `wc_env.sh` | T0 | 0 | exec | cron `0 12 * * 1-5` bq_freshness_check.sh (+61) |
| `alphalens_report.py` | T1 | 1 | import | cron `0 23 * * 0-4` newdeals_daily_report.py |
| `assert_chain_outputs.sh` | T1 | 1 | exec | cron `30 11 * * 1-5` daily_refresh_v34b_linux.sh |
| `auto_update_commodity_wb.py` | T1 | 1 | exec | cron `0 1 5 * *` auto_update_commodity_wb.sh (+1) |
| `auto_update_commodity_wb.sh` | T1 | 0 | exec | cron `0 1 5 * *` auto_update_commodity_wb.sh (+1) |
| `build_concentration_history.py` | T1 | 1 | exec | cron `30 11 * * 1-5` daily_refresh_v34b_linux.sh |
| `build_dt_4gate.py` | T1 | 1 | exec | cron `30 11 * * 1-5` daily_refresh_v34b_linux.sh |
| `c1_shadow_paper.py` | T1 | 0 | exec | cron `20 17 * * 1-5` c1_shadow_paper.py |
| `cheap_pb_floor.py` | T1 | 1 | exec | cron `20 12 * * 1-5` pt_8l_daily.sh |
| `converge_report.py` | T1 | 1 | import | cron `0 23 * * 0-4` newdeals_daily_report.py |
| `crisis_alert_push.py` | T1 | 1 | exec | cron `5 13 * * 1-5` paper_late_feeds.sh |
| `custom30_history.py` | T1 | 1 | exec | cron `30 8 * * 1-5` papertrade_daily.sh |
| `custom30_yield_labels.py` | T1 | 2 | import | cron `30 8 * * 1-5` papertrade_daily.sh |
| `custom_basket.py` | T1 | 2 | import | cron `30 8 * * 1-5` papertrade_daily.sh |
| `daily_refresh_v34b_linux.sh` | T1 | 0 | exec | cron `30 11 * * 1-5` daily_refresh_v34b_linux.sh |
| `dc_book_waterfall_paper.py` | T1 | 0 | exec | cron `15 17 * * 1-5` dc_book_waterfall_paper.py |
| `dcf_refresh_gate.py` | T1 | 0 | exec | cron `10 1 11 * *` dcf_refresh_gate.py |
| `deploy_v3_4b_package/build_v3_1_clean.py` | T1 | 1 | exec | cron `30 11 * * 1-5` daily_refresh_v34b_linux.sh |
| `deploy_v3_4b_package/build_v3_4_bull_aware.py` | T1 | 1 | exec | cron `30 11 * * 1-5` daily_refresh_v34b_linux.sh |
| `dna_card.py` | T1 | 1 | exec | cron `20 12 * * 1-5` pt_8l_daily.sh |
| `edge_health_monitor.py` | T1 | 1 | exec | cron `30 8 * * 1-5` papertrade_daily.sh |
| `fetch_bdi_daily.py` | T1 | 1 | exec | cron `30 8 * * 1-5` papertrade_daily.sh (+1) |
| `fetch_new_listings.py` | T1 | 1 | exec | cron `10 11 * * 1-5` fetch_new_listings_daily.sh |
| `fetch_new_listings_daily.sh` | T1 | 0 | exec | cron `10 11 * * 1-5` fetch_new_listings_daily.sh |
| `freight_map.py` | T1 | 2 | import | cron `20 12 * * 1-5` pt_8l_daily.sh |
| `fundamental_rating.py` | T1 | 2 | exec | cron `15 2 * * 6` refresh_fa_ratings.sh |
| `hit_details.py` | T1 | 1 | exec | cron `0 12 * * 1-5` hit_details_daily.sh |
| `hog_price_feed.py` | T1 | 0 | exec | cron `0 2 * * 1` hog_price_feed.py |
| `macro_healthcheck.py` | T1 | 1 | exec | cron `30 8 * * 1-5` papertrade_daily.sh (+2) |
| `mike/agents/Taylor/anomaly_scan.py` | T1 | 1 | exec | cron `10 1 * * 5` fearbuy_weekly_scan.sh (+3) |
| `mike/agents/Taylor/insider_flags.py` | T1 | 0 | exec | cron `45 11 * * 1-5` insider_flags.py |
| `mike/bin/bq_monthly_pin.py` | T1 | 1 | exec | cron `0 15 1 * *` bq_monthly_pin.sh |
| `mike/bin/bq_monthly_pin.sh` | T1 | 0 | exec | cron `0 15 1 * *` bq_monthly_pin.sh |
| `mike/bin/capture_upcom_vwap_eod.py` | T1 | 1 | exec | cron `15 8 * * 1-5` capture_upcom_vwap_eod.sh |
| `mike/bin/capture_upcom_vwap_eod.sh` | T1 | 0 | exec | cron `15 8 * * 1-5` capture_upcom_vwap_eod.sh |
| `mike/bin/check_sbv_weekly.sh` | T1 | 0 | exec | cron `0 8 * * 5` check_sbv_weekly.sh |
| `mike/bin/corp_action_daily.sh` | T1 | 0 | exec | cron `30 0 * * 1-5` corp_action_daily.sh |
| `mike/bin/corp_action_feed_canary.py` | T1 | 0 | exec | cron `5 0 * * 1-5` corp_action_feed_canary.py |
| `mike/bin/csv_fresh_today.sh` | T1 | 1 | exec | cron `35 12 * * 1-5` telegram_run_daily.sh (+1) |
| `mike/bin/custom30v_rebalance_watch.sh` | T1 | 0 | exec | cron `5 9 * * 1-5` custom30v_rebalance_watch.sh |
| `mike/bin/discretionary_candidate_funnel.py` | T1 | 1 | exec | cron `10 1 * * 5` fearbuy_weekly_scan.sh (+1) |
| `mike/bin/fa_ratings_earnings_window_daily.sh` | T1 | 0 | exec | cron `0 13 * * *` fa_ratings_earnings_window_daily.sh |
| `mike/bin/fearbuy_weekly_scan.sh` | T1 | 0 | exec | cron `10 1 * * 5` fearbuy_weekly_scan.sh (+1) |
| `mike/bin/fiinprox_harvest_tick.py` | T1 | 1 | exec | cron `7,27,47 * * * *` fiinprox_harvest_tick.sh |
| `mike/bin/fiinprox_harvest_tick.sh` | T1 | 0 | exec | cron `7,27,47 * * * *` fiinprox_harvest_tick.sh |
| `mike/bin/hit_details_daily.sh` | T1 | 0 | exec | cron `0 12 * * 1-5` hit_details_daily.sh |
| `mike/bin/marginability_check.py` | T1 | 2 | import | cron `10 1 * * 5` fearbuy_weekly_scan.sh (+1) |
| `mike/bin/opening_window_l2_poll.py` | T1 | 0 | exec | cron `13 2 * * 1-5` opening_window_l2_poll.py |
| `mike/bin/orb_drift_monitor.py` | T1 | 0 | exec | cron `50 8 * * 1-5` orb_drift_monitor.py |
| `mike/bin/orb_normstat.py` | T1 | 1 | import | cron `50 8 * * 1-5` orb_drift_monitor.py |
| `mike/bin/paper_corp_action.py` | T1 | 0 | exec | cron `40 1 * * 1-5` paper_corp_action.py |
| `mike/bin/paper_corp_action_selfcheck.py` | T1 | 1 | exec | cron `40 1 * * 1-5` paper_corp_action.py |
| `mike/bin/paper_late_feeds.sh` | T1 | 0 | exec | cron `5 13 * * 1-5` paper_late_feeds.sh |
| `mike/bin/paper_main_early_check.sh` | T1 | 0 | exec | cron `40 2 * * 1,3,5` paper_main_early_check.sh (+2) |
| `mike/bin/paper_main_probe_plan.py` | T1 | 0 | exec | cron `52 1 * * 1-5` paper_main_probe_plan.py |
| `mike/bin/paper_programs_daily_report.py` | T1 | 1 | exec | cron `30 0 * * 2-6` paper_programs_daily_report.sh |
| `mike/bin/paper_programs_daily_report.sh` | T1 | 0 | exec | cron `30 0 * * 2-6` paper_programs_daily_report.sh |
| `mike/bin/refresh_fa_ratings.sh` | T1 | 0 | exec | cron `15 2 * * 6` refresh_fa_ratings.sh |
| `mike/bin/refresh_fa_ratings_8l.sh` | T1 | 0 | exec | cron `30 1 * * 6` refresh_fa_ratings_8l.sh |
| `mike/bin/send_macro_note_email.py` | T1 | 2 | exec | cron `0 20 6 * *` vn_realestate_monthly_check.sh |
| `mike/bin/snapshot_corp_action_daily.py` | T1 | 0 | exec | cron `50 23 * * *` snapshot_corp_action_daily.py |
| `mike/bin/treasury_buyback_window_monitor.py` | T1 | 0 | exec | cron `10 0 * * 1` treasury_buyback_window_monitor.py |
| `mike/bin/usage_watch.py` | T1 | 1 | exec | cron `7,27,47 * * * *` fiinprox_harvest_tick.sh (+1) |
| `mike/bin/vn_realestate_monthly_check.py` | T1 | 1 | exec | cron `0 20 6 * *` vn_realestate_monthly_check.sh |
| `mike/bin/vn_realestate_monthly_check.sh` | T1 | 0 | exec | cron `0 20 6 * *` vn_realestate_monthly_check.sh |
| `mike/bin/wait_for_artifact.sh` | T1 | 1 | exec | cron `0 12 * * 1-5` hit_details_daily.sh |
| `newdeals_daily_report.py` | T1 | 0 | exec | cron `0 23 * * 0-4` newdeals_daily_report.py |
| `oil_transmission.py` | T1 | 2 | import | cron `20 12 * * 1-5` pt_8l_daily.sh |
| `oni_index_feed.py` | T1 | 0 | exec | cron `0 2 20 * *` oni_index_feed.py |
| `orb_pt.py` | T1 | 1 | exec | cron `30 8 * * 1-5` papertrade_daily.sh |
| `papertrade_compare.py` | T1 | 1 | exec | cron `30 8 * * 1-5` papertrade_daily.sh |
| `papertrade_daily.sh` | T1 | 0 | exec | cron `30 8 * * 1-5` papertrade_daily.sh |
| `phosphorus_dgc_weekly.py` | T1 | 1 | exec | cron `30 8 * * 1-5` papertrade_daily.sh |
| `preflight_bq_cache.py` | T1 | 1 | exec | cron `45 16 * * 1-5` sync_bq_cache_daily.sh (+9) |
| `pt_8l_daily.sh` | T1 | 0 | exec | cron `20 12 * * 1-5` pt_8l_daily.sh |
| `pt_capitulation_shadow.py` | T1 | 1 | exec | cron `30 8 * * 1-5` papertrade_daily.sh |
| `pt_dates.py` | T1 | 2 | import | cron `30 8 * * 1-5` papertrade_daily.sh |
| `pt_v11_tq34b.py` | T1 | 1 | exec | cron `30 8 * * 1-5` papertrade_daily.sh |
| `pt_v12_macro.py` | T1 | 1 | exec | cron `30 8 * * 1-5` papertrade_daily.sh |
| `pt_v22_dt5g.py` | T1 | 1 | exec | cron `30 8 * * 1-5` papertrade_daily.sh |
| `pt_v4_dt5g.py` | T1 | 1 | exec | cron `30 8 * * 1-5` papertrade_daily.sh |
| `pull_us_market.py` | T1 | 1 | exec | cron `30 8 * * 1-5` papertrade_daily.sh (+1) |
| `rank_8l.py` | T1 | 1 | exec | cron `20 12 * * 1-5` pt_8l_daily.sh |
| `rank_8l_daily_alert.py` | T1 | 1 | exec | cron `20 12 * * 1-5` pt_8l_daily.sh |
| `rating_8l.py` | T1 | 1 | exec | cron `20 12 * * 1-5` pt_8l_daily.sh |
| `rating_8l_history.py` | T1 | 1 | exec | cron `30 1 * * 6` refresh_fa_ratings_8l.sh |
| `refresh_deposit_rate_vn.sh` | T1 | 0 | exec | cron `10 1 3 * *` refresh_deposit_rate_vn.sh |
| `refresh_fa_ratings.py` | T1 | 1 | exec | cron `15 2 * * 6` refresh_fa_ratings.sh |
| `refresh_lagged_caches.py` | T1 | 1 | exec | cron `30 8 * * 1-5` papertrade_daily.sh |
| `regime_size_overlay.py` | T1 | 2 | import | cron `30 8 * * 1-5` papertrade_daily.sh |
| `restate_guard.sh` | T1 | 1 | exec | cron `30 11 * * 1-5` daily_refresh_v34b_linux.sh |
| `rubber_trend_break.py` | T1 | 2 | import | cron `35 11 * * 1-5` rubber_weekly.sh |
| `rubber_weekly.py` | T1 | 1 | exec | cron `35 11 * * 1-5` rubber_weekly.sh |
| `rubber_weekly.sh` | T1 | 0 | exec | cron `35 11 * * 1-5` rubber_weekly.sh |
| `scripts/build_snapshot.py` | T1 | 1 | exec | cron `30 11 * * 1-5` daily_refresh_v34b_linux.sh |
| `sector_lens_monitor.py` | T1 | 1 | exec | cron `20 12 * * 1-5` pt_8l_daily.sh (+2) |
| `snapshot_state_vintage.py` | T1 | 1 | exec | cron `30 8 * * 1-5` papertrade_daily.sh |
| `sync_bq_cache.py` | T1 | 1 | exec | cron `45 16 * * 1-5` sync_bq_cache_daily.sh |
| `sync_bq_cache_daily.sh` | T1 | 0 | exec | cron `45 16 * * 1-5` sync_bq_cache_daily.sh |
| `telegram_run_daily.sh` | T1 | 0 | exec | cron `35 12 * * 1-5` telegram_run_daily.sh |
| `unified_screener.py` | T1 | 1 | exec | cron `20 12 * * 1-5` pt_8l_daily.sh |
| `update_shares_live.py` | T1 | 1 | exec | cron `40 11 * * 1-5` update_shares_live.sh |
| `update_shares_live.sh` | T1 | 0 | exec | cron `40 11 * * 1-5` update_shares_live.sh |
| `vcb_fx_feed.py` | T1 | 0 | exec | cron `15 1 * * 1-5` vcb_fx_feed.py |
| `vn30_8l.py` | T1 | 1 | exec | cron `20 12 * * 1-5` pt_8l_daily.sh |
| `vnindex_5state_dual_v3.py` | T1 | 1 | exec | cron `30 11 * * 1-5` daily_refresh_v34b_linux.sh |
| `vnindex_5state_ew_v1.py` | T1 | 1 | exec | cron `30 11 * * 1-5` daily_refresh_v34b_linux.sh |
| `immutable_publish_selfcheck.py` | T2 | 2 | exec | cron `30 20 * * 5` weekly_ops_audit.sh |
| `mike/bin/anomaly_escalate.py` | T2 | 1 | exec | cron `20 1 * * 1-5` ops_health_check.sh (+1) |
| `mike/bin/archive_memory.py` | T2 | 1 | exec | cron `0 19 * * *` kb_nightly.sh |
| `mike/bin/backup_freshness_check.sh` | T2 | 0 | exec | cron `35 1 * * *` backup_freshness_check.sh |
| `mike/bin/bus_question_housekeeping.py` | T2 | 1 | exec | cron `0 19 * * *` kb_nightly.sh |
| `mike/bin/ccdb_bridge_drift_check.sh` | T2 | 1 | exec | cron `25 1 * * 1-5` cron_health_check_daily.sh |
| `mike/bin/cli_provider.sh` | T2 | 2 | exec | cron `*/10 * * * *` resume_pending.py (+8) |
| `mike/bin/close_bus_question.py` | T2 | 2 | exec | cron `20 1 * * 1-5` ops_health_check.sh (+3) |
| `mike/bin/close_plan_approval_questions.py` | T2 | 1 | exec | cron `20 1 * * 1-5` ops_health_check.sh (+2) |
| `mike/bin/code_quality_autodispatch.py` | T2 | 1 | exec | cron `0 3 * * 0` code_quality_weekly.sh |
| `mike/bin/code_quality_scope.py` | T2 | 1 | exec | cron `0 3 * * 0` code_quality_weekly.sh |
| `mike/bin/code_quality_weekly.sh` | T2 | 0 | exec | cron `0 3 * * 0` code_quality_weekly.sh |
| `mike/bin/compact_done_watcher.sh` | T2 | 1 | exec | hook `SessionStart` session_start.sh |
| `mike/bin/consolidate.sh` | T2 | 0 | exec | cron `7 * * * *` consolidate.sh |
| `mike/bin/consolidate_git_scope_selfcheck.py` | T2 | 1 | exec | cron `0 19 * * *` kb_nightly.sh |
| `mike/bin/context_watch.py` | T2 | 1 | exec | cron `*/10 * * * *` watchdog.sh (+1) |
| `mike/bin/cron_health_check.py` | T2 | 1 | exec | cron `25 1 * * 1-5` cron_health_check_daily.sh |
| `mike/bin/cron_health_check_daily.sh` | T2 | 0 | exec | cron `25 1 * * 1-5` cron_health_check_daily.sh |
| `mike/bin/ctxbloat_fact_check.py` | T2 | 1 | exec | cron `0 19 * * *` kb_nightly.sh |
| `mike/bin/cursor_advance_selfcheck.py` | T2 | 1 | exec | cron `0 19 * * *` kb_nightly.sh |
| `mike/bin/daily_retro.sh` | T2 | 0 | exec | cron `30 17 * * *` daily_retro.sh |
| `mike/bin/discover_sessions.py` | T2 | 0 | exec | cron `*/10 * * * *` discover_sessions.py |
| `mike/bin/dispatch_question_hint.py` | T2 | 2 | exec | cron `*/10 * * * *` resume_pending.py (+8) |
| `mike/bin/fleet_backup.sh` | T2 | 0 | exec | cron `0 17 * * *` fleet_backup.sh |
| `mike/bin/fleet_housekeeping.sh` | T2 | 0 | exec | cron `0 15 * * 0` fleet_housekeeping.sh |
| `mike/bin/forensic_flag_review_check.py` | T2 | 1 | exec | cron `20 1 * * 1-5` ops_health_check.sh (+1) |
| `mike/bin/heartbeat.sh` | T2 | 1 | exec | hook `Stop` stop.sh |
| `mike/bin/incidents_index_sync.py` | T2 | 1 | exec | cron `25 1 * * 1-5` cron_health_check_daily.sh |
| `mike/bin/is_serving.py` | T2 | 1 | exec | cron `*/10 * * * *` watchdog.sh |
| `mike/bin/jobs.sh` | T2 | 2 | exec | cron `*/10 * * * *` resume_pending.py (+8) |
| `mike/bin/kb_nightly.sh` | T2 | 0 | exec | cron `0 19 * * *` kb_nightly.sh |
| `mike/bin/model_config_watch.py` | T2 | 1 | exec | cron `*/10 * * * *` watchdog.sh |
| `mike/bin/notify_telegram.sh` | T2 | 1 | exec | cron `20 1 * * 1-5` ops_health_check.sh (+1) |
| `mike/bin/now_line.py` | T2 | 1 | exec | hook `UserPromptSubmit` user_prompt_submit.sh |
| `mike/bin/ops_health_check.sh` | T2 | 0 | exec | cron `20 1 * * 1-5` ops_health_check.sh (+1) |
| `mike/bin/ops_health_check_selfcheck.py` | T2 | 1 | exec | cron `0 19 * * *` kb_nightly.sh |
| `mike/bin/paper_checkpoint_escalation.sh` | T2 | 0 | exec | cron `40 0 * * 2-6` paper_checkpoint_escalation.sh |
| `mike/bin/production_manifest.py` | T2 | 1 | exec | cron `0 3 * * 0` code_quality_weekly.sh |
| `mike/bin/publish_context.sh` | T2 | 1 | exec | cron `7 * * * *` consolidate.sh (+1) |
| `mike/bin/rebuild_context_mini.py` | T2 | 1 | exec | cron `7 * * * *` consolidate.sh |
| `mike/bin/recap_prev.py` | T2 | 1 | exec | hook `SessionStart` session_start.sh |
| `mike/bin/render_profile_prompt.sh` | T2 | 2 | exec | cron `*/10 * * * *` resume_pending.py (+8) |
| `mike/bin/resume_pending.py` | T2 | 0 | exec | cron `*/10 * * * *` resume_pending.py |
| `mike/bin/run_selfchecks.sh` | T2 | 1 | exec | cron `30 20 * * 5` weekly_ops_audit.sh |
| `mike/bin/selfcheck_baseline_diff.py` | T2 | 1 | exec | cron `30 21 * * *` selfcheck_weekly_baseline_check.sh |
| `mike/bin/selfcheck_weekly_baseline_check.sh` | T2 | 0 | exec | cron `30 21 * * *` selfcheck_weekly_baseline_check.sh |
| `mike/bin/spend_report.py` | T2 | 1 | exec | cron `0 19 * * *` kb_nightly.sh (+1) |
| `mike/bin/spend_report_autodispatch.py` | T2 | 2 | exec | cron `0 2 * * 0` spend_report_weekly.sh |
| `mike/bin/spend_report_weekly.py` | T2 | 1 | exec | cron `0 2 * * 0` spend_report_weekly.sh |
| `mike/bin/spend_report_weekly.sh` | T2 | 0 | exec | cron `0 2 * * 0` spend_report_weekly.sh |
| `mike/bin/staleness_watch.py` | T2 | 1 | exec | cron `*/10 * * * *` watchdog.sh |
| `mike/bin/sync_native_agents.sh` | T2 | 1 | exec | cron `0 17 * * *` fleet_backup.sh |
| `mike/bin/time_claim_audit.py` | T2 | 1 | exec | cron `30 17 * * *` daily_retro.sh |
| `mike/bin/usage_limit_phrases.sh` | T2 | 1 | exec | cron `*/10 * * * *` resume_pending.py (+8) |
| `mike/bin/wags_arch_review_round2.py` | T2 | 2 | exec | cron `20 1 * * 1-5` ops_health_check.sh (+3) |
| `mike/bin/wags_autofix.sh` | T2 | 1 | exec | cron `20 1 * * 1-5` ops_health_check.sh (+3) |
| `mike/bin/wags_bus_question_pending.py` | T2 | 2 | exec | cron `20 1 * * 1-5` ops_health_check.sh (+3) |
| `mike/bin/wags_bus_verdict.py` | T2 | 2 | exec | cron `20 1 * * 1-5` ops_health_check.sh (+3) |
| `mike/bin/wags_risk_tier.py` | T2 | 2 | exec | cron `20 1 * * 1-5` ops_health_check.sh (+3) |
| `mike/bin/wags_verdict_parse.py` | T2 | 2 | exec | cron `20 1 * * 1-5` ops_health_check.sh (+3) |
| `mike/bin/wakeup_profile.py` | T2 | 1 | exec | cron `0 19 * * *` kb_nightly.sh |
| `mike/bin/watchdog.sh` | T2 | 0 | exec | cron `*/10 * * * *` watchdog.sh |
| `mike/bin/watcher_slow_threshold.py` | T2 | 2 | exec | cron `*/10 * * * *` resume_pending.py (+8) |
| `mike/bin/weekly_ops_audit.sh` | T2 | 0 | exec | cron `30 20 * * 5` weekly_ops_audit.sh |
| `mike/bin/worktree_cleanup_daily.sh` | T2 | 0 | exec | cron `0 20 * * *` worktree_cleanup_daily.sh |
| `mike/bin/worktree_stale_check.py` | T2 | 1 | exec | cron `20 1 * * 1-5` ops_health_check.sh (+1) |
| `mike/hooks/_directives.sh` | T2 | 1 | exec | hook `SessionStart` session_start.sh (+1) |
| `mike/hooks/_resolve_id.sh` | T2 | 1 | exec | hook `SessionStart` session_start.sh (+2) |
| `mike/hooks/session_start.sh` | T2 | 0 | exec | hook `SessionStart` session_start.sh |
| `mike/hooks/stop.sh` | T2 | 0 | exec | hook `Stop` stop.sh |
| `mike/hooks/user_prompt_submit.sh` | T2 | 0 | exec | hook `UserPromptSubmit` user_prompt_submit.sh |
| `t2_settlement_selfcheck.py` | T2 | 2 | exec | cron `0 19 * * *` kb_nightly.sh |
| `account_overrides_broker_resolution_selfcheck.py` | T3 | - | selfcheck | phủ: trading_bot/__init__.py, trading_bot/config.py |
| `anomaly_gate_prod_parity_selfcheck.py` | T3 | - | selfcheck | phủ: anomaly_gate.py |
| `anomaly_gate_selfcheck.py` | T3 | - | selfcheck | phủ: anomaly_gate.py |
| `approval_gate_selfcheck.py` | T3 | - | selfcheck | phủ: bot_execute.py, trading_bot/__init__.py (+2) |
| `atc_postclose_selfcheck.py` | T3 | - | selfcheck | phủ: trading_bot/__init__.py, trading_bot/brokers.py (+4) |
| `basket_price_basis_selfcheck.py` | T3 | - | selfcheck | phủ: custom_basket.py, simulate_holistic_nav.py |
| `book_tagging_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/compute_park_trim.py, mike/bin/park_holdings.py (+4) |
| `brokers_nav_shadow_selfcheck.py` | T3 | - | selfcheck | phủ: trading_bot/__init__.py, trading_bot/brokers.py |
| `capit_lever_selfcheck.py` | T3 | - | selfcheck | phủ: bot_execute.py, mike/bin/send_plan_report.sh (+5) |
| `capit_participation_cap_selfcheck.py` | T3 | - | selfcheck | phủ: trading_bot/__init__.py, trading_bot/config.py (+3) |
| `cash_only_loan_package_selfcheck.py` | T3 | - | selfcheck | phủ: dnse_api.py, trading_bot/__init__.py (+3) |
| `churn_guard_selfcheck.py` | T3 | - | selfcheck | phủ: trading_bot/__init__.py, trading_bot/config.py (+3) |
| `concurrent_lock_selfcheck.py` | T3 | - | selfcheck | phủ: bot_execute.py, trading_bot/__init__.py (+1) |
| `custom30_publish_weight_selfcheck.py` | T3 | - | selfcheck | phủ: custom_basket.py |
| `custom30_yield_labels_selfcheck.py` | T3 | - | selfcheck | phủ: custom30_yield_labels.py, simulate_holistic_nav.py (+2) |
| `dc_book_waterfall_selfcheck.py` | T3 | - | selfcheck | phủ: dc_book_waterfall_paper.py, trading_bot/__init__.py (+1) |
| `dcf_check_selfcheck.py` | T3 | - | selfcheck | phủ: dcf_valuation.py, trading_bot/__init__.py (+3) |
| `dcf_refresh_gate_selfcheck.py` | T3 | - | selfcheck | phủ: dcf_refresh_gate.py |
| `dcf_selector_selfcheck.py` | T3 | - | selfcheck | phủ: custom_basket.py, dcf_valuation.py (+2) |
| `discretionary_accumulation_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/discretionary_accumulation_inject.py, trading_bot/__init__.py (+2) |
| `discretionary_participation_cap_selfcheck.py` | T3 | - | selfcheck | phủ: trading_bot/__init__.py, trading_bot/config.py (+3) |
| `discretionary_rule_a_selfcheck.py` | T3 | - | selfcheck | phủ: trading_bot/__init__.py, trading_bot/discretionary_accumulation.py (+1) |
| `discretionary_target_pct_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/discretionary_accumulation_inject.py, trading_bot/__init__.py (+2) |
| `dt5g_chain_freshness_selfcheck.py` | T3 | - | selfcheck | phủ: assert_chain_outputs.sh, build_dt_4gate.py (+5) |
| `due_diligence_selfcheck.py` | T3 | - | selfcheck | phủ: bot_execute.py, trading_bot/__init__.py (+2) |
| `dynamic_no_chase_ceiling_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/discretionary_accumulation_inject.py, trading_bot/__init__.py (+4) |
| `excluded_tickers_selfcheck.py` | T3 | - | selfcheck | phủ: trading_bot/__init__.py, trading_bot/plan.py |
| `exdate_price_frame_selfcheck.py` | T3 | - | selfcheck | phủ: corp_action_lib.py, mike/bin/merge_park_orders.py (+8) |
| `expected_volume_pacing_selfcheck.py` | T3 | - | selfcheck | phủ: trading_bot/__init__.py, trading_bot/config.py (+3) |
| `extreme_regime_selfcheck.py` | T3 | - | selfcheck | phủ: trading_bot/__init__.py, trading_bot/config.py (+3) |
| `eyrisk_selector_selfcheck.py` | T3 | - | selfcheck | phủ: custom_basket.py, simulate_holistic_nav.py |
| `freshness_ops_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/bq_freshness_check.sh, mike/bin/dispatch.sh (+5) |
| `gdkhq_rollout_selfcheck.py` | T3 | - | selfcheck | phủ: trading_bot/__init__.py, trading_bot/exdate_gate.py (+3) |
| `ghost_order_selfcheck.py` | T3 | - | selfcheck | phủ: trading_bot/__init__.py, trading_bot/brokers.py (+3) |
| `hard_no_chase_ceiling_selfcheck.py` | T3 | - | selfcheck | phủ: trading_bot/__init__.py, trading_bot/config.py (+2) |
| `hybrid_fill_timing_selfcheck.py` | T3 | - | selfcheck | phủ: trading_bot/__init__.py, trading_bot/config.py (+3) |
| `lag_adv_cap_selfcheck.py` | T3 | - | selfcheck | phủ: bot_execute.py, trading_bot/__init__.py (+3) |
| `lag_forensic_filter_selfcheck.py` | T3 | - | selfcheck | phủ: lag_forensic_filter.py, lag_live_schedule.py (+1) |
| `lag_governance_order_gate_selfcheck.py` | T3 | - | selfcheck | phủ: bot_execute.py, lag_forensic_filter.py (+2) |
| `lag_liq_signal_filter_selfcheck.py` | T3 | - | selfcheck | phủ: custom30.py, lag_liq_ledger.py (+3) |
| `lag_live_schedule_selfcheck.py` | T3 | - | selfcheck | phủ: lag_live_schedule.py |
| `lag_rating_filter_selfcheck.py` | T3 | - | selfcheck | phủ: lag_rating_filter.py, simulate_holistic_nav.py |
| `lag_rating_order_gate_selfcheck.py` | T3 | - | selfcheck | phủ: lag_rating_filter.py, trading_bot/__init__.py (+1) |
| `loan_package_multi_account_selfcheck.py` | T3 | - | selfcheck | phủ: dnse_api.py, mike/bin/discretionary_accumulation_inject.py (+4) |
| `loan_package_resolution_selfcheck.py` | T3 | - | selfcheck | phủ: trading_bot/__init__.py, trading_bot/brokers.py (+1) |
| `mike/agents/Mafee/reconcile_parents_selfcheck.py` | T3 | - | selfcheck | phủ: trading_bot/__init__.py, trading_bot/executor.py (+1) |
| `mike/agents/Taylor/anomaly_escalate_selfcheck.py` | T3 | - | selfcheck | phủ: mike/agents/Taylor/anomaly_scan.py, mike/bin/anomaly_escalate.py |
| `mike/agents/Taylor/capit_dd_gate_selfcheck.py` | T3 | - | selfcheck | phủ: anomaly_gate.py, simulate_holistic_nav.py |
| `mike/agents/Taylor/chase_cap_selfcheck.py` | T3 | - | selfcheck | phủ: trading_bot/__init__.py, trading_bot/config.py (+1) |
| `mike/agents/Taylor/insider_flags_selfcheck.py` | T3 | - | selfcheck | phủ: anomaly_gate.py, mike/agents/Taylor/insider_flags.py |
| `mike/agents/Taylor/seccap_dyn_selfcheck.py` | T3 | - | selfcheck | phủ: custom_basket.py, simulate_holistic_nav.py |
| `mike/agents/Taylor/universe_freshness_selfcheck.py` | T3 | - | selfcheck | phủ: mike/agents/Taylor/anomaly_scan.py |
| `mike/agents/Winston/freshness_warn_selfcheck.py` | T3 | - | selfcheck | phủ: anomaly_gate.py, dt5g_freshness.py (+6) |
| `mike/bin/append_event_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/append_event.sh, mike/bin/json_payload_diag.py (+1) |
| `mike/bin/backup_freshness_check_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/backup_freshness_check.sh |
| `mike/bin/broker_fill_confirm_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/broker_fill_confirm.py |
| `mike/bin/build_universe_pit_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/build_universe_pit.py |
| `mike/bin/bus_question_closure_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/append_event.sh, mike/bin/bus_question_audit.py (+1) |
| `mike/bin/bus_question_housekeeping_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/bus_question_housekeeping.py, mike/bin/check_report_cadence.sh (+1) |
| `mike/bin/check_report_cadence_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/append_event.sh, mike/bin/bus_question_audit.py (+1) |
| `mike/bin/circuit_expiry_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/dispatch.sh, mike/bin/mike_json.py |
| `mike/bin/claim_reply_selfcheck.sh` | T3 | - | selfcheck | phủ: mike/bin/jobs.sh, mike/bin/mike_json.py |
| `mike/bin/cli_provider_selfcheck.sh` | T3 | - | selfcheck | phủ: mike/bin/append_event.sh, mike/bin/consolidate.sh (+4) |
| `mike/bin/close_plan_approval_questions_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/bus_question_audit.py, mike/bin/close_plan_approval_questions.py |
| `mike/bin/code_quality_autodispatch_selfcheck.sh` | T3 | - | selfcheck | phủ: mike/bin/append_event.sh, mike/bin/code_quality_autodispatch.py (+2) |
| `mike/bin/code_quality_weekly_scope_selfcheck.sh` | T3 | - | selfcheck | phủ: mike/bin/code_quality_scope.py, mike/bin/code_quality_weekly.sh (+2) |
| `mike/bin/commit_collision_gate_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/consolidate.sh, mike/bin/cron_health_check_daily.sh (+11) |
| `mike/bin/compute_active_nav_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/compute_active_nav.py, mike/bin/compute_jit_unpark.py (+3) |
| `mike/bin/compute_jit_unpark_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/compute_jit_unpark.py, mike/bin/park_holdings.py |
| `mike/bin/compute_park_trim_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/compute_jit_unpark.py, mike/bin/compute_park_trim.py (+4) |
| `mike/bin/corp_action_auto_confirm_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/corp_action_auto_confirm.py |
| `mike/bin/corp_action_feed_canary_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/corp_action_feed_canary.py, wc_env.sh |
| `mike/bin/corp_action_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/corp_actions.py, mike/bin/park_holdings.py (+1) |
| `mike/bin/daily_nav_snapshot_corpaction_error_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/daily_nav_snapshot.py, mike/bin/verify_account_snapshot.py |
| `mike/bin/daily_nav_snapshot_from_raw_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/corp_action_daily.py, mike/bin/daily_nav_snapshot.py (+1) |
| `mike/bin/daily_retro_failcause_selfcheck.sh` | T3 | - | selfcheck | phủ: mike/bin/daily_retro.sh, mike/bin/usage_limit_phrases.sh |
| `mike/bin/discretionary_accumulation_inject_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/discretionary_accumulation_inject.py, mike/bin/exdate_frame.py (+4) |
| `mike/bin/discretionary_margin_gate_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/corp_actions.py, mike/bin/daily_nav_snapshot.py (+1) |
| `mike/bin/dispatch_discord_topic_selfcheck.sh` | T3 | - | selfcheck | phủ: mike/bin/append_event.sh, mike/bin/consolidate.sh (+4) |
| `mike/bin/dispatch_question_hint_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/dispatch.sh, mike/bin/dispatch_question_hint.py |
| `mike/bin/dispatch_tiny_prompt_selfcheck.sh` | T3 | - | selfcheck | phủ: mike/bin/dispatch.sh, mike/bin/ops_health_check.sh (+1) |
| `mike/bin/dispatch_wc_root_anchor_selfcheck.sh` | T3 | - | selfcheck | phủ: mike/bin/dispatch.sh, preflight_bq_cache.py (+1) |
| `mike/bin/dividend_adjusted_return_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/dividend_adjusted_return.py |
| `mike/bin/dt5g_publisher_gate_selfcheck.sh` | T3 | - | selfcheck | phủ: mike/bin/bq_freshness_check.sh, mike/bin/notify.sh (+1) |
| `mike/bin/dt5g_writer_watch_selfcheck.sh` | T3 | - | selfcheck | phủ: mike/bin/append_event.sh, mike/bin/dt5g_writer_watch.py (+2) |
| `mike/bin/due_diligence_corp_flags_selfcheck.py` | T3 | - | selfcheck | phủ: corp_action_lib.py, trading_bot/__init__.py (+1) |
| `mike/bin/eod_delivery_wiring_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/eod_trading_report.sh |
| `mike/bin/eod_trading_report_account_filter_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/broker_fill_confirm.py, mike/bin/eod_trading_report.sh (+1) |
| `mike/bin/exdate_frame_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/compute_active_nav.py, mike/bin/compute_jit_unpark.py (+5) |
| `mike/bin/exrights_price_basis_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/daily_nav_snapshot.py, mike/bin/verify_account_snapshot.py |
| `mike/bin/filter_lag_entry_window_selfcheck.py` | T3 | - | selfcheck | phủ: trading_bot/__init__.py, trading_bot/vn_market.py |
| `mike/bin/forensic_flag_review_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/forensic_flag_review_check.py |
| `mike/bin/job_cancel_guard_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/append_event.sh, mike/bin/consolidate.sh (+5) |
| `mike/bin/kb_nightly_backup_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/kb_nightly.sh |
| `mike/bin/kb_nightly_ctxbloat_split_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/ctxbloat_fact_check.py, mike/bin/dispatch.sh (+1) |
| `mike/bin/kb_nightly_phase1_atomic_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/kb_nightly.sh |
| `mike/bin/merge_park_orders_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/dnse_fee_rates.py, mike/bin/merge_park_orders.py |
| `mike/bin/mike_json_archive_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/mike_json.py |
| `mike/bin/mike_json_has_event_prefix_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/mike_json.py |
| `mike/bin/nav_corpaction_gate_e2e_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/corp_action_daily.py, mike/bin/daily_nav_snapshot.py (+1) |
| `mike/bin/nav_cum_dividend_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/daily_nav_snapshot.py |
| `mike/bin/nav_exdate_forecast_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/nav_exdate_forecast.py |
| `mike/bin/nav_scripts_2account_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/daily_nav_snapshot.py, mike/bin/verify_account_snapshot.py |
| `mike/bin/nav_snapshot_daily_selfcheck.sh` | T3 | - | selfcheck | phủ: mike/bin/daily_nav_snapshot.py, mike/bin/eod_trading_report.sh (+7) |
| `mike/bin/nav_sync_retry_rc_selfcheck.sh` | T3 | - | selfcheck | phủ: mike/bin/append_event.sh, mike/bin/daily_nav_snapshot.py (+2) |
| `mike/bin/notify_thread_argswap_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/discord_channel.sh, mike/bin/notify_thread.sh |
| `mike/bin/now_injection_selfcheck.sh` | T3 | - | selfcheck | phủ: mike/bin/discord_channel.sh |
| `mike/bin/opening_window_l2_poll_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/opening_window_l2_poll.py |
| `mike/bin/ops_health_check_rejected_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/ops_health_check.sh |
| `mike/bin/orb_drift_monitor_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/orb_drift_monitor.py |
| `mike/bin/paper_checkpoint_escalation_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/append_event.sh, mike/bin/dispatch.sh (+4) |
| `mike/bin/paper_report_render_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/paper_programs_daily_report.py, paper_entry_adjust.py |
| `mike/bin/plan_funding_gate_fee_sync_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/dnse_fee_rates.py |
| `mike/bin/preempt_wakeup_selfcheck.sh` | T3 | - | selfcheck | phủ: mike/bin/dispatch.sh |
| `mike/bin/preflight_order_invariants_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/preflight_check.sh |
| `mike/bin/production_manifest_selfcheck.sh` | T3 | - | selfcheck | phủ: mike/bin/jobs.sh, mike/bin/production_manifest.py |
| `mike/bin/reconcile_equity_realized_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/dividend_adjusted_return.py, mike/bin/verify_account_snapshot.py |
| `mike/bin/report_delivery_gate_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/nav_period_returns.py, mike/bin/report_delivery_gate.py |
| `mike/bin/report_delivery_ledger_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/notify_thread.sh, mike/bin/report_delivery_gate.py (+4) |
| `mike/bin/report_return_gate_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/report_return_gate.py, mike/bin/wc_paths.py |
| `mike/bin/sector_valuation_lens_selfcheck.py` | T3 | - | selfcheck | phủ: alt_valuation_lens.py |
| `mike/bin/selfcheck_baseline_diff_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/ops_health_check.sh, mike/bin/selfcheck_baseline_diff.py (+2) |
| `mike/bin/send_plan_report_park_jit_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/send_plan_report.sh |
| `mike/bin/send_plan_report_state_gate_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/send_plan_report.sh |
| `mike/bin/signal_holds_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/signal_holds.py |
| `mike/bin/snapshot_corp_action_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/snapshot_corp_action_daily.py |
| `mike/bin/stop_circuit_breaker_selfcheck.sh` | T3 | - | selfcheck | phủ: mike/bin/heartbeat.sh, mike/bin/mike_json.py (+2) |
| `mike/bin/summary_parse_position_selfcheck.sh` | T3 | - | selfcheck | phủ: mike/bin/cron_health_check_daily.sh, mike/bin/daily_retro.sh |
| `mike/bin/treasury_buyback_window_monitor_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/treasury_buyback_window_monitor.py, mike/bin/wc_paths.py (+1) |
| `mike/bin/tz_anchor_gate_selfcheck.py` | T3 | - | selfcheck | phủ: bot_execute.py, mike/bin/dispatch.sh |
| `mike/bin/universe_pit_quality_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/build_universe_pit.py, mike/bin/build_universe_pit_quality.py |
| `mike/bin/vendor_mismatch_alert_selfcheck.sh` | T3 | - | selfcheck | phủ: mike/bin/append_event.sh, mike/bin/notify_thread.sh (+2) |
| `mike/bin/verify_account_snapshot_bq_price_date_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/verify_account_snapshot.py |
| `mike/bin/verify_account_snapshot_broker_positions_marketprice_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/verify_account_snapshot.py |
| `mike/bin/verify_account_snapshot_corp_action_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/verify_account_snapshot.py |
| `mike/bin/verify_account_snapshot_lot_reset_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/verify_account_snapshot.py |
| `mike/bin/verify_finding_bg_job_selfcheck.sh` | T3 | - | selfcheck | phủ: mike/bin/mike_json.py |
| `mike/bin/wags_arch_review_round2_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/bus_question_audit.py, mike/bin/close_bus_question.py (+4) |
| `mike/bin/wags_autofix_postq_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/wags_autofix.sh |
| `mike/bin/wags_bus_question_pending_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/bus_question_audit.py, mike/bin/wags_bus_question_pending.py |
| `mike/bin/wags_bus_verdict_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/wags_autofix.sh, mike/bin/wags_bus_verdict.py |
| `mike/bin/wags_dispatch_dead_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/wags_autofix.sh |
| `mike/bin/wags_verdict_parse_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/wags_verdict_parse.py |
| `mike/bin/wait_for_artifact_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/hit_details_daily.sh, mike/bin/wait_for_artifact.sh |
| `mike/bin/wakeup_profile_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/wakeup_profile.py |
| `mike/bin/watcher_slow_threshold_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/watcher_slow_threshold.py |
| `mike/bin/worktree_stale_check_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/report_return_gate.py, mike/bin/worktree_stale_check.py (+1) |
| `mike/bin/write_scope_conflict_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/dispatch.sh, mike/bin/mike_json.py (+1) |
| `money_path_freshness_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/bq_freshness_check.sh, mike/bin/compute_active_nav.py (+4) |
| `net_offsetting_orders_selfcheck.py` | T3 | - | selfcheck | phủ: trading_bot/__init__.py, trading_bot/plan.py |
| `netting_recon_selfcheck.py` | T3 | - | selfcheck | phủ: trading_bot/__init__.py, trading_bot/netting_recon.py (+1) |
| `order_book_shadow_selfcheck.py` | T3 | - | selfcheck | phủ: trading_bot/__init__.py, trading_bot/brokers.py (+3) |
| `oshares_wire_selfcheck.py` | T3 | - | selfcheck | phủ: oshares_pit.py, rating_8l.py |
| `pacing_horizon_note_selfcheck.py` | T3 | - | selfcheck | phủ: trading_bot/__init__.py, trading_bot/plan.py |
| `paper_main_window_selfcheck.py` | T3 | - | selfcheck | phủ: trading_bot/__init__.py, trading_bot/brokers.py (+3) |
| `paper_probe_netting_selfcheck.py` | T3 | - | selfcheck | phủ: mike/bin/paper_main_probe_plan.py, trading_bot/__init__.py (+1) |
| `phs_flash_api_selfcheck.py` | T3 | - | selfcheck | phủ: phs_flash_api.py, trading_bot/__init__.py (+1) |
| `plan_cash_commitment_selfcheck.py` | T3 | - | selfcheck | phủ: trading_bot/__init__.py, trading_bot/plan_cash_commitment.py (+1) |
| `plan_check_field_schema_selfcheck.py` | T3 | - | selfcheck | phủ: trading_bot/__init__.py, trading_bot/config.py (+3) |
| `plan_funding_gate_selfcheck.py` | T3 | - | selfcheck | phủ: trading_bot/__init__.py, trading_bot/plan_funding_gate.py |
| `probe_linger_selfcheck.py` | T3 | - | selfcheck | phủ: trading_bot/__init__.py, trading_bot/config.py (+2) |
| `quote_l2_logging_selfcheck.py` | T3 | - | selfcheck | phủ: trading_bot/__init__.py, trading_bot/brokers.py |
| `refresh_skip_participation_selfcheck.py` | T3 | - | selfcheck | phủ: trading_bot/__init__.py, trading_bot/brokers.py (+4) |
| `restate_guard_selfcheck.sh` | T3 | - | selfcheck | phủ: restate_guard.sh |
| `route_selector_selfcheck.py` | T3 | - | selfcheck | phủ: custom_basket.py |
| `rubber_weekly_selfcheck.py` | T3 | - | selfcheck | phủ: rubber_trend_break.py, rubber_weekly.py |
| `rule_a_ceiling_selfcheck.py` | T3 | - | selfcheck | phủ: trading_bot/__init__.py, trading_bot/brokers.py (+4) |
| `rule_a_ref_guard_selfcheck.py` | T3 | - | selfcheck | phủ: trading_bot/__init__.py, trading_bot/brokers.py (+4) |
| `sync_cache_lock_selfcheck.py` | T3 | - | selfcheck | phủ: sync_bq_cache.py |
| `tick_retry_selfcheck.py` | T3 | - | selfcheck | phủ: trading_bot/__init__.py, trading_bot/config.py (+2) |
| `universe_pit_p2_selfcheck.py` | T3 | - | selfcheck | phủ: bq_local_cache.py, custom_basket.py (+2) |
| `universe_pit_p3_selfcheck.py` | T3 | - | selfcheck | phủ: simulate_holistic_nav.py |
| `universe_pit_p4_selfcheck.py` | T3 | - | selfcheck | phủ: simulate_holistic_nav.py |
| `v4final_selector_selfcheck.py` | T3 | - | selfcheck | phủ: custom_basket.py, simulate_holistic_nav.py |

## Gốc

| loại | lịch/sự kiện/unit | script | tầng | file trong repo |
|---|---|---|---|---|
| cron | `30 8 * * 1-5` | papertrade_daily.sh | T1 | `papertrade_daily.sh` |
| cron | `20 12 * * 1-5` | pt_8l_daily.sh | T1 | `pt_8l_daily.sh` |
| cron | `35 12 * * 1-5` | telegram_run_daily.sh | T1 | `telegram_run_daily.sh` |
| cron | `30 11 * * 1-5` | daily_refresh_v34b_linux.sh | T1 | `daily_refresh_v34b_linux.sh` |
| cron | `0 1 5 * *` | auto_update_commodity_wb.sh | T1 | `auto_update_commodity_wb.sh` |
| cron | `0 1 10 * *` | auto_update_commodity_wb.sh | T1 | `auto_update_commodity_wb.sh` |
| cron | `7 * * * *` | consolidate.sh | T2 | `mike/bin/consolidate.sh` |
| cron | `*/10 * * * *` | watchdog.sh | T2 | `mike/bin/watchdog.sh` |
| cron | `*/10 * * * *` | discover_sessions.py | T2 | `mike/bin/discover_sessions.py` |
| cron | `*/10 * * * *` | resume_pending.py | T2 | `mike/bin/resume_pending.py` |
| cron | `35 11 * * 1-5` | rubber_weekly.sh | T1 | `rubber_weekly.sh` |
| cron | `0 17 * * *` | fleet_backup.sh | T2 | `mike/bin/fleet_backup.sh` |
| cron | `40 11 * * 1-5` | update_shares_live.sh | T1 | `update_shares_live.sh` |
| cron | `45 11 * * 1-5` | insider_flags.py | T1 | `mike/agents/Taylor/insider_flags.py` |
| cron | `45 16 * * 1-5` | sync_bq_cache_daily.sh | T1 | `sync_bq_cache_daily.sh` |
| cron | `@reboot` | start.sh | T2 | (ngoài repo / không file) |
| cron | `*/5 * * * *` | start.sh | T2 | (ngoài repo / không file) |
| cron | `10 11 * * 1-5` | fetch_new_listings_daily.sh | T1 | `fetch_new_listings_daily.sh` |
| cron | `0 12 * * 1-5` | bq_freshness_check.sh | T0 | `mike/bin/bq_freshness_check.sh` |
| cron | `15 13 * * 1-5` | compute_active_nav_all.sh | T0 | `mike/bin/compute_active_nav_all.sh` |
| cron | `30 13 * * 1-5` | inject_discretionary_orders.sh | T0 | `mike/bin/inject_discretionary_orders.sh` |
| cron | `0 14 * * 1-5` | send_plan_report.sh | T0 | `mike/bin/for_each_live_account.sh`, `mike/bin/send_plan_report.sh` |
| cron | `0 16 * * 1-5` | send_plan_report.sh | T0 | `mike/bin/for_each_live_account.sh`, `mike/bin/send_plan_report.sh` |
| cron | `0 8 * * 5` | check_sbv_weekly.sh | T1 | `mike/bin/check_sbv_weekly.sh` |
| cron | `20 1 * * 1-5` | ops_health_check.sh | T2 | `mike/bin/for_each_live_account.sh`, `mike/bin/ops_health_check.sh` |
| cron | `45 1 * * 1-5` | preflight_check.sh | T0 | `mike/bin/for_each_live_account.sh`, `mike/bin/preflight_check.sh` |
| cron | `0 19 * * *` | kb_nightly.sh | T2 | `mike/bin/kb_nightly.sh` |
| cron | `0 20 * * *` | worktree_cleanup_daily.sh | T2 | `mike/bin/worktree_cleanup_daily.sh` |
| cron | `30 17 * * *` | daily_retro.sh | T2 | `mike/bin/daily_retro.sh` |
| cron | `5 2 * * 1-5` | run_bot.sh | T0 | `mike/bin/run_bot.sh` |
| cron | `5 2 * * 1-5` | run_bot.sh | T0 | `mike/bin/run_bot.sh` |
| cron | `*/5 2-7 * * 1-5` | bot_heartbeat.sh | T0 | `mike/bin/bot_heartbeat.sh` |
| cron | `*/5 2-7 * * 1-5` | bot_heartbeat.sh | T0 | `mike/bin/bot_heartbeat.sh` |
| cron | `30 4 * * 1-5` | pkill | T0 | (ngoài repo / không file) |
| cron | `30 4 * * 1-5` | pkill | T0 | (ngoài repo / không file) |
| cron | `31 4 * * 1-5` | session_announce.sh | T0 | `mike/bin/session_announce.sh` |
| cron | `1 6 * * 1-5` | session_announce.sh | T0 | `mike/bin/session_announce.sh` |
| cron | `50 7 * * 1-5` | session_announce.sh | T0 | `mike/bin/session_announce.sh` |
| cron | `45 5 * * 1-5` | ops_health_check.sh | T2 | `mike/bin/for_each_live_account.sh`, `mike/bin/ops_health_check.sh` |
| cron | `0 6 * * 1-5` | run_bot.sh | T0 | `mike/bin/run_bot.sh` |
| cron | `0 6 * * 1-5` | run_bot.sh | T0 | `mike/bin/run_bot.sh` |
| cron | `0 12 * * 1-5` | hit_details_daily.sh | T1 | `mike/bin/hit_details_daily.sh` |
| cron | `10 12 * * 1-5` | eod_trading_report.sh | T0 | `mike/bin/eod_trading_report.sh`, `mike/bin/for_each_live_account.sh` |
| cron | `30 0 * * 2-6` | paper_programs_daily_report.sh | T1 | `mike/bin/paper_programs_daily_report.sh` |
| cron | `15 17 * * 1-5` | dc_book_waterfall_paper.py | T1 | `dc_book_waterfall_paper.py` |
| cron | `15 1 * * 1-5` | vcb_fx_feed.py | T1 | `vcb_fx_feed.py` |
| cron | `0 2 * * 1` | hog_price_feed.py | T1 | `hog_price_feed.py` |
| cron | `0 23 * * 0-4` | newdeals_daily_report.py | T1 | `newdeals_daily_report.py` |
| cron | `52 1 * * 1-5` | paper_main_probe_plan.py | T1 | `mike/bin/paper_main_probe_plan.py` |
| cron | `10 2 * * 1,3,5` | bot_execute.py | T0 | `bot_execute.py` |
| cron | `46 3 * * 2,4` | bot_execute.py | T0 | `bot_execute.py` |
| cron | `32 4 * * 1-5` | pkill | T0 | (ngoài repo / không file) |
| cron | `5 6 * * 1-5` | bot_execute.py | T0 | `bot_execute.py` |
| cron | `40 2 * * 1,3,5` | paper_main_early_check.sh | T1 | `mike/bin/paper_main_early_check.sh` |
| cron | `16 4 * * 2,4` | paper_main_early_check.sh | T1 | `mike/bin/paper_main_early_check.sh` |
| cron | `35 6 * * 1-5` | paper_main_early_check.sh | T1 | `mike/bin/paper_main_early_check.sh` |
| cron | `30 1 * * 6` | refresh_fa_ratings_8l.sh | T1 | `mike/bin/refresh_fa_ratings_8l.sh` |
| cron | `15 2 * * 6` | refresh_fa_ratings.sh | T1 | `mike/bin/refresh_fa_ratings.sh` |
| cron | `0 13 * * *` | fa_ratings_earnings_window_daily.sh | T1 | `mike/bin/fa_ratings_earnings_window_daily.sh` |
| cron | `10 1 3 * *` | refresh_deposit_rate_vn.sh | T1 | `refresh_deposit_rate_vn.sh` |
| cron | `10 1 11 * *` | dcf_refresh_gate.py | T1 | `dcf_refresh_gate.py` |
| cron | `10 1 * * 5` | fearbuy_weekly_scan.sh | T1 | `mike/bin/fearbuy_weekly_scan.sh` |
| cron | `0 1 * * 1` | fearbuy_weekly_scan.sh | T1 | `mike/bin/fearbuy_weekly_scan.sh` |
| cron | `5 13 * * 1-5` | paper_late_feeds.sh | T1 | `mike/bin/paper_late_feeds.sh` |
| cron | `0 15 1 * *` | bq_monthly_pin.sh | T1 | `mike/bin/bq_monthly_pin.sh` |
| cron | `0 15 * * 0` | fleet_housekeeping.sh | T2 | `mike/bin/fleet_housekeeping.sh` |
| cron | `30 20 * * 5` | weekly_ops_audit.sh | T2 | `mike/bin/weekly_ops_audit.sh` |
| cron | `25 1 * * 1-5` | cron_health_check_daily.sh | T2 | `mike/bin/cron_health_check_daily.sh` |
| cron | `30 1 * * *` | check_report_cadence.sh | T0 | `mike/bin/check_report_cadence.sh` |
| cron | `40 0 * * 2-6` | paper_checkpoint_escalation.sh | T2 | `mike/bin/paper_checkpoint_escalation.sh` |
| cron | `5 9 * * 1-5` | custom30v_rebalance_watch.sh | T1 | `mike/bin/custom30v_rebalance_watch.sh` |
| cron | `30 21 * * *` | selfcheck_weekly_baseline_check.sh | T2 | `mike/bin/selfcheck_weekly_baseline_check.sh` |
| cron | `30 0 * * 1-5` | corp_action_daily.sh | T1 | `mike/bin/corp_action_daily.sh` |
| cron | `0 2 * * 6` | check_report_cadence.sh | T0 | `mike/bin/check_report_cadence.sh` |
| cron | `0 2 1 * *` | check_report_cadence.sh | T0 | `mike/bin/check_report_cadence.sh` |
| cron | `30 12 * * 1-5` | park_trim_daily.sh | T0 | `mike/bin/park_trim_daily.sh` |
| cron | `40 12 * * 1-5` | jit_unpark_daily.sh | T0 | `mike/bin/jit_unpark_daily.sh` |
| cron | `20 13 * * 1-5` | merge_park_daily.sh | T0 | `mike/bin/merge_park_daily.sh` |
| cron | `0 2 * * 0` | spend_report_weekly.sh | T2 | `mike/bin/spend_report_weekly.sh` |
| cron | `0 3 * * 0` | code_quality_weekly.sh | T2 | `mike/bin/code_quality_weekly.sh` |
| cron | `45 14 * * 1-5` | late_plan_catchup.sh | T0 | `mike/bin/late_plan_catchup.sh` |
| cron | `0 15 * * 1-5` | late_plan_catchup.sh | T0 | `mike/bin/late_plan_catchup.sh` |
| cron | `30 16 * * 1-5` | late_plan_catchup.sh | T0 | `mike/bin/late_plan_catchup.sh` |
| cron | `50 23 * * *` | snapshot_corp_action_daily.py | T1 | `mike/bin/snapshot_corp_action_daily.py`, `wc_env.sh` |
| cron | `15 8 * * 1-5` | capture_upcom_vwap_eod.sh | T1 | `mike/bin/capture_upcom_vwap_eod.sh` |
| cron | `20 17 * * 1-5` | c1_shadow_paper.py | T1 | `c1_shadow_paper.py` |
| cron | `25 12 * * 1-5` | corp_action_auto_confirm.py | T0 | `mike/bin/corp_action_auto_confirm.py` |
| cron | `20 8 * * 1-5` | discretionary_margin_check_exits_daily.sh | T0 | `mike/bin/discretionary_margin_check_exits_daily.sh` |
| cron | `0 20 6 * *` | vn_realestate_monthly_check.sh | T1 | `mike/bin/vn_realestate_monthly_check.sh` |
| cron | `*/15 12-14 * * 1-5` | nav_sync_retry.sh | T0 | `mike/bin/nav_sync_retry.sh` |
| cron | `50 12 * * 1-5` | nav_snapshot_daily.sh | T0 | `mike/bin/nav_snapshot_daily.sh` |
| cron | `35 1 * * *` | backup_freshness_check.sh | T2 | `mike/bin/backup_freshness_check.sh` |
| cron | `0 2 20 * *` | oni_index_feed.py | T1 | `oni_index_feed.py` |
| cron | `7,27,47 * * * *` | fiinprox_harvest_tick.sh | T1 | `mike/bin/fiinprox_harvest_tick.sh` |
| cron | `5 0 * * 1-5` | corp_action_feed_canary.py | T1 | `mike/bin/corp_action_feed_canary.py`, `wc_env.sh` |
| cron | `10 0 * * 1` | treasury_buyback_window_monitor.py | T1 | `mike/bin/treasury_buyback_window_monitor.py`, `wc_env.sh` |
| cron | `50 1 * * 1-5` | plan_approval_reminder.sh | T0 | `mike/bin/plan_approval_reminder.sh` |
| cron | `40 1 * * 1-5` | paper_corp_action.py | T1 | `mike/bin/paper_corp_action.py` |
| cron | `50 8 * * 1-5` | orb_drift_monitor.py | T1 | `mike/bin/orb_drift_monitor.py` |
| cron | `13 2 * * 1-5` | opening_window_l2_poll.py | T1 | `mike/bin/opening_window_l2_poll.py` |
| hook | `SessionStart` | session_start.sh | T2 | `mike/hooks/session_start.sh` |
| hook | `Stop` | stop.sh | T2 | `mike/hooks/stop.sh` |
| hook | `UserPromptSubmit` | user_prompt_submit.sh | T2 | `mike/hooks/user_prompt_submit.sh` |
