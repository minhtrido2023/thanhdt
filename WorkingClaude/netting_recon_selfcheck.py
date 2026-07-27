# -*- coding: utf-8 -*-
"""Self-check reconciliation post-fill netting — `trading_bot.netting_recon`.

Kiểm chứng buộc phải có (dispatch Taylor_20260727_040719):
- Đúng khi NET=0 / 100% nội bộ (định giá @ ref, 0 chạm broker, 2 leg bù trừ).
- Đúng khi NET≠0 (định giá 2 leg @ giá khớp THẬT của lệnh net).
- FAIL LOUD đúng khi giá khớp không lấy được.
- KHÔNG lệch book-vs-broker trong mọi case sạch; FAIL LOUD khi broker delta bất nhất.
- Khớp MỘT PHẦN không gây FAIL giả.
- TÍCH HỢP (L/M/N — quant-skeptic yêu cầu, không chỉ mock): nạp dòng FILL THẬT trong journal
  executor qua `get_net_fill_from_journal` → chứng minh giá lấy từ avg_price broker (cột
  `price` của FILL) chứ KHÔNG phải giá đặt lệnh; khớp một phần + bình quân gia quyền đúng.

Chạy: python3 netting_recon_selfcheck.py   (thuần logic, không broker/BQ/pickle thật)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trading_bot.plan import (PlannedOrder, TradePlan, net_offsetting_orders)  # noqa: E402
from trading_bot.netting_recon import (reconcile_netted_fills, write_recon_log,  # noqa: E402
                                       get_net_fill_from_journal)

FAILS = []
NCHECK = [0]


def check(name, cond, detail=""):
    NCHECK[0] += 1
    print(("  ✅ " if cond else "  ❌ ") + name + (f" — {detail}" if detail else ""))
    if not cond:
        FAILS.append(name)


def mkplan(orders):
    return TradePlan(plan_date="2026-07-27", signal_date="2026-07-24", strategy="V2.4",
                     strategy_version="r3", state=3, state_name="NEUTRAL",
                     nav_basis={}, orders=orders, account="selfcheck_recon")


def order(tk, side, qty, px=24_900, book="LAG", pri=5, urg="normal", note=""):
    return PlannedOrder(id=f"{side.upper()}-{tk}-{pri:02d}", ticker=tk, side=side, qty=qty,
                        ref_price=px, book=book, priority=pri, urgency=urg, note=note)


def refmap(d):
    return lambda tk: d.get(tk)


def fillmap(d):
    # d: {ticker: (filled_qty, avg_price)}
    return lambda tk, side: d.get(tk, (0, None))


def market_delta(records):
    """Σ Δ book chạm-thị-trường của 1 record = net_to_broker (nội bộ bù trừ)."""
    return sum(r["net_to_broker"] for r in records)


# ── A. NET≠0 (VPB SELL 100), KHỚP ĐỦ @ giá thật 24.850 ────────────────────────────────
print("\nA. NET≠0 khớp đủ @ giá khớp thật (VPB SELL 800 park + BUY 700 LAG → NET SELL 100)")
_, adj = net_offsetting_orders(mkplan([
    order("VPB", "sell", 800, book="custom30V_parking", pri=1, urg="high"),
    order("VPB", "buy", 700, book="LAG", pri=2),
]))
recs, fails = reconcile_netted_fills(
    adj, get_net_fill=fillmap({"VPB": (100, 24_850)}), ref_price_of=refmap({"VPB": 24_900}),
    broker_net_delta={"VPB": -100})
check("không failure", not fails, str(fails))
check("1 record", len(recs) == 1)
r = recs[0]
check("net_to_broker = -100 (bán)", r["net_to_broker"] == -100, str(r["net_to_broker"]))
check("giá dùng = giá khớp THẬT 24.850", r["price"] == 24_850, str(r["price"]))
check("price_source = giá khớp thật", "khớp thật" in r["price_source"], r["price_source"])
check("cả 2 leg định giá @ 24.850 (nội bộ cùng giá)",
      r["buy_legs"][0]["price"] == 24_850 and r["sell_legs"][0]["price"] == 24_850)
check("buy_leg book=LAG qty=700", r["buy_legs"][0]["book"] == "LAG" and r["buy_legs"][0]["qty"] == 700)
check("sell_leg book=park qty=800",
      r["sell_legs"][0]["book"] == "custom30V_parking" and r["sell_legs"][0]["qty"] == 800)
check("Σ book chạm-TT == net_to_broker (-100)", market_delta(recs) == -100)

# ── B. NET=0 / 100% nội bộ (mua 700 = bán 700) → 0 chạm broker, định giá @ ref ─────────
print("\nB. NET=0 (100% nội bộ): SELL 700 park + BUY 700 LAG → 0 lệnh broker")
_, adj = net_offsetting_orders(mkplan([
    order("HPG", "sell", 700, px=26_000, book="custom30V_parking", pri=1),
    order("HPG", "buy", 700, px=26_000, book="LAG", pri=2),
]))
check("adj action INTERNAL_ONLY", adj[0]["action"] == "INTERNAL_ONLY")
recs, fails = reconcile_netted_fills(
    adj, get_net_fill=fillmap({}), ref_price_of=refmap({"HPG": 26_000}),
    broker_net_delta={"HPG": 0})
check("không failure", not fails, str(fails))
r = recs[0]
check("net_to_broker = 0", r["net_to_broker"] == 0)
check("giá dùng = ref 26.000", r["price"] == 26_000)
check("price_source ghi rõ NET=0 no market leg", "NET=0" in r["price_source"], r["price_source"])
check("2 leg 700 mua & 700 bán @ 26.000 → bù trừ",
      r["buy_legs"][0]["qty"] == 700 and r["sell_legs"][0]["qty"] == 700
      and r["buy_legs"][0]["price"] == 26_000 and r["sell_legs"][0]["price"] == 26_000)
check("Σ book chạm-TT == 0", market_delta(recs) == 0)

# ── C. FAIL LOUD: NET≠0 khớp nhưng KHÔNG lấy được giá khớp thật ────────────────────────
print("\nC. FAIL LOUD — NET≠0 khớp 100cp nhưng avg_price=None")
_, adj = net_offsetting_orders(mkplan([
    order("VPB", "sell", 800, book="custom30V_parking", pri=1),
    order("VPB", "buy", 700, book="LAG", pri=2),
]))
recs, fails = reconcile_netted_fills(
    adj, get_net_fill=fillmap({"VPB": (100, None)}), ref_price_of=refmap({"VPB": 24_900}))
check("có đúng 1 failure", len(fails) == 1, str(fails))
check("failure nói về giá khớp thật", fails and "giá khớp thật" in fails[0]["reason"])
check("KHÔNG ghi record khi fail", len(recs) == 0)

# ── D. FAIL LOUD: broker delta bất nhất với phần net theo fill ─────────────────────────
print("\nD. FAIL LOUD — fill nói net -100 nhưng vị thế broker đổi -300 (Σbook ≠ broker)")
_, adj = net_offsetting_orders(mkplan([
    order("VPB", "sell", 800, book="custom30V_parking", pri=1),
    order("VPB", "buy", 700, book="LAG", pri=2),
]))
recs, fails = reconcile_netted_fills(
    adj, get_net_fill=fillmap({"VPB": (100, 24_850)}), ref_price_of=refmap({"VPB": 24_900}),
    broker_net_delta={"VPB": -300})
check("có đúng 1 failure", len(fails) == 1, str(fails))
check("failure nói Σ(book) ≠ broker", fails and "Σ(book) ≠ broker" in fails[0]["reason"])
check("KHÔNG ghi record khi fail", len(recs) == 0)

# ── E. Khớp MỘT PHẦN — không FAIL giả (net SELL 100 chỉ khớp 60) ───────────────────────
print("\nE. Khớp một phần: NET SELL 100 chỉ khớp 60cp @ 24.800, broker đổi -60")
_, adj = net_offsetting_orders(mkplan([
    order("VPB", "sell", 800, book="custom30V_parking", pri=1),
    order("VPB", "buy", 700, book="LAG", pri=2),
]))
recs, fails = reconcile_netted_fills(
    adj, get_net_fill=fillmap({"VPB": (60, 24_800)}), ref_price_of=refmap({"VPB": 24_900}),
    broker_net_delta={"VPB": -60})
check("không failure (partial hợp lệ)", not fails, str(fails))
check("net_to_broker = -60", recs[0]["net_to_broker"] == -60)
check("Σ book chạm-TT == -60 == broker delta", market_delta(recs) == -60)

# ── F. FAIL LOUD: NET=0 nhưng thiếu ref price ─────────────────────────────────────────
print("\nF. FAIL LOUD — NET=0 nhưng không lấy được ref price để định giá nội bộ")
_, adj = net_offsetting_orders(mkplan([
    order("HPG", "sell", 700, book="custom30V_parking", pri=1),
    order("HPG", "buy", 700, book="LAG", pri=2),
]))
recs, fails = reconcile_netted_fills(
    adj, get_net_fill=fillmap({}), ref_price_of=refmap({}))  # ref rỗng
check("có đúng 1 failure", len(fails) == 1, str(fails))
check("failure nói về giá tham chiếu", fails and "giá tham chiếu" in fails[0]["reason"])

# ── G. FAIL LOUD: NET=0 nhưng vị thế broker lại đổi (ghost) ────────────────────────────
print("\nG. FAIL LOUD — NET=0 (0 lệnh ra broker) nhưng broker đổi -700cp (ghost)")
_, adj = net_offsetting_orders(mkplan([
    order("HPG", "sell", 700, book="custom30V_parking", pri=1),
    order("HPG", "buy", 700, book="LAG", pri=2),
]))
recs, fails = reconcile_netted_fills(
    adj, get_net_fill=fillmap({}), ref_price_of=refmap({"HPG": 26_000}),
    broker_net_delta={"HPG": -700})
check("có đúng 1 failure", len(fails) == 1, str(fails))
check("failure nói vị thế broker đổi dù 0 lệnh", fails and "vị thế broker đổi" in fails[0]["reason"])

# ── H. NET≠0 bên MUA lớn (net BUY) — dấu net_to_broker & cross-check dương ─────────────
print("\nH. NET BUY: BUY 800 LAG + SELL 700 park → NET BUY 100, khớp đủ @ 24.700, broker +100")
_, adj = net_offsetting_orders(mkplan([
    order("VPB", "buy", 800, book="LAG", pri=2),
    order("VPB", "sell", 700, book="custom30V_parking", pri=1),
]))
check("adj net BUY", adj[0]["net_side"] == "buy" and adj[0]["net_qty"] == 100)
recs, fails = reconcile_netted_fills(
    adj, get_net_fill=fillmap({"VPB": (100, 24_700)}), ref_price_of=refmap({"VPB": 24_900}),
    broker_net_delta={"VPB": 100})
check("không failure", not fails, str(fails))
check("net_to_broker = +100 (mua)", recs[0]["net_to_broker"] == 100)
check("Σ book chạm-TT == +100", market_delta(recs) == 100)

# ── I. Lệnh net khớp 0cp — định giá @ ref, không fail, 0 chạm broker ───────────────────
print("\nI. NET≠0 nhưng lệnh net khớp 0cp (chưa ai khớp) → @ref, net_to_broker 0")
_, adj = net_offsetting_orders(mkplan([
    order("VPB", "sell", 800, book="custom30V_parking", pri=1),
    order("VPB", "buy", 700, book="LAG", pri=2),
]))
recs, fails = reconcile_netted_fills(
    adj, get_net_fill=fillmap({"VPB": (0, None)}), ref_price_of=refmap({"VPB": 24_900}),
    broker_net_delta={"VPB": 0})
check("không failure", not fails, str(fails))
check("net_to_broker = 0 (chưa khớp)", recs[0]["net_to_broker"] == 0)
check("giá @ ref 24.900", recs[0]["price"] == 24_900)
check("price_source ghi 0-filled", "0-filled" in recs[0]["price_source"], recs[0]["price_source"])

# ── J. adj hỏng (total_buy - total_sell ≠ net_qty) → FAIL LOUD ─────────────────────────
print("\nJ. FAIL LOUD — adj bị sửa hỏng: net_qty không khớp total_buy-total_sell")
bad_adj = [{"ticker": "VPB", "action": "NETTED", "net_side": "sell",
            "total_buy": 700, "total_sell": 800, "net_qty": -50, "internal_qty": 700,
            "buy_legs": [{"book": "LAG", "qty": 700, "note": ""}],
            "sell_legs": [{"book": "custom30V_parking", "qty": 800, "note": ""}]}]
recs, fails = reconcile_netted_fills(
    bad_adj, get_net_fill=fillmap({"VPB": (50, 24_850)}), ref_price_of=refmap({"VPB": 24_900}))
check("có đúng 1 failure", len(fails) == 1, str(fails))
check("failure nói adj hỏng", fails and "adj hỏng" in fails[0]["reason"])

# ── K. write_recon_log: atomic JSONL, append, records rỗng → None ─────────────────────
print("\nK. write_recon_log — ghi JSONL atomic + append + rỗng trả None")
import tempfile  # noqa: E402
import json as _json  # noqa: E402
tmpd = tempfile.mkdtemp(prefix="recon_selfcheck_")
_, adj = net_offsetting_orders(mkplan([
    order("VPB", "sell", 800, book="custom30V_parking", pri=1),
    order("VPB", "buy", 700, book="LAG", pri=2),
]))
recs, _ = reconcile_netted_fills(
    adj, get_net_fill=fillmap({"VPB": (100, 24_850)}), ref_price_of=refmap({"VPB": 24_900}),
    broker_net_delta={"VPB": -100})
p1 = write_recon_log(recs, "selfcheck_recon", "2026-07-27", tmpd)
check("ghi ra path", p1 and os.path.exists(p1))
with open(p1, encoding="utf-8") as f:
    lines = [l for l in f if l.strip()]
check("1 dòng JSONL", len(lines) == 1)
check("dòng parse được + ticker đúng", _json.loads(lines[0])["ticker"] == "VPB")
p2 = write_recon_log(recs, "selfcheck_recon", "2026-07-27", tmpd)  # append lần 2
with open(p2, encoding="utf-8") as f:
    lines2 = [l for l in f if l.strip()]
check("append → 2 dòng", len(lines2) == 2)
check("records rỗng → None", write_recon_log([], "selfcheck_recon", "2026-07-27", tmpd) is None)
import shutil  # noqa: E402
shutil.rmtree(tmpd, ignore_errors=True)

# ── L. TÍCH HỢP journal THẬT: get_net_fill_from_journal lấy avg_price, KHÔNG giá đặt lệnh ──
# quant-skeptic (job Taylor_20260727_040719) yêu cầu: feed 1 dòng journal FILL thật (parent
# NET-<ticker>-<SIDE>) qua get_net_fill để CHỨNG MINH avg_price (không phải c["price"]) là nguồn.
print("\nL. Integration — FILL row THẬT trong journal executor: giá = avg_price broker, không giá đặt")
import csv as _csv  # noqa: E402
tmpd_j = tempfile.mkdtemp(prefix="recon_journal_")
_HDR = ["ts", "event", "parent_id", "ticker", "side", "child_oid", "qty", "price",
        "filled_total", "note"]  # đúng header executor._journal ghi


def write_journal(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = _csv.writer(f)
        w.writerow(_HDR)
        for r in rows:
            w.writerow(r)


jpath = os.path.join(tmpd_j, "exec_scL_journal.csv")
# giá ĐẶT LỆNH (PLACE) = 24.900; giá KHỚP THẬT (FILL avg_price) = 24.850 → phải lấy 24.850.
write_journal(jpath, [
    ["2026-07-27T09:20:00", "PLACE", "NET-VPB-SELL", "VPB", "sell", "ORD1", 100, 24_900, 0, "đặt"],
    ["2026-07-27T09:22:00", "FILL", "NET-VPB-SELL", "VPB", "sell", "ORD1", 100, 24_850, 100, ""],
    # nhiễu: event khác + parent khác KHÔNG được tính vào
    ["2026-07-27T09:22:00", "FILL", "BUY-HPG-02", "HPG", "buy", "ORDX", 500, 26_000, 500, ""],
])
filled, avg = get_net_fill_from_journal(jpath, "VPB", "sell")
check("journal: filled = 100", filled == 100, str(filled))
check("journal: avg_price = 24.850 (avg_price broker, KHÔNG phải 24.900 giá đặt)",
      avg == 24_850, str(avg))
# feed qua reconcile_netted_fills với READER THẬT (không mock) → record giá phải là 24.850
_, adj = net_offsetting_orders(mkplan([
    order("VPB", "sell", 800, px=24_900, book="custom30V_parking", pri=1),
    order("VPB", "buy", 700, px=24_900, book="LAG", pri=2),
]))
recs, fails = reconcile_netted_fills(
    adj, get_net_fill=lambda tk, side: get_net_fill_from_journal(jpath, tk, side),
    ref_price_of=refmap({"VPB": 24_900}))
check("integration: không failure", not fails, str(fails))
check("integration: record giá = 24.850 (từ journal FILL, KHÔNG phải ref/đặt 24.900)",
      recs and recs[0]["price"] == 24_850, str(recs[0]["price"] if recs else None))
check("integration: cả 2 leg định giá @ 24.850",
      recs and recs[0]["buy_legs"][0]["price"] == 24_850
      and recs[0]["sell_legs"][0]["price"] == 24_850)

# ── M. TÍCH HỢP journal THẬT: khớp MỘT PHẦN qua code path thật (không false-fail) ──
print("\nM. Integration — NET SELL 100 chỉ khớp 60cp (cumulative) trong journal thật → partial")
jpath2 = os.path.join(tmpd_j, "exec_scM_journal.csv")
# cùng child, cumulative tăng dần 30 → 60: dòng cuối (60) thắng, KHÔNG cộng dồn thành 90.
write_journal(jpath2, [
    ["2026-07-27T09:21:00", "FILL", "NET-VPB-SELL", "VPB", "sell", "ORD1", 30, 24_800, 30, ""],
    ["2026-07-27T09:25:00", "FILL", "NET-VPB-SELL", "VPB", "sell", "ORD1", 60, 24_800, 60, ""],
])
filled2, avg2 = get_net_fill_from_journal(jpath2, "VPB", "sell")
check("journal partial: filled = 60 (cumulative dòng cuối, không cộng 30+60)", filled2 == 60, str(filled2))
check("journal partial: avg = 24.800", avg2 == 24_800, str(avg2))
_, adj = net_offsetting_orders(mkplan([
    order("VPB", "sell", 800, px=24_900, book="custom30V_parking", pri=1),
    order("VPB", "buy", 700, px=24_900, book="LAG", pri=2),
]))
recs, fails = reconcile_netted_fills(
    adj, get_net_fill=lambda tk, side: get_net_fill_from_journal(jpath2, tk, side),
    ref_price_of=refmap({"VPB": 24_900}))
check("integration partial: không false-fail (60 ∈ [0,100])", not fails, str(fails))
check("integration partial: net_to_broker = -60", recs and recs[0]["net_to_broker"] == -60,
      str(recs[0]["net_to_broker"] if recs else None))
check("integration partial: giá = 24.800 (avg khớp thật)", recs and recs[0]["price"] == 24_800)

# ── N. TÍCH HỢP journal THẬT: bình quân gia quyền qua NHIỀU child ──
print("\nN. Integration — 2 child khớp giá khác nhau → avg_price gia quyền theo qty")
jpath3 = os.path.join(tmpd_j, "exec_scN_journal.csv")
write_journal(jpath3, [
    ["2026-07-27T09:20:00", "FILL", "NET-VPB-SELL", "VPB", "sell", "ORD1", 40, 24_800, 40, ""],
    ["2026-07-27T09:24:00", "FILL", "NET-VPB-SELL", "VPB", "sell", "ORD2", 60, 24_900, 100, ""],
])
filled3, avg3 = get_net_fill_from_journal(jpath3, "VPB", "sell")
check("journal 2-child: filled = 100 (40+60)", filled3 == 100, str(filled3))
check("journal 2-child: avg gia quyền = 24.860 ((40·24800+60·24900)/100)", avg3 == 24_860, str(avg3))
# không có journal / parent không tồn tại → (0, None), không crash
check("journal thiếu file → (0,None)", get_net_fill_from_journal(
    os.path.join(tmpd_j, "khong_ton_tai.csv"), "VPB", "sell") == (0, None))
check("parent không có FILL → (0,None)", get_net_fill_from_journal(jpath3, "HPG", "buy") == (0, None))
shutil.rmtree(tmpd_j, ignore_errors=True)

# ── Tổng kết ──────────────────────────────────────────────────────────────────────────
print(f"\n{'='*70}")
if FAILS:
    print(f"❌ {len(FAILS)}/{NCHECK[0]} FAIL: {FAILS}")
    sys.exit(1)
print(f"✅ TẤT CẢ PASS ({NCHECK[0]}/{NCHECK[0]})")
