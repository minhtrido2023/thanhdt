#!/usr/bin/env python3
"""
ba_ticker_filters.py
====================
Centralized ticker exclusion lists for BA-system 45-day hold.

Rationale: Some sectors have negative-expected returns at 3M horizon but
positive at long horizon. They belong in long-hold FA portfolio, NOT in
BA-45d.

KCN (Industrial Parks):
  - All-time KCN @ 3M: Mean -3.88%, Median -3.06%, WR 39.2% (negative-expected)
  - All-time KCN @ 1Y: Mean +18.51%, WR 61% (positive at long horizon)
  - Sector takes years for pre-sales → revenue recognition
  - → Excluded from BA-45d; preserved for long-hold portfolio

CG_AUTO (ICB 3353):
  - FA-untradeable: all 5 top indicators have IC -0.22 to -0.26 (anti-signal)
  - 37 observations confirm pattern
  - → Excluded from BA-45d
"""

# KCN tickers — Vietnamese industrial park developers
# Confirmed via manual classification + observed FA exploration
KCN_TICKERS = {
    "SIP", "KBC", "IDC", "NTC", "TIP", "BCM", "SZB", "SZC", "LHG", "SZL",
    "D2D", "IDV", "BAX", "ITA", "SNZ", "VRG", "VGC", "HPI", "MH3", "SZG",
    "TID", "TIX", "LHC", "DXP",
}

# Auto dealers (ICB 3353) — FA-untradeable per v8c findings
AUTO_DEALER_TICKERS = {
    # Populated from ICB 3353 lookup
    "CTF", "GGG", "GMA", "HAX", "HHS", "HTL", "HUT", "PTM",
    # (additional from BQ query: bq query "SELECT DISTINCT ticker FROM tav2_bq.ticker WHERE ICB_Code = 3353")
}

# Combined exclusion set for BA-45d
BA_45D_EXCLUSIONS = KCN_TICKERS | AUTO_DEALER_TICKERS


def filter_signals_for_ba_45d(sig_df, additional_excludes=None):
    """Remove tickers unsuitable for BA-45d short-term hold.

    Args:
        sig_df: pandas DataFrame with 'ticker' column
        additional_excludes: optional set of tickers to also exclude

    Returns:
        Filtered DataFrame
    """
    excludes = BA_45D_EXCLUSIONS.copy()
    if additional_excludes:
        excludes |= set(additional_excludes)
    return sig_df[~sig_df["ticker"].isin(excludes)].copy()


if __name__ == "__main__":
    print(f"KCN_TICKERS: {len(KCN_TICKERS)} tickers")
    print(f"  {sorted(KCN_TICKERS)}")
    print(f"AUTO_DEALER_TICKERS: {len(AUTO_DEALER_TICKERS)} tickers")
    print(f"  {sorted(AUTO_DEALER_TICKERS)}")
    print(f"Total BA_45D_EXCLUSIONS: {len(BA_45D_EXCLUSIONS)} tickers")
