# -*- coding: utf-8 -*-
"""
cpi_vn.py — Vietnam headline CPI year-over-year (%), MONTHLY.

DATA PROVENANCE (tier order, best first: T1 > T1.5 > T3 > T2):
  TIER 1 — REAL, AUTHORITATIVE (2025-06 .. 2026-06, 13 months):
    Source: General Statistics Office of Vietnam (NSO/GSO), Highcharts chart-embed
      https://www.nso.gov.vn/chart/cpi/embed/?show=chart   (chart slug "cpi", post id 24238)
    Method: fetch the embed HTML, parse the raw Highcharts `series ... data` JSON array
      of [ "M/YYYY", yoy_pct ] pairs — no NLP / prose parsing. Fetched 2026-07-06 for
      job Taylor_20260706_105930. The values in NSO_CPI_YOY_REAL below OVERRIDE the
      proxy anchors for the months they cover.
    LIMITATION: the NSO CPI chart is a SINGLE evergreen post with a ROLLING 13-month
      window (it slides forward each month; there are no per-article historical charts —
      article pages are prose-only, and probing older chart slugs/ids all 404). So real
      chart data reaches back only ~13 months. Gold/USD: NSO articles are titled
      "...chỉ số giá vàng và chỉ số giá đô la Mỹ" but publish NO chart for them (prose
      only) — not fetchable by this method; keep vnstock gold / macro USD/VND instead.

  TIER 1.5 — REAL, FiinPro-X (2008-01 .. 2026-08, 224 months) — ADDED 2026-09-27, job
    Taylor_20260927_022319, finding `fiinprox-H2-cpi-swap`:
    Source: mike/data/fiinprox_cpi_monthly_20260914.csv, column `cpi_yoy_pct` (headline CPI YoY).
    Registry: mike/kb/data_registry/macro/fiinprox_cpi_monthly.md (status DERIVED — headline matches
    the real NSO print 13/13 months, diff 0.00). Sits BELOW Tier 1 (the live NSO chart keeps absolute
    priority) and ABOVE Tier 2/Tier 3, which stay in place as fallbacks.
    WHY: Tier 2 declares correct anchors and then LINEARLY INTERPOLATES between them, so the months
    in between are fabricated. Measured against this file: MAE 0.49pp, max 2.51pp, 30 months off by
    >1pp; worst is 2019 (interpolated 4.5-4.7 for Sep/Oct vs the real 2.0-2.2 — the pork-price shock
    only broke out in Nov-Dec 2019, so a whole year of steady climb was an artifact of the two
    anchors). `cpi_yoy_chg3` (the 3-month direction) agreed in sign on only 77.5% of Tier-2 months.
    MEASURED CONSEQUENCE, so nobody oversells this: macro_confidence_regime relabels 27/185 months
    (14.6%) — and ZERO of them in the 2011 or 2022 inflation episodes (both series read CPI far above
    every threshold there). DCF delta is EXACTLY 0.000% on 7/7 valuable names, because the default
    DCF_TERMINAL_MODE=cap_rf clamps g_term at r_f. This is DATA HYGIENE, not alpha: no evidence was
    produced that it improves returns or signal quality.
    ⚠️ FROZEN SNAPSHOT, NOT A FEED (coding_guidelines §14). FiinPro-X trial ended 2026-09-28 — this
    file will never gain a month. Tier 1.5 therefore covers only up to FIINPRO_CPI_LAST_MONTH (read
    from the file, never hardcoded); any later month falls back to Tier 2's forward-fill and
    `cpi_monthly_df()` prints a ONE-TIME coverage warning naming the gap. The continuing live source
    is Tier 1 (GSO/NSO monthly print) — refresh NSO_CPI_YOY_REAL, not this file.

  TIER 2 — PROXY / ANCHOR (2011-01 .. 2025-05, pre-NSO-window): best-estimate MONTHLY
    YoY anchors from well-documented public GSO / IMF / news prints for the pivotal
    turning points, linearly interpolated between anchors (same treatment
    `deposit_rate_vn.py` uses for the Big-4 deposit rate). Directionally reliable
    (2011 spike, 2015 near-zero, 2019 pork spike, 2020 collapse, 2022-H2 uptick);
    individual month levels are +/- a few tenths. Kept as FALLBACK only; superseded by
    Tier-1 wherever the two overlap.

  TIER 3 — BACKFILL, 2007-01 .. 2010-12 (pre-Tier-2-window; covers the 2008 hyperinflation
    peak + 2009 base-effect trough): monthly headline CPI YoY (%) sourced by Winston
    (data-ops) into `mike/agents/Taylor/research/vn_cpi_sbv_2007_2010_winston.csv`
    (fetched 2026-08-25, job Taylor_20260825_052019). Mixed per-month confidence — kept in
    the source CSV, NOT modeled here as a column (see CPI_YOY_BACKFILL_2007_2010 comment):
      HIGH (direct GSO press-release/press-snippet print): 2007-06, 2008-04, 2008-07,
        2008-08, 2008-09, 2008-11, 2009-07 (7 months).
      MEDIUM (CEIC's own estimate/interpolation of the GSO series, not the primary print):
        the other 41 months. Directionally reliable (2008 peak 28.3% Aug, 2009 trough
        -0.02% Oct) but individual levels carry more uncertainty than Tier 1/2.
    Superseded by Tier 2 from 2011-01 onward (no overlap by construction — Tier 2's
    earliest anchor is exactly 2011-01-01). Since Tier 1.5 was added, Tier 3's only EFFECTIVE months
    are 2007-01..2007-12 (FiinPro starts 2008-01); 2008-2010 now come from FiinPro, which is the
    better source there too (2008 agreed with T3 to MAE 0.01pp, but T3 is off 1.3-2.3pp across
    2009-09/10 and 2010-09..11 — the "-0.02% Oct-2009 base-effect trough" in the list below is
    WRONG, the real trough was 1.97% in 2009-08). Tier 3 still covers 2008-2010 whenever the
    FiinPro file is unavailable, which is exactly why it was not deleted.

  NOTE ON WHAT TIER 1 CHANGED: the old proxy badly missed early-2026 — it modeled a
    smooth rise (2026-01 proxy 4.5) whereas the real NSO print DIPPED to 2.53 in Jan
    then spiked (Mar 4.65 → May 5.60 → Jun 4.69). The spike is real but LATER and
    sharper than the proxy assumed; Jan-2026 was actually a low, not a step up.

Documented Tier-2 proxy anchors (YoY %, headline CPI vs same month prior year):
  2011: Jan 12.2, Apr 17.5, Aug 23.0 (peak), Dec 18.1     [inflation crisis]
  2012: Jan 17.3, Jun 6.9, Dec 6.8                         [rapid disinflation]
  2013: Jun 6.7, Dec 6.0
  2014: Jan 5.5, Dec 1.8                                    [falling]
  2015: whole year ~0.6-1.0, Dec 0.6                        [near-zero, oil crash]
  2016: Jan 0.8, Dec 4.7                                    [rebound]
  2017: avg 3.5, Dec 2.6
  2018: Jun 4.7 (peak), Dec 3.0
  2019: Jan 2.6, Dec 5.2                                    [ASF pork spike late]
  2020: Jan 6.4 (peak), Dec 0.2                             [collapse]
  2021: avg 1.8, Dec 1.8
  2022: Jan 1.9, Dec 4.55                                   [rising H2]
  2023: Jan 4.9, Jun 2.0, Dec 3.6
  2024: Jan 3.4, mid ~4.4, Dec 2.9
  2025: ~3.3 flat, Dec 3.4  [→ superseded from 2025-06 by real NSO]
"""
import os

import pandas as pd

# TIER 1 — REAL headline CPI YoY (%) from NSO chart-embed (slug "cpi"), fetched 2026-07-06.
# Rolling 13-month window; these OVERRIDE the interpolated proxy for the months present.
NSO_CPI_YOY_REAL = {
    "2025-06-01": 3.57, "2025-07-01": 3.19, "2025-08-01": 3.24, "2025-09-01": 3.38,
    "2025-10-01": 3.25, "2025-11-01": 3.58, "2025-12-01": 3.48, "2026-01-01": 2.53,
    "2026-02-01": 3.35, "2026-03-01": 4.65, "2026-04-01": 5.46, "2026-05-01": 5.60,
    "2026-06-01": 4.69,
}

# TIER 1 (bonus) — REAL **CORE** inflation YoY (%) from NSO chart "inflation" (slug "inflation",
# post id 24239), same fetch/window. Not read by anything; kept for reference only.
# RENAMED 2026-09-27 (was NSO_CPI_YOY_AVG_REAL, job Taylor_20260927_022319): the old name and comment
# claimed this was the year-to-date AVERAGE ("bình quân") print. It is not — all 13 values match
# fiinprox_cpi_monthly_20260914.csv's `core_yoy_pct` (lạm phát cơ bản) exactly, and NONE of them
# matches the headline series. See trap #1 in mike/kb/data_registry/macro/fiinprox_cpi_monthly.md.
# Safe rename: grep 2026-09-27 found the old name DEFINED here and read nowhere in any .py.
NSO_CPI_CORE_YOY_REAL = {
    "2025-06-01": 3.46, "2025-07-01": 3.30, "2025-08-01": 3.25, "2025-09-01": 3.18,
    "2025-10-01": 3.30, "2025-11-01": 3.28, "2025-12-01": 3.27, "2026-01-01": 3.19,
    "2026-02-01": 3.74, "2026-03-01": 3.96, "2026-04-01": 4.66, "2026-05-01": 4.67,
    "2026-06-01": 4.50,
}

# (year-month-01, headline_cpi_yoy_pct)  — monthly anchors, linearly interpolated between
CPI_ANCHORS = [
    ("2011-01-01", 12.2), ("2011-04-01", 17.5), ("2011-08-01", 23.0), ("2011-12-01", 18.1),
    ("2012-06-01",  6.9), ("2012-12-01",  6.8),
    ("2013-06-01",  6.7), ("2013-12-01",  6.0),
    ("2014-01-01",  5.5), ("2014-12-01",  1.8),
    ("2015-06-01",  1.0), ("2015-12-01",  0.6),
    ("2016-01-01",  0.8), ("2016-12-01",  4.7),
    ("2017-06-01",  2.5), ("2017-12-01",  2.6),
    ("2018-06-01",  4.7), ("2018-12-01",  3.0),
    ("2019-01-01",  2.6), ("2019-12-01",  5.2),
    ("2020-01-01",  6.4), ("2020-06-01",  3.2), ("2020-12-01",  0.2),
    ("2021-06-01",  2.4), ("2021-12-01",  1.8),
    ("2022-01-01",  1.9), ("2022-06-01",  3.4), ("2022-12-01",  4.55),
    ("2023-01-01",  4.9), ("2023-06-01",  2.0), ("2023-12-01",  3.6),
    ("2024-01-01",  3.4), ("2024-06-01",  4.4), ("2024-12-01",  2.9),
    ("2025-01-01",  3.6), ("2025-05-01",  3.4),  # last proxy month before real NSO takes over
]


# TIER 3 — BACKFILL headline CPI YoY (%), 2007-01..2010-12. Source: Winston (data-ops),
# mike/agents/Taylor/research/vn_cpi_sbv_2007_2010_winston.csv (fetched 2026-08-25). Mixed
# confidence per month (see module docstring); HIGH-confidence (direct GSO print) months are
# 2007-06, 2008-04, 2008-07, 2008-08, 2008-09, 2008-11, 2009-07 — all other months MEDIUM
# (CEIC estimate). Covers the 2008 hyperinflation peak (28.32% Aug-2008) and the 2009
# base-effect trough (-0.02% Oct-2009).
CPI_YOY_BACKFILL_2007_2010 = {
    "2007-01-01": 6.74, "2007-02-01": 7.03, "2007-03-01": 6.73, "2007-04-01": 7.13,
    "2007-05-01": 7.14, "2007-06-01": 7.82, "2007-07-01": 8.27, "2007-08-01": 8.27,
    "2007-09-01": 8.73, "2007-10-01": 8.84, "2007-11-01": 9.37, "2007-12-01": 12.63,
    "2008-01-01": 14.11, "2008-02-01": 15.74, "2008-03-01": 19.39, "2008-04-01": 21.42,
    "2008-05-01": 25.20, "2008-06-01": 26.84, "2008-07-01": 27.04, "2008-08-01": 28.32,
    "2008-09-01": 27.90, "2008-10-01": 26.74, "2008-11-01": 24.22, "2008-12-01": 19.89,
    "2009-01-01": 17.49, "2009-02-01": 14.81, "2009-03-01": 11.19, "2009-04-01": 9.23,
    "2009-05-01": 5.65, "2009-06-01": 3.67, "2009-07-01": 3.31, "2009-08-01": 2.27,
    "2009-09-01": 0.68, "2009-10-01": -0.02, "2009-11-01": 4.35, "2009-12-01": 6.52,
    "2010-01-01": 7.62, "2010-02-01": 8.46, "2010-03-01": 9.46, "2010-04-01": 9.23,
    "2010-05-01": 9.09, "2010-06-01": 8.69, "2010-07-01": 8.19, "2010-08-01": 8.23,
    "2010-09-01": 7.57, "2010-10-01": 7.89, "2010-11-01": 8.84, "2010-12-01": 11.75,
}


# ---------------- TIER 1.5 — FiinPro-X monthly headline CPI (frozen snapshot) ----------------
# Path is module-relative so a git worktree (where mike/ is absent — .gitignore:107 hides the nested
# repo) degrades LOUDLY to Tier 2 instead of silently reading a stale copy. Env override is for
# selfchecks only.
FIINPRO_CPI_CSV = os.environ.get(
    "FIINPRO_CPI_CSV",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mike", "data",
                 "fiinprox_cpi_monthly_20260914.csv"))
FIINPRO_CPI_VINTAGE = "2026-09-14"      # the day the snapshot was harvested; it never advances
_FIINPRO_CPI = None                     # cached pd.Series (Timestamp -> headline YoY %)
_WARNED = set()                         # one-time warnings, keyed by message


def _warn_once(msg):
    if msg not in _WARNED:
        _WARNED.add(msg)
        print(f"[cpi_vn] {msg}")


def fiinpro_cpi_series():
    """Tier-1.5 headline CPI YoY (%) keyed by month-start Timestamp. Empty Series when the snapshot
    is unavailable -> every caller falls back to Tier 2/Tier 3 (the pre-2026-09-27 behaviour)."""
    global _FIINPRO_CPI
    if _FIINPRO_CPI is not None:
        return _FIINPRO_CPI
    try:
        f = pd.read_csv(FIINPRO_CPI_CSV)
        idx = pd.to_datetime(f["month"].astype(str) + "-01")
        ser = pd.Series(pd.to_numeric(f["cpi_yoy_pct"], errors="coerce").values, index=idx)
        _FIINPRO_CPI = ser.dropna().sort_index()
    except Exception as e:
        _warn_once(f"Tier 1.5 UNAVAILABLE ({FIINPRO_CPI_CSV}: {e}) -> Tier 2 interpolation is in "
                   f"force for 2011-01..2025-05 and Tier 3 for 2007-2010. Values there are PROXY "
                   f"(MAE 0.49pp, max 2.51pp) -- do not quote them as real prints.")
        _FIINPRO_CPI = pd.Series(dtype=float)
    return _FIINPRO_CPI


def cpi_coverage(end):
    """FRESHNESS CHECK (coding_guidelines §14) for the producer->consumer pair
    `fiinprox_cpi_monthly_20260914.csv` (frozen) -> this module (read live).

    Returns (real_last, fp_last, gap_months) where gap_months lists the requested months no REAL
    source covers, i.e. the months served by the Tier-2 forward-fill. Never raises: this module
    feeds golive_recommend_v23, so it must degrade, not abort — but it must degrade OUT LOUD."""
    end_ts = pd.to_datetime(end).normalize().replace(day=1)
    real_last = max(pd.to_datetime(list(NSO_CPI_YOY_REAL))) if NSO_CPI_YOY_REAL else pd.NaT
    fp = fiinpro_cpi_series()
    fp_last = fp.index.max() if len(fp) else pd.NaT
    covered = max([d for d in (real_last, fp_last) if pd.notna(d)], default=pd.NaT)
    if pd.isna(covered) or end_ts <= covered:
        return real_last, fp_last, []
    gap = list(pd.date_range(covered + pd.offsets.MonthBegin(1), end_ts, freq="MS"))
    _m = lambda d: "(none)" if pd.isna(d) else f"{d:%Y-%m}"     # NaT = that tier has no month at all
    _warn_once(
        f"CPI COVERAGE GAP: {len(gap)} month(s) {gap[0]:%Y-%m}..{gap[-1]:%Y-%m} have NO real source. "
        f"Tier 1 (live NSO) ends {_m(real_last)}; Tier 1.5 (FiinPro snapshot {FIINPRO_CPI_VINTAGE}, "
        f"trial ended 2026-09-28 -> FROZEN) ends {_m(fp_last)}. Those months are Tier 2's "
        f"forward-fill of its last anchor, NOT a print. FIX = refresh NSO_CPI_YOY_REAL from the GSO "
        f"monthly release; refreshing the FiinPro file is impossible.")
    return real_last, fp_last, gap


def cpi_monthly_df(end="2026-06-01"):
    """Monthly YoY CPI (%): real NSO chart-embed where available (2025-06..2026-06),
    linear-interpolated proxy anchors 2011-01..2025-05 (fallback), Tier-3 backfill
    2007-01..2010-12 (fallback, pre-Tier-2 window)."""
    a = pd.DataFrame(CPI_ANCHORS, columns=["time", "cpi_yoy"])
    a["time"] = pd.to_datetime(a["time"])
    a = a.set_index("time").sort_index()
    backfill = pd.Series({pd.to_datetime(k): v for k, v in CPI_YOY_BACKFILL_2007_2010.items()})
    start = min(a.index.min(), backfill.index.min())
    idx = pd.date_range(start, pd.to_datetime(end), freq="MS")
    s = a["cpi_yoy"].reindex(a.index.union(idx)).interpolate(method="index").reindex(idx)
    out = s.reset_index()
    out.columns = ["time", "cpi_yoy"]
    # Overlay Tier-3 backfill first (lowest priority; NaN below 2011-01 since Tier-2's
    # anchors start there and interpolate() never extrapolates before its first anchor).
    out["cpi_yoy"] = out["time"].map(backfill).fillna(out["cpi_yoy"])
    # Overlay Tier 1.5 (FiinPro-X real prints, 2008-01..2026-08) above Tier 2/Tier 3. With the file
    # present this leaves Tier 3 serving 2007 only; with the file absent Tier 3 still covers
    # 2007-2010 and Tier 2 still covers 2011+ -- i.e. exactly the pre-wire behaviour.
    fp = fiinpro_cpi_series()
    out["cpi_yoy"] = out["time"].map(fp).fillna(out["cpi_yoy"]) if len(fp) else out["cpi_yoy"]
    out["is_fiinpro"] = out["time"].isin(fp.index)
    # Overlay REAL NSO values wherever present (Tier 1 overrides everything).
    real = pd.Series({pd.to_datetime(k): v for k, v in NSO_CPI_YOY_REAL.items()})
    out["cpi_yoy"] = out["time"].map(real).fillna(out["cpi_yoy"])
    out["is_real_nso"] = out["time"].isin(real.index)
    out["is_fiinpro"] = out["is_fiinpro"] & ~out["is_real_nso"]
    # `is_backfill_2007_2010` must mean "Tier 3 is what you are actually reading", so it is computed
    # AFTER the higher tiers have overridden -- otherwise 2008-2010 would keep claiming Tier 3.
    out["is_backfill_2007_2010"] = (out["time"].isin(backfill.index)
                                    & ~out["is_fiinpro"] & ~out["is_real_nso"])
    cpi_coverage(end)          # §14 freshness gate: warns once if `end` reaches past every real tier
    # 3-month change of YoY = "inflation accelerating?" (direction signal)
    out["cpi_yoy_chg3"] = out["cpi_yoy"].diff(3)
    return out


def merge_cpi(df, time_col="time", end="2026-06-01"):
    """as-of (backward) merge monthly cpi_yoy / cpi_yoy_chg3 onto a daily frame."""
    cpi = cpi_monthly_df(end=end)
    d = df.sort_values(time_col).copy()
    d[time_col] = pd.to_datetime(d[time_col])
    return pd.merge_asof(d, cpi, left_on=time_col, right_on="time",
                         direction="backward", suffixes=("", "_cpi"))


if __name__ == "__main__":
    c = cpi_monthly_df(end="2026-08-01")
    ann = c.groupby(c.time.dt.year).cpi_yoy.mean().round(2)
    src = c.assign(tier=lambda d: pd.Series(
        ["T1 NSO" if a else "T1.5 FiinPro" if b else "T3 backfill" if cc else "T2 proxy"
         for a, b, cc in zip(d.is_real_nso, d.is_fiinpro, d.is_backfill_2007_2010)], index=d.index))
    print("VN CPI YoY (annual mean of monthly, %) and the tier each year is served from:")
    for y, v in ann.items():
        tiers = "+".join(sorted(src[src.time.dt.year == y].tier.unique()))
        print(f"  {y}: {v:5.2f}   [{tiers}]")
    print("\nmonths per tier: " + ", ".join(f"{k}={v}" for k, v in src.tier.value_counts().items()))
