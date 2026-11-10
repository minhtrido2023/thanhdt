"""Cash dividends (corporate_action DIV, value_per_share VND/cp, exright_date) earned by LAG stock holdings in ledger TAG.
Holding is entitled if buy date < exright_date <= sell date (or still held at END). Stock/ISS events NOT added (shares handled elsewhere / out of scope; flagged).
usage: TAG END -> prints sum bn and %nav0; writes engine/lag_div_{TAG}_to{END}.csv"""
import sys, io, subprocess, json, pandas as pd, numpy as np
WC="/home/trido/thanhdt/WorkingClaude"; R=f"{WC}/mike/agents/Taylor/research/book_regime_fit_20261110"
TAG, END = sys.argv[1], sys.argv[2]; WT = TAG + "_to" + END[5:].replace("-","")
t = pd.read_csv(f"{R}/engine/{TAG}_transactions.csv", parse_dates=["ymd"]); t = t[(t.book=="LAGGED") & ~t.ticker.str.startswith("CUSTOM") & (t.ymd<=END)]
lots = []
for hid, g in t.groupby("holding_id"):
    b = g[g.buy_amount>0]; s = g[g.sell_amount>0]
    if b.empty: continue
    # holding opened before 07-01 -> start from first row date
    sh = b.shares.iloc[0] if len(b) else 0
    lots.append(dict(holding_id=hid, ticker=g.ticker.iloc[0], buy=b.ymd.min(), sell=(s.ymd.max() if len(s) else pd.Timestamp(END)), shares=g.shares.max()))
L = pd.DataFrame(lots)
tk = ",".join(f"'{x}'" for x in L.ticker.unique())
q = f"SELECT c.ticker,c.exright_date,c.value_per_share,c.event_status FROM tav2_bq.corporate_action AS c WHERE c.event_code='DIV' AND c.ticker IN ({tk}) AND c.exright_date>=DATE '2026-06-01' AND c.exright_date<=DATE '{END}' AND COALESCE(c.event_status,'')<>'not_executed'"
r = subprocess.run(["bq","query","--use_legacy_sql=false","--project_id=lithe-record-440915-m9","--format=csv","--max_rows=100000",q],capture_output=True,text=True)
if r.returncode: raise SystemExit(r.stderr[-800:])
d = pd.read_csv(io.StringIO(r.stdout), parse_dates=["exright_date"]).drop_duplicates(["ticker","exright_date","value_per_share"])
m = L.merge(d, on="ticker"); m = m[(m.buy < m.exright_date) & (m.exright_date <= m.sell)]
m["div_vnd"] = m.shares * m.value_per_share
nav0 = json.load(open(f"{R}/engine/partA_{WT}.json"))["LAG"]["nav0"]
m.to_csv(f"{R}/engine/lag_div_{WT}.csv", index=False)
print(TAG, END, "n_div_events", len(m), "sum_bn %.3f"%(m.div_vnd.sum()/1e9), "pct_nav0 %.2f%%"%(100*m.div_vnd.sum()/nav0))
print(m.sort_values("div_vnd",ascending=False)[["ticker","exright_date","value_per_share","shares","div_vnd"]].head(8).to_string())
