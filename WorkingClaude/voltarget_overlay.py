"""
Vol-Target Sizing Layer (AMH proposal #2)
=========================================
AMH: survival > optimization; volatility is time-varying (vol clustering); in
crises vol explodes and correlations -> 1. DT5G moves exposure on STATE (slow by
design: asym commit enC=25). A vol-target layer scales exposure *continuously* by
recent realized vol -- a fast, independent survival valve that contracts BEFORE
DT5G changes state. (This is the valve flagged as mandatory for futures.)

    w_final = w_state * clip(vol_target / realized_vol, 0, cap)

v1 test: VNINDEX 5-state allocation sim (Kelly money-metric, same as the DT-optimal
studies). Compares:
  BASE        = DT5G state-weight only (benchmark)
  VT_valve    = state-weight x min(1, vt/rv)         (cap=1.0, only de-risks)
  VT_2side    = state-weight x clip(vt/rv, 0, 1.5)   (also scales up when calm)
across a vol_target grid, with faithful T+1 / 3-session ramp / TC mechanics.

Input : data/dt5g_vnindex.csv  (time, state, vnindex)
Output: console table + data/voltarget_results.csv + voltarget_overlay.png

Run: python voltarget_overlay.py
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
DATA = WORKDIR + r"\data\dt5g_vnindex.csv"
STATE_W = {1: 0.0, 2: 0.2, 3: 0.7, 4: 1.0, 5: 1.3}   # CRISIS/BEAR/NEUTRAL/BULL/EXBULL (BQ codes 1-5)
TC = 0.001            # 0.1% on traded portion
VOL_WIN = 20          # realized-vol lookback (trading days)
ANN = 252
IS_END = "2019-12-31"


def load():
    df = pd.read_csv(DATA, parse_dates=["time"]).sort_values("time").reset_index(drop=True)
    df["ret"] = df["vnindex"].pct_change()
    df["w_state"] = df["state"].map(STATE_W)
    # causal realized vol (annualized), known at close of t -> used to size t+1
    df["rv"] = df["ret"].rolling(VOL_WIN).std() * np.sqrt(ANN)
    df["rv_ewma"] = df["ret"].ewm(span=VOL_WIN).std() * np.sqrt(ANN)
    return df


def simulate(ret, w_target, tc=TC):
    """Single-path NAV with T+1 exec, 3-session ramp, TC on |dw|. Returns nav series."""
    n = len(ret)
    nav = np.ones(n)
    w_cur = 0.0
    w_prev_t = w_target.copy()
    nav_val = 1.0
    out = np.empty(n); out[:] = np.nan
    for t in range(1, n):
        # target known from info at t-1 (already causal in w_target construction)
        wt = w_target[t-1]
        if np.isnan(wt):
            out[t] = nav_val
            continue
        gap = wt - w_cur
        w_new = wt if abs(gap) < 0.03 else w_cur + gap / 3.0
        r = ret[t]
        if np.isnan(r):
            r = 0.0
        cost = tc * abs(w_new - w_cur)
        nav_val *= (1 + w_new * r - cost)
        w_cur = w_new
        out[t] = nav_val
    return pd.Series(out)


def metrics(nav, dates):
    nav = nav.dropna()
    d = dates.loc[nav.index]
    years = (d.iloc[-1] - d.iloc[0]).days / 365.25
    cagr = nav.iloc[-1] ** (1 / years) - 1
    r = nav.pct_change().dropna()
    vol = r.std() * np.sqrt(ANN)
    sharpe = (r.mean() * ANN) / vol if vol > 0 else 0
    downside = r[r < 0].std() * np.sqrt(ANN)
    sortino = (r.mean() * ANN) / downside if downside > 0 else 0
    roll_max = nav.cummax()
    dd = (nav / roll_max - 1).min()
    calmar = cagr / abs(dd) if dd < 0 else np.nan
    return dict(CAGR=cagr, Vol=vol, Sharpe=sharpe, Sortino=sortino,
                MaxDD=dd, Calmar=calmar, FinalNAV=nav.iloc[-1])


def target_series(df, kind, vt=None, cap=1.0, vol_col="rv"):
    ws = df["w_state"].values.astype(float)
    if kind == "BASE":
        return ws
    rv = df[vol_col].values
    with np.errstate(divide="ignore", invalid="ignore"):
        mult = np.clip(vt / rv, 0, cap)
    mult = np.where(np.isnan(rv), 1.0, mult)
    return ws * mult


def fmt(m):
    return (f"CAGR {m['CAGR']*100:5.2f}%  Vol {m['Vol']*100:4.1f}%  "
            f"Sharpe {m['Sharpe']:.2f}  Sortino {m['Sortino']:.2f}  "
            f"MaxDD {m['MaxDD']*100:6.2f}%  Calmar {m['Calmar']:.2f}  NAV {m['FinalNAV']:.2f}x")


def run_block(df, label_filter=None):
    dates = df["time"]
    ret = df["ret"].values
    rows = []
    navs = {}

    def add(name, wt):
        nav = simulate(ret, wt)
        full = metrics(nav, dates)
        is_mask = df["time"] <= IS_END
        m_is = metrics(simulate(ret[is_mask.values], wt[is_mask.values]), dates[is_mask].reset_index(drop=True))
        oos = df["time"] > IS_END
        m_oos = metrics(simulate(ret[oos.values], wt[oos.values]), dates[oos].reset_index(drop=True))
        rows.append(dict(arm=name, **{f"{k}": v for k, v in full.items()},
                         CAGR_IS=m_is["CAGR"], CAGR_OOS=m_oos["CAGR"],
                         Calmar_OOS=m_oos["Calmar"]))
        navs[name] = nav
        return full

    # benchmark
    m = add("BASE (DT5G)", target_series(df, "BASE"))
    print(f"  BASE (DT5G)            {fmt(m)}")
    # B&H reference
    m = add("VNINDEX B&H", np.ones(len(df)))
    print(f"  VNINDEX B&H            {fmt(m)}")

    print("  --- vol-target valve (cap=1.0, de-risk only) ---")
    for vt in [0.12, 0.15, 0.18, 0.20, 0.22]:
        wt = target_series(df, "VT", vt=vt, cap=1.0)
        m = add(f"VT_valve vt={vt:.2f}", wt)
        print(f"  VT_valve vt={vt:.2f}        {fmt(m)}")

    print("  --- vol-target two-sided (cap=1.5) ---")
    for vt in [0.15, 0.18, 0.20, 0.22]:
        wt = target_series(df, "VT", vt=vt, cap=1.5)
        m = add(f"VT_2side vt={vt:.2f}", wt)
        print(f"  VT_2side vt={vt:.2f}        {fmt(m)}")

    print("  --- EWMA vol valve (cap=1.0) ---")
    for vt in [0.15, 0.18]:
        wt = target_series(df, "VT", vt=vt, cap=1.0, vol_col="rv_ewma")
        m = add(f"VT_valve_ewma vt={vt:.2f}", wt)
        print(f"  VT_valve_ewma vt={vt:.2f}   {fmt(m)}")

    # === LEVERAGE test (futures path): vol-target is NON-redundant only with leverage ===
    print("  --- LEVERED DT5G (L=2x, futures-like) — does vol-target rescue DD? ---")
    ws = df["w_state"].values.astype(float)
    rv = df["rv"].values
    L = 2.0
    base_lev = np.clip(L * ws, 0, L * 1.3)
    m = add("BASE_L2 (lev only)", base_lev)
    print(f"  BASE_L2 (lev only)     {fmt(m)}")
    for vt in [0.15, 0.18]:
        with np.errstate(divide="ignore", invalid="ignore"):
            valve = np.clip(vt / rv, 0, 1.0)
        valve = np.where(np.isnan(rv), 1.0, valve)
        wt = base_lev * valve
        m = add(f"BASE_L2+VTvalve vt={vt:.2f}", wt)
        print(f"  BASE_L2+VTvalve {vt:.2f}    {fmt(m)}")

    return pd.DataFrame(rows), navs


def main():
    df = load()
    print(f"Data: {df['time'].min().date()} -> {df['time'].max().date()} | {len(df)} sessions")
    print(f"VNINDEX realized vol (20d ann): median {df['rv'].median()*100:.1f}%  "
          f"p10 {df['rv'].quantile(.1)*100:.1f}%  p90 {df['rv'].quantile(.9)*100:.1f}%")
    print(f"State dwell: " + ", ".join(f"{k}:{(df['state']==k).mean()*100:.0f}%" for k in range(5)))
    print()
    res, navs = run_block(df)
    res.to_csv(WORKDIR + r"\data\voltarget_results.csv", index=False)

    # plot a few representative NAV paths + a DD comparison
    pick = ["BASE (DT5G)", "VNINDEX B&H", "VT_valve vt=0.15", "VT_2side vt=0.18"]
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 9), sharex=True)
    for name in pick:
        nav = navs[name]
        ax1.plot(df["time"], nav, lw=1.3, label=name)
        dd = nav / nav.cummax() - 1
        ax2.plot(df["time"], dd, lw=1.0, label=name)
    ax1.set_yscale("log"); ax1.set_title("Vol-Target Sizing Layer — NAV (log)"); ax1.legend(fontsize=8); ax1.grid(alpha=0.3)
    ax2.set_title("Drawdown"); ax2.legend(fontsize=8); ax2.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(WORKDIR + r"\voltarget_overlay.png", dpi=110)
    print("\nSaved: voltarget_overlay.png | data/voltarget_results.csv")


if __name__ == "__main__":
    main()
