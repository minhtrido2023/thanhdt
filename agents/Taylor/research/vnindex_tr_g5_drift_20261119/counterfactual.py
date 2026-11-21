"""Phản thực: thêm mã HOSE vắng khỏi rổ (DMX: BQ có giá, OShares NULL; GEL/CRV: không có dòng BQ).
Số CP = vốn hoá VNDirect /v4/ratios itemCode 51003 ngày 2026-11-18 ÷ giá đóng cửa 18/11 (giả định số CP
không đổi trong cửa sổ — ƯỚC LƯỢNG). Giá GEL/CRV: DNSE chart-api stock 1D. Chỉ đọc."""
import json, urllib.request, datetime as dt
import pandas as pd, numpy as np
from zoneinfo import ZoneInfo
ICT = ZoneInfo("Asia/Ho_Chi_Minh")
D = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/vnindex_tr_g5_drift_20261119"
u = pd.read_pickle(f"{D}/u_frame_latest.pkl"); a = pd.read_pickle(f"{D}/day_frame_latest.pkl")
CAP = {"DMX": 9.7614594e13, "GEL": 2.136e13, "CRV": 1.57414571375e13}   # VNDirect 51003, 2026-11-18
def dnse(sym):
    t0 = int(dt.datetime(2026, 5, 1, tzinfo=ICT).timestamp()); t1 = int(dt.datetime(2026, 11, 19, tzinfo=ICT).timestamp())
    url = f"https://services.entrade.com.vn/chart-api/v2/ohlcs/stock?symbol={sym}&resolution=1D&from={t0}&to={t1}"
    j = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read())
    return pd.Series(j["c"], index=pd.to_datetime([dt.datetime.fromtimestamp(t, ICT).date() for t in j["t"]]))
px = {s: dnse(s) for s in CAP}
for s, p in px.items():
    # DNSE chart giá theo nghìn đồng? chuẩn hoá theo bậc độ lớn
    sc = 1000 if p.iloc[-1] < 1000 else 1
    px[s] = p * sc
    print(s, "DNSE first", p.index[0].date(), "last", p.index[-1].date(), "close18/11", px[s].iloc[-1], "shares est", f"{CAP[s] / px[s].iloc[-1]:.4e}")
days = a.index
add = []
for s, p in px.items():
    p = p.reindex(days).ffill()        # không có giao dịch: giữ giá (VN-Index cũng giữ giá tham chiếu)
    sh = CAP[s] / p.iloc[-1]
    r = p.pct_change()
    add.append(pd.DataFrame({"time": days, "ticker": s, "mc1": (p.shift(1) * sh).values, "pr": r.values}).dropna())
X = pd.concat([u[["time", "ticker", "mc1", "pr"]]] + add)
synth = lambda x: (x.pr * x.mc1).groupby(x.time).sum() / x.groupby("time").mc1.sum()
W = ("2026-08-15", "2026-11-11"); off = a.off[W[0]:W[1]]
G = lambda k: (np.prod(1 + k[W[0]:W[1]]) - np.prod(1 + off)) * 100
print("G5 rebuild", round(G(synth(u)), 3))
for s in CAP:
    print(" + ", s, round(G(synth(pd.concat([u[["time", "ticker", "mc1", "pr"]]] + [x for x in add if x.ticker.iloc[0] == s]))), 3))
k_all = synth(X); print("G5 rebuild + DMX+GEL+CRV", round(G(k_all), 3))
d_all = (k_all - a.off)[W[0]:W[1]] * 1e4
print("mean d bp", round(d_all.mean(), 3), "| corr with off", round(np.corrcoef(d_all, off)[0, 1], 3))
# G5 trượt toàn 2026 cho bản đã thêm 3 mã
k = k_all["2026-05-06":]; o = a.off["2026-05-06":]
g = (np.exp(np.log1p(k).rolling(60).sum()) - np.exp(np.log1p(o).rolling(60).sum())) * 100
g0 = (np.exp(np.log1p(synth(u)["2026-05-06":]).rolling(60).sum()) - np.exp(np.log1p(o).rolling(60).sum())) * 100
pd.DataFrame({"g5_rebuild": g0, "g5_rebuild_plus3": g}).dropna().to_csv(f"{D}/g5_rolling_rebuild.csv")
print(pd.DataFrame({"rebuild": g0, "plus3": g}).dropna().resample("W").last().round(2).to_string())
