"""
Bước 2.1 — chọn ngưỡng gate [A] rule2 (Debt_Eq) và rule3 (dilution) CHỈ bằng dữ liệu
<= 2019-12-31, KHÔNG nhìn danh tính 16 mã BANNED và KHÔNG nhìn kết quả OOS.

Tiêu chí khai TRƯỚC (frozen, không đổi sau khi thấy OOS):
  "ngưỡng = percentile 95 của phân phối metric trên universe IS (<=2019-12-31)"
  -- quy ước thống kê chuẩn "gắn cờ đuôi 5% cực đoan nhất", không tham chiếu tên mã nào.
  Percentile 90 tính song song làm robustness check (KHÔNG phải ngưỡng chính).
N_TRIALS bước này = 1 (chỉ 1 quy tắc chọn: percentile-95-của-IS, p90 là phụ lục robustness
tính CÙNG LÚC, không phải thử-rồi-chọn lại theo kết quả).
"""
import pandas as pd, numpy as np, json
from datetime import datetime, timezone

df = pd.read_csv("universe_financials_v3_intcov.csv", parse_dates=["time", "Release_Date"])
df = df.sort_values(["ticker", "time"]).reset_index(drop=True)

IS_CUTOFF = pd.Timestamp("2019-12-31")
is_df = df[df["time"] <= IS_CUTOFF].copy()

# dilution_pct: same construction as v2 (rolling 12Q min OShares, shift(1) to stay PIT)
df["min_oshares_12q"] = df.groupby("ticker")["OShares"].transform(lambda s: s.rolling(12, min_periods=4).min().shift(1))
df["dilution_pct"] = df["OShares"] / df["min_oshares_12q"] - 1
is_df["min_oshares_12q"] = df.loc[is_df.index, "min_oshares_12q"]
is_df["dilution_pct"] = df.loc[is_df.index, "dilution_pct"]

# --- Debt_Eq_P0 threshold (rule2), IS-only distribution, all (ticker,quarter) rows <=2019-12-31 ---
deq_is = is_df["Debt_Eq_P0"].dropna()
deq_p90 = deq_is.quantile(0.90)
deq_p95 = deq_is.quantile(0.95)

# --- dilution_pct threshold (rule3), IS-only distribution ---
dil_is = is_df["dilution_pct"].dropna()
dil_is = dil_is[dil_is.abs() < 50]  # drop absurd outliers (e.g. OShares data errors, |dilution|>5000%) before quantile
dil_p90 = dil_is.quantile(0.90)
dil_p95 = dil_is.quantile(0.95)

thresholds = {
    "selected_at_utc": datetime.now(timezone.utc).isoformat(),
    "is_cutoff": "2019-12-31",
    "criterion": "percentile-95 of the metric distribution on IS universe (<=2019-12-31), frozen before any OOS run; p90 computed in parallel as a robustness variant, not a re-pick",
    "n_trials_this_step": 1,
    "n_obs_is_debt_eq": int(len(deq_is)),
    "n_obs_is_dilution": int(len(dil_is)),
    "debt_eq_threshold_PRIMARY_p95": round(float(deq_p95), 4),
    "debt_eq_threshold_robustness_p90": round(float(deq_p90), 4),
    "dilution_threshold_PRIMARY_p95": round(float(dil_p95), 4),
    "dilution_threshold_robustness_p90": round(float(dil_p90), 4),
    "rule2_definition": "Debt_Eq_P0 > debt_eq_threshold AND EBITDA_P0 < 0, sustained 2 consecutive quarters (unchanged from v2's semantic fix, only the Debt_Eq cutoff value is now IS-only)",
    "rule3_definition": "dilution_pct > dilution_threshold (OShares / min(OShares, trailing 12Q, shifted 1) - 1)",
    "rule1_definition": "BVPS <= 0 (unchanged, not a tuned threshold -- objective accounting fact)",
}
print(json.dumps(thresholds, indent=2, ensure_ascii=False))
with open("thresholds_is_only.json", "w") as f:
    json.dump(thresholds, f, indent=2, ensure_ascii=False)

# also compare to v2's hindsight-fit values for transparency (not used in the gate itself)
print("\n--- for reference only, v2 hindsight-fit values (NOT used in this v3 gate) ---")
print("v2 Debt_Eq threshold: 3.5 (fixed constant, inherited from v1)")
print("v2 dilution threshold: 0.80 (explicitly matched to BAF's actual 84% dilution)")
