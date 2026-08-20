#!/usr/bin/env python3
"""Selfcheck cho `compute_jit_unpark.py` (L2 JIT unpark).

Chạy THẬT, không mock nửa vời: mọi test bơm `holdings`/`orders`/`adv_fn`/`day_cap_override`/
`share_override` nên KHÔNG chạm DNSE, KHÔNG chạm BQ, KHÔNG cần bootstrap snapshot ⇒ tái lập
được ở bất kỳ máy nào, bất kỳ giờ nào.

MA TRẬN TZ (§16 + skill `verify-before-done`): file tự spawn lại chính nó dưới 4 môi trường
`env -u TZ` / ICT / UTC / America/New_York rồi so DIGEST — một selfcheck thừa hưởng TZ đúng của
tác giả thì pass bất kể code có neo TZ hay không, nên phải so chéo môi trường mới có giá trị.

    python3 mike/bin/compute_jit_unpark_selfcheck.py           # đủ: tests + ma trận TZ
    JIT_SC_CHILD=1 python3 ... compute_jit_unpark_selfcheck.py # chỉ chạy tests (dùng nội bộ)
"""
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from compute_jit_unpark import (compute_jit_unpark, allocate, trigger_orders,  # noqa: E402
                                JIT_TRIGGER_FRAC, SHRINK_FRAC, MIN_ORDER_VND,
                                ETF_FRICTION, LOT, LAG_ADV_PCT)
from park_holdings import today_ict                                            # noqa: E402

FAILS, PASSES, DIGEST_PARTS = [], [], []


def check(name, cond, detail=""):
    (PASSES if cond else FAILS).append(name)
    print(f"  {'✅' if cond else '❌'} {name}" + (f" — {detail}" if detail else ""))


def digest(name, obj):
    """Ghi kết quả vào digest để so chéo giữa các TZ."""
    DIGEST_PARTS.append(name + "=" + json.dumps(obj, sort_keys=True, default=str))


def close(a, b, tol=1.0):
    return abs(float(a) - float(b)) <= tol


# ───────────────────────────────────────────────────────── dữ liệu tổng hợp

def mk_holdings(park=(("AAA", 1000, 50_000), ("BBB", 2000, 25_000), ("CCC", 500, 100_000)),
                cash=0.0, excluded=(), unverified=(), reconcile_ok=True,
                sellable=None, extra_books=(), leak_capit_into_park=False, egg=0.0):
    """holdings giả lập ĐÚNG hợp đồng của `park_holdings()`.

    `park`: (ticker, qty, price) — mỗi mã chia 2 lô để kiểm FIFO.
    `extra_books`: (ticker, book, qty, price) — lô sổ KHÁC (CAPIT/LAG/...) để chứng minh L2
    không thể chạm tới (chúng KHÔNG nằm trong `park_lots`).
    """
    park_lots, positions = [], {}
    for tk, qty, px in park:
        q1 = (qty // 2 // LOT) * LOT
        q2 = qty - q1
        for i, q in enumerate((q1, q2)):
            if q <= 0:
                continue
            park_lots.append({"ticker": tk, "book": "PARK", "play_type": "NEUTRAL_park",
                              "entry_date": f"2026-0{6 + i}-15", "qty": q, "price": px * 0.9,
                              "source": f"lot{i}", "market_price": px, "mv_vnd": q * px})
        positions[tk] = {"qty": qty, "market_price": px,
                         "sellable": qty if sellable is None else sellable.get(tk, qty)}
    other = []
    for tk, book, qty, px in extra_books:
        lot = {"ticker": tk, "book": book, "play_type": book, "entry_date": "2026-05-01",
               "qty": qty, "price": px, "source": "other", "market_price": px, "mv_vnd": qty * px}
        other.append(lot)
        positions.setdefault(tk, {"qty": qty, "market_price": px, "sellable": qty})
        if leak_capit_into_park:
            park_lots.append(lot)
    return {"account_label": "SC", "asof": "2026-08-06",
            "park_lots": park_lots, "lots": park_lots + other,
            "broker_positions": positions,
            "park_mv_vnd": sum(l["mv_vnd"] for l in park_lots if l["book"] == "PARK"),
            "cash_available_vnd": cash, "egg_assets_vnd": egg,
            "excluded_tickers": sorted(excluded), "unverified_tickers": sorted(unverified),
            "reconcile": {"ok": reconcile_ok, "mismatches": []
                          if reconcile_ok else [{"ticker": "AAA", "diff": -100}]}}


def buy(ticker, qty, px, book="LAG", oid=None, priority=10, play="LAG_HI"):
    return {"id": oid or f"BUY-{ticker}", "ticker": ticker, "side": "buy", "qty": qty,
            "ref_price": px, "book": book, "play_type": play, "priority": priority}


ADV_BIG = lambda tk, asof: (50_000_000_000.0, asof, None)          # noqa: E731 — trần rộng
ADV_ERR = lambda tk, asof: (None, None, "không có dữ liệu")        # noqa: E731
ADV_STALE = lambda tk, asof: (50e9, "2026-05-01", None)            # noqa: E731 — cũ 97 ngày
ADV_ZERO = lambda tk, asof: (0.0, asof, None)                      # noqa: E731

BASE = dict(asof="2026-08-06", share_override=0.5, adv_fn=ADV_BIG,
            day_cap_override=5_000_000_000.0)


def run(holdings, orders, **kw):
    a = dict(BASE)
    a.update(kw)
    return compute_jit_unpark("SC", holdings=holdings, orders=orders, **a)


# ─────────────────────────────────────────────────────────────────── các test

def t01_cash_du():
    h = mk_holdings(cash=200_000_000)
    r = run(h, [buy("FPT", 1000, 100_000)])          # target 100tr, cash 200tr
    check("T01 cash đủ ⇒ NO_JIT_NEEDED, không bán gì",
          r["decision"] == "NO_JIT_NEEDED" and not r["orders"]
          and r["buy_amendments"][0]["status"] == "FUNDED_BY_CASH"
          and r["cash_end_vnd"] == 100_000_000,
          f"decision={r['decision']} cash_end={r['cash_end_vnd']:,.0f}")
    digest("t01", [r["decision"], r["orders"], r["cash_end_vnd"]])


def t01b_biên_099():
    """Ngưỡng đúng 0,99: cash = 0,99×target ⇒ KHÔNG trigger; nhỏ hơn 1đ ⇒ trigger."""
    tv = 100_000_000
    r_eq = run(mk_holdings(cash=tv * JIT_TRIGGER_FRAC), [buy("FPT", 1000, 100_000)])
    r_lt = run(mk_holdings(cash=tv * JIT_TRIGGER_FRAC - 1), [buy("FPT", 1000, 100_000)])
    check("T01b biên 0,99 — cash = 0,99×target ⇒ KHÔNG trigger JIT",
          r_eq["decision"] == "NO_JIT_NEEDED" and "needed_vnd" not in r_eq["buy_amendments"][0],
          f"{r_eq['decision']}")
    check("T01b2 thiếu 1đ so với biên ⇒ trigger, needed = (target − cash)/(1 − friction)",
          abs(r_lt["buy_amendments"][0].get("needed_vnd")
              - (tv - (tv * JIT_TRIGGER_FRAC - 1)) / (1 - ETF_FRICTION)) < 1e-6
          and r_lt["decision"] == "JIT",
          f"{r_lt['decision']} needed={r_lt['buy_amendments'][0].get('needed_vnd'):,.0f}")
    # ⚠️ Phương án (C) đã áp (2026-08-06): `needed` ~1,0tr < 1 lô rẻ nhất (2,5tr) nên trước đây ra
    # NO_SELL_POSSIBLE và lệnh mua co 1000→900cp (mất 10tr vì thiếu ĐÚNG 1 đồng). Nay làm tròn LÊN
    # 1 lô BBB ⇒ mua ĐỦ. Đây chính là hành vi user duyệt: bán dư ≤ 1 lô để không mất trọn lô mua.
    m_eq, m_lt = r_eq["buy_amendments"][0], r_lt["buy_amendments"][0]
    check("T01b3 không trigger ⇒ vẫn CO theo sức mua thật; trigger + (C) ⇒ mua ĐỦ nguyên lệnh",
          m_eq["status"] == "SHRINK" and 0 < m_eq["qty_final"] < 1000
          and m_lt["status"] == "FUNDED_BY_JIT" and m_lt["qty_final"] == 1000,
          f"r_eq {m_eq['status']} {m_eq['qty_final']}cp / r_lt {m_lt['status']} "
          f"{m_lt['qty_final']}cp (bán dư {r_lt['jit_sell_total_vnd'] - m_lt['needed_vnd']:,.0f}đ)")
    digest("t01b", [r_eq["decision"], r_lt["decision"], m_eq["qty_final"], m_lt["qty_final"],
                    round(r_lt["jit_sell_total_vnd"], 6)])


def t02_thieu_mot_phan():
    """cash thiếu một phần ⇒ bán đủ `needed` (làm tròn LÊN ≤ 1 lô), lệnh mua nguyên vẹn."""
    h = mk_holdings(cash=60_000_000)
    r = run(h, [buy("FPT", 1000, 100_000)])          # target 100tr, thiếu 40tr
    m = r["buy_amendments"][0]
    gross = r["jit_sell_total_vnd"]
    need_exp = 40_000_000 / (1 - ETF_FRICTION)
    cheapest = LOT * min(50_000, 25_000, 100_000)    # rổ AAA/BBB/CCC ⇒ 1 lô rẻ nhất = 2,5tr
    # ⚠️ Bất biến ĐÃ ĐỔI (phương án C, 2026-08-06): trước đây `Σ bán ≤ needed` (làm tròn XUỐNG);
    # nay `needed ≤ Σ bán < needed + 1 lô rẻ nhất`. Cận trên vẫn CHẶT — không phải "bán tuỳ ý".
    check("T02 thiếu 40tr ⇒ needed = (target − cash)/(1 − friction); needed ≤ Σ bán < needed+1 lô",
          r["decision"] == "JIT" and abs(m["needed_vnd"] - need_exp) < 1
          and gross >= need_exp - 1e-6 and gross < need_exp + cheapest,
          f"needed={m['needed_vnd']:,.0f} gross={gross:,.0f} (dư {gross - need_exp:,.0f}đ "
          f"< 1 lô {cheapest:,.0f}đ) status={m['status']}")
    # (B) đã khử hụt do PHÍ; (C) khử nốt hụt do RỜI RẠC LÔ BÁN ⇒ lệnh mua giữ NGUYÊN 1000cp thay vì
    # co còn 900cp (mất 10tr) như trước. Sức mua sau JIT phải ≥ target — đó là mục tiêu của (C).
    check("T02a1 (C) ⇒ lệnh mua KHÔNG còn bị co: mua đủ 1000cp, sức mua ≥ target",
          m["status"] == "FUNDED_BY_JIT" and m["qty_final"] == m["qty_plan"] == 1000
          and m["buying_power_vnd"] >= m["target_value_vnd"] - 1e-6
          and abs((m["cash_before_vnd"] + m["jit_proceeds_net_vnd"])
                  - m["buying_power_vnd"]) < 1e-6,
          f"qty {m['qty_plan']}→{m['qty_final']}, sức mua {m['buying_power_vnd']:,.0f} vs "
          f"target {m['target_value_vnd']:,.0f}")
    check("T02b thu ròng = gross × (1 − friction)",
          abs(m["jit_proceeds_net_vnd"] - gross * (1 - ETF_FRICTION)) < 1e-6,
          f"net={m['jit_proceeds_net_vnd']:,.2f}")
    check("T02c pro-rata: bán ≥2 mã, KHÔNG bán sạch mã nào (giữ cấu trúc rổ)",
          len(r["sells_by_ticker"]) >= 2
          and all(r["sells_by_ticker"][tk] < h["broker_positions"][tk]["qty"]
                  for tk in r["sells_by_ticker"]),
          str(r["sells_by_ticker"]))
    lots = [o["fifo_lots"] for o in r["orders"]]
    check("T02d FIFO trong mã: lô entry_date cũ nhất bị tiêu thụ trước",
          all(fl == sorted(fl, key=lambda x: x["entry_date"]) and fl[0]["entry_date"] <= fl[-1]["entry_date"]
              for fl in lots if fl),
          str([[l["entry_date"] for l in fl] for fl in lots]))
    digest("t02", [r["decision"], r["sells_by_ticker"], round(gross, 6)])


def t03_thieu_hon_daycap():
    """needed bị trần TỔNG/phiên cắt ⇒ carry-over, lệnh mua bị CO (đúng engine, live thì defer)."""
    h = mk_holdings(park=(("AAA", 100000, 50_000), ("BBB", 100000, 25_000)), cash=0)
    r = run(h, [buy("FPT", 10000, 100_000)], day_cap_override=200_000_000.0)
    m = r["buy_amendments"][0]
    exp_tv = m["jit_proceeds_net_vnd"] * SHRINK_FRAC
    check("T03 needed cắt bởi trần TỔNG/phiên (200tr < 1 tỷ cần)",
          abs(m["needed_vnd"] - 200_000_000) < 1 and m["day_cap_binding"] is True,
          f"needed={m['needed_vnd']:,.0f}")
    check("T03b lệnh mua bị CO đúng công thức (cash+margin)×0,95, KHÔNG defer nguyên lệnh",
          m["status"] == "SHRINK" and 0 < m["qty_final"] < 10000
          and abs(m["qty_final"] * 100_000 - (exp_tv // (100_000 * LOT)) * 100_000 * LOT) < 1,
          f"status={m['status']} qty {m['qty_plan']}→{m['qty_final']} tv={exp_tv:,.0f}")
    check("T03c trần còn lại cuối kỳ = trần − đã bán (carry-over sang phiên sau)",
          abs(r["etf_day_cap_remaining_end_vnd"]
              - (200_000_000 - r["jit_sell_total_vnd"])) < 1e-6,
          f"còn {r['etf_day_cap_remaining_end_vnd']:,.0f}")
    digest("t03", [m["status"], m["qty_final"], round(r["jit_sell_total_vnd"], 6)])


def t04_excluded():
    h = mk_holdings(park=(("DGC", 5000, 100_000), ("BBB", 5000, 25_000)), cash=0,
                    excluded=("DGC",))
    r = run(h, [buy("FPT", 1000, 100_000)])
    check("T04 excluded_tickers (DGC) KHÔNG bao giờ bị bán",
          "DGC" not in r["sells_by_ticker"]
          and any(b["ticker"] == "DGC" and "excluded" in b["reason"] for b in r["blocked"]),
          str(r["sells_by_ticker"]))
    digest("t04", [r["sells_by_ticker"], r["blocked"]])


def t05_capit_khong_dung():
    """Vị thế CAPIT/LAG/BAL không nằm trong park_lots ⇒ cấu trúc không thể chạm tới."""
    h = mk_holdings(park=(("AAA", 5000, 50_000),), cash=0,
                    extra_books=(("SAB", "CAPIT", 3000, 60_000), ("MST", "LAG", 1000, 20_000),
                                 ("HPG", "BAL", 2000, 30_000)))
    r = run(h, [buy("FPT", 1000, 100_000)])
    touched = set(r["sells_by_ticker"])
    check("T05 CAPIT (stop_exempt/slot_exempt) + LAG + BAL KHÔNG bị đụng",
          touched == {"AAA"} and not (touched & {"SAB", "MST", "HPG"}), str(touched))
    r2 = run(mk_holdings(park=(("AAA", 5000, 50_000),), cash=0,
                         extra_books=(("SAB", "CAPIT", 3000, 60_000),),
                         leak_capit_into_park=True),
             [buy("FPT", 1000, 100_000)])
    check("T05b bất biến: lô KHÔNG-PARK lọt vào park_lots ⇒ fail-closed, không bán gì",
          r2["decision"] == "BLOCKED_BOOK_INVARIANT" and not r2["orders"], r2["decision"])
    digest("t05", [sorted(touched), r2["decision"]])


def t06_unverified():
    h = mk_holdings(cash=0, unverified=("AAA",))
    r = run(h, [buy("FPT", 1000, 100_000)])
    check("T06 ticker UNVERIFIED không sinh lệnh bán (§21)",
          "AAA" not in r["sells_by_ticker"]
          and any(b["ticker"] == "AAA" and "UNVERIFIED" in b["reason"] for b in r["blocked"]),
          str(r["sells_by_ticker"]))
    digest("t06", [r["sells_by_ticker"]])


def t07_reconcile():
    r = run(mk_holdings(cash=0, reconcile_ok=False), [buy("FPT", 1000, 100_000)])
    check("T07 sổ lệch broker ⇒ BLOCKED_RECONCILE, 0 đề xuất",
          r["decision"] == "BLOCKED_RECONCILE" and not r["orders"], r["decision"])
    digest("t07", [r["decision"]])


def t08_no_trigger():
    h = mk_holdings(cash=0)
    orders = [buy("BID", 1000, 40_000, book="custom30V_parking", play="NEUTRAL_park"),
              buy("SAB", 500, 60_000, book="CAPIT", play="CAPIT_GOLDEN"),
              {"id": "SELL-AAA", "ticker": "AAA", "side": "sell", "qty": 100,
               "ref_price": 50_000, "book": "LAG"}]
    r = run(h, orders)
    check("T08 chỉ có lệnh PARK/CAPIT/bán ⇒ NO_TRIGGER (L2 chỉ chạy khi có MUA BAL/LAG)",
          r["decision"] == "NO_TRIGGER" and not r["orders"], r["decision"])
    r2 = run(h, [buy("HPG", 1000, 30_000, book="BAL", play="MOMENTUM")])
    check("T08b lệnh mua book BAL cũng là trigger (không chỉ LAG)",
          r2["decision"] == "JIT" and bool(r2["orders"]), r2["decision"])
    digest("t08", [r["decision"], r2["decision"]])


def t09_drop_duoi_1tr():
    """Sức mua sau JIT < 1tr ⇒ engine BỎ lệnh (dòng 1195)."""
    h = mk_holdings(park=(("AAA", 100, 5_000),), cash=0)      # PARK chỉ 500k
    r = run(h, [buy("FPT", 1000, 100_000)], day_cap_override=400_000.0)
    m = r["buy_amendments"][0]
    check("T09 sau JIT vẫn < 1tr ⇒ DROP lệnh mua",
          m["status"] == "DROP" and m["qty_final"] == 0
          and m["target_value_final_vnd"] < MIN_ORDER_VND, f"{m['status']} {m['reason'][:60]}")
    digest("t09", [m["status"], m["qty_final"]])


def t10_chia_tran_voi_l1():
    """L1 và L2 tiêu chung trần TỔNG + trần per-name + cùng số cp vật lý."""
    h = mk_holdings(park=(("AAA", 10000, 50_000), ("BBB", 10000, 25_000)), cash=0)
    l1 = {"orders": [{"ticker": "AAA", "qty": 9900, "value_vnd": 495_000_000.0}]}
    r = run(h, [buy("FPT", 1000, 100_000)], l1_result=l1)
    check("T10 trần TỔNG trừ trước phần L1 đã đề xuất",
          abs(r["etf_day_cap_remaining_start_vnd"]
              - (5_000_000_000.0 - 495_000_000.0)) < 1e-6,
          f"{r['etf_day_cap_remaining_start_vnd']:,.0f}")
    check("T10b không bán trùng cp L1 đã lấy: L1 9.900 + L2 ≤ 100 = tổng ≤ 10.000 đang giữ",
          9900 + r["sells_by_ticker"].get("AAA", 0) <= 10000, str(r["sells_by_ticker"]))
    l1b = {"orders": [{"ticker": "AAA", "qty": 9950, "value_vnd": 497_500_000.0}]}
    rb = run(h, [buy("FPT", 1000, 100_000)], l1_result=l1b)
    check("T10c phần còn lại < 1 lô ⇒ chặn hẳn mã đó, nêu rõ lý do L1",
          rb["sells_by_ticker"].get("AAA", 0) == 0
          and any(b["ticker"] == "AAA" and "L1" in b["reason"] for b in rb["blocked"]),
          str(rb["sells_by_ticker"]))
    # Trần per-name cũng phải trừ phần L1: ADV nhỏ + L1 đã ăn hết trần ⇒ L2 không còn gì.
    adv_small = lambda tk, asof: (30_000_000.0, asof, None)     # noqa: E731 → cap 3tr/mã
    rc = run(h, [buy("FPT", 1000, 100_000)], adv_fn=adv_small,
             l1_result={"orders": [{"ticker": "AAA", "qty": 60, "value_vnd": 3_000_000.0}]})
    check("T10d trần per-name (ADV) cũng trừ phần L1 đã dùng",
          rc["sells_by_ticker"].get("AAA", 0) == 0, str(rc["sells_by_ticker"]))
    digest("t10", [r["sells_by_ticker"], rb["sells_by_ticker"], rc["sells_by_ticker"],
                   round(r["etf_day_cap_remaining_start_vnd"], 6)])


def t11_tran_per_name_va_t2():
    """Trần ADV per-name và ràng buộc T+2 (`sellable`) đều là trần CỨNG."""
    h = mk_holdings(park=(("AAA", 10000, 50_000), ("BBB", 10000, 25_000)), cash=0,
                    sellable={"AAA": 300, "BBB": 10000})
    r = run(h, [buy("FPT", 1000, 100_000)])
    check("T11 không bán quá `sellable` (cp chưa về T+2)",
          r["sells_by_ticker"].get("AAA", 0) <= 300, str(r["sells_by_ticker"]))
    # trần per-name = 0,20 × ADV × share; ADV nhỏ ⇒ cắt
    adv_small = lambda tk, asof: (10_000_000.0, asof, None)     # noqa: E731 → cap = 1tr
    r2 = run(h, [buy("FPT", 1000, 100_000)], adv_fn=adv_small)
    check("T11b trần per-name = LAG_ADV_PCT × ADV × share là trần cứng",
          all(v * (50_000 if tk == "AAA" else 25_000) <= 1_000_000 + 1e-6
              for tk, v in r2["sells_by_ticker"].items()), str(r2["sells_by_ticker"]))
    for name, fn, why in (("ADV lỗi", ADV_ERR, "không đo được ADV"),
                          ("ADV cũ", ADV_STALE, "cũ"), ("ADV≤0", ADV_ZERO, "ADV ≤ 0")):
        rr = run(h, [buy("FPT", 1000, 100_000)], adv_fn=fn)
        check(f"T11c fail-closed per-name khi {name}",
              not rr["orders"] and all(why in b["reason"] for b in rr["blocked"]),
              f"{rr['decision']} {[b['reason'][:30] for b in rr['blocked']]}")
    digest("t11", [r["sells_by_ticker"], r2["sells_by_ticker"]])


def t12_nhieu_lenh_tuan_tu():
    """Nhiều lệnh mua: theo priority, trần dùng chung, lệnh sau thấy cash đã đổi."""
    h = mk_holdings(park=(("AAA", 20000, 50_000), ("BBB", 20000, 25_000)), cash=0)
    orders = [buy("XXX", 1000, 100_000, oid="BUY-XXX", priority=20),
              buy("YYY", 1000, 100_000, oid="BUY-YYY", priority=10)]
    r = run(h, orders, day_cap_override=150_000_000.0)
    ids = [m["order_id"] for m in r["buy_amendments"]]
    check("T12 duyệt theo priority tăng dần (YYY p=10 trước XXX p=20)",
          ids == ["BUY-YYY", "BUY-XXX"], str(ids))
    check("T12b tổng bán ≤ trần TỔNG/phiên dùng chung cho MỌI lệnh",
          r["jit_sell_total_vnd"] <= 150_000_000 + 1e-6,
          f"{r['jit_sell_total_vnd']:,.0f}")
    check("T12c mã bán không vượt số đang giữ (tích luỹ qua nhiều lệnh)",
          all(q <= h["broker_positions"][tk]["qty"] for tk, q in r["sells_by_ticker"].items()),
          str(r["sells_by_ticker"]))
    digest("t12", [ids, r["sells_by_ticker"], round(r["jit_sell_total_vnd"], 6)])


def t13_so_hoc_tien():
    """Bảo toàn tiền: cash_end = cash_start + Σ thu ròng − Σ giá trị mua chốt lại."""
    h = mk_holdings(park=(("AAA", 20000, 50_000), ("BBB", 20000, 25_000)), cash=30_000_000)
    r = run(h, [buy("XXX", 1000, 100_000, oid="A", priority=1),
                buy("YYY", 800, 100_000, oid="B", priority=2)])
    net = sum(m["jit_proceeds_net_vnd"] for m in r["buy_amendments"])
    spent = sum(m["target_value_final_vnd"] if m["status"] != "SHRINK"
                else m["qty_final"] * m["ref_price"] for m in r["buy_amendments"])
    check("T13 bảo toàn tiền mặt qua toàn bộ chuỗi",
          abs(r["cash_end_vnd"] - (r["cash_start_vnd"] + net - spent)) < 1e-6,
          f"end={r['cash_end_vnd']:,.2f} vs {r['cash_start_vnd'] + net - spent:,.2f}")
    check("T13b Σ giá trị lệnh bán = Σ jit_sell_vnd của các lệnh mua",
          abs(sum(o["value_vnd"] for o in r["orders"])
              - sum(m["jit_sell_vnd"] for m in r["buy_amendments"])) < 1e-6)
    digest("t13", [round(r["cash_end_vnd"], 6)])


def t14_lam_tron_lo():
    """`needed` nhỏ hơn 1 lô của mọi mã ⇒ không đẻ lệnh rác; needed vừa đủ 1 lô ⇒ có lệnh."""
    h = mk_holdings(park=(("AAA", 10000, 50_000), ("BBB", 10000, 25_000)), cash=0)
    r0 = run(h, [buy("FPT", 1000, 100_000)], day_cap_override=1_000_000.0)   # < 1 lô rẻ nhất
    check("T14 needed < 1 lô ⇒ 0 lệnh bán (không lệnh lẻ), lệnh mua bị DROP",
          not r0["orders"] and r0["buy_amendments"][0]["status"] == "DROP",
          f"{r0['decision']}")
    r1 = run(h, [buy("FPT", 1000, 100_000)], day_cap_override=3_000_000.0)
    check("T14b needed = 3tr ⇒ largest-remainder vẫn đẻ được lệnh (không im lặng)",
          bool(r1["orders"]) and all(o["qty"] % LOT == 0 for o in r1["orders"])
          and r1["jit_sell_total_vnd"] <= 3_000_000 + 1e-6,
          f"{r1['sells_by_ticker']} Σ={r1['jit_sell_total_vnd']:,.0f}")
    px_map = {"AAA": 50_000, "BBB": 25_000}
    mkpool = lambda: {tk: {"px": px, "mv": px * 10000.0, "avail_qty": 10000,      # noqa: E731
                           "cap_remaining_vnd": 1e12, "sold_qty": 0}
                      for tk, px in px_map.items()}
    # ⚠️ Bất biến ĐÃ ĐỔI (C, 2026-08-06). CŨ: `Σ ≤ needed`. MỚI, hai vế đều phải giữ:
    #   (a) cận DƯỚI: Σ ≥ needed — TRỪ KHI hết dư địa (bán sạch mọi mã vẫn chưa đủ);
    #   (b) cận TRÊN: Σ < needed + 1 lô rẻ nhất — "bán dư tối đa 1 lô", KHÔNG phải bán tuỳ ý.
    cheapest = LOT * min(px_map.values())                       # 100cp × 25.000 = 2,5tr
    pool_mv = sum(px * 10000 for px in px_map.values())         # bán sạch được tối đa 750tr
    for needed in (0, 1, 24_999, 25_000, 3_000_000, 77_777_777, 999_999_999):
        a = allocate(needed, mkpool())
        tot = sum(q * px_map[tk] for tk, q in a.items())
        exhausted = tot >= pool_mv - 1e-6                       # hết dư địa ⇒ không thể tròn LÊN
        check(f"T14c allocate({needed:,}): needed ≤ Σ < needed+1 lô (hoặc hết dư địa), bội số lô",
              (tot >= needed - 1e-6 or exhausted)
              and tot < needed + cheapest
              and all(q % LOT == 0 and q > 0 for q in a.values()),
              f"Σ={tot:,.0f} (dư {tot - needed:,.0f}đ, 1 lô rẻ nhất {cheapest:,.0f}đ"
              + (", HẾT DƯ ĐỊA" if exhausted else "") + f") {a}")
    check("T14c2 ceiling là trần CỨNG: (C) KHÔNG thêm lô nếu vượt trần TỔNG/phiên",
          sum(q * px_map[tk] for tk, q in allocate(3_000_000, mkpool(),
                                                   ceiling=3_000_000).items()) <= 3_000_000 + 1e-6
          and sum(q * px_map[tk] for tk, q in allocate(1, mkpool(), ceiling=1).items()) == 0,
          f"ceiling=3tr ⇒ Σ={sum(q * px_map[tk] for tk, q in allocate(3_000_000, mkpool(), ceiling=3_000_000).items()):,.0f}")
    a3 = allocate(3_000_000, mkpool())
    check("T14d allocate xác định (chạy 2 lần y hệt)",
          a3 == allocate(3_000_000, mkpool()), str(a3))
    check("T14e (C) chọn lô RẺ NHẤT còn dư địa (BBB @25k, không phải AAA @50k)",
          allocate(1, mkpool()) == {"BBB": LOT}, str(allocate(1, mkpool())))
    digest("t14", [r0["decision"], r1["sells_by_ticker"], a3, allocate(1, mkpool())])


def t15_xac_dinh():
    h = mk_holdings(park=(("AAA", 10000, 50_000), ("BBB", 10000, 25_000),
                          ("CCC", 10000, 33_300)), cash=0)
    a = run(h, [buy("FPT", 1000, 100_000)])
    b = run(mk_holdings(park=(("AAA", 10000, 50_000), ("BBB", 10000, 25_000),
                              ("CCC", 10000, 33_300)), cash=0), [buy("FPT", 1000, 100_000)])
    check("T15 chạy lại cho kết quả y hệt (tie-break xác định)",
          json.dumps(a["sells_by_ticker"], sort_keys=True)
          == json.dumps(b["sells_by_ticker"], sort_keys=True), str(a["sells_by_ticker"]))
    digest("t15", [a["sells_by_ticker"]])


def t16_tz():
    """`today_ict()` phải neo ICT bất kể TZ của process (§16)."""
    exp = dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date().isoformat()
    check("T16 today_ict() = ngày ICT bất kể TZ process",
          today_ict() == exp, f"{today_ict()} vs {exp} (TZ={os.environ.get('TZ', '<unset>')})")
    # KHÔNG đưa vào digest: ngày thật đổi theo lúc chạy, không phải theo TZ.


def t17_khong_ghi_gi():
    """L2 CHỈ ĐỌC: không được sinh side-effect nào lên plan/journal."""
    import compute_jit_unpark as M
    src = open(M.__file__, encoding="utf-8").read()
    bad = [k for k in ("open(", "json.dump") if False]      # placeholder, kiểm tra cụ thể dưới
    writes = [ln.strip() for ln in src.splitlines()
              if ('open(' in ln and '"w"' in ln) or ("os.replace" in ln) or ("os.rename" in ln)]
    check("T17 chỉ ghi file khi người dùng truyền --out (không đụng plan/journal)",
          len(writes) == 1 and "a.out" in writes[0] and not bad, str(writes))
    digest("t17", [len(writes)])


def t18_grossup_va_lam_tron_len_3_muc_gia():
    """A/B/C trên ĐÚNG 3 mức giá đã đo trong báo cáo — hai nguồn làm lệnh mua hụt tiền, hai phương
    án, mỗi phương án khử đúng một nguồn:

      (1) **phí ma sát**   : bán `needed` chỉ thu về `needed×(1−f)`.  ← (B) gross-up khử
      (2) **rời rạc lô bán**: làm tròn XUỐNG lô nên `gross < needed`, dư tới gần 1 lô bán.
                                                                      ← (C) làm tròn LÊN khử

    Ba chân so trên CÙNG một rổ, dùng chính `allocate()` — KHÔNG cần checkout bản cũ:
      · A = tiền-(B): `needed_A = tv0 − cash`,   làm tròn XUỐNG
      · B = tiền-(C): `needed_B = needed_A/(1−f)`, làm tròn XUỐNG
      · C = HIỆN HÀNH: `needed_B`,                 làm tròn LÊN ≤ 1 lô
    Mẹo tái lập chân "làm tròn XUỐNG" mà không cần cờ riêng: `allocate(x, pool, ceiling=x)` —
    vòng largest-remainder dừng khi mọi lô còn lại đều đắt hơn phần dư, nên `ceiling=x` khiến lô
    làm tròn LÊN không bao giờ lọt ⇒ đúng bằng hành vi cũ. (Chính tính chất này là T14c2.)

    `gap = tv0 − sức mua`: **âm = dư**. Bất biến đại số giữ nguyên qua cả 3 chân (T18b):
        gap = (needed − gross) × (1 − friction)
    """
    from compute_jit_unpark import build_pool
    park = (("AAA", 4_000, 90_000), ("BBB", 6_000, 41_000), ("CCC", 9_000, 27_000),
            ("DDD", 12_000, 19_000), ("EEE", 20_000, 13_000))      # hình dạng rổ ngân hàng thật
    for px, qty in ((100_000, 800), (30_000, 2_600), (12_000, 6_600)):
        h = mk_holdings(park=park, cash=5_000_000)
        r = run(h, [buy("FPT", qty, px)])
        m = r["buy_amendments"][0]
        tv0, cash0 = m["target_value_vnd"], m["cash_before_vnd"]
        needed, gross, bp = m["needed_vnd"], m["jit_sell_vnd"], m["buying_power_vnd"]
        gap = tv0 - bp
        check(f"T18a px={px:,} — needed = (tv0 − cash)/(1 − friction) (ĐÃ gross-up)",
              abs(needed - (tv0 - cash0) / (1 - ETF_FRICTION)) < 1e-6,
              f"needed={needed:,.2f}")
        check(f"T18b px={px:,} — bất biến gap = (needed − gross)×(1−f) giữ nguyên (gap âm = dư)",
              abs(gap - (needed - gross) * (1 - ETF_FRICTION)) < 1e-6,
              f"gap {gap:,.0f}đ = (needed − gross) {needed - gross:,.0f}đ × (1−friction)")
        # ── A và B: recompute độc lập trên ĐÚNG cùng rổ, `ceiling=needed` = làm tròn XUỐNG ──
        pool_ab, _, _ = build_pool(h, BASE["asof"], BASE["share_override"], ADV_BIG)
        need_a = tv0 - cash0
        gross_a = sum(q * pool_ab[tk]["px"]
                      for tk, q in allocate(need_a, pool_ab, ceiling=need_a).items())
        gap_a = need_a - gross_a * (1 - ETF_FRICTION)
        gross_b = sum(q * pool_ab[tk]["px"]
                      for tk, q in allocate(needed, pool_ab, ceiling=needed).items())
        gap_b = tv0 - (cash0 + gross_b * (1 - ETF_FRICTION))
        cheapest = LOT * min(d["px"] for d in pool_ab.values())
        check(f"T18c px={px:,} — C ≤ B ≤ A: mỗi phương án chỉ làm hụt GIẢM, không bao giờ tăng",
              gap <= gap_b + 1e-6 and gap_b <= gap_a + 1e-6,
              f"A(cũ) {gap_a:,.0f}đ → B(gross-up) {gap_b:,.0f}đ → C(tròn LÊN) {gap:,.0f}đ")
        check(f"T18d px={px:,} — chỉ (C) đưa hụt về 0, và bán dư < 1 lô rẻ nhất",
              gap <= 1e-6 and gap_b > 1e-6 and (gross - needed) < cheapest
              and m["qty_final"] == m["qty_plan"] == qty,
              f"B vẫn hụt {gap_b:,.0f}đ (co lệnh, mất {LOT*px/1e6:,.1f}tr) — C dư "
              f"{-gap:,.0f}đ, bán dư {gross - needed:,.0f}đ < 1 lô {cheapest:,.0f}đ, mua đủ "
              f"{m['qty_final']:,}cp")
        digest(f"t18_{px}", [round(needed, 6), round(gross, 6), round(gap, 6),
                             round(gap_a, 6), round(gap_b, 6), m["status"], m["qty_final"]])


def t18e_C_het_hut_that():
    """(C) ĐÃ WIRE — ca mẫu của báo cáo 08-06 (rổ 3 mã, lô rẻ nhất 2,70tr) nay hết hụt THẬT.

    Trước (C): hụt 786.150đ ⇒ lệnh mua co 800→700cp, MẤT 10tr. Sau (C): bán dư đúng 1 lô CCC
    (2,70tr) ⇒ sức mua ≥ target ⇒ mua đủ 800cp. Chi phí thật của (C) = phần bán dư, và test này
    ghim luôn cận trên của nó (< 1 lô rẻ nhất) để không ai nới thành "bán tuỳ ý".
    """
    from compute_jit_unpark import build_pool
    park = (("AAA", 4_000, 90_000), ("BBB", 6_000, 41_000), ("CCC", 9_000, 27_000))
    h = mk_holdings(park=park, cash=5_000_000)
    r = run(h, [buy("FPT", 800, 100_000)])
    m = r["buy_amendments"][0]
    tv0, needed, gross = m["target_value_vnd"], m["needed_vnd"], m["jit_sell_vnd"]
    pool, _, _ = build_pool(h, BASE["asof"], BASE["share_override"], ADV_BIG)
    cheapest_lot = min(LOT * pool[tk]["px"] for tk in pool)          # = 2,70tr (CCC @27.000)
    check("T18e (C) đã áp ⇒ gross ≥ needed, sức mua ≥ target, mua ĐỦ nguyên lệnh (hụt = 0)",
          gross >= needed - 1e-6 and m["buying_power_vnd"] >= tv0 - 1e-6
          and m["qty_final"] == m["qty_plan"] == 800 and m["status"] == "FUNDED_BY_JIT",
          f"gross {gross:,.0f} ≥ needed {needed:,.0f}; sức mua {m['buying_power_vnd']:,.0f} ≥ "
          f"target {tv0:,.0f}; mua đủ {m['qty_final']}cp")
    check("T18e2 chi phí (C) có cận trên CHẶT: bán dư < 1 lô rẻ nhất của rổ",
          gross - needed < cheapest_lot and gross - needed >= 0,
          f"bán dư {gross - needed:,.0f}đ < 1 lô rẻ nhất {cheapest_lot:,.0f}đ "
          f"(≈{(gross - needed)/tv0*100:.2f}% lệnh mua) — đổi lấy 10tr lệnh mua không bị mất")
    digest("t18e", [round(gross, 6), round(needed, 6), m["status"], m["qty_final"],
                    round(cheapest_lot, 6)])


def t19_C_tran_cung_van_giu():
    """(C) KHÔNG được nới bất kỳ trần CỨNG nào — 3 trần, mỗi trần một ca riêng."""
    park = (("AAA", 4_000, 90_000), ("BBB", 6_000, 41_000), ("CCC", 9_000, 27_000))

    # (1) Trần TỔNG/phiên đang BÓ: needed == day_cap ⇒ không lô nào lọt ⇒ (C) tự tắt, lệnh vẫn CO.
    h1 = mk_holdings(park=park, cash=0)
    r1 = run(h1, [buy("FPT", 10_000, 100_000)], day_cap_override=200_000_000.0)
    m1 = r1["buy_amendments"][0]
    check("T19a trần TỔNG/phiên là trần CỨNG: Σ bán ≤ trần, (C) không nới, lệnh mua vẫn CO",
          r1["jit_sell_total_vnd"] <= 200_000_000 + 1e-6 and m1["status"] == "SHRINK"
          and m1["day_cap_binding"] is True,
          f"Σ bán {r1['jit_sell_total_vnd']:,.0f} ≤ trần 200.000.000 | {m1['status']} "
          f"{m1['qty_plan']}→{m1['qty_final']}cp")

    # (2) Trần per-name (LAG_ADV_PCT × ADV × share) — ADV bé ⇒ mỗi mã chỉ bán được vài lô.
    h2 = mk_holdings(park=park, cash=5_000_000)
    adv_small = lambda tk, asof: (60_000_000.0, asof, None)         # noqa: E731
    r2 = run(h2, [buy("FPT", 800, 100_000)], adv_fn=adv_small)
    cap_i = LAG_ADV_PCT * 60_000_000.0 * BASE["share_override"]
    check("T19b trần per-name là trần CỨNG: mọi mã bán ≤ trần ADV riêng, kể cả lô làm tròn LÊN",
          all(o["value_vnd"] <= cap_i + 1e-6 for o in r2["orders"]),
          f"trần/mã {cap_i:,.0f}đ | " + ", ".join(f"{o['ticker']} {o['value_vnd']:,.0f}"
                                                  for o in r2["orders"]))

    # (3) sellable T+2 — chỉ 100cp mỗi mã được bán, lô làm tròn LÊN không được vượt.
    h3 = mk_holdings(park=park, cash=5_000_000,
                     sellable={"AAA": 100, "BBB": 100, "CCC": 100})
    r3 = run(h3, [buy("FPT", 800, 100_000)])
    check("T19c sellable (T+2) là trần CỨNG: không mã nào bán quá phần được phép",
          all(q <= 100 for q in r3["sells_by_ticker"].values()),
          str(r3["sells_by_ticker"]))

    # (4) Hết dư địa hoàn toàn ⇒ (C) tự tắt (không có lô nào để thêm), không lỗi, vẫn CO lệnh.
    h4 = mk_holdings(park=(("AAA", 100, 10_000),), cash=0)          # cả rổ chỉ 1tr
    r4 = run(h4, [buy("FPT", 1000, 100_000)])
    check("T19d hết dư địa (bán sạch rổ vẫn thiếu) ⇒ (C) tự tắt, không bán quá số đang giữ",
          r4["sells_by_ticker"].get("AAA", 0) <= 100
          and r4["buy_amendments"][0]["status"] == "DROP",
          f"{r4['sells_by_ticker']} {r4['buy_amendments'][0]['status']}")
    digest("t19", [round(r1["jit_sell_total_vnd"], 6), m1["qty_final"],
                   r2["sells_by_ticker"], r3["sells_by_ticker"], r4["sells_by_ticker"]])


# ── T20: §pool-egg-L2 (2026-08-19) — egg cộng vào cash/bp, user duyệt sau khi làm rõ quy trình:
# rút Trứng vàng trong giờ hành chính, về TRONG PHIÊN, không phí (khác PARK — không qua sổ lệnh).
def t20a_egg_du_khong_ban_gi():
    """egg đủ bù toàn bộ target ⇒ triggered=False, KHÔNG bán PARK nào (khớp T01 nhưng nguồn
    tiền là egg thay vì cash thật — chứng minh egg thay thế được cash trong quyết định trigger)."""
    h = mk_holdings(cash=0.0, egg=200_000_000)
    r = run(h, [buy("FPT", 1000, 100_000)])          # target 100tr, cash 0 nhưng egg 200tr
    check("T20a egg đủ bù toàn bộ target ⇒ NO_JIT_NEEDED, không bán PARK nào",
          r["decision"] == "NO_JIT_NEEDED" and not r["orders"]
          and r["buy_amendments"][0]["status"] == "FUNDED_BY_CASH"
          and r["cash_start_vnd"] == 200_000_000,
          f"decision={r['decision']} cash_start={r['cash_start_vnd']:,.0f}")
    digest("t20a", [r["decision"], r["orders"], r["cash_start_vnd"]])


def t20b_egg_giam_needed_vs_cash_only():
    """CHỨNG MINH SO SÁNH: cùng target/cash, một bên có egg một bên không — egg PHẢI làm
    `needed` (lượng PARK cần bán) giảm ĐÚNG BẰNG phần egg che phủ, không hơn không kém (egg
    KHÔNG chiết khấu phí — khác PARK, xem §pool-egg-L2)."""
    tv = 100_000_000
    cash_only = 60_000_000
    egg_add = 25_000_000
    r_no_egg = run(mk_holdings(cash=cash_only), [buy("FPT", 1000, 100_000)])
    r_egg = run(mk_holdings(cash=cash_only, egg=egg_add), [buy("FPT", 1000, 100_000)])
    need_no_egg = r_no_egg["buy_amendments"][0]["needed_vnd"]
    need_egg = r_egg["buy_amendments"][0]["needed_vnd"]
    check("T20b egg giảm needed ĐÚNG BẰNG egg/(1−friction) — không hơn không kém, KHÔNG chiết "
          "khấu phí riêng cho egg (đúng khác biệt egg-vs-PARK)",
          r_egg["decision"] == "JIT"
          and close(need_no_egg - need_egg, egg_add / (1 - ETF_FRICTION), 1),
          f"need_no_egg={need_no_egg:,.0f} need_egg={need_egg:,.0f} "
          f"chênh={need_no_egg - need_egg:,.0f} kỳ_vọng={egg_add / (1 - ETF_FRICTION):,.0f}")
    digest("t20b", [round(need_no_egg, 6), round(need_egg, 6)])


def t20c_egg_mac_dinh_0_khong_hoi_quy():
    """Không khai egg (mặc định 0.0, mọi fixture T01-T19 cũ) ⇒ hành vi Y HỆT trước khi vá."""
    r_default = run(mk_holdings(cash=60_000_000), [buy("FPT", 1000, 100_000)])
    r_explicit_zero = run(mk_holdings(cash=60_000_000, egg=0.0), [buy("FPT", 1000, 100_000)])
    check("T20c egg mặc định 0.0 ⇒ không regression cho mọi test cũ không khai egg",
          r_default["cash_start_vnd"] == r_explicit_zero["cash_start_vnd"] == 60_000_000
          and r_default["buy_amendments"][0]["needed_vnd"]
          == r_explicit_zero["buy_amendments"][0]["needed_vnd"],
          f"{r_default['cash_start_vnd']:,.0f} / {r_explicit_zero['cash_start_vnd']:,.0f}")


def t20d_egg_assets_vnd_bao_cao_dung():
    """`egg_assets_vnd` phải xuất hiện nguyên vẹn trong output — audit trail, không bị nuốt."""
    r = run(mk_holdings(cash=10_000_000, egg=45_000_000), [buy("FPT", 100, 100_000)])
    check("T20d egg_assets_vnd + cash_available_vnd (raw) đều có trong output, không bị gộp mất",
          r.get("egg_assets_vnd") == 45_000_000 and r.get("cash_available_vnd") == 10_000_000
          and r["cash_start_vnd"] == 55_000_000,
          f"egg={r.get('egg_assets_vnd')} cash_available={r.get('cash_available_vnd')} "
          f"cash_start={r['cash_start_vnd']}")


def t20e_qty_final_khong_ghi_de_plan():
    """Chứng minh (per quant-skeptic vòng 2): qty_final của L2 (giờ lớn hơn vì egg) KHÔNG tự
    ghi đè qty của lệnh mua trong plan — đó là việc của `merge_park_orders.py` (KHÔNG đổi qty,
    chỉ chú thích), không phải của `compute_jit_unpark.py`. Test này khẳng định biên trách
    nhiệm: output chỉ là ĐỀ XUẤT, plan gốc (đầu vào `orders`) không bị mutate."""
    orig_orders = [buy("FPT", 1000, 100_000)]
    orig_qty_before = orig_orders[0]["qty"]
    r = run(mk_holdings(cash=0.0, egg=200_000_000), orig_orders)
    check("T20e input `orders` KHÔNG bị mutate bởi compute_jit_unpark (qty gốc giữ nguyên) — "
          "việc merge/ghi qty vào plan là trách nhiệm CỦA merge_park_orders.py, không phải ở đây",
          orig_orders[0]["qty"] == orig_qty_before == 1000
          and r["buy_amendments"][0]["qty_final"] == 1000,
          f"orig_qty={orig_orders[0]['qty']} qty_final={r['buy_amendments'][0]['qty_final']}")


def t20f_egg_relied_warning():
    """quant-skeptic vòng 2 (REFUTED) đòi: khi egg thực sự cần để khớp lệnh, PHẢI có cảnh báo
    tường minh trong out['notes'] (không chỉ CLI stdout) — headless/`--out` JSON phải thấy được.
    Case (a): egg=0, cash đủ ⇒ KHÔNG cảnh báo, funded_via=cash. Case (b): cash=0, egg đủ bù
    TOÀN BỘ ⇒ CÓ cảnh báo, funded_via=cash+egg, egg_relied_vnd = đúng target. Case (c): cash bù
    được MỘT PHẦN, egg bù phần còn lại ⇒ cảnh báo với egg_relied_vnd = đúng phần egg gánh."""
    # (a) không cần egg — không cảnh báo
    r_a = run(mk_holdings(cash=200_000_000, egg=999_000_000), [buy("FPT", 1000, 100_000)])
    m_a = r_a["buy_amendments"][0]
    check("T20f(a) cash đủ, không cần egg ⇒ funded_via=cash, egg_relied_vnd=0, KHÔNG cảnh báo",
          m_a.get("funded_via") == "cash" and m_a.get("egg_relied_vnd") == 0.0
          and not any("Trứng vàng" in n for n in r_a["notes"]),
          f"funded_via={m_a.get('funded_via')} egg_relied={m_a.get('egg_relied_vnd')} "
          f"notes={r_a['notes']}")
    # (b) egg bù TOÀN BỘ (cash=0) ⇒ cảnh báo, egg_relied = đúng target
    r_b = run(mk_holdings(cash=0.0, egg=200_000_000), [buy("FPT", 1000, 100_000)])
    m_b = r_b["buy_amendments"][0]
    check("T20f(b) cash=0, egg bù toàn bộ ⇒ funded_via=cash+egg, egg_relied_vnd=target, CÓ "
          "cảnh báo 'CẦN RÚT Trứng vàng' trong out['notes'] (không chỉ CLI)",
          m_b.get("funded_via") == "cash+egg" and m_b.get("egg_relied_vnd") == 100_000_000
          and any("CẦN RÚT Trứng vàng" in n and "BUY-FPT" in n for n in r_b["notes"]),
          f"funded_via={m_b.get('funded_via')} egg_relied={m_b.get('egg_relied_vnd')} "
          f"notes={r_b['notes']}")
    # (c) cash bù MỘT PHẦN (60tr/100tr target), egg bù phần còn lại — không qua JIT (đủ cash+egg
    # ngay từ đầu nên không trigger bán PARK, chỉ khác biệt ở bước fallback bp/qf).
    r_c = run(mk_holdings(cash=60_000_000, egg=50_000_000), [buy("FPT", 1000, 100_000)])
    m_c = r_c["buy_amendments"][0]
    check("T20f(c) cash bù một phần + egg bù phần còn lại ⇒ egg_relied_vnd = đúng phần egg cần "
          "dùng (target 100tr − qf_real dựa trên cash-only 60tr)",
          m_c.get("funded_via") == "cash+egg" and m_c.get("egg_relied_vnd", 0) > 0
          and m_c["egg_relied_vnd"] <= 50_000_000
          and any("CẦN RÚT Trứng vàng" in n for n in r_c["notes"]),
          f"funded_via={m_c.get('funded_via')} egg_relied={m_c.get('egg_relied_vnd')} "
          f"qty_final={m_c.get('qty_final')}")
    digest("t20f", [m_a.get("funded_via"), m_a.get("egg_relied_vnd"),
                    m_b.get("funded_via"), m_b.get("egg_relied_vnd"),
                    m_c.get("funded_via"), round(m_c.get("egg_relied_vnd", 0), 6)])


def t20g_egg_relied_la_can_tren_khong_phai_chinh_xac():
    """quant-skeptic vòng 3 REFUTED: counterexample tái lập được — egg đủ lớn để TỰ ĐẨY cash
    qua JIT_TRIGGER_FRAC ⇒ nhánh JIT-bán-PARK bị TẮT trong lượt chạy thật (triggered=False) ⇒
    `egg_relied_vnd` gán TOÀN BỘ target là "cần egg", bỏ qua khả năng PARK JIT-sale lẽ ra bù
    được phần lớn nếu không có egg. Test này KHOÁ LẠI đúng counterexample đó + khẳng định tường
    minh: đây là CẬN TRÊN chấp nhận được (an toàn — báo NHIỀU hơn chứ không bao giờ ÍT hơn thực
    tế cần), không phải một bug cần chặn merge, vì hệ quả chỉ là một cảnh báo tư vấn (không phải
    gate — gate thật `check_plan_funding()` không đổi)."""
    # Counterexample nguyên văn quant-skeptic vòng 3: cash=10tr, egg=90tr, target=100tr.
    h = mk_holdings(cash=10_000_000, egg=90_000_000)
    r = run(h, [buy("FPT", 1000, 100_000)])          # target 100tr
    m = r["buy_amendments"][0]
    check("T20g(a) egg tự đẩy cash qua ngưỡng trigger ⇒ triggered=False, KHÔNG bán PARK nào "
          "(đây CHÍNH LÀ nhánh gây sai số — khoá lại để không hồi quy thành bất ngờ)",
          r["decision"] == "NO_JIT_NEEDED" and not r["orders"],
          f"decision={r['decision']} n_orders={len(r['orders'])}")
    check("T20g(b) egg_relied_vnd = CẬN TRÊN = toàn bộ target (100tr) — biết là quá cao so với "
          "thực tế (PARK JIT-sale lẽ ra bù được phần lớn ~90tr nếu không có egg), CHẤP NHẬN vì "
          "hướng AN TOÀN cho cảnh báo tư vấn, không phải một số chính xác",
          m.get("egg_relied_vnd") == 100_000_000 and m.get("funded_via") == "cash+egg",
          f"egg_relied={m.get('egg_relied_vnd')} funded_via={m.get('funded_via')}")
    # Bất biến AN TOÀN (không phải bất biến CHÍNH XÁC): egg_relied_vnd không bao giờ VƯỢT target
    # (không báo cần nhiều hơn cả lệnh mua) và không bao giờ ÂM.
    check("T20g(c) bất biến an toàn: 0 ≤ egg_relied_vnd ≤ target_value_vnd (không âm, không vượt "
          "giá trị lệnh mua)",
          0 <= m.get("egg_relied_vnd", -1) <= m["target_value_vnd"],
          f"egg_relied={m.get('egg_relied_vnd')} target={m['target_value_vnd']}")
    digest("t20g", [r["decision"], m.get("egg_relied_vnd"), m.get("funded_via")])


def t20h_multi_order_bat_bien_an_toan_tung_lenh():
    """quant-skeptic vòng 4 (CONFIRMED, killer_objection phụ) — mỗi lệnh dùng CHUNG `egg0`
    (không trừ dần qua các lệnh, ghi rõ trong docstring là hạn chế CỐ Ý). Test này khoá lại: dù
    2+ lệnh cùng dựa vào egg0 chung, bất biến AN TOÀN (0 ≤ egg_relied_vnd ≤ target_value_vnd)
    vẫn giữ cho TỪNG lệnh riêng lẻ trong chuỗi — không chỉ lệnh đơn lẻ như T20g."""
    h = mk_holdings(cash=0.0, egg=120_000_000)
    orders = [buy("XXX", 1000, 100_000, oid="BUY-XXX", priority=10),
              buy("YYY", 1000, 100_000, oid="BUY-YYY", priority=20)]
    r = run(h, orders)
    ms = {m["order_id"]: m for m in r["buy_amendments"]}
    check("T20h(a) cả 2 lệnh đều có funded_via/egg_relied_vnd hợp lệ (không lỗi/thiếu field)",
          set(ms) == {"BUY-XXX", "BUY-YYY"}
          and all(m.get("funded_via") in ("cash", "cash+egg") for m in ms.values())
          and all(m.get("egg_relied_vnd") is not None for m in ms.values()),
          f"{[(k, v.get('funded_via'), v.get('egg_relied_vnd')) for k, v in ms.items()]}")
    check("T20h(b) bất biến an toàn GIỮ CHO TỪNG lệnh: 0 ≤ egg_relied_vnd ≤ target_value_vnd "
          "(không chỉ lệnh đơn lẻ như T20g — đây là 2 lệnh cùng dựa vào egg0 chung)",
          all(0 <= m["egg_relied_vnd"] <= m["target_value_vnd"] for m in ms.values()),
          f"{[(k, v['egg_relied_vnd'], v['target_value_vnd']) for k, v in ms.items()]}")
    digest("t20h", [sorted((k, v.get("funded_via"), v.get("egg_relied_vnd"))
                          for k, v in ms.items())])


TESTS = [t01_cash_du, t01b_biên_099, t02_thieu_mot_phan, t03_thieu_hon_daycap, t04_excluded,
         t05_capit_khong_dung, t06_unverified, t07_reconcile, t08_no_trigger, t09_drop_duoi_1tr,
         t10_chia_tran_voi_l1, t11_tran_per_name_va_t2, t12_nhieu_lenh_tuan_tu, t13_so_hoc_tien,
         t14_lam_tron_lo, t15_xac_dinh, t16_tz, t17_khong_ghi_gi,
         t18_grossup_va_lam_tron_len_3_muc_gia, t18e_C_het_hut_that, t19_C_tran_cung_van_giu,
         t20a_egg_du_khong_ban_gi, t20b_egg_giam_needed_vs_cash_only,
         t20c_egg_mac_dinh_0_khong_hoi_quy, t20d_egg_assets_vnd_bao_cao_dung,
         t20e_qty_final_khong_ghi_de_plan, t20f_egg_relied_warning,
         t20g_egg_relied_la_can_tren_khong_phai_chinh_xac,
         t20h_multi_order_bat_bien_an_toan_tung_lenh]


def run_tests():
    print(f"=== compute_jit_unpark selfcheck | TZ={os.environ.get('TZ', '<unset>')} ===")
    print(f"    hằng số PORT: trigger={JIT_TRIGGER_FRAC} shrink={SHRINK_FRAC} "
          f"min_order={MIN_ORDER_VND:,} friction={ETF_FRICTION} lot={LOT}")
    for t in TESTS:
        t()
    d = hashlib.sha256("\n".join(DIGEST_PARTS).encode()).hexdigest()[:16]
    print(f"\n  {len(PASSES)} PASS / {len(FAILS)} FAIL")
    if FAILS:
        print("  ❌ " + "; ".join(FAILS))
    print(f"DIGEST={d}")
    return 0 if not FAILS else 1


def tz_matrix():
    """Chạy lại chính file này dưới 4 môi trường TZ, so DIGEST + exit code."""
    envs = [("<unset>", None), ("Asia/Ho_Chi_Minh", "Asia/Ho_Chi_Minh"),
            ("UTC", "UTC"), ("America/New_York", "America/New_York")]
    results = []
    for name, tz in envs:
        env = dict(os.environ, JIT_SC_CHILD="1")
        env.pop("TZ", None)
        if tz:
            env["TZ"] = tz
        p = subprocess.run([sys.executable, os.path.abspath(__file__)], env=env,
                           capture_output=True, text=True)
        dg = next((ln.split("=", 1)[1] for ln in p.stdout.splitlines()
                   if ln.startswith("DIGEST=")), None)
        nfail = next((ln for ln in p.stdout.splitlines() if "FAIL" in ln and "PASS" in ln), "?")
        results.append((name, p.returncode, dg, nfail.strip()))
        print(f"  TZ={name:<20} exit={p.returncode} digest={dg} [{nfail.strip()}]")
        if p.returncode != 0:
            print(p.stdout[-4000:])
            print(p.stderr[-2000:])
    ok = all(r[1] == 0 for r in results) and len({r[2] for r in results}) == 1
    print(f"\n{'✅' if ok else '❌'} MA TRẬN TZ: "
          f"{'mọi môi trường PASS và digest ĐỒNG NHẤT' if ok else 'LỆCH giữa các môi trường'}")
    return 0 if ok else 1


if __name__ == "__main__":
    if os.environ.get("JIT_SC_CHILD"):
        sys.exit(run_tests())
    rc = run_tests()
    print("\n=== ma trận TZ (env -u TZ / ICT / UTC / New York) ===")
    sys.exit(max(rc, tz_matrix()))
