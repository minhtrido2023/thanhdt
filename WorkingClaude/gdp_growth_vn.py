# -*- coding: utf-8 -*-
"""
gdp_growth_vn.py — Vietnam REAL GDP growth (annual %), yearly series.

Used as the REAL-growth component of the DCF terminal growth rate (dcf terminal g =
long-run inflation + long-run real GDP, faded — see dcf_earning_power.py / the framework).
The current production DCF uses terminal g = 5y-avg CPI only, which implicitly assumes
real growth = 0 forever (very conservative). This module supplies the real-growth term.

DATA PROVENANCE — REAL, AUTHORITATIVE (single tier, unlike cpi_vn.py):
  Source: World Bank Open Data API, indicator NY.GDP.MKTP.KD.ZG
    ("GDP growth (annual %)", growth of constant-LCU real GDP → a REAL growth rate).
    https://api.worldbank.org/v2/country/VNM/indicator/NY.GDP.MKTP.KD.ZG?format=json
  Fetched 2026-07-17 (job Taylor_20260717_063638); World Bank `lastupdated` = 2026-07-13.
  Full annual series 2000-2025 (26 obs, no gaps) pasted below verbatim from the API. Same
  provider family as the WB CMO commodity feed already in the repo (auto_update_commodity_wb.*).

  REFRESH: annual, low-urgency. WB revises prior years and appends the newest ~Q1-Q2.
  refresh_gdp_growth_vn.py re-fetches and rewrites GDP_ANNUAL below (idempotent). The 15y
  long-run average this feeds is insensitive to any single-year revision, so a stale copy for
  a few months is harmless (documented in mike/kb/data_registry.md).

POINT-IN-TIME: annual GDP for year Y is published by GSO in late Dec of year Y (preliminary)
  and revised later. longrun_real_gdp(asof) uses only years with year <= asof.year - 1 (fully
  published prior years) — conservative, and immaterial to a 15y average anyway.

WHY A LONG-RUN AVERAGE, NOT THE CURRENT YEAR (convergence caveat, Damodaran):
  Using the CURRENT real growth (VN 2022-2025 ran 5-8.5%) as the PERPETUAL terminal rate
  over-values grossly — convergence theory says an emerging economy fades toward a mature
  sustainable rate as it develops; it does not compound at today's pace forever. Damodaran's
  rule: terminal nominal g must not exceed the economy's growth AND should not exceed the
  risk-free rate. So (a) we average 15-20 years (already smooths in the slower years, incl. the
  2020-21 COVID trough), and (b) the DCF caller fades/caps this term (see dcf_earning_power.py
  term_mode). This module only supplies the raw long-run real-growth number; the fade/cap is
  the DCF's decision, kept there so it is visible and testable.
"""
import numpy as np, pandas as pd

# (year, real_gdp_growth_pct) — World Bank NY.GDP.MKTP.KD.ZG, VNM, fetched 2026-07-17.
GDP_ANNUAL = [
    (2000, 6.79), (2001, 6.19), (2002, 6.32), (2003, 6.90), (2004, 7.54),
    (2005, 7.55), (2006, 6.98), (2007, 7.13), (2008, 5.66), (2009, 5.40),
    (2010, 6.42), (2011, 6.41), (2012, 5.50), (2013, 5.55), (2014, 6.42),
    (2015, 6.99), (2016, 6.69), (2017, 6.94), (2018, 7.47), (2019, 7.36),
    (2020, 2.87), (2021, 2.55), (2022, 8.54), (2023, 4.98), (2024, 7.04),
    (2025, 8.02),
]

LONGRUN_YEARS = 15          # default long-run averaging window (15y smooths cycle + COVID)


def gdp_annual_df():
    df = pd.DataFrame(GDP_ANNUAL, columns=["year", "gdp_growth"])
    return df.sort_values("year").reset_index(drop=True)


def longrun_real_gdp(asof=None, years=LONGRUN_YEARS):
    """Long-run average REAL GDP growth (decimal), point-in-time as-of `asof`.

    Uses the `years` most recent fully-published annual observations available at `asof`
    (year <= asof.year - 1). Returns a plain float (decimal, e.g. 0.062). If `asof` is None,
    uses the whole latest window."""
    df = gdp_annual_df()
    if asof is not None:
        cutoff = pd.to_datetime(asof).year - 1
        df = df[df.year <= cutoff]
    if len(df) == 0:
        return 0.06                          # fail-safe default (~VN mature real growth)
    w = df.tail(years)
    return float(w.gdp_growth.mean()) / 100.0


if __name__ == "__main__":
    df = gdp_annual_df()
    v = df.gdp_growth.values
    print("VN real GDP growth (annual %), World Bank NY.GDP.MKTP.KD.ZG:")
    for _, r in df.iterrows():
        print(f"  {int(r.year)}: {r.gdp_growth:5.2f}")
    print(f"\nn={len(df)}  {int(df.year.min())}-{int(df.year.max())}")
    print(f"mean ALL={v.mean():.2f}%  median={np.median(v):.2f}%  "
          f"last15y={v[-15:].mean():.2f}%  last20y={v[-20:].mean():.2f}%")
    print(f"longrun_real_gdp(2026-06, 15y) = {longrun_real_gdp('2026-06-01'):.4f}")
