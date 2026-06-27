"""DRI Q3-2026 NP nowcast from rubber price (RSS3) + seasonality. DRI = purest VN natural-rubber play
(NP tracks revenue=vol×price; minimal KCN/liquidation noise — unlike DPR/PHR). Rubber price = Winston's
data/rubber_monthly.csv (RSS3 USD/kg). DRI quarterly NP/Revenue = BQ ticker_financial. OLS via numpy (no dep).
Tests contemporaneous vs 1-quarter-lagged price (contracts lag spot). Honest: small n (~20q), 2026Q1 outlier."""
import duckdb, numpy as np, pandas as pd
c = duckdb.connect()

# 1) quarterly RSS3 avg price from monthly
m = pd.read_csv("data/rubber_monthly.csv"); m["dt"] = pd.PeriodIndex(m["month"], freq="M")
m["q"] = m["dt"].dt.asfreq("Q")
rss3 = m.groupby("q")["price"].mean().rename("rss3")

# 2) DRI quarterly NP + Revenue from BQ
d = c.execute("""SELECT quarter, NP_P0/1e9 NP, Revenue_P0/1e9 Rev FROM read_parquet('data/bq_cache/ticker_financial.parquet')
WHERE ticker='DRI' AND NP_P0 IS NOT NULL ORDER BY time""").df()
d["q"] = d["quarter"].apply(lambda s: pd.Period(year=int(s[:4]), quarter=int(s[-1]), freq="Q"))  # "2025Q3"
d = d.set_index("q")
df = d.join(rss3, how="inner")
df["rss3_lag1"] = rss3.reindex(df.index - 1).values        # prior-quarter price (contract lag)
df["qnum"] = df.index.quarter
print(f"=== DRI vs RSS3, {len(df)} quarters ({df.index.min()}..{df.index.max()}) ===")
print(df[["NP","Rev","rss3","rss3_lag1","qnum"]].round(2).to_string())

def ols(cols, y):
    X = np.column_stack([np.ones(len(y))] + cols); beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    yhat = X @ beta; ss = 1 - ((y-yhat)**2).sum()/((y-y.mean())**2).sum(); return beta, ss

# seasonal dummies (Q2/Q3/Q4 vs Q1 base)
def seas(idx_q): return [(idx_q==2).astype(float),(idx_q==3).astype(float),(idx_q==4).astype(float)]

for ycol in ["NP","Rev"]:
    for plab, pcol in [("contemp","rss3"),("lag1","rss3_lag1")]:
        sub = df.dropna(subset=[ycol,pcol])
        y = sub[ycol].values; price = sub[pcol].values; sd = seas(sub["qnum"].values)
        beta, r2 = ols([price]+sd, y)
        print(f"\n{ycol} ~ {plab}_price + seasonal:  R2={r2:.2f}  price_beta={beta[1]:.1f} (per +1 USD/kg)")
        # Q3-2026 nowcast: contemp uses Q3 price scenarios; lag1 uses Q2-2026 actual (~2.666)
        for scen, px in (([("Q3@2.45",2.45),("Q3@2.60",2.60),("Q3@2.73",2.73)] if plab=="contemp"
                          else [("lag Q2=2.67",2.666)])):
            x = np.array([1, px, 0,1,0])  # Q3 dummy on
            print(f"     {scen}: {ycol}_Q3'26 = {x@beta:.0f}" + (" B VND" if ycol=="NP" else " B rev"))

print("\nbase: DRI Q3'25 NP=39.0B, Rev=184B. Caveats: n~20q, 2026Q1=78.4B outlier (vol/FX jump per Winston),")
print("selling price lags spot via contracts, volume +5-10% YoY (8605ha) not in price-only model.")
