"""BA-system Live Engine — daily recommendation script.

Combines:
  - Layer 1 (FA-system): 7-axis fundamental quality → tier A/B/C/D/E
  - Layer 2 (TA-system v10): momentum + value + FA tier + sector + 5-state regime
                             + Fin/RE × FA-D bonus +10 / Fin/RE × FA-A penalty -10
  - Layer 3 (this engine): cross-reference, classify into BA-system play types
                           + suggest position sizing for the 50/50 BAL+VN30 strategy

PRODUCTION CONFIG (BA-system, validated 2014-2026, 15 backtest rounds):
  Strategy: 50% BAL+Fin/RE-max-4 + 50% VN30_BAL
    - BAL: ticker_prune universe, sector 8 (Fin/RE) max 4 positions
    - VN30: top 30 tickers by avg liquidity, no sector cap
    - max_positions=10 each, hold_days=45, stop_loss=-20% (conservative)
    - T+1 entry, T+3 min hold, BL20 (re-entry blacklist 20 sessions)
    - liquidity 20% ADV cap, 5-day fill, slippage 0.1% + tiered exit slip

Expected at 50B NAV: CAGR 17.15%, Sharpe 1.21, MaxDD -14.5%, Calmar 1.18
                     85.4% Q win rate; 2022 crash: +2.6% (vs VNI -33%)

Run: python recommend_holistic.py [YYYY-MM-DD]
"""
import os
import subprocess
import sys
import io
from datetime import date
from io import StringIO

import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
PROJECT = "lithe-record-440915-m9"
BQ_BIN = r"bq"

# ─── BA-system v10 scoring SQL — Fin/RE × FA-D/A baked into TA score ─────
# UNIFIED: auto-fallback ticker (canonical) → ticker_1m (rolling, more recent).
# For dates > MAX(ticker.time): use ticker_1m + carry forward last known VNINDEX_RSI_Max3M
# (frozen approximation; the value only changes when VNI makes new 3M RSI highs).
# Tier thresholds: MEGA ≥170, MOMENTUM ≥155, MOMENTUM_S ≥140, MOMENTUM_A ≥125.
SCORE_SQL = """
WITH fa_dated AS (
  SELECT f.ticker, f.time AS f_time, f.tier AS fa_tier_hist,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.fa_ratings AS f
),
-- D1+slot12 (deployed 2026-05-16): AdvCust YoY for RE_BACKLOG_BUY tier (ICB 8633)
adv_dated AS (
  SELECT f.ticker, f.time AS f_time,
    SAFE_DIVIDE(f.AdvCust_P0, NULLIF(f.AdvCust_P4, 0)) - 1 AS adv_yoy,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.ticker_financial AS f
),
-- Compute VNINDEX_RSI_Max3M from VNINDEX D_RSI (UNION ticker VNINDEX + ticker_1m VNINDEX),
-- rolling MAX over last 60 sessions.
-- BUG FIX 2026-05-19: ticker_1m chứa cả 'VNI' (junk: Close ~6300, D_RSI sai)
-- và 'VNINDEX' (đúng). Trước đây dùng 'VNI' → VNINDEX_RSI_Max3M bị ô nhiễm cho
-- các ngày fallback từ ticker_1m. Đổi sang 'VNINDEX'.
vni_history AS (
  SELECT t.time, t.D_RSI
  FROM tav2_bq.ticker AS t
  WHERE t.ticker = 'VNINDEX' AND t.D_RSI IS NOT NULL
  UNION ALL
  SELECT t.time, t.D_RSI
  FROM tav2_bq.ticker_1m AS t
  WHERE t.ticker = 'VNINDEX' AND t.D_RSI IS NOT NULL
    AND NOT EXISTS (
      SELECT 1 FROM tav2_bq.ticker AS t2
      WHERE t2.time = t.time AND t2.ticker = 'VNINDEX' AND t2.D_RSI IS NOT NULL
    )
),
vni_max3m AS (
  SELECT time,
    MAX(D_RSI) OVER (ORDER BY time ROWS BETWEEN 59 PRECEDING AND CURRENT ROW) AS rsi_max3m
  FROM vni_history
),
-- Unified daily snapshot: prefer ticker (canonical), fallback to ticker_1m
ticker_data AS (
  SELECT t.ticker, t.time, t.Close, t.Volume, t.D_RSI, t.D_MACDdiff,
         t.MA20, t.MA50, t.MA200, t.MA50_T1, t.Close_T1,
         t.HI_3M_T1, t.ID_HI_3Y, t.D_RSI_Max1W,
         t.PE, t.PE_MA5Y, t.PE_SD5Y, t.FSCORE,
         t.NP_P0, t.NP_P1, t.NP_P4, t.ICB_Code, t.Volume_3M_P50,
         'ticker' AS src
  FROM tav2_bq.ticker AS t
  WHERE t.time = DATE '{day}'
    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
    AND t.D_RSI IS NOT NULL

  UNION ALL

  SELECT t.ticker, t.time, t.Close, t.Volume, t.D_RSI, t.D_MACDdiff,
         t.MA20, t.MA50, t.MA200, t.MA50_T1, t.Close_T1,
         t.HI_3M_T1, t.ID_HI_3Y, t.D_RSI_Max1W,
         t.PE, t.PE_MA5Y, t.PE_SD5Y, t.FSCORE,
         t.NP_P0, t.NP_P1, t.NP_P4, t.ICB_Code, t.Volume_3M_P50,
         'ticker_1m' AS src
  FROM tav2_bq.ticker_1m AS t
  WHERE t.time = DATE '{day}'
    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
    AND t.D_RSI IS NOT NULL
    AND NOT EXISTS (
      SELECT 1 FROM tav2_bq.ticker AS t2
      WHERE t2.time = DATE '{day}' AND t2.ticker = t.ticker AND t2.D_RSI IS NOT NULL
    )
)
SELECT
  t.ticker, t.time, t.Close, t.Volume,
  ROUND(t.D_RSI, 2) AS rsi,
  ROUND(t.D_MACDdiff, 1) AS macd_diff,
  ROUND(t.Close / NULLIF(t.MA50,0) - 1, 3) AS vs_ma50,
  ROUND(t.MA50 / NULLIF(t.MA50_T1,0) - 1, 4) AS ma50_slope,
  ROUND(t.Close / NULLIF(t.HI_3M_T1,0) - 1, 3) AS vs_3m_high,
  ROUND(t.PE, 1) AS pe,
  ROUND((t.PE - t.PE_MA5Y) / NULLIF(t.PE_SD5Y, 0), 2) AS pe_zscore,
  CAST(t.FSCORE AS INT64) AS fscore,
  ROUND(SAFE_DIVIDE(t.NP_P0, t.NP_P4) - 1, 2) AS np_yoy,
  ROUND(SAFE_DIVIDE(t.NP_P0, t.NP_P1) - 1, 2) AS np_qoq,
  CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS sector_top,
  t.ICB_Code AS icb_code,
  ROUND(adv.adv_yoy, 2) AS adv_yoy,
  fa.fa_tier_hist,
  s5.state AS state5,
  ROUND(t.Volume_3M_P50 * t.Close / 1e9, 2) AS liq_b_vnd,
  t.src AS data_source,
  rel.days_since_release,
  -- v10 TA score (max ~194)
  CASE WHEN t.D_RSI > 0.50 THEN 25 ELSE 0 END
  + CASE WHEN t.Close > t.MA50 AND t.MA50 > t.MA200 THEN 25 ELSE 0 END
  + CASE WHEN t.Volume >= t.Volume_3M_P50 * 1.3 AND t.Close > t.Close_T1 THEN 20 ELSE 0 END
  + CASE WHEN t.D_MACDdiff > 0 THEN 15 ELSE 0 END
  + CASE WHEN t.Close > t.MA20 THEN 15 ELSE 0 END
  + CASE WHEN t.D_RSI > 0.75 THEN 5 ELSE 0 END
  + CASE WHEN t.D_RSI < 0.30 THEN -10 ELSE 0 END
  + CASE WHEN t.PE > 0 AND t.PE_MA5Y > 0 AND t.PE < t.PE_MA5Y - 0.5*t.PE_SD5Y THEN 15 ELSE 0 END
  + CASE WHEN t.PE > 0 AND t.PE_MA5Y > 0 AND t.PE > t.PE_MA5Y + 1.0*t.PE_SD5Y THEN -15 ELSE 0 END
  + CASE WHEN vmax.rsi_max3m > 0.65 THEN 10 ELSE 0 END
  + CASE WHEN t.ID_HI_3Y <= 5 THEN 8 ELSE 0 END
  + CASE WHEN t.D_RSI_Max1W > 0.65 THEN 5 ELSE 0 END
  + CASE WHEN t.FSCORE >= 8 THEN 10 ELSE 0 END
  + CASE WHEN t.NP_P0 > t.NP_P4 * 1.5 AND t.NP_P4 > 0 THEN 8 ELSE 0 END
  + CASE WHEN t.NP_P0 < t.NP_P4 * 0.7 AND t.NP_P4 > 0 THEN -8 ELSE 0 END
  + CASE WHEN t.ICB_Code IS NOT NULL AND CAST(FLOOR(t.ICB_Code/1000) AS INT64) IN (8,9) THEN 5 ELSE 0 END
  + CASE WHEN t.ICB_Code IS NOT NULL AND CAST(FLOOR(t.ICB_Code/1000) AS INT64) IN (4,7) THEN -5 ELSE 0 END
  + CASE WHEN t.MA50_T1 > 0 AND t.MA50 > t.MA50_T1 THEN 5 ELSE 0 END
  + CASE WHEN t.MA50_T1 > 0 AND t.MA50 > t.MA50_T1 * 1.005 THEN 5 ELSE 0 END
  + CASE WHEN t.MA50_T1 > 0 AND t.MA50 < t.MA50_T1 THEN -5 ELSE 0 END
  + CASE WHEN t.HI_3M_T1 > 0 AND t.Close / t.HI_3M_T1 < 0.85 THEN -10 ELSE 0 END
  + CASE WHEN t.NP_P0 > t.NP_P1 * 1.2 AND t.NP_P1 > 0 THEN 8 ELSE 0 END
  -- v10: Fin/RE (sector 8) × FA-D bonus / × FA-A penalty (round-12 breakthrough)
  + CASE WHEN CAST(FLOOR(t.ICB_Code/1000) AS INT64) = 8 AND fa.fa_tier_hist = 'D' THEN 10 ELSE 0 END
  + CASE WHEN CAST(FLOOR(t.ICB_Code/1000) AS INT64) = 8 AND fa.fa_tier_hist = 'A' THEN -10 ELSE 0 END
  AS ta_score,
  CASE WHEN t.D_RSI > 0.90 THEN 1 ELSE 0 END AS warn_rsi_blowoff,
  CASE WHEN t.MA20 > 0 AND t.Close / t.MA20 > 1.25 THEN 1 ELSE 0 END AS warn_extended_ma20,
  CASE WHEN t.HI_3M_T1 > 0 AND t.Close / t.HI_3M_T1 < 0.85 THEN 1 ELSE 0 END AS warn_dd_deep
FROM ticker_data AS t
LEFT JOIN fa_dated AS fa
  ON fa.ticker = t.ticker AND t.time >= fa.f_time
 AND (fa.next_f_time IS NULL OR t.time < fa.next_f_time)
LEFT JOIN adv_dated AS adv
  ON adv.ticker = t.ticker AND t.time >= adv.f_time
 AND (adv.next_f_time IS NULL OR t.time < adv.next_f_time)
LEFT JOIN vni_max3m AS vmax ON vmax.time = t.time
-- 5-state may be stale; forward-fill: use most-recent state on or before t.time
LEFT JOIN (
  SELECT t.time, ARRAY_AGG(s.state ORDER BY s.time DESC LIMIT 1)[OFFSET(0)] AS state
  FROM (SELECT DISTINCT time FROM ticker_data) AS t
  LEFT JOIN tav2_bq.vnindex_5state AS s ON s.time <= t.time
  GROUP BY t.time
) AS s5 ON s5.time = t.time
-- Days since latest quarterly Release_Date (Fresh-Q filter, round 19 adoption)
LEFT JOIN (
  SELECT t.ticker,
    DATE_DIFF(DATE '{day}', MAX(tf.Release_Date), DAY) AS days_since_release
  FROM (SELECT DISTINCT ticker FROM ticker_data) AS t
  LEFT JOIN tav2_bq.ticker_financial AS tf
    ON tf.ticker = t.ticker AND tf.Release_Date <= DATE '{day}'
  GROUP BY t.ticker
) AS rel ON rel.ticker = t.ticker
ORDER BY ta_score DESC
"""

# Latest date from EITHER ticker or ticker_1m (auto-pick most recent)
LATEST_DATE_SQL = """
SELECT MAX(d) AS d FROM (
  SELECT MAX(t.time) AS d FROM tav2_bq.ticker AS t WHERE t.D_RSI IS NOT NULL
  UNION ALL
  SELECT MAX(t.time) AS d FROM tav2_bq.ticker_1m AS t WHERE t.D_RSI IS NOT NULL
)
"""

# VN30 universe: top 30 tickers by avg daily liquidity over 2020-2025 window
VN30_QUERY = """
SELECT t.ticker
FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker
ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC
LIMIT 30
"""


def bq(sql: str) -> pd.DataFrame:
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql)
        sql_path = f.name
    try:
        cmd = (f'"{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} '
               f'--format=csv --max_rows=5000 < "{sql_path}"')
        out = subprocess.run(cmd, capture_output=True, text=True, check=True, shell=True)
    finally:
        os.unlink(sql_path)
    return pd.read_csv(StringIO(out.stdout))


def load_fa_full(target_date: str) -> pd.DataFrame:
    """Load latest FA snapshot per ticker (≤ target_date) from cached CSV."""
    fa = pd.read_csv(os.path.join(WORKDIR, "fundamental_rating_all.csv"))
    fa["time"] = pd.to_datetime(fa["time"])
    fa = fa[fa["time"] <= pd.Timestamp(target_date)]
    fa = fa.sort_values("time").groupby("ticker").tail(1).reset_index(drop=True)
    return fa


def classify_play_type(row) -> tuple:
    """BA-system v10 play type classifier — tier thresholds aligned with round-12."""
    ta = row["ta_score"]
    fa_tier = row.get("fa_tier")
    state5 = row.get("state5")
    pe_z = row.get("pe_zscore")
    np_yoy = row.get("np_yoy")
    rev_yoy = row.get("Revenue_YoY_P0")
    has_warn = (row.get("warn_rsi_blowoff", 0) + row.get("warn_extended_ma20", 0)
                + row.get("warn_dd_deep", 0)) >= 1

    if pd.isna(state5) or int(state5) in (1, 2):
        return ("AVOID_bear", 0, "BEAR/CRISIS regime — system stays in cash")

    s = int(state5)

    # ── D1 RE_BACKLOG_BUY (deployed 2026-05-16, validated E4/slot12) ──────
    # ICB 8633 (Real Estate + KCN) with advance-customer surge → leading revenue signal.
    # Fires for C/D FA tier (D1 captures cyclical recovery; sector exempt from cap=4).
    icb_code = row.get("icb_code")
    adv_yoy  = row.get("adv_yoy")
    if (icb_code is not None and not pd.isna(icb_code) and float(icb_code) == 8633.0
        and adv_yoy is not None and not pd.isna(adv_yoy) and float(adv_yoy) > 0.5
        and fa_tier in ("C", "D")
        and ta >= 120 and s in (3, 4, 5)
        and ((not pd.isna(np_yoy) and np_yoy > 0)
             or (not pd.isna(rev_yoy) and rev_yoy > 0))):
        return ("RE_BACKLOG_BUY", 55,
                "BA-core: RE/KCN advance-customer surge — backlog leading revenue (exempt sector cap)")

    if fa_tier == "E":
        return ("AVOID_faE", 5, "FA tier E — quá yếu, không trade")

    # ── BA-system core tiers (v10 thresholds) ──────────────────────────
    if ta >= 170 and s in (4, 5) and fa_tier in ("C", "D"):
        return ("MEGA", 100, "BA-core: ENTER FULL (1/10 portfolio), hold 45d, stop -20%")
    if ta >= 170 and s in (4, 5):
        return ("S_PRO", 50, "Watch only — FA-less = lower edge (NOT in BA-core)")
    if ta >= 155 and s in (4, 5) and fa_tier in ("C", "D"):
        return ("MOMENTUM", 88, "BA-core: ENTER FULL (1/10 portfolio)")
    if ta >= 155 and s in (4, 5) and fa_tier in ("A", "B"):
        return ("MOMENTUM_QUALITY", 65, "Hold core — FA alignment ≠ momentum edge")
    if ta >= 155 and s == 3 and fa_tier in ("C", "D"):
        return ("MOMENTUM_N", 80, "BA-core: ENTER (NEUTRAL caution)")
    if (fa_tier in ("A", "B") and not pd.isna(pe_z) and pe_z < -0.5
        and ta >= 95 and s in (3, 4, 5) and not has_warn):
        return ("COMPOUNDER_BUY", 50, "Long-term accumulate (separate from BA book)")
    if (fa_tier == "C" and ta >= 100 and s in (4, 5)
        and ((not pd.isna(np_yoy) and np_yoy > 0.20)
             or (not pd.isna(rev_yoy) and rev_yoy > 0.20))):
        return ("DEEP_VALUE_RECOVERY", 70, "BA-core: ENTER (1/10 portfolio), recovery setup")
    if ta >= 140 and s in (4, 5):
        return ("MOMENTUM_S", 72, "BA-core: ENTER (1/10 portfolio)")
    if ta >= 125 and s in (4, 5):
        return ("MOMENTUM_A", 55, "Watch — broader, lower conviction")
    if ta >= 140 and s == 3:
        return ("MOMENTUM_S_N", 45, "NEUTRAL caution — only AGGRESSIVE strategy")
    if fa_tier in ("A", "B") and 70 <= ta < 130:
        return ("COMPOUNDER_HOLD", 40, "Hold core, no urgent buy")
    if fa_tier in ("A", "B"):
        return ("WAIT", 30, "Quality stock — wait for technical setup")

    return ("PASS", 15, "No clear setup")


# BA-system core tier set (BAL strategy — entered at 1/10 NAV per pos, up to 12 slots)
BA_CORE_TIERS = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S",
                 "DEEP_VALUE_RECOVERY", "RE_BACKLOG_BUY"]
PRIORITY = {"MEGA": 100, "MOMENTUM": 88, "MOMENTUM_N": 80, "MOMENTUM_S": 72,
            "DEEP_VALUE_RECOVERY": 70, "RE_BACKLOG_BUY": 55}
# Sector cap exempt: RE_BACKLOG can slot beyond Fin/RE=4 cap (D1 alpha source)
SECTOR_CAP_EXEMPT = {"RE_BACKLOG_BUY"}

# F-system F_HAdapted position map (validated: 20% allocation gives Sh 1.26 vs BA-only 1.21)
# Memory: f_ba_mix_results.md
F_HADAPTED_MAP = {1: -1.00, 2: -0.20, 3: +0.70, 4: +1.00, 5: +1.30}
F_OVERLAY_PCT = 0.20  # 20% of capital reserved for F-system overlay


def print_f_overlay(state5: int):
    """Print F-system F_HAdapted overlay position recommendation."""
    if state5 is None:
        return
    s = int(state5)
    pos = F_HADAPTED_MAP.get(s, 0.0)
    state_names = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}
    sname = state_names.get(s, "?")
    nav_pct = pos * F_OVERLAY_PCT * 100  # net VN30F exposure as % of total NAV
    side = "LONG" if pos > 0 else ("SHORT" if pos < 0 else "FLAT")

    print(f"\n{'═' * 88}")
    print(f"  🔄 F-SYSTEM OVERLAY (optional 20% capital, F_HAdapted) — {sname}")
    print(f"{'═' * 88}")
    if pos == 0:
        print(f"  Target VN30F position: FLAT (state={sname})")
        print(f"  No futures action needed in NEUTRAL state under F_HAdapted? — actually +0.70 long")
    print(f"  F_HAdapted target: {pos:+.2f} × VN30 underlying ({side})")
    print(f"  At 20% capital allocation → NET VN30F exposure: {nav_pct:+.1f}% of total NAV")
    if s == 2:  # BEAR
        print(f"  💡 BEAR regime — F-system goes SHORT VN30F. This is when F overlay shines:")
        print(f"     historical 2018 +38%, 2022 +19.8% on F_Balanced (similar profile to F_HAdapted)")
    elif s == 1:  # CRISIS
        print(f"  ⚠ CRISIS regime — max short VN30F. Higher risk, but F historically protected")
    elif s == 3:  # NEUTRAL
        print(f"  📈 NEUTRAL — F still LONG +0.70 (F_HAdapted mirrors H-system in NEUTRAL)")
    elif s == 4:  # BULL
        print(f"  📈 BULL — F LONG full +1.00 leverage")
    elif s == 5:  # EX-BULL
        print(f"  🔥 EX-BULL — F LONG +1.30 (above 1× leverage)")
    print(f"  Hold horizon: state-dependent (re-snap whenever state changes)")
    print(f"  TC: 0.03% per trade, roll cost ~1.2%/yr; T+0 snap on state transition")
    print(f"  NOTE: this overlay is OPTIONAL. Stay 100% BA-system if avoiding futures.")


# ─── V11 PRODUCTION SPEC (deployed 2026-05-15) ───────────────────────────
# Validated 2026-05-14 via test_state_var_with_p3.py + test_v4_adaptive_overheat.py
# Memory: ba_v11_production_proposal.md
# Performance vs v10 baseline (canonical 50/50 12y backtest):
#   FULL CAGR 16.87% → 19.77% (+2.90pp)
#   OOS 2024-2026: 24.26% → 27.00% (+2.74pp)
#   Mid 2018-2023: 20.09% → 25.18% (+5.09pp)
#   Pre-OOS 2014-19: 7.31% → 10.44% (+3.13pp)
#
# V11 changes vs v10:
#   1. P3 COMPOSITE overheat filter (anchor + regime confirmation, self-adapting)
#      Block buys when: VNI/MA200 > 1.30 AND (state5==5 OR VNI_D_RSI > 0.75)
#      Static 1.30 anchor proven robust over 12y (only 31 trigger days, ~0.5%)
#      Regime confirmation (state5/RSI) provides natural adaptation to market shift
#   2. SV_TIGHT state-conditional Fresh-Q:
#      state 1 (CRISIS): ≤30d, state 2-3 (BEAR/NEUTRAL): ≤60d, state 4-5 (BULL): no filter
#      Replaces static 60d-everywhere from previous F1 production
#
# Adaptive alternatives tested + REJECTED (whipsaw, over-filtering):
#   Z-score 1.5/2 SD: -3 to -7pp CAGR loss
#   Walk-forward 5Y p95: overfits to recent
#   State5 transitions alone: too sparse signal

BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}
FRESH_Q_BY_STATE = {1: 30, 2: 60, 3: 60}  # states 4, 5: no filter
P3_VNI_MA200_THRESHOLD = 1.30
P3_VNI_RSI_THRESHOLD = 0.75  # D_RSI 0-1 scale (equiv to 75 on standard 0-100)

# Backward-compat alias (deprecated; use V11 logic via select_book)
FRESH_Q_MAX_DAYS = 60


# Fetch VNI overheat metrics for target date
VNI_OVERHEAT_QUERY = """
SELECT
  t.time,
  t.Close AS vni_close,
  t.MA200 AS vni_ma200,
  t.Close / NULLIF(t.MA200, 0) AS vni_ma200_ratio,
  t.D_RSI AS vni_d_rsi
FROM tav2_bq.ticker AS t
WHERE t.ticker = 'VNINDEX' AND t.time <= DATE '{day}'
  AND t.MA200 IS NOT NULL
ORDER BY t.time DESC
LIMIT 1
"""


def select_book(df: pd.DataFrame, max_positions: int = 10,
                fin_re_cap: int = None,
                state5_today: int = None,
                vni_ma200_ratio: float = None,
                vni_d_rsi: float = None,
                fresh_q_max_days: int = None) -> pd.DataFrame:
    """Pick top BA-core picks with V11 filter stack (deployed 2026-05-15).

    V11 filters:
      1. P3 COMPOSITE overheat: block buys when VNI/MA200 > 1.30 AND (state5==5 OR D_RSI>0.75)
      2. SV_TIGHT Fresh-Q: state-conditional (30d state 1, 60d state 2-3, no filter state 4-5)
      3. play_type ∈ BA_CORE_TIERS
      4. Fin/RE sector ≤ fin_re_cap

    Args:
      state5_today: VNINDEX 5-state regime (1=CRISIS..5=EX-BULL)
      vni_ma200_ratio: VNI Close / MA200 (>1.30 = overheated)
      vni_d_rsi: VNI D_RSI on 0-1 scale (>0.75 = overbought)
      fresh_q_max_days: legacy override; if None uses V11 SV_TIGHT logic

    Sort by (priority desc, ta_score desc), fill up to max_positions.
    """
    cand = df[df["play_type"].isin(BA_CORE_TIERS)].copy()
    if cand.empty:
        return cand

    # ── V11 P3 COMPOSITE: overheat filter (numeric anchor + regime confirmation) ──
    if vni_ma200_ratio is not None:
        overheat_numeric = vni_ma200_ratio > P3_VNI_MA200_THRESHOLD
        regime_confirm = False
        if state5_today is not None and int(state5_today) == 5:
            regime_confirm = True
        if vni_d_rsi is not None and vni_d_rsi > P3_VNI_RSI_THRESHOLD:
            regime_confirm = True
        if overheat_numeric and regime_confirm:
            before = len(cand)
            cand = cand[~cand["play_type"].isin(BUY_TIERS_V11)].copy()
            n_blocked = before - len(cand)
            if n_blocked > 0:
                rsi_str = f"{vni_d_rsi:.3f}" if vni_d_rsi is not None else "n/a"
                print(f"      V11 P3 COMPOSITE overheat (VNI/MA200={vni_ma200_ratio:.3f} "
                      f"> {P3_VNI_MA200_THRESHOLD}, state5={state5_today}, D_RSI={rsi_str}): "
                      f"blocked {n_blocked} buy candidates")
    if cand.empty:
        return cand

    # ── V11 SV_TIGHT: state-conditional Fresh-Q ──
    if fresh_q_max_days is not None:
        # Legacy override path
        threshold = fresh_q_max_days
        threshold_source = f"legacy fresh_q_max_days={threshold}"
    elif state5_today is not None and int(state5_today) in FRESH_Q_BY_STATE:
        threshold = FRESH_Q_BY_STATE[int(state5_today)]
        threshold_source = f"V11 SV_TIGHT state={state5_today} → {threshold}d"
    elif state5_today is not None and int(state5_today) in (4, 5):
        threshold = None  # BULL: no filter
        threshold_source = f"V11 SV_TIGHT state={state5_today} (BULL) → no Fresh-Q filter"
    else:
        threshold = 60  # default fallback (state unknown)
        threshold_source = "fallback state=unknown → 60d"

    if threshold is not None and "days_since_release" in cand.columns:
        before = len(cand)
        cand = cand[cand["days_since_release"].notna() &
                     (cand["days_since_release"] <= threshold)].copy()
        n_filtered = before - len(cand)
        if n_filtered > 0:
            print(f"      V11 SV_TIGHT Fresh-Q ({threshold_source}): removed {n_filtered} stale tickers")

    if cand.empty:
        return cand

    cand["_priority"] = cand["play_type"].map(PRIORITY)
    cand = cand.sort_values(["_priority", "ta_score"], ascending=False).reset_index(drop=True)

    selected = []
    sec_count = {}
    for _, r in cand.iterrows():
        sec = r.get("sector_top")
        pt = r.get("play_type")
        # D1: RE_BACKLOG_BUY exempt from sector cap (slot beyond Fin/RE=4)
        if (fin_re_cap is not None and sec == 8
            and sec_count.get(8, 0) >= fin_re_cap
            and pt not in SECTOR_CAP_EXEMPT):
            continue
        selected.append(r)
        sec_count[sec] = sec_count.get(sec, 0) + 1
        if len(selected) >= max_positions:
            break
    return pd.DataFrame(selected) if selected else cand.iloc[:0]


def print_book(book: pd.DataFrame, label: str, weight_pct: float):
    """Pretty-print a portfolio book (BAL or VN30)."""
    print(f"\n{'═' * 88}")
    print(f"  📋 {label} — {weight_pct:.0f}% portfolio weight")
    print(f"{'═' * 88}")
    if book.empty:
        print("  (no eligible BA-core signals today — keep cash for this book)")
        return
    cols = ["play_type", "ticker", "Close", "ta_score", "fa_tier",
            "rsi", "ma50_slope", "vs_3m_high", "pe_zscore", "np_yoy",
            "sector_top", "liq_b_vnd"]
    print(book[cols].to_string(index=False, float_format=lambda x: f"{x:.2f}"))
    sec_count = book["sector_top"].value_counts().sort_index()
    print(f"\n  Sector breakdown: {dict(sec_count)}")
    fin_re = sec_count.get(8, 0)
    if fin_re >= 4:
        print(f"  ⚠ Fin/RE = {fin_re} (cap = 4) — reached ceiling")


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else bq(LATEST_DATE_SQL)["d"].iloc[0]
    print("=" * 88)
    print(f"  🏆 BA-SYSTEM LIVE ENGINE — {target}")
    print(f"     Strategy: 50% BAL+Fin/RE-max-4 + 50% VN30_BAL  (D1+slot12: RE_BACKLOG exempt)")
    print(f"     PM: max=12pos, 10%/pos cap, hold=45d, stop=-20%, BL20, T+3 min hold")
    print("=" * 88)

    print("\n[1/4] Loading TA v10 scoring + 5-state regime …")
    ta_df = bq(SCORE_SQL.format(day=target))
    print(f"      {len(ta_df)} tickers scored")

    print("[2/4] Loading FA 7-axis breakdown …")
    fa_df = load_fa_full(target)
    print(f"      {len(fa_df)} tickers with FA snapshot")

    print("[3/4] Loading VN30 universe (top 30 by avg liq 2020-2025) …")
    vn30_set = set(bq(VN30_QUERY)["ticker"])
    print(f"      {len(vn30_set)} VN30 tickers: "
          f"{', '.join(sorted(vn30_set)[:10])}, …")

    print("[4/4] Cross-referencing & classifying …")
    fa_cols = ["ticker", "tier", "total_score", "score_quality", "score_stability",
               "score_cash", "score_shareholder", "score_growth", "score_health",
               "score_valuation", "NP_R", "Revenue_YoY_P0", "NP_peak_ratio",
               "Rev_peak_ratio"]
    fa_subset = fa_df[fa_cols].rename(columns={"tier": "fa_tier",
                                                "total_score": "fa_total_score"})
    df = ta_df.merge(fa_subset, on="ticker", how="left")

    LIQ_FLOOR = 1.0
    df_liq = df[df["liq_b_vnd"] >= LIQ_FLOOR].copy()

    play_results = df_liq.apply(classify_play_type, axis=1, result_type="expand")
    play_results.columns = ["play_type", "conviction", "action_note"]
    df_liq = pd.concat([df_liq, play_results], axis=1)
    df_liq = df_liq.sort_values("conviction", ascending=False).reset_index(drop=True)

    state5 = df_liq["state5"].dropna().iloc[0] if df_liq["state5"].notna().any() else None
    state_names = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}
    state_label = state_names.get(int(state5)) if state5 else "?"
    print(f"\n  Market regime (5-state): {state_label} (state={state5})")

    if state5 is not None and int(state5) in (1, 2):
        print("\n  ❌ BEAR/CRISIS regime — BA-system goes to cash. No new entries today.")
        # F-overlay still has a position (SHORT) in BEAR/CRISIS — show it
        print_f_overlay(state5)
        out_path = os.path.join(WORKDIR, f"holistic_{target}.csv")
        df_liq.to_csv(out_path, index=False)
        print(f"\n  Full output saved: {out_path}")
        return

    # ── V11: Fetch VNI overheat metrics for P3 COMPOSITE filter ────────
    print("\n  Loading VNI overheat metrics (V11 P3 COMPOSITE) ...")
    vni_metrics = bq(VNI_OVERHEAT_QUERY.format(day=target))
    if len(vni_metrics) > 0:
        vni_ma200_ratio = float(vni_metrics["vni_ma200_ratio"].iloc[0])
        vni_d_rsi = float(vni_metrics["vni_d_rsi"].iloc[0])
        vni_close = float(vni_metrics["vni_close"].iloc[0])
        vni_ma200 = float(vni_metrics["vni_ma200"].iloc[0])
        print(f"      VNI Close={vni_close:.2f}, MA200={vni_ma200:.2f}, "
              f"ratio={vni_ma200_ratio:.3f}, D_RSI={vni_d_rsi:.3f}")
        overheat = (vni_ma200_ratio > P3_VNI_MA200_THRESHOLD and
                    (int(state5) == 5 or vni_d_rsi > P3_VNI_RSI_THRESHOLD))
        print(f"      Overheated? {'YES — P3 will block new bull buys' if overheat else 'no'}")
    else:
        vni_ma200_ratio = None; vni_d_rsi = None
        print("      WARN: VNI overheat metrics unavailable — P3 filter disabled")

    # ── Build the two books (V11 filter stack applied) ────────────────
    bal_universe = df_liq.copy()  # full ticker_prune
    vn30_universe = df_liq[df_liq["ticker"].isin(vn30_set)].copy()
    state5_int = int(state5) if state5 is not None else None

    # D1+slot12 deployment (2026-05-16): max_positions=12 (was 10).
    # Per-slot size = NAV/10 = 10% per position. Extra 2 slots allow RE_BACKLOG_BUY
    # to fill beyond 10 active positions when triggered. Validated E4: FULL +0.26pp,
    # OOS24-26 +1.65pp, OOS22-26 +1.13pp, DD -14.3% vs v4 -15.1%.
    #
    # BullDvg Boost (Plan A, 2026-05-19): when filtered BullDvg fires (close_hi252<=0.85),
    # expand max_positions 12 -> 15 for 60 sessions. Validated OOS 2019-26: +1.09pp CAGR
    # at lift=25%, Sharpe +0.05, DD unchanged. See bull_div_boost.py + backtest_plan_a.py.
    #
    # SBV Macro Overlay (2026-05-19): composite of refi_chg_90d_lag90 + DXY_rank252.
    # TIGHT regime (score>=+1.0) -> max_pos 12->8. LOOSE regime (score<=-0.7) -> 12->15.
    # Validated FULL +2.37pp, OOS2 2022-26 +2.40pp, 20/20 date-noise trials positive.
    # See sbv_macro_overlay.py + tier2b_sensitivity.py.
    #
    # Combine priority: SBV TIGHT > BullDvg LOOSE > SBV LOOSE > BullDvg LOOSE > Normal
    # (TIGHT macro overrides any upward boost as defensive measure)
    _max_pos = 12
    _max_pos_sources = []
    try:
        from bull_div_boost import get_current_max_positions as _bull_mp
        _bull = _bull_mp()
        if _bull != 12:
            _max_pos_sources.append(('BullDvg', _bull))
    except Exception as _e:
        print(f"  WARN: BullDvg Boost unavailable ({_e})")
    try:
        from sbv_macro_overlay import get_current_max_positions as _sbv_mp
        _sbv = _sbv_mp()
        if _sbv != 12:
            _max_pos_sources.append(('SBV Macro', _sbv))
    except Exception as _e:
        print(f"  WARN: SBV Macro Overlay unavailable ({_e})")

    # Priority resolution: any TIGHT (<12) overrides; otherwise MAX of LOOSE boosts
    if _max_pos_sources:
        tight = [v for _,v in _max_pos_sources if v < 12]
        loose = [v for _,v in _max_pos_sources if v > 12]
        if tight:
            _max_pos = min(tight)  # most defensive wins
            active = ', '.join(f"{n}={v}" for n,v in _max_pos_sources if v < 12)
            print(f"  🛡  Defensive overlay ACTIVE: max_positions {12} -> {_max_pos}  ({active})")
        elif loose:
            _max_pos = max(loose)  # most aggressive boost wins
            active = ', '.join(f"{n}={v}" for n,v in _max_pos_sources if v > 12)
            print(f"  ⚡ Boost overlay ACTIVE: max_positions {12} -> {_max_pos}  ({active})")
    bal_book = select_book(bal_universe, max_positions=_max_pos, fin_re_cap=4,
                            state5_today=state5_int,
                            vni_ma200_ratio=vni_ma200_ratio, vni_d_rsi=vni_d_rsi)
    vn30_book = select_book(vn30_universe, max_positions=_max_pos, fin_re_cap=None,
                             state5_today=state5_int,
                             vni_ma200_ratio=vni_ma200_ratio, vni_d_rsi=vni_d_rsi)

    print_book(bal_book, "BOOK A — BAL+Fin/RE-max-4 (full ticker_prune)", 50)
    print_book(vn30_book, "BOOK B — VN30_BAL (top 30 liquidity)", 50)
    print_f_overlay(state5)

    # ── Distribution summary ───────────────────────────────────────────
    print(f"\n{'═' * 88}")
    print("  PLAY TYPE DISTRIBUTION (entire scored universe)")
    print(f"{'═' * 88}")
    pt_counts = df_liq["play_type"].value_counts()
    order = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY",
             "RE_BACKLOG_BUY",
             "MOMENTUM_S_N", "MOMENTUM_A", "MOMENTUM_QUALITY", "S_PRO",
             "COMPOUNDER_BUY", "COMPOUNDER_HOLD", "WAIT", "PASS",
             "AVOID_bear", "AVOID_faE"]
    for pt in order:
        n = pt_counts.get(pt, 0)
        if n:
            tag = " ⭐ BA-core" if pt in BA_CORE_TIERS else ""
            print(f"  {pt:22} {n:4d}{tag}")

    # ── Detail tables for high-conviction (informational beyond the books) ──
    cols_show = ["ticker", "Close", "ta_score", "fa_tier", "fa_total_score",
                 "rsi", "ma50_slope", "vs_3m_high", "pe_zscore",
                 "np_yoy", "sector_top", "liq_b_vnd"]
    HIGH_CONV = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S",
                 "DEEP_VALUE_RECOVERY", "MOMENTUM_QUALITY", "COMPOUNDER_BUY"]
    for pt in HIGH_CONV:
        sub = df_liq[df_liq["play_type"] == pt]
        if sub.empty:
            continue
        print(f"\n{'─' * 88}")
        print(f"  {pt}  ({len(sub)} mã)  → {sub.iloc[0]['action_note']}")
        print(f"{'─' * 88}")
        print(sub[cols_show].head(15).to_string(index=False,
            float_format=lambda x: f"{x:.2f}"))

    # ── Save ───────────────────────────────────────────────────────────
    out_path = os.path.join(WORKDIR, f"holistic_{target}.csv")
    df_liq.to_csv(out_path, index=False)

    bal_book_path = os.path.join(WORKDIR, f"ba_book_bal_{target}.csv")
    vn30_book_path = os.path.join(WORKDIR, f"ba_book_vn30_{target}.csv")
    if not bal_book.empty:
        bal_book.to_csv(bal_book_path, index=False)
    if not vn30_book.empty:
        vn30_book.to_csv(vn30_book_path, index=False)

    print(f"\n  Full universe saved: {out_path}")
    if not bal_book.empty:
        print(f"  BAL book saved:      {bal_book_path}")
    if not vn30_book.empty:
        print(f"  VN30 book saved:     {vn30_book_path}")

    print(f"\n  ┌{'─' * 86}┐")
    print(f"  │  💡 Execution checklist for tomorrow (T+1 entry):")
    print(f"  │    • BAL book: {len(bal_book)} positions × 5% NAV = {len(bal_book) * 5}% deployed")
    print(f"  │    • VN30 book: {len(vn30_book)} positions × 5% NAV = {len(vn30_book) * 5}% deployed")
    print(f"  │    • Each position 5% (=1/10 of 50% book)")
    print(f"  │    • ⚠ ASYMMETRIC ORDER TIMING (Layer 3 v4):")
    print(f"  │       BUY  at T+1 14:45 ATC (MOC) for T1_TOP (ADV >= 50B/day)")
    print(f"  │            Non-TOP: 11:15 limit @ p_open OR staggered intraday")
    print(f"  │            HYBRID rule adds +1.75pp CAGR / +0.09 Sharpe")
    print(f"  │       SELL at T+1 09:00 ATO/Open (canonical; do NOT delay)")
    print(f"  │            Selling late LOSES alpha (-7.6pp/yr at ATC in BEAR)")
    print(f"  │    • Stop loss -20% from entry, hold 45d, BL20 after stop")
    print(f"  │    • If T-3 ago you stopped a ticker, do NOT re-enter")
    print(f"  └{'─' * 86}┘")


if __name__ == "__main__":
    main()
