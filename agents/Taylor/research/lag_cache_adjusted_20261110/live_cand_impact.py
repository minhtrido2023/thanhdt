# B4 (arch-review): tác động cache điều chỉnh lên live_lag_candidates (earnings_events_classified.csv -> pa_HL3 -> qualify).
# ctrl = csv canonical; adjv2 = csv dẫn xuất từ pkl vòng 2. Cùng earnings_surprise_data.pkl. Chạy: $DNA_PYEXE live_cand_impact.py
import sys, json, os, pandas as pd
W = "/home/trido/thanhdt/WorkingClaude"; R = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, W)
import lag_live_schedule as L
a = L.live_lag_candidates(csv_path=f"{W}/data/earnings_events_classified.csv")
b = L.live_lag_candidates(csv_path=f"{R}/derived_v2/earnings_events_classified_adjv2.csv")
k = ["ticker", "quarter", "Release_Date"]
j = a.merge(b, on=k, suffixes=("_c", "_a"))
out = {"events": len(j), "qualify_ctrl": int(j.qualify_c.sum()), "qualify_adj": int(j.qualify_a.sum()),
       "pa_HL3_changed_gt0.5pp": int(((j.pa_HL3_c - j.pa_HL3_a).abs() > 0.5).sum()),
       "only_ctrl_all": sorted(set(j[j.qualify_c & ~j.qualify_a].ticker)), "only_adj_all": sorted(set(j[~j.qualify_c & j.qualify_a].ticker))}
start = pd.Timestamp("2026-07-12")   # cửa sổ 120 ngày của golive tính tới 2026-11-10
w = j[j.Release_Date >= start]
out["window_120d"] = {"events": len(w), "qualify_ctrl": int(w.qualify_c.sum()), "qualify_adj": int(w.qualify_a.sum()),
    "only_ctrl": sorted(set(w[w.qualify_c & ~w.qualify_a].ticker)), "only_adj": sorted(set(w[~w.qualify_c & w.qualify_a].ticker)),
    "tier_changed_among_qualified_both": int(((w.tier_c != w.tier_a) & w.qualify_c & w.qualify_a).sum())}
print(json.dumps(out, indent=1, ensure_ascii=False)); json.dump(out, open(f"{R}/live_cand_impact.json", "w"), indent=1, ensure_ascii=False)
