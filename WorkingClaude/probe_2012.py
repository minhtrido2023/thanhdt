#!/usr/bin/env python3
"""probe_2012.py — validate the 2012 buy-opportunity + compare two cheapness signals:
  (A) pb_z vs own 5Y history  vs  (B) Fed-model = market 1/PE - deposit rate (cheap vs CASH).
User recalls 2012 as a great buy; 2012 had HIGH deposit rates (~14% SBV-cap era) -> the Fed-model may
say 'not cheap' (cash yields more) exactly when pb_z says 'cheap' and the market bottoms. Tests which
signal would have fired at the 2012 bottom and the forward payoff. Uses MEDIAN PE (not mean -> penny
-stock 1/PE outliers). Usage: source ./wc_env.sh && $DNA_PYEXE probe_2012.py
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from ic_panel_8l import bq
from deposit_rate_vn import DEPOSIT_EVENTS

def main():
    # monthly: VNINDEX, median market PE (liquid), median pb_z (liquid), forward 12M VNINDEX
    q = bq("""SELECT FORMAT_DATE('%Y-%m', t.time) ym,
      CAST(ROUND(ANY_VALUE(t.VNINDEX),0) AS INT64) vni,
      ROUND(APPROX_QUANTILES(CASE WHEN t.PE>0 THEN t.PE END, 2)[OFFSET(1)],1) med_pe,
      ROUND(APPROX_QUANTILES(SAFE_DIVIDE(t.PB-t.PB_MA5Y,NULLIF(t.PB_SD5Y,0)),2)[OFFSET(1)],2) med_pbz
    FROM tav2_bq.ticker_prune AS t
    WHERE t.Trading_Value_1M_P50>3e9 AND t.time BETWEEN DATE '2011-01-01' AND DATE '2014-12-31'
    GROUP BY ym ORDER BY ym""")
    q["m"] = pd.PeriodIndex(q["ym"], freq="M")
    q = q.set_index("m")
    # VNINDEX forward 12M return (from the monthly vni)
    vni = q["vni"].astype(float)
    q["fwd12M"] = (vni.shift(-12) / vni - 1.0 * 1).round(2)
    q["fwd12M"] = (vni.shift(-12) / vni - 1.0)
    # deposit step series -> monthly
    dep = pd.Series({pd.Period(pd.Timestamp(d), freq="M"): v for d, v in DEPOSIT_EVENTS}).sort_index()
    q["deposit"] = dep.reindex(dep.index.union(q.index)).ffill().reindex(q.index)
    q["mkt_eyield"] = (100.0 / q["med_pe"]).round(1)               # market earnings yield %
    q["fed_spread"] = (q["mkt_eyield"] - q["deposit"]).round(1)    # 1/PE - deposit (cheap-vs-cash)
    q["pbz_cheap"] = q["med_pbz"] <= -0.3                          # cheap vs own history
    q["fed_cheap"] = q["fed_spread"] >= 0                          # earnings yield beats cash

    print("MONTHLY 2011-2014 — two cheapness signals at the 2012 bottom:\n")
    print(f"{'month':8} {'VNI':>5} {'medPE':>6} {'eyld%':>6} {'depo%':>6} {'fedSpr':>7} {'pb_z':>6} "
          f"{'pbz_cheap':>9} {'fed_cheap':>9} {'fwd12M':>7}")
    for m, r in q.iterrows():
        f12 = f"{r.fwd12M*100:+.0f}%" if pd.notna(r.fwd12M) else "  -"
        print(f"{str(m):8} {int(r.vni):>5} {r.med_pe:>6.1f} {r.mkt_eyield:>6.1f} {r.deposit:>6.1f} "
              f"{r.fed_spread:>+7.1f} {r.med_pbz:>6.2f} {str(bool(r.pbz_cheap)):>9} {str(bool(r.fed_cheap)):>9} {f12:>7}")

    # verdict at the 2012 bottom window
    btm = q.loc[[m for m in q.index if str(m) in ("2011-12","2012-01","2012-05","2012-11")]]
    print("\nVERDICT at 2012-era lows (fwd-12M = the payoff you'd have captured):")
    for m, r in btm.iterrows():
        print(f"  {m}: pb_z {r.med_pbz:+.2f} ({'CHEAP' if r.pbz_cheap else 'not'}) | "
              f"fed_spread {r.fed_spread:+.1f}pp ({'cheap-vs-cash' if r.fed_cheap else 'CASH WINS -> fed says AVOID'}) | "
              f"fwd12M {r.fwd12M*100:+.0f}%")

if __name__ == "__main__":
    main()
