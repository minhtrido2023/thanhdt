"""Metric các chân engine (PREREG Q4). Tính lại từ CSV (DAILY combined_nav), không đọc số engine tự in.
Usage: python legs_metrics.py"""
import glob, hashlib, json, os
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
W = "/home/trido/thanhdt/WorkingClaude"
LEGS = ["ctrl_p0", "cap3_p0", "cap4_p0", "cap5_p0", "ctrl_1m", "cap3_1m", "cap4_1m", "cap5_1m"]
EXPECT = {"ctrl_p0": "4707bcbeb7e801d49a4a851ffd91d5e7", "ctrl_1m": "bcd0469f42c2f76937a6ebb10aae9b40"}
BASE = {"MEGA", "MOMENTUM", "DEEP_VALUE_RECOVERY", "RE_BACKLOG_BUY"}


def met(nav):
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    r = nav.pct_change().dropna()
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1 / yrs) - 1
    sh = r.mean() / r.std() * np.sqrt(len(r) / yrs)
    dd = float((nav / nav.cummax() - 1).min())
    return dict(cagr=cagr, sharpe=sh, maxdd=dd, calmar=cagr / -dd)


res = {}
for tag in LEGS:
    f = glob.glob(f"{W}/data/v23_golive_audit_*_exp_{tag}_*.csv")
    if len(f) != 1:
        res[tag] = {"error": f"found {len(f)} csv"}; continue
    raw = open(f[0], "rb").read()
    d = pd.read_csv(f[0], low_memory=False)
    D = d[d.record_type == "DAILY"].copy(); D["ymd"] = pd.to_datetime(D.ymd); D = D.set_index("ymd").sort_index()
    nav = D.combined_nav.astype(float)
    M = d[d.record_type == "METRIC"]
    mk = dict(zip(M["key"].astype(str), M["value"])) if len(M) else {}
    o = dict(csv=os.path.basename(f[0]), md5=hashlib.md5(raw).hexdigest(), full=met(nav),
             IS=met(nav[:"2019-12-31"]), OOS=met(nav["2019-12-31":]))
    o["control_byte_identical"] = (o["md5"] == EXPECT[tag]) if tag in EXPECT else None
    o["selfcheck"] = {k: v for k, v in mk.items() if "identity" in k}
    w21 = np.array([nav.iloc[i + 21] / nav.iloc[i] - 1 for i in range(0, len(nav) - 21, 21)])
    roll = (nav.shift(-21) / nav - 1).dropna()
    o["win21"] = dict(n=len(w21), p01=float(np.quantile(w21, .01)), p05=float(np.quantile(w21, .05)),
                      min=float(w21.min()), rolling_min=float(roll.min()))
    # realized BAL trade weight % combined NAV (own path)
    s = D.cap_bal / D.combined_nav
    T = d[(d.record_type == "TX") & (d.book == "BAL")].copy(); T["ymd"] = pd.to_datetime(T.ymd)
    T = T[T.play_type.str.replace("_W$", "", regex=True).isin(BASE)]
    g = T.groupby("holding_id"); e = g.ymd.min(); b = g.buy_amount.sum()
    wn = pd.Series([b[h] / D.nav_bal_ref[e[h]] * s[e[h]] for h in b.index])
    o["bal_trades"] = dict(n=int(len(wn)), median_w=float(wn.median()), p90_w=float(wn.quantile(.9)), max_w=float(wn.max()))
    if tag.startswith("cap"):
        wcap = int(tag[3]) / 100
        o["bal_trades"]["n_over_cap_plus_0p5pp"] = int((wn > wcap + 0.005).sum())
    res[tag] = o

for conv in ("p0", "1m"):
    c = res.get(f"ctrl_{conv}", {})
    if "full" not in c: continue
    for w in (3, 4, 5):
        t = res.get(f"cap{w}_{conv}", {})
        if "full" not in t: continue
        t["delta_vs_ctrl_pp"] = {
            "cagr": (t["full"]["cagr"] - c["full"]["cagr"]) * 100,
            "maxdd": (t["full"]["maxdd"] - c["full"]["maxdd"]) * 100,
            "sharpe": t["full"]["sharpe"] - c["full"]["sharpe"],
            "calmar": t["full"]["calmar"] - c["full"]["calmar"],
            "IS_cagr": (t["IS"]["cagr"] - c["IS"]["cagr"]) * 100, "OOS_cagr": (t["OOS"]["cagr"] - c["OOS"]["cagr"]) * 100,
            "IS_maxdd": (t["IS"]["maxdd"] - c["IS"]["maxdd"]) * 100, "OOS_maxdd": (t["OOS"]["maxdd"] - c["OOS"]["maxdd"]) * 100,
            "win21_p01": (t["win21"]["p01"] - c["win21"]["p01"]) * 100,
            "win21_rolling_min": (t["win21"]["rolling_min"] - c["win21"]["rolling_min"]) * 100}
json.dump(res, open(f"{HERE}/legs_metrics.json", "w"), indent=1, default=str)
for k, v in res.items():
    if "full" not in v: print(k, v); continue
    f_ = v["full"]
    print(f"{k:8s} md5 {v['md5'][:8]} ctrl_ok={v['control_byte_identical']} CAGR {f_['cagr']*100:6.2f} Sh {f_['sharpe']:.2f} "
          f"DD {f_['maxdd']*100:6.2f} Cal {f_['calmar']:.2f} | IS {v['IS']['cagr']*100:5.2f}/{v['IS']['maxdd']*100:6.2f} "
          f"OOS {v['OOS']['cagr']*100:5.2f}/{v['OOS']['maxdd']*100:6.2f} | w21 p01 {v['win21']['p01']*100:5.2f} "
          f"roll-min {v['win21']['rolling_min']*100:6.2f} | BALw med {v['bal_trades']['median_w']*100:.2f} max {v['bal_trades']['max_w']*100:.2f}"
          + (f" over {v['bal_trades'].get('n_over_cap_plus_0p5pp')}" if 'n_over_cap_plus_0p5pp' in v['bal_trades'] else ""))
    if "delta_vs_ctrl_pp" in v: print("          Δ", {a: round(b, 3) for a, b in v["delta_vs_ctrl_pp"].items()})
