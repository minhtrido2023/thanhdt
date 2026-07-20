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
     - no DC name → 100% custom30V (empty-day = full parking = safety, not a defect);
     - build_orders: BUYS list DC before custom30V (deploy order).
  B. REGIME FLAT / reverse-unwind — leaving NEUTRAL flattens the sleeve, SELLS list parking
     before DC book, reverse_unwind flag True, sleeve returns to cash.
  C. FAIL-SAFE on missing data — DC signal None → hold prior (no rebalance); state unreadable
     → hold prior; custom30V basket missing → park held as CASH; price cache unreadable → no_data,
     no crash, no fabrication.
  D. NEGATIVE CONTROL — the flag defaults OFF; SpaceX / any live account resolves the flag to
     False; advance() on a disabled account is a pure no-op (writes no state); the two prior paper
     flags are untouched. The sleeve places no orders (touches no executor / plan-builder call).

  v2 (2026-07-20, job Taylor_20260720_091731) adds group E — the four agenda fixes:
     E1 CONTINUOUS-RESIDUAL: bal_lag_has_deal no longer flattens the sleeve (the v1 bug).
     E2 q2m5 cadence: no rebalance until the custom30V basket rebal_date changes; weights drift.
     E3 overlap cap 0.15: a name in BOTH DC book and custom30V never exceeds 0.15 combined,
        the trimmed excess goes to basket members with headroom (else cash).
     E4 liquidity floor 3B replaces the DHG hard-exclude; missing TV fails the floor; an
        unreadable TV map falls back to the OLD hard-exclude (never to a looser rule).

Run: python dc_book_waterfall_selfcheck.py   (exit 0 = all pass, non-zero = a check failed)
"""
import os
import sys
import tempfile

import dc_book_waterfall_paper as dcw
from dc_book_waterfall_paper import (compute_waterfall_targets, build_orders, turnover,
                                     dc_membership, apply_overlap_cap,
                                     CUSTOM30V, NEUTRAL, OVERLAP_CAP, LIQ_FLOOR_VND)

BIG = 9e9          # comfortably clears the 3B liquidity floor
LIQ_OK = lambda *tks: {t: BIG for t in tks}

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
    liq = None                              # None → dc_membership falls back to hard-exclude

    @classmethod
    def install(cls):
        dcw.sleeve_enabled = lambda account="main": True
        dcw.nav_basis = lambda account="main": 1_000_000_000.0
        dcw.load_trigger = lambda status_file=None: cls.trigger
        dcw.load_double_confirm = lambda: cls.dc_set
        dcw.load_custom30v_basket = lambda: cls.basket
        dcw.latest_closes = lambda tickers: cls.closes
        dcw.load_liquidity = lambda tickers: (
            cls.liq if cls.liq is None else {t: cls.liq.get(t, 0.0) for t in tickers})


def fresh_state_paths():
    d = tempfile.mkdtemp(prefix="dcw_selfcheck_")
    dcw.STATE_FILE = os.path.join(d, "state.json")
    dcw.NAV_CSV = os.path.join(d, "nav.csv")


# =======================================================================================
print("A. WIRING / priority order (pure core)")
DC5 = {"ACB": "ACCUMULATE", "MBB": "ACCUMULATE", "TCB": "ACCUMULATE",
       "FPT": "STRONG", "SSI": "ACCUMULATE"}
# A REALISTIC custom30V basket: 30 equal names @ 3.33% — like production, so the 0.15 combined
# cap never binds on the parking leg itself (a 2-name toy basket would be capped to shreds and
# would test a situation that cannot occur).
PARK = {f"P{i:02d}": 1.0 / 30 for i in range(30)}    # disjoint from DC5

# NOTE ON THE 0.15 CAP: the pinned eff_cap (dc_overlap_cap_backtest.py, job _042827) applies
# `min(w, X)` to EVERY name, not only overlapping ones. So the 0.20 DC-layer cap is effectively
# superseded by the 0.15 combined ceiling for every DC name. That is the spec as backtested —
# the tests below assert 0.15, deliberately.
tgt, dep, _, det = compute_waterfall_targets(NEUTRAL, DC5, PARK, LIQ_OK(*DC5))
ok("A1 ≥5 names → deployed", dep)
ok("A1 ≥5 names → each 0.15 (combined cap binds)", all(abs(tgt[t] - 0.15) < 1e-9 for t in DC5),
   f"got={[round(tgt[t],4) for t in DC5]}")
ok("A1 ≥5 names → pre-cap park leg ~0", det["park_leg"] < 1e-9, f"park={det['park_leg']}")
ok("A1 capped excess parked in the basket, total ≈ 1.0",
   abs(sum(tgt.values()) - 1.0) < 1e-9, f"sum={sum(tgt.values())}")

# thin 3-name set → 0.20 DC cap binds first (park leg 0.40), then the 0.15 combined cap
DC3 = {"ACB": "ACCUMULATE", "MBB": "ACCUMULATE", "TCB": "ACCUMULATE"}
tgt3, _, _, det3 = compute_waterfall_targets(NEUTRAL, DC3, PARK, LIQ_OK(*DC3))
ok("A2 thin(3) → DC names at the 0.15 ceiling", all(abs(tgt3[t] - 0.15) < 1e-9 for t in DC3))
ok("A2 thin(3) → pre-cap park leg 0.40", abs(det3["park_leg"] - 0.40) < 1e-9, f"park={det3['park_leg']}")
ok("A2 thin(3) → basket absorbs the rest (total ≈ 1.0)", abs(sum(tgt3.values()) - 1.0) < 1e-9)

# empty DC set → 100% custom30V (spread over the basket, no name near the cap)
tgte, depe, _, dete = compute_waterfall_targets(NEUTRAL, {}, PARK, {})
ok("A4 empty DC → 100% custom30V", abs(dete["park_leg"] - 1.0) < 1e-9 and depe
   and abs(sum(tgte.values()) - 1.0) < 1e-9, f"sum={sum(tgte.values())}")

# build_orders: BUYS list DC before custom30V (deploy order)
buys = build_orders({}, {"ACB": 0.2, "MBB": 0.2, CUSTOM30V: 0.6})
buy_tickers = [o["ticker"] for o in buys if o["side"] == "buy"]
ok("A5 deploy: DC bought before custom30V", buy_tickers and buy_tickers[-1] == CUSTOM30V and CUSTOM30V not in buy_tickers[:-1])

# =======================================================================================
print("B. REGIME FLAT / reverse-unwind")
tgt_ns, dep_ns, _, _ = compute_waterfall_targets(2, DC5, PARK, LIQ_OK(*DC5))  # BEAR
ok("B1 non-NEUTRAL → sleeve flat", tgt_ns == {} and not dep_ns)

# deployed → flat: sells list parking FIRST, then DC book
prev = {"ACB": 0.2, "MBB": 0.2, "VHM": 0.3, "VCB": 0.3}
unwind = build_orders(prev, {}, ["ACB", "MBB"])
sell_tickers = [o["ticker"] for o in unwind if o["side"] == "sell"]
ok("B2 unwind: all positions sold", set(sell_tickers) == set(prev))
ok("B2 unwind: parking sold FIRST", set(sell_tickers[:2]) == {"VHM", "VCB"}, f"order={sell_tickers}")
ok("B2 unwind: no buys", not any(o["side"] == "buy" for o in unwind))

# end-to-end reverse_unwind flag via advance() — regime leaves NEUTRAL
fresh_state_paths(); Inject.install()
Inject.dc_set = dict(DC5)
Inject.liq = LIQ_OK(*DC5)
Inject.basket = ({"VHM": 0.5, "VCB": 0.5}, "2026-05-05")
Inject.trigger = (NEUTRAL, "NEUTRAL", False)
Inject.closes = ({"ACB": 22600, "MBB": 24750, "TCB": 33400, "FPT": 70800, "SSI": 26400,
                  "VHM": 40000, "VCB": 60000}, "2026-07-06")
st1, s1 = dcw.advance("main")
ok("B3 day-1 advanced + deployed", st1 == "advanced" and s1["deployed"])
# day-2 regime drops to BEAR → sleeve flattens
Inject.trigger = (2, "BEAR", False)
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
Inject.dc_set = dict(DC5)
Inject.liq = LIQ_OK(*DC5)
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

# C2 DT5G state unreadable → hold prior
Inject.dc_set = dict(DC5)
Inject.trigger = (None, "?", None)
Inject.closes = ({"ACB": 22600, "MBB": 24750, "TCB": 33400, "FPT": 70800, "SSI": 26400,
                  "VHM": 40000}, "2026-07-08")
stc2, sc2 = dcw.advance("main")
ok("C2 state None → held prior weights", stc2 == "advanced"
   and set(sc2["weights"]) == set(sc["weights"]), f"weights={sorted(sc2['weights'])}")

# C3 custom30V basket missing but parking required → held as CASH
fresh_state_paths(); Inject.install()
Inject.trigger = (NEUTRAL, "NEUTRAL", False)
Inject.dc_set = dict(DC3)          # thin → 40% park
Inject.liq = LIQ_OK(*DC3)
Inject.basket = ({}, None)         # basket gone
Inject.closes = ({"ACB": 22600, "MBB": 24750, "TCB": 33400}, "2026-07-06")
stc3, sc3 = dcw.advance("main")
ok("C3 basket missing → only DC names held", set(sc3["weights"]) == set(DC3))
# 3 DC names capped at 0.15 = 0.45 deployed; no basket to absorb the rest → 0.55 cash
ok("C3 basket missing → remainder held as CASH",
   abs(sc3["history"][-1]["cash_weight"] - 0.55) < 1e-9,
   f"cash={sc3['history'][-1]['cash_weight']}")

# C4 price cache unreadable → no_data, no crash
fresh_state_paths(); Inject.install()
Inject.closes = ({}, None)
stc4, sc4 = dcw.advance("main")
ok("C4 no prices → no_data no-op", stc4 == "no_data")

# C5 idempotent per close (same data_date → unchanged)
fresh_state_paths(); Inject.install()
Inject.trigger = (NEUTRAL, "NEUTRAL", False)
Inject.dc_set = dict(DC5)
Inject.liq = LIQ_OK(*DC5)
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
# 5 DC names @0.15 (combined cap) = 75% active, all +10%; VHM is the only basket name so it
# absorbs 0.15 of the capped excess and is flat → gross = 0.75 × 10% = 7.5%
ok("C6 MTM: gross ≈ +7.5%", abs(last["gross_ret_pct"] - 7.5) < 0.1, f"gross={last['gross_ret_pct']}")
ok("C6 MTM: NAV grew ~7.5%", abs(s6["nav_vnd"] / 1e9 - 1.075) < 0.01, f"nav={s6['nav_vnd']}")

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
# The DCF echo (added 2026-07-15) reads trading_bot.strategies for an INFORMATIONAL cache lookup.
# What must stay true is that the sleeve never places/plans an order — assert on the write-side
# entry points, not on the import (the old blanket import assertion went stale on 07-15).
ok("D4 places/plans no order",
   not any(k in src for k in ("place_order", "load_plan", "bot_execute", "build_plan", "submit_order")))

# =======================================================================================
print("E. v2 AGENDA FIXES (job Taylor_20260720_091731)")
importlib.reload(dcw)
from dc_book_waterfall_paper import (compute_waterfall_targets, build_orders,
                                     dc_membership, apply_overlap_cap)

# ---- E1 CONTINUOUS-RESIDUAL: a BAL/LAG deal must NOT flatten the sleeve (the v1 bug) ----
src_v2 = open(os.path.join(dcw.WORKDIR, "dc_book_waterfall_paper.py"), encoding="utf-8").read()
ok("E1 core takes no bal_lag_has_deal argument",
   "def compute_waterfall_targets(state, dc_set, basket" in src_v2)
fresh_state_paths(); Inject.install()
Inject.trigger = (NEUTRAL, "NEUTRAL", False)
Inject.dc_set = dict(DC5); Inject.liq = LIQ_OK(*DC5)
Inject.basket = ({"VHM": 0.5, "VCB": 0.5}, "2026-05-05")
Inject.closes = ({"ACB": 22600, "MBB": 24750, "TCB": 33400, "FPT": 70800, "SSI": 26400,
                  "VHM": 40000, "VCB": 60000}, "2026-07-06")
_, e1a = dcw.advance("main")
w_before = dict(e1a["weights"])
Inject.trigger = (NEUTRAL, "NEUTRAL", True)          # BAL/LAG deal appears — v1 would go flat
Inject.closes = ({t: p for t, p in Inject.closes[0].items()}, "2026-07-07")
_, e1b = dcw.advance("main")
ok("E1 BAL/LAG deal does NOT flatten sleeve", e1b["deployed"] and sum(e1b["weights"].values()) > 0.9,
   f"deployed={e1b['deployed']} sum={sum(e1b['weights'].values())}")
ok("E1 BAL/LAG deal causes NO turnover", abs(e1b["history"][-1]["turnover"]) < 1e-9,
   f"turnover={e1b['history'][-1]['turnover']}")
ok("E1 no reverse-unwind on a BAL/LAG deal", not e1b["reverse_unwind_last"])
ok("E1 weights unchanged (flat prices)",
   all(abs(e1b["weights"].get(t, 0) - w) < 1e-9 for t, w in w_before.items()))

# ---- E2 q2m5 cadence: no rebalance until the basket rebal_date changes ----
Inject.dc_set = {"ACB": "ACCUMULATE", "MBB": "ACCUMULATE"}   # membership CHANGES mid-quarter
Inject.liq = LIQ_OK("ACB", "MBB")
Inject.closes = ({"ACB": 22600, "MBB": 24750, "TCB": 33400, "FPT": 70800, "SSI": 26400,
                  "VHM": 40000, "VCB": 60000}, "2026-07-08")
_, e2a = dcw.advance("main")
ok("E2 membership change mid-quarter → NO rebalance", not e2a["history"][-1]["rebalanced"]
   and set(e2a["weights"]) == set(w_before), f"weights={sorted(e2a['weights'])}")
ok("E2 no rebal → zero turnover/TC", abs(e2a["history"][-1]["turnover"]) < 1e-9)
Inject.basket = ({"VHM": 0.5, "VCB": 0.5}, "2026-08-05")      # new q2m5 rebal_date
Inject.closes = ({"ACB": 22600, "MBB": 24750, "TCB": 33400, "FPT": 70800, "SSI": 26400,
                  "VHM": 40000, "VCB": 60000}, "2026-07-09")
_, e2b = dcw.advance("main")
ok("E2 new basket rebal_date → REBALANCE fires", e2b["history"][-1]["rebalanced"])
ok("E2 rebalance adopts the new DC membership",
   set(e2b["history"][-1]["dc_names"]) == {"ACB", "MBB"}, f"dc={e2b['history'][-1]['dc_names']}")
ok("E2 state records the rebal_date it built on", e2b["rebal_date"] == "2026-08-05")

# ---- E2b weights DRIFT (not snapped) between rebalances ----
fresh_state_paths(); Inject.install()
Inject.trigger = (NEUTRAL, "NEUTRAL", False)
Inject.dc_set = {"ACB": "ACCUMULATE", "MBB": "ACCUMULATE"}; Inject.liq = LIQ_OK("ACB", "MBB")
Inject.basket = ({}, "2026-05-05")     # no basket → DC leg 0.40, rest cash; keeps the maths clean
Inject.closes = ({"ACB": 10000, "MBB": 10000}, "2026-07-06")
_, d0 = dcw.advance("main")
Inject.closes = ({"ACB": 12000, "MBB": 10000}, "2026-07-07")   # ACB +20%, MBB flat
_, d1 = dcw.advance("main")
# 2 names @ min(0.20, 0.5) = 0.20 → 0.15 combined cap → 0.15 each, 0.70 cash.
# gross = 0.15*20% + 0.15*0 = 3%; ACB weight drifts to 0.15*1.2/1.03
ok("E2b drift: gross = +3%", abs(d1["history"][-1]["gross_ret_pct"] - 3.0) < 1e-6,
   f"gross={d1['history'][-1]['gross_ret_pct']}")
ok("E2b drift: ACB weight grew", abs(d1["weights"]["ACB"] - 0.15 * 1.2 / 1.03) < 1e-9,
   f"ACB={d1['weights']['ACB']}")
ok("E2b drift: no turnover charged", abs(d1["history"][-1]["turnover"]) < 1e-9)

# ---- E3 overlap cap 0.15 combined ----
# ACB is in BOTH the DC book (0.20) and the basket → uncapped it would be 0.20 + park·w
DC4 = {"ACB": "A", "MBB": "A", "TCB": "A", "FPT": "A"}          # 4 names @0.20 = 0.80 DC leg
BK = {"ACB": 0.5, "VHM": 0.5}                                   # park 0.20 → ACB +0.10 = 0.30
tgtc, _, _, detc = compute_waterfall_targets(NEUTRAL, DC4, BK, LIQ_OK(*DC4))
ok("E3 combined weight capped at 0.15", all(w <= OVERLAP_CAP + 1e-9 for w in tgtc.values()),
   f"max={max(tgtc.values()):.4f}")
ok("E3 overlap name detected", detc["overlap_names"] == ["ACB"])
ok("E3 excess redistributed to basket members with headroom",
   tgtc["VHM"] > 0.10 + 1e-9, f"VHM={tgtc.get('VHM')}")
ok("E3 total ≤ 1.0", sum(tgtc.values()) <= 1.0 + 1e-9)
# pure-core cap: everything over cap trimmed, headroom-less case → cash residual
capped, resid = apply_overlap_cap({"A": 0.40, "B": 0.30}, set(), OVERLAP_CAP)
ok("E3 no headroom → excess becomes cash residual",
   abs(capped["A"] - 0.15) < 1e-9 and abs(capped["B"] - 0.15) < 1e-9
   and abs(resid - 0.40) < 1e-9, f"resid={resid}")
# NEGATIVE CONTROL: no overlap → no name is FLAGGED as shared and nothing spills to cash.
# NOTE (corrected 2026-07-20, job Taylor_20260720_091731): the 0.15 cap is a BLANKET combined
# per-name cap, not an overlap-only rule — the pinned backtest `dc_overlap_cap_backtest.eff_cap`
# does `row = np.minimum(row, X)` across the WHOLE row, on top of the separate CAP_DC=0.20 DC-leg
# cap. So a DC name with no basket overlap is still trimmed 0.20 → 0.15, with the excess
# redistributed to basket members. An earlier version of this test asserted DC names keep 0.20;
# that encoded an assumption the pinned formula never implemented. Test fixed, code left alone.
tgtn, _, _, detn = compute_waterfall_targets(NEUTRAL, DC3, PARK, LIQ_OK(*DC3))
ok("E3 NEG-control: no overlap → no shared name flagged, no cash residual",
   detn["overlap_names"] == [] and detn["cap_residual"] == 0.0
   and abs(sum(tgtn.values()) - 1.0) < 1e-9,
   f"overlap={detn['overlap_names']} resid={detn['cap_residual']}")
ok("E3 blanket cap: even a non-overlapping DC name is trimmed 0.20 → 0.15 (pinned eff_cap)",
   all(abs(tgtn[t] - OVERLAP_CAP) < 1e-9 for t in DC3),
   f"{ {t: round(tgtn[t], 6) for t in DC3} }")

# ---- E4 liquidity floor 3B replaces the DHG hard-exclude ----
DCL = {"ACB": "A", "DHG": "A", "MBB": "A"}
liq_thin = {"ACB": BIG, "DHG": 1.2e9, "MBB": BIG}          # DHG below the 3B floor
mem, floor_on, dropped = dc_membership(DCL, liq_thin)
ok("E4 floor drops a sub-3B name", set(mem) == {"ACB", "MBB"} and dropped == ["DHG"] and floor_on)
mem2, _, dropped2 = dc_membership(DCL, {"ACB": BIG, "MBB": BIG})   # DHG's TV missing entirely
ok("E4 missing TV fails the floor (fail-safe)", set(mem2) == {"ACB", "MBB"} and dropped2 == ["DHG"])
mem3, floor_on3, _ = dc_membership(DCL, {"ACB": BIG, "DHG": 5e9, "MBB": BIG})
ok("E4 a LIQUID DHG is now admitted (floor is by merit, not by name)",
   set(mem3) == {"ACB", "DHG", "MBB"} and floor_on3)
mem4, floor_on4, _ = dc_membership(DCL, None)                      # TV map unreadable
ok("E4 unreadable liq map → falls back to the OLD hard-exclude (never looser)",
   set(mem4) == {"ACB", "MBB"} and not floor_on4)
ok("E4 floor threshold is 3B", abs(LIQ_FLOOR_VND - 3_000_000_000.0) < 1e-6)

# ---- E5 v1 history archived, v2 restarts from the 1B basis ----
v1_csv = os.path.join(dcw.DATA_DIR, "dc_book_waterfall_paper_nav_v1.csv")
ok("E5 v1 NAV series archived", os.path.exists(v1_csv))
ok("E5 v2 state carries a version tag", dcw.SLEEVE_VERSION == "v2")

# =======================================================================================
print(f"\n{'='*60}\nRESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("FAILED:", ", ".join(FAIL))
    sys.exit(1)
print("ALL PASS ✓")
sys.exit(0)
