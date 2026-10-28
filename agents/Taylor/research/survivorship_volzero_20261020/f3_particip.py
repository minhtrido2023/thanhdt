"""F3 §4 mô tả hậu kỳ: phân phối tỷ lệ tham gia = giá trị mua LAG / giá trị khớp THỰC cùng ngày (dv), theo % giá trị mua."""
import glob, re, sys, pandas as pd, numpy as np
PIN = {"p30_pin0": "raw/pin_4707bcbe.csv", "p30_pin1M": "raw/pin_bcd0469f.csv", "p0_pin0": "raw/pin_537e349b.csv", "p0_pin1M": "raw/pin_a6ba34d8.csv"}
C = "/home/trido/thanhdt/WorkingClaude/data/bq_cache_asof20260729_postrestate/ticker"
px = pd.concat([pd.read_parquet(f, columns=["ticker", "time", "Volume", "Price", "Close"]) for f in sorted(glob.glob(f"{C}/*.parquet"))])
px["time"] = pd.to_datetime(px.time); px["dv"] = px.Volume.astype(float) * px.Price.where(px.Price.notna(), px.Close).astype(float)
px = px.set_index(["ticker", "time"])
def part(csv):
    df = pd.read_csv(csv, low_memory=False)
    b = df[(df.record_type == "TX") & (df.book == "LAG") & (df.play_type != "ETF_PARK") & (df.action == "buy")].copy()
    b["ymd"] = pd.to_datetime(b.ymd); b["buy_amount"] = b.buy_amount.astype(float)
    dv = px.reindex(pd.MultiIndex.from_arrays([b.ticker, b.ymd])).dv.values
    r = np.where(dv > 0, b.buy_amount.values / np.where(dv > 0, dv, 1), np.inf); w = b.buy_amount.values; W = w.sum()
    oos = (b.ymd >= "2020-01-01").values
    return {f"gt{int(t*100)}": 100 * w[r > t].sum() / W for t in (0.2, 0.5, 1.0)} | {
        "gt20_OOS": 100 * w[oos & (r > 0.2)].sum() / w[oos].sum(), "gt100_OOS": 100 * w[oos & (r > 1.0)].sum() / w[oos].sum(),
        "median_part_by_value": float(np.median(np.repeat(np.minimum(r, 99), 1))), "buy_bn": W / 1e9}
rows = [dict(var="pin", leg=l, **part(p)) for l, p in PIN.items()]
for var in sys.argv[1:]:
    for l in PIN:
        csv = re.findall(r"/home/trido/thanhdt/WorkingClaude/data/v23_golive\S*\.csv", open(f"logs/vz_{var}_{l}.log").read())[-1]
        rows.append(dict(var=var, leg=l, **part(csv)))
out = pd.DataFrame(rows); print(out.round(1).to_string(index=False)); out.to_csv(f"out_f3_particip.csv", index=False)
