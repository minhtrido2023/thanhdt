# DCF follow-ups 30/10 — SELFCHECK (job Taylor_20261030_073001)
Nhánh `session/dcf-followups-20261030` (outer wt-dcf-followups-20261030 + mike wt-dcf-followups-mike-20261030). Chưa merge.

1. Ghim legacy (`os.environ.setdefault("DCF_RATE_FRAME","legacy")` trước import dcf_valuation): WC dcf_rate_robustness.py; mike: erp_v2.py, impact_v2.py, rf_slow_measure.py, h2_dcf_ab.py, dcf_rich_outlook_20261024/{build_panel,mch_case}.py, dcf_rich_outlook_rerun_20261024/build_panel.py, exp_capitdcf/{build_panel,dcf_mechanism,panelB_events,pool_variants}.py, exp_capit_dcf/capit_dcf_study.py.
   Tái lập (chạy bản sao ra /tmp/fu_repro2, diff với bản commit): erp_v2 + impact_v2 = BYTE-GIỐNG (12 csv + 2 stdout). rf_slow_measure KHÔNG tái lập byte (results.json/today_basket/monthly csv): script lấy "today" = max ngày dữ liệu (10-13 → 10-29) nên vintage dữ liệu đổi, không phải do frame. dcf_rate_robustness: chỉ so định tính (Δ pinned vs fixed +0.0006..0.0013, cùng chiều) — cùng lý do vintage; không so byte.
   Không ghim (ghi nhận, khác lớp — theo prod có chủ đích): custom_basket*.py (classify_dcf), cctg_tier2_banks_20261013/prod_snapshot.py (chụp discount_rate prod), trading_bot/strategies.py.
2. dcf_earning_power CLI in ke_range_note; vòng terminal-g mode bắt ValueError dưới v2 (n/a). Selfcheck [5b] + mutation [M5b].
3. fake_root/mutant dùng _mkdtemp + atexit cleanup. /tmp/dcfrf_* còn lại = 0 (đo `ls /tmp | grep -c dcfrf_`).
4. ops_health CHECKDCFRF quét thêm WorkingClaude/*.sh, trading_bot/*.sh|*.py, WorkingClaude/*.py, mike/bin/*.py (regex python environ[..]=/setdefault/putenv/dict; loại selfcheck, test_*, dcf_valuation, dcf_earning_power, dcf_rate_robustness). Selfcheck [2j][2l][2m][2n][2o] + mutation [M2j][M2l][M2n].

Kết quả: dcf_rate_frame_selfcheck.py OK (45 PASS) ở TZ=UTC và env -u TZ (DCF_RF_OPS_HEALTH trỏ bản mike mới); dcf_refresh_gate / dcf_selector / dcf_check / dcf_earning_power_test OK; ops_health_check{,_lossbrake,_rejected,_autofix_dryrun}_selfcheck OK. Cây PROD: ops_health warn=0.
