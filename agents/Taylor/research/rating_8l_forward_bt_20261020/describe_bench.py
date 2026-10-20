"""Mô tả (KHÔNG thuộc verdict PREREG_BT): CAGR/Sharpe/DD của rổ EW mọi mã in_universe (giá pin, cân lại ngày, không phí)
cùng giai đoạn sleeve — để tách phần beta small-cap khỏi phần riêng của G1. Chạy: $DNA_PYEXE describe_bench.py"""
import os, numpy as np, pandas as pd, db_dtypes  # noqa: F401
os.chdir(os.path.dirname(os.path.abspath(__file__)))
px = pd.read_parquet("raw/px_pin.parquet"); px["time"] = pd.to_datetime(px.time.astype(str))
u = pd.read_parquet("../rating_8l_lag_p2_20261020/raw/univ.parquet"); u["time"] = pd.to_datetime(u.time.astype(str))
c = px.pivot(index="time", columns="ticker", values="Close")
obs = c.notna(); r = c.ffill().pct_change(fill_method=None)
U = u.assign(v=True).pivot(index="time", columns="ticker", values="v").reindex(index=c.index, columns=c.columns).fillna(False).astype(bool)
m = U.shift(1, fill_value=False) & obs & r.notna()          # thành viên phiên trước (PIT), có giá hôm nay
ew = r.where(m).mean(axis=1)
S = pd.read_csv("out_bt_daily_V1_H40_pin0_2p5B.csv", parse_dates=["date"]).set_index("date").nav.pct_change()
df = pd.concat([S.rename("S"), ew.rename("EW")], axis=1, join="inner").dropna()
for nm, x in (("FULL", df), ("IS", df[df.index <= "2019-12-31"]), ("OOS", df[df.index >= "2020-01-01"])):
    out = []
    for k in ("S", "EW"):
        v = (1 + x[k]).cumprod(); y = (x.index[-1] - x.index[0]).days / 365.25
        out.append(f"{k}: CAGR {v.iloc[-1] ** (1 / y) - 1:.4f} Sh {x[k].mean() / x[k].std() * 252 ** .5:.3f} DD {(v / v.cummax() - 1).min():.4f}")
    b = np.cov(x.S, x.EW)[0, 1] / x.EW.var()
    print(nm, " | ".join(out), f"| beta S~EW {b:.3f} corr {x.S.corr(x.EW):.3f}")
