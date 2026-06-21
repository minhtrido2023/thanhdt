"""TA Daily Score v6 — Layer 2 of FA+TA combined system.

Architecture:
  Layer 1 (existing FA-system): tier A/B universe
  Layer 2 (THIS): momentum + value + fresh-high + FA quality + sector tilt
                  + MA50 slope + drawdown filter + earnings momentum + market regime
  Layer 3 (intraday API): timing within day (separate script)

Validated on tav2_bq.ticker (prune universe), 2014-01-01 → 2026-01-16, BULL only:
  TIER_S_PRO   (≥160): n=526   P3M=20.34% hit10=48.7% hit20=37.5% lose10=13.5% (0.04% univ)
  TIER_S_HIGH  (≥145): n=4.5k  P3M=15.51% hit10=46.3% hit20=32.6% lose10=18.0% (0.32% univ)
  TIER_S       (≥130): n=21k   P3M=12.28% hit10=42.5% hit20=28.6% lose10=19.5% (1.5% univ)
  TIER_A       (≥115): n=59k   P3M=10.34% hit10=39.8% hit20=25.9% lose10=19.5% (4.2% univ)
  Baseline     (all):  n=1.39M P3M= 4.5%  hit10=29.5% hit20=17.0% lose10=22.0%

Score formula (max ~184):
  Technical (max 113):
    +25  RSI strong (D_RSI > 0.50)
    +25  Uptrend (Close > MA50 AND MA50 > MA200)
    +20  Volume confirm (Vol >= Vol_3M_P50 * 1.3 AND Close > Close_T1)
    +15  MACD positive (D_MACDdiff > 0)
    +15  Above MA20
    +10  Broad market max3M strong (VNI_RSI_Max3M > 0.65)
     +8  Fresh 3Y high (ID_HI_3Y <= 5)
     +5  RSI Max1W high (D_RSI_Max1W > 0.65)
     +5  Bonus extreme strength (D_RSI > 0.75)
    -10  Penalty weak (D_RSI < 0.30)
  Valuation:
    +15  Cheap PE (PE < PE_MA5Y - 0.5*PE_SD5Y)
    -15  Expensive PE (PE > PE_MA5Y + 1.0*PE_SD5Y)
  FA quality:
    +10  FSCORE >= 8 (Piotroski quality top decile)
     +8  NP earnings growth strong YoY (NP_P0 > 1.5*NP_P4)
     -8  NP earnings decline YoY (NP_P0 < 0.7*NP_P4)
  Sector tilt:
     +5  Sector 8 (Financials/RE) or 9 (Tech/Telecom) — momentum-friendly
     -5  Sector 4 (Health) or 7 (Utilities) — momentum-weak
  Trend confirmation (v6 add):
     +5  MA50 rising (MA50 > MA50_T1)
     +5  MA50 strong rising (MA50 > MA50_T1 * 1.005)
     -5  MA50 falling (MA50 < MA50_T1)
    -10  Drawdown deep (Close/HI_3M_T1 < 0.85 — relief rally pattern)
  Earnings momentum (v6 add):
     +8  NP QoQ acceleration (NP_P0 > NP_P1 * 1.2)

Regime gate: BULL = VNI_RSI > 0.45 AND VNI_MACDdiff > 0
             NEUTRAL = VNI_RSI > 0.40
             BEAR = otherwise (skip — no edge)

Watchlist WARN flags (info only, not in score):
  warn_rsi_blowoff: D_RSI > 0.90 (cliff zone)
  warn_extended_ma20: Close/MA20 > 1.25
  warn_extended_ma50: MA50/MA200 > 1.40

Limitations: 2022 (crash) & 2023 (chop) still negative-edge years even at S_PRO tier.
For production, layer with vnindex_5state_system.py to skip CRISIS/BEAR states.

Run: python ta_score_daily.py [YYYY-MM-DD]
"""
import subprocess
import sys
from io import StringIO

import pandas as pd

PROJECT = "lithe-record-440915-m9"
BQ_BIN = r"bq"

SCORE_SQL = """
WITH fa_dated AS (
  SELECT
    f.ticker, f.time AS f_time, f.tier AS fa_tier, f.total_score AS fa_score,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.fa_ratings AS f
),
state5_table AS (
  SELECT s5.time AS s5_time, s5.state AS state5
  FROM tav2_bq.vnindex_5state AS s5
),
base AS (
  SELECT
    t.ticker, t.time, t.Close, t.Volume,
    t.D_RSI, t.D_RSI_Max1W, t.D_MACDdiff,
    t.MA20, t.MA50, t.MA200, t.MA50_T1, t.HI_3M_T1,
    t.Volume_3M_P50, t.Close_T1,
    t.PE, t.PE_MA5Y, t.PE_SD5Y,
    t.ID_HI_3Y, t.Risk_Rating, t.ICB_Code,
    t.FSCORE, t.NP_P0, t.NP_P1, t.NP_P4, t.ROE5Y, t.ROIC5Y,
    t.VNINDEX_RSI, t.VNINDEX_MACDdiff, t.VNINDEX_RSI_Max3M,
    t.VNINDEX_RSI_MinT3,
    fa.fa_tier, fa.fa_score,
    s5.state5,
    -- Technical
    CASE WHEN t.D_RSI > 0.50                          THEN 25 ELSE 0 END AS s_rsi_strong,
    CASE WHEN t.Close > t.MA50 AND t.MA50 > t.MA200   THEN 25 ELSE 0 END AS s_uptrend,
    CASE WHEN t.Volume >= t.Volume_3M_P50 * 1.3
          AND t.Close > t.Close_T1                    THEN 20 ELSE 0 END AS s_volume,
    CASE WHEN t.D_MACDdiff > 0                        THEN 15 ELSE 0 END AS s_macd_pos,
    CASE WHEN t.Close > t.MA20                        THEN 15 ELSE 0 END AS s_above_ma20,
    CASE WHEN t.VNINDEX_RSI_Max3M > 0.65              THEN 10 ELSE 0 END AS s_vni_max3m,
    CASE WHEN t.ID_HI_3Y <= 5                         THEN  8 ELSE 0 END AS s_fresh_high,
    CASE WHEN t.D_RSI_Max1W > 0.65                    THEN  5 ELSE 0 END AS s_rsi_max1w,
    CASE WHEN t.D_RSI > 0.75                          THEN  5 ELSE 0 END AS s_bonus_extreme,
    CASE WHEN t.D_RSI < 0.30                          THEN -10 ELSE 0 END AS s_penalty_weak,
    -- Valuation
    CASE WHEN t.PE > 0 AND t.PE_MA5Y > 0 AND t.PE < t.PE_MA5Y - 0.5*t.PE_SD5Y
                                                      THEN 15 ELSE 0 END AS s_cheap_pe,
    CASE WHEN t.PE > 0 AND t.PE_MA5Y > 0 AND t.PE > t.PE_MA5Y + 1.0*t.PE_SD5Y
                                                      THEN -15 ELSE 0 END AS s_expensive_pe,
    -- FA quality
    CASE WHEN t.FSCORE >= 8                                         THEN 10 ELSE 0 END AS s_fscore_top,
    CASE WHEN t.NP_P0 > t.NP_P4 * 1.5 AND t.NP_P4 > 0               THEN  8 ELSE 0 END AS s_np_growth,
    CASE WHEN t.NP_P0 < t.NP_P4 * 0.7 AND t.NP_P4 > 0               THEN -8 ELSE 0 END AS s_np_decline,
    -- Sector tilt
    CASE WHEN t.ICB_Code IS NOT NULL
          AND CAST(FLOOR(t.ICB_Code / 1000) AS INT64) IN (8, 9)
                                                      THEN  5 ELSE 0 END AS s_sector_strong,
    CASE WHEN t.ICB_Code IS NOT NULL
          AND CAST(FLOOR(t.ICB_Code / 1000) AS INT64) IN (4, 7)
                                                      THEN -5 ELSE 0 END AS s_sector_weak,
    -- Trend confirmation (v6)
    CASE WHEN t.MA50_T1 > 0 AND t.MA50 > t.MA50_T1               THEN  5 ELSE 0 END AS s_ma50_rising,
    CASE WHEN t.MA50_T1 > 0 AND t.MA50 > t.MA50_T1 * 1.005       THEN  5 ELSE 0 END AS s_ma50_strong,
    CASE WHEN t.MA50_T1 > 0 AND t.MA50 < t.MA50_T1               THEN -5 ELSE 0 END AS s_ma50_falling,
    CASE WHEN t.HI_3M_T1 > 0 AND t.Close / t.HI_3M_T1 < 0.85     THEN -10 ELSE 0 END AS s_dd_deep,
    -- Earnings momentum (v6)
    CASE WHEN t.NP_P0 > t.NP_P1 * 1.2 AND t.NP_P1 > 0            THEN  8 ELSE 0 END AS s_np_qoq,
    -- Regime (v7: 4-state with BULL_strong)
    CASE
      WHEN t.VNINDEX_RSI > 0.55 AND t.VNINDEX_MACDdiff > 0
           AND t.VNINDEX_RSI_MinT3 > 0.45                       THEN 'BULL_strong'
      WHEN t.VNINDEX_RSI > 0.45 AND t.VNINDEX_MACDdiff > 0      THEN 'BULL'
      WHEN t.VNINDEX_RSI > 0.40                                 THEN 'NEUTRAL'
      ELSE                                                            'BEAR'
    END AS regime
  FROM tav2_bq.ticker AS t
  LEFT JOIN fa_dated AS fa
    ON fa.ticker = t.ticker AND t.time >= fa.f_time
   AND (fa.next_f_time IS NULL OR t.time < fa.next_f_time)
  LEFT JOIN state5_table AS s5 ON s5.s5_time = t.time
  WHERE t.time = DATE '{day}'
    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
)
SELECT
  time, ticker, Close, Volume,
  s_rsi_strong + s_uptrend + s_volume + s_macd_pos + s_above_ma20
    + s_cheap_pe + s_vni_max3m + s_fresh_high + s_rsi_max1w
    + s_bonus_extreme + s_penalty_weak + s_expensive_pe
    + s_fscore_top + s_np_growth + s_np_decline
    + s_sector_strong + s_sector_weak
    + s_ma50_rising + s_ma50_strong + s_ma50_falling + s_dd_deep
    + s_np_qoq AS score,
  regime,
  ROUND(D_RSI, 2)              AS rsi,
  ROUND(D_RSI_Max1W, 2)        AS rsi_max1w,
  ROUND(D_MACDdiff, 1)         AS macd_diff,
  ROUND(Close / MA50 - 1, 3)   AS vs_ma50,
  ROUND(MA20 / NULLIF(Close, 0) - 1, 3) AS vs_ma20,
  ROUND(MA50 / NULLIF(MA200, 0) - 1, 3) AS ma50_spread,
  ROUND(PE, 1)                 AS pe,
  ROUND((PE - PE_MA5Y) / NULLIF(PE_SD5Y, 0), 2) AS pe_zscore,
  CAST(FSCORE AS INT64)        AS fscore,
  ROUND(SAFE_DIVIDE(NP_P0, NP_P4) - 1, 2) AS np_yoy,
  ROUND(ROE5Y * 100, 1)        AS roe5y_pct,
  fa_tier,
  ROUND(fa_score, 2)           AS fa_score,
  state5,
  CAST(ICB_Code AS INT64)      AS icb,
  CAST(FLOOR(ICB_Code / 1000) AS INT64) AS sector_top,
  ID_HI_3Y                     AS days_since_hi3y,
  ROUND(Risk_Rating, 1)        AS risk,
  ROUND(VNINDEX_RSI, 2)        AS vni_rsi,
  ROUND(VNINDEX_RSI_Max3M, 2)  AS vni_max3m,
  ROUND(Volume_3M_P50 * Close / 1e9, 2) AS liq_b_vnd,
  ROUND(SAFE_DIVIDE(MA50, MA50_T1) - 1, 4) AS ma50_slope,
  ROUND(SAFE_DIVIDE(Close, HI_3M_T1) - 1, 3) AS vs_3m_high,
  ROUND(SAFE_DIVIDE(NP_P0, NP_P1) - 1, 2)    AS np_qoq,
  CASE WHEN D_RSI > 0.90 THEN 1 ELSE 0 END                       AS warn_rsi_blowoff,
  CASE WHEN MA20 > 0 AND Close / MA20 > 1.25 THEN 1 ELSE 0 END   AS warn_extended_ma20,
  CASE WHEN MA200 > 0 AND MA50 / MA200 > 1.40 THEN 1 ELSE 0 END  AS warn_extended_ma50,
  CASE WHEN HI_3M_T1 > 0 AND Close / HI_3M_T1 < 0.85 THEN 1 ELSE 0 END AS warn_dd_deep,
  s_rsi_strong, s_uptrend, s_volume, s_macd_pos, s_above_ma20,
  s_cheap_pe, s_vni_max3m, s_fresh_high, s_rsi_max1w,
  s_bonus_extreme, s_penalty_weak, s_expensive_pe,
  s_fscore_top, s_np_growth, s_np_decline,
  s_sector_strong, s_sector_weak,
  s_ma50_rising, s_ma50_strong, s_ma50_falling, s_dd_deep, s_np_qoq
FROM base
ORDER BY score DESC, ticker
"""

LATEST_DATE_SQL = """
SELECT MAX(t.time) AS d FROM tav2_bq.ticker AS t WHERE t.D_RSI IS NOT NULL
"""


def bq(sql: str) -> pd.DataFrame:
    import tempfile, os
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


def tier(score: float, state5, fa_tier: str = None) -> str:
    """
    v9 tier — uses VNINDEX 5-state system as regime gate (replaces heuristic).

    State map (from vnindex_5state_system.py):
      1=CRISIS (0% alloc), 2=BEAR (20%), 3=NEUTRAL (70%), 4=BULL (100%), 5=EX-BULL (130%)

    Validated edges:
      MEGA (S160+ + state 4,5 + FA C/D): n=148, P3M=32.8%, hit20=59.5%, lose10=4.1% ⭐⭐⭐
      S_PRO (S160+ + state 4,5):                 P3M=21.4%, hit20=39.4%, lose10=13.6%
      S_HIGH (S145+ + state 4,5 + FA C/D):       P3M=20.3%, hit20=42.4%, lose10=15.7%
      S145+ + state=4 BULL only:                 P3M=19.9%, hit20=41.9%, lose10=14.0%
      S145+ + state=5 EX-BULL:                   P3M=15.1%, hit20=32.0%, lose10=25.1% (risky!)
      S145+ + state IN (1,2) BEAR:               P3M= 6.7%, hit20=20.2%, lose10=25.4% (skip!)

    FA tier × momentum is INVERSE: FA A/B compounders underperform momentum trades;
    FA C/D (recovery/junk-rally) outperform.
    """
    if state5 is None:
        # Fallback: no state data (probably future date)
        return "NO_STATE"
    s = int(state5)
    if s in (1, 2):
        return "BEAR_skip"      # state CRISIS or BEAR — no edge, lose10 high
    fa = fa_tier if fa_tier else "?"
    # MEGA-ELITE: S160+ + BULL/EX-BULL + FA C/D recovery
    if score >= 160 and s in (4, 5) and fa in ("C", "D"):
        return "MEGA"
    if score >= 160 and s in (4, 5):
        return "S_PRO"
    if score >= 145 and s in (4, 5):
        if fa in ("C", "D"):
            return "S_HIGH"
        if fa in ("A", "B"):
            return "S_HIGH_AB"
        return "S_HIGH"
    if score >= 145 and s == 3:
        return "S_HIGH_N"        # NEUTRAL caution
    if score >= 130 and s in (3, 4, 5):
        return "S"          if s != 3 else "S_N"
    if score >= 115 and s in (3, 4, 5):
        return "A"          if s != 3 else "A_N"
    if score >= 95:
        return "B"
    if score >= 70:
        return "C"
    return "PASS"


def main():
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = bq(LATEST_DATE_SQL)["d"].iloc[0]
    print(f"Target date: {target}")

    df = bq(SCORE_SQL.format(day=target))
    if df.empty:
        print(f"No data for {target}")
        return

    df["tier"] = df.apply(lambda r: tier(r["score"], r.get("state5"), r.get("fa_tier")), axis=1)

    regime = df["regime"].iloc[0]
    vni_rsi = df["vni_rsi"].iloc[0]
    vni_max3m = df["vni_max3m"].iloc[0]
    print(f"Market regime: {regime}  (VNI RSI={vni_rsi}, RSI_Max3M={vni_max3m})")
    print(f"Stocks scored: {len(df)}")

    state_names = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}
    s5 = df["state5"].dropna().iloc[0] if "state5" in df.columns and df["state5"].notna().any() else None
    s5_label = state_names.get(int(s5), f"?{s5}") if s5 is not None else "NO_DATA"
    print(f"  5-state regime: {s5_label} (state={s5})")

    print("\n--- Tier distribution ---")
    for t in ["MEGA", "S_PRO", "S_HIGH", "S_HIGH_AB", "S_HIGH_N", "S", "S_N", "A", "A_N",
              "B", "C", "PASS", "BEAR_skip", "NO_STATE"]:
        n = (df["tier"] == t).sum()
        if n:
            print(f"  {t:11} {n:4d} ({n/len(df)*100:.1f}%)")

    if regime == "BEAR":
        print("\n[!] Market regime BEAR — TA score has no edge. Skip trading.")
        out_path = f"ta_score_watchlist_{target}.csv"
        df.to_csv(out_path, index=False)
        print(f"\nFull output saved: {out_path}")
        return

    # Apply liquidity floor for live watchlist (per memory feedback_liquidity_filter)
    LIQ_FLOOR = 1.0  # 1B VND
    eligible = ["MEGA", "S_PRO", "S_HIGH", "S_HIGH_AB", "S_HIGH_N", "S", "S_N", "A", "A_N"]
    watchlist = df[(df["tier"].isin(eligible)) &
                   (df["liq_b_vnd"] >= LIQ_FLOOR)].copy()

    watchlist["warn"] = (
        watchlist["warn_rsi_blowoff"].astype(int)
        + watchlist["warn_extended_ma20"].astype(int)
        + watchlist["warn_extended_ma50"].astype(int)
        + watchlist["warn_dd_deep"].astype(int)
    )
    watchlist["warn_tag"] = watchlist.apply(
        lambda r: ",".join(filter(None, [
            "RSI>0.90"   if r["warn_rsi_blowoff"]   else "",
            "vsMA20>25%" if r["warn_extended_ma20"] else "",
            "MA50>1.40"  if r["warn_extended_ma50"] else "",
            "DD<-15%"    if r["warn_dd_deep"]       else "",
        ])) or "-", axis=1)

    print(f"\n--- Watchlist (tier ∈ {{MEGA,S_PRO,S_HIGH,S_HIGH_AB,*_N,S,A}} + liq ≥ {LIQ_FLOOR}B VND): {len(watchlist)} mã ---")
    cols = ["tier", "ticker", "Close", "score", "rsi",
            "ma50_slope", "vs_3m_high", "pe_zscore", "fscore",
            "np_yoy", "np_qoq", "fa_tier", "sector_top", "liq_b_vnd", "warn_tag"]
    if not watchlist.empty:
        print(watchlist[cols].to_string(index=False))
        n_warn = (watchlist["warn"] >= 1).sum()
        if n_warn:
            print(f"\n  ⚠ {n_warn}/{len(watchlist)} mã có cảnh báo overextension — cân nhắc giảm size hoặc chờ pullback")

    out_path = f"ta_score_watchlist_{target}.csv"
    df.to_csv(out_path, index=False)
    print(f"\nFull output saved: {out_path}")


if __name__ == "__main__":
    main()
