#!/usr/bin/env python3
"""Test whether foreign-flow (netVal/netVol, level + N-day accumulation) leads future
VNINDEX returns. Mirrors the VN30F-basis IC method (Spearman, full-history + current
episode). Honest NO-GO if IC~0 or inconsistent.
"""
import duckdb
import numpy as np
import pandas as pd
from scipy import stats

TA = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor"
BQ = "/home/trido/thanhdt/WorkingClaude/data/bq_cache/ticker"


def load_vnindex():
    con = duckdb.connect()
    frames = []
    for y in range(2018, 2027):
        q = f"select time, Close from read_parquet('{BQ}/{y}.parquet') where ticker='VNINDEX'"
        frames.append(con.execute(q).df())
    px = pd.concat(frames, ignore_index=True)
    px["time"] = pd.to_datetime(px["time"])
    px = px.sort_values("time").drop_duplicates("time").reset_index(drop=True)
    return px


def prep(flow_csv, px):
    f = pd.read_csv(flow_csv)
    f["tradingDate"] = pd.to_datetime(f["tradingDate"])
    f = f.rename(columns={"tradingDate": "time"})[["time", "netVal", "netVol", "buyVal", "sellVal"]]
    df = px.merge(f, on="time", how="inner").sort_values("time").reset_index(drop=True)
    # forward log returns
    for h in (5, 10, 20):
        df[f"fwd{h}"] = np.log(df["Close"].shift(-h) / df["Close"])
    # signals: level (raw netVal) + N-day cumulative accumulation
    df["nv"] = df["netVal"]
    for n in (5, 10, 20):
        df[f"cum{n}"] = df["netVal"].rolling(n).sum()
    # rolling z-score of daily netVal (20d) — scale-stationary version
    m = df["netVal"].rolling(20).mean()
    s = df["netVal"].rolling(20).std()
    df["nv_z20"] = (df["netVal"] - m) / s
    return df


def ic_table(df, sig_cols, label):
    print(f"\n=== IC (Spearman)  {label}  n_base={len(df)} ===")
    print(f"{'signal':<10} {'fwd5':>16} {'fwd10':>16} {'fwd20':>16}")
    rows = []
    for sig in sig_cols:
        line = f"{sig:<10}"
        rowd = {"signal": sig}
        for h in (5, 10, 20):
            sub = df[[sig, f"fwd{h}"]].dropna()
            if len(sub) < 50:
                line += f" {'n/a':>16}"
                continue
            rho, p = stats.spearmanr(sub[sig], sub[f"fwd{h}"])
            line += f" {rho:+.3f}(p{p:.2f})".rjust(16)
            rowd[f"fwd{h}_ic"] = rho
            rowd[f"fwd{h}_p"] = p
            rowd[f"fwd{h}_n"] = len(sub)
        print(line)
        rows.append(rowd)
    return pd.DataFrame(rows)


def episode(df, peak_date, label, pre=25, post=10):
    peak = pd.Timestamp(peak_date)
    win = df[(df["time"] >= peak - pd.Timedelta(days=pre*2)) & (df["time"] <= peak + pd.Timedelta(days=post*2))].copy()
    win = win.tail(pre + post + 5)
    print(f"\n=== EPISODE around {label} (peak/pivot {peak_date}) ===")
    print(f"{'date':<12}{'Close':>9}{'netVal_bn':>11}{'cum5_bn':>10}{'cum10_bn':>11}")
    for _, r in win.iterrows():
        mark = "  <-- pivot" if r["time"] == peak else ""
        nv = r["netVal"]/1e9 if pd.notna(r["netVal"]) else float('nan')
        c5 = r["cum5"]/1e9 if pd.notna(r["cum5"]) else float('nan')
        c10 = r["cum10"]/1e9 if pd.notna(r["cum10"]) else float('nan')
        print(f"{str(r['time'].date()):<12}{r['Close']:>9.1f}{nv:>11.0f}{c5:>10.0f}{c10:>11.0f}{mark}")


if __name__ == "__main__":
    px = load_vnindex()
    print(f"VNINDEX px: {len(px)} rows {px.time.min().date()} -> {px.time.max().date()}")

    idx = prep(f"{TA}/foreign_flow_vnindex.csv", px)
    sig_cols = ["nv", "cum5", "cum10", "cum20", "nv_z20"]
    ic_idx = ic_table(idx, sig_cols, "INDEX foreign flow (full 2018-2026)")

    # coincident check: correlation of netVal with SAME-day return (sign of coincidence)
    idx["ret0"] = np.log(idx["Close"] / idx["Close"].shift(1))
    coin = idx[["nv", "ret0"]].dropna()
    rho_c, p_c = stats.spearmanr(coin["nv"], coin["ret0"])
    # lead: netVal_t vs ret_{t-1} (does flow lag price?)
    idx["ret_prev"] = idx["ret0"].shift(1)
    lag = idx[["nv", "ret_prev"]].dropna()
    rho_l, p_l = stats.spearmanr(lag["nv"], lag["ret_prev"])
    print(f"\n[coincidence] Spearman(netVal_t, ret_t)      = {rho_c:+.3f} (p={p_c:.3g})")
    print(f"[reactivity ] Spearman(netVal_t, ret_{{t-1}})   = {rho_l:+.3f} (p={p_l:.3g})  (>0 => flow chases prior move)")

    # deriv (historical only)
    dv = prep(f"{TA}/foreign_flow_vn30f.csv", px)
    ic_dv = ic_table(dv, sig_cols, "VN30F front-month foreign flow (2018-2025-12, STALE for 2026)")

    # episodes on INDEX (fresh)
    episode(idx, "2026-05-18", "CURRENT selloff peak (VNI top)")
    episode(idx, "2026-07-17", "CURRENT accel-down pivot")
    # benign reference: a local high that did NOT lead to a big drawdown
    episode(idx, "2026-01-15", "benign-ish reference (early 2026)")

    # sub-period IC stability (index): split 2018-2021 vs 2022-2026
    for lo, hi, tag in [("2018-01-01", "2021-12-31", "IS 2018-2021"),
                        ("2022-01-01", "2026-12-31", "OOS 2022-2026")]:
        sub = idx[(idx["time"] >= lo) & (idx["time"] <= hi)]
        ic_table(sub, ["nv", "cum10", "nv_z20"], f"INDEX {tag}")
