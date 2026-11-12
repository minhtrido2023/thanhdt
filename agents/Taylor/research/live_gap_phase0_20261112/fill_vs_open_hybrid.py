#!/usr/bin/env python3
"""GD0 viec 4 — fill-vs-open sau HYBRID go-live (2026-08-26). Cung phep do execution_alpha_20260925 (extract_fills_v2/slippage_v2 = ban sao doi ten file).
CONTROL: <=2026-09-25 phai tai tao N=326, mean vs open 5.52, sd 94.58 (FINDINGS.md 2a).
Cum doc lap = (phien x ma); bootstrap theo cum. Nguong rollback: mean > +22bps (current_ops.md:66). Dau: + = te cho minh.
Chay: /home/trido/thanhdt/wc_venv/bin/python fill_vs_open_hybrid.py"""
import os, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(20261112)
m = pd.read_csv(f"{HERE}/slippage_all.csv"); m["d"] = pd.to_datetime(m.trans_date)
B = "slip_vs_open_bps"
def stat(s, label):
    s = s.dropna(subset=[B]); x = s[B].values; n = len(x)
    if n < 3: return dict(label=label, n_orders=n)
    cl = s.groupby(["trans_date", "ticker"])[B].mean(); gid = s.groupby(["trans_date", "ticker"]).ngroup().values
    G = np.unique(gid); idx = {g: np.where(gid == g)[0] for g in G}; w = s.notional_vnd.values
    bm, bw = [], []
    for _ in range(5000):
        p = rng.choice(G, len(G)); sel = np.concatenate([idx[g] for g in p])
        bm.append(x[sel].mean()); bw.append(np.average(x[sel], weights=w[sel]))
    r = dict(label=label, n_orders=n, n_clusters=int(len(cl)), n_days=int(s.trans_date.nunique()),
             mean_bps=round(x.mean(), 2), sd_order=round(x.std(ddof=1), 2), median=round(float(np.median(x)), 2),
             wtd_mean_bps=round(float(np.average(x, weights=w)), 2),
             cluster_mean=round(cl.mean(), 2), cluster_sd=round(cl.std(ddof=1), 2),
             ci95_mean_cluster=[round(np.percentile(bm, 2.5), 1), round(np.percentile(bm, 97.5), 1)],
             ci95_wtd_cluster=[round(np.percentile(bw, 2.5), 1), round(np.percentile(bw, 97.5), 1)],
             P_mean_gt_22=round(float((np.array(bm) > 22).mean()), 3), P_wtd_gt_22=round(float((np.array(bw) > 22).mean()), 3),
             notional_vnd=round(float(s.notional_vnd.sum())))
    return r
res = []
ctrl = m[m.d <= "2026-09-25"]
res.append(stat(ctrl, "CONTROL <=09-25 (ky vong N=326, mean 5.52, sd 94.58)"))
pre = m[(m.d < "2026-08-26")]; post = m[m.d >= "2026-08-26"]
res.append(stat(pre, "PRE-HYBRID 07-01..08-25")); res.append(stat(post, "POST-HYBRID 08-26..11-11 (all)"))
for sd, nm in (("NB", "BUY"), ("NS", "SELL")):
    res.append(stat(post[post.side == sd], f"POST {nm}"))
    res.append(stat(pre[pre.side == sd], f"PRE {nm}"))
for a in ("SpaceX", "ZaloPay"): res.append(stat(post[post.account == a], f"POST {a}"))
for b, g in post.groupby("tod_bucket"): res.append(stat(g, f"POST tod {b}"))
# theo khung ~10 phien
post = post.copy(); days = sorted(post.trans_date.unique()); blk = {d: i // 10 for i, d in enumerate(days)}
post["blk"] = post.trans_date.map(blk)
for k, g in post.groupby("blk"): res.append(stat(g, f"POST khung10phien#{k} {g.trans_date.min()}..{g.trans_date.max()}"))
json.dump(res, open(f"{HERE}/fill_vs_open_stats.json", "w"), indent=1, ensure_ascii=False)
pd.DataFrame(res).to_csv(f"{HERE}/fill_vs_open_stats.csv", index=False)
pd.set_option("display.width", 300); pd.set_option("display.max_colwidth", 60)
print(pd.DataFrame(res)[["label","n_orders","n_clusters","n_days","mean_bps","sd_order","wtd_mean_bps","cluster_mean","ci95_mean_cluster","ci95_wtd_cluster","P_mean_gt_22","P_wtd_gt_22"]].to_string())
