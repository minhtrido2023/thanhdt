#!/usr/bin/env python
"""Dung lai duong NAV NGAY cua ro CAPIT theo `universe_pit` cho MOI su kien washout.

Ly do ton tai: `events_outcome.csv` (nguyen lieu ma dispatch tro toi) la chan `ticker_prune`
(TB x = +10,45%, 70,6% duong) — KHONG phai chan headline `universe_pit` (+9,75%, 64,7%) ma
§4 guard #5 cua ke hoach BAT BUOC dung lam so chinh. `compare_pit.csv` co r_pit/x_pit nhung
THIEU `mae` va duong di ngay — bat buoc cho margin-call overlay (§1.2, §3.1).

Tai lap y nguyen co hoc cua `robust_pit.py:outcome()`:
  vao lenh T+1 sau ngay tin hieu, giu 60 phien, ro equal-weight buy-and-hold (rebalance-free),
  NAV_t = trung binh (P_t / P_entry) tren cac ten co du gia.

SELF-CHECK bat buoc: r tai lap phai khop `r_pit` trong compare_pit.csv toi 1e-9.
Khong dung BQ (p2/px_pit.parquet da phu 50/50 ten PIT). Khong dung cot profit_*.
"""
import numpy as np
import pandas as pd
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
HOLD = 60

px = pd.read_parquet(EXP / "p2" / "px_pit.parquet")
px["time"] = pd.to_datetime(px["time"])
bp = pd.read_csv(EXP / "basket_pit.csv", parse_dates=["event"])
vni = pd.read_csv(EXP / "vni.csv", parse_dates=["time"])
cmp_ = pd.read_csv(EXP / "compare_pit.csv", parse_dates=["event"])

cal = np.sort(vni["time"].unique())
W = px.pivot_table(index="time", columns="ticker", values="Close").reindex(cal).ffill()

paths, meta = {}, []
for ev, g in bp.groupby("event"):
    names = sorted(g["ticker"].unique())
    i0 = int(np.searchsorted(cal, np.datetime64(ev)))
    rec = dict(event=ev, n_req=len(names))
    if len(names) < 3:
        rec["skip"] = "ro<3"; meta.append(rec); continue
    ie, ix = i0 + 1, i0 + 1 + HOLD
    if ix >= len(cal):
        rec["skip"] = "chua du 60 phien"; meta.append(rec); continue
    sub = W.iloc[ie:ix + 1][names]
    p0 = sub.iloc[0]
    ok = p0.notna() & sub.iloc[-1].notna()
    if int(ok.sum()) < 3:
        rec["skip"] = "thieu gia"; meta.append(rec); continue
    nav = (sub.loc[:, ok] / p0[ok]).mean(axis=1)
    rec.update(skip="", n=int(ok.sum()),
               r=float(nav.iloc[-1] - 1), mae=float(nav.min() - 1),
               cal_days=float((cal[ix] - cal[ie]) / np.timedelta64(1, "D")),
               names=",".join(sorted(p0[ok].index)))
    meta.append(rec)
    paths[pd.Timestamp(ev).strftime("%Y-%m-%d")] = pd.DataFrame(
        {"event": ev, "t": np.arange(len(nav)), "time": nav.index, "nav": nav.to_numpy()})

M = pd.DataFrame(meta).sort_values("event").reset_index(drop=True)

# ---------------------------------------------------------------- SELF-CHECK
chk = M.merge(cmp_[["event", "r_pit", "n_pit"]], on="event", how="left")
sub = chk[chk["r"].notna() & chk["r_pit"].notna()]
d = (sub["r"] - sub["r_pit"]).abs()
print(f"SELF-CHECK tai lap r_pit: {len(sub)} su kien, sai so max = {d.max():.3e}")
assert d.max() < 1e-9, f"TAI LAP THAT BAI, max diff {d.max()}"
nd = (sub["n"] != sub["n_pit"]).sum()
print(f"SELF-CHECK so ten trong ro: {nd} su kien lech (ky vong 0)")
assert nd == 0

full = M[M["skip"] == ""].copy()
full = full[full["event"] >= "2014-01-01"]
print(f"\nN (2014+, ket cuc day du) = {len(full)}  [ky vong 17]")
print(f"TB r   = {full['r'].mean():+.4%}")
print(f"TB x   = {(full['r'] - (0.125*full['cal_days']/365 + 0.0015)).mean():+.4%}  [ky vong +9,75%]")
print(f"%duong (x) = {((full['r'] - (0.125*full['cal_days']/365+0.0015)) > 0).mean():.1%}  [ky vong 64,7%]")
print(f"MAE xau nhat = {full['mae'].min():+.4%}")

M.to_csv(HERE / "events_outcome_pit.csv", index=False)
pd.concat(paths.values()).to_csv(HERE / "event_paths_pit.csv", index=False)
print(f"\n-> events_outcome_pit.csv ({len(M)} dong), event_paths_pit.csv ({len(paths)} duong)")
