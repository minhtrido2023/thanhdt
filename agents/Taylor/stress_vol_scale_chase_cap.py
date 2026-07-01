# -*- coding: utf-8 -*-
"""Vol-scale buy chase-cap (patch#3) — paper-only activation stress harness (Taylor, 2026-07-01).

Drives the REAL executor path (trading_bot.executor.Executor._buy_chase_pct + _limit_price)
through the genuine load_config()/load_accounts() resolution, and asserts:
  0. WIRING       — paper(main) flag True, live(SpaceX) + global DEFAULT False.
  1. WIDEN        — paper, high rvol → cap widens to clamp(k*rvol, static, ceil), capped at ceil.
  2. MONOTONE     — paper, low rvol (k*rvol < static) → never below static cap.
  3. FAIL-SAFE    — paper, rvol absent / <=0 → static cap.
  4. LIMIT PRICE  — paper limit sits HIGHER than the static-cap price on the same high-rvol quote.
  5. NEG CONTROL  — live(SpaceX) cfg on the SAME high-rvol quote → static cap (flag off).

No secrets are printed. Throwaway plan label — never touches real main/SpaceX exec logs.
"""
import sys

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")

from trading_bot.config import load_config, load_accounts
from trading_bot.brokers import Quote
from trading_bot.plan import PlannedOrder, TradePlan
from trading_bot.executor import Executor

PLAN_DATE = "2026-07-01"
FAILS = []


def check(name, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        FAILS.append(name)


class FakeBroker:
    name = "fake"

    def __init__(self, quote_map):
        self.quote_map = quote_map

    def get_quote(self, symbol):
        raw = self.quote_map.get(symbol)
        return Quote(raw) if raw else None

    def get_cash(self):
        return 10_000_000_000


def raw_quote(sym, last, ref, floor, ceil, bid, ask, vol=5_000_000):
    return {"symbol": sym, "exchange": "HOSE", "lastprice": last, "refprice": ref,
            "floor": floor, "ceiling": ceil, "bidprice1": bid, "askprice1": ask,
            "totalvolume": vol}


def make_plan(orders):
    return TradePlan(plan_date=PLAN_DATE, signal_date="2026-06-30", strategy="v23",
                     strategy_version="2.4", state=3, state_name="NEUTRAL",
                     nav_basis={"account_nav": 1e9, "paper_nav": 1e9, "scale": 1.0},
                     orders=orders, account="STRESSTEST_VOLCAP",
                     created_at="2026-07-01T09:00:00")


def eff_cfg(label):
    cfg = load_config()
    for p in load_accounts(cfg):
        if p["label"] == label:
            return p["cfg"]
    raise KeyError(label)


# ---- 0. config wiring proof --------------------------------------------------
print("== 0. CONFIG WIRING (real load_config/load_accounts) ==")
paper_cfg = eff_cfg("main")
live_cfg = eff_cfg("SpaceX")
STATIC = paper_cfg["max_chase_pct_buy"]          # 0.015
K = paper_cfg["chase_cap_vol_k"]                  # 2.0
CEIL = paper_cfg["chase_cap_vol_ceil"]            # 0.04
check("paper(main) chase_cap_vol_scale_enabled == True", paper_cfg["chase_cap_vol_scale_enabled"] is True)
check("live(SpaceX) chase_cap_vol_scale_enabled == False", live_cfg["chase_cap_vol_scale_enabled"] is False)
check("global DEFAULT stays False", load_config()["chase_cap_vol_scale_enabled"] is False)
check("paper params match approved (k=2.0, ceil=0.04, static=0.015)",
      K == 2.0 and CEIL == 0.04 and STATIC == 0.015)

buy = PlannedOrder(id="BUY-01", ticker="VOL", side="buy", qty=10000, ref_price=20000, priority=1)

# ---- 1. WIDEN: high rvol, clamp to ceil -------------------------------------
print("\n== 1. WIDEN — paper, high rvol → clamp(k*rvol, static, ceil) ==")
brk = FakeBroker({"VOL": raw_quote("VOL", last=20000, ref=20000, floor=18600, ceil=21400,
                                   bid=20000, ask=25000)})
ex = Executor(make_plan([buy]), brk, dict(paper_cfg))
ex._gap_ref["VOL"] = {"prior_close": 20000, "rvol_20d": 0.05}   # 5% vol → k*rvol=0.10 → clamp to ceil
check("k*rvol beyond ceil → capped at ceil (0.04)", abs(ex._buy_chase_pct("VOL") - CEIL) < 1e-12)

ex._gap_ref["VOL"] = {"prior_close": 20000, "rvol_20d": 0.012}  # k*rvol=0.024 (between static & ceil)
check("k*rvol within band → returns k*rvol (0.024)", abs(ex._buy_chase_pct("VOL") - 0.024) < 1e-12)

# ---- 2. MONOTONE: low rvol never below static -------------------------------
print("\n== 2. MONOTONE — paper, low rvol (k*rvol < static) → static floor ==")
ex._gap_ref["VOL"] = {"prior_close": 20000, "rvol_20d": 0.005}  # k*rvol=0.01 < static 0.015
check("k*rvol below static → clamps up to static", abs(ex._buy_chase_pct("VOL") - STATIC) < 1e-12)

# ---- 3. FAIL-SAFE: rvol absent / <=0 → static -------------------------------
print("\n== 3. FAIL-SAFE — paper, rvol missing / <=0 → static ==")
ex._gap_ref.pop("VOL", None)
check("rvol absent → static", abs(ex._buy_chase_pct("VOL") - STATIC) < 1e-12)
ex._gap_ref["VOL"] = {"prior_close": 20000, "rvol_20d": 0.0}
check("rvol == 0 → static", abs(ex._buy_chase_pct("VOL") - STATIC) < 1e-12)
ex._gap_ref["VOL"] = {"prior_close": 20000, "rvol_20d": -0.03}
check("rvol < 0 → static", abs(ex._buy_chase_pct("VOL") - STATIC) < 1e-12)

# ---- 4. LIMIT PRICE: widened cap lifts the placed limit ---------------------
print("\n== 4. LIMIT PRICE — paper limit > static-cap limit on same high-rvol quote ==")
q = brk.get_quote("VOL")
ex._gap_ref["VOL"] = {"prior_close": 20000, "rvol_20d": 0.05}   # widened → ceil 0.04
px_paper = ex._limit_price(buy, q, cross=True)
# static-cap reference limit (flag off): ask 25000 well above both caps → both cap-bound
static_cap_px = 20000 * (1 + STATIC)
check("paper limit ~ ref*(1+ceil) = 20800", abs(px_paper - 20000 * (1 + CEIL)) <= 50)
check("paper limit strictly ABOVE static-cap price (20300)", px_paper > static_cap_px)

# ---- 5. NEG CONTROL: live(SpaceX) cfg → static on identical setup ------------
print("\n== 5. NEG CONTROL — live(SpaceX) effective cfg → static (flag off) ==")
brk_l = FakeBroker({"VOL": raw_quote("VOL", last=20000, ref=20000, floor=18600, ceil=21400,
                                     bid=20000, ask=25000)})
ex_l = Executor(make_plan([buy]), brk_l, dict(live_cfg))
ex_l._gap_ref["VOL"] = {"prior_close": 20000, "rvol_20d": 0.05}   # SAME high rvol
check("live ignores rvol → static cap", abs(ex_l._buy_chase_pct("VOL") - STATIC) < 1e-12)
px_live = ex_l._limit_price(buy, brk_l.get_quote("VOL"), cross=True)
check("live limit == static-cap price (20300), below paper", abs(px_live - static_cap_px) <= 50 and px_live < px_paper)

# ---- verdict ----------------------------------------------------------------
print("\n" + "=" * 60)
if FAILS:
    print(f"RESULT: FAIL — {len(FAILS)} check(s): {FAILS}")
    sys.exit(1)
print("RESULT: PASS — vol-scale buy chase-cap active on PAPER only, live/global untouched.")
