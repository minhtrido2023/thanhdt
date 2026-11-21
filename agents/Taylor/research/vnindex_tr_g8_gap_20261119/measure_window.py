"""Biến thể production: cửa sổ dựng ~11 phiên (anchor = 6 dòng sealed lùi). (b') = thành viên HOSE niêm yết
>= N phiên, KHÔNG có dòng nào trong cửa sổ [t-10 phiên, t]; (a') = có giá t-1,t, không OShares nào trong cửa sổ."""
import sys, pickle
import pandas as pd
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-vnindex-tr-g8-gap-20261119/bin")
import vnindex_total_return as v
D = __file__.rsplit("/", 1)[0]
inp = pickle.load(open(f"{D}/bq_inputs_20251103.pkl", "rb"))
panel, _ = v._coerce_inputs(inp["panel"], inp["ca"])
sp = v.load_membership()
sess = sorted(panel[panel.ticker == "VNINDEX"].time.unique())
px = panel[panel.ticker != "VNINDEX"]
WIN, N = 11, 5
ra, rb = [], []
for i, t in enumerate(sess):
    if t < pd.Timestamp("2026-01-02") or i < WIN: continue
    w = px[(px.time >= sess[i - WIN + 1]) & (px.time <= t)]
    have = set(w.ticker)
    mem = [k for k, ss in sp.items() if any(pd.Timestamp(a) <= t < pd.Timestamp(b) for a, b in ss)]
    for k in mem:
        st = max(pd.Timestamp(a) for a, b in sp[k] if pd.Timestamp(a) <= t)
        nl = sum(1 for x in sess if st <= x <= t)
        if k not in have and nl >= N:
            rb.append((t.date(), k))
        elif k in have:
            wk = w[w.ticker == k].sort_values("time")
            if len(wk) >= 2 and wk.time.iloc[-1] == t and wk.time.iloc[-2] == sess[i - 1] and \
                    not (wk.OShares.iloc[:-1] > 0).any() and (wk.Price > 0).sum() >= N:
                ra.append((t.date(), k))
A = pd.DataFrame(ra, columns=["date", "ticker"]); B = pd.DataFrame(rb, columns=["date", "ticker"])
A.to_csv(f"{D}/cand_a_window.csv", index=False); B.to_csv(f"{D}/cand_b_window.csv", index=False)
for nm, X in (("a'", A), ("b'", B)):
    print(nm, "phiên có >=1 mã:", X.date.nunique(), "| theo mã:")
    print(X.groupby("ticker").date.agg(["min", "max", "size"]).to_string())
