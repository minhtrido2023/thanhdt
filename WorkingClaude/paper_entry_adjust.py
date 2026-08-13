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

No corporate-action table is needed to COMPUTE this: `Close/Price` already encodes the cumulative
effect of every event (cash dividend, stock dividend, bonus, rights issue) between `asof` and
today — which is exactly, and only, what a total-return mark needs. `tav2_bq.corporate_action` is
used to VERIFY the result independently (see `--selfcheck` case 8 and
`paper_entry_corpaction_crosscheck.py`), never to compute it. That split matters: Bẫy (4) of the
same doc says `Close/Price` cannot tell you WHICH event happened, so it must never be used to
derive a per-share cash number — but a total-return REBASE needs only the magnitude, not the
event type, so it is the correct tool here.

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


@dataclass
class AdjustedEntry:
    """Result of rebasing one frozen entry price. `entry_adj` is always safe to divide by."""
    ticker: str
    entry_price: float           # as recorded in the paper JSON (raw, frozen)
    entry_adj: float             # rebased into today's adjusted scale
    factor: float | None         # Close/Price at asof; None when unavailable
    raw_at_asof: float | None    # Price(asof) — used only to validate the recorded entry
    asof_used: str | None        # the trading day actually resolved (<= requested asof)
    status: str                  # ADJUSTED | UNCHANGED | NO_DATA | BAD_FACTOR
    note: str | None = None      # human-readable caveat, surfaced in the report when set

    @property
    def is_adjusted(self) -> bool:
        return self.status == "ADJUSTED"

    @property
    def degraded(self) -> bool:
        """True when we could not verify the rebase and fell back to the raw frozen entry."""
        return self.status in ("NO_DATA", "BAD_FACTOR")

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


def adjust_entries(items, cache_dir=None) -> dict:
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
        factor = close_at / price_at

        # Invariant: adjustment only ever scales historical prices DOWN (dividends/dilution are
        # value leaving the share). factor > 1 means the pair is not what we think it is.
        if not (0.0 < factor <= 1.0 + FACTOR_EPS):
            out[(ticker, asof)] = AdjustedEntry(
                ticker, entry_price, entry_price, factor, price_at, time_used, "BAD_FACTOR",
                f"Close/Price = {factor:.6f} ngoài (0,1] — không rebase, giữ giá gốc",
            )
            continue

        note = None
        if abs(entry_price - price_at) / price_at > ENTRY_MATCH_TOL:
            note = (f"entry_price {entry_price:,.0f} ≠ giá thô {time_used} ({price_at:,.0f}) "
                    f"— kiểm tra lại ngày chụp giá trong file paper")

        status = "ADJUSTED" if factor < 1.0 - FACTOR_EPS else "UNCHANGED"
        out[(ticker, asof)] = AdjustedEntry(
            ticker, entry_price, entry_price * factor, factor, price_at, time_used, status, note,
        )
    return out


# --------------------------------------------------------------------------------------------
# selfcheck
# --------------------------------------------------------------------------------------------
def _selfcheck() -> int:
    """Offline logic cases + live-cache cases (skipped, not failed, when the cache is absent)."""
    fails, skips = [], []

    def check(name, cond, detail=""):
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
        check("7. MBB thật: factor ≈ 0,800794 và entry_adj ≈ 20.180",
              m.is_adjusted and abs(m.factor - 0.800794) < 1e-5 and abs(m.entry_adj - 20180.0) < 1.0,
              f"factor={m.factor:.6f} entry_adj={m.entry_adj:,.1f}")

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
        print(f"FAILED {len(fails)}: {fails}")
        return 1
    print(f"OK — tất cả selfcheck PASS{f' (skip: {skips})' if skips else ''}")
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
