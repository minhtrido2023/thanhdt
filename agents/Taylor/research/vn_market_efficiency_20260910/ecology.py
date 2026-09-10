"""BUOC 2 — VN ecology proxies. Reports ONLY what real data exists; no invented numbers.

Series actually built here:
  E1 net foreign flow (VNINDEX, HOSE) — VNDirect finfo, registry CANDIDATE-FEASIBLE, 2018-08-30+
  E2 foreign gross PARTICIPATION share — E1 numerator / universe_pit turnover denominator
     (caveat stated in the report: numerator HOSE-only, denominator all floors -> level biased
      DOWN, trend still readable)
  E3 turnover velocity — universe_pit monthly turnover, deflated to constant VND (7%/yr,
     the Inflation_7 convention used across this codebase)
  E4 breadth — count of universe_pit members (already in efficiency_monthly.csv)
NOT available anywhere (BQ tav2_bq/tav2_mike, local data/, registry): market-wide margin debt,
retail-vs-institution trading share as a SERIES, new brokerage accounts as a SERIES.
"""
import os
import numpy as np
import pandas as pd

D = os.path.dirname(os.path.abspath(__file__))

# E1 foreign flow
f = pd.read_csv(os.path.join(D, "foreign_flow_vnindex_raw.csv"), parse_dates=["tradingDate"])
f["ym"] = f.tradingDate.values.astype("datetime64[M]")
fm = f.groupby("ym").agg(net_foreign_vnd=("netVal", "sum"),
                         gross_foreign_vnd=("buyVal", "sum"),
                         sess=("netVal", "count")).reset_index()
fm["gross_foreign_vnd"] += f.groupby("ym")["sellVal"].sum().to_numpy()

# E3/E2 denominator: universe turnover
p = pd.read_csv(os.path.join(D, "monthly_panel.csv"), parse_dates=["ym"])
turn = p.groupby("ym").apply(
    lambda g: (g.adv_vnd * g.ndays).sum(), include_groups=False).rename("turnover_vnd").reset_index()
turn["n_names"] = p.groupby("ym")["ticker"].count().to_numpy()

e = turn.merge(fm, on="ym", how="left")
# deflate to constant 2026 VND at 7%/yr (Inflation_7 convention, CLAUDE.md)
yrs = (pd.Timestamp("2026-09-01") - e.ym).dt.days / 365.25
e["turnover_real_vnd"] = e.turnover_vnd * (1.07 ** yrs)
e["foreign_share"] = e.gross_foreign_vnd / e.turnover_vnd
e["net_foreign_pct_turnover"] = e.net_foreign_vnd / e.turnover_vnd
e.to_csv(os.path.join(D, "ecology_monthly.csv"), index=False)

e["year"] = e.ym.dt.year
g = e[e.year >= 2010].groupby("year").agg(
    turnover_real_tyVND=("turnover_real_vnd", lambda s: s.mean() / 1e9),
    n_names=("n_names", "mean"),
    net_foreign_tyVND_yr=("net_foreign_vnd", lambda s: s.sum() / 1e9),
    foreign_share=("foreign_share", "mean"),
    months_fx=("net_foreign_vnd", "count")).round(4)
print("=== Ecology proxies by year (turnover in ty VND/month, constant-2026 VND) ===")
print(g.to_string())

print("\n=== E1 net foreign flow, annual (ty VND) — REAL DATA, VNDirect finfo, 2018-08-30+ ===")
fy = f.copy(); fy["year"] = fy.tradingDate.dt.year
print((fy.groupby("year")["netVal"].sum() / 1e9).round(0).to_string())
print(f"coverage: {f.tradingDate.min().date()} -> {f.tradingDate.max().date()}, {len(f)} sessions")

print("\n=== NOT AVAILABLE (checked, not assumed) ===")
for k in ["margin debt toàn thị trường / vốn hoá",
          "tỷ trọng giao dịch NĐT cá nhân vs tổ chức (CHUỖI theo tháng/năm)",
          "số tài khoản mở mới VSD (CHUỖI)"]:
    print(f"  - {k}: KHÔNG có trong tav2_bq, tav2_mike, data/, hay data_registry (dạng chuỗi)")
