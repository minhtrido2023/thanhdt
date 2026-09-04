import pandas as pd, numpy as np, os
W = os.path.dirname(os.path.abspath(__file__))
pe_df = pd.read_csv(os.path.join(W, "universe_pe.csv"), parse_dates=["time"])
pe_df["quarter"] = pe_df.time.dt.to_period("Q")
close_df = pd.read_csv(os.path.join(W, "full_close.csv"), parse_dates=["time"])
pivot = close_df.pivot_table(index="time", columns="ticker", values="Close").sort_index()
dates = pivot.index

qdates = pe_df.groupby("quarter").time.min().sort_values().reset_index()
selections = {}
for _, row in qdates.iterrows():
    qd = row.time
    day = pe_df[pe_df.time == qd]
    day = day[(day.PE.notna()) & (day.PE > 0)]
    if len(day) < 20:
        selections[row.quarter] = []
        continue
    thresh = day.PE.quantile(0.10)
    sel = day[day.PE <= thresh].ticker.tolist()
    selections[row.quarter] = sel

qtr_series = pd.Series(dates).dt.to_period("Q").values
nav, nav_dates = [], []
current_qtr, current_weights, port_value = None, None, 1.0
weight_check = []
n_dropped_delist = 0

for i, d in enumerate(dates):
    q = qtr_series[i]
    if q != current_qtr:
        sel = [tkr for tkr in selections.get(q, []) if tkr in pivot.columns and not pd.isna(pivot.loc[d, tkr])]
        current_qtr = q
        if len(sel) == 0:
            current_weights = None
        else:
            w_each = port_value / len(sel)
            current_weights = {tkr: w_each / pivot.loc[d, tkr] for tkr in sel}
            tot_w = sum(units * pivot.loc[d, tkr] for tkr, units in current_weights.items())
            weight_check.append(abs(tot_w - port_value))
    if current_weights is not None:
        vals = []
        for tkr, units in list(current_weights.items()):
            px = pivot.loc[d, tkr]
            if pd.isna(px):
                # ticker missing today (halt/delist) -> carry last known value via units*last_valid_price
                # find last valid price up to d for this ticker (forward-fill within held period only)
                col = pivot[tkr]
                last_valid = col.loc[:d].ffill().iloc[-1]
                px = last_valid
            if not pd.isna(px):
                vals.append(units * px)
        if vals:
            port_value = sum(vals)
    nav.append(port_value)
    nav_dates.append(d)

NAV = pd.DataFrame({"time": nav_dates, "nav_quality": nav})
NAV.to_csv(os.path.join(W, "quality_basket_nav.csv"), index=False)

print(f"Rebalance quarters: {len(qdates)}, with selection: {sum(1 for v in selections.values() if v)}")
sizes = [len(v) for v in selections.values() if v]
print(f"Median basket size: {np.median(sizes):.0f}, min={min(sizes)}, max={max(sizes)}")
print(f"Self-check weight-sum error at rebalance (should be ~0): max={max(weight_check):.2e}")
print(f"NAV: start=1.0000 end={NAV.nav_quality.iloc[-1]:.4f}")
print(f"Date range: {NAV.time.min().date()} .. {NAV.time.max().date()}")
years = (NAV.time.iloc[-1] - NAV.time.iloc[0]).days / 365.25
cagr = NAV.nav_quality.iloc[-1] ** (1/years) - 1
print(f"CAGR quality basket (no cost, no rebal-cost, gross): {100*cagr:.2f}% over {years:.1f}y")
