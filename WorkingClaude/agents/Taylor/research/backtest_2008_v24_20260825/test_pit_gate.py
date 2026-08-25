import sys, os
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
os.chdir("/home/trido/thanhdt/WorkingClaude")
import pandas as pd
import cpi_vn, deposit_rate_vn

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
CAPIT_LEVER_PIT_CPI_TH = 6.0
CAPIT_LEVER_PIT_DEP_TH = 9.0

cpi_df = cpi_vn.cpi_monthly_df(end="2026-12-31")[["time", "cpi_yoy"]]
dep_bf = pd.read_csv(os.path.join(WORKDIR, "mike/agents/Taylor/research/vn_cpi_sbv_2007_2010_winston.csv"))
dep_bf["time"] = pd.to_datetime(dict(year=dep_bf.year, month=dep_bf.month, day=1))
dep_bf = dep_bf[["time", "deposit_rate_approx_pct"]].rename(columns={"deposit_rate_approx_pct": "deposit_bf"})
idx = pd.DataFrame({"time": pd.date_range("2007-01-01", "2026-12-31", freq="D")})
m = pd.merge_asof(idx.sort_values("time"), cpi_df.sort_values("time"), on="time", direction="backward")
m = pd.merge_asof(m, dep_bf.sort_values("time"), on="time", direction="backward")
prod = deposit_rate_vn.merge_deposit(idx.copy())[["time", "deposit_rate"]]
m = m.merge(prod, on="time", how="left")
m["deposit_final"] = m["deposit_rate"].fillna(m["deposit_bf"])
blocked = (m["cpi_yoy"] >= CAPIT_LEVER_PIT_CPI_TH) | (m["deposit_final"] >= CAPIT_LEVER_PIT_DEP_TH)
blocked = blocked | m["cpi_yoy"].isna() | m["deposit_final"].isna()

tests = {
    "2009-12-15": True,   # inside 2009-11-26->2010-03-31 BLOCKED cluster
    "2008-09-15": True,   # inside 2007-12-13->2009-07-23 BLOCKED cluster
    "2011-08-01": True,   # inside 2011-07-12->2012-02-17 BLOCKED cluster
    "2018-08-01": False,  # inside 2018-05-28->2019-02-18 PASS cluster
    "2020-04-01": False,  # inside 2020-03-11->2020-05-08 PASS cluster
    "2022-06-01": False,  # inside 2022-05-13->2022-07-29 PASS cluster
}
s = pd.Series(blocked.values, index=m["time"].values)
ok = True
for dstr, expect_blocked in tests.items():
    dt = pd.Timestamp(dstr)
    pos = s.index.searchsorted(dt, side="right") - 1
    got_blocked = bool(s.iloc[pos])
    status = "OK" if got_blocked == expect_blocked else "MISMATCH"
    if status != "OK": ok = False
    print(f"{dstr}: blocked={got_blocked} expect={expect_blocked} [{status}]")
print("ALL OK" if ok else "FAILURES FOUND")
