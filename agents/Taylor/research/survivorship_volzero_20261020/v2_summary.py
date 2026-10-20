"""Tóm tắt V2 theo PREREG_V2 §5 (đọc out_v2_*.csv). job Taylor_20261020_153324."""
import pandas as pd
F = 0.46
r = pd.read_csv("out_v2_results.csv"); s = pd.read_csv("out_v2_solo.csv"); l = pd.read_csv("out_v2_lots.csv")
def lab(x):
    k = (x.abs() >= F).sum(); return "duoi san" if k == 0 else ("vuot san" if k == len(x) else f"cat san ({k}/{len(x)})")
g = r.groupby(["cfgk", "set", "var", "cfg"])
t = g.agg(lo=("d_cagr_pp", "min"), hi=("d_cagr_pp", "max"), sh_lo=("d_sharpe", "min"), sh_hi=("d_sharpe", "max"),
          dd_lo=("d_maxdd_pp", "min"), dd_hi=("d_maxdd_pp", "max"), n_tk=("n_tk", "max"), n_stuck=("n_stuck", "max"),
          label=("d_cagr_pp", lab)).reset_index()
t.to_csv("out_v2_summary.csv", index=False)
pd.set_option("display.width", 250)
print(t[(t.cfg == "MIX")].round(2).to_string(index=False))
sm = s[(s.cfgk == "main") & s.inN]
hit = sm[sm.d_cagr_pp.abs() >= F].groupby(["var", "tk"]).d_cagr_pp.agg(["min", "max", "count"])
print("\nN solo |d|>=0.46 (main):\n", hit.round(2).to_string() if len(hit) else "KHONG CO")
for v in ["UB", "MID", "LIVE"]:
    x = sm[sm["var"] == v].assign(a=lambda d: d.d_cagr_pp.abs()).groupby("tk").agg(amax=("a", "max"), lo=("d_cagr_pp", "min"),
        hi=("d_cagr_pp", "max"), cat=("cat", "first")).sort_values("amax", ascending=False).head(5)
    print(f"\nTop5 N {v}:\n", x.round(3).to_string())
    print(f"  N co >=1 lo ({v}, theo chan):", sm[sm["var"] == v].groupby("leg").tk.nunique().to_dict())
