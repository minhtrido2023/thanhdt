"""Waterfall vòng 3 (job Taylor_20261112_122855): mỗi TK, cold và warm-live-scale tách riêng, thêm bậc 'lịch park live'.
Lợi suất kỳ engine đọc từ exposure_decomp3.csv (ky, day1=bfill); live = TWR GĐ0; hurdle PIT GĐ0."""
import pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, hashlib, glob, os
R = os.path.dirname(os.path.abspath(__file__))
T = pd.read_csv(f"{R}/exposure_decomp3.csv"); K = T[(T.ky == "ky") & (T.day1 == "bfill")]
HUR = {"SpaceX": 2.548, "ZaloPay": 2.455}
TAG = {("SpaceX", "cold_p0"): "c3_SXcold_p0", ("SpaceX", "cold_park"): "c3_SXcold_ps", ("SpaceX", "warm_p0"): "c3_SXwarm_p0",
       ("SpaceX", "warm_park"): "c3_SXwarm_ps", ("ZaloPay", "cold_p0"): "c3_Zcold_p0", ("ZaloPay", "cold_park"): "c3_Zcold_ps",
       ("ZaloPay", "warm_p0"): "c3_Zwarm_p0", ("ZaloPay", "warm_park"): "c3_Zwarm_ps"}
LAB = {"cold_p0": "W1 cold park=0", "cold_park": "W1P cold + lịch park live", "warm_p0": "W1 warm-live park=0",
       "warm_park": "W1P warm-live + lịch park live"}
rows = []
for acct in ["SpaceX", "ZaloPay"]:
    g = K[K.TK == acct]
    for _, x in g.iterrows():
        f = glob.glob(f"{R}/ledgers/*_exp_exp_gap_{TAG[(acct, x.engine)]}_univpit*.csv")[0]
        rows.append(dict(TK=acct, regime=x.engine.split("_")[0], buoc=LAB[x.engine], r_pct=round(x.eng_r, 3),
                         vs_hurdle=round(x.eng_r - HUR[acct], 2), live_minus_engine=round(x.gap, 2),
                         md5=hashlib.md5(open(f, "rb").read()).hexdigest()))
    rows.append(dict(TK=acct, regime="live", buoc="LIVE", r_pct=round(g.live_r.iloc[0], 3), vs_hurdle=round(g.live_r.iloc[0] - HUR[acct], 2),
                     live_minus_engine=None, md5="GĐ0 vs_savings_table.csv"))
W = pd.DataFrame(rows); W.to_csv(f"{R}/waterfall.csv", index=False); print(W.to_string(index=False))
fig, ax = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)
for a, acct in zip(ax, ["SpaceX", "ZaloPay"]):
    w = W[W.TK == acct]; c = ["#8aa" if "park=0" in s else ("#c66" if "LIVE" in s else "#46a") for s in w.buoc]
    a.bar(range(len(w)), w.r_pct, color=c); a.axhline(HUR[acct], ls="--", c="k", lw=1); a.axhline(0, c="grey", lw=.5)
    a.set_xticks(range(len(w))); a.set_xticklabels(w.buoc, rotation=30, ha="right", fontsize=8)
    a.set_title(f"{acct}: lợi suất kỳ % (đường đứt = hurdle tiết kiệm PIT {HUR[acct]}%)", fontsize=9)
    for i, v in enumerate(w.r_pct): a.text(i, v, f"{v:+.2f}", ha="center", va="bottom" if v >= 0 else "top", fontsize=8)
plt.tight_layout(); plt.savefig(f"{R}/waterfall.png", dpi=110)
