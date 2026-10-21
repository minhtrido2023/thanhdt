"""Gom Δ so pin + Δ so V1D cho F1/F2/F3 (đọc out_metrics_*.csv do v_metrics.py ghi)."""
import glob, pandas as pd
m = pd.concat([pd.read_csv(f) for f in glob.glob("out_metrics_*.csv")]).drop_duplicates(["var", "leg"], keep="last")
legs = ["p30_pin0", "p30_pin1M", "p0_pin0", "p0_pin1M"]
v1d = m[m["var"] == "V1D"].set_index("leg")
rows = []
for var in ["V1D", "F1_N5H10", "F1_N5H30", "F1_N20H10", "F1_N20H30", "F2", "F2F1_N20H10", "F2F1_N5H30", "F2C", "F3L", "F3B", "ctlZ"]:
    g = m[m["var"] == var].set_index("leg").reindex(legs)
    if g.cagr.isna().all():
        continue
    f = lambda c: " / ".join(f"{x:+.2f}" for x in g[c])
    rng = lambda c, k=2: f"{g[c].min():+.{k}f}…{g[c].max():+.{k}f}"
    rows.append(dict(var=var, d_cagr=f("d_cagr_pp"), d_cagr_vs_V1D=" / ".join(f"{a - b:+.2f}" for a, b in zip(g.cagr, v1d.reindex(legs).cagr)),
                     d_sharpe=rng("d_sharpe", 3), d_maxdd=rng("d_maxdd_pp"), d_is=rng("d_is_pp"), d_oos=rng("d_oos_pp"),
                     above_floor=f"{int((g.d_cagr_pp.abs() > 0.46).sum())}/4 ({'+' if g.d_cagr_pp.mean() > 0 else '-'})",
                     selfcheck=g.selfcheck_maxerr_vnd.max()))
out = pd.DataFrame(rows); pd.set_option("display.width", 300); pd.set_option("display.max_colwidth", 60)
print(out.to_string(index=False)); out.to_csv("out_f_summary.csv", index=False)
