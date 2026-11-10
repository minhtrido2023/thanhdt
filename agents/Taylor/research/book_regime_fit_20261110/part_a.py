"""Part A — per-book papertrade decomposition (pt_v22_dt5g), go-live 2026-07-01 -> last log row.
P&L identity per book per day:  dNAV = PnL_stock + PnL_etf - fees   (cash earns 0 in papertrade)
  PnL_stock(d) = stocks(d) - stocks(d-1) - buys_stk(d) + sells_stk(d)      (non-MTM TX only)
  PnL_etf(d)   = etf(d)    - etf(d-1)    - buys_etf(d) + sells_etf(d)
Self-check: residual dNAV - (PnL_stock + PnL_etf - fees) must be ~0 VND.
"""
import sys, json
import numpy as np, pandas as pd
WC = "/home/trido/thanhdt/WorkingClaude"
OUT = f"{WC}/mike/agents/Taylor/research/book_regime_fit_20261110"
START = sys.argv[1] if len(sys.argv) > 1 else "2026-07-01"

logs = pd.read_csv(f"{WC}/data/pt_v22_dt5g_logs.csv", parse_dates=["ymd"]).set_index("ymd")
tx = pd.read_csv(f"{WC}/data/pt_v22_dt5g_transactions.csv", parse_dates=["ymd"])
tx = tx[~tx["reason"].astype(str).str.startswith("MTM")]
tx["kind"] = np.where(tx["ticker"].str.startswith("CUSTOM"), "etf", "stk")
vni = pd.read_csv(f"{OUT}/data/vnindex.csv", parse_dates=["time"]).set_index("time")["Close"]

_d = logs["BAL_etf"]; _t = tx[(tx.book=="BAL")&(tx.kind=="etf")].groupby("ymd").agg(b=("buy_amount","sum"), s=("sell_amount","sum"))
_t = _t.reindex(logs.index).fillna(0)
basket_r = (_d.diff() - _t.b + _t.s) / (_d.shift(1) + _t.b)
books = {"BAL": ("BAL", "BAL"), "LAG": ("SECOND", "LAGGED")}
res, monthly_all = {}, []
for b, (pfx, tb) in books.items():
    d = pd.DataFrame({"cash": logs[f"{pfx}_cash"], "stk": logs[f"{pfx}_stocks"], "etf": logs[f"{pfx}_etf"]})
    d["nav"] = d.sum(axis=1)
    t = tx[tx["book"] == tb]
    g = t.groupby(["ymd", "kind"]).agg(buy=("buy_amount", "sum"), sell=("sell_amount", "sum"), fee=("fee", "sum")).unstack("kind").fillna(0)
    g.columns = [f"{a}_{k}" for a, k in g.columns]
    d = d.join(g, how="left").fillna(0)
    for c in ["buy_stk", "sell_stk", "fee_stk", "buy_etf", "sell_etf", "fee_etf"]:
        if c not in d: d[c] = 0.0
    d["pnl_stk"] = d["stk"].diff() - d["buy_stk"] + d["sell_stk"]
    d["pnl_etf"] = d["etf"].diff() - d["buy_etf"] + d["sell_etf"]
    d["fees"] = d["fee_stk"] + d["fee_etf"]
    d["resid"] = d["nav"].diff() - (d["pnl_stk"] + d["pnl_etf"] - d["fees"])
    d["vni"] = vni.reindex(d.index)
    d["vni_r"] = d["vni"].pct_change()
    w = d.loc[START:].copy()
    w0 = d.index[d.index.get_loc(w.index[0]) - 1]          # base = close of session before START
    nav0 = d.loc[w0, "nav"]
    # sleeve returns (stock sleeve: denominator = prev mv + same-day buys)
    stk_den = d["stk"].shift(1) + d["buy_stk"]
    d["r_stk"] = np.where(stk_den > 1e6, d["pnl_stk"] / stk_den, np.nan)
    etf_den = d["etf"].shift(1) + d["buy_etf"]
    d["r_etf"] = np.where(etf_den > 1e6, d["pnl_etf"] / etf_den, np.nan)
    d["r_nav"] = d["nav"].pct_change()
    w = d.loc[START:]
    navs = pd.concat([pd.Series([nav0], index=[w0]), w["nav"]])
    dd = (navs / navs.cummax() - 1).min()
    vni_ret = w["vni"].iloc[-1] / d.loc[w0, "vni"] - 1
    # beta of book & of stock sleeve vs VNINDEX (daily)
    def beta_alpha(r):
        x = pd.concat([r, w["vni_r"]], axis=1).dropna()
        if len(x) < 10: return np.nan, np.nan, len(x)
        bta = np.cov(x.iloc[:, 0], x.iloc[:, 1])[0, 1] / x.iloc[:, 1].var()
        a = (x.iloc[:, 0] - bta * x.iloc[:, 1]).mean() * len(x)   # cumulative arithmetic alpha over active days
        return bta, a, len(x)
    b_nav, a_nav, _ = beta_alpha(w["r_nav"])
    b_stk, a_stk, n_stk = beta_alpha(w["r_stk"])
    # stock sleeve vs VNI on the SAME active days (geometric)
    act = w["r_stk"].dropna()
    stk_geo = (1 + act).prod() - 1
    vni_same = (1 + w.loc[act.index, "vni_r"]).prod() - 1
    etf_act = w["r_etf"].dropna()
    etf_geo = (1 + etf_act).prod() - 1
    vni_same_etf = (1 + w.loc[etf_act.index, "vni_r"]).prod() - 1
    avg_expo = {k: float((w[k] / w["nav"]).mean()) for k in ["stk", "etf", "cash"]}
    r = dict(book=b, start_base=str(w0.date()), end=str(w.index[-1].date()), n_sessions=len(w),
             nav0=nav0, nav_end=float(w["nav"].iloc[-1]), ret=float(w["nav"].iloc[-1] / nav0 - 1),
             maxdd=float(dd), vol_ann=float(w["r_nav"].std() * np.sqrt(252)), vni_ret=float(vni_ret),
             pnl_stk=float(w["pnl_stk"].sum()), pnl_etf=float(w["pnl_etf"].sum()), fees=float(w["fees"].sum()),
             pnl_stk_pct=float(w["pnl_stk"].sum() / nav0), pnl_etf_pct=float(w["pnl_etf"].sum() / nav0), fees_pct=float(w["fees"].sum() / nav0),
             selfcheck_max_abs_resid_vnd=float(w["resid"].abs().max()),
             avg_expo=avg_expo, beta_nav=float(b_nav), alpha_nav_cum_arith=float(a_nav),
             stock_sleeve=dict(active_days=int(n_stk), geo_ret=float(stk_geo), vni_same_days=float(vni_same), excess=float(stk_geo - vni_same), beta=float(b_stk), alpha_cum_arith=float(a_stk)),
             etf_sleeve=dict(active_days=len(etf_act), geo_ret=float(etf_geo), vni_same_days=float(vni_same_etf), excess=float(etf_geo - vni_same_etf)))
    # dollar attribution (beta=1 benchmark, same-day dollar exposure); basket daily return = BAL etf sleeve r_etf
    bask = basket_r.reindex(w.index)
    r["attr_pct_nav"] = dict(
        vni_beta_on_invested=float(((w["stk"].shift(1).fillna(0) + w["buy_stk"]) * w["vni_r"]).sum() / nav0 + ((w["etf"].shift(1).fillna(0) + w["buy_etf"]) * w["vni_r"]).sum() / nav0),
        selection_vs_vni=float((w["pnl_stk"] - (w["stk"].shift(1).fillna(0) + w["buy_stk"]) * w["vni_r"]).sum() / nav0),
        selection_vs_basket=float((w["pnl_stk"] - (w["stk"].shift(1).fillna(0) + w["buy_stk"]) * bask).sum() / nav0),
        park_vehicle_vs_vni=float((w["pnl_etf"] - (w["etf"].shift(1).fillna(0) + w["buy_etf"]) * w["vni_r"]).sum() / nav0),
        fees=float(-w["fees"].sum() / nav0), resid_identity=float(w["resid"].sum() / nav0))
    stk_cap = (w["stk"].shift(1).fillna(0) + w["buy_stk"])
    r["stock_sleeve"]["dietz_ret"] = float(w["pnl_stk"].sum() / stk_cap[stk_cap > 1e6].mean())
    r["stock_sleeve"]["vni_dollar_matched"] = float((stk_cap * w["vni_r"]).sum() / stk_cap[stk_cap > 1e6].mean())
    r["stock_sleeve"]["basket_dollar_matched"] = float((stk_cap * bask).sum() / stk_cap[stk_cap > 1e6].mean())
    # beta-explained part of book: beta_nav * vni_ret
    r["beta_part"] = float(b_nav * vni_ret)
    res[b] = r
    m = w.copy(); m["mon"] = m.index.to_period("M")
    navm = pd.concat([pd.Series([nav0], index=[w0]), w["nav"]])
    for mon, grp in m.groupby("mon"):
        prev = navs[navs.index < grp.index[0]].iloc[-1]
        vprev = d["vni"][d.index < grp.index[0]].iloc[-1]
        monthly_all.append(dict(book=b, month=str(mon), ret=grp["nav"].iloc[-1] / prev - 1, vni=grp["vni"].iloc[-1] / vprev - 1,
                                pnl_stk_pct=grp["pnl_stk"].sum() / prev, pnl_etf_pct=grp["pnl_etf"].sum() / prev, fees_pct=grp["fees"].sum() / prev,
                                expo_stk=(grp["stk"] / grp["nav"]).mean(), expo_etf=(grp["etf"] / grp["nav"]).mean()))
    d.to_csv(f"{OUT}/part_a_daily_{b}.csv")

# combined (50/50 static papertrade)
tot0 = res["BAL"]["nav0"] + res["LAG"]["nav0"]; tot1 = res["BAL"]["nav_end"] + res["LAG"]["nav_end"]
res["COMBINED"] = dict(ret=tot1 / tot0 - 1)
mon = pd.DataFrame(monthly_all); mon.to_csv(f"{OUT}/part_a_monthly.csv", index=False)
json.dump(res, open(f"{OUT}/part_a_{START}.json", "w"), indent=1, default=float)
print("ATTR", json.dumps({b: res[b]["attr_pct_nav"] | {"ret": res[b]["ret"], "sleeve": res[b]["stock_sleeve"]} for b in ["BAL","LAG"]}, indent=1, default=lambda x: round(float(x),4)))
if False: print(json.dumps(res, indent=1, default=lambda x: round(float(x), 5)))
print(mon.round(4).to_string())
