# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pandas as pd, numpy as np
from simulate_holistic_nav import bq, VNI_QUERY

logs = pd.read_csv("data/v11_transparent_logs.csv")
logs["ymd"] = pd.to_datetime(logs["ymd"])

nav = logs["nav"]
peak = nav.cummax()
dd = (nav - peak) / peak * 100
max_dd_idx = int(dd.idxmin())
n_yrs = (logs["ymd"].iloc[-1] - logs["ymd"].iloc[0]).days / 365.25

rets = nav.pct_change().dropna()
spy = len(rets) / n_yrs
sharpe = rets.mean() / rets.std() * np.sqrt(spy) if rets.std() > 0 else 0
ds = rets[rets < 0]
sortino = rets.mean() / ds.std() * np.sqrt(spy) if len(ds) and ds.std() > 0 else 0
cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1 / n_yrs) - 1
calmar = cagr / abs(dd.min() / 100) if dd.min() < 0 else 0

print("=" * 75)
print("  V11 SIMULATION REPORT  —  2022-01-04 → 2026-05-15 (4.36 years), 50B init")
print("=" * 75)
print(f"  Final NAV:        {nav.iloc[-1]/1e9:>7.2f}B")
print(f"  Total return:     {(nav.iloc[-1]/nav.iloc[0]-1)*100:>+7.2f}%")
print(f"  CAGR:             {cagr*100:>+7.2f}%")
print(f"  Sharpe:           {sharpe:>7.2f}")
print(f"  Sortino:          {sortino:>7.2f}")
print(f"  MaxDD:            {dd.min():>+7.2f}%   (on {logs.loc[max_dd_idx, 'ymd'].date()})")
print(f"  Calmar:           {calmar:>7.2f}")
print(f"  Sessions/yr:      {spy:>7.1f}")

print()
print("YEAR-BY-YEAR:")
logs["year"] = logs["ymd"].dt.year
yr = logs.groupby("year").agg(start=("nav", "first"), end=("nav", "last"))
yr["return_pct"] = (yr["end"] / yr["start"] - 1) * 100
for y, r in yr.iterrows():
    print(f"  {int(y)}: {r['start']/1e9:>6.2f}B → {r['end']/1e9:>6.2f}B  ({r['return_pct']:>+6.2f}%)")

print()
print("VNINDEX BASELINE (same window):")
vni = bq(VNI_QUERY.format(start="2022-01-01", end="2026-05-18"))
vni["time"] = pd.to_datetime(vni["time"])
vc = vni["Close"]
vni_cagr = ((vc.iloc[-1] / vc.iloc[0]) ** (1 / n_yrs) - 1) * 100
vni_dd = ((vc - vc.cummax()) / vc.cummax() * 100).min()
vni_rets = vc.pct_change().dropna()
vni_sharpe = vni_rets.mean() / vni_rets.std() * np.sqrt(spy) if vni_rets.std() > 0 else 0
print(f"  CAGR: {vni_cagr:>+7.2f}%")
print(f"  Sharpe: {vni_sharpe:>7.2f}")
print(f"  MaxDD: {vni_dd:>+7.2f}%")

print()
print(f"ALPHA: CAGR {(cagr*100 - vni_cagr):>+.2f}pp, Sharpe {(sharpe - vni_sharpe):>+.2f}, "
      f"DD {(vni_dd - dd.min()):>+.2f}pp better")

print()
print("TRANSACTION SUMMARY:")
tx = pd.read_csv("data/v11_transparent_transactions.csv")
tx["ymd"] = pd.to_datetime(tx["ymd"])
real = tx[tx["reason"] != "MTM_UNREALIZED"]
stk = real[real["ticker"] != "E1VFVN30"]
print(f"  Stock buys: {(stk['action']=='buy').sum()}  Stock sells: {(stk['action']=='sell').sum()}")
print(f"  Unique tickers: {stk['ticker'].nunique()}")
re_bk = real[real["play_type"] == "RE_BACKLOG_BUY"]
print(f"  RE_BACKLOG_BUY trades: {(re_bk['action']=='buy').sum()} buys / "
      f"{(re_bk['action']=='sell').sum()} sells across "
      f"{re_bk['ticker'].nunique()} tickers")
abnd = real[real["reason"] == "ABANDONED_REFUND"]
print(f"  ABANDONED_REFUND events: {len(abnd)} (across {abnd['ticker'].nunique()} tickers)")

# Top winners/losers — use FULL transactions (includes MTM_UNREALIZED phantoms)
# so partial-FIFO lots reconcile (real-sells + MTM = total proceeds at cost basis).
print()
print("TOP WINNERS (P&L incl. MTM for open):")
closed = []
for hid, grp in tx.groupby("holding_id"):
    bs = grp[grp["action"] == "buy"]
    ss_all = grp[grp["action"] == "sell"]  # includes MTM
    if bs.empty or ss_all.empty:
        continue
    cost = bs["buy_amount"].sum() + bs["fee"].sum()
    proceeds = ss_all["sell_amount"].sum() - ss_all["fee"].sum()
    pnl = proceeds - cost
    has_mtm = (ss_all["reason"] == "MTM_UNREALIZED").any()
    real_ss = ss_all[ss_all["reason"] != "MTM_UNREALIZED"]
    last_reason = (real_ss["reason"].iloc[-1] if not real_ss.empty
                   else ss_all["reason"].iloc[-1])
    if cost > 0:
        closed.append({"ticker": grp["ticker"].iloc[0], "hid": hid,
                       "entry": bs["ymd"].min().date(),
                       "exit": ss_all["ymd"].max().date(),
                       "cost": cost, "pnl": pnl,
                       "pnl_pct": (proceeds/cost-1)*100,
                       "reason": last_reason + ("+MTM" if has_mtm else ""),
                       "book": grp["book"].iloc[0] if "book" in grp.columns else "?"})
cdf = pd.DataFrame(closed).sort_values("pnl", ascending=False)
for _, r in cdf.head(10).iterrows():
    print(f"  {r['ticker']:<6} {r['book']:<5} {r['entry']} → {r['exit']}  "
          f"cost {r['cost']/1e6:>7.1f}M  pnl {r['pnl']/1e6:>+8.1f}M  ({r['pnl_pct']:>+6.2f}%)  [{r['reason']}]")

print()
print("TOP LOSERS (realized P&L):")
for _, r in cdf.tail(10).iloc[::-1].iterrows():
    print(f"  {r['ticker']:<6} {r['book']:<5} {r['entry']} → {r['exit']}  "
          f"cost {r['cost']/1e6:>7.1f}M  pnl {r['pnl']/1e6:>+8.1f}M  ({r['pnl_pct']:>+6.2f}%)  [{r['reason']}]")
