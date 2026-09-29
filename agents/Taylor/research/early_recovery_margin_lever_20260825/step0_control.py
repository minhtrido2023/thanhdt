"""Step 0 — control leg: tai lap so pin R3 tu CSV DAILY (28.86 / 1.90 / -17.8 / 1.62)."""
import pandas as pd, numpy as np, sys
W = "/home/trido/thanhdt/WorkingClaude"
CSV = W + "/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_repin0803_price_univpit.csv"
df = pd.read_csv(CSV, low_memory=False)
d = df[df["record_type"] == "DAILY"].copy()
d["ymd"] = pd.to_datetime(d["ymd"])
d = d.sort_values("ymd").drop_duplicates("ymd", keep="last").set_index("ymd")
nav = d["combined_nav"].astype(float)
print("rows", len(nav), nav.index[0].date(), "->", nav.index[-1].date())
print("NAV start %.4fB  end %.4fB" % (nav.iloc[0]/1e9, nav.iloc[-1]/1e9))

def metrics(nav, label=""):
    r = nav.pct_change().dropna()
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    cagr = ((nav.iloc[-1]/nav.iloc[0]) ** (1/yrs) - 1) * 100
    sh = r.mean()/r.std()*np.sqrt(252)
    dd = (nav/nav.cummax() - 1).min() * 100
    cal = cagr / abs(dd)
    return dict(label=label, CAGR=cagr, Sharpe=sh, MaxDD=dd, Calmar=cal, finalB=nav.iloc[-1]/1e9, yrs=yrs)

m = metrics(nav, "R3 base")
print(m)
# per-year sanity + IS/OOS
for lo, hi, nm in [("2014-01-01","2019-12-31","IS"), ("2020-01-01","2026-12-31","OOS")]:
    s = nav[(nav.index>=lo)&(nav.index<=hi)]
    y = (s.index[-1]-s.index[0]).days/365.25
    print(nm, "%.2f%%" % (((s.iloc[-1]/s.iloc[0])**(1/y)-1)*100))
# gross exposure
for c in ["bal_stocks_ref","bal_etf_ref","lag_stocks_ref","lag_etf_ref","bal_cash_ref","lag_cash_ref"]:
    d[c] = pd.to_numeric(d[c], errors="coerce")
gross = (d["bal_stocks_ref"]+d["bal_etf_ref"]+d["lag_stocks_ref"]+d["lag_etf_ref"]) / nav
print("gross exposure: mean %.3f  median %.3f  p10 %.3f  p90 %.3f  max %.3f" %
      (gross.mean(), gross.median(), gross.quantile(.10), gross.quantile(.90), gross.max()))
print("state counts:", d["state"].value_counts().to_dict())
