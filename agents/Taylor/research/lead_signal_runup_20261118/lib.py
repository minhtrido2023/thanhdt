"""Thư viện dùng chung: nạp dữ liệu, đặc trưng (S01..S21, C1..C3, K1..K4), nhãn. Theo PREREG.md md5 ef70c866.
Mọi đặc trưng tại dòng t chỉ dùng dữ liệu ≤ t (rolling causal). Nhãn dùng tương lai (chỉ là nhãn)."""
import glob, os
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ.setdefault("MKL_NUM_THREADS", "1"); os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np, pandas as pd

ROOT = "/home/trido/thanhdt/WorkingClaude"
SIGS = ["S01", "S02", "S03", "S04", "S05", "S06", "S07", "S08", "S09", "S10", "S11", "S12", "S13", "S14", "S15",
        "S16", "S17", "S18", "S19", "S20", "S21", "C1", "C2", "C3"]
NAMES = {"S01": "ATRP_LOW", "S02": "BBW_LOW", "S03": "NR7_ID", "S04": "TIGHT20", "S05": "VCP_CONTRACT", "S06": "DRYUP",
         "S07": "SURGE3", "S08": "SURGE5", "S09": "DRY_THEN_SURGE", "S10": "HIDDEN_ACC", "S11": "UPDOWN_VOL",
         "S12": "OBV_DIV", "S13": "HIGHER_LOWS", "S14": "NEAR_52W", "S15": "BREAKOUT_52W", "S16": "RS_LEAD",
         "S17": "MA_CONV_X", "S18": "CEIL_TODAY", "S19": "CEIL2_5D", "S20": "GAPUP", "S21": "TURN_RANK_JUMP",
         "C1": "TIGHT20&SURGE3", "C2": "ATRP_LOW&NEAR_52W", "C3": "RS_LEAD&UPDOWN_VOL"}
KS = ["K1", "K2", "K3", "K4"]
XS = [0.20, 0.30]
H = 10


def load(start_year=2012):
    cols = ["time", "ticker", "Open", "High", "Low", "Close", "Price", "Volume", "Inflation_7"]
    files = [f for f in sorted(glob.glob(f"{ROOT}/data/bq_cache/ticker/20*.parquet")) if int(os.path.basename(f)[:4]) >= start_year]
    raw = pd.concat([pd.read_parquet(f, columns=cols) for f in files])
    raw["time"] = pd.to_datetime(raw["time"])
    raw = raw.sort_values(["ticker", "time"]).drop_duplicates(["ticker", "time"]).reset_index(drop=True)
    u = pd.concat([pd.read_parquet(f, columns=["time", "ticker", "in_universe"]) for f in sorted(glob.glob(f"{ROOT}/data/bq_cache/universe_pit/*.parquet"))])
    u["time"] = pd.to_datetime(u["time"]); u = u.drop_duplicates(["time", "ticker"])
    vni = raw[raw.ticker == "VNINDEX"][["time", "Open", "Close"]].rename(columns={"Open": "VO", "Close": "V"})
    df = raw[raw.ticker != "VNINDEX"].merge(u, on=["time", "ticker"], how="left").merge(vni, on="time", how="left")
    df["in_universe"] = df["in_universe"].fillna(False).astype(bool)
    return df.sort_values(["ticker", "time"]).reset_index(drop=True), vni


def feats(g):
    """g: 1 mã, đã sort theo time, cột Open..Volume, Inflation_7, V. Trả DataFrame cùng index."""
    O, Hh, Lw, C = (g[c].astype(float) for c in ["Open", "High", "Low", "Close"])
    V = g["V"].astype(float)
    TV = g["Price"].astype(float) * g["Volume"].astype(float)
    C1 = C.shift(1)
    ret = C / C1 - 1
    out = pd.DataFrame(index=g.index)
    out["ret"] = ret
    out["TV"] = TV
    adv_prev = TV.shift(1).rolling(20, min_periods=10).mean()
    out["ADV20"] = TV.rolling(20, min_periods=10).mean()
    out["ADV20_real"] = (TV / g["Inflation_7"].astype(float)).rolling(20, min_periods=10).mean()
    out["MDV60_real"] = (TV / g["Inflation_7"].astype(float)).rolling(60, min_periods=60).median()
    out["nvol20"] = (g["Volume"] > 0).astype(float).rolling(20, min_periods=1).sum()
    # band causal
    mx = ret.shift(1).rolling(250, min_periods=120).max()
    band = np.where(mx <= 0.075, 0.07, np.where(mx <= 0.105, 0.10, 0.15))
    band = np.where(mx.isna(), 0.07, band)
    out["band"] = band
    ceil = (ret >= 0.95 * band)
    out["ceil"] = ceil
    out["floor"] = (ret <= -0.95 * band)
    rng = Hh - Lw
    TR = pd.concat([rng, (Hh - C1).abs(), (Lw - C1).abs()], axis=1).max(axis=1)
    atr14 = TR.rolling(14, min_periods=14).mean()
    atrp = atr14 / C
    s = {}
    s["S01"] = atrp.rolling(250, min_periods=250).rank(pct=True) <= 0.10
    ma20 = C.rolling(20, min_periods=20).mean(); sd20 = C.rolling(20, min_periods=20).std(ddof=0)
    bbw = 4 * sd20 / ma20
    s["S02"] = bbw.rolling(250, min_periods=250).rank(pct=True) <= 0.10
    s["S03"] = (rng <= rng.rolling(7, min_periods=7).min()) & (Hh <= Hh.shift(1)) & (Lw >= Lw.shift(1))
    hi20, lo20 = Hh.rolling(20, min_periods=20).max(), Lw.rolling(20, min_periods=20).min()
    s["S04"] = hi20 / lo20 - 1 <= 0.10
    w = [(Hh.shift(k).rolling(10, min_periods=10).max() / Lw.shift(k).rolling(10, min_periods=10).min() - 1) for k in (20, 10, 0)]
    s["S05"] = (w[0] > w[1]) & (w[1] > w[2]) & (w[2] <= 0.08) & (C >= 0.90 * Hh.rolling(60, min_periods=60).max())
    s["S06"] = TV.rolling(10, min_periods=10).median() <= 0.4 * TV.shift(10).rolling(120, min_periods=60).median()
    clv = np.where(rng > 0, (C - Lw) / rng.where(rng > 0, 1), np.where(C >= C1, 1.0, 0.0))
    clv = pd.Series(clv, index=g.index)
    out["clv"] = clv
    s["S07"] = (TV >= 3 * adv_prev) & (clv >= 0.5) & (ret > 0)
    s["S08"] = (TV >= 5 * adv_prev) & (clv >= 0.5) & (ret > 0)
    s["S09"] = s["S06"].shift(1, fill_value=False).astype(bool) & s["S07"]
    s["S10"] = (TV >= 3 * adv_prev) & (ret.abs() <= 0.02)
    up = TV.where(ret > 0, 0.0).rolling(20, min_periods=20).sum()
    dn = TV.where(ret < 0, 0.0).rolling(20, min_periods=20).sum()
    s["S11"] = ((dn > 0) & (up / dn.where(dn > 0, 1) >= 2)) | ((dn == 0) & (up > 0))
    obv = (np.sign(ret.fillna(0)) * TV).cumsum()
    s["S12"] = (obv >= obv.rolling(60, min_periods=60).max()) & ((C / C.shift(20) - 1).abs() <= 0.05)
    l3 = [Lw.shift(k).rolling(10, min_periods=10).min() for k in (20, 10, 0)]
    s["S13"] = (l3[0] < l3[1]) & (l3[1] < l3[2])
    h250 = Hh.shift(1).rolling(249, min_periods=249).max()
    s["S14"] = (C >= 0.95 * h250) & (C < h250)
    s["S15"] = (C > h250) & (TV >= 1.5 * adv_prev)
    rs = C / V
    s["S16"] = (rs >= rs.rolling(120, min_periods=120).max()) & (C < C.shift(1).rolling(119, min_periods=119).max())
    ma50 = C.rolling(50, min_periods=50).mean()
    mxma = np.maximum(ma20, ma50)
    s["S17"] = ((ma20 / ma50 - 1).abs() <= 0.02) & (C > mxma) & (C1 <= mxma.shift(1))
    s["S18"] = ceil
    s["S19"] = ceil.astype(float).rolling(5, min_periods=5).sum() >= 2
    s["S20"] = (O >= 1.02 * Hh.shift(1)) & (C >= O)
    for k, v in s.items():
        out[k] = v.fillna(False).astype(bool) if hasattr(v, "fillna") else v
    out["C1"] = out.S04 & out.S07
    out["C2"] = out.S01 & out.S14
    out["C3"] = out.S16 & out.S11
    out["ma50"] = ma50
    out["above_ma50"] = C > ma50
    out["ret5"] = C / C.shift(5) - 1
    out["run20"] = C / C.rolling(21, min_periods=21).min() - 1
    # climax (mô tả)
    out["K1"] = (TV >= TV.rolling(60, min_periods=60).max()) & (clv <= 0.3) & (rng >= 1.5 * atr14)
    out["K2"] = C / ma20 - 1 >= 0.25
    out["K3"] = ((ret > 0).astype(float).rolling(6, min_periods=6).sum() >= 5) & (C / C.shift(6) - 1 >= 0.20)
    out["K4"] = out["floor"]
    out["nhist"] = np.arange(len(g))
    return out


def labels(g):
    """Nhãn + giao dịch cho 1 mã. maxexR, minexR trên k=1..10; NaN nếu đình chỉ / lỗi dữ liệu / thiếu tương lai."""
    C = g["Close"].astype(float).to_numpy(); O = g["Open"].astype(float).to_numpy(); V = g["V"].astype(float).to_numpy()
    t = g["time"].to_numpy(); L = len(C)
    ex = np.full((L, H), np.nan)
    for k in range(1, H + 1):
        ex[:L - k, k - 1] = C[k:] / C[:L - k] - V[k:] / V[:L - k]
    ar = np.r_[np.nan, np.abs(C[1:] / C[:-1] - 1)]
    bad = np.zeros(L, bool)
    big = ar > 0.25
    for k in range(1, H + 1):
        bad[:L - k] |= big[k:]
    gap = np.full(L, np.inf)
    gap[:L - H] = (t[H:] - t[:L - H]) / np.timedelta64(1, "D")
    valid = (gap <= 25) & ~bad & ~np.isnan(ex).any(axis=1)
    mx = np.where(valid, np.nanmax(np.where(np.isnan(ex), -9, ex), axis=1), np.nan)
    mn = np.where(valid, np.nanmin(np.where(np.isnan(ex), 9, ex), axis=1), np.nan)
    o1 = np.r_[O[1:], np.nan]
    c10 = np.r_[C[H:], np.full(H, np.nan)]
    v10 = np.r_[V[H:], np.full(H, np.nan)]
    trade_ex = np.where(valid, c10 / o1 - 1 - (v10 / V - 1), np.nan)
    return pd.DataFrame({"maxex": mx, "minex": mn, "valid": valid, "o1": o1, "trade_ex": trade_ex}, index=g.index)
