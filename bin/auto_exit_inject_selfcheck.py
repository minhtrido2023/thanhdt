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
import datetime as dt
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

# Mutation test lô-1-1 (job Taylor_20261028_162413): con chạy với LOT_MUTANT=<id> nạp bản ĐỘT BIẾN
# của auto_exit_inject.py / portfolio_status.py (exec với __file__ GỐC để wc_paths tìm đúng WC_ROOT)
# rồi chỉ chạy `lot_tests` — phá fix thì phải ĐỎ. Bảng đột biến: `LOT_MUTANTS` bên dưới.
LOT_MUTANTS = {
    "MA1_sell_all_lots": ("auto_exit_inject.py", "        if not is_due(s):\n            if gate is None:",
                          "        if False:\n            if gate is None:"),
    "MA2_all_rights_lots": ("auto_exit_inject.py",
                            '"LAG", injected, capped_notes, sessions,\n                     rights_lots=due_rights,',
                            '"LAG", injected, capped_notes, sessions,\n                     '
                            'rights_lots=lag_lots.get(tk, {}).get("rights_lots"),'),
    "MA3_sessions_newest_due": ("auto_exit_inject.py", "else max(sessions_max, s)", "else min(sessions_max, s)"),
    "MA4_legacy_fallback": ("auto_exit_inject.py",
                            "    if not isinstance(lot_list, list) or not lot_list:\n",
                            "    if not lot_list:\n        lot_list = [{'qty': lot['qty'], 'entry_date': lot['entry_date']}]\n"
                            "    if False:\n"),
    "MA5_stoploss_no_minhold": ("auto_exit_inject.py", "lambda s: s >= rules.BAL_STOP_LOSS_MIN_HOLD", "lambda s: True"),
    # Vòng 2 (job Taylor_20261028_165505): bỏ quy tắc prefix theo thứ tự sổ (L12/L15) · bỏ hợp
    # stop-loss vào lệnh T+45 (L13) · lô bị giữ chỉ in, không vào blocked (L12b).
    "MA6_no_prefix": ("auto_exit_inject.py", "        if gate is not None:\n            stranded.append",
                      "        if False:\n            stranded.append"),
    "MA7_no_sl_union": ("auto_exit_inject.py", "                qty, due_rights = sl[1], sl[4]\n",
                        "                pass\n"),
    "MA8_held_not_blocked": ("auto_exit_inject.py",
                             '            print(f"  [LOT-ORDER] {book} {tk}: {held}")\n'
                             '            blocked.append({"ticker": tk, "reason": held, "held_qty": held_qty})\n',
                             '            print(f"  [LOT-ORDER] {book} {tk}: {held}")\n'),
    # Vòng 3: bước lọc blocked "held" sau gộp stop-loss (L16a) · cho lọc dù lệnh gộp bị cap cắt (L16c).
    "MA9_no_held_filter": ("auto_exit_inject.py", "and got >= want:\n", "and False:\n"),
    "MA10_filter_ignores_cap": ("auto_exit_inject.py", "and got >= want:\n", "and True:\n"),
    "MP1_snapshot_no_lots": ("portfolio_status.py", '        d["lots"].append(one)\n', "        pass\n"),
    "MP2_hint_all_due": ("portfolio_status.py",
                         "    due = [g for g in groups if g[2] >= LAG_EXIT_SESSIONS_FIXED]\n",
                         "    due = groups if any(g[2] >= LAG_EXIT_SESSIONS_FIXED for g in groups) else []\n"),
}


def _load_mutant(mid):
    import types
    fname, old, new = LOT_MUTANTS[mid]
    path = os.path.join(HERE, fname)
    src = open(path, encoding="utf-8").read()
    if src.count(old) != 1:
        raise SystemExit(f"mutant {mid}: chuỗi gốc xuất hiện {src.count(old)} lần (≠1) — bảng đột biến lỗi thời")
    mod = types.ModuleType(fname[:-3])
    mod.__file__ = path
    sys.modules[fname[:-3]] = mod
    exec(compile(src.replace(old, new), path, "exec"), mod.__dict__)


if os.environ.get("LOT_MUTANT"):
    _mid = os.environ["LOT_MUTANT"]
    if LOT_MUTANTS[_mid][0] == "portfolio_status.py":
        _load_mutant(_mid)          # nạp TRƯỚC aei ⇒ `from portfolio_status import ...` lấy bản đột biến
    else:
        import portfolio_status  # noqa: E402,F401
        _load_mutant(_mid)

import auto_exit_inject as aei  # noqa: E402
import portfolio_status as ps  # noqa: E402
import capit_episode  # noqa: E402
import park_holdings as ph  # noqa: E402
import corp_actions as ca  # noqa: E402
from trading_bot.vn_market import next_trading_day  # noqa: E402

# Cổng quyền mua (X1, lag_rights_exit_hold.py) có selfcheck riêng (lag_rights_exit_hold_selfcheck.py);
# ở đây mã giả không có quyền mua — chặn tra BQ thật, giữ nguyên hành vi mọi ca cũ.
aei.rights_hold.holds_for = lambda *a, **kw: {}

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
    """positions: {ticker: (qty, marketPrice)} — costPrice=marketPrice (lãi/lỗ 0, dùng cho test
    không quan tâm stop-loss)."""
    write_positions_cost(exec_dir, asof, {tk: (qty, mp, mp) for tk, (qty, mp) in positions.items()})


def write_positions_cost(exec_dir, asof, positions, sellable=None):
    """positions: {ticker: (qty, costPrice, marketPrice)} — dùng khi test cần tách giá vốn khỏi
    giá thị trường (stop-loss). `sellable` (dict {ticker: tradeQuantity}, optional) — mặc định
    TOÀN BỘ qty sellable (vị thế LAG/BAL/CAPIT đã giữ ≥ mốc exit luôn qua lâu T+2), chỉ set khác
    khi test CHỦ Ý kiểm tra cap Σsell (xem Test cap cross-book `_cap_sellable`)."""
    sellable = sellable or {}
    path = os.path.join(exec_dir, f"dnse_raw_{asof}.jsonl")
    rec = {"kind": "positions", "account_no": ACCOUNT_NO, "payload": {"positions": [
        {"symbol": tk, "openQuantity": qty, "costPrice": cp, "marketPrice": mp,
         "tradeQuantity": sellable.get(tk, qty)}
        for tk, (qty, cp, mp) in positions.items()]}}
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def write_positions_raw(exec_dir, asof, rows, account_no=None):
    """Ghi THẲNG danh sách row vị thế thô, cho phép NHIỀU row CÙNG symbol — mirror DNSE trả
    nhiều gói vay (loan-package) cùng mã trên CÙNG 1 snapshot `positions`. KHÁC
    `write_positions_cost` (dict keyed theo ticker ⇒ chỉ 1 row/mã, không dựng được ca này) — dùng
    để test hành vi CỘNG DỒN của `broker_positions_with_cost()` (Mcap5, arch-review vòng 3)."""
    path = os.path.join(exec_dir, f"dnse_raw_{asof}.jsonl")
    rec = {"kind": "positions", "account_no": account_no or ACCOUNT_NO,
           "payload": {"positions": rows}}
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def install_subprocess_recorder():
    """Monkeypatch `aei.subprocess.run` bằng recorder — bắt THẬT mọi side-effect ra ngoài tiến
    trình (bus/Discord) mà `process_account` có thể kích hoạt, thay vì chỉ suy luận từ code đọc
    được. Sự cố gốc (job Taylor_20260930, selfcheck lần đầu của CHÍNH file này) ghi nhầm episode
    giả lên bus thật vì guard test-mode không được xác nhận bằng cách này — gỡ guard ở
    `_send_block_alert`/`_send_capit_reminder` vẫn để 71/71 test cũ PASS (arch-review vòng 3)."""
    orig = aei.subprocess.run
    calls = []

    def _fake(cmd, *a, **kw):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0)
    aei.subprocess.run = _fake
    return orig, calls


def restore_subprocess_recorder(orig):
    aei.subprocess.run = orig


def write_capit_ledger(path, episode=None):
    data = {"episodes": [episode] if episode else []}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def write_bootstrap(plan_dir, account, account_no, day0_date, positions, reconcile_ok=True,
                    status="APPROVED by selfcheck"):
    """Bootstrap ngày 0 tối giản cho test `book_lot_snapshot()` THẬT (gọi `park_holdings()` thật,
    KHÔNG monkeypatch) — `positions`: [{"ticker","qty","book","entry_date","cost_price_vnd",
    "play_type"(optional)}, ...], cho phép CÙNG ticker xuất hiện NHIỀU lần với book khác nhau
    (mirror ca VPB thật: 1 ticker, 2 lô, 2 book)."""
    snap = {"_status": status, "account_label": account, "account_no": account_no,
            "day0_date": day0_date,
            "broker_source": {"file": "selfcheck", "ts": f"{day0_date}T00:00:00"},
            "reconcile_ok": reconcile_ok, "positions": positions}
    path = os.path.join(plan_dir,
                        f"bootstrap_book_snapshot_{account}_{day0_date.replace('-', '')}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(snap, f)
    return path


def patch_account_profile(account_no, excluded=()):
    """`park_holdings.account_profile()` đọc `secrets/trading_bot_accounts.json` thật — account
    giả của selfcheck không có trong đó ⇒ phải monkeypatch (mirror cách
    `compute_park_trim_selfcheck.py` dùng `excluded_dividend_config_override`)."""
    orig = ph.account_profile
    ph.account_profile = lambda label: {"account_id": account_no, "excluded_tickers": list(excluded)}
    return orig


def restore_account_profile(orig):
    ph.account_profile = orig


def setup_sandbox():
    td = tempfile.mkdtemp(prefix="auto_exit_selfcheck_")
    exec_dir = os.path.join(td, "execution_logs")
    plan_dir = os.path.join(td, "trade_plans")
    os.makedirs(exec_dir)
    os.makedirs(plan_dir)
    ledger_path = os.path.join(td, "capit_episode.json")
    write_capit_ledger(ledger_path)
    return td, exec_dir, plan_dir, ledger_path


def patch_all(exec_dir, plan_dir, ledger_path, lag_lots=None, bal_lots=None,
             lag_ok=True, bal_ok=True, lag_blocked=None, bal_blocked=None):
    """`lag_lots`/`bal_lots` (dict {ticker: {'qty':int,'entry_date':str}} hoặc None=rỗng) monkeypatch
    `aei.book_lot_snapshot` để trả THẲNG — Test1..11 kiểm NGƯỠNG EXIT của
    `_lag_bal_candidates`/`_bal_stop_loss_candidates`/`process_account` (dedup, REFUSE khi đã
    duyệt, phantom-sell guard...), KHÔNG phải cơ chế bootstrap+FIFO của `park_holdings()` — cái đó
    có test riêng (Test12+, gọi `book_lot_snapshot` THẬT). Cùng tinh thần `holdings=` override của
    `compute_park_trim_selfcheck.py` (bypass I/O, test riêng từng lớp). `lag_ok=False`/`bal_ok=False`
    mô phỏng park_holdings() LỖI KẾT CẤU (Test1d) — `lots` trả về RỖNG bất kể `lag_lots`/`bal_lots`
    được truyền gì, đúng ngữ nghĩa `book_lot_snapshot` thật (ok=False ⇒ lots rỗng, blocked rỗng).
    `lag_blocked`/`bal_blocked` (dict {ticker: reason} hoặc None=rỗng) mô phỏng mã UNVERIFIED
    RIÊNG LẺ trong book ok=True (fail-safe TỪNG MÃ, arch-review vòng 2) — khác `lag_ok=False` ở
    chỗ các mã KHÁC trong `lag_lots`/`bal_lots` vẫn ra bình thường."""
    orig = dict(EXEC_DIR=ps.EXEC_DIR, PLAN_DIR=aei.PLAN_DIR, LEDGER_PATH=capit_episode.LEDGER_PATH,
                account_no_for=aei.account_no_for, book_lot_snapshot=aei.book_lot_snapshot,
                BLOCK_ALERT_STATE_PATH=aei.BLOCK_ALERT_STATE_PATH)
    ps.EXEC_DIR = exec_dir
    aei.PLAN_DIR = plan_dir
    capit_episode.LEDGER_PATH = ledger_path
    aei.account_no_for = lambda account: ACCOUNT_NO if account == ACCOUNT else None
    aei.BLOCK_ALERT_STATE_PATH = os.path.join(plan_dir, "_auto_exit_block_alert_state.json")
    _by_book = {"LAG": (dict(lag_lots or {}), lag_ok, dict(lag_blocked or {})),
                "BAL": (dict(bal_lots or {}), bal_ok, dict(bal_blocked or {}))}

    def _fake(account, book_label, asof=None, **kw):
        lots, ok, blocked = _by_book.get(book_label, ({}, True, {}))
        if not ok:
            return {}, False, "selfcheck: giả lập reconcile lệch (kết cấu)", {}
        # Fixture dạng cũ {qty, entry_date} (Test1..11, trước lô-1-1) = MỘT lô — bổ sung `lots`
        # đúng dạng `book_lot_snapshot` thật. Fixture CÓ `lots` (lot_tests) đi nguyên. Ca THIẾU
        # `lots` ⇒ fail-safe được kiểm thẳng ở `lot_tests` (gọi `_lag_bal_candidates`, không qua đây).
        lots = {tk: (v if "lots" in v else dict(v, lots=[{"qty": v["qty"], "entry_date": v["entry_date"]}]))
                for tk, v in lots.items()}
        return dict(lots), True, None, dict(blocked)
    aei.book_lot_snapshot = _fake
    return orig


def restore_all(orig):
    ps.EXEC_DIR = orig["EXEC_DIR"]
    aei.PLAN_DIR = orig["PLAN_DIR"]
    capit_episode.LEDGER_PATH = orig["LEDGER_PATH"]
    aei.account_no_for = orig["account_no_for"]
    aei.book_lot_snapshot = orig["book_lot_snapshot"]
    aei.BLOCK_ALERT_STATE_PATH = orig["BLOCK_ALERT_STATE_PATH"]


def write_plan(plan_dir, account, plan_date, approved_by=None, orders=None):
    plan = {"plan_date": plan_date, "signal_date": plan_date, "strategy": "V2.4",
            "strategy_version": "2.4", "state": 2, "state_name": "NEUTRAL",
            "nav_basis": {"account_nav": 1e9}, "orders": list(orders or []), "account": account,
            "approved_by": approved_by}
    path = os.path.join(plan_dir, f"plan_{account}_{plan_date}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(plan, f)
    return path


def existing_sell_order(ticker, qty, book, order_id):
    """Lệnh SELL CÓ SẴN trong plan (vd PARKMERGE-SELL book khác cùng mã) — mirror ca VPB thật
    ZaloPay 02/10: PARKMERGE-SELL VPB 300 (PARK) + LAG 882 > tradeQuantity 900."""
    return {"id": order_id, "ticker": ticker, "side": "sell", "qty": qty, "ref_price": 20000.0,
            "book": book, "play_type": "PARK_TRIM", "priority": 1, "note": "pre-existing"}


def patch_all_e2e(exec_dir, plan_dir, ledger_path, account_no, excluded=(), corp_actions=None):
    """Mirror `patch_all` nhưng KHÔNG mock `aei.book_lot_snapshot` — dùng cho test end-to-end gọi
    `park_holdings()` THẬT (bootstrap+FIFO+corp-action). `book_lot_snapshot()` production path
    (process_account KHÔNG truyền plan_dir/exec_dir) gọi `park_holdings(account, asof=asof,
    need_price=False)` — `plan_dir`/`exec_dir` rơi về DEFAULT của `park_holdings()`. Default
    argument của Python bind GIÁ TRỊ `PLAN_DIR`/`EXEC_DIR` tại thời điểm module LOAD (một lần),
    KHÔNG tra lại `park_holdings.PLAN_DIR` mỗi lần gọi ⇒ gán `ph.PLAN_DIR = ...` KHÔNG có tác
    dụng gì (đã verify: vẫn đọc nhầm `data/trade_plans` thật). Phải sửa THẲNG
    `park_holdings.__defaults__` (tuple vị trí `(asof, plan_dir, exec_dir, broker, corp_actions,
    price_fn, need_price)` — xem `inspect.signature` nếu hàm đổi chữ ký)."""
    orig = dict(EXEC_DIR=ps.EXEC_DIR, PLAN_DIR=aei.PLAN_DIR, LEDGER_PATH=capit_episode.LEDGER_PATH,
                account_no_for=aei.account_no_for, ph_defaults=ph.park_holdings.__defaults__,
                ph_account_profile=ph.account_profile, ph_load_corp_actions=ph.load_corp_actions,
                BLOCK_ALERT_STATE_PATH=aei.BLOCK_ALERT_STATE_PATH)
    ps.EXEC_DIR = exec_dir
    aei.PLAN_DIR = plan_dir
    capit_episode.LEDGER_PATH = ledger_path
    aei.account_no_for = lambda account: account_no if account == ACCOUNT else None
    aei.BLOCK_ALERT_STATE_PATH = os.path.join(plan_dir, "_auto_exit_block_alert_state.json")
    d = list(orig["ph_defaults"])
    d[1], d[2] = plan_dir, exec_dir   # (asof, plan_dir, exec_dir, broker, corp_actions, price_fn, need_price)
    ph.park_holdings.__defaults__ = tuple(d)
    ph.account_profile = lambda label: {"account_id": account_no, "excluded_tickers": list(excluded)}
    ph.load_corp_actions = lambda *a, **kw: list(corp_actions or [])
    return orig


def restore_all_e2e(orig):
    ps.EXEC_DIR = orig["EXEC_DIR"]
    aei.PLAN_DIR = orig["PLAN_DIR"]
    capit_episode.LEDGER_PATH = orig["LEDGER_PATH"]
    aei.account_no_for = orig["account_no_for"]
    ph.park_holdings.__defaults__ = orig["ph_defaults"]
    ph.account_profile = orig["ph_account_profile"]
    ph.load_corp_actions = orig["ph_load_corp_actions"]
    aei.BLOCK_ALERT_STATE_PATH = orig["BLOCK_ALERT_STATE_PATH"]


def load_plan_raw(plan_dir, account, plan_date):
    with open(os.path.join(plan_dir, f"plan_{account}_{plan_date}.json"), encoding="utf-8") as f:
        return json.load(f)


def _lots(*items):
    """Fixture sổ lô ĐÚNG dạng `book_lot_snapshot` (qty gộp, entry_date MIN, `lots` từng lô).
    item = (qty, entry_date) hoặc (qty, entry_date, rights_subscription)."""
    lots = []
    for it in items:
        one = {"qty": it[0], "entry_date": it[1]}
        if len(it) > 2:
            one["rights_subscription"] = it[2]
        lots.append(one)
    return {"qty": sum(i[0] for i in items), "entry_date": min(i[1] for i in items), "lots": lots}


def _run_mock(signal_date_str, plan_date, positions_cost, sellable=None, lag_lots=None, bal_lots=None):
    """process_account THẬT trên sandbox, sổ lô bơm qua `patch_all` (mock). Trả (plan, sells{(tk,book):o})."""
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_positions_cost(exec_dir, signal_date_str, positions_cost, sellable=sellable)
        write_plan(plan_dir, ACCOUNT, plan_date)
        orig = patch_all(exec_dir, plan_dir, ledger_path, lag_lots=lag_lots, bal_lots=bal_lots)
        sp_orig, _calls = install_subprocess_recorder()
        try:
            aei.process_account(ACCOUNT, plan_date, signal_date_str, dry_run=False)
        finally:
            restore_subprocess_recorder(sp_orig)
            restore_all(orig)
        plan = load_plan_raw(plan_dir, ACCOUNT, plan_date)
        return plan, {(o["ticker"], o["book"]): o for o in plan["orders"] if o["side"] == "sell"}
    finally:
        shutil.rmtree(td, ignore_errors=True)


def _notes(plan, key):
    return [x for n in plan.get("auto_exit_inject_notes") or [] for x in n.get(key) or []]


def lot_tests(signal_date, plan_date, before):
    """Lô-1-1 (job Taylor_20261028_162413): exit theo TỪNG LÔ, không theo qty gộp/entry MIN.
    `before(n)` = ngày ISO n phiên trước signal_date. Mọi ca ĐỎ dưới ít nhất một đột biến `LOT_MUTANTS`."""
    sig = str(signal_date)
    sig_d = signal_date
    print("\n[LOT] exit theo từng lô")
    # L1 — ca THẬT ZaloPay VPB 28/10 (sổ lô park_holdings đo 28/10): 282cp lô cũ (64 phiên) +
    # 100+200+200+200 (2 phiên) + 100+100 (1 phiên) = 1.182; sellable 700. Bản cũ: SELL 700.
    vpb = _lots((282, before(64)), (100, before(2)), (200, before(2)), (200, before(2)), (200, before(2)),
                (100, before(1)), (100, before(1)))
    plan, sells = _run_mock(sig, plan_date, {"VPB": (1182, 25000.0, 25000.0)}, sellable={"VPB": 700},
                            lag_lots={"VPB": vpb})
    o = sells.get(("VPB", "LAG"))
    check("L1 VPB ZaloPay: SELL đúng 282 (lô tới hạn), KHÔNG 700/1.182", o is not None and o["qty"] == 282,
          f"sells={ {k: v['qty'] for k, v in sells.items()} }")
    check("L1 VPB: không bị cắt sellable (282 ≤ 700), note nêu phần giữ lại 900cp",
          not _notes(plan, "capped") and o is not None and "giữ 900cp lô chưa tới hạn" in o["note"],
          o and o["note"])
    inj = _notes(plan, "injected")
    check("L1 VPB: sessions_held báo = của lô CŨ NHẤT tới hạn (64)",
          [x["sessions_held"] for x in inj] == [64], inj)

    # L2 — SCL thoát hẳn rồi vào lại: sổ lô chỉ còn lô mới (FIFO đã tiêu lô cũ) ⇒ không bán
    scl = _lots((100, before(2)), (100, before(2)), (100, before(2)), (200, before(2)), (200, before(0)))
    plan, sells = _run_mock(sig, plan_date, {"SCL": (700, 30000.0, 30000.0)}, lag_lots={"SCL": scl})
    check("L2 SCL vào lại sau khi thoát hẳn (mọi lô < T+25): KHÔNG bán, không chặn",
          ("SCL", "LAG") not in sells and not _notes(plan, "blocked"), (sells, _notes(plan, "blocked")))

    # L3 — mọi lô tới hạn ⇒ bán HẾT (Σ), note 'thoát toàn bộ'
    allx = _lots((300, before(40)), (200, before(30)), (100, before(25)))
    plan, sells = _run_mock(sig, plan_date, {"ALL": (600, 20000.0, 20000.0)}, lag_lots={"ALL": allx})
    o = sells.get(("ALL", "LAG"))
    check("L3 mọi lô tới hạn ⇒ bán 600 (toàn bộ), sessions = 40",
          o is not None and o["qty"] == 600 and "thoát toàn bộ" in o["note"]
          and [x["sessions_held"] for x in _notes(plan, "injected")] == [40], (o, _notes(plan, "injected")))

    # L4 — không lô nào tới hạn (lô cũ nhất 24 phiên) ⇒ không bán, không chặn
    none_ = _lots((300, before(24)), (200, before(3)))
    plan, sells = _run_mock(sig, plan_date, {"NON": (500, 20000.0, 20000.0)}, lag_lots={"NON": none_})
    check("L4 không lô nào tới hạn ⇒ không bán, không chặn", not sells and not _notes(plan, "blocked"),
          (sells, plan.get("auto_exit_inject_notes")))

    # L5 — lô tới hạn 282 + cap sellable 200 (lệnh PARK khác chiếm/T+2) ⇒ cắt 282→200, ghi capped
    plan, sells = _run_mock(sig, plan_date, {"VPB": (1182, 25000.0, 25000.0)}, sellable={"VPB": 200},
                            lag_lots={"VPB": vpb})
    cp = _notes(plan, "capped")
    check("L5 cap sellable nhỏ hơn phần tới hạn: SELL 200, capped desired=282 (KHÔNG desired=1.182)",
          sells.get(("VPB", "LAG"), {}).get("qty") == 200 and [(c["desired_qty"], c["capped_qty"]) for c in cp]
          == [(282, 200)], (sells, cp))

    # L6 — BAL T+45 theo lô: 300 @45 + 400 @44 ⇒ bán 300
    balx = _lots((300, before(45)), (400, before(44)))
    plan, sells = _run_mock(sig, plan_date, {"BLX": (700, 20000.0, 20000.0)}, bal_lots={"BLX": balx})
    check("L6 BAL T+45: lô @45 bán (300), lô @44 giữ", sells.get(("BLX", "BAL"), {}).get("qty") == 300,
          {k: v["qty"] for k, v in sells.items()})

    # L7 — lô quyền mua: lô thường 1.000 + lô quyền 500 (kế thừa entry cũ, CHƯA niêm yết) tới hạn;
    # lô quyền 300 kế thừa entry MỚI (chưa tới hạn). held 1.800, sellable 1.000 (800 chưa cho bán).
    # Đúng: tới hạn 1.500 ⇒ khoá 500 (chỉ lô quyền TỚI HẠN) ⇒ SELL 1.000. Nếu đưa CẢ lô quyền 300
    # chưa tới hạn vào phần khoá ⇒ khoá 800 ⇒ SELL 700 (sai — ăn mất 300cp tới hạn).
    rs = lambda q: {"event_id": "RS-SELF", "credit_date": before(1), "listing_date": plan_date, "qty_hint": q}
    rx = _lots((1000, before(30)), (500, before(30), rs(500)), (300, before(5), rs(300)))
    rx["rights_qty"] = 800
    rx["rights_lots"] = [dict(rs(500), qty=500), dict(rs(300), qty=300)]
    plan, sells = _run_mock(sig, plan_date, {"RGT": (1800, 20000.0, 20000.0)}, sellable={"RGT": 1000},
                            lag_lots={"RGT": rx})
    lk = _notes(plan, "rights_locked")
    check("L7 lô quyền: chỉ lô quyền TỚI HẠN vào phần khoá (500) ⇒ SELL 1.000, không cắt",
          sells.get(("RGT", "LAG"), {}).get("qty") == 1000 and [x["locked_qty"] for x in lk] == [500]
          and not _notes(plan, "capped"), (sells, lk, _notes(plan, "capped")))

    # L8 — fail-safe: thiếu `lots` / entry_date hỏng / Σ lô ≠ qty gộp ⇒ KHÔNG bán, vào blocked (§29)
    pos8 = {t: {"qty": 1000, "marketPrice": 20000.0, "avg_cost": 20000.0} for t in ("NOL", "BADD", "SUMX")}
    lots8 = {"NOL": {"qty": 1000, "entry_date": before(40)},
             "BADD": _lots((500, before(40)), (500, "2026-13-45")),
             "SUMX": dict(_lots((500, before(40)), (400, before(40))), qty=1000)}
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        c8, b8 = aei._lag_bal_candidates(sig_d, pos8, "LAG", lots8, aei.rules.lag_should_exit)
    check("L8 thiếu lots / entry_date hỏng / Σ lệch ⇒ 0 candidate, cả 3 vào blocked có lý do",
          c8 == [] and sorted(b["ticker"] for b in b8) == ["BADD", "NOL", "SUMX"]
          and all(b["reason"] for b in b8), (c8, b8))
    # L8b — 1 mã hỏng KHÔNG chặn mã khác cùng book (fail-safe từng mã)
    lots8b = dict(lots8, GOOD=_lots((1000, before(40))))
    pos8b = dict(pos8, GOOD={"qty": 1000, "marketPrice": 20000.0, "avg_cost": 20000.0})
    with contextlib.redirect_stdout(io.StringIO()):
        c8b, _b = aei._lag_bal_candidates(sig_d, pos8b, "LAG", lots8b, aei.rules.lag_should_exit)
    check("L8b mã hỏng không chặn mã sạch cùng book (GOOD vẫn ra 1.000)",
          [(c[0], c[1]) for c in c8b] == [("GOOD", 1000)], c8b)

    # L9 — stop-loss BAL theo lô: lô 300 giữ 10 phiên + lô 200 mua 1 phiên trước (< min_hold 2),
    # lỗ −25% trên giá vốn broker ⇒ chỉ bán 300 (lô vừa mua không bị cắt ở phiên 0/1).
    sl = _lots((300, before(10)), (200, before(1)))
    plan, sells = _run_mock(sig, plan_date, {"SLX": (500, 20000.0, 15000.0)}, bal_lots={"SLX": sl})
    o = sells.get(("SLX", "BAL"))
    check("L9 stop-loss BAL: chỉ lô đủ min_hold (300) bị bán, lô 1 phiên (200) giữ",
          o is not None and o["qty"] == 300 and "STOP-LOSS" in o["note"], o)

    # L10 — sổ lô THẬT (park_holdings bootstrap, không mock): VPB 282 @64 + 900 @2/1 cùng book LAG,
    # + 1.100 PARK cùng mã ⇒ SELL LAG đúng 282.
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_bootstrap(plan_dir, ACCOUNT, ACCOUNT_NO, before(0), [
            {"ticker": "VPB", "qty": 282, "book": "LAG", "entry_date": before(64), "cost_price_vnd": 20000.0},
            {"ticker": "VPB", "qty": 700, "book": "LAG", "entry_date": before(2), "cost_price_vnd": 25000.0},
            {"ticker": "VPB", "qty": 200, "book": "LAG", "entry_date": before(1), "cost_price_vnd": 25000.0},
            {"ticker": "VPB", "qty": 1100, "book": "PARK", "entry_date": before(90), "cost_price_vnd": 18000.0}])
        write_positions_cost(exec_dir, sig, {"VPB": (2282, 22000.0, 25000.0)}, sellable={"VPB": 1800})
        write_plan(plan_dir, ACCOUNT, plan_date)
        orig = patch_all_e2e(exec_dir, plan_dir, ledger_path, ACCOUNT_NO)
        sp_orig, _calls = install_subprocess_recorder()
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                snap = ps.book_lot_snapshot(ACCOUNT, "LAG", asof=sig)
                aei.process_account(ACCOUNT, plan_date, sig, dry_run=False)
        finally:
            restore_subprocess_recorder(sp_orig)
            restore_all_e2e(orig)
        plan = load_plan_raw(plan_dir, ACCOUNT, plan_date)
        s10 = {(o["ticker"], o["book"]): o["qty"] for o in plan["orders"] if o["side"] == "sell"}
        check("L10 sổ lô THẬT: book_lot_snapshot giữ qty/entry gộp (1.182, lô cũ nhất) + `lots` 3 lô",
              snap[1] and snap[0].get("VPB", {}).get("qty") == 1182
              and snap[0]["VPB"].get("entry_date") == before(64) and len(snap[0]["VPB"].get("lots") or []) == 3,
              snap)
        check("L10 sổ lô THẬT end-to-end: SELL VPB LAG = 282 (không 1.182), PARK không bị bán",
              s10 == {("VPB", "LAG"): 282}, s10)
    finally:
        shutil.rmtree(td, ignore_errors=True)

    # L11 — dòng EOD (portfolio_status.lag_exit_hint) đọc CÙNG sổ lô ⇒ nhóm khớp đúng phần bị bán
    h = ps.lag_exit_hint("VPB", {"VPB": vpb}, sig)
    check("L11 EOD hint VPB: 282cp ĐÃ QUA (64 phiên) + 900cp chưa tới hạn (còn 23 phiên)",
          h is not None and h.startswith("282cp ĐÃ QUA hạn cố định T+25 (64 phiên từ ")
          and "900cp vào " in h and "còn 23 phiên" in h, h)

    # L12 — FIFO lệch thứ tự (arch-review vòng 2, lỗi A; tái hiện /tmp/arch_lot/fifo_hazard.py): lô gốc
    # A 1.000cp bán sau GDKHQ → mua lại B 500cp (3 phiên trước) → credit lô quyền R 200cp KẾ THỪA
    # entry A (tới hạn) nhưng được THÊM VÀO SỔ SAU B. LotBook.sell THẬT trừ theo thứ tự sổ ⇒ bán 200 sẽ
    # trừ vào B. Mô phỏng 4 đêm liên tiếp (asof tiến 1 phiên/đêm, khớp lệnh quyết định vào LotBook
    # thật): bản vá KHÔNG được bán gì (B chưa tới hạn cả 4 đêm), R vào blocked với lý do thứ tự trừ.
    book = ph.LotBook()
    book.buy("XYZ", "LAG", 1000, 20000, before(40), "j")
    book.sell("XYZ", "LAG", 1000, before(10), "j")
    book.buy("XYZ", "LAG", 500, 21000, before(3), "j")
    book.rights_credit({"ticker": "XYZ", "subscribed_qty": 200, "event_id": "E1", "exercise_ratio": 1.0,
                        "credit_date": before(1), "exright_date": before(20), "issue_price_vnd": 10000,
                        "at": "x", "listing_date": before(1)},
                       [{"ticker": "XYZ", "book": "LAG", "entry_date": before(40), "qty": 1000, "play_type": ""}])
    check("L12 tiền đề: sổ LotBook THẬT đặt lô quyền R (entry cũ) SAU lô mua lại B",
          [(l["qty"], bool(l.get("rights_subscription"))) for l in book.lots] == [(500, False), (200, True)],
          book.lots)
    night, sold, nights, reasons = sig_d, 0, [], []
    for _ in range(4):
        lots_x = [{"qty": l["qty"], "entry_date": l["entry_date"],
                   **({"rights_subscription": l["rights_subscription"]} if l.get("rights_subscription") else {})}
                  for l in book.lots if l["ticker"] == "XYZ" and l["book"] == "LAG"]
        snap_x = {"XYZ": {"qty": sum(l["qty"] for l in lots_x), "entry_date": min(l["entry_date"] for l in lots_x),
                          "lots": lots_x}}
        with contextlib.redirect_stdout(io.StringIO()):
            c12, b12 = aei._lag_bal_candidates(
                night, {"XYZ": {"qty": snap_x["XYZ"]["qty"], "marketPrice": 20000.0, "avg_cost": 20000.0}},
                "LAG", snap_x, aei.rules.lag_should_exit)
        q = sum(c[1] for c in c12)
        nights.append(q)
        reasons += [b["reason"] for b in b12 if b["ticker"] == "XYZ"]
        if q:
            book.sell("XYZ", "LAG", q, str(next_trading_day(night)), "bot")
            sold += q
        night = next_trading_day(night)
    check("L12 4 đêm liên tiếp với LotBook thật: KHÔNG bán cp nào (bản cũ: 200/200/100)",
          sold == 0 and nights == [0, 0, 0, 0], nights)
    check("L12b lô quyền 200cp bị giữ vào blocked MỖI đêm, lý do nêu thứ tự trừ lô + lô chưa tới hạn 500cp",
          len(reasons) == 4 and all("giữ 200cp tới hạn" in r and "thứ tự trừ lô" in r and "lô 500cp" in r
                                    for r in reasons), reasons[:1])
    # L12c — end-to-end process_account cùng sổ ⇒ không SELL, blocked có mã XYZ book LAG
    xyz = _lots((500, before(3)), (200, before(40), {"event_id": "E1", "credit_date": before(1),
                                                     "listing_date": before(1)}))
    plan, sells = _run_mock(sig, plan_date, {"XYZ": (700, 20000.0, 20000.0)}, lag_lots={"XYZ": xyz})
    bl = [b for b in _notes(plan, "blocked") if b["ticker"] == "XYZ"]
    check("L12c process_account: không SELL XYZ, blocked (XYZ, LAG) nêu lô bị giữ",
          not sells and len(bl) == 1 and bl[0]["book"] == "LAG" and "thứ tự trừ lô" in bl[0]["reason"], (sells, bl))

    # L13 — lỗi B: BAL 300 @45 + 200 @10, lỗ −25% ⇒ MỘT lệnh BAL 500 (T+45 ∪ stop-loss), note nêu cả hai
    blx = _lots((300, before(45)), (200, before(10)))
    plan, sells = _run_mock(sig, plan_date, {"BLX": (500, 20000.0, 15000.0)}, bal_lots={"BLX": blx})
    o = sells.get(("BLX", "BAL"))
    n_bal = sum(1 for x in plan["orders"] if x["ticker"] == "BLX" and x["side"] == "sell")
    check("L13 BAL 300@45 + 200@10 lỗ −25% ⇒ SELL 500 (một lệnh), note nêu T+45 + STOP-LOSS",
          o is not None and o["qty"] == 500 and n_bal == 1 and "45" in o["note"] and "STOP-LOSS" in o["note"]
          and "200cp lô ≥2 phiên theo stop-loss" in o["note"], o)
    # L14 — lô T+45 + lô KHÔNG đủ điều kiện stop-loss (1 phiên < min_hold) ⇒ chỉ 300
    bly = _lots((300, before(45)), (200, before(1)))
    plan, sells = _run_mock(sig, plan_date, {"BLY": (500, 20000.0, 15000.0)}, bal_lots={"BLY": bly})
    o = sells.get(("BLY", "BAL"))
    check("L14 BAL 300@45 + 200@1 lỗ −25% ⇒ SELL 300 (lô 1 phiên chưa đủ min_hold), không blocked",
          o is not None and o["qty"] == 300 and "STOP-LOSS" in o["note"] and not _notes(plan, "blocked"), o)
    # L14b — lỗ chỉ −10% (không chạm stop-loss) ⇒ chỉ T+45 300, note không nhắc stop-loss
    plan, sells = _run_mock(sig, plan_date, {"BLX": (500, 20000.0, 18000.0)}, bal_lots={"BLX": blx})
    o = sells.get(("BLX", "BAL"))
    check("L14b BAL 300@45 + 200@10 lỗ −10% ⇒ SELL 300 thuần T+45",
          o is not None and o["qty"] == 300 and "STOP-LOSS" not in o["note"], o)
    # L15 — stop-loss + thứ tự sổ: lô 200 @1 phiên ĐỨNG ĐẦU, lô 300 @10 sau, lỗ −25% ⇒ không bán,
    # 300 vào blocked (stop-loss) — không im lặng
    blz = _lots((200, before(1)), (300, before(10)))
    plan, sells = _run_mock(sig, plan_date, {"BLZ": (500, 20000.0, 15000.0)}, bal_lots={"BLZ": blz})
    bl = [b for b in _notes(plan, "blocked") if b["ticker"] == "BLZ"]
    check("L15 stop-loss: lô đủ min_hold nằm sau lô 1 phiên ⇒ không SELL, blocked nêu 300cp bị giữ",
          not sells and len(bl) == 1 and "giữ 300cp tới hạn" in bl[0]["reason"], (sells, bl))

    # L16 — vòng 3: blocked "held" của T+45 không được mâu thuẫn với lệnh gộp stop-loss đã phủ lô đó
    blh = _lots((300, before(50)), (200, before(10)), (100, before(60)))
    plan, sells = _run_mock(sig, plan_date, {"BLH": (600, 20000.0, 15000.0)}, bal_lots={"BLH": blh})
    o = sells.get(("BLH", "BAL"))
    check("L16a BAL [300@50,200@10,100@60] lỗ −25% ⇒ SELL 600 VÀ blocked rỗng (lệnh gộp đã phủ lô giữ)",
          o is not None and o["qty"] == 600 and not _notes(plan, "blocked"), (o, _notes(plan, "blocked")))
    plan, sells = _run_mock(sig, plan_date, {"BLH": (600, 20000.0, 20000.0)}, bal_lots={"BLH": blh})
    o = sells.get(("BLH", "BAL"))
    bl = [b for b in _notes(plan, "blocked") if b["ticker"] == "BLH"]
    check("L16b đối chứng không stop-loss ⇒ SELL 300 và blocked 'giữ 100cp' vẫn còn",
          o is not None and o["qty"] == 300 and len(bl) == 1 and "giữ 100cp tới hạn" in bl[0]["reason"], (o, bl))
    plan, sells = _run_mock(sig, plan_date, {"BLH": (600, 20000.0, 15000.0)}, sellable={"BLH": 500},
                            bal_lots={"BLH": blh})
    o = sells.get(("BLH", "BAL"))
    bl = [b for b in _notes(plan, "blocked") if b["ticker"] == "BLH"]
    check("L16c lệnh gộp bị cap sellable 500<600 ⇒ SELL 500 và blocked 'giữ 100cp' vẫn còn",
          o is not None and o["qty"] == 500 and len(bl) == 1 and "giữ 100cp tới hạn" in bl[0]["reason"], (o, bl))


def run_lot_mutants():
    """Mỗi đột biến trong `LOT_MUTANTS` chạy lại `lot_tests` ở tiến trình con — phải ĐỎ (rc≠0)."""
    print("\n[LOT-MUTANTS]")
    killed = []
    for mid in LOT_MUTANTS:
        env = dict(os.environ, LOT_MUTANT=mid, AUTO_EXIT_TEST_MODE="1", MIKE_BOT_TEST_MODE="1")
        r = subprocess.run([sys.executable, os.path.abspath(__file__)], env=env, capture_output=True,
                           text=True, timeout=600)
        fails = [ln.strip() for ln in r.stdout.splitlines() if ln.strip().startswith("FAIL —")]
        ok = r.returncode != 0 and bool(fails)
        killed.append(ok)
        print(f"  {'KILLED' if ok else 'SURVIVED'} {mid} (rc={r.returncode}, {len(fails)} FAIL"
              + (f": {fails[0][:90]}" if fails else (f"; stderr: {r.stderr.strip()[-200:]}" if r.stderr else ""))
              + ")")
    check(f"LOT-MUTANTS: {sum(killed)}/{len(killed)} đột biến bị giết", all(killed))


def main():
    base = next_trading_day(next_trading_day(__import__("datetime").date(2024, 1, 2)))  # ngày giao dịch chắc chắn hợp lệ
    signal_date = nth_session_after(base, 100)  # đủ chỗ lùi 100 phiên cho mọi test (lot_tests lùi 90)
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
        assert 0 <= n <= idx_signal, f"lùi {n} phiên vượt chuỗi ({idx_signal}) — index âm sẽ quấn vòng"
        return str(chain[idx_signal - n])

    if os.environ.get("LOT_MUTANT"):
        lot_tests(signal_date, plan_date, entry_n_sessions_before)
        print(f"\n{len(PASS)} PASS, {len(FAIL)} FAIL")
        return 1 if FAIL else 0

    lag_exit_entry = entry_n_sessions_before(25)      # đúng mốc — PHẢI exit
    lag_not_yet_entry = entry_n_sessions_before(24)   # thiếu 1 phiên — KHÔNG exit
    bal_exit_entry = entry_n_sessions_before(45)      # đúng mốc BAL — PHẢI exit

    # ---------------- Test 1: LAG @25 exit, LAG @24 giữ nguyên, BAL @45 exit ----------------
    # lots bơm thẳng qua book_lot_snapshot (mock) — xem docstring patch_all(). Journal/`write_journal`
    # KHÔNG còn liên quan tới đường LAG/BAL nữa (process_account đọc entry/qty qua book_lot_snapshot,
    # không qua _first_fill_dates) nên bỏ hẳn, tránh fixture chết gây hiểu nhầm.
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_positions(exec_dir, signal_date_str, {
            "AAA": (1000, 20000.0), "BBB": (500, 15000.0), "CCC": (2000, 30000.0)})
        write_plan(plan_dir, ACCOUNT, plan_date)
        lag_lots = {"AAA": {"qty": 1000, "entry_date": lag_exit_entry},
                    "BBB": {"qty": 500, "entry_date": lag_not_yet_entry}}
        bal_lots = {"CCC": {"qty": 2000, "entry_date": bal_exit_entry}}
        orig = patch_all(exec_dir, plan_dir, ledger_path, lag_lots=lag_lots, bal_lots=bal_lots)
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
            check("Test1: AAA qty đúng sổ lô LAG (1000)", sells[("AAA", "LAG")]["qty"] == 1000)
    finally:
        shutil.rmtree(td, ignore_errors=True)

    # ---------------- Test 1b: qty sổ lô (book_lot_snapshot) KHÁC tổng vị thế broker của mã —
    # mirror ca VPB thật (mã nằm lẫn LAG+PARK): chỉ phần LAG được bán, KHÔNG phải tổng broker ----
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_positions(exec_dir, signal_date_str, {"MIXED": (1800, 20000.0)})  # tổng broker 1800
        write_plan(plan_dir, ACCOUNT, plan_date)
        lag_lots = {"MIXED": {"qty": 700, "entry_date": lag_exit_entry}}   # chỉ 700 là LAG
        orig = patch_all(exec_dir, plan_dir, ledger_path, lag_lots=lag_lots)
        try:
            rc = aei.process_account(ACCOUNT, plan_date, signal_date_str, dry_run=False)
        finally:
            restore_all(orig)
        check("Test1b: rc=0", rc == 0, f"rc={rc}")
        plan = load_plan_raw(plan_dir, ACCOUNT, plan_date)
        sells = {(o["ticker"], o["book"]): o for o in plan["orders"] if o["side"] == "sell"}
        check("Test1b: MIXED có lệnh sell LAG", ("MIXED", "LAG") in sells)
        if ("MIXED", "LAG") in sells:
            check("Test1b: qty = PHẦN LAG (700), KHÔNG PHẢI tổng broker (1800)",
                  sells[("MIXED", "LAG")]["qty"] == 700,
                  f"qty={sells[('MIXED', 'LAG')]['qty']}")
    finally:
        shutil.rmtree(td, ignore_errors=True)

    # ---------------- Test 1c: qty sổ lô > tổng vị thế broker (2 nguồn lệch nhau) ⇒ FAIL-SAFE,
    # KHÔNG chèn (không đoán cắt bớt) ----------------
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_positions(exec_dir, signal_date_str, {"BADQTY": (500, 20000.0)})  # broker chỉ còn 500
        write_plan(plan_dir, ACCOUNT, plan_date)
        lag_lots = {"BADQTY": {"qty": 700, "entry_date": lag_exit_entry}}   # sổ lô nói 700 — LỆCH
        orig = patch_all(exec_dir, plan_dir, ledger_path, lag_lots=lag_lots)
        try:
            rc = aei.process_account(ACCOUNT, plan_date, signal_date_str, dry_run=False)
        finally:
            restore_all(orig)
        check("Test1c: rc=0", rc == 0, f"rc={rc}")
        plan = load_plan_raw(plan_dir, ACCOUNT, plan_date)
        sells = {(o["ticker"], o["book"]) for o in plan["orders"] if o["side"] == "sell"}
        check("Test1c: BADQTY (sổ lô > broker) KHÔNG chèn lệnh", ("BADQTY", "LAG") not in sells,
              f"got={sells}")
        notes1c = plan.get("auto_exit_inject_notes") or []
        blocked1c = (notes1c[-1].get("blocked") or []) if notes1c else []
        check("Test1c: BADQTY xuất hiện trong blocked_notes book=LAG (§29, Mblk — không chỉ "
              "'không chèn')", any(b["ticker"] == "BADQTY" and b["book"] == "LAG"
                                   for b in blocked1c), f"blocked={blocked1c}")
        check("Test1c: entry ghi bởi WRITER THẬT có source=auto_exit_inject (Mwriter_no_source)",
              bool(notes1c) and notes1c[-1].get("source") == "auto_exit_inject", f"notes={notes1c}")
    finally:
        shutil.rmtree(td, ignore_errors=True)

    # ---------------- Test 1d: book_lot_snapshot ok=False (park_holdings KHÔNG đối soát được) ⇒
    # process_account KHÔNG chèn gì cho book đó, rc vẫn 0 (fail-safe, không phải crash) ----------
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_positions(exec_dir, signal_date_str, {"AAA": (1000, 20000.0), "CCC": (2000, 30000.0)})
        write_plan(plan_dir, ACCOUNT, plan_date)
        orig = patch_all(exec_dir, plan_dir, ledger_path,
                         lag_lots={"AAA": {"qty": 1000, "entry_date": lag_exit_entry}},
                         bal_lots={"CCC": {"qty": 2000, "entry_date": bal_exit_entry}},
                         lag_ok=False, bal_ok=True)
        try:
            rc = aei.process_account(ACCOUNT, plan_date, signal_date_str, dry_run=False)
        finally:
            restore_all(orig)
        check("Test1d: rc=0 (fail-safe, không crash)", rc == 0, f"rc={rc}")
        plan = load_plan_raw(plan_dir, ACCOUNT, plan_date)
        sells = {(o["ticker"], o["book"]) for o in plan["orders"] if o["side"] == "sell"}
        check("Test1d: LAG ok=False ⇒ AAA KHÔNG chèn dù tới mốc", ("AAA", "LAG") not in sells,
              f"got={sells}")
        check("Test1d: BAL ok=True KHÔNG bị ảnh hưởng ⇒ CCC vẫn chèn", ("CCC", "BAL") in sells,
              f"got={sells}")
        notes1d = plan.get("auto_exit_inject_notes") or []
        blocked1d = (notes1d[-1].get("blocked") or []) if notes1d else []
        check("Test1d: lỗi kết cấu LAG ghi vào blocked_notes với ticker=None, book=LAG (§29, Mblk)",
              any(b["ticker"] is None and b["book"] == "LAG" for b in blocked1d),
              f"blocked={blocked1d}")
    finally:
        shutil.rmtree(td, ignore_errors=True)

    # ---------------- Test 1e: qty sổ lô BAL > broker ở đường STOP-LOSS (`_bal_stop_loss_candidates`
    # — guard riêng, KHÁC hàm với Test1c vốn chỉ phủ `_lag_bal_candidates`) ⇒ FAIL-SAFE, KHÔNG tính
    # stop-loss ----------------
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_positions_cost(exec_dir, signal_date_str, {"SLBAD": (500, 100000.0, 75000.0)})  # broker 500
        write_plan(plan_dir, ACCOUNT, plan_date)
        bal_lots = {"SLBAD": {"qty": 700, "entry_date": bal_exit_entry}}   # sổ lô nói 700 — LỆCH
        orig = patch_all(exec_dir, plan_dir, ledger_path, bal_lots=bal_lots)
        try:
            rc = aei.process_account(ACCOUNT, plan_date, signal_date_str, dry_run=False)
        finally:
            restore_all(orig)
        check("Test1e: rc=0", rc == 0, f"rc={rc}")
        plan = load_plan_raw(plan_dir, ACCOUNT, plan_date)
        sells = {(o["ticker"], o["book"]) for o in plan["orders"] if o["side"] == "sell"}
        check("Test1e: SLBAD (sổ lô > broker, -25% lỗ) KHÔNG chèn stop-loss",
              ("SLBAD", "BAL") not in sells, f"got={sells}")
        notes1e = plan.get("auto_exit_inject_notes") or []
        blocked1e = (notes1e[-1].get("blocked") or []) if notes1e else []
        check("Test1e: SLBAD xuất hiện trong blocked_notes với lý do stop-loss (§29, Mblk)",
              any(b["ticker"] == "SLBAD" and b["book"] == "BAL" and "(stop-loss)" in b["reason"]
                  for b in blocked1e), f"blocked={blocked1e}")
        # bal_exit_entry (45 phiên) cũng ĐỦ tuổi cho check T+45 THƯỜNG (không chỉ stop-loss) — cả
        # 2 wiring (`bal_qty_blocked` KHÔNG hậu tố + `stoploss_qty_blocked` CÓ hậu tố) đều fire
        # độc lập trên CÙNG `bal_lots`; dòng dưới khẳng định riêng wiring KHÔNG hậu tố cũng được
        # test (gỡ nó không bị Test1e trên che giấu, vì assertion đó chỉ cần entry CÓ hậu tố).
        check("Test1e: SLBAD CŨNG xuất hiện qua wiring T+45 thường (KHÔNG hậu tố stop-loss)",
              any(b["ticker"] == "SLBAD" and b["book"] == "BAL" and "(stop-loss)" not in b["reason"]
                  for b in blocked1e), f"blocked={blocked1e}")
    finally:
        shutil.rmtree(td, ignore_errors=True)

    # ---------------- Test 1f (Mblk3/4/5/7, arch-review vòng 3): `book_lot_snapshot()` TỰ trả
    # per-ticker blocked (mock qua `bal_blocked=`) cho BAL — mã blocked KHÔNG bán, mã KHÁC cùng
    # book (bal_lots) vẫn bán bình thường; blocked_notes ghi đúng ticker/book. Đường DÂY A
    # (book_lot_snapshot's own blocked dict, line 326-327 gốc) — KHÁC đường DÂY B đã test ở
    # Test1c/1e (guard qty-mismatch BÊN TRONG `_lag_bal_candidates`/`_bal_stop_loss_candidates`).
    # Đường A cho LAG đã có e2e thật (Test14/15/20) nhưng cho BAL CHƯA từng test — gỡ wiring
    # `for tk, reason in bal_blocked.items(): _add_blocked(tk, "BAL", reason)` sẽ không bị bắt. --
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_positions(exec_dir, signal_date_str, {
            "BALGOOD": (1000, 20000.0), "BALBAD": (500, 20000.0)})
        write_plan(plan_dir, ACCOUNT, plan_date)
        bal_lots = {"BALGOOD": {"qty": 1000, "entry_date": bal_exit_entry}}
        bal_blocked = {"BALBAD": "selfcheck: book_lot_snapshot reconcile lệch (per-ticker)"}
        orig = patch_all(exec_dir, plan_dir, ledger_path, bal_lots=bal_lots, bal_blocked=bal_blocked)
        try:
            rc = aei.process_account(ACCOUNT, plan_date, signal_date_str, dry_run=False)
        finally:
            restore_all(orig)
        check("Test1f: rc=0", rc == 0, f"rc={rc}")
        plan = load_plan_raw(plan_dir, ACCOUNT, plan_date)
        sells = {(o["ticker"], o["book"]) for o in plan["orders"] if o["side"] == "sell"}
        check("Test1f: BALGOOD (trong lots, không blocked) vẫn bán", ("BALGOOD", "BAL") in sells,
              f"got={sells}")
        check("Test1f: BALBAD (blocked riêng mã qua book_lot_snapshot) KHÔNG bán",
              ("BALBAD", "BAL") not in sells, f"got={sells}")
        notes1f = plan.get("auto_exit_inject_notes") or []
        blocked1f = (notes1f[-1].get("blocked") or []) if notes1f else []
        check("Test1f: BALBAD xuất hiện trong blocked_notes book=BAL (Mblk3/4/5/7)",
              any(b["ticker"] == "BALBAD" and b["book"] == "BAL" for b in blocked1f),
              f"blocked={blocked1f}")
    finally:
        shutil.rmtree(td, ignore_errors=True)

    # ---------------- TestCap (Mcap5, arch-review vòng 3): 2 dòng loan-package CÙNG mã trong raw
    # broker snapshot — `broker_positions_with_cost()` phải CỘNG DỒN qty/sellable, KHÔNG lấy giá
    # trị lô cuối (mirror vị thế vay margin chia nhiều gói nợ cùng 1 mã, DNSE trả nhiều dòng —
    # `write_positions_cost` cũ không dựng được ca này vì dict keyed theo ticker). -------------
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_positions_raw(exec_dir, signal_date_str, [
            {"symbol": "LOANPKG", "openQuantity": 300, "costPrice": 20000.0,
             "marketPrice": 21000.0, "tradeQuantity": 300},
            {"symbol": "LOANPKG", "openQuantity": 300, "costPrice": 20000.0,
             "marketPrice": 21000.0, "tradeQuantity": 300},
        ])
        exec_orig = ps.EXEC_DIR
        ps.EXEC_DIR = exec_dir
        try:
            out = ps.broker_positions_with_cost(ACCOUNT_NO, signal_date_str)
        finally:
            ps.EXEC_DIR = exec_orig
        check("TestCap: qty cộng dồn 2 lô (300+300=600)", out.get("LOANPKG", {}).get("qty") == 600,
              f"out={out}")
        check("TestCap: sellable CỘNG DỒN (300+300=600), KHÔNG lấy lô cuối (Mcap5)",
              out.get("LOANPKG", {}).get("sellable") == 600, f"out={out}")
    finally:
        shutil.rmtree(td, ignore_errors=True)

    # ---------------- Test 2: dedup — chạy lại KHÔNG nhân đôi lệnh ----------------
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_positions(exec_dir, signal_date_str, {"AAA": (1000, 20000.0)})
        write_plan(plan_dir, ACCOUNT, plan_date)
        lag_lots = {"AAA": {"qty": 1000, "entry_date": lag_exit_entry}}
        orig = patch_all(exec_dir, plan_dir, ledger_path, lag_lots=lag_lots)
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
        write_positions(exec_dir, signal_date_str, {"AAA": (1000, 20000.0)})
        write_plan(plan_dir, ACCOUNT, plan_date, approved_by="user")
        before = load_plan_raw(plan_dir, ACCOUNT, plan_date)
        orig = patch_all(exec_dir, plan_dir, ledger_path,
                         lag_lots={"AAA": {"qty": 1000, "entry_date": lag_exit_entry}})
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
        write_positions(exec_dir, signal_date_str, {"AAA": (1000, 20000.0)})
        plan_path = write_plan(plan_dir, ACCOUNT, plan_date)
        plan = load_plan_raw(plan_dir, ACCOUNT, plan_date)
        plan.pop("approved_by", None)
        plan["approved_by_user"] = "user"
        with open(plan_path, "w", encoding="utf-8") as f:
            json.dump(plan, f)
        before = load_plan_raw(plan_dir, ACCOUNT, plan_date)
        orig = patch_all(exec_dir, plan_dir, ledger_path,
                         lag_lots={"AAA": {"qty": 1000, "entry_date": lag_exit_entry}})
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

    # ---------------- Test 8b: mã nằm LẪN book (broker 1600 = CAPIT 900 + book khác 700) → chỉ bán
    # phần CAPIT (900), không bán lố sang book khác (code-quality 2026-10-25) ----------------
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_journal(exec_dir, [])
        write_positions(exec_dir, signal_date_str, {"VNM": (1600, 60000.0)})
        write_plan(plan_dir, ACCOUNT, plan_date)
        write_capit_ledger(ledger_path, {
            "episode_id": "CAPIT-TEST8B", "status": "open", "sessions_held": 61,
            "qty_per_account": {ACCOUNT: {"VNM": 900}}})
        orig = patch_all(exec_dir, plan_dir, ledger_path)
        try:
            rc = aei.process_account(ACCOUNT, plan_date, signal_date_str, dry_run=False)
        finally:
            restore_all(orig)
        plan = load_plan_raw(plan_dir, ACCOUNT, plan_date)
        vnm = [o for o in plan["orders"] if o["book"] == "CAPIT" and o["side"] == "sell" and o["ticker"] == "VNM"]
        check("Test8b: rc=0 và có đúng 1 lệnh sell CAPIT VNM", rc == 0 and len(vnm) == 1, f"rc={rc} n={len(vnm)}")
        check("Test8b: qty = phần CAPIT (900), KHÔNG phải tổng broker (1600)",
              bool(vnm) and vnm[0]["qty"] == 900, f"qty={vnm[0]['qty'] if vnm else None}")
        capped = [c for n in plan.get("auto_exit_inject_notes", []) for c in n.get("capped", [])
                  if c["ticker"] == "VNM" and c["book"] == "CAPIT"]
        check("Test8b: phần dư 700cp được ghi vào auto_exit_inject_notes.capped (không im lặng)",
              len(capped) == 1 and capped[0]["desired_qty"] == 1600 and capped[0]["capped_qty"] == 900, str(capped))
    finally:
        shutil.rmtree(td, ignore_errors=True)

    # ---------------- Test 9: BAL stop-loss -20% trên giá vốn (job Taylor_20260930_111053) —
    # ĐỘC LẬP mốc T+45: entry chỉ 5 phiên trước signal_date (≥min_hold=2), chưa tới T+45 ----------
    bal_recent_entry = entry_n_sessions_before(5)
    bal_lots_t9 = {tk: {"qty": 1000, "entry_date": bal_recent_entry}
                  for tk in ("EXACT20", "UNDER20", "OVER20", "EXITED")}
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_positions_cost(exec_dir, signal_date_str, {
            "EXACT20": (1000, 100000.0, 80000.0),   # pnl = -20.0% đúng boundary → trigger
            "UNDER20": (1000, 100000.0, 80001.0),    # pnl = -19.999% → KHÔNG trigger
            "OVER20": (1000, 100000.0, 75000.0),     # pnl = -25.0% → trigger
            # "EXITED" không còn trong positions — đã thoát qua đường khác, KHÔNG phantom-sell
        })
        write_plan(plan_dir, ACCOUNT, plan_date)
        orig = patch_all(exec_dir, plan_dir, ledger_path, bal_lots=bal_lots_t9)
        try:
            rc = aei.process_account(ACCOUNT, plan_date, signal_date_str, dry_run=False)
        finally:
            restore_all(orig)
        check("Test9: rc=0", rc == 0, f"rc={rc}")
        plan = load_plan_raw(plan_dir, ACCOUNT, plan_date)
        sells = {(o["ticker"], o["book"]) for o in plan["orders"] if o["side"] == "sell"}
        check("Test9: EXACT20 (-20.0%) có lệnh sell (boundary đúng)", ("EXACT20", "BAL") in sells)
        check("Test9: OVER20 (-25.0%) có lệnh sell", ("OVER20", "BAL") in sells)
        check("Test9: UNDER20 (-19.999%) KHÔNG có lệnh sell", ("UNDER20", "BAL") not in sells)
        check("Test9: EXITED (hết vị thế) KHÔNG bị bán khống (phantom-sell guard)",
              ("EXITED", "BAL") not in sells)
    finally:
        shutil.rmtree(td, ignore_errors=True)

    # ---------------- Test 10: BAL stop-loss dedup — không nhân đôi khi chạy lại ----------------
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_positions_cost(exec_dir, signal_date_str, {"EXACT20": (1000, 100000.0, 80000.0)})
        write_plan(plan_dir, ACCOUNT, plan_date)
        orig = patch_all(exec_dir, plan_dir, ledger_path,
                         bal_lots={"EXACT20": {"qty": 1000, "entry_date": bal_recent_entry}})
        try:
            aei.process_account(ACCOUNT, plan_date, signal_date_str, dry_run=False)
            aei.process_account(ACCOUNT, plan_date, signal_date_str, dry_run=False)
        finally:
            restore_all(orig)
        plan = load_plan_raw(plan_dir, ACCOUNT, plan_date)
        n_sell = sum(1 for o in plan["orders"] if o["ticker"] == "EXACT20" and o["side"] == "sell")
        check("Test10: chạy 2 lần KHÔNG nhân đôi lệnh stop-loss", n_sell == 1, f"count={n_sell}")
    finally:
        shutil.rmtree(td, ignore_errors=True)

    # ---------------- Test 11: BAL stop-loss min_hold=2 — lỗ -25% nhưng mới giữ 1 phiên KHÔNG
    # trigger (pin chưa từng kiểm chứng stop-loss ở phiên 0/1, quant-skeptic 2026-09-30) ----------
    bal_1session_entry = entry_n_sessions_before(1)
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_positions_cost(exec_dir, signal_date_str, {"TOOFRESH": (1000, 100000.0, 75000.0)})
        write_plan(plan_dir, ACCOUNT, plan_date)
        orig = patch_all(exec_dir, plan_dir, ledger_path,
                         bal_lots={"TOOFRESH": {"qty": 1000, "entry_date": bal_1session_entry}})
        try:
            rc = aei.process_account(ACCOUNT, plan_date, signal_date_str, dry_run=False)
        finally:
            restore_all(orig)
        check("Test11: rc=0", rc == 0, f"rc={rc}")
        plan = load_plan_raw(plan_dir, ACCOUNT, plan_date)
        sells = {(o["ticker"], o["book"]) for o in plan["orders"] if o["side"] == "sell"}
        check("Test11: TOOFRESH (-25%, chỉ 1 phiên) KHÔNG bán (chưa đủ min_hold=2)",
              ("TOOFRESH", "BAL") not in sells, f"got={sells}")
    finally:
        shutil.rmtree(td, ignore_errors=True)

    # ---------------- Test 12-14: `book_lot_snapshot()` THẬT — gọi `park_holdings()` thật qua
    # bootstrap+FIFO (`broker=`/`corp_actions=` bơm tay để bypass DNSE/BQ live I/O, mirror
    # `compute_park_trim_selfcheck.py`), KHÔNG mock `aei.book_lot_snapshot` như Test1-11 ----------
    day0 = str(entry_n_sessions_before(60))

    # Test 12: vị thế mua CHỈ qua bootstrap, KHÔNG journal nào — mirror ca CSV/ZaloPay thật (mua
    # trước khi journal có cột `book`, 2026-08-04): book_lot_snapshot vẫn phải THẤY nó.
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_bootstrap(plan_dir, ACCOUNT, ACCOUNT_NO, day0, [
            {"ticker": "OLDBUY", "qty": 800, "book": "LAG", "entry_date": day0,
             "cost_price_vnd": 20000.0}])
        prof_orig = patch_account_profile(ACCOUNT_NO)
        try:
            lots, ok, reason, blocked = ps.book_lot_snapshot(
                ACCOUNT, "LAG", asof=signal_date_str, plan_dir=plan_dir, exec_dir=exec_dir,
                broker=({"OLDBUY": {"qty": 800, "market_price": 20000.0}}, 0.0, {}),
                corp_actions=[])
        finally:
            restore_account_profile(prof_orig)
        check("Test12: ok=True (sổ lô đối soát khớp)", ok is True, f"reason={reason}")
        check("Test12: OLDBUY thấy được dù KHÔNG journal nào (chỉ bootstrap)",
              lots.get("OLDBUY", {}).get("qty") == 800, f"lots={lots}")
        check("Test12: entry_date = ngày 0 bootstrap", lots.get("OLDBUY", {}).get("entry_date") == day0,
              f"lots={lots}")
    finally:
        shutil.rmtree(td, ignore_errors=True)

    # Test 13: mã nằm lẫn 2 book cùng lúc qua bootstrap — mirror ca VPB thật (LAG 700 + PARK 1100,
    # CÙNG mã) — book_lot_snapshot("LAG") và book_lot_snapshot("PARK") phải TÁCH đúng từng phần,
    # không phải tổng 1800.
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_bootstrap(plan_dir, ACCOUNT, ACCOUNT_NO, day0, [
            {"ticker": "VPB", "qty": 700, "book": "LAG", "entry_date": day0,
             "cost_price_vnd": 20000.0},
            {"ticker": "VPB", "qty": 1100, "book": "PARK", "entry_date": day0,
             "cost_price_vnd": 18000.0}])
        prof_orig = patch_account_profile(ACCOUNT_NO)
        try:
            broker = ({"VPB": {"qty": 1800, "market_price": 21000.0}}, 0.0, {})
            lag_lots, lag_ok, _, lag_blk = ps.book_lot_snapshot(
                ACCOUNT, "LAG", asof=signal_date_str, plan_dir=plan_dir, exec_dir=exec_dir,
                broker=broker, corp_actions=[])
            park_lots, park_ok, _, park_blk = ps.book_lot_snapshot(
                ACCOUNT, "PARK", asof=signal_date_str, plan_dir=plan_dir, exec_dir=exec_dir,
                broker=broker, corp_actions=[])
        finally:
            restore_account_profile(prof_orig)
        check("Test13: LAG ok=True", lag_ok is True)
        check("Test13: VPB phần LAG = 700 (KHÔNG PHẢI tổng broker 1800)",
              lag_lots.get("VPB", {}).get("qty") == 700, f"lag_lots={lag_lots}")
        check("Test13: PARK ok=True", park_ok is True)
        check("Test13: VPB phần PARK = 1100", park_lots.get("VPB", {}).get("qty") == 1100,
              f"park_lots={park_lots}")
    finally:
        shutil.rmtree(td, ignore_errors=True)

    # Test 14: broker báo qty KHÁC tổng sổ lô CHO 1 MÃ (reconcile lệch) ⇒ ok=True (park_holdings
    # tự nó KHÔNG lỗi kết cấu), nhưng mã đó bị BLOCKED riêng (arch-review vòng 2: fail-safe TỪNG
    # MÃ, không phải cả book) — mirror ca thật SpaceX TPB 200 (ledger) vs 230 (broker).
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_bootstrap(plan_dir, ACCOUNT, ACCOUNT_NO, day0, [
            {"ticker": "MISMATCH", "qty": 1000, "book": "LAG", "entry_date": day0,
             "cost_price_vnd": 20000.0}])
        prof_orig = patch_account_profile(ACCOUNT_NO)
        try:
            lots, ok, reason, blocked = ps.book_lot_snapshot(
                ACCOUNT, "LAG", asof=signal_date_str, plan_dir=plan_dir, exec_dir=exec_dir,
                broker=({"MISMATCH": {"qty": 900, "market_price": 20000.0}}, 0.0, {}),
                corp_actions=[])
        finally:
            restore_account_profile(prof_orig)
        check("Test14: ok=True (park_holdings tự nó không lỗi kết cấu)", ok is True,
              f"ok={ok} reason={reason}")
        check("Test14: MISMATCH KHÔNG nằm trong lots (bị block riêng mã)",
              "MISMATCH" not in lots, f"lots={lots}")
        check("Test14: MISMATCH nằm trong blocked, lý do nhắc reconcile lệch",
              "MISMATCH" in blocked and "lệch" in blocked["MISMATCH"],
              f"blocked={blocked}")
    finally:
        shutil.rmtree(td, ignore_errors=True)

    # Test 15: mã lệch reconcile KHÔNG chặn các mã KHÁC cùng book — fail-safe TỪNG MÃ, không cả
    # book (arch-review vòng 2, required change #1).
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_bootstrap(plan_dir, ACCOUNT, ACCOUNT_NO, day0, [
            {"ticker": "MISMATCH2", "qty": 1000, "book": "LAG", "entry_date": day0,
             "cost_price_vnd": 20000.0},
            {"ticker": "CLEAN", "qty": 500, "book": "LAG", "entry_date": day0,
             "cost_price_vnd": 20000.0}])
        prof_orig = patch_account_profile(ACCOUNT_NO)
        try:
            lots, ok, reason, blocked = ps.book_lot_snapshot(
                ACCOUNT, "LAG", asof=signal_date_str, plan_dir=plan_dir, exec_dir=exec_dir,
                broker=({"MISMATCH2": {"qty": 900, "market_price": 20000.0},
                         "CLEAN": {"qty": 500, "market_price": 20000.0}}, 0.0, {}),
                corp_actions=[])
        finally:
            restore_account_profile(prof_orig)
        check("Test15: ok=True", ok is True, f"ok={ok} reason={reason}")
        check("Test15: CLEAN (mã KHÔNG lệch) vẫn ra lots bình thường",
              lots.get("CLEAN", {}).get("qty") == 500, f"lots={lots}")
        check("Test15: MISMATCH2 (mã lệch) bị block riêng, KHÔNG kéo CLEAN theo",
              "MISMATCH2" in blocked and "MISMATCH2" not in lots, f"blocked={blocked} lots={lots}")
    finally:
        shutil.rmtree(td, ignore_errors=True)

    # ---------------- Test 16 (Mb+Mc, arch-review vòng 2): NHIỀU lô CÙNG ticker+book cộng dồn
    # qty, entry_date = lô SỚM NHẤT (không phải gần nhất) — mirror ca VPI 4 lô thật cùng book.
    # Mutation Mb (min→max entry_date) hoặc Mc (không cộng, chỉ giữ 1 lô) đều làm sai kết quả. ---
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_bootstrap(plan_dir, ACCOUNT, ACCOUNT_NO, day0, [
            {"ticker": "VPI", "qty": 300, "book": "BAL", "entry_date": day0,
             "cost_price_vnd": 20000.0},
            {"ticker": "VPI", "qty": 150, "book": "BAL", "entry_date": entry_n_sessions_before(55),
             "cost_price_vnd": 20000.0},
            {"ticker": "VPI", "qty": 250, "book": "BAL", "entry_date": entry_n_sessions_before(50),
             "cost_price_vnd": 20000.0},
            {"ticker": "VPI", "qty": 100, "book": "BAL", "entry_date": entry_n_sessions_before(45),
             "cost_price_vnd": 20000.0}])
        prof_orig = patch_account_profile(ACCOUNT_NO)
        try:
            lots, ok, reason, blocked = ps.book_lot_snapshot(
                ACCOUNT, "BAL", asof=signal_date_str, plan_dir=plan_dir, exec_dir=exec_dir,
                broker=({"VPI": {"qty": 800, "market_price": 20000.0}}, 0.0, {}), corp_actions=[])
        finally:
            restore_account_profile(prof_orig)
        check("Test16: ok=True", ok is True, f"reason={reason}")
        check("Test16: VPI qty = CỘNG DỒN 4 lô (300+150+250+100=800)",
              lots.get("VPI", {}).get("qty") == 800, f"lots={lots}")
        check("Test16: VPI entry_date = lô SỚM NHẤT (day0), không phải lô gần nhất",
              lots.get("VPI", {}).get("entry_date") == day0, f"lots={lots}")
    finally:
        shutil.rmtree(td, ignore_errors=True)

    # ---------------- Test 17 (Mi, arch-review vòng 2): stop-loss CHỈ bán phần BAL khi ticker
    # nằm lẫn BAL+PARK cùng lúc — KHÔNG bán khống phần PARK theo tổng broker. ----------------
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_bootstrap(plan_dir, ACCOUNT, ACCOUNT_NO, day0, [
            {"ticker": "VPI2", "qty": 700, "book": "BAL", "entry_date": bal_exit_entry,
             "cost_price_vnd": 100000.0},
            {"ticker": "VPI2", "qty": 300, "book": "PARK", "entry_date": bal_exit_entry,
             "cost_price_vnd": 100000.0}])
        prof_orig = patch_account_profile(ACCOUNT_NO)
        try:
            bal_lots, bal_ok2, _, _ = ps.book_lot_snapshot(
                ACCOUNT, "BAL", asof=signal_date_str, plan_dir=plan_dir, exec_dir=exec_dir,
                broker=({"VPI2": {"qty": 1000, "market_price": 75000.0}}, 0.0, {}), corp_actions=[])
        finally:
            restore_account_profile(prof_orig)
        check("Test17: BAL ok=True", bal_ok2 is True)
        check("Test17: VPI2 phần BAL = 700 (KHÔNG PHẢI tổng broker 1000)",
              bal_lots.get("VPI2", {}).get("qty") == 700, f"bal_lots={bal_lots}")
        positions17 = {"VPI2": {"qty": 1000, "marketPrice": 75000.0, "avg_cost": 100000.0}}  # -25%
        out17, blocked17 = aei._bal_stop_loss_candidates(
            dt.date.fromisoformat(signal_date_str), positions17, bal_lots)
        check("Test17: stop-loss trả đúng 1 candidate", len(out17) == 1, f"out={out17}")
        if out17:
            check("Test17: qty stop-loss = PHẦN BAL (700), KHÔNG PHẢI tổng broker (1000)",
                  out17[0][1] == 700, f"out={out17}")
    finally:
        shutil.rmtree(td, ignore_errors=True)

    # ---------------- Test 18 (required change #4): Σ SELL cross-book vượt sellable
    # (tradeQuantity) ⇒ CẮT phần LAG còn lại, KHÔNG bỏ qua hẳn — mirror ca thật ZaloPay 02/10 VPB
    # (PARKMERGE-SELL 300 PARK + LAG 882 > 900 sellable). ----------------
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_positions_cost(exec_dir, signal_date_str, {"VPB": (1182, 20000.0, 20000.0)},
                             sellable={"VPB": 900})
        write_plan(plan_dir, ACCOUNT, plan_date,
                  orders=[existing_sell_order("VPB", 300, "PARK", "PARKMERGE-SELL-VPB")])
        lag_lots = {"VPB": {"qty": 882, "entry_date": lag_exit_entry}}
        orig = patch_all(exec_dir, plan_dir, ledger_path, lag_lots=lag_lots)
        sp_orig, sp_calls = install_subprocess_recorder()
        try:
            rc = aei.process_account(ACCOUNT, plan_date, signal_date_str, dry_run=False)
        finally:
            restore_subprocess_recorder(sp_orig)
            restore_all(orig)
        check("Test18: rc=0", rc == 0, f"rc={rc}")
        check("Test18: AUTO_EXIT_TEST_MODE=1 ⇒ 0 subprocess.run thật dù có capped (Mguard_block_alert)",
              len(sp_calls) == 0, f"calls={sp_calls}")
        plan = load_plan_raw(plan_dir, ACCOUNT, plan_date)
        lag_sell = next((o for o in plan["orders"]
                         if o["ticker"] == "VPB" and o["book"] == "LAG"), None)
        check("Test18: VPB LAG có lệnh sell (bị CẮT, KHÔNG bỏ hẳn)", lag_sell is not None)
        if lag_sell:
            check("Test18: qty bị cắt còn 600 (900 sellable − 300 PARK đã có)",
                  lag_sell["qty"] == 600, f"qty={lag_sell['qty']}")
        notes18 = plan.get("auto_exit_inject_notes") or []
        capped18 = (notes18[-1].get("capped") or []) if notes18 else []
        check("Test18: capped_notes ghi lại mã bị cắt (§29)",
              any(c["ticker"] == "VPB" for c in capped18), f"capped={capped18}")
        check("Test18: entry ghi bởi WRITER THẬT có source=auto_exit_inject (Mwriter_no_source)",
              bool(notes18) and notes18[-1].get("source") == "auto_exit_inject", f"notes={notes18}")
    finally:
        shutil.rmtree(td, ignore_errors=True)

    # ---------------- Test 19: Σ SELL cross-book đã DÙNG HẾT sellable ⇒ LAG bị cắt về 0 (KHÔNG
    # chèn lệnh nào), nhưng VẪN phải hiện ra trong capped_notes — bản cũ sẽ lặng lẽ in "không có
    # candidate" dù THỰC RA có candidate bị chặn hoàn toàn (đúng bug arch-review mô phỏng). ------
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_positions_cost(exec_dir, signal_date_str, {"VPB2": (1182, 20000.0, 20000.0)},
                             sellable={"VPB2": 300})
        write_plan(plan_dir, ACCOUNT, plan_date,
                  orders=[existing_sell_order("VPB2", 300, "PARK", "PARKMERGE-SELL-VPB2")])
        lag_lots = {"VPB2": {"qty": 882, "entry_date": lag_exit_entry}}
        orig = patch_all(exec_dir, plan_dir, ledger_path, lag_lots=lag_lots)
        sp_orig, sp_calls = install_subprocess_recorder()
        try:
            rc = aei.process_account(ACCOUNT, plan_date, signal_date_str, dry_run=False)
        finally:
            restore_subprocess_recorder(sp_orig)
            restore_all(orig)
        check("Test19: rc=0", rc == 0, f"rc={rc}")
        check("Test19: AUTO_EXIT_TEST_MODE=1 ⇒ 0 subprocess.run thật dù capped về 0 (Mguard_block_alert)",
              len(sp_calls) == 0, f"calls={sp_calls}")
        plan = load_plan_raw(plan_dir, ACCOUNT, plan_date)
        lag_sell = next((o for o in plan["orders"]
                         if o["ticker"] == "VPB2" and o["book"] == "LAG"), None)
        check("Test19: VPB2 LAG KHÔNG có lệnh sell (hết chỗ sellable)", lag_sell is None)
        notes19 = plan.get("auto_exit_inject_notes") or []
        capped19 = (notes19[-1].get("capped") or []) if notes19 else []
        check("Test19: dù KHÔNG chèn lệnh, vẫn ghi capped_notes (không lặng lẽ biến mất, §29)",
              any(c["ticker"] == "VPB2" and c["capped_qty"] == 0 for c in capped19),
              f"capped={capped19}")
    finally:
        shutil.rmtree(td, ignore_errors=True)

    # ---------------- Test 20 (Ma, end-to-end, required change #3): process_account dùng
    # book_lot_snapshot THẬT (không mock) — mã reconcile-lệch trong book LAG KHÔNG được bán dù
    # tới mốc, mã KHÁC CÙNG book (sạch) vẫn bán bình thường — fail-safe TỪNG MÃ chạy xuyên suốt
    # tới tận plan cuối, không chỉ ở lớp book_lot_snapshot. ----------------
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_bootstrap(plan_dir, ACCOUNT, ACCOUNT_NO, day0, [
            {"ticker": "BADTK", "qty": 1000, "book": "LAG", "entry_date": day0,
             "cost_price_vnd": 20000.0},
            {"ticker": "GOODTK", "qty": 500, "book": "LAG", "entry_date": day0,
             "cost_price_vnd": 20000.0}])
        write_positions_cost(exec_dir, signal_date_str,
                             {"BADTK": (900, 20000.0, 20000.0),   # broker 900 ≠ sổ lô 1000 — lệch
                              "GOODTK": (500, 20000.0, 20000.0)})
        write_plan(plan_dir, ACCOUNT, plan_date)
        orig = patch_all_e2e(exec_dir, plan_dir, ledger_path, ACCOUNT_NO)
        sp_orig, sp_calls = install_subprocess_recorder()
        try:
            rc = aei.process_account(ACCOUNT, plan_date, signal_date_str, dry_run=False)
        finally:
            restore_subprocess_recorder(sp_orig)
            restore_all_e2e(orig)
        check("Test20: rc=0", rc == 0, f"rc={rc}")
        check("Test20: AUTO_EXIT_TEST_MODE=1 ⇒ 0 subprocess.run thật dù có blocked (Mguard_block_alert)",
              len(sp_calls) == 0, f"calls={sp_calls}")
        plan = load_plan_raw(plan_dir, ACCOUNT, plan_date)
        sells20 = {(o["ticker"], o["book"]) for o in plan["orders"] if o["side"] == "sell"}
        check("Test20: BADTK (lệch reconcile) KHÔNG bán dù tới mốc T+25",
              ("BADTK", "LAG") not in sells20, f"sells={sells20}")
        check("Test20: GOODTK (sạch, CÙNG book) vẫn bán bình thường",
              ("GOODTK", "LAG") in sells20, f"sells={sells20}")
        notes20 = plan.get("auto_exit_inject_notes") or []
        blocked20 = (notes20[-1].get("blocked") or []) if notes20 else []
        check("Test20: BADTK hiện ra trong blocked_notes (§29)",
              any(b["ticker"] == "BADTK" for b in blocked20), f"blocked={blocked20}")
    finally:
        shutil.rmtree(td, ignore_errors=True)

    # ---------------- Test 21 (end-to-end, corp-action ×1.2604104, required change #3): mirror
    # ca VPB production thật — bootstrap 700cp LAG, sự kiện thưởng ×1.2604104 ⇒
    # floor(700×1.2604104)=882cp, giữ ≥25 phiên tại signal_date ⇒ đề xuất bán ĐÚNG 882cp (SAU
    # corp-action, không phải 700cp bootstrap gốc). ----------------
    vpb_entry = str(entry_n_sessions_before(40))
    vpb_ex_date = str(entry_n_sessions_before(35))
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_bootstrap(plan_dir, ACCOUNT, ACCOUNT_NO, vpb_entry, [
            {"ticker": "VPB", "qty": 700, "book": "LAG", "entry_date": vpb_entry,
             "cost_price_vnd": 20000.0}])
        vpb_action = ca.validate({
            "ticker": "VPB", "event_type": "STOCK_DIVIDEND", "qty_multiplier": 1.2604104,
            "ex_date": vpb_ex_date, "broker_effective_ts": f"{vpb_ex_date}T00:00:00",
            "_status": "CONFIRMED"})
        write_positions_cost(exec_dir, signal_date_str, {"VPB": (882, 25000.0, 27800.0)})
        write_plan(plan_dir, ACCOUNT, plan_date)
        orig = patch_all_e2e(exec_dir, plan_dir, ledger_path, ACCOUNT_NO,
                             corp_actions=[vpb_action])
        try:
            rc = aei.process_account(ACCOUNT, plan_date, signal_date_str, dry_run=False)
        finally:
            restore_all_e2e(orig)
        check("Test21: rc=0", rc == 0, f"rc={rc}")
        plan = load_plan_raw(plan_dir, ACCOUNT, plan_date)
        vpb_sell = next((o for o in plan["orders"]
                         if o["ticker"] == "VPB" and o["book"] == "LAG"), None)
        check("Test21: VPB LAG có lệnh sell", vpb_sell is not None)
        if vpb_sell:
            check("Test21: qty = 882 (700×1.2604104 floor, SAU corp-action, không phải 700 cũ)",
                  vpb_sell["qty"] == 882, f"qty={vpb_sell['qty']}")
    finally:
        shutil.rmtree(td, ignore_errors=True)

    # ---------------- Test 22 (Mguard_alert_never_sent, arch-review vòng 3): `_send_block_alert`
    # PHẢI được GỌI đúng 1 lần khi có blocked/capped + dry_run=False, 0 lần khi dry_run=True — test
    # CALL SITE trong process_account (KHÁC Test18/19/20 vốn test subprocess.run BÊN TRONG hàm đó,
    # test riêng đúng 1 lớp). Monkeypatch TRỰC TIẾP `aei._send_block_alert` bằng recorder, KHÔNG
    # chạm subprocess — bỏ `AUTO_EXIT_TEST_MODE` không ảnh hưởng vì hàm bị thay hẳn. -------------
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_positions(exec_dir, signal_date_str, {"BADQTY22": (500, 20000.0)})
        write_plan(plan_dir, ACCOUNT, plan_date)
        lag_lots = {"BADQTY22": {"qty": 700, "entry_date": lag_exit_entry}}  # sổ lô > broker — blocked
        orig = patch_all(exec_dir, plan_dir, ledger_path, lag_lots=lag_lots)
        sba_orig = aei._send_block_alert
        sba_calls = []
        aei._send_block_alert = lambda *a, **kw: sba_calls.append((a, kw))
        try:
            aei.process_account(ACCOUNT, plan_date, signal_date_str, dry_run=True)
            check("Test22: dry_run=True ⇒ _send_block_alert KHÔNG được gọi",
                  len(sba_calls) == 0, f"calls={len(sba_calls)}")
            rc = aei.process_account(ACCOUNT, plan_date, signal_date_str, dry_run=False)
            check("Test22: rc=0", rc == 0, f"rc={rc}")
            check("Test22: dry_run=False + có blocked ⇒ _send_block_alert gọi ĐÚNG 1 LẦN "
                  "(Mguard_alert_never_sent)", len(sba_calls) == 1, f"calls={len(sba_calls)}")
        finally:
            aei._send_block_alert = sba_orig
            restore_all(orig)
    finally:
        shutil.rmtree(td, ignore_errors=True)

    # ---------------- Test 23 (arch-review vòng 4): `_new_block_alert_lines` — khoá dedup PHẢI
    # theo NỘI DUNG (reason/capped_qty), KHÔNG chỉ (ticker,book) — nội dung đổi trong CÙNG ngày
    # (lượt chạy sau nói lý do khác, hoặc cắt sâu hơn) vẫn phải báo lại; CÙNG ngày + CÙNG nội
    # dung mới bị nuốt; NGÀY khác luôn báo lại dù nội dung cũ (Mdedup_never_skip = nuốt mọi thứ
    # mãi mãi; Mdedup_always_skip = không bao giờ nuốt gì, mất tác dụng dedup). --------------
    print("\n[Test23] _new_block_alert_lines — dedup theo (ticker,book,reason/capped_qty) tới khi nội dung đổi")
    _tmp_dir23 = tempfile.mkdtemp(prefix="aei_dedup_")
    _state_path23 = os.path.join(_tmp_dir23, "state.json")
    _orig_state_path23 = aei.BLOCK_ALERT_STATE_PATH
    aei.BLOCK_ALERT_STATE_PATH = _state_path23
    try:
        _blocked_a = [{"ticker": "DEDUP1", "book": "LAG", "reason": "lý do A"}]
        lines_a, state_a = aei._new_block_alert_lines("DedupAcct", _blocked_a, [], "2026-10-01")
        check("Test23a: lần đầu trong ngày ⇒ có dòng mới", len(lines_a) == 1, f"lines={lines_a}")
        with open(_state_path23, "w", encoding="utf-8") as f:
            json.dump(state_a, f)

        lines_b, _ = aei._new_block_alert_lines("DedupAcct", _blocked_a, [], "2026-10-01")
        check("Test23b: CÙNG ngày + CÙNG (ticker,book,reason) ⇒ bị nuốt (Mdedup_never_skip chết)",
              len(lines_b) == 0, f"lines={lines_b}")

        _blocked_c = [{"ticker": "DEDUP1", "book": "LAG", "reason": "lý do B — ĐỔI nội dung"}]
        lines_c, _ = aei._new_block_alert_lines("DedupAcct", _blocked_c, [], "2026-10-01")
        check("Test23c: CÙNG ngày nhưng reason ĐỔI ⇒ vẫn báo lại (khoá theo NỘI DUNG, "
              "Mdedup_always_skip chết)", len(lines_c) == 1, f"lines={lines_c}")

        lines_d, _ = aei._new_block_alert_lines("DedupAcct", _blocked_a, [], "2026-10-02")
        check("Test23d: ngày KHÁC + nội dung CŨ ⇒ vẫn bị nuốt (dedup tới khi nội dung đổi, "
              "Mdedup_by_day chết)", len(lines_d) == 0, f"lines={lines_d}")

        _, state_empty = aei._new_block_alert_lines("DedupAcct", [], [], "2026-10-02")
        check("Test23h: lượt không còn mã nào ⇒ state tỉa khoá cũ",
              state_empty.get("DedupAcct") == {}, f"state={state_empty}")
        with open(_state_path23, "w", encoding="utf-8") as f:
            json.dump(state_empty, f)
        lines_i, _ = aei._new_block_alert_lines("DedupAcct", _blocked_a, [], "2026-10-03")
        check("Test23i: mã biến mất rồi xuất hiện lại ⇒ báo lại (Mdedup_never_prune chết)",
              len(lines_i) == 1, f"lines={lines_i}")
        with open(_state_path23, "w", encoding="utf-8") as f:
            json.dump(state_a, f)
        _b_other = [{"ticker": "DEDUP9", "book": "LAG", "reason": "mã khác"}]
        lines_j, state_j = aei._new_block_alert_lines("DedupAcct", _blocked_a + _b_other, [], "2026-10-04")
        check("Test23j: 1 mã cũ + 1 mã mới ⇒ chỉ báo mã mới, giữ khoá cũ",
              len(lines_j) == 1 and "DEDUP9" in lines_j[0] and len(state_j["DedupAcct"]) == 2,
              f"lines={lines_j}")

        _capped_a = [{"ticker": "DEDUP2", "book": "BAL", "desired_qty": 1000, "capped_qty": 600}]
        lines_e, state_e = aei._new_block_alert_lines("DedupAcct", [], _capped_a, "2026-10-03")
        check("Test23e: capped lần đầu trong ngày ⇒ có dòng mới", len(lines_e) == 1, f"lines={lines_e}")
        with open(_state_path23, "w", encoding="utf-8") as f:
            json.dump(state_e, f)
        lines_f, _ = aei._new_block_alert_lines("DedupAcct", [], _capped_a, "2026-10-03")
        check("Test23f: capped CÙNG ngày + CÙNG capped_qty ⇒ bị nuốt", len(lines_f) == 0, f"lines={lines_f}")

        _capped_b = [{"ticker": "DEDUP2", "book": "BAL", "desired_qty": 1000, "capped_qty": 300}]
        lines_g, _ = aei._new_block_alert_lines("DedupAcct", [], _capped_b, "2026-10-03")
        check("Test23g: capped_qty ĐỔI trong cùng ngày (600→300, lượt sau cắt sâu hơn) ⇒ vẫn báo lại",
              len(lines_g) == 1, f"lines={lines_g}")
    finally:
        aei.BLOCK_ALERT_STATE_PATH = _orig_state_path23
        shutil.rmtree(_tmp_dir23, ignore_errors=True)

    # ---------------- Test 24 (arch-review vòng 4): `_send_block_alert` — notify_thread.sh phải
    # được gọi với ĐÚNG topic 'trading_daily' (Mnotify_topic), và dedup-state CHỈ được ghi SAU khi
    # notify_thread xác nhận rc=0 (Mnotify_removed) — bug gốc: state ghi TRƯỚC + `check=False` bỏ
    # qua returncode ⇒ bridge lỗi (rc=1) vẫn bị coi "đã alert hôm nay", lượt chạy lại cùng ngày
    # KHÔNG gửi lại ⇒ cảnh báo §29 mất im lặng. Recorder tự trả rc theo TÊN script, không chạm
    # subprocess thật — guard `AUTO_EXIT_TEST_MODE` phải tạm BỎ để chạy được qua nhánh gửi thật
    # (test riêng NÀY mô phỏng "guard đã qua", khác Test18-22 test chính guard). -------------
    print("\n[Test24] _send_block_alert — notify_thread topic đúng + dedup chỉ ghi khi rc=0")

    def _recorder_rc(rc_notify):
        calls = []

        def _fake(cmd, *a, **kw):
            calls.append(cmd)
            script = os.path.basename(cmd[0]) if cmd else ""
            if script == "notify_thread.sh":
                return subprocess.CompletedProcess(
                    cmd, rc_notify, "",
                    "" if rc_notify == 0 else "selfcheck: giả lập notify_thread lỗi")
            return subprocess.CompletedProcess(cmd, 0, "", "")
        return _fake, calls

    _tmp_dir24 = tempfile.mkdtemp(prefix="aei_sba_")
    _state_path24 = os.path.join(_tmp_dir24, "state.json")
    _orig_env_tm = os.environ.pop("AUTO_EXIT_TEST_MODE", None)
    _orig_sp_run24 = aei.subprocess.run
    _orig_state_path24 = aei.BLOCK_ALERT_STATE_PATH
    aei.BLOCK_ALERT_STATE_PATH = _state_path24
    try:
        fake_ok, calls_ok = _recorder_rc(0)
        aei.subprocess.run = fake_ok
        aei._send_block_alert("RecAcct", [{"ticker": "REC1", "book": "LAG", "reason": "r"}], [])
        _notify_calls = [c for c in calls_ok if os.path.basename(c[0]) == "notify_thread.sh"]
        check("Test24a: notify_thread được gọi ĐÚNG 1 LẦN với topic 'trading_daily' (Mnotify_topic)",
              len(_notify_calls) == 1 and _notify_calls[0][-1] == "trading_daily",
              f"calls={_notify_calls}")
        check("Test24b: notify rc=0 ⇒ state ĐƯỢC ghi", os.path.exists(_state_path24))

        if os.path.exists(_state_path24):
            os.remove(_state_path24)
        fake_fail, calls_fail = _recorder_rc(1)
        aei.subprocess.run = fake_fail
        aei._send_block_alert("RecAcct", [{"ticker": "REC2", "book": "LAG", "reason": "r2"}], [])
        _notify_calls_fail = [c for c in calls_fail if os.path.basename(c[0]) == "notify_thread.sh"]
        check("Test24c: notify_thread vẫn được GỌI dù sẽ rc=1 (không bị skip nhầm)",
              len(_notify_calls_fail) == 1)
        check("Test24d: notify rc=1 (bridge lỗi) ⇒ KHÔNG ghi state — cảnh báo không mất im lặng "
              "(Mnotify_removed chết nếu guard rc bị bỏ)",
              not os.path.exists(_state_path24))
    finally:
        aei.subprocess.run = _orig_sp_run24
        aei.BLOCK_ALERT_STATE_PATH = _orig_state_path24
        if _orig_env_tm is not None:
            os.environ["AUTO_EXIT_TEST_MODE"] = _orig_env_tm
        shutil.rmtree(_tmp_dir24, ignore_errors=True)

    # ---------------- Test 25 (arch-review vòng 4): `portfolio_status.book_lot_snapshot`'s
    # `_reason_for` — ranh giới TỪ (`\b`), KHÔNG phải substring thô: ticker "AAA" KHÔNG được khớp
    # nhầm cảnh báo của ticker KHÁC chứa "AAA" làm tiền tố ("AAAB") — Mregex_substring chết nếu
    # ai đổi `pat.search(w)` thành `tk in w` thô hoặc bỏ `\b`. Monkeypatch `park_holdings.
    # park_holdings` (tên mà `book_lot_snapshot` tự `from park_holdings import park_holdings` mỗi
    # lần gọi) để trả fixture tối giản, không cần dựng bootstrap+FIFO thật. -------------------
    print("\n[Test25] book_lot_snapshot._reason_for — ranh giới TỪ, không khớp nhầm AAA/AAAB")
    _ph_orig = ph.park_holdings

    def _fake_ph(account, asof=None, need_price=False, **kw):
        return {
            "lots": [{"ticker": "AAA", "book": "LAG", "qty": 100, "entry_date": "2026-01-01"},
                     {"ticker": "AAAB", "book": "LAG", "qty": 200, "entry_date": "2026-01-01"}],
            "reconcile": {"mismatches": []},
            "unverified_tickers": ["AAA", "AAAB"],
            "warnings": ["AAAB: reconcile lệch broker nghiêm trọng"],
        }
    ph.park_holdings = _fake_ph
    try:
        _, ok25, _, blocked25 = ps.book_lot_snapshot(ACCOUNT, "LAG", asof=signal_date_str)
        check("Test25: ok=True", ok25)
        check("Test25a: AAAB khớp ĐÚNG cảnh báo của chính nó (không fallback)",
              blocked25.get("AAAB") == "AAAB: reconcile lệch broker nghiêm trọng",
              f"blocked={blocked25}")
        check("Test25b: AAA KHÔNG bị gán nhầm cảnh báo của AAAB — rơi về fallback chung "
              "(Mregex_substring chết)",
              blocked25.get("AAA", "").startswith("unverified")
              and blocked25.get("AAA") != blocked25.get("AAAB"),
              f"blocked={blocked25}")
    finally:
        ph.park_holdings = _ph_orig

    # ---------------- Test 26 (vòng 4, item 3e): book_lot_snapshot BAL ok=False — ĐỐI XỨNG của
    # Test1d (vốn chỉ phủ nhánh LAG). `_add_blocked(None, "BAL", ...)` ở đường BAL (process_account
    # dòng ~398) dùng CODE PATH RIÊNG so với đường LAG (dòng ~374) — Test1d PASS không chứng minh
    # gì về nhánh này (Mblk_balstruct). ----------------
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_positions(exec_dir, signal_date_str,
                        {"AAA26": (1000, 20000.0), "CCC26": (2000, 30000.0)})
        write_plan(plan_dir, ACCOUNT, plan_date)
        orig = patch_all(exec_dir, plan_dir, ledger_path,
                         lag_lots={"AAA26": {"qty": 1000, "entry_date": lag_exit_entry}},
                         bal_lots={"CCC26": {"qty": 2000, "entry_date": bal_exit_entry}},
                         lag_ok=True, bal_ok=False)
        try:
            rc = aei.process_account(ACCOUNT, plan_date, signal_date_str, dry_run=False)
        finally:
            restore_all(orig)
        check("Test26: rc=0 (fail-safe, không crash)", rc == 0, f"rc={rc}")
        plan = load_plan_raw(plan_dir, ACCOUNT, plan_date)
        sells26 = {(o["ticker"], o["book"]) for o in plan["orders"] if o["side"] == "sell"}
        check("Test26: BAL ok=False ⇒ CCC26 KHÔNG chèn dù tới mốc", ("CCC26", "BAL") not in sells26,
              f"got={sells26}")
        check("Test26: LAG ok=True KHÔNG bị ảnh hưởng ⇒ AAA26 vẫn chèn", ("AAA26", "LAG") in sells26,
              f"got={sells26}")
        notes26 = plan.get("auto_exit_inject_notes") or []
        blocked26 = (notes26[-1].get("blocked") or []) if notes26 else []
        check("Test26: lỗi kết cấu BAL ghi vào blocked_notes với ticker=None, book=BAL "
              "(§29, Mblk_balstruct)",
              any(b["ticker"] is None and b["book"] == "BAL" for b in blocked26),
              f"blocked={blocked26}")
    finally:
        shutil.rmtree(td, ignore_errors=True)

    # ---------------- Test 27 (vòng 4, item 3d): `_add_blocked` dedup khi 2 NGUỒN ĐỘC LẬP
    # (book_lot_snapshot.blocked + qty-mismatch guard của `_lag_bal_candidates`) báo TRÙNG
    # (ticker,book,reason) Y HỆT cho CÙNG 1 mã — ca "book_lot_snapshot() trả về mã trùng" nêu
    # trong docstring của `_add_blocked` (Mbaldedup_off: mutant tắt check dedup sẽ in 2 bullet
    # trùng). Chạy 2 bước: bước 1 LẤY đúng chuỗi reason thật mà guard qty-mismatch tự sinh (tránh
    # hardcode lệch kiểu int/float), bước 2 ép `lag_blocked` trả CHÍNH chuỗi đó để tạo trùng lặp
    # thật, xác nhận dedup còn ĐÚNG 1. ----------------
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    probe27 = None
    try:
        write_positions(exec_dir, signal_date_str, {"DUPTK27": (50, 20000.0)})
        write_plan(plan_dir, ACCOUNT, plan_date)
        orig = patch_all(exec_dir, plan_dir, ledger_path,
                         lag_lots={"DUPTK27": {"qty": 100, "entry_date": lag_exit_entry}})
        try:
            aei.process_account(ACCOUNT, plan_date, signal_date_str, dry_run=False)
        finally:
            restore_all(orig)
        plan = load_plan_raw(plan_dir, ACCOUNT, plan_date)
        notes_probe = plan.get("auto_exit_inject_notes") or []
        blocked_probe = (notes_probe[-1].get("blocked") or []) if notes_probe else []
        probe27 = next((b for b in blocked_probe if b.get("ticker") == "DUPTK27"), None)
        check("Test27 (setup): qty-mismatch guard tự sinh reason cho DUPTK27",
              probe27 is not None, f"blocked={blocked_probe}")
    finally:
        shutil.rmtree(td, ignore_errors=True)

    if probe27:
        _dup_reason27 = probe27["reason"]
        td, exec_dir, plan_dir, ledger_path = setup_sandbox()
        try:
            write_positions(exec_dir, signal_date_str, {"DUPTK27": (50, 20000.0)})
            write_plan(plan_dir, ACCOUNT, plan_date)
            orig = patch_all(exec_dir, plan_dir, ledger_path,
                             lag_lots={"DUPTK27": {"qty": 100, "entry_date": lag_exit_entry}},
                             lag_blocked={"DUPTK27": _dup_reason27})
            try:
                rc = aei.process_account(ACCOUNT, plan_date, signal_date_str, dry_run=False)
            finally:
                restore_all(orig)
            check("Test27: rc=0", rc == 0, f"rc={rc}")
            plan = load_plan_raw(plan_dir, ACCOUNT, plan_date)
            notes27 = plan.get("auto_exit_inject_notes") or []
            blocked27 = (notes27[-1].get("blocked") or []) if notes27 else []
            dup27 = [b for b in blocked27
                    if b.get("ticker") == "DUPTK27" and b.get("reason") == _dup_reason27]
            check("Test27: 2 nguồn ĐỘC LẬP báo TRÙNG (ticker,book,reason) y hệt ⇒ dedup còn "
                  "ĐÚNG 1, không nhân đôi (Mbaldedup_off)", len(dup27) == 1, f"blocked={blocked27}")
        finally:
            shutil.rmtree(td, ignore_errors=True)

    # ---------------- Test 28: chạy lại sau lỗi kết cấu (DNSE 500 tối 26/10) — sổ lô LAG+BAL dựng
    # được ⇒ `blocked` của entry auto trước chuyển sang `blocked_superseded` (báo cáo chỉ đọc
    # `blocked`), entry THỦ CÔNG không bị đụng; sổ lô vẫn lỗi ⇒ KHÔNG gỡ. ----------------
    for _case28, _bal_ok28 in (("ok", True), ("vẫn lỗi", False)):
        td, exec_dir, plan_dir, ledger_path = setup_sandbox()
        try:
            write_positions(exec_dir, signal_date_str, {})
            write_plan(plan_dir, ACCOUNT, plan_date)
            _pp28 = os.path.join(plan_dir, f"plan_{ACCOUNT}_{plan_date}.json")
            _pl28 = json.load(open(_pp28, encoding="utf-8"))
            _pl28["auto_exit_inject_notes"] = [
                {"at": "t0", "source": "auto_exit_inject",
                 "blocked": [{"ticker": None, "book": "BAL", "reason": "park_holdings lỗi: HTTP 500"}]},
                {"at": "t1", "manual": True,
                 "blocked": [{"ticker": "MAN", "book": "BAL", "reason": "ghi tay"}]}]
            json.dump(_pl28, open(_pp28, "w", encoding="utf-8"), ensure_ascii=False)
            orig = patch_all(exec_dir, plan_dir, ledger_path, lag_lots={}, bal_lots={},
                             lag_ok=True, bal_ok=_bal_ok28)
            try:
                rc = aei.process_account(ACCOUNT, plan_date, signal_date_str, dry_run=False)
            finally:
                restore_all(orig)
            plan = load_plan_raw(plan_dir, ACCOUNT, plan_date)
            n28 = plan.get("auto_exit_inject_notes") or []
            auto28 = [n for n in n28 if n.get("source") == "auto_exit_inject"]
            live_blocked28 = [b for n in auto28 for b in (n.get("blocked") or [])]
            if _bal_ok28:
                check("Test28: sổ lô dựng lại được ⇒ blocked cũ → blocked_superseded, không còn blocked sống",
                      rc == 0 and not live_blocked28 and bool(auto28[0].get("blocked_superseded")),
                      f"rc={rc} notes={n28}")
            else:
                check("Test28: sổ BAL vẫn lỗi ⇒ KHÔNG gỡ blocked (vẫn báo ⛔)",
                      any(b["book"] == "BAL" and b["ticker"] is None for b in live_blocked28),
                      f"notes={n28}")
            check(f"Test28 ({_case28}): entry thủ công giữ nguyên blocked",
                  any(n.get("manual") and n.get("blocked") for n in n28), f"notes={n28}")
        finally:
            shutil.rmtree(td, ignore_errors=True)

    # ---------------- Test 29: positions KHÔNG đọc được (dnse_raw chưa có bản ghi) dù sổ lô OK ⇒
    # KHÔNG gỡ blocked cũ (lượt này chưa đánh giá lại gì). ----------------
    td, exec_dir, plan_dir, ledger_path = setup_sandbox()
    try:
        write_plan(plan_dir, ACCOUNT, plan_date)   # cố ý KHÔNG write_positions
        _pp29 = os.path.join(plan_dir, f"plan_{ACCOUNT}_{plan_date}.json")
        _pl29 = json.load(open(_pp29, encoding="utf-8"))
        _pl29["auto_exit_inject_notes"] = [
            {"at": "t0", "source": "auto_exit_inject",
             "blocked": [{"ticker": None, "book": "BAL", "reason": "park_holdings lỗi: HTTP 500"}]}]
        json.dump(_pl29, open(_pp29, "w", encoding="utf-8"), ensure_ascii=False)
        orig = patch_all(exec_dir, plan_dir, ledger_path, lag_lots={}, bal_lots={},
                         lag_ok=True, bal_ok=True)
        try:
            aei.process_account(ACCOUNT, plan_date, signal_date_str, dry_run=False)
        finally:
            restore_all(orig)
        n29 = load_plan_raw(plan_dir, ACCOUNT, plan_date).get("auto_exit_inject_notes") or []
        check("Test29: positions=None ⇒ blocked cũ KHÔNG bị gỡ",
              bool(n29) and bool(n29[0].get("blocked")) and not n29[0].get("blocked_superseded"),
              f"notes={n29}")
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

    lot_tests(signal_date, plan_date, entry_n_sessions_before)
    run_lot_mutants()

    print(f"\n{len(PASS)} PASS, {len(FAIL)} FAIL")
    if FAIL:
        print("FAILED:", FAIL)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
