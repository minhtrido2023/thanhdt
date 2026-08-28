---
kind: reference
title: Selfcheck registry — snapshot tự sinh, ĐỪNG sửa tay
generated_by: bin/run_selfchecks.sh
generated_at: 2026-08-28T20:46:45Z
---

# Selfcheck registry (auto-generated, ĐỪNG sửa tay — sửa `bin/run_selfchecks.sh`)

Chạy: `bash mike/bin/run_selfchecks.sh [--live]`. Lần gần nhất: 208 PASS / 15 FAIL / 20 SKIP (live).

| File | Tier | Status | Thời gian |
|---|---|---|---|
| `anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 3s |
| `anomaly_gate_selfcheck.py` | offline | PASS | 7s |
| `approval_gate_selfcheck.py` | offline | PASS | 0s |
| `basket_price_basis_audit_selfcheck.py` | offline | PASS | 8s |
| `basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `book_tagging_selfcheck.py` | offline | PASS | 1s |
| `capit_exit_floor_selfcheck.py` | offline | PASS | 0s |
| `capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `capit_participation_cap_selfcheck.py` | offline | PASS | 2s |
| `cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `churn_guard_selfcheck.py` | offline | PASS | 0s |
| `concurrent_lock_selfcheck.py` | offline | PASS | 1s |
| `custom30_publish_weight_selfcheck.py` | offline | PASS | 0s |
| `custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `dc_book_waterfall_selfcheck.py` | offline | PASS | 1s |
| `dcf_check_selfcheck.py` | offline | PASS | 0s |
| `dcf_refresh_gate_selfcheck.py` | offline | PASS | 1s |
| `dcf_selector_selfcheck.py` | offline | PASS | 1s |
| `discretionary_accumulation_selfcheck.py` | offline | PASS | 0s |
| `discretionary_participation_cap_selfcheck.py` | offline | PASS | 1s |
| `discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `discretionary_target_pct_selfcheck.py` | offline | PASS | 1s |
| `dt5g_chain_freshness_selfcheck.py` | offline | PASS | 0s |
| `due_diligence_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `dynamic_no_chase_ceiling_selfcheck.py` | offline | PASS | 0s |
| `edge_wlag_gate_selfcheck.py` | offline | PASS | 1s |
| `excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `exdate_price_frame_selfcheck.py` | offline | PASS | 1s |
| `expected_volume_pacing_selfcheck.py` | offline | PASS | 7s |
| `expvol_shadow_probe_selfcheck.py` | offline | PASS | 0s |
| `extreme_regime_selfcheck.py` | offline | PASS | 1s |
| `eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `freshness_ops_selfcheck.py` | offline | PASS | 2s |
| `gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `ghost_order_selfcheck.py` | offline | PASS | 1s |
| `hard_no_chase_ceiling_selfcheck.py` | offline | PASS | 3s |
| `hybrid_fill_timing_selfcheck.py` | offline | PASS | 2s |
| `immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `lag_adv_cap_selfcheck.py` | offline | PASS | 1s |
| `lag_forensic_filter_selfcheck.py` | offline | PASS | 0s |
| `lag_governance_order_gate_selfcheck.py` | offline | PASS | 1s |
| `lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `lag_live_schedule_selfcheck.py` | offline | PASS | 22s |
| `lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `lag_rating_order_gate_selfcheck.py` | offline | PASS | 1s |
| `loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/DollarBill/tools/compute_park_add_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Mafee/reconcile_parents_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/anomaly_escalate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/capit_dd_gate_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/chase_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/insider_flags_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/div_growth_tilt_20260821/selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/dividend_yield_floor_20260818/selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/listing_date_exchange_study_20260817/selfcheck_gate.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/pump_before_raise_flag_20260817/selfcheck_pump_flag.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/serial_capital_raiser_20260817/selfcheck_serial.py` | offline | PASS | 8s |
| `mike/agents/Taylor/seccap_dyn_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/universe_freshness_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Winston/freshness_warn_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/bin/append_event_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/approve_plan_with_jit_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/broker_fill_confirm_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/build_universe_pit_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/bus_question_closure_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/bus_question_housekeeping_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/check_report_cadence_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/circuit_expiry_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/claim_reply_selfcheck.sh` | offline | PASS | 1s |
| `mike/bin/cli_provider_selfcheck.sh` | offline | PASS | 56s |
| `mike/bin/code_quality_gate_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/commit_collision_gate_selfcheck.py` | offline | PASS | 4s |
| `mike/bin/compute_active_nav_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/compute_jit_unpark_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/compute_park_trim_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/consolidate_git_scope_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/corp_action_daily_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/corp_action_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/cursor_advance_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/daily_retro_failcause_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/daily_retro_wake_metrics_selfcheck.sh` | offline | FAIL(rc=1) | 0s |
| `mike/bin/diagnosis_evidence_gate_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/bin/dispatch_discord_topic_selfcheck.sh` | offline | PASS | 45s |
| `mike/bin/dispatch_question_hint_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/dispatch_tiny_prompt_selfcheck.sh` | offline | PASS | 2s |
| `mike/bin/dt5g_publisher_gate_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/dt5g_writer_watch_selfcheck.sh` | offline | FAIL(rc=1) | 15s |
| `mike/bin/due_diligence_corp_flags_selfcheck.py` | offline | PASS | 50s |
| `mike/bin/eod_delivery_wiring_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/exrights_price_basis_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/filter_lag_entry_window_selfcheck.py` | offline | PASS | 20s |
| `mike/bin/job_cancel_guard_selfcheck.py` | offline | FAIL(rc=1) | 44s |
| `mike/bin/kb_nightly_backup_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/kb_nightly_ctxbloat_split_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/merge_park_orders_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/bin/mike_json_archive_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/mike_json_has_event_prefix_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/nav_cum_dividend_selfcheck.py` | offline | PASS | 14s |
| `mike/bin/nav_scripts_2account_selfcheck.py` | offline | PASS | 34s |
| `mike/bin/notify_thread_argswap_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/now_injection_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/ops_health_check_rejected_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/ops_health_check_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/order_book_shadow_probe_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/paper_checkpoint_escalation_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/paper_report_render_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/preempt_wakeup_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/preflight_order_invariants_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/report_delivery_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/sector_valuation_lens_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/selfcheck_baseline_diff_selfcheck.py` | offline | PASS | 6s |
| `mike/bin/send_plan_report_park_jit_selfcheck.py` | offline | PASS | 6s |
| `mike/bin/send_plan_report_state_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/signal_holds_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/snapshot_corp_action_selfcheck.py` | offline | PASS | 4s |
| `mike/bin/stop_circuit_breaker_selfcheck.sh` | offline | PASS | 3s |
| `mike/bin/summary_parse_position_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/universe_pit_quality_selfcheck.py` | offline | PASS | 9s |
| `mike/bin/verify_account_snapshot_corp_action_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/verify_account_snapshot_lot_reset_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/verify_finding_bg_job_selfcheck.sh` | offline | PASS | 1s |
| `mike/bin/wags_autofix_postq_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/wags_bus_verdict_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/wags_dispatch_dead_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/wags_verdict_parse_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/wake_debounce_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/wake_thread_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/wakeup_audit_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/wakeup_profile_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/watcher_slow_threshold_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/write_scope_conflict_selfcheck.py` | offline | PASS | 1s |
| `mike_paseo/agents/DollarBill/tools/compute_park_add_selfcheck.py` | offline | PASS | 1s |
| `mike_paseo/agents/Mafee/reconcile_parents_selfcheck.py` | offline | PASS | 0s |
| `mike_paseo/agents/Taylor/anomaly_escalate_selfcheck.py` | offline | PASS | 0s |
| `mike_paseo/agents/Taylor/capit_dd_gate_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike_paseo/agents/Taylor/chase_cap_selfcheck.py` | offline | PASS | 0s |
| `mike_paseo/agents/Taylor/insider_flags_selfcheck.py` | offline | PASS | 1s |
| `mike_paseo/agents/Taylor/research/div_growth_tilt_20260821/selfcheck.py` | offline | PASS | 2s |
| `mike_paseo/agents/Taylor/research/dividend_yield_floor_20260818/selfcheck.py` | offline | PASS | 5s |
| `mike_paseo/agents/Taylor/research/listing_date_exchange_study_20260817/selfcheck_gate.py` | offline | PASS | 0s |
| `mike_paseo/agents/Taylor/research/pump_before_raise_flag_20260817/selfcheck_pump_flag.py` | offline | PASS | 0s |
| `mike_paseo/agents/Taylor/research/serial_capital_raiser_20260817/selfcheck_serial.py` | offline | PASS | 9s |
| `mike_paseo/agents/Taylor/seccap_dyn_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike_paseo/agents/Taylor/universe_freshness_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike_paseo/agents/Winston/freshness_warn_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike_paseo/bin/append_event_selfcheck.py` | offline | PASS | 1s |
| `mike_paseo/bin/approve_plan_with_jit_selfcheck.py` | offline | PASS | 1s |
| `mike_paseo/bin/broker_fill_confirm_selfcheck.py` | offline | PASS | 1s |
| `mike_paseo/bin/build_universe_pit_selfcheck.py` | offline | PASS | 0s |
| `mike_paseo/bin/bus_question_closure_selfcheck.py` | offline | PASS | 1s |
| `mike_paseo/bin/bus_question_housekeeping_selfcheck.py` | offline | PASS | 0s |
| `mike_paseo/bin/check_report_cadence_selfcheck.py` | offline | PASS | 0s |
| `mike_paseo/bin/circuit_expiry_selfcheck.py` | offline | PASS | 1s |
| `mike_paseo/bin/claim_reply_selfcheck.sh` | offline | PASS | 0s |
| `mike_paseo/bin/cli_provider_selfcheck.sh` | offline | PASS | 56s |
| `mike_paseo/bin/code_quality_gate_selfcheck.sh` | offline | PASS | 1s |
| `mike_paseo/bin/commit_collision_gate_selfcheck.py` | offline | PASS | 3s |
| `mike_paseo/bin/compute_active_nav_selfcheck.py` | offline | PASS | 1s |
| `mike_paseo/bin/compute_jit_unpark_selfcheck.py` | offline | PASS | 2s |
| `mike_paseo/bin/compute_park_trim_selfcheck.py` | offline | PASS | 0s |
| `mike_paseo/bin/consolidate_git_scope_selfcheck.py` | offline | PASS | 1s |
| `mike_paseo/bin/corp_action_daily_selfcheck.py` | offline | PASS | 0s |
| `mike_paseo/bin/corp_action_selfcheck.py` | offline | PASS | 0s |
| `mike_paseo/bin/cursor_advance_selfcheck.py` | offline | PASS | 2s |
| `mike_paseo/bin/daily_retro_failcause_selfcheck.sh` | offline | PASS | 0s |
| `mike_paseo/bin/daily_retro_wake_metrics_selfcheck.sh` | offline | FAIL(rc=1) | 0s |
| `mike_paseo/bin/dispatch_discord_topic_selfcheck.sh` | offline | PASS | 45s |
| `mike_paseo/bin/dispatch_question_hint_selfcheck.py` | offline | PASS | 0s |
| `mike_paseo/bin/dispatch_tiny_prompt_selfcheck.sh` | offline | PASS | 3s |
| `mike_paseo/bin/dt5g_publisher_gate_selfcheck.sh` | offline | PASS | 0s |
| `mike_paseo/bin/dt5g_writer_watch_selfcheck.sh` | offline | FAIL(rc=1) | 16s |
| `mike_paseo/bin/due_diligence_corp_flags_selfcheck.py` | offline | PASS | 50s |
| `mike_paseo/bin/eod_delivery_wiring_selfcheck.py` | offline | PASS | 0s |
| `mike_paseo/bin/exrights_price_basis_selfcheck.py` | offline | PASS | 0s |
| `mike_paseo/bin/filter_lag_entry_window_selfcheck.py` | offline | PASS | 20s |
| `mike_paseo/bin/job_cancel_guard_selfcheck.py` | offline | FAIL(rc=1) | 44s |
| `mike_paseo/bin/kb_nightly_backup_selfcheck.py` | offline | PASS | 0s |
| `mike_paseo/bin/kb_nightly_ctxbloat_split_selfcheck.py` | offline | PASS | 1s |
| `mike_paseo/bin/merge_park_orders_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike_paseo/bin/mike_json_archive_selfcheck.py` | offline | PASS | 1s |
| `mike_paseo/bin/mike_json_has_event_prefix_selfcheck.py` | offline | PASS | 0s |
| `mike_paseo/bin/nav_cum_dividend_selfcheck.py` | offline | PASS | 14s |
| `mike_paseo/bin/nav_scripts_2account_selfcheck.py` | offline | PASS | 34s |
| `mike_paseo/bin/notify_thread_argswap_selfcheck.py` | offline | PASS | 1s |
| `mike_paseo/bin/now_injection_selfcheck.sh` | offline | PASS | 0s |
| `mike_paseo/bin/ops_health_check_rejected_selfcheck.py` | offline | PASS | 0s |
| `mike_paseo/bin/ops_health_check_selfcheck.py` | offline | PASS | 1s |
| `mike_paseo/bin/order_book_shadow_probe_selfcheck.py` | offline | PASS | 0s |
| `mike_paseo/bin/paper_checkpoint_escalation_selfcheck.py` | offline | PASS | 0s |
| `mike_paseo/bin/paper_report_render_selfcheck.py` | offline | PASS | 0s |
| `mike_paseo/bin/preempt_wakeup_selfcheck.sh` | offline | PASS | 1s |
| `mike_paseo/bin/preflight_order_invariants_selfcheck.py` | offline | PASS | 0s |
| `mike_paseo/bin/report_delivery_gate_selfcheck.py` | offline | PASS | 0s |
| `mike_paseo/bin/sector_valuation_lens_selfcheck.py` | offline | PASS | 0s |
| `mike_paseo/bin/selfcheck_baseline_diff_selfcheck.py` | offline | PASS | 6s |
| `mike_paseo/bin/send_plan_report_park_jit_selfcheck.py` | offline | PASS | 6s |
| `mike_paseo/bin/send_plan_report_state_gate_selfcheck.py` | offline | PASS | 1s |
| `mike_paseo/bin/signal_holds_selfcheck.py` | offline | PASS | 0s |
| `mike_paseo/bin/snapshot_corp_action_selfcheck.py` | offline | PASS | 4s |
| `mike_paseo/bin/stop_circuit_breaker_selfcheck.sh` | offline | PASS | 3s |
| `mike_paseo/bin/summary_parse_position_selfcheck.sh` | offline | PASS | 0s |
| `mike_paseo/bin/universe_pit_quality_selfcheck.py` | offline | PASS | 8s |
| `mike_paseo/bin/verify_account_snapshot_corp_action_selfcheck.py` | offline | PASS | 1s |
| `mike_paseo/bin/verify_account_snapshot_lot_reset_selfcheck.py` | offline | PASS | 2s |
| `mike_paseo/bin/verify_finding_bg_job_selfcheck.sh` | offline | PASS | 1s |
| `mike_paseo/bin/wags_autofix_postq_selfcheck.py` | offline | PASS | 0s |
| `mike_paseo/bin/wags_bus_verdict_selfcheck.py` | offline | PASS | 1s |
| `mike_paseo/bin/wags_dispatch_dead_selfcheck.py` | offline | PASS | 0s |
| `mike_paseo/bin/wags_verdict_parse_selfcheck.py` | offline | PASS | 0s |
| `mike_paseo/bin/wake_debounce_selfcheck.sh` | offline | PASS | 0s |
| `mike_paseo/bin/wake_thread_selfcheck.py` | offline | PASS | 0s |
| `mike_paseo/bin/wakeup_audit_selfcheck.py` | offline | PASS | 0s |
| `mike_paseo/bin/wakeup_profile_selfcheck.py` | offline | PASS | 1s |
| `mike_paseo/bin/watcher_slow_threshold_selfcheck.py` | offline | PASS | 0s |
| `mike_paseo/bin/write_scope_conflict_selfcheck.py` | offline | PASS | 1s |
| `money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `netting_recon_selfcheck.py` | offline | PASS | 0s |
| `order_book_shadow_selfcheck.py` | offline | PASS | 0s |
| `oshares_wire_selfcheck.py` | offline | PASS | 20s |
| `pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `paper_main_window_selfcheck.py` | offline | PASS | 1s |
| `paper_probe_netting_selfcheck.py` | offline | PASS | 0s |
| `phs_flash_api_selfcheck.py` | offline | PASS | 1s |
| `plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `plan_funding_gate_selfcheck.py` | offline | PASS | 0s |
| `probe_linger_selfcheck.py` | offline | PASS | 3s |
| `quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `refresh_skip_participation_selfcheck.py` | offline | PASS | 1s |
| `restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `route_selector_selfcheck.py` | offline | PASS | 5s |
| `rubber_weekly_selfcheck.py` | offline | PASS | 1s |
| `rule_a_ceiling_selfcheck.py` | offline | PASS | 1s |
| `rule_a_ref_guard_selfcheck.py` | offline | PASS | 0s |
| `sync_cache_lock_selfcheck.py` | offline | PASS | 5s |
| `t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `tbot/code/tests/selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
