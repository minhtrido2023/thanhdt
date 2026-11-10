"""Per-order fill-price sanity vs BQ Open on the 13 gap sessions. Output: gap_fill_check.txt"""
import pandas as pd, numpy as np, sys
E=sys.argv[1]
b=pd.read_csv(f"{E}/data/lag_px_bq_fixed_2026H2.csv",parse_dates=["time"]); b["Open_raw"]=b.Open*b.Price/b.Close
gap=pd.to_datetime(['2026-06-26','2026-06-30','2026-07-15','2026-07-16','2026-07-17','2026-07-20','2026-07-21','2026-07-22','2026-07-27','2026-07-28','2026-07-29','2026-09-08','2026-09-14'])
out=[]
for tag in ["ctrl","fixA","fixB"]:
    t=pd.read_csv(f"{E}/engine/{tag}_transactions.csv",parse_dates=["ymd"]); t=t[~t.reason.astype(str).str.startswith("MTM")&~t.ticker.str.startswith("CUSTOM")]
    m=t.merge(b,left_on=["ymd","ticker"],right_on=["time","ticker"],how="left"); m["gap"]=m.ymd.isin(gap)
    m["dev_open_adj"]=m.adj_price/m.Open-1; m["dev_open_raw"]=m.adj_price/m.Open_raw-1
    m["dev"]=np.where(tag=="fixB",m.dev_open_adj,np.where(tag=="ctrl",np.where(m.book=="BAL",m.dev_open_adj,m.dev_open_raw),m.dev_open_raw))
    for bk in ["BAL","LAGGED"]:
        for g in [True,False]:
            y=m[(m.book==bk)&(m.gap==g)&m.Open.notna()]
            out.append(f"{tag:5s} {bk:6s} {'gap   ' if g else 'normal'} n={len(y):3d} value={ (y.buy_amount.sum()+y.sell_amount.sum())/1e9:6.2f}B  orders |fill/Open-1|>2%: {(y.dev.abs()>0.02).sum():3d}  >5%: {(y.dev.abs()>0.05).sum():3d}  median|dev|={y.dev.abs().median():.4f}")
    if tag=="ctrl":
        x=m[(m.book=="LAGGED")&m.gap&m.Open.notna()].assign(a=lambda d:d.dev.abs()).sort_values("a",ascending=False).head(10)
        out.append(x[["ymd","ticker","adj_price","Open_raw","dev"]].to_string())
open(f"{E}/gap_fill_check.txt","w").write("\n".join(out)); print("\n".join(out))
