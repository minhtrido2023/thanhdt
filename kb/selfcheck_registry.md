---
kind: reference
title: Selfcheck registry — snapshot tự sinh, ĐỪNG sửa tay
generated_by: bin/run_selfchecks.sh
generated_at: 2026-11-14T07:52:25Z
---

# Selfcheck registry (auto-generated, ĐỪNG sửa tay — sửa `bin/run_selfchecks.sh`)

Chạy: `bash mike/bin/run_selfchecks.sh [--live]`. Lần gần nhất: 3806 PASS / 1298 FAIL / 1057 SKIP (live).

| File | Tier | Status | Thời gian |
|---|---|---|---|
| `account_overrides_broker_resolution_selfcheck.py` | offline | PASS | 0s |
| `anomaly_gate_freshness_session_selfcheck.py` | offline | PASS | 0s |
| `anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 3s |
| `anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `approval_gate_selfcheck.py` | offline | PASS | 0s |
| `atc_cancel_overorder_selfcheck.py` | offline | PASS | 0s |
| `atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 13s |
| `basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `book_tagging_selfcheck.py` | offline | PASS | 1s |
| `brokers_cash_fields_selfcheck.py` | offline | PASS | 0s |
| `brokers_nav_shadow_selfcheck.py` | offline | PASS | 0s |
| `brokers_tradequantity_selfcheck.py` | offline | PASS | 0s |
| `capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `cctg6m_series_selfcheck.py` | offline | PASS | 0s |
| `cctg_deposit_asof_ict_selfcheck.py` | offline | PASS | 3s |
| `cctg_deposit_wiring_selfcheck.py` | offline | PASS | 4s |
| `cctg_overlay_selfcheck.py` | offline | PASS | 1s |
| `cctg_tier2_series_selfcheck.py` | offline | PASS | 12s |
| `churn_guard_selfcheck.py` | offline | PASS | 2s |
| `close_repair_selfcheck.py` | offline | PASS | 1s |
| `concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `cpi_vn_te_selfcheck.py` | offline | PASS | 0s |
| `cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=124) | 61s |
| `cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 0s |
| `cq_hardcore_20261108_selfcheck.py` | offline | PASS | 0s |
| `custom30_publish_guard_selfcheck.py` | offline | PASS | 0s |
| `custom30_publish_weight_selfcheck.py` | offline | PASS | 1s |
| `custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `custom_basket_forensic_failclosed_selfcheck.py` | offline | PASS | 0s |
| `daily_refresh_morning_selfcheck.sh` | offline | PASS | 1s |
| `dc_book_waterfall_selfcheck.py` | offline | PASS | 0s |
| `dcf_check_selfcheck.py` | offline | PASS | 1s |
| `dcf_rate_display_selfcheck.py` | offline | PASS | 0s |
| `dcf_rate_frame_selfcheck.py` | offline | PASS | 27s |
| `dcf_refresh_gate_selfcheck.py` | offline | PASS | 0s |
| `dcf_rstar_refresh_selfcheck.py` | offline | PASS | 1s |
| `dcf_season_selfcheck.py` | offline | PASS | 5s |
| `dcf_selector_selfcheck.py` | offline | PASS | 2s |
| `dd_flag_order_gate_selfcheck.py` | offline | PASS | 0s |
| `deposit_fallback_direction_selfcheck.py` | offline | PASS | 178s |
| `discretionary_accumulation_selfcheck.py` | offline | PASS | 20s |
| `discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `discretionary_target_pct_selfcheck.py` | offline | PASS | 7s |
| `dna_report_killswitch_line_selfcheck.py` | offline | PASS | 0s |
| `dna_report_liquidity_line_selfcheck.py` | offline | PASS | 1s |
| `dot2_batch_selfcheck.py` | offline | PASS | 0s |
| `dsr_family_manifest_selfcheck.py` | offline | PASS | 27s |
| `dt5g_chain_freshness_selfcheck.py` | offline | PASS | 21s |
| `due_diligence_selfcheck.py` | offline | PASS | 86s |
| `dynamic_no_chase_ceiling_selfcheck.py` | offline | PASS | 2s |
| `edge_wlag_gate_selfcheck.py` | offline | PASS | 23s |
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
| `fetch_bdi_daily_selfcheck.py` | offline | PASS | 1s |
| `freshness_ops_selfcheck.py` | offline | PASS | 2s |
| `gdkhq_rollout_selfcheck.py` | offline | PASS | 1s |
| `ghost_order_selfcheck.py` | offline | PASS | 3s |
| `hard_no_chase_ceiling_selfcheck.py` | offline | PASS | 10s |
| `hybrid_fill_timing_selfcheck.py` | offline | PASS | 8s |
| `idle_cash_age_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `idle_rate_proxy_selfcheck.py` | offline | PASS | 2s |
| `immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `lag_adv_basis_selfcheck.py` | offline | PASS | 1s |
| `lag_adv_cap_selfcheck.py` | offline | PASS | 0s |
| `lag_dd_zone_gate_selfcheck.py` | offline | PASS | 2s |
| `lag_forensic_filter_selfcheck.py` | offline | PASS | 1s |
| `lag_governance_order_gate_selfcheck.py` | offline | PASS | 0s |
| `lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `lag_live_schedule_selfcheck.py` | offline | PASS | 23s |
| `lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `lag_rating_gate_snapshot_selfcheck.py` | offline | PASS | 56s |
| `lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `lag_rating_stale_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `lagged_cache_adjusted_selfcheck.py` | offline | PASS | 9s |
| `loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `logto_silent_defaults_selfcheck.py` | offline | PASS | 0s |
| `macro_gate_health_tz_selfcheck.py` | offline | PASS | 1s |
| `macro_healthcheck_sbv_reconfirm_selfcheck.py` | offline | PASS | 5s |
| `macro_killswitch_a_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/DollarBill/tools/compute_park_add_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Mafee/reconcile_parents_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/anomaly_escalate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/capit_dd_gate_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/chase_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/insider_flags_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/aria_H_20260913/plan_funding_gate_fee_sync_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/basket_ca_pin_20260927/pin_resolution_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/c30v_position_replay_20260927/run_selfcheck.sh` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/c30v_position_replay_20260927/run_selfcheck_finish.sh` | offline | FAIL(rc=124) | 61s |
| `mike/agents/Taylor/research/c30v_position_replay_20260927/selfcheck_replay.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/corp_action_program_20260815/selfcheck_sprint1.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/corp_action_program_20260815/selfcheck_sprint2.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/corp_action_program_20260815/selfcheck_sprint3.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/corp_action_program_20260815/selfcheck_sprint4.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/dcf_expectation_lens_20261101/implied_and_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/dcf_level_rerun_20261102/selfcheck_live.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/dcf_rate_proxy_20261102/selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/dcf_rate_proxy_20261102/selfcheck_tz.sh` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/dd_fwd_prelock_20261111/calc/selfcheck_forward.sh` | offline | PASS | 2s |
| `mike/agents/Taylor/research/dd_redo_20261105/_common_g2/selfcheck_g2.sh` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/dd_redo_20261105/_common_g2r2/selfcheck_r2.sh` | offline | PASS | 6s |
| `mike/agents/Taylor/research/div_growth_tilt_20260821/selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/dividend_yield_floor_20260818/selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/firm_behavior_fingerprint_20261016/selfcheck_spot.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/lag_bal_discriminators_20261025/selfcheck_hand.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/liquidity_spread_deposit_lead_20261105/selfcheck.sh` | offline | PASS | 9s |
| `mike/agents/Taylor/research/listing_date_exchange_study_20260817/selfcheck_gate.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/account_overrides_broker_resolution_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/anomaly_gate_freshness_session_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/atc_cancel_overorder_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/brokers_tradequantity_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/cctg6m_series_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/cctg_deposit_asof_ict_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/cctg_deposit_wiring_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/cctg_overlay_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/cctg_tier2_series_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/churn_guard_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/close_repair_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/cpi_vn_te_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/cq_hardcore_20261108_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/custom30_publish_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/custom30_publish_weight_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/custom_basket_forensic_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/daily_refresh_morning_selfcheck.sh` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/dc_book_waterfall_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/dcf_rate_display_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/dcf_rate_frame_selfcheck.py` | offline | PASS | 28s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/dcf_refresh_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/dcf_rstar_refresh_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/dcf_season_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/dcf_selector_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/dd_flag_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/deposit_fallback_direction_selfcheck.py` | offline | FAIL(rc=1) | 10s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/dna_report_killswitch_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/dna_report_liquidity_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/dot2_batch_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/dsr_family_manifest_selfcheck.py` | offline | PASS | 27s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/edge_wlag_gate_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/expected_volume_pacing_selfcheck.py` | offline | PASS | 25s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/failc_residual_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/failc_sweep8_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/failopen_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/failopen_telegram_refresh_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/fetch_bdi_daily_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/freshness_ops_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/hybrid_fill_timing_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/idle_rate_proxy_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/lag_adv_basis_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/lag_adv_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/lag_dd_zone_gate_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/lag_governance_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/lag_live_schedule_selfcheck.py` | offline | PASS | 23s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/lag_rating_gate_snapshot_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/lag_rating_stale_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/lagged_cache_adjusted_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/logto_silent_defaults_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/macro_gate_health_tz_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/macro_healthcheck_sbv_reconfirm_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/macro_killswitch_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/navbasis_loud_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/netting_recon_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/oshares_dcf_selfcheck.py` | offline | PASS | 549s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/oshares_wire_selfcheck.py` | offline | PASS | 19s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/planpy_failopen_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/probe_linger_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/rating8l_eff_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/rating8l_icb_pit_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 49s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/rating_pit_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/refresh_earnings_surprise_pkl_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/route_selector_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/rubber_weekly_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/sbv_policy_verify_selfcheck.py` | offline | PASS | 17s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/sell_loan_package_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/te_macro_crosscheck_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/te_weekly_bash_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/tz_asof_ict_dd_dcf_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_adjv2_20261110/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/account_overrides_broker_resolution_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/anomaly_gate_freshness_session_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/anomaly_gate_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/atc_cancel_overorder_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/brokers_tradequantity_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/cctg6m_series_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/cctg_deposit_asof_ict_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/cctg_deposit_wiring_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/cctg_overlay_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/cctg_tier2_series_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/churn_guard_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/close_repair_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/cpi_vn_te_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/cq_hardcore_20261108_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/custom30_publish_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/custom30_publish_weight_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/custom_basket_forensic_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/daily_refresh_morning_selfcheck.sh` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/dc_book_waterfall_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/dcf_rate_display_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/dcf_rate_frame_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/dcf_refresh_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/dcf_rstar_refresh_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/dcf_season_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/dcf_selector_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/dd_flag_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/deposit_fallback_direction_selfcheck.py` | offline | FAIL(rc=1) | 11s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/discretionary_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/dna_report_killswitch_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/dna_report_liquidity_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/dot2_batch_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/edge_wlag_gate_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/expected_volume_pacing_selfcheck.py` | offline | PASS | 24s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/failc_residual_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/failc_sweep8_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/failopen_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/failopen_telegram_refresh_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/fetch_bdi_daily_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/freshness_ops_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/hybrid_fill_timing_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/idle_rate_proxy_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/lag_adv_basis_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/lag_adv_cap_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/lag_dd_zone_gate_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/lag_governance_order_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/lag_live_schedule_selfcheck.py` | offline | PASS | 22s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/lag_rating_gate_snapshot_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/lag_rating_order_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/lag_rating_stale_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/lagged_cache_adjusted_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/logto_silent_defaults_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/macro_gate_health_tz_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/macro_healthcheck_sbv_reconfirm_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/macro_killswitch_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/navbasis_loud_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/oshares_dcf_selfcheck.py` | offline | PASS | 540s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/oshares_wire_selfcheck.py` | offline | PASS | 20s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/planpy_failopen_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/probe_linger_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/rating8l_eff_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/rating8l_icb_pit_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 49s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/rating_pit_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/refresh_earnings_surprise_pkl_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/refresh_skip_participation_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/route_selector_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/rubber_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/sbv_policy_verify_selfcheck.py` | offline | PASS | 17s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/sell_loan_package_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/t2_settlement_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/te_macro_crosscheck_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/te_weekly_bash_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/tz_asof_ict_dd_dcf_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_frozen20261112/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/account_overrides_broker_resolution_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/anomaly_gate_freshness_session_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/atc_cancel_overorder_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/brokers_tradequantity_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/cctg6m_series_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/cctg_deposit_asof_ict_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/cctg_deposit_wiring_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/cctg_overlay_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/cctg_tier2_series_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/churn_guard_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/close_repair_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/concurrent_lock_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/cpi_vn_te_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/cq_hardcore_20261108_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/custom30_publish_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/custom30_publish_weight_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/custom_basket_forensic_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/daily_refresh_morning_selfcheck.sh` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/dc_book_waterfall_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/dcf_rate_display_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/dcf_rate_frame_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/dcf_refresh_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/dcf_rstar_refresh_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/dcf_season_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/dcf_selector_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/dd_flag_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/deposit_fallback_direction_selfcheck.py` | offline | FAIL(rc=1) | 10s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/dna_report_killswitch_line_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/dna_report_liquidity_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/dot2_batch_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 20s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/edge_wlag_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/expected_volume_pacing_selfcheck.py` | offline | PASS | 24s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/failc_residual_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/failc_sweep8_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/failopen_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/failopen_telegram_refresh_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/fetch_bdi_daily_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/freshness_ops_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/hybrid_fill_timing_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/idle_rate_proxy_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/lag_adv_basis_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/lag_adv_cap_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/lag_dd_zone_gate_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/lag_governance_order_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/lag_live_schedule_selfcheck.py` | offline | PASS | 22s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/lag_rating_gate_snapshot_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/lag_rating_stale_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/lagged_cache_adjusted_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/logto_silent_defaults_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/macro_gate_health_tz_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/macro_healthcheck_sbv_reconfirm_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/macro_killswitch_a_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/money_path_freshness_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/navbasis_loud_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/oshares_dcf_selfcheck.py` | offline | PASS | 546s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/oshares_wire_selfcheck.py` | offline | PASS | 18s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/paper_main_window_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/planpy_failopen_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/probe_linger_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/rating8l_eff_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/rating8l_icb_pit_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 49s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/rating_pit_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/refresh_earnings_surprise_pkl_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/route_selector_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/rubber_weekly_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/sbv_policy_verify_selfcheck.py` | offline | PASS | 18s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/sell_loan_package_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/te_macro_crosscheck_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/te_weekly_bash_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/tz_asof_ict_dd_dcf_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bm_vintage20261029/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/account_overrides_broker_resolution_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/anomaly_gate_freshness_session_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/atc_cancel_overorder_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/brokers_tradequantity_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/cctg6m_series_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/cctg_deposit_asof_ict_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/cctg_deposit_wiring_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/cctg_overlay_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/cctg_tier2_series_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/churn_guard_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/close_repair_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/cpi_vn_te_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/cq_hardcore_20261108_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/custom30_publish_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/custom30_publish_weight_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/custom_basket_forensic_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/daily_refresh_morning_selfcheck.sh` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/dc_book_waterfall_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/dcf_check_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/dcf_rate_display_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/dcf_rate_frame_selfcheck.py` | offline | PASS | 27s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/dcf_refresh_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/dcf_rstar_refresh_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/dcf_season_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/dcf_selector_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/dd_flag_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/deposit_fallback_direction_selfcheck.py` | offline | FAIL(rc=1) | 10s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/dna_report_killswitch_line_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/dna_report_liquidity_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/dot2_batch_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/edge_wlag_gate_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/expected_volume_pacing_selfcheck.py` | offline | PASS | 25s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/failc_residual_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/failc_sweep8_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/failopen_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/failopen_telegram_refresh_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/fetch_bdi_daily_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/freshness_ops_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/ghost_order_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 9s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/hybrid_fill_timing_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/idle_rate_proxy_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/lag_adv_basis_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/lag_adv_cap_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/lag_dd_zone_gate_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/lag_governance_order_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/lag_live_schedule_selfcheck.py` | offline | PASS | 22s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/lag_rating_gate_snapshot_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/lag_rating_stale_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/lagged_cache_adjusted_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/logto_silent_defaults_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/macro_gate_health_tz_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/macro_healthcheck_sbv_reconfirm_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/macro_killswitch_a_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/navbasis_loud_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/oshares_dcf_selfcheck.py` | offline | PASS | 547s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/oshares_wire_selfcheck.py` | offline | PASS | 19s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/planpy_failopen_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/probe_linger_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/rating8l_eff_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/rating8l_icb_pit_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 50s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/rating_pit_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/refresh_earnings_surprise_pkl_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/route_selector_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/rubber_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/sbv_policy_verify_selfcheck.py` | offline | PASS | 17s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/screen_sort_direction_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/sell_loan_package_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/te_macro_crosscheck_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/te_weekly_bash_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/tz_asof_ict_dd_dcf_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_adjv2_20261110/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/account_overrides_broker_resolution_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/anomaly_gate_freshness_session_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/atc_cancel_overorder_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/brokers_tradequantity_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/cctg6m_series_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/cctg_deposit_asof_ict_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/cctg_deposit_wiring_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/cctg_overlay_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/cctg_tier2_series_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/churn_guard_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/close_repair_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/cpi_vn_te_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/cq_hardcore_20261108_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/custom30_publish_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/custom30_publish_weight_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/custom_basket_forensic_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/daily_refresh_morning_selfcheck.sh` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/dc_book_waterfall_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/dcf_rate_display_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/dcf_rate_frame_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/dcf_refresh_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/dcf_rstar_refresh_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/dcf_season_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/dcf_selector_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/dd_flag_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/deposit_fallback_direction_selfcheck.py` | offline | FAIL(rc=1) | 10s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/dna_report_killswitch_line_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/dna_report_liquidity_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/dot2_batch_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 20s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 13s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/edge_wlag_gate_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/expected_volume_pacing_selfcheck.py` | offline | PASS | 24s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/failc_residual_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/failc_sweep8_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/failopen_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/failopen_telegram_refresh_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/fetch_bdi_daily_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/freshness_ops_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 9s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/hybrid_fill_timing_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/idle_rate_proxy_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/lag_adv_basis_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/lag_adv_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/lag_dd_zone_gate_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/lag_governance_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/lag_live_schedule_selfcheck.py` | offline | PASS | 23s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/lag_rating_gate_snapshot_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/lag_rating_stale_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/lagged_cache_adjusted_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/logto_silent_defaults_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/macro_gate_health_tz_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/macro_healthcheck_sbv_reconfirm_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/macro_killswitch_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/navbasis_loud_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/oshares_dcf_selfcheck.py` | offline | PASS | 544s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/oshares_wire_selfcheck.py` | offline | PASS | 20s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/paper_main_window_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/planpy_failopen_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/probe_linger_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/rating8l_eff_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/rating8l_icb_pit_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 51s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/rating_pit_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/refresh_earnings_surprise_pkl_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/route_selector_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/rubber_weekly_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/sbv_policy_verify_selfcheck.py` | offline | PASS | 18s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/sell_loan_package_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/te_macro_crosscheck_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/te_weekly_bash_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/tz_asof_ict_dd_dcf_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_frozen20261112/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/account_overrides_broker_resolution_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/anomaly_gate_freshness_session_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/atc_cancel_overorder_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/brokers_tradequantity_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/cctg6m_series_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/cctg_deposit_asof_ict_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/cctg_deposit_wiring_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/cctg_overlay_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/cctg_tier2_series_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/churn_guard_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/close_repair_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/cpi_vn_te_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/cq_hardcore_20261108_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/custom30_publish_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/custom30_publish_weight_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/custom_basket_forensic_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/daily_refresh_morning_selfcheck.sh` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/dc_book_waterfall_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/dcf_check_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/dcf_rate_display_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/dcf_rate_frame_selfcheck.py` | offline | PASS | 27s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/dcf_refresh_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/dcf_rstar_refresh_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/dcf_season_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/dcf_selector_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/dd_flag_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/deposit_fallback_direction_selfcheck.py` | offline | FAIL(rc=1) | 10s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/dna_report_killswitch_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/dna_report_liquidity_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/dot2_batch_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 20s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 11s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/edge_wlag_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/expected_volume_pacing_selfcheck.py` | offline | PASS | 25s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/extreme_regime_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/failc_residual_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/failc_sweep8_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/failopen_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/failopen_telegram_refresh_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/fetch_bdi_daily_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/freshness_ops_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 9s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/hybrid_fill_timing_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/idle_rate_proxy_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/lag_adv_basis_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/lag_adv_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/lag_dd_zone_gate_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/lag_governance_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/lag_live_schedule_selfcheck.py` | offline | PASS | 22s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/lag_rating_gate_snapshot_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/lag_rating_stale_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/lagged_cache_adjusted_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/logto_silent_defaults_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/macro_gate_health_tz_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/macro_healthcheck_sbv_reconfirm_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/macro_killswitch_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/navbasis_loud_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/oshares_dcf_selfcheck.py` | offline | PASS | 547s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/oshares_wire_selfcheck.py` | offline | PASS | 19s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/planpy_failopen_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/probe_linger_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/rating8l_eff_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/rating8l_icb_pit_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 49s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/rating_pit_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/refresh_earnings_surprise_pkl_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/route_selector_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/rubber_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/sbv_policy_verify_selfcheck.py` | offline | PASS | 17s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/sell_loan_package_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/t2_settlement_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/te_macro_crosscheck_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/te_weekly_bash_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/tz_asof_ict_dd_dcf_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/bq_vintage20261029/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/account_overrides_broker_resolution_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/anomaly_gate_freshness_session_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/atc_cancel_overorder_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/brokers_tradequantity_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/cctg6m_series_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/cctg_deposit_asof_ict_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/cctg_deposit_wiring_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/cctg_overlay_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/cctg_tier2_series_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/churn_guard_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/close_repair_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/cpi_vn_te_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/cq_hardcore_20261108_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/custom30_publish_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/custom30_publish_weight_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/custom_basket_forensic_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/daily_refresh_morning_selfcheck.sh` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/dc_book_waterfall_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/dcf_rate_display_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/dcf_rate_frame_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/dcf_refresh_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/dcf_rstar_refresh_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/dcf_season_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/dcf_selector_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/dd_flag_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/deposit_fallback_direction_selfcheck.py` | offline | FAIL(rc=1) | 10s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/dna_report_killswitch_line_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/dna_report_liquidity_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/dot2_batch_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/edge_wlag_gate_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/expected_volume_pacing_selfcheck.py` | offline | PASS | 25s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/failc_residual_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/failc_sweep8_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/failopen_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/failopen_telegram_refresh_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/fetch_bdi_daily_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/freshness_ops_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 9s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/hybrid_fill_timing_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/idle_rate_proxy_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/lag_adv_basis_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/lag_adv_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/lag_dd_zone_gate_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/lag_governance_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/lag_live_schedule_selfcheck.py` | offline | PASS | 23s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/lag_rating_gate_snapshot_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/lag_rating_stale_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/lagged_cache_adjusted_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/logto_silent_defaults_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/macro_gate_health_tz_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/macro_healthcheck_sbv_reconfirm_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/macro_killswitch_a_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/navbasis_loud_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/oshares_dcf_selfcheck.py` | offline | PASS | 551s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/oshares_wire_selfcheck.py` | offline | PASS | 19s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/plan_cash_commitment_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/planpy_failopen_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/probe_linger_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/rating8l_eff_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/rating8l_icb_pit_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 50s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/rating_pit_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/refresh_earnings_surprise_pkl_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/route_selector_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/rubber_weekly_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/sbv_policy_verify_selfcheck.py` | offline | PASS | 17s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/sell_loan_package_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/te_macro_crosscheck_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/te_weekly_bash_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/tz_asof_ict_dd_dcf_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_adjv2_20261110/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/account_overrides_broker_resolution_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/anomaly_gate_freshness_session_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/atc_cancel_overorder_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/brokers_tradequantity_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/cctg6m_series_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/cctg_deposit_asof_ict_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/cctg_deposit_wiring_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/cctg_overlay_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/cctg_tier2_series_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/churn_guard_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/close_repair_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/cpi_vn_te_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/cq_hardcore_20261108_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/custom30_publish_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/custom30_publish_weight_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/custom_basket_forensic_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/daily_refresh_morning_selfcheck.sh` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/dc_book_waterfall_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/dcf_rate_display_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/dcf_rate_frame_selfcheck.py` | offline | PASS | 27s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/dcf_refresh_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/dcf_rstar_refresh_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/dcf_season_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/dcf_selector_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/dd_flag_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/deposit_fallback_direction_selfcheck.py` | offline | FAIL(rc=1) | 10s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/discretionary_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/dna_report_killswitch_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/dna_report_liquidity_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/dot2_batch_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/dsr_family_manifest_selfcheck.py` | offline | PASS | 27s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 11s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/edge_wlag_gate_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/expected_volume_pacing_selfcheck.py` | offline | PASS | 25s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/extreme_regime_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/failc_residual_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/failc_sweep8_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/failopen_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/failopen_telegram_refresh_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/fetch_bdi_daily_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/freshness_ops_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 9s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/hybrid_fill_timing_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/idle_rate_proxy_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/lag_adv_basis_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/lag_adv_cap_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/lag_dd_zone_gate_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/lag_governance_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/lag_live_schedule_selfcheck.py` | offline | PASS | 23s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/lag_rating_gate_snapshot_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/lag_rating_stale_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/lagged_cache_adjusted_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/logto_silent_defaults_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/macro_gate_health_tz_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/macro_healthcheck_sbv_reconfirm_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/macro_killswitch_a_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/money_path_freshness_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/navbasis_loud_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/oshares_dcf_selfcheck.py` | offline | PASS | 542s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/oshares_wire_selfcheck.py` | offline | PASS | 20s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/plan_check_field_schema_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/planpy_failopen_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/probe_linger_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/rating8l_eff_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/rating8l_icb_pit_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 51s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/rating_pit_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/refresh_earnings_surprise_pkl_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/route_selector_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/rubber_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/sbv_policy_verify_selfcheck.py` | offline | PASS | 17s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/sell_loan_package_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/te_macro_crosscheck_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/te_weekly_bash_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/tz_asof_ict_dd_dcf_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_frozen20261112/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/account_overrides_broker_resolution_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/anomaly_gate_freshness_session_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/anomaly_gate_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/atc_cancel_overorder_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/brokers_tradequantity_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/cctg6m_series_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/cctg_deposit_asof_ict_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/cctg_deposit_wiring_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/cctg_overlay_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/cctg_tier2_series_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/churn_guard_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/close_repair_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/cpi_vn_te_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/cq_hardcore_20261108_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/custom30_publish_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/custom30_publish_weight_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/custom_basket_forensic_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/daily_refresh_morning_selfcheck.sh` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/dc_book_waterfall_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/dcf_check_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/dcf_rate_display_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/dcf_rate_frame_selfcheck.py` | offline | PASS | 27s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/dcf_refresh_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/dcf_rstar_refresh_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/dcf_season_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/dcf_selector_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/dd_flag_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/deposit_fallback_direction_selfcheck.py` | offline | FAIL(rc=1) | 10s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/dna_report_killswitch_line_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/dna_report_liquidity_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/dot2_batch_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/edge_wlag_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/expected_volume_pacing_selfcheck.py` | offline | PASS | 25s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/failc_residual_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/failc_sweep8_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/failopen_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/failopen_telegram_refresh_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/fetch_bdi_daily_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/freshness_ops_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 9s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/hybrid_fill_timing_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/idle_rate_proxy_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/lag_adv_basis_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/lag_adv_cap_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/lag_dd_zone_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/lag_governance_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/lag_live_schedule_selfcheck.py` | offline | PASS | 23s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/lag_rating_gate_snapshot_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/lag_rating_stale_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/lagged_cache_adjusted_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/logto_silent_defaults_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/macro_gate_health_tz_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/macro_healthcheck_sbv_reconfirm_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/macro_killswitch_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/navbasis_loud_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/oshares_dcf_selfcheck.py` | offline | PASS | 553s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/oshares_wire_selfcheck.py` | offline | PASS | 19s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/plan_cash_commitment_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/planpy_failopen_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/probe_linger_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/rating8l_eff_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/rating8l_icb_pit_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 49s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/rating_pit_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/refresh_earnings_surprise_pkl_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/route_selector_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/rubber_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/sbv_policy_verify_selfcheck.py` | offline | PASS | 18s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/screen_sort_direction_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/sell_loan_package_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/te_macro_crosscheck_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/te_weekly_bash_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/tz_asof_ict_dd_dcf_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/btb_vintage20261029/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/account_overrides_broker_resolution_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/churn_guard_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/concurrent_lock_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/custom30_publish_weight_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/dc_book_waterfall_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/dcf_refresh_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/dcf_selector_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 11s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/edge_wlag_gate_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/expected_volume_pacing_selfcheck.py` | offline | PASS | 24s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/extreme_regime_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/failc_residual_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/failc_sweep8_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/freshness_ops_selfcheck.py` | offline | FAIL(rc=1) | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 9s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/hybrid_fill_timing_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/idle_cash_age_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/idle_rate_proxy_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/lag_adv_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/lag_governance_order_gate_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/lag_live_schedule_selfcheck.py` | offline | PASS | 23s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/lag_rating_order_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/money_path_freshness_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/oshares_wire_selfcheck.py` | offline | PASS | 19s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/plan_cash_commitment_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/probe_linger_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/rating8l_icb_pit_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 42s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/route_selector_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/rubber_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/rule_a_ref_guard_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/screen_sort_direction_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_adjv2_20261110/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/account_overrides_broker_resolution_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/churn_guard_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/custom30_publish_weight_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/dc_book_waterfall_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/dcf_refresh_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/dcf_selector_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/edge_wlag_gate_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/expected_volume_pacing_selfcheck.py` | offline | PASS | 25s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/failc_residual_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/failc_sweep8_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/freshness_ops_selfcheck.py` | offline | FAIL(rc=1) | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/hybrid_fill_timing_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/idle_cash_age_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/idle_rate_proxy_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/lag_adv_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/lag_governance_order_gate_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/lag_live_schedule_selfcheck.py` | offline | PASS | 22s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/lag_rating_order_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/money_path_freshness_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/netting_recon_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/oshares_wire_selfcheck.py` | offline | PASS | 19s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/plan_cash_commitment_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/probe_linger_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/rating8l_icb_pit_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 40s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/route_selector_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/rubber_weekly_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/rule_a_ref_guard_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_frozen20261112/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/account_overrides_broker_resolution_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/churn_guard_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/custom30_publish_weight_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/dc_book_waterfall_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/dcf_refresh_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/dcf_selector_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/edge_wlag_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/expected_volume_pacing_selfcheck.py` | offline | PASS | 24s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/failc_residual_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/failc_sweep8_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/freshness_ops_selfcheck.py` | offline | FAIL(rc=1) | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/hybrid_fill_timing_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/idle_cash_age_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/idle_rate_proxy_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/lag_adv_cap_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/lag_governance_order_gate_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/lag_live_schedule_selfcheck.py` | offline | PASS | 22s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/lag_rating_order_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/oshares_wire_selfcheck.py` | offline | PASS | 19s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/probe_linger_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/rating8l_icb_pit_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 40s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/route_selector_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/rubber_weekly_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/rule_a_ref_guard_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/t2_settlement_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rm_vintage20261029/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/account_overrides_broker_resolution_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/churn_guard_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/custom30_publish_weight_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/dc_book_waterfall_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/dcf_refresh_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/dcf_selector_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/edge_wlag_gate_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/expected_volume_pacing_selfcheck.py` | offline | PASS | 25s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/failc_residual_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/failc_sweep8_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/freshness_ops_selfcheck.py` | offline | FAIL(rc=1) | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/hybrid_fill_timing_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/idle_cash_age_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/idle_rate_proxy_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/lag_adv_cap_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/lag_governance_order_gate_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/lag_live_schedule_selfcheck.py` | offline | PASS | 22s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/lag_rating_order_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/money_path_freshness_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/oshares_wire_selfcheck.py` | offline | PASS | 20s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/probe_linger_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/rating8l_icb_pit_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 41s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/route_selector_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/rubber_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/rule_a_ref_guard_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_adjv2_20261110/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/account_overrides_broker_resolution_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/churn_guard_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/custom30_publish_weight_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/dc_book_waterfall_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/dcf_refresh_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/dcf_selector_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/edge_wlag_gate_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/expected_volume_pacing_selfcheck.py` | offline | PASS | 25s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/extreme_regime_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/failc_residual_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/failc_sweep8_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/freshness_ops_selfcheck.py` | offline | FAIL(rc=1) | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 9s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/hybrid_fill_timing_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/idle_cash_age_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/idle_rate_proxy_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/lag_adv_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/lag_governance_order_gate_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/lag_live_schedule_selfcheck.py` | offline | PASS | 23s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/oshares_wire_selfcheck.py` | offline | PASS | 19s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/paper_main_window_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/probe_linger_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/rating8l_icb_pit_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 39s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/route_selector_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/rubber_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/rule_a_ref_guard_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_frozen20261112/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/account_overrides_broker_resolution_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/capit_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/churn_guard_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/custom30_publish_weight_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/dc_book_waterfall_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/dcf_check_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/dcf_refresh_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/dcf_selector_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 11s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/edge_wlag_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/expected_volume_pacing_selfcheck.py` | offline | PASS | 24s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/failc_residual_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/failc_sweep8_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/freshness_ops_selfcheck.py` | offline | FAIL(rc=1) | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/hybrid_fill_timing_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/idle_cash_age_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/idle_rate_proxy_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/lag_adv_cap_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/lag_governance_order_gate_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/lag_live_schedule_selfcheck.py` | offline | PASS | 23s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/oshares_wire_selfcheck.py` | offline | PASS | 19s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/paper_main_window_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/probe_linger_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/rating8l_icb_pit_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 40s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/route_selector_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/rubber_weekly_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/rule_a_ref_guard_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/t2_settlement_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rq_vintage20261029/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/account_overrides_broker_resolution_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/churn_guard_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/custom30_publish_weight_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/dc_book_waterfall_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/dcf_refresh_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/dcf_selector_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/edge_wlag_gate_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/expected_volume_pacing_selfcheck.py` | offline | PASS | 24s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/failc_residual_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/failc_sweep8_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/freshness_ops_selfcheck.py` | offline | FAIL(rc=1) | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/hybrid_fill_timing_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/idle_cash_age_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/idle_rate_proxy_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/lag_adv_cap_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/lag_governance_order_gate_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/lag_live_schedule_selfcheck.py` | offline | PASS | 22s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/lag_rating_order_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/money_path_freshness_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/oshares_wire_selfcheck.py` | offline | PASS | 20s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/probe_linger_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/rating8l_icb_pit_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 39s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/route_selector_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/rubber_weekly_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/rule_a_ref_guard_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_adjv2_20261110/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/account_overrides_broker_resolution_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/churn_guard_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/custom30_publish_weight_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/dc_book_waterfall_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/dcf_check_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/dcf_refresh_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/dcf_selector_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/edge_wlag_gate_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/expected_volume_pacing_selfcheck.py` | offline | PASS | 24s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/failc_residual_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/failc_sweep8_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/freshness_ops_selfcheck.py` | offline | FAIL(rc=1) | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/hybrid_fill_timing_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/idle_cash_age_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/idle_rate_proxy_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/lag_adv_cap_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/lag_governance_order_gate_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/lag_live_schedule_selfcheck.py` | offline | PASS | 23s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/oshares_wire_selfcheck.py` | offline | PASS | 19s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/pacing_horizon_note_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/plan_check_field_schema_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/probe_linger_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/rating8l_icb_pit_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 40s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/route_selector_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/rubber_weekly_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/rule_a_ref_guard_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_frozen20261112/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/account_overrides_broker_resolution_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/churn_guard_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/custom30_publish_weight_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/dc_book_waterfall_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/dcf_refresh_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/dcf_selector_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 13s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/edge_wlag_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/expected_volume_pacing_selfcheck.py` | offline | PASS | 25s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/extreme_regime_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/failc_residual_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/failc_sweep8_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/freshness_ops_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/gdkhq_rollout_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/ghost_order_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 9s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/hybrid_fill_timing_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/idle_cash_age_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/idle_rate_proxy_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/lag_adv_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/lag_governance_order_gate_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/lag_live_schedule_selfcheck.py` | offline | PASS | 23s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/oshares_wire_selfcheck.py` | offline | PASS | 25s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/plan_check_field_schema_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/probe_linger_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/rating8l_icb_pit_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 40s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/route_selector_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/rubber_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/rule_a_ref_guard_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A/sb/rtb_vintage20261029/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/account_overrides_broker_resolution_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/anomaly_gate_freshness_session_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/anomaly_gate_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/atc_cancel_overorder_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/brokers_tradequantity_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/cctg6m_series_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/cctg_deposit_asof_ict_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/cctg_deposit_wiring_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/cctg_overlay_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/cctg_tier2_series_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/churn_guard_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/close_repair_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/cpi_vn_te_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/cq_hardcore_20261108_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/custom30_publish_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/custom30_publish_weight_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/custom_basket_forensic_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/daily_refresh_morning_selfcheck.sh` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/dc_book_waterfall_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/dcf_rate_display_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/dcf_rate_frame_selfcheck.py` | offline | PASS | 27s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/dcf_refresh_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/dcf_rstar_refresh_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/dcf_season_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/dcf_selector_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/dd_flag_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/deposit_fallback_direction_selfcheck.py` | offline | FAIL(rc=1) | 10s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/dna_report_killswitch_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/dna_report_liquidity_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/dot2_batch_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/edge_wlag_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/expected_volume_pacing_selfcheck.py` | offline | PASS | 24s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/failc_residual_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/failc_sweep8_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/failopen_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/failopen_telegram_refresh_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/fetch_bdi_daily_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/freshness_ops_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/ghost_order_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 9s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/hybrid_fill_timing_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/idle_rate_proxy_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/lag_adv_basis_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/lag_adv_cap_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/lag_dd_zone_gate_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/lag_governance_order_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/lag_live_schedule_selfcheck.py` | offline | PASS | 22s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/lag_rating_gate_snapshot_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/lag_rating_order_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/lag_rating_stale_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/lagged_cache_adjusted_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/logto_silent_defaults_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/macro_gate_health_tz_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/macro_healthcheck_sbv_reconfirm_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/macro_killswitch_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/navbasis_loud_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/oshares_dcf_selfcheck.py` | offline | PASS | 542s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/oshares_wire_selfcheck.py` | offline | PASS | 20s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/plan_check_field_schema_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/planpy_failopen_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/probe_linger_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/rating8l_eff_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/rating8l_icb_pit_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 50s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/rating_pit_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/refresh_earnings_surprise_pkl_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/route_selector_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/rubber_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/sbv_policy_verify_selfcheck.py` | offline | PASS | 17s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/sell_loan_package_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/te_macro_crosscheck_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/te_weekly_bash_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/tz_asof_ict_dd_dcf_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/m/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/account_overrides_broker_resolution_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/churn_guard_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/concurrent_lock_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/custom30_publish_weight_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/dc_book_waterfall_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/dcf_refresh_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/dcf_selector_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/dsr_family_manifest_selfcheck.py` | offline | PASS | 25s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 11s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/edge_wlag_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/expected_volume_pacing_selfcheck.py` | offline | PASS | 24s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/failc_residual_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/failc_sweep8_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/freshness_ops_selfcheck.py` | offline | FAIL(rc=1) | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/hybrid_fill_timing_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/idle_cash_age_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/idle_rate_proxy_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/lag_adv_cap_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/lag_governance_order_gate_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/lag_live_schedule_selfcheck.py` | offline | PASS | 23s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/oshares_wire_selfcheck.py` | offline | PASS | 20s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/probe_linger_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/rating8l_icb_pit_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 40s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/route_selector_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/rubber_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/rule_a_ref_guard_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/t2_settlement_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A2/sb/r/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/account_overrides_broker_resolution_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/anomaly_gate_freshness_session_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/approval_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/atc_cancel_overorder_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/brokers_tradequantity_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/cctg6m_series_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/cctg_deposit_asof_ict_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/cctg_deposit_wiring_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/cctg_overlay_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/cctg_tier2_series_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/churn_guard_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/close_repair_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/concurrent_lock_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/cpi_vn_te_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/cq_hardcore_20261108_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/custom30_publish_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/custom30_publish_weight_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/custom_basket_forensic_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/daily_refresh_morning_selfcheck.sh` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/dc_book_waterfall_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/dcf_rate_display_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/dcf_rate_frame_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/dcf_refresh_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/dcf_rstar_refresh_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/dcf_season_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/dcf_selector_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/dd_flag_order_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/deposit_fallback_direction_selfcheck.py` | offline | FAIL(rc=1) | 10s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/dna_report_killswitch_line_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/dna_report_liquidity_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/dot2_batch_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/edge_wlag_gate_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/expected_volume_pacing_selfcheck.py` | offline | PASS | 24s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/failc_residual_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/failc_sweep8_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/failopen_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/failopen_telegram_refresh_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/fetch_bdi_daily_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/freshness_ops_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/ghost_order_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 9s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/hybrid_fill_timing_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/idle_rate_proxy_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/lag_adv_basis_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/lag_adv_cap_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/lag_dd_zone_gate_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/lag_governance_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/lag_live_schedule_selfcheck.py` | offline | PASS | 23s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/lag_rating_gate_snapshot_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/lag_rating_stale_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/lagged_cache_adjusted_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/logto_silent_defaults_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/macro_gate_health_tz_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/macro_healthcheck_sbv_reconfirm_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/macro_killswitch_a_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/money_path_freshness_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/navbasis_loud_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/oshares_dcf_selfcheck.py` | offline | PASS | 542s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/oshares_wire_selfcheck.py` | offline | PASS | 19s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/paper_main_window_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/planpy_failopen_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/probe_linger_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/rating8l_eff_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/rating8l_icb_pit_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 50s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/rating_pit_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/refresh_earnings_surprise_pkl_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/route_selector_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/rubber_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/sbv_policy_verify_selfcheck.py` | offline | PASS | 17s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/sell_loan_package_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/t2_settlement_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/te_macro_crosscheck_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/te_weekly_bash_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/tz_asof_ict_dd_dcf_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_adj/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/account_overrides_broker_resolution_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/anomaly_gate_freshness_session_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/atc_cancel_overorder_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/brokers_tradequantity_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/cctg6m_series_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/cctg_deposit_asof_ict_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/cctg_deposit_wiring_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/cctg_overlay_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/cctg_tier2_series_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/churn_guard_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/close_repair_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/cpi_vn_te_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/cq_hardcore_20261108_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/custom30_publish_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/custom30_publish_weight_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/custom_basket_forensic_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/daily_refresh_morning_selfcheck.sh` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/dc_book_waterfall_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/dcf_check_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/dcf_rate_display_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/dcf_rate_frame_selfcheck.py` | offline | PASS | 27s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/dcf_refresh_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/dcf_rstar_refresh_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/dcf_season_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/dcf_selector_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/dd_flag_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/deposit_fallback_direction_selfcheck.py` | offline | FAIL(rc=1) | 10s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/dna_report_killswitch_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/dna_report_liquidity_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/dot2_batch_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/edge_wlag_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/expected_volume_pacing_selfcheck.py` | offline | PASS | 24s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/failc_residual_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/failc_sweep8_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/failopen_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/failopen_telegram_refresh_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/fetch_bdi_daily_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/freshness_ops_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/hybrid_fill_timing_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/idle_rate_proxy_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/lag_adv_basis_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/lag_adv_cap_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/lag_dd_zone_gate_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/lag_governance_order_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/lag_live_schedule_selfcheck.py` | offline | PASS | 22s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/lag_rating_gate_snapshot_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/lag_rating_stale_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/lagged_cache_adjusted_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/logto_silent_defaults_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/macro_gate_health_tz_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/macro_healthcheck_sbv_reconfirm_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/macro_killswitch_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/navbasis_loud_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/oshares_dcf_selfcheck.py` | offline | PASS | 543s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/oshares_selfcheck_fixture.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/oshares_wire_selfcheck.py` | offline | PASS | 20s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/plan_cash_commitment_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/planpy_failopen_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/probe_linger_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/rating8l_eff_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/rating8l_icb_pit_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 52s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/rating_pit_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/refresh_earnings_surprise_pkl_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/route_selector_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/rubber_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/sbv_policy_verify_selfcheck.py` | offline | PASS | 17s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/sell_loan_package_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/te_macro_crosscheck_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/te_weekly_bash_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/tz_asof_ict_dd_dcf_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/m_vint/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/account_overrides_broker_resolution_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/anomaly_gate_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/churn_guard_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/custom30_publish_weight_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/dc_book_waterfall_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/dcf_refresh_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/dcf_selector_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/dsr_family_manifest_selfcheck.py` | offline | PASS | 27s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/edge_wlag_gate_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/expected_volume_pacing_selfcheck.py` | offline | PASS | 25s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/failc_residual_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/failc_sweep8_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/freshness_ops_selfcheck.py` | offline | FAIL(rc=1) | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/ghost_order_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 9s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/hybrid_fill_timing_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/idle_cash_age_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/idle_rate_proxy_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/lag_adv_cap_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/lag_governance_order_gate_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/lag_live_schedule_selfcheck.py` | offline | PASS | 23s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/oshares_wire_selfcheck.py` | offline | PASS | 20s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/probe_linger_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/rating8l_icb_pit_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 41s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/route_selector_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/rubber_weekly_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/rule_a_ref_guard_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/t2_settlement_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_adj/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/account_overrides_broker_resolution_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/churn_guard_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/custom30_publish_weight_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/dc_book_waterfall_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/dcf_refresh_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/dcf_selector_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/edge_wlag_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/expected_volume_pacing_selfcheck.py` | offline | PASS | 25s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/extreme_regime_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/failc_residual_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/failc_sweep8_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/freshness_ops_selfcheck.py` | offline | FAIL(rc=1) | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/hybrid_fill_timing_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/idle_cash_age_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/idle_rate_proxy_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/lag_adv_cap_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/lag_governance_order_gate_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/lag_live_schedule_selfcheck.py` | offline | PASS | 22s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/oshares_wire_selfcheck.py` | offline | PASS | 20s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/probe_linger_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/rating8l_icb_pit_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 41s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/route_selector_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/rubber_weekly_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/rule_a_ref_guard_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A3/sb/r_vint/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/account_overrides_broker_resolution_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/anomaly_gate_freshness_session_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/atc_cancel_overorder_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/brokers_tradequantity_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/cctg6m_series_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/cctg_deposit_asof_ict_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/cctg_deposit_wiring_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/cctg_overlay_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/cctg_tier2_series_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/churn_guard_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/close_repair_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/cpi_vn_te_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/cq_hardcore_20261108_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/custom30_publish_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/custom30_publish_weight_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/custom_basket_forensic_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/daily_refresh_morning_selfcheck.sh` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/dc_book_waterfall_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/dcf_rate_display_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/dcf_rate_frame_selfcheck.py` | offline | PASS | 27s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/dcf_refresh_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/dcf_rstar_refresh_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/dcf_season_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/dcf_selector_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/dd_flag_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/deposit_fallback_direction_selfcheck.py` | offline | FAIL(rc=1) | 10s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/discretionary_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/dna_report_killswitch_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/dna_report_liquidity_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/dot2_batch_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/edge_wlag_gate_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/expected_volume_pacing_selfcheck.py` | offline | PASS | 24s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/failc_residual_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/failc_sweep8_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/failopen_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/failopen_telegram_refresh_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/fetch_bdi_daily_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/freshness_ops_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/hybrid_fill_timing_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/idle_rate_proxy_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/lag_adv_basis_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/lag_adv_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/lag_dd_zone_gate_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/lag_governance_order_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/lag_live_schedule_selfcheck.py` | offline | PASS | 22s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/lag_rating_gate_snapshot_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/lag_rating_stale_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/lagged_cache_adjusted_selfcheck.py` | offline | PASS | 9s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/logto_silent_defaults_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/macro_gate_health_tz_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/macro_healthcheck_sbv_reconfirm_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/macro_killswitch_a_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/money_path_freshness_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/navbasis_loud_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/oshares_dcf_selfcheck.py` | offline | PASS | 547s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/oshares_wire_selfcheck.py` | offline | PASS | 20s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/paper_main_window_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/planpy_failopen_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/probe_linger_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/rating8l_eff_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/rating8l_icb_pit_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 51s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/rating_pit_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/refresh_earnings_surprise_pkl_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/route_selector_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/rubber_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/sbv_policy_verify_selfcheck.py` | offline | PASS | 17s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/sell_loan_package_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/te_macro_crosscheck_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/te_weekly_bash_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/tz_asof_ict_dd_dcf_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/m_adj/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/account_overrides_broker_resolution_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/churn_guard_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/custom30_publish_weight_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/dc_book_waterfall_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/dcf_refresh_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/dcf_selector_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/discretionary_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/edge_wlag_gate_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/expected_volume_pacing_selfcheck.py` | offline | PASS | 25s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/extreme_regime_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/failc_residual_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/failc_sweep8_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/freshness_ops_selfcheck.py` | offline | FAIL(rc=1) | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 9s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/hybrid_fill_timing_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/idle_cash_age_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/idle_rate_proxy_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/lag_adv_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/lag_governance_order_gate_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/lag_live_schedule_selfcheck.py` | offline | PASS | 22s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/lag_rating_order_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/oshares_wire_selfcheck.py` | offline | PASS | 20s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/probe_linger_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/rating8l_icb_pit_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 41s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/refresh_skip_participation_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/route_selector_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/rubber_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/rule_a_ref_guard_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/screen_sort_direction_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/r_adj/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/account_overrides_broker_resolution_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/anomaly_gate_freshness_session_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/atc_cancel_overorder_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/brokers_tradequantity_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/cctg6m_series_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/cctg_deposit_asof_ict_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/cctg_deposit_wiring_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/cctg_overlay_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/cctg_tier2_series_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/churn_guard_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/close_repair_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/cpi_vn_te_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/cq_hardcore_20261108_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/custom30_publish_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/custom30_publish_weight_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/custom_basket_forensic_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/daily_refresh_morning_selfcheck.sh` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/dc_book_waterfall_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/dcf_rate_display_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/dcf_rate_frame_selfcheck.py` | offline | PASS | 27s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/dcf_refresh_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/dcf_rstar_refresh_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/dcf_season_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/dcf_selector_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/dd_flag_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/deposit_fallback_direction_selfcheck.py` | offline | FAIL(rc=1) | 11s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/discretionary_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/dna_report_killswitch_line_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/dna_report_liquidity_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/dot2_batch_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/edge_wlag_gate_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/expected_volume_pacing_selfcheck.py` | offline | PASS | 24s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/failc_residual_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/failc_sweep8_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/failopen_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/failopen_telegram_refresh_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/fetch_bdi_daily_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/freshness_ops_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/ghost_order_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 9s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/hybrid_fill_timing_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/idle_rate_proxy_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/lag_adv_basis_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/lag_adv_cap_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/lag_dd_zone_gate_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/lag_governance_order_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/lag_live_schedule_selfcheck.py` | offline | PASS | 22s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/lag_rating_gate_snapshot_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/lag_rating_stale_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/lagged_cache_adjusted_selfcheck.py` | offline | PASS | 9s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/logto_silent_defaults_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/macro_gate_health_tz_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/macro_healthcheck_sbv_reconfirm_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/macro_killswitch_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/navbasis_loud_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/oshares_dcf_selfcheck.py` | offline | PASS | 543s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/oshares_wire_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/paper_main_window_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/plan_check_field_schema_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/planpy_failopen_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/probe_linger_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/rating8l_eff_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/rating8l_icb_pit_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 52s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/rating_pit_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/refresh_earnings_surprise_pkl_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/route_selector_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/rubber_weekly_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/sbv_policy_verify_selfcheck.py` | offline | PASS | 16s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/screen_sort_direction_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/sell_loan_package_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/te_macro_crosscheck_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/te_weekly_bash_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/tz_asof_ict_dd_dcf_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A4/sb/t_adj/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/account_overrides_broker_resolution_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/anomaly_gate_freshness_session_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/atc_cancel_overorder_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/brokers_tradequantity_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/cctg6m_series_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/cctg_deposit_asof_ict_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/cctg_deposit_wiring_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/cctg_overlay_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/cctg_tier2_series_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/churn_guard_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/close_repair_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/cpi_vn_te_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/cq_hardcore_20261108_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/custom30_publish_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/custom30_publish_weight_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/custom_basket_forensic_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/daily_refresh_morning_selfcheck.sh` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/dc_book_waterfall_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/dcf_rate_display_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/dcf_rate_frame_selfcheck.py` | offline | PASS | 28s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/dcf_refresh_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/dcf_rstar_refresh_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/dcf_season_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/dcf_selector_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/dd_flag_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/deposit_fallback_direction_selfcheck.py` | offline | FAIL(rc=1) | 10s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/dna_report_killswitch_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/dna_report_liquidity_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/dot2_batch_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/edge_wlag_gate_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/expected_volume_pacing_selfcheck.py` | offline | PASS | 24s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/failc_residual_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/failc_sweep8_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/failopen_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/failopen_telegram_refresh_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/fetch_bdi_daily_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/freshness_ops_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/hybrid_fill_timing_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/idle_rate_proxy_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/lag_adv_basis_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/lag_adv_cap_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/lag_dd_zone_gate_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/lag_governance_order_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/lag_live_schedule_selfcheck.py` | offline | PASS | 22s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/lag_rating_gate_snapshot_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/lag_rating_order_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/lag_rating_stale_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/lagged_cache_adjusted_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/logto_silent_defaults_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/macro_gate_health_tz_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/macro_healthcheck_sbv_reconfirm_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/macro_killswitch_a_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/money_path_freshness_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/navbasis_loud_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/oshares_dcf_selfcheck.py` | offline | PASS | 545s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/oshares_wire_selfcheck.py` | offline | PASS | 20s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/plan_cash_commitment_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/planpy_failopen_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/probe_linger_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/rating8l_eff_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/rating8l_icb_pit_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 51s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/rating_pit_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/refresh_earnings_surprise_pkl_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/route_selector_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/rubber_weekly_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/sbv_policy_verify_selfcheck.py` | offline | PASS | 17s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/sell_loan_package_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/te_macro_crosscheck_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/te_weekly_bash_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/tz_asof_ict_dd_dcf_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_adj/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/account_overrides_broker_resolution_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/anomaly_gate_freshness_session_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/atc_cancel_overorder_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 9s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/brokers_tradequantity_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/cctg6m_series_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/cctg_deposit_asof_ict_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/cctg_deposit_wiring_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/cctg_overlay_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/cctg_tier2_series_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/churn_guard_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/close_repair_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/concurrent_lock_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/cpi_vn_te_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/cq_hardcore_20261108_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/custom30_publish_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/custom30_publish_weight_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/custom_basket_forensic_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/daily_refresh_morning_selfcheck.sh` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/dc_book_waterfall_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/dcf_rate_display_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/dcf_rate_frame_selfcheck.py` | offline | PASS | 27s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/dcf_refresh_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/dcf_rstar_refresh_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/dcf_season_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/dcf_selector_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/dd_flag_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/deposit_fallback_direction_selfcheck.py` | offline | FAIL(rc=1) | 11s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/dna_report_killswitch_line_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/dna_report_liquidity_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/dot2_batch_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/dsr_family_manifest_selfcheck.py` | offline | PASS | 27s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 20s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/edge_wlag_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/expected_volume_pacing_selfcheck.py` | offline | PASS | 24s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/failc_residual_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/failc_sweep8_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/failopen_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/failopen_telegram_refresh_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/fetch_bdi_daily_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/freshness_ops_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 9s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/hybrid_fill_timing_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/idle_rate_proxy_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/lag_adv_basis_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/lag_adv_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/lag_dd_zone_gate_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/lag_governance_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/lag_live_schedule_selfcheck.py` | offline | PASS | 22s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/lag_rating_gate_snapshot_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/lag_rating_order_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/lag_rating_stale_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/lagged_cache_adjusted_selfcheck.py` | offline | PASS | 9s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/logto_silent_defaults_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/macro_gate_health_tz_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/macro_healthcheck_sbv_reconfirm_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/macro_killswitch_a_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/money_path_freshness_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/navbasis_loud_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/oshares_dcf_selfcheck.py` | offline | PASS | 546s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/oshares_wire_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/planpy_failopen_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/probe_linger_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/rating8l_eff_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/rating8l_icb_pit_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 53s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/rating_pit_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/refresh_earnings_surprise_pkl_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/route_selector_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/rubber_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/rule_a_ceiling_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/sbv_policy_verify_selfcheck.py` | offline | PASS | 17s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/sell_loan_package_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/te_macro_crosscheck_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/te_weekly_bash_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/tz_asof_ict_dd_dcf_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/m_vint/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/account_overrides_broker_resolution_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/churn_guard_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/custom30_publish_weight_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/dc_book_waterfall_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/dcf_check_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/dcf_refresh_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/dcf_selector_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/edge_wlag_gate_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/expected_volume_pacing_selfcheck.py` | offline | PASS | 25s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/failc_residual_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/failc_sweep8_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/freshness_ops_selfcheck.py` | offline | FAIL(rc=1) | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/hybrid_fill_timing_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/idle_cash_age_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/idle_rate_proxy_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/lag_adv_cap_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/lag_governance_order_gate_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/lag_live_schedule_selfcheck.py` | offline | PASS | 22s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/lag_rating_order_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/oshares_wire_selfcheck.py` | offline | PASS | 19s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/probe_linger_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/rating8l_icb_pit_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 43s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/route_selector_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/rubber_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/rule_a_ref_guard_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_adj/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/account_overrides_broker_resolution_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/approval_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/atc_postclose_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/churn_guard_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/custom30_publish_weight_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/dc_book_waterfall_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/dcf_refresh_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/dcf_selector_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/edge_wlag_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/expected_volume_pacing_selfcheck.py` | offline | PASS | 25s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/failc_residual_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/failc_sweep8_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/freshness_ops_selfcheck.py` | offline | FAIL(rc=1) | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 9s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/hybrid_fill_timing_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/idle_cash_age_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/idle_rate_proxy_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/lag_adv_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/lag_governance_order_gate_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/lag_live_schedule_selfcheck.py` | offline | PASS | 23s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/lag_rating_order_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/money_path_freshness_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/oshares_selfcheck_fixture.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/oshares_wire_selfcheck.py` | offline | PASS | 19s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/probe_linger_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/rating8l_icb_pit_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 42s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/route_selector_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/rubber_weekly_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/rule_a_ref_guard_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A5/sb/r_vint/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/account_overrides_broker_resolution_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/anomaly_gate_freshness_session_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/atc_cancel_overorder_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/basket_price_basis_audit_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/brokers_tradequantity_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/cctg6m_series_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/cctg_deposit_asof_ict_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/cctg_deposit_wiring_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/cctg_overlay_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/cctg_tier2_series_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/churn_guard_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/close_repair_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/cpi_vn_te_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/cq_hardcore_20261108_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/custom30_publish_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/custom30_publish_weight_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/custom_basket_forensic_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/daily_refresh_morning_selfcheck.sh` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/dc_book_waterfall_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/dcf_rate_display_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/dcf_rate_frame_selfcheck.py` | offline | PASS | 28s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/dcf_refresh_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/dcf_rstar_refresh_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/dcf_season_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/dcf_selector_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/dd_flag_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/deposit_fallback_direction_selfcheck.py` | offline | FAIL(rc=1) | 11s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/dna_report_killswitch_line_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/dna_report_liquidity_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/dot2_batch_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/edge_wlag_gate_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/expected_volume_pacing_selfcheck.py` | offline | PASS | 24s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/failc_residual_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/failc_sweep8_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/failopen_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/failopen_telegram_refresh_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/fetch_bdi_daily_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/freshness_ops_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/hybrid_fill_timing_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/idle_cash_age_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/idle_rate_proxy_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/lag_adv_basis_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/lag_adv_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/lag_dd_zone_gate_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/lag_governance_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/lag_live_schedule_selfcheck.py` | offline | PASS | 23s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/lag_rating_gate_snapshot_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/lag_rating_stale_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/lagged_cache_adjusted_selfcheck.py` | offline | PASS | 9s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/logto_silent_defaults_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/macro_gate_health_tz_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/macro_healthcheck_sbv_reconfirm_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/macro_killswitch_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/navbasis_loud_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/netting_recon_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/oshares_dcf_selfcheck.py` | offline | PASS | 545s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/oshares_wire_selfcheck.py` | offline | PASS | 20s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/paper_main_window_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/planpy_failopen_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/probe_linger_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/rating8l_eff_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/rating8l_icb_pit_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 54s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/rating_pit_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/refresh_earnings_surprise_pkl_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/route_selector_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/rubber_weekly_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/sbv_policy_verify_selfcheck.py` | offline | PASS | 16s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/screen_sort_direction_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/sell_loan_package_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/te_macro_crosscheck_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/te_weekly_bash_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/tz_asof_ict_dd_dcf_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_adj/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/account_overrides_broker_resolution_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/anomaly_gate_freshness_session_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/anomaly_gate_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/atc_cancel_overorder_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/basket_price_basis_audit_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/brokers_tradequantity_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/cctg6m_series_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/cctg_deposit_asof_ict_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/cctg_deposit_wiring_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/cctg_overlay_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/cctg_tier2_series_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/churn_guard_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/close_repair_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/cpi_vn_te_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/cq_hardcore_20261108_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/custom30_publish_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/custom30_publish_weight_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/custom_basket_forensic_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/daily_refresh_morning_selfcheck.sh` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/dc_book_waterfall_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/dcf_check_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/dcf_rate_display_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/dcf_rate_frame_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/dcf_refresh_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/dcf_rstar_refresh_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/dcf_season_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/dcf_selector_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/dd_flag_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/deposit_fallback_direction_selfcheck.py` | offline | FAIL(rc=1) | 10s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/dna_report_killswitch_line_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/dna_report_liquidity_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/dot2_batch_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 12s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/edge_wlag_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/expected_volume_pacing_selfcheck.py` | offline | PASS | 24s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/failc_residual_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/failc_sweep8_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/failopen_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/failopen_telegram_refresh_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/fetch_bdi_daily_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/freshness_ops_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 9s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/hybrid_fill_timing_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/idle_cash_age_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/idle_rate_proxy_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/lag_adv_basis_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/lag_adv_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/lag_dd_zone_gate_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/lag_governance_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/lag_live_schedule_selfcheck.py` | offline | PASS | 23s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/lag_rating_gate_snapshot_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/lag_rating_stale_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/lagged_cache_adjusted_selfcheck.py` | offline | PASS | 9s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/logto_silent_defaults_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/macro_gate_health_tz_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/macro_healthcheck_sbv_reconfirm_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/macro_killswitch_a_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/navbasis_loud_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/oshares_dcf_selfcheck.py` | offline | PASS | 545s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/oshares_wire_selfcheck.py` | offline | PASS | 19s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/pacing_horizon_note_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/planpy_failopen_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/probe_linger_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/rating8l_eff_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/rating8l_icb_pit_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 52s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/rating_pit_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/refresh_earnings_surprise_pkl_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/route_selector_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/rubber_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/sbv_policy_verify_selfcheck.py` | offline | PASS | 17s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/sell_loan_package_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/te_macro_crosscheck_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/te_weekly_bash_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/tz_asof_ict_dd_dcf_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/sb/c_vint/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_A6/selfchecks.sh` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/account_overrides_broker_resolution_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/anomaly_gate_freshness_session_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/atc_cancel_overorder_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/basket_price_basis_audit_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/brokers_tradequantity_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/cctg6m_series_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/cctg_deposit_asof_ict_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/cctg_deposit_wiring_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/cctg_overlay_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/cctg_tier2_series_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/churn_guard_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/close_repair_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/cpi_vn_te_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/cq_hardcore_20261108_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/custom30_publish_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/custom30_publish_weight_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/custom_basket_forensic_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/daily_refresh_morning_selfcheck.sh` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/dc_book_waterfall_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/dcf_rate_display_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/dcf_rate_frame_selfcheck.py` | offline | PASS | 28s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/dcf_refresh_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/dcf_rstar_refresh_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/dcf_season_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/dcf_selector_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/dd_flag_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/deposit_fallback_direction_selfcheck.py` | offline | FAIL(rc=1) | 10s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/discretionary_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/dna_report_killswitch_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/dna_report_liquidity_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/dot2_batch_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 12s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/edge_wlag_gate_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/expected_volume_pacing_selfcheck.py` | offline | PASS | 25s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/extreme_regime_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/failc_residual_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/failc_sweep8_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/failopen_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/failopen_telegram_refresh_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/fetch_bdi_daily_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/freshness_ops_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 9s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/hybrid_fill_timing_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/idle_cash_age_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/idle_rate_proxy_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/lag_adv_basis_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/lag_adv_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/lag_dd_zone_gate_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/lag_governance_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/lag_live_schedule_selfcheck.py` | offline | PASS | 23s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/lag_rating_gate_snapshot_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/lag_rating_order_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/lag_rating_stale_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/lagged_cache_adjusted_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/logto_silent_defaults_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/macro_gate_health_tz_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/macro_healthcheck_sbv_reconfirm_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/macro_killswitch_a_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/money_path_freshness_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/navbasis_loud_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/oshares_dcf_selfcheck.py` | offline | PASS | 542s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/oshares_wire_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/planpy_failopen_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/probe_linger_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/rating8l_eff_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/rating8l_icb_pit_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 52s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/rating_pit_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/refresh_earnings_surprise_pkl_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/route_selector_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/rubber_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/sbv_policy_verify_selfcheck.py` | offline | PASS | 17s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/sell_loan_package_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/te_macro_crosscheck_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/te_weekly_bash_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/tz_asof_ict_dd_dcf_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_exec_D/sb_D/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/account_overrides_broker_resolution_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/anomaly_gate_freshness_session_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/anomaly_gate_selfcheck.py` | offline | PASS | 9s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/atc_cancel_overorder_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/basket_price_basis_audit_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/brokers_tradequantity_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/cctg6m_series_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/cctg_deposit_asof_ict_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/cctg_deposit_wiring_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/cctg_overlay_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/cctg_tier2_series_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/churn_guard_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/close_repair_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/cpi_vn_te_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/cq_hardcore_20261108_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/custom30_publish_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/custom30_publish_weight_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/custom_basket_forensic_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/daily_refresh_morning_selfcheck.sh` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/dc_book_waterfall_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/dcf_rate_display_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/dcf_rate_frame_selfcheck.py` | offline | PASS | 27s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/dcf_refresh_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/dcf_rstar_refresh_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/dcf_season_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/dcf_selector_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/dd_flag_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/deposit_fallback_direction_selfcheck.py` | offline | FAIL(rc=1) | 10s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/dna_report_killswitch_line_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/dna_report_liquidity_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/dot2_batch_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 12s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/edge_wlag_gate_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/expected_volume_pacing_selfcheck.py` | offline | PASS | 25s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/failc_residual_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/failc_sweep8_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/failopen_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/failopen_telegram_refresh_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/fetch_bdi_daily_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/freshness_ops_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 9s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/hybrid_fill_timing_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/idle_rate_proxy_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/lag_adv_basis_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/lag_adv_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/lag_dd_zone_gate_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/lag_governance_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/lag_live_schedule_selfcheck.py` | offline | PASS | 22s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/lag_rating_gate_snapshot_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/lag_rating_order_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/lag_rating_stale_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/lagged_cache_adjusted_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/logto_silent_defaults_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/macro_gate_health_tz_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/macro_healthcheck_sbv_reconfirm_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/macro_killswitch_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/navbasis_loud_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/oshares_dcf_selfcheck.py` | offline | PASS | 542s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/oshares_wire_selfcheck.py` | offline | PASS | 22s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 3s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/planpy_failopen_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/probe_linger_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/rating8l_eff_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/rating8l_icb_pit_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 52s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/rating_pit_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/refresh_earnings_surprise_pkl_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/route_selector_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/rubber_weekly_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/sbv_policy_verify_selfcheck.py` | offline | PASS | 16s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/screen_sort_direction_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/sell_loan_package_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/te_macro_crosscheck_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/te_weekly_bash_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/tz_asof_ict_dd_dcf_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_adj/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/account_overrides_broker_resolution_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/anomaly_gate_freshness_session_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/anomaly_gate_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/atc_cancel_overorder_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/basket_price_basis_audit_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/brokers_tradequantity_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/cctg6m_series_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/cctg_deposit_asof_ict_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/cctg_deposit_wiring_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/cctg_overlay_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/cctg_tier2_series_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/churn_guard_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/close_repair_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/cpi_vn_te_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/cq_hardcore_20261108_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/custom30_publish_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/custom30_publish_weight_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/custom_basket_forensic_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/daily_refresh_morning_selfcheck.sh` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/dc_book_waterfall_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/dcf_rate_display_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/dcf_rate_frame_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/dcf_refresh_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/dcf_rstar_refresh_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/dcf_season_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/dcf_selector_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/dd_flag_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/deposit_fallback_direction_selfcheck.py` | offline | FAIL(rc=1) | 11s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/dna_report_killswitch_line_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/dna_report_liquidity_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/dot2_batch_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 13s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/edge_wlag_gate_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/expected_volume_pacing_selfcheck.py` | offline | PASS | 24s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/failc_residual_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/failc_sweep8_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/failopen_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/failopen_telegram_refresh_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/fetch_bdi_daily_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/freshness_ops_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 9s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/hybrid_fill_timing_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/idle_rate_proxy_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/lag_adv_basis_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/lag_adv_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/lag_dd_zone_gate_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/lag_governance_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/lag_live_schedule_selfcheck.py` | offline | PASS | 22s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/lag_rating_gate_snapshot_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/lag_rating_order_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/lag_rating_stale_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/lagged_cache_adjusted_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/logto_silent_defaults_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/macro_gate_health_tz_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/macro_healthcheck_sbv_reconfirm_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/macro_killswitch_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/navbasis_loud_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/oshares_dcf_selfcheck.py` | offline | PASS | 544s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/oshares_wire_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/paper_main_window_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/planpy_failopen_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/probe_linger_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/rating8l_eff_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/rating8l_icb_pit_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 53s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/rating_pit_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/refresh_earnings_surprise_pkl_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/route_selector_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/rubber_weekly_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/sbv_policy_verify_selfcheck.py` | offline | PASS | 17s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/sell_loan_package_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/te_macro_crosscheck_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/te_weekly_bash_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/tz_asof_ict_dd_dcf_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1_20261112/sandbox_ctrl/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/account_overrides_broker_resolution_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/anomaly_gate_freshness_session_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/atc_cancel_overorder_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/basket_price_basis_audit_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/brokers_tradequantity_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/cctg6m_series_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/cctg_deposit_asof_ict_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/cctg_deposit_wiring_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/cctg_overlay_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/cctg_tier2_series_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/churn_guard_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/close_repair_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/cpi_vn_te_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/cq_hardcore_20261108_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/custom30_publish_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/custom30_publish_weight_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/custom_basket_forensic_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/daily_refresh_morning_selfcheck.sh` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/dc_book_waterfall_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/dcf_rate_display_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/dcf_rate_frame_selfcheck.py` | offline | PASS | 27s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/dcf_refresh_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/dcf_rstar_refresh_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/dcf_season_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/dcf_selector_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/dd_flag_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/deposit_fallback_direction_selfcheck.py` | offline | FAIL(rc=1) | 11s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/dna_report_killswitch_line_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/dna_report_liquidity_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/dot2_batch_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 13s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/edge_wlag_gate_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/expected_volume_pacing_selfcheck.py` | offline | PASS | 25s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/extreme_regime_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/failc_residual_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/failc_sweep8_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/failopen_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/failopen_telegram_refresh_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/fetch_bdi_daily_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/freshness_ops_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 9s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/hybrid_fill_timing_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/idle_rate_proxy_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/lag_adv_basis_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/lag_adv_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/lag_dd_zone_gate_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/lag_governance_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/lag_live_schedule_selfcheck.py` | offline | PASS | 23s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/lag_rating_gate_snapshot_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/lag_rating_stale_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/lagged_cache_adjusted_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/logto_silent_defaults_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/macro_gate_health_tz_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/macro_healthcheck_sbv_reconfirm_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/macro_killswitch_a_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/navbasis_loud_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/oshares_dcf_selfcheck.py` | offline | PASS | 544s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/oshares_wire_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/planpy_failopen_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/probe_linger_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/rating8l_eff_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/rating8l_icb_pit_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 52s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/rating_pit_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/refresh_earnings_surprise_pkl_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/route_selector_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/rubber_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/sbv_policy_verify_selfcheck.py` | offline | PASS | 17s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/sell_loan_package_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/t2_settlement_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/te_macro_crosscheck_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/te_weekly_bash_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/tz_asof_ict_dd_dcf_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fix/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/account_overrides_broker_resolution_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/anomaly_gate_freshness_session_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/atc_cancel_overorder_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/basket_price_basis_audit_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/brokers_tradequantity_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/cctg6m_series_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/cctg_deposit_asof_ict_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/cctg_deposit_wiring_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/cctg_overlay_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/cctg_tier2_series_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/churn_guard_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/close_repair_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/cpi_vn_te_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/cq_hardcore_20261108_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/custom30_publish_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/custom30_publish_weight_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/custom_basket_forensic_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/daily_refresh_morning_selfcheck.sh` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/dc_book_waterfall_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/dcf_rate_display_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/dcf_rate_frame_selfcheck.py` | offline | PASS | 27s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/dcf_refresh_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/dcf_rstar_refresh_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/dcf_season_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/dcf_selector_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/dd_flag_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/deposit_fallback_direction_selfcheck.py` | offline | FAIL(rc=1) | 10s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/dna_report_killswitch_line_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/dna_report_liquidity_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/dot2_batch_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 20s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 13s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/edge_wlag_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/expected_volume_pacing_selfcheck.py` | offline | PASS | 24s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/failc_residual_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/failc_sweep8_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/failopen_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/failopen_telegram_refresh_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/fetch_bdi_daily_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/freshness_ops_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/hybrid_fill_timing_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/idle_rate_proxy_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/lag_adv_basis_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/lag_adv_cap_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/lag_dd_zone_gate_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/lag_governance_order_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/lag_live_schedule_selfcheck.py` | offline | PASS | 22s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/lag_rating_gate_snapshot_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/lag_rating_stale_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/lagged_cache_adjusted_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/logto_silent_defaults_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/macro_gate_health_tz_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/macro_healthcheck_sbv_reconfirm_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/macro_killswitch_a_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/navbasis_loud_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/oshares_dcf_selfcheck.py` | offline | PASS | 544s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/oshares_wire_selfcheck.py` | offline | PASS | 22s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/planpy_failopen_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/probe_linger_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/rating8l_eff_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/rating8l_icb_pit_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 53s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/rating_pit_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/refresh_earnings_surprise_pkl_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/route_selector_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/rubber_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/sbv_policy_verify_selfcheck.py` | offline | PASS | 17s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/sell_loan_package_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/te_macro_crosscheck_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/te_weekly_bash_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/tz_asof_ict_dd_dcf_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_fixswapall/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/account_overrides_broker_resolution_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/anomaly_gate_freshness_session_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/approval_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/atc_cancel_overorder_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/atc_postclose_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/basket_price_basis_audit_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/brokers_tradequantity_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/cctg6m_series_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/cctg_deposit_asof_ict_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/cctg_deposit_wiring_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/cctg_overlay_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/cctg_tier2_series_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/churn_guard_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/close_repair_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/cpi_vn_te_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/cq_hardcore_20261108_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/custom30_publish_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/custom30_publish_weight_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/custom_basket_forensic_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/daily_refresh_morning_selfcheck.sh` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/dc_book_waterfall_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/dcf_check_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/dcf_rate_display_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/dcf_rate_frame_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/dcf_refresh_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/dcf_rstar_refresh_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/dcf_season_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/dcf_selector_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/dd_flag_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/deposit_fallback_direction_selfcheck.py` | offline | FAIL(rc=1) | 10s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/discretionary_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/dna_report_killswitch_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/dna_report_liquidity_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/dot2_batch_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 12s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/edge_wlag_gate_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/expected_volume_pacing_selfcheck.py` | offline | PASS | 24s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/failc_residual_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/failc_sweep8_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/failopen_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/failopen_telegram_refresh_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/fetch_bdi_daily_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/freshness_ops_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/hybrid_fill_timing_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/idle_rate_proxy_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/lag_adv_basis_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/lag_adv_cap_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/lag_dd_zone_gate_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/lag_governance_order_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/lag_live_schedule_selfcheck.py` | offline | PASS | 22s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/lag_rating_gate_snapshot_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/lag_rating_stale_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/lagged_cache_adjusted_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/logto_silent_defaults_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/macro_gate_health_tz_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/macro_healthcheck_sbv_reconfirm_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/macro_killswitch_a_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/money_path_freshness_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/navbasis_loud_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/oshares_dcf_selfcheck.py` | offline | PASS | 565s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/oshares_wire_selfcheck.py` | offline | PASS | 22s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/plan_cash_commitment_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/planpy_failopen_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/probe_linger_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/rating8l_eff_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/rating8l_icb_pit_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 53s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/rating_pit_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/refresh_earnings_surprise_pkl_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/route_selector_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/rubber_weekly_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/sbv_policy_verify_selfcheck.py` | offline | PASS | 17s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/sell_loan_package_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/te_macro_crosscheck_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/te_weekly_bash_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/tz_asof_ict_dd_dcf_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_liq/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/account_overrides_broker_resolution_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/anomaly_gate_freshness_session_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/atc_cancel_overorder_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/basket_price_basis_audit_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/book_tagging_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/brokers_cash_fields_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/brokers_tradequantity_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/cctg6m_series_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/cctg_deposit_asof_ict_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/cctg_deposit_wiring_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/cctg_overlay_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/cctg_tier2_series_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/churn_guard_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/close_repair_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/cpi_vn_te_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/cq_hardcore_20261108_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/custom30_publish_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/custom30_publish_weight_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/custom_basket_forensic_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/daily_refresh_morning_selfcheck.sh` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/dc_book_waterfall_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/dcf_rate_display_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/dcf_rate_frame_selfcheck.py` | offline | PASS | 27s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/dcf_refresh_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/dcf_rstar_refresh_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/dcf_season_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/dcf_selector_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/dd_flag_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/deposit_fallback_direction_selfcheck.py` | offline | FAIL(rc=1) | 10s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/discretionary_accumulation_selfcheck.py` | offline | PASS | 20s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/discretionary_target_pct_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/dna_report_killswitch_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/dna_report_liquidity_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/dot2_batch_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/due_diligence_selfcheck.py` | offline | PASS | 92s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/dynamic_no_chase_ceiling_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/edge_wlag_gate_selfcheck.py` | offline | PASS | 24s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/exdate_price_frame_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/expected_volume_pacing_selfcheck.py` | offline | PASS | 24s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/expvol_shadow_probe_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/failc_residual_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/failc_sweep8_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/failopen_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/failopen_telegram_refresh_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/fetch_bdi_daily_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/freshness_ops_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/hard_no_chase_ceiling_selfcheck.py` | offline | PASS | 10s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/hybrid_fill_timing_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/idle_rate_proxy_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/lag_adv_basis_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/lag_adv_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/lag_dd_zone_gate_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/lag_forensic_filter_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/lag_governance_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/lag_live_schedule_selfcheck.py` | offline | PASS | 23s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/lag_rating_gate_snapshot_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/lag_rating_stale_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/lagged_cache_adjusted_selfcheck.py` | offline | PASS | 9s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/logto_silent_defaults_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/macro_gate_health_tz_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/macro_healthcheck_sbv_reconfirm_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/macro_killswitch_a_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/navbasis_loud_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/order_book_shadow_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/oshares_dcf_selfcheck.py` | offline | PASS | 545s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/oshares_wire_selfcheck.py` | offline | PASS | 20s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/pacing_horizon_note_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/paper_probe_netting_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/plan_check_field_schema_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/plan_funding_gate_selfcheck.py` | offline | PASS | 10s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/planpy_failopen_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/probe_linger_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/rating8l_eff_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/rating8l_icb_pit_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 53s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/rating_pit_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/refresh_earnings_surprise_pkl_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/route_selector_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/rubber_weekly_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/sbv_policy_verify_selfcheck.py` | offline | PASS | 17s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/sell_loan_package_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/t2_settlement_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/te_macro_crosscheck_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/te_weekly_bash_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/tz_asof_ict_dd_dcf_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_main/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/account_overrides_broker_resolution_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/anomaly_gate_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/basket_price_basis_audit_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/churn_guard_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/custom30_publish_weight_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/dc_book_waterfall_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/dcf_refresh_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/dcf_selector_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/discretionary_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 12s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/edge_wlag_gate_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/expected_volume_pacing_selfcheck.py` | offline | PASS | 24s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/failc_residual_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/failc_sweep8_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/freshness_ops_selfcheck.py` | offline | FAIL(rc=1) | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/hybrid_fill_timing_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/idle_cash_age_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/idle_rate_proxy_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/lag_adv_cap_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/lag_governance_order_gate_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/lag_live_schedule_selfcheck.py` | offline | PASS | 22s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/oshares_wire_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/plan_cash_commitment_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/probe_linger_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/rating8l_icb_pit_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 44s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/route_selector_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/rubber_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/rule_a_ceiling_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/rule_a_ref_guard_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/screen_sort_direction_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_pincode/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/account_overrides_broker_resolution_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/anomaly_gate_freshness_session_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/anomaly_gate_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/atc_cancel_overorder_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 15s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/basket_price_basis_audit_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/book_tagging_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/brokers_cash_fields_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/brokers_tradequantity_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/cctg6m_series_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/cctg_deposit_asof_ict_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/cctg_deposit_wiring_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/cctg_overlay_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/cctg_tier2_series_selfcheck.py` | offline | PASS | 16s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/churn_guard_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/close_repair_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/cpi_vn_te_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/cq_hardcore_20261108_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/custom30_publish_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/custom30_publish_weight_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/custom_basket_forensic_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/daily_refresh_morning_selfcheck.sh` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/dc_book_waterfall_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/dcf_rate_display_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/dcf_rate_frame_selfcheck.py` | offline | PASS | 34s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/dcf_refresh_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/dcf_rstar_refresh_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/dcf_season_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/dcf_selector_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/dd_flag_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/deposit_fallback_direction_selfcheck.py` | offline | FAIL(rc=1) | 10s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/discretionary_accumulation_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/discretionary_target_pct_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/dna_report_killswitch_line_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/dna_report_liquidity_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/dot2_batch_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/dsr_family_manifest_selfcheck.py` | offline | PASS | 27s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/due_diligence_selfcheck.py` | offline | PASS | 90s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/dynamic_no_chase_ceiling_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/edge_wlag_gate_selfcheck.py` | offline | PASS | 25s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/exdate_price_frame_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/expected_volume_pacing_selfcheck.py` | offline | PASS | 24s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/expvol_shadow_probe_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/failc_residual_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/failc_sweep8_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/failopen_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/failopen_telegram_refresh_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/fetch_bdi_daily_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/freshness_ops_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/hard_no_chase_ceiling_selfcheck.py` | offline | PASS | 10s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/hybrid_fill_timing_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/idle_rate_proxy_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/lag_adv_basis_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/lag_adv_cap_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/lag_dd_zone_gate_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/lag_forensic_filter_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/lag_governance_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/lag_live_schedule_selfcheck.py` | offline | PASS | 22s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/lag_rating_gate_snapshot_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/lag_rating_stale_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/lagged_cache_adjusted_selfcheck.py` | offline | PASS | 9s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/logto_silent_defaults_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/macro_gate_health_tz_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/macro_healthcheck_sbv_reconfirm_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/macro_killswitch_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/navbasis_loud_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/netting_recon_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/order_book_shadow_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/oshares_dcf_selfcheck.py` | offline | PASS | 549s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/oshares_wire_selfcheck.py` | offline | PASS | 27s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/paper_probe_netting_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/plan_funding_gate_selfcheck.py` | offline | PASS | 11s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/planpy_failopen_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/probe_linger_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/rating8l_eff_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/rating8l_icb_pit_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 56s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/rating_pit_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/refresh_earnings_surprise_pkl_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/refresh_skip_participation_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/route_selector_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/rubber_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/rule_a_ceiling_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/sbv_policy_verify_selfcheck.py` | offline | PASS | 17s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/screen_sort_direction_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/sell_loan_package_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/te_macro_crosscheck_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/te_weekly_bash_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/tz_asof_ict_dd_dcf_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapall/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/account_overrides_broker_resolution_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/anomaly_gate_freshness_session_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/atc_cancel_overorder_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/basket_price_basis_audit_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/book_tagging_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/brokers_cash_fields_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/brokers_tradequantity_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/cctg6m_series_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/cctg_deposit_asof_ict_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/cctg_deposit_wiring_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/cctg_overlay_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/cctg_tier2_series_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/churn_guard_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/close_repair_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/cpi_vn_te_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/cq_hardcore_20261108_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/custom30_publish_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/custom30_publish_weight_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/custom_basket_forensic_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/daily_refresh_morning_selfcheck.sh` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/dc_book_waterfall_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/dcf_check_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/dcf_rate_display_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/dcf_rate_frame_selfcheck.py` | offline | PASS | 32s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/dcf_refresh_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/dcf_rstar_refresh_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/dcf_season_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/dcf_selector_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/dd_flag_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/deposit_fallback_direction_selfcheck.py` | offline | FAIL(rc=1) | 11s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/discretionary_accumulation_selfcheck.py` | offline | PASS | 20s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/discretionary_target_pct_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/dna_report_killswitch_line_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/dna_report_liquidity_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/dot2_batch_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/due_diligence_selfcheck.py` | offline | PASS | 91s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/dynamic_no_chase_ceiling_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/edge_wlag_gate_selfcheck.py` | offline | PASS | 24s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/exdate_price_frame_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/expected_volume_pacing_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/expvol_shadow_probe_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/failc_residual_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/failc_sweep8_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/failopen_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/failopen_telegram_refresh_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/fetch_bdi_daily_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/freshness_ops_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/hard_no_chase_ceiling_selfcheck.py` | offline | PASS | 10s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/hybrid_fill_timing_selfcheck.py` | offline | PASS | 9s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/idle_rate_proxy_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/lag_adv_basis_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/lag_adv_cap_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/lag_dd_zone_gate_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/lag_forensic_filter_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/lag_governance_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/lag_live_schedule_selfcheck.py` | offline | PASS | 24s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/lag_rating_gate_snapshot_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/lag_rating_stale_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/lagged_cache_adjusted_selfcheck.py` | offline | PASS | 11s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/logto_silent_defaults_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/macro_gate_health_tz_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/macro_healthcheck_sbv_reconfirm_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/macro_killswitch_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/navbasis_loud_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/order_book_shadow_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/oshares_dcf_selfcheck.py` | offline | PASS | 606s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/oshares_wire_selfcheck.py` | offline | PASS | 22s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/paper_probe_netting_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/plan_funding_gate_selfcheck.py` | offline | PASS | 11s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/planpy_failopen_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/probe_linger_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/rating8l_eff_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/rating8l_icb_pit_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 53s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/rating_pit_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/refresh_earnings_surprise_pkl_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/route_selector_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/rubber_weekly_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/sbv_policy_verify_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/screen_sort_direction_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/sell_loan_package_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/te_macro_crosscheck_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/te_weekly_bash_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/tz_asof_ict_dd_dcf_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapeh/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/account_overrides_broker_resolution_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/anomaly_gate_freshness_session_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/anomaly_gate_selfcheck.py` | offline | PASS | 9s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/atc_cancel_overorder_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 15s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/basket_price_basis_audit_selfcheck.py` | offline | PASS | 11s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/book_tagging_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/brokers_cash_fields_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/brokers_tradequantity_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/capit_participation_cap_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/cctg6m_series_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/cctg_deposit_asof_ict_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/cctg_deposit_wiring_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/cctg_overlay_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/cctg_tier2_series_selfcheck.py` | offline | PASS | 17s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/churn_guard_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/close_repair_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/cpi_vn_te_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/cq_hardcore_20261108_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/custom30_publish_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/custom30_publish_weight_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/custom_basket_forensic_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/daily_refresh_morning_selfcheck.sh` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/dc_book_waterfall_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/dcf_rate_display_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/dcf_rate_frame_selfcheck.py` | offline | PASS | 42s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/dcf_refresh_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/dcf_rstar_refresh_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/dcf_season_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/dcf_selector_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/dd_flag_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/deposit_fallback_direction_selfcheck.py` | offline | FAIL(rc=1) | 11s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/discretionary_accumulation_selfcheck.py` | offline | PASS | 20s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/discretionary_participation_cap_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/discretionary_target_pct_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/dna_report_killswitch_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/dna_report_liquidity_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/dot2_batch_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/dsr_family_manifest_selfcheck.py` | offline | PASS | 29s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/due_diligence_selfcheck.py` | offline | PASS | 98s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/dynamic_no_chase_ceiling_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/edge_wlag_gate_selfcheck.py` | offline | PASS | 25s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/exdate_price_frame_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/expected_volume_pacing_selfcheck.py` | offline | PASS | 24s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/expvol_shadow_probe_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/failc_residual_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/failc_sweep8_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/failopen_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/failopen_telegram_refresh_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/fetch_bdi_daily_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/freshness_ops_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/hard_no_chase_ceiling_selfcheck.py` | offline | PASS | 10s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/hybrid_fill_timing_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/idle_rate_proxy_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/lag_adv_basis_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/lag_adv_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/lag_dd_zone_gate_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/lag_forensic_filter_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/lag_governance_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/lag_live_schedule_selfcheck.py` | offline | PASS | 23s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/lag_rating_gate_snapshot_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/lag_rating_stale_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/lagged_cache_adjusted_selfcheck.py` | offline | PASS | 9s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/logto_silent_defaults_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/macro_gate_health_tz_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/macro_healthcheck_sbv_reconfirm_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/macro_killswitch_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/navbasis_loud_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/order_book_shadow_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/oshares_dcf_selfcheck.py` | offline | PASS | 545s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/oshares_wire_selfcheck.py` | offline | PASS | 20s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/pacing_horizon_note_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/paper_probe_netting_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/plan_check_field_schema_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/plan_funding_gate_selfcheck.py` | offline | PASS | 10s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/planpy_failopen_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/probe_linger_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/rating8l_eff_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/rating8l_icb_pit_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 55s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/rating_pit_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/refresh_earnings_surprise_pkl_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/route_selector_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/rubber_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/sbv_policy_verify_selfcheck.py` | offline | PASS | 17s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/sell_loan_package_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/te_macro_crosscheck_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/te_weekly_bash_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/tz_asof_ict_dd_dcf_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapesd/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/account_overrides_broker_resolution_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/anomaly_gate_freshness_session_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/approval_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/atc_cancel_overorder_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/atc_postclose_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/basket_price_basis_audit_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/book_tagging_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/brokers_cash_fields_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/brokers_tradequantity_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/cctg6m_series_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/cctg_deposit_asof_ict_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/cctg_deposit_wiring_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/cctg_overlay_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/cctg_tier2_series_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/churn_guard_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/close_repair_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/cpi_vn_te_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/cq_hardcore_20261108_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/custom30_publish_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/custom30_publish_weight_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/custom_basket_forensic_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/daily_refresh_morning_selfcheck.sh` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/dc_book_waterfall_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/dcf_rate_display_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/dcf_rate_frame_selfcheck.py` | offline | PASS | 28s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/dcf_refresh_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/dcf_rstar_refresh_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/dcf_season_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/dcf_selector_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/dd_flag_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/deposit_fallback_direction_selfcheck.py` | offline | FAIL(rc=1) | 10s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/discretionary_accumulation_selfcheck.py` | offline | PASS | 20s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/discretionary_participation_cap_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/discretionary_target_pct_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/dna_report_killswitch_line_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/dna_report_liquidity_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/dot2_batch_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/due_diligence_selfcheck.py` | offline | PASS | 91s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/dynamic_no_chase_ceiling_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/edge_wlag_gate_selfcheck.py` | offline | PASS | 24s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/exdate_price_frame_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/expected_volume_pacing_selfcheck.py` | offline | PASS | 25s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/expvol_shadow_probe_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/extreme_regime_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/failc_residual_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/failc_sweep8_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/failopen_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/failopen_telegram_refresh_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/fetch_bdi_daily_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/freshness_ops_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/hard_no_chase_ceiling_selfcheck.py` | offline | PASS | 16s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/hybrid_fill_timing_selfcheck.py` | offline | PASS | 10s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/idle_rate_proxy_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/lag_adv_basis_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/lag_adv_cap_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/lag_dd_zone_gate_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/lag_forensic_filter_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/lag_governance_order_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/lag_live_schedule_selfcheck.py` | offline | PASS | 23s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/lag_rating_gate_snapshot_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/lag_rating_order_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/lag_rating_stale_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/lagged_cache_adjusted_selfcheck.py` | offline | PASS | 9s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/logto_silent_defaults_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/macro_gate_health_tz_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/macro_healthcheck_sbv_reconfirm_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/macro_killswitch_a_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/money_path_freshness_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/navbasis_loud_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/order_book_shadow_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/oshares_dcf_selfcheck.py` | offline | PASS | 544s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/oshares_wire_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/paper_probe_netting_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/plan_funding_gate_selfcheck.py` | offline | PASS | 11s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/planpy_failopen_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/probe_linger_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/rating8l_eff_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/rating8l_icb_pit_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 56s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/rating_pit_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/refresh_earnings_surprise_pkl_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/route_selector_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/rubber_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/sbv_policy_verify_selfcheck.py` | offline | PASS | 17s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/sell_loan_package_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/te_macro_crosscheck_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/te_weekly_bash_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/tz_asof_ict_dd_dcf_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_swapev/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/account_overrides_broker_resolution_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/anomaly_gate_freshness_session_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/anomaly_gate_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/approval_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/atc_cancel_overorder_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/basket_price_basis_audit_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/brokers_tradequantity_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/cctg6m_series_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/cctg_deposit_asof_ict_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/cctg_deposit_wiring_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/cctg_overlay_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/cctg_tier2_series_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/churn_guard_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/close_repair_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/cpi_vn_te_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/cq_hardcore_20261108_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/custom30_publish_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/custom30_publish_weight_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/custom_basket_forensic_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/daily_refresh_morning_selfcheck.sh` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/dc_book_waterfall_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/dcf_rate_display_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/dcf_rate_frame_selfcheck.py` | offline | PASS | 27s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/dcf_refresh_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/dcf_rstar_refresh_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/dcf_season_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/dcf_selector_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/dd_flag_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/deposit_fallback_direction_selfcheck.py` | offline | FAIL(rc=1) | 10s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/discretionary_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/dna_report_killswitch_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/dna_report_liquidity_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/dot2_batch_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/dsr_family_manifest_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 13s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/edge_wlag_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/expected_volume_pacing_selfcheck.py` | offline | PASS | 25s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/extreme_regime_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/failc_residual_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/failc_sweep8_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/failopen_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/failopen_telegram_refresh_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/fetch_bdi_daily_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/freshness_ops_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 9s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/hybrid_fill_timing_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/idle_rate_proxy_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/lag_adv_basis_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/lag_adv_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/lag_dd_zone_gate_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/lag_governance_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/lag_live_schedule_selfcheck.py` | offline | PASS | 23s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/lag_rating_gate_snapshot_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/lag_rating_stale_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/lagged_cache_adjusted_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/logto_silent_defaults_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/macro_gate_health_tz_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/macro_healthcheck_sbv_reconfirm_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/macro_killswitch_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/navbasis_loud_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/netting_recon_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/oshares_dcf_selfcheck.py` | offline | PASS | 546s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/oshares_wire_selfcheck.py` | offline | PASS | 21s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/planpy_failopen_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/probe_linger_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/rating8l_eff_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/rating8l_icb_pit_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 53s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/rating_pit_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/refresh_earnings_surprise_pkl_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/route_selector_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/rubber_weekly_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/sbv_policy_verify_selfcheck.py` | offline | PASS | 17s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/sell_loan_package_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/t2_settlement_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/te_macro_crosscheck_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/te_weekly_bash_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/tz_asof_ict_dd_dcf_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1b_20261112/sb_warmunadj/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/account_overrides_broker_resolution_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/anomaly_gate_freshness_session_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/anomaly_gate_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/approval_gate_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/atc_cancel_overorder_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/atc_postclose_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/atc_upcom_ordertype_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/auto_exit_rules_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/basket_oshares_step_exdate_selfcheck.py` | offline | PASS | 13s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/basket_price_basis_audit_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/basket_return_leg_oshares_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/brokers_cash_fields_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/brokers_nav_shadow_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/brokers_tradequantity_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/capit_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/cctg6m_series_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/cctg_deposit_asof_ict_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/cctg_deposit_wiring_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/cctg_overlay_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/cctg_tier2_series_selfcheck.py` | offline | PASS | 12s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/churn_guard_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/close_repair_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/cpi_vn_te_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/cpi_vn_tier15_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/cq_hard_boundary_20261004_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/cq_hardcore_20261108_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/custom30_publish_guard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/custom30_publish_weight_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/custom30_yield_labels_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/custom_basket_forensic_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/daily_refresh_morning_selfcheck.sh` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/dc_book_waterfall_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/dcf_check_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/dcf_rate_display_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/dcf_rate_frame_selfcheck.py` | offline | PASS | 28s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/dcf_refresh_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/dcf_rstar_refresh_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/dcf_season_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/dcf_selector_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/dd_flag_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/deposit_fallback_direction_selfcheck.py` | offline | FAIL(rc=1) | 11s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/discretionary_accumulation_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/discretionary_participation_cap_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/discretionary_rule_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/discretionary_target_pct_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/dna_report_killswitch_line_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/dna_report_liquidity_line_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/dot2_batch_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/dsr_family_manifest_selfcheck.py` | offline | PASS | 27s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/dt5g_chain_freshness_selfcheck.py` | offline | PASS | 20s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/due_diligence_selfcheck.py` | offline | FAIL(rc=1) | 13s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/dynamic_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/edge_wlag_gate_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/exdate_price_frame_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/expected_volume_pacing_selfcheck.py` | offline | PASS | 25s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/expvol_shadow_probe_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/extreme_regime_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/failc_residual_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/failc_sweep8_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/failopen_failclosed_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/failopen_telegram_refresh_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/fetch_bdi_daily_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/freshness_ops_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/gdkhq_rollout_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/ghost_order_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/hard_no_chase_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 9s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/hybrid_fill_timing_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/idle_rate_proxy_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/lag_adv_basis_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/lag_adv_cap_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/lag_dd_zone_gate_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/lag_forensic_filter_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/lag_governance_order_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/lag_live_schedule_selfcheck.py` | offline | PASS | 22s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/lag_rating_gate_snapshot_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/lag_rating_stale_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/lagged_cache_adjusted_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/loan_package_multi_account_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/logto_silent_defaults_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/macro_gate_health_tz_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/macro_healthcheck_sbv_reconfirm_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/macro_killswitch_a_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/navbasis_loud_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/netting_recon_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/order_book_shadow_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/oshares_dcf_selfcheck.py` | offline | PASS | 546s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/oshares_wire_selfcheck.py` | offline | PASS | 26s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/paper_probe_netting_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/plan_check_field_schema_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/plan_funding_gate_selfcheck.py` | offline | FAIL(rc=1) | 8s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/planpy_failopen_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/probe_linger_selfcheck.py` | offline | PASS | 7s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/rating8l_eff_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/rating8l_icb_pit_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 54s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/rating_pit_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/refresh_earnings_surprise_pkl_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/route_selector_selfcheck.py` | offline | PASS | 4s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/rubber_weekly_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/rule_a_ceiling_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/sbv_policy_verify_selfcheck.py` | offline | PASS | 17s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/screen_sort_direction_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/sell_loan_package_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/te_macro_crosscheck_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/te_weekly_bash_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/tz_asof_ict_dd_dcf_selfcheck.py` | offline | PASS | 3s |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/live_gap_phase1c_20261112/sb/v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/research/oshares_live_r10_20261031/run_dcf_selfchecks.sh` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/oshares_live_r11_20261031/run_dcf_selfchecks.sh` | offline | PASS | 0s |
| `mike/agents/Taylor/research/oshares_live_r12_20261031/run_dcf_selfchecks.sh` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/research/oshares_live_r12_20261031/run_selfcheck.sh` | offline | PASS | 0s |
| `mike/agents/Taylor/research/oshares_live_r8_20261031/run_dcf_selfchecks.sh` | offline | FAIL(rc=124) | 60s |
| `mike/agents/Taylor/research/oshares_live_r9_20261031/run_dcf_selfchecks.sh` | offline | PASS | 0s |
| `mike/agents/Taylor/research/pump_before_raise_flag_20260817/selfcheck_pump_flag.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/report_style_v2_20261031/selfcheck.py` | offline | FAIL(rc=1) | 9s |
| `mike/agents/Taylor/research/serial_capital_raiser_20260817/selfcheck_serial.py` | offline | FAIL(rc=1) | 9s |
| `mike/agents/Taylor/research/ta_model_5pct_20261106/selfcheck.py` | offline | FAIL(rc=1) | 16s |
| `mike/agents/Taylor/research/ta_schools_vn_20261025/selfcheck.py` | offline | PASS | 30s |
| `mike/agents/Taylor/research/treasury_reconcile_20260917/treasury_adjust_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/treasury_table_20260918/treasury_share_events_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/research/trend_basics_filter_20261025/selfcheck_hand.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/Taylor/research/vn_market_efficiency_20260910/selfcheck_efficiency.py` | offline | PASS | 1s |
| `mike/agents/Taylor/seccap_dyn_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/universe_freshness_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Wags/research/measured_by_20261013/run_related_selfchecks.sh` | offline | PASS | 0s |
| `mike/agents/Winston/freshness_warn_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/adjfactor_drift_detect_selfcheck.py` | offline | PASS | 32s |
| `mike/bin/annualization_basis_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/bin/append_event_selfcheck.py` | offline | PASS | 11s |
| `mike/bin/approve_plan_with_jit_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/arch_noise_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/asof_label_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/auto_exit_disc_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/auto_exit_inject_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/backup_freshness_check_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/backup_push_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/bctc_q3_chain_wiring_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/book_clearing_g3_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/bin/bq_freshness_check_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/bin/bq_freshness_morning_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/bq_price_freeze_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/broker_fill_confirm_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/build_universe_pit_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/bus_question_closure_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/bus_question_housekeeping_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/cash_identity_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/bin/check_report_cadence_quarterly_selfcheck.py` | offline | PASS | 49s |
| `mike/bin/check_report_cadence_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/circuit_expiry_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/claim_reply_selfcheck.sh` | offline | PASS | 1s |
| `mike/bin/classifier_denial_count_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/clear_books_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/cli_provider_selfcheck.sh` | offline | PASS | 70s |
| `mike/bin/close_plan_approval_questions_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/code_quality_autodispatch_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `mike/bin/code_quality_gate_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/code_quality_weekly_scope_selfcheck.sh` | offline | PASS | 2s |
| `mike/bin/commit_collision_gate_selfcheck.py` | offline | PASS | 7s |
| `mike/bin/commodity_cycle_forward_tracker_selfcheck.py` | offline | PASS | 19s |
| `mike/bin/commodity_freshness_monitor_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/commodity_nowcast_block_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/commodity_sue_decomp_forward_tracker_selfcheck.py` | offline | PASS | 3s |
| `mike/bin/compute_active_nav_broker_fills_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/compute_active_nav_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/compute_jit_unpark_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/compute_park_trim_selfcheck.py` | offline | PASS | 19s |
| `mike/bin/consolidate_git_scope_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/corp_action_auto_confirm_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/corp_action_broker_detect_selfcheck.py` | offline | PASS | 3s |
| `mike/bin/corp_action_daily_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/corp_action_feed_canary_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/corp_action_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/corp_actions_skip_unsupported_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/corp_actions_verify_cashleg_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/cursor_advance_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/custom30v_rebalance_watch_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/daily_dashboard_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/daily_decision_topic_wt_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/daily_nav_snapshot_broker_fills_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/daily_nav_snapshot_corpaction_error_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/daily_nav_snapshot_from_raw_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/daily_retro_failcause_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/daily_retro_measured_by_selfcheck.sh` | offline | PASS | 12s |
| `mike/bin/dd_price_zone_watch_selfcheck.py` | offline | PASS | 4s |
| `mike/bin/dd_price_zones_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/dd_zone_candidates_funnel_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/decision_actions_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/decision_inbox_cog_selfcheck.py` | offline | PASS | 5s |
| `mike/bin/decision_inbox_r2_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/decision_inbox_selfcheck.py` | offline | PASS | 3s |
| `mike/bin/diagnosis_evidence_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/discretionary_accumulation_inject_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/discretionary_candidate_funnel_selfcheck.py` | offline | PASS | 4s |
| `mike/bin/discretionary_dd_pick_selfcheck.py` | offline | PASS | 5s |
| `mike/bin/discretionary_margin_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/dispatch_bg_export_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/dispatch_discord_topic_selfcheck.sh` | offline | PASS | 46s |
| `mike/bin/dispatch_loop_hint_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/dispatch_question_hint_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/dispatch_round_cap_selfcheck.py` | offline | PASS | 10s |
| `mike/bin/dispatch_tiny_prompt_selfcheck.sh` | offline | PASS | 3s |
| `mike/bin/dispatch_token_telemetry_selfcheck.py` | offline | PASS | 76s |
| `mike/bin/dispatch_wakeup_gate_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/dispatch_wakeup_hint_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/dispatch_wc_root_anchor_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/dividend_adjusted_return_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/dri_buy_gate_watch_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/dt5g_publish_runs_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/bin/dt5g_publisher_gate_selfcheck.sh` | offline | PASS | 1s |
| `mike/bin/dt5g_writer_watch_selfcheck.sh` | offline | FAIL(rc=1) | 16s |
| `mike/bin/due_diligence_corp_flags_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/bin/egg_transfer_alert_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/eod_delivery_wiring_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/eod_report_v2_failopen_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/eod_trading_report_account_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/bin/exdate_frame_cashleg_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/exdate_frame_selfcheck.py` | offline | PASS | 9s |
| `mike/bin/expected_session_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/exrights_price_basis_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/fa_ratings_8l_future_rows_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/fa_ratings_conditional_rerate_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/fa_ratings_earnings_window_gate_selfcheck.sh` | offline | PASS | 3s |
| `mike/bin/fa_ratings_ticker_gate_selfcheck.sh` | offline | PASS | 140s |
| `mike/bin/failopen_batch1_selfcheck.py` | offline | PASS | 8s |
| `mike/bin/filter_lag_entry_window_selfcheck.py` | offline | PASS | 19s |
| `mike/bin/forensic_flag_review_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/fund_bench_cron_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/fund_restatement_selfcheck.py` | offline | PASS | 6s |
| `mike/bin/gate_block_question_selfcheck.py` | offline | PASS | 35s |
| `mike/bin/github_pat_expiry_check_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/hose_membership_refresh_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/intraday_oos_monthly_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/intraday_price_watch_selfcheck.py` | offline | PASS | 43s |
| `mike/bin/job_cancel_guard_selfcheck.py` | offline | PASS | 44s |
| `mike/bin/kb_hot_size_gate_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/kb_nightly_backup_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/kb_nightly_ctxbloat_split_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/kb_nightly_phase1_atomic_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/lag_dd_gate_selfcheck.py` | offline | PASS | 24s |
| `mike/bin/lag_plan_calendar_check_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/lag_plan_consistency_check_selfcheck.py` | offline | PASS | 6s |
| `mike/bin/lag_rights_exit_hold_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/ledger_anchor_check_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/ledger_seal_weekly_selfcheck.py` | offline | PASS | 5s |
| `mike/bin/livermore_report_block_selfcheck.py` | offline | PASS | 27s |
| `mike/bin/livermore_selfcheck.py` | offline | PASS | 398s |
| `mike/bin/macro_indicator_freshness_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/manual_actions_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/bin/measured_by_warn_report_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/memcap_selfcheck.sh` | offline | PASS | 1s |
| `mike/bin/merge_park_orders_selfcheck.py` | offline | PASS | 93s |
| `mike/bin/mike_json_archive_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/mike_json_has_event_prefix_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/nav_corpaction_gate_e2e_selfcheck.py` | offline | PASS | 11s |
| `mike/bin/nav_cum_dividend_selfcheck.py` | offline | PASS | 15s |
| `mike/bin/nav_exdate_forecast_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/nav_flow_term_selfcheck.py` | offline | PASS | 14s |
| `mike/bin/nav_jump_flow_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/nav_ledger_vault_selfcheck.py` | offline | PASS | 7s |
| `mike/bin/nav_loss_brake_monitor_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/bin/nav_period_benchmark_selfcheck.py` | offline | PASS | 4s |
| `mike/bin/nav_scripts_2account_selfcheck.py` | offline | PASS | 45s |
| `mike/bin/nav_scripts_sandbox_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/nav_sleeve_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/nav_snapshot_daily_selfcheck.sh` | offline | PASS | 16s |
| `mike/bin/nav_sync_retry_rc_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/nav_unit_ledger_selfcheck.py` | offline | PASS | 10s |
| `mike/bin/notify_discord_selfcheck.py` | offline | PASS | 3s |
| `mike/bin/notify_thread_argswap_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/now_injection_selfcheck.sh` | offline | PASS | 1s |
| `mike/bin/oddlot_full_exit_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/opening_window_l2_poll_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/ops_health_check_autofix_dryrun_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/ops_health_check_lossbrake_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/ops_health_check_rejected_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/ops_health_check_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/orb_drift_monitor_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/orb_pt_appendonly_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/bin/order_book_shadow_probe_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/orphan_lot_blocked_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/paper_checkpoint_escalation_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/paper_corp_action_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/paper_report_render_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/park_chain_alert_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/park_holdings_manual_lot_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/bin/park_holdings_statement_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/park_holdings_transfer_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/park_rail_consistency_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/period_table_32_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/plan_funding_gate_fee_sync_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/plan_position_drift_check_selfcheck.py` | offline | PASS | 4s |
| `mike/bin/pnj_q3_review_watch_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/portfolio_status_selfcheck.py` | offline | PASS | 8s |
| `mike/bin/preempt_wakeup_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/prefetch_dnse_statement_selfcheck.sh` | offline | PASS | 1s |
| `mike/bin/preflight_order_invariants_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/production_manifest_selfcheck.sh` | offline | FAIL(rc=1) | 49s |
| `mike/bin/question_commit_hint_selfcheck.py` | offline | PASS | 10s |
| `mike/bin/rating_8l_forward_tracker_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/reconcile_equity_egg_selfcheck.py` | offline | PASS | 30s |
| `mike/bin/reconcile_equity_realized_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/report_delivery_gate_selfcheck.py` | offline | PASS | 7s |
| `mike/bin/report_delivery_ledger_selfcheck.py` | offline | PASS | 6s |
| `mike/bin/report_gate_quarterly_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/bin/report_return_gate_selfcheck.py` | offline | PASS | 4s |
| `mike/bin/report_v2_selfcheck.py` | offline | FAIL(rc=124) | 60s |
| `mike/bin/retro_escalate_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/retro_relay_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/rights_issue_alert_selfcheck.py` | offline | PASS | 6s |
| `mike/bin/rights_subscription_qty_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/rights_subscription_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/rights_terp_price_gate_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/rnd_preflight_power_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/runonce_label_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/savings_hurdle_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/sector_valuation_lens_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/selfcheck_baseline_diff_selfcheck.py` | offline | PASS | 6s |
| `mike/bin/selfcheck_macro_snapshot_asof.py` | offline | PASS | 57s |
| `mike/bin/selfcheck_red_owner_sweep.sh` | offline | PASS | 5s |
| `mike/bin/send_plan_report_aei_notes_selfcheck.py` | offline | PASS | 7s |
| `mike/bin/send_plan_report_ddzone_wire_selfcheck.py` | offline | PASS | 6s |
| `mike/bin/send_plan_report_nowcast_wire_selfcheck.py` | offline | PASS | 20s |
| `mike/bin/send_plan_report_park_jit_selfcheck.py` | offline | PASS | 26s |
| `mike/bin/send_plan_report_state_gate_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/signal_holds_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/snapshot_corp_action_selfcheck.py` | offline | PASS | 6s |
| `mike/bin/staleness_watch_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/stop_circuit_breaker_selfcheck.sh` | offline | PASS | 3s |
| `mike/bin/stop_wakeup_gate_selfcheck.py` | offline | PASS | 3s |
| `mike/bin/strategy_fit_dashboard_selfcheck.py` | offline | PASS | 3s |
| `mike/bin/strategy_fit_email_attach_selfcheck.py` | offline | PASS | 5s |
| `mike/bin/summary_parse_position_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/sunday_plan_round_selfcheck.sh` | offline | PASS | 685s |
| `mike/bin/surface_question_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/treasury_buyback_window_monitor_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/tz_anchor_gate_selfcheck.py` | offline | PASS | 7s |
| `mike/bin/universe_gap_fill_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/universe_pit_quality_selfcheck.py` | offline | PASS | 10s |
| `mike/bin/vendor_mismatch_alert_selfcheck.sh` | offline | PASS | 12s |
| `mike/bin/verify_account_snapshot_bq_price_date_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/verify_account_snapshot_broker_positions_marketprice_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/verify_account_snapshot_corp_action_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/verify_account_snapshot_lot_reset_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/verify_finding_bg_job_selfcheck.sh` | offline | PASS | 1s |
| `mike/bin/vnindex_total_return_selfcheck.py` | offline | PASS | 3s |
| `mike/bin/wags_arch_review_round2_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/wags_autofix_postq_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/wags_bus_question_pending_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/wags_bus_verdict_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/wags_dispatch_dead_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/wags_since_filter_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/wags_verdict_parse_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/wait_for_artifact_selfcheck.py` | offline | PASS | 8s |
| `mike/bin/wake_debounce_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/wake_thread_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/wakeup_audit_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/wakeup_profile_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/watcher_slow_threshold_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/work_ledger_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/work_tree_server_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/bin/worktree_stale_check_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/write_scope_conflict_selfcheck.py` | offline | PASS | 1s |
| `money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `navbasis_loud_selfcheck.py` | offline | PASS | 0s |
| `net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `netting_recon_selfcheck.py` | offline | PASS | 0s |
| `order_book_shadow_selfcheck.py` | offline | PASS | 0s |
| `oshares_dcf_selfcheck.py` | offline | PASS | 542s |
| `oshares_selfcheck_fixture.py` | offline | PASS | 0s |
| `oshares_wire_selfcheck.py` | offline | PASS | 23s |
| `pacing_horizon_note_selfcheck.py` | offline | PASS | 0s |
| `paper_main_window_selfcheck.py` | offline | PASS | 2s |
| `paper_probe_netting_selfcheck.py` | offline | PASS | 0s |
| `phs_flash_api_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `plan_funding_gate_selfcheck.py` | offline | PASS | 11s |
| `planpy_failopen_selfcheck.py` | offline | PASS | 0s |
| `probe_linger_selfcheck.py` | offline | PASS | 7s |
| `quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `rating8l_eff_guard_selfcheck.py` | offline | PASS | 1s |
| `rating8l_icb_pit_selfcheck.py` | offline | PASS | 1s |
| `rating_8l_history_bank_aq_selfcheck.py` | offline | PASS | 53s |
| `rating_pit_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `refresh_deposit_cctg_weekly_selfcheck.py` | offline | PASS | 1s |
| `refresh_earnings_surprise_pkl_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `refresh_skip_participation_selfcheck.py` | offline | PASS | 6s |
| `restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `route_selector_selfcheck.py` | offline | PASS | 4s |
| `rubber_weekly_selfcheck.py` | offline | PASS | 2s |
| `rule_a_ceiling_selfcheck.py` | offline | PASS | 0s |
| `rule_a_ref_guard_selfcheck.py` | offline | PASS | 1s |
| `sbv_policy_verify_selfcheck.py` | offline | PASS | 17s |
| `screen_sort_direction_selfcheck.py` | offline | PASS | 2s |
| `sell_adv_cap_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `sell_loan_package_selfcheck.py` | offline | PASS | 0s |
| `sell_split_by_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `sync_cache_lock_selfcheck.py` | offline | PASS | 5s |
| `t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `te_macro_crosscheck_selfcheck.py` | offline | PASS | 1s |
| `te_weekly_bash_selfcheck.py` | offline | PASS | 0s |
| `tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `tz_asof_ict_dd_dcf_selfcheck.py` | offline | PASS | 3s |
| `universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
