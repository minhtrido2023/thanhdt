import pandas as pd, numpy as np, os
W = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(W, "universe_pe.csv"), parse_dates=["time"])
df = df.sort_values(["ticker","time"]).reset_index(drop=True)
df["quarter"] = df.time.dt.to_period("Q")

# rebalance dates = first trading day of each quarter present in panel
qdates = df.groupby("quarter").time.min().sort_values()
qdates = qdates.reset_index()

# Selection at each rebalance date: PIT PE (Price-based, already PIT per data_registry) > 0, top decile (lowest PE = highest ey)
# universe restricted to that day's universe_pit membership (already filtered by join)
selections = {}
for _, row in qdates.iterrows():
    qd = row.time
    day = df[df.time == qd]
    day = day[(day.PE.notna()) & (day.PE > 0)]
    if len(day) < 20:
        selections[row.quarter] = []
        continue
    thresh = day.PE.quantile(0.10)  # top decile = lowest PE (highest ey)
    sel = day[day.PE <= thresh].ticker.tolist()
    selections[row.quarter] = sel

# Build daily equal-weight NAV: within each quarter, hold the quarter's selection fixed, equal-weight,
# reweight only at quarter boundary (buy-and-hold within quarter, no intra-quarter rebalance -> weights drift, standard convention)
pivot = df.pivot_table(index="time", columns="ticker", values="Close")
pivot = pivot.sort_index()
dates = pivot.index

nav = []
nav_dates = []
current_qtr = None
current_weights = None  # dict ticker->units (shares-equivalent), rebased at each quarter start
port_value = 1.0
prev_prices = None
weight_check = []

qtr_series = pd.Series(dates).dt.to_period("Q").values

for i, d in enumerate(dates):
    q = qtr_series[i]
    if q != current_qtr:
        # rebalance: equal weight among selection, using today's close (entry price)
        sel = [tkr for tkr in selections.get(q, []) if tkr in pivot.columns and not pd.isna(pivot.loc[d, tkr])]
        current_qtr = q
        if len(sel) == 0:
            current_weights = None
        else:
            w_each = port_value / len(sel)
            current_weights = {tkr: w_each / pivot.loc[d, tkr] for tkr in sel}  # units
            # self-check: total weight = 100%
            tot_w = sum(units * pivot.loc[d, tkr] for tkr, units in current_weights.items())
            weight_check.append(abs(tot_w - port_value))
    if current_weights is not None:
        vals = []
        for tkr, units in current_weights.items():
            px = pivot.loc[d, tkr]
            if pd.isna(px):
                px = prev_prices.get(tkr, np.nan) if prev_prices else np.nan
            if not pd.isna(px):
                vals.append(units * px)
        if vals:
            port_value = sum(vals)
    nav.append(port_value)
    nav_dates.append(d)
    prev_prices = {tkr: pivot.loc[d, tkr] for tkr in pivot.columns if not pd.isna(pivot.loc[d, tkr])}

NAV = pd.DataFrame({"time": nav_dates, "nav_quality": nav})
NAV.to_csv(os.path.join(W, "quality_basket_nav.csv"), index=False)

print(f"Rebalance dates: {len(qdates)}, quarters with selection: {sum(1 for v in selections.values() if v)}")
print(f"Median basket size: {np.median([len(v) for v in selections.values() if v]):.0f}")
print(f"Self-check weight sum error (should be ~0): max={max(weight_check):.2e}, n_checks={len(weight_check)}")
print(f"NAV range: {NAV.nav_quality.min():.4f} .. {NAV.nav_quality.max():.4f}, final={NAV.nav_quality.iloc[-1]:.4f}")
print(f"Date range: {NAV.time.min().date()} .. {NAV.time.max().date()}")
