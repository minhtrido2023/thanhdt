# -*- coding: utf-8 -*-
"""
P1 — Breadth compass (la ban thu hai) validation.

Question: does the 2D regime (DT5G index-state x breadth-state) carry information
the 1D index-state misses — specifically, is the "index healthy x breadth weak"
cell toxic for the BOOK (EW ticker_prune proxy) even when the index looks fine?

Inputs (pre-exported):
  data/breadth_prune_daily.csv  — time, n, n_above, breadth, ew_ret (ticker_prune, MA200 non-null)
  data/dt5g_state_series.csv    — time, state (1=CRISIS..5=EX-BULL), state_raw
  VNINDEX.csv                   — time, Close (index level)

Causality: breadth smoothed MA10 (trailing), all signals known at close t,
forward returns measured t -> t+h close-to-close.
"""
import pandas as pd
import numpy as np

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

STATE_NAMES = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}
B_WEAK, B_STRONG = 0.35, 0.55  # breadth bucket edges on smoothed breadth
MIN_NAMES = 100                # min universe size for trustworthy breadth

def load():
    br = pd.read_csv(f"{WORKDIR}/data/breadth_prune_daily.csv", parse_dates=["time"])
    br = br[br["n"] >= MIN_NAMES].copy()
    st = pd.read_csv(f"{WORKDIR}/data/dt5g_state_series.csv", parse_dates=["time"])
    vni = pd.read_csv(f"{WORKDIR}/data/VNINDEX.csv", usecols=["time", "Close"], parse_dates=["time"])
    vni = vni.rename(columns={"Close": "vni"})

    df = st.merge(br[["time", "n", "breadth", "ew_ret"]], on="time", how="inner")
    df = df.merge(vni, on="time", how="left").sort_values("time").reset_index(drop=True)

    # causal smoothing + EW index level
    df["breadth_s"] = df["breadth"].rolling(10, min_periods=5).mean()
    df["ew_idx"] = (1.0 + df["ew_ret"].fillna(0)).cumprod()

    def bucket(b):
        if np.isnan(b): return np.nan
        if b < B_WEAK: return "WEAK"
        if b > B_STRONG: return "STRONG"
        return "MID"
    df["b_state"] = df["breadth_s"].apply(bucket)

    for h in (20, 60):
        df[f"vni_f{h}"] = df["vni"].shift(-h) / df["vni"] - 1
        df[f"ew_f{h}"] = df["ew_idx"].shift(-h) / df["ew_idx"] - 1
    return df

def fmt_pct(x):
    return "   na" if pd.isna(x) else f"{100*x:+5.1f}"

def matrix(df, col, label):
    print(f"\n=== {label} — median fwd, by (DT5G state x breadth bucket) ===")
    print(f"{'state':<9}" + "".join(f"{b:>14}" for b in ["WEAK", "MID", "STRONG"]))
    for s in [1, 2, 3, 4, 5]:
        row = f"{STATE_NAMES[s]:<9}"
        for b in ["WEAK", "MID", "STRONG"]:
            g = df[(df.state == s) & (df.b_state == b)][col].dropna()
            row += f"{fmt_pct(g.median()):>8} n={len(g):<4}" if len(g) else f"{'—':>8}      "
        print(row)

def winrate(df, col, label):
    print(f"\n=== {label} — win% (fwd>0), by cell ===")
    print(f"{'state':<9}" + "".join(f"{b:>10}" for b in ["WEAK", "MID", "STRONG"]))
    for s in [1, 2, 3, 4, 5]:
        row = f"{STATE_NAMES[s]:<9}"
        for b in ["WEAK", "MID", "STRONG"]:
            g = df[(df.state == s) & (df.b_state == b)][col].dropna()
            row += f"{100*(g>0).mean():>9.0f}%" if len(g) else f"{'—':>10}"
        print(row)

def episodes(df):
    """Contiguous runs of divergence: state>=3 (NEUTRAL+) while breadth WEAK."""
    d = df.copy()
    d["div"] = (d.state >= 3) & (d.b_state == "WEAK")
    d["grp"] = (d["div"] != d["div"].shift()).cumsum()
    out = []
    for _, g in d[d["div"]].groupby("grp"):
        if len(g) < 10:  # ignore blips < 2 weeks
            continue
        i0, i1 = g.index[0], g.index[-1]
        ew_dur = d.loc[i1, "ew_idx"] / d.loc[i0, "ew_idx"] - 1
        vni_dur = d.loc[i1, "vni"] / d.loc[i0, "vni"] - 1
        f60_ew = d.loc[i1, "ew_f60"]; f60_vni = d.loc[i1, "vni_f60"]
        out.append((g.time.iloc[0].date(), g.time.iloc[-1].date(), len(g),
                    vni_dur, ew_dur, f60_vni, f60_ew))
    print("\n=== Divergence episodes: DT5G in NEUTRAL/BULL/EX-BULL while breadth WEAK (>=10 sessions) ===")
    print(f"{'start':<12}{'end':<12}{'len':>4} | {'VNI dur':>8} {'EW dur':>8} | {'VNI f60':>8} {'EW f60':>8}")
    for s0, s1, n, vd, ed, fv, fe in out:
        print(f"{str(s0):<12}{str(s1):<12}{n:>4} | {fmt_pct(vd):>8} {fmt_pct(ed):>8} | {fmt_pct(fv):>8} {fmt_pct(fe):>8}")
    return out

def main():
    df = load()
    print(f"Sample: {df.time.min().date()} -> {df.time.max().date()}, {len(df)} sessions "
          f"(universe >= {MIN_NAMES} names)")
    print(f"Breadth (smoothed) now: {df.breadth_s.iloc[-1]:.1%}  bucket={df.b_state.iloc[-1]}  "
          f"DT5G state={STATE_NAMES[df.state.iloc[-1]]}")

    # occupancy
    occ = df.groupby(["state", "b_state"]).size().unstack(fill_value=0)
    occ.index = [STATE_NAMES[s] for s in occ.index]
    print("\n=== Cell occupancy (sessions) ===")
    print(occ.reindex(columns=["WEAK", "MID", "STRONG"]).to_string())

    matrix(df, "ew_f60", "EW ticker_prune basket (BOOK proxy), fwd 60d")
    matrix(df, "vni_f60", "VNINDEX, fwd 60d")
    matrix(df, "ew_f20", "EW basket, fwd 20d")
    winrate(df, "ew_f60", "EW basket fwd 60d")

    # headline contrast: same DT5G state, breadth WEAK vs STRONG
    print("\n=== Headline: EW fwd60 spread (STRONG - WEAK breadth) within same index state ===")
    for s in [3, 4, 5]:
        w = df[(df.state == s) & (df.b_state == "WEAK")]["ew_f60"].dropna()
        st_ = df[(df.state == s) & (df.b_state == "STRONG")]["ew_f60"].dropna()
        if len(w) > 20 and len(st_) > 20:
            print(f"  {STATE_NAMES[s]:<8}: WEAK {fmt_pct(w.median())}% (n={len(w)})  "
                  f"STRONG {fmt_pct(st_.median())}% (n={len(st_)})  "
                  f"spread {fmt_pct(st_.median()-w.median())}pp")

    episodes(df)

    # the 2025-08+ window specifically
    w = df[df.time >= "2025-08-01"]
    print(f"\n=== Since 2025-08-01 ===")
    print(f"VNINDEX: {fmt_pct(w.vni.iloc[-1]/w.vni.iloc[0]-1)}%   "
          f"EW basket: {fmt_pct(w.ew_idx.iloc[-1]/w.ew_idx.iloc[0]-1)}%")
    print("breadth bucket occupancy:", w.b_state.value_counts().to_dict())
    print("DT5G state occupancy:", {STATE_NAMES[k]: v for k, v in w.state.value_counts().items()})
    div_days = ((w.state >= 3) & (w.b_state == "WEAK")).sum()
    print(f"divergence days (state>=NEUTRAL & breadth WEAK): {div_days}/{len(w)}")

    df.to_csv(f"{WORKDIR}/data/breadth_compass_panel.csv", index=False)
    print(f"\npanel saved -> data/breadth_compass_panel.csv")

if __name__ == "__main__":
    main()
