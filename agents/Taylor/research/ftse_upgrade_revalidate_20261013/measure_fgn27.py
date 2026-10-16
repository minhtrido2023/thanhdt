"""Foreign flow restricted to the 27 FTSE All-Cap names (VNDirect finfo per-stock; incl. put-through). Same placebo design as measure.py."""
import json, glob, numpy as np, pandas as pd, db_dtypes  # noqa
rows = []
for f in glob.glob("fgn_stock/*.json"):
    try: rows += json.load(open(f))["data"]
    except Exception as ex: print("BAD", f, ex)
D = pd.DataFrame(rows).drop_duplicates(["code", "tradingDate"]); D["tradingDate"] = pd.to_datetime(D["tradingDate"])
print("names", D.code.nunique(), "rows", len(D), D.tradingDate.min().date(), D.tradingDate.max().date())
P = pd.read_parquet("panel_pit.parquet", columns=["time", "ticker", "turn"]); P["time"] = pd.to_datetime(P["time"])
days = np.array(sorted(P.time.unique())); e = int(np.searchsorted(days, np.datetime64("2026-09-21"))); NPOST = len(days) - e; NPRE = 60
names = sorted(D.code.unique())
T27 = P[P.ticker.isin(names)].groupby("time").turn.sum().reindex(days)
g = D.groupby("tradingDate").agg(buy=("buyVal", "sum"), sell=("sellVal", "sum"), net=("netVal", "sum")).reindex(days)
share = (g.buy + g.sell) / 2 / T27; net = g.net / 1e9
MK = pd.read_parquet("mkt_turn.parquet"); MK["time"] = pd.to_datetime(MK["time"]); 
FA = pd.read_csv("foreign_vnindex_vndirect.csv", parse_dates=["tradingDate"]).set_index("tradingDate").reindex(days)
conc = (g.buy + g.sell) / (FA.buyVal + FA.sellVal)          # share of ALL foreign trading that is in the 27 names
def st(i):
    pre, post = slice(i - NPRE, i), slice(i, i + NPOST)
    return {k: (float(s.iloc[pre].median()), float(s.iloc[post].median()), float(s.iloc[post].median() - s.iloc[pre].median()))
            for k, s in [("fgn_share_of_ftse27_turnover", share), ("fgn_net_ftse27_bn_day", net), ("ftse27_share_of_all_foreign_trading", conc)]}
act = st(e); s0 = int(np.searchsorted(days, np.datetime64("2019-01-02")))
plc = [st(i) for i in range(e - NPOST, s0 + NPRE, -NPOST)]
seas = [st(int(np.searchsorted(days, np.datetime64(f"{y}-09-21")))) for y in range(2019, 2026)]
for k, (a, b, d) in act.items():
    pv = np.array([p[k][2] for p in plc]); pv = pv[~np.isnan(pv)]; sv = np.array([s[k][2] for s in seas])
    print(f"{k:38s} pre {a:10.4f} post {b:10.4f} chg {d:+10.4f} | placebo N={len(pv)} p5 {np.percentile(pv,5):+.4f} p50 {np.percentile(pv,50):+.4f} p95 {np.percentile(pv,95):+.4f} pctile {(pv<d).mean()*100:.1f} | seasonal N={len(sv)} min {sv.min():+.4f} med {np.median(sv):+.4f} max {sv.max():+.4f}")
print("cum foreign net FTSE27 post (bn):", round(net.iloc[e:].sum()), "| pre60:", round(net.iloc[e-60:e].sum()), "| all-market post:", round(FA.netVal.iloc[e:].sum()/1e9), "pre60:", round(FA.netVal.iloc[e-60:e].sum()/1e9))
six = D[D.code.isin("VCB VIC VHM BID HPG VPB".split())].groupby("tradingDate").netVal.sum().reindex(days) / 1e9
print("All-World 6: net bn/day median pre", round(six.iloc[e-60:e].median()), "post", round(six.iloc[e:].median()), "| cum post", round(six.iloc[e:].sum()))
print(D[D.tradingDate >= "2026-09-21"].groupby("code").netVal.sum().div(1e9).round(0).sort_values().to_string())
