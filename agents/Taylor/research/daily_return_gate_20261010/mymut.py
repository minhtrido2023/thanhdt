import os, sys, shutil, subprocess, tempfile, re
from concurrent.futures import ThreadPoolExecutor
BIN = "/home/trido/thanhdt/WorkingClaude/wt-totalreturn-1010/bin"
REAL_ROOT = "/home/trido/thanhdt/WorkingClaude"
DAR, RRG = "dividend_adjusted_return.py", "report_return_gate.py"
sys.path.insert(0, BIN)
M = [
 # ---------------- DAR vòng 2 (B1 design i)
 ("M01_orphan_never_vetoes", DAR, "            if orphan.get(d, 0.0) > 0:", "            if False:"),
 ("M02_orphan_no_holding_check", DAR, "        if not any(float(qmap.get((adj.ticker, d)) or 0) > 0", "        if False and not any(float(qmap.get((adj.ticker, d)) or 0) > 0"),
 ("M03_owned_ignores_cash", DAR, 'cum <= day <= ex and abs(st["cash"] - cash) <= 1.0', "cum <= day <= ex and True"),
 ("M04_owned_ignores_mult", DAR, '                   and abs(st["q1"] - st["q0"] * mult) <= 1.5', "                   and True"),
 ("M05_owned_ignores_window", DAR, 'tk == adj.ticker and cum <= day <= ex and', "tk == adj.ticker and True and"),
 ("M05b_owned_any_ticker", DAR, 'return any(tk == adj.ticker and cum <= day', "return any(True and cum <= day"),
 ("M06_touch_step_any_date", DAR, '                    and adj.last_cum_date <= st["ts"][:10] <= adj.ex_date:', "                    and True:"),
 ("M06b_touch_only_cash_steps", DAR, 'if st["kind"] in ("cash", "stock", "cash+stock") and not owned(st) \\', 'if st["kind"] in ("cash",) and not owned(st) \\'),
 ("M06c_touch_ignores_owned", DAR, 'if st["kind"] in ("cash", "stock", "cash+stock") and not owned(st) \\', 'if st["kind"] in ("cash", "stock", "cash+stock") and True \\'),
 ("M07_orphan_only_lastcum", DAR, "        for d in (adj.last_cum_date, adj.ex_date):\n            if orphan.get(d, 0.0) > 0:", "        for d in (adj.last_cum_date,):\n            if orphan.get(d, 0.0) > 0:"),
 ("M07b_orphan_only_ex", DAR, "        for d in (adj.last_cum_date, adj.ex_date):\n            if orphan.get(d, 0.0) > 0:", "        for d in (adj.ex_date,):\n            if orphan.get(d, 0.0) > 0:"),
 ("M08_lagged_also_asks_broker", DAR, "        elif lo == a.last_cum_date:\n            pending.append(a)", "        else:\n            pending.append(a)"),
 ("M08b_lagged_vendor_window_wide", DAR, "for a, lo in [(a, a.ex_date) for a in lagged]", "for a, lo in [(a, a.last_cum_date + 'x') for a in lagged]"),
 ("M09_slip_unbounded", DAR, "            if (_d.date.fromisoformat(d2) - _d.date.fromisoformat(d)).days > CASH_SLIP_DAYS:", "            if (_d.date.fromisoformat(d2) - _d.date.fromisoformat(d)).days > 9999:"),
 ("M09b_slip_days_1", DAR, "CASH_SLIP_DAYS = 4\n", "CASH_SLIP_DAYS = 1\n"),
 ("M09c_slip_days_3", DAR, "CASH_SLIP_DAYS = 4\n", "CASH_SLIP_DAYS = 3\n"),
 ("M09d_slip_days_8", DAR, "CASH_SLIP_DAYS = 4\n", "CASH_SLIP_DAYS = 8\n"),
 ("M10_net_same_sign", DAR, "            if res[d] * res[d2] < 0 and abs(res[d] + res[d2]) <= tol(res[d]):", "            if abs(res[d] + res[d2]) <= tol(res[d]):"),
 ("M10b_net_any_amount", DAR, "            if res[d] * res[d2] < 0 and abs(res[d] + res[d2]) <= tol(res[d]):", "            if res[d] * res[d2] < 0:"),
 ("M11_orphan_returns_negative", DAR, "    return {d: r for d, r in res.items() if r > tol(r)}", "    return {d: r for d, r in res.items() if abs(r) > tol(r)}"),
 ("M12_covers_or", DAR, "        return any(r[:19] <= lo for r in self.readings) and any(r[:19] >= hi for r in self.readings)", "        return any(r[:19] <= lo for r in self.readings) or any(r[:19] >= hi for r in self.readings)"),
 ("M13_covers_slack_day", DAR, "def covers(self, t0: str, t1: str, slack_s: int = 300) -> bool:", "def covers(self, t0: str, t1: str, slack_s: int = 86400) -> bool:"),
 ("M13b_covers_slack_zero", DAR, "def covers(self, t0: str, t1: str, slack_s: int = 300) -> bool:", "def covers(self, t0: str, t1: str, slack_s: int = 0) -> bool:"),
 ("M14_noise_vnd_cap_off", DAR, "            and 0 < adj.ratio_per_share <= NOISE_MAX_VND)", "            and True)"),
 ("M14b_noise_vnd_200", DAR, "NOISE_MAX_VND = 150.0\n", "NOISE_MAX_VND = 200.0\n"),
 ("M15_lag_tol_10pct", DAR, "LAG_TOL = 0.02\n", "LAG_TOL = 0.10\n"),
 ("M15b_lag_tol_half_pct", DAR, "LAG_TOL = 0.02\n", "LAG_TOL = 0.005\n"),
 ("M15c_lag_guard_off", DAR, "    if p <= 0 or cash >= p:\n        return False\n    want = m * p / (p - cash)", "    want = m * p / (p - cash)"),
 ("M15d_lag_ignores_cash", DAR, "    want = m * p / (p - cash)\n", "    want = m\n"),
 ("M15e_lag_ignores_mult", DAR, "    want = m * p / (p - cash)\n", "    want = p / (p - cash)\n"),
 ("M15f_lag_uses_all_iss", DAR, '    m = 1.0 + float(row["stock_free"] if "stock_free" in row else (row.get("stock") or 0.0))\n    if p <= 0', '    m = 1.0 + float(row.get("stock") or 0.0)\n    if p <= 0'),
 ("M16_lag_no_ratio_update", DAR, "        v.ratio_per_share = round(v.last_cum_price * (1.0 - 1.0 / total), 2)\n", "        pass\n"),
 ("M16b_lag_no_jump_update", DAR, "        v.ratio_jump = total - 1.0\n", "        pass\n"),
 ("M16c_lag_no_pershare_update", DAR, "        if v.source == \"unresolved\":\n            v.per_share = v.ratio_per_share\n", "        pass\n"),
 ("M17_lag_matches_same_day", DAR, "        v = vendor_backed.get((adj.ticker, adj.last_cum_date))", "        v = vendor_backed.get((adj.ticker, adj.ex_date))"),
 ("M17b_lag_veto_ignored", DAR, "    for adj, v in lagged:\n        if id(adj) in vetoes:\n            continue", "    for adj, v in lagged:\n        if False:\n            continue"),
 ("M17c_shaped_veto_ignored", DAR, "    for adj in shaped:\n        if id(adj) in vetoes:\n            continue", "    for adj in shaped:\n        if False:\n            continue"),
 ("M18_entitle_unknown_becomes_no", DAR, "        elif days is not None and (a.last_cum_date in days or a.ex_date in days):", "        elif True:"),
 ("M18b_entitle_no_becomes_unknown", DAR, "        elif days is not None and (a.last_cum_date in days or a.ex_date in days):", "        elif False:"),
 ("M18c_entitle_only_lastcum_day", DAR, "        elif days is not None and (a.last_cum_date in days or a.ex_date in days):", "        elif days is not None and (a.last_cum_date in days):"),
 ("M19_entitle_marks_noise", DAR, '    for a in adjs:\n        if a.kind == "RATIO_NOISE":\n            continue\n        q, status, why = qty_entitled(qmap, a)', '    for a in adjs:\n        q, status, why = qty_entitled(qmap, a)'),
 ("M20_unknown_entitled_counts", DAR, 'return a.resolved and getattr(a, "entitled", "") not in ("no", "unknown")', 'return a.resolved and getattr(a, "entitled", "") not in ("no",)'),
 ("M20b_no_entitled_counts", DAR, 'return a.resolved and getattr(a, "entitled", "") not in ("no", "unknown")', 'return a.resolved and getattr(a, "entitled", "") not in ("unknown",)'),
 ("M20c_unknown_not_flagged", DAR, '                if not getattr(a, "resolved", False) or getattr(a, "entitled", "") == "unknown"]', '                if not getattr(a, "resolved", False)]'),
 ("M22_account_ignored", DAR, "    if account_no:\n        mark_entitlement(adjs, account_no)", "    if False:\n        mark_entitlement(adjs, account_no)"),
 ("M24_unknown_method_silent", DAR, "            elif method not in NONFREE_ISS:", "            elif False:"),
 ("M25_unknown_method_frame_ok", DAR, '        if row.get("unknown_methods"):\n            adj.frame_ok = False', '        if row.get("unknown_methods"):\n            adj.frame_ok = True'),
 ("M26_vendor_only_drops_odd", DAR, "        if not ((row.get(\"cash\") or 0) > 0 or (row.get(\"stock_free\") or 0) > 0\n                or row.get(\"unknown_methods\")):", "        if not ((row.get(\"cash\") or 0) > 0 or (row.get(\"stock_free\") or 0) > 0):"),
 ("M27_readings_empty", DAR, "    out.readings = [ts for ts, _ in series]\n", "    out.readings = []\n"),
 ("M27b_deltas_include_negative", DAR, "        if cd > prev_cd:\n            out[ts[:10]]", "        if cd != prev_cd:\n            out[ts[:10]]"),
 ("M28_steptotal_q1", DAR, '                out[d] = out.get(d, 0.0) + st["q0"] * st["cash"]', '                out[d] = out.get(d, 0.0) + st["q1"] * st["cash"]'),
 ("M29_announced_window_only_executed", DAR, "        anyrow = bq_corp_events_window(sorted({a.ticker for a in both}), start, end,\n                                       include_announced=True)", "        anyrow = bq_corp_events_window(sorted({a.ticker for a in both}), start, end,\n                                       include_announced=False)"),
 ("M30_vendor_hit_ignores_window", DAR, "return sorted(ex for (tk, ex) in anyrow if tk == a.ticker and lo <= ex <= a.ex_date)", "return sorted(ex for (tk, ex) in anyrow if tk == a.ticker and ex == a.ex_date)"),
 ("M31_vetoed_note_dropped", DAR, "        if id(adj) in vetoes and adj.kind != \"CASH_CONFIRMED\":", "        if False:"),
 ("M32_noise_resolved_false", DAR, '        if self.kind == "RATIO_NOISE":\n            return True\n        if not self.frame_ok:', '        if not self.frame_ok:'),
 ("M33_qtymap_days_dropped", DAR, "    out.days = set(day_last_rec)\n", "    pass\n"),
 # ---------------- RRG vòng 2 + d02941e9
 ("R01_mask_no_cover_check", RRG, '    if not cashd.covers(st["ts0"], st["ts"]):', "    if False:"),
 ("R02_mask_window_zero", RRG, '    lo = _dt.date.fromisoformat(st["ts0"][:10]) - _dt.timedelta(days=dar.CASH_SLIP_DAYS)\n    hi = _dt.date.fromisoformat(st["ts"][:10]) + _dt.timedelta(days=dar.CASH_SLIP_DAYS)', '    lo = _dt.date.fromisoformat(st["ts0"][:10])\n    hi = _dt.date.fromisoformat(st["ts"][:10])'),
 ("R02b_mask_window_30d", RRG, '    hi = _dt.date.fromisoformat(st["ts"][:10]) + _dt.timedelta(days=dar.CASH_SLIP_DAYS)', '    hi = _dt.date.fromisoformat(st["ts"][:10]) + _dt.timedelta(days=30)'),
 ("R02c_mask_window_lo_60d", RRG, '    lo = _dt.date.fromisoformat(st["ts0"][:10]) - _dt.timedelta(days=dar.CASH_SLIP_DAYS)', '    lo = _dt.date.fromisoformat(st["ts0"][:10]) - _dt.timedelta(days=60)'),
 ("R03_mask_only_buy", RRG, '            if st["kind"] in ("buy", "other"):\n                doubt', '            if st["kind"] in ("buy",):\n                doubt'),
 ("R03b_mask_only_other", RRG, '            if st["kind"] in ("buy", "other"):\n                doubt', '            if st["kind"] in ("other",):\n                doubt'),
 ("R04_masked_resolved_ok", RRG, '        if obs.get("why") == "masked":', "        if False:"),
 ("R05_qty_mismatch_unres_not_row_blocked", RRG, "        if key not in expected and tk in unres_tk:", "        if False:"),
 ("R06_mention_counts_weight_cols", RRG, "                    if _PCT_ANY_RE.search(c) and not any(bad in h.lower() for bad in PCT_HEADER_NO):", "                    if _PCT_ANY_RE.search(c):"),
 ("R07_near_pct_400chars", RRG, 'r"(?![A-Za-z0-9])([^%\\n]{0,40}?)"', 'r"(?![A-Za-z0-9])([^%\\n]{0,400}?)"'),
 ("R07b_near_pct_crosses_tickers", RRG, '        if not re.search(r"(?<![A-Za-z0-9])" + _TK + r"(?![A-Za-z0-9])", m.group(1)):', "        if True:"),
 ("R09_blind_includes_weight_cols", RRG, "                if SIGNED_PCT_CELL_RE.match(c) and not any(\n                        bad in h.lower() for bad in PCT_HEADER_NO):", "                if SIGNED_PCT_CELL_RE.match(c) and not any(\n                        False for bad in PCT_HEADER_NO):"),
 ("R09b_blind_never", RRG, "                if SIGNED_PCT_CELL_RE.match(c) and not any(", "                if False and not any("),
 ("R09c_blind_unsigned_too", RRG, 'SIGNED_PCT_CELL_RE = re.compile(r"^\\s*(?:\\*\\*)?[+\\-−]\\d+', 'SIGNED_PCT_CELL_RE = re.compile(r"^\\s*(?:\\*\\*)?[+\\-−]?\\d+'),
 ("R10_pre_ex_tol_150", RRG, '                and abs(cash - step["cash"]) <= 1.0:', '                and abs(cash - step["cash"]) <= 150.0:'),
 ("R11_closed_holding_events_counted", RRG, "        if cur and a.ex_date < cur[0][0][:10]:", "        if False:"),
 ("R12_all_deltas_orphan", RRG, "    orphan = dar.unexplained_cash(cashd, dar.cash_step_totals(series))", "    orphan = dar.unexplained_cash(cashd, {})"),
 ("R12b_no_orphan", RRG, "    orphan = dar.unexplained_cash(cashd, dar.cash_step_totals(series))", "    orphan = {}"),
 ("R15_mention_loop_off", RRG, '        if set(keys) <= unresolved_published or not mention[tk]["pub"]:\n            continue', '        if True:\n            continue'),
 ("R16_mentions_no_quote_strip", RRG, "    stripped = [_strip_quote(ln) for ln in lines]", "    stripped = list(lines)"),
 ("R18_Y01_entitlement_check_removed", RRG, "        if dar._qty_at(qmap, a) <= 0:          # tài khoản này KHÔNG nắm giữ tại ngày chốt quyền", "        if False:"),
 ("R19_noise_not_skipped", RRG, '        if getattr(a, "kind", "") == "RATIO_NOISE":\n            continue', '        if False:\n            continue'),
 ("R20_cands_when_pct_found", RRG, "    return qty_i, pct_i, ([] if pct_i is not None else cands)", "    return qty_i, pct_i, cands"),
 ("R21_cand_any_cell", RRG, '            col = next((j for j in cands if j < len(cells) and "%" in cells[j]), None)', "            col = next((j for j in cands if j < len(cells)), None)"),
 ("R22_cand_last_not_first", RRG, '            col = next((j for j in cands if j < len(cells) and "%" in cells[j]), None)', '            col = next((j for j in reversed(cands) if j < len(cells) and "%" in cells[j]), None)'),
 ("R23_excluded_unres_blocks_by_qty", RRG, "        if k not in excluded_keys:\n            unres_tk.setdefault(k[0], []).append(k)", "        if True:\n            unres_tk.setdefault(k[0], []).append(k)"),
 ("R24_pre_ex_income_when_future", RRG, "            if pre[0] <= asof:\n", "            if True:\n"),
 ("R25_masked_step_skip_claimed_check", RRG, "            if i in claimed.get(tk, set()):\n                continue\n            if st[\"kind\"] in (\"buy\", \"other\"):", "            if st[\"kind\"] in (\"buy\", \"other\"):"),
 ("R26_absent_message_always", RRG, "    absent = [(k, v) for k, v in quiet if not (mention[k[0]][\"pub\"] or mention[k[0]][\"seen\"])]", "    absent = list(quiet)"),
 ("R27_bad_mult_ignored", RRG, '            bad_mult = abs(obs["q1"] - obs["q0"] * want_mult) > 1.5', "            bad_mult = False"),
 ("R28_bad_cash_ignored", RRG, '            bad_cash = abs(obs["cash"] - want_cash) > 1.0', "            bad_cash = False"),
 ("R29_addback_always_equal", RRG, "        if abs(deducted.get(tk, 0.0) - out.get(tk, 0.0)) > 1e-6:", "        if False:"),
 ("R30_tol_pp_050", RRG, "DEFAULT_TOL_PP = 0.15 ", "DEFAULT_TOL_PP = 0.50 "),
]

def sc(work, fname):
    env = dict(os.environ, PYTHONPATH=BIN, MIKE_BOT_TEST_MODE="1",
               WC_ROOT=os.path.join(work, "wcroot") if fname == RRG else REAL_ROOT)
    env.pop("TZ", None)
    p = subprocess.run([sys.executable, os.path.join(work, fname), "--selfcheck"], env=env, cwd=work,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = p.stdout
    crash = "Traceback (most recent call last)" in out
    nfail = len(re.findall(r"^\s*(?:❌|FAIL)", out, flags=re.M))
    return p.returncode, crash, nfail

def one(src, m):
    name, f, old, new = m[0], m[-3], m[-2], m[-1]
    n = src[f].count(old)
    if n != 1:
        return name, f, f"HỎNG({n})", ""
    work = tempfile.mkdtemp(prefix="arch2_mut_")
    try:
        os.makedirs(os.path.join(work, "wcroot", "data", "execution_logs"))
        open(os.path.join(work, "wcroot", "wc_env.sh"), "w").close()
        for g, text in src.items():
            open(os.path.join(work, g), "w", encoding="utf-8").write(text.replace(old, new) if g == f else text)
        res = [sc(work, f)] + ([sc(work, RRG)] if f == DAR else [])
    finally:
        shutil.rmtree(work, ignore_errors=True)
    if not any(r[0] for r in res):
        return name, f, "SỐNG", ""
    kinds = ["crash" if c else f"assert×{nf}" for rc, c, nf in res if rc]
    return name, f, "CHẾT", ",".join(kinds)

if __name__ == "__main__":
    src = {f: open(os.path.join(BIN, f), encoding="utf-8").read() for f in (DAR, RRG)}
    which = sys.argv[1] if len(sys.argv) > 1 else "mine"
    if which == "author":
        import total_return_mutants as trm
        muts = [(n, f, o, nw) for n, c, f, o, nw in trm.MUTANTS]
    else:
        muts = M
    with ThreadPoolExecutor(6) as pool:
        results = list(pool.map(lambda m: one(src, m), muts))
    for r in results:
        print(f"{r[2]:9s} {r[0]:45s} {r[1]:32s} {r[3]}")
    print("TỔNG", len(results), "| sống:", [r[0] for r in results if r[2] == "SỐNG"], "| hỏng:", [r[0] for r in results if r[2].startswith("HỎNG")],
          "| chết-do-crash:", [r[0] for r in results if "crash" in r[3] and "assert" not in r[3]])
