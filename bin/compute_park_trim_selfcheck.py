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
import park_holdings as PH                                       # noqa: E402
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


FIXTURE_DEBT = 50e6     # xem `holdings()` — chỉ để sổ mặc định KHÔNG trùng chữ ký lỗi feed


def holdings(lots, cash=0.0, excluded=(), unver=(), reconcile_ok=True, sellable=None,
             total_cash="net_zero", div_recv=0.0, debt="net_zero", egg=0.0):
    """lots = [(ticker, qty, entry_date, source)] — mv tính từ PX.

    `total_cash` = mẫu số pool L1 (totalCash DNSE). `None` = DNSE thiếu field ⇒ phải fail-closed.

    Mặc định `total_cash`/`debt` = "net_zero": tài khoản margin có ĐÚNG `FIXTURE_DEBT` đồng tiền
    và `FIXTURE_DEBT` đồng nợ ⇒ vốn chủ sở hữu nhàn rỗi = totalCash − totalDebt = 0 ⇒ pool =
    park_mv, GIỮ NGUYÊN mọi con số kỳ vọng của T1-T17 (chúng viết trên giả định pool = 1.000tr).

    VÌ SAO không để thẳng cả ba field tiền = 0 cho gọn (bản trước làm vậy): "totalCash = totalDebt
    = availableCash = 0 mà sổ PARK > 0" CHÍNH LÀ chữ ký lỗi feed DNSE 2026-07-27 và code CHẶN nó
    (fail-closed, T18k). Một sổ test hợp lệ không được trùng chữ ký lỗi — nếu trùng thì mọi ca
    T1-T17 sẽ trả BLOCKED_CASH_BASIS và selfcheck sập, đúng như đã xảy ra khi thêm guard.
    """
    if total_cash == "net_zero" and debt == "net_zero":
        total_cash, debt = cash + FIXTURE_DEBT, FIXTURE_DEBT     # net = cash (thường 0)
    else:                       # ca T18* khai tường minh ⇒ giữ đúng số nó khai, không tự chèn nợ
        total_cash = cash if total_cash == "net_zero" else total_cash
        debt = 0.0 if debt == "net_zero" else debt
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
            "cash_total_vnd": total_cash,
            "cash_dividend_receiving_vnd": div_recv,
            "cash_debt_vnd": debt,
            "egg_assets_vnd": egg,
            "cash_basis": "total_cash",
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

# ── T18: MẪU SỐ POOL = totalCash, KHÔNG availableCash (bug 2026-08-09) ──────
# Mọi ca "chặn được" đều kèm CA CHỨNG MINH NGƯỢC: bỏ phần sửa ⇒ THẬT SỰ hỏng (§24).
# Kịch bản tái dựng ca thật SpaceX 08-07: PARK 1.000tr, vừa bán 400tr (chưa settle), tiền đã
# settle chỉ 20tr. totalCash = 20 + 400 = 420tr.
H_SETTLED, H_UNSETTLED = 20e6, 400e6
r18 = run(holdings(BASE_LOTS, cash=H_SETTLED, total_cash=H_SETTLED + H_UNSETTLED))
check("T18 pool dùng totalCash: 1.000tr PARK + 420tr = 1.420tr ⇒ target 1.136tr > PARK ⇒ NO_TRIM",
      r18["decision"] == "NO_TRIM" and close(r18["pool_vnd"], 1_420e6, 1),
      f"{r18['decision']} pool={r18.get('pool_vnd')}")
r18_bad = run(holdings(BASE_LOTS, cash=H_SETTLED, total_cash=H_SETTLED))
check("T18b CHỨNG MINH NGƯỢC — cùng sổ mà mẫu số bỏ tiền bán chưa settle ⇒ TRIM oan 180tr",
      r18_bad["decision"] == "TRIM" and close(r18_bad["pool_vnd"], 1_020e6, 1)
      and r18_bad["trim_total_vnd"] > 150e6,
      f"{r18_bad['decision']} pool={r18_bad.get('pool_vnd')} "
      f"trim={r18_bad.get('trim_total_vnd')}")

# Vòng lặp tự kích: bán X ⇒ park_mv−X, và cash ĐO ĐƯỢC không tăng (tiền chưa settle).
# Với mẫu số ĐÚNG tỷ lệ phải giảm; với availableCash tỷ lệ gần như đứng yên.
def _ratio(park_mv, settled, unsettled, use_total):
    pool = (settled + unsettled if use_total else settled) + park_mv
    return park_mv / pool


_before = _ratio(1_000e6, 20e6, 0, True)
_after_ok = _ratio(600e6, 20e6, 400e6, True)      # bán 400tr, mẫu số đúng
_after_bug = _ratio(600e6, 20e6, 400e6, False)    # bán 400tr, mẫu số cũ
check("T18c bán 400tr ⇒ mẫu số đúng hạ tỷ lệ 98,0%→58,8% (giảm thật)",
      close(_before, 0.98039, 1e-4) and close(_after_ok, 0.58824, 1e-4))
check("T18d CHỨNG MINH NGƯỢC — mẫu số cũ chỉ hạ 98,0%→96,8%: bán 400tr gần như vô hiệu "
      "⇒ phiên sau lại đòi trim (vòng lặp tự kích)",
      close(_after_bug, 0.96774, 1e-4) and (_before - _after_bug) < 0.02)

check("T18e DNSE thiếu totalCash ⇒ BLOCKED_CASH_BASIS, KHÔNG âm thầm rơi về availableCash",
      run(holdings(BASE_LOTS, cash=H_SETTLED, total_cash=None))["decision"]
      == "BLOCKED_CASH_BASIS")
check("T18f cổ tức chờ nhận NẰM TRONG totalCash ⇒ không cộng thêm lần nữa (pool = totalCash+PARK)",
      close(run(holdings(BASE_LOTS, cash=H_SETTLED, total_cash=100e6,
                         div_recv=30e6))["pool_vnd"], 1_100e6, 1))
# L2 (compute_jit_unpark) PHẢI vẫn dùng availableCash — hai ngữ nghĩa khác nhau, đừng gộp.
_ju = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "compute_jit_unpark.py"), encoding="utf-8").read()
check("T18g L2 jit_unpark vẫn sizing theo cash_available_vnd (tiền tiêu được), KHÔNG đổi sang total",
      'h["cash_available_vnd"]' in _ju and 'h["cash_total_vnd"]' not in _ju)

# ── T18h: nợ margin PHẢI bị trừ khỏi mẫu số (phản biện quant-skeptic 2026-08-09) ──
# Tái dựng quy mô nợ THẬT của SpaceX ngày 2026-07-03 (409,9tr) trên cùng sổ PARK 1.000tr.
DEBT = 409.9e6
r18h = run(holdings(BASE_LOTS, cash=20e6, total_cash=500e6, debt=DEBT))
check("T18h pool trừ nợ margin: (500 − 409,9) + 1.000 = 1.090,1tr",
      close(r18h["pool_vnd"], 1_090.1e6, 1), f"pool={r18h.get('pool_vnd')}")
r18h_bad = run(holdings(BASE_LOTS, cash=20e6, total_cash=500e6, debt=0.0))
check("T18i CHỨNG MINH NGƯỢC — bỏ qua nợ ⇒ pool phồng 1.500tr, trần PARK 1.200tr > PARK 1.000tr "
      "⇒ NO_TRIM hoàn toàn, trong khi trừ nợ đúng thì PHẢI trim 127,9tr (under-trim)",
      close(r18h_bad["pool_vnd"], 1_500e6, 1)
      and r18h_bad["decision"] == "NO_TRIM" and r18h["decision"] == "TRIM"
      # mức VƯỢT TRẦN = −delta = 1.000 − 80%×1.090,1 = 127,92tr. (KHÔNG so với trim_total_vnd:
      # đó là tổng SELL-ONLY Σ max(0, mv−tgt), theo thiết kế LỚN HƠN mức vượt trần — §HỆ QUẢ.)
      and close(-r18h["delta_vnd"], 127.92e6, 1e4),
      f"trừ nợ={r18h['decision']}/vượt {-r18h['delta_vnd']:,.0f} vs bỏ nợ={r18h_bad['decision']}")
check("T18j DNSE thiếu totalDebt ⇒ BLOCKED_CASH_BASIS (không âm thầm coi nợ = 0)",
      run(holdings(BASE_LOTS, cash=20e6, total_cash=500e6,
                   debt=None))["decision"] == "BLOCKED_CASH_BASIS")

# ── T18k-T18m: lỗi feed DNSE "số 0" (sự cố THẬT 2026-07-27) ────────────────
# quant-skeptic REFUTED vòng 2: bản vá trước chỉ chặn field THIẾU (None), không chặn field CÓ
# MÀ BẰNG 0 — mà 0 mới là hình dạng của sự cố đã xảy ra. Đây là ca ĐẮT NHẤT: pool = park_mv
# ⇒ PARK "chiếm 100% pool" ⇒ bán gần sạch sổ.
#
# Phát hiện nằm Ở NGUỒN (`park_holdings`, nơi duy nhất thấy block `stock` thô), KHÔNG lặp ở
# consumer — nên T18k/T18l kiểm qua ĐƯỜNG THẬT `read_broker_snapshot` (dưới, sau `_raw_snapshot`),
# còn ở đây chỉ kiểm hai vị từ phát hiện như đơn vị.
check("T18m1 _stock_block_all_zero: block toàn 0 ⇒ True; có 1 field khác 0 ⇒ False",
      PH._stock_block_all_zero({"totalCash": 0, "totalDebt": 0, "availableCash": 0})
      and not PH._stock_block_all_zero({"totalCash": 0, "totalDebt": 0, "depositInterest": 318}))
# Đây là khe hở mà _stock_block_all_zero KHÔNG bịt được: depositInterest cộng dồn liên tục nên
# hiếm khi đúng 0, chỉ cần nó khác 0 là "toàn block bằng 0" trả False trong khi mẫu số pool vẫn
# hỏng đúng kiểu tệ nhất.
check("T18m2 _cash_fields_all_zero: 3 field tiền = 0 (dù depositInterest≠0) ⇒ True",
      PH._cash_fields_all_zero({"totalCash": 0, "totalDebt": 0, "availableCash": 0,
                                "depositInterest": 318}))
check("T18m3 CHỨNG MINH NGƯỢC — chỉ cần 1 trong 3 field tiền khác 0 ⇒ False (không chặn nhầm "
      "tài khoản hết tiền tiêu nhưng còn tiền bán chưa settle)",
      not PH._cash_fields_all_zero({"totalCash": 500e6, "totalDebt": 0, "availableCash": 0}))
check("T18m4 thiếu field ⇒ False (để `_f_or_none`→None lo, không nhập nhèm hai chế độ hỏng)",
      not PH._cash_fields_all_zero({"totalCash": 0, "totalDebt": 0}))
# T18n — ĐƯỜNG THẬT: dựng file dnse_raw có bản ghi balances toàn-0 rồi gọi chính
# read_broker_snapshot() (không phải fixture bơm tay). Đây mới là đường production đi qua;
# lỗ hổng vòng 2 chính là "selfcheck xanh nhưng code path thật vẫn TRIM".
def _raw_snapshot(stock_block):
    with tempfile.TemporaryDirectory() as td:
        acc, day = "0009999999", "2026-08-07"
        with open(os.path.join(td, f"dnse_raw_{day}.jsonl"), "w", encoding="utf-8") as f:
            f.write(json.dumps({"account_no": acc, "kind": "positions", "ts": f"{day}T19:00:00",
                                "payload": {"positions": [{"accountNo": acc, "symbol": "AAA",
                                                           "openQuantity": 100,
                                                           "marketPrice": 10000,
                                                           "tradeQuantity": 100}]}}) + "\n")
            f.write(json.dumps({"account_no": acc, "kind": "balances", "ts": f"{day}T19:01:00",
                                "payload": {"stock": stock_block}}) + "\n")
        return PH.read_broker_snapshot("TEST", acc, day, exec_dir=td)


_, _, m_zero = _raw_snapshot({"totalCash": 0, "totalDebt": 0, "availableCash": 0,
                              "depositInterest": 0, "cashDividendReceiving": 0})
_, _, m_ok = _raw_snapshot({"totalCash": 500e6, "totalDebt": 0, "availableCash": 20e6,
                            "depositInterest": 318, "cashDividendReceiving": 0})
check("T18n read_broker_snapshot (đường THẬT): balances toàn-0 ⇒ total_cash/total_debt = None",
      m_zero["total_cash_vnd"] is None and m_zero["total_debt_vnd"] is None
      and m_zero["balance_all_zero"] is True,
      f"{m_zero['total_cash_vnd']} / {m_zero['total_debt_vnd']}")
check("T18o CHỨNG MINH NGƯỢC — cùng đường đó với số hợp lệ (nợ=0 thật) VẪN đọc ra số, "
      "không chặn nhầm mọi tài khoản không nợ",
      m_ok["total_cash_vnd"] == 500e6 and m_ok["total_debt_vnd"] == 0.0
      and m_ok["balance_all_zero"] is False,
      f"{m_ok['total_cash_vnd']} / {m_ok['total_debt_vnd']}")

# T18k — ca quant-skeptic vòng 2 đòi, chạy TRỌN chuỗi thật: dnse_raw có totalCash=0 VÀ
# totalDebt=0 (đúng hình dạng lỗi 07-27) nhưng depositInterest≠0 để `_stock_block_all_zero`
# KHÔNG bắt được ⇒ chỉ `_cash_fields_all_zero` cứu. Yêu cầu: PHẢI ra BLOCKED_CASH_BASIS.
_, _, m_cash0 = _raw_snapshot({"totalCash": 0, "totalDebt": 0, "availableCash": 0,
                               "depositInterest": 318, "cashDividendReceiving": 0})
_h_cash0 = holdings(BASE_LOTS, cash=0.0, total_cash=m_cash0["total_cash_vnd"],
                    debt=m_cash0["total_debt_vnd"])
r18k = run(_h_cash0)
check("T18k ĐƯỜNG THẬT: dnse_raw totalCash=0 VÀ totalDebt=0 (sổ PARK 1.000tr) ⇒ "
      "BLOCKED_CASH_BASIS, 0 lệnh — KHÔNG bán sạch sổ",
      r18k["decision"] == "BLOCKED_CASH_BASIS" and not r18k["orders"],
      f"{r18k['decision']} n_orders={len(r18k['orders'])}")
# CHỨNG MINH NGƯỢC: chính sổ đó, nếu mẫu số tin con số hỏng thay vì fail-closed ⇒ thảm hoạ thật.
# Dùng totalCash = 1đ (KHÔNG phải 0) để lách đúng cái guard vừa dựng — mục đích ở đây là đo HẬU
# QUẢ của một mẫu số gần-như-chỉ-còn-park_mv, không phải kiểm lại guard (T18k đã kiểm).
r18k_bad = run(holdings(BASE_LOTS, cash=0.0, total_cash=1.0, debt=0.0))
_sold = sum(o["qty"] * PX[o["ticker"]] for o in r18k_bad["orders"])
check("T18l CHỨNG MINH NGƯỢC — nếu tin mẫu số 0 thì PARK = 100% pool ⇒ TRIM bán ≥190tr "
      "(≈ gần sạch phần vượt trần); đó chính là thứ T18k chặn",
      r18k_bad["decision"] == "TRIM" and _sold >= 190e6,
      f"{r18k_bad['decision']} bán {_sold:,.0f}")

# ── T18p-T18t: khe hở quant-skeptic vòng 3 — lỗi feed chỉ ăn HAI trong ba field ────
# Guard "cả ba field = 0" KHÔNG bắt được ca này: totalCash=0, totalDebt=0 (hỏng) nhưng
# availableCash còn sống ⇒ pool = 0 + park_mv ⇒ TRIM BÁN SẠCH 100% sổ PARK. Reviewer dựng lại
# được bằng cách gọi thẳng compute_trim(). Bịt bằng BẤT BIẾN totalCash ⊇ availableCash.
r18p = run(holdings(BASE_LOTS, cash=5e6, total_cash=0.0, debt=0.0))
check("T18p ca vòng 3: totalCash=0 & totalDebt=0 nhưng availableCash=5tr (feed ăn 2/3 field) "
      "⇒ BLOCKED_CASH_BASIS, 0 lệnh — KHÔNG bán sạch sổ",
      r18p["decision"] == "BLOCKED_CASH_BASIS" and not r18p["orders"],
      f"{r18p['decision']} n_orders={len(r18p['orders'])}")
check("T18q CHỨNG MINH NGƯỢC — bỏ bất biến đi thì chính sổ đó cho pool = park_mv (PARK 100%) "
      "⇒ mức bán = toàn bộ phần vượt trần 200tr",
      close(1_000e6 - 0.80 * (0.0 + 1_000e6), 200e6, 1))
check("T18r bất biến KHÔNG chặn nhầm ca thường: totalCash 420tr > availableCash 20tr ⇒ chạy bình "
      "thường (đây là hình dạng SpaceX 08-07 thật)",
      run(holdings(BASE_LOTS, cash=20e6, total_cash=420e6))["decision"] in ("TRIM", "NO_TRIM"))
check("T18s bất biến CHO PHÉP totalCash == availableCash (tài khoản không có gì chưa settle)",
      run(holdings(BASE_LOTS, cash=100e6, total_cash=100e6))["decision"] in ("TRIM", "NO_TRIM"))
check("T18t _cash_fields_inconsistent: tc<ac ⇒ True; tc≥ac ⇒ False; thiếu field ⇒ False",
      PH._cash_fields_inconsistent({"totalCash": 0, "availableCash": 5e6})
      and not PH._cash_fields_inconsistent({"totalCash": 420e6, "availableCash": 20e6})
      and not PH._cash_fields_inconsistent({"totalCash": 100e6, "availableCash": 100e6})
      and not PH._cash_fields_inconsistent({"totalDebt": 0}))
# ĐƯỜNG THẬT cho cùng khe hở đó (dnse_raw → read_broker_snapshot → compute_trim).
_, _, m_partial = _raw_snapshot({"totalCash": 0, "totalDebt": 0, "availableCash": 5e6,
                                 "depositInterest": 318, "cashDividendReceiving": 0})
check("T18u ĐƯỜNG THẬT: dnse_raw ăn 2/3 field ⇒ read_broker_snapshot trả total_cash=None "
      "⇒ consumer fail-closed",
      m_partial["total_cash_vnd"] is None and m_partial["balance_all_zero"] is True,
      f"{m_partial['total_cash_vnd']} / {m_partial['balance_all_zero']}")

# ── T19: §pool-egg (2026-08-19) — tái lập ĐÚNG sự cố thật (user hỏi "đâu phải kỳ rebalance,
# sao lại TRIM"). Cùng sổ PARK, cùng cash_total, chỉ khác: một phần vốn đã chuyển sang Trứng
# vàng (egg). KHÔNG cộng egg ⇒ TRIM oan; CÓ cộng egg ⇒ NO_TRIM/trim nhỏ hơn đúng bằng phần vốn
# đó. Đây là bug THẬT đã xảy ra (SpaceX 08-18: totalCash rơi 100,2tr, egg tăng ~100,2tr).
r19_no_egg = run(holdings(BASE_LOTS, cash=0.0, total_cash=100e6, debt=0.0, egg=0.0))
r19_with_egg = run(holdings(BASE_LOTS, cash=0.0, total_cash=100e6, debt=0.0, egg=100e6))
check("T19a KHÔNG cộng egg — sổ hệt T18 base nhưng cash chỉ còn 100tr (phần kia đã sang egg) "
      "⇒ TRIM oan (đúng chữ ký sự cố thật 08-19)",
      r19_no_egg["decision"] == "TRIM",
      f"{r19_no_egg['decision']} pool={r19_no_egg.get('pool_vnd')}")
check("T19b CÓ cộng egg 100tr (đúng số đã 'biến mất' khỏi cash) ⇒ pool phục hồi về 1.100tr, "
      "target 880tr > PARK 1.000tr? — PARK vẫn > target nên vẫn TRIM, nhưng NHẸ HƠN HẲN "
      "(egg bù đúng phần đã mất, không bù thêm/bớt)",
      close(r19_with_egg["pool_vnd"], r19_no_egg["pool_vnd"] + 100e6, 1)
      and r19_with_egg["delta_vnd"] > r19_no_egg["delta_vnd"],
      f"pool no_egg={r19_no_egg['pool_vnd']:,.0f} with_egg={r19_with_egg['pool_vnd']:,.0f} "
      f"delta no_egg={r19_no_egg['delta_vnd']:,.0f} with_egg={r19_with_egg['delta_vnd']:,.0f}")
check("T19c egg_assets_vnd được ghi lại nguyên vẹn vào output (audit trail — không bị nuốt "
      "âm thầm trong phép cộng)",
      r19_with_egg.get("egg_assets_vnd") == 100e6 and r19_no_egg.get("egg_assets_vnd") == 0.0,
      f"{r19_with_egg.get('egg_assets_vnd')} / {r19_no_egg.get('egg_assets_vnd')}")
check("T19d không khai egg (default 0.0, mọi ca T1-T18 cũ) ⇒ hành vi Y HỆT trước khi vá — "
      "không có regression cho holdings không mang field mới",
      run(holdings(BASE_LOTS, cash=100e6, total_cash=420e6))["pool_vnd"]
      == run(holdings(BASE_LOTS, cash=100e6, total_cash=420e6, egg=0.0))["pool_vnd"])

# ĐƯỜNG THẬT: dnse_raw có field "egg" sibling của "stock" (đúng schema thật, xem
# data/execution_logs/dnse_raw_2026-08-18.jsonl) ⇒ read_broker_snapshot() (historical branch,
# park_holdings.py) phải đọc ra egg_assets_vnd đúng, KHÔNG chỉ fixture bơm tay ở trên.
def _raw_snapshot_egg(stock_block, egg_value):
    with tempfile.TemporaryDirectory() as td:
        acc, day = "0009999999", "2026-08-07"
        with open(os.path.join(td, f"dnse_raw_{day}.jsonl"), "w", encoding="utf-8") as f:
            f.write(json.dumps({"account_no": acc, "kind": "positions", "ts": f"{day}T19:00:00",
                                "payload": {"positions": [{"accountNo": acc, "symbol": "AAA",
                                                           "openQuantity": 100,
                                                           "marketPrice": 10000,
                                                           "tradeQuantity": 100}]}}) + "\n")
            f.write(json.dumps({"account_no": acc, "kind": "balances", "ts": f"{day}T19:01:00",
                                "payload": {"stock": stock_block,
                                            "egg": {"totalValue": egg_value}}}) + "\n")
        return PH.read_broker_snapshot("TEST", acc, day, exec_dir=td)


_, _, m_egg = _raw_snapshot_egg({"totalCash": 9_783_984, "totalDebt": 0,
                                 "availableCash": 4_382, "depositInterest": 318,
                                 "cashDividendReceiving": 9_775_000}, 100_223_898)
check("T19e ĐƯỜNG THẬT (historical branch) — dnse_raw có sibling \"egg\" đúng schema thật ⇒ "
      "read_broker_snapshot() đọc ra egg_assets_vnd đúng số (số thật SpaceX 08-18)",
      m_egg["egg_assets_vnd"] == 100_223_898.0,
      f"egg_assets_vnd={m_egg.get('egg_assets_vnd')}")
_, _, m_egg_zero = _raw_snapshot_egg({"totalCash": 100e6, "totalDebt": 0, "availableCash": 20e6,
                                      "depositInterest": 318, "cashDividendReceiving": 0}, 0)
check("T19f ĐƯỜNG THẬT — egg=0 (tài khoản không dùng Trứng vàng) ⇒ egg_assets_vnd=0.0, "
      "không lỗi/None",
      m_egg_zero["egg_assets_vnd"] == 0.0,
      f"egg_assets_vnd={m_egg_zero.get('egg_assets_vnd')}")

print(f"\n=== {len(PASS)} PASS / {len(FAIL)} FAIL ===")
if FAIL:
    for f in FAIL:
        print(f"  ✗ {f}")
sys.exit(1 if FAIL else 0)
