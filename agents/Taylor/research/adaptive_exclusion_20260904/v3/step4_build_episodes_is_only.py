"""
Bước 2.3 (chuẩn bị) — build episode CSV (ticker,start,end) từ gate [A] dùng ngưỡng IS-only
(thresholds_is_only.json), CÙNG cơ chế PIT/sustained-2Q/BANNED-rỗng như v2's build_gate_v2.py
(chỉ đổi giá trị 2 ngưỡng, không đổi logic).
"""
import pandas as pd, numpy as np, json

with open("thresholds_is_only.json") as f:
    TH = json.load(f)
DEQ_TH = TH["debt_eq_threshold_PRIMARY_p95"]
DIL_TH = TH["dilution_threshold_PRIMARY_p95"]
print(f"Using IS-only thresholds: Debt_Eq>{DEQ_TH}, dilution>{DIL_TH}")

df = pd.read_csv("universe_financials_v3_intcov.csv", parse_dates=["time", "Release_Date"])
df = df.sort_values(["ticker", "time"]).reset_index(drop=True)
df["eff_date"] = df["Release_Date"]
df.loc[df["eff_date"].isna(), "eff_date"] = df["time"] + pd.Timedelta(days=45)

df["min_oshares_12q"] = df.groupby("ticker")["OShares"].transform(lambda s: s.rolling(12, min_periods=4).min().shift(1))
df["dilution_pct"] = df["OShares"] / df["min_oshares_12q"] - 1

df["r1_negeq"] = df["BVPS"] <= 0
df["r2_combo"] = (df["Debt_Eq_P0"] > DEQ_TH) & (df["EBITDA_P0"] < 0)
df["r2_sust"] = df["r2_combo"] & df.groupby("ticker")["r2_combo"].shift(1).fillna(False)
df["r3_dilution"] = df["dilution_pct"] > DIL_TH
df["any_flag"] = df["r1_negeq"] | df["r2_sust"] | df["r3_dilution"]

def build_episodes(d2):
    rows = []
    for tk, g in d2.groupby("ticker"):
        g = g.sort_values("eff_date").reset_index(drop=True)
        flagged = g["any_flag"].values
        eff = g["eff_date"].values
        i = 0; n = len(g)
        while i < n:
            if flagged[i]:
                start = eff[i]; j = i + 1; clean_run = 0
                end = pd.Timestamp("2027-09-04")
                while j < n:
                    if not flagged[j]:
                        clean_run += 1
                        if clean_run >= 2:
                            end = eff[j]; break
                    else:
                        clean_run = 0
                    j += 1
                rows.append(dict(ticker=tk, start=start, end=end))
                i = j if j > i else i + 1
            else:
                i += 1
    return pd.DataFrame(rows)

episodes = build_episodes(df)
episodes.to_csv("dynamic_exclude_events_v3_is_only.csv", index=False)
print(f"n episodes: {len(episodes)}, n distinct tickers: {episodes['ticker'].nunique()}")
print(f"any_flag rate: {df['any_flag'].mean()*100:.2f}%  (r1={df['r1_negeq'].mean()*100:.2f}%, "
      f"r2_sust={df['r2_sust'].mean()*100:.2f}%, r3={df['r3_dilution'].mean()*100:.2f}%)")

# must-catch check (same as v2 for continuity)
for tk in ["HVN", "BAF"]:
    ep = episodes[episodes.ticker == tk]
    print(f"{tk} episodes: {ep[['start','end']].values.tolist()}")
