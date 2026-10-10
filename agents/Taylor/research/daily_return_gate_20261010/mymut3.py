import sys
sys.argv = [sys.argv[0]]
exec(open("/tmp/arch_rev2/mymut.py").read().split('if __name__ == "__main__":')[0])
M3 = [
 ("N01_settle_single_lot_only", DAR, "    for n in range(1, len(lots) + 1):", "    for n in range(1, 2):"),
 ("N02_settle_tol_100k", DAR, "            if abs(sum(lots[i] for i in idx) - paid) <= 1.0:", "            if abs(sum(lots[i] for i in idx) - paid) <= 100000.0:"),
 ("N03_initial_outstanding_ignored", DAR, "    lots = [float(series[0][1])] if series and series[0][1] > 0 else []", "    lots = []"),
 ("N03b_lots_cap_2", DAR, "    if len(lots) > 16:", "    if len(lots) > 2:"),
 ("N05_holding_from_ledger_start", DAR, "        first = max((i for i, r in enumerate(rows) if r[0][:10] < lo), default=0)", "        first = 0"),
 ("N05b_holding_to_ledger_end", DAR, "        last = min((i for i, r in enumerate(rows) if r[0][:10] >= hi), default=len(rows) - 1)", "        last = len(rows) - 1"),
 ("N06_step5_window_only_ex_day", DAR, 'code, text = cash_witness(L["cashd"], L["orphan"], lo + "T00:00:00", hi + "T00:00:00")', 'code, text = cash_witness(L["cashd"], L["orphan"], hi + "T00:00:00", hi + "T00:00:00")'),
 ("N06b_step5_window_only_cum_day", DAR, 'code, text = cash_witness(L["cashd"], L["orphan"], lo + "T00:00:00", hi + "T00:00:00")', 'code, text = cash_witness(L["cashd"], L["orphan"], lo + "T00:00:00", lo + "T00:00:00")'),
 ("N07_step5_also_when_spans", DAR, "        if not spans:\n            code, text = cash_witness", "        if True:\n            code, text = cash_witness"),
 ("N08_lag_sufficiency_ignores_own", DAR, "    got = own * (1.0 + float(late.ratio_jump or 0.0))", "    got = (1.0 + float(late.ratio_jump or 0.0))"),
 ("N09_lag_necessity_tight", DAR, "    if abs(own / want - 1.0) <= LAG_TOL:\n        return False", "    if abs(own / want - 1.0) <= 0.0005:\n        return False"),
 ("N09b_lag_necessity_loose", DAR, "    if abs(own / want - 1.0) <= LAG_TOL:\n        return False", "    if abs(own / want - 1.0) <= 0.2:\n        return False"),
 ("N13_ledger_all_deltas_orphan", DAR, '            "orphan": unexplained_cash(cashd, cash_step_totals(series))}', '            "orphan": unexplained_cash(cashd, {})}'),
 ("N13b_ledger_no_orphan", DAR, '            "orphan": unexplained_cash(cashd, cash_step_totals(series))}', '            "orphan": {}}'),
 ("N15_opening_pair_from_first_record", DAR, "max((t for t in record_ts if t < ts), default=ts)", "min((t for t in record_ts if t < ts), default=ts)"),
 ("N16_entitle_unknown_status_ignored", DAR, '        if status == "unknown":\n            a.entitled, a.entitled_note = "unknown", why', '        if False:\n            a.entitled, a.entitled_note = "unknown", why'),
 ("N22_blind_lo_inclusive", DAR, 'if not (any(t[:10] < lo for t in L["ts"]) and any(t[:10] >= hi for t in L["ts"])):', 'if not (any(t[:10] <= lo for t in L["ts"]) and any(t[:10] >= hi for t in L["ts"])):'),
 ("N22b_blind_hi_exclusive", DAR, 'if not (any(t[:10] < lo for t in L["ts"]) and any(t[:10] >= hi for t in L["ts"])):', 'if not (any(t[:10] < lo for t in L["ts"]) and any(t[:10] > hi for t in L["ts"])):'),
 ("N24_drops_empty", DAR, "    out.drops = odd\n", "    out.drops = []\n"),
 ("N25_witness_orphan_window_exclusive", DAR, "    near = {d: v for d, v in orphan.items() if lo <= _d.date.fromisoformat(d) <= hi}", "    near = {d: v for d, v in orphan.items() if lo < _d.date.fromisoformat(d) < hi}"),
 ("N26_meets_strict", DAR, "        return t0[:10] <= hi and t1[:10] >= lo", "        return t0[:10] < hi and t1[:10] > lo"),
 ("N27_lagged_root_wrong", DAR, "    cands = [(a, (v.ticker, v.ex_date)) for a, v in lagged] + [(a, None) for a in shaped]", "    cands = [(a, None) for a, v in lagged] + [(a, None) for a in shaped]"),
 ("N28_scope_wrong_key", DAR, 'return bq_corp_events_window(sc["tickers"], sc["start"], sc["end"]).get((ticker, ex_date))', 'return bq_corp_events_window(sc["tickers"], sc["start"], sc["end"]).get((ticker, ex_date)) or None'),
 ("N29_asked_only_first", DAR, "    asked = set(tickers)\n", "    asked = set(list(tickers)[:1])\n"),
 # gate
 ("N30_hidden_paid_for_seen_steps", RRG, '        if obs["kind"] == "hidden":\n            q_cum', '        if True:\n            q_cum'),
 ("N31_hidden_paid_latest_qty", RRG, "            q_cum = [r[1] for r in cur if r[0][:10] <= a.last_cum_date]", "            q_cum = [r[1] for r in cur]"),
 ("N33_gate_record_ts_empty", RRG, "    record_ts = sorted({r[0] for rows in series.values() for r in rows})", "    record_ts = []"),
 ("N37_hidden_paid_clears_all_orphans", RRG, "        orphan = dar.unexplained_cash(cashd, totals)", "        orphan = {}"),
 ("N38_hidden_paid_overwrites_totals", RRG, "            totals[d] = totals.get(d, 0.0) + v", "            totals[d] = v"),
 ("N39_opening_pairs_all_series", RRG, "        for before, opened in dar.opening_pairs(cur, record_ts):", "        for before, opened in dar.opening_pairs(cur, record_ts)[:0] or []:"),
 ("N40_h1c_only_first", RRG, "    matched_tk = {tk for tk, qty, _p in rows if (tk, qty) in expected}", "    matched_tk = {tk for tk, qty, _p in rows}"),
 ("N41_nocover_ignores_prose_tk", RRG, "                    if v[5] > 0 and k not in seen and k[0] not in prose_tk]", "                    if v[5] > 0 and k not in seen]"),
 ("N42_later_stock_any_kind", RRG, '    if step["kind"] not in ("stock", "cash+stock"):\n        return ""', '    if False:\n        return ""'),
 ("N43_mask_doubt_swapped", RRG, 'code, text = dar.cash_witness(cashd, orphan, st["ts0"], st["ts"])', 'code, text = dar.cash_witness(cashd, orphan, st["ts"], st["ts"])'),
]
src = {f: open(os.path.join(BIN, f), encoding="utf-8").read() for f in (DAR, RRG)}
with ThreadPoolExecutor(6) as pool:
    results = list(pool.map(lambda m: one(src, m), M3))
for r in results: print(f"{r[2]:9s} {r[0]:42s} {r[1]:30s} {r[3]}")
print("TỔNG", len(results), "| sống:", [r[0] for r in results if r[2] == "SỐNG"], "| hỏng:", [r[0] for r in results if r[2].startswith("HỎNG")], "| chỉ-sập:", [r[0] for r in results if "crash" in r[3] and "assert" not in r[3]])
