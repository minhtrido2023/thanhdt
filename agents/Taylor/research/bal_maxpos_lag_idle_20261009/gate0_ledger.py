"""Gate-0 part A (ledger-only, no engine): from the pinned p0_off ledger, reconstruct BAL open-position
count per session, LAG buy flag, BAL cash share — by DT5G state. Answers: how often is BAL AT the 12-slot cap?"""
import pandas as pd, numpy as np, sys
F = "/home/trido/thanhdt/WorkingClaude/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_park3-0_wtnamecap_advprice_etfcreatpit_exp_p0_off_univpit.csv"
df = pd.read_csv(F, low_memory=False)
d = df[df.record_type == "DAILY"].copy(); d["ymd"] = pd.to_datetime(d.ymd)
for c in ["state","nav_bal_ref","bal_cash_ref","bal_stocks_ref","lag_cash_ref","nav_lag_ref","cap_bal","cap_lag"]:
    d[c] = pd.to_numeric(d[c], errors="coerce")
tx = df[df.record_type == "TX"].copy(); tx["ymd"] = pd.to_datetime(tx.ymd)
tx["shares"] = pd.to_numeric(tx.shares, errors="coerce")
print("TX books/actions:", tx.groupby(["book","action"]).size().to_dict())
# BAL open positions: track holding_id net shares through each day (end-of-day)
bal = tx[tx.book == "BAL"].copy()
bal["sg"] = bal.shares.where(bal.action == "buy", -bal.shares)
# holding open on day D (EOD) iff cum net shares through D > 0; count distinct tickers
pos = bal.groupby(["holding_id","ymd"]).sg.sum().groupby(level=0).cumsum().reset_index()
cnt = {}
days = d.ymd.sort_values().values
for h, g in pos.groupby("holding_id"):
    g = g.sort_values("ymd"); t = h.rsplit("_", 2)[0]
    for i in range(len(g)):
        a = g.ymd.iloc[i]; b = g.ymd.iloc[i+1] if i+1 < len(g) else pd.Timestamp("2100-01-01")
        if g.sg.iloc[i] > 1e-6:
            for dd in days[(days >= a) & (days < b)]: cnt.setdefault(dd, set()).add(t)
cnt = {k: len(v) for k, v in cnt.items()}
print("TX dates not in DAILY:", len(set(tx.ymd) - set(d.ymd)))
d["bal_npos"] = d.ymd.map(cnt).fillna(0).astype(int)
lagbuy = set(tx[(tx.book == "LAG") & (tx.action == "buy")].ymd)
d["lag_idle"] = ~d.ymd.isin(lagbuy)
d["bal_cash_pct"] = d.bal_cash_ref / d.nav_bal_ref
d["lag_cash_pct"] = d.lag_cash_ref / d.nav_lag_ref
d["lag_cash_comb"] = d.lag_cash_pct * d.cap_lag / (d.cap_bal + d.cap_lag)
d["bal_cash_comb"] = d.bal_cash_pct * d.cap_bal / (d.cap_bal + d.cap_lag)
d["at_cap"] = d.bal_npos >= 12
names = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EXBULL"}
g = d.groupby("state").agg(N=("ymd","size"), lag_idle=("lag_idle","mean"), npos_mean=("bal_npos","mean"),
    npos_p90=("bal_npos", lambda s: s.quantile(.9)), npos_max=("bal_npos","max"), at_cap=("at_cap","mean"),
    bal_cash=("bal_cash_pct","mean"), lag_cash=("lag_cash_pct","mean"), lag_cash_comb=("lag_cash_comb","mean"))
g.index = [names[int(i)] for i in g.index]; print(g.round(3).to_string())
idle = d[d.lag_idle]
g2 = idle.groupby("state").agg(N_idle=("ymd","size"), at_cap=("at_cap","mean"), npos_mean=("bal_npos","mean"),
    bal_cash=("bal_cash_pct","mean"), bal_cash_comb=("bal_cash_comb","mean"), lag_cash_comb=("lag_cash_comb","mean"))
g2.index = [names[int(i)] for i in g2.index]; print("\nLAG-idle sessions only:\n", g2.round(3).to_string())
print("\nBAL npos distribution (all):", d.bal_npos.value_counts().sort_index().to_dict())
d[["ymd","state","bal_npos","lag_idle","bal_cash_pct","lag_cash_pct","lag_cash_comb","bal_cash_comb"]].to_csv("gate0_daily.csv", index=False)
