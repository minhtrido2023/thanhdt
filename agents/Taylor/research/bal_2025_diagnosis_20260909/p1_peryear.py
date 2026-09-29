import pandas as pd, numpy as np, json
SRC="../ccs_phase2_Taylor_20260906_153255/daily_ctrl_exp.csv"
d=pd.read_csv(SRC)
d=d[d.record_type=="DAILY"].copy()
d["ymd"]=pd.to_datetime(d["ymd"]); d=d.sort_values("ymd").set_index("ymd")
for c in ["nav_bal_ref","nav_lag_ref","combined_nav","vni_close","cap_bal","cap_lag","w_lag_tgt"]:
    d[c]=pd.to_numeric(d[c],errors="coerce")
print("R3 ctrl check: final combined %.4fB  CAGR-implied"%(d.combined_nav.iloc[-1]/1e9))

rows=[]
for y,g in d.groupby(d.index.year):
    prev=d[d.index<g.index[0]]
    def yr(col):
        s0 = prev[col].iloc[-1] if len(prev) else g[col].iloc[0]
        return g[col].iloc[-1]/s0-1
    rows.append(dict(year=y,
        bal=yr("nav_bal_ref")*100, lag=yr("nav_lag_ref")*100,
        comb=yr("combined_nav")*100, vni=yr("vni_close")*100,
        w_lag_mean=g.w_lag_tgt.mean(),
        bal_share_mean=(g.cap_bal/(g.cap_bal+g.cap_lag)).mean(),
        # contribution to combined return: sum of daily bal-capital pnl / start combined nav
        n=len(g)))
t=pd.DataFrame(rows)
# daily contribution decomposition (exact, additive on combined NAV)
d["rb"]=d.nav_bal_ref.pct_change().fillna(0); d["rl"]=d.nav_lag_ref.pct_change().fillna(0)
d["pnl_b"]=d.cap_bal.shift(1).fillna(d.cap_bal.iloc[0])*d.rb
d["pnl_l"]=d.cap_lag.shift(1).fillna(d.cap_lag.iloc[0])*d.rl
con=[]
for y,g in d.groupby(d.index.year):
    prev=d[d.index<g.index[0]]
    n0 = prev.combined_nav.iloc[-1] if len(prev) else g.combined_nav.iloc[0]
    con.append(dict(year=y, bal_contrib_pp=g.pnl_b.sum()/n0*100, lag_contrib_pp=g.pnl_l.sum()/n0*100,
                    rebal_cost_pp=-pd.to_numeric(g.rebal_cost,errors="coerce").sum()/n0*100,
                    bal_pnl_B=g.pnl_b.sum()/1e9, lag_pnl_B=g.pnl_l.sum()/1e9))
t=t.merge(pd.DataFrame(con),on="year")
pd.set_option("display.width",200)
print(t.round(2).to_string(index=False))
t.to_csv("p1_peryear_book_returns.csv",index=False)
