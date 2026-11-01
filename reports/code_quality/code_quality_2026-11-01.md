# Code quality weekly — 2026-11-01

File đã quét: 25 (nguồn FALLBACK diff 7 ngày (manifest HEAD lệch thực tế (production_manifest.py --check): DRIFT 8 dòng — manifest commit lệch thực tế. Nếu thay đổi là CỐ Ý: chạy `python3 mike/bin/production_manifest.py` rồi commit kb/production_manifest.{json,md}. + mike/bin/report_v2/__init__.py [T0] (mới vào production, từ mike/bin/report_delivery_gate.py) + mike/bin/report_v2/artifact_lint.py [T0] (mới vào production, từ mike/bin/report_v2/build.py)); hot-core round-robin: /home/trido/thanhdt/WorkingClaude/mike/bin/ops_autofix.sh)
Finding: 6 (từ 6 trước verify)

## /home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_capitdcf/dcf_mechanism.py:20 — correctness (high)
- Owner đề xuất: Taylor
- The MoS calculation uses the back-adjusted Close as price instead of the unadjusted Price. Per-share FV is computed on that day's OShares, so the MoS is distorted by each stock's later corporate actions (look-ahead). This contaminates the 'DCF MoS IC +0.187' result in RESULT.md.
- Bằng chứng: line 20: `px = r["Close"]`; line 22: `D.fair_value(r["ticker"], r["entry"], price=float(px), fin=fin)`. data/capit_selection_features.csv row 1: HPG 2014-05-09 Close=2680.0, while ticker_prune for the same day has Price=46200.0, Close=2680.0 (17x apart). The sibling scripts build_panel.py:43, panelB_events.py:31 and exp_capit_dcf/capit_dcf_study.py:48 all use `COALESCE(Price,Close)`. RESULT.md:18 `| DCF MoS | **+0.187** | 1.40 | 13 |`.
- Hướng sửa đề xuất: Join the unadjusted Price from ticker_prune by (ticker, entry) and use it as price for fair_value, then rerun dcf_mechanism.py and update RESULT.md/RESULT_RANKPRIMARY.md. The within-event IC changes because the adjustment factor differs per ticker.
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/dc_book_waterfall_paper.py:565 — correctness (medium)
- Owner đề xuất: Taylor
- If the state file is corrupt or unreadable, _load_state silently returns None. advance() then re-initialises the sleeve at the original NAV basis, and _save_state overwrites the old file, wiping the paper track record (nav_vnd, cum_pnl_pct, weights, history) without any log line.
- Bằng chứng: lines 502-509: `try: ... return json.load(f) except Exception: return None`; line 565: `st = _load_state() or _init_state(nav_basis(account))`; line 705: `_save_state(st)` (os.replace). Runs daily from cron `15 17 * * 1-5 ... dc_book_waterfall_paper.py --update`.
- Hướng sửa đề xuất: Distinguish a missing file (→ init) from an existing but unreadable file (→ print a loud warning, back the file up to .corrupt, skip this run's advance). Do not re-init over it.
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/dcf_valuation.py:338 — correctness (medium)
- Owner đề xuất: Taylor
- _load_routes/_load_icb_map swallow read errors and permanently cache an empty result. is_financial() then returns False for every stock, so banks, insurers and brokers get valued with FCFE DCF (the wrong model) silently for the rest of the process.
- Bằng chứng: lines 322-323: `except Exception: _ICB_CACHE = {}`; lines 338-339: `except Exception: _ROUTE_CACHE = pd.DataFrame(columns=["ticker","time","route"])`; is_financial lines 346-352: empty routes → `is_financial_icb(_load_icb_map().get(ticker, np.nan))` → NaN → not financial. No warning anywhere.
- Hướng sửa đề xuất: On read error, print one loud stderr warning (use the module's existing _shout) and do not cache the empty value, or have fair_value return NOT_COMPUTED with reason 'sector map unavailable' instead of falling through to FCFE.
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_capitdcf/panelB_events.py:26 — correctness (medium)
- Owner đề xuất: Taylor
- fwd() has no guard for a truncated horizon. For late events, r250 (and possibly r120) is a partial-horizon return mixed into the mean/LOO of the N=14 panel. build_panel.py:36 has this guard (`if j < h*0.8: return nan`), but panelB is missing it.
- Bằng chứng: line 26: `return s.iloc[min(h, len(s)-1)] / s.iloc[0] - 1`. EVENTS includes '2026-03-09' and '2025-10-20'; ticker_prune cache max(time)=2026-10-30, so 2026-03-09 + 250 sessions falls past the end of the data and r250 is only ~160 sessions.
- Hướng sửa đề xuất: Add the same guard as build_panel.fwd (return NaN when available sessions < 0.8*h) so truncated events are dropped from the h=120/250 rows instead of being counted as a full horizon.
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/deploy_golive_dt5g_v4/golive_recommend_v23.py:487 — correctness (low)
- Owner đề xuất: Taylor
- The nav_history fallback in _account_nav_basis takes the last CSV row with no age check (active_nav right above has one via ACTIVE_NAV_MAX_AGE_D). If daily_nav_snapshot stops, an arbitrarily stale total NAV is used to split the CAPIT %ADV cap across accounts.
- Bằng chứng: lines 486-489: `r = pd.read_csv(p2).iloc[-1]; nav2 = float(r["nav"]); if nav2 > 0: ... return nav2, ...` — only checks nav2 > 0, not the age of r['date'] (the docstring says the file is 'dated theo nội dung', but the code never compares that date).
- Hướng sửa đề xuất: Compute the age from r['date'] the same way as the active_nav block. If it exceeds a few sessions, append a reason and do not use the value (fall back to equal split / None as already designed).

## /home/trido/thanhdt/WorkingClaude/mike/bin/ops_autofix.sh:146 — correctness (low)
- Owner đề xuất: Wags
- The Trading Daily notification says the fixer is 'Winston/fable', but the actual dispatch is `--model opus` (the downgrade was made 2026-07-17). The user-facing message is wrong about the model running.
- Bằng chứng: line 146: `"🔧 [ops-autofix] ... đã tự động cử agent chẩn đoán + sửa (Winston/fable)."`; line 177: `--bg --thread "$TRADING_DAILY_THREAD" --timeout "$AUTOFIX_TIMEOUT" --model opus`; header lines 9-10: 'Model hạ từ fable xuống opus (cost-opt model-drift fix, 2026-07-17)'.
- Hướng sửa đề xuất: Change the text on line 146 to 'Winston/opus', or better, derive it from a single variable shared with --model on line 177 so the two cannot drift apart again.

## File đã đọc kỹ, không có vấn đề (20)
- /home/trido/thanhdt/WorkingClaude/bot_execute.py
- /home/trido/thanhdt/WorkingClaude/capit_lever_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/cctg_deposit_wiring_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/cctg_tier2_series_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/cpi_vn.py
- /home/trido/thanhdt/WorkingClaude/cpi_vn_tier15_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/custom_basket.py
- /home/trido/thanhdt/WorkingClaude/dcf_backtest.py
- /home/trido/thanhdt/WorkingClaude/dcf_earning_power.py
- /home/trido/thanhdt/WorkingClaude/dcf_fv_sens_cache.py
- /home/trido/thanhdt/WorkingClaude/dcf_rate_frame_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/dcf_rate_robustness.py
- /home/trido/thanhdt/WorkingClaude/deploy_golive_dt5g_v4/publish_gated_state.py
- /home/trido/thanhdt/WorkingClaude/deploy_golive_dt5g_v4/publish_run_log.py
- /home/trido/thanhdt/WorkingClaude/fetch_bdi_daily.py
- /home/trido/thanhdt/WorkingClaude/fetch_bdi_daily_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/freshness_ops_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/macro_killswitch_a_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_capit_dcf/capit_dcf_study.py
- /home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_capitdcf/build_panel.py