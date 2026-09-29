"""H5 step 1 -- build the two retail-ecology series. Rules per PREREG.md §2.1-2.2."""
import numpy as np, pandas as pd
WC="/home/trido/thanhdt/WorkingClaude"; MIKE=f"{WC}/mike"
E=pd.read_csv(f"{MIKE}/data/fiinprox_vnindex_investor_flow_daily_20260914.csv",parse_dates=["date"])
E["flags"]=E["flags"].fillna("")
G=["foreign_matched_net_bn","foreign_deal_net_bn","proprietary_net_bn",
   "local_institutional_net_bn","local_individual_net_bn"]

n0=len(E)
E=E[E["date"]>="2016-04-01"].copy()                                   # 5 groups only from 2016-04
E=E[~E["flags"].str.contains("provisional")].copy()                   # PREREG: drop provisional
# PREREG: drop the proprietary-missing stretch (a missing group breaks the denominator)
prop_gap=(E["date"]>="2022-03-03")&(E["date"]<="2022-05-16")
# PREREG: drop large block-deal days (registry trap #3: the sell side lands on `individual`)
big_deal=E["foreign_deal_net_bn"].abs()>=1000
print(f"rows {n0} -> after 2016-04 {len(E)}; prop-gap dropped {int(prop_gap.sum())}; "
      f"big-deal(|deal|>=1000bn) dropped {int(big_deal.sum())}")
print("  big-deal days:", ", ".join(str(x.date()) for x in E.loc[big_deal,'date'].head(12)))
E=E[~prop_gap & ~big_deal].copy()
E=E.dropna(subset=G).reset_index(drop=True)
print(f"  usable rows with all 5 groups: {len(E)}  {E["date"].min().date()} -> {E["date"].max().date()}")

# --- series 1: retail_net_share (daily, then monthly mean)
E["abs_sum5"]=E[G].abs().sum(axis=1)
E["retail_net_share"]=E["local_individual_net_bn"].abs()/E.abs_sum5
mon=(E.set_index("date")["retail_net_share"].resample("MS").mean().rename("retail_net_share_m")
       .to_frame())
mon["n_days"]=E.set_index("date")["retail_net_share"].resample("MS").count()
mon=mon[mon["n_days"]>=10]                                            # a month needs >=10 clean days
print(f"\nretail_net_share_m: {len(mon)} months {mon.index.min().date()} -> {mon.index.max().date()}"
      f"  mean={mon["retail_net_share_m"].mean():.3f} sd={mon["retail_net_share_m"].std():.3f}")
print(mon["retail_net_share_m"].resample("YE").mean().round(3).to_string())

# --- series 2: retail_capitulation (z-score of 20d sum of individual net)
s=E.set_index("date")["local_individual_net_bn"]
S20=s.rolling(20,min_periods=15).sum()
cap=((S20-S20.rolling(250,min_periods=180).mean())/S20.rolling(250,min_periods=180).std()).rename("retail_capitulation")
out=pd.concat([s,S20.rename("indiv_S20"),cap],axis=1)
out.to_csv("h5_retail_daily.csv")
mon.to_csv("h5_retail_monthly.csv")
print(f"\nretail_capitulation: valid from {cap.first_valid_index().date()}, "
      f"min={cap.min():.2f} on {cap.idxmin().date()}, max={cap.max():.2f} on {cap.idxmax().date()}")
