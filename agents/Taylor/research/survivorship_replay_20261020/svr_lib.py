"""Thư viện dựng lại đầu vào engine từ giá VNDirect (job Taylor_20261020_094204, theo PREREG.md md5 21165fd1)."""
import os, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
KBD = "/home/trido/thanhdt/WorkingClaude/mike/kb/projects/delisted-tickers-survivorship-20261020.d"


def load_px(tk):
    """Chuẩn hoá: index=date; cột floor, open, close, adClose, nmVolume, val(nm+pt), after_lt."""
    for p in (f"{KBD}/prices/{tk}.csv", f"{KBD}/prices_all/{tk}.csv", f"{HERE}/data/px_{tk}.csv"):
        if os.path.exists(p):
            d = pd.read_csv(p); break
    else:
        raise FileNotFoundError(tk)
    d["date"] = pd.to_datetime(d["date"]); d = d.sort_values("date").drop_duplicates("date", keep="last").set_index("date")
    for c in ["nmValue", "ptValue", "nmVolume"]:
        d[c] = d[c].fillna(0.0) if c in d else 0.0
    d["val"] = d.nmValue + d.ptValue
    return d[["floor", "open", "close", "adClose", "nmVolume", "val"]].astype({"open": float, "close": float, "adClose": float})


def rsi(c, n=14, kind="wilder"):
    dlt = c.diff(); up = dlt.clip(lower=0); dn = -dlt.clip(upper=0)
    if kind == "wilder":
        au = up.ewm(alpha=1 / n, adjust=False).mean(); ad = dn.ewm(alpha=1 / n, adjust=False).mean()
    else:
        au = up.rolling(n).mean(); ad = dn.rolling(n).mean()
    return au / (au + ad)


def indicators(px, cal, rsi_kind="wilder"):
    """Chỉ báo SIGNAL_V11 phần giá trên lịch `cal` (ngày ticker có dòng). Close/Price theo VND."""
    d = px[px.index.isin(cal)].copy()
    C = d.adClose * 1000.0; P = d.close * 1000.0; V = d.nmVolume
    o = pd.DataFrame(index=d.index)
    o["Close"] = C; o["Price"] = P; o["Volume"] = V
    o["Open"] = d.open * d.adClose / d.close.replace(0, np.nan) * 1000.0
    o["Close_T1"] = C.shift(1)
    for n in (20, 50, 200):
        o[f"MA{n}"] = C.rolling(n).mean()
    o["MA50_T1"] = o.MA50.shift(1)
    o["D_RSI"] = rsi(C, 14, rsi_kind)
    e12 = C.ewm(span=12, adjust=False).mean(); e26 = C.ewm(span=26, adjust=False).mean()
    macd = e12 - e26; o["D_MACDdiff"] = macd - macd.ewm(span=9, adjust=False).mean()
    o["HI_3M_T1"] = C.rolling(60).max().shift(1)
    # ID_HI_3Y: số phiên kể từ đỉnh 3 năm (756 phiên)
    o["ID_HI_3Y"] = C.rolling(756, min_periods=60).apply(lambda a: len(a) - 1 - int(np.argmax(a)), raw=True)
    o["D_RSI_Max1W"] = o.D_RSI.rolling(5).max()
    o["Volume_3M_P50"] = V.rolling(60).median()
    o["liq"] = o.Volume_3M_P50 * P
    return o


def ta_px(o, vni_rsimax3m):
    """Phần ta chỉ dùng giá/khối lượng (không BCTC, không ngành)."""
    t = (np.where(o.D_RSI > 0.50, 25, 0) + np.where((o.Close > o.MA50) & (o.MA50 > o.MA200), 25, 0)
         + np.where((o.Volume >= o.Volume_3M_P50 * 1.3) & (o.Close > o.Close_T1), 20, 0)
         + np.where(o.D_MACDdiff > 0, 15, 0) + np.where(o.Close > o.MA20, 15, 0)
         + np.where(o.D_RSI > 0.75, 5, 0) + np.where(o.D_RSI < 0.30, -10, 0)
         + np.where(vni_rsimax3m.reindex(o.index) > 0.65, 10, 0)
         + np.where(o.ID_HI_3Y <= 5, 8, 0) + np.where(o.D_RSI_Max1W > 0.65, 5, 0)
         + np.where((o.MA50_T1 > 0) & (o.MA50 > o.MA50_T1), 5, 0)
         + np.where((o.MA50_T1 > 0) & (o.MA50 > o.MA50_T1 * 1.005), 5, 0)
         + np.where((o.MA50_T1 > 0) & (o.MA50 < o.MA50_T1), -5, 0)
         + np.where((o.HI_3M_T1 > 0) & (o.Close / o.HI_3M_T1 < 0.85), -10, 0))
    return pd.Series(t, index=o.index, dtype=float)


def universe(px, cal_all, infl, first_row=None):
    """Replica ruleset v1 (build_universe_pit.py). cal_all = lịch VNINDEX. Trả Series bool trên ngày mã có dòng."""
    d = px.copy()
    d = d[d.index.isin(cal_all)]
    rn = pd.Series(np.arange(len(cal_all)), index=cal_all)
    d_rn = rn.reindex(d.index).values
    close = d.adClose * 1000.0
    inf = infl.reindex(d.index)
    inf = inf.where(inf > 0, 1.07 ** (d.index.year - 2026))
    tv = (d.close * 1000.0 * d.nmVolume / inf).fillna(0.0)
    age = np.arange(1, len(d) + 1)
    gap = np.r_[0, np.diff(d_rn) - 1]
    med = tv.rolling(60, min_periods=60).median()
    mx = tv.rolling(20, min_periods=20).max()
    can = (age >= 60) & (close >= 1000) & (med >= 1e9)
    must = (gap >= 10) | (close < 1000) | (mx < 0.5e9)
    st, cur = [], None
    for c_, m_ in zip(can.values, must.values):
        if m_: cur = False
        elif c_: cur = True
        st.append(bool(cur) if cur is not None else False)
    return pd.Series(st, index=d.index)
