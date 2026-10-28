#!/usr/bin/env python3
"""Selfcheck `park_holdings` — sự kiện journal BOOK_TRANSFER + `LotBook.transfer` (clearing G1).

Sandbox offline: bootstrap/journal giả trong tmp, `broker=` bơm tay, corp_actions/rights_subs bơm
tay, broker_statement=False, `account_profile` thay bằng hồ sơ giả (KHÔNG đọc secrets thật).

Kịch bản (ca thật SpaceX VPB 26-29/10 thu nhỏ): bootstrap VPB PARK 160@07-02 + 126@08-11, FPT
LAG 500; 26/10 LAG mua VPB 1.500 (FILL tích luỹ 2 dòng).
  S0 inert       — không có dòng BOOK_TRANSFER ⇒ không có khoá `book_transfers_applied`, sổ y nguyên
  S1 bình thường — 29/10 chuyển 200 PARK→LAG: PARK còn 86 (prefix 160+40), LAG +2 lô MỚI ở CUỐI
                   sổ (entry 29/10, giá ref, holding_since giữ ngày cũ), Σ VPB bất biến, reconcile OK
  S2 idempotent  — cùng id ghi 2 lần (2 file) ⇒ y hệt S1
  S3 nhiều đêm   — 29/10 200 + 30/10 86 ⇒ PARK 0, lô đích theo đúng thứ tự
  S4 thiếu qty   — chuyển 300 > 286 ⇒ KHÔNG chuyển gì (nguyên tử), VPB UNVERIFIED
  S5 lô quyền    — prefix chạm lô CP quyền mua ⇒ từ chối, UNVERIFIED
  S6 id xung đột — cùng id khác qty ⇒ bản sau bỏ, UNVERIFIED
  S7 dòng hỏng   — thiếu from= ⇒ UNVERIFIED, không áp
  S8 auto_exit   — lô vừa chuyển KHÔNG tới hạn T+25 ngày 29/10 (`auto_exit_inject._due_lots`),
                   tới hạn đúng sau 25 phiên
  S9 quyền       — ×1,1 ex 29/10 (credit 30/10): lô chuyển ngày 29/10 VẪN hưởng (holding_since)
  S10 prefix     — sau transfer, lô nguồn còn lại giữ thứ tự; lô bị lấy là prefix theo thứ tự sell()

Mutant (phải bị bắt): M1 thừa kế entry_date cũ · M2 bỏ idempotent · M3 chuyển một phần khi thiếu ·
M4 chèn lô đích lên ĐẦU sổ · M5 trừ LIFO · M6 bỏ holding_since · M7 bỏ chặn lô quyền.

Chạy: python mike/bin/park_holdings_transfer_selfcheck.py   (rc 0 = PASS)
"""
import copy
import csv
import datetime as dt
import importlib.util
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import park_holdings as PH  # noqa: E402

LABEL = "SBX"                       # nhãn giả — không trùng account thật (quyền mua/statement thật)
BOOT = [("VPB", "PARK", 160, 22154, "2026-07-02"), ("VPB", "PARK", 126, 20556, "2026-08-11"),
        ("FPT", "LAG", 500, 100000, "2026-09-15")]
HDR = ["ts", "event", "parent_id", "ticker", "side", "child_oid", "qty", "price", "filled_total",
       "book", "play_type", "note"]
XID = "XFER-SBX-2026-10-29-VPB-PARK-LAG"
FAILS = []


def check(name, cond, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILS.append(name)
    return cond


def xrow(ts, xid, tk, qty, px, frm="PARK", to="LAG", note=None):
    return [ts, "BOOK_TRANSFER", xid, tk, "transfer", xid, qty, px, qty, to, "LAG_LO",
            note if note is not None else f"from={frm};to={to};src=selfcheck"]


def build(extra=None):
    """extra = {date: [rows]} thêm vào journal. Trả (sb, ex, pl)."""
    sb = tempfile.mkdtemp(prefix="ph_xfer_")
    ex, pl = os.path.join(sb, "exec"), os.path.join(sb, "plans")
    os.makedirs(ex)
    os.makedirs(pl)
    json.dump({"_status": "APPROVED selfcheck", "reconcile_ok": True, "day0_date": "2026-10-01",
               "broker_source": {"ts": "2026-09-30T19:10:00"},
               "positions": [{"ticker": t, "book": b, "qty": q, "cost_price_vnd": p, "entry_date": d}
                             for t, b, q, p, d in BOOT]},
              open(os.path.join(pl, f"bootstrap_book_snapshot_{LABEL}_20261001.json"), "w"))
    days = {"2026-10-26": [["2026-10-26T09:20:00", "FILL", "B1", "VPB", "buy", "c1", 900, 23000, 900, "LAG", "LAG_LO", ""],
                           ["2026-10-26T09:40:00", "FILL", "B1", "VPB", "buy", "c1", 1500, 23000, 1500, "LAG", "LAG_LO", ""]]}
    for d, rows in (extra or {}).items():
        days.setdefault(d, []).extend(rows)
    for d, rows in days.items():
        with open(os.path.join(ex, f"exec_{LABEL}_{d}_journal.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(HDR)
            w.writerows(rows)
    return sb, ex, pl


def run(mod, extra=None, broker_qty=None, corp_actions=None, asof="2026-10-30"):
    sb, ex, pl = build(extra)
    try:
        mod.account_profile = lambda label: {"label": label, "account_id": "000", "excluded_tickers": []}
        bq = broker_qty or {"VPB": 1786, "FPT": 500}
        pos = {t: {"qty": q, "market_price": 10000.0, "sellable": q} for t, q in bq.items()}
        return mod.park_holdings(LABEL, asof=asof, plan_dir=pl, exec_dir=ex,
                                 broker=(pos, 0.0, {"source": "selfcheck"}),
                                 corp_actions=corp_actions or [], rights_subs=[],
                                 broker_statement=False, need_price=False)
    finally:
        shutil.rmtree(sb, ignore_errors=True)


def lots_of(h, tk, book):
    return [l for l in h["lots"] if l["ticker"] == tk and l["book"] == book]


def qty(h, tk, book=None):
    return sum(l["qty"] for l in h["lots"] if l["ticker"] == tk and (book is None or l["book"] == book))


def lag_snapshot(h, tk, book="LAG"):
    """Dựng đúng cấu trúc `portfolio_status.book_lot_snapshot` (lọc book, GIỮ thứ tự sổ)."""
    ls = [{"qty": l["qty"], "entry_date": l["entry_date"]} for l in h["lots"]
          if l["ticker"] == tk and l["book"] == book]
    return {"qty": sum(x["qty"] for x in ls), "entry_date": ls[0]["entry_date"], "lots": ls}


T29 = "2026-10-29T08:45:00"
T30 = "2026-10-30T08:45:00"


def scenarios(mod):
    """dict tên → bool. Dùng chung cho bản thật và mutant."""
    import auto_exit_inject as AEI
    RULES = AEI.rules
    from portfolio_status import count_trading_days
    from trading_bot.vn_market import next_trading_day
    r = {}
    h0 = run(mod)
    r["S0_inert_no_key"] = "book_transfers_applied" not in h0 and h0["reconcile"]["ok"] \
        and qty(h0, "VPB", "PARK") == 286 and qty(h0, "VPB", "LAG") == 1500

    h1 = run(mod, {"2026-10-29": [xrow(T29, XID, "VPB", 200, 23500)]})
    park, lag = lots_of(h1, "VPB", "PARK"), lots_of(h1, "VPB", "LAG")
    new = [l for l in lag if l.get("book_transfer")]
    r["S1_park_left_86"] = [(l["qty"], l["entry_date"]) for l in park] == [(86, "2026-08-11")]
    r["S1_two_new_lots_at_end"] = (h1["lots"][-2:] == new and [l["qty"] for l in new] == [160, 40])
    r["S1_new_entry_date_price"] = all(l["entry_date"] == "2026-10-29" and l["price"] == 23500.0
                                       for l in new)
    r["S1_holding_since_kept"] = [l.get("holding_since") for l in new] == ["2026-07-02", "2026-08-11"]
    r["S1_total_invariant"] = qty(h1, "VPB") == 1786 and h1["reconcile"]["ok"] \
        and "VPB" not in h1["unverified_tickers"]
    r["S1_applied_key"] = h1.get("book_transfers_applied", [{}])[0].get("applied_qty") == 200

    h2 = run(mod, {"2026-10-29": [xrow(T29, XID, "VPB", 200, 23500), xrow(T29, XID, "VPB", 200, 23500)],
                   "2026-10-30": [xrow(T29, XID, "VPB", 200, 23500)]})
    r["S2_idempotent"] = (qty(h2, "VPB", "PARK") == 86 and qty(h2, "VPB", "LAG") == 1700
                          and "VPB" not in h2["unverified_tickers"])

    h3 = run(mod, {"2026-10-29": [xrow(T29, XID, "VPB", 200, 23500)],
                   "2026-10-30": [xrow(T30, XID + "-2", "VPB", 86, 23600)]})
    new3 = [l for l in lots_of(h3, "VPB", "LAG") if l.get("book_transfer")]
    r["S3_multi_night"] = (qty(h3, "VPB", "PARK") == 0 and qty(h3, "VPB") == 1786
                           and [(l["qty"], l["entry_date"]) for l in new3]
                           == [(160, "2026-10-29"), (40, "2026-10-29"), (86, "2026-10-30")])

    h4 = run(mod, {"2026-10-29": [xrow(T29, XID, "VPB", 300, 23500)]})
    r["S4_insufficient_atomic"] = (qty(h4, "VPB", "PARK") == 286 and qty(h4, "VPB", "LAG") == 1500
                                   and "VPB" in h4["unverified_tickers"])

    h6 = run(mod, {"2026-10-29": [xrow(T29, XID, "VPB", 200, 23500)],
                   "2026-10-30": [xrow(T30, XID, "VPB", 86, 23500)]})
    r["S6_conflict_unverified"] = (qty(h6, "VPB", "PARK") == 86 and "VPB" in h6["unverified_tickers"])

    h7 = run(mod, {"2026-10-29": [xrow(T29, XID, "VPB", 200, 23500, note="to=LAG")]})
    r["S7_invalid_row"] = (qty(h7, "VPB", "PARK") == 286 and "VPB" in h7["unverified_tickers"])

    # S8 — auto_exit per-lot: lô chuyển 29/10 không tới hạn ngày 29/10 dù lô gốc từ 07-02
    snap = lag_snapshot(h1, "VPB")
    is_due = RULES.lag_should_exit
    due29, err = AEI._due_lots(snap, dt.date(2026, 10, 29), is_due)
    r["S8_not_due_on_transfer_day"] = err is None and due29[0] == 0
    d = dt.date(2026, 10, 29)
    for _ in range(25):
        d = next_trading_day(d)
    dueN, err = AEI._due_lots(snap, d, is_due)
    r["S8_due_after_25_sessions"] = (err is None and dueN[0] == 1700
                                     and count_trading_days(dt.date(2026, 10, 29), d) == 25)

    # S8b — sổ đích CHƯA có lô nào (BAL): không có lô mới đứng chắn prefix, nên lô chuyển phải tự
    # mang entry_date mới — thừa kế 07-02 thì T+45 tới hạn ngay và bị bán trong ngày.
    h8 = run(mod, {"2026-10-29": [xrow(T29, XID + "-BAL", "VPB", 200, 23500, to="BAL")]})
    due8, err = AEI._due_lots(lag_snapshot(h8, "VPB", "BAL"), dt.date(2026, 10, 29), RULES.bal_should_exit)
    r["S8b_bal_not_due_on_transfer_day"] = err is None and due8[0] == 0 and qty(h8, "VPB", "BAL") == 200

    # S9 — quyền: ex 29/10, broker credit 30/10 ×1,1 ⇒ 286 cp PARK cũ (giờ 86 PARK + 200 LAG) hưởng
    ca = [{"id": "VPB-X", "ticker": "VPB", "event_type": "STOCK_DIVIDEND", "qty_multiplier": 1.1,
           "ex_date": "2026-10-29", "broker_effective_ts": "2026-10-30T07:00:00", "_status": "CONFIRMED"}]
    h9 = run(mod, {"2026-10-29": [xrow(T29, XID, "VPB", 200, 23500)]}, corp_actions=ca,
             broker_qty={"VPB": 1964, "FPT": 500})   # (286+1500)×1,1 sàn = 1964
    r["S9_rights_by_holding_since"] = qty(h9, "VPB") == int((286 + 1500) * 1.1 + 1e-9)

    # S10 — prefix: các lô KHÔNG phải VPB/PARK giữ nguyên thứ tự tương đối
    others0 = [(l["ticker"], l["book"], l["qty"]) for l in h0["lots"] if not (l["ticker"] == "VPB" and l["book"] == "PARK")]
    others1 = [(l["ticker"], l["book"], l["qty"]) for l in h1["lots"]
               if not (l["ticker"] == "VPB" and l["book"] == "PARK") and not l.get("book_transfer")]
    r["S10_prefix_order"] = (others0 == others1 and [l.get("book_transfer", {}).get("from_entry_date")
                                                      for l in new] == ["2026-07-02", "2026-08-11"])
    return r


def lotbook_rights(mod):
    """S5 — LotBook trực tiếp: prefix chạm lô quyền mua ⇒ từ chối nguyên tử."""
    b = mod.LotBook()
    b.buy("ABC", "PARK", 100, 10000, "2026-09-01", "t")
    b.lots.append({"ticker": "ABC", "book": "PARK", "play_type": "", "entry_date": "2026-09-01",
                   "qty": 50, "price": 5000.0, "source": "rights", "rights_subscription": {"event_id": "R"}})
    before = copy.deepcopy(b.lots)
    n = b.transfer("ABC", "PARK", "LAG", 120, "2026-10-29", 11000, "t", "LAG_LO", "X1")
    ok_block = n == 0 and b.lots == before and "ABC" in b.unverified
    b2 = mod.LotBook()
    b2.buy("ABC", "PARK", 100, 10000, "2026-09-01", "t")
    b2.lots.append(dict(before[1]))
    n2 = b2.transfer("ABC", "PARK", "LAG", 100, "2026-10-29", 11000, "t", "LAG_LO", "X2")
    ok_prefix_only = n2 == 100 and "ABC" not in b2.unverified   # lô quyền nằm SAU prefix ⇒ được
    return {"S5_rights_lot_blocked": ok_block, "S5_rights_after_prefix_ok": ok_prefix_only}


def all_scenarios(mod):
    out = scenarios(mod)
    out.update(lotbook_rights(mod))
    return out


MUTANTS = {
    "M1_inherit_entry_date": ('"entry_date": date, "qty": take', '"entry_date": lot["entry_date"], "qty": take'),
    "M2_no_idempotency": ('if ev["id"] in xfer_seen:', 'if False:'),
    "M3_partial_when_short": ("        if have < qty:\n", "        if False:\n"),
    "M4_new_lots_front": ('self.lots = [l for l in self.lots if l["qty"] > 0] + new_lots',
                          'self.lots = new_lots + [l for l in self.lots if l["qty"] > 0]'),
    "M5_lifo": ("for lot in pool:                                  # cùng vòng tiêu thụ với sell()",
                "for lot in reversed(pool):"),
    "M6_no_holding_since": ('return lot.get("holding_since") or lot["entry_date"]', 'return lot["entry_date"]'),
    "M7_no_rights_block": ('if any(lot.get("rights_subscription") for lot, _ in plan):', 'if False:'),
}


def load_mutant(name, old, new):
    src = open(os.path.join(HERE, "park_holdings.py"), encoding="utf-8").read()
    if src.count(old) != 1:
        raise SystemExit(f"mutant {name}: chuỗi gốc xuất hiện {src.count(old)} lần (phải đúng 1) — selfcheck lỗi thời")
    d = tempfile.mkdtemp(prefix="ph_mut_")
    p = os.path.join(d, f"park_holdings_{name}.py")
    open(p, "w", encoding="utf-8").write(src.replace(old, new))
    spec = importlib.util.spec_from_file_location(f"park_holdings_{name}", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    shutil.rmtree(d, ignore_errors=True)
    return m


def main():
    os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")
    print(f"== park_holdings BOOK_TRANSFER selfcheck (TZ={os.environ.get('TZ', '<unset>')}) ==")
    for k, v in all_scenarios(PH).items():
        check(k, v)
    print("== mutants (mỗi mutant phải làm ≥1 kịch bản FAIL) ==")
    for name, (old, new) in MUTANTS.items():
        m = load_mutant(name, old, new)
        try:
            res = all_scenarios(m)
            killed = [k for k, v in res.items() if not v]
        except Exception as e:
            killed = [f"exception {type(e).__name__}"]
        check(f"{name} bị bắt", bool(killed), "mutant SỐNG — kịch bản không phân biệt được")
        if killed:
            print(f"        ↳ bắt bởi: {', '.join(killed[:4])}")
    print(f"\n{'PASS' if not FAILS else 'FAIL'} — {len(FAILS)} lỗi" + (f": {FAILS}" if FAILS else ""))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
