# -*- coding: utf-8 -*-
"""Phase-0 0c — IC/hit-rate DAY DU theo context that cho fa_ratings_8l (rating/route/tier).
Job Taylor_20260711_114557 (plan plan_fa8l_retune_20260711.md muc 0c). QUYET DINH CP0 go/no-go.

Nguon du lieu: BigQuery THAT (SDK google-cloud-bigquery, KHONG dung DuckDB cache/pkl) —
theo yeu cau user "dua tren du lieu thuc te, khong phai so lieu ao".

Thiet ke:
- Universe: prune-membership (nhu SIGNAL_V11 ticker_data), liq >= 1e9, D_RSI IS NOT NULL.
- Sampling: WEEKLY (thu Tu, DAYOFWEEK=4) 2014-01-01 -> 2026-06-19 (giam autocorrelation overlap;
  descriptive stats, khong phai selection).
- ta_base = ta cua SIGNAL_V11 TRU 2 term fa_tier (T7 bank-adjust) -> tier-neutral, tranh
  circularity giua 2 thang do khi so sanh (T7 chi anh huong ICB8 +-10).
- state5 = tav2_bq.vnindex_5state_dt5g_live as-of (PRODUCTION gated state — theo data_registry).
- As-of join: fa_ratings_8l (rating 1-5, route, tier A-E) + legacy fa_ratings (fa_tier control).
- Forward: profit_2W (T+10), profit_1M (T+20), profit_2M (T+40), profit_3M (T+60) — forward cols,
  CHI dung cho research/IC, khong bao gio lam live filter.
- IS 2014-2019 / OOS 2020+.

Output: data/fa8l_exp/ic_context_8l_20260711.csv (tidy, moi dong = context x scale x horizon)
        + digest in ra stdout. KHONG cham file canonical nao (guidelines #8).
"""
import sys, io
import numpy as np
import pandas as pd
from scipy import stats
from google.cloud import bigquery

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
PROJECT = "lithe-record-440915-m9"
OUT_CSV = "/home/trido/thanhdt/WorkingClaude/data/fa8l_exp/ic_context_8l_20260711.csv"
START, END = "2014-01-01", "2026-06-19"

SQL = f"""
WITH vni_history AS (
  SELECT t.time, t.D_RSI FROM tav2_bq.ticker AS t
  WHERE t.ticker = 'VNINDEX' AND t.D_RSI IS NOT NULL
),
vni_max3m AS (
  SELECT time, MAX(D_RSI) OVER (ORDER BY time ROWS BETWEEN 59 PRECEDING AND CURRENT ROW) AS rsi_max3m
  FROM vni_history
),
fa8_dated AS (
  SELECT f.ticker, f.time AS f_time, f.rating, f.route, f.tier AS tier8l,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.fa_ratings_8l AS f
),
leg_dated AS (
  SELECT f.ticker, f.time AS f_time, f.tier AS fa_tier_leg,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.fa_ratings AS f
),
base AS (
  SELECT t.ticker, t.time, t.Close,
    (CASE WHEN t.D_RSI > 0.50 THEN 25 ELSE 0 END
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
    + CASE WHEN t.NP_P0 > t.NP_P1 * 1.2 AND t.NP_P1 > 0 THEN 8 ELSE 0 END) AS ta_base,
    (t.PE - t.PE_MA5Y) / NULLIF(t.PE_SD5Y, 0) AS pe_z,
    (t.D_RSI > 0.90 OR (t.MA20 > 0 AND t.Close / t.MA20 > 1.25)) AS warn_ext,
    CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS sec,
    t.profit_2W, t.profit_1M, t.profit_2M, t.profit_3M
  FROM tav2_bq.ticker AS t
  LEFT JOIN vni_max3m AS vmax ON vmax.time = t.time
  WHERE t.time BETWEEN DATE '{START}' AND DATE '{END}'
    AND EXTRACT(DAYOFWEEK FROM t.time) = 4
    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
    AND t.D_RSI IS NOT NULL
    AND t.Volume_3M_P50 * COALESCE(t.Price, t.Close) >= 1e9
),
staterc AS (
  SELECT b.time AS btime,
    ARRAY_AGG(s.state ORDER BY s.time DESC LIMIT 1)[OFFSET(0)] AS state5
  FROM (SELECT DISTINCT time FROM base) AS b
  LEFT JOIN tav2_bq.vnindex_5state_dt5g_live AS s ON s.time <= b.time
  GROUP BY b.time
),
rel AS (
  SELECT b.ticker, b.time, DATE_DIFF(b.time, MAX(tf.Release_Date), DAY) AS days_since_release
  FROM (SELECT DISTINCT ticker, time FROM base) AS b
  LEFT JOIN tav2_bq.ticker_financial AS tf
    ON tf.ticker = b.ticker AND tf.Release_Date <= b.time
  GROUP BY b.ticker, b.time
)
SELECT b.*, st.state5, r.days_since_release,
  fa8.rating, fa8.route, fa8.tier8l, leg.fa_tier_leg
FROM base AS b
LEFT JOIN staterc AS st ON st.btime = b.time
LEFT JOIN rel AS r ON r.ticker = b.ticker AND r.time = b.time
LEFT JOIN fa8_dated AS fa8
  ON fa8.ticker = b.ticker AND b.time >= fa8.f_time
 AND (fa8.next_f_time IS NULL OR b.time < fa8.next_f_time)
LEFT JOIN leg_dated AS leg
  ON leg.ticker = b.ticker AND b.time >= leg.f_time
 AND (leg.next_f_time IS NULL OR b.time < leg.next_f_time)
"""

print("[0c] querying REAL BigQuery (weekly panel 2014->2026-06-19)...")
client = bigquery.Client(project=PROJECT)
job = client.query(SQL)
df = job.result().to_dataframe()
print(f"  rows: {len(df):,}   bytes processed: {job.total_bytes_processed/1e9:.2f} GB")
df["time"] = pd.to_datetime(df["time"])
df["is_oos"] = np.where(df["time"] < "2020-01-01", "IS", "OOS")
TIER_MAP = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}
df["tier8l_n"] = df["tier8l"].map(TIER_MAP)
df["leg_n"] = df["fa_tier_leg"].map(TIER_MAP)
df["fresh60"] = df["days_since_release"].notna() & (df["days_since_release"] <= 60)

# route groups: scored routes (co lich su chấm diem tich cuc) vs neutral-mode routes
NEUTRAL_ROUTES = {"BANK", "POWER", "SECURITIES", "INSURANCE"}
df["routegrp"] = np.where(df["route"].isin(NEUTRAL_ROUTES), "NEUTRALMODE",
                  np.where(df["route"].notna(), "SCORED", "NOROUTE"))

HORIZONS = ["profit_2W", "profit_1M", "profit_2M", "profit_3M"]

# ---- context definitions (production-shaped, theo plan: ta-threshold x state5 x route) ----
def ctx_masks(d):
    s45 = d["state5"].isin([4, 5]); s3 = d["state5"] == 3; s12 = d["state5"].isin([1, 2])
    out = {
        "ALL":                     pd.Series(True, index=d.index),
        "state45":                 s45,
        "state3":                  s3,
        "state12":                 s12,
        "ta170_s45":               (d["ta_base"] >= 170) & s45,
        "ta155_s45":               (d["ta_base"] >= 155) & s45,
        "ta140_s45":               (d["ta_base"] >= 140) & s45,
        "ta125_s45":               (d["ta_base"] >= 125) & s45,
        "ta155_s3_fresh60":        (d["ta_base"] >= 155) & s3 & d["fresh60"],
        "ta140_s3":                (d["ta_base"] >= 140) & s3,
        "compound_pez_ta95_s345":  (d["pe_z"] < -0.5) & (d["ta_base"] >= 95) & d["state5"].isin([3,4,5]) & (~d["warn_ext"].fillna(False).astype(bool)),
        "ta155_s45_SCORED":        (d["ta_base"] >= 155) & s45 & (d["routegrp"] == "SCORED"),
        "ta155_s45_NEUTRALMODE":   (d["ta_base"] >= 155) & s45 & (d["routegrp"] == "NEUTRALMODE"),
        "ta125_s45_SCORED":        (d["ta_base"] >= 125) & s45 & (d["routegrp"] == "SCORED"),
        "ta125_s45_NEUTRALMODE":   (d["ta_base"] >= 125) & s45 & (d["routegrp"] == "NEUTRALMODE"),
        "s45_BANK":                s45 & (d["route"] == "BANK"),
        "s45_SECURITIES":          s45 & (d["route"] == "SECURITIES"),
        "s345_REALESTATE":         d["state5"].isin([3,4,5]) & (d["route"] == "REALESTATE"),
    }
    return out

SCALES = {"rating8l": "rating", "tier8l": "tier8l_n", "legacy": "leg_n"}

rows = []
for period in ["IS", "OOS", "FULL"]:
    d = df if period == "FULL" else df[df["is_oos"] == period]
    masks = ctx_masks(d)
    for ctx, m in masks.items():
        sub = d[m]
        for scale, col in SCALES.items():
            for h in HORIZONS:
                v = sub[[col, h]].dropna()
                n = len(v)
                if n < 50:
                    continue
                ic, icp = stats.spearmanr(v[col], v[h])
                rec = {"period": period, "context": ctx, "scale": scale, "horizon": h,
                       "n": n, "ic": round(float(ic), 4), "ic_p": round(float(icp), 4)}
                # per-level mean fwd + hitrate (level 1..5)
                for lv in [1, 2, 3, 4, 5]:
                    lvv = v[v[col] == lv][h]
                    rec[f"n{lv}"] = len(lvv)
                    rec[f"mean{lv}"] = round(float(lvv.mean()), 4) if len(lvv) >= 20 else np.nan
                    rec[f"hit{lv}"] = round(float((lvv > 0).mean()), 4) if len(lvv) >= 20 else np.nan
                rows.append(rec)

res = pd.DataFrame(rows)
res.to_csv(OUT_CSV, index=False)
print(f"  -> {OUT_CSV}  ({len(res)} cells)")

# ---- digest: cac context production quyet dinh CP0 ----
KEY_CTX = ["ta170_s45", "ta155_s45", "ta140_s45", "ta125_s45", "ta155_s3_fresh60",
           "ta140_s3", "compound_pez_ta95_s345", "ta155_s45_SCORED", "ta155_s45_NEUTRALMODE",
           "state45", "state3", "ALL"]
pd.set_option("display.width", 250)
for scale in SCALES:
    print("\n" + "=" * 130)
    print(f"  SCALE = {scale}   (IC>0 = level cao/te hon -> fwd cao hon; voi rating: AM = quality giup)")
    print("=" * 130)
    for h in ["profit_1M", "profit_2M"]:
        print(f"\n--- horizon {h} ---")
        sub = res[(res["scale"] == scale) & (res["horizon"] == h) & res["context"].isin(KEY_CTX)]
        piv = sub.pivot_table(index="context", columns="period", values=["ic", "n"], aggfunc="first")
        piv = piv.reindex(KEY_CTX)
        print(piv.to_string())

print("\n--- per-rating mean fwd (rating8l, profit_2M, cac context chinh) ---")
for period in ["IS", "OOS"]:
    print(f"\n[{period}]")
    sub = res[(res["scale"] == "rating8l") & (res["horizon"] == "profit_2M") & (res["period"] == period) & res["context"].isin(KEY_CTX)]
    cols = ["context", "n", "ic"] + [f"mean{i}" for i in range(1, 6)] + [f"hit{i}" for i in range(1, 6)]
    print(sub[cols].to_string(index=False))
print("\nDONE 0c.")
