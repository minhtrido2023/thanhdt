---
kind: reference
title: Selfcheck registry — snapshot tự sinh, ĐỪNG sửa tay
generated_by: bin/run_selfchecks.sh
generated_at: 2026-09-25T20:44:25Z
---

# Selfcheck registry (auto-generated, ĐỪNG sửa tay — sửa `bin/run_selfchecks.sh`)

Chạy: `bash mike/bin/run_selfchecks.sh [--live]`. Lần gần nhất: 178 PASS / 9 FAIL / 20 SKIP (live).

| File | Tier | Status | Thời gian |
|---|---|---|---|
| `account_overrides_broker_resolution_selfcheck.py` | offline | PASS | 0s |
| `anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 3s |
| `anomaly_gate_selfcheck.py` | offline | PASS | 8s |
| `approval_gate_selfcheck.py` | offline | PASS | 0s |
| `archive/capit_exit_floor_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `basket_price_basis_audit_selfcheck.py` | offline | PASS | 8s |
| `basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `book_tagging_selfcheck.py` | offline | PASS | 1s |
| `brokers_nav_shadow_selfcheck.py` | offline | PASS | 1s |
| `capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `churn_guard_selfcheck.py` | offline | PASS | 2s |
| `concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `custom30_publish_weight_selfcheck.py` | offline | PASS | 1s |
| `custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `dc_book_waterfall_selfcheck.py` | offline | PASS | 0s |
| `dcf_check_selfcheck.py` | offline | PASS | 1s |
| `dcf_refresh_gate_selfcheck.py` | offline | PASS | 0s |
| `dcf_selector_selfcheck.py` | offline | PASS | 2s |
| `discretionary_accumulation_selfcheck.py` | offline | PASS | 11s |
| `discretionary_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `discretionary_target_pct_selfcheck.py` | offline | PASS | 4s |
| `dt5g_chain_freshness_selfcheck.py` | offline | PASS | 0s |
| `due_diligence_selfcheck.py` | offline | PASS | 72s |
| `dynamic_no_chase_ceiling_selfcheck.py` | offline | PASS | 2s |
| `edge_wlag_gate_selfcheck.py` | offline | PASS | 1s |
| `excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `exdate_price_frame_selfcheck.py` | offline | PASS | 0s |
| `expected_volume_pacing_selfcheck.py` | offline | PASS | 24s |
| `expvol_shadow_probe_selfcheck.py` | offline | PASS | 0s |
| `extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `freshness_ops_selfcheck.py` | offline | PASS | 2s |
| `gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `ghost_order_selfcheck.py` | offline | PASS | 4s |
| `hard_no_chase_ceiling_selfcheck.py` | offline | PASS | 9s |
| `hybrid_fill_timing_selfcheck.py` | offline | PASS | 8s |
| `immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `lag_adv_cap_selfcheck.py` | offline | PASS | 1s |
| `lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `lag_governance_order_gate_selfcheck.py` | offline | PASS | 0s |
| `lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `lag_live_schedule_selfcheck.py` | offline | PASS | 23s |
| `lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `lag_rating_order_gate_selfcheck.py` | offline | PASS | 1s |
| `loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/DollarBill/tools/compute_park_add_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Mafee/reconcile_parents_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/anomaly_escalate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/capit_dd_gate_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/chase_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/insider_flags_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/aria_H_20260913/plan_funding_gate_fee_sync_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/div_growth_tilt_20260821/selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/dividend_yield_floor_20260818/selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/listing_date_exchange_study_20260817/selfcheck_gate.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/pump_before_raise_flag_20260817/selfcheck_pump_flag.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/serial_capital_raiser_20260817/selfcheck_serial.py` | offline | FAIL(rc=1) | 9s |
| `mike/agents/Taylor/research/treasury_reconcile_20260917/treasury_adjust_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/treasury_table_20260918/treasury_share_events_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/vn_market_efficiency_20260910/selfcheck_efficiency.py` | offline | PASS | 2s |
| `mike/agents/Taylor/seccap_dyn_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/universe_freshness_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Winston/freshness_warn_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/append_event_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/bin/approve_plan_with_jit_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/backup_freshness_check_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/backup_push_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/broker_fill_confirm_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/build_universe_pit_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/bus_question_closure_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/bus_question_housekeeping_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/check_report_cadence_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/circuit_expiry_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/claim_reply_selfcheck.sh` | offline | PASS | 1s |
| `mike/bin/cli_provider_selfcheck.sh` | offline | PASS | 56s |
| `mike/bin/close_plan_approval_questions_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/bin/code_quality_autodispatch_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/bin/code_quality_gate_selfcheck.sh` | offline | PASS | 1s |
| `mike/bin/code_quality_weekly_scope_selfcheck.sh` | offline | PASS | 1s |
| `mike/bin/commit_collision_gate_selfcheck.py` | offline | PASS | 4s |
| `mike/bin/compute_active_nav_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/compute_jit_unpark_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/compute_park_trim_selfcheck.py` | offline | PASS | 12s |
| `mike/bin/consolidate_git_scope_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/corp_action_auto_confirm_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/corp_action_daily_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/corp_action_feed_canary_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/corp_action_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/cursor_advance_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/daily_nav_snapshot_corpaction_error_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/daily_nav_snapshot_from_raw_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/daily_retro_failcause_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/diagnosis_evidence_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/discretionary_accumulation_inject_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/discretionary_margin_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/dispatch_discord_topic_selfcheck.sh` | offline | PASS | 45s |
| `mike/bin/dispatch_question_hint_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/dispatch_tiny_prompt_selfcheck.sh` | offline | PASS | 3s |
| `mike/bin/dispatch_wc_root_anchor_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/dividend_adjusted_return_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/dt5g_publisher_gate_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/dt5g_writer_watch_selfcheck.sh` | offline | PASS | 16s |
| `mike/bin/due_diligence_corp_flags_selfcheck.py` | offline | PASS | 47s |
| `mike/bin/eod_delivery_wiring_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/eod_trading_report_account_filter_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/exdate_frame_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/exrights_price_basis_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/filter_lag_entry_window_selfcheck.py` | offline | PASS | 20s |
| `mike/bin/forensic_flag_review_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/job_cancel_guard_selfcheck.py` | offline | PASS | 45s |
| `mike/bin/kb_nightly_backup_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/kb_nightly_ctxbloat_split_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/kb_nightly_phase1_atomic_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/merge_park_orders_selfcheck.py` | offline | PASS | 92s |
| `mike/bin/mike_json_archive_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/mike_json_has_event_prefix_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/nav_corpaction_gate_e2e_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/nav_cum_dividend_selfcheck.py` | offline | PASS | 14s |
| `mike/bin/nav_exdate_forecast_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/nav_scripts_2account_selfcheck.py` | offline | PASS | 47s |
| `mike/bin/nav_snapshot_daily_selfcheck.sh` | offline | PASS | 15s |
| `mike/bin/nav_sync_retry_rc_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/notify_thread_argswap_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/now_injection_selfcheck.sh` | offline | PASS | 1s |
| `mike/bin/opening_window_l2_poll_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/ops_health_check_rejected_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/ops_health_check_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/orb_drift_monitor_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/orb_pt_appendonly_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/bin/order_book_shadow_probe_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/paper_checkpoint_escalation_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/paper_corp_action_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/paper_report_render_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/plan_funding_gate_fee_sync_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/preempt_wakeup_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/preflight_order_invariants_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/production_manifest_selfcheck.sh` | offline | FAIL(rc=1) | 20s |
| `mike/bin/reconcile_equity_realized_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/report_delivery_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/report_delivery_ledger_selfcheck.py` | offline | PASS | 5s |
| `mike/bin/report_return_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/rnd_preflight_power_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/sector_valuation_lens_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/selfcheck_baseline_diff_selfcheck.py` | offline | PASS | 6s |
| `mike/bin/send_plan_report_park_jit_selfcheck.py` | offline | PASS | 6s |
| `mike/bin/send_plan_report_state_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/signal_holds_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/snapshot_corp_action_selfcheck.py` | offline | PASS | 6s |
| `mike/bin/stop_circuit_breaker_selfcheck.sh` | offline | PASS | 3s |
| `mike/bin/summary_parse_position_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/treasury_buyback_window_monitor_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/tz_anchor_gate_selfcheck.py` | offline | PASS | 4s |
| `mike/bin/universe_pit_quality_selfcheck.py` | offline | PASS | 7s |
| `mike/bin/vendor_mismatch_alert_selfcheck.sh` | offline | PASS | 12s |
| `mike/bin/verify_account_snapshot_bq_price_date_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/verify_account_snapshot_broker_positions_marketprice_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/verify_account_snapshot_corp_action_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/verify_account_snapshot_lot_reset_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/verify_finding_bg_job_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/wags_arch_review_round2_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/wags_autofix_postq_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/wags_bus_question_pending_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/wags_bus_verdict_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/wags_dispatch_dead_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/wags_verdict_parse_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/wait_for_artifact_selfcheck.py` | offline | PASS | 8s |
| `mike/bin/wake_debounce_selfcheck.sh` | offline | PASS | 1s |
| `mike/bin/wake_thread_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/wakeup_audit_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/wakeup_profile_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/watcher_slow_threshold_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/worktree_stale_check_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/write_scope_conflict_selfcheck.py` | offline | PASS | 1s |
| `money_path_freshness_selfcheck.py` | offline | PASS | 1s |
| `net_offsetting_orders_selfcheck.py` | offline | PASS | 1s |
| `netting_recon_selfcheck.py` | offline | PASS | 0s |
| `order_book_shadow_selfcheck.py` | offline | PASS | 0s |
| `oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `oshares_wire_selfcheck.py` | offline | PASS | 20s |
| `pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `paper_probe_netting_selfcheck.py` | offline | PASS | 0s |
| `phs_flash_api_selfcheck.py` | offline | PASS | 1s |
| `plan_cash_commitment_selfcheck.py` | offline | PASS | 1s |
| `plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `plan_funding_gate_selfcheck.py` | offline | PASS | 0s |
| `probe_linger_selfcheck.py` | offline | PASS | 7s |
| `quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `route_selector_selfcheck.py` | offline | PASS | 4s |
| `rubber_weekly_selfcheck.py` | offline | PASS | 1s |
| `rule_a_ceiling_selfcheck.py` | offline | PASS | 1s |
| `rule_a_ref_guard_selfcheck.py` | offline | PASS | 0s |
| `sync_cache_lock_selfcheck.py` | offline | PASS | 6s |
| `t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `tbot/code/tests/selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
