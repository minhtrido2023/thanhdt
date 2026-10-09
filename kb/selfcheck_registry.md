---
kind: reference
title: Selfcheck registry — snapshot tự sinh, ĐỪNG sửa tay
generated_by: bin/run_selfchecks.sh
generated_at: 2026-10-09T20:52:17Z
---

# Selfcheck registry (auto-generated, ĐỪNG sửa tay — sửa `bin/run_selfchecks.sh`)

Chạy: `bash mike/bin/run_selfchecks.sh [--live]`. Lần gần nhất: 240 PASS / 11 FAIL / 25 SKIP (live).

| File | Tier | Status | Thời gian |
|---|---|---|---|
| `account_overrides_broker_resolution_selfcheck.py` | offline | PASS | 0s |
| `anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 3s |
| `anomaly_gate_selfcheck.py` | offline | PASS | 7s |
| `approval_gate_selfcheck.py` | offline | PASS | 0s |
| `archive/capit_exit_floor_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `atc_cancel_overorder_selfcheck.py` | offline | PASS | 0s |
| `atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 12s |
| `basket_price_basis_audit_selfcheck.py` | offline | PASS | 8s |
| `basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `book_tagging_selfcheck.py` | offline | PASS | 1s |
| `brokers_cash_fields_selfcheck.py` | offline | PASS | 0s |
| `brokers_nav_shadow_selfcheck.py` | offline | PASS | 1s |
| `brokers_tradequantity_selfcheck.py` | offline | PASS | 0s |
| `capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `cctg6m_series_selfcheck.py` | offline | PASS | 0s |
| `cctg_deposit_wiring_selfcheck.py` | offline | PASS | 9s |
| `cctg_overlay_selfcheck.py` | offline | PASS | 1s |
| `churn_guard_selfcheck.py` | offline | PASS | 2s |
| `close_repair_selfcheck.py` | offline | PASS | 0s |
| `concurrent_lock_selfcheck.py` | offline | PASS | 1s |
| `cpi_vn_tier15_selfcheck.py` | offline | PASS | 2s |
| `cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 0s |
| `custom30_publish_guard_selfcheck.py` | offline | PASS | 0s |
| `custom30_publish_weight_selfcheck.py` | offline | PASS | 0s |
| `custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `custom_basket_forensic_failclosed_selfcheck.py` | offline | PASS | 1s |
| `dc_book_waterfall_selfcheck.py` | offline | PASS | 0s |
| `dcf_check_selfcheck.py` | offline | PASS | 1s |
| `dcf_refresh_gate_selfcheck.py` | offline | PASS | 0s |
| `dcf_selector_selfcheck.py` | offline | PASS | 2s |
| `discretionary_accumulation_selfcheck.py` | offline | PASS | 14s |
| `discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `discretionary_target_pct_selfcheck.py` | offline | PASS | 5s |
| `dna_report_killswitch_line_selfcheck.py` | offline | PASS | 1s |
| `dot2_batch_selfcheck.py` | offline | PASS | 0s |
| `dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `dt5g_chain_freshness_selfcheck.py` | offline | PASS | 1s |
| `due_diligence_selfcheck.py` | offline | PASS | 71s |
| `dynamic_no_chase_ceiling_selfcheck.py` | offline | PASS | 2s |
| `edge_wlag_gate_selfcheck.py` | offline | PASS | 1s |
| `excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `exdate_price_frame_selfcheck.py` | offline | PASS | 0s |
| `expected_volume_pacing_selfcheck.py` | offline | PASS | 25s |
| `expvol_shadow_probe_selfcheck.py` | offline | PASS | 0s |
| `extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `failc_residual_selfcheck.py` | offline | PASS | 2s |
| `failc_sweep8_selfcheck.py` | offline | PASS | 1s |
| `failopen_failclosed_selfcheck.py` | offline | PASS | 0s |
| `failopen_telegram_refresh_selfcheck.py` | offline | PASS | 0s |
| `freshness_ops_selfcheck.py` | offline | PASS | 3s |
| `gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `ghost_order_selfcheck.py` | offline | PASS | 4s |
| `hard_no_chase_ceiling_selfcheck.py` | offline | PASS | 9s |
| `hybrid_fill_timing_selfcheck.py` | offline | PASS | 8s |
| `idle_rate_proxy_selfcheck.py` | offline | PASS | 1s |
| `immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `lag_adv_cap_selfcheck.py` | offline | PASS | 0s |
| `lag_forensic_filter_selfcheck.py` | offline | PASS | 1s |
| `lag_governance_order_gate_selfcheck.py` | offline | PASS | 0s |
| `lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `lag_live_schedule_selfcheck.py` | offline | PASS | 22s |
| `lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `lag_rating_order_gate_selfcheck.py` | offline | PASS | 1s |
| `loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `logto_silent_defaults_selfcheck.py` | offline | PASS | 0s |
| `macro_killswitch_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/DollarBill/tools/compute_park_add_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Mafee/reconcile_parents_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/anomaly_escalate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/capit_dd_gate_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/chase_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/insider_flags_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/aria_H_20260913/plan_funding_gate_fee_sync_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/basket_ca_pin_20260927/pin_resolution_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/c30v_position_replay_20260927/run_selfcheck.sh` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/c30v_position_replay_20260927/run_selfcheck_finish.sh` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/c30v_position_replay_20260927/selfcheck_replay.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/div_growth_tilt_20260821/selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/dividend_yield_floor_20260818/selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/listing_date_exchange_study_20260817/selfcheck_gate.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/pump_before_raise_flag_20260817/selfcheck_pump_flag.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/serial_capital_raiser_20260817/selfcheck_serial.py` | offline | FAIL(rc=1) | 9s |
| `mike/agents/Taylor/research/treasury_reconcile_20260917/treasury_adjust_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/treasury_table_20260918/treasury_share_events_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/vn_market_efficiency_20260910/selfcheck_efficiency.py` | offline | PASS | 1s |
| `mike/agents/Taylor/seccap_dyn_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/universe_freshness_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Winston/freshness_warn_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/adjfactor_drift_detect_selfcheck.py` | offline | PASS | 32s |
| `mike/bin/annualization_basis_selfcheck.py` | offline | FAIL(rc=1) | 28s |
| `mike/bin/append_event_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/approve_plan_with_jit_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/asof_label_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/auto_exit_inject_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/backup_freshness_check_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/backup_push_selfcheck.sh` | offline | PASS | 1s |
| `mike/bin/bq_freshness_check_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/bin/bq_price_freeze_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/broker_fill_confirm_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/build_universe_pit_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/bus_question_closure_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/bus_question_housekeeping_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/check_report_cadence_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/circuit_expiry_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/claim_reply_selfcheck.sh` | offline | PASS | 1s |
| `mike/bin/cli_provider_selfcheck.sh` | offline | PASS | 58s |
| `mike/bin/close_plan_approval_questions_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/code_quality_autodispatch_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/bin/code_quality_gate_selfcheck.sh` | offline | PASS | 1s |
| `mike/bin/code_quality_weekly_scope_selfcheck.sh` | offline | PASS | 2s |
| `mike/bin/commit_collision_gate_selfcheck.py` | offline | PASS | 4s |
| `mike/bin/compute_active_nav_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/compute_jit_unpark_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/compute_park_trim_selfcheck.py` | offline | PASS | 13s |
| `mike/bin/consolidate_git_scope_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/corp_action_auto_confirm_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/corp_action_broker_detect_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/corp_action_daily_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/corp_action_feed_canary_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/corp_action_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/corp_actions_verify_cashleg_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/cursor_advance_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/daily_nav_snapshot_corpaction_error_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/daily_nav_snapshot_from_raw_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/daily_retro_failcause_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/diagnosis_evidence_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/discretionary_accumulation_inject_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/discretionary_candidate_funnel_selfcheck.py` | offline | PASS | 4s |
| `mike/bin/discretionary_margin_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/dispatch_discord_topic_selfcheck.sh` | offline | PASS | 46s |
| `mike/bin/dispatch_loop_hint_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/dispatch_question_hint_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/dispatch_round_cap_selfcheck.py` | offline | PASS | 11s |
| `mike/bin/dispatch_tiny_prompt_selfcheck.sh` | offline | PASS | 3s |
| `mike/bin/dispatch_token_telemetry_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/bin/dispatch_wc_root_anchor_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/dividend_adjusted_return_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/dt5g_publisher_gate_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/dt5g_writer_watch_selfcheck.sh` | offline | PASS | 15s |
| `mike/bin/due_diligence_corp_flags_selfcheck.py` | offline | PASS | 50s |
| `mike/bin/eod_delivery_wiring_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/eod_trading_report_account_filter_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/exdate_frame_cashleg_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/exdate_frame_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/exrights_price_basis_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/failopen_batch1_selfcheck.py` | offline | PASS | 12s |
| `mike/bin/filter_lag_entry_window_selfcheck.py` | offline | PASS | 19s |
| `mike/bin/forensic_flag_review_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/github_pat_expiry_check_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/intraday_price_watch_selfcheck.py` | offline | PASS | 14s |
| `mike/bin/job_cancel_guard_selfcheck.py` | offline | PASS | 44s |
| `mike/bin/kb_hot_size_gate_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/kb_nightly_backup_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/kb_nightly_ctxbloat_split_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/kb_nightly_phase1_atomic_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/merge_park_orders_selfcheck.py` | offline | PASS | 91s |
| `mike/bin/mike_json_archive_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/mike_json_has_event_prefix_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/nav_corpaction_gate_e2e_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/nav_cum_dividend_selfcheck.py` | offline | PASS | 14s |
| `mike/bin/nav_exdate_forecast_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/nav_flow_term_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/nav_jump_flow_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/nav_scripts_2account_selfcheck.py` | offline | FAIL(rc=1) | 41s |
| `mike/bin/nav_snapshot_daily_selfcheck.sh` | offline | PASS | 15s |
| `mike/bin/nav_sync_retry_rc_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/notify_thread_argswap_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/now_injection_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/oddlot_full_exit_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/opening_window_l2_poll_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/ops_health_check_autofix_dryrun_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/ops_health_check_rejected_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/ops_health_check_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/orb_drift_monitor_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/orb_pt_appendonly_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/bin/order_book_shadow_probe_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/paper_checkpoint_escalation_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/paper_corp_action_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/paper_report_render_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/park_chain_alert_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/park_rail_consistency_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/plan_funding_gate_fee_sync_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/plan_position_drift_check_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/bin/portfolio_status_selfcheck.py` | offline | PASS | 8s |
| `mike/bin/preempt_wakeup_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/preflight_order_invariants_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/production_manifest_selfcheck.sh` | offline | PASS | 29s |
| `mike/bin/question_commit_hint_selfcheck.py` | offline | PASS | 7s |
| `mike/bin/reconcile_equity_egg_selfcheck.py` | offline | PASS | 23s |
| `mike/bin/reconcile_equity_realized_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/report_delivery_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/report_delivery_ledger_selfcheck.py` | offline | PASS | 5s |
| `mike/bin/report_return_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/retro_escalate_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/rnd_preflight_power_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/runonce_label_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/sector_valuation_lens_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/selfcheck_baseline_diff_selfcheck.py` | offline | PASS | 6s |
| `mike/bin/selfcheck_red_owner_sweep.sh` | offline | PASS | 3s |
| `mike/bin/send_plan_report_aei_notes_selfcheck.py` | offline | PASS | 5s |
| `mike/bin/send_plan_report_park_jit_selfcheck.py` | offline | PASS | 13s |
| `mike/bin/send_plan_report_state_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/signal_holds_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/snapshot_corp_action_selfcheck.py` | offline | PASS | 6s |
| `mike/bin/stop_circuit_breaker_selfcheck.sh` | offline | PASS | 3s |
| `mike/bin/summary_parse_position_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/treasury_buyback_window_monitor_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/tz_anchor_gate_selfcheck.py` | offline | PASS | 5s |
| `mike/bin/universe_pit_quality_selfcheck.py` | offline | PASS | 7s |
| `mike/bin/vendor_mismatch_alert_selfcheck.sh` | offline | PASS | 13s |
| `mike/bin/verify_account_snapshot_bq_price_date_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/verify_account_snapshot_broker_positions_marketprice_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/verify_account_snapshot_corp_action_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/verify_account_snapshot_lot_reset_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/verify_finding_bg_job_selfcheck.sh` | offline | PASS | 1s |
| `mike/bin/wags_arch_review_round2_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/wags_autofix_postq_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/wags_bus_question_pending_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/wags_bus_verdict_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/wags_dispatch_dead_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/wags_verdict_parse_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/wait_for_artifact_selfcheck.py` | offline | PASS | 8s |
| `mike/bin/wake_debounce_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/wake_thread_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/wakeup_audit_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/wakeup_profile_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/watcher_slow_threshold_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/worktree_stale_check_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/write_scope_conflict_selfcheck.py` | offline | PASS | 1s |
| `money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `navbasis_loud_selfcheck.py` | offline | PASS | 1s |
| `net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `netting_recon_selfcheck.py` | offline | PASS | 0s |
| `order_book_shadow_selfcheck.py` | offline | PASS | 0s |
| `oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `oshares_wire_selfcheck.py` | offline | PASS | 20s |
| `pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `paper_probe_netting_selfcheck.py` | offline | PASS | 0s |
| `phs_flash_api_selfcheck.py` | offline | PASS | 1s |
| `plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `plan_funding_gate_selfcheck.py` | offline | PASS | 9s |
| `planpy_failopen_selfcheck.py` | offline | PASS | 0s |
| `probe_linger_selfcheck.py` | offline | PASS | 8s |
| `quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `rating8l_icb_pit_selfcheck.py` | offline | PASS | 1s |
| `rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 36s |
| `refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 1s |
| `refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `route_selector_selfcheck.py` | offline | PASS | 4s |
| `rubber_weekly_selfcheck.py` | offline | PASS | 2s |
| `rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `sbv_policy_verify_selfcheck.py` | offline | PASS | 5s |
| `screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `sell_loan_package_selfcheck.py` | offline | PASS | 1s |
| `sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `sync_cache_lock_selfcheck.py` | offline | PASS | 5s |
| `t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `tbot/code/tests/selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
