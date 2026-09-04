import pandas as pd, numpy as np

df = pd.read_csv("universe_financials_v3_intcov.csv", parse_dates=["time", "Release_Date"])
df = df.sort_values(["ticker", "time"]).reset_index(drop=True)

# EBITM_P0 median=0.0545, p75=0.133 across 56,576 rows -- ALREADY a fraction (5.45% median EBIT
# margin), not a "x100 percent" number. quant-skeptic's verify log used EBITM_P0/100*Revenue_P0
# (an extra spurious /100) -- corrected here; see v3 report for the reproduced discrepancy.
df["EBIT_est"] = df["EBITM_P0"] * df["Revenue_P0"]
df["EBIT_est_skeptic_wrong"] = df["EBITM_P0"] / 100.0 * df["Revenue_P0"]
df["TotalDebt"] = df["StDebt_P0"].fillna(0) + df["LtDebt_P0"].fillna(0)
df["CashLike"] = df["Cash_P0"].fillna(0) + df["LtInvest_P0"].fillna(0)
df["NetDebt"] = df["TotalDebt"] - df["CashLike"]

# implied denominator, both numerator candidates, only where IntCov_P0 well away from 0 (avoid div blowup)
mask = df["IntCov_P0"].abs() > 0.05
df.loc[mask, "implied_denom_EBIT"] = df.loc[mask, "EBIT_est"] / df.loc[mask, "IntCov_P0"]
df.loc[mask, "implied_denom_EBITDA"] = df.loc[mask, "EBITDA_P0"] / df.loc[mask, "IntCov_P0"]

# ---- Part A: SBA + HVN case detail (numerator sign-sanity, reproduce v2 numbers) ----
for tk in ["SBA", "HVN"]:
    g = df[(df.ticker == tk) & (df.quarter.isin(["2013Q1", "2016Q1", "2020Q1", "2024Q4"]))]
    print(f"\n=== {tk} spot quarters ===")
    print(g[["quarter", "IntCov_P0", "EBIT_est", "EBITDA_P0", "NP_P0", "TotalDebt", "CashLike", "NetDebt", "implied_denom_EBIT", "implied_denom_EBITDA"]].to_string(index=False))

# ---- Part B: does implied_denom track NetDebt (debt-heavy => positive; cash-heavy => negative)? ----
# regression across full panel, only rows where EBIT_est > 0 and IntCov well-defined (isolates denominator sign question)
sub = df[mask & (df["EBIT_est"] > 0) & df["implied_denom_EBIT"].notna() & df["NetDebt"].notna()].copy()
sub = sub[sub["implied_denom_EBIT"].abs() < sub["implied_denom_EBIT"].abs().quantile(0.99)]  # trim extreme outliers (near-zero IntCov blowups)

corr = sub[["implied_denom_EBIT", "NetDebt", "TotalDebt", "CashLike"]].corr()
print("\n=== Part B: correlation of implied_denom_EBIT with NetDebt/TotalDebt/CashLike (n=%d) ===" % len(sub))
print(corr["implied_denom_EBIT"])

# sign-match rate: what fraction of rows have sign(implied_denom_EBIT) == sign(NetDebt)?
sign_match = (np.sign(sub["implied_denom_EBIT"]) == np.sign(sub["NetDebt"])).mean()
print(f"\nsign(implied_denom_EBIT) == sign(NetDebt) match rate: {sign_match*100:.1f}%  (n={len(sub)})")

# compare against naive alternative: sign match with TotalDebt alone (always positive unless debt=0) -- sanity floor
sign_match_totaldebt = (np.sign(sub["implied_denom_EBIT"]) == np.sign(sub["TotalDebt"].replace(0, np.nan))).mean()
print(f"sign(implied_denom_EBIT) == sign(TotalDebt) [gross debt, always >=0] match rate: {sign_match_totaldebt*100:.1f}%")

# ---- Part C: bucket by NetDebt sign, look at IntCov sign distribution ----
sub2 = df[df["IntCov_P0"].notna()].copy()
sub2["netdebt_bucket"] = np.where(sub2["NetDebt"] > 0, "net_debtor", np.where(sub2["NetDebt"] < 0, "net_cash_rich", "zero"))
tab = sub2.groupby("netdebt_bucket")["IntCov_P0"].apply(lambda s: (s < 0).mean() * 100)
print("\n=== Part C: pct IntCov_P0<0 by NetDebt bucket (n=%d total) ===" % len(sub2))
print(tab)
print(sub2.groupby("netdebt_bucket").size())

# ---- Part D: candidate formula fit -- try implied rate r such that denom_candidate = StDebt*r_s + LtDebt*r_l - CashLike*r_c approximates implied_denom_EBIT via OLS (no intercept) ----
from numpy.linalg import lstsq
subD = df[mask & (df["EBIT_est"] > 0) & df["implied_denom_EBIT"].notna()].copy()
subD = subD[subD["implied_denom_EBIT"].abs() < subD["implied_denom_EBIT"].abs().quantile(0.99)]
X = subD[["StDebt_P0", "LtDebt_P0", "Cash_P0", "LtInvest_P0"]].fillna(0).values
y = subD["implied_denom_EBIT"].values
coef, res, rank, sv = lstsq(X, y, rcond=None)
print("\n=== Part D: OLS implied_denom_EBIT ~ b1*StDebt + b2*LtDebt + b3*Cash + b4*LtInvest (no intercept, n=%d) ===" % len(subD))
print(dict(zip(["StDebt_P0", "LtDebt_P0", "Cash_P0", "LtInvest_P0"], coef)))
yhat = X @ coef
ss_res = ((y - yhat) ** 2).sum()
ss_tot = ((y - y.mean()) ** 2).sum()
print(f"R^2 = {1 - ss_res/ss_tot:.4f}")
