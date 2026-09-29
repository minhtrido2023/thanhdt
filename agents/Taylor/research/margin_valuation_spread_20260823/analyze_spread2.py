# -*- coding: utf-8 -*-
"""Phase-0 part 2: breadth of the DY>=deposit opportunity set, dose-response, spread-vs-dd52 crosstab."""
import os
import numpy as np, pandas as pd

D = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/margin_valuation_spread_20260823"
m = pd.read_csv(os.path.join(D, "monthly_spread_series.csv"), parse_dates=["time"])
b = pd.read_csv(os.path.join(D, "_breadth_monthly.csv"), parse_dates=["time"])
m = m.merge(b, on="time", how="left", suffixes=("", "_b"))
m = m[m["time"] >= "2008-01-01"].reset_index(drop=True)

THR = [4, 5, 6, 7, 8, 10, 12, 15]
COLS = ["n_dy04", "n_dy05", "n_dy06", "n_dy07", "n_dy08", "n_dy10", "n_dy12", "n_dy15"]

def breadth_at(row):
    """# of universe names with DY >= deposit rate, linearly interpolated between measured thresholds."""
    d, n = row["deposit_use"], row["n_b"] if "n_b" in row else row["n"]
    if pd.isna(d) or pd.isna(n) or n == 0:
        return np.nan
    ys = [row[c] for c in COLS]
    v = np.interp(d, THR, ys)
    return 100.0 * v / n

m["breadth_dy_ge_dep_pct"] = m.apply(breadth_at, axis=1)
m.to_csv(os.path.join(D, "monthly_spread_series.csv"), index=False)

pd.set_option("display.width", 200)
print("=" * 100)
print("A2b  BREADTH — % universe with cash DY >= 12M deposit rate  (interpolated, PIT universe)")
top = m.nlargest(18, "breadth_dy_ge_dep_pct")[
    ["time", "vnindex", "dd52", "deposit_use", "dy_med_payers_pct", "breadth_dy_ge_dep_pct", "state", "fwd12m"]]
top["time"] = top["time"].dt.date
print(top.round(3).to_string(index=False))
print("\nbreadth distribution (pct of universe): " +
      " ".join("p%d=%.1f" % (q, m["breadth_dy_ge_dep_pct"].quantile(q / 100)) for q in (10, 25, 50, 75, 90, 99)))

print("\n" + "=" * 100)
print("A3b  DOSE-RESPONSE — months bucketed by spread, forward 12m return & net carry after margin")
for col, lab in [("spread2p_dypay_dep", "DY(median payer) - deposit"),
                 ("spread1_ey_dep", "EY(cap-wtd) - deposit"),
                 ("spread3m_eymed_mgn", "EY(median) - margin"),
                 ("breadth_dy_ge_dep_pct", "breadth %DY>=deposit")]:
    sub = m.dropna(subset=[col, "fwd12m"]).copy()
    sub["q"] = pd.qcut(sub[col], 5, labels=["Q1 low", "Q2", "Q3", "Q4", "Q5 high"])
    g = sub.groupby("q", observed=True).apply(lambda x: pd.Series({
        "n_mo": len(x),
        "med_" + col[:12]: x[col].median(),
        "fwd12_med%": 100 * x["fwd12m"].median(),
        "net12_med_pp": (100 * x["fwd12m"] - x["margin_rate"]).median(),
        "share_net12>0": 100 * ((100 * x["fwd12m"] - x["margin_rate"]) > 0).mean(),
        "fwd24_med%": 100 * x["fwd24m"].median(),
    }), include_groups=False)
    print("\n-- %s --" % lab)
    print(g.round(1).to_string())

print("\n" + "=" * 100)
print("A5b  SPREAD vs dd52 (the already-approved CAPIT lever gate) — does spread add anything?")
sub = m.dropna(subset=["spread2p_dypay_dep", "fwd12m", "dd52"]).copy()
print("corr(spread2p, dd52) = %.3f | corr(breadth, dd52) = %.3f" % (
    sub["spread2p_dypay_dep"].corr(sub["dd52"]),
    m.dropna(subset=["breadth_dy_ge_dep_pct", "dd52"])["breadth_dy_ge_dep_pct"].corr(m["dd52"])))
sub["deep_dd"] = sub["dd52"] <= -0.20
sub["hi_sp"] = sub["spread2p_dypay_dep"] >= 0
ct = sub.groupby(["deep_dd", "hi_sp"], observed=True).apply(lambda x: pd.Series({
    "n_mo": len(x), "fwd12_med%": 100 * x["fwd12m"].median(),
    "net12_med_pp": (100 * x["fwd12m"] - x["margin_rate"]).median(),
    "share_net12>0": 100 * ((100 * x["fwd12m"] - x["margin_rate"]) > 0).mean(),
}), include_groups=False)
print(ct.round(1).to_string())
print("\n(rows: deep_dd = VNINDEX dd52<=-20%; hi_sp = DY(median payer) >= deposit)")
