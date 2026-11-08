# Code quality weekly — 2026-11-08

File đã quét: 25 (nguồn FALLBACK diff 7 ngày (manifest HEAD lệch thực tế (production_manifest.py --check): DRIFT 2 dòng — manifest commit lệch thực tế. Nếu thay đổi là CỐ Ý: chạy `python3 mike/bin/production_manifest.py` rồi commit kb/production_manifest.{json,md}. - mike/bin/work_tree_server.py [T2] (rời production) - mike/bin/work_tree_tunnel.sh [T2] (rời production)); hot-core round-robin: /home/trido/thanhdt/WorkingClaude/trading_bot/plan.py)
Finding: 11 (từ 11 trước verify)

## /home/trido/thanhdt/WorkingClaude/trading_bot/plan.py:415 — correctness (high)
- Owner đề xuất: Taylor
- net_offsetting_orders() builds the NET order from only a subset of fields. It drops hard_no_chase_ceiling_vnd, ceiling_rule/anchor/tau, hard_sell_floor_vnd and cash_only from the lead leg, so these hard guards disappear for any ticker that gets netted.
- Bằng chứng: plan.py:415-426 constructs PlannedOrder(id=..., ticker, side, qty, ref_price=lead.ref_price, book, play_type, priority, urgency, note, dcf_check, dcf_override_reason, dd_check, dd_override_reason). It does not copy hard_no_chase_ceiling_vnd, hard_sell_floor_vnd or cash_only. Pipeline order in bot_execute.py: load_plan (plan.py:256-265 sets hard_no_chase_ceiling_vnd at the load boundary) -> ... -> bot_execute.py:591 net_offsetting_orders. Nothing restores the ceiling afterwards: grep for hard_no_chase_ceiling_vnd/cash_only in bot_execute.py returns nothing, and executor.py:838/852/1041 reads the field from the order via getattr(...). dd_flag_order_gate_selfcheck.py:260-266 (NET-C) shows a real NET order with lead book=DISCRETIONARY_SPECIAL (the book that carries cash_only + hard ceiling, case TV1/UPCOM).
- Hướng sửa đề xuất: In net_order, copy from lead (only when side matches): hard_no_chase_ceiling_vnd + the 4 ceiling_* fields for buy, hard_sell_floor_vnd for sell, cash_only. For buy, take min() of the ceilings across all buy legs and max() of the floors across sell legs (the tighter bound). Add a selfcheck: BUY with ceiling + smaller SELL on the same ticker => the NET BUY keeps the ceiling.
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/trading_bot/plan.py:2239 — correctness (high)
- Owner đề xuất: Taylor
- approval_block_reason() treats any non-empty approved_by string as approved, except none/null/nil/nan. A plan with requires_user_approval=true and approved_by='auto'/'pending'/'false'/'DollarBill' passes the approval gate and runs live, even though the file already defines APPROVAL_PLACEHOLDERS listing exactly these strings.
- Bằng chứng: plan.py:2240-2247: if approved.lower() in ('none','null','nil','nan'): approved = '' / if approved: return None. Meanwhile plan.py:1143-1145 APPROVAL_PLACEHOLDERS = ('', 'none', ..., 'false', '0', 'pending', 'tbd', 'auto', 'agent', 'bot', 'system', 'mike', 'dollarbill', ...) is used only by margin_day_approval (plan.py:1340). Real precedent: grep data/trade_plans/*.json finds 6 plans (SpaceX 2026-07-07..07-13) where the generator wrote approved_by='auto' (that time with requires_user_approval=False, so the gate was not exercised).
- Hướng sửa đề xuất: In approval_block_reason, replace the 4-string tuple with APPROVAL_PLACEHOLDERS (approved.lower() in APPROVAL_PLACEHOLDERS => treat as unapproved). Add a selfcheck case: requires_user_approval=true + approved_by='auto'/'pending' => blocked.
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/bot_execute.py:447 — guideline:§20 (medium)
- Owner đề xuất: Taylor
- --accept-gdkhq-by defaults to 'user'. Running --accept-gdkhq-shadow (which turns on live D1-D3 GDKHQ) without the flag writes accepted_by='user' into the acceptance state, even when an agent ran it: a fabricated 'user approved' record on the money path.
- Bằng chứng: bot_execute.py:447: ap.add_argument('--accept-gdkhq-by', default='user', ...); :508 accept_gdkhq_shadow(args.accept_gdkhq_shadow, args.accept_gdkhq_by, ...); trading_bot/gdkhq_rollout.py:205 writes 'accepted_by': str(accepted_by). §20: mark 'user' only when the user actually confirmed in real time.
- Hướng sửa đề xuất: Drop the default (required=True when --accept-gdkhq-shadow is used), or reject 'user'/empty/APPROVAL_PLACEHOLDERS and require a specific name + approval reference.
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/dcf_valuation.py:401 — correctness (medium)
- Owner đề xuất: Taylor
- terminal_growth() hardcodes cpi_monthly_df(end='2026-12-01'). From 2027-01 on, the 5-year CPI window silently loses the newest months: the mean is taken over a series cut off at 12/2026, and cpi_coverage() does not warn because it only checks up to that same hardcoded end.
- Bằng chứng: dcf_valuation.py:400-404: _CPI_DF = _cpi.cpi_monthly_df(end='2026-12-01'); w = cpi[(cpi.time <= a) & (cpi.time > a - 365*years)]. cpi_vn.py:361 cpi_coverage(end) only reports the gap up to end. Example: asof=2027-04-15 -> the window is missing 2027-01..04, g_T/g_terminal_frac_real are computed on the old window and nothing prints. Today is 2026-11-08, so this kicks in in under 2 months. (Under domestic_v2, g = min(cpi+gdp, 5.5%), so the FV impact is often capped, but g_terminal_frac_real and the legacy frame are affected directly.)
- Hướng sửa đề xuất: Pass end = month start of asof (or today ICT), and key the cache by end, so cpi_coverage() warns correctly when a month has no real source.
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/dc_book_waterfall_selfcheck.py:225 — assert-on-live-state (medium)
- Owner đề xuất: Taylor
- Section D asserts on the current production config instead of an invariant. It turns red when the user changes an unrelated flag or turns off the paper trial, even though the dc_book code is correct.
- Bằng chứng: dc_book_waterfall_selfcheck.py:230-231 ok('D1 chase_cap_vol_scale is LIVE (default True since 2026-08-04)', DEFAULTS.get('chase_cap_vol_scale_enabled') is True) is an executor flag unrelated to this module. :233-234 profiles = load_accounts(load_config()); ok('D2 main resolves flag ON', profiles['main']['cfg'].get('dc_book_waterfall_enabled') is True) reads the real trading_bot_accounts.json. :408 ok('E5 v1 NAV series archived', os.path.exists(data/dc_book_waterfall_paper_nav_v1.csv)) depends on a production artifact. (§23 corollary 1)
- Hướng sửa đề xuất: Remove the chase_cap_vol_scale assert. Replace D2/E5 with an invariant: no live account (mode=live) has the flag ON. The 'main ON' check belongs in ops_health, not the selfcheck.
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/converge_report.py:50 — duplicate-formula (low)
- Owner đề xuất: Taylor
- The 'double-confirm' rule (sector_lens status=BUY AND 8L rating ≤2) is copied by hand in at least 3 files, which will drift when the threshold changes in one place.
- Bằng chứng: grep -rn 'int(rt) <= 2': converge_report.py:61 (_live_double_confirm), dc_book_waterfall_paper.py:402 (load_double_confirm, docstring :393 'Identical selection to converge_report._live_double_confirm'), newdeals_daily_report.py:99. All three bodies are the same: slm.compute_status() -> df[df.status=='BUY'] -> ratings.get(t) <= 2 -> buy_mode or 'ACCUMULATE'.
- Hướng sửa đề xuất: Move it into one function (e.g. sector_lens_monitor.double_confirm_set()) and have all 3 consumers call it. Keep each caller's fail mode as is ({} vs None).

## /home/trido/thanhdt/WorkingClaude/dc_book_waterfall_paper.py:635 — correctness (low)
- Owner đề xuất: Taylor
- When a held name has no close on the advance day (suspended or missing from the cache), r_i is set to 0, and new_close drops that name. From then on c0 is permanently None, so the return between the last known close and the resumption price is never booked into the paper NAV.
- Bằng chứng: dc_book_waterfall_paper.py:634-635: c0, c1 = prev_close.get(t), closes.get(t); r_i = (c1/c0 - 1.0) if (c0 and c1) else 0.0. :679 new_close = {t: closes[t] for t in target_w if t in closes}, so a name with no close today drops out of last_close while its weight stays in target_w (drifted). On resumption day c0 = None, so r_i = 0 again and the gap (e.g. -20% during the halt) is lost permanently, overstating cum_pnl_pct.
- Hướng sửa đề xuất: Carry forward the old close for names with no price today: new_close = {t: closes.get(t, prev_close.get(t)) ...} and log/flag the day's row as having a missing price (no silent 0).

## /home/trido/thanhdt/WorkingClaude/cpi_vn_tier15_selfcheck.py:168 — assert-on-live-state (low)
- Owner đề xuất: Taylor
- The freshness-gate test asserts the gap is exactly the 4 months 2026-09..12. That value depends on NSO_CPI_YOY_REAL currently ending at 2026-06 and TE being off. Doing the fix the warning itself recommends (refresh NSO_CPI_YOY_REAL from GSO) turns the selfcheck red even though the code is correct.
- Bằng chứng: cpi_vn_tier15_selfcheck.py:168-171: ok([str(d.date()) for d in gap2] == ['2026-09-01','2026-10-01','2026-11-01','2026-12-01'], ...). cpi_vn.py:305 warning: 'FIX = refresh NSO_CPI_YOY_REAL from the GSO monthly release'. Also test_dcf :266/:286 requires all 7 named tickers (CSV, DGC, DRI, NCT, SAB, TV1, VNM) to price on live data (bq_cache) via ok(len(priced) == 7).
- Hướng sửa đề xuất: Assert on the relation instead: gap2 == the months from max(real_last, fp_last)+1 to 2026-12 (computed from the module's own tier data); in test_dcf require len(priced) >= 3.

## /home/trido/thanhdt/WorkingClaude/dcf_valuation.py:1032 — correctness (low)
- Owner đề xuất: Taylor
- latest_price_session(asof) only falls back to 2*.parquet when the year file errors on read. If the year file exists but has no row ≤asof for the ticker (asof = 1/1 holiday, or a ticker halted early in January), it returns (None, None) and dcf_check reports NOT_COMPUTED 'no_price', even though the previous year has a price.
- Bằng chứng: dcf_valuation.py:1030-1040: yr = str(year(asof)); try: read_parquet('.../ticker/{yr}.parquet') WHERE ticker=... AND time <= asof LIMIT 1 / except: read '2*.parquet'; if len(df) == 0: return None, None. By contrast price_session_for (:913-923) already reads both {a.year-1} and {a.year}.
- Hướng sửa đề xuất: Read both the {yr-1} and {yr} files (like price_session_for), or fall back to 2*.parquet when df is empty, not only on exception.

## /home/trido/thanhdt/WorkingClaude/trading_bot/plan.py:122 — bare-datetime-now (low)
- Owner đề xuất: Taylor
- TradePlan.save() stamps created_at with a bare datetime.now(), which depends on the host TZ (debt already recorded in tz_anchor_baseline: trading_bot/plan.py=1).
- Bằng chứng: plan.py:122: d['created_at'] = d['created_at'] or dt.datetime.now().isoformat(timespec='seconds'). mike/kb/tz_anchor_baseline.json files['trading_bot/plan.py'] = 1. executor.py:345 only compares created_at for equality, so trading logic is unaffected, but the timestamp is wrong under cron env -u TZ.
- Hướng sửa đề xuất: Use dt.datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')) and lower the baseline with --update-baseline.

## /home/trido/thanhdt/WorkingClaude/failopen_telegram_refresh_selfcheck.py:93 — correctness (low)
- Owner đề xuất: Taylor
- The 'new version still print-only' assertion is a tautology. The condition `needle not in new or '_notify_failopen' in new` is always true once line 83 has confirmed _notify_failopen is in new, so the check can never fail.
- Bằng chứng: failopen_telegram_refresh_selfcheck.py:83 ok(f'_notify_failopen(p["label"], "{gate}"' in new, ...) runs before :93 ok(needle not in new or '_notify_failopen' in new, f'#1 bản MỚI vẫn còn print-only cho {needle!r}'). The second operand is guaranteed True, so an old print-only line left in bot_execute.py would not be caught.
- Hướng sửa đề xuất: Change it to ok(needle not in new, ...) (the new version must not keep the old print line).

## File đã đọc kỹ, không có vấn đề (18)
- /home/trido/thanhdt/WorkingClaude/auto_exit_rules.py
- /home/trido/thanhdt/WorkingClaude/cpi_vn.py
- /home/trido/thanhdt/WorkingClaude/cpi_vn_te_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/dcf_rate_display.py
- /home/trido/thanhdt/WorkingClaude/dcf_rate_display_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/dcf_rate_frame_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/dcf_refresh_gate.py
- /home/trido/thanhdt/WorkingClaude/dcf_rstar_refresh.py
- /home/trido/thanhdt/WorkingClaude/dcf_rstar_refresh_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/dcf_season_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/dcf_selector_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/dd_flag_order_gate_mutation.py
- /home/trido/thanhdt/WorkingClaude/dd_flag_order_gate_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/deploy_golive_dt5g_v4/golive_recommend_v23.py
- /home/trido/thanhdt/WorkingClaude/deposit_cctg_trend_check.py
- /home/trido/thanhdt/WorkingClaude/dna_report.py
- /home/trido/thanhdt/WorkingClaude/dna_report_liquidity_line_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/freshness_ops_selfcheck.py