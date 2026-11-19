# Dọn research cũ 19/11/2026 (user duyệt 18:55 ICT, `decided_by: user`)
Luật user: DD đã xong chỉ cần cập nhật tiếp → GIỮ; nghiên cứu khác xong và im >3 ngày → xoá.
## Đã làm
- Xoá khỏi working tree (git rm) mọi file KHÔNG phải `.md` trong **259** thư mục `agents/Taylor/research/*` (không phải `dd_*`, mtime ≤ 2026-11-16, không bị bin/*.py, ../*.py, trading_bot, cron, registry tham chiếu): 201.902 file tracked (~1,7G). **Giữ mọi `.md`** (REPORT/README/PREREG) nên con trỏ trong KB vẫn mở được.
- Khôi phục: `git checkout 395e59dd46e9896a296fe3c5b7b0c1be437877bd -- agents/Taylor/research/<thư_mục>` (commit cha của lần dọn này; file nằm nguyên trong lịch sử git).
- KHÔNG đụng: toàn bộ `dd_*`; 45 thư mục có code/cron tham chiếu (danh sách dưới); file CHƯA track (pkl/parquet ~1,4G, `.gitignore` ghi không tái tạo được) — chờ user quyết.
- Worktree gỡ: `wt-lag-early-exit-20261116` (NO-GO, nhánh `research/lag-early-exit-20261116` giữ), `wt-1571329025157103646` (commit đã có trên master 3158615c0) + 6 worktree đã merge.
## Vì sao `agents/Taylor` ~7G
File thật được git track (PDF BCTC/DD ~3,2G, CSV ~2,1G chủ yếu live_gap_exec_*, PNG ~1,1G) ⇒ mỗi worktree checkout đủ ~7G. Giảm: tạo worktree bằng sparse-checkout (không lấy `agents/Taylor/research`).
## Thư mục code tham chiếu (giữ nguyên)
- thin_exec_20260812
- dcf_vn_calibration_20261101
- rating_8l_forward_bt_20261020
- dividend_yield_floor_20260818
- ceiling_ab_pacing_20260814
- discretionary_lane_c_earnings_growth_20261006
- upcom_ref_anchor_20260815
- rating_8l_lag_20261020
- livermore_divergence_20261114
- erp_domestic_v2_20261030
- commodity_cycle_prereg_20261025
- lag_cache_adjusted_20261110
- aria_F_20260913
- oshares_live_r10_20261031
- lag_entry_window_width_20261021
- fund_cashflow_detect_20261012
- fund_step4_20261014
- orb_reeval_20260925
- dcf_level_rerun_20261102
- oshares_freeze_live_20260914
- discretionary_dd_pick_v2_20261101
- live_gap_phase0_20261112
- oshares_weight_exdate_20260927
- dc_3book_architecture_20260825
- oshares_gate_move_20260813
- amh_changepoint_fitness_20260910
- lag_fidelity_decomp_20260803
- capital_raise_warning_20261029
- intraday_watch_20261006
- lag_rights_audit_20261022
- price_freeze_gate_20260927
- idle_cash_proxy_20260927
- self_computed_adjfactor_20260927
- exdate_order_pipeline_20260815
- lag_rating_lag_q3_20261111
- livermore_report_block_20261025
- discretionary_funnel_adaptive_pb_round3_20260830
- ledger_seal_weekly_20261016
- yield_floor_custom30v_phase1_20260818
- commodity_cycle_prereg2_20261025
- orb_threshold_recalc_20260925
- decision_inbox_design_20261113
- nav_jump_gate_20260927
- oshares_live_anchor_20260820
- opening_window_limit_20260926
## Thư mục đã xoá file nặng
book_regime_fit_20261110, live_gap_exec_A, live_gap_phase1b_20261112, live_gap_phase1c_20261112, live_gap_exec_A3, live_gap_exec_A4, mania_20260903, live_gap_exec_A5, ccs_phase0_Taylor_20260905_135003, valuetrap_20260904, discretionary_sleeve_correlation_20260830, strategy_regime_matrix_20260822, rerun_groupB_fixed_20261009, blind_val_20261114, live_gap_exec_A2, dcf_expectation_lens_20261101, live_gap_exec_A6, ftse_upgrade_revalidate_20261013, adaptive_exclusion_20260904, dri_val_supply_adj_r4_20261027, exit_signal_backtest_20260721, live_gap_exec_D, ta_schools_vn_20261025, top5_postearnings_sleeve_20260818, liquidity_burst_pattern_20260826, valuation_gated_tier_unlock_20260830, live_gap_exec_E, postshock_20260823, survivorship_replay_20261020, bal_2025_diagnosis_20260909, dcf_rich_outlook_rerun_20261024, first_disclosure_feasibility_20260917, lag_per_share_surprise_rights_20261022, c30v_position_replay_20260927, survivorship_volzero_20261020, serial_capital_raiser_20260817, div_growth_signal_20260821, firm_behavior_fingerprint_20261016, kaffa_correlation_cluster_20260910, dgc_valuation_20261027_r5, rating_8l_lag_p2v2_20261020, vn_market_efficiency_20260910, live_gap_phase2b_20261112, rating_8l_lag_p2_20261020, dgc_valuation_20261029_r12, dgc_valuation_20261029_r11, dgc_valuation_20261029_r10, dgc_valuation_20261029_r9, corp_action_program_20260815, ta_model_5pct_20261106, report_v2_wire_20261031, bal_edge_monthly_gate_20261110, rating_8l_eff_guard_20261020, survivorship_sensitivity_v2_20261020, survivorship_sensitivity_20261020, screen_regen_20260927, report_style_v2_20261031, ccs_phase0_earnings_quality, dcf_rich_outlook_20261024, live_gap_exec_A7, live_gap_phase3_20261112, selfcheck_write_scan_20260927, ccs_phase2_Taylor_20260906_153255, dgc_valuation_20261027_r4, extreme_bottom_recognition_20260823, cash_dividend_announcement_premium_20260904, dgc_valuation_20261029_r8, fearbuy_blend, fund_unit_ledger_20261011, live_gap_exec_A9, lag_runup_effect_20261024, capit_tranche_probe, fearbuy_screen, livermore_stock_pilot_20261022, oshares_live_r9_20261031, report_v2_r3_20261031, div_growth_tilt_20260821, oshares_live_r8_20261031, live_gap_phase2a_20261112, custom30v_selector_20260909, custom30v_placebo_20260910, bal_edge_gate_20260910, dgc_valuation_20261029_r7, bal_maxpos_lag_idle_20261009, dgc_valuation_20261027_r6, erp_domestic_20261030, dgc_valuation_20261027_r2, dgc_valuation_20261027_r3, dgc_valuation_20261027, oshares_fwd_absorb_20260914, failg_icb_pit_20260927, fiinprox_h3_h1_h2_20260927, oshares_live_r12_20261031, adaptive_gate_20260723, survivorship_followup_20261020, daily_return_gate_20261010, measurement_integrity_audit_20260927, intraday_cutloss_replay_v2_20261009, dgc_ke_domestic_20261030, failc_sweep8_20260927, lag_bal_discriminators_20261025, entry_risk_tech_20261022, oshares_live_r11_20261031, intraday_cutloss_replay_20261009, discretionary_funnel_adaptive_pb_20260830, early_recovery_margin_lever_20260825, fund_history_lock_20261014, dcf_discount_rate_rf_slow_20261013, fpt_dd_tech_20261014, pre_exdate_avoidance_20260821, orb_diagnosis_20260925, lag_price_reaction_class_20261022, live_gap_exec_B4, out, fiinprox_h4_h5_20260927, lag_edge_exitkey_20260910, capit_flag_gate_20261103, dcf_rate_proxy_20261102, trend_basics_filter_20261025, iss_event_study_20260821, margin_valuation_spread_phase1_20260823, postmerge_haukiem_20260927, ta_trend_entry_filter_20261025, breadth_tercile_recheck_20260927, bctc_q3_m1_gate_impl_20261013, discretionary_funnel_adaptive_pb_redo_20260830, total_return_gips_20261010, pump_before_raise_flag_20260817, treasury_oshares_overlay_20260907, fiinprox_h1h2_wire_20260927, bal_neutral_gate_20260909, vnindex_tr_sealed_20261021, oshares_lookback_20260820, c30v_w2_q2_20260927, rate_source_label_12m_20261014, bal_adaptive_exit_20260909, fpt_dcf_deconsol_20261014, failopen_inventory_20260928, cctg_tier2_banks_20261013, park_fraction_grid_20260927, capit_margin_hold_lock_20261013, custom30v_accrual_gate_20260830, fund_step4_r2_20261014, treasury_table_20260918, strategy_fit_email_20261011, margin_valuation_spread_20260823, liquidity_spread_deposit_lead_20261105, oshares_live_dcf_20261030, repin_dep1m_20260928, discretionary_8l_funnel_20261006, dt5g_gate_tzaware_20261011, fearbuy_idio, commodity_p4_sulfur_20261026, execution_alpha_20260925, ais_chain_order_20261019, bal_concentration_cap_20261022, treasury_reconcile_20260917, fund_step4_impl_20261014, iss_median_study_20260821, dt5g_gate_followups_20261012, bal_loss_attribution_20261022, orb_fiinx_vn30f1m_20260925, oshares_live_r2r7_20261030, live_gap_exec_B5, rights_alerts_nb_20261025, dt_badzone_count_20261019, lag_forensic_20260803, aria_A1_20260913, nav_loss_brake_20261012, dcwf_regen_20260930, vn_rational_vs_overreaction_framework_20260831, strategy_fit_tier3_20261012, repin_park0_dep1m_20261008, rating_8l_pit_2010_20261020, dt5g_ext_2008_20260904, dri_val_supply_adj_20261027, dgc_discount_rate_20261029, vn_gold_price_equity_channel_20260831, sector_frames_20261026, discretionary_sleeve_candidate_funnel_20260830, vn_breadth_of_prior_rally_20260831, c30v_hau_kiem_20260927, basket_ca_pin_20260927, ccs_phase1_Taylor_20260905_141801, monthly_report_202609, live_gap_phase1_20261112, repin_park030_20260927, listing_date_exchange_study_20260817, weekly_20261026_20261030, c30v_retleg_repin_20260927, orderbook_shadow_checkpoint_20261014, dri_val_supply_adj_r2_20261027, vn_top_divergence_and_margin_selloff_20260831, cash_div_first_disclosure_validation_20261009, live_gap_exec_B2, fpt_q3_eval_20261021, idle_pool_redeploy_20260927, extreme_bottom_mechanism_classifier_20260823, gate_source_check_20261012, faild_divtax_20260927, erp_domestic_dcf_enable_20261030, vn_2009_recovery_trigger_20260831, lag_quality_20260803, aria_K_20260913, bal_edge_gate_20261110, dri_val_supply_adj_r3_20261027, rule_a_ref_guard_20260815, adjfactor_repair_20260927, tv1_sb5_ppa_price_20261013, live_gap_exec_C2, lag_disc_blended, failc_residual_20260927, alphalens_audit_20261001, park_holdings_manual_sell_20261022, funnel_lane_c_season_20261006, aria_H_20260913, aria_A2_20260913, live_gap_exec_B3, oshares_absorption_20260820, lagedge_causal_20260927, lag_rights_n1_20261022, forensic_failclosed_20260927, vn_2012_recovery_trigger_20260831, vn_prior_trend_meanreversion_hypothesis_20260831, vn_2022_2018_margin_signature_recheck_20260831, oshares_warn_20260814, funnel_lane_c_build_20261006, failc_ab_20260927, vnindex_tr_restate_20261021, vn_2020_2022_recovery_trigger_20260831, navflow_annualize_20260927, lag_repin_20260803, dgc_q3_forecast_20261026, weekly_20261012_20261016, vn_all_corrections_inventory_20260831, rnd_direction_shortlist_20260925, plan_report_audit_20260928, decision_inbox_impl_20261113, bctc_q3_readiness_20261013, avc_tv1_hydrology_20261023, weekly_20261019_20261023, vnindex_tr_polish_20261021, live_gap_exec_B, lag_rights_patches_20261022, final_pin_20260927, corp_action_snapshot_aprime_20260915, branch_audit_20261016, anchor_reverify_20260927, lag_dd_gate_20261021, crisis_dd_HT1_20261030, cpi_pit_merge_fix_20261025, codex_dns_block_20260814, selfcheck_red_20260814, margin_cap_recovery_forensic_20260825, macro_snapshot_asof_20261105, dcf_followups_20261030, cutloss_crisis_dd_20261101, crisis_dd_HT1, dcwf_regen_20260930_2
