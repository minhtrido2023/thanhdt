# Code quality weekly — 2026-11-22

File đã quét: 25 (nguồn manifest T0-T2, T0 xếp đầu; hot-core round-robin: /home/trido/thanhdt/WorkingClaude/trading_bot/brokers.py)
Finding: 5 (từ 5 trước verify)

## /home/trido/thanhdt/WorkingClaude/trading_bot/brokers.py:683 — correctness (medium)
- Owner đề xuất: Taylor
- DNSEBroker.get_max_buy_qty() and get_buying_power() catch every exception and return None. They do not call _log_raw and do not print anything. In the executor, an error from the ppse call then looks exactly like a real lack of cash.
- Bằng chứng: brokers.py:683-684 `except Exception:\n    return None` (same pattern at 701-702). _log_raw('ppse', ...) is only called on the success path (678, 696). Caller executor.py:2163-2167: `qmax = self.broker.get_max_buy_qty(...)`, then `if qmax is None or qmax < qty: self._journal("WAIT_CASH", ..., note="thiếu tiền — chờ lệnh bán khớp" + (... if qmax is not None else ""))`. When qmax is None the journal entry says only 'thiếu tiền', with no ppse error attached.
- Hướng sửa đề xuất: In the except branch, call self._log_raw('ppse_error', {symbol, price, loan_package_id_sent, error: f'{type(e).__name__}: {e}'}) and keep returning None (fail-safe unchanged). Optionally have the executor add '(ppse không đọc được)' to the WAIT_CASH note when qmax is None.
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/bull_div_boost.py:233 — bare-datetime-now (low)
- Owner đề xuất: Taylor
- get_current_max_positions() uses a bare datetime.today().date() to decide whether the boost window has expired. This function feeds max_positions in production (recommend_holistic.py:597).
- Bằng chứng: bull_div_boost.py:233 `today_d = datetime.today().date()` and line 75 `'date': str(datetime.today().date())`. The import at line 23 has no ZoneInfo. Caller: recommend_holistic.py:597 `from bull_div_boost import get_current_max_positions as _bull_mp`.
- Hướng sửa đề xuất: Replace with datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).date() at both places, 75 and 233 (or use today_ict() from trading_bot).

## /home/trido/thanhdt/WorkingClaude/daily_refresh_v34b_linux.sh:26 — bare-datetime-now (low)
- Owner đề xuất: Wags
- The log file name and START/DONE/ABORT timestamps use bare `date`, while the same script already uses TZ='Asia/Ho_Chi_Minh' date for TODAY_ICT (line 53) and for the alerts.
- Bằng chứng: line 26 `LOG="data/refresh_v34b_linux_$(date +%Y-%m-%d).log"`; lines 29, 32, 357 `$(date)`; line 196 `TS="$(date +%Y%m%d_%H%M%S)"`. Compare line 53 `TODAY_ICT="$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)"`. The script does not export TZ itself.
- Hướng sửa đề xuất: Add `export TZ=Asia/Ho_Chi_Minh` right after `source wc_env.sh`, the same pattern as orb_futures_run.sh:21 and ai_momentum_cron.sh:11.

## /home/trido/thanhdt/WorkingClaude/mike/bin/derivative_margin.py:87 — guideline:§29 (low)
- Owner đề xuất: Wags
- read_derivative_positions() swallows the exception and returns None. The fail-closed reason the caller gets cannot say why the read failed.
- Bằng chứng: derivative_margin.py:85-88 `try: r = client.positions(account_no, market_type="DERIVATIVE")\nexcept Exception:\n    return None`. The reason produced at line 78 is: 'đang có ký quỹ phái sinh ...đ nhưng KHÔNG đọc được vị thế DERIVATIVE'. Caller: daily_nav_snapshot.py:799.
- Hướng sửa đề xuất: Return or record the exception text (for example return None plus print to stderr f'{type(e).__name__}: {e}') and include it in the reason at line 78. Keep None/fail-closed unchanged.

## /home/trido/thanhdt/WorkingClaude/trading_bot/brokers.py:1291 — dead-code (low)
- Owner đề xuất: Taylor
- DNSEBroker.modify_order() has no callers in the canonical tree. It also contains a latent bug: the HTTP 500 quirk branch picks the live order with the highest id without filtering by symbol.
- Bằng chứng: `grep -rn modify_order --include=*.py --include=*.sh .` (excluding wt-*/archive/research/release_8l) finds only brokers.py:1291-1324 (its own definition), dnse_api.py:157 / phs_flex_api.py:194 (the client's own method), dnse_api_full_test.py:194 and phs_flex_api.py:24 (they call client.modify_order directly, not the broker), and intraday_price_watch_selfcheck.py:408 (a string in a blocklist). Lines 1320-1323: `candidates = [(int(k), k) for k, u in updates.items() if not u.is_dead and k != str(order_id)]` → `max(candidates)`.
- Hướng sửa đề xuất: Delete the method (no callers). If it is kept for later, filter candidates by the symbol of the old order (qget(u.raw,'symbol')) before taking max.

## File đã đọc kỹ, không có vấn đề (5)
- /home/trido/thanhdt/WorkingClaude/mike/bin/compute_active_nav.py
- /home/trido/thanhdt/WorkingClaude/mike/bin/dd_zone_candidates_block.py
- /home/trido/thanhdt/WorkingClaude/mike/bin/orb_futures_run.sh
- /home/trido/thanhdt/WorkingClaude/mike/bin/ai_momentum_cron.sh
- /home/trido/thanhdt/WorkingClaude/mike/bin/vnindex_total_return_selfcheck.py