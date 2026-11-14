"""B: đếm candidate DT 4-gate lịch sử 2014→nay (N cho §6). Replay = dt_gate_hazard_research.extract_episodes
(cùng hàm dna_report.get_dt_gate_clock dùng) trên nền v3.4b (vnindex_5state_tam_quan_v34b_clean, cache local).
Self-check: dt_4gate(replay) vs vnindex_5state_dt5g_live.state_raw (DT4) — phải 0 diff."""
import sys, json
import numpy as np, pandas as pd
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor")
from dt_gate_hazard_research import extract_episodes, dt_4gate
BQC = "/home/trido/thanhdt/WorkingClaude/data/bq_cache"
b = pd.read_parquet(f"{BQC}/vnindex_5state_tam_quan_v34b_clean.parquet")
b["time"] = pd.to_datetime(b["time"]); b = b[b.time >= "2014-01-01"].sort_values("time").reset_index(drop=True)
raw = b["state"].astype(int).values; times = b["time"].values
dt4 = dt_4gate(raw)
live = pd.read_parquet(f"{BQC}/vnindex_5state_dt5g_live.parquet"); live["time"] = pd.to_datetime(live["time"])
chk = pd.DataFrame({"time": b.time, "dt4": dt4}).merge(live[["time", "state", "state_raw"]], on="time")
out = {"base_rows": len(b), "base_first": str(b.time.iloc[0].date()), "base_last": str(b.time.iloc[-1].date()),
       "selfcheck_overlap": len(chk), "diff_dt4_vs_live_state_raw": int((chk.dt4 != chk.state_raw).sum()),
       "diff_dt4_vs_live_state(DT5G)": int((chk.dt4 != chk.state).sum()),
       "transitions_base": int((np.diff(raw) != 0).sum()), "transitions_dt4": int((np.diff(dt4) != 0).sum()),
       "transitions_dt5g_live_state": int((live.sort_values("time").state.diff().fillna(0) != 0).sum())}
ep = extract_episodes(times, raw); ep["start"] = pd.to_datetime(ep["start"]); ep["year"] = ep.start.dt.year
out["episodes_total"] = len(ep)
out["by_need_outcome"] = {f"need{k[0]}_{k[1]}": int(v) for k, v in ep.groupby(["need", "outcome"]).size().items()}
# candidate "đáng hỏi" theo §6: chạm ≥5/10 hoặc ≥15/25
q = ep[((ep.need == 10) & (ep.length >= 5)) | ((ep.need == 25) & (ep.length >= 15))]
out["qualifying_k5of10_or_k15of25"] = len(q)
out["qualifying_by_need_outcome"] = {f"need{k[0]}_{k[1]}": int(v) for k, v in q.groupby(["need", "outcome"]).size().items()}
out["qualifying_commit_rate"] = round(float((q.outcome == "commit").mean()), 3)
out["qualifying_by_year"] = {int(k): int(v) for k, v in q.groupby("year").size().items()}
out["qualifying_IS_2014_2019"] = int((q.year <= 2019).sum()); out["qualifying_OOS_2020p"] = int((q.year >= 2020).sum())
sn = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EXBULL"}
out["qualifying_by_from_to"] = {f"{sn[a]}->{sn[c]}": int(v) for (a, c), v in q.groupby(["committed_from", "cand"]).size().items()}
# rời BULL/EX-BULL (sự kiện §3.4)
lv = ep[(ep.outcome == "commit") & ep.committed_from.isin([4, 5]) & (ep.cand < ep.committed_from)]
out["commits_leaving_BULL_EXBULL"] = len(lv); out["commits_leaving_dates"] = [str(x.date()) for x in pd.to_datetime(lv.end)]
ep.to_csv("B_episodes.csv", index=False)
json.dump(out, open("B_result.json", "w"), indent=1)
print(json.dumps(out, indent=1))
