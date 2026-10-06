#!/usr/bin/env python3
"""Chạy đột biến các cổng chính của intraday_price_watch trong sandbox /tmp (không đụng repo).
Mỗi đột biến: chép 3 file bin/ sang /tmp, thay ĐÚNG 1 chỗ (assert đếm =1), chạy selfcheck.
KILLED = selfcheck exit≠0. Chạy: $DNA_PYEXE mutation_run.py"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
BIN = os.path.join(REPO, "bin")
FILES = ("intraday_cutloss_engine.py", "intraday_price_watch.py", "intraday_price_watch_selfcheck.py")
FIX = os.path.join(HERE, "fixtures", "replay_bars.json")
EN, DR = "intraday_cutloss_engine.py", "intraday_price_watch.py"

M = [
    ("trig_ret", EN, "TRIG_RET = -0.05", "TRIG_RET = -0.06"),
    ("trig_idio", EN, "TRIG_IDIO = -0.04", "TRIG_IDIO = -0.03"),
    ("trig_and_or", EN, "price_hit = ret <= ret_thr + EPS and idio", "price_hit = ret <= ret_thr + EPS or idio"),
    ("trig_no_floor", EN, '"hit": bool(at_floor or price_hit)', '"hit": bool(price_hit)'),
    ("vni_missing_drop", EN, "idio = ret - vni_ret if vni_ret is not None else ret",
     "idio = ret - vni_ret if vni_ret is not None else 0.0"),
    ("disc_sells_unclear", EN, "    if book in (DISCRETIONARY, UNKNOWN):\n        return HOLD", "    pass"),
    ("unclear_sell_all", EN, "    if verdict == UNCLEAR:\n        return SELL_HALF", "    if verdict == UNCLEAR:\n        return SELL_ALL"),
    ("broken_hold", EN, "    if verdict == BROKEN:\n        return SELL_ALL", "    if verdict == BROKEN:\n        return HOLD"),
    ("invest_compressed", EN, "INVEST_MIN, INVEST_MIN_COMPRESSED = 20, 10", "INVEST_MIN, INVEST_MIN_COMPRESSED = 20, 20"),
    ("invest_20_30", EN, "INVEST_MIN, INVEST_MIN_COMPRESSED = 20, 10", "INVEST_MIN, INVEST_MIN_COMPRESSED = 30, 10"),
    ("reply_30", EN, "REPLY_MIN, REPLY_MIN_COMPRESSED = 30, 15", "REPLY_MIN, REPLY_MIN_COMPRESSED = 20, 15"),
    ("reply_compressed", EN, "REPLY_MIN, REPLY_MIN_COMPRESSED = 30, 15", "REPLY_MIN, REPLY_MIN_COMPRESSED = 30, 30"),
    ("room_compress", EN, "ROOM_COMPRESS = 0.03", "ROOM_COMPRESS = 0.01"),
    ("reply_bot_ok", EN, '        if m.get("is_bot"):\n            continue', '        if False:\n            continue'),
    ("reply_any_ticker", EN, "            if tk != ticker.upper():\n                continue",
     "            if False:\n                continue"),
    ("reply_since", EN, "if ts is None or ts < since or", "if ts is None or"),
    ("reply_earliest", EN, 'if best is None or ts >= best[1]["created_at"]:', 'if best is None:'),
    ("reply_unanchored", EN, '_REPLY_HEAD = r"(?m)^\\s*', '_REPLY_HEAD = r"(?m)\\s*'),
    ("reply_half_as_all", EN, 'act = SELL_HALF if verb.startswith("BAN") and "50" in verb',
     'act = SELL_ALL if verb.startswith("BAN") and "50" in verb'),
    ("upcom_atc_kept", EN, '        if hose_phase == "ATC" or (hose_phase == "CLOSED"', '        if (hose_phase == "CLOSED"'),
    ("hnx_ato_kept", EN, '    if hose_phase == "ATO":\n        return "MORNING"', '    if False:\n        return "MORNING"'),
    ("upcom_atc_api", EN, '            return None, "UPCOM không có ATC', '            return "ATC", "UPCOM không có ATC'),
    ("upcom_mp_api", EN, '            return None, "UPCOM chỉ LO', '            return "MTL", "UPCOM chỉ LO'),
    ("mp_verified_claim", EN, 'return "MTL", "CHƯA xác minh', 'return "MTL", "đã xác minh'),
    ("mode_no_depth", EN, "or depth2 < q:", ":"),
    ("mode_room_urgent", EN, "ROOM_FAST, ROOM_URGENT = 0.03, 0.015", "ROOM_FAST, ROOM_URGENT = 0.03, 0.0"),
    ("mode_speed", EN, "SPEED_FAST = -0.01", "SPEED_FAST = -0.02"),
    ("mode_stuck_off", EN, "    if at_floor_no_bid:\n        return 4", "    if False:\n        return 4"),
    ("escalate_off", EN, "    return max(prev or 0, new)", "    return new"),
    ("botstop_off", EN, "    if bot_stop:\n        events.append", "    if False:\n        events.append"),
    ("lunch_off", EN, '    if phase == "LUNCH":\n        events.append', '    if False:\n        events.append'),
    ("t2_ignored", EN, 'sell_left = max(0, int(sellable) - ex["sold"])', 'sell_left = max(0, int(ex["target"]))'),
    ("atc_repeat", EN, '        if not ex["atc_sent"]:', '        if True:'),
    ("ato_off", EN, '    if phase == "ATO":\n        if not ex["ato_sent"]:', '    if phase == "ATO_X":\n        if not ex["ato_sent"]:'),
    ("tranche_all", EN, "frac = max(f for m, f in MODE1_TRANCHES if mins >= m - EPS)", "frac = 1.0"),
    ("depth_share", EN, "MODE1_DEPTH_SHARE = 0.30", "MODE1_DEPTH_SHARE = 1.0"),
    ("urgent_at_bid", EN, '                _place(ex, "LO", floor, even, now, snap, exchange, "even", intents,\n                       "LO giá sàn',
     '                _place(ex, "LO", best_bid or floor, even, now, snap, exchange, "even", intents,\n                       "LO giá sàn'),
    ("floor_requeue", EN, "keep=lambda o: abs(o[\"price\"] - floor) < EPS)", "keep=None)"),
    ("floor_round_down", EN, "return n * t if abs(n * t - raw) < EPS else (n + 1) * t", "return n * t"),
    ("match_any_price", EN, "if left <= 0 or p is None or p < price - EPS:", "if left <= 0 or p is None:"),
    ("auction_wrong_kind", EN, 'res = (snap.get("auctions") or {}).get(o["kind"])', 'res = (snap.get("auctions") or {}).get("ATO")'),
    ("auction_no_wait", EN, "                if age <= AUCTION_RESULT_WAIT_MIN:", "                if False:"),
    ("resting_px_floor", EN, 'max(o["price"], last)', 'o["price"]'),
    ("ro_allow_place", DR, 'ALLOWED = frozenset({"secdef",', 'ALLOWED = frozenset({"place_order", "secdef",'),
    ("scan_every_min", DR, "SCAN_EVERY_MIN = 15", "SCAN_EVERY_MIN = 1"),
    ("retrigger_daily", DR, "        if tk in st[\"cases\"]:\n            continue", "        if False:\n            continue"),
    ("no_compress_check", DR, '    if not case.get("verdict") and not case.get("compressed") and room is not None \\',
     '    if False and not case.get("compressed") and room is not None \\'),
    ("no_timeout", DR, 'if v or now >= E.verdict_deadline(t0, case.get("compressed")):', 'if v:'),
    ("default_early", DR, 'if not case.get("decision") and case.get("reply_deadline") and now >= _p(case["reply_deadline"]):',
     'if not case.get("decision") and case.get("reply_deadline"):'),
    ("ignore_user", DR, '        if act and str(msg.get("id")) != str(dec.get("msg_id")):', '        if False:'),
    ("user_hold_no_stop", DR, '        if act == E.HOLD:                           # user GIỮ',
     '        if False:                           # user GIỮ'),
    ("carry_hold", DR, '        if c.get("status") in NO_CARRY:', '        if c.get("status") in TERMINAL:'),
    ("watch_dispatch", DR, '    case["watch_only"] = not case["holdings"] and not case["deferred_buys"]',
     '    case["watch_only"] = False'),
    ("verdict_overrides_exec", DR, '            if case["status"] not in ("INVESTIGATING", "AWAITING_REPLY"):',
     '            if False:'),
    ("holiday_run", DR, "if now.weekday() >= 5 or is_holiday(day):", "if now.weekday() >= 5:"),
    ("no_rebuy_short", EN, "NO_REBUY_SESSIONS = 10", "NO_REBUY_SESSIONS = 5"),
    ("carry_mode_kept", DR, '            ex.update({"mode": 0, "open": [], "ato_sent": False, "atc_sent": False})',
     '            ex.update({"open": [], "ato_sent": False, "atc_sent": False})'),
    ("defer_buys_off", DR, '    for b in u["buys"]:\n        try:', '    for b in []:\n        try:'),
    ("tag_off", DR, 'TAG = "[SHADOW]"', 'TAG = ""'),
    # ---------------- r2: 6 đột biến reviewer thấy SỐNG ở r1
    ("R_flock_off", DR, "            fcntl.flock(lockf, fcntl.LOCK_EX | fcntl.LOCK_NB)", "            pass"),
    ("R_presave_dispatch_off", DR, "                    _save(deps, day, st)                        # at-most-once",
     "                    pass  # at-most-once"),
    ("R_acct_filter_off", DR, 'str(qget(p, "accountno", "account_no")) != str(account_id):', "False:"),
    ("R_mention_off", DR, '(owner_mention(CHANNELS) if mention else "")', '""'),
    ("R_mode2_cancel_off", EN, "        _cancel_open(ex, now, intents)              # đặt lại mỗi 1'",
     "        pass  # đặt lại mỗi 1'"),
    # "bỏ lưu state trước notify" ở r2 = 2 chỗ ghi đĩa trước khi gửi (dự kiến DƯ THỪA nhau — xem báo cáo)
    ("R_presave_notify_flush_off", DR, '        m["attempts"] += 1\n        _save(deps, day, st)\n',
     '        m["attempts"] += 1\n'),
    ("R_presave_notify_both_off", DR, '        m["attempts"] += 1\n        _save(deps, day, st)\n',
     '        m["attempts"] += 1\n', '    _eod_summary(st, now, deps)\n    _save(deps, day, st)\n',
     '    _eod_summary(st, now, deps)\n'),
    ("R_presave_notify_all_off", DR, '        m["attempts"] += 1\n        _save(deps, day, st)\n',
     '        m["attempts"] += 1\n', '    _eod_summary(st, now, deps)\n    _save(deps, day, st)\n',
     '    _eod_summary(st, now, deps)\n', '    if changed:\n        _save(deps, day, st)\n\n\ndef _apply_decision',
     '    pass\n\n\ndef _apply_decision'),
    # ---------------- r2: mục chặn 1-7
    ("S1_from_taylor", DR, 'DISPATCH_FROM_ID = "intraday_watch"', 'DISPATCH_FROM_ID = "Taylor"'),
    ("S1_retries", DR, '"--retries", "0", ', ''),
    ("S2_timeout_uncaught", DR, "    except subprocess.TimeoutExpired:\n", "    except ZeroDivisionError:\n"),
    ("S2_oserror_uncaught", DR, '    except OSError as e:\n        return None, f"dispatch.sh không chạy được',
     '    except ZeroDivisionError as e:\n        return None, f"dispatch.sh không chạy được'),
    ("S2_t0_lies", DR, '    elif inv.get("job"):\n        inv_line = (f"  ⇒ đang điều tra', '    elif True:\n        inv_line = (f"  ⇒ đang điều tra'),
    ("S2_t0_no_reason", DR, "{inv.get('skipped') or inv.get('note') or '?'}", ""),
    ("S2_job_dead_off", DR, "            if js in JOB_DEAD:", "            if False:"),
    ("S3_no_t0", DR, '"late": now.time() >= LATE_TRIGGER, "t0_pending": True}', '"late": now.time() >= LATE_TRIGGER, "t0_pending": False}'),
    ("S3_t0_mention_off", DR, '                    mention=True, now=now)\n            case["t0_pending"] = False',
     '                    mention=False, now=now)\n            case["t0_pending"] = False'),
    ("S3_flush_ignore_result", DR, "        bad = {ch: info for ch, (ok, info) in res.items() if not ok}", "        bad = {}"),
    ("S3_flush_resend_all", DR, '        m["left"] = [ch for ch in m["left"] if ch in bad]', '        m["left"] = list(m["left"])'),
    ("S3_budget_off", DR, '        if deps.over_budget():\n            log_event(deps.state_dir, day, "BUDGET", now=now, where="pending_work"',
     '        if False:\n            log_event(deps.state_dir, day, "BUDGET", now=now, where="pending_work"'),
    ("S3_outbox_carry_off", DR, 'st["outbox"] = [m for m in ((prev or {}).get("outbox") or []) if m.get("left")',
     'st["outbox"] = [m for m in [] if m.get("left")'),
    ("S4_mw_off", DR, "    reason = E.market_wide_reason([h[2] for h in hits])", "    reason = None"),
    ("S4_mw_vni_off", EN, '    if any(h.get("vni_missing") for h in hits):', '    if False:'),
    ("S4_mw_hits4", EN, "MARKET_WIDE_MIN_HITS = 3", "MARKET_WIDE_MIN_HITS = 4"),
    ("S4_mw_hits2", EN, "MARKET_WIDE_MIN_HITS = 3", "MARKET_WIDE_MIN_HITS = 2"),
    ("S4_mw_floor3", EN, "MARKET_WIDE_MIN_FLOOR = 2", "MARKET_WIDE_MIN_FLOOR = 3"),
    ("S4_mw_realert", DR, '        new = [h for h in hits if h[0] not in mw]', '        new = list(hits)'),
    ("S4_cap_scan_off", DR, '    if (st.get("dispatch_by_scan") or {}).get(case["t0"], 0) >= MAX_DISPATCH_PER_SCAN:', '    if False:'),
    ("S4_cap_day_off", DR, '    if _stats(st)["dispatches"] >= MAX_DISPATCH_PER_DAY:', '    if False:'),
    ("S4_halt_off", DR, '    if st.get("dispatch_halted"):\n        return False', '    if False:\n        return False'),
    ("S4_priority_off", DR, 'sorted(st["cases"].items(), key=lambda kv: -_case_value(kv[1]))', 'sorted(st["cases"].items())'),
    ("S5_quote_health_off", DR, "    if n_q >= 4 and n_err / n_q > QUOTE_ERR_ALERT:", "    if False:"),
    ("S5_ccdb_health_off", DR, '            health_alert(st, "ccdb", f"không', '            (lambda *a, **k: None)(st, "ccdb", f"không'),
    ("S5_health_ratelimit_off", DR, "    if last and (now - _p(last)).total_seconds() < HEALTH_ALERT_EVERY_MIN * 60:", "    if False:"),
    ("S5_init_alert_off", DR, '        crash_alert(a.state_dir, "init", traceback.format_exc(), notifier)', '        pass'),
    ("S5_crash_alert_off", DR, '        crash_alert(a.state_dir, "crash", traceback.format_exc(), notifier)', '        pass'),
    ("S5_crash_once_off", DR, "    if os.path.exists(flag):\n        return False", "    if False:\n        return False"),
    ("S5_eod_off", DR, '    if now.time() < EOD_SUMMARY_AT or st.get("eod_summary_sent"):', '    if True:'),
    ("S5_eod_repeat", DR, '    if now.time() < EOD_SUMMARY_AT or st.get("eod_summary_sent"):', '    if now.time() < EOD_SUMMARY_AT:'),
    ("S5_pos_err_off", DR, '            if errors is not None:\n                errors.append', '            if False:\n                errors.append'),
    ("S5_chfail_off", DR, "                    if alive:", "                    if False:"),
    ("S6_reply_no_prefix", DR, "act, msg = E.parse_reply(msgs, tk, since=t0, prefix=REPLY_PREFIX)",
     "act, msg = E.parse_reply(msgs, tk, since=t0, prefix=None)"),
    ("S6_note_off", DR, 'SHADOW_NOTE = "ĐÂY LÀ CHẠY THỬ (SHADOW), KHÔNG CÓ LỆNH THẬT"', 'SHADOW_NOTE = ""'),
    ("S6_engine_prefix_off", EN, '    rx = _reply_re(_fold(prefix) if prefix else None)', '    rx = _reply_re(None)'),
    # ---------------- r2: mặc định an toàn a-d
    ("Da_non_agent_sells", EN, '    if source != "agent":\n        return NON_AGENT_DEFAULT', '    if False:\n        return NON_AGENT_DEFAULT'),
    ("Da_const_half", EN, "NON_AGENT_DEFAULT = HOLD ", "NON_AGENT_DEFAULT = SELL_HALF "),
    ("Da_src_mislabel", DR, '                src = "timeout" if job else "no_dispatch"', '                src = "agent"'),
    ("Db_default_off", EN, "    if no_auto_sell:\n        return HOLD", "    if False:\n        return HOLD"),
    ("Db_exec_off", DR, '        if h.get("no_auto_sell") and act != E.HOLD:', '        if False:'),
    ("Db_restricted_off", DR, "if t in restricted else None)", "if False else None)"),
    ("Dc_late_off", DR, '(case.get("late") and now.date() == _p(case["t0"]).date()) or rd.time()', '(False) or rd.time()'),
    ("Dc_1415_off", DR, "or rd.time() > NO_EOD_DEFAULT_AFTER \\", "or False \\"),
    ("Dc_reminder_off", DR, "        fn = _run_reminder", '        return {"skipped": "reminder-off"}'),
    ("Dc_reminder_dupe", DR, 'mention=True, key=f"remind:{tk}:{day}", now=now)', 'mention=True, key=None, now=now)'),
    ("Dd_alt_off", DR, "    if alt:\n        log_event", "    if False:\n        log_event"),
    ("Dd_rel_hose", EN, 'REL_TRIG = {"HOSE": -0.03,', 'REL_TRIG = {"HOSE": -0.05,'),
    ("Dd_rel_idio", EN, "REL_IDIO = -0.03", "REL_IDIO = -0.02"),
    ("Dd_latency_off", DR, '            case["verdict"]["latency_min"] = lat', '            case["verdict"]["latency_min"] = None'),
    # ---------------- phân loại book
    ("B_c30v_label", DR, '"CUSTOM30V_PARKING": "CUSTOM30V", ', ""),
    ("B_prefixes_plan_only", DR, '_PLAN_PREFIXES = ("plan", "park_add", "jit_unpark", "park_trim")', '_PLAN_PREFIXES = ("plan",)'),
    ("B_bootstrap_off", DR, '            if b and p.get("ticker"):\n                books[p["ticker"].upper()] = b',
     '            if False:\n                books[p["ticker"].upper()] = b'),
    ("B_sell_overrides", DR, "        books.setdefault(t, b)", "        books[t] = b"),
]


def main():
    py = os.environ.get("DNA_PYEXE", "/home/trido/thanhdt/wc_venv/bin/python")
    res = []
    from concurrent.futures import ThreadPoolExecutor

    def one(m):
        name, f, pairs = m[0], m[1], list(zip(m[2::2], m[3::2]))
        d = tempfile.mkdtemp(prefix=f"ipw_mut_{name}_")
        try:
            os.makedirs(os.path.join(d, "bin"))
            for x in FILES:
                shutil.copy(os.path.join(BIN, x), os.path.join(d, "bin", x))
            p = os.path.join(d, "bin", f)
            s = open(p).read()
            for a, b in pairs:                    # mỗi chỗ thay phải khớp ĐÚNG 1 lần
                n = s.count(a)
                if n != 1:
                    return (name, f"BAD-PATTERN({n})", a[:60])
                s = s.replace(a, b)
            open(p, "w").write(s)
            try:
                r = subprocess.run([py, os.path.join(d, "bin", "intraday_price_watch_selfcheck.py")],
                                   capture_output=True, text=True, timeout=300,
                                   env=dict(os.environ, IPW_FIXTURE=FIX))
                out = (r.stdout + r.stderr).strip().splitlines()
                return (name, "KILLED" if r.returncode != 0 else "SURVIVED", out[-1] if out else "")
            except subprocess.TimeoutExpired:
                return (name, "KILLED(timeout)", "")
        finally:
            shutil.rmtree(d, ignore_errors=True)
    with ThreadPoolExecutor(max_workers=int(os.environ.get("MUT_WORKERS", "8"))) as pool:
        res = list(pool.map(one, M))
    # Đột biến TƯƠNG ĐƯƠNG đã phân tích (không phải lỗ test): 3 chỗ ghi đĩa trước khi gửi tin dư thừa
    # nhau (lưu cuối process_case / lưu trước flush / lưu trong flush) + cờ t0_pending tính lại được ⇒
    # bỏ 1-2 chỗ không đổi hành vi; bỏ CẢ 3 (R_presave_notify_all_off) thì selfcheck phải giết.
    EQUIV = {"R_presave_notify_flush_off", "R_presave_notify_both_off"}
    k = sum(1 for r in res if r[1].startswith("KILLED"))
    for r in res:
        print(f"{r[1]:16s} {r[0]:24s} {r[2] if len(r) > 2 else ''}")
    print(f"\n{k}/{len(res)} đột biến bị giết; SURVIVED={[r[0] for r in res if r[1] == 'SURVIVED']}; "
          f"BAD={[r[0] for r in res if r[1].startswith('BAD')]}")
    bad = [r[0] for r in res if not r[1].startswith("KILLED") and r[0] not in EQUIV]
    print(f"tương đương (đã phân tích, chấp nhận): {sorted(EQUIV & {r[0] for r in res if r[1] == 'SURVIVED'})}")
    sys.exit(0 if not bad else 1)


if __name__ == "__main__":
    main()
