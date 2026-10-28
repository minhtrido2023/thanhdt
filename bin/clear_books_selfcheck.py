#!/usr/bin/env python3
"""Selfcheck `clear_books.py` (clearing PARK→LAG/BAL, SHADOW giai đoạn 1).

Offline hoàn toàn: sổ lô + plan dựng tay, `holdings_fn`/`load_banned` bơm tay, plan/out ghi vào tmp.
Đếm phiên dùng `portfolio_status.count_trading_days` THẬT (lịch nghỉ VN).

Kịch bản:
  A1 cơ hội chuẩn       — PARK bán 200 + LAG mua 1.500 VPB ⇒ chuyển 200, mua còn 1.300, bán còn 0,
                          tiết kiệm = 200×23.500×(phí mua+phí bán+thuế) lấy từ dnse_fee_rates
  A2 thiếu sellable     — broker sellable 150 ⇒ m_raw 150, hạ về 100 (bội lô lệnh còn lại)
  A3 sellable 0 / chưa đủ T+2 — chặn, có lý do
  A4 lô quyền / UNVERIFIED / excluded / BANNED — chặn từng mã, có lý do
  A5 2 sổ đích          — PARK bán 300, LAG mua 200 + BAL mua 200 ⇒ LAG 200, BAL 100 (Σ ≤ PARK bán)
  R1 roll               — bán LAG + mua LAG cùng mã ⇒ chỉ báo, tiết kiệm 0, không thành cơ hội
  X1 MISSED ca thật SpaceX VPB 26→29/10 — PARK 160+126, LAG mua 5×300 ngày 26/10, plan bán PARK 200
                          ⇒ missed 286cp, tiết kiệm 0, "lẽ ra" ≈ 19.760đ
  X2 ca thật ZaloPay VPB — PARK 30 dưới ngưỡng (không có lệnh bán PARK), LAG auto-exit 282
                          ⇒ không cơ hội, không missed, không roll
  F1-F4 fail-closed      — thiếu plan / sổ lô SystemExit / orders không phải list / asof ≥ plan_date
                          ⇒ rc=2, status=ERROR, dòng người đọc KHÔNG nói "không có cơ hội"
  W1 file ghi            — JSON ở <out>/<acct>_<plan_date>.json, status SHADOW, plan_md5 đúng

Mutant (phải bị bắt): C1 bỏ thuế bán · C2 bỏ làm tròn lô · C3 bỏ trần broker sellable ·
C4 bỏ cổng UNVERIFIED · C5 bỏ cổng lô quyền · C6 lỗi dữ liệu trả rc 0 · C7 missed không cần PARK bán.

Chạy: python mike/bin/clear_books_selfcheck.py   (rc 0 = PASS)
"""
import hashlib
import importlib.util
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import clear_books as CB  # noqa: E402
import dnse_fee_rates as FEES  # noqa: E402
from portfolio_status import count_trading_days  # noqa: E402

PD, ASOF = "2026-10-29", "2026-10-28"
FAILS = []
RATE = FEES.FEE_RATE_BUY_PCT / 100 + FEES.FEE_RATE_SELL_PCT / 100 + FEES.SELL_TAX_RATE


def check(name, cond, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILS.append(name)
    return cond


def lot(tk, book, q, d, **kw):
    return dict({"ticker": tk, "book": book, "play_type": "", "entry_date": d, "qty": q,
                 "price": 20000.0, "source": "t"}, **kw)


def H(lots, sellable=None, unverified=(), excluded=(), label="SBX"):
    tot = {}
    for l in lots:
        tot[l["ticker"]] = tot.get(l["ticker"], 0) + l["qty"]
    pos = {t: {"qty": q, "sellable": (sellable or {}).get(t, q)} for t, q in tot.items()}
    return {"account_label": label, "lots": lots, "broker_positions": pos,
            "unverified_tickers": sorted(unverified), "excluded_tickers": sorted(excluded),
            "reconcile": {"ok": True}, "bootstrap": "sb"}


def O(oid, tk, side, q, book, px=23500.0):
    return {"id": oid, "ticker": tk, "side": side, "qty": q, "book": book, "ref_price": px}


PARK_VPB = [lot("VPB", "PARK", 160, "2026-07-02"), lot("VPB", "PARK", 126, "2026-08-11")]


def an(mod, plan_orders, h, banned=()):
    return mod.analyze({"orders": plan_orders}, h, PD, set(banned), count_trading_days)


def scenarios(mod):
    r = {}
    base = [O("S-PARK", "VPB", "sell", 200, "PARK"), O("B-LAG", "VPB", "buy", 1500, "LAG")]
    a1 = an(mod, base, H(list(PARK_VPB)))
    o = a1["opportunities"][0] if a1["opportunities"] else {}
    r["A1_transfer_200"] = (o.get("transfer_qty") == 200 and o.get("buy_qty_after") == 1300
                            and o.get("park_sell_qty_after") == 0 and o.get("to_book") == "LAG")
    r["A1_saving_from_fee_constants"] = o.get("saving_est_vnd") == round(200 * 23500 * RATE)

    a2 = an(mod, base, H(list(PARK_VPB), sellable={"VPB": 150}))
    o2 = a2["opportunities"][0] if a2["opportunities"] else {}
    r["A2_sellable_cap_and_lot"] = o2.get("m_raw") == 150 and o2.get("transfer_qty") == 100 \
        and o2.get("buy_qty_after") % 100 == 0 and o2.get("park_sell_qty_after") % 100 == 0

    a3 = an(mod, base, H(list(PARK_VPB), sellable={"VPB": 0}))
    r["A3_sellable0_blocked"] = not a3["opportunities"] and any(b["ticker"] == "VPB" for b in a3["blocked"])
    a3b = an(mod, base, H([lot("VPB", "PARK", 300, "2026-10-28")]))     # mua hôm qua ⇒ chưa T+2
    r["A3_unsettled_blocked"] = not a3b["opportunities"] and any("T+2" in b["reason"] for b in a3b["blocked"])

    a4r = an(mod, base, H(PARK_VPB + [lot("VPB", "PARK", 20, "2026-09-01", rights_subscription={"event_id": "R"})]))
    r["A4_rights_blocked"] = not a4r["opportunities"] and any("quyền" in b["reason"] for b in a4r["blocked"])
    a4u = an(mod, base, H(list(PARK_VPB), unverified=["VPB"]))
    r["A4_unverified_blocked"] = not a4u["opportunities"] and any("UNVERIFIED" in b["reason"] for b in a4u["blocked"])
    a4e = an(mod, base, H(list(PARK_VPB), excluded=["VPB"]))
    r["A4_excluded_blocked"] = not a4e["opportunities"] and a4e["blocked"]
    a4b = an(mod, base, H(list(PARK_VPB)), banned=["VPB"])
    r["A4_banned_blocked"] = not a4b["opportunities"] and any(b["reason"] == "BANNED" for b in a4b["blocked"])

    a5 = an(mod, [O("S", "VPB", "sell", 300, "PARK"), O("BL", "VPB", "buy", 200, "LAG"),
                  O("BB", "VPB", "buy", 200, "BAL")], H(PARK_VPB + [lot("VPB", "PARK", 100, "2026-08-20")]))
    r["A5_two_target_books"] = ([(x["to_book"], x["transfer_qty"]) for x in a5["opportunities"]]
                                == [("LAG", 200), ("BAL", 100)])

    r1 = an(mod, [O("S", "ABC", "sell", 300, "LAG"), O("B", "ABC", "buy", 200, "LAG")],
            H([lot("ABC", "LAG", 300, "2026-09-01")]))
    r["R1_roll_report_only"] = (not r1["opportunities"] and len(r1["roll_candidates"]) == 1
                                and r1["roll_candidates"][0]["saving_est_vnd"] == 0)

    # X1 — ca thật SpaceX VPB (plan 29/10: chỉ bán PARK 200 + mua MCH LAG)
    x1 = an(mod, [O("PARKMERGE-SELL-VPB", "VPB", "sell", 200, "PARK"),
                  O("BUY-MCH-LAG-01", "MCH", "buy", 200, "LAG", 139800.0)],
            H(PARK_VPB + [lot("VPB", "LAG", 300, "2026-10-26") for _ in range(5)]))
    m = x1["missed"][0] if x1["missed"] else {}
    r["X1_spacex_vpb_missed_286"] = (not x1["opportunities"] and m.get("ticker") == "VPB"
                                     and m.get("would_have_transferred_qty") == 286
                                     and m.get("saving_est_vnd") == 0
                                     and m.get("forgone_saving_est_vnd") == round(286 * 23500 * RATE))
    # X2 — ca thật ZaloPay VPB
    x2 = an(mod, [O("BUY-MCH", "MCH", "buy", 200, "LAG", 139800.0),
                  O("AEI-VPB", "VPB", "sell", 282, "LAG")],
            H([lot("VPB", "LAG", 282, "2026-07-27"), lot("VPB", "PARK", 30, "2025-11-20"),
               lot("VPB", "LAG", 600, "2026-10-26"), lot("VPB", "LAG", 300, "2026-10-27")]))
    r["X2_zalopay_nothing"] = not (x2["opportunities"] or x2["missed"] or x2["roll_candidates"] or x2["blocked"])
    return r


def io_scenarios(mod):
    r = {}
    sb = tempfile.mkdtemp(prefix="cb_sc_")
    try:
        pl, out = os.path.join(sb, "plans"), os.path.join(sb, "out")
        os.makedirs(pl)
        mod.load_banned = lambda: set()
        good = lambda a, d: H(list(PARK_VPB))   # noqa: E731
        rc, rep = mod.run_account("SBX", PD, ASOF, pl, out, 5, count_trading_days, good)
        r["F1_missing_plan_rc2"] = rc == 2 and rep["status"] == "ERROR" and "không có cơ hội" not in rep["summary_line"]
        plan = {"orders": [O("S", "VPB", "sell", 200, "PARK"), O("B", "VPB", "buy", 1500, "LAG")],
                "park_trim_proposal": {"asof": ASOF}}
        pth = os.path.join(pl, f"plan_SBX_{PD}.json")
        json.dump(plan, open(pth, "w"))

        def boom(a, d):
            raise SystemExit("[park_holdings] THIẾU bootstrap snapshot (giả lập)")
        rc, rep = mod.run_account("SBX", PD, ASOF, pl, out, 5, count_trading_days, boom)
        r["F2_ledger_systemexit_rc2"] = rc == 2 and "bootstrap" in rep.get("error", "") \
            and "không có cơ hội" not in rep["summary_line"]
        json.dump({"orders": "x"}, open(pth, "w"))
        rc, rep = mod.run_account("SBX", PD, ASOF, pl, out, 5, count_trading_days, good)
        r["F3_orders_not_list_rc2"] = rc == 2 and rep["status"] == "ERROR"
        json.dump(plan, open(pth, "w"))
        rc, rep = mod.run_account("SBX", PD, PD, pl, out, 5, count_trading_days, good)
        r["F4_asof_not_before_rc2"] = rc == 2 and rep["status"] == "ERROR"
        rc, rep = mod.run_account("SBX", PD, None, pl, out, 5, count_trading_days, good)
        f = os.path.join(out, f"SBX_{PD}.json")
        disk = json.load(open(f)) if os.path.exists(f) else {}
        r["W1_written_shadow"] = (rc == 0 and disk.get("status") == "SHADOW" and disk.get("asof") == ASOF
                                  and disk.get("plan_md5") == hashlib.md5(open(pth, "rb").read()).hexdigest()
                                  and disk.get("total_saving_est_vnd") == round(200 * 23500 * RATE))
        r["W1_plan_untouched"] = json.load(open(pth)) == plan
    finally:
        shutil.rmtree(sb, ignore_errors=True)
    return r


def all_scenarios(mod):
    out = scenarios(mod)
    out.update(io_scenarios(mod))
    return out


MUTANTS = {
    "C1_no_sell_tax": ('m * px_sell * (r["sell_fee"] + r["sell_tax"])', 'm * px_sell * r["sell_fee"]'),
    "C2_no_lot_rounding": ("m = lot_feasible(m_raw, buy_qty, rem_buy)", "m = m_raw"),
    "C3_no_broker_sellable": ("avail = min(settled, int(broker_sellable))", "avail = settled"),
    "C4_no_unverified_gate": ("elif tk in unverified:", "elif False:"),
    "C5_no_rights_gate": ('elif any(l.get("rights_subscription") for l in park_lots):', "elif False:"),
    "C6_dataerror_rc0": ('rep["error"] = str(e) if str(e) else type(e).__name__\n        rc = 2',
                         'rep["error"] = str(e) if str(e) else type(e).__name__\n        rc = 0'),
    "C7_missed_without_park_sell": ("        if not park_sells:\n            continue\n",
                                    "        if False:\n            continue\n"),
}


def load_mutant(name, old, new):
    src = open(os.path.join(HERE, "clear_books.py"), encoding="utf-8").read()
    if src.count(old) != 1:
        raise SystemExit(f"mutant {name}: chuỗi gốc xuất hiện {src.count(old)} lần (phải đúng 1)")
    d = tempfile.mkdtemp(prefix="cb_mut_")
    p = os.path.join(d, f"clear_books_{name}.py")
    open(p, "w", encoding="utf-8").write(src.replace(old, new))
    spec = importlib.util.spec_from_file_location(f"clear_books_{name}", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    shutil.rmtree(d, ignore_errors=True)
    return m


def main():
    os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")
    print(f"== clear_books selfcheck (TZ={os.environ.get('TZ', '<unset>')}) ==")
    for k, v in all_scenarios(CB).items():
        check(k, v)
    print("== mutants ==")
    for name, (old, new) in MUTANTS.items():
        m = load_mutant(name, old, new)
        try:
            killed = [k for k, v in all_scenarios(m).items() if not v]
        except Exception as e:
            killed = [f"exception {type(e).__name__}: {e}"]
        check(f"{name} bị bắt", bool(killed), "mutant SỐNG")
        if killed:
            print(f"        ↳ bắt bởi: {', '.join(killed[:4])}")
    print(f"\n{'PASS' if not FAILS else 'FAIL'} — {len(FAILS)} lỗi" + (f": {FAILS}" if FAILS else ""))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
