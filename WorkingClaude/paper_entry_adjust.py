#!/usr/bin/env python3
"""paper_entry_adjust.py — rebase a FROZEN paper entry_price into today's adjusted-price scale.

WHY (the bug this exists to kill)
---------------------------------
Paper-portfolio reports compare a FROZEN `entry_price` (a raw price snapshot taken once, at
launch, and never updated) against a LIVE `Close` (retroactively dividend/split-adjusted from
TODAY's vintage). Mixing those two reference frames is Bẫy (2) of
`mike/kb/data_registry/price-volume/ticker_close_vs_price_dividend_adj.md`: every corporate action
that happens AFTER entry gets charged to the position as if it were a price loss.

Measured case (2026-08-13): MBB went ex-rights 2026-08-11 (10% rights issue + 15% stock dividend)
on top of a 1.000đ cash dividend 2026-07-09. `alphalens_report.py` reported **-18.8%**; the true
total return was **+1.3%** — a 20,2pp error that INVERTED the sign, and it moved the whole
4-name portfolio from -3,08% to +1,96%.

THE FIX
-------
Multiply the frozen raw entry by the adjustment ratio today's vintage assigns to the entry date:

    factor    = Close(asof) / Price(asof)        # today's vintage, same row
    entry_adj = entry_price * factor
    pct       = Close_now / entry_adj - 1

Both ends of the return then sit on the SAME adjusted scale.

WHICH CONVENTION — and why the paper books do NOT get the TERP one
-------------------------------------------------------------------
`Close/Price` is built on the TERP convention: at a rights issue it assumes the holder either
SUBSCRIBED at the offer price or SOLD the right at its theoretical value. Verified by inverting
MBB's own 2026-08-11 step, which contains a 10% rights issue and a 15% stock dividend at once:

    (P_cum + r·S) / (P_cum·(1 + r + r_sd)) = (24.250 + 0,10×10.000) / (24.250 × 1,25)
                                           = 0,832990   — the observed step, to six decimals.

That is a fine convention for an account with cash in it. A PAPER book has no cash account, never
subscribed and never sold anything, so crediting it with the value of a right it could not take up
OVERSTATES the return. Two conventions are therefore reported, and the accrue-only one leads:

  * `factor_accrue_only`  — cash dividends and stock dividends/bonuses only, i.e. everything that
    lands in the holder's lap without a decision. Rights are EXCLUDED: the right lapses. This is
    the headline (`entry_adj`, `pct_vs`).
  * `factor_terp`         — the raw `Close/Price`, reported alongside, for anyone comparing
    against the adjusted price series directly.

They are IDENTICAL whenever no rights issue falls in the window, which is the overwhelming
majority of positions — so this distinction changes a number only where it must. Measured on MBB
(entry 25.200 at 2026-06-30): TERP `entry_adj` 20.180 → +1,3%; accrue-only 21.069 → −2,9%.
The rights component is backed out as a RESIDUAL of the ex-date price step (the corp-action feed
carries no subscription price — `value_per_share` is NULL on the rights row), so it needs every
other event that same day to be sized; when one is not, the position degrades to
`RIGHTS_UNRESOLVED` rather than quietly falling back to TERP.

WHAT THE CORP-ACTION TABLE IS AND IS NOT USED FOR
--------------------------------------------------
The TERP factor needs no event data at all: `Close/Price` already encodes the cumulative effect of
every event between `asof` and today, which is exactly what a total-return mark needs. Bẫy (4) of
the registry doc says that ratio cannot tell you WHICH event happened, so it must never be used to
derive a per-share cash number — but a magnitude-only rebase is the one job it is right for.

`tav2_bq.corporate_action` enters for exactly two things, both of them classification rather than
measurement: (a) knowing that a rights issue occurred at all, and (b) sizing the OTHER events that
went ex the same day so the rights step can be divided out. It is also the independent verifier
(`paper_entry_corpaction_crosscheck.py`) — a different data path from the price ETL, which is what
makes agreement between them evidence.

CONTROL PROPERTY (the thing that makes this safe to ship)
---------------------------------------------------------
A ticker with no corporate action between `asof` and today has `factor == 1.0` EXACTLY, so
`entry_adj == entry_price` and the reported number is byte-identical to the pre-fix behaviour.
The fix can only move a number when a real corporate action justifies moving it.

Reference frames — do NOT reuse this for real money
---------------------------------------------------
This helper marks PAPER positions, where there is no cash account, no real fill and no dividend
actually received. For REAL positions the canonical path stays
`mike/bin/dividend_adjusted_return.py` (coding_guidelines §21): it solves per-share cash from the
broker's own `cashDividendReceiving` and nets 5% TNCN tax. Do not swap one for the other.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

WORKDIR = Path(os.environ.get("WORKDIR_8L", os.environ.get("WORKDIR", "/home/trido/thanhdt/WorkingClaude")))
DEFAULT_CACHE = WORKDIR / "data" / "bq_cache"

# A raw price and its adjusted twin may disagree by at most this much before we call the recorded
# entry_price "not the close of asof" and say so out loud (a recorded entry that is NOT the
# asof close is legitimate — an intraday fill — but it must be visible, not silently absorbed).
ENTRY_MATCH_TOL = 0.005          # 0,5%
FACTOR_EPS = 1e-6                # float slack around the factor <= 1 invariant
# a year file lagging the newest cache file by more than this cannot be trusted to carry today's
# retroactive adjustment. 2 days covers a weekend's worth of normal cron jitter and nothing more.
VINTAGE_TOL_DAYS = 2.0
RIGHTS_METHOD = "Quyền mua CP cho Cổ đông hiện hữu"
# relative drop tolerated in the non-decreasing Close/Price invariant before calling it a real
# violation (vs rounding noise) — same threshold, same empirical basis as `_TERP_DROP_TOL` in
# mike/bin/paper_programs_daily_report.py (measured 227x gap between rounding noise (4,01e-4,
# 4 AlphaLens tickers, 58 sessions) and a real break (9,09e-2, FPT 2026-09-29)). Kept as one
# named constant here rather than imported, so this module has no import-time dependency on the
# report script (`paper_entry_adjust.py` is imported BY the reports, not the reverse).
TERP_DROP_TOL = 5e-3


@dataclass
class AdjustedEntry:
    """Result of rebasing one frozen entry price. `entry_adj` is always safe to divide by.

    `factor` is the factor actually USED for `entry_adj` — accrue-only by default. `factor_terp`
    is always the raw `Close/Price`; when no rights issue falls in the window the two are equal
    and `rights_events` is empty.
    """
    ticker: str
    entry_price: float           # as recorded in the paper JSON (raw, frozen)
    entry_adj: float             # rebased into today's adjusted scale
    factor: float | None         # the factor USED (see `convention`); None when unavailable
    raw_at_asof: float | None    # Price(asof) — used only to validate the recorded entry
    asof_used: str | None        # the trading day actually resolved (<= requested asof)
    status: str                  # ADJUSTED | UNCHANGED | NO_DATA | BAD_FACTOR
                                 # | RIGHTS_UNRESOLVED | VINTAGE_STALE | REPAIR_INCONSISTENT
                                 # | REPAIR_PRICE_MISMATCH
    note: str | None = None      # human-readable caveat, surfaced in the report when set
    factor_terp: float | None = None      # raw Close/Price (TERP: rights subscribed or sold)
    convention: str = "accrue_only"       # accrue_only | terp
    rights_events: tuple = ()             # ex-dates of the rights issues stripped out
    adj_source: str = "vendor"            # vendor | self_computed (see close_repair.py)
    repair_note: str | None = None        # why the Close was replaced, when it was

    @property
    def is_adjusted(self) -> bool:
        return self.status == "ADJUSTED"

    @property
    def degraded(self) -> bool:
        """True when we could not verify the rebase and fell back to the raw frozen entry."""
        return self.status in ("NO_DATA", "BAD_FACTOR", "RIGHTS_UNRESOLVED", "VINTAGE_STALE",
                               "REPAIR_INCONSISTENT", "REPAIR_PRICE_MISMATCH")

    def pct_vs(self, current_close: float) -> float:
        """Total return % of this position, both ends on the adjusted scale."""
        return (current_close - self.entry_adj) / self.entry_adj * 100.0


def _fetch_rows(items, cache_dir):
    """Return {(ticker, asof): (time, Close, Price)} — last trading row <= asof per request.

    One duckdb pass over the yearly ticker cache. Raises on genuine infrastructure failure; the
    caller decides whether that degrades a report or aborts it.
    """
    import duckdb

    con = duckdb.connect()
    con.execute("SET threads=1")
    try:
        out = {}
        glob = f"{cache_dir}/ticker/*.parquet"
        for ticker, asof in {(i[0], i[1]) for i in items}:
            row = con.execute(
                f"""
                SELECT time, Close, Price
                FROM read_parquet('{glob}')
                WHERE ticker = ?
                  AND time <= CAST(? AS DATE)
                  AND time >= CAST(? AS DATE) - INTERVAL 20 DAY
                  AND Price IS NOT NULL AND Price > 0
                  AND Close IS NOT NULL AND Close > 0
                ORDER BY time DESC
                LIMIT 1
                """,
                [ticker, asof, asof],
            ).fetchone()
            if row:
                out[(ticker, asof)] = (str(row[0]), float(row[1]), float(row[2]))
        return out
    finally:
        con.close()



def _repaired_series_violation(ticker, asof, events, series, series_max):
    """(exdate_bad, r0, r_min) or None — non-decreasing check on the REPAIRED ratio series.

    Only called for a (ticker, asof) row close_repair already marked `adj_source="self_computed"`
    — i.e. this checks close_repair's OWN output for internal consistency, not the vendor's.
    `Close/Price` at date d = product of adjustment factors for every ex-date still AHEAD of d, so
    it must be NON-DECREASING as d advances (fewer future ex-dates remain). `close_repair.py`
    recomputes this ratio independently at every date via `factor_after`, so a correct, complete
    `corporate_action` table makes the repaired series satisfy this by construction. A VIOLATION
    here is mechanical evidence (§29, `kb/coding_guidelines.md`) that `corporate_action` itself is
    wrong/missing an event for this ticker/window — not that the vendor needs a cap (that case is
    `_terp_factor_stale` in `mike/bin/paper_programs_daily_report.py`, which stays the safety net
    for entries close_repair has NOT touched). The caller must fail closed, not guess a number.
    """
    import close_repair             # re-imported: this function is called independently of
                                     # `_repair_close`'s own local import, e.g. from selfcheck/tests

    future = sorted((b for b in series if asof <= b["d"] <= series_max), key=lambda b: b["d"])
    if len(future) < 2:
        return None
    ratios = []
    for bar in future:
        if bar["price"] <= 0:
            continue
        rep = close_repair.repair_row(ticker, bar, events, series, series_max)
        ratios.append((bar["d"], rep.close / bar["price"]))
    if len(ratios) < 2:
        return None
    _, r0 = ratios[0]
    d_bad, r_min = min(ratios[1:], key=lambda x: x[1])
    if r0 > 0 and (r0 - r_min) / r0 > TERP_DROP_TOL:
        return d_bad, r0, r_min
    return None


def _price_mismatch(ticker, asof, events, series, series_max):
    """tuple of `close_repair.PriceCrossCheck` mismatches, or None — independent GROSS-error
    screen against REAL price action at the ex-date (Việc nhỏ 3, 2026-09-29, job
    Taylor_20260929_032553). Only called for a (ticker, asof) row close_repair already marked
    `adj_source="self_computed"`. Catches the direction `_repaired_series_violation` structurally
    cannot: `corporate_action` OVER-stating an event (ratio/value too HIGH) keeps the repaired
    ratio series monotone but disagrees with what actually traded on the ex-date session — see
    `close_repair.py`'s `PRICE_XCHECK_TOL` comment block for the calibration evidence and its own
    disclosed blind spot (sub-~20% ratio errors are not reliably distinguishable from ordinary
    single-day trading noise; this is a coarse screen, not an exact validator).
    """
    import close_repair             # re-imported: same reasoning as _repaired_series_violation

    mismatches, _notes = close_repair.price_crosscheck_after(asof, events, series, series_max)
    return mismatches if mismatches else None


def _repair_close(rows, items, cache_dir, cache_max_date):
    """({(tk,asof): (time, Close, Price)}, {(tk,asof): Repair}, {(tk,asof): violation},
    {(tk,asof): price_mismatches}) — the vendor Close REPAIRED, plus two independent fail-closed
    consistency checks on that repair (monotonicity + real-price cross-check, see
    `_repaired_series_violation` / `_price_mismatch`).

    Layer 2 of the self-computed adjustment factor (`close_repair.py`), OFF unless
    `MIKE_CLOSE_REPAIR=1`. Wired HERE and nowhere else because `_fetch_rows` is the single point
    at which a vendor `Close` enters this module; `factor_terp = Close/Price` and everything
    downstream of it — `entry_adj`, the report's tỉ suất, and `report_return_gate`'s T1 test — are
    derived from exactly this pair.

    Never raises and never degrades an entry: on ANY failure it returns the original rows plus a
    note. A repair that cannot be computed must leave the existing gate blocking, not replace one
    unverifiable number with another.
    """
    if not rows:
        return rows, {}, {}, {}
    try:
        import duckdb

        import close_repair
        from corp_action_lib import events as ca_events
    except Exception as e:                       # close_repair absent, BQ lib absent, no duckdb
        return rows, {"_error": f"không nạp được close_repair ({str(e)[:90]})"}, {}, {}
    if not close_repair.enabled():
        return rows, {}, {}, {}

    try:
        keys = [(t, a) for (t, a) in rows]
        tickers = sorted({t for t, _ in keys})
        # the window must start before the OLDEST asof (the ffill band guard reads a neighbour bar)
        # and end at the series, never at today's date — see close_repair's docstring.
        start = min(a for _, a in keys)
        con = duckdb.connect()
        con.execute("SET threads=1")
        glob = f"{cache_dir}/ticker/*.parquet"
        tk_sql = ",".join("?" for _ in tickers)
        bars = con.execute(
            f"""
            SELECT ticker, CAST(time AS VARCHAR), Close, Price, High, Low, Volume
            FROM read_parquet('{glob}')
            WHERE ticker IN ({tk_sql})
              AND time >= CAST(? AS DATE) - INTERVAL 25 DAY
              AND Close > 0 AND Price > 0
            ORDER BY ticker, time
            """,
            [*tickers, start],
        ).fetchall()
        con.close()
        series = {}
        for tk, d, c, pr, hi, lo, vol in bars:
            # `volume=None` (missing, never a real 0) is a distinct case from `volume=0.0` (real
            # no-trade session) for `price_crosscheck`'s §29 evidence-based label — do not collapse
            # a genuinely-missing reading into 0 with `vol or 0`.
            series.setdefault(tk, []).append(
                {"d": d, "close": float(c), "price": float(pr),
                 "high": float(hi or 0), "low": float(lo or 0),
                 "volume": float(vol) if vol is not None else None})
        series_max = cache_max_date or max((b["d"] for s in series.values() for b in s), default=None)
        if not series_max:
            return rows, {"_error": "không xác định được ngày cuối của chuỗi giá"}, {}, {}
        evs = {}
        for e in ca_events(tickers, since=start, until=series_max):
            evs.setdefault(e["ticker"], []).append(e)
    except Exception as e:
        return rows, {"_error": f"không dựng được dữ liệu sửa Close ({str(e)[:90]})"}, {}, {}

    out, reps, violations, price_mismatches = dict(rows), {}, {}, {}
    for (tk, asof), (time_used, close_at, price_at) in rows.items():
        try:
            rep = close_repair.repair_row(
                tk, {"d": time_used, "close": close_at, "price": price_at,
                     "high": next((b["high"] for b in series.get(tk, []) if b["d"] == time_used), 0),
                     "low": next((b["low"] for b in series.get(tk, []) if b["d"] == time_used), 0)},
                evs.get(tk, []), series.get(tk, []), series_max)
        except Exception as e:                    # a single bad ticker must not sink the report
            # Keep the parser's own words. Swallowing them and printing a guessed cause is the
            # §29 failure mode: the caller then reports a reason nothing ever read.
            reps[(tk, asof)] = f"lỗi khi sửa Close: {type(e).__name__}: {str(e)[:120]}"
            continue
        reps[(tk, asof)] = rep
        if rep.repaired:
            out[(tk, asof)] = (time_used, rep.close, price_at)
            try:
                v = _repaired_series_violation(
                    tk, asof, evs.get(tk, []), series.get(tk, []), series_max)
            except Exception:                     # the invariant check itself must not sink a repair
                v = None
            if v is not None:
                violations[(tk, asof)] = v
            try:
                pm = _price_mismatch(tk, asof, evs.get(tk, []), series.get(tk, []), series_max)
            except Exception:                     # the cross-check itself must not sink a repair
                pm = None
            if pm is not None:
                price_mismatches[(tk, asof)] = pm
    return out, reps, violations, price_mismatches

def cache_vintage(cache_dir=None) -> dict:
    """{year: mtime} for `bq_cache/ticker/*.parquet` plus `ticker_1m` — the freshness fault line.

    `_fetch_rows` reads the factor out of the YEAR file containing `asof`, while the reports read
    today's price out of `ticker_1m.parquet`. Those are different files on different refresh
    paths: measured 2026-08-13, `2025.parquet` was last written 07-29 and `2026.parquet` 08-12.
    `Close/Price` is retroactively restated, so a stale year file silently UNDER-adjusts any entry
    dated in that year — the exact bug this module exists to kill, coming back through the cache
    instead of through the formula. No paper book has a pre-2026 entry today, which is why it has
    not bitten; the assert goes in before one does.
    """
    cache_dir = Path(cache_dir) if cache_dir else DEFAULT_CACHE
    out = {}
    for p in sorted((cache_dir / "ticker").glob("*.parquet")):
        out[p.stem] = p.stat().st_mtime
    p1m = cache_dir / "ticker_1m.parquet"
    if p1m.exists():
        out["ticker_1m"] = p1m.stat().st_mtime
    return out


def stale_years(cache_dir=None, tol_days: float = VINTAGE_TOL_DAYS) -> dict:
    """{year: lag_days} for year files written materially before the newest cache file."""
    v = cache_vintage(cache_dir)
    if not v:
        return {}
    newest = max(v.values())
    return {y: (newest - m) / 86400.0 for y, m in v.items()
            if y != "ticker_1m" and (newest - m) / 86400.0 > tol_days}


def _rights_free_factor(ticker, asof, factor_terp, until, cache_dir):
    """(factor_accrue_only, rights_ex_dates, error|None) — strip the rights component out.

    The corp-action feed carries no subscription price for a rights issue (`value_per_share` is
    NULL on every one), so the rights adjustment is recovered as the RESIDUAL of the ex-date price
    step after dividing out every other event that went ex the same day:

        adj_day    = ratio(prev trading day) / ratio(ex-date)      # ratio = Close/Price
        adj_others = Π (P_cum − D)/P_cum  for cash dividends
                     Π 1/(1 + r)          for stock dividends / bonus shares
        adj_rights = adj_day / adj_others

    Any same-day event whose size is unknown makes the residual meaningless, so it returns an
    error instead of a number. Non-accruing ISS (ESOP, placement) contribute nothing to the price
    step by construction (`corp_action_lib`) and are correctly skipped.
    """
    # Fast path: no price adjustment at all → no corp-action of any kind → skip BQ entirely.
    # This is the control property stated in the module docstring: factor == 1.0 exactly when
    # nothing happened. Avoids spurious BQ calls (and BQ-unavailable warnings) for clean positions.
    if abs(factor_terp - 1.0) <= FACTOR_EPS:
        return factor_terp, (), None

    from corp_action_lib import events as ca_events, is_price_adjusting

    evs = ca_events([ticker], since=asof, until=until)
    rights = [e for e in evs if e["event_code"] == "ISS"
              and (e.get("issue_method_name_vi") or "").strip() == RIGHTS_METHOD]
    if not rights:
        return factor_terp, (), None

    ex_dates = sorted({e["exright_date"] for e in rights})
    if until is None:
        return None, tuple(ex_dates), "không xác định được ngày mới nhất của cache giá"
    total = 1.0
    for d in ex_dates:
        step = _ratio_step(ticker, d, cache_dir)
        if step is None:
            return None, tuple(ex_dates), f"thiếu giá quanh ex-date {d} trong cache"
        prev_ratio, ex_ratio, prev_price = step
        if not (prev_ratio > 0 and ex_ratio > 0):
            return None, tuple(ex_dates), f"tỉ số Close/Price không hợp lệ quanh {d}"
        adj_day = prev_ratio / ex_ratio

        adj_others = 1.0
        for e in (x for x in evs if x["exright_date"] == d):
            method = (e.get("issue_method_name_vi") or "").strip()
            if e["event_code"] == "ISS" and method == RIGHTS_METHOD:
                continue
            if not is_price_adjusting(e):
                continue                     # ESOP/placement: no price step to account for
            if e["event_code"] == "DIV":
                vps = e.get("value_per_share")
                if vps is None or float(vps) <= 0:
                    return None, tuple(ex_dates), f"cổ tức tiền {d} không có value_per_share"
                adj_others *= (prev_price - float(vps)) / prev_price
            else:
                r = e.get("exercise_ratio")
                if r is None or float(r) <= 0:
                    return None, tuple(ex_dates), f"ISS {d} ({method}) không có exercise_ratio"
                adj_others *= 1.0 / (1.0 + float(r))

        adj_rights = adj_day / adj_others
        if not (0.0 < adj_rights <= 1.0 + FACTOR_EPS):
            return None, tuple(ex_dates), (
                f"phần quyền mua tách ra tại {d} = {adj_rights:.6f} ngoài (0,1] — "
                f"không tin được, không rebase theo accrue-only")
        total *= adj_rights

    return factor_terp / total, tuple(ex_dates), None


def _ratio_step(ticker, exright_date, cache_dir):
    """(ratio_prev, ratio_ex, raw_price_prev) around `exright_date`, or None."""
    import duckdb

    con = duckdb.connect()
    con.execute("SET threads=1")
    try:
        rows = con.execute(
            f"""
            SELECT time, Close / NULLIF(Price, 0) AS ratio, Price
            FROM read_parquet('{cache_dir}/ticker/*.parquet')
            WHERE ticker = ?
              AND time BETWEEN CAST(? AS DATE) - INTERVAL 15 DAY AND CAST(? AS DATE)
              AND Price > 0 AND Close > 0
            ORDER BY time DESC LIMIT 2
            """,
            [ticker, exright_date, exright_date],
        ).fetchall()
    except Exception:          # missing/corrupt cache is a "cannot resolve", not a crash
        return None
    finally:
        con.close()
    # LIMIT 2 descending gives [ex-date, previous trading day] — only valid if the first row IS
    # the ex-date (otherwise the ex-date is missing from the cache and the residual is garbage)
    if len(rows) < 2 or str(rows[0][0]) != exright_date:
        return None
    return float(rows[1][1]), float(rows[0][1]), float(rows[1][2])


def adjust_entries(items, cache_dir=None, convention="accrue_only") -> dict:
    """Rebase many frozen entries at once.

    items: iterable of (ticker, asof_YYYY_MM_DD, entry_price)
    returns: {(ticker, asof): AdjustedEntry}

    Keyed by (ticker, asof), NOT by ticker: the same name legitimately appears in two paper books
    with different entry dates and different entry prices (MBB/ACB/FPT are in both alphalens and
    converge). A ticker-only key silently lets one book's entry overwrite the other's — that bug
    was caught by the corp-action cross-check and is pinned by selfcheck case 11.

    Never raises: any failure degrades that position to `status="NO_DATA"` with `entry_adj ==
    entry_price` (i.e. exactly the old, pre-fix behaviour) and a note explaining why. A paper
    report must not be aborted by this block, but it must never silently pretend it adjusted.
    """
    items = [(t, str(a), float(p)) for t, a, p in items]
    cache_dir = Path(cache_dir) if cache_dir else DEFAULT_CACHE

    try:
        rows = _fetch_rows(items, cache_dir)
        fetch_err = None
    except Exception as e:  # duckdb missing, cache missing, corrupt parquet...
        rows, fetch_err = {}, str(e)[:120]

    try:
        stale = stale_years(cache_dir)
        vintage = cache_vintage(cache_dir)
        newest_year = max((y for y in vintage if y != "ticker_1m"), default=None)
    except Exception:                       # cache absent -> the NO_DATA path already covers it
        stale, newest_year = {}, None

    try:
        cache_max_date = _cache_max_date(cache_dir)
    except Exception:
        cache_max_date = None

    # Layer 2 (OFF by default, see `_repair_close`). Placed after `_fetch_rows` and before
    # `factor_terp` is read, because the whole point is that `factor_terp` must be computed off a
    # COMPLETE adjustment. It only ever replaces `Close`; `Price` and `time_used` are untouched.
    rows, repairs, repair_violations, price_mismatches = _repair_close(
        rows, items, cache_dir, cache_max_date)

    out = {}
    for ticker, asof, entry_price in items:
        row = rows.get((ticker, asof))
        if row is None:
            out[(ticker, asof)] = AdjustedEntry(
                ticker, entry_price, entry_price, None, None, None, "NO_DATA",
                f"không có giá {asof} trong cache" + (f" ({fetch_err})" if fetch_err else ""),
            )
            continue

        time_used, close_at, price_at = row
        factor_terp = close_at / price_at
        rep = repairs.get((ticker, asof))
        if isinstance(rep, str):                  # the repair layer failed on THIS ticker
            prov = {"adj_source": "vendor", "repair_note": rep}
        else:
            prov = {"adj_source": rep.adj_source if rep is not None else "vendor",
                    "repair_note": (rep.reason if rep is not None and rep.repaired else None)}

        # close_repair claimed self_computed for this entry AND its own repaired ratio series
        # still breaks the non-decreasing invariant — mechanical evidence (§29) that
        # `corporate_action` itself is wrong for this ticker/window, not that the vendor needs a
        # cap. Fail closed: keep the raw entry, do not guess at a corrected factor.
        viol = repair_violations.get((ticker, asof))
        if viol is not None:
            d_bad, r0, r_min = viol
            out[(ticker, asof)] = AdjustedEntry(
                ticker, entry_price, entry_price, factor_terp, price_at, time_used,
                "REPAIR_INCONSISTENT",
                f"close_repair đã tự sửa Close (self_computed) nhưng hệ số Close/Price SAU sửa "
                f"vẫn GIẢM theo thời gian ({r0:.6f} tại {asof} → {r_min:.6f} tại {d_bad}) — bằng "
                f"chứng cơ học rằng corporate_action cho {ticker} trong cửa sổ này sai/thiếu sự "
                f"kiện, không phải vendor chưa hồi tố. Không đoán số đúng, giữ giá gốc.",
                factor_terp=factor_terp, convention=convention, **prov,
            )
            continue

        # Independent GROSS-error screen against REAL price action at the ex-date (Việc nhỏ 3,
        # 2026-09-29): catches the direction `viol` above structurally cannot — corporate_action
        # OVERSTATING an event keeps the repaired ratio series monotone (no `viol`) but disagrees
        # with what actually traded. Checked SECOND, only when `viol` above did not already fire,
        # because it is a noisier, threshold-based screen (see close_repair.PRICE_XCHECK_TOL
        # comment block) rather than a mechanical invariant.
        pmiss = price_mismatches.get((ticker, asof))
        if pmiss is not None:
            detail = "; ".join(f"{xc.ex}: f={xc.f_formula:.6f} vs giá thật r_real={xc.r_real:.6f} "
                               f"(dev={xc.dev:+.2%})" for xc in pmiss)
            out[(ticker, asof)] = AdjustedEntry(
                ticker, entry_price, entry_price, factor_terp, price_at, time_used,
                "REPAIR_PRICE_MISMATCH",
                f"close_repair đã tự sửa Close (self_computed) nhưng hệ số công thức LỆCH biến "
                f"động giá THẬT tại ex-date quá PRICE_XCHECK_TOL ({detail}) — nghi corporate_action "
                f"sai/thiếu sự kiện cho {ticker} theo chiều LÀM ĐẸP tỉ suất (bất biến đơn điệu ở "
                f"trên không bắt được chiều này). Không đoán số đúng, giữ giá gốc; cần Winston "
                f"đối soát lại corporate_action.",
                factor_terp=factor_terp, convention=convention, **prov,
            )
            continue

        # Invariant: adjustment only ever scales historical prices DOWN (dividends/dilution are
        # value leaving the share). factor > 1 means the pair is not what we think it is.
        if not (0.0 < factor_terp <= 1.0 + FACTOR_EPS):
            out[(ticker, asof)] = AdjustedEntry(
                ticker, entry_price, entry_price, factor_terp, price_at, time_used, "BAD_FACTOR",
                f"Close/Price = {factor_terp:.6f} ngoài (0,1] — không rebase, giữ giá gốc",
                factor_terp=factor_terp, convention=convention, **prov,
            )
            continue

        # The factor was read out of the year file containing `asof`. If that file is stale
        # relative to the rest of the cache, its Close/Price has not absorbed recent events and
        # the rebase would UNDER-adjust — refuse rather than under-adjust silently.
        yr = asof[:4]
        if yr in stale:
            out[(ticker, asof)] = AdjustedEntry(
                ticker, entry_price, entry_price, factor_terp, price_at, time_used,
                "VINTAGE_STALE",
                f"bq_cache/ticker/{yr}.parquet cũ hơn {newest_year}.parquet {stale[yr]:.1f} ngày "
                f"— Close/Price của {asof} có thể chưa gồm sự kiện gần đây, KHÔNG rebase",
                factor_terp=factor_terp, convention=convention, **prov,
            )
            continue

        rights = ()
        if convention == "accrue_only":
            try:
                factor, rights, err = _rights_free_factor(
                    ticker, asof, factor_terp, cache_max_date, cache_dir)
            except Exception as e:                    # BQ down, duckdb missing, ...
                factor, err = None, f"không tra được corporate_action: {str(e)[:90]}"
            if factor is None:
                # rights==() here means either (a) BQ failed before we could check, or
                # (b) rights were found but their factor couldn't be resolved (rights non-empty).
                # Use different note text so the reader knows which case they're looking at.
                if rights:
                    note_text = (f"có quyền mua sau {asof} nhưng không tách được phần quyền "
                                 f"({err}) — KHÔNG dùng TERP thay thế, giữ giá gốc")
                else:
                    note_text = (f"BQ không khả dụng, không xác định được quyền mua sau {asof} "
                                 f"({err}) — tạm giữ giá gốc đến khi BQ phục hồi")
                out[(ticker, asof)] = AdjustedEntry(
                    ticker, entry_price, entry_price, None, price_at, time_used,
                    "RIGHTS_UNRESOLVED",
                    note_text,
                    factor_terp=factor_terp, convention=convention, rights_events=rights,
                    **prov,
                )
                continue
        else:
            factor = factor_terp

        note = None
        if abs(entry_price - price_at) / price_at > ENTRY_MATCH_TOL:
            note = (f"entry_price {entry_price:,.0f} ≠ giá thô {time_used} ({price_at:,.0f}) "
                    f"— kiểm tra lại ngày chụp giá trong file paper")
        if rights:
            note = ((note + " · ") if note else "") + (
                f"quyền mua {', '.join(rights)} bị LOẠI khỏi tỉ suất (sổ paper không có tài khoản "
                f"tiền, không thực hiện quyền): factor {factor:.6f} thay vì TERP {factor_terp:.6f}")

        status = "ADJUSTED" if factor < 1.0 - FACTOR_EPS else "UNCHANGED"
        out[(ticker, asof)] = AdjustedEntry(
            ticker, entry_price, entry_price * factor, factor, price_at, time_used, status, note,
            factor_terp=factor_terp, convention=convention, rights_events=rights, **prov,
        )
    return out


def _cache_max_date(cache_dir) -> str | None:
    """Newest trading day in the price cache — the vintage every factor here speaks for.

    This, not `date.today()`, is the right end of the corp-action window: an event that went ex
    after the cache's last day is not yet in `Close/Price`, so pulling it into the accrue-only
    residual would subtract an adjustment the price series has not made.
    """
    import duckdb

    con = duckdb.connect()
    con.execute("SET threads=1")
    try:
        row = con.execute(
            f"SELECT MAX(time) FROM read_parquet('{cache_dir}/ticker/*.parquet')").fetchone()
        return str(row[0]) if row and row[0] else None
    finally:
        con.close()


# --------------------------------------------------------------------------------------------
# selfcheck
# --------------------------------------------------------------------------------------------
def _selfcheck() -> int:
    """Offline logic cases + live-cache cases (skipped, not failed, when the cache is absent)."""
    fails, skips, ran = [], [], []

    # counted, never typed — a hand-written "N/N" in a summary line is a number nobody re-derives
    def check(name, cond, detail=""):
        ran.append(name)
        print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f" — {detail}" if detail else ""))
        if not cond:
            fails.append(name)

    print("== A. Logic thuần (không cần cache) ==")

    # 1. CONTROL — no corporate action => factor 1.0 => number must not move AT ALL.
    e = AdjustedEntry("CTRL", 25000.0, 25000.0 * 1.0, 1.0, 25000.0, "2026-06-30", "UNCHANGED")
    old_pct = (26000.0 - 25000.0) / 25000.0 * 100
    check("1. control: factor=1 ⇒ pct y hệt trước khi sửa",
          e.pct_vs(26000.0) == old_pct, f"{e.pct_vs(26000.0):.6f}% == {old_pct:.6f}%")

    # 2. sign-flip case reproduced from the real MBB numbers
    e = AdjustedEntry("MBB", 25200.0, 25200.0 * 0.800794, 0.800794, 25200.0, "2026-06-30", "ADJUSTED")
    check("2. MBB: entry_adj = 25.200 × 0,800794 = 20.180",
          abs(e.entry_adj - 20180.0) < 0.5, f"{e.entry_adj:,.2f}")
    check("3. MBB: pct đảo dấu âm→dương",
          e.pct_vs(20450.0) > 0 > (20450.0 - 25200.0) / 25200.0 * 100,
          f"sửa {e.pct_vs(20450.0):+.2f}% vs lỗi {(20450.0-25200.0)/25200.0*100:+.2f}%")

    # 3. degradation must be visible AND must fall back to the old behaviour, not to garbage
    r = adjust_entries([("__NOSUCHTICKER__", "2026-06-30", 10000.0)], cache_dir=DEFAULT_CACHE)
    d = r[("__NOSUCHTICKER__", "2026-06-30")]
    check("4. mã không có dữ liệu ⇒ NO_DATA, giữ nguyên giá gốc, không ném exception",
          d.status == "NO_DATA" and d.entry_adj == 10000.0 and d.degraded and d.note)

    r = adjust_entries([("X", "2026-06-30", 1.0)], cache_dir="/nonexistent-cache-path")
    check("5. cache hỏng/thiếu ⇒ degrade an toàn, không ném exception",
          r[("X", "2026-06-30")].status == "NO_DATA" and r[("X", "2026-06-30")].entry_adj == 1.0)

    # 4. the factor>1 guard (a pair that is not Close/Price would trip this)
    bad = AdjustedEntry("B", 100.0, 100.0, 1.4, 100.0, "d", "BAD_FACTOR", "n")
    check("6. guard factor>1 ⇒ BAD_FACTOR, entry_adj = giá gốc", bad.degraded and bad.entry_adj == 100.0)

    # 7-8. REPAIR_INCONSISTENT (Việc nhỏ 2, 2026-09-29): close_repair's OWN repaired ratio series
    # must still satisfy the non-decreasing invariant. Mirrors the real FPT case (exercise_ratio
    # 0.10, ex-date 2026-09-21) with the event's exercise_ratio mutated — mechanical evidence
    # (§29, kb/coding_guidelines.md) that corporate_action itself is wrong for that ticker/window,
    # not that the vendor needs a cap. Pure logic on a synthetic series/events — no cache/BQ needed.
    _fpt_series = [
        {"d": "2026-06-30", "close": 70200.0, "price": 70200.0, "high": 0.0, "low": 0.0},
        {"d": "2026-09-18", "close": 65180.0, "price": 71700.0, "high": 0.0, "low": 0.0},
        {"d": "2026-09-22", "close": 63700.0, "price": 63700.0, "high": 0.0, "low": 0.0},
    ]
    _fpt_max = "2026-09-22"
    _true_ev = {"ticker": "FPT", "exright_date": "2026-09-21", "event_code": "ISS",
                "issue_method_name_vi": "Cổ phiếu thưởng", "exercise_ratio": 0.1}
    _bad_ev = {**_true_ev, "exercise_ratio": 0.05}
    v_true = _repaired_series_violation("FPT", "2026-06-30", [_true_ev], _fpt_series, _fpt_max)
    v_bad = _repaired_series_violation("FPT", "2026-06-30", [_bad_ev], _fpt_series, _fpt_max)
    check("7. ca FPT thật (exercise_ratio đúng 0,10) ⇒ chuỗi đã sửa KHÔNG vi phạm bất biến",
          v_true is None, f"{v_true}")
    check("8. mutate exercise_ratio 0,10→0,05 (corporate_action sai) ⇒ BẮT ĐƯỢC vi phạm cơ học, "
          "KHÔNG âm thầm dùng số sai",
          v_bad is not None and (v_bad[1] - v_bad[2]) / v_bad[1] > TERP_DROP_TOL, f"{v_bad}")

    # 9-10. PRICE_XCHECK_TOL cross-check (Việc nhỏ 3, 2026-09-29, close_repair.price_crosscheck):
    # independent screen against REAL raw price at ex-date, catching the mirror-image defect 7-8
    # structurally cannot — corporate_action OVERSTATING an event (ratio too HIGH) keeps the
    # repaired series monotone (no `viol`) but disagrees with what actually traded.
    #
    # ⚠️ Uses a SEPARATE real-data fixture (`_fpt_series_real`), NOT `_fpt_series` above: the round-1
    # version of this check reused `_fpt_series` (High=Low=0,0 on every bar) and quant-skeptic
    # (REFUTED, round 1) caught that this zeroes-out `_band_lifted_suspect`'s guard entirely — the
    # selfcheck passed while the real code, on real bars, refused ~94% of events (including FPT
    # itself) as "ffill-suspect" because the guard lifted the ex-date bar's band with the CUM bar's
    # ratio (wrong side of the event boundary). Fixed in `price_crosscheck` (see its `chained_ex`
    # comment); this fixture uses ACTUAL `tav2_bq.ticker` bars (queried 2026-09-29) so the guard
    # runs for real and the numbers below are independently reproducible.
    _fpt_series_real = [
        {"d": "2026-09-14", "close": 72400.0, "price": 72400.0, "high": 73600.0, "low": 72000.0},
        {"d": "2026-09-15", "close": 66090.0, "price": 72700.0, "high": 66730.0, "low": 65910.0},
        {"d": "2026-09-16", "close": 67090.0, "price": 73800.0, "high": 67090.0, "low": 65000.0},
        {"d": "2026-09-17", "close": 67550.0, "price": 74300.0, "high": 67550.0, "low": 66000.0},
        {"d": "2026-09-18", "close": 65180.00000000001, "price": 71700.0, "high": 68000.0,
         "low": 65180.00000000001},
        {"d": "2026-09-21", "close": 66400.0, "price": 66400.0, "high": 66800.0, "low": 65000.0},
        {"d": "2026-09-22", "close": 66600.0, "price": 66600.0, "high": 67000.0, "low": 66200.0},
    ]
    _fpt_max_real = "2026-09-22"
    # Real market step across the ex-date: P_cum=71.700 (2026-09-18, last session before ex) →
    # P_ex=66.400 (2026-09-21, first session on/after ex) → r_real = 1,079819. This matches the
    # ORIGINAL finding's own manual sanity check ("71.700(09-18)→66.400(09-21), khớp bonus 10%",
    # paper-report-fpt-double-adjust-fix-20260929 viec1) almost exactly (formula f=1,10 vs r_real
    # 1,079819 ⇒ dev=−1,83%, i.e. FPT also moved ~+1,8% on real market terms that session).
    import close_repair as _cr
    _gross_bad_ev = {**_true_ev, "exercise_ratio": 1.0}    # 10x fat-finger: f=2,00 vs f=1,10 true
    _micro_bad_ev = {**_true_ev, "exercise_ratio": 0.15}   # quant-skeptic's own mutation: f=1,15
    xc_true, notes_true = _cr.price_crosscheck_after(
        "2026-06-30", [_true_ev], _fpt_series_real, _fpt_max_real)
    xc_gross, _notes_gross = _cr.price_crosscheck_after(
        "2026-06-30", [_gross_bad_ev], _fpt_series_real, _fpt_max_real)
    xc_micro, _notes_micro = _cr.price_crosscheck_after(
        "2026-06-30", [_micro_bad_ev], _fpt_series_real, _fpt_max_real)
    check("9. ca FPT thật (0,10) trên dữ liệu giá THẬT ⇒ ĐƯỢC KIỂM (không bị từ chối oan), công "
          "thức khớp giá thật trong PRICE_XCHECK_TOL, KHÔNG mismatch",
          xc_true == () and notes_true and "khớp" in notes_true[0], f"{xc_true} · note={notes_true}")
    check("10a. mutate 0,10→1,0 (sai 10 lần, fat-finger) ⇒ BẮT ĐƯỢC bằng giá thật (bất biến đơn "
          "điệu 7-8 KHÔNG bắt được ca này vì hệ số CAO hơn không phá tính đơn điệu)",
          len(xc_gross) == 1 and xc_gross[0].mismatch, f"{xc_gross}")
    check("10b. mutate 0,10→0,15 (đúng mutation của quant-skeptic, +4,5% hệ số) ⇒ KHÔNG bắt được "
          "— GIỚI HẠN ĐÃ CÔNG BỐ của phương pháp (lệch 6,1% trên dữ liệu thật nằm trong nhiễu 1 "
          "phiên bình thường đo thực nghiệm ~1,4% median; PRICE_XCHECK_TOL=20% hiệu chỉnh để tránh "
          "báo động giả trên >1.500 sự kiện thật, không phải bỏ sót cài đặt)",
          xc_micro == (), f"{xc_micro}")

    # 11. Việc A (dispatch Taylor_20260929_042515, §29 kb/coding_guidelines.md): nhãn lý do chối
    # phiên ex-date "chained" phải RẼ THEO Volume — quant-skeptic (round 2, killer_objection) đo
    # thật VHM 2026-08-06 (KL 16.902.474) và TRC 2026-09-15 (KL 611.072) bị nhãn "ffill/không
    # giao dịch" dù CÓ giao dịch thật; nguyên nhân thật là vendor báo giá Price trễ 1 phiên trên
    # dòng ex-date. Bar THẬT từ tav2_bq.ticker (truy vấn 2026-09-29), event thật từ
    # tav2_bq.corporate_action. Cả 3 ca dưới đây phải giữ NGUYÊN quyết định từ chối
    # (mismatch=False, không repair) — chỉ lý do hiển thị đổi, không nới coverage.
    _vhm_series = [
        {"d": "2026-08-03", "close": 74000.0, "price": 148000.0, "high": 74850.0, "low": 72550.0,
         "volume": 5338830.0},
        {"d": "2026-08-04", "close": 76450.0, "price": 152900.0, "high": 76650.0, "low": 73400.0,
         "volume": 6362273.0},
        {"d": "2026-08-05", "close": 76500.0, "price": 153000.0, "high": 79400.0, "low": 76500.0,
         "volume": 10722235.0},
        {"d": "2026-08-06", "close": 77100.0, "price": 153000.0, "high": 81700.0, "low": 76800.0,
         "volume": 16902474.0},
        {"d": "2026-08-07", "close": 73000.0, "price": 73000.0, "high": 76800.0, "low": 73000.0,
         "volume": 9164067.0},
    ]
    _vhm_max = "2026-08-07"
    _vhm_ev = {"ticker": "VHM", "exright_date": "2026-08-06", "event_code": "ISS",
               "issue_method_name_vi": "Trả Cổ tức bằng Cổ phiếu", "exercise_ratio": 1.0}
    xc_vhm, notes_vhm = _cr.price_crosscheck_after("2026-06-30", [_vhm_ev], _vhm_series, _vhm_max)
    check("11a. VHM 2026-08-06 (Volume=16.902.474>0 THẬT, ex-date Price lặp lại 153.000 phiên "
          "trước): nhãn phải nói 'nghi vendor báo giá trễ' kèm đúng KL, KHÔNG PHẢI 'không giao "
          "dịch' — quyết định vẫn từ chối như trước (không mismatch, không repair)",
          xc_vhm == () and notes_vhm and "vendor báo giá trễ" in notes_vhm[0]
          and "16,902,474" in notes_vhm[0], f"{notes_vhm}")

    _trc_series = [
        {"d": "2026-09-11", "close": 20450.0, "price": 81800.0, "high": 20820.0, "low": 20380.0,
         "volume": 95900.0},
        {"d": "2026-09-14", "close": 20150.0, "price": 80600.0, "high": 20600.0, "low": 20120.0,
         "volume": 149500.0},
        {"d": "2026-09-15", "close": 21550.0, "price": 80600.0, "high": 21550.0, "low": 21100.0,
         "volume": 611072.0},
        {"d": "2026-09-16", "close": 22400.0, "price": 22400.0, "high": 22600.0, "low": 21550.0,
         "volume": 445944.0},
        {"d": "2026-09-17", "close": 22300.0, "price": 22300.0, "high": 22400.0, "low": 21500.0,
         "volume": 161472.0},
    ]
    _trc_max = "2026-09-17"
    _trc_ev = {"ticker": "TRC", "exright_date": "2026-09-15", "event_code": "ISS",
               "issue_method_name_vi": "Cổ phiếu thưởng", "exercise_ratio": 3.0}
    xc_trc, notes_trc = _cr.price_crosscheck_after("2026-06-30", [_trc_ev], _trc_series, _trc_max)
    check("11b. TRC 2026-09-15 (Volume=611.072>0 THẬT, ex-date Price lặp lại 80.600 phiên "
          "trước): nhãn phải nói 'nghi vendor báo giá trễ' kèm đúng KL — quyết định vẫn từ chối "
          "như trước",
          xc_trc == () and notes_trc and "vendor báo giá trễ" in notes_trc[0]
          and "611,072" in notes_trc[0], f"{notes_trc}")

    # Ca đối chứng Volume==0: SYNTHETIC, không phải bar thật — lý do khai rõ (§29, không giấu):
    # quét TOÀN BỘ 15 ứng viên "ex-date Volume=0 thật" trong cả cửa sổ hiệu chỉnh
    # 2025-01-01..2026-09-15 (BCB×2, BMV, BTT, BTV, CQT, DNN, KTL, LM8, NHC, PVM, SDN, SEB, VAF,
    # VLW — truy vấn 2026-09-29) qua ĐÚNG `price_crosscheck_after` thật, và CẢ 15/15 bị từ chối
    # SỚM HƠN bởi guard ffill có sẵn trên phiên CUM (`_band_lifted_suspect`, lỗi RIÊNG đã biết —
    # xem `recommended_reruns` #3 của quant-skeptic round 2: các mã Volume=0 gần sự kiện hầu hết
    # là mã thanh khoản cực mỏng, High=Low=Price gần như mọi phiên, nên bất kỳ neighbour nào có
    # giá khác cũng làm lift-band lệch quá dung sai 1e-9) — nhánh "Volume==0 ⇒ ffill" bên dưới vì
    # vậy KHÔNG có ca thật nào chạy tới được trong mẫu hiện tại. Dùng fixture số học sạch (giống
    # tiền lệ case 7-8 phía trên: "Pure logic on a synthetic series/events") để kiểm ĐÚNG nhánh mã
    # nguồn, không giả vờ đây là số thị trường thật.
    _syn0_series = [
        {"d": "2024-01-01", "close": 100.0, "price": 100.0, "high": 100.0, "low": 100.0,
         "volume": 500.0},
        {"d": "2024-01-02", "close": 110.0, "price": 115.0, "high": 116.0, "low": 114.0,
         "volume": 600.0},
        {"d": "2024-01-03", "close": 110.0, "price": 115.0, "high": 0.0, "low": 0.0,
         "volume": 0.0},
    ]
    _syn0_ev = {"ticker": "SYN", "exright_date": "2024-01-03", "event_code": "ISS",
                "issue_method_name_vi": "Cổ phiếu thưởng", "exercise_ratio": 0.1}
    xc_syn0, notes_syn0 = _cr.price_crosscheck_after(
        "2023-12-01", [_syn0_ev], _syn0_series, "2024-01-03")
    check("11c. [SYNTHETIC, không phải bar thật — xem comment] Volume=0,0 trên phiên ex-date, "
          "phiên cum KHÔNG bị nghi ffill: nhãn PHẢI là 'không giao dịch (ffill)', KHÔNG PHẢI "
          "'vendor báo giá trễ' — quyết định vẫn từ chối như trước",
          xc_syn0 == () and notes_syn0 and "không giao dịch phiên này (ffill)" in notes_syn0[0],
          f"{notes_syn0}")

    # Ca chuỗi KHÔNG mang Volume (caller cũ / fixture thiếu cột) — PHẢI fallback nhãn trung thực,
    # TUYỆT ĐỐI không đoán 1 trong 2 nhánh trên khi thiếu dữ liệu (§29). Same real VHM bars, chỉ
    # bỏ field "volume" để test riêng đường fallback.
    _vhm_series_novol = [{k: v for k, v in b.items() if k != "volume"} for b in _vhm_series]
    xc_novol, notes_novol = _cr.price_crosscheck_after(
        "2026-06-30", [_vhm_ev], _vhm_series_novol, _vhm_max)
    check("11d. chuỗi KHÔNG mang Volume (thiếu field) ⇒ fallback nhãn trung thực 'chưa phân biệt "
          "được', KHÔNG đoán bừa 1 trong 2 nhánh — quyết định vẫn từ chối như trước",
          xc_novol == () and notes_novol and "chưa phân biệt được" in notes_novol[0],
          f"{notes_novol}")

    print("== B. Dữ liệu thật trong cache ==")
    cache_ok = (DEFAULT_CACHE / "ticker").is_dir()
    if not cache_ok:
        print("  SKIP  không có data/bq_cache/ticker — bỏ qua nhóm B")
        skips.append("B")
    else:
        live = adjust_entries(
            [("MBB", "2026-06-30", 25200.0), ("STB", "2026-06-30", 73800.0),
             ("ACB", "2026-06-30", 22650.0), ("HDB", "2026-06-30", 25850.0)],
        )
        m = live[("MBB", "2026-06-30")]
        check("7. MBB thật: Close/Price (TERP) ≈ 0,800794 — quy ước accrue-only kiểm ở ca 12-14",
              m.is_adjusted and abs(m.factor_terp - 0.800794) < 1e-5,
              f"terp={m.factor_terp:.6f} accrue_only={m.factor:.6f} entry_adj={m.entry_adj:,.1f}")

        # THE control assertion the dispatch demanded: names with no corp-action must be untouched.
        # FPT KHÔNG dùng được ở đây nữa — có bonus-share ex-date 2026-09-21 (Layer 2 self-computed
        # sẽ sửa Close, factor 0,909091 ≠ 1,0). STB xác nhận zero price-adjusting event
        # 2026-06-30..2026-09-27 (corp_action_lib.events), thay thế đúng tinh thần "không có
        # corp-action sau entry" mà case này muốn kiểm.
        for tk, ep in (("STB", 73800.0), ("ACB", 22650.0), ("HDB", 25850.0)):
            a = live[(tk, "2026-06-30")]
            check(f"8. {tk} (không có corp-action sau entry): entry_adj == entry_price TUYỆT ĐỐI",
                  a.status == "UNCHANGED" and a.entry_adj == ep and a.factor == 1.0,
                  f"status={a.status} entry_adj={a.entry_adj:,.1f}")

        # recorded-entry validation must fire on the known alphalens metadata slip (entry_date
        # says 2026-07-01 but every entry_price is the 2026-06-30 raw close)
        slip = adjust_entries([("FPT", "2026-07-01", 70200.0)])[("FPT", "2026-07-01")]
        check("9. bắt được lệch entry_price vs giá thô ngày entry (FPT 70.200 vs 72.900 ngày 07-01)",
              slip.note is not None and "≠" in slip.note, slip.note)

        same = adjust_entries([("ACB", "2026-07-01", 22650.0)])[("ACB", "2026-07-01")]
        check("10. không báo lệch sai khi entry_price ĐÚNG bằng giá thô", same.note is None)

        # ---- 12-16: quy ước quyền mua (Việc C1) --------------------------------------------
        # MBB 2026-08-11 = quyền mua 10% (giá 10.000đ) + cổ tức CP 15% cùng ngày. Sổ paper không
        # có tài khoản tiền ⇒ không thực hiện được quyền ⇒ tỉ suất phải theo accrue-only.
        check("12. MBB: hai quy ước KHÁC nhau và accrue-only THẬN TRỌNG hơn (entry_adj lớn hơn)",
              m.factor_terp is not None and m.factor < 1.0 and m.factor > m.factor_terp,
              f"accrue_only={m.factor:.6f} > terp={m.factor_terp:.6f}")
        check("13. MBB: phần quyền tách ra khớp công thức TERP nghịch đảo "
              "(24.250+0,1×10.000)/(24.250×1,25) = 0,832990",
              abs(m.factor / m.factor_terp - 1.0 / 0.9579385) < 5e-4,
              f"terp/accrue = {m.factor_terp / m.factor:.6f} vs 0,957939")
        check("14. MBB: ex-date quyền mua được NÊU TÊN trong kết quả, không ẩn",
              m.rights_events == ("2026-08-11",) and m.note and "quyền mua" in m.note,
              f"{m.rights_events}")
        terp = adjust_entries([("MBB", "2026-06-30", 25200.0)], convention="terp")
        mt = terp[("MBB", "2026-06-30")]
        check("15. convention='terp' tái lập ĐÚNG số cũ (20.180) — đổi quy ước, không đổi công thức",
              abs(mt.entry_adj - 20180.0) < 1.0 and mt.rights_events == (),
              f"{mt.entry_adj:,.1f}")
        check("16. mã KHÔNG có quyền mua ⇒ hai quy ước TRÙNG KHÍT tuyệt đối",
              all(adjust_entries([(t, "2026-06-30", p)])[(t, "2026-06-30")].factor
                  == adjust_entries([(t, "2026-06-30", p)], convention="terp")[
                      (t, "2026-06-30")].factor
                  for t, p in (("FPT", 70200.0), ("ACB", 22650.0))))
        # fail-visibly, never fall back to TERP behind the reader's back
        f_, r_, err_ = _rights_free_factor("MBB", "2026-06-30", 0.800794, "2026-08-12",
                                           "/nonexistent-cache-path")
        check("17. không tách được phần quyền ⇒ trả lỗi, KHÔNG âm thầm dùng TERP",
              f_ is None and r_ == ("2026-08-11",) and err_, f"err={err_}")

        # ---- 18-19: cache vintage (Việc C2) -------------------------------------------------
        import tempfile
        import time as _t
        with tempfile.TemporaryDirectory() as td:
            d = Path(td) / "ticker"
            d.mkdir(parents=True)
            (d / "2025.parquet").write_bytes(b"x")
            (d / "2026.parquet").write_bytes(b"x")
            old = _t.time() - 20 * 86400
            os.utime(d / "2025.parquet", (old, old))
            st = stale_years(td)
            check("18. bắt được file NĂM cũ hơn phần còn lại của cache",
                  set(st) == {"2025"} and st["2025"] > 19, f"{ {k: round(v,1) for k,v in st.items()} }")
        real = stale_years()
        check("19. cache THẬT: mọi năm có sổ paper (2026) phải còn tươi, nếu không phải nói ra",
              "2026" not in real,
              f"năm cũ hiện tại: { {k: round(v,1) for k, v in real.items()} } "
              f"(chưa có sổ paper nào ngoài 2026 nên chưa chặn ai)")

        # 11. REGRESSION — the same ticker in two books with different asof/entry must NOT collide.
        # A ticker-keyed result dict silently returned converge's MBB entry for alphasens's MBB;
        # caught by paper_entry_corpaction_crosscheck.py, pinned here so it cannot come back.
        both = adjust_entries([("MBB", "2026-07-01", 25200.0), ("MBB", "2026-06-26", 24750.0)])
        a1, a2 = both[("MBB", "2026-07-01")], both[("MBB", "2026-06-26")]
        check("11. cùng mã, 2 sổ paper khác asof/entry ⇒ KHÔNG đè nhau",
              len(both) == 2 and a1.entry_price == 25200.0 and a2.entry_price == 24750.0
              and a1.entry_adj != a2.entry_adj,
              f"07-01→{a1.entry_adj:,.0f} · 06-26→{a2.entry_adj:,.0f}")

    print()
    if fails:
        print(f"FAILED {len(fails)}/{len(ran)}: {fails}")
        return 1
    print(f"OK — paper_entry_adjust selfcheck PASS {len(ran)}/{len(ran)}"
          f"{f' (skip: {skips})' if skips else ''}")
    return 0


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--selfcheck", action="store_true")
    ap.add_argument("--ticker")
    ap.add_argument("--asof")
    ap.add_argument("--entry", type=float)
    a = ap.parse_args()

    if a.selfcheck:
        raise SystemExit(_selfcheck())
    if a.ticker and a.asof and a.entry:
        r = adjust_entries([(a.ticker, a.asof, a.entry)])[(a.ticker, a.asof)]
        print(r)
    else:
        ap.error("cần --selfcheck hoặc --ticker/--asof/--entry")
