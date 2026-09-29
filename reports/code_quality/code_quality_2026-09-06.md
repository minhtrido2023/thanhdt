# Code quality weekly — 2026-09-06

File đã quét: 25 (hot-core tuần này: `/home/trido/thanhdt/WorkingClaude/trading_bot/executor.py`)
Finding: 1 (từ 1 trước verify)

## mike/bin/compute_active_nav.py:248 — correctness (high)
- Owner đề xuất: Wags
- NameError: `_dt_stale` is used but never imported/defined, crashing the script whenever an account has both manual_offbook_assets_vnd != 0 and manual_offbook_assets_asof set.
- Bằng chứng: Lines 244-255:
  offbook = float(profile.get("manual_offbook_assets_vnd") or 0)
  offbook_asof = profile.get("manual_offbook_assets_asof") or ""
  if offbook and offbook_asof:
      asof_ref = args.asof or today_ict().isoformat()
      try:
          age_days = (_dt_stale.date.fromisoformat(asof_ref)
                      - _dt_stale.date.fromisoformat(offbook_asof)).days
          ...
      except ValueError:
          pass
`grep -n "datetime\|_dt_stale" mike/bin/compute_active_nav.py` shows `_dt_stale` appears ONLY at lines 248-249 — no `import datetime as _dt_stale` or any definition anywhere in the file (only `import argparse, json, os, subprocess, sys` + `from trading_bot.vn_market import today_ict`). `except ValueError` does not catch `NameError`, so this crashes the whole script with an uncaught traceback instead of the file's normal fail-closed messaging. Currently dormant only because both live accounts (secrets/trading_bot_accounts.json) have `manual_offbook_assets_vnd: 0` today — but this is exactly the code path the file's own docstring describes as a real, previously-used feature ("Trứng vàng DNSE", withdrawn to 0 on 2026-07-20/07-22, per the accounts.json notes), so it will fire again the next time a nonzero off-book balance + asof is configured.
- Đã qua verify độc lập: sống sót phản biện.

## File đã đọc kỹ, không có vấn đề (24)
- dc_book_waterfall_paper.py
- dc_book_waterfall_selfcheck.py
- deploy_golive_dt5g_v4/golive_recommend_v23.py
- dna_report.py
- macro_healthcheck.py
- mike/agents/Taylor/anomaly_scan.py
- mike/agents/Taylor/cap_signal_advisory_check.py
- mike/agents/Taylor/exp_insider/cap_signal_grid_test_round2.py
- mike/agents/Taylor/exp_insider/cluster_buy_scoping.py
- mike/agents/Taylor/exp_insider/dc_3book_real_blend.py
- mike/agents/Taylor/exp_insider/dc_pure_beta_check.py
- mike/agents/Taylor/exp_insider/dc_state_gated_bull_only.py
- mike/agents/Taylor/exp_lag_bullmode_20260830/gate_diagnostic.py
- mike/agents/Taylor/exp_lag_bullmode_20260830/pt_v23_lagbullsue.py
- mike/agents/Taylor/exp_vn2020_2022_recovery/step1_bottoms.py
- mike/agents/Taylor/exp_vn2020_2022_recovery/step1b_peak_check.py
- mike/agents/Taylor/insider_flags.py
- mike/agents/Winston/freshness_warn_selfcheck.py
- mike/bin/bq_monthly_pin.py
- mike/bin/bq_monthly_pin.sh
- mike/bin/check_report_cadence.sh
- mike/bin/check_report_cadence_selfcheck.py
- mike/bin/code_quality_weekly.sh
- mike/bin/custom30v_rebalance_watch.sh