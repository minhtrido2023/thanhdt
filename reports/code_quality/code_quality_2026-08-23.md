# Code quality weekly — 2026-08-23

File đã quét: 25 (hot-core tuần này: `/home/trido/thanhdt/WorkingClaude/trading_bot/plan.py`)
Finding: 9 (từ 9 trước verify)

## trading_bot/brokers.py:260 — guideline:§25 (high)
- Owner đề xuất: Taylor
- BrokerBase.get_nav() computes NAV as get_cash() + market_value, but get_cash() on DNSEBroker returns the spendable-now field (availableCash-family), not the totalCash−totalDebt figure §25 mandates for NAV/sizing denominators.
- Bằng chứng: brokers.py:260-268 `def get_nav(self): cash = self.get_cash(); ...; return cash + mv`. DNSEBroker.get_cash() (line 522-531) reads `availablecash`/`withdrawablecash`/`purchasingpower`/... . Confirmed live caller: trading_bot/strategies.py:391 `account_nav = broker.get_nav()` then `scale = account_nav / paper['nav']` — the target-sizing denominator §25 says must use totalCash−totalDebt. mike/bin/compute_active_nav.py:144-146 explicitly documents this exact mistake: 'KHÔNG dùng b.get_cash(): hàm đó trả availableCash... SAI cho cơ sở NAV'.
- Đã qua verify độc lập: sống sót phản biện.

## trading_bot/plan.py:1968 — correctness (high)
- Owner đề xuất: Taylor
- lever_live_preflight's live-NAV anchor check uses broker.get_cash() (availableCash) instead of totalCash−totalDebt, contradicting its own docstring's claim to replicate compute_active_nav.py's formula, and repeating a bug class already fixed twice elsewhere in this repo.
- Bằng chứng: plan.py:1968 `cash = float(broker.get_cash() or 0)` then line 1985 `nav_live = cash + mv + offbook_vnd - excl_mv`. Docstring (line ~1867) claims 'đúng công thức mike/bin/compute_active_nav.py', but that file (line 144-146) says verbatim: 'KHÔNG dùng b.get_cash(): hàm đó trả availableCash... SAI cho cơ sở NAV'. §25's own measured case shows availableCash can understate totalCash by >95% same-day post-sale, which would make nav_live spuriously low and could wrongly trigger LIVE_PREFLIGHT_STRIP (stripping legitimate CAPIT margin leverage) on an ordinary trading day. Same bug class previously fixed in compute_park_trim.py (2026-08-09) and compute_active_nav.py (2026-08-10).
- Đã qua verify độc lập: sống sót phản biện.

## trading_bot/brokers.py:176 — correctness (high)
- Owner đề xuất: Taylor
- The base OrderUpdate.is_dead property treats any status string containing the bare substring "f" or "x" as dead; this bug is self-documented as fixed only for PHSFlashOrderUpdate, but DNSEBroker.poll_orders() and PHSBroker.poll_orders() still construct plain OrderUpdate and inherit the unfixed heuristic.
- Bằng chứng: brokers.py:182-183 `return any(k in s for k in ("cancel", "hủy", "huy", "reject", "từ chối", "fill", "khớp hết", "matchall", "expire", "f", "x"))`. PHSFlashOrderUpdate's docstring (lines 978-982) states verbatim the base heuristic wrongly kills a live status like 'Pending confirmation' because it contains 'f', causing 'executor đóng con lệnh và giải phóng chỗ trong khi lệnh vẫn còn khớp được' (double-exposure risk). DNSEBroker.poll_orders() (line 953-969) and PHSBroker.poll_orders() (line 429-443) both still build plain `OrderUpdate(oid, qget(o, "orderstatus"/"status", ...))`, not a status-code-based subclass — any live DNSE/PHS status string containing 'f' or 'x' (e.g. 'Confirmed') would be misclassified dead, freeing the order slot and risking a duplicate order — the same failure class ghost_order_selfcheck.py exists to prevent.
- Đã qua verify độc lập: sống sót phản biện.

## trading_bot/plan.py:381 — correctness (medium)
- Owner đề xuất: Taylor
- net_offsetting_orders() silently drops any order in a ticker group whose side is neither "buy" nor "sell" when that group also contains a genuine buy and sell — the order is marked handled but never re-emitted into new_orders or into any adj/log record.
- Bằng chứng: plan.py:372-393: `buys = [g for g in group if (g.side or "").lower() == "buy"]`, `sells = [... == "sell"]`; when `buys and sells` are both non-empty, line 381-382 does `for g in group: handled.add(id(g))` marking EVERY order in the group handled, but only members of `buys`/`sells` ever get appended via the synthesized net order — a third order with a blank/malformed `side` in that same ticker group vanishes from the executed plan with no trace.
- Đã qua verify độc lập: sống sót phản biện.

## trading_bot/brokers.py:1266 — guideline:§5 (medium)
- Owner đề xuất: Taylor
- PaperBroker._save() writes the cross-session state file (bot_paper_<label>.json) with a direct overwrite instead of the atomic tmp+os.replace pattern §5 requires for shared state files, unlike other writers in this same file.
- Bằng chứng: brokers.py:1266-1269 `def _save(self): os.makedirs(...); with open(self.state_file, "w", ...) as f: json.dump(self.state, f, ...)` — no tmp file, no os.replace. Called after every fill/cancel. A kill mid-write truncates the JSON and the next `_load()` (json.load) has no recovery path.
- Đã qua verify độc lập: sống sót phản biện.

## trading_bot/config.py:297 — guideline:§5 (low)
- Owner đề xuất: Taylor
- load_accounts()/load_config() bootstrap-write trading_bot_accounts.json/trading_bot_config.json with a direct overwrite instead of atomic tmp+rename; lower risk since this path only fires once, when the file doesn't yet exist.
- Bằng chứng: config.py:298-299 `with open(path, "w", ...) as f: json.dump({"accounts": raw}, f, ...)` and config.py:354-355 same pattern for DEFAULTS.

## oshares_live.py:1734 — assert-on-live-state (medium)
- Owner đề xuất: Taylor
- Several _selfcheck assertions call oshares_at with no cache fixture (hitting BigQuery live) and hard-code the exact expected share count at a fixed date, so a later vendor backfill/restatement of the corp-action feed (which this same module's docstring says happens routinely) can flip a currently-passing check to FAIL with zero code change.
- Bằng chứng: oshares_live.py:1734 `hhv = oshares_at(["HHV"], "2026-08-19", live=True)["HHV"]` then asserted `== 574_511_888.0` (line ~1749); same pattern for VCI (line ~1764, `== 850_100_000.0`) and ABB/NVL/KBC (lines ~2052-2072). Most other cases in the same selfcheck are deliberately hermetic with frozen fixtures citing §23, but these specific live-BQ checks are not.
- Đã qua verify độc lập: sống sót phản biện.

## lag_live_schedule_selfcheck.py:162 — bare-datetime-now (low)
- Owner đề xuất: Taylor
- TODAY is derived from a bare datetime.now().date() with no ZoneInfo("Asia/Ho_Chi_Minh") anchor, so the synthetic "event released today" fixture can land on the wrong calendar day if the host process TZ differs from ICT (e.g. right after UTC midnight but before ICT midnight, or vice versa).
- Bằng chứng: lag_live_schedule_selfcheck.py:162 `TODAY = pd.Timestamp(datetime.now().date())`, used to build synthetic release-date fixtures and to compute a T+5 scheduling offset (checks C1-C6).

## trading_bot/brokers.py:912 — dead-code (low)
- Owner đề xuất: Taylor
- DNSEBroker.modify_order() has zero callers anywhere in the repo; executor.py uses cancel+replace instead.
- Bằng chứng: grep -rn "broker\.modify_order" across the repo (excluding worktree copies) returns no hits; executor.py only calls `self.broker.cancel_order(...)` for order amendment (lines 1332, 1939, 1987), never `.modify_order(`.

## File đã đọc kỹ, không có vấn đề (21)
- bal_shadow_paper.py
- bot_execute.py
- capit_exit_floor_selfcheck.py
- capit_lever_selfcheck.py
- corp_action_lib.py
- custom30_history.py
- custom30_yield_labels.py
- custom30_yield_labels_selfcheck.py
- due_diligence_selfcheck.py
- exdate_price_frame_selfcheck.py
- gdkhq_rollout_selfcheck.py
- ghost_order_selfcheck.py
- hybrid_fill_timing_selfcheck.py
- lag_rule_a_ceiling.py
- order_book_shadow_selfcheck.py
- oshares_pit.py
- paper_entry_adjust.py
- paper_main_window_selfcheck.py
- phs_flash_api.py
- phs_flash_api_selfcheck.py
- quote_l2_logging_selfcheck.py