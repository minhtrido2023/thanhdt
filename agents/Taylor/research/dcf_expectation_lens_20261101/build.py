# -*- coding: utf-8 -*-
"""build.py — panel quý (tăng trưởng nhiều cửa sổ, PIT) + panel tháng (PE/PCF/EVEB, PE tự thân, mom, fwd, SUE).
Job Taylor_20261101_165940. Tái dùng data/ và engine của ../dcf_vn_calibration_20261101. PREREG §0-§1."""
import os
import sys
import numpy as np
import pandas as pd
import duckdb

WC = "/home/trido/thanhdt/WorkingClaude"
HERE = os.path.dirname(os.path.abspath(__file__))
PRIOR = os.path.join(HERE, "..", "dcf_vn_calibration_20261101")
DATA = os.path.join(HERE, "data")
sys.path.insert(0, PRIOR)
from common import month_close, add_fwd  # noqa: E402


def sg(a, b):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    d = np.abs(a) + np.abs(b)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(d > 0, 2 * (a - b) / d, np.nan)


def simple_g(a, b):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(b > 0, a / b - 1, np.nan)


def qord(q):
    return q.str[:4].astype(int) * 4 + q.str[-1].astype(int) - 1


def build_quarterly():
    c = duckdb.connect()
    cols = ",".join(["ticker", "time", "quarter"] + [f"NP_P{i}" for i in range(8)] + [f"Revenue_P{i}" for i in range(8)]
                    + ["NPM_P0", "ROE_Trailing", "NP_R"])
    f = c.execute(f"SELECT {cols} FROM read_parquet('{WC}/data/bq_cache/ticker_financial.parquet')").df()
    f["time"] = pd.to_datetime(f["time"])
    f = f[f.quarter.notna() & f.quarter.str.match(r"^\d{4}Q[1-4]$")].copy()
    f = f.sort_values(["ticker", "time"])
    n0 = len(f)
    # cùng (ticker, time) ⇒ giữ dòng cuối (khớp engine); cùng (ticker, quarter) nhiều time ⇒ giữ bản ĐẦU (khả dụng sớm nhất)
    f = f.drop_duplicates(["ticker", "time"], keep="last")
    dq = f.duplicated(["ticker", "quarter"], keep="first")
    print(f"fin rows {n0}, sau dedupe time {len(f)}, dòng quý trùng (giữ bản đầu) {int(dq.sum())}")
    f = f[~dq].copy()
    f["qo"] = qord(f.quarter)
    f["TTM0"] = f[[f"NP_P{i}" for i in range(4)]].sum(axis=1, min_count=4)
    f["TTM1"] = f[[f"NP_P{i}" for i in range(4, 8)]].sum(axis=1, min_count=4)
    f["RTTM0"] = f[[f"Revenue_P{i}" for i in range(4)]].sum(axis=1, min_count=4)
    f["RTTM1"] = f[[f"Revenue_P{i}" for i in range(4, 8)]].sum(axis=1, min_count=4)
    key = f.set_index(["ticker", "qo"])
    out = f.copy()

    def lag(col, k):  # giá trị col của dòng quý qo-k (đã công bố trước, nếu time ≤ time hiện tại)
        s = out.set_index(["ticker", "qo"])[[col, "time"]].copy()
        s.index = pd.MultiIndex.from_arrays([s.index.get_level_values(0), s.index.get_level_values(1) + k])
        m = out[["ticker", "qo", "time"]].merge(s.rename(columns={col: "v", "time": "tl"}).reset_index()
                                                .rename(columns={"level_0": "ticker", "level_1": "qo"}),
                                                on=["ticker", "qo"], how="left")
        v = m["v"].values.copy()
        if k > 0:
            v[(m.tl > m.time).values] = np.nan
        return v

    out["TTM2"] = lag("TTM1", 4)
    out["TTM3"] = lag("TTM1", 8)
    out["TTM5"] = lag("TTM1", 16)
    out["RTTM2"] = lag("RTTM1", 4)
    out["gQ2"] = sg(out.NP_P0 + out.NP_P1, out.NP_P4 + out.NP_P5)
    out["g1"] = sg(out.TTM0, out.TTM1)
    out["g2"] = sg(out.TTM0, out.TTM2) / 2
    out["g3"] = sg(out.TTM0, out.TTM3) / 3
    out["g5"] = sg(out.TTM0, out.TTM5) / 5
    out["rg1"] = sg(out.RTTM0, out.RTTM1)
    out["rg2"] = sg(out.RTTM0, out.RTTM2) / 2
    out["g1s"] = simple_g(out.TTM0, out.TTM1)
    out["gQ2s"] = simple_g(out.NP_P0 + out.NP_P1, out.NP_P4 + out.NP_P5)
    g1 = None
    out["g1_l4"] = lag("g1", 4)
    out["acc"] = out.g1 - out.g1_l4
    out["accS"] = out.gQ2 - out.g1
    # LAG SUE (pt_v23_audit_2014.py ~1059)
    exp = out[["NP_P1", "NP_P2", "NP_P3", "NP_P4"]].mean(axis=1)
    out["sue"] = ((out.NP_P0 - exp) / np.maximum(np.abs(exp), 1e9)).clip(-5, 5)
    # tương lai (CHỈ biến kết quả): TTM của dòng q+4, q+8 — không kiểm time (là kết quả)
    out["TTMf1"] = lag("TTM0", -4)
    out["TTMf2"] = lag("TTM0", -8)
    out["f1"] = sg(out.TTMf1, out.TTM0)
    out["f2"] = sg(out.TTMf2, out.TTM0) / 2
    for k in (1, 2, 3, 4):  # cho dấu hiệu "đỉnh" Q3
        out[f"npm_l{k}"] = lag("NPM_P0", k)
        out[f"roe_l{k}"] = lag("ROE_Trailing", k)
        out[f"g1s_l{k}"] = lag("g1s", k)
    del g1
    out.to_parquet(os.path.join(DATA, "qpanel.parquet"))
    print("qpanel", out.shape)
    return out


def build_monthly(q):
    pan = pd.read_parquet(os.path.join(PRIOR, "data", "panel_monthly.parquet"))
    pan = pan[~pan.is_fin.astype(bool)].copy()
    c = duckdb.connect()
    px = pd.read_parquet(os.path.join(PRIOR, "data", "px_daily.parquet"), columns=["time", "ticker"])
    vn = px[px.ticker == "VNINDEX"].time
    me = pd.DatetimeIndex(vn.groupby(vn.dt.to_period("M")).max().values)
    me_s = ",".join(f"DATE '{d.date()}'" for d in me[me >= "2013-01-01"])
    v = c.execute(f"SELECT time,ticker,PE,PCF,EVEB,Trading_Value FROM read_parquet('{WC}/data/bq_cache/ticker/*.parquet') "
                  f"WHERE time IN ({me_s})").df()
    v["time"] = pd.to_datetime(v["time"])
    old = pd.read_csv(os.path.join(DATA, "pe_2008_2012.csv.gz"), parse_dates=["time"])
    old = old[old.time < v.time.min()][["time", "ticker", "PE", "PCF", "EVEB", "Trading_Value"]]
    v = pd.concat([old, v], ignore_index=True)
    v["t"] = v.time.dt.to_period("M")
    v = v.sort_values("time").drop_duplicates(["ticker", "t"], keep="last")
    # PE tự thân: percentile trong 60 tháng TRƯỚC (min 24), chỉ PE>0; tương tự PCF
    v = v.sort_values(["ticker", "time"])
    for col in ("PE", "PCF"):
        x = v[col].where(v[col] > 0)

        def own(s):
            arr = s.values
            res = np.full(len(arr), np.nan)
            for i in range(len(arr)):
                if not np.isfinite(arr[i]):
                    continue
                h = arr[max(0, i - 60):i]
                h = h[np.isfinite(h)]
                if len(h) >= 24:
                    res[i] = (np.sum(h < arr[i]) + 0.5 * np.sum(h == arr[i])) / len(h) * 100
            return pd.Series(res, index=s.index)
        v[f"{col}_own"] = x.groupby(v.ticker, group_keys=False).apply(own)
    v["tv3"] = v.groupby("ticker").Trading_Value.transform(lambda s: s.rolling(3, min_periods=1).mean())
    pan["tp"] = pan.t.dt.to_period("M")
    pan = pan.merge(v[["ticker", "t", "PE", "PCF", "EVEB", "tv3", "PE_own", "PCF_own"]].rename(columns={"t": "tp"}),
                    on=["ticker", "tp"], how="left")
    qq = q.drop(columns=["quarter"]).rename(columns={"time": "qtime"}).sort_values("qtime")
    pan = pd.merge_asof(pan.sort_values("t"), qq, left_on="t", right_on="qtime", by="ticker", direction="backward",
                        suffixes=("", "_q"))
    mc, me2 = month_close()
    pan = add_fwd(pan, mc, me2)
    piv = mc.pivot(index="t", columns="ticker", values="Close").reindex(me2)
    mom = (piv.shift(1) / piv.shift(12) - 1).stack().rename("mom").reset_index()
    pan = pan.merge(mom, on=["t", "ticker"], how="left")
    pan.to_parquet(os.path.join(DATA, "mpanel.parquet"))
    print("mpanel", pan.shape, "PE cover", pan.PE.notna().mean().round(3), "PE_own cover", pan.PE_own.notna().mean().round(3),
          "g1 cover", pan.g1.notna().mean().round(3), "g5 cover", pan.g5.notna().mean().round(3))


if __name__ == "__main__":
    q = build_quarterly()
    build_monthly(q)
