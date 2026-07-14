# -*- coding: utf-8 -*-
"""a4_dy_selfcheck.py — does the A4 DY tie-break do EXACTLY what was pre-registered, and nothing else?

Job Taylor_20260714_152605. Research-only.

Arm A4 (pre-registered §12.4): on the A2 (`eyonly`) base, DY may TIE-BREAK inside the marginal band
(ey ranks 20-45) and nowhere else. Three properties have to hold, and none of them is self-evident
from reading the code:
  P1 BAND-ONLY   — ranks outside the band are bit-identical to A2.
  P2 FAIL-OPEN   — a name without a positive DY does not move at all (~30% of obs have no DY>0).
                   Sorting the band by DY would sink those names: that PENALISES absent data and is
                   a different, unmeasured rule.
  P3 ORDERING    — inside the band, DY-bearing names sit in DY-descending order, in the slots they
                   already occupied.
Plus a NEGATIVE CONTROL (P4): the mechanism must actually change something. A rule that silently
no-ops would pass P1-P3 vacuously — the same trap §12.6 caught on the `eyfin` PCF check.

The DY as-of used here is re-derived from BQ independently of custom_basket's own `dy_at` closure:
checking the module with the module's own helper would make the check vacuous (same reasoning as
v4final_lib's re-implementation of _cap_group_jointly).

Run: $DNA_PYEXE mike/agents/Taylor/v4final_exp/a4_dy_selfcheck.py
"""
import bisect
import os
import sys

import numpy as np
import pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)
from simulate_holistic_nav import bq  # noqa: E402
import custom_basket as cb  # noqa: E402

START, END = "2014-01-02", "2026-06-19"
PIT = dict(quality="none", rebal="q2m5", gate_rating=3, top_n=30, name_cap=0.10, qtilt=None)
LO, HI = 20, 45
PASS, FAIL = [], []


def chk(ok, name, detail=""):
    (PASS if ok else FAIL).append(name)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


# ================================================================= PART 1 — unit: reorder semantics
# Independent re-implementation of the pre-registered rule. If this and custom_basket's `_dy_reorder`
# ever disagree on the integration panel below, one of them is wrong — that is the point of writing
# it twice.
def reorder_ref(names, dy, lo, hi):
    band = names[lo - 1:hi]
    if len(band) < 2:
        return list(names)
    slots = [i for i, t in enumerate(band) if dy.get(t) is not None]
    if len(slots) < 2:
        return list(names)
    ranked = sorted((band[i] for i in slots), key=lambda t: dy[t], reverse=True)
    out = list(band)
    for s, it in zip(slots, ranked):
        out[s] = it
    return names[:lo - 1] + out + names[hi:]


print("=" * 78)
print("PART 1 — unit tests of the tie-break semantics (synthetic, no BQ)")
print("=" * 78)

# U1 fail-open: B and D have no DY -> they must not move; A,C,E permute among slots 0,2,4.
n = list("ABCDE")
dy = {"A": 0.01, "B": None, "C": 0.05, "D": None, "E": 0.03}
r = reorder_ref(n, dy, 1, 5)
chk(r == ["C", "B", "E", "D", "A"], "U1 fail-open: no-DY names keep their exact slot", f"{r}")
chk(r[1] == "B" and r[3] == "D", "U1b no-DY names not sunk to the back", f"{r}")

# U2 band-only
n = list("ABCDEFGH")
dy = {t: 1.0 - i * 0.1 for i, t in enumerate(n)}   # already DY-desc -> a full sort is identity...
dy["C"], dy["E"] = 0.1, 0.9                        # ...except inside the band, where it is not
r = reorder_ref(n, dy, 3, 5)
chk(r[:2] == ["A", "B"] and r[5:] == ["F", "G", "H"], "U2 band-only: outside band untouched", f"{r}")
chk(r[2:5] == ["E", "D", "C"], "U2b in-band sorted DY-desc", f"{r[2:5]}")

# U3 all-missing -> exact no-op
n = list("ABCDE")
r = reorder_ref(n, {t: None for t in n}, 1, 5)
chk(r == n, "U3 all DY absent -> exact no-op")

# U4 single DY-bearing name -> no-op (nothing to break a tie against)
r = reorder_ref(n, {"A": 0.05, "B": None, "C": None, "D": None, "E": None}, 1, 5)
chk(r == n, "U4 one DY name -> no-op")

# U5 permutation invariant: never invents/drops a name
n = list("ABCDEFGH")
dy = {"A": .1, "B": None, "C": .9, "D": .2, "E": None, "F": .5, "G": .3, "H": None}
r = reorder_ref(n, dy, 2, 7)
chk(sorted(r) == sorted(n) and len(r) == len(n), "U5 permutation invariant (no name invented/lost)")

# U6 NEGATIVE CONTROL: the rule is not inert
chk(r != n, "U6 negative control: mechanism DOES reorder when DY is informative", f"{r}")

# ============================================================= PART 2 — integration vs the A2 base
print()
print("=" * 78)
print("PART 2 — integration: A4 vs A2 on the real 2014-2026 panel")
print("=" * 78)


def build(select, dy_band=None):
    saved = {k: os.environ.get(k) for k in ("BASKET_SELECT", "BASKET_DY_TIEBREAK")}
    os.environ["BASKET_SELECT"] = select
    if dy_band:
        os.environ["BASKET_DY_TIEBREAK"] = dy_band
    else:
        os.environ.pop("BASKET_DY_TIEBREAK", None)
    try:
        return cb.build_pit(bq, START, END, weight_scheme="namecap", **PIT)
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


print("\n--- building A2 (eyonly, DY OFF) ---")
_, _, mem_a2, _ = build("eyonly")
print("\n--- building A4 (eyonly + DY tie-break 20:45) ---")
_, _, mem_a4, bx4 = build("eyonly", f"{LO}:{HI}")

# ---- independent DY as-of (mirrors dy_floor_test.py; NOT custom_basket's closure) ----
_dv = bq(f"""SELECT f.ticker, f.time, f.Release_Date, f.Dividend_Min3Y
FROM tav2_bq.ticker_financial f WHERE f.time <= DATE '{END}' AND f.Dividend_Min3Y IS NOT NULL""")
_dv["eff"] = (pd.to_datetime(_dv["Release_Date"])
              .fillna(pd.to_datetime(_dv["time"]) + pd.Timedelta(days=45)))
_dv = _dv.sort_values("eff")
_hist = {tk: (list(g["eff"]), list(g["Dividend_Min3Y"])) for tk, g in _dv.groupby("ticker")}
reb = sorted(pd.to_datetime(mem_a4["rebal_date"]).unique())
_in = ",".join(f"DATE '{pd.Timestamp(x).date()}'" for x in reb)
_px = bq(f"SELECT t.ticker, t.time, t.Price FROM tav2_bq.ticker t "
         f"WHERE t.time IN ({_in}) AND t.Price IS NOT NULL")
_px["time"] = pd.to_datetime(_px["time"])
_pxm = {(r.ticker, r.time): float(r.Price) for r in _px.itertuples()}


def dy_ref(tk, d):
    e, px = _hist.get(tk), _pxm.get((tk, pd.Timestamp(d)))
    if not e or not px or px <= 0:
        return None
    i = bisect.bisect_right(e[0], pd.Timestamp(d)) - 1
    if i < 0:
        return None
    v = float(e[1][i])
    return v / px if v > 0 else None


a2 = {pd.Timestamp(d): list(g.sort_values("liq_rank")["ticker"])
      for d, g in mem_a2.groupby(pd.to_datetime(mem_a2["rebal_date"]))}
a4 = {pd.Timestamp(d): list(g.sort_values("liq_rank")["ticker"])
      for d, g in mem_a4.groupby(pd.to_datetime(mem_a4["rebal_date"]))}
chk(set(a2) == set(a4), "I0 same rebal dates", f"{len(a2)} rebals")

# P1 BAND-ONLY: ranks 1..LO-1 must be identical name-for-name, every rebal.
bad = [d for d in a2 if a2[d][:LO - 1] != a4[d][:LO - 1]]
chk(not bad, f"P1 band-only: ranks 1-{LO - 1} identical to A2 on all {len(a2)} rebals",
    f"violations: {[str(x.date()) for x in bad[:3]]}")

# P2 FAIL-OPEN: inside the visible band (ranks LO..30), any name WITHOUT DY>0 must sit at the exact
# same rank in A4 as in A2 — the rule may not move it, in either direction.
viol, n_nodv = [], 0
for d in a2:
    for i in range(LO - 1, min(30, len(a2[d]))):
        t2 = a2[d][i]
        if dy_ref(t2, d) is None:
            n_nodv += 1
            if i >= len(a4[d]) or a4[d][i] != t2:
                viol.append((str(d.date()), i + 1, t2, a4[d][i] if i < len(a4[d]) else None))
chk(not viol, f"P2 fail-open: all {n_nodv} no-DY names in ranks {LO}-30 kept their exact rank",
    f"violations: {viol[:3]}")

# P3 ORDERING: the DY-bearing names in the visible band must be DY-descending in A4.
bad3 = []
for d in a4:
    v = [dy_ref(t, d) for t in a4[d][LO - 1:30]]
    v = [x for x in v if x is not None]
    if any(v[i] < v[i + 1] - 1e-12 for i in range(len(v) - 1)):
        bad3.append(str(d.date()))
chk(not bad3, f"P3 ordering: DY-bearing names in ranks {LO}-30 are DY-descending",
    f"violations: {bad3[:3]}")

# P3b the DY-bearing names must occupy the SAME SLOTS as in A2 (a permutation, not a re-cut).
bad3b = []
for d in a2:
    s2 = [i for i in range(LO - 1, min(30, len(a2[d]))) if dy_ref(a2[d][i], d) is not None]
    s4 = [i for i in range(LO - 1, min(30, len(a4[d]))) if dy_ref(a4[d][i], d) is not None]
    if s2 != s4:
        bad3b.append(str(d.date()))
chk(not bad3b, "P3b DY-bearing names occupy the same slots as A2 (permutation, not re-cut)",
    f"violations: {bad3b[:3]}")

# P4 NEGATIVE CONTROL: A4 must differ from A2 somewhere, or the whole arm is measuring nothing.
chg = [d for d in a2 if a2[d] != a4[d]]
chg_set = [d for d in a2 if set(a2[d]) != set(a4[d])]
chk(bool(chg), "P4 negative control: A4 differs from A2 (rule is not inert)",
    f"{len(chg)}/{len(a2)} rebals reordered, {len(chg_set)} changed MEMBERSHIP")

# P5 basket integrity
chk(all(len(v) == 30 for v in a4.values()), "P5 every A4 rebal still picks exactly 30 names")
chk(all(len(set(v)) == len(v) for v in a4.values()), "P5b no duplicate names in an A4 basket")

# P6 OFF-path: DY unset must reproduce A2 exactly (byte-identical selector behaviour).
print("\n--- rebuilding A2 with DY env unset (OFF-path regression) ---")
_, _, mem_off, _ = build("eyonly")
off = {pd.Timestamp(d): list(g.sort_values("liq_rank")["ticker"])
       for d, g in mem_off.groupby(pd.to_datetime(mem_off["rebal_date"]))}
chk(off == a2, "P6 OFF-path (BASKET_DY_TIEBREAK unset) reproduces A2 exactly")

# ---- coverage + effect-size ledger (not a pass/fail; the numbers a reviewer will ask for) ----
cov = [(1 if dy_ref(t, d) is not None else 0) for d in a4 for t in a4[d]]
print(f"\n  DY>0 coverage inside A4 baskets: {100 * np.mean(cov):.1f}% "
      f"({sum(cov)}/{len(cov)} name-rebals)")
print(f"  rebals with a MEMBERSHIP change vs A2: {len(chg_set)}/{len(a2)}")
if chg_set:
    _in_out = []
    for d in chg_set:
        _in_out.append((str(d.date()), sorted(set(a4[d]) - set(a2[d])), sorted(set(a2[d]) - set(a4[d]))))
    for row in _in_out[:6]:
        print(f"    {row[0]}: IN {row[1]}  OUT {row[2]}")
    print(f"  mean names swapped per changed rebal: "
          f"{np.mean([len(x[1]) for x in _in_out]):.2f}")

print()
print("=" * 78)
print(f"RESULT: {len(PASS)} PASS / {len(FAIL)} FAIL")
if FAIL:
    print("FAILED: " + ", ".join(FAIL))
print("=" * 78)
sys.exit(1 if FAIL else 0)
