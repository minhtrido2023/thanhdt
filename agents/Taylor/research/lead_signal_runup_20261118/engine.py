"""Dựng panel mã-ngày: đặc trưng + nhãn + giao dịch. PREREG md5 ef70c866. PAPER-ONLY.
Chạy: /home/trido/thanhdt/wc_venv/bin/python engine.py  → panel.parquet, control_leg.json"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

OUT = os.path.dirname(os.path.abspath(__file__))
df, vni = load()
print("rows", len(df), "tickers", df.ticker.nunique(), "last", df.time.max().date(), flush=True)
vo_ok = (vni.VO.notna() & (vni.VO != vni.V)).mean()
print("VNI Open khác Close ở", round(vo_ok, 3), "số phiên", flush=True)

parts = []
for tk, g in df.groupby("ticker", sort=False):
    if len(g) < 260 or not g.in_universe.any():
        continue
    f = feats(g); lb = labels(g)
    keep = g[["time", "ticker", "in_universe", "Close", "Open", "Volume"]].join(f).join(lb)
    parts.append(keep)
P = pd.concat(parts).sort_values(["ticker", "time"]).reset_index(drop=True)

# control leg (livermore 14/11): in_universe ∧ MDV60 thực ≥ 20 tỷ ∧ 2014-01-01..2026-11-05
cl = int((P.in_universe & (P.MDV60_real >= 20e9) & (P.time >= "2014-01-01") & (P.time <= "2026-11-05")).sum())
json.dump({"ctrl_leg_mine": cl, "ctrl_leg_livermore": 300438}, open(f"{OUT}/control_leg.json", "w"))
print("CONTROL LEG", cl, "vs 300438", flush=True)

# S21 cắt ngang
uni = P.in_universe & (P.Volume > 0)
P["tvrank"] = np.nan
P.loc[uni, "tvrank"] = P[uni].groupby("time").TV.rank(pct=True)
prev = P.groupby("ticker").tvrank.transform(lambda s: s.shift(1).rolling(20, min_periods=10).mean())
P["S21"] = (P.tvrank - prev >= 0.30).fillna(False)

# breadth PIT
br = P[uni].groupby("time").above_ma50.mean().rename("breadth")
P = P.merge(br, on="time", how="left")
st = pd.read_parquet(f"{ROOT}/data/bq_cache/vnindex_5state_dt5g_live.parquet")[["time", "state"]]
st["time"] = pd.to_datetime(st["time"]); P = P.merge(st.rename(columns={"state": "dt5g"}), on="time", how="left")

P["E"] = (P.in_universe & (P.Volume > 0) & (P.nhist >= 250) & (P.nvol20 >= 10) & P.valid & (P.time >= "2014-01-02"))
P["year"] = P.time.dt.year
P["OOS"] = P.time >= "2020-01-01"
P["chase"] = P.ret5 > 0.15
for X in XS:
    P[f"y{int(X*100)}"] = (P.maxex >= X)
P["unfill"] = P.o1 >= P.Close * (1 + 0.95 * P.band)
slip = np.select([P.ADV20 >= 20e9, P.ADV20 >= 5e9, P.ADV20 >= 1e9], [0.001, 0.003, 0.0075], 0.015)
P["cost_rt"] = 2 * (0.001 + slip)
P["net_ex"] = P.trade_ex - P.cost_rt
# cửa sổ trước T0: tín hiệu bất kỳ trong t-5..t-1 (tính trên dòng liên tục của mã, TRƯỚC khi lọc)
gb = P.groupby("ticker")
for s_ in SIGS:
    P[f"pre5_{s_}"] = gb[s_].transform(lambda x: x.astype(float).shift(1).rolling(5, min_periods=1).max()).fillna(0).astype(bool)
# đợt run-up: ngày F mới cách ngày F cuối của đợt trước >= 20 dòng thì mở đợt mới; T0 = ngày F đầu đợt
for X in XS:
    c = f"y{int(X*100)}"; T0 = np.zeros(len(P), bool); eid = np.full(len(P), -1)
    F = (P.E & P[c]).to_numpy(); pos = P.nhist.to_numpy(); n_ep = 0
    for tk, idx in gb.indices.items():
        last = -10**9
        for i in idx[F[idx]]:
            if pos[i] - last >= 20:
                T0[i] = True; n_ep += 1
            eid[i] = n_ep; last = pos[i]
    P[f"T0_{c}"] = T0; P[f"ep_{c}"] = eid
    print("episodes", c, n_ep, flush=True)
P = P[P.E | P.ticker.isin(["TV1", "VCP"])].reset_index(drop=True)
P.to_parquet(f"{OUT}/panel.parquet")
print("panel E rows", int(P.E.sum()), "IS", int((P.E & ~P.OOS).sum()), "OOS", int((P.E & P.OOS).sum()), flush=True)
