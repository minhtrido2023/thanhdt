#!/usr/bin/env python3
"""Self-check cho `compute_park_trim.py` — công thức phân bổ BÁN của L1/L0.

VÌ SAO CÓ FILE NÀY (2026-08-07, job Taylor_20260807_020402): công thức phân bổ đổi từ pro-rata
theo trọng số ĐANG CÓ (`w_live_i × trim_total`) sang khoảng cách tới trọng số MỤC TIÊU
(`order_i = mv_i − tgt_i`, §D1 `park_membership_sync_L0_design_20260806.md`, user John duyệt).
Lỗ hổng gốc: SHS (0,5% PARK SpaceX) rớt rổ 2026-08-05 nhưng pro-rata chỉ phân cho nó 609k đ/phiên
⇒ luôn < 1 lô ⇒ mắc kẹt VĨNH VIỄN, không đường ra. Trước đó module này KHÔNG có selfcheck riêng
(chỉ có `send_plan_report_park_jit_selfcheck.py` kiểm phần HIỂN THỊ).

Chạy:  python3 mike/bin/compute_park_trim_selfcheck.py
Theo skill `verify-before-done`:
  · KHÔNG dùng `data/golive_v23_status.json` thật — mọi ca patch `cpt.STATE_FILE` sang file tạm
    (nếu không, state live ≠ NEUTRAL sẽ làm MỌI ca trả SKIP_STATE và selfcheck "PASS" giả).
  · KHÔNG gọi mạng: `price_fn`/`adv_fn`/`share_override`/`day_cap_override`/`basket_override`
    đều bơm tay.
  · Ca T15 chạy `park_target_basket` trên CSV THẬT (đọc file, không mạng) để bắt lỗi schema.
  · Chạy lại toàn bộ dưới `env -u TZ` + ICT + UTC + America/New_York (bẫy §16).
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
WC = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, WC)

import compute_park_trim as cpt                                  # noqa: E402
from trading_bot.vn_market import LOT                            # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'} — {name}" + (f"  [{detail}]" if detail else ""))


def close(a, b, tol=1.0):
    return abs(float(a) - float(b)) <= tol


# ── Fixture: rổ + giá + sổ, số tròn để kiểm tay được ─────────────────────────
# rổ mục tiêu (Σ = 1,000): PC1 = BANNED, TIN = quá nhỏ so với 1 lô, XCL = excluded_tickers.
BASKET = {"AAA": 0.40, "BBB": 0.25, "CCC": 0.20, "PC1": 0.10, "DDD": 0.045,
          "TIN": 0.005}
PX = {"AAA": 10_000, "BBB": 20_000, "CCC": 50_000, "DDD": 30_000,
      "TIN": 60_000, "PC1": 40_000, "SHS": 20_000, "XCL": 25_000}
BIG_CAP = 10e9          # trần TỔNG/phiên rộng ⇒ không binding trừ khi ca cố ý siết
ASOF = "2026-08-07"


def price_fn(calls=None):
    def _f(tk):
        if calls is not None:
            calls.append(tk)
        return (PX.get(tk), None) if tk in PX else (None, "không có giá test")
    return _f


def adv_fn_ok(adv=1e12):
    return lambda tk, asof: (adv, asof, None)


def holdings(lots, cash=0.0, excluded=(), unver=(), reconcile_ok=True, sellable=None):
    """lots = [(ticker, qty, entry_date, source)] — mv tính từ PX."""
    park_lots = [{"ticker": t, "qty": q, "market_price": PX[t], "mv_vnd": q * PX[t],
                  "price": PX[t], "entry_date": d, "source": s, "book": "PARK"}
                 for (t, q, d, s) in lots]
    per = {}
    for l in park_lots:
        per[l["ticker"]] = per.get(l["ticker"], 0) + l["qty"]
    bpos = {t: {"qty": q, "market_price": PX[t],
                "sellable": (sellable or {}).get(t, q)} for t, q in per.items()}
    return {"account_label": "TEST", "asof": ASOF,
            "park_lots": park_lots, "broker_positions": bpos,
            "park_mv_vnd": sum(l["mv_vnd"] for l in park_lots),
            "cash_available_vnd": cash,
            "reconcile": {"ok": reconcile_ok,
                          "mismatches": [] if reconcile_ok else [{"ticker": "AAA", "diff": 100}]},
            "unverified_tickers": list(unver), "excluded_tickers": list(excluded)}


# Sổ chuẩn: PARK 1.000tr, cash 0 ⇒ pool 1.000tr, target 80% = 800tr, vượt 200tr.
#   AAA 300tr (DƯỚI target 357,54tr)   BBB 400tr (TRÊN 223,46tr)
#   CCC 200tr (TRÊN 178,77tr)          SHS 100tr (NGOÀI rổ ⇒ target 0 — ca SHS thật)
BASE_LOTS = [("AAA", 30_000, "2026-05-05", "j1"),
             ("BBB", 20_000, "2026-05-05", "j1"),
             ("CCC", 4_000, "2026-05-05", "j1"),
             ("SHS", 3_000, "2026-04-01", "j0"),     # lô CŨ hơn → FIFO phải lấy trước
             ("SHS", 2_000, "2026-06-10", "j2")]


def run(h, state=None, basket=None, **kw):
    """Gọi compute_trim với STATE_FILE tạm (state mặc định NEUTRAL=3, etf_park_frac=0,80)."""
    st = {"state": 3, "state_name": "NEUTRAL", "date": ASOF, "etf_park_frac": 0.80}
    if state is not None:
        st.update(state)
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(st, f)
    old = cpt.STATE_FILE
    cpt.STATE_FILE = path
    try:
        kw.setdefault("share_override", 1.0)
        kw.setdefault("adv_fn", adv_fn_ok())
        kw.setdefault("day_cap_override", BIG_CAP)
        kw.setdefault("basket_override", BASKET if basket is None else basket)
        kw.setdefault("price_fn", price_fn())
        return cpt.compute_trim("TEST", ASOF, 0.80, holdings=h, **kw)
    finally:
        cpt.STATE_FILE = old
        os.unlink(path)


def by_ticker(r, tk):
    return next((o for o in r["orders"] if o["ticker"] == tk), None)


# ═══════════════════════════════════════════════════════════════════════════
print("=== compute_park_trim selfcheck — công thức tgt_i − mv_i ===")

# ── T1-T4: ca SHS THẬT — mã rớt rổ phải được bán SẠCH ───────────────────────
r = run(holdings(BASE_LOTS))
check("T1 decision=TRIM", r["decision"] == "TRIM", r["decision"])
o_shs = by_ticker(r, "SHS")
check("T2 (a) SHS rớt rổ ⇒ CÓ lệnh bán", o_shs is not None)
check("T2b (a) SHS bán SẠCH 5.000cp (= toàn bộ vị thế)",
      o_shs and o_shs["qty"] == 5_000, o_shs and o_shs["qty"])
check("T3 (a) SHS in_basket=False, target_vnd=0",
      o_shs and o_shs["in_basket"] is False and o_shs["target_vnd"] == 0)
check("T4 (a) FIFO SHS: lô 2026-04-01 (3.000cp) trước lô 2026-06-10 (2.000cp)",
      o_shs and [(l["entry_date"], l["qty"]) for l in o_shs["fifo_lots"]]
      == [("2026-04-01", 3_000), ("2026-06-10", 2_000)],
      o_shs and o_shs["fifo_lots"])

# ── T5-T7: (b) BANNED + (c) chuẩn hoá trọng số ──────────────────────────────
drop = {d["ticker"]: d for d in r["basket_dropped"]}
check("T5 (b) PC1 (BANNED) bị loại khỏi rổ mục tiêu",
      "PC1" in drop and "BANNED" in drop["PC1"]["reason"], sorted(drop))
check("T5b (b) PC1 KHÔNG có trong target_weights (tgt=0)", "PC1" not in r["target_weights"])
check("T6 (c) TIN bị loại vì target < 1 lô",
      "TIN" in drop and "1 lô" in drop["TIN"]["reason"],
      drop.get("TIN", {}).get("reason"))
# w' = w / Σ(khả thi) với Σ = 0,40+0,25+0,20+0,045 = 0,895
exp_w = {"AAA": 0.40 / 0.895, "BBB": 0.25 / 0.895, "CCC": 0.20 / 0.895, "DDD": 0.045 / 0.895}
check("T7 (c) trọng số chuẩn hoá đúng trên tập khả thi + Σ = 1",
      set(r["target_weights"]) == set(exp_w)
      and all(abs(r["target_weights"][k] - v) < 1e-12 for k, v in exp_w.items())
      and abs(sum(r["target_weights"].values()) - 1.0) < 1e-12,
      r["target_weights"])
check("T7b (c) Σ trọng số bị bỏ = 10,5% (PC1 10% + TIN 0,5%)",
      abs(r["basket_dropped_weight"] - 0.105) < 1e-12, r["basket_dropped_weight"])

# ── T8-T10: số tiền — tgt_i = 800tr × w' ────────────────────────────────────
check("T8 target_value AAA = 800tr × 0,4/0,895 = 357,54tr",
      close(r["target_value_vnd"]["AAA"], 800e6 * 0.40 / 0.895, 1),
      r["target_value_vnd"]["AAA"])
check("T9 AAA DƯỚI target ⇒ KHÔNG bán, nằm ở at_or_below_target",
      by_ticker(r, "AAA") is None
      and any(a["ticker"] == "AAA" for a in r["at_or_below_target"]))
o_bbb, o_ccc = by_ticker(r, "BBB"), by_ticker(r, "CCC")
# BBB: 400tr − 223,46tr = 176,54tr → /20.000 = 8.826,8 → làm tròn xuống lô = 8.800cp
check("T10 BBB bán 8.800cp (176,54tr làm tròn lô)", o_bbb and o_bbb["qty"] == 8_800,
      o_bbb and o_bbb["qty"])
# CCC: 200tr − 178,77tr = 21,23tr → /50.000 = 424,6 → 400cp
check("T10b CCC bán 400cp (21,23tr làm tròn lô)", o_ccc and o_ccc["qty"] == 400,
      o_ccc and o_ccc["qty"])
check("T10c Σ lệch cấu trúc = 297,77tr (BBB 176,54 + CCC 21,23 + SHS 100)",
      close(r["structural_excess_vnd"], 400e6 - 800e6 * 0.25 / 0.895
            + 200e6 - 800e6 * 0.20 / 0.895 + 100e6, 10),
      r["structural_excess_vnd"])
check("T10d Σ bán > mức vượt trần 200tr ⇒ cảnh báo DƯỚI target được ghi ra",
      r["underpark_after_vnd"] > 0
      and any("DƯỚI target" in n for n in r["notes"]),
      f"underpark={r['underpark_after_vnd']:,.0f}")

# ── T11: (b2) BANNED mà ĐANG GIỮ ⇒ target 0 ⇒ bán sạch ──────────────────────
r2 = run(holdings(BASE_LOTS + [("PC1", 1_000, "2026-05-05", "j1")]))
o_pc1 = by_ticker(r2, "PC1")
check("T11 (b) PC1 đang giữ + BANNED ⇒ bán SẠCH 1.000cp",
      o_pc1 and o_pc1["qty"] == 1_000 and o_pc1["in_basket"] is False,
      o_pc1 and o_pc1["qty"])

# ── T12: (4b) excluded_tickers ∩ rổ ⇒ tgt=0, KHÔNG sinh lệnh bán ────────────
bk_x = dict(BASKET, XCL=0.05)
bk_x = {k: v / sum(bk_x.values()) for k, v in bk_x.items()}   # chuẩn hoá lại cho Σ=1
r3 = run(holdings(BASE_LOTS + [("XCL", 1_000, "2026-05-05", "j1")], excluded=("XCL",)),
         basket=bk_x)
check("T12 (4b) XCL excluded: KHÔNG có lệnh bán",
      by_ticker(r3, "XCL") is None
      and any(b["ticker"] == "XCL" and "excluded" in b["reason"] for b in r3["blocked"]))
check("T12b (4b) XCL bị loại khỏi rổ mục tiêu ⇒ trọng số chuẩn hoá sang mã khác",
      "XCL" not in r3["target_weights"]
      and any(d["ticker"] == "XCL" and "excluded" in d["reason"]
              for d in r3["basket_dropped"]))

# ── T13-T14: (d) hồi quy các ranh giới cứng CŨ ──────────────────────────────
check("T13a reconcile lệch ⇒ BLOCKED_RECONCILE, 0 lệnh",
      (lambda x: x["decision"] == "BLOCKED_RECONCILE" and not x["orders"])(
          run(holdings(BASE_LOTS, reconcile_ok=False))))
check("T13b state ≠ NEUTRAL ⇒ SKIP_STATE, 0 lệnh",
      (lambda x: x["decision"] == "SKIP_STATE" and not x["orders"])(
          run(holdings(BASE_LOTS), state={"state": 1, "state_name": "BEAR"})))
r_no = run(holdings([("AAA", 30_000, "2026-05-05", "j1")], cash=7_500_000))
# PARK 300tr, cash 7,5tr ⇒ pool 307,5tr, target 246tr — PARK vượt 54tr > band ⇒ vẫn TRIM.
check("T13c PARK ≤ target + band ⇒ NO_TRIM (trigger mức GIỮ NGUYÊN)",
      (lambda x: x["decision"] == "NO_TRIM" and not x["orders"])(
          run(holdings([("AAA", 30_000, "2026-05-05", "j1")], cash=80_000_000))),
      "PARK 300tr / pool 380tr = 78,9% < 80%")
check("T13d ticker UNVERIFIED ⇒ blocked, KHÔNG sinh lệnh",
      (lambda x: by_ticker(x, "SHS") is None
       and any(b["ticker"] == "SHS" and "UNVERIFIED" in b["reason"] for b in x["blocked"]))(
          run(holdings(BASE_LOTS, unver=("SHS",)))))
check("T13e không đo được ADV ⇒ blocked mã đó (fail-closed per-name)",
      (lambda x: by_ticker(x, "SHS") is None
       and any(b["ticker"] == "SHS" and "ADV" in b["reason"] for b in x["blocked"]))(
          run(holdings(BASE_LOTS),
              adv_fn=lambda tk, asof: ((0, asof, "lỗi test") if tk == "SHS"
                                       else (1e12, asof, None)))))
check("T13f trần %ADV per-name cắt lệnh ⇒ adv_capped + carry-over",
      (lambda x: (lambda o: o and o["adv_capped"] and o["qty"] == 2_500
                  and x["trim_shortfall_vnd"] > 0)(by_ticker(x, "SHS")))(
          run(holdings(BASE_LOTS),
              adv_fn=lambda tk, asof: ((50e6 / cpt.LAG_ADV_PCT, asof, None) if tk == "SHS"
                                       else (1e12, asof, None)))),
      "ADV cắt SHS còn 50tr = 2.500cp")
check("T13g sellable (T+2) chặn phần chưa về",
      (lambda o: o and o["qty"] == 1_200)(
          by_ticker(run(holdings(BASE_LOTS, sellable={"SHS": 1_234})), "SHS")),
      "sellable 1.234cp → làm tròn lô 1.200")
r_cap = run(holdings(BASE_LOTS), day_cap_override=100e6)
check("T14a trần TỔNG/phiên binding ⇒ mọi want co theo cùng 1 hệ số",
      r_cap["day_cap_binding"] is True
      and close(r_cap["day_cap_scale"], 100e6 / r_cap["structural_excess_vnd"], 1e-9)
      and close(r_cap["trim_total_vnd"], 100e6, 1),
      f"scale={r_cap['day_cap_scale']:.4f}")
check("T14b trần TỔNG hỏng/không đo được ⇒ BLOCKED_DAYCAP",
      (lambda x: x["decision"] == "BLOCKED_DAYCAP" and not x["orders"])(
          run(holdings(BASE_LOTS), day_cap_override=0)))
check("T14c rổ mục tiêu hỏng (Σw ≠ 1) ⇒ BLOCKED_BASKET, 0 lệnh",
      (lambda x: x["decision"] == "BLOCKED_BASKET" and not x["orders"])(
          run(holdings(BASE_LOTS), basket={"AAA": 0.4})))
check("T14d không mã nào khả thi ⇒ BLOCKED_NO_FEASIBLE_BASKET",
      (lambda x: x["decision"] == "BLOCKED_NO_FEASIBLE_BASKET" and not x["orders"])(
          run(holdings(BASE_LOTS), basket={"PC1": 1.0})))

# ── T15: rổ THẬT từ CSV — PIT + schema ──────────────────────────────────────
w, rd, err = cpt.park_target_basket(ASOF)
# Kỳ vọng dựng ĐỘC LẬP từ chính CSV (không ghim ngày cứng — kỳ rebal đổi hàng quý).
import pandas as _pd                                              # noqa: E402
_csv = _pd.read_csv(cpt.BASKET_CSV)
_exp_rd = str(_csv[_csv.rebal_date.astype(str) <= ASOF].rebal_date.astype(str).max())
check("T15a park_target_basket đọc được CSV thật: đúng kỳ hiệu lực, 30 mã, Σw≈1",
      err is None and rd == _exp_rd and len(w) == 30 and abs(sum(w.values()) - 1) < 0.01,
      f"{rd} (kỳ vọng {_exp_rd}) n={len(w) if w else 0} err={err}")
w2, rd2, err2 = cpt.park_target_basket("2026-06-01")
check("T15b PIT: asof 2026-06-01 ⇒ kỳ 2026-05-05 (KHÔNG nhìn trước kỳ 08-05)",
      err2 is None and rd2 == "2026-05-05", rd2)
check("T15c asof trước mọi kỳ rebal ⇒ lỗi, không đoán",
      cpt.park_target_basket("2010-01-01")[2] is not None)
check("T15d file rổ không tồn tại ⇒ lỗi (fail-closed)",
      cpt.park_target_basket(ASOF, path="/tmp/khong-co-file-nay.csv")[2] is not None)

# ── T16: price_fn CHỈ được gọi cho mã KHÔNG có trong vị thế broker ──────────
calls = []
run(holdings(BASE_LOTS), price_fn=price_fn(calls))
check("T16 price_fn chỉ hỏi mã chưa giữ (DDD, TIN) — mã đang giữ dùng giá broker",
      set(calls) == {"DDD", "TIN"}, sorted(set(calls)))
check("T16b mã trong rổ không lấy được giá ⇒ loại khỏi rổ khả thi (fail-closed = bán ÍT đi)",
      (lambda x: "DDD" not in x["target_weights"]
       and any(d["ticker"] == "DDD" and "giá" in d["reason"] for d in x["basket_dropped"]))(
          run(holdings(BASE_LOTS),
              price_fn=lambda tk: ((None, "quote lỗi") if tk == "DDD"
                                   else (PX.get(tk), None)))))
check("T16c live_price_fn với asof quá khứ ⇒ báo lỗi, KHÔNG chạm mạng/BQ",
      cpt.live_price_fn("2020-01-02")("AAA")[0] is None)

# ── T17: bất biến kế toán — Σ lệnh = Σ min(want, trần) đã làm tròn lô ───────
r4 = run(holdings(BASE_LOTS))
check("T17 Σ value_vnd lệnh = Σ qty × giá, và ≤ trim_total",
      close(r4["trim_proposed_vnd"], sum(o["qty"] * o["ref_price"] for o in r4["orders"]), 1)
      and r4["trim_proposed_vnd"] <= r4["trim_total_vnd"] + 1)
_held = {t: sum(l["qty"] for l in holdings(BASE_LOTS)["park_lots"] if l["ticker"] == t)
         for t in {l[0] for l in BASE_LOTS}}
check("T17b không lệnh nào bán quá số đang giữ / quá sellable",
      all(o["qty"] <= _held[o["ticker"]] and o["qty"] <= o["sellable"] for o in r4["orders"]))

print(f"\n=== {len(PASS)} PASS / {len(FAIL)} FAIL ===")
if FAIL:
    for f in FAIL:
        print(f"  ✗ {f}")
sys.exit(1 if FAIL else 0)
