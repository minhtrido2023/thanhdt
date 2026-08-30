# Code quality weekly — 2026-08-30

File đã quét: 25 (hot-core tuần này: `/home/trido/thanhdt/WorkingClaude/trading_bot/plan.py`)
Finding: 5 (từ 5 trước verify)

## deploy_golive_dt5g_v4/golive_recommend_v23.py:85 — guideline:§16 (medium)
- Owner đề xuất: Taylor
- bare-datetime-now: END/START/START_BR/START_VNI date windows computed with `datetime.now()` (no ZoneInfo anchor) in the canonical PRODUCTION recommender.
- Bằng chứng: END = datetime.now().strftime("%Y-%m-%d")
START = (datetime.now() - timedelta(days=120)).strftime("%Y-%m-%d")
START_BR = (datetime.now() - timedelta(days=240)).strftime("%Y-%m-%d")
START_VNI = (datetime.now() - timedelta(days=420)).strftime("%Y-%m-%d")
- Đã qua verify độc lập: sống sót phản biện.

## deploy_golive_dt5g_v4/golive_recommend_v23.py:1216 — guideline:§16 (low)
- Owner đề xuất: Taylor
- Report 'Generated' timestamp uses bare `datetime.now()` instead of an ICT-anchored clock.
- Bằng chứng: L.append(f"*Generated {datetime.now():%Y-%m-%d %H:%M}. System: V2.3 = ...")

## mike/agents/Taylor/anomaly_scan.py:379 — guideline:§16 (medium)
- Owner đề xuất: Taylor
- bare-datetime-now: default scan date falls back to `datetime.date.today()` (no TZ anchor) even though the same file defines a careful `_ict_now()` helper elsewhere.
- Bằng chứng: end = datetime.date.fromisoformat(args.asof) if args.asof else datetime.date.today()
- Đã qua verify độc lập: sống sót phản biện.

## mike/agents/Taylor/insider_flags.py:231 — guideline:§16 (medium)
- Owner đề xuất: Taylor
- bare-datetime-now: default `asof` for the insider-sell scan falls back to `datetime.date.today()`, not ICT-anchored; run around midnight ICT under a UTC host could pick yesterday's date and shift the 90-day window.
- Bằng chứng: asof = datetime.date.fromisoformat(args.asof) if args.asof else datetime.date.today()
- Đã qua verify độc lập: sống sót phản biện.

## dna_report.py:69 — guideline:§16 (low)
- Owner đề xuất: Taylor
- DT5G regime staleness flag computed with `date.today()` (no TZ anchor) instead of an ICT-anchored date.
- Bằng chứng: from datetime import date
lag = (date.today() - pd.Timestamp(asof).date()).days
stale_flag = lag > 2

## File đã đọc kỹ, không có vấn đề (21)
- agents/Taylor/build_bank_npl_coverage.py
- bank_lens_v3.py
- c1_shadow_paper.py
- capit_lever_selfcheck.py
- cash_only_loan_package_selfcheck.py
- cpi_vn.py
- dc_book_waterfall_paper.py
- dc_book_waterfall_selfcheck.py
- dc_bull_signal_by_state.py
- dnse_api_full_test.py
- exdate_price_frame_selfcheck.py
- hybrid_fill_timing_selfcheck.py
- lag_forensic_filter.py
- lag_forensic_filter_selfcheck.py
- loan_package_resolution_selfcheck.py
- mike/agents/Taylor/exp_lag_advdyn_20260825/pt_v23_advdyn.py
- mike/agents/Taylor/exp_lag_advdyn_20260825/run_leg.sh
- mike/agents/Taylor/exp_lag_bull_park_20260825/run_bullpark.sh
- mike/agents/Taylor/universe_freshness_selfcheck.py
- mike/agents/Winston/freshness_warn_selfcheck.py
- mike/bin/append_event.sh