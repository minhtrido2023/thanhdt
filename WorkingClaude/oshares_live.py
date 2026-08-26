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
from datetime import date, timedelta

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

# Cửa sổ QUÝ-END → NGÀY CÔNG BỐ mà `_absorption_test` quét ngược từ ngày của dòng quý. Một dòng
# `ticker_financial` mang ngày CÔNG BỐ (vd 07-31) nhưng số của nó có thể là số chốt tại QUÝ-END
# (30-06): mọi sự kiện trong khoảng giữa hai mốc đó có thể đã, hoặc chưa, nằm trong con số. 120
# ngày phủ cả trường hợp chậm nhất (BCTC năm đã kiểm toán: hạn 90 ngày sau ngày chốt) mà vẫn là
# một khoảng ĐÓNG — cửa sổ còn bị chặn dưới bởi AIS gần nhất, nên con số này chỉ là trần.
ABSORB_WINDOW_DAYS = 120

# CỬA SỔ NHÌN LÙI của cổng chứng nhận AIS (2026-08-20, job `Taylor_20260820_062330`). Áp dụng
# CHỈ KHI mắt xích AIS liền trước KHÔNG chứng nhận được — xem `_anchor_candidates`. Hai trần là
# lưới an toàn, không phải tham số tinh chỉnh: mọi ca thật đo được (HHV, IDC 2022, ba dòng lớn
# của FPT) chỉ cần đi lùi ĐÚNG MỘT bước qua một mắt xích gãy.
AIS_LOOKBACK_MAX_STEPS = 5
AIS_LOOKBACK_MAX_DAYS = 730


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


def _unabsorbed_iss(ais_rows, iss, upto_exright, verdicts=None):
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
    # MỐC `prev` ĐI THEO CÙNG LUẬT VỚI CỔNG CHỨNG NHẬN (`_anchor_candidates`, 2026-08-20). Cả
    # hàm này lẫn cổng kia đều dựa vào MỘT giả định: `prev` là một phát biểu ĐÚNG về mức niêm
    # yết, vì `delta = last - prev` chỉ có nghĩa khi cả hai đầu đều đúng. Trên một chuỗi vendor
    # xáo trộn thứ tự thì mắt xích liền trước KHÔNG đúng, và `delta` ra một số vô nghĩa ⇒
    # `_subset_matching` không khớp được gì ⇒ hàm rơi về `after` và bỏ sót ISS chưa niêm yết.
    #   TCB, đo 2026-08-20: AIS 2024-08-06 = 7.045.021.622 (thưởng 1:1) → AIS 2024-11-21 =
    #   3.522.510.811 (RA SAU, total NHỎ HƠN — chốt trên nền 2023-08-30, bỏ qua đợt thưởng) →
    #   AIS 2025-12-01 = 7.064.851.739. Lấy `prev` = 2024-11-21 cho `delta` = 3.542.340.928,
    #   không khớp ISS nào; lấy `prev` = mốc LÀNH 2024-08-06 cho `delta` = 19.830.117 = ĐÚNG
    #   ISS 2024-11-30, và phần dư (ESOP 2025-08-04, 21.388.675 CP) hiện ra là CHƯA niêm yết —
    #   đúng như thực tế. Không có mốc lùi thì TCB@2026-03-01 trả 7.064.851.739, thấp hơn sự
    #   thật (7.086.240.414, mọi dòng quý và AIS 2026-08-05 đều xác nhận) đúng 0,30%.
    # `verdicts` VẮNG ⇒ `_anchor_candidates` trả đúng mắt xích liền trước ⇒ hành vi CŨ y nguyên;
    # hàm này không bao giờ tự nới khi caller không đưa được bảng verdict.
    _prior = _distinct_ais([r for r in rows[:-1]
                            if r["effective_date"] < last["effective_date"]])
    _cands = _anchor_candidates(_prior, verdicts or {}, last["effective_date"])
    prev = _cands[-1] if _cands else None
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


def _unsizable(e):
    """True nếu `_roll` sẽ coi `e` là BLOCKER — không có cỡ nào dùng được. Giữ ĐÚNG thứ tự
    fallback của `_roll` (`shares_delta` → `issue_volumn` → `exercise_ratio`); đọc lại điều kiện
    ở đây thay vì gọi `_roll` để không phải dựng một `value` giả chỉ để hỏi một câu boolean."""
    return not any((e.get(f) is not None and float(e[f]) != 0.0)
                   for f in ("shares_delta", "issue_volumn", "exercise_ratio"))


def _size_hint(e):
    """Cỡ mà `_roll` SẼ dùng cho `e`, dạng chuỗi cho `note` — không giả định trường nào có sẵn."""
    for f in ("shares_delta", "issue_volumn"):
        if e.get(f) is not None and float(e[f]) != 0.0:
            return f"{float(e[f]):,.0f} ({f})"
    r = e.get("exercise_ratio")
    return f"×{1.0 + float(r):.4f} (exercise_ratio)" if r else "(không cỡ)"


def _absorption_test(row_time, row_value, ais, iss):
    """(events_to_roll, report) — dòng quý `row_time` ĐÃ nuốt những ISS nào trong cửa sổ quý-end?

    ⚠️ THÊM 2026-08-20 (job `Taylor_20260820_043511`, chỉ đạo user). Lỗ hổng nó bịt, nguyên văn
    quan sát của user: *"ngày ra BCTC ví dụ 28.07 chỉ phản ánh dữ liệu đúng đến 30.06 (quý-end);
    sự kiện từ 01.07 trở đi CHƯA được phản ánh đầy đủ trong báo cáo"*. Một dòng
    `ticker_financial` mang NGÀY CÔNG BỐ, còn con số trong nó có thể là số chốt tại QUÝ-END. Khi
    dòng quý làm NEO (`FIN_FALLBACK` / `ANCHOR_UNVERIFIED`), `_pending_iss` chỉ lăn các ISS có
    `exright_date > anchor_date`, tức mọi sự kiện rơi vào khoảng `(quý-end, ngày công bố]` bị coi
    là ĐÃ nằm trong neo — và nếu vendor chép nguyên số quý-end thì đó là THIẾU ÂM THẦM.

    KHÔNG THAY MỘT LUẬT CẮT-NGÀY BẰNG MỘT LUẬT CẮT-NGÀY KHÁC. Vendor KHÔNG nhất quán — đo được
    cả hai phía, cùng một bảng:
      * `HHV` dòng 2026-07-31 = 574.511.888. Cổ tức CP 5% ex 2026-07-09 khai
        `issue_volumn` 27.345.592 / `exercise_ratio` 0,05 ⇒ base vendor tự khai
        B = 546.911.840, và B × 1,05 = 574.257.432 — lệch 0,044% so với dòng quý, TRONG
        `EXPLAIN_TOL`. Dòng đó ĐÃ GỒM sự kiện: cắt theo quý-end sẽ đếm HAI LẦN (+4,76%).
      * `FPT` dòng 2025-07-22 mang số SAU đợt thưởng 15% ex 2025-07-21 (registry
        `ticker_financial_oshares.md`) — vendor cập nhật tới tận ngày công bố.
    ⇒ Không có ngày nào tách được hai ca này. Cái tách được chúng là SỐ HỌC, và số học đó do
    CHÍNH sự kiện khai ra: `B = issue_volumn / exercise_ratio` là số CP trước sự kiện theo lời
    khai của tổ chức phát hành.

    GIẢ THUYẾT, TỔNG QUÁT CHO n SỰ KIỆN trong cửa sổ (sắp theo `exright_date` tăng dần). Gọi
    `B_k` = base khai của sự kiện thứ k ⇒ `B_k` chính là số CP SAU khi đã gồm k−1 sự kiện đầu:

        H_k ("dòng quý gồm đúng k sự kiện đầu"),  k = 0..n
            k < n :  kỳ vọng = B_{k+1}
            k = n :  kỳ vọng = B_n × (1 + ratio_n)

    So `row_value` với từng kỳ vọng trong `EXPLAIN_TOL`:
      (a) khớp ĐÚNG MỘT `H_k` ⇒ lăn các sự kiện thứ k+1..n (k = n ⇒ không lăn gì, ca `HHV`).
          Lăn bằng `issue_volumn` — số ĐẾM, không phải tỉ lệ (xem `_roll`).
      (b) không khớp cái nào, khớp NHIỀU cái, hoặc thiếu `ratio`/`issue_volumn` ở bất kỳ sự kiện
          nào trong cửa sổ ⇒ **GIỮ NGUYÊN HÀNH VI CŨ (không lăn)** và gắn nhãn
          `WINDOW_AMBIGUOUS` kèm CẢ HAI/ CẢ n+1 con số giả thuyết, để người đọc snapshot thấy
          khoảng chưa quyết được thay vì im lặng.

    Vì sao ca không quyết được lại nghiêng về KHÔNG LĂN: cùng bất đối xứng mà cả module này theo
    (xem `_unabsorbed_iss`) — cộng thêm một lượng CP đã nằm trong neo thì thổi phồng mẫu số của
    mọi chỉ số per-share một cách âm thầm; không cộng thì để nguyên con số đang phục vụ hôm nay,
    và nhãn `WINDOW_AMBIGUOUS` nói ra chỗ thiếu.

    ⚠️ TỈ LỆ NHỎ LÀM B KÉM TIN CẬY, và điều đó tự đẩy ca về nhánh (b), có chủ đích. `exercise_ratio`
    được làm tròn 4–5 chữ số ⇒ sai số tương đối của `B` ≈ 5e-6/ratio: ratio 0,05 cho 0,01%
    (trong `EXPLAIN_TOL`), nhưng một đợt ESOP ratio 0,00225 cho ~0,22% (NGOÀI `EXPLAIN_TOL`) ⇒
    không giả thuyết nào khớp ⇒ `WINDOW_AMBIGUOUS`, không lăn. Đó là kết quả ĐÚNG: với ESOP nhỏ,
    `B` đơn giản không đủ độ phân giải để trả lời, và nói "không biết" rẻ hơn đoán.

    CỬA SỔ BỊ CHẶN HAI ĐẦU, không quét vô hạn về quá khứ:
        (max(AIS gần nhất ≤ row_time, row_time − ABSORB_WINDOW_DAYS), row_time]
    Chặn dưới bằng AIS gần nhất vì một ISS có `exright` TRƯỚC AIS đó đã ở trong cả AIS lẫn BCTC
    (hoặc là ca lock-up mà `_unabsorbed_iss` xử lý ở nhánh neo AIS) — kéo nó vào đây là mở lại
    đúng lỗi "orphan event cưỡi lên mọi câu trả lời sau" đã đo ở `_unabsorbed_iss`. Lấy `max` =
    cửa sổ HẸP NHẤT = gần hành vi cũ nhất.
    """
    floor = (date.fromisoformat(row_time) - timedelta(days=ABSORB_WINDOW_DAYS)).isoformat()
    prior_ais = [a["effective_date"] for a in ais if a["effective_date"] <= row_time]
    if prior_ais:
        floor = max(floor, max(prior_ais))
    window = sorted(_dedup_iss([e for e in iss if floor < e["exright_date"] <= row_time]),
                    key=lambda e: e["exright_date"])
    if not window:
        return [], None

    bases = []
    for e in window:
        r, v = e.get("exercise_ratio"), e.get("issue_volumn")
        bases.append(None if (r is None or float(r) <= 0 or v is None or float(v) <= 0)
                     else float(v) / float(r))
    hyps = []                                   # hyps[k] = kỳ vọng của H_k, k = 0..n
    for k in range(len(window) + 1):
        if k < len(window):
            hyps.append(bases[k])
        elif bases[-1] is None:
            hyps.append(None)
        else:
            hyps.append(bases[-1] * (1.0 + float(window[-1]["exercise_ratio"])))
    matches = [k for k, exp in enumerate(hyps)
               if exp and abs(row_value - exp) / exp <= EXPLAIN_TOL]

    rep = {"window_from": floor, "window_to": row_time, "row_value": row_value,
           "events": [_event_dict(e) for e in window],
           "hypotheses": [{"absorbed_count": k, "expected": exp,
                           "rel_diff": (None if not exp else row_value / exp - 1.0)}
                          for k, exp in enumerate(hyps)]}
    def _ambiguous(why):
        rep["verdict"] = "WINDOW_AMBIGUOUS"
        rep["rolled"] = []
        rep["note"] = (
            f"{len(window)} ISS trong cửa sổ ({floor}, {row_time}] KHÔNG quyết được là dòng quý "
            f"{row_value:,.0f} đã gồm hay chưa ({why}) ⇒ GIỮ hành vi cũ: KHÔNG lăn. "
            "Các số giả thuyết: "
            + " · ".join(f"gồm {k}/{len(window)} ⇒ "
                         + ("thiếu ratio/issue_volumn" if not h else f"{h:,.0f}")
                         for k, h in enumerate(hyps)))
        return [], rep

    if len(matches) != 1:
        return _ambiguous(f"{len(matches)} giả thuyết khớp trong {EXPLAIN_TOL*100:.1f}%")
    k = matches[0]
    extra = window[k:]
    # ⚠️ 2026-08-20 (attempt 2): một sự kiện mà `_roll` KHÔNG định cỡ được (thiếu cả
    # `shares_delta`, `issue_volumn` LẪN `exercise_ratio`) có thể lọt vào `extra` — giả thuyết
    # của CHÍNH nó là None nên nó không bao giờ được khớp, nhưng một giả thuyết k' < k khớp thì
    # nó vẫn bị kéo theo. Để nguyên thì hoặc `_roll` biến nó thành blocker (một câu trả lời ĐANG
    # CÓ SỐ bị đẩy về `UNKNOWN_RATIO` — regression), hoặc — đo thật — dòng `note` ném `TypeError`
    # thô vì `float(None)`. Không quyết cỡ được thì đúng là "không quyết được": về nhánh (c).
    if any(_unsizable(e) for e in extra):
        return _ambiguous(
            "khớp giả thuyết 'đã gồm %d/%d' NHƯNG %d sự kiện phải lăn không có cỡ dùng được "
            "(thiếu cả shares_delta, issue_volumn lẫn exercise_ratio)"
            % (k, len(window), sum(1 for e in extra if _unsizable(e))))
    rep["verdict"] = "ABSORBED" if not extra else "ROLLED"
    rep["rolled"] = [_event_dict(e) for e in extra]
    rep["note"] = (
        f"dòng quý {row_value:,.0f} khớp giả thuyết 'đã gồm {k}/{len(window)} ISS của cửa sổ' "
        f"(kỳ vọng {hyps[k]:,.0f}, lệch {(row_value/hyps[k]-1)*100:+.3f}%) ⇒ "
        + ("KHÔNG lăn lại sự kiện nào" if not extra else
           f"LĂN {len(extra)} sự kiện chưa được phản ánh: "
           + ", ".join(f"{e['exright_date']} +{_size_hint(e)}" for e in extra)))
    return extra, rep


def _pending_iss(ais_rows, iss, anchor_date, anchor_source, asof, verdicts=None):
    """The ISS still to be rolled onto an anchor — the answer depends on WHICH anchor it is.

    An AIS states the LISTED count, so what it already contains is decided by the accounting of
    the AIS chain up to it (`_unabsorbed_iss`). A `ticker_financial` row states the ISSUED count
    — a private placement is in the balance sheet from the day it is issued, long before the
    exchange lists it (that is the whole reason `FIN_FALLBACK` exists) — so for a quarterly
    anchor the ex-date remains the right test and the AIS chain must NOT be consulted. Using one
    rule for both anchors would either lose lock-up shares from an AIS or double-count
    placements on a quarterly row.

    `verdicts` (2026-08-20) chỉ đi tiếp xuống `_unabsorbed_iss` để nó chọn được mốc `prev` LÀNH
    trên một chuỗi AIS bị xáo trộn thứ tự. Vắng ⇒ hành vi cũ y nguyên.
    """
    if anchor_source == "corporate_action.AIS":
        return _unabsorbed_iss([r for r in ais_rows if r["effective_date"] <= anchor_date],
                               iss, asof, verdicts)
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


def _explain_quarterly(q, ais, iss, verdicts=None):
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
    prior = _distinct_ais([a for a in ais if a["effective_date"] <= t])
    if not prior:
        hit = [a for a in ais if a["effective_date"] > t
               and abs(float(a["shares_total_after"]) - v) < 1.0]
        if hit:
            return False, False, (
                f"{v:,.0f} trùng ĐÚNG số của AIS {hit[0]['effective_date']} (SAU ngày quý "
                f"{t}) và không có AIS nào trước đó để giải thích ⇒ RESTATE"), None
        return True, False, "không có AIS nào <= ngày quý ⇒ nhận nhưng KHÔNG kiểm chứng được", None
    if verdicts is None:
        verdicts = _ais_verdicts_from_rows(ais, iss)
    # CÙNG luật chọn mốc với cổng chứng nhận AIS (`_anchor_candidates`, nới 2026-08-20): mốc mặc
    # định vẫn là AIS liền trước; chỉ khi CHÍNH mốc đó không chứng nhận được mới lùi tới mốc lành
    # gần nhất. Một luật, hai chỗ dùng — nếu không, cùng một chuỗi AIS xáo trộn sẽ cho cổng này
    # và cổng kia hai câu trả lời khác nhau (đúng ca HHV 2026-07-31: đối chiếu với AIS 2026-05-07
    # lệch +14,65%, đối chiếu với AIS 2026-04-08 khớp TỪNG ĐƠN VỊ).
    # `upto_date` cho cửa sổ nhìn lùi = ngày AIS liền trước (`prior[-1]`), KHÔNG phải `t` (ngày
    # quý) — cùng cách `_unabsorbed_iss` gọi hàm này (`last["effective_date"]`), vì `t` có thể
    # cách rất xa mắt xích AIS cuối (đúng lúc AIS đã CŨ, tức chính lúc cổng này cần lùi mốc nhất —
    # ca EVF 2026-08-26: mắt xích liền trước 2024-12-06 → 2023-12-22 chỉ cách 350 ngày, nhưng
    # 2023-12-22 → t=2026-07-21 là 942 ngày, VƯỢT `AIS_LOOKBACK_MAX_DAYS` một cách giả tạo nếu đo
    # theo `t`).
    lookback_upto = prior[-1]["effective_date"]
    first = None                    # (mốc, kỳ vọng|None, blockers|None) của ứng viên GẦN NHẤT
    for a in _anchor_candidates(prior, verdicts, lookback_upto):
        # not `a.effective_date < exright <= t` any more: an ISS that went ex BEFORE the AIS but
        # is absent from its `shares_delta` (a lock-up ESOP) is missing from the AIS and PRESENT
        # in the quarterly report, so it belongs in the expectation. Same predicate as
        # `oshares_at` uses — one rule, not two. HAH's quarterly row of 2026-07-30 (191.840.401)
        # only closes against the AIS of 2026-05-27 (185.840.401) once both unlisted ESOP
        # tranches are in it.
        between = _unabsorbed_iss([r for r in prior if r["effective_date"] <= a["effective_date"]],
                                  iss, t, verdicts)
        expected, _applied, blockers = _roll(float(a["shares_total_after"]), between)
        if blockers:
            first = first or (a, None, blockers)
            continue
        if abs(v - expected) / expected <= EXPLAIN_TOL:
            return True, True, "", expected
        first = first or (a, expected, None)
    # BÁO CÁO theo ứng viên GẦN NHẤT (mốc mặc định), không phải theo ứng viên cuối cùng đã thử:
    # người đọc `reason` hỏi "dòng quý này lệch bao nhiêu so với phát biểu mới nhất của sở", và
    # `fin_expected_from_ais` phải giữ đúng nghĩa đó. Số ứng viên đã thử được nói ra khi >1 để
    # không ai đọc nhầm thành "chỉ đối chiếu một chỗ".
    a, expected, blockers = first
    n = len(_anchor_candidates(prior, verdicts, lookback_upto))
    more = f" (đã thử {n} mốc AIS, kể cả mốc lùi)" if n > 1 else ""
    if blockers:
        return False, False, (f"ISS {[b['exright_date'] for b in blockers]} không có tỉ lệ/"
                              f"shares_delta ⇒ không dựng được kỳ vọng để đối chiếu{more}"), None
    return False, False, (f"{v:,.0f} không giải thích được từ AIS {a['effective_date']} "
                          f"({float(a['shares_total_after']):,.0f}) "
                          f"⇒ kỳ vọng {expected:,.0f}, lệch {(v/expected-1)*100:+.2f}%{more}"), expected


def _stale_fallback_verdict(q, a, ais_age_days, ais_certified, live=False):
    """(allow, reason) — số quý bị cổng giải thích LOẠI có được phục vụ như FIN_FALLBACK không?

    Chỉ chạy khi `_explain_quarterly` đã LOẠI dòng quý. BA điều kiện, tất cả đều cần:

      1. CÓ một neo AIS. Không có AIS mà vẫn bị loại thì lý do loại duy nhất là chữ ký RESTATE
         (`v` trùng khít một AIS SAU ngày quý) — đó là bằng chứng look-ahead, không phải lý do
         để tin dòng quý.
      1b. **CHỈ NHÁNH PIT (`live=False`)** — neo AIS đó phải ĐƯỢC CHỨNG NHẬN (`_ais_certified`).
         Xem §NHÁNH LIVE bên dưới: điều kiện này ĐẢO CHIỀU khi `live=True`.
      2. Neo AIS đã CŨ hơn một kỳ báo cáo (`FIN_FALLBACK_MAX_AIS_AGE_DAYS`). Còn tươi thì nó vẫn
         là phát biểu mới nhất của sở về số CP niêm yết; không có gì để thay thế.
      3. Dòng quý phải MỚI HƠN neo AIS. Nếu không, "rơi về BCTC" là đi LÙI.

    ĐIỀU KIỆN THỨ TƯ ĐÃ BỎ 2026-08-19 (chỉ đạo user, job Taylor_20260819_032946). Nó đọc CHIỀU:
    dòng quý CAO hơn kỳ vọng lăn từ AIS ⇒ từ chối, vì feed chỉ có `ISS` (luôn CỘNG) và không có
    mã sự kiện mua cổ phiếu quỹ, nên số GIẢM là thứ feed không thể báo còn số TĂNG là thứ lẽ ra
    phải có. Lập luận đó SAI ở một ca thật: **cổ phiếu phát hành riêng lẻ là cổ phiếu THẬT và
    được BCTC ghi nhận từ trước ngày NIÊM YẾT BỔ SUNG**, nên một số đúng vẫn tới dưới dạng TĂNG
    không giải thích được. Chính sách user: khi AIS đã cũ, `ticker_financial` là nguồn tốt nhất.

    §NHÁNH LIVE — ĐIỀU KIỆN 1b ĐẢO CHIỀU (2026-08-20, chỉ đạo user, job Taylor_20260820_015520)
    ---------------------------------------------------------------------------------------
    `live=True` ⇒ neo AIS CHƯA chứng nhận KHÔNG còn là lý do từ chối; điều kiện 2 và 3 vẫn phải
    đạt, nên BCTC chỉ thắng khi nó MỚI HƠN ngày neo AIS và neo đó đã quá một kỳ báo cáo.

    Vì sao đảo: luật vòng 4 đọc "neo AIS trượt cổng" thành "nghi ngờ TẤT CẢ", nhưng chuỗi AIS
    gãy/không đối chiếu được là bằng chứng chống lại CHÍNH AIS, không phải chống lại BCTC — nó
    làm BCTC ĐÁNG TIN HƠN một cách tương đối, không phải kém hơn. Bằng chứng sống, TCB 2026-08-20:
    dòng quý 2026-07-21 = 7.086.240.414 bị cổng loại 2 tuần liền (lệch +0,30% so với chuỗi AIS);
    ngày 08-05 AIS mới về và `shares_total_after` của nó = **đúng con số BCTC đã nói từ 07-21**.
    BCTC đi TRƯỚC AIS và ĐÚNG. Hai ca đang bị kẹt cùng hình dạng, cùng ngày: EVF (AIS 2024-12-06
    uncertified, BCTC 2026-07-21 = 760.565.802 mới hơn **1,5 năm**) và HHV (AIS 2026-05-07
    uncertified, BCTC 2026-07-31 = 574.511.888).

    Vẫn TỪ CHỐI khi BCTC CŨ HƠN neo AIS uncertified (điều kiện 3 — đó là đi LÙI), và vẫn từ chối
    khi neo AIS còn tươi ≤ `FIN_FALLBACK_MAX_AIS_AGE_DAYS` (điều kiện 2 — sở vừa phát biểu thì
    không có gì để thay thế, kể cả khi phát biểu đó chưa đối chiếu được). Cơ chế CHỨNG NHẬN
    (`_ais_verdicts`/`_ais_certified`) KHÔNG bị xoá và cổng neo AIS ở cuối `oshares_at` KHÔNG đổi:
    một neo AIS uncertified vẫn không bao giờ được phục vụ như `AIS_EXACT`. Chỉ đổi đúng một
    hành vi: từ "trượt cổng ⇒ câm với mọi nguồn" sang "trượt cổng ⇒ nhường cho BCTC mới hơn".

    ⚠️ PIT GIỮ NGUYÊN. `oshares_at()` mặc định `live=False`, nên `oshares_pit`/backtest không đổi
    một số nào: ở đó fail-closed vẫn đắt hơn look-ahead. Chỉ `corp_action_daily.py` (nhánh phục vụ
    LIVE, publish snapshot hằng ngày) truyền `live=True`.

    ⚠️ CÁI GIÁ, ĐO ĐƯỢC, KHÔNG ĐƯỢC QUÊN: bỏ cổng này đồng thời nhận lại look-ahead thật. Trên
    246 mã `ticker_prune`, tại asof=2026-03-01 (có 5,5 tháng dữ liệu tương lai để đối chiếu) 12 mã
    đổi số và **3 mã mang chữ ký RESTATE** — giá trị phục vụ trùng KHÍT một AIS chỉ có hiệu lực
    SAU đó: HAH 185.840.401 (AIS 2026-05-27), ABB 1.397.208.685 (AIS 2026-06-19), NVL
    2.234.496.474 (AIS 2026-05-29). Không còn cổng point-in-time nào chặn chúng: chữ ký RESTATE
    cần chính AIS TƯƠNG LAI mới tính được. Consumer backtest phải tự đọc `method == "FIN_FALLBACK"`
    (`anchor_verified` luôn False) và tự quyết.

    ⚠️ CÁI GIÁ RIÊNG CỦA NHÁNH LIVE, ĐO TRÊN CÙNG PHÉP ĐO (2026-08-20, job Taylor_20260820_015520,
    script `mike/agents/Taylor/research/oshares_live_anchor_20260820/lookahead_cost_probe.py`,
    kết quả `cost_20260301.json`). Rổ = 263 mã `ticker_prune` tại phiên cuối ≤ 2026-03-01, đối
    chiếu bằng 5,5 tháng dữ liệu tương lai. CẢ HAI nhánh đo lại trên CÙNG rổ đó, vì rổ "246 mã"
    của phép đo 08-19 không tái lập được và so hai con số trên hai rổ là so hai thứ khác nhau:
      * ĐƯỢC: PIT từ chối **28/263** mã, LIVE từ chối **7/263** ⇒ nhánh LIVE cứu **21 mã**
        (+8,0pp phủ). Cả 21 đều đi đúng một đường `AIS_UNCERTIFIED → FIN_FALLBACK`; KHÔNG mã nào
        đổi số theo kiểu khác, tức nhánh mới không rò sang hành vi nào ngoài ca nó nhắm tới.
      * MẤT: chữ ký RESTATE trên neo KHÔNG kiểm chứng được (`FIN_FALLBACK`/`ANCHOR_UNVERIFIED` —
        con đường DUY NHẤT một số tương lai vào được câu trả lời) đi từ **4 mã** (ABB, HAH, NVL,
        TDC) lên **5** — thêm ĐÚNG **1 mã: KBC** (941.754.759 = AIS 2026-06-25).
      * KHÔNG ĐƯỢC TRÍCH con số "chữ ký RESTATE thô" (11 → 12): 7/11 ca của nhánh PIT có neo
        `ANCHOR_ONLY`, tức dòng quý ĐÃ đối chiếu xong với chuỗi AIS — một mã không đổi số CP thì
        AIS kế tiếp trùng khít một cách hoàn toàn vô tội, đó không phải look-ahead.
      * Kiểm chứng chéo phép đo: `FIN_FALLBACK`-RESTATE của nhánh PIT ra ĐÚNG 3 mã ABB/HAH/NVL —
        khớp tuyệt đối con số 3 ghim ở đoạn trên, đo độc lập trên một rổ khác.
    ⇒ tỉ lệ đánh đổi 21 ăn 1. Con số phải nhắc lại khi ai đó muốn siết/nới nhánh này là **1 mã**,
    không phải 12.
    """
    if a is None:
        return False, "không có neo AIS: dòng quý bị loại vì chữ ký RESTATE, không phải vì AIS cũ"
    if not ais_certified and not live:
        return False, (f"neo AIS {a['effective_date']} CHƯA được chứng nhận ⇒ nhánh PIT giữ "
                       f"nguyên luật vòng 4 (từ chối trả lời), không đi vòng sang neo dòng quý")
    if ais_age_days is None or ais_age_days <= FIN_FALLBACK_MAX_AIS_AGE_DAYS:
        return False, (f"neo AIS {a['effective_date']} còn tươi ({ais_age_days} ngày "
                       f"<= {FIN_FALLBACK_MAX_AIS_AGE_DAYS}) ⇒ không rơi về BCTC")
    if q["time"] <= a["effective_date"]:
        return False, (f"dòng quý {q['time']} CŨ hơn neo AIS {a['effective_date']} ⇒ rơi về BCTC "
                       f"là đi LÙI")
    uncert = ("" if ais_certified else
              " — neo AIS này CHƯA chứng nhận, và đó là lý do TĂNG chứ không giảm độ tin của "
              "BCTC (nhánh LIVE, chính sách user 2026-08-20)")
    return True, (f"neo AIS {a['effective_date']} cũ {ais_age_days} ngày (> "
                  f"{FIN_FALLBACK_MAX_AIS_AGE_DAYS}); dòng quý {q['time']} = "
                  f"{float(q['OShares']):,.0f} mới hơn ⇒ BCTC là phát biểu tốt nhất về số CP "
                  f"đang lưu hành (chính sách user 2026-08-19, KHÔNG xét chiều tăng/giảm)"
                  + uncert)


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


def _distinct_ais(ais_rows):
    """AIS sort tăng dần theo `effective_date`, MỘT dòng mỗi ngày (giữ dòng CUỐI của nhóm).

    Giữ dòng cuối là để bảo toàn nguyên xi hành vi của vòng lặp cũ (`zip(rows, rows[1:])` +
    `continue` khi trùng ngày): ở đó mốc dùng cho transition kế tiếp luôn là dòng SAU CÙNG của
    nhóm cùng ngày. FPT có 4 dòng AIS y hệt nhau ngày 2018-07-16 và 2 dòng ngày 2018-04-23 (một
    dòng `shares_total_after` rỗng đã bị caller lọc trước) — trùng ngày là chuyện thường, không
    suy ra được thứ tự trong ngày, nên gộp lại thành một mốc.
    """
    by_date = {}
    for r in sorted(ais_rows, key=lambda x: x["effective_date"]):
        by_date[r["effective_date"]] = r
    return [by_date[d] for d in sorted(by_date)]


def _anchor_candidates(prior, verdicts, upto_date):
    """Những AIS được phép làm MỐC đối chiếu cho một phát biểu tại `upto_date`, gần nhất trước.

    `prior` = AIS đã lọc theo ngày bởi caller (`< upto_date` cho một AIS, `<= upto_date` cho một
    dòng quý), đã qua `_distinct_ais`. Luôn trả về ÍT NHẤT mắt xích liền trước — tức luật cũ là
    một TẬP CON của luật này, không phải một luật khác.

    NỚI 2026-08-20 (job `Taylor_20260820_062330`, chỉ đạo user). Trước đó cổng chứng nhận chỉ đối
    chiếu với **AIS LIỀN TRƯỚC**, và điều đó gãy khi chính mắt xích liền trước là dòng hỏng — mà
    feed vendor xáo trộn thứ tự thì lỗi ấy KHÔNG hiếm:

      HHV, đo trên BQ 2026-08-20 (văn bản HOSE 1692/TB-SGDHCM xác nhận con số):
        AIS 2026-04-08  delta 49.733.293  total 547.166.296   (executed)
        AIS 2026-05-07  delta 41.500.000  total 473.755.528   (executed — RA SAU nhưng total NHỎ
                                                               HƠN; 473.755.528 = 432.255.528 +
                                                               41.500.000, tức nó chốt trên nền
                                                               của AIS 2024-09-09, bỏ qua hai AIS
                                                               ở giữa ⇒ vendor xáo trộn thứ tự)
        AIS 2026-08-20  delta 27.345.592  total 574.511.888
      547.166.296 + 27.345.592 = 574.511.888 — KHỚP TỪNG ĐƠN VỊ với cả dòng `ticker_financial`
      2026-07-31 lẫn văn bản HOSE. Đối chiếu với AIS liền trước (473.755.528) lệch +14,65% ⇒
      dòng ĐÚNG bị đánh UNVERIFIED, và tối 2026-08-20 khi AIS này lật `executed` nó trở thành neo
      tươi nhất ⇒ HHV lẽ ra REGRESS từ 574.511.888 về `None` (AIS_UNCERTIFIED) đúng ngay sau khi
      sở xác nhận chính con số đó.

    ĐIỀU KIỆN VÀO — mắt xích liền trước phải KHÔNG chứng nhận được. Đây là chỗ luật này khác hẳn
    "thử mọi AIS trong 24 tháng", và sự khác biệt ĐÃ ĐO ĐƯỢC, không phải khẩu vị:
      * `AAA` 2019-06-03 (`shares_total_after` 58.664.988, `shares_delta` 1.700.000) là một trong
        HAI ca vendor sai mà cả module này được viết ra để chặn. Mắt xích liền trước của nó
        (2018-10-18, 171.199.976) chứng nhận ĐƯỢC ⇒ không đi lùi ⇒ vẫn UNVERIFIED. Nếu bỏ điều
        kiện vào và cho thử mọi AIS trong cửa sổ 5 bước, nó KHỚP CHÍNH XÁC mốc 2017-01-24
        (56.964.988 + 1.700.000 = 58.664.988) và ca chặn kinh điển này lọt lưới. Trùng hợp số học
        thuần tuý — hai mốc cách nhau 860 ngày và 4 đợt phát hành.
      * `IDC` 2020-05-28 (3.000.000.000, ~10× thật) — mắt xích liền trước (2019-06-13,
        300.000.000) chứng nhận được ⇒ không đi lùi ⇒ vẫn UNVERIFIED.
    ⇒ Lý do DUY NHẤT được phép bước qua một mắt xích là mắt xích đó GÃY. Một chuỗi lành thì phát
    biểu gần nhất là phát biểu đúng, và "một mốc cũ hơn tình cờ cộng ra đúng số" là trùng hợp,
    không phải bằng chứng.

    MỐC THAY THẾ PHẢI TỰ NÓ ĐÃ ĐƯỢC CHỨNG NHẬN, và dừng ở cái ĐẦU TIÊN tìm được. Neo vào một dòng
    chưa kiểm để chứng nhận dòng sau là bắc cầu trên nền không kiểm — đúng thứ vòng-tròn mà cổng
    này tồn tại để chặn. `verdicts` luôn đã có đủ verdict của mọi dòng TRƯỚC `upto_date` vì hàm
    gọi đi theo thứ tự thời gian.

    KHÔNG dùng `ticker_financial` để chứng nhận một AIS (đã cân nhắc, BÁC — chỉ đạo cho phép tự
    quyết): dòng quý là thứ `_explain_quarterly`/`_stale_fallback_verdict` đang PHỤC VỤ dựa trên
    chính neo AIS này. Lấy nó chứng nhận neo rồi lấy neo giải thích nó là vòng tròn hoàn hảo, và
    nó cũng đưa look-ahead của `ticker_financial` (2.667 dòng restate, xem docstring module) vào
    thẳng nhánh AIS vốn đang sạch. Hai nguồn chỉ độc lập khi không nguồn nào là hệ quả của nguồn
    kia; ở đây chúng không độc lập.
    """
    if not prior:
        return []
    out = [prior[-1]]
    if verdicts.get(prior[-1]["effective_date"]) in _SERVE_AIS_VERDICTS:
        return out                              # mắt xích liền trước LÀNH ⇒ không có cớ đi lùi
    for step, r in enumerate(reversed(prior[:-1]), start=1):
        if step > AIS_LOOKBACK_MAX_STEPS or \
                _days_between(r["effective_date"], upto_date) > AIS_LOOKBACK_MAX_DAYS:
            break
        if verdicts.get(r["effective_date"]) in _SERVE_AIS_VERDICTS:
            out.append(r)
            break                               # mắt xích LÀNH đầu tiên, không đi xa hơn
    return out


def _delta_predates_anchor(base, delta, iss):
    """True nếu `delta` trùng khít (trong `EXPLAIN_TOL`) cỡ một ISS đã ex-right TRƯỚC (hoặc đúng)
    ngày hiệu lực của `base`.

    ⚠️ EVF 2024-12-06 (job `Taylor_20260826_013256`). Candidate (b) của `_ais_reconciles`
    (`base_v + delta`) ngầm giả định `delta` là hoạt động MỚI phát sinh SAU `base` — nhưng nếu
    đúng cỡ đó đã ex-right TỪ TRƯỚC `base`, nó không phải hoạt động mới: đó là niêm yết TRỄ của
    một lô đã tồn tại từ trước, và `base_v` (đúng ra) đã phải gồm nó rồi. Chấp nhận (b) trong ca
    này hợp thức hoá một neo "chốt trên nền cũ" — same trùng hợp số học mà `_anchor_candidates`
    cảnh báo cho AAA/IDC, chỉ khác chỗ trùng hợp xảy ra qua `shares_delta` thay vì qua một mốc
    lùi khác. EVF: AIS 2023-12-22 (702.128.062) + delta 2.120.227 (AIS 2024-12-06) = 704.248.289
    KHỚP KHÍT — nhưng 2.120.227 là cỡ của ISS "Phát hành cho CBCNV" ex-right 2023-12-05, TRƯỚC
    2023-12-22. Lô đó đã được AIS 2024-11-22 (760.565.802, mốc THẬT ở giữa) cộng vào từ trước;
    2024-12-06 chỉ đăng ký niêm yết TRỄ đúng lô đó trên nền CŨ. Chặn (b) ở đây; candidate (a) —
    lăn qua ISS — không đụng tới, và đường đúng để giải thích các dòng SAU vẫn là (a) qua mốc lùi
    `_anchor_candidates`/`_unabsorbed_iss` đã có sẵn (không mốc mới, không luật mới ở đó).
    """
    for e in iss:
        if e["exright_date"] > base["effective_date"]:
            continue
        for f in ("shares_delta", "issue_volumn"):
            sz = e.get(f)
            if sz is not None and float(sz) > 0 and abs(float(sz) - delta) / delta <= EXPLAIN_TOL:
                return True
    return False


def _ais_reconciles(base, actual, delta, iss, upto_date):
    """`actual` (mức CP niêm yết công bố tại `upto_date`) có giải thích được từ mốc `base` không?

    HAI đường hợp lệ, khớp MỘT là đủ — giữ nguyên chữ và nghĩa của bản 2026-08-13, chỉ tách ra
    thành hàm để phần "mốc nào" và phần "khớp thế nào" không còn dính vào nhau:
        (a) roll(base, ISS ở giữa)      — ISS đã cộng phần tăng, AIS chỉ là lần đăng ký niêm yết
        (b) base + shares_delta         — không có ISS tương ứng, `shares_delta` là nguồn duy nhất
    Cộng cả hai là ĐẾM HAI LẦN (xem `_ais_verdicts`). Ngưỡng khớp vẫn là `EXPLAIN_TOL` (0,1%) —
    cổng nới CHỖ ĐỐI CHIẾU, KHÔNG nới ĐỘ CHÍNH XÁC.
    """
    base_v = float(base["shares_total_after"])
    cands = []
    # RAW ex-date window, cố ý — xem `_ais_verdicts`: chính hàm này XÁC LẬP xem một AIS đã niêm
    # yết ISS nào, nên khoá nó theo output của phép khớp đó là vòng tròn.
    between = _dedup_iss([e for e in iss
                          if base["effective_date"] < e["exright_date"] <= upto_date])
    rolled, _applied, blockers = _roll(base_v, between)
    if not blockers:
        cands.append(rolled)                                 # (a) — chỉ khi lăn được HẾT ISS
    if delta is not None and float(delta) > 0 and not _delta_predates_anchor(base, float(delta), iss):
        cands.append(base_v + float(delta))                  # (b) — không phụ thuộc ISS
    # `cands` RỖNG (blocker chắn (a) VÀ không có delta cho (b)) ⇒ không dựng được kỳ vọng nào.
    # Đây là chỗ `all([]) == True` từng làm nghĩa đảo ngược nếu viết gọn ⇒ viết TƯỜNG MINH.
    return bool(cands) and any(e > 0 and abs(actual - e) / e <= EXPLAIN_TOL for e in cands)


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
    ais_rows = [c for c in corp
                if c["ticker"] == ticker and c["event_code"] == "AIS"
                and c["effective_date"] and c["effective_date"] <= asof
                and c["shares_total_after"]]
    iss = [c for c in corp if c["ticker"] == ticker and c["event_code"] == "ISS"
           and c["exright_date"] and c["exright_date"] <= asof]
    return _ais_verdicts_from_rows(ais_rows, iss)


def _ais_verdicts_from_rows(ais_rows, iss):
    """Lõi của `_ais_verdicts`, tách ra 2026-08-20 để `_explain_quarterly` dùng CHUNG một bản.

    `oshares_at` đã có sẵn hai danh sách này (đã cắt theo `asof`, đã lọc `shares_total_after`) —
    trước đây nó phải đi vòng qua `corp`/`ticker`/`asof` để hỏi lại cùng một câu, và
    `_explain_quarterly` thì không hỏi được câu đó chút nào. Hai bộ lọc là TƯƠNG ĐƯƠNG:
    `dilutes_share_count` ở `oshares_at` chính là `event_code == "ISS"`.
    """
    rows = _distinct_ais(ais_rows)
    verdicts = {}
    if rows:
        verdicts[rows[0]["effective_date"]] = "NO_PRIOR"
    # theo thứ tự thời gian, KHÔNG phải vì gọn: `_anchor_candidates` đọc verdict của các dòng
    # TRƯỚC dòng đang xét, nên chúng phải đã tính xong.
    for i, cur in enumerate(rows):
        if i == 0:
            continue
        actual = float(cur["shares_total_after"])
        delta = cur.get("shares_delta")
        ok = any(_ais_reconciles(base, actual, delta, iss, cur["effective_date"])
                 for base in _anchor_candidates(rows[:i], verdicts, cur["effective_date"]))
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


def oshares_at(tickers, asof, _cache=None, live=False):
    """{ticker: dict} — shares outstanding at `asof`, with the derivation shown.

    Each value carries `value`, `method`, `anchor_date`, `anchor_value`, `anchor_source` and the
    list of ISS events applied, so any number can be re-derived by hand from the output alone.
    `value is None` whenever the method is `UNKNOWN_RATIO`, `NO_ANCHOR` or `AIS_UNCERTIFIED` —
    callers MUST handle that; there is no "best effort" number behind it.

    `live=False` (mặc định) = nhánh POINT-IN-TIME, dùng cho backtest/`oshares_pit`: không đổi một
    số nào so với trước 2026-08-20. `live=True` = nhánh PHỤC VỤ HÔM NAY: nới ĐÚNG MỘT điều kiện —
    neo AIS chưa chứng nhận không còn chặn được một dòng BCTC MỚI HƠN nó (xem §NHÁNH LIVE trong
    `_stale_fallback_verdict`). Nới ở đây là nhận thêm look-ahead để đổi lấy độ phủ, nên nó CHỈ
    hợp lệ khi câu hỏi là "hôm nay có bao nhiêu CP" — không bao giờ hợp lệ trong một backtest.
    Cổng chứng nhận neo AIS ở cuối hàm KHÔNG bị `live` chạm tới ở cả hai nhánh.

    NỚI THỨ HAI CỦA NHÁNH LIVE (2026-08-20): `_absorption_test`. Khi neo là dòng quý CHƯA được
    cổng giải thích thông qua, các ISS rơi vào cửa sổ `(quý-end, ngày công bố]` được KIỂM bằng số
    học xem dòng quý đã gồm chúng chưa, thay vì mặc định "đã gồm". Kết luận luôn được ghi ra
    `absorption_test` (kể cả ca `WINDOW_AMBIGUOUS` = không quyết được ⇒ giữ hành vi cũ).
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
        # MỘT lần cho cả mã, và FAIL-CLOSED: cổng chứng nhận sập ⇒ bảng verdict RỖNG ⇒ mọi neo
        # AIS coi như chưa chứng nhận (`.get()` trả None), và `_anchor_candidates` co về đúng luật
        # cũ "chỉ AIS liền trước" vì không mốc lùi nào chứng nhận được. Không có nhánh nào của
        # cổng sập mà lại NỚI ra.
        try:
            verdicts = _ais_verdicts(corp, tk, asof)
        except Exception:                       # noqa: BLE001 — fail-closed by design
            verdicts = {}

        anchors, rejected, unverified = [], [], False
        fin_fallback = None
        a = max(ais, key=lambda r: r["effective_date"]) if ais else None
        q = max(qs, key=lambda r: r["time"]) if qs else None
        ais_age_days = _days_between(a["effective_date"], asof) if a else None

        if a:
            anchors.append((a["effective_date"], float(a["shares_total_after"]),
                            "corporate_action.AIS"))
        if q:
            ok, verified, why, expected = _explain_quarterly(q, ais, iss, verdicts)
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
                a_ok = bool(a) and verdicts.get(a["effective_date"]) in _SERVE_AIS_VERDICTS
                allow, fb_why = _stale_fallback_verdict(q, a, ais_age_days, a_ok, live=live)
                if allow:
                    anchors.append((q["time"], float(q["OShares"]), "ticker_financial"))
                    unverified = True          # served, but the gate never cleared it
                    fin_fallback = {"fin_fallback": True, "fin_quarter": q["time"],
                                    "fin_value": float(q["OShares"]),
                                    "ais_anchor_date": a["effective_date"] if a else None,
                                    "ais_age_days": ais_age_days,
                                    "fin_expected_from_ais": expected,
                                    # ghi RA bản ghi, không chỉ vào chuỗi lý do: người đọc snapshot
                                    # phải lọc được "số này chỉ tồn tại nhờ nhánh LIVE" bằng một
                                    # trường, không phải bằng cách grep tiếng Việt trong `reason`.
                                    "fin_anchor_ais_certified": a_ok, "fin_branch_live": bool(live),
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

        # ── ABSORPTION TEST (2026-08-20) ────────────────────────────────────────────────────
        # CHỈ nhánh LIVE, và CHỈ khi neo là dòng quý CHƯA được cổng giải thích thông qua
        # (`FIN_FALLBACK` / `ANCHOR_UNVERIFIED`). Neo dòng quý ĐÃ verified thì `_explain_quarterly`
        # đã đối chiếu xong bằng `_unabsorbed_iss` — hỏi lại ở đây là hai lời đáp cho một câu hỏi.
        # `live` gác cổng vì nhánh PIT KHÔNG được đổi một số nào (backtest đang ghim); mở cho PIT
        # là một quyết định riêng, cần đo lại trên rổ, không phải hệ quả tự nhiên của bản vá này.
        absorb = None
        extra = []
        if live and anchor_src == "ticker_financial" and unverified:
            extra, absorb = _absorption_test(anchor_date, anchor_value, ais, iss)

        pending = _pending_iss(ais, iss, anchor_date, anchor_src, asof, verdicts) + extra
        value, applied, blockers = _roll(anchor_value, pending)

        anchor_verified = not (unverified and anchor_src == "ticker_financial")
        base = {"ticker": tk, "asof": asof, "anchor_date": anchor_date,
                "anchor_value": anchor_value, "anchor_source": anchor_src,
                "anchor_verified": anchor_verified, "rejected_anchors": rejected}
        if absorb:
            # ghi RA bản ghi kể cả khi kết luận là "không lăn": ca WINDOW_AMBIGUOUS chỉ có giá trị
            # nếu người đọc snapshot NHÌN THẤY nó — im lặng ở đây là đúng lỗi mà nó đi sửa.
            base["absorption_test"] = absorb
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
                and verdicts.get(anchor_date) not in _SERVE_AIS_VERDICTS:
            out[tk] = {**base, "value": None, "method": "AIS_UNCERTIFIED",
                       "uncertified_value": value, "uncertified_method": method,
                       "events_applied": [_event_dict(e, h, s) for e, h, s in applied],
                       "note": f"neo AIS {anchor_date} ({anchor_value:,.0f}) không đối chiếu được "
                               f"với BẤT KỲ mốc AIS nào trong cửa sổ nhìn lùi ⇒ KHÔNG phục vụ "
                               f"{value:,.0f} (fail-closed); "
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
    # ⚠️ N1/N1b/N2 VIẾT LẠI 2026-08-20 (job `Taylor_20260820_062330`, cửa sổ nhìn lùi). Bất biến
    # được bảo vệ KHÔNG ĐỔI — "hai số vendor sai này KHÔNG BAO GIỜ được phục vụ" — nhưng HÌNH DẠNG
    # của việc từ chối thì đổi, và phải nói thẳng chứ không sửa lén con số kỳ vọng:
    #   trước: dòng AIS hỏng là neo tươi nhất, dòng quý bị loại vì đối chiếu với CHÍNH nó ⇒
    #          `oshares_at` câm (`value=None`, `AIS_UNCERTIFIED`);
    #   nay:   dòng AIS hỏng vẫn UNVERIFIED (đó mới là cổng), nhưng dòng quý nay đối chiếu được
    #          với mốc LÀNH phía trước nó ⇒ được nhận làm neo và trả về SỐ ĐÚNG.
    # Kiểm ở tầng VERDICT chứ không chỉ ở tầng `method`: `method` đổi khi neo khác thắng, verdict
    # thì phát biểu đúng cái cổng này chịu trách nhiệm. Một test chỉ đọc `method` sẽ đọc "trả số
    # đúng" thành "cổng thủng".
    icache4 = _fetch(["IDC"], "2021-02-05")
    idc = oshares_at(["IDC"], "2021-02-05", _cache=icache4)["IDC"]
    idc_v = _ais_verdicts(icache4[1], "IDC", "2021-02-05")
    print(f"  IDC 2021-02-05: {fmt(idc['value'])} [{idc['method']}] anchor={idc['anchor_date']} "
          f"({idc['anchor_source']}) · verdict AIS 2020-05-28 = {idc_v.get('2020-05-28')}")
    check("N1. IDC: dòng AIS 2020-05-28 (3.000.000.000) VẪN không chứng nhận được, kể cả với cửa "
          "sổ nhìn lùi — mắt xích liền trước của nó (2019-06-13) LÀNH nên không được phép đi lùi",
          idc_v.get("2020-05-28") == "UNVERIFIED", str(idc_v))
    check("N1b. …nên 3.000.000.000 KHÔNG BAO GIỜ là số phục vụ; số trả về là 300.000.000 từ neo "
          "KHÁC (dòng quý, nay đối chiếu được với mốc AIS lành 2019-06-13)",
          idc["value"] == 300_000_000.0 and idc["anchor_source"] == "ticker_financial"
          and idc.get("uncertified_value") is None,
          f"value={fmt(idc['value'])} method={idc['method']} anchor={idc['anchor_source']}")
    # nạp một lần ở mốc MUỘN rồi cắt lại bằng `asof` trong từng lời gọi — `oshares_at` và
    # `_ais_verdicts` đều tự lọc theo `asof`, nên một cache dùng được cho cả ca 2020 lẫn ca 2021.
    fcache4 = _fetch(["FPT"], "2026-08-13")
    fpt5 = oshares_at(["FPT"], "2020-05-05", _cache=fcache4)["FPT"]
    fpt_v = _ais_verdicts(fcache4[1], "FPT", "2020-05-05")
    fpt_v21 = _ais_verdicts(fcache4[1], "FPT", "2021-01-01")
    check("N2. FPT: dòng AIS 2020-04-06 (461.723.054, ca REFUTED vòng 2) VẪN không chứng nhận "
          "được — cả 5 mốc lùi đều không dựng ra nó",
          fpt_v.get("2020-04-06") == "UNVERIFIED", str(fpt_v))
    check("N2b. …và 461.723.054 không phải số phục vụ: FPT 2020-05-05 trả 681.668.102 — ĐÚNG con "
          "số mà docstring module ghim là sự thật của ngày đó",
          fpt5["value"] == 681_668_102.0 and fpt5["value"] != 461_723_054.0,
          f"value={fmt(fpt5['value'])} method={fpt5['method']} anchor={fpt5['anchor_date']} "
          f"({fpt5['anchor_source']})")
    # LỢI ÍCH ĐO ĐƯỢC của cửa sổ nhìn lùi trên chính chuỗi FPT: 3 dòng AIS LỚN từng bị đánh
    # UNVERIFIED oan (mắt xích liền trước của mỗi dòng là một dòng ESOP có `shares_total_after`
    # hỏng) nay khớp CHÍNH XÁC — không phải "trong dung sai", mà bằng đúng từng cổ phiếu.
    check("N2c. cửa sổ nhìn lùi CỨU chuỗi AIS thật của FPT: 2018-07-16 / 2019-06-24 / 2020-06-22 "
          "đều OK (mỗi dòng lùi ĐÚNG 1 bước qua một dòng ESOP hỏng)",
          all(fpt_v21.get(d) == "OK" for d in ("2018-07-16", "2019-06-24", "2020-06-22"))
          and all(fpt_v21.get(d) == "UNVERIFIED"
                  for d in ("2018-04-23", "2019-04-05", "2020-04-06")),
          str(fpt_v21))
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

    print("== NHÁNH LIVE vs PIT: neo AIS uncertified nhường cho BCTC MỚI HƠN (2026-08-20) ==")
    # HERMETIC — CỐ Ý, không chạm BQ. Các ca dưới kiểm LUẬT RẼ NHÁNH, và luật thì không được rot
    # theo dữ liệu sống (§23 hệ luận 1): hình dạng lấy từ ca thật EVF/HHV/TCB/HAH ngày 2026-08-20
    # nhưng số được ĐÓNG BĂNG ở đây. Ca thật, đo trên BQ sống, nằm ở khối "CÁI GIÁ" ngay dưới.
    def _A(tk, eff, total, delta=None):
        return {"ticker": tk, "event_code": "AIS", "exright_date": None, "effective_date": eff,
                "exercise_ratio": None, "issue_method_name_vi": None, "shares_delta": delta,
                "issue_volumn": None, "listing_date": None, "shares_total_after": total,
                "title": f"AIS {tk} {eff}"}

    def _I(tk, ex, vol=None, ratio=None, method="Trả Cổ tức bằng Cổ phiếu"):
        return {"ticker": tk, "event_code": "ISS", "exright_date": ex, "effective_date": None,
                "exercise_ratio": ratio, "issue_method_name_vi": method, "shares_delta": None,
                "issue_volumn": vol, "listing_date": None, "shares_total_after": None,
                "title": f"ISS {tk} {ex}"}

    def _Q(tk, t, sh):
        return {"ticker": tk, "time": t, "OShares": sh}

    # Neo AIS "uncertified" dựng bằng hình dạng ĐÃ ĐO của cổng: một transition có shares_delta
    # MÂU THUẪN với neo trước (ứng viên (b) dựng được và sai) ⇒ verdict UNVERIFIED. KHÔNG
    # monkeypatch `_ais_certified` — vá cổng đi thì ca này không còn chứng minh được gì.
    #   EVF: AIS ...-12-06 uncertified, BCTC 1,5 NĂM SAU = 760.565.802, không giải thích được.
    LV_ASOF = "2026-08-20"
    EVF_C = ([_Q("EVFX", "2026-07-21", 760_565_802.0)],
             [_A("EVFX", "2023-06-01", 100_000_000.0),
              _A("EVFX", "2024-12-06", 704_248_289.0, delta=1_000_000.0)])
    for tag, want_live in (("PIT", None), ("LIVE", 760_565_802.0)):
        r = oshares_at(["EVFX"], LV_ASOF, _cache=EVF_C, live=(tag == "LIVE"))["EVFX"]
        check(f"LV1{'' if tag == 'PIT' else 'b'}. [{tag}] neo AIS 2024-12-06 CHƯA chứng nhận + "
              f"BCTC 2026-07-21 mới hơn 1,5 năm ⇒ "
              + ("TỪ CHỐI (AIS_UNCERTIFIED) — backtest không đổi một số nào"
                 if tag == "PIT" else "phục vụ BCTC 760.565.802 (FIN_FALLBACK)"),
              r["value"] == want_live
              and r["method"] == ("AIS_UNCERTIFIED" if tag == "PIT" else "FIN_FALLBACK"),
              f"{fmt(r['value'])} [{r['method']}]")
    r = oshares_at(["EVFX"], LV_ASOF, _cache=EVF_C, live=True)["EVFX"]
    check("LV1c. số phục vụ qua nhánh LIVE mang CỜ TRUY VẾT: anchor_verified=False, "
          "fin_anchor_ais_certified=False, fin_branch_live=True — consumer lọc được bằng FIELD, "
          "không phải bằng cách đọc tiếng Việt trong `reason`",
          r.get("anchor_verified") is False and r.get("fin_anchor_ais_certified") is False
          and r.get("fin_branch_live") is True,
          f"verified={r.get('anchor_verified')} cert={r.get('fin_anchor_ais_certified')} "
          f"live={r.get('fin_branch_live')}")

    #   HHV: y hệt, NHƯNG có 1 ISS ex 07-09 nằm TRƯỚC ngày dòng quý 07-31 ⇒ BCTC đã chứa nó rồi.
    #   Đây là ca CHỐNG ĐẾM HAI LẦN: lăn thêm ISS đó lên neo BCTC sẽ ra 601.857.480, sai +4,76%.
    HHV_C = ([_Q("HHVX", "2026-07-31", 574_511_888.0)],
             [_A("HHVX", "2024-01-05", 400_000_000.0),
              _A("HHVX", "2026-05-07", 473_755_528.0, delta=1_000_000.0),
              _I("HHVX", "2026-07-09", vol=27_345_592.0, ratio=0.05)])
    r = oshares_at(["HHVX"], LV_ASOF, _cache=HHV_C, live=True)["HHVX"]
    check("LV2. [CHỐNG ĐẾM HAI LẦN] ISS ex 07-09 nằm TRƯỚC neo BCTC 07-31 ⇒ KHÔNG lăn lại; giá "
          "trị đúng bằng dòng quý 574.511.888, KHÔNG phải 601.857.480",
          r["value"] == 574_511_888.0 and r["events_applied"] == [],
          f"{fmt(r['value'])} +{len(r['events_applied'])} ISS")
    HHV_C2 = (HHV_C[0], HHV_C[1] + [_I("HHVX", "2026-08-14", vol=5_000_000.0)])
    r2 = oshares_at(["HHVX"], LV_ASOF, _cache=HHV_C2, live=True)["HHVX"]
    check("LV2b. CHỨNG MINH NGƯỢC cho LV2 — ISS ex 08-14 nằm SAU neo BCTC 07-31 thì PHẢI được "
          "lăn (nếu không, LV2 xanh chỉ vì hàm không bao giờ lăn gì)",
          r2["value"] == 579_511_888.0 and len(r2["events_applied"]) == 1,
          f"{fmt(r2['value'])} +{len(r2['events_applied'])} ISS")

    #   TCB: neo AIS uncertified nhưng CÒN TƯƠI (15 ngày) ⇒ điều kiện 2 vẫn chặn ở CẢ HAI nhánh.
    TCB_C = ([_Q("TCBX", "2026-07-21", 7_086_240_414.0)],
             [_A("TCBX", "2025-12-01", 7_064_851_739.0),
              _A("TCBX", "2026-08-05", 7_086_240_414.0, delta=1.0)])
    why_pit = (oshares_at(["TCBX"], LV_ASOF, _cache=TCB_C, live=False)["TCBX"]
               .get("rejected_anchors") or [{}])[0].get("fallback_refused", "")
    r_live = oshares_at(["TCBX"], LV_ASOF, _cache=TCB_C, live=True)["TCBX"]
    why_live = (r_live.get("rejected_anchors") or [{}])[0].get("fallback_refused", "")
    check("LV3. [PIT] neo AIS uncertified ⇒ chặn ngay ở điều kiện 1b, KHÔNG bao giờ tới điều "
          "kiện 2 (thứ tự điều kiện là một phần của luật, không phải chi tiết cài đặt)",
          "CHƯA được chứng nhận" in why_pit, why_pit[:90])
    check(f"LV3b. [LIVE] ĐIỀU KIỆN 2 CÒN NGUYÊN — 1b đã nới nên luồng chạy tới đây, và neo AIS "
          f"mới 15 ngày (<= {FIN_FALLBACK_MAX_AIS_AGE_DAYS}) VẪN chặn: sở vừa phát biểu thì "
          f"không có gì để thay thế, kể cả khi phát biểu đó chưa đối chiếu được",
          "còn tươi" in why_live, why_live[:90])

    #   Đi LÙI: neo AIS uncertified MỚI HƠN dòng quý ⇒ điều kiện 3 chặn ở cả hai nhánh.
    BACK_C = ([_Q("BWDX", "2024-01-31", 50_000_000.0)],
              [_A("BWDX", "2023-01-05", 40_000_000.0),
               _A("BWDX", "2026-05-07", 90_000_000.0, delta=1.0)])
    r = oshares_at(["BWDX"], LV_ASOF, _cache=BACK_C, live=True)["BWDX"]
    why = (r.get("rejected_anchors") or [{}])[0].get("fallback_refused", "")
    check("LV4. ĐIỀU KIỆN 3 CÒN NGUYÊN — dòng quý 2024-01-31 CŨ hơn neo AIS 2026-05-07 ⇒ nhánh "
          "LIVE vẫn TỪ CHỐI (rơi về BCTC lúc này là đi LÙI)",
          r["value"] is None and r["method"] == "AIS_UNCERTIFIED" and "đi LÙI" in why,
          f"{fmt(r['value'])} [{r['method']}] {why[:80]}")

    #   HAH thật: dòng quý 02-02 mang số của AIS 05-27, neo AIS trước đó (09-09) đã cũ 146 ngày
    #   ⇒ FIN_FALLBACK phục vụ chính con số look-ahead. Đây là CÁI GIÁ CÓ TỪ 2026-08-19, KHÔNG
    #   phải của nhánh LIVE — pin lại để một hồi quy sau này đổ nhầm tội cho bản vá này.
    HAH_C = ([_Q("HAHX", "2026-02-02", 185_840_401.0)],
             [_A("HAHX", "2025-09-09", 168_861_212.0),
              _A("HAHX", "2026-05-27", 185_840_401.0)])
    hah = {tag: oshares_at(["HAHX"], "2026-03-01", _cache=HAH_C,
                           live=(tag == "LIVE"))["HAHX"] for tag in ("PIT", "LIVE")}
    check("LV5. ca HAH (look-ahead ĐÃ CÓ từ chính sách 2026-08-19) ra Y HỆT nhau ở hai nhánh ⇒ "
          "nhánh LIVE KHÔNG làm ca này tệ thêm; nó cũng không sửa được ca này",
          hah["PIT"]["value"] == hah["LIVE"]["value"] == 185_840_401.0
          and hah["PIT"]["method"] == hah["LIVE"]["method"] == "FIN_FALLBACK",
          f"PIT {fmt(hah['PIT']['value'])} [{hah['PIT']['method']}] · "
          f"LIVE {fmt(hah['LIVE']['value'])} [{hah['LIVE']['method']}]")

    #   Chữ ký RESTATE — cổng look-ahead point-in-time DUY NHẤT còn lại: không có AIS nào TRƯỚC
    #   dòng quý, và dòng quý trùng khít một AIS SAU nó (đã nhìn thấy được tại `asof`).
    RST_C = ([_Q("RSTX", "2026-02-02", 185_840_401.0)],
             [_A("RSTX", "2026-05-27", 185_840_401.0)])
    for tag in ("PIT", "LIVE"):
        r = oshares_at(["RSTX"], LV_ASOF, _cache=RST_C, live=(tag == "LIVE"))["RSTX"]
        why = (r.get("rejected_anchors") or [{}])[0].get("reason", "")
        check(f"LV5{'b' if tag == 'PIT' else 'c'}. [{tag}] CỔNG CHỮ KÝ RESTATE CÒN NGUYÊN — dòng "
              f"quý 02-02 bị LOẠI vì trùng khít AIS 05-27, và neo thắng là AIS chứ KHÔNG phải "
              f"dòng quý (nhánh LIVE không mở đường vòng nào ở đây)",
              "RESTATE" in why and r["anchor_source"] == "corporate_action.AIS"
              and r["anchor_date"] == "2026-05-27",
              f"anchor={r['anchor_date']} ({r['anchor_source']}) · {why[:70]}")

    #   Cổng CHỨNG NHẬN NEO AIS ở cuối `oshares_at` KHÔNG bị `live` chạm tới: không có dòng quý
    #   nào để nhường thì neo AIS uncertified vẫn bị từ chối y như trước.
    NOQ_C = ([], [_A("NOQX", "2023-01-05", 40_000_000.0),
                  _A("NOQX", "2025-01-05", 90_000_000.0, delta=1.0)])
    r = oshares_at(["NOQX"], LV_ASOF, _cache=NOQ_C, live=True)["NOQX"]
    check("LV6. CỔNG CHỨNG NHẬN NEO AIS KHÔNG BỊ NỚI — không có dòng quý để nhường thì neo AIS "
          "uncertified vẫn AIS_UNCERTIFIED dưới live=True (chỉ đổi HÀNH VI KHI TRƯỢT CỔNG, "
          "không xoá cổng)",
          r["value"] is None and r["method"] == "AIS_UNCERTIFIED"
          and r.get("uncertified_value") == 90_000_000.0,
          f"{fmt(r['value'])} [{r['method']}] uncertified={fmt(r.get('uncertified_value'))}")

    check("LV7. neo AIS ĐƯỢC chứng nhận ⇒ hai nhánh trả Y HỆT nhau (nhánh LIVE chỉ đụng đúng "
          "nhánh uncertified, không phải một chính sách khác cho mọi mã)",
          all(oshares_at([t], LV_ASOF, _cache=c, live=False)[t]["value"]
              == oshares_at([t], LV_ASOF, _cache=c, live=True)[t]["value"]
              for t, c in (("TCBX", TCB_C), ("HAHX", HAH_C))))

    print("== ABSORPTION TEST: cửa sổ QUÝ-END → NGÀY CÔNG BỐ (2026-08-20) ==")
    # Lỗ hổng: dòng quý mang NGÀY CÔNG BỐ nhưng số có thể chốt tại QUÝ-END ⇒ ISS trong khoảng
    # giữa có thể ĐÃ hoặc CHƯA nằm trong neo. Vendor KHÔNG nhất quán (HHV gồm, FPT gồm, nhưng
    # không có gì bảo đảm) ⇒ quyết bằng SỐ HỌC `B = issue_volumn / exercise_ratio`, không bằng
    # một luật cắt-ngày thứ hai. Xem `_absorption_test`.

    # (a) CA THẬT, dữ liệu SỐNG — HHV: dòng quý 2026-07-31 ĐÃ gồm cổ tức CP 5% ex 2026-07-09.
    # Đây là ca duy nhất của khối này chạm BQ, cố ý: luật thì hermetic, còn "vendor thật sự có
    # hành xử như thế không" thì phải hỏi dữ liệu thật.
    hhv = oshares_at(["HHV"], "2026-08-19", live=True)["HHV"]
    ab = hhv.get("absorption_test") or {}
    print(f"  HHV 2026-08-19 [live]: {fmt(hhv['value'])} [{hhv['method']}] "
          f"absorption={ab.get('verdict')} rolled={len(ab.get('rolled') or [])}")
    for hy in ab.get("hypotheses", []):
        print(f"     gồm {hy['absorbed_count']}/1 ⇒ kỳ vọng {fmt(hy['expected'])} "
              f"(lệch {hy['rel_diff']*100:+.3f}%)" if hy["expected"] else "     (không dựng được)")
    # ⚠️ AB1 ĐỔI CƠ CHẾ 2026-08-20 (cửa sổ nhìn lùi, job `Taylor_20260820_062330`) — KẾT QUẢ thì
    # không đổi. Trước đó dòng quý HHV 2026-07-31 bị `_explain_quarterly` LOẠI (nó chỉ đối chiếu
    # được với AIS liền trước 2026-05-07, lệch +14,65%), nên câu trả lời đi qua nhánh
    # `FIN_FALLBACK` + absorption test. Nay dòng quý ĐỐI CHIẾU ĐƯỢC qua mốc lùi 2026-04-08
    # (547.166.296 + 27.345.592 = 574.511.888, khớp từng đơn vị) ⇒ neo được nhận thẳng, verified,
    # và absorption test KHÔNG chạy — theo đúng thiết kế của nó ("neo dòng quý ĐÃ verified thì
    # `_explain_quarterly` đã đối chiếu xong; hỏi lại ở đây là hai lời đáp cho một câu hỏi").
    # Bất biến SỐ HỌC được bảo vệ vẫn y nguyên và vẫn được kiểm ở đây: KHÔNG lăn lại ISS ex 07-09.
    check("AB1. [THẬT] HHV 2026-08-19 = 574.511.888 và ISS ex 07-09 KHÔNG bị lăn lại — cắt theo "
          "quý-end sẽ ra 601.857.480 (+4,76%), đếm hai lần",
          hhv["value"] == 574_511_888.0 and hhv["events_applied"] == [],
          f"{fmt(hhv['value'])} [{hhv['method']}] +{len(hhv['events_applied'])} ISS")
    check("AB1b. …và nay nó đi bằng ĐƯỜNG TỐT HƠN: dòng quý 07-31 đối chiếu ĐƯỢC qua mốc lùi ⇒ "
          "anchor_verified=True và absorption test KHÔNG chạy (neo đã verified thì hỏi lại là "
          "hai lời đáp cho một câu hỏi). Trước 2026-08-20 ca này ra FIN_FALLBACK + ABSORBED",
          hhv["anchor_verified"] is True and "absorption_test" not in hhv
          and hhv["anchor_source"] == "ticker_financial",
          f"[{hhv['method']}] verified={hhv['anchor_verified']} "
          f"absorb={'absorption_test' in hhv}")
    # …nên khối này vẫn cần MỘT ca THẬT còn đi qua absorption test, nếu không toàn bộ AB* rớt
    # xuống chỉ còn fixture và không ai biết vendor ngoài đời có hành xử như thế không nữa.
    # VCI @2026-03-01: phát hành riêng lẻ 17,6% ex 2025-12-16 (127.500.000 CP, `listing_date`
    # 2026-12-17 — một năm sau), dòng quý 2026-02-02 = 850.100.000 ĐÃ gồm nó.
    vci = oshares_at(["VCI"], "2026-03-01", live=True)["VCI"]
    ab_r = vci.get("absorption_test") or {}
    hyp = {h["absorbed_count"]: h for h in ab_r.get("hypotheses", [])}
    print(f"  VCI 2026-03-01 [live]: {fmt(vci['value'])} [{vci['method']}] "
          f"{ab_r.get('verdict')} · giả thuyết {[(h['absorbed_count'], h['expected']) for h in ab_r.get('hypotheses', [])]}")
    check("AB1c. [THẬT, (a) ĐÃ GỒM] VCI 2026-03-01: dòng quý 850.100.000 khớp giả thuyết 'đã gồm "
          "1/1' trong EXPLAIN_TOL còn giả thuyết 'chưa gồm' lệch ~17,6% ⇒ ABSORBED, không lăn "
          "lại 127,5 triệu CP. Kiểm QUAN HỆ giữa hai giả thuyết, không chép cứng float của vendor",
          ab_r.get("verdict") == "ABSORBED" and vci["events_applied"] == []
          and abs(hyp.get(1, {}).get("rel_diff", 9)) < EXPLAIN_TOL
          and abs(hyp.get(0, {}).get("rel_diff", 0)) > EXPLAIN_TOL,
          f"{fmt(vci['value'])} verdict={ab_r.get('verdict')} "
          f"rel_diff 0/1 = {hyp.get(0, {}).get('rel_diff')} / {hyp.get(1, {}).get('rel_diff')}")

    # (b) SỐ QUÝ-END: cùng hình dạng HHV nhưng dòng quý = ĐÚNG base vendor khai ⇒ CHƯA gồm sự
    # kiện ⇒ PHẢI lăn. Hermetic: đây là hành vi user cảnh báo, hiện chưa quan sát được ca thật
    # nào trên rổ (xem báo cáo job), nên fixture là cách DUY NHẤT giữ nó không mốc.
    QE_C = ([_Q("QENDX", "2026-07-31", 546_911_840.0)],
            [_A("QENDX", "2026-05-07", 473_755_528.0),
             _I("QENDX", "2026-07-09", vol=27_345_592.0, ratio=0.05)])
    qe = {tag: oshares_at(["QENDX"], LV_ASOF, _cache=QE_C, live=(tag == "LIVE"))["QENDX"]
          for tag in ("PIT", "LIVE")}
    print(f"  QENDX PIT: {fmt(qe['PIT']['value'])} [{qe['PIT']['method']}] · "
          f"LIVE: {fmt(qe['LIVE']['value'])} [{qe['LIVE']['method']}] "
          f"{(qe['LIVE'].get('absorption_test') or {}).get('verdict')}")
    check("AB2. [(b) CHƯA GỒM] dòng quý = ĐÚNG base vendor khai (546.911.840) ⇒ LĂN ISS ex "
          "07-09 bằng issue_volumn ⇒ 574.257.432, không để thiếu 27.345.592 CP",
          qe["LIVE"]["value"] == 574_257_432.0
          and (qe["LIVE"].get("absorption_test") or {}).get("verdict") == "ROLLED"
          and [e["exright_date"] for e in qe["LIVE"]["events_applied"]] == ["2026-07-09"],
          f"{fmt(qe['LIVE']['value'])} +{len(qe['LIVE']['events_applied'])} ISS")
    check("AB2b. NHÁNH PIT KHÔNG ĐỔI MỘT SỐ NÀO — cùng fixture, neo AIS ĐƯỢC chứng nhận nên PIT "
          "cũng phục vụ FIN_FALLBACK, nhưng absorption test không chạy: value = đúng dòng quý, "
          "không có field `absorption_test`",
          qe["PIT"]["value"] == 546_911_840.0 and qe["PIT"]["method"] == "FIN_FALLBACK"
          and "absorption_test" not in qe["PIT"] and qe["PIT"]["events_applied"] == [],
          f"{fmt(qe['PIT']['value'])} [{qe['PIT']['method']}] "
          f"absorb={'absorption_test' in qe['PIT']}")

    # (c) KHÔNG QUYẾT ĐƯỢC — hai kiểu, cả hai phải GIỮ hành vi cũ VÀ nói ra
    AMB_C = ([_Q("AMBX", "2026-07-31", 560_000_000.0)],
             [_A("AMBX", "2026-05-07", 473_755_528.0),
              _I("AMBX", "2026-07-09", vol=27_345_592.0, ratio=0.05)])
    amb = oshares_at(["AMBX"], LV_ASOF, _cache=AMB_C, live=True)["AMBX"]
    ab_a = amb.get("absorption_test") or {}
    print(f"  AMBX: {fmt(amb['value'])} [{amb['method']}] {ab_a.get('verdict')} — "
          f"{(ab_a.get('note') or '')[:100]}")
    check("AB3. [(c) MƠ HỒ] dòng quý 560.000.000 không khớp GIẢ THUYẾT NÀO ⇒ GIỮ hành vi cũ "
          "(không lăn) và gắn WINDOW_AMBIGUOUS",
          amb["value"] == 560_000_000.0 and amb["events_applied"] == []
          and ab_a.get("verdict") == "WINDOW_AMBIGUOUS" and ab_a.get("rolled") == [],
          f"{fmt(amb['value'])} verdict={ab_a.get('verdict')}")
    check("AB3b. …và KHÔNG IM LẶNG: note nêu CẢ HAI con số giả thuyết để người đọc snapshot thấy "
          "khoảng chưa quyết được (546.911.840 ↔ 574.257.432)",
          "546,911,840" in (ab_a.get("note") or "")
          and "574,257,432" in (ab_a.get("note") or ""),
          (ab_a.get("note") or "(trống)")[-110:])
    NOR_C = ([_Q("NORX", "2026-07-31", 560_000_000.0)],
             [_A("NORX", "2026-05-07", 473_755_528.0),
              _I("NORX", "2026-07-09", vol=27_345_592.0, ratio=None)])
    nor = oshares_at(["NORX"], LV_ASOF, _cache=NOR_C, live=True)["NORX"]
    ab_n = nor.get("absorption_test") or {}
    check("AB3c. [(c) THIẾU TRƯỜNG] ISS không có exercise_ratio ⇒ không dựng nổi base ⇒ vẫn "
          "WINDOW_AMBIGUOUS + KHÔNG lăn (KHÔNG được biến thành blocker: value vẫn có số)",
          nor["value"] == 560_000_000.0 and nor["method"] != "UNKNOWN_RATIO"
          and ab_n.get("verdict") == "WINDOW_AMBIGUOUS"
          and "thiếu ratio/issue_volumn" in (ab_n.get("note") or ""),
          f"{fmt(nor['value'])} [{nor['method']}] {(ab_n.get('note') or '')[-60:]}")

    # n = 2: hấp thụ MỘT PHẦN. B_k của sự kiện thứ k chính là số CP sau k−1 sự kiện đầu, nên
    # luật tổng quát hoá thẳng; nếu chỉ test n=1 thì một bản cài chỉ-xét-sự-kiện-cuối vẫn PASS.
    TWO_C = ([_Q("TWOX", "2026-07-31", 510_000_000.0)],
             [_A("TWOX", "2026-05-07", 500_000_000.0),
              _I("TWOX", "2026-07-05", vol=10_000_000.0, ratio=0.02),
              _I("TWOX", "2026-07-20", vol=20_400_000.0, ratio=0.04)])
    two = oshares_at(["TWOX"], LV_ASOF, _cache=TWO_C, live=True)["TWOX"]
    ab_t = two.get("absorption_test") or {}
    print(f"  TWOX: {fmt(two['value'])} {ab_t.get('verdict')} rolled="
          f"{[e['exright_date'] for e in ab_t.get('rolled') or []]}")
    check("AB4. HẤP THỤ MỘT PHẦN (n=2): dòng quý 510.000.000 = base khai của ISS 07-20 ⇒ đã gồm "
          "ISS 07-05, CHƯA gồm ISS 07-20 ⇒ lăn ĐÚNG một sự kiện ⇒ 530.400.000",
          two["value"] == 530_400_000.0
          and [e["exright_date"] for e in ab_t.get("rolled") or []] == ["2026-07-20"],
          f"{fmt(two['value'])} rolled={[e['exright_date'] for e in ab_t.get('rolled') or []]}")

    # CHẶN DƯỚI của cửa sổ: một ISS TRƯỚC AIS gần nhất KHÔNG được kéo vào — đó là đường quay lại
    # lỗi "orphan event cưỡi lên mọi câu trả lời sau" đã đo ở `_unabsorbed_iss`.
    OLD_C = ([_Q("OLDX", "2026-07-31", 546_911_840.0)],
             [_A("OLDX", "2026-05-07", 473_755_528.0),
              _I("OLDX", "2026-05-06", vol=27_345_592.0, ratio=0.05)])
    old = oshares_at(["OLDX"], LV_ASOF, _cache=OLD_C, live=True)["OLDX"]
    check("AB5. CHẶN DƯỚI: ISS ex 2026-05-06 nằm TRƯỚC AIS 2026-05-07 ⇒ ngoài cửa sổ ⇒ không "
          "absorption test, không lăn (dù dòng quý khớp khít giả thuyết 'chưa gồm')",
          old["value"] == 546_911_840.0 and old["events_applied"] == []
          and "absorption_test" not in old,
          f"{fmt(old['value'])} absorb={'absorption_test' in old}")
    # …và ĐỐI CHỨNG NGƯỢC: dời đúng sự kiện đó sang SAU AIS thì nó PHẢI vào cửa sổ và được lăn.
    IN_C = ([_Q("INX", "2026-07-31", 546_911_840.0)],
            [_A("INX", "2026-05-07", 473_755_528.0),
             _I("INX", "2026-05-08", vol=27_345_592.0, ratio=0.05)])
    inn = oshares_at(["INX"], LV_ASOF, _cache=IN_C, live=True)["INX"]
    check("AB5b. ĐỐI CHỨNG NGƯỢC cho AB5 — cùng sự kiện dời sang 2026-05-08 (SAU AIS) thì vào "
          "cửa sổ và ĐƯỢC lăn ⇒ 574.257.432 (nếu không, AB5 xanh chỉ vì cửa sổ luôn rỗng)",
          inn["value"] == 574_257_432.0 and len(inn["events_applied"]) == 1,
          f"{fmt(inn['value'])} +{len(inn['events_applied'])} ISS")
    # SỰ KIỆN KHÔNG ĐỊNH CỠ ĐƯỢC lọt vào `extra`. Giả thuyết của CHÍNH nó là None nên nó không
    # bao giờ được khớp — nhưng một giả thuyết k' nhỏ hơn khớp thì nó vẫn bị kéo theo. Đo thật
    # 2026-08-20 (attempt 2) trên bản chưa vá: `_absorption_test` ném `TypeError: float()
    # argument must be ... not 'NoneType'` từ dòng `note`; và nếu qua được dòng đó thì `_roll`
    # biến nó thành blocker ⇒ một câu trả lời ĐANG CÓ SỐ bị đẩy về `UNKNOWN_RATIO`. Cả hai đều
    # là regression so với hành vi cũ (cũ: không lăn, vẫn có số).
    NOSZ_C = ([_Q("NOSZX", "2026-07-31", 500_000_000.0)],
              [_A("NOSZX", "2026-05-07", 500_000_000.0),
               _I("NOSZX", "2026-07-05", vol=10_000_000.0, ratio=0.02),
               _I("NOSZX", "2026-07-20")])          # không shares_delta / issue_volumn / ratio
    nosz = oshares_at(["NOSZX"], LV_ASOF, _cache=NOSZ_C, live=True)["NOSZX"]
    ab_z = nosz.get("absorption_test") or {}
    print(f"  NOSZX: {fmt(nosz['value'])} [{nosz['method']}] {ab_z.get('verdict')}")
    check("AB7. [(c) KHÔNG ĐỊNH CỠ ĐƯỢC] dòng quý khớp khít 'đã gồm 0/2' NHƯNG sự kiện 07-20 "
          "không có cỡ nào dùng được ⇒ về WINDOW_AMBIGUOUS, KHÔNG lăn, KHÔNG crash và KHÔNG bị "
          "đẩy về UNKNOWN_RATIO (giữ nguyên số cũ 500.000.000)",
          nosz["value"] == 500_000_000.0 and nosz["method"] != "UNKNOWN_RATIO"
          and nosz["events_applied"] == []
          and ab_z.get("verdict") == "WINDOW_AMBIGUOUS"
          and "không có cỡ dùng được" in (ab_z.get("note") or ""),
          f"{fmt(nosz['value'])} [{nosz['method']}] {ab_z.get('verdict')}")
    check("AB7b. ĐỐI CHỨNG NGƯỢC cho AB7 — cùng cửa sổ nhưng sự kiện 07-20 CÓ issue_volumn thì "
          "vẫn ROLLED cả hai ⇒ 530.400.000 (nếu không, AB7 xanh chỉ vì luật chặn mọi ca n=2)",
          oshares_at(["OKZX"], LV_ASOF, live=True, _cache=(
              [_Q("OKZX", "2026-07-31", 500_000_000.0)],
              [_A("OKZX", "2026-05-07", 500_000_000.0),
               _I("OKZX", "2026-07-05", vol=10_000_000.0, ratio=0.02),
               _I("OKZX", "2026-07-20", vol=20_400_000.0, ratio=0.04)]))["OKZX"]["value"]
          == 530_400_000.0)

    # neo AIS / neo dòng quý ĐÃ verified: absorption test KHÔNG được chạm tới
    check("AB6. neo KHÔNG phải dòng quý-chưa-verified ⇒ KHÔNG có field `absorption_test` "
          "(EVF: không ISS nào; TCB nhánh LIVE: neo AIS)",
          "absorption_test" not in oshares_at(["EVFX"], LV_ASOF, _cache=EVF_C, live=True)["EVFX"]
          and "absorption_test" not in oshares_at(["TCBX"], LV_ASOF, _cache=TCB_C,
                                                  live=True)["TCBX"])

    print("== CỬA SỔ NHÌN LÙI của cổng chứng nhận AIS (2026-08-20) ==")
    # HERMETIC — số lấy từ ca thật (HHV / AAA) nhưng ĐÓNG BĂNG ở đây: đây là test của LUẬT, và
    # luật không được rot theo feed sống (§23 hệ luận 1). Ca thật, đo trên BQ, nằm ở N1/N2/N2c.
    #
    # HHVX = hình dạng HHV ngày 2026-08-20, văn bản HOSE 1692/TB-SGDHCM xác nhận 574.511.888:
    #   AIS 04-08 total 547.166.296 → AIS 05-07 total 473.755.528 (RA SAU, total NHỎ HƠN — vendor
    #   xáo trộn thứ tự) → AIS 08-20 total 574.511.888 = 547.166.296 + 27.345.592.
    HHV_A = [_A("HHVX", "2025-09-15", 497_433_003.0, delta=23_677_475.0),
             _A("HHVX", "2026-04-08", 547_166_296.0, delta=49_733_293.0),
             _A("HHVX", "2026-05-07", 473_755_528.0, delta=41_500_000.0)]
    HHV_I = [_I("HHVX", "2025-12-25", vol=49_733_293.0, ratio=0.10,
                method="Quyền mua CP cho Cổ đông hiện hữu"),
             _I("HHVX", "2026-07-09", vol=27_345_592.0, ratio=0.05)]
    HHV_Q = [_Q("HHVX", "2026-07-31", 574_511_888.0)]
    HHV_FEED = HHV_A + [_A("HHVX", "2026-08-20", 574_511_888.0, delta=27_345_592.0)] + HHV_I
    lb_v = _ais_verdicts_from_rows([r for r in HHV_FEED if r["event_code"] == "AIS"], HHV_I)
    print(f"  HHVX verdicts: {lb_v}")
    check("LB1. AIS 2026-08-20 chứng nhận ĐƯỢC qua mốc lùi 2026-04-08 (547.166.296 + 27.345.592 "
          "= 574.511.888), trong khi mốc liền trước 2026-05-07 vẫn UNVERIFIED",
          lb_v.get("2026-08-20") == "OK" and lb_v.get("2026-05-07") == "UNVERIFIED"
          and lb_v.get("2026-04-08") == "OK", str(lb_v))
    lb1 = oshares_at(["HHVX"], LV_ASOF, live=False, _cache=(HHV_Q, HHV_FEED))["HHVX"]
    check("LB1b. …⇒ khi AIS 08-20 lật `executed` (đợt ingest tối 2026-08-20) neo tươi nhất PHỤC "
          "VỤ 574.511.888 [AIS_EXACT] thay vì REGRESS về None. Nhánh PIT (live=False) — cổng "
          "chứng nhận là cổng CHUNG, không phải đặc quyền của nhánh LIVE",
          lb1["value"] == 574_511_888.0 and lb1["method"] == "AIS_EXACT"
          and lb1["anchor_date"] == "2026-08-20",
          f"{fmt(lb1['value'])} [{lb1['method']}] anchor={lb1['anchor_date']}")
    lb2 = oshares_at(["HHVX"], LV_ASOF, live=False, _cache=(HHV_Q, HHV_A + HHV_I))["HHVX"]
    check("LB2. TRƯỚC đợt ingest (chưa có AIS 08-20): dòng quý 2026-07-31 nay ĐỐI CHIẾU ĐƯỢC qua "
          "cùng mốc lùi ⇒ anchor_verified=True, hết residual 'không đối soát được tại 07-31'",
          lb2["value"] == 574_511_888.0 and lb2["anchor_verified"] is True
          and lb2["method"] == "ANCHOR_ONLY" and lb2.get("fin_fallback") is not True,
          f"{fmt(lb2['value'])} [{lb2['method']}] verified={lb2['anchor_verified']}")

    # ── ĐIỀU KIỆN VÀO: mắt xích liền trước LÀNH ⇒ CẤM đi lùi. Đây là cái giữ được bài học AAA/IDC.
    # Số thật của AAA. 56.964.988 + 1.700.000 = 58.664.988 — mốc 2017-01-24 KHỚP CHÍNH XÁC dòng
    # vendor sai 2019-06-03. Nếu cổng "thử mọi AIS trong cửa sổ" thì ca chặn kinh điển này lọt.
    LOCK_A = [_A("LOCKX", "2017-01-24", 56_964_988.0, delta=5_065_000.0),
              _A("LOCKX", "2017-07-28", 59_249_988.0, delta=2_285_000.0),
              _A("LOCKX", "2018-01-09", 83_599_988.0, delta=24_350_000.0),
              _A("LOCKX", "2018-06-06", 167_199_976.0, delta=83_599_988.0),
              _A("LOCKX", "2018-10-18", 171_199_976.0, delta=4_000_000.0),
              _A("LOCKX", "2019-06-03", 58_664_988.0, delta=1_700_000.0)]
    lock_v = _ais_verdicts_from_rows(LOCK_A, [])
    check("LB3. [KHÔNG NỚI LỎNG] AAA 2019-06-03 (58.664.988) VẪN UNVERIFIED: mắt xích liền trước "
          "2018-10-18 (171.199.976) LÀNH ⇒ không được phép đi lùi — dù mốc 2017-01-24 cộng ra "
          "ĐÚNG con số đó (56.964.988 + 1.700.000)",
          lock_v.get("2019-06-03") == "UNVERIFIED" and lock_v.get("2018-10-18") == "OK"
          and 56_964_988.0 + 1_700_000.0 == 58_664_988.0, str(lock_v))
    # …và CHỨNG MINH NGƯỢC ngay tại `_anchor_candidates`: chính điều kiện vào là thứ đang chặn,
    # không phải trùng hợp nào khác. Cùng một `prior`, chỉ đổi verdict của mắt xích liền trước.
    lock_prior = _distinct_ais(LOCK_A[:-1])
    c_lanh = _anchor_candidates(lock_prior, {r["effective_date"]: "OK" for r in lock_prior},
                                "2019-06-03")
    c_gay = _anchor_candidates(lock_prior,
                               {**{r["effective_date"]: "OK" for r in lock_prior},
                                "2018-10-18": "UNVERIFIED"}, "2019-06-03")
    check("LB3b. CHỨNG MINH NGƯỢC cho LB3 — cùng chuỗi, chỉ đổi verdict mắt xích liền trước: "
          "LÀNH ⇒ 1 mốc (luật cũ y nguyên); GÃY ⇒ 2 mốc (mở thêm 2018-06-06). Nếu không có ca "
          "này, LB3 xanh có thể chỉ vì cửa sổ không bao giờ mở",
          [r["effective_date"] for r in c_lanh] == ["2018-10-18"]
          and [r["effective_date"] for r in c_gay] == ["2018-10-18", "2018-06-06"],
          f"lành={[r['effective_date'] for r in c_lanh]} · "
          f"gãy={[r['effective_date'] for r in c_gay]}")

    # ── MỐC LÙI PHẢI TỰ NÓ ĐÃ CHỨNG NHẬN, và dừng ở cái LÀNH ĐẦU TIÊN.
    # ⚠️ Mắt xích LIỀN TRƯỚC vẫn luôn là mốc mặc định dù verdict của nó là gì — đó là luật CŨ và
    # nó không đổi (bản trước 2026-08-20 cũng đối chiếu với nó vô điều kiện). Cái phải chứng minh
    # ở đây là MỐC LÙI THÊM — thứ duy nhất bản vá này thêm vào — phải TỰ NÓ đã chứng nhận.
    CHAIN_A = [_A("CHAINX", "2026-01-05", 100_000_000.0),                  # NO_PRIOR
               _A("CHAINX", "2026-02-05", 999_999_999.0, delta=1_000_000.0),   # UNVERIFIED
               _A("CHAINX", "2026-03-05", 555_555_555.0, delta=1_000_000.0),   # UNVERIFIED
               _A("CHAINX", "2026-04-05", 1_000_999_999.0, delta=1_000_000.0)]
    chain_v = _ais_verdicts_from_rows(CHAIN_A, [])
    check("LB4. mốc lùi thêm phải TỰ chứng nhận: 2026-04-05 (1.000.999.999) khớp KHÍT mốc lùi "
          "2026-02-05 (999.999.999 + 1.000.000) nhưng CHÍNH mốc đó CHƯA kiểm ⇒ bỏ qua, đi tiếp "
          "tới mốc lành đầu tiên (2026-01-05) và KHÔNG khớp ⇒ UNVERIFIED. Bắc cầu trên nền "
          "không kiểm chính là vòng tròn cổng này tồn tại để chặn",
          chain_v.get("2026-04-05") == "UNVERIFIED"
          and chain_v.get("2026-02-05") == "UNVERIFIED"
          and 999_999_999.0 + 1_000_000.0 == 1_000_999_999.0, str(chain_v))
    check("LB4b. CHỨNG MINH NGƯỢC cho LB4 — cùng chuỗi, chỉ đánh dấu 2026-02-05 là ĐÃ chứng "
          "nhận: nó lọt vào danh sách mốc và phép khớp thành công. Nếu không có ca này, LB4 "
          "xanh có thể chỉ vì phép khớp sai chứ không phải vì cổng chặn",
          [r["effective_date"] for r in _anchor_candidates(
              _distinct_ais(CHAIN_A[:-1]),
              {"2026-01-05": "NO_PRIOR", "2026-02-05": "OK", "2026-03-05": "UNVERIFIED"},
              "2026-04-05")] == ["2026-03-05", "2026-02-05"]
          and _ais_reconciles(CHAIN_A[1], 1_000_999_999.0, 1_000_000.0, [], "2026-04-05"))

    # ── TRẦN THỜI GIAN của cửa sổ, và đối chứng ngược cho nó.
    FAR_A = [_A("FARX", "2023-01-05", 100_000_000.0),
             _A("FARX", "2026-02-05", 999_999_999.0, delta=1_000_000.0),
             _A("FARX", "2026-03-05", 101_000_000.0, delta=1_000_000.0)]
    NEAR_A = [_A("NEARX", "2025-01-05", 100_000_000.0),
              _A("NEARX", "2026-02-05", 999_999_999.0, delta=1_000_000.0),
              _A("NEARX", "2026-03-05", 101_000_000.0, delta=1_000_000.0)]
    far_v = _ais_verdicts_from_rows(FAR_A, [])
    near_v = _ais_verdicts_from_rows(NEAR_A, [])
    check(f"LB5. TRẦN {AIS_LOOKBACK_MAX_DAYS} NGÀY chặn thật: mốc lành cách 1.155 ngày ⇒ ngoài "
          f"cửa sổ ⇒ UNVERIFIED; cùng chuỗi với mốc cách 424 ngày ⇒ OK (đối chứng ngược — nếu "
          f"không có nó, LB5 xanh có thể chỉ vì phép khớp sai)",
          far_v.get("2026-03-05") == "UNVERIFIED" and near_v.get("2026-03-05") == "OK",
          f"xa={far_v.get('2026-03-05')} · gần={near_v.get('2026-03-05')}")

    # ── MỐC LÙI CŨNG ÁP CHO `_unabsorbed_iss` (cùng ranh giới "AIS liền trước") ──────────────
    # Hình dạng TCB, đóng băng: AIS 2024-08-06 (thưởng 1:1) → AIS 2024-11-21 RA SAU nhưng total
    # NHỎ HƠN (chốt trên nền cũ) → AIS 2025-12-01. Nếu `_unabsorbed_iss` lấy `prev` = 2024-11-21
    # thì `delta` = 3.542.340.928 không khớp ISS nào ⇒ ESOP ex 2025-08-04 (21.388.675 CP) bị coi
    # là ĐÃ niêm yết ⇒ dòng quý 7.086.240.414 bị LOẠI và câu trả lời tụt về 7.064.851.739 (−0,30%).
    TCBS_A = [_A("TCBSX", "2023-08-30", 3_517_238_514.0, delta=6_323_716.0),
              _A("TCBSX", "2024-08-06", 7_045_021_622.0, delta=3_522_510_811.0),
              _A("TCBSX", "2024-11-21", 3_522_510_811.0, delta=5_272_297.0),
              _A("TCBSX", "2025-12-01", 7_064_851_739.0, delta=19_830_117.0)]
    TCBS_I = [_I("TCBSX", "2023-11-20", vol=5_272_297.0, ratio=0.0, method="Phát hành cho CBCNV"),
              _I("TCBSX", "2024-06-20", vol=3_522_510_811.0, ratio=1.0,
                 method="Cổ phiếu thưởng"),
              _I("TCBSX", "2024-11-30", vol=19_830_117.0, ratio=0.002815,
                 method="Phát hành cho CBCNV"),
              _I("TCBSX", "2025-08-04", vol=21_388_675.0, ratio=0.0030275,
                 method="Phát hành cho CBCNV")]
    TCBS_Q = [_Q("TCBSX", "2026-01-22", 7_086_240_414.0)]
    lb6 = oshares_at(["TCBSX"], "2026-03-01", live=False,
                     _cache=(TCBS_Q, TCBS_A + TCBS_I))["TCBSX"]
    _uni_no = [e["exright_date"] for e in _unabsorbed_iss(TCBS_A, TCBS_I, "2026-01-22")]
    _uni_yes = [e["exright_date"] for e in _unabsorbed_iss(
        TCBS_A, TCBS_I, "2026-01-22", _ais_verdicts_from_rows(TCBS_A, TCBS_I))]
    print(f"  TCBSX 2026-03-01: {fmt(lb6['value'])} [{lb6['method']}] neo={lb6['anchor_date']} "
          f"({lb6['anchor_source']}) verified={lb6['anchor_verified']}")
    check("LB6. `_unabsorbed_iss` cũng lùi qua mắt xích gãy: ESOP ex 2025-08-04 hiện ra là CHƯA "
          "niêm yết ⇒ dòng quý 7.086.240.414 ĐỐI CHIẾU ĐƯỢC (7.064.851.739 + 21.388.675) ⇒ phục "
          "vụ ĐÚNG 7.086.240.414 thay vì 7.064.851.739 (−0,30%)",
          lb6["value"] == 7_086_240_414.0 and lb6["anchor_verified"] is True
          and lb6["anchor_source"] == "ticker_financial",
          f"{fmt(lb6['value'])} [{lb6['method']}] verified={lb6['anchor_verified']}")
    check("LB6b. CHỨNG MINH NGƯỢC cho LB6 — KHÔNG truyền `verdicts` thì `_unabsorbed_iss` giữ "
          "NGUYÊN luật cũ (mốc = AIS liền trước) và ESOP 2025-08-04 bị coi là đã niêm yết. "
          "Mặc định của hàm không bao giờ tự nới",
          _uni_no == [] and _uni_yes == ["2025-08-04"],
          f"không verdicts={_uni_no} · có verdicts={_uni_yes}")

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

    # CÁI GIÁ RIÊNG của nhánh LIVE, đo cùng ngày trên cùng rổ: đúng MỘT mã look-ahead mới.
    kbc = oshares_at(["KBC"], "2026-03-01", live=True)["KBC"]
    kbc_pit = oshares_at(["KBC"], "2026-03-01", live=False)["KBC"]
    check("F6b. [CÁI GIÁ NHÁNH LIVE] KBC 2026-03-01: PIT từ chối, LIVE phục vụ 941.754.759 = "
          "ĐÚNG số của AIS 2026-06-25 (look-ahead). Đây là mã DUY NHẤT nhánh LIVE thêm vào tập "
          "look-ahead trên rổ 263 mã — đổi lại 21 mã được phủ. Pin để lần siết/nới sau nhìn thấy "
          "cả hai vế",
          kbc_pit["value"] is None and kbc["value"] == 941_754_759.0
          and kbc["method"] == "FIN_FALLBACK",
          f"PIT {fmt(kbc_pit['value'])} [{kbc_pit['method']}] · "
          f"LIVE {fmt(kbc['value'])} [{kbc['method']}]")

    print("== Bất biến chung: value is None ⟺ method ∈ {UNKNOWN_RATIO, NO_ANCHOR, AIS_UNCERTIFIED} ==")
    every = [h, m, idc, fpt5, tcb_boom, vre, vre_off, na, cc1,
             h5, h5b, hh1, hh2, kbc, kbc_pit, lb1, lb2, lb6, vci,
             hhv, amb, nor, two, old, inn, *qe.values(),
             *cost.values(), *ctrl.values(), *series.values()]
    check("10. không bao giờ trả số kèm nhãn 'không biết', và ngược lại",
          all((r["value"] is None)
              == (r["method"] in ("UNKNOWN_RATIO", "NO_ANCHOR", "AIS_UNCERTIFIED"))
              for r in every))
    served_ais = [r for r in every
                  if r["value"] is not None and r.get("anchor_source") == "corporate_action.AIS"]
    # gieo sẵn feed HERMETIC: `_corp_of` đi hỏi BQ, mà `HHVX` là mã fixture nên không có ở đó.
    # Gieo bằng CHÍNH feed đã dựng ⇒ bất biến 10b vẫn kiểm thật ca này, không phải miễn trừ nó.
    _corp_memo = {"HHVX": HHV_FEED}

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
