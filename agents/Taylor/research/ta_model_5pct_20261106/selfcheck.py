"""Self-check (PREREG §5): tái hiện ĐỘC LẬP 400 deal ngẫu nhiên (chân control = mọi mã đủ ĐK) bằng vòng lặp
thuần Python trên OHLC thô của từng mã, so giá vào/ra/lý do với engine (vector hoá). Kỳ vọng Δ = 0.
Kèm: chênh lệch tiền trên 1 tỷ VND/deal ở s=0,2% phải = 0 VND."""
import glob, os, sys
import numpy as np, pandas as pd

ROOT = "/home/trido/thanhdt/WorkingClaude"
OUT = os.path.dirname(os.path.abspath(__file__))
FEE, S = 0.00097, 0.002
d = pd.read_parquet(f"{OUT}/deals.parquet")
rng = np.random.default_rng(7)
samp = d.iloc[rng.choice(len(d), 400, replace=False)]
tk = set(samp.ticker)
raw = pd.concat([pd.read_parquet(f, columns=["time", "ticker", "Open", "High", "Low", "Close"], filters=[("ticker", "in", list(tk))])
                 for f in sorted(glob.glob(f"{ROOT}/data/bq_cache/ticker/20*.parquet")) if os.path.basename(f)[:4] >= "2012"])
raw["time"] = pd.to_datetime(raw["time"])
raw = raw.sort_values(["ticker", "time"]).drop_duplicates(["ticker", "time"])
by = {t: g.reset_index(drop=True) for t, g in raw.groupby("ticker")}


def sim(g, i, H, mode):
    rows = g.to_dict("records")
    if i + 1 >= len(rows):
        return np.nan, np.nan, -1
    c0, b = rows[i]["Close"], rows[i + 1]
    cap = c0 * 1.03
    if b["High"] == b["Low"] and b["Open"] > c0:
        return np.nan, np.nan, 0
    if b["Open"] <= cap: e = b["Open"]
    elif b["Low"] <= cap: e = cap
    else: return np.nan, np.nan, 0
    tp, sl = e * 1.05, e * 0.95
    pend = None
    for k in range(2, H + 2):
        j = i + 1 + k
        if j >= len(rows):
            return e, np.nan, -1
        r, rp = rows[j], rows[j - 1]
        if pend is not None:
            return e, r["Open"], pend
        if k == H + 1:
            return e, np.nan, -1
        lk = r["High"] == r["Low"] and r["Close"] < rp["Close"]
        if mode == "HL" and k >= 3:
            if r["Open"] >= tp: return e, r["Open"], 1
            if r["Open"] <= sl:
                if lk: pend = 2; continue
                return e, r["Open"], 2
            if r["Low"] <= sl: return e, sl, 2
            if r["High"] >= tp: return e, tp, 1
        else:
            if r["Close"] >= tp: return e, r["Close"], 1
            if r["Close"] <= sl:
                if lk: pend = 2; continue
                return e, r["Close"], 2
        if k == H:
            if lk: pend = 3; continue
            return e, r["Close"], 3
    return e, np.nan, -1


bad, vnd = 0, 0.0
for _, s in samp.iterrows():
    g = by[s.ticker]
    i = int(np.flatnonzero(g.time.to_numpy() == np.datetime64(s.time))[0])
    for t, H, mode in [("C20", 20, "C"), ("HL20", 20, "HL"), ("C10", 10, "C"), ("HL10", 10, "HL")]:
        e, x, rs = sim(g, i, H, mode)
        if rs != s[f"rs_{t}"]:
            bad += 1; print("reason mismatch", s.ticker, s.time.date(), t, rs, s[f"rs_{t}"]); continue
        if rs > 0:
            a = 1e9 * (x * (1 - FEE - S) / (e * (1 + FEE + S)) - 1)
            b = 1e9 * (s[f"ex_{t}"] * (1 - FEE - S) / (s[f"ent_{t}"] * (1 + FEE + S)) - 1)
            vnd += abs(a - b)
            if abs(e - s[f"ent_{t}"]) > 1e-9 or abs(x - s[f"ex_{t}"]) > 1e-9:
                bad += 1; print("price mismatch", s.ticker, s.time.date(), t, e, x, s[f"ent_{t}"], s[f"ex_{t}"])
print(f"deals checked 400 x 4 modes | mismatches {bad} | tổng |Δ P&L| trên 1 tỷ/deal = {vnd:.6f} VND")
sys.exit(1 if bad or vnd > 1e-3 else 0)
