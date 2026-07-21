# -*- coding: utf-8 -*-
"""Self-check trần %ADV cho book LAG — `trading_bot.plan.cap_lag_orders`.

Đóng lỗ hổng live-vs-backtest phát hiện 2026-07-21 (job Taylor_20260721_130404/_133858):
backtest pinned R3 mô phỏng LAG với liquidity_volume_pct=0.20, đường live không có trần nào.

Chạy: $DNA_PYEXE lag_adv_cap_selfcheck.py   (hoặc python3 — không phụ thuộc pickle pandas3)
Mọi case đều monkeypatch `_adv_for_gate`, KHÔNG đọc bq_cache thật, trừ case cuối (E) đọc
cache thật cho IVS/TMG/TRC để xem trần áp ra số bao nhiêu trên chính rổ LAG 07-24.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trading_bot import plan as planmod  # noqa: E402
from trading_bot.plan import PlannedOrder, TradePlan, cap_lag_orders, LAG_ADV_PCT  # noqa: E402

FAILS = []
NCHECK = [0]


def check(name, cond, detail=""):
    NCHECK[0] += 1
    print(("  ✅ " if cond else "  ❌ ") + name + (f" — {detail}" if detail else ""))
    if not cond:
        FAILS.append(name)


def mkplan(orders, plan_date="2026-07-24"):
    return TradePlan(plan_date=plan_date, signal_date="2026-07-23", strategy="V2.4",
                     strategy_version="r3", state=3, state_name="NEUTRAL",
                     nav_basis={}, orders=orders, account="selfcheck_lagadv")


def order(tk, qty, px=10_000, book="LAG", side="buy"):
    return PlannedOrder(id=f"{side.upper()}-{tk}", ticker=tk, side=side, qty=qty,
                        ref_price=px, book=book)


def fake_adv(mapping, data_date="2026-07-23"):
    """mapping: ticker -> adv(float) | ("ERR", msg) | (adv, data_date)."""
    def _f(ticker, asof):
        v = mapping.get(ticker)
        if v is None:
            return None, None, "không có dòng nào trong bq_cache/ticker"
        if isinstance(v, tuple) and v[0] == "ERR":
            return None, None, v[1]
        if isinstance(v, tuple):
            return float(v[0]), v[1], None
        return float(v), data_date, None
    return _f


_orig_adv = planmod._adv_for_gate
ONE = ["SpaceX"]              # 1 account live → share = 1.0
TWO = ["SpaceX", "ZaloPay"]   # 2 account live → share = 0.5

# ── A. ADV bình thường: KHÔNG đổi hành vi ────────────────────────────────────────────
print("\nA. ADV bình thường — lệnh nhỏ hơn trần, không đổi gì")
planmod._adv_for_gate = fake_adv({"TRC": 10e9})   # trần = 20% × 10 tỷ = 2 tỷ
p, adj = cap_lag_orders(mkplan([order("TRC", 10_000, 20_000)]), "SpaceX", live_labels=ONE)
check("qty giữ nguyên", p.orders[0].qty == 10_000, f"qty={p.orders[0].qty} (200tr < trần 2 tỷ)")
check("không có điều chỉnh nào", adj == [], f"adj={adj}")

print("\nA2. Order KHÔNG phải LAG-buy → gate không đụng tới")
planmod._adv_for_gate = fake_adv({})   # mọi mã đều 'không có dữ liệu' → nếu đụng sẽ BLOCK
p, adj = cap_lag_orders(mkplan([order("AAA", 99_999, book="BAL"),
                                order("BBB", 99_999, book="CAPIT"),
                                order("CCC", 99_999, book="LAG", side="sell"),
                                order("DDD", 99_999, book="")]), "SpaceX", live_labels=ONE)
check("cả 4 lệnh non-LAG-buy đi qua nguyên vẹn", len(p.orders) == 4 and adj == [],
      f"n={len(p.orders)} adj={len(adj)}")

# ── B. ADV mỏng: cắt đúng 20% ────────────────────────────────────────────────────────
print("\nB. ADV mỏng — cắt đúng 20% ADV, làm tròn lô")
planmod._adv_for_gate = fake_adv({"IVS": 1e9})    # trần = 200tr @ 10.000đ = 20.000cp
p, adj = cap_lag_orders(mkplan([order("IVS", 50_000, 10_000)]), "SpaceX", live_labels=ONE)
check("action=TRIMMED", adj and adj[0]["action"] == "TRIMMED", str(adj[:1]))
check("cắt về đúng 20.000 cp", p.orders[0].qty == 20_000, f"qty={p.orders[0].qty}")
check("giá trị sau cắt == 20% ADV", abs(p.orders[0].qty * 10_000 - 0.20 * 1e9) < 1e-6)
check("LAG_ADV_PCT khớp backtest LIQ_LAG", LAG_ADV_PCT == 0.20, f"={LAG_ADV_PCT}")

print("\nB2. Chia theo số account live — 2 account thì mỗi bên chỉ được 1/2 trần")
p, adj = cap_lag_orders(mkplan([order("IVS", 50_000, 10_000)]), "SpaceX", live_labels=TWO)
check("share=0.5 → cắt về 10.000 cp", p.orders[0].qty == 10_000, f"qty={p.orders[0].qty}")
p2, _ = cap_lag_orders(mkplan([order("IVS", 50_000, 10_000)]), "ZaloPay", live_labels=TWO)
check("tổng 2 account = đúng 20% ADV, không phải 40%",
      (p.orders[0].qty + p2.orders[0].qty) * 10_000 == 0.20 * 1e9,
      f"tổng={(p.orders[0].qty + p2.orders[0].qty) * 10_000:,.0f}đ")
p3, _ = cap_lag_orders(mkplan([order("IVS", 50_000, 10_000)]), "main", live_labels=TWO,
                       account_mode="paper")
check("account paper dùng CÙNG share với live (không phải 1.0 → không lệch paper-vs-live)",
      p3.orders[0].qty == 10_000, f"qty={p3.orders[0].qty}")

print("\nB3. Làm tròn xuống lô — không bao giờ vượt trần vì làm tròn")
planmod._adv_for_gate = fake_adv({"XXX": 1.234e9})   # trần 246,8tr @ 10.000 = 24.68 lô lẻ
p, adj = cap_lag_orders(mkplan([order("XXX", 99_999, 10_000)]), "SpaceX", live_labels=ONE)
check("qty là bội số 100", p.orders[0].qty % 100 == 0, f"qty={p.orders[0].qty}")
check("giá trị ≤ trần", p.orders[0].qty * 10_000 <= 0.20 * 1.234e9,
      f"{p.orders[0].qty * 10_000:,.0f} ≤ {0.20 * 1.234e9:,.0f}")

# ── C. FAIL-CLOSED ───────────────────────────────────────────────────────────────────
print("\nC. Fail-closed — mọi trường hợp không đo được ADV phải CHẶN, không thả")
cases = [
    ("mã không có trong cache", {"ZZZ": None}, "ZZZ", 10_000),
    ("lỗi đọc cache", {"ZZZ": ("ERR", "bq_cache/ticker rỗng")}, "ZZZ", 10_000),
    ("ADV = 0 (TMG: Volume_3M_P50=0)", {"TMG": 0.0}, "TMG", 10_000),
    ("ADV âm (dữ liệu hỏng)", {"ZZZ": -5.0}, "ZZZ", 10_000),
    ("dữ liệu ADV quá cũ (>30 ngày)", {"ZZZ": (10e9, "2026-05-01")}, "ZZZ", 10_000),
]
for label, mp, tk, qty in cases:
    planmod._adv_for_gate = fake_adv(mp)
    p, adj = cap_lag_orders(mkplan([order(tk, qty)]), "SpaceX", live_labels=ONE)
    check(f"CHẶN: {label}", p.orders == [] and adj and adj[0]["action"] == "BLOCKED",
          adj[0]["reason"][:90] if adj else "KHÔNG chặn (!!)")

planmod._adv_for_gate = fake_adv({"ZZZ": 10e9})
p, adj = cap_lag_orders(mkplan([order("ZZZ", 100, px=0)]), "SpaceX", live_labels=ONE)
check("CHẶN: ref_price=0", p.orders == [] and adj and adj[0]["action"] == "BLOCKED",
      adj[0]["reason"][:80] if adj else "KHÔNG chặn (!!)")

planmod._adv_for_gate = fake_adv({"ZZZ": 1e6})   # trần 200k < 1 lô @ 10.000 (=1tr)
p, adj = cap_lag_orders(mkplan([order("ZZZ", 500, 10_000)]), "SpaceX", live_labels=ONE)
check("CHẶN: trần < 1 lô", p.orders == [] and adj and adj[0]["action"] == "BLOCKED",
      adj[0]["reason"][:80] if adj else "KHÔNG chặn (!!)")


def _boom(*a, **k):
    raise RuntimeError("load_accounts hỏng")


planmod._adv_for_gate = fake_adv({"ZZZ": 10e9})
import trading_bot.config as cfgmod  # noqa: E402
_orig_la = cfgmod.load_accounts
cfgmod.load_accounts = _boom
p, adj = cap_lag_orders(mkplan([order("ZZZ", 100)]), "SpaceX")
cfgmod.load_accounts = _orig_la
check("CHẶN: không dựng được danh sách account live (exception)",
      p.orders == [] and adj and adj[0]["action"] == "BLOCKED",
      adj[0]["reason"][:80] if adj else "KHÔNG chặn (!!)")

# ── C3. Hai case FAIL-OPEN mà quant-skeptic bắt được (REFUTED bản đầu 2026-07-21) ─────
print("\nC3. Fail-OPEN đã sửa — danh sách live rỗng / account live không có trong danh sách")
planmod._adv_for_gate = fake_adv({"IVS": 1e9})
p, adj = cap_lag_orders(mkplan([order("IVS", 50_000, 10_000)]), "SpaceX", live_labels=[])
check("CHẶN: live_labels rỗng (trước đây âm thầm share=1.0 → mua full trần)",
      p.orders == [] and adj and adj[0]["action"] == "BLOCKED",
      adj[0]["reason"][:100] if adj else "KHÔNG chặn (!!) — fail-open tái diễn")
p, adj = cap_lag_orders(mkplan([order("IVS", 50_000, 10_000)]), "NewBroker",
                        live_labels=["SpaceX", "ZaloPay"])
check("CHẶN: account live KHÔNG có trong danh sách (vd broker ngoài DNSE) — "
      "trước đây mỗi bên enforce full 20% ⇒ tổng 40% ADV",
      p.orders == [] and adj and adj[0]["action"] == "BLOCKED",
      adj[0]["reason"][:100] if adj else "KHÔNG chặn (!!) — bug 40% ADV tái diễn")
p, adj = cap_lag_orders(mkplan([order("IVS", 50_000, 10_000)]), "main", live_labels=[],
                        account_mode="paper")
check("paper + live_labels rỗng → KHÔNG chặn, share=1.0 (paper không tiêu thanh khoản thật)",
      p.orders and p.orders[0].qty == 20_000,
      f"qty={p.orders[0].qty if p.orders else 'BLOCKED'}")

print("\nC4. Nguồn N = MỌI broker, không chỉ DNSE (live_dnse_labels lọc broker='dnse')")
src_plan = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "trading_bot", "plan.py"), encoding="utf-8").read()
_fn = src_plan[src_plan.index("def cap_lag_orders"):src_plan.index("def _adv_for_gate")]
# bỏ docstring trước khi soi — docstring CÓ nhắc live_dnse_labels để giải thích vì sao KHÔNG dùng
_body = _fn.split('"""')[2] if _fn.count('"""') >= 2 else _fn
check("thân hàm KHÔNG import/gọi live_dnse_labels", "live_dnse_labels" not in _body)
check("dùng load_accounts + lọc mode=='live'",
      "load_accounts" in _fn and '"live"' in _fn)

print("\nC2. Chặn 1 mã KHÔNG được ảnh hưởng mã khác trong cùng plan")
planmod._adv_for_gate = fake_adv({"TMG": 0.0, "TRC": 10e9})
p, adj = cap_lag_orders(mkplan([order("TMG", 10_000), order("TRC", 100),
                                order("KEEP", 10_000, book="BAL")]), "SpaceX", live_labels=ONE)
tks = sorted(o.ticker for o in p.orders)
check("TMG bị chặn, TRC + BAL giữ nguyên", tks == ["KEEP", "TRC"], f"còn lại {tks}")

# ── D. Wiring ────────────────────────────────────────────────────────────────────────
print("\nD. Wiring vào bot_execute.py")
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot_execute.py"),
           encoding="utf-8").read()
check("import cap_lag_orders", "cap_lag_orders" in src.split("def ")[0])
check("gọi cap_lag_orders(plan, p[\"label\"], account_mode=cfg[\"mode\"])",
      "cap_lag_orders(plan, p[\"label\"], account_mode=cfg[\"mode\"])" in src)
check("gọi SAU cap_capit_orders và TRƯỚC approval gate",
      src.index("cap_capit_orders(plan") < src.index("cap_lag_orders(plan")
      < src.index("approval_block_reason(plan)"))

# ── E. Rổ LAG 07-24 thật (đọc bq_cache thật) ─────────────────────────────────────────
print("\nE. Rổ LAG 07-24 thật — IVS / TMG / TRC (bq_cache thật, không monkeypatch)")
planmod._adv_for_gate = _orig_adv
from trading_bot.due_diligence import adv_vnd  # noqa: E402
for tk in ("IVS", "TMG", "TRC"):
    adv, dd, err = adv_vnd(tk, "2026-07-23")
    if err:
        print(f"  · {tk}: ADV n/a — {err}  → gate sẽ CHẶN (fail-closed)")
        continue
    cap1 = LAG_ADV_PCT * adv * 1.0
    cap2 = LAG_ADV_PCT * adv * 0.5
    print(f"  · {tk}: ADV {adv/1e9:,.3f} tỷ (data {dd}) → trần 1 account live "
          f"{cap1/1e6:,.0f} tr/phiên; 2 account live {cap2/1e6:,.0f} tr/phiên mỗi bên"
          + ("   ⛔ ADV=0 → CHẶN HOÀN TOÀN" if adv <= 0 else ""))

print("\n" + "=" * 72)
print(f"KẾT QUẢ: {NCHECK[0] - len(FAILS)}/{NCHECK[0]} — "
      f"{'PASS' if not FAILS else 'FAIL: ' + ', '.join(FAILS)}")
sys.exit(1 if FAILS else 0)
