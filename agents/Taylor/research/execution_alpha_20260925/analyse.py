#!/usr/bin/env python3
"""Distribution of measured slippage + cluster bootstrap + decomposition."""
import os, json
import numpy as np, pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
m = pd.read_csv(os.path.join(HERE, "slippage.csv"))
rng = np.random.default_rng(20260925)

CLU = ["trans_date", "ticker"]          # one price shock = one observation
BENCH = ["slip_vs_open_bps", "slip_vs_prevclose_bps", "slip_vs_close_bps", "slip_vs_limit_bps"]

out = {}

# ---------- 1. raw distribution, order level and cluster level ----------
def desc(x):
    x = np.asarray(x, float); x = x[~np.isnan(x)]
    return dict(n=int(len(x)), mean=float(x.mean()), sd=float(x.std(ddof=1)),
                se=float(x.std(ddof=1)/np.sqrt(len(x))),
                t=float(x.mean()/(x.std(ddof=1)/np.sqrt(len(x)))),
                skew=float(stats.skew(x)), exkurt=float(stats.kurtosis(x)),
                p01=float(np.percentile(x,1)), p05=float(np.percentile(x,5)),
                p25=float(np.percentile(x,25)), p50=float(np.median(x)),
                p75=float(np.percentile(x,75)), p95=float(np.percentile(x,95)),
                p99=float(np.percentile(x,99)),
                mn=float(x.min()), mx=float(x.max()))

out["distribution"] = {}
for b in BENCH:
    o = desc(m[b])
    c = desc(m.groupby(CLU)[b].mean())
    out["distribution"][b] = {"order_level": o, "cluster_level_date_x_ticker": c}

# ---------- 2. cluster bootstrap on the notional-weighted total cost ----------
gid = m.groupby(CLU).ngroup().values
groups = np.unique(gid)
notional = m["notional_vnd"].values
span_days = (pd.to_datetime(m.trans_date).max() - pd.to_datetime(m.trans_date).min()).days + 1
ann = 365.0 / span_days

boot = {}
for b in BENCH:
    v = m[b].values
    obs_cost = np.nansum(v / 1e4 * notional)
    draws = np.empty(5000)
    idx_by_g = {g: np.where(gid == g)[0] for g in groups}
    for i in range(5000):
        pick = rng.choice(groups, size=len(groups), replace=True)
        sel = np.concatenate([idx_by_g[g] for g in pick])
        draws[i] = np.nansum(v[sel] / 1e4 * notional[sel]) * (len(gid) / len(sel))
    boot[b] = dict(
        total_cost_vnd=float(obs_cost),
        ci95=[float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))],
        p_cost_le_0=float((draws <= 0).mean()),
        notional_wtd_bps=float(obs_cost / notional.sum() * 1e4),
        annualised_vnd=float(obs_cost * ann),
    )
out["cluster_bootstrap_total_cost"] = boot
out["meta"] = dict(
    n_orders=int(len(m)), n_clusters=int(len(groups)),
    n_dates=int(m.trans_date.nunique()), n_tickers=int(m.ticker.nunique()),
    span_days=int(span_days), annualiser=float(ann),
    notional_vnd=float(notional.sum()),
    notional_annualised_vnd=float(notional.sum() * ann),
    clusters_per_year=float(len(groups) * ann),
    orders_per_year=float(len(m) * ann),
)

# ---------- 3. range position ----------
g = m.groupby(CLU)["range_pos_cost"].mean()
t, p = stats.ttest_1samp(g.dropna(), 0.5)
out["range_pos_cost"] = dict(order_level_mean=float(m.range_pos_cost.mean()),
                             cluster_mean=float(g.mean()), cluster_n=int(g.notna().sum()),
                             t_vs_0p5=float(t), p_vs_0p5=float(p))

# ---------- 4. decomposition — ONLY axes with evidence in the data ----------
def cell(sub, b="slip_vs_open_bps"):
    x = sub[b].dropna()
    if len(x) < 3: return None
    gg = sub.groupby(CLU)[b].mean().dropna()
    return dict(n_orders=int(len(x)), n_clusters=int(len(gg)),
                mean_bps=float(x.mean()),
                cluster_mean_bps=float(gg.mean()),
                cluster_sd=float(gg.std(ddof=1)),
                cluster_t=float(gg.mean()/(gg.std(ddof=1)/np.sqrt(len(gg)))),
                wtd_bps=float(np.average(x, weights=sub.loc[x.index, "notional_vnd"])),
                notional=float(sub.loc[x.index, "notional_vnd"].sum()))

dec = {}
for axis, col in [("time_of_day_placed", "tod_bucket"), ("side", "side"),
                  ("account", "account")]:
    dec[axis] = {str(k): cell(v) for k, v in m.groupby(col)}

m["adv_bucket"] = pd.cut(m["adv_frac"], [0, .0005, .002, .01, .05, 1],
                         labels=["<0.05%ADV", "0.05-0.2%", "0.2-1%", "1-5%", ">5%"])
dec["order_size_vs_day_volume"] = {str(k): cell(v) for k, v in m.groupby("adv_bucket", observed=True)}

m["notional_bucket"] = pd.cut(m["notional_vnd"], [0, 5e6, 1e7, 2e7, 5e7, 1e12],
                              labels=["<5tr", "5-10tr", "10-20tr", "20-50tr", ">50tr"])
dec["order_notional"] = {str(k): cell(v) for k, v in m.groupby("notional_bucket", observed=True)}

# chase evidence: did we fill BELOW our own limit (price improvement) or AT it?
m["at_limit"] = (m["slip_vs_limit_bps"] > -0.01)
dec["filled_at_own_limit_vs_better"] = {
    ("at_limit" if k else "better_than_limit"): cell(v) for k, v in m.groupby("at_limit")}
out["decomposition_vs_open"] = dec

# per-ticker, worst offenders by VND
tk = (m.assign(cost=m.slip_vs_open_bps/1e4*m.notional_vnd)
        .groupby("ticker").agg(n=("order_id","size"), notional=("notional_vnd","sum"),
                               cost_vnd=("cost","sum"), mean_bps=("slip_vs_open_bps","mean"))
        .sort_values("cost_vnd", ascending=False))
out["per_ticker_top10_cost"] = json.loads(tk.head(10).to_json(orient="index"))
out["per_ticker_bottom5_cost"] = json.loads(tk.tail(5).to_json(orient="index"))

with open(os.path.join(HERE, "stats.json"), "w") as fh:
    json.dump(out, fh, indent=2, ensure_ascii=False)

pd.set_option("display.width", 250)
print("=== META ==="); print(json.dumps(out["meta"], indent=2))
print("\n=== TOTAL COST (cluster bootstrap, 5000 draws) ===")
for b, v in boot.items():
    print("  %-24s cost=%14s VND  CI95=[%s, %s]  P(cost<=0)=%.3f  wtd=%6.2f bps  ann=%s"%(
        b, f"{v['total_cost_vnd']:,.0f}", f"{v['ci95'][0]:,.0f}", f"{v['ci95'][1]:,.0f}",
        v["p_cost_le_0"], v["notional_wtd_bps"], f"{v['annualised_vnd']:,.0f}"))
print("\n=== range_pos_cost ==="); print(json.dumps(out["range_pos_cost"], indent=2))
print("\n=== DECOMPOSITION (vs session open) ===")
for axis, cells in dec.items():
    print("\n--", axis)
    for k, v in cells.items():
        if v is None: continue
        print("   %-16s n=%3d clu=%3d  mean=%7.2f  cluMean=%7.2f  cluT=%6.2f  wtd=%7.2f  notional=%s"%(
            k, v["n_orders"], v["n_clusters"], v["mean_bps"], v["cluster_mean_bps"],
            v["cluster_t"], v["wtd_bps"], f"{v['notional']:,.0f}"))
print("\n=== per-ticker worst 10 by VND cost vs open ==="); print(tk.head(10).round(1).to_string())
