"""Baseline cho §8 (mô tả, NGOÀI họ 48): (i) P(commit đi xuống từ NEUTRAL/BULL/EX-BULL trong 40 phiên) của một ngày
ngẫu nhiên 2014+; (ii) độ phủ: tỉ lệ ngày có RBEAR14-U1 trong 90 ngày lịch trước ⇒ số commit rời BULL kỳ vọng bị 'phủ' do ngẫu nhiên."""
import json, numpy as np, pandas as pd
from scipy.stats import binom
U1 = pd.read_parquet("u1_daily.parquet"); U1 = U1[U1.time >= "2014-01-01"].reset_index(drop=True)
ep = pd.read_csv("B_episodes.csv", parse_dates=["start", "end"]); E = pd.read_parquet("events.parquet")
rb = E[(E.U == "U1") & (E.type == "RBEAR") & (E.rsi == 14)].time.sort_values()
dn = ep[(ep.outcome == "commit") & ep.committed_from.isin([3, 4, 5]) & (ep.cand < ep.committed_from)].end.sort_values().to_numpy()
pos = {t: i for i, t in enumerate(U1.time)}; dpos = np.array([pos[t] for t in dn if t in pos])
last = len(U1) - 41
p40 = np.mean([((dpos > i) & (dpos <= i + 40)).any() for i in range(last)])
cov = np.mean([((rb < t) & (rb >= t - pd.Timedelta(days=90))).any() for t in U1.time])
lv = ep[(ep.outcome == "commit") & ep.committed_from.isin([4, 5]) & (ep.cand < ep.committed_from)]
obs = int(sum(((rb < c) & (rb >= c - pd.Timedelta(days=90))).any() for c in lv.end))
n_hit40 = 13 - 6
out = dict(p_random_day_down_commit_within40=round(float(p40), 3), RBEAR_followed_within40=f"{n_hit40}/13",
           p_binom_ge=round(float(binom.sf(n_hit40 - 1, 13, p40)), 3),
           coverage_90d=round(float(cov), 3), commits_leaving_BULL=len(lv), covered_obs=obs,
           covered_expected=round(float(cov * len(lv)), 2), p_binom_cover_ge=round(float(binom.sf(obs - 1, len(lv), cov)), 3),
           note="mô tả, ngoài họ 48, N=13/11, không vào tiêu chí; không hiệu chỉnh đa kiểm định")
json.dump(out, open("dt5g_baseline.json", "w"), indent=1); print(out)
