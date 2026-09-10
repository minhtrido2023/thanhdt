"""
AMH #4 — Fitness matrix revived, axis-2 = BREADTH TERCILE (PIT), per fleet convention 2026-08-22.

Difference vs the dead fitness_matrix.py (besides it not running on Linux):
  1. axis 2 is breadth tercile PIT, not Value-Radar zone and not state-only;
  2. DT5G state at formation is read PIT (state ON the formation session), NOT the calendar
     month's MODAL state -- the modal state uses sessions AFTER formation, i.e. look-ahead;
  3. DT5G comes from the canonical `tav2_bq.vnindex_5state_dt5g_live`, not the local
     data/dt5g_vnindex.csv that fitness_matrix.py reads (that file disagrees with the live
     table on 52 sessions);
  4. t-stats use Newey-West HAC (lag 2) because the monthly fwd-3M IC series is overlapping
     by construction -- see the AMH#3 finding in the same folder.

Breadth definition -- copied verbatim from macro_state_live._breadth_sql (BREADTH_SOURCE="pit"):
  breadth_t = AVG(Close_t > MA200_t) over {ticker : universe_pit.in_universe on day t}
  session t is classified by breadth_{t-1} (PIT, no same-session look-ahead)
  tercile cut = 1/3 and 2/3 quantile of the ROLLING 252 sessions ENDING at t-1.

PAPER-ONLY diagnostic. Not a return enhancer. Expected dCAGR ~ 0.
Outputs: fitness2_cells.csv, fitness2_marginals.csv, fitness2_out.txt, fitness2.png
"""
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

WC = "/home/trido/thanhdt/WorkingClaude"
OUT = WC + "/mike/agents/Taylor/research/amh_changepoint_fitness_20260910"

FWD = "fwd_3m"
MIN_NAMES = 25
NW_LAG = 2                 # fwd-3M overlap = 3 months -> HAC lag 2
MIN_M_REPORT = 10          # below this a cell is printed as "--" (not reported at all)
MIN_M_CONCLUDE = 18        # below this a cell is REPORTED but flagged KHONG-KET-LUAN
BREADTH_ROLL = 252
QTILE = 0.20
IS_END = "2019-12-31"

STATE_LBL = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EXBULL"}
TERC_LBL = {0: "B-LOW", 1: "B-MID", 2: "B-HIGH"}

SIGNALS = {
    "pb_z": "Val: PB_z", "PB": "Val: PB", "PE": "Val: PE",
    "ROIC5Y": "Qual: ROIC5Y", "FSCORE": "Qual: FSCORE", "ROE_Min5Y": "Qual: ROE_Min5Y",
    "mom_200": "Mom: Close/MA200", "D_RSI": "Mom: D_RSI",
    "D_CMF": "Flow: CMF", "C_L1M": "Pos: Close/Low1M",
}
QUAL_DROP0 = {"ROIC5Y", "ROE_Min5Y"}


def spearman(a, b):
    return pd.Series(a).rank().corr(pd.Series(b).rank())


def nw_tstat(x, lag=NW_LAG):
    """Newey-West HAC t-stat for the mean of a serially correlated series."""
    x = np.asarray(x, float); n = len(x)
    if n < 4:
        return np.nan
    e = x - x.mean()
    g0 = (e @ e) / n
    s = g0
    for L in range(1, min(lag, n - 1) + 1):
        gl = (e[L:] @ e[:-L]) / n
        s += 2.0 * (1.0 - L / (lag + 1.0)) * gl
    if s <= 0:
        return np.nan
    return x.mean() / np.sqrt(s / n)


def load():
    # ---- panel, replicating edge_health_monitor.load_panel() ----
    df = pd.read_csv(WC + "/data/edge_panel.csv", parse_dates=["time"])
    df = df[df[FWD].notna()].copy()
    lo, hi = df[FWD].quantile([0.005, 0.995])
    df[FWD] = df[FWD].clip(lo, hi)
    df["ym"] = df["time"].dt.to_period("M")
    # formation session = the FIRST session of each calendar month present in the panel
    form = df.groupby("ym")["time"].min().rename("form_dt")
    df = df.merge(form, left_on="ym", right_index=True)
    df = df[df["time"] == df["form_dt"]].copy()   # drop the handful of late-entry stragglers

    # ---- DT5G, PIT: the state ON the formation session (canonical live table) ----
    st = pd.read_csv(OUT + "/dt5g_live.csv", parse_dates=["time"]).sort_values("time")
    st_map = st.set_index("time")["state"]
    st_pit = st_map.reindex(sorted(set(st_map.index) | set(form.values))).ffill()

    # ---- breadth PIT + causal rolling tercile ----
    bd = pd.read_csv(OUT + "/breadth_pit.csv", parse_dates=["time"]).sort_values("time")
    bd = bd.set_index("time")
    b_prev = bd["b200"].shift(1)                       # classify day t by breadth_{t-1}
    q1 = b_prev.rolling(BREADTH_ROLL, min_periods=BREADTH_ROLL).quantile(1 / 3)
    q2 = b_prev.rolling(BREADTH_ROLL, min_periods=BREADTH_ROLL).quantile(2 / 3)
    terc = pd.Series(np.where(b_prev.isna() | q1.isna(), np.nan,
                     np.where(b_prev <= q1, 0, np.where(b_prev <= q2, 1, 2))),
                     index=bd.index)

    fdt = pd.DatetimeIndex(sorted(form.values))
    meta = pd.DataFrame({
        "form_dt": fdt,
        "state": st_pit.reindex(fdt).values,
        "b_prev": b_prev.reindex(fdt).values,
        "terc": terc.reindex(fdt).values,
    }).dropna()
    meta["state"] = meta["state"].astype(int)
    meta["terc"] = meta["terc"].astype(int)
    df = df.merge(meta, on="form_dt", how="inner")
    return df, meta


def month_ic_spread(g, col, full_sign):
    s = g[[col, FWD]].dropna()
    if col in QUAL_DROP0:
        s = s[s[col] != 0.0]
    if len(s) < MIN_NAMES or s[col].nunique() < 5:
        return None
    ic = spearman(s[col].values, s[FWD].values)
    n = len(s); k = max(3, int(n * QTILE))
    ss = s.sort_values(col)
    raw = ss[FWD].iloc[-k:].mean() - ss[FWD].iloc[:k].mean()
    return ic, (full_sign * raw if full_sign else raw)


def series_by_month(df, col, full_sign):
    rows = {}
    for dt, g in df.groupby("form_dt"):
        r = month_ic_spread(g, col, full_sign)
        if r is not None:
            rows[dt] = r
    if not rows:
        return pd.DataFrame(columns=["ic", "sp"])
    return pd.DataFrame(rows, index=["ic", "sp"]).T.sort_index()


def cell_stats(sub):
    """sub = DataFrame indexed by formation date with columns ic, sp."""
    n = len(sub)
    if n == 0:
        return None
    ic = sub["ic"].values
    return dict(n_months=n, mean_ic=float(np.mean(ic)),
                t_nw=nw_tstat(ic), t_naive=float(np.mean(ic) / (np.std(ic, ddof=1) / np.sqrt(n)))
                if n > 2 and np.std(ic, ddof=1) > 0 else np.nan,
                hit=float((np.sign(ic) == np.sign(np.mean(ic))).mean()),
                ls_spread_pct=float(np.mean(sub["sp"].values) * 100))


def main():
    df, meta = load()
    print("=" * 96)
    print("AMH #4 — FITNESS MATRIX, axis2 = BREADTH TERCILE PIT (paper-only diagnostic)")
    print("=" * 96)
    print(f"Formation months: {meta.form_dt.min():%Y-%m} -> {meta.form_dt.max():%Y-%m} "
          f"| n={len(meta)} | panel obs={len(df):,} | tickers={df.ticker.nunique()}")
    print("\nMonths per (DT5G state x breadth tercile) — THIS is the honest N, read it first:")
    ct = pd.crosstab(meta["state"].map(STATE_LBL), meta["terc"].map(TERC_LBL))
    ct = ct.reindex(index=[v for v in STATE_LBL.values() if v in ct.index],
                    columns=[v for v in TERC_LBL.values() if v in ct.columns]).fillna(0).astype(int)
    ct["TOTAL"] = ct.sum(axis=1)
    ct.loc["TOTAL"] = ct.sum(axis=0)
    print(ct.to_string())
    print(f"\nReporting floor: n_months >= {MIN_M_REPORT} to print a cell at all; "
          f">= {MIN_M_CONCLUDE} to treat it as conclusion-grade.")
    print(f"Breadth today ({pd.read_csv(OUT + '/breadth_pit.csv').iloc[-1]['time']}): "
          f"{pd.read_csv(OUT + '/breadth_pit.csv').iloc[-1]['b200']:.1%}")

    cells, marg = [], []
    for col, label in SIGNALS.items():
        s_all = series_by_month(df, col, 0)
        if len(s_all) < 24:
            continue
        full_sign = np.sign(s_all["ic"].mean()) or 1
        s_all = series_by_month(df, col, full_sign)
        s_all = s_all.join(meta.set_index("form_dt")[["state", "terc"]], how="inner")

        base = cell_stats(s_all)
        marg.append(dict(signal=col, label=label, axis="FULL", bucket="ALL", **base))

        # marginal: DT5G state
        for st, g in s_all.groupby("state"):
            r = cell_stats(g)
            if r and r["n_months"] >= MIN_M_REPORT:
                marg.append(dict(signal=col, label=label, axis="DT5G",
                                 bucket=STATE_LBL[int(st)], **r))
        # marginal: breadth tercile
        for tc, g in s_all.groupby("terc"):
            r = cell_stats(g)
            if r and r["n_months"] >= MIN_M_REPORT:
                marg.append(dict(signal=col, label=label, axis="BREADTH",
                                 bucket=TERC_LBL[int(tc)], **r))
        # marginal: IS / OOS
        for nm, g in (("IS_2014_19", s_all[s_all.index <= IS_END]),
                      ("OOS_2020p", s_all[s_all.index > IS_END])):
            r = cell_stats(g)
            if r and r["n_months"] >= MIN_M_REPORT:
                marg.append(dict(signal=col, label=label, axis="SPLIT", bucket=nm, **r))

        # 2-way cells
        for (st, tc), g in s_all.groupby(["state", "terc"]):
            r = cell_stats(g)
            if r is None:
                continue
            cells.append(dict(signal=col, label=label, state=STATE_LBL[int(st)],
                              terc=TERC_LBL[int(tc)], grade=("CONCLUDE" if r["n_months"] >= MIN_M_CONCLUDE
                              else ("THIN" if r["n_months"] >= MIN_M_REPORT else "TOO-THIN")), **r))

    C = pd.DataFrame(cells); M = pd.DataFrame(marg)
    C.round(4).to_csv(OUT + "/fitness2_cells.csv", index=False)
    M.round(4).to_csv(OUT + "/fitness2_marginals.csv", index=False)

    def show(sub, idx, colk):
        piv = sub.pivot_table(index=idx, columns=colk, values="mean_ic", aggfunc="first")
        pn = sub.pivot_table(index=idx, columns=colk, values="n_months", aggfunc="first")
        pt = sub.pivot_table(index=idx, columns=colk, values="t_nw", aggfunc="first")
        # t_nw is NaN for tiny cells -> pivot_table drops those rows/cols entirely; realign
        pn = pn.reindex(index=piv.index, columns=piv.columns)
        pt = pt.reindex(index=piv.index, columns=piv.columns)
        o = {}
        for c in piv.columns:
            o[c] = {}
            for r in piv.index:
                v, n, t = piv.loc[r, c], pn.loc[r, c], pt.loc[r, c]
                if pd.isna(v) or pd.isna(n) or n < MIN_M_REPORT:
                    o[c][r] = "     --     "
                else:
                    star = "*" if (pd.notna(t) and abs(t) >= 2) else " "
                    grade = "" if n >= MIN_M_CONCLUDE else "?"
                    o[c][r] = f"{v:+.3f}{star}{grade} n{int(n):<3d}"
        return pd.DataFrame(o).reindex(index=piv.index)

    print("\n" + "=" * 96)
    print("TIER 1 — MARGINALS (thickest N). mean fwd-3M IC · * = |t_NW|>=2 · ? = n<%d" % MIN_M_CONCLUDE)
    print("=" * 96)
    for ax, order in (("DT5G", list(STATE_LBL.values())),
                      ("BREADTH", list(TERC_LBL.values())),
                      ("SPLIT", ["IS_2014_19", "OOS_2020p"])):
        sub = M[M.axis == ax]
        if sub.empty:
            continue
        t = show(sub, "label", "bucket")
        t = t[[c for c in order if c in t.columns]]
        full = M[M.axis == "FULL"].set_index("label")
        t.insert(0, "FULL", [f"{full.loc[r,'mean_ic']:+.3f}"
                             f"{'*' if abs(full.loc[r,'t_nw'])>=2 else ' '} n{int(full.loc[r,'n_months'])}"
                             for r in t.index])
        print(f"\n--- by {ax} ---")
        print(t.to_string())

    print("\n" + "=" * 96)
    print("TIER 2 — 2-WAY CELLS (DT5G x breadth tercile). Read n FIRST. '--' = n<%d, no number shown."
          % MIN_M_REPORT)
    print("=" * 96)
    for col, label in SIGNALS.items():
        sub = C[C.signal == col]
        if sub.empty:
            continue
        t = show(sub, "state", "terc")
        t = t.reindex(index=[s for s in STATE_LBL.values() if s in t.index])
        t = t[[c for c in TERC_LBL.values() if c in t.columns]]
        print(f"\n{label}  (full-sample IC {M[(M.signal==col)&(M.axis=='FULL')].mean_ic.iloc[0]:+.3f})")
        print(t.to_string())

    # ---- the operational question ----
    print("\n" + "=" * 96)
    print("OPERATIONAL ANSWER — is momentum dead everywhere, or only in NEUTRAL/low-breadth?")
    print("=" * 96)
    for col in ("mom_200", "D_RSI"):
        print(f"\n[{col}]")
        sub = C[(C.signal == col)].sort_values("mean_ic")
        print(sub[["state", "terc", "n_months", "mean_ic", "t_nw", "hit",
                   "ls_spread_pct", "grade"]].round(3).to_string(index=False))
    n_conc = (C.grade == "CONCLUDE").sum()
    print(f"\nCells at conclusion grade (n>={MIN_M_CONCLUDE}): {n_conc} / {len(C)} "
          f"({n_conc/len(C):.0%}). The rest are NOT interpretable — do not read the grid as a picture.")

    # ---- heatmap for mom_200 + PE ----
    figs = [c for c in ("mom_200", "PE", "ROE_Min5Y") if c in set(C.signal)]
    fig, axes = plt.subplots(1, len(figs), figsize=(5.2 * len(figs), 4.4))
    axes = np.atleast_1d(axes)
    for ax, col in zip(axes, figs):
        sub = C[C.signal == col]
        piv = sub.pivot_table(index="state", columns="terc", values="mean_ic")
        pn = sub.pivot_table(index="state", columns="terc", values="n_months")
        piv = piv.reindex(index=[s for s in STATE_LBL.values() if s in piv.index],
                          columns=[t for t in TERC_LBL.values() if t in piv.columns])
        pn = pn.reindex_like(piv)
        d = piv.values.astype(float).copy()
        d[np.asarray(pn.values, float) < MIN_M_REPORT] = np.nan   # never draw a cell we won't report
        im = ax.imshow(d, cmap="RdYlGn", vmin=-0.15, vmax=0.15, aspect="auto")
        ax.set_xticks(range(piv.shape[1])); ax.set_xticklabels(piv.columns)
        ax.set_yticks(range(piv.shape[0])); ax.set_yticklabels(piv.index)
        for i in range(piv.shape[0]):
            for j in range(piv.shape[1]):
                if np.isfinite(d[i, j]):
                    ax.text(j, i, f"{d[i,j]:+.2f}\nn={int(pn.values[i,j])}",
                            ha="center", va="center", fontsize=8)
                else:
                    ax.text(j, i, "n too\nsmall", ha="center", va="center",
                            fontsize=7, color="grey")
        ax.set_title(f"{SIGNALS[col]} — fwd-3M IC", fontsize=10)
        fig.colorbar(im, ax=ax, fraction=0.046)
    fig.suptitle("AMH#4 fitness matrix — DT5G state x breadth tercile (PIT). Blank = N too thin.",
                 fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(OUT + "/fitness2.png", dpi=110)
    print("\nSaved fitness2.png, fitness2_cells.csv, fitness2_marginals.csv")


if __name__ == "__main__":
    main()
