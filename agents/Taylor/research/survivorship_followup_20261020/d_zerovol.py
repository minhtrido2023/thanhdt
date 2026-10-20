"""D phụ: quy mô mua/bán LAG vào ngày KL khớp=0 (engine khớp theo ADV 3M, không theo KL ngày)."""
import sys, glob, json, pandas as pd
C = "/home/trido/thanhdt/WorkingClaude/data/bq_cache_asof20260729_postrestate/ticker"
px = pd.concat([pd.read_parquet(f, columns=["ticker", "time", "Volume"]) for f in sorted(glob.glob(f"{C}/*.parquet"))])
px["time"] = pd.to_datetime(px.time); vol = px.set_index(["ticker", "time"]).Volume
out = {}
for a in sys.argv[1:]:
    label, path = a.split("=", 1)
    df = pd.read_csv(path, low_memory=False)
    tx = df[(df.record_type == "TX") & (df.play_type != "ETF_PARK")].copy(); tx["ymd"] = pd.to_datetime(tx.ymd)
    tx["v"] = [vol.get((t, d), 0) for t, d in zip(tx.ticker, tx.ymd)]; tx["z"] = ~(tx.v.fillna(0) > 0)
    tx["amt"] = tx.buy_amount.astype(float).fillna(0) + tx.sell_amount.astype(float).fillna(0)
    out[label] = {f"{b}_{a_}": dict(n=int(len(g)), n_zero=int(g.z.sum()), amt_share_zero=float(g[g.z].amt.sum() / g.amt.sum()))
                  for (b, a_), g in tx.groupby(["book", "action"])}
print(json.dumps(out, indent=1)); json.dump(out, open("d_zerovol.json", "w"), indent=1)
