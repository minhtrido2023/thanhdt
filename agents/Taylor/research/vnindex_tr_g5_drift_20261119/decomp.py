"""Tái lập k2_synth_pr + phân rã lệch G5 theo mã. Chỉ đọc."""
import sys, os, pickle, json
import numpy as np, pandas as pd
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/bin")
import vnindex_total_return as v
D = os.path.dirname(os.path.abspath(__file__))
inp = pickle.load(open(f"{D}/bq_inputs_20260504.pkl", "rb"))
panel, ca = v._coerce_inputs(inp["panel"], inp["ca"])
MEM = sys.argv[1] if len(sys.argv) > 1 else v.MEMBERSHIP_LATEST
spells = v.load_membership(MEM)
divs = v.dividends(ca)
idx = panel[panel.ticker == "VNINDEX"].set_index("time").Price.sort_index()
pn = panel[panel.ticker != "VNINDEX"]
day = v.div_yield_daily(pn, spells, divs, idx)
ser = pd.read_csv("/home/trido/thanhdt/WorkingClaude/data/benchmark/vnindex_tr_daily.csv", parse_dates=["date"]).set_index("date")
cmp = pd.DataFrame({"csv": ser.k2_synth_pr, "re": day.k2_synth_pr}).dropna()
cmp = cmp["2026-06-01":]
print("replicate max|diff| bp:", (cmp.csv - cmp.re).abs().max() * 1e4, "n", len(cmp))
# ---- per-ticker frame (same filters as div_yield_daily)
s = pn.copy(); s["time"] = pd.to_datetime(s.time); s = s.sort_values(["ticker", "time"]).reset_index(drop=True)
g = s.groupby("ticker")
for a, b in (("P1", "Price"), ("C1", "Close"), ("S1", "OShares"), ("t1", "time")):
    s[a] = g[b].shift(1)
s["hose"] = False
for code, rows in s.groupby("ticker").groups.items():
    sp = spells.get(code)
    if not sp: continue
    tt = s.loc[rows, "time"].values; m = np.zeros(len(tt), bool)
    for a, b in sp: m |= (tt >= np.datetime64(a)) & (tt < np.datetime64(b))
    s.loc[rows, "hose"] = m
dv = divs.copy(); dv["time"] = pd.to_datetime(dv.time)
s = s.merge(dv, on=["ticker", "time"], how="left"); s["div"] = s["div"].fillna(0.0)
prev_idx = pd.Series(idx.index[:-1], index=idx.index[1:])
s["t1_ok"] = s.t1.values == s.time.map(prev_idx).values
u = s[s.hose & s.t1_ok & s.P1.gt(0) & s.Price.gt(0) & s.S1.gt(0)].copy()
u["mc1"] = u.P1 * u.S1
u["dy"] = np.where(u["div"] / u.P1 > v.DY_CORRUPT, 0, u["div"] / u.P1)
u["pr"] = u.Close / u.C1 - 1 - u.dy          # giá-thuần theo cách synth ngầm định
u["w"] = u.mc1 / u.groupby("time").mc1.transform("sum")
u.to_pickle(f"{D}/u_frame.pkl")
off = idx.pct_change()
day["off"] = off.reindex(day.index); day["d"] = day.k2_synth_pr - day.off
day.to_pickle(f"{D}/day_frame.pkl")
print(day["2026-08-14":"2026-11-11"].d.describe())
