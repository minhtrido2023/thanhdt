#!/usr/bin/env python3
"""Selfcheck GĐ3 clearing PARK→LAG/BAL: `clear_books --apply`, `apply_book_transfers`, `book_clearing`,
hoàn tác trong `merge_park_orders`, bất biến `preflight_check.sh`, khối `send_plan_report.sh`.

Sandbox offline: bootstrap/journal/plan giả trong tmp (nhãn SBX), sổ lô = `park_holdings` THẬT replay
journal THẬT (broker bơm tay, `account_profile` giả — không đọc secrets/DNSE), lịch phiên THẬT
(`portfolio_status.count_trading_days`). Ca nền = SpaceX VPB 26-29/10 thu nhỏ: PARK 160@07-02 +
126@08-11, LAG mua 1.500 ngày 26/10; plan 29/10 bán PARK 200 + mua LAG VPB 1.500 + mua LAG FPT 300.

  A  clear_books APPLY : A1 knob tắt ⇒ SHADOW, plan nguyên byte · A2 ghi transfer 200, mua 1.500→1.300,
     bán PARK 200→gỡ, FPT không đụng · A3 chạy lại = cùng orders/transfer · A4 plan đã duyệt ⇒ rc2,
     không ghi · A5 trượt cổng book đích ⇒ không transfer · A6 bán lẻ full-exit 286 ⇒ m=200, còn 86
  M  merge_park_orders : hoàn tác (mua về 1.500, hết book_transfers) · transfer APPLIED ⇒ REFUSED
  B  apply_book_transfers (journal THẬT + sổ lô THẬT): B1 áp ⇒ journal 1 dòng, sổ PARK 86 / LAG +200
     entry 29/10, Σ VPB bất biến, reconcile OK · B2 chạy lại ⇒ không dòng thứ 2 · B3 kill sau journal
     trước plan ⇒ chạy lại chỉ đánh dấu APPLIED · B4 lỗi giữa chừng ⇒ emergency khôi phục APPLIED theo
     journal · B5 thiếu sellable ⇒ PAUSE, gỡ lệnh liên kết, FPT giữ, rc3, journal không ghi · B6 lô quyền ·
     B7 PARK chưa T+2 · B8 plan bị sửa sau clearing · B9 chưa duyệt ⇒ không làm gì · B10 BOT_STOP ·
     B11 chéo account · B12 id trùng khác nội dung · B13 BANNED · B14 journal header cũ ⇒ không ghi ·
     B15 trượt cổng · B16 2 sổ đích vượt PARK ⇒ cái sau PAUSE · B17 main() plan không transfer ⇒ rc0
     · B18 nhiều đêm: đêm 2 sổ thấy lô chuyển đêm 1
  C  preflight: plan sau clearing ⇒ OK · sửa qty ⇒ BOOK_XFER_MISMATCH · bán+chuyển > sellable ⇒ đỏ
  D  send_plan_report: khối "Chuyển nhãn sổ" hiện, entry hỏng ⇒ không sập
Mutant (phải bị bắt): xem MUTANTS cuối file.

Chạy: python3 mike/bin/book_clearing_g3_selfcheck.py   (rc 0 = PASS). Đặt MIKE_BOT_TEST_MODE=1 (§5b).
"""
import copy
import csv
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import park_holdings as PH  # noqa: E402
import wc_paths  # noqa: E402
from portfolio_status import count_trading_days  # noqa: E402

WC = wc_paths.find_wc_root(__file__)
LABEL, PD, ASOF = "SBX", "2026-10-29", "2026-10-28"
XID = f"XFER-{LABEL}-{PD}-VPB-PARK-LAG"
HDR = ["ts", "event", "parent_id", "ticker", "side", "child_oid", "qty", "price", "filled_total",
       "book", "play_type", "note"]
BOOT = [("VPB", "PARK", 160, 22154, "2026-07-02"), ("VPB", "PARK", 126, 20556, "2026-08-11"),
        ("FPT", "LAG", 500, 100000, "2026-09-15")]
FAILS = []
QUIET = [False]


def check(name, cond, detail=""):
    if not QUIET[0]:
        print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILS.append(name)
    return bool(cond)


# ───────────────────────────────────────────── module loader (cho mutant)

SRC = {n: os.path.join(HERE, f"{n}.py") for n in
       ("book_clearing", "apply_book_transfers", "clear_books", "merge_park_orders")}


def load_mods(mut=None):
    """Nạp 4 module từ text (mutant: (tên, old, new)). book_clearing nạp trước và đặt vào
    sys.modules để 3 module kia import đúng bản (thật hoặc mutant)."""
    mods, saved = {}, sys.modules.get("book_clearing")
    try:
        for n in ("book_clearing", "apply_book_transfers", "clear_books", "merge_park_orders"):
            src = open(SRC[n], encoding="utf-8").read()
            if mut and mut[0] == n:
                assert src.count(mut[1]) == 1, f"mutant {mut} không khớp đúng 1 chỗ"
                src = src.replace(mut[1], mut[2])
            spec = importlib.util.spec_from_loader(f"_g3_{n}", loader=None, origin=SRC[n])
            m = importlib.util.module_from_spec(spec)
            m.__file__ = SRC[n]
            if n == "book_clearing":
                sys.modules["book_clearing"] = m
            if n == "apply_book_transfers":
                AB_SRC[0] = src
            exec(compile(src, SRC[n], "exec"), m.__dict__)
            mods[n] = m
    finally:
        if saved is not None:
            sys.modules["book_clearing"] = saved
    mods["apply_book_transfers"].BC = mods["book_clearing"]   # import muộn ⇒ gắn tay bản (mutant) đang test
    return mods


# ───────────────────────────────────────────── sandbox

class SB:
    def __init__(self, journal=None, boot=None):
        self.root = tempfile.mkdtemp(prefix="g3_")
        self.ex, self.pl = os.path.join(self.root, "exec"), os.path.join(self.root, "plans")
        os.makedirs(self.ex)
        os.makedirs(self.pl)
        json.dump({"_status": "APPROVED selfcheck", "reconcile_ok": True, "day0_date": "2026-10-01",
                   "broker_source": {"ts": "2026-09-30T19:10:00"},
                   "positions": [{"ticker": t, "book": b, "qty": q, "cost_price_vnd": p, "entry_date": d}
                                 for t, b, q, p, d in (boot or BOOT)]},
                  open(os.path.join(self.pl, f"bootstrap_book_snapshot_{LABEL}_20261001.json"), "w"))
        days = {"2026-10-26": [["2026-10-26T09:40:00", "FILL", "B1", "VPB", "buy", "c1", 1500, 23000,
                                1500, "LAG", "LAG_LO", ""]]}
        for d, rows in (journal or {}).items():
            days.setdefault(d, []).extend(rows)
        for d, rows in days.items():
            with open(os.path.join(self.ex, f"exec_{LABEL}_{d}_journal.csv"), "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(HDR)
                w.writerows(rows)
        self.broker = {"VPB": {"qty": 1786, "sellable": 1786}, "FPT": {"qty": 500, "sellable": 500}}
        self.post = None   # hậu xử lý sổ lô (lô quyền / chưa T+2)

    def holdings(self, label, asof):
        PH.account_profile = lambda lb: {"label": lb, "account_id": "000", "excluded_tickers": []}
        pos = {t: {"qty": v["qty"], "market_price": 10000.0, "sellable": v["sellable"]}
               for t, v in self.broker.items()}
        h = PH.park_holdings(label, asof=asof, plan_dir=self.pl, exec_dir=self.ex,
                             broker=(pos, 0.0, {"source": "selfcheck"}), corp_actions=[],
                             rights_subs=[], broker_statement=False, need_price=False)
        if self.post:
            self.post(h)
        return h

    def plan_path(self, d=PD):
        return os.path.join(self.pl, f"plan_{LABEL}_{d}.json")

    def write_plan(self, plan, d=PD):
        json.dump(plan, open(self.plan_path(d), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    def read_plan(self, d=PD):
        return json.load(open(self.plan_path(d), encoding="utf-8"))

    def journal_rows(self, d=PD):
        p = os.path.join(self.ex, f"exec_{LABEL}_{d}_journal.csv")
        return list(csv.DictReader(open(p, newline="", encoding="utf-8"))) if os.path.exists(p) else []

    def close(self):
        shutil.rmtree(self.root, ignore_errors=True)


def base_plan(park_sell=200, approved=None, d=PD, asof=ASOF):
    return {"plan_date": d, "account": LABEL, "signal_date": asof, "strategy": "t",
            "strategy_version": "t", "state": 2, "state_name": "NEUTRAL", "nav_basis": {},
            "mode": "live", "requires_user_approval": True, "approved_by": approved,
            "park_trim_proposal": {"asof": asof},
            "orders": [
                {"id": "SELL-VPB-PARK-01", "ticker": "VPB", "side": "sell", "qty": park_sell,
                 "book": "PARK", "play_type": "PARK_TRIM", "ref_price": 23500.0, "priority": 1,
                 "merge_owner": "park_merge_v1", "merged_from": {"sellable_at_calc": 286}},
                {"id": "BUY-VPB-LAG-01", "ticker": "VPB", "side": "buy", "qty": 1500, "book": "LAG",
                 "play_type": "LAG_LO", "ref_price": 23500.0, "priority": 3},
                {"id": "BUY-FPT-LAG-01", "ticker": "FPT", "side": "buy", "qty": 300, "book": "LAG",
                 "play_type": "LAG_LO", "ref_price": 100000.0, "priority": 3}]}


EV_NONE = (lambda tickers, since=None, until=None, codes=None: [])
GATE_OK = (lambda plan, x, ex: (True, "stub"))
GATE_NO = (lambda plan, x, ex: (False, "stub: 8L rating=4"))


def cb_apply(M, sb, knob=True, gates=GATE_OK, d=PD, asof=ASOF, events=EV_NONE):
    return M["clear_books"].run_account(
        LABEL, d, asof, sb.pl, os.path.join(sb.root, "out"), 5, count_fn=count_trading_days,
        holdings_fn=sb.holdings, apply=True,
        knob_fn=(lambda: (knob, "stub")), gates_fn=gates, events_fn=events)


def ab_deps(M, sb, approval=None, banned=(), gates=GATE_OK, now=f"{PD}T09:01:00", events=EV_NONE,
            approval_fn=None):
    import datetime as dt
    from zoneinfo import ZoneInfo
    return {"ph": PH, "holdings_fn": sb.holdings, "banned_fn": (lambda: set(banned)),
            "count_fn": count_trading_days, "gates_fn": gates,
            "events_fn": events,
            "approval_fn": approval_fn or (lambda plan: approval),
            "now_fn": (lambda: dt.datetime.fromisoformat(now).replace(tzinfo=ZoneInfo("Asia/Ho_Chi_Minh")))}


def ab_run(M, sb, d=PD, approve=True, **kw):
    if approve:   # clear_books từ chối plan đã duyệt ⇒ sáng thực thi mới có chữ ký (như production)
        p = sb.read_plan(d)
        if not p.get("approved_by"):
            p["approved_by"] = "user"
            sb.write_plan(p, d)
    plan = sb.read_plan(d)
    stop = os.path.join(sb.root, "BOT_STOP")
    return M["apply_book_transfers"].run(LABEL, d, sb.plan_path(d), plan, sb.ex,
                                         ab_deps(M, sb, **kw), bot_stop=stop)


def cleared(M, park_sell=200):
    """sandbox + plan đã clear_books --apply."""
    sb = SB()
    sb.write_plan(base_plan(park_sell))
    rc, rep = cb_apply(M, sb)
    return sb, rc, rep


ORIG_QTY = {"SELL-VPB-PARK-01": 200, "BUY-VPB-LAG-01": 1500, "BUY-FPT-LAG-01": 300}


def orders_qty(p):
    return {o["id"]: o["qty"] for o in p["orders"]}


def n_xfer_rows(sb, d=PD):
    return sum(1 for r in sb.journal_rows(d) if r.get("event") == "BOOK_TRANSFER")


def strip_ts(plan):
    p = copy.deepcopy(plan)
    p.pop("book_clearing", None)
    for x in p.get("book_transfers") or []:
        x.pop("created_at", None)
    return p


# ───────────────────────────────────────────── kịch bản

def part_a(M, r):
    sb = SB()
    try:
        sb.write_plan(base_plan())
        raw = open(sb.plan_path(), "rb").read()
        rc, rep = cb_apply(M, sb, knob=False)
        r["A1_knob_off_shadow_plan_untouched"] = (rc == 0 and rep["mode"] == "SHADOW"
                                                  and open(sb.plan_path(), "rb").read() == raw
                                                  and bool(rep.get("apply_refused"))
                                                  and len(rep["opportunities"]) == 1)
        rc, rep = cb_apply(M, sb)
        p = sb.read_plan()
        by = {o["id"]: o for o in p["orders"]}
        xs = p.get("book_transfers") or []
        r["A2_apply_written"] = (rc == 0 and rep["mode"] == "APPLY" and len(xs) == 1
                                 and xs[0]["id"] == XID and xs[0]["qty"] == 200
                                 and by["BUY-VPB-LAG-01"]["qty"] == 1300
                                 and by["BUY-VPB-LAG-01"]["book_clearing"]["orig_qty"] == 1500
                                 and "SELL-VPB-PARK-01" not in by
                                 and xs[0]["removed_orders"][0]["id"] == "SELL-VPB-PARK-01"
                                 and by["BUY-FPT-LAG-01"]["qty"] == 300
                                 and "book_clearing" not in by["BUY-FPT-LAG-01"]
                                 and xs[0]["status"] == "PLANNED")
        r["A2_binding_selfconsistent"] = M["book_clearing"].binding_problems(p, xs[0]) == [] if xs else False
        first = strip_ts(p)
        rc, rep = cb_apply(M, sb)
        r["A3_rerun_idempotent"] = rc == 0 and strip_ts(sb.read_plan()) == first
        # A4 plan đã duyệt
        sb.write_plan(base_plan(approved="user"))
        raw = open(sb.plan_path(), "rb").read()
        rc, rep = cb_apply(M, sb)
        r["A4_approved_refused"] = rc == 2 and open(sb.plan_path(), "rb").read() == raw
        # A5 trượt cổng book đích
        sb.write_plan(base_plan())
        rc, rep = cb_apply(M, sb, gates=GATE_NO)
        p = sb.read_plan()
        r["A5_gate_fail_no_transfer"] = (rc == 0 and not p.get("book_transfers")
                                         and {o["id"]: o["qty"] for o in p["orders"]}["BUY-VPB-LAG-01"] == 1500
                                         and any("cổng book đích" in b["reason"] for b in rep["blocked"]))
        # A6 bán lẻ full-exit 286
        sb.write_plan(base_plan(park_sell=286))
        rc, rep = cb_apply(M, sb)
        p = sb.read_plan()
        by = {o["id"]: o for o in p["orders"]}
        r["A6_odd_full_exit_keeps_odd"] = (rc == 0 and (p.get("book_transfers") or [{}])[0].get("qty") == 200
                                           and by.get("SELL-VPB-PARK-01", {}).get("qty") == 86
                                           and by["BUY-VPB-LAG-01"]["qty"] == 1300)
    finally:
        sb.close()


def hypo_bal(M, on):
    """Test MÁY MÓC chuỗi 2 transfer (B16/M3/M4/E10/R2): GĐ3 phương án A đã bỏ BAL khỏi phạm vi, nên
    giả lập 'đích thứ 2' bằng cách tạm mở BAL trong bản module đang test. KHÔNG phải hành vi production
    (production: TO_BOOKS=('LAG',) — xem part_r3)."""
    BCm, CBm = M["book_clearing"], M["clear_books"]
    hypo_bal.active = bool(on)
    if on:
        hypo_bal.saved = (BCm.TO_BOOKS, BCm.SKIPPED_TO_BOOKS, CBm.TO_BOOKS)
        BCm.TO_BOOKS = CBm.TO_BOOKS = ("LAG", "BAL")
        BCm.SKIPPED_TO_BOOKS = {}
    else:
        BCm.TO_BOOKS, BCm.SKIPPED_TO_BOOKS, CBm.TO_BOOKS = hypo_bal.saved


def part_m(M, r):
    sb, rc, rep = cleared(M)
    try:
        p = sb.read_plan()
        l1 = {"decision": "TRIM", "reconcile_ok": True, "account_label": LABEL, "trim_proposed_vnd": 0,
              "orders": [{"ticker": "VPB", "side": "sell", "qty": 200, "ref_price": 23500.0,
                          "value_vnd": 200 * 23500, "book": "PARK", "play_type": "PARK_TRIM",
                          "sellable": 286}]}
        new, mrep = M["merge_park_orders"].merge_park_orders(p, l1, None, ex_map={})
        by = {o["id"]: o for o in new.get("orders") or []}
        sells = [o for o in new.get("orders") or [] if o["side"] == "sell" and o["ticker"] == "VPB"]
        r["M1_merge_reverts_clearing"] = (mrep["status"] == "OK" and not new.get("book_transfers")
                                          and sum(o["qty"] for o in sells) == 200
                                          and by.get("BUY-VPB-LAG-01", {}).get("qty") == 1500
                                          and "book_clearing" not in by.get("BUY-VPB-LAG-01", {})
                                          and mrep.get("clearing_reverted") == [XID])
        p2 = copy.deepcopy(p)
        p2["book_transfers"][0]["status"] = "APPLIED"
        new2, mrep2 = M["merge_park_orders"].merge_park_orders(p2, l1, None, ex_map={})
        r["M2_merge_refuses_applied"] = mrep2["status"] == "REFUSED" and new2 == p2
    finally:
        sb.close()


def _b(M, setup=None, **kw):
    sb, rc, rep = cleared(M)
    if setup:
        setup(sb)
    out = ab_run(M, sb, **kw)
    return sb, out


def _pre_approve(sb):
    """plan ĐÃ có approved_by nhưng cổng bot (approval_fn) vẫn chặn ⇒ không áp (phủ đường approval_fn
    độc lập với kiểm approved_by của clearing — mutant X6)."""
    p = sb.read_plan()
    p["approved_by"] = "user"
    sb.write_plan(p)


def part_b(M, r):
    AB = M["apply_book_transfers"]
    # B1 + B2 + B3 + B18
    sb, (rc, plan, log) = _b(M)
    try:
        h = sb.holdings(LABEL, PD)
        park = sum(l["qty"] for l in h["lots"] if l["ticker"] == "VPB" and l["book"] == "PARK")
        new_lag = [l for l in h["lots"] if l["ticker"] == "VPB" and l["book"] == "LAG"
                   and l.get("book_transfer")]
        tot = sum(l["qty"] for l in h["lots"] if l["ticker"] == "VPB")
        p = sb.read_plan()
        r["B1_applied_journal_ledger"] = (rc == 0 and n_xfer_rows(sb) == 1
                                          and p["book_transfers"][0]["status"] == "APPLIED"
                                          and park == 86 and sum(l["qty"] for l in new_lag) == 200
                                          and all(l["entry_date"] == PD for l in new_lag)
                                          and tot == 1786 and h["reconcile"]["ok"]
                                          and "VPB" not in h["unverified_tickers"]
                                          and {o["id"] for o in p["orders"]} == {"BUY-VPB-LAG-01", "BUY-FPT-LAG-01"})
        rc2, _, _ = ab_run(M, sb)
        r["B2_rerun_no_second_row"] = rc2 == 0 and n_xfer_rows(sb) == 1
        p = sb.read_plan()
        p["book_transfers"][0]["status"] = "PLANNED"      # kill sau journal, trước plan
        sb.write_plan(p)
        rc3, _, log3 = ab_run(M, sb)
        r["B3_kill_after_journal_resume"] = (rc3 == 0 and n_xfer_rows(sb) == 1
                                             and sb.read_plan()["book_transfers"][0]["status"] == "APPLIED"
                                             and len(sb.read_plan()["orders"]) == 2)
        # B4: lỗi bất ngờ ⇒ emergency đọc journal ⇒ APPLIED, không pause
        p = sb.read_plan()
        p["book_transfers"][0]["status"] = "PLANNED"
        sb.write_plan(p)
        AB.emergency_pause_all(sb.plan_path(), "giả lập", LABEL, PD, sb.ex)
        p = sb.read_plan()
        r["B4_emergency_respects_journal"] = (p["book_transfers"][0]["status"] == "APPLIED"
                                              and len(p["orders"]) == 2)
        # B18 đêm 2: plan 30/10 bán PARK 86 lẻ; sổ asof 29/10 thấy lô chuyển
        h2 = sb.holdings(LABEL, PD)
        lag_new = [l for l in h2["lots"] if l.get("book_transfer")]
        r["B18_next_night_ledger_sees_transfer"] = (sum(l["qty"] for l in lag_new) == 200
                                                    and all(l["book"] == "LAG" for l in lag_new))
    finally:
        sb.close()
    # B4b: emergency khi journal CHƯA có ⇒ PAUSE
    sb, rc, rep = cleared(M)
    try:
        AB.emergency_pause_all(sb.plan_path(), "giả lập", LABEL, PD, sb.ex)
        p = sb.read_plan()
        r["B4b_emergency_pauses_unwritten"] = (p["book_transfers"][0]["status"] == "PAUSED"
                                               and orders_qty(p) == ORIG_QTY)
    finally:
        sb.close()

    def paused(name, setup=None, rc_want=3, **kw):
        sb, (rc, plan, log) = _b(M, setup, **kw)
        try:
            p = sb.read_plan()
            ok = (rc == rc_want and n_xfer_rows(sb) == 0
                  and p["book_transfers"][0]["status"] == "PAUSED"
                  and orders_qty(p) == ORIG_QTY            # PAUSE = KHÔI PHỤC lệnh gốc (item 6)
                  and set(p["book_transfers"][0]["restored_orders"]) == {"SELL-VPB-PARK-01", "BUY-VPB-LAG-01"})
            r[name] = ok
        finally:
            sb.close()

    def low_sellable(sb):
        sb.broker["VPB"]["sellable"] = 150
    paused("B5_low_sellable_paused", low_sellable)

    def rights(sb):
        def post(h):
            for l in h["lots"]:
                if l["ticker"] == "VPB" and l["book"] == "PARK":
                    l["rights_subscription"] = {"event_id": "t"}
                    break
        sb.post = post
    paused("B6_rights_lot_paused", rights)

    def unsettled(sb):
        def post(h):
            for l in h["lots"]:
                if l["ticker"] == "VPB" and l["book"] == "PARK":
                    l["entry_date"] = "2026-10-28"
                    break
        sb.post = post
    paused("B7_park_not_T2_paused", unsettled)

    def edited(sb):
        p = sb.read_plan()
        for o in p["orders"]:
            if o["id"] == "BUY-VPB-LAG-01":
                o["qty"] = 1500
        sb.write_plan(p)
    sb, (rc, plan, log) = _b(M, edited)
    try:
        p = sb.read_plan()
        r["B8_plan_edited_after_clearing_paused"] = (rc == 3 and n_xfer_rows(sb) == 0
                                                     and p["book_transfers"][0]["status"] == "PAUSED"
                                                     and orders_qty(p) == ORIG_QTY)
    finally:
        sb.close()

    for name, kw, setup in (("B9_bot_gate_blocks_noop", {"approval": "cổng bot: chưa duyệt"}, _pre_approve),
                            ("B10_bot_stop_noop", {"approve": False}, lambda sb: open(os.path.join(sb.root, "BOT_STOP"), "w").close())):
        sb, rc0, rep0 = cleared(M)
        try:
            if setup:
                setup(sb)
            raw = open(sb.plan_path(), "rb").read()
            rc, _, _ = ab_run(M, sb, **kw)
            r[name] = rc == 0 and n_xfer_rows(sb) == 0 and open(sb.plan_path(), "rb").read() == raw
        finally:
            sb.close()

    def cross(sb):
        p = sb.read_plan()
        p["book_transfers"][0]["account"] = "OTHER"
        sb.write_plan(p)
    paused("B11_cross_account_paused", cross)

    def dup(sb):
        with open(os.path.join(sb.ex, f"exec_{LABEL}_2026-10-27_journal.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(HDR)
            w.writerow(["2026-10-27T09:00:00", "BOOK_TRANSFER", XID, "VPB", "transfer", XID, 100,
                        23500.0, 100, "LAG", "LAG_LO", "from=PARK;to=LAG;src=x"])
        sb.broker["VPB"]["qty"] = 1786
    sb, (rc, plan, log) = _b(M, dup)
    try:
        r["B12_dup_id_diff_content_paused"] = (rc == 3 and sb.read_plan()["book_transfers"][0]["status"] == "PAUSED"
                                               and n_xfer_rows(sb) == 0)
    finally:
        sb.close()

    paused("B13_banned_paused", None, banned=("VPB",))

    def legacy(sb):
        with open(os.path.join(sb.ex, f"exec_{LABEL}_{PD}_journal.csv"), "w", newline="") as f:
            csv.writer(f).writerow(HDR[:9] + ["note"])
    sb, rc, rep = cleared(M)
    try:
        legacy(sb)
        try:
            ab_run(M, sb)
            r["B14_legacy_header_refused"] = False
        except ValueError:
            r["B14_legacy_header_refused"] = n_xfer_rows(sb) == 0
    finally:
        sb.close()

    paused("B15_target_gate_fail_paused", None, gates=GATE_NO)

    hypo_bal(M, True)
    # B16 hai sổ đích hợp lệ lúc lập plan (PARK 300 → LAG 200 + BAL 100); sáng hôm sau sổ PARK chỉ
    # còn 250 ⇒ transfer LAG áp, transfer BAL (prefix CỘNG DỒN 300 > 250) phải PAUSE.
    sb = SB(boot=[("VPB", "PARK", 200, 22154, "2026-07-02"), ("VPB", "PARK", 100, 20556, "2026-08-11"),
                  ("FPT", "LAG", 500, 100000, "2026-09-15")])
    try:
        sb.broker["VPB"] = {"qty": 1800, "sellable": 1800}
        pl = base_plan(park_sell=300)
        pl["orders"][0]["merged_from"]["sellable_at_calc"] = 300
        pl["orders"][1]["qty"] = 200
        pl["orders"].append({"id": "BUY-VPB-BAL-01", "ticker": "VPB", "side": "buy", "qty": 100,
                             "book": "BAL", "play_type": "BAL", "ref_price": 23500.0, "priority": 3})
        sb.write_plan(pl)
        cb_apply(M, sb)
        n_planned = len(sb.read_plan().get("book_transfers") or [])
        chained = sb.read_plan()
        rv, _ = M["book_clearing"].revert_clearing(chained)
        r["M3_revert_chain_restores_orig"] = (n_planned == 2 and sorted((o["id"], o["qty"]) for o in rv["orders"]) == sorted(
            [("SELL-VPB-PARK-01", 300), ("BUY-VPB-LAG-01", 200), ("BUY-VPB-BAL-01", 100), ("BUY-FPT-LAG-01", 300)])
            and not any("book_clearing" in o for o in rv["orders"]))
        cp = copy.deepcopy(chained)
        cp["approved_by"] = "user"
        r["C4_preflight_ok_chained_transfers"] = pf_flags(cp, pf_block(mut=PF_MUT[0])) == "OK"

        def shrink(h):
            for l in h["lots"]:
                if l["ticker"] == "VPB" and l["book"] == "PARK" and l["entry_date"] == "2026-08-11":
                    l["qty"] = 50
        sb.post = shrink
        rc, _, log = ab_run(M, sb)
        st = [x["status"] for x in sb.read_plan()["book_transfers"]]
        pq = orders_qty(sb.read_plan())
        r["B16_two_targets_cumulative_prefix"] = (n_planned == 2 and rc == 3
                                                  and st == ["APPLIED", "PAUSED"] and n_xfer_rows(sb) == 1
                                                  # PAUSE chỉ trả phần của transfer BAL: bán PARK 300−200(LAG đã áp)=100, mua BAL 100
                                                  and pq.get("SELL-VPB-PARK-01") == 100 and pq.get("BUY-VPB-BAL-01") == 100
                                                  and "BUY-VPB-LAG-01" not in pq)
    finally:
        sb.close()

    # M4 lệnh bán PARK bị 2 transfer giảm nối tiếp mà vẫn > 0 (300 → 200 → 100) ⇒ hoàn tác về 300
    sb = SB(boot=[("VPB", "PARK", 200, 22154, "2026-07-02"), ("VPB", "PARK", 100, 20556, "2026-08-11"),
                  ("FPT", "LAG", 500, 100000, "2026-09-15")])
    try:
        sb.broker["VPB"] = {"qty": 1800, "sellable": 1800}
        pl = base_plan(park_sell=300)
        pl["orders"][0]["merged_from"]["sellable_at_calc"] = 300
        pl["orders"][1]["qty"] = 100
        pl["orders"].append({"id": "BUY-VPB-BAL-01", "ticker": "VPB", "side": "buy", "qty": 100,
                             "book": "BAL", "play_type": "BAL", "ref_price": 23500.0, "priority": 3})
        sb.write_plan(pl)
        cb_apply(M, sb)
        p = sb.read_plan()
        sell = {o["id"]: o for o in p["orders"]}.get("SELL-VPB-PARK-01", {})
        rv, _ = M["book_clearing"].revert_clearing(p)
        r["M4_double_reduced_order_reverts_to_orig"] = (
            len(p.get("book_transfers") or []) == 2 and sell.get("qty") == 100
            and {o["id"]: o["qty"] for o in rv["orders"]}["SELL-VPB-PARK-01"] == 300)
    finally:
        sb.close()

    hypo_bal(M, False)

    # B17 main(): plan không có transfer ⇒ rc0 (tầng stdlib)
    sb = SB()
    try:
        sb.write_plan(base_plan())
        rc = AB.main(["--account", LABEL, "--date", PD, "--plan-dir", sb.pl, "--exec-dir", sb.ex])
        r["B17_main_no_transfers_rc0"] = rc == 0 and n_xfer_rows(sb) == 0
    finally:
        sb.close()


# ───────────────────────────────────────────── C preflight (khối python THẬT trong bash)

def pf_block(src_path=None, mut=None):
    src_path = src_path or os.path.join(HERE, "preflight_check.sh")
    src = open(src_path, encoding="utf-8").read()
    m = re.search(r'PLAN_INFO=\$\(python3 - "\$PLAN_FILE".*?<<\'PY\'\n(.*?)\nPY\n', src, re.S)
    blk = m.group(1)
    if mut:
        assert blk.count(mut[0]) == 1, f"mutant preflight không khớp: {mut[0][:50]}"
        blk = blk.replace(*mut)
    return blk


def pf_flags(plan, blk):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(plan, f)
    try:
        out = subprocess.run([sys.executable, "-", f.name], input=blk, capture_output=True, text=True)
        return out.stdout.strip().split("|", 7)[-1] if out.stdout.strip() else "CRASH:" + out.stderr[-200:]
    finally:
        os.unlink(f.name)


PF_MUT = [None]   # mutant preflight đang chạy (C4 nằm trong part_b dùng chung)


def part_c(M, r, pf_mut=None):
    blk = pf_block(mut=pf_mut)
    sb, rc, rep = cleared(M)
    try:
        p = sb.read_plan()
        p["approved_by"] = "user"
        r["C1_preflight_ok_after_clearing"] = pf_flags(p, blk) == "OK"
        q = copy.deepcopy(p)
        for o in q["orders"]:
            if o["id"] == "BUY-VPB-LAG-01":
                o["qty"] = 1500
        r["C2_preflight_mismatch"] = "BOOK_XFER_MISMATCH" in pf_flags(q, blk)
        q = copy.deepcopy(p)
        q["book_transfers"][0]["qty"] = 200
        q["orders"].append({"id": "SELL-VPB-LAG-09", "ticker": "VPB", "side": "sell", "qty": 100,
                            "book": "LAG", "ref_price": 23500.0})
        r["C3_preflight_sell_plus_transfer_gt_cap"] = "SELL_GT_SELLABLE:VPB(300>286)" in pf_flags(q, blk)
    finally:
        sb.close()


# ───────────────────────────────────────────── D send_plan_report (chạy script THẬT, --dry-run)

def part_d(r):
    real = os.path.join(WC, "data", "trade_plans", "plan_SpaceX_2026-08-07.json")
    if not os.path.exists(real):
        r["D_send_plan_report_skipped_no_fixture"] = False
        return
    plan = json.load(open(real, encoding="utf-8"))
    plan.pop("auto_exit_inject_notes", None)
    x = {"id": "XFER-SpaceX-x-VPB-PARK-LAG", "ticker": "VPB", "from_book": "PARK", "to_book": "LAG",
         "qty": 200, "ref_price": 23500.0, "status": "PLANNED", "saving_est_vnd": 18610,
         "buy_orders": [{"id": "BUY-VPB-LAG-01", "orig_qty": 1500, "qty_after": 1300}],
         "sell_orders": [{"id": "SELL-VPB-PARK-01", "orig_qty": 200, "qty_after": 0}]}
    outs = []
    for bx in ([x], [{"ticker": "VPB", "qty": "rác", "buy_orders": "x"}]):
        td = tempfile.mkdtemp()
        try:
            for sub in ("data/trade_plans", "state"):
                os.makedirs(os.path.join(td, sub), exist_ok=True)
            os.symlink(os.path.join(WC, "trading_bot"), os.path.join(td, "trading_bot"))
            env = dict(os.environ, SEND_PLAN_WORKDIR_OVERRIDE=td,
                       SEND_PLAN_MARKER_DIR=os.path.join(td, "state", "marker"))
            exp = subprocess.run(
                [sys.executable, "-c", "import datetime as dt; from zoneinfo import ZoneInfo; "
                 "from trading_bot.vn_market import next_trading_day; "
                 "print(next_trading_day(dt.datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).date()))"],
                cwd=WC, capture_output=True, text=True, env=env).stdout.strip()
            pp = dict(plan, plan_date=exp, book_transfers=bx)
            json.dump(pp, open(os.path.join(td, "data", "trade_plans", f"plan_SpaceX_{exp}.json"), "w"),
                      ensure_ascii=False)
            rr = subprocess.run(["bash", os.path.join(HERE, "send_plan_report.sh"), "--account", "SpaceX",
                                 "--dry-run"], capture_output=True, text=True, env=env, timeout=600)
            outs.append((rr.returncode, rr.stdout + rr.stderr))
        finally:
            shutil.rmtree(td, ignore_errors=True)
    o1, o2 = outs[0][1], outs[1][1]
    r["D1_report_shows_transfer"] = ("Chuyển nhãn sổ 1 mã" in o1 and "VPB 200cp PARK→LAG" in o1
                                     and "BUY-VPB-LAG-01 1,500→1,300cp" in o1 and "18,610đ" in o1)
    r["D2_broken_entry_warns_not_crash"] = "Không render được khối book_transfers" in o2 and outs[1][0] == outs[0][0]


# ───────────────────────────────────────────── R vòng 2 (arch-review + quant-skeptic 05/11)

def real_approval_fn():
    """approval_block_reason THẬT của bot (không stub) trên TradePlan dựng từ plan dict."""
    import dataclasses
    if WC not in sys.path:
        sys.path.insert(0, WC)
    from trading_bot import plan as TP
    kp = {f.name for f in dataclasses.fields(TP.TradePlan)}

    def fn(plan):
        tp = TP.TradePlan(**{k: v for k, v in plan.items() if k in kp and k != "orders"}, orders=[])
        tp.orders = []     # đúng ca lỗi: orders rỗng sau clearing
        return TP.approval_block_reason(tp)
    return fn


def plan_only_pair():
    """plan chỉ có cặp PARK bán 200 + LAG mua 200 ⇒ clearing làm orders=[]."""
    pl = base_plan(200)
    pl["orders"] = [pl["orders"][0], dict(pl["orders"][1], qty=200)]
    return pl


def holds_env(matcher, dd=True):
    """Vá trading_bot.plan: signal_holds matcher + 3 cổng đọc nguồn sống → identity (tất định)."""
    if WC not in sys.path:
        sys.path.insert(0, WC)
    from trading_bot import plan as TP
    names = ("_signal_holds_matcher", "filter_dd_flag_orders", "filter_lag_rating_orders",
             "filter_lag_governance_orders")
    saved = {n: getattr(TP, n) for n in names}
    TP._signal_holds_matcher = (lambda: matcher)
    for n in names[1:]:
        setattr(TP, n, lambda t, asof=None: (t, []))
    return TP, saved


def bot_filter_names():
    import ast
    src = open(os.path.join(WC, "bot_execute.py"), encoding="utf-8").read()
    out = set()
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id.startswith("filter_"):
            out.add(n.func.id)
    return out


def _sh_sandbox(mut=None):
    """Cây giả S/{bot_execute.py, wc_env.sh, data/trade_plans, mike/bin/{run_bot.sh, book_transfers_gate.sh,
    bot_heartbeat.sh(copy), stubs}} — chạy run_bot.sh/_restart_bot THẬT (mutant: (file, old, new))."""
    root = tempfile.mkdtemp(prefix="g3sh_")
    bn = os.path.join(root, "mike", "bin")
    os.makedirs(bn)
    os.makedirs(os.path.join(root, "data", "trade_plans"))
    os.makedirs(os.path.join(root, "mike", "logs"))
    open(os.path.join(root, "wc_env.sh"), "w").write("export TZ=Asia/Ho_Chi_Minh\n")
    for fn in ("run_bot.sh", "book_transfers_gate.sh", "bot_heartbeat.sh"):
        src = open(os.path.join(HERE, fn), encoding="utf-8").read()
        if mut and mut[0] == fn:
            assert src.count(mut[1]) == 1, f"mutant {mut[:2]} không khớp đúng 1 chỗ"
            src = src.replace(mut[1], mut[2])
        open(os.path.join(bn, fn), "w").write(src)
    open(os.path.join(bn, "apply_book_transfers.py"), "w").write(
        "import os, sys\nprint('stub apply')\nrc = int(os.environ.get('STUB_APPLY_RC', '0'))\n"
        "if rc == 3:\n    print('⛔ XFER-x: PAUSE (khôi phục lệnh gốc) — LY-DO-THAT-123')\nsys.exit(rc)\n")
    for fn in ("notify_thread.sh", "append_event.sh", "ops_autofix.sh"):   # in ra STDOUT như bản thật (append_event: "appended ...")
        open(os.path.join(bn, fn), "w").write(f'#!/bin/bash\necho "{fn} $*" >> "{root}/calls.log"\necho "STDOUT-LEAK-{fn}"\n')
        os.chmod(os.path.join(bn, fn), 0o755)
    open(os.path.join(root, "bot_execute.py"), "w").write(
        f"import sys\nprint('BOT-LINE')\nopen({root!r} + '/bot_ran.txt', 'a').write(' '.join(sys.argv[1:]) + '\\n')\n")
    return root


def _sh_plan(root, transfers):
    p = {"orders": [{"id": "A", "qty": 100}]}
    if transfers is not None:
        p["book_transfers"] = transfers
    json.dump(p, open(os.path.join(root, "data", "trade_plans", f"plan_ACC_{PD}.json"), "w"))


def _ran(root):
    return os.path.exists(os.path.join(root, "bot_ran.txt"))


def part_sh(r, mut=None):
    """Ngữ nghĩa rc của run_bot.sh + autoheal (_restart_bot) — item 4/5."""
    import time
    X = lambda st: {"id": "x" + st, "status": st}
    cases = [  # (tên, rc apply, transfers, bot_chạy_run_bot, rc_run_bot)
        ("rc0_pending", 0, [X("PLANNED")], True, 0),
        ("rc3_paused", 3, [X("PAUSED")], True, 0),
        ("rc2_pending_closed", 2, [X("PLANNED")], False, 2),
        ("rc2_mixed_closed", 2, [X("APPLIED"), X("PLANNED")], False, 2),
        ("rc1_pending_closed", 1, [X("PLANNED")], False, 1),
        ("rc2_no_transfers_flag_off_runs", 2, None, True, 0),
        ("rc1_import_err_empty_list_runs", 1, [], True, 0),
        ("rc2_all_applied_runs", 2, [X("APPLIED"), X("PAUSED")], True, 0),
        ("rc2_status_missing_closed", 2, [{"id": "x"}], False, 2),
        ("rc2_status_none_closed", 2, [{"id": "x", "status": None}], False, 2),
        ("rc2_transfers_not_list_closed", 2, "garbage", False, 2),
    ]
    for name, arc, xfers, bot_runs, want_rc in cases:
        root = _sh_sandbox(mut)
        try:
            _sh_plan(root, xfers)
            env = dict(os.environ, STUB_APPLY_RC=str(arc), TZ="Asia/Ho_Chi_Minh")
            cp = subprocess.run(["bash", os.path.join(root, "mike", "bin", "run_bot.sh"), "--account", "ACC",
                                 "--date", PD], capture_output=True, text=True, env=env, timeout=60)
            r[f"SH_run_bot_{name}"] = _ran(root) == bot_runs and cp.returncode == want_rc
            if arc == 3:   # thông báo PAUSE phải mang LÝ DO THẬT (đuôi dòng PAUSE của apply), không phải đường dẫn log
                calls = open(os.path.join(root, "calls.log")).read()
                notif = [ln for ln in calls.splitlines() if ln.startswith("notify_thread.sh") and "TẠM DỪNG" in ln]
                r["SH_run_bot_rc3_notice_has_real_reason"] = bool(notif) and "LY-DO-THAT-123" in notif[0]
            if xfers is None and arc == 2:   # cảnh báo + bus, không im lặng
                calls = open(os.path.join(root, "calls.log")).read()
                r["SH_run_bot_warn_when_apply_fails_no_transfers"] = "book-transfer-apply-warn" in calls
        finally:
            shutil.rmtree(root, ignore_errors=True)
    # autoheal: trích hàm _restart_bot THẬT từ bot_heartbeat.sh (bản trong sandbox, có thể là mutant)
    for name, arc, xfers, bot_runs in (("hb_rc2_pending_no_restart", 2, [X("PLANNED")], False),
                                       ("hb_rc3_paused_restarts", 3, [X("PAUSED")], True),
                                       ("hb_rc0_restarts", 0, [X("PLANNED")], True),
                                       ("hb_rc2_no_transfers_restarts", 2, None, True)):
        root = _sh_sandbox(mut)
        try:
            _sh_plan(root, xfers)
            hb = open(os.path.join(root, "mike", "bin", "bot_heartbeat.sh"), encoding="utf-8").read()
            m = re.search(r"^_restart_bot\(\) \{\n.*?\n\}\n", hb, re.S | re.M)
            # như bot_heartbeat.sh:218 — NEWPID="$(_restart_bot)" HỨNG stdout ⇒ không được có byte lạ
            script = (f'set -uo pipefail; ROOT={root}/mike; WC_ROOT={root}; ACCOUNT=ACC; PLAN_DATE={PD}\n'
                      f'sleep() {{ :; }}\n{m.group(0)}\nNEWPID="$(_restart_bot)"; printf "CAPTURED=[%s]" "$NEWPID"')
            cp = subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=60,
                                env=dict(os.environ, STUB_APPLY_RC=str(arc), TZ="Asia/Ho_Chi_Minh"))
            cap = re.search(r"CAPTURED=\[(.*)\]", cp.stdout, re.S)
            cap = cap.group(1) if cap else "<no capture>"
            # fail-closed ⇒ RỖNG; ok ⇒ rỗng hoặc chỉ PID (chữ số)
            r[f"SH_{name}_stdout_clean"] = (cap == "" if not bot_runs else re.fullmatch(r"\d*", cap.strip()) is not None)
            t_end = time.time() + 4
            while bot_runs and not _ran(root) and time.time() < t_end:
                time.sleep(0.1)
            if not bot_runs:
                time.sleep(0.5)
            r[f"SH_{name}"] = _ran(root) == bot_runs
            if bot_runs:   # log autoheal giữ cả output apply lẫn bot (>> chứ không >)
                import glob
                lg = glob.glob(os.path.join(root, "mike", "logs", "run_bot_ACC_autoheal_*.log"))
                txt = open(lg[0], encoding="utf-8").read() if lg else ""
                t_end = time.time() + 3
                while "BOT-LINE" not in txt and lg and time.time() < t_end:
                    time.sleep(0.1)
                    txt = open(lg[0], encoding="utf-8").read()
                r[f"SH_{name}_log_keeps_apply_output"] = "stub apply" in txt and "BOT-LINE" in txt
        finally:
            shutil.rmtree(root, ignore_errors=True)


def part_r3(M, r):
    """Vòng 3 (user chọn phương án A, 05/11): chỉ PARK→LAG · approval chuỗi · corp-action timeout · jidx=None."""
    import time
    BCm, AB = M["book_clearing"], M["apply_book_transfers"]

    # ── T1 BAL không bao giờ là đích ────────────────────────────────────────────────────
    def bal_plan():
        pl = base_plan(200)
        pl["orders"][1].update(qty=200, book="BAL", play_type="BAL", id="BUY-VPB-BAL-01", ref_price=23500.0)
        return pl
    r["T1a_to_books_is_lag_only"] = tuple(BCm.TO_BOOKS) == ("LAG",) and BCm.SKIPPED_TO_BOOKS.get("BAL") == "bal_stoploss_basis"
    sb = SB()
    try:
        sb.write_plan(bal_plan())
        rc, rep = cb_apply(M, sb)
        r["T1b_clear_books_skips_bal_with_reason"] = (
            rc == 0 and unchanged(sb, bal_plan()) and not rep["opportunities"]
            and any(b.get("to_book") == "BAL" and b["reason"] == "bal_stoploss_basis" for b in rep["blocked"]))
    finally:
        sb.close()
    # lớp 2: apply_opportunities từ chối đích BAL dù caller đưa vào
    sb = SB()
    try:
        sb.write_plan(bal_plan())
        pl = sb.read_plan()
        _, xs, sk = BCm.apply_opportunities(pl, [{
            "ticker": "VPB", "to_book": "BAL", "transfer_qty": 200, "buy_order_ids": ["BUY-VPB-BAL-01"],
            "park_sell_order_ids": ["SELL-VPB-PARK-01"], "ref_price_buy": 23500.0}], LABEL, PD, "t")
        r["T1c_apply_opportunities_refuses_bal"] = (not xs and len(sk) == 1 and sk[0]["reason"] == "bal_stoploss_basis")
    finally:
        sb.close()
    # lớp 3: plan có transfer đích BAL (viết tay/phiên bản cũ) ⇒ apply_book_transfers PAUSE + KHÔI PHỤC, không ghi journal
    hypo_bal(M, True)
    sb = SB()
    try:
        sb.write_plan(bal_plan())
        cb_apply(M, sb)
        built = len(sb.read_plan().get("book_transfers") or []) == 1
    finally:
        hypo_bal(M, False)
    try:
        rc, _, log = ab_run(M, sb)
        pl = sb.read_plan()
        r["T1d_apply_never_transfers_to_bal"] = (built and rc == 3 and n_xfer_rows(sb) == 0
                                                 and pl["book_transfers"][0]["status"] == "PAUSED"
                                                 and orders_qty(pl).get("SELL-VPB-PARK-01") == 200
                                                 and orders_qty(pl).get("BUY-VPB-BAL-01") == 200)
    finally:
        sb.close()

    # ── T2 approval: chuỗi 'None'/'null' + orders=[] ; requires_user_approval='true' ────────
    r["T2a_approval_problem_units"] = (
        BCm.approval_problem({"requires_user_approval": True, "approved_by": "None"})
        and BCm.approval_problem({"requires_user_approval": True, "approved_by": "null"})
        and BCm.approval_problem({"requires_user_approval": "true", "approved_by": None})
        and BCm.approval_problem({"requires_user_approval": "True"})
        and BCm.approval_problem({"requires_user_approval": True, "approved_by": "  "})
        and BCm.approval_problem({"requires_user_approval": "false", "approved_by": None}) is None
        and BCm.approval_problem({"requires_user_approval": True, "approved_by": "user"}) is None)
    fn = real_approval_fn()
    for tag, edit, applied in (("approved_by_None_str", {"approved_by": "None"}, False),
                               ("approved_by_null_str", {"approved_by": "null"}, False),
                               ("requires_true_str_unapproved", {"requires_user_approval": "true", "approved_by": None}, False),
                               ("requires_true_str_approved", {"requires_user_approval": "true", "approved_by": "user"}, True)):
        sb = SB()
        try:
            sb.write_plan(plan_only_pair())
            cb_apply(M, sb)
            pl = sb.read_plan()
            pl.update(edit)
            sb.write_plan(pl)
            raw = open(sb.plan_path(), "rb").read()
            rc, _, _ = ab_run(M, sb, approve=False, approval_fn=fn)
            ok = (rc == 0 and (n_xfer_rows(sb) == 1) == applied
                  and (applied or open(sb.plan_path(), "rb").read() == raw))
            r[f"T2b_empty_orders_{tag}_{'applied' if applied else 'not_applied'}"] = ok
        finally:
            sb.close()

    # ── T3 corp-action: BQ chậm ⇒ chặn trong ≤ trần, không treo ─────────────────────────
    slow = (lambda tickers, since=None, until=None, codes=None: (time.sleep(4), [])[1])
    t0 = time.time()
    why = BCm.corp_action_problem("VPB", ASOF, PD, slow, timeout_s=0.3)
    r["T3a_corp_action_timeout_blocks"] = bool(why) and "quá" in why and time.time() - t0 < 2.0
    r["T3b_corp_action_timeout_default_le_30"] = 0 < BCm.CORP_ACTION_TIMEOUT_S <= 30
    saved_to = BCm.CORP_ACTION_TIMEOUT_S
    BCm.CORP_ACTION_TIMEOUT_S = 0.3
    sb, rc0, _ = cleared(M)
    try:
        t0 = time.time()
        rc, _, log = ab_run(M, sb, events=slow)
        pl = sb.read_plan()
        r["T3c_apply_slow_bq_pauses_and_restores"] = (
            rc == 3 and time.time() - t0 < 2.5 and n_xfer_rows(sb) == 0
            and pl["book_transfers"][0]["status"] == "PAUSED"
            and orders_qty(pl) == {k: v for k, v in ORIG_QTY.items()})
        import fcntl   # flock đã nhả sau khi chạy xong
        fd = os.open(os.path.join(sb.pl, f".apply_book_transfers_{LABEL}.lock"), os.O_WRONLY | os.O_CREAT, 0o644)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            r["T3d_flock_released_after_timeout"] = True
        except OSError:
            r["T3d_flock_released_after_timeout"] = False
        finally:
            os.close(fd)
    finally:
        BCm.CORP_ACTION_TIMEOUT_S = saved_to
        sb.close()

    # ── T4 emergency_pause_all khi journal đọc không được SAU khi dòng đã ghi: không ghi đôi journal ──
    sb, _, _ = cleared(M)
    try:
        pre = sb.read_plan()
        pre["approved_by"] = "user"
        sb.write_plan(pre)
        pre_raw = open(sb.plan_path(), "rb").read()
        rc, _, _ = ab_run(M, sb)
        wrote = rc == 0 and n_xfer_rows(sb) == 1
        open(sb.plan_path(), "wb").write(pre_raw)       # giả lập chết sau journal, trước khi lưu plan
        saved_ji = AB.journal_index
        AB.journal_index = lambda *a, **k: (_ for _ in ()).throw(OSError("journal unreadable"))
        try:
            AB._late_imports()
            AB.emergency_pause_all(sb.plan_path(), "boom", LABEL, PD, sb.ex)
        finally:
            AB.journal_index = saved_ji
        st = sb.read_plan()["book_transfers"][0]["status"]
        rc2, _, _ = ab_run(M, sb)
        r["T4_jidx_none_no_double_journal_row"] = (wrote and st == "PAUSED" and rc2 in (0, 3) and n_xfer_rows(sb) == 1)
    finally:
        sb.close()


def unchanged(sb, base):
    """plan trên đĩa không có book_transfers và orders y hệt `base` (clear_books luôn ghi lại marker
    `book_clearing` cấp plan khi APPLY nên so ngữ nghĩa, không so byte)."""
    p = sb.read_plan()
    key = lambda pl: sorted((o["id"], o["qty"]) for o in pl["orders"])
    return not p.get("book_transfers") and key(p) == key(base)


def part_r2(M, r):
    BCm, AB = M["book_clearing"], M["apply_book_transfers"]
    # ── R1 (item 1) approval THẬT + orders=[] ───────────────────────────────────────────
    sb = SB()
    try:
        sb.write_plan(plan_only_pair())
        rc, rep = cb_apply(M, sb)
        p = sb.read_plan()
        raw = open(sb.plan_path(), "rb").read()
        fn = real_approval_fn()
        hole = fn(p)      # cổng của bot im lặng khi orders=[] — đây chính là lỗ
        rcu, _, logu = ab_run(M, sb, approve=False, approval_fn=fn)
        r["R1_unapproved_empty_orders_not_applied"] = (
            rc == 0 and p["orders"] == [] and p["book_transfers"][0]["status"] == "PLANNED" and hole is None
            and rcu == 0 and n_xfer_rows(sb) == 0 and open(sb.plan_path(), "rb").read() == raw)
        rca, _, _ = ab_run(M, sb, approve=True, approval_fn=fn)
        r["R1b_approved_empty_orders_applied"] = (rca == 0 and n_xfer_rows(sb) == 1
                                                  and sb.read_plan()["book_transfers"][0]["status"] == "APPLIED")
    finally:
        sb.close()
    # R1c preflight (khối python THẬT): orders=[] + transfer PLANNED + chưa duyệt ⇒ NOT_APPROVED
    sb = SB()
    try:
        sb.write_plan(plan_only_pair())
        cb_apply(M, sb)
        p = sb.read_plan()
        blk = pf_block(mut=PF_MUT[0])
        r["R1c_preflight_not_approved_when_empty_orders_with_transfer"] = "NOT_APPROVED" in pf_flags(p, blk)
        p["approved_by"] = "user"
        r["R1d_preflight_ok_when_approved"] = pf_flags(p, blk) == "OK"
        q = {"orders": [], "requires_user_approval": True}
        r["R1e_preflight_hold_plan_still_ok"] = "NOT_APPROVED" not in pf_flags(q, blk)
    finally:
        sb.close()

    hypo_bal(M, True)
    # ── R2 (item 2) signal_holds + FAIL_OPEN + parity + tích hợp ─────────────────────────
    def bal_plan():
        pl = base_plan(200)
        pl["orders"][1].update(qty=200, book="BAL", play_type="BAL", id="BUY-VPB-BAL-01")
        pl["orders"][1]["ref_price"] = 23500.0
        return pl

    def run_gate(matcher):
        sb = SB()
        TP, saved = holds_env(matcher)
        try:
            sb.write_plan(bal_plan())
            rc, rep = cb_apply(M, sb, gates=BCm.target_book_gates)
            return rc, rep, unchanged(sb, bal_plan()), sb.read_plan()
        finally:
            for n, f in saved.items():
                setattr(TP, n, f)
            sb.close()
    hold = (lambda tk, side, book, asof=None, plan_date=None:
            {"scope": "book", "value": "BAL", "until": "2026-12-31", "reason": "tạm giữ BAL"}
            if (side == "buy" and book == "BAL") else None)
    rc0, rep0, same0, p0 = run_gate(lambda *a, **k: None)
    r["R2a_baseline_no_hold_clears_bal_buy_fully"] = (
        rc0 == 0 and len(p0.get("book_transfers") or []) == 1
        and p0["book_transfers"][0]["buy_orders"][0]["qty_after"] == 0)
    rc1, rep1, same1, p1 = run_gate(hold)
    r["R2b_bal_hold_blocks_transfer"] = (rc1 == 0 and not p1.get("book_transfers") and same1
                                         and any("BAL" in b.get("reason", "") and "signal_holds" in b.get("reason", "")
                                                 for b in rep1["blocked"]))
    rc2, rep2, same2, p2 = run_gate(None)     # module không nạp được ⇒ FAIL_OPEN ⇒ CHẶN
    r["R2c_fail_open_holds_blocks_transfer"] = (rc2 == 0 and not p2.get("book_transfers") and same2
                                                and any("FAIL_OPEN" in b.get("reason", "") for b in rep2["blocked"]))
    bot_set = bot_filter_names()
    r["R2d_ast_parity_gates_vs_bot_execute"] = bot_set == set(BCm.GATE_STEPS) and len(bot_set) == 5
    if not r["R2d_ast_parity_gates_vs_bot_execute"] and not QUIET[0]:
        print(f"      bot_execute filter_*={sorted(bot_set)} vs GATE_STEPS={sorted(BCm.GATE_STEPS)}")
    # tích hợp: cổng THẬT (không vá), mã excluded ⇒ chặn ở bước 1; mã thường ⇒ đi hết chuỗi thật
    sbi = SB()
    try:
        sbi.write_plan(bal_plan())
        pl = sbi.read_plan()
        trial, xs, _ = BCm.apply_opportunities(pl, [{
            "ticker": "VPB", "to_book": "BAL", "transfer_qty": 200, "buy_order_ids": ["BUY-VPB-BAL-01"],
            "park_sell_order_ids": ["SELL-VPB-PARK-01"], "ref_price_buy": 23500.0}], LABEL, PD, "t")
        ok_ex, why_ex = BCm.target_book_gates(trial, xs[0], {"VPB"})
        ok_r, why_r = BCm.target_book_gates(trial, xs[0], set())
        r["R2e_integration_real_gates"] = (ok_ex is False and "filter_excluded_tickers" in why_ex
                                           and isinstance(ok_r, bool)
                                           and (ok_r or any(n in why_r for n in BCm.GATE_STEPS)))
    finally:
        sbi.close()

    hypo_bal(M, False)

    # ── R3 (item 3) corp-action trong (asof, plan_date] ─────────────────────────────────
    calls = []
    ev_hit = (lambda tickers, since=None, until=None, codes=None:
              (calls.append((tuple(tickers), since, until)) or
               [{"ticker": "VPB", "event_code": "DIV", "exright_date": PD}]))
    ev_boom = (lambda tickers, since=None, until=None, codes=None: (_ for _ in ()).throw(RuntimeError("bq down")))
    sb = SB()
    try:
        sb.write_plan(base_plan(200))
        rc, rep = cb_apply(M, sb, events=ev_hit)
        r["R3a_clear_books_blocks_ex_date_in_window"] = (
            rc == 0 and unchanged(sb, base_plan(200))
            and any("corp-action" in b.get("reason", "") for b in rep["blocked"])
            and calls and calls[0] == (("VPB",), ASOF, PD))
        rc, rep = cb_apply(M, sb, events=ev_boom)
        r["R3b_clear_books_fail_closed_on_source_error"] = (
            rc == 0 and unchanged(sb, base_plan(200))
            and any("corp-action" in b.get("reason", "") for b in rep["blocked"]))
    finally:
        sb.close()
    for nm, ev in (("R3c_apply_pauses_on_ex_date", ev_hit), ("R3d_apply_pauses_on_source_error", ev_boom)):
        sb, rc0_, rep0_ = cleared(M)
        try:
            rc, _, log = ab_run(M, sb, events=ev)
            p = sb.read_plan()
            r[nm] = (rc == 3 and n_xfer_rows(sb) == 0 and p["book_transfers"][0]["status"] == "PAUSED"
                     and orders_qty(p) == ORIG_QTY and any("corp-action" in l for l in log))
        finally:
            sb.close()

    # ── R5 (item 7) 9 mutant sống: ca còn thiếu của apply_book_transfers ────────────────
    def bpaused(name, setup=None, **kw):
        sb, (rc, plan, log) = _b(M, setup, **kw)
        try:
            p = sb.read_plan()
            r[name] = (rc == 3 and n_xfer_rows(sb) == 0 and p["book_transfers"][0]["status"] == "PAUSED"
                       and orders_qty(p) == ORIG_QTY)
        finally:
            sb.close()

    def post_set(key, val):
        def setup(sb):
            sb.post = (lambda h: h.__setitem__(key, val))
        return setup
    bpaused("E1_excluded_ticker_paused", post_set("excluded_tickers", ["VPB"]))
    bpaused("E2_unverified_ticker_paused", post_set("unverified_tickers", ["VPB"]))
    bpaused("E3_broker_reconcile_mismatch_paused",
            post_set("reconcile", {"ok": False, "mismatches": [{"ticker": "VPB", "diff": 5}]}))

    def no_sellable(sb):
        sb.broker["VPB"]["sellable"] = None
    bpaused("E4_broker_sellable_missing_paused", no_sellable)
    bpaused("E5_today_ne_plan_date_paused", None, now="2026-10-30T09:01:00")
    # E6 journal có dòng cuối dở dang (không \n) ⇒ từ chối ghi (không dính dòng)
    sb, rc_, rep_ = cleared(M)
    try:
        jp = os.path.join(sb.ex, f"exec_{LABEL}_{PD}_journal.csv")
        with open(jp, "w", newline="") as f:
            f.write(",".join(HDR) + "\r\n2026-10-29T09:00:00,FILL,B9,ZZZ,buy,c9,100,23000,100,LAG,LAG_LO")
        before = open(jp, "rb").read()
        try:
            ab_run(M, sb)
            r["E6_partial_last_journal_line_refused"] = False
        except ValueError:
            r["E6_partial_last_journal_line_refused"] = open(jp, "rb").read() == before
    finally:
        sb.close()

    # ── clear_books: excluded / prefix T+2 / trần bán ───────────────────────────────────
    for nm, setup in (("E7_clear_books_excluded_blocked", post_set("excluded_tickers", ["VPB"])),):
        sb = SB()
        try:
            sb.write_plan(base_plan(200))
            setup(sb)
            rc, rep = cb_apply(M, sb)
            r[nm] = (rc == 0 and unchanged(sb, base_plan(200))
                     and any("excluded" in b.get("reason", "") for b in rep["blocked"]))
        finally:
            sb.close()
    sb = SB()
    try:
        sb.write_plan(base_plan(200))

        def unsettled_first(h):
            for l in h["lots"]:
                if l["ticker"] == "VPB" and l["book"] == "PARK":
                    l["entry_date"] = "2026-10-28"
                    break
        sb.post = unsettled_first
        rc, rep = cb_apply(M, sb)
        r["E8_clear_books_park_prefix_not_T2_blocked"] = (rc == 0 and unchanged(sb, base_plan(200))
                                                          and not rep["opportunities"])
    finally:
        sb.close()
    sb = SB()
    try:
        pl = base_plan(200)
        pl["orders"].append({"id": "SELL-VPB-LAG-09", "ticker": "VPB", "side": "sell", "qty": 100,
                             "book": "LAG", "ref_price": 23500.0, "priority": 2})
        sb.write_plan(pl)       # trần 286 chỉ nằm trên lệnh bán PARK (bị gỡ sau clearing): 100 + 200(chuyển) = 300 > 250
        pl["orders"][0]["merged_from"]["sellable_at_calc"] = 250
        sb.write_plan(pl)
        raw = open(sb.plan_path(), "rb").read()
        rc, rep = cb_apply(M, sb)
        r["E9_sell_cap_uses_removed_order_cap"] = (rc == 2 and open(sb.plan_path(), "rb").read() == raw
                                                   and "sellable" in str(rep.get("error")))
    finally:
        sb.close()

    # ── item 6 PAUSE khôi phục: chuỗi 2 transfer, pause transfer ĐẦU (còn lại giữ phần của nó) ──
    # (B5/B7/B8/B16 đã phủ 1 transfer + chuỗi PAUSE sau; ở đây PAUSE trước, sau còn PLANNED)
    hypo_bal(M, True)
    pl = base_plan(300)
    sbx = SB(boot=[("VPB", "PARK", 200, 22154, "2026-07-02"), ("VPB", "PARK", 100, 20556, "2026-08-11"),
                   ("FPT", "LAG", 500, 100000, "2026-09-15")])
    try:
        sbx.broker["VPB"] = {"qty": 1800, "sellable": 1800}
        pl["orders"][0]["merged_from"]["sellable_at_calc"] = 300
        pl["orders"][1]["qty"] = 200
        pl["orders"].append({"id": "BUY-VPB-BAL-01", "ticker": "VPB", "side": "buy", "qty": 100,
                             "book": "BAL", "play_type": "BAL", "ref_price": 23500.0, "priority": 3})
        sbx.write_plan(pl)
        cb_apply(M, sbx)
        cp = sbx.read_plan()
        t1 = cp["book_transfers"][0]["id"]
        after = BCm.pause_transfer(cp, t1, "test", "2026-10-29T09:00:00")
        q = orders_qty(after)
        r["E10_pause_first_of_chain_keeps_second_delta"] = (
            after["book_transfers"][0]["status"] == "PAUSED"
            and q.get("BUY-VPB-LAG-01") == 200            # mua LAG khôi phục về gốc
            and q.get("SELL-VPB-PARK-01") == 200)         # bán PARK 300 − Δ(BAL)=100 còn lại
    finally:
        sbx.close()
        hypo_bal(M, False)

    # ── item 8 flock + item 4 import muộn ───────────────────────────────────────────────
    import fcntl
    sb, rc_, rep_ = cleared(M)
    try:
        px = sb.plan_path()
        raw = open(px, "rb").read()
        lockp = os.path.join(sb.pl, f".apply_book_transfers_{LABEL}.lock")
        fd = os.open(lockp, os.O_WRONLY | os.O_CREAT, 0o644)
        fcntl.flock(fd, fcntl.LOCK_EX)
        old = AB.LOCK_TIMEOUT_S
        AB.LOCK_TIMEOUT_S = 0.6
        try:
            rcl = AB.main(["--account", LABEL, "--date", PD, "--plan-dir", sb.pl, "--exec-dir", sb.ex])
        finally:
            AB.LOCK_TIMEOUT_S = old
            os.close(fd)
        r["L1_flock_held_by_other_process_fails_fast_no_write"] = (
            rcl == 2 and n_xfer_rows(sb) == 0 and open(px, "rb").read() == raw)
    finally:
        sb.close()
    # I1: import book_clearing hỏng + plan KHÔNG transfer ⇒ rc0; CÓ transfer ⇒ rc2 (subprocess, nguồn mutant)
    for nm, with_x, want in (("I1_import_broken_no_transfers_rc0", False, 0),
                             ("I2_import_broken_with_transfers_rc2", True, 2)):
        sb = SB()
        tmp = tempfile.mkdtemp(prefix="g3imp_")
        try:
            pl = base_plan(200)
            if with_x:
                pl["book_transfers"] = [{"id": "x", "status": "PLANNED"}]
            sb.write_plan(pl)
            for fn in ("wc_paths.py",):
                shutil.copy(os.path.join(HERE, fn), tmp)
            open(os.path.join(tmp, "apply_book_transfers.py"), "w").write(
                open(SRC["apply_book_transfers"], encoding="utf-8").read() if AB_SRC[0] is None else AB_SRC[0])
            code = (f"import sys; sys.path.insert(0, {tmp!r}); sys.modules['book_clearing'] = None\n"
                    f"import apply_book_transfers as A\n"
                    f"sys.exit(A.main(['--account', {LABEL!r}, '--date', {PD!r}, '--plan-dir', {sb.pl!r}, "
                    f"'--exec-dir', {sb.ex!r}]))")
            cp = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=60,
                                env=dict(os.environ, MIKE_BOT_TEST_MODE="1"))
            r[nm] = cp.returncode == want
        finally:
            sb.close()
            shutil.rmtree(tmp, ignore_errors=True)

    # ── item 9: các file mới nằm trong bao đóng của gốc T0 (run_bot.sh/bot_heartbeat.sh) ⇒ manifest xếp T0 ──
    spec = importlib.util.spec_from_file_location("_pm_g3", os.path.join(HERE, "production_manifest.py"))
    pm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pm)
    pm.in_scope = lambda p: os.path.isfile(p)
    pm.REF_BASES = [os.path.dirname(HERE), HERE] + list(pm.REF_BASES)
    pm.IMPORT_BASES = [HERE] + list(pm.IMPORT_BASES)

    def edges(f):
        src = open(os.path.join(HERE, f), encoding="utf-8").read()
        e = (pm.edges_shell_src(src, HERE) if f.endswith(".sh") else pm.edges_python_src(src, HERE))
        return {os.path.basename(str(x[0] if isinstance(x, tuple) else x)) for x in e}
    r["T0a_run_bot_sources_gate"] = "book_transfers_gate.sh" in edges("run_bot.sh")
    r["T0b_heartbeat_sources_gate"] = "book_transfers_gate.sh" in edges("bot_heartbeat.sh")
    r["T0c_gate_runs_apply"] = "apply_book_transfers.py" in edges("book_transfers_gate.sh")
    r["T0d_apply_imports_book_clearing"] = "book_clearing.py" in edges("apply_book_transfers.py")
    roots = {k for k, v in pm.ROOT_TIER.items() if v == "T0"} if hasattr(pm, "ROOT_TIER") else set()
    r["T0e_roots_run_bot_heartbeat_are_T0"] = {"run_bot.sh", "bot_heartbeat.sh"} <= roots


AB_SRC = [None]    # nguồn apply_book_transfers (mutant) cho ca subprocess I1/I2


# ───────────────────────────────────────────── mutant

MUTANTS = {
    "X1_skip_binding": ("apply_book_transfers", "probs = BC.binding_problems(plan, x)", "probs = []"),
    "X2_no_idempotent": ("apply_book_transfers", "if not probs and xid in jidx:", "if False:"),
    "X3_no_sellable": ("apply_book_transfers", "if int(sell) < need:", "if False:"),
    "X4_no_T2": ("apply_book_transfers", "if n < 2:", "if False:"),
    "X5_no_rights": ("apply_book_transfers", 'if l.get("rights_subscription"):\n            return', 'if False:\n            return'),
    "X6_ignore_approval": ("apply_book_transfers", 'why = deps["approval_fn"](plan)', "why = None"),
    "X7_no_account_check": ("apply_book_transfers", 'if x.get("account") != account:', "if False:"),
    "X8_no_cumulative_prefix": ("apply_book_transfers", "need = used.get(tk, 0) + m", "need = m"),
    "X9_no_banned": ("apply_book_transfers", "if tk in banned:", "if False:"),
    "X10_ignore_gates": ("apply_book_transfers", 'ok, gwhy = deps["gates_fn"](plan, x, set((h or {}).get("excluded_tickers") or []))', 'ok, gwhy = True, ""'),
    "X11_emergency_blind": ("apply_book_transfers", "done = jidx is not None and", "done = False and"),
    "K1_pause_no_restore_qty": ("book_clearing", 'o["qty"] = _orig_qty(o, ref) - others', 'o["qty"] = o["qty"]'),
    "K1b_pause_no_reappend_removed": ("book_clearing", "                    orders.append(o)\n                    by_id[oid] = o", "                    by_id[oid] = o"),
    "K9_sell_cap_ignores_removed": ("book_clearing", "                _cap_from(ro)", "                pass"),
    "K10_gate_without_signal_holds": ("book_clearing", '"filter_excluded_tickers", "filter_signal_holds", "filter_dd_flag_orders"', '"filter_excluded_tickers", "filter_dd_flag_orders"'),
    "K11_corp_action_ignored": ("book_clearing", "    if ev:\n        e0 = ev[0]", "    if False:\n        e0 = ev[0]"),
    "K12_approval_problem_off": ("book_clearing", '    if not req:\n        return None\n    ap = plan.get("approved_by")', '    if True:\n        return None\n    ap = plan.get("approved_by")'),
    "X12_partial_last_line_ok": ("apply_book_transfers", 'if f.read(1) != b"\\n":', "if False:"),
    "X13_no_excluded_check": ("apply_book_transfers", 'if tk in set(h.get("excluded_tickers") or []):', "if False:"),
    "X14_no_unverified_check": ("apply_book_transfers", 'if tk in set(h.get("unverified_tickers") or []):', "if False:"),
    "X15_no_reconcile_check": ("apply_book_transfers", "    if bad:\n        return [f\"{tk} lệch", "    if False:\n        return [f\"{tk} lệch"),
    "X16_no_sellable_missing_check": ("apply_book_transfers", "if sell is None:", "if False:"),
    "X17_no_today_eq_plan_date": ("apply_book_transfers", "if not probs and now_fn().date().isoformat() != date:", "if False:"),
    "X18_no_pending_approval_check": ("apply_book_transfers", "    if pending and not why:", "    if False:"),
    "X19_no_corp_action_check": ("apply_book_transfers", 'cwhy = BC.corp_action_problem(x["ticker"], BC.plan_asof(plan), date, deps.get("events_fn"))', "cwhy = None"),
    "X20_no_flock": ("apply_book_transfers", "fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)", "pass"),
    "X21_top_level_import": ("apply_book_transfers", "BC = None   # book_clearing", "import book_clearing as BC   # book_clearing"),
    "Q5_no_sell_cap_postcheck": ("clear_books", "+ BC.sell_cap_problems(new)", "+ []"),
    "Q6_no_excluded_check": ("clear_books", 'if tk in excluded:\n            why = "excluded_tickers của account"', 'if False:\n            why = "excluded_tickers của account"'),
    "Q7_no_park_prefix_T2": ("clear_books", 'if _sessions(l["entry_date"], plan_date, count_fn) < 2:', "if False:"),
    "Q8_no_corp_action_check": ("clear_books", 'cwhy = BC.corp_action_problem(op["ticker"], rep.get("asof"), plan_date, events_fn)', "cwhy = None"),
    "K2_revert_no_restore": ("book_clearing", '\n            o["qty"] = int(bc["orig_qty"])', "\n            pass"),
    "K3_lot_ignores_odd": ("book_clearing", "(rest % LOT == 0 or rest % LOT == odd)", "rest % LOT == 0"),
    "K4_revert_applied_ok": ("book_clearing", "    if applied:\n        raise", "    if False:\n        raise"),
    "K5_binding_no_qty": ("book_clearing", "if q != want:", "if False:"),
    "K6_revert_removed_ignores_marker": ("book_clearing", 'ro["qty"] = int(bc["orig_qty"])', "pass"),
    "K7_marker_overwritten": ("book_clearing", 'o.setdefault("book_clearing", {"transfer_id": xid, "orig_qty": orig})', 'o["book_clearing"] = {"transfer_id": xid, "orig_qty": orig}'),
    "K8_binding_per_record_not_final": ("book_clearing", 'want = final.get(ref.get("id"), int(ref.get("qty_after")))', 'want = int(ref.get("qty_after"))'),
    "Q1_knob_ignored": ("clear_books", "        if on:\n            mode = APPLY", "        if True:\n            mode = APPLY"),
    "Q2_approved_ok": ("clear_books", "if mode == APPLY and _approved(plan):", "if False:"),
    "Q3_gates_ignored": ("clear_books", "ok, why = gates_fn(trial, xs[0], excluded)", "ok, why = True, ''"),
    "Q4_no_revert_first": ("clear_books", "base, reverted = BC.revert_clearing(plan)", "base, reverted = plan, []"),
    "T1_to_books_has_bal": ("book_clearing", 'TO_BOOKS = ("LAG",)\n', 'TO_BOOKS = ("LAG", "BAL")\n'),
    "T2_analyze_no_bal_skip_record": ("clear_books", "            if park_sells and sk_bk in b_by:", "            if False and sk_bk in b_by:"),
    "T3_apply_opps_no_to_book_guard": ("book_clearing", "        if op.get(\"to_book\") not in TO_BOOKS:", "        if False:"),
    "T4_approval_str_None_ok": ("book_clearing", 'if ap.lower() in ("none", "null", "nil", "nan"):', "if False:"),
    "T5_requires_str_ignored": ("book_clearing", 'req = req.strip().lower() not in ("", "false", "no", "0", "none")', "req = False"),
    "T6_corp_action_no_timeout": ("book_clearing", "th.join(lim)", "th.join()"),
    "G1_merge_no_revert": ("merge_park_orders", "p, _cleared = BC.revert_clearing(p)", "_cleared = []"),
}
SH_MUTANTS = {
    "S1_gate_always_closed": ("book_transfers_gate.sh", 'if [ "$pend" != "0" ]; then', "if true; then"),
    "S2_gate_never_closed": ("book_transfers_gate.sh", 'return "$rc"', "return 0"),
    "S3_heartbeat_skips_gate": ("bot_heartbeat.sh", 'book_transfers_gate "$ACCOUNT" "$PLAN_DATE" "$rlog" || return 0', ":"),
    "S5_gate_tee_to_stdout": ("book_transfers_gate.sh", 'tee -a "$log" <"$out" >&2', 'tee -a "$log" <"$out"'),
    "S6_gate_append_event_stdout": ("book_transfers_gate.sh", '\\"pending_transfers\\":$pend,\\"log\\":\\"$log\\"}" >/dev/null 2>&1 || true', '\\"pending_transfers\\":$pend,\\"log\\":\\"$log\\"}" 2>/dev/null || true'),
    "S7_gate_notify_stdout": ("book_transfers_gate.sh", '(log: $log)" "$tid" >/dev/null 2>&1 || true', '(log: $log)" "$tid" 2>/dev/null || true'),
    "S8_heartbeat_truncates_log": ("bot_heartbeat.sh", '>> "$rlog" 2>&1 < /dev/null', '> "$rlog" 2>&1 < /dev/null'),
    "S9_pause_notice_prints_log_path": ("book_transfers_gate.sh", 'Lý do: ${why:-không trích được từ output apply — xem log} (log: $log)', 'Lý do: $log (log: $log)'),
    "S10_missing_status_not_pending": ("book_transfers_gate.sh", 'print(sum(1 for x in xs if not (isinstance(x, dict) and x.get("status") in ("APPLIED", "PAUSED"))))', 'print(sum(1 for x in xs if isinstance(x, dict) and x.get("status") == "PLANNED"))'),
    "S11_nonlist_not_pending": ("book_transfers_gate.sh", 'elif not isinstance(xs, list):\n    print(1)', 'elif not isinstance(xs, list):\n    print(0)'),
    "S4_run_bot_skips_gate": ("run_bot.sh", 'book_transfers_gate "$ACCOUNT" "$PLAN_DATE" "$LOG" || _xrc=$?', "_xrc=0"),
}
PF_MUTANTS = {
    "P1_pf_transfer_not_counted": ('_tot = sum(_q(o) for o in _os) + _xout.get(_tk, 0)', '_tot = sum(_q(o) for o in _os)'),
    "P2_pf_no_binding": ('if _xbad: flags.append', 'if False: flags.append'),
    "P4_pf_empty_orders_skips_approval": ('if n_orders > 0 or _xfers:', 'if n_orders > 0:'),
    "P3_pf_per_record_not_final": ('_want = _final.get(_r.get("id"), 0)', '_want = _q({"qty": _r.get("qty_after")})'),
}


def all_parts(M, pf_mut=None):
    r = {}
    PF_MUT[0] = pf_mut
    for fn in (part_a, part_m, part_b, part_r2, part_r3):
        try:
            fn(M, r)
        except Exception as e:
            r[f"{fn.__name__}_CRASH:{type(e).__name__}:{str(e)[:80]}"] = False
        if getattr(hypo_bal, "active", False):   # part crash giữa chừng ⇒ không để rò patch sang part sau
            hypo_bal(M, False)
    try:
        part_c(M, r, pf_mut)
    except Exception as e:
        r[f"part_c_CRASH:{type(e).__name__}:{e}"] = False
    return r


def main():
    print("== GĐ3 clearing selfcheck (cây thật) ==")
    M = load_mods()
    r = all_parts(M)
    part_d(r)
    part_sh(r)
    for k, v in r.items():
        check(k, v)
    print("== mutant ==")
    QUIET[0] = True
    for name, (mod, old, new) in MUTANTS.items():
        rr = all_parts(load_mods((mod, old, new)))
        caught = [k for k, v in rr.items() if not v]
        QUIET[0] = False
        check(f"{name} bị bắt", bool(caught), "SỐNG — không ca nào đỏ")
        if caught:
            print(f"        ↳ bắt bởi: {', '.join(caught[:4])}")
        QUIET[0] = True
    for name, mut in PF_MUTANTS.items():
        rr = all_parts(M, pf_mut=mut)
        caught = [k for k, v in rr.items() if not v]
        QUIET[0] = False
        check(f"{name} bị bắt", bool(caught), "SỐNG")
        if caught:
            print(f"        ↳ bắt bởi: {', '.join(caught[:4])}")
        QUIET[0] = True
    for name, mut in SH_MUTANTS.items():
        rr = {}
        part_sh(rr, mut)
        caught = [k for k, v in rr.items() if not v]
        QUIET[0] = False
        check(f"{name} bị bắt", bool(caught), "SỐNG")
        if caught:
            print(f"        ↳ bắt bởi: {', '.join(caught[:4])}")
        QUIET[0] = True
    QUIET[0] = False
    print(f"\n{'PASS — 0 lỗi' if not FAILS else 'FAIL — ' + ', '.join(FAILS)}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
