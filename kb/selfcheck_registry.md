---
kind: reference
title: Selfcheck registry — snapshot tự sinh, ĐỪNG sửa tay
generated_by: bin/run_selfchecks.sh
generated_at: 2026-08-10T12:05:23Z
---

# Selfcheck registry (auto-generated, ĐỪNG sửa tay — sửa `bin/run_selfchecks.sh`)

Chạy: `bash mike/bin/run_selfchecks.sh [--live]`. Lần gần nhất: 140 PASS / 38 FAIL / 27 SKIP (live).

| File | Tier | Status | Thời gian |
|---|---|---|---|
| `anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 2s |
| `anomaly_gate_selfcheck.py` | offline | PASS | 7s |
| `approval_gate_selfcheck.py` | offline | PASS | 0s |
| `basket_price_basis_audit_selfcheck.py` | offline | PASS | 8s |
| `basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `book_tagging_selfcheck.py` | offline | PASS | 1s |
| `capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `capit_participation_cap_selfcheck.py` | offline | PASS | 1s |
| `cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `churn_guard_selfcheck.py` | offline | PASS | 1s |
| `concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `custom30_publish_weight_selfcheck.py` | offline | PASS | 0s |
| `dc_book_waterfall_selfcheck.py` | offline | PASS | 0s |
| `dcf_check_selfcheck.py` | offline | PASS | 1s |
| `dcf_refresh_gate_selfcheck.py` | offline | PASS | 0s |
| `dcf_selector_selfcheck.py` | offline | PASS | 1s |
| `discretionary_accumulation_selfcheck.py` | offline | PASS | 1s |
| `discretionary_participation_cap_selfcheck.py` | offline | PASS | 1s |
| `dt5g_chain_freshness_selfcheck.py` | offline | PASS | 0s |
| `due_diligence_selfcheck.py` | offline | PASS | 11s |
| `edge_wlag_gate_selfcheck.py` | offline | PASS | 1s |
| `excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `extreme_regime_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `freshness_ops_selfcheck.py` | offline | PASS | 2s |
| `ghost_order_selfcheck.py` | offline | PASS | 1s |
| `hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `hybrid_fill_timing_selfcheck.py` | offline | PASS | 3s |
| `immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `lag_adv_cap_selfcheck.py` | offline | PASS | 0s |
| `lag_forensic_filter_selfcheck.py` | offline | PASS | 1s |
| `lag_governance_order_gate_selfcheck.py` | offline | PASS | 0s |
| `lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `lag_live_schedule_selfcheck.py` | offline | FAIL(rc=1) | 22s |
| `lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `lag_rating_order_gate_selfcheck.py` | offline | PASS | 1s |
| `loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Mafee/reconcile_parents_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/anomaly_escalate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/capit_dd_gate_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/chase_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/insider_flags_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/pending_adv3t_hard_gate_20260810/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/pending_live_flip_chase_cap_20260804/new/chase_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/pending_live_flip_chase_cap_20260804/new/dc_book_waterfall_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/pending_park_trim_partial_reconcile_20260810/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/seccap_dyn_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Winston/freshness_warn_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522519012066721923/agents/Mafee/reconcile_parents_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522519012066721923/agents/Taylor/anomaly_escalate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1522519012066721923/agents/Taylor/capit_dd_gate_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/wt-1522519012066721923/agents/Taylor/chase_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522519012066721923/agents/Taylor/insider_flags_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522519012066721923/agents/Taylor/pending_live_flip_chase_cap_20260804/new/chase_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522519012066721923/agents/Taylor/pending_live_flip_chase_cap_20260804/new/dc_book_waterfall_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522519012066721923/agents/Taylor/seccap_dyn_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/wt-1522519012066721923/agents/Winston/freshness_warn_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1522519012066721923/bin/build_universe_pit_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522519012066721923/bin/cli_provider_selfcheck.sh` | offline | PASS | 55s |
| `mike/agents/wt-1522519012066721923/bin/compute_active_nav_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522519012066721923/bin/compute_jit_unpark_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522519012066721923/bin/compute_park_trim_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522519012066721923/bin/consolidate_git_scope_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1522519012066721923/bin/corp_action_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522519012066721923/bin/cursor_advance_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1522519012066721923/bin/dispatch_discord_topic_selfcheck.sh` | offline | PASS | 44s |
| `mike/agents/wt-1522519012066721923/bin/dt5g_publisher_gate_selfcheck.sh` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522519012066721923/bin/dt5g_writer_watch_selfcheck.sh` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522519012066721923/bin/filter_lag_entry_window_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522519012066721923/bin/mike_json_archive_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1522519012066721923/bin/nav_cum_dividend_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522519012066721923/bin/nav_scripts_2account_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522519012066721923/bin/ops_health_check_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522519012066721923/bin/paper_checkpoint_escalation_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522519012066721923/bin/paper_report_render_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1522519012066721923/bin/plan_canonical_identity_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522519012066721923/bin/preflight_order_invariants_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522519012066721923/bin/run_selfchecks.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/wt-1522519012066721923/bin/sector_valuation_lens_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522519012066721923/bin/selfcheck_scope_map.sh` | offline | PASS | 0s |
| `mike/agents/wt-1522519012066721923/bin/selfcheck_weekly_baseline_artifact_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522519012066721923/bin/selfcheck_weekly_baseline_check.sh` | offline | FAIL(rc=124) | 60s |
| `mike/agents/wt-1522519012066721923/bin/send_plan_report_park_jit_selfcheck.py` | offline | FAIL(rc=1) | 5s |
| `mike/agents/wt-1522519012066721923/bin/time_standard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522519012066721923/bin/universe_pit_quality_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/wt-1522519012066721923/bin/verify_account_snapshot_corp_action_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522519012066721923/bin/wakeup_profile_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/bin/build_universe_pit_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/cli_provider_selfcheck.sh` | offline | PASS | 56s |
| `mike/bin/compute_active_nav_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/compute_jit_unpark_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/compute_park_trim_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/consolidate_git_scope_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/corp_action_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/cursor_advance_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/dispatch_discord_topic_selfcheck.sh` | offline | PASS | 44s |
| `mike/bin/dt5g_publisher_gate_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/dt5g_writer_watch_selfcheck.sh` | offline | PASS | 16s |
| `mike/bin/filter_lag_entry_window_selfcheck.py` | offline | PASS | 11s |
| `mike/bin/job_cancel_guard_selfcheck.py` | offline | FAIL(rc=1) | 33s |
| `mike/bin/mike_json_archive_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/nav_cum_dividend_selfcheck.py` | offline | PASS | 14s |
| `mike/bin/nav_scripts_2account_selfcheck.py` | offline | PASS | 23s |
| `mike/bin/ops_health_check_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/paper_checkpoint_escalation_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/paper_report_render_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/preflight_order_invariants_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/run_selfchecks.sh` | live | SKIP(--live để chạy) | - |
| `mike/bin/sector_valuation_lens_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/selfcheck_scope_map.sh` | offline | PASS | 0s |
| `mike/bin/selfcheck_weekly_baseline_check.sh` | offline | FAIL(rc=124) | 60s |
| `mike/bin/send_plan_report_park_jit_selfcheck.py` | offline | FAIL(rc=1) | 5s |
| `mike/bin/universe_pit_quality_selfcheck.py` | offline | FAIL(rc=1) | 6s |
| `mike/bin/verify_account_snapshot_corp_action_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/verify_account_snapshot_lot_reset_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/wakeup_profile_selfcheck.py` | offline | PASS | 1s |
| `money_path_freshness_selfcheck.py` | offline | PASS | 1s |
| `net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `netting_recon_selfcheck.py` | offline | PASS | 0s |
| `paper_main_window_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `paper_probe_netting_selfcheck.py` | offline | PASS | 0s |
| `plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `plan_funding_gate_selfcheck.py` | offline | PASS | 0s |
| `refresh_skip_participation_selfcheck.py` | offline | PASS | 2s |
| `restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `route_selector_selfcheck.py` | offline | PASS | 4s |
| `rubber_weekly_selfcheck.py` | offline | PASS | 2s |
| `sync_cache_lock_selfcheck.py` | offline | PASS | 5s |
| `t2_settlement_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `tbot/code/tests/selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `wt-1520374161971875940/agents/Mafee/reconcile_parents_selfcheck.py` | offline | PASS | 0s |
| `wt-1520374161971875940/agents/Taylor/anomaly_escalate_selfcheck.py` | offline | PASS | 0s |
| `wt-1520374161971875940/agents/Taylor/capit_dd_gate_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `wt-1520374161971875940/agents/Taylor/chase_cap_selfcheck.py` | offline | PASS | 0s |
| `wt-1520374161971875940/agents/Taylor/insider_flags_selfcheck.py` | offline | PASS | 1s |
| `wt-1520374161971875940/agents/Taylor/pending_live_flip_chase_cap_20260804/new/chase_cap_selfcheck.py` | offline | PASS | 0s |
| `wt-1520374161971875940/agents/Taylor/pending_live_flip_chase_cap_20260804/new/dc_book_waterfall_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `wt-1520374161971875940/agents/Taylor/seccap_dyn_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `wt-1520374161971875940/agents/Winston/freshness_warn_selfcheck.py` | offline | PASS | 0s |
| `wt-1520374161971875940/bin/build_universe_pit_selfcheck.py` | offline | PASS | 1s |
| `wt-1520374161971875940/bin/cli_provider_selfcheck.sh` | offline | PASS | 54s |
| `wt-1520374161971875940/bin/compute_jit_unpark_selfcheck.py` | offline | PASS | 2s |
| `wt-1520374161971875940/bin/compute_park_trim_selfcheck.py` | offline | PASS | 0s |
| `wt-1520374161971875940/bin/consolidate_git_scope_selfcheck.py` | offline | PASS | 1s |
| `wt-1520374161971875940/bin/corp_action_selfcheck.py` | offline | PASS | 0s |
| `wt-1520374161971875940/bin/cursor_advance_selfcheck.py` | offline | PASS | 2s |
| `wt-1520374161971875940/bin/dispatch_discord_topic_selfcheck.sh` | offline | PASS | 43s |
| `wt-1520374161971875940/bin/dt5g_publisher_gate_selfcheck.sh` | offline | PASS | 1s |
| `wt-1520374161971875940/bin/dt5g_writer_watch_selfcheck.sh` | offline | PASS | 15s |
| `wt-1520374161971875940/bin/filter_lag_entry_window_selfcheck.py` | offline | PASS | 0s |
| `wt-1520374161971875940/bin/mike_json_archive_selfcheck.py` | offline | PASS | 1s |
| `wt-1520374161971875940/bin/nav_cum_dividend_selfcheck.py` | offline | PASS | 15s |
| `wt-1520374161971875940/bin/nav_scripts_2account_selfcheck.py` | offline | PASS | 21s |
| `wt-1520374161971875940/bin/ops_health_check_selfcheck.py` | offline | PASS | 1s |
| `wt-1520374161971875940/bin/paper_checkpoint_escalation_selfcheck.py` | offline | PASS | 0s |
| `wt-1520374161971875940/bin/paper_report_render_selfcheck.py` | offline | PASS | 0s |
| `wt-1520374161971875940/bin/preflight_order_invariants_selfcheck.py` | offline | PASS | 0s |
| `wt-1520374161971875940/bin/run_selfchecks.sh` | live | SKIP(--live để chạy) | - |
| `wt-1520374161971875940/bin/sector_valuation_lens_selfcheck.py` | offline | PASS | 1s |
| `wt-1520374161971875940/bin/selfcheck_scope_map.sh` | offline | PASS | 0s |
| `wt-1520374161971875940/bin/selfcheck_weekly_baseline_check.sh` | offline | FAIL(rc=124) | 60s |
| `wt-1520374161971875940/bin/send_plan_report_park_jit_selfcheck.py` | offline | FAIL(rc=1) | 5s |
| `wt-1520374161971875940/bin/universe_pit_quality_selfcheck.py` | offline | FAIL(rc=1) | 6s |
| `wt-1520374161971875940/bin/verify_account_snapshot_corp_action_selfcheck.py` | offline | PASS | 2s |
| `wt-1520374161971875940/bin/wakeup_profile_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `wt-1532076080175779942/agents/Mafee/reconcile_parents_selfcheck.py` | offline | PASS | 0s |
| `wt-1532076080175779942/agents/Taylor/anomaly_escalate_selfcheck.py` | offline | PASS | 0s |
| `wt-1532076080175779942/agents/Taylor/capit_dd_gate_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `wt-1532076080175779942/agents/Taylor/chase_cap_selfcheck.py` | offline | PASS | 0s |
| `wt-1532076080175779942/agents/Taylor/insider_flags_selfcheck.py` | offline | PASS | 1s |
| `wt-1532076080175779942/agents/Taylor/pending_live_flip_chase_cap_20260804/new/chase_cap_selfcheck.py` | offline | PASS | 0s |
| `wt-1532076080175779942/agents/Taylor/pending_live_flip_chase_cap_20260804/new/dc_book_waterfall_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `wt-1532076080175779942/agents/Taylor/seccap_dyn_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `wt-1532076080175779942/agents/Winston/freshness_warn_selfcheck.py` | offline | PASS | 0s |
| `wt-1532076080175779942/bin/build_universe_pit_selfcheck.py` | offline | PASS | 1s |
| `wt-1532076080175779942/bin/cli_provider_selfcheck.sh` | offline | PASS | 54s |
| `wt-1532076080175779942/bin/compute_jit_unpark_selfcheck.py` | offline | PASS | 2s |
| `wt-1532076080175779942/bin/compute_park_trim_selfcheck.py` | offline | PASS | 1s |
| `wt-1532076080175779942/bin/consolidate_git_scope_selfcheck.py` | offline | PASS | 0s |
| `wt-1532076080175779942/bin/corp_action_selfcheck.py` | offline | PASS | 0s |
| `wt-1532076080175779942/bin/cursor_advance_selfcheck.py` | offline | PASS | 2s |
| `wt-1532076080175779942/bin/dispatch_discord_topic_selfcheck.sh` | offline | PASS | 43s |
| `wt-1532076080175779942/bin/dt5g_publisher_gate_selfcheck.sh` | offline | PASS | 1s |
| `wt-1532076080175779942/bin/dt5g_writer_watch_selfcheck.sh` | offline | PASS | 16s |
| `wt-1532076080175779942/bin/filter_lag_entry_window_selfcheck.py` | offline | PASS | 0s |
| `wt-1532076080175779942/bin/mike_json_archive_selfcheck.py` | offline | PASS | 0s |
| `wt-1532076080175779942/bin/nav_cum_dividend_selfcheck.py` | offline | PASS | 15s |
| `wt-1532076080175779942/bin/nav_scripts_2account_selfcheck.py` | offline | PASS | 22s |
| `wt-1532076080175779942/bin/ops_health_check_selfcheck.py` | offline | PASS | 0s |
| `wt-1532076080175779942/bin/paper_checkpoint_escalation_selfcheck.py` | offline | PASS | 1s |
| `wt-1532076080175779942/bin/paper_report_render_selfcheck.py` | offline | PASS | 0s |
| `wt-1532076080175779942/bin/preflight_order_invariants_selfcheck.py` | offline | PASS | 0s |
| `wt-1532076080175779942/bin/run_selfchecks.sh` | live | SKIP(--live để chạy) | - |
| `wt-1532076080175779942/bin/sector_valuation_lens_selfcheck.py` | offline | PASS | 0s |
| `wt-1532076080175779942/bin/selfcheck_scope_map.sh` | offline | PASS | 0s |
| `wt-1532076080175779942/bin/selfcheck_weekly_baseline_check.sh` | offline | FAIL(rc=124) | 60s |
| `wt-1532076080175779942/bin/send_plan_report_park_jit_selfcheck.py` | offline | FAIL(rc=1) | 5s |
| `wt-1532076080175779942/bin/universe_pit_quality_selfcheck.py` | offline | FAIL(rc=1) | 16s |
| `wt-1532076080175779942/bin/verify_account_snapshot_corp_action_selfcheck.py` | offline | PASS | 2s |
| `wt-1532076080175779942/bin/wakeup_profile_selfcheck.py` | offline | FAIL(rc=1) | 0s |
