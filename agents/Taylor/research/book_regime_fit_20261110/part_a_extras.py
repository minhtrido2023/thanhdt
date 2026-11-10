"""Per-play_type and per-holding P&L (realized + MTM) for holdings alive after 2026-07-01. usage: TAG END
Regenerates part_a_by_playtype.txt / part_a_lag_holdings.txt (the originals were produced ad hoc; this is the saved script)."""
import sys, json, pandas as pd, numpy as np
WC="/home/trido/thanhdt/WorkingClaude"; R=f"{WC}/mike/agents/Taylor/research/book_regime_fit_20261110"
TAG, END = sys.argv[1], sys.argv[2]; WT = TAG + "_to" + END[5:].replace("-","")
tx = pd.read_csv(f"{R}/engine/{TAG}_transactions.csv", parse_dates=["ymd"]); tx = tx[(tx.ymd <= END) & ~tx.ticker.str.startswith("CUSTOM")]
pa = json.load(open(f"{R}/engine/partA_{WT}.json"))
alive = tx[tx.ymd >= "2026-07-01"].holding_id.unique()
t = tx[tx.holding_id.isin(alive)]
g = t.groupby(["book","holding_id"]).agg(ticker=("ticker","first"), pt=("play_type","first"), first=("ymd","min"), last=("ymd","max"),
        buy=("buy_amount","sum"), sell=("sell_amount","sum"), fee=("fee","sum")).reset_index()
g["pnl"] = g.sell - g.buy - g.fee; g["ret"] = g.pnl / g.buy.replace(0, np.nan)
lines = []
s = g.groupby(["book","pt"]).agg(n=("pnl","size"), win=("pnl", lambda x: (x>0).mean()), buy_bn=("buy","sum"), pnl_bn=("pnl","sum"))
s["buy_bn"] /= 1e9; s["pnl_bn"] /= 1e9
s["pnl_pct_navbook"] = [s.loc[i,"pnl_bn"]*1e9 / pa["BAL" if i[0]=="BAL" else "LAG"]["nav0"] for i in s.index]
lines.append(s.round(3).to_string())
lines.append("note: realized+MTM (sell rows incl. MTM_UNREALIZED) for holdings alive after 2026-07-01; includes P&L before 07-01 for holdings opened earlier")
open(f"{R}/engine/by_playtype_{WT}.txt","w").write("\n".join(lines))
L = g[g.book=="LAGGED"].sort_values("pnl")
h = [f"LAGGED n {len(L)} win {(L.pnl>0).mean():.2f} sum_pnl_bn {L.pnl.sum()/1e9:.2f}", "ticker first last buy pnl ret"]
for _, r in pd.concat([L.head(8), L.tail(5)]).iterrows(): h.append(f"{r.ticker:>6} {r['first'].date()} {r['last'].date()} {r.buy/1e9:.2f} {r.pnl/1e9:.3f} {r.ret:.3f}")
open(f"{R}/engine/lag_holdings_{WT}.txt","w").write("\n".join(h)); print(lines[0]); print("\n".join(h[:8]))
