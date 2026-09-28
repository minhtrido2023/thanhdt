#!/usr/bin/env python3
"""Selfcheck for `close_repair.py` (Layer 2 self-computed back-adjustment).

Offline by design: every case builds its own price series and event list, so this runs with BQ
down and with the parquet cache absent. The only thing it imports from the outside is
`corp_action_lib.is_price_adjusting` (a pure predicate).

Two tiers, and the second is the one that matters:

  * ASSERTIONS pin behaviour. They pass on correct code — and a fair number of them would ALSO
    pass on subtly wrong code, which is why the second tier exists.
  * MUTATION GUARDS re-exec the module with one deliberate defect injected and require a NAMED
    assertion to go red. A test that survives the mutation is not testing the thing it claims to
    test. The mutations chosen are exactly the wrong implementations that were measured to be
    wrong on real vendor data (multiply same-day events; compare raw `Price` to the adjusted
    band; window the events by today instead of by the series) plus the fail-closed paths whose
    whole value is refusing.

Usage:  python3 close_repair_selfcheck.py [--mutations]   (both tiers run by default)
"""
from __future__ import annotations

import os
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = (HERE / "close_repair.py").read_text()

FAILS: list = []
NCHECK = 0


def check(cond, label):
    global NCHECK
    NCHECK += 1
    if not cond:
        FAILS.append(label)


def load(src=SRC, name="close_repair_under_test"):
    """Exec `src` as a fresh module. Used unmutated for the assertions and mutated for tier 2."""
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    m = types.ModuleType(name)
    m.__file__ = str(HERE / "close_repair.py")
    # @dataclass resolves annotations through sys.modules[cls.__module__]; an unregistered module
    # makes the decorator itself crash, which would look like a defect in close_repair.py.
    sys.modules[name] = m
    try:
        exec(compile(src, m.__file__, "exec"), m.__dict__)
    finally:
        sys.modules.pop(name, None)
    return m


# ------------------------------------------------------------------ fixtures

def bars(spec):
    """spec = [(date, close, price[, high, low]), ...] ascending."""
    out = []
    for row in spec:
        d, c, p = row[0], float(row[1]), float(row[2])
        hi = float(row[3]) if len(row) > 3 else 0.0
        lo = float(row[4]) if len(row) > 4 else 0.0
        out.append({"d": d, "close": c, "price": p, "high": hi, "low": lo})
    return out


def iss(ex, ratio, method="Cổ phiếu thưởng"):
    return {"event_code": "ISS", "exright_date": ex, "exercise_ratio": ratio,
            "value_per_share": None, "issue_method_name_vi": method}


def div(ex, dps):
    return {"event_code": "DIV", "exright_date": ex, "exercise_ratio": None,
            "value_per_share": dps, "issue_method_name_vi": None}


# ---------------------------------------------------------- tier 1: assertions

def run_assertions(cr, tag=""):
    """Every named check. `tag` lets the mutation tier report WHICH assertion it killed."""
    named = {}

    def nc(name, cond):
        named[name] = bool(cond)
        check(cond, f"{tag}{name}")

    # -- the flag: ON unless exactly "0" (default flipped 2026-09-28 after quant-skeptic
    #    CONFIRMED round 2). "0" is the kill switch; anything else, including absent, is ON.
    saved = os.environ.pop("MIKE_CLOSE_REPAIR", None)
    try:
        nc("flag/absent_is_on", cr.enabled() is True)
        for v, want in (("0", False), ("", True), ("true", True), ("yes", True),
                        ("2", True), ("1", True)):
            os.environ["MIKE_CLOSE_REPAIR"] = v
            nc(f"flag/{v!r}_is_{want}", cr.enabled() is want)
    finally:
        os.environ.pop("MIKE_CLOSE_REPAIR", None)
        if saved is not None:
            os.environ["MIKE_CLOSE_REPAIR"] = saved

    # -- pure stock event: computable with NO price at all (f = 1 + q)
    s = bars([("2026-09-01", 100.0, 100.0)])
    f, _n = cr.group_factor("2026-09-21", [iss("2026-09-21", 0.1)], s)
    nc("stock/bonus_10pct_is_1.1", f is not None and abs(f - 1.1) < 1e-12)

    # -- SAME-DAY COMBINE, stock legs (GEX 2026-05-05 bonus 20% + stock div 25%).
    #    Exchange: 1 + 0,45 = 1,450 (vendor measured 1,450191). Naive product 1,20*1,25 = 1,500.
    f, _n = cr.group_factor("2026-05-05",
                            [iss("2026-05-05", 0.20),
                             iss("2026-05-05", 0.25, "Trả Cổ tức bằng Cổ phiếu")], s)
    nc("sameday/stock_sums_not_multiplies", f is not None and abs(f - 1.45) < 1e-12)
    nc("sameday/stock_is_not_product", f is not None and abs(f - 1.50) > 1e-6)

    # -- SAME-DAY COMBINE, cash legs (DGC 2026-09-14: 3.000 + 5.000 on raw 46.750).
    #    Exchange: 46750/38750 = 1,206452 (vendor matched to 6 dp). Product of singles: 1,196544.
    sd = bars([("2026-09-11", 46750.0, 46750.0), ("2026-09-12", 46750.0, 46750.0)])
    f, _n = cr.group_factor("2026-09-14", [div("2026-09-14", 3000.0), div("2026-09-14", 5000.0)], sd)
    nc("sameday/cash_sums_not_multiplies", f is not None and abs(f - 46750 / 38750) < 1e-9)
    nc("sameday/cash_is_not_product", f is not None and abs(f - 1.196544) > 1e-4)

    # -- fail-closed: rights issue is unknowable from our columns
    f, note = cr.group_factor("2026-09-21",
                              [iss("2026-09-21", 0.1, "Quyền mua CP cho Cổ đông hiện hữu")], s)
    nc("failclosed/rights_is_none", f is None)
    nc("failclosed/rights_note_says_why", f is None and "quyền mua" in (note or "").lower())

    # -- fail-closed: unparsable / non-positive economic terms
    nc("failclosed/ratio_unparsable",
       cr.group_factor("2026-09-21", [iss("2026-09-21", "n/a")], s)[0] is None)
    nc("failclosed/ratio_zero",
       cr.group_factor("2026-09-21", [iss("2026-09-21", 0)], s)[0] is None)
    nc("failclosed/dps_unparsable",
       cr.group_factor("2026-09-21", [div("2026-09-21", "x")], sd)[0] is None)
    nc("failclosed/cash_exceeds_price",
       cr.group_factor("2026-09-21", [div("2026-09-21", 99999.0)], sd)[0] is None)
    nc("failclosed/unknown_code",
       cr.group_factor("2026-09-21", [{"event_code": "XYZ", "exright_date": "2026-09-21"}],
                       s)[0] is None)
    nc("failclosed/no_cum_session_for_cash",
       cr.group_factor("2026-01-01", [div("2026-01-01", 500.0)], sd)[0] is None)

    # -- the ffill BAND GUARD must LIFT the band into the raw frame.
    #    Healthy pre-event row: adjusted band [97.750, 99.520], raw Price 117.900, factor ~1,2.
    #    Comparing raw to the adjusted band directly flags this (measured on FPT 2025-06-11).
    healthy = bars([("2026-06-10", 98_000.0, 117_600.0, 99_000.0, 97_000.0),
                    ("2026-06-11", 98_500.0, 118_200.0, 99_520.0, 97_750.0)])
    f, note = cr.group_factor("2026-06-12", [div("2026-06-12", 1000.0)], healthy)
    nc("band/healthy_row_not_flagged", f is not None)
    #    Genuine ffill: the raw price of the suspect bar is carried over from T-1 and lands far
    #    outside its own lifted band.
    ffilled = bars([("2026-06-10", 50_000.0, 60_000.0, 51_000.0, 49_000.0),
                    ("2026-06-11", 40_000.0, 60_000.0, 41_000.0, 39_000.0)])
    f, note = cr.group_factor("2026-06-12", [div("2026-06-12", 1000.0)], ffilled)
    nc("band/ffill_row_refused", f is None)
    nc("band/ffill_note_says_why", f is None and "ffill" in (note or "").lower())
    #    A pure stock leg needs no price, so an unusable price bar must NOT block it.
    f, _n = cr.group_factor("2026-06-12", [iss("2026-06-12", 0.1)], ffilled)
    nc("band/stock_leg_survives_bad_price", f is not None and abs(f - 1.1) < 1e-12)
    #    A genuine band MISMATCH that is NOT a price freeze (Price moved from T-1, 60.000->58.000,
    #    so the chain-freeze short-circuit does not fire) must still be caught by the lift/band
    #    comparison itself -- keeps that comparison under live mutation coverage, distinct from
    #    the frozen-Price signature above.
    bad_band = bars([("2026-06-10", 50_000.0, 60_000.0, 51_000.0, 49_000.0),
                     ("2026-06-11", 40_000.0, 58_000.0, 41_000.0, 39_000.0)])
    f, note = cr.group_factor("2026-06-12", [div("2026-06-12", 1000.0)], bad_band)
    nc("band/bad_band_refused", f is None)

    # -- dedup on the ECONOMIC term only: identical rows collapse, real tranches sum
    kept, dropped = cr.dedup_same_term([div("2026-09-14", 3000.0), div("2026-09-14", 3000.0)])
    nc("dedup/identical_collapses", len(kept) == 1 and len(dropped) == 1)
    kept, dropped = cr.dedup_same_term([div("2026-09-14", 3000.0), div("2026-09-14", 5000.0)])
    nc("dedup/distinct_tranches_kept", len(kept) == 2 and not dropped)

    # -- THE WINDOW ENDS AT THE SERIES, NOT AT TODAY. An ex-date after the last price bar cannot
    #    be in the vendor's Close yet; counting it invents a defect on a healthy row.
    s2 = bars([("2026-09-01", 100.0, 100.0), ("2026-09-02", 100.0, 100.0)])
    r, unk, _n = cr.factor_after("2026-09-01", [iss("2026-12-01", 0.1)], s2, "2026-09-02")
    nc("window/future_exdate_ignored", abs(r - 1.0) < 1e-12 and not unk)
    r, unk, _n = cr.factor_after("2026-09-01", [iss("2026-09-02", 0.1)], s2, "2026-09-02")
    nc("window/exdate_inside_counted", abs(r - 1.1) < 1e-12)
    r, unk, _n = cr.factor_after("2026-09-02", [iss("2026-09-02", 0.1)], s2, "2026-09-02")
    nc("window/own_exdate_not_counted", abs(r - 1.0) < 1e-12)

    # -- chained ex-dates compound
    r, unk, _n = cr.factor_after("2026-09-01",
                                 [iss("2026-09-02", 0.1), iss("2026-09-02", 0.0)], s2, "2026-09-02")
    s3 = bars([("2026-09-01", 100.0, 100.0), ("2026-09-02", 100.0, 100.0),
               ("2026-09-03", 100.0, 100.0)])
    r, unk, _n = cr.factor_after("2026-09-01",
                                 [iss("2026-09-02", 0.1), iss("2026-09-03", 0.2)], s3, "2026-09-03")
    nc("chain/two_exdates_compound", abs(r - 1.1 * 1.2) < 1e-12 and not unk)

    # -- non-price-adjusting ISS (ESOP / placement) is skipped, not treated as unknown
    r, unk, notes = cr.factor_after(
        "2026-09-01", [iss("2026-09-02", 0.1, "Phát hành riêng lẻ")], s2, "2026-09-02")
    nc("taxonomy/non_adjusting_skipped", abs(r - 1.0) < 1e-12 and not unk)
    nc("taxonomy/non_adjusting_noted",
       any("NON price-adjusting" in n for n in notes))

    # -- repair_row: the decision table
    fpt = bars([("2026-06-29", 70_400.0, 70_400.0), ("2026-06-30", 70_200.0, 70_200.0)])
    bar = fpt[-1]
    rep = cr.repair_row("FPT", bar, [iss("2026-09-21", 0.1)], fpt, "2026-09-25")
    nc("repair/fires_on_missing_factor", rep.repaired)
    nc("repair/close_is_price_over_rpred", rep.repaired and abs(rep.close - 70_200.0 / 1.1) < 1e-6)
    nc("repair/labels_self_computed", rep.adj_source == "self_computed")
    nc("repair/keeps_price_untouched", rep.price == 70_200.0)
    nc("repair/reports_dev", rep.dev is not None and abs(rep.dev - (1.0 / 1.1 - 1.0)) < 1e-9)

    #    vendor already correct -> leave alone. The residual is deliberately NEGATIVE
    #    (r_obs slightly BELOW r_pred, −0,1%): a positive residual would also be refused by the
    #    "vendor adjusted more than we can explain" branch below, so the tol branch would be
    #    untested. Measured: DXG carries an unexplained −0,17% on a 14% bonus, which is the real
    #    shape this tolerance exists for.
    close_ok = 70_200.0 / (1.1 * (1 - 0.001))
    ok = bars([("2026-06-29", 64_000.0, 70_400.0), ("2026-06-30", close_ok, 70_200.0)])
    rep = cr.repair_row("FPT", ok[-1], [iss("2026-09-21", 0.1)], ok, "2026-09-25")
    nc("repair/vendor_correct_untouched", not rep.repaired and rep.adj_source == "vendor")
    nc("repair/vendor_correct_close_same", abs(rep.close - close_ok) < 1e-9)
    nc("repair/vendor_correct_dev_is_negative", rep.dev is not None and -0.003 < rep.dev < 0)

    #    an uncomputable ex-date anywhere in the window -> emit NOTHING
    rep = cr.repair_row("X", bar,
                        [iss("2026-09-21", 0.1),
                         iss("2026-09-22", 0.1, "Quyền mua CP cho Cổ đông hiện hữu")],
                        fpt, "2026-09-25")
    nc("repair/uncomputable_blocks_repair", not rep.repaired)
    nc("repair/uncomputable_listed", rep.uncomputable_ex == ("2026-09-22",))
    nc("repair/uncomputable_close_unchanged", rep.close == 70_200.0)

    #    vendor adjusted MORE than our events explain -> our table is the suspect, do not touch
    over = bars([("2026-06-29", 50_000.0, 70_400.0), ("2026-06-30", 50_000.0, 70_200.0)])
    rep = cr.repair_row("X", over[-1], [iss("2026-09-21", 0.1)], over, "2026-09-25")
    nc("repair/dev_positive_refused", not rep.repaired and rep.dev is not None and rep.dev > 0)

    #    degenerate inputs
    rep = cr.repair_row("X", {"d": "2026-06-30", "close": 0.0, "price": 100.0},
                        [iss("2026-09-21", 0.1)], fpt, "2026-09-25")
    nc("repair/close_zero_is_vendor", rep.adj_source == "vendor")
    rep = cr.repair_row("X", {"d": "2026-06-30", "close": 100.0, "price": 0.0},
                        [iss("2026-09-21", 0.1)], fpt, "2026-09-25")
    nc("repair/price_zero_is_vendor", rep.adj_source == "vendor")

    #    no events at all -> vendor, untouched
    rep = cr.repair_row("X", bar, [], fpt, "2026-09-25")
    nc("repair/no_events_is_vendor", rep.adj_source == "vendor" and rep.close == 70_200.0)

    #    a non-positive cash amount is a bad ROW, not a factor of 1: it must land in the
    #    uncomputable branch, not quietly scale nothing.
    rep = cr.repair_row("X", bar, [div("2026-09-21", -500.0)], fpt, "2026-09-25")
    nc("repair/negative_dps_uncomputable",
       not rep.repaired and rep.uncomputable_ex == ("2026-09-21",))

    # -- REGRESSION (job Taylor_20260928_105249): VNM-shape ex-date-off-by-one. VNM's real
    #    ex-date was 2026-06-25 (raw Price dropped exactly by the DIV 1.850đ that day) but
    #    `corporate_action.exright_date` records 2026-06-26 -- one session late. The vendor's
    #    Close already reflects the TRUE (06-25) ex-date throughout, so a naive group_factor
    #    that trusts our metadata's 06-26 label would compute the cum bar off an ALREADY
    #    adjusted 06-25 row and derive a wrong r_pred, risking overwriting a Close that was
    #    correct all along. Real numbers, `tav2_bq.ticker` pinned 2026-09-28.
    vnm = bars([("2026-06-22", 56_740.0, 58_600.0, 57_710.0, 56_740.0),
                ("2026-06-23", 56_600.0, 58_400.0, 57_180.0, 56_600.0),
                ("2026-06-24", 56_500.0, 58_300.0, 56_890.0, 56_310.0),
                ("2026-06-25", 56_500.0, 56_450.0, 56_790.0, 56_400.0),
                ("2026-06-26", 56_300.0, 56_300.0, 56_800.0, 55_900.0)])
    vnm_ev = [div("2026-06-26", 1850.0)]
    f, note = cr.group_factor("2026-06-26", vnm_ev, vnm)
    nc("vnm/exdate_offbyone_caught_by_band_guard", f is None)
    nc("vnm/exdate_offbyone_note_says_ffill", f is None and "ffill" in (note or "").lower())
    for d, close0 in (("2026-06-22", 56_740.0), ("2026-06-24", 56_500.0), ("2026-06-25", 56_500.0)):
        b = next(x for x in vnm if x["d"] == d)
        rep = cr.repair_row("VNM", b, vnm_ev, vnm, "2026-06-26")
        nc(f"vnm/{d}_untouched", not rep.repaired and rep.close == close0)

    # -- EDGE CASE 2a (quant-skeptic, job Taylor_20260928_105249): the NEIGHBOUR row used to
    #    lift the band is itself a chained ffill artifact (Price frozen at the SAME stale value
    #    for two consecutive sessions). `_band_lifted_suspect` only ever looks one row back, so
    #    the lift ratio it borrows is corrupted by the same defect it exists to catch. The test
    #    degenerates to "is yesterday's Close inside today's [Low,High]", which a slow market
    #    trivially satisfies -- BUG: a 2-session-frozen Price slips through undetected.
    chain = bars([("2026-01-01", 50_000.0, 50_000.0, 50_500.0, 49_500.0),
                  ("2026-01-02", 49_800.0, 50_000.0, 50_100.0, 49_600.0),   # neighbour: frozen
                  ("2026-01-03", 49_700.0, 50_000.0, 49_900.0, 49_600.0)])  # cum bar: STILL frozen
    f, _n = cr.group_factor("2026-01-04", [div("2026-01-04", 500.0)], chain)
    nc("chainffill/two_session_freeze_caught", f is None)

    # -- quant-skeptic verify round 2 (job Taylor_20260928_111625): the first chainffill fixture
    #    happens to have ALL THREE rows sharing one price, which the fix's early-exit specifically
    #    matches on (series[i-1]==bar==series[i-2]). A GENUINE 2-session-only freeze -- grandparent
    #    at a DIFFERENT price, only the immediate neighbour and the cum bar share the frozen Price
    #    -- must be caught too, or the fix only works for >=3-session freezes by coincidence.
    chain2 = bars([("2026-01-01", 50_000.0, 48_000.0, 48_500.0, 47_500.0),   # grandparent: moved
                   ("2026-01-02", 49_800.0, 50_000.0, 50_100.0, 49_600.0),   # neighbour: real trade
                   ("2026-01-03", 49_700.0, 50_000.0, 49_900.0, 49_600.0)])  # cum bar: frozen copy
    f, _n = cr.group_factor("2026-01-04", [div("2026-01-04", 500.0)], chain2)
    nc("chainffill/two_session_freeze_grandparent_differs_caught", f is None)

    # -- EDGE CASE 2b (quant-skeptic, job Taylor_20260928_105249): the row BEING REPAIRED has no
    #    ffill guard of its own -- only the cum bar *inside* group_factor is band-tested.
    #    Own Price (90.000) sits far outside its own [Low,High]=[93.500, 94.500] while its Close
    #    (94.000, the vendor's genuinely fine number) is untouched. BUG: repair_row silently
    #    replaces close=94.000 with close=90.000 (= its own stale Price) instead of refusing.
    stale = bars([("2026-06-28", 100_000.0, 100_000.0, 101_000.0, 99_000.0),
                 ("2026-06-29", 99_000.0, 99_000.0, 99_500.0, 98_500.0)])
    stale_bar = {"d": "2026-06-30", "close": 94_000.0, "price": 90_000.0,
                "high": 94_500.0, "low": 93_500.0}
    rep = cr.repair_row("X", stale_bar, [div("2026-07-01", 1000.0)], stale, "2026-06-30")
    nc("selfband/repaired_row_own_price_guarded", not rep.repaired)   # currently FAILS
    return named


# ------------------------------------------------------- tier 2: mutation guards

MUTATIONS = [
    ("sameday_multiplies_stock_legs",
     "        q_total += ratio", "        q_total = (1.0 + q_total) * (1.0 + ratio) - 1.0",
     ["sameday/stock_sums_not_multiplies", "sameday/stock_is_not_product"]),
    ("sameday_multiplies_cash_legs",
     "    f = (1.0 + q_total) * p_cum / (p_cum - d_total)",
     "    f = (1.0 + q_total) * p_cum / (p_cum - d_total) * 0.99",
     ["sameday/cash_sums_not_multiplies"]),
    ("band_compares_raw_to_adjusted_band",
     "    lift = neighbour[\"price\"] / neighbour[\"close\"]", "    lift = 1.0",
     ["band/healthy_row_not_flagged"]),
    ("band_lifts_with_the_suspect_row_itself",
     "    lift = neighbour[\"price\"] / neighbour[\"close\"]",
     "    lift = bar[\"price\"] / bar[\"close\"]",
     ["band/bad_band_refused"]),
    ("window_uses_no_upper_bound",
     "        if not ex or not (date < ex <= series_max):", "        if not ex or not (date < ex):",
     ["window/future_exdate_ignored"]),
    ("window_includes_own_exdate",
     "        if not ex or not (date < ex <= series_max):",
     "        if not ex or not (date <= ex <= series_max):",
     ["window/own_exdate_not_counted"]),
    ("rights_silently_treated_as_one",
     "                return None, (f\"{ex} ISS quyền mua: subscription price is not a column of \"\n"
     "                              f\"corporate_action (ref_price NULL on all rows) → unknowable\")",
     "                continue",
     ["failclosed/rights_is_none", "repair/uncomputable_blocks_repair"]),
    ("uncomputable_no_longer_blocks_repair",
     "    if uncomputable:", "    if False and uncomputable:",
     ["repair/uncomputable_blocks_repair", "repair/uncomputable_listed"]),
    ("flag_ignores_kill_switch",
     "    return os.environ.get(ENV_FLAG, \"1\") != \"0\"", "    return True",
     ["flag/'0'_is_False"]),
    ("vendor_agreement_no_longer_respected",
     "    if abs(dev) <= tol:", "    if False:",
     ["repair/vendor_correct_untouched", "repair/vendor_correct_close_same"]),
    ("positive_dev_now_repairs",
     "    if dev > 0:", "    if False:",
     ["repair/dev_positive_refused"]),
    ("dedup_drops_real_tranches",
     "        key = (ev.get(\"event_code\"), str(ev.get(\"exercise_ratio\")), "
     "str(ev.get(\"value_per_share\")))",
     "        key = (ev.get(\"event_code\"),)",
     ["dedup/distinct_tranches_kept", "sameday/cash_sums_not_multiplies"]),
    ("non_adjusting_events_now_counted",
     "        if not is_price_adjusting(ev):", "        if False:",
     ["taxonomy/non_adjusting_skipped"]),
    ("nonpositive_cash_treated_as_no_event",
     "            if dps <= 0:\n                return None, f\"{ex} DIV value_per_share <= 0\"",
     "            if dps <= 0:\n                continue",
     ["repair/negative_dps_uncomputable", "failclosed/dps_unparsable"]),
]


def run_mutations():
    killed, survived = 0, []
    for name, old, new, expect in MUTATIONS:
        if old not in SRC:
            survived.append(f"{name}: MUTATION ANCHOR NOT FOUND — the guard is vacuous")
            continue
        mutated = SRC.replace(old, new, 1)
        if mutated == SRC:
            survived.append(f"{name}: replace was a no-op")
            continue
        before = len(FAILS)
        try:
            named = run_assertions(load(mutated, f"mut_{name}"), tag=f"[mut:{name}] ")
        except Exception as e:
            del FAILS[before:]
            killed += 1
            print(f"  KILLED   {name:42s} (raised {type(e).__name__})")
            continue
        del FAILS[before:]          # mutated-run failures are the POINT, not real failures
        red = [k for k in expect if named.get(k) is False]
        if red:
            killed += 1
            print(f"  KILLED   {name:42s} by {', '.join(red)}")
        else:
            missing = [k for k in expect if k not in named]
            survived.append(f"{name}: expected {expect} to go red; "
                            f"{'unknown assertion names ' + str(missing) if missing else 'all passed'}")
            print(f"  SURVIVED {name:42s} <-- the assertions do not cover this defect")
    return killed, survived


def main() -> int:
    only_mut = "--mutations" in sys.argv
    print("close_repair_selfcheck — tier 1: assertions")
    if not only_mut:
        run_assertions(load())
        print(f"  {NCHECK} assertions, {len(FAILS)} failed")
        for f in FAILS:
            print(f"    FAIL {f}")
    print("\nclose_repair_selfcheck — tier 2: mutation guards")
    killed, survived = run_mutations()
    print(f"\n  {killed}/{len(MUTATIONS)} mutations killed")
    for s in survived:
        print(f"    SURVIVED {s}")
    bad = len(FAILS) + len(survived)
    print(f"\n{'PASS' if bad == 0 else 'FAIL'} — {NCHECK} assertions run, "
          f"{len(FAILS)} assertion failures, {len(survived)} surviving mutations")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
