#!/usr/bin/env python3
"""oshares_live.py — shares outstanding at ANY date, without waiting for the next quarterly report.

STATUS: WIRED (2026-08-13) through `oshares_pit.py`, and SAFE to call directly since the AIS
certification gate moved in here (round 4, job `Taylor_20260813_154112`).
Round 1 REFUTED this module on 2026-08-13 for the two defects rewritten below; round 2 CONFIRMED
the rewrite (bus, 2026-08-13T06:06:49Z) and two consumers went live the same day:
`custom30_core_select_audit.py` (historical) and `rating_8l.py::_reconcile_oshares` (live).

WHERE THE AIS GATE LIVES — HERE, NOT IN THE ADAPTER (changed 2026-08-13, round 4)
---------------------------------------------------------------------------------
Until round 4 this module accepted `AIS.shares_total_after` UNCONDITIONALLY and the certification
gate lived in `oshares_pit._ais_verdicts`, at the CONSUMER layer — so `oshares_at()` called
directly still answered 3.000.000.000 for IDC across 2020-05-28 → 2022-09-05 (~10× too high for
two years) and 461.723.054 for FPT on 2020-05-05 (−32,3%), with only a docstring warning between a
new consumer and those numbers. A docstring is not a gate. `_ais_verdicts` + the serve policy now
live BELOW, and `oshares_at` refuses an uncertified AIS anchor itself: `value=None`,
`method="AIS_UNCERTIFIED"`, whatever it declined to serve preserved in `uncertified_value` so a
caller can log it. No caller can route around it, and there is exactly one copy of the logic —
`oshares_pit` imports this one rather than keeping a second.

⚠️ THIS IS NOT THE SAME AS "SAFE TO SUBSTITUTE FOR YOUR CURRENT NUMBER". `oshares_at` DECLINES far
more often the further back you look (33,3% of a 108-name universe at 2014-07-01), so a naked
substitution trades look-ahead for a bigger availability bias. A consumer still needs a fallback
policy, and that is what `oshares_pit` / `oshares_reconciled` are for — plus the coarse
`SANITY_FACTOR` magnitude gate, which is deliberately a CONSUMER-layer decision and stayed there
(measured 2026-08-13: it still catches ~27 gross-error cells this certification gate does not).

Replaces the manual path (`update_shares_live.py`, run by hand into the 4-row
`tav2_bq.shares_outstanding_live`) with a computed answer from two sources that already exist:
`ticker_financial.OShares` (quarterly) + `tav2_bq.corporate_action` (per-event).

THE PROBLEM
-----------
`ticker_financial.OShares` only moves when a quarter is published, so between reports it is stale
by up to ~3 months — and it is the denominator of market cap, EPS and every per-share metric. A
15% bonus issue makes it 15% wrong the day the stock goes ex.

WHY THE FIRST VERSION WAS WRONG (both defects measured, both fixed here)
------------------------------------------------------------------------
(1) It picked whichever of `ticker_financial` / `AIS` carried the LATEST date and called that the
    "freshest asserted fact". But `ticker_financial.OShares` is **RESTATED, not point-in-time**:
    a quarterly row is rewritten later to carry the share count as it stands at publication (or
    later still). Measured 2026-08-13 on the whole table: **2.667 quarterly rows across 576
    tickers** carry a value that equals an AIS listed count which only became effective LATER —
    up to **2.693 days** later, **626 of them since 2024-01-01**. So "ticker_financial moves
    first" is mostly a restatement artifact, i.e. LOOK-AHEAD, not early data.

    Concrete: HAH's quarterly row dated **2026-02-02** already carries **185.840.401** — the count
    that only came into existence with the AIS of **2026-05-27** (listing 16.979.189 shares from a
    convertible-bond conversion on 2026-03-12 and an ESOP on 2026-04-17, both AFTER 02-02). The
    old code answered 185.840.401 for 2026-03-01. The truth that day was 168.861.212.

(2) It rolled forward with `(1 + exercise_ratio)` for every ISS — but `exercise_ratio` is 0 or
    NULL for **3.914 of 9.297** executed ISS rows (42%), and the zeros are concentrated exactly in
    the methods that do not accrue to existing holders: private placement 2.187/2.280, ESOP
    1.105/1.222, convertible-bond conversion 240/243, auction 140/142, merger 85/99. Multiplying
    by 1.0 there is a silent no-op that was nevertheless labelled `ISS_ESTIMATE`, i.e. reported as
    if the event had been accounted for. `shares_delta` cannot rescue it: that column is
    **NULL on 100% of ISS rows (0 of 9.297)** — it is populated only on AIS/NLIS/SUSP.

THE METHOD — an anchor that must EXPLAIN ITSELF, then a fail-closed roll-forward
-------------------------------------------------------------------------------
For a target date D, using only facts knowable at D (no row dated after D is consulted, in either
direction — the gate below is point-in-time, so a backtest at D gets the same answer live-at-D):

  1. `AIS.shares_total_after` (latest `effective_date <= D`) is the exact anchor: it is the
     registry's own statement of the listed count.
  2. A `ticker_financial` row (latest `time <= D`) is admitted as an anchor ONLY IF its value is
     EXPLAINED — i.e. the last AIS at-or-before that row, rolled forward through the executed ISS
     between them, reproduces it within 0,1%. FPT's 2025Q2 row (dated 07-22, carrying the
     post-bonus 1.703.507.121 seven weeks before the AIS) IS explained — the 15% bonus went ex on
     07-21, one day earlier — so genuine early data still gets used. HAH's 2026-02-02 row is NOT
     explained (no event between the 2025-09-09 AIS and 02-02 accounts for +16.979.189) and is
     rejected. A row that cannot be explained because an intervening ISS has no usable ratio is
     also rejected: unverifiable is not the same as verified.
  3. Roll the surviving anchor forward through every executed ISS with `exright_date` in
     (anchor_date, D], preferring `shares_delta` when present (additive, exact) and falling back
     to `(1 + exercise_ratio)`. An ISS with NEITHER — ratio in {0, NULL} and no delta — **fails
     CLOSED**: `value=None`, `method="UNKNOWN_RATIO"`, the blocking events listed. It is not
     multiplied by 1.0 and it is not labelled as handled.

WHICH EVENTS COUNT — every ISS, not just the price-adjusting ones
-----------------------------------------------------------------
Share count and price adjustment are different questions (see `corp_action_lib`). An ESOP issue
creates shares without touching the price; excluding it because "the price didn't move" would
undercount. Verified on FPT's two 2025-05-07 ESOP tranches: rolling the 2025-04-23 quarterly count
forward through both gives 1.481.340.xxx against the 2025-06-19 AIS ground truth of 1.481.330.122
— 0,0007% apart. Both gaps are fractional-share rounding, not method error.

ACCURACY, STATED HONESTLY
-------------------------
`AIS_EXACT`      — the anchor is an AIS that PASSED the certification gate below and nothing
                   ratio-derived happened since: the registry's own number, checked.
`AIS_UNCERTIFIED` — the anchor is an AIS that could NOT be reconciled with the AIS before it.
                   **`value is None`**; the refused number is kept in `uncertified_value` for the
                   caller's log, never as an answer.
`ANCHOR_ONLY`    — the anchor is a quarterly row that PASSED the explanation gate, nothing since.
`ANCHOR_UNVERIFIED` — the anchor is a quarterly row for a ticker with no AIS before it, so the
                   gate had nothing to check it against (DHG). The number is returned because
                   blanking every never-listed-again ticker is a coverage loss the data does not
                   justify — but it is NOT cleared, and a consumer that needs a checked number
                   must treat this like a miss.
`ISS_ESTIMATE`   — rolled through at least one ratio-derived event: ~0,001% observed error on FPT;
                   an ESTIMATE because `exercise_ratio` is rounded and treasury/fractional-share
                   handling is not modelled.
`UNKNOWN_RATIO`  — an intervening ISS carries no usable size. **`value is None`** — the caller
                   gets nothing, deliberately, rather than a number that is quietly the old one.
`FIN_FALLBACK`   — the explanation gate REFUSED the quarterly row, but the AIS anchor has been
                   silent for more than `FIN_FALLBACK_MAX_AIS_AGE_DAYS` and the row is newer than
                   that AIS. Served anyway, rolled through any ISS since. `anchor_verified` is
                   False — the gate never cleared it. See the policy note below, which includes
                   the look-ahead this label knowingly re-admits.
`NO_ANCHOR`      — nothing admissible at or before D.

STALE-AIS FALLBACK TO `ticker_financial` (policy, user-approved 2026-08-19)
---------------------------------------------------------------------------
Every corporate action that moves the share count between reports (issue, buyback, split) is
reflected in the next published financial statement, and `ticker_financial.OShares` is then
restated to the true count. So once the last AIS is more than a quarter old, the newest quarterly
row is the better statement of reality — the AIS has simply stopped being updated.

`VRE` is the case that forced this: its only AIS is **2018-12-26 = 2.328.818.410**, the 2019
buyback of 56.500.000 shares produced **no corp-action row at all**, and the quarterly rows have
carried the correct **2.272.318.410** since 2019-10-29. Before this change `oshares_at` served the
2018 number — 2,49% too high — for seven years, at the highest-confidence label `AIS_EXACT`,
because the explanation gate rejected the (correct) quarterly row: 2.272.318.410 cannot be rolled
forward from the 2018 AIS, there being no event to explain the DECREASE. A gate built to catch
restatement cannot tell a restated row from an unreported buyback, so it rejects both.

⚠️ THE COST, STATED BECAUSE IT IS REAL. `ticker_financial.OShares` is filed **TRAP** in the data
registry (`mike/kb/data_registry/fundamentals/ticker_financial_oshares.md`) precisely because it is
RESTATED, not point-in-time: 2.667 quarterly rows across 576 tickers carry a value that only became
effective LATER (measured 2026-08-13). This fallback re-admits that column, so on a STALE-AIS
ticker a historical `asof` can now receive a restated — i.e. look-ahead — number, which the
explanation gate used to block. Two things bound the damage and neither is a proof of safety:
  * the fallback only fires when the AIS anchor is stale, so the tickers with an actively
    maintained AIS trail (where the gate does real work) are untouched;
  * it does not disable the ISS roll-forward — a quarterly row is still moved through every ISS
    dated after it, so a bonus that went ex after the last report is not lost.
For VRE specifically the fallback is clean point-in-time (the quarterly series steps 1.901.078.733
→ 2.328.818.410 on 2018-10-31 → 2.272.318.410 on 2019-10-29, i.e. it tracks the events instead of
being back-filled). That is one ticker, not a guarantee about the other 575.
NO DIRECTION GATE — THE COST IS ACCEPTED, MEASURED, AND WRITTEN DOWN HERE
The first cut of this fallback shipped with a fifth condition: refuse a quarterly row HIGHER than
the rolled-forward AIS, on the reasoning that `ISS` only ever adds shares and there is no event
code for a buyback, so an unexplained DECREASE is the change the feed structurally cannot report
while an unexplained INCREASE is one it was supposed to. **That condition was removed 2026-08-19
on the user's instruction** ("`ticker_financial` is the authoritative source once the AIS is
stale"), because the sign of the miss does not in fact separate the two cases: shares issued by
private placement are real and restated into the next quarterly report long before the exchange
lists them, so a perfectly valid count arrives as an unexplained INCREASE.

MEASURED, 246 tickers of the current `ticker_prune` universe, both directions stated:
  * asof 2026-08-19 (live use): 8 tickers change. Three of them (`VPB` 7.933.923.601, `QNS`
    367.648.153, `NAF` 61.181.992) go from **no answer at all** (`UNKNOWN_RATIO`) to a number;
    `OIL` goes 201.425.936 → 1.034.229.500, i.e. the AIS trail was understating it by 5x. None
    carries the restatement signature — but at asof = the edge of the data there is no future to
    check against, so that is an ABSENCE OF EVIDENCE, not evidence of absence.
  * asof 2026-03-01 (backtest use, 5,5 months of future data available to audit against): 12
    tickers change and **3 of them are genuine look-ahead** — `HAH` 185.840.401 (the count created
    by the 2026-03-12 conversion + 2026-04-17 ESOP, listed 2026-05-27), `ABB` 1.397.208.685 (AIS
    2026-06-19), `NVL` 2.234.496.474 (AIS 2026-05-29). Signature: the served value equals, to the
    share, an AIS that only became effective LATER. **~25% of affected answers.**
⚠️ `HAH` at 2026-03-01 is the exact number regression check `H1` was written to prevent, and this
module now returns it. `H1`/`H2` in `_selfcheck` were rewritten to assert the new behaviour and
are labelled ACCEPTED COST — they are not evidence the look-ahead was fixed.
⚠️ There is no known point-in-time discriminator left. The restatement signature above needs the
FUTURE AIS to compute, so it can audit an answer afterwards but cannot gate one live; a restated
row carries no other tell (its `time` is not rewritten). Anyone who wants the protection back has
to bring a new data source, not a cleverer read of this one.
⚠️ `SUSP` carries 605 executed rows with a NEGATIVE `shares_delta` (cancellations) and this module
does not read it. Wiring it in could turn some refusals into explained decreases — not attempted
here, out of scope, written down so it is not rediscovered.
⇒ A BACKTEST consumer that cares about look-ahead must read `method == "FIN_FALLBACK"` and decide
for itself; `anchor_verified` is False on every one of them.

RESIDUAL LIMITATION, STATED BECAUSE IT CANNOT BE CLOSED FROM THIS SIDE
-----------------------------------------------------------------------
The explanation gate can only reject a restated quarterly row when the restatement contradicts
events the feed already carries. A row restated to a count whose backing AIS has not been ingested
yet is invisible to it — the same blind spot every point-in-time reconstruction has. That is one
more reason `ticker_financial.OShares` is filed TRAP in the data registry
(`mike/kb/data_registry/fundamentals/ticker_financial_oshares.md`) and why AIS, not the quarterly
row, is the primary anchor here.
"""
from __future__ import annotations

import itertools
from datetime import date

from corp_action_lib import TABLE, bq, dilutes_share_count

FIN_TABLE = "lithe-record-440915-m9.tav2_bq.ticker_financial"

# An AIS older than this (in days, relative to `asof`) is no longer treated as the freshest
# statement of the listed count: a quarterly `ticker_financial` row dated after it takes over as
# the anchor (`FIN_FALLBACK`). 90 days = one reporting quarter, the interval at which OShares is
# republished — the point past which "no AIS since" stops meaning "nothing has changed".
FIN_FALLBACK_MAX_AIS_AGE_DAYS = 90

# a quarterly count is "explained" by the rolled-forward AIS when it lands this close. The largest
# real gap measured is FPT's 0,0013% (fractional-share rounding on a 15% bonus); 0,1% leaves two
# orders of magnitude of headroom over that while still rejecting HAH's 10,1% jump.
EXPLAIN_TOL = 0.001


def _days_between(d0, d1):
    """`d1 - d0` in days, both "YYYY-MM-DD" strings. Plain date arithmetic — no timezone enters
    here (both ends are calendar dates already fixed by BQ / the caller's `asof`), so §16 of the
    coding guidelines does not apply."""
    return (date.fromisoformat(d1) - date.fromisoformat(d0)).days


def _dedup_iss(events):
    """Drop revisions of the same issuance; keep genuinely distinct tranches.

    Bẫy (3) of the registry: rows can repeat on (ticker, exright_date, event_code). Two rows on
    one day are REAL when they are different issuances (MBB 2026-08-11 = a 10% rights issue AND a
    15% stock dividend, both of which add shares) and a DUPLICATE when they restate the same one.
    Key on (exright_date, issue_method_name_vi, exercise_ratio): FPT's two 2025-05-07 ESOP rows
    differ in ratio (0,00225 vs 0,00472) and both survive, as they must.
    """
    seen, out = set(), []
    for e in events:
        key = (e["exright_date"], e.get("issue_method_name_vi"), str(e.get("exercise_ratio")))
        if key in seen:
            continue
        seen.add(key)
        out.append(e)
    return out


def _subset_matching(pool, target, tol=1.0):
    """Indices of the ISS in `pool` whose `issue_volumn` sums to `target`, or None.

    `pool` is a list of `(index, event)`. Returns None — meaning "the accounting does not close"
    — rather than a best guess, because every caller treats None as "assume absorbed", the
    conservative direction. Candidate sets are tried smallest-first and, within a size, in
    ex-date order, so the FIFO reading wins when two tranches happen to be the same size.
    """
    vols = []
    for i, e in pool:
        v = e.get("issue_volumn")
        if v is None or float(v) <= 0:
            return None                    # a sizeless event in the pool: no accounting possible
        vols.append((i, float(v)))
    if len(vols) > 14:                     # 2**14 subsets is the practical ceiling; bail out
        return None
    for k in range(1, len(vols) + 1):
        for combo in itertools.combinations(vols, k):
            if abs(sum(v for _i, v in combo) - target) <= tol:
                return {i for i, _v in combo}
    return None


def _unabsorbed_iss(ais_rows, iss, upto_exright):
    """The ISS issued on or before `upto_exright` that the AIS chain has NOT demonstrably listed.

    ⚠️ ADDED 2026-08-19 (job `Taylor_20260819_044259`). Until then the only test anywhere in this
    module was `exright_date <= anchor_date`, and that is WRONG for an issue with a lock-up,
    because the two facts are not the same fact:
      * `exright_date` — the day the shares are ISSUED. They exist and dilute from this day, and
        the company's own balance sheet counts them from this day.
      * the AIS — the day the exchange LISTS them and restates `shares_total_after`.
    `HAH` is the case that forced the fix: an ESOP went ex 2026-04-17 (2.500.000 shares) and the
    next AIS, 2026-05-27, has `shares_delta` = 16.979.189 — exactly the convertible-bond
    conversion of 2026-03-12 and nothing else. Those 2,5 triệu shares are issued, are in the
    Q2/2026 report, and are in NO AIS. Under the old test they were filtered out as "already in
    the anchor" and disappeared for as long as the lock-up lasts.

    ⚠️ `listing_date` IS NOT THE FIELD THAT ANSWERS THIS — measured, after it was tried and it
    failed. It looks right in aggregate (join `ISS.listing_date` to `AIS.effective_date` and
    3.529 of 3.642 matched groups reproduce `shares_delta` exactly) and it is wrong precisely on
    the events this function exists for:
      * `FPT`'s ESOP of 2024-10-09 carries `listing_date` **2034-10-09** and **2027-10-11** — yet
        the AIS of 2025-01-02 lists `shares_delta` = 10.621.117 = 3.319.000 + 7.302.117, i.e.
        BOTH tranches, under three months later. The far date is the transfer-restriction expiry.
      * `VND`'s two issues of 2024-05-29 carry `listing_date` 2024-09-04 and 2025-07-14 and were
        BOTH listed by the single AIS of 2024-08-22 (`shares_delta` = 304.455.899 = their exact
        sum). The field is an announced intention that reality overtakes.
    Measured cost of gating on it: on 212 `ticker_prune` names, 45 counts came out too high, up
    to **+58,6%** (`AMS`), against 2 improved. Do not reintroduce it.

    SO THE TEST IS THE ACCOUNTING, NOT A DATE — and it is scoped to ONE window, deliberately:

        (prev AIS, last AIS]   the only window where "is this share listed?" is still open

    Take the last AIS's own `shares_delta` and find the subset of ISS in that window whose
    `issue_volumn` sums to it. Those are what it listed; the remainder in that window is not
    listed yet. Anything older than `prev AIS` is presumed listed and is NEVER re-added:
    `shares_total_after` is an ABSOLUTE level, not a running total, so an old issue is inside it
    whether or not this code can reconstruct which AIS absorbed it. Walking the whole chain and
    accumulating unmatched events instead was tried the same day and is catastrophically wrong —
    one failed match early in a ticker's history orphans an event that then rides forward onto
    every later answer: 98 of 212 names came out too high, `VNM` by +683 triệu shares (+32,7%).

    FAIL-CLOSED MEANS "ASSUME LISTED", and every uncertain branch takes it: no prior AIS, no
    usable delta, a window member with no `issue_volumn`, a window too large to search, or simply
    no subset that adds up ⇒ the whole window is treated as listed. Adding a share the registry
    has already counted inflates the denominator of every per-share metric silently; declining to
    add one leaves the already-shipped answer in place. The two directions are not symmetric, so
    this only widens where the arithmetic proves the widening.
    """
    pool = _dedup_iss([e for e in iss if e["exright_date"] <= upto_exright])
    rows = sorted(ais_rows, key=lambda x: x["effective_date"])
    if not rows:
        return pool                              # no AIS at all: nothing has been listed by one
    last = rows[-1]
    prev = next((r for r in reversed(rows[:-1])
                 if r["effective_date"] < last["effective_date"]), None)
    after = [e for e in pool if e["exright_date"] > last["effective_date"]]
    if prev is None:
        return after                             # first AIS of the ticker: nothing to difference
    window = [(i, e) for i, e in enumerate(pool)
              if prev["effective_date"] < e["exright_date"] <= last["effective_date"]]
    # THE LEVEL, NOT `shares_delta` — priority measured, not stylistic. `shares_total_after` is
    # the registry's statement of the whole listed count; `shares_delta` is the size of ONE
    # notice, and a single restatement routinely settles several. `MBS` 2026-07-02 carries
    # `shares_delta` = 333.644.470 (the rights issue) while its level rose 342.236.664 — the
    # rights issue PLUS the 8.592.194 ESOP of 2026-01-22. Sizing the window off `shares_delta`
    # left that ESOP looking unlisted and added it a second time; `HVH` 2026-07-14 (+20 triệu
    # private placement) and `MBS` are two of the six such false adds this priority removes.
    if float(last["shares_total_after"]) > float(prev["shares_total_after"]):
        delta = float(last["shares_total_after"]) - float(prev["shares_total_after"])
    else:
        return after                             # level flat or falling: nothing provable here
    picked = _subset_matching(window, delta)
    if picked is None:
        return after
    return [e for i, e in window if i not in picked] + after


def _pending_iss(ais_rows, iss, anchor_date, anchor_source, asof):
    """The ISS still to be rolled onto an anchor — the answer depends on WHICH anchor it is.

    An AIS states the LISTED count, so what it already contains is decided by the accounting of
    the AIS chain up to it (`_unabsorbed_iss`). A `ticker_financial` row states the ISSUED count
    — a private placement is in the balance sheet from the day it is issued, long before the
    exchange lists it (that is the whole reason `FIN_FALLBACK` exists) — so for a quarterly
    anchor the ex-date remains the right test and the AIS chain must NOT be consulted. Using one
    rule for both anchors would either lose lock-up shares from an AIS or double-count
    placements on a quarterly row.
    """
    if anchor_source == "corporate_action.AIS":
        return _unabsorbed_iss([r for r in ais_rows if r["effective_date"] <= anchor_date],
                               iss, asof)
    return _dedup_iss([e for e in iss if e["exright_date"] > anchor_date])


def _roll(anchor_value, events):
    """(value, blockers) — roll `anchor_value` through `events` in ex-date order, fail-closed.

    Size fallback order, most exact first: `shares_delta` (additive, the registry's own count of
    new shares) → `issue_volumn` (the ISS row's own share count) → `(1 + exercise_ratio)`. An
    event offering none of the three is a BLOCKER: it is returned, not skipped, and the caller
    must refuse to answer. Measured on 2026-08-13, `shares_delta` is NULL on every one of the
    9.297 executed ISS rows, so the delta branch is dead today — it is here because the fallback
    order is the correctness statement, and a vendor backfill must not silently keep using the
    rounded number once the exact one arrives.

    ⚠️ `issue_volumn` ADDED 2026-08-19 (job `Taylor_20260819_044259`) and it is the single biggest
    behaviour change this function has had. Measured on the whole table that day:
      * it is populated on **9.273 of 9.304** executed ISS rows (99,7%), against `exercise_ratio`
        which is 0/NULL on 3.914 (42%). It rescues **3.867** of those 3.914 — i.e. rows this
        function used to fail CLOSED on now get an exact answer; only **18** rows are left with
        no usable size at all.
      * it is not merely more AVAILABLE, it is more ACCURATE. Ground truth = `AIS.shares_delta`
        joined on `ISS.listing_date == AIS.effective_date` (3.642 matched groups): `issue_volumn`
        reproduces it EXACTLY on 3.529 (96,9%), within 0,1% on 3.542. Head-to-head on the 2.155
        groups carrying BOTH fields: `issue_volumn` 95,6% within 0,1% (median error 0,0) against
        `exercise_ratio` 76,2% (median 8,2e-5). The ratio is rounded to 4-5 decimals; the volume
        is a count.
    ⇒ an event applied via `shares_delta` or `issue_volumn` is an exact registry COUNT, so it does
    not make the answer an estimate; only the `exercise_ratio` branch does (see `iss_estimate` in
    `oshares_at`).
    """
    value, applied, blockers = float(anchor_value), [], []
    for e in sorted(events, key=lambda r: r["exright_date"]):
        delta = e.get("shares_delta")
        vol = e.get("issue_volumn")
        ratio = e.get("exercise_ratio")
        if delta is not None and float(delta) != 0.0:
            value += float(delta)
            applied.append((e, "shares_delta", float(delta)))
        elif vol is not None and float(vol) > 0.0:
            value += float(vol)
            applied.append((e, "issue_volumn", float(vol)))
        elif ratio is not None and float(ratio) > 0.0:
            value *= (1.0 + float(ratio))
            applied.append((e, "exercise_ratio", float(ratio)))
        else:
            blockers.append(e)
    return value, applied, blockers


def _event_dict(e, how=None, size=None):
    d = {"exright_date": e["exright_date"], "listing_date": e.get("listing_date"),
         "method_vi": e.get("issue_method_name_vi"),
         "title": e.get("title"), "ratio": e.get("exercise_ratio"),
         "issue_volumn": e.get("issue_volumn"), "shares_delta": e.get("shares_delta")}
    if how:
        d["applied_via"], d["applied_size"] = how, size
    return d


def _fetch(tickers, until):
    tk = ",".join(f'"{t}"' for t in tickers)
    quarters = bq(f"""
        SELECT ticker, CAST(time AS STRING) time, OShares
        FROM `{FIN_TABLE}`
        WHERE ticker IN ({tk}) AND time <= DATE "{until}" AND OShares IS NOT NULL AND OShares > 0
        ORDER BY ticker, time
    """)
    corp = bq(f"""
        SELECT ticker, event_code, CAST(exright_date AS STRING) exright_date,
               CAST(effective_date AS STRING) effective_date,
               CAST(listing_date AS STRING) listing_date,
               exercise_ratio, issue_volumn, issue_method_name_vi, shares_delta,
               shares_total_after,
               SUBSTR(event_title_vi, 1, 70) AS title
        FROM `{TABLE}`
        WHERE ticker IN ({tk}) AND event_status = "executed" AND event_code IN ("ISS", "AIS")
        ORDER BY ticker, COALESCE(exright_date, effective_date)
    """)
    return quarters, corp


def _explain_quarterly(q, ais, iss):
    """(ok, verified, reason, expected) — can the last AIS at-or-before `q` be rolled INTO `q`?

    `expected` is the rolled-forward count the gate compared against, or None when no expectation
    could be built at all (no prior AIS, or a blocking ISS). It no longer gates anything — the
    stale-AIS fallback stopped reading the direction of the miss on 2026-08-19 — but it is still
    returned and stamped on the answer as `fin_expected_from_ais`, because "what the AIS trail
    predicted, and by how much the report disagreed" is the first thing anyone auditing a
    `FIN_FALLBACK` number asks, and re-deriving it at the call site would be a second copy of
    this roll.

    This is the gate that makes a restated quarterly row unusable. `ais`/`iss` are already clipped
    to `asof` by the caller, and the primary test looks only at rows dated at or before
    `q["time"]`, so it never consults the future to answer a question about the past.

    Two outcomes short of a clean pass:
      * no AIS at all before `q` — nothing to check against. Rejecting outright would blank out
        every ticker that has never listed additional shares (DHG), which is a coverage loss the
        data does not justify. Admit it, but return `verified=False` so the answer is labelled
        `ANCHOR_UNVERIFIED` rather than passed off as checked — unless an AIS AFTER `q` (still at
        or before `asof`) already carries exactly this value, which is the restatement signature
        with no innocent reading available here.
      * an intervening ISS with no usable size — the expectation cannot be built, so the row
        cannot be cleared. Unverifiable is not the same as verified.
    """
    t, v = q["time"], float(q["OShares"])
    prior = [a for a in ais if a["effective_date"] <= t]
    if not prior:
        hit = [a for a in ais if a["effective_date"] > t
               and abs(float(a["shares_total_after"]) - v) < 1.0]
        if hit:
            return False, False, (
                f"{v:,.0f} trùng ĐÚNG số của AIS {hit[0]['effective_date']} (SAU ngày quý "
                f"{t}) và không có AIS nào trước đó để giải thích ⇒ RESTATE"), None
        return True, False, "không có AIS nào <= ngày quý ⇒ nhận nhưng KHÔNG kiểm chứng được", None
    a = max(prior, key=lambda r: r["effective_date"])
    # not `a.effective_date < exright <= t` any more: an ISS that went ex BEFORE the AIS but is
    # absent from its `shares_delta` (a lock-up ESOP) is missing from the AIS and PRESENT in the
    # quarterly report, so it belongs in the expectation. Same predicate as `oshares_at` uses —
    # one rule, not two. HAH's quarterly row of 2026-07-30 (191.840.401) only closes against the
    # AIS of 2026-05-27 (185.840.401) once both unlisted ESOP tranches are in it.
    between = _unabsorbed_iss([r for r in ais if r["effective_date"] <= a["effective_date"]],
                              iss, t)
    expected, _applied, blockers = _roll(float(a["shares_total_after"]), between)
    if blockers:
        return False, False, (f"ISS {[b['exright_date'] for b in blockers]} không có tỉ lệ/"
                              f"shares_delta ⇒ không dựng được kỳ vọng để đối chiếu"), None
    if abs(v - expected) / expected > EXPLAIN_TOL:
        return False, False, (f"{v:,.0f} không giải thích được từ AIS {a['effective_date']} "
                              f"({float(a['shares_total_after']):,.0f}) + {len(between)} ISS "
                              f"⇒ kỳ vọng {expected:,.0f}, lệch {(v/expected-1)*100:+.2f}%"), expected
    return True, True, "", expected


def _stale_fallback_verdict(q, a, ais_age_days, ais_certified):
    """(allow, reason) — số quý bị cổng giải thích LOẠI có được phục vụ như FIN_FALLBACK không?

    Chỉ chạy khi `_explain_quarterly` đã LOẠI dòng quý. BA điều kiện, tất cả đều cần:

      1. CÓ một neo AIS. Không có AIS mà vẫn bị loại thì lý do loại duy nhất là chữ ký RESTATE
         (`v` trùng khít một AIS SAU ngày quý) — đó là bằng chứng look-ahead, không phải lý do
         để tin dòng quý.
      1b. Neo AIS đó phải ĐƯỢC CHỨNG NHẬN (`_ais_certified`). Cổng vòng 4 nói rõ: neo AIS trượt
         cổng thì KHÔNG được "tụt sang neo dòng quý" — làm thế là ĐỔI SỐ chứ không phải dời cổng.
      2. Neo AIS đã CŨ hơn một kỳ báo cáo (`FIN_FALLBACK_MAX_AIS_AGE_DAYS`). Còn tươi thì nó vẫn
         là phát biểu mới nhất của sở về số CP niêm yết; không có gì để thay thế.
      3. Dòng quý phải MỚI HƠN neo AIS. Nếu không, "rơi về BCTC" là đi LÙI.

    ĐIỀU KIỆN THỨ TƯ ĐÃ BỎ 2026-08-19 (chỉ đạo user, job Taylor_20260819_032946). Nó đọc CHIỀU:
    dòng quý CAO hơn kỳ vọng lăn từ AIS ⇒ từ chối, vì feed chỉ có `ISS` (luôn CỘNG) và không có
    mã sự kiện mua cổ phiếu quỹ, nên số GIẢM là thứ feed không thể báo còn số TĂNG là thứ lẽ ra
    phải có. Lập luận đó SAI ở một ca thật: **cổ phiếu phát hành riêng lẻ là cổ phiếu THẬT và
    được BCTC ghi nhận từ trước ngày NIÊM YẾT BỔ SUNG**, nên một số đúng vẫn tới dưới dạng TĂNG
    không giải thích được. Chính sách user: khi AIS đã cũ, `ticker_financial` là nguồn tốt nhất.

    ⚠️ CÁI GIÁ, ĐO ĐƯỢC, KHÔNG ĐƯỢC QUÊN: bỏ cổng này đồng thời nhận lại look-ahead thật. Trên
    246 mã `ticker_prune`, tại asof=2026-03-01 (có 5,5 tháng dữ liệu tương lai để đối chiếu) 12 mã
    đổi số và **3 mã mang chữ ký RESTATE** — giá trị phục vụ trùng KHÍT một AIS chỉ có hiệu lực
    SAU đó: HAH 185.840.401 (AIS 2026-05-27), ABB 1.397.208.685 (AIS 2026-06-19), NVL
    2.234.496.474 (AIS 2026-05-29). Không còn cổng point-in-time nào chặn chúng: chữ ký RESTATE
    cần chính AIS TƯƠNG LAI mới tính được. Consumer backtest phải tự đọc `method == "FIN_FALLBACK"`
    (`anchor_verified` luôn False) và tự quyết.
    """
    if a is None:
        return False, "không có neo AIS: dòng quý bị loại vì chữ ký RESTATE, không phải vì AIS cũ"
    if not ais_certified:
        return False, (f"neo AIS {a['effective_date']} CHƯA được chứng nhận ⇒ giữ nguyên luật "
                       f"vòng 4 (từ chối trả lời), không đi vòng sang neo dòng quý")
    if ais_age_days is None or ais_age_days <= FIN_FALLBACK_MAX_AIS_AGE_DAYS:
        return False, (f"neo AIS {a['effective_date']} còn tươi ({ais_age_days} ngày "
                       f"<= {FIN_FALLBACK_MAX_AIS_AGE_DAYS}) ⇒ không rơi về BCTC")
    if q["time"] <= a["effective_date"]:
        return False, (f"dòng quý {q['time']} CŨ hơn neo AIS {a['effective_date']} ⇒ rơi về BCTC "
                       f"là đi LÙI")
    return True, (f"neo AIS {a['effective_date']} cũ {ais_age_days} ngày (> "
                  f"{FIN_FALLBACK_MAX_AIS_AGE_DAYS}); dòng quý {q['time']} = "
                  f"{float(q['OShares']):,.0f} mới hơn ⇒ BCTC là phát biểu tốt nhất về số CP "
                  f"đang lưu hành (chính sách user 2026-08-19, KHÔNG xét chiều tăng/giảm)")


# Verdict nào của một neo AIS thì ĐƯỢC PHỤC VỤ. Đây là dòng CHÍNH SÁCH của cổng — mọi thứ khác
# chỉ là cách tính verdict. Đo 2026-08-13 (job Taylor_20260813_142812), xem `_ais_verdicts`:
#   "OK"        — đối chiếu được với AIS liền trước và KHỚP.
#   "NO_PRIOR"  — là AIS ĐẦU TIÊN có `shares_total_after` của mã: KHÔNG CÓ GÌ để đối chiếu, khác
#                 hẳn "dựng được kỳ vọng và nó SAI". Phục vụ, đúng như `_explain_quarterly` xử lý
#                 dòng quý không có AIS nào trước nó (nhận, nhưng không coi là đã kiểm) — và ở
#                 tầng consumer neo này vẫn còn cổng biên độ `oshares_pit._sane` đứng sau.
#                 ĐO ĐƯỢC (rổ 171 mã × 48 ngày rebal = 7.610 ô):
#                   phục vụ NO_PRIOR (đang chạy) : live 6.603 (86,8%) · liq CAGR 12,44%
#                   loại NO_PRIOR  (biến thể chặt): live 6.290 (82,7%) · liq CAGR 12,46%
#                 ⇒ chặt hơn đẩy thêm 313 ô (4,1pp phủ) về lại số quý RESTATE — tức đổi look-ahead
#                 lấy look-ahead — để mua 0,02pp CAGR, nằm trong nhiễu. Không có ca hại nào đo
#                 được ở nhánh này: FPT 2017-07-03 (AIS đầu tiên, 530.961.105) đối chiếu ĐÚNG với
#                 dòng quý 2017-08-01 (530.878.729, lệch 0,015%).
#                 Đây là điểm PHÁN ĐOÁN duy nhất còn lại của cổng; đổi chính sách = sửa 1 dòng này.
#   "UNVERIFIED"— mọi trường hợp còn lại (dựng được kỳ vọng nhưng lệch, HOẶC không dựng nổi kỳ
#                 vọng nào). KHÔNG phục vụ.
_SERVE_AIS_VERDICTS = ("OK", "NO_PRIOR")


def _ais_verdicts(corp, ticker, asof):
    """{effective_date: "OK" | "NO_PRIOR" | "UNVERIFIED"} cho MỌI AIS của mã, tại `asof`.

    ⚠️ DỜI VÀO ĐÂY 2026-08-13 (vòng 4, job Taylor_20260813_154112). Trước đó hàm này sống ở
    `oshares_pit`, tức cổng chỉ chặn được người đi qua lớp bọc; `oshares_at()` gọi thẳng vẫn trả
    3.000.000.000 cho IDC và 461.723.054 cho FPT. Không đổi một luật nào khi dời — chỉ đổi CHỖ,
    và `oshares_pit` nay import lại hàm này thay vì giữ bản thứ hai.

    ⚠️ ĐỔI NGHĨA 2026-08-13 (quant-skeptic REFUTED bản trước, job Taylor_20260813_142812).
    Bản trước là `_suspect_ais` — một bộ **BẮT LỖI**: trả về tập AIS *chứng minh được là sai*, và
    mọi dòng còn lại được phục vụ ở nhãn tin cậy cao nhất `AIS_EXACT`. Đó là thế giới MỞ: "chưa
    bắt được" bị đọc thành "đã kiểm". Hàm này là bộ **CHỨNG NHẬN**: nó chỉ nói dòng nào đối chiếu
    ĐƯỢC và KHỚP; chỉ những dòng đó được phục vụ (`_SERVE_AIS_VERDICTS`).

    Vì sao phải đổi, chứ không phải vá thêm một luật: quant-skeptic chỉ ra tập cờ cũ không phải
    "lỗi vendor" mà là "transition NẰM CẠNH một bất thường" — IDC 2022-09-05 (dòng ĐÚNG) bị gắn cờ
    chỉ vì đứng sau dòng 3 tỷ hỏng, trong khi FPT 2020-04-06 (dòng SAI) lọt lưới. Một bộ bắt lỗi
    không thể sửa được bằng cách bắt giỏi hơn; phải thôi tuyên bố "đây là lỗi" và chỉ tuyên bố
    "đây là dòng tôi kiểm được".

    Bất biến kiểm được, chỉ dùng dữ liệu của riêng feed corp-action (không mượn số quý). Có HAI
    cách hợp lệ để tới `shares_total_after[i]`, và một dòng đúng chỉ cần khớp MỘT trong hai:

        (a) roll(shares_total_after[i-1], ISS ở giữa)     — sự kiện ISS đã cộng phần tăng rồi,
                                                             AIS chỉ là lần đăng ký niêm yết của
                                                             CHÍNH số CP đó
        (b) shares_total_after[i-1] + shares_delta[i]      — không có bản ghi ISS nào tương ứng,
                                                             `shares_delta` là nguồn duy nhất

    ⚠️ Cộng cả hai (`roll(...) + delta`) là ĐẾM HAI LẦN và đó là lỗi bản đầu của hàm này: nó gắn
    cờ 12/12 AIS của FPT, kể cả 2025-09-12 = 1.703.507.121 mà `_selfcheck` bên dưới đã chứng minh
    là ĐÚNG. Dùng lại `_roll` nên phần lăn sự kiện là CÙNG một hàm với phần tính số, không phải
    bản chép tay thứ hai.

    Chỉ xét AIS có `effective_date <= asof`: quyết định LOẠI cũng phải point-in-time, nếu không
    một AIS năm 2026 lại đang bác một câu trả lời của năm 2019.

    ⚠️ MỘT ISS CHẮN ĐƯỜNG CHỈ GIẾT ỨNG VIÊN (a), KHÔNG GIẾT (b). Đây chính là lỗ hổng đã bị bác:
    bản trước `continue` ngay khi `_roll` trả blocker, vứt bỏ luôn ứng viên (b) — dù (b) =
    `prev + shares_delta` không cần lăn qua ISS nào cả. Quét toàn bảng 2026-08-13: **213/2.505
    transition (129 mã)** có đúng hình dạng "blocker chắn đường NHƯNG (b) dựng được và MÂU THUẪN"
    — tức 213 dòng vendor sai đang được phục vụ ở nhãn `AIS_EXACT` mà không ai kiểm. Ca FPT
    2020-05-05 (461.723.054 thay vì 681.668.102, −32,3%) là một trong số đó. Thêm 7 ca
    (6 mã) không dựng được ứng viên NÀO ⇒ nay là "UNVERIFIED", trước là phục vụ im lặng.

    Chi phí của chiều ngược lại đã cân nhắc và CHẤP NHẬN: khi có ISS thật xen giữa, (b) thiếu
    phần cổ phiếu do ISS sinh ra nên có thể báo UNVERIFIED oan. Hậu quả của báo oan là **rơi về
    đúng số caller đang dùng hôm nay** — không mất gì; hậu quả của bỏ lọt là thay một số đúng
    bằng một số sai −32%. Hai chiều KHÔNG đối xứng, nên cổng cố ý lệch về phía báo oan.

    HAI CA THẬT nó bắt được, cả hai đã kiểm tay bằng ba nguồn độc lập:
      IDC 2020-05-28  delta 108.000.000, total_after 3.000.000.000, AIS trước 300.000.000
                      ⇒ kỳ vọng 408.000.000, lệch ~7,4×. (8 quý sau đó vẫn 300tr; AIS kế 329.999.929.)
      AAA 2019-06-03  delta 1.700.000, total_after 58.664.988, AIS trước 171.199.976
                      ⇒ kỳ vọng 172.899.976. Ca này LỌT qua cổng biên độ thô ×3 của `oshares_pit`
                      (58,66/171,20 = 0,343, hụt biên 1/3 = 0,333) — đó là lý do phải có cổng theo
                      bất biến, không chỉ cổng theo biên độ.
    """
    rows = sorted((c for c in corp
                   if c["ticker"] == ticker and c["event_code"] == "AIS"
                   and c["effective_date"] and c["effective_date"] <= asof
                   and c["shares_total_after"]),
                  key=lambda r: r["effective_date"])
    iss = [c for c in corp if c["ticker"] == ticker and c["event_code"] == "ISS"
           and c["exright_date"] and c["exright_date"] <= asof]
    verdicts = {}
    if rows:
        verdicts[rows[0]["effective_date"]] = "NO_PRIOR"
    for prev, cur in zip(rows, rows[1:]):
        if cur["effective_date"] == prev["effective_date"]:
            continue                                        # cùng ngày: không suy ra thứ tự được
        base_prev = float(prev["shares_total_after"])
        actual = float(cur["shares_total_after"])
        cands = []
        # deliberately the RAW ex-date window, not `_unabsorbed_iss`: this function is what
        # ESTABLISHES which ISS an AIS delta accounts for, so keying it on the output of that
        # same matching would be circular. Candidate (a) simply overshoots when a lock-up issue
        # falls in the window — and (b) still stands, which is why the transition is not lost.
        between = _dedup_iss([e for e in iss
                              if prev["effective_date"] < e["exright_date"]
                              <= cur["effective_date"]])
        rolled, _applied, blockers = _roll(base_prev, between)
        if not blockers:
            cands.append(rolled)                             # (a) — chỉ khi lăn được HẾT ISS
        delta = cur.get("shares_delta")
        if delta is not None and float(delta) > 0:
            cands.append(base_prev + float(delta))           # (b) — không phụ thuộc ISS
        # `cands` RỖNG (blocker chắn (a) VÀ không có delta cho (b)) ⇒ không dựng được kỳ vọng nào
        # ⇒ UNVERIFIED. Đây là chỗ `all([]) == True` từng làm nghĩa của hàm đảo ngược nếu viết
        # gọn, nên điều kiện được viết TƯỜNG MINH.
        ok = bool(cands) and any(e > 0 and abs(actual - e) / e <= EXPLAIN_TOL for e in cands)
        verdicts[cur["effective_date"]] = "OK" if ok else "UNVERIFIED"
    return verdicts


def _ais_certified(corp, ticker, asof, anchor_date):
    """Neo AIS `anchor_date` có được chứng nhận không? FAIL-CLOSED.

    Verdict lạ, thiếu ngày trong bảng, hay bản thân `_ais_verdicts` ném lỗi ⇒ CHƯA chứng nhận.
    Đây là cùng một kỷ luật "không kiểm được thì KHÔNG cho qua" mà quant-skeptic đã bác một bản
    trước vì làm ngược (`oshares_pit._anchor_unverified` cũ trả "được phục vụ" ở cả ba nhánh đó).
    """
    try:
        return _ais_verdicts(corp, ticker, asof).get(anchor_date) in _SERVE_AIS_VERDICTS
    except Exception:                                       # noqa: BLE001 — fail-closed by design
        return False


def oshares_at(tickers, asof, _cache=None):
    """{ticker: dict} — shares outstanding at `asof`, with the derivation shown.

    Each value carries `value`, `method`, `anchor_date`, `anchor_value`, `anchor_source` and the
    list of ISS events applied, so any number can be re-derived by hand from the output alone.
    `value is None` whenever the method is `UNKNOWN_RATIO`, `NO_ANCHOR` or `AIS_UNCERTIFIED` —
    callers MUST handle that; there is no "best effort" number behind it.
    """
    if isinstance(tickers, str):
        tickers = [tickers]
    quarters, corp = _cache if _cache else _fetch(tickers, asof)

    out = {}
    for tk in tickers:
        qs = [q for q in quarters if q["ticker"] == tk and q["time"] <= asof]
        ais = [c for c in corp if c["ticker"] == tk and c["event_code"] == "AIS"
               and c["effective_date"] and c["effective_date"] <= asof
               and c["shares_total_after"]]
        iss = [c for c in corp if c["ticker"] == tk and c["event_code"] == "ISS"
               and c["exright_date"] and c["exright_date"] <= asof and dilutes_share_count(c)]

        anchors, rejected, unverified = [], [], False
        fin_fallback = None
        a = max(ais, key=lambda r: r["effective_date"]) if ais else None
        q = max(qs, key=lambda r: r["time"]) if qs else None
        ais_age_days = _days_between(a["effective_date"], asof) if a else None

        if a:
            anchors.append((a["effective_date"], float(a["shares_total_after"]),
                            "corporate_action.AIS"))
        if q:
            ok, verified, why, expected = _explain_quarterly(q, ais, iss)
            if ok:
                anchors.append((q["time"], float(q["OShares"]), "ticker_financial"))
                unverified = not verified
            else:
                # STALE-AIS FALLBACK (2026-08-19, user policy). The gate has just refused the
                # quarterly row. That refusal is right when the row was restated ahead of an AIS
                # not yet ingested — and WRONG when the count genuinely moved through something
                # the feed carries no event for. `_stale_fallback_verdict` is the only place that
                # distinguishes them; nothing here decides on its own.
                # certification is read HERE, not only at the gate below: once a quarterly
                # anchor wins, `anchor_src` is no longer AIS and that gate never runs.
                a_ok = bool(a) and _ais_certified(corp, tk, asof, a["effective_date"])
                allow, fb_why = _stale_fallback_verdict(q, a, ais_age_days, a_ok)
                if allow:
                    anchors.append((q["time"], float(q["OShares"]), "ticker_financial"))
                    unverified = True          # served, but the gate never cleared it
                    fin_fallback = {"fin_fallback": True, "fin_quarter": q["time"],
                                    "fin_value": float(q["OShares"]),
                                    "ais_anchor_date": a["effective_date"] if a else None,
                                    "ais_age_days": ais_age_days,
                                    "fin_expected_from_ais": expected,
                                    "fin_explain_note": why, "fin_fallback_reason": fb_why}
                else:
                    rejected.append({"source": "ticker_financial", "date": q["time"],
                                     "value": float(q["OShares"]), "reason": why,
                                     "fallback_refused": fb_why})

        if not anchors:
            out[tk] = {"ticker": tk, "asof": asof, "value": None, "method": "NO_ANCHOR",
                       "anchor_date": None, "anchor_value": None, "anchor_source": None,
                       "events_applied": [], "rejected_anchors": rejected,
                       "note": "không có AIS nào <= ngày cần tính, và số quý (nếu có) không "
                               "kiểm chứng được"}
            continue

        # freshest ADMISSIBLE fact wins; AIS breaks a same-date tie (it is a registry statement
        # about the listed count, not a figure copied into a financial statement)
        anchor_date, anchor_value, anchor_src = max(
            anchors, key=lambda a: (a[0], a[2] == "corporate_action.AIS"))

        pending = _pending_iss(ais, iss, anchor_date, anchor_src, asof)
        value, applied, blockers = _roll(anchor_value, pending)

        anchor_verified = not (unverified and anchor_src == "ticker_financial")
        base = {"ticker": tk, "asof": asof, "anchor_date": anchor_date,
                "anchor_value": anchor_value, "anchor_source": anchor_src,
                "anchor_verified": anchor_verified, "rejected_anchors": rejected}
        # provenance only counts when the fallback anchor actually WON the max() above; a
        # fallback candidate that lost to a newer AIS must not stamp its keys on someone else's
        # answer.
        fin_served = fin_fallback is not None and anchor_src == "ticker_financial" \
            and anchor_date == fin_fallback["fin_quarter"]
        if fin_served:
            base.update(fin_fallback)

        if blockers:
            out[tk] = {**base, "value": None, "method": "UNKNOWN_RATIO",
                       "blocking_events": [_event_dict(b) for b in blockers],
                       "events_applied": [_event_dict(e, h, s) for e, h, s in applied],
                       "note": f"{len(blockers)} sự kiện ISS sau anchor không có exercise_ratio "
                               f"lẫn shares_delta ⇒ KHÔNG trả số (fail-closed)"}
            continue

        # only the ratio branch makes an answer an ESTIMATE. `shares_delta` and `issue_volumn`
        # are exact registry share COUNTS (issue_volumn reproduces AIS.shares_delta exactly on
        # 96,9% of 3.642 matched groups — see `_roll`), so rolling through them keeps the
        # anchor's own label.
        iss_estimate = bool(applied) and any(h == "exercise_ratio" for _e, h, _s in applied)
        if fin_served:
            # ONE label for the whole branch: what a consumer must know first is that the number
            # came from the quarterly column, not from the registry. Whether an ISS was rolled on
            # top is a separate fact and is reported separately (`iss_estimate` + `events_applied`)
            # rather than by mangling it into the method string.
            method = "FIN_FALLBACK"
            base["iss_estimate"] = iss_estimate
        elif iss_estimate:
            method = "ISS_ESTIMATE"
        elif anchor_src == "corporate_action.AIS":
            method = "AIS_EXACT"           # applied deltas, if any, are exact registry counts
        else:
            method = "ANCHOR_ONLY" if anchor_verified else "ANCHOR_UNVERIFIED"

        # ── CỔNG CHỨNG NHẬN NEO AIS ─────────────────────────────────────────────────────────
        # Neo dòng quý đã có cổng riêng (`_explain_quarterly`) ngay lúc nhận; neo AIS trước vòng 4
        # KHÔNG có cổng nào — nhãn tin cậy cao nhất lại là nhánh duy nhất không ai kiểm.
        # Đặt SAU khi tính xong, không phải lúc chọn neo, và đó là CỐ Ý:
        #   * nhánh `blockers` ở trên đã từ chối trả lời rồi ⇒ giữ nguyên nhãn UNKNOWN_RATIO (lý
        #     do ĐẦU TIÊN chặn mới là lý do đúng để báo);
        #   * KHÔNG tụt xuống một neo cũ hơn hay sang neo dòng quý khi neo AIS trượt cổng. Làm thế
        #     là ĐỔI SỐ, không còn là dời cổng — và số thay thế đó chưa ai đo. Ở đây từ chối trả
        #     lời; consumer rơi về đúng số nó đang dùng hôm nay (`oshares_pit`).
        if anchor_src == "corporate_action.AIS" \
                and not _ais_certified(corp, tk, asof, anchor_date):
            out[tk] = {**base, "value": None, "method": "AIS_UNCERTIFIED",
                       "uncertified_value": value, "uncertified_method": method,
                       "events_applied": [_event_dict(e, h, s) for e, h, s in applied],
                       "note": f"neo AIS {anchor_date} ({anchor_value:,.0f}) không đối chiếu được "
                               f"với AIS liền trước ⇒ KHÔNG phục vụ {value:,.0f} (fail-closed); "
                               f"số bị từ chối giữ ở `uncertified_value` để ghi log"}
            continue

        out[tk] = {**base, "value": value, "method": method,
                   "events_applied": [_event_dict(e, h, s) for e, h, s in applied]}
    return out


def _selfcheck() -> int:
    fails, ran = [], []

    # counted, never typed: the previous version's summary line said "11/11" while the file
    # actually ran 12 checks. A hand-written total is a number nobody re-derives.
    def check(name, cond, detail=""):
        ran.append(name)
        print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f" — {detail}" if detail else ""))
        if not cond:
            fails.append(name)

    def fmt(v):
        return f"{v:,.0f}" if v is not None else "None"

    print("== FPT 2025: thưởng CP 15% ex 2025-07-21 → AIS hiệu lực 2025-09-12 ==")
    AIS_TRUTH = 1_703_507_121
    PRE = 1_481_330_122          # AIS 2025-06-19, ground truth trước sự kiện

    cache = _fetch(["FPT"], "2026-08-13")
    series = {}
    for d in ["2025-07-18", "2025-07-20", "2025-07-21", "2025-07-22",
              "2025-08-15", "2025-09-11", "2025-09-12", "2025-10-01"]:
        r = oshares_at(["FPT"], d, _cache=cache)["FPT"]
        series[d] = r
        print(f"  {d}: {fmt(r['value']):>15}  [{r['method']:13s}] anchor={r['anchor_date']}"
              f" ({r['anchor_source']}) +{len(r.get('events_applied', []))} ISS")

    check("1. trước ex-right: bằng ĐÚNG AIS 2025-06-19 (1.481.330.122)",
          series["2025-07-20"]["value"] == PRE, fmt(series['2025-07-20']['value']))
    check("2. ĐÚNG ngày ex-right 07-21: nhảy lên ~1,7 tỷ (không chờ 7 tuần tới AIS)",
          series["2025-07-21"]["value"] is not None
          and abs(series["2025-07-21"]["value"] - AIS_TRUTH) / AIS_TRUTH < 0.001
          and series["2025-07-21"]["method"] in ("AIS_EXACT", "ISS_ESTIMATE"),
          f"{fmt(series['2025-07-21']['value'])} [{series['2025-07-21']['method']}] — lệch "
          f"{abs(series['2025-07-21']['value']-AIS_TRUTH)/AIS_TRUTH*100:.4f}%")
    # The series is non-decreasing EXCEPT at the one step where an ISS_ESTIMATE is superseded by
    # a hard number (1.703.529.640 -> 1.703.507.121). That -22.519 is the estimate converging onto
    # truth, not shares disappearing, so the honest assertion is "no MATERIAL decrease, and any
    # decrease must be an estimate giving way to a measured anchor".
    drops = [(a, b) for a, b in zip(list(series)[:-1], list(series)[1:])
             if series[b]["value"] is not None and series[a]["value"] is not None
             and series[b]["value"] < series[a]["value"] - 1e-6]
    check("3. chuỗi không giảm ĐÁNG KỂ; mọi bước giảm đều là ước lượng nhường chỗ cho số đo",
          all(series[a]["method"] == "ISS_ESTIMATE"
              and series[b]["method"] in ("AIS_EXACT", "ANCHOR_ONLY")
              and abs(series[b]["value"] - series[a]["value"]) / series[a]["value"] < 0.0001
              for a, b in drops),
          f"{len(drops)} bước giảm: " + (", ".join(
              f"{a}→{b} ({(series[b]['value']/series[a]['value']-1)*100:+.4f}%)" for a, b in drops)
              or "không có"))
    check("3b. đầu chuỗi < cuối chuỗi (thực sự đã tăng qua sự kiện)",
          series["2025-07-18"]["value"] < series["2025-10-01"]["value"],
          f"{fmt(series['2025-07-18']['value'])} → {fmt(series['2025-10-01']['value'])}")
    check("4. sau AIS hiệu lực: KHỚP TUYỆT ĐỐI shares_total_after = 1.703.507.121",
          series["2025-09-12"]["value"] == AIS_TRUTH and series["2025-10-01"]["value"] == AIS_TRUTH,
          fmt(series['2025-09-12']['value']))
    check("5. không đếm hai lần: sau AIS không nhân lại ISS đã nằm trong AIS",
          series["2025-10-01"]["events_applied"] == [])
    # the quarterly row dated 07-22 carries the post-bonus count ONE DAY after ex-right. That is
    # genuine early data (the 15% bonus explains it exactly), so the restatement gate must LET IT
    # THROUGH — a gate that rejected everything would pass the HAH test for the wrong reason.
    q722 = oshares_at(["FPT"], "2025-07-22", _cache=cache)["FPT"]
    check("5b. cổng RESTATE không chặn nhầm số quý CÓ căn cứ (FPT 07-22, thưởng 07-21 giải thích)",
          not q722["rejected_anchors"],
          f"rejected={q722['rejected_anchors']}")

    print("== Kiểm chứng ESOP (loại KHÔNG điều chỉnh giá nhưng VẪN tăng số CP) ==")
    r = oshares_at(["FPT"], "2025-06-18", _cache=cache)["FPT"]
    print(f"  2025-06-18 (trước AIS 06-19): {fmt(r['value']):>15} [{r['method']}] "
          f"+{len(r.get('events_applied', []))} ISS")
    check("6. lăn qua 2 đợt ESOP 2025-05-07 ⇒ khớp AIS 06-19 trong 0,01%",
          r["value"] is not None and abs(r["value"] - PRE) / PRE < 0.0001
          and len(r["events_applied"]) == 2,
          f"{fmt(r['value'])} vs {PRE:,.0f}")
    check("7. hai đợt ESOP cùng ngày, KHÁC số lượng ⇒ giữ CẢ HAI (không dedup nhầm); "
          "applied_size là issue_volumn chính xác, không phải tỉ lệ xấp xỉ",
          sorted(e["applied_size"] for e in r["events_applied"]) == [3_315_000.0, 6_945_939.0])

    # ------------------------------------------------------------------ HỒI QUY: 2 lỗi đã đo
    print("== HỒI QUY VIỆC B — HAH: số quý RESTATE + ISS không có tỉ lệ ==")
    hcache = _fetch(["HAH"], "2026-08-19")

    # (1) look-ahead: the 2026-02-02 quarterly row already carries 185.840.401, a count created by
    # the 2026-03-12 conversion + 2026-04-17 ESOP and only listed by the AIS of 2026-05-27.
    h = oshares_at(["HAH"], "2026-03-01", _cache=hcache)["HAH"]
    print(f"  2026-03-01: {fmt(h['value'])} [{h['method']}] anchor={h['anchor_date']} "
          f"({h['anchor_source']}) rejected={len(h['rejected_anchors'])}")
    for rj in h["rejected_anchors"]:
        print(f"     ⛔ loại anchor {rj['source']} {rj['date']} = {rj['value']:,.0f}: {rj['reason']}")
    # ⚠️ CÁI GIÁ ĐÃ CHẤP NHẬN (2026-08-19, chỉ đạo user). Cổng CHIỀU đã bị gỡ khỏi
    # `_stale_fallback_verdict`, mà neo AIS 2025-09-09 của HAH tại 2026-03-01 đã cũ 173 ngày ⇒
    # fallback bắt được dòng quý và PHỤC VỤ đúng con số look-ahead mà H1 sinh ra để chặn.
    # Ba check dưới GIỮ NGUYÊN VỊ TRÍ và ĐẢO kỳ vọng: chúng là bằng chứng cái giá đang trả,
    # KHÔNG phải bằng chứng lỗi đã sửa. Muốn lấy lại: đặt lại điều kiện chiều trong hàm đó.
    check("H1. [CÁI GIÁ] 2026-03-01 NAY TRẢ 185.840.401 — số chỉ ra đời với AIS 2026-05-27 "
          "(sau ngày hỏi 87 ngày) — vì fallback không còn xét chiều tăng/giảm",
          h["value"] == 185_840_401 and h["method"] == "FIN_FALLBACK",
          f"{fmt(h['value'])} [{h['method']}]")
    check("H2. [CÁI GIÁ] số ĐÚNG point-in-time 168.861.212 KHÔNG bị mất dấu: nó vẫn là kỳ vọng "
          "lăn từ AIS và được ghi ra `fin_expected_from_ais`, `anchor_verified`=False",
          h.get("fin_expected_from_ais") == 168_861_212.0 and h["anchor_verified"] is False,
          f"expected={fmt(h.get('fin_expected_from_ais'))} verified={h['anchor_verified']}")
    check("H3. lý do cổng giải thích LOẠI dòng quý vẫn được nêu ra, không im lặng — chỉ chuyển "
          "từ `rejected_anchors` sang `fin_explain_note` vì dòng quý nay được phục vụ",
          "không giải thích được" in (h.get("fin_explain_note") or ""),
          (h.get("fin_explain_note") or "(trống)")[:90])

    # (2) convertible-bond conversions: exercise_ratio = 0.0, no shares_delta.
    # Old code: multiplied by 1.0 → UNKNOWN_RATIO, value=None (fail-closed, correct at the time).
    # New code: issue_volumn is populated → applied exactly → correct value.
    #   2025-03-20 TRANS: issue_volumn=8.551.327 → AIS 2025-05-28 confirms 129.894.418 ✓
    #   2026-03-12 TRANS: issue_volumn=16.979.189 → AIS 2026-05-27 confirms 185.840.401 ✓
    hh1 = oshares_at(["HAH"], "2025-03-25", _cache=hcache)["HAH"]
    print(f"  2025-03-25: {fmt(hh1['value'])} [{hh1['method']}] anchor={hh1['anchor_date']}")
    check("H4/2025-03-25. chuyển đổi TP 2025-03-20 (issue_volumn=8.551.327) ⇒ value=129.894.418 "
          "(AIS 2025-05-28 xác nhận); method AIS_EXACT hoặc ANCHOR_ONLY tuỳ anchor nào thắng",
          hh1["value"] == 129_894_418
          and hh1["method"] in ("AIS_EXACT", "ANCHOR_ONLY"),
          f"value={fmt(hh1['value'])} method={hh1['method']}")
    hh2 = oshares_at(["HAH"], "2026-03-13", _cache=hcache)["HAH"]
    print(f"  2026-03-13: {fmt(hh2['value'])} [{hh2['method']}] anchor={hh2['anchor_date']}")
    check("H4/2026-03-13. chuyển đổi TP 2026-03-12 (issue_volumn=16.979.189) ⇒ FIN_FALLBACK "
          "202.819.590 (neo Q4/2025 185.840.401 + TRANS 16.979.189)",
          hh2["value"] == 202_819_590 and hh2["method"] == "FIN_FALLBACK",
          f"value={fmt(hh2['value'])} method={hh2['method']}")

    # (3) NEW: ESOP tranches — no GDKHQ, no price adjustment, but shares are real and dilutive.
    # HAH issued 2 ESOP tranches after AIS 2026-05-27 (185.840.401):
    #   ESOP1: exright 2026-04-17, issue_volumn=2.500.000, listing_date=2028-?? (far future)
    #   ESOP2: exright 2026-07-28, issue_volumn=3.500.000, listing_date=2028-?? (far future)
    # _unabsorbed_iss correctly finds both as unabsorbed from AIS 2026-05-27:
    #   delta 2026-05-27 = 16.979.189 (bond conv only) → ESOP1 not in delta → unabsorbed
    #   ESOP2 exright > last AIS → in "after"
    print("== HAH ESOP: _unabsorbed_iss tìm CP ESOP chưa niêm yết (mục tiêu ban đầu) ==")
    h5 = oshares_at(["HAH"], "2026-08-19", _cache=hcache)["HAH"]
    print(f"  HAH 2026-08-19: {fmt(h5['value'])} [{h5['method']}] anchor={h5['anchor_date']} "
          f"+{len(h5.get('events_applied', []))} ISS")
    for ev in h5.get("events_applied", []):
        print(f"    ISS {ev['exright_date']} +{fmt(ev.get('applied_size'))}")
    check("H5. HAH 2026-08-19 = 191.840.401 "
          "(AIS 185.840.401 + ESOP1 2.500.000 + ESOP2 3.500.000)",
          h5["value"] == 191_840_401,
          f"{fmt(h5['value'])} [{h5['method']}]")
    h5b = oshares_at(["HAH"], "2026-05-28", _cache=hcache)["HAH"]
    print(f"  HAH 2026-05-28 (sau AIS 2026-05-27, trước ESOP2 2026-07-28): "
          f"{fmt(h5b['value'])} [{h5b['method']}] +{len(h5b.get('events_applied', []))} ISS")
    check("H5b. HAH 2026-05-28 = 188.340.401 (ESOP1 đã tính, ESOP2 chưa exright)",
          h5b["value"] == 188_340_401,
          f"{fmt(h5b['value'])} [{h5b['method']}]")

    print("== HỒI QUY VIỆC B — 'Phát hành riêng lẻ' (2.187/2.280 dòng ratio 0/NULL) ==")
    pp = bq(f"""
        SELECT ticker, CAST(exright_date AS STRING) exright_date
        FROM `{TABLE}`
        WHERE event_code = "ISS" AND event_status = "executed"
          AND issue_method_name_vi = "Phát hành riêng lẻ"
          AND (exercise_ratio IS NULL OR exercise_ratio = 0) AND shares_delta IS NULL
          AND exright_date BETWEEN DATE "2025-01-01" AND DATE "2026-06-30"
        ORDER BY exright_date DESC LIMIT 1
    """)
    check("P0. tìm được ít nhất 1 ca 'Phát hành riêng lẻ' thật để kiểm (test không rỗng)",
          bool(pp), str(pp))
    if pp:
        tkp, exrp = pp[0]["ticker"], pp[0]["exright_date"]
        after = (__import__("datetime").date.fromisoformat(exrp)
                 + __import__("datetime").timedelta(days=1)).isoformat()
        p = oshares_at([tkp], after)[tkp]
        print(f"  {tkp} {after}: {fmt(p['value'])} [{p['method']}] "
              f"blocking={[b['exright_date'] for b in p.get('blocking_events', [])]}")
        check(f"P1. {tkp} ngay sau phát hành riêng lẻ {exrp} ⇒ UNKNOWN_RATIO, value=None",
              p["value"] is None and p["method"] == "UNKNOWN_RATIO"
              and any(b["exright_date"] == exrp for b in p["blocking_events"]),
              f"value={fmt(p['value'])} method={p['method']}")

    print("== Ca đối chứng: không có sự kiện sau anchor ⇒ KHÔNG được đụng vào số anchor ==")
    ctrl = oshares_at(["DHG", "PVT", "TCB", "ACB", "HDB"], "2026-08-12")
    for tk, r in sorted(ctrl.items()):
        print(f"  {tk}: {fmt(r['value']):>15} [{r['method']:17s}] anchor={r['anchor_date']}"
              f" ({r['anchor_source']}) +{len(r.get('events_applied', []))} ISS")
    # coverage must not be bought with a false label: DHG has no AIS at all, so its quarterly
    # anchor cannot be cleared — it is returned, and it says so.
    check("8d. mã không có AIS nào ⇒ vẫn trả số nhưng gắn nhãn ANCHOR_UNVERIFIED",
          ctrl["DHG"]["value"] is not None and ctrl["DHG"]["method"] == "ANCHOR_UNVERIFIED"
          and ctrl["DHG"]["anchor_verified"] is False,
          f"{fmt(ctrl['DHG']['value'])} [{ctrl['DHG']['method']}]")
    # property, not an assumption about which tickers happen to be event-free — the earlier
    # version hardcoded "PVT has no events", which was simply false and masked a real bug
    check("8. mọi mã không có ISS sau anchor ⇒ value == anchor_value TUYỆT ĐỐI",
          all(r["value"] == r["anchor_value"]
              for r in ctrl.values() if r["value"] is not None and not r["events_applied"]))
    check("8b. có ít nhất 1 mã đối chứng thật sự không sự kiện (test không rỗng)",
          any(r.get("events_applied") == [] and r["value"] is not None for r in ctrl.values()),
          f"{[t for t, r in ctrl.items() if r.get('events_applied') == []]}")
    # regression: the bq CLI truncates at 100 rows by default; batching several tickers used to
    # silently drop the newest quarters and fall back to a year-old anchor (fixed in
    # corp_action_lib.bq via --max_rows). Batched must equal one-at-a-time, always.
    solo = {t: oshares_at([t], "2026-08-12")[t] for t in ctrl}
    check("8c. gọi theo LÔ == gọi từng mã (không bị bq cắt 100 dòng)",
          all(ctrl[t]["value"] == solo[t]["value"]
              and ctrl[t].get("anchor_date") == solo[t].get("anchor_date") for t in ctrl),
          "; ".join(f"{t}: lô {ctrl[t].get('anchor_date')} vs đơn {solo[t].get('anchor_date')}"
                    for t in ctrl if ctrl[t].get("anchor_date") != solo[t].get("anchor_date"))
          or "khớp hết")

    print("== MBB: 2 đợt CÙNG NGÀY 2026-08-11 (quyền mua 10% + cổ tức CP 15%) ==")
    m = oshares_at(["MBB"], "2026-08-12")["MBB"]
    print(f"  {fmt(m['value'])} [{m['method']}] anchor={m['anchor_date']} "
          f"({m['anchor_source']}) events="
          f"{[(e['exright_date'], e.get('applied_size')) for e in m.get('events_applied', [])]}")
    check("9. cộng CẢ HAI đợt cùng ngày (quyền mua 10% + cổ tức CP 15%), "
          "applied_size = số cổ phần chính xác từ issue_volumn",
          sorted(e["applied_size"] for e in m.get("events_applied", [])
                 if e["exright_date"] == "2026-08-11") == [805_499_990.0, 1_208_249_986.0])

    # ── VÒNG 4: cổng chứng nhận neo AIS nay nằm TRONG module này ────────────────────────────
    # Trước vòng 4 cổng chỉ có ở `oshares_pit`, nên đúng hai lệnh dưới đây trả về số sai. Đây là
    # lý do tồn tại của cả vòng này: gọi thẳng phải an toàn, không chỉ gọi qua lớp bọc.
    print("== VÒNG 4: gọi THẲNG oshares_at cũng không được trả neo AIS chưa chứng nhận ==")
    idc = oshares_at(["IDC"], "2021-02-05")["IDC"]
    print(f"  IDC 2021-02-05: {fmt(idc['value'])} [{idc['method']}] "
          f"bị từ chối={fmt(idc.get('uncertified_value'))}")
    check("N1. IDC 2021-02-05 KHÔNG còn trả 3.000.000.000 khi gọi thẳng",
          idc["value"] is None and idc["method"] == "AIS_UNCERTIFIED",
          f"value={fmt(idc['value'])} method={idc['method']}")
    check("N1b. …và số bị từ chối ĐÚNG là 3.000.000.000, giữ lại để ghi log chứ không phục vụ",
          idc["uncertified_value"] == 3_000_000_000.0, fmt(idc.get("uncertified_value")))
    fpt5 = oshares_at(["FPT"], "2020-05-05")["FPT"]
    check("N2. FPT 2020-05-05 KHÔNG còn trả 461.723.054 khi gọi thẳng (ca REFUTED vòng 2)",
          fpt5["value"] is None and fpt5["method"] == "AIS_UNCERTIFIED"
          and fpt5["uncertified_value"] == 461_723_054.0,
          f"value={fmt(fpt5['value'])} bị từ chối={fmt(fpt5.get('uncertified_value'))}")
    # CHỨNG MINH NGƯỢC — nếu không có ca test này thì N1/N2 có thể PASS chỉ vì mã đó rỗng dữ liệu.
    # Sửa `globals()` chứ không `import oshares_live`: chạy bằng `python oshares_live.py` thì
    # module này là `__main__`, một lệnh import sẽ nạp BẢN THỨ HAI và vá nhầm chỗ.
    # Phải mở CẢ HAI cổng thì hai số sai mới quay lại được. Từ 2026-08-19 cổng chứng nhận không
    # còn là thứ duy nhất chặn IDC: fallback FIN_FALLBACK cũng chặn (xem N3b). Mở mỗi cổng chứng
    # nhận rồi kết luận "cổng không chặn" là đọc nhầm một lớp phòng thủ thứ hai thành thất bại.
    _keep_serve = _SERVE_AIS_VERDICTS
    _keep_age = FIN_FALLBACK_MAX_AIS_AGE_DAYS
    globals()["_SERVE_AIS_VERDICTS"] = ("OK", "NO_PRIOR", "UNVERIFIED")
    try:
        idc_half = oshares_at(["IDC"], "2021-02-05")["IDC"]     # chỉ mở cổng chứng nhận
        globals()["FIN_FALLBACK_MAX_AIS_AGE_DAYS"] = 10 ** 9    # …rồi tắt luôn fallback
        idc_no = oshares_at(["IDC"], "2021-02-05")["IDC"]
        fpt_no = oshares_at(["FPT"], "2020-05-05")["FPT"]
    finally:
        globals()["_SERVE_AIS_VERDICTS"] = _keep_serve
        globals()["FIN_FALLBACK_MAX_AIS_AGE_DAYS"] = _keep_age
    check("N3. CHỨNG MINH NGƯỢC: mở CẢ HAI cổng ⇒ CẢ HAI số sai THẬT SỰ quay lại (đang chặn thật)",
          idc_no["value"] == 3_000_000_000.0 and idc_no["method"] == "AIS_EXACT"
          and fpt_no["value"] == 461_723_054.0,
          f"IDC {fmt(idc_no['value'])} · FPT {fmt(fpt_no['value'])}")
    check("N3b. PHÒNG THỦ HAI LỚP: mở riêng cổng chứng nhận thì 3.000.000.000 VẪN không ra — "
          "fallback chặn độc lập (số quý 300.000.000 thấp hơn neo hỏng)",
          idc_half["value"] == 300_000_000.0 and idc_half["method"] == "FIN_FALLBACK",
          f"{fmt(idc_half['value'])} [{idc_half['method']}]")
    # FAIL-CLOSED: hàm chứng nhận hỏng ⇒ KHÔNG phục vụ (không phải "không kiểm được thì cho qua")
    _keep_v = _ais_verdicts

    def _boom_verdicts(*_a, **_k):
        raise RuntimeError("cổng chứng nhận sập giả lập")

    globals()["_ais_verdicts"] = _boom_verdicts
    try:
        tcb_boom = oshares_at(["TCB"], "2026-08-12")["TCB"]
    finally:
        globals()["_ais_verdicts"] = _keep_v
    check("N4. FAIL-CLOSED: `_ais_verdicts` NÉM LỖI ⇒ neo AIS coi như CHƯA chứng nhận",
          tcb_boom["value"] is None and tcb_boom["method"] == "AIS_UNCERTIFIED",
          f"{fmt(tcb_boom['value'])} [{tcb_boom['method']}]")
    # …và cổng không được nuốt sạch: mã sạch vẫn phải ra AIS_EXACT, nếu không N1/N2 chỉ chứng minh
    # "chặn tất cả", một cổng vô dụng cũng PASS được.
    check("N5. ĐỐI CHỨNG: TCB 2026-08-12 (neo AIS chứng nhận được) VẪN phục vụ AIS_EXACT",
          ctrl["TCB"]["value"] is not None and ctrl["TCB"]["method"] == "AIS_EXACT",
          f"{fmt(ctrl['TCB']['value'])} [{ctrl['TCB']['method']}]")
    check("N6. neo dòng quý KHÔNG bị cổng AIS đụng tới (đã có cổng RESTATE riêng)",
          all(ctrl[t]["value"] is not None
              and ctrl[t]["method"] in ("ANCHOR_ONLY", "ANCHOR_UNVERIFIED")
              for t in ("ACB", "DHG", "HDB", "PVT")),
          str({t: ctrl[t]["method"] for t in ("ACB", "DHG", "HDB", "PVT")}))
    # NO_PRIOR = AIS đầu tiên của mã: được phục vụ có chủ đích (xem `_SERVE_AIS_VERDICTS`)
    fcache = _fetch(["FPT"], "2026-08-13")
    check("N7. verdict NO_PRIOR (FPT 2017-07-03, AIS đầu tiên) ⇒ được phục vụ",
          _ais_verdicts(fcache[1], "FPT", "2017-08-01").get("2017-07-03") == "NO_PRIOR"
          and oshares_at(["FPT"], "2017-07-03", _cache=fcache)["FPT"]["value"] == 530_961_105,
          str(oshares_at(["FPT"], "2017-07-03", _cache=fcache)["FPT"]["method"]))
    # POINT-IN-TIME: một AIS của tương lai không được bác câu trả lời của quá khứ
    icache = _fetch(["IDC"], "2026-08-13")
    check("N8. PIT: xét tại 2020-01-01 thì AIS 2022-09-05 chưa tồn tại ⇒ không có verdict",
          "2022-09-05" not in _ais_verdicts(icache[1], "IDC", "2020-01-01"),
          str(sorted(_ais_verdicts(icache[1], "IDC", "2020-01-01"))))

    # ── FIN_FALLBACK: neo AIS CŨ quá một kỳ báo cáo ⇒ rơi về dòng quý ─────────────────────
    # Chính sách user chốt 2026-08-19. VRE là ca buộc phải có: AIS duy nhất 2018-12-26, đợt mua
    # cổ phiếu quỹ 2019 KHÔNG sinh dòng corp-action nào, và dòng quý mang số đúng từ 2019-10-29.
    print("== FIN_FALLBACK — VRE: AIS 2018 đứng im, mua CP quỹ 2019 không có sự kiện ==")
    vre = oshares_at(["VRE"], "2026-08-19")["VRE"]
    print(f"  VRE 2026-08-19: {fmt(vre['value'])} [{vre['method']}] anchor={vre['anchor_date']} "
          f"({vre['anchor_source']}) AIS {vre.get('ais_anchor_date')} cũ "
          f"{vre.get('ais_age_days')} ngày")
    check("F1. VRE 2026-08-19 ⇒ FIN_FALLBACK = 2.272.318.410 (số BCTC), KHÔNG phải AIS 2018",
          vre["value"] == 2_272_318_410.0 and vre["method"] == "FIN_FALLBACK",
          f"{fmt(vre['value'])} [{vre['method']}]")
    check("F1b. …và xuất xứ được ghi đủ để tra tay: quý neo, tuổi AIS, anchor_verified=False",
          vre.get("fin_quarter") == vre["anchor_date"] and vre.get("ais_age_days", 0) > 90
          and vre["anchor_verified"] is False and vre.get("fin_fallback") is True,
          f"quý={vre.get('fin_quarter')} tuổi AIS={vre.get('ais_age_days')} "
          f"verified={vre['anchor_verified']}")
    # CHỨNG MINH NGƯỢC — nếu không có ca này thì F1 có thể PASS vì bất kỳ lý do nào khác.
    _keep_age = FIN_FALLBACK_MAX_AIS_AGE_DAYS
    globals()["FIN_FALLBACK_MAX_AIS_AGE_DAYS"] = 10 ** 9
    try:
        vre_off = oshares_at(["VRE"], "2026-08-19")["VRE"]
    finally:
        globals()["FIN_FALLBACK_MAX_AIS_AGE_DAYS"] = _keep_age
    check("F1c. CHỨNG MINH NGƯỢC: tắt fallback ⇒ VRE quay lại ĐÚNG con số sai 2.328.818.410 "
          "(+2,49%) — fallback là thứ đang sửa, không phải trùng hợp",
          vre_off["value"] == 2_328_818_410.0,
          f"{fmt(vre_off['value'])} [{vre_off['method']}]")

    print("== FIN_FALLBACK — ba ca KHÔNG được đụng tới ==")
    # (a) AIS còn tươi: fallback không có cửa xen vào
    tcb_age = _days_between(ctrl["TCB"]["anchor_date"], "2026-08-12")
    check(f"F2. AIS còn tươi ({tcb_age} ngày <= {FIN_FALLBACK_MAX_AIS_AGE_DAYS}) ⇒ TCB vẫn "
          f"AIS_EXACT, nhãn KHÔNG đổi",
          tcb_age <= FIN_FALLBACK_MAX_AIS_AGE_DAYS
          and ctrl["TCB"]["method"] == "AIS_EXACT" and "fin_fallback" not in ctrl["TCB"],
          f"{ctrl['TCB']['method']} tuổi={tcb_age}")
    # (b) không có cả AIS lẫn dòng quý: NO_ANCHOR như cũ, không bịa số
    na = oshares_at(["FPT"], "2001-01-01")["FPT"]
    check("F3. không có AIS lẫn dòng quý ⇒ NO_ANCHOR, value=None (fallback không bịa số)",
          na["value"] is None and na["method"] == "NO_ANCHOR", f"{na['method']}")
    # (c) BA điều kiện còn lại phải thật sự chặn — thử THẲNG vào `_stale_fallback_verdict` với
    # dữ liệu dựng sẵn, không qua BQ: mỗi lần chỉ hỏng đúng MỘT điều kiện, nên một PASS ở đây
    # không thể do một điều kiện khác gánh hộ. Bản thân chữ ký hàm (4 tham số, không còn
    # `expected`) đã là bằng chứng cổng CHIỀU không còn tồn tại.
    _a = {"effective_date": "2024-01-01", "shares_total_after": 100_000_000}
    _q_new = {"time": "2026-07-31", "OShares": 999_999_999}     # CAO hơn AIS gấp 10 lần
    _q_old = {"time": "2023-06-30", "OShares": 90_000_000}
    _f4 = {
        "quý cũ hơn AIS ⇒ TỪ CHỐI": _stale_fallback_verdict(_q_old, _a, 900, True)[0] is False,
        "AIS còn tươi ⇒ TỪ CHỐI": _stale_fallback_verdict(_q_new, _a, 30, True)[0] is False,
        "AIS chưa chứng nhận ⇒ TỪ CHỐI": _stale_fallback_verdict(_q_new, _a, 900, False)[0] is False,
        "không có neo AIS ⇒ TỪ CHỐI": _stale_fallback_verdict(_q_new, None, 900, True)[0] is False,
        "đủ 3 điều kiện + quý CAO gấp 10 ⇒ CHO QUA (cổng chiều đã gỡ)":
            _stale_fallback_verdict(_q_new, _a, 900, True)[0] is True,
    }
    check("F4. ba điều kiện còn lại chặn đúng từng cái một, và chiều TĂNG không còn bị chặn",
          all(_f4.values()), str({k: v for k, v in _f4.items() if not v}) or "5/5")

    print("== FIN_FALLBACK — ca CC1: phát hành riêng lẻ, BCTC ghi trước ngày niêm yết bổ sung ==")
    # CC1: AIS cuối 2025-08-06 = 397.906.100; ISS 2026-06-17 = 76.750.000 CP riêng lẻ,
    # listing_date=2027-06-18 (chưa niêm yết). Q2/2026 (dòng quý 2026-07-31) ghi 474.656.100.
    # Với _unabsorbed_iss: ISS 2026-06-17 exright > AIS 2025-08-06 → nằm trong "after" →
    # _explain_quarterly tính expected = 397.906.100 + 76.750.000 = 474.656.100 = actual → OK,
    # verified=True → quarterly được nhận trực tiếp (ANCHOR_ONLY), không cần FIN_FALLBACK cứu.
    cc1 = oshares_at(["CC1"], "2026-08-19")["CC1"]
    print(f"  CC1 2026-08-19: {fmt(cc1['value'])} [{cc1['method']}] anchor={cc1.get('anchor_date')} "
          f"verified={cc1.get('anchor_verified')} +{len(cc1.get('events_applied', []))} ISS")
    check("F5. CC1 2026-08-19 = 474.656.100 — quarterly Q2/2026 xác nhận được bằng accounting "
          "(ISS 76.750.000 unabsorbed từ AIS, expected khớp ĐÚNG dòng quý)",
          cc1["value"] == 474_656_100.0 and cc1["method"] == "ANCHOR_ONLY"
          and cc1.get("anchor_verified") is True,
          f"{fmt(cc1['value'])} [{cc1['method']}] verified={cc1.get('anchor_verified')}")
    # CHỨNG MINH CƠ CHẾ: _explain_quarterly thành công vì _unabsorbed_iss tìm ra ISS 2026-06-17.
    # Quarterly đã được xác nhận bằng accounting nên không đi qua FIN_FALLBACK.
    # Khác với VRE (F1): VRE không có ISS nào → _explain_quarterly thất bại → FIN_FALLBACK cứu.
    check("F5b. CHỨNG MINH CƠ CHẾ: anchor_verified=True (accounting xác nhận), "
          "không phải FIN_FALLBACK rescue — fin_fallback field không có",
          cc1.get("anchor_verified") is True and cc1.get("fin_fallback") is not True
          and cc1["method"] == "ANCHOR_ONLY",
          f"verified={cc1.get('anchor_verified')} fin_fallback={cc1.get('fin_fallback')} "
          f"method={cc1['method']}")

    print("== CÁI GIÁ ĐO ĐƯỢC: 3 ca RESTATE nay được phục vụ (không còn cổng nào chặn) ==")
    # Đo 2026-08-19 trên 246 mã ticker_prune tại asof=2026-03-01 (có 5,5 tháng tương lai để đối
    # chiếu): 12 mã đổi số, 3 mã mang chữ ký RESTATE — giá trị phục vụ trùng KHÍT một AIS chỉ có
    # hiệu lực SAU đó. Ghim ở đây để một thay đổi sau này "sửa" được nó thì thấy ngay.
    cost = oshares_at(["ABB", "NVL"], "2026-03-01")
    for t in ("ABB", "NVL"):
        print(f"  {t} 2026-03-01: {fmt(cost[t]['value'])} [{cost[t]['method']}]")
    check("F6. [CÁI GIÁ] ABB 1.397.208.685 (AIS 2026-06-19) và NVL 2.234.496.474 (AIS "
          "2026-05-29) — cùng HAH ở H1 là 3/12 ca look-ahead đã đo, KHÔNG phải hành vi mong muốn",
          cost["ABB"]["value"] == 1_397_208_685.0 and cost["ABB"]["method"] == "FIN_FALLBACK"
          and cost["NVL"]["value"] == 2_234_496_474.0 and cost["NVL"]["method"] == "FIN_FALLBACK",
          f"ABB {fmt(cost['ABB']['value'])} [{cost['ABB']['method']}] · "
          f"NVL {fmt(cost['NVL']['value'])} [{cost['NVL']['method']}]")

    print("== Bất biến chung: value is None ⟺ method ∈ {UNKNOWN_RATIO, NO_ANCHOR, AIS_UNCERTIFIED} ==")
    every = [h, m, idc, fpt5, tcb_boom, vre, vre_off, na, cc1,
             h5, h5b, hh1, hh2,
             *cost.values(), *ctrl.values(), *series.values()]
    check("10. không bao giờ trả số kèm nhãn 'không biết', và ngược lại",
          all((r["value"] is None)
              == (r["method"] in ("UNKNOWN_RATIO", "NO_ANCHOR", "AIS_UNCERTIFIED"))
              for r in every))
    served_ais = [r for r in every
                  if r["value"] is not None and r.get("anchor_source") == "corporate_action.AIS"]
    _corp_memo = {}

    def _corp_of(tk):
        if tk not in _corp_memo:
            _corp_memo[tk] = _fetch([tk], "2026-08-13")[1]
        return _corp_memo[tk]

    check("10b. mọi câu trả lời neo AIS ĐƯỢC PHỤC VỤ đều có verdict trong _SERVE_AIS_VERDICTS "
          "(bất biến trên rổ, không chỉ trên 2 ca đã biết)",
          bool(served_ais) and all(
              _ais_certified(_corp_of(r["ticker"]), r["ticker"], r["asof"], r["anchor_date"])
              for r in served_ais),
          f"{len(served_ais)} ca neo AIS được phục vụ: "
          + str(sorted({f"{r['ticker']}@{r['anchor_date']}" for r in served_ais})))

    print()
    if fails:
        print(f"FAILED {len(fails)}/{len(ran)}: {fails}")
        return 1
    print(f"OK — oshares_live selfcheck PASS {len(ran)}/{len(ran)}")
    return 0


if __name__ == "__main__":
    import argparse
    import json

    ap = argparse.ArgumentParser()
    ap.add_argument("--selfcheck", action="store_true")
    ap.add_argument("--ticker", help="mã, phân tách bằng dấu phẩy")
    ap.add_argument("--asof", help="YYYY-MM-DD")
    a = ap.parse_args()

    if a.selfcheck:
        raise SystemExit(_selfcheck())
    if a.ticker and a.asof:
        print(json.dumps(oshares_at(a.ticker.split(","), a.asof), indent=2, ensure_ascii=False))
    else:
        ap.error("cần --selfcheck hoặc --ticker/--asof")
