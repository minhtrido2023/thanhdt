import pandas as pd, numpy as np, os, json
W = os.path.dirname(os.path.abspath(__file__))
close_df = pd.read_csv(os.path.join(W, "full_close.csv"), parse_dates=["time"])
close_df = close_df.drop_duplicates(subset=["time","ticker"])
pivot = close_df.pivot_table(index="time", columns="ticker", values="Close").sort_index()
dates = pivot.index

with open(os.path.join(W, "gf_selections.json")) as f:
    selections_raw = json.load(f)
selections = {pd.Period(k): v for k, v in selections_raw.items()}

qtr_series = pd.Series(dates).dt.to_period("Q").values
nav, nav_dates = [], []
current_qtr, current_weights, port_value = None, None, 1.0
weight_check = []

for i, d in enumerate(dates):
    q = qtr_series[i]
    if q != current_qtr:
        sel = [tkr for tkr in selections.get(q, []) if tkr in pivot.columns and not pd.isna(pivot.loc[d, tkr])]
        current_qtr = q
        if len(sel) == 0:
            current_weights = None  # stay in cash if no selection that quarter (rare, 6/75)
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
                col = pivot[tkr]
                px = col.loc[:d].ffill().iloc[-1]
            if not pd.isna(px):
                vals.append(units * px)
        if vals:
            port_value = sum(vals)
    nav.append(port_value)
    nav_dates.append(d)

NAV = pd.DataFrame({"time": nav_dates, "nav_gf": nav})
NAV.to_csv(os.path.join(W, "gf_basket_nav.csv"), index=False)
years = (NAV.time.iloc[-1] - NAV.time.iloc[0]).days / 365.25
print(f"Self-check weight-sum error: max={max(weight_check):.2e}")
print(f"NAV: start=1.0 end={NAV.nav_gf.iloc[-1]:.4f}, CAGR={100*(NAV.nav_gf.iloc[-1]**(1/years)-1):.2f}% over {years:.1f}y")
V = pd.read_csv(os.path.join(W,"mania_daily_full.csv"), parse_dates=["time"]).set_index("time").vnindex_close
V = V/V.iloc[0]
print(f"VNINDEX same window: CAGR={100*(V.iloc[-1]**(1/years)-1):.2f}%, total={100*(V.iloc[-1]-1):.1f}%")
