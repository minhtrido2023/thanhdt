#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Behaviour + regression self-check for the DC-book NEUTRAL idle-cash WATERFALL paper sleeve.

Same discipline as extreme_regime_selfcheck.py / the vol-scale chase-cap check: no network, no
BQ — the module's fail-safe I/O wrappers are monkeypatched with synthetic data, STATE_FILE/NAV_CSV
are redirected to a tmp path, and the pure core is exercised directly. Asserts the four things the
dispatch (job Taylor_20260706_132553) requires:

  A. WIRING / priority order — waterfall fills BAL/LAG → DC book → custom30V:
     - ≥5 DC names → book fully active (custom30V ≈ 0);
     - thin set (3 names) → 0.20 cap binds → 60% active / 40% custom30V;
     - DHG hard-excluded from the active book;
     - no DC name → 100% custom30V (empty-day = full parking = safety, not a defect);
     - build_orders: BUYS list DC before custom30V (deploy order).
  B. REVERSE-UNWIND fires when BAL/LAG get a deal back — deployed→flat produces SELLS with
     custom30V before DC book, reverse_unwind flag True, sleeve returns to cash.
  C. FAIL-SAFE on missing data — DC signal None → hold prior (no rebalance); trigger unreadable
     → hold prior; custom30V basket missing → park held as CASH; price cache unreadable → no_data,
     no crash, no fabrication.
  D. NEGATIVE CONTROL — the flag defaults OFF; SpaceX / any live account resolves the flag to
     False; advance() on a disabled account is a pure no-op (writes no state); the two prior paper
     flags are untouched. The sleeve is self-contained (touches no executor / plan-builder file).

Run: python dc_book_waterfall_selfcheck.py   (exit 0 = all pass, non-zero = a check failed)
"""
import os
import sys
import tempfile

import dc_book_waterfall_paper as dcw
from dc_book_waterfall_paper import (compute_waterfall_targets, build_orders, turnover,
                                     CUSTOM30V, NEUTRAL)

PASS, FAIL = [], []


def ok(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f" — {detail}" if detail and not cond else ""))


# ----- injectable fake I/O so advance() runs fully offline -----------------------------
class Inject:
    trigger = (NEUTRAL, "NEUTRAL", False)   # (state, name, bal_lag_has_deal)
    dc_set = {}
    basket = ({}, None)
    closes = ({}, None)

    @classmethod
    def install(cls):
        dcw.sleeve_enabled = lambda account="main": True
        dcw.nav_basis = lambda account="main": 1_000_000_000.0
        dcw.load_trigger = lambda status_file=None: cls.trigger
        dcw.load_double_confirm = lambda: cls.dc_set
        dcw.load_custom30v_basket = lambda: cls.basket
        dcw.latest_closes = lambda tickers: cls.closes


def fresh_state_paths():
    d = tempfile.mkdtemp(prefix="dcw_selfcheck_")
    dcw.STATE_FILE = os.path.join(d, "state.json")
    dcw.NAV_CSV = os.path.join(d, "nav.csv")


# =======================================================================================
print("A. WIRING / priority order (pure core)")
# ≥5 names, NEUTRAL, BAL/LAG dry → fully active
tgt, dep, _ = compute_waterfall_targets(NEUTRAL, False,
    {"ACB": "ACCUMULATE", "MBB": "ACCUMULATE", "TCB": "ACCUMULATE", "FPT": "STRONG", "SSI": "ACCUMULATE"})
ok("A1 ≥5 names → deployed", dep)
ok("A1 ≥5 names → each 0.20", all(abs(tgt[t] - 0.20) < 1e-9 for t in tgt if t != CUSTOM30V))
ok("A1 ≥5 names → custom30V ~0", tgt.get(CUSTOM30V, 0.0) < 1e-9, f"c30v={tgt.get(CUSTOM30V)}")
ok("A1 weights sum ≈ 1.0", abs(sum(tgt.values()) - 1.0) < 1e-9, f"sum={sum(tgt.values())}")

# thin 3-name set → 0.20 cap binds → 60% active / 40% custom30V
tgt3, _, _ = compute_waterfall_targets(NEUTRAL, False,
    {"ACB": "ACCUMULATE", "MBB": "ACCUMULATE", "TCB": "ACCUMULATE"})
ok("A2 thin(3) → 0.20 each", all(abs(tgt3[t] - 0.20) < 1e-9 for t in tgt3 if t != CUSTOM30V))
ok("A2 thin(3) → custom30V 0.40", abs(tgt3.get(CUSTOM30V, 0) - 0.40) < 1e-9, f"c30v={tgt3.get(CUSTOM30V)}")

# DHG excluded from the active book
tgtd, _, _ = compute_waterfall_targets(NEUTRAL, False,
    {"ACB": "ACCUMULATE", "DHG": "ACCUMULATE", "MBB": "ACCUMULATE"})
ok("A3 DHG excluded from active book", "DHG" not in tgtd)
ok("A3 DHG excluded → 2 active names", sum(1 for t in tgtd if t != CUSTOM30V) == 2)

# empty DC set → 100% custom30V
tgte, depe, _ = compute_waterfall_targets(NEUTRAL, False, {})
ok("A4 empty DC → 100% custom30V", abs(tgte.get(CUSTOM30V, 0) - 1.0) < 1e-9 and depe)

# build_orders: BUYS list DC before custom30V (deploy order)
buys = build_orders({}, {"ACB": 0.2, "MBB": 0.2, CUSTOM30V: 0.6})
buy_tickers = [o["ticker"] for o in buys if o["side"] == "buy"]
ok("A5 deploy: DC bought before custom30V", buy_tickers and buy_tickers[-1] == CUSTOM30V and CUSTOM30V not in buy_tickers[:-1])

# =======================================================================================
print("B. REVERSE-UNWIND (BAL/LAG get a deal back)")
# not-NEUTRAL and bal_lag=True must both yield flat sleeve
tgt_flat, dep_flat, _ = compute_waterfall_targets(NEUTRAL, True, {"ACB": "ACCUMULATE"})
ok("B1 BAL/LAG has deal → sleeve flat", tgt_flat == {} and not dep_flat)
tgt_ns, dep_ns, _ = compute_waterfall_targets(2, False, {"ACB": "ACCUMULATE"})  # BEAR
ok("B1 non-NEUTRAL → sleeve flat", tgt_ns == {} and not dep_ns)

# deployed → flat: sells list custom30V FIRST, then DC book
prev = {"ACB": 0.2, "MBB": 0.2, CUSTOM30V: 0.6}
unwind = build_orders(prev, {})
sell_tickers = [o["ticker"] for o in unwind if o["side"] == "sell"]
ok("B2 unwind: all positions sold", set(sell_tickers) == {"ACB", "MBB", CUSTOM30V})
ok("B2 unwind: custom30V sold FIRST", sell_tickers[0] == CUSTOM30V, f"order={sell_tickers}")
ok("B2 unwind: no buys", not any(o["side"] == "buy" for o in unwind))

# end-to-end reverse_unwind flag via advance()
fresh_state_paths(); Inject.install()
Inject.dc_set = {"ACB": "ACCUMULATE", "MBB": "ACCUMULATE", "TCB": "ACCUMULATE",
                 "FPT": "STRONG", "SSI": "ACCUMULATE"}
Inject.basket = ({"VHM": 0.5, "VCB": 0.5}, "2026-05-05")
Inject.trigger = (NEUTRAL, "NEUTRAL", False)
Inject.closes = ({"ACB": 22600, "MBB": 24750, "TCB": 33400, "FPT": 70800, "SSI": 26400,
                  "VHM": 40000, "VCB": 60000}, "2026-07-06")
st1, s1 = dcw.advance("main")
ok("B3 day-1 advanced + deployed", st1 == "advanced" and s1["deployed"])
# day-2 BAL/LAG deal returns → unwind
Inject.trigger = (NEUTRAL, "NEUTRAL", True)
Inject.closes = ({"ACB": 23000, "MBB": 25000, "TCB": 34000, "FPT": 72000, "SSI": 27000,
                  "VHM": 41000, "VCB": 61000}, "2026-07-07")
st2, s2 = dcw.advance("main")
ok("B3 day-2 reverse-unwind fired", st2 == "advanced" and s2["reverse_unwind_last"] and not s2["deployed"])
ok("B3 day-2 sleeve back to cash", abs(sum(s2["weights"].values())) < 1e-9)

# =======================================================================================
print("C. FAIL-SAFE on missing data")
# C1 DC signal None → hold prior allocation (deployed still True, no rebalance)
fresh_state_paths(); Inject.install()
Inject.trigger = (NEUTRAL, "NEUTRAL", False)
Inject.dc_set = {"ACB": "ACCUMULATE", "MBB": "ACCUMULATE", "TCB": "ACCUMULATE",
                 "FPT": "STRONG", "SSI": "ACCUMULATE"}
Inject.basket = ({"VHM": 1.0}, "2026-05-05")
Inject.closes = ({"ACB": 22600, "MBB": 24750, "TCB": 33400, "FPT": 70800, "SSI": 26400,
                  "VHM": 40000}, "2026-07-06")
dcw.advance("main")
Inject.dc_set = None  # signal vanishes
Inject.closes = ({"ACB": 22600, "MBB": 24750, "TCB": 33400, "FPT": 70800, "SSI": 26400,
                  "VHM": 40000}, "2026-07-07")
stc, sc = dcw.advance("main")
ok("C1 DC None → held (no rebalance)", stc == "advanced" and sc["history"][-1]["fail_safe"]
   and sc["deployed"])

# C2 trigger unreadable (state None) → hold prior
Inject.dc_set = {"ACB": "ACCUMULATE", "MBB": "ACCUMULATE", "TCB": "ACCUMULATE",
                 "FPT": "STRONG", "SSI": "ACCUMULATE"}
Inject.trigger = (None, "?", None)
Inject.closes = ({"ACB": 22600, "MBB": 24750, "TCB": 33400, "FPT": 70800, "SSI": 26400,
                  "VHM": 40000}, "2026-07-08")
stc2, sc2 = dcw.advance("main")
ok("C2 trigger None → held prior weights", stc2 == "advanced"
   and set(sc2["weights"]) == {"ACB", "MBB", "TCB", "FPT", "SSI"})

# C3 custom30V basket missing but parking required → held as CASH
fresh_state_paths(); Inject.install()
Inject.trigger = (NEUTRAL, "NEUTRAL", False)
Inject.dc_set = {"ACB": "ACCUMULATE", "MBB": "ACCUMULATE", "TCB": "ACCUMULATE"}  # thin → 40% park
Inject.basket = ({}, None)                                                       # basket gone
Inject.closes = ({"ACB": 22600, "MBB": 24750, "TCB": 33400}, "2026-07-06")
stc3, sc3 = dcw.advance("main")
ok("C3 basket missing → custom30V not held", CUSTOM30V not in sc3["weights"])
ok("C3 basket missing → 40% held as CASH", abs(sc3["history"][-1]["cash_weight"] - 0.40) < 1e-9,
   f"cash={sc3['history'][-1]['cash_weight']}")

# C4 price cache unreadable → no_data, no crash
fresh_state_paths(); Inject.install()
Inject.closes = ({}, None)
stc4, sc4 = dcw.advance("main")
ok("C4 no prices → no_data no-op", stc4 == "no_data")

# C5 idempotent per close (same data_date → unchanged)
fresh_state_paths(); Inject.install()
Inject.trigger = (NEUTRAL, "NEUTRAL", False)
Inject.dc_set = {"ACB": "ACCUMULATE", "MBB": "ACCUMULATE", "TCB": "ACCUMULATE",
                 "FPT": "STRONG", "SSI": "ACCUMULATE"}
Inject.basket = ({"VHM": 1.0}, "2026-05-05")
Inject.closes = ({"ACB": 22600, "MBB": 24750, "TCB": 33400, "FPT": 70800, "SSI": 26400,
                  "VHM": 40000}, "2026-07-06")
dcw.advance("main")
st5, s5 = dcw.advance("main")
ok("C5 same close → unchanged (idempotent)", st5 == "unchanged" and len(s5["history"]) == 1)

# C6 MTM correctness — day-2 +10% on all DC names, held weights earn it (minus TC≈0)
Inject.closes = ({"ACB": 24860, "MBB": 27225, "TCB": 36740, "FPT": 77880, "SSI": 29040,
                  "VHM": 40000}, "2026-07-07")  # DC +10%, VHM flat
st6, s6 = dcw.advance("main")
last = s6["history"][-1]
# 5 DC names @0.20 = 100% active, all +10% → gross ≈ +10%
ok("C6 MTM: gross ≈ +10%", abs(last["gross_ret_pct"] - 10.0) < 0.1, f"gross={last['gross_ret_pct']}")
ok("C6 MTM: NAV grew ~10%", abs(s6["nav_vnd"] / 1e9 - 1.10) < 0.01, f"nav={s6['nav_vnd']}")

# =======================================================================================
print("D. NEGATIVE CONTROL (production untouched)")
# reload the real config module (Inject monkeypatched dcw.sleeve_enabled at module scope;
# the real gating lives in trading_bot.config, unpatched)
from trading_bot.config import DEFAULTS, load_config, load_accounts, pick_accounts
ok("D1 DEFAULTS flag present & False", DEFAULTS.get("dc_book_waterfall_enabled") is False)
ok("D1 prior paper flags untouched (default False)",
   DEFAULTS.get("extreme_regime_enabled") is False
   and DEFAULTS.get("chase_cap_vol_scale_enabled") is False)

profiles = {p["label"]: p for p in load_accounts(load_config())}
ok("D2 main resolves flag ON", profiles["main"]["cfg"].get("dc_book_waterfall_enabled") is True)
for lbl in ("SpaceX", "ZaloPay"):
    if lbl in profiles:
        ok(f"D2 {lbl} (live) resolves flag OFF",
           profiles[lbl]["cfg"].get("dc_book_waterfall_enabled") in (False, None))

# D3 advance() on a disabled account is a pure no-op (restore the REAL sleeve_enabled first)
import importlib
importlib.reload(dcw)   # drop the Inject monkeypatch; use real gating
fresh_state_paths()
st_dis, s_dis = dcw.advance("SpaceX")
ok("D3 advance(SpaceX) → disabled no-op", st_dis == "disabled" and s_dis is None)
ok("D3 disabled → no state file written", not os.path.exists(dcw.STATE_FILE))

# D4 self-contained — the sleeve module imports NO production executor/plan-builder path
src = open(os.path.join(dcw.WORKDIR, "dc_book_waterfall_paper.py"), encoding="utf-8").read()
ok("D4 does not import executor", "from trading_bot.executor" not in src and "import executor" not in src)
ok("D4 does not import strategies/plan-builder", "trading_bot.strategies" not in src)

# =======================================================================================
print(f"\n{'='*60}\nRESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("FAILED:", ", ".join(FAIL))
    sys.exit(1)
print("ALL PASS ✓")
sys.exit(0)
