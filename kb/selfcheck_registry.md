---
kind: reference
title: Selfcheck registry — snapshot tự sinh, ĐỪNG sửa tay
generated_by: bin/run_selfchecks.sh
generated_at: 2026-08-01T15:33:53Z
---

# Selfcheck registry (auto-generated, ĐỪNG sửa tay — sửa `bin/run_selfchecks.sh`)

Chạy: `bash mike/bin/run_selfchecks.sh [--live]`. Lần gần nhất: 38 PASS / 6 FAIL / 14 SKIP (live).

| File | Tier | Status | Thời gian |
|---|---|---|---|
| `anomaly_gate_prod_parity_selfcheck.py` | offline | PASS | 2s |
| `anomaly_gate_selfcheck.py` | offline | FAIL(rc=1) | 7s |
| `approval_gate_selfcheck.py` | offline | PASS | 0s |
| `capit_participation_cap_selfcheck.py` | offline | PASS | 0s |
| `cash_only_loan_package_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `churn_guard_selfcheck.py` | offline | PASS | 1s |
| `concurrent_lock_selfcheck.py` | offline | PASS | 0s |
| `dc_book_waterfall_selfcheck.py` | offline | PASS | 0s |
| `dcf_check_selfcheck.py` | offline | PASS | 1s |
| `dcf_refresh_gate_selfcheck.py` | offline | PASS | 0s |
| `dcf_selector_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `discretionary_accumulation_selfcheck.py` | offline | PASS | 0s |
| `discretionary_participation_cap_selfcheck.py` | offline | PASS | 0s |
| `dt5g_chain_freshness_selfcheck.py` | offline | PASS | 0s |
| `due_diligence_selfcheck.py` | offline | PASS | 9s |
| `edge_wlag_gate_selfcheck.py` | offline | PASS | 1s |
| `excluded_tickers_selfcheck.py` | offline | PASS | 0s |
| `extreme_regime_selfcheck.py` | offline | PASS | 0s |
| `eyrisk_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `freshness_ops_selfcheck.py` | offline | FAIL(rc=1) | 2s |
| `ghost_order_selfcheck.py` | offline | PASS | 0s |
| `immutable_publish_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `lag_adv_cap_selfcheck.py` | offline | PASS | 0s |
| `lag_liq_signal_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `lag_live_schedule_selfcheck.py` | offline | PASS | 23s |
| `lag_rating_filter_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `lag_rating_order_gate_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Mafee/reconcile_parents_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/anomaly_escalate_selfcheck.py` | offline | PASS | 1s |
| `mike/agents/Taylor/capit_dd_gate_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Taylor/chase_cap_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/insider_flags_selfcheck.py` | offline | PASS | 0s |
| `mike/agents/Taylor/seccap_dyn_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `mike/agents/Winston/freshness_warn_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/build_universe_pit_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/consolidate_git_scope_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/cursor_advance_selfcheck.py` | offline | PASS | 2s |
| `mike/bin/dt5g_publisher_gate_selfcheck.sh` | offline | PASS | 0s |
| `mike/bin/dt5g_writer_watch_selfcheck.sh` | offline | PASS | 16s |
| `mike/bin/mike_json_archive_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/nav_scripts_2account_selfcheck.py` | offline | FAIL(rc=1) | 10s |
| `mike/bin/ops_health_check_selfcheck.py` | offline | PASS | 1s |
| `mike/bin/paper_report_render_selfcheck.py` | offline | PASS | 0s |
| `mike/bin/run_selfchecks.sh` | live | SKIP(--live để chạy) | - |
| `mike/bin/universe_pit_quality_selfcheck.py` | offline | FAIL(rc=1) | 5s |
| `money_path_freshness_selfcheck.py` | offline | PASS | 2s |
| `net_offsetting_orders_selfcheck.py` | offline | PASS | 0s |
| `netting_recon_selfcheck.py` | offline | PASS | 0s |
| `paper_main_window_selfcheck.py` | offline | PASS | 0s |
| `restate_guard_selfcheck.sh` | live | SKIP(--live để chạy) | - |
| `route_selector_selfcheck.py` | offline | PASS | 4s |
| `sync_cache_lock_selfcheck.py` | offline | FAIL(rc=1) | 5s |
| `t2_settlement_selfcheck.py` | offline | PASS | 0s |
| `tick_retry_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `universe_pit_p2_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `universe_pit_p3_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `universe_pit_p4_selfcheck.py` | live | SKIP(--live để chạy) | - |
| `v4final_selector_selfcheck.py` | live | SKIP(--live để chạy) | - |
