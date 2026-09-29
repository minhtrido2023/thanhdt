#!/usr/bin/env python3
"""Layer 2 — REPAIR an incomplete vendor back-adjustment from our own corp-action table.

WIRED, ON BY DEFAULT since 2026-09-28 (quant-skeptic CONFIRMED, round 2, job
Taylor_20260928_111625 — round 1 found 2 real edge-case bugs, chainffill + selfband, both fixed
and re-verified before this default flipped). Kill switch: `MIKE_CLOSE_REPAIR=0`. Every number it
changes is an investor-facing tỉ suất (`coding_guidelines` §21) — the same CONFIRMED-verdict gate
applies to any FUTURE change to this file, not just the initial go-live.

WHAT IT FIXES. `tav2_bq.ticker.Close` is the vendor's back-adjusted close. Its cumulative factor
`r = Price/Close` is supposed to be constant between two consecutive ex-dates. Measured
2026-09-27: for every one of the 15 computable tickers with a price-adjusting ex-date in
2026-09-19..09-25, the factor reached only the last 4 cum sessions and the whole earlier history
sits in the pre-event frame (FPT −9,09%, VPB −20,66%). That is not drift, it is exactly one
missing factor. `report_return_gate.paper_entry_gate` correctly refuses to publish a return
computed off such a series — and stays stuck until the vendor rewrites history.

WHAT IT DOES. For one price row `(date, Close, Price)` it recomputes the factor from
`tav2_bq.corporate_action` and, when the vendor's factor is materially smaller, returns
`Close_self = Price / r_pred` with `adj_source="self_computed"`. Design rules, all load-bearing:

  * FAIL-CLOSED, NEVER GUESS. If ANY ex-date in the window cannot be turned into a factor
    (rights issue — the subscription price is not a column, and `ref_price` is NULL on all 2.418
    rows since 2025-01-01; or an `exercise_ratio`/`value_per_share` we cannot parse; or the last
    cum `Price` fails the ffill band guard) the row is returned UNTOUCHED with a reason. The
    existing gate then keeps blocking, which is the correct outcome: a fallback that silently
    used 1,0 for a rights issue would manufacture a clean answer out of a data gap.
  * VENDOR STAYS THE DEFAULT. Agreement inside `TOL` (0,3%) leaves the row alone. 0,3% and not
    0,1% because DXG carries an unexplained −0,17% residual on a 14% bonus over 95 sessions;
    below 0,3% this method cannot tell a defect from vendor convention.
  * THE WINDOW ENDS AT THE SERIES, NOT AT TODAY. `r_pred` multiplies ex-dates in
    `(row_date, series_max_date]`. Using CURRENT_DATE instead would apply the factor of an
    ex-date the price series has not reached yet and INVENT a defect on a healthy row.
  * SAME-DAY EVENTS COMBINE INSIDE THE EXCHANGE FORMULA, THEY DO NOT MULTIPLY.
        P_ref = (P_cum − D_total) / (1 + q_total)   ⇒   f = (1 + q_total)·P_cum/(P_cum − D_total)
    Multiplying per-event factors is wrong by a measurable amount and produces FALSE ACCUSATIONS:
    GEX 2026-05-05 (bonus 20% + stock dividend 25%) → 1,450 matches the vendor's 1,450191
    while 1,20×1,25 = 1,500 is −3,32% off; DGC 2026-09-14 (cash 3.000 + 5.000 on raw 46.750) →
    46750/38750 = 1,206452 matches to 6 decimals while the product gives 1,196544, +0,83% off.
    Both are pinned in the selfcheck.
  * THE ffill BAND GUARD MUST LIFT THE BAND, NOT THE PRICE. `High`/`Low` live in the ADJUSTED
    frame and `Price` does not, so testing `Low <= Price <= High` directly flags every healthy
    pre-event row (FPT 2025-06-11: Price=117.900 vs adjusted band [97.750, 99.520]). The band is
    lifted into the raw frame with the ratio of a NEIGHBOUR row — never the suspect row, where
    `Price/Close` is precisely the quantity under suspicion.
  * A CASH LEG NEEDS A PRICE, A PURE STOCK LEG DOES NOT. `f = 1 + q` is computable even when the
    price row is unusable; only the cash denominator depends on `P_cum`.

Taxonomy is REUSED from `corp_action_lib.is_price_adjusting` (ESOP / private placement do not move
price). `daily_nav_snapshot`'s multipliers are deliberately NOT reused — they are QUANTITY
multipliers and return 1,0 for `DIV` by design, correct for share counts and silently wrong here.
"""
from __future__ import annotations

import os
from collections import defaultdict
from dataclasses import dataclass, field

from corp_action_lib import is_price_adjusting   # pure predicate, no BQ call — safe to import here

TOL = 0.003          # vendor/self agreement band; see module docstring
FACTOR_EPS = 1e-6
ENV_FLAG = "MIKE_CLOSE_REPAIR"


def enabled() -> bool:
    """True unless explicitly disabled. Default ON since the quant-skeptic CONFIRMED verdict
    (round 2, 2026-09-28, job Taylor_20260928_111625, after both fixed bugs — chainffill,
    selfband — were re-verified). Set `MIKE_CLOSE_REPAIR=0` as the kill switch to force it off.
    """
    return os.environ.get(ENV_FLAG, "1") != "0"


@dataclass
class Repair:
    """Verdict for ONE price row. `close` is what the caller should use."""
    ticker: str
    date: str
    close: float
    price: float
    adj_source: str                      # "vendor" | "self_computed"
    r_obs: float | None = None
    r_pred: float | None = None
    dev: float | None = None
    reason: str = ""
    uncomputable_ex: tuple = ()
    notes: tuple = field(default=())

    @property
    def repaired(self) -> bool:
        return self.adj_source == "self_computed"


# ------------------------------------------------------------------ factor maths

def _lift_neighbour(series: list, i: int) -> tuple:
    """(neighbour, chained) — nearest row before `series[i]` whose own Price DIFFERS from
    `series[i]`'s. Walks back past any run of rows sharing that exact Price (a ffill carry-over
    signature) instead of trusting the immediate predecessor: a lift ratio computed off a
    neighbour that shares bar's own raw Price cannot tell a frozen bar from a healthy one — the
    ratio would just normalize the freeze away — so such a neighbour is never usable as the
    reference, no matter how many sessions the run spans. `chained` is True iff >=1 row was
    skipped, i.e. bar's Price repeats at least the immediately preceding session.
    """
    price = series[i]["price"]
    j = i - 1
    chained = False
    while j >= 0 and series[j]["price"] == price:
        j -= 1
        chained = True
    return (series[j] if j >= 0 else None), chained


def _band_lifted_suspect(bar: dict, series: list, i: int) -> bool:
    """True when `bar` (= `series[i]`) cannot be a real trade of that session (ffill signature).

    A raw Price that repeats one or more sessions immediately before it IS the ffill signature
    this guard exists to catch — no neighbour ratio computed from inside that same frozen run can
    be trusted to test it (see `_lift_neighbour`), so any such chain is refused outright, with no
    band test needed. Otherwise lift the adjusted `High`/`Low` band into the raw frame with the
    ratio of the nearest row whose Price genuinely differs. No prior row at all, or no band → we
    cannot test, so we do NOT accuse: return False and let the caller's other guards speak.
    (Refusing here instead would fail-close on every first row of a window.)
    """
    hi, lo = bar.get("high") or 0.0, bar.get("low") or 0.0
    if hi <= 0 or lo <= 0 or i <= 0:
        return False
    neighbour, chained = _lift_neighbour(series, i)
    if chained:
        return True
    if not neighbour or not neighbour.get("close") or neighbour["close"] <= 0:
        return False
    lift = neighbour["price"] / neighbour["close"]
    return not (lo * lift * (1 - 1e-9) <= bar["price"] <= hi * lift * (1 + 1e-9))


def group_factor(ex: str, evs: list, series: list) -> tuple:
    """(factor, note) for ALL price-adjusting events sharing ONE ex-date. None ⇒ uncomputable.

    `series` must be ascending by date and must reach back past `ex` so the last cum bar exists.
    """
    q_total, d_total, kinds = 0.0, 0.0, []
    for ev in evs:
        code = ev.get("event_code")
        method = (ev.get("issue_method_name_vi") or "").strip()
        if code == "ISS":
            if method == "Quyền mua CP cho Cổ đông hiện hữu":
                return None, (f"{ex} ISS quyền mua: subscription price is not a column of "
                              f"corporate_action (ref_price NULL on all rows) → unknowable")
            try:
                ratio = float(ev.get("exercise_ratio") or 0.0)
            except (TypeError, ValueError):
                return None, f"{ex} ISS exercise_ratio unparsable: {ev.get('exercise_ratio')!r}"
            if ratio <= 0:
                return None, f"{ex} ISS exercise_ratio <= 0"
            q_total += ratio
            kinds.append(f"ISS {method or '?'} {ratio:g}")
        elif code == "DIV":
            try:
                dps = float(ev.get("value_per_share") or 0.0)
            except (TypeError, ValueError):
                return None, f"{ex} DIV value_per_share unparsable: {ev.get('value_per_share')!r}"
            if dps <= 0:
                return None, f"{ex} DIV value_per_share <= 0"
            d_total += dps
            kinds.append(f"DIV {dps:g}đ")
        else:
            return None, f"{ex} unsupported event_code={code!r}"

    desc = " + ".join(kinds)
    if d_total <= 0:
        return 1.0 + q_total, f"{ex} {desc} → f={1.0 + q_total:.6f} (no cash leg, no price needed)"

    idxs = [i for i, b in enumerate(series) if b["d"] < ex]
    if not idxs:
        return None, f"{ex} {desc}: no cum session inside the price window"
    i = idxs[-1]
    bar = series[i]
    if _band_lifted_suspect(bar, series, i):
        return None, (f"{ex} {desc}: last cum bar {bar['d']} Price={bar['price']:,.0f} outside the "
                      f"raw-lifted [Low,High] band → ffill suspect, refuse")
    p_cum = bar["price"]
    if p_cum - d_total <= 0:
        return None, f"{ex} {desc}: cash {d_total:,.0f} >= raw price {p_cum:,.0f}"
    f = (1.0 + q_total) * p_cum / (p_cum - d_total)
    return f, f"{ex} {desc} on raw {p_cum:,.0f} ({bar['d']}) → f={f:.6f}"


def dedup_same_term(evs: list) -> tuple:
    """(kept, dropped_notes) — collapse rows identical on the ECONOMIC term only.

    `corporate_action` legitimately holds several tranches on one ex-date and those must SUM, but
    a re-stated amendment of the same tranche must not double-count. Identical
    (code, ratio, dps) rows are indistinguishable from one another, so treating them as one term
    is the conservative read — and it is what matched the vendor on every control event that had
    duplicates.
    """
    seen, kept, dropped = set(), [], []
    for ev in evs:
        key = (ev.get("event_code"), str(ev.get("exercise_ratio")), str(ev.get("value_per_share")))
        if key in seen:
            dropped.append(f"{ev.get('exright_date')} {ev.get('event_code')}: "
                           f"identical economic term repeated, dropped")
            continue
        seen.add(key)
        kept.append(ev)
    return kept, tuple(dropped)


def factor_after(date: str, events: list, series: list, series_max: str) -> tuple:
    """(r_pred, uncomputable_ex, notes) — product of factors for ex-dates in (date, series_max].

    `series_max` and not today's date: an ex-date the price series has not reached cannot be in
    the vendor's `Close` yet, so including it would invent a defect on a healthy row.
    """
    by_ex = defaultdict(list)
    notes = []
    for ev in events:
        ex = ev.get("exright_date")
        if not ex or not (date < ex <= series_max):
            continue
        if not is_price_adjusting(ev):
            notes.append(f"{ex} {ev.get('event_code')} "
                         f"{(ev.get('issue_method_name_vi') or '').strip()!r}: NON price-adjusting")
            continue
        by_ex[ex].append(ev)

    r, uncomputable = 1.0, []
    for ex in sorted(by_ex):
        kept, dropped = dedup_same_term(by_ex[ex])
        notes.extend(dropped)
        f, note = group_factor(ex, kept, series)
        notes.append(note)
        if f is None:
            uncomputable.append(ex)
        else:
            r *= f
    return r, tuple(uncomputable), tuple(notes)


# ------------------------------------------------------------------ independent price cross-check
#
# WHY THIS EXISTS (Việc nhỏ 3, 2026-09-29, job Taylor_20260929_032553). The repaired-series
# monotonicity check (`paper_entry_adjust._repaired_series_violation`) only catches the direction
# where `corporate_action` UNDER-states an event (r_pred too LOW makes the repaired ratio series
# non-monotone and gets caught). The mirror-image defect — `corporate_action` OVER-states an event
# (wrong exercise_ratio/value_per_share, too HIGH) — makes `r_pred` too HIGH, `Close_self` too LOW,
# the reported return FLATTERED, and the repaired series stays perfectly monotone: the invariant is
# blind to it by construction (quant-skeptic, job Taylor_20260929_022438, killer_objection,
# mutation-tested with exercise_ratio 0,15 and 0,104 against FPT's true 0,10, neither caught).
#
# THE ONLY INDEPENDENT GROUND TRUTH AVAILABLE is what actually traded on the ex-date session —
# `tav2_bq.ticker.Price` (raw), which neither `group_factor`'s formula nor the vendor's `Close`
# touches. If `f` is right, the raw step P_cum → P_ex must land close to it; if `corporate_action`
# is wrong, the two disagree regardless of which direction the error runs.
#
# CALIBRATION — RE-MEASURED post-fix (2026-09-29, second pass). The first pass measured |dev| by
# filtering raw BQ rows directly, WITHOUT running the real fail-closed guards below; quant-skeptic
# (job Taylor_20260929_032553, round 1, REFUTED) caught that the ex-date bar's ffill guard, as
# first written, lifted its ADJUSTED band with the CUM bar's Price/Close — the wrong side of the
# event boundary — so on real data (406-event spot sample) it refused ~94% of events as
# "ffill-suspect", including the FPT case this check exists for, and the selfcheck passed only
# because its fixture zeroed High/Low, bypassing the guard entirely. Fixed by dropping the band
# test for the ex-date bar and keeping only `_lift_neighbour`'s `chained` flag (a raw-Price-repeats
# check that compares raw to raw, so it is valid on EITHER side of an event boundary) — see the
# comment inside `price_crosscheck` at the `chained_ex` check.
#
# Re-measured THROUGH THE FIXED PRODUCTION FUNCTION `price_crosscheck_after` itself (not a
# standalone filter) — committed, re-runnable version: `price_xcheck_calibration.py` (Việc B,
# dispatch Taylor_20260929_042515, 2026-09-29; replaces an earlier /tmp-only measurement per §8c).
# `tav2_bq.corporate_action` × `tav2_bq.ticker`, ALL price-adjusting DIV/ISS(bonus|stock-dividend)
# events 2025-01-01..2026-09-15 (n=1.587 candidates with a price series covering the ex-date, out
# of 1.917 total pairs — 314 tickers this measurement script itself could not fetch ANY
# `tav2_bq.ticker` row for, a gap in DATA COVERAGE, not in `price_crosscheck`; 16 more with the
# ex-date beyond the fetched price window). MẪU SỐ của 4 nhóm dưới đây là CHÍNH n=1.587, cộng khớp
# chẵn (script tự `assert` điều này mỗi lần chạy):
#   - tested=782 (49,3%) reach a |dev| verdict — the set reported below.
#   - ffill_cum_band=681: the CUM bar itself is refused by `_band_lifted_suspect` (raw Price
#     outside the raw-lifted [Low,High] band) — corrected label, 2026-09-29: the first pass
#     (round-2 /tmp measurement) called this bucket "681 uncomputable (rights issue/unparsable/
#     cash≥price)" by GUESSING from the category NAME instead of reading the actual `note` text;
#     re-verified against the real `note` strings and 100% of these 681 say "outside the
#     raw-lifted" — none are rights-issue/unparsable/cash≥price. True formula-uncomputable count
#     in this window is 0 (see below) — this SQL only fetches DIV/ISS-bonus, so 0 rights-issue is
#     expected by construction, not evidence the branch is dead in general.
#   - ffill_chained=121: `_lift_neighbour`'s `chained` (raw Price repeats the prior session,
#     either on the CUM bar or the EX-DATE bar — the latter is one of Việc A's 3 §29 labels).
#   - uncomputable_formula=0: `group_factor` returning None for a genuine formula reason (rights
#     issue/unparsable/cash≥price) — zero in-sample, kept as a distinct bucket since it is real
#     `group_factor` behavior that could be nonzero on a different event mix.
#   - no_cum_bar_in_window=3: no session before the ex-date inside the fetched price window.
# Among the 782 TESTED events, |dev| — median 1,41%, p75 2,91%, p90 5,64%, p95 8,31%, p97 9,84%,
# p99 12,60%, max 23,40% — confirms the first pass's conclusion despite the bug fix changing WHICH
# events get tested: this is genuine same-day trading noise around a corp-action step (comparing a
# SINGLE session's raw close to a formula has an irreducible floor of several percent that a
# MULTI-session cumulative comparison, what `TOL` above guards, does not have), not vendor/data-
# quality noise. Reusing `TOL=0,3%` here would flag ~100% of tested events — useless.
#
# PRICE_XCHECK_TOL = 0,20 (20%): false-positive rate on the 782 tested events is 0,13% (1/782;
# 2,81%/22 at 10%, 0,38%/3 at 15%) — a coarse, GROSS-error screen. It reliably catches an
# order-of-magnitude-wrong exercise_ratio/value_per_share (decimal slip, wrong/duplicated event: a
# 0,10→1,0 fat-finger on the real FPT market data below IS caught, dev=−46,0%) but — DISCLOSED
# LIMIT, same class as the monotonicity check's one-directional blind spot — it CANNOT distinguish
# quant-skeptic's 0,15/0,104 micro-mutations (4,5%/0,36% shift in `f`; on the real FPT data 0,15
# gives dev=−6,1%) from ordinary single-day noise (already ~1,4% at the median). Catching those
# would need a per-ticker volatility-adjusted statistic — out of scope for this pass, flagged here
# so it is not forgotten.
#
# LỆNH TÁI LẬP: source wc_env.sh && python3 price_xcheck_calibration.py (đo lần đầu 2026-09-29;
# chi phí BQ ~28MB, xem VINTAGE trong docstring của script đó).
PRICE_XCHECK_TOL = 0.20


@dataclass
class PriceCrossCheck:
    """Independent GROSS-error screen for ONE ex-date group — see the comment block above for the
    calibration evidence and its disclosed blind spot. `mismatch=True` is the only actionable
    signal; `mismatch=False` with `f_formula`/`r_real`/`dev` left `None` means "could not test"
    (uncomputable formula, no usable cum/ex bar, ffill-suspect), NEVER "tested and it's fine" — the
    caller must not read an untested row as clean.
    """
    ex: str
    f_formula: float | None
    r_real: float | None
    dev: float | None
    mismatch: bool
    note: str = ""


def _last_cum_index(series: list, ex: str) -> int | None:
    """Index of the last bar strictly before `ex` — the SAME rule `group_factor` uses internally
    for its own cum-bar lookup, duplicated rather than extracted: `group_factor` returns only the
    factor/note (not the index) and is not to be changed for this (Việc nhỏ 3 dispatch constraint:
    additive only, existing functions untouched)."""
    idxs = [i for i, b in enumerate(series) if b["d"] < ex]
    return idxs[-1] if idxs else None


def price_crosscheck(ex: str, kept_evs: list, series: list,
                     tol: float = PRICE_XCHECK_TOL) -> PriceCrossCheck:
    """One ex-date's formula factor vs the REAL raw price step across it — see block above.

    `kept_evs` = events for this ex-date, already deduped by `dedup_same_term` (same contract as
    `group_factor`, reused here UNMODIFIED to get `f` — same-day combos are therefore checked
    against the correct combined exchange formula, never a multiplied-per-event approximation).
    Fail-closed like every other check in this module: any bar that cannot be trusted (uncomputable
    formula, no cum/ex bar in the window, ffill-suspect per `_band_lifted_suspect`) returns
    `mismatch=False` with a note explaining why — never a guessed verdict.
    """
    f, note_f = group_factor(ex, kept_evs, series)
    if f is None:
        return PriceCrossCheck(ex, None, None, None, False, note_f)

    i_cum = _last_cum_index(series, ex)
    if i_cum is None:
        return PriceCrossCheck(ex, f, None, None, False, f"{ex}: không có phiên cum trong cửa sổ")
    i_ex = next((i for i, b in enumerate(series) if b["d"] >= ex), None)
    if i_ex is None:
        return PriceCrossCheck(ex, f, None, None, False,
                               f"{ex}: chuỗi giá chưa tới phiên ex-date, chưa cross-check được")

    if _band_lifted_suspect(series[i_cum], series, i_cum):
        return PriceCrossCheck(ex, f, None, None, False,
                               f"{ex}: phiên cum {series[i_cum]['d']} nghi ffill, không cross-check")
    # KHÔNG dùng `_band_lifted_suspect` cho phiên ex-date: hàm đó lift band ADJUSTED của bar bằng
    # tỉ lệ Price/Close của một NEIGHBOUR PHÍA TRƯỚC ex-date — đúng khi bar và neighbour cùng một
    # "khung" (dùng trong `group_factor` cho chính phiên cum, và trong `repair_row`'s own self-
    # check cho một dòng NẰM TRONG cùng cửa sổ vendor còn stale). Phiên ex-date lại nằm NGAY BÊN
    # KIA của bước nhảy: tỉ lệ Price/Close của neighbour phía trước CHÍNH LÀ hệ số của sự kiện đang
    # xét (hoặc một artefact vendor tạm thời khác), nên áp nó vào band của phiên SAU sự kiện là lấy
    # band một khung, lift bằng hệ số của khung kia — sai khung, không phải bằng chứng ffill thật
    # (quant-skeptic REFUTED bản đầu vì lỗi này: band lift làm ~94% sự kiện thật — kể cả chính ca
    # FPT — bị từ chối oan "nghi ffill", bao gồm cả 3 mutation trong selfcheck). Chỉ tái dùng phần
    # AN TOÀN xuyên biên sự kiện của cùng cơ chế: `_lift_neighbour`'s `chained` — Price LẶP LẠI
    # đúng giá trị của (các) phiên liền trước là bằng chứng ffill/không giao dịch, ĐÚNG bất kể hai
    # phiên có cùng khung hay không (so sánh Price thô với Price thô, không quy đổi qua Close).
    _, chained_ex = _lift_neighbour(series, i_ex)
    if chained_ex:
        # §29 (kb/coding_guidelines.md): "ffill/không giao dịch" là một NGUYÊN NHÂN, không phải
        # cách diễn đạt trung tính của "Price lặp lại" — quant-skeptic (round 2) đo thật VHM
        # 2026-08-06 (KL 16.902.474) và TRC 2026-09-15 (KL 611.072) đều bị nhãn này dù CÓ giao
        # dịch thật; nguyên nhân thật ở 2 ca đó là vendor báo giá Price trễ 1 phiên trên dòng
        # ex-date, không phải không giao dịch. Rẽ nhãn theo bit cơ học `Volume` của chính bar —
        # quyết định TỪ CHỐI (mismatch=False) giữ nguyên ở CẢ BA nhánh, chỉ lý do hiển thị đổi.
        vol = series[i_ex].get("volume")
        if vol is None:
            vol_reason = ("ffill HOẶC vendor báo giá trễ — chưa phân biệt được vì chuỗi không "
                          "mang Volume")
        elif vol > 0:
            vol_reason = (f"giá thô lặp lại phiên trước DÙ CÓ giao dịch thật (KL={vol:,.0f}) ⇒ "
                          f"nghi vendor báo giá trễ 1 phiên trên dòng ex-date")
        else:
            vol_reason = "mã không giao dịch phiên này (ffill)"
        return PriceCrossCheck(ex, f, None, None, False,
                               f"{ex}: phiên ex-date {series[i_ex]['d']} {vol_reason}, không "
                               f"cross-check")

    p_cum, p_ex = series[i_cum]["price"], series[i_ex]["price"]
    if p_cum <= 0 or p_ex <= 0:
        return PriceCrossCheck(ex, f, None, None, False, f"{ex}: Price <= 0, không cross-check")

    r_real = p_cum / p_ex
    dev = r_real / f - 1.0
    mismatch = abs(dev) > tol
    return PriceCrossCheck(
        ex, f, r_real, dev, mismatch,
        f"{ex}: công thức f={f:.6f} vs giá thật r_real={r_real:.6f} "
        f"(P_cum={p_cum:,.0f} {series[i_cum]['d']} → P_ex={p_ex:,.0f} {series[i_ex]['d']}) "
        f"dev={dev:+.4%}" + (" → MISMATCH, vượt PRICE_XCHECK_TOL" if mismatch else " → khớp"))


def price_crosscheck_after(date: str, events: list, series: list, series_max: str,
                           tol: float = PRICE_XCHECK_TOL) -> tuple:
    """(mismatches, notes) over every price-adjusting ex-date in (date, series_max].

    Mirrors `factor_after`'s own grouping (same `is_price_adjusting` filter, same
    `dedup_same_term`) so this checks EXACTLY the ex-date set that produced `r_pred` — never a
    silently different one.
    """
    by_ex = defaultdict(list)
    for ev in events:
        ex = ev.get("exright_date")
        if not ex or not (date < ex <= series_max):
            continue
        if not is_price_adjusting(ev):
            continue
        by_ex[ex].append(ev)

    mismatches, notes = [], []
    for ex in sorted(by_ex):
        kept, _dropped = dedup_same_term(by_ex[ex])
        xc = price_crosscheck(ex, kept, series, tol)
        notes.append(xc.note)
        if xc.mismatch:
            mismatches.append(xc)
    return tuple(mismatches), tuple(notes)


# ------------------------------------------------------------------- public entry

def repair_row(ticker: str, bar: dict, events: list, series: list, series_max: str,
               tol: float = TOL) -> Repair:
    """Verdict for one row. `bar` = {d, close, price[, high, low]}; `series` ascending, covers it.

    Returns `adj_source="vendor"` — i.e. change NOTHING — in every doubtful case: no events, an
    uncomputable ex-date in the window, a non-positive price, or vendor/self agreement inside
    `tol`. Only a computable chain plus a material disagreement yields a repair.
    """
    close, price = float(bar["close"]), float(bar["price"])
    base = dict(ticker=ticker, date=bar["d"], close=close, price=price)
    if close <= 0 or price <= 0:
        return Repair(**base, adj_source="vendor", reason="Close hoặc Price <= 0")

    # The row BEING REPAIRED needs the same ffill guard as the cum bar `group_factor` tests
    # internally — otherwise a stale/ffilled Price on THIS row (outside its own lifted band) gets
    # treated as ground truth and used to compute `r_obs`, silently overwriting a correct Close
    # with a wrong self-computed one.
    own_hist = [b for b in series if b["d"] < bar["d"]] + [bar]
    if _band_lifted_suspect(bar, own_hist, len(own_hist) - 1):
        return Repair(**base, adj_source="vendor",
                      reason="chính dòng đang sửa nằm ngoài band ffill-lifted của phiên liền "
                             "trước → Price nghi ngờ ffill/stale, không tự tin sửa dựa trên "
                             "input đáng ngờ")

    r_obs = price / close
    r_pred, uncomputable, notes = factor_after(bar["d"], events, series, series_max)
    if uncomputable:
        return Repair(**base, adj_source="vendor", r_obs=r_obs,
                      reason=f"{len(uncomputable)} ex-date không tính được hệ số → KHÔNG phát sinh "
                             f"gì, để cổng hiện hành tiếp tục chặn",
                      uncomputable_ex=tuple(uncomputable), notes=notes)
    dev = r_obs / r_pred - 1.0
    if abs(dev) <= tol:
        return Repair(**base, adj_source="vendor", r_obs=r_obs, r_pred=r_pred, dev=dev,
                      reason=f"vendor khớp trong {tol:.1%} — giữ nguyên Close của vendor",
                      notes=notes)
    if dev > 0:
        # r_obs > r_pred ⇒ the vendor adjusted MORE than our events explain ⇒ the likely gap is in
        # OUR table (a missing event), not in the vendor's. Repairing here would overwrite a
        # correct Close with a wrong one. Direction is a triage hint, not proof — so: refuse.
        return Repair(**base, adj_source="vendor", r_obs=r_obs, r_pred=r_pred, dev=dev,
                      reason=f"r_obs > r_pred ({dev:+.4%}) — vendor điều chỉnh NHIỀU hơn sự kiện "
                             f"ta có; khả năng cao BẢNG CỦA TA thiếu sự kiện → không sửa giá",
                      notes=notes)
    return Repair(**{**base, "close": price / r_pred}, adj_source="self_computed", r_obs=r_obs,
                  r_pred=r_pred, dev=dev,
                  reason=f"vendor lệch {dev:+.4%} (r_obs={r_obs:.6f} vs r_pred={r_pred:.6f}) "
                         f"→ Close_self = Price/r_pred",
                  notes=notes)
