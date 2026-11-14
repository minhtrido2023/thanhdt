"""Gói κ lặp lại cho P0 (kế hoạch §1 H4 / §8 G0): 20 case × 3 lần đọc độc lập của Livermore.
Chọn case bằng SEED cố định, KHÔNG chọn tay: 15 cổ phiếu từ universe_pit (in_universe ∧ MDV60 thực ≥ 20 tỷ, = U2 của
engine phân kỳ, đọc control.parquet) + 5 mốc VNINDEX. As-of ∈ [2014-01, 2025-09-30]; ≤1 case/mã; VNINDEX cách nhau ≥ 60 phiên;
bỏ (mã, as-of) trùng ±60 ngày với 100 case battery 05/11. Định dạng = battery 05/11 (250 phiên OHLC ÷ close đầu ×100,
vol ÷ trung vị cửa sổ); KHÔNG mã, KHÔNG ngày, KHÔNG nói chuỗi nào là chỉ số.
Chạy: /home/trido/thanhdt/wc_venv/bin/python build_cases.py  (từ thư mục kappa/)"""
import glob, json, os
import numpy as np, pandas as pd
ROOT = "/home/trido/thanhdt/WorkingClaude"; HERE = os.path.dirname(os.path.abspath(__file__)); UP = os.path.dirname(HERE)
SEED = 20261114; rng = np.random.default_rng(SEED)
N_STK, N_VNI, W, H = 15, 5, 250, 20
cols = ["time", "ticker", "Open", "High", "Low", "Close", "Volume"]
raw = pd.concat([pd.read_parquet(f, columns=cols) for f in sorted(glob.glob(f"{ROOT}/data/bq_cache/ticker/20*.parquet"))])
raw["time"] = pd.to_datetime(raw.time); raw = raw.sort_values(["ticker", "time"]).drop_duplicates(["ticker", "time"]).reset_index(drop=True)
CT = pd.read_parquet(f"{UP}/control.parquet"); CT["time"] = pd.to_datetime(CT.time)
bat = json.load(open(f"{ROOT}/mike/agents/Mike/research/livermore_stock_battery_20261105/SEALED_truth.json"))
bat_by = {}
for b in bat: bat_by.setdefault(b["ticker"], []).append(pd.Timestamp(b["asof"]))
G = {tk: g.reset_index(drop=True) for tk, g in raw.groupby("ticker")}


def window_ok(g, i):
    if i < W - 1 or i + H >= len(g): return False
    w = g.iloc[i - W + 1:i + 1]
    if (w.Volume == 0).mean() > 0.2 or w[["Open", "High", "Low", "Close"]].isna().any().any(): return False
    r = g.Close.iloc[i - W + 1:i + H + 1].pct_change().abs()
    return not (r > 0.16).any()


def case(g, i):
    w = g.iloc[i - W + 1:i + 1]; base = w.Close.iloc[0]; vm = w.Volume.median()
    df = pd.DataFrame({"session": range(W), "open": (w.Open.values / base * 100).round(2), "high": (w.High.values / base * 100).round(2),
                       "low": (w.Low.values / base * 100).round(2), "close": (w.Close.values / base * 100).round(2),
                       "vol_rel": (w.Volume.values / vm).round(2)})
    c0 = g.Close.iloc[i]; cl = w.Close.values
    tr = dict(asof=str(g.time.iloc[i].date()), fwd20=float(g.Close.iloc[i + H] / c0 - 1), up=int(g.Close.iloc[i + H] > c0),
              mom20=float(c0 / g.Close.iloc[i - 20] - 1), mom60=float(c0 / g.Close.iloc[i - 60] - 1),
              rp250=float((cl[-1] - w.Low.min()) / (w.High.max() - w.Low.min())))
    return df, tr


picked = []
# cổ phiếu
pool = CT[(CT.time >= "2014-01-01") & (CT.time <= "2025-09-30")][["ticker", "time"]].reset_index(drop=True)
seen = set()
for j in rng.permutation(len(pool)):
    if sum(p["kind"] == "stock" for p in picked) == N_STK: break
    tk, t = pool.ticker[j], pool.time[j]
    if tk in seen or any(abs((t - a).days) <= 60 for a in bat_by.get(tk, [])): continue
    g = G[tk]; ii = np.flatnonzero(g.time.values == np.datetime64(t))
    if len(ii) != 1 or not window_ok(g, int(ii[0])): continue
    df, tr = case(g, int(ii[0])); picked.append(dict(kind="stock", ticker=tk, df=df, **tr)); seen.add(tk)
# VNINDEX
gv = G["VNINDEX"]; cand = np.flatnonzero((gv.time >= "2014-01-01").values & (gv.time <= "2025-09-30").values)
vpos = []
for i in rng.permutation(cand):
    if len(vpos) == N_VNI: break
    if any(abs(int(i) - p) < 60 for p in vpos) or not window_ok(gv, int(i)): continue
    vpos.append(int(i)); df, tr = case(gv, int(i)); picked.append(dict(kind="VNINDEX", ticker="VNINDEX", df=df, **tr))
assert len(picked) == N_STK + N_VNI
order = rng.permutation(len(picked))
os.makedirs(f"{HERE}/cases", exist_ok=True); truth = []
for k, j in enumerate(order, 1):
    p = picked[j]; lab = f"K{k:02d}"
    p["df"].to_csv(f"{HERE}/cases/{lab}.csv", index=False)
    truth.append({"label": lab, **{a: b for a, b in p.items() if a != "df"}})
json.dump(truth, open(f"{HERE}/SEALED_truth.json", "w"), indent=1)
labels = [t["label"] for t in truth]
for r in (1, 2, 3):   # thứ tự đọc khác nhau mỗi lần (chống hiệu ứng thứ tự), seed cố định
    o = np.random.default_rng(SEED + r).permutation(labels)
    open(f"{HERE}/run{r}_order.txt", "w").write("\n".join(o) + "\n")
print(len(truth), "cases;", sum(t["kind"] == "VNINDEX" for t in truth), "VNINDEX; base rate up =", np.mean([t["up"] for t in truth]))
