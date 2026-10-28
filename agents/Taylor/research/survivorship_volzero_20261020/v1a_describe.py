"""V1(a) — quy mô lệnh khớp vào ngày Volume=0 ở 4 chân pin + kiểm giá carry (PREREG_V1 §1)."""
import sys, glob, json
import pandas as pd

C = "/home/trido/thanhdt/WorkingClaude/data/bq_cache_asof20260729_postrestate/ticker"
px = pd.concat([pd.read_parquet(f, columns=["ticker", "time", "Open", "High", "Low", "Close", "Volume"])
                for f in sorted(glob.glob(f"{C}/*.parquet"))], ignore_index=True)
px["time"] = pd.to_datetime(px.time)
px = px.sort_values(["ticker", "time"])
px["Close_prev"] = px.groupby("ticker").Close.shift(1)
px = px.set_index(["ticker", "time"])

out, years = {}, {}
for a in sys.argv[1:]:
    label, path = a.split("=", 1)
    df = pd.read_csv(path, low_memory=False)
    tx = df[df.record_type == "TX"].copy()
    tx["ymd"] = pd.to_datetime(tx.ymd)
    tx["amt"] = tx.buy_amount.astype(float).fillna(0) + tx.sell_amount.astype(float).fillna(0)
    j = px.reindex(pd.MultiIndex.from_arrays([tx.ticker, tx.ymd]))
    for c in ["Open", "High", "Low", "Close", "Volume", "Close_prev"]:
        tx[c] = j[c].values
    tx["missing"] = tx.Volume.isna()
    tx["z"] = tx.Volume == 0
    tx["ohlc_flat"] = (tx.Open == tx.High) & (tx.High == tx.Low) & (tx.Low == tx.Close)
    tx["eq_prev"] = (tx.Close - tx.Close_prev).abs() <= 1e-9 * tx.Close.abs().clip(lower=1)
    tx["grp"] = tx.book + "_" + tx.action
    tx.loc[tx.play_type == "ETF_PARK", "grp"] = "ETF_PARK_" + tx.action
    tx = tx[tx.reason != "MTM_UNREALIZED"]          # dòng mark cuối kỳ, không phải lệnh
    o = {}
    for g, d in tx.groupby("grp"):
        zz = d[d.z]
        o[g] = dict(n=int(len(d)), n_zero=int(len(zz)), n_missing=int(d.missing.sum()),
                    amt_bn=round(d.amt.sum() / 1e9, 3), amt_zero_bn=round(zz.amt.sum() / 1e9, 3),
                    amt_share_zero=round(float(zz.amt.sum() / d.amt.sum()), 4) if d.amt.sum() else None,
                    zero_carry_n=int((zz.ohlc_flat & zz.eq_prev).sum()),
                    zero_flat_only_n=int((zz.ohlc_flat & ~zz.eq_prev).sum()),
                    zero_eqprev_only_n=int((~zz.ohlc_flat & zz.eq_prev).sum()),
                    zero_neither_n=int((~zz.ohlc_flat & ~zz.eq_prev).sum()),
                    zero_carry_amt_share=round(float(zz[zz.ohlc_flat & zz.eq_prev].amt.sum() / zz.amt.sum()), 4) if len(zz) else None,
                    top3=[dict(ticker=r.ticker, ymd=str(r.ymd.date()), amt_bn=round(r.amt / 1e9, 2), reason=r.reason)
                          for r in zz.nlargest(3, "amt").itertuples()])
        if d.action.iloc[0] == "sell" and not g.startswith("ETF"):
            o[g]["zero_by_reason"] = {k: dict(n=int(len(v)), amt_bn=round(v.amt.sum() / 1e9, 2))
                                      for k, v in zz.groupby("reason")}
    out[label] = o
    yy = tx[tx.grp.isin(["LAG_buy", "LAG_sell", "BAL_buy", "BAL_sell"])].copy()
    yy["yr"] = yy.ymd.dt.year
    t = yy.groupby(["grp", "yr"]).apply(lambda d: pd.Series(dict(
        n=len(d), n_zero=int(d.z.sum()), share_zero=d[d.z].amt.sum() / d.amt.sum() if d.amt.sum() else float("nan"))),
        include_groups=False).reset_index()
    t.insert(0, "leg", label)
    years[label] = t

json.dump(out, open("v1a_describe.json", "w"), indent=1, default=str)
pd.concat(years.values()).to_csv("v1a_by_year.csv", index=False)
for leg, o in out.items():
    print(f"== {leg}")
    for g, r in o.items():
        print(f"  {g:14s} n={r['n']:5d} zero={r['n_zero']:4d} miss={r['n_missing']:3d} share_zero={r['amt_share_zero']} "
              f"carry={r['zero_carry_n']} flat_only={r['zero_flat_only_n']} eqprev_only={r['zero_eqprev_only_n']} "
              f"neither={r['zero_neither_n']} carry_amt_share={r['zero_carry_amt_share']}")
        print(f"      top3={r['top3']}")
        if "zero_by_reason" in r:
            print(f"      by_reason={r['zero_by_reason']}")
