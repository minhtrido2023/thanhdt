"""Kiểm định §3 (universe replica) + §4 (chỉ báo, BCTC) trên 5 mã còn sống. PREREG md5 21165fd1."""
import sys, json, numpy as np, pandas as pd
from svr_lib import load_px, indicators, ta_px, universe, rsi
D = "data"; LIVE = ["HPG", "VNM", "HQC", "ITA", "DLG"]
vni = pd.read_csv(f"{D}/bq_vni.csv", parse_dates=["time"]).set_index("time")
cal = vni.index; infl = vni.Inflation_7
vmax = vni.D_RSI.rolling(60, min_periods=1).max()
bq = pd.read_csv(f"{D}/bq_live.csv", parse_dates=["time"])
up = pd.read_csv(f"{D}/bq_upit_live.csv", parse_dates=["time"])
res = {"universe": {}, "ind": {}}
W0, W1 = pd.Timestamp("2014-01-02"), pd.Timestamp("2026-06-19")
kind = sys.argv[1] if len(sys.argv) > 1 else "wilder"
allta = []
for tk in LIVE:
    px = load_px(tk)
    u = universe(px, cal, infl)
    ub = up[up.ticker == tk].set_index("time").in_universe.astype(str).str.lower().eq("true")
    days = cal[(cal >= W0) & (cal <= W1)]
    a = u.reindex(days).fillna(False); b = ub.reindex(days).fillna(False)
    res["universe"][tk] = dict(agree=float((a == b).mean()), n=len(days), rep_in=int(a.sum()), bq_in=int(b.sum()))
    o = indicators(px, px.index, kind)
    g = bq[bq.ticker == tk].set_index("time")
    j = o.join(g, rsuffix="_bq", how="inner"); j = j[(j.index >= W0) & (j.index <= W1)]
    r = {}
    for c in ["Close", "D_RSI", "MA20", "MA50", "MA200", "Volume_3M_P50", "HI_3M_T1", "ID_HI_3Y", "D_RSI_Max1W"]:
        x, y = j[c], j[c + "_bq"]; m = x.notna() & y.notna()
        r[c] = float(np.median(np.abs(x[m] - y[m]) / np.abs(y[m]).clip(lower=1e-9)))
    r["MACD_sign_agree"] = float((np.sign(j.D_MACDdiff) == np.sign(j.D_MACDdiff_bq)).mean())
    r["RSI>0.5_agree"] = float(((j.D_RSI > .5) == (j.D_RSI_bq > .5)).mean())
    bqo = pd.DataFrame({c: j[c + "_bq"] for c in ["Close", "MA20", "MA50", "MA200", "MA50_T1", "Close_T1", "D_RSI",
                        "D_MACDdiff", "HI_3M_T1", "ID_HI_3Y", "D_RSI_Max1W", "Volume_3M_P50", "Volume"]})
    t1 = ta_px(j[bqo.columns], vmax); t2 = ta_px(bqo, vmax)
    r["ta_exact"] = float((t1 == t2).mean()); r["ta_absdiff_med"] = float((t1 - t2).abs().median())
    r["IDHI3Y<=5_agree"] = float(((j.ID_HI_3Y <= 5) == (j.ID_HI_3Y_bq <= 5)).mean())
    r["HI3M<0.85_agree"] = float(((j.Close / j.HI_3M_T1 < .85) == (j.Close_bq / j.HI_3M_T1_bq < .85)).mean())
    r["ta>=44_agree"] = float(((t1 >= 44) == (t2 >= 44)).mean()); r["n"] = len(j)
    res["ind"][tk] = r; allta.append((t1 == t2).values)
res["ta_exact_pooled"] = float(np.concatenate(allta).mean()); res["rsi_kind"] = kind
print(json.dumps(res, indent=1))
