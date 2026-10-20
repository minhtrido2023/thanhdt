"""V1(a) bổ sung (NGOÀI PREREG, chỉ chẩn đoán): lệnh mua LAG ngày KL=0 có ADV 3M (Volume_3M_P50) = 0 không
— tức rơi vào nhánh 'ADV<=0 => bỏ trần, mua trọn size 1 phiên' của engine (LIQ_ZERO_BLOCK mặc định tắt)."""
import sys, glob, json, pandas as pd
C = "/home/trido/thanhdt/WorkingClaude/data/bq_cache_asof20260729_postrestate/ticker"
px = pd.concat([pd.read_parquet(f, columns=["ticker", "time", "Volume", "Volume_3M_P50"]) for f in sorted(glob.glob(f"{C}/*.parquet"))])
px["time"] = pd.to_datetime(px.time); px = px.set_index(["ticker", "time"])
out = {}
for a in sys.argv[1:]:
    label, path = a.split("=", 1)
    df = pd.read_csv(path, low_memory=False)
    tx = df[(df.record_type == "TX") & (df.book == "LAG") & (df.action == "buy") & (df.play_type != "ETF_PARK")].copy()
    tx["ymd"] = pd.to_datetime(tx.ymd); tx["amt"] = tx.buy_amount.astype(float)
    j = px.reindex(pd.MultiIndex.from_arrays([tx.ticker, tx.ymd]))
    tx["v"] = j.Volume.values; tx["adv"] = j.Volume_3M_P50.values
    tx["z"] = tx.v == 0; tx["adv0"] = ~(tx.adv > 0)
    o = {}
    for (z, a0), g in tx.groupby(["z", "adv0"]):
        o[f"volzero={z}_adv3m_le0={a0}"] = dict(n=int(len(g)), amt_share=round(float(g.amt.sum() / tx.amt.sum()), 4))
    out[label] = o
print(json.dumps(out, indent=1)); json.dump(out, open("v1a_adv.json", "w"), indent=1)
