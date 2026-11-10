# VÒNG 2 (chỉ chân adjv2): tái sinh earnings_events_classified.csv + lag_edge_health.csv từ px (đúng logic refresh step [4] +
# edge_health_monitor.lag_edge_health), cho CTRL (pkl canonical) và ADJ (pkl adjusted). So w_LAG.
# Chạy: $DNA_PYEXE measure_edge.py  (threads=1). Không ghi data/ canonical (LAG_EDGE_OUT + WORKDIR sandbox).
import os, sys, hashlib, json, shutil, pandas as pd, numpy as np
W = "/home/trido/thanhdt/WorkingClaude"; R = os.path.dirname(os.path.abspath(__file__)); D = f"{R}/derived_v2"
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
os.makedirs(D, exist_ok=True)
out = {}
for tag, p in [("adjv2", f"{R}/v2/earnings_px_adj.pkl")]:
    px = pd.read_pickle(p); px["time"] = pd.to_datetime(px.time)
    wd = f"{D}/wd_{tag}"; os.makedirs(wd + "/data", exist_ok=True)
    shutil.copy(p, wd + "/data/earnings_px.pkl")
    ev = events_cls(px); evp = f"{D}/earnings_events_classified_{tag}.csv"; ev.to_csv(evp, index=False)
    shutil.copy(evp, wd + "/data/earnings_events_classified.csv")
    m.WORKDIR = wd; os.environ["LAG_EDGE_OUT"] = f"{D}/lag_edge_health_{tag}.csv"
    res = m.lag_edge_health()
    out[tag] = {**res, "events_md5": md5(evp), "edge_md5": md5(f"{D}/lag_edge_health_{tag}.csv"), "n_events": len(ev)}
json.dump(out, open(f"{R}/edge_results_v2.json", "w"), indent=1, ensure_ascii=False, default=str); print(json.dumps(out, indent=1, ensure_ascii=False, default=str))
