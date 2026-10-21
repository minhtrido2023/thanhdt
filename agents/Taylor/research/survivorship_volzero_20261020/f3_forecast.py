"""PREREG_F3 §1-2: hệ số sự kiện LAG m_Y (PIT, mở rộng theo năm) + độ chính xác dự báo dv. Mô tả."""
import glob, json, numpy as np, pandas as pd
C = "/home/trido/thanhdt/WorkingClaude/data/bq_cache_asof20260729_postrestate/ticker"
px = pd.concat([pd.read_parquet(f, columns=["ticker", "time", "Volume", "Price", "Close", "Volume_3M_P50"]) for f in sorted(glob.glob(f"{C}/*.parquet"))])
px["time"] = pd.to_datetime(px.time); px = px.sort_values(["ticker", "time"])
p_ = px.Price.where(px.Price.notna(), px.Close).astype(float)
px["dv"] = px.Volume.astype(float) * p_; px.loc[px.Volume == 0, "dv"] = 0.0
g = px.groupby("ticker").dv
px["F"] = g.transform(lambda v: v.rolling(20, min_periods=1).median().shift(1)).fillna(0.0)          # chính (tính 0)
px["E20"] = g.transform(lambda v: v.where(v > 0).rolling(20, min_periods=1).median().shift(1)).fillna(0.0)  # V1E20
px["ADV3M"] = px.Volume_3M_P50.astype(float) * p_                                                    # trần pin
px = px.set_index(["ticker", "time"])
def buys(csv, book):
    df = pd.read_csv(csv, low_memory=False)
    tx = df[(df.record_type == "TX") & (df.book == book) & (df.play_type != "ETF_PARK") & (df.action == "buy")].copy()
    tx["ymd"] = pd.to_datetime(tx.ymd); tx["buy_amount"] = tx.buy_amount.astype(float)
    j = px.reindex(pd.MultiIndex.from_arrays([tx.ticker, tx.ymd]))
    for c in ("Volume", "dv", "F", "E20", "ADV3M"): tx[c] = j[c].values
    return tx
lag = buys("raw/pin_4707bcbe.csv", "LAG")
ok = lag[(lag.Volume > 0) & (lag.F > 0)].copy(); ok["r"] = ok.dv / ok.F; ok["yr"] = ok.ymd.dt.year
mult = {}
for Y in range(2014, 2027):
    prev = ok[ok.yr < Y].r
    mult[Y] = float(prev.median()) if len(prev) else 1.0
print("m_Y:", {k: round(v, 3) for k, v in mult.items()})
print("n lệnh LAG (Volume>0,F>0) theo năm:", ok.groupby("yr").size().to_dict())
lag["Fm"] = lag.F * lag.ymd.dt.year.map(mult)
bal = buys("raw/pin_4707bcbe.csv", "BAL")
rows = []
for nm, d, cols in (("LAG", lag, ["ADV3M", "E20", "F", "Fm"]), ("BAL", bal, ["ADV3M", "E20", "F"])):
    d = d[d.Volume > 0]
    for c in cols:
        f = d[c].astype(float); pos = f > 0
        rows.append(dict(book=nm, forecast=c, n=len(d), pct_fc_zero=100 * (~pos).mean(),
                         median_log_actual_over_fc=float(np.median(np.log(d.dv[pos] / f[pos]))),
                         pct_actual_below_fc=100 * float((d.dv[pos] < f[pos]).mean()),
                         pct_buyvalue_weighted_actual_below_fc=100 * float(d.buy_amount[pos][d.dv[pos] < f[pos]].sum() / d.buy_amount[pos].sum())))
acc = pd.DataFrame(rows); print(acc.round(3).to_string(index=False)); acc.to_csv("out_f3_accuracy.csv", index=False)
# theo năm cho LAG F và Fm
d = lag[(lag.Volume > 0)]; yr = []
for Y, gg in d.groupby(d.ymd.dt.year):
    r = {"yr": Y, "n": len(gg)}
    for c in ("ADV3M", "F", "Fm"):
        pos = gg[c] > 0
        r[f"below_{c}"] = round(100 * float((gg.dv[pos] < gg[c][pos]).mean()), 1)
        r[f"mlog_{c}"] = round(float(np.median(np.log(gg.dv[pos] / gg[c][pos]))), 3)
    yr.append(r)
print(pd.DataFrame(yr).to_string(index=False)); pd.DataFrame(yr).to_csv("out_f3_accuracy_by_year.csv", index=False)
json.dump(mult, open("f3_mult.json", "w"))
print("F3_MULT=" + ",".join(f"{k}:{v:.6f}" for k, v in mult.items()))
