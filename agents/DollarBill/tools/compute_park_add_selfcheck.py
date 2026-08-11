#!/usr/bin/env python3
"""Self-check cho `compute_park_add.py` — đường MUA (P2) của sổ PARK.

VÌ SAO CÓ FILE NÀY (2026-08-11, job DollarBill_20260810_185924): quant-skeptic
(`mike/logs/verify_20260810_191101_3573336.log`) trả **REFUTED / confidence high** cho luận điểm
"P2 là ảnh đối xứng đại số của L1 nên thừa hưởng được độ an toàn của L1". Mục
`reproducibility_selfcheck` ghi thẳng: *"fail — NO compute_park_add_selfcheck.py exists, while L1
ships mike/bin/compute_park_trim_selfcheck.py"*, và lý do nó coi đây là lỗi nặng chứ không phải
thiếu sót hình thức: **ba guard tiền của L1 từng bị chính quant-skeptic vòng 2/3 phá được qua
đường gọi trực tiếp `compute_trim(holdings=...)`** — đúng đường mà file này test.

Bốn khiếm khuyết quant-skeptic tìm ra đã được vá trong `compute_park_add.py` cùng ngày; file này
là thứ giữ cho chúng KHÔNG bị gỡ ra lần sau. Mỗi ca dưới đây neo vào đúng một khiếm khuyết đó:

  · T20-T22  clamp `scale_delta` — thiếu nó, mua trọn Σwant đẩy PARK lên **84,04% (SpaceX) /
             87,38% (ZaloPay)** so với trần 80% mà chính L1 sinh ra để giữ (số đo thật 08-11).
  · T30-T31  cổng DT5G `SKIP_STATE` — thiếu nó, tool size một lệnh mua 80% pool giữa BEAR/CRISIS.
  · T40-T43  ba guard tiền của L1 (`debt is None` KHÔNG được ép về 0; chữ ký feed toàn-0;
             bất biến `totalCash ≥ availableCash`).
  · T50-T52  `name_cap` 0,10 NAV — trước khi vá, `active_nav_vnd=None` âm thầm TẮT trần này.

Theo skill `verify-before-done`:
  · KHÔNG đọc `data/golive_v23_status.json` thật — mọi ca patch `cpa.STATE_FILE` sang file tạm.
    Không patch thì state live ≠ NEUTRAL sẽ làm MỌI ca trả SKIP_STATE và selfcheck "PASS" giả.
  · KHÔNG gọi mạng: `price_fn`/`adv_fn`/`share_override`/`day_cap_override`/`basket_override`
    bơm tay hết.
  · Ca "chặn được" đều có **ca chứng minh ngược** (bỏ ràng buộc ⇒ thật sự vượt), không khẳng
    định suông — cùng kỷ luật `hard_no_chase_ceiling_selfcheck.py` (§24).
  · Chạy lại toàn bộ dưới `env -u TZ` + ICT + UTC + America/New_York (bẫy §16).

Chạy:  python3 mike/agents/DollarBill/tools/compute_park_add_selfcheck.py
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import compute_park_add as cpa                                   # noqa: E402
from trading_bot.vn_market import LOT                            # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'} — {name}" + (f"  [{detail}]" if detail else ""))


def close(a, b, tol=1.0):
    return abs(float(a) - float(b)) <= tol


# ── Fixture: rổ + giá + sổ, số tròn để kiểm TAY được ─────────────────────────
# PC1 = BANNED vĩnh viễn. TIN = trọng số quá nhỏ so với 1 lô ⇒ phải bị loại khỏi rổ khả thi.
BASKET = {"AAA": 0.40, "BBB": 0.25, "CCC": 0.20, "PC1": 0.10, "DDD": 0.045, "TIN": 0.005}
PX = {"AAA": 10_000, "BBB": 20_000, "CCC": 50_000, "DDD": 30_000,
      "TIN": 60_000, "PC1": 40_000, "XCL": 25_000}
BIG_CAP = 10e12          # trần TỔNG/phiên rộng ⇒ không binding trừ khi ca cố ý siết
BIG_NAV = 10_000e6       # NAV rộng ⇒ name_cap 0,10 không binding trừ khi ca cố ý siết
SHARE = 0.5
ASOF = "2026-08-11"
M = 1e6

# Sổ chuẩn: PARK 500tr + tiền 500tr ⇒ pool 1.000tr, target 80% = 800tr, delta = 300tr.
#   AAA 200tr (DƯỚI target 357,542tr)   BBB 300tr (TRÊN target 223,464tr ⇒ overweight)
# Chính BBB tạo ra bất đẳng thức Σwant > delta — hạt nhân của ca clamp T20.
BASE_LOTS = [("AAA", 20_000), ("BBB", 15_000)]
FIXTURE_DEBT = 50e6      # sổ mặc định KHÔNG được trùng chữ ký lỗi feed toàn-0 (xem T42)

# Số kỳ vọng tính TAY (đơn vị tr đồng), dùng lại ở nhiều ca:
#   rổ khả thi sau khi bỏ PC1 (BANNED) + TIN (<1 lô): Σw = 0,895
#   tgt_AAA = 800 × 0,40/0,895 = 357,5419  · tgt_BBB = 800 × 0,25/0,895 = 223,4637
#   tgt_CCC = 800 × 0,20/0,895 = 178,7709  · tgt_DDD = 800 × 0,045/0,895 = 40,2235
#   want = (157,5419 ; 0 ; 178,7709 ; 40,2235)  ⇒ Σwant = 376,5363 > delta = 300
#   thừa = Σwant − delta = 76,5363 = ĐÚNG phần vượt trọng số của BBB (300 − 223,4637)
TGT = {"AAA": 800 * 0.40 / 0.895, "BBB": 800 * 0.25 / 0.895,
       "CCC": 800 * 0.20 / 0.895, "DDD": 800 * 0.045 / 0.895}
WANT_TOTAL = (TGT["AAA"] - 200) + TGT["CCC"] + TGT["DDD"]
DELTA = 300.0


def price_fn(tk):
    return (PX.get(tk), None) if tk in PX else (None, "không có giá test")


def adv_fn_ok(adv=1e12, per_ticker=None):
    def _f(tk, asof):
        a = (per_ticker or {}).get(tk, adv)
        return (a, asof, None)
    return _f


def holdings(lots=None, cash=500 * M, excluded=(), unver=(), reconcile_ok=True,
             total_cash="net_zero", div_recv=0.0, debt="net_zero"):
    """lots = [(ticker, qty)] — mv tính từ PX.

    `total_cash`/`debt` mặc định "net_zero": tài khoản có ĐÚNG `FIXTURE_DEBT` đồng tiền và
    `FIXTURE_DEBT` đồng nợ chồng lên `cash` ⇒ totalCash − totalDebt = cash, giữ nguyên mọi con số
    kỳ vọng ở trên, mà sổ vẫn KHÔNG trùng chữ ký lỗi feed DNSE toàn-0 (T42 chặn chữ ký đó).
    """
    lots = BASE_LOTS if lots is None else lots
    if total_cash == "net_zero" and debt == "net_zero":
        total_cash, debt = cash + FIXTURE_DEBT, FIXTURE_DEBT
    else:
        total_cash = cash if total_cash == "net_zero" else total_cash
        debt = 0.0 if debt == "net_zero" else debt
    park_lots = [{"ticker": t, "qty": q, "market_price": PX[t], "mv_vnd": q * PX[t],
                  "price": PX[t], "entry_date": "2026-05-05", "source": "j1", "book": "PARK"}
                 for (t, q) in lots]
    per = {}
    for l in park_lots:
        per[l["ticker"]] = per.get(l["ticker"], 0) + l["qty"]
    bpos = {t: {"qty": q, "market_price": PX[t], "sellable": q} for t, q in per.items()}
    return {"account_label": "TEST", "asof": ASOF,
            "park_lots": park_lots, "broker_positions": bpos,
            "park_mv_vnd": sum(l["mv_vnd"] for l in park_lots),
            "cash_available_vnd": cash,
            "cash_total_vnd": total_cash,
            "cash_dividend_receiving_vnd": div_recv,
            "cash_debt_vnd": debt,
            "cash_basis": "total_cash",
            "reconcile": {"ok": reconcile_ok,
                          "mismatches": [] if reconcile_ok else [{"ticker": "AAA", "diff": 100}]},
            "unverified_tickers": list(unver), "excluded_tickers": list(excluded)}


def run(state=3, **kw):
    """Gọi compute_add với mọi cổng ngoài đã bơm tay (không mạng, không file production)."""
    kw.setdefault("holdings", holdings())
    kw.setdefault("basket_override", BASKET)
    kw.setdefault("share_override", SHARE)
    kw.setdefault("day_cap_override", BIG_CAP)
    kw.setdefault("adv_fn", adv_fn_ok())
    kw.setdefault("price_fn", price_fn)
    kw.setdefault("active_nav_vnd", BIG_NAV)
    kw.setdefault("asof", ASOF)
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        if state is not None:
            json.dump({"state": state, "state_name": {3: "NEUTRAL", 1: "BEAR", 0: "CRISIS"}.get(state),
                       "date": ASOF, "etf_park_frac": 0.8}, f)
            path = f.name
        else:
            path = f.name          # file rỗng ⇒ nhánh "không đọc được state"
            f.write("{}")
    old = cpa.STATE_FILE
    cpa.STATE_FILE = path
    try:
        return cpa.compute_add("TEST", **kw)
    finally:
        cpa.STATE_FILE = old
        os.unlink(path)


def spent_with_fee(r):
    return sum(o["qty"] * o["ref_price"] for o in r["orders"]) * (1.0 + cpa.FEE_RATE)


# ═══════════════════════════════════════════════════════════════════════════
print("\n── T1x: đường cơ sở — phân bổ đúng, mọi trần tôn trọng ──")
r = run()
check("T10 decision=ADD", r["decision"] == "ADD", r["decision"])
check("T11 rổ khả thi = 4 mã (bỏ PC1 BANNED + TIN <1 lô)", r["basket_feasible_n"] == 4,
      f"n={r['basket_feasible_n']}")
check("T12 PC1 (BANNED) bị loại khỏi rổ, KHÔNG có lệnh",
      "PC1" not in {o["ticker"] for o in r["orders"]}
      and any(d["ticker"] == "PC1" and "BANNED" in d["reason"] for d in r["basket_dropped"]))
check("T13 TIN bị loại vì target < 1 lô",
      any(d["ticker"] == "TIN" and "1 lô" in d["reason"] for d in r["basket_dropped"]))
check("T14 target/mã khớp tính tay (chuẩn hoá trên Σw=0,895)",
      all(close(r["target_value_vnd"][t], TGT[t] * M, tol=1.0) for t in TGT),
      f"AAA={r['target_value_vnd']['AAA']:,.0f} vs {TGT['AAA']*M:,.0f}")
check("T15 mọi qty là bội của LOT", all(o["qty"] % LOT == 0 for o in r["orders"]))
check("T16 Σ chi (gồm phí) ≤ hard_budget", spent_with_fee(r) <= r["hard_budget_vnd"] + 1,
      f"{spent_with_fee(r):,.0f} ≤ {r['hard_budget_vnd']:,.0f}")
check("T17 Σ chi (gồm phí) ≤ budget", spent_with_fee(r) <= r["budget_vnd"] + 1)
check("T18 KHÔNG mã nào bị đẩy VƯỢT trọng số mục tiêu của nó",
      all(o["mv_vnd"] + o["value_vnd"] <= o["target_vnd"] + 1 for o in r["orders"]))
check("T19 BBB (đang vượt target) nằm ở at_or_above_target, KHÔNG có lệnh",
      "BBB" in {x["ticker"] for x in r["at_or_above_target"]}
      and "BBB" not in {o["ticker"] for o in r["orders"]})

print("\n── T2x: CLAUSE CLAMP `scale_delta` (khiếm khuyết #2 quant-skeptic 08-11) ──")
check("T20 Σwant > delta đúng bằng phần THỪA của mã overweight (bất biến đại số)",
      close(r["structural_deficit_vnd"], WANT_TOTAL * M, tol=100)
      and close(r["overshoot_if_unclamped_vnd"], (WANT_TOTAL - DELTA) * M, tol=100),
      f"Σwant={r['structural_deficit_vnd']:,.0f} thừa={r['overshoot_if_unclamped_vnd']:,.0f} "
      f"(BBB vượt {(300 - TGT['BBB']) * M:,.0f})")
check("T21 CHỨNG MINH NGƯỢC: KHÔNG clamp thì thật sự vượt trần 80%",
      r["park_pct_if_unclamped"] > r["target_park"] + 0.02,
      f"unclamped={r['park_pct_if_unclamped']:.4f} > target={r['target_park']:.2f}")
check("T22 CÓ clamp ⇒ PARK sau khi mua KHÔNG vượt target, overpark = 0",
      r["park_pct_after"] <= r["target_park"] + 1e-9 and r["overpark_after_vnd"] == 0.0,
      f"after={r['park_pct_after']:.4f} overpark={r['overpark_after_vnd']:,.0f}")
check("T23 clamp là ràng buộc BINDING ở ca này (delta chặt hơn tiền/thanh khoản)",
      r["delta_binding"] and not r["day_cap_binding"] and not r["cash_binding"],
      f"scale_delta={r['scale_delta']:.4f} scale_cash={r['scale_cash']:.4f}")

print("\n── T3x: cổng DT5G (khiếm khuyết #1 — mua rổ parking giữa BEAR/CRISIS) ──")
for st, nm in ((1, "BEAR"), (0, "CRISIS")):
    rs = run(state=st)
    check(f"T30 state={st} ({nm}) ⇒ SKIP_STATE, 0 lệnh",
          rs["decision"] == "SKIP_STATE" and not rs["orders"], rs["decision"])
rs = run(state=None)
check("T31 không đọc được state ⇒ BLOCKED_STATE (fail-closed), 0 lệnh",
      rs["decision"] == "BLOCKED_STATE" and not rs["orders"], rs["decision"])

print("\n── T4x: BA guard tiền của L1 (khiếm khuyết #3) ──")
rs = run(holdings=holdings(total_cash=550 * M, debt=None))
check("T40 totalDebt=None ⇒ BLOCKED_CASH_BASIS (KHÔNG ép về 0)",
      rs["decision"] == "BLOCKED_CASH_BASIS" and not rs["orders"], rs["decision"])
rs = run(holdings=holdings(total_cash=None, debt=0.0))
check("T41 totalCash=None ⇒ BLOCKED_CASH_BASIS", rs["decision"] == "BLOCKED_CASH_BASIS",
      rs["decision"])
rs = run(holdings=holdings(cash=0.0, total_cash=0.0, debt=0.0))
check("T42 mọi field tiền = 0 mà sổ PARK > 0 ⇒ BLOCKED (chữ ký lỗi feed 2026-07-27)",
      rs["decision"] == "BLOCKED_CASH_BASIS", rs["decision"])
rs = run(holdings=holdings(cash=600 * M, total_cash=500 * M, debt=0.0))
check("T43 totalCash < availableCash ⇒ BLOCKED (vi phạm bất biến kế toán §25)",
      rs["decision"] == "BLOCKED_CASH_BASIS", rs["decision"])
check("T44 CHỨNG MINH NGƯỢC: sổ tiền hợp lệ thì KHÔNG bị chặn", run()["decision"] == "ADD")

print("\n── T5x: name_cap 0,10 NAV (khiếm khuyết #4 — trước đây âm thầm TẮT) ──")
try:
    run(active_nav_vnd=None)
    check("T50 active_nav_vnd=None ⇒ fail-closed (raise), KHÔNG âm thầm bỏ trần", False,
          "không raise")
except ValueError as e:
    check("T50 active_nav_vnd=None ⇒ fail-closed (raise), KHÔNG âm thầm bỏ trần", True, str(e)[:60])
# NAV 2.500tr ⇒ name_cap = 250tr. AAA đang giữ 200tr ⇒ room chỉ còn 50tr < want (~125,5tr).
rs = run(active_nav_vnd=2500 * M)
aaa = next((o for o in rs["orders"] if o["ticker"] == "AAA"), None)
check("T51 name_cap BINDING: lệnh AAA ≤ room 50tr", aaa is not None and aaa["value_vnd"] <= 50 * M + 1,
      f"AAA={aaa['value_vnd']:,.0f} room={aaa['name_cap_room_vnd']:,.0f}" if aaa else "no AAA")
check("T52 sau lệnh, vị thế TỔNG của AAA ≤ 0,10 × NAV",
      aaa is not None and aaa["held_qty_all_books"] * PX["AAA"] + aaa["value_vnd"] <= 0.10 * 2500 * M + 1)

print("\n── T6x: các trần còn lại + nhánh fail-closed ──")
rs = run(adv_fn=adv_fn_ok(per_ticker={"CCC": 100 * M}))
ccc = next((o for o in rs["orders"] if o["ticker"] == "CCC"), None)
cap_ccc = cpa.LAG_ADV_PCT * 100 * M * SHARE
check("T60 %ADV cap BINDING trên CCC (0,20 × ADV × share)",
      ccc is not None and ccc["value_vnd"] <= cap_ccc + 1 and ccc["adv_capped"],
      f"CCC={ccc['value_vnd']:,.0f} ≤ cap={cap_ccc:,.0f}" if ccc else "no CCC")
rs = run(day_cap_override=50 * M)
check("T61 trần thanh khoản TỔNG/phiên BINDING",
      rs["day_cap_binding"] and sum(o["value_vnd"] for o in rs["orders"]) <= 50 * M + 1,
      f"Σ={sum(o['value_vnd'] for o in rs['orders']):,.0f}")
rs = run(pp0buy_vnd=100 * M)
check("T62 pp0Buy là trần THỨ HAI (ca thật ZaloPay 08-11: pp0Buy < trần tiền mặt)",
      rs["budget_vnd"] <= 100 * M + 1 and spent_with_fee(rs) <= 100 * M + 1,
      f"budget={rs['budget_vnd']:,.0f}")
rs = run(holdings=holdings(lots=[("AAA", 20_000), ("BBB", 15_000), ("CCC", 6_000)], cash=200 * M))
check("T63 PARK đã ở/trên target ⇒ NO_ADD", rs["decision"] == "NO_ADD", rs["decision"])
rs = run(holdings=holdings(div_recv=500 * M))
check("T64 toàn bộ tiền là cổ tức PHẢI THU ⇒ NO_CASH (không tiêu được, §25)",
      rs["decision"] == "NO_CASH" and not rs["orders"], rs["decision"])
rs = run(holdings=holdings(reconcile_ok=False))
check("T65 sổ lô lệch broker ⇒ BLOCKED_RECONCILE (cùng luật L1)",
      rs["decision"] == "BLOCKED_RECONCILE" and not rs["orders"], rs["decision"])
rs = run(holdings=holdings(unver=("AAA",)))
check("T66 có mã UNVERIFIED ⇒ BLOCKED_UNVERIFIED (§21)",
      rs["decision"] == "BLOCKED_UNVERIFIED" and not rs["orders"], rs["decision"])
rs = run(holdings=holdings(excluded=("AAA",)))
check("T67 excluded_tickers KHÔNG BAO GIỜ được mua",
      "AAA" not in {o["ticker"] for o in rs["orders"]}
      and any(d["ticker"] == "AAA" and "excluded" in d["reason"] for d in rs["basket_dropped"]))
rs = run(basket_override={"AAA": 0.30, "BBB": 0.20})
check("T68 rổ có Σ trọng số ≠ 1 ⇒ BLOCKED_BASKET (fail-closed)",
      rs["decision"] == "BLOCKED_BASKET", rs["decision"])
rs = run(reserve_vnd=400 * M)
check("T69 reserve (tiền đã hứa cho lệnh khác) bị trừ khỏi ngân sách TRƯỚC khi phân bổ",
      rs["budget_vnd"] <= 100 * M + 1, f"budget={rs['budget_vnd']:,.0f}")

print("\n── T7x: rổ THẬT (bắt lỗi schema CSV, đọc file, không mạng) ──")
try:
    bw, rd, err = cpa.park_target_basket(ASOF)
    check("T70 park_target_basket đọc được rổ custom30V thật, Σw ≈ 1",
          not err and bw and 0.99 <= sum(bw.values()) <= 1.01,
          f"kỳ {rd}, n={len(bw) if bw else 0}, Σ={sum(bw.values()):.4f}" if bw else str(err))
except Exception as e:                                            # noqa: BLE001
    check("T70 park_target_basket đọc được rổ custom30V thật, Σw ≈ 1", False, repr(e)[:80])

print(f"\n{'=' * 60}\nKẾT QUẢ: {len(PASS)} PASS / {len(FAIL)} FAIL")
if FAIL:
    print("FAIL:", "; ".join(FAIL))
sys.exit(1 if FAIL else 0)
