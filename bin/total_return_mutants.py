#!/usr/bin/env python3
"""Bộ ĐỘT BIẾN cho bản vá chuẩn tỉ suất tổng 2026-10-10 (GIPS/tax-lot).

Mỗi đột biến đảo ĐÚNG MỘT dòng vá trong `dividend_adjusted_return.py` / `report_return_gate.py`
về hành vi cũ (hoặc gỡ đúng một lá chắn), rồi chạy selfcheck nhúng của file đó trên BẢN SAO:
selfcheck phải ĐỎ. Đột biến sống = một dòng vá không có assertion nào canh.

Bản sao nằm trong thư mục tạm của HỆ THỐNG (`tempfile.mkdtemp()`), KHÔNG trong `bin/`: bản đầu
đặt chúng dưới `bin/.total_return_mutants_*` để `wc_paths.find_wc_root(__file__)` tìm ra gốc —
tức là có lúc trong `bin/` tồn tại một `report_return_gate.py` ĐỘT BIẾN, không gitignore, một
lượt bị kill là để lại (arch-review N9). Gốc cây truyền tường minh qua `WC_ROOT`:
  · cổng → một cây GIẢ dựng ngay trong thư mục tạm (`wc_env.sh` + `data/execution_logs/` rỗng):
    selfcheck nhúng của cổng không đọc sổ thật nào, nên không lượt nào chạm được dữ liệu sống;
  · công cụ cổ tức → cây THẬT chứa file này: mục 19 của selfcheck đó ĐỌC (chỉ đọc) sổ vị thế
    thật qua `daily_nav_snapshot` để ghim 6 ca credit sớm — cây giả làm chính baseline đỏ.

Không nằm trong `run_selfchecks.sh` (tên file cố ý KHÔNG khớp `*selfcheck*`): chạy N lần selfcheck
nên chậm, và nó kiểm bộ TEST chứ không kiểm code. Chạy tay khi sửa hai file trên:

    python3 mike/bin/total_return_mutants.py            # rc=0 ⇔ baseline xanh VÀ mọi đột biến chết
    python3 mike/bin/total_return_mutants.py X05 Y12    # chỉ các đột biến có tên chứa chuỗi đó
"""
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

BIN = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BIN)
import wc_paths  # noqa: E402

REAL_ROOT = wc_paths.find_wc_root(__file__)
DAR, RRG = "dividend_adjusted_return.py", "report_return_gate.py"

# (tên, ca, file, đoạn gốc — phải xuất hiện ĐÚNG 1 lần, đoạn thay)
MUTANTS = [
    ("noise_never", "CA1", DAR, "NOISE_AMP_MULT = 1.5\n", "NOISE_AMP_MULT = 0.0\n"),
    ("noise_on_lookup_error", "CA1", DAR,
     "            continue                               # KHÔNG tra được ⇒ không được phép gọi là nhiễu\n",
     "            row = None\n"),
    ("noise_any_size", "CA1", DAR,
     "            and 0 < adj.ratio_jump <= NOISE_AMP_MULT * adj.ratio_noise_amp\n",
     "            and True\n"),
    ("solver_no_vendor_witness", "CA1", DAR,
     "            if val <= 0 or not (ok_ratio or ok_vendor):", "            if val <= 0 or not ok_ratio:"),
    ("solver_no_sanity", "CA1", DAR,
     "            if val <= 0 or not (ok_ratio or ok_vendor):", "            if val <= 0:"),
    ("unverified_old_definition", "CA1", DAR,
     '                if not getattr(a, "resolved", False) or getattr(a, "entitled", "") == "unknown"]',
     '                if a.kind != "CASH_CONFIRMED" or getattr(a, "entitled", "") == "unknown"]'),
    ("no_vendor_union", "CA1", DAR,
     "    warnings = _add_vendor_only_events(adjs, tickers, start, end)\n", "    warnings = []\n"),
    ("lagged_jump_not_merged", "CA1", DAR,
     "        if v is not None and _lag_completes(v, looked[id(v)][0], adj):", "        if False:"),
    ("lagged_jump_merged_blindly", "CA1", DAR,
     "    return abs(got / want - 1.0) <= LAG_TOL\n", "    return True\n"),
    ("div_not_rebased", "CA4", DAR,
     "        return self.cash_per_share / self.frame_factor\n", "        return self.cash_per_share\n"),
    ("cost_not_rebased", "CA4", DAR, "            cost = cost / mult\n", "            pass\n"),
    ("frame_guess_when_undeclared", "CA4", DAR,
     '        if cost_frame not in ("purchase", "current"):', "        if False:"),
    ("frame_excludes_own_leg", "CA4", DAR,
     "            for j, ok in zip(evs[i:], known[i:]):", "            for j, ok in zip(evs[i + 1:], known[i + 1:]):"),
    ("rights_counted_as_free", "CA4", DAR, "            if method in FREE_SHARE_ISS:", "            if True:"),
    ("mult_conflict_ignored", "CA4", DAR,
     "        if abs(adj.share_multiplier - (1.0 + free)) > MULT_TOL:", "        if False:"),
    ("unknown_later_event_ok", "CA4", DAR,
     "            return False                               # không nguồn nào nói nó là tiền hay cổ phiếu\n",
     "            return True\n"),
    ("nonfree_iss_called_stock", "CA4", DAR, '                        else "ISS_NONFREE")', '                        else "STOCK_CONFIRMED")'),
    ("vendor_multiplier_dropped", "CA4", DAR,
     "    elif free > 0:\n        adj.share_multiplier = 1.0 + free\n", "    elif False:\n        pass\n"),
    ("stock_step_loose_tolerance", "CA2", DAR,
     "        elif abs(c1 - c0) <= max(1.0, 1e-3 * q1):", "        elif abs(c1 - c0) <= max(p1, 1.0):"),
    ("blank_reads_kept", "CA2", DAR,
     "    return {sym: _drop_blank_reads(rows) for sym, rows in out.items()}\n", "    return out\n"),
    ("entitled_falls_to_exdate", "CA2", DAR,
     '        if adj.last_cum_date in getattr(qmap, "days", ()):', "        if False:"),

    ("noise_treated_as_event", "CA1", RRG,
     '        if getattr(a, "kind", "") == "RATIO_NOISE":\n            continue', "        if False:\n            continue"),
    ("gate_issues_expectation_anyway", "CA2", RRG, "            if tk in blockers:\n", "            if False:\n"),
    ("unresolved_event_not_blocked", "CA2", RRG,
     '        if not getattr(a, "resolved", a.cash_per_share > 0):', "        if False:"),
    ("unclaimed_step_ignored", "CA2", RRG,
     '            if st["kind"] not in ("cash", "stock", "cash+stock"):', "            if True:"),
    ("resolved_vs_broker_step_unchecked", "CA2", RRG, "            if bad_cash or bad_mult:", "            if False:"),
    ("unobservable_treated_as_clean", "CA2", RRG, "    if not covered:\n", "    if False:\n"),
    ("lookup_failed_always_blocks", "CA2", RRG, '            if obs["kind"] != "none":', "            if True:"),
    ("claim_order_by_date_only", "CA2", RRG,
     '    for a in sorted(adjs, key=lambda x: (not getattr(x, "resolved", False), x.ex_date)):',
     "    for a in sorted(adjs, key=lambda x: x.ex_date):"),
    ("pre_ex_any_amount", "CA2", RRG, '                and abs(cash - step["cash"]) <= 1.0:', "                and True:"),
    ("pre_ex_counts_income", "CA2", RRG, "            if pre[0] <= asof:\n", "            if True:\n"),
    ("addback_ignored", "CA2", RRG,
     "    raw_cost = cost_price + addback_ps\n", "    raw_cost = cost_price + gross_ps\n"),
    ("lookback_fixed_120d", "CA2", RRG,
     "    return min(floor, days[0]) if days else floor\n", "    return floor\n"),
    ("price_always_close", "CA2", RRG,
     '    return (price, "Price") if later_events else (close, "Close")\n', '    return (close, "Close")\n'),
    ("excluded_skipped", "CA3", RRG,
     "            if tk in excl:\n                excluded_keys[key] = lb\n",
     "            if tk in excl:\n                continue\n"),
    ("excluded_in_total", "CA3", RRG,
     "            if tk not in excl:\n                tot_pl += pl\n", "            if True:\n                tot_pl += pl\n"),
    ("excluded_prose_checked", "CA3", RRG,
     "        if key not in excluded_keys:\n            by_ticker.setdefault(key[0], []).append((lb, exp))\n",
     "        if True:\n            by_ticker.setdefault(key[0], []).append((lb, exp))\n"),
    ("gate_div_not_rebased", "CA4", RRG,
     "        g = a.cash_per_share_now * phi\n", "        g = a.cash_per_share * phi\n"),
    ("no_dilution", "CA4", RRG, '            phi *= st["q0"] / st["q1"]\n', "            phi *= 1.0\n"),
    ("closed_holding_counted", "CA4", RRG,
     "        if cur and a.ex_date < cur[0][0][:10]:\n", "        if False:\n"),
    ("header_needs_pct_sign", "HDR", RRG,
     "    return qty_i, pct_i, ([] if pct_i is not None else cands)\n",
     "    return qty_i, pct_i, []\n"),
    ("money_column_read_as_pct", "HDR", RRG,
     "            col = next((j for j in cands if j < len(cells) and \"%\" in cells[j]), None)",
     "            col = next((j for j in cands if j < len(cells)), None)"),
    ("by_cell_takes_last_named", "HDR", RRG,
     "            col = next((j for j in cands if j < len(cells) and \"%\" in cells[j]), None)",
     "            col = cands[-1] if cands and cands[-1] < len(cells) and \"%\" in cells[cands[-1]] else None"),
    ("loss_header_not_known", "HDR", RRG, 'PCT_HEADER_OK = ("lãi", "lỗ", ', 'PCT_HEADER_OK = ("lãi", '),
    ("ty_suat_y_not_known", "HDR", RRG, '"tỉ suất", "tỷ suất", ', '"tỉ suất", '),
    ("qty_header_not_known", "HDR", RRG, 'low in ("kl", "qty")', 'low in ("kl",)'),
    ("blind_cells_not_blocked", "HDR", RRG,
     "    for ln, tk, hdr, cell in unrecognized_return_cells(report_path):",
     "    for ln, tk, hdr, cell in []:"),
    ("blind_ignores_weight_columns", "HDR", RRG,
     "                if SIGNED_PCT_CELL_RE.match(c) and not any(\n"
     "                        bad in h.lower() for bad in PCT_HEADER_NO):",
     "                if SIGNED_PCT_CELL_RE.match(c):"),
    ("blind_any_pct_cell", "HDR", RRG,
     "                if SIGNED_PCT_CELL_RE.match(c) and not any(",
     "                if \"%\" in c and not any("),
    ("ticker_regex_letters_only", "TV1", RRG, '_TK = r"[A-Z][A-Z0-9]{2}"\n', '_TK = r"[A-Z]{3}"\n'),
    # ---------------- vòng 2 (arch-review 9c4b8a90): B1 — nhiễu chỉ sau khi hỏi đủ nhân chứng
    ("X01_noise_without_drop_evidence", "B1", DAR,
     "    return (adj.ratio_noise_amp > RATIO_JUMP_MIN\n", "    return (True\n"),
    ("X02_noise_mult_3x", "B1", DAR, "NOISE_AMP_MULT = 1.5\n", "NOISE_AMP_MULT = 3.0\n"),
    ("X03_noise_mult_8x", "B1", DAR, "NOISE_AMP_MULT = 1.5\n", "NOISE_AMP_MULT = 8.0\n"),
    ("noise_no_physical_cap", "B1", DAR,
     "            and 0 < adj.ratio_per_share <= NOISE_MAX_VND)", "            and True)"),
    ("noise_cap_200", "B1", DAR, "NOISE_MAX_VND = 150.0\n", "NOISE_MAX_VND = 200.0\n"),
    ("noise_executed_only", "B1", DAR,
     "        anyrow = bq_corp_events_window(sorted({a.ticker for a in both}), start, end,\n"
     "                                       include_announced=True)",
     "        anyrow = bq_corp_events_window(sorted({a.ticker for a in both}), start, end,\n"
     "                                       include_announced=False)"),
    ("noise_vendor_row_ignored", "B1", DAR,
     '        if hit:\n            out[id(a)] = (f"vendor', '        if False:\n            out[id(a)] = (f"vendor'),
    ("noise_announced_error_swallowed", "B1", DAR,
     "        return {id(a): why for a in both}\n", "        return {}\n"),
    ("noise_ignores_cost_steps", "B1", DAR,
     '            if st["kind"] in ("cash", "stock", "cash+stock") and not owned(st) \\',
     '            if False and not owned(st) \\'),
    ("noise_ignores_orphan_cash", "B1", DAR,
     "            if orphan.get(d, 0.0) > 0:", "            if False:"),
    ("noise_cash_of_account_not_holding", "B1", DAR,
     "        if not any(float(qmap.get((adj.ticker, d)) or 0) > 0\n"
     "                   for d in (adj.last_cum_date, adj.ex_date)):\n            continue",
     "        if False:\n            continue"),
    ("noise_owned_step_counts", "B1", DAR,
     '("cash", "stock", "cash+stock") and not owned(st) \\', '("cash", "stock", "cash+stock") and True \\'),
    ("noise_owned_ignores_amount", "B1", DAR,
     'and abs(st["cash"] - cash) <= 1.0\n', "and True\n"),
    ("noise_veto_ignored", "B1", DAR,
     "    for adj in shaped:\n        if id(adj) in vetoes:", "    for adj in shaped:\n        if False:"),
    ("lag_veto_ignored", "B1", DAR,
     "    for adj, v in lagged:\n        if id(adj) in vetoes:", "    for adj, v in lagged:\n        if False:"),
    ("cash_slip_not_paired", "B1", DAR,
     "            if res[d] * res[d2] < 0 and abs(res[d] + res[d2]) <= tol(res[d]):",
     "            if False:"),
    ("cash_slip_40_days", "B1", DAR, "CASH_SLIP_DAYS = 4\n", "CASH_SLIP_DAYS = 40\n"),
    ("cash_negative_residual_is_orphan", "B1", DAR,
     "    return {d: r for d, r in res.items() if r > tol(r)}\n",
     "    return {d: abs(r) for d, r in res.items() if abs(r) > tol(r)}\n"),
    ("cash_totals_drop_cash_plus_stock", "B1", DAR,
     '            if st["cash"] > 0:\n                d = st["ts"][:10]',
     '            if st["kind"] == "cash":\n                d = st["ts"][:10]'),
    ("cash_covers_one_side", "B4", DAR,
     "return any(r[:19] <= lo for r in self.readings) and any(",
     "return any(r[:19] <= lo for r in self.readings) or any("),
    # ---------------- B2 — quyền hưởng theo tài khoản
    ("account_ignored", "B2", DAR,
     "    if account_no:\n        mark_entitlement(adjs, account_no)", "    if False:\n        pass"),
    ("not_entitled_still_counted", "B2", DAR,
     '        return a.resolved and getattr(a, "entitled", "") not in ("no", "unknown")',
     "        return a.resolved"),
    ("no_ledger_read_as_not_held", "B2", DAR,
     "        elif days is not None and (a.last_cum_date in days or a.ex_date in days):",
     "        elif True:"),
    ("unknown_entitlement_not_flagged", "B2", DAR,
     '                if not getattr(a, "resolved", False) or getattr(a, "entitled", "") == "unknown"]',
     '                if not getattr(a, "resolved", False)]'),
    # ---------------- đột biến reviewer còn sống ở 9c4b8a90 (dar)
    ("X05_iss_nonfree_with_cash_resolved", "X", DAR,
     "            return self.vendor_cash <= 0\n", "            return True\n"),
    ("X06_stock_with_unsolved_cash_resolved", "X", DAR,
     '        return (self.kind == "STOCK_CONFIRMED" and self.vendor_cash <= 0\n',
     '        return (self.kind == "STOCK_CONFIRMED" and True\n'),
    ("X07_lookup_failed_later_event_known", "X", DAR,
     '                j.vendor_check in ("unavailable", "lookup_failed"):',
     '                j.vendor_check in ("unavailable",):'),
    ("X08_unresolved_mult_in_cost", "X", DAR,
     '        if counts(a) and a.kind != "RATIO_NOISE":', '        if a.kind != "RATIO_NOISE":'),
    ("X09_blank_drop_ignores_qty", "X", DAR,
     "        if j < n and rows[j][1] == out[-1][1] and abs(rows[j][2] - out[-1][2]) <= 1.0:",
     "        if j < n and abs(rows[j][2] - out[-1][2]) <= 1.0:"),
    ("X10_cost_step_tol_50", "X", DAR, "COST_STEP_TOL = 0.5 ", "COST_STEP_TOL = 50.0 "),
    # ---------------- B3 — mã không có kỳ vọng
    ("unresolved_qty_mismatch_passes", "B3", RRG,
     "        if key not in expected and tk in unres_tk:", "        if False:"),
    ("unresolved_mention_scan_off", "B3", RRG,
     '        if set(keys) <= unresolved_published or not mention[tk]["pub"]:', "        if True:"),
    ("mention_weight_column_counts", "B3", RRG,
     "                    if _PCT_ANY_RE.search(c) and not any(bad in h.lower() for bad in PCT_HEADER_NO):",
     "                    if _PCT_ANY_RE.search(c):"),
    ("mention_any_cell_of_row", "B3", RRG,
     '            if is_table and any(c.replace("*", "").strip() == tk for c in cells):',
     "            if is_table:"),
    ("mention_blockquote_not_stripped", "B3", RRG,
     "    stripped = [_strip_quote(ln) for ln in lines]", "    stripped = list(lines)"),
    ("mention_pct_of_other_ticker", "B3", RRG,
     '        if not re.search(r"(?<![A-Za-z0-9])" + _TK + r"(?![A-Za-z0-9])", m.group(1)):',
     "        if True:"),
    ("mention_no_prose_rule", "B3", RRG,
     "                near = _near_signed_pct(line, tk)", "                near = None"),
    ("quiet_message_unconditional", "B3", RRG,
     '    absent = [(k, v) for k, v in quiet if not (mention[k[0]]["pub"] or mention[k[0]]["seen"])]',
     "    absent = list(quiet)"),
    ("Y11_excluded_unresolved_blocks_prose", "B3", RRG,
     "        if k not in excluded_keys:\n            unres_tk.setdefault", "        if True:\n            unres_tk.setdefault"),
    # ---------------- B4 — bước mua/bán che bước trừ
    ("Y04_buy_other_does_not_hide", "B4", RRG,
     '    if masks:\n        return {"kind": "hidden", "why": "masked"', '    if False:\n        return {"kind": "hidden", "why": "masked"'),
    ("masked_resolved_assumed_deducted", "B4", RRG,
     '        if obs.get("why") == "masked":', "        if False:"),
    ("mask_doubt_ignored", "B4", RRG, "                if doubt:\n", "                if False:\n"),
    ("mask_no_cash_coverage_ok", "B4", RRG,
     '    if not cashd.covers(st["ts0"], st["ts"]):', "    if False:"),
    ("mask_orphan_cash_ignored", "B4", RRG, "    if near:\n", "    if False:\n"),
    ("mask_orphan_any_date", "B4", RRG,
     "    near = {d: v for d, v in orphan.items() if lo <= _dt.date.fromisoformat(d) <= hi}",
     "    near = dict(orphan)"),
    ("mask_only_buy", "B4", RRG,
     '            if st["kind"] in ("buy", "other"):\n                doubt',
     '            if st["kind"] in ("buy",):\n                doubt'),
    # ---------------- đột biến reviewer còn sống ở 9c4b8a90 (cổng)
    ("Y02_observe_window_unbounded_right", "Y", RRG,
     '           if a.last_cum_date <= st["ts"][:10] <= a.ex_date and i not in claimed]',
     '           if a.last_cum_date <= st["ts"][:10] and i not in claimed]'),
    ("Y03_covered_and_to_or", "Y", RRG,
     "               and any(r[0][:10] >= a.ex_date for r in cur))",
     "               or any(r[0][:10] >= a.ex_date for r in cur))"),
    ("Y05_dilution_counts_buys_before_event", "Y", RRG,
     '        if st["ts"] > after_ts and st["kind"] == "buy" and st["q1"] > 0:',
     '        if st["kind"] == "buy" and st["q1"] > 0:'),
    ("Y06_after_fallback_empty", "Y", RRG,
     '        after = obs["ts"] if "ts" in obs else a.last_cum_date + "T99"',
     '        after = obs["ts"] if "ts" in obs else ""'),
    ("Y07_unclaimed_stock_steps_ignored", "Y", RRG,
     '            if st["kind"] not in ("cash", "stock", "cash+stock"):',
     '            if st["kind"] not in ("cash",):'),
    ("Y08_pre_ex_accepts_stock_leg_event", "Y", RRG,
     '        if cash > 0 and float(row.get("stock_free") or 0.0) <= 0 \\', "        if cash > 0 and True \\"),
    ("Y09_holding_ignores_asof", "Y", RRG,
     "    cut = [r for r in series if r[0][:10] <= asof]", "    cut = list(series)"),
    ("Y10_lookup_failed_never_blocks", "Y", RRG, '            if obs["kind"] != "none":', "            if False:"),
    ("Y12_resolved_none_counts_deducted", "Y", RRG,
     '        if obs["kind"] == "none":\n            notes.append(f"{tk} ex {a.ex_date}: cổ tức',
     '        if False:\n            notes.append(f"{tk} ex {a.ex_date}: cổ tức'),
    ("Y13_unresolved_none_blocks", "Y", RRG,
     '            if obs["kind"] == "none":\n                notes.append(f"{tk} ex {a.ex_date} [{a.kind}] CHƯA giải',
     '            if False:\n                notes.append(f"{tk} ex {a.ex_date} [{a.kind}] CHƯA giải'),
    ("Y14_future_events_not_skipped", "Y", RRG, "        if a.ex_date > asof:\n", "        if False:\n"),
    ("Y15_pure_stock_event_adds_income", "Y", RRG, "        if want_cash <= 0:\n", "        if False:\n"),
    ("Y16_pre_ex_for_any_step_kind", "Y", RRG,
     '            if st["kind"] == "cash":\n                try:', '            if True:\n                try:'),
    ("Y17_price_today_branch", "Y", RRG, "                 if asof < today else {})", "                 if False else {})"),
    ("Y18_later_events_executed_only", "Y", RRG,
     "        later = (dar.bq_corp_events_window(tickers, asof, today, include_announced=True)",
     "        later = (dar.bq_corp_events_window(tickers, asof, today, include_announced=False)"),
    # ---------------- N12 — phương thức phát hành lạ
    ("N12_unknown_method_not_reported", "N12", DAR,
     "            elif method not in NONFREE_ISS:\n", "            elif False:\n"),
    ("N12_unknown_method_frame_ok", "N12", DAR,
     '        if row.get("unknown_methods"):\n            adj.frame_ok = False',
     '        if False:\n            adj.frame_ok = False'),
    ("N12_unknown_method_not_added", "N12", DAR,
     '                or row.get("unknown_methods")):', "                or False):"),
    ("N8_a2_exception_back", "N8", DAR,
     "        if changed:\n            adj.kind = \"STOCK_SUSPECTED\"",
     "        if changed and float(getattr(adj, \"vendor_cash\", 0.0) or 0.0) <= 0:\n"
     "            adj.kind = \"STOCK_SUSPECTED\""),
    # ---------------- N3 / N5 / N7
    ("N3_old_step_matches_by_amount", "N3", RRG,
     "        if ex in taken or (_dt.date.fromisoformat(ex) - step_day).days > PRE_EX_DAYS:",
     "        if ex in taken:"),
    ("N3_event_claims_many_steps", "N3", RRG,
     "        if ex in taken or (_dt.date.fromisoformat(ex) - step_day).days > PRE_EX_DAYS:",
     "        if (_dt.date.fromisoformat(ex) - step_day).days > PRE_EX_DAYS:"),
    ("N5_blocker_prints_solver_note", "N5", RRG,
     "            if not a.frame_ok and a.frame_note:", "            if False:"),
    ("N7_ex_equals_asof_rejected", "N7", RRG,
     "    lo = (day - _dt.timedelta(days=1)).isoformat()        # cửa sổ vendor là (lo, end]",
     "    lo = asof"),
    ("N7_ex_equals_asof_no_income", "N7", RRG, "            if pre[0] <= asof:\n", "            if False:\n"),
]


def _selfcheck(workdir: str, fname: str) -> int:
    env = dict(os.environ, PYTHONPATH=BIN + os.pathsep + os.environ.get("PYTHONPATH", ""),
               MIKE_BOT_TEST_MODE="1",
               WC_ROOT=os.path.join(workdir, "wcroot") if fname == RRG else REAL_ROOT)
    return subprocess.run([sys.executable, os.path.join(workdir, fname), "--selfcheck"],
                          env=env, cwd=workdir, stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL).returncode


def _workdir(src: dict, mutate=None) -> str:
    """Thư mục tạm chứa bản sao hai file (một file đã đột biến nếu có `mutate`) + cây gốc giả."""
    work = tempfile.mkdtemp(prefix="total_return_mutants_")
    os.makedirs(os.path.join(work, "wcroot", "data", "execution_logs"))
    open(os.path.join(work, "wcroot", "wc_env.sh"), "w").close()
    for f, text in src.items():
        if mutate and mutate[0] == f:
            text = text.replace(mutate[1], mutate[2])
        with open(os.path.join(work, f), "w", encoding="utf-8") as fh:
            fh.write(text)
    return work


def _run_one(src: dict, m: tuple) -> tuple:
    name, case, f, old, new = m
    n = src[f].count(old)
    if n != 1:
        return name, case, f, f"HỎNG — đoạn gốc xuất hiện {n} lần (cần 1)", []
    work = _workdir(src, (f, old, new))
    try:
        # đột biến ở `dar` có thể chỉ lộ qua selfcheck của cổng (cổng import bản sao `dar`)
        rcs = [_selfcheck(work, f)] + ([_selfcheck(work, RRG)] if f == DAR else [])
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return name, case, f, ("CHẾT" if any(rcs) else "SỐNG"), rcs


def main() -> int:
    only = sys.argv[1:]
    picked = [m for m in MUTANTS if not only or any(o in m[0] for o in only)]
    names = [m[0] for m in MUTANTS]
    dup = sorted({n for n in names if names.count(n) > 1})
    if dup:
        print(f"❌ tên đột biến trùng: {dup}")
        return 2
    src = {f: open(os.path.join(BIN, f), encoding="utf-8").read() for f in (DAR, RRG)}
    work = _workdir(src)
    try:
        base = {f: _selfcheck(work, f) for f in (DAR, RRG)}
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print(f"baseline (không đột biến): {base}")
    if any(base.values()):
        print("❌ baseline ĐỎ — mọi kết luận 'đột biến chết' phía dưới sẽ vô nghĩa, dừng.")
        return 2
    with ThreadPoolExecutor(6) as pool:
        results = list(pool.map(lambda m: _run_one(src, m), picked))
    survivors = [r[0] for r in results if r[3] == "SỐNG"]
    broken = [r[0] for r in results if r[3].startswith("HỎNG")]
    for name, case, f, state, rcs in results:
        print(f"  {state.split(' ')[0]:5s} {name:42s} [{case}] {f} rc={rcs}"
              + (f"  {state}" if state.startswith("HỎNG") else ""))
    print(f"\n{len(picked)} đột biến: {len(picked) - len(survivors) - len(broken)} chết, "
          f"{len(survivors)} SỐNG {survivors}, {len(broken)} hỏng {broken}")
    return 1 if (survivors or broken) else 0


if __name__ == "__main__":
    sys.exit(main())
