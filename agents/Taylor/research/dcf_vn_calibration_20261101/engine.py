# -*- coding: utf-8 -*-
"""engine.py — panel DCF dạng vector, tái lập dcf_valuation.fair_value (domestic_v2, OShares quý).
Job Taylor_20261101_155145. R&D: chỉ đọc. Build: python engine.py build  ⇒ data/panel_monthly.parquet
Selfcheck:  python engine.py selfcheck  ⇒ so 400 cặp ngẫu nhiên với dcf_valuation.fair_value (0 VND)."""
import os
import sys
os.environ["DCF_RATE_FRAME"] = "domestic_v2"          # ghim khung đang production (selfcheck so với nó)
import numpy as np
import pandas as pd
import duckdb

WC = "/home/trido/thanhdt/WorkingClaude"
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
sys.path.insert(0, WC)
import dcf_valuation as D  # noqa: E402
D.pin_oshares_source_fin("dcf_vn_calibration")
os.chdir(HERE)

R_CONST = (D.RF_DOMESTIC + D.ERP_DOMESTIC) / 100.0


def load_fin():
    c = duckdb.connect()
    cols = ("ticker,time,quarter,Release_Date,OShares,NP_P0,NP_P1,NP_P2,NP_P3,CF_OA_P0,CF_OA_P1,CF_OA_P2,"
            "CF_OA_P3,CF_Invest_P0,CF_Invest_P1,CF_Invest_P2,CF_Invest_P3,CF_OA_3Y,CF_Invest_3Y,ROE5Y,ROE3Y,"
            "Debt_Eq_P0,EPS_P0,Dividend_1Y,Dividend_3Y,BVPS")
    df = c.execute(f"SELECT {cols} FROM read_parquet('{WC}/data/bq_cache/ticker_financial.parquet')").df()
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values(["ticker", "time"]).reset_index(drop=True)
    return df


def row_inputs(fin):
    """Mỗi dòng tài chính (đã sắp ticker,time) ⇒ input DCF NẾU dòng đó là dòng mới nhất ≤ asof.
    Tái dùng đúng D._annual_series / D.recency_weighted_growth trên tập dòng ≤ dòng đó (cùng `time ≤ a`).
    Chú ý: fair_value lọc `time <= a` ⇒ các dòng TRÙNG time cùng được tính; ta giữ y nguyên bằng cách
    dùng tập dòng có time ≤ time của dòng (nhóm dòng trùng time ⇒ dòng cuối của nhóm là 'last')."""
    out = []
    for tk, g in fin.groupby("ticker", sort=False):
        g = g.reset_index(drop=True)
        times = g.time.values
        for i in range(len(g)):
            # chỉ dòng cuối trong nhóm cùng time mới là `rows.iloc[-1]` của fair_value
            if i + 1 < len(g) and times[i + 1] == times[i]:
                continue
            sub = g.iloc[: i + 1]
            last = sub.iloc[-1]
            rec = {"ticker": tk, "time": last.time, "quarter": last.quarter, "n_rows": len(sub),
                   "OShares": last.OShares, "CF_OA_3Y": last.CF_OA_3Y, "CF_Invest_3Y": last.CF_Invest_3Y,
                   "ROE5Y": last.ROE5Y, "ROE3Y": last.ROE3Y, "Debt_Eq_P0": last.Debt_Eq_P0}
            rec["ttm_np"] = float(np.nansum([last.NP_P0, last.NP_P1, last.NP_P2, last.NP_P3]))
            rec["ttm_fcfe"] = float(np.nansum([last.CF_OA_P0, last.CF_OA_P1, last.CF_OA_P2, last.CF_OA_P3,
                                               last.CF_Invest_P0, last.CF_Invest_P1, last.CF_Invest_P2,
                                               last.CF_Invest_P3]))
            ann = D._annual_series(sub, ["NP_P0", "NP_P1", "NP_P2", "NP_P3"])
            g_raw, gp = D.recency_weighted_growth(ann, D.DEFAULT_WEIGHTS)
            rec["g_raw"] = g_raw
            rec["g1"] = gp[0] if len(gp) > 0 else np.nan
            rec["g2"] = gp[1] if len(gp) > 1 else np.nan
            rec["g3"] = gp[2] if len(gp) > 2 else np.nan
            rec["n_ann"] = len(ann)
            out.append(rec)
    return pd.DataFrame(out)


def load_prices(start_year=2008):
    c = duckdb.connect()
    px = c.execute(f"SELECT time,ticker,Close,Price,Volume,ICB_Code FROM read_parquet('{WC}/data/bq_cache/ticker/*.parquet')").df()
    px["time"] = pd.to_datetime(px["time"])
    old = pd.read_csv(os.path.join(DATA, "px_2008_2012.csv.gz"), parse_dates=["time"])
    old = old[old.time < px.time.min()]
    old = old[old.time.dt.year >= start_year]
    px = pd.concat([old, px], ignore_index=True).sort_values(["ticker", "time"]).reset_index(drop=True)
    return px


def load_universe():
    c = duckdb.connect()
    u = c.execute(f"SELECT time,ticker FROM read_parquet('{WC}/data/bq_cache/universe_pit/*.parquet') WHERE in_universe").df()
    u["time"] = pd.to_datetime(u["time"])
    return u


def month_ends(px):
    vn = px[px.ticker == "VNINDEX"].time
    me = vn.groupby(vn.dt.to_period("M")).max()
    return pd.DatetimeIndex(me.values)


def gT_of(t):
    return D.terminal_growth_mode(t, "cap_rf")


def fv_path(base, growth_path, g_T, r, oshares):
    """growth_path: array (n, N) tăng trưởng từng năm giai đoạn tường minh. Vector."""
    base = np.asarray(base, float)
    n, N = growth_path.shape
    f = base.copy()
    pv = np.zeros(n)
    r = np.broadcast_to(np.asarray(r, float), (n,))
    g_T = np.broadcast_to(np.asarray(g_T, float), (n,))
    for y in range(N):
        f = f * (1 + growth_path[:, y])
        pv += f / (1 + r) ** (y + 1)
    tv = f * (1 + g_T) / (r - g_T)
    return (pv + tv / (1 + r) ** N) / np.asarray(oshares, float)


def build():
    fin = load_fin()
    ri = row_inputs(fin)
    ri.to_parquet(os.path.join(DATA, "row_inputs.parquet"))
    px = load_prices()
    px.to_parquet(os.path.join(DATA, "px_daily.parquet"))
    me = month_ends(px)
    me = me[me >= "2013-12-01"]
    u = load_universe()
    rows = []
    udates = np.sort(u.time.unique())
    ug = {d: g.ticker.unique() for d, g in u.groupby("time")}
    for t in me:
        # universe: phiên gần nhất ≤ t có dữ liệu universe_pit
        k = np.searchsorted(udates, np.datetime64(t), side="right") - 1
        if k < 0:
            continue
        rows.append(pd.DataFrame({"t": t, "ticker": ug[udates[k]]}))
    pan = pd.concat(rows, ignore_index=True)
    # dòng tài chính mới nhất ≤ t (PIT)
    pan = pan.sort_values("t")
    ri2 = ri.sort_values("time")
    pan = pd.merge_asof(pan, ri2, left_on="t", right_on="time", by="ticker", direction="backward")
    # giá Price thô + Close phiên gần nhất ≤ t trong 5 phiên (khớp PRICE_MATCH_SESSIONS)
    pxs = px[["ticker", "time", "Close", "Price", "ICB_Code"]].sort_values("time").rename(columns={"time": "pxt"})
    pan = pd.merge_asof(pan.sort_values("t"), pxs, left_on="t", right_on="pxt", by="ticker", direction="backward")
    pan = pan[(pan.t - pan.pxt).dt.days <= 10]
    # tài chính PIT (route 8L) — dùng chính D.is_financial
    routes = D._load_routes().sort_values("time")
    pan = pd.merge_asof(pan.sort_values("t"), routes.rename(columns={"time": "rt"}), left_on="t", right_on="rt",
                        by="ticker", direction="backward")
    icb = D._load_icb_map()
    pan["is_fin"] = np.where(pan.route.notna(), pan.route.isin(D.FIN_ROUTES),
                             pan.ticker.map(lambda x: D.is_financial_icb(icb.get(x, np.nan))))
    gt = {t: gT_of(t) for t in pan.t.unique()}
    pan["g_T"] = pan.t.map(gt)
    pan["age_days"] = (pan.t - pan.time).dt.days
    pan.to_parquet(os.path.join(DATA, "panel_monthly.parquet"))
    print("panel rows", len(pan), "dates", pan.t.nunique())


def base_valid(p):
    """Điều kiện fair_value ok=True (trước OShares)."""
    m = (p.n_rows >= 4) & (~p.is_fin) & (p.CF_OA_3Y > 0)
    base = (p.CF_OA_3Y + p.CF_Invest_3Y.fillna(0)) / 3.0
    m &= base > 0
    m &= p.OShares > 0
    return m, base


def current_fv(p, N=5, shrink=D.GROWTH_SHRINK, r=None, g_T=None):
    m, base = base_valid(p)
    gT = p.g_T.values if g_T is None else np.broadcast_to(g_T, (len(p),))
    graw = np.where(np.isnan(p.g_raw.values), gT, p.g_raw.values)
    gcl = np.clip(graw, D.G_EXPLICIT_FLOOR, D.G_EXPLICIT_CAP)
    gexp = gT + shrink * (gcl - gT)
    rr = R_CONST if r is None else r
    path = np.repeat(gexp[:, None], N, axis=1)
    fv = fv_path(base.values, path, gT, rr, p.OShares.values)
    return np.where(m, fv, np.nan), gexp


def selfcheck(n=400, seed=20261101):
    p = pd.read_parquet(os.path.join(DATA, "panel_monthly.parquet"))
    fv, _ = current_fv(p)
    p["fv"] = fv
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(p), n, replace=False)
    bad = 0
    nok = 0
    fin = D._load_financials()
    for i in idx:
        row = p.iloc[i]
        res = D.fair_value(row.ticker, row.t, price=row.Price, fin=fin)
        mine = row.fv
        if res["ok"]:
            nok += 1
            if not (np.isfinite(mine) and abs(res["fair_value_ps"] - mine) <= 1e-6 * abs(mine)):
                bad += 1
                print("MISMATCH", row.ticker, row.t.date(), res["fair_value_ps"], mine)
        else:
            if np.isfinite(mine):
                bad += 1
                print("MISMATCH-ok", row.ticker, row.t.date(), res["reason"], mine)
    print(f"selfcheck: {n} cap, {nok} ok, mismatch={bad}")
    return bad


if __name__ == "__main__":
    if sys.argv[1] == "build":
        build()
    elif sys.argv[1] == "selfcheck":
        sys.exit(1 if selfcheck() else 0)
