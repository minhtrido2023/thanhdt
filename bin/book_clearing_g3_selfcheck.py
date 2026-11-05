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
            exec(compile(src, SRC[n], "exec"), m.__dict__)
            mods[n] = m
    finally:
        if saved is not None:
            sys.modules["book_clearing"] = saved
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


GATE_OK = (lambda plan, x, ex: (True, "stub"))
GATE_NO = (lambda plan, x, ex: (False, "stub: 8L rating=4"))


def cb_apply(M, sb, knob=True, gates=GATE_OK, d=PD, asof=ASOF):
    return M["clear_books"].run_account(
        LABEL, d, asof, sb.pl, os.path.join(sb.root, "out"), 5, count_fn=count_trading_days,
        holdings_fn=sb.holdings, apply=True,
        knob_fn=(lambda: (knob, "stub")), gates_fn=gates)


def ab_deps(M, sb, approval=None, banned=(), gates=GATE_OK, now=f"{PD}T09:01:00"):
    import datetime as dt
    from zoneinfo import ZoneInfo
    return {"ph": PH, "holdings_fn": sb.holdings, "banned_fn": (lambda: set(banned)),
            "count_fn": count_trading_days, "gates_fn": gates,
            "approval_fn": (lambda plan: approval),
            "now_fn": (lambda: dt.datetime.fromisoformat(now).replace(tzinfo=ZoneInfo("Asia/Ho_Chi_Minh")))}


def ab_run(M, sb, d=PD, **kw):
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
                                               and [o["id"] for o in p["orders"]] == ["BUY-FPT-LAG-01"])
    finally:
        sb.close()

    def paused(name, setup=None, rc_want=3, **kw):
        sb, (rc, plan, log) = _b(M, setup, **kw)
        try:
            p = sb.read_plan()
            ok = (rc == rc_want and n_xfer_rows(sb) == 0
                  and p["book_transfers"][0]["status"] == "PAUSED"
                  and [o["id"] for o in p["orders"]] == ["BUY-FPT-LAG-01"]
                  and {o["id"] for o in p["book_transfers"][0]["paused_orders"]} == {"BUY-VPB-LAG-01"})
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
                                                     and "BUY-VPB-LAG-01" not in {o["id"] for o in p["orders"]})
    finally:
        sb.close()

    for name, kw, setup in (("B9_not_approved_noop", {"approval": "chưa duyệt"}, None),
                            ("B10_bot_stop_noop", {}, lambda sb: open(os.path.join(sb.root, "BOT_STOP"), "w").close())):
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
        r["B16_two_targets_cumulative_prefix"] = (n_planned == 2 and rc == 3
                                                  and st == ["APPLIED", "PAUSED"] and n_xfer_rows(sb) == 1)
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
    "K1_pause_keeps_orders": ("book_clearing", '(gone if o.get("id") in ids else keep).append(o)', "keep.append(o)"),
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
    "G1_merge_no_revert": ("merge_park_orders", "p, _cleared = BC.revert_clearing(p)", "_cleared = []"),
}
PF_MUTANTS = {
    "P1_pf_transfer_not_counted": ('_tot = sum(_q(o) for o in _os) + _xout.get(_tk, 0)', '_tot = sum(_q(o) for o in _os)'),
    "P2_pf_no_binding": ('if _xbad: flags.append', 'if False: flags.append'),
    "P3_pf_per_record_not_final": ('_want = _final.get(_r.get("id"), 0)', '_want = _q({"qty": _r.get("qty_after")})'),
}


def all_parts(M, pf_mut=None):
    r = {}
    PF_MUT[0] = pf_mut
    for fn in (part_a, part_m, part_b):
        try:
            fn(M, r)
        except Exception as e:
            r[f"{fn.__name__}_CRASH:{type(e).__name__}:{str(e)[:80]}"] = False
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
    QUIET[0] = False
    print(f"\n{'PASS — 0 lỗi' if not FAILS else 'FAIL — ' + ', '.join(FAILS)}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
