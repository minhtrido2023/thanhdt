"""Self-check độc lập (vòng lặp thuần Python, không dùng code vectorized của engine).
1) A2 trên HPG: danh sách sự kiện khớp panel_events. 2) Tái tạo R20 + control F1 cho 1 sự kiện bằng tay.
3) Kiểm corp-action: AAA 2014-08-26 chia tách — R trên giá điều chỉnh vs giá thô."""
import glob, math
import numpy as np, pandas as pd

ROOT = "/home/trido/thanhdt/WorkingClaude"
D = ROOT + "/mike/agents/Taylor/research/ta_schools_vn_20261025"
cols = ["time", "ticker", "Open", "High", "Low", "Close", "Volume", "Price"]
raw = pd.concat([pd.read_parquet(f, columns=cols) for f in sorted(glob.glob(f"{ROOT}/data/bq_cache/ticker/20*.parquet"))])
raw["time"] = pd.to_datetime(raw["time"])
raw = raw.sort_values(["ticker", "time"]).drop_duplicates(["ticker", "time"])
u = pd.concat([pd.read_parquet(f, columns=["time", "ticker", "in_universe"]) for f in sorted(glob.glob(f"{ROOT}/data/bq_cache/universe_pit/*.parquet"))])
u["time"] = pd.to_datetime(u["time"])
inu = {(r.time, r.ticker): bool(r.in_universe) for r in u.drop_duplicates(["time", "ticker"]).itertuples()}
ev = pd.read_parquet(D + "/panel_events.parquet")


def series(tk):
    g = raw[raw.ticker == tk].reset_index(drop=True)
    return {k: g[k].tolist() for k in ["time", "Open", "High", "Low", "Close", "Volume", "Price"]}


def adv_at(s, t):
    return sum(s["Price"][i] * s["Volume"][i] for i in range(t - 19, t + 1)) / 20 if t >= 19 else float("nan")


def eligible(s, t, tk):
    d = s["time"][t]
    if d < pd.Timestamp("2014-01-01") or t < 30: return False
    o, h, l, c, v = (s[k][t] for k in ["Open", "High", "Low", "Close", "Volume"])
    if not (h - l > 0 and o > 0 and c > 0 and l > 0 and v > 0): return False
    a = adv_at(s, t)
    if not (a >= 1e9): return False
    if not inu.get((d, tk), False): return False
    for i in range(t - 25, t + 1):  # bad25 & corp25 (ret/ratio vs phiên trước)
        if i < 1: continue
        if abs(s["Close"][i] / s["Close"][i - 1] - 1) > 0.5: return False
        r1, r0 = s["Close"][i] / s["Price"][i], s["Close"][i - 1] / s["Price"][i - 1]
        if abs(r1 / r0 - 1) > 0.03: return False
    return True


def fwd(s, t, h):
    n = len(s["time"])
    if t + h >= n: return None
    if (s["time"][t + 1] - s["time"][t]).days > 5: return None
    if (s["time"][t + h] - s["time"][t]).days > 1.7 * h + 10: return None
    for i in range(t + 1, t + h + 1):
        if abs(s["Close"][i] / s["Close"][i - 1] - 1) > 0.5: return None
    return s["Close"][t + h] / s["Open"][t + 1] - 1


# ---- 1) A2 trên HPG
tk = "HPG"
s = series(tk); n = len(s["time"])
H, L, C = s["High"], s["Low"], s["Close"]
def mid(t, k):
    return (max(H[t - k + 1:t + 1]) + min(L[t - k + 1:t + 1])) / 2
raw_events = []
for t in range(80, n):
    ten, kij = mid(t, 9), mid(t, 26)
    tenp, kijp = mid(t - 1, 9), mid(t - 1, 26)
    s26 = t - 26
    ssa = (mid(s26, 9) + mid(s26, 26)) / 2
    ssb = mid(s26, 52)
    top = max(ssa, ssb)
    if tenp <= kijp and ten > kij and C[t] > top and eligible(s, t, tk):
        raw_events.append(t)
kept, last = [], -10**9
for t in raw_events:
    if t - last > 10: kept.append(t); last = t
mine = [s["time"][t] for t in kept]
eng = sorted(ev[(ev.ticker == tk) & ev["A2"]].time.tolist())
print("HPG A2 events brute:", len(mine), "engine:", len(eng), "match:", mine == eng)
assert mine == eng

# ---- 2) tái tạo R20 và control F1 cho 1 sự kiện (cuối danh sách có đủ 20 phiên)
t = [x for x in kept if fwd(s, x, 20) is not None][len(kept) // 2]
d0 = s["time"][t]; R = fwd(s, t, 20)
cohort = []  # (ticker, adv, R) cho mọi mã ctrl trong ngày d0
for tk2, g in raw[raw.time >= d0 - pd.Timedelta(days=60)].groupby("ticker"):
    s2 = {k: g[k].tolist() for k in ["time", "Open", "High", "Low", "Close", "Volume", "Price"]}
    if d0 not in set(s2["time"]): continue
    t2 = s2["time"].index(d0)
    if t2 < 19: continue
    if not inu.get((d0, tk2), False): continue
    a = adv_at(s2, t2)
    if not (a >= 1e9): continue
    cohort.append((tk2, a, s2, t2))
# adv cần 20 phiên: nạp lại đủ lịch sử (cửa sổ 60 ngày lịch có thể <20 phiên) → dùng series() đầy đủ
cohort2 = []
for tk2, a, _, _ in cohort:
    s2 = series(tk2); t2 = s2["time"].index(d0)
    cohort2.append((tk2, adv_at(s2, t2), fwd(s2, t2, 20)))
cohort2 = [(a, b, c) for a, b, c in cohort2 if b >= 1e9]
advs = pd.Series({a: b for a, b, _ in cohort2})
rk = advs.rank(pct=True, method="first")
tert = np.minimum(np.ceil(rk * 3) - 1, 2).astype(int)
mytert = tert["HPG"]
peers = [r for a, b, r in cohort2 if tert[a] == mytert and a != "HPG" and r is not None]
ctrl = sum(peers) / len(peers)
x1 = R - ctrl
row = ev[(ev.ticker == "HPG") & (ev.time == d0) & ev["A2"]].iloc[0]
print(f"sự kiện {d0.date()} R20 brute={R:.9f} engine={row.R20:.9f} | ctrl brute={ctrl:.9f} (n={len(peers)}, tertile {mytert}) | X1 brute={x1:.9f} engine={row.X1_20:.9f}")
assert abs(R - row.R20) < 1e-9 and abs(x1 - row.X1_20) < 1e-9

# ---- 3) corp-action AAA 2014-08-26
a = series("AAA"); t = a["time"].index(pd.Timestamp("2014-08-20"))
Radj = a["Close"][t + 10] / a["Open"][t + 1] - 1
Rraw = a["Price"][t + 10] / a["Price"][t + 1] - 1  # giá thô: Price (không có Open thô) → xấp xỉ
print(f"AAA 2014-08-20 -> +10 phiên (qua ex-date 08-26): R điều chỉnh={Radj:+.4f}  vs  R thô (Price/Price)={Rraw:+.4f}  (thô sẽ ghi nhận lỗ giả do chia tách)")
print("SELFCHECK OK")
