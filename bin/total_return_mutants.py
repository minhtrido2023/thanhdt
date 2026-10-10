#!/usr/bin/env python3
"""Bộ ĐỘT BIẾN cho bản vá chuẩn tỉ suất tổng 2026-10-10 (GIPS/tax-lot).

Mỗi đột biến đảo ĐÚNG MỘT dòng vá trong `dividend_adjusted_return.py` / `report_return_gate.py`
về hành vi cũ (hoặc gỡ đúng một lá chắn), rồi chạy selfcheck nhúng của file đó trên BẢN SAO:
selfcheck phải ĐỎ. Đột biến sống = một dòng vá không có assertion nào canh.

Từ vòng 2 của K1 (arch-review 53b48b76, F5) bộ này phủ thêm ba file của đường báo cáo NGÀY, mỗi
file có selfcheck riêng (bảng `TARGETS`): `portfolio_status.py` (selfcheck `portfolio_status_
selfcheck.py`, chạy trên bản sao trong thư mục tạm), `eod_trading_report.sh` và
`check_report_cadence.sh` (selfcheck của chúng nhận bản đột biến qua `EOD_SRC` / `RC_SRC`).

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
PS, PSS = "portfolio_status.py", "portfolio_status_selfcheck.py"
SH, SHS = "eod_trading_report.sh", "eod_trading_report_account_filter_selfcheck.py"
RC, RCS = "check_report_cadence.sh", "check_report_cadence_selfcheck.py"
# file bị đột biến -> các selfcheck phải chạy (theo thứ tự; dừng ở cái đầu tiên ĐỎ). Đột biến ở
# `dar` có thể chỉ lộ qua selfcheck của cổng (cổng import bản sao `dar`); đột biến ở cổng có thể
# chỉ lộ qua HỢP ĐỒNG mà selfcheck của `portfolio_status` ghim với cổng.
TARGETS = {DAR: (DAR, RRG), RRG: (RRG, PSS), PS: (PSS,), SH: (SHS,), RC: (RCS,)}
COPIED = (DAR, RRG, PS, PSS, SH, RC)

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
     "    res = _CostSeries((sym, _drop_blank_reads(rows)) for sym, rows in out.items())\n",
     "    res = _CostSeries(out)\n"),
    ("entitled_falls_to_exdate", "CA2", DAR,
     '        if adj.last_cum_date in getattr(qmap, "days", ()):', "        if False:"),

    ("noise_treated_as_event", "CA1", RRG,
     '        if getattr(a, "kind", "") == "RATIO_NOISE":\n            continue', "        if False:\n            continue"),
    ("gate_issues_expectation_anyway", "CA2", RRG,
     '               "why": list(blockers.get(tk, [])), "code": "blocked" if tk in blockers else ""}',
     '               "why": [], "code": ""}'),
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
     '            if r["excluded"]:\n                excluded_keys[key] = lb\n',
     '            if r["excluded"]:\n                continue\n'),
    ("excluded_in_total", "CA3", RRG,
     '            if not r["excluded"]:\n                tot_pl += r["pl"]\n',
     '            if True:\n                tot_pl += r["pl"]\n'),
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
     '            if st["kind"] in ("cash", "stock", "cash+stock") and not owned(st):',
     '            if False and not owned(st):'),
    ("noise_ignores_orphan_cash", "B1", DAR,
     '            if code == "orphan":\n                return f"{lb} đang giữ',
     '            if False:\n                return f"{lb} đang giữ'),
    ("noise_cash_of_account_not_holding", "B1", DAR,
     "        if not any(r[1] > 0 for r in rows[first:last + 1]):\n            continue",
     "        if False:\n            continue"),
    ("noise_owned_step_counts", "B1", DAR,
     '("cash", "stock", "cash+stock") and not owned(st):', '("cash", "stock", "cash+stock") and True:'),
    ("noise_owned_ignores_amount", "B1", DAR,
     'and abs(st["cash"] - cash) <= 1.0\n', "and True\n"),
    ("noise_veto_ignored", "B1", DAR,
     "    for adj in shaped:\n        if id(adj) in vetoes:", "    for adj in shaped:\n        if False:"),
    ("lag_veto_ignored", "B1", DAR,
     "    for adj, v in lagged:\n        if id(adj) in vetoes:", "    for adj, v in lagged:\n        if False:"),
    ("cash_slip_not_paired", "B1", DAR,
     "            if abs(res[d] + res[d2]) <= tol(res[d]):       # |res[d]| > tol ⇒ buộc TRÁI DẤU",
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
     "        elif days is not None and a.last_cum_date in days:",
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
     '            if is_table and any(re.sub(r"\\s*\\([^()]*\\)\\s*$", "", c.replace("*", "")).strip() == tk\n'
     "                                for c in cells):",
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
    ("mask_no_cash_coverage_ok", "B4", DAR,
     "    if not cashd.covers(t0, t1):\n        return \"blind\"", "    if False:\n        return \"blind\""),
    ("mask_orphan_cash_ignored", "B4", DAR, "    if near:\n        return \"orphan\"",
     "    if False:\n        return \"orphan\""),
    ("mask_orphan_any_date", "B4", DAR,
     "    near = {d: v for d, v in orphan.items() if lo <= _d.date.fromisoformat(d) <= hi}",
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
    # ================= VÒNG 3 (arch-review lần 2, 2026-10-10) =================
    # Tên `Rv_<id>` = bản TƯƠNG ĐƯƠNG của mutant `<id>` trong bộ của reviewer (/tmp/arch_rev2/
    # mymut.py) mà dòng neo đã đổi ở vòng này. KHÔNG có ở đây, có chủ ý:
    #   · M10 (bù trừ cùng dấu): điều kiện `res[d] * res[d2] < 0` đã GỠ vì thừa — |res[d]| > tol
    #     và |res[d] + res[d2]| ≤ tol buộc hai số trái dấu; không còn dòng nào để đột biến.
    #   · M25 (`frame_ok = True` khi vendor khai phương thức lạ): TƯƠNG ĐƯƠNG — `_assign_frames`
    #     chạy sau và đặt lại `frame_ok = False` cho mọi sự kiện có `frame_note` (`_known` trả
    #     False), nên dòng `adj.frame_ok = False` ở đó không quyết định kết quả nào.
    #   · M08 (cú nhảy trễ CŨNG hỏi broker): nay chính là code; đột biến ngược là Rv_M08.
    # ---- C1: một rổ giải
    ("Z01_basket_not_unioned", "C1", DAR,
     "    basket = sorted(asked | ledger_tickers(accounts, start, end))\n", "    basket = sorted(asked)\n"),
    ("Z02_basket_not_filtered", "C1", DAR,
     "    out = _AdjList(a for a in adjs if a.ticker in asked)\n", "    out = _AdjList(adjs)\n"),
    ("Z03_ledger_tickers_zero_qty", "C1", DAR,
     "            if any(q > 0 and start <= ts[:10] <= end for ts, q, _c in rows):",
     "            if any(start <= ts[:10] <= end for ts, q, _c in rows):"),
    ("Z04_ledger_tickers_any_date", "C1", DAR,
     "            if any(q > 0 and start <= ts[:10] <= end for ts, q, _c in rows):",
     "            if any(q > 0 for ts, q, _c in rows):"),
    ("Z05_solver_note_guesses_again", "C1", DAR,
     "            others = sorted({tk for (tk, day), q in qtys[lb].items() if day == d and q}\n",
     "            others = sorted(set()\n"),
    ("Z06_scope_leaks", "C1", DAR, "    finally:\n        _SCOPE = keep\n", "    finally:\n        pass\n"),
    ("Z07_scope_ignores_window", "C1", DAR,
     'return bool(sc) and ticker in sc["tickers"] and (start, end) == (sc["start"], sc["end"])',
     'return bool(sc) and ticker in sc["tickers"]'),
    ("Z08_scope_ignores_ticker", "C1", DAR,
     'return bool(sc) and ticker in sc["tickers"] and (start, end) == (sc["start"], sc["end"])',
     'return bool(sc) and (start, end) == (sc["start"], sc["end"])'),
    ("Z09_scope_swallows_bq_error", "C1", DAR,
     "    if err is not None:\n        raise err\n    return val\n", "    return val\n"),
    ("Z10_scope_serves_announced", "C1", DAR,
     '    if sc and not include_announced and ticker in sc["tickers"] \\',
     '    if sc and ticker in sc["tickers"] \\'),
    ("Z11_scope_serves_out_of_window_ex", "C1", DAR,
     '            and sc["start"] < ex_date <= sc["end"]:', "            and True:"),
    ("Z12_scope_never_batches", "C1", DAR, "    if _SCOPE is None:\n        return fetch()\n",
     "    if True:\n        return fetch()\n"),
    # ---- C2: ghép trễ CẦN và ĐỦ, và cũng phải qua broker
    ("Z20_lag_no_necessity", "C2", DAR,
     "    if abs(own / want - 1.0) <= LAG_TOL:\n        return False\n", ""),
    ("Rv_M08_lagged_skips_broker", "C2", DAR,
     "        else:\n            pending.append(a)\n    if pending:",
     "        elif root is None:\n            pending.append(a)\n    if pending:"),
    ("Rv_M08b_root_row_vetoes_itself", "C2", DAR, "                      and a.last_cum_date <= ex <= a.ex_date and (tk, ex) != root)",
     "                      and a.last_cum_date <= ex <= a.ex_date)"),
    ("Rv_M30_vendor_hit_only_ex_date", "C2", DAR, "                      and a.last_cum_date <= ex <= a.ex_date and (tk, ex) != root)",
     "                      and ex == a.ex_date and (tk, ex) != root)"),
    ("Z21_vendor_hit_no_lower_bound", "C2", DAR, "                      and a.last_cum_date <= ex <= a.ex_date and (tk, ex) != root)",
     "                      and ex <= a.ex_date and (tk, ex) != root)"),
    ("Rv_M15_lag_tol_10pct", "C2", DAR, "LAG_TOL = 0.02\n", "LAG_TOL = 0.10\n"),
    ("Rv_M15b_lag_tol_half_pct", "C2", DAR, "LAG_TOL = 0.02\n", "LAG_TOL = 0.005\n"),
    ("Rv_M15c_lag_guard_off", "C2", DAR,
     "    if p <= 0 or cash >= p:\n        return False\n    want = m * p / (p - cash)", "    want = m * p / (p - cash)"),
    ("Rv_M15d_lag_ignores_cash", "C2", DAR, "    want = m * p / (p - cash)\n", "    want = m\n"),
    ("Rv_M15f_lag_uses_all_iss", "C2", DAR,
     '    m = 1.0 + float(row["stock_free"] if "stock_free" in row else (row.get("stock") or 0.0))\n    if p <= 0',
     '    m = 1.0 + float(row.get("stock") or 0.0)\n    if p <= 0'),
    ("Rv_M16_lag_no_ratio_update", "C2", DAR,
     "        v.ratio_per_share = round(v.last_cum_price * (1.0 - 1.0 / total), 2)\n", "        pass\n"),
    ("Rv_M16b_lag_no_jump_update", "C2", DAR, "        v.ratio_jump = total - 1.0\n", "        pass\n"),
    ("Rv_M16c_lag_no_pershare_update", "C2", DAR,
     '        if v.source == "unresolved":\n            v.per_share = v.ratio_per_share\n', "        pass\n"),
    # ---- K3: lô phải thu / chi trả lẫn
    ("Rv_M27_readings_empty", "C4", DAR, "    out.readings = [ts for ts, _ in series]\n", "    out.readings = []\n"),
    ("Rv_M27b_deltas_include_negative", "C4", DAR,
     "        if cd > prev_cd:\n            out[ts[:10]]", "        if cd != prev_cd:\n            out[ts[:10]]"),
    ("Z30_every_payout_is_odd", "K3", DAR,
     "        elif cd < prev_cd and not _settle_lots(lots, float(prev_cd - cd)):", "        elif cd < prev_cd:"),
    ("Z31_no_payout_is_odd", "K3", DAR,
     "        elif cd < prev_cd and not _settle_lots(lots, float(prev_cd - cd)):", "        elif False:"),
    ("Z32_lots_not_recorded", "K3", DAR, "            lots.append(float(cd - prev_cd))\n", "            pass\n"),
    ("Z33_settle_any_amount", "K3", DAR,
     "            if abs(sum(lots[i] for i in idx) - paid) <= 1.0:", "            if True:"),
    ("Z34_settle_keeps_paid_lots", "K3", DAR,
     "                for i in sorted(idx, reverse=True):\n                    del lots[i]\n", ""),
    ("Z35_payout_never_doubts", "K3", DAR, '    if mixed:\n        return "payout"', '    if False:\n        return "payout"'),
    ("Z36_payout_any_gap", "K3", DAR, "             if p[:19] < t1[:19] and r[:19] > t0[:19]]", "             if True]"),
    ("Z37_payout_gap_touching_start", "K3", DAR, "             if p[:19] < t1[:19] and r[:19] > t0[:19]]",
     "             if p[:19] < t1[:19] and r[:19] >= t0[:19]]"),
    ("Z38_payout_gap_touching_end", "K3", DAR, "             if p[:19] < t1[:19] and r[:19] > t0[:19]]",
     "             if p[:19] <= t1[:19] and r[:19] > t0[:19]]"),
    # ---- K4 / C4: `cash_witness` + `_broker_touched`
    ("Rv_R02_witness_window_lo_zero", "C4", DAR,
     "    lo = _d.date.fromisoformat(t0[:10]) - _d.timedelta(days=CASH_SLIP_DAYS)", "    lo = _d.date.fromisoformat(t0[:10])"),
    ("Rv_R02_witness_window_hi_zero", "C4", DAR,
     "    hi = _d.date.fromisoformat(t1[:10]) + _d.timedelta(days=CASH_SLIP_DAYS)", "    hi = _d.date.fromisoformat(t1[:10])"),
    ("Rv_R02b_witness_window_hi_30d", "C4", DAR,
     "    hi = _d.date.fromisoformat(t1[:10]) + _d.timedelta(days=CASH_SLIP_DAYS)",
     "    hi = _d.date.fromisoformat(t1[:10]) + _d.timedelta(days=30)"),
    ("Rv_R02c_witness_window_lo_60d", "C4", DAR,
     "    lo = _d.date.fromisoformat(t0[:10]) - _d.timedelta(days=CASH_SLIP_DAYS)",
     "    lo = _d.date.fromisoformat(t0[:10]) - _d.timedelta(days=60)"),
    ("Rv_M09b_slip_days_1", "C4", DAR, "CASH_SLIP_DAYS = 4\n", "CASH_SLIP_DAYS = 1\n"),
    ("Rv_M09c_slip_days_3", "C4", DAR, "CASH_SLIP_DAYS = 4\n", "CASH_SLIP_DAYS = 3\n"),
    ("Rv_M09d_slip_days_5", "C4", DAR, "CASH_SLIP_DAYS = 4\n", "CASH_SLIP_DAYS = 5\n"),
    ("Rv_M10b_net_any_amount", "C4", DAR,
     "            if abs(res[d] + res[d2]) <= tol(res[d]):       # |res[d]| > tol ⇒ buộc TRÁI DẤU",
     "            if res[d] * res[d2] < 0:"),
    ("Rv_M04_owned_ignores_mult", "C4", DAR, '                   and abs(st["q1"] - st["q0"] * mult) <= 1.5', "                   and True"),
    ("Rv_M05_owned_ignores_window", "C4", DAR, "tk == adj.ticker and cum <= day <= ex and", "tk == adj.ticker and True and"),
    ("Rv_M05b_owned_any_ticker", "C4", DAR, "return any(tk == adj.ticker and cum <= day", "return any(True and cum <= day"),
    ("Rv_M06_touch_step_any_date", "C4", DAR, "        return t0[:10] <= hi and t1[:10] >= lo\n", "        return True\n"),
    ("Z40_touch_pair_only_by_end_day", "K4", DAR, "        return t0[:10] <= hi and t1[:10] >= lo\n",
     "        return lo <= t1[:10] <= hi\n"),
    ("Rv_M06b_touch_only_cash_steps", "C4", DAR,
     '            if st["kind"] in ("cash", "stock", "cash+stock") and not owned(st):',
     '            if st["kind"] in ("cash",) and not owned(st):'),
    ("Z41_blind_ledger_read_as_clean", "K4", DAR,
     '        if not (any(t[:10] < lo for t in L["ts"]) and any(t[:10] >= hi for t in L["ts"])):', "        if False:"),
    ("Z42_ledger_cover_one_side_enough", "K4", DAR,
     '        if not (any(t[:10] < lo for t in L["ts"]) and any(t[:10] >= hi for t in L["ts"])):',
     '        if not (any(t[:10] < lo for t in L["ts"]) or any(t[:10] >= hi for t in L["ts"])):'),
    ("Z43_masked_pairs_not_asked", "K4", DAR,
     '        spans = ([(st["ts0"], st["ts"]) for st in pairs if st["kind"] in ("buy", "other")]',
     "        spans = ([]"),
    ("Z44_opening_pairs_not_asked", "K4", DAR,
     '                 + [p for p in opening_pairs(rows, L["ts"]) if meets(*p)])', "                 + [])"),
    ("Z45_masked_pair_only_orphan_counts", "K4", DAR,
     "            if code:\n                return (f\"sổ giá vốn {lb} MÙ", "            if code == \"orphan\":\n                return (f\"sổ giá vốn {lb} MÙ"),
    ("Z46_clean_cost_but_blind_cash_vetoes", "K4", DAR,
     '            if code == "orphan":\n                return f"{lb} đang giữ', '            if code:\n                return f"{lb} đang giữ'),
    ("Z47_opening_pair_uses_itself", "K2", DAR,
     "            out.append((rows[i - 1][0] if i else max((t for t in record_ts if t < ts), default=ts),",
     "            out.append((ts,"),
    ("Z48_reopen_not_an_opening", "K2", DAR, "        if q > 0 and (i == 0 or rows[i - 1][1] <= 0):", "        if q > 0 and i == 0:"),
    ("Rv_M33_qtymap_days_dropped", "C4", DAR, "    out.days = set(day_last_rec)\n", "    pass\n"),
    ("Rv_M18_entitle_unknown_becomes_no", "C4", DAR, "        elif days is not None and a.last_cum_date in days:", "        elif True:  # Rv"),
    ("Rv_M18b_entitle_no_becomes_unknown", "C4", DAR, "        elif days is not None and a.last_cum_date in days:", "        elif False:"),
    ("Rv_M18c_entitle_ex_day_record_is_enough", "C4", DAR, "        elif days is not None and a.last_cum_date in days:",
     "        elif days is not None and (a.last_cum_date in days or a.ex_date in days):"),
    ("Rv_M19_entitle_marks_noise", "C4", DAR,
     '    for a in adjs:\n        if a.kind == "RATIO_NOISE":\n            continue\n        q, status, why = qty_entitled(qmap, a)',
     '    for a in adjs:\n        q, status, why = qty_entitled(qmap, a)'),
    # ---- cổng: K2, H1c, C3, K5 và nguyên thủy
    ("Rv_R01_gate_ignores_witness", "C4", RRG,
     '    return (text + " ⇒ không loại trừ được một bước trừ cổ tức nằm lẫn trong cặp bản ghi này"\n            if code else "")',
     '    return ""'),
    ("Rv_R12_all_deltas_orphan", "C4", RRG,
     "    orphan = dar.unexplained_cash(cashd, dar.cash_step_totals(series))", "    orphan = dar.unexplained_cash(cashd, {})"),
    ("Z60_opening_pair_not_checked", "K2", RRG,
     "        for before, opened in dar.opening_pairs(cur, record_ts):", "        for before, opened in []:"),
    ("Z61_solved_hidden_cash_still_orphan", "K2", RRG, "    if hidden_paid:\n", "    if False:\n"),
    ("Z62_hidden_cash_wrong_qty", "K2", RRG,
     "                                                + q_cum[-1] * want_cash)", "                                                + want_cash)"),
    ("Z63_h1c_never_blocks", "H1c", RRG,
     "    for tk in sorted({m[0] for m in unmatched_held_qty_mismatch} - matched_tk):", "    for tk in []:"),
    ("Z64_h1c_blocks_despite_exact_row", "H1c", RRG,
     "    for tk in sorted({m[0] for m in unmatched_held_qty_mismatch} - matched_tk):",
     "    for tk in sorted({m[0] for m in unmatched_held_qty_mismatch}):"),
    ("Z65_nocover_claims_unpublished_blind", "C3", RRG,
     '               if not cov_mention[tk]["pub"]]', "               if True]"),
    ("Z66_unchecked_published_silent", "C3", RRG,
     '    unchecked = [((tk, q), v) for (tk, q), v in nocover_keys if cov_mention[tk]["pub"]]', "    unchecked = []"),
    ("Z67_k5_any_multiplier", "K5", RRG,
     '        if mult > 1.0 and abs(step["q1"] - step["q0"] * mult) <= 1.5:', "        if mult > 1.0:"),
    ("Z68_k5_never_says", "K5", RRG,
     '    if step["kind"] not in ("stock", "cash+stock"):\n        return ""', '    if True:\n        return ""'),
    ("Rv_R07_near_pct_400chars", "C4", RRG, 'r"(?![A-Za-z0-9])([^%\\n]{0,40}?)"', 'r"(?![A-Za-z0-9])([^%\\n]{0,400}?)"'),
    ("Rv_R20_cands_when_pct_found", "C4", RRG,
     "    return qty_i, pct_i, ([] if pct_i is not None else cands)", "    return qty_i, pct_i, cands"),
    ("Rv_R22_cand_last_not_first", "C4", RRG,
     '            col = next((j for j in cands if j < len(cells) and "%" in cells[j]), None)',
     '            col = next((j for j in reversed(cands) if j < len(cells) and "%" in cells[j]), None)'),
    # ================ 2026-10-10 (job Taylor_20261010_105705): P1 + K1 + dòng arch-review lần 3
    # ---------------- P1 — tài khoản sổ rỗng / sổ bắt đầu sau cửa sổ không phải nhân chứng
    ("P1_revert", "P1", DAR,
     "            if _ledger_began_without(L, rows, lo):\n                continue\n",
     "            if False:\n                continue\n"),
    ("P1_skip_any_late_ledger", "P1", DAR,
     "    return first[:10] >= lo and not any(r[0] == first and r[1] > 0 for r in rows)\n",
     "    return first[:10] >= lo\n"),
    ("P1_skip_any_not_held_at_first", "P1", DAR,
     "    return first[:10] >= lo and not any(r[0] == first and r[1] > 0 for r in rows)\n",
     "    return not any(r[0] == first and r[1] > 0 for r in rows)\n"),
    # (P1_first_from_ticker_rows của vòng 1 đảo `L.get("first", …)` về `L["ts"][0]` — từ F1 đó
    #  CHÍNH LÀ code: `ts` đã là mốc mọi bản ghi của tài khoản. Bản tương đương: F1_ts_from_ticker_rows.)
    ("P1_empty_ledger_vetoes", "P1", DAR, "    if not first:\n        return True\n",
     "    if not first:\n        return False\n"),
    ("P1_ledger_first_blank", "P1", DAR,
     '            "first": rec_ts[0] if rec_ts else "",\n', '            "first": "",\n'),
    ("P1_record_ts_skips_empty_records", "P1", DAR,
     '    res.record_ts = [rec.get("ts") or "" for rec in recs]\n',
     "    res.record_ts = sorted({r[0] for rows in res.values() for r in rows})\n"),
    # ---------------- dòng reviewer thấy chưa ai canh (định nghĩa: /tmp/arch_rev2/mymut3.py)
    ("N05_holding_from_ledger_start", "N", DAR,
     "        first = max((i for i, r in enumerate(rows) if r[0][:10] < lo), default=0)", "        first = 0"),
    ("N05b_holding_to_ledger_end", "N", DAR,
     "        last = min((i for i, r in enumerate(rows) if r[0][:10] >= hi), default=len(rows) - 1)",
     "        last = len(rows) - 1"),
    ("N09_lag_necessity_tight", "N", DAR,
     "    if abs(own / want - 1.0) <= LAG_TOL:\n        return False",
     "    if abs(own / want - 1.0) <= 0.0005:\n        return False"),
    ("N09b_lag_necessity_loose", "N", DAR,
     "    if abs(own / want - 1.0) <= LAG_TOL:\n        return False",
     "    if abs(own / want - 1.0) <= 0.2:\n        return False"),
    ("N22_blind_lo_inclusive", "N", DAR,
     'if not (any(t[:10] < lo for t in L["ts"]) and any(t[:10] >= hi for t in L["ts"])):',
     'if not (any(t[:10] <= lo for t in L["ts"]) and any(t[:10] >= hi for t in L["ts"])):'),
    ("N22b_blind_hi_exclusive", "N", DAR,
     'if not (any(t[:10] < lo for t in L["ts"]) and any(t[:10] >= hi for t in L["ts"])):',
     'if not (any(t[:10] < lo for t in L["ts"]) and any(t[:10] > hi for t in L["ts"])):'),
    ("N29_asked_only_first", "N", DAR, "    asked = set(tickers)\n", "    asked = set(list(tickers)[:1])\n"),
    ("N30_hidden_paid_for_seen_steps", "N", RRG,
     '        if obs["kind"] == "hidden":\n            q_cum', "        if True:\n            q_cum"),
    ("N31_hidden_paid_latest_qty", "N", RRG,
     "            q_cum = [r[1] for r in cur if r[0][:10] <= a.last_cum_date]",
     "            q_cum = [r[1] for r in cur]"),
    ("N37_hidden_paid_clears_all_orphans", "N", RRG,
     "        orphan = dar.unexplained_cash(cashd, totals)", "        orphan = {}"),
    ("N38_hidden_paid_overwrites_totals", "N", RRG,
     "            totals[d] = totals.get(d, 0.0) + v", "            totals[d] = v"),
    # ---------------- sổ nhớ truy vấn theo lượt chạy
    ("memo_never_read", "MEMO", DAR, "    if memo and os.path.exists(memo):\n", "    if False:\n"),
    ("memo_never_written", "MEMO", DAR, "    if memo:\n        tmp = ", "    if False:\n        tmp = "),
    ("memo_key_ignores_sql", "MEMO", DAR,
     'hashlib.sha256(sql.encode("utf-8")).hexdigest()', 'hashlib.sha256(b"").hexdigest()'),
    ("memo_on_without_env", "MEMO", DAR,
     '    if not d or not os.path.isdir(d):\n        return ""\n', '    if False:\n        return ""\n'),
    # ---------------- K1 — báo cáo NGÀY: một chỗ tính, cổng đọc đúng dòng vị thế
    ("K1_bits_never_fail", "K1", RRG,
     "              file=out)\n        if any(abs(pct - e) <= tol_pp for _lb, e, _g in cands):\n",
     "              file=out)\n        if True:\n"),
    ("K1_bits_skip_excluded", "K1", RRG,
     "    for key, v in expected.items():\n        exp_by_tk.setdefault(key[0], []).append((v[0], v[1], v[5]))\n",
     "    for key, v in expected.items():\n        if key in excluded_keys:\n            continue\n"
     "        exp_by_tk.setdefault(key[0], []).append((v[0], v[1], v[5]))\n"),
    ("K1_unresolved_bit_not_blocked", "K1", RRG,
     "            elif not set(keys) <= unresolved_published:\n", "            elif False:\n"),
    ("K1_pct_dot_read_as_thousands", "K1", RRG,
     '    if re.fullmatch(r"[+\\-]?\\d+\\.\\d{1,2}", t):\n', "    if False:\n"),
    ("K1_pct_three_decimals_as_decimal", "K1", RRG,
     '    if re.fullmatch(r"[+\\-]?\\d+\\.\\d{1,2}", t):\n', '    if re.fullmatch(r"[+\\-]?\\d+\\.\\d+", t):\n'),
    ("K1_bits_read_inside_tables", "K1", RRG,
     "                continue\n            for tk, num in POSBIT_RE.findall(line):",
     "                pass\n            for tk, num in POSBIT_RE.findall(line):"),
    ("K1_posbit_unsigned", "K1", RRG, 'r"([+\\-−]\\d+(?:[.,]\\d+)?)\\s*%")\nSEP_RE',
     'r"([+\\-−]?\\d+(?:[.,]\\d+)?)\\s*%")\nSEP_RE'),
    ("K1_stale_price_ignored", "K1", RRG,
     '    if not price_session or price_session >= asof or not _is_session_day(asof):\n        return ""\n',
     '    if True:\n        return ""\n'),
    ("K1_stale_on_non_session_day", "K1", RRG,
     "    if not price_session or price_session >= asof or not _is_session_day(asof):\n",
     "    if not price_session or price_session >= asof:\n"),
    ("K1_stale_not_applied", "K1", RRG,
     '        if tk_stale:\n            row["why"].insert(0, tk_stale)\n',
     '        if False:\n            row["why"].insert(0, tk_stale)\n'),
    ("K1_no_cost_gets_pct", "K1", RRG,
     '        elif not row["why"] and cp + addback.get(tk, g) <= 0:\n', "        elif False:\n"),
    ("K1_price_session_dropped", "K1", RRG,
     '    res.price_session = getattr(prices, "session", None)\n', "    res.price_session = None\n"),
    ("K1_prices_session_unset", "K1", RRG, "    out.session = newest\n", "    out.session = None\n"),
    ("K1_published_ignores_bits", "K1", RRG,
     "        published = {tk for tk, _q, _p in rows} | prose_tk | bit_tk\n",
     "        published = {tk for tk, _q, _p in rows} | prose_tk\n"),
    ("K1_nocover_ignores_bits", "K1", RRG, "                    and k[0] not in bit_tk]", "                    ]"),
    ("K1_unheld_bits_counted_checked", "K1", RRG,
     "                bits_unheld += 1                  # mã không có trong sổ vị thế — ngoài phạm vi",
     "                bits_checked += 1"),
    # ---------------- H1c dạng bảng
    ("H1c_row_needs_ticker_first", "H1c", RRG,
     'ROW_RE = re.compile(r"^\\|(?:\\s*\\d+\\.?\\s*\\|)?\\s*(?:\\*\\*)?(" + _TK',
     'ROW_RE = re.compile(r"^\\|\\s*(?:\\*\\*)?(" + _TK'),
    ("H1c_row_no_note_after_ticker", "H1c", RRG, '_TK_NOTE = r"(?:\\s*\\([^|()]*\\))?"', '_TK_NOTE = r""'),
    ("H1c_tables_in_quote_skipped", "H1c", RRG,
     '        lines = [_strip_quote(ln.rstrip("\\n")) for ln in f]\n    rows, blind = [], []',
     '        lines = [ln.rstrip("\\n") for ln in f]\n    rows, blind = [], []'),
    ("H1c_mention_cell_exact_only", "H1c", RRG,
     'any(re.sub(r"\\s*\\([^()]*\\)\\s*$", "", c.replace("*", "")).strip() == tk',
     'any(c.replace("*", "").strip() == tk'),
    # ================ 2026-10-10 vòng 2 của K1 (job Taylor_20261010_125837, arch-review 53b48b76)
    # ---------------- F5: 17 đột biến reviewer để lại (15 SỐNG + 2 chỉ SẬP) — /tmp/archrev_k1_evidence/mymut.py
    ("R04_stale_code_blocked", "F5", RRG, '            row["code"] = "no_price"', '            row["code"] = "blocked"'),
    ("R16_table_cell_num_not_pctnum", "F5", RRG,
     "        qty, pct = _num(cells[qty_i]), _pct_num(cells[col])", "        qty, pct = _num(cells[qty_i]), _num(cells[col])"),
    ("R25_gate_ignores_position_returns_why", "F5", RRG,
     '            if r["why"]:\n                # KHÔNG dựng được giá vốn thô / không có giá đúng phiên',
     '            if False:\n                # KHÔNG dựng được giá vốn thô / không có giá đúng phiên'),
    ("R26_session_is_min_not_max", "F5", RRG,
     '    newest = max((str(r["d"])[:10] for r in rows), default=None)',
     '    newest = min((str(r["d"])[:10] for r in rows), default=None)'),
    ("D01_began_boundary_gt", "F5", DAR,
     "    return first[:10] >= lo and not any(r[0] == first and r[1] > 0 for r in rows)",
     "    return first[:10] > lo and not any(r[0] == first and r[1] > 0 for r in rows)"),
    ("D10_memo_no_isdir_check", "F5", DAR,
     '    if not d or not os.path.isdir(d):\n        return ""', '    if not d:\n        return ""'),
    ("P01_code_always_blocked", "F5", PS,
     '            no_ret[tk] = r.get("code") if r.get("code") in RETURN_UNAVAILABLE else "blocked"',
     '            no_ret[tk] = "blocked"'),
    ("P02_sleeve_den_broker_cost", "F5", PS, '            ret_pl[tk] = (r["pl"], r["qty"] * r["raw_cost"])',
     '            ret_pl[tk] = (r["pl"], r["qty"] * r["cost_price"])'),
    ("P03_sleeve_total_partial", "F5", PS, "        if den and all(tk in ret_pl for tk, *_ in rows):", "        if den:"),
    ("P10_why_row_still_gets_pct", "F5", PS,
     '        else:\n            pnl_pct = r["pct"]\n            ret_pl[tk]',
     '        if r and "pct" in r:\n            pnl_pct = r["pct"]\n            ret_pl[tk]'),
    ("P12_tool_error_swallowed_silently", "F5", PS,
     '            print(f"portfolio_status: công cụ tỉ suất §21 lỗi ({account} {date}) — không in tỉ suất "\n'
     '                  f"mã nào: {ret_err}", file=sys.stderr)', '            pass'),
    ("P13_why_not_logged", "F5", PS,
     '            print(f"portfolio_status: {tk} ({account} {date}) không có tỉ suất §21: "\n'
     '                  + " | ".join(r["why"]), file=sys.stderr)', '            pass'),
    ("B01_memo_not_exported", "F5", SH, '  export DAR_BQ_MEMO_DIR="$_eod_memo"', '  DAR_BQ_MEMO_DIR="$_eod_memo"'),
    ("B02_no_cleanup_trap", "F5", SH, "  trap 'rm -rf \"$_eod_memo\"' EXIT\n", "  :\n"),
    ("B03_timeout_back_to_60", "F5", SH, "capture_output=True, text=True, cwd=wc_root, timeout=600,",
     "capture_output=True, text=True, cwd=wc_root, timeout=60,"),
    ("B04_stderr_not_forwarded", "F5", SH,
     '        if _el.startswith(("portfolio_status:", "ℹ️", "⚠️")):\n            print(_el, file=sys.stderr)',
     '        if False:\n            print(_el, file=sys.stderr)'),
    # (P11_stop_blind_all_sleeves của reviewer: dòng đó đã đổi ở F2 — bản tương đương là
    #  F2_stop_blind_counts_auto_sleeves + F2_stop_blind_all_sleeves bên dưới.)
    # ---------------- F1: `ts` của sổ = mốc MỌI bản ghi, kể cả bản ghi rỗng; bản đọc rỗng đơn lẻ ở đầu sổ
    ("F1_ts_from_ticker_rows", "F1", DAR,
     '    ts = sorted({t for t in (getattr(series, "record_ts", None) or ()) if t} | row_ts)\n',
     "    ts = sorted(row_ts)\n"),
    ("F1_ts_only_record_ts", "F1", DAR,
     '    ts = sorted({t for t in (getattr(series, "record_ts", None) or ()) if t} | row_ts)\n',
     '    ts = sorted({t for t in (getattr(series, "record_ts", None) or ()) if t})\n'),
    ("F1_lone_blank_first_read_kept", "F1", DAR,
     "    if held and sum(1 for t in ts if t < held) == 1:\n", "    if False:\n"),
    ("F1_two_blank_reads_dropped_too", "F1", DAR,
     "    if held and sum(1 for t in ts if t < held) == 1:\n",
     "    if held and sum(1 for t in ts if t < held) >= 1:\n"),
    ("F1_blank_dropped_without_holding", "F1", DAR,
     "    if held and sum(1 for t in ts if t < held) == 1:\n",
     "    if len(ts) >= 1 and sum(1 for t in ts if not held or t < held) >= 1:\n"),
    ("F1_ledger_ts_from_ticker_rows", "F1", DAR, '            "ts": rec_ts,\n',
     '            "ts": sorted({r[0] for rows in series.values() for r in rows}),\n'),
    ("F1_first_ignores_witness_rule", "F1", DAR, '            "first": rec_ts[0] if rec_ts else "",\n',
     '            "first": min(getattr(series, "record_ts", None) or [""]),\n'),
    # ---------------- F4: giá của RIÊNG một mã dừng ở phiên cũ
    ("F4_prices_lagging_unset", "F4", RRG, "    out.lagging = lagging\n", "    out.lagging = {}\n"),
    ("F4_positions_drop_lagging", "F4", RRG,
     '    res.price_lagging = dict(getattr(prices, "lagging", None) or {})\n', "    res.price_lagging = {}\n"),
    ("F4_lagging_ticker_still_gets_pct", "F4", RRG,
     '        tk_stale = stale or (lagging_price_note(tk, lagging[tk], session) if tk in lagging else "")\n',
     "        tk_stale = stale\n"),
    ("F4_lagging_blocks_every_ticker", "F4", RRG,
     '        tk_stale = stale or (lagging_price_note(tk, lagging[tk], session) if tk in lagging else "")\n',
     '        tk_stale = stale or (lagging_price_note(tk, "?", session) if lagging else "")\n'),
    ("F4_lagging_compares_wrong_way", "F4", RRG,
     '        if str(r["d"])[:10] != newest:\n            lagging[r["tk"]] = str(r["d"])[:10]',
     '        if str(r["d"])[:10] == newest:\n            lagging[r["tk"]] = str(r["d"])[:10]'),
    # ---------------- F6: dây bẫy đếm dòng vị thế + POSBIT nhận in đậm / giá trị "?"
    ("F6_tripwire_off", "F6", RRG,
     "    for ln, label, n, read, noret in position_line_gaps(report_path):\n",
     "    for ln, label, n, read, noret in []:\n"),
    ("F6_tripwire_only_when_short", "F6", RRG,
     "        if read + noret != int(m.group(2)):\n", "        if read + noret < int(m.group(2)):\n"),
    ("F6_tripwire_ignores_no_return_mark", "F6", RRG,
     "            noret += body.count(NO_RETURN_MARK)\n", "            noret += 0\n"),
    ("F6_tripwire_counts_table_lines", "F6", RRG,
     '            if body.startswith("|"):\n                continue\n            read +=',
     '            if body.startswith("|"):\n                pass\n            read +='),
    ("F6_tripwire_runs_past_blank_line", "F6", RRG,
     "            if not body.strip():\n                break\n", "            if not body.strip():\n                continue\n"),
    ("F6_tripwire_not_in_blockquote", "F6", RRG,
     '        lines = [_strip_quote(ln.rstrip("\\n")) for ln in f]\n    out = []\n    for i, line in enumerate(lines):\n        m = DETAIL_HDR_RE',
     '        lines = [ln.rstrip("\\n") for ln in f]\n    out = []\n    for i, line in enumerate(lines):\n        m = DETAIL_HDR_RE'),
    ("F6_posbit_no_bold", "F6", RRG,
     'r")\\s+(?:\\d[\\d.,]*\\s*M|\\?)\\s*,\\s*\\*{0,2}\\s*"\n', 'r")\\s+(?:\\d[\\d.,]*\\s*M|\\?)\\s*,\\s*"\n'),
    ("F6_posbit_no_unknown_value", "F6", RRG,
     'r")\\s+(?:\\d[\\d.,]*\\s*M|\\?)\\s*,\\s*\\*{0,2}\\s*"\n', 'r")\\s+\\d[\\d.,]*\\s*M\\s*,\\s*\\*{0,2}\\s*"\n'),
    # ---------------- F2: khoảng cách tới ngưỡng cắt lỗ TỰ ĐỘNG đo trên cơ sở của lệnh
    ("F2_bal_on_published_return", "F2", PS,
     "            basis_pp = broker_pct[tk] if sleeve in AUTO_STOP_SLEEVES else pp\n", "            basis_pp = pp\n"),
    ("F2_every_sleeve_on_broker_basis", "F2", PS,
     "            basis_pp = broker_pct[tk] if sleeve in AUTO_STOP_SLEEVES else pp\n",
     "            basis_pp = broker_pct[tk]\n"),
    ("F2_no_auto_stop_sleeve", "F2", PS, 'AUTO_STOP_SLEEVES = frozenset({"BAL"})\n', "AUTO_STOP_SLEEVES = frozenset()\n"),
    ("F2_basis_other_formula", "F2", PS, "    return (market_price / avg_cost - 1.0) * 100.0\n",
     "    return (market_price - avg_cost) / market_price * 100.0\n"),
    ("F2_basis_without_validity_guard", "F2", PS,
     "    if not avg_cost or avg_cost <= 0 or not market_price or market_price <= 0:\n        return None\n",
     "    if False:\n        return None\n"),
    ("F2_basis_accepts_negative_cost", "F2", PS,
     "    if not avg_cost or avg_cost <= 0 or not market_price or market_price <= 0:\n",
     "    if not avg_cost or not market_price or market_price <= 0:\n"),
    ("F2_auto_text_reads_as_ticker_pct", "F2", PS,
     "    if sleeve in AUTO_STOP_SLEEVES:\n        return emoji, (", "    if False:\n        return emoji, ("),
    ("F2_auto_flag_printed_as_ticker_pct", "F2", PS,
     "        if sleeve in AUTO_STOP_SLEEVES:\n            # không in", "        if False:\n            # không in"),
    ("F2_stop_blind_counts_auto_sleeves", "F2", PS,
     "                        if sl in STOP_LOSS_PCT_BY_SLEEVE and sl not in AUTO_STOP_SLEEVES\n",
     "                        if sl in STOP_LOSS_PCT_BY_SLEEVE\n"),
    ("F2_stop_blind_all_sleeves", "F2", PS,
     "                        if sl in STOP_LOSS_PCT_BY_SLEEVE and sl not in AUTO_STOP_SLEEVES\n",
     "                        if sl not in AUTO_STOP_SLEEVES\n"),
    ("F2_auto_blind_flag_dropped", "F2", PS, "    if auto_blind:\n", "    if False:\n"),
    ("F2_auto_blind_all_sleeves", "F2", PS,
     "    auto_blind = sorted(tk for sl, rows in sleeves.items() if sl in AUTO_STOP_SLEEVES\n",
     "    auto_blind = sorted(tk for sl, rows in sleeves.items()\n"),
    # ---------------- F3: chú thích hai giá
    ("F3_price_note_dropped", "F3", PS, "        lines.append(PRICE_BASIS_NOTE)\n", "        pass\n"),
    # ---------------- F7: vỏ bash
    ("F7_memo_leftovers_never_cleaned", "F7", SH,
     "find \"${TMPDIR:-/tmp}\" -maxdepth 1 -type d -name 'eod_bq_memo.*' -user \"$(id -u)\" -mmin +1440 \\\n"
     "  -exec rm -rf {} + 2>/dev/null || true\n", ":\n"),
    ("F7_memo_cleanup_any_age", "F7", SH, "-user \"$(id -u)\" -mmin +1440 \\\n", "-user \"$(id -u)\" \\\n"),
    ("F7_memo_cleanup_any_name", "F7", SH, "-type d -name 'eod_bq_memo.*' -user", "-type d -name '*.*' -user"),
    ("F7_memo_overrides_caller", "F7", SH,
     'if [ -z "${DAR_BQ_MEMO_DIR:-}" ] && _eod_memo=', "if _eod_memo="),
    ("F7_report_leaks_tool_error", "F7", SH,
     '              + f" [rc={_ps.returncode}]", file=sys.stderr)\n        lines.append(PORTFOLIO_BLOCK_MISSING)',
     '              + f" [rc={_ps.returncode}]", file=sys.stderr)\n        lines.append("⚠️ portfolio_status.py: không có dữ liệu (" + _ps.stderr.strip().splitlines()[-1] + ")")'),
    ("F7_report_leaks_exception", "F7", SH,
     "          file=sys.stderr)\n    lines.append(PORTFOLIO_BLOCK_MISSING)",
     '          file=sys.stderr)\n    lines.append(f"⚠️ portfolio_status.py lỗi: {_e}")'),
    ("F7_tool_error_not_logged", "F7", SH,
     '              + f" [rc={_ps.returncode}]", file=sys.stderr)', '              + f" [rc={_ps.returncode}]", file=open(os.devnull, "w"))'),
    ("F7_exception_not_logged", "F7", SH,
     '    print(f"portfolio_status: KHÔNG gọi được ({account} {plan_date}) — {type(_e).__name__}: {_e}",\n          file=sys.stderr)',
     '    print(f"portfolio_status: KHÔNG gọi được ({account} {plan_date}) — {type(_e).__name__}: {_e}",\n          file=open(os.devnull, "w"))'),
    ("F7_crash_reason_is_wrapper_line", "F7", SH,
     '    case "$_last" in *"returned non-zero exit status"*)', '    case "$_last" in __khong_bao_gio__)'),
    ("F7_rc_fixed_reason_again", "F7", RC, '          if [ -n "$_RC_BLK" ]; then\n', "          if false; then\n"),
    ("F7_rc_crash_reason_is_wrapper_line", "F7", RC,
     "| grep -v '^[[:space:]]*$' | grep -v 'returned non-zero exit status' | tail -n 1 || true)\"\n            [ -n \"$_RC_WHY\" ] ||",
     "| grep -v '^[[:space:]]*$' | tail -n 1 || true)\"\n            [ -n \"$_RC_WHY\" ] ||"),
    ("F7_rc_wrapper_only_gives_nothing", "F7", RC,
     '            [ -n "$_RC_WHY" ] || _RC_WHY="$(printf', '            : || _RC_WHY="$(printf'),
    ("F7_rc_empty_output_says_nothing", "F7", RC,
     '          [ -n "$_RC_WHY" ] || _RC_WHY="cổng không in dòng nào', '          : || _RC_WHY="cổng không in dòng nào'),
    ("F7_rc_reason_not_sanitized", "F7", RC,
     '          _RC_WHY="$(printf \'%s\' "$_RC_WHY" | python3 -c', '          : "$(printf \'%s\' "$_RC_WHY" | python3 -c'),
    ("F7_rc_reason_not_in_message", "F7", RC,
     '— ${_RC_WHY}. Sweep tự retry mỗi ngày; chi tiết:', '— báo cáo đã tạo nhưng chưa giao đủ (Discord+email, hash-bound). Sweep tự retry mỗi ngày; chi tiết:'),
]


def _selfcheck(workdir: str, fname: str) -> int:
    """Chạy MỘT selfcheck trên bản sao trong `workdir`. `fname` = file mang selfcheck nhúng (DAR,
    RRG) hoặc file selfcheck rời (PSS chạy từ bản sao; SHS/RCS chạy bản thật trong `bin/` và nhận
    file .sh đột biến qua biến môi trường)."""
    env = dict(os.environ, PYTHONPATH=BIN + os.pathsep + os.environ.get("PYTHONPATH", ""),
               MIKE_BOT_TEST_MODE="1", AUTO_EXIT_TEST_MODE="1",
               WC_ROOT=os.path.join(workdir, "wcroot") if fname == RRG else REAL_ROOT)
    env.pop("DAR_BQ_MEMO_DIR", None)
    if fname in (DAR, RRG):
        cmd = [sys.executable, os.path.join(workdir, fname), "--selfcheck"]
    elif fname == PSS:
        cmd = [sys.executable, os.path.join(workdir, PSS)]
    else:
        env["EOD_SRC" if fname == SHS else "RC_SRC"] = os.path.join(workdir, SH if fname == SHS else RC)
        cmd = [sys.executable, os.path.join(BIN, fname)]
    p = subprocess.run(cmd, env=env, cwd=workdir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       text=True)
    # rc ≠ 0 mà có traceback KHÔNG phải AssertionError = selfcheck SẬP giữa chừng: đột biến "chết"
    # nhưng không assertion nào bắt nó, và mọi ca phía sau chỗ sập không còn chạy (arch-review K8).
    tb = p.stdout.rfind("Traceback (most recent call last)")
    crashed = tb >= 0 and "AssertionError" not in p.stdout[tb:]
    return -p.returncode if (p.returncode and crashed) else p.returncode


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
        rcs = []
        for target in TARGETS[f]:
            rcs.append(_selfcheck(work, target))
            if rcs[-1] > 0:                        # đã chết bằng assertion — khỏi chạy cái sau
                break
    finally:
        shutil.rmtree(work, ignore_errors=True)
    if any(rc > 0 for rc in rcs):
        return name, case, f, "CHẾT", rcs
    return name, case, f, ("SẬP" if any(rcs) else "SỐNG"), rcs


def main() -> int:
    only = sys.argv[1:]
    picked = [m for m in MUTANTS if not only or any(o in m[0] for o in only)]
    names = [m[0] for m in MUTANTS]
    dup = sorted({n for n in names if names.count(n) > 1})
    if dup:
        print(f"❌ tên đột biến trùng: {dup}")
        return 2
    src = {f: open(os.path.join(BIN, f), encoding="utf-8").read() for f in COPIED}
    work = _workdir(src)
    try:
        base = {f: _selfcheck(work, f) for f in (DAR, RRG, PSS, SHS, RCS)}
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print(f"baseline (không đột biến): {base}")
    if any(base.values()):
        print("❌ baseline ĐỎ — mọi kết luận 'đột biến chết' phía dưới sẽ vô nghĩa, dừng.")
        return 2
    with ThreadPoolExecutor(6) as pool:
        results = list(pool.map(lambda m: _run_one(src, m), picked))
    survivors = [r[0] for r in results if r[3] == "SỐNG"]
    crashed = [r[0] for r in results if r[3] == "SẬP"]
    broken = [r[0] for r in results if r[3].startswith("HỎNG")]
    for name, case, f, state, rcs in results:
        print(f"  {state.split(' ')[0]:5s} {name:42s} [{case}] {f} rc={rcs}"
              + (f"  {state}" if state.startswith("HỎNG") else ""))
    dead = len(picked) - len(survivors) - len(broken) - len(crashed)
    print(f"\n{len(picked)} đột biến: {dead} chết bằng ASSERTION, {len(survivors)} SỐNG {survivors}, "
          f"{len(crashed)} chỉ làm SẬP selfcheck (rc âm = không assertion nào bắt) {crashed}, "
          f"{len(broken)} hỏng {broken}")
    return 1 if (survivors or broken or crashed) else 0


if __name__ == "__main__":
    sys.exit(main())
