#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Self-check: auto_exit_inject.py (LAG T+25 / BAL T+45 / CAPIT T+60+nhắc T+55) —
job Taylor_20260930_080814.

Test TRỰC TIẾP `process_account()` với fixture trong sandbox (monkeypatch
`portfolio_status.EXEC_DIR` + `capit_episode.LEDGER_PATH` + `auto_exit_inject.account_no_for`
+ `PLAN_DIR` — không chạm dữ liệu thật). Mọi mốc phiên tính bằng CHÍNH `next_trading_day` thật
(lịch nghỉ lễ VN thật), không hardcode ngày, để không vô tình rơi đúng dịp lễ.

Theo skill verify-before-done: chạy lại phần KHÔNG phụ thuộc đồng hồ dưới TZ khác không đổi kết
quả gì (logic ở đây nhận `signal_date`/`plan_date` tường minh, không tự đọc giờ hệ thống) — phần
PHỤ THUỘC đồng hồ (`main()`'s `now_ict()`→`next_trading_day`) test riêng ở CHECK cuối, subprocess
dưới `env -u TZ` + TZ ngoại lai (§16).

Chạy: python3 mike/bin/auto_exit_inject_selfcheck.py
"""
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile

os.environ["AUTO_EXIT_TEST_MODE"] = "1"  # §5b — không ghi reminder lên bus THẬT khi selfcheck

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wc_paths  # noqa: E402
WC_ROOT = wc_paths.find_wc_root(__file__)
sys.path.insert(0, WC_ROOT)

import auto_exit_inject as aei  # noqa: E402
import portfolio_status as ps  # noqa: E402
import capit_episode  # noqa: E402
from trading_bot.vn_market import next_trading_day  # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'} — {name}" + (f"  [{detail}]" if detail else ""))


def nth_session_after(start, n):
    d = start
    for _ in range(n):
        d = next_trading_day(d)
    return d


ACCOUNT = "SelfcheckAcct"
ACCOUNT_NO = "9999999999"


def write_journal(exec_dir, rows):
    path = os.path.join(exec_dir, f"exec_{ACCOUNT}_selfcheck_journal.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["event", "book", "side", "ticker", "ts"])
        w.writeheader()
        for r in rows:
            w.writerow(r)


def write_positions(exec_dir, asof, positions):
    """positions: {ticker: (qty, marketPrice)}"""
    path = os.path.join(exec_dir, f"dnse_raw_{asof}.jsonl")
    rec = {"kind": "positions", "account_no": ACCOUNT_NO, "payload": {"positions": [
        {"symbol": tk, "openQuantity": qty, "costPrice": mp, "marketPrice": mp}
        for tk, (qty, mp) in positions.items()]}}
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def write_capit_ledger(path, episode=None):
    data = {"episodes": [episode] if episode else []}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def setup_sandbox():
    td = tempfile.mkdtemp(prefix="auto_exit_selfcheck_")
    exec_dir = os.path.join(td, "execution_logs")
    plan_dir = os.path.join(td, "trade_plans")
    os.makedirs(exec_dir)
    os.makedirs(plan_dir)
    ledger_path = os.path.join(td, "capit_episode.json")
    write_capit_ledger(ledger_path)
    return td, exec_dir, plan_dir, ledger_path


def patch_all(exec_dir, plan_dir, ledger_path):
    orig = dict(EXEC_DIR=ps.EXEC_DIR, PLAN_DIR=aei.PLAN_DIR, LEDGER_PATH=capit_episode.LEDGER_PATH,
                account_no_for=aei.account_no_for)
    ps.EXEC_DIR = exec_dir
    aei.PLAN_DIR = plan_dir
    capit_episode.LEDGER_PATH = ledger_path
    aei.account_no_for = lambda account: ACCOUNT_NO if account == ACCOUNT else None
    return orig


def restore_all(orig):
    ps.EXEC_DIR = orig["EXEC_DIR"]
    aei.PLAN_DIR = orig["PLAN_DIR"]
    capit_episode.LEDGER_PATH = orig["LEDGER_PATH"]
    aei.account_no_for = orig["account_no_for"]


def write_plan(plan_dir, account, plan_date, approved_by=None):
    plan = {"plan_date": plan_date, "signal_date": plan_date, "strategy": "V2.4",
            "strategy_version": "2.4", "state": 2, "state_name": "NEUTRAL",
            "nav_basis": {"account_nav": 1e9}, "orders": [], "account": account,
            "approved_by": approved_by}
    path = os.path.join(plan_dir, f"plan_{account}_{plan_date}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(plan, f)
    return path


def load_plan_raw(plan_dir, account, plan_date):
    with open(os.path.join(plan_dir, f"plan_{account}_{plan_date}.json"), encoding="utf-8") as f:
        return json.load(f)


def main():
    base = next_trading_day(next_trading_day(__import__("datetime").date(2024, 1, 2)))  # ngày giao dịch chắc chắn hợp lệ
    signal_date = nth_session_after(base, 60)   # đủ chỗ lùi 60 phiên cho mọi test
    plan_date = str(next_trading_day(signal_date))
    signal_date_str = str(signal_date)

    # Tính entry date bằng cách LÙI: sinh 1 chuỗi phiên dài rồi lấy offset ngược từ signal_date.
    # (không có prev_trading_day export công khai — build forward từ một điểm đủ xa quá khứ.)
    chain_start = base
    chain = [chain_start]
    while chain[-1] < signal_date:
        chain.append(next_trading_day(chain[-1]))
    idx_signal = chain.index(signal_date)

    def entry_n_sessions_before(n):
        return str(chain[idx_signal - n])

    lag_exit_entry = entry_n_sessions_before(25)      # đúng mốc — PHẢI exit
    lag_not_yet_entry = entry_n_sessions_before(24)   # thiếu 1 phiên — KHÔNG exit
    bal_exit_entry = entry_n_sessions_before(45)      # đúng mốc BAL — PHẢI exit

    # ---------------- Test 1: LAG @25 exit, LAG @24 giữ nguyên, BAL @45 exit ----------------
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_journal(exec_dir, [
            {"event": "FILL", "book": "LAG", "side": "buy", "ticker": "AAA", "ts": lag_exit_entry},
            {"event": "FILL", "book": "LAG", "side": "buy", "ticker": "BBB", "ts": lag_not_yet_entry},
            {"event": "FILL", "book": "BAL", "side": "buy", "ticker": "CCC", "ts": bal_exit_entry},
        ])
        write_positions(exec_dir, signal_date_str, {
            "AAA": (1000, 20000.0), "BBB": (500, 15000.0), "CCC": (2000, 30000.0)})
        write_plan(plan_dir, ACCOUNT, plan_date)
        orig = patch_all(exec_dir, plan_dir, ledger_path)
        try:
            rc = aei.process_account(ACCOUNT, plan_date, signal_date_str, dry_run=False)
        finally:
            restore_all(orig)
        check("Test1: rc=0", rc == 0, f"rc={rc}")
        plan = load_plan_raw(plan_dir, ACCOUNT, plan_date)
        sells = {(o["ticker"], o["book"]): o for o in plan["orders"] if o["side"] == "sell"}
        check("Test1: AAA (LAG@25) có lệnh sell", ("AAA", "LAG") in sells)
        check("Test1: BBB (LAG@24) KHÔNG có lệnh sell", ("BBB", "LAG") not in sells)
        check("Test1: CCC (BAL@45) có lệnh sell", ("CCC", "BAL") in sells)
        if ("AAA", "LAG") in sells:
            check("Test1: AAA qty đúng vị thế broker (1000)", sells[("AAA", "LAG")]["qty"] == 1000)
    finally:
        shutil.rmtree(td, ignore_errors=True)

    # ---------------- Test 2: dedup — chạy lại KHÔNG nhân đôi lệnh ----------------
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_journal(exec_dir, [
            {"event": "FILL", "book": "LAG", "side": "buy", "ticker": "AAA", "ts": lag_exit_entry},
        ])
        write_positions(exec_dir, signal_date_str, {"AAA": (1000, 20000.0)})
        write_plan(plan_dir, ACCOUNT, plan_date)
        orig = patch_all(exec_dir, plan_dir, ledger_path)
        try:
            aei.process_account(ACCOUNT, plan_date, signal_date_str, dry_run=False)
            aei.process_account(ACCOUNT, plan_date, signal_date_str, dry_run=False)
        finally:
            restore_all(orig)
        plan = load_plan_raw(plan_dir, ACCOUNT, plan_date)
        n_sell_aaa = sum(1 for o in plan["orders"] if o["ticker"] == "AAA" and o["side"] == "sell")
        check("Test2: chạy 2 lần KHÔNG nhân đôi lệnh AAA", n_sell_aaa == 1, f"count={n_sell_aaa}")
    finally:
        shutil.rmtree(td, ignore_errors=True)

    # ---------------- Test 3: plan đã duyệt (approved_by) → REFUSE, không ghi ----------------
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_journal(exec_dir, [
            {"event": "FILL", "book": "LAG", "side": "buy", "ticker": "AAA", "ts": lag_exit_entry},
        ])
        write_positions(exec_dir, signal_date_str, {"AAA": (1000, 20000.0)})
        write_plan(plan_dir, ACCOUNT, plan_date, approved_by="user")
        before = load_plan_raw(plan_dir, ACCOUNT, plan_date)
        orig = patch_all(exec_dir, plan_dir, ledger_path)
        try:
            rc = aei.process_account(ACCOUNT, plan_date, signal_date_str, dry_run=False)
        finally:
            restore_all(orig)
        after = load_plan_raw(plan_dir, ACCOUNT, plan_date)
        check("Test3: rc=1 (REFUSE)", rc == 1, f"rc={rc}")
        check("Test3: plan KHÔNG bị sửa (byte-identical)", before == after)
    finally:
        shutil.rmtree(td, ignore_errors=True)

    # ---------------- Test 4: CAPIT @60 → sell toàn bộ rổ; @55 → nhắc, idempotent ----------------
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_journal(exec_dir, [])
        write_positions(exec_dir, signal_date_str, {"VNM": (900, 60000.0), "SAB": (1100, 150000.0)})
        write_plan(plan_dir, ACCOUNT, plan_date)
        write_capit_ledger(ledger_path, {
            "episode_id": "CAPIT-TEST", "status": "open", "sessions_held": 61,
            "qty_per_account": {ACCOUNT: {"VNM": 900, "SAB": 1100}}})
        orig = patch_all(exec_dir, plan_dir, ledger_path)
        try:
            rc = aei.process_account(ACCOUNT, plan_date, signal_date_str, dry_run=False)
        finally:
            restore_all(orig)
        check("Test4: rc=0", rc == 0, f"rc={rc}")
        plan = load_plan_raw(plan_dir, ACCOUNT, plan_date)
        capit_sells = {o["ticker"] for o in plan["orders"] if o["book"] == "CAPIT" and o["side"] == "sell"}
        check("Test4: CAPIT@61 bán TOÀN BỘ rổ (VNM+SAB)", capit_sells == {"VNM", "SAB"},
              f"got={capit_sells}")
    finally:
        shutil.rmtree(td, ignore_errors=True)

    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_journal(exec_dir, [])
        write_positions(exec_dir, signal_date_str, {"VNM": (900, 60000.0)})
        write_plan(plan_dir, ACCOUNT, plan_date)
        write_capit_ledger(ledger_path, {
            "episode_id": "CAPIT-TEST2", "status": "open", "sessions_held": 56,
            "qty_per_account": {ACCOUNT: {"VNM": 900}}})
        orig = patch_all(exec_dir, plan_dir, ledger_path)
        try:
            aei.process_account(ACCOUNT, plan_date, signal_date_str, dry_run=False)
            ledger_after_1 = json.load(open(ledger_path, encoding="utf-8"))
            sent_at_1 = ledger_after_1["episodes"][0].get("reminder_55_sent_at")
            aei.process_account(ACCOUNT, plan_date, signal_date_str, dry_run=False)
            ledger_after_2 = json.load(open(ledger_path, encoding="utf-8"))
            sent_at_2 = ledger_after_2["episodes"][0].get("reminder_55_sent_at")
        finally:
            restore_all(orig)
        plan = load_plan_raw(plan_dir, ACCOUNT, plan_date)
        n_capit_sell = sum(1 for o in plan["orders"] if o["book"] == "CAPIT" and o["side"] == "sell")
        check("Test5: CAPIT@56 KHÔNG bán (chỉ nhắc, chưa tới 60)", n_capit_sell == 0,
              f"count={n_capit_sell}")
        check("Test5: reminder_55_sent_at được ghi lần đầu", sent_at_1 is not None)
        check("Test5: reminder KHÔNG gửi lại lần 2 (idempotent)", sent_at_1 == sent_at_2)
    finally:
        shutil.rmtree(td, ignore_errors=True)

    # ---------------- Test 7: approved_by_user (bí danh) cũng phải REFUSE, không chỉ approved_by
    # (quant-skeptic 2026-09-30: pipeline duyệt plan thật coi 2 field này tương đương —
    # trading_bot/plan.py:264-265, preflight_check.sh, merge_park_orders.py) ----------------
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_journal(exec_dir, [
            {"event": "FILL", "book": "LAG", "side": "buy", "ticker": "AAA", "ts": lag_exit_entry},
        ])
        write_positions(exec_dir, signal_date_str, {"AAA": (1000, 20000.0)})
        plan_path = write_plan(plan_dir, ACCOUNT, plan_date)
        plan = load_plan_raw(plan_dir, ACCOUNT, plan_date)
        plan.pop("approved_by", None)
        plan["approved_by_user"] = "user"
        with open(plan_path, "w", encoding="utf-8") as f:
            json.dump(plan, f)
        before = load_plan_raw(plan_dir, ACCOUNT, plan_date)
        orig = patch_all(exec_dir, plan_dir, ledger_path)
        try:
            rc = aei.process_account(ACCOUNT, plan_date, signal_date_str, dry_run=False)
        finally:
            restore_all(orig)
        after = load_plan_raw(plan_dir, ACCOUNT, plan_date)
        check("Test7: rc=1 (REFUSE trên approved_by_user)", rc == 1, f"rc={rc}")
        check("Test7: plan KHÔNG bị sửa (byte-identical)", before == after)
    finally:
        shutil.rmtree(td, ignore_errors=True)

    # ---------------- Test 8: CAPIT ticker trong qty_per_account nhưng KHÔNG còn vị thế broker
    # (đã thoát qua đường khác) → KHÔNG bán khống theo planned_qty cũ (quant-skeptic 2026-09-30
    # phantom-sell bug) ----------------
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_journal(exec_dir, [])
        write_positions(exec_dir, signal_date_str, {"VNM": (900, 60000.0)})  # SAB đã hết vị thế
        write_plan(plan_dir, ACCOUNT, plan_date)
        write_capit_ledger(ledger_path, {
            "episode_id": "CAPIT-TEST8", "status": "open", "sessions_held": 61,
            "qty_per_account": {ACCOUNT: {"VNM": 900, "SAB": 1100}}})
        orig = patch_all(exec_dir, plan_dir, ledger_path)
        try:
            rc = aei.process_account(ACCOUNT, plan_date, signal_date_str, dry_run=False)
        finally:
            restore_all(orig)
        check("Test8: rc=0", rc == 0, f"rc={rc}")
        plan = load_plan_raw(plan_dir, ACCOUNT, plan_date)
        capit_sells = {o["ticker"] for o in plan["orders"] if o["book"] == "CAPIT" and o["side"] == "sell"}
        check("Test8: VNM (còn vị thế) có lệnh sell", "VNM" in capit_sells)
        check("Test8: SAB (hết vị thế) KHÔNG có lệnh sell khống", "SAB" not in capit_sells,
              f"got={capit_sells}")
    finally:
        shutil.rmtree(td, ignore_errors=True)

    # ---------------- Test 6: TZ-robustness của plan_date trong main() (§16) ----------------
    def expected_plan_date(env):
        r = subprocess.run(
            [sys.executable, "-c",
             "from trading_bot.vn_market import next_trading_day, now_ict; "
             "print(next_trading_day(now_ict().date()))"],
            cwd=WC_ROOT, capture_output=True, text=True, env=env)
        return r.stdout.strip()

    env_default = dict(os.environ)
    env_no_tz = {k: v for k, v in os.environ.items() if k != "TZ"}
    env_ny = dict(os.environ, TZ="America/New_York")
    d1, d2, d3 = (expected_plan_date(env_default), expected_plan_date(env_no_tz),
                  expected_plan_date(env_ny))
    check("Test6: plan_date neo ICT giống nhau qua 3 TZ (default/unset/NY)",
          d1 == d2 == d3 and d1 != "", f"default={d1} unset={d2} NY={d3}")

    print(f"\n{len(PASS)} PASS, {len(FAIL)} FAIL")
    if FAIL:
        print("FAILED:", FAIL)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
