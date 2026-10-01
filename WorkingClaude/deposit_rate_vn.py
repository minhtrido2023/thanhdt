# -*- coding: utf-8 -*-
"""
deposit_rate_vn.py — Big-4 (VCB/BIDV/CTG/Agribank) 12-month term-deposit rate, monthly.
Used as the ABSOLUTE Fed-model hurdle for the 8L valuation v3 deposit lens (state-conditional;
applied only in NEUTRAL/BEAR/CRISIS — see plan). NOT a cross-sectional valuation factor.

Source / calibration (2026-06-19):
  - Cyclical SHAPE from Trading Economics avg *lending* rate 1999-2023 (user-provided chart):
    2008~15.8, 2011~17(peak), 2013~10.4, 2014~8.7, 2015-17~7, 2018-22~7.4-7.9, 2023~9.2.
  - LEVELS pinned to known Big-4 12M *deposit* web anchors (the lending-deposit spread for Big-4
    is ~2%, narrower than the 3-3.5% SME rule, and widens in tight years):
      2026-06 BIDV 12M 6.8% (raised +1.2%); 2024 ~4.7; 2023 7.4(Q1)->5.0(Q4); 2022-12 ~7.5;
      2021/2022H1 ~5.5; 2020 6.0->5.7 (COVID cuts); 2015-17 ~5.5-6.5; 2014 ~7.0.
  - Pre-2014 (out of the value panel, kept for context): 2011 SBV cap ~14%; 2012 12->9; 2013 8->7.
⚠️ PROXY — levels are best-estimate (esp. 2022-H2 spike). Refine if a clean Big-4 series surfaces.

Methodology — resolving Big-4 disagreement (decided 2026-07-20):
  Representative rate = MODE (most common value across all 4 banks), NOT average.
  If 3/4 banks agree on a value, that value wins regardless of the outlier.
  Rationale: the rate that the majority of the dominant state-banks offer is the true market anchor;
  averaging in a contradictory outlier (often from a different channel/term) distorts the hurdle.
"""
import os
import numpy as np, pandas as pd

# (effective_date, big4_12m_deposit_pct_pa) — step series, forward-filled between anchors
DEPOSIT_EVENTS = [
    ("2011-01-01", 14.0),   # SBV cap era (pre-panel, context only)
    ("2012-04-01", 12.0),
    ("2012-10-01",  9.0),
    ("2013-06-01",  7.5),
    ("2014-01-01",  7.0),
    ("2014-07-01",  6.3),
    ("2015-01-01",  5.5),
    ("2016-01-01",  5.5),
    ("2017-01-01",  6.5),
    ("2018-01-01",  6.8),
    ("2019-01-01",  7.0),
    ("2020-01-01",  6.5),
    ("2020-07-01",  5.7),   # COVID easing
    ("2021-01-01",  5.5),
    ("2022-01-01",  5.5),
    ("2022-10-01",  6.8),   # SBV hikes (Oct-2022)
    ("2022-12-01",  7.5),   # late-2022 peak
    ("2023-03-01",  7.2),
    ("2023-06-01",  6.3),
    ("2023-09-01",  5.5),
    ("2023-12-01",  5.0),
    ("2024-04-01",  4.7),   # trough
    ("2025-01-01",  4.8),
    ("2025-09-01",  5.2),   # gentle re-rise
    ("2026-01-01",  6.0),
    ("2026-06-01",  6.8),   # BIDV current (web, +1.2%)
]


# append-only live extension: future point-in-time anchors go here, NEVER edit the 26 frozen
# historical anchors above (see proposal_deposit_rate_monthly_refresh_20260713.md §1). Written only
# by append_deposit_rate.py after a human confirms the number. No CSV / no newer rows -> behaviour
# is byte-identical to the frozen-anchors-only series (100% backward-compatible).
_EVENTS_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "deposit_rate_vn_events.csv")


def deposit_events_df():
    ev = pd.DataFrame(DEPOSIT_EVENTS, columns=["time", "deposit_rate"])
    ev["time"] = pd.to_datetime(ev["time"])
    if os.path.exists(_EVENTS_CSV):
        try:
            extra = pd.read_csv(_EVENTS_CSV, usecols=["effective_date", "deposit_rate"])
        except pd.errors.EmptyDataError:
            extra = None  # empty file (e.g. fresh install, cron hasn't appended yet) -> frozen only
        except pd.errors.ParserError:
            # pandas.errors.ParserError IS a ValueError subclass -- must be caught BEFORE the
            # generic ValueError clause below, and re-raised, not swallowed. A genuinely corrupt
            # CSV (bad quoting, truncated row) used to fall into the old blanket
            # `except (EmptyDataError, ValueError)` and silently revert to frozen-anchors-only
            # with zero signal anywhere that the live feed is broken -- every consumer
            # (rating_8l.py live tilt, dcf_valuation.py, macro_confidence_regime.py,
            # macro_killswitch_a_status) would read stale data believing it was current. Letting
            # it propagate lets macro_killswitch_a_status's fail-closed try/except turn it into an
            # explicit armed+stale+reason='error:...' instead (found 2026-10-01,
            # macro_killswitch_a_selfcheck.py T12).
            raise
        except ValueError:
            extra = None  # e.g. missing expected columns in an old-format file -> frozen only
        if extra is not None and len(extra):
            extra = extra.rename(columns={"effective_date": "time"})
            extra["time"] = pd.to_datetime(extra["time"], errors="coerce")
            extra["deposit_rate"] = pd.to_numeric(extra["deposit_rate"], errors="coerce")
            extra = extra.dropna(subset=["time", "deposit_rate"])
            # only append anchors strictly newer than the last frozen one (append-only, no re-write
            # of history); if two CSV rows share the newest date, sort keeps the last-written one.
            extra = extra[extra["time"] > ev["time"].max()]
            if len(extra):
                ev = pd.concat([ev, extra[["time", "deposit_rate"]]], ignore_index=True)
    return ev.sort_values("time").reset_index(drop=True)


def merge_deposit(df, time_col="time"):
    """as-of (backward) merge the deposit_rate onto a frame with a datetime `time_col`."""
    ev = deposit_events_df()
    d = df.sort_values(time_col).copy()
    d[time_col] = pd.to_datetime(d[time_col])
    return pd.merge_asof(d, ev, left_on=time_col, right_on="time",
                         direction="backward", suffixes=("", "_dep"))


def macro_killswitch_a_status(asof=None, stale_days_limit=45, check_freshness=None):
    """trading_rules.json::macro_kill_switches.A_sbv_rate_suspend, implemented LITERALLY as code
    for the first time (2026-10-01) — grepping 'macro_kill_switches'/'A_sbv_rate_suspend' across
    every .py in the repo previously returned 0 hits, i.e. this was spec-only prose with no
    enforcement mechanism. Trigger: Big-4 12M deposit rate (THIS module's canonical series,
    current_deposit_rate()) > 7.5%. Spec's own freshness clause ("if the deposit feed is stale,
    fail SAFE (treat as armed)") is honored here, but ONLY for the live/monitoring call shape
    (asof=None, i.e. "what is the status right now"): check_freshness defaults to
    `asof is None` and can be overridden explicitly. Without this split, a historical/backtest-
    style call (asof=some past date) would spuriously read "stale" purely because the 26 FROZEN
    historical anchors in DEPOSIT_EVENTS are, by construction, months apart — that's settled
    ground truth, not a live feed failing to refresh (caught by this function's own selfcheck,
    macro_killswitch_a_selfcheck.py T2, 2026-10-01: querying asof='2013-01-01' against the
    2012-10-01 anchor, 92 days prior, was flagged stale under the naive asof-relative definition).

    DISPLAY/MONITORING ONLY as of this commit: the sleeve this switch was designed to gate
    (execution_limits.deep_cheap_recovery_override, the RECOVERY_PARK deep-cheap deploy) remains
    status=PROPOSED/paper with zero live production code path of its own (RECOVERY_PARK env flag
    defaults OFF in pt_v23_audit_2014.py) — there is no live order flow for this function to gate
    yet. It exists so (a) the threshold has a real, testable implementation the day that sleeve
    (or any other consumer) goes live, and (b) the 7.5% level can be monitored today via
    dna_report.build_macro_killswitch_a_line(), independent of the CCTG 6-month certificate rate
    (a DIFFERENT instrument/tenor under separate legal-vn equivalence review — do not conflate).

    stale_days_limit=45 is an ARBITRARY choice (trading_rules.json's own spec text does not name a
    number) and must be read against how this feed is actually refreshed: there is no automated
    daily/live feed for the Big-4 12M deposit rate — the only update path is a human confirming a
    number via `append_deposit_rate.py` after the monthly `refresh_deposit_rate_vn.sh` cron
    *reminder* (fires day-3 ICT, best-effort fetch, does NOT auto-write). So "stale" here concretely
    means "the last MANUAL confirmation is more than stale_days_limit days old", not "a live feed
    stopped ticking". Practical consequence (computed from the real production CSV, last confirmed
    anchor 2026-09-04): staleness triggers on age > 45d, i.e. the 46th day, NOT the 45th (age
    == 45 is still fresh -- see cctg_overlay_selfcheck.py T16's `>` vs `>=` boundary test) --
    if the 2026-11-03 monthly reminder is missed with no human confirming a newer anchor,
    this gate flips to armed=True/stale=True on its own at 2026-09-04 + 46d = **2026-10-20**
    (NOT 2026-10-19, which is still day 45/fresh) — note this in any report that cites
    this function's live status.

    Any exception anywhere in this function (corrupt/unparseable CSV beyond the narrow
    EmptyDataError/ValueError already handled inside deposit_events_df -- e.g. a malformed-quote
    ParserError, a PermissionError on the CSV path, or anything else) is caught at the top level and
    treated as fail-closed: armed=True, stale=True, reason starts with "error:". Same fail-closed
    treatment for a rate value outside RATE_MIN..RATE_MAX (0.5%..30%, a sanity fence on the raw
    `deposit_rate` column) -- this catches a fraction-vs-percent typo (e.g. an anchor written as
    0.068 meaning 6.8%) before it could silently read as "rate 0.07% <= 7.5% -> CLEAR".

    EFFECTIVE RATE (added 2026-10-01, user directive "CCTG đưa vào model làm nguồn lãi proxy nếu
    lãi suất cao hơn gửi tiết kiệm"): after resolving the Big-4 12M rate above, this function also
    looks up cctg_rate_vn.current_cctg_rate_checked() at the same asof and takes max(big4_12m,
    cctg) IF the CCTG observation is itself fresh (same stale_days_limit) and in-range -- never
    averages the two, never lets a stale/out-of-range CCTG value override a good Big-4 reading.
    Before 2026-09-30 (CCTG series' first anchor) current_cctg_rate_checked() returns (None, None,
    None) for every asof, so every call on a date before that is byte-identical to the pre-CCTG
    implementation -- no historical backtest pinned against this function changes. New key in the
    return dict: rate_source ("big4_12m" or "cctg_6m(<date>)", None on no-data/error) records which
    series drove the final rate, since the two are different tenors (12M vs 6M) and a report
    citing this number must say which one is active (see cctg_rate_vn.py module docstring).

    ⚠ SYMMETRIC fail-closed on the CCTG side (round-2 fix 1 closed the original bare `except
    Exception: pass`; round-3 fix 2 closed one asymmetry; round-6 fix, 2026-10-01, user-approved
    hướng B, closes the LAST one -- current behavior, superseding both prior descriptions): a CCTG
    read error, an out-of-range value, OR a STALE reading (age > stale_days_limit) -- regardless of
    whether the last-known CCTG value was itself <= or > the 7.5% threshold -- ALWAYS forces
    `armed=True` directly (not just `stale=True`) and sets `cctg_note`. There is no "last known
    value was already safe, so nothing to escalate" carve-out any more, on purpose: the symmetric
    Big-4 clause two paragraphs below (`big4_stale`) has never had such a carve-out either -- a
    stale Big-4 reading forces `armed=True` unconditionally, no matter what the last Big-4 value
    was, because a feed we have not reconfirmed in `stale_days_limit` days could have moved above
    the trigger in the interim and we would have no way to know. The pre-round-6 CCTG branch broke
    that symmetry by staying silently non-armed (`stale` not even set) whenever the last CCTG
    reading it last saw was <= 7.5% -- exactly the gap a round-6 review user caught: an untouched
    CCTG anchor ages past 45 days with nobody reminded, and the gate would keep reporting CLEAR
    forever on a number nobody has looked at since. Now: ANY cctg_stale (fresh-but-safe excluded,
    see rate-override branch just below) sets `cctg_note` describing the age + last reading and
    forces `armed=True`, identically to every other failure mode in this function.

    Returns dict: armed(bool), rate(float|None, fraction e.g. 0.068), threshold(0.075),
    stale(bool), last_update(str date|None), age_days(int|None), reason(str), rate_source(str|None)."""
    THRESHOLD = 0.075
    RATE_MIN_PCT, RATE_MAX_PCT = 0.5, 30.0
    try:
        if check_freshness is None:
            check_freshness = asof is None
        ev = deposit_events_df()
        asof_ts = pd.Timestamp.today().normalize() if asof is None else pd.to_datetime(asof)
        avail = ev[ev.time <= asof_ts]
        if avail.empty:
            return {"armed": True, "rate": None, "threshold": THRESHOLD, "stale": True,
                    "last_update": None, "age_days": None, "rate_source": None,
                    "reason": "no deposit data at/before asof -> fail-closed (armed)"}
        last_date = avail.iloc[-1]["time"]
        rate_pct = float(avail.iloc[-1]["deposit_rate"])
        if not (RATE_MIN_PCT <= rate_pct <= RATE_MAX_PCT):
            return {"armed": True, "rate": None, "threshold": THRESHOLD, "stale": True,
                    "last_update": str(last_date.date()), "age_days": None, "rate_source": None,
                    "reason": (f"rate_pct={rate_pct!r} ngoài khoảng hợp lệ "
                               f"[{RATE_MIN_PCT},{RATE_MAX_PCT}] -> fail-closed (armed)")}
        rate_source = "big4_12m"
        # cctg_force_armed / cctg_note: symmetric fail-closed treatment for the CCTG overlay.
        # Round-2 fix 1 (2026-10-01) first closed the bare `except Exception: pass` that let every
        # CCTG failure mode fall through to Big-4-only with ZERO trace. Round-3 fix 2 (2026-10-01,
        # quant-skeptic round-3) closed the error/out-of-range asymmetry: those cases now force
        # armed=True directly (not just stale=True), same as every Big-4-side error in this
        # function. Round-6 fix (2026-10-01, user-approved hướng B) closes the LAST asymmetry: a
        # STALE-but-successfully-read CCTG value used to force armed=True ONLY if its last known
        # reading was already > 7.5% -- a stale reading whose last value was <= 7.5% stayed
        # silently non-armed, unlike `big4_stale` below which has no such carve-out at all. Any
        # cctg_stale now unconditionally forces armed=True + sets cctg_note, regardless of what the
        # last-known CCTG value was (see docstring above).
        cctg_force_armed = False
        cctg_note = None
        try:
            from cctg_rate_vn import current_cctg_rate_checked
            cctg_pct, cctg_date, cctg_err = current_cctg_rate_checked(str(asof_ts.date()))
            if cctg_err is not None:
                cctg_force_armed = True
                cctg_note = f"CCTG lỗi/ngoài khoảng ({cctg_err}) -> không xác thực được, fail-closed"
            elif cctg_pct is not None:
                cctg_age = (asof_ts - cctg_date).days
                cctg_stale = check_freshness and cctg_age > stale_days_limit
                if cctg_stale:
                    cctg_force_armed = True
                    cctg_note = (f"CCTG cũ ({cctg_age}d > {stale_days_limit}d), xác nhận thủ công "
                                 f"lần cuối {cctg_date.date()} ({cctg_pct:.2f}%) -> fail-closed "
                                 f"(armed)")
                elif cctg_pct > rate_pct:
                    rate_pct = cctg_pct
                    rate_source = f"cctg_6m({cctg_date.date()})"
        except Exception as exc:
            cctg_force_armed = True
            cctg_note = f"CCTG overlay lỗi không lường trước ({exc!r}) -> không xác thực được, fail-closed"

        rate = rate_pct / 100.0
        age_days = (asof_ts - last_date).days
        big4_stale = check_freshness and age_days > stale_days_limit
        stale = big4_stale or (cctg_note is not None)
        if big4_stale:
            armed = True
            reason = (f"feed stale ({age_days}d > {stale_days_limit}d, lần xác nhận thủ "
                      f"công cuối {last_date.date()}) -> fail-closed (armed)")
        else:
            armed = (rate > THRESHOLD) or cctg_force_armed
            if rate > THRESHOLD:
                reason = f"{rate_source} {rate_pct:.2f}% > 7.5% -> SUSPEND new recovery deploy"
            elif cctg_force_armed:
                # Round-7 fix (2026-10-01, quant-skeptic round-6 "chuỗi reason tự mâu thuẫn"):
                # the rate itself is <= threshold (what would normally read CLEAR), but the CCTG
                # side forces armed anyway -- say ARMED up front instead of saying CLEAR and then
                # contradicting it with "-> ARMED" later in the same string.
                reason = f"{rate_source} {rate_pct:.2f}% <= 7.5% nhưng ARMED (forced); {cctg_note}"
            else:
                reason = f"{rate_source} {rate_pct:.2f}% <= 7.5% -> CLEAR"
        return {"armed": armed, "rate": rate, "threshold": THRESHOLD, "stale": stale,
                "last_update": str(last_date.date()), "age_days": age_days, "reason": reason,
                "rate_source": rate_source, "big4_stale": bool(big4_stale), "cctg_note": cctg_note}
    except Exception as exc:
        return {"armed": True, "rate": None, "threshold": THRESHOLD, "stale": True,
                "last_update": None, "age_days": None, "rate_source": None,
                "reason": f"error: {exc!r} -> fail-closed (armed)"}


def current_deposit_rate(asof=None):
    """asof=None means TODAY, not "the last row in the series" — a future-dated or typo'd
    effective_date (e.g. a year typo) must never pin/pre-empt the live value. Found 2026-07-20
    via adversarial review of append_deposit_rate.py (mike/kb/projects/deposit-rate-autocheck.md,
    round 7->8): the old `if asof is None: return ev.deposit_rate.iloc[-1]` returned whatever row
    sorted last by time, with no bound against the real clock — rating_8l.py calls this with no
    asof (the live NEUTRAL-tilt path), so this was a real, reachable production gap."""
    ev = deposit_events_df()
    asof = pd.Timestamp.today().normalize() if asof is None else pd.to_datetime(asof)
    return float(ev[ev.time <= asof].deposit_rate.iloc[-1])


def effective_deposit_rate(asof=None, stale_days_limit=45, check_freshness=None):
    """max(Big-4 12M, Big-4 CCTG 6M) for DISPLAY-ONLY consumers (value_radar.py and future
    display-only callers) -- added 2026-10-01, same CCTG-overlay policy as
    macro_killswitch_a_status() (see that function's docstring): CCTG only wins if fresh and
    in-range, never averaged, never silently replaces Big-4 when Big-4 is higher. UNLIKE
    macro_killswitch_a_status(), this has no "armed" concept -- it is a plain rate lookup, so a
    stale/missing/bad Big-4 reading here raises (same as current_deposit_rate()'s existing
    behavior) rather than fail-closing to some gate state; callers that need fail-closed semantics
    should use macro_killswitch_a_status(), not this function.

    User approved wiring this into rating_8l.py's NEUTRAL deposit tilt and the DCF discount-rate
    chain (dcf_valuation.py / trading_bot/due_diligence.py / dcf_refresh_gate.py /
    custom30_yield_labels.py) on 2026-10-01 (job Taylor_20261001_054110) -- those 5 call sites
    now go through `consumer_deposit_rate()` below, NOT this function directly. Any FUTURE new
    consumer of this rate should go through `consumer_deposit_rate()` too (one rollback knob),
    not call `effective_deposit_rate()` ad-hoc. See mike/kb/data_registry/macro/cctg_rate_vn.md
    for the full consumer inventory + diff table.

    Returns dict: rate(float, fraction), rate_pct(float), rate_source("big4_12m"|"cctg_6m(<date>)"),
    big4_rate_pct(float), cctg_rate_pct(float|None), last_update(str date)."""
    if check_freshness is None:
        check_freshness = asof is None
    asof_ts = pd.Timestamp.today().normalize() if asof is None else pd.to_datetime(asof)
    big4_pct = current_deposit_rate(str(asof_ts.date()))
    rate_pct, rate_source = big4_pct, "big4_12m"
    last_date = asof_ts
    ev = deposit_events_df()
    avail = ev[ev.time <= asof_ts]
    if len(avail):
        last_date = avail.iloc[-1]["time"]
    # current_cctg_rate_checked() (not the raw current_cctg_rate()) -- the raw getter has NO
    # range validation at all, so a CSV typo (fraction-vs-percent, digit transposition) used to
    # flow straight into this DISPLAY number unchecked (quant-skeptic round-2 fix 1, 2026-10-01).
    # An error/out-of-range CCTG read here degrades to cctg_pct=None (Big-4-only), same as "no
    # CCTG data" -- there is no "armed"/stale concept on this function (see docstring), so the
    # only symmetric behavior available is "don't let a bad value drive the display at all".
    cctg_pct = None
    try:
        from cctg_rate_vn import current_cctg_rate_checked
        cctg_pct, cctg_date, cctg_err = current_cctg_rate_checked(str(asof_ts.date()))
        if cctg_err is not None:
            cctg_pct = None
        elif cctg_pct is not None and cctg_pct > big4_pct:
            cctg_age = (asof_ts - cctg_date).days
            cctg_stale = check_freshness and cctg_age > stale_days_limit
            if not cctg_stale:
                rate_pct, rate_source = cctg_pct, f"cctg_6m({cctg_date.date()})"
    except Exception:
        cctg_pct = None
    return {"rate": rate_pct / 100.0, "rate_pct": rate_pct, "rate_source": rate_source,
            "big4_rate_pct": big4_pct, "cctg_rate_pct": cctg_pct, "last_update": str(last_date.date())}


def consumer_deposit_rate(asof=None):
    """Single wiring point for the 5 LIVE production consumers of `current_deposit_rate()` that
    the user approved switching to the Big-4+CCTG effective rate on 2026-10-01 (job
    Taylor_20261001_054110): rating_8l.py's NEUTRAL deposit tilt, trading_bot/due_diligence.py's
    fear-buy `_yield_floor()`, its batch twin custom30_yield_labels.py, and the DCF
    discount-rate chain (dcf_valuation.py::discount_rate, dcf_refresh_gate.py's drift monitor).
    Centralizing here (rather than editing each call site to call effective_deposit_rate()
    directly) means all 5 move together and share ONE rollback knob.

    Returns a plain float in PERCENT -- same shape/units as current_deposit_rate() -- so every
    call site is a drop-in `current_deposit_rate -> consumer_deposit_rate` rename, no other edit.

    Rollback: env DEPOSIT_RATE_CCTG_OVERLAY=0 reverts ALL 5 consumers to Big-4-only
    (current_deposit_rate()) in one step, e.g. if the CCTG legal-vn re-verification (see
    mike/kb/data_registry/macro/cctg_rate_vn.md §Pháp lý) comes back negative. Default "1" (on).

    History is unaffected either way: cctg_rate_vn has its only anchor at 2026-09-30, so
    effective_deposit_rate() is byte-identical to current_deposit_rate() for every asof before
    that date regardless of this knob -- verified in cctg_deposit_wiring_selfcheck.py."""
    if os.environ.get("DEPOSIT_RATE_CCTG_OVERLAY", "1") == "0":
        return current_deposit_rate(asof)
    return effective_deposit_rate(asof)["rate_pct"]


def effective_deposit_events_df():
    """Same shape as deposit_events_df() (time, deposit_rate) -- a STEP series -- but with
    cctg_rate_vn's series' own anchor dates UNIONED in as additional breakpoints, each row set to
    max(Big-4-as-of-that-date, CCTG-as-of-that-date). A naive as-of merge onto deposit_events_df()'s
    OWN rows alone is a no-op in practice here: Big-4's last anchor row predates CCTG's first
    anchor (2026-06-01 < 2026-09-30), so a backward merge keyed on Big-4's existing row dates would
    never land ON a CCTG date and the CCTG value would never surface downstream (caught 2026-10-01
    before shipping, cctg_overlay_selfcheck.py T8/T9 -- this function's first draft had exactly
    that bug). Any row strictly before CCTG's first anchor is byte-identical to deposit_events_df()
    alone (only Big-4 breakpoints exist that far back). For historical/rolling display-only
    consumers needing the FULL step series (value_radar.py), not a single current-rate lookup --
    no staleness/fail-closed concept here (there is no "now" inside a historical frame); see
    macro_killswitch_a_status()/effective_deposit_rate() for the live, fail-closed version.

    Quant-skeptic round-3 fix (2026-10-01): a CCTG-side parse/range error from cctg_events_df()
    now PROPAGATES instead of being swallowed by a bare `except Exception: return base`. The old
    silent fallback meant a broken CCTG append (bad header, unparseable value, OR a format-valid
    typo like "85" that used to have NO range check at all here) would either vanish into a
    Big-4-only series with zero trace, or -- worse, before cctg_events_df()'s own range guard
    existed -- flow straight into the displayed deposit_rate as a naked out-of-range number. The
    sole caller, value_radar.py's load_series() (via value_radar_now()), already treats any
    exception from this module as "skip this cycle, no Value Radar line" -- showing nothing is
    strictly safer than showing a silently-wrong or silently-stale number."""
    base = deposit_events_df()[["time", "deposit_rate"]].copy()
    from cctg_rate_vn import cctg_events_df
    cev = cctg_events_df().rename(columns={"cctg_rate": "deposit_rate"})
    all_dates = (pd.concat([base[["time"]], cev[["time"]]], ignore_index=True)
                 .drop_duplicates().sort_values("time").reset_index(drop=True))
    big4_asof = pd.merge_asof(all_dates, base.sort_values("time"), on="time", direction="backward")
    cctg_asof = pd.merge_asof(all_dates, cev.sort_values("time"), on="time", direction="backward")
    merged = all_dates.copy()
    merged["deposit_rate"] = np.fmax(big4_asof["deposit_rate"].to_numpy(dtype=float),
                                      cctg_asof["deposit_rate"].fillna(-np.inf).to_numpy(dtype=float))
    return merged.sort_values("time").reset_index(drop=True)


if __name__ == "__main__":
    ev = deposit_events_df()
    # annual view for eyeballing
    idx = pd.date_range("2014-01-01", "2026-06-01", freq="MS")
    s = pd.merge_asof(pd.DataFrame({"time": idx}), ev, on="time", direction="backward")
    ann = s.groupby(s.time.dt.year).deposit_rate.mean().round(2)
    print("Big-4 12M deposit proxy (annual mean, %):")
    for y, v in ann.items():
        print(f"  {y}: {v:.2f}")
    print(f"\ncurrent (2026-06) = {current_deposit_rate():.2f}%")
