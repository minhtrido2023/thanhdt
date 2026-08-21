---
kind: reference
title: Selfcheck registry — snapshot tự sinh, ĐỪNG sửa tay
generated_by: bin/run_selfchecks.sh
generated_at: 2026-08-21T21:33:56Z
---

# Selfcheck registry (auto-generated, ĐỪNG sửa tay — sửa `bin/run_selfchecks.sh`)

Chạy: `bash mike/bin/run_selfchecks.sh [--live]`. Lần gần nhất: 179 PASS / 35 FAIL / 22 SKIP (live).

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
| `capit_participation_cap_selfcheck.py` | offline | PASS | 1s |
| `cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `churn_guard_selfcheck.py` | offline | PASS | 1s |
| `concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `custom30_publish_weight_selfcheck.py` | offline | PASS | 1s |
| `custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `dc_book_waterfall_selfcheck.py` | offline | PASS | 0s |
| `dcf_check_selfcheck.py` | offline | PASS | 1s |
| `dcf_refresh_gate_selfcheck.py` | offline | PASS | 0s |
| `dcf_selector_selfcheck.py` | offline | PASS | 2s |
| `discretionary_accumulation_selfcheck.py` | offline | PASS | 0s |
| `discretionary_participation_cap_selfcheck.py` | offline | PASS | 1s |
| `discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `discretionary_target_pct_selfcheck.py` | offline | PASS | 0s |
| `dt5g_chain_freshness_selfcheck.py` | offline | PASS | 0s |
| `due_diligence_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `dynamic_no_chase_ceiling_selfcheck.py` | offline | PASS | 1s |
| `edge_wlag_gate_selfcheck.py` | offline | PASS | 1s |
| `excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `exdate_price_frame_selfcheck.py` | offline | PASS | 0s |
| `expected_volume_pacing_selfcheck.py` | offline | PASS | 7s |
| `expvol_shadow_probe_selfcheck.py` | offline | PASS | 0s |
| `extreme_regime_selfcheck.py` | offline | PASS | 1s |
| `eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `freshness_ops_selfcheck.py` | offline | PASS | 2s |
| `gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `ghost_order_selfcheck.py` | offline | PASS | 1s |
| `hard_no_chase_ceiling_selfcheck.py` | offline | PASS | 3s |
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
| `mike/.claude/worktrees/wags-fix-coord-08-19/agents/DollarBill/tools/compute_park_add_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/agents/Mafee/reconcile_parents_selfcheck.py` | offline | PASS | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/agents/Taylor/anomaly_escalate_selfcheck.py` | offline | PASS | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/agents/Taylor/capit_dd_gate_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/.claude/worktrees/wags-fix-coord-08-19/agents/Taylor/chase_cap_selfcheck.py` | offline | PASS | 1s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/agents/Taylor/insider_flags_selfcheck.py` | offline | PASS | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/agents/Taylor/research/dividend_yield_floor_20260818/selfcheck.py` | offline | PASS | 5s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/agents/Taylor/research/listing_date_exchange_study_20260817/selfcheck_gate.py` | offline | PASS | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/agents/Taylor/research/pump_before_raise_flag_20260817/selfcheck_pump_flag.py` | offline | PASS | 1s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/agents/Taylor/research/serial_capital_raiser_20260817/selfcheck_serial.py` | offline | PASS | 8s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/agents/Taylor/seccap_dyn_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/.claude/worktrees/wags-fix-coord-08-19/agents/Taylor/universe_freshness_selfcheck.py` | offline | PASS | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/agents/Winston/freshness_warn_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/append_event_selfcheck.py` | offline | PASS | 2s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/approve_plan_with_jit_selfcheck.py` | offline | PASS | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/broker_fill_confirm_selfcheck.py` | offline | PASS | 1s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/build_universe_pit_selfcheck.py` | offline | PASS | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/bus_question_closure_selfcheck.py` | offline | PASS | 1s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/bus_question_housekeeping_selfcheck.py` | offline | PASS | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/check_report_cadence_selfcheck.py` | offline | PASS | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/circuit_expiry_selfcheck.py` | offline | PASS | 1s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/claim_reply_selfcheck.sh` | offline | PASS | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/cli_provider_selfcheck.sh` | offline | PASS | 56s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/commit_collision_gate_selfcheck.py` | offline | FAIL(rc=1) | 3s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/compute_active_nav_selfcheck.py` | offline | PASS | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/compute_jit_unpark_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/compute_park_trim_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/consolidate_git_scope_selfcheck.py` | offline | PASS | 1s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/corp_action_daily_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/corp_action_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/cursor_advance_selfcheck.py` | offline | PASS | 2s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/dispatch_discord_topic_selfcheck.sh` | offline | PASS | 45s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/dispatch_question_hint_selfcheck.py` | offline | PASS | 1s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/dispatch_wake_selfcheck.sh` | offline | PASS | 28s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/dt5g_publisher_gate_selfcheck.sh` | offline | FAIL(rc=1) | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/dt5g_writer_watch_selfcheck.sh` | offline | FAIL(rc=1) | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/due_diligence_corp_flags_selfcheck.py` | offline | PASS | 43s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/eod_delivery_wiring_selfcheck.py` | offline | PASS | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/exrights_price_basis_selfcheck.py` | offline | PASS | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/filter_lag_entry_window_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/job_cancel_guard_selfcheck.py` | offline | FAIL(rc=1) | 44s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/kb_nightly_backup_selfcheck.py` | offline | PASS | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/kb_nightly_ctxbloat_split_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/merge_park_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/mike_json_archive_selfcheck.py` | offline | PASS | 1s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/mike_json_has_event_prefix_selfcheck.py` | offline | PASS | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/nav_cum_dividend_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/nav_scripts_2account_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/notify_thread_argswap_selfcheck.py` | offline | PASS | 1s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/ops_health_check_rejected_selfcheck.py` | offline | PASS | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/ops_health_check_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/order_book_shadow_probe_selfcheck.py` | offline | PASS | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/paper_checkpoint_escalation_selfcheck.py` | offline | PASS | 1s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/paper_report_render_selfcheck.py` | offline | PASS | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/preflight_order_invariants_selfcheck.py` | offline | PASS | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/report_delivery_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/run_selfchecks.sh` | live | SKIP(--live để chạy) | - |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/sector_valuation_lens_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/selfcheck_baseline_diff.py` | offline | FAIL(rc=1) | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/selfcheck_baseline_diff_selfcheck.py` | offline | FAIL(rc=1) | 6s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/selfcheck_scope_map.sh` | offline | PASS | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/selfcheck_weekly_baseline_check.sh` | offline | FAIL(rc=124) | 1409s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/send_plan_report_park_jit_selfcheck.py` | offline | PASS | 6s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/send_plan_report_state_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/snapshot_corp_action_selfcheck.py` | offline | PASS | 4s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/universe_pit_quality_selfcheck.py` | offline | PASS | 10s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/verify_account_snapshot_corp_action_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/verify_account_snapshot_lot_reset_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/wags_autofix_postq_selfcheck.py` | offline | PASS | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/wags_bus_verdict_selfcheck.py` | offline | PASS | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/wags_dispatch_dead_selfcheck.py` | offline | PASS | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/wags_verdict_parse_selfcheck.py` | offline | PASS | 1s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/wake_thread_selfcheck.py` | offline | PASS | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/wakeup_audit_selfcheck.py` | offline | PASS | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/wakeup_profile_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/watcher_slow_threshold_selfcheck.py` | offline | PASS | 0s |
| `mike/.claude/worktrees/wags-fix-coord-08-19/bin/write_scope_conflict_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/DollarBill/tools/compute_park_add_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Mafee/reconcile_parents_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/anomaly_escalate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/capit_dd_gate_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/chase_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/insider_flags_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/div_growth_tilt_20260821/selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/dividend_yield_floor_20260818/selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/listing_date_exchange_study_20260817/selfcheck_gate.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/pump_before_raise_flag_20260817/selfcheck_pump_flag.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/serial_capital_raiser_20260817/selfcheck_serial.py` | offline | PASS | 7s |
| `mike/agents/Taylor/seccap_dyn_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/universe_freshness_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Winston/freshness_warn_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/bin/append_event_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/approve_plan_with_jit_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/broker_fill_confirm_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/build_universe_pit_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/bus_question_closure_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/bus_question_housekeeping_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/check_report_cadence_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/circuit_expiry_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/claim_reply_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/cli_provider_selfcheck.sh` | offline | PASS | 56s |
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
| `mike/bin/dispatch_discord_topic_selfcheck.sh` | offline | PASS | 45s |
| `mike/bin/dispatch_question_hint_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/dispatch_tiny_prompt_selfcheck.sh` | offline | PASS | 2s |
| `mike/bin/dt5g_publisher_gate_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/dt5g_writer_watch_selfcheck.sh` | offline | PASS | 16s |
| `mike/bin/due_diligence_corp_flags_selfcheck.py` | offline | PASS | 45s |
| `mike/bin/eod_delivery_wiring_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/exrights_price_basis_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/filter_lag_entry_window_selfcheck.py` | offline | PASS | 19s |
| `mike/bin/job_cancel_guard_selfcheck.py` | offline | FAIL(rc=1) | 44s |
| `mike/bin/kb_nightly_backup_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/kb_nightly_ctxbloat_split_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/merge_park_orders_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/bin/mike_json_archive_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/mike_json_has_event_prefix_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/nav_cum_dividend_selfcheck.py` | offline | PASS | 14s |
| `mike/bin/nav_scripts_2account_selfcheck.py` | offline | PASS | 33s |
| `mike/bin/notify_thread_argswap_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/bin/now_injection_selfcheck.sh` | offline | FAIL(rc=1) | 0s |
| `mike/bin/ops_health_check_rejected_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/ops_health_check_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/bin/order_book_shadow_probe_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/paper_checkpoint_escalation_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/paper_report_render_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/preflight_order_invariants_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/report_delivery_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/run_selfchecks.sh` | live | SKIP(--live để chạy) | - |
| `mike/bin/sector_valuation_lens_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/selfcheck_baseline_diff.py` | offline | FAIL(rc=1) | 0s |
| `mike/bin/selfcheck_baseline_diff_selfcheck.py` | offline | PASS | 6s |
| `mike/bin/selfcheck_scope_map.sh` | offline | PASS | 0s |
| `mike/bin/selfcheck_weekly_baseline_check.sh` | offline | FAIL(rc=124) | 1579s |
| `mike/bin/send_plan_report_park_jit_selfcheck.py` | offline | PASS | 5s |
| `mike/bin/send_plan_report_state_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/signal_holds_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/snapshot_corp_action_selfcheck.py` | offline | PASS | 4s |
| `mike/bin/stop_circuit_breaker_selfcheck.sh` | offline | PASS | 3s |
| `mike/bin/universe_pit_quality_selfcheck.py` | offline | PASS | 9s |
| `mike/bin/verify_account_snapshot_corp_action_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/verify_account_snapshot_lot_reset_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/verify_finding_bg_job_selfcheck.sh` | offline | PASS | 1s |
| `mike/bin/wags_autofix_postq_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/wags_bus_verdict_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/wags_dispatch_dead_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/wags_verdict_parse_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/wake_debounce_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/wake_thread_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/wakeup_audit_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/wakeup_profile_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/watcher_slow_threshold_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/write_scope_conflict_selfcheck.py` | offline | PASS | 1s |
| `money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `netting_recon_selfcheck.py` | offline | PASS | 0s |
| `order_book_shadow_selfcheck.py` | offline | PASS | 0s |
| `oshares_wire_selfcheck.py` | offline | PASS | 20s |
| `pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `paper_main_window_selfcheck.py` | offline | PASS | 1s |
| `paper_probe_netting_selfcheck.py` | offline | PASS | 0s |
| `phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `plan_cash_commitment_selfcheck.py` | offline | PASS | 1s |
| `plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `plan_funding_gate_selfcheck.py` | offline | PASS | 0s |
| `probe_linger_selfcheck.py` | offline | PASS | 2s |
| `quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `refresh_skip_participation_selfcheck.py` | offline | PASS | 2s |
| `restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `route_selector_selfcheck.py` | offline | PASS | 4s |
| `rubber_weekly_selfcheck.py` | offline | PASS | 2s |
| `rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `rule_a_ref_guard_selfcheck.py` | offline | PASS | 0s |
| `sync_cache_lock_selfcheck.py` | offline | PASS | 6s |
| `t2_settlement_selfcheck.py` | offline | PASS | 0s |
| `tbot/code/tests/selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
