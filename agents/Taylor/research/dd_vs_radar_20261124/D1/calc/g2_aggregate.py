"""Tổng hợp G2: đóng góp từng mô-đun (Δ bước / giá trị trước bước, %) trên các dòng chuỗi (step_order số)."""
import pandas as pd, re, numpy as np
d = pd.concat([pd.read_csv(f) for f in ["g2_waterfall_A.csv", "g2_waterfall_B.csv"]])
d = d[d.step_order.astype(str).str.fullmatch(r"\d+")].copy()
d = d[~d.module.isin(["raw", "final_center"])]
d["base"] = d.module.str.extract(r"^(other:[A-Za-z_]+|[a-z_A-Z0-9]+)")[0]
d.loc[d.base.str.startswith("other"), "base"] = "other"
d["step_pct"] = (d.value_after - d.value_before) / d.value_before * 100
d["ul"] = d.basis.astype(str).str.contains(r"\[UL\]")
g = d.groupby("base").agg(n_steps=("step_pct", "size"), n_tickers=("ticker", "nunique"),
                          median_step_pct=("step_pct", "median"), min_pct=("step_pct", "min"), max_pct=("step_pct", "max"),
                          n_down=("step_pct", lambda x: int((x < -0.05).sum())), n_up=("step_pct", lambda x: int((x > 0.05).sum())),
                          share_UL=("ul", "mean")).round(2).sort_values("median_step_pct")
print(g.to_string()); g.to_csv("g2_module_summary.csv")
tot = d.groupby("ticker").step_pct.apply(lambda x: (np.prod(1 + x.dropna() / 100) - 1) * 100).round(1)
print("chain total % per ticker:", tot.to_dict()); print("median chain total %:", round(float(tot.median()), 1), "N tickers", len(tot))
