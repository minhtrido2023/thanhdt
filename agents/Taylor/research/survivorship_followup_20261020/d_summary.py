"""D tổng hợp: từ d_lots_<leg>.csv + TX + cache giá — bán vào ngày KL=0 (giá đứng), mã ngừng dữ liệu, phơi nhiễm combined khi cap bật lại."""
import sys, glob, json
import numpy as np, pandas as pd
C = "/home/trido/thanhdt/WorkingClaude/data/bq_cache_asof20260729_postrestate/ticker"
px = pd.concat([pd.read_parquet(f, columns=["ticker", "time", "Close", "Volume"]) for f in sorted(glob.glob(f"{C}/*.parquet"))])
px["time"] = pd.to_datetime(px.time); vol = px.set_index(["ticker", "time"]).Volume
res = {}
for a in sys.argv[1:]:
    label, path = a.split("=", 1)
    df = pd.read_csv(path, low_memory=False)
    d = df[df.record_type == "DAILY"].copy(); d["ymd"] = pd.to_datetime(d.ymd); d = d.set_index("ymd").sort_index()
    for c in ["w_lag_tgt", "cap_lag", "combined_nav", "state"]:
        d[c] = d[c].astype(float)
    END = d.index[-1]
    tx = df[(df.record_type == "TX") & (df.book == "LAG") & (df.play_type != "ETF_PARK")].copy(); tx["ymd"] = pd.to_datetime(tx.ymd)
    sells = tx[tx.action == "sell"]
    zv = [(h, t, dd.date()) for h, t, dd in zip(sells.holding_id, sells.ticker, sells.ymd) if not (vol.get((t, dd), 0) > 0)]
    r = pd.read_csv(f"d_lots_{label}.csv"); r["buy"] = pd.to_datetime(r.buy); r["last_sell"] = pd.to_datetime(r.last_sell)
    b = r[r.bear_open].copy()
    # phơi nhiễm combined tối đa trong đời lô = w_in_book × max(cap_lag/combined) trên [buy, last_sell]
    b["max_comb_expo"] = [float(r_.w_in_book * (d.cap_lag / d.combined_nav).loc[r_.buy:r_.last_sell].max()) for r_ in b.itertuples()]
    zvh = {h for h, _, _ in zv}
    b["sold_on_zero_vol"] = b.hid.isin(zvh)
    res[label] = dict(
        lag_lots=len(r), bear_lots=len(b), bear_lots_cap_reenabled=int(b.cap_reenabled.sum()),
        bear_lots_by_year=b.buy.dt.year.value_counts().sort_index().to_dict(),
        bear_ret_med=float(b.ret.median()), bear_ret_min=float(b.ret.min()), bear_ret_max=float(b.ret.max()),
        bear_lots_maxrun_ge5=int((b.max_nontrade_run >= 5).sum()),
        bear_lots_sold_on_zero_vol=int(b.sold_on_zero_vol.sum()),
        bear_lots_open_at_end=int(b.closed_at_end.sum()),
        bear_lots_tk_stops_before_audit_end=b[b.tk_last_row < str(END.date())][["hid", "tk_last_row", "last_sell"]].astype(str).to_dict("records"),
        bear_max_comb_expo_top=b.nlargest(5, "max_comb_expo")[["hid", "max_comb_expo", "ret", "sessions"]].round(4).to_dict("records"),
        bear_worst5=b.nsmallest(5, "ret")[["hid", "ret", "max_comb_expo", "max_nontrade_run", "sold_on_zero_vol"]].round(4).to_dict("records"),
        all_lag_sells_on_zero_vol=len(zv), all_lag_lots_sold_on_zero_vol=len(zvh),
        all_lots_tk_stops_before_end=int((r.tk_last_row < str(END.date())).sum()))
    b.to_csv(f"d_bear_lots_{label}.csv", index=False)
json.dump(res, open("d_summary.json", "w"), indent=1, default=str)
print(json.dumps(res, indent=1, default=str))
