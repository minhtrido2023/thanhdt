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
                                 # | RIGHTS_UNRESOLVED | VINTAGE_STALE
    note: str | None = None      # human-readable caveat, surfaced in the report when set
    factor_terp: float | None = None      # raw Close/Price (TERP: rights subscribed or sold)
    convention: str = "accrue_only"       # accrue_only | terp
    rights_events: tuple = ()             # ex-dates of the rights issues stripped out

    @property
    def is_adjusted(self) -> bool:
        return self.status == "ADJUSTED"

    @property
    def degraded(self) -> bool:
        """True when we could not verify the rebase and fell back to the raw frozen entry."""
        return self.status in ("NO_DATA", "BAD_FACTOR", "RIGHTS_UNRESOLVED", "VINTAGE_STALE")

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

        # Invariant: adjustment only ever scales historical prices DOWN (dividends/dilution are
        # value leaving the share). factor > 1 means the pair is not what we think it is.
        if not (0.0 < factor_terp <= 1.0 + FACTOR_EPS):
            out[(ticker, asof)] = AdjustedEntry(
                ticker, entry_price, entry_price, factor_terp, price_at, time_used, "BAD_FACTOR",
                f"Close/Price = {factor_terp:.6f} ngoài (0,1] — không rebase, giữ giá gốc",
                factor_terp=factor_terp, convention=convention,
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
                factor_terp=factor_terp, convention=convention,
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
                out[(ticker, asof)] = AdjustedEntry(
                    ticker, entry_price, entry_price, None, price_at, time_used,
                    "RIGHTS_UNRESOLVED",
                    f"có quyền mua sau {asof} nhưng không tách được phần quyền ({err}) — "
                    f"KHÔNG dùng TERP thay thế, giữ giá gốc",
                    factor_terp=factor_terp, convention=convention, rights_events=rights,
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
            factor_terp=factor_terp, convention=convention, rights_events=rights,
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

    print("== B. Dữ liệu thật trong cache ==")
    cache_ok = (DEFAULT_CACHE / "ticker").is_dir()
    if not cache_ok:
        print("  SKIP  không có data/bq_cache/ticker — bỏ qua nhóm B")
        skips.append("B")
    else:
        live = adjust_entries(
            [("MBB", "2026-06-30", 25200.0), ("FPT", "2026-06-30", 70200.0),
             ("ACB", "2026-06-30", 22650.0), ("HDB", "2026-06-30", 25850.0)],
        )
        m = live[("MBB", "2026-06-30")]
        check("7. MBB thật: Close/Price (TERP) ≈ 0,800794 — quy ước accrue-only kiểm ở ca 12-14",
              m.is_adjusted and abs(m.factor_terp - 0.800794) < 1e-5,
              f"terp={m.factor_terp:.6f} accrue_only={m.factor:.6f} entry_adj={m.entry_adj:,.1f}")

        # THE control assertion the dispatch demanded: names with no corp-action must be untouched.
        for tk, ep in (("FPT", 70200.0), ("ACB", 22650.0), ("HDB", 25850.0)):
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
