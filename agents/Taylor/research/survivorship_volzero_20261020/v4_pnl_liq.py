"""V4 (PREREG_V4.md) — PnL LAG book ref của PIN theo điều kiện thanh khoản lệnh mua (Z/X/OK/NA), theo năm mua."""
import glob, json, pandas as pd, numpy as np
PIN = {"p30_pin0": "raw/pin_4707bcbe.csv", "p30_pin1M": "raw/pin_bcd0469f.csv", "p0_pin0": "raw/pin_537e349b.csv", "p0_pin1M": "raw/pin_a6ba34d8.csv"}
C = "/home/trido/thanhdt/WorkingClaude/data/bq_cache_asof20260729_postrestate/ticker"
px = pd.concat([pd.read_parquet(f, columns=["ticker", "time", "Volume", "Price", "Close"]) for f in sorted(glob.glob(f"{C}/*.parquet"))])
px["time"] = pd.to_datetime(px.time)
px["dv"] = px.Volume.astype(float) * px.Price.where(px.Price.notna(), px.Close).astype(float)
px = px.set_index(["ticker", "time"])
rows, chk = [], {}
for leg, p in PIN.items():
    df = pd.read_csv(p, low_memory=False)
    tx = df[(df.record_type == "TX") & (df.book == "LAG") & (df.play_type != "ETF_PARK")].copy()
    tx["ymd"] = pd.to_datetime(tx.ymd)
    for c in ["buy_amount", "sell_amount", "fee", "shares"]:
        tx[c] = tx[c].astype(float).fillna(0.0)
    tx["cf"] = tx.sell_amount - tx.buy_amount - tx.fee          # dòng tiền ròng (fee luôn là chi)
    pnl = tx.groupby("holding_id").cf.sum()
    sh = tx.assign(s=np.where(tx.action == "buy", tx.shares, -tx.shares)).groupby("holding_id").s.sum()
    buy_sh = tx[tx.action == "buy"].groupby("holding_id").shares.sum()
    b = tx[tx.action == "buy"].copy()
    j = px.reindex(pd.MultiIndex.from_arrays([b.ticker, b.ymd]))
    b["vol"], b["dv"] = j.Volume.values, j.dv.values
    b["grp"] = np.select([b.vol.isna(), b.vol == 0, b.buy_amount > 0.2 * b.dv], ["NA", "Z", "X"], "OK")
    b["w"] = b.buy_amount / b.groupby("holding_id").buy_amount.transform("sum")
    b["pnl"] = b.w * b.holding_id.map(pnl)
    b["yr"] = b.ymd.dt.year
    resid = (sh.reindex(buy_sh.index) / buy_sh).abs()
    chk[leg] = dict(lots=int(len(buy_sh)), lots_open_resid_gt1pct=int((resid > 0.01).sum()),
                    lots_without_buy=int(len(set(pnl.index) - set(buy_sh.index))),
                    pnl_lots_bn=round(pnl.reindex(buy_sh.index).sum() / 1e9, 3), pnl_alloc_bn=round(b.pnl.sum() / 1e9, 3),
                    pnl_unalloc_bn=round(pnl.drop(buy_sh.index, errors="ignore").sum() / 1e9, 3))
    g = b.groupby(["yr", "grp"]).agg(buy_bn=("buy_amount", "sum"), pnl_bn=("pnl", "sum"), n=("ticker", "size")).reset_index()
    g[["buy_bn", "pnl_bn"]] /= 1e9; g.insert(0, "leg", leg); rows.append(g)
out = pd.concat(rows); out.to_csv("v4_pnl_by_year.csv", index=False)
json.dump(chk, open("v4_checks.json", "w"), indent=1); print(json.dumps(chk, indent=1))
def summ(d):
    t = d.groupby("grp")[["buy_bn", "pnl_bn"]].sum(); tot = t.sum()
    return pd.DataFrame({"buy_bn": t.buy_bn, "buy_share": t.buy_bn / tot.buy_bn, "pnl_bn": t.pnl_bn, "pnl_share": t.pnl_bn / tot.pnl_bn})
for leg in PIN:
    d = out[out.leg == leg]
    print(f"\n==== {leg}")
    for lab, sel in [("2014-2026", d), ("2014-2021", d[d.yr <= 2021]), ("2022-2026", d[d.yr >= 2022])]:
        print(f"-- {lab}"); print(summ(sel).round(3).to_string())
    pv = d.pivot_table(index="yr", columns="grp", values=["buy_bn", "pnl_bn"], aggfunc="sum").fillna(0).round(1)
    print(pv.to_string())
