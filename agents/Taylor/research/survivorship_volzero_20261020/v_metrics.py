"""Δ CAGR/Sharpe/MaxDD biến thể engine vs pin (METRIC trong CSV engine) + IS/OOS CAGR từ DAILY combined_nav."""
import sys, glob, re, json, pandas as pd, numpy as np
PIN = {"p30_pin0": "raw/pin_4707bcbe.csv", "p30_pin1M": "raw/pin_bcd0469f.csv", "p0_pin0": "raw/pin_537e349b.csv", "p0_pin1M": "raw/pin_a6ba34d8.csv"}
def load(p):
    df = pd.read_csv(p, low_memory=False)
    m = df[df.record_type == "METRIC"].set_index("key").value.astype(float)
    d = df[df.record_type == "DAILY"].copy(); d["ymd"] = pd.to_datetime(d.ymd); s = d.set_index("ymd").combined_nav.astype(float)
    def cg(x):
        return (x.iloc[-1] / x.iloc[0]) ** (365.25 / (x.index[-1] - x.index[0]).days) - 1
    return dict(cagr=m.cagr, sharpe=m.sharpe_252, maxdd=m.max_dd, is_cagr=cg(s[:"2019-12-31"]), oos_cagr=cg(s["2019-12-31":]),
                selfcheck=max(m.cash_flow_identity_max_err_vnd_BAL, m.cash_flow_identity_max_err_vnd_LAG,
                              m.final_nav_identity_err_vnd_BAL, m.final_nav_identity_err_vnd_LAG)), df
rows = []
base = {k: load(v)[0] for k, v in PIN.items()}
for var in sys.argv[1:]:
    for leg in PIN:
        log = f"logs/vz_{var}_{leg}.log"
        csv = re.findall(r"/home/trido/thanhdt/WorkingClaude/data/v23_golive\S*\.csv", open(log).read())[-1]
        r, _ = load(csv); b = base[leg]
        rows.append(dict(var=var, leg=leg, cagr=r["cagr"] * 100, d_cagr_pp=(r["cagr"] - b["cagr"]) * 100,
                         d_sharpe=r["sharpe"] - b["sharpe"], d_maxdd_pp=(r["maxdd"] - b["maxdd"]) * 100,
                         d_is_pp=(r["is_cagr"] - b["is_cagr"]) * 100, d_oos_pp=(r["oos_cagr"] - b["oos_cagr"]) * 100,
                         selfcheck_maxerr_vnd=r["selfcheck"], csv=csv.split("/")[-1]))
out = pd.DataFrame(rows); print(out.drop(columns="csv").round(3).to_string(index=False))
out.to_csv(f"out_metrics_{'_'.join(sys.argv[1:])}.csv", index=False)
