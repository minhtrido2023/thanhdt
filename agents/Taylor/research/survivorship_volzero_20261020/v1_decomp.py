"""Phân rã biến thể V1/V3 vs pin: DD (đỉnh/đáy), lợi suất năm combined, book ref final, lô LAG, % khớp ngày KL=0."""
import sys, re, glob, pandas as pd, numpy as np
PIN = {"p30_pin0": "raw/pin_4707bcbe.csv", "p30_pin1M": "raw/pin_bcd0469f.csv", "p0_pin0": "raw/pin_537e349b.csv", "p0_pin1M": "raw/pin_a6ba34d8.csv"}
C = "/home/trido/thanhdt/WorkingClaude/data/bq_cache_asof20260729_postrestate/ticker"
vol = pd.concat([pd.read_parquet(f, columns=["ticker", "time", "Volume"]) for f in sorted(glob.glob(f"{C}/*.parquet"))])
vol["time"] = pd.to_datetime(vol.time); vol = vol.set_index(["ticker", "time"]).Volume
def info(p):
    df = pd.read_csv(p, low_memory=False)
    d = df[df.record_type == "DAILY"].copy(); d["ymd"] = pd.to_datetime(d.ymd); d = d.set_index("ymd")
    s = d.combined_nav.astype(float); dd = s / s.cummax() - 1; t = dd.idxmin(); pk = s[:t].idxmax()
    yr = s.groupby(s.index.year).last().pct_change(); yr.iloc[0] = s.groupby(s.index.year).last().iloc[0] / s.iloc[0] - 1
    tx = df[(df.record_type == "TX") & (df.play_type != "ETF_PARK") & (df.reason != "MTM_UNREALIZED")].copy(); tx["ymd"] = pd.to_datetime(tx.ymd)
    tx["amt"] = tx.buy_amount.astype(float) + tx.sell_amount.astype(float)
    tx["z"] = vol.reindex(pd.MultiIndex.from_arrays([tx.ticker, tx.ymd])).values == 0
    lag = tx[tx.book == "LAG"]
    m = df[df.record_type == "METRIC"].set_index("key").value.astype(float)
    return dict(dd=round(dd.min() * 100, 2), dd_peak=str(pk.date()), dd_trough=str(t.date()), yr=(yr * 100).round(2),
                fin_bal_ref=m.final_nav_bal_ref_vnd / 1e9, fin_lag_ref=m.final_nav_lag_ref_vnd / 1e9,
                lag_lots=lag[lag.action == "buy"].holding_id.nunique(),
                lag_buy_bn=lag[lag.action == "buy"].amt.sum() / 1e9,
                lag_refund_n=int((lag.reason == "ABANDONED_REFUND").sum()),
                lag_zero_buy_share=lag[(lag.action == "buy") & lag.z].amt.sum() / lag[lag.action == "buy"].amt.sum(),
                lag_zero_sell_share=lag[(lag.action == "sell") & lag.z].amt.sum() / lag[lag.action == "sell"].amt.sum())
for var in sys.argv[1:]:
    yrs = {}
    for leg, p in PIN.items():
        b = info(p)
        csv = re.findall(r"/home/trido/thanhdt/WorkingClaude/data/v23_golive\S*\.csv", open(f"logs/vz_{var}_{leg}.log").read())[-1]
        v = info(csv)
        print(f"== {var} {leg}: DD pin {b['dd']} ({b['dd_peak']}→{b['dd_trough']}) vs {v['dd']} ({v['dd_peak']}→{v['dd_trough']}) | "
              f"BALref {b['fin_bal_ref']:.1f}->{v['fin_bal_ref']:.1f}B LAGref {b['fin_lag_ref']:.1f}->{v['fin_lag_ref']:.1f}B | "
              f"LAG lots {b['lag_lots']}->{v['lag_lots']} buy {b['lag_buy_bn']:.0f}->{v['lag_buy_bn']:.0f}B refund {b['lag_refund_n']}->{v['lag_refund_n']} | "
              f"zero-buy {b['lag_zero_buy_share']:.3f}->{v['lag_zero_buy_share']:.3f} zero-sell {b['lag_zero_sell_share']:.3f}->{v['lag_zero_sell_share']:.3f}")
        yrs[leg] = (v["yr"] - b["yr"]).round(2)
    print(f"Δ lợi suất năm combined (pp), {var}:"); print(pd.DataFrame(yrs).T.to_string())
