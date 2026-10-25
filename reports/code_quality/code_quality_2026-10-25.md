# Code quality weekly — 2026-10-25

File đã quét: 25 (nguồn FALLBACK diff 7 ngày (manifest HEAD lệch thực tế (production_manifest.py --check): DRIFT 5 dòng — manifest commit lệch thực tế. Nếu thay đổi là CỐ Ý: chạy `python3 mike/bin/production_manifest.py` rồi commit kb/production_manifest.{json,md}. + mike/bin/egg_transfer_alert.py [T?] (mới vào production, từ (root)) + gốc ('cron', '*/15 2-6 * * 1-5', 'egg_transfer_alert.py', 'T?')); hot-core round-robin: /home/trido/thanhdt/WorkingClaude/mike/bin/wags_autofix.sh)
Finding: 17 (từ 17 trước verify)

## /home/trido/thanhdt/WorkingClaude/mike/bin/wags_autofix.sh:343 — correctness (medium)
- Owner đề xuất: Wags
- Two steps of the pipeline (risk-tier and arch-review) can pick up a STALE finding from an earlier round of the same label. Both scan the whole of Wags.jsonl by substring and take the newest match, without filtering on DISPATCH_START_ISO. So when this round's Wags writes no new finding (the 🟡 branch, dispatch_rc=0), the pipeline still reports ✅ HOÀN TẤT for the old fix.
- Bằng chứng: _arch_review (l.55-63): `for ln in open(inbox): ... if sub and sub.lower() not in (topic+json.dumps(payload)).lower(): continue; pick = e` (no ts filter). wags_risk_tier.py:57-62 is identical (`blob = topic + json.dumps(payload); if substr not in blob: continue; pick = e`). Meanwhile wags_bus_verdict.py:45 DOES filter `ts < since_iso`. The comment at l.314 assumes 'fail-safe mặc định high nếu không tìm thấy', but it does find the old finding. The label is `coord-${TODAY}` (ops_health_check.sh:2262), which runs several times a day, so a second round after the 1h cooldown has the same label.
- Hướng sửa đề xuất: Pass DISPATCH_START_ISO into _arch_review and wags_risk_tier.py and only accept findings with ts >= that mark. In the 🟡 branch (no new finding), skip risk-tier/arch-review and post the inconclusive question instead of reviewing the old finding.
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/mike/bin/bq_freshness_check.sh:1012 — correctness (medium)
- Owner đề xuất: Wags
- The dispatch prompt tells DollarBill to write the plan to data/plan_<ACCT>_<date>.json, but the canonical path is data/trade_plans/. DollarBill has actually followed the wrong path, so at the 19:0x round auto_exit_inject, the morning-skip check and bot_execute do not see the plan.
- Bằng chứng: Prompt: "Ghi plan vào data/plan_${ACCT}_${NEXT_TRADING_DAY}.json". The same file at l.937 checks `$WORKDIR/data/trade_plans/plan_${ACCT}_...`; auto_exit_inject.PLAN_DIR = data/trade_plans; DollarBill CLAUDE.md:86 = data/trade_plans/. On disk: data/plan_ZaloPay_2026-10-23.json (mtime 2026-10-22 19:05:10, 5381B) while data/trade_plans/plan_ZaloPay_2026-10-23.json only appeared at 23:30:05 with different content; same for data/plan_ZaloPay_2026-10-14.json (19:03 vs 23:30).
- Hướng sửa đề xuất: Change the prompt to data/trade_plans/plan_${ACCT}_${NEXT_TRADING_DAY}.json to match l.937, PLAN_DIR and DollarBill's CLAUDE.md.
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/mike/bin/auto_exit_inject.py:567 — correctness (medium)
- Owner đề xuất: Wags
- The CAPIT T+60 exit sells the WHOLE broker position for the ticker (pos['qty']) instead of only the CAPIT portion. If a ticker sits in several books (CAPIT plus LAG/BAL/PARK), the injected SELL also includes the other books' shares. That is exactly the error LAG/BAL already fixed by using book_lot_snapshot.
- Bằng chứng: l.567 `qty = int(pos["qty"])` (CAPIT). By contrast _lag_bal_candidates docstring l.92-95: '`lots` ... ĐÃ TÁCH ĐÚNG phần thuộc `book` ... KHÔNG phải tổng vị thế broker ... tổng broker sẽ CHO QUA sai số lượng, bán khống cả phần book khác'. portfolio_status.book_lot_snapshot docstring cites the real mixed-book case VPB (LAG 700 + PARK 1.100). _cap_sellable only caps by tradeQuantity, not by book.
- Hướng sửa đề xuất: Use min(planned_qty from qty_per_account, pos['qty']), or book_lot_snapshot(account, 'CAPIT') if park_holdings tracks the CAPIT book, so the order sells only the CAPIT lot.
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/cpi_vn.py:269 — correctness (medium)
- Owner đề xuất: Taylor
- merge_cpi labels month M's CPI as M-01 and merges backward, so a day early in month M sees M's own CPI, which GSO only publishes at the end of M or early M+1 (look-ahead). The bug was found and fixed only LOCALLY in a research script; the shared module still has it. Consumers: macro_confidence_regime.py:45 and golive_recommend_v23.py:1003 (the CAPIT lever 'PIT' gate).
- Bằng chứng: cpi_vn.py:274 `pd.merge_asof(d, cpi, left_on=time_col, right_on="time", direction="backward")` on monthly keys `YYYY-MM-01`. mike/agents/Taylor/research/pit_filter_full_2007_2026_test.py:12-27 merge_cpi_pit: '[FIX 2026-08-25, quant-skeptic look-ahead finding] cpi_vn.merge_cpi() tags month M's CPI at timestamp M-01 ... a trading day early in month M (e.g. 2011-05-05) would incorrectly see May's own CPI' → shifts +1 month. grep: macro_confidence_regime.py:45 `df = merge_cpi(df)`; golive_recommend_v23.py:1003 `cpi_vn.merge_cpi(_pit_q, ...)`.
- Hướng sửa đề xuất: Shift the CPI series +1 month in merge_cpi (as merge_pit does) or add a PIT parameter that defaults on. Then re-measure macro_confidence_regime and the PIT gate on history. Live is barely affected because of the max(…, last NSO) fallback.
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/mike/bin/compute_active_nav.py:556 — duplicate-formula (medium)
- Owner đề xuất: Wags
- The §25 NAV formula (totalCash − totalDebt + egg.totalValue + offbook + stock) is hand-copied into at least 4 consumers with no shared function. This is exactly the 'công thức lặp lại' class of hidden core in §23/§25 (the 08-19 egg incident).
- Bằng chứng: compute_active_nav.py:556 `total_nav = cash + total_mv + egg_value + offbook` (cash=totalCash−totalDebt, l.176); daily_nav_snapshot.py:1807 `nav = mtm_stock + cash - debt + offbook + egg_value`; cash_identity.py:255 `row["k"] = cash + cum_div_excl - debt + offbook + egg`; compute_park_trim.py:17 `pool = (totalCash − totalDebt) + egg_assets + park_mv`. The files already differ: nav_history `cash` has already had cum_dividend_excl subtracted, while active_nav `cash` still includes it (handled only with a double-count warning at l.603-611).
- Hướng sửa đề xuất: Extract one helper (e.g. owned_cash(stock_block, egg, offbook)) into a shared module and have all 4 consumers call it, keeping each consumer's own cum-dividend adjustment explicit.
- Đã qua verify độc lập: sống sót phản biện.

## /home/trido/thanhdt/WorkingClaude/mike/bin/check_report_cadence.sh:269 — correctness (low)
- Owner đề xuất: Wags
- The heredoc reads STATE with a bare json.load and no try. If state/report_cadence_dispatched.json is corrupt, the whole overdue-report detector and auto-close silently die while cron still exits 0. The writer at l.595-604 explicitly handles a corrupt state ('state cũ hỏng — dựng lại từ {}'), but the reader does not.
- Bằng chứng: l.269 `state = json.load(open(state_path))`. A traceback leaves PLAN empty → l.513 `N=$(... json.load ...)` fails → `[ "$N" -eq 0 ]` errors → the while loop gets no input → the script ends rc=0. The comment at l.592-594 admits 'state cụt do bị kill giữa chừng từng làm ALREADY/ALREADY_ALERTED phía trên vấp; STATE này bị đọc lại bởi mọi lượt cron sau nên cùng rủi ro'.
- Hướng sửa đề xuất: Wrap that json.load in try/except: fall back to {} and print the real error to stderr, same pattern as l.596-604. Also make the script exit non-zero when PLAN is empty or not JSON.

## /home/trido/thanhdt/WorkingClaude/mike/bin/bq_freshness_check.sh:420 — guideline:§28 (low)
- Owner đề xuất: Wags
- The ticker_prune depth check folds 'BQ query failed' into 'table gutted'. Any bq error (auth/quota/network) gives prune_names=0 or garbage, and the alert says 'bảng bị ghi thiếu/moi ruột'. _check right above was deliberately fixed to separate the two cases.
- Bằng chứng: l.420-424 `prune_names=$(bq query ... 2>/dev/null | tail -1 | tr -d '[:space:]'); prune_names="${prune_names:-0}"` → l.428 'ticker_prune ngày mới nhất chỉ có ${prune_names} mã ... bảng bị ghi thiếu/moi ruột'. Compare l.170-188: '§28: tách "không tìm thấy bằng chứng" khỏi "tìm thấy và xấu"'.
- Hướng sửa đề xuất: Capture bq's rc and full output the way _check does. If rc≠0 or the value is not an integer, send a separate 'BQ QUERY FAILED' message instead of the gutted-table message.

## /home/trido/thanhdt/WorkingClaude/mike/bin/bq_freshness_check.sh:1001 — correctness (low)
- Owner đề xuất: Wags
- The CAPIT_NOTE sent to DollarBill states 'hệ thống KHÔNG có luật tự bán CAPIT ở đường live'. Since 2026-09-30, auto_exit_inject.py injects CAPIT T+60 SELL orders into the draft plan, so DollarBill's plan summary can tell the user something wrong.
- Bằng chứng: l.1001: '... exit CAPIT do NGƯỜI quyết định, hệ thống KHÔNG có luật tự bán CAPIT ở đường live.' auto_exit_inject.py:552-581: '---- CAPIT: T+60 cố định ... _inject_sell(plan, ..., "CAPIT", "CAPIT_AUTO_EXIT", ...)' plus a bus reminder at T+55.
- Hướng sửa đề xuất: Reword that sentence: DollarBill itself should not create CAPIT SELLs, but auto_exit_inject will add a T+60 SELL proposal to the draft for the user to approve.

## /home/trido/thanhdt/WorkingClaude/mike/bin/arch_noise_gate.py:262 — correctness (low)
- Owner đề xuất: Wags
- The daily digest labels every wags_lifecycle record 'arch-review CONFIRMED', but the 'HOÀN TẤT issue' regex also catches LOW-RISK messages, which by definition SKIP arch-reviewer. The digest therefore claims an audit that never happened.
- Bằng chứng: ROUTINE l.121 `re.compile(r"\[wags-autofix\] HOÀN TẤT issue")`; wags_autofix.sh:349 '✅ **[wags-autofix] HOÀN TẤT issue ...** (LOW-RISK — ... bỏ qua arch-reviewer đầy đủ ...)'; build_digest l.262 `f"... {done} hoàn tất / {len(issues)} issue (...), arch-review CONFIRMED"`.
- Hướng sửa đề xuất: Count 'LOW-RISK' and 'CONFIRMED' separately in build_digest (e.g. 'N hoàn tất: x arch-review CONFIRMED, y low-risk bỏ qua review').

## /home/trido/thanhdt/WorkingClaude/bot_execute.py:734 — correctness (low)
- Owner đề xuất: Taylor
- The docstrings of _alert_recon_failure and _reconcile_net_fills promise that the caller sets a non-zero exit when netting recon fails, but main() keeps the exit code unchanged (rc=0). The comment right at the call site contradicts them, so anyone relying on the docstring to monitor exit codes will miss the failure.
- Bằng chứng: l.302 'caller đặt exit ≠ 0 để giám sát bắt'; l.326 'Trả list label có failures (caller đặt exit ≠ 0)'; but l.732-737 'Không đổi exit-code ...' and l.735-746 only print, then return 0 unless approval/funding was blocked.
- Hướng sửa đề xuất: Decide on one behaviour. Either fix both docstrings to say the exit code does not change (monitoring relies on the bus error NETTING_RECON_FAIL), or actually return a separate non-zero code.

## /home/trido/thanhdt/WorkingClaude/deploy_golive_dt5g_v4/golive_recommend_v23.py:1331 — guideline:§5 (low)
- Owner đề xuất: Taylor
- The canonical artifact data/golive_v23_status.json (read by bq_freshness_check, the telegram report and DollarBill) is written in place with no tmp+os.replace. A kill mid-write leaves truncated JSON, and bq_freshness_check l.977-993 swallows the error and treats it as 'no CAPIT', silently dropping the CAPIT note.
- Bằng chứng: l.1331-1332 `with open(os.path.join(WORKDIR, "data", "golive_v23_status.json"), "w", ...) as f: json.dump(status, f, ...)`; CSV l.1236 and MD l.1529 are also written directly. Compare compute_active_nav.py:640-656 citing '§5 coding_guidelines — ghi nguyên tử'.
- Hướng sửa đề xuất: Write status JSON/CSV/MD to a tmp file in the same directory, then os.replace, same pattern as compute_active_nav.py.

## /home/trido/thanhdt/WorkingClaude/mike/bin/check_report_cadence.sh:282 — duplicate-formula (low)
- Owner đề xuất: Wags
- INCOMPLETE_MARKERS is hand-copied from report_return_gate.py with the note 'giữ đồng bộ tay — không import chéo được'. That is false: the heredoc is plain Python and can import report_return_gate from $ROOT/bin.
- Bằng chứng: check_report_cadence.sh:282 `INCOMPLETE_MARKERS = ("[TBD", "[chưa điền", "[chua dien", "[placeholder")`; report_return_gate.py:106 has the identical tuple; report_return_gate only imports stdlib + dividend_adjusted_return + wc_paths (l.67-79).
- Hướng sửa đề xuất: In the heredoc, add sys.path.insert(0, os.path.join(wc_root, 'mike', 'bin')) and `from report_return_gate import INCOMPLETE_MARKERS`, then delete the copy.

## /home/trido/thanhdt/WorkingClaude/mike/bin/check_report_cadence.sh:568 — dead-code (low)
- Owner đề xuất: Wags
- The CORR_STEP branch only runs before 2026-10-24, so as of today (2026-10-25) it is permanently dead along with its reference to report-corrections-pending-20261014.md.
- Bằng chứng: l.568 `if [ "$(TZ=Asia/Ho_Chi_Minh date +%F)" \< "2026-10-24" ]; then CORR_STEP="BẮT BUỘC (báo cáo tuần này ..."`; l.566 comment 'tới hết 2026-10-23'.
- Hướng sửa đề xuất: Delete the CORR_STEP block and the ${CORR_STEP} placeholder in the weekly PROMPT.

## /home/trido/thanhdt/WorkingClaude/custom_basket.py:368 — correctness (low)
- Owner đề xuất: Taylor
- _CA_CACHE is keyed only on tuple(tickers), not on BASKET_CA_SNAPSHOT. If one process reads LIVE and then the SNAPSHOT (or the other way round), the second call returns the first vintage; callers have to remember to clear the cache by hand.
- Bằng chứng: l.368-370 `key = tuple(tickers); if key in _CA_CACHE: return _CA_CACHE[key]` comes before `snap = os.environ.get("BASKET_CA_SNAPSHOT", "")`. grep: basket_oshares_step_exdate_selfcheck.py:193 and research/oshares_weight_exdate_20260927/basket_level_yearly.py:26 both have to call `cb._CA_CACHE.clear()` manually.
- Hướng sửa đề xuất: Include the snapshot path in the key: key = (snap, tuple(tickers)).

## /home/trido/thanhdt/WorkingClaude/mike/bin/auto_exit_inject.py:549 — correctness (low)
- Owner đề xuất: Wags
- The BAL stop-loss path calls _inject_sell without rights_lots/locked_notes, unlike BAL T+45 and LAG. A rights-issue lot that is not yet listed therefore goes through the 🚨 'bị CẮT' (Discord) warning instead of being split out as locked info.
- Bằng chứng: l.532-534 (BAL T+45): `_inject_sell(..., rights_lots=bal_lots.get(tk, {}).get("rights_lots"), locked_notes=locked_notes)`; l.549-550 (stop-loss): `_inject_sell(plan, positions, tk, qty, ref_price, "BAL", "BAL_AUTO_EXIT", note, "BAL-STOPLOSS", injected, capped_notes, f"stoploss={pnl_pct:.1%}")`, missing both arguments.
- Hướng sửa đề xuất: Pass rights_lots=bal_lots.get(tk, {}).get('rights_lots') and locked_notes=locked_notes to the stop-loss call as well.

## /home/trido/thanhdt/WorkingClaude/freshness_ops_selfcheck.py:109 — code-smell:Shotgun Surgery (low)
- Owner đề xuất: Taylor
- The selfcheck runs the real bq_freshness_check.sh with a hand-written fake bq whose stubs match query substrings. Every new probe or hook added to bq_freshness_check.sh needs a matching stub here, otherwise there is a false red. This has already happened at least 3 times.
- Bằng chứng: l.109-110 '(thêm 2026-08-08 — script thật đã mọc thêm 3 probe này; sandbox thiếu stub ...)'; l.117-118 'Price-freeze probe ... thiếu stub ... S1/S3 đỏ (selfcheck-red 2026-09-27→10-09)'; l.178-180 'rights_issue_alert ... thiếu file trong sandbox ⇒ ... S1/S3 đỏ (selfcheck-red 2026-10-22)'.
- Hướng sửa đề xuất: Make the fake-bq fallback (no stub matched) print a clear 'UNSTUBBED QUERY: <q>' and fail the selfcheck with that message, instead of returning gap_days=999 and causing a confusing downstream red. That way the next drift is diagnosed immediately.

## /home/trido/thanhdt/WorkingClaude/custom_basket.py:665 — code-smell:Long Method (low)
- Owner đề xuất: Taylor
- build_pit is a single ~985-line function (665-1650) whose behaviour is switched by about 30 env vars (BASKET_*, V3R_*) inside the body, making it very hard to review or test one variant in isolation.
- Bằng chứng: srcwalk outline: `[665-1650] fn build_pit`. Inside the body: os.environ.get for BASKET_QFLOOR, BASKET_CFO_BLEND, BASKET_CFO_POOL, BASKET_YIELD_METRIC, BASKET_SELECT, BASKET_EXCLUDE, BASKET_LIQ_FLOOR_B, BASKET_MOM_W, BASKET_RSI_W, BASKET_PEADJ, BASKET_DCF_MODE/W/PLACEBO_SEED, V3R_W_ABS/CFO_UP/CFO_DN/TRK_CF/TRK_ROE/ABSTAIN_IMPUTE, BASKET_PLACEBO_FIN, BASKET_SECCAP_MODE, BASKET_FIN_CAP, BASKET_RISK_SCOPE, BASKET_DY_TIEBREAK... The selfchecks have to extract closures via ast (dcf_selector_selfcheck.py:159-195) because they cannot be imported.
- Hướng sửa đề xuất: No large refactor needed. When a variant next changes, pull that variant's block (e.g. dcf_at, the yieldcombo scoring) into a module-level function so it can be imported and tested directly.

## File đã đọc kỹ, không có vấn đề (14)
- /home/trido/thanhdt/WorkingClaude/append_cctg_rate.py
- /home/trido/thanhdt/WorkingClaude/basket_price_basis_audit_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/daily_refresh_v34b_linux.sh
- /home/trido/thanhdt/WorkingClaude/dcf_check_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/dcf_selector_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/deposit_cctg_trend_check.py
- /home/trido/thanhdt/WorkingClaude/lag_rating_stale_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/svs_overlay_v2.py
- /home/trido/thanhdt/WorkingClaude/mike/bin/_now_injection_probe.py
- /home/trido/thanhdt/WorkingClaude/mike/bin/arch_noise_gate_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/mike/bin/auto_exit_inject_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/mike/bin/bus_question_closure_selfcheck.py
- /home/trido/thanhdt/WorkingClaude/mike/bin/close_bus_question.py
- /home/trido/thanhdt/WorkingClaude/mike/bin/compute_active_nav_all.sh