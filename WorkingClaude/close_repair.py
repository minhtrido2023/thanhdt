#!/usr/bin/env python3
"""Layer 2 — REPAIR an incomplete vendor back-adjustment from our own corp-action table.

NOT WIRED INTO PRODUCTION. Gated by env `MIKE_CLOSE_REPAIR=1`; default OFF everywhere. The gate
to turning it on is a quant-skeptic CONFIRMED verdict, because every number it changes is an
investor-facing tỉ suất (`coding_guidelines` §21).

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
    """True only when explicitly switched on. Absent env var = OFF, for every caller."""
    return os.environ.get(ENV_FLAG) == "1"


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

def _band_lifted_suspect(bar: dict, neighbour: dict | None) -> bool:
    """True when `bar['price']` cannot be a real trade of that session (ffill signature).

    Needs a neighbour row to lift the adjusted `High`/`Low` band into the raw frame. No neighbour,
    or no band → we cannot test, so we do NOT accuse: return False and let the caller's other
    guards speak. (Refusing here instead would fail-close on every first row of a window.)
    """
    hi, lo = bar.get("high") or 0.0, bar.get("low") or 0.0
    if hi <= 0 or lo <= 0 or not neighbour:
        return False
    if not neighbour.get("close") or neighbour["close"] <= 0:
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
    if _band_lifted_suspect(bar, series[i - 1] if i > 0 else None):
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
