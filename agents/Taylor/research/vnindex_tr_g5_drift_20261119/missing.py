"""Mã có trong bảng sàn HOSE (vintage latest) ngày t nhưng KHÔNG vào rổ synth — lý do + vốn hoá ước."""
import sys, pickle, datetime as dt
import pandas as pd, numpy as np
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/bin")
import vnindex_total_return as v
D = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/vnindex_tr_g5_drift_20261119"
inp = pickle.load(open(f"{D}/bq_inputs_20260504.pkl", "rb"))
panel, _ = v._coerce_inputs(inp["panel"], inp["ca"])
sp = v.load_membership(); u = pd.read_pickle(f"{D}/u_frame_latest.pkl")
for day in ("2026-09-15", "2026-11-11"):
    t = dt.date.fromisoformat(day)
    mem = {k for k, s in sp.items() if any(a <= t < b for a, b in s)}
    inb = set(u[u.time == day].ticker)
    p = panel[panel.time == day].set_index("ticker")
    miss = sorted(mem - inb)
    rows = []
    for k in miss:
        if k in p.index:
            r = p.loc[k]; why = "no OShares" if not (r.OShares > 0) else "t-1/price filter"
            mc = (r.Price * r.OShares) / 1e12 if r.OShares > 0 else np.nan
        else:
            why, mc = "no ticker row", np.nan
        rows.append((k, why, mc))
    m = pd.DataFrame(rows, columns=["ticker", "why", "mcT"])
    print(day, "HOSE members", len(mem), "in basket", len(inb), "missing", len(miss),
          "| basket mc T", round(u[u.time == day].mc1.sum() / 1e12, 1))
    print(m.why.value_counts().to_string())
    print(m.dropna().sort_values("mcT", ascending=False).head(10).round(2).to_string())
    print("no-row/no-OShares tickers:", " ".join(m[m.mcT.isna()].ticker))
