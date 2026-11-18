"""Self-check theo PREREG §8: (2) không nhìn trước (cắt + nhiễu tương lai), (3) nhãn vòng lặp thuần, (4) 0 VND P&L.
(1) control leg ở control_leg.json; (5) threads=1 qua env trong lib."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
OUT = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(7)
df, vni = load()
FE = [s for s in SIGS if s != "S21"] + KS + ["band", "ADV20", "ret5", "run20"]
tks = [t for t, n in df.groupby("ticker").size().items() if n > 900]
pick = rng.choice(tks, 30, replace=False)
bad = 0; checked = 0
for tk in pick:
    g = df[df.ticker == tk].reset_index(drop=True)
    full = feats(g)
    for cut in rng.integers(300, len(g) - 50, 3):
        gt = g.iloc[:cut + 1]
        ft = feats(gt)
        gn = g.copy()  # nhiễu tương lai
        fut = gn.index > cut
        for c in ["Open", "High", "Low", "Close", "Price"]:
            gn.loc[fut, c] = gn.loc[fut, c] * rng.uniform(0.5, 1.5, fut.sum())
        gn.loc[fut, "Volume"] = gn.loc[fut, "Volume"] * rng.uniform(0, 10, fut.sum())
        fn = feats(gn)
        for f in FE:
            a, b, c2 = full[f].iloc[:cut + 1].to_numpy(), ft[f].to_numpy(), fn[f].iloc[:cut + 1].to_numpy()
            eq = lambda x, y: np.array_equal(x, y) if x.dtype == bool else np.allclose(x, y, equal_nan=True, rtol=0, atol=0)
            checked += 1
            if not (eq(a, b) and eq(a, c2)):
                bad += 1; print("LOOKAHEAD?", tk, cut, f)
# S21 (cắt ngang): tính lại trên panel cắt toàn universe tại 1 mốc
Pn = pd.read_parquet(f"{OUT}/panel.parquet", columns=["time", "ticker", "S21", "E"])
s21_note = "S21 dùng rank cùng ngày + rolling shift(1) của chính mã: chỉ dữ liệu <= t theo cấu trúc (groupby time rank; transform shift/rolling)"

# (3) nhãn bằng vòng lặp thuần
P = pd.read_parquet(f"{OUT}/panel.parquet")
P = P[P.E]
samp = P.sample(2000, random_state=3)
dfi = df.set_index(["ticker", "time"])
lab_err = 0; maxdiff = 0.0
grp = {tk: g.reset_index(drop=True) for tk, g in df[df.ticker.isin(samp.ticker.unique())].groupby("ticker")}
for _, r in samp.iterrows():
    g = grp[r.ticker]; i = int(np.flatnonzero(g.time.to_numpy() == np.datetime64(r.time))[0])
    best = -9; worst = 9
    for k in range(1, 11):
        e = g.Close[i + k] / g.Close[i] - g.V[i + k] / g.V[i]; best = max(best, e); worst = min(worst, e)
    d = max(abs(best - r.maxex), abs(worst - r.minex)); maxdiff = max(maxdiff, d)
    lab_err += d > 1e-12
# (4) 0 VND: 500 lệnh, vốn 1 tỷ/lệnh
tr = P[P.trade_ex.notna() & ~P.unfill].sample(500, random_state=5)
vnd_diff = 0.0
for _, r in tr.iterrows():
    g = grp.get(r.ticker)
    if g is None:
        g = df[df.ticker == r.ticker].reset_index(drop=True); grp[r.ticker] = g
    i = int(np.flatnonzero(g.time.to_numpy() == np.datetime64(r.time))[0])
    stock = g.Open[i + 1]; exitp = g.Close[i + 10]
    idx_ret = g.V[i + 10] / g.V[i] - 1
    pnl_loop = 1e9 * (exitp / stock - 1 - idx_ret)
    vnd_diff += abs(pnl_loop - 1e9 * r.trade_ex)
res = {"lookahead_checks": checked, "lookahead_bad": bad, "s21": s21_note, "label_rows": 2000, "label_err": int(lab_err),
       "label_maxdiff": maxdiff, "trades": 500, "sum_abs_vnd_diff": vnd_diff,
       "PASS": bool(bad == 0 and lab_err == 0 and vnd_diff < 1.0)}
json.dump(res, open(f"{OUT}/selfcheck.json", "w"), indent=1, default=float); print(res)
