"""F2 phân rã phần dương (PREREG_F2 §3, mô tả): lô pin bị chặn trong F2 (không có lô F2 cùng mã, mua đầu trong ±5 phiên) vs lô khớp
được; PnL LAG book ref (tỷ) = Σ(sell−buy−fee) theo holding. Chia IS (mua ≤2019) / OOS (2020+)."""
import re, sys, pandas as pd, numpy as np
PIN = {"p30_pin0": "raw/pin_4707bcbe.csv", "p30_pin1M": "raw/pin_bcd0469f.csv", "p0_pin0": "raw/pin_537e349b.csv", "p0_pin1M": "raw/pin_a6ba34d8.csv"}
def lots(csv):
    df = pd.read_csv(csv, low_memory=False)
    cal = pd.DatetimeIndex(sorted(pd.to_datetime(df[df.record_type == "DAILY"].ymd)))
    tx = df[(df.record_type == "TX") & (df.book == "LAG") & (df.play_type != "ETF_PARK")].copy(); tx["ymd"] = pd.to_datetime(tx.ymd)
    for c in ["buy_amount", "sell_amount", "fee"]:
        tx[c] = tx[c].astype(float).fillna(0.0)
    tx["cf"] = tx.sell_amount - tx.buy_amount - tx.fee
    b = tx[tx.action == "buy"].groupby("holding_id").agg(ticker=("ticker", "first"), d0=("ymd", "min"), buy=("buy_amount", "sum"))
    b["pnl"] = tx.groupby("holding_id").cf.sum().reindex(b.index)
    b["force"] = tx[tx.reason.astype(str).str.contains("F1FORCE")].groupby("holding_id").size().reindex(b.index).fillna(0) > 0
    b["i0"] = cal.searchsorted(b.d0.values); return b
var = sys.argv[1] if len(sys.argv) > 1 else "F2"
rows = []
for leg, p in PIN.items():
    P = lots(p); csv = re.findall(r"/home/trido/thanhdt/WorkingClaude/data/v23_golive\S*\.csv", open(f"logs/vz_{var}_{leg}.log").read())[-1]; V = lots(csv)
    vm = V.reset_index().merge(P.reset_index(), on="ticker", suffixes=("", "_p"))
    vm = vm[(vm.i0 - vm.i0_p).abs() <= 5]
    matched_p = set(vm.holding_id_p)
    blk = P[~P.index.isin(matched_p)]; mt = P[P.index.isin(matched_p)]
    vmt = V[V.index.isin(set(vm.holding_id))]
    for per, lo, hi in (("ALL", "2000", "2100"), ("IS", "2000", "2019-12-31"), ("OOS", "2020-01-01", "2100")):
        f = lambda d: d[(d.d0 >= lo) & (d.d0 <= hi)]
        rows.append(dict(var=var, leg=leg, per=per, pin_lots=len(f(P)), blocked_lots=len(f(blk)), blocked_pin_pnl_bn=f(blk).pnl.sum() / 1e9,
                         blocked_pin_buy_bn=f(blk).buy.sum() / 1e9, matched_pin_pnl_bn=f(mt).pnl.sum() / 1e9,
                         matched_var_pnl_bn=f(vmt).pnl.sum() / 1e9, var_lots=len(f(V)), var_unmatched=len(f(V[~V.index.isin(set(vm.holding_id))])),
                         forced_lots=int(f(V).force.sum())))
out = pd.DataFrame(rows); pd.set_option("display.width", 250); print(out.round(2).to_string(index=False)); out.to_csv(f"out_f2_decomp_{var}.csv", index=False)
