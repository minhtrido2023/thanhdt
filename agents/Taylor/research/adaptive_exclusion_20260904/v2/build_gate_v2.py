import pandas as pd, numpy as np

df = pd.read_csv("universe_financials_v2.csv", parse_dates=["time", "Release_Date"])
df = df.sort_values(["ticker", "time"]).reset_index(drop=True)

# PIT anchor: episode becomes visible from Release_Date (fallback: time + 45d if Release_Date missing)
df["eff_date"] = df["Release_Date"]
df.loc[df["eff_date"].isna(), "eff_date"] = df.loc[df["eff_date"].isna(), "time"] + pd.Timedelta(days=45)

df["min_oshares_12q"] = df.groupby("ticker")["OShares"].transform(lambda s: s.rolling(12, min_periods=4).min().shift(1))
df["dilution_pct"] = df["OShares"] / df["min_oshares_12q"] - 1

# --- rule flags, per (ticker, quarter) ---
df["r1_negeq"] = df["BVPS"] <= 0
df["r2_old_combo"] = (df["Debt_Eq_P0"] > 3.5) & (df["IntCov_P0"] < 1.5)         # v1 rule (kept for compare)
df["r2_new_combo"] = (df["Debt_Eq_P0"] > 3.5) & (df["EBITDA_P0"] < 0)          # v2 revised rule (SBA fix)
df["r3_dilution"] = df["dilution_pct"] > 0.80

def sustained2(s):
    return s & s.shift(1).fillna(False)

out = {}
for tag, r2col in [("old", "r2_old_combo"), ("new", "r2_new_combo")]:
    d2 = df.copy()
    d2["r2_sust"] = d2.groupby("ticker")[r2col].transform(sustained2)
    d2["any_flag"] = d2["r1_negeq"] | d2["r2_sust"] | d2["r3_dilution"]
    out[tag] = d2[["ticker","time","quarter","eff_date","r1_negeq","r2_sust","r3_dilution","any_flag"]].copy()

for tag in ["old", "new"]:
    d2 = out[tag]
    n = len(d2)
    print(f"=== gate rule2={tag} === n_neg_eq={d2.r1_negeq.mean()*100:.2f}%  "
          f"n_r2_sust={d2.r2_sust.mean()*100:.2f}%  n_dilution={d2.r3_dilution.mean()*100:.2f}%  "
          f"any_flag={d2.any_flag.mean()*100:.2f}%")

# --- build PIT episodes (start=eff_date of first flagged quarter, end = eff_date of 2nd consecutive clean quarter's release, or far future if unresolved) ---
def build_episodes(d2):
    rows = []
    for tk, g in d2.groupby("ticker"):
        g = g.sort_values("eff_date").reset_index(drop=True)
        flagged = g["any_flag"].values
        eff = g["eff_date"].values
        i = 0
        n = len(g)
        while i < n:
            if flagged[i]:
                start = eff[i]
                j = i + 1
                clean_run = 0
                end = pd.Timestamp("2027-09-04")  # "today"+ far = still active if never 2-clean-quarters found
                while j < n:
                    if not flagged[j]:
                        clean_run += 1
                        if clean_run >= 2:
                            end = eff[j]
                            break
                    else:
                        clean_run = 0
                    j += 1
                rows.append(dict(ticker=tk, start=start, end=end))
                i = j if j > i else i + 1
                # skip past this episode
                while i < n and eff[i] <= end and flagged[max(0,i-1)]:
                    i += 1
                    break
            else:
                i += 1
    return pd.DataFrame(rows)

ep_new = build_episodes(out["new"])
ep_new.to_csv("dynamic_exclude_events_v2final.csv", index=False)
print(f"\n[episodes v2-new] {len(ep_new)} rows, {ep_new.ticker.nunique()} tickers")

# --- flag-rate comparison old vs new on the exact same base (matches earlier ad-hoc BQ query) ---
print("\n=== old rule2 vs new rule2 candidate composition (Debt_Eq>3.5 subset) ===")
sub = df[df["Debt_Eq_P0"] > 3.5]
print("old candidates (IntCov<1.5):", (sub["IntCov_P0"] < 1.5).sum())
print("new candidates (EBITDA<0):  ", (sub["EBITDA_P0"] < 0).sum())
old_c = sub[sub["IntCov_P0"] < 1.5]
print("  of old candidates: %% profitable (NP_P0>0) =", round((old_c["NP_P0"]>0).mean()*100,1))
print("  of old candidates: %% EBITDA>0 =", round((old_c["EBITDA_P0"]>0).mean()*100,1))
