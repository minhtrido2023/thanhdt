# C2 mục 3: quy nguyên theo mã cho delta live (HTT,PHP rời / KLB,PHR vào) + kiểm 7/11 mã đã bị lag_liq_excluded.
# Chạy: $DNA_PYEXE attrib_4.py  (đọc csv ctrl/adjv2 ở worktree research 11-10 + csv live hiện hành + golive status)
import sys, json, os, glob, pickle, numpy as np, pandas as pd
W = "/home/trido/thanhdt/WorkingClaude"; sys.path.insert(0, W); import lag_live_schedule as L
RW = f"{W}/mike/agents/Taylor/wt-mike-lagadj-1110/agents/Taylor/research/lag_cache_adjusted_20261110"
CSV = {"ctrl": f"{RW}/derived/earnings_events_classified_ctrl.csv", "adjv2": f"{RW}/derived_v2/earnings_events_classified_adjv2.csv",
       "live_now": f"{W}/data/earnings_events_classified.csv"}
ELEVEN = ["HTT", "PHP", "PMP", "TMG", "BSP", "DMN", "KLB", "LAW", "NBC", "PHR", "TPC"]
START = pd.Timestamp("2026-07-12")   # = cửa sổ 120 ngày dùng trong live_cand_impact.json (tới 11-10)
px = pickle.load(open(f"{W}/data/earnings_px.pkl", "rb")); td = np.array(sorted(pd.to_datetime(px[px.ticker == "VNINDEX"].time.unique() if (px.ticker == "VNINDEX").any() else px.time.unique())), dtype="datetime64[ns]")
def entry(rd):
    pos = int(np.searchsorted(td, np.datetime64(rd), side="right")) - 1; t = pos + 5
    return str(pd.Timestamp(td[t]).date()) if 0 <= pos and t < len(td) else f"T+{t-(len(td)-1)} phiên tới"
st = json.load(open(f"{W}/data/golive_v23_status.json"))
liq = {d["ticker"]: d["reason"] for d in st.get("lag_liq_excluded", [])}
rows = []
tabs = {k: L.live_lag_candidates(start=START, csv_path=v).set_index(["ticker", "quarter", "Release_Date"]) for k, v in CSV.items()}
keys = sorted(set().union(*[set(t[t.index.get_level_values(0).isin(ELEVEN)].index) for t in tabs.values()]))
for k in keys:
    r = {"ticker": k[0], "quarter": k[1], "release": str(k[2].date()), "entry_T+5": entry(k[2])}
    for n, t in tabs.items():
        r[f"pa_HL3_{n}"] = round(float(t.loc[k, "pa_HL3"]), 2) if k in t.index and pd.notna(t.loc[k, "pa_HL3"]) else None
        r[f"q_{n}"] = bool(t.loc[k, "qualify"]) if k in t.index else None
    r["prior_n_good_ctrl"] = int(tabs["ctrl"].loc[k, "prior_n_good"]) if k in tabs["ctrl"].index else None
    r["lag_liq_excluded_1112"] = liq.get(k[0])
    rows.append(r)
df = pd.DataFrame(rows); pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
print(df.to_string(index=False))
print("status signal_date", st.get("signal_date"), "| n_lag_liq_excluded", len(liq))
print("11 mã ∩ lag_liq_excluded 11-12:", sorted(set(ELEVEN) & set(liq)))
df.to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "attrib_4.csv"), index=False)
