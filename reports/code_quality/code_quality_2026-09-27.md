# Code quality weekly — 2026-09-27

File đã quét: 25 (nguồn manifest T0-T2, T0 xếp đầu; hot-core round-robin: /home/trido/thanhdt/WorkingClaude/trading_bot/plan_funding_gate.py)
Finding: 13 (từ 13 trước verify)

## /home/trido/thanhdt/WorkingClaude/mike/bin/discretionary_margin_gate.py:195 — correctness (high)
- Owner đề xuất: Wags
- current_price() unpacks 3 values from dnse_close_prices(with_source=True), which returns a 2-tuple — every call raises ValueError, so `check-exits` (kỷ luật thoát −20%) crashes the moment any margin arm is active.
- Bằng chứng: discretionary_margin_gate.py:195 `prices, sources, substituted = dnse_close_prices([ticker], with_source=True)`; verify_account_snapshot.py:533 `return (prices, sources) if with_source else prices`; compute_active_nav.py:317 correctly unpacks 2. cmd_check_exits():400 calls current_price() with no try/except. Reproduced offline with a stub returning the real 2-tuple shape: `current_price RAISES: ValueError not enough values to unpack (expected 3, got 2)`. Latent today only because data/discretionary_margin_arms.json has 0 active arms (cron log = 'Không có case ... active' ×20) and discretionary_margin_gate_selfcheck.py mocks `gate.current_price` entirely (lines 79/439/651/966/1059) so the real function is never exercised.
- Hướng sửa đề xuất: Change line 195 to `prices, sources = dnse_close_prices([ticker], with_source=True)` (drop `substituted`), and add one selfcheck case that calls the REAL current_price() with dnse_close_prices monkeypatched to the 2-tuple shape so the contract is pinned.
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/mike/bin/daily_nav_snapshot.py:953 — duplicate-formula (medium)
- Owner đề xuất: Wags
- NAV cash basis reads totalCash/totalDebt with only a hand-copied all-zero guard; the two other mandatory §25 guards (`_cash_fields_all_zero`, `_cash_fields_inconsistent`) from park_holdings are missing, so a feed that zeroes only the cash fields (depositInterest still non-zero) or returns totalCash<availableCash writes a wrong NAV row.
- Bằng chứng: daily_nav_snapshot.py:623-626 `_stock_all_zero` (local copy) and :953 `if _stock_all_zero(stock)` are the only guards before :962 `cash, debt = stock["totalCash"], stock["totalDebt"]`. park_holdings.py:148 docstring on the sibling guard: 'Điều kiện giống hệt daily_nav_snapshot.py:439 — nếu sửa một nơi, sửa cả hai (đã lệch 1 lần)'; park_holdings.py:158-161 and :183-187 document exactly the two failure shapes the missing guards catch (only cash fields zero; totalCash=0 while availableCash alive). coding_guidelines_ext §25 hệ quả 2: 'Tái dùng 3 guard, đừng viết lại ... bỏ bất kỳ cái nào là để hở đúng một lối'. grep confirms neither `_cash_fields_all_zero` nor `_cash_fields_inconsistent` appears in daily_nav_snapshot.py.
- Hướng sửa đề xuất: Import `_stock_block_all_zero, _cash_fields_all_zero, _cash_fields_inconsistent` from park_holdings (same dir, already on sys.path) and reject the balance record (return 2) if any of the three fires; delete the local `_stock_all_zero` copy or alias it to the imported one so the two files cannot drift again.
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/mike/bin/bq_freshness_check.sh:141 — guideline:§28 (medium)
- Owner đề xuất: Wags
- `_check` and `_check_lastmod` convert any bq command failure (auth/quota/network) into lag=999 and report it as 'bảng STALE' / 'WRITER-DEAD?', so a BQ access outage is diagnosed and escalated (Telegram + Discord + DollarBill block) as data staleness.
- Bằng chứng: bq_freshness_check.sh:141-144 `result=$(bq query ... 2>/dev/null | tail -1); lag_days="${result:-999}"; lag_days=$(printf "%.0f" "$lag_days" 2>/dev/null || echo 999)` then :156-157 alert text 'BQ STALE ... lag=999 ... Pipeline EOD có thể bị skip'. :172-178 same pattern → :185 'chưa được ghi 999d ... Publisher có thể đã chết'. bq writes errors to STDOUT (kb/incidents/2026-08/2026-08-29-bq-error-on-stdout-empty-diagnosis.md, cited in compute_active_nav.py:289), so `tail -1` of an error message yields a non-number → 999. §28: 'tách không tìm thấy bằng chứng khỏi tìm thấy và xấu'. Blocking is the right direction; the operator message points at the wrong cause.
- Hướng sửa đề xuất: In `_check`/`_check_lastmod`, capture bq rc separately (`result=$(bq ... 2>&1); rc=$?`); if rc≠0 or result is non-numeric, emit a distinct 'BQ QUERY FAILED: <first 200 chars>' alert (still FAILED=1 for BLOCK checks) instead of the lag=999 stale text.
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/mike/bin/discretionary_accumulation_inject.py:69 — bare-datetime-now (medium)
- Owner đề xuất: Wags
- plan_date for the injected DISCRETIONARY_SPECIAL order is derived from bare `dt.date.today()` (host TZ), and every ledger/plan/state timestamp from bare `datetime.now().astimezone()`, although `today_ict`/`now_ict` are already imported in the same file.
- Bằng chứng: discretionary_accumulation_inject.py:69 `return str(next_trading_day(dt.date.today()))` (used at :685 when --plan-date omitted); :466 `now_iso = dt.datetime.now().astimezone().isoformat(...)` written into plan notes (:488, :524, :591, :616), ledger (:632) and state (:571). :43 imports `now_ict, today_ict`; :45 defines `_ICT_TZ` and the file's own comment says '§16: neo TZ tường minh, không tin TZ của process'. Cron 20:30 ICT is safe by luck; a manual run under UTC between 00:00–07:00 ICT computes yesterday → next_trading_day = today → injects into today's plan. coding_guidelines §16.
- Hướng sửa đề xuất: Use `next_trading_day(today_ict())` at :69 and `now_ict()`/`dt.datetime.now(_ICT_TZ)` at :466; add the file to the §16 selfcheck run under `env -u TZ`.
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/mike/bin/check_report_cadence.sh:76 — correctness (medium)
- Owner đề xuất: Wags
- A corrupt/truncated `state/report_emailed.json` or `state/report_delivery_incomplete_alerted.json` makes the python one-liner fail, the variable becomes '' (not 'no'), and the delivery catch-up sweep / incomplete-alert is silently skipped for every report; both state files are also written non-atomically, which is how they get truncated.
- Bằng chứng: check_report_cadence.sh:76-81 `ALREADY="$(python3 -c "... json.load(open('$EMAILED_STATE')) ...")"; if [ "$ALREADY" = "no" ]` — on exception stdout is empty so the `= "no"` branch (the whole sweep) is skipped; same at :99-104 for ALREADY_ALERTED. Writes at :126-131 and :493-498 are `json.dump(state, open(..., 'w'))` (no tmp+os.replace). `set -uo pipefail` without `-e` so the script continues and prints 'OK — không có báo cáo ... quá hạn' at :429. Contrast vendor_mismatch_alert.sh:201-212 in the same fleet: 'State hỏng/cụt KHÔNG được làm câm cảnh báo ... coi như CHƯA cảnh báo (fail-open về phía GỬI) và in LỖI THẬT (§29)' and atomic write at :256-282.
- Hướng sửa đề xuất: Treat unreadable state as 'no' (fail-open toward sweeping/alerting) with the real error on stderr, and write both state files via tmp+os.replace as vendor_mismatch_alert.sh already does; pass FNAME/TODAY via env instead of interpolating into the python source.
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/mike/bin/dividend_adjusted_return.py:147 — guideline:§7 (medium)
- Owner đề xuất: Wags
- Live account numbers are hardcoded (`ACCOUNTS = {SpaceX, ZaloPay}`) instead of read from trading_bot_accounts.json; enabling a third account (RocketX already exists in the file) adds no equation to the broker solver and report_return_gate silently never labels its reports.
- Bằng chứng: dividend_adjusted_return.py:147 `ACCOUNTS = {"SpaceX": "0002023347", "ZaloPay": "0001743768"}`; consumed at :994 (`resolve_dividends` default), :1144, and by report_return_gate.py:375 `labels = [lb for lb in dar.ACCOUNTS if lb in name]` and :540 `acct = dar.ACCOUNTS[lb]`. secrets/trading_bot_accounts.json currently lists RocketX (live, enabled=false, account_id 0002023348). config.py:359-366 docstring: 'Thêm account mới ... tự động được các script này nhận, KHÔNG cần sửa code/cron riêng (xem kb/account_onboarding_runbook.md)'; report_return_gate.py:360 cites the same rule ('Đọc từ config, KHÔNG hardcode (§7)'). Also :146/:565 absolute canonical paths instead of wc_paths.
- Hướng sửa đề xuất: Build ACCOUNTS from `trading_bot.config.load_accounts()` (label→account_id for enabled live accounts) with the current dict kept only as offline-selfcheck fixture; derive EXEC_LOG_DIR/_CORP_ACTIONS_PATH from wc_paths like sibling scripts.
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/trading_bot/brokers.py:579 — guideline:§25 (medium)
- Owner đề xuất: Taylor
- DNSEBroker.get_cash() (the 'TIÊU ĐƯỢC NGAY' field used by executor WAIT_CASH and the funding-gate fallback bound) falls through a qget alias chain that ends in `totalcash`/`cash`/`balance`, so if DNSE ever omits/renames availableCash the buying-power check silently switches to the 'SỞ HỮU' number and loosens the money gate.
- Bằng chứng: brokers.py:579-581 `v = _fnum(qget(row, "availablecash", "withdrawablecash", "purchasingpower", "cashavailable", "totalcash", "cash", "balance", default=0))`; qget (:84-93) returns the first key that is not None/''. coding_guidelines_ext §25 hệ quả 1: 'Fail-closed, KHÔNG rơi về ... Rơi về = tái lập đúng bug vừa sửa, lặng lẽ'; §25 table: totalCash includes unsettled sale proceeds + receivable dividends (SpaceX 08-07: availableCash 4.82M vs totalCash 203.66M). Consumers: plan_funding_gate.py:417 fallback bound `cash = float(broker.get_cash() or 0.0)`, executor WAIT_CASH (per plan_funding_gate docstring :21).
- Hướng sửa đề xuất: Read only the availableCash family (`availablecash`, `withdrawablecash`) and return None/raise when absent so callers fail-closed; keep `purchasingpower`/`totalcash`/`balance` out of this chain (they answer a different §25 question).
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/mike/bin/compute_active_nav.py:522 — correctness (medium)
- Owner đề xuất: Wags
- When a ticker has no price from DNSE and the BQ fallback also fails, the position is dropped from total_mv with only a '⚠️' warning and rc=0, so active_nav (the sizing denominator) is written understated and the file is treated as fresh by every consumer.
- Bằng chứng: compute_active_nav.py:318-327: on DNSE miss, `bq_px, err = bq_close_prices(missing)`; if `bq_px` is None nothing is added and no exit; :522-525 `if px is None: print("⚠️ Thiếu giá cho {tk} — bỏ qua khỏi tổng ..."); continue`; :620-627 then writes the canonical file. The file's own [F1] note at :355-360 says cron_health_check.py only matches `^\s*❌`, so a ⚠️-only path is 'MÙ HẲN'. park_holdings.resolve_close_prices (:220-224, :248-253) treats the identical situation as fail-closed for the same reason ('mẫu số cấp tài khoản').
- Hướng sửa đề xuất: If any held ticker still lacks a price after the BQ fallback, print a ❌ line and `sys.exit(3)` without writing (same pattern as rc=4/5/6), so consumers fall back to nav_history instead of a silently smaller active_nav.
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/trading_bot/brokers.py:584 — guideline:§25 (low)
- Owner đề xuất: Taylor
- `_cash_totalcash_minus_debt` re-implements the NAV cash basis with 2 of the 3 mandatory guards — the totalCash<availableCash invariant is missing, so a feed returning totalCash=0/totalDebt=0/availableCash>0 yields cash=0 instead of None.
- Bằng chứng: brokers.py:596-603 checks `tc is None or td is None` and `tc == 0 and td == 0 and (av is None or av == 0)` only; compute_active_nav.cash_basis (:162-173) applies all three via park_holdings. Caller trading_bot/plan.py:1975-1977 uses the value as nav_live for lever preflight (direction fail-safe: strips leverage). §25 hệ quả 2 requires all three guards. Cross-repo import boundary is the documented reason for the copy (cf. plan_funding_gate.py:118-120 FEE_RATE), so a sync selfcheck is the practical fix.
- Hướng sửa đề xuất: Add `if av is not None and tc < av: return None` and cover the three shapes in a broker selfcheck (or a sync-check against park_holdings guards like plan_funding_gate_fee_sync_selfcheck.py does for FEE_RATE).

## /home/trido/thanhdt/WorkingClaude/mike/bin/verify_account_snapshot.py:810 — bare-datetime-now (low)
- Owner đề xuất: Wags
- The 'is asof today → use DNSE live prices' switch uses bare `_dt.date.today()` while the same file anchors today with ZoneInfo 6 lines away in dnse_close_prices(); under a UTC process between 00:00–07:00 ICT the switch is false and BQ (T-1, unadjusted) prices are used for a same-day snapshot.
- Bằng chứng: verify_account_snapshot.py:810 `if tickers and args.asof == _dt.date.today().isoformat():` vs :503 `today = _dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date().isoformat()   # §16`. tz_anchor_gate.py:4 states it blocks `date.today()` (ratchet baseline, so this is old debt but still a live §16 violation on the report-verification path).
- Hướng sửa đề xuất: Compute `today` once via `datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date()` in main() and reuse it at :810.

## /home/trido/thanhdt/WorkingClaude/bot_execute.py:334 — simplification (low)
- Owner đề xuất: Taylor
- `_log_plan_buying_power_shadow` still runs every session although its stated purpose (accumulate ≥10 sessions before promoting to a real gate) was fulfilled on 2026-08-04; it adds one naive ppse call per account per start and writes rows whose `would_block` is known-wrong (single default loan package, no JIT credit), 55/77 rows say true while the real gate lets the plan through.
- Bằng chứng: bot_execute.py:335-340 docstring: 'Mục đích duy nhất: tích luỹ dữ liệu để Mike/user quyết có nên nâng thành gate thật hay không ... ≥10 phiên trước khi bàn ACTIVE'; plan_funding_gate.py:3 '✅ ĐÃ WIRE VÀO PRODUCTION 2026-08-04', :40-48 explains the shadow's default-package measurement is the FALSE-POSITIVE source. data/plan_buying_power_shadow_log.csv: 77 rows, `grep -c ',true$'` = 55; last rows 2026-09-18 ZaloPay 18.93M vs 8.12M → would_block=true. grep: no script consumes the CSV besides plan_buying_power_shadow_replay.py and capit_lever_selfcheck.py (which references the constant only). coding_guidelines §2/§3.
- Hướng sửa đề xuất: Either remove the shadow call at :739 (and the helper) now that check_plan_funding is the gate, or make it log the gate's own verdict (`fund` dict) instead of an independent naive ppse measurement; update capit_lever_selfcheck if it imports the constant.

## /home/trido/thanhdt/WorkingClaude/trading_bot/plan_funding_gate.py:452 — dead-code (low)
- Owner đề xuất: Taylor
- `funding_block_reason()` has no production caller (only its own selfcheck) and, because it cannot pass `execution_state`, any future caller would double-count already-filled/open-child quantities on resume — the exact 2026-08-11/2026-09-17 bug class the state path was added to fix.
- Bằng chứng: grep -rn funding_block_reason (excluding worktrees/archive): trading_bot/plan_funding_gate.py:452 (def) and plan_funding_gate_selfcheck.py:33/126/136/216 only; bot_execute.py:755 calls `check_plan_funding(plan, broker, cfg["mode"], execution_state=execution_state)` directly. :454 `v = check_plan_funding(plan, broker, account_mode)` drops execution_state; docstring :245-258 explains why omitting state re-counts open-child reservations.
- Hướng sửa đề xuất: Delete the wrapper and its 3 selfcheck cases, or add `execution_state=None` passthrough and a docstring line saying callers on the resume path must supply it.

## /home/trido/thanhdt/WorkingClaude/mike/bin/daily_nav_snapshot.py:200 — duplicate-formula (low)
- Owner đề xuất: Wags
- corp_actions.json is parsed three ways in one file: `confirmed_qty_multiplier_after` was switched to `corp_actions.load_corp_actions()` precisely because raw parsing with `except (TypeError, ValueError): continue` swallowed malformed records, but `classify_raw_price_gap` and `confirmed_share_event_multiplier` still use that raw pattern.
- Bằng chứng: daily_nav_snapshot.py:69-81 docstring: 'bản cũ tự đọc raw JSON + except (TypeError, ValueError): pass ... bị NUỐT IM LẶNG ... Sửa: tái dùng corp_actions.load_corp_actions()'. Yet :200-217 and :388-409 still do `json.load(...).get("actions")`, `str(a.get("ex_date"))[:10] <= date` (raw string compare) and `except (TypeError, ValueError): continue`. Failure direction is fail-closed (falls to 'unexplained' → rc=4/5), so severity low, but the two readers can disagree with the validated one on the same record.
- Hướng sửa đề xuất: Route both helpers through `corp_actions.load_corp_actions(path=CORP_ACTIONS_FILE, ticker=...)` (accepting the `actions=` fixture param as a list of validated dicts) so one validator governs all three readers.

## File đã đọc kỹ, không có vấn đề (14)
- /home/trido/thanhdt/WorkingClaude/mike/bin/append_event.sh
- /home/trido/thanhdt/WorkingClaude/mike/bin/compute_jit_unpark.py
- /home/trido/thanhdt/WorkingClaude/mike/bin/compute_park_trim.py
- /home/trido/thanhdt/WorkingClaude/mike/bin/corp_action_auto_confirm.py
- /home/trido/thanhdt/WorkingClaude/mike/bin/corp_actions.py
- /home/trido/thanhdt/WorkingClaude/mike/bin/eod_trading_report.sh
- /home/trido/thanhdt/WorkingClaude/mike/bin/exdate_frame.py
- /home/trido/thanhdt/WorkingClaude/mike/bin/json_payload_diag.py
- /home/trido/thanhdt/WorkingClaude/mike/bin/nav_exdate_forecast.py
- /home/trido/thanhdt/WorkingClaude/mike/bin/park_holdings.py
- /home/trido/thanhdt/WorkingClaude/mike/bin/plan_approval_reminder.sh
- /home/trido/thanhdt/WorkingClaude/mike/bin/report_return_gate.py
- /home/trido/thanhdt/WorkingClaude/mike/bin/vendor_mismatch_alert.sh
- /home/trido/thanhdt/WorkingClaude/trading_bot/config.py