"""B2 — đánh giá sleeve theo PREREG_BT §5-6. Đọc out_bt_daily_*.csv + raw/r3_pin0.csv, raw/r3_pin1m.csv (ledger pin,
md5 4707bcbe… / bcd0469f…). EXPLORATORY. Chạy: OMP_NUM_THREADS=1 $DNA_PYEXE evaluate_bt.py > out_eval_stdout.txt"""
import os

import numpy as np
import pandas as pd
from scipy.stats import norm, skew, kurtosis

os.chdir(os.path.dirname(os.path.abspath(__file__)))
SEED, NB, W = 20261020, 2000, 0.05
IS_END, OOS_START = pd.Timestamp("2019-12-31"), pd.Timestamp("2020-01-01")


def nav(tag):
    d = pd.read_csv(f"out_bt_daily_{tag}.csv", parse_dates=["date"]).set_index("date").nav
    return d


def metr(r, dates):
    r = pd.Series(r, index=dates).dropna()
    v = (1 + r).cumprod()
    yrs = (r.index[-1] - r.index[0]).days / 365.25
    return dict(CAGR=v.iloc[-1] ** (1 / yrs) - 1, Sharpe=r.mean() / r.std() * np.sqrt(252),
                MaxDD=(v / v.cummax() - 1).min(), ann_mean=r.mean() * 252, N_days=len(r))


def qblocks(idx):
    q = pd.PeriodIndex(idx, freq="Q")
    lab, gi = np.unique(q.astype(str), return_inverse=True)
    return [np.where(gi == k)[0] for k in range(len(lab))]


def boot(fn, arrays, idx):
    """bootstrap khối quý: fn(*arrays_resampled) → số. Trả (lo, hi, p hai phía quanh 0)."""
    B = qblocks(idx)
    rng = np.random.default_rng(SEED)
    out = []
    for _ in range(NB):
        ii = np.concatenate([B[k] for k in rng.integers(0, len(B), len(B))])
        out.append(fn(*[a[ii] for a in arrays]))
    out = np.array(out)
    return np.percentile(out, 2.5), np.percentile(out, 97.5), max(2 * min((out <= 0).mean(), (out >= 0).mean()), 1 / NB)


def sh(r):
    return r.mean() / r.std() * np.sqrt(252)


def dsr(r, srs):
    """Deflated Sharpe (Bailey & López de Prado 2014), SR theo ngày; srs = SR ngày của N_trials biến thể."""
    N, g = len(srs), 0.5772156649
    sr0 = np.sqrt(np.var(srs, ddof=1)) * ((1 - g) * norm.ppf(1 - 1 / N) + g * norm.ppf(1 - 1 / (N * np.e)))
    s = r.mean() / r.std()
    T = len(r)
    z = (s - sr0) * np.sqrt(T - 1) / np.sqrt(1 - skew(r) * s + (kurtosis(r, fisher=False) - 1) / 4 * s ** 2)
    return norm.cdf(z), sr0, s


def r3(path):
    d = pd.read_csv(path, low_memory=False)
    d = d[d.record_type == "DAILY"].copy()
    d["date"] = pd.to_datetime(d.ymd)
    d = d.set_index("date")
    return d.combined_nav.astype(float), d.nav_lag_ref.astype(float)


rows, verdict = [], {}
for idle, led in (("pin0", "raw/r3_pin0.csv"), ("pin1M", "raw/r3_pin1m.csv")):
    print(f"\n================ {idle} ({'SÀN' if idle == 'pin0' else 'TRẦN'}) ================")
    S = {v: nav(f"{v}_{idle}_2p5B") for v in ("V1_H40", "V2_H20", "V3_H40_adv5")}
    rS = {v: s.pct_change().dropna() for v, s in S.items()}
    # sleeve một mình
    for v, r in rS.items():
        for nm, m in (("FULL", r.index >= r.index[0]), ("IS", r.index <= IS_END), ("OOS", r.index >= OOS_START)):
            x = r[m]
            mt = metr(x.values, x.index)
            lo, hi, p = boot(lambda a: a.mean() * 252, [x.values], x.index)
            rows.append(dict(idle=idle, leg=f"sleeve {v}", period=nm, **mt, ann_mean_ci_lo=lo, ann_mean_ci_hi=hi, p_ann_mean=p))
    srs = np.array([r.mean() / r.std() for r in rS.values()])
    d_, sr0, s1 = dsr(rS["V1_H40"].values, srs)
    print(f"DSR V1 (N_trials=3): {d_:.4f} | SR ngày {s1:.4f} vs SR0 {sr0:.4f} | SR ngày 3 biến thể {np.round(srs, 4)}")
    # R3 + LAG
    nR3, nLAG = r3(led)
    rR3, rLAG = nR3.pct_change(), nLAG.pct_change()
    df = pd.concat([rS["V1_H40"].rename("S"), rR3.rename("R3"), rLAG.rename("LAG")], axis=1, join="inner").dropna()
    df = df[df.index >= pd.Timestamp("2014-07-02")]
    print(f"chồng lấn {df.index[0].date()}→{df.index[-1].date()} N={len(df)}")
    mo = (1 + df).resample("ME").prod() - 1
    cor = dict(daily_S_LAG=df.S.corr(df.LAG), daily_S_R3=df.S.corr(df.R3),
               monthly_S_LAG=mo.S.corr(mo.LAG), monthly_S_R3=mo.S.corr(mo.R3), daily_LAG_R3=df.LAG.corr(df.R3))
    print("tương quan:", {k: round(v, 3) for k, v in cor.items()})
    df["MIX"] = (1 - W) * df.R3 + W * df.S
    res = {}
    for nm, m in (("FULL", df.index >= df.index[0]), ("IS", df.index <= IS_END), ("OOS", df.index >= OOS_START)):
        x = df[m]
        a, b = metr(x.R3.values, x.index), metr(x.MIX.values, x.index)
        lo, hi, p = boot(lambda r3_, s_: sh((1 - W) * r3_ + W * s_) - sh(r3_), [x.R3.values, x.S.values], x.index)
        res[nm] = dict(dSharpe=b["Sharpe"] - a["Sharpe"], lo=lo, hi=hi, p=p)
        rows.append(dict(idle=idle, leg="R3", period=nm, **a))
        rows.append(dict(idle=idle, leg=f"R3+{W:.0%} sleeve V1", period=nm, **b, dSharpe=b["Sharpe"] - a["Sharpe"],
                         dSharpe_ci_lo=lo, dSharpe_ci_hi=hi, p_dSharpe=p, dCAGR=b["CAGR"] - a["CAGR"],
                         dMaxDD=b["MaxDD"] - a["MaxDD"]))
        print(f"{nm}: R3 CAGR {a['CAGR']:.4f} Sh {a['Sharpe']:.3f} DD {a['MaxDD']:.4f} | MIX CAGR {b['CAGR']:.4f} "
              f"Sh {b['Sharpe']:.3f} DD {b['MaxDD']:.4f} | ΔSh {b['Sharpe'] - a['Sharpe']:+.4f} CI[{lo:+.4f},{hi:+.4f}] p {p:.3f}")
    verdict[idle] = dict(res=res, dsr=d_, cor=cor)

T = pd.DataFrame(rows)
T.to_csv("out_eval_metrics.csv", index=False)
pd.set_option("display.width", 250)
print("\n", T[["idle", "leg", "period", "CAGR", "Sharpe", "MaxDD", "ann_mean_ci_lo", "ann_mean_ci_hi", "p_ann_mean"]]
      .query("leg.str.startswith('sleeve')", engine="python").round(4).to_string(index=False))

# nhãn PREREG_BT §6
v0, v1 = verdict["pin0"], verdict["pin1M"]
if v0["res"]["FULL"]["dSharpe"] <= 0 or v1["res"]["FULL"]["dSharpe"] <= 0:
    lab = "không có"
elif all(v["res"]["FULL"]["lo"] > 0 and v["res"]["IS"]["dSharpe"] > 0 and v["res"]["OOS"]["dSharpe"] > 0
         and v["dsr"] >= 0.95 for v in (v0, v1)):
    lab = "có đóng góp tăng thêm sau phí"
else:
    lab = "không phân biệt được (thiếu N)"
print(f"\nNHÃN (PREREG_BT §6, V1): {lab}")
for k, v in verdict.items():
    print(k, {p: {a: round(b, 4) for a, b in r.items()} for p, r in v["res"].items()}, "DSR", round(v["dsr"], 4))
