"""Nguồn Δ R3 (pin0%): khác biệt lệnh LAG + w_lag_tgt giữa ctrl và adj, theo năm."""
import pandas as pd, glob, numpy as np
f = {t: glob.glob(f"sandbox_{t}/data/*exp_r3_{t}_p0_off_univpit.csv")[0] for t in ("ctrl", "adj")}
d = {t: pd.read_csv(p, low_memory=False) for t, p in f.items()}
tx = {t: x[(x.record_type == "TX")].assign(y=lambda z: z.ymd.str[:4]) for t, x in d.items()}
for book in ("BAL", "LAG"):
    a, b = tx["ctrl"][tx["ctrl"].book == book], tx["adj"][tx["adj"].book == book]
    k = ["ymd", "ticker", "action"]; m = a.merge(b, on=k, how="outer", indicator=True)
    print(book, "TX ctrl", len(a), "adj", len(b), "| khác theo năm:", m[m._merge != "both"].ymd.str[:4].value_counts().sort_index().to_dict())
dl = {t: x[x.record_type == "DAILY"].set_index("ymd") for t, x in d.items()}
w = pd.concat([dl["ctrl"].w_lag_tgt.rename("c"), dl["adj"].w_lag_tgt.rename("a")], axis=1).dropna()
dw = w[w.c != w.a]; print("w_lag_tgt khác:", len(dw), "ngày; theo năm", pd.Series(dw.index.str[:4]).value_counts().sort_index().to_dict())
for t in ("ctrl", "adj"):
    x = dl[t]; x = x[x.index.str[:4] == "2023"]
    print(t, "2023 nav_lag_ref đầu/cuối", round(float(x.nav_lag_ref.iloc[0]) / 1e9, 2), round(float(x.nav_lag_ref.iloc[-1]) / 1e9, 2),
          "nav_bal_ref", round(float(x.nav_bal_ref.iloc[0]) / 1e9, 2), round(float(x.nav_bal_ref.iloc[-1]) / 1e9, 2))
a = tx["ctrl"]; b = tx["adj"]
for t, x in (("ctrl", a), ("adj", b)):
    z = x[(x.book == "LAG") & (x.y == "2023") & (x.action == "buy")]
    print(t, "LAG buy 2023:", len(z), sorted(set(z.ticker))[:40])
