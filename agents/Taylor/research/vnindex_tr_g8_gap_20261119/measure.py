"""Đo tần suất ứng viên G8-mới trên 2026: mỗi phiên t, mã thuộc bảng sàn HOSE (latest) không vào rổ do
(a) có giá t-1,t nhưng không có OShares nào tới t-1 (trong cửa sổ), (b) không có dòng nào trong `ticker` tới t."""
import sys, pickle, collections
import pandas as pd, numpy as np
W = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-vnindex-tr-g8-gap-20261119/bin"
sys.path.insert(0, W)
import vnindex_total_return as v
D = sys.path[0] if False else __file__.rsplit("/", 1)[0]
inp = pickle.load(open(f"{D}/bq_inputs_20251103.pkl", "rb"))
panel, _ = v._coerce_inputs(inp["panel"], inp["ca"])
fs = pd.DataFrame(inp["first_seen"]); fs["first_time"] = pd.to_datetime(fs.first_time)
first = fs.set_index("ticker").first_time
sp = v.load_membership()
idx = panel[panel.ticker == "VNINDEX"].set_index("time").Price.sort_index()
sess = list(idx.index)
s = panel[panel.ticker != "VNINDEX"].sort_values(["ticker", "time"]).copy()
g = s.groupby("ticker")
s["t1"] = g.time.shift(1); s["P1"] = g.Price.shift(1)
s["S1_ff"] = g.OShares.transform(lambda x: x.ffill()).groupby(s.ticker).shift(1)
s["npx"] = g.Price.transform(lambda x: x.gt(0).cumsum())
prev = dict(zip(sess[1:], sess[:-1]))
bt = {k: d for k, d in s.groupby("time")}
a_rows, b_rows = [], []
for t in sess:
    if t < pd.Timestamp("2026-01-02"): continue
    mem = {k for k, ss in sp.items() if any(pd.Timestamp(a) <= t < pd.Timestamp(b) for a, b in ss)}
    d = bt.get(t, pd.DataFrame(columns=s.columns)).set_index("ticker")
    for k in mem:
        if k in d.index:
            r = d.loc[k]
            if r.t1 == prev.get(t) and r.P1 > 0 and r.Price > 0 and not (r.S1_ff > 0):
                a_rows.append((t.date(), k, int(r.npx)))
        else:
            f = first.get(k)
            if f is None or f > t:
                st = min(pd.Timestamp(a) for a, b in sp[k] if pd.Timestamp(a) <= t)
                nlist = sum(1 for x in sess if st <= x <= t)
                b_rows.append((t.date(), k, nlist, None if f is None else f.date()))
A = pd.DataFrame(a_rows, columns=["date", "ticker", "n_px"]); B = pd.DataFrame(b_rows, columns=["date", "ticker", "n_listed_sess", "first_seen"])
A.to_csv(f"{D}/cand_a_2026.csv", index=False); B.to_csv(f"{D}/cand_b_2026.csv", index=False)
n = sum(1 for t in sess if t >= pd.Timestamp("2026-01-02"))
print("phiên 2026:", n)
print("(a) theo mã:", A.groupby("ticker").agg(first=("date", "min"), last=("date", "max"), n=("date", "size"), npx_min=("n_px", "min")).to_string())
print("(b) theo mã:", B.groupby("ticker").agg(first=("date", "min"), last=("date", "max"), n=("date", "size"), nl_min=("n_listed_sess", "min"), fs=("first_seen", "first")).to_string())
