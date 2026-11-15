# Code quality weekly — 2026-11-15

File đã quét: 25 (nguồn manifest T0-T2, T0 xếp đầu; hot-core round-robin: /home/trido/thanhdt/WorkingClaude/trading_bot/executor.py)
Finding: 6 (từ 6 trước verify)

## /home/trido/thanhdt/WorkingClaude/trading_bot/executor.py:2687 — correctness (medium)
- Owner đề xuất: Taylor
- The fill-lagging check sums p.get('qty', 0) over state['parents'], but parent state never has a 'qty' key. So total_plan is always 0, fill_rate falls back to 1.0, and the 11:00 'fill_lagging' bus warning can never fire.
- Bằng chứng: executor.py:2687-2689: `total_plan = sum(p.get("qty", 0) for p in ps.values())` / `fill_rate = total_fill / total_plan if total_plan else 1.0`. Parent dicts are only built at :355-358 and :366-368 with keys filled/done/atc_sent/children/last_slice_ts/dcf_check (no qty). Real state file data/execution_logs/exec_*_state.json has parent keys ['filled','done','atc_sent','children','last_slice_ts','dcf_check','place_fail_streak','place_fail_note']. `grep -rh fill_lagging mike/bus | wc -l` = 0: the event has never been published since 204b3826d added it. mike/bin/run_bot.sh:12 still lists fill_lagging as one of the bot's alerts.
- Hướng sửa đề xuất: Compute the planned quantity from the plan instead of the state: total_plan = sum(o.qty for o in e.plan.orders) and total_fill = sum(e.state['parents'][o.id]['filled'] for o in e.plan.orders). Add a selfcheck where 30% filled at 11:00 must emit fill_lagging (use MIKE_BOT_TEST_EVENT_SINK).
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/bull_div_boost.py:45 — correctness (medium)
- Owner đề xuất: Taylor
- _q() calls subprocess.run with an argument list plus shell=True. On Linux/POSIX only the first item ('bq') runs as the command and the other items (including the SQL) are dropped, so detect_today() never runs its query and the BullDvg boost can never fire.
- Bằng chứng: bull_div_boost.py:42-45: `cmd = ['bq', 'query', '--use_legacy_sql=false', ..., '-q', sql]` / `subprocess.run(cmd, capture_output=True, text=True, shell=True)`. Read-only repro of the semantics: `subprocess.run(['echo','SHOULD_PRINT'], shell=True, capture_output=True, text=True).stdout` = '\n' (the second argument is dropped). Effect: bull_div_boost_state.json = {fire_history: [], current_window: null}, data/bull_div_boost_log.csv last row is 2026-06-15 (mtime Jun 15). The consumer recommend_holistic.py:597-598 (`from bull_div_boost import get_current_max_positions`) therefore always gets MAX_POS_NORMAL=12. This pattern only worked on the old Windows machine.
- Hướng sửa đề xuất: Drop shell=True (keep the list), and set PATH/CLOUDSDK_CONFIG via env like corp_action_lib.bq does. Or call corp_action_lib.bq directly instead of keeping a separate bq wrapper.
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/bull_div_boost.py:233 — bare-datetime-now (low)
- Owner đề xuất: Taylor
- datetime.today() is used without anchoring to ICT, both for the boost-window expiry check and for the error-path date.
- Bằng chứng: bull_div_boost.py:233 `today_d = datetime.today().date()` (cal_days = today_d - fire_d decides whether MAX_POS_BOOSTED still applies). :75 `return {'date': str(datetime.today().date()), 'error': 'no_data'}`. When cron runs under TZ=UTC between 00:00 and 07:00 ICT, today_d is the previous day, so the window lasts one day longer than HOLD_DAYS*1.4 calendar days (guidelines §16).
- Hướng sửa đề xuất: Use datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).date() at both places (or today_ict() from trading_bot.vn_market).

## /home/trido/thanhdt/WorkingClaude/trading_bot/executor.py:2508 — correctness (low)
- Owner đề xuất: Taylor
- write_report labels the column 'avg fill px' and computes the 'Executed' total from the child order's limit price c['price'], not the broker's actual fill price. For ATC children (price=None) it falls back to o.ref_price.
- Bằng chứng: executor.py:2508-2510: `avg = (sum(c["filled"] * (c["price"] or o.ref_price) for c in fills) / ...)` / `tot_fill += ps["filled"] * (avg or o.ref_price)`. _sync_fills :1299-1300 receives u.avg_price but only writes it to the journal, never into the child state. ATC children are created with "price": None at :2359. A buy filled below its limit, or any ATC fill, shows a wrong 'avg fill px' and 'Executed' value in exec_*_report.md and in the FLEET line at :2735 (guidelines §6/§27: placed price is not fill price).
- Hướng sửa đề xuất: In _sync_fills, store c['avg_price'] = u.avg_price when the broker returns it, and have write_report prefer c.get('avg_price') over c['price']. Or rename the column to 'avg limit px' if this report is only meant to show placed prices.

## /home/trido/thanhdt/WorkingClaude/capit_episode.py:210 — perf (low)
- Owner đề xuất: Taylor
- _refresh_evidence calls _filled_qty once per (account, session, ticker, side), and each call re-opens and JSON-parses the whole dnse_raw_<date>.jsonl file (1–3.4 MB/day) just to read the last 'orders' snapshot.
- Bằng chứng: capit_episode.py:204-212: `for lb in labels: for d in days: for (tk, side), q in _plan_capit_orders(...).items(): ... fq = _filled_qty(workdir, lb, d, tk, side)`. _filled_qty :145 → _raw_records :104-114 reads and json.loads every line of the file on each call. Measured: dnse_raw_2026-11-11.jsonl = 3.3 MB, 2026-11-12 = 3.45 MB. An open episode with 60 sessions × 5 tickers × 2 accounts means about 600 full parses of 1–3 MB files on each golive run (episode is currently closed, so this is latent).
- Hướng sửa đề xuất: Cache the last 'orders' snapshot per (date, label) inside _refresh_evidence (read each file once), then look up tk/side from that cache.

## /home/trido/thanhdt/WorkingClaude/cpi_vn.py:367 — correctness (low)
- Owner đề xuất: Taylor
- cpi_monthly_df() and merge_cpi() default to end='2026-06-01'. Any caller that omits end gets a CPI series cut off at 2026-06, and merge_asof backward silently forward-fills that old value onto every later date.
- Bằng chứng: cpi_vn.py:322 `def cpi_monthly_df(end="2026-06-01")`, :367 `def merge_cpi(df, time_col="time", end="2026-06-01", pit=True)`. Live caller without end: macro_confidence_regime.py:45 `df = merge_cpi(df)` (research/display), so every day after 2026-07 gets CPI frozen at 2026-05 (after the pit +1-month shift). The same hardcoded-end class was already fixed in dcf_valuation.py:401-404 (comment 'cq-2026-11-08 #4: end = đầu tháng của asof (không hardcode ...)'), but the default in cpi_vn itself is still stale.
- Hướng sửa đề xuất: Make the default end=None and resolve it to the first day of the current ICT month inside the function (same as dcf_valuation.py:404). Or require end with no default so callers cannot forget it.

## File đã đọc kỹ, không có vấn đề (15)
- /home/trido/thanhdt/WorkingClaude/alt_valuation_lens.py
- /home/trido/thanhdt/WorkingClaude/anomaly_gate.py
- /home/trido/thanhdt/WorkingClaude/auto_exit_rules.py
- /home/trido/thanhdt/WorkingClaude/bot_execute.py
- /home/trido/thanhdt/WorkingClaude/bq_local_cache.py
- /home/trido/thanhdt/WorkingClaude/cctg_rate_vn.py
- /home/trido/thanhdt/WorkingClaude/close_repair.py
- /home/trido/thanhdt/WorkingClaude/corp_action_lib.py
- /home/trido/thanhdt/WorkingClaude/custom30.py
- /home/trido/thanhdt/WorkingClaude/dcf_rate_display.py
- /home/trido/thanhdt/WorkingClaude/dcf_rstar_refresh.py
- /home/trido/thanhdt/WorkingClaude/dnse_api.py
- /home/trido/thanhdt/WorkingClaude/dt5g_freshness.py
- /home/trido/thanhdt/WorkingClaude/fetch_dnse_khoplenh_email.py
- /home/trido/thanhdt/WorkingClaude/gdp_growth_vn.py