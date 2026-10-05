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
    ("trig_and_or", EN, "price_hit = ret <= TRIG_RET + EPS and idio", "price_hit = ret <= TRIG_RET + EPS or idio"),
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
    ("reply_unanchored", EN, '_REPLY_RE = re.compile(r"(?m)^\\s*(?:<@!?\\d+>\\s*)*(GIU',
     '_REPLY_RE = re.compile(r"(?m)\\s*(?:<@!?\\d+>\\s*)*(GIU'),
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
    ("retrigger_daily", DR, "            if tk in st[\"cases\"]:\n                continue", "            if False:\n                continue"),
    ("no_compress_check", DR, '    if not case.get("verdict") and not case.get("compressed") and room is not None \\',
     '    if False and not case.get("compressed") and room is not None \\'),
    ("no_timeout", DR, 'if v or now >= E.verdict_deadline(t0, case.get("compressed")):', 'if v:'),
    ("default_early", DR, 'if not case.get("decision") and case.get("reply_deadline") and now >= _p(case["reply_deadline"]):',
     'if not case.get("decision") and case.get("reply_deadline"):'),
    ("ignore_user", DR, '        if act and str(msg.get("id")) != str(dec.get("msg_id")):', '        if False:'),
    ("user_hold_no_stop", DR, '        if act == E.HOLD:                           # user GIỮ',
     '        if False:                           # user GIỮ'),
    ("carry_hold", DR, '        if c.get("status") in NO_CARRY:', '        if c.get("status") in TERMINAL:'),
    ("watch_dispatch", DR, '    watch_only = not case["holdings"] and not case["deferred_buys"]', '    watch_only = False'),
    ("verdict_overrides_exec", DR, '            if case["status"] not in ("INVESTIGATING", "AWAITING_REPLY"):',
     '            if False:'),
    ("holiday_run", DR, "if now.weekday() >= 5 or is_holiday(day) or not", "if now.weekday() >= 5 or not"),
    ("no_rebuy_short", EN, "NO_REBUY_SESSIONS = 10", "NO_REBUY_SESSIONS = 5"),
    ("carry_mode_kept", DR, '            ex.update({"mode": 0, "open": [], "ato_sent": False, "atc_sent": False})',
     '            ex.update({"open": [], "ato_sent": False, "atc_sent": False})'),
    ("defer_buys_off", DR, '    for b in u["buys"]:\n        try:', '    for b in []:\n        try:'),
    ("tag_off", DR, 'TAG = "[SHADOW]"', 'TAG = ""'),
]


def main():
    py = os.environ.get("DNA_PYEXE", "/home/trido/thanhdt/wc_venv/bin/python")
    res = []
    for name, f, a, b in M:
        d = tempfile.mkdtemp(prefix=f"ipw_mut_{name}_")
        os.makedirs(os.path.join(d, "bin"))
        for x in FILES:
            shutil.copy(os.path.join(BIN, x), os.path.join(d, "bin", x))
        p = os.path.join(d, "bin", f)
        s = open(p).read()
        n = s.count(a)
        if n != 1:
            res.append((name, f"BAD-PATTERN({n})"))
            shutil.rmtree(d)
            continue
        open(p, "w").write(s.replace(a, b))
        try:
            r = subprocess.run([py, os.path.join(d, "bin", "intraday_price_watch_selfcheck.py")],
                               capture_output=True, text=True, timeout=300,
                               env=dict(os.environ, IPW_FIXTURE=FIX))
            out = (r.stdout + r.stderr).strip().splitlines()
            res.append((name, "KILLED" if r.returncode != 0 else "SURVIVED", out[-1] if out else ""))
        except subprocess.TimeoutExpired:
            res.append((name, "KILLED(timeout)", ""))
        shutil.rmtree(d)
    k = sum(1 for r in res if r[1].startswith("KILLED"))
    for r in res:
        print(f"{r[1]:16s} {r[0]:24s} {r[2] if len(r) > 2 else ''}")
    print(f"\n{k}/{len(res)} đột biến bị giết; SURVIVED={[r[0] for r in res if r[1] == 'SURVIVED']}; "
          f"BAD={[r[0] for r in res if r[1].startswith('BAD')]}")
    sys.exit(0 if k == len(res) else 1)


if __name__ == "__main__":
    main()
