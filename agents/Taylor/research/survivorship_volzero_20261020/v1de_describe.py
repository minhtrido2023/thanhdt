"""V1D/V1E mô tả (PREREG_V1D §3): lô LAG, tổng mua, refund, % giá trị mua LAG ngày Volume=0 (Z) / vượt 20% khớp cùng ngày (X),
lô LAG_HI/LO giữ >30 / >45 phiên (trần giữ 25), lô kẹt cuối kỳ, book ref BAL/LAG. Pin + từng biến thể."""
import sys, re, glob, pandas as pd, numpy as np
PIN = {"p30_pin0": "raw/pin_4707bcbe.csv", "p30_pin1M": "raw/pin_bcd0469f.csv", "p0_pin0": "raw/pin_537e349b.csv", "p0_pin1M": "raw/pin_a6ba34d8.csv"}
C = "/home/trido/thanhdt/WorkingClaude/data/bq_cache_asof20260729_postrestate/ticker"
px = pd.concat([pd.read_parquet(f, columns=["ticker", "time", "Volume", "Price", "Close"]) for f in sorted(glob.glob(f"{C}/*.parquet"))])
px["time"] = pd.to_datetime(px.time); px["dv"] = px.Volume.astype(float) * px.Price.where(px.Price.notna(), px.Close).astype(float)
px = px.set_index(["ticker", "time"])
def info(p):
    df = pd.read_csv(p, low_memory=False)
    cal = pd.DatetimeIndex(sorted(pd.to_datetime(df[df.record_type == "DAILY"].ymd)))
    m = df[df.record_type == "METRIC"].set_index("key").value.astype(float)
    tx = df[(df.record_type == "TX") & (df.book == "LAG") & (df.play_type != "ETF_PARK")].copy(); tx["ymd"] = pd.to_datetime(tx.ymd)
    tx["buy_amount"] = tx.buy_amount.astype(float)
    b = tx[tx.action == "buy"].copy(); j = px.reindex(pd.MultiIndex.from_arrays([b.ticker, b.ymd]))
    z = j.Volume.values == 0; x = (~z) & (b.buy_amount.values > 0.2 * j.dv.values)
    s = tx[(tx.action == "sell") & (tx.reason != "MTM_UNREALIZED") & (tx.reason != "ABANDONED_REFUND")]
    lb = b.groupby("holding_id").ymd.max(); ls = s.groupby("holding_id").ymd.max()
    hl = b.groupby("holding_id").play_type.first().isin(["LAG_HI", "LAG_LO"])
    k = ls.index.intersection(lb.index[hl.reindex(lb.index).values])
    held = pd.Series(cal.searchsorted(ls[k].values) - cal.searchsorted(lb[k].values), index=k)
    return dict(lots=b.holding_id.nunique(), buy_bn=b.buy_amount.sum() / 1e9, refund=int((tx.reason == "ABANDONED_REFUND").sum()),
                z=b.buy_amount[z].sum() / b.buy_amount.sum(), x=b.buy_amount[x].sum() / b.buy_amount.sum(),
                held30=int((held > 30).sum()), held45=int((held > 45).sum()),
                stuck=int(((tx.reason == "MTM_UNREALIZED")).sum()),
                bal_ref=m.final_nav_bal_ref_vnd / 1e9, lag_ref=m.final_nav_lag_ref_vnd / 1e9)
rows = []
for leg, p in PIN.items():
    rows.append(dict(var="pin", leg=leg, **info(p)))
for var in sys.argv[1:]:
    for leg in PIN:
        log = open(f"logs/vz_{var}_{leg}.log").read()
        csv = re.findall(r"/home/trido/thanhdt/WorkingClaude/data/v23_golive\S*\.csv", log)[-1]
        r = dict(var=var, leg=leg, **info(csv))
        for tag in ("ZVF", "V1D", "V3"):
            mm = re.findall(rf"\[{tag}\] v23audit_LAG: cumulative (\{{.*\}})", log)
            if mm: r[f"{tag}_LAG"] = mm[-1]
        rows.append(r)
out = pd.DataFrame(rows); out.to_csv(f"out_describe_{'_'.join(sys.argv[1:])}.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 120)
print(out.round(3).to_string(index=False))
