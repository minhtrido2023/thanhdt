#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Self-check: nhánh DISCRETIONARY của auto_exit_inject.py + `auto_exit_rules.disc_exit_triggers`
+ sàn bán tuyệt đối `hard_sell_floor_vnd` (plan.py/executor.py) — job Taylor_20261106_072056.

Luật (user chốt 06/11/2026 14:19 ICT): đóng ≥ +10% giá vốn broker ⇒ đề xuất SELL; ≤ −10% ⇒ đề xuất SELL
để user xác nhận + notify; đủ 25 phiên kể từ ngày vào ⇒ đề xuất SELL. Selfcheck test ngưỡng + biên đúng
±10,00% bằng giá THẬT (float), T+2, fail-safe, idempotent, refuse-approved, config không hardcode mã,
executor sàn bán (LO + ATC). Mutant (`DISC_MUTANT=<id>`) phá từng guard ⇒ phải ĐỎ.

Cần chạy với WC_ROOT trỏ cây WorkingClaude chứa bản sửa `auto_exit_rules.py`/`trading_bot/` (worktree
repo ngoài) — xem lệnh trong báo cáo. Không chạm dữ liệu thật (sandbox + monkeypatch, AUTO_EXIT_TEST_MODE).

Chạy: WC_ROOT=<cây> python3 bin/auto_exit_disc_selfcheck.py
"""
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile
import types

os.environ["AUTO_EXIT_TEST_MODE"] = "1"   # §5b — không bus/Discord thật
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")   # §5b — import Executor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wc_paths  # noqa: E402
WC_ROOT = wc_paths.find_wc_root(__file__)
sys.path.insert(0, WC_ROOT)

# id -> (đường dẫn tương đối, tên module, chuỗi gốc, chuỗi đột biến)
MUTANTS = {
    "M1_target_strict": (os.path.join(WC_ROOT, "auto_exit_rules.py"), "auto_exit_rules",
                         "if pnl_pct >= target_pct - DISC_EPS:", "if pnl_pct > target_pct:"),
    "M2_stop_strict": (os.path.join(WC_ROOT, "auto_exit_rules.py"), "auto_exit_rules",
                       "if pnl_pct <= -stop_pct + DISC_EPS:", "if pnl_pct < -stop_pct:"),
    "M3_stop_no_eps": (os.path.join(WC_ROOT, "auto_exit_rules.py"), "auto_exit_rules",
                       "if pnl_pct <= -stop_pct + DISC_EPS:", "if pnl_pct <= -stop_pct:"),
    "M4_time_strict": (os.path.join(WC_ROOT, "auto_exit_rules.py"), "auto_exit_rules",
                       "sessions_held >= max_sessions", "sessions_held > max_sessions"),
    "M5_no_t2_gate": (os.path.join(HERE, "auto_exit_inject.py"), "auto_exit_inject",
                      "if gate or n < DISC_T2_SESSIONS:", "if gate or n < 0:"),
    "M6_no_entry_check": (os.path.join(HERE, "auto_exit_inject.py"), "auto_exit_inject",
                          'if lot.get("entry_date") != e["entry_date"]:', "if False:"),
    "M7_no_buy_conflict": (os.path.join(HERE, "auto_exit_inject.py"), "auto_exit_inject",
                           'if any(o.get("ticker") == tk and o.get("side") == "buy" for o in plan.get("orders", [])):',
                           "if False:"),
    "M8_floor_no_guard": (os.path.join(WC_ROOT, "trading_bot", "executor.py"), "trading_bot.executor",
                          "if hard_floor and px < hard_floor:", "if False:"),
    "M9_floor_no_atc_skip": (os.path.join(WC_ROOT, "trading_bot", "executor.py"), "trading_bot.executor",
                             "            if self._hard_sell_floor(o):\n                # Đối xứng",
                             "            if False:\n                # Đối xứng"),
    "M10_no_floor_field": (os.path.join(WC_ROOT, "trading_bot", "plan.py"), "trading_bot.plan",
                           "    hard_sell_floor_vnd: float = None\n", ""),
    "M11_lot_qty_unchecked": (os.path.join(HERE, "auto_exit_inject.py"), "auto_exit_inject",
                              'if lot["qty"] > pos["qty"]:', "if False:"),
}


def _load_mutant(mid):
    path, modname, old, new = MUTANTS[mid]
    src = open(path, encoding="utf-8").read()
    if src.count(old) != 1:
        raise SystemExit(f"mutant {mid}: chuỗi gốc xuất hiện {src.count(old)} lần (≠1) — bảng đột biến lỗi thời")
    if modname.startswith("trading_bot."):
        import trading_bot  # noqa: F401  — package phải có trước khi exec submodule
    mod = types.ModuleType(modname)
    mod.__file__ = path
    if "." in modname:
        mod.__package__ = modname.rsplit(".", 1)[0]
    sys.modules[modname] = mod
    exec(compile(src.replace(old, new), path, "exec"), mod.__dict__)
    if modname == "trading_bot.plan":
        import trading_bot
        trading_bot.plan = mod


if os.environ.get("DISC_MUTANT"):
    _m = MUTANTS[os.environ["DISC_MUTANT"]][1]
    if _m == "auto_exit_inject":
        import auto_exit_rules  # noqa: F401
    _load_mutant(os.environ["DISC_MUTANT"])

import auto_exit_rules as rules  # noqa: E402
import auto_exit_inject as aei  # noqa: E402
import portfolio_status as ps  # noqa: E402
import trading_bot.plan as tbplan  # noqa: E402
from trading_bot.executor import Executor  # noqa: E402
from trading_bot.vn_market import next_trading_day  # noqa: E402

PASS, FAIL = [], []
ACCOUNT, ACCOUNT_NO = "SelfcheckAcct", "9999999999"


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'} — {name}" + (f"  [{detail}]" if detail else ""))


def nth_session_after(start, n):
    d = start
    for _ in range(n):
        d = next_trading_day(d)
    return d


def prev_session(d, n=1):
    """Phiên giao dịch thứ n TRƯỚC d (đi lùi tới khi next_trading_day khớp)."""
    for _ in range(n):
        c = d - dt.timedelta(days=1)
        while next_trading_day(c) != d:
            c -= dt.timedelta(days=1)
        d = c
    return d


# ---------------------------------------------------------------- sandbox
def rule_entry(tk="FPT", entry="2026-11-06", **kw):
    e = {"ticker": tk, "account": ACCOUNT, "book": "DISCRETIONARY_SPECIAL", "entry_date": entry,
         "target_pct": 0.10, "stop_pct": 0.10, "max_sessions": 25, "thin_liquidity": False}
    e.update(kw)
    return e


def run(signal, plan_date, positions, rules_doc, lots=None, lots_ok=True, lots_blocked=None,
        orders=None, approved_by=None, dry_run=False, raw_rules=None, repeat=1):
    """process_account THẬT trên sandbox. positions: {tk:(qty,cost,mp[,sellable])} hoặc None (không ghi
    dnse_raw). lots: {tk: [(qty, entry_date), ...]} cho sổ lô DISC (mock book_lot_snapshot).
    Trả (rc, plan, disc_sells, notes_entries, stdout_calls)."""
    td = tempfile.mkdtemp(prefix="disc_exit_selfcheck_")
    exec_dir, plan_dir = os.path.join(td, "exec"), os.path.join(td, "plans")
    os.makedirs(exec_dir)
    os.makedirs(plan_dir)
    if positions is not None:
        rec = {"kind": "positions", "account_no": ACCOUNT_NO, "payload": {"positions": [
            {"symbol": tk, "openQuantity": v[0], "costPrice": v[1], "marketPrice": v[2],
             "tradeQuantity": v[3] if len(v) > 3 else v[0]} for tk, v in positions.items()]}}
        with open(os.path.join(exec_dir, f"dnse_raw_{signal}.jsonl"), "w") as f:
            f.write(json.dumps(rec) + "\n")
    plan = {"plan_date": plan_date, "signal_date": signal, "strategy": "V2.4", "strategy_version": "2.4",
            "state": 2, "state_name": "NEUTRAL", "nav_basis": {"account_nav": 1e9},
            "orders": list(orders or []), "account": ACCOUNT, "approved_by": approved_by,
            "requires_user_approval": True}
    with open(os.path.join(plan_dir, f"plan_{ACCOUNT}_{plan_date}.json"), "w") as f:
        json.dump(plan, f)
    rules_path = os.path.join(td, "discretionary_exit_rules.json")
    if raw_rules is not None:
        open(rules_path, "w").write(raw_rules)
    elif rules_doc is not None:
        json.dump({"version": 1, "positions": rules_doc}, open(rules_path, "w"))
    led = os.path.join(td, "capit.json")
    json.dump({"episodes": []}, open(led, "w"))
    lot_map = {tk: {"qty": sum(q for q, _ in ls), "entry_date": min(d for _, d in ls),
                    "lots": [{"qty": q, "entry_date": d} for q, d in ls]} for tk, ls in (lots or {}).items()}
    calls = {"disc_snapshot": 0, "subprocess": []}

    def fake_snapshot(account, book, asof=None, **kw):
        if book == "DISCRETIONARY_SPECIAL":
            calls["disc_snapshot"] += 1
            if not lots_ok:
                return {}, False, "selfcheck: lỗi kết cấu", {}
            return dict(lot_map), True, None, dict(lots_blocked or {})
        return {}, True, None, {}
    orig = dict(EXEC_DIR=ps.EXEC_DIR, PLAN_DIR=aei.PLAN_DIR, acct=aei.account_no_for, snap=aei.book_lot_snapshot,
                rp=aei.DISC_RULES_PATH, ap=aei.DISC_ALERT_STATE_PATH, bp=aei.BLOCK_ALERT_STATE_PATH,
                led=aei.capit_episode.LEDGER_PATH, sp=aei.subprocess.run, rh=aei.rights_hold.holds_for)
    ps.EXEC_DIR, aei.PLAN_DIR = exec_dir, plan_dir
    aei.account_no_for = lambda a: ACCOUNT_NO if a == ACCOUNT else None
    aei.book_lot_snapshot = fake_snapshot
    aei.DISC_RULES_PATH = rules_path
    aei.DISC_ALERT_STATE_PATH = os.path.join(td, "disc_alert.json")
    aei.BLOCK_ALERT_STATE_PATH = os.path.join(td, "block_alert.json")
    aei.capit_episode.LEDGER_PATH = led
    aei.rights_hold.holds_for = lambda *a, **k: {}

    def _fake_run(cmd, *a, **kw):
        calls["subprocess"].append(cmd)
        return subprocess.CompletedProcess(cmd, 0, "", "")
    aei.subprocess.run = _fake_run
    try:
        rcs = [aei.process_account(ACCOUNT, plan_date, signal, dry_run) for _ in range(repeat)]
        with open(os.path.join(plan_dir, f"plan_{ACCOUNT}_{plan_date}.json")) as f:
            out = json.load(f)
        # load_plan THẬT: field sàn bán phải sống qua ranh giới nạp plan (§24 "field bị lọc mất là im lặng")
        op = tbplan.PLAN_DIR
        tbplan.PLAN_DIR = plan_dir
        try:
            loaded = tbplan.load_plan(plan_date, ACCOUNT)
        finally:
            tbplan.PLAN_DIR = op
    finally:
        ps.EXEC_DIR, aei.PLAN_DIR = orig["EXEC_DIR"], orig["PLAN_DIR"]
        aei.account_no_for, aei.book_lot_snapshot = orig["acct"], orig["snap"]
        aei.DISC_RULES_PATH, aei.DISC_ALERT_STATE_PATH = orig["rp"], orig["ap"]
        aei.BLOCK_ALERT_STATE_PATH, aei.capit_episode.LEDGER_PATH = orig["bp"], orig["led"]
        aei.subprocess.run, aei.rights_hold.holds_for = orig["sp"], orig["rh"]
        shutil.rmtree(td, ignore_errors=True)
    sells = [o for o in out["orders"] if o.get("book") == "DISCRETIONARY_SPECIAL" and o["side"] == "sell"]
    blocked = [b for n in out.get("auto_exit_inject_notes") or [] for b in n.get("blocked") or []]
    capped = [c for n in out.get("auto_exit_inject_notes") or [] for c in n.get("capped") or []]
    return dict(rc=rcs[-1], rcs=rcs, plan=out, sells=sells, blocked=blocked, capped=capped, calls=calls,
                loaded=loaded)


# ---------------------------------------------------------------- tests
def test_rules():
    print("== R: auto_exit_rules.disc_exit_triggers (biên bằng giá thật, float) ==")
    T = lambda p, s=0: rules.disc_exit_triggers(p, s, 0.10, 0.10, 25)  # noqa: E731
    check("R1 đúng +10,00% (56100/51000) ⇒ TARGET", T(56100 / 51000 - 1) == ["TARGET"], repr(56100 / 51000 - 1))
    check("R1b pnl literal đúng 0.10 / −0.10 ⇒ TARGET / STOP (ngữ nghĩa ≥/≤, không phải >/<)",
          T(0.10) == ["TARGET"] and T(-0.10) == ["STOP"])
    check("R2 dưới +10% 1 đồng (56099/51000) ⇒ không bắn", T(56099 / 51000 - 1) == [])
    check("R3 đúng −10,00% (45900/51000) ⇒ STOP", T(45900 / 51000 - 1) == ["STOP"], repr(45900 / 51000 - 1))
    check("R4 trên −10% 1 đồng (45901/51000) ⇒ không bắn", T(45901 / 51000 - 1) == [])
    check("R5 đúng −10,00% giá vốn lẻ (46035/51150) ⇒ STOP", T(46035 / 51150 - 1) == ["STOP"], repr(46035 / 51150 - 1))
    check("R6 đúng +10,00% giá vốn lẻ (56265/51150) ⇒ TARGET", T(56265 / 51150 - 1) == ["TARGET"], repr(56265 / 51150 - 1))
    check("R7 phiên 25 ⇒ TIME, 24 ⇒ không", T(0.0, 25) == ["TIME"] and T(0.0, 24) == [])
    check("R8 STOP + TIME cùng lúc ⇒ ['STOP','TIME']", T(-0.2, 30) == ["STOP", "TIME"])
    check("R9 pnl None ⇒ chỉ xét TIME", rules.disc_exit_triggers(None, 3, .1, .1, 25) == [])
    e = dt.date(2026, 11, 6)
    d25 = nth_session_after(e, 25)
    check("R10 phiên thứ 25 sau 06/11/2026 = 11/12/2026 (vn_market thật)", d25 == dt.date(2026, 12, 11), str(d25))
    check("R11 count_trading_days(06/11, 11/12) = 25 và (06/11, 10/12) = 24",
          ps.count_trading_days(e, dt.date(2026, 12, 11)) == 25 and ps.count_trading_days(e, dt.date(2026, 12, 10)) == 24)


def test_injector():
    print("== I: process_account nhánh DISCRETIONARY ==")
    E = "2026-11-06"
    sig = nth_session_after(dt.date(2026, 11, 6), 5)
    pdate = next_trading_day(sig)
    S, P = sig.isoformat(), pdate.isoformat()
    lots_ok = {"FPT": [(300, E), (500, E)]}

    r = run(S, P, {"FPT": (800, 51000, 56100)}, [rule_entry()], lots=lots_ok)
    o = r["sells"][0] if r["sells"] else {}
    check("I1 TARGET đúng +10,00% ⇒ chèn 1 SELL qty broker 800, book DISC", len(r["sells"]) == 1 and o.get("qty") == 800
          and o.get("play_type") == "DISCRETIONARY_AUTO_EXIT", str(r["sells"])[:200])
    check("I1b sàn bán = ceil(51000×1,10) = 56100 (field riêng §24)", o.get("hard_sell_floor_vnd") == 56100.0,
          str(o.get("hard_sell_floor_vnd")))
    lo = [x for x in (r["loaded"].orders if r["loaded"] else []) if x.ticker == "FPT"]
    check("I1c load_plan THẬT giữ hard_sell_floor_vnd (không bị lọc im lặng)",
          bool(lo) and getattr(lo[0], "hard_sell_floor_vnd", None) == 56100.0)
    check("I1d plan vẫn requires_user_approval, chưa approved", r["plan"].get("requires_user_approval") is True
          and not r["plan"].get("approved_by"))
    check("I1e TARGET không tự notify (chỉ STOP notify)", not r["calls"]["subprocess"])

    r = run(S, P, {"FPT": (800, 51000, 56099)}, [rule_entry()], lots=lots_ok)
    check("I2 +9,998% ⇒ không chèn, không gọi sổ lô", not r["sells"] and r["calls"]["disc_snapshot"] == 0)

    r = run(S, P, {"FPT": (800, 51000, 45900)}, [rule_entry()], lots=lots_ok)
    o = r["sells"][0] if r["sells"] else {}
    check("I3 STOP đúng −10,00% ⇒ chèn SELL đề xuất, requires_user_confirm, KHÔNG sàn",
          len(r["sells"]) == 1 and o["disc_exit"]["requires_user_confirm"] is True and not o.get("hard_sell_floor_vnd")
          and "XÁC NHẬN" in o["note"])
    r = run(S, P, {"FPT": (800, 51000, 45901)}, [rule_entry()], lots=lots_ok)
    check("I3b −9,998% ⇒ không chèn", not r["sells"])

    sig25 = nth_session_after(dt.date(2026, 11, 6), 25)
    r = run(sig25.isoformat(), next_trading_day(sig25).isoformat(), {"FPT": (800, 51000, 52000)},
            [rule_entry()], lots=lots_ok)
    check("I4 phiên 25 (signal 11/12) ⇒ TIME SELL, không sàn", len(r["sells"]) == 1
          and r["sells"][0]["disc_exit"]["triggers"] == ["TIME"] and not r["sells"][0].get("hard_sell_floor_vnd"))
    sig24 = nth_session_after(dt.date(2026, 11, 6), 24)
    r = run(sig24.isoformat(), next_trading_day(sig24).isoformat(), {"FPT": (800, 51000, 52000)},
            [rule_entry()], lots=lots_ok)
    check("I4b phiên 24 ⇒ không chèn", not r["sells"])
    r = run(sig25.isoformat(), next_trading_day(sig25).isoformat(), {"FPT": (800, 51000, 57000)},
            [rule_entry()], lots=lots_ok)
    check("I4c TARGET+TIME ⇒ bỏ sàn (hết hạn phải thoát được)", len(r["sells"]) == 1
          and not r["sells"][0].get("hard_sell_floor_vnd"))

    r = run(S, P, {"FPT": (800, 51000, 56100)}, [rule_entry()], lots=lots_ok, approved_by="user")
    check("I5 plan đã approved_by ⇒ rc=1, không chèn", r["rc"] == 1 and not r["sells"])
    r = run(S, P, {"FPT": (800, 51000, 56100)}, [rule_entry()], lots=lots_ok)
    r2 = run(S, P, {"FPT": (800, 51000, 56100)}, [rule_entry()], lots=lots_ok, repeat=3)
    check("I6 chạy 3 lần ⇒ đúng 1 SELL DISC (dedup ticker/book/sell)", len(r2["sells"]) == 1)
    r = run(S, P, {"FPT": (800, 51000, 56100)}, [rule_entry()], lots=lots_ok,
            orders=[{"id": "X", "ticker": "FPT", "side": "sell", "qty": 800, "ref_price": 1,
                     "book": "DISCRETIONARY_SPECIAL"}])
    check("I6b plan có sẵn SELL DISC tay ⇒ không chèn thêm", len(r["sells"]) == 1 and r["sells"][0]["id"] == "X")

    r = run(S, P, {"FPT": (800, None, 56100)}, [rule_entry()], lots=lots_ok)
    check("I7 thiếu giá vốn broker ⇒ không chèn + blocked", not r["sells"] and any(b["ticker"] == "FPT" for b in r["blocked"]))
    r = run(S, P, None, [rule_entry()], lots=lots_ok)
    check("I7b không có snapshot broker ⇒ không chèn + blocked", not r["sells"] and any(b["ticker"] == "FPT" for b in r["blocked"]))
    r = run(S, P, {"FPT": (800, 51000, 56100)}, [rule_entry()], lots=lots_ok, lots_ok=False)
    check("I7c sổ lô DISC lỗi kết cấu ⇒ không chèn + blocked", not r["sells"] and r["blocked"])
    r = run(S, P, {"FPT": (800, 51000, 56100)}, [rule_entry()], lots=lots_ok, lots_blocked={"FPT": "unverified"})
    check("I7d mã unverified trong sổ lô ⇒ không chèn + blocked", not r["sells"] and r["blocked"])
    r = run(S, P, {"FPT": (0, 51000, 56100)}, [rule_entry()], lots=lots_ok)
    check("I7e broker không còn giữ ⇒ không chèn, không blocked", not r["sells"] and not r["blocked"])

    # T+2: signal S, plan P. Lô mua ngày S ⇒ count(S,P)=1 < 2 ⇒ chưa bán được; mua prev(S) ⇒ =2 ⇒ chiều P.
    s_d = dt.date.fromisoformat(S)
    r = run(S, P, {"NNC": (100, 46900, 51590)}, [rule_entry("NNC", S)], lots={"NNC": [(100, S)]})
    check("I8 lô khớp ngày signal (chưa về T+2 tới phiên plan) ⇒ KHÔNG chèn", not r["sells"])
    pv = prev_session(s_d).isoformat()
    r = run(S, P, {"NNC": (100, 46900, 51590, 0)}, [rule_entry("NNC", pv)], lots={"NNC": [(100, pv)]})
    o = r["sells"][0] if r["sells"] else {}
    check("I8b lô về T+2 đúng phiên plan ⇒ chèn, earliest_session=AFTERNOON (dù tradeQuantity tối nay = 0)",
          o.get("qty") == 100 and o["disc_exit"]["earliest_session"] == "AFTERNOON")
    pv3 = prev_session(s_d, 3).isoformat()
    r = run(S, P, {"NNC": (300, 46900, 42210)}, [rule_entry("NNC", pv3, thin_liquidity=True)],
            lots={"NNC": [(100, pv3), (200, S)]})
    o = r["sells"][0] if r["sells"] else {}
    check("I8c NNC nhiều lô: bán 100 đã về, giữ 200 chưa về; giá vốn = avg broker; cờ khớp một phần",
          o.get("qty") == 100 and o["disc_exit"]["avg_cost_broker"] == 46900 and o["disc_exit"]["partial_fill_ok"]
          and "thanh khoản mỏng" in o["note"] and "200cp chưa về" in o["note"])

    r = run(S, P, {"FPT": (800, 51000, 45000)}, [rule_entry()], lots=lots_ok,
            orders=[{"id": "B", "ticker": "FPT", "side": "buy", "qty": 100, "ref_price": 1, "book": "DISCRETIONARY_SPECIAL"}])
    check("I9 plan có BUY cùng mã ⇒ không chèn SELL + blocked", not r["sells"] and any("MUA" in b["reason"] for b in r["blocked"]))
    r = run(S, P, {"FPT": (800, 51000, 56100)}, [rule_entry(entry="2026-11-05")], lots=lots_ok)
    check("I10 entry_date khai ≠ sổ lô ⇒ không chèn + blocked", not r["sells"] and any("entry_date" in b["reason"] for b in r["blocked"]))
    r = run(S, P, {"FPT": (700, 51000, 56100)}, [rule_entry()], lots=lots_ok)
    check("I11 sổ lô 800 > broker 700 ⇒ không chèn + blocked", not r["sells"] and r["blocked"])
    r = run(S, P, {"FPT": (1000, 51000, 56100)}, [rule_entry()], lots=lots_ok)
    check("I11b mã lẫn book (broker 1000, DISC 800) ⇒ chỉ bán 800", r["sells"] and r["sells"][0]["qty"] == 800)
    r = run(S, P, {"FPT": (800, 51000, 56100)}, [rule_entry()], lots=lots_ok,
            orders=[{"id": "P", "ticker": "FPT", "side": "sell", "qty": 300, "ref_price": 1, "book": "PARK"}])
    check("I11c Σ SELL cross-book > broker ⇒ cap 500 + capped note", r["sells"] and r["sells"][0]["qty"] == 500 and r["capped"])

    r = run(S, P, {"ZZZ": (500, 10000, 11000)}, [rule_entry("ZZZ", E)], lots={"ZZZ": [(500, E)]})
    check("I12 mã bất kỳ khai ở data (ZZZ) ⇒ hoạt động (không hardcode FPT/NNC)", len(r["sells"]) == 1)
    r = run(S, P, {"FPT": (800, 51000, 56100)}, None, lots=lots_ok)
    check("I12b không có file luật ⇒ no-op", not r["sells"] and not r["blocked"])
    r = run(S, P, {"FPT": (800, 51000, 56100)}, None, lots=lots_ok, raw_rules="{hỏng")
    check("I12c file luật hỏng ⇒ không chèn + blocked", not r["sells"] and r["blocked"])
    r = run(S, P, {"FPT": (800, 51000, 56100)}, [rule_entry(target_pct=1.5)], lots=lots_ok)
    check("I12d ngưỡng ngoài (0,1) ⇒ không chèn + blocked", not r["sells"] and r["blocked"])
    r = run(S, P, {"FPT": (800, 51000, 56100)}, [rule_entry(), rule_entry(target_pct=0.05)], lots=lots_ok)
    check("I12e khai trùng mã ⇒ không chèn + blocked", not r["sells"] and r["blocked"])
    r = run(S, P, {"FPT": (800, 51000, 56100)}, [dict(rule_entry(), account="OtherAcct")], lots=lots_ok)
    check("I12f entry account khác ⇒ bỏ qua", not r["sells"])
    r = run(S, P, {"FPT": (800, 51000, 56100)}, [rule_entry(target_sell_floor_pct=None)], lots=lots_ok)
    check("I12g target_sell_floor_pct=null ⇒ không sàn", r["sells"] and not r["sells"][0].get("hard_sell_floor_vnd"))

    r = run(S, P, {"FPT": (800, 51000, 45900)}, [rule_entry()], lots=lots_ok, dry_run=True)
    check("I13 dry-run ⇒ không ghi plan, không notify", not r["sells"] and not r["calls"]["subprocess"])
    # notify STOP: test-mode guard ⇒ KHÔNG subprocess; tắt guard ⇒ gọi notify_thread.sh trading_daily
    r = run(S, P, {"FPT": (800, 51000, 45900)}, [rule_entry()], lots=lots_ok)
    check("I14 STOP dưới AUTO_EXIT_TEST_MODE ⇒ không gọi kênh thật", not r["calls"]["subprocess"])
    os.environ["AUTO_EXIT_TEST_MODE"] = "0"
    try:
        r = run(S, P, {"FPT": (800, 51000, 45900)}, [rule_entry()], lots=lots_ok, repeat=2)
    finally:
        os.environ["AUTO_EXIT_TEST_MODE"] = "1"
    n_notify = [c for c in r["calls"]["subprocess"] if "notify_thread.sh" in c[0] and "CẮT LỖ" in c[1]]
    check("I14b STOP ⇒ notify trading_daily đúng 1 lần qua 2 lượt (dedup sau gửi OK)",
          len(n_notify) == 1 and n_notify[0][2] == "trading_daily", str(len(n_notify)))


class _Q:
    def __init__(self, **kw):
        self.__dict__.update(dict(last=None, ref=None, exchange="HOSE", bid=None, ask=None, floor=None,
                                  ceiling=None, exchange_known=True))
        self.__dict__.update(kw)


def _fake_exec(orders=()):
    from trading_bot.config import DEFAULTS
    f = types.SimpleNamespace(state={"parents": {}}, cfg=dict(DEFAULTS), journal=[])
    f._hard_buy_ceiling = Executor._hard_buy_ceiling
    f._hard_sell_floor = Executor._hard_sell_floor
    f._buy_chase_pct = lambda t: 0.03
    f._journal = lambda ev, o, **kw: f.journal.append(ev)
    f._save_state = lambda: None
    f.plan = types.SimpleNamespace(orders=list(orders))
    return f


def test_executor():
    print("== E: executor sàn bán tuyệt đối ==")
    PO = tbplan.PlannedOrder
    f = _fake_exec()
    o = PO(id="S", ticker="FPT", side="sell", qty=800, ref_price=56100, book="DISCRETIONARY_SPECIAL",
           hard_sell_floor_vnd=56100)
    o0 = PO(id="S0", ticker="FPT", side="sell", qty=800, ref_price=56100, book="DISCRETIONARY_SPECIAL")
    q = _Q(last=55500, ref=56000, bid=55400, ask=55600, floor=52100, ceiling=59900)
    px0 = Executor._limit_price(f, o0, q, cross=True)
    px = Executor._limit_price(f, o, q, cross=True)
    check("E1 không sàn: bán đuổi xuống bid 55.400 (chứng minh ngược)", px0 == 55400, str(px0))
    check("E1b có sàn 56.100: giá đặt ≥ 56.100", px is not None and px >= 56100, str(px))
    pxe = Executor._limit_price(f, o, q, cross=True, extreme=True)
    check("E2 EXTREME sell-to-floor vẫn không xuống dưới sàn tuyệt đối", pxe is not None and pxe >= 56100, str(pxe))
    q2 = _Q(last=50000, ref=51000, bid=49900, ask=50100, floor=47500, ceiling=54500)
    check("E3 trần phiên 54.500 < sàn 56.100 ⇒ None (không đặt)", Executor._limit_price(f, o, q2, cross=True) is None)
    check("E3b không sàn cùng quote ⇒ đặt được (chứng minh ngược)", Executor._limit_price(f, o0, q2, cross=True) is not None)
    ob = PO(id="B", ticker="FPT", side="buy", qty=100, ref_price=50000, hard_sell_floor_vnd=99999)
    check("E4 sàn bán không ảnh hưởng lệnh MUA", Executor._hard_sell_floor(ob) is None
          and Executor._limit_price(f, ob, q2, cross=True) is not None)
    og = PO(id="G", ticker="FPT", side="sell", qty=1, ref_price=1, hard_sell_floor_vnd="rác")
    check("E5 giá trị rác ⇒ None (hành vi cũ)", Executor._hard_sell_floor(og) is None)

    class _Reached(Exception):
        pass

    def _atc(order):
        f = _fake_exec([order])
        f.state["parents"][order.id] = {"done": False, "atc_sent": False}
        f.broker = types.SimpleNamespace(get_quote=lambda t: _Q(exchange="HOSE"))

        def _open_child(ps):
            raise _Reached()
        f._open_child = _open_child
        try:
            Executor._atc_sweep(f)
        except _Reached:
            return "REACHED", f.journal
        return "SKIPPED", f.journal
    res, j = _atc(o)
    check("E6 ATC: lệnh có sàn bán ⇒ HARD_FLOOR_SKIP_ATC, không tới bước đặt ATC", res == "SKIPPED"
          and "HARD_FLOOR_SKIP_ATC" in j, f"{res} {j}")
    res0, _ = _atc(o0)
    check("E6b ATC: không sàn ⇒ tới bước đặt ATC (chứng minh ngược)", res0 == "REACHED")


def run_mutants():
    print("== MUTANTS: mỗi đột biến phải làm selfcheck ĐỎ ==")
    for mid in MUTANTS:
        env = dict(os.environ, DISC_MUTANT=mid)
        p = subprocess.run([sys.executable, os.path.abspath(__file__)], env=env, capture_output=True, text=True)
        fails = [ln.strip() for ln in p.stdout.splitlines() if ln.strip().startswith("FAIL")]
        check(f"mutant {mid} bị bắt (rc≠0)", p.returncode != 0 and bool(fails),
              (fails[0][:90] if fails else (p.stderr.strip().splitlines() or ["?"])[-1][:120]))


def main():
    test_rules()
    test_injector()
    test_executor()
    if not os.environ.get("DISC_MUTANT") and not os.environ.get("DISC_NO_MUTANTS"):
        run_mutants()
    print(f"\n{len(PASS)} PASS / {len(FAIL)} FAIL")
    if FAIL:
        print("FAIL:", FAIL)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
