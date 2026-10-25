#!/usr/bin/env python3
"""Selfcheck N1 + N4 — sổ khai báo quyền mua (`rights_subscription.py`) và các consumer.

Chạy:  $DNA_PYEXE bin/rights_subscription_selfcheck.py            (exit 0 ⇔ mọi ca PASS)
       bin/rights_subscription_selfcheck.py --mutants               (đột biến code, mỗi mutant PHẢI bị giết)
Sandbox mkdtemp + chặn ghi ngoài sandbox//tmp; MIKE_BOT_TEST_MODE=1, AUTO_EXIT_TEST_MODE=1; không BQ,
không DNSE, không bus/Discord (subprocess bị thay bằng recorder). Kịch bản số = audit
agents/Taylor/research/lag_rights_audit_20261022 (SCL 14.000 @30.000, quyền 14:5 @12.500 ⇒ 5.000cp).
"""
import os
os.environ["MIKE_BOT_TEST_MODE"] = "1"      # §5b — TRƯỚC mọi import trading_bot
os.environ["AUTO_EXIT_TEST_MODE"] = "1"
import builtins
import contextlib
import csv
import datetime as dt
import io
import json
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT_TMP = tempfile.mkdtemp(prefix="rights_sub_sc_")
os.environ["MIKE_LAG_RIGHTS_DIR"] = os.path.join(ROOT_TMP, "lag_rights_default")
os.environ["VERIFY_ACCOUNT_EXEC_DIR"] = ROOT_TMP
os.environ["VERIFY_ACCOUNT_KNOWN_DISCREPANCIES"] = os.path.join(ROOT_TMP, "kd_none.json")

if "--mutants" in sys.argv[1:]:
    # ---- đột biến: chép bin/ vào thư mục tạm TRONG cây WorkingClaude (wc_paths cần marker), sửa
    # ĐÚNG một chỗ, chạy lại selfcheck — mỗi mutant phải làm ít nhất một ca FAIL.
    MUTANTS = [
        ("M1 net_fills_between bỏ cộng khai báo", "daily_nav_snapshot.py",
         "                out[tk] = out.get(tk, 0.0) + qty\n", "                pass\n"),
        ("M2 rights_credit bỏ kế thừa entry_date", "park_holdings.py",
         '"entry_date": l["entry_date"], "qty": a,', '"entry_date": sub["credit_date"], "qty": a,'),
        ("M3 bỏ chụp lô hưởng quyền tại GDKHQ (chụp lúc credit)", "park_holdings.py",
         "            timeline.append((r[\"exright_date\"], 2, r, \"rights_subscriptions.json\"))\n",
         "            timeline.append((r[\"credit_date\"] + \"T23:59:58\", 2, r, \"rights_subscriptions.json\"))\n"),
        ("M4 bỏ chặn khai vượt quyền", "park_holdings.py",
         "        if not entitled or qty > cap:", "        if not entitled:"),
        # >>> N4 (PHẦN 2 — legal-vn 22/10)
        ("M5 N4 park: nhân cả lô quyền đang chờ", "park_holdings.py",
         "                             and rights_sub.pending_at(l[\"rights_subscription\"], ex_date))]",
         "                             and False)]"),
        # <<< N4
        ("M6 auto_exit bỏ tách lô khoá", "auto_exit_inject.py",
         "    return qty - locked, locked", "    return qty, 0"),
        # >>> B1 vòng 2 (arch-review): khoá chỉ phần CHƯA niêm yết, có hạn, không nuốt thiếu hụt khác
        ("M17 khoá không giới hạn bởi phần broker không cho bán (nuốt SELL book khác)", "auto_exit_inject.py",
         "max(int(held) - int(sellable), 0))", "int(qty))"),
        ("M18 khoá cả lô đã tới listing_date", "auto_exit_inject.py",
         "            if ld >= plan_date:", "            if True:"),
        ("M25 NB1 biên listing_date == plan_date không khoá (về '>')", "auto_exit_inject.py",
         "            if ld >= plan_date:", "            if ld > plan_date:"),
        ("M19 khoá không hết hạn credit_date+10 phiên", "auto_exit_inject.py",
         "        elif n <= RIGHTS_LOCK_MAX_SESSIONS:", "        elif True:"),
        ("M20 cảnh báo cắt bỏ chẩn đoán lô quyền hết khoá", "auto_exit_inject.py",
         "        if lock_diag:", "        if False:"),
        ("M21 alert bỏ dòng khoá chờ niêm yết", "auto_exit_inject.py",
         "    for lk in locked_notes or []:", "    for lk in []:"),
        # <<< B1 vòng 2
        ("M24 NB2 cash_identity đặt chân tiền ở credit_date", "cash_identity.py",
         "                else [(s[\"payment_date\"], 0.0, qty * px), (s[\"credit_date\"], qty, 0.0)])",
         "                else [(s[\"credit_date\"], qty, qty * px)])"),
        ("M23 NB1 reconcile tính phí cả lô quyền", "reconcile_equity.py",
         "        fees = (true_cost_basis - rights_held_value) * fee_buy_pct / 100.0", "        pass"),
        ("M26 NB2-reconcile bỏ phải thu CP quyền đã nộp tiền", "reconcile_equity.py",
         "args.offbook_assets + rights_receivable_value\n", "args.offbook_assets\n"),
        ("M27 NB2-reconcile phải thu tính cả lô đã về broker", "reconcile_equity.py",
         "and s_[\"credit_date\"] > asof]", "]"),
        ("M28 NB4 credit_frame bỏ pending_rights", "dividend_adjusted_return.py",
         "                                                         pending_rights=pend)",
         "                                                         pending_rights=0.0)"),
        ("M29 NB4 KL hưởng quyền gồm cả lô chờ", "dividend_adjusted_return.py",
         "float(detail[\"residual\"]) - pend\n", "float(detail[\"residual\"])\n"),
        ("M22 B2 net_fills_journal_and_broker (đường sizing broker_statement=True) bỏ cộng lô quyền", "exdate_frame.py",
         "    for d, evs in rights_sub.fill_events(account_label, account_no=account_no).items():",
         "    for d, evs in {}.items():"),
        ("M7 verify bỏ khai báo", "verify_account_snapshot.py",
         "    for date, evs in sorted(rights_sub.fill_events(", "    for date, evs in sorted([] if True else rights_sub.fill_events("),
        ("M8 verify bỏ đối chiếu KL broker", "verify_account_snapshot.py",
         "        if abs(raw_agg[tk][0] - bq_) > 1e-6:", "        if False:"),
        ("M9 cash_identity tính phí lô quyền", "cash_identity.py",
         'if fx["side"] == "buy" and not fx.get("fee_free"))', 'if fx["side"] == "buy")'),
        # >>> N4 (PHẦN 2 — legal-vn 22/10)
        ("M10 N4 NAV: bỏ trừ lô chờ ở KL kỳ vọng", "daily_nav_snapshot.py",
         "        expected = (qty_prev - pending_rights) * ratio if pending_rights else qty_prev * ratio",
         "        expected = qty_prev * ratio"),
        ("M11 N4 verify: bỏ miễn nhân hệ số cho lô chờ", "verify_account_snapshot.py",
         "                and not (key and rights_sub.exempt_from(key, a[\"ex_date\"])):", ":"),
        # <<< N4
        ("M12 sổ chấp nhận decided_by≠user", "rights_subscription.py",
         '    if rec["decided_by"] != "user":', '    if False:'),
        ("M13 sổ không lọc account (§12)", "rights_subscription.py",
         '        if r["account"] != account:\n            continue\n', ''),
        ("M14 reconcile bỏ khai báo", "reconcile_equity.py",
         "        events_by_date.setdefault(d, []).extend(evs)", "        pass"),
        # >>> N4 (PHẦN 2 — legal-vn 22/10)
        ("M16 exdate_frame (active_nav) bỏ trừ lô chờ", "exdate_frame.py",
         "                if prev_d and ev and ev.get(\"date\") else 0.0)", "                if False else 0.0)"),
        ("M15 pending_at: chờ kết thúc ngay khi credit", "rights_subscription.py",
         "    return sub[\"credit_date\"] <= d and (end is None or d < end)", "    return False"),
        # <<< N4
    ]
    import wc_paths
    wc = wc_paths.find_wc_root(__file__)
    base = tempfile.mkdtemp(prefix=".mut_rights_sub_", dir=os.path.dirname(HERE))
    py = sys.executable
    alive = []
    try:
        ctl = subprocess.run([py, os.path.join(HERE, os.path.basename(__file__))],
                             capture_output=True, text=True, timeout=900)
        print(f"CONTROL (không đột biến): rc={ctl.returncode} — {ctl.stdout.strip().splitlines()[-1]}")
        if ctl.returncode != 0:
            print(ctl.stdout[-3000:], ctl.stderr[-2000:])
            sys.exit(2)
        for i, (name, fn, old, new) in enumerate(MUTANTS):
            mb = os.path.join(base, f"m{i}", "bin")
            shutil.copytree(HERE, mb, ignore=shutil.ignore_patterns("__pycache__", ".mut_*"))
            p = os.path.join(mb, fn)
            s = open(p, encoding="utf-8").read()
            if s.count(old) != 1:
                print(f"  ⚠️ {name}: mẫu đột biến xuất hiện {s.count(old)} lần — mutant KHÔNG HỢP LỆ")
                alive.append(name)
                continue
            open(p, "w", encoding="utf-8").write(s.replace(old, new))
            r = subprocess.run([py, os.path.join(mb, os.path.basename(__file__))],
                               capture_output=True, text=True, timeout=900)
            fails = [ln.strip() for ln in r.stdout.splitlines() if ln.startswith("  FAIL")]
            killed = r.returncode != 0
            print(f"  {'KILLED' if killed else 'ALIVE '} {name}: rc={r.returncode} "
                  f"{(fails[0][:150] if fails else (r.stderr.strip().splitlines() or [''])[-1][:150])}")
            if not killed:
                alive.append(name)
    finally:
        shutil.rmtree(base, ignore_errors=True)
        shutil.rmtree(ROOT_TMP, ignore_errors=True)
    print(f"\nmutants: {len(MUTANTS) - len(alive)}/{len(MUTANTS)} killed" + (f" — SỐNG: {alive}" if alive else ""))
    sys.exit(1 if alive else 0)

# ---------------- chặn ghi ngoài sandbox ----------------
_real_open, _real_replace, _real_rename = builtins.open, os.replace, os.rename


def _chk(path):
    p = os.path.realpath(str(path))
    if not (p.startswith(os.path.realpath(ROOT_TMP)) or p.startswith("/tmp/")):
        raise PermissionError(f"SELFCHECK GUARD: chặn ghi ngoài sandbox: {p}")


def _open(file, mode="r", *a, **k):
    if isinstance(file, (str, bytes, os.PathLike)) and any(c in mode for c in "wax+"):
        _chk(file)
    return _real_open(file, mode, *a, **k)


builtins.open = _open
os.replace = lambda s, d, *a, **k: (_chk(d), _real_replace(s, d, *a, **k))[1]
os.rename = lambda s, d, *a, **k: (_chk(d), _real_rename(s, d, *a, **k))[1]

import wc_paths  # noqa: E402
sys.path.insert(0, wc_paths.find_wc_root(__file__))
import rights_subscription as RS  # noqa: E402
import park_holdings as ph  # noqa: E402
import portfolio_status as ps  # noqa: E402
import auto_exit_inject as aei  # noqa: E402
import capit_episode  # noqa: E402
import daily_nav_snapshot as D  # noqa: E402
import verify_account_snapshot as V  # noqa: E402
import reconcile_equity as RE  # noqa: E402
import dividend_adjusted_return as DAR  # noqa: E402
import cash_identity as CI  # noqa: E402
import broker_fill_confirm as BFC  # noqa: E402 — B2: thay statement DNSE bằng bản giả (hermetic)
import exdate_frame as EF  # noqa: E402
import corp_action_daily as CAD  # noqa: E402 — chèn mike/bin (master) lên đầu sys.path ⇒ import SAU CÙNG
sys.path.insert(0, HERE)                    # …và đặt lại bin/ của cây đang kiểm lên đầu
for _m in ("verify_account_snapshot", "daily_nav_snapshot", "park_holdings", "rights_subscription",
           "reconcile_equity", "cash_identity", "auto_exit_inject", "portfolio_status", "exdate_frame"):
    assert os.path.dirname(os.path.abspath(sys.modules[_m].__file__)) == HERE, (_m, sys.modules[_m].__file__)
from trading_bot.vn_market import next_trading_day  # noqa: E402

CALLS = []
aei.subprocess.run = lambda cmd, *a, **k: (CALLS.append(cmd), subprocess.CompletedProcess(cmd, 0))[1]
RESULTS = []


def check(name, cond, info=""):
    RESULTS.append((name, bool(cond)))
    print(f"  {'PASS' if cond else 'FAIL'} {name}" + (f" — {info}" if info and not cond else ""))


def raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except RS.RightsSubscriptionError as e:
        return str(e)
    return None


def nth(start, n):
    d = start
    for _ in range(n):
        d = next_trading_day(d)
    return d


# ================================ L. sổ khai báo ================================
print("L. rights_subscription — khai báo, provenance, lọc account")
EVID, TK = "999001", "SCL"
BQ_ROW = {"id": EVID, "ticker": TK, "issue_method_code": "Rights", "issue_status_code": "D",
          "event_status": "executed", "exright_date": "2026-11-09", "record_date": "2026-11-10",
          "public_date": "2026-10-20", "exercise_ratio": 0.35714286, "value_per_share": None,
          "total_value": 1e11, "issue_volumn": 8e6}
import lag_rights_exit_hold as RH  # noqa: E402
H = RH.event_hash(BQ_ROW)
LP = os.path.join(ROOT_TMP, "L", "subscriptions.json")
fetch = lambda tks: [dict(BQ_ROW)]  # noqa: E731
base_kw = dict(account="RightsAcct", ticker=TK, event_id=EVID, event_hash_seen=H, subscribed_qty=5000,
               issue_price=12500, payment_date="2026-11-16", decided_by="user",
               at="2026-11-16T10:00:00+07:00", source="discord fixture", fetch=fetch, path=LP,
               account_no="8888888888")
rec = RS.record(**base_kw)
check("L1 ghi hợp lệ: credit_date mặc định = payment_date, GDKHQ lấy từ BQ",
      rec["credit_date"] == "2026-11-16" and rec["exright_date"] == "2026-11-09"
      and rec["issue_price_source"] == "bq+user", rec)
check("L2 decided_by≠user bị từ chối", raises(RS.record, **dict(base_kw, decided_by="agent")))
check("L3 `at` không múi giờ bị từ chối", raises(RS.record, **dict(base_kw, at="2026-11-16T10:00:00")))
check("L4 event_hash lệch bị từ chối", raises(RS.record, **dict(base_kw, event_hash_seen="deadbeef0000")))
check("L5 giá phát hành ≠ BQ bị từ chối", raises(RS.record, **dict(base_kw, issue_price=13000)))
check("L6 BQ chưa có GDKHQ bị từ chối",
      raises(RS.record, **dict(base_kw, fetch=lambda t: [dict(BQ_ROW, exright_date=None)],
                               event_hash_seen=RH.event_hash(dict(BQ_ROW, exright_date=None)))))
check("L7 source rỗng bị từ chối", raises(RS.record, **dict(base_kw, source=" ")))
check("L8 payment_date < GDKHQ bị từ chối", raises(RS.record, **dict(base_kw, payment_date="2026-11-06")))
RS.record(**dict(base_kw, subscribed_qty=4000))
subs = RS.load_subscriptions("RightsAcct", LP)
check("L9 bản mới nhất (account, event) có hiệu lực", len(subs) == 1 and subs[0]["subscribed_qty"] == 4000, subs)
RS.record(**dict(base_kw, account="OtherAcct", account_no="7777777777", subscribed_qty=100))
check("L10 §12 lọc theo account", [s["subscribed_qty"] for s in RS.load_subscriptions("RightsAcct", LP)] == [4000]
      and [s["subscribed_qty"] for s in RS.load_subscriptions("OtherAcct", LP)] == [100])
check("L11 account_no lệch ⇒ raise", raises(RS.load_subscriptions, "RightsAcct", LP, "0000000000"))
RS.record(**dict(base_kw, subscribed_qty=0))
check("L12 subscribed_qty=0 huỷ khai báo", RS.load_subscriptions("RightsAcct", LP) == [])
check("L13 không còn file tạm sau ghi atomic",
      not [f for f in os.listdir(os.path.dirname(LP)) if f.endswith(".tmp")])
with _real_open(LP, "w") as f:
    f.write("{hỏng")
check("L14 file hỏng ⇒ RightsSubscriptionError (consumer fail-closed)", raises(RS.load_subscriptions, "RightsAcct", LP))
s0 = {"credit_date": "2026-11-16", "registered_date": "2026-11-25", "listing_date": None}
check("L15 pending_at: trước credit=False · trong chờ=True · từ ngày ghi nhận=False · chưa có ngày ghi nhận=True",
      (not RS.pending_at(s0, "2026-11-10")) and RS.pending_at(s0, "2026-11-20")
      and not RS.pending_at(s0, "2026-11-25") and RS.pending_at(dict(s0, registered_date=None), "2027-05-01"))
k = RS.event_key(dict(s0, event_id="X"))
check("L16 exempt_from đọc đúng cửa sổ chờ từ khoá; khoá thường không miễn",
      RS.exempt_from(k, "2026-11-20") and not RS.exempt_from(k, "2026-11-26")
      and not RS.exempt_from("12345", "2026-11-20"))

# ================================ P. sổ lô + auto-exit ================================
print("\nP. park_holdings (sổ lô) + auto_exit_inject (khoá chờ niêm yết)")
ACC, ACC_NO, OTHER_NO = "RightsAcct", "8888888888", "7777777777"
DAY0 = "2026-10-01"
PARK = {"FPT": (6_000, 100_000), "MBB": (30_000, 25_000)}
E = dt.date(2026, 10, 26)
T0 = nth(E, 10)                    # GDKHQ quyền mua
PAY = nth(T0, 5)                   # nộp tiền = ngày CP về openQuantity (dạng A, tiền lệ MBB 08-28)
T25 = nth(E, 25)
LIST = nth(T25, 40)
JCOLS = ["ts", "event", "parent_id", "child_oid", "ticker", "side", "qty", "price", "book", "play_type"]


def sandbox(tag):
    td = os.path.join(ROOT_TMP, "P_" + tag)
    ex, pl = os.path.join(td, "execution_logs"), os.path.join(td, "trade_plans")
    os.makedirs(ex)
    os.makedirs(pl)
    snap = {"_status": "APPROVED selfcheck fixture", "account_label": ACC, "account_no": ACC_NO,
            "day0_date": DAY0, "broker_source": {"file": "fx", "ts": f"{DAY0}T00:00:00"}, "reconcile_ok": True,
            "positions": [{"ticker": t, "qty": q, "book": "custom30V_parking", "entry_date": DAY0,
                           "cost_price_vnd": px} for t, (q, px) in PARK.items()]}
    with open(os.path.join(pl, f"bootstrap_book_snapshot_{ACC}_{DAY0.replace('-', '')}.json"), "w") as f:
        json.dump(snap, f)
    return td, ex, pl


def journal(ex, date, fills):
    p = os.path.join(ex, f"exec_{ACC}_{date}_journal.csv")
    new = not os.path.exists(p)
    with open(p, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=JCOLS)
        if new:
            w.writeheader()
        for i, (tk, side, q, px, book) in enumerate(fills):
            w.writerow({"ts": f"{date}T09:30:0{i}", "event": "FILL", "parent_id": f"P-{tk}-{date}-{i}",
                        "child_oid": f"C-{tk}-{date}-{i}", "ticker": tk, "side": side, "qty": q, "price": px,
                        "book": book, "play_type": "LAG_LO" if book == "LAG" else ""})


def raw(ex, date, lag_open, lag_trade, lag_mp=25_400):
    rows = [{"accountNo": ACC_NO, "symbol": t, "openQuantity": q, "tradeQuantity": q, "marketPrice": px,
             "costPrice": px, "status": "OPEN"} for t, (q, px) in PARK.items()]
    if lag_open:
        rows.append({"accountNo": ACC_NO, "symbol": TK, "openQuantity": lag_open, "tradeQuantity": lag_trade,
                     "marketPrice": lag_mp, "costPrice": lag_mp, "status": "OPEN"})
    recs = [{"ts": f"{date}T20:30:00", "kind": "positions", "account_no": OTHER_NO,
             "payload": {"positions": [{"accountNo": OTHER_NO, "symbol": TK, "openQuantity": 999,
                                        "tradeQuantity": 999, "marketPrice": 1, "costPrice": 1}]}},
            {"ts": f"{date}T20:30:01", "kind": "positions", "account_no": ACC_NO, "payload": {"positions": rows}},
            {"ts": f"{date}T20:30:02", "kind": "balances", "account_no": ACC_NO,
             "payload": {"stock": {"availableCash": 100e6, "totalCash": 100e6, "totalDebt": 0.0,
                                   "cashDividendReceiving": 0.0, "depositInterest": 1.0},
                         "egg": {"totalValue": 300e6}}}]
    with open(os.path.join(ex, f"dnse_raw_{date}.jsonl"), "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")


def sub(qty=5000, credit=PAY, account=ACC, account_no=ACC_NO, registered=None, ex=T0, listing=None):
    return {"account": account, "account_no": account_no, "ticker": TK, "event_id": EVID, "event_hash": H,
            "exright_date": ex.isoformat(), "exercise_ratio": 0.35714286, "issue_price_vnd": 12500.0,
            "subscribed_qty": qty, "payment_date": credit.isoformat(), "credit_date": credit.isoformat(),
            "registered_date": registered, "listing_date": listing.isoformat() if listing else None,
            "decided_by": "user",
            "at": "2026-11-16T10:00:00+07:00", "source": "fixture"}


def wire(ex, pl, td, acts=(), subs=()):
    """Trỏ mọi đường đọc/ghi của ph/ps/aei/capit vào sandbox; khai báo qua file sandbox (đường production)."""
    rd = os.path.join(td, "lag_rights")
    os.makedirs(rd, exist_ok=True)
    with open(os.path.join(rd, "subscriptions.json"), "w") as f:
        json.dump({"subscriptions": list(subs)}, f)
    os.environ["MIKE_LAG_RIGHTS_DIR"] = rd
    ledger = os.path.join(td, "capit.json")
    with open(ledger, "w") as f:
        json.dump({"episodes": []}, f)
    ps.EXEC_DIR, aei.PLAN_DIR, capit_episode.LEDGER_PATH = ex, pl, ledger
    aei.BLOCK_ALERT_STATE_PATH = os.path.join(td, "alert_state.json")
    aei.account_no_for = lambda a: ACC_NO if a == ACC else None
    d0 = list(_PH_DEFAULTS)
    d0[1], d0[2] = pl, ex
    ph.park_holdings.__defaults__ = tuple(d0)
    ph.account_profile = lambda label: {"account_id": ACC_NO, "excluded_tickers": []}
    ph.load_corp_actions = lambda *a, **k: list(acts)
    aei.rights_hold.holds_for = lambda *a, **k: {}      # X1 có selfcheck riêng; ở đây GDKHQ đã qua


_PH_DEFAULTS = ph.park_holdings.__defaults__


def run_exit(tag, signal, broker, fills=(), acts=(), subs=(), lag_buys=((E, 14_000),), pre_orders=()):
    td, ex, pl = sandbox(tag)
    for d, q in lag_buys:
        journal(ex, d.isoformat(), [(TK, "buy", q, 30_000, "LAG")])
    for d, f in fills:
        journal(ex, d.isoformat(), [f])
    raw(ex, signal.isoformat(), *broker)
    wire(ex, pl, td, acts, subs)
    plan_date = next_trading_day(signal).isoformat()
    pp = os.path.join(pl, f"plan_{ACC}_{plan_date}.json")
    with open(pp, "w") as f:
        json.dump({"plan_date": plan_date, "orders": list(pre_orders), "account": ACC}, f)
    m0 = _real_open(pp).read()   # so NỘI DUNG, không so mtime (độ phân giải mtime làm ca chập chờn)
    with contextlib.redirect_stdout(io.StringIO()) as out:
        aei.process_account(ACC, plan_date, signal.isoformat(), dry_run=False)
    plan = json.load(_real_open(pp))
    h = ph.park_holdings(ACC, asof=signal.isoformat(), need_price=False)
    lots, ok, _r, blk = ps.book_lot_snapshot(ACC, "LAG", asof=signal.isoformat())
    notes = plan.get("auto_exit_inject_notes") or []
    return {"sells": [(o["ticker"], o["qty"]) for o in plan["orders"]], "notes": notes,
            "written": _real_open(pp).read() != m0, "h": h, "lots": lots, "blk": blk, "out": out.getvalue()}


def _k(r, key):
    return [x for n in r["notes"] for x in n.get(key, [])]


r = run_exit("p0_control_no_decl", T25, (19_000, 14_000))
check("P0 ĐỐI CHỨNG (không khai báo): sổ lệch broker ⇒ SCL chặn (hành vi cũ)",
      not r["h"]["reconcile"]["ok"] and TK in r["blk"] and r["sells"] == [], r["h"]["reconcile"])
r = run_exit("p1_credit_before_t25", T25, (19_000, 14_000), subs=[sub(listing=LIST)])
lag = [l for l in r["h"]["lots"] if l["ticker"] == TK]
check("P1a sổ khớp broker 19.000 khi có khai báo; L1/L2 hết BLOCKED_RECONCILE",
      r["h"]["reconcile"]["ok"], r["h"]["reconcile"]["mismatches"])
check("P1b lô quyền 5.000 @12.500, book LAG, entry_date KẾ THỪA lô gốc",
      any(l["qty"] == 5000 and l["price"] == 12500 and l["book"] == "LAG" and l["entry_date"] == E.isoformat()
          and l.get("rights_subscription") for l in lag), lag)
check("P1c T+25: bán 14.000 (phần sellable), 5.000 ghi 'khoá chờ niêm yết', KHÔNG cờ cắt/chặn",
      r["sells"] == [(TK, 14_000)] and [x["locked_qty"] for x in _k(r, "rights_locked")] == [5000]
      and not _k(r, "capped") and not _k(r, "blocked"), (r["sells"], r["notes"]))
S26 = nth(T25, 1)
r = run_exit("p2_locked_after_sale", nth(T25, 20), (5_000, 0),
             fills=[(S26, (TK, "sell", 14_000, 25_400, "LAG"))], subs=[sub(listing=LIST)])
check("P2 đã bán 14.000, 5.000 chưa niêm yết (listing_date tương lai): không mồ côi, không lệnh, không cờ "
      "cắt/chặn; plan GHI note rights_locked để báo cáo hiện ra (B1 vòng 2)",
      r["h"]["reconcile"]["ok"] and r["sells"] == [] and not _k(r, "capped") and not _k(r, "blocked")
      and [x["locked_qty"] for x in _k(r, "rights_locked")] == [5000] and r["written"]
      and "[RIGHTS-LOCKED]" in r["out"], (r["h"]["reconcile"], r["notes"], r["blk"]))
r = run_exit("p3_listing", LIST, (5_000, 5_000), fills=[(S26, (TK, "sell", 14_000, 25_400, "LAG"))],
             subs=[sub(listing=LIST)])
check("P3 phiên đầu tiên sellable: auto-exit bán ngay 5.000 (quá hạn vì entry kế thừa)",
      r["sells"] == [(TK, 5_000)] and not _k(r, "capped"), (r["sells"], r["notes"]))
r = run_exit("p4_sold_after_ex_before_credit", T25, (5_000, 0),
             fills=[(nth(T0, 1), (TK, "sell", 14_000, 25_400, "LAG"))], subs=[sub()])
check("P4 lô gốc bán SAU GDKHQ trước khi CP về: cơ sở chụp tại GDKHQ ⇒ vẫn thêm 5.000",
      r["h"]["reconcile"]["ok"] and sum(l["qty"] for l in r["h"]["lots"] if l["ticker"] == TK) == 5000,
      r["h"]["warnings"][-3:])
r = run_exit("p5_sold_before_ex", T25, (5_000, 0),
             fills=[(nth(E, 3), (TK, "sell", 14_000, 30_000, "LAG"))], subs=[sub()])
check("P5 bán hết TRƯỚC GDKHQ ⇒ không lô hưởng quyền ⇒ KHÔNG thêm, SCL UNVERIFIED (fail-closed)",
      TK in r["h"]["unverified_tickers"] and TK in r["blk"], r["h"]["warnings"][-2:])
r = run_exit("p6_over_cap", T25, (19_001, 14_000), subs=[sub(qty=5001)])
check("P6 khai vượt quyền tối đa (5.001 > 5.000) ⇒ không thêm, UNVERIFIED",
      TK in r["h"]["unverified_tickers"] and r["sells"] == [], r["h"]["warnings"][-1:])
E2 = nth(E, 2)
r = run_exit("p7_two_lots", T25, (19_000, 14_000), subs=[sub()], lag_buys=((E, 10_000), (E2, 4_000)))
rl = sorted((l["entry_date"], l["qty"]) for l in r["h"]["lots"] if l.get("rights_subscription"))
check("P7 chia Hamilton theo lô hưởng quyền: 10.000→3.571 (entry E), 4.000→1.429 (entry E+2)",
      rl == sorted([(E.isoformat(), 3571), (E2.isoformat(), 1429)]), rl)
r = run_exit("p8_other_account", T25, (19_000, 14_000),
             subs=[sub(account="OtherAcct", account_no=OTHER_NO)])
check("P8 §12: khai báo của account khác không vào sổ account này", not r["h"]["reconcile"]["ok"])
# >>> N4 (PHẦN 2 — legal-vn 22/10)
SDX = nth(PAY, 3)                  # cổ tức CP 9% GDKHQ nằm trong khoảng chờ VSDC
sdiv = {"id": "SCL-SDIV", "ticker": TK, "event_type": "STOCK_DIVIDEND", "qty_multiplier": 1.09,
        "ex_date": SDX.isoformat(), "record_date": SDX.isoformat(),
        "broker_effective_ts": f"{(SDX - dt.timedelta(days=1)).isoformat()}T19:30:00",
        "_status": "CONFIRMED fixture", "evidence": []}
before_t25 = nth(SDX, 1)
r = run_exit("p9_n4_pending", before_t25, (20_260, 15_260), subs=[sub()], acts=[sdiv])
check("P9 N4: cổ tức CP 9% trong khoảng chờ ⇒ chỉ lô gốc nhân (14.000→15.260), lô quyền giữ 5.000",
      r["h"]["reconcile"]["ok"] and sorted(l["qty"] for l in r["h"]["lots"] if l["ticker"] == TK) == [5000, 15260],
      (r["h"]["reconcile"]["mismatches"], [(l["qty"], l.get("rights_subscription") is not None)
                                          for l in r["h"]["lots"] if l["ticker"] == TK]))
r = run_exit("p10_n4_registered", before_t25, (20_710, 15_260),
             subs=[sub(registered=nth(PAY, 1).isoformat())], acts=[sdiv])
check("P10 N4 đối chứng: đã ghi nhận trước GDKHQ cổ tức ⇒ lô quyền cũng hưởng (5.000→5.450)",
      r["h"]["reconcile"]["ok"], r["h"]["reconcile"]["mismatches"])
# <<< N4
# >>> B1 vòng 2 (arch-review): khoá chỉ phần CHƯA niêm yết, có hạn, thiếu hụt khác vẫn cảnh báo cắt
r = run_exit("p12_listed_still_short", LIST, (5_000, 0), fills=[(S26, (TK, "sell", 14_000, 25_400, "LAG"))],
             subs=[sub(listing=LIST)])
cp = _k(r, "capped")
check("P12 (a) đã tới listing_date nhưng broker tradeQuantity vẫn 0 ⇒ KHÔNG khoá, cảnh báo cắt 5.000→0 "
      "kèm chẩn đoán nêu listing_date",
      r["sells"] == [] and not _k(r, "rights_locked") and [(c["desired_qty"], c["capped_qty"]) for c in cp] == [(5000, 0)]
      and LIST.isoformat() in cp[0].get("rights_diag", "") and "niêm yết" in cp[0]["reason"], r["notes"])
OTHER_SELL = {"id": "SELL-SCL-PARKMERGE-X", "ticker": TK, "side": "sell", "qty": 2000, "book": "custom30V_parking"}
r = run_exit("p13_other_book_sell", T25, (19_000, 16_000), subs=[sub(listing=LIST)], pre_orders=[OTHER_SELL])
cp = _k(r, "capped")
check("P13 (b) SELL book khác chiếm 2.000 sellable: khoá chỉ 3.000 (= open−trade), 16.000 cắt còn 14.000 "
      "⇒ CÓ cảnh báo cắt (bản vòng 1 nuốt im lặng: khoá 5.000, không cắt)",
      [x["locked_qty"] for x in _k(r, "rights_locked")] == [3000]
      and [(c["desired_qty"], c["capped_qty"]) for c in cp] == [(16000, 14000)]
      and (TK, 14_000) in r["sells"], (r["sells"], r["notes"]))
r = run_exit("p14_expired_no_listing", T25, (19_000, 14_000), subs=[sub()])
cp = _k(r, "capped")
n_exp = ps.count_trading_days(PAY, next_trading_day(T25))
check(f"P14 (c) chưa khai listing_date, plan_date = credit_date + {n_exp} phiên > 10 ⇒ HẾT khoá, cảnh báo "
      "cắt 19.000→14.000 kèm chẩn đoán số phiên + credit_date",
      n_exp > 10 and not _k(r, "rights_locked") and [(c["desired_qty"], c["capped_qty"]) for c in cp] == [(19000, 14000)]
      and f"đã {n_exp} phiên" in cp[0].get("rights_diag", "") and PAY.isoformat() in cp[0]["rights_diag"]
      and r["sells"] == [(TK, 14_000)], (n_exp, r["notes"]))
CR_LATE = nth(T0, 9)      # credit trễ: plan_date T25+1 chỉ cách credit vài phiên
r = run_exit("p15_within_window_no_listing", T25, (19_000, 14_000), subs=[sub(credit=CR_LATE)])
check("P15 ĐỐI CHỨNG cho P14: chưa khai listing_date nhưng còn trong 10 phiên ⇒ vẫn khoá 5.000, không cắt",
      ps.count_trading_days(CR_LATE, next_trading_day(T25)) <= 10
      and [x["locked_qty"] for x in _k(r, "rights_locked")] == [5000] and not _k(r, "capped"), r["notes"])
check("P16 probe arch-review: thiếu openQuantity ⇒ không khoá (19.000,0); có ⇒ khoá đúng phần broker giữ",
      aei._rights_locked_split(TK, 19000, 5000, {TK: {"sellable": 16000}}) == (19000, 0)
      and aei._rights_locked_split(TK, 19000, 5000, {TK: {"sellable": 16000, "qty": 19000}}) == (16000, 3000))
LK = [{"ticker": TK, "book": "LAG", "locked_qty": 5000, "reason": "SCL book=LAG: 5000cp CP quyền mua KHOÁ fixture"}]
CPD = [{"ticker": TK, "book": "LAG", "desired_qty": 19000, "capped_qty": 14000, "reason": "x",
        "rights_diag": "lô quyền mua 5000cp ... đã 11 phiên > hạn 10 phiên"}]
aei.BLOCK_ALERT_STATE_PATH = os.path.join(ROOT_TMP, "alert_state_p17.json")
l1, st = aei._new_block_alert_lines(ACC, [], [], "2026-12-01", LK)
aei._atomic_write_json(aei.BLOCK_ALERT_STATE_PATH, st)
l2, _st = aei._new_block_alert_lines(ACC, [], [], "2026-12-02", LK)
l3, _st = aei._new_block_alert_lines(ACC, [], CPD, "2026-12-02", [])
check("P17 alert: khoá báo ℹ️ 1 lần (dedup ngày sau); hết hạn ⇒ ⚠️ cắt kèm chẩn đoán",
      len(l1) == 1 and l1[0].startswith("ℹ️") and l2 == [] and len(l3) == 1 and "đã 11 phiên" in l3[0], (l1, l2, l3))
# <<< B1 vòng 2
# >>> rights alert NB1 (25/10, arch-review 22/10 NON-BLOCKING 1): plan_date == listing_date ⇒ VẪN khoá.
# auto_exit chạy tối T−1 (plan_date = listing_date), broker tradeQuantity chưa gồm lô quyền ⇒ bản
# `ld > plan_date` ra ⚠️ "đã tới ngày niêm yết… broker vẫn chưa cho bán" giả cho MỌI đợt niêm yết.
EVE = nth(T25, 39)
assert next_trading_day(EVE) == LIST
r = run_exit("p18_listing_eve", EVE, (5_000, 0), fills=[(S26, (TK, "sell", 14_000, 25_400, "LAG"))],
             subs=[sub(listing=LIST)])
check("P18 biên plan_date == listing_date (tối T−1): khoá 5.000 (ℹ️), KHÔNG ⚠️ cắt, không lệnh",
      r["sells"] == [] and [x["locked_qty"] for x in _k(r, "rights_locked")] == [5000] and not _k(r, "capped"),
      (r["sells"], r["notes"]))
check("P18b biên hàm: listing_date == plan_date ⇒ khoá; == plan_date−1 phiên ⇒ hết khoá (đối chứng P12)",
      aei._rights_lock_status([{"qty": 5000, "credit_date": PAY.isoformat(), "listing_date": LIST.isoformat()}],
                              LIST.isoformat())[0] == 5000
      and aei._rights_lock_status([{"qty": 5000, "credit_date": PAY.isoformat(), "listing_date": EVE.isoformat()}],
                                  LIST.isoformat())[0] == 0)


def _inj(plan_date, held, sellable):
    pl_, inj_, cap_, lk_ = {"plan_date": plan_date, "orders": []}, [], [], []
    aei._inject_sell(pl_, {TK: {"qty": held, "sellable": sellable}}, TK, 19_000, 25_400, "LAG", "LAG", "n",
                     "X", inj_, cap_, "d", rights_lots=[{"qty": 5000, "credit_date": PAY.isoformat(),
                                                         "listing_date": LIST.isoformat(), "event_id": EVID}],
                     locked_notes=lk_)
    return [o["qty"] for o in pl_["orders"]], [c["capped_qty"] for c in cap_], [x["locked_qty"] for x in lk_]


check("P18c HÀNH VI ĐỔI (công bố): tối T−1, 1 book (held 19.000/sellable 14.000) ⇒ lệnh 14.000 — y hệt bản cũ "
      "(cắt về sellable), chỉ đổi ⚠️→ℹ️", _inj(LIST.isoformat(), 19_000, 14_000) == ([14_000], [], [5000]),
      _inj(LIST.isoformat(), 19_000, 14_000))
check("P18d HÀNH VI ĐỔI (công bố): tối T−1, mã có thêm 10.000 ở book khác (held 29.000/sellable 24.000) ⇒ "
      "lệnh LAG 14.000 (bản cũ 19.000: ăn 5.000 sellable của book kia), lô quyền bán phiên sau",
      _inj(LIST.isoformat(), 29_000, 24_000) == ([14_000], [], [5000])
      and _inj(nth(LIST, 1).isoformat(), 29_000, 24_000) == ([19_000], [], []),
      (_inj(LIST.isoformat(), 29_000, 24_000), _inj(nth(LIST, 1).isoformat(), 29_000, 24_000)))
# <<< rights alert NB1
check("P11 không gọi subprocess thật (bus/Discord)", CALLS == [], CALLS)

# ================================ N. chuỗi NAV ================================
print("\nN. daily_nav_snapshot / verify_account_snapshot / reconcile_equity / cash_identity")
ACCT, ACCT_NO = "SpaceX", "0002023347"      # nhãn thật, MỌI thư mục là sandbox
Q0, COST, S_PX, RQ = 14000.0, 30000.0, 12500.0, 5000.0
CASH_BUY = 899_592_600.0
P_PREV, P = "2025-10-24", "2025-10-27"
CASH_PAID = CASH_BUY - RQ * S_PX
COST_BLEND = (Q0 * COST + RQ * S_PX) / (Q0 + RQ)
PRICE = {"2025-10-01": 30000.0, "2025-10-24": 20500.0, "2025-10-27": 20000.0,
         "2025-11-04": 19900.0, "2025-11-05": 20500.0}
SDIV_EV = {"ticker": TK, "date": "2025-11-06", "event_code": "ISS", "price_adjusting": True,
           "exercise_ratio": "0.09", "issue_method_vi": "Trả Cổ tức bằng Cổ phiếu",
           "value_per_share": None, "event_status": "executed"}


def nsub(qty=RQ, credit=P, registered=None):
    return {"account": ACCT, "account_no": ACCT_NO, "ticker": TK, "event_id": EVID, "event_hash": H,
            "exright_date": "2025-10-17", "exercise_ratio": 0.35714286, "issue_price_vnd": S_PX,
            "subscribed_qty": int(qty), "payment_date": credit, "credit_date": credit,
            "registered_date": registered, "listing_date": None, "decided_by": "user",
            "at": "2025-10-27T10:00:00+07:00", "source": "fixture"}


def pos_rec(ts, qty, mp, trade=None, cost=None):
    return {"kind": "positions", "ts": ts, "account_no": ACCT_NO, "payload": {"positions": [
        {"symbol": TK, "accountNo": ACCT_NO, "openQuantity": qty, "tradeQuantity": qty if trade is None else trade,
         "marketPrice": mp, "costPrice": COST if cost is None else cost, "status": "OPEN", "loanPackageId": 1841}]}}


def bal_rec(ts, cash):
    return {"kind": "balances", "ts": ts, "account_no": ACCT_NO, "payload": {
        "stock": {"totalCash": cash, "availableCash": cash, "totalDebt": 0.0, "withdrawableCash": cash,
                  "depositInterest": 1000.0, "depositFeeAmount": 0.0, "cashDividendReceiving": 0.0,
                  "secureAmount": 0.0, "orderSecured": 0.0}, "egg": {"totalValue": 0.0}}}


def write_raw(d, date, recs):
    with open(os.path.join(d, f"dnse_raw_{date}.jsonl"), "a", encoding="utf-8") as f:
        for r_ in recs:
            f.write(json.dumps(r_) + "\n")


JHDR = "ts,event,parent_id,ticker,side,child_oid,qty,price,filled_total,book,play_type,note\n"


def write_journal(d, date, rows=()):
    with open(os.path.join(d, f"exec_{ACCT}_{date}_journal.csv"), "w", encoding="utf-8") as f:
        f.write(JHDR + "".join(x + "\n" for x in rows))


def write_nav_hist(d, rows):
    fn = ["date", "nav", "mtm_stock", "cash", "margin_debt", "offbook_assets", "egg_assets", "balance_ts",
          "cum_dividend_excl", "nav_is_estimate", "nav_source"]
    with open(os.path.join(d, f"nav_history_{ACCT}.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fn)
        w.writeheader()
        for r_ in rows:
            w.writerow({k: r_.get(k, "") for k in fn})


def hist_row(date, qty, px, cash, ts):
    return {"date": date, "nav": f"{qty * px + cash:.0f}", "mtm_stock": f"{qty * px:.0f}", "cash": f"{cash:.0f}",
            "margin_debt": "0", "offbook_assets": "0", "egg_assets": "0", "balance_ts": ts,
            "cum_dividend_excl": "0", "nav_is_estimate": "False", "nav_source": "fx"}


SDIV_CONFIRMED = {"id": "SCL-2025-11-06-SDIV", "ticker": TK, "event_type": "STOCK_DIVIDEND",
                  "qty_multiplier": 1.09, "ex_date": "2025-11-06", "broker_effective_ts": "2025-11-05T19:30:00",
                  "_status": "CONFIRMED — fixture"}


def ndir(tag, subs=(), actions=()):
    d = os.path.join(ROOT_TMP, "N_" + tag)
    os.makedirs(d)
    rd = os.path.join(d, "lag_rights")
    os.makedirs(rd)
    with open(os.path.join(rd, "subscriptions.json"), "w") as f:
        json.dump({"subscriptions": list(subs)}, f)
    os.environ["MIKE_LAG_RIGHTS_DIR"] = rd
    with open(os.path.join(d, "corp_actions.json"), "w") as f:
        json.dump({"actions": list(actions)}, f)
    return d


class _Stub:
    class R:
        returncode, stdout, stderr = 0, "", ""

    @staticmethod
    def run(*a, **k):
        return _Stub.R()


def run_nav(d, prev, date, q_prev, q_now, mp_prev, mp_now, cash_prev, cash_now, trade_now=None,
            cost_now=None, events=()):
    write_raw(d, prev, [pos_rec(f"{prev}T19:05:00", q_prev, mp_prev), bal_rec(f"{prev}T19:05:10", cash_prev)])
    write_raw(d, date, [pos_rec(f"{date}T19:10:00", q_now, mp_now, trade_now, cost_now),
                        bal_rec(f"{date}T19:10:20", cash_now)])
    for x in ("2025-10-01", prev, date):
        write_journal(d, x)
    with open(os.path.join(d, f"corp_action_daily_{date}.json"), "w") as f:
        json.dump({"asof": date, "status": "OK", "usable": True, "feed_status": "FRESH",
                   "upcoming_events_held": list(events)}, f)
    write_nav_hist(d, [hist_row(prev, q_prev, PRICE.get(prev, mp_prev), cash_prev, f"{prev}T19:05:10")])
    old = (D.EXEC_DIR, D.CORP_ACTIONS_FILE, D.HISTORY_FILE_TMPL, CAD.snapshot_path, D.bq_raw_prices,
           D.cum_dividend_double_count, sys.argv, V.EXEC_DIR, D.subprocess, D.rights_subscription_check)
    D.EXEC_DIR = V.EXEC_DIR = d
    D.CORP_ACTIONS_FILE = os.path.join(d, "corp_actions.json")
    D.HISTORY_FILE_TMPL = os.path.join(d, "nav_history_{account}.csv")
    CAD.snapshot_path = lambda x, failed=False: os.path.join(d, f"corp_action_daily_{x}.json")
    D.bq_raw_prices = lambda tickers, dt_: ({t: PRICE[date] for t in tickers}, {t: PRICE[prev] for t in tickers}, None)
    D.cum_dividend_double_count = lambda *a, **k: {"amount": 0.0, "delta": 0.0, "expected_bq": None,
                                                   "tickers": [], "bq_max_date": None, "note": "", "warnings": []}
    D.subprocess = _Stub
    # Tắt đường N3 (bước giá vốn + BQ) để đo RIÊNG đường khai báo — N3 có selfcheck riêng.
    D.rights_subscription_check = lambda *a, **k: (False, "selfcheck: N3 tắt")
    os.environ.pop("NAV_SANITY_MAX_PCT", None)
    sys.argv = ["daily_nav_snapshot.py", "--account", ACCT, "--account-no", ACCT_NO, "--date", date, "--from-raw"]
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            rc = D.main()
    finally:
        (D.EXEC_DIR, D.CORP_ACTIONS_FILE, D.HISTORY_FILE_TMPL, CAD.snapshot_path, D.bq_raw_prices,
         D.cum_dividend_double_count, sys.argv, V.EXEC_DIR, D.subprocess, D.rights_subscription_check) = old
    sp = os.path.join(d, f"nav_snapshot_{ACCT}_{date}.json")
    return rc, (json.load(_real_open(sp)) if os.path.exists(sp) else None), err.getvalue()


pay_kw = dict(prev=P_PREV, date=P, q_prev=Q0, q_now=Q0 + RQ, mp_prev=20500, mp_now=20000,
              cash_prev=CASH_BUY, cash_now=CASH_PAID, trade_now=Q0, cost_now=COST_BLEND)
rc, snap, err = run_nav(ndir("n0_control"), **pay_kw)
check("N0 ĐỐI CHỨNG ngày nộp tiền không khai báo (N3 tắt) ⇒ rc=5", rc == 5, rc)
rc, snap, err = run_nav(ndir("n1_decl", [nsub()]), **pay_kw)
check("N1 có khai báo ⇒ rc=0, NAV = 19.000×20.000 + tiền", rc == 0 and snap
      and abs(snap["nav"] - ((Q0 + RQ) * 20000 + CASH_PAID)) < 1, (rc, err[-400:]))
rc, snap, err = run_nav(ndir("n1b_wrong_qty", [nsub(qty=4999)]), **pay_kw)
check("N1b khai sai KL (4.999) ⇒ vẫn chặn rc=5 (fail-closed)", rc == 5, rc)
rc, snap, err = run_nav(ndir("n1c_wrong_day", [nsub(credit="2025-10-24")]), **pay_kw)
check("N1c khai sai ngày credit ⇒ vẫn chặn rc=5", rc == 5, rc)
# N4 — cổ tức CP 9% (GDKHQ 11-06) trong khoảng chờ: broker credit 1.260 (chỉ 14.000 hưởng)
# >>> N4 (PHẦN 2 — legal-vn 22/10)
sd_kw = dict(prev="2025-11-04", date="2025-11-05", q_prev=Q0 + RQ, q_now=Q0 + RQ + 1260, mp_prev=19900,
             mp_now=round(20500 / 1.09), cash_prev=CASH_PAID, cash_now=CASH_PAID, events=[SDIV_EV])
rc, snap, err = run_nav(ndir("n4_control_no_decl", actions=[SDIV_CONFIRMED]), **sd_kw)
check("N4a ĐỐI CHỨNG (CONFIRMED ×1,09, không khai báo): 20.260/1,09 = 18.587 ≠ 19.000 ⇒ rc=5 (audit A5)",
      rc == 5, rc)
rc, snap, err = run_nav(ndir("n4_pending", [nsub()], [SDIV_CONFIRMED]), **sd_kw)
check("N4b lô quyền chờ: (20.260−5.000)/1,09 + 5.000 = 19.000 ⇒ --from-raw phục hồi rc=0, KL quy ngược 19.000",
      rc == 0 and snap and abs(snap["nav"] - ((Q0 + RQ) * 20500 + CASH_PAID)) < 1, (rc, err[-500:]))
rc, snap, err = run_nav(ndir("n4_pending_broker_1710", [nsub()], [SDIV_CONFIRMED]), **dict(sd_kw, q_now=Q0 + RQ + 1710))
check("N4c lô quyền chờ nhưng broker credit 1.710 ⇒ KHÔNG khớp kỳ vọng mới ⇒ chặn (không nới)",
      rc == 5 and "CHƯA GIẢI THÍCH" in err, (rc, err[-300:]))
det_p = D.classify_qty_residual(SDIV_EV, Q0 + RQ + 1260, Q0 + RQ, 0.0, "2025-11-04", pending_rights=RQ)
det_0 = D.classify_qty_residual(SDIV_EV, Q0 + RQ + 1260, Q0 + RQ, 0.0, "2025-11-04")
check("N4d classify_qty_residual: pending ⇒ share_event_credit (1.260); mặc định 0 ⇒ qty_unexplained như cũ",
      det_p[0] == "share_event_credit" and det_0[0] == "qty_unexplained", (det_p[0], det_0[0]))
# <<< N4


def run_ef(tag, subs, prev, date, q_prev, q_now, mp, events=(), broker_statement=False):
    """exdate_frame.classify_positions — cổng của compute_active_nav (mẫu số sizing).
    `broker_statement=True` = đường production (`compute_active_nav.py` gọi đúng cờ này): statement DNSE
    giả CÓ mặt nhưng KHÔNG có dòng SCL nào (CP quyền về không qua lệnh sàn) — hermetic, không đọc data/ thật."""
    d = ndir("E_" + tag, subs)
    write_raw(d, prev, [pos_rec(f"{prev}T19:05:00", q_prev, mp), bal_rec(f"{prev}T19:05:10", CASH_PAID)])
    write_raw(d, date, [pos_rec(f"{date}T19:10:00", q_now, mp), bal_rec(f"{date}T19:10:20", CASH_PAID)])
    for x in ("2025-10-01", prev, date):
        write_journal(d, x)
    with open(os.path.join(d, f"corp_action_daily_{date}.json"), "w") as f:
        json.dump({"asof": date, "status": "OK", "usable": True, "feed_status": "FRESH",
                   "upcoming_events_held": list(events)}, f)
    old = (D.EXEC_DIR, V.EXEC_DIR, CAD.snapshot_path, D.rights_subscription_check, BFC.load_broker_fills)
    BFC.load_broker_fills = lambda *a, **k: BFC.BrokerFills(True, "selfcheck statement rỗng", "fx")
    D.EXEC_DIR = V.EXEC_DIR = d
    CAD.snapshot_path = lambda x, failed=False: os.path.join(d, f"corp_action_daily_{x}.json")
    D.rights_subscription_check = lambda *a, **k: (False, "selfcheck: N3 tắt")
    try:
        with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            return EF.classify_positions(ACCT, ACCT_NO, date, {TK: {"total": q_now, "marketPrice": mp}},
                                         broker_statement=broker_statement)
    finally:
        D.EXEC_DIR, V.EXEC_DIR, CAD.snapshot_path, D.rights_subscription_check, BFC.load_broker_fills = old


ef_pay = dict(prev=P_PREV, date=P, q_prev=Q0, q_now=Q0 + RQ, mp=20000)
cr, bl = run_ef("pay_control", [], **ef_pay)
check("E0 ĐỐI CHỨNG active_nav ngày nộp tiền không khai báo (N3 tắt) ⇒ SCL blocked (rc=6)", TK in bl, bl)
cr, bl = run_ef("pay_decl", [nsub()], **ef_pay)
check("E1 có khai báo ⇒ active_nav không chặn", not bl and not cr, (cr, bl))
# >>> N4 (PHẦN 2 — legal-vn 22/10)
ef_sd = dict(prev="2025-11-04", date="2025-11-05", q_prev=Q0 + RQ, q_now=Q0 + RQ + 1260, mp=round(20500 / 1.09),
             events=[SDIV_EV])
cr, bl = run_ef("sd_control", [], **ef_sd)
check("E2 ĐỐI CHỨNG cổ tức CP 9%, lô quyền chưa khai: credit 1.260 ⇒ blocked", TK in bl, (cr, bl))
cr, bl = run_ef("sd_pending", [nsub()], **ef_sd)
check("E3 N4 lô quyền chờ: credit 1.260 = (19.000−5.000)×9% ⇒ credited, không chặn",
      TK in cr and not bl and cr[TK].get("pending_rights_qty") == RQ, (cr, bl))
# <<< N4
# >>> B2 vòng 2 (arch-review): đường sizing PRODUCTION (compute_active_nav ⇒ broker_statement=True)
cr, bl = run_ef("pay_control_bs", [], broker_statement=True, **ef_pay)
check("E0b ĐỐI CHỨNG broker_statement=True, không khai báo ⇒ SCL blocked", TK in bl, bl)
cr, bl = run_ef("pay_decl_bs", [nsub()], broker_statement=True, **ef_pay)
check("E1b broker_statement=True + khai báo ⇒ lô quyền cộng vào lệnh khớp thật ⇒ không chặn",
      not bl and not cr, (cr, bl))
cr, bl = run_ef("sd_control_bs", [], broker_statement=True, **ef_sd)
check("E2b ĐỐI CHỨNG broker_statement=True, cổ tức CP, lô quyền chưa khai ⇒ blocked", TK in bl, (cr, bl))
cr, bl = run_ef("sd_pending_bs", [nsub()], broker_statement=True, **ef_sd)
check("E3b broker_statement=True + N4 lô chờ ⇒ credited 1.260, không chặn",
      TK in cr and not bl and cr[TK].get("pending_rights_qty") == RQ, (cr, bl))
# <<< B2 vòng 2


def run_vas(tag, subs, broker_qty=Q0 + RQ, extra_sdiv=False, cost_now=COST_BLEND):
    d = ndir("V_" + tag, subs)
    write_raw(d, "2025-10-01", [{"kind": "orders", "ts": "2025-10-01T15:00:00", "account_no": ACCT_NO,
                                 "payload": {"orders": [{"id": 1, "accountNo": ACCT_NO, "symbol": TK, "side": "NB",
                                                         "fillQuantity": Q0, "averagePrice": COST, "price": COST,
                                                         "modifiedDate": "2025-10-01T02:30:00Z",
                                                         "createdDate": "2025-10-01T02:20:00Z",
                                                         "orderStatus": "Filled"}]}},
                                pos_rec("2025-10-01T19:00:00", Q0, 30000), bal_rec("2025-10-01T19:00:10", CASH_BUY)])
    write_journal(d, "2025-10-01", [f"2025-10-01T09:30:00,FILL,P1,{TK},buy,C1,{int(Q0)},{COST},{int(Q0)},LAG,PEAD,"])
    write_raw(d, P, [pos_rec(f"{P}T19:10:00", broker_qty, 20000, Q0, cost_now), bal_rec(f"{P}T19:10:20", CASH_PAID)])
    write_journal(d, P)
    kdp = os.path.join(d, "kd.json")
    with open(kdp, "w") as f:
        json.dump({"discrepancies": []}, f)
    out_json = os.path.join(d, f"verified_snapshot_{ACCT}_{P}.json")
    old = (V.EXEC_DIR, V.KNOWN_DISCREPANCY_PATH, V.bq_close_prices, sys.argv, V.load_corp_actions)
    V.EXEC_DIR, V.KNOWN_DISCREPANCY_PATH = d, kdp
    V.bq_close_prices = lambda tickers, asof: ({t: PRICE[asof] for t in tickers}, None)
    V.load_corp_actions = lambda *a, **k: []
    sys.argv = ["verify_account_snapshot.py", "--account", ACCT, "--account-no", ACCT_NO,
                "--dates", f"2025-10-01,{P}", "--asof", P, "--out", out_json]
    rc = 0
    try:
        with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            try:
                V.main()
            except SystemExit as e:
                rc = e.code
    finally:
        V.EXEC_DIR, V.KNOWN_DISCREPANCY_PATH, V.bq_close_prices, sys.argv, V.load_corp_actions = old
    return d, out_json, rc, json.load(_real_open(out_json))


d0_, s0_, rc, res = run_vas("control", [])
p0 = res["positions"][0]
check("V0 ĐỐI CHỨNG không khai báo: giá vốn chỉ 14.000 @30.000 (hành vi cũ, audit B2.4)",
      p0["qty"] == Q0 and p0["true_avg_cost"] == COST)
dV, sV, rc, res = run_vas("decl", [nsub()])
p1 = res["positions"][0]
check("V1 có khai báo: 19.000 @25.394,7 = costPrice broker; verified=True",
      rc == 0 and p1["qty"] == Q0 + RQ and abs(p1["true_avg_cost"] - round(COST_BLEND, 1)) < 0.11 and res["verified"],
      (rc, p1, res["warnings"]))
check("V1b P&L chưa thực hiện = broker (19.000×(20.000−25.394,74) = −102,5tr)",
      abs(p1["unrealized_pnl"] - (Q0 + RQ) * (20000 - COST_BLEND)) < 1, p1["unrealized_pnl"])
_, _, rc, res = run_vas("decl_wrong", [nsub(qty=4999)], broker_qty=Q0 + RQ)
check("V2 khai 4.999 nhưng broker 19.000 ⇒ WARN qty ⇒ verified=False, exit 1",
      rc == 1 and not res["verified"], (rc, res["warnings"]))
# N4 ở giá vốn: lô quyền chờ không nhân hệ số cổ tức CP
# >>> N4 (PHẦN 2 — legal-vn 22/10)
acts = [{"ticker": TK, "ex_date": "2025-11-06", "qty_multiplier": 1.09}]
key = RS.event_key(RS.validate(nsub()))
m_rights = V.corp_action_multiplier(TK, P, "2025-11-10", acts, key=key)
m_norm = V.corp_action_multiplier(TK, "2025-10-01", "2025-11-10", acts, key="1")
check("V3 N4: hệ số cổ tức CP không áp lô quyền đang chờ (1,0), vẫn áp lô thường (1,09)",
      m_rights == 1.0 and m_norm == 1.09, (m_rights, m_norm))
# <<< N4

# >>> rights alert NB4 (25/10): N4 wire vào dividend_adjusted_return.credit_frame — trước đây gọi
# classify_qty_residual KHÔNG truyền pending_rights ⇒ cổ tức CP 9% credit sớm trong khoảng chờ VSDC
# (14.000×9% = 1.260, không phải 19.000×9% = 1.710) ⇒ 'unknown' (fail-closed, §21 UNVERIFIED).
import types as _types  # noqa: E402


def run_cf(tag, subs, qty_now):
    ndir("CF_" + tag, subs)                    # sổ khai báo sandbox (MIKE_LAG_RIGHTS_DIR)
    adj = _types.SimpleNamespace(ticker=TK, last_cum_date="2025-11-05", ex_date="2025-11-06",
                                 last_cum_price=20500.0)
    saved = {k: getattr(D, k) for k in ("_corp_action_daily_snapshot", "raw_positions", "previous_raw_qty",
                                        "net_fills_between", "held_event_next_session")}
    D._corp_action_daily_snapshot = lambda day: None
    D.raw_positions = lambda acc, day: ({TK: {"qty": qty_now, "marketPrice": 20500.0}}, f"{day}T19:00:00")
    D.previous_raw_qty = lambda acc, tk, day: (Q0 + RQ, "2025-11-04")
    D.net_fills_between = lambda *a, **k: {}
    D.held_event_next_session = lambda snap, day, tk: SDIV_EV
    try:
        return DAR.credit_frame(ACCT, ACCT_NO, [adj])[(TK, "2025-11-05")]
    finally:
        for k, v in saved.items():
            setattr(D, k, v)


f0 = run_cf("control", [], Q0 + RQ + 1260)
check("F0 ĐỐI CHỨNG không khai báo: 19.000→20.260 (phần dư 1.260 ≠ 19.000×9%) ⇒ unknown (fail-closed)",
      f0["status"] == "unknown" and f0["entitled"] is None, f0)
f1 = run_cf("pending", [nsub()], Q0 + RQ + 1260)
check("F1 N4: lô quyền 5.000 chờ VSDC ⇒ phần dư 1.260 = 14.000×9% ⇒ pre_credit, KL hưởng quyền 14.000 (không gồm lô chờ)",
      f1["status"] == "pre_credit" and abs(f1["entitled"] - Q0) < 1e-6 and "chờ VSDC" in f1["note"], f1)
f2 = run_cf("registered", [nsub(registered="2025-10-29")], Q0 + RQ + 1710)
check("F2 đối chứng: đã ghi nhận trước ex-date ⇒ pending 0 ⇒ 19.000×9% = 1.710 khớp ⇒ hưởng 19.000",
      f2["status"] == "pre_credit" and abs(f2["entitled"] - (Q0 + RQ)) < 1e-6 and "chờ VSDC" not in f2["note"], f2)
f3 = run_cf("pending_wrong", [nsub()], Q0 + RQ + 1710)
check("F3 lô chờ nhưng broker credit 1.710 (cả lô quyền) ⇒ vẫn unknown (không nới khi bằng chứng ngược)",
      f3["status"] == "unknown", f3)
# <<< rights alert NB4

# reconcile_equity trên snapshot V1
old = (V.EXEC_DIR, DAR.EXEC_LOG_DIR, sys.argv, RE.__dict__.get("load_corp_actions"))
V.EXEC_DIR = DAR.EXEC_LOG_DIR = dV
os.environ["MIKE_LAG_RIGHTS_DIR"] = os.path.join(dV, "lag_rights")   # sổ của ca V1 (run_vas sau đó đã đổi env)
sys.argv = ["reconcile_equity.py", "--account", ACCT, "--account-no", ACCT_NO, "--starting-capital",
            "1320000000", "--snapshot", sV, "--balance-raw", os.path.join(dV, f"dnse_raw_{P}.jsonl"),
            "--trading-fees", str(14000 * 30000 * 0.00097)]
import corp_actions as _CA  # noqa: E402
_old_lca = _CA.load_corp_actions
_CA.load_corp_actions = lambda *a, **k: []
rc = 0
out = io.StringIO()
try:
    with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(out):
        try:
            RE.main()
        except SystemExit as e:
            rc = e.code
finally:
    V.EXEC_DIR, DAR.EXEC_LOG_DIR, sys.argv = old[:3]
    _CA.load_corp_actions = _old_lca
rj = json.load(_real_open(sV.replace("verified_snapshot", "reconcile_equity")))
check("R1 reconcile_equity: hết lệch +62,5tr (|residual| < 5tr sàn), in dòng khai báo quyền mua",
      abs(rj["residual"]) < 5e6 and "CP quyền mua user khai" in out.getvalue(), (rj["residual"], rc))
check("R1b lô quyền vào replay realized: tổng giá trị mua = 14.000×30.000 + 5.000×12.500",
      abs(rj["fill_buy_value"] - (Q0 * COST + RQ * S_PX)) < 1, rj["fill_buy_value"])
# NB1 vòng 2: không truyền --trading-fees ⇒ phí ước tính KHÔNG tính lên lô quyền (phí 0)
old = (V.EXEC_DIR, DAR.EXEC_LOG_DIR, sys.argv)
V.EXEC_DIR = DAR.EXEC_LOG_DIR = dV
os.environ["MIKE_LAG_RIGHTS_DIR"] = os.path.join(dV, "lag_rights")
sys.argv = ["reconcile_equity.py", "--account", ACCT, "--account-no", ACCT_NO, "--starting-capital",
            "1320000000", "--snapshot", sV, "--balance-raw", os.path.join(dV, f"dnse_raw_{P}.jsonl")]
_CA.load_corp_actions = lambda *a, **k: []
try:
    with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
        try:
            RE.main()
        except SystemExit:
            pass
finally:
    V.EXEC_DIR, DAR.EXEC_LOG_DIR, sys.argv = old
    _CA.load_corp_actions = _old_lca
rj3 = json.load(_real_open(sV.replace("verified_snapshot", "reconcile_equity")))
_fp = rj3["fee_rate_pct_used"] / 100.0
check("R3 NB1: phí mặc định = 14.000×30.000×phí (lô quyền 5.000×12.500 phí 0); fee_gap không tính lô quyền",
      abs(rj3["trading_fees_used"] - Q0 * COST * _fp) < 1
      and abs(rj3["explain_fee_on_turnover_gap_est"] - (Q0 * COST * _fp - Q0 * COST * _fp)) < 1,
      (rj3["trading_fees_used"], rj3["explain_fee_on_turnover_gap_est"], Q0 * COST * _fp))
check("R1c ĐỐI CHỨNG credit = payment: không có phải thu (rights_paid_not_credited = 0)",
      rj["rights_paid_not_credited"] == 0 and rj3["rights_paid_not_credited"] == 0)


def run_re(d, snap, balance_date=P):
    """reconcile_equity (--trading-fees cố định) trên snapshot `snap`; trả (json, stdout)."""
    old_ = (V.EXEC_DIR, DAR.EXEC_LOG_DIR, sys.argv)
    V.EXEC_DIR = DAR.EXEC_LOG_DIR = d
    os.environ["MIKE_LAG_RIGHTS_DIR"] = os.path.join(d, "lag_rights")
    sys.argv = ["reconcile_equity.py", "--account", ACCT, "--account-no", ACCT_NO, "--starting-capital",
                "1320000000", "--snapshot", snap, "--balance-raw", os.path.join(d, f"dnse_raw_{balance_date}.jsonl"),
                "--trading-fees", str(14000 * 30000 * 0.00097)]
    _CA.load_corp_actions = lambda *a, **k: []
    o_ = io.StringIO()
    try:
        with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(o_):
            try:
                RE.main()
            except SystemExit:
                pass
    finally:
        V.EXEC_DIR, DAR.EXEC_LOG_DIR, sys.argv = old_
        _CA.load_corp_actions = _old_lca
    return json.load(_real_open(snap.replace("verified_snapshot", "reconcile_equity"))), o_.getvalue()


# >>> rights alert NB2-reconcile (25/10): khai credit_date > payment_date, asof nằm GIỮA ⇒ tiền đã rời
# (balance CASH_PAID), CP chưa về broker (openQuantity 14.000) ⇒ bản cũ lệch +5.000×12.500 = +62,5tr.
SPLIT = dict(nsub(credit="2025-10-29"), payment_date=P)
dS, sS, rc, resS = run_vas("split_mid", [SPLIT], broker_qty=Q0, cost_now=COST)
rjS, outS = run_re(dS, sS)
check("R4 credit > payment, asof ở giữa: snapshot CHƯA có lô quyền (14.000) nhưng residual |.| < 5tr nhờ "
      "phải thu 5.000×12.500 = 62,5tr ở vế phải, có dòng in",
      resS["positions"][0]["qty"] == Q0 and abs(rjS["rights_paid_not_credited"] - RQ * S_PX) < 1
      and abs(rjS["residual"]) < 5e6 and "Phải thu CP quyền mua đã nộp tiền" in outS,
      (resS["positions"][0]["qty"], rjS["rights_paid_not_credited"], rjS["residual"]))
check("R4b residual R4 ≈ residual R1 (credit = payment, cùng tiền) — cùng thực tế kinh tế, cùng kết luận",
      abs(rjS["residual"] - rj["residual"]) < 1e6, (rjS["residual"], rj["residual"]))
# <<< rights alert NB2-reconcile
ev_r = RS.fill_events(ACCT, path=os.path.join(dV, "lag_rights", "subscriptions.json"))
evs = {"2025-10-01": [("2025-10-01T09:30:00", "1", TK, "buy", Q0, COST)], **ev_r,
       "2025-11-20": [("2025-11-20T10:00:00", "2", TK, "sell", Q0 + RQ, 20000.0)]}
rz = RE.realized_pnl_from_events(evs, "2025-11-20", [])
check("R2 bán cả 19.000 @20.000: realized = 19.000×20.000 − 482,5tr = −102,5tr, không phần bán 'untraced'",
      abs(rz["realized"] - ((Q0 + RQ) * 20000 - (Q0 * COST + RQ * S_PX))) < 1 and rz["untraced_sell_proceeds"] == 0,
      (rz["realized"], rz["untraced_sell_proceeds"]))


def run_ci(tag, subs):
    d = ndir("C_" + tag, subs)
    seed = os.path.join(d, "seed.json")
    with open(seed, "w") as f:
        json.dump({}, f)
    write_raw(d, P_PREV, [pos_rec(f"{P_PREV}T19:05:00", Q0, 20500), bal_rec(f"{P_PREV}T19:05:10", CASH_BUY)])
    write_raw(d, P, [pos_rec(f"{P}T19:10:00", Q0 + RQ, 20000, Q0, COST_BLEND), bal_rec(f"{P}T19:10:20", CASH_PAID)])
    write_nav_hist(d, [hist_row(P_PREV, Q0, 20500, CASH_BUY, f"{P_PREV}T19:05:10"),
                       hist_row(P, Q0 + RQ, 20000, CASH_PAID, f"{P}T19:10:20")])
    inc = os.path.join(d, "inc.json")
    with open(inc, "w") as f:
        json.dump({ACCT: {"account_no": ACCT_NO, "inception_date": "2025-09-30"}}, f)
    flows = os.path.join(d, "flows.json")
    with open(flows, "w") as f:
        json.dump({"flows": []}, f)
    with open(os.path.join(d, "acks.json"), "w") as f:
        json.dump({}, f)
    res = CI.check_account(ACCT, nav_dir=d, raw_dir=d, flows_path=flows, inception_path=inc, seed_path=seed,
                           acks_path=os.path.join(d, "acks.json"),
                           corp_actions_path=os.path.join(d, "corp_actions.json"))
    return [w for w in res["windows"] if w.get("checkable")][-1]


w0 = run_ci("control", [])
check("C0 ĐỐI CHỨNG không khai báo: cửa sổ có qty_gaps SCL +5.000 (cần người xem)",
      w0["qty_gaps"].get(TK) == RQ, w0["qty_gaps"])
w1 = run_ci("decl", [nsub()])
check("C1 có khai báo: cửa sổ đóng (không qty_gaps, phần dư ≈ 0 vì phí = 0)",
      not w1["qty_gaps"] and abs(w1["unexplained"]) < 1000 and not w1["kind"],
      (w1["qty_gaps"], w1["unexplained"], w1["kind"]))
lg = CI.load_rights_subscription_fills(ACCT, ACCT_NO, path=os.path.join(ROOT_TMP, "N_C_decl", "lag_rights",
                                                                      "subscriptions.json"))
ndir("C_split", [dict(nsub(credit="2025-10-29"), payment_date=P)])
lg2 = CI.load_rights_subscription_fills(ACCT, ACCT_NO)
check("C2 NB2: payment=credit ⇒ 1 bản ghi (đối chứng); payment<credit ⇒ chân TIỀN ở payment_date, chân KL ở credit_date",
      [(x["moment"].date().isoformat(), x["qty"], x["value"]) for x in lg] == [(P, RQ, RQ * S_PX)]
      and sorted((x["moment"].date().isoformat(), x["qty"], x["value"]) for x in lg2)
      == [(P, 0.0, RQ * S_PX), ("2025-10-29", RQ, 0.0)], (lg, lg2))

# ================================ tổng ================================
shutil.rmtree(ROOT_TMP, ignore_errors=True)
n_ok = sum(ok for _, ok in RESULTS)
print(f"\n{n_ok}/{len(RESULTS)} PASS")
sys.exit(0 if n_ok == len(RESULTS) else 1)
