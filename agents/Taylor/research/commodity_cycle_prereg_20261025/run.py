"""Commodity early-cycle test — implements PREREG.md (commit 103df32e4). Read-only research."""
import json
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
WC = Path("/home/trido/thanhdt/WorkingClaude")
CMO = WC / "data/_wb_cache/CMO-Historical-Data-Monthly.xlsx"
SERIES = {"rubber": "Rubber, RSS3", "crude oil": "Crude oil, average", "urea": "Urea ",
          "DAP": "DAP", "sugar": "Sugar, world"}
H_MAIN, TH_MAIN = 126, 1.10
HORIZONS = {"3M": 63, "6M": 126, "12M": 252}
THRESH = [1.05, 1.10, 1.20]
WIN_START, WIN_END = pd.Timestamp("2014-01-01"), pd.Timestamp("2026-03-31")
rng = np.random.default_rng(20261025)

cmap = pd.read_csv(HERE / "commodity_map.csv")
prim = cmap[cmap.in_primary == "Y"]
fam_tickers = prim.groupby("commodity").ticker.apply(list).to_dict()
all_mapped = set(cmap.ticker)

# --- commodity prices
raw = pd.read_excel(CMO, "Monthly Prices", header=4)
raw = raw.iloc[1:].rename(columns={raw.columns[0]: "m"})
raw["month"] = pd.PeriodIndex(raw.m.str.replace("M", "-"), freq="M")
px = {f: pd.to_numeric(raw.set_index("month")[c], errors="coerce").dropna() for f, c in SERIES.items()}

# --- stock prices + universe
con = duckdb.connect()
P = con.sql(f"""select time, ticker, Close, ICB_Code from read_parquet('{WC}/data/bq_cache/ticker/*.parquet')
               where time >= '2013-06-01' and Close > 0""").df()
P["time"] = pd.to_datetime(P.time)
close = P.pivot_table(index="time", columns="ticker", values="Close").sort_index().ffill()
icb = P.dropna(subset=["ICB_Code"]).groupby("ticker").ICB_Code.last().astype(int).astype(str).str.zfill(4)
U = con.sql(f"""select time, ticker from read_parquet('{WC}/data/bq_cache/universe_pit/*.parquet')
               where in_universe""").df()
U["time"] = pd.to_datetime(U.time)
umembers = U.groupby("time").ticker.apply(set)
days = close.index


def entry_day(month):  # first session strictly after the 10th of month+1
    d = (month + 1).to_timestamp() + pd.Timedelta(days=10)  # = day 11
    i = days.searchsorted(d, side="left")
    return days[i] if i < len(days) else None


def fwd(t, tickers, h):
    i = days.get_loc(t)
    j = min(i + h, len(days) - 1)
    sub = close.loc[:, [x for x in tickers if x in close.columns]]
    r = sub.iloc[j] / sub.iloc[i] - 1
    return r.dropna()


def supersector(fam):
    codes = {icb.get(t, "")[:2] for t in fam_tickers[fam]} - {""}
    return codes


def measure(fam, t, h):
    uni = umembers.get(t, set())
    exp = [x for x in fam_tickers[fam] if x in uni]
    if not exp:
        return None
    ss = supersector(fam)
    ctrl = [x for x in uni if x not in all_mapped and icb.get(x, "")[:2] in ss]
    fb = len(ctrl) < 5
    if fb:
        ctrl = [x for x in uni if x not in all_mapped]
    re, rc = fwd(t, exp, h), fwd(t, ctrl, h)
    if re.empty or rc.empty:
        return None
    return dict(n_exp=len(re), n_ctrl=len(rc), r_exp=re.mean(), r_ctrl=rc.mean(),
                X=re.mean() - rc.mean(), fallback=fb, exp=",".join(sorted(re.index)))


def events(fam, th):
    s = px[fam]
    R = s / s.rolling(12).mean()
    out, last = [], None
    for m in R.index[13:]:
        if R[m] >= th and R[m - 1] < th and (last is None or (m - last).n > 12):
            last = m
            t = entry_day(m)
            if t is not None and WIN_START <= t <= WIN_END:
                out.append((m, t, R[m]))
            elif t is not None and t < WIN_START:
                pass
    return out


def run(th, h):
    rows = []
    for fam in SERIES:
        for m, t, r in events(fam, th):
            res = measure(fam, t, h)
            if res:
                rows.append(dict(family=fam, sig_month=str(m), entry=t.date(), R=round(r, 3), **res))
    ev = pd.DataFrame(rows).sort_values("entry").reset_index(drop=True)
    # clusters: entries < 126 sessions apart chain together
    pos = [days.get_loc(pd.Timestamp(e)) for e in ev.entry]
    cl, c = [], 0
    for k, p in enumerate(pos):
        if k and p - pos[k - 1] >= 126:
            c += 1
        cl.append(c)
    ev["cluster"] = cl
    return ev


def stats(ev):
    cm = ev.groupby("cluster").X.mean()
    n = len(cm)
    boots = [cm.sample(n, replace=True, random_state=int(rng.integers(1e9))).mean() for _ in range(10000)]
    from scipy.stats import binomtest
    pos = int((cm > 0).sum())
    first_entry = ev.groupby("cluster").entry.min()
    is_ = cm[pd.to_datetime(first_entry) < "2020-01-01"]
    oos = cm[pd.to_datetime(first_entry) >= "2020-01-01"]
    loco = [cm.drop(k).mean() for k in cm.index]
    lofo = {f: ev[ev.family != f].groupby("cluster").X.mean().mean() for f in ev.family.unique()}
    return dict(n_events=len(ev), n_clusters=n, mean_cl=cm.mean(), median_cl=cm.median(), sd_cl=cm.std(),
                ci90=(float(np.percentile(boots, 5)), float(np.percentile(boots, 95))),
                pos_cl=pos, sign_p=binomtest(pos, n, 0.5, alternative="greater").pvalue,
                IS_mean=is_.mean(), IS_n=len(is_), OOS_mean=oos.mean(), OOS_n=len(oos),
                loco_min=min(loco), lofo=lofo, mde=2.5 * cm.std() / np.sqrt(n),
                mean_event=ev.X.mean(), hit_event=(ev.X > 0).mean())


def baseline(h):
    out = {}
    for fam in SERIES:
        xs = []
        for m in pd.period_range("2013-12", "2026-02", freq="M"):
            t = entry_day(m)
            if t is None or not (WIN_START <= t <= WIN_END):
                continue
            r = measure(fam, t, h)
            if r:
                xs.append(r["X"])
        out[fam] = (float(np.mean(xs)), len(xs))
    return out


if __name__ == "__main__":
    main = run(TH_MAIN, H_MAIN)
    main.to_csv(HERE / "events_main.csv", index=False)
    s = stats(main)
    base = baseline(H_MAIN)
    # baseline weighted by the event family mix
    base_mix = float(np.mean([base[f][0] for f in main.family]))
    grid = []
    for th in THRESH:
        for hn, h in HORIZONS.items():
            ev = run(th, h)
            g = stats(ev)
            grid.append(dict(th=th, h=hn, n_ev=g["n_events"], n_cl=g["n_clusters"],
                             mean_cl=g["mean_cl"], median_cl=g["median_cl"], ci90_lo=g["ci90"][0],
                             pos_cl=g["pos_cl"], IS=g["IS_mean"], OOS=g["OOS_mean"]))
    grid = pd.DataFrame(grid)
    grid.to_csv(HERE / "grid.csv", index=False)
    crit = {
        "1_mean>=5pp_and_median>0": bool(s["mean_cl"] >= 0.05 and s["median_cl"] > 0),
        "2_ci90_lo>0": bool(s["ci90"][0] > 0),
        "3_pos>=2/3_and_sign_p<0.10": bool(s["pos_cl"] >= 2 / 3 * s["n_clusters"] and s["sign_p"] < 0.10),
        "4_IS>0_and_OOS>0": bool(s["IS_mean"] > 0 and s["OOS_mean"] > 0),
        "5_loco_min>0_and_lofo_min>0": bool(s["loco_min"] > 0 and min(s["lofo"].values()) > 0),
        "6_event_minus_baseline>=3pp": bool(main.X.mean() - base_mix >= 0.03),
    }
    out = dict(main=s, baseline=base, baseline_mix=base_mix, criteria=crit, PASS=all(crit.values()))
    json.dump(out, open(HERE / "summary.json", "w"), indent=1, default=str)
    pd.set_option("display.width", 250)
    print(main.drop(columns=["exp"]).to_string())
    print(json.dumps(out, indent=1, default=str))
    print(grid.round(4).to_string())
    sys.exit(0)
