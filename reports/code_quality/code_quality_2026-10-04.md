# Code quality weekly — 2026-10-04

File đã quét: 25 (nguồn FALLBACK diff 7 ngày (manifest HEAD lệch thực tế (production_manifest.py --check): DRIFT 30 dòng — manifest commit lệch thực tế. Nếu thay đổi là CỐ Ý: chạy `python3 mike/bin/production_manifest.py` rồi commit kb/production_manifest.{json,md}. + auto_exit_rules.py [T?] (mới vào production, từ mike/bin/auto_exit_inject.py) + cctg_rate_vn.py [T0] (mới vào production, từ mike/bin/ops_health_check.sh)); hot-core round-robin: /home/trido/thanhdt/WorkingClaude/bot_execute.py)
Finding: 12 (từ 12 trước verify)

## /home/trido/thanhdt/WorkingClaude/append_cctg_rate.py:161 — correctness (medium)
- Owner đề xuất: Taylor
- --force cannot replace a row whose effective_date is already in the CSV, even though the docs say it can. The 'not newer than last anchor' guard always exits first, so the --force row-replacement code at lines 239-240 can never run.
- Bằng chứng: L150: `if args.effective in existing and not args.force:` → SKIP is bypassed with --force; then L160-161: `last_date = existing_ev["time"].max().date()` / `if eff <= last_date: sys.exit(...)`. If args.effective is already a row, then eff <= max(time), so it always exits. L239-240: `if args.force: rows = [r for r in rows if r["effective_date"] != args.effective]` cannot be reached for an existing date. Help text L101: 'append even if effective_date exists'.
- Hướng sửa đề xuất: When --force is set and args.effective is already in `existing`, check against the max date of the rows that remain after removing that one (not the full max). Or remove the 'exists' wording from --force and delete the unreachable removal branch.
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/append_deposit_rate.py:317 — bare-datetime-now (medium)
- Owner đề xuất: Taylor
- The 'today' used by the JOB_ID gates is the bare `date.today()` (host TZ). That today drives --collected==today, the --effective window and source recency. The sibling append_cctg_rate.py was fixed with _ICT; this file was not.
- Bằng chứng: L317: `real_today = date.today().isoformat()` vs append_cctg_rate.py L117: `real_today = datetime.now(_ICT).date().isoformat()`. real_today is used at L324 (eff_age_days), L344 (`collected != real_today` → refuse agent), L390-399 (source age).
- Hướng sửa đề xuất: Replace with `datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date().isoformat()`, the same as append_cctg_rate.py. It still passes the tz_anchor_gate baseline because the ratchet only goes down.
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/bank_compounder_screen.py:132 — correctness (medium)
- Owner đề xuất: Taylor
- simulate() iterates only over months that had at least one qualifier. A month with 0 qualifiers is merged into the previous period: one row spans 2+ months, but metrics() still annualizes as len(r)/12. This distorts CAGR/Sharpe/MaxDD. Also, `months_zero`/`(cnt.n_qualify==0)` is always 0 because cnt is built from sel.groupby('d').
- Bằng chứng: L132: `rs = sorted(picks_map.keys())`; L135-136: `d_next = rs[i + 1]; entry, exit_ = next_session(d), next_session(d_next)` → holds through empty months; L161: `yrs = len(r) / 12.0`. L110-113: `for d, gg in sel.groupby("d"): ... counts.append((d, len(gg), len(top)))` → n_qualify>=1 always; L183/L286 report `months 0`/`months_zero` = 0 by construction. The docstring itself says '7-8 liquid names 2013-17', so empty months happen in practice. Compare aviation_screen.py, which iterates the full `rebal` grid + hold_cash_when_empty.
- Hướng sửa đề xuất: Iterate over the full `rebal` grid like aviation_screen.simulate (empty month → cash row net=0/-TC). Build cnt from the rebal grid with a 0 fill so months_zero means something.
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/compounder_screen.py:104 — correctness (medium)
- Owner đề xuất: Taylor
- Same bug as bank_compounder_screen: the NAV loop iterates `sorted(picks.keys())`, so months with no qualifier (or no prices) are absorbed into a multi-month holding period but counted as 1 period of 1/12 year. CAGR/Sharpe are wrong, and the 'months with <5' stat skips 0-qualifier months.
- Bằng chứng: L104: `rebal_sorted = sorted(picks.keys())`; L108-110: `d_next = rebal_sorted[i + 1]` … `exit_ = next_session(d_next)`; L142: `yrs = len(r) / 12.0`. cnt is built only from `sel.groupby("d")` (L80-84) → months with 0 qualifiers are missing from cnt.
- Hướng sửa đề xuất: Loop over `rebal` (all month-ends). Months with no picks hold cash (net=−TC×turnover), the same pattern as aviation_screen.simulate(hold_cash_when_empty=True).
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/capit_lever_selfcheck.py:340 — assert-on-live-state (medium)
- Owner đề xuất: Taylor
- The selfcheck asserts on a value of the PRODUCTION config, `data/trading_rules.json → capit_margin_lever.enabled is True` (A7 and again at G1 L1396), rather than an invariant. If the user turns the lever off (a legitimate kill-switch), the selfcheck goes red even though the code is correct. The comment at L335-339 admits the pin has already been flipped once (False→True) when the decision changed.
- Bằng chứng: L339-340: `check("A7 …và đang BẬT (enabled=true) — user duyệt 2026-08-22", real_pol["enabled"] is True, ...)`; L1394-1397: `real_blk = json.load(f)["capit_margin_lever"]` / `check("G1 ... enabled == true (user 2026-08-22)", real_blk["enabled"] is True ...)`. coding_guidelines_ext §23 hệ luận: assert on an invariant (relation/sign/fail-safe), not on a value.
- Hướng sửa đề xuất: Drop A7/G1 (keep the scope checks A6/G3, or move them to config-schema validation). The enabled/disabled state should be checked as an invariant: 'enabled=False ⇒ no order carries a loan package', which F5-F8 already cover.
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/cctg_deposit_wiring_selfcheck.py:195 — assert-on-live-state (low)
- Owner đề xuất: Taylor
- The selfcheck reads the real append-only CSVs (data/deposit_rate_vn_events.csv, data/cctg_rate_vn_events.csv) without isolating them, then asserts the exact production values: Big-4 = 6.8%, CCTG-minus-Big-4 spread = 0.70pp exactly, CCTG > Big-4. A valid new row with effective_date ≤ 2026-10-01 (agents may backdate up to 35 days) or a CCTG row on 2026-10-01 would turn it red even though the wiring code is unchanged.
- Bằng chứng: L194-195: `check("delta matches CCTG-vs-Big4 spread (0.70pp) exactly", abs((r_eff - r_big4) - 0.007) < 1e-9)`; L106: `"... (CCTG 7.5% beats Big-4 12M 6.8%)"`; L227: `abs(BIG4_AT - 6.8) < 1e-9`. grep: no monkeypatch of `_EVENTS_CSV` in this file (cctg_overlay_selfcheck.py does it with tmp CSVs). The live CSV just received a new row 2026-10-03.
- Hướng sửa đề xuất: Point dep._EVENTS_CSV/cctg._EVENTS_CSV at a tmp fixture CSV (like cctg_overlay_selfcheck), or assert the relation `r_eff - r_big4 == (cctg_rate - big4_rate)/100` computed from the same source instead of the hardcoded 0.007/6.8.

## /home/trido/thanhdt/WorkingClaude/cctg_rate_vn.py:126 — bare-datetime-now (low)
- Owner đề xuất: Taylor
- asof=None resolves to `pd.Timestamp.today()` (host TZ). The docstring says it must anchor to the real clock. tz_anchor_gate does not cover pd.Timestamp, so this slipped through. On a UTC host between 00:00 and 07:00 ICT, a row effective 'today' is not yet visible to current_cctg_rate().
- Bằng chứng: L126: `asof_ts = pd.Timestamp.today().normalize() if asof is None else pd.to_datetime(asof)`; caller with asof=None: append_cctg_rate.py L226/L264 `cctg_rate_vn.current_cctg_rate()`. §16 'CHƯA phủ: pd.Timestamp.now()'.
- Hướng sửa đề xuất: `pd.Timestamp.now(tz="Asia/Ho_Chi_Minh").tz_localize(None).normalize()`. Also fix the 3 identical spots in deposit_rate_vn.py (L195/280/306) in the same commit, so the two series do not drift apart.

## /home/trido/thanhdt/WorkingClaude/capit_episode.py:372 — bare-datetime-now (low)
- Owner đề xuất: Taylor
- The manual-close close_date and ledger updated_at use bare `datetime.now()`. On a host/cron without TZ between 00:00 and 07:00 ICT, close_date is recorded as the previous day in the CAPIT ledger.
- Bằng chứng: L372: `ep["close_date"] = datetime.now().strftime("%Y-%m-%d")`; L351: `ledger["updated_at"] = datetime.now().isoformat(timespec="seconds")`. kb/tz_anchor_baseline.json: `"capit_episode.py": 2` (old debt, not yet fixed).
- Hướng sửa đề xuất: Use `datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))` for both, then lower the baseline with `--update-baseline`.

## /home/trido/thanhdt/WorkingClaude/bot_execute.py:69 — correctness (low)
- Owner đề xuất: Taylor
- _notify_gdkhq_shadow puts try/except around the whole loop over 2 threads. If the first subprocess.run raises (TimeoutExpired after 20s, OSError), the second thread, _GDKHQ_DECISION_THREAD (where the user approves rollout), gets no notification at all.
- Bằng chứng: L69-74: `try:\n    for target in (_TRADING_DAILY_THREAD, _GDKHQ_DECISION_THREAD):\n        subprocess.run([script, message, target], timeout=20, check=False, ...)\nexcept Exception:\n    pass`
- Hướng sửa đề xuất: Move the try/except inside the for loop so each thread is best-effort on its own.

## /home/trido/thanhdt/WorkingClaude/bot_execute.py:209 — code-smell:Duplicated Code (low)
- Owner đề xuất: Taylor
- The atomic trace-write block (tmp → json.dump → fsync → os.replace) is copied verbatim twice in _run_gdkhq_shadow.
- Bằng chứng: L152-158 and L209-215 are identical: `tmp_path = trace_path + f".tmp.{os.getpid()}"` / `with open(tmp_path, "w", ...) as f: json.dump(trace, f, ...); f.write("\n"); f.flush(); os.fsync(f.fileno())` / `os.replace(tmp_path, trace_path)`.
- Hướng sửa đề xuất: Extract a local `_write_trace(trace, trace_path)` helper and call it at both places.

## /home/trido/thanhdt/WorkingClaude/alphalens_report.py:195 — duplicate-formula (low)
- Owner đề xuất: Taylor
- The Gordon justified-P/B formula with hardcoded COE=0.13/g=0.05 is copied by hand into at least 4 live files instead of imported from one place. Changing COE/g in one place (e.g. bank_compounder_screen.COE) leaves the others silently out of sync, and the EXIT ALERT in the daily report would fire on stale parameters.
- Bằng chứng: grep: alphalens_report.py:195 `just_pb = (roe5y - 0.05) / 0.08`; sector_strong_threshold.py:62 `just = (d["ROE5Y"] - 0.05) / 0.08`; sector_lens_monitor.py:168 `just = (roe5 - 0.05) / 0.08`; bank_compounder_screen.py:89 `(df.ROE5Y - GG) / (COE - GG)`.
- Hướng sửa đề xuất: Add one function `justified_pb(roe5y, coe=0.13, g=0.05)` (e.g. in alt_valuation_lens.py, which already documents it) and import it in the 3 live consumers.

## /home/trido/thanhdt/WorkingClaude/atc_cancel_overorder_selfcheck.py:64 — dead-code (low)
- Owner đề xuất: Taylor
- The function l_strip() is defined but never called.
- Bằng chứng: `grep -rn "l_strip" --include=*.py .` → only `def l_strip(s):` at atc_cancel_overorder_selfcheck.py:64 (plus identical copies of the same file in worktrees mike/agents/Taylor/wt-*), no call sites.
- Hướng sửa đề xuất: Delete the 2-line l_strip() function.

## File đã đọc kỹ, không có vấn đề (7)
- /home/trido/thanhdt/WorkingClaude/auto_exit_rules.py
- /home/trido/thanhdt/WorkingClaude/auto_exit_rules_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/aviation_screen.py
- /home/trido/thanhdt/WorkingClaude/bootstrap_nav.py
- /home/trido/thanhdt/WorkingClaude/brokers_tradequantity_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/close_repair.py
- /home/trido/thanhdt/WorkingClaude/concurrent_lock_selfcheck.py