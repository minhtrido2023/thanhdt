"""Phần dư G5 sau khi dựng lại (rổ hôm nay): phân rã theo mã + kiểm giả thuyết trọng số."""
import pandas as pd, numpy as np
D = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/vnindex_tr_g5_drift_20261119"
u = pd.read_pickle(f"{D}/u_frame_latest.pkl"); a = pd.read_pickle(f"{D}/day_frame_latest.pkl")
off = a.off; W = ("2026-08-15", "2026-11-11")
uw = u[(u.time >= W[0]) & (u.time <= W[1])].copy()
G = lambda k: (np.prod(1 + k) - np.prod(1 + off[W[0]:W[1]])) * 100
synth = lambda x: (x.pr * x.mc1).groupby(x.time).sum() / x.groupby("time").mc1.sum()
print("G5 rebuild", round(G(synth(uw)), 3))
# 1) leave-one-out theo mã: ảnh hưởng của việc bỏ mã i lên G5
base = G(synth(uw)); top = uw.groupby("ticker").mc1.mean().sort_values(ascending=False).index[:40]
loo = {t: base - G(synth(uw[uw.ticker != t])) for t in top}
print("LOO (G5 giảm bao nhiêu pp nếu bỏ mã):"); print(pd.Series(loo).sort_values().round(3).head(6).to_string()); print(pd.Series(loo).sort_values().round(3).tail(6).to_string())
# 2) trọng số "liên tục": cap chỉ trôi theo giá — J = (P*S)/(P1*S1)/(1+pr)
uw["S"] = uw.OShares; uw["J"] = (uw.Price * uw.S) / (uw.P1 * uw.S1) / (1 + uw.pr)
ev = uw[(uw.J - 1).abs() > 0.02].copy(); ev["mcT"] = ev.mc1 / 1e12
print("cap-jump events |J-1|>2%, mc1>5T:"); print(ev[ev.mcT > 5][["time","ticker","Price","P1","Close","C1","S","S1","J","mcT"]].round(3).to_string())
# 3) synth với trọng số buy-and-hold từ 2026-08-14 (bỏ mọi bước nhảy vốn hoá không do giá)
u0 = u[u.time <= W[1]].copy()
cap0 = u0[u0.time == "2026-08-14"].set_index("ticker").eval("Price*OShares")
rows = []
for t, x in uw.groupby("time"): rows.append(x)
growth = (1 + uw.pivot(index="time", columns="ticker", values="pr").fillna(0)).cumprod().shift(1).fillna(1)
bh = growth.mul(cap0.reindex(growth.columns), axis=1)
pr = uw.pivot(index="time", columns="ticker", values="pr")
mask = pr.notna() & bh.notna()
k_bh = (pr.where(mask) * bh.where(mask)).sum(1) / bh.where(mask).sum(1)
print("G5 buy-and-hold weights (rổ cố định 08-14):", round(G(k_bh), 3))
# 4) tương quan lệch ngày với thị trường / n đổi / ngày có cổ tức
d = (synth(uw) - off[W[0]:W[1]]) * 1e4
X = pd.DataFrame({"d": d, "off": off * 100, "absoff": off.abs() * 100, "dn": a.n.diff().abs(), "y": a.y * 1e4}).loc[W[0]:W[1]]
print(X.corr().d.round(3).to_string())
b = np.polyfit(X.off, X.d, 1); print("hồi quy d(bp)= %.3f*off(%%) + %.3f" % tuple(b))
X.to_csv(f"{D}/daily_diff_rebuild.csv")
