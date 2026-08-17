---
kind: reference
title: Selfcheck registry — snapshot tự sinh, ĐỪNG sửa tay
generated_by: bin/run_selfchecks.sh
generated_at: 2026-08-14T21:24:42Z
---

# Selfcheck registry (auto-generated, ĐỪNG sửa tay — sửa `bin/run_selfchecks.sh`)

Chạy: `bash mike/bin/run_selfchecks.sh [--live]`. Lần gần nhất: 371 PASS / 133 FAIL / 52 SKIP (live).

| File | Tier | Status | Thời gian |
|---|---|---|---|
| `anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 3s |
| `anomaly_gate_selfcheck.py` | offline | PASS | 7s |
| `approval_gate_selfcheck.py` | offline | PASS | 0s |
| `basket_price_basis_audit_selfcheck.py` | offline | PASS | 9s |
| `basket_price_basis_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `book_tagging_selfcheck.py` | offline | PASS | 1s |
| `capit_lever_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `capit_participation_cap_selfcheck.py` | offline | PASS | 1s |
| `cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `churn_guard_selfcheck.py` | offline | PASS | 1s |
| `concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `custom30_publish_weight_selfcheck.py` | offline | PASS | 0s |
| `dc_book_waterfall_selfcheck.py` | offline | PASS | 1s |
| `dcf_check_selfcheck.py` | offline | PASS | 0s |
| `dcf_refresh_gate_selfcheck.py` | offline | PASS | 1s |
| `dcf_selector_selfcheck.py` | offline | PASS | 1s |
| `discretionary_accumulation_selfcheck.py` | offline | PASS | 0s |
| `discretionary_participation_cap_selfcheck.py` | offline | PASS | 2s |
| `discretionary_target_pct_selfcheck.py` | offline | PASS | 0s |
| `dt5g_chain_freshness_selfcheck.py` | offline | PASS | 0s |
| `due_diligence_selfcheck.py` | offline | PASS | 9s |
| `dynamic_no_chase_ceiling_selfcheck.py` | offline | PASS | 1s |
| `edge_wlag_gate_selfcheck.py` | offline | PASS | 0s |
| `excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `expected_volume_pacing_selfcheck.py` | offline | PASS | 7s |
| `expvol_shadow_probe_selfcheck.py` | offline | PASS | 0s |
| `extreme_regime_selfcheck.py` | offline | PASS | 1s |
| `eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `freshness_ops_selfcheck.py` | offline | PASS | 2s |
| `ghost_order_selfcheck.py` | offline | PASS | 1s |
| `hard_no_chase_ceiling_selfcheck.py` | offline | PASS | 3s |
| `hybrid_fill_timing_selfcheck.py` | offline | PASS | 2s |
| `immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `lag_adv_cap_selfcheck.py` | offline | PASS | 0s |
| `lag_forensic_filter_selfcheck.py` | offline | PASS | 1s |
| `lag_governance_order_gate_selfcheck.py` | offline | PASS | 0s |
| `lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `lag_live_schedule_selfcheck.py` | offline | PASS | 23s |
| `lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `loan_package_resolution_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/DollarBill/tools/compute_park_add_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Mafee/reconcile_parents_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/anomaly_escalate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/capit_dd_gate_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/chase_cap_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/insider_flags_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/pending_adv3t_hard_gate_20260810/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/pending_live_flip_chase_cap_20260804/new/chase_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/pending_live_flip_chase_cap_20260804/new/dc_book_waterfall_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/pending_park_trim_partial_reconcile_20260810/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/pending_park_trim_partial_reconcile_20260810/compute_jit_unpark_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/Taylor/seccap_dyn_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/universe_freshness_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Winston/freshness_warn_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1521113190405247057/agents/DollarBill/tools/compute_park_add_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1521113190405247057/agents/Mafee/reconcile_parents_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1521113190405247057/agents/Taylor/anomaly_escalate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1521113190405247057/agents/Taylor/capit_dd_gate_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/wt-1521113190405247057/agents/Taylor/chase_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1521113190405247057/agents/Taylor/insider_flags_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1521113190405247057/agents/Taylor/pending_adv3t_hard_gate_20260810/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/wt-1521113190405247057/agents/Taylor/pending_live_flip_chase_cap_20260804/new/chase_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1521113190405247057/agents/Taylor/pending_live_flip_chase_cap_20260804/new/dc_book_waterfall_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1521113190405247057/agents/Taylor/pending_park_trim_partial_reconcile_20260810/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1521113190405247057/agents/Taylor/pending_park_trim_partial_reconcile_20260810/compute_jit_unpark_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1521113190405247057/agents/Taylor/seccap_dyn_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/wt-1521113190405247057/agents/Taylor/universe_freshness_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1521113190405247057/agents/Winston/freshness_warn_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1521113190405247057/bin/approve_plan_with_jit_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1521113190405247057/bin/broker_fill_confirm_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1521113190405247057/bin/build_universe_pit_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1521113190405247057/bin/check_report_cadence_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1521113190405247057/bin/cli_provider_selfcheck.sh` | offline | PASS | 56s |
| `mike/agents/wt-1521113190405247057/bin/commit_collision_gate_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `mike/agents/wt-1521113190405247057/bin/compute_active_nav_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1521113190405247057/bin/compute_jit_unpark_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1521113190405247057/bin/compute_park_trim_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1521113190405247057/bin/consolidate_git_scope_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1521113190405247057/bin/corp_action_daily_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1521113190405247057/bin/corp_action_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1521113190405247057/bin/cursor_advance_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/wt-1521113190405247057/bin/dispatch_discord_topic_selfcheck.sh` | offline | PASS | 45s |
| `mike/agents/wt-1521113190405247057/bin/dispatch_question_hint_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1521113190405247057/bin/dt5g_publisher_gate_selfcheck.sh` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1521113190405247057/bin/dt5g_writer_watch_selfcheck.sh` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1521113190405247057/bin/exrights_price_basis_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1521113190405247057/bin/filter_lag_entry_window_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1521113190405247057/bin/job_cancel_guard_selfcheck.py` | offline | FAIL(rc=1) | 46s |
| `mike/agents/wt-1521113190405247057/bin/kb_nightly_backup_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1521113190405247057/bin/merge_park_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1521113190405247057/bin/mike_json_archive_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1521113190405247057/bin/mike_json_has_event_prefix_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1521113190405247057/bin/nav_cum_dividend_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1521113190405247057/bin/nav_scripts_2account_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1521113190405247057/bin/notify_thread_argswap_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1521113190405247057/bin/ops_health_check_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1521113190405247057/bin/paper_checkpoint_escalation_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1521113190405247057/bin/paper_report_render_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1521113190405247057/bin/preflight_order_invariants_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1521113190405247057/bin/run_selfchecks.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/wt-1521113190405247057/bin/sector_valuation_lens_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1521113190405247057/bin/selfcheck_baseline_diff.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1521113190405247057/bin/selfcheck_baseline_diff_selfcheck.py` | offline | FAIL(rc=1) | 3s |
| `mike/agents/wt-1521113190405247057/bin/selfcheck_scope_map.sh` | offline | PASS | 0s |
| `mike/agents/wt-1521113190405247057/bin/selfcheck_weekly_baseline_check.sh` | offline | FAIL(rc=124) | 60s |
| `mike/agents/wt-1521113190405247057/bin/send_plan_report_park_jit_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/wt-1521113190405247057/bin/send_plan_report_state_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1521113190405247057/bin/universe_pit_quality_selfcheck.py` | offline | PASS | 9s |
| `mike/agents/wt-1521113190405247057/bin/verify_account_snapshot_corp_action_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1521113190405247057/bin/verify_account_snapshot_lot_reset_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1521113190405247057/bin/wags_autofix_postq_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1521113190405247057/bin/wags_bus_verdict_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1521113190405247057/bin/wags_verdict_parse_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1521113190405247057/bin/wakeup_profile_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1521113190405247057/bin/watcher_slow_threshold_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1521113190405247057/bin/write_scope_conflict_selfcheck.py` | offline | PASS | 0s |
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
| `mike/agents/wt-1522519012066721923/bin/consolidate_git_scope_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522519012066721923/bin/corp_action_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522519012066721923/bin/cursor_advance_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/wt-1522519012066721923/bin/dispatch_discord_topic_selfcheck.sh` | offline | PASS | 44s |
| `mike/agents/wt-1522519012066721923/bin/dt5g_publisher_gate_selfcheck.sh` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522519012066721923/bin/dt5g_writer_watch_selfcheck.sh` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522519012066721923/bin/filter_lag_entry_window_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522519012066721923/bin/mike_json_archive_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522519012066721923/bin/nav_cum_dividend_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522519012066721923/bin/nav_scripts_2account_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522519012066721923/bin/ops_health_check_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522519012066721923/bin/paper_checkpoint_escalation_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1522519012066721923/bin/paper_report_render_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522519012066721923/bin/plan_canonical_identity_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/wt-1522519012066721923/bin/preflight_order_invariants_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522519012066721923/bin/run_selfchecks.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/wt-1522519012066721923/bin/sector_valuation_lens_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522519012066721923/bin/selfcheck_scope_map.sh` | offline | PASS | 0s |
| `mike/agents/wt-1522519012066721923/bin/selfcheck_weekly_baseline_artifact_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522519012066721923/bin/selfcheck_weekly_baseline_check.sh` | offline | FAIL(rc=124) | 60s |
| `mike/agents/wt-1522519012066721923/bin/send_plan_report_park_jit_selfcheck.py` | offline | FAIL(rc=1) | 5s |
| `mike/agents/wt-1522519012066721923/bin/time_standard_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522519012066721923/bin/universe_pit_quality_selfcheck.py` | offline | FAIL(rc=1) | 9s |
| `mike/agents/wt-1522519012066721923/bin/verify_account_snapshot_corp_action_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522519012066721923/bin/wakeup_profile_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/wt-1522576692638388364/agents/DollarBill/tools/compute_park_add_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522576692638388364/agents/Mafee/reconcile_parents_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522576692638388364/agents/Taylor/anomaly_escalate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522576692638388364/agents/Taylor/capit_dd_gate_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/wt-1522576692638388364/agents/Taylor/chase_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522576692638388364/agents/Taylor/insider_flags_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1522576692638388364/agents/Taylor/pending_adv3t_hard_gate_20260810/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/wt-1522576692638388364/agents/Taylor/pending_live_flip_chase_cap_20260804/new/chase_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522576692638388364/agents/Taylor/pending_live_flip_chase_cap_20260804/new/dc_book_waterfall_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522576692638388364/agents/Taylor/pending_park_trim_partial_reconcile_20260810/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522576692638388364/agents/Taylor/pending_park_trim_partial_reconcile_20260810/compute_jit_unpark_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522576692638388364/agents/Taylor/seccap_dyn_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/wt-1522576692638388364/agents/Taylor/universe_freshness_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522576692638388364/agents/Winston/freshness_warn_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522576692638388364/bin/approve_plan_with_jit_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1522576692638388364/bin/broker_fill_confirm_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1522576692638388364/bin/build_universe_pit_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522576692638388364/bin/check_report_cadence_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1522576692638388364/bin/cli_provider_selfcheck.sh` | offline | PASS | 55s |
| `mike/agents/wt-1522576692638388364/bin/commit_collision_gate_selfcheck.py` | offline | FAIL(rc=1) | 3s |
| `mike/agents/wt-1522576692638388364/bin/compute_active_nav_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522576692638388364/bin/compute_jit_unpark_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522576692638388364/bin/compute_park_trim_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522576692638388364/bin/consolidate_git_scope_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1522576692638388364/bin/corp_action_daily_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522576692638388364/bin/corp_action_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522576692638388364/bin/cursor_advance_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/wt-1522576692638388364/bin/dispatch_discord_topic_selfcheck.sh` | offline | PASS | 45s |
| `mike/agents/wt-1522576692638388364/bin/dispatch_question_hint_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522576692638388364/bin/dt5g_publisher_gate_selfcheck.sh` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522576692638388364/bin/dt5g_writer_watch_selfcheck.sh` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522576692638388364/bin/exrights_price_basis_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1522576692638388364/bin/filter_lag_entry_window_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522576692638388364/bin/job_cancel_guard_selfcheck.py` | offline | FAIL(rc=1) | 46s |
| `mike/agents/wt-1522576692638388364/bin/kb_nightly_backup_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522576692638388364/bin/merge_park_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522576692638388364/bin/mike_json_archive_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1522576692638388364/bin/mike_json_has_event_prefix_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522576692638388364/bin/nav_cum_dividend_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522576692638388364/bin/nav_scripts_2account_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522576692638388364/bin/notify_thread_argswap_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1522576692638388364/bin/ops_health_check_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522576692638388364/bin/paper_checkpoint_escalation_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522576692638388364/bin/paper_report_render_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522576692638388364/bin/preflight_order_invariants_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1522576692638388364/bin/run_selfchecks.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/wt-1522576692638388364/bin/sector_valuation_lens_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522576692638388364/bin/selfcheck_baseline_diff.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522576692638388364/bin/selfcheck_baseline_diff_selfcheck.py` | offline | FAIL(rc=1) | 3s |
| `mike/agents/wt-1522576692638388364/bin/selfcheck_scope_map.sh` | offline | PASS | 0s |
| `mike/agents/wt-1522576692638388364/bin/selfcheck_weekly_baseline_check.sh` | offline | FAIL(rc=124) | 60s |
| `mike/agents/wt-1522576692638388364/bin/send_plan_report_park_jit_selfcheck.py` | offline | PASS | 5s |
| `mike/agents/wt-1522576692638388364/bin/send_plan_report_state_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1522576692638388364/bin/universe_pit_quality_selfcheck.py` | offline | PASS | 8s |
| `mike/agents/wt-1522576692638388364/bin/verify_account_snapshot_corp_action_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522576692638388364/bin/verify_account_snapshot_lot_reset_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522576692638388364/bin/wags_autofix_postq_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522576692638388364/bin/wags_bus_verdict_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1522576692638388364/bin/wags_verdict_parse_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522576692638388364/bin/wakeup_profile_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1522576692638388364/bin/watcher_slow_threshold_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1522576692638388364/bin/write_scope_conflict_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1536246356098814022-cleanup/agents/Mafee/reconcile_parents_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1536246356098814022-cleanup/agents/Taylor/anomaly_escalate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1536246356098814022-cleanup/agents/Taylor/capit_dd_gate_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/wt-1536246356098814022-cleanup/agents/Taylor/chase_cap_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1536246356098814022-cleanup/agents/Taylor/insider_flags_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1536246356098814022-cleanup/agents/Taylor/pending_adv3t_hard_gate_20260810/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/wt-1536246356098814022-cleanup/agents/Taylor/pending_live_flip_chase_cap_20260804/new/chase_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1536246356098814022-cleanup/agents/Taylor/pending_live_flip_chase_cap_20260804/new/dc_book_waterfall_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1536246356098814022-cleanup/agents/Taylor/pending_park_trim_partial_reconcile_20260810/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1536246356098814022-cleanup/agents/Taylor/pending_park_trim_partial_reconcile_20260810/compute_jit_unpark_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1536246356098814022-cleanup/agents/Taylor/seccap_dyn_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/wt-1536246356098814022-cleanup/agents/Winston/freshness_warn_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/approve_plan_with_jit_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/build_universe_pit_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/cli_provider_selfcheck.sh` | offline | PASS | 55s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/compute_active_nav_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/compute_jit_unpark_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/compute_park_trim_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/consolidate_git_scope_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/corp_action_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/cursor_advance_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/dispatch_discord_topic_selfcheck.sh` | offline | PASS | 44s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/dt5g_publisher_gate_selfcheck.sh` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/dt5g_writer_watch_selfcheck.sh` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/exrights_price_basis_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/filter_lag_entry_window_selfcheck.py` | offline | FAIL(rc=1) | 1s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/job_cancel_guard_selfcheck.py` | offline | FAIL(rc=1) | 46s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/merge_park_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/mike_json_archive_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/nav_cum_dividend_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/nav_scripts_2account_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/ops_health_check_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/paper_checkpoint_escalation_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/paper_report_render_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/preflight_order_invariants_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/run_selfchecks.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/wt-1536246356098814022-cleanup/bin/sector_valuation_lens_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/selfcheck_scope_map.sh` | offline | PASS | 0s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/selfcheck_weekly_baseline_check.sh` | offline | FAIL(rc=124) | 716s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/send_plan_report_park_jit_selfcheck.py` | offline | FAIL(rc=1) | 5s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/send_plan_report_state_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/universe_pit_quality_selfcheck.py` | offline | FAIL(rc=1) | 5s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/verify_account_snapshot_corp_action_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/verify_account_snapshot_lot_reset_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/wakeup_profile_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1536246356098814022-cleanup/bin/write_scope_conflict_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/agents/Mafee/reconcile_parents_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/agents/Taylor/anomaly_escalate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/agents/Taylor/capit_dd_gate_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/wt-1536246356098814022-dispatchtrap/agents/Taylor/chase_cap_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/agents/Taylor/insider_flags_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/agents/Taylor/pending_adv3t_hard_gate_20260810/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/wt-1536246356098814022-dispatchtrap/agents/Taylor/pending_live_flip_chase_cap_20260804/new/chase_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/agents/Taylor/pending_live_flip_chase_cap_20260804/new/dc_book_waterfall_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/agents/Taylor/pending_park_trim_partial_reconcile_20260810/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/agents/Taylor/pending_park_trim_partial_reconcile_20260810/compute_jit_unpark_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/agents/Taylor/seccap_dyn_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/wt-1536246356098814022-dispatchtrap/agents/Winston/freshness_warn_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/approve_plan_with_jit_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/build_universe_pit_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/cli_provider_selfcheck.sh` | offline | PASS | 55s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/compute_active_nav_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/compute_jit_unpark_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/compute_park_trim_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/consolidate_git_scope_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/corp_action_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/cursor_advance_selfcheck.py` | offline | PASS | 2s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/dispatch_discord_topic_selfcheck.sh` | offline | PASS | 44s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/dt5g_publisher_gate_selfcheck.sh` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/dt5g_writer_watch_selfcheck.sh` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/exrights_price_basis_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/filter_lag_entry_window_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/job_cancel_guard_selfcheck.py` | offline | FAIL(rc=1) | 43s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/merge_park_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/mike_json_archive_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/nav_cum_dividend_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/nav_scripts_2account_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/ops_health_check_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/paper_checkpoint_escalation_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/paper_report_render_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/preflight_order_invariants_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/run_selfchecks.sh` | live | SKIP(--live để chạy) | - |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/sector_valuation_lens_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/selfcheck_scope_map.sh` | offline | PASS | 0s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/selfcheck_weekly_baseline_check.sh` | offline | FAIL(rc=124) | 60s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/send_plan_report_park_jit_selfcheck.py` | offline | FAIL(rc=1) | 5s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/send_plan_report_state_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/universe_pit_quality_selfcheck.py` | offline | FAIL(rc=1) | 5s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/verify_account_snapshot_corp_action_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/verify_account_snapshot_lot_reset_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/agents/wt-1536246356098814022-dispatchtrap/bin/wakeup_profile_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `mike/bin/approve_plan_with_jit_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/broker_fill_confirm_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/build_universe_pit_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/check_report_cadence_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/cli_provider_selfcheck.sh` | offline | PASS | 56s |
| `mike/bin/commit_collision_gate_selfcheck.py` | offline | PASS | 3s |
| `mike/bin/compute_active_nav_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/compute_jit_unpark_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/compute_park_trim_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/consolidate_git_scope_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/corp_action_daily_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/corp_action_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/cursor_advance_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/dispatch_discord_topic_selfcheck.sh` | offline | PASS | 45s |
| `mike/bin/dispatch_question_hint_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/dt5g_publisher_gate_selfcheck.sh` | offline | PASS | 1s |
| `mike/bin/dt5g_writer_watch_selfcheck.sh` | offline | PASS | 15s |
| `mike/bin/exrights_price_basis_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/filter_lag_entry_window_selfcheck.py` | offline | PASS | 10s |
| `mike/bin/job_cancel_guard_selfcheck.py` | offline | FAIL(rc=1) | 47s |
| `mike/bin/kb_nightly_backup_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/merge_park_orders_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/mike_json_archive_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/mike_json_has_event_prefix_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/nav_cum_dividend_selfcheck.py` | offline | PASS | 15s |
| `mike/bin/nav_scripts_2account_selfcheck.py` | offline | PASS | 35s |
| `mike/bin/notify_thread_argswap_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/ops_health_check_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/paper_checkpoint_escalation_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/paper_report_render_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/preflight_order_invariants_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/run_selfchecks.sh` | live | SKIP(--live để chạy) | - |
| `mike/bin/sector_valuation_lens_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/selfcheck_baseline_diff.py` | offline | FAIL(rc=1) | 0s |
| `mike/bin/selfcheck_baseline_diff_selfcheck.py` | offline | PASS | 6s |
| `mike/bin/selfcheck_scope_map.sh` | offline | PASS | 0s |
| `mike/bin/selfcheck_weekly_baseline_check.sh` | offline | FAIL(rc=124) | 60s |
| `mike/bin/send_plan_report_park_jit_selfcheck.py` | offline | PASS | 5s |
| `mike/bin/send_plan_report_state_gate_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/universe_pit_quality_selfcheck.py` | offline | PASS | 8s |
| `mike/bin/verify_account_snapshot_corp_action_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/verify_account_snapshot_lot_reset_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/wags_autofix_postq_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/wags_bus_verdict_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/wags_verdict_parse_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/wakeup_profile_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/watcher_slow_threshold_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/write_scope_conflict_selfcheck.py` | offline | PASS | 1s |
| `money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `netting_recon_selfcheck.py` | offline | PASS | 0s |
| `oshares_wire_selfcheck.py` | offline | PASS | 20s |
| `paper_main_window_selfcheck.py` | offline | PASS | 1s |
| `paper_probe_netting_selfcheck.py` | offline | PASS | 0s |
| `plan_cash_commitment_selfcheck.py` | offline | PASS | 0s |
| `plan_check_field_schema_selfcheck.py` | offline | PASS | 0s |
| `plan_funding_gate_selfcheck.py` | offline | PASS | 0s |
| `quote_l2_logging_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `refresh_skip_participation_selfcheck.py` | offline | PASS | 2s |
| `restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `route_selector_selfcheck.py` | offline | PASS | 4s |
| `rubber_weekly_selfcheck.py` | offline | PASS | 2s |
| `sync_cache_lock_selfcheck.py` | offline | PASS | 5s |
| `t2_settlement_selfcheck.py` | offline | PASS | 1s |
| `tbot/code/tests/selfcheck.py` | offline | FAIL(rc=1) | 0s |
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
| `wt-1520374161971875940/bin/dt5g_publisher_gate_selfcheck.sh` | offline | PASS | 0s |
| `wt-1520374161971875940/bin/dt5g_writer_watch_selfcheck.sh` | offline | PASS | 15s |
| `wt-1520374161971875940/bin/filter_lag_entry_window_selfcheck.py` | offline | PASS | 0s |
| `wt-1520374161971875940/bin/mike_json_archive_selfcheck.py` | offline | PASS | 1s |
| `wt-1520374161971875940/bin/nav_cum_dividend_selfcheck.py` | offline | PASS | 14s |
| `wt-1520374161971875940/bin/nav_scripts_2account_selfcheck.py` | offline | PASS | 22s |
| `wt-1520374161971875940/bin/ops_health_check_selfcheck.py` | offline | PASS | 0s |
| `wt-1520374161971875940/bin/paper_checkpoint_escalation_selfcheck.py` | offline | PASS | 1s |
| `wt-1520374161971875940/bin/paper_report_render_selfcheck.py` | offline | PASS | 0s |
| `wt-1520374161971875940/bin/preflight_order_invariants_selfcheck.py` | offline | PASS | 0s |
| `wt-1520374161971875940/bin/run_selfchecks.sh` | live | SKIP(--live để chạy) | - |
| `wt-1520374161971875940/bin/sector_valuation_lens_selfcheck.py` | offline | PASS | 0s |
| `wt-1520374161971875940/bin/selfcheck_scope_map.sh` | offline | PASS | 0s |
| `wt-1520374161971875940/bin/selfcheck_weekly_baseline_check.sh` | offline | FAIL(rc=124) | 60s |
| `wt-1520374161971875940/bin/send_plan_report_park_jit_selfcheck.py` | offline | FAIL(rc=1) | 5s |
| `wt-1520374161971875940/bin/universe_pit_quality_selfcheck.py` | offline | FAIL(rc=1) | 6s |
| `wt-1520374161971875940/bin/verify_account_snapshot_corp_action_selfcheck.py` | offline | PASS | 2s |
| `wt-1520374161971875940/bin/wakeup_profile_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `wt-1521475726329516122/agents/DollarBill/tools/compute_park_add_selfcheck.py` | offline | PASS | 0s |
| `wt-1521475726329516122/agents/Mafee/reconcile_parents_selfcheck.py` | offline | PASS | 0s |
| `wt-1521475726329516122/agents/Taylor/anomaly_escalate_selfcheck.py` | offline | PASS | 1s |
| `wt-1521475726329516122/agents/Taylor/capit_dd_gate_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `wt-1521475726329516122/agents/Taylor/chase_cap_selfcheck.py` | offline | PASS | 0s |
| `wt-1521475726329516122/agents/Taylor/insider_flags_selfcheck.py` | offline | PASS | 0s |
| `wt-1521475726329516122/agents/Taylor/pending_adv3t_hard_gate_20260810/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `wt-1521475726329516122/agents/Taylor/pending_live_flip_chase_cap_20260804/new/chase_cap_selfcheck.py` | offline | PASS | 0s |
| `wt-1521475726329516122/agents/Taylor/pending_live_flip_chase_cap_20260804/new/dc_book_waterfall_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `wt-1521475726329516122/agents/Taylor/pending_park_trim_partial_reconcile_20260810/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `wt-1521475726329516122/agents/Taylor/pending_park_trim_partial_reconcile_20260810/compute_jit_unpark_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `wt-1521475726329516122/agents/Taylor/seccap_dyn_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `wt-1521475726329516122/agents/Taylor/universe_freshness_selfcheck.py` | offline | PASS | 0s |
| `wt-1521475726329516122/agents/Winston/freshness_warn_selfcheck.py` | offline | PASS | 1s |
| `wt-1521475726329516122/bin/approve_plan_with_jit_selfcheck.py` | offline | PASS | 1s |
| `wt-1521475726329516122/bin/broker_fill_confirm_selfcheck.py` | offline | PASS | 0s |
| `wt-1521475726329516122/bin/build_universe_pit_selfcheck.py` | offline | PASS | 1s |
| `wt-1521475726329516122/bin/check_report_cadence_selfcheck.py` | offline | PASS | 0s |
| `wt-1521475726329516122/bin/cli_provider_selfcheck.sh` | offline | PASS | 56s |
| `wt-1521475726329516122/bin/commit_collision_gate_selfcheck.py` | offline | FAIL(rc=1) | 3s |
| `wt-1521475726329516122/bin/compute_active_nav_selfcheck.py` | offline | PASS | 0s |
| `wt-1521475726329516122/bin/compute_jit_unpark_selfcheck.py` | offline | PASS | 2s |
| `wt-1521475726329516122/bin/compute_park_trim_selfcheck.py` | offline | PASS | 0s |
| `wt-1521475726329516122/bin/consolidate_git_scope_selfcheck.py` | offline | PASS | 1s |
| `wt-1521475726329516122/bin/corp_action_daily_selfcheck.py` | offline | PASS | 0s |
| `wt-1521475726329516122/bin/corp_action_selfcheck.py` | offline | PASS | 0s |
| `wt-1521475726329516122/bin/cursor_advance_selfcheck.py` | offline | PASS | 2s |
| `wt-1521475726329516122/bin/dispatch_discord_topic_selfcheck.sh` | offline | PASS | 45s |
| `wt-1521475726329516122/bin/dispatch_question_hint_selfcheck.py` | offline | PASS | 0s |
| `wt-1521475726329516122/bin/dt5g_publisher_gate_selfcheck.sh` | offline | PASS | 1s |
| `wt-1521475726329516122/bin/dt5g_writer_watch_selfcheck.sh` | offline | PASS | 15s |
| `wt-1521475726329516122/bin/exrights_price_basis_selfcheck.py` | offline | PASS | 0s |
| `wt-1521475726329516122/bin/filter_lag_entry_window_selfcheck.py` | offline | PASS | 10s |
| `wt-1521475726329516122/bin/job_cancel_guard_selfcheck.py` | offline | FAIL(rc=1) | 46s |
| `wt-1521475726329516122/bin/kb_nightly_backup_selfcheck.py` | offline | PASS | 0s |
| `wt-1521475726329516122/bin/merge_park_orders_selfcheck.py` | offline | PASS | 0s |
| `wt-1521475726329516122/bin/mike_json_archive_selfcheck.py` | offline | PASS | 1s |
| `wt-1521475726329516122/bin/mike_json_has_event_prefix_selfcheck.py` | offline | PASS | 0s |
| `wt-1521475726329516122/bin/nav_cum_dividend_selfcheck.py` | offline | PASS | 15s |
| `wt-1521475726329516122/bin/nav_scripts_2account_selfcheck.py` | offline | PASS | 33s |
| `wt-1521475726329516122/bin/notify_thread_argswap_selfcheck.py` | offline | PASS | 1s |
| `wt-1521475726329516122/bin/ops_health_check_selfcheck.py` | offline | PASS | 0s |
| `wt-1521475726329516122/bin/paper_checkpoint_escalation_selfcheck.py` | offline | PASS | 0s |
| `wt-1521475726329516122/bin/paper_report_render_selfcheck.py` | offline | PASS | 1s |
| `wt-1521475726329516122/bin/preflight_order_invariants_selfcheck.py` | offline | PASS | 0s |
| `wt-1521475726329516122/bin/run_selfchecks.sh` | live | SKIP(--live để chạy) | - |
| `wt-1521475726329516122/bin/sector_valuation_lens_selfcheck.py` | offline | PASS | 0s |
| `wt-1521475726329516122/bin/selfcheck_baseline_diff.py` | offline | FAIL(rc=1) | 0s |
| `wt-1521475726329516122/bin/selfcheck_baseline_diff_selfcheck.py` | offline | FAIL(rc=1) | 3s |
| `wt-1521475726329516122/bin/selfcheck_scope_map.sh` | offline | PASS | 0s |
| `wt-1521475726329516122/bin/selfcheck_weekly_baseline_check.sh` | offline | FAIL(rc=124) | 60s |
| `wt-1521475726329516122/bin/send_plan_report_park_jit_selfcheck.py` | offline | PASS | 5s |
| `wt-1521475726329516122/bin/send_plan_report_state_gate_selfcheck.py` | offline | PASS | 1s |
| `wt-1521475726329516122/bin/universe_pit_quality_selfcheck.py` | offline | PASS | 8s |
| `wt-1521475726329516122/bin/verify_account_snapshot_corp_action_selfcheck.py` | offline | PASS | 2s |
| `wt-1521475726329516122/bin/verify_account_snapshot_lot_reset_selfcheck.py` | offline | PASS | 2s |
| `wt-1521475726329516122/bin/wags_autofix_postq_selfcheck.py` | offline | PASS | 0s |
| `wt-1521475726329516122/bin/wags_bus_verdict_selfcheck.py` | offline | PASS | 0s |
| `wt-1521475726329516122/bin/wags_verdict_parse_selfcheck.py` | offline | PASS | 1s |
| `wt-1521475726329516122/bin/wakeup_profile_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `wt-1521475726329516122/bin/watcher_slow_threshold_selfcheck.py` | offline | PASS | 0s |
| `wt-1521475726329516122/bin/write_scope_conflict_selfcheck.py` | offline | PASS | 1s |
| `wt-1521735922066919515/agents/Mafee/reconcile_parents_selfcheck.py` | offline | PASS | 0s |
| `wt-1521735922066919515/agents/Taylor/anomaly_escalate_selfcheck.py` | offline | PASS | 1s |
| `wt-1521735922066919515/agents/Taylor/capit_dd_gate_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `wt-1521735922066919515/agents/Taylor/chase_cap_selfcheck.py` | offline | PASS | 0s |
| `wt-1521735922066919515/agents/Taylor/insider_flags_selfcheck.py` | offline | PASS | 0s |
| `wt-1521735922066919515/agents/Taylor/pending_adv3t_hard_gate_20260810/lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `wt-1521735922066919515/agents/Taylor/pending_live_flip_chase_cap_20260804/new/chase_cap_selfcheck.py` | offline | PASS | 0s |
| `wt-1521735922066919515/agents/Taylor/pending_live_flip_chase_cap_20260804/new/dc_book_waterfall_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `wt-1521735922066919515/agents/Taylor/pending_park_trim_partial_reconcile_20260810/book_tagging_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `wt-1521735922066919515/agents/Taylor/pending_park_trim_partial_reconcile_20260810/compute_jit_unpark_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `wt-1521735922066919515/agents/Taylor/seccap_dyn_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `wt-1521735922066919515/agents/Winston/freshness_warn_selfcheck.py` | offline | PASS | 1s |
| `wt-1521735922066919515/bin/approve_plan_with_jit_selfcheck.py` | offline | PASS | 1s |
| `wt-1521735922066919515/bin/build_universe_pit_selfcheck.py` | offline | PASS | 0s |
| `wt-1521735922066919515/bin/cli_provider_selfcheck.sh` | offline | PASS | 55s |
| `wt-1521735922066919515/bin/compute_active_nav_selfcheck.py` | offline | PASS | 0s |
| `wt-1521735922066919515/bin/compute_jit_unpark_selfcheck.py` | offline | PASS | 2s |
| `wt-1521735922066919515/bin/compute_park_trim_selfcheck.py` | offline | PASS | 1s |
| `wt-1521735922066919515/bin/consolidate_git_scope_selfcheck.py` | offline | PASS | 1s |
| `wt-1521735922066919515/bin/corp_action_selfcheck.py` | offline | PASS | 0s |
| `wt-1521735922066919515/bin/cursor_advance_selfcheck.py` | offline | PASS | 2s |
| `wt-1521735922066919515/bin/dispatch_discord_topic_selfcheck.sh` | offline | PASS | 44s |
| `wt-1521735922066919515/bin/dt5g_publisher_gate_selfcheck.sh` | offline | PASS | 0s |
| `wt-1521735922066919515/bin/dt5g_writer_watch_selfcheck.sh` | offline | PASS | 15s |
| `wt-1521735922066919515/bin/exrights_price_basis_selfcheck.py` | offline | FAIL(rc=1) | 0s |
| `wt-1521735922066919515/bin/filter_lag_entry_window_selfcheck.py` | offline | PASS | 10s |
| `wt-1521735922066919515/bin/job_cancel_guard_selfcheck.py` | offline | FAIL(rc=1) | 46s |
| `wt-1521735922066919515/bin/merge_park_orders_selfcheck.py` | offline | PASS | 0s |
| `wt-1521735922066919515/bin/mike_json_archive_selfcheck.py` | offline | PASS | 1s |
| `wt-1521735922066919515/bin/nav_cum_dividend_selfcheck.py` | offline | PASS | 14s |
| `wt-1521735922066919515/bin/nav_scripts_2account_selfcheck.py` | offline | PASS | 33s |
| `wt-1521735922066919515/bin/ops_health_check_selfcheck.py` | offline | PASS | 1s |
| `wt-1521735922066919515/bin/paper_checkpoint_escalation_selfcheck.py` | offline | PASS | 0s |
| `wt-1521735922066919515/bin/paper_report_render_selfcheck.py` | offline | PASS | 0s |
| `wt-1521735922066919515/bin/preflight_order_invariants_selfcheck.py` | offline | PASS | 1s |
| `wt-1521735922066919515/bin/run_selfchecks.sh` | live | SKIP(--live để chạy) | - |
| `wt-1521735922066919515/bin/sector_valuation_lens_selfcheck.py` | offline | PASS | 0s |
| `wt-1521735922066919515/bin/selfcheck_scope_map.sh` | offline | PASS | 0s |
| `wt-1521735922066919515/bin/selfcheck_weekly_baseline_check.sh` | offline | FAIL(rc=124) | 60s |
| `wt-1521735922066919515/bin/send_plan_report_park_jit_selfcheck.py` | offline | FAIL(rc=1) | 5s |
| `wt-1521735922066919515/bin/send_plan_report_state_gate_selfcheck.py` | offline | PASS | 0s |
| `wt-1521735922066919515/bin/universe_pit_quality_selfcheck.py` | offline | FAIL(rc=1) | 6s |
| `wt-1521735922066919515/bin/verify_account_snapshot_corp_action_selfcheck.py` | offline | PASS | 2s |
| `wt-1521735922066919515/bin/verify_account_snapshot_lot_reset_selfcheck.py` | offline | PASS | 2s |
| `wt-1521735922066919515/bin/wakeup_profile_selfcheck.py` | offline | FAIL(rc=1) | 0s |
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
| `wt-1532076080175779942/bin/dt5g_writer_watch_selfcheck.sh` | offline | PASS | 15s |
| `wt-1532076080175779942/bin/filter_lag_entry_window_selfcheck.py` | offline | PASS | 0s |
| `wt-1532076080175779942/bin/mike_json_archive_selfcheck.py` | offline | PASS | 0s |
| `wt-1532076080175779942/bin/nav_cum_dividend_selfcheck.py` | offline | PASS | 14s |
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
| `wt-1532076080175779942/bin/universe_pit_quality_selfcheck.py` | offline | FAIL(rc=1) | 5s |
| `wt-1532076080175779942/bin/verify_account_snapshot_corp_action_selfcheck.py` | offline | PASS | 2s |
| `wt-1532076080175779942/bin/wakeup_profile_selfcheck.py` | offline | FAIL(rc=1) | 0s |
