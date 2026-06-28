"""
DQ-2 PATCH — Block profit_* from forward-fill in process_stock_indicator
Status: STAGED (prepared 2026-06-28, NOT yet applied to kaffa)
Target: /workspace/kaffa_v2/worker/data_tasks.py (or equivalent)
Author: Winston (dispatched by Mike, spec from Taylor)

APPLY WITH:
  python ssh_kaffa.py "patch -p1 -d /workspace/kaffa_v2 < /tmp/dq2_patch.patch"
  OR apply the code changes described below manually.

PRE-REQUISITE: read the actual data_tasks.py on kaffa first:
  python ssh_kaffa.py "grep -n 'ffill\\|fillna\\|fill.*NaN\\|last.*row\\|profit_' /workspace/kaffa_v2/worker/data_tasks.py | head -60"
"""

# ─── CONSTANTS — to add near the top of data_tasks.py ───────────────────────

# Columns that carry forward-looking information and must NEVER be ffilled.
# Source: DQ-2 spec from Taylor 2026-06-28.
PROFIT_COLS_NO_FILL = [
    "profit_2W", "profit_1M", "profit_2M", "profit_3M",
    "profit_2W_center_3", "profit_2W_center_5", "profit_2W_center_7",
    "profit_2W_center_10", "profit_2W_center_11", "profit_2W_center_15",
    "profit_2W_center_20",
]

# Safe columns for forward-fill (sticky fundamentals, regime, etc.)
# Only columns explicitly listed here will be ffilled on the live row.
# Extend this list when a new sticky column is added — do NOT relax to "all except profit_*".
FFILL_WHITELIST = [
    # Fundamental / valuation (sticky — released quarterly, valid until next release)
    "PE", "PB", "PS", "PCF", "EVEB", "EPS", "DY", "PEG", "BVPS",
    "ROE5Y", "ROIC5Y", "ROIC3Y", "ROIC_Min3Y", "ROIC_Min5Y",
    "ROE_Min3Y", "ROE_Min5Y", "FSCORE",
    "Debt_Eq_P0", "NP_P0", "NP_P1", "NP_P2", "NP_P3", "NP_P4",
    "CF_OA_P0", "CF_OA_P1", "CF_OA_P2", "CF_OA_P3",
    "CF_Invest_P0", "CF_Invest_P1", "CF_Invest_P2", "CF_Invest_P3",
    "NPM_P0", "IntCov_P0",
    "PE_MA5Y", "PE_MA1Y", "PE_MA3M", "PE_SD5Y", "PE_SD1Y", "PE_SD3M",
    "PB_MA5Y", "PB_MA1Y", "PB_MA3M", "PB_SD5Y", "PB_SD1Y", "PB_SD3M",
    "EVEB_MA5Y", "EVEB_MA1Y", "EVEB_MA3M", "EVEB_SD5Y", "EVEB_SD1Y", "EVEB_SD3M",
    "ROIC_Trailing", "CF_OA_5Y", "CF_Invest_5Y",
    # Risk / meta (updated quarterly / infrequently)
    "Risk_Rating", "ICB_Code",
    # Volume analytics — computed from rolling windows, sticky for 1M windows
    "Volume_1M", "Volume_3M_P50", "Volume_3M_P90",
    "Volume_Max1Y_High", "Volume_Max5Y_High",
    "Trading_Value_1M_P50",
    # VAP (volume-at-price) — computed over lookback windows
    "VAP1W", "VAP1M", "VAP3M",
    # Support/resistance — computed over 1Y lookback
    "Res_1Y", "Sup_1Y",
    # VNINDEX mirrors — these come from market-wide data, valid for the session
    "VNINDEX", "VNINDEX_RSI", "VNINDEX_CMF", "VNINDEX_MACDdiff",
    "VNINDEX_RSI_MinT3", "VNINDEX_RSI_Max1W", "VNINDEX_RSI_Max3M",
    # Pattern stats — 3Y lookback, updated daily but may be NaN for new tickers
    "Pattern_Median_Profit_3Y", "Pattern_Deal_Count_3Y", "Pattern_Winrate_3Y",
]


# ─── REPLACEMENT CODE for the ffill block in process_stock_indicator ─────────
#
# FIND this block in data_tasks.py (approximate, grep for it):
#   # fill last row NaN from previous row
#   df.iloc[-1] = df.iloc[-1].fillna(df.iloc[-2])
#
# OR: df = df.ffill()   (if applied to the whole frame)
# OR: df.iloc[-1] = df.iloc[-1].combine_first(df.iloc[-2])
#
# REPLACE WITH the function below:

def fill_last_row_whitelist(df, whitelist=None, no_fill=None):
    """
    Forward-fill NaN values in the last row of df, but ONLY for whitelisted columns.
    Forward-looking columns (profit_*) must remain NaN.

    Args:
        df: pandas DataFrame — the app dataset; last row is the live T row.
        whitelist: list of column names allowed to be filled. If None, uses FFILL_WHITELIST.
        no_fill: list of column names that must NEVER be filled. If None, uses PROFIT_COLS_NO_FILL.

    Returns:
        df with last row filled selectively (in-place-safe — returns modified copy).
    """
    import pandas as pd

    if whitelist is None:
        whitelist = FFILL_WHITELIST
    if no_fill is None:
        no_fill = PROFIT_COLS_NO_FILL

    if len(df) < 2:
        return df

    df = df.copy()
    last_idx = df.index[-1]
    prev_idx = df.index[-2]

    # Only operate on columns that exist in both the whitelist and the DataFrame.
    cols_to_fill = [c for c in whitelist if c in df.columns]

    # Safety: never fill no_fill columns, even if they somehow appear in whitelist.
    cols_to_fill = [c for c in cols_to_fill if c not in no_fill]

    for col in cols_to_fill:
        if pd.isna(df.at[last_idx, col]):
            df.at[last_idx, col] = df.at[prev_idx, col]

    # Sanity: verify no_fill columns remain NaN in the last row.
    for col in no_fill:
        if col in df.columns and not pd.isna(df.at[last_idx, col]):
            import logging
            logging.warning(
                f"DQ-2 guard: {col} is NOT NaN in last row (value={df.at[last_idx, col]!r}). "
                "This column must be left as NaN. Clearing."
            )
            df.at[last_idx, col] = float("nan")

    return df


# ─── ASSERTION to add before BQ append step [H] ──────────────────────────────
#
# Add this function and call it before the BQ upload in pipeline step [H].
# Call: assert_profit_cols_null(df)
#
# If this raises, DO NOT proceed with BQ append — log the error, alert Telegram,
# and skip the upload for this run to avoid poisoning BQ with look-ahead data.

def assert_profit_cols_null(df, n_recent=60):
    """
    Assert that all profit_* columns are NaN for the most recent n_recent rows.

    In production, the last ~10-60 rows will have NaN profit_* because the
    forward-looking window has not yet elapsed (e.g., profit_2W requires T+10 to close).
    If any profit_* value is non-NaN in this window, it means look-ahead leaked in
    (likely via forward-fill or incorrect data join).

    Args:
        df: pandas DataFrame — the app dataset about to be uploaded to BQ.
        n_recent: int — how many recent rows to check (default 60 = ~3 months of trading).

    Raises:
        AssertionError with details if any profit_* column has non-NaN in recent rows.
    """
    import pandas as pd

    # Derive all profit columns dynamically from column names.
    profit_cols = [c for c in df.columns
                   if c.startswith("profit_") or "_center_" in c]

    if not profit_cols:
        # No profit columns in this dataset — nothing to assert.
        return

    tail = df.tail(n_recent)

    violations = {}
    for col in profit_cols:
        non_null = tail[col].dropna()
        if len(non_null) > 0:
            violations[col] = {
                "count": len(non_null),
                "last_date": str(tail.index[tail[col].notna()][-1]) if hasattr(tail.index, '__iter__') else "unknown",
                "sample_value": float(non_null.iloc[-1]),
            }

    if violations:
        msg = (
            f"DQ-2 ASSERTION FAILED: profit_* columns have non-NaN values in last {n_recent} rows. "
            f"This indicates look-ahead leak. DO NOT upload to BQ.\n"
            f"Violations: {violations}"
        )
        raise AssertionError(msg)


# ─── USAGE EXAMPLE (replace the ffill block in process_stock_indicator) ──────
#
# Before (WRONG):
#   df.iloc[-1] = df.iloc[-1].fillna(df.iloc[-2])
#
# After (CORRECT):
#   df = fill_last_row_whitelist(df)
#
# Before BQ append in step [H]:
#   assert_profit_cols_null(df, n_recent=60)  # raises AssertionError if leak detected
#   upload_to_bq(df)  # only reached if assertion passes


# ─── HOW TO APPLY ─────────────────────────────────────────────────────────────
#
# 1. SSH to kaffa: python ssh_kaffa.py "grep -n 'ffill\|fillna.*NaN\|last.*row' /workspace/kaffa_v2/worker/data_tasks.py"
# 2. Identify the exact lines of the ffill block.
# 3. Add PROFIT_COLS_NO_FILL and FFILL_WHITELIST constants near the top of data_tasks.py.
# 4. Replace the ffill block with: df = fill_last_row_whitelist(df)
# 5. Add assert_profit_cols_null(df) call immediately before the BQ upload in step [H].
# 6. Test: python ssh_kaffa.py "cd /workspace/kaffa_v2 && python -c 'from worker.data_tasks import fill_last_row_whitelist, assert_profit_cols_null; print(\"OK\")'"
# 7. Report result to bus with append_event.sh
