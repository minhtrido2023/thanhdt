"""TA model ±5% (T+2 VN) — engine theo PREREG.md. PAPER-ONLY.
Chạy: /home/trido/thanhdt/wc_venv/bin/python engine.py
Ghi: deals.parquet (mọi deal đủ điều kiện L20 + cờ pattern), meta.json."""
import glob, json, os
import numpy as np, pandas as pd

ROOT = "/home/trido/thanhdt/WorkingClaude"
OUT = os.path.dirname(os.path.abspath(__file__))
START, LOAD_FROM = pd.Timestamp("2014-01-01"), "2012"
FEE = 0.00097
TIERS = {"L20": 20e9, "L50": 50e9, "L100": 100e9}
HS = [10, 20]
PATS = ["BRK", "PB20", "PB50", "SQZ", "OSB", "FTD"]
CAP = 1.03

# ------------------------------------------------------------ load
cols = ["time", "ticker", "Open", "High", "Low", "Close", "Price", "Volume", "Inflation_7", "MA20", "MA50", "MA200"]
fs = [f for f in sorted(glob.glob(f"{ROOT}/data/bq_cache/ticker/20*.parquet")) if os.path.basename(f)[:4] >= LOAD_FROM]
raw = pd.concat([pd.read_parquet(f, columns=cols) for f in fs])
raw["time"] = pd.to_datetime(raw["time"])
raw = raw.sort_values(["ticker", "time"]).drop_duplicates(["ticker", "time"]).reset_index(drop=True)
vni = raw[raw.ticker == "VNINDEX"].set_index("time")["Close"].sort_index()
df = raw[raw.ticker != "VNINDEX"].reset_index(drop=True)
u = pd.concat([pd.read_parquet(f, columns=["time", "ticker", "in_universe"]) for f in sorted(glob.glob(f"{ROOT}/data/bq_cache/universe_pit/*.parquet"))])
u["time"] = pd.to_datetime(u["time"])
u = u.drop_duplicates(["time", "ticker"])
df = df.merge(u, on=["time", "ticker"], how="left")
df["in_universe"] = df["in_universe"].fillna(False).astype(bool)
df = df.sort_values(["ticker", "time"]).reset_index(drop=True)
print("rows", len(df), "tickers", df.ticker.nunique(), "last", df.time.max().date(), flush=True)

g = df.groupby("ticker", sort=False)
O, Hh, L, C, V = (df[k].astype(float).to_numpy() for k in ["Open", "High", "Low", "Close", "Volume"])
tid = pd.factorize(df["ticker"])[0]
n = len(df)

def gs(col, k):  # shift theo mã
    return g[col].shift(k) if isinstance(col, str) else col.groupby(df["ticker"], sort=False).shift(k)

def roll(s, w, fn, minp=None):
    r = s.groupby(df["ticker"], sort=False).rolling(w, min_periods=minp or w)
    return getattr(r, fn)().reset_index(level=0, drop=True).sort_index()

c = df["Close"].astype(float)
ma20, ma50, ma200 = roll(c, 20, "mean"), roll(c, 50, "mean"), roll(c, 200, "mean")
tv_real = df["Price"].astype(float) * df["Volume"].astype(float) / df["Inflation_7"].astype(float)
mdv60 = roll(tv_real, 60, "median")
vol = df["Volume"].astype(float)
vavg20_prev = gs(roll(vol, 20, "mean"), 1)
hi60_prev = gs(roll(df["High"].astype(float), 60, "max"), 1)

# self-check MA tự tính vs cột BQ
chk = {}
for nm, mine in [("MA20", ma20), ("MA50", ma50), ("MA200", ma200)]:
    m = mine.notna() & df[nm].notna() & (df.time >= START)
    chk[nm] = float(((mine[m] - df.loc[m, nm]).abs() / c[m] < 1e-3).mean())
print("MA match", chk, flush=True)

# --------------------------------------------------- patterns (≤ T0)
P = {}
P["BRK"] = (c > hi60_prev) & (vol >= 1.5 * vavg20_prev) & (c > ma50)
ma50_l20, ma200_l20 = gs(ma50, 20), gs(ma200, 20)
hi20_prev = gs(roll(df["High"].astype(float), 20, "max"), 1)
low = df["Low"].astype(float)
P["PB20"] = (ma50 > ma200) & (ma50 > ma50_l20) & (c > ma50) & (low <= ma20 * 1.01) & (c >= ma20) & (hi20_prev >= ma20 * 1.05)
P["PB50"] = (ma50 > ma200) & (ma200 > ma200_l20) & (low <= ma50 * 1.01) & (c >= ma50)
sd20 = roll(c, 20, "std")
bw = 4 * sd20 / ma20
bw_prev = gs(bw, 1)
bw_q20 = gs(bw.groupby(df["ticker"], sort=False).rolling(120, min_periods=120).quantile(0.2).reset_index(level=0, drop=True).sort_index(), 1)
P["SQZ"] = (bw_prev <= bw_q20) & (c > ma20 + 2 * sd20) & (vol > vavg20_prev)
# RSI14 Wilder
dlt = c.groupby(df["ticker"], sort=False).diff()
up, dn = dlt.clip(lower=0), (-dlt).clip(lower=0)
au = up.groupby(df["ticker"], sort=False).transform(lambda s: s.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean())
ad = dn.groupby(df["ticker"], sort=False).transform(lambda s: s.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean())
rsi = 100 - 100 / (1 + au / ad.replace(0, np.nan))
P["OSB"] = (gs(rsi, 1) < 30) & (c > gs("High", 1))
# FTD cấp mã
lo20 = roll(c, 20, "min")
# vị trí đáy trong 20 phiên: số phiên kể từ min
def bars_since_min(s):
    a = s.to_numpy(); out = np.full(len(a), np.nan)
    for i in range(19, len(a)):
        w = a[i - 19:i + 1]
        if np.isnan(w).any(): continue
        out[i] = 19 - int(np.argmin(w))  # số phiên kể từ đáy (lần chạm đầu)
    return pd.Series(out, index=s.index)
bsm = c.groupby(df["ticker"], sort=False, group_keys=False).apply(bars_since_min)
dd_from_hi = lo20 / roll(c, 80, "max") - 1  # đỉnh 60 phiên trước đáy ≈ max 80 phiên (đáy nằm trong 20 phiên gần)
ret1 = c / gs(c, 1) - 1
P["FTD"] = (bsm >= 4) & (bsm <= 10) & (dd_from_hi <= -0.15) & (ret1 >= 0.03) & (vol > gs(vol, 1)) & (vol > vavg20_prev) & (c > lo20)

# --------------------------------------------------- eligibility
elig = (df["in_universe"] & (mdv60 >= TIERS["L20"]) & (df.time >= START)).to_numpy()
pos = g.cumcount().to_numpy()

def cooldown(flag, gap=10):
    idx = np.flatnonzero(flag); out = np.zeros(n, bool); last_t, last_p = -1, -10**9
    for i in idx:
        if tid[i] != last_t or pos[i] - last_p > gap:
            out[i] = True; last_t, last_p = tid[i], pos[i]
    return out

flags = {p: cooldown(P[p].fillna(False).to_numpy() & elig) for p in PATS}
for p in PATS: print(p, int(flags[p].sum()), flush=True)

# --------------------------------------------------- deal simulation
same = lambda a, b: (b < n) & (tid[np.minimum(b, n - 1)] == tid[a])
Cprev = np.r_[np.nan, C[:-1]]
locked_dn = (Hh == L) & (C < Cprev) & (np.r_[-1, tid[:-1]] == tid)

def simulate(idx, H, mode):
    """trả về entry, exit, reason(0 unfilled,1 TP,2 SL,3 TO,-1 thiếu dữ liệu), exit_k"""
    m = len(idx); b = idx + 1
    ok_b = same(idx, b)
    bb = np.minimum(b, n - 1)
    cap = C[idx] * CAP
    ceil_lock = (Hh[bb] == L[bb]) & (O[bb] > C[idx])
    ent = np.where(O[bb] <= cap, O[bb], np.where(L[bb] <= cap, cap, np.nan))
    ent[ceil_lock | ~ok_b] = np.nan
    reason = np.where(np.isnan(ent), 0, -9).astype(int)
    reason[~ok_b] = -1
    ex = np.full(m, np.nan); exk = np.full(m, -1)
    tp, sl = ent * 1.05, ent * 0.95
    pend = np.zeros(m, bool); pend_reason = np.zeros(m, int)
    for k in range(2, H + 2):
        d = b + k; okd = same(idx, d); dd = np.minimum(d, n - 1)
        act = reason == -9
        # thiếu dữ liệu
        miss = act & ~okd
        reason[miss] = -1
        act &= okd
        # pending bán từ phiên sàn trắng
        pe = act & pend
        ex[pe] = O[dd[pe]]; reason[pe] = pend_reason[pe]; exk[pe] = k
        act &= ~pe
        if k == H + 1:  # chỉ phục vụ pending
            reason[act] = -1  # không bao giờ xảy ra: TO đã đóng ở k=H
            break
        cl, lk = C[dd], locked_dn[dd]
        if mode == "HL" and k >= 3:
            o = O[dd]
            r_tpo = act & (o >= tp); ex[r_tpo] = o[r_tpo]; reason[r_tpo] = 1; exk[r_tpo] = k; act &= ~r_tpo
            r_slo = act & (o <= sl)
            ok = r_slo & ~lk; ex[ok] = o[ok]; reason[ok] = 2; exk[ok] = k
            pd_ = r_slo & lk; pend[pd_] = True; pend_reason[pd_] = 2; reason[pd_] = -9
            act &= ~r_slo
            r_sl = act & (L[dd] <= sl); ex[r_sl] = sl[r_sl]; reason[r_sl] = 2; exk[r_sl] = k; act &= ~r_sl
            r_tp = act & (Hh[dd] >= tp); ex[r_tp] = tp[r_tp]; reason[r_tp] = 1; exk[r_tp] = k; act &= ~r_tp
        else:
            r_tp = act & (cl >= tp); ex[r_tp] = cl[r_tp]; reason[r_tp] = 1; exk[r_tp] = k; act &= ~r_tp
            r_sl = act & (cl <= sl)
            ok = r_sl & ~lk; ex[ok] = cl[ok]; reason[ok] = 2; exk[ok] = k
            pd_ = r_sl & lk; pend[pd_] = True; pend_reason[pd_] = 2
            act &= ~r_sl
        if k == H:
            ok = act & ~lk & ~pend; ex[ok] = cl[ok]; reason[ok] = 3; exk[ok] = k
            pd_ = act & lk & ~pend; pend[pd_] = True; pend_reason[pd_] = 3
    reason[(reason == -9)] = -1
    return ent, ex, reason, exk

idx = np.flatnonzero(elig)
out = pd.DataFrame({"row": idx, "time": df.time.to_numpy()[idx], "ticker": df.ticker.to_numpy()[idx],
                    "mdv60": mdv60.to_numpy()[idx], "c_ma50": (c / ma50).to_numpy()[idx]})
vma50 = vni.rolling(50).mean()
out["vni_up"] = (vni / vma50 > 1).reindex(out["time"]).to_numpy()
for p in PATS: out[p] = flags[p][idx]
for H in HS:
    for mode in ["C", "HL"]:
        ent, ex, rs, ek = simulate(idx, H, mode)
        t = f"{mode}{H}"
        out[f"ent_{t}"], out[f"ex_{t}"], out[f"rs_{t}"], out[f"k_{t}"] = ent, ex, rs, ek
        vc = pd.Series(rs).value_counts().sort_index().to_dict()
        print(t, {int(a): int(b) for a, b in vc.items()}, flush=True)
out.to_parquet(f"{OUT}/deals.parquet")
json.dump({"ma_match": chk, "n_elig": int(len(idx)), "last": str(df.time.max().date()),
           "pattern_counts_L20": {p: int(flags[p].sum()) for p in PATS}}, open(f"{OUT}/meta.json", "w"), indent=1)
print("done")
