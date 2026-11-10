# Tái sinh earnings_events_classified.csv + lag_edge_health.csv từ px (đúng logic refresh step [4] +
# edge_health_monitor.lag_edge_health), cho CTRL (pkl canonical) và ADJ (pkl adjusted). So w_LAG.
# Chạy: $DNA_PYEXE measure_edge.py  (threads=1). Không ghi data/ canonical (LAG_EDGE_OUT + WORKDIR sandbox).
import os, sys, hashlib, json, shutil, pandas as pd, numpy as np
W = "/home/trido/thanhdt/WorkingClaude"; R = os.path.dirname(os.path.abspath(__file__)); D = f"{R}/derived"
sys.path.insert(0, W)
import edge_health_monitor as m
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()
ev_raw = pd.read_pickle(f"{W}/data/earnings_events.pkl"); ev_raw["Release_Date"] = pd.to_datetime(ev_raw["Release_Date"])
# đúng code refresh_lagged_caches.py step [4] (main) — chép nguyên, chỉ tham số hoá px
def classify(npr, pre, rel, post):
    if pd.isna(npr): return "NO_NPR"
    good, bad = npr >= 15, npr <= -15
    if good:
        if pre >= 10 and rel <= -2: return "LEAK_RUNUP_POS"
        if abs(pre) < 5 and rel >= 3: return "EFFICIENT_POS"
        if abs(pre) < 5 and abs(rel) < 3 and post >= 5: return "LAGGED_POS"
        if pre >= 10 and rel >= 0 and post < 0: return "LEAK_RUNUP_POS"
    if bad:
        if pre <= -10 and rel >= 2: return "LEAK_DUMP_NEG"
        if abs(pre) < 5 and rel <= -3: return "EFFICIENT_NEG"
        if abs(pre) < 5 and abs(rel) < 3 and post <= -5: return "LAGGED_NEG"
    return "NOISE"
def events_cls(px):
    piv = px.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
    dates = np.array(piv.index); cols = set(piv.columns)
    def off(tk, ref, o):
        pos = np.searchsorted(dates, np.datetime64(ref), side="right") - 1
        if pos < 0: return np.nan
        t = pos + o
        if t < 0 or t >= len(dates): return np.nan
        return piv.iloc[t][tk]
    rows = []
    for _, r in ev_raw.iterrows():
        tk, rdt = r["ticker"], r["Release_Date"]
        if tk not in cols: continue
        a = off(tk, rdt, -30); b = off(tk, rdt, -1); c = off(tk, rdt, 5); d = off(tk, rdt, 30)
        if any(pd.isna(x) for x in [a, b, c, d]): continue
        if min(a, b, c, d) <= 0: continue
        pre = (b/a-1)*100; rel = (c/b-1)*100; post = (d/c-1)*100
        npr = r["NP_R"]*100 if pd.notna(r["NP_R"]) else np.nan
        rows.append({"ticker": tk, "quarter": r["quarter"], "Release_Date": rdt, "NP_R": npr,
                     "Rev_YoY": r["Revenue_YoY_P0"]*100 if pd.notna(r["Revenue_YoY_P0"]) else np.nan,
                     "pre_ret": pre, "rel_ret": rel, "post_ret": post, "pattern": classify(npr, pre, rel, post)})
    return pd.DataFrame(rows)
out = {}
for tag, p in [("ctrl", f"{W}/data/earnings_px.pkl"), ("adj", f"{R}/earnings_px_adj.pkl")]:
    px = pd.read_pickle(p); px["time"] = pd.to_datetime(px.time)
    wd = f"{D}/wd_{tag}"; os.makedirs(wd + "/data", exist_ok=True)
    shutil.copy(p, wd + "/data/earnings_px.pkl")
    ev = events_cls(px); evp = f"{D}/earnings_events_classified_{tag}.csv"; ev.to_csv(evp, index=False)
    shutil.copy(evp, wd + "/data/earnings_events_classified.csv")
    m.WORKDIR = wd; os.environ["LAG_EDGE_OUT"] = f"{D}/lag_edge_health_{tag}.csv"
    res = m.lag_edge_health()
    out[tag] = {**res, "events_md5": md5(evp), "edge_md5": md5(f"{D}/lag_edge_health_{tag}.csv"), "n_events": len(ev)}
# control fidelity vs canonical files
out["ctrl_vs_canonical"] = {
    "events_csv_identical": md5(f"{D}/earnings_events_classified_ctrl.csv") == md5(f"{W}/data/earnings_events_classified.csv"),
    "edge_csv_identical": md5(f"{D}/lag_edge_health_ctrl.csv") == md5(f"{W}/data/lag_edge_health.csv"),
    "canonical_events_md5": md5(f"{W}/data/earnings_events_classified.csv"), "canonical_edge_md5": md5(f"{W}/data/lag_edge_health.csv")}
# pattern changes
a = pd.read_csv(f"{D}/earnings_events_classified_ctrl.csv"); b = pd.read_csv(f"{D}/earnings_events_classified_adj.csv")
j = a.merge(b, on=["ticker", "quarter", "Release_Date"], how="outer", suffixes=("_c", "_a"), indicator=True)
jj = j[j._merge == "both"]
out["events"] = {"both": len(jj), "only_ctrl": int((j._merge == "left_only").sum()), "only_adj": int((j._merge == "right_only").sum()),
    "pattern_changed": int((jj.pattern_c != jj.pattern_a).sum()), "lagged_pos_ctrl": int((a.pattern == "LAGGED_POS").sum()),
    "lagged_pos_adj": int((b.pattern == "LAGGED_POS").sum()), "post_ret_absdiff_gt1pp": int(((jj.post_ret_c - jj.post_ret_a).abs() > 1).sum())}
# w_LAG history (good states): mean12 by known_date, ffill onto trading days, tilt 0.65 if >= 4.0 (EDGE_THR pt_v22/pt_v23)
days = pd.DatetimeIndex(sorted(pd.read_pickle(f"{W}/data/earnings_px.pkl").time.unique()))
days = days[(days >= "2014-01-02") & (days.dayofweek < 5)]
s = {}
for tag in ("ctrl", "adj"):
    e = pd.read_csv(f"{D}/lag_edge_health_{tag}.csv", parse_dates=["known_date"]).drop_duplicates("known_date").set_index("known_date").sort_index()["mean12"]
    s[tag] = e.reindex(days, method="ffill")
w = pd.DataFrame({k: np.where(v >= 4.0, 0.65, 0.50) for k, v in s.items()}, index=days)
w[s["ctrl"].isna().values | s["adj"].isna().values] = np.nan
dif = w[(w.ctrl != w.adj) & w.notna().all(axis=1)]
w.assign(m12_ctrl=s["ctrl"].values, m12_adj=s["adj"].values).to_csv(f"{D}/w_lag_history.csv")
runs = []
if len(dif):
    g = (dif.index.to_series().diff() > pd.Timedelta(days=7)).cumsum()
    for _, x in dif.groupby(g.values): runs.append([str(x.index[0].date()), str(x.index[-1].date()), len(x), float(x.ctrl.iloc[0]), float(x.adj.iloc[0])])
out["w_lag_history"] = {"days": int(w.notna().all(axis=1).sum()), "days_differ": len(dif), "runs[start,end,n,ctrl,adj]": runs,
    "first_day": str(days[0].date()), "last_day": str(days[-1].date())}
json.dump(out, open(f"{R}/edge_results.json", "w"), indent=1, ensure_ascii=False, default=str)
print(json.dumps(out, indent=1, ensure_ascii=False, default=str))
