"""
Realistic Value Book + Walk-Forward Weight (AMH action, follow-ups #1 & #2)
===========================================================================
(1) CAPACITY: replace the equal-weight microcap-prone proxy with a deployable
    long-only value book — high liquidity floor, liquidity-WEIGHTED (per-name
    cap), realistic TC 0.30%. If value's Sharpe survives this, the edge is real
    (memory warns proxies inflate +3-12pp from illiquid names).
    Part A = liquidity-floor sensitivity (does the edge decay with size?).
(2) WALK-FORWARD the sleeve weight: pick w on trailing data only, apply forward.
    If the WF-chosen blend still beats book-alone OOS, ~25-30% isn't in-sample.

Inputs : data/edge_panel.csv (has liq), data/dt5g_vnindex.csv, prod-spec NAV.
Run    : python value_book_realistic.py
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
NAVF = WORKDIR + r"\data\5sys_prodspec_201401_202605_dt5g.csv"
PANEL = WORKDIR + r"\data\edge_panel.csv"
STATEF = WORKDIR + r"\data\dt5g_vnindex.csv"
FWD = "fwd_1m"
QTILE = 0.20
TC = 0.003           # realistic round-trip incl slippage
NAME_CAP = 0.08      # max weight per name
STATE_W = {1: 0.0, 2: 0.2, 3: 0.7, 4: 1.0, 5: 1.3}


def ann(ret):
    ret = ret.dropna()
    mu = ret.mean()*12; sd = ret.std(ddof=1)*np.sqrt(12)
    sharpe = mu/sd if sd > 0 else 0
    dn = ret[ret < 0].std(ddof=1)*np.sqrt(12); sortino = mu/dn if dn > 0 else 0
    nav = (1+ret).cumprod(); dd = (nav/nav.cummax()-1).min()
    return dict(CAGR=mu*100, Sharpe=sharpe, Sortino=sortino, MaxDD=dd*100,
                Calmar=mu/abs(dd) if dd < 0 else np.nan)


def fmt(m):
    return (f"CAGR {m['CAGR']:5.1f}%  Sharpe {m['Sharpe']:.2f}  Sortino {m['Sortino']:.2f}  "
            f"MaxDD {m['MaxDD']:6.1f}%  Calmar {m['Calmar']:.2f}")


def load_panel():
    df = pd.read_csv(PANEL, parse_dates=["time"])
    df = df[df[FWD].notna()].copy()
    lo, hi = df[FWD].quantile([0.005, 0.995]); df[FWD] = df[FWD].clip(lo, hi)
    df["ym"] = df["time"].dt.to_period("M")
    st = pd.read_csv(STATEF, parse_dates=["time"]); st["ym"] = st["time"].dt.to_period("M")
    df["state"] = df["ym"].map(st.groupby("ym")["state"].agg(lambda s: int(s.mode().iloc[0])))
    return df


def value_book(df, liq_floor, weight="liq"):
    """Gated long-only top-quintile value book. weight in {'eq','liq'}."""
    rets = {}; prev_w = None; navg = []
    for ym, g in df.groupby("ym"):
        s = g[["ticker", "PB", "PE", "liq", FWD, "state"]].dropna(subset=["PB", "PE", FWD, "liq"])
        s = s[s["liq"] >= liq_floor]
        if len(s) < 15:
            continue
        s["vscore"] = s["PB"].rank(pct=True) + s["PE"].rank(pct=True)
        k = max(5, int(len(s)*QTILE))
        picks = s.nsmallest(k, "vscore").copy()
        if weight == "liq":
            w = np.minimum(picks["liq"], picks["liq"].quantile(0.9))
            w = w / w.sum()
            w = np.minimum(w, NAME_CAP); w = w / w.sum()
        else:
            w = pd.Series(1.0/len(picks), index=picks.index)
        wser = pd.Series(w.values, index=picks["ticker"].values)
        raw = float((w.values * picks[FWD].values).sum())
        # turnover vs prev weights
        if prev_w is None:
            turn = 1.0
        else:
            alln = wser.index.union(prev_w.index)
            turn = (wser.reindex(alln, fill_value=0) - prev_w.reindex(alln, fill_value=0)).abs().sum()
        prev_w = wser
        gate = STATE_W.get(int(picks["state"].iloc[0]), 0.7)
        rets[ym] = gate*raw - TC*turn*gate
        navg.append(len(picks))
    return pd.Series(rets).sort_index(), float(np.mean(navg)) if navg else 0


def book_monthly(col):
    nav = pd.read_csv(NAVF, parse_dates=["time"]).set_index("time")[col]
    r = nav.resample("ME").last().pct_change(); r.index = r.index.to_period("M")
    return r.dropna()


def walk_forward(book, value, grid=(0.0, 0.1, 0.2, 0.3, 0.4, 0.5), lookback=36, metric="Calmar"):
    """Each month, pick w maximizing trailing-`lookback` blend `metric`, apply next month."""
    idx = book.index.intersection(value.index)
    b, v = book.loc[idx], value.loc[idx]
    wf = pd.Series(index=idx, dtype=float); chosen = pd.Series(index=idx, dtype=float)
    for t in range(len(idx)):
        if t < lookback:
            w = 0.3
        else:
            past_b = b.iloc[t-lookback:t]; past_v = v.iloc[t-lookback:t]
            best, bw = -1e9, 0.3
            for w_ in grid:
                m = ann((1-w_)*past_b + w_*past_v)
                sc = m[metric]
                if np.isfinite(sc) and sc > best:
                    best, bw = sc, w_
            w = bw
        chosen.iloc[t] = w
        wf.iloc[t] = (1-w)*b.iloc[t] + w*v.iloc[t]
    return wf, chosen


def main():
    df = load_panel()
    print("=== PART A — value-book liquidity-floor sensitivity (is the edge real or microcap?) ===")
    print(f"{'floor':>8} {'weight':>6} {'avg_names':>9}   metrics")
    for floor in [2e9, 1e10, 2e10, 5e10]:
        for wmode in ["eq", "liq"]:
            vb, nn = value_book(df, floor, wmode)
            if len(vb) < 24:
                print(f"{floor/1e9:6.0f}B {wmode:>6} {nn:9.0f}   (too few months)"); continue
            print(f"{floor/1e9:6.0f}B {wmode:>6} {nn:9.0f}   {fmt(ann(vb))}")

    # realistic deployable book: 10B floor, liquidity-weighted
    vb_real, nn = value_book(df, 1e10, "liq")
    print(f"\nRealistic value book (10B floor, liq-weighted, TC {TC*100:.2f}%, "
          f"avg {nn:.0f} names): {fmt(ann(vb_real))}")
    vb_proxy, _ = value_book(df, 2e9, "eq")
    print(f"Proxy (2B floor, equal-weight)                                : {fmt(ann(vb_proxy))}")

    print("\n=== PART B — blend realistic value book onto real V4/V5 (fixed w) ===")
    for col, lbl in [("V4_V121_ENS_TQ34b", "V4"), ("V5_V4_KellyQ2", "V5")]:
        book = book_monthly(col)
        idx = book.index.intersection(vb_real.index)
        print(f"\n  -- {lbl} alone: {fmt(ann(book.loc[idx]))}")
        for w in [0.2, 0.3, 0.4]:
            print(f"     +{int(w*100)}% value(real): {fmt(ann((1-w)*book.loc[idx] + w*vb_real.loc[idx]))}")

    print("\n=== PART C — WALK-FORWARD weight (trailing 36m, pick w by Calmar, apply fwd) ===")
    for col, lbl in [("V4_V121_ENS_TQ34b", "V4"), ("V5_V4_KellyQ2", "V5")]:
        book = book_monthly(col)
        wf, chosen = walk_forward(book, vb_real)
        idx = wf.index
        oos = idx >= pd.Period("2020-01")
        print(f"\n  {lbl}:")
        print(f"    book alone        : {fmt(ann(book.loc[idx]))}")
        print(f"    fixed 30% value   : {fmt(ann(0.7*book.loc[idx] + 0.3*vb_real.loc[idx]))}")
        print(f"    WALK-FWD weight   : {fmt(ann(wf))}")
        print(f"      WF mean w {chosen.mean():.2f} (range {chosen.min():.1f}-{chosen.max():.1f}); "
              f"OOS-only WF: {fmt(ann(wf[oos]))} vs book OOS {fmt(ann(book.loc[idx][oos]))}")

    pd.DataFrame({"value_real": vb_real}).to_csv(WORKDIR + r"\data\value_book_realistic.csv")
    print("\nSaved: data/value_book_realistic.csv")


if __name__ == "__main__":
    main()
